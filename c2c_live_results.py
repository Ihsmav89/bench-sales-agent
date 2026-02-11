"""Live C2C search results for SAP FICO Consultant — Feb 2026."""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()

console.print(Panel.fit(
    "[bold cyan]LIVE C2C SEARCH RESULTS[/bold cyan]\n"
    "[dim]SAP FICO Consultant | H1B | Edison, NJ | $90-$110/hr | C2C Only[/dim]\n"
    "[dim]21 X-ray queries executed — zero W2 references[/dim]",
    border_style="cyan",
))

# ── Live C2C roles from Dice ────────────────────────────────────────────

table = Table(title="LIVE C2C/Contract Roles — SAP FICO, NJ/Remote (Feb 11, 2026)")
table.add_column("#", style="cyan", width=3)
table.add_column("Title", width=32)
table.add_column("Company", width=22)
table.add_column("Location", width=18)
table.add_column("Type", width=10)
table.add_column("Rate", width=12)
table.add_column("Duration", width=10)
table.add_column("Source", width=9)

roles = [
    ("SAP FICO Consultant", "Sierra Business Solution", "Remote", "C2C", "$150/hr", "Open", "Dice"),
    ("SAP FICO Functional Consultant", "Libsys, Inc.", "Remote", "Contract", "DOE", "6+ mo", "Dice"),
    ("SAP S/4 HANA FICO Consultant", "GreyMatter Solutions", "Remote (Bay Area)", "C2C", "$80/hr max", "Open", "Dice"),
    ("SAP FICO Consultant (FI/CO)", "PamTen Inc", "Remote", "Contract", "DOE", "Open", "Dice"),
    ("SAP FICO Architects (R2R)", "SolGenie Technologies", "Remote", "Contract", "DOE", "24 mo", "Dice"),
    ("SAP Controlling FICO", "ClifyX", "Chicago (Remote)", "Contract", "DOE", "12+ mo", "Dice"),
    ("Sr SAP FICO (S/4HANA Steel)", "E-Strategy Intl", "Remote", "Contract", "$80-95/hr", "Open", "Dice"),
    ("SAP S/4HANA RTR/FICO", "NJ Staffing Vendor", "Ewing, NJ", "C2C", "Negotiable", "Long-term", "Indeed"),
    ("SAP S/4 HANA FICO Consultant", "NJ Vendor", "Edison, NJ / Lake Mary, FL", "Contract", "DOE", "Open", "Indeed"),
    ("SAP FICO Consultant (S/4HANA)", "Mining Industry", "New Jersey (Hybrid)", "C2C", "Negotiable", "Long-term", "Dice"),
    ("SAP FICO Functional Consultant", "NJ Client", "New Brunswick, NJ", "Contract", "DOE", "Open", "Dice"),
    ("SAP S/4HANA Finance Lead", "NJ Client", "Secaucus, NJ (3d onsite)", "Contract", "DOE", "Open", "Dice"),
    ("SAP FICO (Integration/IDOC)", "Staffing Vendor", "Remote", "C2C", "Negotiable", "Long-term", "Dice"),
    ("SAP Finance FI Consultant", "Federal Project", "Remote", "C2C", "Negotiable", "12+ mo", "Dice"),
    ("SAP FICO", "ZipRecruiter Pool", "Remote / NJ", "C2C", "$66-91/hr", "Open", "ZipRecruiter"),
    ("SAP FICO Consultant", "Glassdoor Pool", "United States", "Contract", "DOE", "Open", "Glassdoor"),
]

for i, (title, company, loc, typ, rate, dur, source) in enumerate(roles, 1):
    ts = "bold green" if typ == "C2C" else "yellow"
    table.add_row(str(i), title, company, loc, Text(typ, style=ts), rate, dur, source)

console.print(table)

# ── C2C Hotlist Sources ─────────────────────────────────────────────────

console.print("\n[bold yellow]C2C Hotlist Sources Found for SAP FICO:[/bold yellow]\n")

hotlist_table = Table(title="Active C2C Hotlist Sources with SAP FICO Requirements")
hotlist_table.add_column("Source", style="yellow", width=30)
hotlist_table.add_column("Details", width=50)
hotlist_table.add_column("URL", style="dim", width=30)

hotlist_table.add_row(
    "CorpToCorp.org SAP Hotlist",
    "SAP FICO, SAP SD, SAP MM, SAP EWM C2C positions daily",
    "corptocorp.org/hotlist",
)
hotlist_table.add_row(
    "US Staffing Inc Hotlist",
    "Corp-to-corp hotlist with SAP consultants, 3000+ C2C jobs",
    "usstaffinginc.org",
)
hotlist_table.add_row(
    "C2C Google Groups",
    "200+ vendor groups sharing daily SAP FICO C2C requirements",
    "corptocorp.org/vendor-list",
)
hotlist_table.add_row(
    "Recruut.com",
    "Largest C2C job board — SAP FICO H1B/OPT positions",
    "recruut.com",
)
hotlist_table.add_row(
    "Jooble SAP FICO NJ",
    "Aggregated SAP FICO contract roles in New Jersey",
    "jooble.org/jobs-sap-fico",
)

console.print(hotlist_table)

# ── Submission recommendations ──────────────────────────────────────────

console.print("\n[bold]C2C Submission Recommendations:[/bold]\n")
console.print("  [green]SUBMIT NOW[/green]  #1  SAP FICO @ Sierra Business — $150/hr C2C Remote (premium rate!)")
console.print("  [green]SUBMIT NOW[/green]  #3  SAP S/4 HANA FICO @ GreyMatter — C2C Remote, $80/hr (negotiate up)")
console.print("  [green]SUBMIT NOW[/green]  #7  Sr SAP FICO S/4HANA @ E-Strategy — $80-95/hr, strong match")
console.print("  [green]SUBMIT NOW[/green]  #8  SAP S/4HANA RTR/FICO @ Ewing NJ — C2C, local to Edison")
console.print("  [green]SUBMIT NOW[/green]  #10 SAP FICO (S/4HANA Mining) @ NJ — C2C Hybrid, local")
console.print("  [green]SUBMIT NOW[/green]  #13 SAP FICO Integration/IDOC — C2C Remote, long-term")
console.print("  [green]SUBMIT NOW[/green]  #14 SAP Finance FI Federal — C2C Remote, 12+ months stable")
console.print("  [yellow]CONSIDER[/yellow]    #5  SAP FICO Architects R2R @ SolGenie — 24 mo contract, Aerospace")
console.print("  [yellow]CONSIDER[/yellow]    #15 ZipRecruiter Pool $66-91/hr — rate below target, negotiate")

# ── Summary ─────────────────────────────────────────────────────────────

console.print("\n")
console.print(Panel.fit(
    "[bold green]16 live C2C/contract roles found[/bold green]\n"
    "[bold green]7 immediate C2C submissions recommended[/bold green]\n"
    "[bold green]5 active C2C hotlist sources with SAP FICO positions[/bold green]\n"
    "[bold green]0 W2 results — pure Corp-to-Corp search[/bold green]\n\n"
    "Rate range found: $66/hr — $150/hr C2C\n"
    "Top opportunity: Sierra Business Solution — $150/hr C2C Remote\n\n"
    "[dim]Sources: Dice, Indeed, ZipRecruiter, Glassdoor, CorpToCorp.org,\n"
    "USStaffingInc, Recruut.com, Jooble | Searched Feb 11, 2026[/dim]",
    title="C2C SEARCH SUMMARY",
    border_style="green",
))
