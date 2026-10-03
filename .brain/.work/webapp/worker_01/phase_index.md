# Worker 01 phase index

Plan the complete authorized upload-to-observation path: safe archive intake, supported cryptographic discovery, and truthful coverage/benchmark accounting.

## Dynamic phase count
This worker has **3 MVP phases and 2 conditional production phases**, sized for its assigned scope. Phase counts intentionally differ among workers. None of its MVP responsibilities may be left to a later stage.

| ID | Phase | File | Gate |
|---|---|---|---|
| MVP-01 | Safe upload intake and scan boundary | `mvp_phases/mvp_01.md` | MVP complete-product gate |
| MVP-02 | Supported source, manifest, config and certificate discovery | `mvp_phases/mvp_02.md` | MVP complete-product gate |
| MVP-03 | Coverage, partial scans and benchmark readiness | `mvp_phases/mvp_03.md` | MVP complete-product gate |
| PROD-01 | Static binary and container discovery extension | `prod_phases/prod_01.md` | Post-MVP production gate |
| PROD-02 | Separately authorized endpoint/network evidence | `prod_phases/prod_02.md` | Post-MVP production gate |

## Frontend React App Phases
Production-grade Single Page Application (SPA) replacing static web dashboard with responsive, interactive PQC discovery, Mosca risk visualization, and CycloneDX 1.6 CBOM explorer.

| ID | Phase | File | Gate |
|---|---|---|---|
| Phase-Aa | React Frontend Foundation & Core Scan Workflow | `mvp_phases/phase_Aa.md` | Frontend Gate 1 (Foundation & Scan) |
| Phase-Ab | Risk Dashboard, CBOM Export & Advanced Visualizations | `mvp_phases/phase_Ab.md` | Frontend Gate 2 (Complete Web UI) |

Production is optional enhancement planning and begins only after the MVP gate.
