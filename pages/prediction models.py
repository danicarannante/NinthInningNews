import streamlit as st
from pybaseball import team_batting, team_pitching, schedule_and_record,pitching_stats,statcast_pitcher
import pandas as pd
from variables import team_mapping
from pybaseball import cache
import plotly
import plotly.express as px
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LassoCV
from sklearn.preprocessing import StandardScaler

cache.enable()
year = st.sidebar.slider('Select Year', min_value=2000, max_value=2024, value=2023)

# -------------------------  Info Section ------------------------------------
info = f"""
<div style='background-color: LightBlue; margin-bottom:5px;border-radius: 5px; text-align: center; width: auto;'>
    <h1 font-size: 35px;>Prediction Models</h1> 
</div>
"""
st.markdown(info, unsafe_allow_html=True)

# ------------------------- pitcher outs predictions --------------------------------
# text = ''' This model predicts strikeouts for pitchers using data from the last five MLB seasons, sourced from the pybaseball library. It incorporates various pitching 
# # statistics such as innings pitched, walks, home runs, earned run average (ERA), WHIP (Walks plus Hits per Inning Pitched), Fielding Independent Pitching (FIP),
# # mistakes per appearance, and approximate batters faced per game. Utilizing LASSO regression with cross-validation, the model identifies
# # which features are most predictive of strikeouts and assesses their impact on the predictions. The results are visualized in a scatter plot 
# # comparing predicted versus actual strikeouts, with a trendline illustrating the relationship between these values. Hover tooltips provide
# # additional context by displaying key metrics like ERA, WHIP, and mistakes per appearance. The accuracy of the model is demonstrated by how closely the 
# # predicted strikeouts align with the actual values, offering insights into the effectiveness of various pitching metrics for forecasting performance.'''

text = ''' This model predicts strikeouts for pitchers using data from the last three MLB seasons, sourced from the pybaseball library. It incorporates various pitching 
statistics such as innings pitched, walks, home runs, earned run average (ERA), WHIP (Walks plus Hits per Inning Pitched), Fielding Independent Pitching (FIP),
mistakes per appearance, and approximate batters faced per game.Utilizing LASSO regression with cross-validation, the model identifies
# which features are most predictive of strikeouts and assesses their impact on the predictions. The results are visualized in a scatter plot 
# comparing predicted versus actual strikeouts, with a trendline illustrating the relationship between these values. Hover tooltips provide
# additional context by displaying key metrics like ERA, WHIP, and mistakes per appearance. The accuracy of the model is demonstrated by how closely the 
# predicted strikeouts align with the actual values, offering insights into the effectiveness of various pitching metrics for forecasting performance.'''
prediction_descrip = f"""
<div style=margin-bottom:5px; text-align: center; width: auto;'>
    <p font-size: 1px;>{text}</p> 
</div>
"""
st.markdown(prediction_descrip, unsafe_allow_html=True)

data = pd.concat([pitching_stats(year) for year in range(year - 3, year)])

data.reset_index(drop=True, inplace=True)

# Feature Engineering
data['MistakesPerAppearance'] = (data['BK'] + data['HBP'] + data['WP']) / data['G']
data['BattersFacedApprox'] = data['IP'] * 3  # Approximate batters faced per game

# Select relevant features and the target variable
features = ['Name', 'IP', 'BB', 'HR', 'ERA', 'WHIP', 'FIP', 'MistakesPerAppearance', 'BattersFacedApprox']
X = data[features].dropna()
y = data['SO'].loc[X.index]  # Ensure that y matches X
names = data['Name'].loc[X.index]  # Ensure names match X

# Split the data into training and testing sets
X_train, X_test, y_train, y_test, names_train, names_test = train_test_split(
    X, y, names, test_size=0.2, random_state=42
)

# Drop 'Name' from features
X_train = X_train.drop(columns=['Name'])
X_test = X_test.drop(columns=['Name'])

# Scale the features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Initialize and fit the LASSO model with cross-validation
lasso = LassoCV(alphas=[0.1, 1, 10], cv=5, max_iter=10000)
lasso.fit(X_train_scaled, y_train)

# Make predictions on the test set
y_pred = lasso.predict(X_test_scaled)

# Combine the results into a single DataFrame with additional hover data
results = pd.DataFrame({
    'Actual': y_test,
    'Predicted': y_pred,
    'IP': X_test['IP'].values,
    'ERA': X_test['ERA'].values,
    'WHIP': X_test['WHIP'].values,
    'MistakesPerAppearance': X_test['MistakesPerAppearance'].values,
    'BattersFacedApprox': X_test['BattersFacedApprox'].values,
    'Name': names_test.values
})
numeric_columns = ['Actual', 'Predicted', 'IP', 'ERA', 'WHIP', 'MistakesPerAppearance', 'BattersFacedApprox']
results[numeric_columns] = results[numeric_columns].round(2)

# Create the scatter plot with hover features
fig = px.scatter(
    results,
    x='Actual',
    y='Predicted',
    hover_name='Name',
    hover_data=['IP', 'ERA', 'WHIP', 'MistakesPerAppearance', 'BattersFacedApprox'],
    trendline='ols'
)

# Update the layout for better visualization
fig.update_layout(
    title='Predicted vs Actual Strikeouts',
    xaxis_title='Actual Strikeouts',
    yaxis_title='Predicted Strikeouts'
)

# Remove text labels from the dots
fig.update_traces(marker=dict(size=10), selector=dict(mode='markers'))

# Show the plot in Streamlit
st.plotly_chart(fig)
