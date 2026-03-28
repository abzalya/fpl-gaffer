#Declaring a pydantic api contract
#optimize route
from pydantic import BaseModel
from decimal import Decimal
from typing import Optional

class SquadRequest(BaseModel):
    opta_code: int
    locked: bool

class ChipsRequest(BaseModel):
    wildcard: bool
    free_hit: bool
    bench_boost: bool
    triple_captain: bool

class OptimizeRequest(BaseModel):
    existing_squad: list[SquadRequest] | None
    chips: ChipsRequest
    bank: float
    free_transfers: int
    horizon: int

class PointsResponse(BaseModel):
    gw: int
    pts: Decimal

class SquadResponse(BaseModel):
    club: str
    name: str
    price: Decimal
    position: str
    opta_code: int
    is_captain: bool
    is_starter: bool
    expected_pts: list[PointsResponse]

class TransferResponse(BaseModel):
    club: str
    name: str
    price: Decimal
    position: str
    opta_code: int    

class OptimizeResponse(BaseModel):
    status: str
    horizon: int
    solve_time_ms: int
    error_message: str | None
    squad: list[SquadResponse]
    transfers_in: list[TransferResponse] | None
    transfers_out: list[TransferResponse] | None