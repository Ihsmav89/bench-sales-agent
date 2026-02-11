"""Demo walkthrough of the Bench Sales Agent capabilities."""

from datetime import date
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from bench_sales_agent.agent import BenchSalesAgent
from bench_sales_agent.data.database import Database
from bench_sales_agent.models.consultant import ConsultantProfile, VisaStatus, EmploymentType
from bench_sales_agent.models.job import JobRequirement
from bench_sales_agent.models.vendor import Vendor, VendorTier
from bench_sales_agent.search.xray_engine import XRaySearchEngine, ConsultantSearchParams
from bench_sales_agent.search.job_board_urls import JobBoardURLBuilder
from bench_sales_agent.templates.emails import EmailTemplates

console = Console()

# ── Banner ───────────────────────────────────────────────────────────────

console.print(Panel.fit(
    "[bold cyan]BENCH SALES AGENT — FULL DEMO[/bold cyan]\n"
    "[dim]Walking through all major features[/dim]",
    border_style="cyan",
))

# ── 1. Add Consultants to Bench ─────────────────────────────────────────

console.print("\n[bold yellow]═══ STEP 1: Adding Consultants to Bench ═══[/bold yellow]\n")

db = Database("/tmp/bench_sales_demo.json")

consultants = [
    ConsultantProfile(
        full_name="Rajesh Kumar",
        email="rajesh.k@example.com",
        phone="469-555-0101",
        current_location="Dallas, TX",
        job_title="Java Developer",
        primary_skills=["Java", "Spring Boot", "Microservices", "AWS", "Docker", "Kubernetes"],
        secondary_skills=["React", "PostgreSQL", "Jenkins", "Terraform"],
        total_experience_years=10,
        us_experience_years=7,
        visa_status=VisaStatus.H1B,
        remote_preference="Remote",
        relocation=True,
        relocation_preferences=["Austin, TX", "Charlotte, NC", "Atlanta, GA"],
        expected_rate_hourly=80,
        minimum_rate_hourly=70,
        bench_since=date(2025, 12, 15),
        employment_types_accepted=[EmploymentType.C2C, EmploymentType.W2],
    ),
    ConsultantProfile(
        full_name="Priya Sharma",
        email="priya.s@example.com",
        phone="312-555-0202",
        current_location="Chicago, IL",
        job_title="Data Engineer",
        primary_skills=["Python", "Spark", "AWS", "Snowflake", "Airflow", "SQL"],
        secondary_skills=["Kafka", "dbt", "Terraform", "Databricks"],
        total_experience_years=7,
        us_experience_years=5,
        visa_status=VisaStatus.H4_EAD,
        remote_preference="Remote",
        relocation=False,
        expected_rate_hourly=75,
        minimum_rate_hourly=65,
        bench_since=date(2026, 1, 5),
        employment_types_accepted=[EmploymentType.W2, EmploymentType.C2C],
    ),
    ConsultantProfile(
        full_name="Michael Chen",
        email="michael.c@example.com",
        phone="206-555-0303",
        current_location="Seattle, WA",
        job_title="DevOps Engineer",
        primary_skills=["AWS", "Kubernetes", "Terraform", "Docker", "Python", "CI/CD"],
        secondary_skills=["Azure", "Ansible", "Prometheus", "Grafana"],
        total_experience_years=8,
        us_experience_years=8,
        visa_status=VisaStatus.GC,
        remote_preference="Hybrid",
        relocation=True,
        relocation_preferences=["Bay Area, CA", "Portland, OR"],
        expected_rate_hourly=90,
        minimum_rate_hourly=80,
        bench_since=date(2026, 1, 20),
        employment_types_accepted=[EmploymentType.C2C, EmploymentType.W2],
    ),
]

for c in consultants:
    cid = db.add_consultant(c)
    console.print(f"  [green]✓[/green] Added: {c.one_liner()}  [dim](ID: {cid})[/dim]")

# ── 2. View Bench Dashboard ─────────────────────────────────────────────

console.print("\n[bold yellow]═══ STEP 2: Bench Dashboard ═══[/bold yellow]\n")

table = Table(title="Bench Consultants")
table.add_column("ID", style="cyan")
table.add_column("Name")
table.add_column("Title")
table.add_column("Top Skills")
table.add_column("Visa")
table.add_column("Location")
table.add_column("Rate")
table.add_column("Bench Days", justify="right", style="red")

