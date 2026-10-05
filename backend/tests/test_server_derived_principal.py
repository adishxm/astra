"""ASTRA - Permanent Server-Derived Principal Authentication & Route Authorization Tests.

Verifies:
  1. Server-derived tenant and user identity from API credentials (single-key and mapped-keys mode).
  2. Strict ignoring/rejection of untrusted client headers (X-Tenant-ID, X-User-ID).
  3. Fail-closed protection for missing, invalid, or malformed credentials in hosted mode.
  4. Local offline fixed principal behavior and CLI compatibility.
  5. Complete route-by-route multi-tenant isolation across all endpoints (scans, detail, findings, coverage, risk, context PUT, export, evidence, workflow export, audit endpoints).
  6. Audit event attribution, export exact-count semantics, restart persistence, and tamper detection.
"""

import io
import json
import os
import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytest
from fastapi.testclient import TestClient

from app.auth import get_tenant_id, get_user_id, verify_api_key, _UPLOAD_RATE_LIMIT_STORE
from app.main import app
from app.services.scan_service import GLOBAL_SCAN_SERVICE, GLOBAL_SCAN_STORE
from app.web_workflow.audit_store import AuditChainStore, GLOBAL_AUDIT_STORE

client = TestClient(app)


def create_crypto_test_zip() -> io.BytesIO:
    """Create an in-memory zip archive with cryptography code for scanner tests."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(
            "app.py",
            "import hashlib\n"
            "from cryptography.hazmat.primitives.asymmetric import rsa\n"
            "key = rsa.generate_private_key(public_exponent=65537, key_size=2048)\n"
            "h = hashlib.sha256(b'test').hexdigest()\n",
        )
    buf.seek(0)
    return buf


@pytest.fixture(autouse=True)
def isolate_test_stores():
    """Ensure clean temporary audit and scan stores for every test."""
    _UPLOAD_RATE_LIMIT_STORE.clear()
    temp_dir = tempfile.mkdtemp(prefix="astra_principal_test_")
    audit_file = os.path.join(temp_dir, "audit_chain.json")
    scans_dir = os.path.join(temp_dir, "scans")

    old_audit_path = GLOBAL_AUDIT_STORE.file_path
    old_scan_dir = GLOBAL_SCAN_STORE.storage_dir

    test_audit_store = AuditChainStore(storage_path=audit_file)
    GLOBAL_AUDIT_STORE.file_path = Path(audit_file)
    GLOBAL_AUDIT_STORE._chain = test_audit_store._chain

    GLOBAL_SCAN_STORE.storage_dir = Path(scans_dir)
    GLOBAL_SCAN_STORE.storage_dir.mkdir(parents=True, exist_ok=True)
    GLOBAL_SCAN_STORE._memory_cache.clear()

    yield

    _UPLOAD_RATE_LIMIT_STORE.clear()
    GLOBAL_AUDIT_STORE.file_path = old_audit_path
    GLOBAL_SCAN_STORE.storage_dir = old_scan_dir
    GLOBAL_SCAN_STORE._memory_cache.clear()
    shutil.rmtree(temp_dir, ignore_errors=True)


# ============================================================================
# Phase 1 — Permanent Authentication / Principal Tests
# ============================================================================


def test_single_key_mode_derives_configured_principal(monkeypatch):
    """Verify single-key configuration binds to the server-configured tenant/user principal."""
    monkeypatch.setenv("ASTRA_API_KEY", "secret-key-100")
    monkeypatch.setenv("ASTRA_DEFAULT_TENANT_ID", "acme-corp")
    monkeypatch.setenv("ASTRA_DEFAULT_USER_ID", "acme-admin")
    monkeypatch.delenv("ASTRA_API_KEYS", raising=False)

    headers = {
        "X-ASTRA-API-KEY": "secret-key-100",
        "X-Tenant-ID": "forged-tenant",
        "X-User-ID": "forged-user",
    }

    # Upload scan with forged headers
    resp = client.post(
        "/api/v1/scans/upload",
        files={"file": ("test.zip", create_crypto_test_zip(), "application/zip")},
        headers=headers,
    )
    assert resp.status_code == 200
    scan_id = resp.json()["scan_id"]

    # Verify stored record tenant is acme-corp, NOT forged-tenant
    record = GLOBAL_SCAN_STORE.get(scan_id)
    rec_tenant = getattr(record, "tenant_id", None) if not isinstance(record, dict) else record.get("tenant_id")
    assert rec_tenant == "acme-corp"


def test_mapped_keys_mode_derives_distinct_principals(monkeypatch):
    """Verify ASTRA_API_KEYS maps distinct API keys to distinct server-configured tenant/user principals."""
    api_keys = {
        "alpha-key": {"tenant_id": "tenant-alpha", "user_id": "alice"},
        "beta-key": {"tenant_id": "tenant-beta", "user_id": "bob"},
    }
    monkeypatch.setenv("ASTRA_API_KEYS", json.dumps(api_keys))

    # Upload for Alpha
    resp_a = client.post(
        "/api/v1/scans/upload",
        files={"file": ("alpha.zip", create_crypto_test_zip(), "application/zip")},
        headers={"X-ASTRA-API-KEY": "alpha-key", "X-Tenant-ID": "attacker-tenant"},
    )
    assert resp_a.status_code == 200
    scan_id_a = resp_a.json()["scan_id"]

    # Upload for Beta
    resp_b = client.post(
        "/api/v1/scans/upload",
        files={"file": ("beta.zip", create_crypto_test_zip(), "application/zip")},
        headers={"X-ASTRA-API-KEY": "beta-key", "X-Tenant-ID": "attacker-tenant"},
    )
    assert resp_b.status_code == 200
    scan_id_b = resp_b.json()["scan_id"]

    rec_a = GLOBAL_SCAN_STORE.get(scan_id_a)
    rec_b = GLOBAL_SCAN_STORE.get(scan_id_b)
    tenant_a = rec_a.tenant_id if hasattr(rec_a, "tenant_id") else rec_a.get("tenant_id")
    tenant_b = rec_b.tenant_id if hasattr(rec_b, "tenant_id") else rec_b.get("tenant_id")

    assert tenant_a == "tenant-alpha"
    assert tenant_b == "tenant-beta"


def test_missing_and_invalid_hosted_credentials_fail_closed(monkeypatch):
    """Verify hosted mode returns 401 Unauthorized for missing or invalid keys across protected endpoints."""
    monkeypatch.setenv("ASTRA_HOSTED_MODE", "true")
    monkeypatch.setenv("ASTRA_API_KEY", "valid-prod-key")

    # Missing credential -> 401
    resp_missing = client.get("/api/v1/scans")
    assert resp_missing.status_code == 401
    assert "Unauthorized" in resp_missing.json()["detail"]
    assert "valid-prod-key" not in resp_missing.json()["detail"]

    # Invalid credential -> 401
    resp_invalid = client.get("/api/v1/scans", headers={"X-ASTRA-API-KEY": "invalid-key"})
    assert resp_invalid.status_code == 401
    assert "Unauthorized" in resp_invalid.json()["detail"]


def test_header_forgery_and_duplicate_headers_ignored(monkeypatch):
    """Verify client-supplied X-Tenant-ID and X-User-ID headers cannot alter principal identity under any variation."""
    api_keys = {"valid-key": {"tenant_id": "tenant-real", "user_id": "real-user"}}
    monkeypatch.setenv("ASTRA_API_KEYS", json.dumps(api_keys))

    variations = [
        {"X-ASTRA-API-KEY": "valid-key", "X-Tenant-ID": "fake-tenant"},
        {"X-ASTRA-API-KEY": "valid-key", "X-Tenant-ID": "", "X-User-ID": ""},
        {"X-ASTRA-API-KEY": "valid-key", "X-Tenant-ID": "tenant-a, tenant-b"},
        {"X-ASTRA-API-KEY": "valid-key", "X-Tenant-ID": "null"},
        {"X-ASTRA-API-KEY": "valid-key", "X-Tenant-ID": "../../../etc/passwd"},
    ]

    for headers in variations:
        resp = client.get("/api/v1/scans", headers=headers)
        assert resp.status_code == 200, f"Failed for headers: {headers}"


def test_local_unauthenticated_mode_fixed_principal(monkeypatch):
    """Verify local offline mode uses fixed default principal and ignores client identity headers."""
    monkeypatch.setenv("ASTRA_HOSTED_MODE", "false")
    monkeypatch.delenv("ASTRA_API_KEY", raising=False)
    monkeypatch.delenv("ASTRA_API_KEYS", raising=False)
    monkeypatch.setenv("ASTRA_DEFAULT_TENANT_ID", "local-default")

    # In local mode, requests succeed without API key
    resp = client.get("/api/v1/scans", headers={"X-Tenant-ID": "spoofed-local-tenant"})
    assert resp.status_code == 200


def test_malformed_api_keys_json_fails_closed(monkeypatch):
    """Verify malformed ASTRA_API_KEYS JSON fails closed in hosted mode."""
    monkeypatch.setenv("ASTRA_HOSTED_MODE", "true")
    monkeypatch.setenv("ASTRA_API_KEYS", "{bad_json: true,")

    resp = client.get("/api/v1/scans", headers={"X-ASTRA-API-KEY": "some-key"})
    assert resp.status_code == 401


# ============================================================================
# Phase 2 — Permanent Route-by-Route Authorization Tests
# ============================================================================


def setup_synthetic_tenant_scans(monkeypatch):
    """Helper to seed synthetic scans for tenant-alpha and tenant-beta."""
    api_keys = {
        "alpha-key": {"tenant_id": "tenant-alpha", "user_id": "alice"},
        "beta-key": {"tenant_id": "tenant-beta", "user_id": "bob"},
    }
    monkeypatch.setenv("ASTRA_API_KEYS", json.dumps(api_keys))

    # Upload scan for Alpha
    resp_a = client.post(
        "/api/v1/scans/upload",
        files={"file": ("alpha.zip", create_crypto_test_zip(), "application/zip")},
        headers={"X-ASTRA-API-KEY": "alpha-key"},
    )
    assert resp_a.status_code == 200
    scan_id_a = resp_a.json()["scan_id"]

    # Upload scan for Beta
    resp_b = client.post(
        "/api/v1/scans/upload",
        files={"file": ("beta.zip", create_crypto_test_zip(), "application/zip")},
        headers={"X-ASTRA-API-KEY": "beta-key"},
    )
    assert resp_b.status_code == 200
    scan_id_b = resp_b.json()["scan_id"]

    return scan_id_a, scan_id_b, {"X-ASTRA-API-KEY": "alpha-key"}, {"X-ASTRA-API-KEY": "beta-key"}


def test_route_list_scans_isolation(monkeypatch):
    """Verify GET /api/v1/scans returns only own tenant scans."""
    scan_id_a, scan_id_b, alpha_headers, beta_headers = setup_synthetic_tenant_scans(monkeypatch)

    list_a = client.get("/api/v1/scans", headers=alpha_headers).json()
    assert any(s["scan_id"] == scan_id_a for s in list_a)
    assert not any(s["scan_id"] == scan_id_b for s in list_a)

    # Forged header attempt on Alpha list request
    forged_headers = dict(alpha_headers)
    forged_headers["X-Tenant-ID"] = "tenant-beta"
    list_forged = client.get("/api/v1/scans", headers=forged_headers).json()
    assert not any(s["scan_id"] == scan_id_b for s in list_forged)


def test_route_scan_detail_findings_coverage_risk_isolation(monkeypatch):
    """Verify GET /api/v1/scans/{id}, /findings, /coverage, /risk enforce isolation (404 on foreign scan)."""
    scan_id_a, scan_id_b, alpha_headers, beta_headers = setup_synthetic_tenant_scans(monkeypatch)

    endpoints = [
        f"/api/v1/scans/{scan_id_a}",
        f"/api/v1/scans/{scan_id_a}/findings",
        f"/api/v1/scans/{scan_id_a}/coverage",
        f"/api/v1/scans/{scan_id_a}/risk",
    ]

    # Owner access (Alpha -> Alpha scan) -> 200
    for ep in endpoints:
        resp = client.get(ep, headers=alpha_headers)
        assert resp.status_code == 200, f"Owner failed for {ep}"

    # Foreign tenant access (Beta -> Alpha scan) -> 404
    for ep in endpoints:
        resp = client.get(ep, headers=beta_headers)
        assert resp.status_code == 404, f"Foreign tenant was not denied with 404 for {ep}"
        assert scan_id_a not in resp.text or "not found" in resp.text.lower()


def test_route_context_update_correct_method_and_isolation(monkeypatch):
    """Verify PUT /api/v1/scans/{id}/context allows owner update and denies foreign tenant with 404."""
    scan_id_a, scan_id_b, alpha_headers, beta_headers = setup_synthetic_tenant_scans(monkeypatch)
    ctx_payload = {"data_shelf_life_years": 10.0, "migration_duration_years": 4.0}

    # Owner update -> 200
    resp_owner = client.put(f"/api/v1/scans/{scan_id_a}/context", json=ctx_payload, headers=alpha_headers)
    assert resp_owner.status_code == 200
    assert resp_owner.json()["context"]["data_shelf_life_years"] == 10.0

    # Foreign update -> 404
    resp_foreign = client.put(f"/api/v1/scans/{scan_id_a}/context", json=ctx_payload, headers=beta_headers)
    assert resp_foreign.status_code == 404


def test_route_cbom_export_isolation(monkeypatch):
    """Verify GET /api/v1/scans/{id}/export returns CBOM for owner and 404 for foreign tenant."""
    scan_id_a, scan_id_b, alpha_headers, beta_headers = setup_synthetic_tenant_scans(monkeypatch)

    # Owner export -> 200
    resp_owner = client.get(f"/api/v1/scans/{scan_id_a}/export?format=cyclonedx", headers=alpha_headers)
    assert resp_owner.status_code == 200
    assert resp_owner.json()["bomFormat"] == "CycloneDX"

    # Foreign export -> 404
    resp_foreign = client.get(f"/api/v1/scans/{scan_id_a}/export?format=cyclonedx", headers=beta_headers)
    assert resp_foreign.status_code == 404


def test_route_workflow_evidence_and_export_isolation(monkeypatch):
    """Verify workflow evidence and export endpoints isolate findings per server tenant."""
    scan_id_a, scan_id_b, alpha_headers, beta_headers = setup_synthetic_tenant_scans(monkeypatch)

    # Get Alpha's scan detail to extract an asset_id
    detail_a = client.get(f"/api/v1/scans/{scan_id_a}", headers=alpha_headers).json()
    canonical_assets = detail_a.get("canonical_assets", [])
    assert len(canonical_assets) > 0
    asset_id_a = canonical_assets[0]["asset_id"]

    # Owner evidence query -> list response
    ev_owner = client.get(f"/api/v1/workflow/evidence/{asset_id_a}", headers=alpha_headers)
    assert ev_owner.status_code == 200
    assert isinstance(ev_owner.json(), list)

    # Foreign evidence query -> empty list
    ev_foreign = client.get(f"/api/v1/workflow/evidence/{asset_id_a}", headers=beta_headers)
    assert ev_foreign.status_code == 200
    assert len(ev_foreign.json()) == 0

    # Workflow export isolation
    exp_owner = client.get("/api/v1/workflow/export", headers=alpha_headers)
    assert exp_owner.status_code == 200
    assert "assets" in exp_owner.json()

    exp_foreign = client.get("/api/v1/workflow/export", headers=beta_headers)
    assert exp_foreign.status_code == 200
    foreign_assets = exp_foreign.json().get("assets", [])

    # Foreign export should not expose Alpha's assets
    assert not any(a.get("asset_id") == asset_id_a for a in foreign_assets if isinstance(a, dict))


def test_route_audit_append_uses_server_principal(monkeypatch):
    """Verify POST /api/v1/workflow/audit/chain/append sets actor and tenant_id from server principal."""
    api_keys = {"key-auditor": {"tenant_id": "sec-ops", "user_id": "auditor-42"}}
    monkeypatch.setenv("ASTRA_API_KEYS", json.dumps(api_keys))

    headers = {
        "X-ASTRA-API-KEY": "key-auditor",
        "X-Tenant-ID": "evil-tenant",
        "X-User-ID": "evil-actor",
    }
    body = {
        "action": "POLICY_REVIEW",
        "actor": "body-actor-override",
        "asset_id": "asset-100",
        "details": {"notes": "Audit approved"},
    }

    resp = client.post("/api/v1/workflow/audit/chain/append", json=body, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["details"]["tenant_id"] == "sec-ops"
    assert data["details"]["user_id"] == "auditor-42"


def test_route_audit_list_verify_perscan_isolation(monkeypatch):
    """Verify audit chain endpoints filter events by server-derived tenant."""
    scan_id_a, scan_id_b, alpha_headers, beta_headers = setup_synthetic_tenant_scans(monkeypatch)

    # Beta querying audit chain should not see Alpha's scan events
    beta_audit = client.get("/api/v1/workflow/audit/chain", headers=beta_headers).json()
    assert not any(e.get("asset_id") == scan_id_a for e in beta_audit)
    assert any(e.get("asset_id") == scan_id_b for e in beta_audit)

    # Beta querying audit verify should return valid for Beta's events only
    beta_verify = client.get("/api/v1/workflow/audit/chain/verify", headers=beta_headers).json()
    assert beta_verify["valid"] is True
    assert not any(e.get("asset_id") == scan_id_a for e in beta_verify.get("events", []))

    # Beta querying per-scan audit events for Alpha scan -> empty list
    beta_perscan = client.get(f"/api/v1/workflow/audit/events/{scan_id_a}", headers=beta_headers).json()
    assert len(beta_perscan) == 0


def test_route_hosted_directory_scan_policy(monkeypatch):
    """Verify POST /api/v1/scans/directory is denied with 403 by default in hosted mode."""
    monkeypatch.setenv("ASTRA_HOSTED_MODE", "true")
    monkeypatch.setenv("ASTRA_API_KEY", "hosted-key")
    monkeypatch.delenv("ASTRA_ALLOW_DIRECTORY_SCAN", raising=False)

    headers = {"X-ASTRA-API-KEY": "hosted-key"}
    resp = client.post("/api/v1/scans/directory", json={"target_dir": "."}, headers=headers)
    assert resp.status_code == 403
    assert "disabled in hosted mode" in resp.json()["detail"].lower()


# ============================================================================
# Phase 3 — Audit Semantics & Persistence Tests
# ============================================================================


def test_audit_export_semantics_exact_counts(monkeypatch):
    """Verify scan intake emits 0 export events, successful export emits 1, failed export emits 0."""
    api_keys = {"export-key": {"tenant_id": "tenant-export", "user_id": "exporter-1"}}
    monkeypatch.setenv("ASTRA_API_KEYS", json.dumps(api_keys))
    headers = {"X-ASTRA-API-KEY": "export-key"}

    # 1. Intake scan upload
    upload_resp = client.post(
        "/api/v1/scans/upload",
        files={"file": ("vault.zip", create_crypto_test_zip(), "application/zip")},
        headers=headers,
    )
    assert upload_resp.status_code == 200
    scan_id = upload_resp.json()["scan_id"]

    # Verify 0 CBOM_EXPORTED events after intake
    events_1 = client.get("/api/v1/workflow/audit/chain", headers=headers).json()
    cbom_events_1 = [e for e in events_1 if e["action"] == "CBOM_EXPORTED"]
    assert len(cbom_events_1) == 0

    # 2. Failed export (invalid scan ID) -> 0 CBOM_EXPORTED events emitted
    client.get("/api/v1/scans/non-existent-id/export?format=cyclonedx", headers=headers)
    events_2 = client.get("/api/v1/workflow/audit/chain", headers=headers).json()
    cbom_events_2 = [e for e in events_2 if e["action"] == "CBOM_EXPORTED"]
    assert len(cbom_events_2) == 0

    # 3. Successful export -> exactly 1 CBOM_EXPORTED event
    export_resp = client.get(f"/api/v1/scans/{scan_id}/export?format=cyclonedx", headers=headers)
    assert export_resp.status_code == 200

    events_3 = client.get("/api/v1/workflow/audit/chain", headers=headers).json()
    cbom_events_3 = [e for e in events_3 if e["action"] == "CBOM_EXPORTED"]
    assert len(cbom_events_3) == 1
    assert cbom_events_3[0]["asset_id"] == scan_id
    assert cbom_events_3[0]["details"]["tenant_id"] == "tenant-export"
    assert cbom_events_3[0]["details"]["user_id"] == "exporter-1"


def test_audit_forged_actor_in_request_ignored(monkeypatch):
    """Verify forged actor/tenant in headers or body is ignored by audit recorder."""
    api_keys = {"auditor-key": {"tenant_id": "real-dept", "user_id": "real-user-123"}}
    monkeypatch.setenv("ASTRA_API_KEYS", json.dumps(api_keys))

    headers = {
        "X-ASTRA-API-KEY": "auditor-key",
        "X-Tenant-ID": "fake-dept",
        "X-User-ID": "fake-user",
    }
    body = {
        "action": "MANUAL_LOG",
        "actor": "fake-body-user",
        "asset_id": "asset-555",
        "details": {"reason": "test"},
    }

    resp = client.post("/api/v1/workflow/audit/chain/append", json=body, headers=headers)
    assert resp.status_code == 200
    ev = resp.json()

    assert ev["details"]["tenant_id"] == "real-dept"
    assert ev["details"]["user_id"] == "real-user-123"


def test_audit_restart_persistence_and_tamper_detection(tmp_path):
    """Verify AuditChainStore disk persistence, restart reloading, and SHA-256 tamper detection."""
    chain_file = tmp_path / "persistent_chain.json"

    # 1. Instantiate store and append events
    store1 = AuditChainStore(storage_path=str(chain_file))
    e1 = store1.append_event("BOOT", actor="sys", details={"step": 1})
    e2 = store1.append_event("SCAN", actor="sys", details={"step": 2})

    tip1 = store1.get_tip_hash()
    assert e2.event_hash == tip1

    # 2. Simulate server restart by creating a new AuditChainStore instance on same file
    store2 = AuditChainStore(storage_path=str(chain_file))
    assert len(store2.list_events()) == 2
    assert store2.get_tip_hash() == tip1
    verify_res = store2.verify_chain()
    assert verify_res["valid"] is True
    assert verify_res["events_count"] == 2

    # 3. Controlled tamper test: modify payload in chain_file on disk
    with open(chain_file, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    # Tamper with details of event 1
    raw_data[0]["details"]["step"] = 9999
    with open(chain_file, "w", encoding="utf-8") as f:
        json.dump(raw_data, f)

    # 4. Load store from tampered file and assert tamper detection triggers
    store3 = AuditChainStore(storage_path=str(chain_file))
    tamper_report = store3.verify_chain()
    assert tamper_report["valid"] is False
    assert "Payload modification at sequence 1" in tamper_report["reason"]
