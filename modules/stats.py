import requests, os

API_KEY = "80e09bb4d95617666c18d7690fade8b5"
BASE = "https://v3.football.api-sports.io"
HEADERS = {"x-apisports-key": API_KEY}

def get_live_fixture_id(team_name: str) -> int | None:
    r = requests.get(f"{BASE}/fixtures", headers=HEADERS,
                     params={"live": "all"})
    for f in r.json().get("response", []):
        teams = f["teams"]
        if team_name.lower() in [
            teams["home"]["name"].lower(),
            teams["away"]["name"].lower()
        ]:
            return f["fixture"]["id"]
    return None
def get_match_stats(fixture_id: int) -> dict:
    r = requests.get(f"{BASE}/fixtures", headers=HEADERS,
                     params={"id": fixture_id})
    data = r.json()["response"][0]
    goals = data["goals"]
    events = data.get("events", [])
    last_event = events[-1] if events else {}
    return {
        "home_score": goals["home"],
        "away_score": goals["away"],
        "minute": data["fixture"]["status"]["elapsed"],
        "last_event_type": last_event.get("type"),
        "last_event_detail": last_event.get("detail"),
        "last_event_team": last_event.get("team", {}).get("name"),
        "last_event_player": last_event.get("player", {}).get("name"),
    }

if __name__ == "__main__":
    fid = get_live_fixture_id("Inter") # Change here the match you want
    if fid:
        print(get_match_stats(fid))
    else:
        print("No live match found")


#To test anytime replace the function get_live_fixture_id with the following
#it will return all live matches and then you choose the one to get the feature from
''' def get_live_fixture_id(team_name: str) -> int | None:
    r = requests.get(
        f"{BASE}/fixtures",
        headers=HEADERS,
        params={"live": "all"}
    )

    data = r.json().get("response", [])

    print("LIVE MATCHES:")
    for f in data:
        home = f["teams"]["home"]["name"]
        away = f["teams"]["away"]["name"]

        print(home, "vs", away)

        if team_name.lower() in [home.lower(), away.lower()]:
            return f["fixture"]["id"]

    return None'''
