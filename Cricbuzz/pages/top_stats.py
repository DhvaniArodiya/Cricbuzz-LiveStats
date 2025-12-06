import streamlit as st
import sqlite3
import pandas as pd

def app():
    st.set_page_config(page_title="Top Stats", page_icon="📊", layout="wide")

    st.title("📊 Top Stats")
    st.markdown("View **top performances** from ongoing matches.")

    # Connect to SQLite
    conn = sqlite3.connect("cricbuzz.db", check_same_thread=False)

    # Load tables
    players_df = pd.read_sql("SELECT * FROM players", conn)
    stats_df = pd.read_sql("SELECT * FROM player_format_summary", conn)
    fielding_df = pd.read_sql("SELECT * FROM fielding", conn)

    # Merge player stats with player info
    merged_df = stats_df.merge(players_df, on="player_id", how="left")

    # Merge fielding stats
    merged_fielding = fielding_df.groupby("player_id")["catches"].sum().reset_index()
    merged_df = merged_df.merge(merged_fielding, on="player_id", how="left")
    merged_df["catches"] = merged_df["catches"].fillna(0)

    # Sort by runs and wickets
    top_stats = merged_df.sort_values(by=["runs", "wickets"], ascending=[False, False]).head(10)

    if top_stats.empty:
        st.warning("⚠️ No stats available.")    
    else:
        st.subheader("🏏 Top Performances")
        st.dataframe(
            top_stats[["full_name", "runs", "wickets", "catches"]],
            width="stretch"
        )

    conn.close()
