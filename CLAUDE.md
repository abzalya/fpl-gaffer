# FPL Optimizer - Project Context

## Overview
Production-grade Fantasy Premier League optimization platform. Uses ML (XGBoost) to predict player points and linear programming (PuLP) to construct optimal squads. Portfolio/CV project demonstrating full-stack data engineering + ML + web development.

## Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Backend API | FastAPI | latest |
| ORM | SQLAlchemy + Alembic | 2.0+ |
| Database | PostgreSQL | 15+ |
| Cache | Redis | 7+ |
| Orchestration | Apache Airflow | 2.7+ |
| Transformations | dbt | latest |
| ML | XGBoost, scikit-learn | latest |
| Optimization | PuLP (CBC solver) | latest |
| Frontend | Next.js (App Router) | 14 |
| Styling | Tailwind CSS | latest |
| Language (BE) | Python | 3.11+ |
| Language (FE) | TypeScript | 5+ |
| Containers | Docker + Docker Compose | latest |
| CI | GitHub Actions | - |
| Python deps | pip + requirements.txt | - |

## Project Structure
```
fpl-optimizer/
├── CLAUDE.md              # This file - project context for Claude Code
├── TASKS.md               # Task tracking with sprint breakdowns
├── FPL_Optimizer_PRD.md   # Full product requirements document
├── docker-compose.yml     # All services orchestration
├── docker/
│   └── init_db.sql        # Creates fpl_optimizer + airflow_metadata DBs
├── .env.example           # Environment variable template
├── backend/               # FastAPI + Python
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic/           # Database migrations
│   ├── src/
│   │   ├── main.py        # FastAPI app entry point
│   │   ├── controllers/   # API endpoints (presentation layer)
│   │   ├── services/      # Business logic layer
│   │   ├── repositories/  # Data access layer (SQLAlchemy)
│   │   ├── models/        # SQLAlchemy ORM models
│   │   ├── schemas/       # Pydantic request/response schemas
│   │   ├── optimizer/     # PuLP optimization engine
│   │   └── config.py      # Settings and configuration
│   └── tests/
│       ├── unit/
│       ├── integration/
│       └── fixtures/
├── frontend/              # Next.js + TypeScript
│   ├── Dockerfile
│   ├── package.json
│   ├── app/               # Next.js App Router pages
│   ├── components/        # React components
│   ├── lib/               # API clients, types, utils
│   └── tests/
├── airflow/               # Airflow DAGs and config
│   ├── Dockerfile
│   ├── dags/              # DAG definitions
│   ├── plugins/
│   └── scripts/           # Python extraction/training scripts
├── dbt/                   # dbt transformation project
│   ├── dbt_project.yml
│   ├── models/
│   │   ├── bronze_to_silver/
│   │   └── silver_to_gold/
│   ├── tests/
│   └── macros/
├── models/                # Trained ML model files (.pkl)
└── docs/                  # Architecture diagrams, guides
```

## Architecture Rules

### Clean Architecture (Backend)
- **Controllers** handle HTTP only (parse request, return response). No business logic.
- **Services** contain all business logic. No direct DB access.
- **Repositories** handle all database operations via SQLAlchemy. No business logic.
- Dependencies flow inward: Controllers → Services → Repositories → Database

### Data Architecture (Medallion)
- **Bronze**: Raw JSON from FPL API. Append-only, never modified.
- **Silver**: Normalized, cleaned data in 3NF. Source of truth.
- **Gold**: Denormalized, ML-ready features. Derived from Silver via dbt.

### Database Rules
- `fpl_optimizer` database: All application data (Bronze/Silver/Gold tables)
- `airflow_metadata` database: Airflow internal tables only
- All schema changes go through Alembic migrations - never modify DB schema manually
- dbt manages Gold layer transformations (SQL-based, version controlled)

### Frontend Data Access
- Next.js API routes query PostgreSQL directly for simple reads (players, fixtures, gameweeks)
- FastAPI handles ML predictions and optimization (heavy compute)
- Never call FastAPI for simple CRUD operations

## Key Commands
```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up -d postgres redis

# View logs
docker-compose logs -f fastapi

# Run backend tests
docker-compose exec fastapi pytest -m unit
docker-compose exec fastapi pytest -m integration

# Run frontend tests
docker-compose exec nextjs npm test

# Run dbt models
docker-compose exec airflow dbt run --project-dir /opt/airflow/dbt

# Run dbt tests
docker-compose exec airflow dbt test --project-dir /opt/airflow/dbt

# Create Alembic migration
docker-compose exec fastapi alembic revision --autogenerate -m "description"

# Apply migrations
docker-compose exec fastapi alembic upgrade head

# Access Airflow UI
# http://localhost:8080 (admin/admin)
```

## Coding Conventions

### Python (Backend)
- Formatter: black (line length 88)
- Linter: ruff
- Type hints on all function signatures
- Docstrings on public functions (Google style)
- Test files mirror source structure: `src/services/foo.py` → `tests/unit/test_foo.py`

### TypeScript (Frontend)
- Formatter: prettier
- Linter: eslint
- Strict TypeScript mode enabled
- React components as functional components with TypeScript interfaces for props

### General
- No hardcoded credentials - use environment variables
- All API responses use Pydantic schemas (backend) or TypeScript interfaces (frontend)
- Git commit messages: imperative mood, concise ("Add player repository", not "Added player repository")

## Important Notes
- Historical data sourced from vaastav/Fantasy-Premier-League GitHub repo (CSV dumps)
- FPL API rate limit: ~50 requests/second. Implement exponential backoff for bulk player data extraction.
- The PRD (`FPL_Optimizer_PRD.md`) is the authoritative reference for all feature requirements and data schemas.
