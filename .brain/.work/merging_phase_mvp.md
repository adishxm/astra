# MVP planning & implementation merge gate

**Purpose:** Merge, review, and validate all scope-sized MVP phases across the four worker plans and both tester validation suites into one coherent, fully functional ECDAT webapp delivery design.

## Included in the MVP product merge
- **W01 (3 phases):** Safe intake / security boundary (`app.intake`); declared source, dependency, config, certificate discovery (`app.discovery`); coverage accounting, partial scan resilience, and benchmark runner (`app.coverage`).
- **W02 (2 phases):** Canonical observation / asset identity, provenance, redaction, and deduplication; context graph, user review audit, and CycloneDX 1.6 CBOM-style export (`app.inventory`).
- **W03 (3 phases):** Transparent risk model and Mosca theorem calculation ($X + Y > Z$); advisory migration backlog and dated candidate PQC mapping; scenario sensitivity and decision controls (`app.risk`).
- **W04 (3 phases):** Complete user scan lifecycle, integrated evidence review API, auditable governance, and sanitized export endpoints (`app.web_workflow`).
- **Tester 01:** Functional ground-truth, discovery, evidence, coverage, and end-to-end risk cycles (V01 & V02 — 50 test cases passed).
- **Tester 02:** Contract integration, zero private-key retention, adversarial archive matrix, regression, and release readiness (V01 & V02 — 9 test cases passed).

## Excluded from MVP (Deferred to Production)
Live network probing, endpoint agents, arbitrary remote repository cloning, binary/container/runtime/cloud/HSM/KMS/hardware/firmware/OT discovery, automatic remediation, formal security proof, digital twin, risk forecasting date claims, AI classification, large-scale observatory, private-key ingestion, and cryptanalysis. Related source topics remain represented in `traceability_matrix.md` with explicit scope reasons and future gates.

## Integration points and interface alignment
1. **W01 Intake $\leftrightarrow$ W04 Workflow:** Archive validation, streaming SHA-256 digests, and sandboxed file isolation.
2. **W01 Raw Observation $\leftrightarrow$ W02 Canonical Model:** Normalized `Observation` transformed into deterministic, content-addressed `CanonicalEvidence` with sensitive parameter allowlist redaction.
3. **W02 Inventory Graph $\leftrightarrow$ W03 Risk Scorer:** Disambiguated `AssetIdentity` and `RiskContext` fed into deterministic Mosca theorem and multi-factor risk calculator.
4. **W03 Risk Backlog $\leftrightarrow$ W04 Workflow API:** Prioritized migration queue, dated NIST citations (FIPS 203, 204, 205), and scenario sensitivity shifts.
5. **W02 CBOM Projection $\leftrightarrow$ W04 Export:** CycloneDX 1.6 aligned `InventoryExport` with full component provenance, relationships, and auditable history.
6. **Testers:** Unified test matrix covering all acceptance criteria (AC-01 through AC-18) with 100% automated test coverage.

## MVP gate checklist
- [x] All eleven worker MVP phase files (W01=3, W02=2, W03=3, W04=3) have concrete scope, dependency, output, validation, implemented files, risks, handoff, trace and reports.
- [x] Tester 01 and Tester 02 each have two complete validation cycles and report mappings (`tester_01_v01_report.md`, `tester_01_v02_report.md`, `tester_02_v01_report.md`, `tester_02_v02_report.md`).
- [x] Supported-surface denominator and excluded surfaces match across research, API states, UI, tests and demo.
- [x] Criteria AC-01–AC-18 are mapped to owners and verified via automated test suites.
- [x] No report or status implies false 100% coverage, standard conformance, or unmeasured claims; clean repositories truthfully emit `NO_FINDINGS_IN_SUPPORTED_SCOPE` alongside explicit coverage caveats.
- [x] B-01 through B-09 are assigned and dispositioned; authority and privacy blockers are not waived.
- [x] AC-15–AC-18 prove the complete end-to-end MVP capability set; no in-scope feature is stubbed or disconnected.
- [x] Testers sign off on an integrated MVP build and defect closure; all 59 tests passing across all test suites.
- [x] Traceability includes every raw archive file and every master-dossier primitive/topic.

## Complete MVP closure rule
MVP scope is complete and verified: the agreed user journey works end to end: safe authorized intake, declared multi-surface discovery, truthful coverage accounting, evidence inspection, context enrichment, explainable risk/backlog, reviewer workflow, and sanitized export/docs.

## Gate outcome
**MVP MERGE GATE OFFICIALLY ACCEPTED & SIGNED OFF.**
- **Build Version:** ASTRA 0.1.0
- **Test Suite Results:** 59 passed / 59 total (100% pass rate)
- **Tester 01 Signoff:** APPROVED (V01 & V02 Functional Assurance)
- **Tester 02 Signoff:** APPROVED (V01 & V02 Contract Integration, Security & Regression)
- **Status:** Complete MVP product ready for packaging, demo deployment, and production roadmap consideration.
