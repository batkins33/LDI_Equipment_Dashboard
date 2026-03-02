# Equipment Hours Validation — Dashboard + ETL + Canonical Schema (POC/MVP)

Generated: 2026-02-27

This package is a build-ready technical design for an internal **Equipment Hours Validation** MVP/POC that reconciles:
- **Telematics / GPS runtime** (engine hours)
- **HCSS HeavyJob** timecard equipment hours (**provisional + approved/final**)
- **HCSS Safety inspections** meter readings + evidence (photos)
- **HCSS Equipment360** meter readings (shop-maintained truth)

## Start here
1) `docs/EXECUTIVE_SUMMARY.md`
2) `docs/DASHBOARD_LAYOUT.md`
3) `docs/ETL_SCHEDULE.md`
4) `docs/CANONICAL_SCHEMA.md`
5) Implement DB: `specs/db_schema.sql`
6) Use dev-agent build prompt: `agent/DEV_AGENT_PROMPT.md`

## Key idea
**Approval flow must not block validation.**
- Provisional truth powers daily audit (yesterday by 6am)
- Final truth updates as approvals land + nightly backfill

