# API Contract (Mock)

## Backend
- Health: `GET /health`

### Mock ACC
- `GET /mock/acc/projects`
- `GET /mock/acc/documents?project_id=...`

### Mock Procore
- `GET /mock/procore/projects`
- `GET /mock/procore/rfis?project_id=...`

### Mock HCSS
- `GET /mock/hcss/business-units`
- `GET /mock/hcss/jobs?business_unit_id=...`
- `GET /mock/hcss/cost-codes`
- `GET /mock/hcss/vendors`
- `GET /mock/hcss/tickets?job_id=...`

### Canonical API
- `GET/POST /api/unified-jobs`
- `GET/POST /api/vendor-maps`
- `GET/POST /api/cost-code-maps`
- `POST /api/reports/daily-trucking-summary?unified_job_id=...&date=YYYY-MM-DD`
- `GET /api/report-runs`
- `GET /api/audit-log`
