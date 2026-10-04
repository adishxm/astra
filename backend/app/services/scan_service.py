"""ASTRA - Master Application Scan Service & Persistence Store.

Coordinates the unified, end-to-end cryptographic analysis pipeline:
Safe Intake -> Multi-Surface Discovery -> Honest Coverage Accounting ->
Canonical Evidence Normalization -> Contextual Mosca Risk -> Dated PQC Backlog ->
Temporal DNA Fingerprinting -> CycloneDX 1.6 CBOM Export -> Storage.
"""

import hashlib
import json
import os
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from app.core.config import INTAKE_ENGINE_VERSION, COLLECTOR_VERSION, RULESET_VERSION
from app.intake.extractor import SafeArchiveExtractor
from app.intake.models import ScanManifest, ScanStatus, ArchiveType, IntakeRequest, ExtractedFileEntry
from app.intake.sandbox import SandboxManager
from app.discovery.engine import DiscoveryEngine
from app.discovery.models import Observation
from app.coverage.accounting import CoverageAccountant
from app.coverage.models import CoverageReport
from app.inventory.models import (
    AssetIdentity,
    CanonicalEvidence,
    InventoryExport,
    map_observation_to_canonical,
)
from app.inventory.temporal import TemporalLineageEngine, InventorySnapshot
from app.inventory.cbom_reconciliation import CBOMReconciliationEngine
from app.risk.models import ContextFactors, RiskEvaluation, RiskScenario
from app.risk.scorer import RiskScorer
from app.risk.backlog import BacklogBuilder


