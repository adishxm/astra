# ASTRA Frontend — API Contract & Reality Check

> **Document Status:** Verified against live ASTRA backend engine (`v1.0.0`, Team HEXARK, SIH26164)  
> **Target Branch:** `feat/frontend-p01-api-contract`  
> **Source Fixtures:** `frontend/src/test/fixtures/` (26 fixtures captured and validated)

---

## 1. Executive Summary & Integration Architecture

This document defines the formal, verified contract between the ASTRA FastAPI backend (`http://127.0.0.1:8000`) and the incoming React Single Page Application (SPA). Every field, type, nullable flag, and error response in this contract has been extracted directly from live captured responses and confirmed against backend implementation code in `backend/app/`.

### Architecture & Base URL
- **Vite Dev Server:** `http://localhost:5173` (proxies `/api` and `/health` to `http://127.0.0.1:8000`)
- **Backend API Base:** `http://127.0.0.1:8000`
- **CORS:** Backend defaults to wildcard `allow_origins=["*"]` with credentials disabled. With Vite reverse proxy, all frontend calls are same-origin.
- **Protocol Formats:** All REST request/response payloads use JSON (`application/json`), except archive intake which uses multipart form-data (`multipart/form-data`). Timestamps use ISO 8601 UTC with fractional seconds (`YYYY-MM-DDTHH:MM:SS.mmmmmm+00:00`).

---

## 2. Comprehensive Endpoint Catalog

---

### 2.1 System Health & Metadata (`GET /health` & `GET /api/v1/health`)

- **Method / Path:** `GET /health` (also aliased at `GET /api/v1/health`)
- **Query Parameters:** None
- **Used by:** `Header.jsx`, `DashboardPage.jsx`, `useHealth.js`

#### Response Shape
| Field | Type | Nullable? | Example from Real Fixture (`health.json`) | Used by Spec Component |
|---|---|---|---|---|
| `status` | string | No | `"pass"` | `Badge.jsx`, Header status indicator |
| `service` | string | No | `"ASTRA Cryptographic Engine"` | Header, System information modal |
| `version` | string | No | `"1.0.0"` | Footer version badge |
| `team` | string | No | `"HEXARK"` | Footer attribution |
| `profile` | string | No | `"AIR_GAPPED_SOVEREIGN_ENTERPRISE"` | Header sovereign mode badge |
| `hosted_mode` | boolean | No | `false` | Upload / Directory scan feature toggles |
| `directory_scan_permitted` | boolean | No | `true` | Settings / Scan UI options |
| `privacy_notice` | object | No | `{"processing": "LOCAL_CPU_ONLY", "telemetry_egress": "DISABLED", "retention": "PERSISTED_LOCALLY_IN_ASTRA_STORE", "secrets_handling": "AUTOMATIC_PRIVATE_KEY_REDACTION"}` | Privacy modal / Tooltip |
| `timestamp` | string (ISO) | No | `"2026-10-03T16:56:58.337072+00:00"` | Live heartbeat indicator |
| `pqc_standards` | array[string] | No | `["FIPS 203 (ML-KEM)", "FIPS 204 (ML-DSA)", "FIPS 205 (SLH-DSA)"]` | Dashboard standards footer |

#### Observed Errors
- None under normal operation (returns 200). If backend is offline, browser `fetch` throws `TypeError: Failed to fetch`.

---

### 2.2 Archive Intake & Full Scan Execution (`POST /api/v1/scans/upload`)

- **Method / Path:** `POST /api/v1/scans/upload`
- **Content-Type:** `multipart/form-data; boundary=...`
- **Body:** Form field `file` containing binary archive (`.zip`, `.tar`, `.tar.gz`, `.tgz`, `.tar.bz2`)
- **Execution Model:** **Synchronous / Blocking**. The server uploads bytes to sandbox, streams extraction, executes all static discovery detectors, computes coverage denominator, evaluates default Mosca risk, and projects CycloneDX 1.6 CBOM before responding.
- **Used by:** `UploadDropzone.jsx`, `ScanPage.jsx`

