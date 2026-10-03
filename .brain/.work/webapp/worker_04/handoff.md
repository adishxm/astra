# Worker 04 handoff plan

## Phase-specific planned work
- **MVP-01 — Complete user journey, roles and scan lifecycle** (MVP): Specify local-first analyst workflow: scope/authorization notice, upload constraints, job status, rejected/partial/failed/complete states, accessible navigation and explicit no-finding vs unknown messaging. No framework or stack is frozen without a repo. Completion evidence: A user can understand what input is accepted, what the scan does, and whether it finished completely. Trace: R01,R02,R03,R05,R10.
- **MVP-02 — Integrated evidence review, risk queue and export experience** (MVP): Design linked evidence detail, context enrichment, auditable accept/suppress/correct workflow, risk assumption controls, prioritized backlog and sanitized exports using stable W01–W03 contracts. Completion evidence: End-to-end analyst task is complete: scan → inspect → enrich → prioritize → review → export. Trace: R01,R02,R03,R05,R06,R10.
- **MVP-03 — MVP packaging, documentation and demo acceptance** (MVP): Plan complete user/admin quick-start, supported-format/limitations guide, threat/privacy notes, synthetic demo runbook, report wording, troubleshooting, deterministic fallback and final MVP release checklist. Close every MVP item with an owner/tester review; list no unfinished core capability. Completion evidence: A user/tester can operate the MVP within stated bounds without hidden inputs or undocumented core steps; MVP gate has no unresolved in-scope work. Trace: R01,R02,R03,R05,R06,R10,R12.
- **PROD-01 — Offline operations, security hardening and production release readiness** (production): After MVP, plan self-host/offline profile, RBAC/audit/retention, backup/deletion, observability, rule-update provenance, accessibility and operational release documentation. Completion evidence: Reviewed operational/release plan with independent security owner and resolved deployment decisions. Trace: R01,R02,R03,R04,R05,R10.

## Completion rule
All 3 MVP phases for this worker and every upstream dependency must be accepted before this worker hands off to the MVP merge. A core deliverable cannot be marked “future” or deferred to production.

## Still pending
No source code, implementation, metrics, or tests exist in this planning run. Resolve owner blockers; execute and document them only during an authorized implementation stage.

## Dependencies / blockers
See each phase and `.work/shared/blocker_log.md`. Production work starts only after `merging_phase_mvp.md`.

## Validation / expected result
Tester cycles must cover this worker's acceptance IDs and retest any fix. Expected result is a coherent plan; it is not an observed runtime result.

## Report paths
- `../../.report/worker_04_mvp_01_report.md` — Complete user journey, roles and scan lifecycle.
- `../../.report/worker_04_mvp_02_report.md` — Integrated evidence review, risk queue and export experience.
- `../../.report/worker_04_mvp_03_report.md` — MVP packaging, documentation and demo acceptance.
- `../../.report/worker_04_prod_01_report.md` — Offline operations, security hardening and production release readiness.

## Docs, merge notes and recommendation
Update `phase_index.md`, `status.md`, shared traceability, contracts, acceptance and test matrix after any scope change. Keep one report per phase. Recommendation: complete all in-scope MVP phases and close all MVP defects before merge; then consider optional production phases.
