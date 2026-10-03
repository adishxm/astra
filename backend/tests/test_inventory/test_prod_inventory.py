"""
Production test suite for Worker 02:
- PROD-01: Temporal Cryptographic Lineage & DNA Drift Tracking
- PROD-02: CycloneDX 1.6 Schema Validation & Multi-Generator Reconciliation
"""

import pytest
from app.inventory.temporal import TemporalLineageEngine
from app.inventory.cbom_reconciliation import CBOMReconciliationEngine


def test_temporal_dna_hash_and_drift_detection():
    """Verify deterministic DNA hash computation and accurate drift detection."""
    engine = TemporalLineageEngine()

    v1_assets = [
        {"id": "ast-001", "algorithm": "RSA", "key_size": 2048, "purpose": "encryption"},
        {"id": "ast-002", "algorithm": "AES", "key_size": 256, "purpose": "storage"},
    ]
    snap_v1 = engine.create_snapshot("scan-101", v1_assets, version_tag="v1.0.0")

    assert snap_v1.dna_hash is not None
    assert len(snap_v1.dna_hash) == 64
    assert snap_v1.asset_count == 2

    # In v2: ast-002 key_size changes to 128 (modified), ast-003 is added
    v2_assets = [
        {"id": "ast-001", "algorithm": "RSA", "key_size": 2048, "purpose": "encryption"},
        {"id": "ast-002", "algorithm": "AES", "key_size": 128, "purpose": "storage"},
        {"id": "ast-003", "algorithm": "ML-KEM-768", "key_size": 768, "purpose": "key_exchange"},
    ]
    snap_v2 = engine.create_snapshot("scan-102", v2_assets, version_tag="v2.0.0")

    assert snap_v2.dna_hash != snap_v1.dna_hash

    drift = engine.detect_drift(snap_v1, snap_v2)
    assert drift.dna_changed is True
    assert len(drift.added_assets) == 1
    assert drift.added_assets[0]["id"] == "ast-003"
    assert len(drift.removed_assets) == 0
    assert len(drift.modified_assets) == 1
    assert drift.modified_assets[0]["asset_id"] == "ast-002"
    assert "key_size" in drift.modified_assets[0]["changes"]
    assert drift.modified_assets[0]["changes"]["key_size"] == {"from": 256, "to": 128}


def test_temporal_downgrade_regression_detection():
    """Verify detection of cryptographic strength downgrade regressions (e.g., AES-256 -> DES)."""
    engine = TemporalLineageEngine()

    v1_assets = [
        {"id": "ast-core-01", "algorithm": "AES-256", "key_size": 256},
        {"id": "ast-core-02", "algorithm": "ML-DSA-65", "key_size": 65},
    ]
    snap_v1 = engine.create_snapshot("scan-201", v1_assets)

    # Downgrade ast-core-01 to DES (Tier 4 -> Tier 1)
    v2_assets = [
        {"id": "ast-core-01", "algorithm": "DES", "key_size": 56},
        {"id": "ast-core-02", "algorithm": "ML-DSA-65", "key_size": 65},
    ]
    snap_v2 = engine.create_snapshot("scan-202", v2_assets)

    drift = engine.detect_drift(snap_v1, snap_v2)
    assert len(drift.downgraded_assets) == 1
    downgrade = drift.downgraded_assets[0]
    assert downgrade["asset_id"] == "ast-core-01"
    assert downgrade["previous_algorithm"] == "AES-256"
    assert downgrade["current_algorithm"] == "DES"
    assert downgrade["previous_tier"] > downgrade["current_tier"]


def test_cbom_validator_cyclonedx_16():
    """Verify CycloneDX 1.6 CBOM schema validation rules."""
    engine = CBOMReconciliationEngine()

    valid_cbom = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.6",
        "serialNumber": "urn:uuid:3e671687-395b-41f5-a30f-a58921a69b79",
        "version": 1,
        "components": [
            {
                "type": "cryptographic-asset",
                "name": "RSA-Signing-Key",
                "cryptoProperties": {
                    "assetType": "algorithm",
                    "algorithmProperties": {
                        "primitive": "unknown",
                        "parameterSetIdentifier": "2048",
                        "executionEnvironment": "software-plain-ram"
                    }
                }
            }
        ]
    }
    val_result = engine.validate_cyclonedx_16(valid_cbom)
    assert val_result["valid"] is True
    assert val_result["component_count"] == 1
    assert val_result["crypto_asset_count"] == 1
    assert len(val_result["errors"]) == 0

    # Invalid CBOM: wrong specVersion and missing cryptoProperties on cryptographic-asset
    invalid_cbom = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "components": [
            {
                "type": "cryptographic-asset",
                "name": "Broken-Asset"
            }
        ]
    }
    invalid_result = engine.validate_cyclonedx_16(invalid_cbom)
    assert invalid_result["valid"] is False
    assert any("specVersion" in err for err in invalid_result["errors"])
    assert any("cryptoProperties" in err for err in invalid_result["errors"])


def test_cbom_multi_generator_reconciliation():
    """Verify multi-generator reconciliation and Discrepancy Index computation."""
    engine = CBOMReconciliationEngine()

    # Generator 1: ASTRA Native Scanner
    astra_cbom = {
        "generator": "astra",
        "components": [
            {
                "type": "cryptographic-asset",
                "name": "tls-cert-rsa",
                "cryptoProperties": {"algorithmProperties": {"name": "RSA", "parameterSetIdentifier": "2048"}}
            },
            {
                "type": "cryptographic-asset",
                "name": "db-token-aes",
                "cryptoProperties": {"algorithmProperties": {"name": "AES", "parameterSetIdentifier": "256"}}
            }
        ]
    }

    # Generator 2: IBM CBOM / External Scanner (detected tls-cert-rsa and legacy sha1)
    ibm_cbom = {
        "generator": "ibm-cbom",
        "components": [
            {
                "type": "cryptographic-asset",
                "name": "tls-cert-rsa",
                "cryptoProperties": {"algorithmProperties": {"name": "RSA", "parameterSetIdentifier": "2048"}}
            },
            {
                "type": "cryptographic-asset",
                "name": "legacy-hasher",
                "cryptoProperties": {"algorithmProperties": {"name": "SHA-1"}}
            }
        ]
    }

    reconciliation = engine.reconcile_generators([astra_cbom, ibm_cbom])

    assert reconciliation["total_generators"] == 2
    assert reconciliation["unique_assets"] == 3
    assert len(reconciliation["consensus_assets"]) == 1
    assert reconciliation["consensus_assets"][0]["name"] == "tls-cert-rsa"
    assert len(reconciliation["discrepancies"]) == 2

    # Discrepancy Index should be > 0.0 since not all generators agree on all assets
    assert 0.0 < reconciliation["discrepancy_index"] <= 1.0

    # Ensure minority scanner claims are preserved in unified CBOM
    unified = reconciliation["unified_cbom"]
    assert unified["bomFormat"] == "CycloneDX"
    assert unified["specVersion"] == "1.6"
    assert len(unified["components"]) == 3
