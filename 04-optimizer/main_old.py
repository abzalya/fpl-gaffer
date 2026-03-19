import pulp 
from data_loader import load_data
import config
import csv


players = load_data('data/players.csv')
existing_team = load_data('data/existing_team.csv')

#User input
free_hit = 0 
wildcard = 0
bench_boost = 0
triple_captain = 0
free_transfers = 2
existing_team_test_var = 0


#Optimizer Code in main.py TEMPORARAILY, will be moved to a function in optimizer.py later
#Constraints
budget = config.BUDGET
total_players = config.TOTAL_PLAYERS
starter_players = config.STARTING_PLAYERS
max_players_per_team = config.MAX_PLAYERS_PER_TEAM
set_positions = config.POSITIONS

#Positions 
min_players_per_position = config.MIN_PLAYERS_PER_POSITION
max_players_per_position = config.MAX_PLAYERS_PER_POSITION

#Penalties
hit_penalty = config.HIT_PENALTY

#Game Week Weights
gw_weights = config.GW_WEIGHTS
gw_weights_single = [1.0, 0.0, 0.0, 0.0, 0.0] #if we want to optimize for a single game week, set the weight for that game week to 1 and the rest to 0

# Small weight to push bench players towards cheaper options without overriding the main objective
BENCH_COST_EPSILON = 0.001

##MAIN OPTIMIZATION CODE
#Problem
problem = pulp.LpProblem("FPL_Optimizer", pulp.LpMaximize)

#Decision Variables
#Selected players (binary)
selected = {player['id']: pulp.LpVariable(f"selected_{player['id']}", cat='Binary') for player in players}
starters = {player['id']: pulp.LpVariable(f"starter_{player['id']}", cat='Binary') for player in players}

#Objective: Maximize game week points.
if bench_boost == 1:
    # All 15 players score — maximize all selected for single GW
    problem += pulp.lpSum(
        selected[player['id']] * pulp.lpSum(player[f'gw{i+1}'] * gw_weights_single[i] for i in range(len(gw_weights_single)))
        for player in players
    ), "Total_Points"
elif free_hit == 1:
    # 11 starters score for single GW; bench 4 are cheap fillers
    starter_pts = pulp.lpSum(
        starters[player['id']] * pulp.lpSum(player[f'gw{i+1}'] * gw_weights_single[i] for i in range(len(gw_weights_single)))
        for player in players
    )
    bench_cost = pulp.lpSum(
        (selected[player['id']] - starters[player['id']]) * player['price'] for player in players
    )
    problem += starter_pts - BENCH_COST_EPSILON * bench_cost, "Total_Points"
elif wildcard == 1 or existing_team_test_var == 0:
    # 11 starters optimized over 5 GWs; bench 4 are cheap fillers
    starter_pts = pulp.lpSum(
        starters[player['id']] * pulp.lpSum(player[f'gw{i+1}'] * gw_weights[i] for i in range(len(gw_weights)))
        for player in players
    )
    bench_cost = pulp.lpSum(
        (selected[player['id']] - starters[player['id']]) * player['price'] for player in players
    )
    problem += starter_pts - BENCH_COST_EPSILON * bench_cost, "Total_Points"
else:
    # Existing team: same as wildcard for now (hit penalty TODO)
    starter_pts = pulp.lpSum(
        starters[player['id']] * pulp.lpSum(player[f'gw{i+1}'] * gw_weights[i] for i in range(len(gw_weights)))
        for player in players
    )
    bench_cost = pulp.lpSum(
        (selected[player['id']] - starters[player['id']]) * player['price'] for player in players
    )
    problem += starter_pts - BENCH_COST_EPSILON * bench_cost, "Total_Points"

#Constraints
#Budget constraint
problem += pulp.lpSum(selected[player['id']] * player['price'] for player in players) <= budget, "Budget_Constraint"

#Players constraints
problem += pulp.lpSum(selected[player['id']] for player in players) == total_players, "Total_Players_Constraint"

if bench_boost == 1:
    # All 15 play — starters == selected
    for player in players:
        problem += starters[player['id']] == selected[player['id']], f"BenchBoost_AllPlay_{player['id']}"
else:
    # Exactly 11 starters, and each starter must be one of the selected 15
    problem += pulp.lpSum(starters[player['id']] for player in players) == starter_players, "Starter_Players_Constraint"
    for player in players:
        problem += starters[player['id']] <= selected[player['id']], f"Starter_In_Selected_{player['id']}"

#Max players per team
teams = set(player['club'] for player in players)
for team in teams:
    problem += pulp.lpSum(selected[player['id']] for player in players if player['club'] == team) <= max_players_per_team, f"Max_Players_{team}"

#Position constraints
positions = set(player['position'] for player in players)
for position in positions:
    problem += pulp.lpSum(selected[player['id']] for player in players if player['position'] == position) >= min_players_per_position[set_positions.index(position)], f"Min_{position}_Selected_Constraint"
    problem += pulp.lpSum(selected[player['id']] for player in players if player['position'] == position) <= max_players_per_position[set_positions.index(position)], f"Max_{position}_Selected_Constraint"
    # Starters must also satisfy minimum position counts
    problem += pulp.lpSum(starters[player['id']] for player in players if player['position'] == position) >= min_players_per_position[set_positions.index(position)], f"Min_{position}_Starter_Constraint"

#Solve the problem
problem.solve()

#Output results
optimized_team = [player for player in players if pulp.value(selected[player['id']]) == 1]
total_price = sum(player['price'] for player in optimized_team)

#print(f"Optimized Team: {optimized_team}")
#print(f"Total Price: {total_price}")

for player in optimized_team:
    print("Name:", player["name"])
    print("Club:", player["club"])
    print("Position:", player["position"])
    print("-------------------")

position_counts = {}

for player in optimized_team:
    pos = player["position"]
    position_counts[pos] = position_counts.get(pos, 0) + 1

print("Number of players per position:")
for pos, count in position_counts.items():
    print(pos, ":", count)

grand_total = 0

for player in optimized_team:
    total_points = (
        player["gw1"] +
        player["gw2"] +
        player["gw3"] +
        player["gw4"] +
        player["gw5"]
    )

    grand_total += total_points

print("Grand Total Points:", grand_total)

#TODO: Add an existing team constraint. look at the existing team and optimize based on that. Limit transfers to 5? add a hit penalty for transfers over free transfers.
#TODO: Add captain and triple captain. see how it affects the outcomes. (Probably nothing changes as captain will usually be the player with most expected points anyway) 

#export
result_team = []
for p in optimized_team:
    player_row = p.copy()
    player_row["starter"] = bool(starters[p["id"]].value())
    result_team.append(player_row)

with open(f"f{free_hit}w{wildcard}b{bench_boost}e{existing_team_test_var}-output_.csv", "w", newline="") as f:
    fieldnames = result_team[0].keys()
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(result_team)