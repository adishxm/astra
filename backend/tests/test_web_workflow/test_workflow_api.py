"""Tests for Worker 04 Web Workflow."""

from fastapi.testclient import TestClient
from fastapi import FastAPI
from app.web_workflow.router import router

app = FastAPI()
app.include_router(router)
client = TestClient(app)

def test_get_evidence_drilldown():
    response = client.get("/api/v1/workflow/evidence/asset-123")
    assert response.status_code == 200
    assert response.json() == []

def test_create_audit_record():
    payload = {
        "reason": "Test review",
        "previous_value": "UNKNOWN",
        "new_value": "VERIFIED",
        "linked_evidence": "canon-1"
    }
    response = client.post("/api/v1/workflow/audit", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["reason"] == "Test review"
    assert data["actor"] is None

def test_create_audit_record_missing_reason():
    payload = {
        "reason": "",
        "previous_value": "UNKNOWN",
        "new_value": "VERIFIED",
        "linked_evidence": "canon-1"
    }
    response = client.post("/api/v1/workflow/audit", json=payload)
    assert response.status_code == 400

def test_get_export():
    response = client.get("/api/v1/workflow/export")
    assert response.status_code == 200
    data = response.json()
    assert data["profile"] == "Astra Project Export Draft"
