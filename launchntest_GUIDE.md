# ASTRA — Algorithm Security Tracking and Risk Assessment
### Launch, Test & Usage Guide

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Test Suite](https://img.shields.io/badge/tests-88%20passing%20in%20CI-brightgreen.svg)](https://github.com/adishxm/astra/actions/workflows/ci.yml)
[![PQC Standard](https://img.shields.io/badge/NIST-FIPS%20203%20%7C%20204%20%7C%20205-purple.svg)](https://csrc.nist.gov/projects/post-quantum-cryptography)

> This document is the **authoritative operational guide** for launching, testing, and operating **ASTRA** (**A**lgorithm **S**ecurity **T**racking and **R**isk **A**ssessment — SIH26164 ECDAT). Built by Team **HEXARK**, it covers local development, one-click Windows launch, Docker deployment, CLI usage, REST API workflows, the interactive Web Dashboard, and the automated test suite.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation & Setup](#installation--setup)
   - [Local Development (Bare-Metal)](#option-a-local-development-bare-metal)
   - [Docker Deployment](#option-b-docker-deployment)
3. [Environment Configuration](#environment-configuration)
4. [Launching ASTRA](#launching-astra)
   - [CLI Launch](#1-zero-dependency-cli)
   - [FastAPI Web Server](#2-fastapi-web-server--interactive-dashboard)
   - [Docker Launch](#3-docker-compose-launch)
5. [Complete Scan Workflow — Start to Finish](#complete-scan-workflow--start-to-finish)
   - [Step 1: Initiate a Scan](#step-1-initiate-a-scan)
   - [Step 2: Review Results](#step-2-review-scan-results)
   - [Step 3: Risk & Mosca Analysis](#step-3-risk--mosca-horizon-analysis)
   - [Step 4: Export CBOM](#step-4-export-cyclonedx-16-cbom)
   - [Step 5: Validate CBOM](#step-5-validate-cbom-schema)
6. [REST API Reference](#rest-api-reference)
7. [Interactive Web Dashboard — Real-Time Features](#interactive-web-dashboard--real-time-features)
   - [Drag-and-Drop Archive Upload](#drag-and-drop-archive-upload)
   - [Interactive Mosca Slider](#interactive-mosca-slider)
   - [Cryptographic Inventory Browser](#cryptographic-inventory-browser)
   - [Cryptographic DNA Viewer](#cryptographic-dna-viewer)
   - [One-Click CBOM Export](#one-click-cbom-export)
8. [Production & Air-Gapped Operations](#production--air-gapped-operations)
   - [Tamper-Evident Audit Chain](#tamper-evident-audit-chain)
   - [Air-Gapped Bundle Verification](#air-gapped-bundle-verification)
   - [Production Health Check](#production-health-check)
9. [Running the Automated Test Suite](#running-the-automated-test-suite)
10. [Troubleshooting](#troubleshooting)
11. [Security Considerations](#security-considerations)

---

## Prerequisites

| Requirement | Version | Purpose |
|---|---|---|
| **Python** | 3.10+ | Runtime for backend and CLI |
| **pip** | Latest | Python package installer |
| **Git** | Any | Repository cloning |
| **Docker** *(optional)* | 20.10+ | Container-based deployment |
| **Docker Compose** *(optional)* | v2+ | Multi-service orchestration |

> **Note**: ASTRA is designed to run in **air-gapped sovereign environments**. No internet connectivity is required once dependencies are installed. Zero telemetry is emitted.

---

## Installation & Setup

### Option A: Local Development (Bare-Metal)

```bash
# 1. Clone the repository
git clone https://github.com/adishxm/astra.git
cd astra

# 2. Create a Python virtual environment
python -m venv venv

# Activate on Linux / macOS:
source venv/bin/activate

# Activate on Windows:
.\venv\Scripts\activate

# 3. Install all dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 4. Register the 'astra' CLI globally in editable mode
pip install -e .

# 5. Verify the installation
astra version
```

**Expected output:**
```
ASTRA (Enterprise Cryptographic Discovery & Analysis Tool) v1.0.0
NIST Post-Quantum Standards: FIPS 203 (ML-KEM), FIPS 204 (ML-DSA), FIPS 205 (SLH-DSA)
Operational Profile: AIR_GAPPED_SOVEREIGN_ENTERPRISE
CycloneDX CBOM Specification: 1.6 Conformance
```

### Option B: Docker Deployment

```bash
# Build and start the ASTRA engine container
docker compose up --build

# The server is now live at http://localhost:8000
```

The Dockerfile uses `python:3.10-slim`, installs system dependencies (`gcc`, `libffi-dev`), creates a non-root `astra` user (UID 1000), and runs `uvicorn` on port 8000.

---

## Environment Configuration

Copy the example environment file and customize as needed:

```bash
cp .env.example .env
```

| Variable | Default | Description |
|---|---|---|
| `ASTRA_ENV` | `development` | Runtime mode (`development`, `production`) |
| `ASTRA_HOST` | `0.0.0.0` | Server bind address |
| `ASTRA_PORT` | `8000` | Server bind port |
| `MAX_ARCHIVE_SIZE_BYTES` | `104857600` (100 MB) | Maximum upload archive size |
| `MAX_UNCOMPRESSED_SIZE_BYTES` | `524288000` (500 MB) | Maximum total extracted size |
| `MAX_COMPRESSION_RATIO` | `100` | Zip bomb defense cutoff (100:1) |
| `MAX_FILE_COUNT` | `10000` | Maximum files per archive |
| `DEFAULT_CRQC_HORIZON_YEARS` | `7.0` | Default Mosca quantum threat horizon $Z$ |
| `MIGRATION_HORIZON_SLIDER_MIN` | `1.0` | Min value for Mosca slider UI |
| `MIGRATION_HORIZON_SLIDER_MAX` | `20.0` | Max value for Mosca slider UI |
| `TEMP_SCANS_DIR` | `temp_scans` | Temporary scan intake directory |
| `SANDBOX_TMP_DIR` | `sandbox_tmp` | Ephemeral sandbox workspace |

---

## Launching ASTRA

### 1. Zero-Dependency CLI

The `astra` CLI is a zero-dependency, air-gapped compatible command-line tool. After `pip install -e .`, it is available system-wide.

```bash
# Show version and NIST PQC standards
astra version

# Scan a local directory (table output)
astra scan ./my_project --format table

# Scan an archive file with JSON output
astra scan ./codebase.zip --format json --output report.json

# Show a previous scan's summary
astra show <scan_id>

# Evaluate Mosca risk with custom horizon parameters
astra risk <scan_id> --horizon 10.0 --shelf-life 5.0 --migration 3.0

# Export CycloneDX 1.6 CBOM
astra export <scan_id> --output cbom.json

# Validate CBOM schema compliance
astra validate <scan_id>

# Launch the web server and dashboard
astra serve --host 127.0.0.1 --port 8000
```

### 2. FastAPI Web Server & Interactive Dashboard

```bash
# Direct uvicorn launch (development)
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Or via the CLI
astra serve --host 0.0.0.0 --port 8000 --reload
```

Once running, access:

| URL | Description |
|---|---|
| `http://localhost:8000` | Interactive Web Dashboard |
| `http://localhost:8000/docs` | Swagger / OpenAPI interactive API docs |
| `http://localhost:8000/redoc` | ReDoc API documentation |
| `http://localhost:8000/health` | System health check endpoint |

### 3. Docker Compose Launch

```bash
# Start the full stack
docker compose up --build

# Run in detached (background) mode
docker compose up -d --build

# Check container health
docker compose ps

# View real-time logs
docker compose logs -f astra-ecdat

# Stop and remove containers
docker compose down
```

The Docker container:
- Runs as non-root user `astra` (UID 1000)
- Exposes port `8000`
- Persists scan data to `./data:/app/data`
- Auto-restarts on failure (`unless-stopped`)
- Includes a built-in health check (`curl http://localhost:8000/health`)

---

## Complete Scan Workflow — Start to Finish

This section walks through a real-world cryptographic audit from start to finish.

### Step 1: Initiate a Scan

**Option A: CLI — Scan a directory**
```bash
astra scan ./my_target_project --format table
```

**Option B: CLI — Scan an archive**
```bash
astra scan ./codebase_bundle.zip --format json --output full_scan.json
```

**Option C: REST API — Upload an archive**
```bash
curl -X POST http://localhost:8000/api/v1/scans/upload \
  -F "file=@./codebase_bundle.zip"
```

**Option D: REST API — Scan a server-local directory**
```bash
curl -X POST http://localhost:8000/api/v1/scans/directory \
  -H "Content-Type: application/json" \
  -d '{"path": "/absolute/path/to/project", "target_name": "my-project"}'
```

**Option E: Web Dashboard — Drag-and-drop**
Open `http://localhost:8000` and drag your `.zip` or `.tar.gz` file into the upload zone.

#### What happens internally:

```
Archive Upload
    │
    ▼
Worker 01: Safe Intake
    ├─ Magic byte validation (ZIP/TAR/GZIP/BZIP2)
    ├─ Zip bomb protection (100:1 ratio, 500 MB cap)
    ├─ Path traversal & symlink lockdown
    └─ Ephemeral read-only sandbox created
    │
    ▼
Worker 01: Deterministic Discovery
    ├─ Source code AST + regex scanning (Python, Java, JS/TS, Go, C/C++, Rust)
    ├─ Package manifest parsing (package.json, pom.xml, requirements.txt, etc.)
    ├─ TLS/SSH config auditing
    ├─ X.509 certificate metadata extraction
    ├─ Static binary & container layer analysis
    ├─ Network endpoint detection
    └─ Private key redaction (zero-secret guarantee)
    │
    ▼
Worker 01: Coverage Accounting
    ├─ Honest denominator: N_assessed / N_total
    ├─ Blind-spot flagging for unsupported formats
    └─ Clean state: NO_FINDINGS_IN_SUPPORTED_SCOPE (never "Safe")
    │
    ▼
Worker 02: Evidence & Inventory
    ├─ Canonical evidence normalization
    ├─ Asset identity disambiguation
    ├─ Temporal DNA fingerprinting (SHA-256)
    └─ CycloneDX 1.6 CBOM projection
    │
    ▼
Worker 03: Risk & Migration
    ├─ Mosca Theorem evaluation (X + Y > Z)
    ├─ Multi-factor risk scoring
    ├─ Dated NIST PQC candidate backlog
    ├─ Kahn topological migration roadmap
    └─ Security invariant & rollback assurance
    │
    ▼
Worker 04: Results Delivery
    ├─ CLI table/JSON output
    ├─ REST API JSON response
    ├─ Web Dashboard real-time update
    └─ Tamper-evident audit logging
```

### Step 2: Review Scan Results

**CLI:**
```bash
# Show scan summary by ID
astra show scan-d6f0cb73

# Output:
# Scan ID:             scan-d6f0cb73
# Target:              codebase_bundle.zip
# Created At:          2026-10-03T12:00:00+00:00
# Coverage:            87.5%
# Clean State Label:   FINDINGS_PRESENT
# Cryptographic DNA:   a1b2c3d4e5f6...
```

**REST API:**
```bash
# Get full scan record
curl http://localhost:8000/api/v1/scans/<scan_id>

# Get findings and observations only
curl http://localhost:8000/api/v1/scans/<scan_id>/findings

# Get coverage report
curl http://localhost:8000/api/v1/scans/<scan_id>/coverage

# List all previous scans
curl http://localhost:8000/api/v1/scans
```

### Step 3: Risk & Mosca Horizon Analysis

The **Mosca Theorem** formally evaluates: _If your data shelf-life ($X$) + migration duration ($Y$) exceeds the quantum threat horizon ($Z$), then you are at immediate Store-Now-Decrypt-Later (SNDL) risk._

$$X + Y > Z \implies \text{CRITICAL — Immediate Migration Required}$$

**CLI:**
```bash
astra risk scan-d6f0cb73 --horizon 10.0 --shelf-life 5.0 --migration 3.0
```

**REST API:**
```bash
curl http://localhost:8000/api/v1/scans/<scan_id>/risk
```

**Web Dashboard:** Use the interactive Mosca slider (see [Interactive Mosca Slider](#interactive-mosca-slider)).

### Step 4: Export CycloneDX 1.6 CBOM

**CLI:**
```bash
astra export scan-d6f0cb73 --output cbom_cyclonedx.json
```

**REST API:**
```bash
curl http://localhost:8000/api/v1/scans/<scan_id>/export
```

The exported CBOM conforms to the CycloneDX 1.6 Cryptographic Asset Profile specification, including:
- Component identities with SHA-256 evidence digests
- Algorithm classifications (classical / post-quantum)
- Key sizes, confidence bands, and provenance metadata
- Multi-scanner reconciliation (Discrepancy Index $D$)

### Step 5: Validate CBOM Schema

```bash
astra validate scan-d6f0cb73

# Output:
# [SUCCESS] CBOM for scan scan-d6f0cb73 is VALID under CycloneDX 1.6.
# Cryptographic Components: 14
```

---

## REST API Reference

All endpoints are documented interactively at `/docs` (Swagger UI) and `/redoc` once the server is running.

### Core Scan Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/scans/upload` | Upload archive and execute full scan pipeline |
| `POST` | `/api/v1/scans/directory` | Scan a local server directory |
| `GET` | `/api/v1/scans` | List all completed scans |
| `GET` | `/api/v1/scans/{scan_id}` | Retrieve complete scan record |
| `GET` | `/api/v1/scans/{scan_id}/findings` | Canonical assets and observations |
| `GET` | `/api/v1/scans/{scan_id}/coverage` | Truthful coverage report |
| `GET` | `/api/v1/scans/{scan_id}/risk` | Mosca risk evaluations and PQC backlog |
| `GET` | `/api/v1/scans/{scan_id}/export` | CycloneDX 1.6 CBOM export |

### Workflow & Governance Endpoints (Worker 04)

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/workflow/evidence/{asset_id}` | Evidence drilldown for a specific asset |
| `POST` | `/api/v1/workflow/audit` | Create an audit review record |
| `GET` | `/api/v1/workflow/export` | Sanitized inventory export |
| `POST` | `/api/v1/workflow/audit/chain/append` | Append event to tamper-evident audit chain |
| `GET` | `/api/v1/workflow/audit/chain/verify` | Verify audit chain integrity |
| `POST` | `/api/v1/workflow/offline/bundle/verify` | Verify air-gapped rule/intel update bundle |
| `GET` | `/api/v1/workflow/health/production` | Production readiness and isolation health |

### System Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | System health check |
| `GET` | `/api/v1/health` | System health check (versioned) |
| `GET` | `/` | Web Dashboard (when static assets exist) |
| `GET` | `/docs` | Swagger / OpenAPI interactive documentation |
| `GET` | `/redoc` | ReDoc API documentation |

---

## Interactive Web Dashboard — Real-Time Features

Access the dashboard at **`http://localhost:8000`** after launching the server.

### Drag-and-Drop Archive Upload

1. Open the dashboard in any modern browser.
2. **Drag** a `.zip` or `.tar.gz` archive into the upload zone — or click to browse.
3. The archive is sent to `/api/v1/scans/upload`.
4. The scan pipeline executes in real-time and the dashboard updates automatically with results.

### Interactive Mosca Slider

The Mosca slider is the centerpiece of ASTRA's real-time risk visualization:

1. **Quantum Threat Horizon ($Z$)**: Slide to set when you believe CRQC (Cryptographically Relevant Quantum Computers) will become available (1–20 years).
2. **Data Shelf-Life ($X$)**: Set how long your data must remain confidential.
3. **Migration Duration ($Y$)**: Set how long you estimate PQC migration will take.
4. The dashboard **recalculates in real-time**: all asset urgency tiers (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`) dynamically update as you adjust the sliders.
5. Assets where $X + Y > Z$ are immediately flagged as **CRITICAL (SNDL Risk)** with visual red indicators.

> **How it works**: Each slider change triggers a client-side recalculation against every detected cryptographic asset. The urgency breakdown counter (CRITICAL/HIGH/MEDIUM/LOW) refreshes instantly, and the risk table reorders by priority. This enables scenario-based sensitivity analysis — you can model optimistic vs. pessimistic quantum timelines without re-running the scan.

### Cryptographic Inventory Browser

- **Real-time search and filter** across all detected algorithms, key sizes, confidence ratings, and source locations.
- Each finding row shows: Algorithm name, Key Size (bits), Source Kind (source code, manifest, config, certificate, binary, etc.), File Location (with line number), and Confidence band.
- Click any row to expand the full canonical evidence chain with SHA-256 evidence digests.

### Cryptographic DNA Viewer

- Displays the **deterministic SHA-256 Cryptographic DNA hash** for the entire scan.
- When multiple scans of the same codebase exist, the viewer shows **temporal drift** — which assets were `added`, `removed`, or `modified` between versions.
- **Downgrade alerts**: If a stronger algorithm (e.g., AES-256) was replaced with a weaker one (e.g., DES), a high-urgency regression alert is triggered automatically.

### One-Click CBOM Export

- Click the **Export CBOM** button to download a CycloneDX 1.6 JSON file.
- Alternatively, use the **Copy to Clipboard** button for quick pasting into compliance tools.
- The exported CBOM includes all canonical evidence, component relationships, and provenance metadata.

---

## Production & Air-Gapped Operations

ASTRA is designed for **sovereign, air-gapped enterprise environments** with zero outbound telemetry.

### Tamper-Evident Audit Chain

All governance decisions (scan approvals, review sign-offs, risk acknowledgements) are chained into an immutable **SHA-256 Merkle-style hash chain**.

```bash
# Append a governance event
curl -X POST http://localhost:8000/api/v1/workflow/audit/chain/append \
  -H "Content-Type: application/json" \
  -d '{"action": "APPROVE_SCAN", "actor": "security_lead", "asset_id": "asset-001", "details": {"justification": "PQC migration verified"}}'

# Verify the entire chain is intact (no tampering)
curl http://localhost:8000/api/v1/workflow/audit/chain/verify
```

If any record in the chain has been modified or deleted, verification fails with details about the broken link.

### Air-Gapped Bundle Verification

In offline environments, threat intelligence and rule updates are delivered as **signed bundles**. ASTRA verifies bundle integrity before applying updates.

```bash
curl -X POST http://localhost:8000/api/v1/workflow/offline/bundle/verify \
  -H "Content-Type: application/json" \
  -d '{"manifest": {"version": "2026.10", "checksum_sha256": "<sha256>"}, "raw_content": "<bundle_content>", "signer_key_id": "<key_id>"}'
```

### Production Health Check

Evaluate sandbox isolation, air-gapped status, local ruleset cache, and memory quotas:

```bash
curl http://localhost:8000/api/v1/workflow/health/production
```

---

## Running the Automated Test Suite

ASTRA includes **84 automated tests** covering unit, integration, security, and end-to-end product validation.

### Run All Tests

```bash
# From the repository root
python -m pytest backend/tests -v
```

**Expected output:**
```
============================= 84 passed in 3.57s ==============================
```

### Run Tests in Docker

```bash
docker compose --profile test run astra-tests
```

### Test Suite Breakdown

| Test Module | Count | Scope |
|---|---|---|
| `test_intake/` | 13 | Archive safety: zip bombs, path traversal, symlink escapes, magic byte validation |
| `test_discovery/` | 12 | Multi-surface discovery: source code, configs, certs, binaries, containers, network |
| `test_coverage/` | 4 | Honest denominator, benchmark precision/recall (≥80%), clean state labeling |
| `test_inventory/` | 7 | Canonical evidence, temporal DNA time-machine, CycloneDX 1.6 reconciliation |
| `test_risk/` | 13 | Mosca theorem, multi-factor scoring, Kahn topological roadmaps, rollback assurance |
| `test_web_workflow/` | 7 | Workflow API, tamper-evident audit chain, air-gapped bundle verification |
| `test_functional_assurance/` | 9 | End-to-end user journey cycles (V01 & V02) |
| `test_integration_security/` | 9 | Zero-key retention, hostile archive attacks, schema round-trip, alert fatigue reduction |
| `test_e2e_product.py` | 10 | Full product integration: ScanService, FastAPI endpoints, CLI commands |

### Run Specific Test Modules

```bash
# Run only intake security tests
python -m pytest backend/tests/test_intake -v

# Run only risk and Mosca tests
python -m pytest backend/tests/test_risk -v

# Run only end-to-end product tests
python -m pytest backend/tests/test_e2e_product.py -v

# Run with coverage report
python -m pytest backend/tests -v --cov=backend/app --cov-report=term-missing
```

---

## Troubleshooting

### Common Issues & Solutions

| Problem | Cause | Solution |
|---|---|---|
| `ModuleNotFoundError: No module named 'app'` | PYTHONPATH not set | Run `pip install -e .` or set `PYTHONPATH=backend` |
| `astra: command not found` | CLI not registered | Run `pip install -e .` from the repo root |
| Port 8000 already in use | Another process on port | Use `astra serve --port 8001` or kill the existing process |
| `Unsupported archive format` on upload | Wrong file extension | Supported formats: `.zip`, `.tar`, `.tar.gz`, `.tgz`, `.tar.bz2` |
| Docker health check failing | Container not ready | Wait 10–15s for startup; check `docker compose logs -f` |
| Scan returns 0 findings | No crypto in supported files | Check `clean_state_label` — `NO_FINDINGS_IN_SUPPORTED_SCOPE` is expected for non-crypto codebases |
| `SymlinkEscapeError` | Archive contains symlinks pointing outside sandbox | ASTRA rejects these for security; remove symlinks from the archive |
| High compression ratio rejected | Archive exceeds 100:1 ratio | Split large archives or increase `MAX_COMPRESSION_RATIO` in `.env` |

### Log Verbosity

```bash
# Enable debug logging
ASTRA_DEBUG=true astra scan ./project --format table

# Verbose pytest output
python -m pytest backend/tests -v --tb=long
```

---

## Security Considerations

ASTRA enforces strict boundary security by design. For details, see [`SECURITY.md`](SECURITY.md).

| Guarantee | Implementation |
|---|---|
| **Zero Private Key Storage** | Private keys are detected, masked as `[REDACTED_PRIVATE_KEY_MATERIAL]`, and never persisted |
| **Zip Bomb Protection** | Streaming byte counters enforce 100:1 ratio, 500 MB total, 50 MB per-file limits |
| **Sandbox Isolation** | Ephemeral, read-only directories with symlink/hardlink escape rejection |
| **Path Traversal Defense** | `../`, null bytes, and Windows drive specifiers are blocked before filesystem access |
| **Zero Telemetry** | Air-gapped sovereign profile — no outbound network calls, no analytics, no tracking |
| **Tamper-Evident Audit** | SHA-256 Merkle-chain ensures all governance decisions are cryptographically immutable |
| **Non-Root Execution** | Docker container runs as `astra` user (UID 1000), not root |

### Reporting Vulnerabilities

If you discover a security vulnerability, **do not open a public GitHub issue**. Instead:
1. Email `topasingh903811@gmail.com` with reproduction steps and impact assessment.
2. We acknowledge receipt within 48 hours and coordinate responsible disclosure.

---

## Quick Reference Card

```
┌──────────────────────────────────────────────────────────────────┐
│                   ASTRA Quick Reference                          │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  INSTALL:  git clone https://github.com/adishxm/astra.git       │
│            pip install -e .                                      │
│                                                                  │
│  SCAN:     astra scan ./project --format table                   │
│            astra scan ./archive.zip --format json -o report.json │
│                                                                  │
│  REVIEW:   astra show <scan_id>                                  │
│                                                                  │
│  RISK:     astra risk <scan_id> --horizon 10 --shelf-life 5      │
│                        --migration 3                             │
│                                                                  │
│  EXPORT:   astra export <scan_id> -o cbom.json                   │
│                                                                  │
│  VALIDATE: astra validate <scan_id>                              │
│                                                                  │
│  SERVE:    astra serve --port 8000                                │
│            → Dashboard:  http://localhost:8000                    │
│            → API Docs:   http://localhost:8000/docs               │
│                                                                  │
│  TEST:     python -m pytest backend/tests -v                     │
│                                                                  │
│  DOCKER:   docker compose up --build                             │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

_For contributing guidelines, see [`CONTRIBUTING.md`](CONTRIBUTING.md). For security policy, see [`SECURITY.md`](SECURITY.md). For full architecture and capabilities, see [`README.md`](README.md)._
