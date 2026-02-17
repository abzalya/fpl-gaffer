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

##MAIN OPTIMIZATION CODE
#Problem 
problem = pulp.LpProblem("FPL_Optimizer", pulp.LpMaximize)

#Decision Variables
#Selected players (binary)
selected = {player['id']: pulp.LpVariable(f"selected_{player['id']}", cat='Binary') for player in players} #.iterrows()
starters = {player['id']: pulp.LpVariable(f"starter_{player['id']}", cat='Binary') for player in players} #.iterrows()

#Objective: Maximize game week points. 
if bench_boost == 1: #If bench boost is active, then maximize points for all 15 players
    problem += pulp.lpSum([selected[player['id']] * pulp.lpSum([player[f'gw{i+1}'] * gw_weights[i] for i in range(len(gw_weights))]) for player in players]), "Total_Points"
elif free_hit ==1: #Starters only for 1 game week. 
    problem += pulp.lpSum([starters[player['id']] * pulp.lpSum([player[f'gw{i+1}'] * gw_weights_single[i] for i in range(len(gw_weights_single))]) for player in players]), "Total_Points"
elif wildcard == 1 or existing_team_test_var == 0: #new team or wildcard optimization. 
    problem += pulp.lpSum([starters[player['id']] * pulp.lpSum([player[f'gw{i+1}'] * gw_weights[i] for i in range(len(gw_weights))]) for player in players]), "Total_Points"
else: #TODO: base case (wildcard/new team ) for now, implement existing team and hit penalty later
    problem += pulp.lpSum([starters[player['id']] * pulp.lpSum([player[f'gw{i+1}'] * gw_weights[i] for i in range(len(gw_weights))]) for player in players]), "Total_Points"

#Constraints
#Budget constraint
problem += pulp.lpSum(selected[player['id']] * player['price'] for player in players) <= budget, "Budget_Constraint"

#Players constraints
problem += pulp.lpSum(selected[player['id']] for player in players) == total_players, "Total_Players_Constraint"
problem += pulp.lpSum(starters[player['id']] for player in players) == starter_players, "Starter_Players_Constraint"

#Max players per team
teams = set(player['club'] for player in players)
for team in teams:
    problem += pulp.lpSum(selected[player['id']] for player in players if player['club'] == team) <= max_players_per_team, f"Max_Players_{team}"

#Position constraints
positions = set(player['position'] for player in players)
for position in positions:
    problem += pulp.lpSum(selected[player['id']] for player in players if player['position'] == position) >= min_players_per_position[set_positions.index(position)], f"Min_{position}_Constraint"
    problem += pulp.lpSum(selected[player['id']] for player in players if player['position'] == position) <= max_players_per_position[set_positions.index(position)], f"Max_{position}_Constraint"

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

#TODO: introduce tokens and tweak algo
#TODO: introduce starter variable, if bench boost = 1, then maximise points for 15 players only gw1, otherwise, maximise points for 11 players all gws + 4 players cheapest to fill positions
#TODO: if existing team = 0, or wildcard = 1 then maximise points for 11 players all gws
#TODO: if freehit = 1, then maximise points for 11 players all gws + 4 players cheapest to fill positions
#TODO: if existing team, then maximise points for 11 players all gws + 4 players cheapest to fill positions, but add hit penalty for players not in existing team. Limit to 5 transfers? 

#export
result_team = []
for p in optimized_team:
    player_row = p.copy()
    player_row["starter"] = bool(starters[p["id"]].value())
    result_team.append(player_row)

with open(f"output_.csv", "w", newline="") as f:
    fieldnames = result_team[0].keys()
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(result_team)