# Worker 04 Phase E: Dynamic Quality Gate Rehearsal Alignment, Complete Documentation Sync & 100/100 Closeout

**Document:** `phase_e.md`  
**Worker:** Worker 04 (`.brain/.work/webapp/worker_04`)  
**Target Roadmap Area:** P1 / Closeout, Judging Rehearsal & Truthful Verification  
**Target Readiness Score Impact:** +5 points across all rubric dimensions (Full 100/100 Closeout)  
**Status:** SPECIFICATION COMPLETE  

---

## 1. Objectives & Executive Scope

Phase E completes the full 100-point roadmap recovery by aligning the master judging rehearsal runner, synchronizing all repository documentation, and providing transparent, evidence-backed verification:
1. **Dynamic Quality Gate Rehearsal Alignment (`scripts/run_judging_rehearsal.py`)**:
   - Align Factor 1 to actively verify all 5 core discovery surfaces (Source, Manifest, Config, Cert, Container OCI) plus Cloud KMS and PKCS#11 HSM adapters on live scans.
   - Align Factor 3 to verify the corrected `Asymmetric` category resolution and server-persisted audit chain.
   - Eliminate any misleading "100% Certified" or "Full Roadmap Recovery" claims, replacing them with:
     `"100 / 100 AUTOMATED QUALITY GATES PASSED ON TESTED BENCHMARK EVIDENCE"`
     explicitly noting that scores reflect local automated acceptance criteria on synthetic and holdout test fixtures.
2. **Complete Documentation Synchronization (`README.md`)**:
   - Synchronize test counts across all badges, headings, and tables to reflect the exact current counts:
     - Exact backend test count (142 + all new Worker 04 tests).
     - Exact frontend test count (192 tests across 48 test suites).
     - Exact combined total test count.
   - Update Table of Contents (removing stale 311/333 references).
   - Update the Supported Scope Matrix to list Cloud KMS and PKCS#11 HSM as verified local prototype adapters.
   - Ensure the NIST FIPS 203 errata notice (17 November 2025) is prominent and accurately contextualized.
3. **Repository-Wide End-to-End Verification**:
   - Execute full backend pytest suite (100% passing).
   - Execute full frontend vitest suite (100% passing).
   - Execute dynamic master judging rehearsal (`scripts/run_judging_rehearsal.py`, exit code 0).

---

## 2. Technical Deliverables

| Deliverable | File | Target Behavior |
|---|---|---|
| **Aligned Rehearsal Runner** | `scripts/run_judging_rehearsal.py` | Dynamically evaluates all surfaces, persistent audit chain, and asymmetric category with transparent evidence reporting. |
| **Comprehensive README** | `README.md` | Perfectly synchronized test counts, updated scope matrix, and transparent quality gate documentation. |
| **Phase E Automated Test Suite**| `backend/tests/test_worker04_phase_e_rehearsal_closeout.py` | Pytest suite validating rehearsal runner execution, README synchronicity, and 100/100 quality gates. |
| **Phase E Completion Report** | `.brain/.work/.report/worker04_phase_e_report.md` | Standardized audit report documenting all implementation details and verification results. |

---

## 3. Test Strategy & Acceptance Gates

- **Test E.1:** Assert `python scripts/run_judging_rehearsal.py` executes dynamically and returns exit code 0.
- **Test E.2:** Assert `README.md` test counts exactly match `pytest` and `vitest` execution numbers.
- **Test E.3:** Assert zero stale test counts (e.g. 88, 119, 141, 311, 333) remain in active documentation or UI.
- **Test E.4:** Full repository automated test suite passes with 0 failures.
