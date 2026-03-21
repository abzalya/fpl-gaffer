# FPL Gaffer — optimizer Entry Point
# Version: 1.0.0
import csv
import pulp
import uuid
import yaml
import pandas as pd
from datetime import datetime, timezone
from pathlib import Path
from data.loader import load_predictions
from temporary_input import adjust_user_input
from load_user_input import load_user_input
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

#USER INPUT LOADING
#FAKE json response that can be adjusted for testing purposes (my personal team)
user_input = adjust_user_input(0)

user_existing_opta_codes, user_locked_players, user_chip, user_bank, user_free_transfers, user_horizon = load_user_input(user_input)

#user choice of horizon and free_hit chip dictate the optimizer goal. filter the input df into the optimizer beforehand. 
def apply_horizon_filter(horizon, chip, df: pd.DataFrame):
    effective_horizon = 1 if chip == "free_hit" else horizon
    return df[df["horizon"] <= effective_horizon]

#slice weights to match the horizons
def slice_weights(df: pd.DataFrame):
    num_horizons = df["horizon"].max()  # or df["horizon"].max()
    return [w for _, w in horizon_weights[:num_horizons]]
#use: gw_weights = slice_weights(predictions)

#preprocess data for the optimizer
def preprocess_data(df: pd.DataFrame):
    pts = df.pivot(index="opta_code", columns="horizon", values="predicted_points")
    pts.columns = [f'h{h}' for h in pts.columns]  # rename 1→h1 etc.
    pts = pts.reset_index()
    meta = df[['opta_code',"predicted_gameweek_id", "season_id", "web_name", "first_name", "second_name", "team", 'position', 'price']].drop_duplicates('opta_code')
    #return pts.merge(meta, on='opta_code')
    processed_df = pts.merge(meta, on='opta_code')
    return processed_df.to_dict(orient='records')

#PREDICTIONS LOADING AS INPUT FOR OPTIMIZER
predictions = load_predictions()
predictions_filtered = apply_horizon_filter(user_horizon, user_chip, predictions)
players = preprocess_data(predictions_filtered)


run_id = uuid.uuid4()
run_at = datetime.now(timezone.utc)


# TEMP: exclude players from these teams entirely
TEMP_EXCLUDED_TEAMS = {"Arsenal", "Man City", "Wolves", "Crystal Palace"}
players = [p for p in players if p.get("team", "") not in TEMP_EXCLUDED_TEAMS]

# Chip flags (default: no chips, fresh squad selection)
bench_boost = 0
free_hit = 1
wildcard = 0
existing_team_test_var = 0

# Locked players: derived from existing_squad entries where locked=true
locked_players = []  # e.g. [p["player_id"] for p in existing_squad if p.get("locked")]

# Weights THIS IS GOOD KEEP
gw_weights = slice_weights(test)
gw_weights_single = [1.0] # this is now legacy, delete once optimizer code refactored. 
BENCH_COST_EPSILON = 0.01 # pushing bench players to have minimal cost. 

# Budget / squad size aliases
budget = max_budget
total_players = max_players
starter_players = starting_players

# Position order and limits (derived from config)
set_positions = [pos for pos, _ in position_total_limit]
max_players_per_position = [lim for _, lim in position_total_limit]
min_players_per_position = [lim for _, lim in position_starting_min]

#test on old code
##MAIN OPTIMIZATION CODE
#Problem
problem = pulp.LpProblem("FPL_Optimizer", pulp.LpMaximize)

#Decision Variables
#Selected players (binary)
selected = {player['opta_code']: pulp.LpVariable(f"selected_{player['opta_code']}", cat='Binary') for player in players}
starters = {player['opta_code']: pulp.LpVariable(f"starter_{player['opta_code']}", cat='Binary') for player in players}

#existing players needs adjustment
existing_players = [p for p in players if p["opta_code"] in existing_opta_codes]

