"""Dashboard route — home page with stats overview."""

from fastapi import APIRouter, Request

from ..app import get_db, get_templates

router = APIRouter()


@router.get("/")
async def dashboard(request: Request):
    db = get_db(request)
    templates = get_templates(request)
    stats = db.get_stats()
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "active": "dashboard",
        "stats": stats,
    })
