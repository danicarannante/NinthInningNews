import streamlit as st
from pybaseball import pitching_stats, playerid_lookup, statcast_pitcher,statcast, spraychart,plot_stadium, plot_strike_zone
from variables import team_mapping, get_league_data, stadium_mapping,pitch_type_mapping
import pandas as pd
import datetime 
import matplotlib.pyplot as plt
import seaborn as sns


selected_team = st.sidebar.selectbox('Select a team:', st.session_state["teams"])
abv = team_mapping[selected_team]

ps = pitching_stats(st.session_state['year'], end_season=st.session_state['year'], league='all', qual=1, ind=1)
filtered = ps[ps["Team" ] == abv]
players = sorted([name for name in filtered['Name']])
selected_player = st.sidebar.selectbox('Select a pitcher:', players)
player_info = filtered[filtered['Name'] == selected_player]
print(selected_player)

player_lookup = playerid_lookup(selected_player.split(" ")[1],selected_player.split(" ")[0]) # contains id to use in baseball reference
player_api_id = player_lookup['key_bbref'].values[0]
player_fangraphs_id = player_lookup['key_fangraphs'].values[0]
debut_date = int(player_lookup['mlb_played_first'].values[0])

# ------------------------- Player Info Section ------------------------------------
info = f"""
<div style='background-color: LightBlue; border-radius: 5px; text-align: center; width: auto;'>
    <h1 font-size: 35px'>{selected_player}</h1> 
    <p style='margin-bottom: 5px; font-size: 18px;'>Age: {player_info["Age"].values[0]} | Debut: {debut_date} | Team : {selected_team}</p>
</div>
"""
st.markdown(info, unsafe_allow_html=True)

# -------------------------- Player Stats --------------------------------------------
short_df = player_info.get(['W','L','G','GS','IP','WHIP','WAR','ERA','SV','FIP','xFIP','BB','SO','TTO%'])
st.dataframe(short_df,hide_index=True)

# ----------------------------------- Statcast Pitcher Table --------------------------
#data = statcast_batter('2008-04-01','2024-11-01',player_id=pid) # grab all historic data
pid = player_lookup['key_mlbam'].values[0]
data = statcast_pitcher(f"{st.session_state['year']}-01-01",f"{st.session_state['year']}-12-31",player_id=pid) # 1 year data for 2023, filter out foul balls,strikes, balls
data = data[data['game_type'] == 'R']
pitches_df = data.get(['player_name','release_speed','pitch_type'])
# st.dataframe(pitches_df,hide_index=True)

# -------------------------------- strike zone ---------------------------------

filtered_mapping = {v : k for k, v in pitch_type_mapping.items() if k in data['pitch_type'].dropna().unique()}
pitch_types = data['pitch_type'].dropna().unique() 
selected_pitch_type = st.selectbox("Select Pitch Type", list(filtered_mapping.keys()))
filtered_data = data[data['pitch_type'] == filtered_mapping[selected_pitch_type]]
fig = plot_strike_zone(filtered_data).get_figure()
st.pyplot(fig)

# ------------------------------------------------------------------------------
subheader = f"""
<div style='background-color: LightBlue; border-radius: 5px; text-align: center; width: auto;'>
    <p style='margin-bottom: 5px;'>Pitch Velocity Distribution</p> 
</div>
"""
st.markdown(subheader, unsafe_allow_html=True)

pitch_types = pitches_df['pitch_type'].unique()

for pitch_type in pitch_types:    
    # Create the distribution table
    pitch_type_data = pitches_df[pitches_df['pitch_type'] == pitch_type]    

    # Create the KDE plot
    fig, ax = plt.subplots(figsize=(8, 4))
    kde = sns.kdeplot(
        pitch_type_data['release_speed'],
        ax=ax, 
        fill=True,
        alpha=0.7,
        linewidth=1.5
    )  
    rate = (len(pitch_type_data) / len(pitches_df)) * 100
    ax.set_xlabel("Velocity (mph)")
    ax.set_ylabel("Density")
    median_velocity = pitch_type_data['release_speed'].median()
   
    ax.set_title(f"{pitch_type_mapping[pitch_type]} {median_velocity:.0f}mph | {rate:.2f}%") # mph, Peak Density: {median_density:.2f}")
    st.pyplot(fig)

print("you got this")