#### Response Shape
| Field | Type | Nullable? | Example from Real Fixture (`scan_upload_response.json`) | Used by Spec Component |
|---|---|---|---|---|
| `status` | string | No | `"completed"` | `ScanSummaryCard.jsx` |
| `scan_id` | string | No | `"scan-15ff86cd"` | Navigation redirect `/scans/:scanId` |
| `target_name` | string | No | `"synthetic_sample.zip"` | Scan title display |
| `created_at` | string (ISO) | No | `"2026-10-03T16:56:58.460333+00:00"` | Timestamp display |
| `asset_count` | integer | No | `6` | Summary asset count badge |
| `coverage_percentage` | float | No | `85.71` | Coverage radial gauge |
| `clean_state_label` | string | No | `"COMPLETE_WITH_COVERAGE_ACCOUNTING"` | Clean state audit badge |
| `dna_hash` | string (hex) | No | `"e6e1eeb805b4c1265f2479f64bfdb8a49d5bf5cb7a7d4cf48148b55ca135763a"` | Cryptographic DNA chip |
| `canonical_assets` | array[object] | No | Array of `AssetIdentity` objects | Findings preview |
| `summary` | object | No | See detail below | Stats row & cards |
| `summary.total_files` | integer | No | `6` | Total files count |
| `summary.assessed_files` | integer | No | `6` | Assessed files count |
| `summary.coverage_percentage` | float | No | `85.71` | Coverage metric |
| `summary.clean_state_label` | string | No | `"COMPLETE_WITH_COVERAGE_ACCOUNTING"` | Status badge |
| `summary.critical_urgency_count` | integer | No | `1` | Critical urgency count |
| `summary.high_urgency_count` | integer | No | `2` | High urgency count |
| `summary.medium_urgency_count` | integer | No | `1` | Medium urgency count |
| `summary.low_urgency_count` | integer | No | `1` | Low urgency count |

#### Observed Errors
- **`400 Bad Request`** (`errors/400_invalid_archive.json`):
  ```json
  { "detail": "Unsupported archive format. Expected one of: .zip, .tar, .tar.gz, .tar.bz2" }
  ```
- **`413 Request Entity Too Large`** (`errors/413_too_large.json`):
  ```json
  { "detail": "Uploaded archive exceeds maximum limit of 100 MB" }
  ```
- **`500 Internal Server Error`**:
  ```json
  { "detail": "Scan execution failed: File is not a zip file" }
  ```

---

### 2.3 List Scans (`GET /api/v1/scans`)

- **Method / Path:** `GET /api/v1/scans`
- **Query Parameters:** None (backend returns all in-memory scans sorted by `created_at` descending)
- **Used by:** `ScanHistoryTable.jsx`, `DashboardPage.jsx`, `useScans.js`

#### Response Shape (Array of Objects)
| Field | Type | Nullable? | Example from Real Fixture (`scans_list.json`) | Used by Spec Component |
|---|---|---|---|---|
| `scan_id` | string | No | `"scan-15ff86cd"` | Row key, click navigation |
| `target_name` | string | No | `"synthetic_sample.zip"` | Target repository / archive name |
| `created_at` | string (ISO) | No | `"2026-10-03T16:56:58.460333+00:00"` | Relative time / date column |
| `asset_count` | integer | No | `6` | Asset count badge |
| `coverage_percentage` | float | No | `85.71` | Coverage bar / pill |
| `dna_hash` | string (hex) | No | `"e6e1eeb805b4c1265f2479f64bfdb8a49d5bf5cb7a7d4cf48148b55ca135763a"` | DNA fingerprint preview |

#### Surprising Finding / Gap:
`GET /api/v1/scans` items do **NOT** contain `critical_urgency_count`, `high_urgency_count`, or `clean_state_label`. To compute the Dashboard "Critical Risks" aggregate card across all scans, the frontend must either make individual calls to `/api/v1/scans/:id` or derive it from fetched scan records (see Section 5 & Gaps).

---

### 2.4 Get Scan Detail (`GET /api/v1/scans/{scan_id}`)

- **Method / Path:** `GET /api/v1/scans/{scan_id}`
- **Path Parameter:** `scan_id` (e.g. `scan-15ff86cd`)
- **Used by:** `ScanDetailPage.jsx`, `ScanSummaryCard.jsx`, `useApi.js`

