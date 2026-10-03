# ECDAT webapp — master execution plan

**Planning freeze:** 2026-10-03. **Mode:** planning only. **Project basis:** supplied SIH26164 ECDAT research. **Delivery sequence:** MVP design → MVP planning merge gate → production design → final production planning gate.

## Goal and measurable research hypothesis
Plan a local-first webapp that converts an authorized, bounded repository/archive into a reviewable, evidence-linked cryptographic inventory, an explicit coverage/unknown report, a transparent contextual migration-priority queue, and a sanitized CBOM-style export. The research hypothesis is that provenance plus context yields more auditable and less duplicate-prone prioritization than a regex-only flat-severity baseline. It remains unproven until an implementation is evaluated against seeded ground truth.

## Non-goals
No source code, runtime logic, test execution, active scanning, arbitrary network probing, uploaded-code execution, automatic remediation, private-key ingestion, or AI-driven classification is part of this planning run. No complete enterprise discovery claim. Features such as hardware, firmware, cloud, runtime, binary, container, live TLS, digital twin, formal property proof, cryptanalysis, and national-scale observatory are staged or explicitly excluded.

## Workstream topology — phase counts sized to assigned scope
| Owner | MVP responsibility | MVP phase count | Conditional post-MVP responsibility |
|---|---|---:|---|
| Worker 01 — Discovery & Safe Intake | Safe archive intake; supported source/manifest/config/certificate discovery; coverage and benchmark readiness | 3 | 2 phases: static binary/container evaluation; separately authorized endpoint/network evidence |
| Worker 02 — Evidence & Interoperable Inventory | Evidence/identity/redaction model; context graph, review/audit and CBOM-style export | 2 | 2 phases: temporal identity/drift; schema conformance and generator reconciliation |
| Worker 03 — Risk & Migration | Transparent model; advisory mapping/backlog; scenario sensitivity and decision evidence | 3 | 2 phases: constrained roadmap; security-property/trust/rollback assurance |
| Worker 04 — Web Workflow & Integration | Complete workflow and roles; integrated evidence/risk/export experience; packaging/docs/demo and handoff | 3 | 1 phase: offline operations, security hardening and release readiness |
| Tester 01 — Functional assurance | Discovery/evidence/coverage plus risk and end-to-end acceptance plans | 2 cycles | Repeat by release and retest every worker fix |
| Tester 02 — Integration/regression/docs | Contract/security/export plus regression/docs/demo/release plans | 2 cycles | Production gate-specific review |

Counts deliberately differ (3/2/3/3) because intake/coverage, evidence/export, decision support, and end-to-end integration have different decomposition needs. These are phase gates, not an equal phase quota. **All MVP phases together yield the complete MVP within the declared and officially confirmed boundary.** A critical in-scope capability cannot be left as a TODO, stub, unintegrated output, or production-phase task. Production is only for optional capabilities beyond the usable MVP.

## Delivery lifecycle and dependencies
1. **Preflight:** inspect repository (none supplied), freeze research sources, verify official statement and owner scope, establish safe-upload and data-retention assumptions.
2. **Contract first:** W02 drafts observation model; W01 detector output, W03 risk inputs, W04 UI/API states align before parallel phase work. W01 and W02 can plan in parallel with this contract as a gate.
3. **MVP plan:** complete all scope-sized phases in each worker index: W01 safe intake → discovery → coverage; W02 evidence model → context graph/export; W03 risk model → migration backlog → scenario validation; W04 user workflow → integrated review/decision/export → docs/demo/release acceptance. Testers plan early and review the complete integrated MVP, not only isolated modules.
4. **MVP merge gate:** require every in-scope capability to be fully specified, integrated end-to-end, covered by validation plans, documented and owned. Anything unfinished within the agreed boundary blocks MVP completion; only explicit non-MVP extensions can remain for production. This document describes a planning gate, not a code merge.
5. **Production plan:** only after MVP planning gate; narrow extension phases have separate authorization, accuracy and safety gates.
6. **Final production merge gate:** reconcile completed *plans*, unresolved limitations, retest requirements, release documentation, and residual follow-ups.

## MVP definition and completeness rule

The desired MVP is a **usable, coherent end-to-end webapp within the declared and official scope**: an authorized user can supply an accepted archive; receive a complete or honestly partial scan; inspect evidence/coverage; enrich context; understand and adjust migration priority; review findings; and export the inventory/report. No core step may be missing, left as a mock/stub, or postponed to production. “MVP complete” means all these in-scope capabilities are integrated and meet their acceptance criteria, not merely that every worker wrote a phase plan.

The explicit scope boundary is bounded upload-based local-first discovery for the supported and named source, dependency-manifest, configuration, and certificate-file formats, plus evidence-backed inventory, contextual risk, advisory queue, and sanitized export. If official SIH requirements make another surface mandatory for MVP, re-scope it **before** MVP approval and add worker phases, interfaces, validation and reports. Deferred surfaces below are optional expansions only, never uncompleted MVP work.

## MVP acceptance thresholds (targets, not achieved results)
- Supported artifact classes, languages, exclusions and coverage denominator are versioned and shown to the user.
- Seeded-source benchmark targets ≥80% precision and ≥80% recall from the supplied SIH report; report per-class counts, confidence intervals or sample limitations where feasible, and do not extrapolate beyond corpus.
- Every finding links to safe evidence (source path/line or file hash), detector/rule version and scan timestamp; secrets are redacted.
- Duplicate handling is reversible/provenanced; conflicting observations remain visible.
- Unknown, unsupported, failed, not assessed and no finding are distinct states.
- Risk weights, horizon, data lifetime and migration duration are visible/versioned; changing a scenario input predictably changes rationale/rank where the factor is relevant.
- CBOM-style output passes its selected schema/profile validator before it is described as conformant; otherwise call it a project export.
- End-to-end synthetic demo completes without production data, network authority, or external model dependency.

## Decisions, assumptions, blockers
See `shared/decision_log.md`, `shared/assumptions.md`, and `shared/blocker_log.md`. High priority: exact official SIH wording; initial supported languages; upload/retention limits; CBOM schema/version; risk default owner approval; hosting and data jurisdiction.

## Planning deliverables and stop condition
Every worker phase has an objective, inputs, outputs, dependencies, tasks, future files-to-change list, validation, success criteria, risks/mitigations, report path, traceability IDs and handoff. Phase counts are scope-driven and unequal where the work warrants it. MVP completion requires all in-scope capabilities to be integrated and accepted; no unfinished core MVP capability can roll into production. Every tester cycle has scope, acceptance, defect taxonomy, documentation changes, signoff, report and traceability. Stop planning-complete only after both merge checklists, traceability coverage audit, and all planned report files are present; this does not assert implementation readiness without resolving the blockers.
