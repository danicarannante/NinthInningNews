from pybaseball import pitching_stats,batting_stats
import requests 
import datetime
from datetime import timedelta
import re
import streamlit as st
from variables import img_mapping
cache.enable()

team_name_mapping = {
    "ARI": "Arizona Diamondbacks",
    "ATL": "Atlanta Braves",
    "BAL": "Baltimore Orioles",
    "BOS": "Boston Red Sox",
    "CHC": "Chicago Cubs",
    "CHW": "Chicago White Sox",
    "CIN": "Cincinnati Reds",
    "CLE": "Cleveland Guardians",
    "COL": "Colorado Rockies",
    "DET": "Detroit Tigers",
    "MIA": "Miami Marlins",
    "HOU": "Houston Astros",
    "KCR": "Kansas City Royals",
    "LAA": "Los Angeles Angels",
    "LAD": "Los Angeles Dodgers",
    "MIL": "Milwaukee Brewers",
    "MIN": "Minnesota Twins",
    "NYM": "New York Mets",
    "NYY": "New York Yankees",
    "OAK": "Oakland Athletics",
    "PHI": "Philadelphia Phillies",
    "PIT": "Pittsburgh Pirates",
    "SDP": "San Diego Padres",
    "SFG": "San Francisco Giants",
    "SEA": "Seattle Mariners",
    "STL": "St. Louis Cardinals",
    "TBR": "Tampa Bay Rays",
    "TEX": "Texas Rangers",
    "TOR": "Toronto Blue Jays",
    "WSN": "Washington Nationals"
}

info = f"""
<div style='background-color: LightBlue; margin-bottom:5px;border-radius: 5px; text-align: center; width: auto;'>
    <h1 font-size: 35px;>Game Outcome Predictions</h1> 
</div>
"""
st.markdown(info, unsafe_allow_html=True)

text = ''' This prediction model estimates the winner of an MLB game by comparing offensive and pitching stats. 
It calculates a confidence score based on the differences in expected offensive production (xOP) and expected earned run average (xERA) for both teams. 
The model then predicts the winner by evaluating whether the home team has superior offensive and pitching metrics compared to the away team, or vice versa. 
The red box represents a wrong prediction while the green box represents a correct prediction.'''

prediction_descrip = f"""
<div style=margin-bottom:5px; text-align: center; width: auto;'>
    <p font-size: 1px;>{text}</p> 
</div>
"""
st.markdown(prediction_descrip, unsafe_allow_html=True)

end_date = datetime.datetime.today() - timedelta(days=1)  # Yesterday
start_date = end_date - timedelta(days=60)  # Two months ago

# Create the slider
selected_date = st.sidebar.slider(
    "Select Date Range",
    min_value=start_date.date(),
    max_value=end_date.date(),
    value=end_date.date(),
    format="YYYY-MM-DD"
)


data = pitching_stats(2024, qual=5)
pitcher_stats = data[['Name', 'xERA', 'ERA', 'Stuff+']]
pitcher_stats_dict = {} # pitching data dictionary
for index, row in pitcher_stats.iterrows():
    pitcher_name = row['Name']
    pitcher_stats_dict[pitcher_name] = row.drop('Name').to_dict()

data = batting_stats(2024, qual=50)
ignore = ["Name", "IDfg", "Season", "Age", "Dol", "Age Rng", "G", "AB", "PA"]
data.drop(ignore, axis=1, inplace=True)
batting = data[data["Team"] != "- - -"]

batting['Team'] = batting['Team'].replace(team_name_mapping)
team_batting_stats = batting.groupby("Team").mean().reset_index()
# Create a new Column/Value
team_batting_stats['xOP'] = (team_batting_stats['xBA'] + team_batting_stats['xSLG'] + team_batting_stats['BB%'] + team_batting_stats['AVG'] + team_batting_stats['OPS'])
xOP_baseline = team_batting_stats['xOP'].mean() - 1
team_batting_stats['xOP'] = team_batting_stats['xOP'] - xOP_baseline
# Convert the DataFrame to a dictionary with team names as keys
team_batting_stats_dict = team_batting_stats.set_index('Team').T.to_dict()


# Get today's date in YYYY-MM-DD format
#today = datetime.datetime.today().strftime('%Y-%m-%d')
today = '2024-07-28'
print(today)
# MLB GameDay API URL for the schedule
url = f'https://statsapi.mlb.com/api/v1/schedule?sportId=1&hydrate=probablePitcher(note)&date={selected_date}'
response = requests.get(url)
data = response.json()

matchups = []
for date in data['dates']:
    for game in date['games']:
        matchup = {}
        matchup['date'] = today
        matchup['home_team'] = game['teams']['home']['team']['name']
        matchup['away_team'] = game['teams']['away']['team']['name']

        try:
            home_pitcher_info = game['teams']['home']['probablePitcher']
            away_pitcher_info = game['teams']['away']['probablePitcher']
        except KeyError:
            continue
        matchup['home_pitcher'] = home_pitcher_info['fullName']
        matchup['away_pitcher'] = away_pitcher_info['fullName']

        if game['status']['detailedState'] == 'Final':
            if game['teams']['home']['isWinner'] is True:
                matchup['winner'] = matchup['home_team']
            elif game['teams']['away']['isWinner'] is True:
                matchup['winner'] = matchup['away_team']
        else: 
            matchup['winner'] = 'Game not completed'

        matchups.append(matchup)
        print(matchup)


        
