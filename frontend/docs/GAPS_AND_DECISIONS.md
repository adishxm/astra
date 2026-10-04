# ASTRA Frontend — Gap Analysis & Architecture Decisions

> **Document Status:** Complete & Verified against live ASTRA backend engine (`v1.0.0`, Team HEXARK, SIH26164)  
> **Target Branch:** `feat/frontend-p01-api-contract`  
> **Prerequisite:** Rule 2 ("Do NOT modify anything under `backend/`") strictly respected.

---

## 1. Executive Summary

During the P01 API Contract and Reality Check, the backend engine, routes, and domain services were audited against the React SPA specifications in `phase_Aa.md` and `phase_Ab.md`. While the core scanning, coverage, risk evaluation, and CBOM export flows are 100% operational, several advanced features specified for Phase Ab (Roadmap graph visualization, temporal drift diffs, multi-scanner reconciliation, and audit event listing) rely on backend Python engines that have not been exposed as REST endpoints in `app/main.py`.

Below is the verified status and decision matrix for each gap.

---

## 2. Gap Evaluation & Verification

---

### Gap 1: No REST Endpoint Returns Migration Roadmap Waves
- **Status:** `CONFIRMED`
- **Evidence:**
  - `backend/app/risk/roadmap.py` implements `DependencyRoadmapEngine` and `compute_roadmap(assets: List[MigrationDependencyNode]) -> MigrationRoadmap` (lines 62-222).
  - In `backend/app/services/scan_service.py` (lines 298-315), `ScanRecord` invokes only `RiskScorer` and `BacklogBuilder`. `compute_roadmap` is **never called** during scan execution and roadmap data is not stored in `ScanRecord`.
  - In `backend/app/main.py` (lines 233-290), `GET /api/v1/scans/{scan_id}/risk` returns only `{scan_id, scenario, context, risk_evaluations, backlog_items}`.
- **Impact on Frontend:** `RoadmapPage.jsx` (`phase_Ab.md` Section 4.3) cannot retrieve phased waves (Phase 1 PKI, Phase 2 Core, Phase 3 Edge), graph dependencies, or bottleneck rankings from the live API.

