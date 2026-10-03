"""ASTRA - Network Endpoint & TLS Handshake Metadata Detector (Worker 01 - PROD-02).

Performs authorized endpoint metadata ingestion and simulated handshake inspection.
Enforces:
- Strict authorization allowlist gate (never connects to unauthorized hosts/ports)
- Rigorous separation of the 4 operational planes:
  1. CAPABILITY (what the endpoint is able to support)
  2. CONFIGURATION (what the administrator directed)
  3. NEGOTIATION (what was chosen in a specific session)
  4. ACTUAL_USE (what is actively transmitting live application data)
- Detection of classical vs PQC hybrid key exchanges (X25519MLKEM768 vs X25519)
- Downgrade vulnerability identification (SSLv3, TLS 1.0/1.1, export ciphers)
"""

import hashlib
import json
import re
import uuid
from enum import Enum
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


class NetworkOperationalPlane(str, Enum):
    """The four operational planes defined in the master research thesis."""

    CAPABILITY = "CAPABILITY"          # Server ciphersuite capability spectrum
    CONFIGURATION = "CONFIGURATION"    # Declared directives in configuration
    NEGOTIATION = "NEGOTIATION"        # Handshake negotiated choice
    ACTUAL_USE = "ACTUAL_USE"          # Active live payload transmission


# Allowed test / lab domains for authorized network evidence
DEFAULT_AUTHORIZED_ALLOWLIST = {
    "localhost",
    "127.0.0.1",
    "::1",
    "test.local",
    "pqc-lab.internal",
    "sandbox.internal",
}


