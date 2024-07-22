import streamlit as st
from pybaseball import batting_stats,playerid_lookup, statcast_batter,statcast, spraychart,plot_stadium
from variables import team_mapping, wOBA, create_summary_table, classify_hit, get_league_data, stadium_mapping, get_comparison
import pandas as pd
import datetime 
import matplotlib.pyplot as plt
import seaborn as sns
from pybaseball import cache

cache.enable()
# player stats page

selected_team = st.sidebar.selectbox('Select a team:', st.session_state["teams"])
abv = team_mapping[selected_team]

bs = batting_stats(st.session_state['year'], end_season=st.session_state['year'], league='all', qual=1, ind=1)
filtered = bs[bs["Team" ] == abv]
players = sorted([name for name in filtered['Name']])
selected_player = st.sidebar.selectbox('Select a player:', players)
player_info = filtered[filtered['Name'] == selected_player].get(['Age','G','AB','PA','H','1B','2B','3B','HR','R','RBI','BB','HBP','SF','SH','wOBA','xwOBA'])
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
short_df = player_info.get(['G','AB','PA','H','1B','2B','3B','HR','R','RBI','BB','HBP','SF','SH'])
st.dataframe(short_df,hide_index=True)

col1,col2 = st.columns(2)
season_wOBA = f"""
<div style='background-color: LightBlue; margin-bottom:1px; padding: 1px; border-radius: 5px; text-align: center; width: auto;'>
    <h1 style='margin-bottom: 1px; font-size: 34px'>{player_info['wOBA'].values[0]}</h1>
    <p style='margin-bottom: 1px; font-size: 18px;'>{st.session_state['year']} wOBA for {selected_player}</p>
    
</div>
"""
season_xwOBA = f"""
<div style='background-color: LightBlue; margin-bottom:1px; padding: 1px; border-radius: 5px; text-align: center; width: auto;'>
    <h1 style='margin-bottom: 1px; font-size: 34px'>{player_info['xwOBA'].values[0]}</h1>
    <p style='margin-bottom: 1px; font-size: 18px;'>{st.session_state['year']} wOBA for {selected_player}</p>
</div>
"""
with col1:
    st.markdown(season_wOBA, unsafe_allow_html=True)
with col2:
    st.markdown(season_xwOBA, unsafe_allow_html=True)

# ----------------------------------- Statcast Batter Table --------------------------
#data = statcast_batter('2008-04-01','2024-11-01',player_id=pid) # grab all historic data
pid = player_lookup['key_mlbam'].values[0]
data = statcast_batter(f"{st.session_state['year']}-01-01",f"{st.session_state['year']}-12-31",player_id=pid).get(['player_name','p_throws','launch_angle','launch_speed','hit_location','bb_type','stand','events','woba_value','estimated_woba_using_speedangle','woba_denom','game_type','hc_x','hc_y']) # 1 year data for 2023, filter out foul balls,strikes, balls
data = data[data['game_type'] == 'R']
data['bb_type'] = data['bb_type'] .replace({'ground_ball': 'ground ball','line_drive': 'line drive','fly_ball':'fly ball'})

hits_df = data[data['events'].isin(['single','double','triple','home_run'])] #.get(['player_name','launch_angle','launch_speed','hit_location','bb_type','stand','events','woba_value','estimated_woba_using_speedangle','woba_denom'])
hits_df['hit_classification'] = hits_df.apply(classify_hit, axis=1)
hit_summary_df = create_summary_table(hits_df).set_index('batted ball type')


if 'league_data' in st.session_state:
    league_data = st.session_state['league_data']
    hits_league_data = league_data[league_data['events'].isin(['single','double','triple','home_run'])] # .get(['player_name','hit_location','launch_angle','launch_speed','bb_type','stand','events','woba_value','estimated_woba_using_speedangle','woba_denom'])
    hits_league_data['bb_type'] = hits_league_data['bb_type'] .replace({'ground_ball': 'ground ball','line_drive': 'line drive','fly_ball':'fly ball'})
    hits_league_data['hit_classification'] = hits_league_data.apply(classify_hit, axis=1)
    league_summary_df = create_summary_table(hits_league_data).set_index('batted ball type')
    player_title= f"""
    <div margin-bottom:10px; padding: 10px; border-radius: 5px; text-align: center; width: auto;'>
        <h1 style='margin-bottom: 5px; text-align: center; font-size: 20px'>Directional Batted Ball Average Statistics for {st.session_state["year"]}</h1>
    </div>
    """
    st.markdown(player_title, unsafe_allow_html=True)
    st.dataframe(get_comparison(hit_summary_df,league_summary_df),use_container_width=True)
key = f"""
<div style='background-color: LightBlue; margin-bottom:10px; padding: 10px; border-radius: 5px; text-align: center; width: auto;'>
    <p1 text-align: center; font-size: 20px'>Yellow: Within + or -.005 of league average value <br> Green: Greater than league average value <br> Pink: Less than league average value </p1>
</div>
"""
st.sidebar.markdown(key, unsafe_allow_html=True)

# ----------------------------- Hits spraychart ----------------------------- 
spray_title = f"""
<div style='background-color: LightBlue; border-radius: 5px; text-align: center; width: auto;'>
    <h1 style='margin-bottom: 5px; font-size: 18px;'> Hit Type Outcomes for L vs R Handed Pitchers </h1>
</div>
"""
st.markdown(spray_title, unsafe_allow_html=True)

col1,col2 = st.columns(2)
hit_types = data['bb_type'].dropna().unique()  
selected_hit_type = col1.selectbox("Select Hit Type", hit_types)
pitcher_selection = col2.selectbox("Right Handed or Left Handed Pitcher", ['R','L'])
filtered_data = data[data['bb_type'] == selected_hit_type]
filter_data = filtered_data[filtered_data['p_throws'] == pitcher_selection]
print(filter_data)
fig = spraychart(filtered_data, stadium_mapping[selected_team], size=50, title=f"{selected_hit_type} for {st.session_state['year']}").get_figure()
st.pyplot(fig)
# --------------------------------------------------------------
