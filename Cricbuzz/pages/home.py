import streamlit as st

def app():
    st.markdown("""
        <style>
        .block-container {padding-top:2rem;}
        .custom-header {background: linear-gradient(90deg,#ff5e62 0,#ff9966 100%); padding:1.3rem; border-radius:1rem;}
        .custom-card {background: #4d057c; padding:1rem; border-radius:0.75rem; margin-bottom:1rem;}
        .custom-text {color: #fff; font-size:1.1rem;}
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="custom-header"><h2 style="color:#fff;margin-bottom:0;">🏏 Cricbuzz Analytics Dashboard</h2><span style="color:#fde68a;font-weight:bold;">Project Structure</span></div>', unsafe_allow_html=True)
    col1, col2 = st.columns([1,2])

    with col1:
        st.markdown("""
        <div class="custom-card custom-text">
            <b>📁 Live Scorecard</b><br><span style="color:#fde68a;">Real-time scores and analytics.</span>
        </div>
        <div class="custom-card custom-text">
            <b>📁 Player Analytics CRUD page</b><br><span style="color:#fde68a;">Manage, visualize, and explore player data.</span>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        ### Explore every module from the sidebar:
        - 🟢 <b>Live Scorecard</b><br>
        - 📊 <b>Player Analytics & Stats</b><br>
        - 🧮 <b>SQL Analytics</b><br>
        - ⚙️ <b>CRUD Operations</b>
        """, unsafe_allow_html=True)
        st.markdown('<span style="color:#d1d5fa;font-weight:bold;">Made with Python, Streamlit, SQL & REST API 🚀</span>', unsafe_allow_html=True) 
