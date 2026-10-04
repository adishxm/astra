"""Worker 04 - Web Workflow API."""

from fastapi import APIRouter, HTTPException, Body, Depends
from typing import Any, Dict, List, Optional
from app.auth import verify_api_key
from app.inventory.models import CanonicalEvidence, AuditRecord, InventoryExport
from app.web_workflow.hardening import (
    AirGappedBundleManager,
    TamperEvidentAuditChainer,
    ProductionHealthEvaluator,
    ChainedAuditEvent,
)

router = APIRouter(
    prefix="/api/v1/workflow",
    tags=["Worker 04"],
    dependencies=[Depends(verify_api_key)],
)

# In-memory chain for demo and verification
_GLOBAL_AUDIT_CHAIN: List[ChainedAuditEvent] = []


@router.get("/evidence/{asset_id}", response_model=List[CanonicalEvidence])
def get_evidence_drilldown(asset_id: str):
    """Evidence drill-down for a specific asset."""
    return []


@router.post("/audit", response_model=AuditRecord)
def create_audit_record(record: AuditRecord):
    """Review and audit history."""
    if not record.reason:
        raise HTTPException(status_code=400, detail="Reason is required")
    record.actor = None
    return record


@router.get("/export", response_model=InventoryExport)
def get_export():
    """Sanitized export."""
    return InventoryExport(assets=[], relationships=[], audit_trail=[])


# Production extension endpoints (PROD-01)


@router.post("/audit/chain/append", response_model=ChainedAuditEvent)
def append_chained_audit(
    action: str = Body(...),
    actor: str = Body(...),
    asset_id: Optional[str] = Body(None),
    details: Dict[str, Any] = Body(default_factory=dict),
):
    """Append a new tamper-evident event to the running audit hash chain."""
    return TamperEvidentAuditChainer.append_event(
        chain=_GLOBAL_AUDIT_CHAIN,
        action=action,
        actor=actor,
        asset_id=asset_id,
        details=details,
    )


@router.get("/audit/chain/verify")
def verify_audit_chain():
    """Verify integrity of the tamper-evident audit log."""
    return TamperEvidentAuditChainer.verify_chain(_GLOBAL_AUDIT_CHAIN)


@router.post("/offline/bundle/verify")
def verify_offline_bundle(payload: Dict[str, Any] = Body(...)):
    """Verify integrity of an offline air-gapped rule/intel update package."""
    manifest = payload.get("manifest", {})
    raw_content = payload.get("raw_content", "").encode("utf-8")
    signer = payload.get("signer_key_id", "")
    res = AirGappedBundleManager.verify_bundle(manifest, raw_content, signer)
    if not res.get("valid"):
        raise HTTPException(status_code=400, detail=res.get("reason"))
    return res


@router.get("/health/production")
def get_production_health():
    """Evaluate production readiness and air-gapped security profile."""
    return ProductionHealthEvaluator.evaluate_readiness()
