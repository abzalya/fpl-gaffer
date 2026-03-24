# Load the featuresfrom processed.player_gw_features.
# Returns a DataFrame sorted by (season_id, gameweek_id) ready for walk-forward training.
# Version: 1.0.0

import pandas as pd
from db.engine import engine


def load_features(horizon: int): #all training rows where target is not null. 
    
    target_col = f"pts_target_h{horizon}" #target column name depends on horizon

    query = f"""
        SELECT *
        FROM processed.player_gw_features
        WHERE {target_col} IS NOT NULL
        ORDER BY season_id ASC, gameweek_id ASC
    """

    df = pd.read_sql(query, engine)
    return df


def load_latest_features(): #the row to predict on. Most recent gameweek with features. Used for inference.
    # OLD: global MAX(gameweek_id) — excluded blank-GW teams whose latest row is GW-1.
    # query = """
    #     SELECT *
    #     FROM processed.player_gw_features
    #     WHERE season_id = (SELECT MAX(season_id) FROM processed.player_gw_features)
    #       AND gameweek_id = (
    #           SELECT MAX(gameweek_id)
    #           FROM processed.player_gw_features
    #           WHERE season_id = (SELECT MAX(season_id) FROM processed.player_gw_features)
    #       )
    # """
    # NEW: per-player latest row so blank-GW teams are included with their last available features.
    # Also returns current_gw (global max) so predictions are tagged consistently.
    current_gw_query = """
        SELECT MAX(gameweek_id)
        FROM processed.player_gw_features
        WHERE season_id = (SELECT MAX(season_id) FROM processed.player_gw_features)
    """
    current_gw = int(pd.read_sql(current_gw_query, engine).iloc[0, 0])

    query = """
        SELECT DISTINCT ON (opta_code) *
        FROM processed.player_gw_features
        WHERE season_id = (SELECT MAX(season_id) FROM processed.player_gw_features)
        ORDER BY opta_code, gameweek_id DESC
    """

    df = pd.read_sql(query, engine)
    return df, current_gw
