"""ASTRA - Worker 03 Comprehensive Test Suite (MVP-01, MVP-02, MVP-03).

Validates transparent risk model, Mosca theorem calculations (X + Y > Z),
candidate migration backlog generation, dated NIST citations, scenario sensitivity,
and alert fatigue reduction over flat baseline (AC-07, AC-08, AC-10, AC-12).
"""

import uuid
from pathlib import Path
import pytest

from app.discovery.models import (
    ClaimType,
    ConfidenceBand,
    EvidenceState,
    Observation,
    SourceKind,
)
from app.risk.backlog import BacklogBuilder, MigrationBacklog, MigrationTask
from app.risk.models import (
    BusinessCriticality,
    ContextFactors,
    ExposureScope,
    RiskEvaluation,
    RiskScenario,
    UrgencyLevel,
)
from app.risk.scenarios import BaselineComparison, ScenarioAnalyzer
from app.risk.scorer import RiskScorer
from app.risk.taxonomy import lookup_algorithm_profile


def make_test_obs(algorithm: str, purpose: str = "KEY_EXCHANGE", path: str = "src/app.py") -> Observation:
    """Helper to construct synthetic observation."""
    return Observation(
        observation_id=str(uuid.uuid4()),
        scan_id="scan-risk-test",
        candidate_asset_id=f"asset-{algorithm.lower()}",
        claim_type=ClaimType.ALGORITHM_USE,
        source_kind=SourceKind.SOURCE_CODE,
        algorithm=algorithm,
        purpose=purpose,
        relative_path=path,
        start_line=10,
        evidence_digest="sha256dummy",
        sanitized_excerpt=f"{algorithm} usage",
        detector_id="det-test",
        ruleset_version="2026.10-nist-pqc",
        confidence=ConfidenceBand.CONFIRMED,
        confidence_rationale="test",
        state=EvidenceState.OBSERVED,
    )


# ==============================================================================
# Worker 03 MVP-01 Tests: Transparent Risk Model & Mosca Calculations (AC-07)
# ==============================================================================

def test_mosca_deadline_violation_triggers_critical_urgency():
    """Verify AC-07: If X (shelf life) + Y (migration) > Z (quantum horizon), mark CRITICAL."""
    # Data must stay confidential for 10 years, migration takes 3 years (total 13 yrs).
    # CRQC expected in 8 years (Z = 8). 13 > 8 -> Violates Mosca condition!
    ctx = ContextFactors(
        data_shelf_life_years=10.0,
        migration_duration_years=3.0,
        exposure=ExposureScope.PUBLIC_FACING,
        criticality=BusinessCriticality.HIGH_IMPACT,
    )
    scenario = RiskScenario(quantum_threat_horizon_years=8.0)

    obs = make_test_obs("RSA-2048")
    scorer = RiskScorer(scenario=scenario)
    eval_res = scorer.evaluate_observation(obs, ctx)

    assert eval_res.mosca_condition_violated is True
    assert eval_res.mosca_slack_years == -5.0  # 8 - 13 = -5
    assert eval_res.urgency == UrgencyLevel.CRITICAL
    assert "RC_MOSCA_DEADLINE_VIOLATED_SNDL_RISK" in eval_res.reason_codes
    assert eval_res.risk_score >= 80.0


def test_mosca_safe_slack_for_short_lived_data():
    """Verify AC-07: If data lifetime is short, Mosca condition is satisfied (slack > 0)."""
    # Shelf life 1 yr + migration 1 yr = 2 yrs < 8 yrs horizon
    ctx = ContextFactors(
        data_shelf_life_years=1.0,
        migration_duration_years=1.0,
        exposure=ExposureScope.INTERNAL_SHARED,
        criticality=BusinessCriticality.MODERATE,
    )
    scenario = RiskScenario(quantum_threat_horizon_years=8.0)

    obs = make_test_obs("RSA-2048")
    scorer = RiskScorer(scenario=scenario)
    eval_res = scorer.evaluate_observation(obs, ctx)

    assert eval_res.mosca_condition_violated is False
    assert eval_res.mosca_slack_years == 6.0  # 8 - 2 = 6
    assert eval_res.urgency != UrgencyLevel.CRITICAL


def test_broken_legacy_algorithm_is_always_critical():
    """Verify AC-07: MD5 and DES are always flagged CRITICAL regardless of quantum horizon."""
    obs = make_test_obs("MD5", purpose="HASHING")
    scorer = RiskScorer()
    eval_res = scorer.evaluate_observation(obs, ContextFactors())

    assert eval_res.urgency == UrgencyLevel.CRITICAL
    assert "RC_ALGORITHM_BROKEN_LEGACY" in eval_res.reason_codes
    assert eval_res.risk_score >= 70.0


def test_factor_contributions_transparency():
    """Verify AC-07: Factor contributions provide explainable breakdown summing to ~100%."""
    obs = make_test_obs("ECDSA", purpose="SIGNATURE")
    scorer = RiskScorer()
    eval_res = scorer.evaluate_observation(obs, ContextFactors())

    assert "algorithm_vulnerability" in eval_res.factor_contributions
    assert "operational_exposure" in eval_res.factor_contributions
    assert "business_criticality" in eval_res.factor_contributions

    total_percentage = sum(eval_res.factor_contributions.values())
    assert 98.0 <= total_percentage <= 102.0  # Accounting for rounding


# ==============================================================================
# Worker 03 MVP-02 Tests: Candidate Mapping & Migration Backlog (AC-08)
# ==============================================================================

