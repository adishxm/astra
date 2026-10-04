# Worker 03 Phase C Report: Empirical Benchmark Math Repair: Finding-Level Precision, Unmatched False Positive Accounting & Holdout Integrity

**Owner:** Risk, Migration Planning & Secure Operations (Worker 03)  
**Stage:** 100-Point Fresh Assessment Roadmap — Phase C of E  
**Phase:** Phase C  
**Status:** IMPLEMENTED & VALIDATED  
**Traceability IDs:** R05, R06, R11  
**Acceptance Criteria:** AC-06, AC-09, AC-10  
**Date:** 2026-10-04  

---

## 1. Executive Summary & Objective

Phase C fixes the benchmark metric math flaws exposed in the Fresh Product Assessment:
1. **Unmatched / Spurious Findings Now Count as False Positives**:
   - In the prior implementation, on positive files each expected label was checked, but extra detected findings that had no matching ground-truth label were discarded from the false positive count.
   - Refactored `compute_metrics` in `backend/tests/test_e2e_corpus_benchmark.py`:
     - Every detected finding is evaluated. Any prediction on a positive file not matching an expected label is penalized as an **FP**.
     - Any prediction on a negative control file is penalized as an **FP**.
     - Any ground-truth expected label not matched by a detection is an **FN**.
     - Successfully matched pairs count as **TP**.
     - Clean negative control files with zero detections count as **TN**.
2. **Replication & Verification of Assessment Probe**:
   - Under the prior math, a test with expected RSA but with extra MD5 and AES detections produced `TP=1, FP=0, precision=100%`.
   - Under the repaired math, the same probe correctly reports `TP=1, FP=2, FN=0, precision=33.33%`.
3. **Strict Canonical Algorithm Matcher**:
   - Replaced loose substring and reverse-substring matching (`or exp in det or det in exp`) with strict canonical normalization and verified cryptographic equivalence dictionaries (e.g. `RSA2048` $\leftrightarrow$ `RSA`, `AES256` $\leftrightarrow$ `AES256GCM`, `ECDSA` $\leftrightarrow$ `secp256r1`).
   - Fixed regex flaw in `config_detector.py` where `TLSv1` matched `TLSv1.2` and `TLSv1.3` as false positive `TLSv1.0` via negative lookahead `TLSv1(?!\.)`.
4. **Clean, Unit-Consistent Denominators**:
   - Finding-level Precision: $\frac{TP}{TP + FP}$
   - Finding-level Recall: $\frac{TP}{TP + FN}$
   - Finding-level $F_1$: $2 \cdot \frac{Precision \cdot Recall}{Precision + Recall}$
   - Negative Control False Alarm Rate: $\frac{\text{Negative Control Violations}}{\text{Total Negative Control Files}}$ (consistent file unit).

---

## 2. Technical Decisions & Code Deliverables

| Module | File | Changes Made |
|---|---|---|
| **Benchmark Metric Engine** | `backend/tests/test_e2e_corpus_benchmark.py` | Refactored `compute_metrics` for bipartite finding-level matching; penalizes all extra detections on positive files as FPs; enforces unit-consistent negative control FPR. |
| **Configuration Detector** | `backend/app/discovery/detectors/config_detector.py` | Refined `TLSv1.0` signature with `TLSv1(?!\.)` to prevent false positive detections on `TLSv1.2` and `TLSv1.3`. |
| **Phase C Automated Test Suite** | `backend/tests/test_worker03_phase_c_benchmark.py` | 5 automated tests verifying the assessment probe replication, adversarial noise degradation, negative control accounting, strict matching, and corpus quality thresholds. |

---

## 3. Test Strategy & Verification Results

### 3.1 Automated Phase C Test Suite (`test_worker03_phase_c_benchmark.py`)

- **Execution Command:** `pytest backend/tests/test_worker03_phase_c_benchmark.py -v`
- **Result:** 5 passed in 1.86s (100% pass rate)

```text
backend/tests/test_worker03_phase_c_benchmark.py::TestWorker03PhaseCBenchmarkMath::test_direct_assessment_probe_repaired PASSED [ 20%]
backend/tests/test_worker03_phase_c_benchmark.py::TestWorker03PhaseCBenchmarkMath::test_adversarial_noise_injection_degrades_precision PASSED [ 40%]
backend/tests/test_worker03_phase_c_benchmark.py::TestWorker03PhaseCBenchmarkMath::test_negative_control_spurious_detection_penalized PASSED [ 60%]
backend/tests/test_worker03_phase_c_benchmark.py::TestWorker03PhaseCBenchmarkMath::test_strict_algo_matcher_rejects_unrelated_substrings PASSED [ 80%]
backend/tests/test_worker03_phase_c_benchmark.py::TestWorker03PhaseCBenchmarkMath::test_corpus_benchmark_passes_research_thresholds PASSED [100%]
```

### 3.2 Repaired Ground Truth Benchmark (`test_e2e_corpus_benchmark.py`)

- **Execution Command:** `pytest backend/tests/test_e2e_corpus_benchmark.py -v -s`
- **Result:** 5 passed in 1.10s (100% pass rate)

```text
[Phase C Benchmark — Training Set]
TP=29, FP=0, FN=0, TN=6
Precision: 100.00% (Threshold: >= 80.00%)
Recall:    100.00% (Threshold: >= 80.00%)
F1 Score:  100.00%
FPR:       0.00%

[Phase C Benchmark — Holdout Set]
TP=10, FP=0, FN=0, TN=1
Precision: 100.00% (Threshold: >= 80.00%)
Recall:    100.00% (Threshold: >= 80.00%)
F1 Score:  100.00%

[Surface Breakdown: MANIFEST]      Precision: 100.00% | Recall: 100.00%
[Surface Breakdown: CONFIG]        Precision: 100.00% | Recall: 100.00%
[Surface Breakdown: SOURCE_CODE]   Precision: 100.00% | Recall: 100.00%
[Surface Breakdown: CERTIFICATE]   Precision: 100.00% | Recall: 100.00%
```

### 3.3 Full Regression Suite

- **Execution Command:** `pytest backend/tests/test_worker03_phase_a_security.py backend/tests/test_worker03_phase_b_frontend_semantics.py backend/tests/test_worker03_phase_c_benchmark.py backend/tests/test_e2e_corpus_benchmark.py backend/tests/test_e2e_product.py -v`
- **Result:** 31 passed in 10.16s (100% pass rate)

---

## 4. Acceptance Gate Confirmation

- [x] Extra detected algorithms on positive files count as False Positives ($Precision < 100\%$ on noisy predictions).
- [x] Spurious findings on negative control files count as False Positives with consistent file denominator ($FPR = \frac{\text{Violations}}{\text{Negative Files}}$).
- [x] Strict canonical algorithm matcher eliminates loose substring matches.
- [x] Config detector false-positive on `TLSv1` prefix resolved.
- [x] Training and Holdout benchmarks both achieve $\ge 80\%$ Precision and $\ge 80\%$ Recall under repaired, adversarial-sensitive math.
