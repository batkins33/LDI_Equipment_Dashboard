from fastapi import APIRouter
from ..storage import list_fixture

router = APIRouter()

@router.get("/business-units")
def business_units():
    return list_fixture("hcss_business_units.json")

@router.get("/jobs")
def jobs(business_unit_id: str | None = None):
    jobs = list_fixture("hcss_jobs.json")
    if business_unit_id:
        jobs = [j for j in jobs if j.get("business_unit_id") == business_unit_id]
    return jobs

@router.get("/cost-codes")
def cost_codes():
    return list_fixture("hcss_cost_codes.json")

@router.get("/vendors")
def vendors():
    return list_fixture("hcss_vendors.json")

@router.get("/tickets")
def tickets(job_id: str | None = None):
    t = list_fixture("hcss_tickets.json")
    if job_id:
        t = [x for x in t if x.get("job_id") == job_id]
    return t
