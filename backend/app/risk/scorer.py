"""ASTRA - Deterministic Mosca-Aware Risk Scorer (Worker 03 - MVP-01).

Computes explainable, multi-factor risk scores, Mosca horizon evaluations,
and factor contributions adhering to AC-07.
"""

from typing import Dict, List, Optional, Tuple

from app.core.config import RULESET_VERSION
from app.discovery.models import Observation
from app.risk.models import (
    ContextFactors,
    RiskEvaluation,
    RiskScenario,
    UrgencyLevel,
)
from app.risk.taxonomy import lookup_algorithm_profile


class RiskScorer:
    """Calculates deterministic risk scores and Mosca theorem horizons."""

    def __init__(self, scenario: Optional[RiskScenario] = None):
        self.scenario = scenario or RiskScenario()

    def evaluate_observation(
        self,
        observation: Observation,
        context: Optional[ContextFactors] = None,
    ) -> RiskEvaluation:
        """Evaluate contextual risk for an individual cryptographic observation."""
        ctx = context or ContextFactors()
        algo_name = observation.algorithm or "UNKNOWN"
        profile = lookup_algorithm_profile(algo_name)

        # 1. Base Algorithm Vulnerability Score (0 to 100)
        algo_score = profile.base_vulnerability_score * 10.0

        # 2. Mosca Theorem Calculation: X + Y > Z
        # X: data shelf life, Y: migration time, Z: quantum threat horizon
        x = ctx.data_shelf_life_years
        y = ctx.migration_duration_years
        z = self.scenario.quantum_threat_horizon_years

        exposure_duration = x + y
        mosca_violated = (exposure_duration > z) and (profile.vulnerability_tier in ("QUANTUM_VULNERABLE", "BROKEN"))
        mosca_slack = round(z - exposure_duration, 2)

        # Mosca Urgency Score (0 to 100)
        if mosca_violated:
            # The more severe the overdue slack, the closer to 100
            overdue = exposure_duration - z
            mosca_score = min(100.0, 75.0 + (overdue * 5.0))
        elif profile.vulnerability_tier in ("QUANTUM_VULNERABLE", "BROKEN"):
            # Not yet violated, but positive risk depending on how close slack is
            slack_ratio = max(0.0, min(1.0, 1.0 - (mosca_slack / max(1.0, z))))
            mosca_score = slack_ratio * 70.0
        else:
            # Post-quantum or classical resistant
            mosca_score = 0.0

        # 3. Exposure Score (0 to 100)
        exposure_score = (ctx.exposure.value / 5.0) * 100.0

        # 4. Criticality Score (0 to 100)
        criticality_score = (ctx.criticality.value / 5.0) * 100.0

        # 5. Composite Weighted Score
        w_algo = self.scenario.weight_quantum_vulnerability
        w_mosca = self.scenario.weight_mosca_urgency
        w_exp = self.scenario.weight_exposure
        w_crit = self.scenario.weight_criticality

        raw_score = (
            (algo_score * w_algo)
            + (mosca_score * w_mosca)
            + (exposure_score * w_exp)
            + (criticality_score * w_crit)
        )
        composite_score = round(max(0.0, min(100.0, raw_score)), 2)

        # Reason Codes & Urgency Tier Calibration
        reason_codes: List[str] = []

        if profile.vulnerability_tier == "BROKEN":
            urgency = UrgencyLevel.CRITICAL
            reason_codes.append("RC_ALGORITHM_BROKEN_LEGACY")
        elif mosca_violated:
            urgency = UrgencyLevel.CRITICAL
            reason_codes.append("RC_MOSCA_DEADLINE_VIOLATED_SNDL_RISK")
        elif composite_score >= 65.0:
            urgency = UrgencyLevel.HIGH
            reason_codes.append("RC_HIGH_COMPOSITE_RISK")
        elif composite_score >= 40.0:
            urgency = UrgencyLevel.MEDIUM
            reason_codes.append("RC_MODERATE_MIGRATION_PRIORITY")
        elif composite_score >= 15.0:
            urgency = UrgencyLevel.LOW
            reason_codes.append("RC_LOW_RISK_CLASSICAL")
        else:
            urgency = UrgencyLevel.INFORMATIONAL
            reason_codes.append("RC_POST_QUANTUM_OR_SECURE")

        if ctx.exposure.value >= 4:
            reason_codes.append("RC_PUBLIC_OR_PARTNER_FACING")
        if ctx.criticality.value >= 4:
            reason_codes.append("RC_HIGH_BUSINESS_CRITICALITY")

        # Factor Contributions breakdown (percentages)
        factor_contribs = {}
        if composite_score > 0:
            factor_contribs = {
                "algorithm_vulnerability": round((algo_score * w_algo / composite_score) * 100, 1),
                "mosca_horizon_urgency": round((mosca_score * w_mosca / composite_score) * 100, 1),
                "operational_exposure": round((exposure_score * w_exp / composite_score) * 100, 1),
                "business_criticality": round((criticality_score * w_crit / composite_score) * 100, 1),
            }

        recommendation_dict = None
        if profile.migration_candidate:
            recommendation_dict = profile.migration_candidate.model_dump()

        return RiskEvaluation(
            asset_id=observation.candidate_asset_id,
            algorithm=algo_name,
            purpose=observation.purpose or "CRYPTOGRAPHIC_OPERATION",
            risk_score=composite_score,
            urgency=urgency,
            mosca_condition_violated=mosca_violated,
            mosca_slack_years=mosca_slack,
            factor_contributions=factor_contribs,
            reason_codes=reason_codes,
            context=ctx,
            confidence_source="OWNER_SUPPLIED" if ctx.is_user_enriched else "DEFAULT_ASSUMPTION",
            recommendation=recommendation_dict,
            assumptions_applied={
                "scenario_id": self.scenario.scenario_id,
                "quantum_threat_horizon_years": z,
                "data_shelf_life_years": x,
                "migration_duration_years": y,
                "context_source": "OWNER_SUPPLIED" if ctx.is_user_enriched else "DEFAULT_ASSUMPTION",
                "ruleset_version": RULESET_VERSION,
                "scenario_caveat": "Mosca urgency reflects scenario simulation assumptions (X + Y > Z) and baseline defaults until enriched by asset owner.",
            },
        )