#### Decision Table — Gap 1
| Option | Description | Cost to frontend | Cost to backend | Risk |
|---|---|---|---|---|
| **A. Derive client-side** | Build a JavaScript topological sort algorithm in React using `backlog_items` and `canonical_assets`. Heuristically assign assets to waves based on `purpose` and `claim_type`. | Medium (reimplementing Kahn's algorithm in JS) | Zero | Low (client has enough metadata for heuristics) |
| **B. Fixture/mock + label in UI** | Use static mock roadmap fixture with an explicit "DEMO SIMULATION" badge in the UI. | Low | Zero | Medium (does not reflect scanned repository dependencies) |
| **C. Request backend change** | Add `GET /api/v1/scans/{scan_id}/roadmap` returning `MigrationRoadmap` model from `app.risk.roadmap`. | Low | Very Low (engine already written in `app/risk/roadmap.py`) | Very Low |

- **Recommendation:** **Option A (Derive client-side)** for Phase Aa/Ab frontend build, while proposing **Option C (Backend Route)** for the next backend release.
- **Proposed Backend Endpoint (for Option C):**
  - **Method / Path:** `GET /api/v1/scans/{scan_id}/roadmap`
  - **Proposed Response Shape:**
    ```json
    {
      "scan_id": "scan-15ff86cd",
      "total_assets": 6,
      "has_cycles": false,
      "cycle_nodes": [],
      "bottlenecks": [
        { "asset_id": "rsa-2048-crypto_service.py-22", "algorithm": "RSA-2048", "risk_score": 68.38, "downstream_unblocked_count": 3 }
      ],
      "phases": [
        {
          "phase_number": 1,
          "phase_title": "Phase 1: Foundational Cryptographic Libraries & PKI Trust Anchors",
          "asset_ids": ["rsa-2048-crypto_service.py-22"],
          "total_estimated_effort_days": 10.0,
          "unblocked_downstream_count": 2
        }
      ],
      "roadmap_summary": "Partitioned 6 assets into 2 dependency-ordered phases."
    }
    ```
- **Needs Team Decision?** `NEEDS TEAM DECISION` (Question 1: Should we derive roadmap waves client-side in React or request Worker 03 / backend to expose `GET /api/v1/scans/{id}/roadmap`?)

---

### Gap 2: No Endpoint Lists Audit Chain Events
- **Status:** `CONFIRMED`
- **Evidence:**
  - `backend/app/web_workflow/router.py` (lines 43-64) exposes `POST /audit/chain/append` (appends to `_GLOBAL_AUDIT_CHAIN`) and `GET /audit/chain/verify`.
  - `verify_audit_chain()` calls `TamperEvidentAuditChainer.verify_chain()` which returns only `{"valid": true, "event_count": 3, "genesis_hash": "...", "tip_hash": "...", "message": "..."}`.
  - The actual list of appended events in `_GLOBAL_AUDIT_CHAIN` is **never returned** by any endpoint.
  - Furthermore, `_GLOBAL_AUDIT_CHAIN` is an in-memory Python list that resets when the server restarts.
- **Impact on Frontend:** `AuditChainViewer.jsx` (`phase_Ab.md` Section 4.4) can verify chain integrity and submit new events, but cannot render the full historical timeline of past events after a page refresh.

#### Decision Table — Gap 2
| Option | Description | Cost to frontend | Cost to backend | Risk |
|---|---|---|---|---|
| **A. Derive client-side** | Store submitted audit events in React state and `localStorage`. When the user appends an event, save the response object (`ChainedAuditEvent`). | Low (simple localStorage persistence) | Zero | Low (resilient for user session) |
| **B. Fixture/mock + label in UI** | Seed the UI with synthetic initial audit events from fixture `audit_append_response.json`. | Low | Zero | Low |
| **C. Request backend change** | Add `GET /api/v1/workflow/audit/chain/events` returning `List[ChainedAuditEvent]`. | Low | Very Low (return `_GLOBAL_AUDIT_CHAIN`) | Very Low |

- **Recommendation:** **Option A + B (Client-side cache seeded with default events)** for immediate SPA functionality, with **Option C** logged for backend enhancement.
- **Proposed Backend Endpoint (for Option C):**
  - **Method / Path:** `GET /api/v1/workflow/audit/chain/events`
  - **Proposed Response Shape:** `Array<ChainedAuditEvent>`
- **Needs Team Decision?** `NEEDS TEAM DECISION` (Question 2: Should audit events be persisted to disk/DB on the backend, or is client-side session/localStorage sufficient for the prototype?)

---

### Gap 3: No REST Endpoint for Drift History or Multi-Scanner Reconciliation
- **Status:** `CONFIRMED`
- **Evidence:**
  - `backend/app/inventory/temporal.py` defines `TemporalLineageEngine.detect_drift(prior, current) -> CryptographicDrift` (lines 208-319).
  - `backend/app/inventory/cbom_reconciliation.py` defines `CBOMReconciliationEngine.reconcile_generators(scanner_outputs) -> ReconciliationResult` (lines 153-269).
  - Neither `detect_drift` nor `reconcile_generators` is bound to a route in `backend/app/main.py`.
- **Impact on Frontend:**
  - `DriftTimeline.jsx` and `SnapshotCompare.jsx` (`phase_Ab.md` Section 3.1) cannot call a server-side drift diff between two scan IDs.
  - `ReconciliationView.jsx` (`phase_Ab.md` Section 4.2C) cannot submit multiple CBOMs to receive a unified reconciliation matrix.

#### Decision Table — Gap 3
| Option | Description | Cost to frontend | Cost to backend | Risk |
|---|---|---|---|---|
| **A. Derive client-side** | 1. For Drift: Compare two scan detail objects fetched via `GET /api/v1/scans/{id}` client-side (diffing `canonical_assets` and `dna_hash`).<br/>2. For Reconciliation: Implement client-side CBOM diffing. | Medium | Zero | Low (both scans' canonical assets are fully available in React) |
| **B. Fixture/mock + label in UI** | Load pre-computed reconciliation demo fixture when comparing external scanners. | Low | Zero | Low |
| **C. Request backend change** | Add `POST /api/v1/inventory/drift/compare` taking `{"prior_scan_id": "...", "current_scan_id": "..."}` and `POST /api/v1/inventory/reconcile`. | Low | Low | Very Low |

- **Recommendation:** **Option A (Client-side asset diffing for drift)** using the deterministic DNA hashes and asset lists, combined with **Option B** for multi-vendor scanner demos.
- **Needs Team Decision?** `NEEDS TEAM DECISION` (Question 3: For the snapshot comparison view, do we perform the JSON delta client-side or should backend provide a dedicated `/scans/compare` diff endpoint?)

---

### Gap 4: No Server-Side Async Scan Progress / Job Status
- **Status:** `CONFIRMED`
- **Evidence:**
  - `backend/app/main.py` lines 90-146 (`upload_and_scan`): Archive upload is a single, synchronous blocking `async def` handler.
  - No background task queue (Celery, RQ, asyncio tasks) or job store exists for scans. No `/api/v1/scans/{job_id}/status` or WebSocket endpoint exists.
- **Impact on Frontend:** `UploadDropzone.jsx` cannot track backend analysis stages (Intake -> Discovery -> Coverage -> Risk -> CBOM) in real-time from server events.

#### Decision Table — Gap 4
| Option | Description | Cost to frontend | Cost to backend | Risk |
|---|---|---|---|---|
| **A. Client-side simulated progress** | Track real network upload percentage via `XMLHttpRequest.upload.onprogress` (0% to 100%). Once upload finishes and backend is processing, display an animated staged spinner ("Analyzing Cryptographic Primitives... Evaluating Mosca Risk... Projecting CycloneDX CBOM..."). | Low | Zero | Zero (standard SPA pattern for fast sub-second scans) |
| **B. Request backend async jobs** | Refactor backend upload to return `202 Accepted` with `job_id`, plus polling `/status` or SSE. | High | High | High (breaks existing 88/88 backend tests and CLI assumptions) |

- **Recommendation:** **Option A (Client-side simulated stages during network wait)**. Because local scans on test archives complete in 50–300ms, synchronous blocking with client-side stage animation is smooth and responsive.

---

### Gap 5: `GET /api/v1/scans` List Shape Missing Risk & Clean-State Counts
- **Status:** `CONFIRMED`
- **Evidence:**
  - `backend/app/services/scan_service.py` lines 172-181 (`ScanStore.list_all`):
    ```python
    scans.append({
        "scan_id": sid,
        "target_name": rec.target_name,
        "created_at": rec.created_at.isoformat(),
        "asset_count": len(rec.canonical_assets),
        "coverage_percentage": rec.coverage.overall_coverage_percentage,
        "dna_hash": rec.snapshot.cryptographic_dna_hash,
    })
    ```
  - Fields present in `ScanRecord.summary` (such as `critical_urgency_count`, `high_urgency_count`, `clean_state_label`) are **omitted** from the list response.
- **Impact on Frontend:** The Dashboard Quick Stats card "Critical Risks" cannot be computed directly from `GET /api/v1/scans` without fetching individual scan records.

#### Decision Table — Gap 5
| Option | Description | Cost to frontend | Cost to backend | Risk |
|---|---|---|---|---|
| **A. Derive from latest scan / in-flight cache** | 1. Fetch `GET /api/v1/scans`.<br/>2. If scans exist, fetch `GET /api/v1/scans/{latest_id}` to get the latest scan's critical risk count and summary.<br/>3. Maintain an in-memory lookup of loaded scan summaries in React context. | Low | Zero | Zero |
| **B. Batch fetch on dashboard mount** | `Promise.all` fetch detail for top 5 scans on dashboard load. | Low | Zero | Low (minimal overhead on local server) |
| **C. Request backend change** | Add `summary` or `critical_urgency_count` to `ScanStore.list_all()`. | Low | Very Low (1 line edit in `scan_service.py`) | Very Low |

- **Recommendation:** **Option A + B (Fetch latest scan detail alongside scan list)**. The frontend hook `useScans()` will fetch the list and automatically fetch the latest scan's detail to populate the dashboard metrics seamlessly.

---

### Gap 6: `/api/v1/scans/directory` Relevance in Web UI
- **Status:** `NOT A GAP` (Expected Architecture Boundary)
- **Evidence:**
  - `backend/app/main.py` lines 149-184: `POST /api/v1/scans/directory` is intended for local CLI executions (`astra scan <path>`).
  - In hosted mode (`ASTRA_HOSTED_MODE=true`), directory scans are disabled by security policy (HTTP 403).
  - Web browser security models prevent web applications from accessing arbitrary absolute host paths.
- **Impact on Frontend:** The web UI will exclusively use `POST /api/v1/scans/upload` for archive uploads, with an optional "Local Path Scan" input available only when `directory_scan_permitted: true` in `/health`.

---

### Gap 7: CORS Behavior & Dev Server Proxy
- **Status:** `NOT A GAP` (Fully Verified)
- **Evidence:**
  - Backend `backend/app/main.py` (lines 46-61) configures `CORSMiddleware` with `allow_origins=["*"]` by default.
  - `frontend/vite.config.js` configures proxy for `/api` and `/health` targeting `http://localhost:8000`.
  - In production, static assets are served directly from FastAPI (`backend/app/main.py` lines 343-366) at root `/`.
- **Conclusion:** No CORS friction exists; development and production serve from unified origins.

---

### Gap 8: Duplicate Route Registration Collision in `backend/app/main.py`
- **Status:** `CONFIRMED`
- **Evidence:**
  - In `backend/app/main.py` line 64: `app.include_router(workflow_router)`.
  - In `backend/app/web_workflow/router.py` line 19: `@router.get("/evidence/{asset_id}")` is defined as a stub returning `[]`.
  - In `backend/app/main.py` line 305: `@app.get("/api/v1/workflow/evidence/{asset_id}")` is defined with persistent search over `GLOBAL_SCAN_STORE`.
  - In FastAPI / Starlette, route matching evaluates routes in the exact order they are registered. Because `workflow_router` was included first, all requests to `GET /api/v1/workflow/evidence/{asset_id}` hit the router stub and return `[]` (as captured in fixture `evidence_asset.json`).
- **Impact on Frontend:** `GET /api/v1/workflow/evidence/{asset_id}` currently returns empty arrays.
- **Frontend Workaround:** The frontend already has full evidence data inside `findings.json` (`observations[]` and `canonical_assets[]`). The frontend will perform asset evidence drill-down directly from the scan findings object in memory.

---

## 3. Summary of Decisions & Implementation Strategy

| Component / Page | Challenge / Gap | Frontend Implementation Strategy |
|---|---|---|
| **Dashboard (`/`)** | Missing urgency count in `/api/v1/scans` | Fetch `GET /api/v1/scans` and `GET /api/v1/scans/:latestId` concurrently. |
| **Findings (`/findings`)** | No cross-scan aggregate endpoint | Fetch `/api/v1/scans` and load findings for recent scans client-side. |
| **Roadmap (`/roadmap/:id`)** | No `/roadmap` endpoint exposed | Derive migration waves from `risk.backlog_items` and `findings.canonical_assets` client-side. |
| **Audit (`/audit`)** | No endpoint to list past audit events | Maintain active session audit event list in `localStorage`, verified via `GET /workflow/audit/chain/verify`. |
| **Drift (`/scans/:id`)** | No `/drift` endpoint exposed | Compute delta between previous and current `canonical_assets` and `dna_hash` client-side. |
| **Evidence Drilldown** | Route collision on `/workflow/evidence` | Drill into `observations[]` within the active scan's findings state. |
