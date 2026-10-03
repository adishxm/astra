# Phase Ab — Risk Dashboard, CBOM Export & Advanced Visualizations

**Owner:** Worker 01 (Frontend)  
**Stage:** Frontend React App — Phase 2 of 2  
**Status:** PLANNED — no implementation or test execution claimed  
**Traceability IDs:** R01, R02, R03, R04, R05, R06, R10, R12  
**Acceptance mapping:** AC-03, AC-04, AC-05, AC-06, AC-07, AC-08, AC-09, AC-10, AC-12  
**Depends on:** Phase Aa completed (43+ tests passing, core scan workflow functional)  
**Prerequisite:** Phase Aa React app running with routing, API client, and design system

---

## 1. Objective

Extend the Phase Aa foundation with **risk analysis visualization**, **CBOM export viewer**, **migration roadmap UI**, **temporal drift timeline**, **advanced comparison views**, and **production hardening controls**. This phase completes the full-featured ASTRA Web Dashboard.

---

## 2. New Dependencies (Additions to Phase Aa)

| Package | Purpose |
|---|---|
| `framer-motion` | Page transitions, list animations, chart reveal |
| `react-hot-toast` | Non-blocking toast notifications |
| `file-saver` | Client-side CBOM/report download |

```bash
npm install framer-motion react-hot-toast file-saver
```

---

## 3. New Component Architecture

### 3.1 Additional File Tree

```
frontend/src/
├── components/
│   ├── risk/
│   │   ├── MoscaTimeline.jsx       ← X+Y>Z visual timeline
│   │   ├── MoscaTimeline.css
│   │   ├── RiskScoreCard.jsx       ← Individual asset risk score
│   │   ├── RiskScoreCard.css
│   │   ├── RiskHeatmap.jsx         ← Algorithm x Severity matrix
│   │   ├── RiskHeatmap.css
│   │   ├── RiskSlider.jsx          ← CRQC horizon slider control
│   │   ├── RiskSlider.css
│   │   ├── BacklogTable.jsx        ← Migration backlog task list
│   │   └── BacklogTable.css
│   ├── cbom/
│   │   ├── CBOMTreeView.jsx        ← Hierarchical CBOM component tree
│   │   ├── CBOMTreeView.css
│   │   ├── CBOMExportPanel.jsx     ← Download CycloneDX 1.6 JSON
│   │   ├── CBOMExportPanel.css
│   │   ├── ReconciliationView.jsx  ← Multi-scanner comparison
│   │   └── ReconciliationView.css
│   ├── temporal/
│   │   ├── DriftTimeline.jsx       ← Cryptographic DNA drift over time
│   │   ├── DriftTimeline.css
│   │   ├── SnapshotCompare.jsx     ← Side-by-side snapshot diff
│   │   └── SnapshotCompare.css
│   ├── roadmap/
│   │   ├── MigrationRoadmap.jsx    ← Dependency-aware phase view
│   │   ├── MigrationRoadmap.css
│   │   ├── RoadmapNode.jsx         ← Individual migration task
│   │   └── RoadmapNode.css
│   ├── hardening/
│   │   ├── AuditChainViewer.jsx    ← Tamper-evident audit log
│   │   ├── AuditChainViewer.css
│   │   ├── HealthDashboard.jsx     ← Production readiness panel
│   │   └── HealthDashboard.css
│   └── common/
│       ├── TabBar.jsx              ← Reusable tab navigation
│       ├── TabBar.css
│       ├── Modal.jsx               ← Overlay dialog
│       ├── Modal.css
│       ├── Tooltip.jsx             ← Hover information
│       ├── Tooltip.css
│       ├── ProgressRing.jsx        ← Circular progress indicator
│       └── ProgressRing.css
├── pages/
│   ├── RiskPage.jsx                ← Full risk analysis dashboard
│   ├── CBOMPage.jsx                ← CBOM viewer and export
│   ├── RoadmapPage.jsx             ← Migration roadmap
│   ├── AuditPage.jsx               ← Governance audit trail
│   └── SettingsPage.jsx            ← Configuration and preferences
└── hooks/
    ├── useRisk.js                  ← GET /api/v1/scans/:id/risk
    ├── useCBOM.js                  ← GET /api/v1/scans/:id/export
    ├── useAuditChain.js            ← Workflow audit chain endpoints
    └── useProductionHealth.js      ← GET /api/v1/workflow/health/production
```

