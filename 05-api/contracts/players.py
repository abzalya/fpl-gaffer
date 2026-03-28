#Declaring a pydantic api contract
# players route
from pydantic import BaseModel
from decimal import Decimal


class FixtureResponse(BaseModel):
    horizon: int
    is_home: bool | None
    opponent: str
    difficulty: int | None


class PlayerResponse(BaseModel):
    opta_code: int
    name: str
    club: str
    club_short: str
    position: str
    price: Decimal
    status: str
    predicted_pts_h1: float | None
    predicted_pts_h2: float | None
    predicted_pts_h3: float | None
    fixtures: list[FixtureResponse]
