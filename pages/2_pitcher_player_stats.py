import streamlit as st
from pybaseball import pitching_stats, playerid_lookup, statcast_pitcher, statcast, spraychart,plot_stadium, plot_strike_zone
from variables import team_mapping, get_league_data, stadium_mapping,pitch_type_mapping
import pandas as pd
import datetime 
import matplotlib.pyplot as plt
from plotly.subplots import make_subplots
import seaborn as sns
import plotly.express as px
import numpy as np
import plotly.graph_objs as go
from pybaseball import cache

cache.enable()

selected_team = st.sidebar.selectbox('Select a team:', st.session_state["teams"])
abv = team_mapping[selected_team]

ps = pitching_stats(st.session_state['year'], end_season=st.session_state['year'], league='all', qual=1, ind=1)
filtered = ps[ps["Team" ] == abv]
players = sorted([name for name in filtered['Name']])
selected_player = st.sidebar.selectbox('Select a pitcher:', players)
player_info = filtered[filtered['Name'] == selected_player].get(['Age','W','L','G','GS','IP','WHIP','WAR','ERA','SV','FIP','xFIP','BB','SO','TTO%'])
print(selected_player)

player_lookup = playerid_lookup(selected_player.split(" ")[1],selected_player.split(" ")[0]) # contains id to use in baseball reference
player_api_id = player_lookup['key_mlbam'].values[0]
player_fangraphs_id = player_lookup['key_fangraphs'].values[0]
debut_date = int(player_lookup['mlb_played_first'].values[0])
img_url = f"https://securea.mlb.com/mlb/images/players/head_shot/{player_api_id}.jpg"

# ------------------------- Player Info Section ------------------------------------
info = f"""
<div style='background-color: LightBlue; border-radius: 5px; padding: 10px; margin-bottom: 5px;display: flex; align-items: center;'>
    <img src='{img_url}' style='width: 100px; margin-right: 15px; border-radius: 5px;'>
    <div style='flex-grow: 1; text-align: center; display: flex; flex-direction: column; justify-content: center;'>
        <h1 style='text-align: center; font-size: 35px;'>{selected_player}</h1> 
        <p style='font-size: 20px;'>Age: {player_info["Age"].values[0]} | Debut: {debut_date} | Team : {selected_team}</p>
    </div>
</div>
"""
st.markdown(info, unsafe_allow_html=True)


# -------------------------- Player Stats --------------------------------------------
short_df = player_info.get(['W','L','G','GS','IP','WHIP','WAR','ERA','SV','FIP','xFIP','BB','SO','TTO%'])
st.dataframe(short_df,hide_index=True)

# ----------------------------------- Statcast Pitcher Table --------------------------
pid = player_lookup['key_mlbam'].values[0]
data = statcast_pitcher(f"{st.session_state['year']}-01-01",f"{st.session_state['year']}-12-31",player_id=pid)#.get(['player_name','release_speed','events','pitch_type','game_type','plate_x','plate_z']) # 1 year data for 2023, filter out foul balls,strikes, balls
data = data[data['game_type'] == 'R']
pitches_df = data.get(['player_name','release_speed','pitch_type'])

# ----------------------- strike zone display and velocity distribution  --------------------------
subheader = f"""
    <div margin-bottom:5px; padding: 10px; border-radius: 5px; text-align: center; width: auto;'>
        <h1 style='text-align: center; font-size: 20px'>Pitch Distribution</h1>
    </div>
    """

st.markdown(subheader, unsafe_allow_html=True)

filtered_mapping = {v : k for k, v in pitch_type_mapping.items() if k in data['pitch_type'].dropna().unique()}
pitch_types = data['pitch_type'].dropna().unique() 
selected_pitch_type = st.selectbox('',list(filtered_mapping.keys()))
filtered_data = data[data['pitch_type'] == filtered_mapping[selected_pitch_type]] 
avg_val = filtered_data['release_speed'].median()
filtered_avg_data = filtered_data[filtered_data['release_speed'] > avg_val] 
fig = plot_strike_zone(filtered_avg_data).get_figure()

col1,col2 = st.columns(2)
col2.pyplot(fig)
descript = f"""
<div style='text-align: center; width: auto;'>
    <p style='margin-bottom: 0px;'><em>pitches above {avg_val}mph </em></p> 
</div>
"""
col2.markdown(descript, unsafe_allow_html=True)

# ------------------------------------------------------------------------------

fig, ax = plt.subplots(figsize=(8, 4))
kde = sns.kdeplot(
    filtered_data['release_speed'],
    ax=ax, 
    fill=True,
    alpha=0.7,
    linewidth=1.5
)  
rate = (len(filtered_data) / len(pitches_df)) * 100
ax.set_xlabel("Velocity (mph)")
ax.set_ylabel("Density")
median_velocity = filtered_data['release_speed'].median()

ax.set_title(f"{selected_pitch_type} {median_velocity:.0f}mph | {rate:.2f}%")
col1.write(" ")
col1.write(" ")
col1.write(" ")
col1.pyplot(fig)

print("you got this")

