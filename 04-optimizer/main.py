# FPL Gaffer — optimizer Entry Point
# Version: 1.0.0
import json
import time
import yaml
from pathlib import Path
from data.loader import load_predictions
from data.preprocessor import apply_horizon_filter, preprocess_data, slice_weights
from tests.temporary_input import adjust_user_input
from load_user_input import load_user_input
from optimizer import select_squad
from registry.logger import save_log

def run_optimizer(user_input: dict, triggered_by: str = "api"):
    #loading config
    CONFIG_PATH = Path(__file__).parent / "config.yaml"

    def load_config():
        with open(CONFIG_PATH) as f:
            return yaml.safe_load(f)

    config = load_config()
    max_budget = config["constraints"]["max_budget"]
    horizon_weights = list(config["constraints"]["horizon_weights"].items())

    #USER INPUT LOADING
    user_existing_opta_codes, user_locked_players, user_chip, user_bank, user_free_transfers, user_horizon = load_user_input(user_input)

    #PREDICTIONS LOADING AS INPUT FOR OPTIMIZER
    predictions = load_predictions()
    predictions_filtered = apply_horizon_filter(user_horizon, user_chip, predictions)
    players = preprocess_data(predictions_filtered)

    #Weights
    gw_weights = slice_weights(predictions_filtered, horizon_weights)

    #Budget
    budget = max_budget
    if user_existing_opta_codes:
        existing_players = [p for p in players if p["opta_code"] in user_existing_opta_codes]
        budget = user_bank + sum(p["price"] for p in existing_players)

    t0 = time.monotonic()
    squad_json, transfers_in_json, transfers_out_json, transfer_hits, status, error_message = select_squad(
        players,
        gw_weights,
        budget,
        user_chip,
        user_locked_players,
        user_existing_opta_codes,
        user_free_transfers,
        config["constraints"],
    )
    solve_time_ms = int((time.monotonic() - t0) * 1000)

    #logging

    save_log(
        status=status,
        solve_time_ms=solve_time_ms,
        input_params=user_input,
        error_message=error_message,
        #run fields
        db_input=predictions_filtered,
        transfer_hits=transfer_hits,
        squad_json=squad_json,
        transfers_in_json=transfers_in_json,
        transfers_out_json=transfers_out_json,
        triggered_by=triggered_by,
        user_chip=user_chip,
        effective_horizon=int(predictions_filtered["horizon"].max()),
        budget=budget)

    return {
    "status": status,
    "horizon": int(predictions_filtered["horizon"].max()),
    "solve_time_ms": solve_time_ms,
    "error_message": error_message,
    "squad": squad_json,
    "transfers_in": transfers_in_json,
    "transfers_out": transfers_out_json,
    }

if __name__ == "__main__":
    #FAKE json response that can be adjusted for testing purposes (my personal team)
    user_input = adjust_user_input(2)
    run_optimizer(user_input, "manual")

#TODO:
#safeguarding
#1. only one chip should be active at any one time. i think its fine for now but definetely needs to be thought through. 
#Caching
#1. we can cache load_predictions() it is the same data every week until next week. 
#optimizer solve time is in miliseconds. bottleneck on load. 
#Redis or in-memory TTL cache to show knowledge
#2. New user team can still be cached. can be our landing page maybe ?
