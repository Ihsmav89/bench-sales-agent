"""
Interactive CLI for the Bench Sales Agent.

Rich-powered terminal interface with menus, tables, and formatted output.
"""

from __future__ import annotations

import sys
from datetime import date

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


def banner():
    console.print(Panel.fit(
        "[bold cyan]BENCH SALES AGENT[/bold cyan]\n"
        "[dim]AI-Powered IT Staffing & Contract Role Search Engine[/dim]\n"
        "[dim]15 Years of Bench Sales Expertise Built In[/dim]",
        border_style="cyan",
    ))


def show_main_menu():
    console.print("\n[bold]Main Menu[/bold]")
    console.print("  [cyan]1[/cyan]  Manage Bench Consultants")
    console.print("  [cyan]2[/cyan]  Search for Contract Roles")
    console.print("  [cyan]3[/cyan]  Manage Job Requirements")
    console.print("  [cyan]4[/cyan]  Manage Vendors")
    console.print("  [cyan]5[/cyan]  Submissions & Follow-ups")
    console.print("  [cyan]6[/cyan]  Generate Emails & Hotlists")
    console.print("  [cyan]7[/cyan]  AI Chat (Ask the Agent)")
    console.print("  [cyan]8[/cyan]  Market Rate Analysis")
    console.print("  [cyan]9[/cyan]  Dashboard / Stats")
    console.print("  [cyan]0[/cyan]  Exit")
    return Prompt.ask("\nSelect", choices=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"])


# ── Consultant Management ────────────────────────────────────────────────


def add_consultant_interactive(db: Database):
    console.print("\n[bold]Add New Bench Consultant[/bold]\n")

    name = Prompt.ask("Full Name")
    email = Prompt.ask("Email")
    phone = Prompt.ask("Phone")
    location = Prompt.ask("Current Location (City, ST)", default="")
    job_title = Prompt.ask("Job Title (e.g., Java Developer)")

    skills_raw = Prompt.ask("Primary Skills (comma-separated)")
    primary_skills = [s.strip() for s in skills_raw.split(",") if s.strip()]

    secondary_raw = Prompt.ask("Secondary Skills (comma-separated, optional)", default="")
    secondary_skills = [s.strip() for s in secondary_raw.split(",") if s.strip()]

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


def consultant_menu(db: Database, agent: BenchSalesAgent):
    while True:
        console.print("\n[bold]Consultant Management[/bold]")
        console.print("  [cyan]1[/cyan]  Add Consultant")
        console.print("  [cyan]2[/cyan]  List All Consultants")
        console.print("  [cyan]3[/cyan]  AI Profile Analysis")
        console.print("  [cyan]0[/cyan]  Back")
        choice = Prompt.ask("Select", choices=["0", "1", "2", "3"])

        if choice == "0":
            break
        elif choice == "1":
            add_consultant_interactive(db)
        elif choice == "2":
            list_consultants(db)
        elif choice == "3":
            consultants = db.list_consultants()
            if not consultants:
                console.print("[yellow]No consultants. Add one first.[/yellow]")
                continue
            list_consultants(db)
            cid = Prompt.ask("Enter Consultant ID to analyze")
            c = db.get_consultant(cid)
            if c:
                with console.status("AI analyzing profile..."):
                    analysis = agent.analyze_consultant(c)
                console.print(Panel(Markdown(analysis), title="Profile Analysis", border_style="green"))
            else:
                console.print("[red]Consultant not found.[/red]")


# ── Search for Roles ─────────────────────────────────────────────────────


def search_menu(db: Database, agent: BenchSalesAgent):
    while True:
        console.print("\n[bold]Search for Contract Roles[/bold]")
        console.print("  [cyan]1[/cyan]  Search by Consultant Profile")
        console.print("  [cyan]2[/cyan]  Custom Search (Title + Skills + Location)")
        console.print("  [cyan]3[/cyan]  Generate X-Ray Queries Only")
        console.print("  [cyan]4[/cyan]  Job Board Direct Links")
        console.print("  [cyan]0[/cyan]  Back")
        choice = Prompt.ask("Select", choices=["0", "1", "2", "3", "4"])

        if choice == "0":
            break
        elif choice == "1":
            _search_by_consultant(db, agent)
        elif choice == "2":
            _custom_search(agent)
        elif choice == "3":
            _xray_queries_only()
        elif choice == "4":
            _job_board_links()


def _search_by_consultant(db: Database, agent: BenchSalesAgent):
    consultants = db.list_consultants()
    if not consultants:
        console.print("[yellow]No consultants. Add one first.[/yellow]")
        return

    list_consultants(db)
    cid = Prompt.ask("Enter Consultant ID")
    c = db.get_consultant(cid)
    if not c:
        console.print("[red]Consultant not found.[/red]")
        return

    with console.status("Generating comprehensive search strategy..."):
        strategy = agent.generate_search_strategy(c)

    # Display X-ray queries grouped by category
    queries = strategy["xray_queries"]
    _display_queries(queries, f"X-Ray Search Queries for {c.full_name}")

    # Display hotlist queries
    hotlist_queries = strategy["hotlist_queries"]
    if hotlist_queries:
        _display_queries(hotlist_queries, "Hotlist/Requirement List Queries")

    # Display board links
    board_links = strategy["board_links"]
    _display_board_links(board_links)

    # Display synonyms
    synonyms = strategy["role_synonyms"]
    if len(synonyms) > 1:
        console.print(f"\n[bold]Also search for:[/bold] {', '.join(synonyms[1:])}")


def _custom_search(agent: BenchSalesAgent):
    title = Prompt.ask("Job Title")
    skills_raw = Prompt.ask("Skills (comma-separated)")
    skills = [s.strip() for s in skills_raw.split(",") if s.strip()]
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
    skills_raw = Prompt.ask("Top Skills (comma-separated)")
    skills = [s.strip() for s in skills_raw.split(",") if s.strip()]
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
    # Group by category
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

        # Sort by priority
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

    # Ask if user wants to see actual queries
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


# ── Job Requirements ─────────────────────────────────────────────────────


def job_menu(db: Database):
    while True:
        console.print("\n[bold]Job Requirements[/bold]")
        console.print("  [cyan]1[/cyan]  Add Job Requirement")
        console.print("  [cyan]2[/cyan]  List Active Jobs")
        console.print("  [cyan]3[/cyan]  Match Consultant to Jobs")
        console.print("  [cyan]0[/cyan]  Back")
        choice = Prompt.ask("Select", choices=["0", "1", "2", "3"])

        if choice == "0":
            break
        elif choice == "1":
            _add_job_interactive(db)
        elif choice == "2":
            _list_jobs(db)
        elif choice == "3":
            _match_consultant_to_jobs(db)


def _add_job_interactive(db: Database):
    console.print("\n[bold]Add New Job Requirement[/bold]\n")

    title = Prompt.ask("Job Title")
    client = Prompt.ask("Client Name (if known)", default="")
    vendor = Prompt.ask("Vendor Name")
    vendor_email = Prompt.ask("Vendor Contact Email", default="")
    description = Prompt.ask("Brief Description", default="")

    skills_raw = Prompt.ask("Required Skills (comma-separated)")
    required_skills = [s.strip() for s in skills_raw.split(",") if s.strip()]

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
    consultants = db.list_consultants()
    if not consultants:
        console.print("[yellow]No consultants.[/yellow]")
        return

    list_consultants(db)
    cid = Prompt.ask("Consultant ID to match")
    c = db.get_consultant(cid)
    if not c:
        console.print("[red]Not found.[/red]")
        return

    jobs = db.list_jobs()
    if not jobs:
        console.print("[yellow]No jobs to match against.[/yellow]")
        return

    # Calculate match scores
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


# ── Vendor Management ────────────────────────────────────────────────────


def vendor_menu(db: Database):
    while True:
        console.print("\n[bold]Vendor Management[/bold]")
        console.print("  [cyan]1[/cyan]  Add Vendor")
        console.print("  [cyan]2[/cyan]  List Vendors")
        console.print("  [cyan]0[/cyan]  Back")
        choice = Prompt.ask("Select", choices=["0", "1", "2"])

        if choice == "0":
            break
        elif choice == "1":
            _add_vendor_interactive(db)
        elif choice == "2":
            _list_vendors(db)


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


# ── Submissions ──────────────────────────────────────────────────────────


def submission_menu(db: Database):
    while True:
        console.print("\n[bold]Submissions & Follow-ups[/bold]")
        console.print("  [cyan]1[/cyan]  View Pending Follow-ups")
        console.print("  [cyan]2[/cyan]  View Submissions by Consultant")
        console.print("  [cyan]0[/cyan]  Back")
        choice = Prompt.ask("Select", choices=["0", "1", "2"])

        if choice == "0":
            break
        elif choice == "1":
            _pending_followups(db)
        elif choice == "2":
            _submissions_by_consultant(db)


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


# ── Email Generation ─────────────────────────────────────────────────────


def email_menu(db: Database, agent: BenchSalesAgent):
    while True:
        console.print("\n[bold]Email & Hotlist Generation[/bold]")
        console.print("  [cyan]1[/cyan]  Generate Hotlist Email")
        console.print("  [cyan]2[/cyan]  Generate Submission Email")
        console.print("  [cyan]3[/cyan]  AI-Crafted Submission Email")
        console.print("  [cyan]4[/cyan]  Vendor Introduction Email")
        console.print("  [cyan]0[/cyan]  Back")
        choice = Prompt.ask("Select", choices=["0", "1", "2", "3", "4"])

        if choice == "0":
            break
        elif choice == "1":
            _generate_hotlist(db)
        elif choice == "2":
            _generate_submission_email(db)
        elif choice == "3":
            _ai_submission_email(db, agent)
        elif choice == "4":
            _vendor_intro_email()


def _generate_hotlist(db: Database):
    consultants = db.list_consultants()
    if not consultants:
        console.print("[yellow]No consultants.[/yellow]")
        return

    email = EmailTemplates.hotlist_email(consultants)
    console.print(Panel(f"[bold]Subject:[/bold] {email['subject']}\n\n{email['body']}",
                        title="Hotlist Email", border_style="green"))


def _generate_submission_email(db: Database):
    list_consultants(db)
    cid = Prompt.ask("Consultant ID")
    c = db.get_consultant(cid)
    if not c:
        console.print("[red]Not found.[/red]")
        return

    _list_jobs(db)
    jid = Prompt.ask("Job ID")
    j = db.get_job(jid)
    if not j:
        console.print("[red]Not found.[/red]")
        return

    email = EmailTemplates.submission_email(c, j)
    console.print(Panel(f"[bold]Subject:[/bold] {email['subject']}\n\n{email['body']}",
                        title="Submission Email", border_style="green"))


def _ai_submission_email(db: Database, agent: BenchSalesAgent):
    list_consultants(db)
    cid = Prompt.ask("Consultant ID")
    c = db.get_consultant(cid)
    if not c:
        console.print("[red]Not found.[/red]")
        return

    _list_jobs(db)
    jid = Prompt.ask("Job ID")
    j = db.get_job(jid)
    if not j:
        console.print("[red]Not found.[/red]")
        return

    with console.status("AI crafting submission email..."):
        result = agent.craft_submission_email(c, j)
    console.print(Panel(Markdown(result), title="AI-Crafted Submission", border_style="green"))


def _vendor_intro_email():
    skills_raw = Prompt.ask("Your specializations (comma-separated)")
    skills = [s.strip() for s in skills_raw.split(",") if s.strip()]
    email = EmailTemplates.vendor_introduction_email(skills)
    console.print(Panel(f"[bold]Subject:[/bold] {email['subject']}\n\n{email['body']}",
                        title="Vendor Introduction", border_style="green"))


# ── AI Chat ──────────────────────────────────────────────────────────────


def ai_chat(agent: BenchSalesAgent, db: Database):
    console.print("\n[bold]AI Bench Sales Chat[/bold]")
    console.print("[dim]Ask anything about bench sales, market rates, strategies, etc.[/dim]")
    console.print("[dim]Type 'exit' to go back.[/dim]\n")

    # Give AI context about current data
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
    skills_raw = Prompt.ask("Key Skills (comma-separated)")
    skills = [s.strip() for s in skills_raw.split(",") if s.strip()]

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

    while True:
        try:
            choice = show_main_menu()

            if choice == "0":
                console.print("[bold]Goodbye![/bold]")
                sys.exit(0)
            elif choice == "1":
                consultant_menu(db, agent)
            elif choice == "2":
                search_menu(db, agent)
            elif choice == "3":
                job_menu(db)
            elif choice == "4":
                vendor_menu(db)
            elif choice == "5":
                submission_menu(db)
            elif choice == "6":
                email_menu(db, agent)
            elif choice == "7":
                ai_chat(agent, db)
            elif choice == "8":
                market_analysis(agent)
            elif choice == "9":
                dashboard(db)

        except KeyboardInterrupt:
            console.print("\n[bold]Goodbye![/bold]")
            sys.exit(0)
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")


if __name__ == "__main__":
    main()
