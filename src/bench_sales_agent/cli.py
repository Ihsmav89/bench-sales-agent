"""
Interactive CLI for the Bench Sales Agent.

Rich-powered terminal interface with menus, tables, and formatted output.
"""

from __future__ import annotations

import sys
from collections.abc import Callable
from datetime import date
from typing import Any

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Confirm, FloatPrompt, IntPrompt, Prompt
from rich.table import Table
from rich.text import Text

from .agent import BenchSalesAgent
from .data.database import Database
from .models.consultant import ConsultantProfile, EmploymentType, VisaStatus
from .models.job import JobRequirement
from .models.vendor import Vendor, VendorTier
from .search.job_board_urls import JobBoardURLBuilder
from .search.xray_engine import ConsultantSearchParams, XRaySearchEngine
from .templates.emails import EmailTemplates

console = Console()


# ── Shared Helpers ──────────────────────────────────────────────────────


def parse_csv(raw: str) -> list[str]:
    """Split comma-separated string into stripped, non-empty items."""
    return [s.strip() for s in raw.split(",") if s.strip()]


def run_menu(
    title: str, items: list[tuple[str, Callable[[], None]]], *, exit_label: str = "Back",
) -> None:
    """Run an interactive menu loop. Items are (label, handler) tuples, numbered 1..N."""
    choices = [str(i) for i in range(len(items) + 1)]
    while True:
        console.print(f"\n[bold]{title}[/bold]")
        for i, (label, _) in enumerate(items, 1):
            console.print(f"  [cyan]{i}[/cyan]  {label}")
        console.print(f"  [cyan]0[/cyan]  {exit_label}")

        choice = Prompt.ask("Select", choices=choices)
        if choice == "0":
            break
        items[int(choice) - 1][1]()


def prompt_select(
    items: list,
    list_fn: Callable[[], None],
    get_fn: Callable[[str], Any | None],
    *,
    label: str = "ID",
    empty_msg: str = "No items found.",
) -> Any | None:
    """List entities, prompt for ID, fetch and return. Returns None on empty list or not found."""
    if not items:
        console.print(f"[yellow]{empty_msg}[/yellow]")
        return None
    list_fn()
    eid = Prompt.ask(label)
    entity = get_fn(eid)
    if entity is None:
        console.print("[red]Not found.[/red]")
    return entity


def show_email_panel(email: dict, title: str) -> None:
    """Display a generated email in a Rich panel."""
    console.print(Panel(
        f"[bold]Subject:[/bold] {email['subject']}\n\n{email['body']}",
        title=title, border_style="green",
    ))


def banner():
    console.print(Panel.fit(
        "[bold cyan]BENCH SALES AGENT[/bold cyan]\n"
        "[dim]AI-Powered IT Staffing & Contract Role Search Engine[/dim]\n"
        "[dim]15 Years of Bench Sales Expertise Built In[/dim]",
        border_style="cyan",
    ))


# ── Consultant Management ────────────────────────────────────────────────


def add_consultant_interactive(db: Database):
    console.print("\n[bold]Add New Bench Consultant[/bold]\n")

    name = Prompt.ask("Full Name")
    email = Prompt.ask("Email")
    phone = Prompt.ask("Phone")
    location = Prompt.ask("Current Location (City, ST)", default="")
    job_title = Prompt.ask("Job Title (e.g., Java Developer)")

    primary_skills = parse_csv(Prompt.ask("Primary Skills (comma-separated)"))
    secondary_skills = parse_csv(
        Prompt.ask("Secondary Skills (comma-separated, optional)", default=""),
    )

    exp = FloatPrompt.ask("Total Experience (years)")
    us_exp = FloatPrompt.ask("US Experience (years)", default=0)

    console.print("\nVisa Status Options:")
    for i, vs in enumerate(VisaStatus, 1):
        console.print(f"  {i}. {vs.value}")
    visa_idx = IntPrompt.ask("Select visa status", default=1)
    visa = list(VisaStatus)[max(0, visa_idx - 1)]

    remote = Prompt.ask("Work Preference", choices=["Remote", "Hybrid", "Onsite"], default="Remote")
    relocation = Confirm.ask("Open to relocation?", default=False)

    rate = FloatPrompt.ask("Expected Rate ($/hr)", default=0)
    min_rate = FloatPrompt.ask("Minimum Rate ($/hr)", default=0)

    consultant = ConsultantProfile(
        full_name=name,
        email=email,
        phone=phone,
        current_location=location,
        job_title=job_title,
        primary_skills=primary_skills,
        secondary_skills=secondary_skills,
        total_experience_years=exp,
        us_experience_years=us_exp,
        visa_status=visa,
        remote_preference=remote,
        relocation=relocation,
        expected_rate_hourly=rate if rate > 0 else None,
        minimum_rate_hourly=min_rate if min_rate > 0 else None,
        bench_since=date.today(),
        employment_types_accepted=[EmploymentType.W2, EmploymentType.C2C],
    )

    cid = db.add_consultant(consultant)
    console.print(f"\n[green]Consultant added successfully! ID: {cid}[/green]")
    console.print(f"[dim]{consultant.one_liner()}[/dim]")
    return cid


