"""Submissions and follow-up routes."""

from fastapi import APIRouter, Request

from ..app import get_db, get_templates

router = APIRouter()


@router.get("")
async def list_submissions(request: Request, consultant_id: str = ""):
    db = get_db(request)
    templates = get_templates(request)
    if consultant_id:
        subs = db.get_submissions_for_consultant(consultant_id)
    else:
        subs = db.list_pending_followups()
    consultants = db.list_consultants()
    return templates.TemplateResponse("submissions/list.html", {
        "request": request,
        "active": "submissions",
        "submissions": subs,
        "consultants": consultants,
        "selected_consultant": consultant_id,
    })
