# ASTRA — Algorithm Security Tracking and Risk Assessment
### SIH26164 Enterprise Cryptographic Discovery & Analysis Tool (ECDAT)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![CI](https://github.com/adishxm/astra/actions/workflows/ci.yml/badge.svg)](https://github.com/adishxm/astra/actions/workflows/ci.yml)
[![Backend Tests](https://img.shields.io/badge/backend%20tests-88%20passing-brightgreen.svg)](https://github.com/adishxm/astra/actions/workflows/ci.yml)
[![Frontend Tests](https://img.shields.io/badge/frontend%20tests-192%20passing-brightgreen.svg)](https://github.com/adishxm/astra/actions/workflows/ci.yml)
[![3D Visualization](https://img.shields.io/badge/3D%20Engine-Mosca%20Parameter%20Space-orange.svg)]()
[![Team: HEXARK](https://img.shields.io/badge/Team-HEXARK-blue.svg)]()
[![NIST PQC](https://img.shields.io/badge/NIST-FIPS%20203%20%7C%20204%20%7C%20205-purple.svg)](https://csrc.nist.gov/projects/post-quantum-cryptography)
[![CycloneDX CBOM](https://img.shields.io/badge/CycloneDX-1.6%20CBOM-orange.svg)](https://cyclonedx.org/)
[![Profile: Sovereign](https://img.shields.io/badge/Profile-Air--Gapped%20Sovereign-red.svg)]()

> **ASTRA by Team HEXARK is an open-source cryptographic discovery and CBOM prototype aligned with SIH26164 (ECDAT). Scan source, manifests, configs and certificates, evaluate Mosca PQC migration risk, and export CycloneDX 1.6 CBOM.**

---

## Table of Contents

1. [Executive Summary & Problem Alignment](#executive-summary--problem-alignment)
2. [Supported Scope & Limitations (SIH26164 Matrix)](#supported-scope--limitations-sih26164-matrix)
3. [60-Second Quickstart & Launch Options](#60-second-quickstart--launch-options)
   - [Option A: One-Click Windows Launcher (`launch.bat`)](#option-a-one-click-windows-launcher-launchbat-recommended)
   - [Option B: Zero-Dependency CLI Scan](#option-b-zero-dependency-cli-scan)
   - [Option C: FastAPI Web Server & Interactive Dashboard](#option-c-fastapi-web-server--interactive-dashboard)
   - [Option D: Docker Deployment](#option-d-docker-deployment)
   - [Option E: Synthetic Near-Term Demo Walkthrough](#option-e-synthetic-near-term-demo-walkthrough)
4. [System Architecture & Multi-Worker Pipeline](#system-architecture--multi-worker-pipeline)
5. [Complete Audit Workflow — Step-by-Step](#complete-audit-workflow--step-by-step)
   - [Step 1: Initiate a Scan](#step-1-initiate-a-scan)
   - [Step 2: Review Results & Clean State Labeling](#step-2-review-results--clean-state-labeling)
   - [Step 3: Mosca Horizon & Risk Sensitivity Analysis](#step-3-mosca-horizon--risk-sensitivity-analysis)
   - [Step 4: Export CycloneDX 1.6 CBOM](#step-4-export-cyclonedx-16-cbom)
   - [Step 5: Validate CBOM Schema Compliance](#step-5-validate-cbom-schema-compliance)
6. [Interactive Web Dashboard — Real-Time Features](#interactive-web-dashboard--real-time-features)
   - [Drag-and-Drop Archive Intake](#drag-and-drop-archive-intake)
   - [Interactive Mosca Slider ($Z$, $X$, $Y$)](#interactive-mosca-slider)
   - [3D Parameter Space Visualizer ($X \times Y \times Z$)](#3d-parameter-space-visualizer-x--y--z)
   - [Cryptographic Inventory Browser](#cryptographic-inventory-browser)
   - [Cryptographic DNA Viewer & Drift Regression Alerts](#cryptographic-dna-viewer--drift-regression-alerts)
   - [One-Click CBOM Export & Copy](#one-click-cbom-export--copy)
7. [Comprehensive REST API Reference](#comprehensive-rest-api-reference)
   - [Core Scan Endpoints](#core-scan-endpoints)
   - [Workflow & Governance Endpoints](#workflow--governance-endpoints)
   - [System & Health Probes](#system--health-probes)
8. [Production & Air-Gapped Sovereign Operations](#production--air-gapped-sovereign-operations)
   - [Tamper-Evident SHA-256 Audit Chain](#tamper-evident-sha-256-audit-chain)
   - [Air-Gapped Signed Update Bundle Verification](#air-gapped-signed-update-bundle-verification)
   - [Production Readiness Health Evaluation](#production-readiness-health-evaluation)
9. [Environment Configuration](#environment-configuration)
10. [Automated Test Suite (88 Passing Tests)](#automated-test-suite-88-passing-tests)
11. [Troubleshooting & FAQ](#troubleshooting--faq)
12. [Privacy, Threat Model & Security Considerations](#privacy-threat-model--security-considerations)
13. [Quick Reference Card](#quick-reference-card)
14. [Development Roadmap (Phase 2 Enterprise)](#development-roadmap-phase-2-enterprise)
15. [License & Credits](#license--credits)

---

## Executive Summary & Problem Alignment

**ASTRA** (**A**lgorithm **S**ecurity **T**racking and **R**isk **A**ssessment) is an open-source cryptographic discovery and CBOM prototype engineered by **Team HEXARK** for Smart India Hackathon 2026 problem statement **SIH26164 (Enterprise Cryptographic Discovery & Analysis Tool - ECDAT)**.

Modern enterprise systems are exposed to the **Store-Now-Decrypt-Later (SNDL)** threat: adversarial actors intercept and record encrypted network traffic and proprietary data today, preparing to decrypt it once Cryptographically Relevant Quantum Computers (CRQCs) emerge. Transitioning to Post-Quantum Cryptography (PQC) requires knowing **where**, **how**, and **what** cryptographic algorithms are employed across codebases, manifests, configs, and certificates.

ASTRA addresses this challenge with:
- **Evidence-First Discovery**: Pinpoints exact file paths, line numbers, and code contexts for cryptographic primitives across 6 programming languages, package manifests, TLS/SSH configurations, and X.509 certificates.
- **Truthful Denominator Coverage**: Tracks assessed versus unassessed files ($N_{\text{assessed}} / N_{\text{total}}$), preventing false senses of security when unsupported file formats are present.
- **Explainable Mosca Theorem Risk Scorer**: Models the Mosca inequality ($X + Y > Z$) with dynamic scenario sensitivity sliders to calculate exact Store-Now-Decrypt-Later vulnerability deadlines.
- **Standardized CycloneDX 1.6 CBOM**: Produces validated, compliant Cryptographic Bill of Materials with multi-scanner reconciliation.
- **Sovereign, Air-Gapped Architecture**: Operates 100% locally on CPU with zero telemetry, streaming zip-bomb defenses, automated private key redaction, and an immutable SHA-256 Merkle-style audit log.

---

## Supported Scope & Limitations (SIH26164 Matrix)

To maintain absolute credibility and transparent engineering standards, ASTRA explicitly delineates what is verified and supported in this prototype versus what is planned for future enterprise releases:

| Surface / Capability | Prototype Status | Implementation & Coverage Details |
|---|---|---|
| **Source Code Detection** | ✅ **Verified** | Python AST + multi-language regex across Python, Java, JavaScript/TypeScript, Go, C/C++, and Rust. Automatic full-line and inline comment filtering eliminates false positives. |
| **Dependency Manifests** | ✅ **Verified** | Parses `package.json`, `pom.xml`, `requirements.txt`, `pyproject.toml`, `go.mod`, and `Cargo.toml`. Accurately labels declared library capabilities distinct from confirmed source-level invocations. |
| **TLS & Infrastructure Configs**| ✅ **Verified** | Audits TLS protocol versions (`TLSv1.2`, `TLSv1.3`), legacy SSL (`SSLv3`, `TLSv1.0`), and cipher suites in `.yaml`, `.conf`, `.ini`, and `.properties`. |
| **Certificates & Public Keys** | ✅ **Verified** | Parses X.509 certificate metadata (Subject, Issuer, public key algorithm, bit length, validity). Enforces strict automated private key redaction (`[REDACTED_PRIVATE_KEY_MATERIAL]`). |
| **Static Binary Inspection** | ✅ **Verified (Direct Scans)** | Direct filesystem scans (`astra scan <dir>`) statically inspect ELF, PE/COFF, and Mach-O headers for crypto symbols (OpenSSL, Libsodium, liboqs), ASN.1 OIDs, and constants without code execution. Web archive uploads filter executables (`.exe`, `.dll`, `.so`) at intake for defense-in-depth isolation. |
| **Container & Dockerfiles** | ✅ **Verified** | Audits Dockerfile instructions, base OS crypto packages, and certificate environment variables. |
| **Truthful Coverage Accounting**| ✅ **Verified** | Tracks honest denominator $N_{\text{assessed}} / N_{\text{total}}$. Repositories with unsupported file formats (media, binaries, unrecognized formats) surface coverage warnings rather than misleading "100% clean" claims. |
| **Mosca Scenario Risk Engine** | ✅ **Verified** | Evaluates Store-Now-Decrypt-Later (SNDL) risk via Mosca theorem ($X + Y > Z$). Threat horizons and data shelf-lives are explicitly tagged as **scenario simulation assumptions**, not predictive forecasts. |
| **CycloneDX 1.6 CBOM Export** | ✅ **Verified** | Emits standardized CycloneDX 1.6 Cryptographic Bill of Materials (CBOM) with automated schema validation. |
| **Hardware Security Modules (HSM)** | ⏳ **Enterprise Roadmap** | PKCS#11 hardware tokens, smartcards, and physical HSM discovery are planned for future hardware-connected releases. |
| **Cloud KMS Fleet Scanners** | ⏳ **Enterprise Roadmap** | Live cloud fleet discovery across AWS KMS, Azure Key Vault, and GCP Cloud KMS is planned for multi-cloud enterprise agents. |
| **Kernel eBPF Network Probe** | ⏳ **Enterprise Roadmap** | Live kernel-level TLS socket interception via eBPF probes is planned for dynamic runtime inspection. |

---

## 60-Second Quickstart & Launch Options

### Option A: One-Click Windows Launcher (`launch.bat`) (Recommended)

Double-click **`launch.bat`** in the repository root (or run it from PowerShell/CMD):
```cmd
launch.bat
```
The launcher will automatically:
1. Verify Python 3.10+ installation.
2. Check and allocate local port 8000.
3. Automatically install all required dependencies from `requirements.txt`.
4. Launch the FastAPI backend and embedded Web Dashboard.
5. Poll `/health` until live, then automatically launch your default browser to `http://localhost:8000`.

---

### Option B: Zero-Dependency CLI Scan

ASTRA includes a standalone, air-gapped compatible CLI tool that runs locally with declared dependencies:

```bash
# 1. Clone the repository
git clone https://github.com/adishxm/astra.git
cd astra

# 2. Install dependencies & register CLI globally
pip install -r requirements.txt
pip install -e .

# 3. Verify CLI installation
astra version

# 4. Scan a target project directory
astra scan ./examples/synthetic_sample --format table
```

---

### Option C: FastAPI Web Server & Interactive Dashboard

```bash
# Launch server directly via Uvicorn
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Or launch via the global CLI
astra serve --host 127.0.0.1 --port 8000
```
Open **`http://localhost:8000`** in your browser. Interactive OpenAPI documentation is available at **`http://localhost:8000/docs`**.

---

### Option D: Docker Deployment

```bash
# Build and run the containerized ASTRA engine
docker compose up --build

# Run in background (detached) mode
docker compose up -d --build

# Execute test suite inside the container
docker compose --profile test run astra-tests
```
The Docker container executes as an unprivileged user `astra` (UID 1000) with volume persistence at `./data`.

---

### Option E: Synthetic Near-Term Demo Walkthrough

ASTRA includes a pre-built reference multi-surface test project in [`examples/synthetic_sample/`](examples/synthetic_sample/):
```bash
# 1. Scan the synthetic sample
astra scan ./examples/synthetic_sample --format table

# 2. Re-evaluate Mosca risk with custom scenario parameters
astra risk scan-<id> --horizon 8.0 --shelf-life 5.0 --migration 2.0

# 3. Export validated CycloneDX 1.6 CBOM
astra export scan-<id> --output cbom.json

# 4. Validate schema compliance
astra validate scan-<id>
```

---

## System Architecture & Multi-Worker Pipeline

ASTRA is built upon an asynchronous, decoupled multi-worker architecture designed for modularity, defensibility, and zero secret retention:

```mermaid
flowchart TD
    %% Input Layer
    subgraph IntakeSources["1. Target Intake Surfaces"]
        direction LR
        Archive["Authorized Archive<br/>(.zip, .tar, .tar.gz, .tar.bz2)"]
        DirScan["Local Codebase / Directory<br/>(Bare-Metal CLI / CI Runner)"]
    end

    %% Worker 01
    subgraph W01["Worker 01: Safe Intake, Discovery & Coverage Engine"]
        direction TB
        subgraph W01_Intake["Safe Intake & Sandbox Containment (app.intake)"]
            MagicCheck["Magic Byte Format Verification"]
            ZipBombDef["Zip Bomb & Streaming Quotas (100:1 Ratio, 500MB Cap)"]
            Sandbox["Ephemeral Read-Only Sandbox Workspace"]
            MagicCheck --> ZipBombDef --> Sandbox
        end

        subgraph W01_Discovery["Multi-Surface Cryptographic Discovery (app.discovery)"]
            ASTScan["Source Code Scanner (Python AST + Multi-Lang Regex)<br/>Comment & Docstring Stripping"]
            ManifestScan["Dependency Manifests<br/>(package.json, pom.xml, requirements.txt, go.mod, Cargo.toml)"]
            ConfigScan["TLS & SSH Configs (.yaml, .conf, .ini)"]
            CertScan["X.509 Certificates & Public Key Metadata"]
            BinaryScan["Static Binary Headers (ELF, PE, Mach-O Symbols & OIDs)"]
            ContainerScan["Dockerfiles & Container Posture"]
            Redactor["Automated Private Key Redaction [REDACTED_PRIVATE_KEY_MATERIAL]"]
        end

        subgraph W01_Coverage["Truthful Coverage Accounting (app.coverage)"]
            CoverageCalc["Honest Denominator: N_assessed / N_total"]
            CleanState["Clean State Guard: NO_FINDINGS_IN_SUPPORTED_SCOPE"]
        end

        Sandbox --> W01_Discovery
        W01_Discovery --> Redactor
        Redactor --> W01_Coverage
    end

    Archive --> MagicCheck
    DirScan --> W01_Discovery

    %% Worker 02
    subgraph W02["Worker 02: Canonical Evidence & CBOM Engine (app.inventory)"]
        Norm["Canonical Evidence Normalization & Deduplication"]
        DNA["Temporal Cryptographic DNA Hashing (SHA-256)"]
        Drift["Cryptographic Drift & Downgrade Regression Detection"]
        CBOMGen["CycloneDX 1.6 CBOM Projection & Schema Validator"]
        Recon["Multi-Scanner Reconciliation (Discrepancy Index D)"]

        Norm --> DNA --> Drift
        Norm --> CBOMGen --> Recon
    end

    %% Worker 03
    subgraph W03["Worker 03: Mosca Risk & Migration Roadmap (app.risk)"]
        MoscaCalc["Mosca Inequality Evaluator: X + Y > Z<br/>(Shelf-Life + Migration vs. Threat Horizon)"]
        SNDLAlert["Store-Now-Decrypt-Later (SNDL) Deadline & Slack Calculation"]
        MultiFactor["Multi-Factor Scoring (Vulnerability 40%, Mosca 25%, Exposure 20%, Criticality 15%)"]
        PQCMapping["Candidate NIST PQC Backlog (FIPS 203 ML-KEM, 204 ML-DSA, 205 SLH-DSA)"]
        KahnRoadmap["Kahn Topological Sorting Migration Waves (Foundation -> Platform -> Edge)"]

        MoscaCalc --> SNDLAlert --> MultiFactor
        MultiFactor --> PQCMapping --> KahnRoadmap
    end

    %% Worker 04
    subgraph W04["Worker 04: Delivery, Web UI & Air-Gapped Governance (app.web_workflow)"]
        FastAPI["FastAPI Master Application & REST API (/api/v1/scans)"]
        Dashboard["Interactive Web Dashboard (Real-Time Mosca Slider & DNA Viewer)"]
        CLI["Zero-Dependency CLI Tool (astra scan / risk / export / validate)"]
        AuditChain["Tamper-Evident SHA-256 Merkle Audit Chain"]
        AirGap["Air-Gapped Sovereign Profile & Signed Bundle Verification"]

        FastAPI --> Dashboard
        FastAPI --> AuditChain
        FastAPI --> AirGap
    end

    %% Inter-worker data flows
    W01_Coverage -->|"Canonical Observations"| W02
    W01_Coverage -->|"Cryptographic Assets"| W03
    W02 -->|"Validated CycloneDX 1.6 CBOM"| W04
    W03 -->|"PQC Migration Roadmap & Risk Scores"| W04
```

### Worker Roles & Responsibilities

- **Worker 01 (`app.intake`, `app.discovery`, `app.coverage`)**: Ingests archives with strict zip-bomb and symlink containment; runs multi-surface static detectors; computes honest coverage denominator ($N_{\text{assessed}} / N_{\text{total}}$).
- **Worker 02 (`app.inventory`)**: Normalizes observations into content-addressed `CanonicalEvidence`; tracks temporal posture drift with SHA-256 Cryptographic DNA hashes; projects CycloneDX 1.6 CBOM with multi-scanner reconciliation.
- **Worker 03 (`app.risk`)**: Evaluates Mosca inequality ($X + Y > Z$); calculates Store-Now-Decrypt-Later urgency; maps candidate PQC algorithms (NIST FIPS 203/204/205); computes Kahn topological roadmaps.
- **Worker 04 (`app.web_workflow`)**: Powers FastAPI endpoints, embedded glassmorphism Web Dashboard, immutable SHA-256 Merkle-style audit chains, and air-gapped signed bundle verification.

---

## Complete Audit Workflow — Step-by-Step

### Step 1: Initiate a Scan

You can initiate scans through multiple entrypoints:

**Option A: CLI — Scan Directory**
```bash
astra scan ./my_target_project --format table
```

**Option B: CLI — Scan Archive with JSON Output**
```bash
astra scan ./codebase.zip --format json --output scan_report.json
```

**Option C: REST API — Upload Archive**
```bash
curl -X POST http://localhost:8000/api/v1/scans/upload \
  -F "file=@./codebase.zip"
```

**Option D: REST API — Scan Server Directory**
```bash
curl -X POST http://localhost:8000/api/v1/scans/directory \
  -H "Content-Type: application/json" \
  -d '{"path": "/absolute/path/to/project", "target_name": "my-project"}'
```

**Option E: Web Dashboard**
Open `http://localhost:8000` and drag-and-drop your `.zip` or `.tar.gz` file into the upload zone.

---

### Step 2: Review Results & Clean State Labeling

ASTRA enforces a strict **non-misleading clean state invariant**: repositories with no detected cryptography are labeled `NO_FINDINGS_IN_SUPPORTED_SCOPE` alongside coverage caveats—**never** falsely marked as "Safe".

**CLI Inspection:**
```bash
astra show scan-d6f0cb73
```
Output:
```text
Scan ID:             scan-d6f0cb73
Target:              codebase_bundle.zip
Created At:          2026-10-03T12:00:00+00:00
Coverage:            87.5% (7/8 files assessed)
Clean State Label:   FINDINGS_PRESENT
Cryptographic DNA:   a1b2c3d4e5f6...
```

**REST API Inspection:**
```bash
# Retrieve full scan record
curl http://localhost:8000/api/v1/scans/scan-d6f0cb73

# Retrieve honest coverage accounting report
curl http://localhost:8000/api/v1/scans/scan-d6f0cb73/coverage
```

---

### Step 3: Mosca Horizon & Risk Sensitivity Analysis

The **Mosca Theorem** formally models post-quantum migration urgency:

$$\text{If } X + Y > Z \implies \text{CRITICAL Store-Now-Decrypt-Later (SNDL) Deadline Violation}$$

Where:
- $X$ = **Data Secrecy Shelf-Life** (years the data must remain confidential).
- $Y$ = **Migration Duration** (years required to transition systems to PQC).
- $Z$ = **Quantum Threat Horizon** (years until Cryptographically Relevant Quantum Computers exist).
- $\text{Slack} = Z - (X + Y)$. Negative slack indicates an immediate violation.

**CLI Dynamic Re-Evaluation:**
```bash
astra risk scan-d6f0cb73 --horizon 8.0 --shelf-life 5.0 --migration 2.0
```
Output:
```text
[*] Risk & Mosca Horizon Analysis for Scan: scan-d6f0cb73
Active Scenario: Quantum Horizon Z = 8.0 yrs (Assumption) | Shelf-Life X = 5.0 yrs | Migration Y = 2.0 yrs
Mosca Inequality: X (5.0) + Y (2.0) = 7.0 yrs vs Z (8.0 yrs) -> SATISFIED (X + Y <= Z)

Algorithm    Risk Score   Urgency Tier   Mosca Urgency Status
---------------------------------------------------------------
RSA-2048     58.0         HIGH           No (Slack: +1.0y)
AES-256      12.0         LOW            No (Slack: +1.0y)
```

**REST API Dynamic Re-Evaluation:**
```bash
curl "http://localhost:8000/api/v1/scans/scan-d6f0cb73/risk?horizon=5.0&shelf_life=4.0&migration=2.0"
```

---

### Step 4: Export CycloneDX 1.6 CBOM

ASTRA exports standards-compliant Cryptographic Bill of Materials following the official **CycloneDX 1.6 Cryptographic Asset Profile**:

```bash
astra export scan-d6f0cb73 --output cbom_cyclonedx.json
```

**Sample CycloneDX 1.6 CBOM Excerpt:**
```json
{
  "bomFormat": "CycloneDX",
  "specVersion": "1.6",
  "serialNumber": "urn:uuid:3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "version": 1,
  "metadata": {
    "timestamp": "2026-10-03T18:00:00Z",
    "tools": [
      {
        "vendor": "HEXARK",
        "name": "ASTRA ECDAT",
        "version": "1.0.0"
      }
    ]
  },
  "components": [
    {
      "type": "cryptographic-asset",
      "name": "RSA-2048",
      "cryptoProperties": {
        "assetType": "algorithm",
        "algorithmProperties": {
          "primitive": "asymmetric",
          "parameterSetIdentifier": "2048",
          "classicalSecurityLevel": 112,
          "nistQuantumSecurityLevel": 0
        },
        "oid": "1.2.840.113549.1.1.1"
      }
    }
  ]
}
```

---

### Step 5: Validate CBOM Schema Compliance

Verify that the generated CBOM strictly conforms to CycloneDX 1.6 specifications:
```bash
astra validate scan-d6f0cb73
```
Output:
```text
[SUCCESS] CBOM for scan scan-d6f0cb73 is VALID under CycloneDX 1.6.
Cryptographic Components: 7
```

---

## Interactive Web Dashboard — Real-Time Features

Access the dashboard at **`http://localhost:8000`** after launching the server.

### Drag-and-Drop Archive Intake
- Drop `.zip`, `.tar`, `.tar.gz`, or `.tar.bz2` files directly onto the browser upload target.
- Live progress feedback tracks upload, decompression in isolated sandbox, discovery engine execution, and inventory projection.

### Interactive Mosca Slider
- **Quantum Threat Horizon ($Z$)**: Adjust slider from 1 to 20 years.
- **Data Shelf-Life ($X$)**: Adjust secrecy requirement from 1 to 15 years.
- **Migration Time ($Y$)**: Adjust migration timeline from 1 to 10 years.
- **Instant Client-Side Recalculation**: Urgency counts (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`) and backlog priority order dynamically recalculate without triggering server re-scans.
- Items where $X + Y > Z$ instantly flag with glowing red indicators and Store-Now-Decrypt-Later alerts.

### 3D Parameter Space Visualizer ($X \times Y \times Z$)
Directly below the Mosca sliders in the `02 / MOSCA RISK` tab, an interactive 3D coordinate space visualizer renders the geometric reality of Store-Now-Decrypt-Later exposure:
- **3D Coordinate Axes**: Maps Shelf-Life ($X$, 0–25y in amber), Migration Duration ($Y$, 0–10y in cyan), and Threat Horizon ($Z$, 0–15y in purple).
- **Critical Boundary Hypersurface ($X + Y = Z$)**: A translucent 3D plane dynamically partitions the parameter volume into the **SNDL Risk Exposure Zone** ($X + Y > Z$) and the **Safe Horizon Zone** ($X + Y \le Z$), with contour isoclines and boundary annotations.
- **Live Scenario Beacon & Radar Pulsing**: Adjusting any slider dynamically repositions a pulsating amber beacon with real-time drop-lines, floor shadow projection, and coordinate HUD status readout.
- **Plotted Cryptographic Assets**: Assets from the scan inventory are plotted directly in 3D (green nodes for safe assets, red glowing nodes for SNDL-exposed assets) with floor footprint projections and interactive mouse hover HUD cards showing algorithm details, location, and exposure slack.
- **Full Camera Controls**: Interactive pitch/yaw drag rotation, wheel zoom, preset perspective buttons (`Isometric`, `X-Y Plane`, `X-Z Elevation`), camera reset, and auto-spin orbit toggle.
- **Air-Gapped Sovereign Design**: Engineered with a self-contained HTML5 Canvas 3D projection engine with zero external CDNs or remote dependencies, preserving complete air-gapped isolation.

### Cryptographic Inventory Browser
- Instant search and filtering across algorithm names, key sizes, source file locations, and confidence levels.
- Click any row to expand the full canonical evidence chain, line numbers, and SHA-256 evidence digests.

### Cryptographic DNA Viewer & Drift Regression Alerts
- Displays the scan's deterministic SHA-256 Cryptographic DNA hash.
- Across subsequent scans of the same project, the viewer tracks **temporal drift** (`added`, `removed`, `modified`).
- **Downgrade Alerts**: Automatically flags security regressions if a strong primitive is downgraded (e.g. `AES-256` $\to$ `DES`).

### One-Click CBOM Export & Copy
- Download validated CycloneDX 1.6 JSON with a single click.
- "Copy to Clipboard" button enables rapid ingestion into SIEM or compliance workflows.

---

## Comprehensive REST API Reference

All endpoints are fully documented with interactive testing at **`http://localhost:8000/docs`** (Swagger UI) and **`http://localhost:8000/redoc`**.

### Core Scan Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/scans/upload` | Upload archive (`.zip`, `.tar.gz`) and execute full scan pipeline |
| `POST` | `/api/v1/scans/directory` | Scan server-local directory (disabled when `ASTRA_HOSTED_MODE=true`) |
| `GET` | `/api/v1/scans` | List all historical scans |
| `GET` | `/api/v1/scans/{scan_id}` | Retrieve complete scan record and metadata |
| `GET` | `/api/v1/scans/{scan_id}/findings` | Retrieve canonical assets and detected cryptographic observations |
| `GET` | `/api/v1/scans/{scan_id}/coverage` | Retrieve honest coverage accounting report and blind-spot metrics |
| `GET` | `/api/v1/scans/{scan_id}/risk` | Retrieve Mosca risk calculations or dynamically re-evaluate via query params (`horizon`, `shelf_life`, `migration`) |
| `GET` | `/api/v1/scans/{scan_id}/export` | Export standardized CycloneDX 1.6 CBOM JSON |

### Workflow & Governance Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/workflow/evidence/{asset_id}` | Evidence drilldown for a specific cryptographic asset identity |
| `POST` | `/api/v1/workflow/audit` | Record human verification, override, or signoff audit decision |
| `GET` | `/api/v1/workflow/export` | Export sanitized inventory with parametric secret redaction |
| `POST` | `/api/v1/workflow/audit/chain/append` | Append governance event to immutable SHA-256 Merkle-style audit chain |
| `GET` | `/api/v1/workflow/audit/chain/verify` | Verify cryptographic integrity of the entire governance audit chain |
| `POST` | `/api/v1/workflow/offline/bundle/verify`| Cryptographically verify signed offline threat ruleset bundles |
| `GET` | `/api/v1/workflow/health/production` | Production readiness probe: sandbox isolation, memory quotas, air-gapped status |

### System & Health Probes

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Simple system liveness probe |
| `GET` | `/api/v1/health` | Versioned health probe with sovereign privacy and local processing guarantees |
| `GET` | `/` | Serves the embedded interactive Web Dashboard |
| `GET` | `/docs` | OpenAPI / Swagger interactive documentation |
| `GET` | `/redoc` | ReDoc API documentation |

---

## Production & Air-Gapped Sovereign Operations

ASTRA is engineered for **sovereign, air-gapped enterprise environments** where data cannot leave the boundary:

### Tamper-Evident SHA-256 Audit Chain
Every governance decision (scan approvals, risk overrides, migration sign-offs) is cryptographically linked into a SHA-256 Merkle-style hash chain:
```bash
# Append an audit decision
curl -X POST http://localhost:8000/api/v1/workflow/audit/chain/append \
  -H "Content-Type: application/json" \
  -d '{"action": "APPROVE_MIGRATION", "actor": "crypto_lead", "asset_id": "asset-rsa-01", "details": {"target": "ML-KEM-768"}}'

# Verify chain integrity (detects any tampering or deletion)
curl http://localhost:8000/api/v1/workflow/audit/chain/verify
```

### Air-Gapped Signed Update Bundle Verification
In restricted environments with zero internet access, detection rulesets and NIST PQC mappings are delivered via signed offline update bundles:
```bash
curl -X POST http://localhost:8000/api/v1/workflow/offline/bundle/verify \
  -H "Content-Type: application/json" \
  -d '{"manifest": {"version": "2026.10", "checksum_sha256": "<digest>"}, "raw_content": "<content>", "signer_key_id": "<key_id>"}'
```

### Production Readiness Health Evaluation
```bash
curl http://localhost:8000/api/v1/workflow/health/production
```
Validates:
- Ephemeral sandbox read-only containment.
- Zero external socket connections (air-gapped guarantee).
- Local ruleset cache status and memory limit quotas.

---

## Environment Configuration

Configure ASTRA via `.env` file or environment variables:

| Variable | Default | Description |
|---|---|---|
| `ASTRA_ENV` | `development` | Runtime environment (`development`, `production`) |
| `ASTRA_HOST` | `0.0.0.0` | Host bind address |
| `ASTRA_PORT` | `8000` | Port bind address |
| `ASTRA_HOSTED_MODE` | `false` | When `true`, disables arbitrary `/directory` scans for public hosting safety |
| `ASTRA_CORS_ORIGINS` | `*` | Allowed CORS origins (credentials disabled on wildcard `*`) |
| `MAX_ARCHIVE_SIZE_BYTES` | `104857600` (100 MB) | Maximum upload archive size before HTTP 413 rejection |
| `MAX_UNCOMPRESSED_SIZE_BYTES` | `524288000` (500 MB) | Maximum total extracted uncompressed size |
| `MAX_COMPRESSION_RATIO` | `100` | Zip bomb defense ratio cutoff (100:1) |
| `MAX_FILE_COUNT` | `10000` | Maximum files extracted per archive |
| `DEFAULT_CRQC_HORIZON_YEARS` | `8.0` | Default Mosca quantum threat horizon $Z$ (scenario assumption) |
| `DEFAULT_DATA_SHELF_LIFE_YEARS`| `5.0` | Default data secrecy shelf-life $X$ (scenario assumption) |
| `DEFAULT_MIGRATION_DURATION_YEARS`| `2.0` | Default migration timeline $Y$ (scenario assumption) |
| `TEMP_SCANS_DIR` | `temp_scans` | Temporary scan intake directory |
| `SANDBOX_TMP_DIR` | `sandbox_tmp` | Ephemeral sandbox workspace |

---

## Automated Test Suite (280 Passing Tests)

ASTRA includes an exhaustive automated test suite with **280 tests passing** (88 backend + 192 frontend) across unit, integration, adversarial security, frontend UI components, 3D parameter space logic, and end-to-end user journeys:

### 1. Backend Test Suite (88 Tests)
```bash
python -m pytest backend/tests -v
```
Output:
```text
============================= 88 passed in 3.52s ==============================
```

#### Backend Module Breakdown

| Test Suite Module | Tests | Verification Scope |
|---|---|---|
| `test_intake/` | 13 | Magic byte validation, streaming zip bomb cutoff (100:1), path traversal (`../`, null-byte), symlink/hardlink escape defense |
| `test_discovery/` | 15 | Multi-language source AST/regex, comment & docstring filtering (`#`, `//`, `/* */`, `"""`), manifests, configs, certs, binaries, containers, network |
| `test_coverage/` | 4 | Honest denominator accounting ($N_{\text{assessed}} / N_{\text{total}}$), seeded corpus benchmark ($\ge 80\%$ precision/recall), clean state labeling |
| `test_inventory/` | 7 | Canonical evidence normalization, temporal DNA hash drift, downgrade regression detection, CycloneDX 1.6 validation, multi-scanner reconciliation |
| `test_risk/` | 13 | Mosca theorem ($X+Y>Z$), multi-factor risk scoring, dated NIST PQC mappings, Kahn topological migration roadmaps, security invariant preservation |
| `test_web_workflow/` | 7 | Workflow drilldown, tamper-evident SHA-256 Merkle audit chain, air-gapped bundle verification, production readiness probe |
| `test_functional_assurance/` | 9 | End-to-end user journey cycles (V01 & V02) |
| `test_integration_security/` | 10 | Zero private-key retention, parameter allowlist redaction, hostile archive attack matrix, alert fatigue reduction target ($>50\%$) |
| `test_e2e_product.py` | 10 | Master FastAPI application factory, static dashboard serving, dynamic scenario risk API, standalone CLI commands, synthetic demo scan |

### 2. Frontend Test Suite (192 Tests Across 48 Test Suites)
```bash
cd frontend
npm test
```
Output:
```text
 Test Files  48 passed (48)
      Tests  192 passed (192)
```

#### Frontend Verification Scope
- **Component Primitives**: Modals, Badges, Tabs, Progress Rings, Tooltips, Empty States, and Error Boundaries.
- **Inventory & CBOM**: CycloneDX 1.6 export modals, algorithm matrix mapping, pagination, filtering, and evidence viewers.
- **Mosca Risk & 3D Visualization**: Interactive slider recalculation, SNDL deadline tracking, 3D parameter space projection math, depth sorting, and canvas lifecycle.
- **Scan & Migration Flow**: Drag-and-drop intake, live progress hooks, Kahn topological roadmap rendering, and transition banners.

---

## Troubleshooting & FAQ

| Issue | Root Cause | Immediate Solution |
|---|---|---|
| **Port 8000 already in use** | Another service is listening on port 8000 | Run `astra serve --port 8001` or let `launch.bat` assign an open port |
| **`ModuleNotFoundError: No module named 'app'`** | Python path not referencing backend | Run `pip install -e .` from repo root or set `PYTHONPATH=backend` |
| **`astra: command not found`** | CLI entrypoint not installed | Run `pip install -e .` inside your active virtual environment |
| **`SymlinkEscapeError` during upload** | Archive contains symlinks targeting outside directory | ASTRA rejects symlink escapes for server safety; re-archive without absolute symlinks |
| **Archive rejected: `Compression ratio exceeds limit`** | Archive exceeds 100:1 compression ratio | Zip bomb protection triggered. Unpack and scan directly via `astra scan <dir>` |
| **Scan returns 0 findings** | Target codebase contains no supported cryptographic primitives | Look at `clean_state_label`: `NO_FINDINGS_IN_SUPPORTED_SCOPE` indicates honest absence in supported scope, not a scanner error |
| **Binaries skipped during archive scan** | Executables (`.exe`, `.dll`, `.so`) blocked at web intake | Intended defense-in-depth isolation for uploaded archives. Scan binaries directly via CLI: `astra scan <dir>` |

---

## Privacy, Threat Model & Security Considerations

ASTRA operates under strict enterprise security principles:

1. **Zero Private Key Retention**:
   Whenever private key material (`BEGIN PRIVATE KEY`, `BEGIN RSA PRIVATE KEY`, etc.) is detected, it is immediately masked with `[REDACTED_PRIVATE_KEY_MATERIAL]` and marked `redacted = True`. Private key bytes are never written to disk or logs.
2. **Defensive Archive Decompression**:
   Streaming byte counters enforce 100:1 maximum compression ratio, 500 MB total uncompressed size, and 50 MB single-file limits. Path traversals (`../`), null bytes (`\0`), and symlink escapes are rejected immediately.
3. **Hosted Mode Guardrails**:
   When `ASTRA_HOSTED_MODE=true` is set, the `/api/v1/scans/directory` endpoint is disabled to prevent arbitrary server filesystem exploration by unauthenticated users.
4. **Zero Outbound Telemetry**:
   No outbound network calls, analytics pings, or third-party API dependencies exist. All analysis runs entirely on local CPU.
5. **Vulnerability Reporting**:
   To report a security vulnerability, please email `parinidhijain101@gmail.com`. Do not file public GitHub issues for security vulnerabilities.

---

## Quick Reference Card

```text
┌──────────────────────────────────────────────────────────────────┐
│                   ASTRA Quick Reference Card                     │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  LAUNCH:   launch.bat                 (Windows One-Click)        │
│                                                                  │
│  INSTALL:  git clone https://github.com/adishxm/astra.git        │
│            cd astra && pip install -r requirements.txt           │
│            pip install -e .                                      │
│                                                                  │
│  SCAN:     astra scan ./project --format table                   │
│            astra scan ./archive.zip --format json -o out.json    │
│                                                                  │
│  REVIEW:   astra show <scan_id>                                  │
│                                                                  │
│  RISK:     astra risk <scan_id> --horizon 8.0 --shelf-life 5.0   │
│                        --migration 2.0                           │
│                                                                  │
│  EXPORT:   astra export <scan_id> --output cbom.json             │
│                                                                  │
│  VALIDATE: astra validate <scan_id>                              │
│                                                                  │
│  SERVE:    astra serve --port 8000                               │
│            → Web UI:    http://localhost:8000                    │
│            → API Docs:  http://localhost:8000/docs               │
│                                                                  │
│  TEST:     python -m pytest backend/tests -v                     │
│                                                                  │
│  DOCKER:   docker compose up --build                             │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## Development Roadmap (Phase 2 Enterprise)

| Milestone | Capability | Architectural Description |
|---|---|---|
| **Phase 2.1** | Hardware Security Modules (HSM) | Integration with PKCS#11 hardware security modules, smartcards, and physical enterprise appliances. |
| **Phase 2.2** | Multi-Cloud KMS Discovery | Agentless connectors for AWS KMS, Azure Key Vault, and Google Cloud KMS fleets. |
| **Phase 2.3** | Runtime eBPF Dynamic Inspection | Linux kernel eBPF probes for capturing active TLS handshakes, socket ciphers, and negotiated extensions. |
| **Phase 2.4** | Automated PQC PR Remediation | Automated CI bots for generating pull requests migrating deprecated primitives to NIST PQC standards. |

---

## License & Credits

- **Project**: **ASTRA** (**A**lgorithm **S**ecurity **T**racking and **R**isk **A**ssessment).
- **License**: Licensed under the [MIT License](LICENSE).
- **Team**: Engineered by Team **HEXARK** for Smart India Hackathon 2026 (Problem Statement **SIH26164**).
- **Standards Conformance**:
  - NIST Post-Quantum Cryptography: **FIPS 203 (ML-KEM)**, **FIPS 204 (ML-DSA)**, **FIPS 205 (SLH-DSA)**.
  - CycloneDX Specification: **v1.6 Cryptographic Asset Profile (CBOM)**.
