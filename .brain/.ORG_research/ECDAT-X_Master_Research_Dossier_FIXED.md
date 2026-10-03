# ECDAT-X --- Enterprise Cryptographic Discovery, Intelligence & Migration Verification Platform

**SIH 2026 Problem Statement:** 26164 --- Enterprise Cryptographic
Discovery & Analysis Tool (ECDAT)\
**Organization:** National Technical Research Organisation (NTRO)\
**Theme:** Blockchain & Cybersecurity\
**Document type:** Research / Architecture Master Dossier\
**Prepared:** 03 October 2026

------------------------------------------------------------------------

## 0. Executive Thesis

The SIH problem statement asks for an enterprise tool that discovers
cryptographic artefacts, builds a cryptographic inventory/CBOM, assesses
quantum risk, classifies assets, and recommends post-quantum or hybrid
alternatives.

A basic implementation can therefore be represented as:

``` text
SCAN
  ↓
FIND CRYPTO
  ↓
CBOM
  ↓
RISK
  ↓
PQC RECOMMENDATION
```

That is necessary, but it is not the research frontier.

The stronger research question is:

> **Can a machine maintain an evidence-backed model of an organization's
> cryptographic reality, quantify what it does and does not know,
> predict the consequences of cryptographic change, identify a safe
> transition under explicit constraints, verify the resulting security
> properties, and continuously learn from what happens in production?**

This reframes ECDAT from a scanner into a **Cryptographic
State-Transition Verification System**.

The system should therefore evolve through seven fundamental
capabilities:

1.  **Observe** cryptographic reality across source, binary,
    configuration, runtime, network, certificates, cloud, hardware and
    firmware.
2.  **Reconcile** conflicting observations into an evidence-backed
    cryptographic reality model.
3.  **Reason** about data sensitivity, business criticality,
    dependencies, quantum exposure, implementation quality and systemic
    concentration.
4.  **Predict** what will happen if a cryptographic asset, protocol,
    key, certificate, trust anchor, library or hardware dependency
    changes.
5.  **Find** migration strategies that satisfy security, compatibility,
    performance, cost, hardware, vendor and operational constraints.
6.  **Verify** that the required security properties actually survived
    the transition---not merely that a new algorithm appears somewhere
    in a certificate or binary.
7.  **Continuously observe** the deployed system, detect
    drift/downgrade/rollback, compare prediction with reality, and
    update the model.

The uploaded research corpus makes the same strategic distinction: a
basic CBOM scanner is only the first layer, while the larger opportunity
is an enterprise cryptographic observability, reasoning and migration
system. fileciteturn1file3L615-L668

------------------------------------------------------------------------

# 1. What Existing Ecosystems Already Solve

ECDAT must explicitly build on existing work rather than pretending
every component is novel.

The current ecosystem broadly looks like:

``` text
Cryptographic Discovery
        ↓
CBOM / CADI
        ↓
Risk Assessment
        ↓
PQC Selection
        ↓
Interoperability / Benchmarking
        ↓
Migration Planning
```

NIST's current PQC migration work separates **cryptographic visibility
and risk management** from **interoperability and benchmarking**. The
IETF CADI work expands discovery beyond source code into CBOM
declarations, SAST, binaries/images, simulated handshakes, traffic
analysis, process identification and configuration extraction. IBM's
CBOM research focuses on evidence capture, naming/configuration
ambiguity, and relationships between components that provide versus
consume cryptography. Recent academic work is also exploring graph-based
migration planning.

Therefore:

> **CBOM + graph + risk + PQC recommendation is not enough as the
> central novelty.**

The opportunity is to connect these fragmented layers into a closed
loop.

### Research positioning

ECDAT-X should be described as:

> **An evidence-backed cryptographic observability and state-transition
> verification platform for enterprise post-quantum migration.**

Not:

> "A better CBOM scanner."

------------------------------------------------------------------------

# 2. Architectural North Star

``` text
                         ┌──────────────────────────────┐
                         │      ECDAT COMMAND CENTER    │
                         └──────────────┬───────────────┘
                                        │
                         ┌──────────────▼───────────────┐
                         │  CRYPTOGRAPHIC REALITY GRAPH │
                         └──────────────┬───────────────┘
                                        │
          ┌─────────────────────────────┼────────────────────────────┐
          │                             │                            │
          ▼                             ▼                            ▼
   DISCOVERY ENGINE              INTELLIGENCE ENGINE          MIGRATION ENGINE
          │                             │                            │
 source / AST                    evidence / uncertainty       strategy search
 binary                          risk / HNDL                   simulation
 container                       attack graph                  constraint solving
 runtime                         lineage / DNA                 dependency ordering
 network                         systemic risk                 cost / impact
 cloud                           temporal causality             rollback analysis
 hardware                        security properties            validation
 firmware                        AI reasoning
 certificates
          │                             │                            │
          └─────────────────────────────┼────────────────────────────┘
                                        ▼
                           ┌─────────────────────────┐
                           │ REMEDIATION / VALIDATION│
                           └────────────┬────────────┘
                                        ▼
                           ┌─────────────────────────┐
                           │ CONTINUOUS OBSERVABILITY │
                           └────────────┬────────────┘
                                        │
                                        ▼
                              LEARNING / FEEDBACK LOOP
```

------------------------------------------------------------------------

# 3. Fundamental Primitive #1 --- Multi-Modal Cryptographic Discovery

## 3.1 Why source scanning is insufficient

The original PS explicitly calls for source repositories, binaries,
libraries and containers. The 2026 IETF CADI work goes further by
discussing:

-   static source scanning
-   CBOM declarations
-   binary/image scanning
-   CI/CD discovery
-   active protocol probing
-   passive traffic identification
-   TLS/IPsec/SSH discovery
-   runtime/process identification
-   configuration extraction
-   legacy black-box systems

The uploaded research identifies the same transition: discovery should
span source, binary, container, network, runtime, hardware, cloud and
firmware rather than relying on one modality.
fileciteturn1file3L645-L668

## 3.2 Discovery planes

### Source plane

Discover:

-   algorithms
-   key-generation APIs
-   signing APIs
-   encryption/decryption APIs
-   hash functions
-   KDFs
-   protocol implementations
-   TLS/SSH/IPsec configuration
-   certificates and trust stores
-   hard-coded parameters
-   cryptographic constants
-   algorithm-selection logic
-   third-party crypto wrappers

### Binary plane

Analyze:

-   ELF
-   PE
-   DLL
-   SO
-   APK
-   firmware images
-   native libraries
-   statically linked crypto
-   stripped binaries
-   embedded certificates
-   protocol identifiers
-   algorithm OIDs
-   known crypto constants
-   crypto-related symbols

### Container plane

Inspect:

-   base images
-   packages
-   native crypto libraries
-   language dependencies
-   configuration
-   certificates
-   environment variables
-   image layers
-   embedded binaries
-   service-mesh configuration

### Runtime plane

Observe:

-   loaded crypto libraries
-   process behavior
-   cryptographic API calls
-   runtime configuration
-   protocol handshakes
-   dynamic instrumentation evidence
-   process-to-service relationships
-   eBPF/system-level telemetry where appropriate

### Network plane

Discover:

-   TLS
-   QUIC
-   SSH
-   IPsec
-   VPN
-   mTLS
-   LDAP/LDAPS
-   SMTP/IMAP
-   SFTP
-   database TLS
-   service mesh
-   API gateways
-   load balancers

### Cloud plane

Inspect:

-   KMS
-   cloud certificates
-   managed databases
-   object storage encryption
-   serverless functions
-   managed TLS
-   cloud HSMs
-   key policies
-   infrastructure-as-code
-   machine images
-   secrets/configuration metadata

### Hardware / firmware plane

Inspect:

-   HSM
-   TPM
-   secure enclave
-   smart card
-   crypto accelerator
-   secure boot
-   firmware signing
-   device identity
-   embedded certificates
-   long-lived embedded crypto

### Certificate / PKI plane

Track:

-   leaf certificates
-   intermediate CAs
-   roots
-   algorithms
-   key sizes
-   validity periods
-   trust stores
-   certificate consumers
-   chain relationships
-   renewal mechanisms

------------------------------------------------------------------------

# 4. Fundamental Primitive #2 --- Semantic Cryptography Discovery

A grep-style detector such as:

``` text
search("RSA")
search("AES")
search("ECDSA")
```

is inadequate.

Cryptography can be several abstraction layers away:

``` text
Application
   ↓
Business function
   ↓
Crypto wrapper
   ↓
Library API
   ↓
Crypto implementation
   ↓
Algorithm
```

Therefore ECDAT should build a semantic analysis pipeline:

``` text
Source
  ↓
AST
  ↓
Call Graph
  ↓
Data Flow
  ↓
Control Flow
  ↓
Crypto API
  ↓
Algorithm
  ↓
Parameters
  ↓
Purpose
  ↓
Protected Data
```

The goal is not:

> "RSA was found."

The goal is:

> "This function generates an RSA-2048 key that is used for digital
> signatures in the authentication service, and the resulting
> authentication decision protects the payment API."

This aligns with the uploaded research's emphasis on semantic
AST/data-flow discovery and IBM's work on cryptographic code discovery.
fileciteturn1file3L615-L623

### Required analysis types

-   AST matching
-   call-chain tracking
-   taint/data-flow analysis
-   interprocedural analysis
-   configuration resolution
-   wrapper/API resolution
-   dependency resolution
-   semantic purpose classification

------------------------------------------------------------------------

# 5. Fundamental Primitive #3 --- Binary Reverse-Cryptography

A binary may contain cryptography even when source code is unavailable.

Input:

``` text
app.exe
libcrypto.so
firmware.bin
APK
DLL
ELF
container image
```

Output should be evidence-backed:

``` text
Algorithm: RSA-2048
Evidence:
  - OpenSSL symbol
  - ASN.1 OID
  - RSA key-size constant
Confidence: 0.96
```

Not:

``` text
RSA detected.
```

### Binary evidence sources

-   crypto function signatures
-   known library fingerprints
-   OIDs
-   constants
-   instruction patterns
-   certificate structures
-   protocol strings
-   symbol tables
-   imported functions
-   embedded keys/certificates
-   known implementation fingerprints

### Research requirement

Every reverse-engineering conclusion must retain:

``` text
claim
→ evidence
→ detector
→ confidence
→ timestamp
→ scope
```

This becomes critical later for evidence provenance.

------------------------------------------------------------------------

# 6. Fundamental Primitive #4 --- Runtime Cryptography Discovery

Static analysis tells us what **could** happen.

Runtime observation tells us what **did** happen.

Example:

``` text
STATIC:
RSA
ECDSA
AES

RUNTIME:
ECDSA P-256
AES-256-GCM
```

ECDAT should explicitly represent this difference.

Potential techniques:

-   eBPF
-   system-call tracing
-   dynamic instrumentation
-   shared-library observation
-   runtime configuration inspection
-   process inspection
-   network observation
-   telemetry correlation

The CADI draft discusses process identification/eBPF and other passive
approaches while acknowledging practical limitations.

------------------------------------------------------------------------

# 7. Fundamental Primitive #5 --- Cryptographic Reality / Epistemology Engine

This is one of the most important architectural ideas.

A mature system must distinguish:

``` text
DECLARED
OBSERVED
INFERRED
VERIFIED
CONFLICTING
UNKNOWN
```

### Declared

A vendor, application or inventory says:

``` text
"PQC enabled."
```

### Observed

ECDAT directly sees:

``` text
TLS handshake → X25519
```

### Inferred

Evidence suggests a particular library path is responsible.

### Verified

ECDAT actively tests the behavior in a controlled environment.

### Conflicting

One evidence source says RSA while runtime/network evidence says ECDSA.

### Unknown

ECDAT cannot establish the actual state.

Example:

``` text
RSA-2048
────────────────────
Declared       YES
Static         YES
Binary         YES
Runtime        NO
Network        NO
Certificate    NO
Hardware       UNKNOWN

Confidence: 0.87
Evidence age: 3 days
Contradictions: 1
```

The uploaded research explicitly proposes treating uncertainty as a
first-class object rather than forcing the system to choose one "truth."
fileciteturn1file2L391-L469

### Key principle

> **Unknown is not zero risk. Unknown is an epistemic state.**

This distinction should propagate into risk, migration and verification.

------------------------------------------------------------------------

# 8. Fundamental Primitive #6 --- Evidence Fabric

Every claim produced by ECDAT should have an evidence chain.

``` text
CLAIM
 │
 ├── source file
 ├── binary evidence
 ├── runtime observation
 ├── network handshake
 ├── certificate
 ├── configuration
 ├── detector
 ├── timestamp
 ├── freshness
 ├── confidence
 └── contradictions
```

Example:

``` text
CLAIM:
Service A uses ECDSA P-256.

EVIDENCE:
1. source API call
2. binary dependency
3. runtime observation
4. TLS certificate
5. network handshake

STATUS:
Verified

FRESHNESS:
8 minutes

CONTRADICTIONS:
None
```

### Evidence graph

Evidence should itself become graph data:

``` text
Evidence
   ↓ supports
Claim
   ↓ describes
Crypto Asset
   ↓ affects
System
```

This allows ECDAT to answer:

> Why do you believe this?

rather than merely:

> What did you find?

------------------------------------------------------------------------

# 9. Fundamental Primitive #7 --- Asset Identity Engine

A major hidden problem is identity resolution.

The following may all represent one system:

``` text
payment-api
payment-api-prod
pay-prod-02
10.20.4.17
container abc123
Kubernetes pod xyz
AWS instance i-xxx
GitHub repo /payment
TLS certificate ABC
```

ECDAT must determine whether these are:

``` text
8 independent assets
```

or:

``` text
1 logical system represented through 8 observations.
```

### Canonical identity model

``` text
Logical System
 ├── Repository
 ├── Build Artifact
 ├── Container
 ├── Runtime Process
 ├── Host
 ├── Network Identity
 ├── Certificate
 ├── Cloud Resource
 └── Crypto Assets
```

This is essentially **entity resolution for cybersecurity**.

Without it, a cryptographic knowledge graph becomes duplicate-heavy and
unreliable.

------------------------------------------------------------------------

# 10. Fundamental Primitive #8 --- Cryptographic Reality Graph

CBOM should not be the internal master model.

Instead:

``` text
                DATA
                 │
              protects
                 │
               CRYPTO
             /   |    \
            /    |     \
   implemented  used  configured
        /         |        \
    library     service     policy
       |           |          |
    version      runtime      owner
       |           |
     vendor      network
```

CBOM becomes:

> **A projection/export of the richer internal graph.**

This allows future interoperability with:

-   CBOM
-   SBOM
-   HBOM
-   OBOM
-   cloud inventories
-   CMDB
-   PKI inventories
-   vulnerability databases

The uploaded research explicitly recommends treating CBOM as an output
while maintaining a richer canonical cryptographic model.
fileciteturn1file3L615-L623

------------------------------------------------------------------------

# 11. Fundamental Primitive #9 --- Crypto → Data → System Lineage

A cryptographic algorithm matters because of what it protects.

Example:

``` text
Government Secret Data
        ↓
Payment / Records Service
        ↓
AES-256-GCM
        ↓
Database
        ↓
Backup
        ↓
Cloud Storage
```

ECDAT should answer:

-   What data does this primitive protect?
-   Where did that data originate?
-   Where is it copied?
-   How long must it remain confidential?
-   Which cryptographic mechanisms protect each copy?
-   Which backup/archive paths remain vulnerable?
-   What happens if this primitive is compromised?

This creates:

> **Cryptographic data lineage.**

------------------------------------------------------------------------

# 12. Fundamental Primitive #10 --- Capability ≠ Configuration ≠ Negotiation ≠ Actual Use

This distinction should be first-class.

A service may:

``` text
CAPABILITY:
RSA, ECDSA, ML-DSA

        ↓

CONFIGURATION:
ECDSA preferred

        ↓

NEGOTIATION:
ECDSA selected

        ↓

ACTUAL USE:
ECDSA used for authentication
```

These are four different facts.

A PQC-capable service is not necessarily a PQC-using service.

The uploaded research explicitly identifies this gap and connects it to
network observability limitations. fileciteturn1file0L79-L127

------------------------------------------------------------------------

# 13. Fundamental Primitive #11 --- Cryptographic Time Machine

Cryptography is time-dependent.

Example:

``` text
09:00 → RSA
10:00 → ECDSA
11:00 → PQ hybrid
12:00 → rollback → RSA
```

A static CBOM might simply contain:

``` text
RSA
ECDSA
ML-KEM
```

but lose the critical temporal fact:

> When was each mechanism active?

Represent every observation as:

``` text
(asset,
 algorithm,
 context,
 timestamp,
 evidence)
```

Then ECDAT can answer:

-   When did RSA become active?
-   When did it stop?
-   Did PQC ever actually become active?
-   Was there a rollback?
-   Was a vulnerable algorithm active for only 17 minutes?
-   Which deployment introduced the change?

The uploaded research defines this as a **cryptographic event stream /
Cryptographic Time Machine**. fileciteturn1file0L12-L34

------------------------------------------------------------------------

# 14. Fundamental Primitive #12 --- Crypto Drift Causality

A drift detector says:

``` text
Crypto configuration changed.
```

A causal investigation engine asks:

``` text
Deployment #1842
      ↓
Configuration change
      ↓
Certificate replacement
      ↓
TLS fallback
      ↓
Crypto downgrade
```

The objective is to correlate:

-   deployment events
-   configuration changes
-   certificate changes
-   library upgrades
-   runtime changes
-   network behavior
-   algorithm changes

with timestamps.

This converts ECDAT from an inventory system into a **cryptographic
incident investigation system**.

------------------------------------------------------------------------

# 15. Fundamental Primitive #13 --- Crypto DNA

Every application/system should have a cryptographic profile.

Example:

``` text
PAYMENT-SERVICE

Encryption:
  AES-256-GCM

Key Exchange:
  ECDH P-256

Authentication:
  ECDSA P-256

Hash:
  SHA-256

Transport:
  TLS 1.3

Certificates:
  4

HSM:
  YES

PQC:
  NO

Crypto Agility:
  LIMITED

Quantum Exposure:
  HIGH

Migration Complexity:
  HIGH
```

Crypto DNA should be dynamically generated from the evidence graph---not
manually entered.

------------------------------------------------------------------------

# 16. Fundamental Primitive #14 --- Cryptographic Dependency Graph

Model:

``` text
Payment API
 ├── TLS
 │    └── ECDHE
 │         └── P-256
 ├── Certificate
 │    └── ECDSA
 │         └── P-256
 └── HSM
      └── firmware 4.2
```

Then ask:

> What happens if P-256 must be removed?

The graph should traverse:

``` text
P-256
 ↓
ECDSA certificates
 ↓
services
 ↓
clients
 ↓
business applications
 ↓
sensitive datasets
```

Recent 2026 research is already exploring dependency-aware PQC migration
planning and graph-based cryptographic risk modeling. The research
opportunity is therefore not merely "use a graph"; it is to connect
graph reasoning to uncertainty, change, verification and continuous
feedback.

------------------------------------------------------------------------

# 17. Fundamental Primitive #15 --- Cryptographic Single Points of Failure

Suppose:

``` text
500 applications
      ↓
ECDSA P-256
```

This is not necessarily 500 independent problems.

It may be one systemic dependency.

Calculate:

-   dependency centrality
-   affected-system count
-   critical-system reach
-   data reach
-   vendor concentration
-   library concentration
-   CA concentration
-   HSM concentration
-   algorithm concentration

Output:

``` text
CRYPTOGRAPHIC SYSTEMIC DEPENDENCY

Primitive: ECDSA P-256
Affected applications: 500
Critical systems: 37
Common library: X
Common CA: Y
Common HSM: Z
```

------------------------------------------------------------------------

# 18. Fundamental Primitive #16 --- Cryptographic Monoculture / Concentration Risk

A future enterprise may have:

``` text
80% of applications
→ same crypto library

70% of certificates
→ same CA

90% of HSM workloads
→ same vendor

85% of authentication
→ same primitive family
```

Even if each individual asset is secure, concentration creates systemic
risk.

ECDAT should therefore model:

``` text
Algorithm concentration
Library concentration
Vendor concentration
CA concentration
Hardware concentration
Firmware concentration
Protocol concentration
```

This is analogous to systemic risk rather than ordinary vulnerability
scoring.

------------------------------------------------------------------------

# 19. Fundamental Primitive #17 --- Quantum Attack Propagation Graph

Do not stop at:

``` text
RSA = quantum vulnerable
```

Model:

``` text
Quantum-vulnerable primitive
          ↓
Certificate
          ↓
Authentication
          ↓
Identity
          ↓
Service
          ↓
Application
          ↓
Sensitive data
          ↓
Business process
```

Then answer:

> If this primitive becomes breakable, what is the downstream business
> impact?

------------------------------------------------------------------------

# 20. Fundamental Primitive #18 --- Data-Centric Quantum Risk

Quantum risk should depend on more than the algorithm.

A stronger model includes:

``` text
Cryptographic vulnerability
+
Data sensitivity
+
Data lifetime
+
Exposure
+
Migration time
+
Business criticality
+
Dependency centrality
+
Hardware/vendor lead time
```

Two RSA-2048 systems can have radically different migration urgency:

``` text
SYSTEM A
Data lifetime: 3 months
Migration: 2 weeks

SYSTEM B
Data lifetime: 25 years
Migration: 4 years
```

Same primitive.

Different strategic situation.

------------------------------------------------------------------------

# 21. Fundamental Primitive #19 --- HNDL / SNDL Intelligence

Build a dedicated:

## Harvest-Now-Decrypt-Later Engine

Ask:

``` text
Is data encrypted today?
        ↓
Will it remain sensitive when quantum
capabilities become available?
        ↓
Is the protection quantum-vulnerable?
        ↓
How long does migration take?
```

Then classify exposure using the organization's policy rather than
pretending there is one universal score.

------------------------------------------------------------------------

# 22. Fundamental Primitive #20 --- Scenario-Based Mosca

The SIH PS explicitly references Mosca's inequality.

Do not implement it as a single deterministic date.

Model:

``` text
Data lifetime
+
Migration time
+
Uncertainty
+
CRQC scenario
```

Use scenarios:

``` text
Scenario A:
Earlier-than-expected CRQC

Scenario B:
Middle scenario

Scenario C:
Later scenario
```

Then calculate:

-   assets becoming urgent
-   remaining migration window
-   HNDL exposure
-   systems requiring accelerated action
-   sensitivity to assumptions

The output should expose assumptions.

------------------------------------------------------------------------

# 23. Fundamental Primitive #21 --- Quantum Scenario Engine

Instead of saying:

> "A CRQC arrives in 2037."

represent uncertainty explicitly:

``` text
CRQC timing:
  scenario distribution

Data lifetime:
  distribution

Migration duration:
  distribution

Vendor readiness:
  uncertainty

Hardware readiness:
  uncertainty
```

Then perform scenario analysis.

This is more scientifically honest and more useful for planning.

------------------------------------------------------------------------

# 24. Fundamental Primitive #22 --- Security Property First-Class Model

Algorithms are implementation mechanisms.

Security requirements are higher-level properties.

Model:

``` text
Crypto Asset
     ↓
Security Property
     ↓
Business Requirement
```

Properties may include:

-   confidentiality
-   integrity
-   authentication
-   identity binding
-   forward secrecy
-   non-repudiation
-   key establishment
-   quantum resistance
-   downgrade resistance
-   trust continuity

This allows ECDAT to ask:

> What property does this algorithm provide?

rather than:

> Which algorithm is present?

------------------------------------------------------------------------

# 25. Fundamental Primitive #23 --- Security Property Compiler

A user should be able to state:

``` text
Authentication must remain secure
even if classical public-key cryptography
is broken.
```

ECDAT compiles this into machine-verifiable requirements:

``` text
✓ PQ credential
✓ PQ verification
✓ PQ-bearing validation chain
✓ appropriate trust anchor
✓ PQ evidence contributes to decision
✓ prohibited classical fallback
✓ downgrade detection
```

The uploaded research explicitly proposes this concept.
fileciteturn1file4L701-L748

This is a major shift from algorithm inventory to **security-property
verification**.

------------------------------------------------------------------------

# 26. Fundamental Primitive #24 --- Authentication Property Verification

A hybrid certificate containing classical + PQ material is not
sufficient evidence that hybrid security was actually achieved.

ECDAT should test:

> **Did the PQ evidence actually contribute to the authentication
> decision?**

This matters because recent 2026 research identified verifier-semantics
cases where classical validation can remain outcome-bearing even when PQ
evidence is present.

Therefore:

``` text
Certificate contains PQ
        ≠
PQC authentication property verified
```

That distinction should become a core validation primitive.

------------------------------------------------------------------------

# 27. Fundamental Primitive #25 --- Trust Graph

Certificate migration is not just leaf replacement.

Model:

``` text
Root CA
   ↓
Intermediate CA
   ↓
Leaf Certificate
   ↓
Service
   ↓
Client
   ↓
Trust Store
```

Also include:

-   device provisioning
-   firmware trust
-   OS trust
-   application trust
-   HSM trust
-   boot trust

Then simulate:

> What happens if this trust anchor changes?

The uploaded research emphasizes that PQ authentication depends on the
full validation path and trust anchor, not merely the leaf certificate.
fileciteturn1file8L1583-L1633

------------------------------------------------------------------------

# 28. Fundamental Primitive #26 --- PKI Dependency Graph

Track:

``` text
certificate
 ↓
issuer
 ↓
algorithm
 ↓
key type
 ↓
chain
 ↓
application
 ↓
server
 ↓
business service
```

Detect:

-   expired certificates
-   weak algorithms
-   weak keys
-   inappropriate lifetimes
-   orphan certificates
-   duplicate certificates
-   shadow certificates
-   chain problems
-   PQ readiness
-   migration dependencies

CycloneDX CBOM already models certificates and cryptographic
relationships; ECDAT should add temporal, trust, verification and
migration semantics.

------------------------------------------------------------------------

# 29. Fundamental Primitive #27 --- HSM / KMS / TPM Intelligence

Inventory:

``` text
HSM
KMS
TPM
Secure Enclave
Smart Card
Crypto Accelerator
```

For each:

``` text
Vendor
Model
Firmware
Supported algorithms
Supported key types
PQC capability
Upgrade path
Replacement path
Certification
Dependencies
```

