import requests

BASE_URL = "https://cricbuzz-cricket.p.rapidapi.com"

HEADERS = {
    "x-rapidapi-key": "5670032a90mshae1f46da8637796p14d1ccjsnf3b7630272dd",
    "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
}

def get_live_matches():
    url = f"{BASE_URL}/matches/v1/live"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        return None
