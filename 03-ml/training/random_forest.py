# Random Forest training module.
# Implements walk-forward validation and final model fitting.
# Version: 1.0.0

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Maps the 'status' string column (a/d/i/s/u) to integers.
# Unknown values (e.g. NaN, unexpected strings) become -1.
STATUS_MAP = {"a": 0, "d": 1, "i": 2, "s": 3, "u": 4}


def _build_sort_key(df: pd.DataFrame):
    return df["season_id"] * 100 + df["gameweek_id"]


def preprocess(X: pd.DataFrame, categorical_str_cols: list[str]):
    X = X.copy()

    # String → int
    for col in categorical_str_cols:
        if col in X.columns:
            X[col] = X[col].map(STATUS_MAP).fillna(-1).astype(int)

    # Boolean → int
    bool_cols = X.select_dtypes(include="bool").columns.tolist()
    for col in bool_cols:
        X[col] = X[col].astype(int)

    # TODO: add one-hot encoding for nominal categorical columns if needed (e.g. element_type, team_id) @16/03
    return X


def _build_model(hyperparams: dict):
    return RandomForestRegressor(**hyperparams)


def _metrics(y_true: pd.Series, y_pred: np.ndarray):
    mae = mean_absolute_error(y_true, y_pred)
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    r2 = r2_score(y_true, y_pred)
    return {"mae": round(mae, 4), "rmse": round(rmse, 4), "r2": round(r2, 4)}


def walk_forward(
    df: pd.DataFrame,
    config: dict,
    horizon: int,
): # returns tuple[list[dict], RandomForestRegressor, list[str]]
    
    # Args:
    #     df:       Full feature DataFrame from loader.load_features().
    #     config:   Parsed config.yaml dict.
    #     horizon:  1, 2, or 3.

    # Returns:
    #     fold_metrics: List of dicts, one per validation fold.
    #     final_model:  RandomForestRegressor fitted on all available data.
    #     feature_cols: Ordered list of column names used as features.
    target_col = f"pts_target_h{horizon}"
    exclude = set(config["features"]["exclude"])
    cat_str_cols = config["features"].get("categorical_str", [])
    hyperparams = config["model"]["hyperparameters"]

    wf_config = config["training"]["walk_forward"]
    min_train_steps: int = wf_config["min_train_steps"]
    step: int = wf_config["step"]

    # Derive sort key (do NOT add to df permanently — keep df clean)
    sort_key = _build_sort_key(df)
    sorted_steps = sorted(sort_key.unique())

    # Feature columns: everything not excluded and not the sort key itself
    feature_cols = [c for c in df.columns if c not in exclude]

    fold_metrics: list[dict] = []

    for i, val_step in enumerate(sorted_steps[min_train_steps::step]):
        train_mask = sort_key < val_step
        val_mask = sort_key == val_step

        train_df = df[train_mask]
        val_df = df[val_mask]

        # Both subsets already have non-null targets (guaranteed by loader query),
        # but double-check in case of edge cases.
        train_df = train_df[train_df[target_col].notna()]
        val_df = val_df[val_df[target_col].notna()]

        if len(train_df) < 10 or len(val_df) < 1:
            continue

        X_train = preprocess(train_df[feature_cols], cat_str_cols)
        y_train = train_df[target_col]
        X_val = preprocess(val_df[feature_cols], cat_str_cols)
        y_val = val_df[target_col]

        model = _build_model(hyperparams)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_val)

        m = _metrics(y_val, y_pred)

        val_season = int(val_df["season_id"].iloc[0])
        val_gw = int(val_df["gameweek_id"].iloc[0])

        fold_metrics.append({
            "fold_index": i,
            "validation_season_id": val_season,
            "validation_gameweek_id": val_gw,
            "n_train_rows": len(train_df),
            "n_val_rows": len(val_df),
            **m,
        })

    if not fold_metrics:
        raise RuntimeError(
            f"Walk-forward produced 0 folds for horizon h{horizon}. "
            "Check min_train_steps vs available data."
        )

    avg = {
        "avg_mae": round(float(np.mean([f["mae"] for f in fold_metrics])), 4),
        "avg_rmse": round(float(np.mean([f["rmse"] for f in fold_metrics])), 4),
        "avg_r2": round(float(np.mean([f["r2"] for f in fold_metrics])), 4),
    }

    # Final model: train on ALL data
    all_df = df[df[target_col].notna()]
    X_all = preprocess(all_df[feature_cols], cat_str_cols)
    y_all = all_df[target_col]
    final_model = _build_model(hyperparams)
    final_model.fit(X_all, y_all)

    return fold_metrics, final_model, feature_cols, avg


def feature_importances(model: RandomForestRegressor, feature_cols: list[str]):
    importances = dict(zip(feature_cols, model.feature_importances_.tolist()))
    return dict(sorted(importances.items(), key=lambda x: x[1], reverse=True))
