import streamlit as st
import pandas as pd
import sqlite3

# Create a cached DB connection, thread-safe
@st.cache_resource
def get_connection():
    return sqlite3.connect("cricbuzz.db", check_same_thread=False)

def app():
    st.title("🧮 SQL Queries Explorer")

    # Dictionary of all SQL queries
    # --- in pages/sql_queries.py ---

queries = {
    "Q1: Players from India": """
        SELECT
            full_name,
            playing_role,
            batting_style,
            bowling_style
        FROM players
        WHERE country = 'India';
    """,

    "Q2: Matches played in last 30 days": """
        SELECT
            m.match_desc,
            t1.team_name AS team1,
            t2.team_name AS team2,
            v.venue_name || ', ' || v.city AS venue,
            m.match_date
        FROM matches m
        JOIN teams  t1 ON m.team1_id  = t1.team_id
        JOIN teams  t2 ON m.team2_id  = t2.team_id
        JOIN venues v  ON m.venue_id  = v.venue_id
        WHERE m.match_date >= DATE('now','-30 day')
        ORDER BY m.match_date DESC;
    """,

    "Q3: Top 10 highest ODI run scorers": """
        SELECT
            p.full_name,
            s.runs,
            s.batting_average,
            s.centuries
        FROM player_format_summary s
        JOIN players p ON p.player_id = s.player_id
        WHERE s.format = 'ODI'
        ORDER BY s.runs DESC
        LIMIT 10;
    """,

    "Q4: Venues with capacity > 50,000": """
        SELECT
            venue_name,
            city,
            country,
            capacity
        FROM venues
        WHERE capacity > 50000
        ORDER BY capacity DESC;
    """,

    "Q5: Matches won by each team": """
        SELECT
            t.team_name,
            COUNT(*) AS total_wins
        FROM matches m
        JOIN teams t ON m.winner_team_id = t.team_id
        GROUP BY t.team_id, t.team_name
        ORDER BY total_wins DESC;
    """,

    "Q6: Players count by playing role": """
        SELECT
            playing_role,
            COUNT(*) AS player_count
        FROM players
        GROUP BY playing_role
        ORDER BY player_count DESC;
    """,

    "Q7: Highest individual batting score per format": """
        SELECT
            m.match_type AS format,          
            MAX(b.runs) AS highest_runs
        FROM batting_scorecard b
        JOIN innings i ON b.innings_id = i.innings_id
        JOIN matches m ON i.match_id   = m.match_id
        GROUP BY m.match_type;
    """,

    "Q8: Series started in 2024": """
        SELECT
            series_name,
            host_country,
            match_type,
            start_date,
            total_matches
        FROM series
        WHERE strftime('%Y', start_date) = '2024';
    """,
    # ---------- your existing intermediate / advanced queries ----------
    "Q9: Player performance comparison across formats": """
        WITH batting_stats AS (
            SELECT
                player_id,
                COALESCE(SUM(CASE WHEN format = 'Test' THEN runs ELSE 0 END), 0) AS test_runs,
                COALESCE(SUM(CASE WHEN format = 'ODI'  THEN runs ELSE 0 END), 0) AS odi_runs,
                COALESCE(SUM(CASE WHEN format = 'T20I' THEN runs ELSE 0 END), 0) AS t20i_runs,
                AVG(batting_average) AS overall_avg,
                COUNT(DISTINCT format) AS formats_played
            FROM player_format_summary
            GROUP BY player_id
        )
        SELECT 
            p.full_name,
            b.test_runs,
            b.odi_runs,
            b.t20i_runs,
            ROUND(b.overall_avg, 2) AS overall_avg,
            b.formats_played
        FROM batting_stats b
        JOIN players p ON p.player_id = b.player_id
        WHERE b.formats_played >= 2      -- at least 2 formats
        ORDER BY (b.test_runs + b.odi_runs + b.t20i_runs) DESC
        LIMIT 50;
    """,

    "Q10: Last 20 completed matches with details": """
        SELECT
            m.match_desc,
            t1.team_name AS team1,
            t2.team_name AS team2,
            w.team_name  AS winning_team,
            m.victory_margin,
            m.victory_type,
            v.venue_name
        FROM matches m
        JOIN teams  t1 ON m.team1_id       = t1.team_id
        JOIN teams  t2 ON m.team2_id       = t2.team_id
        JOIN teams  w  ON m.winner_team_id = w.team_id
        JOIN venues v  ON m.venue_id       = v.venue_id
        ORDER BY m.match_date DESC
        LIMIT 20;
    """,

    "Q11: Team performance home vs away": """
        SELECT
            t.team_name,
            SUM(CASE WHEN v.country = t.country
                     AND m.winner_team_id = t.team_id THEN 1 ELSE 0 END) AS home_wins,
            SUM(CASE WHEN v.country <> t.country
                     AND m.winner_team_id = t.team_id THEN 1 ELSE 0 END) AS away_wins
        FROM matches m
        JOIN teams  t ON t.team_id IN (m.team1_id, m.team2_id)
        JOIN venues v ON m.venue_id = v.venue_id
        GROUP BY t.team_id, t.team_name;
    """,

    "Q12: Players scoring 50 or more runs in an innings": """
        SELECT
            p.full_name,
            bs.innings_id,
            bs.runs
        FROM batting_scorecard bs
        JOIN players p ON bs.player_id = p.player_id
        WHERE bs.runs >= 50
        ORDER BY bs.runs DESC;
    """,

    "Q13: Top 5 bowlers with best economy rate": """
        SELECT
            p.full_name,
            CAST(s.economy_rate AS FLOAT) AS economy
        FROM player_format_summary s
        JOIN players p ON s.player_id = p.player_id
        WHERE s.economy_rate IS NOT NULL
        ORDER BY economy ASC
        LIMIT 5;
    """,

    "Q14: Top 5 batsmen with highest strike rate": """
        SELECT
            p.full_name,
            CAST(s.strike_rate AS FLOAT) AS strike_rate
        FROM player_format_summary s
        JOIN players p ON s.player_id = p.player_id
        WHERE s.strike_rate IS NOT NULL
        ORDER BY strike_rate DESC
        LIMIT 5;
    """,

    "Q15: Top 10 batsmen by batting average": """
        SELECT
            p.full_name,
            CAST(s.batting_average AS FLOAT) AS batting_average
        FROM player_format_summary s
        JOIN players p ON s.player_id = p.player_id
        WHERE s.batting_average IS NOT NULL
        ORDER BY batting_average DESC
        LIMIT 10;
    """,

    "Q16: Top 10 bowlers by bowling average": """
        SELECT
            p.full_name,
            CAST(s.bowling_average AS FLOAT) AS bowling_average
        FROM player_format_summary s
        JOIN players p ON s.player_id = p.player_id
        WHERE s.bowling_average IS NOT NULL
        ORDER BY bowling_average ASC
        LIMIT 10;
    """,

    "Q17: Players with most matches played": """
        SELECT
            p.full_name,
            s.matches
        FROM player_format_summary s
        JOIN players p ON s.player_id = p.player_id
        WHERE s.matches IS NOT NULL
        ORDER BY s.matches DESC
        LIMIT 10;
    """,

    "Q18: Best all-rounders (runs + wickets)": """
        SELECT
            p.full_name,
            s.runs,
            s.wickets,
            (s.runs + s.wickets * 25) AS allrounder_points
        FROM player_format_summary s
        JOIN players p ON s.player_id = p.player_id
        ORDER BY allrounder_points DESC
        LIMIT 10;
    """
}

    # UI: query selector
choice = st.selectbox("📌 Choose a query", list(queries.keys()), index=0)
query = queries[choice]

# Show query preview
st.subheader("🔍 SQL Query")
st.code(query, language="sql")

# Run query on button click
if st.button("▶️ Run Query"):
    conn = get_connection()
    try:
        df = pd.read_sql(query, conn)

        if df.empty:
            st.warning("⚠️ No results found for this query.")
        else:
            st.success(f"✅ Query executed successfully. {len(df)} rows returned.")
            st.dataframe(df, use_container_width=True)

            # Download option
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Download CSV", csv, "query_results.csv", "text/csv")

    except Exception as e:
        st.error(f"❌ Error running query: {e}")
        st.code(query, language="sql")
