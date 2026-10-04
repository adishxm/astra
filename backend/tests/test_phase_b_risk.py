"""ASTRA - Phase B Defensible Risk Models & Grounded Recommendations Verification Suite.

Validates:
1. Every RiskEvaluation contains non-null ContextFactors and confidence_source.
2. Recommendations are grounded in NIST FIPS/NSA citations with performance and latency trade-offs.
3. Owner context can be updated via PUT /api/v1/scans/{scan_id}/context.
4. Live recalculation dynamically shifts Mosca urgency (X + Y > Z) from DEFAULT_ASSUMPTION to OWNER_SUPPLIED.
"""

import io
import zipfile
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.scan_service import GLOBAL_SCAN_STORE
from app.risk.models import BusinessCriticality, ContextFactors, ExposureScope


client = TestClient(app)


def get_test_scan_id() -> str:
    """Helper to upload synthetic sample and return scan_id."""
    sample_dir = Path("examples/synthetic_sample").resolve()
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_p in sorted(sample_dir.glob("*")):
            if file_p.is_file():
                zf.write(file_p, arcname=file_p.name)
    zip_buffer.seek(0)

    res = client.post(
        "/api/v1/scans/upload",
        files={"file": ("synthetic_sample.zip", zip_buffer, "application/zip")},
    )
    assert res.status_code == 200
    return res.json()["scan_id"]


def test_phase_b_risk_evaluations_contain_grounded_context_and_recommendations():
    """Verify Phase B: Risk evaluations include context factors, confidence source, and grounded PQC citations."""
    scan_id = get_test_scan_id()

    # 1. Fetch risk from API
    res = client.get(f"/api/v1/scans/{scan_id}/risk")
    assert res.status_code == 200
    risk_data = res.json()

    evals = risk_data["risk_evaluations"]
    assert len(evals) > 0, "Expected non-empty risk evaluations"

    found_grounded_pqc = False
    for r in evals:
        # Assert non-null context factors
        assert "context" in r and r["context"] is not None
        assert "data_shelf_life_years" in r["context"]
        assert "migration_duration_years" in r["context"]
        assert "confidence_source" in r
        assert r["confidence_source"] in ("DEFAULT_ASSUMPTION", "OWNER_SUPPLIED")

        # Check algorithm recommendations
        algo = r["algorithm"].upper()
        if "RSA" in algo or "ECDH" in algo:
            assert r["recommendation"] is not None
            rec = r["recommendation"]
            assert "target_standard_ref" in rec
            assert "NIST FIPS" in rec["target_standard_ref"] or "NIST" in rec["target_standard_ref"]
            assert "performance_impact" in rec
            assert len(rec["compatibility_gaps"]) > 0
            found_grounded_pqc = True

    assert found_grounded_pqc, "Expected at least one quantum-vulnerable algorithm with grounded PQC recommendation"


def test_phase_b_owner_context_update_and_live_mosca_recalculation():
    """Verify Phase B: PUT /api/v1/scans/{scan_id}/context updates owner context and recalculates Mosca deadline."""
    scan_id = get_test_scan_id()

    # 1. Submit owner-verified context where X=8.0, Y=3.0 under Z=8.0 (X + Y = 11 > 8 => VIOLATED)
    payload = {
        "data_shelf_life_years": 8.0,
        "migration_duration_years": 3.0,
        "exposure": 5,  # PUBLIC_FACING
        "criticality": 5,  # MISSION_CRITICAL
        "dependency_reach": 4,
        "quantum_threat_horizon_years": 8.0,
    }

    res_put = client.put(f"/api/v1/scans/{scan_id}/context", json=payload)
    assert res_put.status_code == 200, f"Context update failed: {res_put.text}"
    put_data = res_put.json()

    assert put_data["status"] == "updated"
    assert put_data["context"]["is_user_enriched"] is True
    assert put_data["context"]["context_source"] == "OWNER_SUPPLIED"
    assert put_data["context"]["data_shelf_life_years"] == 8.0

    # Assert that quantum vulnerable assets escalated to CRITICAL urgency due to Mosca violation
    updated_evals = put_data["risk_evaluations"]
    rsa_evals = [e for e in updated_evals if "RSA" in e["algorithm"].upper()]
    assert len(rsa_evals) > 0
    for rsa_e in rsa_evals:
        assert rsa_e["mosca_condition_violated"] is True
        assert rsa_e["urgency"] == "CRITICAL"
        assert rsa_e["confidence_source"] == "OWNER_SUPPLIED"

    # 2. Verify persisted record in GLOBAL_SCAN_STORE
    rec = GLOBAL_SCAN_STORE.get(scan_id)
    assert rec is not None
    persisted_evals = rec.risk_evaluations
    persisted_rsa = [e for e in persisted_evals if "RSA" in e.algorithm.upper()][0]
    assert persisted_rsa.mosca_condition_violated is True
    assert persisted_rsa.context.is_user_enriched is True
    assert persisted_rsa.context.context_source == "OWNER_SUPPLIED"
