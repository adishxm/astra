# Worker 04 Phase D: Empirical Holdout Expansion, Real Surface Confusion Matrices & Ground-Truth Verification

**Document:** `phase_d.md`  
**Worker:** Worker 04 (`.brain/.work/webapp/worker_04`)  
**Target Roadmap Area:** P1 / Validation & Evidence Quality  
**Target Readiness Score Impact:** +4 points on Validation and Evidence Quality (Resolves Finding 3)  
**Status:** SPECIFICATION COMPLETE  

---

## 1. Objectives & Executive Scope

Phase D substantiates the empirical accuracy claims with a mathematically rigorous, multi-surface ground-truth benchmark and full per-surface confusion matrices:
1. **Corpus Expansion with Blinded/External Holdout Samples**:
   - Expand `backend/tests/fixtures/corpus/` with verified holdout fixtures:
     - Real OCI Image Layout container sample (`oci_holdout/` containing `index.json`, manifest, and hashed gzip layer).
     - Cloud KMS policy holdout (`kms_holdout.json` with AWS KMS CMKs and Azure Key Vault declarations).
     - PKCS#11 hardware module holdout (`pkcs11_holdout.conf` with token slot definitions).
     - Diverse negative controls with non-cryptographic terminology (e.g. `rsa` in variable names, `aes` in CSS styling, non-crypto hashing).
2. **Per-Surface Confusion Matrices & Metric Computation**:
   - In `backend/tests/test_e2e_corpus_benchmark.py`:
     - Maintain strict bipartite matching between ground-truth labels and detector observations.
     - Compute individual confusion matrices (TP, FP, FN, TN, Precision, Recall, F1, and Negative-Control FPR) across all surfaces:
       1. Source Code (Python, JS, Go, Java, C)
       2. Dependency Manifests
       3. TLS & Infrastructure Configs
       4. X.509 Certificates & Keys
       5. OCI Container Image Layouts
       6. Cloud KMS Policies
       7. PKCS#11 HSM Configurations
       8. Held-out Evaluation Samples
   - Enforce that every surface achieves $\ge 80\%$ Precision and $\ge 80\%$ Recall with $FPR \le 10\%$.
   - Output structured, machine-readable confusion matrices for review and documentation.

---

## 2. Technical Deliverables

| Deliverable | File | Target Behavior |
|---|---|---|
| **Corpus Holdout Fixtures** | `backend/tests/fixtures/corpus/` | Real OCI layout, Cloud KMS manifest, PKCS#11 config, and negative controls. |
| **Updated Labels Specification** | `backend/tests/fixtures/corpus/labels.json` | Truthful ground-truth annotations across all expanded surfaces. |
| **Multi-Surface Benchmark** | `backend/tests/test_e2e_corpus_benchmark.py` | Bipartite finding-level evaluation generating per-surface confusion matrices. |
| **Phase D Automated Test Suite**| `backend/tests/test_worker04_phase_d_benchmark_matrix.py` | Pytest suite validating confusion matrix generation and threshold conformance. |
| **Phase D Completion Report** | `.brain/.work/.report/worker04_phase_d_report.md` | Standardized audit report documenting all implementation details and verification results. |

---

## 3. Test Strategy & Acceptance Gates

- **Test D.1:** Assert all 8 benchmark surface categories pass Precision $\ge 80\%$, Recall $\ge 80\%$, F1 $\ge 80\%$.
- **Test D.2:** Assert negative control samples produce zero false positives on non-crypto code.
- **Test D.3:** Assert confusion matrix cleanly logs TP, FP, FN, and TN for every evaluated surface.
- **Test D.4:** Assert adversarial noise injection continues to drop precision without unpenalized leaks.