for c in db.list_consultants():
    table.add_row(
        c.id or "", c.full_name, c.job_title,
        ", ".join(c.primary_skills[:3]),
        c.visa_status.value, c.current_location,
        c.rate_display(), str(c.bench_duration_days()),
    )
console.print(table)

# ── 3. X-Ray Search Queries ─────────────────────────────────────────────

console.print("\n[bold yellow]═══ STEP 3: X-Ray Search for Rajesh (Java Developer) ═══[/bold yellow]\n")

rajesh = db.list_consultants()[0]
engine = XRaySearchEngine()
params = ConsultantSearchParams(
    job_title=rajesh.job_title,
    primary_skills=rajesh.primary_skills,
    location=rajesh.current_location,
    remote_ok=True,
    visa_status=rajesh.visa_status.value,
    employment_types=["C2C", "W2"],
    experience_years=rajesh.total_experience_years,
)

queries = engine.generate_all_queries(params)
hotlist_queries = engine.generate_hotlist_queries(params)

# Group by category
categories = {}
for q in queries + hotlist_queries:
    categories.setdefault(q.category or "general", []).append(q)

for cat, cat_queries in categories.items():
    cat_queries.sort(key=lambda x: x.priority)
    tbl = Table(title=f"X-Ray Queries: {cat.replace('_', ' ').title()}")
    tbl.add_column("#", width=3, style="cyan")
    tbl.add_column("Platform", width=14, style="yellow")
    tbl.add_column("Description")
    tbl.add_column("Priority", width=8, justify="center")

    for i, q in enumerate(cat_queries, 1):
        pstyle = "bold red" if q.priority == 1 else "yellow" if q.priority == 2 else "dim"
        tbl.add_row(str(i), q.platform.value, q.description, Text(f"P{q.priority}", style=pstyle))
    console.print(tbl)

console.print(f"\n[bold]Total queries generated: {len(queries) + len(hotlist_queries)}[/bold]")

# Show a few sample raw queries
console.print("\n[bold]Sample Raw X-Ray Queries:[/bold]")
for q in queries[:3]:
    console.print(f"\n  [cyan]{q.description}[/cyan]")
    console.print(f"  [dim]Query:[/dim] {q.query[:120]}...")
    console.print(f"  [dim]URL:[/dim] {q.search_url[:100]}...")

# ── 4. Job Board Direct Links ───────────────────────────────────────────

console.print("\n[bold yellow]═══ STEP 4: Direct Job Board Search Links ═══[/bold yellow]\n")

links = JobBoardURLBuilder.all_boards("Java Developer", "Dallas, TX")
tbl = Table(title="Job Board Direct Links — Java Developer, Dallas TX")
tbl.add_column("Platform", style="yellow", width=15)
tbl.add_column("Description")
tbl.add_column("URL", style="dim")

for link in links:
    tbl.add_row(link.platform, link.description, link.url[:90] + "...")
console.print(tbl)

# ── 5. Role Synonyms ────────────────────────────────────────────────────

console.print("\n[bold yellow]═══ STEP 5: Smart Role Synonym Expansion ═══[/bold yellow]\n")

for title in ["java developer", "data engineer", "devops engineer", "full stack developer"]:
    synonyms = engine.get_role_synonyms(title)
    console.print(f"  [cyan]{title}[/cyan] → {', '.join(synonyms)}")

# ── 6. Add Job Requirements ─────────────────────────────────────────────

console.print("\n[bold yellow]═══ STEP 6: Adding Job Requirements ═══[/bold yellow]\n")

jobs = [
    JobRequirement(
        title="Senior Java Developer",
        client_name="Bank of America",
        vendor_name="TechStar Solutions",
        vendor_contact_email="recruiter@techstar.com",
        required_skills=["Java", "Spring Boot", "Microservices", "AWS", "SQL"],
        preferred_skills=["Kubernetes", "Docker", "React"],
        location="Charlotte, NC",
        remote_option="Hybrid",
        duration_months=12,
        bill_rate=95,
        employment_type="C2C",
        source_platform="dice",
        posted_date=date.today(),
    ),
    JobRequirement(
        title="AWS Data Engineer",
        vendor_name="InfoPro Consulting",
        vendor_contact_email="jobs@infopro.com",
        required_skills=["Python", "AWS", "Spark", "Snowflake", "Airflow"],
        location="Remote",
        remote_option="Remote",
        duration_months=6,
        bill_rate=85,
        employment_type="C2C/W2",
        source_platform="linkedin",
        posted_date=date.today(),
    ),
    JobRequirement(
        title="Kubernetes/DevOps Engineer",
        vendor_name="CyberEdge Staffing",
        vendor_contact_email="submit@cyberedge.io",
        required_skills=["Kubernetes", "AWS", "Terraform", "Docker", "CI/CD", "Python"],
        location="Seattle, WA",
        remote_option="Onsite",
        duration_months=18,
        bill_rate=110,
        employment_type="C2C",
        source_platform="email",
        posted_date=date.today(),
    ),
]

