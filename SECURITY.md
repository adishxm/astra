# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

---

## Zero-Secret Guarantee & Security Guarantees

ASTRA is built with strict boundary security principles:
1. **Zero Private Key Storage**: Any detected private keys (`BEGIN RSA PRIVATE KEY`, `BEGIN PRIVATE KEY`, etc.) are intercepted immediately, masked as `[REDACTED_PRIVATE_KEY_MATERIAL]`, and flagged with `redacted = True`. No private key bytes are ever stored in manifests, observations, or database records.
2. **Decompression Bomb Protection**: Input archives are monitored during extraction with strict single-file (50 MB) and cumulative (500 MB) expansion limits and a 100:1 compression ratio cutoff (`AC-02`).
3. **Sandbox Isolation**: Files are extracted to ephemeral, isolated sandbox directories and locked down with read-only permissions before analysis. Symlinks pointing outside extraction targets are strictly rejected.
4. **Denial-of-Service Defenses**: Path traversal (`../`), null bytes (`\0`), and Windows absolute paths are normalized and blocked prior to filesystem operations.
5. **Safe Local Loopback Defaults**: CLI and development server bind exclusively to `127.0.0.1` by default. Active security warnings are emitted if binding to `0.0.0.0` without authentication.
6. **Hosted Mode Protection (`ASTRA_HOSTED_MODE=1`)**: When deployed in public demo mode, arbitrary local filesystem scanning (`POST /api/v1/scans/directory`) is disabled (`HTTP 403 Forbidden`). Only isolated sandboxed archive uploads are accepted.
7. **API Token Authentication**: Configurable via `ASTRA_API_KEY`, enforcing token validation (`X-ASTRA-API-KEY` or `Authorization: Bearer <key>`) on all mutating endpoints.
8. **Upload Quota Enforcement**: Maximum archive upload size is strictly capped at 50 MB (configurable via `ASTRA_MAX_UPLOAD_SIZE_BYTES`) with chunked stream monitoring rejecting oversized requests with `HTTP 413`.
9. **Formal Threat Model**: Full STRIDE analysis and trust boundary architecture is documented in [.brain/.work/threat_model.md](.brain/.work/threat_model.md).
10. **Server-Derived Principal Isolation**: A valid `ASTRA_API_KEY` maps to a single server-configured principal (`ASTRA_DEFAULT_TENANT_ID` / `ASTRA_DEFAULT_USER_ID`). Untrusted client request headers (`X-Tenant-ID`, `X-User-ID`) are strictly ignored and cannot override principal identity or access scope.

---

## Reporting a Vulnerability

If you discover a security vulnerability within ASTRA:
1. Do not open a public issue on GitHub.
2. Send a vulnerability report directly to the security team at `parinidhijain101@gmail.com`.
3. Include steps to reproduce the vulnerability, sample inputs (redacted of sensitive data), and potential impact.
4. We acknowledge receipts within 48 hours and work with you on a coordinated disclosure timeline.
