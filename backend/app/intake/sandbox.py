"""ASTRA - Sandbox Lifecycle & Scan Boundary Manager.

Provides isolated sandbox directory creation, read-only enforcement,
and manifest persistence for downstream worker consumption.
"""

import json
import shutil
import tempfile
import uuid
from pathlib import Path
from typing import Optional

from app.core.config import IntakeLimits
from app.core.security import make_tree_readonly
from app.intake.extractor import SafeArchiveExtractor
from app.intake.models import (
    IntakeRequest,
    ScanManifest,
    ScanStatus,
)


class SandboxManager:
    """Manages ephemeral, isolated sandbox workspaces for archive extraction."""

    def __init__(
        self,
        base_dir: Optional[Path] = None,
        limits: Optional[IntakeLimits] = None,
        retain_on_error: bool = False,
    ):
        self.base_dir = base_dir or Path(tempfile.gettempdir()) / "astra_sandboxes"
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.limits = limits or IntakeLimits()
        self.retain_on_error = retain_on_error
        self.extractor = SafeArchiveExtractor(limits=self.limits)

    def create_sandbox_path(self, scan_id: str) -> Path:
        """Create a dedicated sandbox path for a scan ID."""
        sandbox_path = self.base_dir / f"scan_{scan_id}"
        sandbox_path.mkdir(parents=True, exist_ok=True)
        return sandbox_path

    def execute_intake(self, request: IntakeRequest, scan_id: Optional[str] = None) -> ScanManifest:
        """Process an archive intake request within a guarded sandbox."""
        scan_id = scan_id or f"scan-{str(uuid.uuid4())[:8]}"
        sandbox_dir = self.create_sandbox_path(scan_id)
        archive_path = Path(request.archive_path)

        try:
            manifest = self.extractor.process_and_extract(
                archive_path=archive_path,
                sandbox_dir=sandbox_dir,
                scan_id=scan_id,
                declared_scope=request.declared_scope,
                tenant_id=request.tenant_id,
            )

            # Apply read-only isolation across the extracted sandbox tree
            make_tree_readonly(sandbox_dir)

            # Persist scan manifest inside sandbox for downstream stages and backup adjacent
            manifest_file = sandbox_dir / "scan_manifest.json"
            with open(manifest_file, "w", encoding="utf-8") as f:
                json.dump(manifest.model_dump(mode="json"), f, indent=2, default=str)

            backup_manifest = self.base_dir / f"scan_{scan_id}_manifest.json"
            with open(backup_manifest, "w", encoding="utf-8") as f:
                json.dump(manifest.model_dump(mode="json"), f, indent=2, default=str)

            return manifest

        except Exception as e:
            if not self.retain_on_error and sandbox_dir.exists():
                shutil.rmtree(sandbox_dir, ignore_errors=True)
            raise

    def cleanup_sandbox(self, scan_id: str) -> bool:
        """Purge sandbox directory for given scan ID."""
        manifest_file = self.base_dir / f"scan_{scan_id}_manifest.json"
        if manifest_file.exists():
            manifest_file.unlink(missing_ok=True)

        sandbox_dir = self.base_dir / f"scan_{scan_id}"
        if sandbox_dir.exists():
            # In Windows, files marked read-only cannot be deleted by rmtree without an onerror handler
            def _remove_readonly(func, path, exc_info):
                import os
                import stat

                os.chmod(path, stat.S_IWRITE)
                func(path)

            shutil.rmtree(sandbox_dir, onerror=_remove_readonly)
            return True
        return False
