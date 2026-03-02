# Master POC Bundle — Unified Ops Dashboard + Equipment Hours Validation

This bundle combines two proof-of-concept packages.

## 01 — Unified Ops Dashboard (Mock Server MVP)
**Purpose:** validate the integration architecture across systems (ACC / Procore / HCSS) using mock endpoints + a canonical binding layer.
- Folder: `01-unified-ops-mock-mvp/`
- Start: `01-unified-ops-mock-mvp/README.md`

## 02 — Equipment Hours Validation (HCSS + Telematics + Inspections + Equipment360)
**Purpose:** validate equipment-hour accuracy using a **provisional-by-6am** model plus **approval overlay** and **nightly backfill**.
- Folder: `02-equipment-hours-validation/`
- Start: `02-equipment-hours-validation/README.md`

## Recommended order
1) Run **01** first to prove canonical job binding + UI workflows with mock data.
2) Run **02** next to prove hours reconciliation + exception workflow (mock → live).
3) Merge the two into a single internal “Ops Intelligence Hub” once both are stable.
