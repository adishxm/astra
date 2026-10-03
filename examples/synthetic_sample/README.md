# ASTRA Synthetic Sample Repository

This synthetic sample project is designed for demonstrating and validating ASTRA's end-to-end cryptographic discovery pipeline.

## Contents

| File | Type | Expected Discovery Behavior |
|---|---|---|
| `crypto_service.py` | Source Code (Python) | Detects `RSA-2048` (Quantum-Vulnerable), `AES-256` (Classical), `ML-KEM-768` (Post-Quantum), and `MD5` (Vulnerable). Verifies that comment lines mentioning DES/3DES/RC4/SHA-1 are **filtered out** to prevent false positives. |
| `package.json` | Dependency Manifest | Detects declarations of `crypto-js` and `tweetnacl`. Labeled with `ClaimType.DEPENDENCY_REFERENCE` (declared capability vs runtime call). |
| `nginx.conf` | TLS / Cipher Config | Audits TLS protocol versions (`TLSv1.2`, `TLSv1.3`) and cipher suites (`ECDHE-ECDSA-AES256-GCM-SHA384`, `ECDHE-RSA-AES128-GCM-SHA256`). |
| `sample_certificate.pem` | X.509 Certificate | Parses Subject `CN=api.hexark.internal`, Public Key Algorithm (RSA 2048-bit), validity dates, and issuer. |
| `unsupported_media.wav` | Deliberately Unsupported Format | Demonstrates **truthful coverage accounting**: explicitly counted in denominator $N_{\text{total}}$, flagged as unassessed surface ($N_{\text{assessed}} / N_{\text{total}} < 100\%$), preventing misleading "100% clean" reporting. |

## Quick Scan

Scan this directory with ASTRA CLI:
```bash
astra scan ./examples/synthetic_sample --format table
```
Or upload a packaged `.zip` of this directory to the ASTRA Web Dashboard at `http://localhost:8000`.
