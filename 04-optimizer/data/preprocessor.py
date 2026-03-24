# Data preprocessing for the optimizer
# Version: 1.0.0
import pandas as pd

#user choice of horizon and free_hit chip dictate the optimizer goal. filter the input df into the optimizer beforehand.
def apply_horizon_filter(horizon, chip, df: pd.DataFrame):
    effective_horizon = 1 if chip == "free_hit" else horizon
    return df[df["horizon"] <= effective_horizon]

#slice weights to match the horizons
def slice_weights(df: pd.DataFrame, horizon_weights):
    num_horizons = df["horizon"].max()
    return [w for _, w in horizon_weights[:num_horizons]]

#preprocess data for the optimizer
def preprocess_data(df: pd.DataFrame):
    pts = df.pivot(index="opta_code", columns="horizon", values="predicted_points")
    pts.columns = [f'h{h}' for h in pts.columns]  # rename 1→h1 etc.
    pts = pts.reset_index()
    meta = df.sort_values('horizon')[['opta_code',"predicted_gameweek_id", "season_id", "web_name", "first_name", "second_name", "team", 'position', 'price']].drop_duplicates('opta_code')
    processed_df = pts.merge(meta, on='opta_code')
    return processed_df.to_dict(orient='records')
