from dataclasses import dataclass, field
from typing import Optional

@dataclass
class GameState:
    # From vision
    home_team:   Optional[str] = None
    away_team:   Optional[str] = None
    home_score:  Optional[int] = None
    away_score:  Optional[int] = None
    match_minute:Optional[int] = None
    action:      Optional[str] = None

    # From stats API (overrides vision where available)
    last_event_type:   Optional[str] = None
    last_event_detail: Optional[str] = None
    last_event_player: Optional[str] = None
    last_event_team:   Optional[str] = None

    # Meta
    last_commentary: Optional[str] = None  # avoid repeating ourselves

def merge(state: GameState,
          vision_data: dict,
          stats_data: dict) -> GameState:
    """
    Stats API wins on score/minute (more reliable).
    Vision wins on action description (API has no play-by-play).
    """
    # Scores: trust stats API if available, fall back to vision
    state.home_score  = stats_data.get("home_score")  \
                     or vision_data.get("home_score")
    state.away_score  = stats_data.get("away_score")  \
                     or vision_data.get("away_score")
    state.match_minute = stats_data.get("minute")     \
                      or vision_data.get("match_minute")

    # Teams: vision reads them from the broadcast overlay
    state.home_team = vision_data.get("home_team") or state.home_team
    state.away_team = vision_data.get("away_team") or state.away_team

    # Action: vision only (API has no live play description)
    state.action = vision_data.get("action")
        
        
    # Last event: stats API only (accurate player names, event type)
    state.last_event_type   = stats_data.get("last_event_type")
    state.last_event_player = stats_data.get("last_event_player")
    state.last_event_detail = stats_data.get("last_event_detail")
    state.last_event_team   = stats_data.get("last_event_team")

    return state

