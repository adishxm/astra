"""Automated Verification Suite for Worker 03 Phase C:
Empirical Benchmark Math Repair: Finding-Level Precision, Unmatched False Positive Accounting & Holdout Integrity.

Verifies:
1. Finding-level TP, FP, FN accounting penalizes unlabelled/extra detections on positive files.
2. Direct probe replication: extra detections on positive files reduce precision (not hidden).
3. Adversarial noise sensitivity: injecting spurious detections strictly degrades precision.
4. Negative control accounting: spurious findings on negative files increment FP and FPR without unit mixing.
5. Benchmark mathematical invariants:
   - Precision = TP / (TP + FP)
   - Recall = TP / (TP + FN)
   - F1 = 2 * (P * R) / (P + R)
6. All in-scope surfaces satisfy research thresholds (>= 80% Precision, >= 80% Recall).
"""

from typing import Dict, List
import pytest

from tests.test_e2e_corpus_benchmark import (
    algo_matches,
    compute_metrics,
    CORPUS_DIR,
    LABELS_FILE,
)


class TestWorker03PhaseCBenchmarkMath:
    """Phase C Automated Acceptance Tests."""

    def test_direct_assessment_probe_repaired(self):
        """Test C.1: Replicate the Fresh Assessment probe.
        
        A positive file expected to contain ONLY RSA, but with extra MD5 and AES detections,
        MUST report TP=1, FP=2, FN=0, precision=33.3% (never FP=0, precision=100%).
        """
        entry = {
            "relative_path": "sample/crypto.py",
            "is_negative": False,
            "expected_algorithms": ["RSA-2048"],
        }
        # Injected detections: RSA-2048 (TP) + MD5 (FP) + AES-256 (FP)
        obs_by_file = {
            "sample/crypto.py": ["RSA-2048", "MD5", "AES-256"],
        }

        metrics = compute_metrics([entry], obs_by_file)

        assert metrics["tp"] == 1, "Expected 1 TP for matched RSA-2048"
        assert metrics["fp"] == 2, "Expected 2 FPs for unlabelled MD5 and AES-256 detections"
        assert metrics["fn"] == 0, "Expected 0 FN because RSA was detected"
        assert abs(metrics["precision"] - (1.0 / 3.0)) < 1e-4, f"Precision must be 33.33%, got {metrics['precision']}"
        assert metrics["recall"] == 1.0, "Recall should remain 1.0"

    def test_adversarial_noise_injection_degrades_precision(self):
        """Test C.2: Injecting spurious detection on an existing clean fixture drops precision below 100%."""
        entry = {
            "relative_path": "sample/clean_rsa.py",
            "is_negative": False,
            "expected_algorithms": ["RSA-2048"],
        }
        clean_obs = {"sample/clean_rsa.py": ["RSA-2048"]}
        clean_metrics = compute_metrics([entry], clean_obs)
        assert clean_metrics["precision"] == 1.0
        assert clean_metrics["fp"] == 0

        # Inject noise finding
        noisy_obs = {"sample/clean_rsa.py": ["RSA-2048", "SHA-1"]}
        noisy_metrics = compute_metrics([entry], noisy_obs)
        assert noisy_metrics["tp"] == 1
        assert noisy_metrics["fp"] == 1
        assert noisy_metrics["precision"] == 0.50, "Precision must drop to 50% upon noise injection"

    def test_negative_control_spurious_detection_penalized(self):
        """Test C.3: Spurious detection on negative controls increments FP and elevates FPR."""
        clean_entries = [
            {"relative_path": "sample/clean_1.py", "is_negative": True, "expected_algorithms": []},
            {"relative_path": "sample/clean_2.py", "is_negative": True, "expected_algorithms": []},
        ]
        perfect_obs = {}
        clean_metrics = compute_metrics(clean_entries, perfect_obs)
        assert clean_metrics["tn"] == 2
        assert clean_metrics["fp"] == 0
        assert clean_metrics["fpr"] == 0.0

        # Inject false alarm into clean_1
        spurious_obs = {"sample/clean_1.py": ["MD5"]}
        spurious_metrics = compute_metrics(clean_entries, spurious_obs)
        assert spurious_metrics["tn"] == 1
        assert spurious_metrics["fp"] == 1
        assert spurious_metrics["fpr"] == 0.50, "FPR must be 1 violation / 2 negative files = 50%"

    def test_strict_algo_matcher_rejects_unrelated_substrings(self):
        """Test C.4: algo_matches rejects arbitrary non-cryptographic substrings."""
        # Unrelated words should not match
        assert not algo_matches("AES", "MESSAGE")
        assert not algo_matches("MD5", "MD5SUM_UNVERIFIED_HASH_OR_NOTHING")
        assert not algo_matches("RSA", "UNIVERSAL")
        assert not algo_matches("EC", "SECURITY")

        # Legitimate canonical matches must pass
        assert algo_matches("RSA-2048", "RSA")
        assert algo_matches("AES-256", "AES")
        assert algo_matches("ECDSA", "secp256r1")
        assert algo_matches("CHACHA20", "ChaCha20Poly1305")

    def test_corpus_benchmark_passes_research_thresholds(self):
        """Test C.5: Full corpus benchmark satisfies >= 80% Precision, >= 80% Recall under repaired math."""
        from app.services.scan_service import ScanService
        import json

        with open(LABELS_FILE, "r", encoding="utf-8") as f:
            labels = json.load(f)

        service = ScanService()
        record = service.run_scan_on_directory(str(CORPUS_DIR), "Test Corpus")

        obs_by_file: Dict[str, List[str]] = {}
        for obs in record.observations:
            norm_path = obs.relative_path.replace("\\", "/")
            obs_by_file.setdefault(norm_path, []).append(obs.algorithm)

        train_metrics = compute_metrics(labels["training_set"], obs_by_file)
        assert train_metrics["precision"] >= 0.80, f"Training precision: {train_metrics['precision']}"
        assert train_metrics["recall"] >= 0.80, f"Training recall: {train_metrics['recall']}"
        assert train_metrics["fpr"] <= 0.10, f"Training FPR: {train_metrics['fpr']}"

        holdout_metrics = compute_metrics(labels["holdout_set"], obs_by_file)
        assert holdout_metrics["precision"] >= 0.80, f"Holdout precision: {holdout_metrics['precision']}"
        assert holdout_metrics["recall"] >= 0.80, f"Holdout recall: {holdout_metrics['recall']}"
