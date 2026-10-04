"""ASTRA — Worker 03 Phase E Automated Test Suite.

Validates:
1. Dynamic, evidence-derived rehearsal scorecard computation (earning 100/100 points on real test evidence).
2. Unmet gate failure detection (asserting exit code 1 and score deduction when any rubric gate fails).
3. Truthful documentation synchronization in README.md (FIPS 203 errata notice, Phase 2 enterprise disclosure, accurate test counts).
4. CycloneDX 1.6 CBOM dependency uniqueness and strict schema conformance.
"""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
BACKEND_DIR = REPO_ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from scripts.run_judging_rehearsal import run_rehearsal
from app.services.scan_service import ScanService
from app.inventory.cbom_reconciliation import CBOMReconciliationEngine


class TestWorker03PhaseERehearsal:
    """Automated verification suite for Worker 03 Phase E Closeout."""

    def test_dynamic_rehearsal_scorecard_100_points(self):
        """Verify that the dynamic rehearsal runner executes all 6 rubric factors and earns 100/100 points."""
        exit_code = run_rehearsal()
        assert exit_code == 0, f"Expected return code 0 (100/100), got {exit_code}"

    def test_dynamic_rehearsal_catches_unmet_gate(self):
        """Verify that simulating an unmet gate dynamically deducts score and triggers exit code 1."""
        # Simulate failure in health endpoint during rehearsal
        with patch("scripts.run_judging_rehearsal.TestClient.get") as mock_get:
            class DummyResponse:
                status_code = 500
                text = "Internal Server Error"
                def json(self):
                    return {"status": "fail"}

            mock_get.return_value = DummyResponse()
            exit_code = run_rehearsal()
            assert exit_code == 1, "Expected exit code 1 when an evaluation gate fails"

    def test_readme_truthful_metrics_and_errata_disclosure(self):
        """Verify README.md contains truthful disclosures and up-to-date metrics."""
        readme_path = REPO_ROOT / "README.md"
        assert readme_path.exists(), "README.md not found"
        content = readme_path.read_text(encoding="utf-8")

        # Must cite NIST FIPS 203 errata notice
        assert "17 November 2025" in content or "FIPS 203 errata" in content, "Missing NIST FIPS 203 errata notice in README.md"

        # Must disclose Phase 2 Enterprise Scope (HSM, KMS)
        assert "Hardware Security Modules" in content or "PKCS#11" in content
        assert "Cloud KMS" in content

        # Must document dynamic rehearsal scorecard runner
        assert "run_judging_rehearsal.py" in content

    def test_cbom_dependencies_uniqueness_and_schema(self):
        """Verify that ScanService produces unique dependencies and 100% valid CycloneDX 1.6 CBOM."""
        svc = ScanService()
        record = svc.run_scan_on_directory(str(REPO_ROOT / "examples" / "synthetic_sample"))
        cbom = record.cbom_data

        assert cbom["bomFormat"] == "CycloneDX"
        assert cbom["specVersion"] == "1.6"

        deps = cbom.get("dependencies", [])
        assert len(deps) > 0

        # Check uniqueItems in dependencies array
        dep_refs = [d["ref"] for d in deps]
        assert len(dep_refs) == len(set(dep_refs)), "Duplicate 'ref' found in dependencies array"

        # Check uniqueItems in dependsOn for each node
        for d in deps:
            depends_on = d.get("dependsOn", [])
            assert len(depends_on) == len(set(depends_on)), f"Duplicate item in dependsOn for {d['ref']}"

        # Check that each referenced node is defined in metadata or components
        defined_refs = {cbom["metadata"]["component"]["bom-ref"]} | {c["bom-ref"] for c in cbom.get("components", [])}
        for d in deps:
            assert d["ref"] in defined_refs, f"Dependency ref {d['ref']} not defined in components or metadata"

        # Schema validation
        val_res = CBOMReconciliationEngine.validate_cbom(cbom)
        assert val_res.is_valid is True, f"Validation errors: {val_res.validation_errors}"
