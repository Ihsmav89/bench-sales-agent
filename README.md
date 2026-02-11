# Bench Sales Agent

AI-powered bench sales recruiter for finding C2C contract roles across US job boards. Generates 21+ X-ray search queries per consultant, manages vendors, tracks submissions, and crafts professional emails — with 15 years of bench sales expertise built in.

## Features

- **X-Ray Search Engine** — Generates Google dork queries across LinkedIn, Dice, Indeed, Monster, ZipRecruiter, CareerBuilder, Glassdoor, TechFetch, C2C boards, VMS/MSP platforms, and Google Groups
- **Web UI** — Dark-themed dashboard with FastAPI + HTMX + Tailwind CSS (no JS build step)
- **CLI** — Rich-powered interactive terminal interface
- **AI Chat** — Claude-powered bench sales expert for strategy, rate analysis, and placement advice
- **Consultant Management** — Track bench consultants with skills, visa status, rates, and bench duration
- **Job Matching** — Skill-based matching with percentage scores
- **Email Generation** — Hotlist emails, submission emails, vendor introductions, and AI-crafted submissions
- **Market Rate Benchmarks** — Built-in C2C rate data for 12+ technology categories
- **C2C-Only Search** — All queries target Corp-to-Corp/contract roles (no W2)
- **Offline-Capable** — Search queries, board links, email templates, and data management work without an API key

## Quick Start

```bash
# Clone and install
git clone https://github.com/Ihsmav89/bench-sales-agent.git
cd bench-sales-agent
python3 -m venv .venv && source .venv/bin/activate
pip install -e .

# Launch Web UI (opens browser)
bench-agent-web

# Or launch CLI
bench-agent
```

Optional: Set your Anthropic API key for AI features (chat, analysis, smart emails):

```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

## Web UI

The web interface runs at `http://localhost:8000` with 9 pages:

| Page | Description |
|------|-------------|
| **Dashboard** | Stats overview, quick actions |
| **Consultants** | Add/view bench consultants, AI profile analysis |
| **Search Roles** | Generate X-ray queries by consultant or custom search |
| **Job Requirements** | Track jobs, match consultants to openings |
| **Vendors** | Manage vendor relationships and tiers |
| **Submissions** | Track submissions and follow-ups |
| **Emails** | Generate hotlists, submission emails, AI-crafted emails |
| **AI Chat** | Ask the bench sales expert anything |
| **Market Rates** | C2C rate benchmarks and AI-powered analysis |

## Search Engine

The X-ray search engine generates 21+ queries per consultant across multiple categories:

**Job Search** — LinkedIn Jobs, LinkedIn Posts, Dice, Indeed, direct client career sites, C2C-specific boards, Monster, ZipRecruiter, TechFetch, CareerBuilder, government contracts, VMS/MSP programs, mailing lists

**Contact Find** — LinkedIn recruiter profiles, recruiter email harvesting

**Vendor Hunt** — Vendor requirement emails, staffing company search, LinkedIn vendor companies

Each query includes a clickable Google search URL. Direct job board links are also generated for all 8 supported platforms.

## Deployment

### Docker

```bash
docker compose up
# Runs at http://localhost:8000
```

### pip install

```bash
pip install .
bench-agent-web              # Web UI
bench-agent                  # CLI
```

### Install Scripts

```bash
# macOS
bash scripts/install-macos.sh

# Windows
scripts\install-windows.bat
```

### PyInstaller (Standalone Binary)

```bash
pip install pyinstaller
pyinstaller bench-agent.spec
# Output: dist/bench-agent-web
```

## Project Structure

```
src/bench_sales_agent/
├── agent.py                 # Claude-powered AI agent with recruiter expertise
├── cli.py                   # Rich terminal interface
├── web/
│   ├── app.py               # FastAPI application
│   ├── routes/              # 9 route modules (dashboard, consultants, search, etc.)
│   └── templates/           # Jinja2 + HTMX templates
├── search/
│   ├── xray_engine.py       # X-ray search query generator (core engine)
│   ├── web_search.py        # Async search execution (SerpAPI / Google / scrape)
│   └── job_board_urls.py    # Direct URL builders for 8 job boards
├── models/                  # Pydantic v2 models (consultant, job, vendor)
├── data/database.py         # TinyDB local JSON storage
└── templates/emails.py      # Email template generators
```

## Tech Stack

- **Backend**: FastAPI, Uvicorn, Pydantic v2
- **Frontend**: Jinja2, HTMX, Tailwind CSS (CDN)
- **AI**: Anthropic Claude API
- **Database**: TinyDB (local JSON, no server needed)
- **CLI**: Click, Rich
- **Search**: Google dork queries, 8 job board URL builders

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests (18 tests)
pytest tests/ -v

# Lint
ruff check src/ tests/

# Run single test
pytest tests/test_xray_engine.py::test_queries_are_c2c_only_no_w2 -v
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | For AI features | Claude API key for chat, analysis, smart emails |
| `SERPAPI_KEY` | Optional | SerpAPI key for production web search |
| `GOOGLE_CSE_ID` | Optional | Google Custom Search Engine ID |
| `GOOGLE_API_KEY` | Optional | Google API key for Custom Search |

## License

MIT
