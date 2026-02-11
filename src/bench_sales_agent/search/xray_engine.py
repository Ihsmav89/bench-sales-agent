"""
Advanced X-Ray Search Engine for Bench Sales.

X-ray searching is a technique used by experienced recruiters to find hidden job postings,
vendor contacts, and contract requirements using Google search operators combined with
site-specific knowledge. This module encodes 15 years of bench sales search expertise.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class SearchPlatform(str, Enum):
    LINKEDIN = "linkedin"
    DICE = "dice"
    INDEED = "indeed"
    MONSTER = "monster"
    CAREERBUILDER = "careerbuilder"
    ZIPRECRUITER = "ziprecruiter"
    GLASSDOOR = "glassdoor"
    TECHFETCH = "techfetch"
    GOOGLE = "google"
    CORP_CORP = "corp-corp"


@dataclass
class SearchQuery:
    """Represents a constructed search query with metadata."""

    query: str
    platform: SearchPlatform
    search_url: str
    description: str
    category: str = ""  # "job_search", "vendor_hunt", "contact_find"
    priority: int = 1  # 1=highest


@dataclass
class ConsultantSearchParams:
    """Parameters derived from a consultant's profile for targeted searching."""

    job_title: str
    primary_skills: list[str] = field(default_factory=list)
    secondary_skills: list[str] = field(default_factory=list)
    location: str = ""
    remote_ok: bool = True
    visa_status: str = ""
    employment_types: list[str] = field(default_factory=lambda: ["C2C"])
    experience_years: float = 0
    rate_range: str = ""


