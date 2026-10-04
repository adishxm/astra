"""ASTRA - Configuration Cryptographic Detector (Worker 01 - MVP-02).

Detects TLS protocols, cipher suite specifications, SSH key exchange configurations,
and cryptographic parameters in YAML, Conf, INI, and Properties files.
"""

import hashlib
import re
import uuid
from pathlib import Path
from typing import List

from app.core.config import RULESET_VERSION
from app.discovery.models import (
    ClaimType,
    ConfidenceBand,
    EvidenceState,
    Observation,
    SourceKind,
)

CONFIG_SIGNATURES = [
    # TLS Protocols
    (r"(?i)\b(TLSv1\.3|TLS 1\.3)\b", "TLSv1.3", "PROTOCOL", "CLASSICAL", ConfidenceBand.CONFIRMED),
    (r"(?i)\b(TLSv1\.2|TLS 1\.2)\b", "TLSv1.2", "PROTOCOL", "CLASSICAL", ConfidenceBand.CONFIRMED),
    (r"(?i)\b(TLSv1\.1|TLS 1\.1)\b", "TLSv1.1", "PROTOCOL", "DEPRECATED", ConfidenceBand.CONFIRMED),
    (r"(?i)\b(TLSv1\.0|TLS 1\.0|TLSv1(?!\.))\b", "TLSv1.0", "PROTOCOL", "DEPRECATED", ConfidenceBand.CONFIRMED),
    (r"(?i)\b(SSLv3|SSL 3\.0)\b", "SSLv3", "PROTOCOL", "VULNERABLE", ConfidenceBand.CONFIRMED),
    (r"(?i)\b(SSLv2|SSL 2\.0)\b", "SSLv2", "PROTOCOL", "VULNERABLE", ConfidenceBand.CONFIRMED),

    # Cipher Suites & Key Exchanges
    (r"(?i)\b(ECDHE-RSA-AES256-GCM-SHA384|ECDHE-ECDSA-AES256-GCM-SHA384)\b", "ECDHE-AES256-GCM", "CIPHER_SUITE", "QUANTUM_VULNERABLE", ConfidenceBand.CONFIRMED),
    (r"(?i)\b(ECDHE-RSA-AES128-GCM-SHA256|ECDHE-ECDSA-AES128-GCM-SHA256)\b", "ECDHE-AES128-GCM", "CIPHER_SUITE", "QUANTUM_VULNERABLE", ConfidenceBand.CONFIRMED),
    (r"(?i)\b(DHE-RSA-AES256-GCM-SHA384|DHE-RSA-AES128-GCM-SHA256)\b", "DHE-AES-GCM", "CIPHER_SUITE", "QUANTUM_VULNERABLE", ConfidenceBand.CONFIRMED),
    (r"(?i)\b(RC4-SHA|RC4-MD5|DES-CBC3-SHA)\b", "LEGACY_CIPHER", "CIPHER_SUITE", "VULNERABLE", ConfidenceBand.CONFIRMED),

    # Post-Quantum & Hybrid SSH / TLS Key Exchanges
    (r"(?i)\b(sntrup761x25519-sha512@openssh\.com|mlkem768x25519)\b", "Hybrid-PQC-KEX", "KEY_EXCHANGE", "POST_QUANTUM", ConfidenceBand.CONFIRMED),
    (r"(?i)\b(curve25519-sha256|diffie-hellman-group14-sha256)\b", "Classical-SSH-KEX", "KEY_EXCHANGE", "QUANTUM_VULNERABLE", ConfidenceBand.CONFIRMED),
    
    # Generic Cryptographic Configuration Parameters
    (r"(?i)\b(?:algorithm|cipher|encryption|hash)[_\w]*[\s:=]+['\"]?DES['\"]?\b", "DES", "ALGORITHM_DECLARATION", "VULNERABLE", ConfidenceBand.HIGH),
    (r"(?i)\b(?:algorithm|cipher|encryption|hash)[_\w]*[\s:=]+['\"]?(?:3DES|DES3)['\"]?\b", "3DES", "ALGORITHM_DECLARATION", "VULNERABLE", ConfidenceBand.HIGH),
    (r"(?i)\b(?:algorithm|cipher|encryption|hash)[_\w]*[\s:=]+['\"]?AES['\"]?\b", "AES", "ALGORITHM_DECLARATION", "CLASSICAL", ConfidenceBand.HIGH),
    (r"(?i)\b(?:algorithm|cipher|encryption|hash)[_\w]*[\s:=]+['\"]?RSA['\"]?\b", "RSA", "ALGORITHM_DECLARATION", "QUANTUM_VULNERABLE", ConfidenceBand.HIGH),
    (r"(?i)\b(?:algorithm|cipher|encryption|hash)[_\w]*[\s:=]+['\"]?MD5['\"]?\b", "MD5", "ALGORITHM_DECLARATION", "VULNERABLE", ConfidenceBand.HIGH),
    (r"(?i)\b(?:algorithm|cipher|encryption|hash)[_\w]*[\s:=]+['\"]?SHA-?1['\"]?\b", "SHA-1", "ALGORITHM_DECLARATION", "VULNERABLE", ConfidenceBand.HIGH),
]


class ConfigCryptoDetector:
    """Discovers cryptographic configurations in server, web, and infrastructure configs."""

    DETECTOR_ID = "detector-config-v1"

    SUPPORTED_EXTENSIONS = {
        ".yaml", ".yml", ".conf", ".cnf", ".ini", ".properties", ".toml", ".env"
    }

    def can_analyze(self, file_path: Path) -> bool:
        return file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS

    def analyze_file(
        self,
        file_path: Path,
        relative_path: str,
        scan_id: str,
    ) -> List[Observation]:
        """Scan configuration file for TLS, cipher, and crypto settings."""
        observations: List[Observation] = []

        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
        except OSError:
            return []

        for idx, line in enumerate(lines, start=1):
            line_str = line.strip()
            if not line_str or line_str.startswith(("#", ";")):
                continue

            for pattern, name, purpose, q_status, conf in CONFIG_SIGNATURES:
                if re.search(pattern, line_str):
                    excerpt = line_str[:200]
                    digest = hashlib.sha256(excerpt.encode()).hexdigest()

                    observations.append(
                        Observation(
                            observation_id=str(uuid.uuid4()),
                            scan_id=scan_id,
                            candidate_asset_id=f"config-{name.lower()}-{relative_path}-{idx}",
                            claim_type=ClaimType.CONFIG_PARAMETER,
                            source_kind=SourceKind.CONFIG,
                            algorithm=name,
                            purpose=purpose,
                            relative_path=relative_path,
                            start_line=idx,
                            end_line=idx,
                            evidence_digest=digest,
                            sanitized_excerpt=excerpt,
                            detector_id=self.DETECTOR_ID,
                            ruleset_version=RULESET_VERSION,
                            confidence=conf,
                            confidence_rationale=f"Found cryptographic configuration setting for {name}",
                            state=EvidenceState.DECLARED,
                            raw_parameters={"quantum_status": q_status},
                        )
                    )

        return observations
