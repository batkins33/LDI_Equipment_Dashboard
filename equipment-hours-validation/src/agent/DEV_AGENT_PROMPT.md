# Dev Agent Prompt — Implement Equipment Hours Validation MVP

You are a senior data engineer. Build the MVP exactly per:
- docs/EXECUTIVE_SUMMARY.md
- docs/ETL_SCHEDULE.md
- docs/CANONICAL_SCHEMA.md
- docs/DASHBOARD_LAYOUT.md
- specs/db_schema.sql
- specs/pipeline_specs.yaml
- specs/config/*

## Deliverables
- Python service or jobs that:
  - Pull data from HeavyJob, Safety, Equipment360, Telematics
  - Store raw payloads (bronze)
  - Normalize into silver facts
  - Build gold equipment-day recon + flags + exceptions
- SQL views for dashboard (yesterday provisional, exceptions, lag, compliance, telematics health)
- Idempotent upserts with overlap windows
- Unit tests for mapping + recon + flags
- HOW_TO_RUN + DEPLOY docs

## Key requirements
- Compute provisional daily without approvals blocking
- Overlay final as approvals land (incremental recompute)
- Nightly backfill last 30 days deterministic

## Phases
P0 Repo + DB + config loader
P1 Connectors + bronze store
P2 Silver normalization + crosswalk mapping
P3 Gold recon + flags + exceptions
P4 Scheduling + backfill + health checks
P5 Dashboard views + runbooks + UAT with mock fixtures

Return a short build report after each phase and include paths to key files.
