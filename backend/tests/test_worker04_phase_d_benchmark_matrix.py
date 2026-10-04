"""ASTRA - Worker 04 Phase D Ground Truth Benchmark & Confusion Matrix Validation.

Verifies:
  1. Multi-surface empirical benchmark execution with bipartite finding-level matching.
  2. Strict performance gates: Precision >= 80%, Recall >= 80%, F1 >= 80%, FPR <= 10%
     across all surfaces (SOURCE_CODE, MANIFEST, CONFIG, CERTIFICATE, CONTAINER, CLOUD_KMS, PKCS11_HSM).
  3. Negative controls produce zero false alarms across diverse deceptive syntax.
  4. Generation of machine-readable confusion matrices with TP, FP, FN, TN, and rates.
"""

import json
from pathlib import Path
from typing import Dict, List

import pytest

from app.services.scan_service import ScanService, ScanRecord
from tests.test_e2e_corpus_benchmark import (
    CORPUS_DIR,
    LABELS_FILE,
    algo_matches,
    compute_metrics,
    _group_observations,
)


@pytest.fixture(scope="module")
def corpus_labels() -> Dict:
    with open(LABELS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def benchmark_scan_record() -> ScanRecord:
    service = ScanService()
    record = service.run_scan_on_directory(
        directory_path=str(CORPUS_DIR),
        target_name="ASTRA Ground Truth Benchmark Corpus",
    )
    return record


def test_confusion_matrix_all_surfaces(corpus_labels: Dict, benchmark_scan_record: ScanRecord):
    """Compute and validate structured confusion matrices across all 7 distinct surfaces."""
    obs_by_file = _group_observations(benchmark_scan_record)
    all_entries = corpus_labels["training_set"] + corpus_labels["holdout_set"]

    expected_surfaces = [
        "SOURCE_CODE",
        "MANIFEST",
        "CONFIG",
        "CERTIFICATE",
        "CONTAINER",
        "CLOUD_KMS",
        "PKCS11_HSM",
    ]

    confusion_matrices = {}

    for surface in expected_surfaces:
        surface_entries = [e for e in all_entries if e.get("surface") == surface]
        assert len(surface_entries) > 0, f"No entries found for surface: {surface}"

        matrix = compute_metrics(surface_entries, obs_by_file)
        confusion_matrices[surface] = matrix

        # Research-grade thresholds
        assert matrix["precision"] >= 0.80, f"{surface} Precision failed: {matrix['precision']:.3f}"
        assert matrix["recall"] >= 0.80, f"{surface} Recall failed: {matrix['recall']:.3f}"
        assert matrix["fpr"] <= 0.10, f"{surface} FPR exceeded limit: {matrix['fpr']:.3f}"

    # Verify all expected surfaces are present
    assert set(confusion_matrices.keys()) == set(expected_surfaces)


def test_holdout_set_zero_overfitting(corpus_labels: Dict, benchmark_scan_record: ScanRecord):
    """Validate that the held-out generalization set meets >= 80% F1 score."""
    obs_by_file = _group_observations(benchmark_scan_record)
    holdout_metrics = compute_metrics(corpus_labels["holdout_set"], obs_by_file)

    assert holdout_metrics["precision"] >= 0.80
    assert holdout_metrics["recall"] >= 0.80
    assert holdout_metrics["f1"] >= 0.80
    assert holdout_metrics["tp"] >= 15


def test_negative_controls_zero_false_alarms(corpus_labels: Dict, benchmark_scan_record: ScanRecord):
    """Validate that deceptive variable names (aes_padding, rsa_margin) produce 0 false alarms."""
    obs_by_file = _group_observations(benchmark_scan_record)
    all_entries = corpus_labels["training_set"] + corpus_labels["holdout_set"]
    negative_entries = [e for e in all_entries if e.get("is_negative")]

    assert len(negative_entries) >= 6

    for neg in negative_entries:
        rel_p = neg["relative_path"]
        detected = obs_by_file.get(rel_p, [])
        assert len(detected) == 0, f"False positive detected on negative control {rel_p}: {detected}"


def test_confusion_matrix_json_serialization(corpus_labels: Dict, benchmark_scan_record: ScanRecord):
    """Validate that confusion matrices can be exported to JSON for automated audit logs."""
    obs_by_file = _group_observations(benchmark_scan_record)
    all_entries = corpus_labels["training_set"] + corpus_labels["holdout_set"]

    matrix_export = {
        "benchmark_corpus": "ASTRA Ground Truth Corpus v1.0",
        "surfaces": {},
    }

    for surface in ["SOURCE_CODE", "MANIFEST", "CONFIG", "CERTIFICATE", "CONTAINER", "CLOUD_KMS", "PKCS11_HSM"]:
        surface_entries = [e for e in all_entries if e.get("surface") == surface]
        matrix_export["surfaces"][surface] = compute_metrics(surface_entries, obs_by_file)

    serialized = json.dumps(matrix_export, indent=2)
    assert len(serialized) > 100
    deserialized = json.loads(serialized)
    assert "surfaces" in deserialized
    assert deserialized["surfaces"]["CLOUD_KMS"]["tp"] >= 3
    assert deserialized["surfaces"]["PKCS11_HSM"]["tp"] >= 4
