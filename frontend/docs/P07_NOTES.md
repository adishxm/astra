# P07 — Coverage & Evidence Analysis Implementation Notes

**Worker:** Worker 01 (Frontend)  
**Branch:** `feat/frontend-p07-coverage-evidence`  
**Date:** 2026-10-03  
**Status:** Complete & Fully Verified  

---

## 1. Summary of Work

Phase **P07 (Coverage & Evidence Analysis)** delivers comprehensive visual accounting of scan discovery surfaces, transparent disclosure of coverage gaps and unsupported file formats, collector health telemetry, and strict provenance separation between raw observed evidence and derived system interpretations.

### Key Deliverables:
1. **Coverage Overview Component (`src/components/coverage/CoverageOverview.jsx` + `CoverageOverview.css`)**:
   - Assessed coverage percentage with `ProgressRing` visual progress and numerical percentage.
   - Truthful accounting banner: explicitly communicates that 100% surface coverage does not imply 0% risk.
   - Comprehensive file accounting matrix: Assessed files, Unsupported files, Skipped files, Failed extractions, and Total observations found.
   - Integrity & Completeness state badge (`COMPLETE_WITH_COVERAGE_ACCOUNTING`, `PARTIAL_SCAN_EVALUATION`).

2. **Discovery Surface Breakdown (`src/components/coverage/SurfaceBreakdown.jsx` + `SurfaceBreakdown.css`)**:
   - Surface matrix cards for all supported surfaces:
     - `SOURCE_CODE`
     - `PACKAGE_MANIFEST`
     - `CONFIGURATION`
     - `CERTIFICATE_STORE`
     - `UNSUPPORTED_SURFACE`
   - Per-surface statistics: coverage percentage bar, total files, assessed files, files with findings, and files with no findings.
   - Clickable surface interaction to switch views and inspect findings.

3. **Coverage Gaps Table (`src/components/coverage/CoverageGapsTable.jsx` + `CoverageGapsTable.css`)**:
   - Transparent disclosure of unassessed file surfaces, binary assets, and skipped formats from `manifest.files`.
   - Columns: File Path, File Extension, Formatted File Size, Status (`UNSUPPORTED`, `SKIPPED`), Assessment Gap Reason, and SHA-256 Digest.
   - Search filter for filtering through gap files.
   - Unsupported extensions pill list (e.g. `.json`, `.md`, `.wav`, `.png`).
   - Human-readable byte formatting utility (`formatBytes`).

4. **Collector Health Telemetry (`src/components/coverage/CollectorHealth.jsx` + `CollectorHealth.css`)**:
   - Operational status indicator for all detector engines:
     - `detector-source-code-v1`
     - `detector-manifest-v1`
     - `detector-config-v1`
     - `detector-certificate-v1`
     - `binary_crypto_detector_static_v1`
     - `container_crypto_detector_v1`
     - `network_endpoint_detector_v1`
   - Displays evaluation timestamp from `coverage.evaluated_at`.