---

## 4. New Pages — Detailed Specifications

### 4.1 Risk Analysis Page (`/risk/:scanId`)

**Purpose:** Interactive Mosca risk evaluation with scenario modeling.

#### Section A: Mosca Timeline Visualization

```
                    Data Shelf Life (X)     Migration (Y)
                    ┌─────────────────┐     ┌──────────┐
  2024 ─────────────┤                 ├─────┤          ├────── 2040
                    └─────────────────┘     └──────────┘
                                                         ▲
                                        Quantum Threat Horizon (Z)
                                        
  If X + Y > Z → MIGRATE NOW (red)
  If X + Y = Z → URGENT (amber)
  If X + Y < Z → SAFE (green)
```

- SVG-based horizontal timeline using Recharts `ReferenceLine` and `ReferenceArea`
- X axis: years from now (0 to 30)
- Labeled regions for X (shelf life), Y (migration), Z (CRQC horizon)
- Color-coded urgency zones
- Animated reveal on mount

#### Section B: Risk Scenario Sliders

| Slider | Range | Default | API Param |
|---|---|---|---|
| Quantum Threat Horizon (Z) | 1-30 years | 8 | `horizon` |
| Data Shelf Life (X) | 1-50 years | 5 | `shelf_life` |
| Migration Duration (Y) | 0.5-10 years | 2 | `migration` |

- Slider changes trigger debounced re-evaluation via `GET /api/v1/scans/:scanId/risk?horizon=X&shelf_life=Y&migration=Z`
- Results animate transition between states
- "Reset to defaults" button

#### Section C: Risk Heatmap

- Grid: Algorithms (rows) x Risk Level (columns: Critical/High/Medium/Low/Info)
- Cell color intensity = number of observations at that risk level
- Click cell to filter findings table below
- Recharts `ScatterChart` or custom SVG grid

#### Section D: Migration Backlog Table

| Column | Source |
|---|---|
| Priority | `backlog_items[].priority` |
| Algorithm | `backlog_items[].algorithm` |
| Action | `backlog_items[].recommended_action` |
| NIST Alternative | `backlog_items[].pqc_alternative` |
| Affected Files | Count from observations |
| Status | TODO / IN_PROGRESS / DONE (user-editable locally) |

- Sortable by priority
- Checkboxes for local status tracking
- Export backlog as CSV

### 4.2 CBOM Page (`/cbom/:scanId`)

**Purpose:** View, validate, and export CycloneDX 1.6 Cryptographic Bill of Materials.

#### Section A: CBOM Tree View

- Hierarchical tree: Project > Components > Crypto Properties > Algorithms
- Expand/collapse nodes
- Icon indicators for quantum safety status
- Click any node to see raw JSON

#### Section B: Export Panel

- "Download CycloneDX 1.6 JSON" button (using `file-saver`)
- "Copy to Clipboard" button for raw JSON
- Schema validation status badge (VALID / INVALID)
- File size indicator

#### Section C: Reconciliation View (if multiple scanners available)

- Side-by-side comparison grid
- Discrepancy Index (D) gauge
- Highlighted differences between scanner outputs
- Unified CBOM toggle

### 4.3 Migration Roadmap Page (`/roadmap/:scanId`)

**Purpose:** Dependency-aware, phased migration plan visualization.

#### Roadmap Visualization

- Vertical timeline with phased waves:
  - **Phase 1:** Foundations / PKI (root certificates, CA infrastructure)
  - **Phase 2:** Platform Services (TLS endpoints, API gateways)
  - **Phase 3+:** Edge Endpoints (client libraries, IoT devices)
- Each phase contains `RoadmapNode` cards showing:
  - Component name
  - Current algorithm
  - Target PQC algorithm (FIPS 203/204/205)
  - Dependencies (arrows connecting prerequisite nodes)
  - Estimated effort indicator
- Bottleneck nodes highlighted with warning badge
- Cycle detection warnings displayed as alert banners

### 4.4 Audit Page (`/audit`)

**Purpose:** Tamper-evident governance audit trail viewer.

| Section | Endpoint | Components |
|---|---|---|
| Audit Chain Log | `GET /api/v1/workflow/audit/chain/verify` | `AuditChainViewer` |
| Add Audit Event | `POST /api/v1/workflow/audit/chain/append` | Form with action, actor, details |
| Chain Integrity | Verification result | `Badge` (VERIFIED / BROKEN) |

