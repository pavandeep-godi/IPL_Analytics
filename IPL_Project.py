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

ball2ball_data=pd.read_csv("ball2ball_df.csv")
st.title("Select Batter and Bowler")

# Dropdown selectors using new column names 'batter' and 'bowler'
select1 = st.selectbox('Select a batter', ball2ball_data['batter'].dropna().unique())
select2 = st.selectbox('Select a bowler', ball2ball_data['bowler'].dropna().unique())

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

# --- Streamlit Section Title ---
st.title("IPL Batter Career Stats")

# Clean dropdown selector for choosing a batter
selected_batter = st.selectbox(
    label='Select Batter', 
    options=ball2ball_data['batter'].dropna().unique()
)

# Trigger calculation and display when button is clicked
if st.button("Get Total Runs"):
    
    # Filter the main DataFrame for the selected batter
    batter_df = ball2ball_data.loc[ball2ball_data['batter'] == selected_batter]
    
    # Calculate total runs using Pandas sum (fast and efficient)
    total_runs = int(batter_df['runs_batter'].sum())

    # Build Plotly Gauge Chart
    fig_total_runs = go.Figure(go.Indicator(
        domain={'x': [0, 1], 'y': [0, 1]},
        value=total_runs,
        mode="gauge+number",
        title={'text': f"Total IPL Runs: {selected_batter}"},
        gauge={
            'axis': {'range': [None, 10000]},  # Max limit scaled for top IPL scorers
            'steps': [
                {'range': [0, 2500], 'color': "lightgray"},
                {'range': [2500, 5000], 'color': "gray"}
            ]
        }
    ))

    # Display the interactive Plotly gauge chart
    st.plotly_chart(fig_total_runs, use_container_width=True)

st.title("Batting Statistics")

# Example selection input (replace 'selected_player' with your Streamlit input variable name)
# selected_player = st.selectbox("Select Batter", ball2ball_df['batter'].unique())

if st.button("Generate Batting Stats"):
    # 1. Filter deliveries for the selected player
    player_deliveries = ball2ball_data[ball2ball_data['batter'] == selected_batter]

    if not player_deliveries.empty:
        # 2. Calculate total runs scored in each match per season (Vectorized)
        match_scores = (
            player_deliveries.groupby(['year', 'match_id'])['runs_batter']
            .sum()
            .reset_index(name='runs')
        )

        # 3. Aggregate 30s, 50s, and 100s per season
        # Note: Standard cricket rules treat 50s as 50-99 and 100s as 100+.
        season_summary = (
            match_scores.groupby('year')
            .agg(
                Centuries=('runs', lambda x: (x >= 100).sum()),
                Fifties=('runs', lambda x: ((x >= 50) & (x < 100)).sum()),
                Thirties=('runs', lambda x: ((x >= 30) & (x < 50)).sum()),
            )
            .reset_index()
        )

        # 4. Insert Player Name & Clean Up Output Formatting
        season_summary.insert(0, 'Player', selected_batter)
        season_summary.rename(columns={'year': 'Season'}, inplace=True)

        # Display clean dataframe without index
        st.dataframe(season_summary, hide_index=True)
    else:
        st.warning(f"No records found for {selected_batter}.")


st.title("Bowling Statistics")

# Selectbox for selecting bowler
selected_bowler = st.selectbox("Select Bowler", ball2ball_data["bowler"].unique())

