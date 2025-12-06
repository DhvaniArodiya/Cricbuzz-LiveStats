import streamlit as st

from pages import live_matches, sql_queries, top_stats, crud_operations

# --- STYLING ---
st.markdown("""
    <style>
    .main-title {
        text-align:center;
        font-size:2.2em;
        font-weight:bold;
        color:white;
        padding:1rem;
        border-radius:12px;
        background: linear-gradient(90deg, #f87171, #f59e0b);
    }
    .card {
        background:#1e293b;
        padding:1rem;
        border-radius:1rem;
        text-align:center;
        color:white;
        cursor:pointer;
        transition:0.3s;
        font-size:1.1em;
        margin-bottom:1rem;
    }
    .card:hover {
        background:#334155;
        transform:scale(1.05);
    }
    </style>
""", unsafe_allow_html=True)


# --- SIDEBAR NAVIGATION ---
st.sidebar.title("📌 Navigation")
page = st.sidebar.radio(
    "Go to",
    ["Home", "Live Matches", "SQL Queries", "Top Stats", "CRUD Operations"]
)


# --- DASHBOARD INTERACTIVE CARDS (on Home) ---
if page == "Home":
    st.markdown("<div class='main-title'>🏏 Cricbuzz Analytics Dashboard</div>", unsafe_allow_html=True)

    st.write("### 📂 Project Structure")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("📊 Live Scorecard"):
            page = "Live Matches"
        if st.button("🧑‍🤝‍🧑 Player Analytics (CRUD)"):
            page = "CRUD Operations"

    with col2:
        if st.button("📈 Top Stats"):
            page = "Top Stats"
        if st.button("🗄️ SQL Queries"):
            page = "SQL Queries"

    st.markdown("---")
    st.markdown("""
        Explore every module:
        - 🟢 Live Scorecard → Real-time scores and analytics  
        - 📊 Player Analytics & CRUD → Manage, visualize, and explore player data  
        - 🧮 SQL Analytics → Run SQL queries on cricket datasets  
        - ⚙️ CRUD Operations → Add / Update / Delete player database  
    """)
    st.success(" Navigate using the sidebar or the buttons above!")


# --- PAGE ROUTER ---
if page == "Live Matches":
    live_matches.app()
elif page == "SQL Queries":
    sql_queries.app()
elif page == "Top Stats":
    top_stats.app()
elif page == "CRUD Operations":
    crud_operations.app()
