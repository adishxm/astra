# Research Papers for SIH26164 ECDAT Final Documentation

## Recommended citation strategy

For the ECDAT final report, do not cite papers only to make the bibliography look large. Each citation should support one of these claims:

1. **Why the problem exists:** cryptographic inventory is necessary before PQC migration.
2. **How cryptographic discovery can be performed:** source, dependency, binary, configuration, certificate, and specification analysis.
3. **How to represent findings:** CBOM and provenance relationships.
4. **How to prioritize migration:** Mosca-style timeline reasoning, sensitivity, exposure, business criticality, and migration effort.
5. **Why the problem remains open:** incomplete detection, inconsistent tool outputs, proprietary cryptography, and lack of contextual information.
6. **How ECDAT is evaluated:** precision, recall, coverage, false positives, duplicate reduction, and comparative analysis.

Use peer-reviewed conference/journal papers where possible. Use arXiv papers as recent technical preprints and label them as preprints. Use NIST, CISA, and CycloneDX documents as authoritative standards/guidance, not as peer-reviewed research papers.

## A. Highest-priority papers for ECDAT

### 1. Cryptoscope: Analyzing Cryptographic Usages in Modern Software

**Authors:** Micha Moffie, Omer Boehm, Anatoly Koyfman, Eyal Bin, Efrayim Sztokman, Sukanta Bhattacharjee, Meghnath Saha, James McGugan

**Year/status:** 2025, arXiv preprint

**Link:** https://arxiv.org/abs/2503.19531

**Why it is important:** This is the closest recent technical paper to the ECDAT core. Cryptoscope uses cryptographic domain knowledge and compiler techniques to statically analyze source code. It uses control-flow and data-flow information to construct a queryable inventory rather than returning disconnected API matches. The paper reports that more than 92% of its test cases included the cryptographic operation, APIs, and related material such as keys, nonces, and random sources. It also reports detection of 11 out of 15 cryptographic weaknesses in the CamBench benchmark.

**Use in the final document:**

- Related work for source-code cryptographic discovery.
- Justification for AST, compiler, control-flow, and data-flow analysis.
- Baseline comparison against regex-only scanning.
- Support for ECDAT’s evidence-linked inventory design.

**ECDAT lesson:** Do not treat a cryptographic API call as a complete finding. The surrounding operation, key material, nonce, random source, purpose, and data flow matter.

**Limitation to acknowledge:** It focuses primarily on static source-code analysis. ECDAT can extend the idea to dependencies, certificates, configurations, containers, and binary evidence while clearly reporting coverage limits.

---

### 2. SoK: Challenges for Implementing Automated Cryptography Discovery and Inventory Tool

**Authors:** Hiroki Yamamuro, Shusaku Uemura, Kazuhide Fukushima

**Year/status:** 2026, ICISSP conference paper

**DOI:** https://doi.org/10.5220/0014227100004061

**Paper page:** https://www.scitepress.org/PublishedPapers/2026/142271/

**Why it is important:** This is one of the most directly relevant papers for ECDAT. It formalizes the role of automated cryptography discovery and inventory tools, compares information sources such as source code, binary code, and specification documents, and discusses the strengths and implementation issues of different discovery methods.

**Use in the final document:**

- Problem definition and system scope.
- Justification for multi-surface collection.
- Architecture section for source, binary, and specification collectors.
- Limitations section covering inconsistent information and implementation/configuration differences.
- Research-gap section explaining why “complete discovery” remains difficult.

**ECDAT lesson:** The tool should maintain a **coverage matrix**. For every scan, show what was assessed, what was not assessed, and what confidence applies to each result.

---

### 3. BF-CBOM: Uncovering Cryptographic Assets Through Comparative CBOM Analysis at Scale

**Authors:** Roman Bögli, Jonas Spieler, Timo Kehrer

**Year/status:** 2026, ICPC ’26 short paper; open access

**DOI:** https://doi.org/10.1145/3794763.3794831

**Paper page:** https://dl.acm.org/doi/10.1145/3794763.3794831

**Why it is important:** BF-CBOM orchestrates multiple CBOM generators, aggregates their outputs, and compares the results. Its preliminary experiments show significant discrepancies between generated CBOMs. This is highly valuable for ECDAT because it supports the idea that discovery quality must be evaluated comparatively rather than assumed.

**Use in the final document:**