#### Response Shape
| Field | Type | Nullable? | Example from Real Fixture (`scan_detail.json`) | Used by Spec Component |
|---|---|---|---|---|
| `scan_id` | string | No | `"scan-15ff86cd"` | Page header |
| `status` | string | No | `"completed"` | Status banner |
| `target_name` | string | No | `"synthetic_sample.zip"` | Breadcrumb / Title |
| `created_at` | string (ISO) | No | `"2026-10-03T16:56:58.460333+00:00"` | Header metadata |
| `manifest` | object | No | Object containing `archive_name`, `total_files_in_archive`, `files` | Manifest inspection |
| `coverage` | object | No | Detailed `CoverageReport` (see 2.6) | Coverage overview |
| `asset_count` | integer | No | `6` | Asset counter |
| `observations_count`| integer | No | `16` | Raw observation counter |
| `cryptographic_dna_hash` | string | No | `"e6e1eeb805b4..."` | DNA hash viewer / copy action |
| `summary` | object | No | Identical to upload summary (urgency counts, coverage %) | Quick stats cards |
| `canonical_assets` | array[object] | No | Array of deduplicated `AssetIdentity` items | Assets tab |
| `risk_evaluations` | array[object] | No | Array of `RiskEvaluation` items | Risk tab |
| `backlog_items` | array[object] | No | Array of `PQCBacklogTask` items | Migration backlog |
| `cbom_data` | object | No | Full CycloneDX 1.6 CBOM document | CBOM tab |

#### Observed Errors
- **`404 Not Found`** (`errors/404_scan_not_found.json`):
  ```json
  { "detail": "Scan ID not found: scan-nonexistent-id-0000" }
  ```

---

### 2.5 Get Scan Findings & Observations (`GET /api/v1/scans/{scan_id}/findings`)

- **Method / Path:** `GET /api/v1/scans/{scan_id}/findings`
- **Path Parameter:** `scan_id` (string)
- **Used by:** `FindingsTable.jsx`, `ObservationDetail.jsx`, `FindingsPage.jsx`

#### Response Shape
| Field | Type | Nullable? | Example from Real Fixture (`findings.json`) | Used by Spec Component |
|---|---|---|---|---|
| `scan_id` | string | No | `"scan-15ff86cd"` | Table header |
| `asset_count` | integer | No | `6` | Findings count badge |
| `canonical_assets` | array[object] | No | Grouped assets by algorithm & file | Asset grouping view |
| `observations` | array[object] | No | Flattened list of all 16 evidence items | `FindingsTable.jsx` rows |
| `observations[].observation_id` | string (UUID) | No | `"0e1f99bf-3d2d-4c97-a281-77a118beabff"` | Row key |
| `observations[].candidate_asset_id` | string | No | `"rsa-2048-crypto_service.py-22"` | Group anchor / drilldown link |
| `observations[].claim_type` | string (Enum) | No | `"ALGORITHM_USE"` | Claim type badge |
| `observations[].source_kind` | string (Enum) | No | `"SOURCE_CODE"` | Source icon (Code/Config/Cert) |
| `observations[].algorithm` | string | Yes | `"RSA-2048"` | Column 1: Algorithm |
| `observations[].purpose` | string | Yes | `"ASYMMETRIC"` | Column 2: Purpose |
| `observations[].key_size_bits` | integer | Yes | `2048` | Key size badge |
| `observations[].curve_name` | string | Yes | `null` | Curve tag (e.g. secp256r1) |
| `observations[].protocol` | string | Yes | `null` | Protocol tag (e.g. TLSv1.3) |
| `observations[].relative_path` | string | No | `"crypto_service.py"` | Column 4: Source File |
| `observations[].start_line` | integer | Yes | `22` | Column 4: Line Number |
| `observations[].end_line` | integer | Yes | `22` | Line range |
| `observations[].sanitized_excerpt`| string | No | `"algorithm_tag = \"RSA-2048\""` | Expanded code snippet |
| `observations[].evidence_digest` | string (hex) | No | `"c7f8132721b5..."` | SHA-256 evidence anchor |
| `observations[].redacted` | boolean | No | `false` | Secret redaction banner |
| `observations[].detector_id` | string | No | `"detector-source-code-v1"` | Column 6: Detector |
| `observations[].confidence` | string (Enum) | No | `"CONFIRMED"` | Column 5: Confidence |
| `observations[].confidence_rationale` | string | No | `"Pattern match for RSA-2048 in .py"` | Confidence hover tooltip |
| `observations[].state` | string (Enum) | No | `"OBSERVED"` | Evidence state badge |
| `observations[].observed_at` | string (ISO) | No | `"2026-10-03T16:56:58.456333+00:00"` | Timestamp |
| `observations[].raw_parameters` | object | No | `{"quantum_status": "QUANTUM_VULNERABLE"}` | Column 3: Quantum Safety |

---

### 2.6 Get Truthful Coverage Accounting (`GET /api/v1/scans/{scan_id}/coverage`)

- **Method / Path:** `GET /api/v1/scans/{scan_id}/coverage`
- **Path Parameter:** `scan_id` (string)
- **Used by:** `CoverageBar.jsx`, `ScanDetailPage.jsx`

