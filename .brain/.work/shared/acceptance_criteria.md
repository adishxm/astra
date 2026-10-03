# Acceptance criteria and quality gates

All criteria below are **future implementation acceptance targets**; this planning package does not claim they have passed.

| ID | Acceptance criterion | Owner(s) | Planned evidence |
|---|---|---|---|
| AC-01 | Exact supported input classes, languages, exclusions, size/count/time limits and assessment denominator are documented and visible before scan. | W01/W04 | format matrix; rejected/unsupported fixture tests |
| AC-02 | Archive handling rejects traversal, symlink escape, malformed archives, excessive expansion and prohibited file types; no uploaded code is executed. | W01/W04 | adversarial fixture plan; audit/error mapping |
| AC-03 | Each observation retains detector/rule version, timestamp, repository-relative evidence anchor/hash, scope and sanitized claim; private-key data is never included. | W01/W02 | schema contract and secret-redaction test plan |
| AC-04 | Evidence states distinguish observed/inferred/declared/verified/conflicting/unknown/unsupported/failed; absence of a finding never equals “safe.” | W01/W02/W04 | state-transition and negative-coverage cases |
| AC-05 | Deduplication is provenance-preserving; conflict/uncertain identity does not discard raw observations. | W02 | duplicate and contradiction fixture plan |
| AC-06 | Seeded corpus target from source research: ≥80% precision and ≥80% recall for supported source findings; report per-class counts/limits and no generalized accuracy claim. | W01/Tester 01 | ground-truth protocol and baseline report mapping |
| AC-07 | Risk is deterministic/versioned and displays factors, assumption horizon, sensitivity, missing values, and uncertainty separate from urgency. | W03 | controlled scenario and weight-boundary tests |
| AC-08 | Migration queue is advisory; candidate mappings cite a dated source and expose compatibility/operational gaps; no automatic remediation. | W03/W04 | mapping review plan; stale/unknown mapping test |
| AC-09 | Export has declared profile/version and is validated before being called conformant; secrets are excluded; provenance and scope survive export. | W02 | schema-validator, round-trip and redaction test plans |
| AC-10 | UI supports evidence drill-down, coverage/unknown review, user context and auditable correction/override. | W04/W02 | end-to-end workflow and audit replay plan |
| AC-11 | Partial/failed scans remain clearly partial; collector errors and unsupported formats are visible. | W01/W04 | timeout/parser-failure tests |
| AC-12 | Demo uses labeled synthetic/open fixtures, works without production access or external AI, and reports measured outcomes only after actual tests. | W04/Tester 02 | demo rehearsal and claim review |
| AC-13 | Security, privacy, retention, role access and threat-model requirements are documented before any sensitive source is processed. | W04/Tester 02 | threat-model review, privacy checklist and signoff |
| AC-14 | Research traceability links every archive source/topic to a plan, decision, explicit exclusion, test, report or merge gate. | All/Tester 02 | `traceability_matrix.md` audit |


## MVP complete-product acceptance (new gate)
| ID | Acceptance criterion | Owner(s) | Planned evidence |
|---|---|---|---|
| AC-15 | The MVP is usable end-to-end within its confirmed scope: authorized upload → scan status/result → evidence and coverage inspection → context enrichment → explainable priority → review → sanitized export/report. No required step is a placeholder or disconnected module. | W01–W04 | full synthetic E2E acceptance workflow and integration review |
| AC-16 | Every in-scope MVP capability has an owner, implementation plan, acceptance evidence and tester coverage; there are no unfinished MVP TODOs/stubs or core features moved to production. | All workers / both testers | phase-to-capability closure matrix at MVP merge |
| AC-17 | Any capability excluded from MVP is explicitly outside the agreed product boundary and not required for the promised MVP; if official SIH requirements make it mandatory, scope is re-opened and MVP phases/tests are added before approval. | Project owner / W04 | official-scope reconciliation and signed boundary |
| AC-18 | MVP completion is based on integrated product behavior, not completion of planning files alone; every blocking defect and critical dependency is resolved or the gate remains open. | Both testers / project owner | integrated run evidence, defect closure, documented signoff |


## Gate semantics
A planning gate can approve completeness and coherence of a plan only. **Actual MVP completion additionally requires an implemented, integrated and validated end-to-end product within the confirmed scope**; complete phase plans alone are not product completion. Implementation readiness additionally requires owner decisions and future evidence. A merge gate cannot waive a security/authorization blocker, defer an in-scope core feature, or convert an unknown into a pass.
