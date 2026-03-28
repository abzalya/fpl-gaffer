#GET /gameweek/next - returns the next gameweek_id and deadline time 
# Version: 1.0.0
from fastapi import APIRouter, HTTPException
from contracts.gameweek import GameweekResponse
from db.queries import load_gameweeks

router = APIRouter()

@router.get("/gameweek/next", response_model=GameweekResponse)
def get_next_gameweek():
    df = load_gameweeks()

    if df.empty:
        raise HTTPException(status_code=404, detail="No upcoming gameweek found")

    row = df.iloc[0]

    return GameweekResponse(
        gameweek_id=int(row["gameweek_id"]),
        name=f"Gameweek {int(row['gameweek_id'])}",
        deadline=row["deadline"],
        is_next=bool(row["is_next"]),
    )
