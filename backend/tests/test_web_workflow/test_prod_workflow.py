"""
Production test suite for Worker 04:
- PROD-01: Offline Operations, Tamper-Evident Audit Chaining & Production Hardening
"""

import hashlib
import json
import pytest
from app.web_workflow.hardening import (
    AirGappedBundleManager,
    TamperEvidentAuditChainer,
    ProductionHealthEvaluator,
    ChainedAuditEvent,
)


def test_tamper_evident_audit_chain_integrity():
    """Verify cryptographic audit log chaining and tampering detection."""
    chain = []

    # 1. Append valid events
    ev1 = TamperEvidentAuditChainer.append_event(
        chain=chain,
        action="SCAN_TRIGGERED",
        actor="admin@astra.internal",
        details={"scan_type": "FULL_AIRGAPPED"},
    )
    ev2 = TamperEvidentAuditChainer.append_event(
        chain=chain,
        action="ASSET_REVIEWED",
        actor="security_lead@astra.internal",
        asset_id="ast-001",
        details={"decision": "APPROVED_PQC_MIGRATION"},
    )
    ev3 = TamperEvidentAuditChainer.append_event(
        chain=chain,
        action="EXPORT_GENERATED",
        actor="compliance@astra.internal",
        details={"export_format": "CycloneDX_1.6"},
    )

    assert len(chain) == 3
    assert ev1.prev_hash == "0" * 64
    assert ev2.prev_hash == ev1.event_hash
    assert ev3.prev_hash == ev2.event_hash

    # Verify untampered chain
    verify_res = TamperEvidentAuditChainer.verify_chain(chain)
    assert verify_res["valid"] is True
    assert verify_res["event_count"] == 3

    # 2. Tamper test: modify details of ev2
    chain[1].details["decision"] = "FORGED_DECISION"
    tampered_res = TamperEvidentAuditChainer.verify_chain(chain)
    assert tampered_res["valid"] is False
    assert tampered_res["tamper_detected_at_sequence"] == 2


def test_air_gapped_offline_bundle_verification():
    """Verify offline signed update bundle validation and corruption rejection."""
    payload = b'{"nist_pqc_advisories": ["FIPS-203-ML-KEM", "FIPS-204-ML-DSA"]}'
    payload_hash = hashlib.sha256(payload).hexdigest()

    manifest = {
        "bundle_id": "bundle-2026-10-01",
        "version": "1.4.0",
        "payload_sha256": payload_hash,
        "rules_count": 42,
        "pqc_advisories_count": 8,
    }

    # Valid bundle with authorized key
    result = AirGappedBundleManager.verify_bundle(
        manifest_data=manifest,
        raw_payload_bytes=payload,
        signer_key_id="ASTRA-ROOT-KEY-2026",
    )
    assert result["valid"] is True
    assert result["status"] == "OFFLINE_BUNDLE_VERIFIED"

    # Reject unauthorized signer key
    bad_signer = AirGappedBundleManager.verify_bundle(
        manifest_data=manifest,
        raw_payload_bytes=payload,
        signer_key_id="ROGUE-KEY-9999",
    )
    assert bad_signer["valid"] is False
    assert "Untrusted signer" in bad_signer["reason"]

    # Reject corrupted payload
    corrupted_payload = payload + b"_tampered"
    bad_hash = AirGappedBundleManager.verify_bundle(
        manifest_data=manifest,
        raw_payload_bytes=corrupted_payload,
        signer_key_id="ASTRA-ROOT-KEY-2026",
    )
    assert bad_hash["valid"] is False
    assert "Integrity violation" in bad_hash["reason"]


def test_production_readiness_health_evaluation():
    """Verify production health evaluation report checks air-gapped isolation and quotas."""
    report = ProductionHealthEvaluator.evaluate_readiness(
        air_gapped_mode=True,
        sandbox_isolation_active=True,
        ruleset_cached_locally=True,
    )

    assert report["is_production_ready"] is True
    assert report["profile"] == "AIR_GAPPED_ENTERPRISE_PROD"
    assert report["checks"]["sandbox_filesystem_isolation"]["status"] == "PASS"
    assert report["checks"]["air_gapped_telemetry_isolation"]["status"] == "PASS"
    assert report["checks"]["local_cryptographic_ruleset"]["status"] == "PASS"
