# FPL Gaffer — optimizer Entry Point
# Version: 1.0.0

import uuid
import yaml
import pandas as pd
from datetime import datetime, timezone
from pathlib import Path
from data.loader import load_predictions

#loading config
CONFIG_PATH = Path(__file__).parent / "config.yaml"

def load_config():
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)

config = load_config()
max_budget = config["constraints"]["max_budget"]
max_players = config["constraints"]["max_players"]
starting_players = config["constraints"]["starting_players"]
max_players_per_team = config["constraints"]["max_players_per_team"]
position_total_limit = list(config["constraints"]["position_total_limit"].items())
position_starting_min = list(config["constraints"]["position_starting_min"].items())
horizon_weights = list(config["constraints"]["horizon_weights"].items())

#user choice of horizon and free_hit chip dictate the optimizer goal. filter the input df into the optimizer beforehand. 
def apply_horizon_filter(user_horizon, chip, df: pd.DataFrame):
    effective_horizon = 1 if chip == "free_hit" else user_horizon
    return df[df["horizon"] <= effective_horizon]
#TODO: add defaults so i can pass one thing ?

#slice weights to match the horizons
def slice_weights(df: pd.DataFrame):
    num_horizons = df["horizon"].max()  # or df["horizon"].max()
    return [w for _, w in horizon_weights[:num_horizons]]

#use case: gw_weights = slice_weights(predictions)

#preprocess data for the optimizer
def preprocess_data(df: pd.DataFrame):
    pts = df.pivot(index="opta_code", columns="horizon", values="predicted_points")
    pts.columns = [f'h{h}' for h in pts.columns]  # rename 1→h1 etc.
    pts = pts.reset_index()
    meta = df[['opta_code',"predicted_gameweek_id", "season_id", "web_name", "first_name", "second_name", "team", 'position', 'price']].drop_duplicates('opta_code')
    #return pts.merge(meta, on='opta_code')
    processed_df = pts.merge(meta, on='opta_code')
    return processed_df.to_dict(orient='records')

test = load_predictions()
test = apply_horizon_filter(1, "null", test)
test = preprocess_data(test)
print(test)

run_id = uuid.uuid4()
run_at = datetime.now(timezone.utc)
