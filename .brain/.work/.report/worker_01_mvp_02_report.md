# Planning report — worker_01 MVP-02: Supported source, manifest, config and certificate discovery

- **Prepared:** 2026-10-03, revised planning design
- **Owner:** Discovery & Safe Intake
- **Status:** PLANNED; no implementation or tests have been executed.
- **Research:** SIH report §9 data audit/§10 modular prototype; Cryptoscope, discovery SoK and CBOM research guidance.
- **Traceability:** R01,R02,R05,R06
- **Acceptance:** AC-03,AC-04,AC-06

## Objective
Plan the bounded and explicitly versioned source-language/rule set plus dependency manifests, configuration and certificate fixtures; each detector returns sanitized evidence anchors, rule versions, purpose/algorithm confidence and parse state. Supported languages remain an owner choice.

## Planned work and completion evidence
Each declared supported fixture can produce a structured observation; unsupported surfaces are explicitly identified.

## Future files to create/modify
To be assigned after repository inspection; no application path is invented or created in this planning package. See `.work/webapp/worker_01/mvp_phases/mvp_02.md`.

## Planned validation
positive and negative seed fixtures; ambiguous identifiers; modern and legacy algorithms; line/file evidence; manifest transitive/dependency notes; certificate/config parsing failures

## Dependencies / handoff
W02 canonical observation model; W03 risk input taxonomy. Route findings to worker_01; update the phase plan, report and tester regression mapping.
## Blockers / next step
No results are recorded. Resolve relevant owner decisions and upstream contract dependencies; future execution must append measured evidence and retest records.

## Gate
MVP complete-product merge; no core scope may be deferred.
