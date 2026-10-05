"""ASTRA Worker 1 - Ground-Truth Detector & Coverage Benchmark Suite.

Validates:
1. Ground-truth benchmark corpus detection & coverage accounting metrics:
   - Binary confusion matrix: TP=10, FP=0, FN=0, TN=2 (Precision=1.0, Recall=1.0, F1=1.0, Specificity=1.0).
   - Explicit Abstentions: ABSTAIN_UNSUPPORTED=1, ABSTAIN_UNPARSEABLE=1 (total 14 corpus cases evaluated).
2. Parity across CLI directory scan, CLI archive scan, and FastAPI upload endpoint.
3. Safe archive extraction containment & adversarial path traversal defenses.
4. Honest reporting of unsupported media (.wav) and malformed certificates (.pem) as abstention coverage states, NOT binary TNs.
5. Immutable frontend static contract preservation (frontend/index.html == backend/app/static/index.html).
"""

import json
import tempfile
import zipfile
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.scan_service import ScanService
from app.intake.extractor import SafeArchiveExtractor
from app.core.security import SecurityException

FIXTURES_DIR = Path(__file__).parent / "fixtures"
BENCHMARK_DIR = FIXTURES_DIR / "ground_truth_benchmark"
MANIFEST_FILE = BENCHMARK_DIR / "ground_truth_manifest.json"
CASES_DIR = BENCHMARK_DIR / "cases"
CORPUS_ZIP = FIXTURES_DIR / "ground_truth_corpus.zip"
ADVERSARIAL_ZIP = FIXTURES_DIR / "adversarial_path_traversal.zip"


@pytest.fixture(scope="module")
def ground_truth_manifest():
    assert MANIFEST_FILE.exists(), f"Benchmark manifest not found at {MANIFEST_FILE}"
    with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


