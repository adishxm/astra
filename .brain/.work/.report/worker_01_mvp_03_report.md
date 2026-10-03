# Worker 01 MVP-03 Report: Coverage, Partial Scans and Benchmark Readiness

**Owner:** Discovery & Safe Intake (Worker 01)  
**Stage:** MVP  
**Phase:** MVP-03  
**Status:** IMPLEMENTED & VALIDATED  
**Traceability IDs:** R02, R03, R06, R10, R12  
**Acceptance Criteria:** AC-04, AC-06, AC-11, AC-12  
**Date:** 2026-10-03  

---

## 1. Objective & Scope
Implemented transparent coverage accounting, honest denominator tracking, blind-spot visibility, partial-scan state resilience, and a reproducible seeded benchmark engine. Enforces AC-04 (zero findings $\ne$ "safe"), AC-11 (explicit collector failure states and unsupported format enumeration), and AC-06 ($\ge 80\%$ precision and recall on the supported-source corpus).

---

## 2. Implemented Components

1. **`backend/app/coverage/models.py`**:
   - `SurfaceCategory`: Categories for `SOURCE_CODE`, `PACKAGE_MANIFEST`, `CONFIGURATION`, `CERTIFICATE_STORE`, and `UNSUPPORTED_SURFACE`.
   - `SurfaceCoverage`: Tracks total files, assessed files, findings count, clean files, unsupported files, and coverage percentages per surface.
   - `CoverageReport`: Comprehensive audit report with overall coverage percentage, partial scan flags, unsupported extension list, and collector health.
   - `GroundTruthLabel`, `BenchmarkMetric`, `BenchmarkEvaluation`: Data models for precision, recall, and F1 evaluation.

2. **`backend/app/coverage/accounting.py`**:
   - `CoverageAccountant`:
     - Accurately computes the assessed denominator ($N_{\text{assessed}} / N_{\text{total}}$).
     - Identifies unassessed and unsupported extensions (e.g. `.png`, `.pdf`, `.bin`).
     - Detects collector errors and marks `is_partial_scan = True` with status `PARTIAL_SCAN_COLLECTOR_DEGRADED`.
     - Explicitly labels clean scans as `NO_FINDINGS_IN_SUPPORTED_SCOPE` with visible coverage caveats, preventing any false "Quantum Safe" claim.

3. **`backend/app/coverage/benchmark.py`**:
   - `BenchmarkRunner`:
     - Compares detected observations against pre-registered ground-truth labels.
     - Tallies True Positives, False Positives, False Negatives.
     - Computes Precision, Recall, and F1-score across algorithm classes.
     - Formally evaluates compliance with AC-06 ($\ge 0.80$ threshold).

---

## 3. Phase Validation & Test Results
Executed 25 total tests via pytest (4 new MVP-03 tests + 21 MVP-01/MVP-02 regression tests):

| Test Case | Scenario Tested | Result |
|---|---|---|
| `test_coverage_accountant_surface_breakdown` | Full multi-surface denominator accounting and extension tracking | **PASSED** |
| `test_no_finding_is_never_labeled_safe` | Clean repositories marked `NO_FINDINGS_IN_SUPPORTED_SCOPE` | **PASSED** |
| `test_partial_scan_on_detector_failure` | Collector errors flagged as `PARTIAL_SCAN_COLLECTOR_DEGRADED` | **PASSED** |
| `test_benchmark_runner_seeded_corpus_target` | AC-06 benchmark evaluation achieving $\ge 80\%$ precision & recall | **PASSED** |
| *Discovery MVP-02 Tests (8 cases)* | Source AST/regex, manifests, configs, certs, secret redaction | **PASSED** |
| *Intake MVP-01 Tests (13 cases)* | Zip bomb, path traversal, symlink defense, limits, sandbox | **PASSED** |

**Summary**: 25/25 tests passed (100% pass rate).

---

## 4. Worker 01 MVP Completion Summary
Worker 01 has completed all 3 assigned MVP phases:
- **MVP-01**: Safe upload intake and scan boundary (13 tests)
- **MVP-02**: Supported source, manifest, config and certificate discovery (8 tests)
- **MVP-03**: Coverage accounting, partial scans and benchmark readiness (4 tests)

All deliverables and contracts are ready for consumption by **Worker 02 (Canonical Evidence & Inventory)**, **Worker 03 (Risk & Migration Queue)**, and **Worker 04 (Workflow & Web UI)**.
