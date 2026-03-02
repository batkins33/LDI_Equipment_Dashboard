# API Spec (P0.5 Demo)

## Base

- Base URL: `http://localhost:5000`
- Content-Type: `application/json`

## Endpoints

### GET `/api/health`

Returns basic health status.

### GET `/api/dashboard/overview`

Returns rows from `v_executive_overview`.

Query params:

- `start_date` (optional, `YYYY-MM-DD`)
- `end_date` (optional, `YYYY-MM-DD`)

### GET `/api/dashboard/provisional`

Returns rows from `v_yesterday_provisional`.

Query params:

- `date` (optional, `YYYY-MM-DD`)

### GET `/api/dashboard/exceptions`

Returns rows from `v_exceptions_queue`.

### GET `/api/dashboard/approval-flow`

Returns rows from `v_approval_flow_health`.

Query params:

- `start_date` (optional, `YYYY-MM-DD`)
- `end_date` (optional, `YYYY-MM-DD`)

### GET `/api/dashboard/inspections`

Returns rows from `v_inspections_compliance`.

Query params:

- `start_date` (optional, `YYYY-MM-DD`)
- `end_date` (optional, `YYYY-MM-DD`)

### GET `/api/dashboard/telematics`

Returns rows from `v_telematics_health`.

Query params:

- `start_date` (optional, `YYYY-MM-DD`)
- `end_date` (optional, `YYYY-MM-DD`)

### GET `/api/dashboard/equipment`

Returns rows from `v_equipment_drilldown`.

Query params:

- `equipment_id` (optional, integer)
- `start_date` (optional, `YYYY-MM-DD`)
- `end_date` (optional, `YYYY-MM-DD`)
