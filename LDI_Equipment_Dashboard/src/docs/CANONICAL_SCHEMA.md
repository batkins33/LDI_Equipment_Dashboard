# Canonical Schema & Join Keys

## Reconciliation grain
**Equipment × Day**

## Non-negotiable join strategy
1) Use internal surrogate IDs:
- equipment_id, job_id, employee_id, business_unit_id

2) Maintain crosswalks:
- map_equipment_external (HeavyJob / Safety / E360 / Telematics IDs)
- map_job_external
- map_employee_external

3) Facts store internal IDs + source external IDs for traceability.

## Core tables
Dimensions:
- dim_equipment, dim_job, dim_employee, dim_business_unit, dim_cost_code, dim_date

Silver facts:
- f_timecard_header
- f_timecard_equipment_hours
- f_telematics_equipment_day
- f_inspection_equipment_day
- f_e360_meter_reading

Gold facts:
- g_equipment_day_recon
- g_equipment_day_flags
- g_exceptions

