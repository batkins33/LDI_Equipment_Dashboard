# Unified Ops Dashboard (Mock MVP)

This is a **Phase 0 mock-data MVP** intended to validate the integration architecture before wiring real vendor APIs.

It provides:
- **Backend:** FastAPI mock endpoints under `/mock/acc/*`, `/mock/procore/*`, `/mock/hcss/*`
- **Frontend:** React + Vite UI scaffolding (5 screens: Systems, Jobs, Mappings, Reports, Audit Log)
- **Fixtures:** sample projects/jobs/vendors/cost codes/tickets
- **Canonical API layer:** UnifiedJob, VendorMap, CostCodeMap, ReportRun, AuditLog
- **Playwright UAT:** smoke test scaffold

## Project Structure

```
unified-ops-dashboard/
├── src/                          # Main project source (from 01-unified-ops-mock-mvp)
│   ├── backend/
│   │   ├── app/
│   │   ├── requirements.txt
│   │   └── ...
│   ├── frontend/
│   │   ├── src/
│   │   ├── package.json
│   │   └── ...
│   ├── uat/
│   │   ├── tests/
│   │   └── ...
│   └── docs/
├── .windsurf/
│   ├── specs/
│   │   ├── active/              # Active build specs
│   │   └── archived/            # Completed build specs
│   └── workflows/               # Execution workflows
└── README.md
```

## Quick Start

### Backend
```bash
cd src/backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8081
```

### Frontend
```bash
cd src/frontend
npm install
npm run dev
```

### Playwright UAT
```bash
cd src/uat
npm install
npx playwright install
npm test
```

Frontend expects backend at `http://127.0.0.1:8081`

## Build Phases

- **Phase 1:** UI Screens Implementation
- **Phase 2:** Database Persistence Integration
- **Phase 3:** Real API Connectors

See `.windsurf/specs/active/` for detailed phase specifications.

## Documentation

- `src/docs/MVP_OVERVIEW.md` — MVP scope and goals
- `src/docs/API_CONTRACT.md` — API endpoints and contracts
- `src/docs/UAT.md` — UAT procedures

## Execution

To start a phase, use the PHASE_START_PROMPT workflow:

```
Start Phase <N>: <PHASE NAME>.

Follow .windsurf/workflows/execute-spec.md Step 2 exactly:
...
```

See `.windsurf/workflows/PHASE_START_PROMPT.md` for the complete template.
