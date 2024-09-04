import streamlit as st
from pybaseball import batting_stats,playerid_lookup, statcast_batter,statcast, spraychart,plot_stadium, playerid_reverse_lookup
from variables import team_mapping,create_summary_table, classify_hit, get_league_data, stadium_mapping, get_comparison
import pandas as pd
import datetime 
import matplotlib.pyplot as plt
import plotly.graph_objs as go
import seaborn as sns
from pybaseball import cache
import numpy as np

cache.enable()

selected_team = st.sidebar.selectbox('Select a team:', st.session_state["teams"])
abv = team_mapping[selected_team]

bs = batting_stats(st.session_state['year'], end_season=st.session_state['year'], league='all', qual=1, ind=1)
filtered = bs[bs["Team" ] == abv]
players = sorted([name for name in filtered['Name']])
selected_player = st.sidebar.selectbox('Select a player:', players)
player_info = filtered[filtered['Name'] == selected_player].get(['Age','G','AB','PA','H','1B','2B','3B','HR','R','RBI','BB','HBP','SF','SH','wRC+','wOBA',])
print(selected_player)

player_lookup = playerid_lookup(selected_player.split(" ")[1],selected_player.split(" ")[0],fuzzy=True) # contains id to use in baseball reference
player_api_id = player_lookup['key_mlbam'].values[0]
player_fangraphs_id = player_lookup['key_fangraphs'].values[0]
img_url = f"https://securea.mlb.com/mlb/images/players/head_shot/{player_api_id}.jpg"
debut_date = int(player_lookup['mlb_played_first'].values[0])

# ------------------------- Player Info Section ------------------------------------
info = f"""
<div style='background-color: LightBlue; border-radius: 5px; padding: 10px; margin-bottom: 5px;display: flex; align-items: center;'>
    <img src='{img_url}' style='width: 100px; margin-right: 15px; border-radius: 5px;'>
    <div style='flex-grow: 1; text-align: center; display: flex; flex-direction: column; justify-content: center;'>
        <h1 style='text-align: center; font-size: 35px;'>{selected_player}</h1> 
        <p style='font-size: 20px;'>Age: {player_info["Age"].values[0]} | Debut: {debut_date} | Team : {selected_team} | {st.session_state['year']}</p>
    </div>
</div>
"""
st.markdown(info, unsafe_allow_html=True)

# -------------------------- Player Stats blocks--------------------------------------------
short_df = player_info.get(['G','AB','PA','H','1B','2B','3B','HR','R','RBI','BB','HBP','SF','SH'])
st.dataframe(short_df,hide_index=True)

col1,col2 = st.columns(2)
season_wOBA = f"""
<div style='background-color: LightBlue; margin-bottom:5px; padding: 1px; border-radius: 5px; text-align: center;'>
    <h1 style='margin-bottom: 1px; font-size: 34px'>{player_info['wRC+'].values[0]}</h1>
    <p style='margin-bottom: 1px; font-size: 18px;'>{st.session_state['year']} wRC+ for {selected_player}</p>
    
</div>
"""
season_xwOBA = f"""
<div style='background-color: LightBlue; margin-bottom:5px; padding: 1px; border-radius: 5px; text-align: center;'>
    <h1 style='margin-bottom: 1px; font-size: 34px;'>{player_info['wOBA'].values[0]}</h1>
    <p style='margin-bottom: 1px; font-size: 18px;'>{st.session_state['year']} wOBA for {selected_player}</p>
</div>
"""
with col1:
    st.markdown(season_wOBA, unsafe_allow_html=True)
with col2:
    st.markdown(season_xwOBA, unsafe_allow_html=True)

# ----------------------------------- Statcast Batter Data --------------------------
pid = player_lookup['key_mlbam'].values[0]
data = statcast_batter(f"{st.session_state['year']}-01-01",f"{st.session_state['year']}-12-31",player_id=pid)
data = data[data['game_type'] == 'R']
data['bb_type'] = data['bb_type'] .replace({'ground_ball': 'ground ball','line_drive': 'line drive','fly_ball':'fly ball'})

