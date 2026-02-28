# SQLAlchemy schema and table definitions.
# Storing selected columns + raw_data JSONB 

# Version: v1.1.0

from sqlalchemy import ( 
    MetaData, Table, Column, BigInteger, Integer, SmallInteger, String, Numeric, 
    Boolean, Date,  DateTime, Text,  ForeignKey, UniqueConstraint, Enum, Index)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy import TIMESTAMP 

# MetaData - one per planned schema
archive_metadata = MetaData(schema="archive")
processed_metadata = MetaData(schema="processed")
ml_metadata = MetaData(schema="ml")
optimizer_metadata = MetaData(schema="optimizer")
public_metadata = MetaData(schema="public")


# TABLE DEFINITIONS
# PUBLIC SCHEMA
# 1. SEASONS
# List of seasons. One row per season.
# Upsert key: id
public_seasons = Table(
    "seasons", public_metadata,
    Column("id", SmallInteger, primary_key=True ,autoincrement=False),
    Column("name", String(100)), # E.g. "2025/26"
    Column("start_year", SmallInteger), # E.g. 2025
    Column("end_year", SmallInteger), # E.g. 2026
    Column("is_current", Boolean, default=False),

    UniqueConstraint("id", name="uq_public_seasons_id"),
)

# 2. GAMEWEEKS 
# Source: bootstrap-static - events 
# 38 rows per season. Upserted every week. 
# Upsert key: id
public_gameweeks = Table(
    "gameweeks", public_metadata,
    Column("gameweek_id", SmallInteger, nullable=False),           # FPL GW id 1–38
    Column("season_id", SmallInteger, nullable=False),            # FK → public.seasons
    Column("finished", Boolean, default=False),
    Column("is_current", Boolean, default=False),
    Column("is_next", Boolean, default=False),
    Column("average_entry_score", SmallInteger),                   # Avg score across all FPL managers

    UniqueConstraint("gameweek_id", "season_id", name="uq_public_gameweeks_gw_season"),
)

# 3. TEAMS
public_teams = Table(
    "teams", public_metadata,
    Column("team_id", Integer, nullable=False,),                   # FPL team id
    Column("season_id", SmallInteger, nullable=False),            # FK → public.seasons
    Column("code", Integer),
    Column("name", String(100)),
    Column("short_name", String(10)),
    UniqueConstraint("team_id", "season_id", name="uq_public_teams_id_season"),
)
# 4. PLAYERS
public_players = Table(
    "players", public_metadata,
    # Indexing Info
    Column("opta_code", Integer),  # Unique code for the player (consistent across seasons)
    Column("player_id", Integer, nullable=False),            # FPL element id unique for that season
    Column("season_id", SmallInteger, nullable=False),            # FK → public.seasons
    # Player Info
    Column("web_name", String(100)),
    Column("first_name", String(100)),
    Column("second_name", String(100)),
    Column("team_id", Integer),
    Column("element_type", SmallInteger), # 1=GK 2=DEF 3=MID 4=FWD
    Column("status", String(1)), # a / d / i / s / u
    Column("now_cost", SmallInteger), # 60 = £6.0m
   

    UniqueConstraint("opta_code", "season_id", name="uq_public_players_opta_season"),
)
# Indexes for faster lookups
Index("ix_players_opta_code", public_players.c.opta_code)
Index("ix_players_season_id", public_players.c.season_id)


# ARHCIVE SCHEMA
# 1. GAMEWEEKS 
# Source: bootstrap-static - events 
# 38 rows per season. Upserted every week. 
# Upsert key: id
gameweeks = Table(
    "gameweeks", archive_metadata,
    Column("id", BigInteger, primary_key=True ,autoincrement=True),
    Column("gameweek_id", SmallInteger, nullable=False),           # FPL GW id 1–38
    Column("season_id", SmallInteger, nullable=False),            # FK → public.seasons
    Column("finished", Boolean, default=False),
    Column("is_current", Boolean, default=False),
    Column("is_next", Boolean, default=False),
    Column("average_entry_score", SmallInteger),                   # Avg score across all FPL managers
    # Raw Data
    Column("raw_data", JSONB, nullable=False),

    UniqueConstraint("gameweek_id", "season_id", name="uq_gameweeks_gw_season"),
)