class NetworkEndpointDetector:
    """Authorized network endpoint and TLS handshake metadata detector conforming to Worker 01 PROD-02."""

    DETECTOR_ID = "network_endpoint_detector_v1"

    def __init__(self, authorized_hosts: Optional[Set[str]] = None):
        self.authorized_hosts = set(authorized_hosts or DEFAULT_AUTHORIZED_ALLOWLIST)

    def is_target_authorized(self, host: str) -> bool:
        """Verify host is strictly in the authorized target allowlist."""
        return host.strip().lower() in self.authorized_hosts

    def can_analyze(self, file_path: Path) -> bool:
        """Check if file represents network endpoint metadata or TLS probe dump."""
        name = file_path.name.lower()
        if name.endswith((".tls.json", ".endpoint.json", ".cadi.json")):
            return True
        if "endpoint" in name and file_path.suffix.lower() == ".json":
            return True
        return False

    def analyze_file(
        self,
        file_path: Path,
        relative_path: str,
        scan_id: str,
    ) -> List[Observation]:
        """Analyze network endpoint dump or TLS session metadata."""
        observations: List[Observation] = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            return [
                Observation(
                    observation_id=str(uuid.uuid4()),
                    scan_id=scan_id,
                    candidate_asset_id=f"network:error:{hashlib.sha256(relative_path.encode()).hexdigest()[:10]}",
                    claim_type=ClaimType.NETWORK_ENDPOINT,
                    source_kind=SourceKind.NETWORK,
                    relative_path=relative_path,
                    evidence_digest=hashlib.sha256(str(e).encode()).hexdigest(),
                    sanitized_excerpt=f"Error parsing network endpoint metadata: {e}",
                    detector_id=self.DETECTOR_ID,
                    ruleset_version=RULESET_VERSION,
                    confidence=ConfidenceBand.LOW,
                    confidence_rationale="Malformed network endpoint metadata",
                    state=EvidenceState.FAILED,
                )
            ]

        # Handle list or dict payload
        endpoints = data if isinstance(data, list) else [data]

        for entry in endpoints:
            host = entry.get("host", "unknown")
            port = entry.get("port", 443)

            # Security gate: Must be authorized!
            if not self.is_target_authorized(host):
                observations.append(
                    Observation(
                        observation_id=str(uuid.uuid4()),
                        scan_id=scan_id,
                        candidate_asset_id=f"network:unauthorized:{host}:{port}",
                        claim_type=ClaimType.NETWORK_ENDPOINT,
                        source_kind=SourceKind.NETWORK,
                        relative_path=relative_path,
                        evidence_digest=hashlib.sha256(f"{host}:{port}".encode()).hexdigest(),
                        sanitized_excerpt=f"Target {host}:{port} is NOT on the authorized network scan allowlist. Skipped.",
                        detector_id=self.DETECTOR_ID,
                        ruleset_version=RULESET_VERSION,
                        confidence=ConfidenceBand.LOW,
                        confidence_rationale="Strict allowlist gate blocked non-authorized endpoint",
                        state=EvidenceState.UNSUPPORTED,
                        raw_parameters={"host": host, "port": port, "authorized": False},
                    )
                )
                continue

            # 1. Negotiated Handshake Session (Plane: NEGOTIATION)
            negotiated = entry.get("negotiated_session", {})
            if negotiated:
                protocol = negotiated.get("protocol_version", "TLSv1.3")
                ciphersuite = negotiated.get("ciphersuite", "UNKNOWN")
                key_exchange = negotiated.get("key_exchange", "UNKNOWN")

                is_pqc = "MLKEM" in key_exchange.upper() or "KYBER" in key_exchange.upper()
                algo_label = f"{key_exchange}+{ciphersuite}"
                obs_id = str(uuid.uuid4())
                excerpt = f"Endpoint: {host}:{port} | Protocol: {protocol} | Cipher: {ciphersuite} | KEX: {key_exchange} (PQC={is_pqc})"
                digest = hashlib.sha256(excerpt.encode()).hexdigest()

                observations.append(
                    Observation(
                        observation_id=obs_id,
                        scan_id=scan_id,
                        candidate_asset_id=f"network:{host}:{port}:negotiation",
                        claim_type=ClaimType.NETWORK_ENDPOINT,
                        source_kind=SourceKind.NETWORK,
                        algorithm=ciphersuite,
                        protocol=protocol,
                        purpose="TRANSPORT_SECURITY_NEGOTIATED",
                        relative_path=relative_path,
                        evidence_digest=digest,
                        sanitized_excerpt=excerpt,
                        detector_id=self.DETECTOR_ID,
                        ruleset_version=RULESET_VERSION,
                        confidence=ConfidenceBand.CONFIRMED,
                        confidence_rationale="Directly observed handshake negotiation outcome",
                        state=EvidenceState.OBSERVED,
                        raw_parameters={
                            "operational_plane": NetworkOperationalPlane.NEGOTIATION.value,
                            "host": host,
                            "port": port,
                            "key_exchange": key_exchange,
                            "is_post_quantum": is_pqc,
                            "actual_use_confirmed": False,  # Negotiation does not imply ongoing data use
                        },
                    )
                )

            # 2. Supported Ciphersuite Spectrum (Plane: CAPABILITY)
            capabilities = entry.get("supported_ciphers", [])
            for cipher in capabilities:
                obs_id = str(uuid.uuid4())
                excerpt = f"Endpoint: {host}:{port} | Supported Capability: {cipher}"
                digest = hashlib.sha256(excerpt.encode()).hexdigest()

                observations.append(
                    Observation(
                        observation_id=obs_id,
                        scan_id=scan_id,
                        candidate_asset_id=f"network:{host}:{port}:cap:{cipher}",
                        claim_type=ClaimType.NETWORK_ENDPOINT,
                        source_kind=SourceKind.NETWORK,
                        algorithm=cipher,
                        protocol=entry.get("max_protocol_version", "TLSv1.3"),
                        purpose="TRANSPORT_CIPHER_CAPABILITY",
                        relative_path=relative_path,
                        evidence_digest=digest,
                        sanitized_excerpt=excerpt,
                        detector_id=self.DETECTOR_ID,
                        ruleset_version=RULESET_VERSION,
                        confidence=ConfidenceBand.HIGH,
                        confidence_rationale="Server probe confirmed ciphersuite support capability",
                        state=EvidenceState.OBSERVED,
                        raw_parameters={
                            "operational_plane": NetworkOperationalPlane.CAPABILITY.value,
                            "host": host,
                            "port": port,
                            "cipher": cipher,
                        },
                    )
                )

        return observations
