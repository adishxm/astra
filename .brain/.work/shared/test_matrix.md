# Cross-workstream validation matrix (planned)

| Validation area | Tester / cycle | W01 discovery | W02 evidence/export | W03 risk/migration | W04 workflow/docs | Gate/report |
|---|---|---|---|---|---|---|
| Supported fixture ground truth | Tester 01 V01 | per-language/API/manifests/config/cert examples; precision/recall target | evidence anchor/hash retained | risk input classification stable | upload/status/coverage displayed | MVP; tester_01_validation_01_report.md |
| Blind spots and partial scans | Tester 01 V01; Tester 02 V01 | unsupported, corrupt, timeout, partial | failure state not erased by normalization | confidence/urgency remain separate | UI says not assessed/partial | MVP; both cycles |
| Identity/dedup/conflict | Tester 01 V01; Tester 02 V01 | repeated/multiple detector evidence | stable identity; reversible merge; conflict retained | avoid double-counting dependencies | show provenance and override history | MVP; integration report |
| Risk and assumption sensitivity | Tester 01 V02 | evidence/algorithm/purpose unchanged | context relation integrity | vary lifetime, migration time, horizon, criticality; explanation | slider/queue/why-now consistent | MVP; tester_01_validation_02_report.md |
| CBOM/report export | Tester 02 V01/V02 | observed scope/coverage included | profile/version validator; round-trip/redaction | recommendation caveat/version included | download scope and warning copy correct | MVP and release docs |
| Security/privacy | Tester 02 V01/V02 | hostile archive/path/expansion; no execution | no private-key value in evidence/export | no unsupported recommendation | no external AI/source send, auth/audit/retention plan | MVP planning and prod gate |
| E2E/demo | Tester 01 V02; Tester 02 V02 | deterministic synthetic scan | inspect evidence and export | assumption slider reprioritizes | runbook, docs, errors and limitation statement | MVP merge |
| Regression and production expansion | Tester 02 V02 + future cycles | stable baseline by collector/rule version | schema mapping/backward compatibility | status/rule update re-evaluation | offline operations/accessibility | final production gate |

All entries are planned validation, not executed tests. Defects are classified and routed as defined in tester plans; each correction plan triggers focused regression and report update.
