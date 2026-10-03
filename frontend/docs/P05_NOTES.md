# ASTRA Frontend — Phase P05 Notes
**Topic:** Dashboard & Scan Upload  
**Phase:** P05 (Frontend MVP Phase Aa Complete)  
**Date:** 2026-10-03  
**Author:** Worker 01 (Frontend)

---

## 1. Resolution & Verification of Previous Gaps (Section 0)

| Gap Area | Verification / Fix Implemented | Evidence / Test Status |
|---|---|---|
| **1. Tooltip Coverage & Focus/Escape** | Added [Tooltip.extra.test.jsx](file:///d:/SIH%202026%20Astra/astra-main/frontend/src/components/common/Tooltip.extra.test.jsx) covering keyboard focus/blur, Escape key dismissal, non-element string children, and viewport collision flipping. | `Tooltip.jsx` statement & line coverage increased to **95.74%**. |
| **2. ErrorBoundary Coverage** | Added [ErrorBoundary.test.jsx](file:///d:/SIH%202026%20Astra/astra-main/frontend/src/components/common/ErrorBoundary.test.jsx) verifying both error-free child rendering and unhandled render crash fallback. | `ErrorBoundary.jsx` statement & line coverage increased to **87.87%**. |
| **3. `--text-dim` Contrast & Usage** | Verified `--text-dim` (`#64748b`) is strictly restricted to non-essential decorative text (e.g. "Runs locally. No telemetry." footer and inactive empty placeholder dashes). Essential text uses `--text-main` (18.57:1) and `--text-muted` (7.58:1). | `check_contrast.mjs` passes all essential tokens. |
| **4. `client.js` Coverage** | Added test cases for 204 No Content, 500 server error fallbacks, XHR timeouts, and abort signals in [client.errors.extra.test.js](file:///d:/SIH%202026%20Astra/astra-main/frontend/src/api/client.errors.extra.test.js). | `client.js` statement & line coverage reached **91.07%**. |
| **5. CSS Gzip-Size Discrepancy** | Font subsets were trimmed to Latin-only in P03 (down from 35 files to 12 files). Production CSS bundle size is **24.87 kB raw (4.97 kB gzip)** with all components, layout, dashboard, and scan upload styles included. | `vite build` completed in ~7.5s. |
| **6. Skip-Link Accessibility** | `<a href="#main-content" className="skip-link">` tested via keyboard Tab focus, targeting `<main id="main-content">`. | Verified in [AppLayout.extra.test.jsx](file:///d:/SIH%202026%20Astra/astra-main/frontend/src/components/layout/AppLayout.extra.test.jsx) and live browser review. |
| **7. Toaster Configuration & Feedback** | Configured `react-hot-toast` `<Toaster />` in `App.jsx` with design tokens and triggered live toasts via `toast.success` and `toast.error` in `ScanUpload.jsx`. | Verified in [ScanUpload.test.jsx](file:///d:/SIH%202026%20Astra/astra-main/frontend/src/components/scan/ScanUpload.test.jsx). |

---

## 2. Dashboard Functionality (`src/pages/DashboardPage.jsx`)

1. **KPI Stat Cards:**
   - **Total Discovered Assets:** Sum of asset counts across completed scans (`useScans()`). Displays `0` with "No archives scanned yet" when empty.
   - **Post-Quantum Coverage:** Latest scan coverage percentage rendered using `ProgressRing`. Displays neutral `—` with `Unassessed` badge when unassessed (honest state, never green/safe).
   - **Engine Service Status:** Live indicator connecting to `useHealth()`. Displays `Online` (safe badge) when healthy.
2. **Actionable Scan CTA:**
   - Prominent "New Scan" action in header and dedicated `EmptyState` CTA when no scans exist.
3. **Recent Scans Table:**
   - Lists target archives, scan IDs, formatted dates, asset counts, PQC coverage badges (safe >= 80%, medium >= 50%, high < 50%), and "View" action button linking to `/scans/${scan_id}`.
4. **Resilient UI States:**
   - **Loading:** `LoadingSpinner` with accessible status announcement.
   - **Error:** `ErrorBanner` with working `refetchScans` retry trigger.
   - **Empty:** `EmptyState` with prompt to upload repository archive.

---

## 3. Scan Upload Functionality (`src/components/scan/ScanUpload.jsx`)

1. **Supported Archive Formats:** `.zip`, `.tar`, `.tar.gz`, `.tgz`, `.tar.bz2`, `.tbz2` (aligned with backend `POST /api/v1/scans/upload`).
2. **Intake Size Limit:** 100 MB maximum size limit enforced both client-side and backend streaming.
3. **Input Validation (`validateScanFile`):**
   - Blocks missing selection.
   - Blocks zero-byte empty archives (`"Uploaded archive is zero bytes."`).
   - Blocks archives exceeding 100 MB (`"Uploaded archive exceeds maximum limit of 100 MB"`).
   - Blocks unsupported extensions (`"Unsupported archive format. Expected one of: .zip, .tar, .tar.gz, .tar.bz2"`).
4. **Progress & Submission Lifecycle:**
   - `idle` → `selected` → `uploading` (0–100% real XHR progress) → `analyzing` (elapsed seconds timer) → `success` / `error`.
   - Prevents duplicate submissions while active (buttons disabled, dropzone locked).
   - Supports request cancellation via `AbortController` (`Cancel Scan` button).
5. **Feedback & Notifications:**
   - Triggers `toast.success` upon completion and `toast.error` on failure.
   - Renders success panel with discovered asset count and link to scan details.

---

## 4. Test Suite Summary

### All Tests: 66 Passed across 21 Test Files

```text
 ✓ src/api/client.test.js (4 tests)
 ✓ src/api/client.errors.extra.test.js (10 tests)
 ✓ src/hooks/useApi.test.js (3 tests)
 ✓ src/hooks/useApi.extra.test.js (6 tests)
 ✓ src/components/common/Button.test.jsx (3 tests)
 ✓ src/components/common/Card.test.jsx (2 tests)
 ✓ src/components/common/Badge.test.jsx (3 tests)
 ✓ src/components/common/LoadingSpinner.test.jsx (1 test)
 ✓ src/components/common/ErrorBanner.test.jsx (2 tests)
 ✓ src/components/common/EmptyState.test.jsx (2 tests)
 ✓ src/components/common/TabBar.test.jsx (2 tests)
 ✓ src/components/common/Modal.test.jsx (3 tests)
 ✓ src/components/common/Modal.extra.test.jsx (1 test)
 ✓ src/components/common/Tooltip.test.jsx (2 tests)
 ✓ src/components/common/Tooltip.extra.test.jsx (3 tests)
 ✓ src/components/common/ProgressRing.test.jsx (2 tests)
 ✓ src/components/common/ErrorBoundary.test.jsx (2 tests)
 ✓ src/components/layout/AppLayout.extra.test.jsx (2 tests)
 ✓ src/components/scan/ScanUpload.test.jsx (7 tests)
 ✓ src/pages/DashboardPage.test.jsx (5 tests)
 ✓ src/pages/ScanPage.test.jsx (1 test)
```

### Coverage Percentages
- `api/`: **91.07%**
- `components/common/`: **91.32%**
- `components/layout/`: **92.98%**
- `components/scan/`: **81.04%**
- `hooks/`: **91.07%**
- `pages/DashboardPage.jsx`: **99.49%**
- **Overall Code Coverage:** **85.02%**
