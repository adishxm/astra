"""ASTRA - Master FastAPI Application Entry Point.

Serves:
- REST API for cryptographic scans, evidence drilldown, Mosca risk analysis, and CBOM exports
- Air-gapped health probes and signed rule bundle verification
- Interactive Web Dashboard for live cryptographic visualization
"""

import os
import re
import shutil
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, File, HTTPException, UploadFile, Query, Body, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.services.scan_service import GLOBAL_SCAN_SERVICE, GLOBAL_SCAN_STORE
from app.web_workflow.router import router as workflow_router
from app.inventory.models import CanonicalEvidence, InventoryExport
from app.inventory.cbom_reconciliation import CBOMReconciliationEngine


from app.auth import (
    is_hosted_mode,
    is_directory_scan_allowed,
    get_max_upload_size,
    check_upload_rate_limit,
    verify_api_key,
    get_tenant_id,
    get_user_id,
    _UPLOAD_RATE_LIMIT_STORE,
)

app = FastAPI(
    title="ASTRA - Enterprise Cryptographic Discovery & Analysis Tool",
    description=(
        "ASTRA by Team HEXARK is an open-source cryptographic discovery and CBOM prototype "
        "aligned with SIH26164 (ECDAT). Scan source, manifests, configs and certificates, "
        "evaluate Mosca PQC migration risk, and export CycloneDX 1.6 CBOM."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS configuration: default allow local origins or configured env var; disable credentials for wildcard
allowed_origins_env = os.getenv("ASTRA_CORS_ORIGINS", "")
if allowed_origins_env:
    allowed_origins = [o.strip() for o in allowed_origins_env.split(",") if o.strip()]
    allow_credentials = True
else:
    # Safe default: wildcard without credentials to satisfy W3C/browser security restrictions
    allowed_origins = ["*"]
    allow_credentials = False

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Workflow Router
app.include_router(workflow_router)


@app.get("/health")
@app.get("/api/v1/health")
def get_health():
    """System health check and operational status."""
    return {
        "status": "pass",
        "service": "ASTRA Cryptographic Engine",
        "version": "1.0.0",
        "team": "HEXARK",
        "profile": "AIR_GAPPED_SOVEREIGN_ENTERPRISE",
        "hosted_mode": is_hosted_mode(),
        "authentication_enforced": bool(os.getenv("ASTRA_API_KEY")) or is_hosted_mode(),
        "directory_scan_permitted": is_directory_scan_allowed(),
        "privacy_notice": {
            "processing": "LOCAL_CPU_ONLY",
            "telemetry_egress": "DISABLED",
            "retention": "PERSISTED_LOCALLY_IN_ASTRA_STORE",
            "secrets_handling": "AUTOMATIC_PRIVATE_KEY_REDACTION",
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "pqc_standards": ["FIPS 203 (ML-KEM)", "FIPS 204 (ML-DSA)", "FIPS 205 (SLH-DSA)"],
    }


@app.post("/api/v1/scans/upload")
async def upload_and_scan(
    request: Request,
    file: UploadFile = File(...),
    _: None = Depends(verify_api_key),
):
    """Upload an authorized repository archive (.zip, .tar.gz) and execute complete scan pipeline."""
    check_upload_rate_limit(request)
    valid_suffixes = {".zip", ".tar", ".gz", ".tgz", ".bz2"}
    raw_filename = file.filename or "uploaded_archive.zip"

    # Safely normalize client-provided filename: strip directory traversal / paths
    safe_filename = Path(raw_filename).name
    safe_filename = re.sub(r"[^a-zA-Z0-9_.-]", "_", safe_filename) or "uploaded_archive.zip"

    if not any(safe_filename.lower().endswith(ext) for ext in [".zip", ".tar", ".tar.gz", ".tgz", ".tar.bz2"]):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported archive format. Expected one of: .zip, .tar, .tar.gz, .tar.bz2",
        )

    # Save uploaded bytes to a secure temporary file with active byte streaming limit
    max_upload_size = get_max_upload_size()
    if getattr(file, "size", None) is not None and file.size > max_upload_size:
        raise HTTPException(
            status_code=413,
            detail=f"Uploaded archive exceeds maximum limit of {max_upload_size // (1024 * 1024)} MB",
        )

    temp_dir = tempfile.mkdtemp(prefix="astra_upload_")
    temp_archive = os.path.join(temp_dir, safe_filename)

    try:
        bytes_written = 0
        with open(temp_archive, "wb") as buffer:
            while chunk := await file.read(65536):
                bytes_written += len(chunk)
                if bytes_written > max_upload_size:
                    raise HTTPException(
                        status_code=413,
                        detail=f"Uploaded archive exceeds maximum limit of {max_upload_size // (1024 * 1024)} MB",
                    )
                buffer.write(chunk)

        # Run unified scan pipeline
        record = GLOBAL_SCAN_SERVICE.run_scan_on_archive(
            archive_path=temp_archive,
            target_name=safe_filename,
            tenant_id=get_tenant_id(request),
            user_id=get_user_id(request),
        )
        return {
            "status": "completed",
            "scan_id": record.scan_id,
            "target_name": record.target_name,
            "created_at": record.created_at.isoformat(),
            "asset_count": len(record.canonical_assets),
            "coverage_percentage": record.coverage.overall_coverage_percentage,
            "clean_state_label": record.coverage.scan_status_label,
            "dna_hash": record.snapshot.cryptographic_dna_hash,
            "canonical_assets": [a.model_dump() for a in record.canonical_assets],
            "summary": record.to_dict()["summary"],
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scan execution failed: {str(e)}")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


@app.post("/api/v1/scans/directory")
def scan_directory(
    request: Request,
    payload: Dict[str, Any] = Body(...),
    _: None = Depends(verify_api_key),
):
    """Trigger a cryptographic discovery scan on a local directory."""
    if not is_directory_scan_allowed():
        raise HTTPException(
            status_code=403,
            detail="Arbitrary directory scanning is disabled in hosted mode. Please upload an authorized archive (.zip, .tar.gz) instead.",
        )

    path_str = payload.get("path")
    if not path_str:
        raise HTTPException(status_code=400, detail="Path parameter is required")

    target_dir = Path(path_str).resolve()
    if not target_dir.exists() or not target_dir.is_dir():
        raise HTTPException(status_code=404, detail=f"Directory not found: {path_str}")

    try:
        record = GLOBAL_SCAN_SERVICE.run_scan_on_directory(
            directory_path=str(target_dir),
            target_name=payload.get("target_name"),
            tenant_id=get_tenant_id(request),
            user_id=get_user_id(request),
        )
        return {
            "status": "completed",
            "scan_id": record.scan_id,
            "target_name": record.target_name,
            "created_at": record.created_at.isoformat(),
            "asset_count": len(record.canonical_assets),
            "coverage_percentage": record.coverage.overall_coverage_percentage,
            "clean_state_label": record.coverage.scan_status_label,
            "dna_hash": record.snapshot.cryptographic_dna_hash,
            "canonical_assets": [a.model_dump() for a in record.canonical_assets],
            "summary": record.to_dict()["summary"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Directory scan failed: {str(e)}")


@app.get("/api/v1/scans")
def list_scans(request: Request, _: None = Depends(verify_api_key)):
    """List all previously executed scans."""
    tenant_id = get_tenant_id(request)
    return GLOBAL_SCAN_STORE.list_all(tenant_id=tenant_id)


@app.get("/api/v1/scans/{scan_id}")
def get_scan(scan_id: str, request: Request, _: None = Depends(verify_api_key)):
    """Retrieve complete scan record by ID."""
    record = GLOBAL_SCAN_STORE.get(scan_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Scan ID not found: {scan_id}")
    tenant_id = get_tenant_id(request)
    rec_tenant = getattr(record, "tenant_id", None) if not isinstance(record, dict) else record.get("tenant_id")
    if tenant_id and tenant_id != "default" and rec_tenant and rec_tenant != "default" and rec_tenant != tenant_id:
        raise HTTPException(status_code=404, detail=f"Scan ID not found: {scan_id}")
    return record if isinstance(record, dict) else record.to_dict()


@app.get("/api/v1/scans/{scan_id}/findings")
def get_scan_findings(scan_id: str, _: None = Depends(verify_api_key)):
    """Retrieve canonical assets and observations for a scan."""
    record = GLOBAL_SCAN_STORE.get(scan_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Scan ID not found: {scan_id}")
    data = record if isinstance(record, dict) else record.to_dict()
    observations = []
    if isinstance(record, dict):
        for a in record.get("canonical_assets", []):
            observations.extend(a.get("observations", []))
    else:
        observations = [o.model_dump() for o in record.observations]

    return {
        "scan_id": scan_id,
        "asset_count": data.get("asset_count", 0),
        "canonical_assets": data.get("canonical_assets", []),
        "observations": observations,
    }


@app.get("/api/v1/scans/{scan_id}/coverage")
def get_scan_coverage(scan_id: str, _: None = Depends(verify_api_key)):
    """Retrieve truthful coverage report for a scan."""
    record = GLOBAL_SCAN_STORE.get(scan_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Scan ID not found: {scan_id}")
    data = record if isinstance(record, dict) else record.to_dict()
    return data.get("coverage", {})


@app.get("/api/v1/scans/{scan_id}/risk")
def get_scan_risk(
    scan_id: str,
    horizon: Optional[float] = Query(None, description="Quantum threat horizon Z in years (scenario assumption)"),
    shelf_life: Optional[float] = Query(None, description="Data secrecy shelf-life X in years"),
    migration: Optional[float] = Query(None, description="Migration duration Y in years"),
    _: None = Depends(verify_api_key),
):
    """Retrieve Mosca risk calculations or dynamically re-evaluate under custom scenario assumptions."""
    record = GLOBAL_SCAN_STORE.get(scan_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Scan ID not found: {scan_id}")
    data = record if isinstance(record, dict) else record.to_dict()

    if horizon is not None or shelf_life is not None or migration is not None:
        from app.risk.models import RiskScenario, ContextFactors
        from app.risk.scorer import RiskScorer
        from app.risk.backlog import BacklogBuilder
        from app.discovery.models import Observation

        scenario = RiskScenario(
            quantum_threat_horizon_years=horizon if horizon is not None else 8.0
        )
        context = ContextFactors(
            data_shelf_life_years=shelf_life if shelf_life is not None else 5.0,
            migration_duration_years=migration if migration is not None else 2.0,
            is_user_enriched=True,
            context_source="OWNER_SUPPLIED",
        )
        scorer = RiskScorer(scenario=scenario)
        observations = []
        if isinstance(record, dict):
            for a in record.get("canonical_assets", []):
                for obs_dict in a.get("observations", []):
                    try:
                        observations.append(Observation(**obs_dict))
                    except Exception:
                        pass
        elif hasattr(record, "observations"):
            observations = record.observations

        evals = [scorer.evaluate_observation(obs, context).model_dump() for obs in observations]
        backlog_builder = BacklogBuilder(scenario=scenario)
        backlog_obj = backlog_builder.generate_backlog(observations, scan_id)
        backlog_items = [task.model_dump() for task in backlog_obj.tasks]

        return {
            "scan_id": scan_id,
            "scenario": scenario.model_dump(),
            "context": context.model_dump(),
            "risk_evaluations": evals,
            "backlog_items": backlog_items,
        }

    return {
        "scan_id": scan_id,
        "risk_evaluations": data.get("risk_evaluations", []),
        "backlog_items": data.get("backlog_items", []),
    }


@app.put("/api/v1/scans/{scan_id}/context")
def update_scan_owner_context(
    scan_id: str,
    request: Request,
    payload: Dict[str, Any] = Body(...),
    _: None = Depends(verify_api_key),
):
    """Enrich a scan with verified owner context (data lifetime X, migration Y, exposure, criticality)."""
    record = GLOBAL_SCAN_STORE.get(scan_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Scan ID not found: {scan_id}")

    tenant_id = get_tenant_id(request)
    rec_tenant = getattr(record, "tenant_id", None) if not isinstance(record, dict) else record.get("tenant_id")
    if tenant_id and tenant_id != "default" and rec_tenant and rec_tenant != "default" and rec_tenant != tenant_id:
        raise HTTPException(status_code=404, detail=f"Scan ID not found: {scan_id}")

    from app.risk.models import ContextFactors, RiskScenario
    from app.services.scan_service import GLOBAL_SCAN_SERVICE

    try:
        ctx_data = dict(payload)
        ctx_data["is_user_enriched"] = True
        ctx_data["context_source"] = "OWNER_SUPPLIED"
        
        # If exposure or criticality passed as int or string, parse them
        context = ContextFactors(**ctx_data)
        
        scenario = None
        if "quantum_threat_horizon_years" in payload:
            scenario = RiskScenario(quantum_threat_horizon_years=float(payload["quantum_threat_horizon_years"]))

        updated_record = GLOBAL_SCAN_SERVICE.update_scan_context(
            scan_id=scan_id,
            context=context,
            scenario=scenario,
        )
        return {
            "status": "updated",
            "scan_id": scan_id,
            "context": context.model_dump(),
            "summary": updated_record.to_dict()["summary"],
            "risk_evaluations": [r.model_dump() for r in updated_record.risk_evaluations],
            "backlog_items": updated_record.backlog_items,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid context parameters: {str(e)}")


@app.get("/api/v1/scans/{scan_id}/export")
def get_scan_export(
    scan_id: str,
    request: Request,
    format: str = Query("cyclonedx"),
    _: None = Depends(verify_api_key),
):
    """Export CycloneDX 1.6 Cryptographic Bill of Materials (CBOM) for a scan."""
    record = GLOBAL_SCAN_STORE.get(scan_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Scan ID not found: {scan_id}")

    tenant_id = get_tenant_id(request)
    rec_tenant = getattr(record, "tenant_id", None) if not isinstance(record, dict) else record.get("tenant_id")
    if tenant_id and tenant_id != "default" and rec_tenant and rec_tenant != "default" and rec_tenant != tenant_id:
        raise HTTPException(status_code=404, detail=f"Scan ID not found: {scan_id}")

    try:
        from app.web_workflow.audit_store import GLOBAL_AUDIT_STORE
        GLOBAL_AUDIT_STORE.append_event(
            event_type="CBOM_EXPORTED",
            actor=get_user_id(request),
            payload={
                "scan_id": scan_id,
                "format": format,
                "target_name": getattr(record, "target_name", "unknown") if not isinstance(record, dict) else record.get("target_name", "unknown"),
            },
            tenant_id=tenant_id,
            scan_id=scan_id,
        )
    except Exception:
        pass

    data = record if isinstance(record, dict) else record.to_dict()
    cbom = data.get("cbom_data", {})
    return cbom


# Override workflow stub endpoints with persistent scan data
@app.get("/api/v1/workflow/evidence/{asset_id}", response_model=List[CanonicalEvidence])
def get_evidence_drilldown(
    asset_id: str,
    _: None = Depends(verify_api_key),
):
    """Evidence drill-down for a specific asset across all executed scans."""
    evidences = []
    # Search in-memory cache and persisted records
    for s_meta in GLOBAL_SCAN_STORE.list_all():
        rec = GLOBAL_SCAN_STORE.get(s_meta["scan_id"])
        if not rec:
            continue
        data = rec if isinstance(rec, dict) else rec.to_dict()
        for asset in data.get("canonical_assets", []):
            if asset.get("asset_id") == asset_id:
                for obs in asset.get("observations", []):
                    evidences.append(obs)
    return evidences


@app.get("/api/v1/workflow/export", response_model=InventoryExport)
def get_latest_export(_: None = Depends(verify_api_key)):
    """Sanitized export of the latest scan findings."""
    all_scans = GLOBAL_SCAN_STORE.list_all()
    if not all_scans:
        return InventoryExport(assets=[], relationships=[], audit_trail=[])

    latest_id = all_scans[0]["scan_id"]
    rec = GLOBAL_SCAN_STORE.get(latest_id)
    if not rec:
        return InventoryExport(assets=[], relationships=[], audit_trail=[])
    data = rec if isinstance(rec, dict) else rec.to_dict()

    assets = []
    for a in data.get("canonical_assets", []):
        assets.append(a)

    return InventoryExport(
        assets=assets,
        relationships=[],
        audit_trail=[],
        cbom_profile="CycloneDX-1.6-CBOM",
    )


# Mount Web Dashboard Static Assets
STATIC_DIR = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if not STATIC_DIR.exists():
    STATIC_DIR = Path(__file__).resolve().parent / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)

if (STATIC_DIR / "index.html").exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    @app.get("/")
    def serve_dashboard():
        """Serve the interactive ASTRA Web Dashboard."""
        return FileResponse(STATIC_DIR / "index.html")
else:
    @app.get("/")
    def root_info():
        return {
            "name": "ASTRA - Enterprise Cryptographic Discovery & Analysis Tool",
            "version": "1.0.0",
            "docs": "/docs",
            "health": "/health",
            "cli": "astra scan <path>",
        }
