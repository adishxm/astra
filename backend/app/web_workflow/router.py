"""Worker 04 - Web Workflow API & Server-Persisted Cryptographic Audit (Phase B)."""

from fastapi import APIRouter, HTTPException, Body, Depends, Request
from typing import Any, Dict, List, Optional
from app.auth import verify_api_key, get_tenant_id, get_user_id
from app.inventory.models import CanonicalEvidence, AuditRecord, InventoryExport
from app.web_workflow.hardening import (
    AirGappedBundleManager,
    ProductionHealthEvaluator,
    ChainedAuditEvent,
)
from app.web_workflow.audit_store import GLOBAL_AUDIT_STORE

router = APIRouter(
    prefix="/api/v1/workflow",
    tags=["Worker 04"],
    dependencies=[Depends(verify_api_key)],
)


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


# Production extension endpoints (PROD-01 / Phase B)


@router.post("/audit/chain/append", response_model=ChainedAuditEvent)
def append_chained_audit(
    request: Request,
    action: str = Body(...),
    actor: str = Body(...),
    asset_id: Optional[str] = Body(None),
    details: Dict[str, Any] = Body(default_factory=dict),
):
    """Append a new tamper-evident event to the persistent server audit hash chain."""
    tenant_id = get_tenant_id(request)
    user_id = get_user_id(request)
    return GLOBAL_AUDIT_STORE.append_event(
        action=action,
        actor=actor,
        asset_id=asset_id,
        tenant_id=tenant_id,
        user_id=user_id,
        details=details,
    )


@router.get("/audit/chain")
def get_audit_chain(request: Request, scan_id: Optional[str] = None):
    """Retrieve full or scan-filtered cryptographic audit trail."""
    tenant_id = get_tenant_id(request)
    events = GLOBAL_AUDIT_STORE.get_events(tenant_id=tenant_id, scan_id=scan_id)
    return [e.model_dump() for e in events]


@router.get("/audit/chain/verify")
def verify_audit_chain(request: Request, scan_id: Optional[str] = None):
    """Verify cryptographic integrity of the persistent server audit log."""
    tenant_id = get_tenant_id(request)
    return GLOBAL_AUDIT_STORE.verify_chain(tenant_id=tenant_id, scan_id=scan_id)


@router.get("/audit/events/{scan_id}")
def get_scan_audit_events(scan_id: str, request: Request):
    """Retrieve all authoritative audit blocks bound to a specific scan execution."""
    tenant_id = get_tenant_id(request)
    events = GLOBAL_AUDIT_STORE.get_events(tenant_id=tenant_id, scan_id=scan_id)
    return [e.model_dump() for e in events]


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