if st.button("Generate Bowling Stats"):
    # 1. Filter deliveries for the selected bowler
    bowler_deliveries = ball2ball_data[
        ball2ball_data["bowler"] == selected_bowler
    ].copy()

    if not bowler_deliveries.empty:
        # 2. Identify wickets credited to the bowler
        # (Excludes run outs, retired hurt, etc.)
        if "bowler_wicket" in bowler_deliveries.columns:
            bowler_deliveries["is_bowler_wicket"] = (
                bowler_deliveries["bowler_wicket"].fillna(0).astype(int)
            )
        else:
            # Fallback using wicket_kind if bowler_wicket isn't boolean
            non_bowler_dismissals = [
                "run out",
                "retired hurt",
                "retired out",
                "obstructing the field",
            ]
            bowler_deliveries["is_bowler_wicket"] = (
                bowler_deliveries["wicket_kind"].notna()
                & ~bowler_deliveries["wicket_kind"].isin(non_bowler_dismissals)
            ).astype(int)

        # 3. Calculate wickets taken per match in each season (Vectorized)
        match_wickets = (
            bowler_deliveries.groupby(["year", "match_id"])[
                "is_bowler_wicket"
            ]
            .sum()
            .reset_index(name="wickets")
        )

        # 4. Aggregate total wickets, 3-wicket hauls, and 5-wicket hauls per season
        # Note: 3W hauls are calculated for 3 or 4 wickets; 5W hauls are 5+ wickets.
        season_summary = (
            match_wickets.groupby("year")
            .agg(
                Total_Wickets=("wickets", "sum"),
                Five_Wicket_Hauls=("wickets", lambda x: (x >= 5).sum()),
                Three_Wicket_Hauls=(
                    "wickets",
                    lambda x: ((x >= 3) & (x < 5)).sum(),
                ),
            )
            .reset_index()
        )

        # 5. Insert Player Name & Rename Columns for Display
        season_summary.insert(0, "Player", selected_bowler)
        season_summary.rename(
            columns={
                "year": "Season",
                "Total_Wickets": "Total Wickets",
                "Five_Wicket_Hauls": "5W Hauls",
                "Three_Wicket_Hauls": "3W Hauls (3-4 Wkts)",
            },
            inplace=True,
        )

        # Display clean dataframe without index
        st.dataframe(season_summary, hide_index=True)
    else:
        st.warning(f"No records found for {selected_bowler}.")


st.title("🎯 Auction Metrics")

# Select Metric Category
metric_choice = st.selectbox(
    "Select Auction Category",
    [
        "🔥 Top 20 Death Overs Finishers",
        "⚡ Top 20 Powerplay Bowlers",
        "🛡️ Top 20 Death Overs Bowling Specialists",
    ],
)

# View Mode: All-Time Leaderboard vs Year-Wise
view_mode = st.radio("View Mode", ["All-Time Top 20", "Year-Wise Top 20"], horizontal=True)

if view_mode == "Year-Wise Top 20":
    selected_year = st.selectbox("Select Year", sorted(ball2ball_data["year"].unique(), reverse=True))

# -------------------------------------------------------------
# 1. Top 20 Death Overs Finishers (Overs 16–20: over >= 15)
# -------------------------------------------------------------
if "Finishers" in metric_choice:
    st.subheader("🔥 Top 20 Death Overs Finishers")

    # Filter Death Overs
    df_filtered = ball2ball_data[ball2ball_data["over"] >= 15].copy()
    if view_mode == "Year-Wise Top 20":
        df_filtered = df_filtered[df_filtered["year"] == selected_year]

    # Grouping columns based on view mode
    group_cols = ["batter"] if view_mode == "All-Time Top 20" else ["year", "batter"]

    death_stats = (
        df_filtered.groupby(group_cols)
        .agg(
            Runs=("runs_batter", "sum"),
            Balls_Faced=("valid_ball", "sum"),
            Fours=("runs_batter", lambda x: (x == 4).sum()),
            Sixes=("runs_batter", lambda x: (x == 6).sum()),
        )
        .reset_index()
    )

    # Qualification Threshold (Min 30 balls all-time, 10 balls for a single year)
    min_balls = 30 if view_mode == "All-Time Top 20" else 10
    death_stats = death_stats[death_stats["Balls_Faced"] >= min_balls]

    # Metrics
    death_stats["Strike Rate"] = ((death_stats["Runs"] / death_stats["Balls_Faced"]) * 100).round(2)
    death_stats["Boundary %"] = (
        (((death_stats["Fours"] * 4) + (death_stats["Sixes"] * 6)) / death_stats["Runs"]) * 100
    ).round(2)

    # Sort & Get Top 20
    top_20 = death_stats.sort_values(by="Strike Rate", ascending=False).head(20)
    top_20.rename(columns={"batter": "Batter", "year": "Year"}, inplace=True)

    st.dataframe(top_20, hide_index=True, use_container_width=True)

