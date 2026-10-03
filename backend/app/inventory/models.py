"""ASTRA - Inventory Domain Models (Worker 02)."""

from typing import List, Optional, Set, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import hashlib

from app.discovery.models import Observation, EvidenceState, ConfidenceBand, ClaimType, SourceKind

class CanonicalEvidence(BaseModel):
    """Canonical observation/evidence model."""
    canonical_id: str = Field(..., description="Stable observation/claim ID")
    asset_id: str = Field(..., description="Component identity")
    claim_type: ClaimType
    source_kind: SourceKind
    algorithm: Optional[str] = None
    protocol: Optional[str] = None
    purpose: Optional[str] = None
    key_size_bits: Optional[int] = None
    curve_name: Optional[str] = None
    evidence_digest: str
    sanitized_excerpt: str
    redacted: bool
    detector_id: str
    ruleset_version: str
    confidence: ConfidenceBand
    confidence_rationale: str
    state: EvidenceState
    observed_at: datetime
    relative_path: str
    start_line: Optional[int] = None
    end_line: Optional[int] = None
    raw_parameters: Dict[str, Any] = Field(default_factory=dict)

class AssetIdentity(BaseModel):
    """Identity and deduplication strategy."""
    asset_id: str
    primary_name: str
    observations: List[CanonicalEvidence] = Field(default_factory=list)
    is_uncertain: bool = False

def redact_sensitive_values(raw_params: Dict[str, Any]) -> Dict[str, Any]:
    """Redaction and ingestion adapter."""
    safe_params = {}
    allowlisted = {"public_key", "version", "algorithm"}
    for k, v in raw_params.items():
        if k in allowlisted:
            safe_params[k] = v
        else:
            safe_params[k] = "[REDACTED]"
    return safe_params

def map_observation_to_canonical(obs: Observation) -> CanonicalEvidence:
    """Validator/adapter from Worker 01."""
    # Deterministic ID generation based on stable fields
    id_source = f"{obs.candidate_asset_id}_{obs.claim_type}_{obs.relative_path}_{obs.start_line}"
    canonical_id = hashlib.sha256(id_source.encode()).hexdigest()
    
    return CanonicalEvidence(
        canonical_id=canonical_id,
        asset_id=obs.candidate_asset_id,
        claim_type=obs.claim_type,
        source_kind=obs.source_kind,
        algorithm=obs.algorithm,
        protocol=obs.protocol,
        purpose=obs.purpose,
        key_size_bits=obs.key_size_bits,
        curve_name=obs.curve_name,
        evidence_digest=obs.evidence_digest,
        sanitized_excerpt=obs.sanitized_excerpt,
        redacted=obs.redacted,
        detector_id=obs.detector_id,
        ruleset_version=obs.ruleset_version,
        confidence=obs.confidence,
        confidence_rationale=obs.confidence_rationale,
        state=obs.state,
        observed_at=obs.observed_at,
        relative_path=obs.relative_path,
        start_line=obs.start_line,
        end_line=obs.end_line,
        raw_parameters=redact_sensitive_values(obs.raw_parameters)
    )

class Relationship(BaseModel):
    source_asset_id: str
    target_asset_id: str
    relationship_type: str
    provenance: str
    uncertainty: bool

class RiskContext(BaseModel):
    """Explainable Worker 03 risk inputs."""
    asset_id: str
    algorithm: Optional[str]
    purpose: Optional[str]
    evidence_state: EvidenceState
    confidence: ConfidenceBand
    freshness: datetime
    uncertainty: bool

class AuditRecord(BaseModel):
    """Worker 04 review/audit workflow."""
    reason: str
    actor: Optional[str] = None  # Explicitly None if unauthenticated
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    previous_value: Optional[str]
    new_value: str
    linked_evidence: str

class InventoryExport(BaseModel):
    """Versioned, privacy-safe export."""
    profile: str = "Astra Project Export Draft"
    version: str = "1.0.0"
    assets: List[AssetIdentity]
    relationships: List[Relationship]
    audit_trail: List[AuditRecord]
