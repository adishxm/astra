# Planning report — worker_01 MVP-03: Coverage, partial scans and benchmark readiness

- **Prepared:** 2026-10-03, revised planning design
- **Owner:** Discovery & Safe Intake
- **Status:** PLANNED; no implementation or tests have been executed.
- **Research:** SIH report §§7–9, 12–13; research emphasis on discovery gaps, measured precision/recall and comparator disagreement.
- **Traceability:** R02,R03,R06,R10,R12
- **Acceptance:** AC-04,AC-06,AC-11,AC-12

## Objective
Define per-surface assessed denominators, `NO_FINDING` vs `UNKNOWN/UNSUPPORTED/FAILED`, collector health, provenance-preserving duplicate handoff, ground truth and regex/AST/dependency baselines. Specify the ≥80% precision/recall target only for the agreed seeded supported-source corpus.

## Planned work and completion evidence
User can tell what was assessed, what failed, and what was not assessed; future benchmark results are reproducible by corpus/rule version.

## Future files to create/modify
To be assigned after repository inspection; no application path is invented or created in this planning package. See `.work/webapp/worker_01/mvp_phases/mvp_03.md`.

## Planned validation
empty and mixed repositories; unsupported formats; timeout/partial; duplicates; stale scan; metric denominator; benchmark scope/limitations

## Dependencies / handoff
W02 coverage state and dedup; W04 coverage/error display; Tester 01 V01. Route findings to worker_01; update the phase plan, report and tester regression mapping.
## Blockers / next step
No results are recorded. Resolve relevant owner decisions and upstream contract dependencies; future execution must append measured evidence and retest records.

## Gate
MVP complete-product merge; no core scope may be deferred.
