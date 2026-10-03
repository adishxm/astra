"""ASTRA - Dependency & Manifest Cryptographic Detector (Worker 01 - MVP-02).

Detects cryptographic library dependencies in package.json, pom.xml,
requirements.txt, pyproject.toml, go.mod, and Cargo.toml.
"""

import hashlib
import json
import re
import uuid
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Optional

from app.core.config import RULESET_VERSION
from app.discovery.models import (
    ClaimType,
    ConfidenceBand,
    EvidenceState,
    Observation,
    SourceKind,
)

# Known cryptographic packages and their characteristics
CRYPTO_PACKAGES = [
    # Python
    ("cryptography", "Python standard modern cryptographic library", "HYBRID"),
    ("pycryptodome", "Self-contained cryptographic primitives library", "CLASSICAL"),
    ("pycrypto", "Legacy deprecated Python cryptographic toolkit", "VULNERABLE"),
    ("rsa", "Pure-Python RSA implementation", "QUANTUM_VULNERABLE"),
    ("ecdsa", "Pure-Python ECDSA implementation", "QUANTUM_VULNERABLE"),
    ("pynacl", "Python binding to libsodium", "CLASSICAL"),
    ("liboqs-python", "Open Quantum Safe Python bindings for PQC algorithms", "POST_QUANTUM"),
    ("pqcrypto", "Post-quantum cryptography library", "POST_QUANTUM"),

    # Java / Maven
    ("bcprov", "Bouncy Castle Provider", "HYBRID"),
    ("bcpqc", "Bouncy Castle Post-Quantum Provider", "POST_QUANTUM"),
    ("bouncycastle", "Bouncy Castle Cryptography APIs", "HYBRID"),
    ("tink", "Google Tink Cryptographic Library", "CLASSICAL"),
    ("commons-crypto", "Apache Commons Crypto", "CLASSICAL"),

    # Node.js
    ("crypto-js", "JavaScript library of crypto standards", "CLASSICAL"),
    ("node-forge", "Native implementation of TLS and cryptographic tools", "CLASSICAL"),
    ("tweetnacl", "Port of TweetNaCl cryptographic library", "CLASSICAL"),
    ("libsodium-wrappers", "Libsodium cryptographic library for JS", "CLASSICAL"),

    # Go
    ("golang.org/x/crypto", "Go supplementary cryptographic libraries", "CLASSICAL"),
    ("github.com/cloudflare/circl", "Cloudflare Interoperable Reusable Cryptographic Library (PQC)", "POST_QUANTUM"),
    ("github.com/open-quantum-safe/liboqs-go", "OQS Go bindings for PQC algorithms", "POST_QUANTUM"),

    # Rust
    ("ring", "Safe, fast, small crypto using Rust", "CLASSICAL"),
    ("aes-gcm", "Pure Rust implementation of AES-GCM", "CLASSICAL"),
    ("ed25519-dalek", "Fast and efficient Rust implementation of Ed25519", "QUANTUM_VULNERABLE"),
    ("rsa", "Pure Rust RSA implementation", "QUANTUM_VULNERABLE"),
    ("pqcrypto", "Post-Quantum Cryptography for Rust", "POST_QUANTUM"),
]


