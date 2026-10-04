# ASTRA Threat Model & Deployment Security Architecture

**Application:** ASTRA (Enterprise Cryptographic Discovery & Post-Quantum Analysis Tool)  
**Problem Statement:** SIH26164 (ECDAT) — Team HEXARK  
**Specification Version:** 1.0.0  
**Date:** 2026-10-04  

---

## 1. System Overview & Architecture

ASTRA is an enterprise cryptographic discovery and inventory tool designed to execute both in **air-gapped sovereign environments** (default local CPU operation) and in **managed hosted demo environments**. It inspects source code, dependency manifests, TLS configurations, X.509 certificates, OCI container layers, and network endpoints to construct a CycloneDX 1.6 Cryptographic Bill of Materials (CBOM) and calculate quantum risk horizons using the Mosca theorem ($X + Y > Z$).

```
[ External User / CI/CD ]
         │
         ▼  (HTTP / API Token / Loopback)
┌────────────────────────────────────────────────────────┐
│  ASTRA API Gateway (FastAPI / Uvicorn)                 │
│  - Loopback Binding: 127.0.0.1:8000 (Default)          │
│  - Hosted Mode Gate: ASTRA_HOSTED_MODE=1               │
│  - API Token Gate: X-ASTRA-API-KEY / Bearer Auth       │
│  - Streaming Payload Limit: 50 MB Max                  │
└──────────────────────────┬─────────────────────────────┘
                           │
         ┌─────────────────┴─────────────────┐
         ▼                                   ▼
┌─────────────────────────────┐   ┌─────────────────────────────┐
│ Archive Intake Sandbox      │   │ Authorized Network Guard    │
│ - Path Traversal Normalizer │   │ - Loopback/Allowlist check  │
│ - 100:1 Zip Bomb Defense    │   │ - Simulated/Live TLS Probe  │
│ - Read-Only Temp Sandbox    │   │ - 4-Plane Separation        │
└──────────────┬──────────────┘   └──────────────┬──────────────┘
               │                                 │
               └────────────────┬────────────────┘
                                ▼
┌────────────────────────────────────────────────────────┐
│ Cryptographic Discovery Engine (Worker 01)             │
│ - Source AST & Token Detector                          │
│ - Manifest Dependency Detector                         │
│ - Config & Infrastructure Detector                     │
│ - Certificate & Key Redactor (Zero Secret Storage)     │
│ - OCI Container Manifest & Layer Archive Detector      │
└──────────────────────────┬─────────────────────────────┘
                           │ Observations
                           ▼
┌────────────────────────────────────────────────────────┐
│ Inventory & CBOM Reconciliation Engine (Worker 02)     │
│ - Deterministic Asset ID Mapping                       │
│ - CycloneDX 1.6 CBOM Formulation                       │
│ - Temporal Lineage & Drift Hash Tracking               │
└──────────────────────────┬─────────────────────────────┘
                           │ Canonical Assets
                           ▼
┌────────────────────────────────────────────────────────┐
│ Risk & PQC Migration Engine (Worker 03)                │
│ - Mosca Theorem Horizon Dynamic Calculator             │
│ - Owner-Supplied Context Enrichment                    │
│ - NIST FIPS 203/204/205 & NSA CNSA 2.0 Catalog         │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│ Local Store & Tamper-Evident Audit Chain (Worker 04)   │
│ - Local Disk JSON Storage (data/scans/)                │
│ - SHA-256 Hash Chained Audit Log                       │
│ - Offline Air-Gapped Verification Bundle               │
└────────────────────────────────────────────────────────┘
```

---

## 2. Trust Boundaries

1. **Boundary 1: External Client to API Gateway**
   - Untrusted input: HTTP requests, JSON payloads, uploaded archives.
   - Mitigations: Loopback default (`127.0.0.1`), strict API key verification (`X-ASTRA-API-KEY`), 50MB payload quota, CORS origin restriction.
