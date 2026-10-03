# Worker 01 MVP-02 Report: Supported Source, Manifest, Config and Certificate Discovery

**Owner:** Discovery & Safe Intake (Worker 01)  
**Stage:** MVP  
**Phase:** MVP-02  
**Status:** IMPLEMENTED & VALIDATED  
**Traceability IDs:** R01, R02, R05, R06  
**Acceptance Criteria:** AC-03, AC-04, AC-06  
**Date:** 2026-10-03  

---

## 1. Objective & Scope
Implemented deterministic cryptographic discovery across multi-language source code, package manifests, server configurations, and X.509 certificates. Emits canonical `Observation` objects conforming to the W01 $\to$ W02 shared interface contract. Enforces zero private-key leakage, evidence hashing, snippet sanitization, and truthful evidence states.

---

## 2. Implemented Components

1. **`backend/app/discovery/models.py`**:
   - `Observation`: Standardized schema featuring:
     - `observation_id` (UUIDv4), `scan_id`, `candidate_asset_id`
     - `claim_type`: `ALGORITHM_USE`, `DEPENDENCY_REFERENCE`, `CONFIG_PARAMETER`, `CERTIFICATE_METADATA`, `KEY_SPECIFICATION`
     - `source_kind`: `SOURCE_CODE`, `MANIFEST`, `CONFIG`, `CERTIFICATE`
     - Algorithm parameters: `algorithm`, `protocol`, `purpose`, `key_size_bits`, `curve_name`
     - Evidence anchor: `relative_path`, `start_line`, `end_line`, `evidence_digest` (SHA-256), `sanitized_excerpt`, `redacted` flag
     - Provenance & confidence: `detector_id`, `ruleset_version`, `confidence` (`CONFIRMED`, `HIGH`, `MEDIUM`, `LOW`, `HEURISTIC`), `state` (`OBSERVED`, `INFERRED`, `DECLARED`, `VERIFIED`, `FAILED`)
   - `DiscoverySummary`: Aggregates analyzed files, files with findings, zero findings, unsupported formats, and detector health.

2. **`backend/app/discovery/detectors/source_detector.py`**:
   - Deterministic AST and regex pattern matching covering:
     - Classical symmetric ciphers: AES (128, 192, 256), ChaCha20, 3DES, DES, RC4
     - Classical hashing: SHA-256, SHA-384, SHA-512, SHA-3, BLAKE2, MD5, SHA-1
     - Quantum-vulnerable asymmetric: RSA (1024, 2048, 3072, 4096), DSA, ECDSA, ECDH, Ed25519, X25519, ECC Curves (P-256, P-384)
     - NIST Post-Quantum Cryptography: ML-KEM (Kyber), ML-DSA (Dilithium), SLH-DSA (SPHINCS+), Falcon, Classic-McEliece
   - Automated secret and token sanitization (`[REDACTED_SECRET]`).

3. **`backend/app/discovery/detectors/manifest_detector.py`**:
   - Parses package manifests: `package.json`, `pom.xml`, `requirements.txt`, `pyproject.toml`, `go.mod`, `Cargo.toml`.
   - Discovers cryptographic libraries (e.g. `bouncycastle`, `cryptography`, `crypto-js`, `circl`, `liboqs`, `ring`).

4. **`backend/app/discovery/detectors/config_detector.py`**:
   - Parses TLS protocol configurations (`TLSv1.3`, `TLSv1.2`, deprecated `TLSv1.0`, `SSLv3`).
   - Detects cipher suite configurations (`ECDHE-AES256-GCM`, `DHE-AES-GCM`) and SSH key exchange parameters.

5. **`backend/app/discovery/detectors/certificate_detector.py`**:
   - Parses X.509 certificates (PEM and DER) extracting Subject, Issuer, Public Key Algorithm, Key Size, Signature Algorithm, and validity range.
   - **Zero Secret Leakage**: If private key markers (`BEGIN PRIVATE KEY`) are present, private key data is masked with `[REDACTED_PRIVATE_KEY_MATERIAL]`, marked with `redacted = True`, and private key bytes are never stored.

6. **`backend/app/discovery/engine.py`**:
   - `DiscoveryEngine`: Master coordinator executing all detectors across sandbox files, tracking denominator metrics, and saving `observations.json` for downstream Worker 02 consumption.

---

## 3. Phase Validation & Test Results
Executed 21 total tests via pytest (8 new MVP-02 tests + 13 MVP-01 regression tests):

| Test Case | Scenario Tested | Result |
|---|---|---|
| `test_source_detector_classical_and_pqc` | Discovery of AES, SHA-256, and ML-KEM (Kyber) in source code | **PASSED** |
| `test_source_detector_vulnerable_and_secret_redaction` | Identification of MD5, vulnerable status, and inline secret masking | **PASSED** |
| `test_manifest_detector_package_json` | Extraction of `crypto-js` from `package.json` | **PASSED** |
| `test_manifest_detector_pom_xml` | XML parsing and extraction of BouncyCastle from `pom.xml` | **PASSED** |
| `test_config_detector_tls_and_ssh` | Extraction of TLSv1.3, TLSv1.2, and cipher suites from config | **PASSED** |
| `test_certificate_detector_x509_public_metadata` | Parsing live self-signed X.509 cert; RSA-2048 key size extraction | **PASSED** |
| `test_certificate_detector_private_key_redaction` | Strict redaction of private keys (`[REDACTED_PRIVATE_KEY_MATERIAL]`) | **PASSED** |
| `test_discovery_engine_end_to_end` | Multi-file repository scan, summary metrics, `observations.json` output | **PASSED** |
| *Intake MVP-01 Tests (13 cases)* | Zip bomb, path traversal, symlink blocking, limits, sandbox lifecycle | **PASSED** |

**Summary**: 21/21 tests passed (100% pass rate).

---

## 4. Downstream Handoff
- **To Worker 02 (Evidence & Inventory)**: `observations.json` containing standardized observations with immutable evidence digests, line ranges, and calibrated confidence bands (`CONFIRMED`, `HIGH`, `MEDIUM`).
- **To Worker 03 (Risk & Migration)**: Algorithm names, quantum status tags (`QUANTUM_VULNERABLE`, `POST_QUANTUM`, `VULNERABLE`), and key sizes ready for contextual risk scoring.
