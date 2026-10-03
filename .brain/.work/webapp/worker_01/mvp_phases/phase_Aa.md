# Phase Aa — React Frontend Foundation & Core Scan Workflow

**Owner:** Worker 01 (Frontend)  
**Stage:** Frontend React App — Phase 1 of 2  
**Status:** PLANNED — no implementation or test execution claimed  
**Traceability IDs:** R01, R02, R05, R10, R12  
**Acceptance mapping:** AC-01, AC-02, AC-11, AC-13  
**Depends on:** Backend API v1 endpoints (`/api/v1/scans/*`, `/health`)  
**Prerequisite:** All backend MVP + PROD phases validated (74/74 tests passing)

---

## 1. Objective

Build the React application foundation — project scaffold, design system, routing shell, and the **core scan workflow**: upload archives, view scan history, inspect findings, and drill into coverage reports. This phase delivers a fully functional, API-connected frontend that replaces the existing static `frontend/index.html` prototype.

---

## 2. Tech Stack & Tooling Decision

| Layer | Choice | Rationale |
|---|---|---|
| Build tool | Vite 5.x (already in `package.json`) | Fast HMR, native ESM, zero-config React |
| Framework | React 18 + React Router v6 | SPA with client-side routing |
| Language | JavaScript (JSX) | Matches existing project; no TS migration needed |
| Styling | Vanilla CSS (design tokens via CSS custom properties) | Per project guidelines; no Tailwind |
| HTTP client | `fetch` API (native) | No extra deps; CORS already configured on backend |
| Icons | Lucide React | Lightweight, tree-shakeable SVG icons |
| Charts | Recharts | React-native charting for coverage/risk viz |
| Testing | Vitest + React Testing Library | Vite-native; fast unit/component tests |
| Linting | ESLint (Vite default) | Code quality gate |

---

## 3. Project Scaffold — Task Breakdown

### 3.1 Initialize React in existing `frontend/` directory

```
frontend/
├── index.html              ← Vite entry (update existing)
├── package.json             ← Add React deps
├── vite.config.js           ← Proxy /api to backend
├── src/
│   ├── main.jsx             ← React DOM root
│   ├── App.jsx              ← Router + layout shell
│   ├── index.css            ← Global design tokens
│   ├── api/
│   │   └── client.js        ← Centralized fetch wrapper
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Header.jsx
│   │   │   ├── Sidebar.jsx
│   │   │   └── Footer.jsx
│   │   ├── common/
│   │   │   ├── Button.jsx
│   │   │   ├── Card.jsx
│   │   │   ├── Badge.jsx
│   │   │   ├── LoadingSpinner.jsx
│   │   │   ├── ErrorBanner.jsx
│   │   │   └── EmptyState.jsx
│   │   └── scan/
│   │       ├── UploadDropzone.jsx
│   │       ├── ScanHistoryTable.jsx
│   │       ├── ScanSummaryCard.jsx
│   │       ├── FindingsTable.jsx
│   │       ├── CoverageBar.jsx
│   │       └── ObservationDetail.jsx
│   ├── pages/
│   │   ├── DashboardPage.jsx
│   │   ├── ScanPage.jsx
│   │   ├── ScanDetailPage.jsx
│   │   ├── FindingsPage.jsx
│   │   └── NotFoundPage.jsx
│   └── hooks/
│       ├── useApi.js
│       ├── useScans.js
│       └── useHealth.js
```

### 3.2 Install Dependencies

```bash
npm install react react-dom react-router-dom lucide-react recharts
npm install -D @vitejs/plugin-react vitest @testing-library/react @testing-library/jest-dom jsdom
```

### 3.3 Vite Configuration

```js
// vite.config.js
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/health': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.js',
  },
});
```

---

## 4. Design System — CSS Token Architecture

### 4.1 Design Tokens (`src/index.css`)

Preserve the existing dark theme from the static prototype:

| Token Category | Variables |
|---|---|
| Colors — Base | `--bg-base`, `--bg-surface`, `--bg-card`, `--bg-card-hover` |
| Colors — Borders | `--border-subtle`, `--border-focus` |
| Colors — Accents | `--primary`, `--cyan`, `--emerald`, `--amber`, `--rose`, `--purple` |
| Colors — Text | `--text-main`, `--text-muted`, `--text-dim` |
| Typography | `--font-sans` (Outfit), `--font-mono` (JetBrains Mono) |
| Spacing | `--space-xs` through `--space-3xl` (4px to 48px scale) |
| Radii | `--radius-sm`, `--radius-md`, `--radius-lg`, `--radius-xl` |
| Shadows | `--shadow-card`, `--shadow-elevated`, `--shadow-glow` |
| Transitions | `--transition-fast`, `--transition-normal`, `--transition-slow` |

### 4.2 Component CSS Architecture

- One `.css` file per component directory (co-located)
- BEM-lite naming: `.scan-history__row`, `.upload-zone--active`
- Glassmorphism utilities: `.glass-panel`, `.glass-header`
- Animations: `@keyframes fadeIn`, `@keyframes slideUp`, `@keyframes pulse-glow`

---

## 5. Core Pages — Detailed Specifications

### 5.1 Dashboard Page (`/`)

**Purpose:** At-a-glance system status and recent scan overview.

| Section | Data Source | Components |
|---|---|---|
| Health Status Banner | `GET /health` | `Badge` (pass/fail), uptime indicator |
| Quick Stats Row | Aggregated from `/api/v1/scans` | 4x `Card` — Total Scans, Total Assets, Avg Coverage%, Critical Risks |
| Recent Scans List | `GET /api/v1/scans` (latest 5) | `ScanHistoryTable` (compact mode) |
| Upload CTA | — | `Button` navigates to `/scan` |

**Interactions:**
- Health badge pulses green when `status: "pass"`
- Stats cards animate count-up on mount
- Click any scan row navigates to `/scans/:scanId`

### 5.2 Scan Page (`/scan`)

**Purpose:** Upload archives and trigger scans.

| Section | Data Source | Components |
|---|---|---|
| Upload Dropzone | `POST /api/v1/scans/upload` | `UploadDropzone` — drag-and-drop + click-to-browse |
| Upload Progress | Local state | Progress bar, file name, byte counter |
| Scan Result | API response | `ScanSummaryCard` with asset count, coverage %, DNA hash |

**Interactions:**
- Drag-over visual feedback (border glow, icon change)
- File type validation client-side (`.zip`, `.tar`, `.tar.gz`, `.tar.bz2`)
- Upload progress via `XMLHttpRequest` with progress events
- On success auto-navigate to `/scans/:scanId`
- On error show `ErrorBanner` with detail message

**Validation Rules:**
- Max file size: 100 MB (match backend `max_upload_size`)
- Reject non-archive MIME types before upload
- Show human-readable error for 413, 400, 500 responses

### 5.3 Scan Detail Page (`/scans/:scanId`)

**Purpose:** Comprehensive view of a single scan's results.

| Tab | Endpoint | Components |
|---|---|---|
| Overview | `GET /api/v1/scans/:scanId` | `ScanSummaryCard`, DNA hash display, timestamp |
| Findings | `GET /api/v1/scans/:scanId/findings` | `FindingsTable` — sortable, filterable |
| Coverage | `GET /api/v1/scans/:scanId/coverage` | `CoverageBar` per surface, overall gauge |

**Findings Table Columns:**
1. Algorithm Name
2. Purpose (Encryption / Signing / Hashing / Key Exchange)
3. Quantum Safety (badge: Safe / Vulnerable / Unknown)
4. Source File and Line
5. Confidence Level
6. Detector Name

**Interactions:**
- Click finding row to expand `ObservationDetail` inline
- Sort by any column header
- Filter by quantum safety status
- Search box for algorithm/file name
- Copy DNA hash to clipboard

### 5.4 Findings Page (`/findings`)

**Purpose:** Cross-scan aggregated view of all cryptographic observations.