def list_consultants(db: Database):
    consultants = db.list_consultants()
    if not consultants:
        console.print("[yellow]No consultants in database.[/yellow]")
        return

    table = Table(title="Bench Consultants")
    table.add_column("ID", style="cyan")
    table.add_column("Name")
    table.add_column("Title")
    table.add_column("Skills")
    table.add_column("Visa")
    table.add_column("Location")
    table.add_column("Rate")
    table.add_column("Bench Days", justify="right")

    for c in consultants:
        table.add_row(
            c.id or "",
            c.full_name,
            c.job_title,
            ", ".join(c.primary_skills[:3]),
            c.visa_status.value,
            c.current_location,
            c.rate_display(),
            str(c.bench_duration_days()),
        )

    console.print(table)


def _ai_profile_analysis(db: Database, agent: BenchSalesAgent):
    c = prompt_select(
        db.list_consultants(), lambda: list_consultants(db),
        db.get_consultant, label="Enter Consultant ID to analyze",
        empty_msg="No consultants. Add one first.",
    )
    if not c:
        return
    with console.status("AI analyzing profile..."):
        analysis = agent.analyze_consultant(c)
    console.print(Panel(Markdown(analysis), title="Profile Analysis", border_style="green"))


def consultant_menu(db: Database, agent: BenchSalesAgent):
    run_menu("Consultant Management", [
        ("Add Consultant", lambda: add_consultant_interactive(db)),
        ("List All Consultants", lambda: list_consultants(db)),
        ("AI Profile Analysis", lambda: _ai_profile_analysis(db, agent)),
    ])


# ── Search for Roles ─────────────────────────────────────────────────────


def _search_by_consultant(db: Database, agent: BenchSalesAgent):
    c = prompt_select(
        db.list_consultants(), lambda: list_consultants(db),
        db.get_consultant, label="Enter Consultant ID",
        empty_msg="No consultants. Add one first.",
    )
    if not c:
        return

    with console.status("Generating comprehensive search strategy..."):
        strategy = agent.generate_search_strategy(c)

    queries = strategy["xray_queries"]
    _display_queries(queries, f"X-Ray Search Queries for {c.full_name}")

    hotlist_queries = strategy["hotlist_queries"]
    if hotlist_queries:
        _display_queries(hotlist_queries, "Hotlist/Requirement List Queries")

    _display_board_links(strategy["board_links"])

    synonyms = strategy["role_synonyms"]
    if len(synonyms) > 1:
        console.print(f"\n[bold]Also search for:[/bold] {', '.join(synonyms[1:])}")


def _custom_search(agent: BenchSalesAgent):
    title = Prompt.ask("Job Title")
    skills = parse_csv(Prompt.ask("Skills (comma-separated)"))
    location = Prompt.ask("Location (City, ST)", default="")

    params = ConsultantSearchParams(
        job_title=title,
        primary_skills=skills,
        location=location,
        remote_ok=True,
    )

    engine = XRaySearchEngine()
    queries = engine.generate_all_queries(params)
    _display_queries(queries, f"X-Ray Queries: {title}")

    board_links = JobBoardURLBuilder.all_boards(title, location)
    _display_board_links(board_links)


