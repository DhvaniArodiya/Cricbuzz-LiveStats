import requests
import streamlit as st

BASE_URL = "https://cricbuzz-cricket.p.rapidapi.com"

def fetch_live_matches():
    headers = {
        "x-rapidapi-key": st.secrets["5670032a90mshae1f46da8637796p14d1ccjsnf3b7630272dd"],
        "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
    }

    url = f"{BASE_URL}/matches/v1/recent"

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return []

    data = response.json()
    matches = []

    for t in data.get("typeMatches", []):
        for s in t.get("seriesMatches", []):
            series = s.get("seriesAdWrapper", {})
            series_name = series.get("seriesName", "Unknown Series")

            for m in series.get("matches", []):
                info = m.get("matchInfo", {})
                team1 = info.get("team1", {}).get("teamName", "Unknown")
                team2 = info.get("team2", {}).get("teamName", "Unknown")
                status = info.get("status", "No status")

                matches.append({
                    "series": series_name,
                    "team1": team1,
                    "team2": team2,
                    "status": status
                })

    return matches
