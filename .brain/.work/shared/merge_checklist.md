# Merge and planning-completeness checklist

## MVP planning merge — `merging_phase_mvp.md`
- [ ] Every MVP phase file exists for all four workers and includes objective, inputs, outputs, dependencies, concrete tasks, planned files (not created here), validation, criteria, risk mitigation, handoff, report, trace IDs.
- [ ] W01 surface support matrix and explicit non-assessed classes align to W02 observation states and W04 display.
- [ ] W02 evidence model retains provenance, redaction, uncertainty and conflicts; export is identified as projection pending version validation.
- [ ] W03 risk assumptions and candidate mapping caveats appear in acceptance criteria; no precise quantum forecast or auto-remediation.
- [ ] W04 flow reflects safe upload, partial scans, reviewer audit, synthetic demo and explicit limitations.
- [ ] Tester 01/02 cycle plans cover functional, integration, regression, E2E, edge cases, documentation, defect routing and signoff.
- [ ] Every source file/topic in traceability matrix maps to a plan, decision, assumption, explicit exclusion, test, report or gate.
- [ ] Report mappings exist for every worker MVP phase and tester cycle; they are clearly planned reports, not test results.
- [ ] Open blockers and owner decisions remain visible; none is silently marked resolved.
- [ ] AC-15–AC-18 pass on a real integrated MVP; all user-visible core steps work, no TODO/stub/disconnected feature remains, and nothing in the confirmed MVP boundary is postponed to production.
- [ ] Deferred features are demonstrably optional under the official requirement; if a deferred surface is mandatory, reopen MVP scope and add the phases/tests before signoff.
- [ ] Planning-complete status is never described as product-complete; actual product signoff requires execution evidence and tester/owner approval.

## Production planning merge — `merging_allphase_prod.md`
- [ ] MVP gate is complete before any production extension is treated as ordered work.
- [ ] Each deferred surface has separate safety/authority, accuracy, privacy and benchmark gate.
- [ ] Temporal graph, interoperability, risk optimization and invariant work preserve MVP's data and uncertainty semantics.
- [ ] Security/property verification does not overstate guarantees; negative cases and rollback are covered.
- [ ] Tester 02 documents threat-model, retention, offline, accessibility and release-readiness plans.
- [ ] Updated traceability, phase reports, status board and handoffs agree; residual follow-ups are named owners/actions.
