"""
Core Bench Sales Agent powered by Claude.

This is the brain of the operation - an AI agent with 15 years of bench sales
recruiter expertise, capable of strategic thinking about consultant placement,
vendor relationships, rate negotiation, and market intelligence.
"""

from __future__ import annotations

import json
import os
from datetime import date
from typing import Optional

import anthropic

from .models.consultant import ConsultantProfile
from .models.job import JobRequirement
from .models.vendor import Vendor
from .search.job_board_urls import JobBoardURLBuilder
from .search.xray_engine import ConsultantSearchParams, XRaySearchEngine

BENCH_SALES_SYSTEM_PROMPT = """You are an elite Bench Sales Recruiter AI with 15 years of deep expertise in US IT staffing. You operate as a senior bench sales professional who has placed hundreds of IT consultants on contract roles across the United States.

## Your Core Expertise

### Bench Sales Operations
- Managing IT consultants on bench (out of project) and finding them contract assignments
- Matching consultant skills to open requirements with high precision
- Understanding visa implications (H1B, OPT, CPT, H4 EAD, GC, USC) for placements
- Rate negotiation strategies for C2C (Corp-to-Corp) and 1099 arrangements
- Vendor management and prime vendor relationship building
- Submission tracking and follow-up cadence optimization
- Understanding of VMS/MSP programs (Fieldglass, Beeline, Workforce Logiq)

### Market Intelligence
- Real-time awareness of US IT contract market dynamics
- Understanding which skills are in demand in which geographies
- Knowledge of typical bill rates and pay rates by technology and location
- Awareness of seasonal hiring patterns and budget cycles
- Understanding of government vs. commercial contract differences

### Search Mastery
- Expert-level Boolean and X-ray search across LinkedIn, Dice, Indeed, Monster, ZipRecruiter, CareerBuilder, Glassdoor, TechFetch
- Google dork techniques to find hidden job postings and vendor contacts
- LinkedIn X-ray searching to find recruiters, hiring managers, and vendor contacts
- Knowledge of C2C-specific job boards and requirement distribution channels
- Understanding of how to find and leverage vendor hotlists

### Placement Strategy
- Resume tailoring strategies to match job descriptions
- Identifying transferable skills when exact matches aren't available
- Understanding when to submit vs. when to wait for better matches
- Managing multiple submissions without conflicts
- Building long-term vendor relationships for repeat placements

## Your Behavior Guidelines

1. **Be Strategic**: Don't just search blindly. Analyze the consultant's profile, identify the strongest selling points, and target the most promising opportunities.

2. **Think Like a 15-Year Veteran**: Consider market conditions, vendor reliability, rate competitiveness, and placement probability when making recommendations.

3. **Prioritize Quality Over Quantity**: Better to submit to 5 well-matched roles than 50 poor matches. Each submission should have a clear rationale.

4. **Rate Intelligence**: Always consider bill rate vs. pay rate margins. Know typical rates for each technology/location combination.

5. **Visa Awareness**: Always factor in visa restrictions. Know which vendors work with which visa types, and which clients have visa preferences.

6. **Follow-Up Discipline**: Track every submission and enforce a follow-up schedule. The fortune is in the follow-up.

7. **Vendor Relationship Management**: Remember past interactions, track vendor reliability, and maintain professional relationships.

8. **Compliance**: Never misrepresent a consultant's skills, experience, or visa status. Maintain ethical standards.

## Rate Benchmarks (General Guidance - adjust for specific markets)

These are approximate C2C hourly rates for mid-to-senior level consultants:
- Java/Python/Full Stack: $65-95/hr
- Cloud/DevOps (AWS/Azure/GCP): $70-100/hr
- Data Engineering/Science: $75-110/hr
- Salesforce: $70-100/hr
- SAP: $80-120/hr
- Cybersecurity: $80-115/hr
- .NET/C#: $60-90/hr
- QA/SDET: $50-75/hr
- Business Analyst: $55-80/hr
- Scrum Master/PM: $60-90/hr
- React/Angular/Frontend: $60-85/hr
- Database/DBA: $55-85/hr
- Network/Infrastructure: $55-80/hr

Note: Remote roles typically 5-10% lower. NYC/SF/Seattle premium of 15-25%. Government contracts 10-15% lower but more stable.

## Communication Style
- Professional, concise, and action-oriented
- Use industry terminology naturally (bench, hotlist, right-to-hire, prime vendor, tier-1, etc.)
- Provide specific, actionable recommendations
- Flag risks and concerns proactively
- Structure information clearly with priorities

Today's date: {today}
"""