def normalize_name(name):
    """Normalize the name by converting to lowercase and removing special characters."""
    return re.sub(r'\W+', '', name.lower())

def calculate_confidence(home_team_xOP, away_team_xOP, home_pitcher_xERA, away_pitcher_xERA):
    """Calculate the confidence of a prediction based on differences in xOP and xERA."""
    xOP_diff = abs(home_team_xOP - away_team_xOP)
    xERA_diff = abs(home_pitcher_xERA - away_pitcher_xERA)
    return xOP_diff + xERA_diff

def predict_game_winner(game, team_batting_stats, team_pitching_stats):
    # Normalize team and pitcher names
    home_team = normalize_name(game['home_team'])
    away_team = normalize_name(game['away_team'])
    home_pitcher = normalize_name(game['home_pitcher'])
    away_pitcher = normalize_name(game['away_pitcher'])

    # Check if teams and pitchers are in the stats dictionaries
    if home_team not in team_batting_stats or away_team not in team_batting_stats:
        print(f"Warning: One of the teams ({home_team}, {away_team}) not found in team_batting_stats")
        return None, None

    if home_pitcher not in team_pitching_stats or away_pitcher not in team_pitching_stats:
        print(f"Warning: One of the pitchers ({home_pitcher}, {away_pitcher}) not found in team_pitching_stats")
        return None, None

    # Get xOP and xERA for home and away teams
    home_team_xOP = team_batting_stats[home_team]['xOP']
    away_team_xOP = team_batting_stats[away_team]['xOP']
    home_pitcher_xERA = team_pitching_stats[home_pitcher]['xERA']
    away_pitcher_xERA = team_pitching_stats[away_pitcher]['xERA']

    # Calculate confidence based on differences in xOP and xERA
    confidence = calculate_confidence(home_team_xOP, away_team_xOP, home_pitcher_xERA, away_pitcher_xERA)

    # Predict the winner based on xOP and xERA comparison
    if home_team_xOP > away_team_xOP and home_pitcher_xERA < away_pitcher_xERA:
        return game['home_team'], confidence
    elif home_team_xOP < away_team_xOP and home_pitcher_xERA > away_pitcher_xERA:
        return game['away_team'], confidence
    elif home_team_xOP == away_team_xOP and home_pitcher_xERA < away_pitcher_xERA:
        return game['home_team'], confidence
    elif home_team_xOP == away_team_xOP and home_pitcher_xERA > away_pitcher_xERA:
        return game['away_team'], confidence
    else:
        # In case of ties or inconclusive predictions, return default values
        return None, None


def predict_games(today_games, team_batting_stats, team_pitching_stats):
    predictions = []

    for game in today_games:
        winner, confidence = predict_game_winner(game, team_batting_stats, team_pitching_stats)
        if winner:
            game['predicted_winner'] = winner
            game['confidence'] = confidence
            predictions.append(game)

    # Sort predictions by confidence in descending order
    predictions.sort(key=lambda x: x['confidence'], reverse=True)

    # Assign ranks
    rank = 0
    prev_confidence = None
    for prediction in predictions:
        if prediction['confidence'] != prev_confidence:
            rank += 1
        prediction['rank'] = rank
        prev_confidence = prediction['confidence']
    return predictions




# Normalize keys in the stats dictionaries
team_batting_stats = {normalize_name(k): v for k, v in team_batting_stats_dict.items()}
team_pitching_stats = {normalize_name(k): v for k, v in pitcher_stats_dict.items()}

# Predict game winners
predictions = predict_games(matchups, team_batting_stats, team_pitching_stats)
print(predictions)

def get_team_logo_url(team):
    print(f"https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/{img_mapping[team]}.png")
    return f"https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/{img_mapping[team]}.png"

# ----------------------------------------------------------------------------------------------------------------------
def create_game_card(results):
    with st.container():
        if results['predicted_winner'] == results['winner']:
            bg = 'LightGreen'
        elif results['predicted_winner'] != results['winner']:
            bg = 'Red'

        st.markdown(
            f"""
            <div style="background-color:{bg}; margin-bottom:10px; padding: 5px; border-radius: 10px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="flex: 1;text-align: center;">
                        <img src="{get_team_logo_url(p['home_team'])}" width="50" alt="{p['home_team']} logo">
                        <p style="font-size: 18px; margin:0;">Pitcher: {results['home_pitcher']}</p>
                    </div>
                    <div style="flex: 1; text-align: center;">
                        <p style="font-size: 18px;">Predicted Winner:<br>{results['predicted_winner']}</p>
                        <p style="font-size: 18px;">Confidence: {float(results['confidence']):.2f}</p>
                    </div>
                    <div style="flex: 1; text-align: right;">
                        <img src="{get_team_logo_url(p['away_team'])}" width="50" alt="{p['away_team']} logo">
                        <p style="font-size: 18px;margin:0;">Pitcher: {results['away_pitcher']}</p>
                    </div>
                </div>
            </div>
            """, 
            unsafe_allow_html=True
        )

game_time = "July 29, 2024 - 7:00 PM ET"
for p in predictions:
    create_game_card(p)