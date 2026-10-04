# ASTRA Frontend — P08 Implementation Report: Risk Assessment UI

## 1. Executive Summary

Phase **P08 (Risk Assessment UI)** delivers the presentation layer for backend-computed cryptographic risk evaluations, Mosca Theorem migration timelines ($X + Y > Z$), and candidate post-quantum cryptography (PQC) migration recommendations.

The implementation complies with all core ASTRA truthfulness principles:
* **Backend-Owned Risk:** The frontend never recalculates, transforms, or re-interprets risk scores or urgency ratings. All composite scores, weights, and urgency levels are rendered verbatim from backend evaluations.
* **Risk Honesty:** `Unknown ≠ Low Risk`, `Unassessed ≠ Low Risk`, `Missing Score ≠ 0`, `Missing Severity ≠ Low`, `No Evidence ≠ Safe`. All unassessed or missing values are rendered using neutral styling and explicit "Unassessed" badges.
* **Accessible Visual Design:** Severity is communicated via text labels, icons, and WCAG-compliant color tokens. No color-only signaling.

---

## 2. API Contract & Data Integration

### 2.1 Primary Risk Endpoint: `GET /api/v1/scans/{scan_id}/risk`
Supports optional scenario simulation query parameters:
* `horizon`: Quantum threat horizon in years ($Z$, default `8.0`).
* `shelf_life`: Data confidentiality retention lifespan in years ($X$, default `5.0`).
* `migration`: Migration duration to deploy PQC in years ($Y$, default `2.0`).

### 2.2 Response Structure
```json
{
  "scan_id": "scan-cf529d73",
  "scenario": {
    "scenario_id": "standard-2034-horizon",
    "quantum_threat_horizon_years": 8.0,
    "horizon_rationale": "Planning scenario assumption aligned with NIST IR 8547",
    "weight_quantum_vulnerability": 0.4,
    "weight_mosca_urgency": 0.25,
    "weight_exposure": 0.2,
    "weight_criticality": 0.15
  },
  "context": {
    "data_shelf_life_years": 5.0,
    "migration_duration_years": 2.0,
    "context_source": "DEFAULT_ASSUMPTION"
  },
  "risk_evaluations": [
    {
      "asset_id": "rsa-2048-crypto_service.py-22",
      "algorithm": "RSA-2048",
      "purpose": "ASYMMETRIC",
      "risk_score": 64.31,
      "urgency": "MEDIUM",
      "mosca_condition_violated": false,
      "mosca_slack_years": 1.0,
      "is_scenario_assumption": true,
      "factor_contributions": {
        "algorithm_vulnerability": 43.5,
        "mosca_horizon_urgency": 23.8,
        "operational_exposure": 18.7,
        "business_criticality": 14.0
      },
      "reason_codes": ["RC_MODERATE_MIGRATION_PRIORITY"],
      "assumptions_applied": { ... },
      "evaluated_at": "2026-10-03T16:58:45.449871+00:00"
    }
  ],
  "backlog_items": [
    {
      "task_id": "mig-2e42289f",
      "asset_id": "rsa-2048-crypto_service.py-22",
      "target_pqc_algorithm": "ML-KEM-768 (NIST FIPS 203)",
      "dated_standard_ref": "NIST FIPS 203 (Aug 2024)",
      "priority": "CRITICAL",
      "compatibility_gaps": ["Ciphertext size increases from 256 bytes to 1088 bytes"],
      "recommended_action": "Migrate RSA-2048 to ML-KEM-768",
      "operational_benchmarking_caveat": "Advisory candidate mapping from NIST standards. Requires deployment-specific benchmarking."
    }
  ]
}
```

---

## 3. Implemented Components

