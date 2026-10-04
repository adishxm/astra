"""ASTRA - Master Cryptographic Discovery Engine (Worker 01 - MVP-02).

Coordinates source, manifest, config, and certificate detectors across
sandboxed repositories and produces normalized cryptographic observations.
"""

import json
import time
from pathlib import Path
from typing import List, Optional

from app.discovery.detectors.binary_detector import BinaryCryptoDetector
from app.discovery.detectors.certificate_detector import CertificateCryptoDetector
from app.discovery.detectors.cloud_kms_detector import CloudKmsDetector
from app.discovery.detectors.config_detector import ConfigCryptoDetector
from app.discovery.detectors.container_detector import ContainerCryptoDetector
from app.discovery.detectors.manifest_detector import ManifestCryptoDetector
from app.discovery.detectors.network_detector import NetworkEndpointDetector
from app.discovery.detectors.pkcs11_detector import Pkcs11HsmDetector
from app.discovery.detectors.source_detector import SourceCryptoDetector
from app.discovery.models import (
    DiscoverySummary,
    Observation,
)
from app.intake.models import ScanManifest


class DiscoveryEngine:
    """Master discovery engine orchestrating all deterministic cryptographic detectors."""

    def __init__(self):
        self.source_detector = SourceCryptoDetector()
        self.manifest_detector = ManifestCryptoDetector()
        self.config_detector = ConfigCryptoDetector()
        self.cert_detector = CertificateCryptoDetector()
        self.binary_detector = BinaryCryptoDetector()
        self.container_detector = ContainerCryptoDetector()
        self.network_detector = NetworkEndpointDetector()
        self.cloud_kms_detector = CloudKmsDetector()
        self.pkcs11_detector = Pkcs11HsmDetector()

    def run_discovery(
        self,
        sandbox_dir: Path,
        manifest: ScanManifest,
        output_dir: Optional[Path] = None,
    ) -> DiscoverySummary:
        """Run all detectors against all files listed in the scan manifest."""
        start_time = time.perf_counter()

        observations: List[Observation] = []
        files_with_findings = set()
        files_analyzed = 0
        unsupported_count = 0
        failed_count = 0

        collector_health = {
            self.source_detector.DETECTOR_ID: "OK",
            self.manifest_detector.DETECTOR_ID: "OK",
            self.config_detector.DETECTOR_ID: "OK",
            self.cert_detector.DETECTOR_ID: "OK",
            self.binary_detector.DETECTOR_ID: "OK",
            self.container_detector.DETECTOR_ID: "OK",
            self.network_detector.DETECTOR_ID: "OK",
            self.cloud_kms_detector.DETECTOR_ID: "OK",
            self.pkcs11_detector.DETECTOR_ID: "OK",
        }

        # Scan each file in the sandbox
        for file_entry in manifest.files:
            if file_entry.skip_reason:
                continue

            file_path = sandbox_dir / file_entry.relative_path
            if not file_path.exists():
                continue

            files_analyzed += 1
            file_had_findings = False
            matched_detector = False

            # 1. Check Source Detector
            if self.source_detector.can_analyze(file_path):
                matched_detector = True
                try:
                    obs = self.source_detector.analyze_file(
                        file_path, file_entry.relative_path, manifest.scan_id
                    )
                    if obs:
                        observations.extend(obs)
                        file_had_findings = True
                except Exception as e:
                    failed_count += 1
                    collector_health[self.source_detector.DETECTOR_ID] = f"ERROR: {e}"

            # 2. Check Manifest Detector
            if self.manifest_detector.can_analyze(file_path):
                matched_detector = True
                try:
                    obs = self.manifest_detector.analyze_file(
                        file_path, file_entry.relative_path, manifest.scan_id
                    )
                    if obs:
                        observations.extend(obs)
                        file_had_findings = True
                except Exception as e:
                    failed_count += 1
                    collector_health[self.manifest_detector.DETECTOR_ID] = f"ERROR: {e}"

            # 3. Check Config Detector
            if self.config_detector.can_analyze(file_path):
                matched_detector = True
                try:
                    obs = self.config_detector.analyze_file(
                        file_path, file_entry.relative_path, manifest.scan_id
                    )
                    if obs:
                        observations.extend(obs)
                        file_had_findings = True
                except Exception as e:
                    failed_count += 1
                    collector_health[self.config_detector.DETECTOR_ID] = f"ERROR: {e}"

            # 4. Check Certificate Detector
            if self.cert_detector.can_analyze(file_path):
                matched_detector = True
                try:
                    obs = self.cert_detector.analyze_file(
                        file_path, file_entry.relative_path, manifest.scan_id
                    )
                    if obs:
                        observations.extend(obs)
                        file_had_findings = True
                except Exception as e:
                    failed_count += 1
                    collector_health[self.cert_detector.DETECTOR_ID] = f"ERROR: {e}"

            # 5. Check Binary Detector (Static safe analysis)
            if self.binary_detector.can_analyze(file_path):
                matched_detector = True
                try:
                    obs = self.binary_detector.analyze_file(
                        file_path, file_entry.relative_path, manifest.scan_id
                    )
                    if obs:
                        observations.extend(obs)
                        file_had_findings = True
                except Exception as e:
                    failed_count += 1
                    collector_health[self.binary_detector.DETECTOR_ID] = f"ERROR: {e}"

            # 6. Check Container Detector
            if self.container_detector.can_analyze(file_path):
                matched_detector = True
                try:
                    obs = self.container_detector.analyze_file(
                        file_path, file_entry.relative_path, manifest.scan_id
                    )
                    if obs:
                        observations.extend(obs)
                        file_had_findings = True
                except Exception as e:
                    failed_count += 1
                    collector_health[self.container_detector.DETECTOR_ID] = f"ERROR: {e}"

            # 7. Check Network Endpoint Detector
            if self.network_detector.can_analyze(file_path):
                matched_detector = True
                try:
                    obs = self.network_detector.analyze_file(
                        file_path, file_entry.relative_path, manifest.scan_id
                    )
                    if obs:
                        observations.extend(obs)
                        file_had_findings = True
                except Exception as e:
                    failed_count += 1
                    collector_health[self.network_detector.DETECTOR_ID] = f"ERROR: {e}"

            # 8. Check Cloud KMS Detector (AWS KMS, Azure Key Vault, GCP Cloud KMS)
            if self.cloud_kms_detector.can_analyze(file_path):
                matched_detector = True
                try:
                    obs = self.cloud_kms_detector.analyze_file(
                        file_path, file_entry.relative_path, manifest.scan_id
                    )
                    if obs:
                        observations.extend(obs)
                        file_had_findings = True
                except Exception as e:
                    failed_count += 1
                    collector_health[self.cloud_kms_detector.DETECTOR_ID] = f"ERROR: {e}"

            # 9. Check PKCS#11 Hardware Security Module (HSM) Detector
            if self.pkcs11_detector.can_analyze(file_path):
                matched_detector = True
                try:
                    obs = self.pkcs11_detector.analyze_file(
                        file_path, file_entry.relative_path, manifest.scan_id
                    )
                    if obs:
                        observations.extend(obs)
                        file_had_findings = True
                except Exception as e:
                    failed_count += 1
                    collector_health[self.pkcs11_detector.DETECTOR_ID] = f"ERROR: {e}"

            if not matched_detector:
                unsupported_count += 1

            if file_had_findings:
                files_with_findings.add(file_entry.relative_path)

        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

        summary = DiscoverySummary(
            scan_id=manifest.scan_id,
            total_files_analyzed=files_analyzed,
            files_with_findings=len(files_with_findings),
            files_with_zero_findings=files_analyzed - len(files_with_findings),
            unsupported_files_count=unsupported_count,
            failed_parses_count=failed_count,
            observations=observations,
            detector_health=collector_health,
            duration_ms=duration_ms,
        )

        # Persist observations for Worker 02
        out_dir = output_dir if output_dir else sandbox_dir
        obs_file = out_dir / "observations.json"
        try:
            with open(obs_file, "w", encoding="utf-8") as f:
                json.dump(summary.model_dump(mode="json"), f, indent=2, default=str)
        except OSError:
            pass

        return summary
