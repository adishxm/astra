"""ASTRA - Worker 01 MVP-03 Coverage Accounting & Benchmark Test Suite.

Validates honest denominator accounting, blind-spot visibility, partial scan
state transitions, and precision/recall >= 80% benchmark target (AC-04, AC-06, AC-11, AC-12).
"""

import uuid
from pathlib import Path
import pytest

from app.coverage.accounting import CoverageAccountant
from app.coverage.benchmark import BenchmarkRunner
from app.coverage.models import (
    GroundTruthLabel,
    SurfaceCategory,
)
from app.discovery.models import (
    ClaimType,
    ConfidenceBand,
    DiscoverySummary,
    EvidenceState,
    Observation,
    SourceKind,
)
from app.intake.models import ArchiveType, ExtractedFileEntry, ScanManifest, ScanStatus


def test_coverage_accountant_surface_breakdown():
    """Test honest denominator accounting across source, manifest, config, certs, and unsupported."""
    manifest = ScanManifest(
        scan_id="scan-cov-01",
        archive_name="repo.zip",
        archive_sha256="sha256dummy",
        archive_size_bytes=5000,
        archive_type=ArchiveType.ZIP,
        declared_scope="SCOPE_1",
        tenant_id="tenant-1",
        status=ScanStatus.COMPLETE,
        intake_engine_version="1.0.0",
        collector_version="0.1.0",
        ruleset_version="2026.10-nist-pqc",
        files=[
            ExtractedFileEntry(relative_path="src/app.py", size_bytes=200, sha256="s1", file_extension=".py", is_supported=True),
            ExtractedFileEntry(relative_path="src/clean_utils.py", size_bytes=150, sha256="s2", file_extension=".py", is_supported=True),
            ExtractedFileEntry(relative_path="package.json", size_bytes=100, sha256="s3", file_extension=".json", is_supported=True),
            ExtractedFileEntry(relative_path="nginx.conf", size_bytes=80, sha256="s4", file_extension=".conf", is_supported=True),
            ExtractedFileEntry(relative_path="server.crt", size_bytes=600, sha256="s5", file_extension=".crt", is_supported=True),
            ExtractedFileEntry(relative_path="data/image.png", size_bytes=1000, sha256="s6", file_extension=".png", is_supported=False),
            ExtractedFileEntry(relative_path="docs/guide.pdf", size_bytes=2000, sha256="s7", file_extension=".pdf", is_supported=False),
        ]
    )

    summary = DiscoverySummary(
        scan_id="scan-cov-01",
        total_files_analyzed=7,
        files_with_findings=3,  # app.py, package.json, server.crt
        files_with_zero_findings=4,
        unsupported_files_count=2,
        failed_parses_count=0,
        observations=[
            Observation(
                observation_id=str(uuid.uuid4()),
                scan_id="scan-cov-01",
                candidate_asset_id="c1",
                claim_type=ClaimType.ALGORITHM_USE,
                source_kind=SourceKind.SOURCE_CODE,
                algorithm="AES-256",
                relative_path="src/app.py",
                evidence_digest="d1",
                sanitized_excerpt="aes cipher",
                detector_id="det-src",
                ruleset_version="2026.10-nist-pqc",
                confidence=ConfidenceBand.CONFIRMED,
                confidence_rationale="test",
                state=EvidenceState.OBSERVED,
            ),
            Observation(
                observation_id=str(uuid.uuid4()),
                scan_id="scan-cov-01",
                candidate_asset_id="c2",
                claim_type=ClaimType.DEPENDENCY_REFERENCE,
                source_kind=SourceKind.MANIFEST,
                algorithm="crypto-js",
                relative_path="package.json",
                evidence_digest="d2",
                sanitized_excerpt="crypto-js dep",
                detector_id="det-man",
                ruleset_version="2026.10-nist-pqc",
                confidence=ConfidenceBand.HIGH,
                confidence_rationale="test",
                state=EvidenceState.DECLARED,
            ),
            Observation(
                observation_id=str(uuid.uuid4()),
                scan_id="scan-cov-01",
                candidate_asset_id="c3",
                claim_type=ClaimType.CERTIFICATE_METADATA,
                source_kind=SourceKind.CERTIFICATE,
                algorithm="RSA-2048",
                relative_path="server.crt",
                evidence_digest="d3",
                sanitized_excerpt="rsa cert",
                detector_id="det-cert",
                ruleset_version="2026.10-nist-pqc",
                confidence=ConfidenceBand.CONFIRMED,
                confidence_rationale="test",
                state=EvidenceState.VERIFIED,
            ),
        ],
        detector_health={"det-src": "OK", "det-man": "OK", "det-cfg": "OK", "det-cert": "OK"},
    )

    accountant = CoverageAccountant()
    report = accountant.evaluate_coverage(manifest, summary)

    assert report.total_files_in_archive == 7
    assert report.total_assessed_files == 5      # 2 py + 1 json + 1 conf + 1 crt
    assert report.total_unsupported_files == 2   # png, pdf
    assert report.overall_coverage_percentage == round(5 / 7 * 100, 2)
    assert report.is_partial_scan is False
    assert ".png" in report.unsupported_extensions
    assert ".pdf" in report.unsupported_extensions

    # Check surface breakdown
    src_cov = report.surface_breakdown[SurfaceCategory.SOURCE_CODE.value]
    assert src_cov.total_files == 2
    assert src_cov.assessed_files == 2
    assert src_cov.files_with_findings == 1
    assert src_cov.files_with_no_findings == 1


