import base64
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

# ==============================================================================
# 1. STREAMLIT CONFIGURATION (MUST BE THE FIRST STREAMLIT COMMAND)
# ==============================================================================
st.set_page_config(
    page_title="IPL Auction Intelligence Hub",
    page_icon="🏏",
    layout="wide",
)

# Global Plotly config overriding to hide modebars
_original_plotly_chart = st.plotly_chart


def custom_plotly_chart(fig, *args, **kwargs):
  default_config = {"displayModeBar": False}
  if "config" in kwargs and kwargs["config"] is not None:
    default_config.update(kwargs["config"])
  kwargs["config"] = default_config
  return _original_plotly_chart(fig, *args, **kwargs)


st.plotly_chart = custom_plotly_chart


# ==============================================================================
# 2. DATA LOADING & HEADER SETUP
# ==============================================================================
@st.cache_data
def load_ball_by_ball_data():
  return pd.read_csv("ball2ball_df.csv")


ball2ball_data = load_ball_by_ball_data()

# Render Header with Logo Safely
try:

  def get_image_base64(path):
    with open(path, "rb") as f:
      return base64.b64encode(f.read()).decode()

  logo_b64 = get_image_base64("IPL_LOGO.jpg")

  st.markdown(
      f"""
        <div style="
            background: linear-gradient(135deg, #0F172A 0%, #1E3A8A 100%);
            padding: 24px 32px;
            border-radius: 16px;
            display: flex;
            align-items: center;
            gap: 24px;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.2);
            margin-bottom: 25px;
        ">
            <img src="data:image/jpeg;base64,{logo_b64}" style="width: 85px; height: 85px; border-radius: 12px; object-fit: cover; border: 2px solid rgba(255,255,255,0.2);">
            <div>
                <h1 style="color: #FFFFFF; margin: 0; font-size: 2.3rem; font-weight: 800; letter-spacing: -0.5px;">
                    IPL Auction Analytics Hub
                </h1>
                <p style="color: #94A3B8; margin: 6px 0 0 0; font-size: 1rem; font-weight: 400;">
                    Advanced Metrics • Venue Insights • Player Valuation & Chase Pressure Indexes
                </p>
            </div>
        </div>
    """,
      unsafe_allow_html=True,
  )
except Exception:
  st.title("🎯 IPL Auction Intelligence & Scouting Hub")

st.markdown(
    "For the below analytics, use the settings in the left side of the page."
)

# Shared View Mode Control in Sidebar
st.sidebar.header("⚙️ Global Controls")
view_mode = st.sidebar.radio("View Mode", ["All-Time Top 20", "Year-Wise Top 20"])

if view_mode == "Year-Wise Top 20":
  selected_year = st.sidebar.selectbox(
      "Select Year", sorted(ball2ball_data["year"].unique(), reverse=True)
  )

# Main Section Tabs
tab_batting, tab_bowling, tab_wk = st.tabs(
    ["🏏 Batter Analytics", "⚡ Bowler Analytics", "🧤 WK-Batter Analytics"]
)


# ==============================================================================
# SECTION 1: BATTER ANALYTICS
# ==============================================================================
with tab_batting:
  st.header("🏏 Batting Performance & Phase Intelligence")

  batter_metric = st.selectbox(
      "Select Batting Metric Category",
      [
          "🔥 Powerplay Batters (Overs 1–6)",
          "🧱 Middle Overs Specialists (Overs 7–15)",
          "🚀 Death Overs Finishers (Overs 16–20)",
          "💎 Bankable Batters (400+ Runs @ 150+ SR)",
      ],
  )

  df_bat = ball2ball_data.copy()
  if view_mode == "Year-Wise Top 20":
    df_bat = df_bat[df_bat["year"] == selected_year]

  group_cols = ["batter"] if view_mode == "All-Time Top 20" else ["year", "batter"]

  # 1. Powerplay Batters (Overs 1–6)
  if "Powerplay" in batter_metric:
    st.subheader("⚡ Powerplay Batters (Overs 1–6)")
    pp_bat = df_bat[df_bat["over"] < 6]

    stats = (
        pp_bat.groupby(group_cols)
        .agg(
            Runs=("runs_batter", "sum"),
            Balls_Faced=("valid_ball", "sum"),
            Fours=("runs_batter", lambda x: (x == 4).sum()),
            Sixes=("runs_batter", lambda x: (x == 6).sum()),
            Dismissals=("player_out", lambda x: x.notna().sum()),
        )
        .reset_index()
    )

    min_balls = 100 if view_mode == "All-Time Top 20" else 50
    stats = stats[stats["Balls_Faced"] >= min_balls]

    stats["Strike Rate"] = (
        (stats["Runs"] / stats["Balls_Faced"]) * 100
    ).round(2)
    stats["Average"] = (
        stats["Runs"] / stats["Dismissals"].replace(0, 1)
    ).round(2)

    top_20 = stats.sort_values(
        by=["Strike Rate", "Average"], ascending=[False, False]
    ).head(20)
    top_20.rename(columns={"batter": "Batter", "year": "Year"}, inplace=True)
    st.dataframe(top_20, hide_index=True, use_container_width=True)

  # 2. Middle Overs Specialists (Overs 7–15)
  elif "Middle Overs" in batter_metric:
    st.subheader("🧱 Middle Overs Specialists (Overs 7–15)")
    mid_bat = df_bat[(df_bat["over"] >= 6) & (df_bat["over"] < 15)]

    stats = (
        mid_bat.groupby(group_cols)
        .agg(
            Runs=("runs_batter", "sum"),
            Balls_Faced=("valid_ball", "sum"),
            Dot_Balls=("runs_batter", lambda x: (x == 0).sum()),
            Fours=("runs_batter", lambda x: (x == 4).sum()),
            Sixes=("runs_batter", lambda x: (x == 6).sum()),
            Dismissals=(
                "player_out",
                lambda x: (x.notna()).sum() if "player_out" in x else 0,
            ),
        )
        .reset_index()
    )

    min_balls = 100 if view_mode == "All-Time Top 20" else 50
    stats = stats[stats["Balls_Faced"] >= min_balls]

    stats["Strike Rate"] = (
        (stats["Runs"] / stats["Balls_Faced"]) * 100
    ).round(2)
    stats["Average"] = (
        stats["Runs"] / stats["Dismissals"].replace(0, 1)
    ).round(2)
    stats["Dot Ball %"] = (
        (stats["Dot_Balls"] / stats["Balls_Faced"]) * 100
    ).round(2)

    top_20 = stats.sort_values(
        by=["Average", "Strike Rate"], ascending=[False, False]
    ).head(20)
    top_20.rename(columns={"batter": "Batter", "year": "Year"}, inplace=True)
    st.dataframe(top_20, hide_index=True, use_container_width=True)

  # 3. Death Overs Finishers (Overs 16–20)
  elif "Death Overs Finishers" in batter_metric:
    st.subheader("🚀 Death Overs Finishers (Overs 16–20)")
    death_bat = df_bat[df_bat["over"] >= 15]

    stats = (
        death_bat.groupby(group_cols)
        .agg(
            Runs=("runs_batter", "sum"),
            Balls_Faced=("valid_ball", "sum"),
            Fours=("runs_batter", lambda x: (x == 4).sum()),
            Sixes=("runs_batter", lambda x: (x == 6).sum()),
        )
        .reset_index()
    )

    min_balls = 100 if view_mode == "All-Time Top 20" else 50
    stats = stats[stats["Balls_Faced"] >= min_balls]

    stats["Strike Rate"] = (
        (stats["Runs"] / stats["Balls_Faced"]) * 100
    ).round(2)
    stats["Boundary %"] = (
        (((stats["Fours"] * 4) + (stats["Sixes"] * 6)) / stats["Runs"]) * 100
    ).round(2)

    top_20 = stats.sort_values(by="Strike Rate", ascending=False).head(20)
    top_20.rename(columns={"batter": "Batter", "year": "Year"}, inplace=True)
    st.dataframe(top_20, hide_index=True, use_container_width=True)

  # 4. Bankable Batters (400+ Runs @ 150+ SR in a Season)
  elif "Bankable" in batter_metric:
    st.subheader("💎 Bankable Season Performances (≥ 400 Runs & ≥ 150 SR)")

    stats = (
        ball2ball_data.groupby(["year", "batter"])
        .agg(
            Total_Runs=("runs_batter", "sum"),
            Balls_Faced=("valid_ball", "sum"),
            Fours=("runs_batter", lambda x: (x == 4).sum()),
            Sixes=("runs_batter", lambda x: (x == 6).sum()),
        )
        .reset_index()
    )

    stats["Strike Rate"] = (
        (stats["Total_Runs"] / stats["Balls_Faced"]) * 100
    ).round(2)

    bankable = stats[
        (stats["Total_Runs"] >= 400) & (stats["Strike Rate"] >= 150.0)
    ]

    if view_mode == "Year-Wise Top 20":
      bankable = bankable[bankable["year"] == selected_year]

    top_20 = bankable.sort_values(
        by=["Total_Runs", "Strike Rate"], ascending=[False, False]
    ).head(20)
    top_20.rename(columns={"batter": "Batter", "year": "Year"}, inplace=True)
    st.dataframe(top_20, hide_index=True, use_container_width=True)


