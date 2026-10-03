# ASTRA Frontend — Phase P04 Notes
**Topic:** App Shell, Routing, API Client & Hooks  
**Phase:** P04 (Frontend MVP Phase Aa Foundation)  
**Date:** 2026-10-03  
**Author:** Worker 01 (Frontend)

---

## 1. API Client Public Interface (`src/api/client.js`)

### Signatures & Exports

```typescript
export class ApiError extends Error {
  name: 'ApiError';
  status: number; // HTTP status code or 0 for network/abort
  detail: any;    // Raw backend detail (string, object, or 422 array)
  kind: 'network' | 'client' | 'server' | 'not_found' | 'too_large' | 'aborted';
}

export function apiGet(path: string, options?: { signal?: AbortSignal }): Promise<any>;

export function apiPostFile(
  path: string,
  file: File | Blob,
  onProgress?: (percent: number) => void,
  options?: { signal?: AbortSignal }
): Promise<any>;

export function getErrorMessage(error: any): string;
```

### Configuration
- `BASE_URL` defaults to empty string `''` (leveraging Vite dev server `/api` and `/health` proxies to `http://localhost:8000`) and can be overridden via `VITE_API_BASE_URL` environment variable.

### Error Message Mapping Table

| Status / Condition | `kind` | Message Construction / Template |
|---|---|---|
| `status === 0` (Network failure / fetch TypeError / XHR onerror) | `'network'` | `Unable to connect to ASTRA engine` |
| `status === 400` (Bad request / unsupported archive) | `'client'` | `The archive could not be accepted: <detail>` (or `The archive could not be accepted.`) |
| `status === 404` (Scan/Resource not found) | `'not_found'` | `Not found: <detail>` (or `Not found.`) |
| `status === 413` (Archive exceeds size limit) | `'too_large'` | `The archive is too large. <detail>` (or `The archive is too large.`) |
| `status === 422` (Validation error array) | `'client'` | Formats array into readable string, e.g. `body.scan_id: field required; query.limit: ...` |
| `status >= 500` (Server error) | `'server'` | `The ASTRA engine reported an error: <detail>` |
| Aborted request (`signal.aborted`) | `'aborted'` | `Request aborted` (silently filtered by data hooks) |

---

## 2. React Data Hooks (`src/hooks/`)

### 1. `useApi(path, options)`
- **Signature:** `useApi(path: string | null | undefined, options?: { enabled?: boolean })`
- **Return Shape:** `{ data: T | null, loading: boolean, error: ApiError | null, refetch: () => void }`
- **Behavior:**
  - Automatically skips execution when `path` is falsy or `enabled === false`.
  - Aborts in-flight requests on component unmount and when `path` changes.
  - Guards against out-of-order race conditions using an internal request sequence counter.
  - Automatically filters out aborted errors without updating error state.

### 2. `useScans()`
- **Signature:** `useScans()`
- **Return Shape:** `{ scans: Array<ScanSummary>, loading: boolean, error: ApiError | null, refetch: () => void }`
- **Backend Contract:** `GET /api/v1/scans` returns a JSON array `[{ scan_id, target_name, created_at, asset_count, coverage_percentage, dna_hash }, ...]`. Returns `[]` when loaded with no scans.

### 3. `useHealth()`
- **Signature:** `useHealth()`
- **Return Shape:** `{ health: HealthResponse | null, loading: boolean, error: ApiError | null, refetch: () => void, isHealthy: boolean }`
- **Backend Contract:** `GET /health` returns `{ status: "pass", service: "ASTRA Cryptographic Engine", version: "1.0.0", team: "HEXARK", ... }`.
- **Healthy Field:** `data.status === 'pass'`.

### 4. `usePageTitle(title)`
- **Signature:** `usePageTitle(title: string)`
- **Behavior:** Synchronizes `document.title` to `"<title> | ASTRA"` in `useEffect`. Restores nothing on unmount.

---

## 3. App Shell Layout & Routing Architecture