- Related work for CBOM generation and analysis.
- Motivation for using multiple collectors or baselines.
- Justification for discrepancy detection and provenance tracking.
- Evaluation design: compare ECDAT output with baseline tools and known ground truth.

**ECDAT lesson:** A strong product is not only a scanner. It is also an **evaluation and reconciliation layer** that explains why two sources disagree.

**Recommended experiment inspired by this paper:** Run a seeded repository through regex scanning, AST scanning, dependency analysis, and ECDAT correlation. Compare the findings, duplicates, missing assets, and confidence levels.

---

### 4. Standardization of Cryptography Bill of Materials in OWASP CycloneDX

**Authors:** Basil Hess, Nicklas Körtge

**Year/status:** 2024, ETSI/IQC QSC 2024 workshop publication/presentation

**Link:** https://research.ibm.com/publications/standardization-of-cryptography-bill-of-materials-in-owasp-cyclonedx

**Why it is important:** This work describes the standardization effort for CBOM in OWASP CycloneDX. It covers cryptographic algorithms and properties, dependencies between applications and cryptographic providers, network endpoints and cipher suites, certificates, and key material. It also discusses quantum-safe assessment and integration into SDLC/CI pipelines.

**Use in the final document:**

- CBOM schema selection.
- Data-model design.
- Interoperability justification.
- Future work involving CI/CD and continuous monitoring.

**ECDAT lesson:** Exporting a standard or standard-compatible CBOM is more defensible than inventing a dashboard-only JSON format.

**Important distinction:** This is a standards-oriented publication rather than a conventional empirical research paper. Cite it for CBOM concepts and interoperability, not for detection accuracy.

---

### 5. Migrating Software Systems Towards Post-Quantum Cryptography — A Systematic Literature Review

**Authors:** Christian Näther, Daniel Herzinger, Stefan-Lukas Gazdag, Jan-Philipp Steghöfer, Simon Daum, Daniel Loebenberger

**Year/status:** 2024, systematic literature review/preprint submitted for publication

**Link:** https://arxiv.org/html/2404.12854v2

**Why it is important:** This review surveys PQC migration approaches and real-world software-system migrations. It identifies four major migration phases and highlights recurring adoption challenges: limited PQC experience, high realization effort, security concerns, and complexity. It also notes that terminology, migration steps, and roles are not yet consistently defined.

**Use in the final document:**

- Literature review introduction.
- PQC migration lifecycle.
- Stakeholder and role analysis.
- Justification for ECDAT’s migration backlog and decision-support features.
- Discussion of deployment barriers and strategic flexibility.

**ECDAT lesson:** Inventory is only one phase. ECDAT should connect discovery to risk assessment, roadmap creation, migration planning, and governance without pretending to perform automatic production migration.

---

### 6. Toward a Common Understanding of Cryptographic Agility — A Systematic Review

**Authors:** Christian Näther, Daniel Herzinger, Jan-Philipp Steghöfer, Stefan-Lukas Gazdag, Eduard Hirsch, Daniel Loebenberger

**Year/status:** 2024 initial preprint; revised version listed on arXiv in 2026

**Link:** https://arxiv.org/abs/2411.08781

**Why it is important:** The paper systematizes definitions of cryptographic agility and identifies six categories: context, mode, desired capabilities, cryptographic assets, quality attributes, and drivers. It synthesizes cryptographic agility around the ability to set up, identify, and modify cryptographic assets flexibly, continuously, and efficiently.

**Use in the final document:**

- Define cryptographic agility accurately.
- Explain why ECDAT should identify assets and dependencies rather than only label algorithms.
- Support future roadmap features such as migration readiness, policy checks, and change impact analysis.
- Distinguish crypto-agility from simply “using PQC.”

**ECDAT lesson:** ECDAT is an enabling layer for crypto-agility. The product should help organizations identify what must change and estimate the impact of changing it.

---

### 7. Towards a Unified Quantum Risk Assessment

**Authors:** Šarūnas Grigaliūnas, Rasa Brūzgienė

**Year/status:** 2025, Electronics, 14(17), 3338

**DOI:** https://doi.org/10.3390/electronics14173338

**Link:** https://www.mdpi.com/2079-9292/14/17/3338

