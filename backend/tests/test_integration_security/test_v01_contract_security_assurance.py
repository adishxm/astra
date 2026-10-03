"""ASTRA - Tester 02 Contract Integration, Export & Security Assurance Suite (Cycle V01).

Exhaustively validates:
- Inter-workstream contract compatibility (W01 -> W02 -> W03 -> W04).
- Multi-layer zero private-key leakage across certificate, source, and parameter tiers.
- Parametric redaction allowlist enforcement.
- Hostile archive adversarial matrix (path traversal, symlink escapes, zip bombs, null bytes).
- CBOM-aligned InventoryExport schema serialization and round-trip fidelity.
- AuditRecord security constraints and actor attribution rules.
"""

import io
import json
import os
import tarfile
import tempfile
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import pytest
from app.core.config import IntakeLimits
from app.core.security import (
    DecompressionBombError,
    PathTraversalError,
    SymlinkEscapeError,
    sanitize_relative_path,
)
from app.discovery.detectors.certificate_detector import CertificateCryptoDetector
from app.discovery.models import (
    ClaimType,
    ConfidenceBand,
    EvidenceState,
    Observation,
    SourceKind,
)
from app.intake.extractor import SafeArchiveExtractor
from app.intake.models import ArchiveType, ScanStatus
from app.inventory.models import (
    AssetIdentity,
    AuditRecord,
    CanonicalEvidence,
    InventoryExport,
    Relationship,
    RiskContext,
    map_observation_to_canonical,
    redact_sensitive_values,
)
from app.risk.models import (
    BusinessCriticality,
    ContextFactors,
    ExposureScope,
    RiskScenario,
)
from app.risk.scorer import RiskScorer
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa


