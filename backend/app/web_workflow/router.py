"""Worker 04 - Web Workflow API."""

from fastapi import APIRouter, HTTPException, Body
from typing import Any, Dict, List, Optional
from app.inventory.models import CanonicalEvidence, AuditRecord, InventoryExport
from app.web_workflow.hardening import (
    AirGappedBundleManager,
    LocalReviewEventLog,
    ProductionHealthEvaluator,
    LocalReviewEvent,
)

router = APIRouter(prefix="/api/v1/workflow", tags=["Worker 04"])

# In-memory chain for demo and verification
_GLOBAL_AUDIT_CHAIN: List[LocalReviewEvent] = []


@router.post("/audit", response_model=AuditRecord)
def create_audit_record(record: AuditRecord):
    """Review and audit history."""
    if not record.reason:
        raise HTTPException(status_code=400, detail="Reason is required")
    record.actor = None
    return record


# Production extension endpoints (PROD-01) removed per Phase F0.
