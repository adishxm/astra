# Worker 01 handoff plan

## Phase-specific planned work
- **MVP-01 — Safe upload intake and scan boundary** (MVP): Define the authorized local archive/repository intake, file and resource limits, path normalization, symlink policy, archive-bomb defenses, scan identity and read-only handling. Specify rejection and partial-result behavior. Completion evidence: File the accepted artifact and create a reproducible scan manifest without executing uploaded content. Trace: R01,R02,R05,R10,R12.
- **MVP-02 — Supported source, manifest, config and certificate discovery** (MVP): Plan the bounded and explicitly versioned source-language/rule set plus dependency manifests, configuration and certificate fixtures; each detector returns sanitized evidence anchors, rule versions, purpose/algorithm confidence and parse state. Supported languages remain an owner choice. Completion evidence: Each declared supported fixture can produce a structured observation; unsupported surfaces are explicitly identified. Trace: R01,R02,R05,R06.
- **MVP-03 — Coverage, partial scans and benchmark readiness** (MVP): Define per-surface assessed denominators, `NO_FINDING` vs `UNKNOWN/UNSUPPORTED/FAILED`, collector health, provenance-preserving duplicate handoff, ground truth and regex/AST/dependency baselines. Specify the ≥80% precision/recall target only for the agreed seeded supported-source corpus. Completion evidence: User can tell what was assessed, what failed, and what was not assessed; future benchmark results are reproducible by corpus/rule version. Trace: R02,R03,R06,R10,R12.
- **PROD-01 — Static binary and container discovery extension** (production): Evaluate bounded static-only binary/container adapters on labeled fixtures and document per-format detection/coverage, resource use and isolation needs. Uploaded executables are never run. Completion evidence: A go/no-go recommendation per format backed by a threat model and benchmark plan. Trace: R02,R03,R07,R08.
- **PROD-02 — Separately authorized endpoint/network evidence** (production): Design optional allowlisted TLS metadata/import pathway with written authorization, target scope, rate limits, audit, lab validation, and strict capability/configuration/negotiation/use distinctions. Completion evidence: Safe, separately gated design for one explicitly owned test target; otherwise remain disabled. Trace: R02,R03,R04,R09.

## Completion rule
All 3 MVP phases for this worker and every upstream dependency must be accepted before this worker hands off to the MVP merge. A core deliverable cannot be marked “future” or deferred to production.

## Current execution status
- **MVP-01**: **IMPLEMENTED & VALIDATED**. Safe archive intake (`.zip`, `.tar`, `.tar.gz`, `.tar.bz2`), streaming zip bomb protection, path traversal defenses, symlink escape rejection, sandbox read-only lifecycle, and `ScanManifest` generation implemented in `backend/app/intake/`. Verified with 13 unit tests (100% pass).
- **MVP-02**: **IMPLEMENTED & VALIDATED**. Deterministic discovery across source code (Python AST/regex, Java, JS/TS, Go, C/C++, Rust), package manifests (`package.json`, `pom.xml`, `requirements.txt`), configurations (TLS protocols, cipher suites, SSH), and X.509 certificates with strict private-key redaction. Verified with 8 tests. Emits canonical observations and `DiscoverySummary`.
- **MVP-03**: **IMPLEMENTED & VALIDATED**. Coverage accounting, denominator tracking, blind-spot visibility, partial scan error resilience, and ground-truth benchmark runner. Achieved AC-06 target ($\ge 80\%$ precision and recall). Verified with 4 tests (25/25 suite total).
- **Handoff status**: All Worker 01 MVP deliverables are fully implemented, tested, and ready for integration with Worker 02, Worker 03, and Worker 04.

## Dependencies / blockers
See each phase and `.work/shared/blocker_log.md`. Production work starts only after `merging_phase_mvp.md`.

## Validation / expected result
Tester cycles must cover this worker's acceptance IDs and retest any fix. Expected result is a coherent plan; it is not an observed runtime result.

## Report paths
- `../../.report/worker_01_mvp_01_report.md` — Safe upload intake and scan boundary.
- `../../.report/worker_01_mvp_02_report.md` — Supported source, manifest, config and certificate discovery.
- `../../.report/worker_01_mvp_03_report.md` — Coverage, partial scans and benchmark readiness.
- `../../.report/worker_01_prod_01_report.md` — Static binary and container discovery extension.
- `../../.report/worker_01_prod_02_report.md` — Separately authorized endpoint/network evidence.

## Docs, merge notes and recommendation
Update `phase_index.md`, `status.md`, shared traceability, contracts, acceptance and test matrix after any scope change. Keep one report per phase. Recommendation: complete all in-scope MVP phases and close all MVP defects before merge; then consider optional production phases.