#Objective: Maximize game week points.
def select_squad():
    if bench_boost == 1:
        # All 15 players score — maximize all selected for single GW
        problem += pulp.lpSum(
            selected[player['opta_code']] * pulp.lpSum(player[f'h{i+1}'] * gw_weights_single[i] for i in range(len(gw_weights_single)))
            for player in players
        ), "Total_Points"
    elif free_hit == 1:
        # 11 starters score for single GW; bench 4 are cheap fillers
        starter_pts = pulp.lpSum(
            starters[player['opta_code']] * pulp.lpSum(player[f'h{i+1}'] * gw_weights_single[i] for i in range(len(gw_weights_single)))
            for player in players
        )
        bench_cost = pulp.lpSum(
            (selected[player['opta_code']] - starters[player['opta_code']]) * player['price'] for player in players
        )
        problem += starter_pts - BENCH_COST_EPSILON * bench_cost, "Total_Points"
    elif wildcard == 1 or existing_team_test_var == 0:
        # 11 starters optimized over 5 GWs; bench 4 are cheap fillers
        starter_pts = pulp.lpSum(
            starters[player['opta_code']] * pulp.lpSum(player[f'h{i+1}'] * gw_weights[i] for i in range(len(gw_weights)))
            for player in players
        )
        bench_cost = pulp.lpSum(
            (selected[player['opta_code']] - starters[player['opta_code']]) * player['price'] for player in players
        )
        problem += starter_pts - BENCH_COST_EPSILON * bench_cost, "Total_Points"
    else:
        # Existing team: same as wildcard for now (hit penalty TODO)
        starter_pts = pulp.lpSum(
            starters[player['opta_code']] * pulp.lpSum(player[f'h{i+1}'] * gw_weights[i] for i in range(len(gw_weights)))
            for player in players
        )
        bench_cost = pulp.lpSum(
            (selected[player['opta_code']] - starters[player['opta_code']]) * player['price'] for player in players
        )
        problem += starter_pts - BENCH_COST_EPSILON * bench_cost, "Total_Points"

    #Constraints
    #Budget constraint
    problem += pulp.lpSum(selected[player['opta_code']] * player['price'] for player in players) <= budget, "Budget_Constraint"

    #Players constraints
    problem += pulp.lpSum(selected[player['opta_code']] for player in players) == total_players, "Total_Players_Constraint"

    if bench_boost == 1:
        # All 15 play — starters == selected
        for player in players:
            problem += starters[player['opta_code']] == selected[player['opta_code']], f"BenchBoost_AllPlay_{player['opta_code']}"
    else:
        # Exactly 11 starters, and each starter must be one of the selected 15
        problem += pulp.lpSum(starters[player['opta_code']] for player in players) == starter_players, "Starter_Players_Constraint"
        for player in players:
            problem += starters[player['opta_code']] <= selected[player['opta_code']], f"Starter_In_Selected_{player['opta_code']}"

    #Max players per team
    teams = set(player['team'] for player in players)
    for team in teams:
        problem += pulp.lpSum(selected[player['opta_code']] for player in players if player['team'] == team) <= max_players_per_team, f"Max_Players_{team}"

    #Position constraints
    positions = set(player['position'] for player in players)
    for position in positions:
        problem += pulp.lpSum(selected[player['opta_code']] for player in players if player['position'] == position) >= min_players_per_position[set_positions.index(position)], f"Min_{position}_Selected_Constraint"
        problem += pulp.lpSum(selected[player['opta_code']] for player in players if player['position'] == position) <= max_players_per_position[set_positions.index(position)], f"Max_{position}_Selected_Constraint"
        # Starters must also satisfy minimum position counts
        problem += pulp.lpSum(starters[player['opta_code']] for player in players if player['position'] == position) >= min_players_per_position[set_positions.index(position)], f"Min_{position}_Starter_Constraint"

    # Locked players must be selected
    for pid in locked_players:
        if pid in selected:
            problem += selected[pid] == 1, f"Locked_{pid}"

    #Solve the problem
    problem.solve()

    optimized_team = [player for player in players if pulp.value(selected[player['opta_code']]) == 1]
    return optimized_team

#Output results
optimized_team = [player for player in players if pulp.value(selected[player['opta_code']]) == 1]
print(optimized_team)
total_price = sum(player['price'] for player in optimized_team)

#print(f"Optimized Team: {optimized_team}")
#print(f"Total Price: {total_price}")

for player in optimized_team:
    print("Name:", player["web_name"])
    print("Club:", player["team"])
    print("Position:", player["position"])
    print("-------------------")

grand_total = 0
for player in optimized_team:
    total_points = sum(player[f"h{i+1}"] for i in range(len(gw_weights)))
    grand_total += total_points

print("Grand Total Points:", grand_total)

#TODO: Add an existing team constraint. look at the existing team and optimize based on that. Limit transfers to 5? add a hit penalty for transfers over free transfers.
#TODO: Add captain and triple captain.
#i dont need the captain logic to be in the optimizer i can have it outside and simply captain one with the most points per gameweek predicted. 


#export
result_team = []
for p in optimized_team:
    player_row = p.copy()
    player_row["starter"] = bool(starters[p["opta_code"]].value())
    result_team.append(player_row)

#Output response shape: list of dictionaries
#[{'opta_code': 21205, 'h1': 0.0557, 'predicted_gameweek_id': 31, 'season_id': 25, 'web_name': 'Heaton', 'first_name': 'Tom', 'second_name': 'Heaton', 'team': 'Man Utd', 'position': 'GKP', 'price': 3.8},...]
#Package the squad into a json
def package_squad(result_team, gw_weights):

    base_gw = result_team[0]["predicted_gameweek_id"]
    num_horizons = len(gw_weights)

    squad_jsonb = {
        "squad": [
            {
                "opta_code": p["opta_code"],
                "name": p["web_name"],
                "club": p["team"],
                "position": p["position"],
                "price": p["price"],
                "is_starter": p["starter"],
                "captain": False,  # TODO
                "expected_pts": [
                    {"gw": base_gw + i, "pts": round(p[f"h{i+1}"], 2)}
                    for i in range(num_horizons)
                    if f"h{i+1}" in p
                ],
            }
            for p in result_team
        ],
    }

    return squad_jsonb

##temporary export
import json
squad_json = package_squad(result_team, gw_weights)
output_path = f"f{free_hit}w{wildcard}b{bench_boost}e{existing_team_test_var}-output_.json"
with open(output_path, "w") as f:
    json.dump(squad_json, f, indent=2)
print(f"Squad written to {output_path}")
