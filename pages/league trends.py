import streamlit as st
from pybaseball import team_batting, team_pitching
import pandas as pd

# Year selection
year = st.sidebar.slider('Select Year', min_value=2000, max_value=2024, value=2023)

# Display basic team stats
st.header(f"{year} Season Leaderboards")

# Fetch team batting stats
batting_stats = team_batting(year)

# Display team batting leaderboard
st.subheader("Team Batting Leaderboard")

# Select top N teams to display
top_n = st.sidebar.slider('Select number of top teams to display', min_value=5, max_value=30, value=10)

# Display top teams by various batting stats
st.write("### Top Teams by Batting Average")
top_batting_avg = batting_stats.sort_values(by='AVG', ascending=False).head(top_n)
st.dataframe(top_batting_avg[['Team', 'AVG']])

st.write("### Top Teams by Home Runs")
top_home_runs = batting_stats.sort_values(by='HR', ascending=False).head(top_n)
st.dataframe(top_home_runs[['Team', 'HR']])

st.write("### Top Teams by RBIs")
top_rbis = batting_stats.sort_values(by='RBI', ascending=False).head(top_n)
st.dataframe(top_rbis[['Team', 'RBI']])

st.write("### Top Teams by On-Base Percentage")
top_obp = batting_stats.sort_values(by='OBP', ascending=False).head(top_n)
st.dataframe(top_obp[['Team', 'OBP']])

st.write("### Top Teams by Slugging Percentage")
top_slg = batting_stats.sort_values(by='SLG', ascending=False).head(top_n)
st.dataframe(top_slg[['Team', 'SLG']])

st.write("### Top Teams by OPS")
top_ops = batting_stats.sort_values(by='OPS', ascending=False).head(top_n)
st.dataframe(top_ops[['Team', 'OPS']])

# Fetch team pitching stats
pitching_stats = team_pitching(year)

# Display team pitching leaderboard
st.subheader("Team Pitching Leaderboard")

# Display top teams by various pitching stats
st.write("### Top Teams by ERA")
top_era = pitching_stats.sort_values(by='ERA', ascending=True).head(top_n)
st.dataframe(top_era[['Team', 'ERA']])

st.write("### Top Teams by WHIP")
top_whip = pitching_stats.sort_values(by='WHIP', ascending=True).head(top_n)
st.dataframe(top_whip[['Team', 'WHIP']])

st.write("### Top Teams by Strikeouts")
top_strikeouts = pitching_stats.sort_values(by='SO', ascending=False).head(top_n)
st.dataframe(top_strikeouts[['Team', 'SO']])

st.write("### Top Teams by Walks")
top_walks = pitching_stats.sort_values(by='BB', ascending=True).head(top_n)
st.dataframe(top_walks[['Team', 'BB']])

st.write("### Top Teams by Saves")
top_saves = pitching_stats.sort_values(by='SV', ascending=False).head(top_n)
st.dataframe(top_saves[['Team', 'SV']])
