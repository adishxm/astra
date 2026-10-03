"""Worker 04 - Web Workflow API."""

from fastapi import APIRouter, HTTPException
from typing import List
from app.inventory.models import CanonicalEvidence, AuditRecord, InventoryExport

router = APIRouter(prefix="/api/v1/workflow", tags=["Worker 04"])

@router.get("/evidence/{asset_id}", response_model=List[CanonicalEvidence])
def get_evidence_drilldown(asset_id: str):
    """Evidence drill-down for a specific asset."""
    # Stubbed data access - integration boundary
    return []

@router.post("/audit", response_model=AuditRecord)
def create_audit_record(record: AuditRecord):
    """Review and audit history."""
    if not record.reason:
        raise HTTPException(status_code=400, detail="Reason is required")
    # Fake security constraint documented: actor is None for unauthenticated
    record.actor = None 
    return record

@router.get("/export", response_model=InventoryExport)
def get_export():
    """Sanitized export."""
    return InventoryExport(assets=[], relationships=[], audit_trail=[])
