# Worker 02 handoff plan

## Phase-specific planned work
- **MVP-01 — Canonical evidence, identity and redaction model** (MVP): Define claims, observations, assets, stable IDs, provenance, confidence rationale, timestamp/freshness, scope, rule/source version, redaction and conflict states; specify duplicate resolution without discarding raw observations. Completion evidence: Every future finding has traceable, sanitized provenance and remains distinguishable from declarations/inferences/unknowns. Trace: R02,R03,R04,R05,R06.
- **MVP-02 — Context graph, review audit and CBOM-style export** (MVP): Plan bounded relationships between findings, component/repository, certificate/config, application/system, owner/context; support auditable user review and scan diffs; map an internal model to a selected, versioned CBOM profile plus safe report/CSV exports. Completion evidence: A useful full inventory/review/export loop is planned, with no claim of conformance until schema validation succeeds. Trace: R02,R03,R05,R06,R07,R11.
- **PROD-01 — Temporal identity, change history and evidence reconciliation** (production): Extend accepted MVP records into inventory snapshots, freshness, drift/causality and crypto-to-data/system lineage; measure false merges/splits and retain reversible decisions. Completion evidence: Versioned temporal model proposal with identity stability evidence plan. Trace: R02,R03,R04,R06,R09.
- **PROD-02 — CBOM conformance and multi-generator reconciliation** (production): Validate mapping against selected current schema; compare multiple generators on identical fixtures, retain mapping gaps and source provenance. Completion evidence: Validator-backed conformance claim only if validator passes; reproducible discrepancy report design. Trace: R05,R06,R07,R11.

## Completion rule
All 2 MVP phases for this worker and every upstream dependency must be accepted before this worker hands off to the MVP merge. A core deliverable cannot be marked “future” or deferred to production.

## Still pending
No source code, implementation, metrics, or tests exist in this planning run. Resolve owner blockers; execute and document them only during an authorized implementation stage.

## Dependencies / blockers
See each phase and `.work/shared/blocker_log.md`. Production work starts only after `merging_phase_mvp.md`.

## Validation / expected result
Tester cycles must cover this worker's acceptance IDs and retest any fix. Expected result is a coherent plan; it is not an observed runtime result.

## Report paths
- `../../.report/worker_02_mvp_01_report.md` — Canonical evidence, identity and redaction model.
- `../../.report/worker_02_mvp_02_report.md` — Context graph, review audit and CBOM-style export.
- `../../.report/worker_02_prod_01_report.md` — Temporal identity, change history and evidence reconciliation.
- `../../.report/worker_02_prod_02_report.md` — CBOM conformance and multi-generator reconciliation.

## Docs, merge notes and recommendation
Update `phase_index.md`, `status.md`, shared traceability, contracts, acceptance and test matrix after any scope change. Keep one report per phase. Recommendation: complete all in-scope MVP phases and close all MVP defects before merge; then consider optional production phases.
