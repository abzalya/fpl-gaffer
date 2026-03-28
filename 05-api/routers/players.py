#GET /players - returns the player details from a custom query
# Version: 1.0.0
import pandas as pd
from fastapi import APIRouter, HTTPException
from contracts.players import PlayerResponse
from db.queries import load_players


router = APIRouter()

@router.get("/players", response_model=list[PlayerResponse])
async def get_players():
    df = load_players()

    if df.empty:
        raise HTTPException(status_code=404, detail="No player details found")

    #response = df.to_json(orient="records")
    response = df.to_dict(orient="records")
    #[{'opta_code': 111234, 'name': 'Pickford', 'club': 'Everton', 'club_short': 'EVE', 'position': 'GKP', 'price': 5.6, 'status': 'a', 'predicted_pts_h1': 4.0, 'predicted_pts_h2': 3.1, 'predicted_pts_h3': 3.43, 'h1_is_home': False, 'h1_difficulty': 4, 'h1_opponent': 'BRE', 'h2_is_home': True, 'h2_difficulty': 3, 'h2_opponent': 'LIV', 'h3_is_home': False, 'h3_difficulty': 2.0, 'h3_opponent': 'WHU'}, {'opta_code': 98980, 'name': 'Martinez', 'club': 'Aston Villa', 'club_short': 'AVL', 'position': 'GKP', 'price': 5.1, 'status': 'a', 'predicted_pts_h1': 3.85, 'predicted_pts_h2': 3.33, 'predicted_pts_h3': 3.31, 'h1_is_home': False, 'h1_difficulty': 3, 'h1_opponent': 'NFO', 'h2_is_home': True, 'h2_difficulty': 2, 'h2_opponent': 'SUN', 'h3_is_home': False, 'h3_difficulty': 3.0, 'h3_opponent': 'FUL'}, {'opta_code': 467189, 'name': 'Hermansen', 'club': 'West Ham', 'club_short': 'WHU', 'position': 'GKP', 'price': 4.2, 'status': 'a', 'predicted_pts_h1': 3.84, 'predicted_pts_h2': 3.04, 'predicted_pts_h3': 2.82, 'h1_is_home': True, 'h1_difficulty': 2, 'h1_opponent': 'WOL', 'h2_is_home': False, 'h2_difficulty': 3, 'h2_opponent': 'CRY', 'h3_is_home': True, 'h3_difficulty': 3.0, 'h3_opponent': 'EVE'}, {'opta_code': 184254, 'name': 'Vicario', 'club': 'Spurs', 'club_short': 'TOT', 'position': 'GKP', 'price': 4.7, 'status': 'd', 'predicted_pts_h1': 3.82, 'predicted_pts_h2': 2.64, 'predicted_pts_h3': 2.9, 'h1_is_home': False, 'h1_difficulty': 4, 'h1_opponent': 'SUN', 'h2_is_home': True, 'h2_difficulty': 3, 'h2_opponent': 'BHA', 'h3_is_home': False, 'h3_difficulty': 2.0, 'h3_opponent': 'WOL'}, {'opta_code': 154561, 'name': 'Raya', 'club': 'Arsenal', 'club_short': 'ARS', 'position': 'GKP', 'price': 6.0, 'status': 'a', 'predicted_pts_h1': 3.67, 'predicted_pts_h2': 3.69, 'predicted_pts_h3': 2.59, 'h1_is_home': True, 'h1_difficulty': 3, 'h1_opponent': 'BOU', 'h2_is_home': False, 'h2_difficulty': 5, 'h2_opponent': 'MCI', 'h3_is_home': None, 'h3_difficulty': nan, 'h3_opponent': nan}]
    
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
                f for f in [
                    {"horizon": 1, "is_home": player["h1_is_home"], "difficulty": player["h1_difficulty"], "opponent": player["h1_opponent"]},
                    {"horizon": 2, "is_home": player["h2_is_home"], "difficulty": player["h2_difficulty"], "opponent": player["h2_opponent"]},
                    {"horizon": 3, "is_home": player["h3_is_home"], "difficulty": player["h3_difficulty"], "opponent": player["h3_opponent"]},
                ]
                if pd.notna(f["opponent"])
            ],
        }
        for player in response
    ]

    return [PlayerResponse(**p) for p in players]