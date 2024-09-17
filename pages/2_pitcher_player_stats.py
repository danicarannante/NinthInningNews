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
filtered = ps[(ps["Team" ] == abv) & (ps["G"] > 20)]
players = sorted([name for name in filtered['Name']])
selected_player = st.sidebar.selectbox('Select a pitcher:', players)
player_info = filtered[filtered['Name'] == selected_player].get(['Age','W','L','G','GS','IP','WHIP','WAR','ERA','SV','FIP','xFIP','BB','SO','TTO%'])
print(selected_player)

player_split = selected_player.split(" ")
if len(player_split) == 3:
    player_lookup = playerid_lookup(f"{player_split[1]} {player_split[2]}",player_split[0],fuzzy=True) # contains id to use in baseball reference
else:
    player_lookup = playerid_lookup(player_split[1],player_split[0],fuzzy=True)


player_api_id = player_lookup['key_mlbam'].values[0]
player_fangraphs_id = player_lookup['key_fangraphs'].values[0]
debut_date = int(player_lookup['mlb_played_first'].values[0])
img_url = f"https://securea.mlb.com/mlb/images/players/head_shot/{player_api_id}.jpg"

# ------------------------- Player Info Section ------------------------------------
info = f"""
<div style='border-radius: 5px; padding: 10px; margin-bottom: 5px;display: flex; align-items: center;'>
    <img src='{img_url}' style='width: 100px; margin-right: 15px; border-radius: 5px;'>
    <div style='flex-grow: 1; text-align: center; display: flex; flex-direction: column; justify-content: center;'>
        <h1 style='text-align: center; font-size: 35px;'>{selected_player}</h1> 
        <p style='font-size: 20px;'>Age: {player_info["Age"].values[0]} | Debut: {debut_date} | Team : {selected_team} | {st.session_state['year']}</p>
    </div>
</div>
"""
st.markdown(info, unsafe_allow_html=True)

# -------------------------- Player Stats --------------------------------------------
short_df = player_info.get(['W','L','G','GS','IP','WHIP','WAR','ERA','SV','FIP','xFIP','BB','SO','TTO%'])
st.dataframe(short_df,hide_index=True)

# ----------------------------------- Statcast Pitcher Data --------------------------
pid = player_lookup['key_mlbam'].values[0]
data = statcast_pitcher(f"{st.session_state['year']}-01-01",f"{st.session_state['year']}-12-31",player_id=pid) # 1 Year
data = data[data['game_type'] == 'R']
pitches_df = data.get(['player_name','release_speed','pitch_type'])

# ----------------------- strike zone display and velocity distribution  --------------------------
subheader = f"""
    <div margin-bottom:5px; padding: 10px; border-radius: 5px; text-align: center; width: auto;'>
        <h1 style='text-align: center; font-size: 20px'>Pitch Analysis</h1>
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

# ------------------------- chart ----------------------------------------

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

# -------------------------- pitch type pie chart ---------------
pie_header = f"""
    <div margin-bottom:5px; padding: 10px; border-radius: 5px; text-align: center; width: auto;'>
        <h1 style='text-align: center; font-size: 20px'>Pitch Distribution</h1>
    </div>
    """

st.markdown(pie_header, unsafe_allow_html=True)
data['pitch_type_full'] = data['pitch_type'].map(pitch_type_mapping)
pitch_type_counts = data['pitch_type_full'].value_counts()

# Create a pie chart
fig, ax = plt.subplots()
ax.pie(pitch_type_counts, labels=pitch_type_counts.index, autopct='%1.2f%%', startangle=80)
ax.axis('equal')  # Equal aspect ratio ensures the pie is drawn as a circle.

ax.legend(pitch_type_counts.index, title="Pitch Types", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))

st.pyplot(fig)

# -------------------------------- Bar Chart for Pitch Types -------------------------------------
pitch_header = """
    <div style='margin-bottom:10px; padding: 10px; border-radius: 5px; text-align: center; width: auto;'>
    <h1 style='margin-bottom: 5px; text-align: center; font-size: 20px'>Distribution of Pitch Types by Year</h1>
    </div>
    """
st.markdown(pitch_header, unsafe_allow_html=True)

# Caching function to prevent redundant API calls
@st.cache_data(show_spinner=True)
def get_pitch_type_distribution(years, pitcher_id):
    historical_data = []
    for year in years:
        try:
            # Fetch Statcast data for the pitcher
            data = statcast_pitcher(f"{year}-01-01", f"{year}-12-31", player_id=pitcher_id)
            data = data[data['game_type'] == 'R']  # Only regular season games

            # Create a summary table for pitch type occurrences
            pitch_summary = data['pitch_type'].value_counts(normalize=True).reset_index()
            pitch_summary.columns = ['pitch_type', 'rate_occurrence']
            pitch_summary['year'] = year
            pitch_summary['pitch_type'] = pitch_summary['pitch_type'].map(pitch_type_mapping)

            # Append summary for each year
            historical_data.append(pitch_summary[['pitch_type', 'rate_occurrence', 'year']])

        except Exception as e:
            print(f"Error processing data for year {year}: {e}")
    
    # Return the concatenated DataFrame if there is valid data, otherwise return empty
    if historical_data:
        return pd.concat(historical_data)
    else:
        return pd.DataFrame()

# Specify the years and pitcher_id
years = [2021, 2022, 2023, 2024]

# Get the historical pitch type data with error handling
historical_pitch_type_data = get_pitch_type_distribution(years, pid)

# Check if the returned DataFrame is empty
if not historical_pitch_type_data.empty:
    # Round to three decimal points and convert to percentage
    historical_pitch_type_data['rate_occurrence'] = (historical_pitch_type_data['rate_occurrence']).round(3)

    # Function to plot the bar chart using Seaborn
    def plot_sns_pitch_occurrence(df):  
        plt.figure(figsize=(12, 7))
        bar_plot = sns.barplot(
            x='year',
            y='rate_occurrence',
            hue='pitch_type',
            data=df,
            palette=sns.color_palette("Paired")
        )

        # Add labels and title
        bar_plot.set_xlabel('Year')
        bar_plot.set_ylabel('Percentage')
        bar_plot.set_title('Percentage of Pitch Types by Year')

        # Adjust legend position
        bar_plot.legend(title='Pitch Type', bbox_to_anchor=(1.05, .5), loc='center left', fontsize=16)

        # Display the plot in Streamlit
        st.pyplot(plt)

    # Plot the data
    plot_sns_pitch_occurrence(historical_pitch_type_data)
else:
    st.error("No valid data available for the selected pitcher and years.")