def _xray_queries_only():
    title = Prompt.ask("Job Title")
    skills = parse_csv(Prompt.ask("Top Skills (comma-separated)"))
    location = Prompt.ask("Location (optional)", default="")

    params = ConsultantSearchParams(
        job_title=title,
        primary_skills=skills,
        location=location,
    )

    engine = XRaySearchEngine()
    queries = engine.generate_all_queries(params)
    hotlist = engine.generate_hotlist_queries(params)

    _display_queries(queries + hotlist, f"All X-Ray Queries: {title}")


def _job_board_links():
    title = Prompt.ask("Job Title")
    location = Prompt.ask("Location (optional)", default="")
    links = JobBoardURLBuilder.all_boards(title, location)
    _display_board_links(links)


def _display_queries(queries, title):
    categories = {}
    for q in queries:
        cat = q.category or "general"
        categories.setdefault(cat, []).append(q)

    for cat, cat_queries in categories.items():
        table = Table(title=f"{title} - {cat.replace('_', ' ').title()}")
        table.add_column("#", style="cyan", width=3)
        table.add_column("Platform", style="yellow", width=12)
        table.add_column("Description")
        table.add_column("Priority", justify="center", width=8)

        cat_queries.sort(key=lambda x: x.priority)
        for i, q in enumerate(cat_queries, 1):
            prio_style = "bold red" if q.priority == 1 else "yellow" if q.priority == 2 else "dim"
            table.add_row(
                str(i),
                q.platform.value,
                q.description,
                Text(f"P{q.priority}", style=prio_style),
            )

        console.print(table)

    if Confirm.ask("\nShow raw search queries?", default=False):
        for i, q in enumerate(queries, 1):
            console.print(f"\n[cyan]#{i}[/cyan] [{q.platform.value}] {q.description}")
            console.print(f"  [dim]Query:[/dim] {q.query}")
            console.print(f"  [dim]URL:[/dim] {q.search_url}")


def _display_board_links(links):
    table = Table(title="Direct Job Board Links")
    table.add_column("Platform", style="yellow")
    table.add_column("Description")
    table.add_column("URL", style="dim")

    for link in links:
        table.add_row(link.platform, link.description, link.url[:80] + "...")

    console.print(table)


def search_menu(db: Database, agent: BenchSalesAgent):
    run_menu("Search for Contract Roles", [
        ("Search by Consultant Profile", lambda: _search_by_consultant(db, agent)),
        ("Custom Search (Title + Skills + Location)", lambda: _custom_search(agent)),
        ("Generate X-Ray Queries Only", _xray_queries_only),
        ("Job Board Direct Links", _job_board_links),
    ])


# ── Job Requirements ─────────────────────────────────────────────────────


def _add_job_interactive(db: Database):
    console.print("\n[bold]Add New Job Requirement[/bold]\n")

    title = Prompt.ask("Job Title")
    client = Prompt.ask("Client Name (if known)", default="")
    vendor = Prompt.ask("Vendor Name")
    vendor_email = Prompt.ask("Vendor Contact Email", default="")
    description = Prompt.ask("Brief Description", default="")

    required_skills = parse_csv(Prompt.ask("Required Skills (comma-separated)"))

    location = Prompt.ask("Location", default="Remote")
    remote = Prompt.ask("Work Mode", choices=["Remote", "Hybrid", "Onsite"], default="Remote")
    duration = IntPrompt.ask("Duration (months)", default=12)
    rate = FloatPrompt.ask("Bill Rate ($/hr, 0 if unknown)", default=0)

    emp_type = Prompt.ask("Employment Type", choices=["C2C", "W2", "C2C/W2", "1099"], default="C2C")
    source = Prompt.ask("Source (dice, indeed, linkedin, email, etc.)", default="email")

    job = JobRequirement(
        title=title,
        client_name=client or None,
        vendor_name=vendor,
        vendor_contact_email=vendor_email or None,
        description=description,
        required_skills=required_skills,
        location=location,
        remote_option=remote,
        duration_months=duration,
        bill_rate=rate if rate > 0 else None,
        employment_type=emp_type,
        source_platform=source,
        posted_date=date.today(),
    )

    jid = db.add_job(job)
    console.print(f"\n[green]Job added! ID: {jid}[/green]")


