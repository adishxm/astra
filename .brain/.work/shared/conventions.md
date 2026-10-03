# Planning, evidence, and documentation conventions

- Names: `worker_01`–`worker_04`, `tester_01`–`tester_02`; phase IDs `MVP-01`, `MVP-02`, `PROD-01`, etc.; tester IDs `V01`, `V02`; report filenames exactly match owner and phase/cycle.
- Status vocabulary: `PLANNED`, `BLOCKED`, `READY_FOR_REVIEW`, `PLANNING_SIGNED_OFF`; never use `IMPLEMENTED`, `PASSED`, or `RELEASED` for this planning-only run.
- Evidence words: **observed** = collector saw it; **inferred** = rule derives a claim; **declared** = source/vendor/user says so; **verified** = an explicit validation step tested it; **unknown** = insufficient evidence; **unsupported/not assessed** = surface was not evaluated; **conflicting** = observations disagree. These labels are not interchangeable.
- Every algorithm-status or PQC mapping needs source, version/date and owner review. Drafts/preprints/vendor claims are labelled. No score is presented without assumptions and factor rationale.
- Every report names the exact phase/cycle, owner, objective, planned scope, planned files, validation, expected result (future), blockers, dependencies, next action, traceability and gate.
- Future app file paths shown in worker plans are planning references only and were not created. Keep app implementation in a later authorized execution.
- Uploaded archive evidence is sensitive by default: relative paths and sanitized excerpts only; no private keys/tokens; no external AI by default.
