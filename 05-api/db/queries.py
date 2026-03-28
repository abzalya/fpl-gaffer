# Load the predictions from ml.predictions and training data from ml.training_runs
# Returns a DataFrame
# Version: 1.0.0

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
        latest_features as (
            -- distinct on gets the latest row per player regardless of which GW it's from.
            -- is_stale flags players whose last features predate the global max GW (i.e. they
            -- had a blank gameweek). Their h1 fixture column points at the blank GW (null), so
            -- we shift: display h1 <- feature h2, display h2 <- feature h3, display h3 <- null.
            select distinct on (f.opta_code) f.*,
                f.gameweek_id < g.max_gw as is_stale
            from processed.player_gw_features f
            cross join global_max_gw g
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
            p.web_name                                                                    as name,
            t.name                                                                        as club,
            t.short_name                                                                  as club_short,
            case f.element_type
                when 1 then 'GKP'
                when 2 then 'DEF'
                when 3 then 'MID'
                when 4 then 'FWD'
            end                                                                           as position,
            round(f.now_cost::numeric / 10, 1)                                           as price,
            f.status,
            round(pred.predicted_pts_h1::numeric, 2)                                     as predicted_pts_h1,
            round(pred.predicted_pts_h2::numeric, 2)                                     as predicted_pts_h2,
            round(pred.predicted_pts_h3::numeric, 2)                                     as predicted_pts_h3,
            case when f.is_stale then f.fixture_is_home_h2    else f.fixture_is_home_h1    end as h1_is_home,
            case when f.is_stale then f.fixture_difficulty_h2 else f.fixture_difficulty_h1 end as h1_difficulty,
            case when f.is_stale then t_opp2.short_name        else t_opp1.short_name        end as h1_opponent,
            case when f.is_stale then f.fixture_is_home_h3    else f.fixture_is_home_h2    end as h2_is_home,
            case when f.is_stale then f.fixture_difficulty_h3 else f.fixture_difficulty_h2 end as h2_difficulty,
            case when f.is_stale then t_opp3.short_name        else t_opp2.short_name        end as h2_opponent,
            case when f.is_stale then null                     else f.fixture_is_home_h3    end as h3_is_home,
            case when f.is_stale then null                     else f.fixture_difficulty_h3 end as h3_difficulty,
            case when f.is_stale then null                     else t_opp3.short_name        end as h3_opponent
        from latest_features f
        join public.players p
            on p.opta_code = f.opta_code and p.season_id = (select season_id from current_season)
        join public.teams t
            on t.team_id = f.team_id and t.season_id = (select season_id from current_season)
        left join pivoted_predictions pred
            on pred.opta_code = f.opta_code
        left join public.teams t_opp1
            on t_opp1.team_id = f.opponent_team_id_h1 and t_opp1.season_id = (select season_id from current_season)
        left join public.teams t_opp2
            on t_opp2.team_id = f.opponent_team_id_h2 and t_opp2.season_id = (select season_id from current_season)
        left join public.teams t_opp3
            on t_opp3.team_id = f.opponent_team_id_h3 and t_opp3.season_id = (select season_id from current_season)
        order by f.element_type, pred.predicted_pts_h1 desc nulls last
    """
    df = pd.read_sql(query, engine)
    return df
