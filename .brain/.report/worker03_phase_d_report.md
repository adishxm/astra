# Worker 03 Phase D Report: Real OCI Image Layout Discovery & CycloneDX 1.6 CBOM Dependency Relationships

**Owner:** Risk, Migration Planning & Secure Operations (Worker 03)  
**Stage:** 100-Point Fresh Assessment Roadmap — Phase D of E  
**Phase:** Phase D  
**Status:** IMPLEMENTED & VALIDATED  
**Traceability IDs:** R12, R13, R14, R15  
**Acceptance Criteria:** AC-13, AC-14, AC-15  
**Date:** 2026-10-04  

---

## 1. Executive Summary & Objective

Phase D resolves the container inspection limitations and CBOM dependency representation gaps identified in the Fresh Product Assessment:
1. **Real OCI Image Layout Traversal & Layer Blob Decompression**:
   - Modern OCI container image layouts store extensionless, content-addressed tarballs under `blobs/sha256/<digest>`.
   - Upgraded `ContainerCryptoDetector` in `backend/app/discovery/detectors/container_detector.py`:
     - Detects OCI image layout roots (`index.json`, `oci-layout`, `blobs/sha256/`).
     - Parses `index.json` to resolve image manifest descriptors (`application/vnd.oci.image.manifest.v1+json`).
     - Follows manifest layer descriptors (`application/vnd.oci.image.layer.v1.tar+gzip`, `application/vnd.docker.image.rootfs.diff.tar.gzip`).
     - Decompresses gzip layer blobs safely on the fly (inspects gzip magic bytes `\x1f\x8b` and auto-detects archive format).
     - Traverses layer filesystem hierarchies to extract system cryptographic libraries:
       - `libssl.so*` $\rightarrow$ `OpenSSL` (SYSTEM_CRYPTO_SUITE, CONFIRMED)
       - `libcrypto.so*` $\rightarrow$ `OpenSSL-libcrypto` (SYSTEM_CRYPTO_SUITE, CONFIRMED)
       - `libwolfssl.so*` $\rightarrow$ `WolfSSL` (EMBEDDED_CRYPTO_SUITE, CONFIRMED)
       - `libgnutls.so*` $\rightarrow$ `GnuTLS` (SYSTEM_CRYPTO_SUITE, CONFIRMED)
       - `liboqs.so*` $\rightarrow$ `liboqs` (PQC_ALGORITHMS, CONFIRMED)
       - `/etc/ssl/certs/*` or `ca-certificates.crt` $\rightarrow$ `X.509-Root-Trust-Store` (PKI_TRUST_STORE, HIGH)
       - `/usr/bin/openssl` $\rightarrow$ `OpenSSL-CLI` (SYSTEM_CRYPTO_SUITE, HIGH)
2. **Defensive Archive Safeguards**:
   - Layer digest integrity verification: compares actual SHA-256 hash of layer blob against the manifest's expected `digest`; tampered or corrupted blobs are rejected before decompression.
   - Decompression bomb defenses: limits layer blob size ($\le 100\text{MB}$), member count ($\le 50,000$), and cumulative decompressed bytes ($\le 250\text{MB}$).
   - Path traversal defenses: skips any members containing `..` or leading `/`.
3. **CycloneDX 1.6 CBOM Dependency Graph**:
   - Upgraded `backend/app/services/scan_service.py` to emit standard CycloneDX 1.6 `dependencies` arrays:
     - Root application component assigns `bom-ref: urn:astra:app:<target-name>`.
     - Each cryptographic component declares a unique `bom-ref: urn:astra:crypto:<asset-id>`.
     - The top-level `dependencies` section defines the hierarchical graph: the application depends on discovered crypto primitives and components, and leaf assets declare `dependsOn: []`.
   - Verified that the generated CBOM validates against the official CycloneDX 1.6 JSON Schema (`bom-1.6.schema.json`) with zero validation errors.

---

## 2. Technical Decisions & Code Deliverables

| Module | File | Changes Made |
|---|---|---|
| **Container Detector** | `backend/app/discovery/detectors/container_detector.py` | Added `_analyze_oci_layout`, `_inspect_layer_archive`, and `_analyze_content_addressed_blob`; supports gzip magic byte detection and safe decompression under strict quotas. |
| **Master Scan Service** | `backend/app/services/scan_service.py` | Assigned `bom-ref` to metadata component and all cryptographic assets; generated `dependencies` graph linking root app to crypto assets; imported `re`. |
| **Automated Test Suite** | `backend/tests/test_worker03_phase_d_oci_cbom.py` | 3 automated tests verifying synthetic OCI layout traversal, corrupted blob digest defense, and CycloneDX 1.6 CBOM dependency schema validity. |

---

## 3. Test Strategy & Verification Results

### 3.1 Automated Phase D Test Suite (`test_worker03_phase_d_oci_cbom.py`)

- **Execution Command:** `pytest backend/tests/test_worker03_phase_d_oci_cbom.py -v`
- **Result:** 3 passed in 1.01s (100% pass rate)

```text
backend/tests/test_worker03_phase_d_oci_cbom.py::TestWorker03PhaseDOCICBOM::test_real_oci_image_layout_discovery PASSED [ 33%]
backend/tests/test_worker03_phase_d_oci_cbom.py::TestWorker03PhaseDOCICBOM::test_oci_hostile_archive_safeguards PASSED [ 66%]
backend/tests/test_worker03_phase_d_oci_cbom.py::TestWorker03PhaseDOCICBOM::test_cbom_dependencies_graph_and_schema_validation PASSED [100%]
```

### 3.2 Container Discovery & Security Regression Suite

- **Execution Command:** `pytest backend/tests/test_phase_d_security.py backend/tests/test_discovery/test_prod_discovery.py -v`
- **Result:** 12 passed in 1.93s (100% pass rate)

### 3.3 Full Cumulative Suite (Phase A through Phase D)

- **Execution Command:** `pytest backend/tests/test_worker03_phase_a_security.py backend/tests/test_worker03_phase_b_frontend_semantics.py backend/tests/test_worker03_phase_c_benchmark.py backend/tests/test_worker03_phase_d_oci_cbom.py backend/tests/test_e2e_corpus_benchmark.py backend/tests/test_e2e_product.py -v`
- **Result:** 34 passed in 10.42s (100% pass rate)

---

## 4. Acceptance Gate Confirmation

- [x] OCI image layout index and manifest blobs successfully resolve and decompress gzip layer archives on the fly.
- [x] Hostile or tampered layer digests are detected and rejected prior to extraction.
- [x] Memory and file quotas prevent zip-bomb exploits during container layer decompression.
- [x] Generated CycloneDX 1.6 CBOM contains standard `dependencies` graph linking root application to cryptographic components.
- [x] Generated CBOM passes official CycloneDX 1.6 JSON Schema validation (`bom-1.6.schema.json`).