- Aggregate findings from all scans via `GET /api/v1/scans` then `GET /api/v1/scans/:id/findings`
- Group by algorithm family (RSA, AES, SHA, ECC, PQC)
- Bar chart showing algorithm distribution (Recharts)
- Pie chart showing quantum safety breakdown

---

## 6. API Client Layer

### 6.1 `src/api/client.js`

```js
const BASE_URL = '';  // Vite proxy handles /api prefix

export async function apiGet(path) {
  const res = await fetch(`${BASE_URL}${path}`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export async function apiPostFile(path, file, onProgress) {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open('POST', `${BASE_URL}${path}`);
    xhr.upload.onprogress = (e) => {
      if (e.lengthComputable && onProgress) {
        onProgress(Math.round((e.loaded / e.total) * 100));
      }
    };
    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        resolve(JSON.parse(xhr.responseText));
      } else {
        try {
          reject(new Error(JSON.parse(xhr.responseText).detail));
        } catch {
          reject(new Error(`Upload failed: HTTP ${xhr.status}`));
        }
      }
    };
    xhr.onerror = () => reject(new Error('Network error'));
    const formData = new FormData();
    formData.append('file', file);
    xhr.send(formData);
  });
}
```

### 6.2 Custom Hooks

| Hook | Purpose | Returns |
|---|---|---|
| `useApi(path)` | Generic GET with loading/error state | `{ data, loading, error, refetch }` |
| `useScans()` | `GET /api/v1/scans` | `{ scans, loading, error }` |
| `useHealth()` | `GET /health` | `{ health, loading, error }` |

---

## 7. Routing Configuration

```jsx
// App.jsx routes
<Routes>
  <Route path="/" element={<DashboardPage />} />
  <Route path="/scan" element={<ScanPage />} />
  <Route path="/scans/:scanId" element={<ScanDetailPage />} />
  <Route path="/findings" element={<FindingsPage />} />
  <Route path="*" element={<NotFoundPage />} />
</Routes>
```

---

## 8. Accessibility and SEO Requirements

- All pages set `document.title` via `useEffect`
- Single `<h1>` on every page, proper heading hierarchy
- All interactive elements have unique `id` attributes for testing
- Keyboard navigation: Tab order, Enter/Space activation
- ARIA labels on icons, badges, and status indicators
- Color contrast: WCAG 2.1 AA (4.5:1 minimum for text)
- Focus-visible outlines on all focusable elements

---

## 9. Error and Edge Case Handling

| Scenario | Behavior |
|---|---|
| Backend unreachable | `ErrorBanner` with "Unable to connect to ASTRA engine" + retry button |
| Empty scan list | `EmptyState` with upload CTA |
| Scan not found (404) | Redirect to `/` with toast notification |
| Upload exceeds 100 MB | Client-side rejection before upload starts |
| Invalid archive format | Inline error below dropzone |
| Scan in progress | Loading spinner with elapsed time counter |
| API returns 500 | `ErrorBanner` with error detail from response body |

---

## 10. Phase Aa Test Plan

### 10.1 Unit Tests (Vitest + React Testing Library)

| Test File | Tests | Description |
|---|---|---|
| `Button.test.jsx` | 3 | Renders, handles click, disabled state |
| `Card.test.jsx` | 2 | Renders children, applies variant classes |
| `Badge.test.jsx` | 3 | Renders text, applies status colors (safe/vulnerable/unknown) |
| `LoadingSpinner.test.jsx` | 1 | Renders with aria-label |
| `ErrorBanner.test.jsx` | 2 | Renders message, retry button fires callback |
| `EmptyState.test.jsx` | 2 | Renders message, CTA button navigates |
| `UploadDropzone.test.jsx` | 5 | Drag events, file validation, size limit, upload trigger, error display |
| `ScanHistoryTable.test.jsx` | 4 | Renders rows, empty state, click navigation, timestamp formatting |
| `FindingsTable.test.jsx` | 5 | Column sort, filter, search, row expand, empty state |
| `CoverageBar.test.jsx` | 3 | Percentage display, color thresholds, zero coverage |
| `client.test.js` | 4 | GET success, GET error, file upload, progress callback |
| `useApi.test.js` | 3 | Loading state, success state, error state |
| **Total** | **37** | |

