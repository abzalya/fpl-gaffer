# Optimization logic PuLP
# Version: 1.0.0
import pulp

#Objective: Maximize game week points.
def select_squad(players, gw_weights, budget, user_chip, user_locked_players, user_existing_opta_codes, user_free_transfers, config_constraints):
    total_players = config_constraints["max_players"]
    starter_players = config_constraints["starting_players"]
    max_players_per_team = config_constraints["max_players_per_team"]
    position_total_limit = list(config_constraints["position_total_limit"].items())
    position_starting_min = list(config_constraints["position_starting_min"].items())
    set_positions = [pos for pos, _ in position_total_limit]
    max_players_per_position = [lim for _, lim in position_total_limit]
    min_players_per_position = [lim for _, lim in position_starting_min]
    BENCH_COST_EPSILON = config_constraints["bench_cost_modifier"]

    #PROBLEM
    problem = pulp.LpProblem("FPL_Optimizer", pulp.LpMaximize)

    #Decision Variables for pulp
    selected = {p['opta_code']: pulp.LpVariable(f"selected_{p['opta_code']}", cat='Binary') for p in players}
    starters = {p['opta_code']: pulp.LpVariable(f"starter_{p['opta_code']}", cat='Binary') for p in players}

    #OBJECTIVE
    #Horizon filtering already achieves the idea to tell the optimizer for how many horizons to think.
    #bench_boost is the only chip that changes the objective structure (all 15 score).
    #everything else uses the same objective. maximize starters, minimize bench cost.
    if user_chip == "bench_boost":
        problem += pulp.lpSum(
            selected[p['opta_code']] * pulp.lpSum(p[f'h{i+1}'] * gw_weights[i] for i in range(len(gw_weights)))
            for p in players
        ), "Total_Points"
    else:
        starter_pts = pulp.lpSum(
            starters[p['opta_code']] * pulp.lpSum(p[f'h{i+1}'] * gw_weights[i] for i in range(len(gw_weights)))
            for p in players)
        bench_cost = pulp.lpSum(
            (selected[p['opta_code']] - starters[p['opta_code']]) * p['price'] for p in players)
        #hit penalty
        #wildcard and free_hit chips are exempt
        transfer_penalty = 0
        if user_existing_opta_codes and user_chip not in ("wildcard", "free_hit"):
            existing_set = set(user_existing_opta_codes)
            extra_transfers = pulp.LpVariable("extra_transfers", lowBound=0, cat='Continuous')
            transfers_made = pulp.lpSum(
                selected[p['opta_code']] for p in players if p['opta_code'] not in existing_set
            )
            problem += extra_transfers >= transfers_made - user_free_transfers, "Extra_Transfers_Lower_Bound"
            transfer_penalty = 4 * extra_transfers
        problem += starter_pts - BENCH_COST_EPSILON * bench_cost - transfer_penalty, "Total_Points"

    #CONSTRAINTS
    #Budget constraint
    problem += pulp.lpSum(selected[p['opta_code']] * p['price'] for p in players) <= budget, "Budget_Constraint"

    #Players constraints
    problem += pulp.lpSum(selected[p['opta_code']] for p in players) == total_players, "Total_Players_Constraint"

    if user_chip == "bench_boost": #TODO: at the moment as it is now, it thinks all players play for the whatever horizon is set. can i make it think about that only for h1 ? will that even matter ?
        #i might have at least a small idea, we can designate starters to an optimum team only for h2, h3 within bench boost team. so maximize starter points within a team. that way the lowest with expected points in h2 and h3 are benched.
        #THIS COULD WORK TRY LATER
        #all 15 starters
        for p in players:
            problem += starters[p['opta_code']] == selected[p['opta_code']], f"BenchBoost_AllPlay_{p['opta_code']}"
    else:
        #11 starters, and each starter must be one of the selected 15
        problem += pulp.lpSum(starters[p['opta_code']] for p in players) == starter_players, "Starter_Players_Constraint"
        for p in players:
            problem += starters[p['opta_code']] <= selected[p['opta_code']], f"Starter_In_Selected_{p['opta_code']}"

    #Max players per team
    teams = set(p['team'] for p in players)
    for team in teams:
        problem += pulp.lpSum(selected[p['opta_code']] for p in players if p['team'] == team) <= max_players_per_team, f"Max_Players_{team}"

    #Position constraints
    positions = set(p['position'] for p in players)
    for position in positions:
        idx = set_positions.index(position)
        problem += pulp.lpSum(selected[p['opta_code']] for p in players if p['position'] == position) >= min_players_per_position[idx], f"Min_{position}_Selected_Constraint"
        problem += pulp.lpSum(selected[p['opta_code']] for p in players if p['position'] == position) <= max_players_per_position[idx], f"Max_{position}_Selected_Constraint"
        # Starters must also satisfy minimum position counts
        problem += pulp.lpSum(starters[p['opta_code']] for p in players if p['position'] == position) >= min_players_per_position[idx], f"Min_{position}_Starter_Constraint"

    #Existing team constraints
    #Locked players must be selected
    for opta_code in user_locked_players:
        if opta_code in selected:
            problem += selected[opta_code] == 1, f"Locked_{opta_code}"
    # When the user has an existing team and is not on wildcard or free_hit,
    # the transfer penalty discourages unnecessary changes.
    # No hard constraint, penalty should work

    #Solve the problem
    problem.solve()

    #preparing squad
    squad = [p for p in players if pulp.value(selected[p['opta_code']]) == 1]

    #appending is_starter key to the players.
    for p in squad:
        p["starter"] = bool(starters[p["opta_code"]].value())

    #captain logic #no need to recalculate points here right ?
    #triple captain only makes captain points x3. captain still stays the same. no additional logic
    for p in squad:
        p["captain"] = False

    def captain_score(p):
        return sum(p[f"h{i+1}"] * gw_weights[i] for i in range(len(gw_weights)) if f"h{i+1}" in p)

    captain = max((p for p in squad if p["starter"]), key=captain_score)
    captain["captain"] = True

    #preparing transfers out, in
    selected_codes = {p["opta_code"] for p in squad}
    transfers_in = [p for p in squad if p["opta_code"] not in user_existing_opta_codes]
    transfers_out_codes = [code for code in user_existing_opta_codes if code not in selected_codes]
    transfers_out = [p for p in players if p["opta_code"] in transfers_out_codes]

    transfer_hits = (max(0, len(transfers_in) - user_free_transfers))

    #packaging output
    squad_json = package_squad(squad, gw_weights)
    if user_existing_opta_codes: #no need for transfers if no existing team.
        transfers_in_json = package_transfers(transfers_in)
        transfers_out_json = package_transfers(transfers_out)
    else:
        transfers_in_json = None
        transfers_out_json = None

    return squad_json, transfers_in_json, transfers_out_json, transfer_hits


