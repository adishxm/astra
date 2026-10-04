"""ASTRA - End-to-End Ground Truth Cryptographic Benchmark (Worker 02 - Phase C).

Executes the discovery engine and scan pipeline across a multi-surface,
multi-language labeled cryptographic test corpus (including negative controls
and unseen holdout fixtures).

Computes and validates:
  - Precision = TP / (TP + FP) >= 0.80
  - Recall    = TP / (TP + FN) >= 0.80
  - F1 Score  = 2 * (P * R) / (P + R) >= 0.80
  - False Positive Rate (FPR) = FP / (FP + TN) <= 0.10
across Source Code, Dependency Manifests, Certificates/Keys, and TLS Configs.
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple

import pytest

from app.services.scan_service import ScanService, ScanRecord


CORPUS_DIR = Path(__file__).parent / "fixtures" / "corpus"
LABELS_FILE = CORPUS_DIR / "labels.json"


@pytest.fixture(scope="module")
def corpus_labels() -> Dict:
    """Load the ground truth labels specification."""
    assert LABELS_FILE.exists(), f"Corpus labels file not found at {LABELS_FILE}"
    with open(LABELS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def corpus_scan_record() -> ScanRecord:
    """Run an end-to-end directory scan against the full test corpus."""
    service = ScanService()
    record = service.run_scan_on_directory(
        directory_path=str(CORPUS_DIR),
        target_name="ASTRA Ground Truth Corpus",
    )
    return record


def algo_matches(expected: str, detected: str) -> bool:
    """Strict canonical algorithm matcher with verified cryptographic aliases."""
    exp = expected.upper().replace("-", "").replace("_", "")
    det = detected.upper().replace("-", "").replace("_", "")

    if exp == det:
        return True

    aliases = {
        "ECDSA": ["ECCCURVE", "SECP256R1", "PRIME256V1", "EC", "ECC"],
        "EC": ["ECCCURVE", "SECP256R1", "PRIME256V1", "ECDSA", "ECC"],
        "CHACHA20": ["CHACHA20POLY1305"],
        "CHACHA20POLY1305": ["CHACHA20"],
        "RSA2048": ["RSA"],
        "RSA": ["RSA2048", "RSAPSS"],
        "AES256": ["AES", "AES256GCM", "ECDHEAES256GCM"],
        "AES128": ["AES", "AES128GCM", "ECDHEAES128GCM"],
        "AES": ["AES256", "AES128", "AESGCM", "AES256GCM"],
        "AESGCM": ["AES256GCM", "AES128GCM", "AES", "AES256"],
        "AES256GCM": ["AESGCM", "AES256", "AES"],
        "ED25519": ["EDDSA"],
        "OPENSSL": ["OPENSSL3X", "OPENSSL11", "OPENSSLDEV", "LIBSSL"],
        "OPENSSL3X": ["OPENSSL", "LIBSSL3"],
    }
    if exp in aliases and det in aliases[exp]:
        return True
    if det in aliases and exp in aliases[det]:
        return True

    return False


def compute_metrics(
    entries: List[Dict],
    observations_by_file: Dict[str, List[str]],
) -> Dict[str, float]:
    """Compute finding-level TP, FP, FN, TN, Precision, Recall, F1, and Negative Control FPR.

    Accounting Rules (Honest Scientific Evaluation):
    - On positive files:
      - Matched distinct algorithms count as TP.
      - Expected algorithms not matched count as FN.
      - Extra / unlabelled detected algorithms count as FP.
    - On negative control files:
      - Clean files with 0 detections count as TN.
      - Any detected algorithms count as FP.
    - Negative control FPR = neg_control_violations / neg_control_files (consistent file unit).
    - Finding-level Precision = TP / (TP + FP)
    - Finding-level Recall = TP / (TP + FN)
    - Finding-level F1 = 2 * (P * R) / (P + R)
    """
    tp = 0
    fp = 0
    fn = 0
    tn_files = 0
    neg_control_files = 0
    neg_control_violations = 0

    for entry in entries:
        rel_p = entry["relative_path"]
        expected = entry.get("expected_algorithms", [])
        raw_detected = observations_by_file.get(rel_p, [])

        # Extract distinct detected algorithms for this file
        distinct_detected: List[str] = []
        for det in raw_detected:
            if not any(algo_matches(det, existing) for existing in distinct_detected):
                distinct_detected.append(det)

        if entry.get("is_negative", False):
            neg_control_files += 1
            if len(distinct_detected) == 0:
                tn_files += 1
            else:
                neg_control_violations += 1
                fp += len(distinct_detected)
        else:
            used_det = set()
            for exp in expected:
                matched_idx = None
                for idx, det in enumerate(distinct_detected):
                    if idx not in used_det and algo_matches(exp, det):
                        matched_idx = idx
                        break
                if matched_idx is not None:
                    tp += 1
                    used_det.add(matched_idx)
                else:
                    fn += 1

            # Every extra, unlabelled algorithm detected on a positive file is an FP
            for idx in range(len(distinct_detected)):
                if idx not in used_det:
                    fp += 1

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    fpr = neg_control_violations / neg_control_files if neg_control_files > 0 else 0.0

    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn_files,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "fpr": fpr,
    }


def _group_observations(record: ScanRecord) -> Dict[str, List[str]]:
    obs_by_file: Dict[str, List[str]] = {}
    for obs in record.observations:
        norm_path = obs.relative_path.replace("\\", "/")
        obs_by_file.setdefault(norm_path, []).append(obs.algorithm)
    return obs_by_file


def test_corpus_execution_no_unhandled_exceptions(corpus_scan_record: ScanRecord):
    """Verify that scan completes cleanly with findings and non-zero coverage."""
    assert corpus_scan_record.status == "completed"
    assert len(corpus_scan_record.observations) > 0
    assert corpus_scan_record.coverage.total_assessed_files > 0


def test_corpus_negative_fixtures_true_negative_rate(
    corpus_labels: Dict,
    corpus_scan_record: ScanRecord,
):
    """Verify that negative control fixtures (comments, mock math, clean configs) emit 0 false alarms."""
    obs_by_file = _group_observations(corpus_scan_record)
    all_entries = corpus_labels["training_set"] + corpus_labels["holdout_set"]
    negative_entries = [e for e in all_entries if e.get("is_negative")]

    assert len(negative_entries) > 0

    false_alarms = []
    for entry in negative_entries:
        rel_p = entry["relative_path"]
        detected = obs_by_file.get(rel_p, [])
        if detected:
            false_alarms.append((rel_p, detected))

    assert len(false_alarms) == 0, f"False positives detected in negative controls: {false_alarms}"


def test_corpus_precision_recall_benchmark(
    corpus_labels: Dict,
    corpus_scan_record: ScanRecord,
):
    """Verify that the primary training corpus satisfies research-grade gates (P >= 80%, R >= 80%)."""
    obs_by_file = _group_observations(corpus_scan_record)
    metrics = compute_metrics(corpus_labels["training_set"], obs_by_file)

    print("\n[Phase C Benchmark — Training Set]")
    print(f"TP={metrics['tp']}, FP={metrics['fp']}, FN={metrics['fn']}, TN={metrics['tn']}")
    print(f"Precision: {metrics['precision'] * 100:.2f}% (Threshold: >= 80.00%)")
    print(f"Recall:    {metrics['recall'] * 100:.2f}% (Threshold: >= 80.00%)")
    print(f"F1 Score:  {metrics['f1'] * 100:.2f}%")
    print(f"FPR:       {metrics['fpr'] * 100:.2f}%")

    assert metrics["precision"] >= 0.80, f"Precision below research threshold: {metrics['precision']:.3f}"
    assert metrics["recall"] >= 0.80, f"Recall below research threshold: {metrics['recall']:.3f}"
    assert metrics["fpr"] <= 0.10, f"FPR exceeds limit: {metrics['fpr']:.3f}"


def test_holdout_generalization_benchmark(
    corpus_labels: Dict,
    corpus_scan_record: ScanRecord,
):
    """Verify that the unseen holdout set validates detector generalization without overfitting."""
    obs_by_file = _group_observations(corpus_scan_record)
    metrics = compute_metrics(corpus_labels["holdout_set"], obs_by_file)

    print("\n[Phase C Benchmark — Holdout Set]")
    print(f"TP={metrics['tp']}, FP={metrics['fp']}, FN={metrics['fn']}, TN={metrics['tn']}")
    print(f"Precision: {metrics['precision'] * 100:.2f}% (Threshold: >= 80.00%)")
    print(f"Recall:    {metrics['recall'] * 100:.2f}% (Threshold: >= 80.00%)")
    print(f"F1 Score:  {metrics['f1'] * 100:.2f}%")

    assert metrics["precision"] >= 0.80, f"Holdout precision below threshold: {metrics['precision']:.3f}"
    assert metrics["recall"] >= 0.80, f"Holdout recall below threshold: {metrics['recall']:.3f}"


def test_per_surface_breakdown(
    corpus_labels: Dict,
    corpus_scan_record: ScanRecord,
):
    """Verify quality across distinct surfaces: SOURCE_CODE, MANIFEST, CERTIFICATE, CONFIG."""
    obs_by_file = _group_observations(corpus_scan_record)
    all_entries = corpus_labels["training_set"] + corpus_labels["holdout_set"]

    surfaces = {
        "SOURCE_CODE",
        "MANIFEST",
        "CERTIFICATE",
        "CONFIG",
        "CONTAINER",
        "CLOUD_KMS",
        "PKCS11_HSM",
    }

    for surface in surfaces:
        surface_entries = [e for e in all_entries if e.get("surface") == surface]
        metrics = compute_metrics(surface_entries, obs_by_file)

        print(f"\n[Surface Breakdown: {surface}]")
        print(f"TP={metrics['tp']}, FP={metrics['fp']}, FN={metrics['fn']}, TN={metrics['tn']}")
        print(f"Precision: {metrics['precision'] * 100:.2f}% | Recall: {metrics['recall'] * 100:.2f}%")

        assert metrics["precision"] >= 0.80, f"{surface} precision below 80%: {metrics['precision']}"
        assert metrics["recall"] >= 0.80, f"{surface} recall below 80%: {metrics['recall']}"
