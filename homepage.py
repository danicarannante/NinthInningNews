import streamlit as st
import pandas as pd
from pybaseball import standings,statcast
from variables import get_league_data

st.set_page_config(
    page_title="MLB Data Explorer"
)



selected_year = st.sidebar.selectbox('Year', list(reversed(range(2019,2025))))
current_standings = standings(selected_year)
st.session_state['year'] = selected_year
st.session_state['data'] = False

title = f"""
<div style='background-color: LightBlue; border-radius: 1px; text-align: center; width: auto;'>
    <h1 style='margin-bottom: 5px; font-size: 18px;'>League Standings for {selected_year} </h1>
</div>
"""
st.markdown(title, unsafe_allow_html=True)


col1, col2 = st.columns(2)
for league in current_standings[:3]:
    col1.write(league)
for league in current_standings[3:]:
    col2.write(league)

teams = sorted(set(team for table in current_standings for team in table['Tm']))
st.session_state['teams'] = teams


df = pd.read_csv(f'{selected_year}.csv')
print(df) 
if 'league_data' not in st.session_state or st.session_state['data'] is False:
    print('loading league data.....')
    # st.session_state['league_data'] =   pd.read_csv(f'{selected_year}.csv')
    st.session_state['league_data'] = get_league_data()
    st.session_state['data'] = True
    print('finished....')
