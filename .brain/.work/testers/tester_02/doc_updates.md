# Tester 02 documentation review/update plan

| Cycle | Documentation to inspect/update | Source of truth | Signoff evidence |
|---|---|---|---|
| V01 — Contract integration, export, hostile input and privacy review | Supported scope, limitations, coverage/uncertainty labels, test protocol/results, defect taxonomy and report/export guide | Acceptance criteria + interface contract + actual versioned test evidence when available | Reviewer, date, version, changed sections, unresolved wording risks |
| V02 — Regression, documentation, demo and release-readiness review | Supported scope, limitations, coverage/uncertainty labels, test protocol/results, defect taxonomy and report/export guide | Acceptance criteria + interface contract + actual versioned test evidence when available | Reviewer, date, version, changed sections, unresolved wording risks |


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
