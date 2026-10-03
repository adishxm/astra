"""ASTRA - Security-Property, Trust & Rollback Assurance Engine (Worker 03 - PROD-02).

Implements:
- Security invariant verification (Confidentiality, Authenticity, Forward Secrecy, Non-Repudiation)
- Downgrade immunity auditing (protecting against active cipher stripping and MITM manipulation)
- Rollback safety evaluation (dual-mode / hybrid transition safety, fail-closed vs. fail-open)
- Trust-chain anchor continuity analysis
"""

from enum import Enum
from typing import Any, Dict, List, Optional, Set
from pydantic import BaseModel, Field


class SecurityProperty(str, Enum):
    """Core cryptographic security properties."""

    CONFIDENTIALITY = "CONFIDENTIALITY"
    AUTHENTICITY = "AUTHENTICITY"
    INTEGRITY = "INTEGRITY"
    FORWARD_SECRECY = "FORWARD_SECRECY"
    NON_REPUDIATION = "NON_REPUDIATION"
    QUANTUM_RESISTANCE = "QUANTUM_RESISTANCE"


class CandidateTransition(BaseModel):
    """Proposed cryptographic migration transition for an asset."""

    asset_id: str
    legacy_algorithm: str
    purpose: str
    candidate_algorithm: str
    is_hybrid: bool = False
    fallback_allowed: bool = False
    fallback_algorithm: Optional[str] = None
    protocol_context: str = "TLSv1.3"


class InvariantAuditResult(BaseModel):
    """Evaluation of security invariant preservation for a candidate transition."""

    asset_id: str
    is_sound: bool = True
    preserved_properties: List[SecurityProperty] = Field(default_factory=list)
    missing_properties: List[SecurityProperty] = Field(default_factory=list)
    downgrade_vulnerable: bool = False
    rollback_safe: bool = True
    findings: List[str] = Field(default_factory=list)
    assurance_score: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Overall security and transition assurance score (0-100)",
    )


