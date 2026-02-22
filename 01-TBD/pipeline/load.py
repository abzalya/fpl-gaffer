# Version: v1.0.0

from sqlalchemy.dialects.postgresql import insert as pg_insert
from db.schema import gameweeks, teams, player_snapshots, player_future_fixtures, player_gw_history
from pipeline.clean import clean_future_fixture, clean_player_snapshot, clean_gameweeks, clean_gw_history, clean_team

# 1. GAMEWEEKS
def upsert_gameweeks(engine, gameweek_data: list[dict], season_id: int):
    if not gameweek_data:
        print("No gameweek data to upsert.")
        return
    
    cleaned = [clean_gameweeks(row, season_id) for row in gameweek_data]
    
    stmt = pg_insert(gameweeks).values(cleaned)
    stmt = stmt.on_conflict_do_update(
        constraint="uq_gameweeks_gw_season",
        set_={col: stmt.excluded[col] for col in cleaned[0].keys()}
    )
    with engine.begin() as conn:
        conn.execute(stmt)

# 2. TEAMS
def upsert_teams(engine, team_data: list[dict], season_id: int):
    if not team_data:
        print("No team data to upsert.")
        return
    
    cleaned = [clean_team(row, season_id) for row in team_data]
    
    stmt = pg_insert(teams).values(cleaned)
    stmt = stmt.on_conflict_do_update(
        constraint="uq_teams_id_season",
        set_={col: stmt.excluded[col] for col in cleaned[0].keys()}
    )
    with engine.begin() as conn:
        conn.execute(stmt)

# 3. PLAYERS SNAPSHOT
def upsert_player_snapshot(engine, player_data: list[dict], fetched_gameweek_id: int, season_id: int):
    if not player_data:
        print("No player snapshot data to upsert.")
        return
    
    cleaned = [clean_player_snapshot(row, fetched_gameweek_id, season_id) for row in player_data]
    
    stmt = pg_insert(player_snapshots).values(cleaned)
    stmt = stmt.on_conflict_do_update(
        constraint="uq_snapshots_player_fgw_season",
        set_={col: stmt.excluded[col] for col in cleaned[0].keys()}
    )
    with engine.begin() as conn:
        conn.execute(stmt)

# 4. PLAYER FUTURE FIXTURES
def upsert_future_fixtures(engine, player_id: int, opta_code: str, fixture_data: list[dict], fetched_gameweek_id: int):
    if not fixture_data:
        print(f"No future fixture data to upsert for player {player_id}.")
        return
    
    cleaned = [clean_future_fixture(row, player_id, fetched_gameweek_id, opta_code) for row in fixture_data]
    
    stmt = pg_insert(player_future_fixtures).values(cleaned)
    stmt = stmt.on_conflict_do_update(
        constraint="uq_future_fixtures_player_fgw_fixture",
        set_={col: stmt.excluded[col] for col in cleaned[0].keys()}
    )
    with engine.begin() as conn:
        conn.execute(stmt)

# 5. PLAYER GAMEWEEK HISTORY
def upsert_gw_history(engine, player_id: int, season_id: int, opta_code: str, history_data: list[dict]):
    if not history_data:
        print(f"No gameweek history data to upsert for player {player_id}.")
        return
    
    cleaned = [clean_gw_history(row, player_id, opta_code, season_id) for row in history_data]
    
    stmt = pg_insert(player_gw_history).values(cleaned)
    stmt = stmt.on_conflict_do_update(
        constraint="uq_history_player_fixture_season",
        set_={col: stmt.excluded[col] for col in cleaned[0].keys()}
    )
    with engine.begin() as conn:
        conn.execute(stmt)