# Worker 01 Phase Ab Report: Risk Dashboard, CBOM Export & Advanced Visualizations

**Owner:** Discovery & Frontend Architecture (Worker 01)  
**Stage:** Frontend React App — Phase 2 of 2  
**Phase:** Phase Ab  
**Status:** SPECIFICATION & ARCHITECTURE DESIGN COMPLETE  
**Traceability IDs:** R01, R02, R03, R04, R05, R06, R10, R12  
**Acceptance Criteria:** AC-03, AC-04, AC-05, AC-06, AC-07, AC-08, AC-09, AC-10, AC-12  
**Date:** 2026-10-03  

---

## 1. Executive Summary & Objective

Phase Ab extends the Phase Aa foundation into a comprehensive cryptographic governance and PQC migration platform. It delivers interactive Mosca migration deadline visualizations ($X + Y > Z$), dynamic CRQC collapse horizon sliders, hierarchical CycloneDX 1.6 CBOM inspection with streaming export, multi-scanner reconciliation diffs, cryptographic DNA drift tracking over time, dependency-aware migration roadmaps with cycle detection, and cryptographic audit chain verification.

---

## 2. Advanced Technology Stack Additions

| Library | Version | Purpose |
|---|---|---|
| **`framer-motion`** | ^11.x | Fluid page transitions, tab underlines, timeline bar animations |
| **`react-hot-toast`** | ^2.4 | Accessible, non-blocking toast notifications for export and copy operations |
| **`file-saver`** | ^2.0 | Memory-safe client-side streaming download of CycloneDX 1.6 CBOM JSON |

---

## 3. Advanced Features & Component Architecture

### 3.1 Interactive Mosca Theorem & Risk Dashboard (`/risk/:scanId`)
- **`MoscaTimeline.jsx`**: Visualizes shelf life ($X$), migration time ($Y$), and quantum threat horizon ($Z$). Dynamic color transitions (Green for safe slack, Amber for approaching deadline, Crimson Red for $X+Y > Z$ migration failure).
- **`RiskSlider.jsx`**: Debounced (300ms) interactive controls allowing CISO/security analysts to test varying CRQC horizon estimates (e.g., 2029 vs 2035) with live backend recalculation.
- **`RiskHeatmap.jsx`**: Multi-dimensional matrix mapping algorithmic risk classes (Classical Broken, Transition Vulnerable, Quantum Safe) against operational severity.
- **`BacklogTable.jsx`**: Prioritized remediation task list with candidate PQC replacements (e.g. ML-KEM / FIPS 203, ML-DSA / FIPS 204, SLH-DSA / FIPS 205) and CSV export.

### 3.2 CycloneDX 1.6 CBOM Explorer & Reconciliation (`/cbom/:scanId`)
- **`CBOMTreeView.jsx`**: Hierarchical component tree rendering crypto assets categorized by algorithm type, key size, curves, and file origins.
- **`CBOMExportPanel.jsx`**: Instant download and clipboard copy of official CycloneDX 1.6 JSON with integrated schema validity badges.
- **`ReconciliationView.jsx`**: Dual-pane diff comparing ASTRA's native findings against third-party scanner outputs, highlighting consensus and discrepancies.

### 3.3 Cryptographic DNA Drift & Migration Roadmap (`/roadmap/:scanId`)
- **`DriftTimeline.jsx`**: Tracks temporal changes in repository cryptographic signatures across successive commits/scans.
- **`SnapshotCompare.jsx`**: Side-by-side diff highlighting introduced crypto algorithms and deprecated ciphers.
- **`MigrationRoadmap.jsx`**: Topologically sorted visual execution phases with circular dependency detection and bottleneck warnings.

### 3.4 Governance, Audit Chain & Production Health (`/audit`, `/settings`)
- **`AuditChainViewer.jsx`**: Inspects append-only, SHA-256 tamper-evident audit logs with live chain integrity badge (`VERIFIED` vs `BROKEN`).
- **`HealthDashboard.jsx`**: Production readiness monitor verifying air-gapped readiness, zero external telemetry leakage, and collector health.
- **`SettingsPage.jsx`**: Configures local API URLs, alert thresholds, dark/light theme preferences, stored in browser `localStorage`.

---

## 4. Test Strategy & Verification Matrix

Phase Ab specifies **73 automated test suites**, delivering an aggregate frontend test count of **116 tests**:

1. **Phase Ab Unit Tests (65 tests)**:
   - `MoscaTimeline.test.jsx` (4), `RiskSlider.test.jsx` (3), `RiskScoreCard.test.jsx` (3), `RiskHeatmap.test.jsx` (3), `BacklogTable.test.jsx` (4)
   - `CBOMTreeView.test.jsx` (4), `CBOMExportPanel.test.jsx` (3), `ReconciliationView.test.jsx` (3)
   - `DriftTimeline.test.jsx` (3), `SnapshotCompare.test.jsx` (3)
   - `MigrationRoadmap.test.jsx` (4), `RoadmapNode.test.jsx` (2)
   - `AuditChainViewer.test.jsx` (4), `HealthDashboard.test.jsx` (3)
   - `TabBar.test.jsx` (2), `Modal.test.jsx` (3), `Tooltip.test.jsx` (2), `ProgressRing.test.jsx` (2)
   - `useRisk.test.js` (3), `useCBOM.test.js` (2), `useDebounce.test.js` (2), `useLocalSettings.test.js` (3)

2. **Integration Tests (5 tests)**:
   - `RiskPage.integration.test.jsx`: Scan risk fetch, slider interaction, live update.
   - `CBOMPage.integration.test.jsx`: Tree expansion, JSON download simulation.
   - `RoadmapPage.integration.test.jsx`: Dependency graph rendering and phase grouping.
   - `AuditPage.integration.test.jsx`: Hash chain traversal and verification badge.
   - `SettingsPage.integration.test.jsx`: Preference mutation and persistence.

3. **Cross-Phase Smoke Tests (3 tests)**:
   - `full-navigation.smoke.test.jsx`: Seamless routing across all Phase Aa and Phase Ab views.
   - `responsive.smoke.test.jsx`: Layout reflow across desktop (1440px), tablet (768px), and mobile (375px).
   - `production-build.smoke.test.js`: Full tree-shaken Vite production bundle verification.

---

## 5. Artifact Deliverables & Locations

- **Detailed Specification**: [phase_Ab.md](file:///c:/Users/adity/OneDrive/Desktop/sih--p2/.brain/.work/webapp/worker_01/mvp_phases/phase_Ab.md)
- **Work Report (Internal)**: `.brain/.work/.report/phase_Ab_report.md`
- **Audit Report (Public)**: `.brain/.report/phase_Ab_report.md`
- **Target Implementation Directory**: `frontend/src/`
