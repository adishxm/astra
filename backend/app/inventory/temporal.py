"""ASTRA - Temporal Identity & Cryptographic Lineage Engine (Worker 02 - PROD-01).

Implements the Cryptographic Time Machine:
- Snapshot capture of enterprise cryptographic postures across versions/commits
- Cryptographic DNA hashing for instant drift detection
- Identification of added, removed, modified, and critically downgraded cryptographic assets
- Lineage causality tracking across continuous software evolution
"""

import hashlib
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field

from app.inventory.models import AssetIdentity, CanonicalEvidence
from app.discovery.models import ClaimType, ConfidenceBand, EvidenceState, SourceKind


class CryptographicDrift(BaseModel):
    """Cryptographic change delta between two snapshots in time."""

    from_snapshot_id: str
    to_snapshot_id: str
    from_version_tag: str
    to_version_tag: str

    added_assets: List[Dict[str, Any]] = Field(default_factory=list, description="Newly introduced assets")
    removed_assets: List[Dict[str, Any]] = Field(default_factory=list, description="Retired assets")
    modified_assets: List[Dict[str, Any]] = Field(default_factory=list, description="Assets with changed parameters")
    downgraded_assets: List[Dict[str, Any]] = Field(default_factory=list, description="Security regressions / algorithm downgrades")

    dna_changed: bool = Field(..., description="Whether cryptographic DNA hash shifted")
    drift_summary: str = Field(..., description="Human-readable synthesis of temporal drift")

    def __getitem__(self, item: str) -> Any:
        if hasattr(self, item):
            return getattr(self, item)
        raise KeyError(item)


class InventorySnapshot(BaseModel):
    """Point-in-time cryptographic inventory snapshot."""

    snapshot_id: str
    scan_id: str
    version_tag: str = Field(..., description="Git commit, semantic version, or release tag")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    assets: List[AssetIdentity] = Field(default_factory=list)
    cryptographic_dna_hash: str = Field(..., description="Deterministic SHA-256 fingerprint of inventory")

    @property
    def dna_hash(self) -> str:
        return self.cryptographic_dna_hash

    @property
    def asset_count(self) -> int:
        return len(self.assets)

    def __getitem__(self, item: str) -> Any:
        if item == "dna_hash":
            return self.dna_hash
        if item == "asset_count":
            return self.asset_count
        if hasattr(self, item):
            return getattr(self, item)
        raise KeyError(item)


# Known algorithm strength ranking for downgrade detection (lower tier = weaker/vulnerable)
ALGORITHM_STRENGTH_TIERS: Dict[str, int] = {
    # Broken / Legacy (Tier 1)
    "DES": 1,
    "3DES": 1,
    "RC4": 1,
    "MD5": 1,
    "SHA-1": 1,
    # Weak Classical (Tier 2)
    "RSA-1024": 2,
    # Standard Classical (Tier 3)
    "RSA": 3,
    "RSA-2048": 3,
    "RSA-3072": 3,
    "RSA-4096": 3,
    "ECDSA": 3,
    "secp256r1": 3,
    "X25519": 3,
    "Ed25519": 3,
    "AES": 3,
    "AES-128": 3,
    "AES-256": 4,
    "SHA-256": 4,
    "SHA-384": 4,
    "SHA-512": 4,
    # Quantum-Resistant / PQC (Tier 5)
    "ML-KEM": 5,
    "ML-KEM-512": 5,
    "ML-KEM-768": 5,
    "ML-KEM-1024": 5,
    "ML-DSA": 5,
    "ML-DSA-44": 5,
    "ML-DSA-65": 5,
    "ML-DSA-87": 5,
    "SLH-DSA": 5,
}


def _normalize_asset(item: Any) -> AssetIdentity:
    """Helper to normalize an asset input into an AssetIdentity object."""
    if isinstance(item, AssetIdentity):
        return item
    if isinstance(item, dict):
        asset_id = str(item.get("id") or item.get("asset_id") or "ast-unknown")
        primary_name = str(item.get("name") or item.get("primary_name") or asset_id)
        algo = item.get("algorithm")
        key_size = item.get("key_size") or item.get("key_size_bits")
        purpose = item.get("purpose")

        obs = CanonicalEvidence(
            canonical_id=f"can-{asset_id}",
            asset_id=asset_id,
            claim_type=ClaimType.ALGORITHM_USE,
            source_kind=SourceKind.SOURCE_CODE,
            algorithm=str(algo) if algo else None,
            key_size_bits=int(key_size) if key_size is not None else None,
            purpose=str(purpose) if purpose else None,
            evidence_digest=f"digest-{asset_id}",
            sanitized_excerpt=f"algorithm: {algo}",
            redacted=False,
            detector_id="temporal-normalizer",
            ruleset_version="1.0",
            confidence=ConfidenceBand.HIGH,
            confidence_rationale="Normalized from input data",
            state=EvidenceState.VERIFIED,
            observed_at=datetime.now(timezone.utc),
            relative_path="src/crypto",
        )
        return AssetIdentity(
            asset_id=asset_id,
            primary_name=primary_name,
            observations=[obs],
        )
    raise ValueError(f"Unsupported asset type: {type(item)}")