**Why it is important:** The paper proposes the Quantum-Adjusted Risk Score (QARS), extending Mosca’s time-based reasoning with sensitivity and exposure dimensions. It places the model within a PAREK lifecycle: post-quantum asset and algorithm inventory, risk assessment, road mapping, execution, and governance.

**Use in the final document:**

- Theoretical basis for the ECDAT risk engine.
- Justification for combining timeline, data sensitivity, and exposure.
- Risk-scoring methodology.
- Calibration and scenario-based validation.

**ECDAT lesson:** Mosca’s inequality is a useful starting point but is too coarse as a complete enterprise score. ECDAT should use transparent, configurable factors and display how each factor affects priority.

**Caution:** QARS is a recent proposed model. Do not state that it is an universally accepted standard. Present it as a research basis that ECDAT adapts and evaluates.

---

### 8. A Framework for Migrating to Post-Quantum Cryptography: Security Dependency Analysis and Case Studies

**Authors:** K. F. Hasan and co-authors; verify the complete author list from the final IEEE record before submission

**Year/status:** 2024 IEEE publication; related preprint from 2023

**IEEE link:** https://ieeexplore.ieee.org/abstract/document/10417052/

**Preprint link:** https://arxiv.org/abs/2307.06520

**Why it is important:** This work proposes a PQC migration framework based on security dependency analysis and case studies. It is useful for showing that migration decisions depend on relationships between cryptographic components, protocols, software, and systems.

**Use in the final document:**

- Dependency graph design.
- Migration planning and security-dependency analysis.
- Case-study methodology.
- Explanation of why a flat list of algorithms is insufficient.

**ECDAT lesson:** The key unit of analysis should be an **asset plus its dependencies and operational context**, not simply a cryptographic primitive in isolation.

**Bibliographic caution:** IEEE Xplore access may restrict the full text. Use the IEEE record for the final citation and use the open preprint for reading if necessary.

---

## B. Important supporting papers for binary and proprietary cryptography

### 9. Where’s Crypto? Automated Identification and Classification of Proprietary Cryptographic Primitives in Binary Code

**Authors:** Carlo Meijer, Veelasha Moonsamy, Jos Wetzels

**Year/status:** 2021, 30th USENIX Security Symposium, pp. 555–572

**Link:** https://www.usenix.org/conference/usenixsecurity21/presentation/meijer

**BibTeX metadata:** The USENIX page provides an official BibTeX record.

**Why it is important:** This paper addresses the problem of identifying proprietary cryptographic primitives in binary code, including embedded systems. It combines data-flow graph isomorphism with symbolic execution and provides an open-source IDA plug-in.

**Use in the final document:**

- Binary-discovery related work.
- Explanation of why source-code-only scanning is incomplete.
- Future-work justification for binary and embedded-system collectors.
- Discussion of proprietary cryptography and black-box analysis.

**ECDAT lesson:** Binary discovery is technically difficult and should be presented as an advanced module or bounded prototype capability, not as a guaranteed universal feature.

---

### 10. Automated Detection and Classification of Cryptographic Algorithms in Binary Programs Through Machine Learning

**Author:** Diane Duros Hosfelt

**Year/status:** 2015, master’s thesis/preprint

**Link:** https://arxiv.org/abs/1503.01186

**Why it is important:** This work investigates machine-learning methods for discovering and classifying cryptographic algorithms in compiled binaries. It reports promising results on small, single-purpose programs while explicitly noting that further evaluation is required on real-world binaries.

**Use in the final document:**

- Historical background for ML-assisted binary discovery.
- Motivation for treating binary analysis as a research module.
- Support for a cautious statement about generalization from small binaries to enterprise software.

**ECDAT lesson:** A model that works on clean laboratory binaries may not generalize to optimized, obfuscated, statically linked, stripped, or proprietary enterprise binaries. ECDAT must measure this explicitly.

**Citation status:** Use as supporting technical literature, not as the main empirical basis for the ECDAT architecture.

---

## C. Additional papers worth reading if the team has time

### 11. On the State of Crypto-Agility

**Authors:** N. Alnahawi and co-authors

**Year/status:** 2023, Cryptology ePrint Archive

**Link:** https://eprint.iacr.org/2023/487

**Use:** Background on crypto-agility research challenges and terminology. Useful for the literature review and related-work section.

### 12. Enterprise Migration to Post-Quantum Cryptography: Timeline Analysis and Strategic Frameworks

