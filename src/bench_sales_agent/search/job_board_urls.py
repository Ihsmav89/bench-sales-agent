"""
Direct job board URL builders for native platform searches.

Instead of only X-raying through Google, this module generates direct
search URLs for each job board's native search interface.
"""

from __future__ import annotations

import urllib.parse
from dataclasses import dataclass


@dataclass
class JobBoardLink:
    """A direct link to a job board search."""

    platform: str
    url: str
    description: str


class JobBoardURLBuilder:
    """Generates direct search URLs for major job boards."""

    @staticmethod
    def dice(title: str, location: str = "", radius: int = 50) -> JobBoardLink:
        params = {
            "q": f"{title} c2c",
            "location": location,
            "radius": str(radius),
            "filters.employmentType": "CONTRACT",
        }
        url = "https://www.dice.com/jobs?" + urllib.parse.urlencode(params)
        return JobBoardLink("Dice", url, f"Dice: {title} C2C near {location}")

    @staticmethod
    def indeed(title: str, location: str = "", radius: int = 50) -> JobBoardLink:
        params = {
            "q": f"{title} c2c corp to corp",
            "l": location,
            "radius": str(radius),
            "jt": "contract",
        }
        url = "https://www.indeed.com/jobs?" + urllib.parse.urlencode(params)
        return JobBoardLink("Indeed", url, f"Indeed: {title} C2C near {location}")

    @staticmethod
    def linkedin(title: str, location: str = "") -> JobBoardLink:
        params = {
            "keywords": f"{title} c2c corp to corp",
            "location": location or "United States",
            "f_JT": "C",  # Contract
        }
        url = "https://www.linkedin.com/jobs/search/?" + urllib.parse.urlencode(params)
        return JobBoardLink("LinkedIn", url, f"LinkedIn: {title} C2C")

    @staticmethod
    def ziprecruiter(title: str, location: str = "") -> JobBoardLink:
        params = {
            "search": f"{title} c2c corp to corp",
            "location": location or "United States",
        }
        url = "https://www.ziprecruiter.com/jobs/search?" + urllib.parse.urlencode(params)
        return JobBoardLink("ZipRecruiter", url, f"ZipRecruiter: {title} C2C")

    @staticmethod
    def monster(title: str, location: str = "") -> JobBoardLink:
        params = {
            "q": f"{title} c2c corp to corp",
            "where": location or "United States",
        }
        url = "https://www.monster.com/jobs/search/?" + urllib.parse.urlencode(params)
        return JobBoardLink("Monster", url, f"Monster: {title} C2C")

    @staticmethod
    def careerbuilder(title: str, location: str = "") -> JobBoardLink:
        params = {
            "keywords": f"{title} c2c corp to corp",
            "location": location,
        }
        url = "https://www.careerbuilder.com/jobs?" + urllib.parse.urlencode(params)
        return JobBoardLink("CareerBuilder", url, f"CareerBuilder: {title} C2C")

    @staticmethod
    def glassdoor(title: str, location: str = "") -> JobBoardLink:
        params = {
            "sc.keyword": f"{title} c2c corp to corp",
            "locT": "N",
            "locKeyword": location or "United States",
        }
        url = "https://www.glassdoor.com/Job/jobs.htm?" + urllib.parse.urlencode(params)
        return JobBoardLink("Glassdoor", url, f"Glassdoor: {title} C2C")

    @staticmethod
    def techfetch(title: str) -> JobBoardLink:
        params = {"q": title, "jtype": "C2C,Contract"}
        url = "https://www.techfetch.com/job/search?" + urllib.parse.urlencode(params)
        return JobBoardLink("TechFetch", url, f"TechFetch: {title} C2C/contract")

    @classmethod
    def all_boards(cls, title: str, location: str = "") -> list[JobBoardLink]:
        """Generate search URLs for all supported job boards."""
        return [
            cls.dice(title, location),
            cls.indeed(title, location),
            cls.linkedin(title, location),
            cls.ziprecruiter(title, location),
            cls.monster(title, location),
            cls.careerbuilder(title, location),
            cls.glassdoor(title, location),
            cls.techfetch(title),
        ]
