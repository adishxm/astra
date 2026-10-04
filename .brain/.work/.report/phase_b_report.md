# Worker 02 Phase B Report: Defensible Risk Models & Grounded Recommendations

**Owner:** Evidence, Identity & Interoperable Inventory (Worker 02)  
**Stage:** 100-Point Improvement Roadmap — Phase B of E  
**Phase:** Phase B  
**Status:** IMPLEMENTED & VALIDATED  
**Traceability IDs:** R03, R04, R06, R07, R10  
**Acceptance Criteria:** AC-03, AC-05, AC-07, AC-08, AC-12  
**Date:** 2026-10-04  

---

## 1. Executive Summary & Objective

Phase B eliminates the decision support and risk credibility gaps documented in Section 4 & 5 of the *ASTRA / SIH26164 Product Assessment and 100-Point Improvement Roadmap*:
1. **Contextual Risk Grounding**: Attached non-null `ContextFactors` and `confidence_source` to every individual `RiskEvaluation`, providing full visibility into data shelf life ($X$), migration time ($Y$), operational exposure, and business criticality.
2. **Owner-Supplied Context Enrichment**: Implemented `PUT /api/v1/scans/{scan_id}/context`, allowing security owners to submit verified operational parameters ($X, Y$, exposure, criticality, horizon $Z$) and trigger dynamic, live recalculation of the Mosca equation ($X + Y > Z$), escalating Store-Now-Decrypt-Later (SNDL) exposures to `CRITICAL` urgency.
3. **Substantiated PQC & Hybrid Recommendations**: Expanded the cryptographic taxonomy catalog (`MigrationCandidate`) with official standard citations (NIST FIPS 203 ML-KEM, FIPS 204 ML-DSA, FIPS 205 SLH-DSA, NSA CNSA 2.0), empirical performance impact (key/ciphertext size expansion, CPU cycles), network trade-offs (TLS 1.3 ClientHello MTU fragmentation), and hybrid migration stepping stones.
4. **UI Transparency**: Added clear badges distinguishing `DEFAULT_ASSUMPTION` vs `OWNER_VERIFIED` in inventory and risk views, and wired detailed migration trade-off tooltips into the dashboard.

---

## 2. Technical Decisions & Code Deliverables

| Module | File | Changes Made |
|---|---|---|
| **Risk Domain Models** | `backend/app/risk/models.py` | Added `context: ContextFactors`, `confidence_source: str`, and `recommendation: Optional[Dict[str, Any]]` to `RiskEvaluation`. |
| **Taxonomy & Recommendations** | `backend/app/risk/taxonomy.py` | Enriched `MigrationCandidate` with `purpose`, `performance_impact`, `bandwidth_and_cost`, `cisa_nsa_guidance`, and `remediation_steps`. Added profiles for `ECDH`, `ECDHE`, `ECDHE-AES256-GCM`, `ECDHE-AES128-GCM`, `TLSv1.0`, `TLSv1.1`, and `TLSv1.2`. Optimized algorithm prefix lookup. |
| **Risk Scorer** | `backend/app/risk/scorer.py` | Populated `context`, `confidence_source` (`OWNER_SUPPLIED` vs `DEFAULT_ASSUMPTION`), and `recommendation` from catalog. |
| **Scan Service** | `backend/app/services/scan_service.py` | Implemented `update_scan_context(scan_id, context, scenario)` for persistent live recalculation of risk and backlog. |
| **API Endpoints** | `backend/app/main.py` | Added route `PUT /api/v1/scans/{scan_id}/context` to update owner context and return updated risk evaluations. |
| **Active Dashboard** | `frontend/index.html` | Mapped `recommendation` and `contextSource`, added `OWNER VERIFIED` vs `ASSUMPTION` tags and recommendation trade-off tooltips. Synchronized static and production bundles. |

---

## 3. Test Strategy & Verification Results

### 3.1 Automated Phase B Test Suite (`test_phase_b_risk.py`)
- **Suite Command:** `python -m pytest backend/tests/test_phase_b_risk.py -v`
- **Results:** 2 passed in 2.50s (100% pass rate)
  - `test_phase_b_risk_evaluations_contain_grounded_context_and_recommendations`: PASS
    - Asserts every evaluation has non-null context with $X, Y$, and valid `confidence_source`.
    - Asserts quantum-vulnerable algorithms (RSA, ECDH) have non-empty recommendations with NIST FIPS citations, performance impact, and compatibility gaps.
  - `test_phase_b_owner_context_update_and_live_mosca_recalculation`: PASS
    - Verifies `PUT /api/v1/scans/{scan_id}/context` successfully enriches scan with owner parameters ($X=8.0, Y=3.0, Z=8.0$).
    - Asserts live Mosca condition violation ($8.0 + 3.0 = 11.0 > 8.0$) and escalation of urgency to `CRITICAL`.
    - Asserts `context_source` transitions to `OWNER_SUPPLIED`.
    - Verifies updated evaluations and context are persisted in `GLOBAL_SCAN_STORE`.

### 3.2 Full Repository Regression Run
- **Backend Test Suite:** `python -m pytest -q` -> **99 passed, 1 skipped** in 9.38s.
- **Frontend Production Build:** `npm run build` -> **Success (267.78 kB bundle emitted in 441ms)**.

---

## 4. Acceptance Gate Confirmation

- [x] Every risk evaluation has an explicit, traceable `ContextFactors` object.
- [x] Clear separation between `DEFAULT_ASSUMPTION` and `OWNER_SUPPLIED` context.
- [x] Dynamic context update endpoint (`PUT /context`) recalculates Mosca deadline ($X+Y>Z$) live.
- [x] Recommendations include official NIST/NSA citations, key/packet size trade-offs, and hybrid paths.
- [x] All 99 backend tests passing green.
- [x] Phase B gate complete and validated. Ready for Phase C.