def _list_jobs(db: Database):
    jobs = db.list_jobs()
    if not jobs:
        console.print("[yellow]No active jobs.[/yellow]")
        return

    table = Table(title="Active Job Requirements")
    table.add_column("ID", style="cyan")
    table.add_column("Title")
    table.add_column("Vendor")
    table.add_column("Skills")
    table.add_column("Location")
    table.add_column("Rate")
    table.add_column("Type")

    for j in jobs:
        table.add_row(
            j.id or "",
            j.title,
            j.vendor_name or "",
            ", ".join(j.required_skills[:3]),
            j.location,
            f"${j.bill_rate:.0f}/hr" if j.bill_rate else "N/A",
            j.employment_type,
        )
    console.print(table)


def _match_consultant_to_jobs(db: Database):
    c = prompt_select(
        db.list_consultants(), lambda: list_consultants(db),
        db.get_consultant, label="Consultant ID to match",
        empty_msg="No consultants.",
    )
    if not c:
        return

    jobs = db.list_jobs()
    if not jobs:
        console.print("[yellow]No jobs to match against.[/yellow]")
        return

    matches = []
    for j in jobs:
        score = j.match_score(c.primary_skills + c.secondary_skills)
        matches.append((j, score))

    matches.sort(key=lambda x: x[1], reverse=True)

    table = Table(title=f"Job Matches for {c.full_name}")
    table.add_column("ID", style="cyan")
    table.add_column("Title")
    table.add_column("Match %", justify="right")
    table.add_column("Vendor")
    table.add_column("Location")

    for j, score in matches[:15]:
        score_style = "bold green" if score >= 70 else "yellow" if score >= 40 else "red"
        table.add_row(
            j.id or "",
            j.title,
            Text(f"{score:.0f}%", style=score_style),
            j.vendor_name or "",
            j.location,
        )
    console.print(table)


def job_menu(db: Database):
    run_menu("Job Requirements", [
        ("Add Job Requirement", lambda: _add_job_interactive(db)),
        ("List Active Jobs", lambda: _list_jobs(db)),
        ("Match Consultant to Jobs", lambda: _match_consultant_to_jobs(db)),
    ])


# ── Vendor Management ────────────────────────────────────────────────────


def _add_vendor_interactive(db: Database):
    console.print("\n[bold]Add New Vendor[/bold]\n")
    name = Prompt.ask("Company Name")
    contact_name = Prompt.ask("Primary Contact Name", default="")
    contact_email = Prompt.ask("Contact Email", default="")
    contact_phone = Prompt.ask("Contact Phone", default="")

    console.print("Tier: 1=Direct Client, 2=Prime Vendor, 3=Tier-1, 4=Tier-2")
    tier_idx = IntPrompt.ask("Tier", default=3)
    tiers = list(VendorTier)
    tier = tiers[min(tier_idx - 1, len(tiers) - 1)]

    vendor = Vendor(
        company_name=name,
        primary_contact_name=contact_name or None,
        primary_contact_email=contact_email or None,
        primary_contact_phone=contact_phone or None,
        tier=tier,
    )

    vid = db.add_vendor(vendor)
    console.print(f"\n[green]Vendor added! ID: {vid}[/green]")


def _list_vendors(db: Database):
    vendors = db.list_vendors()
    if not vendors:
        console.print("[yellow]No vendors.[/yellow]")
        return

    table = Table(title="Vendors")
    table.add_column("ID", style="cyan")
    table.add_column("Company")
    table.add_column("Tier")
    table.add_column("Contact")
    table.add_column("Email")
    table.add_column("Submissions", justify="right")
    table.add_column("Placements", justify="right")

    for v in vendors:
        table.add_row(
            v.id or "",
            v.company_name,
            v.tier.value,
            v.primary_contact_name or "",
            v.primary_contact_email or "",
            str(v.total_submissions),
            str(v.total_placements),
        )
    console.print(table)


