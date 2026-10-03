# Tester 01 validation plan

**Owner:** Functional assurance planner. **Status:** PLANNED; no tests run. **Workstream owners:** worker_01/worker_02/worker_03.

## V01 — Discovery, ground truth, evidence and coverage

### Validation objective
Ground-truth seeded repositories; source/API and dependency/config/certificate fixtures; regex baseline vs planned richer detector; evidence path/line/hash; duplicates/conflicts; unsupported and corrupt inputs; archive safety; partial collector behavior.

### Coverage areas
- fixture inventory and labels
- precision/recall/F1 calculation plan by supported class
- false positive/negative adjudication procedure
- unknown/unsupported/failed coverage cases
- hostile archive/path/expansion/secret-redaction cases

### Acceptance / traceability
W01 MVP-01/02/03 and W02 MVP-01/02; AC-01–AC-06, AC-11; trace R01–R06/R10/R12.

### Defect and retest route
W01 for intake/detection; W02 for identity/provenance; W04 for visibility. Route all findings through the taxonomy in `role.md`; every material correction reopens targeted regression and updates the cycle report and `validation_log.md`.

### Documentation updates
Update the benchmark protocol, supported-format/coverage statement, limitation copy, test matrix, defect log, and user-facing explanation affected by results. Preserve measured data and test environment when actual execution begins.

### Signoff criteria
All planned cases executed later against a versioned build; critical/security and major defects closed or explicitly owner-accepted with mitigation; target metrics reported by scope; unsupported coverage visible; evidence and export integrity verified; documentation and traceability updated; no false claims; report reviewed by owner.

## V02 — Risk, migration queue and user journey E2E

### Validation objective
End-to-end synthetic scan through evidence review, context entry, risk explanation, scenario changes, queue, candidate migration caveats, report and export; vary data lifetime, horizon, criticality, exposure and migration duration.

### Coverage areas
- determinism and rule-version plan
- sensitivity/monotonicity cases where model intends it
- missing-context and stale evidence cases
- unsupported recommendation and unknown algorithm cases
- baseline flat severity comparison and reviewer agreement design

### Acceptance / traceability
W03 MVP-01/02/03 and W04 MVP-01/02/03; AC-07–AC-10, AC-12, AC-15–AC-18; trace R01–R08/R12/R14.

### Defect and retest route
W03 for model/mapping; W02 for graph/export; W04 for workflow/doc. Route all findings through the taxonomy in `role.md`; every material correction reopens targeted regression and updates the cycle report and `validation_log.md`.

### Documentation updates
Update the benchmark protocol, supported-format/coverage statement, limitation copy, test matrix, defect log, and user-facing explanation affected by results. Preserve measured data and test environment when actual execution begins.

### Signoff criteria
All planned cases executed later against a versioned build; critical/security and major defects closed or explicitly owner-accepted with mitigation; target metrics reported by scope; unsupported coverage visible; evidence and export integrity verified; documentation and traceability updated; no false claims; report reviewed by owner.

## Complete-product gate coverage
Tester signoff must cover the single integrated end-to-end MVP journey, not only module-level test plans: authorized upload, scan completion/partial explanation, evidence/coverage inspection, context entry, risk rationale, reviewer action, export and documentation. A required step that is missing, mocked, disconnected, or deferred to production is a blocking MVP defect. If official scope expands, add test cases and report mappings before approval.

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
