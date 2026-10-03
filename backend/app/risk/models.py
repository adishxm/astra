"""ASTRA - Risk Domain Models (Worker 03 - MVP-01).

Defines contextual risk factors, Mosca theorem horizons (X + Y > Z),
transparent factor contributions, and assumption-aware risk scores (AC-07).
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class UrgencyLevel(str, Enum):
    """Urgency tier based on quantum vulnerability and Mosca deadline."""

    CRITICAL = "CRITICAL"          # Mosca deadline exceeded (X + Y > Z) or broken algorithm
    HIGH = "HIGH"                  # Quantum-vulnerable with high exposure/criticality
    MEDIUM = "MEDIUM"              # Classical strong with moderate lifetime
    LOW = "LOW"                    # Internal or short-lived classical crypto
    INFORMATIONAL = "INFORMATIONAL" # Already PQC, clean, or documentation reference


class ExposureScope(int, Enum):
    """Network and operational exposure of the cryptographic asset."""

    PUBLIC_FACING = 5      # Internet-facing API, public TLS, client auth
    PARTNER_GATEWAY = 4    # B2B or cross-organization communication
    INTERNAL_SHARED = 3    # Microservice mesh or internal enterprise subnet
    LOCAL_ISOLATED = 2     # Localhost, daemon-internal, private storage
    BUILD_OR_TEST = 1      # Unit tests, synthetic fixtures, dev sandbox


class BusinessCriticality(int, Enum):
    """Business impact of compromised confidentiality or integrity."""

    MISSION_CRITICAL = 5   # Core banking, defense, patient telemetry, master root CA
    HIGH_IMPACT = 4        # User identity, billing, proprietary algorithms
    MODERATE = 3           # Standard business application, internal tools
    LOW = 2                # Non-sensitive telemetry, cached content
    DEVELOPMENT = 1        # Scratchpad, dev test mock


class ContextFactors(BaseModel):
    """Contextual metadata supplied by owner or inferred from inventory."""

    data_shelf_life_years: float = Field(
        default=5.0, ge=0.0,
        description="X: Required secrecy duration for protected data (Mosca factor X)",
    )
    migration_duration_years: float = Field(
        default=2.0, ge=0.0,
        description="Y: Estimated time needed to re-engineer and deploy PQC (Mosca factor Y)",
    )
    exposure: ExposureScope = Field(
        default=ExposureScope.INTERNAL_SHARED,
        description="Operational exposure level (1=dev, 5=public)",
    )
    criticality: BusinessCriticality = Field(
        default=BusinessCriticality.MODERATE,
        description="Business criticality (1=dev, 5=mission critical)",
    )
    dependency_reach: int = Field(
        default=1, ge=1,
        description="Blast radius / count of dependent downstream callers or systems",
    )
    is_user_enriched: bool = Field(
        default=False,
        description="True if context was verified by security owner rather than default",
    )


class RiskScenario(BaseModel):
    """Configurable scenario assumption parameters (slider inputs)."""

    scenario_id: str = Field(default="standard-2034-horizon")
    name: str = Field(default="Standard 2034 Cryptanalytically Relevant Quantum Computer (CRQC) Horizon")
    quantum_threat_horizon_years: float = Field(
        default=8.0, ge=1.0,
        description="Z: Estimated time until CRQC emerges (Mosca factor Z)",
    )
    # Weights for risk factors (must sum to 1.0)
    weight_quantum_vulnerability: float = Field(default=0.40, ge=0.0, le=1.0)
    weight_mosca_urgency: float = Field(default=0.25, ge=0.0, le=1.0)
    weight_exposure: float = Field(default=0.20, ge=0.0, le=1.0)
    weight_criticality: float = Field(default=0.15, ge=0.0, le=1.0)


class RiskEvaluation(BaseModel):
    """Transparent risk assessment for an individual cryptographic observation/asset."""

    asset_id: str = Field(..., description="Unique asset or observation identifier")
    algorithm: str = Field(..., description="Normalized cryptographic algorithm name")
    purpose: str = Field(..., description="Cryptographic function (e.g. KEY_EXCHANGE, SIGNATURE)")

    risk_score: float = Field(..., ge=0.0, le=100.0, description="Computed composite risk score (0-100)")
    urgency: UrgencyLevel = Field(..., description="Calibrated urgency tier")

    # Mosca Equation: X + Y > Z => CRITICAL Store-Now-Decrypt-Later (SNDL) Risk
    mosca_condition_violated: bool = Field(
        ..., description="True if X (lifetime) + Y (migration) > Z (quantum horizon)"
    )
    mosca_slack_years: float = Field(
        ..., description="Z - (X + Y): Negative indicates data exposure before migration completes"
    )

    factor_contributions: Dict[str, float] = Field(
        default_factory=dict, description="Percentage contribution of each factor to composite score"
    )
    reason_codes: List[str] = Field(
        default_factory=list, description="Machine-readable decision codes explaining the score"
    )
    assumptions_applied: Dict[str, Any] = Field(
        default_factory=dict, description="Active scenario horizon and factor parameters"
    )
    evaluated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
