# Worker 02 Phase D Report: Security Hardening, Operational Controls & Surface Discovery Expansion

**Owner:** Evidence, Identity & Interoperable Inventory (Worker 02)  
**Stage:** 100-Point Improvement Roadmap — Phase D of E  
**Phase:** Phase D  
**Status:** IMPLEMENTED & VALIDATED  
**Traceability IDs:** R01, R02, R04, R08, R10  
**Acceptance Criteria:** AC-01, AC-02, AC-03, AC-07, AC-12  
**Date:** 2026-10-04  

---

## 1. Executive Summary & Objective

Phase D resolves the operational security and surface boundary challenges highlighted in Section 4 & 5 of the *ASTRA / SIH26164 Product Assessment and 100-Point Improvement Roadmap*:
1. **Hosted Mode Guardrails (`ASTRA_HOSTED_MODE=1`)**:
   - Closed arbitrary server filesystem read vulnerabilities: `POST /api/v1/scans/directory` is actively rejected with **HTTP 403 Forbidden** in hosted demo mode unless explicitly overridden with `ASTRA_ALLOW_DIRECTORY_SCAN=1`.
   - In hosted mode, users interact exclusively via isolated, ephemeral archive uploads.
2. **API Token Authentication**:
   - Implemented token authentication dependency `verify_api_key` enforced on all mutating scan routes (`/api/v1/scans/upload`, `/api/v1/scans/directory`, `/api/v1/scans/{id}/context`).
   - Supports both `X-ASTRA-API-KEY` custom header and `Authorization: Bearer <token>` when `ASTRA_API_KEY` is configured in the environment.
3. **Upload Boundary Limit Quotas**:
   - Enforced a default 50 MB payload upload limit (configurable via `ASTRA_MAX_UPLOAD_SIZE_BYTES`) with real-time stream monitoring rejecting oversized requests with **HTTP 413 Payload Too Large**.
4. **Safe Local Loopback Defaults & Warning**:
   - Standardized `astra serve` and backend runner to bind exclusively to `127.0.0.1` by default.
   - Emits a bold security warning if binding to `0.0.0.0` or `::` without authentication configured.
5. **OCI Container Layer & Manifest Discovery**:
   - Extended `ContainerCryptoDetector` beyond basic Dockerfile text matching to parse OCI/Docker container manifests (`manifest.json`, `index.json`, `oci-layout`) and inspect unpacked container layer archives (`layer.tar`).
   - Confirmed deterministic extraction of system cryptographic libraries (e.g., `OpenSSL`, `WolfSSL`, `liboqs`) and base image identifiers.
6. **Formal Security Governance**:
   - Published comprehensive deployment threat model in `.brain/.work/threat_model.md` covering full STRIDE analysis and trust boundaries.
   - Enriched `SECURITY.md` with operational policies and external hardware boundaries (Cloud KMS/HSM).

---

## 2. Technical Decisions & Code Deliverables

| Module | File | Changes Made |
|---|---|---|
| **API Gateway & Routing** | `backend/app/main.py` | Added `is_hosted_mode()`, `is_directory_scan_allowed()`, `get_max_upload_size()`, and `verify_api_key()` dependency. Enforced 403 in hosted mode, 401 on unauthorized calls, and 413 on oversized uploads. |
| **CLI Runner** | `backend/app/cli.py` | Added `--api-key` parameter and security warning when binding to `0.0.0.0` without authentication. |
| **Container Detector** | `backend/app/discovery/detectors/container_detector.py` | Expanded `can_analyze` and `analyze_file` to inspect OCI manifests and layer tar archives directly for cryptographic components. |
| **Security Architecture** | `SECURITY.md` | Documented loopback defaults, hosted mode protections, API key auth, and upload size quotas. |
| **Threat Model** | `.brain/.work/threat_model.md` | Authored full STRIDE threat analysis, data flow diagrams, and trust boundaries. |
| **Automated Test Suite** | `backend/tests/test_phase_d_security.py` | 8 dedicated automated tests verifying hosted mode, auth enforcement, size quotas, and OCI layer inspection. |

---

## 3. Test Strategy & Verification Results

### 3.1 Automated Phase D Test Suite (`test_phase_d_security.py`)

- **Execution Command:** `pytest backend/tests/test_phase_d_security.py -v`
- **Result:** 8 passed in 1.99s (100% pass rate)

```
tests/test_phase_d_security.py::test_hosted_mode_disallows_directory_scan PASSED
tests/test_phase_d_security.py::test_hosted_mode_override_permits_directory_scan PASSED
tests/test_phase_d_security.py::test_api_key_authentication_enforcement PASSED
tests/test_phase_d_security.py::test_upload_size_limit_quota PASSED
tests/test_phase_d_security.py::test_health_reflects_hosted_mode_status PASSED
tests/test_phase_d_security.py::test_oci_container_manifest_inspection PASSED
tests/test_phase_d_security.py::test_oci_container_layer_tar_archive_inspection PASSED
tests/test_phase_d_security.py::test_cli_host_and_api_key_configuration PASSED
```

### 3.2 Full Repository Regression Run

- **Backend Test Suite:** `pytest` $\rightarrow$ **112 passed, 1 skipped** in 9.52s.
- **Frontend Test Suite:** `npm test -- --run` $\rightarrow$ **192 passed across 48 test files** (100% pass rate).

---

## 4. Acceptance Gate Confirmation

- [x] Hosted mode disables arbitrary directory scans with HTTP 403 Forbidden.
- [x] API token authentication verified for both `X-ASTRA-API-KEY` and Bearer token headers.
- [x] Upload quotas reject oversized archives with HTTP 413 Payload Too Large.
- [x] Loopback binding (`127.0.0.1`) enforced by default with warnings for `0.0.0.0`.
- [x] Container detector inspects OCI manifests and layer tar archives for crypto libraries.
- [x] Formal STRIDE threat model published in `.brain/.work/threat_model.md`.
- [x] All 112 backend tests and 192 frontend tests passing green.
- [x] Phase D gate complete and validated. Ready for Phase E.
