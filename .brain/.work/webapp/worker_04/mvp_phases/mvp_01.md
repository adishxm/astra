# Worker 04 MVP-01: Complete user journey, roles and scan lifecycle

**Owner:** Web Workflow, Integration & Demo  
**Stage:** MVP  
**Status:** PLANNED — no implementation or test execution claimed  
**Research:** SIH reconstructed workflow and feasible architecture; source privacy and coverage research.  
**Traceability IDs:** R01,R02,R03,R05,R10  
**Acceptance mapping:** AC-01,AC-02,AC-04,AC-11,AC-13

## Objective
Specify local-first analyst workflow: scope/authorization notice, upload constraints, job status, rejected/partial/failed/complete states, accessible navigation and explicit no-finding vs unknown messaging. No framework or stack is frozen without a repo.

## Inputs
- Supplied ECDAT research index/synthesis and trace rows `R01,R02,R03,R05,R10`.
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
A user can understand what input is accepted, what the scan does, and whether it finished completely.

### Not included in this phase
MVP work may not be deferred to production; only surfaces explicitly outside the agreed MVP boundary can be deferred.

## Expected outputs
- Phase-specific planning deliverables and downstream contract/handoff.
- Explicit testable success evidence, boundary cases and risk mitigations.
- Report: `../../../.report/worker_04_mvp_01_report.md`.

## Future implementation paths (not created here)
- Assign concrete repo paths after actual repository and stack inspection; no nonexistent path is assumed by this planning file.

## Dependencies
- W01 intake/job contract
- W02 status/evidence states

## Planned validation
- **Acceptance:** AC-01,AC-02,AC-04,AC-11,AC-13.
- **Tester coverage:** Tester 01 `../../../testers/tester_01/test_plan.md`; Tester 02 `../../../testers/tester_02/test_plan.md`.
- **Cases:** wrong/unsupported upload; role denial; cancellation; partial result; long-running scan; accessible errors.
- **Report mapping:** `../../../.report/worker_04_mvp_01_report.md`; findings route to this owner and the affected phase.

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
