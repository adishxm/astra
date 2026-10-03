"""Tests for MVP hardening capabilities."""

from app.web_workflow.hardening import (
    AirGappedBundleManager,
    LocalReviewEventLog,
    ProductionHealthEvaluator,
    LocalReviewEvent,
)

def test_bundle_manager_disabled():
    res = AirGappedBundleManager.verify_bundle({}, b"data", "key")
    assert not res["valid"]

def test_production_health_evaluator_unknown():
    res = ProductionHealthEvaluator.evaluate_readiness()
    assert not res["is_production_ready"]
