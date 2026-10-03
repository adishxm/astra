# ASTRA Frontend Dashboard

The ASTRA Cryptographic Discovery & Post-Quantum Governance Dashboard provides an intuitive, high-performance interface for discovering cryptographic assets, visualizing Mosca inequality horizons ($X+Y>Z$), inspecting Post-Quantum Cryptography (PQC) migration pathways, examining cryptographic DNA fingerprints, and generating CycloneDX 1.6 Cryptographic Bills of Materials (CBOM).

## Features

- **Provenance-Aware Inventory**: View detected cryptographic algorithms, key lengths, curves, implementations, line numbers, and file provenance.
- **Interactive Mosca Inequality Horizon**: Real-time slider adjusting migration timelines ($Y$) and threat horizons ($Z$), recalculating quantum vulnerability deadlines dynamically.
- **PQC Migration Backlog**: Direct mapping from classical algorithms (RSA, ECC, Diffie-Hellman) to FIPS 203 (ML-KEM), FIPS 204 (ML-DSA), and FIPS 205 (SLH-DSA).
- **CycloneDX 1.6 CBOM**: Export industry-standard cryptographically validated bill of materials with one-click JSON clipboard copy or download.
- **Cryptographic DNA Fingerprint**: SHA-256 state and policy fingerprinting for immutable change detection across build cycles.
- **Tamper-Evident Audit Trail**: SHA-256 hash-chained verification log tracking every discovery, assessment, and export action.

## Running the Dashboard

### 1. Embedded Mode (Default & Recommended)
The frontend is embedded within the ASTRA FastAPI backend and served directly at root:
```bash
# Start backend and frontend simultaneously:
astra serve
# or
uvicorn app.main:app --host 0.0.0.0 --port 8000
```
Then navigate to: **`http://localhost:8000`**

### 2. Standalone Mode (Vite Development Server)
To run or develop the frontend independently:
```bash
cd frontend
npm install
npm run dev
```
By default, the UI communicates with the backend REST API on `http://localhost:8000/api/v1`.
