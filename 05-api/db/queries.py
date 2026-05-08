# Load the predictions from ml.predictions and training data from ml.training_runs
# Returns a DataFrame
# Version: 1.1.0

import pandas as pd
from db.engine import engine

def load_gameweeks():
    query = """
        select season_id, gameweek_id, deadline_time as deadline, is_next
        from archive.gameweeks
        where is_next = true
          and season_id = (select id from public.seasons where is_current = true);
    """
    df = pd.read_sql(query, engine)
    return df

def load_players():
    query = """
        with
        current_season as (
            select id as season_id from public.seasons where is_current = true
        ),
        global_max_gw as (
            select max(gameweek_id) as max_gw
            from processed.player_gw_features
            where season_id = (select season_id from current_season)
        ),
        -- aggregate raw fixtures into a JSON array per (player, gw).
        -- DGW players get two entries; BGW players get no row (null join = empty fixtures).
        player_fixtures_json as (
            select
                f.opta_code,
                f.fixture_gameweek_id,
                json_agg(json_build_object(
                    'is_home',     f.is_home,
                    'difficulty',  f.difficulty,
                    'opponent',    t.short_name
                ) order by f.difficulty desc) as fixtures
            from archive.player_future_fixtures f
            join public.teams t
                on  t.team_id    = case when f.is_home then f.team_a else f.team_h end
                and t.season_id  = (select season_id from current_season)
            where f.fixture_gameweek_id in (
                (select max_gw + 1 from global_max_gw),
                (select max_gw + 2 from global_max_gw),
                (select max_gw + 3 from global_max_gw)
            )
            group by f.opta_code, f.fixture_gameweek_id
        ),
        latest_features as (
            select distinct on (f.opta_code) f.*
            from processed.player_gw_features f
            where f.season_id = (select season_id from current_season)
            order by f.opta_code, f.gameweek_id desc
        ),
        pivoted_predictions as (
            select
                opta_code,
                max(predicted_points) filter (where horizon = 1) as predicted_pts_h1,
                max(predicted_points) filter (where horizon = 2) as predicted_pts_h2,
                max(predicted_points) filter (where horizon = 3) as predicted_pts_h3
            from ml.predictions
            where season_id = (select season_id from current_season)
              and features_gameweek_id = (
                  select max(features_gameweek_id) from ml.predictions
                  where season_id = (select season_id from current_season)
              )
            group by opta_code
        )
        select
            f.opta_code,
            p.web_name                              as name,
            t.name                                  as club,
            t.short_name                            as club_short,
            case f.element_type
                when 1 then 'GKP'
                when 2 then 'DEF'
                when 3 then 'MID'
                when 4 then 'FWD'
            end                                     as position,
            round(f.now_cost::numeric / 10, 1)      as price,
            f.status,
            round(pred.predicted_pts_h1::numeric, 2) as predicted_pts_h1,
            round(pred.predicted_pts_h2::numeric, 2) as predicted_pts_h2,
            round(pred.predicted_pts_h3::numeric, 2) as predicted_pts_h3,
            fh1.fixtures                             as h1_fixtures,
            fh2.fixtures                             as h2_fixtures,
            fh3.fixtures                             as h3_fixtures
        from latest_features f
        join public.players p
            on  p.opta_code  = f.opta_code and p.season_id = (select season_id from current_season)
        join public.teams t
            on  t.team_id    = f.team_id   and t.season_id = (select season_id from current_season)
        left join pivoted_predictions pred
            on  pred.opta_code = f.opta_code
        left join player_fixtures_json fh1
            on  fh1.opta_code = f.opta_code and fh1.fixture_gameweek_id = (select max_gw + 1 from global_max_gw)
        left join player_fixtures_json fh2
            on  fh2.opta_code = f.opta_code and fh2.fixture_gameweek_id = (select max_gw + 2 from global_max_gw)
        left join player_fixtures_json fh3
            on  fh3.opta_code = f.opta_code and fh3.fixture_gameweek_id = (select max_gw + 3 from global_max_gw)
        order by f.element_type, pred.predicted_pts_h1 desc nulls last
    """
    df = pd.read_sql(query, engine)
    return df
