# Worker 04 Phase A: Frontend Semantics & Demo Data Transparency

**Document:** `phase_a.md`  
**Worker:** Worker 04 (`.brain/.work/webapp/worker_04`)  
**Target Roadmap Area:** P0 / User Workflow & Visual Accuracy  
**Target Readiness Score Impact:** +3 points on Frontend and User Workflow (Resolves Finding 1 & Finding 4)  
**Status:** SPECIFICATION COMPLETE  

---

## 1. Objectives & Executive Scope

Phase A directly addresses the critical category misclassification and demo state ambiguity identified in the latest reassessment:
1. **Fix `resolveCategory` Asymmetric Substring Bug**:
   - In `frontend/index.html` (and `backend/app/static/index.html`), `purpose.indexOf('SYMMETRIC') !== -1` currently matches before checking `ASYMMETRIC`.
   - Because `'ASYMMETRIC'.indexOf('SYMMETRIC') === 1`, asymmetric primitives (e.g. `RSA-2048`, `ECDSA`, `Ed25519`) were erroneously labeled as "Symmetric".
   - Refactor `resolveCategory` to check `ASYMMETRIC` before `SYMMETRIC` and implement full normalized enum mapping (`ASYMMETRIC_SIGNATURE`, `ASYMMETRIC_ENCRYPTION`, `ASYMMETRIC_KEY_EXCHANGE`, `ASYMMETRIC` $\rightarrow$ "Asymmetric").
2. **Explicit "Synthetic Demo Baseline" Badging**:
   - The initial pre-scan dashboard view loads `DEMO_SCAN` (displaying 182/192 files and seeded events).
   - Add a prominent, clear banner and status badge: `"Synthetic Demo Workspace — Pre-loaded for interface demonstration; submit a scan archive or click 'Load Synthetic Sample' for active live analysis."`
   - Real uploaded scans dynamically replace the demo banner with `"Active Scan: <scan_id> (<filename>)"`.
3. **Synchronize UI Test Counters**:
   - Replace the stale `"88 tests passing"` label in the UI header and hero section with the live synchronized automated test metric (`"334+ Passing Automated Tests across Backend & Frontend"`).
4. **Mirror Synchronous Updates**:
   - Synchronize all edits identically between `frontend/index.html` and `backend/app/static/index.html`.

---

## 2. Technical Deliverables

| Deliverable | File | Target Behavior |
|---|---|---|
| **Category Resolver Fix** | `frontend/index.html` | Checks `ASYMMETRIC` prior to `SYMMETRIC`; correctly maps RSA, ECDSA, Ed25519 to "Asymmetric". |
| **Static Assets Sync** | `backend/app/static/index.html` | Exact byte-for-byte synchronization of `frontend/index.html`. |
| **Demo Banner & Test Badge** | `frontend/index.html` | Initial view explicitly badges demo state and displays 334+ tests passing. |
| **Phase A Automated Test Suite** | `backend/tests/test_worker04_phase_a_frontend_semantics.py` | Pytest suite validating resolver logic, enum branches, and demo badging. |
| **Phase A Completion Report** | `.brain/.work/.report/worker04_phase_a_report.md` | Standardized audit report documenting all implementation details and verification results. |

---

## 3. Test Strategy & Acceptance Gates

- **Test A.1:** Assert `resolveCategory` maps `ASYMMETRIC`, `ASYMMETRIC_SIGNATURE`, `ASYMMETRIC_KEY_EXCHANGE`, and `RSA` to `"Asymmetric"`.
- **Test A.2:** Assert `resolveCategory` maps `SYMMETRIC`, `SYMMETRIC_ENCRYPTION`, and `AES` to `"Symmetric"`.
- **Test A.3:** Assert `resolveCategory` maps `HASH`, `HASH_FUNCTION`, and `MD5` to `"Hash"`.
- **Test A.4:** Assert initial UI contains `"Synthetic Demo"` badge and eliminates stale `"88 tests passing"`.
- **Test A.5:** Assert `frontend/index.html` and `backend/app/static/index.html` are identical.
