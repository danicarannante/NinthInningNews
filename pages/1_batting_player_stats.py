import streamlit as st
from pybaseball import batting_stats,playerid_lookup, statcast_batter, spraychart,plot_stadium, playerid_reverse_lookup
from variables import team_mapping,create_summary_table, classify_hit, get_league_data, stadium_mapping
import pandas as pd
import datetime 
import matplotlib.pyplot as plt
import plotly.graph_objs as go
import seaborn as sns
from pybaseball import cache
from matplotlib.patches import Rectangle
import numpy as np


selected_team = st.sidebar.selectbox('Select a team:', st.session_state["teams"])
abv = team_mapping[selected_team]

bs = batting_stats(st.session_state['year'], end_season=st.session_state['year'], league='all', qual=1, ind=1)
filtered = bs[(bs["Team" ] == abv) & (bs["G"] > 20)]
players = sorted([name for name in filtered['Name']])
selected_player = st.sidebar.selectbox('Select a player:', players)
player_info = filtered[filtered['Name'] == selected_player].get(['Age','G','AB','PA','H','1B','2B','3B','HR','R','RBI','BB','HBP','SF','SH','wRC+','wOBA',])

player_split = selected_player.split(" ")
if len(player_split) == 3:
    player_lookup = playerid_lookup(f"{player_split[1]} {player_split[2]}",player_split[0],fuzzy=True) # contains id to use in baseball reference
else:
    player_lookup = playerid_lookup(player_split[1],player_split[0],fuzzy=True)

player_api_id = player_lookup['key_mlbam'].values[0]
player_fangraphs_id = player_lookup['key_fangraphs'].values[0]
img_url = f"https://securea.mlb.com/mlb/images/players/head_shot/{player_api_id}.jpg"
debut_date = int(player_lookup['mlb_played_first'].values[0])

# ------------------------- Player Info Section -----------------------------------
info = f"""
<div style=' border-radius: 5px; padding: 10px; margin-bottom: 5px;display: flex; align-items: center;'>
    <img src='{img_url}' style='width: 100px; margin-right: 15px; border-radius: 5px;'>
    <div style='flex-grow: 1; text-align: center; display: flex; flex-direction: column; justify-content: center;'>
        <h1 style='text-align: center; font-size: 35px;'>{selected_player}</h1> 
        <p style='font-size: 20px;'>Age: {player_info["Age"].values[0]} | Debut: {debut_date} | Team : {selected_team} | {st.session_state['year']}</p>
    </div>
</div>
"""
st.markdown(info, unsafe_allow_html=True)

# -------------------------- Player Stats Blocks -----------------------------------
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

# ------------------------------ Statcast Batter Data -----------------------
pid = player_lookup['key_mlbam'].values[0]
data = statcast_batter(f"{st.session_state['year']}-01-01",f"{st.session_state['year']}-12-31",player_id=pid)
data = data[data['game_type'] == 'R']
data['bb_type'] = data['bb_type'].replace({'ground_ball': 'ground ball','line_drive': 'line drive','fly_ball':'fly ball'})

# ----------------------------- Hits Spraychart -----------------------------
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

# -------------------------- Heat Map ---------------------------
heatmap_header = f"""
    <div margin-bottom:10px; padding: 10px; border-radius: 5px; text-align: center; width: auto;'>
    <h1 style='text-align: center; font-size: 20px'>Swing Heatmap </h1>
    </div>
    """
st.markdown(heatmap_header, unsafe_allow_html=True)
heatmap_data = data.get(['events','pfx_x','pfx_z','launch_speed','launch_angle','pitch_name','p_throws', 'release_speed', 'release_spin_rate','plate_x', 'plate_z', 'player_name', 'game_year', 'description', 'bb_type'])

heatmap_data['pfx_x_in_pv'] = -12 * heatmap_data['pfx_x'] # horizantal movement
heatmap_data['pfx_z_in'] = 12 * heatmap_data['pfx_z'] # vertical movement

# Create 'barrel' column based on conditions
def is_barrel(row):
    exit_vel = row['launch_speed']
    launch_angle = row['launch_angle']
    
    if exit_vel >= 98:
        # Adjust launch angle range based on exit velocity
        if 98 <= exit_vel <= 99 and 26 <= launch_angle <= 30:
            return True
        elif 99 <= exit_vel <= 100 and 25 <= launch_angle <= 31:
            return True
        elif exit_vel > 100 and 24 <= launch_angle <= 33:
            return True
    return False

# Apply the function to the DataFrame
heatmap_data['barrel'] = heatmap_data.apply(is_barrel, axis=1)


# Create 'pitch_type' column based on 'pitch_name'
heatmap_data['pitch_type'] = heatmap_data['pitch_name'].apply(lambda x: 
    "Breaking Ball" if x in ["Slider", "Curveball", "Knuckle Curve", "Slurve", "Sweeper", "Slow Curve"] else
    "Fastball" if x in ["4-Seam Fastball", "Sinker", "Cutter"] else
    "Offspeed" if x in ["Changeup", "Split-Finger", "Other", "Knuckleball", "Eephus"] else
    "Unknown"
)



