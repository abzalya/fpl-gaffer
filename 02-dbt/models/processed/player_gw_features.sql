-- MODEL: player_gw_features
-- Layer: processed (ML feature matrix)
-- Grain: one row per (opta_code, gameweek_id, season_id)
-- Purpose: Computes all ML features from player_gw_base using backward-only window functions.
-- Version: V1.0.0

-- Sources:
-- {{ ref('player_gw_base') }}
-- archive.player_future_fixtures

-- Note: Double gameweeks may produce multiple rows per horizon from player_future_fixtures.
--       Handle in downstream training code or add aggregation logic here if needed.

{{
    config(
        materialized='incremental',
        schema='processed',
        unique_key=['opta_code', 'gameweek_id', 'season_id'],
        incremental_strategy='delete+insert'
    )
}}

select
    --identifiers
    pgb.opta_code,
    pgb.player_id,
    pgb.gameweek_id,
    pgb.season_id,
    --target columns (lead-based, for 3 separate horizon models)
    --Note: NULL for last N rows of each player's season — filter in training code.
    lead(total_points, 1) over (partition by opta_code, season_id order by gameweek_id) pts_target_h1,
    lead(total_points, 2) over (partition by opta_code, season_id order by gameweek_id) pts_target_h2,
    lead(total_points, 3) over (partition by opta_code, season_id order by gameweek_id) pts_target_h3,
    --upcoming fixture context (from player_future_fixtures)
    --fixture join covers GW27+ (live), lead covers GW1-GW26 (historical). Update when new season starts.
    --difficulty has no equivalent in player_gw_base — NULL pre-GW27, use opponent_strength_hN as proxy.
    --h1: GW+1
    {{ fixture_horizon(1, 'f1') }},
    --h2: GW+2
    {{ fixture_horizon(2, 'f2') }},
    --h3: GW+3
    {{ fixture_horizon(3, 'f3') }},
    --lag features (target column context)
    --gw-1
    lag(total_points,     1) over (partition by opta_code, season_id order by gameweek_id) pts_lag_1,
    lag(opponent_team_id, 1) over (partition by opta_code, season_id order by gameweek_id) opponent_team_id_lag_1,
    lag(opponent_strength,1) over (partition by opta_code, season_id order by gameweek_id) opponent_strength_lag_1,
    lag(was_home,         1) over (partition by opta_code, season_id order by gameweek_id) fixture_is_home_lag_1,
    --gw-2
    lag(total_points,     2) over (partition by opta_code, season_id order by gameweek_id) pts_lag_2,
    lag(opponent_team_id, 2) over (partition by opta_code, season_id order by gameweek_id) opponent_team_id_lag_2,
    lag(opponent_strength,2) over (partition by opta_code, season_id order by gameweek_id) opponent_strength_lag_2,
    lag(was_home,         2) over (partition by opta_code, season_id order by gameweek_id) fixture_is_home_lag_2,
    --current GW performance
    pgb.total_points,
    --points rolling / cumulative
    {{ cumulative_sum('total_points', 'opta_code, season_id', 'gameweek_id') }} pts_season_total,
    {{ rolling_avg('total_points',    'opta_code, season_id', 'gameweek_id', 3) }} pts_rolling_3,
    {{ rolling_avg('total_points',    'opta_code, season_id', 'gameweek_id', 5) }} pts_rolling_5,
    pgb.minutes,
    --minutes rolling / cumulative
    {{ cumulative_sum('minutes',    'opta_code, season_id', 'gameweek_id') }} minutes_season_total,
    {{ rolling_avg('minutes',       'opta_code, season_id', 'gameweek_id', 3) }} minutes_rolling_3,
    {{ rolling_avg('minutes',       'opta_code, season_id', 'gameweek_id', 5) }} minutes_rolling_5,
    pgb.was_home,
    pgb.team_h_score,
    pgb.team_a_score,
    pgb.opponent_team_id,
    pgb.opponent_strength,
    pgb.gw_finished,
    --starts rolling
    pgb.starts,
    {{ rolling_avg('starts', 'opta_code, season_id', 'gameweek_id', 3) }} starts_rolling_3,
    {{ rolling_avg('starts', 'opta_code, season_id', 'gameweek_id', 5) }} starts_rolling_5,
    --goals
    pgb.goals_scored,
    {{ cumulative_sum('goals_scored', 'opta_code, season_id', 'gameweek_id') }} goals_season_total,
    {{ rolling_avg('goals_scored',    'opta_code, season_id', 'gameweek_id', 3) }} goals_rolling_3,
    {{ rolling_avg('goals_scored',    'opta_code, season_id', 'gameweek_id', 5) }} goals_rolling_5,
    --assists
    pgb.assists,
    {{ cumulative_sum('assists', 'opta_code, season_id', 'gameweek_id') }} assists_season_total,
    {{ rolling_avg('assists',    'opta_code, season_id', 'gameweek_id', 3) }} assists_rolling_3,
    {{ rolling_avg('assists',    'opta_code, season_id', 'gameweek_id', 5) }} assists_rolling_5,
    --other
    pgb.own_goals,
    pgb.penalties_missed,
    pgb.penalties_saved,
    --clean sheets (important for GK/DEF)
    pgb.clean_sheets,
    {{ cumulative_sum('clean_sheets', 'opta_code, season_id', 'gameweek_id') }} clean_sheets_season_total,
    {{ rolling_avg('clean_sheets',    'opta_code, season_id', 'gameweek_id', 3) }} clean_sheets_rolling_3,
    {{ rolling_avg('clean_sheets',    'opta_code, season_id', 'gameweek_id', 5) }} clean_sheets_rolling_5,
    --goals conceded (GK/DEF)
    pgb.goals_conceded,
    {{ cumulative_sum('goals_conceded', 'opta_code, season_id', 'gameweek_id') }} goals_conceded_season_total,
    {{ rolling_avg('goals_conceded',    'opta_code, season_id', 'gameweek_id', 3) }} goals_conceded_rolling_3,
    {{ rolling_avg('goals_conceded',    'opta_code, season_id', 'gameweek_id', 5) }} goals_conceded_rolling_5,
    --saves (GK)
    pgb.saves,
    {{ cumulative_sum('saves', 'opta_code, season_id', 'gameweek_id') }} saves_season_total,
    {{ rolling_avg('saves',    'opta_code, season_id', 'gameweek_id', 3) }} saves_rolling_3,
    {{ rolling_avg('saves',    'opta_code, season_id', 'gameweek_id', 5) }} saves_rolling_5,
    --cards
    pgb.yellow_cards,
    {{ cumulative_sum('yellow_cards', 'opta_code, season_id', 'gameweek_id') }} yellow_cards_season_total,
    {{ rolling_avg('yellow_cards',    'opta_code, season_id', 'gameweek_id', 3) }} yellow_cards_rolling_3,
    pgb.red_cards,
    {{ cumulative_sum('red_cards', 'opta_code, season_id', 'gameweek_id') }} red_cards_season_total,
    {{ rolling_avg('red_cards',    'opta_code, season_id', 'gameweek_id', 3) }} red_cards_rolling_3,
    --bonus / bps
    pgb.bonus,
    {{ rolling_avg('bonus', 'opta_code, season_id', 'gameweek_id', 3) }} bonus_rolling_3,
    {{ rolling_avg('bonus', 'opta_code, season_id', 'gameweek_id', 5) }} bonus_rolling_5,
    pgb.bps,
    {{ rolling_avg('bps', 'opta_code, season_id', 'gameweek_id', 3) }} bps_rolling_3,
    {{ rolling_avg('bps', 'opta_code, season_id', 'gameweek_id', 5) }} bps_rolling_5,
    --ICT index
    pgb.influence,
    {{ rolling_avg('influence', 'opta_code, season_id', 'gameweek_id', 3) }} influence_rolling_3,
    {{ rolling_avg('influence', 'opta_code, season_id', 'gameweek_id', 5) }} influence_rolling_5,
    pgb.creativity,
    {{ rolling_avg('creativity', 'opta_code, season_id', 'gameweek_id', 3) }} creativity_rolling_3,
    {{ rolling_avg('creativity', 'opta_code, season_id', 'gameweek_id', 5) }} creativity_rolling_5,
    pgb.threat,
    {{ rolling_avg('threat', 'opta_code, season_id', 'gameweek_id', 3) }} threat_rolling_3,
    {{ rolling_avg('threat', 'opta_code, season_id', 'gameweek_id', 5) }} threat_rolling_5,
    pgb.ict_index,
    {{ rolling_avg('ict_index', 'opta_code, season_id', 'gameweek_id', 3) }} ict_index_rolling_3,
    {{ rolling_avg('ict_index', 'opta_code, season_id', 'gameweek_id', 5) }} ict_index_rolling_5,
    --xG stats
    pgb.xG,
    {{ rolling_avg('xG', 'opta_code, season_id', 'gameweek_id', 3) }} xG_rolling_3,
    {{ rolling_avg('xG', 'opta_code, season_id', 'gameweek_id', 5) }} xG_rolling_5,
    pgb.xA,
    {{ rolling_avg('xA', 'opta_code, season_id', 'gameweek_id', 3) }} xA_rolling_3,
    {{ rolling_avg('xA', 'opta_code, season_id', 'gameweek_id', 5) }} xA_rolling_5,
    pgb.xGI,
    {{ rolling_avg('xGI', 'opta_code, season_id', 'gameweek_id', 3) }} xGI_rolling_3,
    {{ rolling_avg('xGI', 'opta_code, season_id', 'gameweek_id', 5) }} xGI_rolling_5,
    pgb.xGC,
    {{ rolling_avg('xGC', 'opta_code, season_id', 'gameweek_id', 3) }} xGC_rolling_3,
    {{ rolling_avg('xGC', 'opta_code, season_id', 'gameweek_id', 5) }} xGC_rolling_5,
    --player metadata
    pgb.element_type,
    pgb.team_id,
    pgb.status,
    pgb.chance_of_playing_next_round,
    pgb.now_cost
from {{ ref('player_gw_base') }} pgb
--joins for future fixtures
left join archive.player_future_fixtures f1
    on  f1.opta_code = pgb.opta_code and f1.fetched_gameweek_id = pgb.gameweek_id and f1.fixture_gameweek_id = pgb.gameweek_id + 1
left join archive.player_future_fixtures f2
    on  f2.opta_code = pgb.opta_code and f2.fetched_gameweek_id = pgb.gameweek_id and f2.fixture_gameweek_id = pgb.gameweek_id + 2
left join archive.player_future_fixtures f3
    on  f3.opta_code = pgb.opta_code and f3.fetched_gameweek_id = pgb.gameweek_id and f3.fixture_gameweek_id = pgb.gameweek_id + 3

{% if is_incremental() %}
where pgb.gameweek_id > (
    select max(gameweek_id) - 5 from {{ this }}
    where season_id = pgb.season_id
)
{% endif %}
