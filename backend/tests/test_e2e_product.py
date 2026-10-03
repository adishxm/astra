"""
ASTRA End-to-End Product Integration & System Test Suite

Validates:
1. End-to-end Scan Pipeline (ScanService):
   Intake Sandbox -> AST/Regex Multi-surface Discovery -> Coverage Accounting ->
   Canonical Inventory Mapping -> Mosca Horizon Risk Scoring -> PQC Backlog ->
   CycloneDX 1.6 CBOM Generation -> Temporal DNA Hashing.
2. Master FastAPI Application (app.main:app):
   /health, /, /api/v1/scans/directory, /api/v1/scans/upload (zip),
   /api/v1/scans/{id}, /findings, /coverage, /risk, /export, and workflow drilldowns.
3. ASTRA Zero-Dependency Product CLI (app.cli):
   version, scan (table & json), show, risk, export, and validate commands.
"""

import io
import json
import os
import shutil
import tempfile
import zipfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.scan_service import ScanService, ScanStore, GLOBAL_SCAN_STORE
from app.cli import main as cli_main


@pytest.fixture
def sample_crypto_codebase(tmp_path: Path) -> Path:
    """Creates a temporary realistic codebase containing classical cryptography."""
    codebase_dir = tmp_path / "target_codebase"
    codebase_dir.mkdir(parents=True, exist_ok=True)

    auth_py = codebase_dir / "auth.py"
    auth_py.write_text(
        '''"""Authentication module with legacy cryptography."""
import hashlib
from Crypto.Cipher import AES

def hash_user_password(password: str) -> str:
    # Deprecated SHA1 usage
    return hashlib.sha1(password.encode()).hexdigest()

def legacy_encrypt(token: bytes, key: bytes) -> bytes:
    # Legacy AES CBC with fixed IV
    cipher = AES.new(key, AES.MODE_CBC, iv=b"1234567890123456")
    return cipher.encrypt(token)
''',
        encoding="utf-8",
    )

    certs_py = codebase_dir / "certs.py"
    certs_py.write_text(
        '''"""PKI and certificate management."""
import hashlib
from Crypto.PublicKey import RSA

def generate_keypair():
    # Quantum-vulnerable RSA 2048 keypair
    key = RSA.generate(2048)
    return key.export_key()

def md5_fingerprint(cert_data: bytes) -> str:
    # Insecure MD5 fingerprint
    return hashlib.md5(cert_data).hexdigest()
''',
        encoding="utf-8",
    )

    readme_md = codebase_dir / "README.md"
    readme_md.write_text("# Target Codebase\nA test codebase for cryptographic discovery.\n", encoding="utf-8")

    return codebase_dir


@pytest.fixture
def sample_zip_archive(sample_crypto_codebase: Path, tmp_path: Path) -> Path:
    """Packages the sample codebase into a .zip archive for upload intake testing."""
    zip_path = tmp_path / "codebase_bundle.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(sample_crypto_codebase):
            for file in files:
                full_path = Path(root) / file
                rel_path = full_path.relative_to(sample_crypto_codebase)
                zf.write(full_path, arcname=str(rel_path))
    return zip_path


