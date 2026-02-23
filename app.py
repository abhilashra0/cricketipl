import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Cricket Player Performance Dashboard", layout="wide")

# -----------------------------
# Load Data
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("cricket_data_2025.csv")

    # Replace "No stats" with NaN
    df.replace("No stats", None, inplace=True)

    # Convert numeric columns
    numeric_cols = [
        "Year","Runs_Scored","Batting_Average","Batting_Strike_Rate",
        "Centuries","Half_Centuries","Fours","Sixes",
        "Wickets_Taken","Economy_Rate","Bowling_Average"
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df.dropna(subset=["Year"], inplace=True)

    return df

df = load_data()

# -----------------------------
# Title + Objective
# -----------------------------
st.title("🏏 Cricket Player Performance Dashboard")

st.write("""
**Analytical Objective:**  
Analyze cricket player performance trends across years using batting and bowling metrics 
to identify top performers and performance patterns.
""")

# -----------------------------
# Sidebar Filters
# -----------------------------
st.sidebar.header("Filters")

players = st.sidebar.multiselect(
    "Select Player",
    df["Player_Name"].unique(),
    default=df["Player_Name"].unique()[:5]
)

years = st.sidebar.slider(
    "Select Year Range",
    int(df["Year"].min()),
    int(df["Year"].max()),
    (int(df["Year"].min()), int(df["Year"].max()))
)

filtered = df[
    (df["Player_Name"].isin(players)) &
    (df["Year"].between(years[0], years[1]))
]

# -----------------------------
# Metric Cards
# -----------------------------
col1, col2, col3 = st.columns(3)

col1.metric("Total Runs", int(filtered["Runs_Scored"].sum()))
col2.metric("Total Wickets", int(filtered["Wickets_Taken"].sum()))
col3.metric("Average Strike Rate", round(filtered["Batting_Strike_Rate"].mean(),2))

# -----------------------------
# Tabs
# -----------------------------
tab1, tab2 = st.tabs(["📈 Batting Analysis", "🎯 Bowling Analysis"])

# ====================================================
# TAB 1 — Batting
# ====================================================
with tab1:

    st.subheader("Batting Performance")

    # Line chart
    fig1 = px.line(
        filtered,
        x="Year",
        y="Runs_Scored",
        color="Player_Name",
        title="Runs Scored Over Years"
    )
    st.plotly_chart(fig1, use_container_width=True)

    # Bar chart
    top_runs = filtered.groupby("Player_Name")["Runs_Scored"].sum().reset_index()
    fig2 = px.bar(top_runs, x="Player_Name", y="Runs_Scored", title="Total Runs by Player")
    st.plotly_chart(fig2, use_container_width=True)

    # Scatter plot
    fig3 = px.scatter(
        filtered,
        x="Batting_Average",
        y="Batting_Strike_Rate",
        color="Player_Name",
        size="Runs_Scored",
        title="Batting Average vs Strike Rate"
    )
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("""
### Interpretation
- The line chart shows how players' run production changes over time.
- The scatter plot reveals the relationship between batting consistency (average) and scoring speed (strike rate).
- Players with both high strike rate and high average demonstrate superior batting performance.
""")

# ====================================================
# TAB 2 — Bowling
# ====================================================
with tab2:

    st.subheader("Bowling Performance")

    # Bar chart
    wickets = filtered.groupby("Player_Name")["Wickets_Taken"].sum().reset_index()
    fig4 = px.bar(wickets, x="Player_Name", y="Wickets_Taken", title="Total Wickets by Player")
    st.plotly_chart(fig4, use_container_width=True)

    # Heatmap
    heat = filtered.pivot_table(
        values="Wickets_Taken",
        index="Player_Name",
        columns="Year",
        aggfunc="sum"
    ).fillna(0)

    fig5 = px.imshow(heat, title="Wickets Heatmap (Player vs Year)")
    st.plotly_chart(fig5, use_container_width=True)

    st.markdown("""
### Interpretation
- The bar chart highlights the most effective bowlers by total wickets.
- The heatmap reveals seasonal bowling performance patterns.
- Players with consistently high wickets across years show strong bowling reliability.
""")
