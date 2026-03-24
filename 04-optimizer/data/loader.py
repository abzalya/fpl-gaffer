# Load the predictions from ml.predictions and training data from ml.training_runs
# Returns a DataFrame
# Version: 1.0.0

import pandas as pd
from db.engine import engine

def load_predictions(current_gameweek_id: int | None = None):
    if current_gameweek_id is None:
        current_gameweek_id = pd.read_sql(
            "SELECT MAX(features_gameweek_id) FROM ml.predictions", engine
        ).iloc[0, 0]

    query = f"""
        select p.opta_code, p.predicted_points, p.predicted_gameweek_id, p.season_id, p.horizon,  ps.web_name, ps.first_name, ps.second_name, t.name as team,
            case
            when ps.element_type = 1 then 'GKP'
            when ps.element_type = 2 then 'DEF'
            when ps.element_type = 3 then 'MID'
            when ps.element_type = 4 then 'FWD'
            end as position,
            round(ps.now_cost / 10.0, 1) as price
        from ml.predictions p
        join archive.player_snapshots ps
            on p.opta_code = ps.opta_code and p.features_gameweek_id = ps.fetched_gameweek_id
        join public.teams t
            on t.team_id = ps.team_id
        where p.features_gameweek_id = {current_gameweek_id}
    """

    df = pd.read_sql(query, engine)
    return df
