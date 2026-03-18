# FPL Gaffer — ML Training Entry Point
# Version: 1.0.0
#
# Usage:
#   python main.py                              # train h1, triggered_by=manual
#   python main.py --horizon 2                  # train h2
#   python main.py --triggered-by experiment    # mark run as an experiment
#   python main.py --triggered-by pipeline      # used by Airflow
#
# The script:
#   1. Loads config.yaml
#   2. Loads features from processed.player_gw_features
#   3. Runs walk-forward validation
#   4. Saves the final model to artefacts/
#   5. Logs the run to ml.training_runs and ml.model_artefacts

import argparse
import sys
import uuid
import yaml
from datetime import datetime, timezone
from pathlib import Path

# Make imports work when running from the 03-ml directory
sys.path.insert(0, str(Path(__file__).parent))

from data.loader import load_features
from registry.logger import save_run
from training.registry import ALGORITHM_REGISTRY

VALID_TRIGGERED_BY = {"manual", "pipeline", "experiment"}
CONFIG_PATH = Path(__file__).parent / "config.yaml"
ARTEFACTS_DIR = Path(__file__).parent / "artefacts"

def load_config():
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)


def get_algorithm_module(algorithm: str):
    if algorithm not in ALGORITHM_REGISTRY:
        raise ValueError(
            f"Unknown algorithm '{algorithm}'. "
            f"Available: {list(ALGORITHM_REGISTRY.keys())}"
        )
    import importlib
    return importlib.import_module(ALGORITHM_REGISTRY[algorithm])


def main():
    parser = argparse.ArgumentParser(description="FPL Gaffer — Train ML model")
    parser.add_argument(
        "--horizon",
        type=int,
        default=None,
        help="Override the horizon to train (1, 2, or 3). "
             "Defaults to all horizons listed in config.yaml.",
    )
    parser.add_argument(
        "--triggered-by",
        dest="triggered_by",
        default="manual",
        choices=list(VALID_TRIGGERED_BY),
        help="Who/what triggered this run. Default: manual.",
    )
    args = parser.parse_args()

    config = load_config()
    algorithm = config["model"]["algorithm"]
    mod = get_algorithm_module(algorithm)
    walk_forward = mod.walk_forward
    get_importances = mod.feature_importances

    # Determine which horizons to train
    horizons_to_train = (
        [args.horizon] if args.horizon is not None
        else config["training"]["horizons"]
    )

    run_id = uuid.uuid4()
    run_at = datetime.now(timezone.utc)

    for horizon in horizons_to_train:

        df = load_features(horizon)

        fold_metrics, final_model, feature_cols, avg_metrics = walk_forward(
            df=df,
            config=config,
            horizon=horizon,
        )

        artefact_path = save_run(
            run_id=run_id,
            run_at=run_at,
            triggered_by=args.triggered_by,
            algorithm=algorithm,
            horizon=horizon,
            config_snapshot=config,
            fold_metrics=fold_metrics,
            final_model=final_model,
            feature_cols=feature_cols,
            feature_importances=get_importances(final_model, feature_cols),
            avg_metrics=avg_metrics,
            artefacts_dir=ARTEFACTS_DIR,
        )

if __name__ == "__main__":
    main()
