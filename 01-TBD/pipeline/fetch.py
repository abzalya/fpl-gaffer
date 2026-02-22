# Version: 1.0.1
# Note: Introducing rate limiting and retry logic. 

import httpx
import asyncio
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

base_url = "https://fantasy.premierleague.com/api"


async def fetch_bootstrap_static(client: httpx.AsyncClient) -> dict:
    response = await client.get(f"{base_url}/bootstrap-static/")
    response.raise_for_status()
    return response.json()


async def fetch_fixtures(client: httpx.AsyncClient) -> list:
    response = await client.get(f"{base_url}/fixtures/")
    response.raise_for_status()
    return response.json()


@retry(
    wait=wait_exponential(multiplier=1, min=1, max=30),
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type(httpx.HTTPStatusError),
)
async def _fetch_with_retry(client: httpx.AsyncClient, player_id: int) -> dict:
    """Inner function: makes one HTTP call. Retried by tenacity on failure."""
    response = await client.get(f"{base_url}/element-summary/{player_id}/")
    response.raise_for_status()
    return response.json()


async def fetch_player_details(client: httpx.AsyncClient, semaphore: asyncio.Semaphore, player_id: int) -> dict:
    """Fetch element-summary for a single player.
    Semaphore limits concurrent requests. Retry handled internally.
    """
    async with semaphore:
        return await _fetch_with_retry(client, player_id)


async def fetch_all_player_details(client: httpx.AsyncClient, player_ids: list[int], concurrency: int = 20) -> list[dict | Exception]:
    """Fetch element-summary for all players concurrently.

    Caps at `concurrency` simultaneous requests (default: 20, safely under FPL's ~50 req/s).
    Returns list aligned with player_ids — failed fetches are returned as Exception objects,
    not raised, so one failure doesn't kill the entire batch.
    """
    semaphore = asyncio.Semaphore(concurrency)
    tasks = [fetch_player_details(client, semaphore, pid) for pid in player_ids]
    return await asyncio.gather(*tasks, return_exceptions=True)

## httpx over requests for async support and better performance in concurrent requests.
## NOTE: Player id's are season specific. Each player has code which is unique to the player. 