- Chronological event list with hash chain visualization
- Each event shows: timestamp, action, actor, SHA-256 hash link
- Chain verification button with animated check/cross result
- Production Health panel from `GET /api/v1/workflow/health/production`

### 4.5 Settings Page (`/settings`)

**Purpose:** User preferences and configuration.

| Setting | Type | Default |
|---|---|---|
| Default CRQC Horizon | Slider | 8 years |
| Default Shelf Life | Slider | 5 years |
| Default Migration Duration | Slider | 2 years |
| Theme | Toggle | Dark (locked to dark for Phase Ab) |
| Export Format | Dropdown | CycloneDX 1.6 JSON |
| Notifications | Toggle | Enabled |

- Settings persisted in `localStorage`
- Apply across all risk evaluation pages

---

## 5. Updated Routing Configuration

```jsx
// App.jsx routes (Phase Ab additions)
<Routes>
  {/* Phase Aa routes */}
  <Route path="/" element={<DashboardPage />} />
  <Route path="/scan" element={<ScanPage />} />
  <Route path="/scans/:scanId" element={<ScanDetailPage />} />
  <Route path="/findings" element={<FindingsPage />} />
  
  {/* Phase Ab routes */}
  <Route path="/risk/:scanId" element={<RiskPage />} />
  <Route path="/cbom/:scanId" element={<CBOMPage />} />
  <Route path="/roadmap/:scanId" element={<RoadmapPage />} />
  <Route path="/audit" element={<AuditPage />} />
  <Route path="/settings" element={<SettingsPage />} />
  
  <Route path="*" element={<NotFoundPage />} />
</Routes>
```

---

## 6. Updated Sidebar Navigation

```
Dashboard          /
New Scan           /scan
─── Scan Results ───
  Findings         /findings
  Risk Analysis    /risk/:scanId
  CBOM Export      /cbom/:scanId
  Roadmap          /roadmap/:scanId
─── Governance ────
  Audit Trail      /audit
  Settings         /settings
```

- Active route highlighted with `--primary` accent
- Scan-dependent routes show "Select a scan first" tooltip when no scan exists
- Collapsible sidebar on mobile (hamburger menu)

---

## 7. Micro-Animations & Transitions (Framer Motion)

| Element | Animation | Duration |
|---|---|---|
| Page transitions | Fade + slide up | 200ms |
| Card mount | Scale from 0.95 to 1.0 + fade | 300ms |
| Table row enter | Stagger slide from left | 50ms per row |
| Risk slider change | Timeline segments animate width | 400ms ease-out |
| Heatmap cell hover | Scale 1.1 + shadow glow | 150ms |
| Toast notifications | Slide in from top-right | 300ms |
| Modal overlay | Backdrop fade + content scale | 250ms |
| Chart reveal | Draw-in animation | 800ms |
| Badge pulse | Infinite pulse on critical status | 2s loop |
| Sidebar collapse | Width transition | 200ms |

---

## 8. Responsive Design Breakpoints

| Breakpoint | Width | Layout Change |
|---|---|---|
| Desktop | 1200px+ | Full sidebar + main content |
| Tablet | 768px - 1199px | Collapsible sidebar overlay |
| Mobile | below 768px | Bottom navigation bar, stacked cards |

**Key Responsive Rules:**
- Findings table: horizontal scroll on mobile, sticky first column
- Risk timeline: vertical orientation on mobile
- CBOM tree: full-width accordion on mobile
- Roadmap: single-column card stack on mobile
- Charts: responsive container with min-height

---

## 9. New Custom Hooks

| Hook | Endpoint | Returns |
|---|---|---|
| `useRisk(scanId, params)` | `GET /api/v1/scans/:id/risk?...` | `{ risk, loading, error, refetch }` |
| `useCBOM(scanId)` | `GET /api/v1/scans/:id/export` | `{ cbom, loading, error }` |
| `useAuditChain()` | `GET /api/v1/workflow/audit/chain/verify` | `{ chain, verified, loading }` |
| `useProductionHealth()` | `GET /api/v1/workflow/health/production` | `{ health, loading, error }` |
| `useLocalSettings()` | `localStorage` | `{ settings, updateSetting }` |
| `useDebounce(value, delay)` | — | Debounced value for slider inputs |

---

## 10. Phase Ab Test Plan

### 10.1 Unit Tests (Vitest + React Testing Library)

