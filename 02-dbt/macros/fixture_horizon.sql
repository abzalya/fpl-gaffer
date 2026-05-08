-- fixture_horizon
-- Version: V1.1.0
{% macro fixture_horizon(horizon, fixture_alias) %}
    coalesce(
        {{ fixture_alias }}.fixture_count,
        case
            when lead(pgb.total_points, {{ horizon }}) over (partition by pgb.opta_code, pgb.season_id order by pgb.gameweek_id) is not null
            then 1
            else 0
        end
    ) fixture_count_h{{ horizon }},
    {{ fixture_alias }}.difficulty fixture_difficulty_h{{ horizon }},
    coalesce(
        {{ fixture_alias }}.is_home,
        lead(pgb.was_home, {{ horizon }}) over (partition by pgb.opta_code, pgb.season_id order by pgb.gameweek_id)
    ) fixture_is_home_h{{ horizon }},
    coalesce(
        {{ fixture_alias }}.opponent_team_id,
        lead(pgb.opponent_team_id, {{ horizon }}) over (partition by pgb.opta_code, pgb.season_id order by pgb.gameweek_id)
    ) opponent_team_id_h{{ horizon }},
    coalesce(
        t{{ horizon }}.strength,
        lead(pgb.opponent_strength, {{ horizon }}) over (partition by pgb.opta_code, pgb.season_id order by pgb.gameweek_id)
    ) opponent_strength_h{{ horizon }}
{% endmacro %}
