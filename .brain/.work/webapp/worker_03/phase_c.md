# Worker 03 Phase C: Empirical Benchmark Math Repair: Finding-Level Precision, Unmatched False Positive Accounting & Holdout Integrity

**Document:** `phase_c.md`  
**Worker:** Worker 03 (`.brain/.work/webapp/worker_03`)  
**Target Roadmap Area:** P1 — Repair the "100% precision/recall" benchmark before relying on it  
**Target Readiness Score Impact:** +9 points on Validation and Evidence Quality  
**Status:** SPECIFICATION & ARCHITECTURE PLAN COMPLETE  

---

## 1. Objectives & Executive Scope

Phase C fixes the critical benchmark arithmetic flaws exposed in the Fresh Product Assessment:
1. **Unmatched Findings Must Count as False Positives:**
   - In the prior benchmark math (`test_e2e_corpus_benchmark.py`), on positive files each expected label was checked, but extra detected findings that had no matching ground-truth label were ignored in the false-positive counter.
   - Refactor `compute_metrics` so that every detected finding is checked against expected labels:
     - Any prediction on a positive file that does not match an expected label is penalized as an **FP**.
     - Any prediction on a negative/clean file is penalized as an **FP**.
     - Any expected label not matched by a prediction is an **FN**.
     - Matched expected labels are **TP**.
     - Clean files with 0 predictions are counted as **TN**.
2. **Consistent Denominators & Valid Mathematical Formulas:**
   - Compute standard precision, recall, and $F_1$:
     $$Precision = \frac{TP}{TP + FP}$$
     $$Recall = \frac{TP}{TP + FN}$$
     $$F_1 = 2 \cdot \frac{Precision \cdot Recall}{Precision + Recall}$$
3. **Strict Category & Algorithm Matching:**
   - Enforce exact or normalized canonical algorithm taxonomy matches rather than overly broad substring aliases that could treat a wrong label as a match.
4. **Adversarial Perturbation / False Positive Sensitivity Test:**
   - Provide an automated test demonstrating that injecting a deliberate false detection into the prediction set strictly degrades precision (proving that extra unlabelled detections are no longer hidden).

---

## 2. Technical Deliverables

| Deliverable | File | Target Behavior |
|---|---|---|
| **Benchmark Metric Engine** | `backend/tests/test_e2e_corpus_benchmark.py` | Refactor `compute_metrics` to enforce finding-level TP, FP, FN, and TN with unmatched detection penalties. |
| **Ground Truth Labeling** | `backend/tests/fixtures/corpus/labels.json` | Ensure clean separation of positive vs negative samples and locked holdouts. |
| **Phase C Automated Test Suite** | `backend/tests/test_worker03_phase_c_benchmark.py` | Verify that the repaired benchmark math correctly counts extra detections as FPs, drops precision on noise, and maintains >=80% threshold across in-scope surfaces. |
| **Phase C Completion Report** | `.brain/.work/.report/worker03_phase_c_report.md` | Standardized audit report documenting all implementation details and verification results. |

---

## 3. Test Strategy & Acceptance Gates

- **Test C.1:** Run repaired benchmark on ground truth corpus and confirm finding-level TP, FP, FN math.
- **Test C.2:** Adversarial test: add deliberate dummy detection `["SHA-1"]` to an RSA-only file; verify FP increments and precision drops below 100%.
- **Test C.3:** Verify negative controls yield 0 FPs without mixing file and finding units in the denominator.
- **Test C.4:** Verify all in-scope surfaces satisfy research acceptance bar: $\ge 80\%$ Precision and $\ge 80\%$ Recall.
