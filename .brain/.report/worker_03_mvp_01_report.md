# Worker 03 MVP-01 Report: Context Fields and Transparent Risk Model

**Owner:** Risk, Context & Migration Decision Support (Worker 03)  
**Stage:** MVP  
**Phase:** MVP-01  
**Status:** IMPLEMENTED & VALIDATED  
**Traceability IDs:** R01, R02, R03, R05, R06  
**Acceptance Criteria:** AC-07  
**Date:** 2026-10-03  

---

## 1. Objective & Scope
Implemented the contextual, deterministic, Mosca-aware cryptographic risk calculation engine for ASTRA. Replaces opaque severity guesses with an explainable formula separating urgency from confidence, explicitly evaluating Store-Now-Decrypt-Later (SNDL) conditions ($X + Y > Z$), and tracking factor contributions.

---

## 2. Implemented Components

1. **`backend/app/risk/models.py`**:
   - `UrgencyLevel`: `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, `INFORMATIONAL`
   - `ExposureScope`: Operational exposure scale from `PUBLIC_FACING` (5) to `BUILD_OR_TEST` (1)
   - `BusinessCriticality`: Business impact scale from `MISSION_CRITICAL` (5) to `DEVELOPMENT` (1)
   - `ContextFactors`: Encapsulates data shelf life ($X$ years), migration duration ($Y$ years), exposure, criticality, and dependency reach
   - `RiskScenario`: Configurable assumption parameters including CRQC horizon ($Z$ years) and factor weights
   - `RiskEvaluation`: Output schema detailing composite score (0-100), Mosca condition violation flag, Mosca slack years ($Z - (X+Y)$), factor contributions, and reason codes

2. **`backend/app/risk/scorer.py`**:
   - `RiskScorer`:
     - Calculates Mosca theorem: $X + Y > Z \implies \text{CRITICAL Urgency}$
     - Computes composite weighted risk:
       $$\text{Score} = w_{\text{algo}} \cdot S_{\text{algo}} + w_{\text{mosca}} \cdot S_{\text{mosca}} + w_{\text{exp}} \cdot S_{\text{exp}} + w_{\text{crit}} \cdot S_{\text{crit}}$$
     - Produces transparent factor contributions summing to 100%
     - Emits standardized decision codes (`RC_MOSCA_DEADLINE_VIOLATED_SNDL_RISK`, `RC_ALGORITHM_BROKEN_LEGACY`, etc.)

---

## 3. Validation & Test Results
- `test_mosca_deadline_violation_triggers_critical_urgency`: **PASSED** (Overdue slack correctly triggers CRITICAL tier).
- `test_mosca_safe_slack_for_short_lived_data`: **PASSED** (Short shelf life retains positive slack).
- `test_broken_legacy_algorithm_is_always_critical`: **PASSED** (MD5/DES flagged CRITICAL regardless of horizon).
- `test_factor_contributions_transparency`: **PASSED** (Factor percentage breakdown verified).
