# Data Dictionary (Key Fields)

## g_equipment_day_recon
- equipment_id, date_id (PK)
- gps_engine_hours
- tc_hours_provisional
- tc_hours_final
- inspection_meter_delta
- e360_meter_delta
- variance_tc_vs_gps
- variance_meter_vs_gps
- confidence_score (0–100)
- flags_count
- recon_state (PROVISIONAL/FINAL/MIXED)
- last_reconciled_at

## g_exceptions
- exception_id
- equipment_id, date_id, job_id (nullable)
- owner_employee_id
- status (OPEN/IN_PROGRESS/RESOLVED)
- priority
- title, description
- evidence_links_json
- created_at, updated_at

