import streamlit as st
import sqlite3
import pandas as pd

def app():
    st.title("📈 Top Stats")
    st.markdown("View **top player performances** from the database.")

    # Connect to SQLite
    conn = sqlite3.connect("cricbuzz.db", check_same_thread=False)

    # Load players table only (it definitely exists)
    try:
        players_df = pd.read_sql("SELECT * FROM players", conn)
    except Exception as e:
        st.error(f"Error loading players table: {e}")
        conn.close()
        return

    conn.close()

    st.subheader("Players Table (Preview)")
    st.dataframe(players_df.head())

    # Example: show count of players by role (works with any basic schema)
    if "playing_role" in players_df.columns:
        st.subheader("Players by Role")
        role_counts = players_df["playing_role"].value_counts().reset_index()
        role_counts.columns = ["Playing Role", "Count"]
        st.bar_chart(role_counts.set_index("Playing Role"))
