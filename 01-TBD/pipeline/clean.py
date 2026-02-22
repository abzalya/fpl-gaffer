# Data Cleaning before Insertion into DB
# The raw dict is always preserved in its entirety inside "raw_data" so nothing from the API is ever permanently lost.

# Version: v1.0.0

import math
import ast
from datetime import datetime, timezone
from typing import Any, Optional


# Cleaning functions. 
# The FPL API is inconsistent — it mixes ints, floats, empty strings,
# None, nan, and string representations of numbers.

def _int(val: Any) -> Optional[int]:
    """Convert to int. Returns None for empty string, None, or nan."""
    if val is None:
        return None
    if isinstance(val, float) and math.isnan(val):
        return None
    if val == "" or val == "nan":
        return None
    try:
        return int(float(val))          # float() first handles "4.0" → 4
    except (TypeError, ValueError):
        return None


def _float(val: Any) -> Optional[float]:
    """Convert to float. Returns None for empty string, None, or nan."""
    if val is None:
        return None
    if isinstance(val, float) and math.isnan(val):
        return None
    if val == "" or val == "nan":
        return None
    try:
        result = float(val)
        return None if math.isnan(result) else result
    except (TypeError, ValueError):
        return None


def _bool(val: Any) -> Optional[bool]:
    """Convert to bool. Handles Python booleans, 'True'/'False' strings."""
    if val is None or val == "":
        return None
    if isinstance(val, bool):
        return val
    if isinstance(val, str):
        return val.strip().lower() == "true"
    return bool(val)


def _str(val: Any) -> Optional[str]:
    """Convert to string. Returns None for empty strings."""
    if val is None:
        return None
    s = str(val).strip()
    return s if s else None


def _dt(val: Any) -> Optional[datetime]:
    """
    Parse an ISO 8601 timestamp string into a timezone-aware datetime.
    Handles the 'Z' suffix that the FPL API uses.
    Returns None if the value is empty or unparseable.
    """
    if not val or val == "":
        return None
    try:
        s = str(val).strip().replace("Z", "+00:00")
        return datetime.fromisoformat(s)
    except (ValueError, TypeError):
        return None


def _jsonb(val: Any) -> Any:
    """
    Ensure a value is JSON-serialisable for a JSONB column.
    If the API returned a string representation of a Python object
    (e.g. scout_risks comes back as a string like "[{'property': ...}]"),
    safely evaluate it back into a Python object.
    """
    if val is None or val == "":
        return None
    if isinstance(val, (dict, list)):
        return val
    if isinstance(val, str):
        try:
            return ast.literal_eval(val)    # safe eval of Python literals only
        except (ValueError, SyntaxError):
            return val                      # leave as raw string if unparseable
    return val


# 1. GAMEWEEKS
def clean_gameweek(raw: dict, season_id: int) -> dict:
    """
    Cleans one row from bootstrap-static → events.
    top_element_info is a nested dict like {"id": 531, "points": 17}.
    We pull the points out separately for easy querying.
    """
    return {
        "id":                   _int(raw.get("id")),
        "season_id":            season_id,
        "finished":             _bool(raw.get("finished")),
        "is_current":           _bool(raw.get("is_current")),
        "is_next":              _bool(raw.get("is_next")),
        "raw_data":             raw,
    }

# 2. TEAMS
def clean_team(raw: dict, season_id: int) -> dict:
    """Cleans one row from bootstrap-static → teams."""
    return {
        "id":                       _int(raw.get("id")),
        "season_id":                season_id,
        "code":                     _int(raw.get("code")),
        "name":                     _str(raw.get("name")),
        "short_name":               _str(raw.get("short_name")),
        "strength":                 _int(raw.get("strength")),
        "raw_data":                 raw,
    }