#Output response shape: list of dictionaries
#[{'opta_code': 21205, 'h1': 0.0557, 'predicted_gameweek_id': 31, 'season_id': 25, 'web_name': 'Heaton', 'first_name': 'Tom', 'second_name': 'Heaton', 'team': 'Man Utd', 'position': 'GKP', 'price': 3.8},...]
#Package the squad into a json
def package_squad(squad, gw_weights):

    base_gw = squad[0]["predicted_gameweek_id"]
    num_horizons = len(gw_weights)

    squad_json = {
        "squad": [
            {
                "opta_code": p["opta_code"],
                "name": p["web_name"],
                "club": p["team"],
                "position": p["position"],
                "price": p["price"],
                "is_starter": p["starter"],
                "is_captain": p["captain"],
                "expected_pts": [
                    {"gw": base_gw + i, "pts": round(p[f"h{i+1}"], 2)}
                    for i in range(num_horizons)
                    if f"h{i+1}" in p
                ],
            }
            for p in squad
        ],
    }

    return squad_json

def package_transfers(transfers):
    transfers_json = {
        "transfers": [
            {
                "opta_code": p["opta_code"],
                "name": p["web_name"],
                "club": p["team"],
                "position": p["position"],
                "price": p["price"],
            }
            for p in transfers
        ],
    }

    return transfers_json
