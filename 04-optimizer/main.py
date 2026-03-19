# FPL Gaffer — optimizer Entry Point
# Version: 1.0.0

import yaml
from pathlib import Path

CONFIG_PATH = Path(__file__).parent / "config.yaml"

def load_config():
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)


config = load_config()