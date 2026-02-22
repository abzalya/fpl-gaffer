# Version: 1.0.0

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
    

## httpx over requests for async support and better performance in concurrent requests.
## NOTE: Player id's are season specific. Each player has code which is unique to the player. 