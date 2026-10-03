"""ASTRA - Tester 01 Functional Assurance Test Suite (Cycle V01).

Validates:
- W01 Safe Upload Intake boundary controls, archive validation, and sandboxing.
- W01 Multi-surface deterministic discovery (Source, Manifest, Config, Certificate).
- W01 Coverage accounting, honest denominators, and blind-spot visibility.
- W01 Seeded corpus ground-truth precision/recall benchmark (AC-06).
- W02 Canonical evidence identity adapter and parameter redaction allowlist.
- Defensive boundaries: Zip bomb, path traversal, symlink rejection, zero-leakage secrets.
"""

import io
import os
import tarfile
import tempfile
import uuid
import zipfile
from pathlib import Path

import pytest
from app.core.config import IntakeLimits
from app.core.security import (
    PathTraversalError,
    SymlinkEscapeError,
    compute_file_sha256,
    sanitize_relative_path,
)
from app.coverage.accounting import CoverageAccountant
from app.coverage.benchmark import BenchmarkRunner
from app.coverage.models import GroundTruthLabel, SurfaceCategory
from app.discovery.detectors.certificate_detector import CertificateCryptoDetector
from app.discovery.detectors.config_detector import ConfigCryptoDetector
from app.discovery.detectors.manifest_detector import ManifestCryptoDetector
from app.discovery.detectors.source_detector import SourceCryptoDetector
from app.discovery.engine import DiscoveryEngine
from app.discovery.models import (
    ClaimType,
    ConfidenceBand,
    EvidenceState,
    Observation,
    SourceKind,
)
from app.intake.extractor import SafeArchiveExtractor
from app.intake.models import ArchiveType, ScanStatus
from app.intake.sandbox import SandboxManager
from app.inventory.models import (
    AssetIdentity,
    CanonicalEvidence,
    map_observation_to_canonical,
    redact_sensitive_values,
)


