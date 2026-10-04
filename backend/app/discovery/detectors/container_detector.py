"""ASTRA - Container & Image Layer Cryptographic Detector (Worker 01 - PROD-01).

Inspects container definitions, Dockerfiles, OCI layer manifests, and layer tar archives.
Detects:
- Base images and their cryptographic baseline capabilities
- Cryptographic packages installed via package managers (apt, apk, yum, pip)
- Cryptographic environment variable configurations
- Embedded trust anchors and certificate bundle references
- Discovered cryptographic modules directly within unpacked OCI image layers
"""

import hashlib
import json
import re
import tarfile
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from app.core.config import RULESET_VERSION
from app.discovery.models import (
    ClaimType,
    ConfidenceBand,
    EvidenceState,
    Observation,
    SourceKind,
)

# Known crypto packages in container environments
CONTAINER_CRYPTO_PACKAGES: Dict[str, Tuple[str, str, ConfidenceBand]] = {
    "openssl": ("OpenSSL", "SYSTEM_CRYPTO_SUITE", ConfidenceBand.HIGH),
    "libssl-dev": ("OpenSSL-Dev", "DEVELOPMENT_CRYPTO_HEADERS", ConfidenceBand.HIGH),
    "libssl3": ("OpenSSL-3.x", "SYSTEM_CRYPTO_SUITE", ConfidenceBand.HIGH),
    "libssl1.1": ("OpenSSL-1.1", "LEGACY_CRYPTO_SUITE", ConfidenceBand.HIGH),
    "gnutls-bin": ("GnuTLS", "SYSTEM_CRYPTO_SUITE", ConfidenceBand.HIGH),
    "libgnutls30": ("GnuTLS", "SYSTEM_CRYPTO_SUITE", ConfidenceBand.HIGH),
    "wolfssl": ("WolfSSL", "EMBEDDED_CRYPTO_SUITE", ConfidenceBand.HIGH),
    "liboqs": ("liboqs", "PQC_ALGORITHMS", ConfidenceBand.CONFIRMED),
    "liboqs-dev": ("liboqs-Dev", "PQC_ALGORITHMS", ConfidenceBand.CONFIRMED),
    "ca-certificates": ("X.509-Root-Trust-Store", "PKI_TRUST_STORE", ConfidenceBand.HIGH),
    "cryptography": ("Python-cryptography", "APPLICATION_CRYPTO", ConfidenceBand.HIGH),
    "bouncycastle": ("BouncyCastle", "JAVA_CRYPTO_PROVIDER", ConfidenceBand.HIGH),
}

# Crypto configuration environment variables
CRYPTO_ENV_VARS: Dict[str, Tuple[str, str]] = {
    "OPENSSL_CONF": ("OpenSSL-Configuration", "CONFIG_PATH"),
    "SSL_CERT_DIR": ("X.509-Trust-Directory", "TRUST_STORE_PATH"),
    "SSL_CERT_FILE": ("X.509-Certificate-Bundle", "CERTIFICATE_PATH"),
    "NODE_EXTRA_CA_CERTS": ("NodeJS-Custom-CA", "CA_TRUST_OVERRIDE"),
    "REQUESTS_CA_BUNDLE": ("Python-Requests-CA", "CA_TRUST_OVERRIDE"),
}


