import streamlit as st
import pandas as pd
from pybaseball import standings,statcast, schedule_and_record
from variables import get_league_data, team_mapping
from pybaseball import cache
cache.enable()

NinthInningNews = """
    <style>
        .newspaper-heading {
            font-family: 'Georgia', serif; /* Choose a serif font for a newspaper feel */
            font-size: calc(2vw + 2rem); /* Responsive font size */
            font-weight: bold;
            color: #333; /* Dark color for the title */
            text-align: center;
            margin: 5px 0; /* Vertical spacing */
            padding: 0 10px; /* Horizontal padding for smaller screens */
            box-sizing: border-box; /* Ensure padding doesn't affect width */
        }
    </style>
    <div class="newspaper-heading">
        Ninth Inning News
    </div>
"""
st.markdown(NinthInningNews, unsafe_allow_html=True)

bio = f"""
<div style='text-align: center; width: auto;'>
    <p style='margin-bottom:10px; font-style: italic; font-size: 12px;'> Hi and welcome to Ninth Inning News! My name is Daniela and this app is a personal project designed to sharpen my programming skills, explore new tools, and dive deep into the world of baseball data. Feel free to explore, click around, and enjoy the content!
    If you have any questions or feedback, don’t hesitate to reach out at: danielacarannante3@gmail.com.
</p> 
</div>
"""

st.markdown(bio, unsafe_allow_html=True)

selected_year = st.sidebar.selectbox('Year', list(reversed(range(2019,2025))))

current_standings = standings(selected_year)
print(current_standings)
for league in current_standings:
    league.rename(columns={'Tm': 'Team'}, inplace=True)
    try:
        league.drop(columns=['E#'], inplace=True)
    except KeyError:
        print("error occured")
        pass

st.session_state['year'] = selected_year
st.session_state['data'] = False

title = f"""
<div style='background-color: LightBlue; border-radius: 5px; text-align: center; width: auto;'>
    <h1 style='margin-bottom: 5px; font-size: 18px;'>League Standings for {selected_year} </h1>
</div>
"""
st.markdown(title, unsafe_allow_html=True)

col1, col2 = st.columns(2)
for league in current_standings[:3]:
    col1.write(league)
    print("checking...")
for league in current_standings[3:]:
    col2.write(league)
    print("checking...")
teams = sorted(set(team for table in current_standings for team in table['Team']))

st.session_state['teams'] = team_mapping.keys()


cache.enable()
if 'league_data' not in st.session_state or st.session_state['data'] is False:
    with st.sidebar.status('Loading Data...'):
        print(f"loading league data for {st.session_state['year']}")
        #st.session_state['league_data'] =   pd.read_csv(f'{selected_year}.csv')
        st.session_state['league_data'] = get_league_data()
        st.session_state['data'] = True
        print('finished....')
    st.sidebar.success("Data Loaded Successfully")
