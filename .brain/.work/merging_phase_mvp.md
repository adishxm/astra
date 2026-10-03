# MVP planning merge gate

**Purpose:** merge/review all scope-sized MVP phases across the four worker plans and both tester plans into one coherent webapp delivery design. This is a **planning gate**, not code integration or proof of implementation.

## Included in the MVP planning merge
- W01 (3 phases): safe intake/security boundary; declared source/dependency/config/certificate discovery; coverage/partial-result and benchmark plan.
- W02 (2 phases): canonical observation/asset identity, provenance/redaction/conflict/dedupe; context graph, user review/audit and versioned CBOM-style export plan.
- W03 (3 phases): transparent risk model; advisory migration backlog and dated candidate mapping; scenario sensitivity and decision validation plan.
- W04 (3 phases): complete user/scan lifecycle; integrated evidence/context/risk/review/export experience; packaging, documentation, synthetic demo and release acceptance.
- Tester 01 functional ground-truth, discovery, evidence, coverage and E2E risk cycles; Tester 02 integration, privacy/security, regression, docs and release review plans.

## Excluded from MVP
Live network probing, endpoint agents, arbitrary remote repository cloning, binary/container/runtime/cloud/HSM/KMS/hardware/firmware/OT discovery, automatic remediation, formal security proof, digital twin, risk forecasting date claims, AI classification, large-scale observatory, private-key ingestion and cryptanalysis. Related source topics remain represented in `traceability_matrix.md` with scope reason and future decision/test gate.

## Integration points and interface alignment
1. W01 intake job and finding/coverage event contract ↔ W04 job lifecycle and display.
2. W01 raw observation ↔ W02 normalized observation/asset and provenance contract.
3. W02 dependency/context relation ↔ W03 risk inputs and explainability payload.
4. W03 queue/rationale ↔ W04 scenario controls and report.
5. W02 export projection ↔ W04 downloads and Tester 02 schema/round-trip checks.
6. Testers share acceptance IDs, fixture/metric definitions, defect routing and report paths; any contract change reopens scoped tests.

## MVP gate checklist
- [ ] All eleven worker MVP phase files (W01=3, W02=2, W03=3, W04=3) have concrete scope, dependency, output, validation, future files, risks, handoff, trace and report.
- [ ] Tester 01 and Tester 02 each have two complete validation cycles and report mappings.
- [ ] Supported-surface denominator and excluded surfaces match across research, API states, UI, tests and demo.
- [ ] Criteria AC-01–AC-18 are mapped to owners and evidence paths.
- [ ] No report or status implies test execution, application implementation, 100% coverage, standard conformance, or a measured performance result.
- [ ] B-01 through B-09 are assigned and dispositioned; authority/privacy blockers are not waived.
- [ ] AC-15–AC-18 prove the complete end-to-end MVP capability set; no in-scope feature is stubbed, disconnected, or deferred to production.
- [ ] Testers sign off on an integrated MVP build and defect closure in a future execution; planning-only readiness is not product completion.
- [ ] Traceability includes every raw archive file and every master-dossier primitive/topic.

## Remaining production work
Production plans are downstream only: W01 binary/container adapters and separately authorized network evidence; W02 temporal identity/graph and schema/generator reconciliation; W03 constrained roadmap and property/rollback verification; W04 operational/offline/security/release hardening. These are not included in MVP and each requires its own safety/accuracy gate.

## Complete MVP closure rule

MVP scope is considered complete only when the agreed user journey works end to end: safe authorized intake, declared discovery, truthful coverage/partial handling, evidence inspection, context enrichment, explainable risk/backlog, reviewer workflow, and sanitized export/docs. Production phases are optional expansions, not a parking area for incomplete MVP capabilities. If the official SIH requirement makes a deferred surface essential, reopen the scope and add phases, dependencies and tester coverage before the gate.

## Gate outcome at this planning freeze
**PLANNING READY FOR REVIEW — not product-complete and not signed.** Phase plans exist, but no implementation exists and no tester has executed a test. Thus the product MVP is not complete. Critical scope decisions and owner signoff remain open. Next action is official PS verification and repository onboarding, then owner/tester review. See `.work/shared/merge_checklist.md` and status board.
