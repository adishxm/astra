"""ASTRA - Certificate & Key Cryptographic Detector (Worker 01 - MVP-02).

Inspects X.509 certificates and public keys using standard cryptography parser.
Enforces zero secret leakage: private key bytes are detected, flagged, and strictly redacted.
"""

import hashlib
import uuid
from pathlib import Path
from typing import List

from cryptography import x509
from cryptography.hazmat.primitives.asymmetric import dsa, ec, ed25519, rsa

from app.core.config import RULESET_VERSION
from app.discovery.models import (
    ClaimType,
    ConfidenceBand,
    EvidenceState,
    Observation,
    SourceKind,
)


class CertificateCryptoDetector:
    """Discovers X.509 certificates, public keys, and redacts private keys."""

    DETECTOR_ID = "detector-certificate-v1"

    CERT_EXTENSIONS = {".pem", ".crt", ".cer", ".der", ".pub", ".key"}

    def can_analyze(self, file_path: Path) -> bool:
        return file_path.suffix.lower() in self.CERT_EXTENSIONS

    def analyze_file(
        self,
        file_path: Path,
        relative_path: str,
        scan_id: str,
    ) -> List[Observation]:
        """Parse certificate or key file, extract public metadata, and sanitize secrets."""
        observations: List[Observation] = []

        try:
            with open(file_path, "rb") as f:
                raw_bytes = f.read()
        except OSError:
            return []

        # Check for Private Key markers to enforce redaction
        has_private_key = (
            b"PRIVATE KEY" in raw_bytes
            or b"ENCRYPTED PRIVATE KEY" in raw_bytes
        )

        # 1. Try parsing as PEM X.509 Certificate
        try:
            cert = x509.load_pem_x509_certificate(raw_bytes)
            return self._extract_cert_observations(cert, relative_path, scan_id, has_private_key)
        except Exception:
            pass

        # 2. Try parsing as DER X.509 Certificate
        try:
            cert = x509.load_der_x509_certificate(raw_bytes)
            return self._extract_cert_observations(cert, relative_path, scan_id, has_private_key)
        except Exception:
            pass

        # 3. If file contains private key markers but isn't an X.509 cert
        if has_private_key:
            sanitized = "[REDACTED_PRIVATE_KEY_MATERIAL: File contains private key material which is strictly excluded from storage]"
            digest = hashlib.sha256(sanitized.encode()).hexdigest()
            observations.append(
                Observation(
                    observation_id=str(uuid.uuid4()),
                    scan_id=scan_id,
                    candidate_asset_id=f"private-key-{relative_path}",
                    claim_type=ClaimType.KEY_SPECIFICATION,
                    source_kind=SourceKind.CERTIFICATE,
                    algorithm="PRIVATE_KEY",
                    purpose="PRIVATE_KEY_CREDENTIAL",
                    relative_path=relative_path,
                    start_line=1,
                    end_line=1,
                    evidence_digest=digest,
                    sanitized_excerpt=sanitized,
                    redacted=True,
                    detector_id=self.DETECTOR_ID,
                    ruleset_version=RULESET_VERSION,
                    confidence=ConfidenceBand.CONFIRMED,
                    confidence_rationale="Detected private key material; payload sanitized and redacted according to AC-03 policy",
                    state=EvidenceState.OBSERVED,
                    raw_parameters={"contains_secret": True},
                )
            )

        return observations

    def _extract_cert_observations(
        self,
        cert: x509.Certificate,
        relative_path: str,
        scan_id: str,
        has_private_key: bool,
    ) -> List[Observation]:
        """Extract public certificate parameters into structured Observation."""
        obs_list: List[Observation] = []

        # Extract Public Key metadata
        public_key = cert.public_key()
        pub_algo = "UNKNOWN"
        key_size = None
        curve_name = None
        q_status = "QUANTUM_VULNERABLE"

        if isinstance(public_key, rsa.RSAPublicKey):
            pub_algo = f"RSA-{public_key.key_size}"
            key_size = public_key.key_size
        elif isinstance(public_key, ec.EllipticCurvePublicKey):
            curve_name = public_key.curve.name
            pub_algo = f"ECDSA-{curve_name}"
            key_size = public_key.key_size
        elif isinstance(public_key, ed25519.Ed25519PublicKey):
            pub_algo = "Ed25519"
            key_size = 256
        elif isinstance(public_key, dsa.DSAPublicKey):
            pub_algo = f"DSA-{public_key.key_size}"
            key_size = public_key.key_size
            q_status = "VULNERABLE"

        # Signature algorithm
        sig_algo = cert.signature_algorithm_oid._name

        subject = cert.subject.rfc4514_string()
        issuer = cert.issuer.rfc4514_string()
        valid_from = cert.not_valid_before_utc.isoformat()
        valid_to = cert.not_valid_after_utc.isoformat()

        excerpt = (
            f"Subject: {subject} | Issuer: {issuer} | "
            f"PublicKey: {pub_algo} ({key_size} bits) | "
            f"SigAlgo: {sig_algo} | Valid: {valid_from} to {valid_to}"
        )
        digest = hashlib.sha256(excerpt.encode()).hexdigest()

        obs_list.append(
            Observation(
                observation_id=str(uuid.uuid4()),
                scan_id=scan_id,
                candidate_asset_id=f"cert-{pub_algo.lower()}-{relative_path}",
                claim_type=ClaimType.CERTIFICATE_METADATA,
                source_kind=SourceKind.CERTIFICATE,
                algorithm=pub_algo,
                purpose="IDENTITY_AND_AUTHENTICATION",
                key_size_bits=key_size,
                curve_name=curve_name,
                relative_path=relative_path,
                start_line=1,
                end_line=1,
                evidence_digest=digest,
                sanitized_excerpt=excerpt,
                redacted=has_private_key,
                detector_id=self.DETECTOR_ID,
                ruleset_version=RULESET_VERSION,
                confidence=ConfidenceBand.CONFIRMED,
                confidence_rationale="Parsed standard X.509 certificate public key and signature algorithm",
                state=EvidenceState.VERIFIED,
                raw_parameters={
                    "signature_algorithm": sig_algo,
                    "subject": subject,
                    "issuer": issuer,
                    "valid_from": valid_from,
                    "valid_to": valid_to,
                    "quantum_status": q_status,
                },
            )
        )

        return obs_list