# ==============================================================================
# SECTION 2: BOWLER ANALYTICS
# ==============================================================================
with tab_bowling:
  st.header("⚡ Bowler Intelligence")

  bowler_metric = st.selectbox(
      "Select Bowling Metric Category",
      [
          "⚡ Powerplay Bowlers (Overs 1–6)",
          "🎯 Middle Overs Wicket-Takers (Overs 7–15)",
          "🛡️ Death Overs Specialists (Overs 16–20)",
          "📉 Overall Economical Bowlers",
      ],
  )

  df_bowl = ball2ball_data.copy()

  if view_mode == "Year-Wise Top 20":
    df_bowl = df_bowl[df_bowl["year"] == selected_year]

  group_cols = ["bowler"] if view_mode == "All-Time Top 20" else ["year", "bowler"]

  # 1. Powerplay Bowlers
  if "Powerplay" in bowler_metric:
    st.subheader("⚡ Powerplay Bowlers (Overs 1–6)")
    pp_bowl = df_bowl[df_bowl["over"] < 6]

    stats = (
        pp_bowl.groupby(group_cols)
        .agg(
            Wickets=("bowler_wicket", "sum"),
            Runs_Conceded=("runs_bowler", "sum"),
            Legal_Balls=("valid_ball", "sum"),
            Dot_Balls=("runs_total", lambda x: (x == 0).sum()),
        )
        .reset_index()
    )

    min_balls = 100 if view_mode == "All-Time Top 20" else 60
    stats = stats[stats["Legal_Balls"] >= min_balls]

    stats["Economy Rate"] = (
        stats["Runs_Conceded"] / (stats["Legal_Balls"] / 6)
    ).round(2)
    stats["Dot Ball %"] = (
        (stats["Dot_Balls"] / stats["Legal_Balls"]) * 100
    ).round(2)

    top_20 = stats.sort_values(
        by=["Wickets", "Economy Rate"], ascending=[False, True]
    ).head(20)
    top_20.rename(columns={"bowler": "Bowler", "year": "Year"}, inplace=True)
    st.dataframe(top_20, hide_index=True, use_container_width=True)

  # 2. Middle Overs Wicket-Takers (Overs 7–15)
  elif "Middle Overs" in bowler_metric:
    st.subheader("🎯 Middle Overs Wicket-Takers (Overs 7–15)")
    mid_bowl = df_bowl[(df_bowl["over"] >= 6) & (df_bowl["over"] < 15)]

    stats = (
        mid_bowl.groupby(group_cols)
        .agg(
            Wickets=("bowler_wicket", "sum"),
            Runs_Conceded=("runs_bowler", "sum"),
            Legal_Balls=("valid_ball", "sum"),
        )
        .reset_index()
    )

    min_balls = 100 if view_mode == "All-Time Top 20" else 60
    stats = stats[stats["Legal_Balls"] >= min_balls]

    stats["Economy Rate"] = (
        stats["Runs_Conceded"] / (stats["Legal_Balls"] / 6)
    ).round(2)
    stats["Bowling Avg"] = (
        stats["Runs_Conceded"] / stats["Wickets"].replace(0, 1)
    ).round(2)

    top_20 = stats.sort_values(
        by=["Wickets", "Economy Rate"], ascending=[False, True]
    ).head(20)
    top_20.rename(columns={"bowler": "Bowler", "year": "Year"}, inplace=True)
    st.dataframe(top_20, hide_index=True, use_container_width=True)

  # 3. Death Overs Specialists
  elif "Death Overs Specialists" in bowler_metric:
    st.subheader("🛡️ Death Overs Specialists (Overs 16–20)")
    death_bowl = df_bowl[df_bowl["over"] >= 15]

    stats = (
        death_bowl.groupby(group_cols)
        .agg(
            Wickets=("bowler_wicket", "sum"),
            Runs_Conceded=("runs_bowler", "sum"),
            Legal_Balls=("valid_ball", "sum"),
        )
        .reset_index()
    )

    min_balls = 100 if view_mode == "All-Time Top 20" else 60
    stats = stats[stats["Legal_Balls"] >= min_balls]

    stats["Economy Rate"] = (
        stats["Runs_Conceded"] / (stats["Legal_Balls"] / 6)
    ).round(2)

    top_20 = stats.sort_values(by="Economy Rate", ascending=True).head(20)
    top_20.rename(columns={"bowler": "Bowler", "year": "Year"}, inplace=True)
    st.dataframe(top_20, hide_index=True, use_container_width=True)

  # 4. Overall Economical Bowlers
  elif "Economical" in bowler_metric:
    st.subheader("📉 Overall Most Economical Bowlers")

    stats = (
        df_bowl.groupby(group_cols)
        .agg(
            Runs_Conceded=("runs_bowler", "sum"),
            Legal_Balls=("valid_ball", "sum"),
            Wickets=("bowler_wicket", "sum"),
            Dot_Balls=("runs_total", lambda x: (x == 0).sum()),
        )
        .reset_index()
    )

    min_balls = 100 if view_mode == "All-Time Top 20" else 60
    stats = stats[stats["Legal_Balls"] >= min_balls]

    stats["Economy Rate"] = (
        stats["Runs_Conceded"] / (stats["Legal_Balls"] / 6)
    ).round(2)
    stats["Dot Ball %"] = (
        (stats["Dot_Balls"] / stats["Legal_Balls"]) * 100
    ).round(2)

    top_20 = stats.sort_values(by="Economy Rate", ascending=True).head(20)
    top_20.rename(columns={"bowler": "Bowler", "year": "Year"}, inplace=True)
    st.dataframe(top_20, hide_index=True, use_container_width=True)