#### Response Shape
| Field | Type | Nullable? | Example from Real Fixture (`coverage_full.json`) | Used by Spec Component |
|---|---|---|---|---|
| `scan_id` | string | No | `"scan-15ff86cd"` | Scan ID reference |
| `total_files_in_archive` | integer | No | `6` | Total files denominator |
| `total_assessed_files` | integer | No | `6` | Assessed files numerator |
| `total_unsupported_files` | integer | No | `0` | Blind-spot file count |
| `total_skipped_files` | integer | No | `0` | Skipped files count |
| `total_failed_files` | integer | No | `0` | Parser failure count |
| `total_observations_found`| integer | No | `16` | Total findings count |
| `overall_coverage_percentage`| float | No | `85.71` | Main coverage gauge / bar |
| `is_partial_scan` | boolean | No | `false` | Partial scan warning banner |
| `scan_status_label` | string | No | `"COMPLETE_WITH_COVERAGE_ACCOUNTING"` | Clean-state audit label |
| `surface_breakdown` | object | No | Map of surface category -> `SurfaceCoverage` | Surface breakdown grid |
| `surface_breakdown.SOURCE_CODE` | object | No | `{"surface": "SOURCE_CODE", "total_files": 1, "assessed_files": 1, "files_with_findings": 1, "coverage_percentage": 100.0}` | Source code coverage bar |
| `surface_breakdown.PACKAGE_MANIFEST` | object | No | `{"surface": "PACKAGE_MANIFEST", "total_files": 1, "assessed_files": 1, "coverage_percentage": 100.0}` | Manifest coverage bar |
| `surface_breakdown.CONFIGURATION` | object | No | `{"surface": "CONFIGURATION", "total_files": 1, "assessed_files": 1, "coverage_percentage": 100.0}` | Config coverage bar |
| `surface_breakdown.CERTIFICATE_STORE` | object | No | `{"surface": "CERTIFICATE_STORE", "total_files": 1, "assessed_files": 1, "coverage_percentage": 100.0}` | Certs coverage bar |
| `surface_breakdown.UNSUPPORTED_SURFACE` | object | No | `{"surface": "UNSUPPORTED_SURFACE", "total_files": 2, "assessed_files": 0, "coverage_percentage": 0.0}` | Blind-spot / Unsupported bar |
| `unsupported_extensions` | array[string] | No | `[".wav"]` | Unsupported file extension list |
| `collector_health` | object | No | `{"source_code": "HEALTHY", "manifests": "HEALTHY", "configs": "HEALTHY", "certificates": "HEALTHY"}` | Collector health badges |
| `evaluated_at` | string (ISO) | No | `"2026-10-03T16:56:58.459333+00:00"` | Evaluation timestamp |

---

### 2.7 Mosca Risk Evaluation & Scenario Simulation (`GET /api/v1/scans/{scan_id}/risk`)

- **Method / Path:** `GET /api/v1/scans/{scan_id}/risk`
- **Query Parameters (Optional):**
  - `horizon`: float (Quantum Threat Horizon $Z$ in years, default `8.0`, allowed `ge=1.0`)
  - `shelf_life`: float (Data Secrecy Shelf-Life $X$ in years, default `5.0`, allowed `ge=0.0`)
  - `migration`: float (Migration Duration $Y$ in years, default `2.0`, allowed `ge=0.0`)
- **Used by:** `RiskPage.jsx`, `MoscaTimeline.jsx`, `RiskSlider.jsx`, `RiskScoreCard.jsx`, `BacklogTable.jsx`

