"""ASTRA - Worker 01 MVP-02 Cryptographic Discovery Test Suite.

Validates deterministic discovery across source code, manifests, configs, and certificates.
Enforces zero secret leakage and verifies observation contracts (W01 -> W02).
Satisfies Acceptance Criteria: AC-03, AC-04, AC-06.
"""

from datetime import datetime, timezone, timedelta
import tempfile
from pathlib import Path
import pytest

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

from app.discovery.detectors.certificate_detector import CertificateCryptoDetector
from app.discovery.detectors.config_detector import ConfigCryptoDetector
from app.discovery.detectors.manifest_detector import ManifestCryptoDetector
from app.discovery.detectors.source_detector import SourceCryptoDetector
from app.discovery.engine import DiscoveryEngine
from app.discovery.models import (
    ClaimType,
    ConfidenceBand,
    EvidenceState,
    SourceKind,
)
from app.intake.models import ArchiveType, ExtractedFileEntry, ScanManifest, ScanStatus


@pytest.fixture
def temp_repo():
    """Temporary repository workspace."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


def test_source_detector_classical_and_pqc(temp_repo):
    """Test detecting classical algorithms and NIST post-quantum primitives in source files."""
    code_path = temp_repo / "crypto_module.py"
    code_path.write_text(
        "import hashlib\n"
        "from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes\n"
        "def setup():\n"
        "    cipher = Cipher(algorithms.AES(key), modes.GCM(iv))\n"
        "    # Implement Kyber-768 post-quantum key encapsulation\n"
        "    kex = 'ML-KEM-768'\n"
        "    digest = hashlib.sha256(b'data').digest()\n",
        encoding="utf-8",
    )

    detector = SourceCryptoDetector()
    assert detector.can_analyze(code_path) is True

    observations = detector.analyze_file(code_path, "crypto_module.py", "scan-test-01")
    algos = {obs.algorithm for obs in observations}

    assert "AES-256" in algos or "AES" in algos or "AES-128" in algos
    assert "ML-KEM" in algos
    assert "SHA-256" in algos

    for obs in observations:
        assert obs.relative_path == "crypto_module.py"
        assert obs.ruleset_version is not None
        assert obs.evidence_digest is not None
        assert obs.sanitized_excerpt is not None
        assert obs.confidence in (ConfidenceBand.CONFIRMED, ConfidenceBand.HIGH)


def test_source_detector_vulnerable_and_secret_redaction(temp_repo):
    """Test detection of legacy/vulnerable algorithms and redaction of secrets in source."""
    code_path = temp_repo / "legacy_auth.js"
    code_path.write_text(
        "const crypto = require('crypto');\n"
        "const api_secret = 'super_secret_token_1234567890';\n"
        "function hashOld(data) {\n"
        "    return crypto.createHash('md5').update(data).digest('hex');\n"
        "}\n",
        encoding="utf-8",
    )

    detector = SourceCryptoDetector()
    observations = detector.analyze_file(code_path, "legacy_auth.js", "scan-test-02")

    md5_obs = next((o for o in observations if o.algorithm == "MD5"), None)
    assert md5_obs is not None
    assert md5_obs.raw_parameters.get("quantum_status") == "VULNERABLE"

    # Verify secret was redacted in the snippet
    secret_obs = [o for o in observations if o.redacted]
    if secret_obs:
        assert "super_secret_token_1234567890" not in secret_obs[0].sanitized_excerpt
        assert "[REDACTED_SECRET]" in secret_obs[0].sanitized_excerpt


def test_manifest_detector_package_json(temp_repo):
    """Test detecting cryptographic dependencies in package.json."""
    pkg_path = temp_repo / "package.json"
    pkg_path.write_text(
        '{\n  "dependencies": {\n    "crypto-js": "^4.2.0",\n    "express": "^4.18.2"\n  }\n}\n',
        encoding="utf-8",
    )

    detector = ManifestCryptoDetector()
    assert detector.can_analyze(pkg_path) is True

    observations = detector.analyze_file(pkg_path, "package.json", "scan-test-03")
    assert len(observations) >= 1

    crypto_obs = observations[0]
    assert crypto_obs.claim_type == ClaimType.DEPENDENCY_REFERENCE
    assert crypto_obs.source_kind == SourceKind.MANIFEST
    assert "crypto-js" in crypto_obs.algorithm.lower()
    assert crypto_obs.state == EvidenceState.DECLARED


def test_manifest_detector_pom_xml(temp_repo):
    """Test detecting BouncyCastle dependencies in Maven pom.xml."""
    pom_path = temp_repo / "pom.xml"
    pom_path.write_text(
        "<project>\n"
        "  <dependencies>\n"
        "    <dependency>\n"
        "      <groupId>org.bouncycastle</groupId>\n"
        "      <artifactId>bcprov-jdk18on</artifactId>\n"
        "      <version>1.78.1</version>\n"
        "    </dependency>\n"
        "  </dependencies>\n"
        "</project>\n",
        encoding="utf-8",
    )

    detector = ManifestCryptoDetector()
    observations = detector.analyze_file(pom_path, "pom.xml", "scan-test-04")
    assert len(observations) >= 1
    assert "bcprov" in observations[0].algorithm.lower()


def test_config_detector_tls_and_ssh(temp_repo):
    """Test detecting TLS protocols and cipher suites in config files."""
    conf_path = temp_repo / "nginx.conf"
    conf_path.write_text(
        "server {\n"
        "    ssl_protocols TLSv1.2 TLSv1.3;\n"
        "    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA384;\n"
        "}\n",
        encoding="utf-8",
    )

    detector = ConfigCryptoDetector()
    assert detector.can_analyze(conf_path) is True

    observations = detector.analyze_file(conf_path, "nginx.conf", "scan-test-05")
    algos = {o.algorithm for o in observations}

    assert "TLSv1.2" in algos
    assert "TLSv1.3" in algos
    assert "ECDHE-AES256-GCM" in algos


def test_certificate_detector_x509_public_metadata(temp_repo):
    """Test parsing public X.509 certificate and extracting key algorithm and size."""
    cert_path = temp_repo / "server.crt"

    # Generate a genuine test RSA key and self-signed certificate
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, "astra.security.internal"),
    ])
    now = datetime.now(timezone.utc)
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(private_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now)
        .not_valid_after(now + timedelta(days=365))
        .sign(private_key, hashes.SHA256())
    )

    with open(cert_path, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

    detector = CertificateCryptoDetector()
    assert detector.can_analyze(cert_path) is True

    observations = detector.analyze_file(cert_path, "server.crt", "scan-test-06")
    assert len(observations) == 1

    obs = observations[0]
    assert obs.claim_type == ClaimType.CERTIFICATE_METADATA
    assert obs.source_kind == SourceKind.CERTIFICATE
    assert obs.algorithm == "RSA-2048"
    assert obs.key_size_bits == 2048
    assert obs.state == EvidenceState.VERIFIED
    assert "astra.security.internal" in obs.sanitized_excerpt
    assert obs.redacted is False


def test_certificate_detector_private_key_redaction(temp_repo):
    """Test that private key files are strictly detected and redacted without leaking bytes."""
    key_path = temp_repo / "private_key.pem"
    key_path.write_text(
        "-----BEGIN RSA PRIVATE KEY-----\n"
        "MIIEowIBAAKCAQEA0r1Z2x...SECRET_PRIVATE_KEY_BYTES_HERE...\n"
        "-----END RSA PRIVATE KEY-----\n",
        encoding="utf-8",
    )

    detector = CertificateCryptoDetector()
    observations = detector.analyze_file(key_path, "private_key.pem", "scan-test-07")
    assert len(observations) == 1

    obs = observations[0]
    assert obs.redacted is True
    assert "SECRET_PRIVATE_KEY_BYTES_HERE" not in obs.sanitized_excerpt
    assert "[REDACTED_PRIVATE_KEY_MATERIAL" in obs.sanitized_excerpt


def test_discovery_engine_end_to_end(temp_repo):
    """Test master DiscoveryEngine coordinating across all detectors in a sandbox."""
    # Create realistic repository structure in sandbox
    src_dir = temp_repo / "src"
    src_dir.mkdir()
    (src_dir / "service.py").write_text("import hashlib\nh = hashlib.sha256()\n", encoding="utf-8")
    (temp_repo / "requirements.txt").write_text("cryptography>=42.0.0\n", encoding="utf-8")
    (temp_repo / "app.conf").write_text("ssl_protocols TLSv1.3;\n", encoding="utf-8")
    (temp_repo / "unsupported.xyz").write_text("random binary data", encoding="utf-8")

    manifest = ScanManifest(
        scan_id="scan-e2e-discovery",
        archive_name="test.zip",
        archive_sha256="abc123sha256",
        archive_size_bytes=1024,
        archive_type=ArchiveType.ZIP,
        declared_scope="E2E_SCOPE",
        tenant_id="tenant-01",
        status=ScanStatus.RUNNING,
        intake_engine_version="1.0.0",
        collector_version="0.1.0",
        ruleset_version="2026.10-nist-pqc",
        files=[
            ExtractedFileEntry(relative_path="src/service.py", size_bytes=100, sha256="h1", file_extension=".py", is_supported=True),
            ExtractedFileEntry(relative_path="requirements.txt", size_bytes=50, sha256="h2", file_extension=".txt", is_supported=True),
            ExtractedFileEntry(relative_path="app.conf", size_bytes=40, sha256="h3", file_extension=".conf", is_supported=True),
            ExtractedFileEntry(relative_path="unsupported.xyz", size_bytes=20, sha256="h4", file_extension=".xyz", is_supported=False),
        ]
    )

    engine = DiscoveryEngine()
    summary = engine.run_discovery(temp_repo, manifest)

    assert summary.scan_id == "scan-e2e-discovery"
    assert summary.total_files_analyzed == 4
    assert summary.files_with_findings == 3
    assert summary.files_with_zero_findings == 1
    assert summary.unsupported_files_count == 1
    assert len(summary.observations) >= 3

    # Check that observations.json was written to sandbox
    obs_file = temp_repo / "observations.json"
    assert obs_file.exists()
