import streamlit as st

# Title of the page
st.title("Baseball Statistics Glossary")

# Section for Pitching Stats
st.header("Pitching Stats")
st.write("""
**W (Wins)**: The number of games won by the pitcher.

**L (Losses)**: The number of games lost by the pitcher.

**G (Games)**: The total number of games the pitcher has appeared in.

**GS (Games Started)**: The number of games where the pitcher started the game.

**IP (Innings Pitched)**: The total number of innings a pitcher has thrown.

**WHIP (Walks plus Hits per Inning Pitched)**: The total number of walks and hits allowed by a pitcher per inning pitched. Lower WHIP values are better.

**WAR (Wins Above Replacement)**: Estimates the player's total value to their team in terms of wins compared to a replacement-level player. Higher WAR indicates greater value.

**ERA (Earned Run Average)**: Measures the average number of earned runs a pitcher allows per nine innings pitched. A lower ERA indicates better performance.

**SV (Saves)**: The number of games where the pitcher finished the game while preserving the lead.

**FIP (Fielding Independent Pitching)**: Estimates a pitcher's effectiveness based on strikeouts, walks, and home runs, excluding the influence of fielding. Lower FIP values are better.

**xFIP (Expected Fielding Independent Pitching)**: Similar to FIP but normalizes the number of home runs allowed to league average, providing a better indication of a pitcher’s true skill.

**BB (Walks)**: The number of times a pitcher allows a batter to reach base due to four balls thrown.

**SO (Strikeouts)**: The number of times a pitcher records a strikeout.

**TTO% (Three True Outcomes Percentage)**: The percentage of plate appearances that end in a strikeout, walk, or home run.

**K/9 (Strikeouts per Nine Innings)**: Represents the average number of strikeouts a pitcher records in nine innings. Higher values are better.

**xERA (Expected ERA)**: Predicts a pitcher’s ERA based on factors like strikeouts, walks, and batted-ball data. It aims to provide a more accurate picture of a pitcher’s skill.

**BABIP (Batting Average on Balls In Play)**: Measures how often balls in play go for hits. It’s used to gauge how much of a pitcher’s success is due to luck.

**HR/9 (Home Runs per Nine Innings)**: Calculates the average number of home runs allowed by a pitcher per nine innings. Lower values are better.

**K% (Strikeout Rate)**: Represents the percentage of plate appearances that result in strikeouts. Higher K% is better.

**CS% (Caught Stealing Percentage)**: Measures the percentage of base stealers that a catcher successfully throws out. Higher CS% indicates better defensive performance.

**GB/FB (Ground Balls to Fly Balls Ratio)**: The ratio of ground balls to fly balls a pitcher allows. A higher GB/FB ratio suggests better performance in limiting fly balls.
""")

# Section for Hitting Stats
st.header("Hitting Stats")
st.write("""
**PA (Plate Appearances)**: The total number of times a player comes to bat, including walks and hit-by-pitches.

**H (Hits)**: The number of times a player successfully reaches base by hitting the ball.

**1B (Singles)**: Hits where the player reaches first base.

**2B (Doubles)**: Hits where the player reaches second base.

**3B (Triples)**: Hits where the player reaches third base.

**HR (Home Runs)**: Hits where the player rounds all bases and scores a run.

**R (Runs)**: The number of times the player scores a run.

**RBI (Runs Batted In)**: The number of runs a player drives in through hits or walks.

**BB (Walks)**: The number of times a player reaches base due to four balls thrown by the pitcher.

**HBP (Hit By Pitch)**: The number of times a player is awarded first base due to being hit by a pitched ball.

**SF (Sacrifice Flies)**: Hits where the batter flies out but drives in a run.

**SH (Sacrifice Hits)**: Hits where the batter sacrifices themselves to advance a runner, usually a bunt.

**wRC+ (Weighted Runs Created Plus)**: A measure of a player's overall offensive performance, adjusted for ballpark and league averages. A wRC+ of 100 is league average.

**wOBA (Weighted On-Base Average)**: A statistic that assigns different weights to different types of hits to assess a player's overall offensive value. Higher wOBA is better.

**BA (Batting Average)**: The ratio of a batter's hits to their total at-bats. A higher batting average indicates better hitting performance.

**OBP (On-Base Percentage)**: Measures the percentage of times a batter reaches base, including hits, walks, and hit-by-pitches. Higher OBP is better.

**SLG (Slugging Percentage)**: Reflects a batter's power by measuring the total number of bases per at-bat. Higher SLG indicates more power.

**OPS (On-Base Plus Slugging)**: Combines OBP and SLG to provide a comprehensive measure of a batter's offensive performance. Higher OPS values are better.

**wOBA (Weighted On-Base Average)**: Assigns different weights to different types of hits to evaluate a batter's overall offensive value. Higher wOBA is better.

**ISO (Isolated Power)**: Measures a batter's raw power by subtracting batting average from slugging percentage. Higher ISO indicates more power.

**BABIP (Batting Average on Balls In Play)**: Similar to pitching stats, it measures how often balls in play turn into hits for a batter. Higher BABIP can indicate luck or skill.

**Exit Velocity**: The speed of the ball as it leaves the bat. Higher exit velocity generally indicates more power and harder contact.

**Launch Angle**: The angle at which the ball leaves the bat. It helps to determine the trajectory of the hit. Higher launch angles can lead to more home runs.

**Hard Hit Rate**: The percentage of batted balls that are classified as "hard hit" by Statcast. Higher rates indicate more impactful hits.

**Barrels**: A combination of exit velocity and launch angle that signifies the most optimal hits. A higher number of barrels indicates better hitting performance.

**xBA (Expected Batting Average)**: Estimates a batter's average based on the quality of contact and the type of batted balls, not just their actual batting average.
""")

# Section for General Stats
st.header("General Stats")
st.write("""
**WAR (Wins Above Replacement)**: Estimates a player's total value to their team in terms of wins compared to a replacement-level player. Higher WAR indicates greater value.

**wRC+ (Weighted Runs Created Plus)**: Measures a player's overall offensive performance, adjusted for ballpark and league averages. A wRC+ of 100 is league average, and higher is better.

**FIP- (Fielding Independent Pitching Minus)**: A version of FIP that is scaled to league average. A FIP- of 100 is average, and lower values are better.

**ERA+ (Adjusted ERA)**: Adjusts a pitcher's ERA for park effects and league averages. A score of 100 is average, with higher scores indicating better performance.

**Defensive Runs Saved (DRS)**: Quantifies a player’s defensive contributions compared to the average player at their position. Higher DRS indicates better defense.

**Defensive WAR (dWAR)**: Measures a player's defensive value in terms of wins above replacement. Higher dWAR indicates better defensive performance.

**Ultimate Zone Rating (UZR)**: A measure of a player’s defensive performance based on the number of runs saved or allowed through their fielding. Higher UZR indicates better defense.

**On-Base Plus Slugging Plus (OPS+)**: Adjusts OPS for the player's ballpark and league average. A score of 100 is average, with higher scores indicating better performance.

**BABIP (Batting Average on Balls In Play)**: Used to evaluate both pitchers and hitters by measuring how often balls in play turn into hits. 

""")
