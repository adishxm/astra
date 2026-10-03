"""ASTRA - Container & Image Layer Cryptographic Detector (Worker 01 - PROD-01).

Inspects container definitions, Dockerfiles, OCI layer manifests, and service-mesh configurations.
Detects:
- Base images and their cryptographic baseline capabilities
- Cryptographic packages installed via package managers (apt, apk, yum, pip)
- Cryptographic environment variable configurations
- Embedded trust anchors and certificate bundle references
"""

import hashlib
import json
import re
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
        """Check if file is a Dockerfile, Containerfile, or container manifest."""
        name = file_path.name.lower()
        if name in {"dockerfile", "containerfile"} or name.startswith("dockerfile.") or name.startswith("containerfile."):
            return True
        if name in {"manifest.json", "layer.json"} and "oci" in str(file_path).lower():
            return True
        return False

    def analyze_file(
        self,
        file_path: Path,
        relative_path: str,
        scan_id: str,
    ) -> List[Observation]:
        """Analyze container definitions for cryptographic packages, base images, and trust anchors."""
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

        # 1. Inspect Dockerfile lines
        for line_num, line in enumerate(lines, start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue

            # Check FROM instruction (Base Image)
            if stripped.upper().startswith("FROM "):
                base_image = stripped.split()[1]
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
                    # Regex match package names in RUN command
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
