# Worker 04 Phase B: Server-Persisted Cryptographic Audit Chain & Tenant Scoping

**Document:** `phase_b.md`  
**Worker:** Worker 04 (`.brain/.work/webapp/worker_04`)  
**Target Roadmap Area:** P0 / Operations, Audit Authenticity & Tenant Scoping  
**Target Readiness Score Impact:** +3 points on Security and Operations (Resolves Finding 2 & Finding 5)  
**Status:** SPECIFICATION COMPLETE  

---

## 1. Objectives & Executive Scope

Phase B upgrades the audit infrastructure from ephemeral in-memory state to a durable, server-verified cryptographic audit chain with multi-tenant scoping:
1. **Durable File-Backed Audit Store (`AuditChainStore`)**:
   - Currently, audit events are held in transient memory.
   - Implement `AuditChainStore` in `backend/app/web_workflow/` that writes blocks to `data/audit/audit_chain.json`.
   - On application startup, load existing blocks and verify the SHA-256 chain continuity.
2. **Automated Server Event Ingestion**:
   - Automatically append authoritative audit records for:
     - `SCAN_INTAKE`: Emitted upon archive or directory scan completion, capturing `scan_id`, `assessed_files`, `coverage_percentage`, and `dna_hash`.
     - `RISK_RECALCULATED`: Emitted upon owner context updates ($X, Y, Z$) or Mosca escalations.
     - `CBOM_EXPORTED`: Emitted upon CycloneDX 1.6 CBOM generation and schema validation.
3. **Tenant & Actor Scoping**:
   - Support optional `X-Tenant-ID` and `X-User-ID` request headers in the FastAPI pipeline.
   - Attach tenant metadata to scan records and audit blocks to provide tenant-isolated views.
4. **Live Server-Verified Frontend Audit Display**:
   - Wire the web dashboard to fetch `/api/v1/workflow/audit/chain/verify` and real audit events.
   - In demo mode, clearly badge the audit panel as `"Demo Baseline Event Log"`.
   - When an active scan is loaded, display the verified server-side audit trail with verified block height and SHA-256 chain root.

---

## 2. Technical Deliverables

| Deliverable | File | Target Behavior |
|---|---|---|
| **Durable Audit Store** | `backend/app/web_workflow/audit_store.py` | JSON file-backed persistence for SHA-256 Merkle-style audit blocks. |
| **Pipeline Event Hook** | `backend/app/services/scan_service.py` | Automatically logs `SCAN_INTAKE`, `RISK_RECALCULATED`, and `CBOM_EXPORTED` events. |
| **Tenant Scoping** | `backend/app/main.py` & `backend/app/auth.py` | Extracts tenant and user identity from headers/keys and enforces scoping. |
| **Frontend Server Audit Fetch**| `frontend/index.html` & `static` | Calls `/api/v1/workflow/audit/chain/verify` to display verified server chain. |
| **Phase B Automated Test Suite**| `backend/tests/test_worker04_phase_b_audit_persistence.py` | Validates file persistence across restart, event emission, and verification. |
| **Phase B Completion Report** | `.brain/.work/.report/worker04_phase_b_report.md` | Standardized audit report documenting all implementation details and verification results. |

---

## 3. Test Strategy & Acceptance Gates

- **Test B.1:** Assert audit chain persists to disk and reloads with 100% cryptographic integrity.
- **Test B.2:** Assert scanning an archive automatically logs a `SCAN_INTAKE` audit block on the server.
- **Test B.3:** Assert updating scan context logs a `RISK_RECALCULATED` audit block.
- **Test B.4:** Assert `/api/v1/workflow/audit/chain/verify` returns `is_valid: true`, root hash, and accurate block count.
- **Test B.5:** Assert tenant-scoped requests only retrieve records belonging to that tenant.
