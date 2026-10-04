# Phase B: Defensible Risk Models & Grounded Recommendations

**Document:** `phase_b.md`  
**Worker:** Worker 02 (`.brain/.work/webapp/worker_02`)  
**Target Roadmap Area:** Phase B — Make the risk result defensible (P1 Findings)  
**Target Readiness Score Impact:** 72/100 -> 80/100 (+8 points across Engine/API & Differentiation)  
**Status:** SPECIFICATION & ARCHITECTURE PLAN COMPLETE  

---

## 1. Objectives & Executive Scope

Phase B addresses the decision support and risk credibility gaps highlighted in the assessment:
1. **P1: Unverified Defaults vs. Owner-Supplied Context:**
   - Currently, scans use unverified default parameters for data lifetime ($X = 5.0$) and migration time ($Y = 2.0$), and the API omitted the `context` object from `risk_evaluations`.
   - Implement an explicit owner-context enrichment flow per scan/asset:
     - Allow callers/users to submit verified values: `data_shelf_life_years` ($X$), `migration_duration_years` ($Y$), `exposure`, `criticality`, `system_name`, `owner`.
     - Explicitly distinguish and label `DEFAULT_ASSUMPTION` vs `OWNER_CONFIRMED` in API responses, CBOM metadata, and UI badges.
     - Persist owner context with the scan record and expose `PUT /api/v1/scans/{scan_id}/context` to dynamically recalculate Mosca urgency ($X + Y > Z$) and risk scores.
2. **P1: Grounded, Contextual PQC & Hybrid Recommendations:**
   - Replace generic algorithm placeholders with actionable migration paths that specify:
     - Algorithm purpose (Key Encapsulation Mechanism, Digital Signature, Cryptographic Hash, Symmetric Encryption).
     - Target NIST PQC Standard (FIPS 203 ML-KEM, FIPS 204 ML-DSA, FIPS 205 SLH-DSA, or Hybrid X25519+ML-KEM-768).
     - Performance impact (public key / signature size expansion, bandwidth overhead, CPU latency).
     - Compatibility and deployment trade-offs (TLS 1.3 ClientHello packet fragmentation, legacy client fallback).
     - Official dated standard citations (NIST FIPS 203/204/205, NSA CNSA 2.0, BSI TR-02102-1).
3. **UI Integration:**
   - Expose the owner context in the dashboard so users can view and toggle assumption parameters, inspect Mosca slack ($Z - (X + Y)$), and see transparent factor contributions and trade-off rationales.

---

## 2. Technical Specifications & Architecture

### 2.1 Domain Model Upgrades
- **File:** `backend/app/risk/models.py`
  - In `RiskEvaluation`:
    - Add explicit `context: ContextFactors` field to each evaluation object so `r.context` is never null.
    - Add `is_owner_confirmed: bool` property (derived from `context.is_user_enriched`).
    - Add `recommendation: Optional[MigrationCandidate] = None`.
- **File:** `backend/app/risk/taxonomy.py`
  - Enhance `MigrationCandidate` with:
    - `purpose: str` (e.g. "Key Encapsulation Mechanism (KEM)")
    - `performance_impact: str` (e.g. "Public key: 1,184 bytes (vs 32 bytes for X25519); Latency overhead: ~0.4ms")
    - `bandwidth_and_cost: str` (e.g. "Requires TLS record segmentation; storage increase for key bundles")
    - `cisa_nsa_guidance: str` (e.g. "NSA CNSA 2.0 requires ML-KEM-1024 or ML-KEM-768 by 2030 for national security systems")
    - `remediation_steps: List[str]`

### 2.2 Scorer & Service Enrichment
- **File:** `backend/app/risk/scorer.py`
  - Attach the evaluated `ContextFactors` and algorithm `MigrationCandidate` to `RiskEvaluation`.
- **File:** `backend/app/services/scan_service.py`
  - Add method `update_scan_context(scan_id: str, context: ContextFactors, scenario: Optional[RiskScenario] = None) -> ScanRecord`:
    - Reloads record, re-evaluates risk for all observations with updated owner context, regenerates backlog items, updates CBOM, and persists to store.
- **File:** `backend/app/api/workflow_routes.py`
  - Add route: `PUT /api/v1/scans/{scan_id}/context` accepting `ContextFactors` payload and returning updated risk assessment and summary.

### 2.3 Frontend Dashboard Integration
- **File:** `frontend/index.html`
  - Render context badge ("DEFAULT ASSUMPTION" vs "OWNER CONFIRMED") in asset and risk views.
  - Display detailed recommendation card when expanding finding:
    - Shows Target Standard, Hybrid Path, Performance Impact, Bandwidth/Cost note, and Official Citation.
  - Wire interactive parameter adjustment so updating $X$ and $Y$ triggers live recalculation.
  - Sync to `backend/app/static/index.html`.

---

## 3. Test Strategy & Specific Acceptance Gates

### Test 3.1: Risk Scorer & Taxonomy Grounding (`test_phase_b_risk.py`)
- Assert every `RiskEvaluation` contains a non-null `context: ContextFactors` object.
- Test updating context via API (`PUT /api/v1/scans/{scan_id}/context`):
  - Change $X=10.0$ and $Y=3.0$ with $Z=8.0$; assert `mosca_condition_violated == True` and urgency escalates to `CRITICAL`.
  - Verify `context.is_user_enriched == True` and `context_source == "OWNER_SUPPLIED"`.
- Test recommendations:
  - RSA-2048 / ECDH observations map to ML-KEM with non-empty `performance_impact` and valid `target_standard_ref`.
  - RSA-PSS / ECDSA observations map to ML-DSA / SLH-DSA with valid signature size notes.

---

## 4. Phase B Deliverables
- [x] Architecture specification (`phase_b.md`)
- [ ] Code modifications: `backend/app/risk/models.py`, `backend/app/risk/taxonomy.py`, `backend/app/risk/scorer.py`, `backend/app/services/scan_service.py`, `backend/app/api/workflow_routes.py`, `frontend/index.html`
- [ ] Automated test suite: `backend/tests/test_phase_b_risk.py`
- [ ] Phase completion report: `.brain/.work/.report/phase_b_report.md`
- [ ] Git commit and push upon completion.
