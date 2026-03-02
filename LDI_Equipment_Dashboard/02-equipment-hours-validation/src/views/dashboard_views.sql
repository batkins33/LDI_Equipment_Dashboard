CREATE VIEW IF NOT EXISTS v_executive_overview AS
SELECT
  r.date_id,
  COUNT(*) AS equipment_days,
  SUM(CASE WHEN r.recon_state = 'EXCEPTION' THEN 1 ELSE 0 END) AS exception_days,
  ROUND(AVG(COALESCE(r.confidence_score, 0)), 2) AS avg_confidence,
  SUM(COALESCE(r.flags_count, 0)) AS total_flags
FROM g_equipment_day_recon r
GROUP BY r.date_id;

CREATE VIEW IF NOT EXISTS v_yesterday_provisional AS
SELECT
  r.date_id,
  e.equipment_code,
  r.equipment_id,
  r.tc_hours_provisional,
  r.gps_engine_hours,
  r.variance_tc_vs_gps,
  r.confidence_score,
  r.recon_state,
  r.flags_count
FROM g_equipment_day_recon r
LEFT JOIN dim_equipment e ON e.equipment_id = r.equipment_id
WHERE r.recon_state = 'PROVISIONAL';

CREATE VIEW IF NOT EXISTS v_exceptions_queue AS
SELECT
  x.exception_id,
  x.status,
  x.priority,
  x.date_id,
  e.equipment_code,
  x.equipment_id,
  j.job_code,
  x.job_id,
  x.title,
  x.description,
  x.created_at,
  x.updated_at
FROM g_exceptions x
LEFT JOIN dim_equipment e ON e.equipment_id = x.equipment_id
LEFT JOIN dim_job j ON j.job_id = x.job_id
WHERE x.status = 'OPEN'
ORDER BY x.priority DESC, x.created_at DESC;

CREATE VIEW IF NOT EXISTS v_approval_flow_health AS
SELECT
  h.work_date AS date_id,
  COUNT(*) AS timecards_total,
  SUM(CASE WHEN h.status = 'APPROVED' THEN 1 ELSE 0 END) AS timecards_approved,
  SUM(CASE WHEN h.status != 'APPROVED' THEN 1 ELSE 0 END) AS timecards_pending
FROM f_timecard_header h
GROUP BY h.work_date;

CREATE VIEW IF NOT EXISTS v_inspections_compliance AS
SELECT
  i.date_id,
  COUNT(DISTINCT i.equipment_id) AS inspected_equipment_count,
  SUM(CASE WHEN i.issues_count > 0 THEN 1 ELSE 0 END) AS equipment_with_issues
FROM f_inspection_equipment_day i
GROUP BY i.date_id;

CREATE VIEW IF NOT EXISTS v_telematics_health AS
SELECT
  t.date_id,
  COUNT(DISTINCT t.equipment_id) AS telematics_equipment_count,
  SUM(CASE WHEN COALESCE(t.gps_active, 1) = 1 THEN 1 ELSE 0 END) AS gps_active_days,
  SUM(CASE WHEN COALESCE(t.gps_active, 1) = 0 THEN 1 ELSE 0 END) AS gps_inactive_days
FROM f_telematics_equipment_day t
GROUP BY t.date_id;

CREATE VIEW IF NOT EXISTS v_equipment_drilldown AS
SELECT
  r.date_id,
  r.equipment_id,
  e.equipment_code,
  r.gps_engine_hours,
  r.tc_hours_provisional,
  r.tc_hours_final,
  r.inspection_meter_delta,
  r.e360_meter_delta,
  r.variance_tc_vs_gps,
  r.variance_meter_vs_gps,
  r.confidence_score,
  r.recon_state,
  r.flags_count
FROM g_equipment_day_recon r
LEFT JOIN dim_equipment e ON e.equipment_id = r.equipment_id;
