# Worker 03 Phase E: Dynamic Evidence-Derived Rehearsal Scorecard & Truthful Documentation Closeout

**Document:** `phase_e.md`  
**Worker:** Worker 03 (`.brain/.work/webapp/worker_03`)  
**Target Roadmap Area:** P1 / Closeout — Treat benchmark/rehearsal status as test output, not hardcoded certification  
**Target Readiness Score Impact:** +1 point on Differentiation and Demo Value, completes full roadmap closeout  
**Status:** SPECIFICATION & ARCHITECTURE PLAN COMPLETE  

---

## 1. Objectives & Executive Scope

Phase E completes the 100-point roadmap recovery by replacing static self-certification with dynamic, evidence-derived judging output and synchronized, transparent documentation:
1. **Dynamic Rehearsal Scorecard (`scripts/run_judging_rehearsal.py`):**
   - Eliminate hardcoded static tables of `[("Phase A", ..., "PASSED", "100%")]`.
   - Calculate the scorecard dynamically from live machine-readable test results:
     - Health & Air-Gapped Egress: verify `/health` and zero outbound socket connections.
     - Project 1 Ingestion: verify exact file counts ($4/6$, $66.67\%$) and single unified `scan_id`.
     - Project 2 Multi-Surface & OCI Ingestion: verify discovery across all 5 surfaces including OCI layer blob inspection.
     - Dynamic Owner Context & Mosca Shift: verify live urgency escalation ($X+Y > Z \rightarrow$ `CRITICAL`).
     - CycloneDX 1.6 CBOM Conformance: verify CBOM schema validity and presence of `dependencies` graph.
     - Benchmark Accuracy: compute live precision and recall from test results.
   - If any gate fails or is untested, report it honestly as incomplete or failed.
2. **Truthful Documentation Synchronization (`README.md`):**
   - Update `README.md` to reflect real, measured metrics:
     - Total automated passing test count across repository.
     - Transparent OCI Image Layout inspection capability and safe streaming bounds.
     - Clear disclosure of Phase 2 enterprise scope (PKCS#11 HSMs, cloud KMS fleets).
     - Reference to NIST FIPS 203 errata notice (17 November 2025).
     - Evidence-based rehearsal runner usage.
3. **Automated Verification:**
   - Execute the dynamic rehearsal runner under pytest to guarantee zero regressions.

---

## 2. Technical Deliverables

| Deliverable | File | Target Behavior |
|---|---|---|
| **Dynamic Rehearsal Runner** | `scripts/run_judging_rehearsal.py` | Compute scorecard dynamically from live test metrics and schema validation. |
| **Comprehensive README** | `README.md` | Synchronize test metrics, OCI capabilities, errata notices, and dynamic scorecard runner instructions. |
| **Phase E Automated Test Suite** | `backend/tests/test_worker03_phase_e_rehearsal.py` | Tests dynamic rehearsal scorecard computation and exit code 0. |
| **Phase E Completion Report** | `.brain/.work/.report/worker03_phase_e_report.md` | Standardized audit report documenting all implementation details and verification results. |

---

## 3. Test Strategy & Acceptance Gates

- **Test E.1:** Execute `scripts/run_judging_rehearsal.py`; assert all gates are evaluated dynamically and exit code is 0.
- **Test E.2:** Verify that introducing a deliberate failure causes the rehearsal runner to dynamically emit a failing status for that gate.
- **Test E.3:** Verify full repository test pass rate across backend pytest and frontend vitest.
