#GET /players - returns the player details from a custom query
# Version: 1.1.0
import json
import pandas as pd
from fastapi import APIRouter, HTTPException
from contracts.players import PlayerResponse
from db.queries import load_players


router = APIRouter()


def _parse_fixtures(raw, horizon: int) -> list[dict]:
    if raw is None:
        return []
    entries = raw if isinstance(raw, list) else json.loads(raw)
    return [
        {
            "horizon": horizon,
            "is_home": e["is_home"],
            "difficulty": e["difficulty"],
            "opponent": e["opponent"],
        }
        for e in entries
        if e.get("opponent") is not None
    ]


@router.get("/players", response_model=list[PlayerResponse])
async def get_players():
    df = load_players()

    if df.empty:
        raise HTTPException(status_code=404, detail="No player details found")

    response = df.to_dict(orient="records")

    players = [
        {
            "opta_code": player["opta_code"],
            "name": player["name"],
            "club": player["club"],
            "club_short": player["club_short"],
            "position": player["position"],
            "price": player["price"],
            "status": player["status"],
            "predicted_pts_h1": player["predicted_pts_h1"],
            "predicted_pts_h2": player["predicted_pts_h2"],
            "predicted_pts_h3": player["predicted_pts_h3"],
            "fixtures": [
                *_parse_fixtures(player["h1_fixtures"], 1),
                *_parse_fixtures(player["h2_fixtures"], 2),
                *_parse_fixtures(player["h3_fixtures"], 3),
            ],
        }
        for player in response
    ]

    return [PlayerResponse(**p) for p in players]