# ----------------------------- Hits spraychart ----------------------------- 
spray_title = f"""
<div style='border-radius: 5px; text-align: center; width: auto;'>
    <h1 style='margin-bottom: 5px; font-size: 20px;'>Hit Type Outcomes for L vs R Handed Pitchers </h1>
</div>
"""
st.markdown(spray_title, unsafe_allow_html=True)

col1,col2 = st.columns(2)
hit_types = data['bb_type'].dropna().unique()  
selected_hit_type = col1.selectbox("Select Hit Type", hit_types)
pitcher_selection = col2.selectbox("Right Handed or Left Handed Pitcher", ['R','L'])
filtered_data = data[data['bb_type'] == selected_hit_type]
filtered_data = filtered_data[filtered_data['p_throws'] == pitcher_selection]
fig = spraychart(filtered_data, stadium_mapping[selected_team], size=50, title=f"{selected_hit_type} for {st.session_state['year']}").get_figure()
st.pyplot(fig)

# -------------------------- heat map ---------------------------
heatmap_header = f"""
    <div margin-bottom:10px; padding: 10px; border-radius: 5px; text-align: center; width: auto;'>
    <h1 style='text-align: center; font-size: 20px'>Swing Heatmap </h1>
    </div>
    """
st.markdown(heatmap_header, unsafe_allow_html=True)
all_data = data.get(['pfx_x','pfx_z','launch_speed','launch_angle','pitch_name','p_throws', 'release_speed', 'release_spin_rate','plate_x', 'plate_z', 'player_name', 'game_year', 'description', 'bb_type'])

all_data['pfx_x_in_pv'] = -12 * all_data['pfx_x']
all_data['pfx_z_in'] = 12 * all_data['pfx_z']

# Create 'barrel' column based on conditions
all_data['barrel'] = np.where(
    (all_data['launch_speed'] * 1.5 - all_data['launch_angle'] >= 117) &
    (all_data['launch_speed'] + all_data['launch_angle'] >= 124) &
    (all_data['launch_speed'] >= 97) &
    (all_data['launch_angle'] > 4) & (all_data['launch_angle'] < 50),
    1, 0
)

# Create 'pitch_type' column based on 'pitch_name'
all_data['pitch_type'] = all_data['pitch_name'].apply(lambda x: 
    "Breaking Ball" if x in ["Slider", "Curveball", "Knuckle Curve", "Slurve", "Sweeper", "Slow Curve"] else
    "Fastball" if x in ["4-Seam Fastball", "Sinker", "Cutter"] else
    "Offspeed" if x in ["Changeup", "Split-Finger", "Other", "Knuckleball", "Eephus"] else
    "Unknown"
)

# Select the required columns
heatmap_data = all_data[
    ['pitch_name', 'p_throws', 'release_speed', 'pfx_x_in_pv', 'pfx_z_in', 'release_spin_rate', 
     'plate_x', 'plate_z', 'player_name', 'game_year', 'description', 'bb_type', 'barrel']
].dropna()

# Function to filter data for each heat map stat-type
def find_plots(data, column, value):
    return data[data[column] == value]

pitch_type_filter = st.selectbox('Select Pitch Type', heatmap_data['pitch_name'].unique())
plots_data = find_plots(heatmap_data, 'pitch_name', pitch_type_filter)
l_filtered =  find_plots(plots_data, 'p_throws', 'L')
r_filtered =  find_plots(plots_data, 'p_throws', 'R')

from matplotlib.patches import Rectangle
# Plot KDE plot using Seaborn
def create_plot(plots_data,hand):
    plt.figure()
    sns.kdeplot(
        x=plots_data['plate_x'], 
        y=plots_data['plate_z'], 
        cmap='crest', 
        thresh=0.1, 
        levels=100,
        fill=True, 
        legend=True
    )
    strike_zone = Rectangle((-1, 1.5), 2, 2, fill=False, edgecolor='black', linewidth=1)
    plt.gca().add_patch(strike_zone)
    plt.xlim(-2,2)
    plt.ylim(0, 5)
    plt.title(f"Swing Heatmap vs {hand} Handed Pitchers ")
    plt.xlabel('Horizontal Plate Location')
    plt.ylabel('Vertical Plate Location')
    plt.gca()

    return(plt.gcf())