The critical insight:

> **PQC migration is not purely software.**

------------------------------------------------------------------------

# 30. Fundamental Primitive #28 --- Hardware / Firmware Crypto Discovery

Target:

-   IoT
-   routers
-   switches
-   industrial controllers
-   vehicles
-   medical equipment
-   satellites
-   embedded devices

Pipeline:

``` text
Firmware
 ↓
Strings
 ↓
Symbols
 ↓
Constants
 ↓
Crypto implementation
 ↓
Protocols
 ↓
Certificates
 ↓
Root of trust
```

Then:

``` text
Firmware
 ├── RSA-2048
 ├── ECDSA-P256
 ├── TLS
 └── hard-coded certificate
```

------------------------------------------------------------------------

# 31. Fundamental Primitive #29 --- Hardware Root-of-Trust Mapper

Model:

``` text
Secure Boot
    ↓
Bootloader
    ↓
Firmware Signature
    ↓
TPM / Secure Element
    ↓
Device Identity
```

Then determine:

> Which primitive protects the device's root of trust?

This matters because a software-level PQC recommendation may be
impossible if the trust root cannot be upgraded.

NIST's secure-hardware work emphasizes lifecycle considerations spanning
silicon/IP, manufacturing, deployment, operation and end-of-life.

------------------------------------------------------------------------

# 32. Fundamental Primitive #30 --- IT / OT / IoT / ICS Migration Profiles

Different environments have different migration constraints.

``` text
IT
OT
IoT
ICS
```

A cloud server may be updated immediately.

A 20-year industrial controller may require:

-   vendor firmware
-   physical service
-   safety validation
-   downtime window
-   hardware replacement
-   certification
-   field deployment
-   long procurement cycles

Recent research specifically highlights the difference between IT and OT
PQC migration.

Therefore migration feasibility must include the **physical lifecycle**.

------------------------------------------------------------------------

# 33. Fundamental Primitive #31 --- Physical Migration Feasibility

For constrained devices, measure:

-   CPU
-   RAM
-   flash
-   network MTU
-   packet count
-   handshake size
-   energy
-   battery impact
-   latency
-   throughput
-   firmware update capability
-   bootloader capability
-   secure-boot support
-   HSM/TPM support
-   field-service requirements
-   vendor lifecycle

CPU benchmark alone is insufficient.

------------------------------------------------------------------------

# 34. Fundamental Primitive #32 --- PQC Benchmark Lab

The PS asks for recommendations based on latency and cost.

ECDAT should actually benchmark.

Compare:

``` text
Current classical
vs
PQC
vs
Hybrid
```

Measure:

``` text
CPU
RAM
Latency
Bandwidth
Handshake size
Key size
Signature size
Energy
Throughput
Failure rate
```

Potential environments:

-   server
-   laptop
-   ARM
-   embedded device
-   simulated constrained device
-   network emulator

Recent PQC implementation research emphasizes cross-platform
performance, memory, communication, side-channel and constrained-device
trade-offs.

------------------------------------------------------------------------

# 35. Fundamental Primitive #33 --- Migration Is Not One Problem

Separate:

``` text
Algorithm migration
Key migration
Identity migration
Certificate migration
Trust migration
Protocol migration
Application migration
Hardware migration
Firmware migration
```

An RSA-to-ML-DSA transition is not simply:

``` text
replace algorithm name
```

Keys are not generally transformable between unrelated schemes. The
uploaded research highlights key transformation as a major
crypto-agility limitation. fileciteturn1file8L1547-L1579

------------------------------------------------------------------------

# 36. Fundamental Primitive #34 --- Crypto Agility Reverse Proof

Do not merely ask:

> "Is this system crypto agile?"

Actually test it.

Example:

``` text
RSA → ML-DSA
```

Run a controlled sandbox transformation.

Measure:

``` text
Code changes
API changes
Schema changes
Config changes
Protocol changes
Certificate changes
HSM changes
Deployment changes
Test failures
```

If changing the algorithm requires:

``` text
47 code changes
3 API changes
2 schema changes
```

then the system is not truly algorithm-independent.

The uploaded research calls this **Crypto Agility Reverse Proof** and
connects it to NIST's agility definition and IBM's 2026 API assessment.
fileciteturn1file1L325-L377

------------------------------------------------------------------------

# 37. Fundamental Primitive #35 --- Crypto Agility Maturity

A possible maturity framework:

``` text
LEVEL 0 — Unknown
LEVEL 1 — Inventory exists
LEVEL 2 — Crypto identified
LEVEL 3 — Crypto configurable
LEVEL 4 — PQC-ready
LEVEL 5 — Algorithm substitution validated
LEVEL 6 — Policy-driven algorithm selection
LEVEL 7 — Verified state transition
```

Important: the maturity level must be backed by evidence.

Do not call a system "Level 5" merely because a configuration file
exists.

------------------------------------------------------------------------

# 38. Fundamental Primitive #36 --- Migration Invariants

Before changing a system, define properties that must remain true.

Example:

``` text
Authentication continues working
Confidentiality requirement remains satisfied
Latency < 50 ms
No unsupported clients
Auditability preserved
Rollback available
Required trust path remains valid
```

Then:

``` text
BEFORE
  ↓
CHANGE
  ↓
VERIFY INVARIANTS
  ↓
ACCEPT / REJECT
```

This turns migration into a verifiable state transition.

------------------------------------------------------------------------

# 39. Fundamental Primitive #37 --- Migration Attack-Surface Analysis

Migration itself creates a temporary attack surface.

During transition:

``` text
Classical
+
Hybrid
+
PQC
```

may coexist.

This creates:

-   fallback paths
-   dual certificates
-   multiple trust paths
-   multiple key types
-   inconsistent client capabilities
-   downgrade opportunities

Therefore analyze:

``` text
BEFORE MIGRATION
        ↓
TRANSITION STATE
        ↓
AFTER MIGRATION
```

The transition state is often the most interesting security state.

The uploaded research explicitly identifies migration as a security
event rather than assuming migration automatically reduces attack
surface. fileciteturn1file6L1153-L1207

------------------------------------------------------------------------

# 40. Fundamental Primitive #38 --- Cryptographic Rollback Safety

Operational rollback:

``` text
Deployment failed
→ restore old version
```

Cryptographic rollback:

``` text
What security property disappears?
Which assets become vulnerable?
Which clients are affected?
Is classical fallback allowed?
For how long?
Who authorized it?
What evidence is recorded?
```

A rollback can be operationally successful while cryptographically
reintroducing a vulnerable state.

Therefore rollback must be treated as a **security transition**.

------------------------------------------------------------------------

# 41. Fundamental Primitive #39 --- Probabilistic Migration Simulation

Migration plans are not deterministic.

Unknowns include:

-   vendor firmware delivery
-   client compatibility
-   restart behavior
-   undocumented dependencies
-   legacy device failures
-   operational timing
-   performance effects

Represent each migration strategy with:

``` text
Success likelihood
Failure modes
Unknowns
Dependencies
Rollback options
Blast radius
Expected impact
```

Run many scenarios rather than assuming one deterministic future.

The uploaded research explicitly proposes this probabilistic migration
simulator. fileciteturn1file6L1007-L1067

------------------------------------------------------------------------

# 42. Fundamental Primitive #40 --- Unknown Dependency Hunter

Graphs are incomplete.

The most dangerous dependencies may be the ones absent from the graph.

For each migration:

``` text
Proposed Change
      ↓
Assumptions
      ↓
Potential Hidden Dependencies
      ↓
Evidence Search
      ↓
Confidence
```

Example assumption:

> All clients support the new PQ hybrid.

ECDAT searches:

-   historical TLS logs
-   traffic
-   client versions
-   certificates
-   DNS
-   service mesh
-   source repositories

and discovers:

``` text
Unknown legacy client detected.
```

This is **adversarial dependency discovery**.

The uploaded research frames this as asking what dependency would have
to exist for a migration to fail, then actively searching for evidence.
fileciteturn1file6L1071-L1149

------------------------------------------------------------------------

# 43. Fundamental Primitive #41 --- Counter-Hypothesis / Adversarial Verification

For every major conclusion:

``` text
ECDAT believes X.
```

generate:

``` text
What evidence would prove X wrong?
```

Example:

``` text
Claim:
Service is PQ-ready.

Counter-hypotheses:
1. PQ capability exists but is disabled.
2. PQ certificate exists but classical path wins.
3. Client fallback remains enabled.
4. Trust anchor is classical.
5. Hardware cannot perform the PQ operation.
```

Then actively search for disconfirming evidence.

This makes the system less vulnerable to false confidence.

------------------------------------------------------------------------

# 44. Fundamental Primitive #42 --- Cryptographic Chaos Engineering

Borrow the philosophy of chaos engineering.

In a controlled sandbox:

``` text
Remove PQ capability
Expire certificate
Break trust anchor
Reduce MTU
Force old client
Disable HSM feature
Remove preferred algorithm
Force fallback
```

Observe:

``` text
SAFE FAILURE
UNSAFE FAILURE
UNKNOWN
```

Examples:

``` text
PQC unavailable
→ system refuses connection
= SAFE

PQC unavailable
→ silently falls back to RSA
= UNSAFE

PQC unavailable
→ behavior cannot be established
= UNKNOWN
```

This is one of the strongest ways to verify downgrade resistance.

------------------------------------------------------------------------

# 45. Fundamental Primitive #43 --- Migration Digital Twin

Combine:

-   applications
-   services
-   networks
-   users
-   data
-   certificates
-   algorithms
-   keys
-   HSMs
-   hardware
-   vendors
-   dependencies
-   trust relationships
-   deployment history

into a single model.

Then simulate:

``` text
PQC migration
Certificate expiry
Algorithm compromise
Hardware failure
Vendor discontinuation
Trust-anchor change
Rollback
```

This becomes a:

> **Cryptographic Digital Twin.**

The uploaded research describes this as the convergence of the evidence
graph, dependency model and migration simulation.
fileciteturn1file5L890-L921

------------------------------------------------------------------------

# 46. Fundamental Primitive #44 --- Constraint Solver

Do not merely produce:

> "Recommended: ML-DSA."

Let the organization specify:

``` text
Latency < 10 ms
Bandwidth increase < 15%
No hardware replacement
Existing clients must continue working
Rollback must remain possible
Budget < X
Downtime < Y
```

ECDAT evaluates possible migration strategies against these constraints.

Output:

``` text
Strategy A
Constraint violations:
  bandwidth

Strategy B
Constraint violations:
  HSM

Strategy C
Satisfies:
  latency
  bandwidth
  hardware
  client compatibility
  rollback

Strategy D
Requires:
  vendor upgrade
```

The tool should not secretly rank political or business choices; it
should transparently expose constraint satisfaction and trade-offs for
human decision-makers.

------------------------------------------------------------------------

# 47. Fundamental Primitive #45 --- Migration Optimization

The long-term mathematical problem can be formulated as:

``` text
Minimize:

migration cost
+ downtime
+ performance penalty
+ residual security exposure
+ interoperability failures
+ operational disruption

Subject to:

security requirements
business requirements
hardware constraints
vendor constraints
compliance constraints
dependency constraints
rollback constraints
```

The uploaded research explicitly describes this optimization
formulation. fileciteturn1file5L925-L959

Possible optimization techniques:

-   constraint programming
-   integer programming
-   graph optimization
-   multi-objective optimization
-   heuristic search
-   Monte Carlo simulation
-   Pareto-front analysis

The output should expose the trade-off frontier rather than hide it
behind a single score.

------------------------------------------------------------------------

# 48. Fundamental Primitive #46 --- Migration Knowledge Memory

ECDAT should learn from migration outcomes.

Example:

``` text
Migration
  ↓
Failure
  ↓
Root cause
```

Root cause:

``` text
Legacy client only supports RSA.
```

Store this as migration evidence.

Later:

``` text
New system
↓
same dependency pattern
↓
pre-migration warning
```

Over time ECDAT becomes:

> **A cryptographic migration memory.**

Not simply a scanner.

------------------------------------------------------------------------

# 49. Fundamental Primitive #47 --- Discovery Feedback Loop

Static scanners eventually reach blind spots.

Therefore:

``` text
DISCOVER
   ↓
MODEL
   ↓
FIND GAPS
   ↓
SCAN GAPS
   ↓
DISCOVER AGAIN
```

Examples:

``` text
Graph says:
service has unknown dependency

→ launch targeted network investigation

Graph says:
certificate has unknown consumer

→ search logs / trust stores

Graph says:
vendor claims PQ support

→ launch compatibility test
```

This creates **active discovery**.

------------------------------------------------------------------------

# 50. Fundamental Primitive #48 --- Information-Gain-Driven Investigation

Once uncertainty is modeled explicitly, ECDAT can decide what to
investigate next.

For each possible investigation:

``` text
Expected uncertainty reduction
÷
Investigation cost
```

Possible actions:

-   inspect source
-   inspect binary
-   probe endpoint
-   inspect certificate chain
-   inspect runtime
-   query cloud API
-   inspect traffic
-   run compatibility test
-   benchmark hardware

Then choose the investigation that is expected to provide the most
useful information.

This evolves ECDAT from:

> "Scan everything."

to:

> **"Investigate intelligently."**

------------------------------------------------------------------------

# 51. Fundamental Primitive #49 --- Autonomous Cryptographic Investigation Engine

Example:

``` text
Question:
Is Service A truly PQ-authenticated?
```

ECDAT plans:

``` text
1. Inspect certificate
2. Build trust graph
3. Inspect trust anchor
4. Probe TLS
5. Test verifier behavior
6. Check client negotiation
7. Search configuration
8. Compare runtime evidence
9. Look for fallback
10. Produce verification result
```

This is an investigation planner rather than a passive scanner.

------------------------------------------------------------------------

# 52. Fundamental Primitive #50 --- AI Crypto Analyst

AI should sit above structured evidence.

Correct:

``` text
Collectors
   ↓
Evidence Fabric
   ↓
Knowledge Graph
   ↓
Risk Engine
   ↓
AI Reasoning
```

Incorrect:

``` text
Raw enterprise source code
        ↓
LLM
        ↓
"Trust me"
```

AI tasks:

-   explain findings
-   correlate evidence
-   generate investigation hypotheses
-   propose migration candidates
-   explain constraint violations
-   summarize blast radius
-   generate remediation drafts
-   identify contradictory evidence

The AI must not invent evidence.

------------------------------------------------------------------------

# 53. Fundamental Primitive #51 --- Decision Provenance

Every recommendation should be reconstructable:

``` text
Evidence
  ↓
Claims
  ↓
Constraints
  ↓
Threat Model
  ↓
Benchmark Results
  ↓
Compatibility Results
  ↓
Candidate Strategies
  ↓
Rejected Alternatives
  ↓
Human Decision
  ↓
Deployment Outcome
```

This is essential for high-assurance environments.

A future auditor should be able to ask:

> Why did ECDAT recommend this migration?

and receive a reproducible evidence chain.

------------------------------------------------------------------------

# 54. Fundamental Primitive #52 --- ECDAT Itself Must Be Secure

ECDAT will potentially see:

-   source code
-   certificates
-   infrastructure topology
-   crypto configurations
-   HSM metadata
-   cloud architecture
-   sensitive business metadata
-   network structure
-   migration plans

Therefore compromise of ECDAT could give an attacker a map of the
organization's cryptographic defenses.

Security architecture should include:

-   zero-trust collectors
-   least privilege
-   authenticated collection channels
-   encrypted transport
-   encryption at rest
-   RBAC/ABAC
-   tenant isolation
-   immutable audit trail
-   signed evidence
-   tamper detection
-   secure secrets handling
-   private-key material exclusion
-   collector isolation

The uploaded research explicitly identifies ECDAT itself as a high-value
attack surface. fileciteturn0file2L566-L624

------------------------------------------------------------------------

# 55. Fundamental Primitive #53 --- Hostile Input Architecture

A security scanner must assume scanned inputs are hostile.

Potential malicious inputs:

``` text
malicious source
malformed binary
zip bomb
crafted certificate
hostile container
malicious firmware
parser exploit
```

Architecture:

``` text
UNTRUSTED INPUT
      ↓
SANDBOX
      ↓
PARSER
      ↓
NORMALIZED REPRESENTATION
      ↓
ANALYSIS
```

Do not let an enterprise scanner become a remote-code-execution platform
against itself.

------------------------------------------------------------------------

# 56. Fundamental Primitive #54 --- Privacy-Preserving AI

Support:

``` text
Local AI
Cloud AI
```

with policy-controlled routing.

Sensitive environments should allow:

``` text
Enterprise evidence
      ↓
local model
```

while sanitized metadata may be sent to external models where permitted.

AI inputs should preferentially be:

-   structured findings
-   metadata
-   graph relationships
-   sanitized AST fragments
-   non-sensitive summaries

rather than raw enterprise repositories.

------------------------------------------------------------------------

# 57. Fundamental Primitive #55 --- Agentless-First Architecture

Do not assume an agent can be installed everywhere.

Integrate with:

``` text
Git
CI/CD
SIEM
EDR
CMDB
Cloud APIs
Certificate stores
Network scanners
SBOM
CBOM
KMS
HSM
```

ECDAT should be an:

> **Evidence fusion platform.**

not an isolated scanner.

The uploaded research explicitly makes this architectural
recommendation. fileciteturn0file2L700-L735

------------------------------------------------------------------------

# 58. Fundamental Primitive #56 --- Continuous Crypto Monitoring

After migration:

``` text
Observe
 ↓
Compare against expected state
 ↓
Detect drift
 ↓
Investigate
 ↓
Verify
 ↓
Update model
```

Detect:

-   algorithm downgrade
-   certificate replacement
-   unexpected library update
-   trust-anchor change
-   new crypto asset
-   disabled PQC
-   legacy client appearance
-   configuration drift
-   vendor firmware change
-   rollback
-   unexplained cryptographic behavior

------------------------------------------------------------------------

# 59. Fundamental Primitive #57 --- Crypto Regression Detection

Treat cryptography like software regression.

Expected:

``` text
TLS 1.3
Hybrid key exchange
PQ authentication
```

Observed after deployment:

``` text
TLS 1.2
Classical key exchange
```

ECDAT should raise:

> **Cryptographic Regression**

and identify:

-   deployment
-   configuration
-   certificate
-   dependency
-   client
-   rollback
-   vendor change

associated with the regression.

------------------------------------------------------------------------

# 60. Fundamental Primitive #58 --- Blockchain Cryptographic Inventory

Because the SIH theme includes Blockchain & Cybersecurity, support
decentralized systems.

Detect:

``` text
secp256k1
ECDSA
EdDSA
BLS
Merkle trees
hash functions
wallet signatures
multisig
smart-contract cryptography
consensus signatures
zero-knowledge systems
```

Map:

``` text
Wallet
 ↓
Signature
 ↓
Curve
 ↓
Blockchain
 ↓
Asset / smart contract
```

Also analyze:

-   validator authentication
-   node-to-node channels
-   state commitments
-   wallet recovery
-   multisig
-   smart-contract verification

The uploaded research cites recent decentralized-system work on
cryptographic dependency inventory. fileciteturn1file7L1434-L1466

------------------------------------------------------------------------

# 61. Fundamental Primitive #59 --- Crypto Supply-Chain Intelligence

Track:

``` text
Application
 ↓
Library
 ↓
Crypto library
 ↓
Vendor
 ↓
Version
 ↓
Build
 ↓
Binary
```

Questions:

-   Which applications depend on the same crypto library?
-   Which vulnerable implementation version appears across the estate?
-   Which vendor controls the greatest cryptographic dependency?
-   Which libraries are abandoned?
-   Which crypto implementation is no longer maintained?
-   Does a transitive dependency introduce cryptography?

This extends CBOM into **cryptographic supply-chain risk**.

------------------------------------------------------------------------

# 62. Fundamental Primitive #60 --- Implementation Assurance

PQC standardization does not automatically mean implementation security.

Track:

-   library version
-   implementation provenance
-   compiler/toolchain
-   architecture
-   constant-time claims
-   side-channel considerations
-   hardware acceleration
-   known vulnerabilities
-   build flags
-   configuration
-   implementation maturity
-   certification/assurance where relevant

Therefore:

``` text
Algorithm = secure standard
```

does not imply:

``` text
Implementation = secure deployment
```

------------------------------------------------------------------------

# 63. Fundamental Primitive #61 --- Source-vs-Binary Security Gap

A source repository may appear safe while the deployed binary differs.

Model:

``` text
Source
 ↓
Build
 ↓
Artifact
 ↓
Deployment
 ↓
Runtime
```

Compare cryptographic properties at every stage.

Detect:

``` text
Source:
PQC enabled

Build:
old dependency

Binary:
classical crypto

Runtime:
classical crypto
```

This becomes a **cryptographic build-integrity chain**.

------------------------------------------------------------------------

# 64. Fundamental Primitive #62 --- Crypto Build Provenance

Record:

``` text
Source commit
 ↓
Build system
 ↓
Compiler
 ↓
Dependencies
 ↓
Artifact hash
 ↓
Deployment
 ↓
Runtime observation
```

Then tie cryptographic claims to a specific artifact.

This helps prevent:

> "The repository says PQC, therefore production is PQC."

------------------------------------------------------------------------

# 65. Fundamental Primitive #63 --- Secure Migration Sandbox

Before touching production:

``` text
Production model
      ↓
Clone relevant graph
      ↓
Migration candidate
      ↓
Sandbox
      ↓
Synthetic traffic
      ↓
Benchmark
      ↓
Fault injection
      ↓
Security verification
```

The sandbox should support:

-   old clients
-   new clients
-   mixed clients
-   certificates
-   trust stores
-   network conditions
-   MTU variation
-   HSM simulation
-   protocol downgrade attempts
-   rollback testing

------------------------------------------------------------------------

# 66. Fundamental Primitive #64 --- Migration Attack Simulation

Test:

``` text
PQC unavailable
↓
Does system fail closed?

Hybrid negotiation unavailable
↓
Does system fall back?

New certificate rejected
↓
Does service choose old certificate?

Trust anchor missing
↓
Does verifier silently accept classical path?
```

Output:

``` text
SAFE
UNSAFE
UNKNOWN
```

------------------------------------------------------------------------

# 67. Fundamental Primitive #65 --- Migration Blast Radius

For every proposed change:

``` text
Change
 ↓
Affected crypto assets
 ↓
Affected services
 ↓
Affected clients
 ↓
Affected data
 ↓
Affected business processes
```

Then show:

``` text
Direct impact
Indirect impact
Potential impact
Unknown impact
```

The graph should distinguish observed relationships from inferred
relationships.

------------------------------------------------------------------------

# 68. Fundamental Primitive #66 --- Business-Criticality Mapping

Map:

``` text
Crypto
 ↓
System
 ↓
Business Service
 ↓
Business Function
 ↓
Business Impact
```

Example:

``` text
ECDSA
 ↓
Authentication Service
 ↓
Payment Platform
 ↓
Transaction Processing
 ↓
Business-critical
```

This prevents technical risk from being disconnected from operational
reality.

------------------------------------------------------------------------

# 69. Fundamental Primitive #67 --- Cost Intelligence

Migration cost should include more than software engineering.

Potential dimensions:

``` text
Developer effort
Testing
Hardware replacement
Firmware deployment
Certificates
CA changes
HSM changes
Vendor upgrades
Downtime
Network overhead
Bandwidth
Energy
Operational labor
Compliance validation
Training
```

The system should produce a transparent cost model with assumptions.

------------------------------------------------------------------------

# 70. Fundamental Primitive #68 --- Vendor Dependency Intelligence

For each crypto asset:

``` text
Vendor
Supported versions
PQC roadmap
Firmware update path
Hardware replacement path
Support lifetime
Interoperability
Known constraints
```

Then identify:

``` text
Vendor blocker
```

where migration cannot proceed without a third party.

------------------------------------------------------------------------

# 71. Fundamental Primitive #69 --- Migration Readiness Matrix

For every asset:

``` text
Discovery confidence
Quantum exposure
Data lifetime
Migration complexity
Crypto agility
Vendor readiness
Hardware readiness
Trust readiness
PQC compatibility
Verification status
Rollback safety
```

This becomes the migration team's operational dashboard.

------------------------------------------------------------------------

# 72. Fundamental Primitive #70 --- Cryptographic Digital Twin

The full twin contains:

``` text
Enterprise
 ├── Applications
 ├── Services
 ├── Networks
 ├── Users
 ├── Data
 ├── Certificates
 ├── Algorithms
 ├── Keys
 ├── HSMs
 ├── Hardware
 ├── Firmware
 ├── Vendors
 ├── Policies
 └── Dependencies
```

It should support simulations:

``` text
PQC migration
Certificate expiry
Algorithm compromise
Hardware failure
Vendor discontinuation
Trust-anchor replacement
Rollback
Network degradation
Legacy-client appearance
```

This is the architectural convergence point.

------------------------------------------------------------------------

# 72A. Additional Research-Gap Coverage

The following research gaps should be treated as explicit extensions of the
architecture. They are deliberately kept at the research/roadmap level rather
than being presented as mandatory SIH implementation scope.

### Algorithm health and cryptanalytic intelligence

Track changes in algorithm security status, cryptanalytic results, implementation
vulnerabilities, deprecation signals and emergency replacement requirements.
The system should distinguish a standardized algorithm from the current health
of a particular algorithm, implementation or parameter set.

### Sovereign / offline / compartmented operation

Support fully offline and air-gapped deployments, locally verified update
bundles, local models where required, isolated evidence domains and controlled
cross-domain export. This is important for high-assurance environments where
enterprise cryptographic evidence cannot leave the protected environment.

### Federated cryptographic observatory

Extend the enterprise model to sector- or national-scale aggregation without
requiring raw inventories to be centralized. Support privacy-preserving
summaries, federated aggregation, concentration/monoculture analysis and
cross-organization dependency signals.

### Cryptographic canaries for HNDL evidence

A controlled canary mechanism may be used to detect unauthorized access to
specially instrumented sensitive ciphertext or decoy material. A canary event
must be treated as evidence of access/exposure, not proof that an algorithm was
cryptanalytically broken, and must operate only within an authorized test
environment.

### Workload, machine and AI-agent cryptographic identity

