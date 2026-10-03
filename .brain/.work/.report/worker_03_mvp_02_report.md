# Worker 03 MVP-02 Report: Candidate Mapping and Actionable Migration Backlog

**Owner:** Risk, Context & Migration Decision Support (Worker 03)  
**Stage:** MVP  
**Phase:** MVP-02  
**Status:** IMPLEMENTED & VALIDATED  
**Traceability IDs:** R02, R03, R04, R05, R08  
**Acceptance Criteria:** AC-08, AC-10  
**Date:** 2026-10-03  

---

## 1. Objective & Scope
Created an advisory cryptographic migration backlog engine mapping discovered vulnerable and classical assets to official, dated NIST Post-Quantum standards (FIPS 203, 204, 205). Each work item provides concrete recommended actions, hybrid transition paths, and explicit operational/compatibility caveats.

---

## 2. Implemented Components

1. **`backend/app/risk/taxonomy.py`**:
   - `ALGORITHM_CATALOG`: Dated authority references:
     - `RSA` $\to$ `ML-KEM-768` (KEX) / `ML-DSA-65` (Signatures) citing NIST FIPS 203 & 204 (Aug 2024); notes public key expansion ($256\text{B} \to 1,184\text{B}$) and ciphertext sizes.
     - `ECDSA` / `Ed25519` $\to$ `ML-DSA-65` / `SLH-DSA-128s` citing NIST FIPS 204 & 205 (Aug 2024); notes signature expansion ($64\text{B} \to 3,309\text{B}$).
     - `X25519` $\to$ `Hybrid X25519 + ML-KEM-768` (IETF draft-ietf-tls-hybrid-design).
     - `MD5` / `SHA-1` $\to$ `SHA-256` / `SHA3-256` citing NIST SP 800-131A Rev. 2.
     - `DES` / `3DES` / `RC4` $\to$ `AES-256-GCM` citing NIST SP 800-38D.

2. **`backend/app/risk/backlog.py`**:
   - `MigrationTask`: Actionable work item schema with asset location, algorithm, priority, dated standard, compatibility gaps, and human review recommendation.
   - `BacklogBuilder`: Generates prioritized backlog sorted by composite risk score descending.

---

## 3. Validation & Test Results
- `test_dated_pqc_mapping_for_rsa`: **PASSED** (ML-KEM-768 & FIPS 203 reference verified).
- `test_dated_pqc_mapping_for_ecdsa`: **PASSED** (ML-DSA & signature expansion caveats verified).
- `test_backlog_builder_priority_sorting`: **PASSED** (Tasks ordered by risk score descending).
