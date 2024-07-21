import streamlit as st
from pybaseball import team_batting, team_pitching, schedule_and_record
import pandas as pd
from variables import team_mapping
from pybaseball import cache

cache.enable()
# Year selection
year = st.sidebar.slider('Select Year', min_value=2000, max_value=2024, value=2023)

# -------------------------  Info Section ------------------------------------
info = f"""
<div style='background-color: LightBlue; margin-bottom:10px;border-radius: 5px; text-align: center; width: auto;'>
    <h1 font-size: 35px;>{year} Season Leaderboards</h1> 
</div>
"""
st.markdown(info, unsafe_allow_html=True)
# ------------------------------------------------------------------
# for t in team_mapping:
#     print(t)
#     df = schedule_and_record(st.session_state['year'],)
#     df['W/L'] = df['W/L'].replace({'W-wo': 'W','L-lo': 'L'})
#     # Count wins and losses
#     team_stats = df.groupby('Team')['W/L'].value_counts().unstack(fill_value=0).reset_index()
#     team_stats.columns = ['team', 'losses', 'wins']  # Rename columns for clarity
#     # Display the processed data
#     print(team_stats.head())
#     team_stats_long = team_stats.melt(id_vars='Team', value_vars=['wins', 'losses'], 
#                                     var_name='result_type', value_name='count')
#     # Create the bar chart
# fig = px.bar(team_stats_long, x='team', y='count', color='result_type', 
#              labels={'count': 'Total Count', 'result_type': 'Result'},
#              title='Total Wins and Losses for All Teams',
#              barmode='group')
# st.plotly_chart(fig)


# ------------------------------------------------------------------
batting_stats = team_batting(year)
top_n = st.sidebar.slider('Select number of top teams to display', min_value=5, max_value=30, value=10)
reverse_mapping = {v : k for k, v in team_mapping.items()}

# -------------------------- batter leaderboards --------------------------------- 
batting_stats_mappings = [{'name':'Batting Average','abv':'AVG'},{'name':'Home Runs','abv':'HR'},{'name':"RBI's",'abv':'RBI'},{'name':'On-Base Percentage', 'abv':'OBP'},{'name':'Slugging Percentage', 'abv':'SLG'},{'name':'OPS', 'abv':'OPS'}]
for bs in batting_stats_mappings:
    title = f"""
    <div style='background-color: LightBlue; margin-bottom:5px; padding: 5px; border-radius: 5px; text-align: center; width: auto;'>
        <p1 text-align: center; font-size: 50px'>Top Teams by {bs['name']}</p1>
    </div>
    """
    st.markdown(title, unsafe_allow_html=True)
    top_val = batting_stats.sort_values(by=bs['abv'], ascending=False).head(top_n).reindex()
    top_val.reset_index(drop=True, inplace=True)
    top_val.index = top_val.index 
    top_val.insert(0, 'Rank', top_val.index)

    # Display the ranking
    half = len(top_val) // 2
    col1, col2 = st.columns(2)
    with col1:
        left_rankings = '\n'.join([f"{i+1}. {reverse_mapping[row['Team']]} {row[bs['abv']]}" for i, row in top_val.iloc[:half].iterrows()])
        st.markdown(left_rankings)
    with col2:
        right_rankings = '\n'.join([f"{i+1}. {reverse_mapping[row['Team']]} {row[bs['abv']]}" for i, row in top_val.iloc[half:].iterrows()])
        st.markdown(right_rankings)

# ------------------------------ pitching leaders -------------------------------
pitching_stats = team_pitching(year)
pitching_stats_mappings = [{'name':'ERA','abv':'ERA'},{'name':'WHIP','abv':'WHIP'},{'name':"Strikeouts",'abv':'SO'},{'name':'Walks', 'abv':'BB'},{'name':'Saves', 'abv':'SV'}]
for ps in pitching_stats_mappings:
    title = f"""
    <div style='background-color: LightBlue; margin-bottom:5px; padding: 5px; border-radius: 5px; text-align: center; width: auto;'>
        <p1 text-align: center; font-size: 50px'>Top Teams by {ps['name']}</p1>
    </div>
    """
    st.markdown(title, unsafe_allow_html=True)
    if ps['abv'] in ['ERA','WHIP','BB']:
        top_val = pitching_stats.sort_values(by=ps['abv'], ascending=True).head(top_n).reindex()
    else:
        top_val = pitching_stats.sort_values(by=ps['abv'], ascending=False).head(top_n).reindex()
    top_val.reset_index(drop=True, inplace=True)
    top_val.index = top_val.index 
    top_val.insert(0, 'Rank', top_val.index)

    # Display the ranking
    half = len(top_val) // 2
    col1, col2 = st.columns(2)
    with col1:
        left_rankings = '\n'.join([f"{i+1}. {reverse_mapping[row['Team']]} {row[ps['abv']]}" for i, row in top_val.iloc[:half].iterrows()])
        st.markdown(left_rankings)
    with col2:
        right_rankings = '\n'.join([f"{i+1}. {reverse_mapping[row['Team']]} {row[ps['abv']]}" for i, row in top_val.iloc[half:].iterrows()])
        st.markdown(right_rankings)
