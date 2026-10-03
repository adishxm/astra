# Workstream assignment and ownership

| Role | Accountable scope | Owns planning artifacts | Must coordinate with | Explicitly does not own |
|---|---|---|---|---|
| Worker 01 | Safe upload intake and supported deterministic discovery/coverage | `webapp/worker_01/**`; detector and format coverage contract | W02 finding schema, W04 scan UX, Tester 01 ground truth | Risk weights, UI integration, arbitrary network scanning |
| Worker 02 | Canonical evidence, identity, relationships, export | `webapp/worker_02/**`; data dictionary and CBOM projection | W01 observations, W03 risk inputs, W04 evidence/report UI | Creating detections or claiming a complete enterprise graph |
| Worker 03 | Contextual risk and advisory migration planning | `webapp/worker_03/**`; versioned factors and decision rationale | W02 relationships, W04 scenario UX, Tester 01/02 | Cryptographic algorithm certification or automatic remediation |
| Worker 04 | Web workflow, integration, synthetic demo, docs, coordination | `webapp/worker_04/**`, `.demo/` plan, shared doc updates | All workers; both testers; project owner | Building source code in this planning task or inventing test results |
| Tester 01 | Functional correctness and deep E2E validation design | `testers/tester_01/**` | W01/W02/W03 defect owners | Executing an application that does not exist |
| Tester 02 | Integration, regression, security/privacy, documentation, release design | `testers/tester_02/**` | All workers, especially W04 docs/integration | Approving unresolved security/authority blockers on behalf of owner |

## Parallel planning order
W01/W02 initial contract drafts and W03 factor inventory may be drafted in parallel. W02 publishes the canonical observation contract before worker MVP phase files are frozen. W04 defines screens/state transitions after data and risk payloads are stable. Tester plans start from draft contracts, then reconcile after W04 integration. Production work is gated by the MVP merge plan. Each owner uses unique phase/report filenames; shared schema changes require a decision-log entry and affected-worker retest mapping.

## Scope-sized phase allocation and MVP completeness
Worker phase count follows distinct outputs and dependency gates: Worker 01 has 3 MVP phases, Worker 02 has 2, Worker 03 has 3, and Worker 04 has 3. Production phase counts are likewise role-specific. This is intentional; matching phase counts are not a requirement. Each worker's `phase_index.md` is authoritative. The MVP merge is a complete-product gate: all MVP work assigned to all four workers must be delivered, integrated, validated and documented within the confirmed boundary. No core feature may be deferred, stubbed or called “MVP” while incomplete. Production phases can add optional capabilities only after that gate.
