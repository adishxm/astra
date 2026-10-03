# Blocker log

| ID | Blocker / uncertainty | Impact | Owner | Resolution evidence / gate | Status at planning freeze |
|---|---|---|---|---|---|
| B-01 | Exact official SIH26164 statement/admin constraints not directly verified in supplied report; portal text was reported unavailable. | Could change required input sources, outputs or demo constraints. | Project owner + W04 | Compare official portal/problem PDF; update scope and traceability before implementation. | OPEN |
| B-02 | No repository, current branch, git status, commits, or existing planning artifacts were supplied. | Cannot align to existing stack, file paths, or prior design. | Project owner + W04 | Attach/identify repo; repeat repo preflight before implementation. | OPEN |
| B-03 | Initial supported languages and detector baselines are unknown. | Limits MVP scope and measured precision/recall. | W01 + Tester 01 | Select against team expertise and labeled benchmark; freeze support matrix. | OPEN |
| B-04 | Upload size, retention, deletion, tenancy, hosting jurisdiction and data classification are undecided. | Sensitive-source privacy and operational safety. | Product/security owner + W04 | Approve retention and deployment profile; threat-model gate. | OPEN |
| B-05 | Target CBOM schema/profile/version has not been selected or validated. | Export compatibility claims cannot be made. | W02 | Select current target, version and validator; add versioned mapping tests. | OPEN |
| B-06 | Risk factors/weights, horizon assumptions, data-lifetime defaults and criticality scale lack owner approval. | Ranking may be misleading even if computation is correct. | W03 + security/business owner | Review transparent scenarios and sensitivity; record decision before implementation. | OPEN |
| B-07 | No authorized production endpoint/network scope or real enterprise corpus is provided. | Live discovery and representativeness are not evidenced. | Owner + W01 | Keep network scanning deferred; use synthetic/lab fixtures unless written scope is approved. | OPEN |
| B-08 | Exact release expectations and regulatory/security obligations for sensitive deployments are unknown. | Offline/tenant/security controls may need expansion. | Owner + W04/Tester 02 | Confirm deployment audience and required controls before production plan is treated as build-ready. | OPEN |
| B-09 | Current status of all algorithm mappings and source links must be rechecked at implementation time. | Standards/research change; incorrect recommendation risk. | W03 | Date/version rules and verify official sources before release. | OPEN |
