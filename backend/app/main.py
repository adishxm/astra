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

# Security & environment policies
ASTRA_HOSTED_MODE = os.getenv("ASTRA_HOSTED_MODE", "false").lower() in ("1", "true", "yes")
ASTRA_ALLOW_DIRECTORY_SCAN = os.getenv(
    "ASTRA_ALLOW_DIRECTORY_SCAN", "false" if ASTRA_HOSTED_MODE else "true"
).lower() in ("1", "true", "yes")

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
    # Safe default: restrict to local development origins instead of wildcard
    allowed_origins = ["http://127.0.0.1:8000", "http://localhost:8000", "http://127.0.0.1:5173", "http://localhost:5173"]
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
        "hosted_mode": ASTRA_HOSTED_MODE,
        "directory_scan_permitted": ASTRA_ALLOW_DIRECTORY_SCAN,
        "privacy_notice": {
            "processing": "local_only",
            "telemetry_egress": "none",
            "retention": "ephemeral_unless_saved",
            "secrets_handling": "redacted",
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "pqc_standards": ["FIPS 203 (ML-KEM)", "FIPS 204 (ML-DSA)", "FIPS 205 (SLH-DSA)"],
    }


@app.post("/api/v1/scans/upload")
async def upload_and_scan(file: UploadFile = File(...)):
    """Upload an authorized repository archive (.zip, .tar.gz) and execute complete scan pipeline."""
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

    # Save uploaded bytes to a secure temporary file with active byte streaming limit (100 MB max)
    max_upload_size = 100 * 1024 * 1024
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
def get_scan_risk(
    scan_id: str,
    horizon: Optional[float] = Query(None, description="Quantum threat horizon Z in years (scenario assumption)"),
    shelf_life: Optional[float] = Query(None, description="Data secrecy shelf-life X in years"),
    migration: Optional[float] = Query(None, description="Migration duration Y in years"),
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


@app.get("/api/v1/scans/{scan_id}/export")
def get_scan_export(scan_id: str, format: str = Query("cyclonedx")):
    """Export CycloneDX 1.6 Cryptographic Bill of Materials (CBOM) for a scan."""
    record = GLOBAL_SCAN_STORE.get(scan_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Scan ID not found: {scan_id}")
    data = record if isinstance(record, dict) else record.to_dict()
    cbom = data.get("cbom_data", {})
    return cbom





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
