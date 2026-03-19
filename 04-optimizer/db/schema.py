# optimizer SCHEMA definitions

from sqlalchemy import (MetaData, Table, Column, BigInteger, SmallInteger, String, Numeric, UniqueConstraint, Index, Text, CheckConstraint)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy import TIMESTAMP 

optimizer_metadata = MetaData(schema="optimizer")

# optimizer SCHEMA
# 1. optimizer results table
# saves the squad as a single JSONB datatype as they are grouped
# triggered_by to follow 03-ml design and allow fast query on pipeline runs for common requests (i.e. ones where user input_params = NULL)
optimizer_runs = Table(
    "optimizer_runs", optimizer_metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("run_id", UUID(as_uuid=True), nullable=False),           
    Column("run_at", TIMESTAMP(timezone=True), nullable=False),
    Column("gameweek_id", SmallInteger, nullable=False), #features gameweek. prediction is +1
    Column("season_id", SmallInteger, nullable=False),
    Column("horizon", SmallInteger, nullable=False), #1/3
    Column("chip", String(50)), #null/free_hit/wildcard/bench_boost/triple_captain
    Column("free_transfers", SmallInteger),
    Column("transfer_hits", SmallInteger),
    Column("expected_pts", Numeric(8, 4)),
    Column("expected_pts_after_hits", Numeric(8, 4)),
    Column("budget_used", Numeric(6, 1)),
    Column("budget_remaining", Numeric(6, 1)),
    Column("squad", JSONB, nullable=False), 
    Column("transfers_in", JSONB),
    Column("transfers_out", JSONB),
    Column("triggered_by", String(20), nullable=False), #pipeline/manual/experiment
    UniqueConstraint("run_id", name="uq_optimizer_runs_run_id"),
    CheckConstraint("chip IN ('free_hit','wildcard','bench_boost','triple_captain')", name="ck_optimizer_runs_chip"),
    CheckConstraint("triggered_by IN ('pipeline','manual','experiment')", name="ck_optimizer_runs_triggered_by"),
)

Index("ix_optimizer_runs_gameweek_id", optimizer_runs.c.gameweek_id)
Index("ix_optimizer_runs_season_id", optimizer_runs.c.season_id)
Index("ix_optimizer_runs_chip", optimizer_runs.c.chip)
Index("ix_optimizer_runs_triggered_by", optimizer_runs.c.triggered_by)
Index("uix_optimizer_runs_pipeline",
        optimizer_runs.c.gameweek_id,
        optimizer_runs.c.season_id,
        optimizer_runs.c.horizon,
        optimizer_runs.c.chip,
        unique=True,
        postgresql_where=optimizer_runs.c.triggered_by == "pipeline")

#2. optimizer run logger
# Captures inputs and outputs for each optimizer run. run_id is NULL when the run fails before producing a result.
optimizer_run_logs = Table(
    "optimizer_run_logs", optimizer_metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("run_id", UUID(as_uuid=True)),           
    Column("run_at", TIMESTAMP(timezone=True), nullable=False),
    Column("status", String(50), nullable=False), #optimal/error/infeasible
    Column("solve_time_ms", BigInteger, nullable=False),
    Column("input_params", JSONB, nullable=False),
    Column("config_snapshot", JSONB),
    Column("error_message", Text),
    CheckConstraint("status IN ('optimal','error','infeasible')", name="ck_optimizer_run_logs_status"),
)
Index("ix_optimizer_run_logs_run_id", optimizer_run_logs.c.run_id)
Index("ix_optimizer_run_logs_run_at", optimizer_run_logs.c.run_at)
