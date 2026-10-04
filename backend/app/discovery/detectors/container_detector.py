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
    "libssl": ("OpenSSL", "SYSTEM_CRYPTO_SUITE", ConfidenceBand.CONFIRMED),
    "libcrypto": ("OpenSSL-libcrypto", "SYSTEM_CRYPTO_SUITE", ConfidenceBand.CONFIRMED),
    "gnutls-bin": ("GnuTLS", "SYSTEM_CRYPTO_SUITE", ConfidenceBand.HIGH),
    "libgnutls30": ("GnuTLS", "SYSTEM_CRYPTO_SUITE", ConfidenceBand.HIGH),
    "libgnutls": ("GnuTLS", "SYSTEM_CRYPTO_SUITE", ConfidenceBand.CONFIRMED),
    "wolfssl": ("WolfSSL", "EMBEDDED_CRYPTO_SUITE", ConfidenceBand.HIGH),
    "libwolfssl": ("WolfSSL", "EMBEDDED_CRYPTO_SUITE", ConfidenceBand.CONFIRMED),
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
    MAX_BLOB_SIZE_BYTES = 100 * 1024 * 1024  # 100 MB
    MAX_DECOMPRESSED_LAYER_BYTES = 250 * 1024 * 1024  # 250 MB
    MAX_LAYER_ENTRIES = 50000

    def __init__(self):
        self._processed_blob_hashes = set()

    @staticmethod
    def _is_gzip(file_path: Path) -> bool:
        """Check if file has gzip magic bytes (\x1f\x8b)."""
        try:
            with open(file_path, "rb") as f:
                return f.read(2) == b"\x1f\x8b"
        except Exception:
            return False

    def _open_tar_safely(self, file_path: Path):
        """Safely open an uncompressed or gzip tar archive."""
        if self._is_gzip(file_path):
            try:
                return tarfile.open(file_path, "r:gz")
            except Exception:
                return None
        elif tarfile.is_tarfile(file_path):
            try:
                return tarfile.open(file_path, "r:*")
            except Exception:
                return None
        return None

    def can_analyze(self, file_path: Path) -> bool:
        """Check if file is a Dockerfile, Containerfile, OCI layer archive, or container manifest."""
        name = file_path.name.lower()
        if name in {"dockerfile", "containerfile"} or name.startswith("dockerfile.") or name.startswith("containerfile."):
            return True
        if name in {"manifest.json", "layer.json", "index.json", "oci-layout"}:
            return True
        if name.endswith(".tar") or name.endswith(".tar.gz") or name.endswith(".tgz"):
            return True
        if "blobs" in file_path.parts and "sha256" in file_path.parts:
            return True
        return False

    def analyze_file(
        self,
        file_path: Path,
        relative_path: str,
        scan_id: str,
    ) -> List[Observation]:
        """Analyze container definitions, OCI manifests, layouts, and layer archives."""
        name = file_path.name.lower()

        # 1. OCI Image Layout Root (index.json or oci-layout)
        if name in {"index.json", "oci-layout"}:
            parent = file_path.parent
            if (parent / "blobs" / "sha256").is_dir() or (parent / "index.json").is_file():
                return self._analyze_oci_layout(parent, relative_path, scan_id)
            return self._analyze_oci_manifest(file_path, relative_path, scan_id)

        # 2. Content-Addressed Blob in blobs/sha256/<hash>
        if "blobs" in file_path.parts and "sha256" in file_path.parts:
            return self._analyze_content_addressed_blob(file_path, relative_path, scan_id)

        # 3. Layer Archive (.tar, .tar.gz, .tgz)
        if name.endswith(".tar") or name.endswith(".tar.gz") or name.endswith(".tgz"):
            return self._analyze_tar_layer(file_path, relative_path, scan_id)

        # 4. Standalone Manifest or Layer Descriptor
        if name in {"manifest.json", "layer.json"}:
            return self._analyze_oci_manifest(file_path, relative_path, scan_id)

        # 5. Dockerfile / Containerfile
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
        return self._inspect_layer_archive(file_path, relative_path, scan_id)

    def _analyze_oci_layout(
        self,
        layout_root: Path,
        relative_path: str,
        scan_id: str,
    ) -> List[Observation]:
        """Parse standard OCI Image Layout (index.json -> manifest blob -> layer tar+gzip blobs)."""
        observations: List[Observation] = []
        index_file = layout_root / "index.json"
        if not index_file.is_file():
            return []

        try:
            with open(index_file, "r", encoding="utf-8", errors="replace") as f:
                index_data = json.load(f)
        except Exception:
            return []

        blobs_dir = layout_root / "blobs" / "sha256"
        manifests = index_data.get("manifests", [])
        if not isinstance(manifests, list):
            return []

        for m_desc in manifests:
            m_digest = m_desc.get("digest", "")
            m_hash = m_digest.split(":", 1)[-1] if ":" in m_digest else m_digest
            if not m_hash:
                continue

            manifest_blob = blobs_dir / m_hash
            if not manifest_blob.is_file():
                continue

            self._processed_blob_hashes.add(m_hash)

            try:
                with open(manifest_blob, "r", encoding="utf-8", errors="replace") as mf:
                    manifest_data = json.load(mf)
            except Exception:
                continue

            # Check config or annotations for image identity
            config_digest = manifest_data.get("config", {}).get("digest", "")
            if config_digest:
                self._processed_blob_hashes.add(config_digest.split(":", 1)[-1])

            # Inspect each layer descriptor
            layers = manifest_data.get("layers", [])
            for layer_idx, layer_desc in enumerate(layers):
                l_digest = layer_desc.get("digest", "")
                l_hash = l_digest.split(":", 1)[-1] if ":" in l_digest else l_digest
                if not l_hash:
                    continue

                layer_blob = blobs_dir / l_hash
                if not layer_blob.is_file():
                    continue

                self._processed_blob_hashes.add(l_hash)

                # Defense against hostile archive bombs: verify size and sha256
                try:
                    blob_size = layer_blob.stat().st_size
                    if blob_size > 100 * 1024 * 1024:  # 100 MB max layer size
                        continue

                    # Verify sha256 digest integrity
                    with open(layer_blob, "rb") as bf:
                        actual_digest = hashlib.sha256(bf.read()).hexdigest()
                    if actual_digest != l_hash:
                        continue
                except OSError:
                    continue

                # Inspect layer tarball (uncompressed or gzip)
                layer_rel = f"{relative_path}/blobs/sha256/{l_hash[:12]}"
                layer_obs = self._inspect_layer_archive(
                    layer_blob,
                    layer_rel,
                    scan_id,
                    layer_hash=l_hash,
                )
                observations.extend(layer_obs)

        return observations

    def _analyze_content_addressed_blob(
        self,
        file_path: Path,
        relative_path: str,
        scan_id: str,
    ) -> List[Observation]:
        """Analyze a standalone content-addressed blob from blobs/sha256/<hash>."""
        blob_hash = file_path.name
        if blob_hash in self._processed_blob_hashes:
            return []
        self._processed_blob_hashes.add(blob_hash)

        # Check if it's a JSON file (e.g. manifest or config)
        if not self._is_gzip(file_path) and not tarfile.is_tarfile(file_path):
            try:
                with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                    content = json.load(f)
                if isinstance(content, dict) and "schemaVersion" in content:
                    return self._analyze_oci_manifest(file_path, relative_path, scan_id)
            except Exception:
                pass
            return []

        # It's an archive layer
        return self._inspect_layer_archive(
            file_path,
            relative_path,
            scan_id,
            layer_hash=blob_hash,
        )

    def _inspect_layer_archive(
        self,
        file_path: Path,
        relative_path: str,
        scan_id: str,
        layer_hash: Optional[str] = None,
    ) -> List[Observation]:
        """Safely inspect an OCI layer archive (tar or gzip) under streaming limits."""
        observations: List[Observation] = []
        tf = self._open_tar_safely(file_path)
        if not tf:
            return []

        total_decompressed = 0
        seen_pkgs = set()

        try:
            for count, member in enumerate(tf):
                if count > self.MAX_LAYER_ENTRIES:
                    break
                total_decompressed += member.size
                if total_decompressed > self.MAX_DECOMPRESSED_LAYER_BYTES:
                    break
                # Directory traversal defense
                if ".." in member.name or member.name.startswith("/"):
                    continue

                norm_name = member.name.lower().replace("\\", "/")

                for pkg_key, (algo, purpose, conf) in CONTAINER_CRYPTO_PACKAGES.items():
                    if pkg_key in seen_pkgs:
                        continue

                    # Library or binary match
                    matched = False
                    if pkg_key in norm_name:
                        matched = True
                    elif pkg_key == "libssl" and ("libssl.so" in norm_name or "libssl3.so" in norm_name):
                        matched = True
                    elif pkg_key == "libcrypto" and "libcrypto.so" in norm_name:
                        matched = True
                    elif pkg_key == "libwolfssl" and "libwolfssl.so" in norm_name:
                        matched = True
                    elif pkg_key == "openssl" and ("/bin/openssl" in norm_name or "openssl.cnf" in norm_name):
                        matched = True
                    elif pkg_key == "ca-certificates" and ("ca-certificates.crt" in norm_name or "etc/ssl/certs" in norm_name):
                        matched = True

                    if matched:
                        seen_pkgs.add(pkg_key)
                        digest_tag = f"sha256:{layer_hash[:12]}" if layer_hash else "layer"
                        excerpt = f"Discovered in OCI layer ({digest_tag}): {member.name}"
                        observations.append(
                            Observation(
                                observation_id=str(uuid.uuid4()),
                                scan_id=scan_id,
                                candidate_asset_id=f"container:oci:layer:{pkg_key}:{hashlib.sha256(member.name.encode()).hexdigest()[:8]}",
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
                                confidence_rationale=f"Cryptographic system library path '{member.name}' confirmed inside OCI container layer",
                                state=EvidenceState.OBSERVED,
                                raw_parameters={
                                    "member_path": member.name,
                                    "package": pkg_key,
                                    "layer_digest": f"sha256:{layer_hash}" if layer_hash else "",
                                },
                            )
                        )
        except Exception:
            pass
        finally:
            try:
                tf.close()
            except Exception:
                pass

        return observations
