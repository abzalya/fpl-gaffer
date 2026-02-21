# SQLAlchemy schema and table definitions.
# Storing selected columns + raw_data JSONB 

# Version: v1.0.0

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
# ARHCIVE SCHEMA
# 1. GAMEWEEKS 
# Source: bootstrap-static - events 
# 38 rows per season. Upserted every week. 
# Upsert key: id
gameweeks = Table(
    "gameweeks", archive_metadata,
    Column("id", SmallInteger, primary_key=True),           # FPL GW id 1–38
    Column("season_id", Integer, nullable=False),            # FK → public.seasons
    Column("is_current", Boolean, default=False),
    Column("is_next", Boolean, default=False),
    # Raw Data
    Column("raw_data", JSONB, nullable=False),
)

# 2. TEAMS
# Source: bootstrap-static - teams
# 20 rows per season. Once per season.
# Upsert key: (id, season_id)
teams = Table(
    "teams", archive_metadata,
    Column("id", Integer, nullable=False),                   # FPL team id
    Column("season_id", Integer, nullable=False),            # FK → public.seasons
    Column("code", Integer),
    Column("name", String(100)),
    Column("short_name", String(10)),
    Column("strength", SmallInteger),
    # Raw Data
    Column("raw_data", JSONB, nullable=False),
    UniqueConstraint("id", "season_id", name="uq_teams_id_season"),
)

# 3. PLAYERS SNAPSHOT
# Source: bootstrap-static - elements
# Full season snapshot at the time of fetch. 
# Inserted every week for all players.
# Upsert key: (id, season_id, gw_id)

player_snapshots = Table(
    "player_snapshots", archive_metadata,
    # Indexing Info
    Column("id", BigInteger, primary_key=True, autoincrement=True), #Auto id of every row
    Column("opto_code", Integer, nullable=False),  # Unique code for the player (consistent across seasons)
    Column("player_id", Integer, nullable=False),            # FPL element id unique for that season
    Column("gameweek_id", SmallInteger, nullable=False),     # FK → archive.gameweeks
    Column("season_id", Integer, nullable=False),            # FK → public.seasons
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

    UniqueConstraint("opto_code", "gameweek_id", name="uq_snapshots_player_gw"),
)
# Indexes for faster lookups
Index("ix_snapshots_gameweek_id", player_snapshots.c.gameweek_id)
Index("ix_snapshots_player_id", player_snapshots.c.player_id)

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
    Column("opto_code", Integer, nullable=False),  # Unique code for the player (consistent across seasons)
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

    UniqueConstraint(
        "opto_code", "fetched_gameweek_id", "fixture_id",
        name="uq_future_fixtures_player_gw_fixture"
    ),
)

Index("ix_future_fixtures_player_gw", player_future_fixtures.c.opto_code,player_future_fixtures.c.fetched_gameweek_id)

# 5. PLAYER GAMEWEEK HISTORY
# Source: element-summary/{id}/ - history
# One row per player per played fixture.
# Upsert key: (opto_code, fixture_id)
player_gw_history = Table(
    "player_gw_history", archive_metadata,
    # Indexing Info
    Column("id", BigInteger, primary_key=True, autoincrement=True), #Auto id of every row
    Column("opto_code", Integer, nullable=False),  # Unique code for the player (consistent across seasons)
    Column("player_id", Integer, nullable=False),
    # Fixture Info
    Column("fixture_id", Integer, nullable=False),
    Column("gameweek_id", SmallInteger),
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

    UniqueConstraint("opto_code", "fixture_id", name="uq_history_player_fixture"),
)

Index("ix_history_player_id", player_gw_history.c.player_id)
Index("ix_history_gameweek_id", player_gw_history.c.gameweek_id)