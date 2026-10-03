# Worker 03 handoff plan

## Phase-specific planned work
- **MVP-01 — Context fields and transparent risk model** (MVP): Define required/optional context (purpose, data sensitivity/lifetime, exposure, criticality, migration duration, dependency reach), versioned formula/factor semantics, missing-data behavior and separate confidence vs urgency. Completion evidence: Risk can be recomputed and explained from recorded inputs; quantum horizon remains configurable assumption, not prediction. Trace: R01,R02,R03,R05,R06.
- **MVP-02 — Candidate mapping and actionable migration backlog** (MVP): Plan advisory work items tied to evidence/asset/context with priority, reason codes, dated algorithm-status source, candidate standardized/hybrid path, compatibility gaps, review owner and next action. Completion evidence: Each top priority is actionable and traceable without automatic changes or unsupported compatibility guarantees. Trace: R02,R03,R04,R05,R08.
- **MVP-03 — Scenario sensitivity and end-to-end decision behavior** (MVP): Specify assumption controls and reproducible decision explanations; validate how lifetime, migration duration, criticality and exposure affect ordering under transparent rules; define flat-severity baseline and reviewer-agreement evaluation. Completion evidence: An analyst can understand why priority changes and inspect every influential assumption; no opaque or unmeasured claim. Trace: R01,R02,R03,R05,R06,R10.
- **PROD-01 — Dependency-aware constrained migration roadmap** (production): Plan graph-aware ordering over centrality, hardware/vendor, latency/cost, operations windows, data priority and dependencies; compare against flat rankings and expose objective/trade-offs. Completion evidence: Evidence plan for whether constraints improve reviewer agreement/roadmap usefulness; remains advisory. Trace: R02,R03,R04,R06,R08.
- **PROD-02 — Security-property, trust and rollback assurance** (production): Design verification plans for authentication, confidentiality, downgrade, trust-chain and policy invariants across candidate transitions, including negative/failure and cryptographic rollback cases. Completion evidence: Reviewed invariant catalog and feasible test-oracle plan; never claim proof absent formal model/evidence. Trace: R02,R03,R04,R08,R09.

## Completion rule
All 3 MVP phases for this worker and every upstream dependency must be accepted before this worker hands off to the MVP merge. A core deliverable cannot be marked “future” or deferred to production.

## Still pending
No source code, implementation, metrics, or tests exist in this planning run. Resolve owner blockers; execute and document them only during an authorized implementation stage.

## Dependencies / blockers
See each phase and `.work/shared/blocker_log.md`. Production work starts only after `merging_phase_mvp.md`.

## Validation / expected result
Tester cycles must cover this worker's acceptance IDs and retest any fix. Expected result is a coherent plan; it is not an observed runtime result.

## Report paths
- `../../.report/worker_03_mvp_01_report.md` — Context fields and transparent risk model.
- `../../.report/worker_03_mvp_02_report.md` — Candidate mapping and actionable migration backlog.
- `../../.report/worker_03_mvp_03_report.md` — Scenario sensitivity and end-to-end decision behavior.
- `../../.report/worker_03_prod_01_report.md` — Dependency-aware constrained migration roadmap.
- `../../.report/worker_03_prod_02_report.md` — Security-property, trust and rollback assurance.

## Docs, merge notes and recommendation
Update `phase_index.md`, `status.md`, shared traceability, contracts, acceptance and test matrix after any scope change. Keep one report per phase. Recommendation: complete all in-scope MVP phases and close all MVP defects before merge; then consider optional production phases.
