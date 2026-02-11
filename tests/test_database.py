"""Tests for the database layer."""

import os
import tempfile

from bench_sales_agent.data.database import Database
from bench_sales_agent.models.consultant import ConsultantProfile, VisaStatus
from bench_sales_agent.models.job import JobRequirement
from bench_sales_agent.models.vendor import Vendor


def _temp_db() -> Database:
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    os.unlink(path)  # TinyDB will create it
    return Database(path)


def _sample_consultant() -> ConsultantProfile:
    return ConsultantProfile(
        full_name="Jane Smith",
        email="jane@example.com",
        phone="555-0200",
        current_location="Austin, TX",
        job_title="Data Engineer",
        primary_skills=["Python", "Spark", "AWS", "Snowflake"],
        total_experience_years=6,
        visa_status=VisaStatus.GC,
    )


def test_add_and_get_consultant():
    db = _temp_db()
    c = _sample_consultant()
    cid = db.add_consultant(c)
    assert cid

    retrieved = db.get_consultant(cid)
    assert retrieved is not None
    assert retrieved.full_name == "Jane Smith"
    assert retrieved.job_title == "Data Engineer"


def test_list_consultants():
    db = _temp_db()
    db.add_consultant(_sample_consultant())
    consultants = db.list_consultants()
    assert len(consultants) == 1


def test_add_and_search_jobs():
    db = _temp_db()
    job = JobRequirement(
        title="Senior Python Developer",
        required_skills=["Python", "Django", "AWS", "PostgreSQL"],
        vendor_name="TechCorp",
        location="Remote",
    )
    jid = db.add_job(job)
    assert jid

    results = db.search_jobs(["Python", "React"])
    assert len(results) == 1
    assert results[0].title == "Senior Python Developer"


def test_add_vendor():
    db = _temp_db()
    vendor = Vendor(
        company_name="StaffPro Inc",
        primary_contact_email="hr@staffpro.com",
    )
    vid = db.add_vendor(vendor)
    assert vid

    found = db.find_vendor_by_name("staffpro")
    assert found is not None
    assert found.company_name == "StaffPro Inc"


def test_stats():
    db = _temp_db()
    db.add_consultant(_sample_consultant())
    db.add_job(JobRequirement(title="Dev", required_skills=["Python"]))
    db.add_vendor(Vendor(company_name="Vendor1"))

    stats = db.get_stats()
    assert stats["total_consultants"] == 1
    assert stats["total_jobs"] == 1
    assert stats["total_vendors"] == 1
