"""ASTRA - Actionable Migration Backlog Generator (Worker 03 - MVP-02).

Transforms cryptographic observations and risk scores into prioritized,
advisory migration work items citing dated standards and operational gaps (AC-08).
"""

import uuid
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from app.discovery.models import Observation
from app.risk.models import (
    ContextFactors,
    RiskEvaluation,
    RiskScenario,
    UrgencyLevel,
)
from app.risk.scorer import RiskScorer
from app.risk.taxonomy import MigrationCandidate, lookup_algorithm_profile


class MigrationTask(BaseModel):
    """Actionable, advisory work item for cryptographic migration."""

    task_id: str = Field(..., description="Unique task identifier")
    asset_id: str = Field(..., description="Target asset identifier")
    relative_path: str = Field(..., description="Source code or config file path")
    start_line: Optional[int] = Field(None, description="Line number of usage")

    current_algorithm: str = Field(..., description="Current cryptographic algorithm in use")
    purpose: str = Field(..., description="Identified purpose (e.g. KEY_EXCHANGE, SIGNATURE)")

    priority: UrgencyLevel = Field(..., description="Calibrated urgency tier")
    composite_risk_score: float = Field(..., ge=0.0, le=100.0)
    mosca_deadline_passed: bool

    # Candidate Migration Pathway
    target_pqc_algorithm: str = Field(..., description="Recommended NIST standardized PQC algorithm")
    target_hybrid_algorithm: Optional[str] = Field(None, description="Recommended hybrid interim algorithm")
    dated_standard_ref: str = Field(..., description="Official dated authority reference")
    compatibility_gaps: List[str] = Field(default_factory=list, description="Known operational caveats")
    recommended_action: str = Field(..., description="Concrete step for the development team")

    review_owner: str = Field(default="Security Architecture & Crypto Team")
    status: str = Field(default="OPEN", description="OPEN, IN_REVIEW, ACCEPTED, OVERRIDDEN")
    reason_codes: List[str] = Field(default_factory=list)


class MigrationBacklog(BaseModel):
    """Prioritized queue of advisory migration work items."""

    backlog_id: str = Field(..., description="Backlog run identifier")
    scan_id: str = Field(..., description="Source scan run identifier")
    scenario_id: str = Field(..., description="Scenario assumptions applied")

    total_tasks: int = Field(default=0, ge=0)
    critical_count: int = Field(default=0, ge=0)
    high_count: int = Field(default=0, ge=0)
    medium_count: int = Field(default=0, ge=0)
    low_count: int = Field(default=0, ge=0)

    tasks: List[MigrationTask] = Field(
        default_factory=list, description="Prioritized work items sorted by risk score descending"
    )


class BacklogBuilder:
    """Builds prioritized migration backlog from observations and contextual inputs."""

    def __init__(self, scenario: Optional[RiskScenario] = None):
        self.scenario = scenario or RiskScenario()
        self.scorer = RiskScorer(scenario=self.scenario)

    def generate_backlog(
        self,
        observations: List[Observation],
        scan_id: str,
        context_map: Optional[Dict[str, ContextFactors]] = None,
    ) -> MigrationBacklog:
        """Create prioritized migration backlog from observations."""
        ctx_map = context_map or {}
        tasks: List[MigrationTask] = []

        for obs in observations:
            # Skip non-crypto or informational artifacts
            algo = obs.algorithm or "UNKNOWN"
            profile = lookup_algorithm_profile(algo)

            ctx = ctx_map.get(obs.relative_path, ContextFactors())
            risk_eval = self.scorer.evaluate_observation(obs, ctx)

            # Build migration task if migration candidate exists or risk is high
            candidate = profile.migration_candidate
            target_pqc = candidate.target_standard_algorithm if candidate else "N/A - Review with Cryptographer"
            target_hybrid = candidate.target_hybrid_algorithm if candidate else None
            dated_ref = candidate.target_standard_ref if candidate else profile.dated_source
            gaps = candidate.compatibility_gaps if candidate else []
            action = candidate.recommended_action if candidate else "Conduct cryptographic review"

            tasks.append(
                MigrationTask(
                    task_id=f"mig-{str(uuid.uuid4())[:8]}",
                    asset_id=obs.candidate_asset_id,
                    relative_path=obs.relative_path,
                    start_line=obs.start_line,
                    current_algorithm=algo,
                    purpose=obs.purpose or "CRYPTOGRAPHIC_PRIMITIVE",
                    priority=risk_eval.urgency,
                    composite_risk_score=risk_eval.risk_score,
                    mosca_deadline_passed=risk_eval.mosca_condition_violated,
                    target_pqc_algorithm=target_pqc,
                    target_hybrid_algorithm=target_hybrid,
                    dated_standard_ref=dated_ref,
                    compatibility_gaps=gaps,
                    recommended_action=action,
                    reason_codes=risk_eval.reason_codes,
                )
            )

        # Sort tasks by risk score descending (highest priority first)
        tasks.sort(key=lambda t: t.composite_risk_score, reverse=True)

        critical_c = len([t for t in tasks if t.priority == UrgencyLevel.CRITICAL])
        high_c = len([t for t in tasks if t.priority == UrgencyLevel.HIGH])
        medium_c = len([t for t in tasks if t.priority == UrgencyLevel.MEDIUM])
        low_c = len([t for t in tasks if t.priority in (UrgencyLevel.LOW, UrgencyLevel.INFORMATIONAL)])

        return MigrationBacklog(
            backlog_id=f"backlog-{str(uuid.uuid4())[:8]}",
            scan_id=scan_id,
            scenario_id=self.scenario.scenario_id,
            total_tasks=len(tasks),
            critical_count=critical_c,
            high_count=high_c,
            medium_count=medium_c,
            low_count=low_c,
            tasks=tasks,
        )
