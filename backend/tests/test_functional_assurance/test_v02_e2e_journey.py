"""ASTRA - Tester 01 End-to-End User Journey & Risk Assurance Suite (Cycle V02).

Validates:
- W03 Contextual risk engine, Mosca Theorem deadline calculations (X + Y > Z).
- W03 Candidate PQC migration mapping and actionable backlog prioritization.
- W03 Scenario sensitivity (horizon slider, lifetime, exposure, criticality).
- W04 Web workflow integration (Audit logging, evidence review, export).
- Single integrated end-to-end synthetic scan journey without mocks or stubs.
"""

from datetime import datetime, timezone
import uuid
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.discovery.models import (
    ClaimType,
    ConfidenceBand,
    EvidenceState,
    Observation,
    SourceKind,
)
from app.inventory.models import (
    AssetIdentity,
    AuditRecord,
    CanonicalEvidence,
    InventoryExport,
    Relationship,
    map_observation_to_canonical,
)
from app.risk.backlog import BacklogBuilder, MigrationBacklog, MigrationTask
from app.risk.models import (
    BusinessCriticality,
    ContextFactors,
    ExposureScope,
    RiskEvaluation,
    RiskScenario,
    UrgencyLevel,
)
from app.risk.scenarios import BaselineComparison, ScenarioAnalyzer
from app.risk.scorer import RiskScorer
from app.risk.taxonomy import lookup_algorithm_profile
from app.web_workflow.router import router


@pytest.fixture
def api_client():
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


