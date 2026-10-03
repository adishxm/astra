"""ASTRA - Scenario Sensitivity & Baseline Comparison (Worker 03 - MVP-03).

Provides assumption slider controls, sensitivity analysis, flat-severity baseline
comparison, and auditable risk overrides (AC-07, AC-08, AC-10, AC-12).
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from app.discovery.models import Observation
from app.risk.backlog import BacklogBuilder, MigrationBacklog, MigrationTask
from app.risk.models import (
    ContextFactors,
    RiskScenario,
    UrgencyLevel,
)
from app.risk.scorer import RiskScorer


class RiskOverrideRecord(BaseModel):
    """Auditable human override record for an asset's risk or priority."""

    asset_id: str
    original_risk_score: float
    overridden_risk_score: float
    original_urgency: UrgencyLevel
    overridden_urgency: UrgencyLevel
    actor: str = Field(..., description="User or role who authorized the override")
    rationale: str = Field(..., description="Justification for manual risk modification")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SensitivityShift(BaseModel):
    """Summary of how asset priorities shifted under a scenario parameter change."""

    asset_id: str
    algorithm: str
    baseline_score: float
    scenario_score: float
    baseline_urgency: UrgencyLevel
    scenario_urgency: UrgencyLevel
    shift_explanation: str


class BaselineComparison(BaseModel):
    """Comparison between contextual ASTRA prioritization and naive flat severity."""

    total_assets: int
    flat_high_critical_count: int = Field(..., description="Count of assets flagged high/critical by flat severity")
    contextual_high_critical_count: int = Field(..., description="Count of assets flagged high/critical by ASTRA")
    alert_reduction_percentage: float = Field(..., description="Reduction in alert fatigue")
    rationale: str


class ScenarioAnalyzer:
    """Evaluates how changing scenario assumptions impacts risk and queue priority."""

    @staticmethod
    def compare_scenarios(
        observations: List[Observation],
        baseline_scenario: RiskScenario,
        target_scenario: RiskScenario,
        context_map: Optional[Dict[str, ContextFactors]] = None,
    ) -> List[SensitivityShift]:
        """Compute sensitivity deltas across two scenario configurations."""
        ctx_map = context_map or {}
        scorer_base = RiskScorer(scenario=baseline_scenario)
        scorer_target = RiskScorer(scenario=target_scenario)

        shifts: List[SensitivityShift] = []

        for obs in observations:
            ctx = ctx_map.get(obs.relative_path, ContextFactors())
            r_base = scorer_base.evaluate_observation(obs, ctx)
            r_target = scorer_target.evaluate_observation(obs, ctx)

            if r_base.urgency != r_target.urgency or abs(r_base.risk_score - r_target.risk_score) >= 5.0:
                explanation = (
                    f"Horizon changed from {baseline_scenario.quantum_threat_horizon_years}y to "
                    f"{target_scenario.quantum_threat_horizon_years}y. "
                    f"Mosca slack shifted from {r_base.mosca_slack_years}y to {r_target.mosca_slack_years}y."
                )
                shifts.append(
                    SensitivityShift(
                        asset_id=obs.candidate_asset_id,
                        algorithm=obs.algorithm or "UNKNOWN",
                        baseline_score=r_base.risk_score,
                        scenario_score=r_target.risk_score,
                        baseline_urgency=r_base.urgency,
                        scenario_urgency=r_target.urgency,
                        shift_explanation=explanation,
                    )
                )

        return shifts

    @staticmethod
    def compare_against_flat_baseline(
        observations: List[Observation],
        scenario: Optional[RiskScenario] = None,
        context_map: Optional[Dict[str, ContextFactors]] = None,
    ) -> BaselineComparison:
        """Compare contextual ASTRA scoring against flat regex-only algorithm severity."""
        ctx_map = context_map or {}
        scorer = RiskScorer(scenario=scenario or RiskScenario())

        flat_urgent = 0
        context_urgent = 0

        for obs in observations:
            algo = (obs.algorithm or "").upper()
            # Naive flat baseline: all RSA, ECC, MD5, DES are indiscriminately marked critical/high
            if any(k in algo for k in ("RSA", "ECDSA", "ECC", "MD5", "DES", "RC4")):
                flat_urgent += 1

            ctx = ctx_map.get(obs.relative_path, ContextFactors())
            eval_res = scorer.evaluate_observation(obs, ctx)
            if eval_res.urgency in (UrgencyLevel.CRITICAL, UrgencyLevel.HIGH):
                context_urgent += 1

        total = len(observations)
        reduction = 0.0
        if flat_urgent > 0:
            reduction = round(((flat_urgent - context_urgent) / flat_urgent) * 100, 2)

        return BaselineComparison(
            total_assets=total,
            flat_high_critical_count=flat_urgent,
            contextual_high_critical_count=context_urgent,
            alert_reduction_percentage=max(0.0, reduction),
            rationale=(
                f"Contextual prioritization evaluated exposure, shelf-life, and Mosca slack, "
                f"reducing immediate urgent alerts from {flat_urgent} to {context_urgent} ({reduction}% reduction)."
            ),
        )