def vendor_menu(db: Database):
    run_menu("Vendor Management", [
        ("Add Vendor", lambda: _add_vendor_interactive(db)),
        ("List Vendors", lambda: _list_vendors(db)),
    ])


# ── Submissions ──────────────────────────────────────────────────────────


def _pending_followups(db: Database):
    subs = db.list_pending_followups()
    if not subs:
        console.print("[green]No pending follow-ups.[/green]")
        return

    table = Table(title="Pending Follow-ups")
    table.add_column("ID", style="cyan")
    table.add_column("Consultant")
    table.add_column("Job")
    table.add_column("Vendor")
    table.add_column("Status")
    table.add_column("Follow-ups", justify="right")

    for s in subs:
        table.add_row(
            s.id or "",
            s.consultant_id,
            s.job_id,
            s.vendor_name,
            s.status.value,
            str(s.followup_count),
        )
    console.print(table)


def _submissions_by_consultant(db: Database):
    list_consultants(db)
    cid = Prompt.ask("Consultant ID")
    subs = db.get_submissions_for_consultant(cid)
    if not subs:
        console.print("[yellow]No submissions for this consultant.[/yellow]")
        return

    table = Table(title=f"Submissions for {cid}")
    table.add_column("ID", style="cyan")
    table.add_column("Job")
    table.add_column("Vendor")
    table.add_column("Status")
    table.add_column("Rate")
    table.add_column("Submitted")

    for s in subs:
        table.add_row(
            s.id or "",
            s.job_id,
            s.vendor_name,
            s.status.value,
            f"${s.rate_submitted:.0f}" if s.rate_submitted else "",
            str(s.submitted_at.date()) if s.submitted_at else "",
        )
    console.print(table)


def submission_menu(db: Database):
    run_menu("Submissions & Follow-ups", [
        ("View Pending Follow-ups", lambda: _pending_followups(db)),
        ("View Submissions by Consultant", lambda: _submissions_by_consultant(db)),
    ])


# ── Email Generation ─────────────────────────────────────────────────────


def _generate_hotlist(db: Database):
    consultants = db.list_consultants()
    if not consultants:
        console.print("[yellow]No consultants.[/yellow]")
        return

    email = EmailTemplates.hotlist_email(consultants)
    show_email_panel(email, "Hotlist Email")


def _generate_submission_email(db: Database):
    c = prompt_select(
        db.list_consultants(), lambda: list_consultants(db),
        db.get_consultant, label="Consultant ID",
        empty_msg="No consultants.",
    )
    if not c:
        return

    j = prompt_select(
        db.list_jobs(), lambda: _list_jobs(db),
        db.get_job, label="Job ID",
        empty_msg="No active jobs.",
    )
    if not j:
        return

    email = EmailTemplates.submission_email(c, j)
    show_email_panel(email, "Submission Email")


def _ai_submission_email(db: Database, agent: BenchSalesAgent):
    c = prompt_select(
        db.list_consultants(), lambda: list_consultants(db),
        db.get_consultant, label="Consultant ID",
        empty_msg="No consultants.",
    )
    if not c:
        return

    j = prompt_select(
        db.list_jobs(), lambda: _list_jobs(db),
        db.get_job, label="Job ID",
        empty_msg="No active jobs.",
    )
    if not j:
        return

    with console.status("AI crafting submission email..."):
        result = agent.craft_submission_email(c, j)
    console.print(Panel(Markdown(result), title="AI-Crafted Submission", border_style="green"))


def _vendor_intro_email():
    skills = parse_csv(Prompt.ask("Your specializations (comma-separated)"))
    email = EmailTemplates.vendor_introduction_email(skills)
    show_email_panel(email, "Vendor Introduction")


def email_menu(db: Database, agent: BenchSalesAgent):
    run_menu("Email & Hotlist Generation", [
        ("Generate Hotlist Email", lambda: _generate_hotlist(db)),
        ("Generate Submission Email", lambda: _generate_submission_email(db)),
        ("AI-Crafted Submission Email", lambda: _ai_submission_email(db, agent)),
        ("Vendor Introduction Email", _vendor_intro_email),
    ])


