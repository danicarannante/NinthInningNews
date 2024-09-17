import streamlit as st
from pybaseball import team_batting, team_pitching, standings, batting_stats, pitching_stats, schedule_and_record
from variables import team_mapping, img_mapping
import pandas as pd
from pybaseball import cache
import matplotlib.pyplot as plt
import seaborn as sns
import plotly 
import plotly.graph_objs as go
import plotly.express as px

cache.enable()
selected_team = st.sidebar.selectbox('Select a team:', st.session_state["teams"])
abv = team_mapping[selected_team]
year = st.session_state['year']

def get_team_logo_url(team):
    return f"https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/{img_mapping[team]}.png"
# ------------------------- Team Info Section ------------------------------------
info = f"""
<div style=' border-radius: 5px; text-align: center; width: auto;'>
    <div style="flex: 1;text-align: center;margin-bottom:10;">
    <img src="{get_team_logo_url(selected_team)}" width="150">
    </div>
</div>
"""
st.markdown(info, unsafe_allow_html=True)

bs = batting_stats(st.session_state['year'], end_season=st.session_state['year'], league='all', qual=1, ind=1)
team_batting = bs[bs["Team" ] == abv]


# ------------------------ win/loss graph -----------------------------
results = schedule_and_record(st.session_state['year'],team_mapping[selected_team]).get(['Date','Tm','W/L']).dropna()
results['W/L'] = results['W/L'].replace({'W-wo': 'W','L-lo': 'L','L-wo':'L'})

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

# ---------------------- player stats table ------------------------------
dataframe_header = f"""
    <div margin-bottom:10px; padding: 10px; border-radius: 5px; text-align: center; width: auto;'>
    <h1 style='margin-bottom: 5px; text-align: center; font-size: 20px'>Batting Metrics for Current Players</h1>
    </div>
    """
st.markdown(dataframe_header, unsafe_allow_html=True)

batting_df = team_batting[team_batting["AB"] > 10].get(['Name','AVG', 'OBP','wOBA','SLG','OPS','BABIP'])
st.dataframe(batting_df,hide_index=True, height=(37 * batting_df.shape[0]),use_container_width=True)


# ---------------------- leaderboards ------------------------
subheader = f"""
    <div margin-bottom:10px; padding: 10px; border-radius: 5px; text-align: center; width: auto;'>
        <h1 style='margin-bottom: 5px; text-align: center; font-size: 20px'>Top Players by Batting Metrics</h1>
    </div>
    """
st.markdown(subheader, unsafe_allow_html=True)


batting_stats_mappings = [{'name':'Batting Average','abv':'AVG','col':'1'},{'name':'Home Runs','abv':'HR','col':'1'},{'name':"RBIs",'abv':'RBI','col':'1'},
{'name':'On-Base Percentage', 'abv':'OBP','col':'2'},{'name':'Slugging Percentage', 'abv':'SLG','col':'2'},{'name':'OPS', 'abv':'OPS','col':'2'}]
col1,col2 = st.columns(2)

bs = batting_stats(st.session_state['year'], end_season=st.session_state['year'], league='all', qual=1, ind=1)
team_batting = bs[bs["Team" ] == abv]




for bs in batting_stats_mappings:
    top_val = team_batting.sort_values(by=bs['abv'], ascending=False).head(5).reset_index()
    title = f"""
    <div padding: 10px; text-align: center; width: auto;'>
        <h1 style='margin-bottom: 5px; text-align: center; font-size: 20px'>Top Players by {bs["name"]}</h1>
    </div>
    """
    if bs['col'] == '1':
        col1.markdown(title, unsafe_allow_html=True)
    elif bs['col'] == '2':
        col2.markdown(title, unsafe_allow_html=True)

    for idx, row in top_val.iterrows():
        player_name = row['Name']  # Replace with actual player column name
        stat_value = row[bs['abv']]  # Get the stat value for the specific abbreviation
        
        item = f"""
        <div style='text-align: center; width: auto;'>
            <p style='margin-bottom: 5px; text-align: center; font-size: 18px'>{idx + 1}. {player_name} - {stat_value}</p>
        </div>
        """

        if bs['col'] == '1':
            col1.markdown(item, unsafe_allow_html=True)
        elif bs['col'] == '2':
            col2.markdown(item, unsafe_allow_html=True)

    

# --------------------------- trending -------------------------
# for league in current_standings:
#     league.rename(columns={'Tm': 'Team'}, inplace=True)
#     league.drop(columns=['E#'], inplace=True)

#     for tm in league['Team'].tolist():      
#         results = schedule_and_record(st.session_state['year'], team_mapping[tm]).get(['Date','Tm','W/L']).dropna()
#         results['W/L'] = results['W/L'].replace({'W-wo': 'W','L-lo': 'L','L-wo':'L'})
#         results = results.sort_index(ascending=False).head(10)
#         results['win'] = results['W/L'].apply(lambda x: 1 if x == 'W' else 0)
#         results['loss'] = results['W/L'].apply(lambda x: 1 if x == 'L' else 0)
#         if results['win'].sum() >= 9:
#             league['trend'] = '⬆️'
#         elif results['loss'].sum() >= 9:
#             league['trend'] = '⬇️'
#         else:
#             league['trend'] = '➡️'