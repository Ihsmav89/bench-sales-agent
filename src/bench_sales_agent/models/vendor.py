"""Vendor/Prime vendor and client models."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class VendorTier(str, Enum):
    DIRECT_CLIENT = "Direct Client"
    PRIME_VENDOR = "Prime Vendor"
    TIER_1 = "Tier-1 Vendor"
    TIER_2 = "Tier-2 Vendor"
    IMPLEMENTATION_PARTNER = "Implementation Partner"


class VendorRelationship(str, Enum):
    ACTIVE = "Active"
    NEW = "New"
    DORMANT = "Dormant"
    BLACKLISTED = "Blacklisted"


class Vendor(BaseModel):
    """Represents a staffing vendor, prime vendor, or direct client."""

    id: Optional[str] = None
    company_name: str
    tier: VendorTier = VendorTier.TIER_1

    # Contacts
    primary_contact_name: Optional[str] = None
    primary_contact_email: Optional[str] = None
    primary_contact_phone: Optional[str] = None
    additional_contacts: list[dict] = Field(default_factory=list)

    # Business details
    website: Optional[str] = None
    specializations: list[str] = Field(default_factory=list)
    payment_terms: Optional[str] = None  # "Net 30", "Net 45", etc.
    msp_vms: Optional[str] = None  # Fieldglass, Beeline, etc.

    # Track record
    relationship: VendorRelationship = VendorRelationship.NEW
    total_submissions: int = 0
    total_placements: int = 0
    avg_response_time_hours: Optional[float] = None
    reliability_score: float = Field(default=5.0, ge=0, le=10)

    notes: str = ""
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    def placement_rate(self) -> float:
        if self.total_submissions == 0:
            return 0.0
        return (self.total_placements / self.total_submissions) * 100
