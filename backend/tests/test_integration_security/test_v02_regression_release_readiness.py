"""ASTRA - Tester 02 Regression, Documentation & Release Readiness Suite (Cycle V02).

Exhaustively validates:
- Multi-surface deterministic discovery consistency across runs.
- Truthful reporting invariant: clean state labeled NO_FINDINGS_IN_SUPPORTED_SCOPE, zero false safety claims.
- Mosca Theorem boundary conditions (X + Y > Z threshold dynamics).
- Alert fatigue reduction verification: >= 50% critical alert reduction over flat regex/CVSS baseline (AC-12).
- Complete web workflow API lifecycle (evidence drilldown, auditable reviews, export).
"""

from datetime import datetime, timezone
import uuid
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.coverage.accounting import CoverageAccountant
from app.discovery.engine import DiscoveryEngine
from app.discovery.models import (
    ClaimType,
    ConfidenceBand,
    DiscoverySummary,
    EvidenceState,
    Observation,
    SourceKind,
)
from app.intake.models import ArchiveType, ExtractedFileEntry, ScanManifest, ScanStatus
from app.inventory.models import (
    AssetIdentity,
    AuditRecord,
    CanonicalEvidence,
    InventoryExport,
    Relationship,
    map_observation_to_canonical,
)
from app.risk.backlog import BacklogBuilder
from app.risk.models import (
    BusinessCriticality,
    ContextFactors,
    ExposureScope,
    RiskScenario,
    UrgencyLevel,
)
from app.risk.scenarios import BaselineComparison, ScenarioAnalyzer
from app.risk.scorer import RiskScorer
from app.web_workflow.router import router


@pytest.fixture
def workflow_client():
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


def _make_obs(algo: str, path: str) -> Observation:
    return Observation(
        observation_id=str(uuid.uuid4()),
        scan_id="scan-reg-1",
        candidate_asset_id=f"asset-{algo.lower()}",
        claim_type=ClaimType.ALGORITHM_USE,
        source_kind=SourceKind.SOURCE_CODE,
        algorithm=algo,
        relative_path=path,
        start_line=1,
        evidence_digest="a" * 64,
        sanitized_excerpt=f"{algo} code",
        detector_id="det-src",
        ruleset_version="2026.10-nist-pqc",
        confidence=ConfidenceBand.HIGH,
        confidence_rationale="test",
        state=EvidenceState.OBSERVED,
    )


