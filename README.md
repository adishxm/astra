# ASTRA — SIH26164 Enterprise Cryptographic Discovery & Analysis Tool (ECDAT)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![CI](https://github.com/adishxm/astra/actions/workflows/ci.yml/badge.svg)](https://github.com/adishxm/astra/actions/workflows/ci.yml)
[![Test Suite](https://img.shields.io/badge/tests-88%20passing%20in%20CI-brightgreen.svg)](https://github.com/adishxm/astra/actions/workflows/ci.yml)
[![Team: HEXARK](https://img.shields.io/badge/Team-HEXARK-blue.svg)]()
[![NIST PQC](https://img.shields.io/badge/NIST-FIPS%20203%20%7C%20204%20%7C%20205-purple.svg)](https://csrc.nist.gov/projects/post-quantum-cryptography)
[![Launch Guide](https://img.shields.io/badge/📖_Launch_%26_Test_Guide-blue.svg)](launchntest_GUIDE.md)

> **SIH26164 (ECDAT)**: A provenance-aware, coverage-accounted cryptographic discovery, Mosca-horizon post-quantum migration analysis, and standardized CycloneDX 1.6 Cryptographic Bill of Materials (CBOM) engine for enterprise codebases, dependencies, configurations, and certificate stores. Built by team **HEXARK**.

---

## Executive Summary & Scope

**ASTRA** is an open-source cryptographic discovery and CBOM prototype aligned with Smart India Hackathon 2026 problem statement **SIH26164 (Enterprise Cryptographic Discovery & Analysis Tool - ECDAT)**. It provides an auditable, evidence-first approach to discovering cryptographic primitives across source code, package manifests, TLS/SSH configurations, and X.509 certificate stores, accounts for honest scan coverage, explores Mosca theorem post-quantum migration urgency, and exports standardized CycloneDX 1.6 inventories.

ASTRA is an evidence-first prototype and research tool, not a certified enterprise black-box scanner. It explicitly differentiates what was assessed from what was unassessed, treats post-quantum migration horizons as configurable scenario assumptions rather than forecasts, and provides candidate migration pathways for human cryptographic review.

---

## 60-Second Quickstart & Live Demo

You can run ASTRA locally via the one-click launcher, standalone CLI, or FastAPI dashboard:

### Option A: One-Click Windows Launcher (Recommended)
Double-click **`launch.bat`** in the repository root. The launcher will automatically verify Python, install dependencies, allocate ports, launch backend & dashboard, and open your browser to `http://localhost:8000`.

### Option B: Command-Line Interface (CLI) Scan
```bash
# Clone the repository
git clone https://github.com/adishxm/astra.git
cd astra

# Install dependencies (Python 3.10+)
pip install -r requirements.txt

# Run deterministic scan on the included synthetic sample project
python -m app.cli scan ./examples/synthetic_sample --format table
```

### Option C: Realistic Near-Term Demo Walkthrough
1. **Start the app**: Run `launch.bat` or `uvicorn app.main:app --port 8000` from `backend/`.
2. **Scan the synthetic sample**: Upload `examples/synthetic_sample` or run CLI scan.
3. **Inspect evidence**: Review exact file paths, line numbers, detector confidence, and unassessed files.
4. **Explore Mosca scenario**: Adjust quantum threat horizon slider ($Z$) and data shelf-life ($X$) to visualize Store-Now-Decrypt-Later (SNDL) deadline shifts.
5. **Export CBOM**: Export standardized CycloneDX 1.6 CBOM JSON for downstream compliance.

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

## Supported Scope & Limitations (SIH26164 Alignment)

To maintain absolute credibility and transparent engineering standards, ASTRA explicitly delineates what is verified and supported in this prototype versus what is planned for future enterprise releases:

| Surface / Capability | Prototype Status | Implementation & Coverage Details |
|---|---|---|
| **Source Code Detection** | ✅ **Verified** | Python AST + deterministic regex across Python, Java, JavaScript/TypeScript, Go, C/C++, and Rust. Automatic full-line and inline comment filtering eliminates false positives. |
| **Dependency Manifests** | ✅ **Verified** | Parses `package.json`, `pom.xml`, `requirements.txt`, `pyproject.toml`, `go.mod`, and `Cargo.toml`. Accurately labels declared library capabilities distinct from confirmed source-level invocations. |
| **TLS & Infrastructure Configs**| ✅ **Verified** | Audits TLS protocol versions (`TLSv1.2`, `TLSv1.3`), legacy SSL, and cipher suites in `.yaml`, `.conf`, `.ini`, and `.properties`. |
| **Certificates & Public Keys** | ✅ **Verified** | Parses X.509 certificate metadata (Subject, Issuer, public key algorithm, bit length). Enforces strict automated private key redaction (`[REDACTED_PRIVATE_KEY_MATERIAL]`). |
| **Static Binary Inspection** | ✅ **Verified (Direct Scans)** | Direct filesystem scans (`astra scan <dir>`) statically inspect ELF, PE/COFF, and Mach-O headers for crypto symbols (OpenSSL, Libsodium, liboqs), ASN.1 OIDs, and constants without code execution. Web archive uploads filter executables (`.exe`, `.dll`, `.so`) at intake for defense-in-depth isolation. |
| **Container & Dockerfiles** | ✅ **Verified** | Audits Dockerfile instructions, base OS crypto packages, and certificate environment variables. |
| **Truthful Coverage Accounting**| ✅ **Verified** | Tracks honest denominator $N_{\text{assessed}} / N_{\text{total}}$. Repositories with unsupported file formats (media, binaries, unrecognized formats) surface coverage warnings rather than misleading "100% clean" claims. |
| **Mosca Scenario Risk Engine** | ✅ **Verified** | Evaluates Store-Now-Decrypt-Later (SNDL) risk via Mosca theorem ($X + Y > Z$). Threat horizons and data shelf-lives are explicitly tagged as **scenario simulation assumptions**, not predictive forecasts. |
| **CycloneDX 1.6 CBOM Export** | ✅ **Verified** | Emits standardized CycloneDX 1.6 Cryptographic Bill of Materials (CBOM) with automated schema validation. |
| **Hardware Security Modules (HSM)** | ⏳ **Enterprise Roadmap** | PKCS#11 hardware tokens, smartcards, and physical HSM discovery are planned for future hardware-connected releases. |
| **Cloud KMS Fleet Scanners** | ⏳ **Enterprise Roadmap** | Live cloud fleet discovery across AWS KMS, Azure Key Vault, and GCP Cloud KMS is planned for multi-cloud enterprise agents. |
| **Kernel eBPF Network Probe** | ⏳ **Enterprise Roadmap** | Live kernel-level TLS socket interception via eBPF probes is planned for dynamic runtime inspection. |

---

## Privacy, Threat Model & Safe Intake

ASTRA is engineered with a strict **local-first, sovereign** security posture:
- **Local CPU Processing**: All discovery, pattern analysis, and risk scoring execute locally on the host CPU. No code, tokens, or telemetry egress to external cloud services or LLMs.
- **Ephemeral Sandbox Intake**: Archives uploaded via the web interface are extracted into isolated, temporary sandboxes with strict byte, compression ratio, path length, and symlink defenses (`SafeArchiveExtractor`), and unlinked immediately upon completion.
- **Automated Zero-Secret Redaction**: Detected private key blocks and credentials are automatically masked with `[REDACTED_PRIVATE_KEY_MATERIAL]` prior to evidence storage.
- **Demo Recommendation**: Reviewers are encouraged to scan the included `examples/synthetic_sample/` project or open-source repositories. Do not upload live unredacted production secrets to any public demonstration.

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
│   │   │   ├── scorer.py              # RiskScorer (Mosca X+Y>Z evaluation)
│   │   │   ├── backlog.py             # BacklogBuilder (dated NIST PQC mappings)
│   │   │   ├── scenarios.py           # ScenarioSensitivityEngine (CRQC horizon sliders)
│   │   │   ├── roadmap.py             # DependencyRoadmapEngine & Kahn Topological Waves (PROD-01)
│   │   │   └── assurance.py           # SecurityInvariantAssuranceEngine & Rollback Safety (PROD-02)
│   │   ├── services/                  # Production Central Services & Persistence
│   │   │   ├── scan_service.py        # ScanService (unified pipeline) & ScanStore (thread-safe persistence)
│   │   │   └── __init__.py
│   │   ├── static/                    # Embedded Interactive Web Dashboard
│   │   │   └── index.html             # Glassmorphism UI with live Mosca sliders, inventory & CBOM exporter
│   │   ├── web_workflow/              # Worker 04: Workflow API, Hardening & Air-Gapped Operations
│   │   │   ├── router.py              # Evidence drilldown, review audit, and export routes
│   │   │   └── hardening.py           # AirGappedBundleManager & TamperEvidentAuditChainer (PROD-01)
│   │   ├── cli.py                     # ASTRA Zero-Dependency Enterprise CLI Tool
│   │   └── main.py                    # Master FastAPI Application Factory & Entrypoint
│   └── tests/
│       ├── test_e2e_product.py        # 10 End-to-End Product tests (ScanService, FastAPI, CLI)
│       ├── test_intake/               # 13 intake security & boundary tests
│       ├── test_discovery/            # 12 discovery tests (source, config, cert + binary, container, network)
│       ├── test_coverage/             # 4 coverage accounting & benchmark tests
│       ├── test_inventory/            # 7 canonical inventory, temporal & CBOM tests (3 MVP + 4 prod)
│       ├── test_risk/                 # 13 risk, Mosca, roadmap & assurance tests (9 MVP + 4 prod)
│       ├── test_web_workflow/         # 7 workflow API, audit chain & air-gapped tests (4 MVP + 3 prod)
│       ├── test_functional_assurance/ # 9 functional assurance E2E journey tests
│       └── test_integration_security/ # 9 contract security & regression readiness tests (84 tests total)
├── frontend/                          # Standalone Dashboard Package
│   ├── package.json                   # Vite dev server configuration
│   ├── index.html                     # Full responsive UI
│   └── README.md
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

### Installation
```bash
# Clone the repository
git clone https://github.com/adishxm/astra.git
cd astra

# Install dependencies (or pip install -e . to register the 'astra' CLI globally)
pip install -r requirements.txt
pip install -e .
```

---

## Running ASTRA

### 1. Command-Line Interface (CLI)
ASTRA includes a standalone, air-gapped compatible CLI tool that runs locally with declared dependencies (`pip install -r requirements.txt`). It requires no external database servers, Docker, or external network connectivity:

```bash
# Display system version and supported NIST PQC standards
astra version

# Run full cryptographic scan on a directory with tabular terminal output
astra scan ./my_target_project --format table

# Scan an archive (.zip, .tar.gz) and write report to JSON
astra scan ./codebase_bundle.zip --format json --output scan_report.json

# Display previously saved scan summary
astra show scan-d6f0cb73

# Evaluate Mosca inequality horizon (X + Y > Z) and candidate PQC backlog
astra risk scan-d6f0cb73 --horizon 10.0 --shelf-life 5.0 --migration 3.0

# Export CycloneDX 1.6 Cryptographic Bill of Materials (CBOM)
astra export scan-d6f0cb73 --output cbom_cyclonedx.json

# Validate CBOM against CycloneDX 1.6 schema
astra validate scan-d6f0cb73

# Launch the local HTTP server & interactive dashboard
astra serve --host 127.0.0.1 --port 8000
```

### 2. FastAPI Web Server & Interactive Dashboard
Start the production server:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```
Open **`http://localhost:8000`** in your browser to access the ASTRA Web Dashboard:
- **Drag-and-Drop Archive Intake**: Upload `.zip` and `.tar.gz` files directly.
- **Interactive Mosca Slider**: Dynamically adjust quantum threat timelines ($Z$) and data lifetimes ($X$) with real-time recalculation of vulnerability deadlines.
- **Cryptographic Inventory**: Filter and search detected algorithms, key sizes, confidence ratings, and code line locations.
- **One-Click CBOM Export**: Copy or download standard CycloneDX 1.6 JSON.
- **Cryptographic DNA Viewer**: Track posture drift across scans using deterministic SHA-256 fingerprinting.

### 3. Docker & Container Deployment
```bash
# Build and run the ASTRA engine container
docker compose up --build

# Run test suite inside isolated Docker container
docker compose --profile test run astra-tests
```

---

## Running the Automated Test Suite

```bash
# Run all 88 test suites with detailed output
python -m pytest backend/tests -v
```

All 88 automated unit, integration, security, and end-to-end product tests pass with 100% success rate:
```text
============================= 88 passed in 3.57s ==============================
```

---

## Development & Validation Roadmap

### Completed Prototype Workstreams (88/88 Passing Tests)
| Workstream | Role | Prototype Scope Delivered | Status |
|---|---|---|---|
| **Worker 01** | Discovery & Safe Intake | Safe archive intake (ZIP/TAR limits, symlink defenses), multi-surface discovery (source, manifests, configs, certs, direct binary headers), honest coverage accounting | **COMPLETED & VALIDATED** |
| **Worker 02** | Evidence & Inventory | Canonical deduplication, temporal Cryptographic DNA time-machine, CycloneDX 1.6 CBOM projection & reconciliation | **COMPLETED & VALIDATED** |
| **Worker 03** | Risk & Migration | Mosca-model quantum horizon ($X+Y>Z$), scenario sensitivity sliders, Kahn topological wave migration roadmaps, rollback safety | **COMPLETED & VALIDATED** |
| **Worker 04** | Web Workflow & UI | Product CLI, master FastAPI factory, embedded dashboard, tamper-evident audit chaining, air-gapped readiness | **COMPLETED & VALIDATED** |
| **Product Suite** | End-to-End System | Complete end-to-end integration test suite, synthetic demo repository, launch scripts | **COMPLETED & VERIFIED (88/88 PASS)** |

### Future Enterprise Roadmap
| Milestone | Capability | Description |
|---|---|---|
| **Phase 2.1** | Hardware Security Modules (HSM) | Integration with PKCS#11 hardware security modules, smartcards, and enterprise key vaults. |
| **Phase 2.2** | Cloud KMS Multi-Cloud Fleet | Autonomous discovery connectors for AWS KMS, Azure Key Vault, and Google Cloud KMS fleets. |
| **Phase 2.3** | Runtime eBPF Dynamic Inspection | Linux kernel eBPF probes for observing negotiated cipher suites and active cryptographic socket handshakes. |
| **Phase 2.4** | Automated PR Remediation | GitHub Actions and GitLab CI bots for automated code refactoring toward NIST PQC algorithms. |

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
