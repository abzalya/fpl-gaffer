import random
import csv

random.seed(42)

# --- Club and player name pools ---
clubs = [
    "Arsenal", "Aston Villa", "Brentford", "Brighton", "Chelsea",
    "Crystal Palace", "Everton", "Fulham", "Ipswich", "Leicester",
    "Liverpool", "Man City", "Man Utd", "Newcastle", "Nottm Forest",
    "Southampton", "Spurs", "West Ham", "Wolves", "Bournemouth"
]

first_names = [
    "James", "Oliver", "Harry", "Jack", "George", "Noah", "Charlie", "Liam",
    "Thomas", "Lucas", "Mason", "Ethan", "Logan", "Aiden", "Ryan", "Nathan",
    "Dylan", "Aaron", "Leon", "Kai", "Marcus", "Jordan", "Tyler", "Callum",
    "Reece", "Ben", "Sam", "Tom", "Joe", "Dan"
]

last_names = [
    "Smith", "Jones", "Williams", "Taylor", "Brown", "Davies", "Evans",
    "Wilson", "Thomas", "Roberts", "Johnson", "White", "Martin", "Anderson",
    "Thompson", "Garcia", "Martinez", "Robinson", "Clark", "Lewis",
    "Walker", "Hall", "Allen", "Young", "King", "Wright", "Scott", "Green",
    "Baker", "Adams", "Nelson", "Carter", "Mitchell", "Perez", "Turner",
    "Phillips", "Campbell", "Parker", "Edwards", "Collins"
]

positions = ["GKP", "DEF", "MID", "FWD"]

# Position distribution across ~200 players: 20 GK, 60 DEF, 80 MID, 40 FWD
position_pool = (
    ["GKP"] * 20 +
    ["DEF"] * 60 +
    ["MID"] * 80 +
    ["FWD"] * 40
)

# Price ranges per position (in millions)
price_ranges = {
    "GKP": (4.0, 6.5),
    "DEF": (4.0, 7.5),
    "MID": (4.5, 13.0),
    "FWD": (5.5, 14.0),
}

# Base weekly points range per position (better players score more)
# Tier is determined by price — higher price = higher expected points
def base_points(position, price):
    price_min, price_max = price_ranges[position]
    # normalise price to 0-1 tier
    tier = (price - price_min) / (price_max - price_min)

    base_ranges = {
        "GKP": (2.5, 5.5),
        "DEF": (2.0, 6.5),
        "MID": (2.5, 8.5),
        "FWD": (3.0, 9.0),
    }
    lo, hi = base_ranges[position]
    return lo + tier * (hi - lo)


def generate_weekly_points(base, weeks=5):
    """Generate noisy predicted points for each gameweek."""
    points = []
    for _ in range(weeks):
        noise = random.gauss(0, 1.2)
        val = round(max(1.0, base + noise), 2)
        points.append(val)
    return points


# --- Generate Players ---
players = []
used_names = set()
random.shuffle(position_pool)

# Distribute players across clubs roughly evenly (10 per club = 200)
club_pool = clubs * 10
random.shuffle(club_pool)

for i, position in enumerate(position_pool):
    # Unique name
    while True:
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        if name not in used_names:
            used_names.add(name)
            break

    club = club_pool[i]
    price_min, price_max = price_ranges[position]
    price = round(random.uniform(price_min, price_max) * 2) / 2  # round to 0.5

    base = base_points(position, price)
    gw_points = generate_weekly_points(base)

    players.append({
        "id": i + 1,
        "name": name,
        "club": club,
        "position": position,
        "price": price,
        "gw1": gw_points[0],
        "gw2": gw_points[1],
        "gw3": gw_points[2],
        "gw4": gw_points[3],
        "gw5": gw_points[4],
    })


# --- Generate Fake Existing Team (15 players) ---
# Must satisfy: 2 GKP, 5 DEF, 5 MID, 3 FWD, budget <= 100M, max 3 per club

def pick_existing_team(players, budget=100.0):
    requirements = {"GKP": 2, "DEF": 5, "MID": 5, "FWD": 3}
    team = []
    used_ids = set()
    club_counts = {}
    spent = 0

    # Sort each position pool by price to pick affordable players
    # Targeting roughly £6.5M average per player to stay under £100M
    for pos, count in requirements.items():
        pool = sorted(
            [p for p in players if p["position"] == pos],
            key=lambda x: abs(x["price"] - 6.0)  # prefer players near £6M
        )
        picked = 0
        for p in pool:
            if p["id"] in used_ids:
                continue
            if club_counts.get(p["club"], 0) >= 3:
                continue
            if spent + p["price"] > budget - (14 - len(team) - 1) * 4.0:
                continue  # make sure we can still afford remaining slots
            team.append(p)
            used_ids.add(p["id"])
            club_counts[p["club"]] = club_counts.get(p["club"], 0) + 1
            spent += p["price"]
            picked += 1
            if picked == count:
                break

    return team


existing_team = pick_existing_team(players)
existing_team_ids = {p["id"] for p in existing_team}
total_team_cost = sum(p["price"] for p in existing_team)


# --- Save to CSV ---
with open("players.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["id","name","club","position","price","gw1","gw2","gw3","gw4","gw5"])
    writer.writeheader()
    writer.writerows(players)

with open("existing_team.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["id","name","club","position","price","gw1","gw2","gw3","gw4","gw5"])
    writer.writeheader()
    writer.writerows(existing_team)

print(f"Generated {len(players)} players → players.csv")
print(f"\nExisting team ({len(existing_team)} players, £{total_team_cost:.1f}M):")
print(f"{'ID':<5} {'Name':<22} {'Club':<16} {'Pos':<5} {'Price':<7} GW1   GW2   GW3   GW4   GW5")
print("-" * 85)
for p in sorted(existing_team, key=lambda x: x["position"]):
    print(f"{p['id']:<5} {p['name']:<22} {p['club']:<16} {p['position']:<5} £{p['price']:<6} "
          f"{p['gw1']:<6}{p['gw2']:<6}{p['gw3']:<6}{p['gw4']:<6}{p['gw5']}")
print("-" * 85)
print(f"Total cost: £{total_team_cost:.1f}M")
