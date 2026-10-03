"""ASTRA - Production Multi-Modal Discovery Tests (Worker 01 PROD-01 & PROD-02).

Tests:
- Static binary discovery: ELF magic, OpenSSL symbols, PQC symbols (ML-KEM, ML-DSA), ASN.1 OIDs, cryptographic constants
- Container layer discovery: Dockerfile base images, crypto packages, environment variables
- Network endpoint discovery: authorized allowlist gating, separation of CAPABILITY vs NEGOTIATION vs ACTUAL_USE
"""

import json
import pytest
from pathlib import Path

from app.discovery.detectors.binary_detector import BinaryCryptoDetector
from app.discovery.detectors.container_detector import ContainerCryptoDetector
from app.discovery.detectors.network_detector import NetworkEndpointDetector, NetworkOperationalPlane
from app.discovery.models import ClaimType, ConfidenceBand, EvidenceState, SourceKind


def test_static_binary_detector_elf_and_symbols(tmp_path: Path):
    """Verify static binary analysis identifies ELF headers and crypto symbols without process execution."""
    bin_file = tmp_path / "libcrypto_test.so"
    # Create fake ELF binary with symbols
    content = b"\x7fELF" + b"\x00" * 32 + b"RSA_new\x00EVP_EncryptInit_ex\x00AES_gcm_encrypt\x00OQS_KEM_ml_kem_768_new\x00" + b".symtab\x00"
    bin_file.write_bytes(content)

    detector = BinaryCryptoDetector()
    assert detector.can_analyze(bin_file) is True

    observations = detector.analyze_file(bin_file, "libcrypto_test.so", "scan-test-bin-01")
    assert len(observations) >= 3

    algos = {obs.algorithm for obs in observations}
    assert "RSA" in algos
    assert "AES-GCM" in algos
    assert "ML-KEM-768" in algos

    for obs in observations:
        assert obs.source_kind == SourceKind.BINARY
        assert obs.claim_type == ClaimType.BINARY_SYMBOL
        assert obs.raw_parameters.get("execution_performed") is False
        assert obs.raw_parameters.get("is_stripped") is False


def test_static_binary_detector_oids_and_constants(tmp_path: Path):
    """Verify ASN.1 OID and constant matching in static binary bytes."""
    bin_file = tmp_path / "app.exe"
    # MZ header with embedded OID for secp256r1 and SHA-256 initial constants
    content = (
        b"MZ\x90\x00"
        b"Padding Data 12345"
        b"1.2.840.10045.3.1.7"  # secp256r1 OID
        b"Some more binary data"
        b"\x67\xe6\x09\x6a\x85\xae\x67\xbb"  # SHA-256 constant
    )
    bin_file.write_bytes(content)

    detector = BinaryCryptoDetector()
    assert detector.can_analyze(bin_file) is True

    observations = detector.analyze_file(bin_file, "app.exe", "scan-test-bin-02")
    algos = {obs.algorithm for obs in observations}
    assert "secp256r1" in algos
    assert "SHA-256" in algos


def test_container_detector_dockerfile(tmp_path: Path):
    """Verify Dockerfile inspection extracts base image and installed crypto packages."""
    df = tmp_path / "Dockerfile"
    df.write_text(
        "FROM ubuntu:22.04\n"
        "RUN apt-get update && apt-get install -y openssl libssl-dev liboqs ca-certificates\n"
        "ENV SSL_CERT_DIR=/etc/ssl/certs\n"
        "CMD [\"./app\"]\n",
        encoding="utf-8",
    )

    detector = ContainerCryptoDetector()
    assert detector.can_analyze(df) is True

    observations = detector.analyze_file(df, "Dockerfile", "scan-test-docker-01")
    assert len(observations) >= 4

    algos = {obs.algorithm for obs in observations}
    assert any("CONTAINER_BASE" in a for a in algos)
    assert "OpenSSL" in algos
    assert "OpenSSL-Dev" in algos
    assert "liboqs" in algos

    for obs in observations:
        assert obs.source_kind == SourceKind.CONTAINER
        assert obs.state == EvidenceState.DECLARED


def test_network_detector_authorized_and_planes(tmp_path: Path):
    """Verify network detector allowlists hosts and distinguishes operational planes."""
    net_file = tmp_path / "gateway.endpoint.json"
    net_data = [
        {
            "host": "localhost",
            "port": 443,
            "max_protocol_version": "TLSv1.3",
            "negotiated_session": {
                "protocol_version": "TLSv1.3",
                "ciphersuite": "TLS_AES_256_GCM_SHA384",
                "key_exchange": "X25519MLKEM768",
            },
            "supported_ciphers": [
                "TLS_AES_256_GCM_SHA384",
                "TLS_CHACHA20_POLY1305_SHA256",
            ],
        },
        {
            "host": "unauthorized-malicious-domain.com",
            "port": 443,
            "supported_ciphers": ["TLS_AES_128_GCM_SHA256"],
        },
    ]
    net_file.write_text(json.dumps(net_data), encoding="utf-8")

    detector = NetworkEndpointDetector(authorized_hosts={"localhost"})
    assert detector.can_analyze(net_file) is True

    observations = detector.analyze_file(net_file, "gateway.endpoint.json", "scan-test-net-01")

    # Localhost observations
    localhost_obs = [o for o in observations if "localhost" in o.candidate_asset_id]
    assert len(localhost_obs) >= 2

    # Check operational planes
    planes = [o.raw_parameters.get("operational_plane") for o in localhost_obs]
    assert NetworkOperationalPlane.NEGOTIATION.value in planes
    assert NetworkOperationalPlane.CAPABILITY.value in planes

    # Check PQC hybrid detection
    negotiated_obs = [o for o in localhost_obs if o.raw_parameters.get("operational_plane") == NetworkOperationalPlane.NEGOTIATION.value][0]
    assert negotiated_obs.raw_parameters.get("is_post_quantum") is True
    assert negotiated_obs.raw_parameters.get("actual_use_confirmed") is False

    # Check unauthorized endpoint was rejected
    unauthorized_obs = [o for o in observations if "unauthorized" in o.candidate_asset_id]
    assert len(unauthorized_obs) == 1
    assert unauthorized_obs[0].state == EvidenceState.UNSUPPORTED
    assert unauthorized_obs[0].raw_parameters.get("authorized") is False
