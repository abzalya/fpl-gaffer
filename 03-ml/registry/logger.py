# Persists training run metadata, model artefact records, and predictions to the ml schema.
# Version: 1.1.0

import uuid
from datetime import datetime, timezone
from pathlib import Path

import joblib
import pandas as pd
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert as pg_insert

from db.engine import engine
from db.schema import ml_training_runs, ml_model_artefacts, ml_predictions

def save_run(
    *,
    run_id: uuid.UUID,
    run_at: datetime,
    triggered_by: str,
    algorithm: str,
    horizon: int,
    config_snapshot: dict,
    fold_metrics: list[dict],
    final_model,
    feature_cols: list[str],
    feature_importances: dict,
    avg_metrics: dict,
    artefacts_dir: Path,
):
    
    short_id = str(run_id)[:8]
    ts = run_at.strftime("%Y%m%d_%H%M%S")
    pkl_filename = f"{algorithm}_h{horizon}_{ts}_{short_id}.pkl"
    artefact_path = artefacts_dir / pkl_filename

    # 1. Save fold metrics to ml.training_runs
    fold_rows = [
        {
            "run_id": run_id,
            "run_at": run_at,
            "triggered_by": triggered_by,
            "algorithm": algorithm,
            "horizon": horizon,
            "config_snapshot": config_snapshot,
            "fold_index": f["fold_index"],
            "validation_season_id": f["validation_season_id"],
            "validation_gameweek_id": f["validation_gameweek_id"],
            "n_train_rows": f["n_train_rows"],
            "n_val_rows": f["n_val_rows"],
            "mae": f["mae"],
            "rmse": f["rmse"],
            "r2": f["r2"],
        }
        for f in fold_metrics
    ]

    with engine.begin() as conn:
        conn.execute(ml_training_runs.insert(), fold_rows)

    # 2. Save model to disk
    artefacts_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(final_model, artefact_path)

    # 3. Demote existing production models for this horizon, then insert new one
    with engine.begin() as conn:
        conn.execute(
            ml_model_artefacts.update()
            .where(ml_model_artefacts.c.horizon == horizon)
            .where(ml_model_artefacts.c.is_production == True)
            .values(is_production=False)
        )
        conn.execute(
            ml_model_artefacts.insert().values(
                run_id=run_id,
                run_at=run_at,
                triggered_by=triggered_by,
                algorithm=algorithm,
                horizon=horizon,
                artefact_path=str(artefact_path),
                feature_cols=feature_cols,
                feature_importances=feature_importances,
                config_snapshot=config_snapshot,
                n_folds=len(fold_metrics),
                avg_mae=avg_metrics["avg_mae"],
                avg_rmse=avg_metrics["avg_rmse"],
                avg_r2=avg_metrics["avg_r2"],
                is_production=True,
                promoted_at=datetime.now(timezone.utc),
            )
        )

    return artefact_path


def save_predictions(
    *,
    run_id: uuid.UUID,
    predicted_at: datetime,
    horizon: int,
    features_df: pd.DataFrame,
    predicted_points: list[float],
    current_gw: int,  # NEW: global current GW passed explicitly
):

    rows = [
        {
            "run_id": run_id,
            "predicted_at": predicted_at,
            "opta_code": int(row["opta_code"]),
            "season_id": int(row["season_id"]),
            # OLD: used row["gameweek_id"] — blank-GW players were tagged with GW-1,
            # making the optimizer's MAX(features_gameweek_id) filter exclude them.
            # "features_gameweek_id": int(row["gameweek_id"]),
            # "predicted_gameweek_id": int(row["gameweek_id"]) + horizon,
            # NEW: always tag with the global current GW so all players are consistent.
            "features_gameweek_id": current_gw,
            "predicted_gameweek_id": current_gw + horizon,
            "horizon": horizon,
            "predicted_points": round(float(pts), 4),
            "actual_points": None,
        }
        for (_, row), pts in zip(features_df.iterrows(), predicted_points)
    ]

    stmt = pg_insert(ml_predictions).values(rows)
    stmt = stmt.on_conflict_do_update(
        constraint="uq_predictions_player_gw_horizon",
        set_={
            "run_id": stmt.excluded.run_id,
            "predicted_at": stmt.excluded.predicted_at,
            "features_gameweek_id": stmt.excluded.features_gameweek_id,
            "predicted_points": stmt.excluded.predicted_points,
        },
    )

    with engine.begin() as conn:
        conn.execute(stmt)

    return len(rows)
