import requests

url = "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/recent"

headers = {
    "x-rapidapi-key": "5670032a90mshae1f46da8637796p14d1ccjsnf3b7630272dd",
    "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
}

response = requests.get(url, headers=headers)
data = response.json()

# Clean output
for series in data.get("typeMatches", []):
    for match in series.get("seriesMatches", []):
        if "seriesAdWrapper" in match:
            matches = match["seriesAdWrapper"].get("matches", [])
            for m in matches:
                info = m.get("matchInfo", {})
                team1 = info.get("team1", {}).get("teamName", "N/A")
                team2 = info.get("team2", {}).get("teamName", "N/A")
                venue = info.get("venueInfo", {}).get("ground", "Unknown")
                status = info.get("status", "N/A")

                print(f"{team1} vs {team2} | Venue: {venue} | Status: {status}")