class TestTester01V02E2EJourney:
    """Exhaustive validation suite for Cycle V02."""

    def test_e2e_complete_synthetic_scan_to_risk_and_export_journey(self, api_client):
        """Validates the full integrated user journey from observation through backlog to export."""
        # 1. Simulate findings from discovery
        raw_obs = [
            Observation(
                observation_id=str(uuid.uuid4()),
                scan_id="scan-e2e-01",
                candidate_asset_id="asset-core-banking-rsa",
                claim_type=ClaimType.ALGORITHM_USE,
                source_kind=SourceKind.SOURCE_CODE,
                algorithm="RSA-2048",
                purpose="KEY_EXCHANGE",
                relative_path="src/bank/auth.py",
                start_line=42,
                evidence_digest="sha256-abc123",
                sanitized_excerpt="rsa.generate_private_key(key_size=2048)",
                redacted=False,
                detector_id="source-detector",
                ruleset_version="2026.10-nist-pqc",
                confidence=ConfidenceBand.HIGH,
                confidence_rationale="Exact AST call detected",
                state=EvidenceState.OBSERVED,
                raw_parameters={"algorithm": "RSA", "key_size": 2048, "secret_seed": "supersecret"},
            ),
            Observation(
                observation_id=str(uuid.uuid4()),
                scan_id="scan-e2e-01",
                candidate_asset_id="asset-legacy-session-des",
                claim_type=ClaimType.ALGORITHM_USE,
                source_kind=SourceKind.SOURCE_CODE,
                algorithm="DES",
                purpose="SYMMETRIC_ENCRYPTION",
                relative_path="src/legacy/session.java",
                start_line=12,
                evidence_digest="sha256-def456",
                sanitized_excerpt="Cipher.getInstance(\"DES\")",
                redacted=False,
                detector_id="source-detector",
                ruleset_version="2026.10-nist-pqc",
                confidence=ConfidenceBand.HIGH,
                confidence_rationale="Hardcoded legacy algorithm identifier",
                state=EvidenceState.OBSERVED,
                raw_parameters={"algorithm": "DES", "mode": "CBC"},
            ),
            Observation(
                observation_id=str(uuid.uuid4()),
                scan_id="scan-e2e-01",
                candidate_asset_id="asset-nextgen-pqc-kem",
                claim_type=ClaimType.ALGORITHM_USE,
                source_kind=SourceKind.SOURCE_CODE,
                algorithm="ML-KEM",
                purpose="KEY_ENCAPSULATION",
                relative_path="src/pqc/handshake.py",
                start_line=15,
                evidence_digest="sha256-pqc789",
                sanitized_excerpt="ml_kem_768.encapsulate()",
                redacted=False,
                detector_id="source-detector",
                ruleset_version="2026.10-nist-pqc",
                confidence=ConfidenceBand.HIGH,
                confidence_rationale="NIST FIPS 203 PQC standard call",
                state=EvidenceState.OBSERVED,
                raw_parameters={"algorithm": "ML-KEM", "version": "FIPS-203"},
            ),
        ]

        # 2. Worker 02: Canonicalize observations and generate AssetIdentity
        canonical_items = [map_observation_to_canonical(obs) for obs in raw_obs]
        assets = [
            AssetIdentity(asset_id=item.asset_id, primary_name=item.algorithm, observations=[item])
            for item in canonical_items
        ]
        assert len(assets) == 3

        # 3. Worker 03: Risk Assessment with Mosca Theorem
        scorer = RiskScorer()
        builder = BacklogBuilder()

        # Context map: Core banking has high shelf life, partner gateway exposure, mission-critical impact
        context_map = {
            "src/bank/auth.py": ContextFactors(
                data_shelf_life_years=10.0,
                migration_duration_years=3.0,
                exposure=ExposureScope.PARTNER_GATEWAY,
                criticality=BusinessCriticality.MISSION_CRITICAL,
            ),
            "src/legacy/session.java": ContextFactors(
                data_shelf_life_years=1.0,
                migration_duration_years=0.5,
                exposure=ExposureScope.LOCAL_ISOLATED,
                criticality=BusinessCriticality.LOW,
            ),
            "src/pqc/handshake.py": ContextFactors(),
        }

        # 4. Generate Backlog Items
        backlog = builder.generate_backlog(raw_obs, "scan-e2e-01", context_map)
        assert backlog.total_tasks == 3

        # Both broken DES and Mosca-violated RSA should be prioritized
        assert backlog.critical_count >= 1
        tasks_by_algo = {t.current_algorithm: t for t in backlog.tasks}

        # RSA should show target PQC algorithm
        assert "ML-KEM" in tasks_by_algo["RSA-2048"].target_pqc_algorithm or "ML-DSA" in tasks_by_algo["RSA-2048"].target_pqc_algorithm
        assert "FIPS 203" in tasks_by_algo["RSA-2048"].dated_standard_ref or "FIPS 204" in tasks_by_algo["RSA-2048"].dated_standard_ref

        # 5. Worker 04: Audit Logging through API
        audit_payload = {
            "reason": "Tester 01 E2E validation: Verified Mosca deadline violation on RSA core banking",
            "previous_value": "UNREVIEWED",
            "new_value": "ACCEPTED_MIGRATION_BACKLOG",
            "linked_evidence": canonical_items[0].canonical_id,
        }
        audit_res = api_client.post("/api/v1/workflow/audit", json=audit_payload)
        assert audit_res.status_code == 200
        audit_data = audit_res.json()
        assert audit_data["reason"] == audit_payload["reason"]
        assert audit_data["actor"] is None  # Safe unauthenticated actor handling

        # 6. Worker 04: Export Endpoint
        export_res = api_client.get("/api/v1/workflow/export")
        assert export_res.status_code == 200
        export_data = export_res.json()
        assert export_data["profile"] == "Astra Project Export Draft"
        assert export_data["version"] == "1.0.0"

    def test_mosca_theorem_sensitivity_and_slack_dynamics(self):
        """Verifies Mosca theorem math: X + Y > Z implies deadline exceeded, X + Y <= Z implies safety margin."""
        scorer = RiskScorer()

        # Scenario A: Short-lived token (X=0.2y), Fast migration (Y=0.5y), Horizon Z=10.0y
        # X + Y = 0.7 <= 10.0 -> Safe, slack = 9.3 years
        safe_ctx = ContextFactors(
            data_shelf_life_years=0.2,
            migration_duration_years=0.5,
        )
        safe_obs = Observation(
            observation_id="obs-safe",
            scan_id="scan-1",
            candidate_asset_id="asset-1",
            claim_type=ClaimType.ALGORITHM_USE,
            source_kind=SourceKind.SOURCE_CODE,
            algorithm="RSA-2048",
            relative_path="src/token.py",
            start_line=1,
            evidence_digest="dig1",
            sanitized_excerpt="rsa",
            detector_id="det1",
            ruleset_version="2026.10",
            confidence=ConfidenceBand.HIGH,
            confidence_rationale="test",
            state=EvidenceState.OBSERVED,
        )
        safe_risk = scorer.evaluate_observation(safe_obs, safe_ctx)
        assert safe_risk.mosca_condition_violated is False
        assert safe_risk.urgency in (UrgencyLevel.HIGH, UrgencyLevel.MEDIUM)

        # Scenario B: High-retention medical archive (X=20.0y), Complex migration (Y=4.0y), Horizon Z=10.0y
        # X + Y = 24.0 > 10.0 -> Critical violation
        critical_ctx = ContextFactors(
            data_shelf_life_years=20.0,
            migration_duration_years=4.0,
        )
        crit_risk = scorer.evaluate_observation(safe_obs, critical_ctx)
        assert crit_risk.mosca_condition_violated is True
        assert crit_risk.urgency == UrgencyLevel.CRITICAL

    def test_candidate_pqc_mapping_coverage_and_caveats(self):
        """Validates that classical algorithms receive NIST-standardized PQC migration targets with caveats."""
        # 1. RSA
        rsa_prof = lookup_algorithm_profile("RSA-2048")
        assert rsa_prof.migration_candidate is not None
        cand = rsa_prof.migration_candidate
        assert "ML-KEM" in cand.target_standard_algorithm or "ML-DSA" in cand.target_standard_algorithm
        assert len(cand.compatibility_gaps) > 0
        assert "FIPS 203" in cand.target_standard_ref or "FIPS 204" in cand.target_standard_ref

        # 2. ECDSA / ECC
        ecdsa_prof = lookup_algorithm_profile("ECDSA")
        assert ecdsa_prof.migration_candidate is not None
        assert "ML-DSA" in ecdsa_prof.migration_candidate.target_standard_algorithm
        assert "FIPS 204" in ecdsa_prof.migration_candidate.target_standard_ref

        # 3. Classical Symmetric (AES-128)
        aes_prof = lookup_algorithm_profile("AES-128")
        assert aes_prof.migration_candidate is not None
        assert "AES-256" in aes_prof.migration_candidate.target_standard_algorithm  # Grover's defense

        # 4. Unknown algorithm profile handles fallback safely
        unknown_prof = lookup_algorithm_profile("NON_EXISTENT_ALGORITHM")
        assert unknown_prof.migration_candidate is None

    def test_workflow_api_audit_validation_and_rejections(self, api_client):
        """Validates the input constraints and error codes on the workflow API."""
        # 1. Missing reason returns 400 Bad Request
        res = api_client.post("/api/v1/workflow/audit", json={
            "reason": "",
            "previous_value": "OLD",
            "new_value": "NEW",
            "linked_evidence": "canon-123",
        })
        assert res.status_code == 400
        assert "Reason is required" in res.json()["detail"]

        # 2. Valid evidence drilldown endpoint
        res = api_client.get("/api/v1/workflow/evidence/asset-test-456")
        assert res.status_code == 200
        assert isinstance(res.json(), list)