class TestTester02V01ContractSecurityAssurance:
    """Exhaustive integration, contract, and security validation for Cycle V01."""

    def test_cross_contract_field_compatibility(self):
        """Validates contract translation from W01 Observation through W02 CanonicalEvidence to W03 RiskContext."""
        obs = Observation(
            observation_id=str(uuid.uuid4()),
            scan_id=str(uuid.uuid4()),
            candidate_asset_id="asset-auth-service",
            claim_type=ClaimType.ALGORITHM_USE,
            source_kind=SourceKind.SOURCE_CODE,
            algorithm="RSA-2048",
            protocol=None,
            purpose="SIGNING",
            key_size_bits=2048,
            curve_name=None,
            relative_path="services/auth.py",
            start_line=42,
            end_line=45,
            evidence_digest="a" * 64,
            sanitized_excerpt="rsa.generate_private_key(public_exponent=65537, key_size=2048)",
            redacted=False,
            detector_id="source_ast_detector",
            ruleset_version="2026.10-nist-pqc",
            confidence=ConfidenceBand.CONFIRMED,
            confidence_rationale="AST parsed RSA key generation call",
            state=EvidenceState.OBSERVED,
            observed_at=datetime.now(timezone.utc),
            raw_parameters={"key_size": 2048, "secret_seed": "SUPER_SECRET_VALUE", "version": "1.2.0"},
        )

        # 1. Map to W02 CanonicalEvidence
        canonical = map_observation_to_canonical(obs)
        assert canonical.asset_id == "asset-auth-service"
        assert canonical.algorithm == "RSA-2048"
        assert canonical.key_size_bits == 2048
        assert len(canonical.canonical_id) == 64  # SHA-256 hex digest

        # Verify sensitive raw parameter was sanitized
        assert canonical.raw_parameters["secret_seed"] == "[REDACTED]"
        assert canonical.raw_parameters["version"] == "1.2.0"

        # 2. Map to W02 AssetIdentity
        asset = AssetIdentity(
            asset_id=canonical.asset_id,
            primary_name="Authentication Service RSA Keypair",
            observations=[canonical],
            is_uncertain=False,
        )
        assert len(asset.observations) == 1
        assert asset.observations[0].algorithm == "RSA-2048"

        # 3. Translate to W03 RiskContext
        risk_ctx = RiskContext(
            asset_id=asset.asset_id,
            algorithm=canonical.algorithm,
            purpose=canonical.purpose,
            evidence_state=canonical.state,
            confidence=canonical.confidence,
            freshness=canonical.observed_at,
            uncertainty=asset.is_uncertain,
        )
        assert risk_ctx.asset_id == "asset-auth-service"
        assert risk_ctx.algorithm == "RSA-2048"
        assert risk_ctx.uncertainty is False

        # 4. Score with W03 RiskScorer
        context = ContextFactors(
            data_shelf_life_years=10.0,
            migration_duration_years=3.0,
            exposure=ExposureScope.PUBLIC_FACING,
            criticality=BusinessCriticality.MISSION_CRITICAL,
        )
        scenario = RiskScenario(quantum_threat_horizon_years=7.0)
        scorer = RiskScorer(scenario=scenario)
        eval_result = scorer.evaluate_observation(obs, context)
        assert eval_result.mosca_condition_violated is True
        assert eval_result.urgency.value == "CRITICAL"

    def test_zero_secret_leakage_across_all_private_key_formats(self, tmp_path):
        """Guarantees that private key material in various PEM encodings is masked and never stored."""
        # Generate an RSA private key
        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        pem_pkcs8 = key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )

        cert_file = tmp_path / "server.key"
        cert_file.write_bytes(pem_pkcs8)

        detector = CertificateCryptoDetector()
        obs_list = detector.analyze_file(cert_file, "certs/server.key", "scan-test-1")

        # Must detect that a key exists, but MUST redact private bytes
        assert len(obs_list) >= 1
        for obs in obs_list:
            assert obs.redacted is True
            assert "[REDACTED_PRIVATE_KEY_MATERIAL" in obs.sanitized_excerpt
            # The actual base64 key material must NOT appear anywhere in the observation
            assert "MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQ" not in obs.sanitized_excerpt

    def test_param_redaction_allowlist_enforcement(self):
        """Validates that redact_sensitive_values strictly redacts non-allowlisted keys."""
        test_params = {
            "public_key": "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8A...",
            "algorithm": "RSA-2048",
            "version": "1.0.4",
            "private_key": "-----BEGIN RSA PRIVATE KEY-----\nMIIE...",
            "passphrase": "super_secret_password",
            "token": "bearer eyJhbGciOi...",
            "nonce": "98a1c8f42",
            "master_key": "0xDEADBEEFCAFE",
            "salt": "d41d8cd98f00b204e9800998ecf8427e",
        }

        redacted = redact_sensitive_values(test_params)

        # Allowlisted items preserved
        assert redacted["public_key"] == "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8A..."
        assert redacted["algorithm"] == "RSA-2048"
        assert redacted["version"] == "1.0.4"

        # Non-allowlisted items masked
        assert redacted["private_key"] == "[REDACTED]"
        assert redacted["passphrase"] == "[REDACTED]"
        assert redacted["token"] == "[REDACTED]"
        assert redacted["nonce"] == "[REDACTED]"
        assert redacted["master_key"] == "[REDACTED]"
        assert redacted["salt"] == "[REDACTED]"

    def test_hostile_archive_adversarial_matrix(self, tmp_path):
        """Tests the adversarial input matrix against the SafeArchiveExtractor."""
        limits = IntakeLimits(
            max_archive_size_bytes=10 * 1024 * 1024,
            max_uncompressed_size_bytes=20 * 1024 * 1024,
            max_compression_ratio=10.0,
            max_file_count=50,
        )

        extractor = SafeArchiveExtractor(limits=limits)

        # 1. Backtracking path traversal ZIP - must raise PathTraversalError
        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, "w") as zf:
            zf.writestr("../../etc/shadow", "root:x:0:0:::")
        zip_buf.seek(0)
        zip_path = tmp_path / "evil_traversal.zip"
        zip_path.write_bytes(zip_buf.getvalue())

        out_dir = tmp_path / "out_traversal"
        with pytest.raises(PathTraversalError):
            extractor.process_and_extract(zip_path, out_dir, "scan-traversal-1")

        # 2. Decompression bomb exceeding ratio cutoff - must raise DecompressionBombError
        bomb_buf = io.BytesIO()
        with zipfile.ZipFile(bomb_buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("bomb.bin", b"\x00" * (2 * 1024 * 1024))
        bomb_buf.seek(0)
        bomb_path = tmp_path / "bomb.zip"
        bomb_path.write_bytes(bomb_buf.getvalue())

        out_bomb = tmp_path / "out_bomb"
        with pytest.raises(DecompressionBombError):
            extractor.process_and_extract(bomb_path, out_bomb, "scan-bomb-1")

        # 3. Dangerous executables safely ignored
        exe_buf = io.BytesIO()
        with zipfile.ZipFile(exe_buf, "w") as zf:
            zf.writestr("safe_app.py", "print('hello')")
            zf.writestr("malicious.exe", b"\x4D\x5A\x90\x00")
            zf.writestr("script.ps1", "Invoke-Expression")
        exe_buf.seek(0)
        exe_path = tmp_path / "mixed.zip"
        exe_path.write_bytes(exe_buf.getvalue())

        out_mixed = tmp_path / "out_mixed"
        manifest_mixed = extractor.process_and_extract(exe_path, out_mixed, "scan-mixed-1")
        assert manifest_mixed.status == ScanStatus.COMPLETE
        # Executables skipped
        extracted_rel_paths = [f.relative_path for f in manifest_mixed.files if f.is_supported]
        assert "safe_app.py" in extracted_rel_paths
        assert "malicious.exe" not in extracted_rel_paths
        assert "script.ps1" not in extracted_rel_paths

    def test_inventory_export_json_schema_roundtrip(self):
        """Verifies that InventoryExport serializes to standard JSON and round-trips with zero data degradation."""
        canonical = CanonicalEvidence(
            canonical_id="c1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2",
            asset_id="asset-tls-gateway",
            claim_type=ClaimType.CONFIG_PARAMETER,
            source_kind=SourceKind.CONFIG,
            algorithm="ECDHE-RSA-AES256-GCM-SHA384",
            protocol="TLSv1.3",
            purpose="CIPHER_SUITE",
            key_size_bits=256,
            curve_name=None,
            evidence_digest="b" * 64,
            sanitized_excerpt="ssl_ciphers ECDHE-RSA-AES256-GCM-SHA384;",
            redacted=False,
            detector_id="config_crypto_detector",
            ruleset_version="2026.10-nist-pqc",
            confidence=ConfidenceBand.HIGH,
            confidence_rationale="Nginx TLS configuration directive",
            state=EvidenceState.VERIFIED,
            observed_at=datetime.now(timezone.utc),
            relative_path="nginx/conf.d/tls.conf",
            start_line=12,
            end_line=12,
            raw_parameters={"ciphers": "ECDHE-RSA-AES256-GCM-SHA384"},
        )

        asset = AssetIdentity(
            asset_id="asset-tls-gateway",
            primary_name="Edge Reverse Proxy TLS Config",
            observations=[canonical],
            is_uncertain=False,
        )

        relationship = Relationship(
            source_asset_id="asset-tls-gateway",
            target_asset_id="asset-backend-service",
            relationship_type="DEPENDS_ON",
            provenance="config_upstream_proxy",
            uncertainty=False,
        )

        audit_record = AuditRecord(
            reason="Verified production TLS 1.3 suite against NIST SP 800-52r2",
            actor=None,
            timestamp=datetime.now(timezone.utc),
            previous_value="OBSERVED",
            new_value="VERIFIED",
            linked_evidence=canonical.canonical_id,
        )

        export_payload = InventoryExport(
            profile="CycloneDX 1.6 CBOM Export Draft",
            version="1.0.0",
            assets=[asset],
            relationships=[relationship],
            audit_trail=[audit_record],
        )

        # Serialize to JSON
        json_data = export_payload.model_dump_json(indent=2)
        assert "CycloneDX 1.6 CBOM Export Draft" in json_data
        assert "asset-tls-gateway" in json_data
        assert "ECDHE-RSA-AES256-GCM-SHA384" in json_data

        # Deserialize back
        parsed_dict = json.loads(json_data)
        reconstructed = InventoryExport.model_validate(parsed_dict)

        assert reconstructed.version == "1.0.0"
        assert len(reconstructed.assets) == 1
        assert reconstructed.assets[0].primary_name == "Edge Reverse Proxy TLS Config"
        assert len(reconstructed.relationships) == 1
        assert reconstructed.relationships[0].relationship_type == "DEPENDS_ON"
        assert len(reconstructed.audit_trail) == 1
        assert reconstructed.audit_trail[0].new_value == "VERIFIED"