# ==============================================================================
# SECTION 3: WICKETKEEPER-BATTER ANALYTICS
# ==============================================================================
with tab_wk:
  st.header("🧤 Wicketkeeper-Batter Analysis")

  ipl_wicketkeepers = {
      "MS Dhoni",
      "Dinesh Karthik",
      "Wriddhiman Saha",
      "Robin Uthappa",
      "Parthiv Patel",
      "Naman Ojha",
      "Adam Gilchrist",
      "Kumar Sangakkara",
      "Brendon McCullum",
      "Mark Boucher",
      "AB de Villiers",
      "Kamran Akmal",
      "Tatenda Taibu",
      "Luke Ronchi",
      "Manvinder Bisla",
      "CM Gautam",
      "Aditya Tare",
      "Eknath Kerkar",
      "Shreevats Goswami",
      "Mahesh Rawat",
      "Pinal Shah",
      "Yogesh Takawale",
      "Ambati Rayudu",
      "Rishabh Pant",
      "Sanju Samson",
      "KL Rahul",
      "Ishan Kishan",
      "Jitesh Sharma",
      "Dhruv Jurel",
      "Prabhsimran Singh",
      "Anuj Rawat",
      "Abhishek Porel",
      "Vishnu Vinod",
      "KS Bharat",
      "Kumar Kushagra",
      "Robin Minz",
      "Aryan Juyal",
      "Kunal Rathore",
      "Luvnith Sisodia",
      "Sheldon Jackson",
      "Baba Indrajith",
      "Upendra Yadav",
      "Urvil Patel",
      "Vansh Bedi",
      "Shrijith Krishnan",
      "Jos Buttler",
      "Quinton de Kock",
      "Nicholas Pooran",
      "Heinrich Klaasen",
      "Phil Salt",
      "Tristan Stubbs",
      "Devon Conway",
      "Rahmanullah Gurbaz",
      "Josh Inglis",
      "Ryan Rickelton",
      "Shai Hope",
      "Donovan Ferreira",
      "Matthew Wade",
      "Tim Seifert",
      "Sam Billings",
      "Alex Carey",
      "Ben McDermott",
      "Glenn Phillips",
      "Peter Handscomb",
      "Finn Allen",
  }

  selected_position = st.slider(
      "Filter Batting Position Range (e.g., Positions 1 to 8)",
      min_value=1,
      max_value=8,
      value=(1, 8),
  )

  df_wk = ball2ball_data[
      (ball2ball_data["batter"].isin(ipl_wicketkeepers))
      & (ball2ball_data["bat_pos"] >= selected_position[0])
      & (ball2ball_data["bat_pos"] <= selected_position[1])
  ].copy()

  if view_mode == "Year-Wise Top 20":
    df_wk = df_wk[df_wk["year"] == selected_year]

  group_cols = ["batter"] if view_mode == "All-Time Top 20" else ["year", "batter"]

  wk_stats = (
      df_wk.groupby(group_cols)
      .agg(
          Runs=("runs_batter", "sum"),
          Balls_Faced=("valid_ball", "sum"),
          Avg_Batting_Pos=("bat_pos", lambda x: round(x.mean())),
          Fours=("runs_batter", lambda x: (x == 4).sum()),
          Sixes=("runs_batter", lambda x: (x == 6).sum()),
          Dismissals=("player_out", "count"),
      )
      .reset_index()
  )

  min_balls = 30 if view_mode == "All-Time Top 20" else 15
  wk_stats = wk_stats[wk_stats["Balls_Faced"] >= min_balls]

  wk_stats["Strike Rate"] = (
      (wk_stats["Runs"] / wk_stats["Balls_Faced"]) * 100
  ).round(2)
  wk_stats["Average"] = (
      wk_stats["Runs"] / wk_stats["Dismissals"].replace(0, 1)
  ).round(2)
  wk_stats["Avg_Batting_Pos"] = wk_stats["Avg_Batting_Pos"].round(1)

  top_20 = wk_stats.sort_values(
      by=["Runs", "Strike Rate"], ascending=[False, False]
  ).head(20)
  top_20.rename(
      columns={
          "batter": "Wicketkeeper",
          "year": "Year",
          "Avg_Batting_Pos": "Avg Pos",
      },
      inplace=True,
  )

  st.subheader(
      f"Top Wicketkeepers (Batting Positions {selected_position[0]}–{selected_position[1]})"
  )
  st.dataframe(top_20, hide_index=True, use_container_width=True)

import gc
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


# ==========================================
# HELPER: Modern Horizontal Progress Bar
# ==========================================
def create_modern_progress_bar(value, target, label, color):
  """Creates a sleek, modern horizontal progress bar using Plotly."""
  fig = go.Figure()

  # Background track (Gray)
  fig.add_trace(
      go.Bar(
          y=[label],
          x=[target],
          orientation="h",
          marker=dict(color="#E5E7EB", cornerradius=6),
          hoverinfo="none",
          showlegend=False,
      )
  )

  # Active progress track
  fig.add_trace(
      go.Bar(
          y=[label],
          x=[value],
          orientation="h",
          marker=dict(color=color, cornerradius=6),
          text=[f" <b>{value} Matches</b>"],
          textposition="inside",
          insidetextanchor="start",
          textfont=dict(color="white", size=14),
          hoverinfo="x",
          showlegend=False,
      )
  )

  fig.update_layout(
      barmode="overlay",
      height=60,
      margin=dict(l=0, r=20, t=5, b=5),
      xaxis=dict(
          showgrid=False,
          zeroline=False,
          showticklabels=False,
          range=[0, max(target, value + 5)],
      ),
      yaxis=dict(
          showgrid=False,
          zeroline=False,
          tickfont=dict(size=14, color="#374151"),
      ),
      paper_bgcolor="rgba(0,0,0,0)",
      plot_bgcolor="rgba(0,0,0,0)",
  )
  return fig


# ==========================================
# ALL-ROUNDERS SECTION (Memory Optimized + Auto-run)
# ==========================================
st.markdown("---")
st.title("⚡ Top All-Rounders Performance")

# Pre-calculate batter's valid ball flag (In-place bit manipulation to save RAM)
if "batter_ball" not in ball2ball_data.columns:
  if "wide" in ball2ball_data.columns:
    ball2ball_data["batter_ball"] = (ball2ball_data["wide"] == 0).astype("int8")
  elif "extra_type" in ball2ball_data.columns:
    ball2ball_data["batter_ball"] = (
        ball2ball_data["extra_type"] != "wides"
    ).astype("int8")
  else:
    ball2ball_data["batter_ball"] = 1

# ----------------------------------------------------
# Step 0: Apply View Mode Filter
# ----------------------------------------------------
is_year_wise = "view_mode" in locals() and view_mode == "Year-Wise Top 20"

if is_year_wise:
  df_allround = ball2ball_data[ball2ball_data["year"] == selected_year]
else:
  df_allround = ball2ball_data  # Avoid full copy in memory

MIN_RUNS = 15 if is_year_wise else 50
MIN_WICKETS = 2 if is_year_wise else 5

