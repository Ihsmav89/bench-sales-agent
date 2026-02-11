"""FastAPI web application for the Bench Sales Agent."""

from __future__ import annotations

import argparse
import os
import sys
import webbrowser
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

from ..agent import BenchSalesAgent
from ..data.database import Database

TEMPLATES_DIR = Path(__file__).parent / "templates"


@asynccontextmanager
async def lifespan(app: FastAPI):
    db_path = os.environ.get("BENCH_DB_PATH")
    app.state.db = Database(db_path)
    app.state.agent = BenchSalesAgent()
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="Bench Sales Agent", lifespan=lifespan)
    app.state.templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

    from .routes import chat, consultants, dashboard, emails, jobs, market, search, submissions, vendors

    app.include_router(dashboard.router)
    app.include_router(consultants.router, prefix="/consultants", tags=["consultants"])
    app.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
    app.include_router(vendors.router, prefix="/vendors", tags=["vendors"])
    app.include_router(submissions.router, prefix="/submissions", tags=["submissions"])
    app.include_router(search.router, prefix="/search", tags=["search"])
    app.include_router(emails.router, prefix="/emails", tags=["emails"])
    app.include_router(chat.router, prefix="/chat", tags=["chat"])
    app.include_router(market.router, prefix="/market", tags=["market"])

    return app


def get_db(request: Request) -> Database:
    return request.app.state.db


def get_agent(request: Request) -> BenchSalesAgent:
    return request.app.state.agent


def get_templates(request: Request) -> Jinja2Templates:
    return request.app.state.templates


def main():
    import uvicorn

    parser = argparse.ArgumentParser(description="Bench Sales Agent Web UI")
    parser.add_argument("--port", type=int, default=8000, help="Port to listen on")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--db-path", default=None, help="Path to database file")
    parser.add_argument("--no-browser", action="store_true", help="Don't auto-open browser")
    args = parser.parse_args()

    if args.db_path:
        os.environ["BENCH_DB_PATH"] = args.db_path

    if not args.no_browser:
        import threading
        threading.Timer(1.5, lambda: webbrowser.open(f"http://{args.host}:{args.port}")).start()

    uvicorn.run(
        "bench_sales_agent.web.app:create_app",
        factory=True,
        host=args.host,
        port=args.port,
        reload=False,
    )


if __name__ == "__main__":
    main()