class XRaySearchEngine:
    """
    Generates advanced X-ray search queries across multiple platforms.

    This engine encodes the search patterns and Boolean logic that experienced
    bench sales recruiters use to find contract requirements, vendor contacts,
    and hidden job postings that aren't visible through normal job board searches.
    """

    # Common IT role synonyms for broader matching
    ROLE_SYNONYMS = {
        "java developer": ["java developer", "java engineer", "java programmer", "j2ee developer"],
        "python developer": ["python developer", "python engineer", "django developer", "flask developer"],
        "data engineer": ["data engineer", "etl developer", "data pipeline engineer", "big data engineer"],
        "devops engineer": ["devops engineer", "site reliability engineer", "sre", "platform engineer", "cloud engineer"],
        "full stack developer": ["full stack developer", "fullstack developer", "full-stack developer", "mern developer", "mean developer"],
        "qa engineer": ["qa engineer", "qa analyst", "test engineer", "sdet", "quality assurance"],
        "business analyst": ["business analyst", "ba", "business systems analyst", "requirements analyst"],
        "data analyst": ["data analyst", "reporting analyst", "bi analyst", "analytics engineer"],
        "salesforce developer": ["salesforce developer", "sfdc developer", "salesforce engineer", "salesforce admin"],
        "aws engineer": ["aws engineer", "aws architect", "aws devops", "cloud engineer aws"],
        "azure engineer": ["azure engineer", "azure architect", "azure devops", "cloud engineer azure"],
        ".net developer": [".net developer", "dotnet developer", "c# developer", "asp.net developer"],
        "react developer": ["react developer", "react engineer", "reactjs developer", "frontend developer react"],
        "scrum master": ["scrum master", "agile coach", "agile scrum master"],
        "project manager": ["project manager", "program manager", "it project manager", "technical project manager"],
        "data scientist": ["data scientist", "ml engineer", "machine learning engineer", "ai engineer"],
        "sap consultant": ["sap consultant", "sap developer", "sap functional", "sap basis"],
        "network engineer": ["network engineer", "network administrator", "cisco engineer"],
        "security engineer": ["security engineer", "cybersecurity engineer", "information security", "infosec engineer"],
        "database administrator": ["database administrator", "dba", "database engineer", "sql dba"],
    }

    # Contract/C2C specific terms that indicate staffing requirements
    CONTRACT_TERMS = [
        "c2c", "corp to corp", "corp-to-corp", "corp 2 corp",
        "contract", "contract to hire", "c2h", "1099",
        "6 months", "12 months", "long term", "short term",
    ]

    # Terms indicating vendor/staffing company postings
    VENDOR_INDICATORS = [
        "staffing", "consulting", "solutions", "technologies",
        "infotech", "infosys", "cognizant", "tcs", "wipro",
        "hcl", "tek systems", "robert half", "randstad",
    ]

    def __init__(self):
        self._google_base = "https://www.google.com/search?q="

    def generate_all_queries(self, params: ConsultantSearchParams) -> list[SearchQuery]:
        """Generate a comprehensive set of search queries for a consultant profile."""
        queries = []
        queries.extend(self._linkedin_xray_queries(params))
        queries.extend(self._dice_xray_queries(params))
        queries.extend(self._indeed_xray_queries(params))
        queries.extend(self._monster_xray_queries(params))
        queries.extend(self._careerbuilder_xray_queries(params))
        queries.extend(self._ziprecruiter_xray_queries(params))
        queries.extend(self._techfetch_queries(params))
        queries.extend(self._vendor_hunt_queries(params))
        queries.extend(self._direct_client_queries(params))
        queries.extend(self._corp_corp_queries(params))
        queries.extend(self._vms_msp_queries(params))
        queries.extend(self._email_harvest_queries(params))
        return queries

    # ── LinkedIn X-Ray Searches ──────────────────────────────────────────

    def _linkedin_xray_queries(self, p: ConsultantSearchParams) -> list[SearchQuery]:
        queries = []
        title = p.job_title
        skills_str = " OR ".join(f'"{s}"' for s in p.primary_skills[:4])
        loc = p.location

        # 1. Find job postings on LinkedIn via Google X-ray
        q = f'site:linkedin.com/jobs "{title}" ({skills_str})'
        if loc:
            q += f' "{loc}"'
        q += ' ("c2c" OR "corp to corp" OR "corp-to-corp" OR "contract")'
        queries.append(SearchQuery(
            query=q,
            platform=SearchPlatform.LINKEDIN,
            search_url=self._google_base + self._url_encode(q),
            description=f"LinkedIn Jobs X-ray: {title} contract roles",
            category="job_search",
            priority=1,
        ))

        # 2. Find recruiters/vendors posting these roles on LinkedIn
        q2 = f'site:linkedin.com/in ("bench sales" OR "us staffing" OR "it recruiter") ({skills_str})'
        if loc:
            q2 += f' "{loc}"'
        queries.append(SearchQuery(
            query=q2,
            platform=SearchPlatform.LINKEDIN,
            search_url=self._google_base + self._url_encode(q2),
            description=f"LinkedIn People X-ray: Recruiters posting {title} roles",
            category="contact_find",
            priority=2,
        ))

        # 3. Find vendor companies posting these roles
        q3 = (
            f'site:linkedin.com/company ("staffing" OR "consulting" OR "solutions") '
            f'("{title}" OR {skills_str})'
        )
        queries.append(SearchQuery(
            query=q3,
            platform=SearchPlatform.LINKEDIN,
            search_url=self._google_base + self._url_encode(q3),
            description=f"LinkedIn Companies X-ray: Vendors hiring {title}",
            category="vendor_hunt",
            priority=3,
        ))

        # 4. LinkedIn posts mentioning urgent/hot requirements
        q4 = (
            f'site:linkedin.com/posts ("urgent requirement" OR "hot requirement" OR '
            f'"immediate need" OR "looking for") "{title}" ("c2c" OR "corp to corp" OR "corp-to-corp" OR "contract")'
        )
        if loc:
            q4 += f' "{loc}"'
        queries.append(SearchQuery(
            query=q4,
            platform=SearchPlatform.LINKEDIN,
            search_url=self._google_base + self._url_encode(q4),
            description=f"LinkedIn Posts X-ray: Urgent {title} requirements",
            category="job_search",
            priority=1,
        ))

        return queries

    # ── Dice X-Ray Searches ──────────────────────────────────────────────

    def _dice_xray_queries(self, p: ConsultantSearchParams) -> list[SearchQuery]:
        queries = []
        title = p.job_title
        skills_str = " OR ".join(f'"{s}"' for s in p.primary_skills[:4])

        # Dice direct X-ray
        q = f'site:dice.com/job-detail "{title}" ({skills_str})'
        if p.location:
            q += f' "{p.location}"'
        q += ' ("contract" OR "c2c")'
        queries.append(SearchQuery(
            query=q,
            platform=SearchPlatform.DICE,
            search_url=self._google_base + self._url_encode(q),
            description=f"Dice X-ray: {title} contract roles",
            category="job_search",
            priority=1,
        ))

        # Dice with specific visa terms
        if p.visa_status:
            q2 = f'site:dice.com "{title}" ("{p.visa_status}" OR "all visas" OR "any visa")'
            queries.append(SearchQuery(
                query=q2,
                platform=SearchPlatform.DICE,
                search_url=self._google_base + self._url_encode(q2),
                description=f"Dice X-ray: {title} roles accepting {p.visa_status}",
                category="job_search",
                priority=2,
            ))

        return queries

    # ── Indeed X-Ray Searches ────────────────────────────────────────────

    def _indeed_xray_queries(self, p: ConsultantSearchParams) -> list[SearchQuery]:
        queries = []
        title = p.job_title
        skills_str = " OR ".join(f'"{s}"' for s in p.primary_skills[:3])

        q = f'site:indeed.com/viewjob "{title}" ({skills_str}) ("c2c" OR "corp to corp" OR "contract")'
        if p.location:
            q += f' "{p.location}"'
        queries.append(SearchQuery(
            query=q,
            platform=SearchPlatform.INDEED,
            search_url=self._google_base + self._url_encode(q),
            description=f"Indeed X-ray: {title} contract roles",
            category="job_search",
            priority=1,
        ))

        return queries

    # ── Monster X-Ray Searches ───────────────────────────────────────────

    def _monster_xray_queries(self, p: ConsultantSearchParams) -> list[SearchQuery]:
        queries = []
        title = p.job_title

        q = f'site:monster.com "{title}" ("contract" OR "temporary") "{p.location}"'
        queries.append(SearchQuery(
            query=q,
            platform=SearchPlatform.MONSTER,
            search_url=self._google_base + self._url_encode(q),
            description=f"Monster X-ray: {title} contract roles",
            category="job_search",
            priority=2,
        ))

        return queries

    # ── CareerBuilder X-Ray Searches ─────────────────────────────────────

    def _careerbuilder_xray_queries(self, p: ConsultantSearchParams) -> list[SearchQuery]:
        queries = []
        title = p.job_title

        q = f'site:careerbuilder.com "{title}" ("contract" OR "c2c") "{p.location}"'
        queries.append(SearchQuery(
            query=q,
            platform=SearchPlatform.CAREERBUILDER,
            search_url=self._google_base + self._url_encode(q),
            description=f"CareerBuilder X-ray: {title} contract roles",
            category="job_search",
            priority=3,
        ))

        return queries

    # ── ZipRecruiter X-Ray Searches ──────────────────────────────────────

    def _ziprecruiter_xray_queries(self, p: ConsultantSearchParams) -> list[SearchQuery]:
        queries = []
        title = p.job_title
        skills_str = " OR ".join(f'"{s}"' for s in p.primary_skills[:3])

        q = f'site:ziprecruiter.com/jobs "{title}" ({skills_str}) "contract"'
        if p.location:
            q += f' "{p.location}"'
        queries.append(SearchQuery(
            query=q,
            platform=SearchPlatform.ZIPRECRUITER,
            search_url=self._google_base + self._url_encode(q),
            description=f"ZipRecruiter X-ray: {title} contract roles",
            category="job_search",
            priority=2,
        ))

        return queries

    # ── TechFetch Searches ───────────────────────────────────────────────

    def _techfetch_queries(self, p: ConsultantSearchParams) -> list[SearchQuery]:
        queries = []
        title = p.job_title

        q = f'site:techfetch.com "{title}" ("c2c" OR "contract")'
        if p.location:
            q += f' "{p.location}"'
        queries.append(SearchQuery(
            query=q,
            platform=SearchPlatform.TECHFETCH,
            search_url=self._google_base + self._url_encode(q),
            description=f"TechFetch X-ray: {title} C2C/contract roles",
            category="job_search",
            priority=2,
        ))

        return queries

    # ── Vendor Hunting Queries ───────────────────────────────────────────

    def _vendor_hunt_queries(self, p: ConsultantSearchParams) -> list[SearchQuery]:
        """Find vendor companies and contacts who post these kinds of roles."""
        queries = []
        title = p.job_title
        skills_str = " OR ".join(f'"{s}"' for s in p.primary_skills[:3])

        # Find vendor emails from job postings
        q = (
            f'("{title}" OR {skills_str}) ("send resume" OR "email resume" OR '
            f'"send profiles" OR "share profiles") ("c2c" OR "corp to corp" OR "contract") '
            f'"@" (".com" OR ".net" OR ".io")'
        )
        if p.location:
            q += f' "{p.location}"'
        queries.append(SearchQuery(
            query=q,
            platform=SearchPlatform.GOOGLE,
            search_url=self._google_base + self._url_encode(q),
            description=f"Vendor hunt: Find recruiters with {title} needs",
            category="vendor_hunt",
            priority=1,
        ))

        # Find staffing companies specializing in these skills
        q2 = (
            f'"staffing" ("consulting") ({skills_str}) '
            f'("c2c" OR "corp to corp" OR "contract staffing") "united states"'
        )
        queries.append(SearchQuery(
            query=q2,
            platform=SearchPlatform.GOOGLE,
            search_url=self._google_base + self._url_encode(q2),
            description=f"Find staffing companies specializing in {title}",
            category="vendor_hunt",
            priority=2,
        ))

        return queries

    # ── Direct Client Queries ────────────────────────────────────────────

    def _direct_client_queries(self, p: ConsultantSearchParams) -> list[SearchQuery]:
        """Find direct client postings (bypass vendors for better rates)."""
        queries = []
        title = p.job_title
        skills_str = " OR ".join(f'"{s}"' for s in p.primary_skills[:3])

        # Find direct client job postings (career sites)
        q = (
            f'inurl:careers OR inurl:jobs "{title}" ({skills_str}) '
            f'"contract" -site:linkedin.com -site:indeed.com -site:dice.com '
            f'-site:monster.com -site:ziprecruiter.com'
        )
        if p.location:
            q += f' "{p.location}"'
        queries.append(SearchQuery(
            query=q,
            platform=SearchPlatform.GOOGLE,
            search_url=self._google_base + self._url_encode(q),
            description=f"Direct client search: {title} on corporate career sites",
            category="job_search",
            priority=1,
        ))

        # Government / state contract roles
        q2 = (
            f'(site:governmentjobs.com OR site:usajobs.gov OR "state contract") '
            f'"{title}" ({skills_str})'
        )
        if p.location:
            q2 += f' "{p.location}"'
        queries.append(SearchQuery(
            query=q2,
            platform=SearchPlatform.GOOGLE,
            search_url=self._google_base + self._url_encode(q2),
            description=f"Government/state contracts: {title}",
            category="job_search",
            priority=3,
        ))

        return queries

    # ── Corp-to-Corp Specific Queries ────────────────────────────────────

    def _corp_corp_queries(self, p: ConsultantSearchParams) -> list[SearchQuery]:
        """Queries specifically targeting C2C opportunities."""
        queries = []
        title = p.job_title
        skills_str = " OR ".join(f'"{s}"' for s in p.primary_skills[:3])

        q = (
            f'"{title}" ({skills_str}) ("c2c" OR "corp to corp" OR "corp-to-corp") '
            f'("requirement" OR "position" OR "opening" OR "need")'
        )
        if p.location:
            q += f' "{p.location}"'
        queries.append(SearchQuery(
            query=q,
            platform=SearchPlatform.CORP_CORP,
            search_url=self._google_base + self._url_encode(q),
            description=f"C2C specific: {title} corp-to-corp requirements",
            category="job_search",
            priority=1,
        ))

        # Search specifically on C2C job boards
        q2 = f'(site:c2crequirements.com OR site:c2cjobs.com) "{title}" ({skills_str})'
        queries.append(SearchQuery(
            query=q2,
            platform=SearchPlatform.CORP_CORP,
            search_url=self._google_base + self._url_encode(q2),
            description=f"C2C job boards: {title}",
            category="job_search",
            priority=2,
        ))

        return queries

    # ── VMS/MSP Queries ──────────────────────────────────────────────────

    def _vms_msp_queries(self, p: ConsultantSearchParams) -> list[SearchQuery]:
        """Target VMS/MSP managed programs (Fieldglass, Beeline, etc.)."""
        queries = []
        title = p.job_title

        q = (
            f'("{title}") ("fieldglass" OR "beeline" OR "workforce logiq" OR '
            f'"vms" OR "managed service") ("contract" OR "contingent")'
        )
        if p.location:
            q += f' "{p.location}"'
        queries.append(SearchQuery(
            query=q,
            platform=SearchPlatform.GOOGLE,
            search_url=self._google_base + self._url_encode(q),
            description=f"VMS/MSP programs: {title} contingent roles",
            category="job_search",
            priority=3,
        ))

        return queries

    # ── Email / Contact Harvesting ───────────────────────────────────────

    def _email_harvest_queries(self, p: ConsultantSearchParams) -> list[SearchQuery]:
        """Find recruiter/vendor email addresses for direct outreach."""
        queries = []
        title = p.job_title

        q = (
            f'("{title}" OR "bench sales") ("send resume to" OR "email your resume" '
            f'OR "submit resume") "@" ("gmail.com" OR "yahoo.com" OR ".com")'
        )
        queries.append(SearchQuery(
            query=q,
            platform=SearchPlatform.GOOGLE,
            search_url=self._google_base + self._url_encode(q),
            description=f"Find recruiter emails for {title} submissions",
            category="contact_find",
            priority=2,
        ))

        return queries

    # ── Hotlist Search Queries ───────────────────────────────────────────

    def generate_hotlist_queries(self, p: ConsultantSearchParams) -> list[SearchQuery]:
        """Generate queries to find requirement hotlists from vendors."""
        queries = []
        title = p.job_title
        skills_str = " OR ".join(f'"{s}"' for s in p.primary_skills[:3])

        # Find hotlist/requirement list emails posted online
        q = (
            f'("hotlist" OR "requirement list" OR "urgent requirements" OR "hot list") '
            f'({skills_str} OR "{title}") ("c2c" OR "corp to corp" OR "contract")'
        )
        queries.append(SearchQuery(
            query=q,
            platform=SearchPlatform.GOOGLE,
            search_url=self._google_base + self._url_encode(q),
            description=f"Find vendor hotlists with {title} requirements",
            category="job_search",
            priority=1,
        ))

        # Find Google Groups / Yahoo Groups with requirements
        q2 = (
            f'(site:groups.google.com OR "google groups" OR "yahoo groups") '
            f'"requirement" ({skills_str} OR "{title}") ("c2c" OR "contract")'
        )
        queries.append(SearchQuery(
            query=q2,
            platform=SearchPlatform.GOOGLE,
            search_url=self._google_base + self._url_encode(q2),
            description=f"Mailing list requirements for {title}",
            category="job_search",
            priority=3,
        ))

        return queries

    def get_role_synonyms(self, title: str) -> list[str]:
        """Get alternative job titles for broader searching."""
        title_lower = title.lower().strip()
        return self.ROLE_SYNONYMS.get(title_lower, [title])

    @staticmethod
    def _url_encode(query: str) -> str:
        """URL-encode a search query string."""
        import urllib.parse
        return urllib.parse.quote_plus(query)
