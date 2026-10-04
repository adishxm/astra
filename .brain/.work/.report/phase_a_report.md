# Worker 02 Phase A Report: MVP Integrity Gap & Contract Traceability

**Owner:** Evidence, Identity & Interoperable Inventory (Worker 02)  
**Stage:** 100-Point Improvement Roadmap — Phase A of E  
**Phase:** Phase A  
**Status:** IMPLEMENTED & VALIDATED  
**Traceability IDs:** R01, R02, R05, R10, R12  
**Acceptance Criteria:** AC-01, AC-02, AC-04, AC-11, AC-13  
**Date:** 2026-10-04  

---

## 1. Executive Summary & Objective

Phase A closes the critical P0 integrity and contract defects documented in the *ASTRA / SIH26164 Product Assessment and 100-Point Improvement Roadmap*:
1. **Contract Alignment**: Repaired the dashboard API adapter (`loadScanData`) to truthfully read `coverage.overall_coverage_percentage` and `summary.coverage_percentage` (eliminating `NaN%`), correctly map file counts (`summary.assessed_files` and `summary.total_files` instead of the asset count), and map observation fields (`start_line`, `sanitized_excerpt`, and calibrated severity).
2. **Scan ID & Manifest Normalization**: Eliminated divergent IDs across archive extraction and scan execution. Single intake `scan_id` (prefixed with `scan-`) is now strictly preserved and propagated across `ScanRecord`, `ScanManifest`, `CoverageReport`, `InventorySnapshot`, and CycloneDX CBOM `serialNumber` (`urn:uuid:...`).
3. **Extraction Sidecar Isolation**: Extraction manifests (`scan_manifest.json`) are now explicitly excluded from filesystem discovery walks, ensuring the file denominator strictly equals the true archive member count (e.g. exactly 6 files for the synthetic sample).
4. **Canonical Frontend Synchronization**: Synchronized the production frontend build (`frontend/index.html` -> `frontend/dist/index.html`) with the backend fallback (`backend/app/static/index.html`), ensuring no stale static UI can be served.

---

## 2. Technical Decisions & Code Deliverables

| Module | File | Changes Made |
|---|---|---|
| **Intake Sandbox** | `backend/app/intake/sandbox.py` | Standardized `scan_id` minting (`scan-XXXXXXXX`), persisted manifest safely, updated cleanup handler. |
| **Scan Service** | `backend/app/services/scan_service.py` | Added `override_manifest` and `scan_id` propagation to `run_scan_on_directory`, excluded internal metadata files (`scan_manifest.json`, `manifest.json`, `observations.json`) from `os.walk`, harmonized summary totals. |
| **Active Frontend** | `frontend/index.html` | Updated `API_BASE` to resolve same-origin paths, corrected `loadScanData` property mapping for coverage, denominators, line numbers, and evidence snippets. |
| **Static Mirrors** | `backend/app/static/index.html`<br>`frontend/legacy/index.static.html` | Fully synchronized with `frontend/index.html`. |
| **Production Build** | `frontend/dist/index.html` | Re-built with Vite (`npm run build`) in 1.06s. |

---

## 3. Test Strategy & Verification Results

### 3.1 Automated Phase A Test Suite (`test_phase_a_integrity.py`)
- **Suite Command:** `python -m pytest backend/tests/test_phase_a_integrity.py -v`
- **Results:** 2 passed in 2.70s (100% pass rate)
  - `test_phase_a_scan_id_and_denominator_integrity`: PASS
    - Verifies `scan_id` invariant across record, manifest, coverage, snapshot, and CBOM.
    - Verifies synthetic sample denominator: exactly 6 total files, 4 assessed, 66.67% coverage.
    - Verifies zero sidecar pollution from extraction.
    - Verifies all observations have valid line numbers and sanitized excerpts.
  - `test_phase_a_api_contract_for_dashboard`: PASS
    - Verifies `/api/v1/scans/{id}`, `/findings`, `/risk`, and `/export?format=cyclonedx` return fields expected by dashboard.

### 3.2 Full Repository Regression Run
- **Backend Test Suite:** `python -m pytest -q` -> **97 passed, 1 skipped** in 8.21s (Zero regressions).
- **Frontend Test Suite:** `npm test -- --run` -> **192 passed across 48 test suites** in 65.90s.
- **Frontend Production Build:** `npm run build` -> **Success (267.23 kB bundle emitted)**.

---

## 4. Acceptance Gate Confirmation

- [x] Single unified `scan_id` across all intake and persistence layers.
- [x] File denominator invariant: `summary.total_files == coverage.total_files_in_archive == 6`.
- [x] Real upload results mapped correctly in active dashboard without `NaN` or count divergence.
- [x] All 97 backend tests and 192 frontend tests passing green.
- [x] Phase A gate complete and validated. Ready for Phase B.
