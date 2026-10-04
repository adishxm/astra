# Worker 03 Phase A: Security Hardening: Hosted Mode Fail-Closed Auth, Endpoint Protection & Outbound Egress Guard

**Document:** `phase_a.md`  
**Worker:** Worker 03 (`.brain/.work/webapp/worker_03`)  
**Target Roadmap Area:** P0 — Close the hosted-service data exposure & fail-closed access control  
**Target Readiness Score Impact:** +7 points on Security & Operational Readiness  
**Status:** SPECIFICATION & ARCHITECTURE PLAN COMPLETE  

---

## 1. Objectives & Executive Scope

Phase A addresses the critical security and access control vulnerabilities identified in Section 3 and Section 4 of *ASTRA / SIH26164 — Fresh Product Assessment and 100-Point Roadmap*:
1. **Fail-Closed in Hosted Mode:**
   - When hosted mode is enabled (`ASTRA_HOSTED_MODE=1` or `ASTRA_HOSTED_MODE=true`), require `ASTRA_API_KEY` to be configured.
   - If no API key is configured when running in hosted mode, fail closed by refusing unauthenticated uploads and scan listings, returning **HTTP 401 / 403** with a clear security advisory.
2. **Comprehensive Read & Write Protection Across All Scan Endpoints:**
   - In the prior implementation, only mutating endpoints (`/upload`, `/directory`, `/context`) enforced `verify_api_key`.
   - Scan detail (`GET /api/v1/scans/{id}`), findings (`GET /api/v1/scans/{id}/findings`), risk evaluations (`GET /api/v1/scans/{id}/risk`), and exports (`GET /api/v1/scans/{id}/export`) were left unauthenticated, allowing anonymous data exposure.
   - Extend `verify_api_key` dependency to protect **all** scan routes (both `GET` and `POST`/`PUT`) whenever authentication is configured or in hosted mode.
   - Return **HTTP 401 Unauthorized** with `{"detail": "Invalid or missing API key"}` on any unauthenticated access to scan data.
3. **CORS Hardening & Upload Rate Quotas:**
   - In hosted mode, restrict default CORS origins rather than allowing unauthenticated wildcard `*` with credentials.
   - Implement an in-memory sliding-window rate limiter on archive intake to prevent denial-of-service and storage exhaustion (HTTP 429 Too Many Requests).
4. **Air-Gapped Outbound Network Egress Verification:**
   - Implement an automated network-level assertion verifying that during a scan, zero external TCP/UDP sockets are opened, proving complete air-gapped sovereign execution.

---

## 2. Technical Deliverables

| Deliverable | File | Target Behavior |
|---|---|---|
| **Fail-Closed Auth & Full Route Protection** | `backend/app/main.py` | Enforce `verify_api_key` on all scan endpoints (`GET /scans`, `GET /scans/{id}`, `GET /scans/{id}/findings`, `GET /scans/{id}/export`, `GET /scans/{id}/risk`). Fail closed in hosted mode if `ASTRA_API_KEY` is missing. |
| **Rate Limiter & Quotas** | `backend/app/main.py` | Add request rate limit on `/api/v1/scans/upload` returning 429 when thresholds are exceeded. |
| **Security Architecture Docs** | `SECURITY.md` | Document fail-closed hosted mode policy, full read/write auth requirement, and network egress guarantees. |
| **Phase A Automated Test Suite** | `backend/tests/test_worker03_phase_a_security.py` | Tests fail-closed hosted mode, unauthorized 401 on scan detail/findings/export reads, rate limiting, and 0 outbound socket egress. |
| **Phase A Completion Report** | `.brain/.work/.report/worker03_phase_a_report.md` | Standardized audit report documenting all implementation details and verification results. |

---

## 3. Test Strategy & Acceptance Gates

- **Test A.1:** In hosted mode with no API key set, assert mutating and list endpoints fail closed (401/403).
- **Test A.2:** With `ASTRA_API_KEY` set, assert unauthenticated `GET /api/v1/scans/{id}`, `GET /api/v1/scans/{id}/findings`, and `GET /api/v1/scans/{id}/export` return HTTP 401.
- **Test A.3:** With valid `X-ASTRA-API-KEY` or Bearer token, assert requests succeed with HTTP 200.
- **Test A.4:** Assert excessive rapid uploads trigger HTTP 429 Too Many Requests.
- **Test A.5:** Assert zero outbound network connections occur during full scan lifecycle.