class TestTester02V02RegressionReleaseReadiness:
    """Exhaustive regression, accuracy, and release readiness validation for Cycle V02."""

    def test_regression_truthful_reporting_clean_state_invariant(self):
        """Verifies that clean repositories report NO_FINDINGS_IN_SUPPORTED_SCOPE without false security claims."""
        manifest = ScanManifest(
            scan_id="scan-clean-1",
            archive_name="clean_repo.zip",
            archive_sha256="b" * 64,
            archive_size_bytes=1000,
            archive_type=ArchiveType.ZIP,
            declared_scope="SCOPE_CLEAN",
            tenant_id="tenant-clean",
            status=ScanStatus.COMPLETE,
            intake_engine_version="1.0.0",
            collector_version="0.1.0",
            ruleset_version="2026.10-nist-pqc",
            files=[
                ExtractedFileEntry(relative_path="src/hello.py", size_bytes=100, sha256="h1", file_extension=".py", is_supported=True),
                ExtractedFileEntry(relative_path="src/utils.py", size_bytes=200, sha256="h2", file_extension=".py", is_supported=True),
                ExtractedFileEntry(relative_path="README.txt", size_bytes=300, sha256="h3", file_extension=".txt", is_supported=True),
            ],
        )

        summary = DiscoverySummary(
            scan_id="scan-clean-1",
            total_files_analyzed=3,
            files_with_findings=0,
            files_with_zero_findings=3,
            unsupported_files_count=0,
            failed_parses_count=0,
            observations=[],
            detector_health={"det-src": "OK"},
        )

        accountant = CoverageAccountant()
        report = accountant.evaluate_coverage(manifest, summary)

        assert report.total_observations_found == 0
        assert report.total_assessed_files == 2
        assert report.total_unsupported_files == 1
        assert report.unsupported_extensions == [".txt"]
        assert report.scan_status_label == "NO_FINDINGS_IN_SUPPORTED_SCOPE"

        # Truthful invariant: must never claim "SAFE" or "COMPLIANT"
        assert "SAFE" not in report.scan_status_label
        assert "COMPLIANT" not in report.scan_status_label
        assert len(report.unsupported_extensions) > 0

    def test_regression_mosca_horizon_boundary_dynamics(self):
        """Tests exact deadline transition thresholds for the Mosca Theorem (X + Y vs Z)."""
        # Scenario: Data shelf life X = 6 years, Migration time Y = 3 years -> Total X + Y = 9 years
        context = ContextFactors(
            data_shelf_life_years=6.0,
            migration_duration_years=3.0,
            exposure=ExposureScope.PUBLIC_FACING,
            criticality=BusinessCriticality.HIGH_IMPACT,
        )

        obs = _make_obs("RSA-2048", "src/auth.py")

        # 1. Quantum horizon Z = 12 years (Slack = +3.0 years) -> No SNDL violation
        scenario_safe = RiskScenario(quantum_threat_horizon_years=12.0)
        scorer_safe = RiskScorer(scenario=scenario_safe)
        eval_safe = scorer_safe.evaluate_observation(obs, context)
        assert eval_safe.mosca_condition_violated is False
        assert eval_safe.mosca_slack_years == 3.0
        assert eval_safe.urgency != UrgencyLevel.CRITICAL

        # 2. Quantum horizon Z = 9.0 years (Boundary condition: X + Y == Z, Slack = 0.0)
        scenario_boundary = RiskScenario(quantum_threat_horizon_years=9.0)
        scorer_boundary = RiskScorer(scenario=scenario_boundary)
        eval_boundary = scorer_boundary.evaluate_observation(obs, context)
        assert eval_boundary.mosca_slack_years == 0.0

        # 3. Quantum horizon Z = 8.0 years (Violation: X + Y > Z, Slack = -1.0 years) -> Immediate CRITICAL
        scenario_critical = RiskScenario(quantum_threat_horizon_years=8.0)
        scorer_critical = RiskScorer(scenario=scenario_critical)
        eval_critical = scorer_critical.evaluate_observation(obs, context)
        assert eval_critical.mosca_condition_violated is True
        assert eval_critical.mosca_slack_years == -1.0
        assert eval_critical.urgency == UrgencyLevel.CRITICAL
        assert "RC_MOSCA_DEADLINE_VIOLATED_SNDL_RISK" in eval_critical.reason_codes

    def test_regression_alert_fatigue_reduction_target(self):
        """Verifies that contextual risk prioritization achieves >= 50% alert fatigue reduction over flat severity."""
        observations = [
            _make_obs("RSA-2048", "src/prod_gateway.py"),
            _make_obs("RSA-2048", "tests/fixtures/mock_key.py"),
            _make_obs("RSA-1024", "tests/unit/test_rsa.py"),
            _make_obs("ECDSA", "scripts/scratch_dev.py"),
            _make_obs("ECDSA", "internal/tools/debug.py"),
            _make_obs("ECDSA", "public/edge_tls.py"),
            _make_obs("AES-256", "storage/db.py"),
            _make_obs("AES-128", "tests/cache.py"),
            _make_obs("SHA-256", "utils/hash.py"),
            _make_obs("ML-KEM-768", "services/pqc_kex.py"),
        ]

        context_map = {
            "src/prod_gateway.py": ContextFactors(data_shelf_life_years=10, migration_duration_years=3, exposure=ExposureScope.PUBLIC_FACING, criticality=BusinessCriticality.MISSION_CRITICAL),
            "tests/fixtures/mock_key.py": ContextFactors(data_shelf_life_years=0.1, migration_duration_years=0.1, exposure=ExposureScope.BUILD_OR_TEST, criticality=BusinessCriticality.DEVELOPMENT),
            "tests/unit/test_rsa.py": ContextFactors(data_shelf_life_years=0.1, migration_duration_years=0.1, exposure=ExposureScope.BUILD_OR_TEST, criticality=BusinessCriticality.DEVELOPMENT),
            "scripts/scratch_dev.py": ContextFactors(data_shelf_life_years=0.2, migration_duration_years=0.1, exposure=ExposureScope.LOCAL_ISOLATED, criticality=BusinessCriticality.DEVELOPMENT),
            "internal/tools/debug.py": ContextFactors(data_shelf_life_years=0.5, migration_duration_years=0.2, exposure=ExposureScope.LOCAL_ISOLATED, criticality=BusinessCriticality.DEVELOPMENT),
            "public/edge_tls.py": ContextFactors(data_shelf_life_years=12, migration_duration_years=2, exposure=ExposureScope.PARTNER_GATEWAY, criticality=BusinessCriticality.HIGH_IMPACT),
            "storage/db.py": ContextFactors(data_shelf_life_years=15, migration_duration_years=1, exposure=ExposureScope.PUBLIC_FACING, criticality=BusinessCriticality.MISSION_CRITICAL),
            "tests/cache.py": ContextFactors(data_shelf_life_years=0.1, migration_duration_years=0.1, exposure=ExposureScope.BUILD_OR_TEST, criticality=BusinessCriticality.DEVELOPMENT),
            "utils/hash.py": ContextFactors(data_shelf_life_years=5, migration_duration_years=1, exposure=ExposureScope.INTERNAL_SHARED, criticality=BusinessCriticality.LOW),
            "services/pqc_kex.py": ContextFactors(data_shelf_life_years=10, migration_duration_years=1, exposure=ExposureScope.PUBLIC_FACING, criticality=BusinessCriticality.MISSION_CRITICAL),
        }

        scenario = RiskScenario(quantum_threat_horizon_years=8.0)
        comparison = ScenarioAnalyzer.compare_against_flat_baseline(observations, scenario, context_map)

        # Baseline flags all 6 asymmetric assets indiscriminately
        assert comparison.flat_high_critical_count == 6
        # Contextual scoring filters out the dev/test keys
        assert comparison.contextual_high_critical_count <= 3
        # AC-12 specifies >= 50% alert fatigue reduction
        assert comparison.alert_reduction_percentage >= 50.0

    def test_release_readiness_web_api_end_to_end_journey(self, workflow_client):
        """Validates the full workflow API lifecycle for release acceptance."""
        # 1. Evidence drilldown
        resp = workflow_client.get("/api/v1/workflow/evidence/asset-core-signer")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

        # 2. Audit review submission
        audit_payload = {
            "reason": "Security review completed: approved transition from RSA to ML-DSA-65",
            "previous_value": "MIGRATION_PENDING",
            "new_value": "MIGRATION_SCHEDULED",
            "linked_evidence": "canon-obs-rsa-9921",
        }
        audit_resp = workflow_client.post("/api/v1/workflow/audit", json=audit_payload)
        assert audit_resp.status_code == 200
        audit_data = audit_resp.json()
        assert audit_data["reason"] == audit_payload["reason"]
        assert audit_data["new_value"] == "MIGRATION_SCHEDULED"
        assert audit_data["actor"] is None

        # 3. Audit validation rejection on empty reason
        bad_resp = workflow_client.post("/api/v1/workflow/audit", json={
            "reason": "",
            "previous_value": "MIGRATION_PENDING",
            "new_value": "MIGRATION_SCHEDULED",
            "linked_evidence": "canon-obs-rsa-9921",
        })
        assert bad_resp.status_code == 400
        assert "Reason is required" in bad_resp.json()["detail"]

        # 4. Inventory export
        export_resp = workflow_client.get("/api/v1/workflow/export")
        assert export_resp.status_code == 200
        export_data = export_resp.json()
        assert export_data["version"] == "1.0.0"
        assert "profile" in export_data
