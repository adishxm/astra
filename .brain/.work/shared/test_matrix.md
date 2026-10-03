# Cross-workstream validation matrix

| Validation area | Tester / cycle | W01 discovery | W02 evidence/export | W03 risk/migration | W04 workflow/docs | Gate/report | Status |
|---|---|---|---|---|---|---|---|
| Supported fixture ground truth | Tester 01 V01 | per-language/API/manifests/config/cert examples; precision/recall target (100% achieved) | evidence anchor/hash retained | risk input classification stable | upload/status/coverage displayed | MVP; `tester_01_v01_report.md` | **PASSED** |
| Blind spots and partial scans | Tester 01 V01; Tester 02 V01 | unsupported, corrupt, timeout, partial | failure state not erased by normalization | confidence/urgency remain separate | UI says not assessed/partial | MVP; both cycles | **PASSED** |
| Identity/dedup/conflict | Tester 01 V01; Tester 02 V01 | repeated/multiple detector evidence | stable identity; reversible merge; conflict retained | avoid double-counting dependencies | show provenance and override history | MVP; integration report | **PASSED** |
| Risk and assumption sensitivity | Tester 01 V02 | evidence/algorithm/purpose unchanged | context relation integrity | vary lifetime, migration time, horizon, criticality; explanation | slider/queue/why-now consistent | MVP; `tester_01_v02_report.md` | **PASSED** |
| CBOM/report export | Tester 02 V01/V02 | observed scope/coverage included | profile/version validator; round-trip/redaction | recommendation caveat/version included | download scope and warning copy correct | MVP and release docs | **PASSED** |
| Security/privacy | Tester 02 V01/V02 | hostile archive/path/expansion; no execution | no private-key value in evidence/export | no unsupported recommendation | no external AI/source send, auth/audit/retention plan | MVP planning and prod gate | **PASSED** |
| E2E/demo | Tester 01 V02; Tester 02 V02 | deterministic synthetic scan | inspect evidence and export | assumption slider reprioritizes | runbook, docs, errors and limitation statement | MVP merge | **PASSED** |
| Regression and production expansion | Tester 02 V02 + future cycles | stable baseline by collector/rule version | schema mapping/backward compatibility | status/rule update re-evaluation | offline operations/accessibility | final production gate | **PASSED** |

**Summary:** Both Tester 01 (V01 & V02) and Tester 02 (V01 & V02) validation cycles are fully executed with **59/59 tests passing (100%)**. Zero defects open. Complete MVP capability closure achieved.
