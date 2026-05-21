import requests

API_KEY = "80e09bb4d95617666c18d7690fade8b5"
BASE    = "https://v3.football.api-sports.io"
HEADERS = {"x-apisports-key": API_KEY}

def get_live_fixture_id(team_name: str):
        r = requests.get(f"{BASE}/fixtures", headers=HEADERS,
                                              params={"live": "all"}, timeout=10)
        r.raise_for_status()
        for f in r.json().get("response", []):
                    teams = f["teams"]
                    if team_name.lower() in [
                                    teams["home"]["name"].lower(),
                                    teams["away"]["name"].lower()
                    ]:
                                    return f["fixture"]["id"]
                            return None

def get_match_stats(fixture_id: int) -> dict:
        # Request with events so last_event fields are populated
        r = requests.get(f"{BASE}/fixtures", headers=HEADERS,
                                              params={"id": fixture_id, "events": "true"}, timeout=10)
        r.raise_for_status()
        response = r.json().get("response", [])
        if not response:
                    return {}
                data = response[0]
    goals      = data.get("goals", {})
    events     = data.get("events", [])
    last_event = events[-1] if events else {}
    return {
                "home_score":         goals.get("home"),
                "away_score":         goals.get("away"),
                "minute":             data.get("fixture", {}).get("status", {}).get("elapsed"),
                "last_event_type":    last_event.get("type"),
                "last_event_detail":  last_event.get("detail"),
                "last_event_team":    last_event.get("team", {}).get("name"),
                "last_event_player":  last_event.get("player", {}).get("name"),
    }

if __name__ == "__main__":
        fid = get_live_fixture_id("Inter")
    if fid:
                print(get_match_stats(fid))
else:
        print("No live match found")