class BenchSalesAgent:
    """The core AI agent for bench sales operations."""

    def __init__(self, api_key: Optional[str] = None):
        self._api_key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        self._client = anthropic.Anthropic(api_key=self._api_key) if self._api_key else None
        self._xray = XRaySearchEngine()
        self._url_builder = JobBoardURLBuilder()
        self._conversation: list[dict] = []

    @property
    def is_configured(self) -> bool:
        return bool(self._api_key)

    def _system_prompt(self) -> str:
        return BENCH_SALES_SYSTEM_PROMPT.format(today=date.today().isoformat())

    def chat(self, user_message: str, context: Optional[dict] = None) -> str:
        """Send a message to the agent and get a response."""
        if not self._client:
            return self._offline_response(user_message, context)

        enriched = user_message
        if context:
            enriched += f"\n\n[Context: {json.dumps(context, default=str)}]"

        self._conversation.append({"role": "user", "content": enriched})

        response = self._client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=4096,
            system=self._system_prompt(),
            messages=self._conversation,
        )

        assistant_msg = response.content[0].text
        self._conversation.append({"role": "assistant", "content": assistant_msg})

        return assistant_msg

    def analyze_consultant(self, consultant: ConsultantProfile) -> str:
        """Get strategic analysis of a consultant's profile and placement potential."""
        prompt = f"""Analyze this bench consultant's profile and provide:
1. Placement difficulty assessment (Easy/Medium/Hard)
2. Top 3 target job titles to search for
3. Recommended rate strategy
4. Key selling points for vendor submissions
5. Potential challenges and how to address them
6. Recommended geographies (if relocation is an option)

Consultant Profile:
{consultant.model_dump_json(indent=2)}

Bench Duration: {consultant.bench_duration_days()} days
"""
        return self.chat(prompt)

    def generate_search_strategy(self, consultant: ConsultantProfile) -> dict:
        """Generate comprehensive search strategy with queries and board links."""
        params = ConsultantSearchParams(
            job_title=consultant.job_title,
            primary_skills=consultant.primary_skills,
            secondary_skills=consultant.secondary_skills,
            location=consultant.current_location,
            remote_ok=consultant.remote_preference.lower() in ("remote", "hybrid"),
            visa_status=consultant.visa_status.value,
            employment_types=[et.value for et in consultant.employment_types_accepted],
            experience_years=consultant.total_experience_years,
            rate_range=consultant.rate_display(),
        )

        # Generate X-ray queries
        xray_queries = self._xray.generate_all_queries(params)
        hotlist_queries = self._xray.generate_hotlist_queries(params)
        role_synonyms = self._xray.get_role_synonyms(consultant.job_title)

        # Generate direct board links
        board_links = self._url_builder.all_boards(
            consultant.job_title, consultant.current_location
        )

        # Additional board links for synonym titles
        for synonym in role_synonyms[1:3]:  # Top 2 synonyms
            board_links.extend(
                self._url_builder.all_boards(synonym, consultant.current_location)
            )

        return {
            "xray_queries": xray_queries,
            "hotlist_queries": hotlist_queries,
            "board_links": board_links,
            "role_synonyms": role_synonyms,
            "search_params": params,
        }

    def evaluate_job_match(
        self,
        consultant: ConsultantProfile,
        job: JobRequirement,
    ) -> str:
        """AI evaluation of how well a consultant matches a job requirement."""
        prompt = f"""Evaluate this consultant-to-job match and provide:
1. Match Score (0-100%)
2. Matching skills (exact matches)
3. Transferable/related skills
4. Gaps that need to be addressed
5. Submission recommendation (Submit/Hold/Skip) with reasoning
6. Suggested resume tailoring points
7. Talking points for vendor call

Consultant:
{consultant.model_dump_json(indent=2)}

Job Requirement:
{job.model_dump_json(indent=2)}
"""
        return self.chat(prompt)

    def craft_submission_email(
        self,
        consultant: ConsultantProfile,
        job: JobRequirement,
        vendor: Optional[Vendor] = None,
    ) -> str:
        """Generate a professional submission email."""
        vendor_info = vendor.model_dump_json(indent=2) if vendor else "New vendor - no history"
        prompt = f"""Draft a professional bench sales submission email for this consultant to this requirement.

The email should:
- Be concise and professional (max 200 words body)
- Highlight the strongest matching skills first
- Include the consultant's one-liner summary
- Mention availability and rate (if appropriate)
- Include a clear call to action

Consultant:
{consultant.one_liner()}
Full Profile: {consultant.model_dump_json(indent=2)}

Job Requirement:
{job.model_dump_json(indent=2)}

Vendor Info:
{vendor_info}

Generate:
1. Subject line
2. Email body
3. Follow-up plan (when and how)
"""
        return self.chat(prompt)

    def generate_hotlist(self, consultants: list[ConsultantProfile]) -> str:
        """Generate a professional hotlist email for mass distribution."""
        one_liners = "\n".join(
            f"  {i+1}. {c.one_liner()}" for i, c in enumerate(consultants)
        )
        prompt = f"""Generate a professional bench sales hotlist email that I can send to vendors.

The hotlist should:
- Have an attention-grabbing subject line
- List each consultant in a clean, scannable format
- Include key details: Title, Skills, Experience, Visa, Location, Rate, Availability
- Have a professional sign-off with contact instructions
- Be formatted for email (not markdown)

Consultants on bench:
{one_liners}

Full profiles available upon request.
"""
        return self.chat(prompt)

    def market_rate_analysis(self, job_title: str, location: str, skills: list[str]) -> str:
        """Get market rate analysis for a specific role."""
        prompt = f"""Provide a detailed market rate analysis for:
- Role: {job_title}
- Location: {location}
- Key Skills: {', '.join(skills)}

Include:
1. Typical C2C hourly rate range
2. Bill rate expectations
3. C2C margin analysis
4. How location affects rates
5. Premium skills that command higher rates
6. Current market demand level
7. Negotiation advice
"""
        return self.chat(prompt)

    def _offline_response(self, message: str, context: Optional[dict] = None) -> str:
        """Provide useful responses even without API access."""
        msg_lower = message.lower()
        if "search" in msg_lower or "find" in msg_lower:
            return (
                "I can generate search queries and job board links for you even in offline mode. "
                "Use the 'Search for Roles' feature to get X-ray queries and direct links."
            )
        if "rate" in msg_lower:
            return (
                "For rate guidance in offline mode, refer to the built-in rate benchmarks. "
                "Configure ANTHROPIC_API_KEY for AI-powered rate analysis."
            )
        return (
            "I'm running in offline mode (no API key configured). "
            "Search queries, job board links, and data management work without an API key. "
            "Set ANTHROPIC_API_KEY in .env for AI-powered analysis and recommendations."
        )

    def clear_conversation(self):
        """Reset conversation history."""
        self._conversation.clear()