col1,col2 = st.columns(2)
col1.pyplot(create_plot(l_filtered,'L'))
col2.pyplot(create_plot(r_filtered, 'R'))

# -------------------------------- table -----------------------------------------
# Group the data by pitch type and calculate summary statistics
all_data['is_swing'] = all_data['description'].isin(['swinging_strike', 'foul', 'hit_into_play'])
all_data['is_whiff'] = all_data['description'] == 'swinging_strike'
summary_stats = all_data.groupby('pitch_name').agg(
    Pitch_Count=('pitch_name', 'size'),
    Miss_Rate=('description', lambda x: (x == 'swinging_strike').mean()),
    Barrel_Rate=('barrel', 'mean'),
    Avg_Exit_Velocity=('launch_speed', 'mean'),
    Avg_Launch_Angle=('launch_angle', 'mean'),
    Whiff_Rate=('is_whiff', lambda x: x.sum() / all_data.loc[x.index, 'is_swing'].sum()),
    Batting_Average=('description', lambda x: (x == 'hit_into_play').mean()),
).reset_index()
summary_stats = summary_stats.rename(columns={
    'Pitch_Count': 'pitch count',
    'Miss_Rate': 'miss rate',
    'Barrel_Rate': 'barrel rate',
    'Avg_Exit_Velocity': 'average exit velocity',
    'Avg_Launch_Angle': 'average launch angle',
    'Whiff_Rate': 'whiff rate',
    'Batting_Average': 'batting averge'
})

st.dataframe(summary_stats[summary_stats['pitch_name'] == pitch_type_filter].drop("pitch_name",axis=1),hide_index=True)

# -------------------------------- bar chart -------------------------------------
rate_header = f"""
    <div margin-bottom:10px; padding: 10px; border-radius: 5px; text-align: center; width: auto;'>
    <h1 style='margin-bottom: 5px; text-align: center; font-size: 20px'>Distribution of Batted Ball Types by Year</h1>
    </div>
    """
st.markdown(rate_header, unsafe_allow_html=True)

cache.enable()
def get_historical_rate_occurrence(years, player_id):
    historical_data = []
    for year in years:
        data = statcast_batter(f"{year}-01-01", f"{year}-12-31", player_id=player_id)
        data = data[data['game_type'] == 'R']
        data['bb_type'] = data['bb_type'].replace({'ground_ball': 'ground ball', 'line_drive': 'line drive', 'fly_ball': 'fly ball'})
        hits_df = data[data['events'].isin(['single', 'double', 'triple', 'home_run'])]
        hits_df['hit_classification'] = hits_df.apply(classify_hit, axis=1)
        summary_df = create_summary_table(hits_df)
        summary_df['year'] = year
        try:
            historical_data.append(summary_df[['batted ball type', 'rate_occurrence', 'year']])
        except KeyError:
            return
    return pd.concat(historical_data)

# Specify the years and player_id
years = [2021, 2022, 2023, 2024]
player_id = pid  # Replace with actual player_id

# Get the historical data
historical_rate_occurrence = get_historical_rate_occurrence(years, player_id)

# Round to three decimal points and convert to percentage
historical_rate_occurrence['rate_occurrence'] = (historical_rate_occurrence['rate_occurrence']).round(3)

def plot_sns_rate_occurrence(df):  
    plt.figure(figsize=(12, 7))
    bar_plot = sns.barplot(
        x='year',
        y='rate_occurrence',
        hue='batted ball type',
        data=df,
        palette=sns.color_palette("Paired")
    )

    # Add labels and title
    bar_plot.set_xlabel('Year')
    bar_plot.set_ylabel('Percentage')
    bar_plot.set_title('Percentage of Batted Ball Types by Year')

    bar_plot.legend(title='Batted Ball Type', bbox_to_anchor=(1.05, .5), loc='center left',fontsize=16)

    # Display the plot in Streamlit
    st.pyplot(plt)

plot_sns_rate_occurrence(historical_rate_occurrence)