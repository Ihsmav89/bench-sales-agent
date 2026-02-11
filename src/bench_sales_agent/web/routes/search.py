"""Search routes — X-ray queries, board links."""

from fastapi import APIRouter, Form, Request

from ...search.job_board_urls import JobBoardURLBuilder
from ...search.xray_engine import ConsultantSearchParams, XRaySearchEngine
from ..app import get_db, get_templates

router = APIRouter()


@router.get("")
async def search_page(request: Request):
    db = get_db(request)
    templates = get_templates(request)
    consultants = db.list_consultants()
    return templates.TemplateResponse("search/index.html", {
        "request": request,
        "active": "search",
        "consultants": consultants,
    })


@router.post("/xray")
async def xray_search(
    request: Request,
    mode: str = Form("custom"),
    consultant_id: str = Form(""),
    job_title: str = Form(""),
    skills: str = Form(""),
    location: str = Form(""),
):
    db = get_db(request)
    templates = get_templates(request)
    engine = XRaySearchEngine()

    if mode == "consultant" and consultant_id:
        consultant = db.get_consultant(consultant_id)
        if not consultant:
            return templates.TemplateResponse("search/_results.html", {
                "request": request,
                "error": "Consultant not found",
            })
        params = ConsultantSearchParams(
            job_title=consultant.job_title,
            primary_skills=consultant.primary_skills,
            secondary_skills=consultant.secondary_skills,
            location=consultant.current_location,
            remote_ok=consultant.remote_preference.lower() in ("remote", "hybrid"),
            visa_status=consultant.visa_status.value,
        )
        title_label = f"{consultant.full_name} — {consultant.job_title}"
    else:
        skill_list = [s.strip() for s in skills.split(",") if s.strip()]
        params = ConsultantSearchParams(
            job_title=job_title,
            primary_skills=skill_list,
            location=location,
            remote_ok=True,
        )
        title_label = job_title

    queries = engine.generate_all_queries(params)
    hotlist = engine.generate_hotlist_queries(params)

    # Group by category
    categories = {}
    for q in queries + hotlist:
        cat = q.category or "general"
        categories.setdefault(cat, []).append(q)
    for cat_queries in categories.values():
        cat_queries.sort(key=lambda x: x.priority)

    # Board links
    board_links = JobBoardURLBuilder.all_boards(
        params.job_title, params.location or ""
    )

    return templates.TemplateResponse("search/_results.html", {
        "request": request,
        "title_label": title_label,
        "categories": categories,
        "total_queries": len(queries) + len(hotlist),
        "board_links": board_links,
    })