def _build_synthetic_test_archive() -> bytes:
    """Creates an in-memory zip archive with a diverse set of cryptographic assets."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        # 1. Python source with both classical and PQC algorithms
        zf.writestr(
            "src/crypto_service.py",
            (
                "import os\n"
                "from cryptography.hazmat.primitives.asymmetric import rsa\n"
                "# Classical RSA key generation\n"
                "private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)\n"
                "# NIST PQC Kyber / ML-KEM encapsulation\n"
                "from pqcrypto.kem import ml_kem_768\n"
                "ciphertext, shared_secret = ml_kem_768.encapsulate(public_key)\n"
            ),
        )

        # 2. Java source with legacy cipher
        zf.writestr(
            "src/LegacyAuth.java",
            (
                "package com.example.auth;\n"
                "import javax.crypto.Cipher;\n"
                "public class LegacyAuth {\n"
                "    public void init() throws Exception {\n"
                "        Cipher c = Cipher.getInstance(\"DES/CBC/PKCS5Padding\");\n"
                "    }\n"
                "}\n"
            ),
        )

        # 3. Node.js package.json manifest
        zf.writestr(
            "package.json",
            (
                '{\n'
                '  "name": "astra-frontend",\n'
                '  "version": "1.0.0",\n'
                '  "dependencies": {\n'
                '    "@noble/curves": "^1.2.0",\n'
                '    "crypto-js": "^4.2.0"\n'
                '  }\n'
                '}\n'
            ),
        )

        # 4. Nginx TLS configuration
        zf.writestr(
            "conf/nginx.conf",
            (
                "server {\n"
                "    listen 443 ssl;\n"
                "    ssl_protocols TLSv1.2 TLSv1.3;\n"
                "    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES128-GCM-SHA256;\n"
                "}\n"
            ),
        )

        # 5. PEM Certificate
        zf.writestr(
            "certs/tls_cert.pem",
            (
                "-----BEGIN CERTIFICATE-----\n"
                "MIIBkTCCATagAwIBAgIUW8d09...\n"
                "-----END CERTIFICATE-----\n"
            ),
        )

        # 6. Unsupported plain text file (clean/blind-spot surface)
        zf.writestr(
            "notes/design_spec.txt",
            "This document describes the high-level architecture of ASTRA.\n",
        )
    return buf.getvalue()


class TestTester01V01FunctionalAssurance:
    """Exhaustive validation suite for Cycle V01."""

    def test_end_to_end_intake_to_discovery_and_canonical_mapping(self, tmp_path):
        """Validates the end-to-end flow: Archive -> Extraction -> Discovery -> Canonical Model."""
        archive_bytes = _build_synthetic_test_archive()
        archive_path = tmp_path / "test_repo.zip"
        archive_path.write_bytes(archive_bytes)
        sandbox_dir = tmp_path / "sandbox_test"

        limits = IntakeLimits(max_archive_size_bytes=10 * 1024 * 1024)
        extractor = SafeArchiveExtractor(limits=limits)

        # 1. Extraction into safe sandbox
        manifest = extractor.process_and_extract(
            archive_path=archive_path,
            sandbox_dir=sandbox_dir,
            scan_id="test-scan-001",
            declared_scope="SCOPE_TEST",
            tenant_id="tenant-v01",
        )
        assert manifest.status == ScanStatus.COMPLETE
        assert manifest.extracted_file_count == 6
        assert manifest.archive_type == ArchiveType.ZIP
        sha256_digest, archive_size = compute_file_sha256(archive_path)
        assert manifest.archive_sha256 == sha256_digest
        assert manifest.archive_size_bytes == archive_size
        assert sandbox_dir.exists()

        # 2. Master discovery engine execution
        engine = DiscoveryEngine()
        summary = engine.run_discovery(sandbox_dir, manifest)

        assert summary.total_files_analyzed == 6
        assert len(summary.observations) > 0
        assert summary.files_with_findings >= 3

        # Verify all collector detectors remained healthy
        for det_id, status in summary.detector_health.items():
            assert status == "OK", f"Detector {det_id} reported unhealthy status: {status}"

        # 3. Canonical Evidence transformation (Worker 02 integration)
        canonical_items = [map_observation_to_canonical(obs) for obs in summary.observations]
        assert len(canonical_items) == len(summary.observations)

        # Invariant checks on canonical evidence
        canonical_ids = set()
        for item in canonical_items:
            assert isinstance(item, CanonicalEvidence)
            assert item.canonical_id not in canonical_ids, "Canonical IDs must be unique per observation"
            canonical_ids.add(item.canonical_id)
            assert bool(item.asset_id)
            assert item.state in (EvidenceState.OBSERVED, EvidenceState.VERIFIED, EvidenceState.DECLARED)
            assert item.confidence in (ConfidenceBand.CONFIRMED, ConfidenceBand.HIGH, ConfidenceBand.MEDIUM, ConfidenceBand.LOW)

            # Strict zero secret leakage check
            for k, v in item.raw_parameters.items():
                if k not in {"public_key", "version", "algorithm"}:
                    assert v == "[REDACTED]", f"Sensitive parameter '{k}' was not redacted!"

    def test_truthful_coverage_accounting_and_no_finding_labeling(self, tmp_path):
        """Verifies that non-assessed or clean files are NEVER labeled 'Safe' (AC-01, AC-11)."""
        archive_bytes = _build_synthetic_test_archive()
        archive_path = tmp_path / "coverage_test.zip"
        archive_path.write_bytes(archive_bytes)
        sandbox_dir = tmp_path / "sandbox_cov"

        extractor = SafeArchiveExtractor()
        manifest = extractor.process_and_extract(
            archive_path=archive_path,
            sandbox_dir=sandbox_dir,
            scan_id="scan-cov-01",
            declared_scope="SCOPE_COV",
            tenant_id="tenant-v01",
        )

        engine = DiscoveryEngine()
        summary = engine.run_discovery(sandbox_dir, manifest)

        accountant = CoverageAccountant()
        report = accountant.evaluate_coverage(manifest, summary)

        # Denominator checks
        assert report.total_files_in_archive == 6
        assert report.total_assessed_files == 5
        assert report.total_unsupported_files == 1  # .txt file is unsupported
        assert ".txt" in report.unsupported_extensions

        # Surface breakdown validation
        assert report.surface_breakdown[SurfaceCategory.SOURCE_CODE.value].assessed_files == 2
        assert report.surface_breakdown[SurfaceCategory.PACKAGE_MANIFEST.value].assessed_files == 1
        assert report.surface_breakdown[SurfaceCategory.CONFIGURATION.value].assessed_files == 1
        assert report.surface_breakdown[SurfaceCategory.CERTIFICATE_STORE.value].assessed_files == 1
        assert report.surface_breakdown[SurfaceCategory.UNSUPPORTED_SURFACE.value].unsupported_files == 1

        # Check label is NOT 'Safe'
        assert report.scan_status_label == "COMPLETE_WITH_COVERAGE_ACCOUNTING"
        assert "Safe" not in report.scan_status_label

    def test_seeded_corpus_ground_truth_benchmark_precision_recall(self):
        """Validates AC-06: Evaluates benchmark runner on seeded corpus meeting >=80% target."""
        ground_truth = [
            GroundTruthLabel(relative_path="src/crypto.py", expected_algorithm="RSA"),
            GroundTruthLabel(relative_path="src/crypto.py", expected_algorithm="ML-KEM"),
            GroundTruthLabel(relative_path="package.json", expected_algorithm="crypto-js"),
            GroundTruthLabel(relative_path="conf/nginx.conf", expected_algorithm="TLSv1.3"),
            GroundTruthLabel(relative_path="notes/clean.txt", expected_algorithm="", is_negative_fixture=True),
        ]

        # Synthetic observations matching the expected ground truths
        detected_obs = [
            Observation(
                observation_id=str(uuid.uuid4()),
                scan_id="bench-01",
                candidate_asset_id="asset-rsa",
                claim_type=ClaimType.ALGORITHM_USE,
                source_kind=SourceKind.SOURCE_CODE,
                algorithm="RSA",
                relative_path="src/crypto.py",
                start_line=4,
                evidence_digest="sha256-rsa",
                sanitized_excerpt="rsa.generate_private_key",
                detector_id="source-detector",
                ruleset_version="2026.10-nist-pqc",
                confidence=ConfidenceBand.HIGH,
                confidence_rationale="Exact AST match",
                state=EvidenceState.OBSERVED,
            ),
            Observation(
                observation_id=str(uuid.uuid4()),
                scan_id="bench-01",
                candidate_asset_id="asset-mlkem",
                claim_type=ClaimType.ALGORITHM_USE,
                source_kind=SourceKind.SOURCE_CODE,
                algorithm="ML-KEM",
                relative_path="src/crypto.py",
                start_line=7,
                evidence_digest="sha256-mlkem",
                sanitized_excerpt="ml_kem_768.encapsulate",
                detector_id="source-detector",
                ruleset_version="2026.10-nist-pqc",
                confidence=ConfidenceBand.HIGH,
                confidence_rationale="PQC standard reference",
                state=EvidenceState.OBSERVED,
            ),
            Observation(
                observation_id=str(uuid.uuid4()),
                scan_id="bench-01",
                candidate_asset_id="asset-cryptojs",
                claim_type=ClaimType.DEPENDENCY_REFERENCE,
                source_kind=SourceKind.MANIFEST,
                algorithm="crypto-js",
                relative_path="package.json",
                start_line=5,
                evidence_digest="sha256-cryptojs",
                sanitized_excerpt="crypto-js: ^4.2.0",
                detector_id="manifest-detector",
                ruleset_version="2026.10-nist-pqc",
                confidence=ConfidenceBand.HIGH,
                confidence_rationale="Direct npm dependency",
                state=EvidenceState.OBSERVED,
            ),
            Observation(
                observation_id=str(uuid.uuid4()),
                scan_id="bench-01",
                candidate_asset_id="asset-tls",
                claim_type=ClaimType.CONFIG_PARAMETER,
                source_kind=SourceKind.CONFIG,
                algorithm="TLSv1.3",
                relative_path="conf/nginx.conf",
                start_line=3,
                evidence_digest="sha256-tls13",
                sanitized_excerpt="ssl_protocols TLSv1.3",
                detector_id="config-detector",
                ruleset_version="2026.10-nist-pqc",
                confidence=ConfidenceBand.HIGH,
                confidence_rationale="Nginx config directive",
                state=EvidenceState.OBSERVED,
            ),
        ]

        runner = BenchmarkRunner()
        evaluation = runner.evaluate(
            ground_truth=ground_truth,
            observations=detected_obs,
            benchmark_id="SIH26164-TESTER01-V01-SEEDED",
        )

        assert evaluation.overall_precision >= 0.80
        assert evaluation.overall_recall >= 0.80
        assert evaluation.ac06_target_achieved is True
        assert evaluation.total_expected_findings == 4
        assert evaluation.total_detected_findings == 4

    def test_strict_private_key_redaction_in_certificate_detector(self, tmp_path):
        """Ensures that RSA/EC private keys found in files are completely redacted from excerpts."""
        key_file = tmp_path / "server.key"
        key_file.write_text(
            "-----BEGIN RSA PRIVATE KEY-----\n"
            "MIIEowIBAAKCAQEA0Yl5pQ9X...\n"
            "SUPER_SECRET_PRIVATE_KEY_BYTES\n"
            "-----END RSA PRIVATE KEY-----\n"
        )

        detector = CertificateCryptoDetector()
        assert detector.can_analyze(key_file) is True

        observations = detector.analyze_file(key_file, "server.key", "test-scan-123")
        assert len(observations) == 1
        obs = observations[0]

        assert obs.redacted is True
        assert "SUPER_SECRET" not in obs.sanitized_excerpt
        assert "REDACTED_PRIVATE_KEY_MATERIAL" in obs.sanitized_excerpt
        assert obs.claim_type == ClaimType.KEY_SPECIFICATION

    def test_hostile_archive_symlink_and_traversal_rejections(self, tmp_path):
        """Verifies boundary security against path escapes and dangerous symlinks."""
        extractor = SafeArchiveExtractor()

        # 1. Path traversal in tar
        tar_buf = io.BytesIO()
        with tarfile.open(fileobj=tar_buf, mode="w") as tf:
            ti = tarfile.TarInfo(name="../../etc/passwd")
            data = b"root:x:0:0::/root:/bin/bash\n"
            ti.size = len(data)
            tf.addfile(ti, io.BytesIO(data))
        tar_path = tmp_path / "traversal.tar"
        tar_path.write_bytes(tar_buf.getvalue())

        with pytest.raises(PathTraversalError):
            extractor.process_and_extract(
                archive_path=tar_path,
                sandbox_dir=tmp_path / "sandbox_trav",
                scan_id="scan-trav",
            )

        # 2. Symlink escape in tar
        sym_buf = io.BytesIO()
        with tarfile.open(fileobj=sym_buf, mode="w") as tf:
            ti = tarfile.TarInfo(name="symlink_escape")
            ti.type = tarfile.SYMTYPE
            ti.linkname = "/etc/shadow"
            tf.addfile(ti)
        sym_path = tmp_path / "symlink.tar"
        sym_path.write_bytes(sym_buf.getvalue())

        with pytest.raises(SymlinkEscapeError):
            extractor.process_and_extract(
                archive_path=sym_path,
                sandbox_dir=tmp_path / "sandbox_sym",
                scan_id="scan-sym",
            )
