# Shared interface and data contracts (planning level)

No API or schema code is created here. Contracts are logical and stack-agnostic because no repository or implementation stack was supplied.

## Intake → scan job (W01 ↔ W04)
- Input: user-authorized local upload; archive name, size/file count, declared scope, user/tenant, optional context. Never trust client MIME type or archive paths.
- State: `QUEUED → VALIDATING → RUNNING → COMPLETE | PARTIAL | FAILED | REJECTED`; preserve scan ID, collector/rule versions, start/end timestamps, cancellation reason, and per-collector status.
- Result: supported/assessed denominator, exclusions, parse errors and unsupported formats; zero findings is not “safe.” No uploaded code execution or outbound scan.

## Observation → inventory (W01 → W02)
Required logical fields: observation ID; candidate asset ID; claim/asset type; algorithm/protocol/purpose/parameters where known; source kind; repository-relative path; line/range if available; evidence digest and sanitized excerpt; detector/rule version; scan and observed time; scope; confidence band plus rationale; state (`OBSERVED`, `INFERRED`, `DECLARED`, `VERIFIED`, `CONFLICTING`, `UNKNOWN`, `UNSUPPORTED`, `FAILED`); redaction flag. Do not persist private-key bytes or unredacted secret values.

## Identity/graph → risk (W02 → W03)
Stable asset identifiers must not imply verification. Preserve source observations and alternate hypotheses when deduplicating. Relationships carry type, evidence/provenance, confidence, and validity time. Risk input separates algorithm status from usage/purpose, data lifetime/sensitivity, exposure, business criticality, migration duration, dependency impact, scan freshness and uncertainty; missing values remain explicit.

## Risk → UI/export (W03 → W04/W02)
Every priority returns model/rule version, factor values, factor contribution/reason codes, assumptions/horizon, confidence/coverage caveat, advisory candidate mapping/source date, compatibility gaps, and next human action. User overrides require actor, timestamp, rationale and before/after value. Exports exclude secrets and include scope, timestamp, rule/version metadata and known limitations.

## CBOM projection
W02 proposes a versioned internal-to-CycloneDX CBOM mapping only after version selection. Preserve unmapped elements and provenance; validate generated output with a compatible validator before using “valid/conformant.” CSV/PDF/report are convenience projections, not authoritative substitutes.

## Error and security contract
Partial results survive collector failure with explicit coverage loss. Error messages do not include secret values. All uploads have size/count/expansion/time limits, path normalization, symlink policy, content hashing and deletion/retention plan. Role enforcement and audit events are required before multi-user/tenant use. Future endpoint scanning requires explicit allowlist authorization and rate-limits.
