# Final production planning merge gate

**Gate type:** final full-system planning reconciliation after the MVP planning merge and after production phase plans. This document deliberately does not claim any production implementation or deployment has occurred.

## Preconditions
- MVP planning gate is reviewed and signed by the project owner.
- Official scope, repository/stack, data policy and MVP acceptance are confirmed.
- Any production surface has an explicit authorization, risk assessment and representative benchmark before implementation is proposed.

## Production phase plans included
| Track | Planned enhancements | Boundary / evidence needed |
|---|---|---|
| W01 | Static binary/container discovery; optional allowlisted TLS/session evidence extension | Never execute uploaded binaries; network scope must be explicitly owned/authorized; report per-class accuracy and blind spots. |
| W02 | Temporal identity/drift/lineage; current CBOM profile conformance and generator disagreement analysis | Raw observations remain immutable; prove identity stability; validator-backed schema claims only. |
| W03 | Dependency-aware constrained roadmap; security-property, trust, downgrade and rollback validation plan | Advisory; explicit constraints and negative tests; no guarantee without reviewed assumptions and actual evidence. |
| W04 | Offline/self-hosted operational hardening, RBAC/audit/retention/accessibility and release docs | Threat model and owner/security approval; no certification claim. |
| Tester 01/02 | Repeat functional/integration/security/regression cycles for every expanded collector/rule/schema version | Maintain separate denominators, benchmarks, reports, defects and signoffs; unsupported remains visible. |

## Final integration outcomes expected (future)
- One versioned evidence model supports source observations, optional later surfaces, conflicting evidence and temporal provenance without flattening uncertainty.
- Each additional collector has a declared coverage envelope, reliability metrics, safe failure behavior and an authorized scope.
- Risk/roadmap outputs can be reproduced from recorded inputs, rule version and scenario assumptions; recommendation status is advisory.
- Export mappings are validator-backed, privacy-reviewed and versioned.
- UI, audit log and reports distinguish capability, configuration, negotiation and actual use; no silent coverage overclaim.
- Release runbook, retention/deletion, offline update, backup/restore, access control and incident escalation are documented and reviewed.

## Final gate checklist
See `shared/merge_checklist.md` production section. Additionally require: all production reports present; tester defects routed and retested; open risks have named owner/mitigation/expiry; all out-of-scope research topics retain explicit disposition; no blocker is called complete without evidence.

## Residual follow-up register
1. Validate exact SIH problem statement and any official implementation/demo constraint (B-01).
2. On repository handoff, record branch/status/commit and reconcile actual source tree before changing any plan (B-02).
3. Choose and measure initial language/rule coverage, then add only evidence-supported formats (B-03).
4. Approve upload size, retention, hosting jurisdiction, tenancy and access model (B-04/B-08).
5. Select/validate CBOM version and risk defaults (B-05/B-06).
6. Keep live discovery disabled until written authorization and safe lab evidence exist (B-07).
7. Revalidate dated algorithm/status mappings against current authoritative sources before release (B-09).

## Gate outcome
**PLANNED — not signed.** The document consolidates intended production outcomes and residual work. It does not assert that a full system has been built, tested, secured, or released.
