# Archive quality, relevance, and evidence limits

## Inventory integrity
The exact archive contents are retained in `.ORG_research/`. See `../.work/shared/raw_archive_manifest.md` for byte counts and SHA-256 values. Duplicate files remain duplicated to preserve provenance. No additional external sources were fetched for this plan.

## Relevance split
- **Directly actionable:** ECDAT master dossier, competitive dossier, SIH feasibility report (Markdown and PDF), curated research-papers guide, research links/credits list.
- **Contextual:** cryptographic research PDFs that illustrate algorithm/implementation evolution, threshold PQC or adjacent deployment considerations, but do not specify ECDAT features.
- **Peripheral/out of scope:** unrelated OT/VSS, privacy-coin, CKKS, transform, lattice, side-channel, and other cryptographic papers. These are still catalogued in `research_index.md` and the traceability matrix with an explicit no-feature disposition.
- **Search snapshot:** `Papers updated in last 365 days.pdf` is an archive search-result capture containing 3,637 results, not evidence that all listed records were individually reviewed or are relevant.

## Evidence caveats
The SIH report says the official portal's detailed statement was not reachable; several requirements are reconstructed from public transcriptions and the user's uploaded research. SIH project scores are explicitly estimates; competitor descriptions may be vendor-reported or based on search snippets; research dossiers include proposals and future extensions. The plan therefore distinguishes **confirmed by supplied report**, **source-reported**, **planning assumption**, and **unverified** rather than claiming independent verification.

## Interpretation safeguard
A paper that proposes a cryptographic primitive is not equivalent to a standard, a secure implementation, a recommendation, or a deployment requirement. A cryptanalytic attack paper can motivate dated algorithm-health review but is not by itself grounds for classifying all related usage as compromised. Standards and algorithm-status mappings must be checked against authoritative current material before a future build/release.
