"""
TinyDB-based local database for consultants, jobs, vendors, and submissions.

Uses TinyDB for simplicity - no external database server needed.
Data is stored in JSON files under the data/ directory.
"""

from __future__ import annotations

import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from tinydb import Query, TinyDB

from ..models.consultant import ConsultantProfile
from ..models.job import JobRequirement, Submission
from ..models.vendor import Vendor


class Database:
    """Local JSON-based database for all bench sales data."""

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = os.path.join(
                os.path.dirname(
                    os.path.dirname(
                        os.path.dirname(
                            os.path.dirname(__file__)
                        )
                    )
                ),
                "data",
                "bench_sales.json",
            )
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._db = TinyDB(db_path, indent=2)
        self._consultants = self._db.table("consultants")
        self._jobs = self._db.table("jobs")
        self._vendors = self._db.table("vendors")
        self._submissions = self._db.table("submissions")

    # ── Consultants ──────────────────────────────────────────────────────

    def add_consultant(self, consultant: ConsultantProfile) -> str:
        consultant.id = consultant.id or str(uuid.uuid4())[:8]
        consultant.created_at = datetime.now()
        consultant.updated_at = datetime.now()
        self._consultants.insert(consultant.model_dump(mode="json"))
        return consultant.id

    def get_consultant(self, consultant_id: str) -> Optional[ConsultantProfile]:
        q = Query()
        result = self._consultants.search(q.id == consultant_id)
        return ConsultantProfile(**result[0]) if result else None

    def list_consultants(self, on_bench_only: bool = False) -> list[ConsultantProfile]:
        if on_bench_only:
            q = Query()
            results = self._consultants.search(q.bench_since.exists())
        else:
            results = self._consultants.all()
        return [ConsultantProfile(**r) for r in results]

    def update_consultant(self, consultant_id: str, **updates) -> bool:
        q = Query()
        updates["updated_at"] = datetime.now().isoformat()
        updated = self._consultants.update(updates, q.id == consultant_id)
        return len(updated) > 0

    def delete_consultant(self, consultant_id: str) -> bool:
        q = Query()
        removed = self._consultants.remove(q.id == consultant_id)
        return len(removed) > 0

    # ── Jobs ─────────────────────────────────────────────────────────────

    def add_job(self, job: JobRequirement) -> str:
        job.id = job.id or str(uuid.uuid4())[:8]
        job.created_at = datetime.now()
        job.updated_at = datetime.now()
        self._jobs.insert(job.model_dump(mode="json"))
        return job.id

    def get_job(self, job_id: str) -> Optional[JobRequirement]:
        q = Query()
        result = self._jobs.search(q.id == job_id)
        return JobRequirement(**result[0]) if result else None

    def list_jobs(self, active_only: bool = True) -> list[JobRequirement]:
        if active_only:
            q = Query()
            results = self._jobs.search(q.is_active == True)  # noqa: E712
        else:
            results = self._jobs.all()
        return [JobRequirement(**r) for r in results]

    def search_jobs(self, skills: list[str]) -> list[JobRequirement]:
        """Search jobs matching any of the given skills."""
        q = Query()
        results = self._jobs.search(
            q.required_skills.test(
                lambda req_skills: any(
                    s.lower() in [rs.lower() for rs in req_skills]
                    for s in skills
                )
            )
        )
        return [JobRequirement(**r) for r in results]

    def update_job(self, job_id: str, **updates) -> bool:
        q = Query()
        updates["updated_at"] = datetime.now().isoformat()
        updated = self._jobs.update(updates, q.id == job_id)
        return len(updated) > 0

    # ── Vendors ──────────────────────────────────────────────────────────

    def add_vendor(self, vendor: Vendor) -> str:
        vendor.id = vendor.id or str(uuid.uuid4())[:8]
        vendor.created_at = datetime.now()
        vendor.updated_at = datetime.now()
        self._vendors.insert(vendor.model_dump(mode="json"))
        return vendor.id

    def get_vendor(self, vendor_id: str) -> Optional[Vendor]:
        q = Query()
        result = self._vendors.search(q.id == vendor_id)
        return Vendor(**result[0]) if result else None

    def list_vendors(self, active_only: bool = False) -> list[Vendor]:
        if active_only:
            q = Query()
            results = self._vendors.search(q.relationship == "Active")
        else:
            results = self._vendors.all()
        return [Vendor(**r) for r in results]

    def find_vendor_by_name(self, name: str) -> Optional[Vendor]:
        q = Query()
        results = self._vendors.search(
            q.company_name.test(lambda n: name.lower() in n.lower())
        )
        return Vendor(**results[0]) if results else None

    def update_vendor(self, vendor_id: str, **updates) -> bool:
        q = Query()
        updates["updated_at"] = datetime.now().isoformat()
        updated = self._vendors.update(updates, q.id == vendor_id)
        return len(updated) > 0

    # ── Submissions ──────────────────────────────────────────────────────

    def add_submission(self, submission: Submission) -> str:
        submission.id = submission.id or str(uuid.uuid4())[:8]
        submission.created_at = datetime.now()
        submission.updated_at = datetime.now()
        self._submissions.insert(submission.model_dump(mode="json"))
        return submission.id

    def get_submissions_for_consultant(self, consultant_id: str) -> list[Submission]:
        q = Query()
        results = self._submissions.search(q.consultant_id == consultant_id)
        return [Submission(**r) for r in results]

    def get_submissions_for_job(self, job_id: str) -> list[Submission]:
        q = Query()
        results = self._submissions.search(q.job_id == job_id)
        return [Submission(**r) for r in results]

    def list_pending_followups(self) -> list[Submission]:
        """Get submissions that need follow-up."""
        q = Query()
        results = self._submissions.search(
            (q.status == "Submitted")
            | (q.status == "Vendor Screen")
            | (q.status == "Client Review")
        )
        return [Submission(**r) for r in results]

    def update_submission(self, submission_id: str, **updates) -> bool:
        q = Query()
        updates["updated_at"] = datetime.now().isoformat()
        updated = self._submissions.update(updates, q.id == submission_id)
        return len(updated) > 0

    # ── Stats ────────────────────────────────────────────────────────────

    def get_stats(self) -> dict:
        return {
            "consultants_on_bench": len(self.list_consultants(on_bench_only=True)),
            "total_consultants": len(self._consultants),
            "active_jobs": len(self.list_jobs(active_only=True)),
            "total_jobs": len(self._jobs),
            "total_vendors": len(self._vendors),
            "active_submissions": len(self.list_pending_followups()),
            "total_submissions": len(self._submissions),
        }
