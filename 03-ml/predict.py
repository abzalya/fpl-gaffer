# FPL Gaffer — Prediction Entry Point
# Version: 1.0.0
#
# Loads the production model for each horizon, runs inference on the most
# recent GW feature rows, and writes predicted points to ml.predictions.
#
# Usage:
#   python predict.py                   # predict for all trained horizons
#   python predict.py --horizon 1       # predict h1 only

import argparse
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

import joblib
import pandas as pd
from sqlalchemy import text

sys.path.insert(0, str(Path(__file__).parent))

import importlib

from db.engine import engine
from data.loader import load_latest_features
from training.registry import ALGORITHM_REGISTRY
from registry.logger import save_predictions


def _load_production_artefact(horizon: int):
    
    query = text("""
        SELECT run_id, algorithm, artefact_path, feature_cols, config_snapshot
        FROM ml.model_artefacts
        WHERE horizon = :horizon AND is_production = TRUE
        ORDER BY promoted_at DESC
        LIMIT 1
    """)
    with engine.connect() as conn:
        row = conn.execute(query, {"horizon": horizon}).mappings().fetchone()

    if row is None:
        raise RuntimeError(
            f"No production model found for horizon h{horizon}. "
            "Run main.py first to train and register a model."
        )
    return dict(row)


def predict_horizon(horizon: int, features_df: pd.DataFrame):

    artefact = _load_production_artefact(horizon)
    model = joblib.load(artefact["artefact_path"])
    feature_cols: list[str] = artefact["feature_cols"]
    cat_str_cols: list[str] = artefact["config_snapshot"]["features"].get("categorical_str", [])

    # Load the algorithm module to get the correct preprocessing function
    algo_module = importlib.import_module(ALGORITHM_REGISTRY[artefact["algorithm"]])

    # Select only the features the model was trained on
    features = algo_module.preprocess(features_df[feature_cols], cat_str_cols)

    predicted_points = model.predict(features).tolist()

    predicted_at = datetime.now(timezone.utc)
    run_id = uuid.UUID(str(artefact["run_id"]))

    n = save_predictions(
        run_id=run_id,
        predicted_at=predicted_at,
        horizon=horizon,
        features_df=features_df,
        predicted_points=predicted_points,
    )
    print(f"  Horizon h{horizon}: Predicted points for {n} rows.")


def main():
    parser = argparse.ArgumentParser(description="FPL Gaffer — Generate predictions")
    parser.add_argument(
        "--horizon",
        type=int,
        default=None,
        help="Horizon to predict (1, 2, or 3). Defaults to all registered horizons.",
    )
    args = parser.parse_args()

    if args.horizon is not None:
        horizons = [args.horizon]
    else:
        with engine.connect() as conn:
            rows = conn.execute(text("""
                SELECT DISTINCT horizon FROM ml.model_artefacts
                WHERE is_production = TRUE ORDER BY horizon
            """)).fetchall()
        horizons = [r[0] for r in rows]
        if not horizons:
            raise RuntimeError("No production models found. Run main.py to train first.")

    # Load features once — shared across all horizons
    features_df = load_latest_features()

    for horizon in horizons:
        predict_horizon(horizon, features_df)

    print("  Predictions written to ml.predictions.")


if __name__ == "__main__":
    main()