#### Response Shape
| Field | Type | Nullable? | Example from Real Fixture (`risk_custom.json`) | Used by Spec Component |
|---|---|---|---|---|
| `scan_id` | string | No | `"scan-15ff86cd"` | Scan ID reference |
| `scenario` | object | Yes (if params passed) | Scenario simulation assumption metadata | Scenario assumption card |
| `scenario.quantum_threat_horizon_years` | float | No | `5.0` | Active $Z$ slider display |
| `scenario.horizon_rationale` | string | No | `"Planning scenario assumption aligned with NIST IR 8547..."` | Assumption disclaimer |
| `context` | object | Yes (if params passed) | Active context factors | Context display |
| `context.data_shelf_life_years` | float | No | `4.0` | Active $X$ slider display |
| `context.migration_duration_years` | float | No | `2.0` | Active $Y$ slider display |
| `risk_evaluations` | array[object] | No | Array of evaluated assets | Risk heatmap & asset cards |
| `risk_evaluations[].asset_id` | string | No | `"rsa-2048-crypto_service.py-22"` | Asset link |
| `risk_evaluations[].algorithm` | string | No | `"RSA-2048"` | Algorithm name |
| `risk_evaluations[].purpose` | string | No | `"ASYMMETRIC"` | Purpose tag |
| `risk_evaluations[].risk_score` | float | No | `70.4` | Numerical risk score (0-100) |
| `risk_evaluations[].urgency` | string (Enum) | No | `"CRITICAL"` | Urgency Tier (CRITICAL/HIGH/MED/LOW) |
| `risk_evaluations[].mosca_condition_violated` | boolean | No | `true` | SNDL Violation Flag ($X+Y > Z$) |
| `risk_evaluations[].mosca_slack_years` | float | No | `-1.0` | Slack value ($Z - (X+Y)$) |
| `risk_evaluations[].is_scenario_assumption` | boolean | No | `true` | Simulation badge |
| `risk_evaluations[].factor_contributions` | object | No | `{"quantum_vulnerability": 40.0, "mosca_urgency": 25.0, "exposure": 12.0, "criticality": 9.0}` | Risk factor radar / bar breakdown |
| `risk_evaluations[].reason_codes` | array[string] | No | `["QUANTUM_VULNERABLE_ASYMMETRIC", "MOSCA_DEADLINE_EXCEEDED"]` | Decision explanation pills |
| `backlog_items` | array[object] | No | Array of PQC migration tasks | `BacklogTable.jsx` |
| `backlog_items[].task_id` | string | No | `"task-f90a2c1b"` | Backlog row ID |
| `backlog_items[].algorithm` | string | No | `"RSA-2048"` | Current algorithm |
| `backlog_items[].pqc_alternative` | string | No | `"ML-KEM-768 (FIPS 203) / ML-DSA-65 (FIPS 204)"` | NIST PQC Replacement |
| `backlog_items[].priority` | string | No | `"P0_CRITICAL_SNDL"` | Priority badge |
| `backlog_items[].recommended_action`| string | No | `"Replace RSA-2048 key exchange with ML-KEM-768 hybrid mode"` | Action description |

---

### 2.8 Export CycloneDX 1.6 CBOM (`GET /api/v1/scans/{scan_id}/export`)

- **Method / Path:** `GET /api/v1/scans/{scan_id}/export`
- **Query Parameter:** `format`: string (default `"cyclonedx"`)
- **Used by:** `CBOMPage.jsx`, `CBOMTreeView.jsx`, `CBOMExportPanel.jsx`

#### Response Shape
| Field | Type | Nullable? | Example from Real Fixture (`export_cbom.json`) | Used by Spec Component |
|---|---|---|---|---|
| `bomFormat` | string | No | `"CycloneDX"` | Header format validation |
| `specVersion` | string | No | `"1.6"` | Spec version badge |
| `serialNumber` | string (URN) | No | `"urn:uuid:scan-15ff86cd"` | Serial number display |
| `version` | integer | No | `1` | Document version |
| `metadata` | object | No | Metadata with `timestamp`, `tools`, `component` | Metadata box |
| `components` | array[object] | No | Array of cryptographic components | `CBOMTreeView.jsx` root |
| `components[].type` | string | No | `"cryptographic-asset"` | Component type badge |
| `components[].name` | string | No | `"RSA-2048-rsa-2048"` | Component node label |
| `components[].cryptoProperties` | object | No | CycloneDX 1.6 Crypto Properties | Node property inspector |
| `components[].cryptoProperties.assetType` | string | No | `"algorithm"` | Asset classification |
| `components[].cryptoProperties.algorithmProperties.name` | string | No | `"RSA-2048"` | Primitive algorithm |
| `components[].cryptoProperties.algorithmProperties.parameterSetIdentifier` | string | No | `"2048"` | Parameter / key size |
| `components[].cryptoProperties.algorithmProperties.executionEnvironment` | string | No | `"software-plain-ram"` | Execution environment |

---

### 2.9 Governance Audit Trail & Tamper-Evident Chain (`/api/v1/workflow/audit/chain/*`)

#### `POST /api/v1/workflow/audit/chain/append`
- **Method / Path:** `POST /api/v1/workflow/audit/chain/append`
- **Body:**
  ```json
  {
    "action": "SCAN_INITIATED",
    "actor": "secops_lead",
    "asset_id": "rsa-2048-crypto_service.py-22",
    "details": { "scope": "synthetic_sample", "environment": "staging" }
  }
  ```