# ── AI Chat ──────────────────────────────────────────────────────────────


def ai_chat(agent: BenchSalesAgent, db: Database):
    console.print("\n[bold]AI Bench Sales Chat[/bold]")
    console.print("[dim]Ask anything about bench sales, market rates, strategies, etc.[/dim]")
    console.print("[dim]Type 'exit' to go back.[/dim]\n")

    stats = db.get_stats()
    context = {"database_stats": stats}

    while True:
        user_input = Prompt.ask("[bold cyan]You[/bold cyan]")
        if user_input.lower() in ("exit", "quit", "back"):
            break

        with console.status("Thinking..."):
            response = agent.chat(user_input, context=context)

        console.print("\n[bold green]Agent:[/bold green]")
        console.print(Panel(Markdown(response), border_style="green"))


# ── Market Analysis ──────────────────────────────────────────────────────


def market_analysis(agent: BenchSalesAgent):
    console.print("\n[bold]Market Rate Analysis[/bold]\n")
    title = Prompt.ask("Job Title")
    location = Prompt.ask("Location", default="Remote / US")
    skills = parse_csv(Prompt.ask("Key Skills (comma-separated)"))

    with console.status("Analyzing market rates..."):
        analysis = agent.market_rate_analysis(title, location, skills)
    console.print(Panel(Markdown(analysis), title="Market Rate Analysis", border_style="green"))


# ── Dashboard ────────────────────────────────────────────────────────────


def dashboard(db: Database):
    stats = db.get_stats()

    table = Table(title="Bench Sales Dashboard")
    table.add_column("Metric", style="bold")
    table.add_column("Count", justify="right", style="cyan")

    table.add_row("Consultants on Bench", str(stats["consultants_on_bench"]))
    table.add_row("Total Consultants", str(stats["total_consultants"]))
    table.add_row("Active Job Requirements", str(stats["active_jobs"]))
    table.add_row("Total Jobs Tracked", str(stats["total_jobs"]))
    table.add_row("Vendors in Database", str(stats["total_vendors"]))
    table.add_row("Active Submissions", str(stats["active_submissions"]))
    table.add_row("Total Submissions", str(stats["total_submissions"]))

    console.print(table)


# ── Main Entry Point ─────────────────────────────────────────────────────


@click.command()
@click.option("--db-path", default=None, help="Path to database file")
def main(db_path: str | None):
    """Bench Sales Agent - AI-powered IT staffing assistant."""
    db = Database(db_path)
    agent = BenchSalesAgent()

    banner()

    if not agent.is_configured:
        console.print(
            "[yellow]Note: ANTHROPIC_API_KEY not set. AI features (chat, analysis, "
            "smart emails) are limited. Search queries and templates work without it.[/yellow]\n"
        )

    menu_items = [
        ("Manage Bench Consultants", lambda: consultant_menu(db, agent)),
        ("Search for Contract Roles", lambda: search_menu(db, agent)),
        ("Manage Job Requirements", lambda: job_menu(db)),
        ("Manage Vendors", lambda: vendor_menu(db)),
        ("Submissions & Follow-ups", lambda: submission_menu(db)),
        ("Generate Emails & Hotlists", lambda: email_menu(db, agent)),
        ("AI Chat (Ask the Agent)", lambda: ai_chat(agent, db)),
        ("Market Rate Analysis", lambda: market_analysis(agent)),
        ("Dashboard / Stats", lambda: dashboard(db)),
    ]
    choices = [str(i) for i in range(len(menu_items) + 1)]

    while True:
        try:
            console.print("\n[bold]Main Menu[/bold]")
            for i, (label, _) in enumerate(menu_items, 1):
                console.print(f"  [cyan]{i}[/cyan]  {label}")
            console.print("  [cyan]0[/cyan]  Exit")

            choice = Prompt.ask("\nSelect", choices=choices)
            if choice == "0":
                console.print("[bold]Goodbye![/bold]")
                sys.exit(0)
            menu_items[int(choice) - 1][1]()

        except KeyboardInterrupt:
            console.print("\n[bold]Goodbye![/bold]")
            sys.exit(0)
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")


if __name__ == "__main__":
    main()
