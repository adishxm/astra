# Planning status board

| Track | Current state | Planning artifacts | Dependencies / next action |
|---|---|---|---|
| Research ingestion | PLANNED COMPLETE (archive indexed; relevance caveats retained) | `.research/research_index.md`, `.research/research_synthesis.md`, archive manifest | Owner verifies official SIH statement and current citations. |
| W01 discovery | PLANNED | role, phase index, 3 MVP + 2 PROD phases, handoff | Confirm languages, formats and file limits. |
| W02 evidence/inventory | PLANNED | role, phase index, 2 MVP + 2 PROD phases, handoff | Select schema/version and agree contracts. |
| W03 risk/migration | PLANNED | role, phase index, 3 MVP + 2 PROD phases, handoff | Owner approves factors, horizon treatment and defaults. |
| W04 web workflow/docs | PLANNED | role, phase index, 3 MVP + 1 PROD phase, demo runbook | Confirm hosting, retention and official constraints. |
| Tester 01 | PLANNED | two validation cycles, log, doc and signoff plan | Build labeled corpus only in later implementation. |
| Tester 02 | PLANNED | two integration/regression/documentation cycles | Threat model and retention owner input required. |
| MVP planning merge | PLANNING READY FOR REVIEW; PRODUCT MVP NOT BUILT | `merging_phase_mvp.md` and checklist | Resolve critical scope blockers before build authorization. |
| Production planning merge | PLANNED | `merging_allphase_prod.md` | Must remain gated behind MVP merge and future evidence. |

**No code has been implemented; no test is passed; no external scan or deployment has occurred.**

## MVP complete-product rule
No MVP phase or feature may be moved to production merely because another worker's phase is complete. The entire agreed end-to-end workflow must be integrated, validated and documented before product MVP signoff. Current state is planning-only; the MVP itself has not been implemented.