class ContainerCryptoDetector:
    """Deterministic container layer and Dockerfile analyzer conforming to Worker 01 PROD-01."""

    DETECTOR_ID = "container_crypto_detector_v1"

    def can_analyze(self, file_path: Path) -> bool:
        """Check if file is a Dockerfile, Containerfile, OCI layer archive, or container manifest."""
        name = file_path.name.lower()
        if name in {"dockerfile", "containerfile"} or name.startswith("dockerfile.") or name.startswith("containerfile."):
            return True
        if name in {"manifest.json", "layer.json", "index.json", "oci-layout"}:
            return True
        if name.endswith(".tar") and any(k in name for k in ("layer", "image", "oci", "container")):
            return True
        return False

    def analyze_file(
        self,
        file_path: Path,
        relative_path: str,
        scan_id: str,
    ) -> List[Observation]:
        """Analyze container definitions, OCI manifests, and layer archives."""
        name = file_path.name.lower()

        # 1. OCI Layer Archive (.tar)
        if name.endswith(".tar"):
            return self._analyze_tar_layer(file_path, relative_path, scan_id)

        # 2. OCI / Docker Manifest or Layout JSON
        if name in {"manifest.json", "layer.json", "index.json", "oci-layout"}:
            return self._analyze_oci_manifest(file_path, relative_path, scan_id)

        # 3. Dockerfile / Containerfile
        return self._analyze_dockerfile(file_path, relative_path, scan_id)

    def _analyze_dockerfile(
        self,
        file_path: Path,
        relative_path: str,
        scan_id: str,
    ) -> List[Observation]:
        """Analyze Dockerfile instructions for base image, packages, and crypto env variables."""
        observations: List[Observation] = []

        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
        except OSError as e:
            return [
                Observation(
                    observation_id=str(uuid.uuid4()),
                    scan_id=scan_id,
                    candidate_asset_id=f"container:unreadable:{hashlib.sha256(relative_path.encode()).hexdigest()[:12]}",
                    claim_type=ClaimType.CONTAINER_PACKAGE,
                    source_kind=SourceKind.CONTAINER,
                    relative_path=relative_path,
                    evidence_digest=hashlib.sha256(str(e).encode()).hexdigest(),
                    sanitized_excerpt=f"Error reading container definition: {e}",
                    detector_id=self.DETECTOR_ID,
                    ruleset_version=RULESET_VERSION,
                    confidence=ConfidenceBand.LOW,
                    confidence_rationale="Container definition read failure",
                    state=EvidenceState.FAILED,
                )
            ]

        for line_num, line in enumerate(lines, start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue

            # Check FROM instruction (Base Image)
            if stripped.upper().startswith("FROM "):
                parts = stripped.split()
                if len(parts) > 1:
                    base_image = parts[1]
                    obs_id = str(uuid.uuid4())
                    excerpt = f"Base Image: {base_image}"
                    digest = hashlib.sha256(excerpt.encode()).hexdigest()

                    observations.append(
                        Observation(
                            observation_id=obs_id,
                            scan_id=scan_id,
                            candidate_asset_id=f"container:base:{hashlib.sha256(base_image.encode()).hexdigest()[:10]}",
                            claim_type=ClaimType.CONTAINER_PACKAGE,
                            source_kind=SourceKind.CONTAINER,
                            algorithm=f"CONTAINER_BASE:{base_image}",
                            purpose="BASE_OPERATING_SYSTEM_CRYPTO",
                            relative_path=relative_path,
                            start_line=line_num,
                            end_line=line_num,
                            evidence_digest=digest,
                            sanitized_excerpt=stripped[:180],
                            detector_id=self.DETECTOR_ID,
                            ruleset_version=RULESET_VERSION,
                            confidence=ConfidenceBand.MEDIUM,
                            confidence_rationale=f"Base image reference {base_image} dictates host cryptographic primitives",
                            state=EvidenceState.DECLARED,
                            raw_parameters={"base_image": base_image},
                        )
                    )

            # Check Package Installations (RUN apt-get / apk / yum)
            if stripped.upper().startswith("RUN "):
                for pkg_name, (algo, purpose, conf) in CONTAINER_CRYPTO_PACKAGES.items():
                    pattern = rf"\b{re.escape(pkg_name)}\b"
                    if re.search(pattern, stripped, re.IGNORECASE):
                        obs_id = str(uuid.uuid4())
                        excerpt = stripped[:200]
                        digest = hashlib.sha256(excerpt.encode()).hexdigest()

                        observations.append(
                            Observation(
                                observation_id=obs_id,
                                scan_id=scan_id,
                                candidate_asset_id=f"container:pkg:{pkg_name}:{hashlib.sha256(relative_path.encode()).hexdigest()[:8]}",
                                claim_type=ClaimType.CONTAINER_PACKAGE,
                                source_kind=SourceKind.CONTAINER,
                                algorithm=algo,
                                purpose=purpose,
                                relative_path=relative_path,
                                start_line=line_num,
                                end_line=line_num,
                                evidence_digest=digest,
                                sanitized_excerpt=excerpt,
                                detector_id=self.DETECTOR_ID,
                                ruleset_version=RULESET_VERSION,
                                confidence=conf,
                                confidence_rationale=f"Cryptographic system package '{pkg_name}' explicitly installed in container",
                                state=EvidenceState.DECLARED,
                                raw_parameters={"package_name": pkg_name, "command": stripped[:100]},
                            )
                        )

            # Check ENV configurations
            if stripped.upper().startswith("ENV "):
                for env_var, (algo, purpose) in CRYPTO_ENV_VARS.items():
                    if env_var in stripped:
                        obs_id = str(uuid.uuid4())
                        excerpt = stripped[:150]
                        digest = hashlib.sha256(excerpt.encode()).hexdigest()

                        observations.append(
                            Observation(
                                observation_id=obs_id,
                                scan_id=scan_id,
                                candidate_asset_id=f"container:env:{env_var}:{hashlib.sha256(relative_path.encode()).hexdigest()[:8]}",
                                claim_type=ClaimType.CONFIG_PARAMETER,
                                source_kind=SourceKind.CONTAINER,
                                algorithm=algo,
                                purpose=purpose,
                                relative_path=relative_path,
                                start_line=line_num,
                                end_line=line_num,
                                evidence_digest=digest,
                                sanitized_excerpt=excerpt,
                                detector_id=self.DETECTOR_ID,
                                ruleset_version=RULESET_VERSION,
                                confidence=ConfidenceBand.HIGH,
                                confidence_rationale=f"Container crypto environment configuration '{env_var}' set",
                                state=EvidenceState.DECLARED,
                                raw_parameters={"env_var": env_var},
                            )
                        )

        return observations

    def _analyze_oci_manifest(
        self,
        file_path: Path,
        relative_path: str,
        scan_id: str,
    ) -> List[Observation]:
        """Inspect OCI / Docker manifest JSON for image identity and cryptographic layers."""
        observations: List[Observation] = []
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                content = json.load(f)
        except Exception:
            return []

        manifest_entries = content if isinstance(content, list) else [content]

        for idx, entry in enumerate(manifest_entries):
            if not isinstance(entry, dict):
                continue

            # 1. Base image / RepoTag detection
            base_image = (
                entry.get("annotations", {}).get("org.opencontainers.image.base.name")
                or (entry.get("RepoTags", [None])[0] if entry.get("RepoTags") else None)
                or entry.get("config", {}).get("mediaType")
            )
            if base_image:
                obs_id = str(uuid.uuid4())
                excerpt = f"OCI Image Identity / Base: {base_image}"
                observations.append(
                    Observation(
                        observation_id=obs_id,
                        scan_id=scan_id,
                        candidate_asset_id=f"container:oci:base:{hashlib.sha256(str(base_image).encode()).hexdigest()[:10]}",
                        claim_type=ClaimType.CONTAINER_PACKAGE,
                        source_kind=SourceKind.CONTAINER,
                        algorithm=f"CONTAINER_BASE:{base_image}",
                        purpose="BASE_OPERATING_SYSTEM_CRYPTO",
                        relative_path=relative_path,
                        start_line=1,
                        end_line=1,
                        evidence_digest=hashlib.sha256(excerpt.encode()).hexdigest(),
                        sanitized_excerpt=excerpt,
                        detector_id=self.DETECTOR_ID,
                        ruleset_version=RULESET_VERSION,
                        confidence=ConfidenceBand.HIGH,
                        confidence_rationale="Extracted base image / tag from OCI container manifest",
                        state=EvidenceState.DECLARED,
                        raw_parameters={"oci_base": base_image},
                    )
                )

            # 2. Inspect Layers
            layers = entry.get("layers", []) or entry.get("Layers", [])
            for layer_idx, layer in enumerate(layers):
                layer_desc = layer if isinstance(layer, str) else layer.get("digest", str(layer))
                for pkg_name, (algo, purpose, conf) in CONTAINER_CRYPTO_PACKAGES.items():
                    if pkg_name.lower() in layer_desc.lower():
                        obs_id = str(uuid.uuid4())
                        excerpt = f"OCI Layer {layer_idx}: {layer_desc}"
                        observations.append(
                            Observation(
                                observation_id=obs_id,
                                scan_id=scan_id,
                                candidate_asset_id=f"container:oci:layer:{pkg_name}:{hashlib.sha256(layer_desc.encode()).hexdigest()[:8]}",
                                claim_type=ClaimType.CONTAINER_PACKAGE,
                                source_kind=SourceKind.CONTAINER,
                                algorithm=algo,
                                purpose=purpose,
                                relative_path=relative_path,
                                start_line=1,
                                end_line=1,
                                evidence_digest=hashlib.sha256(excerpt.encode()).hexdigest(),
                                sanitized_excerpt=excerpt,
                                detector_id=self.DETECTOR_ID,
                                ruleset_version=RULESET_VERSION,
                                confidence=conf,
                                confidence_rationale=f"OCI container layer references cryptographic module '{pkg_name}'",
                                state=EvidenceState.DECLARED,
                                raw_parameters={"layer_index": layer_idx, "package": pkg_name},
                            )
                        )

        return observations

    def _analyze_tar_layer(
        self,
        file_path: Path,
        relative_path: str,
        scan_id: str,
    ) -> List[Observation]:
        """Inspect contents of an OCI container layer archive for system cryptographic libraries."""
        observations: List[Observation] = []
        if not tarfile.is_tarfile(file_path):
            return []

        try:
            with tarfile.open(file_path, "r") as tf:
                members = tf.getnames()
        except Exception:
            return []

        seen_pkgs = set()
        for member_name in members:
            norm_name = member_name.lower().replace("\\", "/")
            for pkg_key, (algo, purpose, conf) in CONTAINER_CRYPTO_PACKAGES.items():
                if pkg_key in seen_pkgs:
                    continue
                # Match package name or library name (e.g. libssl, wolfssl, openssl, liboqs)
                base_pkg = pkg_key.removeprefix("lib").removesuffix("-dev").removesuffix("-bin").removesuffix("3").removesuffix("1.1")
                if pkg_key in norm_name or (len(base_pkg) >= 3 and base_pkg in norm_name):
                    seen_pkgs.add(pkg_key)
                    excerpt = f"Discovered in OCI layer archive: {member_name}"
                    observations.append(
                        Observation(
                            observation_id=str(uuid.uuid4()),
                            scan_id=scan_id,
                            candidate_asset_id=f"container:layer:binary:{pkg_key}:{hashlib.sha256(member_name.encode()).hexdigest()[:8]}",
                            claim_type=ClaimType.CONTAINER_PACKAGE,
                            source_kind=SourceKind.CONTAINER,
                            algorithm=algo,
                            purpose=purpose,
                            relative_path=relative_path,
                            start_line=1,
                            end_line=1,
                            evidence_digest=hashlib.sha256(excerpt.encode()).hexdigest(),
                            sanitized_excerpt=excerpt,
                            detector_id=self.DETECTOR_ID,
                            ruleset_version=RULESET_VERSION,
                            confidence=ConfidenceBand.CONFIRMED,
                            confidence_rationale=f"Cryptographic library path discovered inside OCI layer archive: {member_name}",
                            state=EvidenceState.OBSERVED,
                            raw_parameters={"member_path": member_name, "package": pkg_key},
                        )
                    )

        return observations