- **Response Shape (`audit_append_response.json`):**
  | Field | Type | Example |
  |---|---|---|
  | `event_id` | string (UUID) | `"b9f9ec26-3844-4824-a292-23c4daaeefae"` |
  | `sequence_number` | integer | `1` |
  | `timestamp` | string (ISO) | `"2026-10-03T16:56:58.503333+00:00"` |
  | `action` | string | `"SCAN_INITIATED"` |
  | `actor` | string | `"secops_lead"` |
  | `asset_id` | string (or null) | `"rsa-2048-crypto_service.py-22"` |
  | `details` | object | `{"scope": "synthetic_sample", "environment": "staging"}` |
  | `previous_event_hash` | string (SHA-256) | `"0000000000000000000000000000000000000000000000000000000000000000"` (Genesis) |
  | `event_hash` | string (SHA-256) | `"0ea78546b8206ae77fca9ea8cb2e9cb00508f7aa9d1e56b85662705aa43e4983"` |

#### `GET /api/v1/workflow/audit/chain/verify`
- **Method / Path:** `GET /api/v1/workflow/audit/chain/verify`
- **Response Shape (`audit_verify_valid.json`):**
  | Field | Type | Example |
  |---|---|---|
  | `valid` | boolean | `true` |
  | `event_count` | integer | `3` |
  | `genesis_hash` | string | `"0000000000000000000000000000000000000000000000000000000000000000"` |
  | `tip_hash` | string | `"225fd244ad3ba9c4275d6bfa5fbc1a583710d68a39619da02aa8e15da589b973"` |
  | `message` | string | `"Audit chain fully verified; zero tampering detected"` |

---

### 2.10 Production Readiness & Sovereign Health (`GET /api/v1/workflow/health/production`)

- **Method / Path:** `GET /api/v1/workflow/health/production`
- **Response Shape (`health_production.json`):**
  | Field | Type | Example | Used by |
  |---|---|---|---|
  | `production_ready` | boolean | `true` | `HealthDashboard.jsx` ready status |
  | `air_gap_compliant` | boolean | `true` | Air-gapped badge |
  | `security_profile` | string | `"AIR_GAPPED_SOVEREIGN"` | Security profile title |
  | `active_defenses` | array[string] | `["Streaming zip bomb limit (100:1 / 500MB)", "Path traversal normalization", "Automated private key redaction", "Memory-only execution sandbox", "Zero outbound telemetry"]` | Defense features checklist |
  | `runtime_environment` | object | `{"os": "Windows-10-10.0.26100-SP0", "python_version": "3.11.9", "cpu_count": 12}` | Environment panel |
  | `timestamp` | string (ISO) | `"2026-10-03T16:56:58.508333+00:00"` | Live check timestamp |

---

## 3. Real Enum Catalog & Design Token Color Mappings

All string enums observed in real fixtures are cataloged below and mapped to the CSS design tokens defined in `phase_Aa.md` Section 4.

