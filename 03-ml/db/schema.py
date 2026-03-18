# ML SCHEMA definitions moved from 01-db/schema.py for sqlalchemy in 03-ml block.

from sqlalchemy import ( 
    MetaData, Table, Column, BigInteger, Integer, SmallInteger, String, Numeric, 
    Boolean, UniqueConstraint, Index)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy import TIMESTAMP 

ml_metadata = MetaData(schema="ml")

# ML SCHEMA
# Tables: ml.training_runs, ml.model_artefacts, ml.predictions
# 1. Training Runs
# One row per walk-forward fold per training execution.
# run_id groups all folds that belong to the same run
ml_training_runs = Table(
    "training_runs", ml_metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("run_id", UUID(as_uuid=True), nullable=False),           # groups folds from the same run
    Column("run_at", TIMESTAMP(timezone=True), nullable=False),
    Column("triggered_by", String(20), nullable=False),             # pipeline | manual | experiment
    Column("algorithm", String(50), nullable=False),
    Column("horizon", SmallInteger, nullable=False),                
    Column("config_snapshot", JSONB, nullable=False),               # full config.yaml at run time
    Column("fold_index", Integer, nullable=False),
    Column("validation_season_id", SmallInteger, nullable=False),
    Column("validation_gameweek_id", SmallInteger, nullable=False),
    Column("n_train_rows", Integer),
    Column("n_val_rows", Integer),
    Column("mae", Numeric(8, 4)),
    Column("rmse", Numeric(8, 4)),
    Column("r2", Numeric(8, 4)),
    UniqueConstraint("run_id", "fold_index", "horizon", name="uq_training_runs_run_fold_horizon"),
)

Index("ix_training_runs_run_id", ml_training_runs.c.run_id)
Index("ix_training_runs_horizon", ml_training_runs.c.horizon)

# 2. Model Artefacts
# One row per saved (final) model file.
# is_production = True marks the model actively used for predictions.
# Only one row per horizon should have is_production = True at a time.
ml_model_artefacts = Table(
    "model_artefacts", ml_metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("run_id", UUID(as_uuid=True), nullable=False),           # FK → training_runs.run_id
    Column("run_at", TIMESTAMP(timezone=True), nullable=False),
    Column("triggered_by", String(20), nullable=False),
    Column("algorithm", String(50), nullable=False),
    Column("horizon", SmallInteger, nullable=False),
    Column("artefact_path", String(500), nullable=False),           # relative path to .pkl
    Column("feature_cols", JSONB, nullable=False),                  # list of features used
    Column("feature_importances", JSONB),                           # {feature_name: importance}
    Column("config_snapshot", JSONB, nullable=False),
    Column("n_folds", Integer),
    Column("avg_mae", Numeric(8, 4)),
    Column("avg_rmse", Numeric(8, 4)),
    Column("avg_r2", Numeric(8, 4)),
    Column("is_production", Boolean, nullable=False, default=False),
    Column("promoted_at", TIMESTAMP(timezone=True)),                # when is_production was set True
)

Index("ix_model_artefacts_horizon", ml_model_artefacts.c.horizon)
Index("ix_model_artefacts_is_production", ml_model_artefacts.c.is_production)
Index("ix_model_artefacts_run_id", ml_model_artefacts.c.run_id)

# 3. Predictions
# One row per (player, predicted GW, horizon).
# Upsert key: (opta_code, season_id, predicted_gameweek_id, horizon).
# Overwritten if predict.py is re-run for the same GW — run_id tracks which
# model version produced the current value.
# actual_points is NULL until that GW is played, then filled by a post-GW job.
ml_predictions = Table(
    "predictions", ml_metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("run_id", UUID(as_uuid=True), nullable=False),              # model that made this prediction
    Column("predicted_at", TIMESTAMP(timezone=True), nullable=False),
    Column("opta_code", Integer, nullable=False),
    Column("season_id", SmallInteger, nullable=False),
    Column("features_gameweek_id", SmallInteger, nullable=False),      # GW of the feature row used
    Column("predicted_gameweek_id", SmallInteger, nullable=False),     # GW being predicted (features_gw + horizon)
    Column("horizon", SmallInteger, nullable=False),
    Column("predicted_points", Numeric(8, 4), nullable=False),
    Column("actual_points", SmallInteger),                             # filled post-GW
    UniqueConstraint(
        "opta_code", "season_id", "predicted_gameweek_id", "horizon",
        name="uq_predictions_player_gw_horizon",
    ),
)

Index("ix_predictions_predicted_gameweek_id", ml_predictions.c.predicted_gameweek_id)
Index("ix_predictions_opta_code", ml_predictions.c.opta_code)
