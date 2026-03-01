# Unified Ops Dashboard — Mock Server MVP (ACC + Procore + HCSS)

This is a **Phase 0 mock-data MVP** intended to validate the integration architecture before wiring real vendor APIs.

It provides:
- **Backend:** FastAPI mock endpoints under `/mock/acc/*`, `/mock/procore/*`, `/mock/hcss/*`
- **Frontend:** React + Vite UI scaffolding (expand into 5 screens: Systems, Jobs, Mappings, Reports, Audit Log)
- **Fixtures:** sample projects/jobs/vendors/cost codes/tickets
- **Canonical API layer:** UnifiedJob, VendorMap, CostCodeMap, ReportRun, AuditLog (in-memory for POC)
- **Playwright UAT:** smoke test scaffold

## Quick start (local)

### Backend
```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8081
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Playwright UAT
```bash
cd uat
npm install
npx playwright install
npm test
```

Frontend expects backend at `http://127.0.0.1:8081`

## Docs
- `docs/MVP_OVERVIEW.md`
- `docs/API_CONTRACT.md`
- `docs/UAT.md`
