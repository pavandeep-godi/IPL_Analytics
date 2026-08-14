import streamlit as st
from streamlit import *
import pandas as pd
import numpy as np
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from PIL import Image


# Save the original method reference
_original_plotly_chart = st.plotly_chart

# Define a custom wrapper with default config
def custom_plotly_chart(fig, *args, **kwargs):
    # Default config to disable mode bar
    default_config = {'displayModeBar': False}
    
    # Merge or set config
    if 'config' in kwargs and kwargs['config'] is not None:
        default_config.update(kwargs['config'])
    kwargs['config'] = default_config

    return _original_plotly_chart(fig, *args, **kwargs)

# Override Streamlit's method globally
st.plotly_chart = custom_plotly_chart


import base64
import streamlit as st

# Helper function to convert local image to base64 for HTML embedding
def get_image_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

logo_b64 = get_image_base64("IPL_LOGO.jpg")

st.markdown(f"""
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
""", unsafe_allow_html=True)


ball2ball_data=pd.read_csv("ball2ball_df.csv")


st.markdown("For the below analytics, use the settings in the lef side of the page")


st.set_page_config(page_title="IPL Auction Intelligence Hub", layout="wide")
st.title("🎯 IPL Auction Intelligence & Scouting Hub")

# Main Section Tabs
tab_batting, tab_bowling, tab_wk = st.tabs(
    ["🏏 Batter Analytics", "⚡ Bowler Analytics", "🧤 WK-Batter Analytics"]
)

# Shared View Mode Control
st.sidebar.header("⚙️ Global Controls")
view_mode = st.sidebar.radio("View Mode", ["All-Time Top 20", "Year-Wise Top 20"])

if view_mode == "Year-Wise Top 20":
    selected_year = st.sidebar.selectbox(
        "Select Year", sorted(ball2ball_data["year"].unique(), reverse=True)
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
                Dismissals=(
                    "player_out",
                    lambda x: (x.notna()).sum() if "player_out" in x else 0,
                ),
            )
            .reset_index()
        )

        min_balls = 100 if view_mode == "All-Time Top 20" else 50
        stats = stats[stats["Balls_Faced"] >= min_balls]

        stats["Strike Rate"] = ((stats["Runs"] / stats["Balls_Faced"]) * 100).round(2)
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

        stats["Strike Rate"] = ((stats["Runs"] / stats["Balls_Faced"]) * 100).round(2)
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

        stats["Strike Rate"] = ((stats["Runs"] / stats["Balls_Faced"]) * 100).round(2)
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

        stats["Strike Rate"] = ((stats["Total_Runs"] / stats["Balls_Faced"]) * 100).round(2)

        bankable = stats[(stats["Total_Runs"] >= 400) & (stats["Strike Rate"] >= 150.0)]

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

        stats["Economy Rate"] = (stats["Runs_Conceded"] / (stats["Legal_Balls"] / 6)).round(2)
        stats["Dot Ball %"] = ((stats["Dot_Balls"] / stats["Legal_Balls"]) * 100).round(2)

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

        stats["Economy Rate"] = (stats["Runs_Conceded"] / (stats["Legal_Balls"] / 6)).round(2)
        stats["Bowling Avg"] = (stats["Runs_Conceded"] / stats["Wickets"].replace(0, 1)).round(2)

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

        stats["Economy Rate"] = (stats["Runs_Conceded"] / (stats["Legal_Balls"] / 6)).round(2)

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

        stats["Economy Rate"] = (stats["Runs_Conceded"] / (stats["Legal_Balls"] / 6)).round(2)
        stats["Dot Ball %"] = ((stats["Dot_Balls"] / stats["Legal_Balls"]) * 100).round(2)

        top_20 = stats.sort_values(by="Economy Rate", ascending=True).head(20)
        top_20.rename(columns={"bowler": "Bowler", "year": "Year"}, inplace=True)
        st.dataframe(top_20, hide_index=True, use_container_width=True)


