# Worker 01 Phase Aa Report: React Frontend Foundation & Core Scan Workflow

**Owner:** Discovery & Frontend Architecture (Worker 01)  
**Stage:** Frontend React App — Phase 1 of 2  
**Phase:** Phase Aa  
**Status:** SPECIFICATION & ARCHITECTURE DESIGN COMPLETE  
**Traceability IDs:** R01, R02, R05, R10, R12  
**Acceptance Criteria:** AC-01, AC-02, AC-11, AC-13  
**Date:** 2026-10-03  

---

## 1. Executive Summary & Objective

Phase Aa designs the production-grade React application foundation to replace the preliminary static HTML dashboard with an enterprise-ready Single Page Application (SPA). Aligned with SIH26164 (ECDAT) requirements and ASTRA’s backend v1 API contracts (`/api/v1/scans/*`, `/health`), this phase establishes the design token system, core navigation shell, upload intake dropzone, scan history tracking, tabular findings explorer, and truthful coverage accounting views.

---

## 2. Technical Stack & Architectural Decisions

| Layer | Selection | Justification |
|---|---|---|
| **Build System** | Vite 5.x | Native ESM, instant HMR, zero-config production bundling |
| **UI Framework** | React 18 + React Router v6 | Declarative component model with client-side SPA routing |
| **Language** | JavaScript (ES2022 / JSX) | Full alignment with existing repository conventions |
| **Styling** | Vanilla CSS (CSS Variables) | Enforces curated dark-mode design system with zero CSS-in-JS runtime overhead |
| **Network Client** | Native `fetch` with typed API client | Lightweight, dependency-free wrapper with retry and error interceptors |
| **Iconography** | Lucide React | Tree-shakeable, clean SVGs for security and navigation indicators |
| **Data Viz** | Recharts | Composable SVG-based coverage charts and risk indicators |
| **Test Runner** | Vitest + React Testing Library + jsdom | Lightning-fast unit and component test harness |

---

## 3. Component & Page Inventory Designed

### 3.1 Routing & Layout
- **Router Shell (`App.jsx`)**: Responsive sidebar, top header with live backend `/health` heartbeat indicator, and dynamic route rendering.
- **`DashboardPage.jsx`**: Global inventory summary metrics, recent scans, system status.
- **`ScanPage.jsx`**: Safe drag-and-drop archive intake (`.zip`, `.tar.gz`, `.tar.bz2`) with real-time pre-upload boundary checks.
- **`ScanDetailPage.jsx`**: Detailed scan audit view featuring multi-surface coverage breakdown, scan manifest metadata, and findings navigation.
- **`FindingsPage.jsx`**: Interactive tabular findings explorer with severity filters, algorithm search, and file path inspection.
- **`NotFoundPage.jsx`**: Graceful 404 handler with quick navigation fallback.

### 3.2 Core UI Components
- **`UploadDropzone.jsx`**: File format validation, boundary verification, compression ratio warning banner, upload progress.
- **`ScanHistoryTable.jsx`**: Tabular scan records, scan status badges (`COMPLETE`, `PARTIAL`, `FAILED`), timestamp formatting.
- **`ScanSummaryCard.jsx`**: Metric callouts for Total Findings, Critical Algorithms, Assessed Surfaces, Duration.
- **`FindingsTable.jsx`**: Algorithmic classification, location, line numbers, severity badges, and secret redaction verification.
- **`CoverageBar.jsx`**: Truthful denominator tracking across Source, Manifest, Config, Certificate surfaces with unassessed file warnings.
- **`ObservationDetail.jsx`**: Slide-over drawer displaying raw evidence, matched ruleset signature, and NIST PQC mapping.

---

## 4. Test Strategy & Verification Matrix

Phase Aa defines **43 automated test suites** ensuring robust client-side behavior:

1. **Unit Tests (37 tests)**:
   - `client.test.js`: API fetch wrappers, 4xx/5xx handling, network timeouts.
   - `useApi.test.js`, `useScans.test.js`, `useHealth.test.js`: State hooks, polling lifecycle, cleanup.
   - `Button.test.jsx`, `Badge.test.jsx`, `Card.test.jsx`, `LoadingSpinner.test.jsx`, `ErrorBanner.test.jsx`, `EmptyState.test.jsx`: Primitives and visual feedback.
   - `UploadDropzone.test.jsx`: Drag-and-drop events, blocked extension rejections, file size enforcement.
   - `ScanHistoryTable.test.jsx`: Sorting, pagination, status badge styling.
   - `FindingsTable.test.jsx`: Text search filtering, severity selection, row selection.
   - `CoverageBar.test.jsx`: Segment percentage calculations, truthfulness labels (preventing false "Quantum Safe" claims).
   - `ObservationDetail.test.jsx`: Parameter rendering, private key redaction confirmation.

2. **Integration Tests (3 tests)**:
   - `DashboardPage.integration.test.jsx`: Mounts page, fetches `/health` and recent scans, renders summary cards.
   - `ScanPage.integration.test.jsx`: Simulates archive drop, initiates intake POST, verifies navigation to detail view.
   - `ScanDetailPage.integration.test.jsx`: Loads scan ID, fetches findings & coverage, verifies tab switching.

3. **Smoke Tests (3 tests)**:
   - `app.smoke.test.jsx`: Zero-crash root mount.
   - `routing.smoke.test.jsx`: Validation of all declared client routes.
   - `vite.build.test.js`: Production bundle build verification.

---

## 5. Artifact Deliverables & Locations

- **Detailed Specification**: [phase_Aa.md](file:///c:/Users/adity/OneDrive/Desktop/sih--p2/.brain/.work/webapp/worker_01/mvp_phases/phase_Aa.md)
- **Work Report (Internal)**: `.brain/.work/.report/phase_Aa_report.md`
- **Audit Report (Public)**: `.brain/.report/phase_Aa_report.md`
- **Target Implementation Directory**: `frontend/src/`
