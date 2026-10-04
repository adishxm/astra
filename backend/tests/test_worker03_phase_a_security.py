"""ASTRA - Worker 03 Phase A Security Hardening & Fail-Closed Auth Tests.

Verifies:
  1. Fail-closed behavior in hosted mode when no API key is configured.
  2. Complete read-and-write protection across all scan endpoints when auth is enabled.
  3. Proper authentication via X-ASTRA-API-KEY and Bearer token headers.
  4. Upload rate limiting triggering HTTP 429 upon threshold breach.
  5. Air-gapped guarantee: Zero outbound network socket connections during analysis.
"""

import io
import os
import socket
import zipfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app, _UPLOAD_RATE_LIMIT_STORE

client = TestClient(app)


def create_minimal_zip() -> io.BytesIO:
    """Create a minimal valid zip file for testing upload endpoints."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("test.py", "import hashlib\nhashlib.sha256(b'hello').hexdigest()\n")
    buf.seek(0)
    return buf


@pytest.fixture(autouse=True)
def cleanup_env():
    """Ensure environment modifications in tests are cleanly reverted."""
    old_env = dict(os.environ)
    _UPLOAD_RATE_LIMIT_STORE.clear()
    yield
    os.environ.clear()
    os.environ.update(old_env)
    _UPLOAD_RATE_LIMIT_STORE.clear()


def test_hosted_mode_fails_closed_without_api_key_on_upload():
    """Verify that in hosted mode without an API key, upload requests fail closed with 401."""
    os.environ["ASTRA_HOSTED_MODE"] = "1"
    os.environ.pop("ASTRA_API_KEY", None)

    zip_buf = create_minimal_zip()
    res = client.post(
        "/api/v1/scans/upload",
        files={"file": ("test.zip", zip_buf, "application/zip")},
    )
    assert res.status_code == 401
    assert "hosted mode" in res.json()["detail"].lower()


def test_hosted_mode_fails_closed_without_api_key_on_list():
    """Verify that in hosted mode without an API key, scan listings fail closed with 401."""
    os.environ["ASTRA_HOSTED_MODE"] = "1"
    os.environ.pop("ASTRA_API_KEY", None)

    res = client.get("/api/v1/scans")
    assert res.status_code == 401
    assert "hosted mode" in res.json()["detail"].lower()


def test_unauthenticated_read_endpoints_fail_with_401_when_key_set():
    """Verify all read/inspection routes require authentication when ASTRA_API_KEY is configured."""
    os.environ["ASTRA_API_KEY"] = "secure-corp-token-8844"
    os.environ["ASTRA_HOSTED_MODE"] = "0"

    # All of these should fail with 401 Unauthorized for anonymous readers
    endpoints = [
        ("/api/v1/scans", "GET"),
        ("/api/v1/scans/fake-scan-id", "GET"),
        ("/api/v1/scans/fake-scan-id/findings", "GET"),
        ("/api/v1/scans/fake-scan-id/coverage", "GET"),
        ("/api/v1/scans/fake-scan-id/risk", "GET"),
        ("/api/v1/scans/fake-scan-id/export", "GET"),
        ("/api/v1/workflow/evidence/fake-asset-id", "GET"),
        ("/api/v1/workflow/export", "GET"),
    ]

    for path, method in endpoints:
        res = client.request(method, path)
        assert res.status_code == 401, f"Expected 401 for unauthenticated {method} {path}, got {res.status_code}"
        assert "Unauthorized" in res.json()["detail"] or "invalid API key" in res.json()["detail"]


def test_authenticated_read_endpoints_succeed_with_header_and_bearer():
    """Verify authenticated access succeeds using X-ASTRA-API-KEY and Bearer token."""
    key = "secure-corp-token-8844"
    os.environ["ASTRA_API_KEY"] = key
    os.environ["ASTRA_HOSTED_MODE"] = "0"

    # 1. Custom header auth
    res_hdr = client.get("/api/v1/scans", headers={"X-ASTRA-API-KEY": key})
    assert res_hdr.status_code == 200

    # 2. Bearer token auth
    res_bearer = client.get("/api/v1/scans", headers={"Authorization": f"Bearer {key}"})
    assert res_bearer.status_code == 200

    # 3. Invalid key fails
    res_invalid = client.get("/api/v1/scans", headers={"X-ASTRA-API-KEY": "wrong-key"})
    assert res_invalid.status_code == 401


def test_upload_rate_limiting_enforcement():
    """Verify in-memory sliding-window upload rate limiter rejects excessive requests with 429."""
    os.environ["ASTRA_RATE_LIMIT_UPLOADS_PER_MINUTE"] = "3"
    os.environ["ASTRA_HOSTED_MODE"] = "0"
    os.environ.pop("ASTRA_API_KEY", None)

    # 3 uploads should pass (or fail with 400 bad archive, but not 429)
    for i in range(3):
        buf = create_minimal_zip()
        res = client.post("/api/v1/scans/upload", files={"file": (f"test_{i}.zip", buf, "application/zip")})
        assert res.status_code == 200, f"Upload {i} failed: {res.status_code}"

    # 4th upload must be rate-limited with HTTP 429
    buf4 = create_minimal_zip()
    res4 = client.post("/api/v1/scans/upload", files={"file": ("test_4.zip", buf4, "application/zip")})
    assert res4.status_code == 429
    assert "rate limit exceeded" in res4.json()["detail"].lower()


def test_air_gapped_zero_outbound_network_egress(monkeypatch):
    """Verify that the cryptographic scan executes with 0 outbound network socket connections."""
    os.environ["ASTRA_HOSTED_MODE"] = "0"
    os.environ.pop("ASTRA_API_KEY", None)

    outbound_attempts = []

    original_connect = socket.socket.connect

    def hostile_socket_guard(self, address):
        host = address[0] if isinstance(address, tuple) else address
        if host in ("127.0.0.1", "localhost", "::1"):
            return original_connect(self, address)
        outbound_attempts.append(address)
        raise ConnectionRefusedError(f"Air-gapped policy violation: attempted egress connection to {address}")

    monkeypatch.setattr(socket.socket, "connect", hostile_socket_guard)

    # Run complete scan on archive
    buf = create_minimal_zip()
    res = client.post("/api/v1/scans/upload", files={"file": ("airgap_test.zip", buf, "application/zip")})
    assert res.status_code == 200
    assert res.json()["status"] == "completed"

    # Assert no outbound socket connections were attempted
    assert len(outbound_attempts) == 0, f"Expected 0 socket connections, got {outbound_attempts}"
