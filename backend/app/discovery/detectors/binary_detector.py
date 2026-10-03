"""ASTRA - Static Binary Cryptographic Detector (Worker 01 - PROD-01).

Performs bounded static-only binary inspection without ever executing untrusted files.
Detects:
- Executable formats (ELF, PE/COFF, Mach-O)
- Exported/imported cryptographic symbols (OpenSSL, Libsodium, Botan, WolfSSL, PQC)
- Standard cryptographic ASN.1 Object Identifiers (OIDs)
- Known cryptographic algorithm constants (SHA-256, MD5)
- Stripped vs unstripped symbol presence
"""

import hashlib
import os
import re
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from app.core.config import RULESET_VERSION
from app.discovery.models import (
    ClaimType,
    ConfidenceBand,
    EvidenceState,
    Observation,
    SourceKind,
)

# Known Binary Magics
MAGIC_ELF = b"\x7fELF"
MAGIC_PE = b"MZ"
MAGIC_MACHO = (b"\xfe\xed\xfa\xce", b"\xfe\xed\xfa\xcf", b"\xce\xfa\xed\xfe", b"\xcf\xfa\xed\xfe")

# Relevant binary extensions
BINARY_EXTENSIONS = {".so", ".dll", ".dylib", ".exe", ".bin", ".elf", ".o", ".a"}

# Cryptographic Symbol Mapping (Symbols -> (Algorithm, Purpose, Confidence))
CRYPTO_SYMBOLS: Dict[str, Tuple[str, str, ConfidenceBand]] = {
    # OpenSSL / BoringSSL
    "RSA_new": ("RSA", "ASYMMETRIC_KEYGEN", ConfidenceBand.HIGH),
    "RSA_generate_key_ex": ("RSA", "ASYMMETRIC_KEYGEN", ConfidenceBand.HIGH),
    "EVP_PKEY_new_raw_private_key": ("GENERIC_PKEY", "KEY_MANAGEMENT", ConfidenceBand.MEDIUM),
    "EC_KEY_new_by_curve_name": ("ECDSA", "ASYMMETRIC_KEYGEN", ConfidenceBand.HIGH),
    "AES_encrypt": ("AES", "SYMMETRIC_ENCRYPT", ConfidenceBand.HIGH),
    "AES_cbc_encrypt": ("AES-CBC", "SYMMETRIC_ENCRYPT", ConfidenceBand.HIGH),
    "AES_gcm_encrypt": ("AES-GCM", "AUTHENTICATED_ENCRYPT", ConfidenceBand.HIGH),
    "DES_set_key": ("DES", "SYMMETRIC_ENCRYPT", ConfidenceBand.CONFIRMED),
    "MD5_Init": ("MD5", "HASHING", ConfidenceBand.CONFIRMED),
    "SHA1_Init": ("SHA-1", "HASHING", ConfidenceBand.CONFIRMED),
    "SHA256_Init": ("SHA-256", "HASHING", ConfidenceBand.HIGH),
    "EVP_sha256": ("SHA-256", "HASHING", ConfidenceBand.HIGH),
    # Post-Quantum / Hybrid symbols (liboqs / pqclean)
    "OQS_KEM_ml_kem_768_new": ("ML-KEM-768", "PQC_KEM", ConfidenceBand.CONFIRMED),
    "OQS_SIG_ml_dsa_65_new": ("ML-DSA-65", "PQC_SIGNATURE", ConfidenceBand.CONFIRMED),
    "PQCLEAN_MLKEM768_CLEAN_crypto_kem_keypair": ("ML-KEM-768", "PQC_KEM", ConfidenceBand.CONFIRMED),
    "PQCLEAN_MLDSA65_CLEAN_crypto_sign_keypair": ("ML-DSA-65", "PQC_SIGNATURE", ConfidenceBand.CONFIRMED),
    "crypto_kem_kyber768_keypair": ("ML-KEM-768", "PQC_KEM", ConfidenceBand.HIGH),
    "crypto_sign_dilithium3_keypair": ("ML-DSA-65", "PQC_SIGNATURE", ConfidenceBand.HIGH),
    # Libsodium
    "crypto_box_curve25519xsalsa20poly1305": ("X25519-XSalsa20-Poly1305", "AUTHENTICATED_ENCRYPT", ConfidenceBand.HIGH),
    "crypto_sign_ed25519_keypair": ("Ed25519", "DIGITAL_SIGNATURE", ConfidenceBand.HIGH),
}