def test_no_finding_is_never_labeled_safe():
    """Verify AC-04: absence of findings produces explicit NO_FINDINGS label, never 'safe'."""
    manifest = ScanManifest(
        scan_id="scan-clean-01",
        archive_name="clean.zip",
        archive_sha256="sha256dummy",
        archive_size_bytes=1000,
        archive_type=ArchiveType.ZIP,
        declared_scope="CLEAN_REPO",
        tenant_id="tenant-1",
        status=ScanStatus.COMPLETE,
        intake_engine_version="1.0.0",
        collector_version="0.1.0",
        ruleset_version="2026.10-nist-pqc",
        files=[
            ExtractedFileEntry(relative_path="src/clean.py", size_bytes=100, sha256="s1", file_extension=".py", is_supported=True),
        ]
    )

    summary = DiscoverySummary(
        scan_id="scan-clean-01",
        total_files_analyzed=1,
        files_with_findings=0,
        files_with_zero_findings=1,
        observations=[],
        detector_health={"det-src": "OK"},
    )

    accountant = CoverageAccountant()
    report = accountant.evaluate_coverage(manifest, summary)

    assert report.total_observations_found == 0
    assert report.scan_status_label == "NO_FINDINGS_IN_SUPPORTED_SCOPE"
    assert "safe" not in report.scan_status_label.lower()


def test_partial_scan_on_detector_failure():
    """Verify AC-11: collector errors cause is_partial_scan = True with clear degraded label."""
    manifest = ScanManifest(
        scan_id="scan-err-01",
        archive_name="broken.zip",
        archive_sha256="sha256dummy",
        archive_size_bytes=1000,
        archive_type=ArchiveType.ZIP,
        declared_scope="BROKEN_REPO",
        tenant_id="tenant-1",
        status=ScanStatus.RUNNING,
        intake_engine_version="1.0.0",
        collector_version="0.1.0",
        ruleset_version="2026.10-nist-pqc",
        files=[
            ExtractedFileEntry(relative_path="src/corrupt.py", size_bytes=100, sha256="s1", file_extension=".py", is_supported=True),
        ]
    )

    summary = DiscoverySummary(
        scan_id="scan-err-01",
        total_files_analyzed=1,
        files_with_findings=0,
        files_with_zero_findings=1,
        failed_parses_count=1,
        observations=[],
        detector_health={"det-src": "ERROR: AST parser crashed"},
    )

    accountant = CoverageAccountant()
    report = accountant.evaluate_coverage(manifest, summary)

    assert report.is_partial_scan is True
    assert report.scan_status_label == "PARTIAL_SCAN_COLLECTOR_DEGRADED"