for j in jobs:
    jid = db.add_job(j)
    console.print(
        f"  [green]✓[/green] {j.title} | {j.vendor_name} | {j.location} | "
        f"${j.bill_rate}/hr | {j.employment_type}  [dim](ID: {jid})[/dim]"
    )

# ── 7. Match Consultants to Jobs ────────────────────────────────────────

console.print("\n[bold yellow]═══ STEP 7: Consultant-to-Job Matching ═══[/bold yellow]\n")

all_consultants = db.list_consultants()
all_jobs = db.list_jobs()

for c in all_consultants:
    console.print(f"\n[bold]{c.full_name} ({c.job_title})[/bold]")
    matches = []
    for j in all_jobs:
        score = j.match_score(c.primary_skills + c.secondary_skills)
        matches.append((j, score))
    matches.sort(key=lambda x: x[1], reverse=True)

    tbl = Table()
    tbl.add_column("Job", width=30)
    tbl.add_column("Match %", justify="right", width=10)
    tbl.add_column("Vendor")
    tbl.add_column("Location")
    tbl.add_column("Rate")
    tbl.add_column("Verdict", width=12)

    for j, score in matches:
        style = "bold green" if score >= 60 else "yellow" if score >= 40 else "red"
        verdict = "SUBMIT" if score >= 60 else "MAYBE" if score >= 40 else "SKIP"
        v_style = "bold green" if verdict == "SUBMIT" else "yellow" if verdict == "MAYBE" else "dim red"
        tbl.add_row(
            j.title, Text(f"{score:.0f}%", style=style),
            j.vendor_name or "", j.location,
            f"${j.bill_rate}/hr" if j.bill_rate else "N/A",
            Text(verdict, style=v_style),
        )
    console.print(tbl)

# ── 8. Add Vendors ──────────────────────────────────────────────────────

console.print("\n[bold yellow]═══ STEP 8: Vendor Database ═══[/bold yellow]\n")

vendors = [
    Vendor(
        company_name="TechStar Solutions",
        tier=VendorTier.TIER_1,
        primary_contact_name="Sarah Johnson",
        primary_contact_email="recruiter@techstar.com",
        primary_contact_phone="704-555-1001",
        specializations=["Java", ".NET", "Cloud"],
        payment_terms="Net 30",
        total_submissions=15,
        total_placements=4,
        reliability_score=8.5,
    ),
    Vendor(
        company_name="InfoPro Consulting",
        tier=VendorTier.PRIME_VENDOR,
        primary_contact_name="David Lee",
        primary_contact_email="jobs@infopro.com",
        specializations=["Data Engineering", "Cloud", "AI/ML"],
        payment_terms="Net 45",
        msp_vms="Fieldglass",
        total_submissions=8,
        total_placements=2,
        reliability_score=7.0,
    ),
    Vendor(
        company_name="CyberEdge Staffing",
        tier=VendorTier.TIER_1,
        primary_contact_name="Mike Torres",
        primary_contact_email="submit@cyberedge.io",
        specializations=["DevOps", "Security", "Cloud"],
        payment_terms="Net 30",
        total_submissions=5,
        total_placements=1,
        reliability_score=6.5,
    ),
]

tbl = Table(title="Vendor Database")
tbl.add_column("Company", style="yellow")
tbl.add_column("Tier")
tbl.add_column("Contact")
tbl.add_column("Specializations")
tbl.add_column("Submissions", justify="right")
tbl.add_column("Placements", justify="right")
tbl.add_column("Placement %", justify="right")
tbl.add_column("Reliability", justify="right")

for v in vendors:
    vid = db.add_vendor(v)
    tbl.add_row(
        v.company_name, v.tier.value,
        v.primary_contact_name or "",
        ", ".join(v.specializations[:3]),
        str(v.total_submissions), str(v.total_placements),
        f"{v.placement_rate():.0f}%",
        f"{v.reliability_score}/10",
    )
console.print(tbl)

# ── 9. Generate Submission Email ─────────────────────────────────────────

