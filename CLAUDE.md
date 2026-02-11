# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Bench Sales Agent — an AI-powered CLI tool for IT staffing bench sales operations. Finds US contract roles for IT consultants currently on bench (out of project). Built with 15 years of bench sales recruiter expertise encoded into search strategies, rate benchmarks, and placement workflows.

## Commands

```bash
# Setup
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# Run the agent
bench-agent
# or: python3 -m bench_sales_agent.cli

# Tests
pytest tests/ -v

# Lint
ruff check src/ tests/
ruff check src/ tests/ --fix   # auto-fix

# Single test
pytest tests/test_xray_engine.py::test_generate_all_queries_returns_results -v
```

## Architecture

```
src/bench_sales_agent/
├── agent.py              # Core AI agent - Claude-powered bench sales brain
│                          # Contains the master system prompt with recruiter expertise
│                          # Orchestrates analysis, matching, email generation
├── cli.py                # Rich-powered interactive CLI (main entry point)
│                          # Menu-driven: consultants, search, jobs, vendors, submissions
├── search/
│   ├── xray_engine.py    # X-ray search query builder (the core differentiator)
│   │                      # Generates Google dork queries for LinkedIn, Dice, Indeed,
│   │                      # Monster, CareerBuilder, ZipRecruiter, TechFetch, C2C boards
│   │                      # Categories: job_search, vendor_hunt, contact_find
│   ├── web_search.py     # Async search execution (SerpAPI / Google API / scrape fallback)
│   └── job_board_urls.py # Direct native URL builders for each job board
├── models/
│   ├── consultant.py     # ConsultantProfile with visa, skills, rates, bench tracking
│   ├── job.py            # JobRequirement + Submission tracking with match scoring
│   └── vendor.py         # Vendor/prime vendor with tier system and reliability scoring
├── data/
│   └── database.py       # TinyDB-based local JSON storage for all entities
└── templates/
    └── emails.py         # Submission, hotlist, follow-up, and vendor intro email generators
```

## Key Design Decisions

- **Offline-capable**: X-ray query generation, job board URLs, email templates, and data management all work without an API key. Only AI chat/analysis features need `ANTHROPIC_API_KEY`.
- **TinyDB for storage**: No external database needed. Data stored in `data/bench_sales.json`.
- **Search strategy**: `XRaySearchEngine` generates 20+ Google dork queries per consultant, targeting job postings, vendor contacts, hotlists, VMS/MSP programs, and C2C-specific boards.
- **Three search backends**: `WebSearchClient` supports SerpAPI (production), Google Custom Search API, and direct scraping (development).
- **Pydantic models throughout**: All data models use Pydantic v2 for validation and serialization.

## Domain Concepts

- **Bench**: Consultant not currently on a project, available for placement
- **C2C (Corp-to-Corp)**: Business-to-business contract arrangement between staffing companies
- **X-ray search**: Using Google's `site:` operator to search within platforms (LinkedIn, Dice, etc.) bypassing their native search limitations
- **Hotlist**: Email blast listing available consultants sent to vendor networks
- **Prime vendor**: Direct vendor relationship with the end client
- **VMS/MSP**: Vendor Management System / Managed Service Provider (Fieldglass, Beeline)
- **Bill rate vs pay rate**: Client pays bill rate to vendor; vendor pays consultant the pay rate

## Environment Variables

- `ANTHROPIC_API_KEY` — Required for AI features (chat, analysis, smart emails)
- `SERPAPI_KEY` — Optional, for production web search
- `GOOGLE_CSE_ID` + `GOOGLE_API_KEY` — Optional, for Google Custom Search