Model workload identities, service-mesh identities, device identities, machine
attestation, short-lived credentials and delegated AI-agent identities,
including the credentials and trust domains used by agents to call tools,
services and APIs.

### Expanded cryptographic taxonomy

The inventory should extend beyond conventional TLS/PKI/public-key assets to
include FHE, MPC, threshold cryptography, zero-knowledge systems, QKD, QRNG,
DNSSEC, code and firmware signing, secure boot, archival signatures,
timestamping and specialized cryptographic hardware.

### Validation and certification intelligence

Track assurance and validation evidence where applicable, including exact
implementation/version or part number, validation/certificate identifiers,
algorithm coverage, associated test references, active/interim/historical
status, relevant caveats and whether deployed artifacts actually correspond to
the validated configuration.

### Procurement-time cryptographic debt prevention

Move crypto governance upstream into procurement and architecture decisions:
capture cryptographic requirements in RFIs/RFPs, record vendor evidence and
exceptions, identify crypto-agility and PQC obligations before purchase, and
feed approved requirements into architecture and CI/CD gates.

### Human and organizational readiness

Model ownership, responsibility and migration readiness alongside technical
state. Support readiness assessments, ownership routing and controlled
tabletop or live migration exercises that measure whether teams can execute,
verify and roll back a cryptographic transition under pressure.

### Post-migration retirement and cryptographic end-of-life

Migration is incomplete until the old cryptographic state is retired. Track
key rewrapping, archival migration, trust-anchor replacement, certificate
revocation, old-key destruction or crypto-shredding where appropriate,
deprecated-library/configuration removal, signed retirement evidence and final
verification that the retired path cannot silently return.

------------------------------------------------------------------------

# 73. The Five Research Primitives

After removing feature duplication, the entire system can be compressed
into five fundamental research areas:

## 73.1 Cryptographic Reality

> What is actually happening?

Includes:

-   multi-modal discovery
-   evidence fabric
-   identity resolution
-   runtime observation
-   capability/configuration/negotiation/use separation
-   CBOM projection
-   uncertainty

## 73.2 Cryptographic Causality

> Why did it happen?

Includes:

-   temporal model
-   event stream
-   drift
-   deployment correlation
-   certificate/config changes
-   rollback causality
-   migration history

## 73.3 Cryptographic Change

> What happens if we change it?

Includes:

-   dependency graph
-   change graph
-   blast radius
-   constraint solving
-   probabilistic simulation
-   hidden dependency discovery
-   migration optimization

## 73.4 Cryptographic Assurance

> Did the required security property actually survive?

Includes:

-   security property compiler
-   trust graph
-   authentication verification
-   invariant checking
-   downgrade testing
-   rollback safety
-   chaos engineering
-   implementation assurance

## 73.5 Cryptographic Investigation

> What should the machine investigate next?

Includes:

-   information-gain-driven discovery
-   counter-hypotheses
-   adversarial discovery
-   autonomous investigation
-   evidence collection planning
-   migration verification planning

------------------------------------------------------------------------

# 74. Closed-Loop ECDAT-X

The final system becomes:

``` text
                 ┌───────────────────────┐
                 │       OBSERVE         │
                 │ source/binary/network │
                 │ runtime/cloud/hardware│
                 └───────────┬───────────┘
                             ↓
                 ┌───────────────────────┐
                 │       RECONCILE       │
                 │ evidence + identity   │
                 │ uncertainty + graph   │
                 └───────────┬───────────┘
                             ↓
                 ┌───────────────────────┐
                 │        REASON         │
                 │ risk + lineage + HNDL │
                 │ dependencies + trust  │
                 └───────────┬───────────┘
                             ↓
                 ┌───────────────────────┐
                 │       PREDICT         │
                 │ change impact +       │
                 │ migration simulation  │
                 └───────────┬───────────┘
                             ↓
                 ┌───────────────────────┐
                 │        SOLVE          │
                 │ constraints +         │
                 │ migration strategies  │
                 └───────────┬───────────┘
                             ↓
                 ┌───────────────────────┐
                 │       VALIDATE        │
                 │ invariants + security │
                 │ properties + chaos    │
                 └───────────┬───────────┘
                             ↓
                 ┌───────────────────────┐
                 │       DEPLOY          │
                 └───────────┬───────────┘
                             ↓
                 ┌───────────────────────┐
                 │       OBSERVE AGAIN   │
                 │ drift + regression +  │
                 │ actual outcome         │
                 └───────────┬───────────┘
                             ↓
                         LEARN
                             │
                             └──────────→ OBSERVE
```

This is the central architecture.

------------------------------------------------------------------------

# 75. What Is Actually Novel Here?

Do **not** claim:

> "Nobody has ever thought of these features."

That is not defensible.

The literature already contains pieces:

-   CBOM
-   CADI
-   static crypto discovery
-   binary discovery
-   network probing
-   graph-based migration
-   crypto agility
-   PQC certificate work
-   downgrade protection
-   certificate validation research
-   PQC benchmarks
-   IT/OT migration studies

The stronger novelty claim is:

> **Existing work is fragmented across discovery, inventory, risk,
> migration, interoperability, certificate validation, observability and
> implementation assurance. ECDAT-X proposes an integrated
> evidence-backed closed-loop architecture that treats cryptographic
> reality, uncertainty, causality, change and security-property
> verification as first-class objects.**

That is a much stronger and more defensible research position.

------------------------------------------------------------------------

# 76. Research Questions

A serious paper/project can formulate the following research questions.

### RQ1 --- Cryptographic Reality

Can multi-modal evidence fusion produce a more accurate representation
of enterprise cryptographic usage than any individual discovery method?

### RQ2 --- Uncertainty

Can uncertainty-aware modeling reduce false-confidence errors in
cryptographic inventories?

### RQ3 --- Temporal Causality

Can temporal correlation identify the root cause of cryptographic drift
and downgrade events?

### RQ4 --- Change Prediction

Can a cryptographic dependency graph predict migration blast radius more
accurately than asset-by-asset assessment?

### RQ5 --- Hidden Dependencies

Can adversarial information gathering discover undocumented migration
dependencies before deployment?

### RQ6 --- Agility

Can controlled algorithm substitution provide stronger evidence of
crypto agility than static maturity scoring?

### RQ7 --- Verification

Can security-property verification detect migration failures that
ordinary CBOM or certificate checks miss?

### RQ8 --- Migration Optimization

Can probabilistic migration planning reduce expected disruption while
maintaining explicit security invariants?

### RQ9 --- Continuous Assurance

Can post-migration observation detect cryptographic regression earlier
than periodic inventory scans?

### RQ10 --- Digital Twin

Can a cryptographic digital twin accurately simulate enterprise
migration outcomes under uncertainty?

------------------------------------------------------------------------

# 77. Proposed Data Model

At minimum, the internal model should contain:

``` text
Asset
System
Application
Service
Repository
Build
Artifact
Binary
Container
Process
NetworkEndpoint
Protocol
Algorithm
Key
Certificate
TrustAnchor
CA
Library
CryptoImplementation
HSM
KMS
TPM
Hardware
Firmware
DataAsset
BusinessService
Vendor
Policy
SecurityProperty
Migration
Evidence
Observation
Claim
Event
Constraint
Invariant
Experiment
Benchmark
Simulation
Decision
Outcome
```

### Core relationship types

``` text
USES
IMPLEMENTS
PROVIDES
CONSUMES
CONFIGURES
NEGOTIATES
OBSERVES
PROTECTS
AUTHENTICATES
DEPENDS_ON
ISSUED_BY
TRUSTS
RUNS_ON
BUILT_FROM
DEPLOYED_AS
AFFECTS
REQUIRES
CONTRADICTS
SUPPORTS
VERIFIES
VIOLATES
REPLACES
ROLLS_BACK_TO
```

------------------------------------------------------------------------

# 78. Evidence Object

Every observation should conceptually look like:

``` json
{
  "claim": "service-A uses ECDSA P-256",
  "subject": "service-A",
  "algorithm": "ECDSA-P256",
  "source": "tls-handshake",
  "method": "active-probe",
  "timestamp": "...",
  "freshness": "...",
  "confidence": 0.98,
  "scope": "production-edge",
  "status": "OBSERVED"
}
```

The implementation can use a relational/event-store/graph hybrid, but
the conceptual model should preserve provenance.

------------------------------------------------------------------------

# 79. Risk Model

Avoid one opaque score.

Expose multiple dimensions:

``` text
Quantum Exposure
HNDL Exposure
Business Criticality
Data Sensitivity
Dependency Centrality
Migration Complexity
Implementation Risk
Vendor Risk
Hardware Risk
Trust Risk
Downgrade Risk
Uncertainty
Systemic Concentration
```

Then provide a policy-defined prioritization layer.

This makes the reasoning auditable.

------------------------------------------------------------------------

# 80. What ECDAT-X Should Never Do

### Never claim certainty without evidence.

### Never equate library presence with actual cryptographic use.

### Never equate PQ capability with PQ deployment.

### Never equate a PQ certificate with PQ authentication.

### Never equate algorithm replacement with complete migration.

### Never treat rollback as automatically safe.

### Never send sensitive source to an external AI model by default.

### Never trust scanned input.

### Never assume the dependency graph is complete.

### Never hide assumptions behind one opaque risk number.

### Never claim a research component is novel merely because it is implemented in one platform.

------------------------------------------------------------------------

# 81. Build vs Research Split

## Buildable SIH core

A realistic high-impact prototype can implement:

1.  Source scanner
2.  Binary/container scanner
3.  Certificate/PKI scanner
4.  Network TLS scanner
5.  CBOM generator
6.  Evidence store
7.  Asset identity
8.  Cryptographic knowledge graph
9.  Quantum/HNDL risk
10. Dependency analysis
11. PQC recommendation
12. PQC benchmark lab
13. Migration dependency visualization
14. Crypto-agility analysis
15. Security-property checks
16. Interactive dashboard
17. Continuous drift detection

## Research-grade extensions

Prototype experimentally:

1.  Cryptographic epistemology
2.  Temporal crypto event stream
3.  Causal drift analysis
4.  Security Property Compiler
5.  Crypto Agility Reverse Proof
6.  Probabilistic migration simulation
7.  Unknown Dependency Hunter
8.  Cryptographic Chaos Engineering
9.  Information-gain-driven discovery
10. Digital twin
11. Migration optimization
12. Decision provenance

This distinction lets the SIH build remain credible while preserving a
strong research roadmap.

------------------------------------------------------------------------

# 82. Suggested Module Architecture

``` text
ECDAT-X/
│
├── collectors/
│   ├── source/
│   ├── ast/
│   ├── binary/
│   ├── container/
│   ├── runtime/
│   ├── network/
│   ├── certificate/
│   ├── cloud/
│   ├── hardware/
│   └── firmware/
│
├── evidence/
│   ├── provenance/
│   ├── confidence/
│   ├── contradiction/
│   └── freshness/
│
├── identity/
│   ├── entity-resolution/
│   └── asset-correlation/
│
├── knowledge/
│   ├── crypto-graph/
│   ├── dependency-graph/
│   ├── trust-graph/
│   ├── data-lineage/
│   └── temporal-model/
│
├── risk/
│   ├── quantum/
│   ├── hndl/
│   ├── business/
│   ├── systemic/
│   ├── implementation/
│   └── uncertainty/
│
├── migration/
│   ├── recommendation/
│   ├── constraints/
│   ├── simulation/
│   ├── optimization/
│   ├── blast-radius/
│   └── rollback/
│
├── verification/
│   ├── invariants/
│   ├── security-properties/
│   ├── trust-validation/
│   ├── downgrade/
│   ├── chaos/
│   └── regression/
│
├── ai/
│   ├── analyst/
│   ├── investigation-planner/
│   ├── explanation/
│   └── remediation/
│
├── benchmark/
│   ├── classical/
│   ├── pqc/
│   ├── hybrid/
│   └── constrained-device/
│
└── ui/
    ├── command-center/
    ├── graph/
    ├── risk/
    ├── migration/
    ├── evidence/
    └── verification/
```

------------------------------------------------------------------------

# 83. Final Product Definition

The strongest definition is:

> **ECDAT-X is an enterprise cryptographic observability, reasoning,
> migration and verification platform that constructs an evidence-backed
> Cryptographic Reality Graph from heterogeneous sources; models
> uncertainty, temporal behavior, dependencies, trust and data lineage;
> evaluates quantum and systemic exposure; simulates and optimizes
> cryptographic state transitions; validates security invariants and
> authentication properties; and continuously monitors the deployed
> environment for cryptographic regression, downgrade and drift.**

------------------------------------------------------------------------

# 84. Final Research Vision

The ultimate lifecycle is:

``` text
OBSERVE REALITY
      ↓
BUILD CRYPTOGRAPHIC MODEL
      ↓
QUANTIFY UNCERTAINTY
      ↓
UNDERSTAND SECURITY PROPERTIES
      ↓
MAP DEPENDENCIES
      ↓
MODEL CHANGE
      ↓
SEARCH FOR SAFE TRANSITIONS
      ↓
SIMULATE
      ↓
VERIFY
      ↓
EXECUTE
      ↓
ATTACK / FAULT TEST
      ↓
OBSERVE PRODUCTION
      ↓
COMPARE PREDICTION VS REALITY
      ↓
LEARN
      ↓
REPEAT
```

The central research question is therefore:

> **Can a machine maintain an evidence-backed model of an organization's
> cryptographic reality, quantify uncertainty, predict the consequences
> of cryptographic changes, find a safe transition under explicit
> constraints, and produce verifiable evidence that required security
> properties survived that transition?**

That is the problem worth building ECDAT-X around.

------------------------------------------------------------------------

# 85. Research References & Evidence Base

The following references are the primary research/standards basis
represented in the uploaded corpus and the preceding research.

## NIST

1.  **NIST NCCoE --- Migration to Post-Quantum Cryptography**\
    https://www.nccoe.nist.gov/applied-cryptography/migration-to-pqc\
    Used for migration phases, cryptographic visibility/risk management,
    interoperability and benchmarking.

2.  **NIST CSWP 39-upd1 --- Considerations for Achieving Crypto Agility:
    Strategies and Practices (2026)**\
    https://csrc.nist.gov/pubs/cswp/39/upd1/considerations-for-achieving-crypto-agility/final\
    Used for the crypto-agility definition and agility
    strategies/metrics.

3.  **NIST Next-Generation Secure Hardware Workshop / IR 8615**\
    https://csrc.nist.gov/pubs/ir/8615/final\
    Used for hardware lifecycle/root-of-trust considerations.

4.  **NIST PIV PQC-related work**\
    Used for trust/identity migration and dual-stack considerations.

## IETF

5.  **Cryptographic Asset Discovery and Inventory (CADI)
    Internet-Draft**\
    https://datatracker.ietf.org/doc/draft-liu-cadi/\
    Used for multi-modal discovery, active/passive methods, legacy black
    boxes, runtime/network approaches and continuous inventory.

6.  **PQC Readiness Gaps / Network Observability Internet-Draft**\
    https://datatracker.ietf.org/doc/draft-vicente-pquip-pqc-readiness-gaps/\
    Used for the capability/configuration/negotiation/actual-use
    distinction and the limits of existing network telemetry.

7.  **PQC Application / Trust Path Internet-Draft**\
    https://datatracker.ietf.org/doc/draft-ietf-uta-pqc-app/\
    Used for trust-anchor and full validation-path considerations.

8.  **PQC Continuity / Downgrade Protection Internet-Draft**\
    https://datatracker.ietf.org/doc/draft-sheffer-tls-pqc-continuity/\
    Used for migration-state downgrade and rollback considerations.

9.  **Composite ML-DSA X.509 / PQT hybrid certificate drafts**\
    IETF Datatracker working drafts.\
    Used for certificate/trust migration analysis.

## IBM Research

10. **The Anatomy of Cryptography Bills of Materials: Standardization
    and Practice in CycloneDX**\
    https://research.ibm.com/publications/the-anatomy-of-cryptography-bills-of-materials-standardization-and-practice-in-cyclonedx\
    Used for CBOM evidence, configuration-driven cryptography, naming
    ambiguity and provider/consumer semantics.

11. **Cryptography Code Discovery and Remediation**\
    https://research.ibm.com/projects/cryptography-code-discovery-and-remediation\
    Used for semantic/static crypto discovery and AI-assisted
    remediation direction.

12. **Cryptographic Agility for Applications: An Assessment Framework
    and Principled API Design**\
    https://research.ibm.com/publications/cryptographic-agility-for-applications-an-assessment-framework-and-principled-api-design\
    Used for crypto-agility API limitations, policy-driven selection and
    key-transformation gaps.

## Academic / Research Literature

13. **Dependency-Aware Post-Quantum Cryptography Migration Planning:
    Graph-Based Optimization for Enterprise Infrastructure** --- IEEE,
    2026.\
    https://ieeexplore.ieee.org/abstract/document/11541993/authors\
    Used for dependency-aware migration ordering and graph optimization.

14. **A graph-based framework for cryptographic risk modeling in the
    post-quantum transition** --- Information and Software Technology /
    Elsevier, 2026.\
    https://www.sciencedirect.com/science/article/pii/S0950584926000881\
    Used for graph-based crypto risk and dependency propagation.

15. **Survey on post-quantum cryptography implementations and deployment
    challenges** --- 2026.\
    https://www.sciencedirect.com/science/article/pii/S0167739X25003577\
    Used for performance, memory, communication, side-channel and
    deployment constraints.

16. **Classical Acceptance Is Not Hybrid Authentication** --- 2026.\
    https://arxiv.org/abs/2607.20800\
    Used for verifier-semantics and outcome-bearing PQ authentication
    analysis.

17. **Quantum-Safe Software Engineering / PQC-aware software migration
    research** --- 2026.\
    https://arxiv.org/abs/2602.05759\
    Used for semantic refactoring, PQC-aware detection and hybrid
    verification.

18. **PQC implementation on constrained ARM-class devices** --- 2026.\
    Used for constrained-device performance/energy considerations.

19. **Post-quantum pairing / Bluetooth deployment research** --- 2026.\
    Used for protocol payload, airtime, retransmission and energy
    constraints.

20. **IT/OT PQC migration research** --- 2026.\
    Used for differences between software-centric IT migration and
    long-lived OT constraints.

21. **Industrial PQC certificate research** --- 2025--2026.\
    Used for industrial certificate migration and
    hybrid/composite/chameleon certificate issues.

22. **Non-invasive PQC proxy for legacy industrial systems** --- 2026.\
    Used for gateway/proxy approaches when legacy hardware cannot be
    directly upgraded.

23. **Recent decentralized-system cryptographic dependency inventory
    research** --- ACM, 2026.\
    DOI: https://doi.org/10.1145/3774905.3794696\
    Used for blockchain/wallet/node/state-commitment cryptographic
    inventory.

## CycloneDX

24. **CycloneDX CBOM Capability**\
    https://cyclonedx.org/capabilities/cbom/\
    Used for CBOM representation and certificate/cryptographic
    relationships.

------------------------------------------------------------------------

# 86. Important Research-Integrity Note

The system should distinguish three categories of claims:

### Established / standardized direction

Examples:

-   NIST PQC migration guidance
-   NIST crypto agility
-   CycloneDX CBOM
-   IETF CADI work

### Active research / draft-stage direction

Examples:

-   CADI as an Internet-Draft
-   network cryptographic observability drafts
-   PQC continuity drafts
-   graph-based migration optimization
-   verifier-semantics research

### ECDAT-X synthesis / proposed research

Examples:

-   Cryptographic Epistemology Engine
-   Cryptographic Time Machine
-   Crypto Agility Reverse Proof
-   Security Property Compiler
-   Unknown Dependency Hunter
-   information-gain-driven cryptographic investigation
-   Cryptographic Chaos Engineering
-   integrated Cryptographic Digital Twin
-   closed-loop state-transition verification

The project should explicitly say when a component is an original
architectural synthesis rather than a standardized capability.

------------------------------------------------------------------------

# 87. One-Sentence Vision

> **ECDAT-X does not merely discover cryptography; it attempts to
> establish cryptographic reality, understand its uncertainty and
> dependencies, predict what happens when it changes, find a safe
> migration path, verify that the required security properties survived,
> and continuously detect when reality diverges from the intended secure
> state.**

------------------------------------------------------------------------

# Appendix A --- Full Uploaded Research Corpus

## Uploaded Research Note 1

Yes. I went much deeper than the PS itself --- into **NIST's current
PQC-migration work, NIST's 2026 crypto-agility paper, IETF's 2026
Cryptographic Asset Discovery draft, CycloneDX/CBOM, IBM Research,
recent IEEE/Elsevier research, NCSC guidance, NSA guidance, and recent
migration/optimization research**.

And I agree with your instinct:

> **A basic implementation of this PS is only the first layer.**
>
> If you want something that feels like **serious R&D rather than "we
> made a CBOM scanner"**, there is a huge amount we can add.

