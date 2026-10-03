"""ASTRA - Truthful Coverage Accounting (Worker 01 - MVP-03).

Computes honest denominators, blind-spot visibility, and partial-scan
state transitions satisfying AC-01, AC-04, and AC-11.
"""

from collections import defaultdict
from typing import Dict, List, Set

from app.coverage.models import (
    CoverageReport,
    SurfaceCategory,
    SurfaceCoverage,
)
from app.discovery.models import DiscoverySummary
from app.intake.models import ScanManifest


class CoverageAccountant:
    """Computes transparent coverage accounting across all assessed repository surfaces."""

    SOURCE_EXTENSIONS: Set[str] = {
        ".py", ".java", ".js", ".jsx", ".ts", ".tsx",
        ".go", ".c", ".cpp", ".h", ".hpp", ".rs"
    }
    MANIFEST_NAMES: Set[str] = {
        "package.json", "pom.xml", "requirements.txt",
        "pyproject.toml", "go.mod", "Cargo.toml"
    }
    CONFIG_EXTENSIONS: Set[str] = {
        ".yaml", ".yml", ".conf", ".cnf", ".ini", ".properties", ".toml", ".env"
    }
    CERT_EXTENSIONS: Set[str] = {
        ".pem", ".crt", ".cer", ".der", ".pub", ".key"
    }

    def categorize_file(self, relative_path: str, extension: str) -> SurfaceCategory:
        """Map a repository file to its appropriate surface category."""
        filename = relative_path.split("/")[-1]
        ext = extension.lower()

        if filename in self.MANIFEST_NAMES:
            return SurfaceCategory.PACKAGE_MANIFEST
        if ext in self.CERT_EXTENSIONS:
            return SurfaceCategory.CERTIFICATE_STORE
        if ext in self.SOURCE_EXTENSIONS:
            return SurfaceCategory.SOURCE_CODE
        if ext in self.CONFIG_EXTENSIONS:
            return SurfaceCategory.CONFIGURATION
        return SurfaceCategory.UNSUPPORTED_SURFACE

    def evaluate_coverage(
        self,
        manifest: ScanManifest,
        summary: DiscoverySummary,
    ) -> CoverageReport:
        """Build an honest, auditable coverage report distinguishing findings, clean files, and unassessed gaps."""
        # Map findings by file
        findings_per_file: Dict[str, int] = defaultdict(int)
        for obs in summary.observations:
            findings_per_file[obs.relative_path] += 1

        surface_stats: Dict[SurfaceCategory, Dict[str, int]] = {
            cat: defaultdict(int) for cat in SurfaceCategory
        }
        unsupported_exts: Set[str] = set()

        total_files = len(manifest.files)
        total_assessed = 0
        total_unsupported = 0
        total_skipped = 0
        total_failed = summary.failed_parses_count

        for file_entry in manifest.files:
            if file_entry.skip_reason:
                total_skipped += 1
                continue

            category = self.categorize_file(file_entry.relative_path, file_entry.file_extension)
            surface_stats[category]["total"] += 1

            if category == SurfaceCategory.UNSUPPORTED_SURFACE:
                total_unsupported += 1
                surface_stats[category]["unsupported"] += 1
                if file_entry.file_extension:
                    unsupported_exts.add(file_entry.file_extension)
            else:
                total_assessed += 1
                surface_stats[category]["assessed"] += 1
                count = findings_per_file.get(file_entry.relative_path, 0)
                if count > 0:
                    surface_stats[category]["findings"] += 1
                else:
                    surface_stats[category]["clean"] += 1

        # Build SurfaceCoverage dictionary
        surface_breakdown: Dict[str, SurfaceCoverage] = {}
        for cat in SurfaceCategory:
            data = surface_stats[cat]
            t = data["total"]
            a = data["assessed"]
            pct = round((a / t * 100), 2) if t > 0 else 0.0
            surface_breakdown[cat.value] = SurfaceCoverage(
                surface=cat,
                total_files=t,
                assessed_files=a,
                files_with_findings=data["findings"],
                files_with_no_findings=data["clean"],
                unsupported_files=data["unsupported"],
                failed_files=0,
                coverage_percentage=pct,
            )

        overall_pct = round((total_assessed / total_files * 100), 2) if total_files > 0 else 0.0

        # Check for partial scan conditions
        is_partial = False
        collector_has_error = any(status.startswith("ERROR") for status in summary.detector_health.values())
        if collector_has_error or total_failed > 0:
            is_partial = True

        status_label = "COMPLETE_WITH_COVERAGE_ACCOUNTING"
        if is_partial:
            status_label = "PARTIAL_SCAN_COLLECTOR_DEGRADED"
        elif total_assessed == 0 and total_files > 0:
            status_label = "NOT_ASSESSED_ALL_UNSUPPORTED"
        elif summary.files_with_findings == 0:
            status_label = "NO_FINDINGS_IN_SUPPORTED_SCOPE"

        return CoverageReport(
            scan_id=manifest.scan_id,
            total_files_in_archive=total_files,
            total_assessed_files=total_assessed,
            total_unsupported_files=total_unsupported,
            total_skipped_files=total_skipped,
            total_failed_files=total_failed,
            total_observations_found=len(summary.observations),
            overall_coverage_percentage=overall_pct,
            is_partial_scan=is_partial,
            scan_status_label=status_label,
            surface_breakdown=surface_breakdown,
            unsupported_extensions=sorted(list(unsupported_exts)),
            collector_health=summary.detector_health,
        )
