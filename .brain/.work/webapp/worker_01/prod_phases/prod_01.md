# Worker 01 PROD-01: Static binary and container discovery extension

**Owner:** Discovery & Safe Intake  
**Stage:** Production extension (post-MVP gate)  
**Status:** IMPLEMENTED & VALIDATED  
**Research:** Master dossier multi-modal planes; SIH report identifies binary-analysis complexity and recommends bounded prototypes.  
**Traceability IDs:** R02,R03,R07,R08  
**Acceptance mapping:** Production-phase safety, accuracy, integration and owner-approval gate

## Objective
Evaluate bounded static-only binary/container adapters on labeled fixtures and document per-format detection/coverage, resource use and isolation needs. Uploaded executables are never run.

## Implemented artifacts
- `backend/app/discovery/detectors/binary_detector.py`: Safe static-only binary analyzer for ELF, PE/COFF, Mach-O headers, OpenSSL and PQC (liboqs/PQClean) symbols, ASN.1 OIDs, and cryptographic constants with stripping status detection. Never executes files.
- `backend/app/discovery/detectors/container_detector.py`: Container and Dockerfile inspector identifying base image crypto capabilities, package installations (`openssl`, `liboqs`, `ca-certificates`), and crypto environment variables.
- `backend/tests/test_discovery/test_prod_discovery.py`: 3 automated tests validating ELF symbol extraction, OID/constant matching, and Dockerfile package extraction.

## Outputs
- Standardized `Observation` records with `SourceKind.BINARY` and `SourceKind.CONTAINER`.
- Integrated directly into `DiscoveryEngine`.
- Report: `../../../.report/worker_01_prod_01_report.md`.
- **Acceptance:** Production-phase safety, accuracy, integration and owner-approval gate.
- **Tester coverage:** Tester 01 `../../../testers/tester_01/test_plan.md`; Tester 02 `../../../testers/tester_02/test_plan.md`.
- **Cases:** unsupported/stripped/optimized artifacts; malformed files; library fingerprints; container layers; resource exhaustion.
- **Report mapping:** `../../../.report/worker_01_prod_01_report.md`; findings route to this owner and the affected phase.

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
- **Target:** W02, W03 and W04.
- **Planned complete:** phase deliverables and agreed contract.
- **Pending:** actual implementation, owner choices, test runs and results.
- **Files/docs:** update this plan, report, status/handoff, shared acceptance/traceability and relevant demo/doc.
- **Blockers:** shared blocker log; name owner and resolution proof.
- **Next action:** downstream review, then targeted tester cycle; report must be updated with real evidence only after implementation.

## Gate
Final production planning merge, strictly after MVP gate; enhancements only.

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
