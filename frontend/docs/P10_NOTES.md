# ASTRA Frontend — P10 Implementation Notes

## Phase: P10 — Migration Planning & Recommendations
**Date:** October 2026  
**Role:** Worker 01 (Frontend)  
**Branch:** `feat/frontend-p10-migration`

---

## 1. Executive Summary & Scope
Phase P10 delivers the frontend representation of **Actionable, Dependency-Aware Post-Quantum Cryptographic Migration Planning and Recommendations** for ASTRA.

### Key Deliverables Implemented:
1. **Migration Summary & Overview (`MigrationSummary`)**:
   - Total migration recommendations count, affected unique assets count, urgent items count (`CRITICAL` + `HIGH`), standardized PQC target candidates count, and architecture review status breakdown (`OPEN`, `IN_REVIEW`, `ACCEPTED`, `COMPLETED`).
   - Prominent **No Automatic Remediation Notice** (P10 Rule #6 & #7): Explicitly clarifies that all recommendations are advisory candidate mappings requiring environmental benchmarking (latency, key size expansion, packet MTU fragmentation) and confirms zero automated code/key changes occur.
2. **Dependency-Aware Phased Migration Roadmap (`MigrationRoadmapView`)**:
   - Visualizes topological phased migration execution:
     - **Phase 1: Foundational Cryptographic Libraries & Trust Anchors** (Prerequisite libraries, package manifests, certificates, and legacy hash replacement).
     - **Phase 2: Core Platform Services & Internal Gateways** (TLS ingress proxy configurations, cipher suites, KEM key encapsulation).
     - **Phase 3: Application-Level & Edge Cryptographic Endpoints** (Application-level asymmetric encryption, digital signatures, and proprietary calls).
   - Interactive phase cards with engineer-day effort estimates and unblocked component metrics.
3. **Migration Recommendation Table (`MigrationTable`)**:
   - Tabular presentation mapping classical algorithms to standardized NIST PQC replacements (`ML-KEM-768`, `ML-DSA-65`, `SLH-DSA`, `SHA-256/3-256`) and hybrid interim pathways.
   - Deterministic client-side multi-field search (current algorithm, target algorithm, hybrid pathway, asset ID, file location, dated standard authority, recommended action).
   - Filters: Urgency / Priority (`ALL`, `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, `INFORMATIONAL`), Status (`ALL`, `OPEN`, `IN_REVIEW`, `ACCEPTED`), and Declared Purpose.
   - Column sorting with accessible direction indicators and pagination controls.
4. **Recommendation Detail Modal (`MigrationDetailModal`)**:
   - Header transition flow: Observed Classical Algorithm $\to$ Recommended Post-Quantum Target.
   - Actionable recommendation text and interim hybrid pathways.
   - Operational Caveats & Engineering Constraints (bulleted list of key size expansions, MTU fragmentation alerts, and performance overhead).
   - Discovery provenance: Canonical Asset ID, file location with exact line numbers, review owner, task ID, and assigned reason codes.
   - Cross-cutting navigation links connecting the task to **Risk Assessment** (`/risk`), **CBOM Inventory** (`/cbom`), and **Source Evidence** (`/scans/{scanId}`).
5. **Dedicated Migration Route & Scan Detail Integration (`/migration`, `/roadmap`, & `ScanDetailPage`)**:
   - Dedicated `/migration` route with scan picker dropdown, loading, error, and empty states.
   - Migration Plan Tab embedded seamlessly inside `ScanDetailPage`.
   - Sidebar navigation item (`/migration`) with `GitFork` icon.

---

## 2. API Contract & Data Model Alignment

All migration items derive from the backend contract:
- `GET /api/v1/scans`: Scans list.
- `GET /api/v1/scans/{scan_id}`: Full scan payload including `backlog_items`, `canonical_assets`, `risk_evaluations`, and `coverage`.
- `GET /api/v1/scans/{scan_id}/risk`: Mosca risk scenarios with updated `backlog_items`.

### Migration Task Model (`MigrationTask`):
```json
{
  "task_id": "mig-2e42289f",
  "asset_id": "md5-crypto_service.py-42",
  "relative_path": "crypto_service.py",
  "start_line": 42,
  "current_algorithm": "MD5",
  "purpose": "HASHING",
  "priority": "CRITICAL",
  "composite_risk_score": 76.31,
  "mosca_deadline_passed": false,
  "target_pqc_algorithm": "SHA-256 (NIST FIPS 180-4) or SHA3-256 (NIST FIPS 202)",
  "target_hybrid_algorithm": null,
  "dated_standard_ref": "NIST FIPS 180-4 / FIPS 202",
  "compatibility_gaps": [
    "Digest size increases from 128 bits to 256 bits; database schema adjustment required"
  ],
  "recommended_action": "Migrate all MD5 hash and HMAC usages to SHA-256 or SHA3-256",
  "review_owner": "Security Architecture & Crypto Team",
  "status": "OPEN",
  "recommendation_type": "CANDIDATE_OPTION_FOR_HUMAN_REVIEW",
  "operational_benchmarking_caveat": "Advisory candidate mapping from NIST standards. Requires deployment-specific benchmarking for latency/cost/bandwidth fit before migration.",
  "reason_codes": ["RC_ALGORITHM_BROKEN_LEGACY"]
}
```

---

## 3. Strict Confirmation: No Automatic Remediation

In strict adherence to **P10 Rule #6 (No Automatic Remediation)** and **Rule #7 (Recommendation Honesty)**:
- **Zero Automated Code Execution:** The frontend does **NOT** edit source code, modify server configuration files, rotate encryption keys, replace certificates, or execute automated shell/migration commands.
- **Pure Advisory Presentation:** The UI serves solely as a strategic, dependency-ordered planning and review interface for security architects and engineering teams.
- **Truthful Urgency:** Urgency ratings are strictly rendered as supplied by the backend contract; unassessed items remain neutral and are never artificially converted to `LOW`.

---

## 4. Cross-Cutting Architectural Relationships

The migration interface provides bidirectional navigation across all architectural layers:
```text
Migration Recommendation (/migration)
       ├── 🔗 Risk Assessment (/risk?scanId=...)
       ├── 🔗 CBOM Inventory (/cbom?scanId=...)
       └── 🔗 Source Evidence (/scans/{scanId})
```

---

## 5. Verification & Test Results

### 1. ESLint Check
```powershell
npm.cmd run lint
```
**Result:** 0 errors, clean check.

### 2. Unit & Integration Test Suite
```powershell
npm.cmd test -- --coverage
```
**Result:**
- **47 test files passed** (100%)
- **190 tests passed** (100%)
- **Statement / Line Coverage:** **92.81%** (exceeds >90% benchmark)

### 3. Production Build
```powershell
npm.cmd run build
```
**Result:** Clean production bundle compiled in `dist/` (7.91s).

### 4. Backend Pytest Suite
```powershell
& ".venv\Scripts\python.exe" -m pytest backend/tests -q
```
**Result:** **88/88 passed** (0 backend files modified, zero regressions across P05–P09).

---

## 6. Limitations & Notes
- Migration task prioritization reflects current NIST FIPS 203/204/205 standards and scenario assumptions ($X+Y>Z$).
- Custom context enrichment is simulated dynamically via the Risk Prioritization interface.
