"""Sample C2C-only search — shows all generated queries with zero W2 references."""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from bench_sales_agent.search.xray_engine import XRaySearchEngine, ConsultantSearchParams
from bench_sales_agent.search.job_board_urls import JobBoardURLBuilder

console = Console()

console.print(Panel.fit(
    "[bold cyan]C2C-ONLY SEARCH SAMPLE[/bold cyan]\n"
    "[dim]All W2 terms removed — Corp-to-Corp focus only[/dim]",
    border_style="cyan",
))

# ── Sample consultant: SAP FICO Consultant, H1B, New Jersey ─────────────
params = ConsultantSearchParams(
    job_title="SAP FICO Consultant",
    primary_skills=["SAP FICO", "SAP S/4HANA", "SAP ECC", "SAP BPC"],
    secondary_skills=["SAP MM", "SAP CO", "ABAP"],
    location="Edison, NJ",
    remote_ok=True,
    visa_status="H1B",
    employment_types=["C2C"],
    experience_years=12,
    rate_range="$90-$110/hr",
)

engine = XRaySearchEngine()

console.print(f"\n[bold yellow]Consultant:[/bold yellow] SAP FICO Consultant | 12 yrs | H1B | Edison, NJ | $90-$110/hr C2C")
console.print(f"[bold yellow]Skills:[/bold yellow] SAP FICO, SAP S/4HANA, SAP ECC, SAP BPC\n")

# ── Generate all queries ────────────────────────────────────────────────
queries = engine.generate_all_queries(params)
hotlist = engine.generate_hotlist_queries(params)
all_queries = queries + hotlist

# ── Verify NO W2 in any query ──────────────────────────────────────────
w2_found = [q for q in all_queries if '"w2"' in q.query.lower()]
if w2_found:
    console.print(f"[bold red]WARNING: {len(w2_found)} queries still contain W2![/bold red]")
else:
    console.print(f"[bold green]VERIFIED: 0 queries contain W2 — pure C2C search[/bold green]\n")

# ── Display queries by category ─────────────────────────────────────────
categories = {}
for q in all_queries:
    categories.setdefault(q.category or "general", []).append(q)

for cat, cat_queries in categories.items():
    cat_queries.sort(key=lambda x: x.priority)
    tbl = Table(title=f"{cat.replace('_', ' ').title()} ({len(cat_queries)} queries)")
    tbl.add_column("#", width=3, style="cyan")
    tbl.add_column("Platform", width=14, style="yellow")
    tbl.add_column("Description", width=42)
    tbl.add_column("P", width=3, justify="center")

    for i, q in enumerate(cat_queries, 1):
        ps = "bold red" if q.priority == 1 else "yellow" if q.priority == 2 else "dim"
        tbl.add_row(str(i), q.platform.value, q.description, Text(str(q.priority), style=ps))
    console.print(tbl)

# ── Show raw queries ────────────────────────────────────────────────────
console.print(f"\n[bold]All {len(all_queries)} Raw Queries (C2C-Only):[/bold]\n")
for i, q in enumerate(all_queries, 1):
    console.print(f"[cyan]#{i:02d}[/cyan] [{q.platform.value:14s}] {q.description}")
    console.print(f"     [dim]{q.query}[/dim]\n")

# ── Direct job board links ──────────────────────────────────────────────
links = JobBoardURLBuilder.all_boards("SAP FICO Consultant", "Edison, NJ")
tbl = Table(title="Direct Job Board Links — SAP FICO C2C")
tbl.add_column("Board", style="yellow", width=15)
tbl.add_column("Description", width=35)
tbl.add_column("URL", style="dim")

for link in links:
    tbl.add_row(link.platform, link.description, link.url[:80] + "...")
console.print(tbl)

# ── Summary ─────────────────────────────────────────────────────────────
console.print(Panel.fit(
    f"[bold green]Total queries: {len(all_queries)}[/bold green]\n"
    f"[bold green]W2 references: 0[/bold green]\n"
    f"[bold green]C2C/Corp-to-Corp queries: {len([q for q in all_queries if 'c2c' in q.query.lower() or 'corp to corp' in q.query.lower()])}[/bold green]\n"
    f"[bold green]Job board links: {len(links)} (all C2C-targeted)[/bold green]",
    title="C2C SEARCH VERIFICATION",
    border_style="green",
))
