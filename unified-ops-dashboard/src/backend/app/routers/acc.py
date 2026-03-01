from fastapi import APIRouter
from ..storage import list_fixture

router = APIRouter()

@router.get("/projects")
def projects():
    return list_fixture("acc_projects.json")

@router.get("/documents")
def documents(project_id: str | None = None):
    docs = list_fixture("acc_documents.json")
    if project_id:
        docs = [d for d in docs if d.get("project_id") == project_id]
    return docs
