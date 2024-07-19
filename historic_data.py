from pybaseball import statcast
import pandas as pd
# stats = statcast("2024-01-01","2024-12-31")
# stats.to_csv("2024.csv")

# stats = statcast("2022-01-01","2022-12-31")
# stats.to_csv("2022.csv")

stats = statcast("2021-01-01","2021-12-31")
stats.to_csv("2021.csv")

stats = statcast("2020-01-01","2020-12-31")
stats.to_csv("2020.csv")

stats = statcast("2019-01-01","2019-12-31")
stats.to_csv("2019.csv")



# league_data = pd.read_csv('2023.csv')  
# print(league_data['player_name'])