# Tester 01 documentation review/update plan

| Cycle | Documentation to inspect/update | Source of truth | Signoff evidence | Status |
|---|---|---|---|---|
| V01 — Discovery, ground truth, evidence and coverage | Supported scope, limitations, coverage/uncertainty labels, test protocol/results, defect taxonomy and report/export guide | Acceptance criteria (AC-01–AC-06, AC-11) + interface contract + actual executed test suite (`test_v01_functional_assurance.py`) | Tester 01, 2026-10-03, v0.1.0, 30 tests in scope passed, verified zero secret leakage and truthful denominator labeling | **REVIEW COMPLETE & VERIFIED** |
| V02 — Risk, migration queue and user journey E2E | Supported scope, limitations, coverage/uncertainty labels, test protocol/results, defect taxonomy and report/export guide | Acceptance criteria (AC-07–AC-10, AC-12, AC-15–AC-18) + interface contract + actual executed test suite (`test_v02_e2e_journey.py`) | Tester 01, 2026-10-03, v0.1.0, 20 tests in scope passed, verified Mosca horizon logic, backlog priority and CBOM export | **REVIEW COMPLETE & VERIFIED** |



Never write successful detection, schema conformity, production security, or performance claims until corresponding evidence exists. Label synthetic data and sample exports. Document policy defaults, dates and update owner.

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