# -------------------------------------------------------------
# 2. Top 20 Powerplay Bowlers (Overs 1–6: over < 6)
# -------------------------------------------------------------
elif "Powerplay" in metric_choice:
    st.subheader("⚡ Top 20 Powerplay Bowlers")

    df_filtered = ball2ball_data[ball2ball_data["over"] < 6].copy()
    if view_mode == "Year-Wise Top 20":
        df_filtered = df_filtered[df_filtered["year"] == selected_year]

    group_cols = ["bowler"] if view_mode == "All-Time Top 20" else ["year", "bowler"]

    pp_stats = (
        df_filtered.groupby(group_cols)
        .agg(
            Wickets=("bowler_wicket", "sum"),
            Runs_Conceded=("runs_bowler", "sum"),
            Legal_Balls=("valid_ball", "sum"),
            Dot_Balls=("runs_total", lambda x: (x == 0).sum()),
        )
        .reset_index()
    )

    # Qualification Threshold (Min 60 balls all-time, 6 balls for a single year)
    min_balls = 30 if view_mode == "All-Time Top 20" else 12
    pp_stats = pp_stats[pp_stats["Legal_Balls"] >= min_balls]

    # Metrics
    pp_stats["Economy Rate"] = (pp_stats["Runs_Conceded"] / (pp_stats["Legal_Balls"] / 6)).round(2)
    pp_stats["Dot Ball %"] = ((pp_stats["Dot_Balls"] / pp_stats["Legal_Balls"]) * 100).round(2)

    # Sort by Most Wickets, then lowest Economy & Get Top 20
    top_20 = pp_stats.sort_values(by=["Wickets", "Economy Rate"], ascending=[False, True]).head(20)
    top_20.rename(columns={"bowler": "Bowler", "year": "Year"}, inplace=True)

    st.dataframe(top_20, hide_index=True, use_container_width=True)

# -------------------------------------------------------------
# 3. Top 20 Death Overs Bowling Specialists (Overs 16–20: over >= 15)
# -------------------------------------------------------------
elif "Specialists" in metric_choice:
    st.subheader("🛡️ Top 20 Death Overs Bowling Specialists")

    df_filtered = ball2ball_data[ball2ball_data["over"] >= 15].copy()
    if view_mode == "Year-Wise Top 20":
        df_filtered = df_filtered[df_filtered["year"] == selected_year]

    group_cols = ["bowler"] if view_mode == "All-Time Top 20" else ["year", "bowler"]

    death_bowl_stats = (
        df_filtered.groupby(group_cols)
        .agg(
            Runs_Conceded=("runs_bowler", "sum"),
            Legal_Balls=("valid_ball", "sum"),
            Wickets=("bowler_wicket", "sum"),
        )
        .reset_index()
    )

    # Qualification Threshold (Min 60 balls all-time, 30 balls for a single year)
    min_balls = 30 if view_mode == "All-Time Top 20" else 12
    death_bowl_stats = death_bowl_stats[death_bowl_stats["Legal_Balls"] >= min_balls]

    # Metrics
    death_bowl_stats["Economy Rate"] = (
        death_bowl_stats["Runs_Conceded"] / (death_bowl_stats["Legal_Balls"] / 6)
    ).round(2)

    # Sort by Lowest Economy Rate & Get Top 20
    top_20 = death_bowl_stats.sort_values(by="Economy Rate", ascending=True).head(20)
    top_20.rename(columns={"bowler": "Bowler", "year": "Year"}, inplace=True)

    st.dataframe(top_20, hide_index=True, use_container_width=True)