### Route Hierarchy
```jsx
<Routes>
  <Route element={<AppLayout />}>
    <Route path="/" element={<DashboardPage />} />
    <Route path="/scan" element={<ScanPage />} />
    <Route path="/scans/:scanId" element={<ScanDetailPage />} />
    <Route path="/findings" element={<FindingsPage />} />
    <Route path="*" element={<NotFoundPage />} />
  </Route>
  {/* Dev-Only Living Style Guide */}
  {import.meta.env.DEV && <Route path="/__styleguide" element={<DevStyleGuide />} />}
</Routes>
```

### Layout Elements & Accessibility
1. **Landmarks:** `<header className="glass-header">`, `<nav aria-label="Main navigation">`, `<main id="main-content">`, `<footer className="app-footer">`.
2. **Heading Hierarchy:** One `<h1>` per page owned exclusively by the page components (`DashboardPage`, `ScanPage`, `FindingsPage`, etc.). Header does **not** contain an `<h1>`.
3. **Skip to Main Content:** Accessible link (`<a href="#main-content" className="skip-link">`) positioned first in DOM; visually hidden until focused via keyboard Tab navigation.
4. **Active Navigation:** `NavLink` provides `aria-current="page"` and styled with `--primary-glow` and `--border-focus`.
5. **Global Notification Toast:** `react-hot-toast` `<Toaster />` mounted once at root with dark theme tokens.
6. **Error Boundary:** `<ErrorBoundary>` wraps the app root, catching unhandled rendering exceptions and offering a reload CTA.
7. **Backend-Unreachable Banner:** Displays an `ErrorBanner` above the page content with exact message `Unable to connect to ASTRA engine` and a working `Retry` button that triggers health refetching.

---

## 4. Test Suite Reconciliation (Spec-Counted vs Extras)

### Spec-Counted Tests (29 Total)
- `src/components/common/Button.test.jsx`: **3**
- `src/components/common/Card.test.jsx`: **2**
- `src/components/common/Badge.test.jsx`: **3**
- `src/components/common/LoadingSpinner.test.jsx`: **1**
- `src/components/common/ErrorBanner.test.jsx`: **2**
- `src/components/common/EmptyState.test.jsx`: **2**
- `src/components/common/TabBar.test.jsx`: **2**
- `src/components/common/Modal.test.jsx`: **3**
- `src/components/common/Tooltip.test.jsx`: **2**
- `src/components/common/ProgressRing.test.jsx`: **2**
- `src/api/client.test.js`: **4** ("GET success", "GET error", "file upload", "progress callback")
- `src/hooks/useApi.test.js`: **3** ("loading state", "success state", "error state")
**Counted Subtotal:** **29 passed**

### Extra Tests (19 Total)
- `src/components/common/Modal.extra.test.jsx`: **1** (Focus trap & return focus)
- `src/api/client.errors.extra.test.js`: **10** (400 invalid archive, 413 limit, 422 array errors, network failure message, abort signal, 204 no-content, 500 server error, XHR upload error, XHR upload abort, XHR timeout)
- `src/hooks/useApi.extra.test.js`: **6** (Skip null path, refetch, race condition protection, useScans, useHealth, usePageTitle)
- `src/components/layout/AppLayout.extra.test.jsx`: **2** (Landmarks & nav links, backend-unreachable banner)
**Total Tests Executed:** **48 passed**

---

## 5. Live Backend Verification Summary

1. **Proxy Health & Scans:** Verified live communication through Vite proxy to FastAPI backend (`http://localhost:8000/health` and `/api/v1/scans`).
2. **Navigation & Active States:** Verified navigation between Dashboard (`/`), New Scan (`/scan`), and Findings (`/findings`). Confirmed document titles updated to `Dashboard | ASTRA`, `New Scan | ASTRA`, and `Findings | ASTRA`.
3. **Backend Failure & Recovery:**
   - Terminated uvicorn backend server process.
   - Refreshed page: Header status badge shifted to `Engine unreachable` and the red error banner `Unable to connect to ASTRA engine` rendered with a `Retry` action.
   - Restarted uvicorn backend process and clicked `Retry`: Error banner cleared immediately and status badge recovered to `Engine online`.
   - Complete browser interaction recording saved at `retry_recovery_check_*.webp`.