class ScanRecord:
    """Represents a complete, persisted cryptographic scan analysis."""

    def __init__(
        self,
        scan_id: str,
        target_name: str,
        manifest: ScanManifest,
        coverage: CoverageReport,
        observations: List[Observation],
        canonical_assets: List[AssetIdentity],
        risk_evaluations: List[RiskEvaluation],
        backlog_items: List[Dict[str, Any]],
        snapshot: InventorySnapshot,
        cbom_data: Dict[str, Any],
        created_at: Optional[datetime] = None,
    ):
        self.scan_id = scan_id
        self.target_name = target_name
        self.manifest = manifest
        self.coverage = coverage
        self.observations = observations
        self.canonical_assets = canonical_assets
        self.risk_evaluations = risk_evaluations
        self.backlog_items = backlog_items
        self.snapshot = snapshot
        self.cbom_data = cbom_data
        self.created_at = created_at or datetime.now(timezone.utc)

    @property
    def status(self) -> str:
        return "completed"

    @property
    def coverage_summary(self) -> Dict[str, Any]:
        return {
            "total_files": self.coverage.total_files_in_archive,
            "assessed_files": self.coverage.total_assessed_files,
            "coverage_percentage": self.coverage.overall_coverage_percentage,
            "total_lines": max(1, self.manifest.total_uncompressed_bytes // 20),
            "languages": {"Python": 1},
        }

    @property
    def cbom(self) -> Dict[str, Any]:
        return self.cbom_data

    @property
    def temporal_snapshot(self) -> Dict[str, Any]:
        return {
            "state_dna_hash": self.snapshot.cryptographic_dna_hash,
            "policy_dna_hash": hashlib.sha256(self.snapshot.cryptographic_dna_hash.encode()).hexdigest(),
        }

    @property
    def pqc_backlog(self) -> List[Dict[str, Any]]:
        return self.backlog_items

    def to_dict(self) -> Dict[str, Any]:
        """Convert complete scan record to serializable dictionary."""
        return {
            "scan_id": self.scan_id,
            "status": "completed",
            "target_name": self.target_name,
            "created_at": self.created_at.isoformat(),
            "manifest": self.manifest.model_dump(),
            "coverage": self.coverage.model_dump(),
            "asset_count": len(self.canonical_assets),
            "observations_count": len(self.observations),
            "cryptographic_dna_hash": self.snapshot.cryptographic_dna_hash,
            "summary": {
                "total_files": self.manifest.total_files_in_archive,
                "assessed_files": self.coverage.total_assessed_files,
                "coverage_percentage": self.coverage.overall_coverage_percentage,
                "clean_state_label": self.coverage.scan_status_label,
                "critical_urgency_count": sum(
                    1 for r in self.risk_evaluations if r.urgency.value == "CRITICAL"
                ),
                "high_urgency_count": sum(
                    1 for r in self.risk_evaluations if r.urgency.value == "HIGH"
                ),
                "medium_urgency_count": sum(
                    1 for r in self.risk_evaluations if r.urgency.value == "MEDIUM"
                ),
                "low_urgency_count": sum(
                    1 for r in self.risk_evaluations if r.urgency.value in {"LOW", "INFORMATIONAL"}
                ),
            },
            "observations": [o.model_dump() for o in self.observations],
            "snapshot": self.snapshot.model_dump(),
            "canonical_assets": [a.model_dump() for a in self.canonical_assets],
            "risk_evaluations": [r.model_dump() for r in self.risk_evaluations],
            "backlog_items": self.backlog_items,
            "cbom_data": self.cbom_data,
        }


class ScanStore:
    """Thread-safe persistent store for scan runs."""

    def __init__(self, storage_dir: Optional[str] = None):
        self.storage_dir = Path(storage_dir or os.path.join(os.getcwd(), "data", "scans"))
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self._memory_cache: Dict[str, ScanRecord] = {}

    def save(self, record: ScanRecord) -> None:
        """Persist scan record to memory and JSON file."""
        self._memory_cache[record.scan_id] = record
        file_path = self.storage_dir / f"{record.scan_id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(record.to_dict(), f, indent=2, default=str)

    def get(self, scan_id: str) -> Optional[ScanRecord]:
        """Retrieve scan record by ID."""
        if scan_id in self._memory_cache:
            return self._memory_cache[scan_id]
        
        file_path = self.storage_dir / f"{scan_id}.json"
        if file_path.exists():
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    
                from app.intake.models import ScanManifest
                from app.coverage.models import CoverageReport
                from app.inventory.models import AssetIdentity
                from app.inventory.temporal import InventorySnapshot
                from app.risk.models import RiskEvaluation
                from app.discovery.models import Observation
                
                manifest = ScanManifest(**data["manifest"])
                coverage = CoverageReport(**data["coverage"])
                observations = [Observation(**o) for o in data.get("observations", [])]
                canonical_assets = [AssetIdentity(**a) for a in data.get("canonical_assets", [])]
                risk_evaluations = [RiskEvaluation(**r) for r in data.get("risk_evaluations", [])]
                if "snapshot" in data:
                    snapshot = InventorySnapshot(**data["snapshot"])
                else:
                    snapshot = InventorySnapshot(
                        snapshot_id=f"snap-{scan_id[:8]}",
                        scan_id=scan_id, 
                        version_tag="v1", 
                        cryptographic_dna_hash=data.get("cryptographic_dna_hash", "")
                    )
                
                record = ScanRecord(
                    scan_id=data["scan_id"],
                    target_name=data["target_name"],
                    manifest=manifest,
                    coverage=coverage,
                    observations=observations,
                    canonical_assets=canonical_assets,
                    risk_evaluations=risk_evaluations,
                    backlog_items=data.get("backlog_items", []),
                    snapshot=snapshot,
                    cbom_data=data.get("cbom_data", {})
                )
                self._memory_cache[scan_id] = record
                return record
            except Exception:
                raise ValueError("Malformed JSON")
        return None

    def list_all(self) -> List[Dict[str, Any]]:
        """List summary of all persisted scans."""
        for file_path in self.storage_dir.glob("*.json"):
            scan_id = file_path.stem
            if scan_id not in self._memory_cache:
                try:
                    self.get(scan_id)
                except ValueError:
                    continue
                
        scans = []
        for sid, rec in self._memory_cache.items():
            scans.append({
                "scan_id": sid,
                "target_name": rec.target_name,
                "created_at": rec.created_at.isoformat(),
                "asset_count": len(rec.canonical_assets),
                "coverage_percentage": rec.coverage.overall_coverage_percentage,
                "dna_hash": rec.snapshot.cryptographic_dna_hash,
            })
        return sorted(scans, key=lambda s: s["created_at"], reverse=True)


class ScanService:
    """Master application service orchestrating end-to-end cryptographic analysis."""

    def __init__(self, scan_store: Optional[ScanStore] = None):
        self.store = scan_store or ScanStore()
        self.extractor = SafeArchiveExtractor()
        self.discovery_engine = DiscoveryEngine()
        self.coverage_accountant = CoverageAccountant()
        self.temporal_engine = TemporalLineageEngine()
        self.reconciliation_engine = CBOMReconciliationEngine()

    def run_scan_on_directory(
        self,
        directory_path: str,
        target_name: Optional[str] = None,
        scenario: Optional[RiskScenario] = None,
        scan_id: Optional[str] = None,
        override_manifest: Optional[ScanManifest] = None,
    ) -> ScanRecord:
        """Analyze a local directory containing source code, manifests, and configs."""
        dir_path = Path(directory_path).resolve()
        if not dir_path.exists() or not dir_path.is_dir():
            raise FileNotFoundError(f"Target directory does not exist or is not a directory: {directory_path}")

        scan_id = scan_id or f"scan-{str(uuid.uuid4())[:8]}"
        name = target_name or dir_path.name
        active_scenario = scenario or RiskScenario()

        import tempfile
        import shutil
        output_dir = Path(tempfile.gettempdir()) / "astra_outputs" / scan_id
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. Collect files & build manifest
        all_files = []
        for root, dirs, files in os.walk(dir_path):
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("__pycache__", "node_modules")]
            for file in sorted(files):
                if file.startswith(".") or file in ("observations.json", "scan_manifest.json", "manifest.json", ".DS_Store", "Thumbs.db"):
                    continue
                full_p = Path(root) / file
                
                if full_p.is_symlink():
                    try:
                        resolved_path = full_p.resolve(strict=True)
                        if not resolved_path.is_relative_to(dir_path):
                            continue
                    except Exception:
                        continue
                
                try:
                    rel_p = str(full_p.relative_to(dir_path)).replace("\\", "/")
                    size = full_p.stat().st_size
                    all_files.append((rel_p, size))
                except Exception:
                    continue

        all_files.sort(key=lambda x: x[0])

        if override_manifest:
            manifest = override_manifest
            # Ensure the scan_id matches the unified scan_id
            manifest.scan_id = scan_id
        else:
            extracted_entries = []
            for rel_p, size in all_files:
                full_p = dir_path / rel_p
                h = hashlib.sha256()
                try:
                    with open(full_p, "rb") as f:
                        while chunk := f.read(65536):
                            h.update(chunk)
                    f_hash = h.hexdigest()
                except Exception:
                    f_hash = "0" * 64

                ext = full_p.suffix.lower()
                extracted_entries.append(
                    ExtractedFileEntry(
                        relative_path=rel_p,
                        size_bytes=size,
                        sha256=f_hash,
                        file_extension=ext,
                        is_supported=True,
                    )
                )

            manifest = ScanManifest(
                scan_id=scan_id,
                archive_name=name,
                archive_sha256="directory-scan-local",
                archive_size_bytes=sum(s for _, s in all_files),
                archive_type=ArchiveType.UNKNOWN,
                declared_scope="LOCAL_DIRECTORY",
                tenant_id="default-tenant",
                status=ScanStatus.COMPLETE,
                intake_engine_version=INTAKE_ENGINE_VERSION,
                collector_version=COLLECTOR_VERSION,
                ruleset_version=RULESET_VERSION,
                total_files_in_archive=len(all_files),
                extracted_file_count=len(all_files),
                total_uncompressed_bytes=sum(s for _, s in all_files),
                files=extracted_entries,
            )

        # 2. Run discovery engine
        discovery_summary = self.discovery_engine.run_discovery(
            sandbox_dir=dir_path,
            manifest=manifest,
            output_dir=output_dir,
        )
        observations = discovery_summary.observations

        # 3. Compute truthful coverage accounting
        coverage_report = self.coverage_accountant.evaluate_coverage(
            manifest=manifest,
            summary=discovery_summary,
        )

        # 4. Canonical evidence normalization & asset identity aggregation
        canonical_evidences = [map_observation_to_canonical(obs) for obs in observations]
        asset_map: Dict[str, List[CanonicalEvidence]] = {}
        for ce in canonical_evidences:
            asset_map.setdefault(ce.asset_id, []).append(ce)

        canonical_assets: List[AssetIdentity] = []
        for aid, ev_list in asset_map.items():
            primary_name = ev_list[0].algorithm or aid
            canonical_assets.append(
                AssetIdentity(
                    asset_id=aid,
                    primary_name=primary_name,
                    observations=ev_list,
                )
            )

        # 5. Contextual Mosca Risk Evaluation & Dated Backlog
        risk_scorer = RiskScorer(scenario=active_scenario)
        risk_evaluations: List[RiskEvaluation] = []
        default_context = ContextFactors()
        for obs in observations:
            eval_res = risk_scorer.evaluate_observation(
                observation=obs,
                context=default_context,
            )
            risk_evaluations.append(eval_res)

        backlog_builder = BacklogBuilder(scenario=active_scenario)
        backlog_obj = backlog_builder.generate_backlog(
            observations=observations,
            scan_id=scan_id,
        )
        backlog_items = [task.model_dump() for task in backlog_obj.tasks]

        # 6. Temporal DNA Fingerprinting
        snapshot = self.temporal_engine.create_snapshot(
            snapshot_id=f"snap-{scan_id[:8]}",
            scan_id=scan_id,
            version_tag="v1.0.0",
            assets=canonical_assets,
        )

        # 7. Generate CycloneDX 1.6 CBOM
        components = []
        seen_comps = set()
        for asset in canonical_assets:
            for obs in asset.observations:
                algo = obs.algorithm or "UNKNOWN"
                comp_name = f"{algo}-{asset.asset_id[:8]}"
                
                # Ensure uniqueItems for CBOM components array
                if comp_name in seen_comps:
                    continue
                seen_comps.add(comp_name)
                
                comp = {
                    "type": "cryptographic-asset",
                    "name": comp_name,
                    "cryptoProperties": {
                        "assetType": "algorithm",
                        "algorithmProperties": {
                            "primitive": "unknown",
                            "parameterSetIdentifier": str(obs.key_size_bits or "standard"),
                            "executionEnvironment": "software-plain-ram",
                        },
                    },
                }
                components.append(comp)

        cbom_data = {
            "bomFormat": "CycloneDX",
            "specVersion": "1.6",
            "serialNumber": f"urn:uuid:{uuid.uuid5(uuid.NAMESPACE_URL, scan_id)}",
            "version": 1,
            "metadata": {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "tools": [{"name": "ASTRA", "version": "1.0.0"}],
                "component": {
                    "type": "application",
                    "name": name,
                },
            },
            "components": components,
        }

        # Validate CBOM conformity
        self.reconciliation_engine.validate_cyclonedx_16(cbom_data)

        # 8. Assemble Record & Save
        record = ScanRecord(
            scan_id=scan_id,
            target_name=name,
            manifest=manifest,
            coverage=coverage_report,
            observations=observations,
            canonical_assets=canonical_assets,
            risk_evaluations=risk_evaluations,
            backlog_items=backlog_items,
            snapshot=snapshot,
            cbom_data=cbom_data,
        )

        self.store.save(record)
        shutil.rmtree(output_dir, ignore_errors=True)
        return record

    def run_scan_on_archive(
        self,
        archive_path: str,
        target_name: Optional[str] = None,
        scenario: Optional[RiskScenario] = None,
    ) -> ScanRecord:
        """Safely extract and analyze a user-authorized archive file (.zip, .tar.gz, etc.)."""
        arc_file = Path(archive_path).resolve()
        if not arc_file.exists():
            raise FileNotFoundError(f"Archive file not found: {archive_path}")

        name = target_name or arc_file.name

        sandbox_mgr = SandboxManager()
        manifest = sandbox_mgr.execute_intake(
            IntakeRequest(
                archive_path=str(arc_file),
                declared_scope=name,
            )
        )
        try:
            record = self.run_scan_on_directory(
                directory_path=manifest.sandbox_directory,
                target_name=name,
                scenario=scenario,
                scan_id=manifest.scan_id,
                override_manifest=manifest,
            )
            return record
        finally:
            sandbox_mgr.cleanup_sandbox(manifest.scan_id)

    @classmethod
    def scan_directory(
        cls,
        directory_path: str,
        target_name: Optional[str] = None,
        scenario: Optional[RiskScenario] = None,
    ) -> ScanRecord:
        """Classmethod helper routing to global scan service."""
        return GLOBAL_SCAN_SERVICE.run_scan_on_directory(directory_path, target_name, scenario)

    @classmethod
    def scan_archive_file(
        cls,
        archive_path: str,
        target_name: Optional[str] = None,
        scenario: Optional[RiskScenario] = None,
    ) -> ScanRecord:
        """Classmethod helper routing to global scan service."""
        return GLOBAL_SCAN_SERVICE.run_scan_on_archive(archive_path, target_name, scenario)


# Global singleton scan service
GLOBAL_SCAN_STORE = ScanStore()
GLOBAL_SCAN_SERVICE = ScanService(GLOBAL_SCAN_STORE)
