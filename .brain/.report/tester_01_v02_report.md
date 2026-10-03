# Functional Assurance Report — Tester 01 Cycle V02: Risk, Migration Queue, and User Journey E2E

- **Date:** 2026-10-03
- **Owner:** Functional Assurance Planner / Tester 01
- **Validation Cycle:** V02
- **Status:** **VALIDATED & SIGNED OFF**
- **Research / Acceptance Mapping:** Worker 03 (MVP-01, MVP-02, MVP-03) & Worker 04 (MVP-01, MVP-02, MVP-03); AC-07–AC-10, AC-12, AC-15–AC-18; Trace IDs R01–R08, R12, R14.
- **Test Suite:** `backend/tests/test_functional_assurance/test_v02_e2e_journey.py` + Worker 03 & Worker 04 test suites (20 tests total in V02 scope).

---

## 1. Executive Summary

Tester 01 conducted end-to-end integration and user journey testing across the contextual risk scoring engine, Mosca Theorem deadline evaluations, actionable post-quantum migration backlog generator, timeline scenario sensitivity analysis, and the web workflow API endpoints (evidence drill-down, review audit logging, and CBOM export).

**Outcome:** 100% of test scenarios passed (20/20 in V02 scope, 50/50 overall). All acceptance criteria AC-07 through AC-10, AC-12, and complete-product gate criteria AC-15 through AC-18 are verified and satisfied. Zero blocking defects exist.

---

## 2. Validation Scope & Executed Test Cases

### 2.1 Contextual Risk Model & Mosca Theorem (AC-07)
- **Mosca Theorem Deadline Math ($X + Y > Z$):**
  - Evaluated condition where required secrecy duration ($X$) + migration duration ($Y$) exceeds the quantum threat horizon ($Z$).
  - When $X + Y > Z$, the system flags `mosca_condition_violated = True` and elevates urgency to `CRITICAL`.
  - When $X + Y \le Z$, positive safety margin (slack) is preserved, avoiding false alarm inflation.
- **Broken Algorithm Override:** Legacy broken ciphers (DES, 3DES, RC4, MD5, SHA-1) are unconditionally flagged as `CRITICAL` regardless of operational lifetime or horizon.
- **Factor Contribution Transparency:** Risk scores break down contributions from quantum vulnerability, exposure scope (local to public-facing), business criticality (development to mission-critical), and data retention.

### 2.2 NIST-Standardized Post-Quantum Migration Backlog (AC-08)
- **Candidate PQC Mapping:** Verified dated authority citations for all algorithm categories:
  - Classical asymmetric encryption/KEM (RSA, DH) $\rightarrow$ ML-KEM (FIPS 203).
  - Classical digital signatures (RSA-PSS, ECDSA, Ed25519) $\rightarrow$ ML-DSA (FIPS 204) and SLH-DSA (FIPS 205).
  - Classical symmetric (AES-128) $\rightarrow$ AES-256 (Grover's algorithm defense).
  - Already-PQC algorithms (ML-KEM, Falcon) $\rightarrow$ `INFORMATIONAL` status (no action required).
- **Caveats & Operational Gaps:** Verified that migration candidates document real-world operational trade-offs (public key size expansion, signature byte overhead, hybrid transition requirements).
- **Backlog Prioritization:** Verified that the backlog sorts work items in strictly descending order of composite risk score, placing critical Mosca violations and broken ciphers at the top.

### 2.3 Scenario Sensitivity & Alert Fatigue Reduction (AC-10, AC-12)
- **Interactive Horizon Slider:** Shifting the CRQC horizon from 15 years to 5 years dynamically escalates long-lived assets to `CRITICAL` with explainable reason codes.
- **Alert Fatigue Reduction:** Compared to a flat-severity baseline (which naively marks every classical cipher as critical), ASTRA’s contextual model reduces developer alert fatigue by filtering out low-exposure, ephemeral test fixtures while prioritizing mission-critical partner gateways.

### 2.4 Complete End-to-End User Journey (AC-15, AC-16, AC-17, AC-18)
- **Seamless Pipeline Integration:** Verified the unbroken data flow:
  $$\text{Archive Upload} \longrightarrow \text{Extraction} \longrightarrow \text{Discovery Observations} \longrightarrow \text{Canonical Evidence} \longrightarrow \text{Contextual Risk} \longrightarrow \text{Migration Backlog} \longrightarrow \text{Audit Action} \longrightarrow \text{CBOM Export}$$
- **Web Workflow Endpoints:**
  - `GET /api/v1/workflow/evidence/{asset_id}`: Retrieves evidence drill-down without data loss.
  - `POST /api/v1/workflow/audit`: Successfully registers reviewer override decisions; enforces mandatory review reason (HTTP 400 on empty string); normalizes unauthenticated actor access safely.
  - `GET /api/v1/workflow/export`: Emits sanitized `InventoryExport` containing assets, relationships, and audit trail under the `Astra Project Export Draft` profile.

---

## 3. Complete-Product Gate Verification

| Acceptance ID | Requirement | Test Verification | Status |
|---|---|---|---|
| **AC-07** | Transparent risk model & Mosca calculations | `test_mosca_deadline_violation_triggers_critical_urgency`, `test_mosca_theorem_sensitivity_and_slack_dynamics` | **PASSED** |
| **AC-08** | Dated PQC migration backlog & candidate mapping | `test_candidate_pqc_mapping_coverage_and_caveats`, `test_backlog_builder_priority_sorting` | **PASSED** |
| **AC-09** | Reversible deduplication & conflict retention | `test_map_observation`, `test_end_to_end_intake_to_discovery_and_canonical_mapping` | **PASSED** |
| **AC-10** | Factor transparency & why-now explanation | `test_factor_contributions_transparency`, `test_scenario_sensitivity_horizon_slider` | **PASSED** |
| **AC-12** | Alert fatigue reduction vs flat severity | `test_baseline_comparison_reduces_alert_fatigue` | **PASSED** |
| **AC-15** | Single integrated MVP workflow | `test_e2e_complete_synthetic_scan_to_risk_and_export_journey` | **PASSED** |
| **AC-16** | Reviewer audit logging with validation | `test_workflow_api_audit_validation_and_rejections`, `test_create_audit_record` | **PASSED** |
| **AC-17** | Sanitized CBOM project export | `test_get_export`, `test_e2e_complete_synthetic_scan_to_risk_and_export_journey` | **PASSED** |
| **AC-18** | Zero stubs/mocks in core pipeline | End-to-end integration test runs against production models and engines | **PASSED** |

---

## 4. Defect Taxonomy & Routing Log

| Defect ID | Severity | Description | Owning Module | Status | Resolution |
|---|---|---|---|---|---|
| *None* | D1–D4 | All end-to-end user journey and workflow API tests passed without defect | N/A | Closed | Verified by test suite |

---

## 5. Retest & Signoff Statement

Cycle V02 validation is complete and fully verified against implementation in `backend/app/` using pytest. The single integrated MVP journey is verified end-to-end with zero mock dependencies in the core analytics and data pipeline. Functional assurance signoff for Cycle V02 is approved.
