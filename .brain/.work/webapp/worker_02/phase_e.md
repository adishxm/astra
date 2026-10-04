# Phase E: Judging Rehearsal, Verification & 100/100 Certification

**Document:** `phase_e.md`  
**Worker:** Worker 02 (`.brain/.work/webapp/worker_02`)  
**Target Roadmap Area:** Phase E — Run a judging rehearsal & Defensible 100/100 Closeout  
**Target Readiness Score Impact:** 96/100 -> 100/100 (+4 points: Flawless Demo, Full Documentation & Evidence Verification)  
**Status:** SPECIFICATION & ARCHITECTURE PLAN COMPLETE  

---

## 1. Objectives & Executive Scope

Phase E completes the 100-Point Improvement Roadmap by executing an end-to-end judging rehearsal and proving all acceptance gates:
1. **Clean Rehearsal & Multi-Project Demonstration:**
   - Follow exact quick-start instructions from a clean environment.
   - Scan Project 1: `examples/synthetic_sample` (4 assessed files / 6 total files, 14 cryptographic assets, 66.67% coverage).
   - Scan Project 2: Representative production sample (`examples/multi_surface_sample` or labelled corpus).
   - Demonstrate:
     - Accurate file denominators (no extraction sidecar artifacts, no `NaN`).
     - Evidence transparency: source code file, exact line number, and sanitized excerpt with private key redaction.
     - Owner context modification via UI/API: demonstrate live urgency shift from `MEDIUM` to `CRITICAL` when $X+Y > Z$.
     - CycloneDX 1.6 CBOM export and independent schema validation against official CycloneDX schema.
     - Honest surface visibility: highlighting covered vs. unassessed files vs. out-of-scope hardware KMS/HSM boundaries.
2. **Reproducible Timing & Golden Artifacts:**
   - Record scan execution timings (< 2s for synthetic sample, deterministic performance).
   - Generate validated golden CBOM and benchmark summary files.
3. **Comprehensive Documentation & 100/100 Audit Evidence:**
   - Update `README.md` with:
     - Real, verified test pass counts across backend pytest and frontend vitest.
     - Verified benchmark accuracy report ($\ge 80\%$ precision and recall).
     - Accurate launch commands pointing to the unified canonical frontend.
     - Full 100-point rubric acceptance table showing every gate met with proof.

---

## 2. Technical Specifications & Verification Run

### 2.1 Golden Multi-Project Demonstration Script
- Create automated rehearsal runner: `scripts/run_judging_rehearsal.py`
  - Step 1: Health heartbeat check (`/health`).
  - Step 2: Ingest synthetic sample archive; verify exact 6 files, 4 assessed, 14 assets, 0 `scan_id` divergence.
  - Step 3: Ingest second representative project; verify multi-surface coverage breakdown.
  - Step 4: Submit owner-context modification ($X=8, Y=3, Z=8$); assert urgency transitions to `CRITICAL`.
  - Step 5: Export CycloneDX 1.6 CBOM and run schema validator; assert 0 schema violations.
  - Step 6: Print formatted judging rehearsal verification scorecard.

### 2.2 README & Final Report Synchronizations
- Update `README.md` to reflect:
  - 100/100 Defensible Scorecard.
  - Test suite metrics: exact test numbers.
  - Supported Surface Matrix.
  - Exact reproducible quickstart commands.

---

## 3. Test Strategy & Specific Acceptance Gates

### Test 3.1: Judging Rehearsal Suite (`test_phase_e_rehearsal.py`)
- Automated pytest verifying the entire end-to-end rehearsal lifecycle.
- Asserts that every single claim in the 100-point roadmap has an automated test passing in the repository.

---

## 4. Phase E Deliverables
- [x] Architecture specification (`phase_e.md`)
- [ ] Judging rehearsal runner script: `scripts/run_judging_rehearsal.py`
- [ ] Automated rehearsal verification test: `backend/tests/test_phase_e_rehearsal.py`
- [ ] Documentation update: `README.md`
- [ ] Phase completion report: `.brain/.work/.report/phase_e_report.md`
- [ ] Git commit and push upon completion.
