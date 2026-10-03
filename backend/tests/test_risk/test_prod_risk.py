"""
Production test suite for Worker 03:
- PROD-01: Dependency-Aware Constrained Migration Roadmap & Cycle Detection
- PROD-02: Security-Property Invariant Preservation & Rollback Safety Assurance
"""

import pytest
from app.risk.models import UrgencyLevel
from app.risk.roadmap import (
    DependencyRoadmapEngine,
    MigrationDependencyNode,
)
from app.risk.assurance import (
    SecurityInvariantAssuranceEngine,
    CandidateTransition,
    SecurityProperty,
)


def test_dependency_roadmap_topological_phases():
    """Verify topological scheduling creates phased migration roadmap."""
    engine = DependencyRoadmapEngine()

    # Asset 1 is foundational crypto lib (e.g. OpenSSL/liboqs)
    # Asset 2 is an internal service using Asset 1
    # Asset 3 is an edge API using Asset 2
    nodes = [
        MigrationDependencyNode(
            asset_id="lib-openssl",
            algorithm="RSA-2048",
            risk_score=75.0,
            urgency=UrgencyLevel.HIGH,
            target_pqc_algorithm="ML-KEM-768",
            dependencies=[],
            estimated_effort_days=10.0,
        ),
        MigrationDependencyNode(
            asset_id="svc-auth",
            algorithm="RSA-2048",
            risk_score=85.0,
            urgency=UrgencyLevel.CRITICAL,
            target_pqc_algorithm="ML-KEM-768",
            dependencies=["lib-openssl"],
            estimated_effort_days=5.0,
        ),
        MigrationDependencyNode(
            asset_id="edge-gateway",
            algorithm="ECDSA",
            risk_score=90.0,
            urgency=UrgencyLevel.CRITICAL,
            target_pqc_algorithm="ML-DSA-65",
            dependencies=["svc-auth"],
            estimated_effort_days=3.0,
        ),
        MigrationDependencyNode(
            asset_id="independent-db",
            algorithm="AES-256",
            risk_score=40.0,
            urgency=UrgencyLevel.LOW,
            target_pqc_algorithm="AES-256",
            dependencies=[],
            estimated_effort_days=2.0,
        ),
    ]

    roadmap = engine.compute_roadmap(nodes)

    assert roadmap.has_cycles is False
    assert roadmap.total_assets == 4
    assert len(roadmap.phases) == 3

    # Phase 1 should contain lib-openssl and independent-db (0 dependencies)
    assert set(roadmap.phases[0].asset_ids) == {"lib-openssl", "independent-db"}
    # Phase 2 should contain svc-auth (dep on lib-openssl)
    assert roadmap.phases[1].asset_ids == ["svc-auth"]
    # Phase 3 should contain edge-gateway (dep on svc-auth)
    assert roadmap.phases[2].asset_ids == ["edge-gateway"]

    # Verify bottleneck identification (lib-openssl unblocks 2 downstream items)
    assert len(roadmap.bottlenecks) >= 1
    top_bottleneck = roadmap.bottlenecks[0]
    assert top_bottleneck["asset_id"] == "lib-openssl"
    assert top_bottleneck["downstream_unblocked_count"] == 2


def test_dependency_roadmap_cycle_detection():
    """Verify cyclic dependency detection prevents invalid migration schedules."""
    engine = DependencyRoadmapEngine()

    cyclic_nodes = [
        MigrationDependencyNode(
            asset_id="node-a",
            algorithm="RSA-2048",
            risk_score=80.0,
            urgency=UrgencyLevel.HIGH,
            target_pqc_algorithm="ML-KEM-768",
            dependencies=["node-b"],
        ),
        MigrationDependencyNode(
            asset_id="node-b",
            algorithm="RSA-2048",
            risk_score=80.0,
            urgency=UrgencyLevel.HIGH,
            target_pqc_algorithm="ML-KEM-768",
            dependencies=["node-a"],
        ),
    ]

    roadmap = engine.compute_roadmap(cyclic_nodes)

    assert roadmap.has_cycles is True
    assert len(roadmap.cycle_nodes) >= 1
    assert "CRITICAL" in roadmap.roadmap_summary
    assert len(roadmap.phases) == 0


def test_security_invariant_preservation():
    """Verify audit correctly verifies property preservation for sound PQC migrations."""
    engine = SecurityInvariantAssuranceEngine()

    # Sound transition: RSA-2048 (Encryption) -> ML-KEM-768 under TLSv1.3
    transition = CandidateTransition(
        asset_id="ast-tls-kem",
        legacy_algorithm="RSA-2048",
        purpose="KEY_EXCHANGE",
        candidate_algorithm="ML-KEM-768",
        protocol_context="TLSv1.3",
        fallback_allowed=False,
    )
    result = engine.audit_transition(transition)

    assert result.is_sound is True
    assert SecurityProperty.CONFIDENTIALITY in result.preserved_properties
    assert SecurityProperty.QUANTUM_RESISTANCE in result.preserved_properties
    assert len(result.missing_properties) == 0
    assert result.downgrade_vulnerable is False
    assert result.rollback_safe is True
    assert result.assurance_score >= 90.0


def test_security_invariant_downgrade_and_insecure_rollback():
    """Verify detection of protocol downgrade vulnerability and insecure classical rollback."""
    engine = SecurityInvariantAssuranceEngine()

    # Insecure transition: TLSv1.0 (downgrade vulnerable) + fallback to broken DES
    bad_transition = CandidateTransition(
        asset_id="ast-legacy-rollback",
        legacy_algorithm="RSA-2048",
        purpose="KEY_EXCHANGE",
        candidate_algorithm="ML-KEM-768",
        protocol_context="TLSv1.0",
        fallback_allowed=True,
        fallback_algorithm="DES",
    )
    result = engine.audit_transition(bad_transition)

    assert result.is_sound is False
    assert result.downgrade_vulnerable is True
    assert result.rollback_safe is False
    assert any("downgrade" in f.lower() for f in result.findings)
    assert any("insecure rollback" in f.lower() for f in result.findings)
    assert result.assurance_score < 60.0
