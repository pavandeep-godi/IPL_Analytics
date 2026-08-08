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