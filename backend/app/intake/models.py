"""ASTRA - Intake Domain Models & Schemas.

Represents scan lifecycle states, archive intake requests, extracted file entries,
and the reproducible ScanManifest conforming to W01 <-> W04 contracts.
"""

from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class ScanStatus(str, Enum):
    """Scan lifecycle states."""

    QUEUED = "QUEUED"
    VALIDATING = "VALIDATING"
    RUNNING = "RUNNING"
    COMPLETE = "COMPLETE"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"
    REJECTED = "REJECTED"


class ArchiveType(str, Enum):
    """Supported archive formats."""

    ZIP = "ZIP"
    TAR = "TAR"
    TAR_GZ = "TAR_GZ"
    TAR_BZ2 = "TAR_BZ2"
    UNKNOWN = "UNKNOWN"


class ExtractedFileEntry(BaseModel):
    """Metadata for an individual extracted file in the sandbox."""

    relative_path: str = Field(..., description="Repository-relative normalized path")
    size_bytes: int = Field(..., ge=0, description="Uncompressed file size in bytes")
    sha256: str = Field(..., description="SHA-256 digest of file content")
    file_extension: str = Field(default="", description="Lower-case file extension")
    is_supported: bool = Field(
        default=False,
        description="Whether this file format has a supported cryptographic parser",
    )
    skip_reason: Optional[str] = Field(
        default=None,
        description="Reason if skipped (e.g. DANGEROUS_EXT, OVERSIZED, UNSUPPORTED)",
    )


class IntakeRequest(BaseModel):
    """Client request to initiate an archive scan."""

    archive_path: str = Field(..., description="Path to archive on disk")
    declared_scope: str = Field(
        default="LOCAL_ARCHIVE",
        description="Declared organizational or repository scope",
    )
    tenant_id: str = Field(default="default-tenant", description="Tenant or owner identifier")
    declared_name: Optional[str] = Field(
        default=None, description="Optional custom name for repository/archive"
    )
    context_notes: Optional[str] = Field(
        default=None, description="Optional contextual notes supplied by user"
    )


class ScanManifest(BaseModel):
    """Reproducible manifest of an intake and extraction run.

    Provides auditability and evidence anchoring for downstream discovery (W02)
    and UI presentation (W04).
    """

    scan_id: str = Field(..., description="Unique UUIDv4 scan identifier")
    archive_name: str = Field(..., description="Base filename of uploaded archive")
    archive_sha256: str = Field(..., description="SHA-256 digest of raw uploaded archive")
    archive_size_bytes: int = Field(..., ge=0, description="Raw upload archive size in bytes")
    archive_type: ArchiveType = Field(..., description="Identified archive container format")
    declared_scope: str = Field(..., description="Declared scope or repository name")
    tenant_id: str = Field(..., description="Tenant identifier")

    status: ScanStatus = Field(
        default=ScanStatus.QUEUED, description="Current lifecycle state of the scan"
    )
    rejection_code: Optional[str] = Field(
        default=None, description="Standardized rejection code if status is REJECTED"
    )
    rejection_reason: Optional[str] = Field(
        default=None, description="Sanitized human-readable rejection explanation"
    )

    started_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when intake started",
    )
    completed_at: Optional[datetime] = Field(
        default=None, description="Timestamp when intake/validation completed"
    )

    intake_engine_version: str = Field(..., description="Version of intake processor")
    collector_version: str = Field(..., description="Version of collector engine")
    ruleset_version: str = Field(..., description="Version of active cryptographic ruleset")

    # Metrics & Denominator
    total_files_in_archive: int = Field(default=0, ge=0)
    extracted_file_count: int = Field(default=0, ge=0)
    skipped_file_count: int = Field(default=0, ge=0)
    total_uncompressed_bytes: int = Field(default=0, ge=0)
    compression_ratio: float = Field(default=0.0, ge=0.0)

    # Sandbox location (internal reference, sanitized in external exports)
    sandbox_directory: Optional[str] = Field(
        default=None, description="Internal path to sandbox workspace"
    )

    # File inventory
    files: List[ExtractedFileEntry] = Field(
        default_factory=list, description="Extracted file inventory"
    )
    collector_health: Dict[str, str] = Field(
        default_factory=dict, description="Status per collector component"
    )
