# Planning report — worker_01 MVP-01: Safe upload intake and scan boundary

- **Prepared:** 2026-10-03, revised planning design
- **Owner:** Discovery & Safe Intake
- **Status:** PLANNED; no implementation or tests have been executed.
- **Research:** Research on sensitive code and hostile inputs; SIH feasibility report §§9–10.
- **Traceability:** R01,R02,R05,R10,R12
- **Acceptance:** AC-01,AC-02,AC-11,AC-13

## Objective
Define the authorized local archive/repository intake, file and resource limits, path normalization, symlink policy, archive-bomb defenses, scan identity and read-only handling. Specify rejection and partial-result behavior.

## Planned work and completion evidence
File the accepted artifact and create a reproducible scan manifest without executing uploaded content.

## Future files to create/modify
To be assigned after repository inspection; no application path is invented or created in this planning package. See `.work/webapp/worker_01/mvp_phases/mvp_01.md`.

## Planned validation
upload limits; dangerous archive entries; traversal/symlink; malformed archive; canceled/oversized scan; no outbound connection

## Dependencies / handoff
W04 upload/job workflow; W02 scan and evidence IDs. Route findings to worker_01; update the phase plan, report and tester regression mapping.
## Blockers / next step
No results are recorded. Resolve relevant owner decisions and upstream contract dependencies; future execution must append measured evidence and retest records.

## Gate
MVP complete-product merge; no core scope may be deferred.
