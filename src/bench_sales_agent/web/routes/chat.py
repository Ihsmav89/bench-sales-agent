"""AI chat route."""

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse

from ..app import get_agent, get_db, get_templates

router = APIRouter()


@router.get("")
async def chat_page(request: Request):
    templates = get_templates(request)
    return templates.TemplateResponse("chat.html", {
        "request": request,
        "active": "chat",
    })


@router.post("/send")
async def send_message(request: Request, message: str = Form(...)):
    agent = get_agent(request)
    db = get_db(request)
    templates = get_templates(request)
    stats = db.get_stats()
    response = agent.chat(message, context={"database_stats": stats})
    return templates.TemplateResponse("chat_response.html", {
        "request": request,
        "user_message": message,
        "agent_response": response,
    })
