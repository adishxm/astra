# Tester 02 validation log (planning status)

No application test has been executed. This log is the structure for future cycles; each row is currently a **planned validation item**, not a result.

| Cycle | Planned area | Planned evidence to record | Result | Defects / owner | Retest |
|---|---|---|---|---|---|
| V01 — Contract integration, export, hostile input and privacy review | Cross-check scan-job states, observation schema, evidence graph, risk rationale, UI and export; map incompatible/partial states; inspect sanitizer, audit, RBAC, retention assumptions and hostile archive plan. | Build/rule/schema version, fixture IDs, commands/environment, counts, metric calculation, coverage and evidence references | NOT RUN | TBD; route per plan | Required after fix |
| V02 — Regression, documentation, demo and release-readiness review | Review corrected MVP plans, synthetic demo runbook, limitations/coverage language, threat model and planned offline deployment; regression across rule/schema versions and production gate readiness. | Build/rule/schema version, fixture IDs, commands/environment, counts, metric calculation, coverage and evidence references | NOT RUN | TBD; route per plan | Required after fix |


When execution begins, append dated entries rather than overwriting history. Record zero-finding results with assessed denominator and coverage; do not convert absence into safety.

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