# Function to filter data for each heat map stat-type
def find_plots(data, column, value):
    return data[data[column] == value]

pitch_type_filter = st.selectbox('Select Pitch Type', heatmap_data['pitch_name'].unique())
plots_data = find_plots(heatmap_data, 'pitch_name', pitch_type_filter)
l_filtered =  find_plots(plots_data, 'p_throws', 'L')
r_filtered =  find_plots(plots_data, 'p_throws', 'R')


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

# -------------------------------- Table -----------------------------------------
valid_at_bat_events = [
    'single', 'double', 'triple', 'home_run', 'strikeout', 
    'field_out', 'force_out', 'grounded_into_double_play', 
    'fielders_choice', 'field_error'
]

summary_stats = heatmap_data.groupby('pitch_name').agg( 
    Pitch_Count=('pitch_name', 'size'),
    At_Bats=('events', lambda x: x[x.isin(valid_at_bat_events)].count()),
    Avg_Exit_Velocity=('launch_speed', 'mean'),
    Avg_Launch_Angle=('launch_angle', 'mean'),
    Barrel_Count=('barrel', lambda x: x[x == True].count()),
    Miss_Swings=('description', lambda x: x[x == 'swinging_strike'].count()),
    Swing_Count = ('description', lambda x: x[x.isin(['swinging_strike', 'foul', 'hit_into_play'])].count()),
    Hits=('events', lambda x: x[x.isin(['single', 'double', 'triple', 'home_run'])].count())
).reset_index()

summary_stats['Batting_Average'] = summary_stats['Hits'] / summary_stats['At_Bats']
summary_stats['Whiff_Rate'] = summary_stats['Miss_Swings'] / summary_stats['Swing_Count']
summary_stats['Batting_Average'] = summary_stats['Hits'] / summary_stats['At_Bats']
summary_stats['Barrel_Rate'] = summary_stats['Barrel_Count'] / summary_stats['Hits']
 
summary_stats = summary_stats.rename(columns={
    'Pitch_Count': 'pitch count',
    'Miss_Rate': 'miss rate',
    'Barrel_Rate': 'barrel rate',
    'Avg_Exit_Velocity': 'avgerage exit velocity',
    'Avg_Launch_Angle': 'avgerage launch angle',
    'Whiff_Rate': 'whiff rate',
    'Batting_Average': 'batting average',
    'Hits':'hits'
})

st.dataframe(summary_stats[summary_stats['pitch_name'] == pitch_type_filter].drop(columns=["pitch_name","At_Bats","Barrel_Count","Miss_Swings","Swing_Count"],axis=1),hide_index=True)

# -------------------------------- Bar Chart -------------------------------------
rate_header = """
    <div style='margin-bottom:10px; padding: 10px; border-radius: 5px; text-align: center; width: auto;'>
    <h1 style='margin-bottom: 5px; text-align: center; font-size: 20px'>Distribution of Batted Ball Types by Year</h1>
    </div>
    """
st.markdown(rate_header, unsafe_allow_html=True)

# Caching function to prevent redundant API calls
@st.cache_data(show_spinner=True)
def get_historical_rate_occurrence(years, player_id):
    historical_data = []
    for year in years:
        try:
            # Fetch Statcast data for the player
            data = statcast_batter(f"{year}-01-01", f"{year}-12-31", player_id=player_id)
            data = data[data['game_type'] == 'R']  # Only regular season games
            data['bb_type'] = data['bb_type'].replace({'ground_ball': 'ground ball', 'line_drive': 'line drive', 'fly_ball': 'fly ball'})

            # Filter hits and classify hit type
            hits_df = data[data['events'].isin(['single', 'double', 'triple', 'home_run'])]
            hits_df['hit_classification'] = hits_df.apply(classify_hit, axis=1)

            # Create summary table
            summary_df = create_summary_table(hits_df)
            summary_df['year'] = year
            historical_data.append(summary_df[['batted ball type', 'rate_occurrence', 'year']])
           

        except Exception as e:
            print(f"Error processing data for year {year}: {e}")
    
    if historical_data:
        return pd.concat(historical_data)
    else:
        return pd.DataFrame()

# Specify the years and player_id
years = [2021, 2022, 2023, 2024]

# Get the historical data with error handling
historical_rate_occurrence = get_historical_rate_occurrence(years, pid)

# Check if the returned DataFrame is empty
if not historical_rate_occurrence.empty:
    # Round to three decimal points and convert to percentage
    historical_rate_occurrence['rate_occurrence'] = (historical_rate_occurrence['rate_occurrence']).round(3)
    # Function to plot the bar chart using Seaborn
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

        # Adjust legend position
        bar_plot.legend(title='Batted Ball Type', bbox_to_anchor=(1.05, .5), loc='center left', fontsize=16)

        # Display the plot in Streamlit
        st.pyplot(plt)

    # Plot the data
    plot_sns_rate_occurrence(historical_rate_occurrence)
else:
    st.error("No valid data available for the selected player and years.")