# ASN.1 Object Identifiers in binary format or byte representations
CRYPTO_OIDS: Dict[str, Tuple[str, str, ConfidenceBand]] = {
    "1.2.840.113549.1.1.1": ("RSA", "ASYMMETRIC_ENCRYPTION", ConfidenceBand.HIGH),
    "1.2.840.113549.1.1.5": ("RSA-SHA1", "DIGITAL_SIGNATURE", ConfidenceBand.CONFIRMED),
    "1.2.840.113549.1.1.11": ("RSA-SHA256", "DIGITAL_SIGNATURE", ConfidenceBand.HIGH),
    "1.2.840.10045.2.1": ("ECC", "ELLIPTIC_CURVE_PUBLIC_KEY", ConfidenceBand.HIGH),
    "1.2.840.10045.3.1.7": ("secp256r1", "ELLIPTIC_CURVE", ConfidenceBand.CONFIRMED),
    "1.3.101.112": ("Ed25519", "DIGITAL_SIGNATURE", ConfidenceBand.HIGH),
    "1.3.101.110": ("X25519", "KEY_EXCHANGE", ConfidenceBand.HIGH),
    "2.16.840.1.101.3.4.4.2": ("ML-KEM-768", "PQC_KEM", ConfidenceBand.CONFIRMED),
    "1.3.6.1.4.1.2.267.7.6.5": ("ML-DSA-65", "PQC_SIGNATURE", ConfidenceBand.CONFIRMED),
    "1.2.840.113549.2.5": ("MD5", "HASHING", ConfidenceBand.CONFIRMED),
    "1.3.14.3.2.26": ("SHA-1", "HASHING", ConfidenceBand.CONFIRMED),
}

# Cryptographic Constant Fingerprints (Little/Big-endian byte sequences)
CRYPTO_CONSTANTS: Dict[bytes, Tuple[str, str, str]] = {
    # SHA-256 initial constants H[0]=0x6a09e667, H[1]=0xbb67ae85
    b"\x67\xe6\x09\x6a\x85\xae\x67\xbb": ("SHA-256", "HASHING", "SHA-256 initial constants detected in static binary"),
    # MD5 initial constants A=0x67452301, B=0xefcdab89
    b"\x01\x23\x45\x67\x89\xab\xcd\xef": ("MD5", "HASHING", "MD5 initial constants detected in static binary"),
}