### 3.1 `RiskSummary` (`src/components/risk/RiskSummary.jsx`)
* **Urgency Cards:** Visual breakdown of `Critical`, `High`, `Medium`, `Low`, and `Unassessed` items.
* **Mosca Theorem Banner:**
  * Formula: $X + Y$ vs $Z$.
  * Slack indicator: negative slack styled in high-visibility critical alert; positive buffer in low/safe styling.
  * **SNDL Warning:** Store Now, Decrypt Later vulnerability warning when $X + Y > Z$.
  * **Assumptions Caveat:** Displays scenario simulation caveat and ruleset version (`2026.10-nist-pqc`).

### 3.2 `RiskFactorBreakdown` (`src/components/risk/RiskFactorBreakdown.jsx`)
* Visualizes the 4 backend-provided factor components:
  1. `algorithm_vulnerability` (Weight: 40%): Mathematical susceptibility.
  2. `mosca_horizon_urgency` (Weight: 25%): Timeline urgency.
  3. `operational_exposure` (Weight: 20%): Network & boundary exposure.
  4. `business_criticality` (Weight: 15%): Asset criticality.
* Supports both individual asset factor breakdown and aggregate scan mean breakdown.

### 3.3 `RiskTable` (`src/components/risk/RiskTable.jsx`)
* **Search:** Filter by algorithm name, asset ID, purpose, or reason codes.
* **Filters:** Urgency filter (`ALL`, `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, `UNASSESSED`) and Mosca timeline filter (`ALL`, `VIOLATED`, `COMPLIANT`).
* **Sorting:** Risk score, urgency weight, algorithm alphabetical, and Mosca slack.
* **Actions:** Row click and "Inspect" button to trigger deep inspection.
* **Pagination:** Accessible page size selector and navigation.

### 3.4 `RiskDetailModal` (`src/components/risk/RiskDetailModal.jsx`)
* Complete inspection modal for a single evaluated asset:
  * Composite Risk Score & Urgency Badge.
  * Full 4-factor percentage bar breakdown.
  * Mosca timeline calculation ($X + Y$ vs $Z$) and SNDL warning.
  * Applied Scenario Assumptions (ID, threat horizon, data shelf-life, migration duration, ruleset).
  * Reason codes list with human-readable explanations.
  * Candidate PQC migration option (target algorithm, dated standard ref, compatibility gaps, benchmarking caveat).

### 3.5 Dedicated Pages & App Integration
* **`RiskPage` (`src/pages/RiskPage.jsx`):** Dedicated `/risk` route with scan picker and interactive Mosca Scenario Simulation controls (Horizon $Z$, Shelf-Life $X$, Migration $Y$).
* **`ScanDetailPage` (`src/pages/ScanDetailPage.jsx`):** Added `Risk Assessment` tab in `TabBar` alongside findings, coverage, discovery surfaces, coverage gaps, and engine health.
* **`Sidebar` (`src/components/layout/Sidebar.jsx`):** Added navigation entry for `/risk`.

---

## 4. Verification & Testing

### 4.1 Test Suite & Coverage
* **Total Frontend Test Files:** 36 passing (100%).
* **Total Frontend Tests:** 136 passing (100%).
* **Statement Coverage:** **93.76%** across all files.
  * `components/risk/RiskDetailModal.jsx`: 96.47%
  * `components/risk/RiskFactorBreakdown.jsx`: 99.25%
  * `components/risk/RiskSummary.jsx`: 95.41%
  * `components/risk/RiskTable.jsx`: 94.27%
  * `pages/RiskPage.jsx`: 92.63%

### 4.2 Lint & Production Build
* `npm.cmd run lint`: **0 errors**.
* `npm.cmd run build`: **0 errors** (`dist/assets/index-CBt3-oge.js` 308.48 kB).

### 4.3 Backend Baseline Verification
* `& ".venv\Scripts\python.exe" -m pytest backend/tests -q`: **88/88 passed** (100%).

---

## 5. Limitations & Future Work

* P08 solely renders backend risk evaluations and candidate recommendations; automated migration code patching or git branch generation is out of scope for P08 and reserved for future remediation phases.
