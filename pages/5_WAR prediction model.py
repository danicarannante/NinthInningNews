import os
import pandas as pd
import numpy as np
from pybaseball import pitching_stats
import streamlit as st

from sklearn.linear_model import Ridge
from sklearn.feature_selection import SequentialFeatureSelector
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import MinMaxScaler
import seaborn as sns
import matplotlib.pyplot as plt
from pybaseball import cache

info = f"""
<div style='background-color: LightBlue; border-radius: 5px; text-align: center; width: auto;'>
    <h1 style='font-size: 30px;'>WAR Predictions Model </h1> 
    <p style='font-size: 20px;'>Ridge Regression Model </p> 
</div>
"""
st.markdown(info, unsafe_allow_html=True)

START = 2002
END = 2023

# load data / data cleaning
cache.enable()
with st.spinner("Loading model..."):
    pitching = pitching_stats(START, END, qual=50) # at least 50 innings
    pitching = pitching[pitching['Season'] != 2020]
pitching = pitching.groupby("IDfg", group_keys=False).filter(lambda x: x.shape[0] > 1)

def next_season(player):
    player = player.sort_values("Season")
    player["Next_WAR"] = player["WAR"].shift(-1)
    return player

pitching = pitching.groupby("IDfg", group_keys=False).apply(next_season)
print(pitching.head())


# filter out non null columns
null_count = pitching.isnull().sum()
complete_cols = list(pitching.columns[null_count == 0])
pitching = pitching[complete_cols + ["Next_WAR"]].copy()

# delete object types
# pitching.dtypes[pitching.dtypes == "object"]
del pitching["Dollars"]
del pitching["Age Rng"]
del pitching["Team"]

# drop the seasons where the Next_WAR is null
pitching_full = pitching.copy()
pitching = pitching.dropna()
print(pitching.dtypes)

# ------------------------- setting up the model  ( Ridge Regression ) -------------------
# https://medium.com/@luhgoldfarb/a-beginner-friendly-intro-to-data-science-in-baseball-a7d8af2b8d12#5c54

rr = Ridge(alpha=1) # alpha = 0 -> simple linear regression

split = TimeSeriesSplit(n_splits=3)

sfs = SequentialFeatureSelector(rr, n_features_to_select=20, direction="forward", cv=split, n_jobs=4)
# standardize the data by scaling all values to a range of 0 to 1. In our process, we selectively exclude certain columns that need to maintain their original scale and only apply this scaling to the remaining columns.
removed_columns = ["Next_WAR", "Name", "IDfg", "Season", "GS"]
selected_columns = pitching.columns[~pitching.columns.isin(removed_columns)]

scaler = MinMaxScaler()
pitching.loc[:, selected_columns] = scaler.fit_transform(pitching[selected_columns])
sfs.fit(pitching[selected_columns], pitching["Next_WAR"])

predictors = list(selected_columns[sfs.get_support()])

# ------------------------- training the model -------------------
def backtest(data, model, predictors, start=9, step=1):
    all_predictions = []
    years = sorted(data["Season"].unique())

    for i in range(start, len(years), step):
        current_year = years[i]
        train = data[data["Season"] < current_year]
        test = data[data["Season"] == current_year]
    
        model.fit(train[predictors], train["Next_WAR"])
        preds = model.predict(test[predictors]) #returns a numpy array 
        preds = pd.Series(preds, index=test.index) #we do this to make it a Series
        combined = pd.concat([test[["Season", "Next_WAR"]], preds.rename("predictions")], axis=1) #combine the Series
        combined["actual"] = combined["Next_WAR"]
        combined = combined.drop("Next_WAR", axis=1)
    
        all_predictions.append(combined)

    return pd.concat(all_predictions)

# --------------------------- improvements ----------------------
pitching = pitching[pitching['Season'] != 2020]
predictions = backtest(pitching, rr, predictors)

# ---------------------- evaluate the model --------------------------------
# RMSE is the average error of the predictions, but to account for negative values we first square the values and then take the root.
# If our error is less than the deviation, it indicates that our model is more accurate than picking essentially at random.
pitching["Next_WAR"].describe()
from sklearn.metrics import mean_squared_error

mse = mean_squared_error(predictions["actual"], predictions["predictions"])
rmse = mse ** 0.5


# --------------------------- visualization --------------------

plt.figure(figsize=(12, 6))

sns.lineplot(x='Season', y='actual', data=predictions, label='Actual WAR', marker='o')

sns.lineplot(x='Season', y='predictions', data=predictions, label='Predicted WAR', marker='o')

plt.title('Actual WAR vs Predicted WAR Over Time')
plt.xlabel('Season')
plt.ylabel('WAR')
plt.legend()

st.pyplot(plt)


# --------------------------- new metrics ----------------------------
obv = f"""
<div style='border-radius: 5px; text-align: center; width: auto;'>
    <h1 style='font-size: 25px;'>Coefficient Analysis</h1>
    <p style='font-size: 20px;'>Positive values suggest that these coefficients are positively related to the Next_WAR</p> 
    <p style='font-size: 20px;'>A higher SO (Strikeouts) indicates a greater WAR with the opposite being true for a feature like Age, suggesting that WAR decreases as players get older</p> 
</div>
"""
st.markdown(obv, unsafe_allow_html=True)

# R-squared is a measure of how well the independent variables explain the variation in the dependent variable.
from sklearn.metrics import r2_score

r_squared = r2_score(predictions['actual'], predictions['predictions'])
feature_names = predictors


coefs_df = pd.DataFrame({
    'Feature': feature_names,
    'Coefficient': rr.coef_
})

coefs_df = coefs_df.reindex(coefs_df.Coefficient.abs().sort_values(ascending=False).index)

plt.figure(figsize=(10, 8))
sns.barplot(x='Coefficient', y='Feature', data=coefs_df)
plt.title('Coefficient Plot of Ridge Regression Model')
plt.xlabel('Coefficient Value')
plt.ylabel('Feature')
st.pyplot(plt)

# Variable Inflation Factor (VIF). VIF puts a number behind what we’re talking about. The more severe the multicollinearity, the higher the VIF
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor

X = pitching[predictors]
X = sm.add_constant(X)

vif = pd.DataFrame()
vif["variables"] = X.columns
vif["VIF"] = [variance_inflation_factor(X.values, i) for i in range(X.shape[1])]

# want to keey the values below 8 - GS seems to be a problem so we add it to our remove columns from above
