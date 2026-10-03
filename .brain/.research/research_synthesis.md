# Research synthesis and planning decisions

## Problem and opportunity
The supplied ECDAT materials define a need to discover cryptographic assets across heterogeneous enterprise environments, describe them in a useful inventory/CBOM, assess quantum-related migration urgency, and help teams prioritize change. The project-specific report identifies the practical bottleneck as **trustworthy coverage plus context**, not merely detecting an algorithm name. A finding without provenance, purpose, dependencies, data lifetime, ownership, exposure, and uncertainty is a weak migration decision.

The master dossier's long-horizon concept is a cryptographic state-transition verification platform: observe, reconcile evidence, quantify uncertainty, reason over dependencies and data, predict change impact, plan constrained migration, verify properties, and monitor drift. The competitive dossier argues that flat inventory/dashboard features are already common; defensible differentiation should be measurable evidence quality, honest blind-spot accounting, explainable prioritization, interoperability, privacy, and verification.

## MVP boundary selected
**MVP = authorized upload of a bounded repository/archive into a local-first webapp; deterministic source-code, dependency-manifest, configuration, and certificate-file discovery for a documented subset; normalized evidence with source path/line/hash and collector/rule version; duplicate-aware inventory; explicit coverage states; user-supplied context; transparent scenario-based quantum/migration prioritization; reviewable CBOM-style JSON/CSV and human-readable report.**

This boundary follows the SIH report's reproducible seeded corpus and emergency fallback. It deliberately does not claim to inventory all enterprise assets. A failed/unsupported collector produces partial coverage and “not assessed,” never an implicit clean bill of health. Core categorization and risk are deterministic; AI is not used to identify algorithms or assign security status.

## Explicitly deferred or excluded
- MVP does not probe arbitrary public endpoints, clone unknown remote repositories, run privileged host agents, inspect live traffic, execute uploaded code, or automatically alter a customer's system.
- Binary, container-image, runtime, cloud KMS/HSM, hardware/TPM, firmware, OT/ICS, service-mesh, and fleet discovery are staged production research/extension tracks, each gated on authorized test fixtures and measurable coverage. No universal detection claim.
- Autonomous remediation, production migration, live PQC negotiation, cryptographic chaos experiments, security-property proofs, cryptographic digital twin, national/federated observatory, blockchain, large language model features, and novel cryptanalysis are not MVP deliverables.
- Never ingest private key material as a feature; sanitize evidence, treat uploaded archives as hostile, and avoid external source-code processing by default.

## Decisions driven by research
| Decision | Evidence basis | Planning consequence |
|---|---|---|
| Evidence first; no bare algorithm-only result | SIH report §§4, 7–9; master dossier primitives 5–10; Cryptoscope and BF-CBOM discussion | W02 owns normalized claims, provenance, confidence, identity and deduplication; W01 supplies evidence anchors. |
| Coverage is distinct from detection result | SIH report §§7, 9, 13; discovery SoK/CISA summary; competitive dossier | W01 emits assessed/unsupported/failed states and coverage denominator; testers inject unsupported files and parser failures. |
| Narrow, repeatable upload-first MVP | SIH report data audit, 72-hour test, fallback and “why not over-engineer”; no repo exists | Workers plan a modular monolith and bounded upload workflow; no new cloud/live integrations. |
| Contextual risk must be explainable and scenario-based | SIH report §11; research note on Mosca/QARS and uncertainty | W03 versions factors/weights and shows sensitivity; quantum horizon is user-configurable, not forecast as fact. |
| CBOM is an export projection, not the internal truth model | CycloneDX paper and master data model; BF-CBOM comparison | W02 defines an internal evidence record first, then validates an interoperable CBOM-like export. |
| No core LLM decisions | SIH report §§5, 10, 15 and master dossier privacy/hostile-input guidance | Rule-only classification and recommendation; optional explanation cannot create new claims and is out of MVP. |
| Real enterprise scopes are not fully observable from an upload | CISA/SIH report and multi-modal master dossier | W03 and W04 expose “not assessed” surfaces and manual context gaps; production extensions require separate gates. |
| Algorithm status can change | supplied papers on Classic McEliece/BAG-Loong and dossier algorithm-health gap | Rules carry source/version/effective date; no “PQC = permanently safe” assertion. Production may add status-feed review. |

## Testable planning hypothesis
On the declared seeded benchmark, a provenance-aware, coverage-accounted inventory plus contextual ranking should be more auditable and produce fewer duplicate/unexplained prioritization outcomes than a regex-only, flat-severity baseline. This remains a **hypothesis** until future implementation runs a pre-registered corpus and reports precision, recall, F1, duplicate reduction, coverage by artifact class, confidence-band agreement, ranking sensitivity, and time-to-inventory. No result is claimed here.

## Decisions still requiring future project owner confirmation
1. Verify exact official SIH26164 wording, constraints, and accepted demo boundaries against the portal; the archive itself records that full portal text was not reachable.
2. Choose the first source languages and exact parser/detector rule set from the team's actual skills and benchmark, not this plan alone.
3. Set upload size/file-count/runtime limits, retention/deletion policy, and hosting jurisdiction before implementation.
4. Confirm target CycloneDX CBOM version/profile and validate generated documents against that version.
5. Approve risk weights and policy defaults with a security owner; retain configurable scenarios and avoid presenting scores as objective facts.
6. Confirm any production network/binary/cloud connector only after written scope/authorization, safe fixtures, and threat modeling.
