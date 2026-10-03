"""Tests for Worker 02 Inventory Models."""

import pytest
from datetime import datetime, timezone
from app.discovery.models import Observation, ClaimType, SourceKind, ConfidenceBand, EvidenceState
from app.inventory.models import map_observation_to_canonical, redact_sensitive_values, AuditRecord

def test_redaction():
    raw = {"public_key": "123", "secret_key": "456", "version": "1.0"}
    safe = redact_sensitive_values(raw)
    assert safe["public_key"] == "123"
    assert safe["secret_key"] == "[REDACTED]"
    assert safe["version"] == "1.0"

def test_map_observation():
    obs = Observation(
        observation_id="obs-1",
        scan_id="scan-1",
        candidate_asset_id="asset-1",
        claim_type=ClaimType.ALGORITHM_USE,
        source_kind=SourceKind.SOURCE_CODE,
        evidence_digest="digest",
        sanitized_excerpt="excerpt",
        detector_id="det-1",
        ruleset_version="1.0",
        confidence=ConfidenceBand.HIGH,
        confidence_rationale="rationale",
        relative_path="path/to/file",
        raw_parameters={"secret": "hidden"}
    )
    canonical = map_observation_to_canonical(obs)
    assert canonical.asset_id == "asset-1"
    assert canonical.raw_parameters["secret"] == "[REDACTED]"
    assert canonical.canonical_id is not None

def test_audit_record():
    record = AuditRecord(
        reason="Manual review",
        previous_value="UNKNOWN",
        new_value="VERIFIED",
        linked_evidence="canonical-id-1"
    )
    assert record.actor is None # unauthenticated state
    assert record.reason == "Manual review"