# 2. TEAMS
# Source: bootstrap-static - teams
# 20 rows per season. Once per season.
# Upsert key: (id, season_id)
teams = Table(
    "teams", archive_metadata,
    Column("id", BigInteger, primary_key=True ,autoincrement=True), #Auto id of every row
    Column("team_id", Integer, nullable=False,),                   # FPL team id
    Column("season_id", SmallInteger, nullable=False),            # FK → public.seasons
    Column("code", Integer),
    Column("name", String(100)),
    Column("short_name", String(10)),
    Column("strength", SmallInteger),
    # Raw Data
    Column("raw_data", JSONB, nullable=False),
    UniqueConstraint("team_id", "season_id", name="uq_teams_id_season"),
)

# 3. PLAYERS SNAPSHOT
# Source: bootstrap-static - elements
# Full season snapshot at the time of fetch. 
# Inserted every week for all players.
# Upsert key: (id, season_id, gw_id)

player_snapshots = Table(
    "player_snapshots", archive_metadata,
    # Indexing Info
    Column("id", BigInteger, primary_key=True ,autoincrement=True), #Auto id of every row
    Column("opta_code", Integer),  # Unique code for the player (consistent across seasons)
    Column("player_id", Integer, nullable=False),            # FPL element id unique for that season
    Column("fetched_gameweek_id", SmallInteger, nullable=False),     
    Column("season_id", SmallInteger, nullable=False),            # FK → public.seasons
    Column("fetched_at", TIMESTAMP(timezone=True), server_default=func.now()),
    # Player Info
    Column("web_name", String(100)),
    Column("first_name", String(100)),
    Column("second_name", String(100)),
    Column("team_id", Integer),
    Column("element_type", SmallInteger), # 1=GK 2=DEF 3=MID 4=FWD
    Column("status", String(1)), # a / d / i / s / u
    Column("now_cost", SmallInteger), # 60 = £6.0m
    # Injury, gw info - out of scope for MVP, can be used for optimizer in the future
    Column("chance_of_playing_next_round", SmallInteger),
    Column("news", Text),
    Column("scout_risks", JSONB),
    # Season Stats - cumulative up to the fetch point in time
    Column("total_points", SmallInteger),
    Column("minutes", Integer),
    Column("goals_scored", SmallInteger),
    Column("assists", SmallInteger),
    Column("clean_sheets", SmallInteger),
    Column("goals_conceded", SmallInteger),
    Column("saves", SmallInteger),
    Column("bonus", SmallInteger),
    Column("yellow_cards", SmallInteger),
    Column("red_cards", SmallInteger),
    Column("starts", SmallInteger),
    # ICT index - FPL metric
    Column("influence", Numeric(6, 1)),
    Column("creativity", Numeric(6, 1)),
    Column("threat", Numeric(6, 1)),
    Column("ict_index", Numeric(6, 1)),
    # Expected Metrics - FPL metric - Needed? 
    Column("expected_goals", Numeric(6, 2)),
    Column("expected_assists", Numeric(6, 2)),
    Column("expected_goals_conceded", Numeric(6, 2)),
    Column("expected_goal_involvements", Numeric(6, 2)),
    # Form Metrics - FPL metric
    Column("form", Numeric(4, 1)),
    Column("points_per_game", Numeric(4, 1)),
    Column("ep_next", Numeric(5, 1)),
    # Defensive Stats - Out of scope for MVP, can be used for optimizer in the future
    Column("clearances_blocks_interceptions", SmallInteger),
    Column("recoveries", SmallInteger),
    Column("tackles", SmallInteger),
    # Raw Data
    Column("raw_data", JSONB, nullable=False),

    UniqueConstraint("opta_code", "fetched_gameweek_id", "season_id", name="uq_snapshots_player_fgw_season"),
)
# Indexes for faster lookups
Index("ix_snapshots_fetched_gameweek_id", player_snapshots.c.fetched_gameweek_id)
Index("ix_snapshots_opta_code", player_snapshots.c.opta_code)
Index("ix_snapshots_season_id", player_snapshots.c.season_id)

