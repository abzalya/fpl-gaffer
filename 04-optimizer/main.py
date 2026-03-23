# FPL Gaffer — optimizer Entry Point
# Version: 1.0.0
import json
import yaml
from pathlib import Path
from data.loader import load_predictions
from data.preprocessor import apply_horizon_filter, preprocess_data, slice_weights
from tests.temporary_input import adjust_user_input
from load_user_input import load_user_input
from optimizer import select_squad

#loading config
CONFIG_PATH = Path(__file__).parent / "config.yaml"

def load_config():
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)

config = load_config()
max_budget = config["constraints"]["max_budget"]
horizon_weights = list(config["constraints"]["horizon_weights"].items())

if __name__ == "__main__":
    #USER INPUT LOADING
    #FAKE json response that can be adjusted for testing purposes (my personal team)
    user_input = adjust_user_input(1)

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

    squad_json, transfers_in_json, transfers_out_json = select_squad(
        players,
        gw_weights,
        budget,
        user_chip,
        user_locked_players,
        user_existing_opta_codes,
        user_free_transfers,
        config["constraints"],
    )
    
    ##temporary export
    output_path = f"chip-{user_chip or 'none'}-existing-{bool(user_existing_opta_codes)}-output_.json"
    with open(output_path, "w") as f:
        json.dump(squad_json, f, indent=2)
    print(f"Squad written to {output_path}")

    transfers_in_path = f"chip-{user_chip or 'none'}-existing-{bool(user_existing_opta_codes)}-transfers_in.json"
    with open(transfers_in_path, "w") as f:
        json.dump(transfers_in_json, f, indent=2)
    print(f"Transfers in written to {transfers_in_path}")

    transfers_out_path = f"chip-{user_chip or 'none'}-existing-{bool(user_existing_opta_codes)}-transfers_out.json"
    with open(transfers_out_path, "w") as f:
        json.dump(transfers_out_json, f, indent=2)
    print(f"Transfers out written to {transfers_out_path}")
