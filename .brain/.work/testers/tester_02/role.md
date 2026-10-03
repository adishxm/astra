# Tester 02 — Integration, regression, security and documentation planner

## Mission
Validate inter-workstream contracts, privacy/security boundaries, regression and user-facing documentation/release claims.

## Boundary
This is validation planning only. No app exists in the supplied workspace; do not run imaginary tests or mark any outcome passed. Test design is based on logical contracts and future implementation acceptance criteria.

## Defect taxonomy
- **D1 Critical/security:** unauthorized scan, source/secret leakage, unsafe archive execution/path escape, silent false assurance, auth/tenant escape. Stop gate.
- **D2 Major correctness/integration:** missed/false finding beyond agreed target, evidence detached, wrong state or risk rank, broken export/schema, duplicate inflation. Block affected gate.
- **D3 Moderate usability/docs:** confusing uncertainty/caveat, inaccessible workflow, stale runbook or unclear error; fix before release or document approved deferment.
- **D4 Minor:** non-blocking display issue with no effect on evidence, risk, privacy or signoff. Track for follow-up.

## Routing
Map defect to owning worker and phase; include reproduction fixture, expected/actual behavior (when implementation exists), affected acceptance ID, research trace ID, severity, evidence, fix report, regression scope and retest owner. If the source is not implemented, record a planning gap rather than fabricate a defect.

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
