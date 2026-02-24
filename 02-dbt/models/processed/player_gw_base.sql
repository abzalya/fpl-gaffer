-- MODEL: player_gw_base
-- Layer: processed (intermediate)
-- Grain: one row per (opta_code, gameweek_id, season_id)
-- Purpose: joins archive tables into a single denormalised fact table.
-- Version: V1.0.0

-- Sources:
--   - archive.player_gw_history
--   - archive.teams
--   - archive.gameweeks
--   - archive.player_snapshots

{{
    config(
        materialized='incremental',
        schema='processed',
        unique_key=['opta_code', 'gameweek_id', 'season_id'],
        incremental_strategy='merge'
    )
}}

SELECT
    ph.opta_code,
    ph.player_id,
    ph.gameweek_id,
    ph.season_id,
    ph.total_points,
    ph.minutes,
    ph.was_home,
    ph.team_h_score,
    ph.team_a_score,
	--stats
    ph.goals_scored, ph.assists, ph.own_goals, ph.penalties_missed,
    ph.clean_sheets, ph.goals_conceded, ph.saves, ph.penalties_saved,
    ph.yellow_cards, ph.red_cards,
    ph.bonus, ph.bps,
    ph.influence, ph.creativity, ph.threat, ph.ict_index,
    ph.expected_goals, ph.expected_assists,
    ph.expected_goal_involvements, ph.expected_goals_conceded,
	--details
    ps.element_type,
    ps.team_id,
    ps.status,
    ph.value now_cost,
	--vs team details
    ph.opponent_team_id,
    t.strength opponent_strength,
    g.finished gw_finished
from archive.player_gw_history ph
left join (
    select distinct on (opta_code)
        opta_code, element_type, team_id, status
    from archive.player_snapshots
    order by opta_code, fetched_gameweek_id desc
) ps on ps.opta_code = ph.opta_code
left join archive.gameweeks g
    on g.gameweek_id = ph.gameweek_id and g.season_id  = ph.season_id
left join archive.teams t
    on t.team_id   = ph.opponent_team_id and t.season_id = ph.season_id

{% if is_incremental() %}
WHERE ph.gameweek_id > (
    SELECT MAX(gameweek_id) FROM {{ this }}
    WHERE season_id = ph.season_id
)
{% endif %}