# ASTRA Frontend — P09 Implementation Notes

## Phase: P09 — Cryptographic Bill of Materials (CBOM)
**Date:** October 2026  
**Role:** Worker 01 (Frontend)  
**Branch:** `feat/frontend-p09-cbom`

---

## 1. Executive Summary & Scope
Phase P09 delivers the frontend presentation of the project's **Cryptographic Bill of Materials (CBOM)** aligned with the **CycloneDX 1.6 Cryptographic Properties Standard** and canonical asset inventory contracts.

### Core Deliverables Built:
1. **CBOM Summary / Overview (`CbomSummary`)**:
   - Total cryptographic assets count, unique algorithms count, cryptographic purpose count, and specification standards.
   - Surface breakdown indicators (`SOURCE_CODE`, `CONFIG`, `MANIFEST`, `CERTIFICATE`, `UNKNOWN`).
   - Explicit **Cryptographic Truthfulness Notice** distinguishing structural inventory from risk severity (P08) and migration planning (P10).
2. **Algorithm Classification Matrix (`CbomAlgorithmMatrix`)**:
   - Categorizes cryptographic primitives into standard functional families (e.g., *Post-Quantum & Key Encapsulation*, *Public Key & Asymmetric Cryptography*, *Symmetric Block & Stream Ciphers*, *Cryptographic Hash Functions*, *Transport Security Protocols*).
   - Shows instance counts, parameter sets, and discovery surfaces per algorithm.
3. **Cryptographic Inventory Table (`CbomInventoryTable`)**:
   - Tabular accounting of all cryptographic component instances.
   - Columns: Algorithm & Canonical Asset, Purpose, Source Location & Line Numbers, Parameters (Key size, curve, parameter set identifier), Confidence & Assessment State, and Actions.
   - Interactive client-side multi-field deterministic search.
   - Filters: Cryptographic Purpose, Discovery Surface, and Detection Confidence.
   - Dynamic sorting across all documented columns with accessible direction toggling.
   - Accessible pagination with page size controls.
4. **Component Detail Modal (`CbomDetailModal`)**:
   - In-depth inspection of CycloneDX 1.6 properties (`assetType`, `parameterSetIdentifier`, `executionEnvironment`, `keySizeBits`, `curveName`).
   - Discovery provenance: Surface kind, claim type, file path, line numbers, detector engine, ruleset version, and SHA-256 evidence digest.
   - Sanitized source evidence viewer.
   - CycloneDX 1.6 JSON representation generator and 1-click clipboard copy.
5. **CycloneDX 1.6 Export Modal (`CbomExportModal`)**:
   - Full live integration with `GET /api/v1/scans/{scan_id}/export?format=cyclonedx`.
   - Real-time JSON preview, copy-to-clipboard, and direct file download (`astra-cbom-<scanId>.json`).
6. **Dedicated CBOM Route & Scan Detail Integration (`/cbom` & `ScanDetailPage`)**:
   - Standalone `/cbom` page with scan selector, loading, error, and empty states.
   - Seamless CBOM Tab inside `ScanDetailPage` alongside Summary, Findings, Coverage, and Risk.

---

## 2. API Contract & Data Normalization

All CBOM components derive deterministically from the documented backend contract:
- `GET /api/v1/scans`: Available scans list.
- `GET /api/v1/scans/{scan_id}`: Full scan payload including `canonical_assets`, `observations`, `coverage_gaps`, and `risk_summary`.
- `GET /api/v1/scans/{scan_id}/export?format=cyclonedx`: Official CycloneDX 1.6 BOM artifact with cryptographic extensions.

### Normalization Pipeline (`normalizeCbomInventory`):
```text
Canonical Assets + Direct Observations + CycloneDX Export
                     │
                     ▼
       Standardized CBOM Inventory Record
  ├── Component Name / Canonical Asset ID
  ├── Algorithm Name & Functional Family
  ├── Declared Purpose (ASYMMETRIC, SYMMETRIC, HASHING, KEY_EXCHANGE, etc.)
  ├── CycloneDX Properties (assetType, parameterSetIdentifier, executionEnvironment)
  ├── Cryptographic Parameters (keySizeBits, curveName, parameterSetIdentifier)
  ├── Discovery Provenance (sourceKind, claimType, relativePath, lines, detectorId, rulesetVersion)
  ├── Confidence Rating & Rationale
  ├── Sanitized Source Code Excerpt
  └── Evidence Digest (SHA-256)
```

---

## 3. Cryptographic Truthfulness & Strict Boundary Enforcement

In strict compliance with **P09 Rule #9 (Cryptographic Truthfulness)**:
- **Inventory ≠ Risk:** The CBOM UI makes zero claims that an algorithm's inclusion implies insecurity or compliance.
- **Visual Separation:** Risk metrics (composite scores, urgency, Mosca theorem $X+Y>Z$) belong strictly to P08 (`/risk`), while cryptographic migration belongs to P10 (`/migration`).
- **Prominent Banner:** A dedicated truthfulness banner is rendered on both `/cbom` and the scan detail CBOM tab.

---

## 4. Sensitive Data Sanitization

- Raw private keys, credentials, plaintext secret tokens, and unsanitized buffer dumps are never exposed.
- All evidence snippets utilize the `sanitized_excerpt` pipeline with strict non-interactive code rendering.

---

## 5. Verification Results

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
- **42 test files passed** (100%)
- **165 tests passed** (100%)
- **Statement / Line Coverage:** **92.28%** (exceeds >90% requirement across all components)

### 3. Production Build
```powershell
npm.cmd run build
```
**Result:** Clean Vite production bundle generated in `dist/` (8.21s).

### 4. Backend Pytest Suite
```powershell
& ".venv\Scripts\python.exe" -m pytest backend/tests -q
```
**Result:** **88/88 passed** (0 regressions, 0 backend files modified).

---

## 6. Limitations & Future Work (P10)
- Cryptographic migration recommendations and algorithm deprecation roadmaps belong to **P10 (Migration Strategy)**.
- CBOM export formats currently support JSON CycloneDX 1.6 as provided by the backend API.
