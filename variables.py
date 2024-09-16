import pandas as pd
import requests
from pybaseball import statcast
import streamlit as st
import matplotlib.pyplot as plt

team_mapping = {
'Arizona Diamondbacks':'ARI', 
'Atlanta Braves':'ATL',
'Baltimore Orioles': 'BAL', 
'Boston Red Sox': 'BOS', 
'Chicago Cubs': 'CHC', 
'Chicago White Sox': 'CHW',
'Cincinnati Reds': 'CIN', 
'Cleveland Guardians': 'CLE',
'Colorado Rockies' :'COL',
'Detroit Tigers' : 'DET', 
'Houston Astros' : 'HOU', 
'Kansas City Royals' : 'KCR',
'Los Angeles Angels': 'LAA',
'Los Angeles Dodgers' : 'LAD', 
'Miami Marlins': 'MIA',
'Milwaukee Brewers': 'MIL', 
'Minnesota Twins': 'MIN', 
'New York Mets': 'NYM', 
'New York Yankees': 'NYY', 
'Oakland Athletics': 'OAK',
'Philadelphia Phillies' :'PHI',
'Pittsburgh Pirates': 'PIT',
'San Diego Padres': 'SDP',
'San Francisco Giants':'SFG',
'Seattle Mariners': 'SEA',
'St. Louis Cardinals': 'STL', 
'Tampa Bay Rays': 'TB', 
'Texas Rangers': 'TEX', 
'Toronto Blue Jays': 'TOR',
'Washington Nationals':'WSN'}

img_mapping   = {
'Arizona Diamondbacks':'ARI', 
'Atlanta Braves':'ATL',
'Baltimore Orioles': 'BAL', 
'Boston Red Sox': 'BOS', 
'Chicago Cubs': 'CHC', 
'Chicago White Sox': 'CHW',
'Cincinnati Reds': 'CIN', 
'Cleveland Guardians': 'CLE',
'Colorado Rockies' :'COL',
'Detroit Tigers' : 'DET', 
'Houston Astros' : 'HOU', 
'Kansas City Royals' : 'KC',
'Los Angeles Angels': 'LAA',
'Los Angeles Dodgers' : 'LAD', 
'Miami Marlins': 'MIA',
'Milwaukee Brewers': 'MIL', 
'Minnesota Twins': 'MIN', 
'New York Mets': 'NYM', 
'New York Yankees': 'NYY', 
'Oakland Athletics': 'OAK',
'Philadelphia Phillies' :'PHI',
'Pittsburgh Pirates': 'PIT',
'San Diego Padres': 'SD',
'San Francisco Giants':'SF',
'Seattle Mariners': 'SEA',
'St. Louis Cardinals': 'STL', 
'Tampa Bay Rays': 'TB', 
'Texas Rangers': 'TEX', 
'Toronto Blue Jays': 'TOR',
'Washington Nationals':'WSH'}

stadium_mapping = {'Arizona Diamondbacks':'diamondbacks', 
'Atlanta Braves':'braves',
'Baltimore Orioles': 'orioles', 
'Boston Red Sox': 'red_sox', 
'Chicago Cubs': 'cubs', 
'Chicago White Sox': 'white_soc',
'Cincinnati Reds': 'reds', 
'Cleveland Guardians': 'indians',
'Colorado Rockies' :'rockies',
'Detroit Tigers' : ' tigers', 
'Houston Astros' : 'astros', 
'Kansas City Royals' : 'royals',
'Los Angeles Angels': 'angels',
'Los Angeles Dodgers' : 'dodgers', 
'Miami Marlins': 'marlins',
'Milwaukee Brewers': 'brewers', 
'Minnesota Twins': 'twins', 
'New York Mets': 'mets', 
'New York Yankees': 'yankees', 
'Oakland Athletics': 'athletics',
'Philadelphia Phillies' :'phillies',
'Pittsburgh Pirates': 'pirates',
'San Diego Padres': 'padres',
'San Francisco Giants':'giants',
'Seattle Mariners': 'mariners',
'St. Louis Cardinals': 'cardinals', 
'Tampa Bay Rays': 'rays', 
'Texas Rangers': 'rangers', 
'Toronto Blue Jays': 'blue_jays',
'Washington Nationals':'nationals',
'Generic': 'generic'}

pitch_type_mapping = {
    'CH': 'Changeup',
    'CU':'Curveball',
    'FC':'Cutter',
    'EP':'Eephus',
    'FO':'Forkball',
    'FF':'Four-Seam Fastball',
    'KN':'Knuckleball',
    'KC':'Knuckle-curve',
    'SC':'Screwball',
    'SI':'Sinker',
    'SL':'Slider',
    'SV':'Slurve',
    'FS':'Splitter',
    'ST':'Sweeper'
}

@st.cache_data
def create_summary_table(data):
    total_hits = len(data)
    # Get all unique combinations of (bb_type, hit_classification)
    unique_combinations = data['hit_classification'].unique()
    print(unique_combinations)
    # Initialize a list to hold the calculated rows
    rows = []
    for htype in unique_combinations:
        filtered_df =  data[data['hit_classification'] == htype]
        rate_occurrence = len(filtered_df) / total_hits
        avg_xWOBA = filtered_df['estimated_woba_using_speedangle'].mean()
        avg_wOBA = filtered_df['woba_value'].mean()
        avg_diff = avg_wOBA - avg_xWOBA
        avg_HH = len(filtered_df[filtered_df['launch_speed'] >= 95]) / total_hits # exit velocity >= 95 mph
 
        # Append the calculated values as a row
        if htype is not None:
            rows.append({
                'batted ball type': htype,
                'rate_occurrence': (rate_occurrence * 100),
                'avg_xWOBA': avg_xWOBA,
                'avg_diff': avg_diff,
                'avg_wOBA_weight': avg_wOBA,
                'avg_HH%': avg_HH
            })

    result_df = pd.DataFrame(rows)
    return (result_df)


# Function to classify hits
def classify_hit(row):
    location = row['hit_location']
    if pd.notna(row['hit_location']):
        if row['hit_location'] in [1,2,8]:
            location = 'center'
        if row['stand'] == "R":
            if row['hit_location'] in [3,4,9]:
                location = 'opposite'
            elif row['hit_location'] in [5,6,7]:
                location = 'pull'
        elif row['stand'] == "L":
            if row['hit_location'] in [3,4,9]:
                location = 'pull'
            elif row['hit_location'] in [5,6,7]:
                location = 'opposite'
        return f"{location} {row['bb_type']}"

@st.cache_data(show_spinner=True)
def get_league_data():
    stats = statcast(f"{st.session_state['year']}-01-01",f"{st.session_state['year']}-12-31").get(['player_name','hit_location','launch_angle','launch_speed','bb_type','stand','events','woba_value','estimated_woba_using_speedangle','woba_denom'])
    return stats
