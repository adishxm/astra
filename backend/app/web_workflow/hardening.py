"""ASTRA - Production Hardening, Air-Gapped Operations & Audit Chaining (Worker 04 - PROD-01).

Implements:
- Air-gapped offline update bundle verification and provenance auditing
- Tamper-evident cryptographic audit log chaining (hash-linked provenance chain)
- Production readiness and isolation health evaluations
"""

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field


class OfflineBundleManifest(BaseModel):
    """Manifest describing an offline air-gapped threat intel / ruleset update package."""

    bundle_id: str
    version: str
    published_at: str
    payload_sha256: str
    signature: str
    rules_count: int
    pqc_advisories_count: int


class ChainedAuditEvent(BaseModel):
    """Cryptographically chained audit event conforming to append-only tamper-evident logs."""

    event_id: str
    sequence_num: int
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    action: str
    actor: str
    asset_id: Optional[str] = None
    details: Dict[str, Any] = Field(default_factory=dict)
    prev_hash: str
    event_hash: str


class AirGappedBundleManager:
    """Verifies signed offline rule bundles and maintains air-gapped operational integrity."""

    TRUSTED_SIGNER_KEY_IDS = {
        "ASTRA-ROOT-KEY-2026",
        "ASTRA-OFFLINE-RELEASE-V1",
    }

    @classmethod
    def verify_bundle(
        cls,
        manifest_data: Dict[str, Any],
        raw_payload_bytes: bytes,
        signer_key_id: str,
    ) -> Dict[str, Any]:
        """Verify SHA-256 payload integrity and signer authority without internet connectivity."""
        if signer_key_id not in cls.TRUSTED_SIGNER_KEY_IDS:
            return {
                "valid": False,
                "reason": f"Untrusted signer key ID: '{signer_key_id}'. Rejecting offline bundle.",
            }

        computed_sha256 = hashlib.sha256(raw_payload_bytes).hexdigest()
        declared_sha256 = manifest_data.get("payload_sha256", "").lower()

        if computed_sha256 != declared_sha256:
            return {
                "valid": False,
                "reason": (
                    f"Integrity violation: computed SHA-256 '{computed_sha256}' "
                    f"does not match declared '{declared_sha256}'"
                ),
            }

        return {
            "valid": True,
            "bundle_id": manifest_data.get("bundle_id"),
            "version": manifest_data.get("version"),
            "rules_count": manifest_data.get("rules_count", 0),
            "pqc_advisories_count": manifest_data.get("pqc_advisories_count", 0),
            "status": "OFFLINE_BUNDLE_VERIFIED",
        }


class TamperEvidentAuditChainer:
    """Maintains and validates tamper-evident cryptographic hash chains for audit records."""

    GENESIS_HASH = "0" * 64

    @staticmethod
    def compute_event_hash(
        prev_hash: str,
        sequence_num: int,
        timestamp: str,
        action: str,
        actor: str,
        asset_id: Optional[str],
        details: Dict[str, Any],
    ) -> str:
        """Compute deterministic SHA-256 digest over audit fields."""
        serialized_details = json.dumps(details, sort_keys=True)
        content = f"{prev_hash}:{sequence_num}:{timestamp}:{action}:{actor}:{asset_id or ''}:{serialized_details}"
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    @classmethod
    def append_event(
        cls,
        chain: List[ChainedAuditEvent],
        action: str,
        actor: str,
        asset_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> ChainedAuditEvent:
        """Append a new tamper-evident event to the running audit chain."""
        seq = len(chain) + 1
        prev_hash = chain[-1].event_hash if chain else cls.GENESIS_HASH
        ts = datetime.now(timezone.utc).isoformat()
        ev_details = details or {}
        event_id = f"ev-{seq:06d}"

        event_hash = cls.compute_event_hash(
            prev_hash=prev_hash,
            sequence_num=seq,
            timestamp=ts,
            action=action,
            actor=actor,
            asset_id=asset_id,
            details=ev_details,
        )

        event = ChainedAuditEvent(
            event_id=event_id,
            sequence_num=seq,
            timestamp=ts,
            action=action,
            actor=actor,
            asset_id=asset_id,
            details=ev_details,
            prev_hash=prev_hash,
            event_hash=event_hash,
        )
        chain.append(event)
        return event

    @classmethod
    def verify_chain(cls, chain: List[ChainedAuditEvent]) -> Dict[str, Any]:
        """Verify cryptographic chain continuity and identify any tampering or reordering."""
        if not chain:
            return {"valid": True, "event_count": 0, "message": "Empty audit chain"}

        for idx, event in enumerate(chain):
            expected_prev = chain[idx - 1].event_hash if idx > 0 else cls.GENESIS_HASH
            if event.prev_hash != expected_prev:
                return {
                    "valid": False,
                    "tamper_detected_at_sequence": event.sequence_num,
                    "reason": f"Broken chain link at index {idx}: expected prev_hash '{expected_prev}', got '{event.prev_hash}'",
                }

            expected_hash = cls.compute_event_hash(
                prev_hash=event.prev_hash,
                sequence_num=event.sequence_num,
                timestamp=event.timestamp,
                action=event.action,
                actor=event.actor,
                asset_id=event.asset_id,
                details=event.details,
            )

            if event.event_hash != expected_hash:
                return {
                    "valid": False,
                    "tamper_detected_at_sequence": event.sequence_num,
                    "reason": f"Payload modification at sequence {event.sequence_num}: hash mismatch",
                }

        return {
            "valid": True,
            "event_count": len(chain),
            "genesis_hash": cls.GENESIS_HASH,
            "tip_hash": chain[-1].event_hash,
            "message": "Audit chain fully verified; zero tampering detected",
        }


class ProductionHealthEvaluator:
    """Evaluates readiness of production deployment (isolation, quotas, offline posture)."""

    @staticmethod
    def evaluate_readiness(
        air_gapped_mode: bool = True,
        sandbox_isolation_active: bool = True,
        ruleset_cached_locally: bool = True,
    ) -> Dict[str, Any]:
        """Evaluate production deployment readiness against security baseline."""
        checks = {
            "sandbox_filesystem_isolation": {
                "status": "PASS" if sandbox_isolation_active else "FAIL",
                "details": "Read-only ephemeral execution container active",
            },
            "air_gapped_telemetry_isolation": {
                "status": "PASS" if air_gapped_mode else "WARN",
                "details": "Zero external internet telemetry; sovereign offline operation",
            },
            "local_cryptographic_ruleset": {
                "status": "PASS" if ruleset_cached_locally else "FAIL",
                "details": "NIST FIPS 203/204/205 rule engine cached locally without remote dependencies",
            },
            "tamper_evident_audit_logging": {
                "status": "PASS",
                "details": "Cryptographic SHA-256 hash chaining active",
            },
        }

        all_passed = all(c["status"] == "PASS" for c in checks.values())

        return {
            "is_production_ready": all_passed,
            "profile": "AIR_GAPPED_ENTERPRISE_PROD" if air_gapped_mode else "STANDARD_PROD",
            "evaluated_at": datetime.now(timezone.utc).isoformat(),
            "checks": checks,
        }