**Author:** R. Campbell

**Year/status:** 2025, *Computers*, 15(1), 9, according to the publisher listing

**Link:** https://www.mdpi.com/2073-431X/15/1/9

**Use:** Strategic migration timelines, “store now, decrypt later,” enterprise planning, and crypto-agility concerns. Use as supporting context, while preferring NIST/CISA for authoritative policy claims.

### 13. Cryptographic Asset Discovery and Inventory for Embedded Systems

**Author:** R. Campbell

**Year/status:** 2026 preprint

**Link:** https://www.preprints.org/manuscript/202601.1422

**Use:** Embedded-system taxonomy and discovery challenges. Useful if ECDAT includes firmware, IoT, or hardware-module scope.

**Caution:** Preprint status should be clearly labelled.

### 14. BF-CBOM replication package and related CBOM generators

The BF-CBOM paper is especially useful because it identifies the need to compare multiple CBOM generators. Read its references and replication package to examine:

- CBOMKit;
- cdxgen with CBOM support;
- CryptobomForge;
- CodeQL/SARIF-based analysis;
- CycloneDX CBOM output.

Use these tools as baselines only after checking their current versions and language support.

## D. Authoritative standards and government documents to cite alongside the papers

These are not research papers, but they should appear in the final ECDAT documentation because they define the practical problem and expected terminology.

### 1. CISA — Strategy for Migrating to Automated Post-Quantum Cryptography Discovery and Inventory Tools

**Year:** 2024

**Link:** https://www.cisa.gov/sites/default/files/2024-09/Strategy-for-Migrating-to-Automated-PQC-Discovery-and-Inventory-Tools.pdf

**Use:** Discovery types, inventory fields, manual-collection gaps, custom software limitations, and deployment context.

### 2. NIST NCCoE — Migration to Post-Quantum Cryptography

**Link:** https://www.nccoe.nist.gov/applied-cryptography/migration-to-pqc

**Use:** Official framing of cryptographic discovery, inventory, risk prioritization, and PQC migration.

### 3. NIST — FIPS 203, FIPS 204, and FIPS 205

**FIPS 203:** https://csrc.nist.gov/pubs/fips/203/final

**FIPS 204:** https://csrc.nist.gov/pubs/fips/204/final

**FIPS 205:** https://csrc.nist.gov/pubs/fips/205/final

**Use:** Official algorithm names and standardization status for ML-KEM, ML-DSA, and SLH-DSA.

### 4. NIST CSWP 39upd1 — Considerations for Achieving Cryptographic Agility

**Link:** https://csrc.nist.gov/pubs/cswp/39/upd1/considerations-for-achieving-crypto-agility/final

**Use:** Definition and operational meaning of crypto-agility. This current update supersedes the earlier CSWP 39 page.

### 5. OWASP CycloneDX — Cryptography Bill of Materials

**Link:** https://cyclonedx.org/capabilities/cbom/

**Use:** CBOM concepts, cryptographic asset relationships, interoperability, and standard output design.

## E. Recommended final-paper shortlist

If the final documentation can cite only **eight research papers**, use these:

1. Yamamuro, Uemura, and Fukushima — **SoK: Challenges for Implementing Automated Cryptography Discovery and Inventory Tool**.
2. Moffie et al. — **Cryptoscope: Analyzing Cryptographic Usages in Modern Software**.
3. Bögli, Spieler, and Kehrer — **BF-CBOM: Uncovering Cryptographic Assets Through Comparative CBOM Analysis at Scale**.
4. Hess and Körtge — **Standardization of Cryptography Bill of Materials in OWASP CycloneDX**.
5. Näther et al. — **Migrating Software Systems Towards Post-Quantum Cryptography — A Systematic Literature Review**.
6. Näther et al. — **Toward a Common Understanding of Cryptographic Agility — A Systematic Review**.
7. Grigaliūnas and Brūzgienė — **Towards a Unified Quantum Risk Assessment**.
8. Meijer, Moonsamy, and Wetzels — **Where’s Crypto? Automated Identification and Classification of Proprietary Cryptographic Primitives in Binary Code**.

Add the Hasan framework when discussing migration dependency analysis, and add Hosfelt when discussing historical ML-based binary detection.

## F. Suggested literature-review structure for the final document

### 1. Cryptographic discovery

