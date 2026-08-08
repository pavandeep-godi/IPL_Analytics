import streamlit as st
from streamlit import *
import pandas as pd
import numpy as np
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from PIL import Image

st.title("IPL Analytics")

image = Image.open("IPL_LOGO.jpg")
st.image(image)

st.markdown(
    "The Indian Premier League (IPL) is a high-energy Twenty20 cricket tournament played in India."
)

Matches_data = pd.read_excel("Matches_Data.xlsx",engine="openpyxl",index_col=0)

#season wise winners
Season_winners=Matches_data.loc[Matches_data.groupby('year')['date'].idxmax()].reset_index()
st.title("season wise winners")
st.write(Season_winners[["year","match_won_by"]])

#Most Successful teams
st.title("Most Successful Teams")
st.write(Season_winners["match_won_by"].value_counts())

#No.of wins in a season for each time
st.title("No.of Winning matches in a season")
valid_matches = Matches_data[Matches_data['match_won_by'] != 'Unknown']
winning_count = st.selectbox('Select Year', Matches_data['year'].unique())
filtered_data = valid_matches[valid_matches['year'] == winning_count]
st.dataframe(
    filtered_data['match_won_by'].value_counts().reset_index(name='Total Wins'), 
    hide_index=True
)


# 1. Filter out 'Unknown' or missing values from team selection options
available_teams = Matches_data['match_won_by'].dropna().unique()
available_teams = [team for team in available_teams if team != 'Unknown']

st.title("Select a Team from the dropdown below to get team-analysis")
# 2. Selectbox for Team selection
Selected_Team = st.selectbox("",available_teams)

# 3. Filter DataFrame for the selected team
Team_data = Matches_data[Matches_data['match_won_by'] == Selected_Team]

# ==========================================
# ALTERNATIVE TO TABLE: Toss Impact Chart
# ==========================================
st.subheader('Toss Decision Impact on Victories')

# Check match wins when Selected_Team won the toss vs lost the toss
Team_data['toss_match_status'] = Team_data['toss_winner'].apply(
    lambda x: 'Won Toss & Match' if x == Selected_Team else 'Lost Toss & Won Match'
)
toss_summary = Team_data['toss_match_status'].value_counts()

# Display as an insightful bar chart
st.bar_chart(toss_summary)

# Optional Breakdown: Toss Decision (Bat vs Field) when team won the toss
toss_decision_wins = Team_data[Team_data['toss_winner'] == Selected_Team]['toss_decision'].value_counts()
if not toss_decision_wins.empty:
    st.caption(f"Toss decision breakdown when {Selected_Team} won the toss & match:")
    st.bar_chart(toss_decision_wins, horizontal=True)




st.subheader(f'Top Match Winners for {Selected_Team}')

# 1. Prepare data
top_players_df = (
    Team_data['player_of_match']
    .value_counts()
    .head(5)
    .reset_index()
)
top_players_df.columns = ['Player', 'Awards']

# 2. Create Horizontal Bar Chart with descending order
fig = px.bar(
    top_players_df,
    x='Awards',
    y='Player',
    orientation='h',
    text='Awards',
    title=f"Top 5 Player of the Match Winners - {Selected_Team}"
)

# Reverse y-axis so the top player is at the top
fig.update_layout(yaxis={'categoryorder': 'total ascending'}, yaxis_title="", xaxis_title="Awards")

# 3. Render in Streamlit
st.plotly_chart(fig, use_container_width=True)

ball2ball_data=pd.read_csv("ball2ball.csv")
st.title("Select Batter and Bowler")

# Dropdown selectors using new column names 'batter' and 'bowler'
select1 = st.selectbox('Select a batter', ball2ball_data['batter'].dropna().unique())
select2 = st.selectbox('Select a bowler', dball2ball_dataf['bowler'].dropna().unique())

# Filter data for selected batter vs bowler matchup
matchup_df = ball2ball_data.loc[(ball2ball_data["batter"] == select1) & (ball2ball_data['bowler'] == select2)]

# Filter for wickets taken by the bowler against this batter
wickets_df = matchup_df.loc[matchup_df['bowler_wicket'] == 1]

# Calculations using 'runs_batter'
total_runs = matchup_df['runs_batter'].sum()
sixes_df = matchup_df.loc[matchup_df['runs_batter'] == 6]
fours_df = matchup_df.loc[matchup_df['runs_batter'] == 4]

sixes = sixes_df['runs_batter'].count()
fours = fours_df['runs_batter'].count()
wickets = wickets_df['bowler_wicket'].count()

st.title("Batter vs Bowler Stats")

# --- Gauge 1: Sixes ---
string_in_string = f"Sixes hit against {select2}"
fig_sixes = go.Figure(go.Indicator(
    domain={'x': [0, 1], 'y': [0, 1]},
    value=sixes,
    mode="gauge+number",
    title={'text': string_in_string},
    gauge={
        'axis': {'range': [None, 20]},
        'steps': [
            {'range': [0, 10], 'color': "lightgray"},
            {'range': [10, 15], 'color': "gray"}
        ]
    }
))
st.plotly_chart(fig_sixes, use_container_width=True)

# --- Gauge 2: Fours ---
string_in_string = f"Fours hit against {select2}"
fig_fours = go.Figure(go.Indicator(
    domain={'x': [0, 1], 'y': [0, 1]},
    value=fours,
    mode="gauge+number",
    title={'text': string_in_string},
    gauge={
        'axis': {'range': [None, 20]},
        'steps': [
            {'range': [0, 10], 'color': "lightgray"},
            {'range': [10, 15], 'color': "gray"}
        ]
    }
))
st.plotly_chart(fig_fours, use_container_width=True)

# --- Gauge 3: Total Runs ---
string_in_string = f"Total runs scored against {select2}"
fig_total = go.Figure(go.Indicator(
    domain={'x': [0, 1], 'y': [0, 1]},
    value=total_runs,
    mode="gauge+number",
    title={'text': string_in_string},
    gauge={
        'axis': {'range': [None, 200]},
        'steps': [
            {'range': [0, 100], 'color': "lightgray"},
            {'range': [100, 150], 'color': "gray"}
        ]
    }
))
st.plotly_chart(fig_total, use_container_width=True)

# --- Gauge 4: Wickets / Outs ---
string_in_string = f"Outs against {select2}"
fig_outs = go.Figure(go.Indicator(
    domain={'x': [0, 1], 'y': [0, 1]},
    value=wickets,
    mode="gauge+number",
    title={'text': string_in_string},
    gauge={
        'axis': {'range': [None, 10]},
        'steps': [
            {'range': [0, 3], 'color': "lightgray"},
            {'range': [3, 6], 'color': "gray"}
        ]
    }
))
st.plotly_chart(fig_outs, use_container_width=True)

