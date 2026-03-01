-- Equipment Hours Validation canonical schema (Postgres-ish; adjust for SQL Server as needed)

CREATE TABLE IF NOT EXISTS dim_date (date_id DATE PRIMARY KEY);

CREATE TABLE IF NOT EXISTS dim_business_unit (
  business_unit_id BIGSERIAL PRIMARY KEY,
  business_unit_code TEXT UNIQUE NOT NULL,
  business_unit_name TEXT
);

CREATE TABLE IF NOT EXISTS dim_job (
  job_id BIGSERIAL PRIMARY KEY,
  business_unit_id BIGINT REFERENCES dim_business_unit(business_unit_id),
  job_code TEXT NOT NULL,
  job_name TEXT,
  active_flag BOOLEAN DEFAULT TRUE,
  UNIQUE (business_unit_id, job_code)
);

CREATE TABLE IF NOT EXISTS dim_employee (
  employee_id BIGSERIAL PRIMARY KEY,
  employee_code TEXT UNIQUE,
  employee_name TEXT,
  active_flag BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS dim_equipment (
  equipment_id BIGSERIAL PRIMARY KEY,
  equipment_code TEXT UNIQUE,
  equipment_name TEXT,
  equipment_type TEXT,
  equipment_class TEXT,
  owned_or_rental TEXT,
  active_flag BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS dim_cost_code (
  cost_code_id BIGSERIAL PRIMARY KEY,
  cost_code TEXT UNIQUE,
  description TEXT
);

CREATE TABLE IF NOT EXISTS map_equipment_external (
  equipment_external_map_id BIGSERIAL PRIMARY KEY,
  equipment_id BIGINT NOT NULL REFERENCES dim_equipment(equipment_id),
  system TEXT NOT NULL,  -- HEAVYJOB/SAFETY/EQUIP360/TELEMATICS
  external_equipment_id TEXT NOT NULL,
  external_device_id TEXT,
  is_primary BOOLEAN DEFAULT TRUE,
  effective_start TIMESTAMP,
  effective_end TIMESTAMP
);

CREATE TABLE IF NOT EXISTS f_timecard_header (
  timecard_id TEXT PRIMARY KEY,
  business_unit_id BIGINT REFERENCES dim_business_unit(business_unit_id),
  job_id BIGINT REFERENCES dim_job(job_id),
  foreman_employee_id BIGINT REFERENCES dim_employee(employee_id),
  work_date DATE NOT NULL REFERENCES dim_date(date_id),
  status TEXT,
  submitted_at TIMESTAMP,
  approved_at TIMESTAMP,
  source_last_modified_at TIMESTAMP,
  snapshot_ts TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS f_timecard_equipment_hours (
  timecard_id TEXT NOT NULL REFERENCES f_timecard_header(timecard_id),
  equipment_id BIGINT NOT NULL REFERENCES dim_equipment(equipment_id),
  cost_code_id BIGINT REFERENCES dim_cost_code(cost_code_id),
  hours NUMERIC(10,2) NOT NULL,
  is_provisional BOOLEAN DEFAULT TRUE,
  snapshot_ts TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS f_telematics_equipment_day (
  equipment_id BIGINT NOT NULL REFERENCES dim_equipment(equipment_id),
  date_id DATE NOT NULL REFERENCES dim_date(date_id),
  engine_hours NUMERIC(10,2),
  snapshot_ts TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS f_inspection_equipment_day (
  equipment_id BIGINT NOT NULL REFERENCES dim_equipment(equipment_id),
  date_id DATE NOT NULL REFERENCES dim_date(date_id),
  inspector_employee_id BIGINT REFERENCES dim_employee(employee_id),
  hour_meter_start NUMERIC(12,2),
  hour_meter_end NUMERIC(12,2),
  meter_delta NUMERIC(12,2),
  photo_count INT,
  issues_count INT,
  snapshot_ts TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS f_e360_meter_reading (
  equipment_id BIGINT NOT NULL REFERENCES dim_equipment(equipment_id),
  reading_at TIMESTAMP NOT NULL,
  meter_type TEXT NOT NULL,
  meter_value NUMERIC(12,2) NOT NULL,
  snapshot_ts TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS g_equipment_day_recon (
  equipment_id BIGINT NOT NULL REFERENCES dim_equipment(equipment_id),
  date_id DATE NOT NULL REFERENCES dim_date(date_id),
  gps_engine_hours NUMERIC(10,2),
  tc_hours_provisional NUMERIC(10,2),
  tc_hours_final NUMERIC(10,2),
  inspection_meter_delta NUMERIC(10,2),
  e360_meter_delta NUMERIC(10,2),
  variance_tc_vs_gps NUMERIC(10,2),
  variance_meter_vs_gps NUMERIC(10,2),
  confidence_score INT,
  flags_count INT,
  recon_state TEXT,
  last_reconciled_at TIMESTAMP,
  PRIMARY KEY (equipment_id, date_id)
);

CREATE TABLE IF NOT EXISTS g_equipment_day_flags (
  equipment_id BIGINT NOT NULL REFERENCES dim_equipment(equipment_id),
  date_id DATE NOT NULL REFERENCES dim_date(date_id),
  flag_code TEXT NOT NULL,
  severity TEXT NOT NULL,
  details_json TEXT,
  created_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS g_exceptions (
  exception_id BIGSERIAL PRIMARY KEY,
  equipment_id BIGINT REFERENCES dim_equipment(equipment_id),
  date_id DATE REFERENCES dim_date(date_id),
  job_id BIGINT REFERENCES dim_job(job_id),
  owner_employee_id BIGINT REFERENCES dim_employee(employee_id),
  status TEXT DEFAULT 'OPEN',
  priority TEXT DEFAULT 'MED',
  title TEXT,
  description TEXT,
  evidence_links_json TEXT,
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP
);
