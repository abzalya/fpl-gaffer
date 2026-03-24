# Saving results and run details in optimizer schema
# Version: 1.1.0

import uuid
from datetime import datetime, timezone

import joblib
import pandas as pd
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert as pg_insert

from db.engine import engine
from db.schema import optimizer_runs, optimizer_run_logs
    
def save_log():
    pass

def save_run(
    *,
    run_id: uuid.UUID,
    run_at: datetime,
    db_input: pd.DataFrame,
    user_input: dict,
    transfer_hits: int,
    squad_json: dict,
    transfers_in_json: dict | None,
    transfers_out_json: dict | None,
    triggered_by: str, 

):
    #expected points and budget used calc
    squad = squad_json["squad"]
    if user_input["chip"] == "bench_boost":
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
            "gameweek_id": db_input["predicted_gameweek_id"].iloc[0] - 1,
            "season_id": db_input["season_id"].iloc[0],
            "horizon": user_input["horizon"],
            "chip": user_input["chip"],
            "free_transfers": user_input["free_transfers"],
            "transfer_hits": transfer_hits,
            "expected_pts": expected_pts,
            "expected_pts_after_hits": expected_pts - (transfer_hits * 4),
            "budget_used": budget_used,
            "budget_remaining": user_input["bank"] - budget_used,
            "squad": squad_json,
            "transfers_in": transfers_in_json,
            "transfers_out": transfers_out_json,
            "triggered_by": triggered_by,
        }
    ]

    stmt = pg_insert(optimizer_runs).values(row)
    stmt = stmt.on_conflict_do_update(
        constraint="uq_optimizer_runs_run_id",
    )

    with engine.begin() as conn:
        conn.execute(stmt)

    return #idk what to return
