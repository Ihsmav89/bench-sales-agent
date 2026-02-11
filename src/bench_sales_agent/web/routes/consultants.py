"""Consultant management routes."""

from datetime import date

from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse

from ...models.consultant import ConsultantProfile, EmploymentType, VisaStatus
from ..app import get_agent, get_db, get_templates

router = APIRouter()


@router.get("")
async def list_consultants(request: Request):
    db = get_db(request)
    templates = get_templates(request)
    consultants = db.list_consultants()
    return templates.TemplateResponse("consultants/list.html", {
        "request": request,
        "active": "consultants",
        "consultants": consultants,
    })


@router.get("/add")
async def add_form(request: Request):
    templates = get_templates(request)
    return templates.TemplateResponse("consultants/add.html", {
        "request": request,
        "active": "consultants",
        "visa_statuses": list(VisaStatus),
    })


@router.post("")
async def create_consultant(
    request: Request,
    full_name: str = Form(...),
    email: str = Form(""),
    phone: str = Form(""),
    current_location: str = Form(""),
    job_title: str = Form(...),
    primary_skills: str = Form(...),
    secondary_skills: str = Form(""),
    total_experience_years: float = Form(0),
    us_experience_years: float = Form(0),
    visa_status: str = Form("H1B"),
    remote_preference: str = Form("Remote"),
    relocation: bool = Form(False),
    expected_rate_hourly: float = Form(0),
    minimum_rate_hourly: float = Form(0),
):
    db = get_db(request)
    consultant = ConsultantProfile(
        full_name=full_name,
        email=email,
        phone=phone,
        current_location=current_location,
        job_title=job_title,
        primary_skills=[s.strip() for s in primary_skills.split(",") if s.strip()],
        secondary_skills=[s.strip() for s in secondary_skills.split(",") if s.strip()],
        total_experience_years=total_experience_years,
        us_experience_years=us_experience_years,
        visa_status=VisaStatus(visa_status),
        remote_preference=remote_preference,
        relocation=relocation,
        expected_rate_hourly=expected_rate_hourly if expected_rate_hourly > 0 else None,
        minimum_rate_hourly=minimum_rate_hourly if minimum_rate_hourly > 0 else None,
        bench_since=date.today(),
        employment_types_accepted=[EmploymentType.C2C],
    )
    db.add_consultant(consultant)
    return RedirectResponse("/consultants", status_code=303)


@router.get("/{consultant_id}")
async def detail(request: Request, consultant_id: str):
    db = get_db(request)
    templates = get_templates(request)
    consultant = db.get_consultant(consultant_id)
    if not consultant:
        return RedirectResponse("/consultants", status_code=303)
    return templates.TemplateResponse("consultants/detail.html", {
        "request": request,
        "active": "consultants",
        "c": consultant,
    })


@router.post("/{consultant_id}/analyze")
async def analyze(request: Request, consultant_id: str):
    db = get_db(request)
    agent = get_agent(request)
    templates = get_templates(request)
    consultant = db.get_consultant(consultant_id)
    if not consultant:
        return templates.TemplateResponse("consultants/_analysis.html", {
            "request": request,
            "error": "Consultant not found",
        })
    analysis = agent.analyze_consultant(consultant)
    return templates.TemplateResponse("consultants/_analysis.html", {
        "request": request,
        "analysis": analysis,
    })


@router.post("/{consultant_id}/delete")
async def delete_consultant(request: Request, consultant_id: str):
    db = get_db(request)
    db.delete_consultant(consultant_id)
    return RedirectResponse("/consultants", status_code=303)