class TestScanServiceEndToEnd:
    """Verifies that the central ScanService accurately processes repositories."""

    def test_directory_scan_pipeline(self, sample_crypto_codebase: Path):
        record = ScanService.scan_directory(sample_crypto_codebase)

        assert record.scan_id.startswith("scan-")
        assert record.status == "completed"

        # 1. Coverage assertion
        coverage = record.coverage_summary
        assert coverage.get("total_files", 0) >= 3
        assert coverage.get("total_lines", 0) > 0
        assert "Python" in coverage.get("languages", {})

        # 2. Canonical assets & observations assertion
        assert len(record.canonical_assets) > 0
        assert len(record.observations) > 0

        asset_names = [a.primary_name for a in record.canonical_assets]
        # At least SHA1, AES, RSA, MD5 should be detected by discovery engines
        detected_algos = " ".join(asset_names).upper()
        assert "SHA" in detected_algos or "AES" in detected_algos or "RSA" in detected_algos

        # 3. Mosca Horizon Risk assessment assertion
        risk = record.risk_evaluations
        assert len(risk) > 0
        assert any(r.risk_score >= 0.0 for r in risk)

        # 4. PQC Backlog assertion
        backlog = record.pqc_backlog
        assert isinstance(backlog, list)

        # 5. CycloneDX 1.6 CBOM assertion
        cbom = record.cbom
        assert cbom.get("bomFormat") == "CycloneDX"
        assert cbom.get("specVersion") == "1.6"
        assert "components" in cbom
        assert isinstance(cbom["components"], list)

        # 6. Temporal DNA Fingerprint assertion
        dna = record.temporal_snapshot
        assert "state_dna_hash" in dna
        assert len(dna["state_dna_hash"]) == 64  # SHA-256 length

        # 7. Persistence retrieval assertion
        retrieved = GLOBAL_SCAN_STORE.get(record.scan_id)
        assert retrieved is not None
        assert retrieved.scan_id == record.scan_id

    def test_archive_scan_pipeline(self, sample_zip_archive: Path):
        record = ScanService.scan_archive_file(sample_zip_archive)

        assert record.scan_id.startswith("scan-")
        assert record.status == "completed"
        assert record.coverage_summary.get("total_files", 0) >= 3
        assert len(record.canonical_assets) > 0
        assert record.cbom.get("specVersion") == "1.6"