# ==============================================================================
# SECTION 3: WICKETKEEPER-BATTER ANALYTICS
# ==============================================================================
with tab_wk:
    st.header("🧤 Wicketkeeper-Batter Analysis (2008–2026)")

    # Master list of IPL Wicketkeepers
    ipl_wicketkeepers = {
        "MS Dhoni", "Dinesh Karthik", "Wriddhiman Saha", "Robin Uthappa", "Parthiv Patel", 
        "Naman Ojha", "Adam Gilchrist", "Kumar Sangakkara", "Brendon McCullum", "Mark Boucher",
        "AB de Villiers", "Kamran Akmal", "Tatenda Taibu", "Luke Ronchi", "Manvinder Bisla",
        "CM Gautam", "Aditya Tare", "Eknath Kerkar", "Shreevats Goswami", "Mahesh Rawat",
        "Pinal Shah", "Yogesh Takawale", "Ambati Rayudu", "Rishabh Pant", "Sanju Samson",
        "KL Rahul", "Ishan Kishan", "Jitesh Sharma", "Dhruv Jurel", "Prabhsimran Singh",
        "Anuj Rawat", "Abhishek Porel", "Vishnu Vinod", "KS Bharat", "Kumar Kushagra",
        "Robin Minz", "Aryan Juyal", "Kunal Rathore", "Luvnith Sisodia", "Sheldon Jackson",
        "Baba Indrajith", "Upendra Yadav", "Urvil Patel", "Vansh Bedi", "Shrijith Krishnan",
        "Jos Buttler", "Quinton de Kock", "Nicholas Pooran", "Heinrich Klaasen", "Phil Salt",
        "Tristan Stubbs", "Devon Conway", "Rahmanullah Gurbaz", "Josh Inglis", "Ryan Rickelton",
        "Shai Hope", "Donovan Ferreira", "Matthew Wade", "Tim Seifert", "Sam Billings",
        "Alex Carey", "Ben McDermott", "Glenn Phillips", "Peter Handscomb", "Finn Allen"
    }

    selected_position = st.slider(
        "Filter Batting Position Range (e.g., Positions 1 to 8)",
        min_value=1,
        max_value=8,
        value=(1, 8),
    )

    # Filter dataframe strictly for designated keepers batting within the selected position range
    df_wk = ball2ball_data[
        (ball2ball_data["batter"].isin(ipl_wicketkeepers)) &
        (ball2ball_data["bat_pos"] >= selected_position[0]) &
        (ball2ball_data["bat_pos"] <= selected_position[1])
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

    wk_stats["Strike Rate"] = ((wk_stats["Runs"] / wk_stats["Balls_Faced"]) * 100).round(2)
    wk_stats["Average"] = (
        wk_stats["Runs"] / wk_stats["Dismissals"].replace(0, 1)
    ).round(2)
    wk_stats["Avg_Batting_Pos"] = wk_stats["Avg_Batting_Pos"].round(1)

    top_20 = wk_stats.sort_values(
        by=["Runs", "Strike Rate"], ascending=[False, False]
    ).head(20)
    top_20.rename(
        columns={"batter": "Wicketkeeper", "year": "Year", "Avg_Batting_Pos": "Avg Pos"},
        inplace=True,
    )

    st.subheader(f"Top Wicketkeepers (Batting Positions {selected_position[0]}–{selected_position[1]})")
    st.dataframe(top_20, hide_index=True, use_container_width=True)



# ==========================================
# HELPER: Modern Horizontal Progress Bar
# ==========================================
def create_modern_progress_bar(value, target, label, color):
    """
    Creates a sleek, modern horizontal progress bar using Plotly.
    """
    fig = go.Figure()
    
    # Background track (Gray)
    fig.add_trace(go.Bar(
        y=[label], x=[target],
        orientation='h',
        marker=dict(color='#E5E7EB', cornerradius=6),
        hoverinfo='none',
        showlegend=False
    ))
    
    # Active progress track
    fig.add_trace(go.Bar(
        y=[label], x=[value],
        orientation='h',
        marker=dict(color=color, cornerradius=6),
        text=[f" <b>{value} Matches</b>"],
        textposition='inside',
        insidetextanchor='start',
        textfont=dict(color='white', size=14),
        hoverinfo='x',
        showlegend=False
    ))

    fig.update_layout(
        barmode='overlay',
        height=60,
        margin=dict(l=0, r=20, t=5, b=5),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[0, max(target, value + 5)]),
        yaxis=dict(showgrid=False, zeroline=False, tickfont=dict(size=14, color='#374151')),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig


# ==========================================
# ALL-ROUNDERS SECTION (Filter-Aware)
# ==========================================
st.markdown("---")
st.title("⚡ Top All-Rounders Performance")

# ----------------------------------------------------
# Step 0: Apply View Mode Filter (All-Time vs Year-Wise)
# ----------------------------------------------------
df_allround = ball2ball_data.copy()
if 'view_mode' in locals() and view_mode == "Year-Wise Top 20":
    df_allround = df_allround[df_allround["year"] == selected_year]

# Dynamic thresholds based on view mode
is_year_wise = ('view_mode' in locals() and view_mode == "Year-Wise Top 20")
MIN_RUNS = 15 if is_year_wise else 50
MIN_WICKETS = 2 if is_year_wise else 5

# ----------------------------------------------------
# Step 1: Filter Dataset to Find Qualified All-Rounders
# ----------------------------------------------------
batting_totals = df_allround.groupby('batter')['runs_batter'].sum()
bowling_totals = df_allround.groupby('bowler')['bowler_wicket'].sum()

allrounder_batters = batting_totals[batting_totals >= MIN_RUNS].index
allrounder_bowlers = bowling_totals[bowling_totals >= MIN_WICKETS].index

allrounders_options = sorted(list(set(allrounder_batters).intersection(set(allrounder_bowlers))))

if not allrounders_options:
    st.info("No all-rounders met the threshold for the currently selected filter.")
else:
    # Selectbox showing qualified all-rounders
    selected_allrounder = st.selectbox(
        label=f'Select All-Rounder ({len(allrounders_options)} players qualified)', 
        options=allrounders_options,
        key="allrounder_selectbox"
    )

    if st.button("Analyze All-Rounder Impact", key="allrounder_btn"):
        
        # ----------------------------------------------------
        # Step 2: Calculate Match-by-Match Batting Stats
        # ----------------------------------------------------
        group_cols_bat = ['match_id', 'batting_team', 'bowling_team']
        if 'year' in df_allround.columns:
            group_cols_bat.append('year')

        batter_matches = df_allround[df_allround['batter'] == selected_allrounder].groupby(
            group_cols_bat
        ).agg(
            runs_scored=('runs_batter', 'sum'),
            balls_faced=('runs_batter', 'count')
        ).reset_index()

        # ----------------------------------------------------
        # Step 3: Calculate Match-by-Match Bowling Stats
        # ----------------------------------------------------
        bowler_matches = df_allround[df_allround['bowler'] == selected_allrounder].groupby(
            'match_id'
        ).agg(
            wickets_taken=('bowler_wicket', 'sum'),
            runs_conceded=('runs_bowler', 'sum'),
            balls_bowled=('valid_ball', 'sum')
        ).reset_index()

        # ----------------------------------------------------
        # Step 4: Merge Batting & Bowling Stats per Match
        # ----------------------------------------------------
        match_perf = pd.merge(
            batter_matches, 
            bowler_matches, 
            on='match_id', 
            how='outer'
        ).fillna(0)

        # ----------------------------------------------------
        # Step 5: Categorize the 3 Contribution Types
        # ----------------------------------------------------
        dual_impact_df = match_perf[(match_perf['runs_scored'] >= 20) & (match_perf['wickets_taken'] >= 1)].copy()
        dual_impact_count = len(dual_impact_df)

        batting_impact_df = match_perf[match_perf['runs_scored'] >= 30]
        batting_impact_count = len(batting_impact_df)

        bowling_impact_df = match_perf[match_perf['wickets_taken'] >= 2]
        bowling_impact_count = len(bowling_impact_df)

        # Career / Selected Scope Totals
        total_runs = int(match_perf['runs_scored'].sum())
        total_wickets = int(match_perf['wickets_taken'].sum())

        # ----------------------------------------------------
        # Step 6: High-Level Metric Cards
        # ----------------------------------------------------
        col1, col2 = st.columns(2)
        col1.metric("Total Runs", f"{total_runs:,}")
        col2.metric("Total Wickets", f"{total_wickets:,}")

        st.markdown("### 📊 Contribution Impact Breakdown")

        # ----------------------------------------------------
        # Step 7: Render Modern Horizontal Progress Bars
        # ----------------------------------------------------
        max_target_dual = 10 if is_year_wise else 25
        max_target_single = 15 if is_year_wise else 40

        st.caption("🔥 **Type 1: Same-Match Dual Impact** (20+ Runs AND 1+ Wicket)")
        st.plotly_chart(
            create_modern_progress_bar(dual_impact_count, max_target_dual, "Dual Impact", "#2563EB"), 
            use_container_width=True
        )

        st.caption("🏏 **Type 2: Key Batting Contribution** (30+ Runs Scored)")
        st.plotly_chart(
            create_modern_progress_bar(batting_impact_count, max_target_single, "Batting Impact", "#16A34A"), 
            use_container_width=True
        )

        st.caption("⚾ **Type 3: Key Bowling Contribution** (2+ Wickets Taken)")
        st.plotly_chart(
            create_modern_progress_bar(bowling_impact_count, max_target_single, "Bowling Impact", "#DC2626"), 
            use_container_width=True
        )

        # ----------------------------------------------------
        # Step 8: Detailed Informative Table
        # ----------------------------------------------------
        with st.expander("📄 View Dual Impact Match Details"):
            if dual_impact_count > 0:
                if 'year' in dual_impact_df.columns:
                    dual_impact_df['year'] = dual_impact_df['year'].astype(int)
                dual_impact_df['runs_scored'] = dual_impact_df['runs_scored'].astype(int)
                dual_impact_df['balls_faced'] = dual_impact_df['balls_faced'].astype(int)
                dual_impact_df['wickets_taken'] = dual_impact_df['wickets_taken'].astype(int)
                dual_impact_df['runs_conceded'] = dual_impact_df['runs_conceded'].astype(int)

                cols_to_display = ['batting_team', 'bowling_team', 'runs_scored', 'balls_faced', 'wickets_taken', 'runs_conceded']
                rename_dict = {
                    'batting_team': 'Team',
                    'bowling_team': 'Opponent',
                    'runs_scored': 'Runs Scored',
                    'balls_faced': 'Balls Faced',
                    'wickets_taken': 'Wickets Taken',
                    'runs_conceded': 'Runs Conceded'
                }

                if 'year' in dual_impact_df.columns:
                    cols_to_display.insert(0, 'year')
                    rename_dict['year'] = 'Season'

                display_df = dual_impact_df[cols_to_display].rename(columns=rename_dict)
                st.dataframe(display_df, use_container_width=True, hide_index=True)
            else:
                st.info("No dual-impact matches found for this player matching the threshold.")

