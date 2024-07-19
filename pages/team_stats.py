import streamlit as st
from pybaseball import team_batting, team_pitching, standings, batting_stats, pitching_stats
from variables import team_mapping
import pandas as pd


selected_team = st.sidebar.selectbox('Select a team:', st.session_state["teams"])
abv = team_mapping[selected_team]
year = st.session_state['year']

# batting = team_batting(year, year, league='all', qual=1, ind=1)
# team_batting = batting[batting["Team" ] == abv]

# -------------------------- batter leaderboards --------------------------------- 
bs = batting_stats(st.session_state['year'], end_season=st.session_state['year'], league='all', qual=1, ind=1)
team_batting = bs[bs["Team" ] == abv]

# Select top N players to display
top_n = st.sidebar.slider('Select number of top players to display', min_value=5, max_value=20, value=10)
# key = f"""
# <div style='background-color: LightBlue; margin-bottom:10px; padding: 10px; border-radius: 5px; text-align: center; width: auto;'>
#     <p1 text-align: center; font-size: 20px'>Yellow: Within + or -.005 of league average value <br> Green: Greater than league average value <br> Pink: Less than league average value </p1>
# </div>
# """
# st.sidebar.markdown(key, unsafe_allow_html=True)

batting_stats_mappings = [{'name':'Batting Average','abv':'AVG'},{'name':'Home Runs','abv':'HR'},{'name':"RBI's",'abv':'RBI'},{'name':'On-Base Percentage', 'abv':'OBP'},{'name':'Slugging Percentage', 'abv':'SLG'},{'name':'OPS', 'abv':'OPS'}]
for bs in batting_stats_mappings:
    title = f"""
    <div style='background-color: LightBlue; margin-bottom:5px; padding: 5px; border-radius: 5px; text-align: center; width: auto;'>
        <p1 text-align: center; font-size: 50px'>Top Players by {bs['name']}</p1>
    </div>
    """
    st.markdown(title, unsafe_allow_html=True)

    top_val = team_batting.sort_values(by=bs['abv'], ascending=False).head(top_n).reindex()
    print(top_val)
    top_val.reset_index(drop=True, inplace=True)
    top_val.index = top_val.index 
    top_val.insert(0, 'Rank', top_val.index)

    # Display the rankings

    half = len(top_val) // 2
    col1, col2 = st.columns(2)
    with col1:
        left_rankings = '\n'.join([f"{i+1}. {row['Name']} {row[bs['abv']]}" for i, row in top_val.iloc[:half].iterrows()])
        st.markdown(left_rankings)
    with col2:
        right_rankings = '\n'.join([f"{i+1}. {row['Name']} {row[bs['abv']]}" for i, row in top_val.iloc[half:].iterrows()])
        st.markdown(right_rankings)




# # ------------------------------pitching leaderboards----------------------------------- 
   
# Fetch player pitching stats
pitching = pitching_stats(year)
team_pitching = pitching[pitching['Team'] == team_mapping[selected_team]]

pitching_stats_mappings = [{'name':'ERA','abv':'ERA'},{'name':'WHIP','abv':'WHIP'},{'name':"Strikeouts",'abv':'SO'},{'name':'Walks', 'abv':'BB'},{'name':'Saves', 'abv':'SV'}]
for ps in pitching_stats_mappings:
    title = f"""
    <div style='background-color: LightBlue; margin-bottom:5px; padding: 5px; border-radius: 5px; text-align: center; width: auto;'>
        <p1 text-align: center; font-size: 50px'>Top Players by {ps['name']}</p1>
    </div>
    """
    st.markdown(title, unsafe_allow_html=True)
    if ps['abv'] == 'ERA':
        top_val = team_pitching.sort_values(by=ps['abv'], ascending=True).head(top_n).reindex()
    else:
        top_val = team_pitching.sort_values(by=ps['abv'], ascending=False).head(top_n).reindex()
    top_val.reset_index(drop=True, inplace=True)
    top_val.index = top_val.index 
    top_val.insert(0, 'Rank', top_val.index)

    # Display the rankings

    half = len(top_val) // 2
    col1, col2 = st.columns(2)
    with col1:
        left_rankings = '\n'.join([f"{i+1}. {row['Name']} {row[ps['abv']]}" for i, row in top_val.iloc[:half].iterrows()])
        st.markdown(left_rankings)
    with col2:
        right_rankings = '\n'.join([f"{i+1}. {row['Name']} {row[ps['abv']]}" for i, row in top_val.iloc[half:].iterrows()])
        st.markdown(right_rankings)