def test_dated_pqc_mapping_for_rsa():
    """Verify AC-08: RSA-2048 maps to NIST FIPS 203 (ML-KEM-768) with dated reference."""
    profile = lookup_algorithm_profile("RSA-2048")
    assert profile.migration_candidate is not None

    cand = profile.migration_candidate
    assert "ML-KEM-768" in cand.target_standard_algorithm
    assert "FIPS 203" in cand.target_standard_ref
    assert "2024" in cand.target_standard_ref
    assert len(cand.compatibility_gaps) > 0  # Mentions key/ciphertext expansion


def test_dated_pqc_mapping_for_ecdsa():
    """Verify AC-08: ECDSA maps to NIST FIPS 204 (ML-DSA) with signature size warnings."""
    profile = lookup_algorithm_profile("ECDSA")
    assert profile.migration_candidate is not None

    cand = profile.migration_candidate
    assert "ML-DSA" in cand.target_standard_algorithm
    assert "FIPS 204" in cand.target_standard_ref
    assert any("signature size" in gap.lower() for gap in cand.compatibility_gaps)


def test_backlog_builder_priority_sorting():
    """Verify AC-08: Backlog sorts tasks with highest composite risk score first."""
    obs_list = [
        make_test_obs("SHA-256", purpose="HASHING", path="src/secure.py"),
        make_test_obs("MD5", purpose="HASHING", path="src/legacy.py"),
        make_test_obs("RSA-2048", purpose="KEY_EXCHANGE", path="src/auth.py"),
    ]

    context_map = {
        "src/auth.py": ContextFactors(
            data_shelf_life_years=15.0,  # Long-lived confidential auth
            exposure=ExposureScope.PUBLIC_FACING,
            criticality=BusinessCriticality.MISSION_CRITICAL,
        ),
        "src/legacy.py": ContextFactors(
            exposure=ExposureScope.INTERNAL_SHARED,
        ),
    }

    builder = BacklogBuilder()
    backlog = builder.generate_backlog(obs_list, "scan-test-01", context_map)

    assert backlog.total_tasks == 3
    # Top task should be either the broken MD5 or the critical long-lived RSA-2048
    top_task = backlog.tasks[0]
    assert top_task.priority == UrgencyLevel.CRITICAL
    assert top_task.composite_risk_score >= backlog.tasks[1].composite_risk_score
    assert backlog.tasks[1].composite_risk_score >= backlog.tasks[2].composite_risk_score


# ==============================================================================
# Worker 03 MVP-03 Tests: Scenario Sensitivity & Baseline Comparison (AC-12)
# ==============================================================================

def test_scenario_sensitivity_horizon_slider():
    """Verify AC-12: Adjusting CRQC horizon slider produces explainable priority shift."""
    obs_list = [
        make_test_obs("RSA-2048", purpose="KEY_EXCHANGE", path="src/api.py"),
    ]
    # Data lifetime 6 yrs + migration 2 yrs = 8 yrs
    ctx_map = {
        "src/api.py": ContextFactors(
            data_shelf_life_years=6.0,
            migration_duration_years=2.0,
        )
    }

    scenario_lenient = RiskScenario(scenario_id="horizon-15y", quantum_threat_horizon_years=15.0)
    scenario_urgent = RiskScenario(scenario_id="horizon-5y", quantum_threat_horizon_years=5.0)

    shifts = ScenarioAnalyzer.compare_scenarios(
        observations=obs_list,
        baseline_scenario=scenario_lenient,
        target_scenario=scenario_urgent,
        context_map=ctx_map,
    )

    assert len(shifts) == 1
    shift = shifts[0]
    assert shift.scenario_score > shift.baseline_score
    assert shift.scenario_urgency == UrgencyLevel.CRITICAL
    assert "Mosca slack" in shift.shift_explanation


def test_baseline_comparison_reduces_alert_fatigue():
    """Verify AC-12: Contextual risk eliminates alert fatigue compared to flat severity."""
    obs_list = [
        # Internal test files with low exposure / dev criticality
        make_test_obs("RSA-2048", path="tests/mock_rsa.py"),
        make_test_obs("ECDSA", path="scratch/test_sign.py"),
        # Genuine production public service
        make_test_obs("RSA-2048", path="src/prod_gateway.py"),
    ]

    ctx_map = {
        "tests/mock_rsa.py": ContextFactors(
            exposure=ExposureScope.BUILD_OR_TEST,
            criticality=BusinessCriticality.DEVELOPMENT,
            data_shelf_life_years=0.1,
        ),
        "scratch/test_sign.py": ContextFactors(
            exposure=ExposureScope.BUILD_OR_TEST,
            criticality=BusinessCriticality.DEVELOPMENT,
            data_shelf_life_years=0.1,
        ),
        "src/prod_gateway.py": ContextFactors(
            exposure=ExposureScope.PUBLIC_FACING,
            criticality=BusinessCriticality.MISSION_CRITICAL,
            data_shelf_life_years=10.0,
        ),
    }

    comparison = ScenarioAnalyzer.compare_against_flat_baseline(
        observations=obs_list,
        context_map=ctx_map,
    )

    # Flat severity flags all 3 assets because all have RSA/ECDSA
    assert comparison.flat_high_critical_count == 3
    # Contextual prioritization only flags prod_gateway.py as critical/high!
    assert comparison.contextual_high_critical_count == 1
    assert comparison.alert_reduction_percentage > 50.0
