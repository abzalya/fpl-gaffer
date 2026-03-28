#POST /optimize — runs the FPL squad optimizer and returns the selected squad, transfers, and solve metadata
# Version: 1.0.0
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "04-optimizer"))

from main_runner import run_optimizer  # type: ignore
from fastapi import APIRouter, HTTPException
from fastapi.concurrency import run_in_threadpool
from contracts.optimize import OptimizeRequest, OptimizeResponse

router = APIRouter()

@router.post("/optimize")
async def optimize(body: OptimizeRequest):
    response = await run_in_threadpool(run_optimizer, body.model_dump())
    if response["status"] != "optimal":
        raise HTTPException(status_code=400, detail=response.get("error_message", "infeasible team"))

    return OptimizeResponse(**response)
