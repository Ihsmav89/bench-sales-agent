"""Market rate analysis route."""

from fastapi import APIRouter, Form, Request

from ..app import get_agent, get_templates

router = APIRouter()


@router.get("")
async def market_page(request: Request):
    templates = get_templates(request)
    return templates.TemplateResponse("market.html", {
        "request": request,
        "active": "market",
    })


@router.post("/analyze")
async def analyze(
    request: Request,
    job_title: str = Form(...),
    location: str = Form("Remote / US"),
    skills: str = Form(...),
):
    agent = get_agent(request)
    templates = get_templates(request)
    skill_list = [s.strip() for s in skills.split(",") if s.strip()]
    analysis = agent.market_rate_analysis(job_title, location, skill_list)
    return templates.TemplateResponse("market_result.html", {
        "request": request,
        "analysis": analysis,
    })
