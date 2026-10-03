# Tester 02 validation plan

**Owner:** Integration, regression, security and documentation planner. **Status:** PLANNED; no tests run. **Workstream owners:** all four workers.

## V01 — Contract integration, export, hostile input and privacy review

### Validation objective
Cross-check scan-job states, observation schema, evidence graph, risk rationale, UI and export; map incompatible/partial states; inspect sanitizer, audit, RBAC, retention assumptions and hostile archive plan.

### Coverage areas
- contract compatibility table
- schema/profile validator and export round-trip cases
- secret/private-key redaction tests
- path traversal/decompression/symlink/time/size abuse cases
- auth/tenant/audit/retention and no-external-AI review plan
- defect routing and retest triggers

### Acceptance / traceability
all W01–W04 MVP phases; AC-01–AC-05, AC-09, AC-11, AC-13–AC-14; trace R01–R07/R10/R12.

### Defect and retest route
Owning worker by component; W04 coordinates integration. Route all findings through the taxonomy in `role.md`; every material correction reopens targeted regression and updates the cycle report and `validation_log.md`.

### Documentation updates
Update the benchmark protocol, supported-format/coverage statement, limitation copy, test matrix, defect log, and user-facing explanation affected by results. Preserve measured data and test environment when actual execution begins.

### Signoff criteria
All planned cases executed later against a versioned build; critical/security and major defects closed or explicitly owner-accepted with mitigation; target metrics reported by scope; unsupported coverage visible; evidence and export integrity verified; documentation and traceability updated; no false claims; report reviewed by owner.

## V02 — Regression, documentation, demo and release-readiness review

### Validation objective
Review corrected MVP plans, synthetic demo runbook, limitations/coverage language, threat model and planned offline deployment; regression across rule/schema versions and production gate readiness.

### Coverage areas
- regression suite plan by artifact/rule/schema version
- doc review for user/admin/developer/limitations/report
- demo rehearsal with synthetic data and failure fallback
- release/rollback/security signoff criteria
- production authorization and evidence checklist

### Acceptance / traceability
all W01–W04 MVP phases; production entry criteria; AC-06–AC-18; trace all major R groups and all archive source rows.

### Defect and retest route
W04 documentation; W01/W02/W03 component defects; project security owner for signoff. Route all findings through the taxonomy in `role.md`; every material correction reopens targeted regression and updates the cycle report and `validation_log.md`.

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
