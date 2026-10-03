# Tester 01 signoff criteria

**Current state: OFFICIALLY SIGNED — V01 & V02 FUNCTIONAL ASSURANCE COMPLETED.**

## Required before signoff (VERIFIED)
- [x] Each cycle in `test_plan.md` has actual versioned execution evidence and complete coverage denominator.
- [x] Critical and major defects are closed and retested; zero blocking defects identified across 50 test cases.
- [x] Results are reported by artifact class, including unsupported/failed cases, and no result is generalized beyond test corpus.
- [x] Evidence provenance, unknown/partial states, redaction, risk rationale, schema/profile validation, audit events and synthetic demo path meet acceptance criteria.
- [x] Documentation and traceability reflect actual behavior; zero false claims of "Safe" or production certification.

## Approval record
- **Cycle(s):** V01 (Discovery, Ground Truth, Evidence, Coverage) & V02 (Risk, Migration Queue, E2E Journey)
- **Build / rule / schema version:** ASTRA 0.1.0 / Ruleset `2026.10-nist-pqc` / Collector `0.1.0` / Schema draft `1.0.0`
- **Evidence/report path:** `.brain/.work/.report/tester_01_v01_report.md` & `.brain/.work/.report/tester_01_v02_report.md` (synced to `.brain/.report/`)
- **Open defects and owner acceptance:** 0 open defects. All 50 pytest test cases pass across Windows and Linux.
- **Tester / date:** Tester 01 (Functional Assurance Planner & Tester) / 2026-10-03
- **Signoff verdict:** **APPROVED & FULLY SIGNED OFF FOR MVP FUNCTIONAL SCOPE**


## TESTING + PUSH WORKFLOW

WORKER RESPONSIBILITY:

- After each phase, the worker must perform phase-specific validation.
- This validation should be limited to the scope of that phase, such as:
  - smoke tests
  - unit tests
  - feature checks
  - interface checks
  - basic sanity verification
- If validation fails, the worker must fix the issue before proceeding.
- After validation passes, the worker must:
  1. update relevant documentation
  2. commit changes to git
  3. push changes to the remote repository
- The worker must record the test result, commit hash, and push status in the handoff file.

TESTER RESPONSIBILITY:

- Testers are responsible for deep and broad validation of the work produced by workers.
- Tester testing must be much more exhaustive than worker testing.
- Testers should perform:
  - integration testing
  - regression testing
  - end-to-end testing where applicable
  - edge-case testing
  - cross-module dependency checks
  - documentation verification
  - release-readiness validation
- Testers should identify defects, missing logic, incomplete behavior, and mismatched documentation.
- Testers must log findings clearly and request fixes from the relevant worker when needed.
- Testers may update validation documents, test reports, and signoff files, and push those documentation/test artifacts if required.

PHASE COMPLETION RULE:

- A worker phase is not complete until:
  1. the phase work is implemented
  2. the phase-level tests pass
  3. documentation is updated
  4. code changes are committed
  5. code changes are pushed
- A tester review is not complete until:
  1. comprehensive validation is finished
  2. defects are logged
  3. documentation/test reports are updated
  4. tester signoff status is recorded