class BinaryCryptoDetector:
    """Safe, static-only binary cryptography analyzer conforming to Worker 01 PROD-01."""

    DETECTOR_ID = "binary_crypto_detector_static_v1"

    def can_analyze(self, file_path: Path) -> bool:
        """Check if file has binary extension or binary magic header."""
        if file_path.suffix.lower() in BINARY_EXTENSIONS:
            return True
        # Read header magic bytes
        try:
            with open(file_path, "rb") as f:
                header = f.read(4)
                if header.startswith(MAGIC_ELF) or header.startswith(MAGIC_PE) or header in MAGIC_MACHO:
                    return True
        except OSError:
            return False
        return False

    def analyze_file(
        self,
        file_path: Path,
        relative_path: str,
        scan_id: str,
    ) -> List[Observation]:
        """Analyze static binary content safely without process execution."""
        observations: List[Observation] = []

        try:
            with open(file_path, "rb") as f:
                # Read binary content up to 10 MB limit for safety
                raw_bytes = f.read(10 * 1024 * 1024)
        except OSError as e:
            return [
                Observation(
                    observation_id=str(uuid.uuid4()),
                    scan_id=scan_id,
                    candidate_asset_id=f"binary:unreadable:{hashlib.sha256(relative_path.encode()).hexdigest()[:12]}",
                    claim_type=ClaimType.BINARY_SYMBOL,
                    source_kind=SourceKind.BINARY,
                    relative_path=relative_path,
                    evidence_digest=hashlib.sha256(str(e).encode()).hexdigest(),
                    sanitized_excerpt=f"Error reading static binary: {e}",
                    detector_id=self.DETECTOR_ID,
                    ruleset_version=RULESET_VERSION,
                    confidence=ConfidenceBand.LOW,
                    confidence_rationale="Static binary read failure",
                    state=EvidenceState.FAILED,
                )
            ]

        # 1. Identify format and stripped status
        is_elf = raw_bytes.startswith(MAGIC_ELF)
        is_pe = raw_bytes.startswith(MAGIC_PE)
        is_macho = any(raw_bytes.startswith(m) for m in MAGIC_MACHO)
        format_name = "ELF" if is_elf else "PE" if is_pe else "Mach-O" if is_macho else "RAW_BINARY"

        # Check for symbol table presence in ELF/PE
        is_stripped = True
        if is_elf and b".symtab" in raw_bytes:
            is_stripped = False
        elif is_pe and b"Export Directory" in raw_bytes or b".edata" in raw_bytes:
            is_stripped = False

        # 2. Extract ASCII/UTF-8 strings from binary for symbol & OID matching
        extracted_strings = set(re.findall(rb"[A-Za-z0-9_.\-]{4,120}", raw_bytes))

        # Check for known symbols
        matched_symbols: Set[str] = set()
        for symbol_str, (algo, purpose, conf) in CRYPTO_SYMBOLS.items():
            sym_bytes = symbol_str.encode("utf-8")
            if sym_bytes in extracted_strings or sym_bytes in raw_bytes:
                matched_symbols.add(symbol_str)
                obs_id = str(uuid.uuid4())
                excerpt = f"Format: {format_name} | Stripped: {is_stripped} | Matched Symbol: {symbol_str}"
                digest = hashlib.sha256(excerpt.encode()).hexdigest()

                observations.append(
                    Observation(
                        observation_id=obs_id,
                        scan_id=scan_id,
                        candidate_asset_id=f"binary:{algo}:{hashlib.sha256(relative_path.encode()).hexdigest()[:10]}",
                        claim_type=ClaimType.BINARY_SYMBOL,
                        source_kind=SourceKind.BINARY,
                        algorithm=algo,
                        purpose=purpose,
                        relative_path=relative_path,
                        evidence_digest=digest,
                        sanitized_excerpt=excerpt,
                        detector_id=self.DETECTOR_ID,
                        ruleset_version=RULESET_VERSION,
                        confidence=conf if not is_stripped else ConfidenceBand.MEDIUM,
                        confidence_rationale=f"Static binary symbol reference in {format_name} binary (stripped={is_stripped})",
                        state=EvidenceState.OBSERVED,
                        raw_parameters={
                            "format": format_name,
                            "symbol": symbol_str,
                            "is_stripped": is_stripped,
                            "execution_performed": False,
                        },
                    )
                )

        # 3. Check for ASN.1 OIDs in binary strings
        for oid_str, (algo, purpose, conf) in CRYPTO_OIDS.items():
            oid_bytes = oid_str.encode("ascii")
            if oid_bytes in raw_bytes:
                obs_id = str(uuid.uuid4())
                excerpt = f"Format: {format_name} | ASN.1 OID Found: {oid_str} -> {algo}"
                digest = hashlib.sha256(excerpt.encode()).hexdigest()

                observations.append(
                    Observation(
                        observation_id=obs_id,
                        scan_id=scan_id,
                        candidate_asset_id=f"binary:oid:{algo}:{hashlib.sha256(relative_path.encode()).hexdigest()[:10]}",
                        claim_type=ClaimType.BINARY_SYMBOL,
                        source_kind=SourceKind.BINARY,
                        algorithm=algo,
                        purpose=purpose,
                        relative_path=relative_path,
                        evidence_digest=digest,
                        sanitized_excerpt=excerpt,
                        detector_id=self.DETECTOR_ID,
                        ruleset_version=RULESET_VERSION,
                        confidence=conf,
                        confidence_rationale=f"Embedded ASN.1 Object Identifier {oid_str} in static binary",
                        state=EvidenceState.OBSERVED,
                        raw_parameters={
                            "oid": oid_str,
                            "format": format_name,
                            "execution_performed": False,
                        },
                    )
                )

        # 4. Check for Cryptographic Constants
        for const_bytes, (algo, purpose, desc) in CRYPTO_CONSTANTS.items():
            if const_bytes in raw_bytes:
                obs_id = str(uuid.uuid4())
                excerpt = f"Format: {format_name} | {desc}"
                digest = hashlib.sha256(excerpt.encode()).hexdigest()

                observations.append(
                    Observation(
                        observation_id=obs_id,
                        scan_id=scan_id,
                        candidate_asset_id=f"binary:const:{algo}:{hashlib.sha256(relative_path.encode()).hexdigest()[:10]}",
                        claim_type=ClaimType.BINARY_SYMBOL,
                        source_kind=SourceKind.BINARY,
                        algorithm=algo,
                        purpose=purpose,
                        relative_path=relative_path,
                        evidence_digest=digest,
                        sanitized_excerpt=excerpt,
                        detector_id=self.DETECTOR_ID,
                        ruleset_version=RULESET_VERSION,
                        confidence=ConfidenceBand.HIGH,
                        confidence_rationale=desc,
                        state=EvidenceState.OBSERVED,
                        raw_parameters={
                            "constant_fingerprint": const_bytes.hex(),
                            "format": format_name,
                            "execution_performed": False,
                        },
                    )
                )

        return observations
