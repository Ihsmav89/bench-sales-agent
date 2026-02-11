"""Email and hotlist generation routes."""

from fastapi import APIRouter, Form, Request

from ...templates.emails import EmailTemplates
from ..app import get_agent, get_db, get_templates

router = APIRouter()


@router.get("")
async def email_page(request: Request):
    db = get_db(request)
    templates = get_templates(request)
    consultants = db.list_consultants()
    jobs = db.list_jobs()
    return templates.TemplateResponse("emails/index.html", {
        "request": request,
        "active": "emails",
        "consultants": consultants,
        "jobs": jobs,
    })


@router.post("/hotlist")
async def generate_hotlist(request: Request):
    db = get_db(request)
    templates = get_templates(request)
    consultants = db.list_consultants()
    if not consultants:
        return templates.TemplateResponse("emails/_preview.html", {
            "request": request,
            "error": "No consultants in database.",
        })
    email = EmailTemplates.hotlist_email(consultants)
    return templates.TemplateResponse("emails/_preview.html", {
        "request": request,
        "subject": email["subject"],
        "body": email["body"],
    })


@router.post("/submission")
async def generate_submission(
    request: Request,
    consultant_id: str = Form(...),
    job_id: str = Form(...),
):
    db = get_db(request)
    templates = get_templates(request)
    consultant = db.get_consultant(consultant_id)
    job = db.get_job(job_id)
    if not consultant or not job:
        return templates.TemplateResponse("emails/_preview.html", {
            "request": request,
            "error": "Consultant or job not found.",
        })
    email = EmailTemplates.submission_email(consultant, job)
    return templates.TemplateResponse("emails/_preview.html", {
        "request": request,
        "subject": email["subject"],
        "body": email["body"],
    })


@router.post("/ai-submission")
async def ai_submission(
    request: Request,
    consultant_id: str = Form(...),
    job_id: str = Form(...),
):
    db = get_db(request)
    agent = get_agent(request)
    templates = get_templates(request)
    consultant = db.get_consultant(consultant_id)
    job = db.get_job(job_id)
    if not consultant or not job:
        return templates.TemplateResponse("emails/_preview.html", {
            "request": request,
            "error": "Consultant or job not found.",
        })
    result = agent.craft_submission_email(consultant, job)
    return templates.TemplateResponse("emails/_preview.html", {
        "request": request,
        "subject": "AI-Crafted Submission",
        "body": result,
    })