| Test File | Tests | Description |
|---|---|---|
| `MoscaTimeline.test.jsx` | 4 | Renders timeline, color zones, animation, responsive |
| `RiskSlider.test.jsx` | 3 | Slider change, debounce, reset to defaults |
| `RiskScoreCard.test.jsx` | 3 | Score display, severity badge, observation count |
| `RiskHeatmap.test.jsx` | 3 | Grid render, cell click filter, empty state |
| `BacklogTable.test.jsx` | 4 | Sort by priority, checkbox toggle, CSV export, empty state |
| `CBOMTreeView.test.jsx` | 4 | Tree expand/collapse, node click, icon status, search |
| `CBOMExportPanel.test.jsx` | 3 | Download trigger, clipboard copy, validation badge |
| `ReconciliationView.test.jsx` | 3 | Side-by-side diff, discrepancy index, unified toggle |
| `DriftTimeline.test.jsx` | 3 | Snapshot timeline, drift markers, empty state |
| `SnapshotCompare.test.jsx` | 3 | Side-by-side diff, added/removed highlights, hash display |
| `MigrationRoadmap.test.jsx` | 4 | Phase rendering, dependency arrows, bottleneck badge, cycle warning |
| `RoadmapNode.test.jsx` | 2 | Node display, PQC alternative mapping |
| `AuditChainViewer.test.jsx` | 4 | Event list, hash chain visualization, verification badge, append form |
| `HealthDashboard.test.jsx` | 3 | Readiness indicators, profile display, zero-telemetry check |
| `TabBar.test.jsx` | 2 | Tab selection, active indicator |
| `Modal.test.jsx` | 3 | Open/close, backdrop click, escape key |
| `Tooltip.test.jsx` | 2 | Hover show, position calculation |
| `ProgressRing.test.jsx` | 2 | Percentage arc, color thresholds |
| `useRisk.test.js` | 3 | Loading, data fetch with params, error |
| `useCBOM.test.js` | 2 | Loading, successful fetch |
| `useDebounce.test.js` | 2 | Immediate value, debounced value |
| `useLocalSettings.test.js` | 3 | Read defaults, update setting, persist to localStorage |
| **Total** | **65** | |

### 10.2 Integration Tests

| Test | Description |
|---|---|
| `RiskPage.integration.test.jsx` | Mounts with scan ID, fetches risk data, slider re-evaluation |
| `CBOMPage.integration.test.jsx` | Mounts with scan ID, renders tree, triggers download |
| `RoadmapPage.integration.test.jsx` | Mounts with scan ID, renders phased roadmap, shows dependencies |
| `AuditPage.integration.test.jsx` | Mounts, fetches chain, verifies integrity |
| `SettingsPage.integration.test.jsx` | Mounts, changes settings, verifies localStorage persistence |

### 10.3 Cross-Phase Smoke Tests

| Test | Description |
|---|---|
| `full-navigation.smoke.test.jsx` | Navigate through all routes without crash |
| `responsive.smoke.test.jsx` | Viewport resize triggers layout changes |
| `production-build.smoke.test.js` | `npm run build` completes with all Phase Ab additions |

### 10.4 Expected Results

- **Phase Ab new tests:** 65 unit + 5 integration + 3 smoke = **73 tests**
- **Combined total:** Phase Aa (43) + Phase Ab (73) = **116 tests passing**
- **Coverage target:** 80% or higher line coverage across all `src/` directories
- **Build gate:** `npm run build` exits with code 0

---

## 11. Report and Documentation Requirements

### 11.1 Reports to Generate

After all tests pass, create the following report files:

| File | Location |
|---|---|
| `phase_Ab_report.md` | `.brain/.work/.report/phase_Ab_report.md` |
| `phase_Ab_report.md` | `.brain/.report/phase_Ab_report.md` |

### 11.2 Report Contents

The report must contain:
- Date (ISO timestamp)
- Status (PASSED / FAILED)
- Test Results (X passed / Y total with pass rate percentage)
- Build Status (SUCCESS / FAILED)
- Coverage (line coverage percentage)
- Summary of what was implemented in Phase Ab
- Vitest output summary (including Phase Aa regression results)
- List of all new/changed files
- Known Issues or technical debt
- Performance metrics (bundle size, lighthouse score if available)
- Git Commit hash, branch, and push status
- Final frontend completion status

---

## 12. Git Workflow

