import streamlit as st
import sqlite3
import pandas as pd

def app():
    st.title("📈 Top Player Stats")
    st.markdown("Simple view of top players from the `players` table in `cricbuzz.db`.")

    # Connect to DB
    try:
        conn = sqlite3.connect("cricbuzz.db", check_same_thread=False)
        query = """
            SELECT 
                full_name,
                country,
                playing_role,
                batting_style,
                bowling_style
            FROM players
            ORDER BY full_name
            LIMIT 50;
        """
        df = pd.read_sql(query, conn)
    except Exception as e:
        st.error(f"Error loading data from database: {e}")
        return
    finally:
        conn.close()

    if df.empty:
        st.warning("No player data found in the database.")
    else:
        st.subheader("Players (sample)")
        # ✅ No custom width, no weird values
        st.dataframe(df)   # <- keep this simple
