import streamlit as st
from pybaseball import team_batting, team_pitching, standings, batting_stats, pitching_stats, schedule_and_record
from variables import team_mapping
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

# ------------------------- Team Info Section ------------------------------------
info = f"""
<div style='background-color: LightBlue; border-radius: 5px; text-align: center; width: auto;'>
    <h1 style='margin-bottom:10px; font-size: 30px'>{selected_team}</h1> 
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

batting_df = team_batting.get(['Name','AVG', 'OBP','wOBA','SLG','OPS','BABIP'])
st.dataframe(batting_df,hide_index=True, height=(37 * batting_df.shape[0]),use_container_width=True)



#     ## On-Base Percentage (OBP)
#     **Description:** Represents the frequency a player reaches base via hits, walks, or hit by pitches divided by total plate appearances.  
#     **League Average:** 0.320  
#     **High vs. Low:** Higher values are better; a higher OBP means a player gets on base more often, which is advantageous for scoring runs.  
    
#     ---
    
#     ## Weighted On-Base Average (wOBA)
#     **Description:** Provides a more comprehensive measure of a player's offensive contributions by weighing different types of hits and plate appearances more accurately.  
#     **League Average:** 0.320  
#     **High vs. Low:** Higher values are better; a higher wOBA reflects more effective offensive performance, including power and contact skills.  
    
#     ---
    
#     ## Slugging Percentage (SLG)
#     **Description:** Measures a player's power by dividing total bases by the number of at-bats. It accounts for extra-base hits.  
#     **League Average:** 0.410  
#     **High vs. Low:** Higher values are better; a higher SLG indicates more power and greater ability to hit for extra bases.  
    
#     ---
    
#     ## On-Base Plus Slugging (OPS)
#     **Description:** Combines OBP and SLG to provide an overall measure of a player's offensive ability.  
#     **League Average:** 0.730  
#     **High vs. Low:** Higher values are better; a higher OPS indicates overall offensive effectiveness, combining both getting on base and hitting for power.  
    
#     ---
    
#     ## Batting Average on Balls In Play (BABIP)
#     **Description:** Measures how often a ball put into play by a batter falls for a hit, excluding home runs and strikeouts.  
#     **League Average:** 0.300  
#     **High vs. Low:** Higher values generally indicate better luck or skill with hitting balls in play. However, extreme values can suggest luck or poor defense.
#     """)


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
    top_val = team_batting.sort_values(by=bs['abv'], ascending=True).head(5)
    fig = px.bar(
        top_val,
        x=bs['abv'],
        y='Name',
        orientation='h',
        title=bs['name'],
        labels={bs['abv']: bs['name'], 'Name': 'Player'},
        text=bs['abv']
    )

    if bs['col'] == '1':
        col1.plotly_chart(fig,use_container_width=True)
    else:
        col2.plotly_chart(fig,use_container_width=True)

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