# ECDAT-X Competitive Advancement Intelligence Dossier
## Enterprise Cryptographic Discovery, Post-Quantum Readiness, Crypto-Agility & Migration Verification

**Prepared:** 03 October 2026  
**Project:** ECDAT / ECDAT-X — SIH 2026 Problem Statement 26164  
**Organization in PS:** National Technical Research Organisation (NTRO)  
**Purpose:** Systematically capture publicly documented advancements made by relevant commercial, open-source, standards, and research ecosystems, then translate those advancements into concrete implications for ECDAT-X.

---

## 0. How to use this document

This is **not a ranking of competitors**.

The purpose is to answer:

> **What has the ecosystem already built, what are the strongest ideas worth learning from, and which capabilities should ECDAT-X absorb, integrate, improve, or deliberately differentiate?**

The document therefore treats competitors positively and focuses on their technical progress.

Three evidence labels are used:

- **Documented:** directly described in official vendor/project documentation.
- **Standards/research:** described by standards bodies, research projects, or academic work.
- **Vendor-reported:** a capability or performance statement made by the vendor itself; it should be validated experimentally before being treated as an engineering fact.

Where a product page describes a capability, this dossier does **not** assume that the capability is uniquely novel, independently benchmarked, or universally available in every deployment tier.

---

# 1. Executive conclusion

The cryptographic-security market has moved significantly beyond:

```text
scan → find algorithms → make CBOM → calculate quantum risk
```

The leading ecosystem is converging toward:

```text
DISCOVER
   ↓
INVENTORY
   ↓
CORRELATE
   ↓
ASSESS RISK
   ↓
ASSIGN OWNERSHIP
   ↓
PRIORITIZE
   ↓
PLAN MIGRATION
   ↓
AUTOMATE / ORCHESTRATE
   ↓
ENFORCE POLICY
   ↓
VERIFY
   ↓
CONTINUOUSLY MONITOR
```

The most important competitive lesson is that **inventory alone is rapidly becoming table stakes**.

The public market already contains serious work in:

1. multi-layer cryptographic discovery;
2. continuous cryptographic inventory;
3. network-level discovery;
4. source-code analysis;
5. binary/container analysis;
6. CBOM generation;
7. ownership and dependency mapping;
8. quantum-risk assessment;
9. PQC migration planning;
10. crypto-agility orchestration;
11. policy enforcement;
12. CI/CD drift detection;
13. ticketing and workflow integration;
14. PKI/certificate lifecycle management;
15. KMS/HSM/key management;
16. enterprise governance;
17. AI-assisted discovery and remediation;
18. developer-native cryptographic analysis;
19. local/offline/privacy-preserving analysis;
20. xBOM/SBOM integration.

ECDAT-X should therefore **build on these advances instead of recreating them as isolated features**.

The more defensible research direction in the existing ECDAT-X plan is the integration of these capabilities into an **evidence-backed cryptographic state-transition system**:

```text
OBSERVE REALITY
      ↓
RECONCILE EVIDENCE
      ↓
QUANTIFY UNCERTAINTY
      ↓
BUILD CRYPTOGRAPHIC REALITY GRAPH
      ↓
UNDERSTAND DEPENDENCIES
      ↓
MODEL SECURITY PROPERTIES
      ↓
PREDICT CHANGE IMPACT
      ↓
SEARCH FOR SAFE MIGRATION
      ↓
SIMULATE
      ↓
EXECUTE
      ↓
ATTACK / FAULT TEST
      ↓
VERIFY SECURITY PROPERTIES
      ↓
MONITOR PRODUCTION
      ↓
DETECT DRIFT / DOWNGRADE / REGRESSION
      ↓
UPDATE THE MODEL
```

This direction is consistent with the existing ECDAT-X research dossier, which explicitly defines the system as an enterprise cryptographic observability, reasoning, migration and verification platform and treats uncertainty, temporal behavior, dependencies, trust, data lineage, simulation, security invariants and continuous verification as first-class concepts.

---

# 2. Market capability map

| Capability | Public ecosystem maturity | Examples |
|---|---|---|
| Certificate discovery | High | Keyfactor, DigiCert, AppViewX, Entrust, Sectigo |
| Key discovery | High | Keyfactor, CipherIQ, Fortanix, Entrust |
| Algorithm discovery | High | Keyfactor, QuSecure, AppViewX, CipherIQ |
| Source-code crypto discovery | High | IBM, AppViewX, PostQ |
| Binary/container discovery | High | IBM CBOMkit-theia, ReversingLabs |
| Network crypto discovery | High and growing | Keyfactor, QuSecure, QryptoCyber, Forescout |
| CBOM generation | High | IBM, AppViewX, QuSecure, CipherIQ, Qubrisk, ReversingLabs |
| Continuous inventory | High | Keyfactor, QuSecure |
| PQC risk assessment | High | Almost all major platforms |
| Migration roadmap | High | DigiCert, QryptoCyber, Fortanix, Sectigo |
| Crypto-agility orchestration | High and strategically important | QuSecure, Keyfactor, Entrust |
| Policy-as-code / policy gates | Emerging | Qubrisk, Keyfactor, AppViewX |
| CI/CD crypto drift | Emerging | Qubrisk, PostQ |
| Developer-native workflow | Emerging | PostQ, IBM ecosystem |
| AI-assisted crypto discovery | Emerging | QryptoCyber, SandboxAQ |
| Privacy/local-first discovery | Emerging | CipherIQ, Qubrisk |
| PKI/HSM/KMS lifecycle integration | High | Entrust, Fortanix, Thales, DigiCert |
| Hardware/firmware visibility | Adjacent / fragmented | ReversingLabs, NetRise and specialist ecosystems |
| Migration simulation | Emerging | ECDAT-X research direction; graph/research ecosystem |
| Security-property verification | Emerging research area | PQC certificate/validation research; ECDAT-X |
| Cryptographic chaos engineering | Emerging research direction | ECDAT-X |
| Cryptographic digital twin | Emerging research direction | ECDAT-X |
| Evidence epistemology / uncertainty-first inventory | Emerging research direction | ECDAT-X |
| Causal crypto drift analysis | Emerging research direction | ECDAT-X |
| Information-gain-driven discovery | Emerging research direction | ECDAT-X |

---

# 3. Keyfactor

## Official resources

