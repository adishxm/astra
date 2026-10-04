# Cryptographic Drift & Determinism Observation Notes

**Target Tested:** `examples/synthetic_sample/`  
**Run 1 Scan ID:** `scan-cf529d73`  
**Run 2 Scan ID:** `scan-26f13bd1`  

## 1. Cryptographic DNA Hash Stability
- **Run 1 DNA Hash:** `edcb54e8c8b2e04a1380807d36d5b7a43ca3c25f4cff275073214177e8a67875`
- **Run 2 DNA Hash:** `edcb54e8c8b2e04a1380807d36d5b7a43ca3c25f4cff275073214177e8a67875`
- **Identical / Deterministic:** `True`

## 2. Findings & Inventory Comparison
| Metric | Run 1 (`scan-cf529d73`) | Run 2 (`scan-26f13bd1`) | Delta |
|---|---|---|---|
| Total Files | 6 | 6 | 0 |
| Assessed Files | 4 | 4 | 0 |
| Coverage % | 57.14% | 57.14% | 0.0% |
| Canonical Assets | 16 | 16 | 0 |
| Observations | 16 | 16 | 0 |
| Clean State Label | `COMPLETE_WITH_COVERAGE_ACCOUNTING` | `COMPLETE_WITH_COVERAGE_ACCOUNTING` | Unchanged |

## 3. Drift Analysis Observation
1. **Determinism:** The Cryptographic DNA SHA-256 hash is 100% deterministic across identical codebase uploads. The tokenization sorts assets by `asset_id` and normalized algorithm names/key sizes, guaranteeing stable fingerprinting.
2. **Scan Record Isolation:** Each upload creates a fresh `scan_id` (`scan-<8-hex>`) stored independently in `GLOBAL_SCAN_STORE`.
3. **Temporal Drift API Gap:** The backend contains a robust `TemporalLineageEngine` (`app.inventory.temporal`) capable of computing `CryptographicDrift` deltas (added, removed, modified, downgraded), but **no REST endpoint currently exposes `detect_drift(prior, current)`**. If two scans exist in `GET /api/v1/scans`, the frontend must either compute drift client-side from the two scan details or request a new backend route `POST /api/v1/scans/drift`.