| Enum Category | Observed Value in Real Data | Description | Recommended Design Token Badge |
|---|---|---|---|
| **Quantum Safety** (`raw_parameters.quantum_status`) | `POST_QUANTUM` | Verified NIST PQC algorithm (ML-KEM, ML-DSA) | `var(--emerald)` (Green `#10b981`) |
| | `CLASSICAL` | Classical strong (AES-256, SHA-256, TLS 1.3) | `var(--cyan)` (Cyan `#06b6d4`) |
| | `QUANTUM_VULNERABLE` | Asymmetric/ECC vulnerable to Shor's algorithm | `var(--rose)` (Red `#f43f5e`) |
| | `VULNERABLE` / `DEPRECATED` | Broken legacy primitive (MD5, DES, TLS 1.0) | `var(--rose)` with strobe animation |
| **Urgency Tier** (`urgency`) | `CRITICAL` | Mosca violation ($X+Y > Z$) or broken crypto | `var(--rose)` (Red `#f43f5e`) |
| | `HIGH` | Quantum vulnerable with high exposure | `var(--amber)` (Amber `#f59e0b`) |
| | `MEDIUM` | Moderate shelf-life classical crypto | `var(--primary)` (Blue `#3b82f6`) |
| | `LOW` | Short-lived internal crypto | `var(--emerald)` (Green `#10b981`) |
| | `INFORMATIONAL` | PQC or documentation reference | `var(--text-muted)` (Slate `#64748b`) |
| **Confidence Level** (`confidence`) | `CONFIRMED` | Syntactically verified AST or X.509 structure | `var(--emerald)` (Solid Green) |
| | `HIGH` | Specific API call with explicit parameters | `var(--cyan)` (Cyan) |
| | `MEDIUM` | Manifest dependency / config parameter | `var(--amber)` (Amber) |
| | `LOW` / `HEURISTIC` | Keyword or pattern association | `var(--text-muted)` (Muted Grey) |
| **Clean State Label** (`clean_state_label`) | `COMPLETE_WITH_COVERAGE_ACCOUNTING` | Scan completed with findings and coverage caveats | `var(--cyan)` |
| | `NO_FINDINGS_IN_SUPPORTED_SCOPE` | Zero findings in assessed files (never "Safe") | `var(--amber)` (Caveated Clean) |
| **Claim Type** (`claim_type`) | `ALGORITHM_USE` | Executable source-level invocation | `var(--primary)` |
| | `DEPENDENCY_REFERENCE` | Declared in package manifest | `var(--purple)` |
| | `CONFIG_PARAMETER` | TLS / cipher suite setting | `var(--cyan)` |
| | `CERTIFICATE_METADATA` | Public key / X.509 certificate | `var(--amber)` |
| **Source Kind** (`source_kind`) | `SOURCE_CODE` | Codebase files (.py, .js, .go, .c, .rs) | Code icon |
| | `MANIFEST` | Package manifests (.json, .toml, .xml) | Package icon |
| | `CONFIG` | Infrastructure config (.conf, .yaml) | Settings icon |
| | `CERTIFICATE` | Certificate stores (.pem, .crt) | Key icon |
| | `BINARY` / `CONTAINER` | Binary headers / Dockerfile | Layers icon |
| **Surface Category** (`surface`) | `SOURCE_CODE` | Assessed source code files | Progress bar cyan |
| | `PACKAGE_MANIFEST` | Assessed dependency files | Progress bar purple |
| | `CONFIGURATION` | Assessed configuration files | Progress bar blue |
| | `CERTIFICATE_STORE` | Assessed public keys and certs | Progress bar amber |
| | `UNSUPPORTED_SURFACE` | Unsupported formats (.wav, .png, .bin) | Progress bar rose / warning |

---

## 4. Spec-vs-Reality Analysis (Every Spec Page Evaluated)

Below is the exhaustive matrix comparing every data requirement across `phase_Aa.md` (Section 5) and `phase_Ab.md` (Section 4) against live backend reality.

