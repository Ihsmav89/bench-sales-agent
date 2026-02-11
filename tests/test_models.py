"""Tests for data models."""

from datetime import date

from bench_sales_agent.models.consultant import ConsultantProfile, VisaStatus
from bench_sales_agent.models.job import JobRequirement
from bench_sales_agent.models.vendor import Vendor


def _sample_consultant() -> ConsultantProfile:
    return ConsultantProfile(
        full_name="John Doe",
        email="john@example.com",
        phone="555-0100",
        current_location="Dallas, TX",
        job_title="Java Developer",
        primary_skills=["Java", "Spring Boot", "Microservices", "AWS", "Docker"],
        total_experience_years=8,
        us_experience_years=5,
        visa_status=VisaStatus.H1B,
        expected_rate_hourly=75,
        minimum_rate_hourly=65,
        bench_since=date(2025, 1, 15),
    )


def test_consultant_one_liner():
    c = _sample_consultant()
    liner = c.one_liner()
    assert "Java Developer" in liner
    assert "H1B" in liner
    assert "Dallas" in liner
    assert "$65-$75/hr" in liner


def test_consultant_search_keywords():
    c = _sample_consultant()
    keywords = c.search_keywords()
    assert "Java Developer" in keywords
    assert "Java" in keywords


def test_consultant_rate_display():
    c = _sample_consultant()
    assert c.rate_display() == "$65-$75/hr"

    c.minimum_rate_hourly = None
    assert c.rate_display() == "$75/hr"

    c.expected_rate_hourly = None
    assert c.rate_display() == "Negotiable"


def test_job_match_score():
    job = JobRequirement(
        title="Senior Java Developer",
        required_skills=["Java", "Spring Boot", "AWS", "Kubernetes", "SQL"],
    )
    # 3 of 5 match
    score = job.match_score(["Java", "Spring Boot", "AWS", "Docker", "React"])
    assert score == 60.0


def test_job_match_score_case_insensitive():
    job = JobRequirement(
        title="Python Dev",
        required_skills=["python", "Django", "PostgreSQL"],
    )
    score = job.match_score(["Python", "DJANGO", "postgresql"])
    assert score == 100.0


def test_vendor_placement_rate():
    v = Vendor(company_name="TechStaff LLC", total_submissions=10, total_placements=3)
    assert v.placement_rate() == 30.0

    v2 = Vendor(company_name="New Vendor")
    assert v2.placement_rate() == 0.0
