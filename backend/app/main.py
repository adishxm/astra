"""ASTRA - Master FastAPI Application Entry Point.

Serves:
- REST API for cryptographic scans, evidence drilldown, Mosca risk analysis, and CBOM exports
- Air-gapped health probes and signed rule bundle verification
- Interactive Web Dashboard for live cryptographic visualization
"""

import os
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, File, HTTPException, UploadFile, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.services.scan_service import GLOBAL_SCAN_SERVICE, GLOBAL_SCAN_STORE
from app.web_workflow.router import router as workflow_router
from app.inventory.models import CanonicalEvidence, InventoryExport
from app.inventory.cbom_reconciliation import CBOMReconciliationEngine

app = FastAPI(
    title="ASTRA - Enterprise Cryptographic Discovery & Analysis Tool",
    description=(
        "Provenance-aware, coverage-accounted cryptographic discovery, "
        "Mosca-horizon risk evaluation, and post-quantum migration engine (SIH26164 ECDAT)."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
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
        "profile": "AIR_GAPPED_SOVEREIGN_ENTERPRISE",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "pqc_standards": ["FIPS 203 (ML-KEM)", "FIPS 204 (ML-DSA)", "FIPS 205 (SLH-DSA)"],
    }


@app.post("/api/v1/scans/upload")
async def upload_and_scan(file: UploadFile = File(...)):
    """Upload an authorized repository archive (.zip, .tar.gz) and execute complete scan pipeline."""
    valid_suffixes = {".zip", ".tar", ".gz", ".tgz", ".bz2"}
    filename = file.filename or "uploaded_archive.zip"
    suffix = Path(filename).suffix.lower()

    if not any(filename.lower().endswith(ext) for ext in [".zip", ".tar", ".tar.gz", ".tgz", ".tar.bz2"]):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported archive format. Expected one of: .zip, .tar, .tar.gz, .tar.bz2",
        )

    # Save uploaded bytes to a secure temporary file
    temp_dir = tempfile.mkdtemp(prefix="astra_upload_")
    temp_archive = os.path.join(temp_dir, filename)

    try:
        with open(temp_archive, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Run unified scan pipeline
        record = GLOBAL_SCAN_SERVICE.run_scan_on_archive(
            archive_path=temp_archive,
            target_name=filename,
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
        raise HTTPException(status_code=500, detail=f"Scan execution failed: {str(e)}")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


@app.post("/api/v1/scans/directory")
def scan_directory(payload: Dict[str, Any] = Body(...)):
    """Trigger a cryptographic discovery scan on a local directory."""
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
def list_scans():
    """List all previously executed scans."""
    return GLOBAL_SCAN_STORE.list_all()


@app.get("/api/v1/scans/{scan_id}")
def get_scan(scan_id: str):
    """Retrieve complete scan record by ID."""
    record = GLOBAL_SCAN_STORE.get(scan_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Scan ID not found: {scan_id}")
    return record if isinstance(record, dict) else record.to_dict()


@app.get("/api/v1/scans/{scan_id}/findings")
def get_scan_findings(scan_id: str):
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
def get_scan_coverage(scan_id: str):
    """Retrieve truthful coverage report for a scan."""
    record = GLOBAL_SCAN_STORE.get(scan_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Scan ID not found: {scan_id}")
    data = record if isinstance(record, dict) else record.to_dict()
    return data.get("coverage", {})


@app.get("/api/v1/scans/{scan_id}/risk")
def get_scan_risk(scan_id: str):
    """Retrieve Mosca risk calculations and candidate PQC backlog for a scan."""
    record = GLOBAL_SCAN_STORE.get(scan_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Scan ID not found: {scan_id}")
    data = record if isinstance(record, dict) else record.to_dict()
    return {
        "scan_id": scan_id,
        "risk_evaluations": data.get("risk_evaluations", []),
        "backlog_items": data.get("backlog_items", []),
    }


@app.get("/api/v1/scans/{scan_id}/export")
def get_scan_export(scan_id: str, format: str = Query("cyclonedx")):
    """Export CycloneDX 1.6 Cryptographic Bill of Materials (CBOM) for a scan."""
    record = GLOBAL_SCAN_STORE.get(scan_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Scan ID not found: {scan_id}")
    data = record if isinstance(record, dict) else record.to_dict()
    cbom = data.get("cbom_data", {})
    return cbom


# Override workflow stub endpoints with persistent scan data
@app.get("/api/v1/workflow/evidence/{asset_id}", response_model=List[CanonicalEvidence])
def get_evidence_drilldown(asset_id: str):
    """Evidence drill-down for a specific asset across all executed scans."""
    evidences = []
    # Search in-memory cache and persisted records
    for s_meta in GLOBAL_SCAN_STORE.list_all():
        rec = GLOBAL_SCAN_STORE.get(s_meta["scan_id"])
        data = rec if isinstance(rec, dict) else rec.to_dict()
        for asset in data.get("canonical_assets", []):
            if asset.get("asset_id") == asset_id:
                for obs in asset.get("observations", []):
                    evidences.append(obs)
    return evidences


@app.get("/api/v1/workflow/export", response_model=InventoryExport)
def get_latest_export():
    """Sanitized export of the latest scan findings."""
    all_scans = GLOBAL_SCAN_STORE.list_all()
    if not all_scans:
        return InventoryExport(assets=[], relationships=[], audit_trail=[])

    latest_id = all_scans[0]["scan_id"]
    rec = GLOBAL_SCAN_STORE.get(latest_id)
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
