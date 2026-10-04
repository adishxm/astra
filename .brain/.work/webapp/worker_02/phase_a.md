# Phase A: Close the MVP Integrity Gap (UI/API Contract, Scan ID Propagation, Archive Accounting & Canonical Frontend Sync)

**Document:** `phase_a.md`  
**Worker:** Worker 02 (`.brain/.work/webapp/worker_02`)  
**Target Roadmap Area:** Phase A — Close the MVP integrity gap first (P0 Findings)  
**Target Readiness Score Impact:** 62/100 -> 72/100 (+10 points across Engine/API/CLI & Frontend Workflow)  
**Status:** SPECIFICATION & ARCHITECTURE PLAN COMPLETE  

---

## 1. Objectives & Executive Scope

Phase A addresses the critical P0 findings identified in the *ASTRA / SIH26164 Product Assessment and 100-Point Improvement Roadmap*:
1. **P0: Real upload results mapped incorrectly in active dashboard (`frontend/index.html`):**
   - Correctly map coverage percentage from `scan.coverage.overall_coverage_percentage` (and fallback to `scan.summary.coverage_percentage`), avoiding `NaN`.
   - Correctly map file counts: `filesAssessed = scan.summary.assessed_files`, `filesTotal = scan.summary.total_files` (eliminating the defect where `scan.asset_count` was used as file counts).
   - Map observation properties properly: `line = obs.start_line`, `evidence = obs.sanitized_excerpt`, severity and PQC recommendations from real risk evaluations (`riskEval.urgency`, `riskEval.candidate_pqc_algorithm`).
   - Fix API base resolution to dynamically respect same-origin / relative paths (`window.location.origin`) rather than hardcoding loopback `http://127.0.0.1:8000`.
2. **P0: Archive metadata & Scan ID inconsistency:**
   - Eliminate extra file counting caused by extraction metadata (`scan_manifest.json` placed inside extraction directory). Exclude internal sidecars from discovery file accounting.
   - Enforce single canonical `scan_id` minted at intake and propagated through `ScanRecord`, `ScanManifest`, `CoverageReport`, `InventorySnapshot`, `Observation`, `backlog_items`, and CycloneDX `serialNumber` (`urn:uuid:...`).
   - Ensure the denominator in `summary.total_files` equals `coverage.total_files_in_archive` equals archive member count (e.g. exactly 6 files for synthetic sample).
3. **P0: Canonical Shipped Frontend & Fallback Synchronization:**
   - Synchronize `backend/app/static/index.html` with `frontend/index.html` to eliminate drift between dev and fallback serving.
   - Ensure `npm run build` produces the canonical production bundle in `frontend/dist/`.
4. **End-to-End Verification Gate:**
   - Automated regression test suite asserting invariant: all IDs match, file counts match, coverage matches, and API responses match expected schema.
   - Browser-level validation test exercising real upload, results display, and CBOM export.

---

## 2. Detailed Technical Specifications & Implementation Steps

### 2.1 Backend Scan Service & Intake Normalization
- **File:** `backend/app/intake/sandbox.py`
  - Modify `execute_intake`: Move `scan_manifest.json` outside the target directory or place it in a dedicated metadata directory outside the extracted source tree, or configure the extractor to prevent it from being included in target file scans.
- **File:** `backend/app/services/scan_service.py`
  - In `run_scan_on_directory`:
    - Accept an optional `scan_id: Optional[str] = None`. If provided, use it rather than generating a new random UUID.
    - Add explicit exclusion for `scan_manifest.json`, `manifest.json`, `.astra_metadata`, `.git`, `.DS_Store`, etc.
  - In `run_scan_on_archive`:
    - Pass the intake manifest's `manifest.scan_id` directly to `run_scan_on_directory(scan_id=manifest.scan_id)`.
    - Ensure `record.scan_id == manifest.scan_id == coverage_report.scan_id == snapshot.scan_id`.
    - Harmonize `summary["total_files"]` and `coverage.total_files_in_archive` to reflect the exact true archive count.

