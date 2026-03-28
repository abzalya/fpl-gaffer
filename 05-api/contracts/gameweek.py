#Declaring a pydantic api contract
#Gameweek route
from pydantic import BaseModel
from datetime import datetime

class GameweekResponse(BaseModel):
    gameweek_id: int
    name: str
    deadline: datetime
    is_next: bool
