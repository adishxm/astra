"""ASTRA - PKCS#11 & Hardware Security Module (HSM) Cryptographic Detector (Worker 04 - Phase C).

Discovers Hardware Security Module (HSM) configurations, PKCS#11 mechanism bindings,
cryptoki slot definitions, and hardware token profiles (e.g. SoftHSM2, OpenSC, Utimaco,
Thales Luna, Nitrokey, YubiKey HSM).
"""

import hashlib
import json
import re
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from app.core.config import RULESET_VERSION
from app.discovery.models import (
    ClaimType,
    ConfidenceBand,
    EvidenceState,
    Observation,
    SourceKind,
)


class Pkcs11HsmDetector:
    """Discovers PKCS#11 Cryptoki hardware mechanisms and token profiles in system configurations."""

    DETECTOR_ID = "detector-pkcs11-hsm-v1"

    SUPPORTED_EXTENSIONS = {
        ".conf", ".cfg", ".ini", ".json", ".properties", ".yaml", ".yml", ".xml"
    }

    # PKCS#11 Mechanism Signatures
    PKCS11_MECHANISMS = [
        (r"(?i)\bCKM_RSA_PKCS_KEY_PAIR_GEN\b", "RSA", "KEY_GENERATION", 2048, None, "PKCS#11 hardware RSA key pair generation mechanism"),
        (r"(?i)\bCKM_RSA_PKCS_PSS\b", "RSA-PSS", "SIGNATURE", 2048, None, "PKCS#11 hardware RSA-PSS signing mechanism"),
        (r"(?i)\bCKM_RSA_PKCS\b", "RSA", "ASYMMETRIC", 2048, None, "PKCS#11 hardware RSA PKCS#1 v1.5 mechanism"),
        (r"(?i)\bCKM_RSA_X_509\b", "RSA", "ASYMMETRIC", 2048, None, "PKCS#11 raw RSA operation mechanism"),
        (r"(?i)\bCKM_EC_KEY_PAIR_GEN\b", "ECDSA", "KEY_GENERATION", 256, "P-256", "PKCS#11 hardware Elliptic Curve key pair generation mechanism"),
        (r"(?i)\bCKM_ECDSA\b", "ECDSA", "SIGNATURE", 256, "P-256", "PKCS#11 hardware ECDSA signing mechanism"),
        (r"(?i)\bCKM_ECDH1_DERIVE\b", "ECDH", "KEY_EXCHANGE", 256, "P-256", "PKCS#11 hardware ECDH key derivation mechanism"),
        (r"(?i)\bCKM_AES_KEY_GEN\b", "AES", "KEY_GENERATION", 256, None, "PKCS#11 hardware AES symmetric key generation mechanism"),
        (r"(?i)\bCKM_AES_GCM\b", "AES-GCM", "SYMMETRIC_ENCRYPTION", 256, None, "PKCS#11 hardware AES-GCM encryption mechanism"),
        (r"(?i)\bCKM_AES_CBC\b", "AES-CBC", "SYMMETRIC_ENCRYPTION", 256, None, "PKCS#11 hardware AES-CBC encryption mechanism"),
        (r"(?i)\bCKM_AES_CTR\b", "AES-CTR", "SYMMETRIC_ENCRYPTION", 256, None, "PKCS#11 hardware AES-CTR encryption mechanism"),
        (r"(?i)\bCKM_SHA256\b", "SHA-256", "HASH", 256, None, "PKCS#11 hardware SHA-256 digest mechanism"),
        (r"(?i)\bCKM_SHA384\b", "SHA-384", "HASH", 384, None, "PKCS#11 hardware SHA-384 digest mechanism"),
        (r"(?i)\bCKM_SHA512\b", "SHA-512", "HASH", 512, None, "PKCS#11 hardware SHA-512 digest mechanism"),
    ]

    # Hardware Token & Module Identifiers
    HSM_MODULE_SIGNATURES = [
        (r"(?i)\b(softhsm2?\.dll|libsofthsm2?\.so)\b", "SoftHSM2-PKCS11", "SoftHSM2 software/token cryptographic provider"),
        (r"(?i)\b(opensc-pkcs11\.so|opensc-pkcs11\.dll)\b", "OpenSC-PKCS11", "OpenSC SmartCard / HSM middleware provider"),
        (r"(?i)\b(libCryptoki2_64\.so|Chrystoki\.conf)\b", "Luna-HSM-PKCS11", "Thales / Gemalto SafeNet Luna HSM provider"),
        (r"(?i)\b(libcs_pkcs11_R3\.so|cs_pkcs11\.dll)\b", "Utimaco-HSM-PKCS11", "Utimaco CryptoServer HSM provider"),
    ]

    # Security Token Flags
    SECURITY_FLAGS = [
        (r"(?i)\bCKF_LOGIN_REQUIRED\b", "CKF_LOGIN_REQUIRED", "HSM requires PIN/credentials authentication before access"),
        (r"(?i)\bCKF_USER_PIN_INITIALIZED\b", "CKF_USER_PIN_INITIALIZED", "HSM user security PIN is securely initialized"),
        (r"(?i)\bCKF_PROTECTED_AUTHENTICATION_PATH\b", "CKF_PROTECTED_AUTHENTICATION_PATH", "HSM enforces hardware-protected entry path (PIN pad)"),
    ]

    def can_analyze(self, file_path: Path) -> bool:
        """Evaluate if file is a PKCS#11 configuration or HSM definition."""
        name_lower = file_path.name.lower()
        if any(keyword in name_lower for keyword in ["pkcs11", "softhsm", "opensc", "hsm", "cryptoki", "chrystoki", "nitrokey", "yubikey"]):
            return True
        return file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS

    def analyze_file(
        self,
        file_path: Path,
        relative_path: str,
        scan_id: str,
    ) -> List[Observation]:
        """Scan file for PKCS#11 cryptographic mechanisms, HSM providers, and token profiles."""
        observations: List[Observation] = []

        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
        except OSError:
            return []

        # Track contextual token flags and slot metadata across lines
        token_flags: List[str] = []
        token_label: Optional[str] = None
        module_name: Optional[str] = None

        for idx, line in enumerate(lines, start=1):
            line_str = line.strip()
            if not line_str or line_str.startswith(("#", ";", "//")):
                continue

            # Check for token labels and modules
            label_match = re.search(r"(?i)\b(?:label|token_label|slot_label)[\s:=]+['\"]?([^'\"\r\n,]+)['\"]?", line_str)
            if label_match:
                token_label = label_match.group(1).strip()

            for mod_pattern, mod_id, mod_desc in self.HSM_MODULE_SIGNATURES:
                if re.search(mod_pattern, line_str):
                    module_name = mod_id

            for flag_pattern, flag_name, flag_desc in self.SECURITY_FLAGS:
                if re.search(flag_pattern, line_str):
                    if flag_name not in token_flags:
                        token_flags.append(flag_name)

            # Check for PKCS#11 Cryptographic Mechanisms
            for pattern, algo, purpose, ksize, curve, rationale in self.PKCS11_MECHANISMS:
                if re.search(pattern, line_str):
                    excerpt = line_str[:200]
                    obs = self._create_observation(
                        scan_id=scan_id,
                        relative_path=relative_path,
                        line_num=idx,
                        algorithm=algo,
                        purpose=purpose,
                        key_size=ksize,
                        curve=curve,
                        excerpt=excerpt,
                        module=module_name or "PKCS#11 Provider",
                        token_label=token_label or "Default Token Slot",
                        token_flags=list(token_flags),
                        rationale=rationale,
                    )
                    observations.append(obs)

        return observations

    def _create_observation(
        self,
        scan_id: str,
        relative_path: str,
        line_num: int,
        algorithm: str,
        purpose: str,
        key_size: Optional[int],
        curve: Optional[str],
        excerpt: str,
        module: str,
        token_label: str,
        token_flags: List[str],
        rationale: str,
    ) -> Observation:
        """Helper to create standardized PKCS#11 HSM Observation."""
        digest = hashlib.sha256(excerpt.encode("utf-8")).hexdigest()
        asset_id = f"hsm-pkcs11-{algorithm.lower()}-{relative_path}-{line_num}"

        return Observation(
            observation_id=str(uuid.uuid4()),
            scan_id=scan_id,
            candidate_asset_id=asset_id,
            claim_type=ClaimType.KEY_SPECIFICATION,
            source_kind=SourceKind.CONFIG,
            algorithm=algorithm,
            purpose=purpose,
            key_size_bits=key_size,
            curve_name=curve,
            relative_path=relative_path,
            start_line=line_num,
            end_line=line_num,
            evidence_digest=digest,
            sanitized_excerpt=excerpt,
            detector_id=self.DETECTOR_ID,
            ruleset_version=RULESET_VERSION,
            confidence=ConfidenceBand.CONFIRMED,
            confidence_rationale=rationale,
            state=EvidenceState.DECLARED,
            raw_parameters={
                "hardware_standard": "PKCS#11",
                "hsm_module": module,
                "token_label": token_label,
                "security_flags": token_flags,
                "infrastructure_type": "HARDWARE_SECURITY_MODULE",
            },
        )
