# Saving results and run details in optimizer schema
# Version: 1.1.0
import sys
import yaml
import uuid
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from sqlalchemy.dialects.postgresql import insert as pg_insert

from db.engine import engine
from db.schema import optimizer_runs, optimizer_run_logs
    
def save_log(
    *,
    # log fields (always required)
    status: str,
    solve_time_ms: int,
    input_params: dict,
    error_message: str | None = None,
    # run fields (only on success)
    db_input: pd.DataFrame | None = None,
    transfer_hits: int | None = None,
    squad_json: dict | None = None,
    transfers_in_json: dict | None = None,
    transfers_out_json: dict | None = None,
    triggered_by: str | None = None,
    user_chip: str | None = None,
):
    run_id = uuid.uuid4()
    run_at = datetime.now(timezone.utc)
    
    with open(Path(__file__).parent.parent / "config.yaml") as f:
        config_snapshot = yaml.safe_load(f)

    row = [
        {
            "run_id": run_id,
            "run_at": run_at,
            "status": status,
            "solve_time_ms": solve_time_ms,
            "input_params": input_params,
            "config_snapshot": config_snapshot,
            "error_message": error_message,
            
        }
    ]
    #check this on both
    stmt = pg_insert(optimizer_run_logs).values(row)
    
    with engine.begin() as conn:
        conn.execute(stmt)
    
    if status == "optimal":
        _save_run(run_id, run_at, db_input, input_params, transfer_hits, squad_json, transfers_in_json, transfers_out_json, triggered_by, user_chip)

def _save_run(
    run_id: uuid.UUID,
    run_at: datetime,
    db_input: pd.DataFrame,
    input_params: dict,
    transfer_hits: int,
    squad_json: dict,
    transfers_in_json: dict | None,
    transfers_out_json: dict | None,
    triggered_by: str,
    user_chip: str | None,

):
    #expected points and budget used calc
    squad = squad_json["squad"]
    if user_chip == "bench_boost":
        h1 = sum(p["expected_pts"][0]["pts"] for p in squad)
        rest = sum(entry["pts"] for p in squad if p["is_starter"] for entry in p["expected_pts"][1:])
        expected_pts = h1 + rest
    else:
        expected_pts = sum(entry["pts"] for p in squad if p["is_starter"] for entry in p["expected_pts"])

    budget_used = sum(p["price"] for p in squad)

    row = [
        {
            "run_id": run_id,
            "run_at": run_at,
            "gameweek_id": int(db_input["predicted_gameweek_id"].iloc[0] - 1),
            "season_id": int(db_input["season_id"].iloc[0]),
            "horizon": input_params["horizon"],
            "chip": user_chip,
            "free_transfers": input_params["free_transfers"],
            "transfer_hits": transfer_hits,
            "expected_pts": expected_pts,
            "expected_pts_after_hits": expected_pts - (transfer_hits * 4),
            "budget_used": budget_used,
            "budget_remaining": input_params["bank"] - budget_used,
            "squad": squad_json,
            "transfers_in": transfers_in_json,
            "transfers_out": transfers_out_json,
            "triggered_by": triggered_by,
        }
    ]

    stmt = pg_insert(optimizer_runs).values(row)
    stmt = stmt.on_conflict_do_nothing(
        constraint="uq_optimizer_runs_run_id",
    )

    with engine.begin() as conn:
        conn.execute(stmt)