class ManifestCryptoDetector:
    """Discovers cryptographic libraries in dependency manifests."""

    DETECTOR_ID = "detector-manifest-v1"

    MANIFEST_FILENAMES = {
        "package.json", "pom.xml", "requirements.txt",
        "pyproject.toml", "go.mod", "Cargo.toml",
    }

    def can_analyze(self, file_path: Path) -> bool:
        return file_path.name in self.MANIFEST_FILENAMES

    def analyze_file(
        self,
        file_path: Path,
        relative_path: str,
        scan_id: str,
    ) -> List[Observation]:
        """Parse dependency manifest and identify cryptographic packages."""
        observations: List[Observation] = []
        name = file_path.name

        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
        except OSError:
            return []

        full_content = "".join(lines)

        # 1. package.json parser
        if name == "package.json":
            try:
                pkg_data = json.loads(full_content)
                deps = {}
                deps.update(pkg_data.get("dependencies", {}))
                deps.update(pkg_data.get("devDependencies", {}))

                for dep_name, version in deps.items():
                    for match_name, desc, q_status in CRYPTO_PACKAGES:
                        if match_name.lower() in dep_name.lower():
                            excerpt = f'"{dep_name}": "{version}"'
                            observations.append(
                                Observation(
                                    observation_id=str(uuid.uuid4()),
                                    scan_id=scan_id,
                                    candidate_asset_id=f"manifest-{dep_name.lower()}-{relative_path}",
                                    claim_type=ClaimType.DEPENDENCY_REFERENCE,
                                    source_kind=SourceKind.MANIFEST,
                                    algorithm=dep_name,
                                    purpose="CRYPTOGRAPHIC_LIBRARY",
                                    relative_path=relative_path,
                                    evidence_digest=hashlib.sha256(excerpt.encode()).hexdigest(),
                                    sanitized_excerpt=excerpt,
                                    detector_id=self.DETECTOR_ID,
                                    ruleset_version=RULESET_VERSION,
                                    confidence=ConfidenceBand.CONFIRMED,
                                    confidence_rationale=f"Package manifest declaration: {dep_name} in package.json ({desc}) — declared dependency capability, distinct from confirmed source-level invocation",
                                    state=EvidenceState.DECLARED,
                                    raw_parameters={"version": version, "quantum_status": q_status},
                                )
                            )
            except json.JSONDecodeError:
                pass

        # 2. pom.xml parser
        elif name == "pom.xml":
            try:
                root = ET.fromstring(full_content)
                # Remove XML namespaces for simple tag querying
                for elem in root.iter():
                    if "}" in elem.tag:
                        elem.tag = elem.tag.split("}", 1)[1]

                for dep in root.findall(".//dependency"):
                    artifact_id_elem = dep.find("artifactId")
                    group_id_elem = dep.find("groupId")
                    version_elem = dep.find("version")

                    artifact_id = artifact_id_elem.text if artifact_id_elem is not None else ""
                    group_id = group_id_elem.text if group_id_elem is not None else ""
                    version = version_elem.text if version_elem is not None else "unknown"

                    for match_name, desc, q_status in CRYPTO_PACKAGES:
                        if match_name.lower() in artifact_id.lower() or match_name.lower() in group_id.lower():
                            excerpt = f"<dependency><groupId>{group_id}</groupId><artifactId>{artifact_id}</artifactId></dependency>"
                            observations.append(
                                Observation(
                                    observation_id=str(uuid.uuid4()),
                                    scan_id=scan_id,
                                    candidate_asset_id=f"pom-{artifact_id.lower()}-{relative_path}",
                                    claim_type=ClaimType.DEPENDENCY_REFERENCE,
                                    source_kind=SourceKind.MANIFEST,
                                    algorithm=artifact_id,
                                    purpose="CRYPTOGRAPHIC_LIBRARY",
                                    relative_path=relative_path,
                                    evidence_digest=hashlib.sha256(excerpt.encode()).hexdigest(),
                                    sanitized_excerpt=excerpt,
                                    detector_id=self.DETECTOR_ID,
                                    ruleset_version=RULESET_VERSION,
                                    confidence=ConfidenceBand.CONFIRMED,
                                    confidence_rationale=f"Maven pom.xml dependency: {desc} — declared dependency capability, distinct from confirmed source-level invocation",
                                    state=EvidenceState.DECLARED,
                                    raw_parameters={"group_id": group_id, "version": version, "quantum_status": q_status},
                                )
                            )
            except ET.ParseError:
                pass

        # 3. Line-based manifests: requirements.txt, go.mod, Cargo.toml, pyproject.toml
        for idx, line in enumerate(lines, start=1):
            line_str = line.strip()
            if not line_str or line_str.startswith("#"):
                continue

            for match_name, desc, q_status in CRYPTO_PACKAGES:
                # Regex boundary for package name in manifest line
                if re.search(rf"\b{re.escape(match_name)}\b", line_str, re.IGNORECASE):
                    # Check if already added in pom or json
                    if any(o.relative_path == relative_path and o.start_line == idx for o in observations):
                        continue

                    excerpt = line_str[:200]
                    observations.append(
                        Observation(
                            observation_id=str(uuid.uuid4()),
                            scan_id=scan_id,
                            candidate_asset_id=f"manifest-{match_name.lower()}-{relative_path}-{idx}",
                            claim_type=ClaimType.DEPENDENCY_REFERENCE,
                            source_kind=SourceKind.MANIFEST,
                            algorithm=match_name,
                            purpose="CRYPTOGRAPHIC_LIBRARY",
                            relative_path=relative_path,
                            start_line=idx,
                            end_line=idx,
                            evidence_digest=hashlib.sha256(excerpt.encode()).hexdigest(),
                            sanitized_excerpt=excerpt,
                            detector_id=self.DETECTOR_ID,
                            ruleset_version=RULESET_VERSION,
                            confidence=ConfidenceBand.HIGH,
                            confidence_rationale=f"Declared dependency manifest reference: {match_name} in {name} ({desc}) — potential capability, distinct from confirmed source invocation",
                            state=EvidenceState.DECLARED,
                            raw_parameters={"quantum_status": q_status},
                        )
                    )

        return observations
