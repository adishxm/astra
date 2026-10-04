"""ASTRA - Phase A Integrity & Traceability Verification Suite.

Validates:
1. Unified scan_id propagation across manifest, coverage, snapshot, CBOM, and record.
2. Honest file denominator accounting (exact 6 files for synthetic sample, 4 assessed, 66.67% coverage).
3. Zero sidecar pollution from intake extraction.
4. Correct API-to-Dashboard contract alignment (no NaN coverage, no missing start_line, accurate file counts).
"""

import io
import uuid
import zipfile
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.scan_service import GLOBAL_SCAN_STORE, ScanService


client = TestClient(app)


def create_synthetic_sample_zip() -> io.BytesIO:
    """Pack examples/synthetic_sample into an in-memory zip archive."""
    candidates = [
        Path("examples/synthetic_sample").resolve(),
        Path(__file__).resolve().parent.parent.parent / "examples" / "synthetic_sample",
        Path(__file__).resolve().parent.parent / "examples" / "synthetic_sample",
    ]
    sample_dir = next((c for c in candidates if c.exists() and c.is_dir()), None)
    assert sample_dir is not None, "examples/synthetic_sample directory must exist"

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_p in sorted(sample_dir.glob("*")):
            if file_p.is_file():
                zf.write(file_p, arcname=file_p.name)
    zip_buffer.seek(0)
    return zip_buffer


def test_phase_a_scan_id_and_denominator_integrity():
    """Verify Phase A: Single scan_id propagation and truthful 6/6 file denominators."""
    zip_bytes = create_synthetic_sample_zip()

    response = client.post(
        "/api/v1/scans/upload",
        files={"file": ("synthetic_sample.zip", zip_bytes, "application/zip")},
    )
    assert response.status_code == 200, f"Upload failed: {response.text}"
    data = response.json()

    scan_id = data["scan_id"]
    assert scan_id.startswith("scan-"), f"Expected scan- prefix, got {scan_id}"

    # 1. Inspect persisted record
    rec = GLOBAL_SCAN_STORE.get(scan_id)
    assert rec is not None, f"ScanRecord {scan_id} not found in store"

    # Assert single scan_id invariant across all layers
    assert rec.scan_id == scan_id
    assert rec.manifest.scan_id == scan_id
    assert rec.coverage.scan_id == scan_id
    assert rec.snapshot.scan_id == scan_id
    expected_cbom_urn = f"urn:uuid:{uuid.uuid5(uuid.NAMESPACE_URL, scan_id)}"
    assert rec.cbom_data["serialNumber"] == expected_cbom_urn

    # 2. Assert truthful file denominators: synthetic sample has exactly 6 files
    assert rec.manifest.total_files_in_archive == 6
    assert rec.coverage.total_files_in_archive == 6
    assert rec.coverage.total_assessed_files == 4
    assert rec.coverage.overall_coverage_percentage == 66.67
    assert rec.coverage_summary["total_files"] == 6
    assert rec.coverage_summary["assessed_files"] == 4

    # Assert summary in to_dict() matches
    rec_dict = rec.to_dict()
    assert rec_dict["summary"]["total_files"] == 6
    assert rec_dict["summary"]["assessed_files"] == 4
    assert rec_dict["summary"]["coverage_percentage"] == 66.67

    # 3. Assert observation metadata
    assert len(rec.observations) > 0
    for obs in rec.observations:
        if obs.start_line is not None:
            assert obs.start_line >= 1
        assert obs.sanitized_excerpt is not None and len(obs.sanitized_excerpt) > 0


def test_phase_a_api_contract_for_dashboard():
    """Verify Phase A: API endpoints return exact fields required by frontend loadScanData."""
    zip_bytes = create_synthetic_sample_zip()

    # Upload
    res_upload = client.post(
        "/api/v1/scans/upload",
        files={"file": ("synthetic_sample.zip", zip_bytes, "application/zip")},
    )
    assert res_upload.status_code == 200
    scan_id = res_upload.json()["scan_id"]

    # 1. GET /api/v1/scans/{scan_id}
    res_scan = client.get(f"/api/v1/scans/{scan_id}")
    assert res_scan.status_code == 200
    scan_json = res_scan.json()
    assert "coverage" in scan_json
    assert scan_json["coverage"]["overall_coverage_percentage"] == 66.67
    assert scan_json["summary"]["total_files"] == 6
    assert scan_json["summary"]["assessed_files"] == 4
    assert scan_json["summary"]["coverage_percentage"] == 66.67

    # 2. GET /api/v1/scans/{scan_id}/findings
    res_findings = client.get(f"/api/v1/scans/{scan_id}/findings")
    assert res_findings.status_code == 200
    findings_json = res_findings.json()
    assert "canonical_assets" in findings_json
    for asset in findings_json["canonical_assets"]:
        assert len(asset["observations"]) > 0
        for obs in asset["observations"]:
            assert "start_line" in obs
            assert "sanitized_excerpt" in obs

    # 3. GET /api/v1/scans/{scan_id}/risk
    res_risk = client.get(f"/api/v1/scans/{scan_id}/risk")
    assert res_risk.status_code == 200
    risk_json = res_risk.json()
    assert "risk_evaluations" in risk_json

    # 4. GET /api/v1/scans/{scan_id}/export?format=cyclonedx
    res_cbom = client.get(f"/api/v1/scans/{scan_id}/export?format=cyclonedx")
    assert res_cbom.status_code == 200
    cbom_json = res_cbom.json()
    assert cbom_json["bomFormat"] == "CycloneDX"
    assert cbom_json["specVersion"] == "1.6"
    assert cbom_json["serialNumber"] == f"urn:uuid:{uuid.uuid5(uuid.NAMESPACE_URL, scan_id)}"
