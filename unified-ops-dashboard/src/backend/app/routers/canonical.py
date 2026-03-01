from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from uuid import uuid4
from datetime import datetime

router = APIRouter()

# In-memory store (POC). Replace with real DB.
STATE: Dict[str, list] = {
    "unified_jobs": [],
    "vendor_maps": [],
    "cost_code_maps": [],
    "report_runs": [],
    "audit_log": [],
}

def log(event: str, payload: dict):
    STATE["audit_log"].append({
        "ts": datetime.utcnow().isoformat() + "Z",
        "event": event,
        "payload": payload,
    })

class UnifiedJob(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    spectrum_job_code: Optional[str] = None
    hcss_job_id: Optional[str] = None
    acc_project_id: Optional[str] = None
    procore_project_id: Optional[str] = None

class VendorMap(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    vendor_name: str
    spectrum_vendor_code: Optional[str] = None
    hcss_vendor_id: Optional[str] = None

class CostCodeMap(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    cost_code: str
    spectrum_cost_code: Optional[str] = None
    hcss_cost_code: Optional[str] = None

class ReportRun(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    report_type: str
    unified_job_id: str
    params: dict = {}
    generated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    output: dict = {}

@router.get("/audit-log")
def audit_log():
    return list(reversed(STATE["audit_log"]))

@router.get("/unified-jobs", response_model=List[UnifiedJob])
def list_jobs():
    return STATE["unified_jobs"]

@router.post("/unified-jobs", response_model=UnifiedJob)
def create_job(job: UnifiedJob):
    STATE["unified_jobs"].append(job.model_dump())
    log("unified_job.created", job.model_dump())
    return job

@router.get("/vendor-maps", response_model=List[VendorMap])
def list_vendor_maps():
    return STATE["vendor_maps"]

@router.post("/vendor-maps", response_model=VendorMap)
def create_vendor_map(vm: VendorMap):
    STATE["vendor_maps"].append(vm.model_dump())
    log("vendor_map.created", vm.model_dump())
    return vm

@router.get("/cost-code-maps", response_model=List[CostCodeMap])
def list_cost_code_maps():
    return STATE["cost_code_maps"]

@router.post("/cost-code-maps", response_model=CostCodeMap)
def create_cost_code_map(cm: CostCodeMap):
    STATE["cost_code_maps"].append(cm.model_dump())
    log("cost_code_map.created", cm.model_dump())
    return cm

@router.post("/reports/daily-trucking-summary", response_model=ReportRun)
def run_daily_trucking_summary(unified_job_id: str, date: str):
    job = next((j for j in STATE["unified_jobs"] if j["id"] == unified_job_id), None)
    if not job:
        raise HTTPException(status_code=404, detail="unified_job_id not found")

    output = {
        "date": date,
        "unified_job": job,
        "kpis": {"tickets": 12, "tons": 320.5, "vendors": 3},
        "notes": "Mock data — replace with real ingestion logic.",
    }

    rr = ReportRun(report_type="Daily Trucking Summary", unified_job_id=unified_job_id, params={"date": date}, output=output)
    STATE["report_runs"].append(rr.model_dump())
    log("report_run.created", rr.model_dump())
    return rr

@router.get("/report-runs", response_model=List[ReportRun])
def list_report_runs():
    return STATE["report_runs"]
