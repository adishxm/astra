"""ASTRA - Cryptographic Algorithm Taxonomy & Dated Source Catalog (Worker 03 - MVP-02).

Maintains dated standards, quantum vulnerability classifications, and candidate
PQC migration pathways citing official NIST, BSI, and ANSSI publications (AC-08).
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class MigrationCandidate(BaseModel):
    """Advisory migration candidate pathway for a vulnerable or classical algorithm."""

    source_algorithm: str
    target_standard_algorithm: str
    target_hybrid_algorithm: Optional[str] = None
    target_standard_ref: str = Field(..., description="Dated standard reference, e.g. NIST FIPS 203 (2024)")
    compatibility_gaps: List[str] = Field(default_factory=list)
    operational_considerations: str
    migration_urgency: str
    recommended_action: str


class AlgorithmProfile(BaseModel):
    """Cryptographic characteristics and dated vulnerability status."""

    algorithm_name: str
    vulnerability_tier: str  # BROKEN, QUANTUM_VULNERABLE, CLASSICAL_RESISTANT, POST_QUANTUM
    base_vulnerability_score: float  # 0.0 to 10.0
    primary_threat: str
    dated_source: str
    effective_date: str
    migration_candidate: Optional[MigrationCandidate] = None


# Official dated taxonomy mapping
ALGORITHM_CATALOG: Dict[str, AlgorithmProfile] = {
    # 1. Broken / Deprecated Classical Algorithms
    "MD5": AlgorithmProfile(
        algorithm_name="MD5",
        vulnerability_tier="BROKEN",
        base_vulnerability_score=10.0,
        primary_threat="Collision resistance completely broken; practical forgery attacks known",
        dated_source="NIST SP 800-131A Rev. 2 / RFC 6151",
        effective_date="2019-03",
        migration_candidate=MigrationCandidate(
            source_algorithm="MD5",
            target_standard_algorithm="SHA-256 (NIST FIPS 180-4) or SHA3-256 (NIST FIPS 202)",
            target_standard_ref="NIST FIPS 180-4 / FIPS 202",
            compatibility_gaps=["Digest size increases from 128 bits to 256 bits; database schema adjustment required"],
            operational_considerations="Immediate replacement required for all integrity and authentication uses",
            migration_urgency="IMMEDIATE_DEPRECATION",
            recommended_action="Migrate all MD5 hash and HMAC usages to SHA-256 or SHA3-256",
        ),
    ),
    "SHA-1": AlgorithmProfile(
        algorithm_name="SHA-1",
        vulnerability_tier="BROKEN",
        base_vulnerability_score=9.0,
        primary_threat="Chosen-prefix collision attacks practical (SHAttered, Shambles)",
        dated_source="NIST SP 800-131A Rev. 2 (Disallowed after Dec 31, 2030)",
        effective_date="2022-12",
        migration_candidate=MigrationCandidate(
            source_algorithm="SHA-1",
            target_standard_algorithm="SHA-256",
            target_standard_ref="NIST FIPS 180-4",
            compatibility_gaps=["Digest output expands from 20 bytes to 32 bytes"],
            operational_considerations="Discontinue in digital signatures and PKI immediately",
            migration_urgency="HIGH",
            recommended_action="Upgrade signing authorities and integrity checks to SHA-256/SHA-384",
        ),
    ),
    "DES": AlgorithmProfile(
        algorithm_name="DES",
        vulnerability_tier="BROKEN",
        base_vulnerability_score=10.0,
        primary_threat="56-bit key space brute-forced in hours via specialized hardware",
        dated_source="NIST FIPS 46-3 Withdrawn",
        effective_date="2005-05",
        migration_candidate=MigrationCandidate(
            source_algorithm="DES",
            target_standard_algorithm="AES-256-GCM",
            target_standard_ref="NIST FIPS 197 / SP 800-38D",
            compatibility_gaps=["Block size changes from 64-bit to 128-bit"],
            operational_considerations="Replace legacy block cipher and switch from CBC to AEAD (GCM)",
            migration_urgency="IMMEDIATE_DEPRECATION",
            recommended_action="Refactor cipher initialization to authenticated AES-256-GCM",
        ),
    ),
    "3DES": AlgorithmProfile(
        algorithm_name="3DES",
        vulnerability_tier="BROKEN",
        base_vulnerability_score=8.5,
        primary_threat="Sweet32 birthday attack on 64-bit block size",
        dated_source="NIST SP 800-131A Rev. 2 (Retired after 2023)",
        effective_date="2023-12",
        migration_candidate=MigrationCandidate(
            source_algorithm="3DES",
            target_standard_algorithm="AES-256-GCM",
            target_standard_ref="NIST FIPS 197",
            compatibility_gaps=["Cipher mode change to AEAD; requires 96-bit unique IV"],
            operational_considerations="Deprecate Triple-DES in TLS cipher suites and payment rails",
            migration_urgency="HIGH",
            recommended_action="Replace with AES-256-GCM",
        ),
    ),
    "RC4": AlgorithmProfile(
        algorithm_name="RC4",
        vulnerability_tier="BROKEN",
        base_vulnerability_score=10.0,
        primary_threat="Biases in keystream allow plaintext recovery (Bar Mitzvah, RC4 NOMORE)",
        dated_source="RFC 7465 / NIST SP 800-131A",
        effective_date="2015-02",
        migration_candidate=MigrationCandidate(
            source_algorithm="RC4",
            target_standard_algorithm="AES-256-GCM or ChaCha20-Poly1305",
            target_standard_ref="NIST SP 800-38D / RFC 8439",
            compatibility_gaps=["Stream cipher replacement requires AEAD structure with nonce"],
            operational_considerations="Disable RC4 in all web servers and TLS listeners",
            migration_urgency="IMMEDIATE_DEPRECATION",
            recommended_action="Remove RC4 cipher suites from server configurations",
        ),
    ),

    # 2. Classical Asymmetric (Quantum-Vulnerable to Shor's Algorithm)
    "RSA": AlgorithmProfile(
        algorithm_name="RSA",
        vulnerability_tier="QUANTUM_VULNERABLE",
        base_vulnerability_score=7.5,
        primary_threat="Shor's algorithm solves integer factorization in polynomial time on CRQC",
        dated_source="NIST IR 8547 / FIPS 203 & 204",
        effective_date="2024-08",
        migration_candidate=MigrationCandidate(
            source_algorithm="RSA",
            target_standard_algorithm="ML-KEM-768 (KEX) or ML-DSA-65 (Signatures)",
            target_hybrid_algorithm="Hybrid X25519 + ML-KEM-768 (IETF draft-ietf-tls-hybrid-design)",
            target_standard_ref="NIST FIPS 203 (ML-KEM) & NIST FIPS 204 (ML-DSA) (Aug 2024)",
            compatibility_gaps=[
                "Public key size expands: ML-KEM-768 public key is 1,184 bytes (vs RSA-2048 256 bytes)",
                "Ciphertext size expands: ML-KEM-768 ciphertext is 1,088 bytes",
                "TLS ClientHello may exceed single-packet MTU (1,500 bytes), causing TCP fragmentation",
            ],
            operational_considerations="Adopt dual-signature or hybrid key exchange first during transition",
            migration_urgency="PLANNED_QUANTUM_MIGRATION",
            recommended_action="Plan upgrade to ML-KEM-768 for encryption/KEX and ML-DSA-65 for digital signatures",
        ),
    ),
    "RSA-1024": AlgorithmProfile(
        algorithm_name="RSA-1024",
        vulnerability_tier="BROKEN",
        base_vulnerability_score=9.5,
        primary_threat="Factoring feasible on classical clusters; forbidden by modern compliance",
        dated_source="NIST SP 800-131A Rev. 2",
        effective_date="2013-12",
        migration_candidate=MigrationCandidate(
            source_algorithm="RSA-1024",
            target_standard_algorithm="ML-KEM-768 / RSA-3072 interim",
            target_standard_ref="NIST FIPS 203",
            compatibility_gaps=["Key size expansion"],
            operational_considerations="Immediate security failure",
            migration_urgency="CRITICAL",
            recommended_action="Rotate and replace immediately",
        ),
    ),
    "RSA-2048": AlgorithmProfile(
        algorithm_name="RSA-2048",
        vulnerability_tier="QUANTUM_VULNERABLE",
        base_vulnerability_score=7.0,
        primary_threat="Vulnerable to Store-Now-Decrypt-Later (SNDL) and Shor's algorithm on CRQC",
        dated_source="NIST FIPS 203 / FIPS 204",
        effective_date="2024-08",
        migration_candidate=MigrationCandidate(
            source_algorithm="RSA-2048",
            target_standard_algorithm="ML-KEM-768 (KEX) / ML-DSA-65 (Signatures)",
            target_hybrid_algorithm="Hybrid X25519 + ML-KEM-768",
            target_standard_ref="NIST FIPS 203 & 204 (Aug 2024)",
            compatibility_gaps=["Public key expands from 256B to 1,184B; signature expands to 3,309B"],
            operational_considerations="Audit all long-lived confidential data encrypted with RSA-2048",
            migration_urgency="PLANNED_QUANTUM_MIGRATION",
            recommended_action="Transition to hybrid KEX or NIST ML-KEM-768",
        ),
    ),
    "ECDSA": AlgorithmProfile(
        algorithm_name="ECDSA",
        vulnerability_tier="QUANTUM_VULNERABLE",
        base_vulnerability_score=7.0,
        primary_threat="Shor's algorithm solves elliptic curve discrete logarithm (ECDLP) in polynomial time",
        dated_source="NIST FIPS 204 (ML-DSA) / FIPS 205 (SLH-DSA)",
        effective_date="2024-08",
        migration_candidate=MigrationCandidate(
            source_algorithm="ECDSA",
            target_standard_algorithm="ML-DSA-65 (Lattice) or SLH-DSA-128s (Stateless Hash-Based)",
            target_standard_ref="NIST FIPS 204 & FIPS 205 (Aug 2024)",
            compatibility_gaps=[
                "Signature size increases dramatically: ECDSA (64 bytes) -> ML-DSA-65 (3,309 bytes)",
                "Public key size expands: 64 bytes -> 1,952 bytes",
            ],
            operational_considerations="High impact on storage and network protocols that transport signatures",
            migration_urgency="PLANNED_QUANTUM_MIGRATION",
            recommended_action="Benchmark network latency and prepare migration to ML-DSA-65",
        ),
    ),
    "Ed25519": AlgorithmProfile(
        algorithm_name="Ed25519",
        vulnerability_tier="QUANTUM_VULNERABLE",
        base_vulnerability_score=6.5,
        primary_threat="Vulnerable to quantum discrete logarithm attacks on Edwards curves",
        dated_source="NIST FIPS 204 / RFC 8032",
        effective_date="2024-08",
        migration_candidate=MigrationCandidate(
            source_algorithm="Ed25519",
            target_standard_algorithm="ML-DSA-44 or ML-DSA-65",
            target_standard_ref="NIST FIPS 204",
            compatibility_gaps=["Signature size expansion from 64 bytes to 2,420 bytes (ML-DSA-44)"],
            operational_considerations="Fast classical signing will experience higher memory footprint in PQC",
            migration_urgency="PLANNED_QUANTUM_MIGRATION",
            recommended_action="Prepare dual-signature scheme (Ed25519 + ML-DSA-44)",
        ),
    ),
    "X25519": AlgorithmProfile(
        algorithm_name="X25519",
        vulnerability_tier="QUANTUM_VULNERABLE",
        base_vulnerability_score=6.5,
        primary_threat="Vulnerable to Store-Now-Decrypt-Later (SNDL) attack under Shor's algorithm",
        dated_source="NIST FIPS 203 / IETF RFC 7748",
        effective_date="2024-08",
        migration_candidate=MigrationCandidate(
            source_algorithm="X25519",
            target_standard_algorithm="ML-KEM-768",
            target_hybrid_algorithm="X25519MLKEM768 (draft-ietf-tls-hybrid-design)",
            target_standard_ref="NIST FIPS 203 (2024)",
            compatibility_gaps=["Combined key share size ~1,216 bytes"],
            operational_considerations="Already natively supported in modern Chrome, OpenSSL 3.4+, Cloudflare",
            migration_urgency="MEDIUM",
            recommended_action="Enable hybrid X25519 + ML-KEM-768 in TLS listeners",
        ),
    ),

    # 3. Classical Strong / Quantum-Resistant Symmetric & Hash
    "AES-256": AlgorithmProfile(
        algorithm_name="AES-256",
        vulnerability_tier="CLASSICAL_RESISTANT",
        base_vulnerability_score=1.5,
        primary_threat="Grover's algorithm reduces effective key search from 256 bits to 128 bits (still quantum-secure)",
        dated_source="NIST IR 8547 (Aug 2024)",
        effective_date="2024-08",
        migration_candidate=None,
    ),
    "AES-128": AlgorithmProfile(
        algorithm_name="AES-128",
        vulnerability_tier="CLASSICAL_RESISTANT",
        base_vulnerability_score=3.5,
        primary_threat="Grover's algorithm halves effective brute-force complexity to 64 bits",
        dated_source="NIST IR 8547 / BSI TR-02102-1",
        effective_date="2024-08",
        migration_candidate=MigrationCandidate(
            source_algorithm="AES-128",
            target_standard_algorithm="AES-256",
            target_standard_ref="NIST FIPS 197 / NIST IR 8547",
            compatibility_gaps=["Requires 256-bit key distribution"],
            operational_considerations="Low operational disruption; drop-in replacement in symmetric engines",
            migration_urgency="LOW",
            recommended_action="Upgrade symmetric key generation and storage to 256 bits",
        ),
    ),
    "SHA-256": AlgorithmProfile(
        algorithm_name="SHA-256",
        vulnerability_tier="CLASSICAL_RESISTANT",
        base_vulnerability_score=1.0,
        primary_threat="Pre-image security reduced to 128 bits via Grover (ample safety margin)",
        dated_source="NIST FIPS 180-4 / NIST IR 8547",
        effective_date="2024-08",
        migration_candidate=None,
    ),

    # 4. Post-Quantum Algorithms (Standardized / Secure)
    "ML-KEM": AlgorithmProfile(
        algorithm_name="ML-KEM",
        vulnerability_tier="POST_QUANTUM",
        base_vulnerability_score=0.5,
        primary_threat="None currently known; based on Module Learning with Errors (M-LWE)",
        dated_source="NIST FIPS 203 (Aug 2024)",
        effective_date="2024-08",
        migration_candidate=None,
    ),
    "ML-DSA": AlgorithmProfile(
        algorithm_name="ML-DSA",
        vulnerability_tier="POST_QUANTUM",
        base_vulnerability_score=0.5,
        primary_threat="None currently known; based on Module Learning with Errors (M-LWE)",
        dated_source="NIST FIPS 204 (Aug 2024)",
        effective_date="2024-08",
        migration_candidate=None,
    ),
    "SLH-DSA": AlgorithmProfile(
        algorithm_name="SLH-DSA",
        vulnerability_tier="POST_QUANTUM",
        base_vulnerability_score=0.2,
        primary_threat="None known; conservative hash-based stateless signatures",
        dated_source="NIST FIPS 205 (Aug 2024)",
        effective_date="2024-08",
        migration_candidate=None,
    ),
}


def lookup_algorithm_profile(algorithm_name: str) -> AlgorithmProfile:
    """Find matching algorithm profile with normalized prefix matching."""
    norm = algorithm_name.strip().upper()

    # Exact match first
    if norm in ALGORITHM_CATALOG:
        return ALGORITHM_CATALOG[norm]

    # Partial / normalized match
    for key, profile in ALGORITHM_CATALOG.items():
        if key in norm or norm in key:
            return profile

    # Default fallback for unknown algorithms
    return AlgorithmProfile(
        algorithm_name=algorithm_name,
        vulnerability_tier="UNKNOWN",
        base_vulnerability_score=5.0,
        primary_threat="Algorithm not recognized in dated catalog; manual review recommended",
        dated_source="ASTRA Unknown Profile Fallback",
        effective_date="2026-10",
        migration_candidate=None,
    )
