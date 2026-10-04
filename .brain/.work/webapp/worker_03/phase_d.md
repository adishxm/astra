# Worker 03 Phase D: Real OCI Image Layout Discovery & CycloneDX 1.6 CBOM Dependency Relationships

**Document:** `phase_d.md`  
**Worker:** Worker 03 (`.brain/.work/webapp/worker_03`)  
**Target Roadmap Area:** P1 / P2 — Demonstrate real OCI image discovery & increase CBOM completeness  
**Target Readiness Score Impact:** +3 points on SIH Problem Fit, +3 points on Scan Engine, API & CLI  
**Status:** SPECIFICATION & ARCHITECTURE PLAN COMPLETE  

---

## 1. Objectives & Executive Scope

Phase D expands cryptographic discovery and inventory completeness by addressing container layout realities and CBOM graph modeling:
1. **Real OCI Image Layout Parsing & Layer Blob Decompression:**
   - Normal OCI container images store compressed layer blobs under extensionless content-addressed paths: `blobs/sha256/<digest>`.
   - Upgrade `ContainerCryptoDetector` in `backend/app/discovery/detectors/container_detector.py`:
     - Recognize OCI layout roots (`oci-layout`, `index.json`, `blobs/sha256/`).
     - Parse `index.json` to identify image manifests (`application/vnd.oci.image.manifest.v1+json`).
     - Resolve layer descriptors (`application/vnd.oci.image.layer.v1.tar+gzip`, `application/vnd.docker.image.rootfs.diff.tar.gzip`).
     - Decompress layer gzip blobs in-memory under strict streaming limits (max layer size, max file count, zip-bomb defense).
     - Traverse container filesystem trees to detect system crypto libraries (e.g. `libssl.so*`, `libcrypto.so*`, WolfSSL, OpenSSL, and `/etc/ssl/certs`).
2. **CycloneDX 1.6 CBOM Dependency Relationships:**
   - In `backend/app/inventory/cbom_generator.py`, expand the CycloneDX 1.6 generator to output a `dependencies` section.
   - Link the root application / scanned service to its declared and discovered cryptographic algorithms, libraries, and certificates.
   - Eliminates the "flat list" limitation and provides a true connected dependency graph as required by CycloneDX CBOM standards.

---

## 2. Technical Deliverables

| Deliverable | File | Target Behavior |
|---|---|---|
| **OCI Image Layout Detector** | `backend/app/discovery/detectors/container_detector.py` | Parse `oci-layout`, `index.json`, inspect gzip layer blobs in `blobs/sha256/...` safely. |
| **CBOM Dependency Graph** | `backend/app/inventory/cbom_generator.py` | Add `dependencies: [...]` linking software components to crypto algorithms. |
| **OCI Image Layout Test Fixture** | `backend/tests/fixtures/oci_image_layout/` | Realistic standards-compliant OCI layout with `index.json`, manifest blob, and gzip layer blob containing `libssl.so.3`. |
| **Phase D Automated Test Suite** | `backend/tests/test_worker03_phase_d_oci_cbom.py` | Tests OCI layout blob inspection, crypto library discovery, and CBOM dependency graph output. |
| **Phase D Completion Report** | `.brain/.work/.report/worker03_phase_d_report.md` | Standardized audit report documenting all implementation details and verification results. |

---

## 3. Test Strategy & Acceptance Gates

- **Test D.1:** Build realistic OCI image layout with hashed gzip layer blob containing `libssl.so.3`; assert `ContainerCryptoDetector` extracts OpenSSL cryptographic component.
- **Test D.2:** Verify OCI extraction adheres to streaming quotas, rejecting corrupted or bomb blobs safely.
- **Test D.3:** Verify exported CycloneDX 1.6 CBOM contains a valid `dependencies` graph linking components.
- **Test D.4:** Validate resulting CBOM against official CycloneDX 1.6 schema (0 schema errors).
