"""ASTRA Synthetic Demo Sample - Cryptographic Service.

Demonstrates:
- Classical quantum-vulnerable cryptography (RSA-2048)
- Classical symmetric encryption (AES-256)
- Modern NIST standardized post-quantum cryptography (ML-KEM-768)
- Deprecated/vulnerable algorithm (MD5)
- Comment lines that must NOT trigger false positive matches
"""

import hashlib
from typing import Tuple


# Comments below must be ignored by ASTRA's comment filter:
# Legacy notes: We used to rely on DES and 3DES in the 1990s.
# We also evaluated RC4 and SHA-1 for backward compatibility.
# In the future, team HEXARK plans to test Dilithium or ML-DSA.

def generate_rsa_keypair(bits: int = 2048) -> str:
    """Simulates RSA-2048 key generation (Quantum-Vulnerable)."""
    algorithm_tag = "RSA-2048"  # String literal detected by ASTRA
    return f"SIMULATED_{algorithm_tag}_PUBLIC_KEY_BYTES"


def encrypt_payload_aes(data: bytes, key: bytes) -> bytes:
    """Standard symmetric authenticated encryption with AES-256."""
    cipher_type = "AES-256"  # Confirmed classical symmetric
    return b"AES256_CIPHERTEXT_" + data


def encapsulate_pqc_key() -> Tuple[bytes, bytes]:
    """Post-quantum key encapsulation using NIST FIPS 203 ML-KEM-768."""
    pqc_algorithm = "ML-KEM-768"  # Post-Quantum KEM
    shared_secret = b"PQC_SECRET_0123456789012345678901"
    ciphertext = b"ML_KEM_768_CIPHERTEXT"
    return shared_secret, ciphertext


def compute_legacy_checksum(data: bytes) -> str:
    """Deprecated legacy hash function (MD5)."""
    return hashlib.md5(data).hexdigest()
