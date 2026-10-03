"""ASTRA - Discovery Domain Models (Worker 01 -> Worker 02 Contract).

Defines the normalized Observation schema, evidence anchors, confidence bands,
and claim types conforming to shared interface contracts.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ClaimType(str, Enum):
    """Categorization of cryptographic claim."""

    ALGORITHM_USE = "ALGORITHM_USE"
    DEPENDENCY_REFERENCE = "DEPENDENCY_REFERENCE"
    CONFIG_PARAMETER = "CONFIG_PARAMETER"
    CERTIFICATE_METADATA = "CERTIFICATE_METADATA"
    KEY_SPECIFICATION = "KEY_SPECIFICATION"
    BINARY_SYMBOL = "BINARY_SYMBOL"
    CONTAINER_PACKAGE = "CONTAINER_PACKAGE"
    NETWORK_ENDPOINT = "NETWORK_ENDPOINT"


class SourceKind(str, Enum):
    """Origin kind of the discovery."""

    SOURCE_CODE = "SOURCE_CODE"
    MANIFEST = "MANIFEST"
    CONFIG = "CONFIG"
    CERTIFICATE = "CERTIFICATE"
    BINARY = "BINARY"
    CONTAINER = "CONTAINER"
    NETWORK = "NETWORK"


class ConfidenceBand(str, Enum):
    """Confidence calibration for discovery."""

    CONFIRMED = "CONFIRMED"      # Syntactically verified AST or parsed X.509 structure
    HIGH = "HIGH"                # Specific API call with explicit parameters
    MEDIUM = "MEDIUM"            # Manifest dependency or configuration setting
    LOW = "LOW"                  # Pattern / heuristic match
    HEURISTIC = "HEURISTIC"      # Keyword / token association


class EvidenceState(str, Enum):
    """Truthful state of evidence."""

    OBSERVED = "OBSERVED"        # Directly extracted by collector
    INFERRED = "INFERRED"        # Derived by rules from context
    DECLARED = "DECLARED"        # Stated in manifest or metadata
    VERIFIED = "VERIFIED"        # Verified by cross-analysis
    CONFLICTING = "CONFLICTING"  # Observations disagree
    UNKNOWN = "UNKNOWN"          # Unclear or incomplete data
    UNSUPPORTED = "UNSUPPORTED"  # File or format not supported by rule
    FAILED = "FAILED"            # Parser failed on this entry


class Observation(BaseModel):
    """Standardized cryptographic observation emitted by Worker 01 to Worker 02."""

    observation_id: str = Field(..., description="Unique UUIDv4 observation identifier")
    scan_id: str = Field(..., description="Parent scan run identifier")
    candidate_asset_id: str = Field(..., description="Heuristic identifier for deduplication")

    claim_type: ClaimType = Field(..., description="Type of cryptographic artifact observed")
    source_kind: SourceKind = Field(..., description="Category of file observed")

    # Cryptographic properties
    algorithm: Optional[str] = Field(None, description="Normalized algorithm name (e.g. AES-256-GCM, RSA, SHA-256)")
    protocol: Optional[str] = Field(None, description="Protocol if applicable (e.g. TLSv1.3, SSHv2)")
    purpose: Optional[str] = Field(None, description="Inferred purpose (e.g. ENCRYPTION, HASHING, SIGNATURE, KEY_EXCHANGE)")
    key_size_bits: Optional[int] = Field(None, description="Key length in bits if detectable")
    curve_name: Optional[str] = Field(None, description="Elliptic curve name (e.g. secp256r1, Ed25519)")

    # Evidence Anchor
    relative_path: str = Field(..., description="Repository-relative file path")
    start_line: Optional[int] = Field(None, ge=1, description="Start line of evidence (1-indexed)")
    end_line: Optional[int] = Field(None, ge=1, description="End line of evidence (1-indexed)")
    evidence_digest: str = Field(..., description="SHA-256 hex digest of the sanitized snippet")
    sanitized_excerpt: str = Field(..., description="Safe excerpt showing context (secrets redacted)")
    redacted: bool = Field(default=False, description="Flag indicating if any sensitive token was redacted")

    # Metadata & Provenance
    detector_id: str = Field(..., description="Identifier of the detector that found this")
    ruleset_version: str = Field(..., description="Version of ruleset active during scan")
    confidence: ConfidenceBand = Field(..., description="Confidence calibration band")
    confidence_rationale: str = Field(..., description="Explanation for assigned confidence")
    state: EvidenceState = Field(default=EvidenceState.OBSERVED, description="Evidence state")

    observed_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp of observation",
    )
    raw_parameters: Dict[str, Any] = Field(
        default_factory=dict, description="Supplementary non-sensitive parameters"
    )


class DiscoverySummary(BaseModel):
    """Aggregate result of running all detectors across an extracted sandbox."""

    scan_id: str = Field(..., description="Scan identifier")
    total_files_analyzed: int = Field(default=0, ge=0)
    files_with_findings: int = Field(default=0, ge=0)
    files_with_zero_findings: int = Field(default=0, ge=0)
    unsupported_files_count: int = Field(default=0, ge=0)
    failed_parses_count: int = Field(default=0, ge=0)

    observations: List[Observation] = Field(
        default_factory=list, description="All collected cryptographic observations"
    )
    detector_health: Dict[str, str] = Field(
        default_factory=dict, description="Status per individual detector"
    )
    duration_ms: float = Field(default=0.0, ge=0.0)
