"""Vendor management routes."""

from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse

from ...models.vendor import Vendor, VendorTier
from ..app import get_db, get_templates

router = APIRouter()


@router.get("")
async def list_vendors(request: Request):
    db = get_db(request)
    templates = get_templates(request)
    vendors = db.list_vendors()
    return templates.TemplateResponse("vendors/list.html", {
        "request": request,
        "active": "vendors",
        "vendors": vendors,
    })


@router.get("/add")
async def add_form(request: Request):
    templates = get_templates(request)
    return templates.TemplateResponse("vendors/add.html", {
        "request": request,
        "active": "vendors",
        "tiers": list(VendorTier),
    })


@router.post("")
async def create_vendor(
    request: Request,
    company_name: str = Form(...),
    primary_contact_name: str = Form(""),
    primary_contact_email: str = Form(""),
    primary_contact_phone: str = Form(""),
    tier: str = Form("Tier-1 Vendor"),
):
    db = get_db(request)
    vendor = Vendor(
        company_name=company_name,
        primary_contact_name=primary_contact_name or None,
        primary_contact_email=primary_contact_email or None,
        primary_contact_phone=primary_contact_phone or None,
        tier=VendorTier(tier),
    )
    db.add_vendor(vendor)
    return RedirectResponse("/vendors", status_code=303)
