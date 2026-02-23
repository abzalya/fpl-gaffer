# Main pipeline orchestration

# Version 1.0.0
from db.engine import engine
from pipeline.load import upsert_gameweeks, upsert_public_season, upsert_teams, upsert_player_snapshot, upsert_future_fixtures, upsert_gw_history, upsert_public_players, upsert_public_teams, upsert_public_gameweeks
from pipeline.fetch import fetch_bootstrap_static, fetch_fixtures, fetch_all_player_details
import httpx
import asyncio  
from dotenv import load_dotenv
import os

load_dotenv()
season_id = int(os.getenv("current_season_id"))


async def run_pipeline():
    #TODO: implement. 
    upsert_public_season(engine, season_id)

    async with httpx.AsyncClient(timeout=30.0) as client:
        
        bootstrap = await fetch_bootstrap_static(client)
        
        gameweek_data = bootstrap["events"]
        team_data     = bootstrap["teams"]
        player_snapshot_data   = bootstrap["elements"]

        fetched_gameweek_id = next(
            (e["id"] for e in gameweek_data if e["is_current"]), None
        )
        
        if fetched_gameweek_id is None:
            print("No current gameweek found in bootstrap data. Aborting.")
            return

        # Upsert public gameweeks, teams, players
        upsert_public_gameweeks(engine, gameweek_data, season_id)
        upsert_public_teams(engine, team_data, season_id)
        upsert_public_players(engine, player_snapshot_data, fetched_gameweek_id, season_id)


        # Upsert archive gameweeks, teams, player snapshots
        upsert_gameweeks(engine, gameweek_data, season_id)
        upsert_teams(engine, team_data, season_id)
        upsert_player_snapshot(engine, player_snapshot_data, fetched_gameweek_id, season_id)
        
        # Fetching details for all players concurrently with rate limiting and retry logic
        player_ids = [p["id"] for p in player_snapshot_data]
        results    = await fetch_all_player_details(client, player_ids)

        # Upsert player details, log failures
        for player, result in zip(player_snapshot_data, results):
            if isinstance(result, Exception):
                print(f"Failed for player {player['id']}: {result}")
                continue

            opta_code = int(player["code"])
            player_id = player["id"]

            upsert_future_fixtures(engine, player_id, opta_code, result["fixtures"], fetched_gameweek_id)
            upsert_gw_history(engine, player_id, season_id, opta_code, result["history"])

if __name__ == "__main__":
    asyncio.run(run_pipeline())