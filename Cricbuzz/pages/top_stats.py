import streamlit as st
import sqlite3
import pandas as pd

def app():
    st.title("📈 Top Player Stats")
    st.markdown("Simple view of top players from the `players` table in `cricbuzz.db`.")

    # Connect to DB
    try:
        
        conn = sqlite3.connect("cricbuzz.db", check_same_thread=False)

        # ✅ Generic query: works with any players schema
        df = pd.read_sql("SELECT * FROM players LIMIT 50;", conn)

        st.subheader("Players (first 50 rows)")
        st.dataframe(df, use_container_width=True)

    except Exception as e:
        st.error(f"Error loading data from database: {e}")

        return
    finally:
        conn.close()