-- fixture_horizon
{% macro fixture_horizon(horizon, fixture_alias) %}
    {{ fixture_alias }}.difficulty fixture_difficulty_h{{ horizon }},
    coalesce(
        {{ fixture_alias }}.is_home,
        lead(was_home, {{ horizon }}) over (partition by opta_code, season_id order by gameweek_id)
    ) fixture_is_home_h{{ horizon }},
    coalesce(
        case when {{ fixture_alias }}.is_home then {{ fixture_alias }}.team_a else {{ fixture_alias }}.team_h end,
        lead(opponent_team_id, {{ horizon }}) over (partition by opta_code, season_id order by gameweek_id)
    ) opponent_team_id_h{{ horizon }},
    lead(opponent_strength, {{ horizon }}) over (partition by opta_code, season_id order by gameweek_id) opponent_strength_h{{ horizon }}
{% endmacro %}
