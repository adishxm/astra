# Phase C: Prove Detector Quality with End-to-End Ground Truth Benchmarking

**Document:** `phase_c.md`  
**Worker:** Worker 02 (`.brain/.work/webapp/worker_02`)  
**Target Roadmap Area:** Phase C — Prove detector quality (P1 Findings)  
**Target Readiness Score Impact:** 80/100 -> 90/100 (+10 points in Validation & Evidence Quality)  
**Status:** SPECIFICATION & ARCHITECTURE PLAN COMPLETE  

---

## 1. Objectives & Executive Scope

Phase C resolves the evidence quality limitation identified in Section 4 & 5 of the Assessment Roadmap:
1. **P1: Empirical Detector Precision & Recall vs Arithmetic Mocking:**
   - Previous tests fed pre-fabricated observation mock objects into the arithmetic scoring function.
   - Build a comprehensive, multi-language, multi-surface labelled test corpus containing genuine cryptographic patterns and challenging negative fixtures.
   - Run the actual `DiscoveryEngine` pipeline on disk against the corpus to generate real observations.
   - Benchmark precision, recall, F1 score, and false-positive rate (FPR) across in-scope detector families (Source Code, Dependency Manifests, Certificates/Keys, TLS Configurations, and Static Binaries).
   - Enforce the research-grade acceptance bar: **$\ge 80\%$ Precision and $\ge 80\%$ Recall** overall and across primary detector categories.
2. **Holdout Corpus & Generalization:**
   - Maintain a dedicated holdout test set with unseen fixtures (different variable names, novel wrapper patterns, misleading comments) to verify that detectors are not overfitted to synthetic samples.
3. **Automated CI Regression Pipeline:**
   - Ensure the benchmark executes deterministically in pytest and logs per-family metrics and any false positives / missed cases.

---

## 2. Technical Specifications & Architecture

### 2.1 Multi-Surface Ground Truth Corpus
- Directory: `backend/tests/fixtures/corpus/`
- Directory: `backend/tests/fixtures/corpus/holdout/`
- Surface categories included:
  1. **Python (`source_code`):**
     - Positive: RSA-2048 key generation (`cryptography.hazmat`), AES-256-GCM cipher initialization, ECDSA P-256 signing, deprecated MD5/SHA-1 hashing.
     - Negative: `hashlib.sha256` non-security hash, non-crypto hashing (`mmh3`, `crc32`), comments discussing crypto without usage, variable names containing "key" or "secret" without crypto calls.
  2. **JavaScript / TypeScript (`source_code` & `manifest`):**
     - Positive: `crypto.subtle.generateKey("RSA-OAEP")`, `crypto.createCipheriv("aes-256-gcm")`, `package.json` with `@noble/ciphers` and `crypto-js`.
     - Negative: Standard math libraries, mock test objects, commented-out crypto import.
  3. **Go (`source_code` & `manifest`):**
     - Positive: `rsa.GenerateKey`, `ecdsa.GenerateKey`, `go.mod` with crypto dependencies.
     - Negative: standard string hashing or log formatting.
  4. **Java & C/C++ (`source_code`):**
     - Positive: `KeyPairGenerator.getInstance("RSA")`, OpenSSL `EVP_PKEY_Q_keygen("RSA")`.
  5. **Certificates & Keys (`certificate`):**
     - Positive: Valid test X.509 RSA-2048 certificate PEM, ECDSA P-256 certificate PEM.
     - Negative: Public text files, license text files, SSH non-key text.
  6. **TLS & Infrastructure Configs (`config`):**
     - Positive: `nginx.conf` with `ssl_protocols TLSv1.2 TLSv1.3; ssl_ciphers ...`
     - Negative: Standard proxy configuration without TLS blocks.

### 2.2 Benchmark Ground Truth Specification
- Metadata file: `backend/tests/fixtures/corpus/labels.json`
- Each entry defines:
  ```json
  {
    "relative_path": "python/vulnerable_rsa.py",
    "expected_algorithm": "RSA-2048",
    "surface": "SOURCE_CODE",
    "is_negative_fixture": false,
    "line_hint": 12
  }
  ```

### 2.3 Automated End-to-End Evaluation Engine
- Create `backend/tests/test_e2e_corpus_benchmark.py`:
  - Executes `DiscoveryEngine.run_discovery` on `backend/tests/fixtures/corpus`.
  - Maps generated observations to labelled expected findings using fuzzy location and algorithm matching.
  - Calculates:
    - $\text{Precision} = \frac{TP}{TP + FP}$
    - $\text{Recall} = \frac{TP}{TP + FN}$
    - $F_1 = 2 \cdot \frac{\text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}}$
    - $\text{FPR} = \frac{FP}{FP + TN}$
  - Enforces assertion: `Precision >= 0.80` and `Recall >= 0.80`.

---

## 3. Test Strategy & Specific Acceptance Gates

### Test 3.1: Corpus Execution Benchmark
- Run actual discovery engine on `corpus/` fixtures.
- Verify that detected findings match expected labels.
- Verify zero crashes or unhandled exceptions across malformed or unusual file formats.

### Test 3.2: Holdout Generalization Verification
- Run discovery engine on `corpus/holdout/`.
- Verify precision $\ge 80\%$ and recall $\ge 80\%$ on holdout set.

---

## 4. Phase C Deliverables
- [x] Architecture specification (`phase_c.md`)
- [ ] Labelled corpus test files: `backend/tests/fixtures/corpus/*`
- [ ] Ground truth definition: `backend/tests/fixtures/corpus/labels.json`
- [ ] Automated end-to-end benchmark test: `backend/tests/test_e2e_corpus_benchmark.py`
- [ ] Phase completion report: `.brain/.work/.report/phase_c_report.md`
- [ ] Git commit and push upon completion.
