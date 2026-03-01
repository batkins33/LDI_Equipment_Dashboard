from fastapi import APIRouter
from ..storage import list_fixture

router = APIRouter()

@router.get("/projects")
def projects():
    return list_fixture("procore_projects.json")

@router.get("/rfis")
def rfis(project_id: str | None = None):
    items = list_fixture("procore_rfis.json")
    if project_id:
        items = [i for i in items if i.get("project_id") == project_id]
    return items
