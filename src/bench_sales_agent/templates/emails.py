"""
Email template generation for bench sales operations.

Templates for common bench sales communications:
- Submission emails to vendors
- Hotlist distribution emails
- Follow-up emails
- Vendor outreach/introduction emails
"""

from __future__ import annotations

from ..models.consultant import ConsultantProfile
from ..models.job import JobRequirement, Submission


class EmailTemplates:
    """Pre-built email templates for bench sales workflows."""

    @staticmethod
    def submission_email(
        consultant: ConsultantProfile,
        job: JobRequirement,
        custom_note: str = "",
    ) -> dict[str, str]:
        """Generate a consultant submission email."""
        skills_match = ", ".join(consultant.primary_skills[:5])
        emp_types = "/".join(et.value for et in consultant.employment_types_accepted)

        subject = (
            f"Submission: {consultant.job_title} | "
            f"{consultant.total_experience_years:.0f}+ Yrs | "
            f"{consultant.visa_status.value} | "
            f"{consultant.current_location} | "
            f"{consultant.rate_display()}"
        )

        body = f"""Hi,

Please find below the profile of our consultant for the {job.title} requirement{f' (Job ID: {job.job_id_external})' if job.job_id_external else ''}.

Candidate Summary:
------------------
Name: {consultant.full_name}
Job Title: {consultant.job_title}
Experience: {consultant.total_experience_years:.0f}+ years (US: {consultant.us_experience_years:.0f}+ years)
Key Skills: {skills_match}
Visa Status: {consultant.visa_status.value}
Current Location: {consultant.current_location}
Relocation: {"Open to relocation" if consultant.relocation else "Local/Remote preferred"}
Work Mode: {consultant.remote_preference}
Employment Type: {emp_types}
Rate: {consultant.rate_display()}
Availability: {"Immediately" if consultant.notice_period_days == 0 else f"{consultant.notice_period_days} days notice"}

{f"Note: {custom_note}" if custom_note else ""}

Please find the resume attached. Looking forward to your feedback.

Best regards"""

        return {"subject": subject, "body": body}

    @staticmethod
    def hotlist_email(consultants: list[ConsultantProfile]) -> dict[str, str]:
        """Generate a hotlist distribution email."""
        today = __import__("datetime").date.today().strftime("%m/%d/%Y")

        subject = f"HOT LIST - Available IT Consultants - {today}"

        lines = []
        for i, c in enumerate(consultants, 1):
            lines.append(
                f"{i}. {c.job_title} | "
                f"{', '.join(c.primary_skills[:4])} | "
                f"{c.total_experience_years:.0f}+ Yrs | "
                f"{c.visa_status.value} | "
                f"{c.current_location} | "
                f"{c.rate_display()} | "
                f"{'Immediate' if c.notice_period_days == 0 else f'{c.notice_period_days}d notice'}"
            )

        body = f"""Hi,

Hope you are doing well!

We have the following consultants available for immediate placement. Please review and let us know if you have any matching requirements.

Available Consultants ({today}):
{"=" * 50}

{chr(10).join(lines)}

{"=" * 50}

All consultants have updated resumes available upon request. We work on both C2C and W2 basis.

If you have any requirements matching the above profiles, please share the job description and we can submit right away.

Best regards"""

        return {"subject": subject, "body": body}

    @staticmethod
    def followup_email(
        consultant: ConsultantProfile,
        job: JobRequirement,
        submission: Submission,
    ) -> dict[str, str]:
        """Generate a follow-up email for a submission."""
        days_since = "recently"
        if submission.submitted_at:
            from datetime import datetime
            delta = datetime.now() - submission.submitted_at
            days_since = f"{delta.days} days ago" if delta.days > 0 else "today"

        subject = f"Follow-up: {consultant.job_title} submission for {job.title}"

        body = f"""Hi,

I wanted to follow up on the profile I submitted {days_since} for the {job.title} position{f' (Job ID: {job.job_id_external})' if job.job_id_external else ''}.

Quick recap:
- Candidate: {consultant.job_title} with {consultant.total_experience_years:.0f}+ years experience
- Key Skills: {', '.join(consultant.primary_skills[:4])}
- Visa: {consultant.visa_status.value}
- Availability: Immediate

The consultant is still available and very interested in this opportunity. Could you please provide an update on the submission status?

Happy to schedule a call or provide any additional information needed.

Best regards"""

        return {"subject": subject, "body": body}

    @staticmethod
    def vendor_introduction_email(skills_offered: list[str]) -> dict[str, str]:
        """Generate an introduction email to a new vendor."""
        skills_str = ", ".join(skills_offered)

        subject = "IT Staffing Partnership Opportunity"

        body = f"""Hi,

I hope this email finds you well. I am reaching out to explore a potential staffing partnership.

We are an IT staffing company with a strong bench of consultants specializing in:
{skills_str}

Our consultants are:
- Available for immediate placement
- Based across the United States
- Available on C2C, W2, and Contract-to-Hire basis
- Experienced with major VMS platforms (Fieldglass, Beeline)

We have successfully placed consultants with Fortune 500 companies and government agencies. We maintain high standards for our consultants and ensure smooth onboarding.

If you have any open requirements matching our expertise, please feel free to share. We would be happy to submit qualified profiles promptly.

Looking forward to a mutually beneficial partnership.

Best regards"""

        return {"subject": subject, "body": body}
