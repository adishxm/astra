# Worker 03 Phase A Report: Security Hardening: Hosted Mode Fail-Closed Auth, Endpoint Protection & Outbound Egress Guard

**Owner:** Risk, Migration Planning & Secure Operations (Worker 03)  
**Stage:** 100-Point Fresh Assessment Roadmap — Phase A of E  
**Phase:** Phase A  
**Status:** IMPLEMENTED & VALIDATED  
**Traceability IDs:** R01, R02, R08, R10  
**Acceptance Criteria:** AC-01, AC-02, AC-03, AC-07, AC-12  
**Date:** 2026-10-04  

---

## 1. Executive Summary & Objective

Phase A closes the hosted-service data exposure and anonymous access vulnerabilities identified in the Fresh Product Assessment:
1. **Hosted Mode Fail-Closed Authentication**:
   - In hosted mode (`ASTRA_HOSTED_MODE=1`), all access now fails closed unless an explicit API key is configured.
   - Unauthenticated uploads and scan listings in hosted mode are actively rejected with **HTTP 401 Unauthorized**.
2. **Comprehensive Read & Write Protection Across All Scan Endpoints**:
   - Extended `verify_api_key` dependency to protect *all* read/inspection endpoints:
     - `GET /api/v1/scans` (scan list)
     - `GET /api/v1/scans/{scan_id}` (scan detail)
     - `GET /api/v1/scans/{scan_id}/findings` (observations & assets)
     - `GET /api/v1/scans/{scan_id}/coverage` (truthful coverage breakdown)
     - `GET /api/v1/scans/{scan_id}/risk` (Mosca risk evaluations)
     - `GET /api/v1/scans/{scan_id}/export` (CycloneDX 1.6 CBOM export)
     - `GET /api/v1/workflow/evidence/{asset_id}` (evidence drilldown)
     - `GET /api/v1/workflow/export` (sanitized export)
   - When authentication is enabled (`ASTRA_API_KEY` configured), any unauthenticated call to these endpoints returns **HTTP 401 Unauthorized**.
3. **Upload Rate Quotas**:
   - Implemented an in-memory sliding-window upload rate limiter on `POST /api/v1/scans/upload`.
   - Rejects excessive bursts exceeding `ASTRA_RATE_LIMIT_UPLOADS_PER_MINUTE` with **HTTP 429 Too Many Requests**.
4. **Air-Gapped Outbound Egress Verification**:
   - Implemented network socket interceptor tests verifying that zero external network egress connections occur during scan operations.

---

## 2. Technical Decisions & Code Deliverables

| Module | File | Changes Made |
|---|---|---|
| **Centralized Security** | `backend/app/auth.py` | Created dedicated security module containing `is_hosted_mode()`, `is_directory_scan_allowed()`, `get_max_upload_size()`, `check_upload_rate_limit()`, and `verify_api_key()`. |
| **API Application** | `backend/app/main.py` | Added rate limit checks to upload endpoint; enforced `verify_api_key` on all scan read routes; exposed `authentication_enforced` in health probe. |
| **Workflow Router** | `backend/app/web_workflow/router.py` | Added `Depends(verify_api_key)` to workflow endpoints to secure evidence drilldowns. |
| **Automated Test Suite** | `backend/tests/test_worker03_phase_a_security.py` | 6 automated tests verifying fail-closed hosted mode, read 401s, Bearer/Header auth, rate limiting 429s, and air-gapped zero egress. |

---

## 3. Test Strategy & Verification Results

### 3.1 Automated Phase A Test Suite (`test_worker03_phase_a_security.py`)

- **Execution Command:** `pytest backend/tests/test_worker03_phase_a_security.py -v`
- **Result:** 6 passed in 4.24s (100% pass rate)

```text
backend/tests/test_worker03_phase_a_security.py::test_hosted_mode_fails_closed_without_api_key_on_upload PASSED
backend/tests/test_worker03_phase_a_security.py::test_hosted_mode_fails_closed_without_api_key_on_list PASSED
backend/tests/test_worker03_phase_a_security.py::test_unauthenticated_read_endpoints_fail_with_401_when_key_set PASSED
backend/tests/test_worker03_phase_a_security.py::test_authenticated_read_endpoints_succeed_with_header_and_bearer PASSED
backend/tests/test_worker03_phase_a_security.py::test_upload_rate_limiting_enforcement PASSED
backend/tests/test_worker03_phase_a_security.py::test_air_gapped_zero_outbound_network_egress PASSED
```

### 3.2 Regression Check Across Security & Rehearsal Suites

- **Execution Command:** `pytest backend/tests/test_phase_d_security.py backend/tests/test_phase_e_rehearsal.py backend/tests/test_web_workflow/test_workflow_api.py -v`
- **Result:** 19 passed in 5.15s (100% pass rate)

---

## 4. Acceptance Gate Confirmation

- [x] Hosted mode fails closed with HTTP 401 when no API key is configured.
- [x] All scan read endpoints (`/scans`, `/findings`, `/coverage`, `/risk`, `/export`) require authentication when `ASTRA_API_KEY` is configured.
- [x] Authenticated requests succeed with `X-ASTRA-API-KEY` or `Bearer <key>`.
- [x] Upload rate limiting protects the service against bursts with HTTP 429.
- [x] Zero outbound socket connections occur during full scan lifecycle.