5. **Evidence Provenance Viewer (`src/components/coverage/EvidenceViewer.jsx` + `EvidenceViewer.css`)**:
   - Strict provenance separation between:
     - **Observed Raw Evidence:** Physical file location, line range, source surface, sanitized code excerpt, SHA-256 evidence digest, and intake parameters.
     - **Derived System Interpretation:** Classified cryptographic primitive, purpose, confidence assessment badge, confidence rationale, detector provenance, ruleset version, and evaluation timestamp.
   - Embedded directly into [`FindingDetailModal`](file:///d:/SIH%202026%20Astra/astra-main/frontend/src/components/findings/FindingDetailModal.jsx) for comprehensive evidence inspection.

6. **Scan Detail Page Integration (`src/pages/ScanDetailPage.jsx`)**:
   - Integrated P03 `TabBar` with tab navigation:
     - `Findings & Primitives` (with finding count badge)
     - `Coverage & Accounting` (Coverage overview + surface matrix)
     - `Discovery Surfaces` (Surface breakdown)
     - `Coverage Gaps` (with gap count badge)
     - `Engine Health` (Detector health grid)
   - Preserves all P06 scan header metrics, DNA hash badge, and urgency pills.

7. **Barrel Export (`src/components/coverage/index.js`)**:
   - Barrel export for [`CoverageOverview`](file:///d:/SIH%202026%20Astra/astra-main/frontend/src/components/coverage/CoverageOverview.jsx), [`SurfaceBreakdown`](file:///d:/SIH%202026%20Astra/astra-main/frontend/src/components/coverage/SurfaceBreakdown.jsx), [`CoverageGapsTable`](file:///d:/SIH%202026%20Astra/astra-main/frontend/src/components/coverage/CoverageGapsTable.jsx), [`formatBytes`](file:///d:/SIH%202026%20Astra/astra-main/frontend/src/components/coverage/CoverageGapsTable.jsx#L10-L16), [`CollectorHealth`](file:///d:/SIH%202026%20Astra/astra-main/frontend/src/components/coverage/CollectorHealth.jsx), and [`EvidenceViewer`](file:///d:/SIH%202026%20Astra/astra-main/frontend/src/components/coverage/EvidenceViewer.jsx).

---

## 2. Security-State Truthfulness Standards

ASTRA strictly implements:
* `100% coverage ≠ 100% security`
* `No coverage ≠ vulnerability`
* `No evidence ≠ safe`
* `Unknown ≠ safe`
* `Unassessed ≠ safe`

All unassessed or unsupported values are explicitly rendered with neutral badge styling and descriptive text, never colored green or converted silently into 0%.

---

## 3. Files Added & Modified

### Added:
- `frontend/src/components/coverage/CoverageOverview.jsx`
- `frontend/src/components/coverage/CoverageOverview.css`
- `frontend/src/components/coverage/CoverageOverview.test.jsx`
- `frontend/src/components/coverage/SurfaceBreakdown.jsx`
- `frontend/src/components/coverage/SurfaceBreakdown.css`
- `frontend/src/components/coverage/SurfaceBreakdown.test.jsx`
- `frontend/src/components/coverage/CoverageGapsTable.jsx`
- `frontend/src/components/coverage/CoverageGapsTable.css`
- `frontend/src/components/coverage/CoverageGapsTable.test.jsx`
- `frontend/src/components/coverage/CollectorHealth.jsx`
- `frontend/src/components/coverage/CollectorHealth.css`
- `frontend/src/components/coverage/CollectorHealth.test.jsx`
- `frontend/src/components/coverage/EvidenceViewer.jsx`
- `frontend/src/components/coverage/EvidenceViewer.css`
- `frontend/src/components/coverage/EvidenceViewer.test.jsx`
- `frontend/src/components/coverage/index.js`
- `frontend/docs/P07_NOTES.md`

### Modified:
- `frontend/src/components/findings/FindingDetailModal.jsx`
- `frontend/src/components/findings/FindingDetailModal.test.jsx`
- `frontend/src/components/findings/FindingsTable.extra.test.jsx`
- `frontend/src/pages/ScanDetailPage.jsx`
- `frontend/src/pages/ScanDetailPage.test.jsx`

---

## 4. Verification Commands & Actual Results

### Frontend Verification
```powershell
npm.cmd run lint
npm.cmd test -- --coverage
npm.cmd run build
```

**Actual Results:**
- **ESLint:** 0 errors, 0 warnings (Clean)
- **Vitest Suite:** **109 passed (109 total)** across **31 test files**
- **Statement Coverage:** **93.05%** overall
  - `components/coverage`: **98.67%**
  - `components/findings`: **96.69%**
  - `pages/ScanDetailPage.jsx`: **98.68%**
  - `pages/FindingsPage.jsx`: **91.00%**
  - `api/client.js`: **91.07%**
- **Vite Production Build:** Succeeded in 7.14s (`dist/assets/index.js`: 79.82 kB gzip, `dist/assets/index.css`: 7.19 kB gzip)

### Backend Verification
```powershell
& ".venv\Scripts\python.exe" -m pytest backend/tests -q
```
**Actual Result:** **88 passed** in 1.62s (0 backend files touched).

---

## 5. Definition of Done Checklist

- [x] Coverage metrics (overall assessed %, assessed files, total files) are rendered clearly with numeric values alongside progress rings.
- [x] Evidence provenance strictly separates raw observed facts from derived interpretations.
- [x] Coverage gaps and unsupported files are disclosed truthfully with reasons and hashes.
- [x] Surface breakdown renders all documented surfaces with file counts and coverage bars.
- [x] Detector engine health telemetry is displayed.
- [x] Unknown/unassessed values use neutral styling and explicit text; no fake safe conclusions.
- [x] Existing P03/P04 components (`TabBar`, `Card`, `Badge`, `ProgressRing`, `LoadingSpinner`, `ErrorBanner`, `EmptyState`) are reused.
- [x] 109/109 frontend tests pass, 93.05% coverage, 88/88 backend tests pass.
- [x] 0 backend files modified.
