"""Job requirements routes."""

from datetime import date

from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse

from ...models.job import JobRequirement
from ..app import get_db, get_templates

router = APIRouter()


@router.get("")
async def list_jobs(request: Request):
    db = get_db(request)
    templates = get_templates(request)
    jobs = db.list_jobs()
    return templates.TemplateResponse("jobs/list.html", {
        "request": request,
        "active": "jobs",
        "jobs": jobs,
    })


@router.get("/add")
async def add_form(request: Request):
    templates = get_templates(request)
    return templates.TemplateResponse("jobs/add.html", {
        "request": request,
        "active": "jobs",
    })


@router.post("")
async def create_job(
    request: Request,
    title: str = Form(...),
    client_name: str = Form(""),
    vendor_name: str = Form(...),
    vendor_contact_email: str = Form(""),
    description: str = Form(""),
    required_skills: str = Form(...),
    location: str = Form("Remote"),
    remote_option: str = Form("Remote"),
    duration_months: int = Form(12),
    bill_rate: float = Form(0),
    employment_type: str = Form("C2C"),
    source_platform: str = Form("email"),
):
    db = get_db(request)
    job = JobRequirement(
        title=title,
        client_name=client_name or None,
        vendor_name=vendor_name,
        vendor_contact_email=vendor_contact_email or None,
        description=description,
        required_skills=[s.strip() for s in required_skills.split(",") if s.strip()],
        location=location,
        remote_option=remote_option,
        duration_months=duration_months,
        bill_rate=bill_rate if bill_rate > 0 else None,
        employment_type=employment_type,
        source_platform=source_platform,
        posted_date=date.today(),
    )
    db.add_job(job)
    return RedirectResponse("/jobs", status_code=303)


@router.post("/match")
async def match_jobs(request: Request, consultant_id: str = Form(...)):
    db = get_db(request)
    templates = get_templates(request)
    consultant = db.get_consultant(consultant_id)
    if not consultant:
        return templates.TemplateResponse("jobs/_match_results.html", {
            "request": request,
            "error": "Consultant not found",
        })
    jobs = db.list_jobs()
    matches = []
    for j in jobs:
        score = j.match_score(consultant.primary_skills + consultant.secondary_skills)
        matches.append((j, score))
    matches.sort(key=lambda x: x[1], reverse=True)
    return templates.TemplateResponse("jobs/_match_results.html", {
        "request": request,
        "matches": matches[:15],
        "consultant": consultant,
    })
