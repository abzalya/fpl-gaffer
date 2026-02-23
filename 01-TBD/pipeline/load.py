# Version: v1.0.0

from sqlalchemy.dialects.postgresql import insert as pg_insert
from db.schema import public_seasons, public_gameweeks, public_teams, public_players, gameweeks, teams, player_snapshots, player_future_fixtures, player_gw_history
from pipeline.clean import clean_future_fixture, clean_player_snapshot, clean_gameweeks, clean_gw_history, clean_team

# PUBLIC SCHEMA
# 1. SEASON
def upsert_public_season(engine, season_id: int):
    values = {"id": season_id, "name": f"20{season_id}/{season_id+1}", "start_year": season_id, "end_year": season_id+1, "is_current": True}
    #TODO: implement a check where we check for existing data and not updating if exists. upserting for now, no harm. 
    #TODO: how do i flip old season entry to is_current = false? need to implement some logic around that. maybe a separate function to mark old season as inactive before upserting new season as active.

    stmt = pg_insert(public_seasons).values(values)
    stmt = stmt.on_conflict_do_nothing(
        constraint="uq_public_seasons_id"
    )
    with engine.begin() as conn:
        conn.execute(stmt)

# TODO: implement a check where we check for existing data and not updating if exists. upserting for now, no harm.
# 2. GAMEWEEKS
def upsert_public_gameweeks(engine, gameweek_data: list[dict], season_id: int):
    if not gameweek_data:
        print("No gameweek data to upsert.")
        return
    
    PUBLIC_GW_COLS = {"gameweek_id", "season_id", "finished", "is_current", "is_next"}
    
    cleaned = [
        {k: v for k, v in clean_gameweeks(row, season_id).items() if k in PUBLIC_GW_COLS}
        for row in gameweek_data
    ]

    stmt = pg_insert(public_gameweeks).values(cleaned)
    stmt = stmt.on_conflict_do_update(
        constraint="uq_public_gameweeks_gw_season",
        set_={col: stmt.excluded[col] for col in cleaned[0].keys()}
    )
    with engine.begin() as conn:
        conn.execute(stmt)

# 3. TEAMS
def upsert_public_teams(engine, team_data: list[dict], season_id: int):
    if not team_data:
        print("No team data to upsert.")
        return
    
    PUBLIC_TEAMS_COLS = {"team_id", "season_id", "code", "name", "short_name"}

    cleaned = [
        {k: v for k, v in clean_team(row, season_id).items() if k in PUBLIC_TEAMS_COLS}
        for row in team_data
    ]

    stmt = pg_insert(public_teams).values(cleaned)
    stmt = stmt.on_conflict_do_update(
        constraint="uq_public_teams_id_season",
        set_={col: stmt.excluded[col] for col in cleaned[0].keys()}
    )
    with engine.begin() as conn:
        conn.execute(stmt)

# 4. PLAYERS                    
def upsert_public_players(engine, player_data: list[dict], fetched_gameweek_id: int,season_id: int):
    if not player_data:
        print("No player data to upsert.")
        return
    
    PUBLIC_PLAYER_COLS = {"opta_code", "player_id", "season_id", "web_name", "first_name", "second_name", "team_id", "element_type", "status", "now_cost"}
    
    cleaned = [
        {k: v for k, v in clean_player_snapshot(row, fetched_gameweek_id, season_id).items() if k in PUBLIC_PLAYER_COLS}
        for row in player_data
    ]
    
    stmt = pg_insert(public_players).values(cleaned)
    stmt = stmt.on_conflict_do_update(
        constraint="uq_public_players_opta_season",
        set_={col: stmt.excluded[col] for col in cleaned[0].keys()}
    )
    with engine.begin() as conn:
        conn.execute(stmt)

# ARCHIVE SCHEMA
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