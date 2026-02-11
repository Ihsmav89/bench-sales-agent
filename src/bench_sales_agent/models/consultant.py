"""Consultant profile model for bench employees."""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class VisaStatus(str, Enum):
    USC = "US Citizen"
    GC = "Green Card"
    H1B = "H1B"
    H1B_TRANSFER = "H1B Transfer"
    H4_EAD = "H4 EAD"
    L1 = "L1"
    L2_EAD = "L2 EAD"
    OPT = "OPT"
    OPT_STEM = "OPT STEM"
    CPT = "CPT"
    TN = "TN"
    E3 = "E3"


class EmploymentType(str, Enum):
    W2 = "W2"
    C2C = "Corp-to-Corp"
    C2H = "Contract-to-Hire"
    FULLTIME = "Full-Time"
    C2C_W2 = "C2C/W2"


class ConsultantProfile(BaseModel):
    """Represents an IT consultant currently on bench."""

    id: Optional[str] = None
    full_name: str
    email: str
    phone: str
    current_location: str = Field(description="City, State format")
    relocation: bool = False
    relocation_preferences: list[str] = Field(default_factory=list)
    remote_preference: str = Field(default="Remote", description="Remote/Hybrid/Onsite")

    # Professional details
    job_title: str = Field(description="Primary role, e.g., Java Developer, Data Engineer")
    primary_skills: list[str] = Field(description="Top 5-7 skills")
    secondary_skills: list[str] = Field(default_factory=list)
    total_experience_years: float
    us_experience_years: float = 0
    summary: str = Field(default="", description="2-3 line professional summary")

    # Immigration
    visa_status: VisaStatus
    visa_expiry: Optional[date] = None
    employer_on_visa: Optional[str] = None

    # Employment
    employment_types_accepted: list[EmploymentType] = Field(
        default_factory=lambda: [EmploymentType.W2, EmploymentType.C2C]
    )
    expected_rate_hourly: Optional[float] = None
    minimum_rate_hourly: Optional[float] = None

    # Availability
    bench_since: Optional[date] = None
    available_from: date = Field(default_factory=date.today)
    notice_period_days: int = 0

    # Documents
    resume_path: Optional[str] = None
    has_updated_resume: bool = False

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    def bench_duration_days(self) -> int:
        if self.bench_since:
            return (date.today() - self.bench_since).days
        return 0

    def search_keywords(self) -> list[str]:
        """Generate optimal search keywords from profile."""
        keywords = [self.job_title] + self.primary_skills[:5]
        return keywords

    def rate_display(self) -> str:
        if self.expected_rate_hourly and self.minimum_rate_hourly:
            return f"${self.minimum_rate_hourly:.0f}-${self.expected_rate_hourly:.0f}/hr"
        if self.expected_rate_hourly:
            return f"${self.expected_rate_hourly:.0f}/hr"
        return "Negotiable"

    def one_liner(self) -> str:
        """One-line summary for hotlists and quick sharing."""
        visa = self.visa_status.value
        loc = self.current_location
        exp = f"{self.total_experience_years:.0f}+ yrs"
        skills = ", ".join(self.primary_skills[:4])
        return f"{self.job_title} | {skills} | {exp} | {visa} | {loc} | {self.rate_display()}"