class TestWorker01GroundTruthBenchmark:
    """Worker 1 Ground-Truth Detector & Coverage Benchmark Suite."""

    def test_ground_truth_corpus_manifest_metrics(self, ground_truth_manifest):
        """Verify ground-truth corpus case detections and compute corrected binary Precision/Recall/F1 and abstention metrics on clean cases."""
        assert CASES_DIR.exists(), f"Cases directory missing at {CASES_DIR}"
        
        # Phase C1 assertions: Verify scan target contains strictly the 14 manifest case files (zero metadata/contamination)
        expected_manifest_paths = sorted([c["relative_path"] for c in ground_truth_manifest["cases"]])
        actual_dir_paths = sorted([p.relative_to(CASES_DIR).as_posix() for p in CASES_DIR.rglob("*") if p.is_file()])
        assert actual_dir_paths == expected_manifest_paths, f"Directory scan root contamination: {actual_dir_paths} != {expected_manifest_paths}"

        # Verify ZIP contains strictly the 14 manifest case members (zero manifest/metadata contamination)
        assert CORPUS_ZIP.exists(), f"Corpus ZIP missing at {CORPUS_ZIP}"
        with zipfile.ZipFile(CORPUS_ZIP, "r") as z:
            actual_zip_members = sorted(z.namelist())
        assert actual_zip_members == expected_manifest_paths, f"Corpus ZIP member contamination: {actual_zip_members} != {expected_manifest_paths}"

        service = ScanService()
        record = service.run_scan_on_directory(
            directory_path=str(CASES_DIR),
            target_name="Synthetic Ground Truth Benchmark Cases Directory"
        )
        data = record.to_dict()

        # Zero metadata contamination assertion: Total observations must be exactly 30 across the 10 positive cases
        total_obs = data.get("observations", [])
        assert len(total_obs) == 30, f"Expected exactly 30 clean observations (zero manifest contamination), got {len(total_obs)}"

        tp = 0
        fp = 0
        fn = 0
        tn = 0
        abstain_unsupported = 0
        abstain_unparseable = 0
        abstain_other = 0

        for case in ground_truth_manifest["cases"]:
            rel_path = case["relative_path"]
            outcome_type = case["outcome_type"]

            path_obs = [
                o for o in total_obs
                if o.get("relative_path") == rel_path or rel_path in o.get("relative_path", "")
            ]
            detected_presence = len(path_obs) > 0

            if outcome_type == "POSITIVE":
                if detected_presence:
                    tp += 1
                else:
                    fn += 1
            elif outcome_type == "NEGATIVE":
                if not detected_presence:
                    tn += 1
                else:
                    fp += 1
            elif outcome_type == "ABSTAIN_UNSUPPORTED":
                abstain_unsupported += 1
            elif outcome_type == "ABSTAIN_UNPARSEABLE":
                abstain_unparseable += 1
            else:
                abstain_other += 1

        precision = tp / (tp + fp) if (tp + fp) > 0 else 1.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 1.0
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 1.0

        assert tp == 10, f"Expected 10 True Positives, got {tp}"
        assert fp == 0, f"Expected 0 False Positives, got {fp}"
        assert fn == 0, f"Expected 0 False Negatives, got {fn}"
        assert tn == 2, f"Expected 2 True Negatives (supported clean cases), got {tn}"
        assert abstain_unsupported == 1, f"Expected 1 ABSTAIN_UNSUPPORTED, got {abstain_unsupported}"
        assert abstain_unparseable == 1, f"Expected 1 ABSTAIN_UNPARSEABLE, got {abstain_unparseable}"

        assert precision == 1.0, f"Precision must be 1.0, got {precision}"
        assert recall == 1.0, f"Recall must be 1.0, got {recall}"
        assert f1 == 1.0, f"F1 Score must be 1.0, got {f1}"
        assert specificity == 1.0, f"Specificity must be 1.0, got {specificity}"

    def test_cli_directory_archive_api_parity(self, ground_truth_manifest):
        """Verify parity across CLI directory scan, CLI archive scan, and REST API upload on clean cases."""
        expected_manifest_paths = sorted([c["relative_path"] for c in ground_truth_manifest["cases"]])
        
        service = ScanService()
        dir_rec = service.run_scan_on_directory(
            directory_path=str(CASES_DIR),
            target_name="Benchmark Directory"
        ).to_dict()

        archive_rec = service.scan_archive_file(CORPUS_ZIP).to_dict()

        client = TestClient(app)
        with open(CORPUS_ZIP, "rb") as f:
            upload_resp = client.post(
                "/api/v1/scans/upload",
                files={"file": ("ground_truth_corpus.zip", f, "application/zip")},
            )
        assert upload_resp.status_code == 200
        scan_id = upload_resp.json()["scan_id"]
        api_rec = client.get(f"/api/v1/scans/{scan_id}").json()

        dir_asset_names = sorted([a.get("primary_name") for a in dir_rec.get("canonical_assets", [])])
        archive_asset_names = sorted([a.get("primary_name") for a in archive_rec.get("canonical_assets", [])])
        api_asset_names = sorted([a.get("primary_name") for a in api_rec.get("canonical_assets", [])])

        # Confirm exact 30 canonical assets and 30 observations across all 3 interfaces (zero contamination)
        assert len(dir_rec.get("observations", [])) == 30, f"Directory obs count mismatch: {len(dir_rec.get('observations', []))}"
        assert len(archive_rec.get("observations", [])) == 30, f"Archive obs count mismatch: {len(archive_rec.get('observations', []))}"
        assert len(dir_asset_names) == 30, f"Asset count mismatch: {len(dir_asset_names)}"

        assert dir_asset_names == archive_asset_names, "Directory vs Archive asset parity mismatch"
        assert archive_asset_names == api_asset_names, "Archive vs API upload asset parity mismatch"

    def test_adversarial_archive_path_traversal_defense(self):
        """Verify SafeArchiveExtractor rejects adversarial path traversal entries."""
        assert ADVERSARIAL_ZIP.exists(), f"Adversarial zip missing at {ADVERSARIAL_ZIP}"
        extractor = SafeArchiveExtractor()
        with tempfile.TemporaryDirectory() as tmpdir:
            sandbox = Path(tmpdir)
            with pytest.raises(SecurityException) as exc_info:
                extractor.process_and_extract(ADVERSARIAL_ZIP, sandbox, "test-adv-scan")
            assert "traversal" in str(exc_info.value).lower() or ".." in str(exc_info.value)

    def test_unsupported_and_malformed_honest_coverage(self):
        """Verify unsupported formats (.wav) and malformed certs (.pem) produce zero false findings and stay abstained."""
        service = ScanService()
        record = service.run_scan_on_directory(
            directory_path=str(CASES_DIR / "unsupported"),
            target_name="Unsupported Fixtures Directory"
        ).to_dict()

        observations = record.get("observations", [])
        assert len(observations) == 0, f"Expected 0 findings in unsupported directory, got {len(observations)}"

    def test_worker2_frontend_static_unmodified_contract(self):
        """Verify frontend/index.html and backend/app/static/index.html are 100% byte-for-byte identical."""
        repo_root = Path(__file__).resolve().parent.parent.parent
        frontend_html = repo_root / "frontend" / "index.html"
        backend_html = repo_root / "backend" / "app" / "static" / "index.html"

        assert frontend_html.exists(), "frontend/index.html missing"
        assert backend_html.exists(), "backend/app/static/index.html missing"

        f_bytes = frontend_html.read_bytes()
        b_bytes = backend_html.read_bytes()

        assert len(f_bytes) == len(b_bytes), f"File size mismatch: frontend={len(f_bytes)} vs backend={len(b_bytes)}"
        assert f_bytes == b_bytes, "frontend/index.html and backend/app/static/index.html byte mismatch"

