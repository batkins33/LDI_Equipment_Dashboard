# Daily ETL Schedule (America/Chicago)

## SLA
- **Yesterday Provisional ready by 06:00**

## Pipelines
01:00 — Refresh master data (jobs, equipment, employees, cost codes, mappings)

Hourly (:15) — Telematics runtime pull (2-hour overlap)

03:00 — Safety inspections pull (yesterday + last 3 days overlap)

04:00 — Equipment360 meter readings (last 7 days + latest)

05:00 — HeavyJob timecards + equipment hours (yesterday + last 7 days overlap)

05:30 — Build Gold recon (yesterday + last 7 days) + flags + publish dashboard views

Every 30 min — Approval overlay (last 14 days) + recompute affected Gold rows

23:00 — Nightly backfill (last 30 days) + rebuild aggregates + health checks

## Notes
- Always use overlap windows (late-arriving updates)
- Persist raw payloads in Bronze for auditability
- Track high-watermarks when possible