# ----------------------------------------------------
# Step 1: Filter Qualified All-Rounders
# ----------------------------------------------------
batting_totals = df_allround.groupby("batter")["runs_batter"].sum()
bowling_totals = df_allround.groupby("bowler")["bowler_wicket"].sum()

allrounder_batters = batting_totals[batting_totals >= MIN_RUNS].index
allrounder_bowlers = bowling_totals[bowling_totals >= MIN_WICKETS].index

allrounders_options = sorted(
    list(set(allrounder_batters).intersection(set(allrounder_bowlers)))
)

if not allrounders_options:
  st.info("No all-rounders met the threshold for the currently selected filter.")
else:
  # Selecting a player automatically triggers the calculations below
  selected_allrounder = st.selectbox(
      label=(
          f"Select All-Rounder ({len(allrounders_options)} players qualified)"
      ),
      options=allrounders_options,
      key="allrounder_selectbox",
  )

  # ----------------------------------------------------
  # Step 2 & 3: Match-by-Match Stats (Runs on Selection)
  # ----------------------------------------------------
  bat_mask = df_allround["batter"] == selected_allrounder
  batter_matches = (
      df_allround.loc[
          bat_mask,
          ["match_id", "runs_batter", "batter_ball", "batting_team", "bowling_team"],
      ]
      .groupby("match_id", as_index=False)
      .agg(
          runs_scored=("runs_batter", "sum"),
          balls_faced=("batter_ball", "sum"),
          batting_team=("batting_team", "first"),
          bowling_team=("bowling_team", "first"),
      )
  )

  bowl_mask = df_allround["bowler"] == selected_allrounder
  bowler_matches = (
      df_allround.loc[
          bowl_mask,
          [
              "match_id",
              "bowler_wicket",
              "runs_bowler",
              "valid_ball",
              "bowling_team",
              "batting_team",
          ],
      ]
      .groupby("match_id", as_index=False)
      .agg(
          wickets_taken=("bowler_wicket", "sum"),
          runs_conceded=("runs_bowler", "sum"),
          balls_bowled=("valid_ball", "sum"),
          bowl_batting_team=("bowling_team", "first"),
          bowl_bowling_team=("batting_team", "first"),
      )
  )

  # ----------------------------------------------------
  # Step 4: Merge Batting & Bowling Stats per Match
  # ----------------------------------------------------
  match_perf = pd.merge(
      batter_matches, bowler_matches, on="match_id", how="outer"
  )

  # Clean team names without allocating unnecessary intermediate DataFrames
  match_perf["batting_team"] = match_perf["batting_team"].fillna(
      match_perf["bowl_batting_team"]
  )
  match_perf["bowling_team"] = match_perf["bowling_team"].fillna(
      match_perf["bowl_bowling_team"]
  )
  match_perf.drop(
      columns=["bowl_batting_team", "bowl_bowling_team"],
      inplace=True,
      errors="ignore",
  )

  # Memory downcasting for numeric metrics
  numeric_cols = [
      "runs_scored",
      "balls_faced",
      "wickets_taken",
      "runs_conceded",
      "balls_bowled",
  ]
  for col in numeric_cols:
    match_perf[col] = match_perf[col].fillna(0).astype("int16")

  if "year" in df_allround.columns:
    match_year_map = (
        df_allround[["match_id", "year"]]
        .drop_duplicates()
        .set_index("match_id")["year"]
    )
    match_perf["year"] = (
        match_perf["match_id"].map(match_year_map).astype("int16")
    )

  # Clear intermediate data from RAM
  del batter_matches, bowler_matches
  gc.collect()

  # ----------------------------------------------------
  # Step 5: Categorize Contribution Types
  # ----------------------------------------------------
  dual_mask = (match_perf["runs_scored"] >= 20) & (
      match_perf["wickets_taken"] >= 1
  )
  dual_impact_df = match_perf[dual_mask]
  dual_impact_count = len(dual_impact_df)

  batting_impact_count = (match_perf["runs_scored"] >= 30).sum()
  bowling_impact_count = (match_perf["wickets_taken"] >= 2).sum()

  total_runs = int(match_perf["runs_scored"].sum())
  total_wickets = int(match_perf["wickets_taken"].sum())

  # ----------------------------------------------------
  # Step 6 & 7: Metric Cards & Progress Bars
  # ----------------------------------------------------
  col1, col2 = st.columns(2)
  col1.metric("Total Runs", f"{total_runs:,}")
  col2.metric("Total Wickets", f"{total_wickets:,}")

  st.markdown("### 📊 Contribution Impact Breakdown")

  max_target_dual = 10 if is_year_wise else 25
  max_target_single = 15 if is_year_wise else 40

  st.caption("🔥 **Type 1: Same-Match Dual Impact** (20+ Runs AND 1+ Wicket)")
  st.plotly_chart(
      create_modern_progress_bar(
          dual_impact_count, max_target_dual, "Dual Impact", "#2563EB"
      ),
      use_container_width=True,
  )

  st.caption("🏏 **Type 2: Key Batting Contribution** (30+ Runs Scored)")
  st.plotly_chart(
      create_modern_progress_bar(
          batting_impact_count, max_target_single, "Batting Impact", "#16A34A"
      ),
      use_container_width=True,
  )

  st.caption("⚾ **Type 3: Key Bowling Contribution** (2+ Wickets Taken)")
  st.plotly_chart(
      create_modern_progress_bar(
          bowling_impact_count, max_target_single, "Bowling Impact", "#DC2626"
      ),
      use_container_width=True,
  )

  # ----------------------------------------------------
  # Step 8: Detailed Informative Table
  # ----------------------------------------------------
  with st.expander("📄 View Dual Impact Match Details"):
    if dual_impact_count > 0:
      cols_to_display = [
          "batting_team",
          "bowling_team",
          "runs_scored",
          "balls_faced",
          "wickets_taken",
          "runs_conceded",
      ]
      rename_dict = {
          "batting_team": "Team",
          "bowling_team": "Opponent",
          "runs_scored": "Runs Scored",
          "balls_faced": "Balls Faced",
          "wickets_taken": "Wickets Taken",
          "runs_conceded": "Runs Conceded",
      }

      if "year" in dual_impact_df.columns:
        cols_to_display.insert(0, "year")
        rename_dict["year"] = "Season"

      st.dataframe(
          dual_impact_df[cols_to_display].rename(columns=rename_dict),
          use_container_width=True,
          hide_index=True,
      )
    else:
      st.info(
          "No dual-impact matches found for this player matching the"
          " threshold."
      )
      
# ==========================================
# FIELDING IMPACT SECTION (Filter-Aware)
# ==========================================
st.markdown("---")
st.title("🧤 Fielding Impact Leaderboard")

# ----------------------------------------------------
# Step 0: Apply View Mode Filter (All-Time vs Year-Wise)
# ----------------------------------------------------
df_fielding = ball2ball_data.copy()
if 'view_mode' in locals() and view_mode == "Year-Wise Top 20":
    df_fielding = df_fielding[df_fielding["year"] == selected_year]

# Support both 'wicket_kind' and 'dismissal_kind' column names
dismissal_col = 'wicket_kind' if 'wicket_kind' in df_fielding.columns else 'dismissal_kind'
fielder_col = 'fielders' if 'fielders' in df_fielding.columns else 'fielder'