1. Stage all new Phase Ab files: `git add frontend/src/components/risk/ frontend/src/components/cbom/ frontend/src/components/temporal/ frontend/src/components/roadmap/ frontend/src/components/hardening/ frontend/src/pages/ frontend/src/hooks/`
2. Stage phase planning docs: `git add .brain/.work/webapp/worker_01/mvp_phases/phase_Ab.md`
3. Stage reports: `git add .brain/.work/.report/phase_Ab_report.md .brain/.report/phase_Ab_report.md`
4. Commit: `git commit -m "feat(frontend): Phase Ab — Risk dashboard, CBOM export, migration roadmap, audit trail"`
5. Push: `git push origin main`

---

## 13. Success Criteria

- [ ] Risk page renders Mosca timeline with interactive sliders
- [ ] Slider changes trigger live risk re-evaluation via API
- [ ] Risk heatmap displays algorithm x severity matrix
- [ ] Migration backlog table sortable and exportable as CSV
- [ ] CBOM tree view renders hierarchical component structure
- [ ] CycloneDX 1.6 JSON downloadable via browser
- [ ] Migration roadmap shows dependency-aware phased waves
- [ ] Bottleneck and cycle detection warnings displayed
- [ ] Audit chain viewer shows tamper-evident event log
- [ ] Chain verification returns VERIFIED/BROKEN badge
- [ ] Production health panel shows air-gapped readiness status
- [ ] Settings page persists preferences to localStorage
- [ ] All page transitions animated with framer-motion
- [ ] Responsive layouts work at desktop/tablet/mobile breakpoints
- [ ] All 116 tests (Phase Aa + Ab combined) passing
- [ ] 80%+ line coverage across all `src/` directories
- [ ] `npm run build` produces error-free production bundle
- [ ] Reports generated in both `.brain/.work/.report/` and `.brain/.report/`
- [ ] Changes committed and pushed to `adishxm/astra` main branch

---

## 14. Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Risk slider debounce causes API spam | 300ms debounce with `useDebounce` hook; loading indicator during re-evaluation |
| CBOM JSON too large for clipboard | Stream download via `file-saver`; clipboard only for small payloads (<1 MB) |
| Framer-motion bundle size | Tree-shake unused features; lazy-load animation-heavy pages |
| Complex SVG roadmap rendering | Simplify to CSS flexbox layout with connector lines; SVG only for arrows |
| Phase Aa regression | Run full test suite including Phase Aa tests before Phase Ab commit |
| Mobile Mosca timeline readability | Switch to vertical orientation below 768px breakpoint |
| localStorage quota limits | Cap stored settings to < 5 KB; fallback to defaults on quota error |

---

## 15. Performance Budget

| Metric | Target |
|---|---|
| First Contentful Paint (FCP) | below 1.5s |
| Largest Contentful Paint (LCP) | below 2.5s |
| Time to Interactive (TTI) | below 3.0s |
| Total Bundle Size (gzipped) | below 300 KB |
| Lighthouse Performance Score | 85+ |

**Optimization Strategies:**
- Code splitting via React `lazy()` for Phase Ab pages
- Dynamic imports for Recharts (only load on chart pages)
- CSS minification via Vite build
- Image optimization (SVG icons, no raster images)

---

## 16. Final Deliverable Summary

Upon completion of Phase Ab, the ASTRA frontend delivers:

| Capability | Pages | API Endpoints |
|---|---|---|
| System health monitoring | Dashboard | `/health` |
| Archive upload and scanning | Scan | `/api/v1/scans/upload` |
| Scan history and management | Dashboard | `/api/v1/scans` |
| Findings inspection | Scan Detail, Findings | `/api/v1/scans/:id/findings` |
| Coverage analysis | Scan Detail | `/api/v1/scans/:id/coverage` |
| Mosca risk evaluation | Risk | `/api/v1/scans/:id/risk` |
| CBOM export and validation | CBOM | `/api/v1/scans/:id/export` |
| Migration roadmap | Roadmap | `/api/v1/scans/:id/risk` (backlog) |
| Tamper-evident audit trail | Audit | `/api/v1/workflow/audit/chain/*` |
| Production readiness | Audit | `/api/v1/workflow/health/production` |
| User preferences | Settings | `localStorage` |

**Total test count:** 116 (43 Phase Aa + 73 Phase Ab)  
**Combined coverage:** 80%+ across all source directories  
**Production readiness:** Full Vite build, responsive design, accessibility compliance
