# Changelog

All notable changes to the **ASTRA** (Enterprise Cryptographic Discovery & Analysis Tool - SIH26164) prototype will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-10-03 (SIH26164 Prototype Release)

Built by Team **HEXARK** for Smart India Hackathon 2026 (Problem Statement: SIH26164 ECDAT).

### Added
- **Adversarial-Resistant Intake (`app.intake`)**:
  - Magic byte verification for ZIP, TAR, TAR.GZ, and TAR.BZ2 archives.
  - Streaming byte counters preventing zip bombs ($100:1$ compression ratio limit, $500\text{ MB}$ total expansion, $50\text{ MB}$ single-file limit).
  - Path traversal and null-byte defenses (`sanitize_relative_path`, `verify_sandbox_containment`).
  - Symlink escape and hard link rejections (`SymlinkEscapeError`).
  - Ephemeral sandbox workspaces unlinked immediately upon completion.
- **Deterministic Cryptographic Discovery (`app.discovery`)**:
  - Python AST scanner for confirmed imports (`hashlib`, `cryptography`, `Crypto`).
  - Universal multi-language source scanner (Python, Java, JS/TS, Go, C/C++, Rust).
  - Comment and docstring filtering (`strip_line_comments`, block comments, triple-quote docstrings) eliminating false-positive matches.
  - Manifest parsers for `package.json`, `pom.xml`, `requirements.txt`, `pyproject.toml`, `go.mod`, `Cargo.toml`.
  - TLS/SSH configuration inspectors (.yaml, .conf, .ini, .properties).
  - X.509 certificate parser extracting Subject, Issuer, Public Key Algorithm, and validity dates.
  - Static binary header detector (ELF, PE, Mach-O) for crypto symbols, ASN.1 OIDs, and constants in direct filesystem scans.
  - Automated private key redaction masking secrets with `[REDACTED_PRIVATE_KEY_MATERIAL]`.
- **Honest Coverage Accounting (`app.coverage`)**:
  - Truthful denominator tracking ($N_{\text{assessed}} / N_{\text{total}}$).
  - Non-misleading clean state: Repositories with no findings are labeled `NO_FINDINGS_IN_SUPPORTED_SCOPE` alongside coverage caveats—never falsely reported as "Safe".
- **Canonical Inventory & CBOM Projection (`app.inventory`)**:
  - Content-addressed `CanonicalEvidence` and `AssetIdentity` aggregation.
  - Temporal Cryptographic DNA hashing (`InventorySnapshot`) and regression downgrade detection.
  - Standardized CycloneDX 1.6 Cryptographic Bill of Materials (CBOM) export and schema validation.
  - Multi-scanner reconciliation engine computing Discrepancy Index ($D$) across ASTRA, IBM CBOM, and CycloneDX CLI.
- **Explainable Mosca Risk & Candidate PQC Backlog (`app.risk`)**:
  - Mosca inequality evaluation: $X$ (data shelf-life) $+ Y$ (migration duration) $> Z$ (quantum threat horizon).
  - Store-Now-Decrypt-Later (SNDL) deadline violation flagging with slack calculation ($Z - (X + Y)$).
  - Scenario simulation assumptions with dynamic re-evaluation sliders via CLI and REST API.
  - Candidate PQC alternative mappings citing dated NIST standards (FIPS 203 ML-KEM, FIPS 204 ML-DSA, FIPS 205 SLH-DSA).
  - Kahn topological wave roadmaps preventing cyclic deadlocks during phased migration.
- **Zero-Dependency CLI & FastAPI Web App**:
  - Standalone CLI (`astra version`, `astra scan`, `astra show`, `astra risk`, `astra export`, `astra validate`, `astra serve`).
  - FastAPI server with air-gapped health probes, REST API, and static glassmorphism Web Dashboard.
  - Windows one-click launcher (`launch.bat`) with ASCII art banner, health polling, and automatic browser opening.
- **Reference Synthetic Fixture (`examples/synthetic_sample/`)**:
  - Multi-surface demo repo with known RSA, AES, ML-KEM, MD5, TLS, X.509 cert, and unsupported media file.
  - Published example CycloneDX 1.6 CBOM export (`examples/sample_cbom_cyclonedx_1.6.json`).

### Security Boundaries
- **CORS Restricted**: Credentials disabled on wildcard `*` origins; configurable via `ASTRA_CORS_ORIGINS`.
- **Upload Boundary**: 100 MB active streaming threshold before disk allocation; filename normalization.
- **Hosted Mode Boundary**: Direct filesystem directory scans disabled when `ASTRA_HOSTED_MODE=true` to prevent arbitrary server traversal.
- **Local-First / Zero Telemetry**: All analysis runs locally on host CPU without network egress.

### Verified Test Evidence
- **88 automated tests** passing in CI across unit, integration, adversarial security, and end-to-end user journeys:
  - 13 archive intake security & boundary tests
  - 15 multi-surface discovery tests (including comment filtering)
  - 4 coverage accounting tests
  - 7 canonical inventory, temporal & CBOM tests
  - 13 risk, Mosca, roadmap & assurance tests
  - 7 workflow API, audit chain & air-gapped tests
  - 9 functional assurance E2E journey tests
  - 9 contract security & regression readiness tests
  - 10 end-to-end product CLI & FastAPI tests

### Known Limitations & Future Enterprise Scope
- **Hardware Security Modules (HSM)**: Physical PKCS#11 tokens and enterprise HSM appliances are out of current prototype scope (planned for Phase 2.1).
- **Cloud KMS Fleet Discovery**: Multi-cloud live key discovery across AWS KMS, Azure Key Vault, and GCP Cloud KMS is planned for Phase 2.2.
- **Kernel eBPF Dynamic Inspection**: Runtime socket capture via Linux eBPF probes is planned for Phase 2.3.
- **Web Archive Intake of Binaries**: Executables (`.exe`, `.dll`, `.so`) are blocked at archive intake for defense-in-depth isolation; static binary analysis is supported in direct filesystem directory scans.
