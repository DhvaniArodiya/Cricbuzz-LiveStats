import streamlit as st
import requests

def fetch_recent_matches():
    url = "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/recent"
    headers = {
        "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com",
        "x-rapidapi-key": "5670032a90mshae1f46da8637796p14d1ccjsnf3b7630272dd"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("typeMatches", [])
    except Exception as e:
        st.error(f" Error fetching recent matches: {e}")
        return []

def app():
    st.title("📊 Live Matches")
    st.markdown("View ongoing and recent international cricket matches. Use filters below.")

    type_matches = fetch_recent_matches()
    if not type_matches:
        st.warning("No recent match data available yet. Please connect to a working data source.")
        return

    teams, statuses = set(), set()

    # Collect filter values
    for match_type in type_matches:
        for series in match_type.get("seriesMatches", []):
            if "seriesAdWrapper" in series:
                for match in series["seriesAdWrapper"].get("matches", []):
                    info = match.get("matchInfo", {})
                    teams.add(info.get("team1", {}).get("teamName"))
                    teams.add(info.get("team2", {}).get("teamName"))
                    statuses.add(info.get("status"))

    teams.discard(None)
    statuses.discard(None)
    teams = sorted(teams)
    statuses = sorted(statuses)

    selected_team = st.selectbox("Filter by Team", ["All Teams"] + teams)
    selected_status = st.selectbox("Filter by Status", ["All Status"] + statuses)

    # Display matches grouped by series
    for match_type in type_matches:
        for series in match_type.get("seriesMatches", []):
            if "seriesAdWrapper" not in series:
                continue

            series_name = (
                series["seriesAdWrapper"].get("seriesName")
                or "Unnamed Series"
            )
            st.subheader(series_name)

            for match in series["seriesAdWrapper"].get("matches", []):
                info = match.get("matchInfo", {})
                team1 = info.get("team1", {}).get("teamName", "N/A")
                team2 = info.get("team2", {}).get("teamName", "N/A")
                status = info.get("status", "N/A")
                venue = info.get("venueInfo", {}).get("ground", "Unknown")

                # Match filtering
                if (
                    (selected_team == "All Teams" or selected_team in [team1, team2])
                    and (selected_status == "All Status" or selected_status == status)
                ):
                    st.markdown(f"**{team1} 🆚 {team2}**")
                    st.write(f"📍 Venue: {venue}")
                    st.write(f"📌 Status: {status}")

                    # Show score if available
                    if match.get("matchScore"):
                        ms = match["matchScore"]
                        team1_score = ms.get("team1Score", {}).get("inngs1", {})
                        team2_score = ms.get("team2Score", {}).get("inngs1", {})
                        if team1_score:
                            st.write(f"🏏 {team1}: {team1_score.get('runs', 0)}/{team1_score.get('wickets', 0)} "
                                     f"in {team1_score.get('overs', 0)} overs")
                        if team2_score:
                            st.write(f"🏏 {team2}: {team2_score.get('runs', 0)}/{team2_score.get('wickets', 0)} "
                                     f"in {team2_score.get('overs', 0)} overs")

                    st.markdown("---")
