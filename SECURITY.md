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

---

## Reporting a Vulnerability

If you discover a security vulnerability within ASTRA:
1. Do not open a public issue on GitHub.
2. Send a vulnerability report directly to the security team at `topasingh903811@gmail.com`.
3. Include steps to reproduce the vulnerability, sample inputs (redacted of sensitive data), and potential impact.
4. We acknowledge receipts within 48 hours and work with you on a coordinated disclosure timeline.