# 3. PLAYERS SNAPSHOT
def clean_player_snapshot(raw: dict, gameweek_id: int, season_id: int) -> dict:
    """Cleans one row from bootstrap-static → elements (~700 per fetch)."""
    return {
        "opta_code":                         _str(raw.get("opta_code")),
        "player_id":                        _int(raw.get("id")),
        "gameweek_id":                      gameweek_id,
        "season_id":                        season_id,
        # Player Info
        "web_name":                         _str(raw.get("web_name")),
        "first_name":                       _str(raw.get("first_name")),
        "second_name":                      _str(raw.get("second_name")),
        "team_id":                          _int(raw.get("team")),
        "element_type":                     _int(raw.get("element_type")),
        "status":                           _str(raw.get("status")),
        "now_cost":                         _int(raw.get("now_cost")),
        # Injury, gw info
        "chance_of_playing_next_round":     _int(raw.get("chance_of_playing_next_round")),
        "news":                             _str(raw.get("news")),
        "scout_risks":                      _jsonb(raw.get("scout_risks")),
        # Season Stats
        "total_points":                     _int(raw.get("total_points")),
        "minutes":                          _int(raw.get("minutes")),
        "goals_scored":                     _int(raw.get("goals_scored")),
        "assists":                          _int(raw.get("assists")),
        "clean_sheets":                     _int(raw.get("clean_sheets")),
        "goals_conceded":                   _int(raw.get("goals_conceded")),
        "saves":                            _int(raw.get("saves")),
        "bonus":                            _int(raw.get("bonus")),
        "yellow_cards":                     _int(raw.get("yellow_cards")),
        "red_cards":                        _int(raw.get("red_cards")),
        "starts":                           _int(raw.get("starts")),
        # ICT index
        "influence":                        _float(raw.get("influence")),
        "creativity":                       _float(raw.get("creativity")),
        "threat":                           _float(raw.get("threat")),
        "ict_index":                        _float(raw.get("ict_index")),
        # Expected Metrics
        "expected_goals":                   _float(raw.get("expected_goals")),
        "expected_assists":                 _float(raw.get("expected_assists")),
        "expected_goals_conceded":          _float(raw.get("expected_goals_conceded")),
        "expected_goal_involvements":       _float(raw.get("expected_goal_involvements")),
        # Form Metrics
        "form":                             _float(raw.get("form")),
        "points_per_game":                  _float(raw.get("points_per_game")),
        "ep_next":                          _float(raw.get("ep_next")),
        # Defensive Stats
        "clearances_blocks_interceptions":  _int(raw.get("clearances_blocks_interceptions")),
        "recoveries":                       _int(raw.get("recoveries")),
        "tackles":                          _int(raw.get("tackles")),
        # Raw Data
        "raw_data":                         raw,
    }


# 4. FUTURE FIXTURES
def clean_future_fixture(raw: dict, player_id: int, fetched_gameweek_id: int, opta_code: str) -> dict:
    """
    Cleans one row from element-summary/{id}/ → fixtures.
    team_h_score and team_a_score will be empty strings for unplayed fixtures.
    """
    return {
        "opta_code":           opta_code,
        "player_id":            player_id,
        "fetched_gameweek_id":  fetched_gameweek_id,
        # Fixture Info
        "fixture_id":           _int(raw.get("id")),
        "fixture_gameweek_id":  _int(raw.get("event")),
        "is_home":              _bool(raw.get("is_home")),
        "difficulty":           _int(raw.get("difficulty")),
        "team_h":               _int(raw.get("team_h")),
        "team_a":               _int(raw.get("team_a")),
        # Raw Data
        "raw_data":             raw,
    }


# 5. GAMEWEEK HISTORY
def clean_gw_history(raw: dict, player_id: int, opta_code: str, season_id: int) -> dict:
    """
    Cleans one row from element-summary/{id}/ → history.
    This is the per-fixture performance record — your ML gold.
    """
    return {
        "opta_code":                         opta_code,
        "player_id":                        player_id,
        # Fixture Info
        "fixture_id":                       _int(raw.get("fixture")),
        "gameweek_id":                      _int(raw.get("round")),
        "season_id":                         season_id,
        "opponent_team_id":                 _int(raw.get("opponent_team")),
        "was_home":                         _bool(raw.get("was_home")),
        # Fixture Result
        "team_h_score":                     _int(raw.get("team_h_score")),
        "team_a_score":                     _int(raw.get("team_a_score")),
        "total_points":                     _int(raw.get("total_points")),
        "minutes":                          _int(raw.get("minutes")),
        # Stats
        "goals_scored":                     _int(raw.get("goals_scored")),
        "assists":                          _int(raw.get("assists")),
        "clean_sheets":                     _int(raw.get("clean_sheets")),
        "goals_conceded":                   _int(raw.get("goals_conceded")),
        "own_goals":                        _int(raw.get("own_goals")),
        "penalties_saved":                  _int(raw.get("penalties_saved")),
        "penalties_missed":                 _int(raw.get("penalties_missed")),
        "yellow_cards":                     _int(raw.get("yellow_cards")),
        "red_cards":                        _int(raw.get("red_cards")),
        "saves":                            _int(raw.get("saves")),
        "bonus":                            _int(raw.get("bonus")),
        "bps":                              _int(raw.get("bps")),
        "starts":                           _int(raw.get("starts")),
        # ICT index
        "influence":                        _float(raw.get("influence")),
        "creativity":                       _float(raw.get("creativity")),
        "threat":                           _float(raw.get("threat")),
        "ict_index":                        _float(raw.get("ict_index")),
        # Expected Metrics
        "expected_goals":                   _float(raw.get("expected_goals")),
        "expected_assists":                 _float(raw.get("expected_assists")),
        "expected_goal_involvements":       _float(raw.get("expected_goal_involvements")),
        "expected_goals_conceded":          _float(raw.get("expected_goals_conceded")),
        # Defensive Stats
        "clearances_blocks_interceptions":  _int(raw.get("clearances_blocks_interceptions")),
        "recoveries":                       _int(raw.get("recoveries")),
        "tackles":                          _int(raw.get("tackles")),
        # Cost
        "value":                            _int(raw.get("value")),
        # Raw Data
        "raw_data":                         raw,
    }