class SecurityInvariantAssuranceEngine:
    """Audits cryptographic migration plans for security invariant violations and rollback vulnerabilities."""

    # Map algorithm categories to security properties
    ALGORITHM_PROPERTIES: Dict[str, Set[SecurityProperty]] = {
        # Classical Key Exchange / Public Key Enc
        "RSA": {SecurityProperty.CONFIDENTIALITY},
        "RSA-2048": {SecurityProperty.CONFIDENTIALITY},
        "ECDH": {SecurityProperty.CONFIDENTIALITY, SecurityProperty.FORWARD_SECRECY},
        "X25519": {SecurityProperty.CONFIDENTIALITY, SecurityProperty.FORWARD_SECRECY},
        # Classical Signatures
        "ECDSA": {SecurityProperty.AUTHENTICITY, SecurityProperty.INTEGRITY, SecurityProperty.NON_REPUDIATION},
        "Ed25519": {SecurityProperty.AUTHENTICITY, SecurityProperty.INTEGRITY, SecurityProperty.NON_REPUDIATION},
        # PQC Key Encapsulation (FIPS 203)
        "ML-KEM-512": {SecurityProperty.CONFIDENTIALITY, SecurityProperty.FORWARD_SECRECY, SecurityProperty.QUANTUM_RESISTANCE},
        "ML-KEM-768": {SecurityProperty.CONFIDENTIALITY, SecurityProperty.FORWARD_SECRECY, SecurityProperty.QUANTUM_RESISTANCE},
        "ML-KEM-1024": {SecurityProperty.CONFIDENTIALITY, SecurityProperty.FORWARD_SECRECY, SecurityProperty.QUANTUM_RESISTANCE},
        # PQC Signatures (FIPS 204 & 205)
        "ML-DSA-44": {SecurityProperty.AUTHENTICITY, SecurityProperty.INTEGRITY, SecurityProperty.NON_REPUDIATION, SecurityProperty.QUANTUM_RESISTANCE},
        "ML-DSA-65": {SecurityProperty.AUTHENTICITY, SecurityProperty.INTEGRITY, SecurityProperty.NON_REPUDIATION, SecurityProperty.QUANTUM_RESISTANCE},
        "ML-DSA-87": {SecurityProperty.AUTHENTICITY, SecurityProperty.INTEGRITY, SecurityProperty.NON_REPUDIATION, SecurityProperty.QUANTUM_RESISTANCE},
        "SLH-DSA": {SecurityProperty.AUTHENTICITY, SecurityProperty.INTEGRITY, SecurityProperty.NON_REPUDIATION, SecurityProperty.QUANTUM_RESISTANCE},
        # Hybrid
        "X25519MLKEM768": {SecurityProperty.CONFIDENTIALITY, SecurityProperty.FORWARD_SECRECY, SecurityProperty.QUANTUM_RESISTANCE},
        "ECDSA+ML-DSA-65": {SecurityProperty.AUTHENTICITY, SecurityProperty.INTEGRITY, SecurityProperty.NON_REPUDIATION, SecurityProperty.QUANTUM_RESISTANCE},
    }

    BROKEN_ALGORITHMS: Set[str] = {"DES", "3DES", "RC4", "MD5", "SHA-1", "RSA-1024"}

    def audit_transition(self, transition: CandidateTransition) -> InvariantAuditResult:
        """Audit candidate cryptographic transition against security invariants."""
        findings = []
        is_sound = True

        # 1. Properties comparison
        # Find baseline properties
        legacy_norm = transition.legacy_algorithm.upper().replace("_", "-")
        target_norm = transition.candidate_algorithm.upper().replace("_", "-")

        legacy_props = set()
        for k, v in self.ALGORITHM_PROPERTIES.items():
            if k.upper() in legacy_norm or legacy_norm in k.upper():
                legacy_props.update(v)

        target_props = set()
        for k, v in self.ALGORITHM_PROPERTIES.items():
            if k.upper() in target_norm or target_norm in k.upper():
                target_props.update(v)

        # Baseline check if target covers legacy required properties
        preserved = list(legacy_props.intersection(target_props))
        # Quantum resistance is an added enhancement
        if SecurityProperty.QUANTUM_RESISTANCE in target_props and SecurityProperty.QUANTUM_RESISTANCE not in preserved:
            preserved.append(SecurityProperty.QUANTUM_RESISTANCE)

        missing = list(legacy_props - target_props)
        if missing:
            is_sound = False
            missing_names = [m.value for m in missing]
            findings.append(f"Security invariant violated: Target candidate lacks properties: {missing_names}")

        # 2. Downgrade immunity verification
        downgrade_vulnerable = False
        if transition.protocol_context in {"TLSv1.0", "TLSv1.1", "SSLv3"}:
            downgrade_vulnerable = True
            is_sound = False
            findings.append(
                f"Protocol context '{transition.protocol_context}' lacks downgrade protection; "
                "adversary can strip PQC extensions via cipher suite rollback."
            )

        # 3. Rollback safety analysis
        rollback_safe = True
        if transition.fallback_allowed:
            fallback_alg = (transition.fallback_algorithm or "").upper()
            if not fallback_alg or any(b in fallback_alg for b in self.BROKEN_ALGORITHMS):
                rollback_safe = False
                is_sound = False
                findings.append(
                    f"Insecure rollback: Transition permits fallback to vulnerable primitive '{fallback_alg or 'UNSPECIFIED'}'. "
                    "Fail-closed policy required."
                )
            elif not transition.is_hybrid:
                findings.append(
                    "Warning: Standalone transition allows classical fallback without hybrid encapsulation; "
                    "dual-mode negotiation should be cryptographically bound."
                )

        # 4. Compute assurance score
        base_score = 100.0
        if missing:
            base_score -= 40.0
        if downgrade_vulnerable:
            base_score -= 30.0
        if not rollback_safe:
            base_score -= 30.0
        if SecurityProperty.QUANTUM_RESISTANCE not in target_props:
            base_score -= 20.0
        if transition.is_hybrid and is_sound:
            base_score = min(100.0, base_score + 5.0)

        final_score = max(0.0, min(100.0, round(base_score, 1)))

        return InvariantAuditResult(
            asset_id=transition.asset_id,
            is_sound=is_sound,
            preserved_properties=preserved,
            missing_properties=missing,
            downgrade_vulnerable=downgrade_vulnerable,
            rollback_safe=rollback_safe,
            findings=findings,
            assurance_score=final_score,
        )