console.print("\n[bold yellow]═══ STEP 9: Submission Email for Rajesh → Senior Java Dev ═══[/bold yellow]\n")

email = EmailTemplates.submission_email(rajesh, all_jobs[0])
console.print(Panel(
    f"[bold]Subject:[/bold] {email['subject']}\n\n{email['body']}",
    title="Submission Email", border_style="green",
))

# ── 10. Generate Hotlist Email ───────────────────────────────────────────

console.print("\n[bold yellow]═══ STEP 10: Hotlist Email (All Bench Consultants) ═══[/bold yellow]\n")

hotlist = EmailTemplates.hotlist_email(all_consultants)
console.print(Panel(
    f"[bold]Subject:[/bold] {hotlist['subject']}\n\n{hotlist['body']}",
    title="Hotlist Email", border_style="magenta",
))

# ── 11. Follow-up Email ─────────────────────────────────────────────────

console.print("\n[bold yellow]═══ STEP 11: Vendor Introduction Email ═══[/bold yellow]\n")

intro = EmailTemplates.vendor_introduction_email(
    ["Java/J2EE", "Python/Data Engineering", "AWS/DevOps", "Full Stack", ".NET"]
)
console.print(Panel(
    f"[bold]Subject:[/bold] {intro['subject']}\n\n{intro['body']}",
    title="Vendor Introduction", border_style="blue",
))

# ── 12. Dashboard ────────────────────────────────────────────────────────

console.print("\n[bold yellow]═══ STEP 12: Dashboard ═══[/bold yellow]\n")

stats = db.get_stats()
tbl = Table(title="Bench Sales Dashboard")
tbl.add_column("Metric", style="bold")
tbl.add_column("Count", justify="right", style="cyan")
tbl.add_row("Consultants on Bench", str(stats["consultants_on_bench"]))
tbl.add_row("Total Consultants", str(stats["total_consultants"]))
tbl.add_row("Active Job Requirements", str(stats["active_jobs"]))
tbl.add_row("Total Jobs Tracked", str(stats["total_jobs"]))
tbl.add_row("Vendors in Database", str(stats["total_vendors"]))
tbl.add_row("Active Submissions", str(stats["active_submissions"]))
tbl.add_row("Total Submissions", str(stats["total_submissions"]))
console.print(tbl)

# ── 13. X-Ray Search for Priya (Data Engineer) ──────────────────────────

console.print("\n[bold yellow]═══ BONUS: X-Ray Search for Priya (Data Engineer) ═══[/bold yellow]\n")

priya = all_consultants[1]
params2 = ConsultantSearchParams(
    job_title=priya.job_title,
    primary_skills=priya.primary_skills,
    location=priya.current_location,
    remote_ok=True,
    visa_status=priya.visa_status.value,
)
queries2 = engine.generate_all_queries(params2)

# Just show job search queries
job_queries = [q for q in queries2 if q.category == "job_search"]
job_queries.sort(key=lambda x: x.priority)

tbl = Table(title=f"Top Job Search Queries for {priya.full_name} ({priya.job_title})")
tbl.add_column("#", width=3, style="cyan")
tbl.add_column("Platform", width=14, style="yellow")
tbl.add_column("Description")
tbl.add_column("Search Query", style="dim", max_width=80)

for i, q in enumerate(job_queries[:8], 1):
    tbl.add_row(str(i), q.platform.value, q.description, q.query[:80] + "...")
console.print(tbl)

# ── Summary ──────────────────────────────────────────────────────────────

console.print("\n")
console.print(Panel.fit(
    "[bold green]Demo Complete![/bold green]\n\n"
    "Features demonstrated:\n"
    "  1. Consultant bench management with visa/rate/skills tracking\n"
    "  2. X-ray search query generation (20+ queries per consultant)\n"
    "  3. Direct job board search links (8 boards)\n"
    "  4. Role synonym expansion for broader searches\n"
    "  5. Job requirement tracking with skill matching scores\n"
    "  6. Consultant-to-job match scoring (auto SUBMIT/MAYBE/SKIP)\n"
    "  7. Vendor database with tier system and placement tracking\n"
    "  8. Professional submission email generation\n"
    "  9. Hotlist email generation for mass vendor outreach\n"
    " 10. Vendor introduction email templates\n"
    " 11. Dashboard with real-time stats\n\n"
    "[dim]Add ANTHROPIC_API_KEY for: AI chat, profile analysis, smart emails, market rates[/dim]",
    border_style="cyan",
))

# Cleanup
import os
os.unlink("/tmp/bench_sales_demo.json")