| Page | Spec Section & Element | Backend Status | Source / Derivation Method |
|---|---|---|---|
| **Dashboard (`/`)** | Health Status Banner | **AVAILABLE** | `GET /health` (`status: "pass"`) |
| | Total Scans Count | **AVAILABLE** | `GET /api/v1/scans` (length of array) |
| | Total Assets Count | **AVAILABLE** | Sum of `asset_count` across `GET /api/v1/scans` items |
| | Avg Coverage % | **AVAILABLE** | Average of `coverage_percentage` across `GET /api/v1/scans` items |
| | Critical Risks Count | **DERIVABLE** | Not in `GET /api/v1/scans`. Must aggregate from `GET /api/v1/scans/:id` or fetch during scan |
| | Recent Scans List | **AVAILABLE** | `GET /api/v1/scans` (slice first 5) |
| **Scan Page (`/scan`)** | Upload Dropzone | **AVAILABLE** | `POST /api/v1/scans/upload` |
| | Client Upload Progress | **AVAILABLE** | Native `XMLHttpRequest.upload.onprogress` |
| | Scan Result Card | **AVAILABLE** | Return value of `POST /api/v1/scans/upload` (`asset_count`, `coverage_percentage`, `dna_hash`) |
| **Scan Detail (`/scans/:id`)** | Overview Summary | **AVAILABLE** | `GET /api/v1/scans/:scan_id` |
| | DNA Hash & Timestamp | **AVAILABLE** | `scan_detail.cryptographic_dna_hash`, `created_at` |
| | Findings Tab Table | **AVAILABLE** | `GET /api/v1/scans/:scan_id/findings` |
| | Observation Inline Detail | **AVAILABLE** | `findings.observations[]` (anchor lines, snippet, digest) |
| | Coverage Tab Report | **AVAILABLE** | `GET /api/v1/scans/:scan_id/coverage` |
| **Findings Page (`/findings`)** | Cross-Scan Aggregation | **DERIVABLE** | Loop `GET /api/v1/scans` then `GET /api/v1/scans/:id/findings` (client-side aggregation) |
| | Algorithm Distribution Chart | **DERIVABLE** | Count occurrences of `algorithm` across findings |
| | Quantum Safety Breakdown | **DERIVABLE** | Count `raw_parameters.quantum_status` across findings |
| **Risk Page (`/risk/:id`)** | Mosca Timeline ($X, Y, Z$) | **AVAILABLE** | `GET /api/v1/scans/:id/risk` (`scenario`, `context`, `risk_evaluations[].mosca_slack_years`) |
| | Scenario Sliders | **AVAILABLE** | Query params `?horizon=Z&shelf_life=X&migration=Y` on `GET /api/v1/scans/:id/risk` |
| | Risk Heatmap Matrix | **DERIVABLE** | Group `risk_evaluations[]` by `algorithm` and `urgency` |
| | Migration Backlog Table | **AVAILABLE** | `risk.backlog_items[]` (`priority`, `algorithm`, `pqc_alternative`, `recommended_action`) |
| **CBOM Page (`/cbom/:id`)** | Hierarchical Tree View | **AVAILABLE** | `GET /api/v1/scans/:id/export` (`components[]` hierarchy) |
| | Download / Copy JSON | **AVAILABLE** | `GET /api/v1/scans/:id/export` with `file-saver` |
| | Schema Validation Badge | **AVAILABLE** | `export_cbom.json` has `specVersion: "1.6"`, `bomFormat: "CycloneDX"` |
| | Multi-Scanner Reconciliation | **MISSING** | `CBOMReconciliationEngine` exists in backend, but **no REST endpoint** exposes multi-generator upload |
| **Roadmap Page (`/roadmap/:id`)**| Phased Migration Waves | **MISSING** | `DependencyRoadmapEngine` exists in backend, but **no REST endpoint** returns roadmap graph |
| | Bottlenecks & Dependencies | **MISSING** | Graph engine not connected to any `/api/v1/` route |
| **Audit Page (`/audit`)** | Verify Audit Chain | **AVAILABLE** | `GET /api/v1/workflow/audit/chain/verify` |
| | Append Audit Event | **AVAILABLE** | `POST /api/v1/workflow/audit/chain/append` |
| | Audit Event History List | **MISSING** | `verify` does not return the list of events; chain is in-memory only |
| | Production Health Panel | **AVAILABLE** | `GET /api/v1/workflow/health/production` |
| **Settings Page (`/settings`)** | Local Preferences | **AVAILABLE** | Stored in browser `localStorage` (default $Z=8, X=5, Y=2$) |

---

## 5. Findings Table 6-Column Exact JSON Path Mapping

The `FindingsTable.jsx` component requires 6 primary columns. Below is the exact path mapping to `findings.json` (from `findings.observations[]`):

| # | Spec Column | Exact JSON Path in `findings.json` | Sample Real Value | Handling / Fallback |
|---|---|---|---|---|
| **1** | **Algorithm** | `obs.algorithm` | `"RSA-2048"` | If null, use `obs.candidate_asset_id` or `"UNKNOWN"` |
| **2** | **Purpose** | `obs.purpose` | `"ASYMMETRIC"` | Formatted as title-case (e.g. "Asymmetric", "Key Exchange") |
| **3** | **Quantum Safety** | `obs.raw_parameters.quantum_status` | `"QUANTUM_VULNERABLE"` | Fallback: check algorithm against NIST PQC list |
| **4** | **Source File & Line**| `obs.relative_path` + `:` + `obs.start_line` | `"crypto_service.py:22"` | If `start_line` is null, show `"crypto_service.py"` |
| **5** | **Confidence** | `obs.confidence` | `"CONFIRMED"` | Badge with `obs.confidence_rationale` tooltip |
| **6** | **Detector** | `obs.detector_id` | `"detector-source-code-v1"` | Humanized name (e.g. "Source Code AST") |

---

## 6. Dashboard Stats Computation Formula

To populate the Dashboard Quick Stats cards from `GET /api/v1/scans`:

```javascript
// Input: scans = array from GET /api/v1/scans
const totalScans = scans.length;
const totalAssets = scans.reduce((acc, s) => acc + (s.asset_count || 0), 0);
const avgCoverage = totalScans > 0
  ? Number((scans.reduce((acc, s) => acc + (s.coverage_percentage || 0), 0) / totalScans).toFixed(1))
  : 0;

// Critical Risks:
// Since GET /api/v1/scans does not include urgency counts, the frontend can:
// Option A: Maintain a local cache of scan details fetched upon upload / inspection
// Option B: Fetch GET /api/v1/scans/:id for the latest scans
// Option C: Display the Critical Risk count for the most recent scan
```
