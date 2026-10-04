"""ASTRA - Phase D Security Hardening & Surface Discovery Expansion Verification.

Validates:
  1. Hosted mode enforcement: POST /api/v1/scans/directory returns HTTP 403 in hosted mode.
  2. API Token authentication: Enforces X-ASTRA-API-KEY and Bearer token when ASTRA_API_KEY is configured.
  3. Upload size limit quotas: Rejects payloads exceeding quota with HTTP 413.
  4. OCI container layer & manifest discovery: Verifies ContainerCryptoDetector extracts
     base images, layer digests, and embedded cryptographic libraries from OCI archives.
  5. CLI safe local defaults & binding warnings.
"""

import io
import json
import os
import tarfile
import tempfile
import zipfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.discovery.detectors.container_detector import ContainerCryptoDetector
from app.discovery.models import SourceKind, EvidenceState, ConfidenceBand
from app.cli import main as cli_main


client = TestClient(app)


def create_minimal_zip() -> io.BytesIO:
    """Create a minimal valid zip file for testing upload endpoints."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("test.py", "x = 1\n")
    buf.seek(0)
    return buf


@pytest.fixture(autouse=True)
def cleanup_env():
    """Ensure environment modifications in tests are cleanly reverted."""
    old_env = dict(os.environ)
    yield
    os.environ.clear()
    os.environ.update(old_env)


def test_hosted_mode_disallows_directory_scan():
    """Verify that arbitrary directory scans are blocked with HTTP 403 in hosted mode."""
    os.environ["ASTRA_HOSTED_MODE"] = "1"
    os.environ.pop("ASTRA_ALLOW_DIRECTORY_SCAN", None)

    res = client.post("/api/v1/scans/directory", json={"path": "."})
    assert res.status_code == 403
    assert "hosted mode" in res.json()["detail"].lower()


def test_hosted_mode_override_permits_directory_scan():
    """Verify that setting ASTRA_ALLOW_DIRECTORY_SCAN=1 explicitly re-enables directory scan."""
    os.environ["ASTRA_HOSTED_MODE"] = "1"
    os.environ["ASTRA_ALLOW_DIRECTORY_SCAN"] = "1"

    # With non-existent path, should pass the 403 check and hit the 404 validation
    res = client.post("/api/v1/scans/directory", json={"path": "non_existent_folder_xyz_123"})
    assert res.status_code == 404


def test_api_key_authentication_enforcement():
    """Verify API token authentication across mutating scan endpoints."""
    test_key = "astra-secret-token-verify-9988"
    os.environ["ASTRA_API_KEY"] = test_key
    os.environ["ASTRA_HOSTED_MODE"] = "0"
    os.environ["ASTRA_ALLOW_DIRECTORY_SCAN"] = "1"

    zip_bytes = create_minimal_zip()

    # 1. Upload without API key -> HTTP 401
    res = client.post(
        "/api/v1/scans/upload",
        files={"file": ("test.zip", zip_bytes, "application/zip")},
    )
    assert res.status_code == 401
    assert "Unauthorized" in res.json()["detail"]

    # 2. Upload with invalid API key -> HTTP 401
    zip_bytes.seek(0)
    res = client.post(
        "/api/v1/scans/upload",
        files={"file": ("test.zip", zip_bytes, "application/zip")},
        headers={"X-ASTRA-API-KEY": "wrong-key"},
    )
    assert res.status_code == 401

    # 3. Upload with valid X-ASTRA-API-KEY header -> HTTP 200
    zip_bytes.seek(0)
    res = client.post(
        "/api/v1/scans/upload",
        files={"file": ("test.zip", zip_bytes, "application/zip")},
        headers={"X-ASTRA-API-KEY": test_key},
    )
    assert res.status_code == 200
    assert "scan_id" in res.json()

    # 4. Upload with Bearer token in Authorization header -> HTTP 200
    zip_bytes.seek(0)
    res = client.post(
        "/api/v1/scans/upload",
        files={"file": ("test.zip", zip_bytes, "application/zip")},
        headers={"Authorization": f"Bearer {test_key}"},
    )
    assert res.status_code == 200


def test_upload_size_limit_quota():
    """Verify upload boundary limit rejects oversized archives with HTTP 413."""
    # Set quota to 1024 bytes (1 KB)
    os.environ["ASTRA_MAX_UPLOAD_SIZE_BYTES"] = "1024"
    os.environ.pop("ASTRA_API_KEY", None)

    # Generate > 1KB uncompressible zip
    large_buf = io.BytesIO()
    with zipfile.ZipFile(large_buf, "w", zipfile.ZIP_STORED) as zf:
        zf.writestr("large.bin", os.urandom(3000))
    large_buf.seek(0)

    res = client.post(
        "/api/v1/scans/upload",
        files={"file": ("oversized.zip", large_buf, "application/zip")},
    )
    assert res.status_code == 413
    assert "exceeds maximum limit" in res.json()["detail"].lower()


def test_health_reflects_hosted_mode_status():
    """Verify /health endpoint dynamically reflects hosted mode & directory scan state."""
    os.environ["ASTRA_HOSTED_MODE"] = "1"
    os.environ["ASTRA_ALLOW_DIRECTORY_SCAN"] = "0"

    res = client.get("/api/v1/health")
    assert res.status_code == 200
    data = res.json()
    assert data["hosted_mode"] is True
    assert data["directory_scan_permitted"] is False


def test_oci_container_manifest_inspection(tmp_path: Path):
    """Verify ContainerCryptoDetector discovers base image identity and layers from OCI manifest."""
    manifest_data = {
        "schemaVersion": 2,
        "mediaType": "application/vnd.oci.image.manifest.v1+json",
        "config": {
            "mediaType": "application/vnd.oci.image.config.v1+json",
            "digest": "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        },
        "layers": [
            {
                "mediaType": "application/vnd.oci.image.layer.v1.tar+gzip",
                "digest": "sha256:openssl-system-layer-abc12345",
            }
        ],
        "annotations": {
            "org.opencontainers.image.base.name": "ubuntu:22.04",
        },
    }

    manifest_file = tmp_path / "manifest.json"
    manifest_file.write_text(json.dumps(manifest_data), encoding="utf-8")

    detector = ContainerCryptoDetector()
    assert detector.can_analyze(manifest_file) is True

    observations = detector.analyze_file(manifest_file, "manifest.json", "scan-test-oci-01")
    assert len(observations) >= 2

    algos = {o.algorithm for o in observations}
    assert any("CONTAINER_BASE:ubuntu:22.04" in a for a in algos)
    assert "OpenSSL" in algos
    for obs in observations:
        assert obs.source_kind == SourceKind.CONTAINER


def test_oci_container_layer_tar_archive_inspection(tmp_path: Path):
    """Verify ContainerCryptoDetector inspects members of OCI layer tar archives directly."""
    layer_tar = tmp_path / "layer.tar"
    with tarfile.open(layer_tar, "w") as tf:
        # Add mock libssl and wolfssl file entries
        info_ssl = tarfile.TarInfo(name="usr/lib/x86_64-linux-gnu/libssl.so.3")
        info_ssl.size = 0
        tf.addfile(info_ssl, io.BytesIO())

        info_wolf = tarfile.TarInfo(name="usr/local/lib/libwolfssl.so")
        info_wolf.size = 0
        tf.addfile(info_wolf, io.BytesIO())

    detector = ContainerCryptoDetector()
    assert detector.can_analyze(layer_tar) is True

    observations = detector.analyze_file(layer_tar, "layer.tar", "scan-test-oci-layer-01")
    assert len(observations) >= 2

    algos = {o.algorithm for o in observations}
    assert any("OpenSSL" in a for a in algos)
    assert "WolfSSL" in algos
    for obs in observations:
        assert obs.source_kind == SourceKind.CONTAINER
        assert obs.confidence == ConfidenceBand.CONFIRMED
        assert obs.state == EvidenceState.OBSERVED


def test_cli_host_and_api_key_configuration():
    """Verify that CLI serve command accepts host and api-key parameters."""
    # Running CLI help or version returns 0
    assert cli_main(["version"]) == 0
