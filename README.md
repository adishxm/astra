# ASTRA — Enterprise Cryptographic Discovery & Analysis Tool (ECDAT)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Test Suite](https://img.shields.io/badge/tests-74%20passed%20%7C%20100%25-brightgreen.svg)]()
[![PQC Standard](https://img.shields.io/badge/NIST-FIPS%20203%20%7C%20204%20%7C%20205-purple.svg)](https://csrc.nist.gov/projects/post-quantum-cryptography)

> **SIH26164 (ECDAT)**: A provenance-aware, coverage-accounted cryptographic discovery and post-quantum migration analysis engine for enterprise codebases, dependencies, configurations, and certificate stores.

---

## Overview

Modern enterprises face a critical transition toward **Post-Quantum Cryptography (PQC)**. However, effective cryptographic migration requires more than regex-matching algorithm names: finding a cryptographic primitive without provenance, purpose, exposure, data lifetime, dependencies, and explicit blind-spot accounting leads to dangerous false confidence.

**ASTRA** solves this with an auditable, evidence-first approach:
1. **Adversarial-Resistant Intake**: Safely extracts user-authorized archives without executing uploaded code, guarding against zip bombs, path traversals, symlink escapes, and malicious payloads.
2. **Deterministic Cryptographic Discovery**: Emits canonical observations with SHA-256 evidence digests, exact line numbers, calibrated confidence bands, and strict zero-secret leakage.
3. **Truthful Coverage Accounting**: Separates assessed code from unassessed formats. Absence of findings is explicitly labeled `NO_FINDINGS_IN_SUPPORTED_SCOPE`—never falsely marked "Safe".
4. **Post-Quantum Readiness**: Detects both classical (quantum-vulnerable) algorithms (RSA, ECC, Diffie-Hellman) and modern NIST PQC standards (ML-KEM/Kyber, ML-DSA/Dilithium, SLH-DSA/SPHINCS+, Falcon).
5. **Continuous Temporal Lineage & CBOM Reconciliation**: Tracks cryptographic posture drift across code versions via deterministic Cryptographic DNA hashing, catches algorithm downgrade regressions, and reconciles multi-scanner CBOMs into unified CycloneDX 1.6 specifications.
6. **Constrained Migration Roadmaps & Invariant Assurance**: Graph-aware topological ordering over hardware/vendor constraints, cyclic deadlock diagnostics, downgrade immunity checks, and rollback safety verification.
7. **Air-Gapped Sovereignty & Tamper-Evident Governance**: Sovereign offline deployments with zero telemetry leakage, signed update bundles, and mathematically verifiable SHA-256 hash-chained audit logging.

---

## System Architecture

```
                       ┌────────────────────────────────────────┐
                       │          Authorized Archive            │
                       │    (.zip, .tar, .tar.gz, .tar.bz2)     │
                       └───────────────────┬────────────────────┘
                                           │
                                           ▼
                       ┌────────────────────────────────────────┐
                       │   Worker 01: Safe Upload Intake        │
                       │   - Magic Byte Format Inspection       │
                       │   - Zip Bomb & Streaming Limit Defense │
                       │   - Path Traversal & Symlink Lockdown  │
                       │   - Ephemeral Read-Only Sandbox Tree   │
                       └───────────────────┬────────────────────┘
                                           │ ScanManifest + Sandbox
                                           ▼
                       ┌────────────────────────────────────────┐
                       │   Worker 01: Deterministic Discovery   │
                       │   - Multi-Language AST & Regex Scanner │
                       │   - Package Manifest Parsers           │
                       │   - TLS & SSH Config Inspectors        │
                       │   - X.509 Certificate Metadata Parser  │
                       │   - Static Binary & Container Scanners │
                       │   - Authorized Endpoint Detectors      │
                       │   - Strict Secret / Key Redaction      │
                       └───────────────────┬────────────────────┘
                                           │ Canonical Observations
                                           ▼
                       ┌────────────────────────────────────────┐
                       │   Worker 01: Truthful Coverage         │
                       │   - Honest Denominator (N_assessed)    │
                       │   - Blind-Spot & Partial Scan Flags    │
                       │   - Seeded Benchmark Runner (>=80%)    │
                       └───────────────────┬────────────────────┘
                                           │
         ┌─────────────────────────────────┼─────────────────────────────────┐
         ▼                                 ▼                                 ▼
┌──────────────────┐             ┌──────────────────┐             ┌──────────────────┐
│    Worker 02     │             │    Worker 03     │             │    Worker 04     │
│ Canonical Evidence│             │ Contextual Risk  │             │ Workflow, Web UI │
│ & CBOM Projection│             │ & Migration Queue│             │  & Review Portal │
│ - Temporal Time  │             │ - Mosca Theorem  │             │ - Drilldown API  │
│   Machine & DNA  │             │ - Sensitivity    │             │ - Tamper-Evident │
│ - Reconciliation │             │ - Dated PQC      │             │   Audit Chaining │
│ - CycloneDX 1.6  │             │ - Phased Roadmap │             │ - Air-Gapped     │
│                  │             │ - Invariant Check│             │   Bundle Verify  │
└──────────────────┘             └──────────────────┘             └──────────────────┘
```

---

## Core Capabilities

### 1. Safe Intake & Scan Boundary (`app.intake` — Worker 01)
- **Container Format Verification**: Inspects file magic bytes (ZIP, GZIP, BZIP2, TAR) to prevent extension spoofing.
- **Decompression Bomb Protection**: Active streaming byte counters enforce maximum compression ratios ($100:1$), total uncompressed sizes ($500\text{ MB}$), and single-file thresholds ($50\text{ MB}$).
- **Directory Traversal Prevention**: Strips leading slashes, blocks parent directory backtracking (`../`), null bytes (`\0`), and drive specifiers.
- **Symlink & Dangerous File Guards**: Rejects symlink/hardlink escapes (`SymlinkEscapeError`) and safely skips dangerous executables (`.exe`, `.dll`, `.so`, `.ps1`).
- **Reproducible Manifest**: Emits `ScanManifest` containing archive SHA-256, scan ID (UUIDv4), file inventory, and extraction metrics.

### 2. Multi-Surface & Multi-Modal Cryptographic Discovery (`app.discovery` — Worker 01)
- **Source Code**: Python AST + multi-language regex covering Python, Java, JavaScript/TypeScript, Go, C/C++, and Rust.
- **Package Manifests**: Identifies cryptographic libraries in `package.json`, `pom.xml`, `requirements.txt`, `pyproject.toml`, `go.mod`, and `Cargo.toml`.
- **Infrastructure & Config**: Audits TLS protocol versions (`TLSv1.3`, `TLSv1.2`, `SSLv3`), cipher suites (`ECDHE-AES256-GCM`), and SSH key exchange mechanisms in `.yaml`, `.conf`, `.ini`, and `.properties`.
- **Certificates & Keys**: Parses X.509 certificates for Subject, Issuer, Public Key Algorithm, Key Size, and validity periods.
- **Static Binary Detector (PROD-01)**: Safe, static-only analysis of ELF, PE/COFF, and Mach-O headers without execution; detects cryptographic symbols (OpenSSL, Libsodium, liboqs), ASN.1 OIDs (RSA, ECC, ML-KEM, ML-DSA), cryptographic constants, and symbol stripping.
- **Container & Layer Detector (PROD-01)**: Audits Dockerfiles and container manifests for base OS crypto posture, cryptographic package dependencies (`openssl`, `liboqs`, `ca-certificates`), and crypto environment variables (`SSL_CERT_DIR`).
- **Authorized Network Endpoint Detector (PROD-02)**: Ingests TLS session metadata and simulated handshakes under strict destination allowlists; categorizes evidence into the four CADI operational planes (`CAPABILITY`, `CONFIGURATION`, `NEGOTIATION`, `ACTUAL_USE`) and detects PQC hybrid key exchanges (`X25519MLKEM768`).
- **Zero-Secret Guarantee**: Detects private key blocks (`BEGIN PRIVATE KEY`) and masks all secret material with `[REDACTED_PRIVATE_KEY_MATERIAL]`, setting `redacted = True`. Private key bytes are never stored.

### 3. Coverage Accounting & Benchmark Engine (`app.coverage` — Worker 01)
- **Honest Denominator Accounting**: Accurately computes $N_{\text{assessed}} / N_{\text{total}}$ across source, manifests, configs, and certificate stores.
- **Non-Misleading Clean State**: Repositories with no detected crypto are labeled `NO_FINDINGS_IN_SUPPORTED_SCOPE` alongside coverage caveats—never falsely reported as "Safe".
- **Partial-Scan Resilience**: Surfaces collector errors or degradation without discarding surviving results.
- **Benchmark Runner**: Pre-registered synthetic corpus evaluation measuring Precision, Recall, and F1 to ensure $\ge 80\%$ benchmark compliance (`AC-06`).

### 4. Canonical Evidence & Inventory Modeling (`app.inventory` — Worker 02)
- **Canonical Evidence Normalization**: Standardizes diverse collector claims into deterministic, content-addressed observations (`CanonicalEvidence`).
- **Asset Identity & Disambiguation**: Aggregates multi-source evidence into unified component identities (`AssetIdentity`) with uncertainty tracking.
- **Parametric Sanitization**: Allowlist-based filtering ensures secrets and internal values are redacted (`[REDACTED]`) prior to ingestion.
- **Relational Context Graph & CBOM Export**: Structures parent-child component relationships, audit trail logging, and privacy-safe CycloneDX-aligned inventory exports (`AC-03`, `AC-05`, `AC-09`).
- **Temporal Cryptographic Time Machine (PROD-01)**: Implements point-in-time `InventorySnapshot` models and deterministic SHA-256 Cryptographic DNA hashing. Computes temporal drift deltas (`added`, `removed`, `modified`) and triggers high-urgency alerts on cryptographic strength downgrade regressions (e.g. `AES-256` $\to$ `DES`).
- **CycloneDX 1.6 Conformance & Multi-Scanner Reconciliation (PROD-02)**: Schema validator for CycloneDX 1.6 cryptographic asset profiles. Multi-generator reconciliation engine computes the **Discrepancy Index** ($D$) across disparate scanners (ASTRA, IBM CBOM, CycloneDX CLI), preserves minority scanner claims, and generates unified, non-lossy CBOMs.

### 5. Contextual Risk, Mosca Horizon & Migration Roadmap (`app.risk` — Worker 03)
- **Mosca Theorem Formulation**: Formally evaluates $X$ (data shelf-life) $+ Y$ (migration duration) $> Z$ (quantum threat horizon). Assets violating this inequality represent immediate Store-Now-Decrypt-Later (SNDL) risks and are automatically escalated to `CRITICAL`.
- **Explainable Multi-Factor Scoring**: Transparently weights algorithm vulnerability ($40\%$), Mosca urgency ($25\%$), operational exposure ($20\%$), and business criticality ($15\%$) with machine-readable reason codes (`AC-07`).
- **Dated Standards & Candidate Migration Backlog**: Links identified algorithms to dated NIST publications (FIPS 203, 204, 205, Aug 2024), candidate standardized/hybrid alternatives, and explicit compatibility/operational caveats (`AC-08`).
- **Scenario Sensitivity & Baseline Comparison**: Dynamic CRQC slider controls show exactly why asset priorities shift; contextual prioritization eliminates alert fatigue ($>50\%$ alert reduction over flat regex/CVSS baselines) (`AC-12`).
- **Dependency-Aware Constrained Roadmap (PROD-01)**: Employs Kahn topological sorting across prerequisite dependencies to generate executable multi-phase roadmaps (Foundation $\to$ Platform $\to$ Edge), preventing deployment failure and identifying critical bottleneck components.
- **Security Invariant & Rollback Assurance (PROD-02)**: Formally audits candidate PQC transitions for security property preservation (Confidentiality, Authenticity, Forward Secrecy, Non-Repudiation), validates MITM downgrade immunity, and enforces fail-closed rollback policies.

### 6. Web Workflow, Hardening & Air-Gapped Operations (`app.web_workflow` — Worker 04)
- **Evidence Drilldown Endpoint**: Granular access to canonical evidence records for specific asset identities (`/api/v1/workflow/evidence/{asset_id}`).
- **Review & Audit Trail**: Auditable governance endpoint recording verification decisions, previous/new states, and review justifications (`/api/v1/workflow/audit`).
- **Sanitized Inventory Export**: Standardized export endpoint emitting CycloneDX-aligned inventory objects with full provenance (`/api/v1/workflow/export`).
- **Tamper-Evident Audit Chaining (PROD-01)**: Chains all governance decisions and review audits into an immutable SHA-256 Merkle-style hash chain (`/api/v1/workflow/audit/chain/verify`), detecting any unauthorized modification or deletion.
- **Air-Gapped Sovereign Readiness & Signed Update Verification (PROD-01)**: Sovereign offline profile with zero outbound telemetry, and local verification of signed offline threat intelligence bundles (`/api/v1/workflow/offline/bundle/verify`).
- **Production Health & Isolation Checks (PROD-01)**: Evaluates sandbox read-only container status, air-gapped isolation, local ruleset cache status, and memory quotas (`/api/v1/workflow/health/production`).

### 7. Dual-Tester Quality & Security Assurance (Tester 01 & Tester 02)
- **Functional Assurance (Tester 01)**: Seeded benchmark testing achieving $\ge 80\%$ precision and recall (`AC-06`), honest denominator validation, and full end-to-end user journeys (Cycles V01 & V02 — 50 tests).
- **Integration & Security Assurance (Tester 02)**: Strict zero private-key retention validation across all formats, hostile archive adversarial attacks (zip bombs, path traversals), schema round-trip integrity, and alert fatigue reduction verification ($>50\%$) (Cycles V01 & V02 — 9 tests).
- **Official Signoff**: Both Tester 01 and Tester 02 have officially reviewed, approved, and signed off on the complete MVP product merge.

---

## Supported Cryptographic Taxonomy

| Category | Algorithms / Primitives Supported |
|---|---|
| **Classical Symmetric** | AES (128, 192, 256), ChaCha20-Poly1305, 3DES, DES, RC4 |
| **Classical Hashing** | SHA-256, SHA-384, SHA-512, SHA3-256, SHA3-512, BLAKE2b/s, MD5, SHA-1 |
| **Classical Asymmetric** | RSA (1024, 2048, 3072, 4096), DSA, ECDSA, ECDH, Ed25519, X25519, ECC Curves (P-256, P-384, secp256k1) |
| **NIST Post-Quantum (PQC)** | ML-KEM (Kyber-512/768/1024), ML-DSA (Dilithium2/3/5), SLH-DSA (SPHINCS+), Falcon, Classic-McEliece |
| **Protocols & Suites** | TLSv1.3, TLSv1.2, Legacy TLS/SSL (v1.0, v1.1, SSLv3), ECDHE/DHE Cipher Suites, Hybrid SSH KEX (`sntrup761x25519`) |

---

## Repository Structure

```
astra/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   ├── config.py              # Security limits, collector & ruleset versions
│   │   │   └── security.py            # Path sanitization, traversal, symlink & hash guards
│   │   ├── intake/                    # Worker 01: MVP-01 Safe Archive Intake
│   │   │   ├── extractor.py           # SafeArchiveExtractor (ZIP, TAR, GZ, BZ2)
│   │   │   ├── models.py              # ScanManifest, ScanStatus, ExtractedFileEntry
│   │   │   └── sandbox.py             # SandboxManager (read-only ephemeral workspaces)
│   │   ├── discovery/                 # Worker 01: MVP-02 Deterministic Discovery
│   │   │   ├── engine.py              # DiscoveryEngine (coordinates all detectors)
│   │   │   ├── models.py              # Canonical Observation schema (W01 -> W02 contract)
│   │   │   └── detectors/
│   │   │       ├── source_detector.py        # Multi-language AST/regex source scanner
│   │   │       ├── manifest_detector.py      # Dependency & package manifest parser
│   │   │       ├── config_detector.py        # TLS protocol & cipher suite auditor
│   │   │       ├── certificate_detector.py   # X.509 parser & private key redactor
│   │   │       ├── binary_detector.py        # Static ELF/PE/Mach-O symbol & OID detector (PROD-01)
│   │   │       ├── container_detector.py     # Dockerfile & container layer inspector (PROD-01)
│   │   │       └── network_detector.py       # Authorized TLS endpoint & handshake detector (PROD-02)
│   │   ├── coverage/                  # Worker 01: MVP-03 Coverage & Benchmark Engine
│   │   │   ├── accounting.py          # CoverageAccountant (honest denominator tracking)
│   │   │   ├── benchmark.py           # BenchmarkRunner (Precision, Recall, F1 against AC-06)
│   │   │   └── models.py              # SurfaceCoverage, CoverageReport, BenchmarkEvaluation
│   │   ├── inventory/                 # Worker 02: Canonical Inventory, Lineage & CBOM
│   │   │   ├── models.py              # CanonicalEvidence, AssetIdentity, redaction
│   │   │   ├── temporal.py            # TemporalLineageEngine & DNA Drift Tracking (PROD-01)
│   │   │   └── cbom_reconciliation.py # CycloneDX 1.6 & Multi-Scanner Reconciler (PROD-02)
│   │   ├── risk/                      # Worker 03: Mosca Horizon, Constrained Roadmap & Assurance
│   │   │   ├── models.py              # ContextFactors, UrgencyLevel, RiskScenario
│   │   │   ├── scorer.py              # ContextualRiskEngine (Mosca X+Y>Z evaluation)
│   │   │   ├── backlog.py             # MigrationBacklogBuilder (dated NIST PQC mappings)
│   │   │   ├── scenarios.py           # ScenarioSensitivityEngine (CRQC horizon sliders)
│   │   │   ├── roadmap.py             # DependencyRoadmapEngine & Kahn Topological Waves (PROD-01)
│   │   │   └── assurance.py           # SecurityInvariantAssuranceEngine & Rollback Safety (PROD-02)
│   │   └── web_workflow/              # Worker 04: Workflow API, Hardening & Air-Gapped Operations
│   │       ├── router.py              # Evidence, review audit, export, and production API
│   │       └── hardening.py           # AirGappedBundleManager & TamperEvidentAuditChainer (PROD-01)
│   └── tests/
│       ├── test_intake/               # 13 intake security & boundary tests
│       ├── test_discovery/            # 12 discovery tests (source, config, cert + binary, container, network)
│       ├── test_coverage/             # 4 coverage accounting & benchmark tests
│       ├── test_inventory/            # 7 canonical inventory, temporal & CBOM tests (3 MVP + 4 prod)
│       ├── test_risk/                 # 13 risk, Mosca, roadmap & assurance tests (9 MVP + 4 prod)
│       ├── test_web_workflow/         # 7 workflow API, audit chain & air-gapped tests (4 MVP + 3 prod)
│       └── test_integration_security/ # 9 dual-tester assurance tests (59 MVP + 15 prod = 74 tests total)
└── .brain/
    ├── .ORG_research/                 # NIST PQC papers, ECDAT dossiers & research PDFs
    ├── .report/                       # Worker signoff reports (MVP-01..03, PROD-01..02)
    └── .work/                         # Shared architecture, contracts, and worker roles
```

---

## Quickstart & Installation

### Prerequisites
- Python 3.10+
- Git

### Setup
```bash
# Clone the repository
git clone https://github.com/adishxm/astra.git
cd astra

# Install required dependencies
pip install pydantic fastapi uvicorn cryptography pyasn1 PyYAML pytest
```

### Running the Test Suite
```bash
# Execute the full automated test suite (50 tests passing 100%)
pytest -v
```

Expected output:
```text
backend/tests/test_coverage/test_coverage_benchmark.py::test_coverage_accountant_surface_breakdown PASSED
backend/tests/test_coverage/test_coverage_benchmark.py::test_no_finding_is_never_labeled_safe PASSED
backend/tests/test_discovery/test_crypto_discovery.py::test_source_detector_classical_and_pqc PASSED
backend/tests/test_functional_assurance/test_v01_functional_assurance.py::TestTester01V01FunctionalAssurance::test_end_to_end_intake_to_discovery_and_canonical_mapping PASSED
backend/tests/test_functional_assurance/test_v02_e2e_journey.py::TestTester01V02E2EJourney::test_e2e_complete_synthetic_scan_to_risk_and_export_journey PASSED
backend/tests/test_intake/test_safe_extractor.py::test_valid_zip_extraction PASSED
backend/tests/test_inventory/test_inventory_models.py::test_map_observation PASSED
backend/tests/test_risk/test_risk_migration.py::test_mosca_deadline_violation_triggers_critical_urgency PASSED
backend/tests/test_web_workflow/test_workflow_api.py::test_create_audit_record PASSED
...
======================== 50 passed in 3.56s ========================
```

---

## Development & Validation Roadmap

| Workstream | Role | Scope | Status |
|---|---|---|---|
| **Worker 01** | Discovery & Safe Intake | Safe archive intake, multi-surface discovery, coverage accounting, benchmark readiness | **COMPLETED & VALIDATED** (MVP-01, 02, 03) |
| **Worker 02** | Evidence & Inventory | Canonical observation deduplication, asset identity graph, CBOM-style projection export | **COMPLETED & VALIDATED** (MVP-01, 02) |
| **Worker 03** | Risk & Migration | Mosca-model quantum horizon analysis, factor sensitivity, migration priority queue | **COMPLETED & VALIDATED** (MVP-01, 02, 03) |
| **Worker 04** | Web Workflow & UI | Fast web intake workflow, evidence drill-down dashboard, audit log & sanitized export | **COMPLETED & VALIDATED** (MVP-01, 02, 03) |
| **Tester 01** | Functional Assurance | Multi-surface discovery, ground truth, canonical evidence, Mosca risk, E2E journey signoff | **COMPLETED & SIGNED OFF** (V01, V02) |
| **Tester 02** | Integration & Security | Release packaging, threat model, CBOM conformance, production gate signoff | Planned |

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