# 4. PLAYER FUTURE FIXTURES
# Source: element-summary/{id}/ - fixtures
# Upcoming fixtures. 
# should we not insert instead? overwriting?
# Upserted weekly — records what the fixture list looked like at each fetch.
# Upsert key: (player_id, fetched_gameweek_id, fixture_id)
player_future_fixtures = Table(
    "player_future_fixtures", archive_metadata,
    # Indexing Info
    Column("id", BigInteger, primary_key=True, autoincrement=True), #Auto id of every row
    Column("opta_code", Integer),  # Unique code for the player (consistent across seasons)
    Column("player_id", Integer, nullable=False), 
    # Fixture Info
    Column("fetched_gameweek_id", SmallInteger, nullable=False),
    Column("fixture_id", Integer, nullable=False),
    Column("fixture_gameweek_id", SmallInteger), 
    Column("is_home", Boolean),
    Column("difficulty", SmallInteger),
    Column("team_h", Integer),
    Column("team_a", Integer),
    # Raw Data
    Column("raw_data", JSONB, nullable=False),

    UniqueConstraint("opta_code", "fetched_gameweek_id", "fixture_id", name="uq_future_fixtures_player_fgw_fixture"),
)

Index("ix_future_fixtures_player_fgw", player_future_fixtures.c.opta_code, player_future_fixtures.c.fetched_gameweek_id)

# 5. PLAYER GAMEWEEK HISTORY
# Source: element-summary/{id}/ - history
# One row per player per played fixture.
# Upsert key: (opta_code, fixture_id)
player_gw_history = Table(
    "player_gw_history", archive_metadata,
    # Indexing Info
    Column("id", BigInteger, primary_key=True, autoincrement=True), #Auto id of every row
    Column("opta_code", Integer),  # Unique code for the player (consistent across seasons)
    Column("player_id", Integer, nullable=False),
    # Fixture Info
    Column("fixture_id", Integer, nullable=False),
    Column("gameweek_id", SmallInteger),
    Column("season_id", SmallInteger),
    Column("opponent_team_id", Integer),
    Column("was_home", Boolean),
    # Fixture Result
    Column("team_h_score", SmallInteger),
    Column("team_a_score", SmallInteger),
    Column("total_points", SmallInteger),
    Column("minutes", SmallInteger),
    # Stats
    Column("goals_scored", SmallInteger),
    Column("assists", SmallInteger),
    Column("clean_sheets", SmallInteger),
    Column("goals_conceded", SmallInteger),
    Column("own_goals", SmallInteger),
    Column("penalties_saved", SmallInteger),
    Column("penalties_missed", SmallInteger),
    Column("yellow_cards", SmallInteger),
    Column("red_cards", SmallInteger),
    Column("saves", SmallInteger),
    Column("bonus", SmallInteger),
    Column("bps", SmallInteger),
    Column("starts", SmallInteger),
    # ICT index - FPL metric
    Column("influence", Numeric(6, 1)),
    Column("creativity", Numeric(6, 1)),
    Column("threat", Numeric(6, 1)),
    Column("ict_index", Numeric(6, 1)),
    # Expected Metrics - FPL metric - Needed? 
    Column("expected_goals", Numeric(6, 2)),
    Column("expected_assists", Numeric(6, 2)),
    Column("expected_goal_involvements", Numeric(6, 2)),
    Column("expected_goals_conceded", Numeric(6, 2)),
    # Defensive Stats - Out of scope for MVP, can be used for optimizer in the future
    Column("clearances_blocks_interceptions", SmallInteger),
    Column("recoveries", SmallInteger),
    Column("tackles", SmallInteger),
    # Cost
    Column("value", SmallInteger),
    # Raw Data
    Column("raw_data", JSONB, nullable=False),

    UniqueConstraint("opta_code", "fixture_id", "season_id", name="uq_history_player_fixture_season"),
)

Index("ix_history_fixture_id", player_gw_history.c.fixture_id)
Index("ix_history_opta_code", player_gw_history.c.opta_code)
Index("ix_history_season_id", player_gw_history.c.season_id)