class TemporalLineageEngine:
    """Manages snapshot history, DNA hashing, and cryptographic regression detection."""

    @staticmethod
    def compute_dna_hash(assets: List[AssetIdentity]) -> str:
        """Compute deterministic SHA-256 digest of entire cryptographic asset posture."""
        normalized_tokens = []
        for asset in sorted(assets, key=lambda a: a.asset_id):
            algos = sorted(
                set(
                    obs.algorithm.upper()
                    for obs in asset.observations
                    if obs.algorithm
                )
            )
            key_sizes = sorted(
                set(
                    str(obs.key_size_bits)
                    for obs in asset.observations
                    if obs.key_size_bits is not None
                )
            )
            token = f"{asset.asset_id}:{','.join(algos)}:{','.join(key_sizes)}"
            normalized_tokens.append(token)

        content = "|".join(normalized_tokens)
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def create_snapshot(
        self,
        snapshot_id: str,
        assets: Optional[List[Any]] = None,
        scan_id: Optional[str] = None,
        version_tag: str = "v1.0.0",
        **kwargs: Any,
    ) -> InventorySnapshot:
        """Build an immutable point-in-time inventory snapshot."""
        if assets is None and "assets" in kwargs:
            assets = kwargs.pop("assets")

        # Flexible argument handling for positional orders
        if isinstance(assets, str):
            actual_scan = assets
            actual_ver = scan_id if isinstance(scan_id, str) else version_tag
            raw_assets = kwargs.get("assets", [])
            actual_scan_id = actual_scan
            actual_version_tag = actual_ver
        else:
            raw_assets = assets or []
            actual_scan_id = scan_id or snapshot_id
            actual_version_tag = version_tag

        normalized_assets = [_normalize_asset(a) for a in raw_assets]
        dna_hash = self.compute_dna_hash(normalized_assets)

        return InventorySnapshot(
            snapshot_id=snapshot_id,
            scan_id=actual_scan_id,
            version_tag=actual_version_tag,
            assets=normalized_assets,
            cryptographic_dna_hash=dna_hash,
        )

    def detect_drift(
        self,
        prior: InventorySnapshot,
        current: InventorySnapshot,
    ) -> CryptographicDrift:
        """Detect cryptographic delta, mutations, and regressions between two snapshots."""
        prior_map = {a.asset_id: a for a in prior.assets}
        current_map = {a.asset_id: a for a in current.assets}

        prior_ids = set(prior_map.keys())
        current_ids = set(current_map.keys())

        added_ids = sorted(list(current_ids - prior_ids))
        removed_ids = sorted(list(prior_ids - current_ids))
        common_ids = sorted(list(prior_ids.intersection(current_ids)))

        added: List[Dict[str, Any]] = [
            {
                "id": aid,
                "asset_id": aid,
                "primary_name": current_map[aid].primary_name,
                "algorithms": sorted(set(obs.algorithm for obs in current_map[aid].observations if obs.algorithm)),
            }
            for aid in added_ids
        ]

        removed: List[Dict[str, Any]] = [
            {
                "id": aid,
                "asset_id": aid,
                "primary_name": prior_map[aid].primary_name,
                "algorithms": sorted(set(obs.algorithm for obs in prior_map[aid].observations if obs.algorithm)),
            }
            for aid in removed_ids
        ]

        modified: List[Dict[str, Any]] = []
        downgraded: List[Dict[str, Any]] = []

        for aid in common_ids:
            p_asset = prior_map[aid]
            c_asset = current_map[aid]

            p_algos = sorted(set(obs.algorithm for obs in p_asset.observations if obs.algorithm))
            c_algos = sorted(set(obs.algorithm for obs in c_asset.observations if obs.algorithm))

            p_keys = sorted(set(obs.key_size_bits for obs in p_asset.observations if obs.key_size_bits is not None))
            c_keys = sorted(set(obs.key_size_bits for obs in c_asset.observations if obs.key_size_bits is not None))

            changes: Dict[str, Any] = {}
            if p_algos != c_algos:
                changes["algorithm"] = {"from": p_algos, "to": c_algos}
            if p_keys != c_keys:
                changes["key_size"] = {
                    "from": p_keys[0] if p_keys else None,
                    "to": c_keys[0] if c_keys else None,
                }

            if changes:
                modified.append({
                    "asset_id": aid,
                    "id": aid,
                    "prior_algorithms": p_algos,
                    "current_algorithms": c_algos,
                    "changes": changes,
                })

            # Check for cryptographic downgrade
            p_tier = max([ALGORITHM_STRENGTH_TIERS.get(alg, 3) for alg in p_algos], default=3)
            c_tier = max([ALGORITHM_STRENGTH_TIERS.get(alg, 3) for alg in c_algos], default=3)

            if c_tier < p_tier:
                downgraded.append({
                    "asset_id": aid,
                    "id": aid,
                    "prior_tier": p_tier,
                    "current_tier": c_tier,
                    "previous_tier": p_tier,
                    "previous_algorithm": p_algos[0] if p_algos else "UNKNOWN",
                    "current_algorithm": c_algos[0] if c_algos else "UNKNOWN",
                    "prior_algorithms": p_algos,
                    "current_algorithms": c_algos,
                    "regression_severity": "CRITICAL" if c_tier <= 1 else "HIGH",
                })

        dna_changed = prior.cryptographic_dna_hash != current.cryptographic_dna_hash

        summary_parts = []
        if added:
            summary_parts.append(f"{len(added)} asset(s) added")
        if removed:
            summary_parts.append(f"{len(removed)} asset(s) retired")
        if modified:
            summary_parts.append(f"{len(modified)} asset(s) modified")
        if downgraded:
            summary_parts.append(f"WARNING: {len(downgraded)} asset(s) downgraded to weaker crypto")
        if not summary_parts:
            summary_parts.append("Zero cryptographic drift detected; posture identical")

        return CryptographicDrift(
            from_snapshot_id=prior.snapshot_id,
            to_snapshot_id=current.snapshot_id,
            from_version_tag=prior.version_tag,
            to_version_tag=current.version_tag,
            added_assets=added,
            removed_assets=removed,
            modified_assets=modified,
            downgraded_assets=downgraded,
            dna_changed=dna_changed,
            drift_summary="; ".join(summary_parts),
        )
