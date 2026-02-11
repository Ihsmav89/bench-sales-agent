"""Job requirement and submission models."""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class JobPriority(str, Enum):
    HOT = "Hot"  # Immediate need, interview this week
    WARM = "Warm"  # Active requirement, 1-2 weeks
    REGULAR = "Regular"  # Standard pipeline


class SubmissionStatus(str, Enum):
    IDENTIFIED = "Identified"
    SUBMITTED = "Submitted"
    VENDOR_SCREEN = "Vendor Screen"
    CLIENT_REVIEW = "Client Review"
    INTERVIEW_SCHEDULED = "Interview Scheduled"
    INTERVIEW_DONE = "Interview Done"
    SELECTED = "Selected"
    ONBOARDED = "Onboarded"
    REJECTED = "Rejected"
    NO_RESPONSE = "No Response"
    CLOSED = "Closed"


class JobRequirement(BaseModel):
    """A contract job requirement found through search."""

    id: Optional[str] = None
    title: str
    client_name: Optional[str] = None
    vendor_name: Optional[str] = None
    vendor_contact_name: Optional[str] = None
    vendor_contact_email: Optional[str] = None
    vendor_contact_phone: Optional[str] = None

    # Job details
    description: str = ""
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    experience_required_years: Optional[float] = None
    duration_months: Optional[int] = None

    # Location
    location: str = ""
    remote_option: str = "Onsite"  # Remote/Hybrid/Onsite

    # Compensation
    bill_rate: Optional[float] = None
    pay_rate: Optional[float] = None
    employment_type: str = "C2C"

    # Visa requirements
    visa_accepted: list[str] = Field(
        default_factory=lambda: ["USC", "GC", "H1B", "OPT", "CPT", "H4 EAD"]
    )

    # Source tracking
    source_url: Optional[str] = None
    source_platform: Optional[str] = None  # dice, indeed, linkedin, email, etc.
    job_id_external: Optional[str] = None
    posted_date: Optional[date] = None

    priority: JobPriority = JobPriority.REGULAR
    is_active: bool = True
    notes: str = ""

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    def match_score(self, consultant_skills: list[str]) -> float:
        """Calculate basic skill match percentage against a consultant."""
        if not self.required_skills:
            return 0.0
        consultant_lower = {s.lower() for s in consultant_skills}
        required_lower = {s.lower() for s in self.required_skills}
        matches = consultant_lower & required_lower
        return (len(matches) / len(required_lower)) * 100 if required_lower else 0.0


class Submission(BaseModel):
    """Tracks a consultant submission to a job requirement."""

    id: Optional[str] = None
    consultant_id: str
    job_id: str
    vendor_name: str

    status: SubmissionStatus = SubmissionStatus.IDENTIFIED
    submitted_at: Optional[datetime] = None
    rate_submitted: Optional[float] = None
    resume_version: Optional[str] = None

    # Interview tracking
    interview_datetime: Optional[datetime] = None
    interview_type: Optional[str] = None  # Phone, Video, In-person
    interview_feedback: Optional[str] = None

    # Follow-up
    last_followup_date: Optional[date] = None
    followup_count: int = 0
    next_followup_date: Optional[date] = None

    notes: str = ""
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
