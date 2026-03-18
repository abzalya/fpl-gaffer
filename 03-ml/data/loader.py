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
    query = """
        SELECT *
        FROM processed.player_gw_features
        WHERE season_id = (SELECT MAX(season_id) FROM processed.player_gw_features)
          AND gameweek_id = (
              SELECT MAX(gameweek_id)
              FROM processed.player_gw_features
              WHERE season_id = (SELECT MAX(season_id) FROM processed.player_gw_features)
          )
    """

    df = pd.read_sql(query, engine)
    return df
