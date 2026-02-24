# FPL Gaffer - Project Context

## Overview
Production-grade Fantasy Premier League optimization platform. Uses ML (XGBoost) to predict player points and linear programming (PuLP) to construct optimal squads. Portfolio/CV project demonstrating full-stack data engineering + ML + web development.

## Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Backend API | FastAPI | latest |
| ORM | SQLAlchemy | 2.0+ |
| Database | PostgreSQL | 15+ |
| Cache | Redis | 7+ |
| Orchestration | Apache Airflow | 2.7+ |
| Transformations | dbt-postgres | 1.11+ |
| ML | XGBoost, scikit-learn | latest |
| Optimization | PuLP (CBC solver) | latest |
| Frontend | Next.js (App Router) | 14 |
| Styling | Tailwind CSS | latest |
| Language (BE) | Python | 3.13 |
| Language (FE) | TypeScript | 5+ |
| Containers | Docker + Docker Compose | latest |
| CI | GitHub Actions | - |

## Python Environment
- `.venv` at project root, Python 3.13 (Homebrew)
- Activate: `source .venv/bin/activate`
- dbt binary: `.venv/bin/dbt`

## Project Structure
```
001 - fpl-gaffer/
├── CLAUDE.md                  # This file
├── .venv/                     # Python 3.13 virtual environment
├── _notes/                    # PRD, task tracking, design notes
│   ├── FPL_Optimizer_PRD.md
│   ├── TASKS.md
│   └── simple_mvp_prd.md
├── 01-TBD/                    # Data pipeline (ingestion → archive schema)
│   ├── main.py                # Pipeline entry point
│   ├── db/
│   │   ├── engine.py          # SQLAlchemy engine setup
│   │   ├── init_db.py         # Creates schemas + archive tables
│   │   └── schema.py          # SQLAlchemy table definitions (archive schema)
│   └── pipeline/
│       ├── fetch.py           # FPL API extraction (rate-limited, retry logic)
│       ├── clean.py           # Data cleaning before insertion
│       └── load.py            # Upsert into archive schema
├── 02-dbt/                    # dbt transformation project
│   ├── dbt_project.yml        # Project name: fpl_gaffer
│   ├── models/
│   │   └── processed/         # Intermediate + feature models
│   ├── macros/
│   ├── tests/
│   └── analyses/
├── 05-optimizer/              # PuLP optimization engine (standalone, pre-integration)
│   ├── optimizer.py
│   ├── data_loader.py
│   └── tests/
└── _notes/                    # Design docs and task tracking
```

## Data Architecture

### Modified Medallion: Archive → Processed → ML

Data is **cleaned before insertion** into archive (not truly raw). The pipeline cleans on ingest; archive is the single source of truth for structured historical data.

```
01-TBD pipeline (Python)
    ↓  fetch → clean → upsert
archive.*                        SQLAlchemy owns DDL
    ↓  dbt run
processed.player_gw_base         Joined fact table (intermediate)
processed.player_gw_features     ML feature matrix (rolling windows, lags)
    ↓  Python training script
ml.training_runs                 Walk-forward fold tracking
ml.model_artefacts               .pkl paths + production flag
ml.predictions                   Per-player per-GW predictions + actuals
```

### Schema Ownership

| Schema | Owner | Contains |
|--------|-------|----------|
| `archive` | SQLAlchemy (01-TBD) | Raw cleaned FPL data — gameweeks, teams, player snapshots, GW history, future fixtures |
| `processed` | dbt (02-dbt) | `player_gw_base` (joined fact), `player_gw_features` (ML features) |
| `ml` | SQLAlchemy + Python | Model registry, training run logs, predictions |
| `optimizer` | SQLAlchemy / FastAPI | Optimization results |
| `public` | SQLAlchemy | Seasons reference table |

### Archive Schema Tables (complete)
- `archive.gameweeks` — 38 rows per season, upserted weekly
- `archive.teams` — 20 rows per season
- `archive.player_snapshots` — full snapshot per player per GW fetch
- `archive.player_future_fixtures` — upcoming fixtures per player per fetch
- `archive.player_gw_history` — one row per player per played fixture

### Processed Schema Design
- `processed.player_gw_base` — one row per `(opta_code, gameweek_id, season_id)`. Joins history + team + gameweek context. Owned by dbt.
- `processed.player_gw_features` — wide ML feature matrix built over `player_gw_base` using backward-only window functions (no data leakage). Keyed on `(opta_code, gameweek_id, season_id)`.

### ML Schema Design
- `ml.training_runs` — tracks each walk-forward fold: `train_start_gw`, `train_end_gw`, `validation_gw`, `horizon` (1/2/3), metrics
- `ml.model_artefacts` — `.pkl` file paths, linked to training run, `is_production` flag
- `ml.predictions` — `(opta_code, gameweek_id, training_run_id, horizon)`, stores `predicted_points` and `actual_points` (filled post-GW)

### Walk-Forward Training
3 separate XGBoost models are trained — one per horizon (GW+1, GW+2, GW+3). Each slides forward independently. Critical rules:
- Features in `processed.player_gw_features` must be **point-in-time correct** — only data available before GW N may appear in the GW N feature row
- Window functions must use `ROWS BETWEEN N PRECEDING AND 1 PRECEDING` (lag-based, never including current row for target-correlated stats)
- Each fold per horizon is a separate `ml.training_runs` record with a `horizon` column

## Database
- **Name**: `fpl_gaffer`
- **Host**: localhost:5432
- **User**: aamirbay

## dbt Setup
- **Project**: `02-dbt/`, name `fpl_gaffer`, profile `fpl_gaffer`
- **Profile file**: `~/.dbt/profiles.yml`
- **Run dbt**: `cd 02-dbt && ../.venv/bin/dbt run`
- **Test connection**: `../.venv/bin/dbt debug`
- dbt owns DDL for `processed.*` only — do not create these tables manually or via SQLAlchemy

## Key Commands
```bash
# Activate environment
source .venv/bin/activate

# Run full pipeline (fetch → clean → load into archive)
python 01-TBD/main.py

# Run dbt models
cd 02-dbt && ../.venv/bin/dbt run

# Run dbt tests
cd 02-dbt && ../.venv/bin/dbt test

# Debug dbt connection
cd 02-dbt && ../.venv/bin/dbt debug

# Compile dbt SQL without running (inspect target/ output)
cd 02-dbt && ../.venv/bin/dbt compile
```

## Architecture Rules

### Clean Architecture (Backend — future FastAPI)
- **Controllers** handle HTTP only. No business logic.
- **Services** contain all business logic. No direct DB access.
- **Repositories** handle all database operations via SQLAlchemy.
- Dependencies flow inward: Controllers → Services → Repositories → Database

### Frontend Data Access
- Next.js API routes query PostgreSQL directly for simple reads
- FastAPI handles ML predictions and optimization (heavy compute)
- Never call FastAPI for simple CRUD operations

## Coding Conventions

### Python
- Formatter: black (line length 88)
- Linter: ruff
- Type hints on all function signatures
- Docstrings on public functions (Google style)

### TypeScript (Frontend)
- Formatter: prettier
- Linter: eslint
- Strict TypeScript mode enabled

### General
- No hardcoded credentials — use environment variables
- Git commit messages: imperative mood ("Add player repository")
- FPL API rate limit: ~50 req/s — exponential backoff implemented in `fetch.py`
- Historical data source: vaastav/Fantasy-Premier-League GitHub repo (CSV dumps)
