"""ASTRA - Worker 04 Phase B Server-Persisted Audit Chain & Tenant Scoping Tests.

Verifies:
  1. AuditChainStore disk persistence to JSON, atomic writes, and SHA-256 tamper detection.
  2. Crash-resilience / server restart simulation preserving block height, hashes, and validity.
  3. Automatic emission of SCAN_INTAKE, CBOM_EXPORTED, and RISK_RECALCULATED audit events.
  4. Multi-tenant scoping and data isolation across scans, context updates, exports, and audit chains.
  5. REST API audit endpoints (/workflow/audit/chain/verify and /workflow/audit/chain/append).
"""

import io
import json
import os
import shutil
import tempfile
import zipfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.web_workflow.audit_store import AuditChainStore, GLOBAL_AUDIT_STORE
from app.web_workflow.hardening import ChainedAuditEvent
from app.services.scan_service import GLOBAL_SCAN_STORE, GLOBAL_SCAN_SERVICE

client = TestClient(app)


def create_minimal_crypto_zip() -> io.BytesIO:
    """Create a minimal zip containing cryptographic code for discovery intake."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(
            "crypto_app.py",
            "import hashlib\n"
            "from cryptography.hazmat.primitives.asymmetric import rsa\n"
            "key = rsa.generate_private_key(public_exponent=65537, key_size=2048)\n"
            "digest = hashlib.sha256(b'astra audit test').hexdigest()\n"
        )
    buf.seek(0)
    return buf


@pytest.fixture(autouse=True)
def clean_audit_and_scan_stores():
    """Isolate audit and scan stores before and after each test."""
    temp_dir = tempfile.mkdtemp(prefix="astra_test_phase_b_")
    audit_file = os.path.join(temp_dir, "audit_chain.json")
    scans_dir = os.path.join(temp_dir, "scans")

    # Point global stores to test directories
    old_audit_path = GLOBAL_AUDIT_STORE.file_path
    old_scan_dir = GLOBAL_SCAN_STORE.storage_dir

    test_audit_store = AuditChainStore(storage_path=audit_file)
    GLOBAL_AUDIT_STORE.file_path = Path(audit_file)
    GLOBAL_AUDIT_STORE._chain = test_audit_store._chain

    GLOBAL_SCAN_STORE.storage_dir = Path(scans_dir)
    GLOBAL_SCAN_STORE.storage_dir.mkdir(parents=True, exist_ok=True)
    GLOBAL_SCAN_STORE._memory_cache.clear()

    yield

    GLOBAL_AUDIT_STORE.file_path = old_audit_path
    GLOBAL_SCAN_STORE.storage_dir = old_scan_dir
    GLOBAL_SCAN_STORE._memory_cache.clear()
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_audit_chain_store_tamper_detection(tmp_path):
    """Test append, sequential SHA-256 hashing, disk persistence, and tamper detection."""
    store_file = tmp_path / "chain.json"
    store = AuditChainStore(storage_path=str(store_file))

    ev1 = store.append_event(
        action="SCAN_INTAKE",
        actor="system",
        asset_id="scan-101",
        tenant_id="tenant-x",
        details={"target": "repo1"},
    )
    assert ev1.sequence_num == 1
    assert ev1.prev_hash == "0" * 64
    assert len(ev1.event_hash) == 64

    ev2 = store.append_event(
        action="CBOM_EXPORTED",
        actor="auditor-alice",
        asset_id="scan-101",
        tenant_id="tenant-x",
        details={"format": "cyclonedx"},
    )
    assert ev2.sequence_num == 2
    assert ev2.prev_hash == ev1.event_hash

    # Verify chain is valid
    res = store.verify_chain()
    assert res["valid"] is True
    assert res["events_count"] == 2
    assert res["tip_hash"] == ev2.event_hash

    # Tamper with event 1 in file on disk
    with open(store_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    data[0]["details"]["target"] = "TAMPERED_REPO"
    with open(store_file, "w", encoding="utf-8") as f:
        json.dump(data, f)

    # Reload store from tampered file
    tampered_store = AuditChainStore(storage_path=str(store_file))
    tampered_res = tampered_store.verify_chain()
    assert tampered_res["valid"] is False
    assert "tamper_detected_at_sequence" in tampered_res


def test_audit_chain_store_persistence_across_restart(tmp_path):
    """Simulate server restart and verify full chain recovery from persistent disk JSON."""
    store_file = tmp_path / "persistent_audit.json"
    store_initial = AuditChainStore(storage_path=str(store_file))

    e1 = store_initial.append_event("BOOT", "init-agent", details={"ver": "1.0"})
    e2 = store_initial.append_event("CONFIG_LOAD", "init-agent", details={"mode": "airgap"})
    e3 = store_initial.append_event("POLICY_APPLY", "sec-lead", details={"preset": "CNSA_2_0"})

    tip_initial = store_initial.get_tip_hash()
    assert e3.event_hash == tip_initial

    # Simulate restart by instantiating a brand new store on the same disk path
    store_restarted = AuditChainStore(storage_path=str(store_file))
    assert len(store_restarted.list_events()) == 3
    assert store_restarted.get_tip_hash() == tip_initial

    verify_report = store_restarted.verify_chain()
    assert verify_report["valid"] is True
    assert verify_report["events_count"] == 3
    assert verify_report["tip_hash"] == tip_initial


def test_scan_workflow_auto_audit_events():
    """Verify that scanning, exporting CBOM, and enriching context auto-emit verified audit events."""
    zip_buf = create_minimal_crypto_zip()
    headers = {
        "X-Tenant-ID": "finance-division",
        "X-User-ID": "crypto-analyst-99",
    }

    # 1. Intake scan upload
    upload_resp = client.post(
        "/api/v1/scans/upload",
        files={"file": ("vault_crypto.zip", zip_buf, "application/zip")},
        headers=headers,
    )
    assert upload_resp.status_code == 200, upload_resp.text
    scan_id = upload_resp.json()["scan_id"]

    # 2. Check audit chain for SCAN_INTAKE
    audit_resp = client.get("/api/v1/workflow/audit/chain/verify", headers=headers)
    assert audit_resp.status_code == 200
    chain_data = audit_resp.json()
    assert chain_data["valid"] is True
    assert chain_data["events_count"] >= 1

    intake_events = [e for e in chain_data["events"] if e["action"] == "SCAN_INTAKE"]
    assert len(intake_events) == 1
    assert intake_events[0]["actor"] == "crypto-analyst-99"
    assert intake_events[0]["details"]["tenant_id"] == "finance-division"
    assert intake_events[0]["asset_id"] == scan_id

    # 3. Export CBOM and verify CBOM_EXPORTED event auto-emitted
    export_resp = client.get(f"/api/v1/scans/{scan_id}/export?format=cyclonedx", headers=headers)
    assert export_resp.status_code == 200
    assert export_resp.json()["bomFormat"] == "CycloneDX"

    audit_resp2 = client.get(f"/api/v1/workflow/audit/chain/verify?scan_id={scan_id}", headers=headers)
    chain_data2 = audit_resp2.json()
    export_events = [e for e in chain_data2["events"] if e["action"] == "CBOM_EXPORTED"]
    assert len(export_events) >= 1
    assert export_events[-1]["details"]["tenant_id"] == "finance-division"

    # 4. Enrich owner context and verify RISK_RECALCULATED event auto-emitted
    ctx_payload = {
        "data_shelf_life_years": 7.0,
        "migration_duration_years": 3.0,
        "exposure": 3,
        "criticality": 4,
    }
    enrich_resp = client.put(f"/api/v1/scans/{scan_id}/context", json=ctx_payload, headers=headers)
    assert enrich_resp.status_code == 200

    audit_resp3 = client.get(f"/api/v1/workflow/audit/chain/verify?scan_id={scan_id}", headers=headers)
    chain_data3 = audit_resp3.json()
    risk_events = [e for e in chain_data3["events"] if e["action"] == "RISK_RECALCULATED"]
    assert len(risk_events) == 1
    assert risk_events[0]["details"]["data_shelf_life_years"] == 7.0
    assert risk_events[0]["details"]["tenant_id"] == "finance-division"


def test_tenant_scoping_and_isolation():
    """Verify tenant isolation between Tenant Alpha and Tenant Beta."""
    alpha_headers = {"X-Tenant-ID": "tenant-alpha", "X-User-ID": "alice"}
    beta_headers = {"X-Tenant-ID": "tenant-beta", "X-User-ID": "bob"}

    # Upload scan for Alpha
    zip_alpha = create_minimal_crypto_zip()
    resp_a = client.post(
        "/api/v1/scans/upload",
        files={"file": ("alpha_repo.zip", zip_alpha, "application/zip")},
        headers=alpha_headers,
    )
    assert resp_a.status_code == 200
    scan_id_a = resp_a.json()["scan_id"]

    # Upload scan for Beta
    zip_beta = create_minimal_crypto_zip()
    resp_b = client.post(
        "/api/v1/scans/upload",
        files={"file": ("beta_repo.zip", zip_beta, "application/zip")},
        headers=beta_headers,
    )
    assert resp_b.status_code == 200
    scan_id_b = resp_b.json()["scan_id"]

    # Alpha lists scans -> sees only Alpha's scan
    list_a = client.get("/api/v1/scans", headers=alpha_headers).json()
    assert any(s["scan_id"] == scan_id_a for s in list_a)
    assert not any(s["scan_id"] == scan_id_b for s in list_a)

    # Beta lists scans -> sees only Beta's scan
    list_b = client.get("/api/v1/scans", headers=beta_headers).json()
    assert any(s["scan_id"] == scan_id_b for s in list_b)
    assert not any(s["scan_id"] == scan_id_a for s in list_b)

    # Cross-tenant access: Beta tries to read Alpha's scan -> 404
    cross_resp = client.get(f"/api/v1/scans/{scan_id_a}", headers=beta_headers)
    assert cross_resp.status_code == 404

    # Cross-tenant context update: Beta tries to update Alpha's context -> 404
    cross_ctx = client.put(
        f"/api/v1/scans/{scan_id_a}/context",
        json={"data_shelf_life_years": 10.0},
        headers=beta_headers,
    )
    assert cross_ctx.status_code == 404

    # Audit isolation: Beta querying audit chain should not see Alpha's scan events
    beta_audit = client.get("/api/v1/workflow/audit/chain/verify", headers=beta_headers).json()
    assert not any(e.get("asset_id") == scan_id_a for e in beta_audit.get("events", []))
    assert any(e.get("asset_id") == scan_id_b for e in beta_audit.get("events", []))


def test_manual_audit_append_endpoint():
    """Verify POST /api/v1/workflow/audit/chain/append creates tamper-evident audit links."""
    headers = {"X-Tenant-ID": "ops-compliance", "X-User-ID": "qa-lead"}
    append_payload = {
        "action": "PEER_REVIEW_APPROVED",
        "actor": "qa-lead",
        "asset_id": "asset-test-99",
        "details": {"reviewer": "Senior Cryptographer", "finding_status": "MITIGATED"},
    }

    append_resp = client.post(
        "/api/v1/workflow/audit/chain/append",
        json=append_payload,
        headers=headers,
    )
    assert append_resp.status_code == 200, append_resp.text
    data = append_resp.json()
    assert data["action"] == "PEER_REVIEW_APPROVED"
    assert data["details"]["tenant_id"] == "ops-compliance"
    chain_tip = data["event_hash"]

    # Verify it shows up in verify
    verify_resp = client.get("/api/v1/workflow/audit/chain/verify", headers=headers)
    assert verify_resp.status_code == 200
    v_data = verify_resp.json()
    assert v_data["valid"] is True
    assert v_data["tip_hash"] == chain_tip