# ----------------------------------------------------
# Step 1: Filter Fielding Events & Calculate Metrics
# ----------------------------------------------------
fielding_data = df_fielding[
    df_fielding[dismissal_col].isin(['caught', 'run out']) & 
    df_fielding[fielder_col].notna() & 
    (df_fielding[fielder_col] != '')
].copy()

if not fielding_data.empty:
    
    # Aggregation per fielder
    fielding_summary = fielding_data.groupby([fielder_col, dismissal_col]).size().unstack(fill_value=0).reset_index()

    # Ensure required columns exist
    if 'caught' not in fielding_summary.columns:
        fielding_summary['caught'] = 0
    if 'run out' not in fielding_summary.columns:
        fielding_summary['run out'] = 0

    # Calculate Fielding Impact Score (FIS)
    fielding_summary['catches'] = fielding_summary['caught'].astype(int)
    fielding_summary['run_outs'] = fielding_summary['run out'].astype(int)
    fielding_summary['total_dismissals'] = fielding_summary['catches'] + fielding_summary['run_outs']
    
    fielding_summary['fielding_impact_score'] = (
        fielding_summary['catches'] * 1.0 + fielding_summary['run_outs'] * 1.5
    ).round(1)

    # Sort by Fielding Impact Score descending
    fielding_summary = fielding_summary.sort_values(by='fielding_impact_score', ascending=False).reset_index(drop=True)
    fielding_summary['Rank'] = fielding_summary.index + 1

    # ----------------------------------------------------
    # Step 2: User Controls (Top N Selection)
    # ----------------------------------------------------
    max_available_fielders = len(fielding_summary)
    slider_max = min(25, max_available_fielders)
    slider_min = min(5, max_available_fielders)

    col_ctrl1, col_ctrl2 = st.columns([1, 2])
    with col_ctrl1:
        top_n = st.slider(
            "Select Top Fielders to Display", 
            min_value=slider_min, 
            max_value=slider_max, 
            value=min(10, slider_max), 
            step=5,
            key="fielding_top_n_slider"
        )

    top_fielders_df = fielding_summary.head(top_n).copy()

    # ----------------------------------------------------
    # Step 3: Top 3 Winner Podium Cards
    # ----------------------------------------------------
    st.markdown("### 🏆 Top Fielding Performers")
    
    podium_cols = st.columns(min(3, len(top_fielders_df)))
    medals = ["🥇 1st Place", "🥈 2nd Place", "🥉 3rd Place"]
    border_colors = ["#FFD700", "#C0C0C0", "#CD7F32"]
    
    for idx in range(min(3, len(top_fielders_df))):
        row = top_fielders_df.iloc[idx]
        with podium_cols[idx]:
            st.markdown(
                f"""
                <div style="
                    background-color: #FFFFFF;
                    border: 1px solid #E5E7EB;
                    border-top: 5px solid {border_colors[idx]};
                    border-radius: 10px;
                    padding: 16px;
                    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
                    text-align: center;
                ">
                    <span style="font-size: 13px; font-weight: 700; color: #6B7280; text-transform: uppercase;">{medals[idx]}</span>
                    <h3 style="margin: 6px 0 2px 0; font-size: 20px; color: #111827;">{row[fielder_col]}</h3>
                    <div style="font-size: 28px; font-weight: 800; color: #2563EB;">{row['fielding_impact_score']} <span style="font-size: 13px; font-weight: 500; color: #6B7280;">FIS</span></div>
                    <div style="margin-top: 8px; font-size: 12px; color: #4B5563;">
                        🧤 <b>{row['catches']}</b> Catches &nbsp;|&nbsp; 🎯 <b>{row['run_outs']}</b> Run Outs
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # ----------------------------------------------------
    # Step 4: Segmented Stacked Chart
    # ----------------------------------------------------
    st.markdown("### 📊 Catches vs. Run Outs Breakdown")

    chart_df = top_fielders_df.iloc[::-1]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=chart_df[fielder_col],
        x=chart_df['catches'],
        name='Catches (1.0 pt)',
        orientation='h',
        marker=dict(color='#3B82F6', cornerradius=4),
        text=chart_df['catches'],
        textposition='inside',
        insidetextanchor='middle',
        textfont=dict(color='white', size=12, family='sans-serif')
    ))

    fig.add_trace(go.Bar(
        y=chart_df[fielder_col],
        x=chart_df['run_outs'],
        name='Run Outs (1.5 pts)',
        orientation='h',
        marker=dict(color='#EF4444', cornerradius=4),
        text=chart_df['run_outs'],
        textposition='inside',
        insidetextanchor='middle',
        textfont=dict(color='white', size=12, family='sans-serif')
    ))

    fig.update_layout(
        barmode='stack',
        height=max(350, top_n * 32),
        margin=dict(l=20, r=20, t=20, b=30),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        ),
        xaxis=dict(
            title='Total Fielding Dismissals',
            showgrid=True,
            gridcolor='#F3F4F6',
            zeroline=False
        ),
        yaxis=dict(
            showgrid=False,
            tickfont=dict(size=13, color='#111827', weight='bold')
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    st.plotly_chart(fig, use_container_width=True)

    # ----------------------------------------------------
    # Step 5: Leaderboard Table
    # ----------------------------------------------------
    with st.expander("📄 View Full Fielding Impact Leaderboard Table"):
        display_fielding = fielding_summary[[
            'Rank', fielder_col, 'catches', 'run_outs', 'total_dismissals', 'fielding_impact_score'
        ]].rename(columns={
            fielder_col: 'Fielder Name',
            'catches': 'Catches',
            'run_outs': 'Run Outs',
            'total_dismissals': 'Total Dismissals',
            'fielding_impact_score': 'Fielding Impact Score (FIS)'
        })

        st.dataframe(
            display_fielding,
            use_container_width=True,
            hide_index=True
        )

else:
    st.info("No fielding data available for the selected view mode / season.")

# ==========================================
# CHASE PRESSURE INDEX SECTION (Filter-Aware)
# ==========================================
st.markdown("---")
st.title("🎯 Chase Pressure Index (CPI)")

with st.expander("ℹ️ How is CPI Calculated?"):
    st.latex(r"\text{CPI} = (\text{Strike Rate} \times 0.5) + (\text{Average} \times 0.3) + \left(\frac{\text{Runs in 180+ Targets}}{\text{Total Runs}} \times 20\right)")
    st.markdown("""
    * **⚡ Strike Rate (50%)** — Scoring speed during chases
    * **📊 Average (30%)** — Consistency and match-finishing ability
    * **🔥 High Target Bonus (20%)** — Performance under high pressure ($\ge 180$ target)
    """)

# ----------------------------------------------------
# Step 0: Apply View Mode Filter (All-Time vs Year-Wise)
# ----------------------------------------------------
df_chase = ball2ball_data.copy()
if "view_mode" in locals() and view_mode == "Year-Wise Top 20":
    df_chase = df_chase[df_chase["year"] == selected_year]

# Filter strictly for 2nd innings with a defined target
chase_data = df_chase[
    (df_chase["innings"] == 2) & 
    (df_chase["runs_target"].notna())
].copy()

if not chase_data.empty:

    # ----------------------------------------------------
    # Step 1: Calculate Chase Stats per Batter
    # ----------------------------------------------------
    chase_summary = (
        chase_data.groupby("batter")
        .agg(
            Innings_Chased=("match_id", "nunique"),
            Chase_Runs=("runs_batter", "sum"),
            Chase_Balls=("valid_ball", "sum"),
            Chase_Dismissals=("player_out", "count"),
            Fours=("runs_batter", lambda x: (x == 4).sum()),
            Sixes=("runs_batter", lambda x: (x == 6).sum()),
            High_Target_Runs=(
                "runs_batter",
                lambda x: x[chase_data.loc[x.index, "runs_target"] >= 180].sum(),
            ),
        )
        .reset_index()
    )

    # Qualification Threshold: Minimum 100 balls faced for All-Time mode
    # (Adjusted to 30 for Year-Wise mode to account for shorter single-season sample sizes)
    min_balls_chase = 100 if ("view_mode" in locals() and view_mode == "All-Time Top 20") else 30
    chase_summary = chase_summary[chase_summary["Chase_Balls"] >= min_balls_chase].copy()

    if not chase_summary.empty:

        # Derived Performance Metrics
        chase_summary["Chase_SR"] = (
            (chase_summary["Chase_Runs"] / chase_summary["Chase_Balls"]) * 100
        ).round(2)

        chase_summary["Chase_Avg"] = (
            chase_summary["Chase_Runs"] / chase_summary["Chase_Dismissals"].replace(0, 1)
        ).round(2)

        chase_summary["Boundary_%"] = (
            ((chase_summary["Fours"] * 4 + chase_summary["Sixes"] * 6) / chase_summary["Chase_Runs"].replace(0, 1)) * 100
        ).round(2)

        # Composite Chase Pressure Index Score
        chase_summary["Chase_Pressure_Index"] = (
            (chase_summary["Chase_SR"] * 0.5) + 
            (chase_summary["Chase_Avg"] * 0.3) + 
            ((chase_summary["High_Target_Runs"] / chase_summary["Chase_Runs"].replace(0, 1)) * 20)
        ).round(1)

        # Sort descending by Chase Pressure Index
        chase_summary = chase_summary.sort_values(by="Chase_Pressure_Index", ascending=False).reset_index(drop=True)
        chase_summary["Rank"] = chase_summary.index + 1

        # ----------------------------------------------------
        # Step 2: User Controls (Top N Slider)
        # ----------------------------------------------------
        max_available_chasers = len(chase_summary)
        slider_max_c = min(25, max_available_chasers)
        slider_min_c = min(5, max_available_chasers)

        col_c1, col_c2 = st.columns([1, 2])
        with col_c1:
            top_n_chase = st.slider(
                "Select Top Chasers to Display",
                min_value=slider_min_c,
                max_value=slider_max_c,
                value=min(10, slider_max_c),
                step=5,
                key="chase_top_n_slider"
            )

        top_chasers_df = chase_summary.head(top_n_chase).copy()

        # ----------------------------------------------------
        # Step 3: Top 3 Winner Podium Cards
        # ----------------------------------------------------
        st.markdown("### 🏆 Top Chase Master Performers")

        podium_cols_c = st.columns(min(3, len(top_chasers_df)))
        medals_c = ["🥇 1st Place", "🥈 2nd Place", "🥉 3rd Place"]
        border_colors_c = ["#FFD700", "#C0C0C0", "#CD7F32"]

        for idx in range(min(3, len(top_chasers_df))):
            row = top_chasers_df.iloc[idx]
            with podium_cols_c[idx]:
                st.markdown(
                    f"""
                    <div style="
                        background-color: #FFFFFF;
                        border: 1px solid #E5E7EB;
                        border-top: 5px solid {border_colors_c[idx]};
                        border-radius: 10px;
                        padding: 16px;
                        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
                        text-align: center;
                    ">
                        <span style="font-size: 13px; font-weight: 700; color: #6B7280; text-transform: uppercase;">{medals_c[idx]}</span>
                        <h3 style="margin: 6px 0 2px 0; font-size: 20px; color: #111827;">{row['batter']}</h3>
                        <div style="font-size: 28px; font-weight: 800; color: #16A34A;">{row['Chase_Pressure_Index']} <span style="font-size: 13px; font-weight: 500; color: #6B7280;">CPI</span></div>
                        <div style="margin-top: 8px; font-size: 12px; color: #4B5563;">
                            🏏 <b>{row['Chase_Runs']}</b> Runs &nbsp;|&nbsp; ⚡ <b>{row['Chase_SR']}</b> SR &nbsp;|&nbsp; 📊 <b>{row['Chase_Avg']}</b> Avg
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        st.markdown("<br>", unsafe_allow_html=True)

        # ----------------------------------------------------
        # Step 4: Clean & Intuitive CPI Leaderboard Chart
        # ----------------------------------------------------
        st.markdown("### 📊 Chase Pressure Index (CPI) Leaderboard")

        # Reverse dataframe order for top-to-bottom bar chart display
        chart_chase_df = top_chasers_df.iloc[::-1].copy()

        # Build clean horizontal bar chart with color gradient
        fig_chase = go.Figure()

        fig_chase.add_trace(go.Bar(
            y=chart_chase_df['batter'],
            x=chart_chase_df['Chase_Pressure_Index'],
            orientation='h',
            marker=dict(
                color=chart_chase_df['Chase_Pressure_Index'],
                colorscale='Emrld',  # Clean green gradient
                showscale=False,
                cornerradius=4
            ),
            # Display formatted CPI score on each bar
            text=[f"  <b>{val:.1f} CPI</b>" for val in chart_chase_df['Chase_Pressure_Index']],
            textposition='outside',
            textfont=dict(size=13, color='#0F766E', family='sans-serif'),
            # Custom Hover Tooltip Template
            customdata=chart_chase_df[['Chase_Runs', 'Chase_SR', 'Chase_Avg', 'High_Target_Runs', 'Innings_Chased']].values,
            hovertemplate=(
                "<b>%{y}</b><br><br>" +
                "🎯 <b>CPI Score:</b> %{x:.1f}<br>" +
                "🏏 <b>Chase Runs:</b> %{customdata[0]} (%{customdata[4]} Innings)<br>" +
                "⚡ <b>Strike Rate:</b> %{customdata[1]:.2f}<br>" +
                "📊 <b>Average:</b> %{customdata[2]:.2f}<br>" +
                "🔥 <b>Runs in 180+ Chases:</b> %{customdata[3]}<extra></extra>"
            )
        ))

        # Add margin to x-axis max so text labels aren't cut off
        max_cpi = chart_chase_df['Chase_Pressure_Index'].max()

        fig_chase.update_layout(
            height=max(360, top_n_chase * 36),
            margin=dict(l=20, r=60, t=20, b=30),
            xaxis=dict(
                title='Chase Pressure Index Score',
                showgrid=True,
                gridcolor='#F3F4F6',
                zeroline=False,
                range=[0, max_cpi * 1.18]  # Extra headroom for labels
            ),
            yaxis=dict(
                showgrid=False,
                tickfont=dict(size=13, color='#111827', weight='bold')
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )

        st.plotly_chart(fig_chase, use_container_width=True)

        # ----------------------------------------------------
        # Step 5: Leaderboard Table Expander
        # ----------------------------------------------------
        with st.expander("📄 View Full Chase Pressure Index Leaderboard Table"):
            display_chase = chase_summary[[
                'Rank', 'batter', 'Innings_Chased', 'Chase_Runs', 'Chase_Balls', 
                'Chase_SR', 'Chase_Avg', 'High_Target_Runs', 'Boundary_%', 'Chase_Pressure_Index'
            ]].rename(columns={
                'batter': 'Batter Name',
                'Innings_Chased': 'Innings Chased',
                'Chase_Runs': 'Chase Runs',
                'Chase_Balls': 'Balls Faced',
                'Chase_SR': 'Strike Rate',
                'Chase_Avg': 'Average',
                'High_Target_Runs': 'Runs in 180+ Targets',
                'Boundary_%': 'Boundary %',
                'Chase_Pressure_Index': 'Chase Pressure Index (CPI)'
            })

            st.dataframe(
                display_chase,
                use_container_width=True,
                hide_index=True
            )
    else:
        st.info(f"No batters met the minimum qualification threshold of {min_balls_chase} balls faced while chasing.")
else:
    st.info("No chase data available for the selected view mode / season.")

# ==========================================
# VENUE SPECIALISTS SECTION (Batter & Bowler)
# ==========================================
st.markdown("---")
st.title("🏟️ Venue Specialists")

# Clean calculation explanation box
with st.expander("ℹ️ How are Venue Performance Indices calculated?"):
    st.latex(r"\text{Batter Venue Index} = (\text{Venue SR} \times 0.5) + (\text{Venue Avg} \times 0.5)")
    st.latex(r"\text{Bowler Venue Index} = \left(\frac{100}{\text{Venue Economy}}\right) \times 0.6 + \left(\frac{100}{\text{Venue Bowling SR}}\right) \times 0.4")
    st.markdown("""
    * **🏏 Batters:** Combines scoring speed (**Strike Rate - 50%**) and consistency (**Average - 50%**) at a specific stadium.
    * **🎯 Bowlers:** Combines run containment (**Economy Rate - 60%**) and wicket-taking frequency (**Bowling SR - 40%**).
    """)

# ----------------------------------------------------
# Step 0: Filter Dataset based on View Mode
# ----------------------------------------------------
df_venue = ball2ball_data.copy()
if "view_mode" in locals() and view_mode == "Year-Wise Top 20":
    df_venue = df_venue[df_venue["year"] == selected_year]

if not df_venue.empty:

    # ----------------------------------------------------
    # Step 1: Venue Selection & Role Toggle
    # ----------------------------------------------------
    top_venues = df_venue["venue"].value_counts().index.tolist()

    col_v1, col_v2 = st.columns([2, 1])
    with col_v1:
        selected_venue = st.selectbox(
            "Select Venue / Stadium",
            options=top_venues,
            key="venue_select_box"
        )
    with col_v2:
        specialist_role = st.radio(
            "Select Category",
            options=["Batting Specialists", "Bowling Specialists"],
            horizontal=True,
            key="venue_role_radio"
        )

    # Filter data for selected venue
    v_data = df_venue[df_venue["venue"] == selected_venue].copy()

    # Dynamic qualification thresholds (All-Time vs Single Year)
    is_all_time = ("view_mode" in locals() and view_mode == "All-Time Top 20")
    min_balls_bat = 60 if is_all_time else 20
    min_balls_bowl = 60 if is_all_time else 24

    # ====================================================
    # BATTING VENUE SPECIALISTS
    # ====================================================
    if specialist_role == "Batting Specialists":
        bat_summary = (
            v_data.groupby("batter")
            .agg(
                Innings=("match_id", "nunique"),
                Runs=("runs_batter", "sum"),
                Balls=("valid_ball", "sum"),
                Dismissals=("player_out", lambda x: x.notna().sum()),
                Fours=("runs_batter", lambda x: (x == 4).sum()),
                Sixes=("runs_batter", lambda x: (x == 6).sum()),
            )
            .reset_index()
        )

        # Filter by qualification threshold
        bat_summary = bat_summary[bat_summary["Balls"] >= min_balls_bat].copy()

        if not bat_summary.empty:
            bat_summary["SR"] = ((bat_summary["Runs"] / bat_summary["Balls"]) * 100).round(2)
            bat_summary["Avg"] = (bat_summary["Runs"] / bat_summary["Dismissals"].replace(0, 1)).round(2)
            bat_summary["Venue_Index"] = ((bat_summary["SR"] * 0.5) + (bat_summary["Avg"] * 0.5)).round(1)

            bat_summary = bat_summary.sort_values(by="Venue_Index", ascending=False).reset_index(drop=True)
            bat_summary["Rank"] = bat_summary.index + 1

            # Top N Slider
            max_bats = len(bat_summary)
            top_n_bat = st.slider("Display Top Batters", 5, min(25, max_bats), min(10, max_bats), step=5, key="top_n_venue_bat")
            top_bats_df = bat_summary.head(top_n_bat).copy()

            # Top 3 Podium Cards
            st.markdown(f"### 🏆 Top Batters at {selected_venue}")
            podium_cols = st.columns(min(3, len(top_bats_df)))
            border_colors = ["#FFD700", "#C0C0C0", "#CD7F32"]
            medals = ["🥇 1st Place", "🥈 2nd Place", "🥉 3rd Place"]

            for i in range(min(3, len(top_bats_df))):
                row = top_bats_df.iloc[i]
                with podium_cols[i]:
                    st.markdown(
                        f"""
                        <div style="background-color: #FFFFFF; border: 1px solid #E5E7EB; border-top: 5px solid {border_colors[i]}; border-radius: 10px; padding: 14px; text-align: center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
                            <span style="font-size: 12px; font-weight: 700; color: #6B7280;">{medals[i]}</span>
                            <h4 style="margin: 4px 0 2px 0; font-size: 18px; color: #111827;">{row['batter']}</h4>
                            <div style="font-size: 26px; font-weight: 800; color: #2563EB;">{row['Venue_Index']} <span style="font-size: 12px; color: #6B7280;">Pts</span></div>
                            <div style="font-size: 12px; color: #4B5563; margin-top: 6px;">
                                🏏 <b>{row['Runs']}</b> Runs &nbsp;|&nbsp; ⚡ <b>{row['SR']}</b> SR &nbsp;|&nbsp; 📊 <b>{row['Avg']}</b> Avg
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

            st.markdown("<br>", unsafe_allow_html=True)

            # Clean Bar Chart
            st.markdown("### 📊 Venue Performance Index Leaderboard")
            chart_df = top_bats_df.iloc[::-1].copy()

            fig_bat = go.Figure(go.Bar(
                y=chart_df['batter'],
                x=chart_df['Venue_Index'],
                orientation='h',
                marker=dict(
                    color=chart_df['Venue_Index'],
                    colorscale='Blues',
                    showscale=False,
                    cornerradius=4
                ),
                text=[f"  <b>{v:.1f} Pts</b>" for v in chart_df['Venue_Index']],
                textposition='outside',
                textfont=dict(size=12, color='#1E40AF'),
                customdata=chart_df[['Runs', 'SR', 'Avg', 'Innings', 'Balls']].values,
                hovertemplate=(
                    "<b>%{y}</b><br><br>" +
                    "📈 <b>Venue Index:</b> %{x:.1f} Pts<br>" +
                    "🏏 <b>Runs:</b> %{customdata[0]} (%{customdata[3]} Innings, %{customdata[4]} Balls)<br>" +
                    "⚡ <b>Strike Rate:</b> %{customdata[1]:.2f}<br>" +
                    "📊 <b>Average:</b> %{customdata[2]:.2f}<extra></extra>"
                )
            ))

            max_pts = chart_df['Venue_Index'].max()
            fig_bat.update_layout(
                height=max(350, top_n_bat * 34),
                margin=dict(l=20, r=60, t=10, b=30),
                xaxis=dict(title='Venue Index Score', showgrid=True, gridcolor='#F3F4F6', range=[0, max_pts * 1.18]),
                yaxis=dict(showgrid=False, tickfont=dict(size=13, color='#111827', weight='bold')),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_bat, use_container_width=True)

            # Data Table
            with st.expander("📄 View Full Batting Leaderboard Table"):
                st.dataframe(
                    top_bats_df[['Rank', 'batter', 'Innings', 'Runs', 'Balls', 'SR', 'Avg', 'Venue_Index']].rename(
                        columns={'batter': 'Batter Name', 'SR': 'Strike Rate', 'Venue_Index': 'Venue Index'}
                    ),
                    use_container_width=True,
                    hide_index=True
                )
        else:
            st.info(f"No batters met the minimum qualification threshold of {min_balls_bat} balls faced at {selected_venue}.")

    # ====================================================
    # BOWLING VENUE SPECIALISTS
    # ====================================================
    else:
        bowl_summary = (
            v_data.groupby("bowler")
            .agg(
                Innings=("match_id", "nunique"),
                Runs_Conceded=("runs_bowler", "sum"),
                Balls_Bowled=("valid_ball", "sum"),
                Wickets=("bowler_wicket", "sum"),
            )
            .reset_index()
        )

        # Filter by qualification threshold
        bowl_summary = bowl_summary[bowl_summary["Balls_Bowled"] >= min_balls_bowl].copy()

        if not bowl_summary.empty:
            bowl_summary["Economy"] = ((bowl_summary["Runs_Conceded"] / bowl_summary["Balls_Bowled"]) * 6).round(2)
            
            # Bowling SR = Balls per Wicket
            bowl_summary["Bowling_SR"] = np.where(
                bowl_summary["Wickets"] > 0,
                (bowl_summary["Balls_Bowled"] / bowl_summary["Wickets"]).round(2),
                bowl_summary["Balls_Bowled"]
            )

            # Bowler Venue Index
            bowl_summary["Venue_Index"] = (
                ((100 / bowl_summary["Economy"].replace(0, 1)) * 0.6) + 
                ((100 / bowl_summary["Bowling_SR"].replace(0, 1)) * 0.4)
            ).round(1)

            bowl_summary = bowl_summary.sort_values(by="Venue_Index", ascending=False).reset_index(drop=True)
            bowl_summary["Rank"] = bowl_summary.index + 1

            # Top N Slider
            max_bowls = len(bowl_summary)
            top_n_bowl = st.slider("Display Top Bowlers", 5, min(25, max_bowls), min(10, max_bowls), step=5, key="top_n_venue_bowl")
            top_bowls_df = bowl_summary.head(top_n_bowl).copy()

            # Top 3 Podium Cards
            st.markdown(f"### 🏆 Top Bowlers at {selected_venue}")
            podium_cols_b = st.columns(min(3, len(top_bowls_df)))
            border_colors = ["#FFD700", "#C0C0C0", "#CD7F32"]
            medals = ["🥇 1st Place", "🥈 2nd Place", "🥉 3rd Place"]

            for i in range(min(3, len(top_bowls_df))):
                row = top_bowls_df.iloc[i]
                with podium_cols_b[i]:
                    st.markdown(
                        f"""
                        <div style="background-color: #FFFFFF; border: 1px solid #E5E7EB; border-top: 5px solid {border_colors[i]}; border-radius: 10px; padding: 14px; text-align: center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
                            <span style="font-size: 12px; font-weight: 700; color: #6B7280;">{medals[i]}</span>
                            <h4 style="margin: 4px 0 2px 0; font-size: 18px; color: #111827;">{row['bowler']}</h4>
                            <div style="font-size: 26px; font-weight: 800; color: #7C3AED;">{row['Venue_Index']} <span style="font-size: 12px; color: #6B7280;">Pts</span></div>
                            <div style="font-size: 12px; color: #4B5563; margin-top: 6px;">
                                🎯 <b>{row['Wickets']}</b> Wkts &nbsp;|&nbsp; 📉 <b>{row['Economy']}</b> Eco &nbsp;|&nbsp; ⚡ <b>{row['Bowling_SR']}</b> Bowl SR
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

            st.markdown("<br>", unsafe_allow_html=True)

            # Clean Bar Chart
            st.markdown("### 📊 Venue Performance Index Leaderboard")
            chart_bowl_df = top_bowls_df.iloc[::-1].copy()

            fig_bowl = go.Figure(go.Bar(
                y=chart_bowl_df['bowler'],
                x=chart_bowl_df['Venue_Index'],
                orientation='h',
                marker=dict(
                    color=chart_bowl_df['Venue_Index'],
                    colorscale='Purples',
                    showscale=False,
                    cornerradius=4
                ),
                text=[f"  <b>{v:.1f} Pts</b>" for v in chart_bowl_df['Venue_Index']],
                textposition='outside',
                textfont=dict(size=12, color='#5B21B6'),
                customdata=chart_bowl_df[['Wickets', 'Economy', 'Bowling_SR', 'Innings', 'Balls_Bowled', 'Runs_Conceded']].values,
                hovertemplate=(
                    "<b>%{y}</b><br><br>" +
                    "📈 <b>Venue Index:</b> %{x:.1f} Pts<br>" +
                    "🎯 <b>Wickets:</b> %{customdata[0]} (%{customdata[3]} Innings, %{customdata[4]} Balls)<br>" +
                    "📉 <b>Economy Rate:</b> %{customdata[1]:.2f}<br>" +
                    "⚡ <b>Bowling Strike Rate:</b> %{customdata[2]:.2f} balls/wkt<extra></extra>"
                )
            ))

            max_pts_b = chart_bowl_df['Venue_Index'].max()
            fig_bowl.update_layout(
                height=max(350, top_n_bowl * 34),
                margin=dict(l=20, r=60, t=10, b=30),
                xaxis=dict(title='Venue Index Score', showgrid=True, gridcolor='#F3F4F6', range=[0, max_pts_b * 1.18]),
                yaxis=dict(showgrid=False, tickfont=dict(size=13, color='#111827', weight='bold')),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_bowl, use_container_width=True)

            # Data Table
            with st.expander("📄 View Full Bowling Leaderboard Table"):
                st.dataframe(
                    top_bowls_df[['Rank', 'bowler', 'Innings', 'Wickets', 'Balls_Bowled', 'Runs_Conceded', 'Economy', 'Bowling_SR', 'Venue_Index']].rename(
                        columns={
                            'bowler': 'Bowler Name',
                            'Balls_Bowled': 'Balls Bowled',
                            'Runs_Conceded': 'Runs Conceded',
                            'Economy': 'Economy Rate',
                            'Bowling_SR': 'Bowling SR',
                            'Venue_Index': 'Venue Index'
                        }
                    ),
                    use_container_width=True,
                    hide_index=True
                )
        else:
            st.info(f"No bowlers met the minimum qualification threshold of {min_balls_bowl} balls bowled at {selected_venue}.")

else:
    st.info("No venue data available for the selected view mode / season.")