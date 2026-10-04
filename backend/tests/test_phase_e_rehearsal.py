"""ASTRA - Phase E Judging Rehearsal, Verification & 100/100 Certification Tests.

Validates the full judging demo flow:
  1. Sovereign air-gapped health profile and disabled telemetry.
  2. Project 1 (synthetic_sample) honest denominator (6/6 files, 4 assessed, 66.67%).
  3. Zero-Secret private key redaction guarantee (AC-03 policy).
  4. Project 2 (multi-surface corpus) multi-surface discovery execution.
  5. Live owner context shift and Mosca inequality escalation ($X+Y > Z$).
  6. CycloneDX 1.6 CBOM export schema validity.
  7. End-to-end judging rehearsal runner execution.
"""

import io
import os
import sys
import zipfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.inventory.cbom_reconciliation import CBOMReconciliationEngine

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
BACKEND_DIR = Path(__file__).resolve().parent.parent

client = TestClient(app)


def create_sample_zip(folder_path: Path) -> io.BytesIO:
    """Create in-memory zip archive from folder."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(folder_path):
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("__pycache__", "node_modules")]
            for file in sorted(files):
                if file.startswith(".") or file in ("observations.json", "scan_manifest.json", "manifest.json", ".DS_Store"):
                    continue
                p = Path(root) / file
                arcname = str(p.relative_to(folder_path)).replace("\\", "/")
                zf.write(p, arcname=arcname)
    buf.seek(0)
    return buf


def test_system_health_and_air_gapped_profile():
    """Verify health endpoint advertises sovereign air-gapped operation without telemetry."""
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "pass"
    assert data["profile"] == "AIR_GAPPED_SOVEREIGN_ENTERPRISE"
    assert data["privacy_notice"]["telemetry_egress"] == "DISABLED"
    assert "FIPS 203 (ML-KEM)" in data["pqc_standards"]
    assert "FIPS 204 (ML-DSA)" in data["pqc_standards"]
    assert "FIPS 205 (SLH-DSA)" in data["pqc_standards"]


def test_project_1_synthetic_sample_ingestion_and_denominator():
    """Verify Project 1 ingestion yields truthful 6-file denominator and unified scan ID."""
    sample_dir = REPO_ROOT / "examples" / "synthetic_sample"
    assert sample_dir.is_dir()
    zip_buf = create_sample_zip(sample_dir)

    res = client.post("/api/v1/scans/upload", files={"file": ("synthetic_sample.zip", zip_buf, "application/zip")})
    assert res.status_code == 200
    data = res.json()
    scan_id = data["scan_id"]
    assert scan_id.startswith("scan-")

    summary = data["summary"]
    assert summary["total_files"] == 6
    assert summary["assessed_files"] == 4
    assert summary["coverage_percentage"] == 66.67
    assert data["asset_count"] in (13, 14)

    # Verify detail observation retrieval
    detail_res = client.get(f"/api/v1/scans/{scan_id}")
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert len(detail["observations"]) in (13, 14)


def test_zero_secret_guarantee_redaction():
    """Verify private key material uploaded is redacted per AC-03 policy."""
    priv_buf = io.BytesIO()
    with zipfile.ZipFile(priv_buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(
            "sensitive/hostile_key.pem",
            "-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA0r1Z2xTOP_SECRET_MATERIAL\n-----END RSA PRIVATE KEY-----\n",
        )
    priv_buf.seek(0)

    res = client.post("/api/v1/scans/upload", files={"file": ("privkey.zip", priv_buf, "application/zip")})
    assert res.status_code == 200
    scan_id = res.json()["scan_id"]

    detail_res = client.get(f"/api/v1/scans/{scan_id}")
    assert detail_res.status_code == 200
    observations = detail_res.json()["observations"]

    redacted_obs = [o for o in observations if o.get("redacted") is True]
    assert len(redacted_obs) >= 1
    for o in redacted_obs:
        assert "[REDACTED_PRIVATE_KEY_MATERIAL" in o.get("sanitized_excerpt", "")
        assert "TOP_SECRET_MATERIAL" not in o.get("sanitized_excerpt", "")


def test_multi_surface_corpus_ingestion():
    """Verify Project 2 (multi-surface corpus) processes cleanly with multi-surface observations."""
    corpus_dir = BACKEND_DIR / "tests" / "fixtures" / "corpus"
    assert corpus_dir.is_dir()
    zip_buf = create_sample_zip(corpus_dir)

    res = client.post("/api/v1/scans/upload", files={"file": ("corpus.zip", zip_buf, "application/zip")})
    assert res.status_code == 200
    data = res.json()
    assert data["scan_id"].startswith("scan-")
    assert data["summary"]["assessed_files"] > 10
    assert data["asset_count"] >= 10


def test_owner_context_shift_and_mosca_escalation():
    """Verify dynamic owner context shift live-recalculates Mosca inequality and escalates urgency."""
    sample_dir = REPO_ROOT / "examples" / "synthetic_sample"
    zip_buf = create_sample_zip(sample_dir)
    upload_res = client.post("/api/v1/scans/upload", files={"file": ("sample.zip", zip_buf, "application/zip")})
    assert upload_res.status_code == 200
    scan_id = upload_res.json()["scan_id"]
    initial_critical = upload_res.json()["summary"]["critical_urgency_count"]
    assert initial_critical in (1, 2)

    # Update owner context: X=8, Y=3, Z=8 -> 11 > 8 -> VIOLATION -> Critical
    context_payload = {
        "data_shelf_life_years": 8.0,
        "migration_time_years": 3.0,
        "quantum_threat_horizon_years": 8.0,
        "exposure_scope": "PUBLIC_INTERNET",
        "business_criticality": "HIGH",
    }
    update_res = client.put(f"/api/v1/scans/{scan_id}/context", json=context_payload)
    assert update_res.status_code == 200
    updated_data = update_res.json()

    assert updated_data["summary"]["critical_urgency_count"] >= 7
    assert updated_data["summary"]["critical_urgency_count"] > initial_critical
    evals = updated_data["risk_evaluations"]
    rsa_eval = next(e for e in evals if "rsa" in e["asset_id"].lower() or "RSA" in e.get("algorithm", ""))
    assert rsa_eval["urgency"] == "CRITICAL"
    assert rsa_eval["confidence_source"] == "OWNER_SUPPLIED"
    rec = rsa_eval["recommendation"]
    assert rec is not None
    assert "FIPS" in rec["target_standard_ref"] or "FIPS" in rec["target_standard_algorithm"]
    assert len(rec["performance_impact"]) > 0
    assert len(rec["bandwidth_and_cost"]) > 0


def test_cyclonedx_16_cbom_export_and_validation():
    """Verify CycloneDX 1.6 CBOM export conforms to schema specifications."""
    sample_dir = REPO_ROOT / "examples" / "synthetic_sample"
    zip_buf = create_sample_zip(sample_dir)
    upload_res = client.post("/api/v1/scans/upload", files={"file": ("sample.zip", zip_buf, "application/zip")})
    scan_id = upload_res.json()["scan_id"]

    export_res = client.get(f"/api/v1/scans/{scan_id}/export?format=cbom")
    assert export_res.status_code == 200
    cbom = export_res.json()

    assert cbom["bomFormat"] == "CycloneDX"
    assert cbom["specVersion"] == "1.6"
    assert len(cbom.get("components", [])) > 0

    validation = CBOMReconciliationEngine.validate_cbom(cbom)
    assert validation.is_valid is True
    assert len(validation.validation_errors) == 0
    assert validation.crypto_components_count > 0


def test_full_rehearsal_script_execution():
    """Verify that the judging rehearsal script executes all 6 steps with code 0."""
    from scripts.run_judging_rehearsal import run_rehearsal
    rc = run_rehearsal()
    assert rc == 0
