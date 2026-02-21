import httpx
import asyncio
import json

base_url = "https://fantasy.premierleague.com/api"

async def fetch_bootstrap_static():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{base_url}/bootstrap-static/")
        return response.json()
    
async def fetch_player_details(player_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{base_url}/element-summary/{player_id}/")
        response.raise_for_status()  # Ensure we catch any HTTP errors
        return response.json()
    
async def fetch_fixtures():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{base_url}/fixtures/")
        return response.json()
    
## Example usage
data = asyncio.run(fetch_bootstrap_static())
# players = data['elements']
# print(players[0])  # Print the first player's data

## httpx over requests for async support and better performance in concurrent requests.

## NOTE: Player id's are season specific. Each player has code which is unique to the player. 

with open('fpl_raw_data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)


##GEMINI adding a gameweek id to the player data for clarity and ease of use in downstream processing. needed?
def get_fpl_player_data(player_web_name="Raya"):
    # 1. Fetch the main data
    data_test = asyncio.run(fetch_bootstrap_static())

    # 2. Find the Current Gameweek
    # We look through 'events' to find the one where 'is_current' is True
    current_gw = None
    for event in data_test['events']:
        if event['is_current']:
            current_gw = event['id']
            break
    
    # 3. Find the Player
    # We look through 'elements' (the API term for players)
    player_data = None
    for player in data_test['elements']:
        if player['web_name'] == player_web_name:
            player_data = player
            break

    if not player_data:
        return f"Player '{player_web_name}' not found."

    # 4. Inject the Gameweek into the player dictionary for clarity
    player_data['extracted_gameweek'] = current_gw

    return player_data

##my best explanation for the above function is that, when we call bootstrap static and elements, within we get data for all player for that gameweel. but that endpoint has no gameweek id. but, events has a current gameweek id by it being "active". and at any given time when we call the api. only 1 gameweek is active. so by appending that data to the response, i can get the gameweek i fetched that data. 

# --- Execution ---
#player_info = get_fpl_player_data("Raya")

# Pretty-print the dictionary
#print(player_info)
