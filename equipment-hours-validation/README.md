# Equipment Hours Validation — Dashboard + ETL + Canonical Schema (POC/MVP)

Generated: 2026-03-01

This package is a build-ready technical design for an internal **Equipment Hours Validation** MVP/POC that reconciles:
- **Telematics / GPS runtime** (engine hours)
- **HCSS HeavyJob** timecard equipment hours (**provisional + approved/final**)
- **HCSS Safety inspections** meter readings + evidence (photos)
- **HCSS Equipment360** meter readings (shop-maintained truth)

## Project Structure

```
equipment-hours-validation/
├── src/                          # Main project source (from 02-equipment-hours-validation)
│   ├── connectors/               # Data source connectors
│   ├── normalization/            # Silver layer normalization
│   ├── reconciliation/           # Gold layer reconciliation
│   ├── mapping/                  # Equipment ID crosswalk mapping
│   ├── scheduling/               # Scheduling and backfill
│   ├── monitoring/               # Health checks
│   ├── dashboard/                # Dashboard views
│   ├── tests/                    # Unit and integration tests
│   ├── config/                   # Configuration files
│   ├── data/                     # Data storage (bronze/silver/gold)
│   └── docs/                     # Documentation
├── .windsurf/
│   ├── specs/
│   │   ├── active/               # Active build specs
│   │   └── archived/             # Completed build specs
│   └── workflows/                # Execution workflows
└── README.md
```

## Start Here

1. `src/docs/EXECUTIVE_SUMMARY.md` — Problem statement and solution overview
2. `src/docs/DASHBOARD_LAYOUT.md` — Dashboard design and metrics
3. `src/docs/ETL_SCHEDULE.md` — Data pipeline schedule
4. `src/docs/CANONICAL_SCHEMA.md` — Data model and schema
5. `src/specs/db_schema.sql` — Database schema implementation
6. `.windsurf/specs/active/` — Build phase specifications

## Key Concept

**Approval flow must not block validation.**
- Provisional truth powers daily audit (yesterday by 6am)
- Final truth updates as approvals land + nightly backfill

## Build Phases

- **Phase P0:** Repo, DB, and Config Loader Setup
- **Phase P1:** Connectors and Bronze Store
- **Phase P2:** Silver Normalization and Crosswalk Mapping
- **Phase P3:** Gold Reconciliation, Flags, and Exceptions
- **Phase P4:** Scheduling, Backfill, and Health Checks
- **Phase P5:** Dashboard Views, Runbooks, and UAT

See `.windsurf/specs/active/` for detailed phase specifications.

## Execution

To start a phase, use the PHASE_START_PROMPT workflow:

```
Start Phase <N>: <PHASE NAME>.

Follow .windsurf/workflows/execute-spec.md Step 2 exactly:
...
```

See `.windsurf/workflows/PHASE_START_PROMPT.md` for the complete template.

## Documentation

- `src/docs/EXECUTIVE_SUMMARY.md` — Problem and solution overview
- `src/docs/ARCHITECTURE_OVERVIEW.md` — System architecture
- `src/docs/DASHBOARD_LAYOUT.md` — Dashboard design
- `src/docs/ETL_SCHEDULE.md` — Data pipeline schedule
- `src/docs/CANONICAL_SCHEMA.md` — Data model
- `src/docs/FLAG_RULES.md` — Exception flag rules
- `src/specs/db_schema.sql` — Database schema
- `src/specs/pipeline_specs.yaml` — Pipeline configuration
