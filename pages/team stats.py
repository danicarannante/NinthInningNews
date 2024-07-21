import streamlit as st
from pybaseball import team_batting, team_pitching, standings, batting_stats, pitching_stats, schedule_and_record
from variables import team_mapping
import pandas as pd
from pybaseball import cache
import matplotlib.pyplot as plt
import seaborn as sns
import plotly 
import plotly.graph_objs as go

cache.enable()
selected_team = st.sidebar.selectbox('Select a team:', st.session_state["teams"])
abv = team_mapping[selected_team]
year = st.session_state['year']

# ------------------------- Team Info Section ------------------------------------
info = f"""
<div style='background-color: LightBlue; border-radius: 5px; text-align: center; width: auto;'>
    <h1 style='margin-bottom:10px; font-size: 35px'>{selected_team}</h1> 
</div>
"""
st.markdown(info, unsafe_allow_html=True)

bs = batting_stats(st.session_state['year'], end_season=st.session_state['year'], league='all', qual=1, ind=1)
team_batting = bs[bs["Team" ] == abv]

# ------------------------ win/loss graph -----------------------------
results = schedule_and_record(st.session_state['year'],team_mapping[selected_team]).get(['Date','Tm','W/L']).dropna()
results['W/L'] = results['W/L'].replace({'W-wo': 'W','L-lo': 'L'})

# Transform data
results['win'] = results['W/L'].apply(lambda x: 1 if x == 'W' else 0)
results['loss'] = results['W/L'].apply(lambda x: 1 if x == 'L' else 0)

fig = go.Figure()
fig.add_trace(go.Scatter(x=results['Date'], y=results['win'].cumsum(), mode='lines+markers', name='Wins', line=dict(color='green')))
fig.add_trace(go.Scatter(x=results['Date'], y=results['loss'].cumsum(), mode='lines+markers', name='Losses', line=dict(color='red')))

fig.update_layout(title=f'Wins and Losses for {st.session_state["year"]}',
    xaxis_title='Date',
    yaxis_title='Cumulative Count',
    yaxis=dict(tickvals=[0, 1], ticktext=['0', '1']))

st.plotly_chart(fig)

# ---------------------- heatmap ------------------------------
batting_heatmap = team_batting.get(['Name','AVG', 'OBP','wOBA','SLG','OPS','BABIP']).dropna()
pivot_table = batting_heatmap.pivot_table(index='Name', values=batting_heatmap.columns)
# Create heatmap for the selected metric
plt.figure(figsize=(12, 10))
ax = sns.heatmap(pivot_table, cmap="crest", annot=True, fmt=".3f", cbar=True)
ax.set_title(f'Heatmap for Players')
ax.set_xlabel('')
ax.set_ylabel('')
ax.tick_params(left=False, bottom=False)
st.pyplot(plt.gcf())

# ---------------------- leaderboards ------------------------
top_n = st.sidebar.slider('Select number of top players to display', min_value=5, max_value=10, value=10)
batting_stats_mappings = [{'name':'Batting Average','abv':'AVG'},{'name':'Home Runs','abv':'HR'},{'name':"RBIs",'abv':'RBI'},{'name':'On-Base Percentage', 'abv':'OBP'},{'name':'Slugging Percentage', 'abv':'SLG'},{'name':'OPS', 'abv':'OPS'}]
for bs in batting_stats_mappings:
    title = f"""
    <div style='background-color: LightBlue; margin-bottom:5px; padding: 5px; border-radius: 5px; text-align: center; width: auto;'>
        <p1 text-align: center; font-size: 50px'>Top Players by {bs['name']}</p1>
    </div>
    """
    st.markdown(title, unsafe_allow_html=True)
    top_val = team_batting.sort_values(by=bs['abv'], ascending=False).head(top_n).reindex()
    top_val.reset_index(drop=True, inplace=True)
    top_val.index = top_val.index 
    top_val.insert(0, 'Rank', top_val.index)

    # Display the ranking
    half = len(top_val) // 2
    col1, col2 = st.columns(2)
    with col1:
        left_rankings = '\n'.join([f"{i+1}. {row['Name']} {row[bs['abv']]}" for i, row in top_val.iloc[:half].iterrows()])
        st.markdown(left_rankings)
    with col2:
        right_rankings = '\n'.join([f"{i+1}. {row['Name']} {row[bs['abv']]}" for i, row in top_val.iloc[half:].iterrows()])
        st.markdown(right_rankings)