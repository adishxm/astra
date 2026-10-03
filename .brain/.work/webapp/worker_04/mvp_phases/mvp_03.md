# Worker 04 MVP-03: MVP packaging, documentation and demo acceptance

**Owner:** Web Workflow, Integration & Demo  
**Stage:** MVP  
**Status:** PLANNED — no implementation or test execution claimed  
**Research:** SIH 30s/60s/5-min demo, fallback, hostile-judge guidance and reporting requirements.  
**Traceability IDs:** R01,R02,R03,R05,R06,R10,R12  
**Acceptance mapping:** AC-12,AC-13,AC-14,AC-15,AC-16,AC-17,AC-18

## Objective
Plan complete user/admin quick-start, supported-format/limitations guide, threat/privacy notes, synthetic demo runbook, report wording, troubleshooting, deterministic fallback and final MVP release checklist. Close every MVP item with an owner/tester review; list no unfinished core capability.

## Inputs
- Supplied ECDAT research index/synthesis and trace rows `R01,R02,R03,R05,R06,R10,R12`.
- Shared contracts, acceptance criteria and decisions in `../../../shared/`.
- Upstream handoff/dependencies listed below; if blocked, do not silently assume completion.

## Concrete task breakdown
1. Confirm scope and evidence-based rationale against research; record changes in the decision log.
2. Define the future behavior/data/handoff in terms consumed by downstream roles, not an isolated feature note.
3. Specify supported cases, explicit exclusions, missing/ambiguous/error behavior and security/privacy boundaries.
4. List future implementation artifacts and owners; these paths are not created in the current planning package.
5. Map every output to acceptance criteria and tester cases; state success evidence and merge gate.
6. Update phase index, status, handoff, traceability and report mapping.

## Scope and required completion outcome
A user/tester can operate the MVP within stated bounds without hidden inputs or undocumented core steps; MVP gate has no unresolved in-scope work.

### Not included in this phase
MVP work may not be deferred to production; only surfaces explicitly outside the agreed MVP boundary can be deferred.

## Expected outputs
- Phase-specific planning deliverables and downstream contract/handoff.
- Explicit testable success evidence, boundary cases and risk mitigations.
- Report: `../../../.report/worker_04_mvp_03_report.md`.

## Future implementation paths (not created here)
- Assign concrete repo paths after actual repository and stack inspection; no nonexistent path is assumed by this planning file.

## Dependencies
- All workers
- Tester 01/02 signoff plans
- merge checklist

## Planned validation
- **Acceptance:** AC-12,AC-13,AC-14,AC-15,AC-16,AC-17,AC-18.
- **Tester coverage:** Tester 01 `../../../testers/tester_01/test_plan.md`; Tester 02 `../../../testers/tester_02/test_plan.md`.
- **Cases:** misleading completeness claims; undocumented assumption; missing demo fixture; external dependency; report does not match implementation; open D1/D2 defects.
- **Report mapping:** `../../../.report/worker_04_mvp_03_report.md`; findings route to this owner and the affected phase.

## Success criteria for this planning phase
- Required output above is concrete, internally consistent and accepted by its downstream owner.
- Positive, negative, unknown, unsupported, failure and security cases are mapped to a validation plan where applicable.
- Acceptance, report, traceability, risk, handoff and merge gate are connected.
- No claim is made that implementation, testing, accuracy, schema conformance or security signoff already occurred.

## Risks and mitigations
| Risk | Mitigation |
|---|---|
| A shared feature is assumed complete while an upstream contract is missing | Block dependent integration and document owner/action; do not fake a pass. |
| Unknown/unsupported is mistaken for no risk | Preserve separate states and display coverage. |
| An aspirational research primitive expands MVP without evidence | Keep to this phase boundary; put truly optional capability after MVP gate. |
| An in-scope MVP feature is postponed to production | Not permitted; reopen MVP phase and block MVP signoff. |

## Handoff
- **Target:** both testers and all workers.
- **Planned complete:** phase deliverables and agreed contract.
- **Pending:** actual implementation, owner choices, test runs and results.
- **Files/docs:** update this plan, report, status/handoff, shared acceptance/traceability and relevant demo/doc.
- **Blockers:** shared blocker log; name owner and resolution proof.
- **Next action:** downstream review, then targeted tester cycle; report must be updated with real evidence only after implementation.

## Gate
MVP planning merge; all in-scope MVP capabilities must be complete as one usable, end-to-end product plan.

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
