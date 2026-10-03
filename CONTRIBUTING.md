# Contributing to ASTRA (SIH26164 ECDAT)

Thank you for your interest in contributing to **ASTRA**!

## Architecture & Phased Workflow

ASTRA is developed according to a strict multi-worker, phased architecture defined in `.brain/.work/`:
- **Worker 01**: Safe Upload Intake, Boundary Sandbox, Deterministic Discovery & Coverage Accounting (`app.intake`, `app.discovery`, `app.coverage`).
- **Worker 02**: Canonical Evidence Modeling, Deduplication, Identity Graph & CycloneDX 1.6 CBOM Projection (`app.inventory`).
- **Worker 03**: Contextual Risk Engine, Mosca Theorem Evaluation ($X + Y > Z$), Dated NIST PQC Taxonomy & Migration Backlog (`app.risk`).
- **Worker 04**: Workflow Orchestrator, Review Audits, Scenario Slider UI & Packaging (`app.api`, `frontend`).

---

## Development Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/adishxm/astra.git
   cd astra
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Linux / macOS
   .\venv\Scripts\activate   # On Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run test suite**:
   ```bash
   pytest
   ```

---

## Coding Standards

- **Strict Type Annotations**: All function signatures must include Python type hints.
- **Explainable Decisions**: Never use opaque constants or unsupported machine learning guesses for cryptographic risk scores. All risk weights, Mosca horizon parameters, and reason codes must be traceable and deterministic.
- **Zero-Secret Invariant**: Detectors and intake modules must never persist private keys or unredacted authentication tokens.
- **Coverage Transparency**: A scan finding zero cryptographic assets must be reported as `NO_FINDINGS_IN_SUPPORTED_SCOPE` alongside explicit denominator metrics—never labeled as "Safe" or "Compliant".