2. **Boundary 2: Archive Intake & Sandbox**
   - Hostile archive payloads (tar slips, zip bombs, symlink escapes).
   - Mitigations: Path normalization, rejection of symlinks resolving outside target directory, 100:1 compression ratio cutoff, 500MB cumulative limit.
3. **Boundary 3: Filesystem & Discovery Inspection**
   - Private key files (`.pem`, `.key`) and embedded secrets in source code.
   - Mitigations: Automatic zero-storage redaction (`[REDACTED_PRIVATE_KEY_MATERIAL]`), secret snippet masking (`[REDACTED_SECRET]`), strictly excluding key bytes from persistence.
4. **Boundary 4: Server Filesystem Integrity (Hosted Mode)**
   - Arbitrary server directory scanning (`POST /api/v1/scans/directory`).
   - Mitigations: In hosted mode (`ASTRA_HOSTED_MODE=1`), direct directory scanning is rejected with HTTP 403; only sandboxed archive uploads are accepted.
5. **Boundary 5: External Hardware & Managed Boundaries**
   - Cloud Key Management Services (AWS KMS, Azure Key Vault, Google Cloud KMS) and Hardware Security Modules (PKCS#11).
   - Policy: Explicitly classified as external hardware-dependent boundaries; ASTRA analyzes client code and configuration referencing them, but does not extract hardware-locked keys.

---

## 3. STRIDE Threat Analysis Matrix

| Threat Category | Potential Attack Vector | Impact | ASTRA Mitigation Controls |
|---|---|---|---|
| **Spoofing** | Unauthorized user manipulates scan context or initiates scans. | High | Optional API token authentication (`ASTRA_API_KEY`) enforced via `verify_api_key` dependency on all mutating endpoints. |
| **Tampering** | Malicious alteration of historical scan records or CBOM output. | Critical | SHA-256 cryptographic DNA hashing of inventory and SHA-256 tamper-evident audit event hash chaining (`TamperEvidentAuditChainer`). |
| **Repudiation** | Operator denies overriding algorithm risk ratings or modifying context. | Medium | Tamper-evident audit chain logging operator ID, action, timestamp, and justification reason (`POST /api/v1/workflow/audit/chain/append`). |
| **Information Disclosure** | Exposure of RSA/ECC private keys or credentials in scan reports. | Critical | Zero-Secret policy: `CertificateCryptoDetector` masks private key bytes before observation creation; source detector masks passwords and tokens. |
| **Denial of Service** | Uploading recursive zip bomb or multi-gigabyte file to exhaust memory. | High | 50MB max upload size limit (`HTTP 413`), chunked disk streaming without loading whole archive into RAM, 100:1 expansion ratio cutoff. |
| **Elevation of Privilege** | Attacker accesses `/etc` or `C:\Windows` via directory scan endpoint in public demo. | Critical | `ASTRA_HOSTED_MODE=1` disables `POST /api/v1/scans/directory` (`HTTP 403 Forbidden`). Only isolated sandboxed archive uploads are allowed. |

---

## 4. Operational Modes & Safe Defaults

| Feature | Local Sovereign Mode (Default) | Hosted Demo Mode (`ASTRA_HOSTED_MODE=1`) |
|---|---|---|
| **HTTP Host Binding** | `127.0.0.1` (Loopback only) | Specified host or reverse-proxy |
| **Directory Scanning** | Enabled (`POST /api/v1/scans/directory`) | **Disabled (HTTP 403)** |
| **Archive Upload** | Enabled (50MB limit) | Enabled (50MB limit + Auth) |
| **API Authentication** | Optional (enabled if `ASTRA_API_KEY` set) | Recommended / Enforced |
| **CORS Policy** | `*` without credentials (safe local) | Restricted via `ASTRA_CORS_ORIGINS` |
| **External Telemetry** | Completely Disabled | Completely Disabled |
