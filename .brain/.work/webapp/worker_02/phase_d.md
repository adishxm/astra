# Phase D: Security Hardening, Operational Controls & Surface Discovery Expansion

**Document:** `phase_d.md`  
**Worker:** Worker 02 (`.brain/.work/webapp/worker_02`)  
**Target Roadmap Area:** Phase D — Secure and scope the demo (P1 Findings)  
**Target Readiness Score Impact:** 90/100 -> 96/100 (+6 points in Security/Operations & Problem Fit)  
**Status:** SPECIFICATION & ARCHITECTURE PLAN COMPLETE  

---

## 1. Objectives & Executive Scope

Phase D addresses the operational security vulnerabilities and surface scope honesty highlighted in Section 4 & 5:
1. **P1: Operational Security Controls & Safe Local Defaults:**
   - Enforce loopback binding (`127.0.0.1`) by default across CLI, server runners, and documentation; issue active runtime warnings if binding to `0.0.0.0` without authentication.
   - Implement Hosted Mode Protection (`ASTRA_HOSTED_MODE=1`):
     - Block arbitrary server filesystem path scans (`POST /api/v1/scans/directory` returns HTTP 403). Only authenticated archive uploads are permitted.
     - Enforce CORS origin restrictions via `ASTRA_CORS_ORIGINS`.
     - Introduce API Token Authentication (`X-ASTRA-API-KEY` / Bearer token via `ASTRA_API_KEY`).
     - Enforce upload boundary limits: archive payload size quotas (50MB default limit) and rate-limiting.
   - Produce a formal deployment threat model (`SECURITY.md` and `.brain/.work/threat_model.md`) defining trust boundaries, attack vectors, and mitigations.
2. **P1: Precise Scope Classification & Surface Expansion:**
   - Differentiate static Dockerfile inspection from real OCI layer archive inspection. Expand `container_detector.py` to inspect unpacked OCI container layer archives (`layer.tar`, `manifest.json`, OCI index).
   - Demonstrate live runtime TLS handshake inspection via `NetworkEndpointDetector` on authorized local endpoints.
   - Clearly publish the Supported Surface Matrix in documentation and UI, honestly marking cloud KMS and physical HSMs as external hardware-dependent boundaries.

---

## 2. Technical Specifications & Architecture

### 2.1 Security Middleware & Access Control
- **File:** `backend/app/main.py`
  - Update CORS middleware: when `ASTRA_HOSTED_MODE=1`, reject wildcard `*` if origins are specified; reject credentials with wildcard.
  - Implement optional API Key Authentication middleware:
    - If `ASTRA_API_KEY` is configured in environment, require `X-ASTRA-API-KEY` or `Authorization: Bearer <key>` on all non-static mutating routes (`/api/v1/scans/upload`, `/api/v1/scans/directory`, `/api/v1/scans/{id}/context`).
  - In `POST /api/v1/scans/directory`:
    - Enforce check: `if ASTRA_HOSTED_MODE and not ASTRA_ALLOW_DIRECTORY_SCAN: raise HTTPException(status_code=403, detail="Arbitrary directory scanning is disabled in hosted mode.")`.
  - In `POST /api/v1/scans/upload`:
    - Check file size before reading full content into memory (reject files > `MAX_UPLOAD_SIZE_BYTES`, default 50 MB, with HTTP 413 Payload Too Large).

### 2.2 CLI Hardening
- **File:** `backend/app/cli.py`
  - Ensure default `--host` is `127.0.0.1`.
  - If `--host 0.0.0.0` is specified without `--api-key` or `ASTRA_API_KEY`, display bold warning: `"[SECURITY WARNING] Binding to 0.0.0.0 exposes the ASTRA API without authentication. Use 127.0.0.1 or configure an API key."`

### 2.3 Surface Discovery Expansion
- **File:** `backend/app/discovery/detectors/container_detector.py`
  - Add OCI layer analyzer capability:
    - Reads OCI image directory or tar containing `manifest.json` / `oci-layout`.
    - Detects system crypto libraries, OpenSSL packages, and installed crypto modules directly from container file tree / layer index.
- **File:** `backend/app/discovery/detectors/network_detector.py`
  - Connect live TLS inspection capability to test against local loopback TLS endpoints with authorized hostname checks.

---

## 3. Test Strategy & Specific Acceptance Gates

### Test 3.1: Security & Hosted Mode Gate (`test_phase_d_security.py`)
- Test hosted mode flag (`ASTRA_HOSTED_MODE=1`):
  - Request `POST /api/v1/scans/directory` -> asserts HTTP 403 Forbidden.
- Test API Key authentication when `ASTRA_API_KEY="secret-key"`:
  - Request upload without header -> asserts HTTP 401 Unauthorized.
  - Request upload with `X-ASTRA-API-KEY: secret-key` -> asserts HTTP 200.
- Test payload size limit:
  - Submit 60MB file -> asserts HTTP 413 Payload Too Large.

### Test 3.2: Container & Network Surface Discovery Gate
- Run scan on sample OCI manifest / container definition; assert base image and crypto packages are classified under `CONTAINER` surface.
- Run live handshake inspector against local test server; assert negotiated ciphersuite is extracted under `NETWORK` surface.

---

## 4. Phase D Deliverables
- [x] Architecture specification (`phase_d.md`)
- [ ] Code modifications: `backend/app/main.py`, `backend/app/cli.py`, `backend/app/discovery/detectors/container_detector.py`
- [ ] Security documentation: `SECURITY.md`, `.brain/.work/threat_model.md`
- [ ] Automated test suite: `backend/tests/test_phase_d_security.py`
- [ ] Phase completion report: `.brain/.work/.report/phase_d_report.md`
- [ ] Git commit and push upon completion.