- [Keyfactor — Cryptographic Discovery & Inventory](https://www.keyfactor.com/products/cryptographic-discovery-inventory/)
- [Keyfactor — Cryptographic Posture Management](https://www.keyfactor.com/products/cryptographic-posture-management/)

## What Keyfactor has advanced

Keyfactor's AgileSec / cryptographic posture work demonstrates one of the most mature approaches to **enterprise-wide cryptographic visibility**.

### 3.1 Multi-surface discovery

Keyfactor describes discovery across:

- endpoints;
- networks;
- cloud environments;
- code repositories;
- filesystems;
- servers;
- cloud workloads;
- infrastructure.

The product documentation also describes lightweight sensors and the ability to leverage existing EDR and vulnerability-management systems.

### 3.2 Broad cryptographic asset taxonomy

The documented discovery scope includes:

- TLS certificates;
- SSH keys;
- tokens;
- algorithms;
- protocols;
- cryptographic libraries;
- dependencies.

This matters because a useful inventory cannot stop at certificates.

### 3.3 Context-enriched inventory

Keyfactor goes beyond a list of assets by associating cryptographic objects with:

- usage;
- ownership;
- dependencies;
- risk context.

This is a major architectural lesson for ECDAT-X:

> **An asset without its surrounding system context is not enough for migration planning.**

### 3.4 Continuous monitoring

Keyfactor explicitly treats cryptographic discovery as something that should continue after the initial inventory.

The lifecycle is:

```text
Deploy sensors
    ↓
Discover
    ↓
Inventory
    ↓
Prioritize
    ↓
Remediate
    ↓
Continuously monitor
    ↓
Report / govern
```

### 3.5 Policy-driven cryptography

Keyfactor also describes centrally defining which algorithms should be used by applications and enforcing policies.

This moves the problem from:

> "What cryptography do we have?"

toward:

> "What cryptography are we allowed to have?"

### 3.6 Enterprise workflow integration

Keyfactor documents integrations with systems used for remediation and risk reporting, including ServiceNow workflows.

This is important because migration findings become useful only when they can enter normal enterprise operating processes.

## What ECDAT-X should learn

**Absorb:**

- continuous discovery;
- sensor architecture;
- enterprise integrations;
- policy engine;
- ownership;
- dependency-aware inventory;
- remediation workflow.

**Improve upon conceptually:**

- attach evidence to every claim;
- preserve contradictory observations;
- track observation freshness;
- model confidence;
- represent temporal state;
- predict migration consequences;
- verify the resulting security properties.

### Strategic lesson

Keyfactor demonstrates the value of **cryptographic posture management at enterprise scale**.

ECDAT-X should not compete by making another static scanner. It should make the inventory itself a **living evidence-backed state model**.

---

# 4. QryptoCyber

## Official resource

- [QryptoCyber](https://qryptocyber.com/)

## What QryptoCyber has advanced

QryptoCyber explicitly positions its platform around AI-powered cryptographic discovery, inventory and remediation strategy.

### 4.1 Five-pillar discovery

Its public product architecture divides discovery into:

1. External Network
2. Internal Network
3. IT Assets
4. Databases
5. Code

This is an excellent decomposition because it forces the system to think about cryptography as an enterprise-wide property rather than a source-code-only problem.

### 4.2 AI-powered inventory

QryptoCyber describes an AI-driven platform that turns cryptographic inventory into strategy and remediation planning.

### 4.3 CBOM as an operational input

The platform can produce a CBOM or structured data intended for downstream orchestration.

### 4.4 Strategy-to-remediation pipeline

The documented lifecycle is:

```text
Discover
   ↓
Inventory
   ↓
Understand risk
   ↓
Build strategy
   ↓
Build roadmap
   ↓
Connect tools / partners
   ↓
Remediate
```

### 4.5 Deployment flexibility

QryptoCyber describes:

- on-premise;
- private cloud;
- SaaS;
- custom deployments.

That is important for government, regulated and sensitive environments.

## What ECDAT-X should learn

**Absorb:**

- five-pillar enterprise discovery model;
- database encryption visibility;
- AI-assisted inventory analysis;
- structured remediation output;
- deployment flexibility.

**Improve:**

ECDAT-X should make the AI's reasoning explicitly evidence-grounded:

```text
AI conclusion
   ↓
supporting observations
   ↓
confidence
   ↓
contradictions
   ↓
recommended next investigation
```

That prevents an AI analyst from becoming a black-box scoring engine.

---

# 5. DigiCert Quantum Central

## Official resource

- [DigiCert — Quantum Central](https://www.digicert.com/news/digicert-introduces-quantum-central)

## Launch

DigiCert announced Quantum Central on **1 July 2026**.

## What it has advanced

### 5.1 Discovery + action

Quantum Central combines:

- cryptographic discovery;
- inventory;
- quantum-vulnerability identification;
- remediation prioritization;
- change requests;
- migration tracking;
- readiness measurement.

### 5.2 Jira integration

The product explicitly supports planning and tracking PQC migration activities through Jira integration.

This is a valuable lesson:

> A security platform should connect findings to the organization's existing execution system.

### 5.3 Roadmap orientation

DigiCert does not stop at saying:

> "This RSA key is quantum-vulnerable."

It moves toward:

> "This asset needs an action, this is the migration process, and this is the organization's progress."

## What ECDAT-X should learn

**Absorb:**

- change-request generation;
- Jira/workflow integration;
- migration progress tracking;
- readiness dashboards.

**Improve:**

ECDAT-X can make the change request richer:

```text
Finding
  ↓
Evidence
  ↓
Dependency graph
  ↓
Predicted blast radius
  ↓
Migration alternatives
  ↓
Benchmark evidence
  ↓
Required tests
  ↓
Rollback plan
  ↓
Verification requirements
  ↓
Change ticket
```

---

# 6. QuSecure

## Official resources

- [QuSecure — Cryptographic Discovery & Inventory](https://www.qusecure.com/quprotect/cryptographic-discovery-and-inventory/)
- [QuSecure — QuProtect](https://www.qusecure.com/quprotect/)
- [QuSecure — Crypto Agility](https://www.qusecure.com/cryptographic-agility-crypto-agility/)

## What QuSecure has advanced

QuSecure is particularly important because it pushes the ecosystem from **discovery into active crypto-agility**.

### 6.1 Continuous cryptographic inventory

QuSecure describes discovery as a continuous capability rather than a one-time project.

### 6.2 Agentless discovery

Its public documentation describes discovery across:

- routers;
- servers;
- endpoints;
- applications;
- cloud;
- network infrastructure.

### 6.3 Algorithm-level identification

The documented scope includes:

- algorithm;
- key size;
- certificate metadata;
- deprecated usage;
- out-of-policy usage.

### 6.4 Recon → Resilience → Reporting

QuSecure describes a three-part operating model:

```text
RECON
cryptographic discovery
      ↓
RESILIENCE
crypto-agility orchestration
      ↓
REPORTING
continuous assurance
```

### 6.5 Runtime crypto-agility

QuSecure describes capabilities involving:

- modular algorithm substitution;
- hybrid post-quantum cryptography;
- dynamic cipher-suite negotiation;
- CI/CD integration;
- infrastructure-as-code;
- policy enforcement.

### 6.6 Network-layer protection

QuProtect R3 is positioned as a software-only PQC platform that can protect cryptographic communication at the network layer and produce CBOM evidence.

## What ECDAT-X should learn

This competitor provides one of the strongest arguments for adding a **state-transition execution layer** to ECDAT.

**Absorb:**

- continuous inventory;
- agentless discovery;
- runtime crypto-agility;
- policy enforcement;
- network-layer protection;
- orchestration;
- CI/CD integration.

**Go deeper:**

ECDAT-X should ask:

> "If I change this algorithm, can I prove that the system remained secure?"

That leads directly to:

- migration simulation;
- interoperability tests;
- security-property verification;
- rollback verification;
- downgrade testing;
- chaos experiments.

---

# 7. IBM — CBOM ecosystem

## Official resources

- [IBM CBOM GitHub](https://github.com/IBM/CBOM)
- [CycloneDX](https://cyclonedx.org/)

## Why IBM matters

IBM has contributed substantially to the **Cryptography Bill of Materials** ecosystem.

IBM's CBOM work was upstreamed into CycloneDX 1.6.

### 7.1 CBOMkit

IBM documents an open-source CBOM toolkit.

### 7.2 Source-code cryptography detection

The ecosystem includes a SonarQube-oriented cryptography plugin capable of detecting cryptographic assets in source code and generating CBOM.

### 7.3 CBOM visualization

CBOM Viewer provides visualization and statistics over CBOM artifacts.

### 7.4 Container/image discovery

CBOMkit-theia is designed to detect cryptographic assets in container images and directories and generate CBOMs.

### 7.5 GitHub Actions

CBOMkit-action integrates CBOM generation into GitHub workflows.

This is particularly valuable because it turns CBOM from a standalone audit artifact into a development lifecycle object.

## What ECDAT-X should learn

**Absorb directly:**

- CycloneDX interoperability;
- CBOM generation;
- source scanning;
- container scanning;
- GitHub Actions;
- visualization;
- developer workflow integration.

**Do not rebuild the standard unnecessarily.**

ECDAT-X should treat CBOM as:

```text
external interoperability format
```

while maintaining a richer internal model:

```text
Evidence
Observation
Claim
Asset
System
Dependency
Trust
SecurityProperty
Event
Migration
Experiment
Decision
Outcome
```

This matches the ECDAT-X dossier's proposed internal graph.

---

# 8. ISARA Advance

## Official resource

- [ISARA Advance](https://www.isara.com/products/isara-advance-cryptographic-inventory-and-risk-assessment-tool.html)

## What ISARA has advanced

### 8.1 Agentless-first enterprise discovery

ISARA describes real-time cryptographic inventory across:

- cloud;
- on-premise;
- hybrid environments.

### 8.2 Discovery → Assess → Prepare

The platform is organized around:

```text
DISCOVER
   ↓
ASSESS
   ↓
PREPARE
```

### 8.3 Risk scoring

The platform emphasizes:

- cryptographic mapping;
- posture scoring;
- risk insights;
- prioritized remediation.

### 8.4 Enterprise practicality

ISARA emphasizes integration and operation without requiring agents or constant data transmission.

## What ECDAT-X should learn

- agentless discovery should be a first-class mode;
- government deployments may require offline/controlled environments;
- discovery must produce actionable priorities;
- deployment architecture matters as much as detection algorithms.

---

# 9. PQStation / QVision

## Official resource

- [PQStation — QVision](https://www.pqstation.com/qvision)

## What it has advanced

QVision describes a layered cryptographic inventory model.

### 9.1 Five-layer inventory

The public product description uses layers around:

```text
Services
   ↓
Components
   ↓
Touchpoints
   ↓
Assets
   ↓
Primitives
```

This is valuable because it prevents the inventory from becoming a flat table.

### 9.2 Continuous discovery

The platform describes discovery of:

- algorithms;
- keys;
- certificates;
- protocols.

### 9.3 Migration ordering

QVision associates discovery with risk and migration ordering.

### 9.4 Legacy-system bridge

PQStation's QSTunnel concept is especially interesting.

The idea is to place a cryptographic-agility layer around legacy systems that cannot themselves immediately support PQC.

This is a practical architecture for:

- legacy appliances;
- IoT;
- VPNs;
- site-to-site communication;
- systems with difficult upgrade paths.

## What ECDAT-X should learn

Add a **Legacy Crypto Transition Gateway** concept to the architecture.

But make it graph-aware:

```text
Legacy System
      ↓
Gateway / Adapter
      ↓
Hybrid / PQC Boundary
      ↓
Modern System
```

ECDAT should understand the gateway as part of the migration graph and calculate whether it introduces a new trust boundary or attack surface.

---

# 10. Encryption Consulting / CBOM Secure

## Official resource

- [Encryption Consulting — Cryptographic Inventory](https://www.encryptionconsulting.com/solutions/cryptographic-inventory/)

## Advancements

### 10.1 Cryptographic inventory

The ecosystem covers:

- certificates;
- keys;
- algorithms;
- CBOM.

### 10.2 Rogue-asset detection

Rogue or unmanaged cryptographic assets are treated as an explicit discovery problem.

This is important because enterprise cryptography frequently exists outside officially approved systems.

### 10.3 Compliance mapping

Cryptographic findings can be mapped to compliance and policy gaps.

### 10.4 Relationship-oriented CBOM

Public material around the company's cryptographic inventory work also emphasizes relationships between cryptographic objects and services.

## ECDAT-X lesson

Add explicit asset states:

```text
KNOWN
UNKNOWN
SHADOW
ROGUE
ORPHANED
DUPLICATE
CONFLICTING
UNVERIFIED
```

A cryptographic asset should not simply be "found" or "not found".

---

# 11. AppViewX Quantum Trust Hub

## Official resources

- [AppViewX — Quantum Trust Hub](https://docs.appviewx.com/Sandbox/quantum_trust_hub.html)
- [AppViewX — Platform documentation](https://docs.appviewx.com/2026.2.0/oxy_ex/appviewx_s_qth.html)

## What it has advanced

### 11.1 Unified dashboard

The platform combines:

- dashboards;
- inventories;
- policies.

### 11.2 Direct vs dependency-based code discovery

Its code inventory distinguishes:

- direct cryptographic usage;
- cryptographic dependencies.

This is a very useful modeling distinction.

### 11.3 Source-level traceability

The documented inventory contains information such as:

- repository;
- file path;
- class;
- method;
- language;
- line number;
- crypto category.

### 11.4 Custom library support

Organizations can upload custom libraries for scanning.

This addresses a real weakness of signature-based scanners: proprietary implementations may not resemble well-known libraries.

### 11.5 Certificate PQC risk fields

The certificate inventory adds PQC-oriented risk severity.

### 11.6 Policy module

Organizations can define custom quantum-safety policies.

## ECDAT-X lesson

Source findings should retain exact evidence:

```text
repository
→ file
→ line
→ symbol
→ API
→ parameter
→ library
→ algorithm
→ runtime evidence
```

And the platform should permit **custom detectors**.

---

# 12. Fortanix

## Official resource

- [Fortanix — Post-Quantum Cryptography](https://www.fortanix.com/solutions/use-case/post-quantum-cryptography)

## What Fortanix has advanced

Fortanix approaches PQC from the perspective of **keys + data services + cryptographic infrastructure**.

### 12.1 Multi-environment key inventory

The public product description includes:

- multi-cloud;
- multi-geography;
- on-premises.

### 12.2 Key usage visibility

It emphasizes understanding:

- where keys are;
- key status;
- key usage;
- critical data services.

### 12.3 Risk visualization

The product uses dashboards and heat maps to prioritize high-risk assets.

### 12.4 Transition support

The architecture goes from:

```text
Discover
   ↓
PQC Assessment
   ↓
PQC Transition
```

## ECDAT-X lesson

Do not model cryptography separately from data.

Add:

```text
Data Asset
   ↓ protected by
Cryptographic Asset
   ↓ implemented by
Crypto Component
   ↓ deployed in
System
   ↓ supporting
Business Service
```

This makes HNDL and business impact substantially more meaningful.

---

# 13. Forescout

## Relevant ecosystem resource

- Microsoft Security Blog — cryptographic inventory / ecosystem discussion:
  https://www.microsoft.com/en-us/security/blog/2026/04/16/building-your-cryptographic-inventory-a-customer-strategy-for-cryptographic-posture-management/

## Advancement

Forescout is important on the **network and cyber-asset visibility** side.

The ecosystem demonstrates how cryptographic posture can be correlated with:

- network communication;
- IT;
- IoT;
- OT;
- application/protocol context;
- geographic context;
- security posture.

## ECDAT-X lesson

A cryptographic inventory should not be isolated from:

```text
Network topology
+
Asset identity
+
Protocol
+
Device type
+
IT/OT classification
+
Business context
```

This is especially important for government and critical infrastructure environments.

---

# 14. SandboxAQ

## Official resource

- [SandboxAQ — Transitioning to a Post-RSA World](https://www.sandboxaq.com/post/transitioning-to-a-post-rsa-world)

## What SandboxAQ has advanced

### 14.1 Crypto-agility strategy

SandboxAQ has positioned crypto-agility as a central part of quantum migration.

### 14.2 AI / ML-assisted cryptographic analysis

Public conference material has described ML-enriched cryptographic inventories and efforts to reduce false positives in software/container analysis.

This is strategically important:

> Discovery quality matters as much as discovery coverage.

A scanner that finds everything but produces massive false positives can become operationally unusable.

## ECDAT-X lesson

Create an explicit:

### Evidence Confidence Engine

For every finding:

```text
Detection
  ↓
Evidence quality
  ↓
Cross-source agreement
  ↓
Confidence
  ↓
Contradiction check
  ↓
Final claim
```

---

# 15. PostQ Software Labs — India

## Official resources

- [PostQ Software Labs](https://postqsoftwarelabs.com/)
- [PostQ Products](https://postqsoftwarelabs.com/products.html)
- [PostQ Code Scan — August 2026 announcement](https://postqsoftwarelabs.com/announcement-2026-08-14-code-scan.html)

## Why PostQ matters

PostQ is particularly relevant to ECDAT because it is an Indian company building directly around cryptographic discovery and PQC migration.

## 15.1 Developer-native discovery

PostQ Code Scanner is described for:

- VS Code;
- Eclipse;
- CLI;
- containers;
- CI/CD;
- standalone reporting.

### 15.2 Multi-language analysis

The public documentation describes:

- cryptographic API detection;
- library identification;
- algorithm identification;
- usage analysis.

### 15.3 Parameter intelligence

PostQ explicitly mentions analysis of:

- key sizes;
- modes;
- curves;
- padding;
- security-relevant parameters.

### 15.4 Source evidence

PostQ preserves:

- file;
- line;
- API;
- parameter;
- related-call evidence.

### 15.5 Multi-dimensional assessment

The platform describes analysis involving:

- PQC readiness;
- CWE-linked misuse;
- FIPS signals;
- crypto-agility;
- cryptographic risk.

### 15.6 Scan-to-scan comparison

The product also describes comparing changes between scans and tracking remediation.

## ECDAT-X lesson

ECDAT-X needs a **developer-facing mode**, not only a CISO dashboard.

Potential workflow:

```text
Developer changes crypto
       ↓
ECDAT Crypto PR Guard
       ↓
Static analysis
       ↓
Dependency analysis
       ↓
Policy check
       ↓
PQC impact
       ↓
CBOM diff
       ↓
Migration impact
       ↓
Security-property tests
       ↓
ALLOW / WARN / BLOCK
```

---

# 16. CipherIQ

## Official resources

- [CipherIQ CBOM Generator](https://docs.cipheriq.io/cbom-generator/)
- [CipherIQ Asset Discovery](https://docs.cipheriq.io/cbom-generator/features/asset-discovery/)

## What CipherIQ has advanced

### 16.1 Multiple scanner strategies

The documented generator uses scanner categories for:

- certificates;
- keys;
- packages;
- services;
- filesystem;
- applications;
- libraries;
- algorithms.

### 16.2 Binary/application analysis

Application scanning can identify cryptographic dependencies.

### 16.3 Dependency graph

The product describes relationships among:

- services;
- protocols;
- algorithms.

### 16.4 PQC readiness

It provides PQC readiness assessment.

### 16.5 Privacy-by-default

The documentation describes redaction of:

- hostnames;
- paths;
- usernames.

### 16.6 High-performance implementation

CipherIQ states that its C11 multithreaded implementation can scan more than 12,000 files/minute. This is **vendor-reported** and should be independently benchmarked.

### 16.7 CycloneDX output

The tool supports CycloneDX CBOM output.

## ECDAT-X lesson

Two important ideas:

1. **scanner modularity**;
2. **privacy-preserving local analysis**.

ECDAT should support a local collector architecture in which sensitive source material does not have to leave the enterprise.

---

# 17. Qubrisk

## Official resource

- [Qubrisk](https://qubrisk.com/)

## What Qubrisk has advanced

Qubrisk is particularly interesting because it combines inventory with **continuous developer workflow control**.

### 17.1 Local-first scanning

It describes scanning source and configuration without uploading source code.

### 17.2 Deterministic asset IDs

Deterministic identifiers help maintain identity across repeated scans.

### 17.3 Redacted evidence

The platform emphasizes retaining useful evidence without exposing sensitive source material.

### 17.4 Versioned CBOM

It describes versioned CycloneDX CBOM generation.

### 17.5 Ownership routing

Assets/findings can be associated with owners.

### 17.6 Migration work objects

The public platform describes connecting assets to:

- owner;
- dependency;
- deadline;
- test plan.

### 17.7 Pull-request drift control

This is one of the most useful modern ideas:

> detect cryptographic regressions at code-change time rather than discovering them months later.

### 17.8 Policy as code

Qubrisk describes policy gates for:

- severity;
- exceptions;
- baselines.

## ECDAT-X lesson

ECDAT should have:

### Crypto Drift Guard

```text
Known-safe state
       ↓
new commit
       ↓
crypto diff
       ↓
new asset?
changed algorithm?
changed parameter?
changed dependency?
changed trust?
       ↓
policy evaluation
       ↓
security-property evaluation
       ↓
PR decision
```

---

# 18. Entrust

## Official resources

- [Entrust — Cryptographic Security Platform](https://www.entrust.com/products/cryptographic-security-platform)
- [Entrust — Post-Quantum Cryptography](https://www.entrust.com/solutions/post-quantum-cryptography)
- [Entrust — Cryptographic Posture Management](https://www.entrust.com/blog/2026/04/from-inventory-to-control-turning-cryptographic-visibility-into-action)

## What Entrust has advanced

Entrust approaches the problem from the **trust infrastructure** side.

### 18.1 PKI + HSM + keys + certificates

Its Cryptographic Security Platform is designed to unify:

- PKI;
- HSMs;
- keys;
- certificates;
- secrets lifecycle management.

### 18.2 Lifecycle automation

The platform emphasizes:

- discovery;
- renewal;
- policy enforcement;
- lifecycle management.

### 18.3 Crypto-agility

Entrust explicitly connects cryptographic inventory to crypto-agility.

### 18.4 Cryptographic Center of Excellence

Entrust describes a Cryptographic Center of Excellence for moving from awareness to action and for identifying, inventorying and prioritizing cryptographic assets and data.

## ECDAT-X lesson

Trust infrastructure must be a graph, not a flat inventory.

Model:

```text
Certificate
   ↓ issued by
CA
   ↓ anchored by
Trust Anchor
   ↓ trusted by
Verifier
   ↓ authenticates
Service
   ↓ protects
Data
```

This becomes critical during PQC migration.

---

# 19. Sectigo Quantum Ready

## Official resources

- [Sectigo Quantum Ready](https://www.sectigo.com/resource-library/sectigo-introduces-sectigo-quantum-ready-qspm)
- [Sectigo Quantum Ready — product discussion](https://www.sectigo.com/blog/sectigo-quantum-ready-post-quantum-readiness/)

## Launch

Sectigo announced Quantum Ready on **17 September 2026**.

## Advancements

The product explicitly combines:

- cryptographic asset discovery;
- dependency mapping;
- quantum-risk assessment;
- PQC migration planning;
- crypto-agility.

This demonstrates that cryptographic inventory is rapidly becoming a dedicated enterprise posture-management category.

## ECDAT-X lesson

The basic product category is becoming crowded.

Therefore the ECDAT differentiator must move toward:

- evidence;
- verification;
- state transition;
- uncertainty;
- simulation;
- causal monitoring.

---

# 20. Thales

## Official resources

- [Thales — Post-Quantum Crypto Agility](https://cpl.thalesgroup.com/encryption/post-quantum-crypto-agility)
- [Thales — Cryptographic Inventory white paper](https://cpl.thalesgroup.com/sites/default/files/content/white-paper/cryptographic-inventory-quantum-readiness-wp.pdf)

## What Thales contributes

Thales connects cryptographic inventory to a broader cryptographic infrastructure ecosystem involving:

- cryptographic agility;
- HSMs;
- PQC;
- QKD;
- QRNG;
- enterprise security.

### Important lesson

Migration cannot be modeled only at the software-algorithm level.

Real enterprises may have:

```text
Software
+
HSM
+
PKI
+
Hardware
+
Randomness
+
Network
+
Certificates
+
Keys
```

ECDAT-X should therefore maintain a hardware/trust-infrastructure layer.

---

# 21. ReversingLabs

## Official resources

- [ReversingLabs — CycloneDX xBOM](https://www.reversinglabs.com/press-releases/reversinglabs-delivers-most-comprehensive-support-for-cyclonedx-xbom)
- [Spectra Assure release notes](https://docs.secure.software/portal/release-notes)

## What it has advanced

ReversingLabs expands the CBOM concept into broader software-supply-chain visibility.

### 21.1 xBOM approach

Public documentation describes support for:

- SBOM;
- CBOM;
- SaaSBOM;
- ML-BOM.

### 21.2 Compiled software visibility

The platform targets packaged/compiled software rather than only source repositories.

This is important because production artifacts can differ from source assumptions.

### ECDAT-X lesson

Use:

```text
Source
  +
Build
  +
Binary
  +
Container
  +
Deployment
```

and reconcile them.

This supports a crucial ECDAT-X question:

> "Does the cryptography declared in source code actually match the cryptography present in the deployed artifact?"

---

# 22. NetRise and embedded/firmware ecosystem

## Ecosystem role

NetRise and similar software/firmware supply-chain platforms are important for environments where cryptography is hidden inside:

- firmware;
- embedded systems;
- IoT;
- device images;
- vendor appliances.

## ECDAT-X lesson

The cryptographic discovery architecture should eventually include:

```text
Firmware
   ↓
Binary
   ↓
Library
   ↓
Crypto implementation
   ↓
Algorithm
   ↓
Device
   ↓
Network relationship
```

This is particularly important for OT and critical infrastructure.

---

# 23. Microsoft ecosystem

## Reference

- [Microsoft Security Blog — Building Your Cryptographic Inventory](https://www.microsoft.com/en-us/security/blog/2026/04/16/building-your-cryptographic-inventory-a-customer-strategy-for-cryptographic-posture-management/)

Microsoft is important less as a standalone CBOM vendor and more as a **large enterprise ecosystem reference point**.

The Microsoft discussion frames cryptographic inventory as foundational to quantum readiness and discusses ecosystem solutions involving cryptographic posture.

## ECDAT-X lesson

Interoperability should be designed from the beginning.

ECDAT should be able to ingest/export:

- CBOM;
- SBOM;
- SARIF;
- JSON;
- CSV;
- policy artifacts;
- evidence records;
- ticketing records.

---

# 24. Open-source CBOM / CycloneDX ecosystem

## References

- [IBM CBOM repository](https://github.com/IBM/CBOM)
- [CycloneDX](https://cyclonedx.org/)
- [CycloneDX Tool Center](https://cyclonedx.org/tool-center/)

The open-source ecosystem is extremely important.

The ecosystem includes tools and projects covering:

- CBOM generation;
- source scanning;
- TLS analysis;
- SSH auditing;
- container scanning;
- binary analysis;
- SBOM/xBOM generation;
- visualization;
- CI/CD integration.

## Major lesson

**Do not build every scanner from scratch.**

ECDAT-X should have a collector/plugin architecture:

```text
Collector SDK
     ↓
normalized observation
     ↓
evidence object
     ↓
entity resolution
     ↓
reality graph
```

A scanner becomes replaceable.

The graph and reasoning system become the durable intellectual core.

---

# 25. NIST migration ecosystem

## Official resources

- [NIST NCCoE — Migration to Post-Quantum Cryptography](https://www.nccoe.nist.gov/applied-cryptography/migration-to-pqc)
- [NIST CSWP 39-upd1 — Crypto Agility](https://csrc.nist.gov/pubs/cswp/39/upd1/considerations-for-achieving-crypto-agility/final)

NIST is not a competitor. It is a foundational reference ecosystem.

## Important advancements

NIST's current migration work explicitly separates:

### Cryptographic visibility and risk management

from

### Interoperability and benchmarking

This is an important architecture clue.

A serious migration platform needs both.

```text
DISCOVERY / RISK
        +
INTEROPERABILITY / BENCHMARKING
        ↓
MIGRATION DECISION
```

NIST's crypto-agility work also makes adaptability an architectural objective rather than merely a product feature.

## ECDAT-X lesson

The benchmark laboratory in the ECDAT-X plan is therefore not optional decoration.

It should become part of migration reasoning.

---

# 26. IETF CADI ecosystem

## Reference

- IETF Internet-Draft: Cryptographic Asset Discovery and Inventory (CADI)

CADI is important because it formalizes the idea that cryptographic discovery needs multiple evidence sources.

The research direction includes discovery methods involving:

- CBOM declarations;
- SAST;
- binaries/images;
- simulated handshakes;
- traffic analysis;
- process identification;
- configuration extraction.

## ECDAT-X lesson

This validates the multi-modal collector architecture:

```text
SOURCE
AST
BINARY
CONTAINER
RUNTIME
NETWORK
CERTIFICATE
CLOUD
HARDWARE
FIRMWARE
```

But ECDAT-X should go one step further by making the evidence fusion itself a research object.

---

# 27. Network observability gap

Recent IETF work on PQC-readiness gaps highlights a practical limitation:

Traditional network telemetry does not necessarily provide structured cryptographic inventory at enterprise scale.

Even when network communication can be observed, an organization may still lack:

- session-level algorithm history;
- downgrade outcomes;
- negotiated cryptographic state;
- relationship between endpoint identity and cryptographic usage.

## ECDAT-X opportunity

Build a:

### Cryptographic Session Intelligence Layer

```text
Endpoint A
    ↓
Connection
    ↓
Protocol
    ↓
Handshake
    ↓
Negotiated algorithm
    ↓
Certificate / key exchange
    ↓
Outcome
    ↓
Downgrade / fallback status
```

This becomes temporal evidence rather than static configuration.

---

# 28. Academic and research direction: graph-based migration

Recent research explores dependency-aware and graph-based PQC migration planning.

This is strongly aligned with ECDAT-X.

Instead of:

```text
Asset A → migrate
Asset B → migrate
Asset C → migrate
```

model:

```text
Application
 ├── Service
 │    ├── Library
 │    ├── Protocol
 │    └── Certificate
 ├── Database
 │    └── Encryption Key
 └── External API
      └── Trust relationship
```

Then migration becomes a graph optimization problem.

## ECDAT-X extension

For every proposed migration:

```text
Candidate change
       ↓
affected subgraph
       ↓
blast radius
       ↓
compatibility constraints
       ↓
benchmark constraints
       ↓
security invariants
       ↓
rollback options
       ↓
expected disruption
```

---

# 29. What the strongest ecosystem advancements have in common

Across all the products and research directions, several patterns repeatedly appear.

## 29.1 Discovery is becoming continuous

Old:

```text
scan once
```

New:

```text
observe continuously
```

## 29.2 Inventory is becoming contextual

Old:

```text
RSA-2048
```

New:

```text
RSA-2048
→ service
→ owner
→ dependency
→ data
→ business criticality
→ trust relationship
→ usage
→ exposure
```

## 29.3 CBOM is becoming an interoperability layer

CBOM should not necessarily be the entire internal data model.

ECDAT-X should maintain a richer graph and export CBOM when required.

## 29.4 Remediation is becoming operational

Modern products increasingly connect findings to:

- Jira;
- ServiceNow;
- CI/CD;
- policy engines;
- infrastructure-as-code;
- remediation workflows.

## 29.5 Crypto-agility is becoming the end goal

Inventory is increasingly understood as the foundation for the ability to change cryptography safely.

---

# 30. Competitive capability extraction for ECDAT-X

The following should be considered **capabilities to absorb from the ecosystem**.

## Tier A — Must absorb

### A1. Continuous inventory
Inspired strongly by Keyfactor and QuSecure.

### A2. Enterprise multi-surface discovery
Source + binary + container + runtime + network + cloud + certificates + hardware.

### A3. CBOM interoperability
IBM / CycloneDX ecosystem.

### A4. Source-level evidence
AppViewX and PostQ.

### A5. Dependency-aware inventory
Keyfactor, AppViewX, CipherIQ and graph research.

### A6. Ownership
Keyfactor, Qubrisk, enterprise CPM systems.

### A7. Policy enforcement
Keyfactor, AppViewX, Qubrisk.

### A8. CI/CD integration
IBM, PostQ, Qubrisk.

### A9. Migration workflow
DigiCert, QryptoCyber, Sectigo.

### A10. Crypto-agility execution
QuSecure, Keyfactor, Entrust.

---

# 31. Tier B — Strong differentiators to integrate

## B1. Evidence-backed cryptographic reality

Every claim should have:

```text
Observation
Source
Timestamp
Collector
Evidence location
Confidence
Freshness
```

## B2. Contradiction engine

If:

```text
Source says RSA
Binary says ECC
Runtime says ML-KEM hybrid
```

do not silently choose one.

Create:

```text
CONFLICT
```

and investigate.

## B3. Epistemic states

Each claim should have a state such as:

```text
DECLARED
OBSERVED
INFERRED
CORROBORATED
VERIFIED
CONFLICTING
UNKNOWN
STALE
```

## B4. Temporal cryptographic state

Track:

```text
t0 → RSA
t1 → RSA + hybrid
t2 → hybrid
t3 → PQC
t4 → unexpected RSA regression
```

## B5. Causal drift analysis

Do not merely say:

> "RSA appeared again."

Ask:

> "Which deployment, dependency, configuration or rollback caused RSA to reappear?"

---

# 32. Tier C — Research-grade differentiators

These ideas already exist in the ECDAT-X research plan and should be treated as experimental research rather than guaranteed product features.

## C1. Security Property Compiler

Translate high-level requirements into verifiable conditions.

Example:

```text
Requirement:
"Authentication must remain PQ-safe."

        ↓

Generated checks:
- PQ-capable signature path
- valid trust chain
- PQ evidence outcome-bearing
- no classical-only fallback
- downgrade resistance
```

## C2. Crypto Agility Reverse Proof

Instead of saying:

> "The architecture appears crypto-agile."

attempt to demonstrate it.

```text
algorithm substitution
        ↓
tests
        ↓
interoperability
        ↓
security-property verification
        ↓
rollback
        ↓
evidence
```

## C3. Unknown Dependency Hunter

Before migration:

```text
"What might break that our inventory does not know about?"
```

Use:

- graph expansion;
- configuration analysis;
- runtime traces;
- network observations;
- dependency inference;
- controlled experiments.

## C4. Probabilistic migration simulation

Represent uncertain dependencies probabilistically.

Example:

```text
Service A
 ├── depends on Library X: 0.98
 ├── depends on Legacy API: 0.42
 └── hidden appliance dependency: 0.17
```

Then simulate migration outcomes.

## C5. Cryptographic chaos engineering

Intentionally test:

- algorithm removal;
- certificate rotation;
- trust-anchor replacement;
- cipher restriction;
- fallback suppression;
- hybrid negotiation failure;
- latency increase;
- packet-size stress.

The objective is to discover hidden dependencies before production discovers them for you.

## C6. Information-gain-driven discovery

Instead of scanning everything equally:

```text
Unknown
  ↓
choose next observation
  ↓
maximize uncertainty reduction
  ↓
update graph
  ↓
choose next observation
```

This can become an optimization problem.

## C7. Cryptographic digital twin

Create a machine-readable model capable of asking:

> "What happens if this cryptographic dependency changes?"

before making the real change.

---

# 33. The biggest lesson: competitors are building pieces of the future ECDAT

A useful mental model is:

```text
                     CRYPTOGRAPHIC ENTERPRISE

       ┌────────────── DISCOVERY ──────────────┐
       │ Keyfactor                              │
       │ QryptoCyber                            │
       │ QuSecure                               │
       │ ISARA                                  │
       │ AppViewX                               │
       │ CipherIQ                               │
       └────────────────────────────────────────┘

       ┌────────────── CBOM / DATA ────────────┐
       │ IBM / CycloneDX                        │
       │ ReversingLabs                          │
       │ Qubrisk                                │
       │ CipherIQ                               │
       └────────────────────────────────────────┘

       ┌────────────── CODE ───────────────────┐
       │ IBM                                    │
       │ PostQ                                  │
       │ AppViewX                               │
       └────────────────────────────────────────┘

       ┌────────────── NETWORK ─────────────────┐
       │ Keyfactor                              │
       │ QuSecure                               │
       │ QryptoCyber                            │
       │ Forescout                              │
       └────────────────────────────────────────┘

       ┌────────────── TRUST ───────────────────┐
       │ DigiCert                               │
       │ Entrust                                │
       │ Sectigo                                │
       │ Thales                                 │
       │ AppViewX                               │
       └────────────────────────────────────────┘

       ┌────────────── KEYS / DATA ─────────────┐
       │ Fortanix                               │
       │ Entrust                                │
       │ Thales                                 │
       └────────────────────────────────────────┘

       ┌────────────── ORCHESTRATION ───────────┐
       │ QuSecure                               │
       │ Keyfactor                              │
       │ Entrust                                │
       └────────────────────────────────────────┘

       ┌────────────── AI ──────────────────────┐
       │ QryptoCyber                            │
       │ SandboxAQ                              │
       └────────────────────────────────────────┘

       ┌────────────── CI / DRIFT ──────────────┐
       │ Qubrisk                                │
       │ PostQ                                  │
       │ IBM                                    │
       └────────────────────────────────────────┘

       ┌────────────── RESEARCH FRONTIER ───────┐
       │ uncertainty                            │
       │ causal drift                           │
       │ migration simulation                   │
       │ security-property verification         │
       │ cryptographic digital twin             │
       │ chaos engineering                      │
       │ information-gain discovery              │
       └────────────────────────────────────────┘
```

The ECDAT-X opportunity is to connect these layers into one evidence-backed reasoning loop.

---

# 34. Exact advancements ECDAT-X should take from each ecosystem

| Source | Advancement to absorb | ECDAT-X implementation direction |
|---|---|---|
| Keyfactor | Continuous inventory | Continuous collectors + temporal graph |
| Keyfactor | Sensors | Collector SDK |
| Keyfactor | Ownership/dependency context | Entity-resolution graph |
| Keyfactor | Policy-driven crypto | Policy-as-code |
| QryptoCyber | Five-pillar discovery | External/internal/IT/db/code coverage |
| QryptoCyber | AI inventory | Evidence-grounded analyst |
| DigiCert | Change requests | Migration work objects |
| DigiCert | Jira tracking | Workflow connectors |
| QuSecure | Continuous discovery | Streaming inventory |
| QuSecure | Crypto-agility orchestration | State-transition engine |
| QuSecure | Runtime negotiation | Session-level telemetry |
| IBM | CBOM | CycloneDX interoperability |
| IBM | Source analysis | Code collector |
| IBM | Container analysis | Container collector |
| IBM | GitHub Actions | CI/CD integration |
| ISARA | Agentless discovery | Agentless collection mode |
| PQStation | Layered inventory | Service → component → touchpoint → asset → primitive |
| PQStation | Legacy gateway | Migration boundary/gateway model |
| Encryption Consulting | Rogue assets | Shadow/rogue/orphan classification |
| AppViewX | Direct vs dependency usage | PROVIDES vs CONSUMES model |
| AppViewX | Source evidence | line-level evidence |
| AppViewX | Custom libraries | detector plugin system |
| Fortanix | Key/data relationship | data-protection graph |
| Forescout | IT/OT/network context | infrastructure graph |
| SandboxAQ | ML false-positive reduction | evidence confidence engine |
| PostQ | Developer-native code analysis | Crypto PR Guard |
| PostQ | parameter analysis | algorithm parameter graph |
| CipherIQ | modular scanners | collector architecture |
| CipherIQ | local privacy | local-first deployment |
| Qubrisk | deterministic IDs | stable asset identity |
| Qubrisk | PR drift | cryptographic regression gate |
| Qubrisk | policy-as-code | signed policy bundles |
| Entrust | PKI/HSM lifecycle | trust infrastructure graph |
| Sectigo | QSPM workflow | continuous quantum posture |
| Thales | hardware/HSM/QKD/QRNG | infrastructure/hardware layer |
| ReversingLabs | compiled artifact CBOM | source-build-binary reconciliation |
| NIST | visibility + benchmarking | discovery + migration lab |
| IETF CADI | multi-method discovery | evidence fusion |
| Network research | session observability | negotiated-state history |
| Graph research | dependency optimization | migration solver |

---

# 35. What ECDAT-X should NOT do

Competitive research is also useful for identifying traps.

## Do not build:

### 35.1 Yet another flat CBOM dashboard

CBOM generation is already well covered.

### 35.2 Yet another certificate scanner

Certificate discovery is a mature capability.

### 35.3 Yet another generic quantum risk score

A single score without evidence and context is weak.

### 35.4 Yet another static source scanner

IBM, AppViewX, PostQ and others already occupy this space.

### 35.5 Yet another AI chatbot

An AI analyst is useful only if it can cite:

- observations;
- evidence;
- graph relationships;
- uncertainty;
- decisions.

### 35.6 A giant collection of disconnected scanners

The moat should not be:

> "We have 27 scanners."

It should be:

> "We can reconcile observations from many scanners into one trustworthy model of cryptographic reality."

---

# 36. ECDAT-X proposed architecture after competitive research

```text
                         ┌──────────────────────────┐
                         │       COLLECTORS         │
                         ├──────────────────────────┤
                         │ Source / AST              │
                         │ Binary                    │
                         │ Container                 │
                         │ Runtime                   │
                         │ Network                   │
                         │ Certificate               │
                         │ Cloud                     │
                         │ KMS / HSM                 │
                         │ Hardware / Firmware       │
                         └────────────┬─────────────┘
                                      ↓
                         ┌──────────────────────────┐
                         │     EVIDENCE ENGINE      │
                         ├──────────────────────────┤
                         │ provenance                │
                         │ timestamp                 │
                         │ confidence                │
                         │ freshness                 │
                         │ contradiction             │
                         │ evidence location         │
                         └────────────┬─────────────┘
                                      ↓
                         ┌──────────────────────────┐
                         │    ENTITY RESOLUTION     │
                         ├──────────────────────────┤
                         │ asset identity            │
                         │ system identity           │
                         │ owner mapping             │
                         │ duplicate resolution     │
                         └────────────┬─────────────┘
                                      ↓
                 ┌────────────────────────────────────────┐
                 │       CRYPTOGRAPHIC REALITY GRAPH      │
                 ├────────────────────────────────────────┤
                 │ crypto graph                            │
                 │ dependency graph                        │
                 │ trust graph                             │
                 │ data lineage                            │
                 │ temporal graph                          │
                 │ business graph                          │
                 └───────────────┬────────────────────────┘
                                 ↓
              ┌─────────────────────────────────────────────┐
              │               REASONING                      │
              ├─────────────────────────────────────────────┤
              │ quantum risk                                 │
              │ HNDL risk                                    │
              │ business risk                                │
              │ implementation risk                          │
              │ systemic concentration                       │
              │ uncertainty                                  │
              │ causal drift                                 │
              └────────────────┬────────────────────────────┘
                               ↓
              ┌─────────────────────────────────────────────┐
              │          MIGRATION INTELLIGENCE              │
              ├─────────────────────────────────────────────┤
              │ alternatives                                 │
              │ compatibility constraints                    │
              │ benchmark evidence                           │
              │ blast radius                                 │
              │ simulation                                   │
              │ optimization                                 │
              │ rollback                                     │
              └────────────────┬────────────────────────────┘
                               ↓
              ┌─────────────────────────────────────────────┐
              │                VERIFICATION                   │
              ├─────────────────────────────────────────────┤
              │ security properties                          │
              │ trust validation                             │
              │ downgrade resistance                         │
              │ interoperability                             │
              │ chaos testing                                │
              │ regression testing                           │
              └────────────────┬────────────────────────────┘
                               ↓
              ┌─────────────────────────────────────────────┐
              │                 EXECUTION                    │
              ├─────────────────────────────────────────────┤
              │ ticketing                                    │
              │ CI/CD                                        │
              │ policy gates                                 │
              │ change windows                               │
              │ deployment                                   │
              └────────────────┬────────────────────────────┘
                               ↓
              ┌─────────────────────────────────────────────┐
              │             CONTINUOUS ASSURANCE             │
              ├─────────────────────────────────────────────┤
              │ runtime observation                          │
              │ drift                                        │
              │ downgrade                                    │
              │ regression                                   │
              │ prediction-vs-reality                        │
              │ model update                                 │
              └─────────────────────────────────────────────┘
```

---

# 37. The most important research distinction

The competitive market largely answers:

> **"What cryptography do we have?"**

Increasingly, it also answers:

> **"How risky is it?"**

And increasingly:

> **"What should we migrate first?"**

And, in some platforms:

> **"How can we execute the transition?"**

ECDAT-X should push the question further:

> **"Can we demonstrate, before and after a cryptographic state transition, that the system's required security properties remained true?"**

That leads to a different architecture.

---

# 38. The ECDAT-X state-transition model

Represent cryptographic configuration as:

```text
STATE S0
```

Example:

```text
RSA
TLS 1.2
Classical certificate
Trust Anchor A
Library X
HSM A
```

Proposed transition:

```text
S0 → S1
```

where:

```text
S1 =
Hybrid KEM
+
PQC-capable signature
+
updated trust chain
+
Library Y
+
HSM B
```

ECDAT-X should compute:

```text
ΔCryptography
ΔTrust
ΔDependencies
ΔPerformance
ΔCompatibility
ΔAttack Surface
ΔBusiness Risk
ΔOperational Risk
```

Then verify:

```text
SecurityProperty(S1) = TRUE
```

If not:

```text
REJECT TRANSITION
```

This is substantially more useful than simply detecting that the new algorithm exists.

---

# 39. Verification-first migration

A mature ECDAT-X migration plan should look like:

```text
1. Observe current state
2. Establish evidence
3. Identify uncertainty
4. Build dependency graph
5. Define target state
6. Define invariants
7. Find candidate migration paths
8. Benchmark candidates
9. Simulate
10. Test interoperability
11. Execute controlled change
12. Verify security properties
13. Verify rollback
14. Monitor production
15. Compare predicted vs actual outcome
16. Update model
```

---

# 40. Proposed ECDAT-X security invariants

Examples:

### Authentication invariant

```text
All authentication paths must terminate in an approved
quantum-resistant or approved hybrid trust path.
```

### Confidentiality invariant

```text
Protected long-lived data must not depend exclusively
on quantum-vulnerable public-key mechanisms.
```

### Downgrade invariant

```text
A PQC-capable endpoint must not silently fall back
to an unauthorized classical-only configuration.
```

### Trust invariant

```text
A migration must not introduce an unapproved trust anchor.
```

### Policy invariant

```text
No deployment may introduce an algorithm prohibited
by the organization's cryptographic policy.
```

### Availability invariant

```text
Migration must remain within the defined latency,
packet-size, memory and availability constraints.
```

---

# 41. Cryptographic evidence object

A core ECDAT-X object should look conceptually like:

```json
{
  "claim": "service-X uses RSA-2048",
  "asset_id": "crypto-8f21",
  "source": "runtime-network-observer",
  "timestamp": "2026-10-03T08:20:00Z",
  "evidence": {
    "endpoint": "service-X",
    "protocol": "TLS",
    "negotiated_algorithm": "RSA"
  },
  "confidence": 0.97,
  "freshness": "current",
  "status": "OBSERVED",
  "supports": [
    "quantum-risk-analysis"
  ]
}
```

A contradictory source should remain visible:

```json
{
  "claim": "service-X uses ECDSA",
  "status": "CONTRADICTORY",
  "source": "source-code-analyzer"
}
```

The system should then investigate rather than silently collapsing the conflict.

---

# 42. Competitor-derived ECDAT-X backlog

## Discovery

- [ ] Source scanner
- [ ] AST scanner
- [ ] Binary scanner
- [ ] Container scanner
- [ ] Runtime collector
- [ ] Network observer
- [ ] Certificate collector
- [ ] Cloud collector
- [ ] KMS collector
- [ ] HSM collector
- [ ] Hardware collector
- [ ] Firmware collector
- [ ] External network scanner
- [ ] Internal network scanner
- [ ] Database encryption scanner

## Evidence

- [ ] Provenance
- [ ] Timestamp
- [ ] Collector identity
- [ ] Confidence
- [ ] Freshness
- [ ] Contradiction detection
- [ ] Signed evidence
- [ ] Evidence replay

## Identity

- [ ] Stable asset IDs
- [ ] Entity resolution
- [ ] Duplicate detection
- [ ] Ownership mapping
- [ ] Rogue asset classification

## Graph

- [ ] Crypto graph
- [ ] Dependency graph
- [ ] Trust graph
- [ ] Data lineage
- [ ] Business graph
- [ ] Temporal graph

## Risk

- [ ] Quantum risk
- [ ] HNDL
- [ ] Business criticality
- [ ] Implementation weakness
- [ ] Systemic concentration
- [ ] Uncertainty
- [ ] Vendor readiness

## Migration

- [ ] PQC recommendations
- [ ] Hybrid options
- [ ] Constraint modeling
- [ ] Benchmarking
- [ ] Blast-radius analysis
- [ ] Simulation
- [ ] Optimization
- [ ] Rollback planning

## Verification

- [ ] Security-property compiler
- [ ] Trust-path verification
- [ ] Downgrade testing
- [ ] Interoperability testing
- [ ] Chaos experiments
- [ ] Regression tests
- [ ] Runtime verification

## Operations

- [ ] Jira
- [ ] ServiceNow
- [ ] GitHub
- [ ] GitLab
- [ ] CI/CD
- [ ] SIEM
- [ ] EDR
- [ ] NDR
- [ ] CMDB
- [ ] KMS/HSM
- [ ] PKI

## AI

- [ ] Evidence-grounded analyst
- [ ] Investigation planner
- [ ] Information-gain discovery
- [ ] Root-cause analysis
- [ ] Remediation explanation
- [ ] Decision provenance

## Second-pass architecture gap audit

A second review of the dossier identifies several areas that should be added without weakening the existing architecture. These are not reasons to discard the current design; they are extensions of the same evidence-backed state-transition model.

### G1. Cryptanalytic and algorithm-health intelligence

**Status: add — high importance.**

The current plan models algorithm choice, weakness and PQC migration, but it should also treat the security status of the *destination algorithm itself* as a continuously changing external signal. The historical PQC process demonstrates why: SIKE was publicly acknowledged as insecure during the NIST process, Rainbow was also broken, and NIST later selected HQC as a backup KEM based on a different mathematical foundation from ML-KEM ([NIST PQC process](https://csrc.nist.gov/Projects/post-quantum-cryptography/post-quantum-cryptography-standardization/round-4-submissions); [NIST HQC selection](https://www.nist.gov/news-events/news/2025/03/nist-selects-hqc-fifth-algorithm-post-quantum-encryption)). On July 29, 2026, the HAWK signature candidate was withdrawn after an AI-assisted cryptanalysis result ([NIST PQC status](https://www.nist.gov/pqc)). These events demonstrate that “PQC” is not a permanent security label.

Add an **Algorithm Health Feed** containing:

- new cryptanalysis papers and attacks;
- parameter/security-level erosion;
- implementation attacks and misuse findings;
- standards changes and deprecations;
- withdrawn or abandoned candidate algorithms;
- algorithm-family diversity and correlated-assumption risk;
- NIST/standards-body status;
- vendor/library implementation status;
- validated-module availability;
- recommended replacement candidates.

Then add **Crypto 911**: given a newly material algorithm-health event, traverse the Cryptographic Reality Graph and produce an evidence-backed blast-radius report, affected systems, owners, dependency blockers, available replacements, estimated migration effort, and a *computed* fast-path migration plan where the graph and environment make it feasible. Do not promise a universal 48-hour migration; the system should calculate whether such a transition is actually possible.

This turns crypto-agility from “we support multiple algorithms” into “we can respond when an algorithm's security status changes.”

### G2. Sovereign, offline and compartmented operation

**Status: add — important for government/defence deployments.**

The existing privacy/local-first direction should be extended into an explicit deployment architecture for environments that cannot depend on SaaS or external AI services. ECDAT-X should support:

- fully offline/air-gapped installation;
- signed offline updates for rules, algorithms, CVE/cryptanalysis feeds and detector packages;
- locally hosted inference models for the AI analyst;
- cryptographic verification of update provenance;
- separated security domains/enclaves;
- controlled cross-domain export of sanitized findings;
- optional one-way reporting/data-diode architectures where appropriate.

This should be treated as a deployment/security property, not as a claim that every NTRO environment has a particular network architecture.

### G3. National/sector-level cryptographic observatory

**Status: add as a future federated layer, not as an MVP requirement.**

The current model is enterprise-centric. A future national layer could ingest privacy-preserving summaries from participating organizations rather than centralizing their raw CBOMs. Possible mechanisms include federated aggregation and carefully designed differential-privacy techniques.

The observatory could detect:

- national or sector-wide algorithm monocultures;
- concentration around one HSM/KMS/CA/vendor;
- systemic dependency on a small number of libraries;
- cross-sector PQC migration bottlenecks;
- common vulnerable cryptographic configurations;
- aggregate readiness trends without exposing organization-level inventories.

For an Indian deployment, the governance layer should map applicable findings and reporting workflows to **CERT-In**, the **Digital Personal Data Protection Act/Rules**, sector-specific requirements and applicable government-approved cryptographic policies. The mapping must remain configurable because regulatory requirements evolve.

### G4. Cryptographic canaries for HNDL/exfiltration evidence

**Status: add as an experimental research capability, with strong governance.**

The existing HNDL model estimates exposure from data lifetime, cryptographic lifetime and migration time. It cannot itself prove that an adversary has harvested particular data. A controlled **cryptographic canary** experiment could place explicitly authorized decoy material in high-value, monitored locations and record any later appearance or access.

Important correction: a canary being exposed would be evidence of access/exfiltration, **not proof that an adversary has broken the underlying cryptographic algorithm**. Therefore the event should be represented as an empirical security signal and correlated with other evidence. Deployment must be opt-in, legally authorized and isolated from real sensitive data.

### G5. Workload, machine and AI-agent cryptographic identity

**Status: add — high-value future-facing extension.**

The identity graph should not assume that humans are the principal cryptographic subjects. Modern infrastructure increasingly assigns short-lived cryptographic identities to workloads. SPIFFE, for example, defines workload identities and short-lived SVIDs that can be rotated frequently.

ECDAT-X should therefore model:

- workload/service identities;
- service-mesh mTLS identities;
- short-lived certificates and automatic rotation;
- workload attestation;
- machine/device identities;
- AI-agent identities and delegated credentials;
- tool/API credentials used by agents;
- trust domains and federation;
- confidential-computing attestation chains;
- cryptography protecting model artifacts and high-value AI assets.

This reinforces the existing temporal model: an inventory snapshot can become stale rapidly when identities rotate automatically, so identity discovery should feed the event stream rather than remain a periodic snapshot.

### G6. Expand the cryptographic taxonomy beyond conventional public-key/TLS/PKI

**Status: add to the discovery ontology; implementation depth can be phased.**

The current architecture should explicitly distinguish additional cryptographic families and trust mechanisms, including:

- FHE;
- MPC;
- threshold signatures/threshold cryptography;
- zero-knowledge systems;
- QKD and quantum-communications equipment where deployed;
- QRNG/RNG infrastructure;
- DNSSEC;
- software/firmware/code-signing chains;
- secure-boot trust chains;
- long-lived archival signatures and trusted timestamps;
- cryptography embedded in specialized hardware and accelerators.

The important design principle is not to promise full semantic analysis of every primitive in the first release. The inventory ontology should be extensible enough that these assets can be represented, related and later analyzed without redesigning the graph.

### G7. Validation and certification intelligence

**Status: add — highly buildable and operationally useful.**

ECDAT-X should track the validation status of cryptographic modules and algorithms where applicable. For FIPS-oriented environments, this means integrating CMVP and CAVP information into the evidence graph rather than treating “FIPS compliant” as an unverified vendor label. NIST states that CAVP algorithm validation is a prerequisite for CMVP module validation, and the CMVP database records validation certificates and associated algorithm implementation references.

For each relevant dependency, track:

- module/product identity;
- exact validated version/part number;
- operational environment;
- certificate/validation identifier;
- validated algorithms;
- CAVP references;
- active/interim/historical status;
- caveats;
- PQC/hybrid support;
- validation expiry/sunset implications;
- relationship to the actually deployed artifact.

This enables questions such as: **“Does the exact cryptographic module we actually deploy have the validation and algorithm capability our policy requires?”**

### G8. Procurement and architecture-time crypto debt prevention

**Status: add — shift-left control.**

The platform should not only discover old cryptographic debt; it should prevent new debt from entering the enterprise. Extend the policy engine into procurement and architecture workflows:

- generate cryptographic requirements for RFPs/RFIs;
- maintain machine-readable vendor crypto questionnaires;
- request evidence rather than accepting declarations alone;
- validate vendor claims against observed artifacts where possible;
- gate architecture approvals on defined crypto-agility properties;
- record exceptions, expiry dates and compensating controls;
- feed approved requirements directly into deployment and CI/CD policy.

This creates a closed loop: **procure → design → build → deploy → observe → migrate → retire**.

### G9. Human/organizational readiness and crypto fire drills

**Status: add — operational extension of the existing chaos-engineering work.**

The graph should represent organizational ownership as a first-class relationship, including teams, service owners, vendors, approvers and escalation paths. Findings should be routable to the accountable owner rather than merely displayed.

Add:

- ownership-confidence scores;
- automatic ticket routing;
- migration readiness passports per team/system;
- tabletop cryptographic incident exercises;
- controlled migration fire drills;
- measured detection, decision, migration and rollback times;
- lessons learned feeding the migration model.

A system can be technically agile yet operationally unable to migrate quickly if no team can execute the change.

### G10. Post-migration retirement and cryptographic end-of-life

**Status: add — closes the lifecycle.**

The current migration/verification model proves that a target state can be reached, but the lifecycle should explicitly prove that the old state was retired. Add evidence for:

- key re-wrapping and re-encryption;
- archival migration;
- trust-anchor replacement;
- old certificate/key retirement;
- crypto-shredding where appropriate;
- revocation and deletion evidence;
- removal of deprecated libraries/configurations;
- signed retirement records;
- re-timestamping or preservation of long-lived signed material where required;
- final verification that old cryptographic paths are no longer reachable.

The desired lifecycle becomes:

```text
DISCOVER → ASSESS → PLAN → MIGRATE → VERIFY → RETIRE → PROVE RETIREMENT
```

### Gap-audit conclusion

These additions do **not** replace the core ECDAT-X thesis. They strengthen it. The common abstraction is still an evidence-backed cryptographic state machine: external intelligence changes the security assumptions, collectors observe the environment, the graph identifies affected entities, the migration engine searches for safe transitions, verification establishes the resulting properties, and continuous monitoring proves that the old or unsafe state does not silently return.

---

# 43. What should become the ECDAT-X moat?

Not:

```text
"we detect RSA."
```

Not:

```text
"we generate CBOM."
```

Not:

```text
"we calculate quantum risk."
```

Not:

```text
"we recommend ML-KEM."
```

Those are important, but the ecosystem is already moving strongly in those directions.

The deeper moat should be:

## Evidence

Can you prove where a claim came from?

## Reality

Can you reconcile source, binary, configuration and runtime?

## Uncertainty

Can you explicitly represent what is unknown?

## Causality

Can you explain why cryptographic state changed?

## Prediction

Can you predict migration consequences?

## Transition

Can you identify a safe path from S0 → S1?

## Verification

Can you prove the security property survived?

## Learning

Can production outcomes update the model?

That produces the central ECDAT-X proposition:

> **Cryptographic State-Transition Intelligence and Verification**

---

# 44. Recommended ECDAT-X product hierarchy

## Layer 1 — ECDAT Core

Enterprise discovery + CBOM.

## Layer 2 — Cryptographic Reality Graph

Evidence, identity, dependency, trust and temporal modeling.

## Layer 3 — Quantum / Systemic Risk

Quantum exposure, HNDL, business impact, implementation and systemic concentration.

## Layer 4 — Migration Intelligence

PQC alternatives, benchmark evidence, constraints, simulation and optimization.

## Layer 5 — Verification

Security properties, trust validation, downgrade protection, interoperability and chaos.

## Layer 6 — Continuous Cryptographic Assurance

Runtime observation, regression, drift, rollback and prediction-vs-reality.

## Layer 7 — Cryptographic AI Analyst

Evidence-grounded investigation and decision support.

---

# 45. Final synthesis

The public ecosystem shows a clear technological progression:

```text
Certificate Management
        ↓
Cryptographic Discovery
        ↓
Cryptographic Inventory
        ↓
CBOM
        ↓
Cryptographic Posture Management
        ↓
Quantum Security Posture Management
        ↓
Crypto-Agility
        ↓
Migration Orchestration
        ↓
Continuous Assurance
        ↓
?????
```

The open research opportunity is the final stage:

```text
CRYPTOGRAPHIC STATE-TRANSITION VERIFICATION
```

The central system would not merely observe that:

> "RSA exists."

It would know:

```text
WHERE RSA exists
WHO owns it
WHAT uses it
WHAT data it protects
WHICH trust relationships depend on it
WHAT depends on those relationships
HOW confident the system is
WHEN the observation was made
WHICH other observations disagree
WHAT will break if it changes
WHICH migration paths are possible
WHAT each path costs
WHAT each path risks
WHICH security properties must remain true
HOW to test them
WHETHER the transition actually preserved them
WHETHER production later drifted
WHY the drift happened
AND WHAT evidence proves each conclusion
```

That is the direction in which the existing ECDAT-X research dossier is already pointing.

---

# 46. Primary references

## Standards / government / research

1. [NIST NCCoE — Migration to Post-Quantum Cryptography](https://www.nccoe.nist.gov/applied-cryptography/migration-to-pqc)
2. [NIST CSWP 39-upd1 — Considerations for Achieving Crypto Agility](https://csrc.nist.gov/pubs/cswp/39/upd1/considerations-for-achieving-crypto-agility/final)
3. [IETF — Cryptographic Asset Discovery and Inventory (CADI) Internet-Draft](https://datatracker.ietf.org/)
4. [CycloneDX](https://cyclonedx.org/)
5. [CycloneDX Tool Center](https://cyclonedx.org/tool-center/)

## Enterprise cryptographic discovery / posture

6. [Keyfactor — Cryptographic Discovery & Inventory](https://www.keyfactor.com/products/cryptographic-discovery-inventory/)
7. [Keyfactor — Cryptographic Posture Management](https://www.keyfactor.com/products/cryptographic-posture-management/)
8. [QryptoCyber](https://qryptocyber.com/)
9. [DigiCert — Quantum Central](https://www.digicert.com/news/digicert-introduces-quantum-central)
10. [QuSecure — Cryptographic Discovery & Inventory](https://www.qusecure.com/quprotect/cryptographic-discovery-and-inventory/)
11. [QuSecure — QuProtect](https://www.qusecure.com/quprotect/)
12. [ISARA Advance](https://www.isara.com/products/isara-advance-cryptographic-inventory-and-risk-assessment-tool.html)
13. [PQStation — QVision](https://www.pqstation.com/qvision)
14. [AppViewX — Quantum Trust Hub](https://docs.appviewx.com/Sandbox/quantum_trust_hub.html)
15. [Fortanix — Post-Quantum Cryptography](https://www.fortanix.com/solutions/use-case/post-quantum-cryptography)
16. [Qubrisk](https://qubrisk.com/)
17. [Sectigo Quantum Ready](https://www.sectigo.com/resource-library/sectigo-introduces-sectigo-quantum-ready-qspm)

## Code / CBOM / software supply chain

18. [IBM CBOM](https://github.com/IBM/CBOM)
19. [PostQ Software Labs](https://postqsoftwarelabs.com/)
20. [PostQ Code Scan announcement](https://postqsoftwarelabs.com/announcement-2026-08-14-code-scan.html)
21. [CipherIQ CBOM Generator](https://docs.cipheriq.io/cbom-generator/)
22. [CipherIQ Asset Discovery](https://docs.cipheriq.io/cbom-generator/features/asset-discovery/)
23. [ReversingLabs — CycloneDX xBOM](https://www.reversinglabs.com/press-releases/reversinglabs-delivers-most-comprehensive-support-for-cyclonedx-xbom)

## Trust / PKI / cryptographic infrastructure

24. [Entrust — Cryptographic Security Platform](https://www.entrust.com/products/cryptographic-security-platform)
25. [Entrust — Post-Quantum Cryptography](https://www.entrust.com/solutions/post-quantum-cryptography)
26. [Thales — Post-Quantum Crypto Agility](https://cpl.thalesgroup.com/encryption/post-quantum-crypto-agility)
27. [Thales — Cryptographic Inventory](https://cpl.thalesgroup.com/sites/default/files/content/white-paper/cryptographic-inventory-quantum-readiness-wp.pdf)

## Ecosystem / context

28. [Microsoft Security — Building Your Cryptographic Inventory](https://www.microsoft.com/en-us/security/blog/2026/04/16/building-your-cryptographic-inventory-a-customer-strategy-for-cryptographic-posture-management/)
29. [SandboxAQ — Transitioning to a Post-RSA World](https://www.sandboxaq.com/post/transitioning-to-a-post-rsa-world)
30. [NIST — Selects HQC as Fifth Algorithm for Post-Quantum Encryption](https://www.nist.gov/news-events/news/2025/03/nist-selects-hqc-fifth-algorithm-post-quantum-encryption)
31. [NIST — Post-Quantum Cryptography](https://www.nist.gov/pqc)
32. [NIST CMVP — Validated Modules](https://csrc.nist.gov/projects/cryptographic-module-validation-program/validated-modules)
33. [NIST CAVP — Cryptographic Algorithm Validation Program](https://csrc.nist.gov/Projects/cryptographic-algorithm-validation-program)
34. [NIST — FIPS 140-3](https://csrc.nist.gov/pubs/fips/140-3/final)
35. [NIST — SHA-1 Transition](https://csrc.nist.gov/news/2022/nist-transitioning-away-from-sha-1-for-all-apps)
36. [NSA — CNSA 2.0 / CSfC Post-Quantum Guidance](https://www.nsa.gov/Portals/75/documents/resources/everyone/csfc/capability-packages/CSfC%20Post%20Quantum%20Cryptography%20Guidance%20Addendum%201_0_Draft_5.pdf)
37. [CERT-In — Directions under Section 70B](https://www.cert-in.org.in/Directions70B.jsp)
38. [MeitY — Digital Personal Data Protection Act, 2023](https://www.meity.gov.in/static/uploads/2024/02/Digital-Personal-Data-Protection-Act-2023.pdf)
39. [MeitY — Digital Personal Data Protection Rules, 2025](https://www.meity.gov.in/documents/act-and-policies/digital-personal-data-protection-rules-2025-gDOxUjMtQWa)
40. [SPIFFE — Secure Production Identity Framework for Everyone](https://spiffe.io/docs/latest/spiffe-specs/spiffe/)
41. [SPIFFE — Workload API](https://spiffe.io/docs/latest/spiffe-specs/spiffe_workload_api/)
42. [NIST — Recommendation for Digital Signature Timeliness](https://www.nist.gov/publications/recommendation-digital-signature-timeliness)

---

# 47. Source-quality note

Vendor pages are useful for establishing **what a vendor publicly says its product does**.

They are not sufficient by themselves to establish:

- independent benchmark superiority;
- real-world coverage in every environment;
- false-positive/false-negative rates;
- production scalability;
- security guarantees;
- unique technical novelty.

For those questions, ECDAT-X should eventually build an **independent benchmark laboratory**.

A serious benchmark should measure:

```text
Detection recall
Detection precision
False-positive rate
False-negative rate
Evidence quality
Asset deduplication
Entity resolution accuracy
Runtime correlation
Network discovery accuracy
PQC classification accuracy
Migration prediction accuracy
Blast-radius prediction
Interoperability success
Performance impact
Memory consumption
Scan throughput
Privacy leakage
Rollback correctness
Downgrade detection
Security-property preservation
```

That benchmark could become one of ECDAT-X's most important research artifacts.

---

# 48. Final architectural principle

The competitors show us how to build:

```text
better scanners
better inventory
better CBOM
better dashboards
better migration workflows
better crypto-agility
```

ECDAT-X should learn all of those.

But the deeper objective should remain:

```text
              ┌───────────────────────┐
              │   CRYPTOGRAPHIC       │
              │      REALITY          │
              └──────────┬────────────┘
                         ↓
              ┌───────────────────────┐
              │      EVIDENCE         │
              └──────────┬────────────┘
                         ↓
              ┌───────────────────────┐
              │     UNCERTAINTY       │
              └──────────┬────────────┘
                         ↓
              ┌───────────────────────┐
              │   REALITY GRAPH       │
              └──────────┬────────────┘
                         ↓
              ┌───────────────────────┐
              │    CHANGE MODEL       │
              └──────────┬────────────┘
                         ↓
              ┌───────────────────────┐
              │   SAFE TRANSITION     │
              └──────────┬────────────┘
                         ↓
              ┌───────────────────────┐
              │      VERIFY           │
              └──────────┬────────────┘
                         ↓
              ┌───────────────────────┐
              │      OBSERVE          │
              └──────────┬────────────┘
                         ↓
                       LEARN
                         │
                         └────────────→ REALITY
```

**The goal is not to know what cryptography exists.**

**The goal is to know what is true, what is uncertain, what will happen if it changes, how to change it safely, and how to prove that security survived the change.**
