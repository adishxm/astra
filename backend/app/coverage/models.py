"""ASTRA - Coverage Accounting & Benchmark Domain Models (Worker 01 - MVP-03).

Provides truthful denominator accounting, blind-spot visibility,
and ground-truth benchmark metrics (precision, recall, F1).
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class SurfaceCategory(str, Enum):
    """Categorized surface of the repository."""

    SOURCE_CODE = "SOURCE_CODE"
    PACKAGE_MANIFEST = "PACKAGE_MANIFEST"
    CONFIGURATION = "CONFIGURATION"
    CERTIFICATE_STORE = "CERTIFICATE_STORE"
    UNSUPPORTED_SURFACE = "UNSUPPORTED_SURFACE"


class SurfaceCoverage(BaseModel):
    """Coverage statistics for an individual surface category."""

    surface: SurfaceCategory
    total_files: int = Field(default=0, ge=0)
    assessed_files: int = Field(default=0, ge=0)
    files_with_findings: int = Field(default=0, ge=0)
    files_with_no_findings: int = Field(default=0, ge=0)
    unsupported_files: int = Field(default=0, ge=0)
    failed_files: int = Field(default=0, ge=0)
    coverage_percentage: float = Field(default=0.0, ge=0.0, le=100.0)


class CoverageReport(BaseModel):
    """Truthful coverage and blind-spot accounting report.

    Enforces AC-04 and AC-11: zero findings is never reported as 'safe',
    and unassessed surfaces remain explicitly visible.
    """

    scan_id: str = Field(..., description="Scan identifier")
    total_files_in_archive: int = Field(default=0, ge=0)
    total_assessed_files: int = Field(default=0, ge=0)
    total_unsupported_files: int = Field(default=0, ge=0)
    total_skipped_files: int = Field(default=0, ge=0)
    total_failed_files: int = Field(default=0, ge=0)

    total_observations_found: int = Field(default=0, ge=0)
    overall_coverage_percentage: float = Field(default=0.0, ge=0.0, le=100.0)
    is_partial_scan: bool = Field(default=False, description="True if any collector failed or timed out")
    scan_status_label: str = Field(
        default="COMPLETE_WITH_COVERAGE_ACCOUNTING",
        description="Explaining coverage integrity",
    )

    surface_breakdown: Dict[str, SurfaceCoverage] = Field(
        default_factory=dict, description="Coverage stats per surface category"
    )
    unsupported_extensions: List[str] = Field(
        default_factory=list, description="Extensions found that lack rule support"
    )
    collector_health: Dict[str, str] = Field(
        default_factory=dict, description="Health status per detector component"
    )
    evaluated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp of coverage evaluation",
    )


class GroundTruthLabel(BaseModel):
    """Expected cryptographic finding for benchmark adjudication."""

    relative_path: str = Field(..., description="Expected file path")
    expected_algorithm: str = Field(..., description="Expected algorithm name (e.g. RSA, AES, SHA-256)")
    expected_line: Optional[int] = Field(None, description="Expected line number if precise")
    is_negative_fixture: bool = Field(default=False, description="True if this fixture should have zero findings")


class BenchmarkMetric(BaseModel):
    """Evaluated precision, recall, and F1 metrics on seeded corpus."""

    target_class: str = Field(..., description="Category or algorithm class evaluated")
    true_positives: int = Field(default=0, ge=0)
    false_positives: int = Field(default=0, ge=0)
    false_negatives: int = Field(default=0, ge=0)
    precision: float = Field(default=0.0, ge=0.0, le=1.0)
    recall: float = Field(default=0.0, ge=0.0, le=1.0)
    f1_score: float = Field(default=0.0, ge=0.0, le=1.0)
    target_met: bool = Field(default=False, description="Whether precision and recall >= 80%")


class BenchmarkEvaluation(BaseModel):
    """Aggregate benchmark report on the seeded supported-source corpus (AC-06)."""

    benchmark_id: str = Field(..., description="Benchmark run identifier")
    corpus_version: str = Field(..., description="Version of the seeded benchmark corpus")
    ruleset_version: str = Field(..., description="Version of discovery ruleset used")

    total_fixtures: int = Field(default=0, ge=0)
    total_expected_findings: int = Field(default=0, ge=0)
    total_detected_findings: int = Field(default=0, ge=0)

    overall_precision: float = Field(default=0.0, ge=0.0, le=1.0)
    overall_recall: float = Field(default=0.0, ge=0.0, le=1.0)
    overall_f1: float = Field(default=0.0, ge=0.0, le=1.0)
    ac06_target_achieved: bool = Field(
        default=False, description="True if both precision and recall >= 0.80"
    )

    per_class_metrics: Dict[str, BenchmarkMetric] = Field(
        default_factory=dict, description="Metrics broken down by algorithm/fixture class"
    )
    evaluated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