Cite Yamamuro et al., Moffie et al., Meijer et al., and Hosfelt. Explain the progression from source-code analysis to binary and specification-based discovery.

### 2. Cryptographic inventory and CBOM

Cite Hess and Körtge, Bögli et al., and CycloneDX. Explain why a standardized, machine-readable output is needed.

### 3. PQC migration and crypto-agility

Cite Näther et al. on PQC migration, Näther et al. on crypto-agility, Hasan et al. on dependency analysis, and NIST CSWP 39upd1.

### 4. Quantum-risk prioritization

Cite Grigaliūnas and Brūzgienė, Mosca-related work where available, CISA, and NIST NCCoE. Explain why timeline alone is insufficient and why ECDAT adds sensitivity, exposure, business criticality, and migration effort.

### 5. Research gap

State that existing work demonstrates strong individual techniques, but ECDAT addresses the integration gap:

> **A reproducible, evidence-linked, multi-surface inventory that reconciles heterogeneous findings, exposes coverage uncertainty, and converts the result into an explainable migration-priority queue.**

## G. Claims the team should avoid

Avoid these unsupported claims:

- “ECDAT is the first cryptographic discovery platform.”
- “ECDAT detects every cryptographic asset.”
- “AI can accurately identify all quantum-vulnerable cryptography.”
- “Mosca’s inequality alone calculates enterprise risk.”
- “The system automatically chooses the correct PQC algorithm for production.”
- “Our scanner is 100% accurate.”
- “The project is novel because it has a dashboard.”

Prefer measurable statements:

- “ECDAT detects X of Y seeded cryptographic cases on the benchmark corpus.”
- “The provenance layer reduces duplicate findings by X% against the baseline.”
- “The contextual risk engine changes prioritization when data lifetime and business criticality change.”
- “Unsupported artifacts are explicitly reported as not assessed.”
- “PQC recommendations are candidate mappings requiring compatibility and operational validation.”

## References

[1]: https://arxiv.org/abs/2503.19531 "Cryptoscope: Analyzing cryptographic usages in modern software"

[2]: https://www.scitepress.org/PublishedPapers/2026/142271/ "SoK: Challenges for Implementing Automated Cryptography Discovery and Inventory Tool"

[3]: https://dl.acm.org/doi/10.1145/3794763.3794831 "BF-CBOM: Uncovering Cryptographic Assets Through Comparative CBOM Analysis at Scale"

[4]: https://research.ibm.com/publications/standardization-of-cryptography-bill-of-materials-in-owasp-cyclonedx "Standardization of Cryptography Bill of Materials in OWASP CycloneDX"

[5]: https://arxiv.org/html/2404.12854v2 "Migrating Software Systems Towards Post-Quantum Cryptography — A Systematic Literature Review"

[6]: https://arxiv.org/abs/2411.08781 "Toward a Common Understanding of Cryptographic Agility — A Systematic Review"

[7]: https://doi.org/10.3390/electronics14173338 "Towards a Unified Quantum Risk Assessment"

[8]: https://www.usenix.org/conference/usenixsecurity21/presentation/meijer "Where’s Crypto? Automated Identification and Classification of Proprietary Cryptographic Primitives in Binary Code"

[9]: https://arxiv.org/abs/1503.01186 "Automated detection and classification of cryptographic algorithms in binary programs through machine learning"

[10]: https://ieeexplore.ieee.org/abstract/document/10417052/ "A Framework for Migrating to Post-Quantum Cryptography: Security Dependency Analysis and Case Studies"

[11]: https://eprint.iacr.org/2023/487 "On the State of Crypto-Agility"

[12]: https://www.cisa.gov/sites/default/files/2024-09/Strategy-for-Migrating-to-Automated-PQC-Discovery-and-Inventory-Tools.pdf "CISA Strategy for Migrating to Automated Post-Quantum Cryptography Discovery and Inventory Tools"

[13]: https://www.nccoe.nist.gov/applied-cryptography/migration-to-pqc "NIST NCCoE Migration to Post-Quantum Cryptography"

[14]: https://csrc.nist.gov/pubs/cswp/39/upd1/considerations-for-achieving-crypto-agility/final "NIST CSWP 39upd1 Considerations for Achieving Cryptographic Agility"

[15]: https://cyclonedx.org/capabilities/cbom/ "OWASP CycloneDX Cryptography Bill of Materials"
