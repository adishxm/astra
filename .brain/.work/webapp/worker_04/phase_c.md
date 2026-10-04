# Worker 04 Phase C: Cloud KMS & Hardware Security Module (PKCS#11) Discovery Adapters

**Document:** `phase_c.md`  
**Worker:** Worker 04 (`.brain/.work/webapp/worker_04`)  
**Target Roadmap Area:** P1 / SIH Problem Fit & Enterprise Scope Expansion  
**Target Readiness Score Impact:** +3 points on SIH Problem Fit and Coverage Breadth (Resolves Finding 6)  
**Status:** SPECIFICATION COMPLETE  

---

## 1. Objectives & Executive Scope

Phase C transitions Cloud KMS and Hardware Security Modules (PKCS#11) from conceptual roadmap items into testable, verifiable discovery engines:
1. **Cloud KMS Discovery Engine (`CloudKmsDetector`)**:
   - Inspects infrastructure-as-code manifests, Terraform templates, cloud formation files, and cloud key export policies:
     - **AWS KMS**: Key policy definitions (`kms:KeySpec`, `kms:KeyUsage`), customer managed keys (CMKs), detecting `RSA_2048`, `RSA_4096`, `ECC_NIST_P256`, `ECC_NIST_P384`, `ECC_NIST_P521`, `SYMMETRIC_DEFAULT` (AES-256-GCM).
     - **Azure Key Vault**: Key manifests and vault configurations, detecting `RSA`, `RSA-HSM`, `EC`, `EC-HSM`, `oct-HSM`.
     - **GCP Cloud KMS**: Key rings, crypto keys, and crypto key version definitions (`GOOGLE_SYMMETRIC_ENCRYPTION`, `RSA_SIGN_PSS_2048_SHA256`, `EC_SIGN_P256_SHA256`).
2. **Hardware Security Module & PKCS#11 Engine (`Pkcs11HsmDetector`)**:
   - Analyzes PKCS#11 configuration profiles (`pkcs11.conf`, `softhsm2.conf`, `opensc.conf`), token manifests, and slot definitions:
     - Detects hardware cryptographic mechanisms (`CKM_RSA_PKCS`, `CKM_RSA_PKCS_KEY_PAIR_GEN`, `CKM_ECDSA`, `CKM_AES_GCM`, `CKM_SHA256`).
     - Extracts hardware token characteristics: token label, manufacturer ID, hardware model, serial number, and security flags (`CKF_LOGIN_REQUIRED`, `CKF_USER_PIN_INITIALIZED`).
3. **Pipeline Integration**:
   - Integrate both detectors into `backend/app/discovery/engine.py` under `SourceKind.INFRASTRUCTURE` / `SourceKind.HARDWARE`.
   - Incorporate discovered KMS and PKCS#11 assets into `ScanRecord`, canonical asset identities, and CycloneDX 1.6 CBOM component lists.

---

## 2. Technical Deliverables

| Deliverable | File | Target Behavior |
|---|---|---|
| **Cloud KMS Detector** | `backend/app/discovery/detectors/cloud_kms_detector.py` | Parses AWS KMS, Azure Key Vault, and GCP Cloud KMS policies and templates. |
| **PKCS#11 HSM Detector** | `backend/app/discovery/detectors/pkcs11_detector.py` | Parses PKCS#11 configurations, slot descriptors, and cryptographic mechanisms. |
| **Discovery Engine Registry** | `backend/app/discovery/engine.py` | Registers `CloudKmsDetector` and `Pkcs11HsmDetector` into the default detection pipeline. |
| **Phase C Automated Test Suite**| `backend/tests/test_worker04_phase_c_kms_hsm.py` | Pytest suite verifying AWS/Azure/GCP KMS detection and PKCS#11 mechanism extraction. |
| **Phase C Completion Report** | `.brain/.work/.report/worker04_phase_c_report.md` | Standardized audit report documenting all implementation details and verification results. |

---

## 3. Test Strategy & Acceptance Gates

- **Test C.1:** Assert `CloudKmsDetector` extracts RSA-2048 and AES-256 keys from AWS KMS policies.
- **Test C.2:** Assert `CloudKmsDetector` extracts EC and RSA keys from Azure Key Vault and GCP Cloud KMS templates.
- **Test C.3:** Assert `Pkcs11HsmDetector` extracts `CKM_RSA_PKCS`, `CKM_ECDSA`, and hardware token metadata from PKCS#11 configs.
- **Test C.4:** Assert full scan pipeline aggregates Cloud KMS and PKCS#11 findings into canonical assets and CycloneDX 1.6 CBOM.