### 2.2 Active Frontend Contract Repair
- **File:** `frontend/index.html`
  - In `fetchAPI`:
    - Use dynamic `API_BASE`:
      ```javascript
      var API_BASE = (window.VITE_API_BASE_URL || (window.location && window.location.origin && window.location.origin !== 'null' && window.location.protocol.startsWith('http') ? window.location.origin : 'http://127.0.0.1:8000')) + '/api/v1';
      ```
  - In `loadScanData(scanId)`:
    - Parse `scan` object from `/scans/{scan_id}`:
      ```javascript
      var covPct = 0;
      if (scan.coverage && typeof scan.coverage.overall_coverage_percentage === 'number') {
        covPct = scan.coverage.overall_coverage_percentage;
      } else if (scan.summary && typeof scan.summary.coverage_percentage === 'number') {
        covPct = scan.summary.coverage_percentage;
      }
      var totalFiles = (scan.summary && scan.summary.total_files) || (scan.coverage && scan.coverage.total_files_in_archive) || 0;
      var assessedFiles = (scan.summary && scan.summary.assessed_files) || (scan.coverage && scan.coverage.total_assessed_files) || 0;
      ```
    - Map observation objects with truthful properties:
      ```javascript
      line: obs.start_line || obs.line_number || 1,
      evidence: obs.sanitized_excerpt || obs.evidence_snippet || obs.detector_id || '',
      confidence: obs.confidence || 'High',
      quantumVulnerable: obs.is_quantum_vulnerable !== undefined ? obs.is_quantum_vulnerable : (riskEval ? riskEval.quantum_vulnerable : true),
      severity: (riskEval && riskEval.urgency && (riskEval.urgency.value || riskEval.urgency)) || obs.severity || 'MEDIUM',
      pqc: (riskEval && riskEval.candidate_pqc_algorithm) || obs.candidate_pqc_algorithm || 'ML-KEM / FIPS 203',
      ```
    - Map summary object:
      ```javascript
      return {
        id: scan.scan_id,
        source: scan.target_name,
        coverage: covPct / 100,
        coveragePercentage: covPct,
        filesAssessed: assessedFiles,
        filesTotal: totalFiles,
        assets: mappedAssets,
        cbomJson: JSON.stringify(cbom, null, 2)
      };
      ```
  - Sync changes to `backend/app/static/index.html` and `frontend/legacy/index.static.html`.

---

## 3. Test Strategy & Specific Acceptance Gates

### Test 3.1: Backend Integration Test (`test_phase_a_integrity.py`)
- Create `backend/tests/test_phase_a_integrity.py`:
  - Upload `examples/synthetic_sample` as zip to `/api/v1/scans/upload`.
  - Assert HTTP 200.
  - Verify returned `scan_id`:
    - Record `scan_id` == Manifest `scan_id` == Coverage `scan_id` == Snapshot `scan_id`.
    - CBOM serial number matches `urn:uuid:{uuid5(scan_id)}`.
  - Verify file denominators:
    - Synthetic sample has exactly 6 files. Assert `summary.total_files == 6` and `coverage.total_files_in_archive == 6`.
    - Assert `coverage.total_assessed_files == 4`.
    - Assert `overall_coverage_percentage == 66.67%`.
  - Verify finding observations have non-null `start_line` and valid `sanitized_excerpt`.

### Test 3.2: Browser / Client End-to-End Test
- Verify frontend loads without errors, maps all fields, shows `66.7%` coverage rather than `NaN%`, shows `4/6 Files` rather than `14/14 Files`.
- Verify CBOM export button downloads valid JSON.

---

## 4. Phase A Deliverables
- [x] Architecture specification (`phase_a.md`)
- [ ] Code modifications: `backend/app/services/scan_service.py`, `backend/app/intake/sandbox.py`, `frontend/index.html`, `backend/app/static/index.html`
- [ ] Automated test suite: `backend/tests/test_phase_a_integrity.py`
- [ ] Phase completion report: `.brain/.work/.report/phase_a_report.md`
- [ ] Git commit and push upon completion.
