# Worker 03 Phase B: Frontend Data Semantics: Purpose-Specific PQC Recommendations, Honest Category Mapping & Real Audit State

**Document:** `phase_b.md`  
**Worker:** Worker 03 (`.brain/.work/webapp/worker_03`)  
**Target Roadmap Area:** P0 — Fix the active frontend's data semantics and eliminate fake audit state  
**Target Readiness Score Impact:** +4 points on Frontend and User Workflow  
**Status:** SPECIFICATION & ARCHITECTURE PLAN COMPLETE  

---

## 1. Objectives & Executive Scope

Phase B resolves the frontend semantic errors and misleading representations highlighted in Section 3 and 4 of the Fresh Product Assessment:
1. **Eliminate `undefined` Category in Active Dashboard:**
   - In `frontend/index.html`, inventory rows map `obs.category`, which does not exist on the canonical evidence model.
   - Refactor the table mapper to extract `obs.claim_type || obs.purpose || obs.source_kind || 'CRYPTOGRAPHIC_PRIMITIVE'`.
2. **Purpose-Specific PQC & Modernization Recommendations (Eliminate Universal ML-KEM Fallback):**
   - The current dashboard fallback mapped `ML-KEM / FIPS 203` to every algorithm, including hashes (MD5), symmetric ciphers (AES), and TLS versions.
   - Wire the frontend adapter to read the typed `recommendation.target_standard_algorithm` and `recommendation.target_standard_ref` directly from the backend's `risk_evaluations`.
   - Implement accurate purpose-specific mappings when generating local recommendations:
     - **Key Exchange / Encapsulation (KEX/KEM)**: RSA KEM, ECDH, X25519 $\rightarrow$ `ML-KEM-768 (NIST FIPS 203)`
     - **Digital Signatures**: RSA-PSS, RSA sign, ECDSA, Ed25519 $\rightarrow$ `ML-DSA-65 (NIST FIPS 204)` or `SLH-DSA-SHA2-128s (NIST FIPS 205)`
     - **Cryptographic Hashes**: MD5, SHA-1 $\rightarrow$ `SHA-256 / SHA-3 (NIST FIPS 202)` (Modernization, NOT KEM!)
     - **Symmetric Encryption**: AES-128, 3DES, RC4 $\rightarrow$ `AES-256-GCM (NIST SP 800-38D)` for Grover 128-bit quantum security margin
     - **Transport Protocols**: SSLv3, TLSv1.0, TLSv1.1 $\rightarrow$ `TLSv1.3 with Hybrid PQC (RFC 8446 / RFC 9370)`
3. **Replace Seeded Demo Audit View with Active Scan Audit Trail:**
   - The active dashboard hardcodes past demo events claiming 182/192 files.
   - Replace this with live, verified audit events fetched from the backend (`GET /api/v1/workflow/audit/chain/verify` and scan timeline), reflecting the actual files, findings, and cryptographic hashes of the current scan.
4. **Synchronize Dashboard Metrics & Test Badges:**
   - Update header status counters in `frontend/index.html` to reflect live repository metrics.

---

## 2. Technical Deliverables

| Deliverable | File | Target Behavior |
|---|---|---|
| **Active Dashboard HTML / JS Mapper** | `frontend/index.html` | Map category cleanly, read typed backend recommendation, eliminate universal ML-KEM fallback, generate real scan audit trail. |
| **PQC Algorithm Mapping Ruleset** | `frontend/index.html` & `backend/app/risk/taxonomy.py` | Distinguish KEM, Signatures, Hashes, Symmetric, and TLS protocols. |
| **Phase B Automated Test Suite** | `backend/tests/test_worker03_phase_b_frontend_semantics.py` | Verify that the HTML adapter logic correctly differentiates KEM vs Signature vs Hash vs Symmetric recommendations. |
| **Phase B Completion Report** | `.brain/.work/.report/worker03_phase_b_report.md` | Standardized audit report documenting all implementation details and verification results. |

---

## 3. Test Strategy & Acceptance Gates

- **Test B.1:** Assert inventory row categories never evaluate to `undefined` for any observation type.
- **Test B.2:** Assert MD5 and SHA-1 yield SHA-256 / SHA-3 modernization recommendations, NOT ML-KEM.
- **Test B.3:** Assert AES-128 yields AES-256-GCM recommendation, NOT ML-KEM.
- **Test B.4:** Assert RSA signatures yield ML-DSA-65 or SLH-DSA-128, NOT ML-KEM.
- **Test B.5:** Assert RSA encryption / ECDH yields ML-KEM-768.
- **Test B.6:** Assert audit trail reflects the current uploaded scan ID and file counts, not hardcoded 182/192 demo state.
