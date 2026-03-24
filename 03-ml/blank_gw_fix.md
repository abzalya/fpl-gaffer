# Blank Gameweek Fix — 2026-03-24

## Problem
When teams have a blank gameweek (no fixture), their players have no feature row
for the global `MAX(gameweek_id)`. `load_latest_features()` used a global max GW
filter, so those players were invisible to the prediction pipeline entirely.

Affected teams: Arsenal, Man City, Wolves, Crystal Palace (GW30 while others at GW31).

This cascaded into the optimizer:
- 825 players had features, but only 664 got predictions
- 7 players in the test squad were missing from predictions
- Their prices were not counted in the budget calculation
- Budget came out as 58m instead of ~83m → optimizer reported infeasible

## Root Cause Chain
1. `load_latest_features()` — global `MAX(gameweek_id)` excluded blank-GW players
2. `save_predictions()` — used `row["gameweek_id"]` for tagging, so any blank-GW
   players that did get through would be tagged GW30 while others were GW31
3. Optimizer `load_predictions()` — filters on `MAX(features_gameweek_id)` = GW31,
   which would have dropped the GW30-tagged rows anyway

## Fix

### `03-ml/data/loader.py` — `load_latest_features()`
Use `DISTINCT ON (opta_code) ORDER BY gameweek_id DESC` to take each player's own
latest row instead of the global max GW. Also returns `current_gw` (global max)
so predictions are tagged consistently regardless of which GW a player's features came from.

### `03-ml/registry/logger.py` — `save_predictions()`
Added `current_gw: int` parameter. Both `features_gameweek_id` and
`predicted_gameweek_id` now derive from `current_gw` instead of `row["gameweek_id"]`.
This ensures all players — including blank-GW teams — are tagged with the same GW
and visible to the optimizer's `MAX(features_gameweek_id)` filter.

### `03-ml/predict.py` — `predict_horizon()` and `main()`
`current_gw` is unpacked from `load_latest_features()` and threaded through
`predict_horizon()` into `save_predictions()`.

## Files Changed
- `03-ml/data/loader.py`
- `03-ml/registry/logger.py`
- `03-ml/predict.py`
