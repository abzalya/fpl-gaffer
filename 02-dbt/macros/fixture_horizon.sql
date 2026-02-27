-- fixture_horizon
{% macro fixture_horizon(horizon, fixture_alias) %}
    {{ fixture_alias }}.difficulty fixture_difficulty_h{{ horizon }},
    coalesce(
        {{ fixture_alias }}.is_home,
        lead(pgb.was_home, {{ horizon }}) over (partition by pgb.opta_code, pgb.season_id order by pgb.gameweek_id)
    ) fixture_is_home_h{{ horizon }},
    coalesce(
        case when {{ fixture_alias }}.is_home then {{ fixture_alias }}.team_a else {{ fixture_alias }}.team_h end,
        lead(pgb.opponent_team_id, {{ horizon }}) over (partition by pgb.opta_code, pgb.season_id order by pgb.gameweek_id)
    ) opponent_team_id_h{{ horizon }},
    lead(pgb.opponent_strength, {{ horizon }}) over (partition by pgb.opta_code, pgb.season_id order by pgb.gameweek_id) opponent_strength_h{{ horizon }}
{% endmacro %}