### 10.2 Integration Tests

| Test | Description |
|---|---|
| `DashboardPage.integration.test.jsx` | Mounts page, fetches health + scans, renders cards |
| `ScanPage.integration.test.jsx` | Mounts page, simulates upload, verifies navigation on success |
| `ScanDetailPage.integration.test.jsx` | Mounts with route param, fetches scan data, renders tabs |

### 10.3 Smoke Tests

| Test | Description |
|---|---|
| `app.smoke.test.jsx` | App mounts without crash |
| `routing.smoke.test.jsx` | All routes resolve to correct pages |
| `vite.build.test.js` | `npm run build` completes without errors |

### 10.4 Test Commands

```bash
# Run all tests
npx vitest run

# Run with coverage
npx vitest run --coverage

# Watch mode during development
npx vitest
```

### 10.5 Expected Results

- **Minimum:** 37 unit tests + 3 integration tests + 3 smoke tests = **43 tests passing**
- **Coverage target:** 80% or higher line coverage on `src/components/` and `src/api/`
- **Build gate:** `npm run build` exits with code 0

---

## 11. Report and Documentation Requirements

### 11.1 Reports to Generate

After all tests pass, create the following report files:

| File | Location |
|---|---|
| `phase_Aa_report.md` | `.brain/.work/.report/phase_Aa_report.md` |
| `phase_Aa_report.md` | `.brain/.report/phase_Aa_report.md` |

### 11.2 Report Contents

The report must contain:
- Date (ISO timestamp)
- Status (PASSED / FAILED)
- Test Results (X passed / Y total with pass rate percentage)
- Build Status (SUCCESS / FAILED)
- Coverage (line coverage percentage)
- Summary of what was implemented
- Vitest output summary
- List of all new/changed files
- Known Issues or items deferred to Phase Ab
- Git Commit hash, branch, and push status

---

## 12. Git Workflow

1. Stage all new frontend files: `git add frontend/src/ frontend/vite.config.js frontend/package.json`
2. Stage phase planning docs: `git add .brain/.work/webapp/worker_01/mvp_phases/phase_Aa.md`
3. Stage reports: `git add .brain/.work/.report/phase_Aa_report.md .brain/.report/phase_Aa_report.md`
4. Commit: `git commit -m "feat(frontend): Phase Aa — React foundation, design system, core scan workflow"`
5. Push: `git push origin main`

---

## 13. Success Criteria

- [ ] React app boots via `npm run dev` and renders dashboard
- [ ] Health endpoint displayed with live status
- [ ] Archive upload then scan completion then results displayed
- [ ] Scan history table populated from API
- [ ] Findings table with sort/filter/search
- [ ] Coverage visualization per surface
- [ ] All 43+ tests passing
- [ ] 80%+ line coverage on components and API layer
- [ ] `npm run build` produces error-free production bundle
- [ ] Reports generated in both `.brain/.work/.report/` and `.brain/.report/`
- [ ] Changes committed and pushed to `adishxm/astra` main branch

---

## 14. Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Backend not running during frontend dev | Vite proxy returns clear error; mock data in tests |
| Existing `frontend/index.html` conflicts | Backup existing file; new React app replaces it via Vite build |
| Large archive uploads timeout | Client-side progress bar + backend streaming already handles this |
| CSS naming collisions | BEM naming convention + scoped component files |
| Browser compatibility gaps | Target modern browsers (ES2020+); Vite handles polyfills |

---

## 15. Handoff to Phase Ab

Phase Aa delivers:
- Running React app with routing and design system
- Core scan workflow (upload, results, findings)
- API client layer with error handling
- 43+ passing tests

Phase Ab will build upon this to add:
- Risk analysis dashboard with Mosca timeline
- CBOM export viewer
- Interactive migration roadmap
- Real-time scan progress
- Advanced filtering and comparison views
