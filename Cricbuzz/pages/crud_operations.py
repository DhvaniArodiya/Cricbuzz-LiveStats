import pandas as pd
import streamlit as st
import sqlite3

def get_connection():
    return sqlite3.connect("cricbuzz.db")

def app():
    st.title("⚙️ CRUD Operations")
    st.markdown("Manage player database: Add, update, or delete player records.")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            runs INTEGER,
            matches INTEGER,
            team TEXT
        );
    """)
    conn.commit()

    with st.form("add_player_form"):
        name = st.text_input("Player Name")
        runs = st.number_input("Runs", min_value=0, step=1)
        matches = st.number_input("Matches", min_value=0, step=1)
        team = st.text_input("Team")
        submitted = st.form_submit_button("Add Player")
        if submitted:
            cursor.execute("INSERT INTO players (name, runs, matches, team) VALUES (?, ?, ?, ?)",
                           (name, runs, matches, team))
            conn.commit()
            st.success(f"Added player {name}")

    st.subheader("Player Records")
    df = pd.read_sql("SELECT * FROM players", conn)
    st.dataframe(df)

    delete_id = st.number_input("Enter Player ID to Delete", min_value=1, step=1)
    if st.button("Delete Player"):
        cursor.execute("DELETE FROM players WHERE id = ?", (delete_id,))
        conn.commit()
        st.success(f"Deleted player ID {delete_id}")

    conn.close()