The interesting part is that some of the strongest ideas are **not
futuristic fantasies**. They are directions that NIST, IETF, IBM
Research and recent academic work are already moving toward.
[NCCoE](https://www.nccoe.nist.gov/applied-cryptography/migration-to-pqc?utm_source=chatgpt.com)

------------------------------------------------------------------------

# 🚀 First, let's redefine what we're building

Basic ECDAT:

``` text
Scan
 ↓
Find crypto
 ↓
CBOM
 ↓
Risk
 ↓
PQC recommendation
```

That's basically the PS.

But advanced ECDAT could become:

``` text
                    ECDAT-X
                       │
       ┌───────────────┼────────────────┐
       ↓               ↓                ↓
   DISCOVERY        INTELLIGENCE     MIGRATION
       │               │                │
       ↓               ↓                ↓
 Source             Risk Engine       Simulation
 Binary             Attack Graph      Dependency plan
 Container          AI reasoning      Auto-remediation
 Network            Data lineage      Crypto-agility
 Runtime            Forecasting       Validation
 Hardware           Compliance        Rollback
 Cloud              Supply chain      Continuous monitor
 Firmware
       │               │                │
       └───────────────┼────────────────┘
                       ↓
                 CRYPTOGRAPHIC
                  DIGITAL TWIN
                       ↓
                 ENTERPRISE PQC
                  COMMAND CENTER
```

**That** is where the 90% is.

------------------------------------------------------------------------

# 1. 🔥 Upgrade #1 --- Don't just scan source code

This is probably the first major advancement.

The current PS explicitly asks for:

-   source repositories
-   binaries
-   libraries
-   container images

But modern cryptographic discovery research is already moving toward
**multiple discovery modes**.

A 2026 IETF Internet-Draft on Cryptographic Asset Discovery and
Inventory (CADI) explicitly discusses:

-   static source scanning
-   CBOM declarations
-   binary/image scanning
-   CI/CD integration
-   active protocol probing
-   passive identification
-   TLS/IPsec/SSH discovery
-   legacy black-box systems

and points out that legacy systems can be impossible to instrument
directly. [IETF
Datatracker](https://datatracker.ietf.org/doc/draft-liu-cadi/?utm_source=chatgpt.com)

So our scanner should become:

``` text
                 DISCOVERY ENGINE
                       │
       ┌───────┬───────┼────────┬─────────┐
       ↓       ↓       ↓        ↓         ↓
     Source  Binary  Container Network  Runtime
       │       │       │        │         │
       └───────┴───────┼────────┴─────────┘
                       ↓
                    Hardware
                       ↓
                     Cloud
                       ↓
                   Firmware
```

This alone makes the system much more serious.

------------------------------------------------------------------------

# 2. 🧠 Upgrade #2 --- Semantic crypto discovery

A basic scanner does:

``` text
search("RSA")
search("AES")
search("ECDSA")
```

That's weak.

Suppose:

``` python
encrypt_document(data)
```

and inside another library:

``` python
encrypt_document()
      ↓
crypto_wrapper()
      ↓
OpenSSL
      ↓
EVP_EncryptInit
      ↓
AES-256-GCM
```

A simple scanner misses the real relationship.

So build a:

## **Semantic Cryptography AST Engine**

It understands:

``` text
Code
 ↓
AST
 ↓
Control flow
 ↓
Data flow
 ↓
Function calls
 ↓
Crypto API
 ↓
Algorithm
 ↓
Parameters
 ↓
Purpose
```

IBM Research is already doing code-level crypto discovery using static
analysis to identify cryptographic assets rather than simply counting
calls to crypto libraries. [IBM
Research](https://research.ibm.com/projects/cryptography-code-discovery-and-remediation?utm_source=chatgpt.com)

That gives us a major research direction:

### **Crypto Semantics Engine**

Instead of:

> "I found `RSA`."

It says:

> "This function generates an RSA-2048 key which is subsequently used
> for digital signatures in the authentication service."

That's a **huge difference**.

------------------------------------------------------------------------

# 3. 🔬 Upgrade #3 --- Data-flow aware cryptography

This gets even better.

Suppose:

``` text
User password
     ↓
Authentication service
     ↓
Hash
     ↓
Database
```

Your tool should understand the flow.

Or:

``` text
Government secret
      ↓
AES encryption
      ↓
Database
      ↓
Backup
      ↓
Cloud storage
```

Now your system knows:

> **Which cryptographic mechanism protects which data.**

This is far more useful than just finding algorithms.

You can build:

# **Crypto → Data → System lineage**

For example:

``` text
SECRET-DATA-001
      │
      ↓
Payment Service
      │
      ↓
AES-256-GCM
      │
      ↓
Database
      │
      ↓
Backup
      │
      ↓
Cloud Storage
```

Then if a cryptographic component changes, you immediately know what
data is affected.

------------------------------------------------------------------------

# 4. 🔥 Upgrade #4 --- Build a Crypto Dependency Graph

This is one of my **favorite additions**.

Don't represent the organization as a table.

Represent it as a **graph**.

``` text
             Application
                  │
             uses │
                  ↓
             OpenSSL
                  │
          implements
                  ↓
             ECDSA
                  │
             protects
                  ↓
            Certificate
                  │
             authenticates
                  ↓
              API Server
                  │
             accesses
                  ↓
           Sensitive DB
```

Now you can answer questions like:

> "If ECDSA becomes unacceptable, what systems are affected?"

Instead of manually searching 50,000 records:

``` text
ECDSA
 ↓
47 certificates
 ↓
19 services
 ↓
7 APIs
 ↓
3 business systems
 ↓
2 critical datasets
```

This is where graph databases become extremely useful.

And recent 2026 research is explicitly exploring **dependency-aware PQC
migration planning using cryptographic dependency graphs and graph
optimization**. [IEEE
Xplore](https://ieeexplore.ieee.org/abstract/document/11541993/authors?utm_source=chatgpt.com)

------------------------------------------------------------------------

# 5. 🚨 Upgrade #5 --- Attack-path / quantum attack graph

Now let's go one step further.

Suppose:

``` text
RSA-2048
   ↓
Authentication
   ↓
Admin API
   ↓
Sensitive Database
```

Your system should understand:

> "This isn't just one vulnerable RSA asset."

It's a **potential attack path**.

So build:

# Quantum Attack Graph

``` text
Quantum-vulnerable crypto
          ↓
Authentication weakness
          ↓
Identity compromise
          ↓
Service access
          ↓
Sensitive data
```

Then calculate:

``` text
Quantum exposure
+
business impact
+
dependency centrality
+
data sensitivity
=
priority
```

This is much more intelligent than:

``` text
RSA = HIGH
```

------------------------------------------------------------------------

# 6. 🧬 Upgrade #6 --- "Cryptographic DNA" of an organization

This could be a killer UI feature.

Give every application a:

## Cryptographic DNA

Example:

``` text
PAYMENT-SERVICE

Symmetric:
AES-256-GCM

Hash:
SHA-256

Key exchange:
ECDH P-256

Signature:
ECDSA P-256

TLS:
TLS 1.3

Certificates:
X.509

Libraries:
OpenSSL 3.x

PQC readiness:
38%

Crypto agility:
LOW
```

Then compare:

``` text
PAYMENT SERVICE
████████████████░░░░ 80%

AUTH SERVICE
██████████░░░░░░░░░░ 50%

LEGACY SERVICE
████░░░░░░░░░░░░░░░░ 20%
```

Now the organization gets a **crypto posture scorecard**.

------------------------------------------------------------------------

# 7. ⚡ Upgrade #7 --- Crypto-agility score

This is a **major modern direction**.

NIST's 2026 final guidance defines crypto agility as the capability to
replace/adapt cryptographic algorithms across protocols, applications,
software, hardware, firmware and infrastructure **without breaking
ongoing operations**. [NIST Computer Security Resource
Center](https://csrc.nist.gov/pubs/cswp/39/upd1/considerations-for-achieving-crypto-agility/final?utm_source=chatgpt.com)

So don't only ask:

> "Is RSA vulnerable?"

Ask:

> **"How difficult would it be to replace RSA in this system?"**

For example:

### System A

``` text
Algorithm stored in config
      ↓
One-line change
      ↓
Restart
```

Crypto agility:

``` text
HIGH
```

### System B

``` text
Algorithm hardcoded
      ↓
Firmware
      ↓
Hardware dependency
      ↓
Vendor dependency
      ↓
No OTA update
```

Crypto agility:

``` text
VERY LOW
```

This is extremely valuable.

------------------------------------------------------------------------

# 8. 🔥 Upgrade #8 --- Crypto-agility maturity model

We can make:

``` text
LEVEL 0
Unknown

LEVEL 1
Inventory exists

LEVEL 2
Crypto identified

LEVEL 3
Crypto centrally configurable

LEVEL 4
PQC-ready

LEVEL 5
Algorithm can be swapped automatically
```

Then:

``` text
Enterprise Crypto Agility:
LEVEL 2 / 5
```

And explain why.

NIST's crypto-agility work specifically identifies the need for
environment-specific strategies, frameworks and metrics and discusses
the development of maturity models/KPIs. [NIST Computer Security
Resource
Center](https://csrc.nist.gov/pubs/cswp/39/considerations-for-achieving-cryptographic-agility/2pd?utm_source=chatgpt.com)

So this isn't something we're inventing out of nowhere.

------------------------------------------------------------------------

# 9. 🤖 Upgrade #9 --- AI Crypto Analyst

Now we can use AI, but **not just as a chatbot**.

Imagine clicking:

> **Why is this system high risk?**

AI receives structured evidence:

``` text
Algorithm = RSA-2048
Purpose = authentication
Data lifetime = 14 years
Business criticality = critical
Migration effort = high
Dependency count = 38
Certificate expiry = 2027
```

Then generates:

> "This system is prioritized because..."

But here's the important part:

## AI should never invent the evidence.

Architecture:

``` text
Scanner
   ↓
Evidence database
   ↓
Risk engine
   ↓
AI explanation layer
```

Not:

``` text
LLM
 ↓
"trust me bro"
```

IBM Research is already exploring AI-assisted cryptographic remediation,
while a 2025 empirical study found promising results for LLM-based
detection and fixing of real-world crypto API misuse. [IBM
Research](https://research.ibm.com/projects/cryptography-code-discovery-and-remediation?utm_source=chatgpt.com)

------------------------------------------------------------------------

# 10. 🛠️ Upgrade #10 --- Automatic remediation

This is where ECDAT becomes REALLY interesting.

Current:

``` text
Found vulnerable RSA
```

Advanced:

``` text
Found vulnerable RSA
       ↓
Locate code
       ↓
Understand usage
       ↓
Determine purpose
       ↓
Generate migration patch
       ↓
Run tests
       ↓
Run crypto scanner again
       ↓
Show diff
```

Example:

``` diff
- RSA-2048
+ ML-DSA-65
```

Or for a protocol:

``` text
ECDH
   ↓
Hybrid X25519 + ML-KEM
```

But the tool should **not automatically deploy changes**.

Instead:

``` text
AI-generated migration patch
          ↓
Developer review
          ↓
Tests
          ↓
Security validation
          ↓
Approve
```

That is much safer.

------------------------------------------------------------------------

# 11. 🧪 Upgrade #11 --- PQC migration laboratory

This is one of the biggest additions I'd make.

The PS asks:

> Recommend PQC/hybrid algorithms based on latency and cost.

Don't merely recommend.

## Actually test them.

Build:

# PQC Benchmark Lab

Take:

``` text
Current:
ECDH + ECDSA
```

Test:

``` text
ML-KEM
ML-DSA
Hybrid
```

Measure:

``` text
CPU
RAM
latency
bandwidth
handshake size
key size
signature size
energy
throughput
```

Recent research shows that PQC deployment can have relatively modest
compute costs in some environments but significantly larger protocol
messages, making bandwidth and deployment context important.
[ScienceDirect](https://www.sciencedirect.com/science/article/pii/S0167739X25003577?utm_source=chatgpt.com)

So ECDAT can say:

> **Don't blindly migrate. Benchmark first.**

------------------------------------------------------------------------

# 12. 📡 Upgrade #12 --- Live network discovery

This is huge.

Imagine you don't have source code.

You have:

``` text
10.20.30.15
```

ECDAT probes the service.

It discovers:

``` text
TLS
 ↓
Supported cipher suites
 ↓
Key exchange
 ↓
Certificate
 ↓
Signature
```

The 2026 IETF CADI draft explicitly discusses active probing for
protocols such as TLS, IPsec and SSH. [IETF
Datatracker](https://datatracker.ietf.org/doc/draft-liu-cadi/?utm_source=chatgpt.com)

So:

``` text
Source scanner
+
Network scanner
```

becomes much more powerful.

------------------------------------------------------------------------

# 13. 👻 Upgrade #13 --- Passive network discovery

Even better:

Don't touch the system.

Observe traffic metadata from an authorized monitoring point.

``` text
Network traffic
       ↓
TLS handshake
       ↓
Cipher suite
       ↓
Certificate
       ↓
Crypto inventory
```

This helps with:

``` text
legacy systems
black boxes
vendor appliances
IoT
industrial systems
```

This is exactly the sort of problem the CADI work discusses: many legacy
devices cannot have software installed on them. [IETF
Datatracker](https://datatracker.ietf.org/doc/draft-liu-cadi/?utm_source=chatgpt.com)

------------------------------------------------------------------------

# 14. 🖥️ Upgrade #14 --- Runtime crypto discovery

Static analysis tells you:

> "The application contains this crypto."

Runtime analysis asks:

> **"What crypto is actually being executed?"**

Architecture:

``` text
Application
     ↓
Runtime instrumentation
     ↓
Crypto API calls
     ↓
Algorithm
     ↓
Parameters
     ↓
Actual usage
```

This helps detect:

``` text
dead code
dynamic libraries
runtime configuration
feature flags
plugins
environment-dependent crypto
```

Then you can compare:

``` text
STATIC INVENTORY
        vs
RUNTIME INVENTORY
```

and show:

> **"Declared crypto ≠ observed crypto."**

That's a genuinely interesting research feature.

------------------------------------------------------------------------

# 15. 📦 Upgrade #15 --- Supply-chain crypto intelligence

This is massive.

Suppose your company uses:

``` text
Library A
 ↓
Library B
 ↓
OpenSSL
 ↓
RSA
```

But your team doesn't own Library A.

So your system should ask:

> "Which third-party dependencies contain quantum-vulnerable
> cryptography?"

Build:

``` text
Your Application
       ↓
Dependency tree
       ↓
Third-party library
       ↓
Crypto implementation
       ↓
Quantum vulnerability
```

Then:

> **"You don't use RSA directly, but dependency X does."**

CBOM already emphasizes the distinction between a library **providing**
cryptographic capability and an application actually **using** it.
[CycloneDX](https://cyclonedx.org/guides/OWASP_CycloneDX-Authoritative-Guide-to-CBOM-en.pdf?utm_source=chatgpt.com)

------------------------------------------------------------------------

# 16. 🔗 Upgrade #16 --- SBOM + CBOM + HBOM + OBOM

This is another advanced direction.

Don't keep CBOM isolated.

CycloneDX now supports a broader BOM ecosystem including:

-   SBOM
-   CBOM
-   HBOM
-   SaaSBOM
-   ML-BOM
-   OBOM
-   VEX
-   attestations

under its broader transparency model. [OWASP
Foundation](https://owasp.org/projects/cyclonedx?utm_source=chatgpt.com)

So:

``` text
                 ENTERPRISE
                     │
       ┌─────────────┼─────────────┐
       ↓             ↓             ↓
     SBOM          CBOM          HBOM
       ↓             ↓             ↓
    Software      Crypto        Hardware
       │             │             │
       └─────────────┼─────────────┘
                     ↓
              SYSTEM GRAPH
```

Now ECDAT understands the **whole stack**.

------------------------------------------------------------------------

# 17. 🔐 Upgrade #17 --- Secret/key exposure detection

Don't only find algorithms.

Find dangerous key practices:

``` text
hardcoded keys
hardcoded IVs
weak random generation
keys in source code
keys in Docker images
keys in config
expired certificates
unused certificates
weak certificates
private-key exposure
```

But importantly:

### Never put discovered secrets into your CBOM/report.

Instead:

``` text
SECRET DETECTED
SHA-256 fingerprint: abc123...
Location: config.yaml:42
Status: REDACTED
```

This makes the scanner useful as a normal security tool too.

------------------------------------------------------------------------

# 18. 🪪 Upgrade #18 --- Certificate intelligence

Create an entire certificate module.

For every certificate:

``` text
Domain
Issuer
Algorithm
Key size
Signature
Expiry
Chain
Usage
System
Owner
Quantum status
```

Then:

### Certificate attack surface

``` text
Expired certificates
Weak signatures
Quantum-vulnerable signatures
Unknown ownership
Near-expiry certificates
Untrusted issuers
```

And:

> **"Which certificates will need PQC migration?"**

------------------------------------------------------------------------

# 19. 🏦 Upgrade #19 --- HSM/KMS intelligence

The PS specifically mentions hardware modules and cloud services.

So build integrations eventually for:

``` text
HSM
KMS
PKI
Certificate Authority
TPM
Secure Enclave
```

And discover:

``` text
What algorithms are supported?
What algorithms are actually used?
Which keys depend on them?
Can firmware be upgraded?
Does the vendor support PQC?
```

This is particularly important because hardware can be **much harder to
migrate** than software.

NIST's migration work explicitly includes interoperability testing
involving HSMs, and NCSC notes the importance of long-lived hardware
roots of trust. [NIST Computer Security Resource
Center](https://csrc.nist.gov/pubs/cswp/48/mapping-migration-to-pqc-project-capabilities-to-r/ipd?utm_source=chatgpt.com)

------------------------------------------------------------------------

# 20. 🛰️ Upgrade #20 --- Firmware / IoT / embedded discovery

Now we're entering serious enterprise territory.

Scan:

``` text
firmware.bin
bootloader
IoT device
router
gateway
industrial controller
sensor
```

Find:

``` text
crypto libraries
crypto constants
certificate stores
signature verification
secure boot
TLS
SSH
```

Then ask:

> Can this device actually be upgraded?

Because:

``` text
Software:
easy-ish

Firmware:
harder

Hardware:
VERY hard
```

That's why the migration planner needs an **upgradeability score**.

------------------------------------------------------------------------

# 21. ⚙️ Upgrade #21 --- PQC performance simulator

This could become a major research component.

For every proposed migration:

``` text
Current
ECDH
 ↓
Candidate
X25519 + ML-KEM-768
```

simulate:

``` text
CPU impact
Memory impact
Bandwidth impact
Latency
Storage
Certificate size
Energy
```

Then:

``` text
Migration candidate A

Security: ★★★★★
Latency: +4%
Bandwidth: +20%
Cost: Low
Compatibility: High
```

vs

``` text
Candidate B

Security: ★★★★★
Latency: +18%
Bandwidth: +50%
Cost: High
Compatibility: Medium
```

**Don't rank them with arbitrary scores without explaining the
criteria.** Instead give transparent measurements and let the operator
choose.

------------------------------------------------------------------------

# 22. 🌐 Upgrade #22 --- Real TLS PQC testing

And this is especially timely.

In August 2026, IETF published **RFC 10024**, defining three PQ/T hybrid
TLS 1.3 key-agreement mechanisms:

``` text
X25519MLKEM768
SecP256r1MLKEM768
SecP384r1MLKEM1024
```

which combine classical ECDHE with ML-KEM. [IETF
Datatracker](https://datatracker.ietf.org/doc/html/rfc10024?utm_source=chatgpt.com)

So our tool could actually have:

``` text
                    TLS LAB
                       │
       ┌───────────────┼──────────────┐
       ↓               ↓              ↓
 Classical          Hybrid           PQ
       │               │              │
    ECDHE           X25519 +       ML-KEM
                    ML-KEM
       └───────────────┼──────────────┘
                       ↓
                 Benchmark
```

This is much stronger than merely saying:

> "Use PQC."

------------------------------------------------------------------------

# 23. 🧠 Upgrade #23 --- Migration Digital Twin

Now we reach the **big idea**.

Create a virtual model of the organization's cryptographic
infrastructure.

Call it:

# **Crypto Digital Twin**

For example:

``` text
                ENTERPRISE
                     │
        ┌────────────┼─────────────┐
        ↓            ↓             ↓
       APIs        Servers        Cloud
        │            │             │
       TLS          PKI           KMS
        │            │             │
       ECDH        ECDSA          RSA
        │            │             │
        └────────────┼─────────────┘
                     ↓
                  CBOM
```

Now simulate:

> "What happens if we replace ECDH with hybrid ML-KEM?"

The twin predicts:

``` text
Affected systems: 17
Affected certificates: 8
Affected services: 5
Bandwidth change: X
Latency change: Y
Dependencies: Z
Migration effort: ...
```

This is where the project stops being a scanner.

It becomes a **decision-support platform**.

------------------------------------------------------------------------

# 24. 🔮 Upgrade #24 --- "What if?" simulation

Give the administrator buttons:

### Scenario A

> "Remove RSA-2048."

System calculates impact.

### Scenario B

> "Deploy hybrid TLS."

System calculates impact.

### Scenario C

> "Disable SHA-1."

System finds:

``` text
dependencies
certificates
legacy clients
```

### Scenario D

> "Vendor doesn't support PQC until 2029."

System recalculates migration plan.

This is basically:

# **PQC What-If Engine**

------------------------------------------------------------------------

# 25. 📅 Upgrade #25 --- Automatic migration roadmap

Instead of:

``` text
HIGH RISK
HIGH RISK
HIGH RISK
```

generate:

``` text
2026
Discovery

2027
Crypto-agility preparation

2028
Critical systems

2029
Network infrastructure

2030
Legacy applications

2031
Hardware

2032+
Remaining legacy systems
```

But make the timeline **derived from actual dependencies and
organization inputs**, not arbitrary dates.

NCSC's current guidance itself structures migration around
discovery/planning, high-priority migration, and eventual completion,
with 2028/2031/2035 target milestones for UK organizations. [National
Cyber Security
Centre](https://www.ncsc.gov.uk/guidance/pqc-migration-timelines?utm_source=chatgpt.com)

------------------------------------------------------------------------

# 26. 💰 Upgrade #26 --- Migration cost estimator

The PS specifically mentions:

> latency, cost, etc.

So let's calculate:

``` text
Software changes
Hardware replacement
Certificate replacement
Testing
Infrastructure
Cloud costs
Bandwidth
Engineering effort
Downtime risk
Vendor dependencies
```

Then:

``` text
Migration estimate:

Applications affected: 42
Engineering effort: X person-days
Hardware replacements: 7
Certificate changes: 93
Expected bandwidth impact: X%
```

That gives executives something useful.

------------------------------------------------------------------------

# 27. 📈 Upgrade #27 --- Continuous monitoring

This is one of the biggest differences between a hackathon scanner and a
real enterprise product.

Don't:

``` text
SCAN
 ↓
REPORT
 ↓
DONE
```

Instead:

``` text
               ECDAT
                  ↓
          Continuous monitoring
                  ↓
       ┌──────────┼──────────┐
       ↓          ↓          ↓
    GitHub      Runtime     Network
       ↓          ↓          ↓
       └──────────┼──────────┘
                  ↓
             Change detected
                  ↓
             Risk recalculated
                  ↓
              Alert
```

Example:

> "New dependency added yesterday."

ECDAT:

> "This dependency introduces RSA-1024."

🔥 That's extremely useful.

------------------------------------------------------------------------

# 28. 🛡️ Upgrade #28 --- Crypto Policy-as-Code

Imagine the organization defines:

``` yaml
policies:
  forbidden:
    - MD5
    - DES
    - RSA-1024

  minimum:
    rsa: 3072
    aes: 256

  pqc_required:
    data_lifetime_years: 10
```

Then CI/CD checks every commit.

Developer writes:

``` python
DES.new(...)
```

Pipeline:

``` text
❌ BUILD BLOCKED

Policy violation:
DES is prohibited.

Suggested alternative:
AES-256-GCM
```

Now ECDAT becomes part of **DevSecOps**.

------------------------------------------------------------------------

# 29. 🔄 Upgrade #29 --- CI/CD crypto gate

Imagine GitHub/GitLab:

``` text
Developer
   ↓
git push
   ↓
CI/CD
   ↓
ECDAT
   ↓
Crypto scan
   ↓
CBOM update
   ↓
Risk check
```

If:

``` text
New quantum-vulnerable crypto
```

then:

``` text
⚠️ Pull Request warning
```

If:

``` text
Forbidden algorithm
```

then:

``` text
❌ Build failed
```

This creates **continuous crypto governance**.

------------------------------------------------------------------------

# 30. 🧪 Upgrade #30 --- Crypto regression testing

Suppose a developer migrates:

``` text
RSA → ML-DSA
```

ECDAT should test:

``` text
Does authentication still work?
Does the certificate chain work?
Does TLS work?
Are signatures valid?
Did latency explode?
Did any dependency break?
```

Then:

``` text
Migration validation:

✓ Functional
✓ Security
✓ Compatibility
✓ Performance
✓ CBOM updated
```

------------------------------------------------------------------------

# 31. 🤖 Upgrade #31 --- AI-assisted code migration

We can combine:

``` text
AST
+
crypto knowledge graph
+
CBOM
+
LLM
```

and produce:

``` text
Old code
   ↓
Understand crypto purpose
   ↓
Determine migration target
   ↓
Generate patch
   ↓
Compile
   ↓
Test
   ↓
Security scan
```

This is very close to the direction IBM Research describes for
cryptography discovery and remediation. [IBM
Research](https://research.ibm.com/projects/cryptography-code-discovery-and-remediation?utm_source=chatgpt.com)

------------------------------------------------------------------------

# 32. 🧠 Upgrade #32 --- Evidence-backed AI

This is crucial.

Every AI conclusion should have:

``` text
Claim
 ↓
Evidence
 ↓
Source
 ↓
Confidence
```

Example:

``` text
Finding:
RSA-2048 detected

Evidence:
auth.py:184
OpenSSL EVP_PKEY_RSA
key_size = 2048

Confidence:
HIGH

Risk reasoning:
...

Recommendation:
...
```

So the AI can't hallucinate.

------------------------------------------------------------------------

# 33. 🔬 Upgrade #33 --- Confidence-aware detection

This is something I'd absolutely put in your project.

Every finding:

``` text
HIGH confidence
MEDIUM confidence
LOW confidence
UNKNOWN
```

For example:

### HIGH

``` text
Explicit RSA API
```

### MEDIUM

``` text
Binary fingerprint
```

### LOW

``` text
Heuristic string match
```

### UNKNOWN

``` text
Encrypted/obfuscated binary
```

Then your report says:

> **"We detected 2,318 assets, of which 1,921 have high-confidence
> evidence."**

That's much more professional than claiming 100% detection.

------------------------------------------------------------------------

# 34. 🧠 Upgrade #34 --- Knowledge graph

Now connect everything.

``` text
Algorithm
    │
    ├── implemented by → Library
    │
    ├── used by → Application
    │
    ├── protects → Data
    │
    ├── contained in → Certificate
    │
    ├── negotiated by → Protocol
    │
    ├── deployed on → Hardware
    │
    └── replaced by → PQC candidate
```

Now your AI has a structured knowledge base.

You can ask:

> "Show me all systems indirectly dependent on ECDSA."

And the graph answers.

------------------------------------------------------------------------

# 35. 🔮 Upgrade #35 --- Quantum threat forecasting

This needs careful handling.

Don't say:

> "Quantum computer will arrive in 2034."

Nobody knows that.

Instead model **scenarios**.

``` text
Scenario A
CRQC early

Scenario B
CRQC medium

Scenario C
CRQC late
```

Then calculate:

``` text
Risk under A
Risk under B
Risk under C
```

So:

``` text
               Quantum timeline
                      ↓
        ┌─────────────┼─────────────┐
        ↓             ↓             ↓
      Early         Medium         Late
        ↓             ↓             ↓
      Risk          Risk           Risk
```

This is far better scientifically than pretending we know "Q-Day".

------------------------------------------------------------------------

# 36. 📊 Upgrade #36 --- Uncertainty-aware Mosca

Even Mosca analysis shouldn't be:

``` text
Q-day = 2035
```

Instead:

``` text
Expected quantum threat:
uncertain

Migration time:
4–7 years

Data lifetime:
15 years
```

Run multiple scenarios.

Then:

``` text
Probability-weighted / scenario risk
```

or simply show:

``` text
Best case
Base case
Adverse case
```

This is much more defensible.

------------------------------------------------------------------------

# 37. 🔗 Upgrade #37 --- Blockchain crypto inventory

Because your SIH theme is:

> **Blockchain & Cybersecurity**

we can add a specialized module.

Detect:

``` text
Wallet signatures
ECDSA
EdDSA
secp256k1
smart-contract cryptography
Merkle trees
hash functions
consensus signatures
blockchain certificates
```

Then:

``` text
Blockchain
     ↓
Cryptographic dependencies
     ↓
Quantum exposure
     ↓
Migration feasibility
```

This could make the project more aligned with the theme without forcing
blockchain into the entire system.

------------------------------------------------------------------------

# 38. 🔐 Upgrade #38 --- Digital-signature migration

This deserves its own engine.

Because encryption isn't the only problem.

You need to migrate:

``` text
Code signing
Firmware signing
Certificates
Document signing
Identity
Authentication
Blockchain signatures
```

Imagine:

``` text
Firmware
   ↓
ECDSA signature
   ↓
Quantum vulnerable
```

ECDAT says:

> "If this firmware-signing mechanism isn't migrated, a future quantum
> attacker could potentially forge signatures and distribute malicious
> firmware."

That is a much more serious scenario than simply saying:

> "ECDSA = vulnerable."

------------------------------------------------------------------------

# 39. 🥇 Upgrade #39 --- Secure-boot / firmware trust chain

For hardware:

``` text
Boot ROM
 ↓
Bootloader
 ↓
Firmware
 ↓
Application
```

Every stage may be cryptographically authenticated.

ECDAT could map:

``` text
Trust chain
     ↓
Signature algorithm
     ↓
Certificate
     ↓
Root key
     ↓
Hardware
```

Then determine:

> **"Can this device's root of trust be migrated?"**

This is advanced and extremely relevant to national-security
infrastructure.

------------------------------------------------------------------------

# 40. ⚡ Upgrade #40 --- Energy-aware PQC

This sounds unusual but is actually a real research direction.

Recent 2026 work benchmarks ML-KEM, ML-DSA and SLH-DSA not just for
speed but **energy consumption across constrained and general-purpose
architectures**.
[MDPI](https://www.mdpi.com/2410-387X/10/4/55?utm_source=chatgpt.com)

So for IoT:

``` text
PQC option A
CPU: low
RAM: medium
Energy: low

PQC option B
CPU: high
RAM: high
Energy: high
```

Then:

> "This algorithm is unsuitable for this battery-powered device."

That's genuinely intelligent recommendation.

------------------------------------------------------------------------

# 41. 🧪 Upgrade #41 --- Side-channel readiness

Another advanced layer.

Don't implement side-channel attacks in your hackathon product.

Instead assess whether implementations have:

``` text
constant-time properties
secure memory handling
side-channel-resistant implementation
hardware acceleration
validated crypto module
```

And classify:

``` text
Implementation assurance:
LOW / MEDIUM / HIGH
```

Because:

> An algorithm can be mathematically secure but badly implemented.

That's an important cryptographic-security principle.

------------------------------------------------------------------------

# 42. 🏭 Upgrade #42 --- Hardware compatibility matrix

For each migration:

``` text
                ML-KEM
                   │
        ┌──────────┼──────────┐
        ↓          ↓          ↓
      Server      HSM        IoT
        │          │          │
      YES          ?          NO
```

Then:

> **"Algorithm supported mathematically, but your HSM firmware doesn't
> support it."**

That's an actual migration blocker.

------------------------------------------------------------------------

# 43. 🧩 Upgrade #43 --- Vendor dependency intelligence

Suppose:

``` text
Application
 ↓
Vendor appliance
 ↓
Vendor doesn't support PQC
```

ECDAT identifies:

``` text
BLOCKER:
Vendor dependency

PQC support:
Unavailable

Expected vendor upgrade:
Unknown

Migration risk:
HIGH
```

NCSC specifically highlights supply-chain/vendor planning as part of PQC
migration. [National Cyber Security
Centre](https://www.ncsc.gov.uk/blog-post/post-quantum-cryptography-what-comes-next?utm_source=chatgpt.com)

------------------------------------------------------------------------

# 44. 📜 Upgrade #44 --- Compliance mapping

Map findings to:

``` text
NIST CSF
NIST 800-53
PQC guidance
CNSA
ISO controls
sector requirements
```

NIST's 2025 CSWP 48 explicitly maps PQC migration capabilities to NIST
CSF 2.0 and SP 800-53. [NIST Computer Security Resource
Center](https://csrc.nist.gov/pubs/cswp/48/mapping-migration-to-pqc-project-capabilities-to-r/ipd?utm_source=chatgpt.com)

So the dashboard could say:

``` text
Finding:
RSA-2048

Security impact:
...

PQC impact:
...

Control mapping:
NIST CSF
SP 800-53
```

------------------------------------------------------------------------

# 45. 📑 Upgrade #45 --- Executive mode vs engineer mode

Same data.

Different audiences.

### CISO:

``` text
Quantum readiness:
62%

Critical systems:
17

Migration blockers:
5

Estimated migration effort:
...

Top risks:
...
```

### Security engineer:

``` text
RSA-2048
EVP_PKEY_RSA
auth/service.cpp:481
OpenSSL 3.2
```

### Developer:

``` text
Replace:
RSA_generate_key_ex()

Suggested:
ML-DSA API

Migration guide:
...
```

### NTRO/technical auditor:

``` text
Evidence
Detection method
Confidence
Standards
Dependencies
Risk methodology
```

That's a proper product.

------------------------------------------------------------------------

# 46. 🔥 The BIGGEST upgrade: ECDAT becomes a closed loop

Basic:

``` text
DISCOVER
   ↓
REPORT
```

Advanced:

``` text
DISCOVER
   ↓
UNDERSTAND
   ↓
MODEL
   ↓
ASSESS
   ↓
SIMULATE
   ↓
PLAN
   ↓
REMEDIATE
   ↓
TEST
   ↓
VALIDATE
   ↓
MONITOR
   ↓
DISCOVER AGAIN
```

That's the system I'd want you to build.

------------------------------------------------------------------------

# 🧠 So I would divide the final system into 10 engines

## ENGINE 1 --- Discovery Engine

``` text
Source
Binary
Container
Network
Runtime
Cloud
Hardware
Firmware
Certificates
```

------------------------------------------------------------------------

## ENGINE 2 --- Crypto Intelligence Engine

Understands:

``` text
Algorithm
Purpose
Parameters
Mode
Implementation
Library
Protocol
```

------------------------------------------------------------------------

## ENGINE 3 --- CBOM Engine

Produces:

``` text
Standardized CBOM
Evidence
Dependencies
Relationships
Provenance
```

CycloneDX is the obvious standard to align with.
[CycloneDX](https://cyclonedx.org/guides/OWASP_CycloneDX-Authoritative-Guide-to-CBOM-en.pdf?utm_source=chatgpt.com)

------------------------------------------------------------------------

## ENGINE 4 --- Crypto Knowledge Graph

``` text
Application
 ↓
Library
 ↓
Algorithm
 ↓
Protocol
 ↓
Certificate
 ↓
Data
 ↓
Business service
```

------------------------------------------------------------------------

## ENGINE 5 --- Quantum Risk Engine

``` text
Quantum vulnerability
+
data lifetime
+
migration time
+
business criticality
+
exposure
+
dependency centrality
```

------------------------------------------------------------------------

## ENGINE 6 --- Migration Intelligence Engine

``` text
PQC candidate
Hybrid candidate
Latency
Cost
Compatibility
Hardware support
Vendor support
```

------------------------------------------------------------------------

## ENGINE 7 --- Migration Simulator

``` text
"What happens if I change this?"
```

------------------------------------------------------------------------

## ENGINE 8 --- Remediation Engine

``` text
Find
 ↓
Suggest patch
 ↓
Test
 ↓
Validate
```

------------------------------------------------------------------------

## ENGINE 9 --- Continuous Monitoring

``` text
Git
Network
Runtime
Cloud
Certificates
Dependencies
```

------------------------------------------------------------------------

## ENGINE 10 --- Command Center

``` text
CISO
Engineer
Developer
Auditor
```

different views.

------------------------------------------------------------------------

# 🏆 Now let's separate the 90% into tiers

This is important because **you shouldn't try to build all of this for
SIH**.

### 🟢 Tier 1 --- PS baseline

You absolutely need:

``` text
✓ Source scanning
✓ Binary scanning
✓ Container scanning
✓ Crypto detection
✓ CBOM
✓ Risk assessment
✓ Mosca
✓ PQC recommendation
✓ GUI
```

That's the basic requirement. [SIH 2026 Problem
Statements](https://sih2026.vuce.in/ps/SIH26164?utm_source=chatgpt.com)

------------------------------------------------------------------------

### 🔵 Tier 2 --- Strong SIH project

Add:

``` text
✓ AST semantic discovery
✓ Crypto dependency graph
✓ Certificate scanner
✓ Network TLS discovery
✓ Confidence scoring
✓ Evidence tracking
✓ SBOM + CBOM correlation
✓ Crypto-agility score
✓ Migration roadmap
```

This is where I would target your actual SIH implementation.

------------------------------------------------------------------------

### 🟣 Tier 3 --- "This team actually researched this"

Add:

``` text
✓ Runtime discovery
✓ Active network probing
✓ Passive discovery
✓ PQC benchmark lab
✓ Migration simulator
✓ What-if analysis
✓ Supply-chain analysis
✓ AI explanation
✓ AI-assisted remediation
✓ CI/CD integration
```

The active/passive discovery direction is particularly well aligned with
the 2026 IETF CADI work. [IETF
Datatracker](https://datatracker.ietf.org/doc/draft-liu-cadi/?utm_source=chatgpt.com)

------------------------------------------------------------------------

### 🔴 Tier 4 --- Research-grade

This becomes genuinely R&D:

``` text
✓ Crypto digital twin
✓ Graph-optimized migration
✓ Quantum scenario modelling
✓ Automated migration planning
✓ Firmware/root-of-trust analysis
✓ Energy-aware PQC selection
✓ Hardware compatibility modelling
✓ Crypto-agility maturity model
✓ Continuous enterprise cryptographic posture
```

Recent work on graph-based migration planning, PQC performance and
energy consumption supports these as credible research directions rather
than random feature ideas. [IEEE
Xplore](https://ieeexplore.ieee.org/abstract/document/11541993/authors?utm_source=chatgpt.com)

------------------------------------------------------------------------

# 🤯 And there is one REALLY interesting insight

I initially thought the most advanced version would be:

> **"A better crypto scanner."**

After looking at the current research landscape, I don't think that's
the ultimate product.

The more interesting product is:

# **ECDAT → Enterprise Cryptographic Digital Twin & PQC Migration Intelligence Platform**

It would know:

``` text
WHAT crypto exists
        ↓
WHERE it exists
        ↓
WHY it exists
        ↓
WHAT data it protects
        ↓
WHAT depends on it
        ↓
HOW quantum-vulnerable it is
        ↓
HOW important it is
        ↓
HOW difficult it is to replace
        ↓
WHAT replacement works
        ↓
WHAT that replacement will cost
        ↓
WHAT breaks if we migrate
        ↓
HOW to migrate safely
        ↓
WHETHER the migration actually worked
```

That's **far beyond the basic PS**.

------------------------------------------------------------------------

# 🔥 And the research landscape actually supports this direction

This isn't me making up futuristic features.

There is a very clear convergence happening:

**NIST** → cryptographic discovery + migration + crypto agility.
[NCCoE](https://www.nccoe.nist.gov/applied-cryptography/migration-to-pqc?utm_source=chatgpt.com)

**IETF** → cryptographic asset discovery/inventory + active/passive
discovery. [IETF
Datatracker](https://datatracker.ietf.org/doc/draft-liu-cadi/?utm_source=chatgpt.com)

**OWASP/CycloneDX** → standardized CBOM and broader BOM ecosystem.
[OWASP
Foundation](https://owasp.org/projects/cyclonedx?utm_source=chatgpt.com)

**IBM Research** → code-level crypto discovery + AI-assisted
remediation + crypto agility. [IBM
Research](https://research.ibm.com/projects/cryptography-code-discovery-and-remediation?utm_source=chatgpt.com)

**IETF** → standardized PQ/T hybrid TLS mechanisms are now progressing
into published standards. [IETF
Datatracker](https://datatracker.ietf.org/doc/html/rfc10024?utm_source=chatgpt.com)

**Recent academic research** → performance benchmarking, AI-assisted
crypto misuse detection, graph-based migration planning and energy-aware
PQC evaluation.
[ScienceDirect](https://www.sciencedirect.com/science/article/pii/S0167739X25003577?utm_source=chatgpt.com)

**NCSC/NSA** → real-world migration timelines, hardware, supply chain,
critical infrastructure and long-term migration planning. [National
Cyber Security
Centre](https://www.ncsc.gov.uk/guidance/pqc-migration-timelines?utm_source=chatgpt.com)

So the field is clearly moving from:

> **"Find vulnerable cryptography."**

toward:

> **"Understand the entire cryptographic ecosystem and safely transition
> it."**

------------------------------------------------------------------------

# 🧠 If this were OUR project, this would be the final vision

``` text
╔══════════════════════════════════════════════╗
║                  ECDAT-X                     ║
║ Enterprise Cryptographic Intelligence        ║
╠══════════════════════════════════════════════╣
║                                              ║
║  DISCOVERY                                   ║
║  ├─ Source                                   ║
║  ├─ Binary                                   ║
║  ├─ Container                                ║
║  ├─ Network                                  ║
║  ├─ Runtime                                  ║
║  ├─ Cloud                                    ║
║  ├─ Hardware                                 ║
║  └─ Firmware                                 ║
║                                              ║
║  INTELLIGENCE                                ║
║  ├─ Crypto semantics                         ║
║  ├─ CBOM                                     ║
║  ├─ Dependency graph                         ║
║  ├─ Data lineage                             ║
║  └─ Evidence / confidence                    ║
║                                              ║
║  QUANTUM RISK                                ║
║  ├─ Mosca                                    ║
║  ├─ HNDL                                     ║
║  ├─ Scenario modelling                       ║
║  ├─ Business criticality                     ║
║  └─ Attack graph                             ║
║                                              ║
║  MIGRATION                                   ║
║  ├─ PQC                                      ║
║  ├─ Hybrid                                   ║
║  ├─ Benchmark                                ║
║  ├─ Cost                                     ║
║  ├─ Compatibility                            ║
║  └─ Migration simulation                     ║
║                                              ║
║  REMEDIATION                                 ║
║  ├─ AI explanation                           ║
║  ├─ Code patches                             ║
║  ├─ CI/CD                                    ║
║  └─ Validation                               ║
║                                              ║
║  CONTINUOUS SECURITY                         ║
║  ├─ Runtime monitoring                       ║
║  ├─ Dependency monitoring                    ║
║  ├─ Certificate monitoring                   ║
║  └─ Crypto-agility monitoring                ║
║                                              ║
╚══════════════════════════════════════════════╝
```

### And the killer screen:

> **"If we migrate this cryptographic asset tomorrow, what breaks?"**

That question is where your project can become **genuinely
differentiated**.

Because then ECDAT isn't merely saying:

**"RSA is vulnerable."**

It's saying:

> **"This RSA implementation protects these 6 services, these 3
> certificates, these 2 business systems and this dataset. Replacing it
> affects these dependencies. Here are 3 technically compatible
> migration paths, their measured performance impact, the required
> hardware changes, and the safest migration sequence."**

**That is the 90%.**

And importantly, the current research/standards landscape gives us
enough material to build this systematically rather than inventing
features randomly.
[NCCoE](https://www.nccoe.nist.gov/applied-cryptography/migration-to-pqc?utm_source=chatgpt.com)

## Uploaded Research Note 2

Yes. **You're right --- we're still nowhere near the ceiling.** I was
thinking mostly in terms of "more features." But after digging further
into the 2026 CADI work, NIST, IETF, CISA material, recent research, and
the software-engineering side of PQC, I see a much larger opportunity.

The important discovery is this:

> **ECDAT should not be designed as a cryptographic scanner. It should
> become an enterprise cryptographic observability + reasoning +
> migration system.**

The 2026 IETF CADI draft itself exposes several discovery modes that go
beyond normal CBOM: static code, binary/image scanning, CI/CD, simulated
handshakes, traffic-pattern analysis, process identification/eBPF,
memory indicators, and configuration extraction. It also explicitly
identifies legacy black-box systems as a major blind spot. [IETF
Datatracker](https://datatracker.ietf.org/doc/html/draft-liu-cadi-00)

So let's push this much further.

# ECDAT-X: the full vision

Think of the system as having **12 layers**, not 5--6.

``` text
                    ┌─────────────────────────────┐
                    │       ECDAT COMMAND        │
                    │         CENTER             │
                    └──────────────┬──────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │  CRYPTOGRAPHIC KNOWLEDGE   │
                    │          GRAPH              │
                    └──────────────┬──────────────┘
                                   │
          ┌────────────────────────┼────────────────────────┐
          │                        │                        │
   DISCOVERY ENGINE          RISK ENGINE            MIGRATION ENGINE
          │                        │                        │
          ▼                        ▼                        ▼
   source / binary          quantum risk          PQC selection
   runtime / network        HNDL risk              migration order
   cloud / hardware        business risk           simulation
   firmware / config       dependency risk         cost
          │                        │                        │
          └────────────────────────┼────────────────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │   REMEDIATION / VALIDATION  │
                    └──────────────┬──────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │     CONTINUOUS MONITORING    │
                    └─────────────────────────────┘
```

And now the **new layers** I would add.

------------------------------------------------------------------------

# 1. Cryptographic Discovery should become MULTI-MODAL

The PS says:

> scan source repositories, binaries, libraries, container images.

That's only the beginning.

The latest CADI work explicitly describes **active and passive
identification** and includes static scanning, binary/image scanning,
CI/CD, simulated handshakes, traffic analysis, process identification
and configuration extraction. [IETF
Datatracker](https://datatracker.ietf.org/doc/html/draft-liu-cadi-00)

So ECDAT can have:

### A. Source scanner

Detect:

``` text
AES
RSA
ECDSA
ECDH
DH
DSA
SHA-1
SHA-256
SHA-3
HMAC
PBKDF
Argon2
bcrypt
TLS
SSH
IPsec
JWT
JWS
JWE
PKCS
X.509
```

But don't stop at finding strings.

------------------------------------------------------------------------

# 2. Semantic Cryptography Discovery

This is much more interesting.

Instead of:

``` text
grep("RSA")
```

do:

``` text
AST
 ↓
Call graph
 ↓
Data flow
 ↓
Crypto API
 ↓
Algorithm
 ↓
Key
 ↓
Protected data
 ↓
System
```

For example:

``` python
private_key = load_key(...)
signature = RSA.sign(private_key, document)
```

ECDAT should understand:

``` text
Document
    ↓
RSA signing
    ↓
RSA-2048
    ↓
Private key
    ↓
Authentication service
    ↓
Payment API
```

Now you've discovered **context**, not merely a keyword.

The CADI draft specifically discusses SAST using AST/data-flow and
tracking call chains into crypto libraries. [IETF
Datatracker](https://datatracker.ietf.org/doc/html/draft-liu-cadi-00)

------------------------------------------------------------------------

# 3. Binary Reverse-Cryptography Engine

This is a huge opportunity.

Imagine the company gives you:

``` text
app.exe
libcrypto.so
firmware.bin
docker image
APK
DLL
ELF
```

ECDAT attempts to recover:

``` text
algorithm signatures
crypto constants
library references
certificate stores
cipher identifiers
TLS implementations
key sizes
protocol strings
crypto symbols
embedded certificates
```

Then:

``` text
Binary
 ↓
Crypto fingerprint
 ↓
Likely algorithm
 ↓
Confidence
 ↓
CBOM
```

And importantly:

### Don't say:

> "This binary uses RSA."

Say:

> RSA-2048 detected\
> Evidence: OpenSSL symbol + ASN.1 OID + RSA key-size constant\
> Confidence: 96%

That's far more defensible.

------------------------------------------------------------------------

# 4. Runtime Cryptography Discovery

This is another level.

Suppose source code says:

``` text
AES
RSA
ECDSA
```

But production actually uses:

``` text
AES-256-GCM
ECDSA P-256
```

ECDAT should be able to observe runtime behavior.

Potential mechanisms include:

-   eBPF
-   system-call tracing
-   library loading
-   process inspection
-   dynamic instrumentation
-   runtime configuration
-   network observation

The CADI draft specifically discusses kernel-level auditing,
shared-library/binary hooking and even memory indicators as possible
passive discovery mechanisms. [IETF
Datatracker](https://datatracker.ietf.org/doc/html/draft-liu-cadi-00)

So your system could produce:

``` text
STATIC VIEW
RSA
ECDSA
AES

        ↓ compare ↓

RUNTIME VIEW
ECDSA P-256
AES-256-GCM

        ↓

DRIFT DETECTED
```

🔥 That's a serious enterprise feature.

------------------------------------------------------------------------

# 5. Crypto Reality vs Crypto Documentation

Create a **Crypto Truth Engine**.

For every asset:

``` text
Declared
Detected
Observed
Inferred
Unknown
```

Example:

  Evidence                          Result
  --------------------------------- ----------
  SBOM says OpenSSL                 Declared
  Binary contains OpenSSL           Detected
  Runtime loads libcrypto           Observed
  TLS uses ECDSA P-256              Observed
  Source has RSA code               Detected
  Actual production usage unknown   Unknown

Then calculate:

### Evidence confidence

``` text
HIGH
MEDIUM
LOW
CONFLICTING
UNKNOWN
```

This is extremely valuable because enterprise inventories are inherently
incomplete.

------------------------------------------------------------------------

# 6. Cryptographic Shadow Discovery

Here's another idea.

Most companies won't know every cryptographic asset.

ECDAT should explicitly hunt for:

> **Crypto that nobody knows exists.**

Call it:

## Shadow Crypto Detection

Look for cryptography hidden in:

-   forgotten repositories
-   abandoned services
-   old Docker images
-   CI artifacts
-   backup servers
-   scripts
-   binaries
-   firmware
-   vendor appliances
-   old certificates
-   old VPNs
-   databases
-   mobile apps
-   JavaScript bundles
-   third-party SDKs
-   infrastructure-as-code
-   Kubernetes secrets/configuration
-   cloud functions
-   Lambda layers
-   machine images

This directly attacks one of the hardest enterprise problems: legacy and
undocumented cryptography. CADI explicitly notes that legacy systems can
behave as black boxes and that CBOM alone cannot discover them. [IETF
Datatracker](https://datatracker.ietf.org/doc/html/draft-liu-cadi-00)

------------------------------------------------------------------------

# 7. Network Cryptography Radar

Now build an actual network intelligence layer.

ECDAT probes:

``` text
TLS
SSH
IPsec
VPN
mTLS
LDAP/LDAPS
SMTP
IMAP
SFTP
database TLS
service mesh
```

For TLS:

``` text
TLS version
cipher suite
key exchange
certificate
signature algorithm
curve
PQC support
hybrid support
server preference
certificate chain
```

And now something important:

### Compare internal vs external posture.

``` text
Internet
   ↓
Load Balancer
   ↓
API Gateway
   ↓
Service Mesh
   ↓
Microservice
   ↓
Database
```

You may discover:

``` text
Internet edge: PQ hybrid
Internal API: ECDSA
Database: RSA
Legacy service: TLS 1.2
```

That becomes an actual **crypto attack surface map**.

------------------------------------------------------------------------

# 8. Passive Traffic Cryptography Intelligence

Don't always probe.

Listen.

The current CADI draft describes traffic-pattern analysis using
handshake metadata, fingerprints, packet behavior and other observable
characteristics, while acknowledging limitations such as encrypted
negotiation metadata and routing differences. [IETF
Datatracker](https://datatracker.ietf.org/doc/html/draft-liu-cadi-00)

ECDAT could therefore have:

``` text
PCAP
 ↓
Protocol classifier
 ↓
Handshake fingerprint
 ↓
Crypto inference
 ↓
Asset correlation
```

This means:

> **You can discover crypto without installing an agent on every
> machine.**

Huge for legacy infrastructure.

------------------------------------------------------------------------

# 9. "Crypto DNA" of Every System

Give every application a cryptographic profile.

Example:

``` text
PAYMENT-SERVICE-07

Crypto DNA
──────────────────────

Encryption
 AES-256-GCM

Key exchange
 ECDH P-256

Authentication
 ECDSA P-256

Hash
 SHA-256

Transport
 TLS 1.3

Certificates
 4

HSM
 YES

PQC
 NO

Crypto agility
 42/100

Quantum exposure
 HIGH

Migration complexity
 HIGH
```

Now you can compare:

``` text
Application A
Application B
Application C
```

instantly.

------------------------------------------------------------------------

# 10. Crypto Dependency Graph

We already discussed this, but I found stronger recent research
supporting it.

A 2026 Information and Software Technology paper proposes graph-based
cryptographic risk modelling where algorithms, protocols, dependencies
and usage contexts become graph nodes/edges, allowing systemic risk and
dependency propagation to be analysed.
[ScienceDirect](https://www.sciencedirect.com/science/article/pii/S0950584926000881?utm_source=chatgpt.com)

So make this central.

Example:

``` text
Payment API
     │
     ├── TLS
     │    └── ECDHE
     │          └── P-256
     │
     ├── Certificate
     │    └── ECDSA
     │          └── P-256
     │
     └── HSM
          └── firmware 4.2
```

Then:

> What happens if P-256 must be removed?

ECDAT traverses the graph.

------------------------------------------------------------------------

# 11. Single Point of Cryptographic Failure

This is something I would definitely add.

Suppose:

``` text
500 applications
       ↓
ECDSA P-256
```

That's not 500 independent problems.

That's potentially:

> **one cryptographic dependency affecting 500 systems.**

ECDAT calculates:

``` text
Dependency Centrality
```

and identifies:

### Cryptographic Single Points of Failure

Example:

``` text
RSA-2048
 ↓
43 applications
 ↓
7 APIs
 ↓
3 critical business systems
```

That asset becomes extremely important to migrate.

------------------------------------------------------------------------

# 12. Quantum Attack Propagation Graph

Go beyond:

> "RSA is quantum vulnerable."

Instead:

``` text
Quantum-vulnerable primitive
          ↓
Certificate
          ↓
Service
          ↓
Application
          ↓
Sensitive data
          ↓
Business process
```

Then show:

> **If this primitive becomes breakable, what gets exposed?**

That's a completely different level of risk modelling.

------------------------------------------------------------------------

# 13. Data-Centric Quantum Risk

This is VERY important.

Don't score only the cryptography.

Score:

``` text
Crypto
+
Data sensitivity
+
Data lifetime
+
Exposure
+
Migration time
+
Business criticality
```

Example:

### System A

``` text
RSA-2048
Data lifetime: 3 months
Migration: 2 weeks
```

### System B

``` text
RSA-2048
Data lifetime: 25 years
Migration: 4 years
```

Same algorithm.

**Completely different strategic risk.**

NIST explicitly includes sensitive/long-lived data in its description of
cryptographic inventory because of harvest-now-decrypt-later concerns.
[NIST
Pages](https://pages.nist.gov/nccoe-migration-post-quantum-cryptography/?utm_source=chatgpt.com)

------------------------------------------------------------------------

# 14. HNDL / SNDL Intelligence

Create a dedicated:

## Harvest-Now-Decrypt-Later Engine

ECDAT asks:

``` text
Is this data encrypted today?
          ↓
Will it still be sensitive when quantum
capability arrives?
          ↓
Is the encryption quantum-vulnerable?
          ↓
How long would migration take?
```

Output:

``` text
HNDL EXPOSURE

Critical
High
Medium
Low
```

------------------------------------------------------------------------

# 15. Quantum Scenario Engine

Don't pretend we know exactly when a CRQC arrives.

Instead:

``` text
Scenario A
CRQC = earlier

Scenario B
CRQC = middle

Scenario C
CRQC = later
```

Calculate:

``` text
Data exposure
Migration deadline
Assets at risk
Systems requiring emergency migration
```

This is much more scientifically honest than:

> "Quantum computer arrives in 2037."

------------------------------------------------------------------------

# 16. Mosca++ Instead of Simple Mosca

The PS explicitly mentions Mosca's inequality.

Don't just implement:

``` text
X + Y > Z
```

Build:

``` text
Data lifetime
+
Migration time
+
Vendor dependency
+
Hardware replacement time
+
Certificate replacement time
+
Testing time
+
Regulatory approval time
+
Interoperability time
```

Then:

### Migration Urgency Index

``` text
LOW
MEDIUM
HIGH
CRITICAL
```

Not merely algorithm vulnerability.

------------------------------------------------------------------------

# 17. Crypto Agility Reverse Engineering

This one can become a research feature.

Ask:

> **How difficult would it be to replace this algorithm?**

Inspect:

``` text
Hardcoded algorithm?
Configurable?
Central crypto provider?
Dependency injection?
Plugin architecture?
Versioned API?
Certificate automation?
HSM support?
Protocol negotiation?
```

Then:

``` text
Crypto Agility Score
```

Example:

``` text
Algorithm replacement
        ↓
config.yaml
        ↓
one-line change
        ↓
HIGH AGILITY
```

versus:

``` text
RSA hardcoded
 ↓
business logic
 ↓
database schema
 ↓
certificate assumptions
 ↓
vendor appliance
 ↓
LOW AGILITY
```

NIST's crypto-agility work explicitly focuses on the ability to
replace/adapt cryptography across applications, protocols, software,
hardware, firmware and infrastructure while maintaining operations.
[NCCoE](https://www.nccoe.nist.gov/applied-cryptography/migration-to-pqc?utm_source=chatgpt.com)

------------------------------------------------------------------------

# 18. Migration Difficulty Prediction

Don't only say:

> "Replace RSA with ML-DSA."

Instead estimate:

``` text
Migration effort

Code changes          ███████
Infrastructure        ███
Certificates          ██████
Hardware              █████████
Testing               ███████
Vendor dependency     ██████████

Estimated complexity: HIGH
```

And explain **why**.

------------------------------------------------------------------------

# 19. PQC Compatibility Matrix

Build a massive compatibility matrix:

``` text
System
   ×
Algorithm
   ×
PQC replacement
   ×
Library
   ×
OS
   ×
CPU
   ×
HSM
   ×
Protocol
   ×
Certificate
```

Example:

``` text
OpenSSL
 ├── ML-KEM
 ├── ML-DSA
 └── SLH-DSA

HSM
 ├── ML-KEM → supported
 ├── ML-DSA → firmware required
 └── SLH-DSA → unsupported
```

This becomes incredibly practical.

------------------------------------------------------------------------

# 20. Real PQC Benchmark Laboratory

Don't trust theoretical performance.

Actually test:

``` text
RSA
ECDSA
ECDH

vs

ML-KEM
ML-DSA
SLH-DSA
Hybrid
```

Measure:

``` text
CPU
RAM
latency
throughput
key size
ciphertext size
signature size
handshake size
energy
network bandwidth
```

NIST's migration project itself has a dedicated interoperability and
benchmarking workstream, so this fits directly into the real migration
problem. [NIST
Pages](https://pages.nist.gov/nccoe-migration-post-quantum-cryptography/?utm_source=chatgpt.com)

------------------------------------------------------------------------

# 21. Protocol Migration Simulator

Now we're getting serious.

Take:

``` text
TLS 1.3
```

and simulate:

``` text
ECDHE
       ↓
X25519MLKEM768
```

Current IETF RFC 10024 defines three PQ/T hybrid TLS 1.3 key-agreement
mechanisms: X25519MLKEM768, SecP256r1MLKEM768 and SecP384r1MLKEM1024.
[IETF
Datatracker](https://datatracker.ietf.org/doc/html/rfc10024?utm_source=chatgpt.com)

ECDAT can therefore show:

``` text
CURRENT

TLS
↓
X25519
↓
Handshake = 4.2 KB


PROPOSED

TLS
↓
X25519 + ML-KEM
↓
Handshake = X KB

Latency = +Y ms
Bandwidth = +Z%
```

Now the recommendation is based on **measurement**.

------------------------------------------------------------------------

# 22. Migration Digital Twin

Create a virtual copy of the organization's crypto infrastructure.

``` text
REAL ENTERPRISE
       ↓
ECDAT MODEL
       ↓
DIGITAL TWIN
```

Then simulate:

> "What if we migrate these 50 assets?"

The system predicts:

``` text
affected applications
affected certificates
affected protocols
performance impact
dependencies
failures
cost
migration duration
```

This could be one of your strongest research contributions.

------------------------------------------------------------------------

# 23. What-If Engine

User clicks:

> **Replace RSA with ML-DSA**

ECDAT calculates:

``` text
+ 23 MB certificate storage
+ 8% bandwidth
+ 4 incompatible systems
+ 2 HSM upgrades
+ 11 certificate replacements

Estimated migration complexity: ...
```

Then:

> **Try hybrid**

And compare the scenario.

This is far beyond a scanner.

------------------------------------------------------------------------

# 24. Migration Ordering Optimizer

This is supported by very recent research.

A 2026 IEEE paper proposes dependency-aware PQC migration planning using
a cryptographic dependency graph, risk weighting and migration ordering
to reduce interoperability failures in simulated enterprise
environments. [IEEE
Xplore](https://ieeexplore.ieee.org/abstract/document/11541993/authors?utm_source=chatgpt.com)

So ECDAT could generate:

``` text
Migration Wave 1
 ├── 12 low-dependency services

Migration Wave 2
 ├── 8 certificate authorities
 ├── 17 APIs

Migration Wave 3
 ├── HSM infrastructure

Migration Wave 4
 └── legacy systems
```

rather than:

> "Migrate everything."

------------------------------------------------------------------------

# 25. Migration Blast Radius

This is another excellent feature.

Before changing crypto:

``` text
SELECT ASSET
       ↓
BLAST RADIUS
```

Show:

``` text
37 applications
12 certificates
8 APIs
4 databases
2 vendors
1 HSM
```

affected.

Then:

> **Don't migrate until blast radius is understood.**

------------------------------------------------------------------------

# 26. Certificate Intelligence Platform

Not merely certificate scanning.

Track:

``` text
certificate
 ↓
issuer
 ↓
algorithm
 ↓
key size
 ↓
chain
 ↓
application
 ↓
server
 ↓
business service
```

Then detect:

-   expired certificates
-   weak algorithms
-   weak keys
-   inappropriate lifetimes
-   orphan certificates
-   duplicate certificates
-   shadow certificates
-   certificate chain problems
-   PQC readiness
-   certificate migration dependencies

CycloneDX CBOM explicitly models certificates and their relationships to
cryptographic assets.
[CycloneDX](https://cyclonedx.org/capabilities/cbom/?utm_source=chatgpt.com)

------------------------------------------------------------------------

# 27. PKI Dependency Graph

Go even deeper:

``` text
Root CA
 ↓
Intermediate CA
 ↓
Certificate
 ↓
Service
 ↓
Client
```

Then simulate:

> "What happens if this CA algorithm needs replacement?"

That's a **PKI migration graph**.

------------------------------------------------------------------------

# 28. HSM/KMS Intelligence

Inventory:

``` text
HSM
KMS
TPM
Secure Enclave
Smart Card
Crypto Accelerator
```

For each:

``` text
vendor
model
firmware
supported algorithms
key types
PQC capability
upgrade path
replacement path
certification
```

This is critical because PQC migration isn't purely software.

------------------------------------------------------------------------

# 29. Firmware Cryptography Scanner

This is huge for:

``` text
IoT
routers
switches
industrial devices
cars
medical equipment
satellites
embedded devices
```

Scan:

``` text
firmware.bin
 ↓
strings
 ↓
symbols
 ↓
constants
 ↓
crypto implementations
 ↓
protocols
```

Then:

``` text
Firmware
RSA-2048
ECDSA-P256
TLS
Hardcoded certificate
```

------------------------------------------------------------------------

# 30. Hardware Root-of-Trust Mapper

Map:

``` text
Secure Boot
 ↓
Bootloader
 ↓
Firmware signing
 ↓
TPM
 ↓
Device identity
```

Then determine:

> Which cryptographic primitive protects the device's root of trust?

That's much deeper than application scanning.

------------------------------------------------------------------------

# 31. OT / ICS Crypto Migration

A 2026 research paper specifically highlights the distinction between IT
and OT environments and the difficulty of PQC migration in long-lived
operational technology.
[ScienceDirect](https://www.sciencedirect.com/science/article/pii/S3050475926011796?utm_source=chatgpt.com)

So create:

``` text
IT
OT
IoT
ICS
```

separate migration profiles.

Because:

``` text
Cloud server
```

can be upgraded tomorrow.

But:

``` text
20-year industrial controller
```

might not.

------------------------------------------------------------------------

# 32. Blockchain Cryptographic Inventory

Since SIH itself places this under:

> **Blockchain & Cybersecurity**

we can exploit that.

Detect:

``` text
secp256k1
ECDSA
EdDSA
BLS
Merkle trees
hash functions
wallet signatures
multisig
smart contract cryptography
consensus signatures
ZK systems
```

Then produce:

``` text
Blockchain PQ Risk
```

Recent ACM work specifically proposes a cryptographic dependency
inventory for decentralized systems including wallet signing,
node-to-node secure channels and state commitments.
[DOI](https://doi.org/10.1145/3774905.3794696?utm_source=chatgpt.com)

So this isn't just theoretical.

------------------------------------------------------------------------

# 33. Smart Contract Crypto Scanner

Scan Solidity:

``` solidity
ecrecover(...)
keccak256(...)
ECDSA(...)
```

Detect:

``` text
signature dependence
hash dependence
key-management problems
quantum-vulnerable primitives
hardcoded cryptographic material
```

OWASP's current smart-contract security material explicitly covers
improper cryptographic key management and hardcoded keys. [OWASP Smart
Contract
Security](https://scs.owasp.org/SCWE/SCSVS-CRYPTO/SCWE-025/?utm_source=chatgpt.com)

------------------------------------------------------------------------

# 34. ZKP / Modern Cryptography Detection

Go beyond classical cryptography.

Detect:

``` text
SNARK
STARK
KZG
pairings
BLS12-381
commitments
Merkle proofs
```

Then classify:

``` text
Quantum vulnerability
Quantum assumptions
Migration considerations
```

This could become an optional advanced research module.

------------------------------------------------------------------------

# 35. Cryptographic Misuse Detection

Not every crypto usage is insecure because of the algorithm.

Detect:

``` text
AES-ECB
weak IV
reused nonce
hardcoded key
predictable RNG
weak password derivation
improper certificate validation
disabled verification
SHA-1
MD5
small RSA keys
wrong padding
bad randomness
```

This turns ECDAT into:

> **Cryptographic Security Analyzer**

rather than merely:

> PQC scanner.

------------------------------------------------------------------------

# 36. Key Lifecycle Intelligence

Track:

``` text
Generate
 ↓
Activate
 ↓
Use
 ↓
Rotate
 ↓
Archive
 ↓
Revoke
 ↓
Destroy
```

Detect:

``` text
never rotated
expired
orphaned
unused
overused
shared
hardcoded
unknown owner
unknown purpose
```

OWASP's current key-management guidance explicitly treats generation,
distribution, destruction, compromise recovery, zeroization and storage
as lifecycle concerns. [OWASP Cheat Sheet
Series](https://cheatsheetseries.owasp.org/cheatsheets/Key_Management_Cheat_Sheet?utm_source=chatgpt.com)

------------------------------------------------------------------------

# 37. Secret-to-Crypto Correlation

Connect:

``` text
Secret
 ↓
Key
 ↓
Algorithm
 ↓
Application
 ↓
Data
```

Example:

``` text
AWS secret
 ↓
AES key
 ↓
database
 ↓
customer records
```

Then:

> "This secret indirectly protects 14 TB of sensitive data."

That's much more useful than a generic secret scanner.

------------------------------------------------------------------------

# 38. Cryptographic Data Lineage

This could be a flagship visualization.

``` text
CUSTOMER DATA
     ↓
DATABASE
     ↓
AES-256
     ↓
KMS KEY
     ↓
BACKUP
     ↓
ARCHIVE
```

And:

``` text
PERSONAL DATA
     ↓
TLS
     ↓
ECDH
     ↓
NETWORK
```

Now ECDAT understands **what cryptography protects what**.

------------------------------------------------------------------------

# 39. Backup & Archive Quantum Risk

This is easily forgotten.

Scan:

``` text
backups
archives
cold storage
tapes
data lakes
object storage
snapshots
logs
```

Ask:

> Are old ciphertexts still sensitive?

This feeds directly into HNDL risk.

------------------------------------------------------------------------

# 40. Cloud Cryptographic Inventory

Support:

``` text
AWS
Azure
GCP
Kubernetes
Cloudflare
```

Discover:

``` text
KMS
Certificates
Secrets
TLS endpoints
Load balancers
API gateways
service mesh
database encryption
storage encryption
IAM signing
```

Then:

``` text
Cloud Crypto Map
```

------------------------------------------------------------------------

# 41. Infrastructure-as-Code Crypto Scanner

Scan:

``` text
Terraform
CloudFormation
Kubernetes YAML
Helm
Ansible
Dockerfiles
GitHub Actions
GitLab CI
```

Find:

``` text
TLS configuration
certificate configuration
KMS references
crypto libraries
security settings
```

Now crypto inventory starts **before deployment**.

------------------------------------------------------------------------

# 42. CI/CD Quantum Security Gate

Every pull request:

``` text
CODE
 ↓
ECDAT
 ↓
Crypto analysis
 ↓
CBOM update
 ↓
Policy check
```

Example:

``` text
❌ RSA-1024 introduced
❌ SHA-1 introduced
⚠ RSA dependency added
⚠ non-agile crypto API
```

Block merge.

------------------------------------------------------------------------

# 43. Crypto Regression Detection

This is brilliant for continuous monitoring.

Today:

``` text
AES-256-GCM
TLS 1.3
```

Tomorrow developer changes it:

``` text
AES-CBC
TLS 1.2
```

ECDAT says:

> **Cryptographic regression detected.**

------------------------------------------------------------------------

# 44. Crypto Drift Detection

Compare:

``` text
Expected crypto
vs
Actual crypto
```

Example:

``` text
Policy:
TLS 1.3 + PQ hybrid

Observed:
TLS 1.2 + ECDHE
```

Then:

``` text
CRYPTO DRIFT
```

------------------------------------------------------------------------

# 45. Crypto Policy-as-Code

Allow:

``` yaml
policy:
  minimum_tls: "1.3"
  forbid:
    - MD5
    - SHA1
    - RSA1024
  pqc:
    required_for:
      - long_lived_sensitive_data
```

Then ECDAT evaluates the whole organization automatically.

------------------------------------------------------------------------

# 46. Supply-Chain Cryptographic Risk

This is a monster area.

Imagine:

``` text
Your application
 ↓
Library
 ↓
Vendor SDK
 ↓
OpenSSL
 ↓
Hardware accelerator
```

One upstream dependency changes crypto.

ECDAT detects:

``` text
Crypto dependency changed
```

Then asks:

> Which downstream systems are affected?

------------------------------------------------------------------------

# 47. Cryptographic SBOM + CBOM + HBOM + OBOM

Instead of isolated inventories:

``` text
SBOM
CBOM
HBOM
OBOM
```

connect them.

``` text
Software
   ↓
Crypto
   ↓
Hardware
   ↓
Runtime
   ↓
Operations
```

This gives a **complete cryptographic supply-chain graph**.

------------------------------------------------------------------------

# 48. Vendor Cryptographic Dependency

Suppose:

``` text
Vendor X
 ↓
Firmware
 ↓
RSA
```

Vendor doesn't support PQC.

ECDAT should say:

``` text
MIGRATION BLOCKER

Reason:
Vendor dependency

Alternative:
Firmware upgrade
Replacement model
Compensating control
```

This is extremely practical.

------------------------------------------------------------------------

# 49. Migration Cost Engine

Estimate:

``` text
Developer cost
Infrastructure cost
HSM upgrade
certificate replacement
hardware replacement
testing
downtime
vendor cost
bandwidth impact
```

Then:

``` text
Estimated migration effort
```

Not a fake exact number --- a transparent estimate with assumptions.

------------------------------------------------------------------------

# 50. Migration Deadline Engine

Combine:

``` text
Risk
+
Data lifetime
+
Migration time
+
Vendor lead time
+
Hardware lifetime
+
Compliance deadline
```

Output:

``` text
Recommended migration window
```

Again, explain the assumptions.

------------------------------------------------------------------------

# 51. Crypto Technical Debt

This is another excellent metric.

Every system gets:

``` text
Crypto Technical Debt
```

based on:

``` text
legacy algorithms
hardcoded crypto
vendor lock-in
poor agility
old libraries
expired certificates
manual processes
migration blockers
```

Then management gets:

> "Where is our cryptographic technical debt?"

------------------------------------------------------------------------

# 52. Crypto Agility Maturity Model

Something like:

``` text
Level 0
Unknown

Level 1
Inventory

Level 2
Discoverable

Level 3
Configurable

Level 4
Automated migration

Level 5
Continuously crypto-agile
```

But make the scoring transparent and evidence-based rather than
arbitrary.

------------------------------------------------------------------------

# 53. AI Crypto Analyst

Now AI becomes useful.

Not:

> "ChatGPT, tell me what to do."

Instead:

``` text
ECDAT database
      ↓
structured evidence
      ↓
AI reasoning
      ↓
explanation
```

AI answers:

> Why is this asset high risk?

And cites:

``` text
Algorithm
Data lifetime
Certificate
Dependency
Migration time
Observed evidence
```

This makes hallucination much easier to control.

------------------------------------------------------------------------

# 54. AI Remediation

Eventually:

``` text
Finding
 ↓
AI generates patch
 ↓
Developer reviews
 ↓
Tests
 ↓
Security validation
 ↓
Merge
```

For example:

``` python
RSA.encrypt(...)
```

AI suggests:

``` python
PQC abstraction layer(...)
```

But **never automatically deploy it**.

------------------------------------------------------------------------

# 55. PQC Migration Code Refactoring

A very interesting research direction.

Recent 2026 work on "Quantum-Safe Software Engineering" argues that PQC
migration is not simply a library swap and proposes PQC-aware detection,
semantic refactoring and hybrid verification.
[arXiv](https://arxiv.org/abs/2602.05759?utm_source=chatgpt.com)

That gives ECDAT another possible research module:

``` text
Legacy Crypto
 ↓
Semantic understanding
 ↓
Migration transformation
 ↓
PQC implementation
 ↓
Verification
```

------------------------------------------------------------------------

# 56. Migration Verification Engine

After migration:

``` text
Did RSA disappear?
Did ECDSA disappear?
Are all certificates updated?
Did performance regress?
Did protocol negotiation change?
Did functionality break?
```

So:

``` text
BEFORE
 ↓
MIGRATE
 ↓
AFTER
 ↓
COMPARE
```

------------------------------------------------------------------------

# 57. Cryptographic Attestation

Every inventory result could contain:

``` text
Source
Timestamp
Scanner
Hash
Evidence
Confidence
Signature
```

This means someone can verify:

> "This inventory wasn't modified."

Very useful for government/enterprise environments.

------------------------------------------------------------------------

# 58. Time-Travel Cryptographic Inventory

Store snapshots:

``` text
2026
2027
2028
```

Then:

``` text
Crypto posture improving?
```

Example:

``` text
2026 → 72% quantum vulnerable
2027 → 54%
2028 → 31%
```

------------------------------------------------------------------------

# 59. Crypto Posture Score

Dashboard:

``` text
QUANTUM READINESS
████████░░ 78%

CRYPTO VISIBILITY
█████████░ 91%

CRYPTO AGILITY
█████░░░░░ 52%

CERTIFICATE HEALTH
████████░░ 81%

MIGRATION READINESS
██████░░░░ 63%
```

But each score must be decomposable.

------------------------------------------------------------------------

# 60. Executive → Engineer Drill Down

CISO sees:

``` text
3 critical migration blockers
```

Click:

``` text
↓
Payment infrastructure
```

Click:

``` text
↓
TLS certificate
```

Click:

``` text
↓
ECDSA P-256
```

Click:

``` text
↓
OpenSSL 3.x
```

Click:

``` text
↓
source file / binary evidence
```

That's an amazing UI story.

------------------------------------------------------------------------

# 61. Crypto Attack-Path Simulator

This is even more advanced.

``` text
Quantum capability
       ↓
Break ECDSA
       ↓
Forge certificate
       ↓
Impersonate service
       ↓
Access API
       ↓
Sensitive data
```

Visualize the path.

------------------------------------------------------------------------

# 62. Cryptographic "What Breaks If..."

Give the user natural-language questions:

> What breaks if RSA becomes unsafe?

> Which systems depend on ECDSA?

> Which data is vulnerable to HNDL?

> Which certificates must be replaced?

> Which vendors block migration?

> What should be migrated first?

> What happens if we switch to ML-DSA?

> Which systems cannot support PQC?

That turns the platform into a **cryptographic reasoning engine**.

------------------------------------------------------------------------

# 63. Explainable Risk

Never:

> Risk = 87.

Instead:

``` text
RISK = HIGH

Why?

+ RSA-2048
+ sensitive data
+ 12-year retention
+ internet exposed
+ migration time: 18 months
+ HSM replacement required
+ 14 downstream dependencies
```

This is much stronger academically.

------------------------------------------------------------------------

# 64. Unknown/Uncertainty Engine

This is something I REALLY want in your project.

Most security systems pretend:

``` text
We know.
```

ECDAT should say:

``` text
Known
Probable
Possible
Unknown
```

Example:

``` text
TLS detected        HIGH confidence
RSA detected        HIGH confidence
Actual key usage    MEDIUM confidence
Data classification LOW confidence
Firmware crypto     UNKNOWN
```

Then:

> **Unknown cryptography becomes an actionable finding.**

------------------------------------------------------------------------

# 65. Discovery Coverage Score

Measure:

``` text
Source coverage
Binary coverage
Network coverage
Runtime coverage
Cloud coverage
Hardware coverage
Firmware coverage
Vendor coverage
```

Then:

``` text
Discovery Coverage = 74%
```

This is far more meaningful than pretending inventory is complete.

------------------------------------------------------------------------

# 66. Blind-Spot Detector

ECDAT explicitly asks:

> **Where can't I see?**

For example:

``` text
15,000 assets

Crypto known: 11,400
Unknown: 3,600
```

Then categorize:

``` text
1,200 legacy devices
800 vendor systems
600 firmware
400 cloud
600 unknown
```

That's incredibly useful for an enterprise.

------------------------------------------------------------------------

# 67. Autonomous Discovery Planner

Now here's a research-grade idea.

ECDAT determines:

> "Where should I scan next?"

For example:

``` text
Unknown crypto
       ↓
Internet-facing asset
       ↓
High-value data
       ↓
Legacy hardware
```

Priority:

``` text
SCAN FIRST
```

The tool becomes adaptive rather than just running a fixed scanner.

------------------------------------------------------------------------

# 68. Discovery Feedback Loop

Full system:

``` text
DISCOVER
   ↓
MODEL
   ↓
FIND GAPS
   ↓
SCAN GAPS
   ↓
DISCOVER AGAIN
```

This is **continuous discovery**.

------------------------------------------------------------------------

# 69. Cryptographic Digital Twin

Now combine everything:

``` text
Enterprise
 ├── applications
 ├── networks
 ├── users
 ├── data
 ├── certificates
 ├── algorithms
 ├── keys
 ├── HSMs
 ├── hardware
 ├── vendors
 └── dependencies
```

into one model.

Then simulate:

``` text
PQC migration
certificate expiry
algorithm compromise
hardware failure
vendor discontinuation
```

That is basically a **Cryptographic Digital Twin**.

------------------------------------------------------------------------

# 70. And now the really crazy extension...

ECDAT could eventually answer:

> **"What is the minimum-cost sequence of changes that makes this
> organization quantum-safe while keeping business disruption below
> X?"**

That becomes an optimization problem:

``` text
Minimize:

migration cost
+
downtime
+
performance penalty
+
risk exposure
+
interoperability failures

Subject to:

security requirements
+
business requirements
+
hardware limitations
+
vendor constraints
+
compliance constraints
```

Now you're entering actual research territory.

------------------------------------------------------------------------

# The full ECDAT-X stack

So I would now define the project as:

``` text
                    ECDAT-X
                      │
        ┌─────────────┴──────────────┐
        │                            │
   DISCOVERY                    INTELLIGENCE
        │                            │
 ┌──────┼──────┐              ┌──────┼──────┐
 │      │      │              │      │      │
Source Binary Runtime      Graph   Lineage  DNA
Network Cloud Hardware     Risk    Evidence Coverage
Firmware Config Passive
        │
        ▼
      CBOM
        │
        ▼
┌───────────────────────────────────────────┐
│        CRYPTOGRAPHIC KNOWLEDGE GRAPH      │
└───────────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────────┐
│             RISK INTELLIGENCE             │
│                                           │
│ Quantum │ HNDL │ Business │ Dependency   │
│ Mosca   │ Exposure │ Criticality │ Blast │
└───────────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────────┐
│          MIGRATION INTELLIGENCE            │
│                                           │
│ PQC │ Hybrid │ Compatibility │ Cost      │
│ Benchmark │ Ordering │ Digital Twin      │
└───────────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────────┐
│              REMEDIATION                  │
│                                           │
│ AI │ Refactoring │ CI/CD │ Policy        │
│ Validation │ Regression │ Rollback        │
└───────────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────────┐
│          CONTINUOUS CRYPTO POSTURE        │
└───────────────────────────────────────────┘
```

## And there are still unexplored areas

I haven't even fully expanded:

-   **formal verification of migration**
-   **side-channel risk intelligence**
-   **randomness/entropy quality analysis**
-   **cryptographic implementation fingerprinting**
-   **compiler-level crypto detection**
-   **WASM/browser JavaScript cryptography**
-   **mobile Android/iOS crypto discovery**
-   **API-level cryptographic misuse**
-   **database-native encryption**
-   **email/P​GP/S​MIME discovery**
-   **VPN/IPsec migration**
-   **SSH fleet migration**
-   **Kerberos/Active Directory cryptography**
-   **RADIUS/EAP cryptography**
-   **Wi-Fi cryptography**
-   **5G/telecom crypto**
-   **satellite/space systems**
-   **automotive ECUs**
-   **medical devices**
-   **payment/HSM infrastructure**
-   **blockchain consensus migration**
-   **zero-knowledge proof systems**
-   **cryptographic implementation vulnerability correlation**
-   **CVE → crypto asset correlation**
-   **EPSS/KEV-style crypto prioritization**
-   **threat-intelligence correlation**
-   **vendor EOL prediction**
-   **algorithm deprecation forecasting**
-   **cryptographic monoculture detection**
-   **cross-organization dependency analysis**
-   **privacy-preserving inventory sharing**
-   **federated CBOM**
-   **multi-cloud crypto posture**
-   **quantum-safe procurement intelligence**
-   **migration contract/SLA tracking**
-   **automated evidence generation for auditors**
-   **compliance-as-code**
-   **cryptographic incident response**
-   **emergency algorithm-replacement mode**

And those are not just random feature ideas: the current ecosystem is
visibly moving toward **continuous discovery, interoperability,
migration planning, and crypto agility**, while the IETF's CADI work is
still explicitly identifying gaps in how legacy and heterogeneous
environments can be inventoried. [IETF
Datatracker](https://datatracker.ietf.org/doc/html/draft-liu-cadi-00)

### The biggest realization

The PS says:

> **"Find cryptographic assets and recommend PQC."**

Your research-grade interpretation should be:

> **"Build a continuously updated model of an organization's
> cryptographic reality, understand what each cryptographic dependency
> protects, quantify quantum and operational risk, simulate migration
> options, determine what will break, generate the safest migration
> sequence, validate the migration, and continuously detect
> cryptographic drift."**

That is **far beyond a CBOM generator**.

And I think **this is the direction we should lock before writing any
more code**: first build the **complete ECDAT-X research architecture +
module hierarchy + data model + 100-feature backlog**, then identify
which \~15--20 features are actually buildable for SIH and which belong
in the research/roadmap layer.

## Uploaded Research Note 3

Yes. And **this is the point where I would stop adding features**.

If I think like someone building a serious security product in
2035---not like someone trying to make an impressive SIH demo---the
question changes from:

> "What more can ECDAT do?"

to:

> **"What fundamental problem will still be unsolved even after
> enterprises have scanners, CBOMs, SBOMs, AI, PQC libraries and cloud
> security tools?"**

I think I found the answer.

NIST's current migration work already separates the problem into
**cryptographic visibility/risk management** and
**interoperability/benchmarking**. The current IETF CADI work describes
continuous discovery, normalization and correlation, while recent
research is moving toward dependency-aware migration planning. [NIST
Pages](https://pages.nist.gov/nccoe-migration-post-quantum-cryptography/?utm_source=chatgpt.com)

So ECDAT should **not** try to win by having 150 scanners.

It should solve the deeper problem:

# The real problem is not "Where is cryptography?"

It is:

> **"Can I trust my understanding of my cryptographic environment enough
> to safely change it?"**

That's a much harder problem.

------------------------------------------------------------------------

# 1. The real enemy: Cryptographic uncertainty

Imagine a company has 50,000 assets.

ECDAT discovers:

``` text
38,200 crypto assets
```

Great.

But then ask:

``` text
How many are actually used?
How many are production?
How many are dead?
Which application owns them?
What data do they protect?
Which dependencies rely on them?
Can they be changed?
Who is allowed to change them?
What happens if we change them?
```

Suddenly the inventory isn't enough.

You need an:

# **Evidence Engine**

Every statement ECDAT makes should have an evidence chain.

Instead of:

``` text
RSA-2048
Risk: HIGH
```

ECDAT should internally represent:

``` text
CLAIM
│
├── Evidence
│   ├── source file
│   ├── binary signature
│   ├── runtime observation
│   ├── TLS handshake
│   └── certificate
│
├── Timestamp
│
├── Detection method
│
├── Confidence
│
└── Contradictions
```

Then:

``` text
RSA-2048
Confidence: 97%
Observed: 3 sources
Last observed: 14:22 UTC
```

But perhaps:

``` text
PQC support
Confidence: 42%
Evidence: vendor documentation only
Runtime validation: absent
```

That distinction is **extremely important**.

A recent 2026 treatment of CBOMs specifically emphasizes evidence
capture, while the emerging CADI work is about identifying, normalizing,
correlating and continuously maintaining crypto assets.
[Springer](https://link.springer.com/chapter/10.1007/978-3-032-28946-9_1?utm_source=chatgpt.com)

------------------------------------------------------------------------

# 2. ECDAT needs to understand "truth", not just detection

This is where I'd make the architecture fundamentally different.

Create three layers:

``` text
OBSERVED
    ↓
INFERRED
    ↓
ASSERTED
```

### Observed

"I saw this."

Example:

``` text
TLS handshake
ECDHE
X25519
```

### Inferred

"Given these observations, this is probably being used."

### Asserted

"The organization claims this service uses X."

Now ECDAT can detect:

``` text
ORGANIZATION CLAIMS:

PQC enabled

        ↓

ECDAT OBSERVES:

Classical X25519 only

        ↓

CONFLICT
```

That is much more powerful than another scanner.

------------------------------------------------------------------------

# 3. The hardest problem: Identity

Here's something I think we missed before.

You need an:

# **Asset Identity Engine**

Suppose these all refer to the same thing:

``` text
payment-api
payment-api-prod
pay-prod-02
10.20.4.17
container abc123
Kubernetes pod xyz
AWS instance i-xxx
GitHub repository /payment
TLS certificate abc
```

Are those:

``` text
8 assets?
```

or

``` text
1 system represented 8 ways?
```

If ECDAT doesn't solve this, the knowledge graph becomes garbage.

So:

``` text
                    SYSTEM
                       │
        ┌──────────────┼──────────────┐
        ↓              ↓              ↓
   repository       container       server
        ↓              ↓              ↓
       code          runtime        network
        │              │              │
        └──────────────┼──────────────┘
                       ↓
                 CRYPTO ASSET
```

This is **entity resolution for cybersecurity**.

And honestly, I would consider this one of the deepest parts of the
project.

------------------------------------------------------------------------

# 4. Stop thinking CBOM. Think "Cryptographic Reality Graph"

CBOM should become only an **output format**.

Your internal representation should be richer:

``` text
                    DATA
                     │
                  protects
                     │
                  CRYPTO
                 /   |   \
                /    |    \
          implemented used  configured
              /       |       \
          library   service    policy
             |         |         |
          version    runtime     owner
             |         |
          vendor     network
```

Then:

``` text
CBOM = projection of the graph
```

That's an important architectural decision.

Because tomorrow the enterprise might use:

``` text
CBOM
SBOM
HBOM
OBOM
SaaSBOM
```

Your system shouldn't care.

It should have its own **canonical cryptographic knowledge model**.

The 2026 CBOM research is already moving toward integration with
SBOM/HBOM/OBOM rather than treating CBOM as an isolated artifact.
[Springer](https://link.springer.com/chapter/10.1007/978-3-032-28946-9_1?utm_source=chatgpt.com)

------------------------------------------------------------------------

# 5. The biggest missing thing: "Can I change it?"

This is where I'd differentiate ECDAT.

Every cryptographic asset should have a:

# **Changeability Profile**

For example:

``` text
RSA-2048
│
├── Algorithm configurable? YES
├── Library configurable? YES
├── Protocol configurable? NO
├── Certificate automation? YES
├── HSM replacement required? NO
├── Vendor dependency? YES
├── Source modification required? NO
├── Restart required? YES
├── Downtime required? UNKNOWN
└── Rollback possible? YES
```

Then ECDAT knows:

> **This asset is vulnerable.**

But more importantly:

> **This asset is changeable in this way.**

That is what a migration team actually needs.

------------------------------------------------------------------------

# 6. Model the organization as a system that can change

This leads to something bigger:

# **Cryptographic Change Graph**

Normal graph:

``` text
A depends on B
```

Your graph:

``` text
A
│
├── depends on B
├── can modify B
├── requires C to change B
├── must coordinate with D
└── breaks E if changed incorrectly
```

Now you can ask:

> "What is the safest sequence of changes?"

This is where the recent dependency-aware migration research becomes
relevant. One 2026 IEEE study explicitly models migration as a
dependency-ordering problem because changing assets independently can
cause interoperability failures. [IEEE
Xplore](https://ieeexplore.ieee.org/abstract/document/11541993/authors?utm_source=chatgpt.com)

------------------------------------------------------------------------

# 7. The system should learn from failed migrations

This is a big 10-year idea.

Imagine ECDAT observes:

``` text
Migration attempt
      ↓
Failure
      ↓
Reason
```

Example:

``` text
Migrated certificate
       ↓
Client rejected handshake
       ↓
Legacy client only supports RSA
```

ECDAT stores:

``` text
Migration Knowledge
```

Next time:

``` text
New service
↓
Same dependency pattern
↓
ECDAT warns BEFORE migration
```

Eventually:

# **ECDAT becomes a migration memory.**

Not merely a scanner.

------------------------------------------------------------------------

# 8. Build a "Cryptographic Failure Model"

This is probably more valuable than adding another scanner.

For every migration:

``` text
CHANGE
 ↓
What can fail?
```

Possible failure dimensions:

``` text
Security
Performance
Compatibility
Availability
Interoperability
Compliance
Hardware
Vendor
Cost
Operations
```

So:

``` text
RSA → ML-DSA
```

doesn't produce:

> Recommended: ML-DSA

It produces:

``` text
SECURITY
✓ quantum resistance

PROTOCOL
⚠ certificate ecosystem compatibility

PERFORMANCE
⚠ larger signatures

NETWORK
⚠ increased payload

HARDWARE
⚠ HSM compatibility unknown

VENDOR
⚠ vendor firmware required

ROLLBACK
✓ supported
```

Now it behaves like an **engineering decision system**.

------------------------------------------------------------------------

# 9. Don't build a "recommendation engine"

Build a:

# **Constraint Solver**

This is a major conceptual upgrade.

Suppose the enterprise says:

``` text
Requirement:

Latency < 10 ms
Bandwidth increase < 15%
No hardware replacement
Must support existing clients
Must be reversible
```

ECDAT searches possible migration strategies.

``` text
Option A
fails bandwidth

Option B
fails HSM

Option C
satisfies all constraints

Option D
requires vendor upgrade
```

The output isn't:

> "C is best."

Instead:

> **C satisfies the defined constraints; A/B/D violate these constraints
> for these reasons.**

That's scientifically cleaner and more useful.

------------------------------------------------------------------------

# 10. Introduce "Migration Invariants"

This is something I'd absolutely put into the research architecture.

Before migration, define things that **must remain true**:

``` text
Authentication must continue working
Data confidentiality must remain ≥ required level
Latency < 50ms
No unsupported clients
No loss of auditability
Rollback available
```

Then:

``` text
BEFORE
   ↓
CHANGE
   ↓
VERIFY INVARIANTS
   ↓
ACCEPT / REJECT
```

This is much closer to formal engineering than "run scanner → get green
check."

------------------------------------------------------------------------

# 11. Formal verification becomes the long-term direction

The 2026 research direction on Quantum-Safe Software Engineering is
interesting here: it explicitly argues that PQC migration isn't simply
swapping a library and proposes **PQC-aware detection, semantic
refactoring and hybrid verification**.
[arXiv](https://arxiv.org/abs/2602.05759?utm_source=chatgpt.com)

So the future ECDAT architecture should eventually become:

``` text
DISCOVER
   ↓
MODEL
   ↓
PROPOSE CHANGE
   ↓
PROVE / VERIFY
   ↓
DEPLOY
   ↓
OBSERVE
   ↓
ROLLBACK IF NECESSARY
```

That's a very different product from a scanner.

------------------------------------------------------------------------

# 12. Security of ECDAT itself

This is something feature-heavy designs often completely forget.

You're building a system that potentially sees:

``` text
source code
certificates
infrastructure
network topology
crypto configurations
HSM metadata
cloud architecture
secrets metadata
business-critical systems
```

If ECDAT gets compromised:

**the attacker gets an extremely valuable map of the organization's
cryptographic defenses.**

Therefore ECDAT itself needs:

### Zero-trust architecture

``` text
Collector
   ↓
authenticated channel
   ↓
ingestion
   ↓
validation
   ↓
isolated analysis
```

### Never collect private key material.

### Cryptographically sign inventory evidence.

### Immutable audit trail.

### RBAC/ABAC.

### Tenant isolation.

### Encryption at rest.

### Encryption in transit.

### Collector least privilege.

### Tamper detection.

### Evidence provenance.

This isn't an optional enterprise feature.

**It's a requirement.**

------------------------------------------------------------------------

# 13. The scanner must assume the environment is hostile

An international-grade security tool cannot assume:

``` text
input = trustworthy
```

What if a repository contains:

``` text
malicious source
malformed binary
zip bomb
hostile container
crafted certificate
malicious firmware
```

Your parser itself becomes an attack surface.

Therefore:

``` text
UNTRUSTED INPUT
      ↓
sandbox
      ↓
parser
      ↓
normalized representation
      ↓
analysis
```

This is **security engineering**, not feature engineering.

------------------------------------------------------------------------

# 14. Don't upload enterprise source code to an AI model

A serious architecture should support:

``` text
                    ECDAT
                      │
          ┌───────────┴───────────┐
          │                       │
       Local AI               Cloud AI
          │                       │
   sensitive evidence       sanitized data
```

AI should operate on:

``` text
structured findings
metadata
AST fragments
sanitized context
```

rather than:

> "Send entire company's source code to an LLM."

That's a massive enterprise requirement.

------------------------------------------------------------------------

# 15. Make the architecture agentless first

This is important.

Don't start with:

> Install our ECDAT agent everywhere.

Enterprises hate that.

Instead:

``` text
Git
CI/CD
SIEM
EDR
CMDB
Cloud APIs
Certificate stores
Network scanners
SBOM
CBOM
KMS
HSM
```

pull existing evidence.

NIST's current PQC migration material already lists existing discovery
approaches/tools for TLS/SSH and certificate discovery, reinforcing that
an ecosystem approach is more realistic than expecting one scanner to
discover everything. [NIST
Pages](https://pages.nist.gov/nccoe-migration-post-quantum-cryptography/?utm_source=chatgpt.com)

So:

# **ECDAT should be an evidence fusion platform.**

Not another isolated scanner.

------------------------------------------------------------------------

# 16. And THEN comes something extremely important:

## Evidence fusion.

Imagine:

``` text
Source scan:
ECDSA

Binary scan:
ECDSA

TLS:
ECDSA

Certificate:
ECDSA

Runtime:
ECDSA
```

Confidence becomes extremely high.

But:

``` text
Source:
RSA

Binary:
unknown

Runtime:
ECDSA

TLS:
ECDSA
```

Now:

> **Source code is not representative of production.**

That's a valuable discovery.

------------------------------------------------------------------------

# 17. ECDAT should detect contradictions

This may become one of the coolest parts of the entire project.

Examples:

### Configuration says:

``` text
TLS 1.3
```

### Network observes:

``` text
TLS 1.2
```

→ **Configuration/Runtime contradiction**

------------------------------------------------------------------------

### SBOM says:

``` text
OpenSSL 3.5
```

### Binary says:

``` text
OpenSSL 1.1
```

→ **Supply-chain/runtime contradiction**

------------------------------------------------------------------------

### Vendor says:

``` text
PQC supported
```

### ECDAT test:

``` text
PQC handshake fails
```

→ **Capability claim unverified**

------------------------------------------------------------------------

This is where ECDAT starts behaving like an **intelligence platform**.

------------------------------------------------------------------------

# 18. Build a "Cryptographic Truth Score"

Not:

> Risk score = 84

Instead:

``` text
CRYPTOGRAPHIC VISIBILITY

Observed       82%
Corroborated   71%
Inferred       18%
Unknown         9%
Contradictory   4%
```

Now the organization knows:

> **How much it actually knows about itself.**

That's a much more profound metric.

------------------------------------------------------------------------

# 19. And I would add one final conceptual layer:

# ECDAT should know when it doesn't know.

This sounds simple.

It isn't.

A mature security system should be able to answer:

``` text
What do you know?
What do you infer?
What don't you know?
What evidence would reduce uncertainty?
```

So the system might say:

> "PQC capability of this HSM is unknown."

Then:

> "To resolve this uncertainty, perform firmware inspection or vendor
> capability test."

That's an **active investigation engine**.

------------------------------------------------------------------------

# 20. ECDAT becomes a closed-loop system

Now put everything together.

``` text
              ┌───────────────┐
              │   DISCOVER    │
              └───────┬───────┘
                      ↓
              ┌───────────────┐
              │   CORRELATE   │
              └───────┬───────┘
                      ↓
              ┌───────────────┐
              │   EVIDENCE    │
              └───────┬───────┘
                      ↓
              ┌───────────────┐
              │    MODEL      │
              └───────┬───────┘
                      ↓
              ┌───────────────┐
              │    ASSESS     │
              └───────┬───────┘
                      ↓
              ┌───────────────┐
              │   SIMULATE    │
              └───────┬───────┘
                      ↓
              ┌───────────────┐
              │    CHANGE     │
              └───────┬───────┘
                      ↓
              ┌───────────────┐
              │    VERIFY     │
              └───────┬───────┘
                      ↓
              ┌───────────────┐
              │    OBSERVE    │
              └───────┬───────┘
                      │
                      └──────────→ DISCOVER
```

That is what I would call **10-years-ahead architecture**.

------------------------------------------------------------------------

# The 7 things I'd actually build

And this is where I disagree with our previous "100 features" direction.

**Do NOT build 100 things.**

Build **7 extraordinarily deep primitives**.

  -----------------------------------------------------------------------
  Core                                What it actually solves
  ----------------------------------- -----------------------------------
  **1. Evidence Fabric**              Can we trust the discovery?

  **2. Asset Identity Graph**         What is actually the same
                                      system/asset?

  **3. Crypto Reality Graph**         What cryptography actually protects
                                      what?

  **4. Uncertainty Engine**           What do we know vs infer vs not
                                      know?

  **5. Change Impact Engine**         What breaks if crypto changes?

  **6. Migration Solver**             What sequence satisfies real
                                      constraints?

  **7. Verification Loop**            Did the migration actually work?
  -----------------------------------------------------------------------

Everything else becomes a **connector, detector, visualization or
plugin** around those seven.

That's much more defensible.

------------------------------------------------------------------------

# And the killer research question

If I were an international researcher judging your project, I wouldn't
be impressed by:

> "We scan Python and detect RSA."

There are already tools and research around inventory and CBOM.

I'd be interested in:

> **"Can we construct an evidence-backed cryptographic dependency graph
> from heterogeneous observations, quantify uncertainty, and
> automatically derive a verifiable, constraint-aware migration plan
> without requiring complete prior knowledge of the enterprise?"**

**That is a research problem.**

And it connects directly to where the field is moving: NIST is treating
visibility/risk and interoperability/benchmarking as distinct migration
challenges; IETF's CADI work is explicitly about continuous discovery
and gaps; recent research is exploring graph-based risk and
dependency-aware migration; and current research is starting to treat
PQC migration as a software-engineering problem rather than a simple
algorithm replacement. [NIST
Pages](https://pages.nist.gov/nccoe-migration-post-quantum-cryptography/?utm_source=chatgpt.com)

### So if we want to make ECDAT genuinely "10 years advanced":

**Don't make it discover more cryptography.**

Make it **understand cryptography with evidence, understand
relationships, understand uncertainty, predict consequences of change,
and verify that change actually worked.**

That is the layer I think we were missing.

## Uploaded Research Note 4

Yes. I went one level deeper this time.

I deliberately **did not search for more features**. I looked at what
NIST, IETF, IBM Research, recent PQC papers, migration frameworks,
certificate work, network-observability work, and recent implementation
research **still leave unresolved**.

And there is a much more interesting answer.

> **The frontier is no longer "discover cryptography."**
>
> The frontier is: **Can a machine establish what cryptography is
> actually doing, prove how certain that knowledge is, predict the
> consequences of changing it, safely execute the change, and prove
> afterward that the security property really survived?**

I cannot honestly claim that literally *nobody* has thought of the ideas
below---research is distributed and some overlap exists. But I found
several **open seams where existing work is fragmented, draft-stage, or
solves only one layer of the problem**. That is where I would push
ECDAT.

------------------------------------------------------------------------

# 1. First: what the world already has

This is important because otherwise we'll accidentally reinvent existing
research.

Today the ecosystem is roughly:

``` text
        DISCOVERY
            ↓
      CBOM / CADI
            ↓
       RISK ASSESSMENT
            ↓
       PQC SELECTION
            ↓
    INTEROPERABILITY TEST
            ↓
       MIGRATION PLAN
```

NIST's current PQC program explicitly separates **cryptographic
visibility/risk management** from **interoperability/benchmarking**.
[NCCoE](https://www.nccoe.nist.gov/applied-cryptography/migration-to-pqc?trk=article-ssr-frontend-pulse_little-text-block&utm_source=chatgpt.com)

The IETF CADI draft now goes substantially beyond simple source
scanning: CBOM, SAST, binary scanning, simulated handshakes, traffic
analysis, process identification and configuration extraction are all
discussed. But it is still an **Internet-Draft**, not an adopted RFC,
and its inventory section remains comparatively open-ended. [IETF
Datatracker](https://datatracker.ietf.org/doc/draft-liu-cadi/?utm_source=chatgpt.com)

CBOM itself is also evolving: recent IBM work discusses evidence
capture, configuration-driven cryptography, ambiguity in naming, and the
distinction between a component **providing** cryptography and
**consuming** it. [IBM
Research](https://research.ibm.com/publications/the-anatomy-of-cryptography-bills-of-materials-standardization-and-practice-in-cyclonedx?utm_source=chatgpt.com)

And graph-based migration planning now exists in research too. [IEEE
Xplore](https://ieeexplore.ieee.org/abstract/document/11541993/authors?utm_source=chatgpt.com)

So:

**CBOM + graph + risk + PQC recommendation is no longer novel enough by
itself.**

We need to go underneath and above those layers.

------------------------------------------------------------------------

# 2. The first fundamental gap: nobody can perfectly observe "cryptographic reality"

This is the deepest problem.

Imagine:

``` text
SOURCE CODE
    ↓
CONFIGURATION
    ↓
LIBRARIES
    ↓
BINARY
    ↓
RUNTIME
    ↓
NETWORK
    ↓
CERTIFICATE
    ↓
HARDWARE
```

These can all tell different stories.

For example:

``` text
Source:
RSA

Config:
ECDSA

Binary:
RSA + ECDSA

Runtime:
ECDSA

Network:
ECDSA

Certificate:
ECDSA
```

What is the truth?

A normal scanner picks one answer.

A mature system should say:

> **There is no single observation called "truth." There are competing
> observations with different confidence, freshness and scope.**

This is a much deeper problem than detection.

------------------------------------------------------------------------

# 3. Build a Cryptographic Epistemology Engine

Yes, I'm deliberately using a philosophical term.

ECDAT should model:

### What was observed?

``` text
OBSERVED
```

### What follows logically from observations?

``` text
INFERRED
```

### What does the vendor/system claim?

``` text
DECLARED
```

### What has actually been tested?

``` text
VERIFIED
```

### What contradicts something else?

``` text
CONFLICTING
```

### What remains unknown?

``` text
UNKNOWN
```

So an asset becomes:

``` text
RSA-2048
────────────────────
Declared       ✓
Static         ✓
Binary         ✓
Runtime        ✗
Network        ✗
Certificate    ✗
Hardware       ?
```

Then:

``` text
Confidence: 0.87
Evidence age: 3 days
Contradictions: 1
```

This is much more powerful than:

> RSA detected.

IBM's recent work already identifies evidence capture as an important
CBOM issue, but the larger idea here is to make **uncertainty itself a
first-class object in the cryptographic model**. [IBM
Research](https://research.ibm.com/publications/the-anatomy-of-cryptography-bills-of-materials-standardization-and-practice-in-cyclonedx?utm_source=chatgpt.com)

------------------------------------------------------------------------

# 4. The second gap: temporal truth

This one is surprisingly important.

Cryptographic inventories are usually treated as:

``` text
Asset → Algorithm
```

But cryptography is **time-dependent**.

Consider:

``` text
09:00 → RSA
10:00 → ECDSA
11:00 → PQ hybrid
12:00 → rollback → RSA
```

A static CBOM may simply say:

``` text
RSA, ECDSA, ML-KEM
```

But that loses the most important information:

> **When was each primitive actually active?**

Therefore build a:

# Cryptographic Time Machine

Every observation becomes:

``` text
(asset, algorithm, context, timestamp, evidence)
```

Then ECDAT can answer:

> When did this service first start using RSA?

> When did it stop?

> Did PQC ever actually become active?

> Did someone roll back?

> Was a vulnerable algorithm active only during a 17-minute deployment
> window?

That turns the inventory into a **cryptographic event stream**.

------------------------------------------------------------------------

# 5. And this leads to something much more interesting: crypto drift causality

Suppose:

``` text
Monday
TLS 1.3 + PQ hybrid

Tuesday
TLS 1.2

Wednesday
TLS 1.3 + PQ hybrid
```

Most systems report:

> Drift detected.

ECDAT should investigate:

``` text
Deployment #1842
       ↓
Configuration change
       ↓
Certificate replacement
       ↓
TLS fallback
       ↓
Crypto downgrade
```

Now it can say:

> **The cryptographic regression was temporally correlated with
> deployment X and configuration Y.**

That is **causal investigation**, not inventory.

------------------------------------------------------------------------

# 6. Third gap: capability ≠ configuration ≠ usage

This distinction is absolutely fundamental.

A server may:

``` text
SUPPORT:
RSA
ECDSA
ML-DSA
```

but actually:

``` text
CONFIGURED:
ECDSA
```

and actually negotiate:

``` text
ACTIVE:
ECDSA
```

and the application may actually authenticate with:

``` text
APPLICATION:
ECDSA
```

Four different realities.

So ECDAT needs four separate states:

``` text
CAPABILITY
     ↓
CONFIGURATION
     ↓
NEGOTIATION
     ↓
ACTUAL USE
```

This becomes particularly important at the network layer. A September
2026 IETF draft points out that existing network telemetry does not
provide structured cryptographic algorithm inventory and that CBOM
cannot tell you the actual session-level negotiation outcome. [IETF
Datatracker](https://datatracker.ietf.org/doc/draft-vicente-pquip-pqc-readiness-gaps/?utm_source=chatgpt.com)

------------------------------------------------------------------------

# 7. Fourth gap: "supported" is not the same as "secure"

This becomes terrifying with PQC hybrids.

Suppose:

``` text
Certificate:
Classical + PQ
```

The verifier accepts it.

You might conclude:

> Hybrid authentication succeeded.

But recent 2026 research found a much subtler issue: some X.509
validation stacks can accept the **classical path while effectively
ignoring whether the PQ evidence contributed to the authentication
decision**. The paper tested multiple validation stacks and describes
this as a structural verifier-semantics problem rather than simply a
missing primitive.
[arXiv](https://arxiv.org/abs/2607.20800?utm_source=chatgpt.com)

This gives us a huge research opportunity:

# Authentication Property Verification

ECDAT should not ask:

> "Does the certificate contain ML-DSA?"

It should ask:

> **"Did ML-DSA actually contribute to the security decision?"**

That distinction is enormous.

------------------------------------------------------------------------

# 8. Build a "Security Property Compiler"

This is one of my favorite ideas.

User specifies:

``` text
REQUIREMENT:

Authentication must remain secure
even if classical public-key cryptography
is broken.
```

ECDAT compiles this into:

``` text
Required:
✓ PQ credential
✓ PQ signature verification
✓ PQ-bearing chain
✓ appropriate trust anchor
✓ PQ evidence must be outcome-bearing
✓ classical fallback prohibited
✓ downgrade detection
```

Then it tests the actual system.

This turns vague security requirements into **machine-verifiable
properties**.

Recent IETF work already highlights that a PQ end-entity certificate
alone is insufficient if the validation chain or trust anchor remains
classical. [IETF
Datatracker](https://datatracker.ietf.org/doc/html/draft-ietf-uta-pqc-app?utm_source=chatgpt.com)

------------------------------------------------------------------------

# 9. Fifth gap: migration plans assume the world behaves deterministically

Most migration algorithms look approximately like:

``` text
Graph
 ↓
Risk
 ↓
Order
 ↓
Migration
```

But real enterprises aren't deterministic.

You don't know:

``` text
Will vendor X deliver firmware?
Will service Y restart correctly?
Will client Z negotiate the new certificate?
Will an undocumented dependency appear?
Will a legacy device fail?
```

So instead of:

> Migration plan

build:

# Probabilistic Migration Simulation

For every migration step:

``` text
Success probability
Failure modes
Dependencies
Unknowns
Rollback options
```

Run thousands of simulated worlds.

Example:

``` text
Strategy A
Expected risk: ...
Failure probability: ...
Worst-case blast radius: ...

Strategy B
Expected risk: ...
Failure probability: ...
Worst-case blast radius: ...
```

This is a **risk simulator**, not a static planner.

------------------------------------------------------------------------

# 10. Sixth gap: nobody has solved "unknown dependency discovery" completely

Graph algorithms assume:

``` text
Graph = reality
```

But the hardest dependencies are precisely the ones **not in the
graph**.

Example:

``` text
Service A
   ↓
Service B
```

Looks safe.

But hidden inside:

``` text
A → undocumented vendor appliance
```

ECDAT doesn't know.

So before migration:

# Dependency Discovery Challenge

Ask:

> **What dependency would have to exist for this migration to fail?**

Then actively search for evidence.

This turns dependency discovery into an **adversarial investigation
problem**.

------------------------------------------------------------------------

# 11. Build an "Unknown Dependency Hunter"

For each planned migration:

``` text
Proposed change
      ↓
Assumptions
      ↓
Potential hidden dependencies
      ↓
Evidence search
      ↓
Confidence
```

Example:

``` text
Assumption:
All clients support PQ hybrid.

ECDAT searches:
- historical TLS logs
- traffic
- client versions
- certificates
- DNS
- service mesh
- source repositories

Result:

Unknown legacy client detected.
```

This is much closer to how elite security teams actually think.

------------------------------------------------------------------------

# 12. Seventh gap: migration itself creates a new attack surface

We have been treating:

``` text
PQC migration = security improvement
```

But migration is itself a security event.

During transition you may have:

``` text
classical + hybrid + PQ
```

simultaneously.

That creates:

``` text
fallbacks
dual certificates
multiple trust paths
multiple key types
different client capabilities
```

And the IETF is actively working on downgrade/rollback protection
because coexistence creates exactly this problem. [IETF
Datatracker](https://datatracker.ietf.org/doc/draft-sheffer-tls-pqc-continuity/?utm_source=chatgpt.com)

Therefore ECDAT needs:

# Migration Attack-Surface Analysis

Before migration:

``` text
Attack surface = A
```

During migration:

``` text
Attack surface = B
```

After migration:

``` text
Attack surface = C
```

The system should analyze **B**, not just A and C.

That's a major gap.

------------------------------------------------------------------------

# 13. Eighth gap: rollback is normally treated as operational, not cryptographic

Imagine:

``` text
Monday:
PQC enabled

Tuesday:
incident

Wednesday:
rollback to classical
```

Operationally:

> Rollback successful.

Cryptographically:

> **You may have silently reintroduced a quantum-vulnerable
> authentication path.**

The current IETF PQC-continuity work is explicitly exploring mechanisms
to prevent this kind of rollback/downgrade behavior. [IETF
Datatracker](https://datatracker.ietf.org/doc/draft-sheffer-tls-pqc-continuity/?utm_source=chatgpt.com)

So ECDAT should have:

# Cryptographic Rollback Safety

Before allowing rollback:

``` text
What security property disappears?
Which assets become vulnerable?
Which clients are affected?
Does policy permit rollback?
How long may rollback remain active?
Who authorized it?
```

That is much deeper than "deployment successful."

------------------------------------------------------------------------

# 14. Ninth gap: crypto agility is often architectural theater

NIST's 2026 crypto-agility paper explicitly says crypto agility involves
replacing/adapting algorithms across protocols, software, hardware,
firmware and infrastructure.
[NIST](https://www.nist.gov/publications/considerations-achieving-crypto-agility-strategies-and-practices-0?utm_source=chatgpt.com)

But recent IBM research found something fascinating: major cryptographic
APIs still have serious gaps. Among the systems examined,
algorithm-specific parameters often leak into applications,
policy-driven algorithm selection is generally missing, and existing
keys cannot generally be transformed to new algorithms automatically.
[IBM
Research](https://research.ibm.com/publications/cryptographic-agility-for-applications-an-assessment-framework-and-principled-api-design?utm_source=chatgpt.com)

So a company can claim:

> "We're crypto agile."

while actually having:

``` text
algorithm hardcoded
   ↓
API leaks algorithm details
   ↓
application depends on RSA semantics
```

Therefore:

# Crypto Agility Reverse Proof

Don't give a score.

Try to **break the claim**.

Ask:

> Can I replace this algorithm without modifying business logic?

Then actually perform a controlled transformation in a sandbox.

If:

``` text
RSA → ML-DSA
```

requires:

``` text
47 code changes
3 API changes
2 schema changes
```

then:

> The system is not truly algorithm-independent.

That's a much more rigorous definition of agility.

------------------------------------------------------------------------

# 15. Tenth gap: key migration is different from algorithm migration

This is huge.

Suppose:

``` text
RSA key
```

needs to become:

``` text
ML-DSA key
```

You cannot simply "convert" an RSA private key into an ML-DSA private
key.

Recent research on cryptographic API agility specifically identifies
lack of **key transformation** as one of the obstacles to true agility.
[IBM
Research](https://research.ibm.com/publications/cryptographic-agility-for-applications-an-assessment-framework-and-principled-api-design?utm_source=chatgpt.com)

Therefore ECDAT should distinguish:

``` text
Algorithm migration
Key migration
Identity migration
Certificate migration
Trust migration
Protocol migration
Application migration
```

These are different problems.

------------------------------------------------------------------------

# 16. Eleventh gap: trust migration is bigger than certificate migration

Suppose you replace:

``` text
RSA certificate
```

with:

``` text
ML-DSA certificate
```

You still have:

``` text
Root CA
Intermediate CA
Trust store
Device provisioning
Firmware trust
OS trust
Application trust
```

The current IETF PQC application draft emphasizes exactly this: the PQ
property depends on the **validation path up to the configured trust
anchor**, not merely the leaf certificate. [IETF
Datatracker](https://datatracker.ietf.org/doc/html/draft-ietf-uta-pqc-app?utm_source=chatgpt.com)

So build:

# Trust Graph

``` text
Root
 ↓
Intermediate
 ↓
Leaf
 ↓
Service
 ↓
Client
 ↓
Trust Store
```

Then simulate:

> "What happens if this trust anchor changes?"

This is much more powerful than certificate inventory.

------------------------------------------------------------------------

# 17. Twelfth gap: the physical world doesn't migrate at software speed

This is one of the largest unsolved practical problems.

A cloud server:

``` text
upgrade → minutes
```

A:

``` text
industrial controller
satellite
vehicle ECU
medical device
smart meter
telecom appliance
```

may have:

``` text
10–20 year lifecycle
```

Recent work continues to identify constrained hardware, OT,
hardware/software co-design and interoperability as major PQC deployment
challenges.
[ScienceDirect](https://www.sciencedirect.com/science/article/pii/S1574013726000833?utm_source=chatgpt.com)

And interestingly, recent Bluetooth research found that PQC can be
computationally feasible on constrained hardware while **communication
overhead, packetization, retransmissions and wireless reliability**
become the actual bottleneck.
[ScienceDirect](https://www.sciencedirect.com/science/article/pii/S2542660526000776?utm_source=chatgpt.com)

So:

> CPU benchmark ≠ migration feasibility.

------------------------------------------------------------------------

# 18. Build a "Physical Migration Model"

For each hardware asset:

``` text
CPU
RAM
Flash
network MTU
battery
firmware update mechanism
bootloader
secure boot
HSM/TPM
physical access
field-service cycle
vendor support lifetime
```

Then:

``` text
PQC feasibility
```

becomes a systems problem.

Not:

> "Does ML-KEM run?"

But:

> **"Can this physical system survive the entire PQC protocol and
> operational lifecycle?"**

That's a far stronger question.

------------------------------------------------------------------------

# 19. Thirteenth gap: energy is a security constraint

For:

``` text
battery devices
satellites
IoT
wearables
industrial sensors
```

energy isn't merely performance.

It affects:

``` text
availability
DoS resilience
battery lifetime
maintenance frequency
physical accessibility
```

So ECDAT could model:

``` text
Crypto operation
 ↓
energy
 ↓
battery impact
 ↓
availability
```

Recent constrained-device research demonstrates why this matters:
algorithm-level compute may look acceptable while communication overhead
dominates the real system cost.
[ScienceDirect](https://www.sciencedirect.com/science/article/pii/S2542660526000776?utm_source=chatgpt.com)

------------------------------------------------------------------------

# 20. Fourteenth gap: PQC implementation security

This is enormous.

NIST-standardized algorithm:

``` text
mathematically secure
```

does **not** mean:

``` text
implementation secure
```

Implementation can leak through:

``` text
timing
cache
power
EM
fault injection
memory
branching
compiler behavior
hardware acceleration
```

Recent PQC deployment surveys continue to identify side-channel
resilience and implementation correctness as open engineering issues.
[ScienceDirect](https://www.sciencedirect.com/science/article/pii/S1574013726000833?utm_source=chatgpt.com)

So ECDAT should eventually have:

# Implementation Assurance Layer

Instead of:

> ML-KEM detected.

It should eventually be capable of asking:

``` text
Which implementation?
Which version?
Which architecture?
Constant-time?
Known side-channel issues?
Hardware acceleration?
Compiler?
Build flags?
Known CVEs?
Known leakage?
```

------------------------------------------------------------------------

# 21. Fifteenth gap: the compiler can change the security properties

This is an extremely deep research direction.

You write:

``` c
constant_time_crypto();
```

But then:

``` text
compiler
 ↓
optimization
 ↓
different machine code
```

Your source-level analysis says:

> Safe.

Your binary may behave differently.

So:

``` text
SOURCE SECURITY
        ↓
COMPILER
        ↓
BINARY SECURITY
```

ECDAT could eventually compare:

> **security assumptions at source vs actual generated machine
> behavior.**

That is a serious research direction.

------------------------------------------------------------------------

# 22. Sixteenth gap: cryptographic monoculture

Imagine:

``` text
10,000 systems

9,700 use:
ECDSA P-256
```

Your risk isn't merely:

``` text
9700 vulnerable assets
```

There's a structural problem:

> **One primitive dominates the entire ecosystem.**

If a common implementation/library/parameter has a systemic problem:

``` text
single weakness
 ↓
massive correlated impact
```

Therefore ECDAT should detect:

# Crypto Monocultures

Examples:

``` text
same algorithm
same library
same vendor
same HSM
same certificate authority
same firmware
same implementation
```

This is analogous to concentration risk in finance.

------------------------------------------------------------------------

# 23. Seventeenth gap: cryptographic systemic risk

Now combine:

``` text
algorithm centrality
+
vendor centrality
+
library centrality
+
certificate authority centrality
+
hardware centrality
```

You might discover:

``` text
OpenSSL version X
       ↓
73% of enterprise services
```

or:

``` text
Vendor HSM
       ↓
91% of signing infrastructure
```

That is not ordinary vulnerability scanning.

It's:

# Cryptographic Systemic Risk

Recent graph-based research already explores structural importance and
single points of failure, but the broader concentration/correlation
problem is still largely open.
[ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0950584926000881?utm_source=chatgpt.com)

------------------------------------------------------------------------

# 24. Eighteenth gap: adversarial cryptographic discovery

This one is really interesting.

What if the environment is deliberately hiding crypto?

An attacker may:

``` text
obfuscate implementation
dynamically load libraries
custom implement algorithms
use proprietary protocols
encrypt configuration
```

So ECDAT should have an:

# Adversarial Discovery Mode

Ask:

> **If an attacker wanted to hide this cryptography from ECDAT, how
> would they do it?**

Then design detectors against those evasions.

This changes ECDAT from:

``` text
scanner
```

to:

``` text
red-teamable discovery system
```

------------------------------------------------------------------------

# 25. Nineteenth gap: deception detection

Suppose:

``` text
CBOM:
ML-KEM

Runtime:
X25519
```

Maybe:

``` text
PQC exists
but isn't actually active.
```

Or a vendor could generate:

``` text
"quantum-safe" metadata
```

without actually providing the promised property.

Therefore:

# Capability Claim Verification

ECDAT should test claims.

``` text
Vendor says:
PQC supported

ECDAT:
prove it.
```

Then:

``` text
Claim
 ↓
Test
 ↓
Observed behavior
 ↓
Evidence
```

This is an extremely strong concept for an enterprise tool.

------------------------------------------------------------------------

# 26. Twentieth gap: "cryptographic property" should be first-class

Currently systems mostly track:

``` text
algorithm = X
```

But the actual requirement is:

``` text
confidentiality
integrity
authentication
non-repudiation
forward secrecy
quantum resistance
key establishment
identity binding
```

So ECDAT should represent:

``` text
CRYPTO ASSET
      ↓
SECURITY PROPERTY
      ↓
BUSINESS REQUIREMENT
```

Example:

``` text
ECDSA
 ↓
authentication
 ↓
device identity
 ↓
industrial safety system
```

Now the migration question becomes:

> What alternative preserves the **same security property**?

Much more powerful.

------------------------------------------------------------------------

# 27. Twenty-first gap: security properties can disappear during migration

Suppose:

``` text
Old system:
authentication + forward secrecy
```

New migration:

``` text
PQC replacement
```

Maybe:

``` text
authentication preserved
but forward secrecy accidentally changed
```

A scanner might say:

> PQC = PASS.

ECDAT should say:

``` text
Quantum resistance ✓
Authentication ✓
Forward secrecy ⚠
Certificate binding ⚠
Rollback safety ✗
```

That's **security-property regression detection**.

------------------------------------------------------------------------

# 28. Twenty-second gap: migration needs experiments, not recommendations

This is where we can go radically beyond normal software.

Suppose ECDAT wants to migrate:

``` text
ECDH
→
X25519 + ML-KEM
```

Don't merely recommend it.

Construct a controlled:

# Migration Sandbox

``` text
Production topology
        ↓
isolated replica
        ↓
apply migration
        ↓
run synthetic traffic
        ↓
measure
        ↓
fault injection
        ↓
rollback
```

Measure:

``` text
latency
throughput
CPU
memory
packet loss
certificate validation
timeouts
retries
failure rate
security properties
```

NIST's migration program explicitly includes interoperability and
benchmarking because real migration cannot be solved from algorithm
names alone.
[NCCoE](https://www.nccoe.nist.gov/applied-cryptography/migration-to-pqc?utm_source=chatgpt.com)

------------------------------------------------------------------------

# 29. Twenty-third gap: chaos engineering for cryptography

This is a concept I would seriously investigate.

We have:

> Chaos engineering

for distributed systems.

Why not:

# Cryptographic Chaos Engineering?

Intentionally inject:

``` text
remove PQ algorithm
disable classical algorithm
expire certificate
increase signature size
reduce MTU
break one trust anchor
force fallback
simulate old client
remove HSM capability
introduce latency
```

Then ask:

> Does the system fail safely?

This could become a **new research direction around crypto migration
resilience**.

------------------------------------------------------------------------

# 30. Twenty-fourth gap: "fail-safe" vs "fail-open" cryptographic behavior

This is extremely important.

Suppose PQ verification fails.

Does the system:

``` text
A → reject
```

or:

``` text
B → silently fall back to classical
```

B may be operationally convenient but cryptographically dangerous.

ECDAT should systematically test:

``` text
failure
 ↓
fallback
 ↓
security property
```

and classify:

``` text
SAFE FAILURE
UNSAFE FAILURE
UNKNOWN FAILURE
```

------------------------------------------------------------------------

# 31. Twenty-fifth gap: migration observability is incomplete

NIST's six-phase model goes through:

``` text
discovery
risk
migration
testing
validation
monitoring
```

But the actual telemetry connecting these stages is fragmented. [IETF
Datatracker](https://datatracker.ietf.org/doc/draft-liu-cadi/?utm_source=chatgpt.com)

So ECDAT should maintain:

``` text
Asset
 ↓
Risk assessment
 ↓
Migration decision
 ↓
Change
 ↓
Test
 ↓
Deployment
 ↓
Observed production behavior
```

One continuous lineage.

Call it:

# Cryptographic Change Provenance

For every migration:

``` text
WHY
WHAT
WHO
WHEN
HOW
EVIDENCE
RESULT
ROLLBACK
```

------------------------------------------------------------------------

# 32. Twenty-sixth gap: "Why did the system make this decision?"

AI makes this harder.

If AI recommends:

``` text
ML-KEM
```

the system must be able to reconstruct:

``` text
Input evidence
 ↓
Constraints
 ↓
Threat model
 ↓
Benchmark results
 ↓
Compatibility checks
 ↓
Recommendation
```

So every recommendation needs:

# Decision Provenance

Not:

> AI recommends ML-KEM.

But:

``` text
Recommendation R-1042

Evidence:
E1
E2
E3
E4

Constraints:
C1
C2
C3

Alternatives:
A
B
C

Rejected because:
...

Human approval:
...

Outcome:
...
```

That's how you make AI usable in high-assurance cybersecurity.

------------------------------------------------------------------------

# 33. Twenty-seventh gap: AI itself can become an attack surface

Imagine an attacker inserts malicious source code containing:

``` text
"Ignore previous security findings..."
```

and your AI analyst consumes repository content.

That's prompt injection.

Or:

``` text
malicious certificate metadata
```

or:

``` text
crafted README
```

So:

# Untrusted Evidence → AI Isolation

Architecture:

``` text
UNTRUSTED DATA
       ↓
parser
       ↓
typed evidence
       ↓
policy filter
       ↓
AI
```

Never:

``` text
raw repository → LLM → security decision
```

The AI should reason over **typed, provenance-linked facts**.

------------------------------------------------------------------------

# 34. Twenty-eighth gap: ECDAT needs adversarial self-testing

The platform should continuously ask:

> "How could my own conclusion be wrong?"

For every finding:

``` text
Finding:
RSA-2048 active

Counter-hypothesis:
RSA code exists but is unreachable.

Search:
Call graph
Runtime
Network
Coverage
```

Then:

``` text
Finding confidence ↑ or ↓
```

This is:

# Hypothesis Testing for Cybersecurity

Not just detection.

------------------------------------------------------------------------

# 35. Twenty-ninth gap: active information gathering

Once ECDAT understands uncertainty:

``` text
Unknown:
HSM supports ML-DSA?
```

It should determine:

> What single observation would reduce uncertainty the most?

Maybe:

``` text
vendor API query
```

or:

``` text
firmware version
```

or:

``` text
controlled handshake
```

This becomes:

# Information-Gain-Driven Discovery

Instead of scanning everything equally.

Mathematically:

``` text
Choose next investigation
that maximizes:

expected uncertainty reduction
/
investigation cost
```

That is a **research-grade discovery strategy**.

------------------------------------------------------------------------

# 36. Thirtieth gap: the system should optimize knowledge, not scans

Traditional:

``` text
Scan everything.
```

Future:

``` text
Where should I look next?
```

Suppose:

``` text
Asset A:
risk unknown
investigation cost = 1

Asset B:
risk unknown
investigation cost = 100

Asset C:
risk unknown
investigation cost = 3
```

ECDAT chooses the investigation that provides the greatest useful
knowledge per unit cost.

That's the beginning of an:

# Autonomous Cryptographic Investigation Engine

And **that**, honestly, is one of the most interesting directions I
found.

------------------------------------------------------------------------

# Now let's combine the genuinely deep gaps

We can reduce everything above into **five research primitives**.

## Primitive 1 --- Cryptographic Reality

``` text
Observed
Declared
Inferred
Verified
Unknown
Contradictory
```

------------------------------------------------------------------------

## Primitive 2 --- Cryptographic Causality

``` text
What caused this crypto state?

Deployment
Config
Library
Certificate
Runtime
Vendor
Network
```

------------------------------------------------------------------------

## Primitive 3 --- Cryptographic Change

``` text
If I change X:

What breaks?
Why?
Where?
How badly?
Can I roll back?
```

------------------------------------------------------------------------

## Primitive 4 --- Cryptographic Assurance

``` text
Did the new system actually
preserve the required security properties?
```

------------------------------------------------------------------------

## Primitive 5 --- Cryptographic Investigation

``` text
What do I still not know?

What observation would reduce
that uncertainty most efficiently?
```

------------------------------------------------------------------------

# This gives us something genuinely different

Instead of:

``` text
             ECDAT
               │
        ┌──────┴──────┐
        ↓             ↓
     Scanner        CBOM
        ↓             ↓
       Risk       Recommendation
```

I would now build:

``` text
                  ECDAT-X
                     │
             ┌───────▼────────┐
             │ REALITY ENGINE │
             └───────┬────────┘
                     │
          ┌──────────▼──────────┐
          │ EVIDENCE / IDENTITY │
          └──────────┬──────────┘
                     │
          ┌──────────▼──────────┐
          │ CRYPTOGRAPHIC GRAPH │
          └──────────┬──────────┘
                     │
       ┌─────────────▼─────────────┐
       │       UNCERTAINTY         │
       └─────────────┬─────────────┘
                     │
       ┌─────────────▼─────────────┐
       │      CHANGE SIMULATOR     │
       └─────────────┬─────────────┘
                     │
       ┌─────────────▼─────────────┐
       │    SECURITY PROPERTIES    │
       │       VERIFICATION        │
       └─────────────┬─────────────┘
                     │
       ┌─────────────▼─────────────┐
       │   MIGRATION EXECUTION     │
       └─────────────┬─────────────┘
                     │
       ┌─────────────▼─────────────┐
       │       OBSERVATION         │
       └─────────────┬─────────────┘
                     │
                     └──────► REALITY
```

------------------------------------------------------------------------

# And here is the part I think could become your actual research contribution

## **Cryptographic Reality → Change → Proof**

The system should be able to take this:

> "This enterprise has RSA-2048."

and eventually answer:

> **"Here is the evidence that RSA-2048 is actually active."**

Then:

> **"Here is what depends on it."**

Then:

> **"Here are the security properties it currently provides."**

Then:

> **"Here are the possible replacement states."**

Then:

> **"We simulated the migration under these constraints."**

Then:

> **"This migration causes these possible failures."**

Then:

> **"We selected this transition because it satisfies these explicit
> constraints."**

Then:

> **"We performed the migration."**

Then:

> **"We tested the required properties."**

Then:

> **"We observed the production system and confirmed the predicted
> state."**

And finally:

> **"Here is cryptographically verifiable evidence of the entire
> transition."**

That is not a scanner.

That is a:

# **Cryptographic State Transition Verification System**

And I haven't found a mature system that combines **all of those layers
into one coherent closed loop**. The existing ecosystem is visibly
fragmented across discovery/CADI, CBOM, crypto-agility research,
graph-based planning, interoperability testing, certificate migration
and network observability. [IETF
Datatracker](https://datatracker.ietf.org/doc/draft-liu-cadi/?utm_source=chatgpt.com)

------------------------------------------------------------------------

# The 10-year version

If I were architecting this in 2036, I'd want ECDAT to behave like this:

``` text
                 ENTERPRISE
                     │
                     ▼
              OBSERVE REALITY
                     │
                     ▼
             BUILD CRYPTO GRAPH
                     │
                     ▼
            QUANTIFY UNCERTAINTY
                     │
                     ▼
          IDENTIFY SECURITY PROPERTIES
                     │
                     ▼
             MODEL CHANGE SPACE
                     │
                     ▼
          SIMULATE POSSIBLE FUTURES
                     │
                     ▼
           FIND SAFE TRANSITION
                     │
                     ▼
             EXECUTE CHANGE
                     │
                     ▼
          ATTACK THE NEW STATE
                     │
                     ▼
          VERIFY SECURITY PROPERTIES
                     │
                     ▼
           OBSERVE PRODUCTION
                     │
                     ▼
        COMPARE PREDICTED VS ACTUAL
                     │
                     ▼
              UPDATE MODEL
                     │
                     └───────────┐
                                 │
                                 ▼
                              REPEAT
```

## And the deepest idea is this:

**The system shouldn't merely tell an organization what cryptography it
has.**

It should maintain a continuously updated answer to:

> ### **"What cryptographic state is the organization actually in, how certain are we, what security properties does that state provide, what states can we safely transition to, and can we prove that the transition preserved those properties?"**

That is the gap I'd chase.

Not another scanner.

Not another dashboard.

Not another CBOM generator.

**A machine-verifiable model of cryptographic reality and safe
cryptographic change.**

And importantly, this direction is not detached from today's technology:
NIST is explicitly pushing visibility, risk management, interoperability
and crypto agility; the IETF is currently working on CADI, network
observability and PQC downgrade continuity; recent research is exposing
certificate-verifier semantics, API-agility limitations,
dependency-aware migration and constrained-device deployment problems.
[NIST](https://www.nist.gov/publications/considerations-achieving-crypto-agility-strategies-and-practices-0?utm_source=chatgpt.com)

**This is where I would stop searching for "more features."**

The next step should be to turn these gaps into a **research
architecture**: define the formal data model, the graph ontology,
evidence model, uncertainty mathematics, change model, security-property
model, simulator, verification model, and then identify **which parts
can actually be implemented for SIH versus which parts become your
research novelty**.
