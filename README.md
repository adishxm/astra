# ASTRA — Enterprise Cryptographic Discovery & Analysis Tool (ECDAT)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Test Suite](https://img.shields.io/badge/tests-37%20passed%20%7C%20100%25-brightgreen.svg)]()
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
└──────────────────┘             └──────────────────┘             └──────────────────┘
```

---

## Core Capabilities (Worker 01 — Completed)

### 1. Safe Intake & Scan Boundary (`app.intake`)
- **Container Format Verification**: Inspects file magic bytes (ZIP, GZIP, BZIP2, TAR) to prevent extension spoofing.
- **Decompression Bomb Protection**: Active streaming byte counters enforce maximum compression ratios ($100:1$), total uncompressed sizes ($500\text{ MB}$), and single-file thresholds ($50\text{ MB}$).
- **Directory Traversal Prevention**: Strips leading slashes, blocks parent directory backtracking (`../`), null bytes (`\0`), and drive specifiers.
- **Symlink & Dangerous File Guards**: Rejects symlink/hardlink escapes (`SymlinkEscapeError`) and safely skips dangerous executables (`.exe`, `.dll`, `.so`, `.ps1`).
- **Reproducible Manifest**: Emits `ScanManifest` containing archive SHA-256, scan ID (UUIDv4), file inventory, and extraction metrics.

### 2. Multi-Surface Cryptographic Discovery (`app.discovery`)
- **Source Code**: Python AST + multi-language regex covering Python, Java, JavaScript/TypeScript, Go, C/C++, and Rust.
- **Package Manifests**: Identifies cryptographic libraries in `package.json`, `pom.xml`, `requirements.txt`, `pyproject.toml`, `go.mod`, and `Cargo.toml`.
- **Infrastructure & Config**: Audits TLS protocol versions (`TLSv1.3`, `TLSv1.2`, `SSLv3`), cipher suites (`ECDHE-AES256-GCM`), and SSH key exchange mechanisms in `.yaml`, `.conf`, `.ini`, and `.properties`.
- **Certificates & Keys**: Parses X.509 certificates for Subject, Issuer, Public Key Algorithm, Key Size, and validity periods.
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

### 5. Contextual Risk & Mosca Horizon Engine (`app.risk` — Worker 03)
- **Mosca Theorem Formulation**: Formally evaluates $X$ (data shelf-life) $+ Y$ (migration duration) $> Z$ (quantum threat horizon). Assets violating this inequality represent immediate Store-Now-Decrypt-Later (SNDL) risks and are automatically escalated to `CRITICAL`.
- **Explainable Multi-Factor Scoring**: Transparently weights algorithm vulnerability ($40\%$), Mosca urgency ($25\%$), operational exposure ($20\%$), and business criticality ($15\%$) with machine-readable reason codes (`AC-07`).
- **Dated Standards & Candidate Migration Backlog**: Links identified algorithms to dated NIST publications (FIPS 203, 204, 205, Aug 2024), candidate standardized/hybrid alternatives, and explicit compatibility/operational caveats (`AC-08`).
- **Scenario Sensitivity & Baseline Comparison**: Dynamic CRQC slider controls show exactly why asset priorities shift; contextual prioritization eliminates alert fatigue ($>50\%$ alert reduction over flat regex/CVSS baselines) (`AC-12`).

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
│   │   │       └── certificate_detector.py   # X.509 parser & private key redactor
│   │   └── coverage/                  # Worker 01: MVP-03 Coverage & Benchmark Engine
│   │       ├── accounting.py          # CoverageAccountant (honest denominator tracking)
│   │       ├── benchmark.py           # BenchmarkRunner (Precision, Recall, F1 against AC-06)
│   │       └── models.py              # SurfaceCoverage, CoverageReport, BenchmarkEvaluation
│   └── tests/
│       ├── test_intake/               # 13 intake security & boundary tests
│       ├── test_discovery/            # 8 cryptographic discovery & redaction tests
│       └── test_coverage/             # 4 coverage accounting & benchmark tests
└── .brain/
    ├── .ORG_research/                 # NIST PQC papers, ECDAT dossiers & research PDFs
    ├── .report/                       # Worker 01 MVP-01, MVP-02, MVP-03 signoff reports
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
# Execute the full automated test suite (25 tests)
python -m pytest -v -p no:cacheprovider -o pythonpath=backend backend/tests
```

Expected output:
```text
backend/tests/test_coverage/test_coverage_benchmark.py::test_coverage_accountant_surface_breakdown PASSED
backend/tests/test_coverage/test_coverage_benchmark.py::test_no_finding_is_never_labeled_safe PASSED
backend/tests/test_coverage/test_coverage_benchmark.py::test_partial_scan_on_detector_failure PASSED
backend/tests/test_coverage/test_coverage_benchmark.py::test_benchmark_runner_seeded_corpus_target PASSED
backend/tests/test_discovery/test_crypto_discovery.py::test_source_detector_classical_and_pqc PASSED
backend/tests/test_discovery/test_crypto_discovery.py::test_certificate_detector_private_key_redaction PASSED
backend/tests/test_discovery/test_crypto_discovery.py::test_discovery_engine_end_to_end PASSED
backend/tests/test_intake/test_safe_extractor.py::test_valid_zip_extraction PASSED
backend/tests/test_intake/test_safe_extractor.py::test_zip_bomb_compression_ratio_defense PASSED
backend/tests/test_intake/test_safe_extractor.py::test_path_traversal_zip_rejection PASSED
backend/tests/test_intake/test_safe_extractor.py::test_symlink_rejection_in_tar PASSED
...
============================= 25 passed in 1.30s ==============================
```

---

## Development Roadmap

| Worker | Role | Scope | Status |
|---|---|---|---|
| **Worker 01** | Discovery & Safe Intake | Safe archive intake, multi-surface discovery, coverage accounting, benchmark readiness | **COMPLETED** (MVP-01, 02, 03) |
| **Worker 02** | Evidence & Inventory | Canonical observation deduplication, asset identity graph, CycloneDX 1.6 CBOM projection | In Progress |
| **Worker 03** | Risk & Migration | Mosca-model quantum horizon analysis, factor sensitivity, migration priority queue | Planned |
| **Worker 04** | Web Workflow & UI | Fast web intake workflow, evidence drill-down dashboard, audit log & sanitized export | Planned |

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
