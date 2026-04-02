#Declaring a pydantic api contract
#optimize route
from pydantic import BaseModel
from decimal import Decimal

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

# Wrappers mirror the nested shape returned by package_squad() and package_transfers() - REQUIRED
class SquadWrapper(BaseModel):
    squad: list[SquadResponse]

class TransfersWrapper(BaseModel):
    transfers: list[TransferResponse]

class OptimizeResponse(BaseModel):
    status: str
    horizon: int
    solve_time_ms: int
    error_message: str | None
    squad: SquadWrapper
    transfers_in: TransfersWrapper | None
    transfers_out: TransfersWrapper | None