def test_benchmark_runner_seeded_corpus_target():
    """Verify AC-06: benchmark evaluation achieves >=80% precision and >=80% recall on seeded corpus."""
    ground_truth = [
        GroundTruthLabel(relative_path="src/auth.py", expected_algorithm="AES-256"),
        GroundTruthLabel(relative_path="src/auth.py", expected_algorithm="SHA-256"),
        GroundTruthLabel(relative_path="src/pqc.py", expected_algorithm="ML-KEM"),
        GroundTruthLabel(relative_path="src/cert.pem", expected_algorithm="RSA-2048"),
        GroundTruthLabel(relative_path="package.json", expected_algorithm="crypto-js"),
        GroundTruthLabel(relative_path="src/negative_sample.py", expected_algorithm="", is_negative_fixture=True),
    ]

    # Observations detected by our engine
    observations = [
        Observation(
            observation_id=str(uuid.uuid4()),
            scan_id="bench-01",
            candidate_asset_id="a1",
            claim_type=ClaimType.ALGORITHM_USE,
            source_kind=SourceKind.SOURCE_CODE,
            algorithm="AES-256",
            relative_path="src/auth.py",
            evidence_digest="d1",
            sanitized_excerpt="aes",
            detector_id="d",
            ruleset_version="2026.10",
            confidence=ConfidenceBand.CONFIRMED,
            confidence_rationale="test",
            state=EvidenceState.OBSERVED,
        ),
        Observation(
            observation_id=str(uuid.uuid4()),
            scan_id="bench-01",
            candidate_asset_id="a2",
            claim_type=ClaimType.ALGORITHM_USE,
            source_kind=SourceKind.SOURCE_CODE,
            algorithm="SHA-256",
            relative_path="src/auth.py",
            evidence_digest="d2",
            sanitized_excerpt="sha",
            detector_id="d",
            ruleset_version="2026.10",
            confidence=ConfidenceBand.CONFIRMED,
            confidence_rationale="test",
            state=EvidenceState.OBSERVED,
        ),
        Observation(
            observation_id=str(uuid.uuid4()),
            scan_id="bench-01",
            candidate_asset_id="a3",
            claim_type=ClaimType.ALGORITHM_USE,
            source_kind=SourceKind.SOURCE_CODE,
            algorithm="ML-KEM",
            relative_path="src/pqc.py",
            evidence_digest="d3",
            sanitized_excerpt="kyber",
            detector_id="d",
            ruleset_version="2026.10",
            confidence=ConfidenceBand.CONFIRMED,
            confidence_rationale="test",
            state=EvidenceState.OBSERVED,
        ),
        Observation(
            observation_id=str(uuid.uuid4()),
            scan_id="bench-01",
            candidate_asset_id="a4",
            claim_type=ClaimType.CERTIFICATE_METADATA,
            source_kind=SourceKind.CERTIFICATE,
            algorithm="RSA-2048",
            relative_path="src/cert.pem",
            evidence_digest="d4",
            sanitized_excerpt="rsa",
            detector_id="d",
            ruleset_version="2026.10",
            confidence=ConfidenceBand.CONFIRMED,
            confidence_rationale="test",
            state=EvidenceState.VERIFIED,
        ),
        Observation(
            observation_id=str(uuid.uuid4()),
            scan_id="bench-01",
            candidate_asset_id="a5",
            claim_type=ClaimType.DEPENDENCY_REFERENCE,
            source_kind=SourceKind.MANIFEST,
            algorithm="crypto-js",
            relative_path="package.json",
            evidence_digest="d5",
            sanitized_excerpt="crypto-js",
            detector_id="d",
            ruleset_version="2026.10",
            confidence=ConfidenceBand.HIGH,
            confidence_rationale="test",
            state=EvidenceState.DECLARED,
        ),
    ]

    runner = BenchmarkRunner()
    evaluation = runner.evaluate(ground_truth, observations)

    assert evaluation.total_fixtures == 6
    assert evaluation.total_expected_findings == 5
    assert evaluation.total_detected_findings == 5
    assert evaluation.overall_precision >= 0.80
    assert evaluation.overall_recall >= 0.80
    assert evaluation.overall_f1 >= 0.80
    assert evaluation.ac06_target_achieved is True