class TestMasterFastAPIEndpoints:
    """Verifies all REST API routes and the embedded static Web Dashboard."""

    @pytest.fixture(autouse=True)
    def setup_client(self):
        self.client = TestClient(app)

    def test_health_endpoints(self):
        r1 = self.client.get("/health")
        assert r1.status_code == 200
        assert r1.json()["status"] == "pass"

        r2 = self.client.get("/api/v1/health")
        assert r2.status_code == 200
        assert r2.json()["status"] == "pass"
        assert r2.json()["version"] == "1.0.0"

    def test_web_dashboard_html_served(self):
        resp = self.client.get("/")
        assert resp.status_code == 200
        assert "text/html" in resp.headers["content-type"]
        assert "ASTRA" in resp.text
        assert "CycloneDX" in resp.text

    def test_directory_scan_endpoint(self, sample_crypto_codebase: Path):
        resp = self.client.post("/api/v1/scans/directory", json={"path": str(sample_crypto_codebase)})
        assert resp.status_code == 200
        data = resp.json()
        assert "scan_id" in data
        assert data["status"] == "completed"
        scan_id = data["scan_id"]

        # Test listing scans
        list_resp = self.client.get("/api/v1/scans")
        assert list_resp.status_code == 200
        scans = list_resp.json()
        assert any(s["scan_id"] == scan_id for s in scans)

        # Test getting scan record
        get_resp = self.client.get(f"/api/v1/scans/{scan_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["scan_id"] == scan_id

        # Test findings drilldown
        find_resp = self.client.get(f"/api/v1/scans/{scan_id}/findings")
        assert find_resp.status_code == 200
        findings = find_resp.json()
        assert "canonical_assets" in findings
        assert "observations" in findings

        # Test coverage
        cov_resp = self.client.get(f"/api/v1/scans/{scan_id}/coverage")
        assert cov_resp.status_code == 200
        assert "total_files_in_archive" in cov_resp.json()

        # Test risk evaluation
        risk_resp = self.client.get(f"/api/v1/scans/{scan_id}/risk")
        assert risk_resp.status_code == 200
        assert "risk_evaluations" in risk_resp.json()

        # Test dynamic scenario risk re-evaluation query parameters
        dyn_risk_resp = self.client.get(f"/api/v1/scans/{scan_id}/risk?horizon=3.0&shelf_life=5.0&migration=2.0")
        assert dyn_risk_resp.status_code == 200
        dyn_data = dyn_risk_resp.json()
        assert "scenario" in dyn_data
        assert dyn_data["scenario"]["quantum_threat_horizon_years"] == 3.0
        assert dyn_data["context"]["data_shelf_life_years"] == 5.0
        assert len(dyn_data["risk_evaluations"]) > 0

        # Test CBOM export
        export_resp = self.client.get(f"/api/v1/scans/{scan_id}/export")
        assert export_resp.status_code == 200
        cbom = export_resp.json()
        assert cbom["bomFormat"] == "CycloneDX"
        assert cbom["specVersion"] == "1.6"

    def test_archive_upload_scan_endpoint(self, sample_zip_archive: Path):
        with open(sample_zip_archive, "rb") as f:
            resp = self.client.post(
                "/api/v1/scans/upload",
                files={"file": ("codebase.zip", f, "application/zip")},
            )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "completed"
        assert len(data["canonical_assets"]) > 0

    def test_workflow_evidence_drilldown(self, sample_crypto_codebase: Path):
        # Run a scan to populate assets
        rec = ScanService.scan_directory(sample_crypto_codebase)
        assert len(rec.canonical_assets) > 0
        first_asset = rec.canonical_assets[0]
        asset_id = first_asset.asset_id

        # Query evidence drilldown
        resp = self.client.get(f"/api/v1/workflow/evidence/{asset_id}")
        assert resp.status_code == 200
        evidence_list = resp.json()
        assert isinstance(evidence_list, list)


class TestZeroDependencyCLI:
    """Verifies that the CLI tool operates cleanly across all subcommands."""

    def test_cli_version(self, capsys):
        code = cli_main(["version"])
        assert code == 0
        captured = capsys.readouterr()
        assert "ASTRA" in captured.out
        assert "1.0.0" in captured.out

    def test_cli_scan_table_output(self, sample_crypto_codebase: Path, capsys):
        code = cli_main(["scan", str(sample_crypto_codebase), "--format", "table"])
        assert code == 0
        captured = capsys.readouterr()
        assert "ASTRA SCAN COMPLETE" in captured.out
        assert "Identified Cryptographic Inventory:" in captured.out
        assert "AES" in captured.out or "RSA" in captured.out

    def test_cli_scan_json_output(self, sample_crypto_codebase: Path, tmp_path: Path, capsys):
        out_file = tmp_path / "scan_result.json"
        code = cli_main(["scan", str(sample_crypto_codebase), "--format", "json", "--output", str(out_file)])
        assert code == 0
        assert out_file.exists()

        with open(out_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert "scan_id" in data
        assert data["status"] == "completed"

        # Now test show, risk, validate, and export on this scan_id
        scan_id = data["scan_id"]

        # 1. show
        show_code = cli_main(["show", scan_id])
        assert show_code == 0

        # 2. risk
        risk_code = cli_main(["risk", scan_id])
        assert risk_code == 0

        # 3. validate
        val_code = cli_main(["validate", scan_id])
        assert val_code == 0

        # 4. export
        cbom_out = tmp_path / "cbom_export.json"
        exp_code = cli_main(["export", scan_id, "--output", str(cbom_out)])
        assert exp_code == 0
        assert cbom_out.exists()
        with open(cbom_out, "r", encoding="utf-8") as f:
            cbom_data = json.load(f)
        assert cbom_data.get("bomFormat") == "CycloneDX"
        assert cbom_data.get("specVersion") == "1.6"

    def test_cli_scan_synthetic_sample_repository(self, capsys):
        """Scans the reference synthetic sample fixture and verifies accurate detection & coverage accounting."""
        sample_path = Path(__file__).resolve().parent.parent.parent / "examples" / "synthetic_sample"
        assert sample_path.exists(), f"Synthetic sample not found at: {sample_path}"

        try:
            code = cli_main(["scan", str(sample_path), "--format", "table"])
            assert code == 0
            captured = capsys.readouterr()

            # Must report coverage with denominator accounting for unsupported wav file
            assert "Coverage Assessment:" in captured.out
            assert "RSA-2048" in captured.out
            assert "AES-256" in captured.out
            assert "ML-KEM" in captured.out
            assert "MD5" in captured.out
            # Comment lines mentioning DES/3DES must not be reported as active findings
            assert "DES-" not in captured.out
            assert "3DES" not in captured.out
        finally:
            obs_file = sample_path / "observations.json"
            if obs_file.exists():
                try:
                    obs_file.unlink()
                except OSError:
                    pass
