# Planning report — tester_01 V01: Discovery, ground truth, evidence and coverage

- **Prepared:** 2026-10-03 (planning freeze)
- **Owner:** Functional assurance planner
- **Validation cycle:** V01
- **Status:** PLANNED; no tests run.
- **Research / acceptance mapping:** W01 MVP-01/02 and W02 MVP-01; AC-01–AC-06, AC-11; trace R01–R06/R10/R12.

## Objective
Ground-truth seeded repositories; source/API and dependency/config/certificate fixtures; regex baseline vs planned richer detector; evidence path/line/hash; duplicates/conflicts; unsupported and corrupt inputs; archive safety; partial collector behavior.

## Planned validation
See `.work/testers/tester_01/test_plan.md` for detailed coverage, acceptance mapping, defect route and signoff. Expected evidence includes build/rule/schema versions, fixture IDs, assessed denominator, per-class counts, outcomes, failure states and documented limitations.

## Files to be created or modified later
No application paths are assigned by this report. Future artifacts include the versioned fixture/benchmark evidence, test logs, defect records, updated docs and component files owned by the mapped workers. This task created planning documents only.

## Expected results (future, not observed)
A reproducible validation record sufficient for a planning/release gate, including negative cases, unsupported/partial states, defects, targeted retest and documentation changes. No pass is claimed.

## Issues / blockers
Tests require an implementation and actual ground-truth fixtures; the current workspace has neither. Official scope, schema, risk defaults, retention and deployment remain open where relevant.

## Dependencies / handoff
Hand defects to the responsible worker named in the tester plan. Require correction report, affected acceptance ID and targeted regression before closing. Update validation log, docs, traceability and merge checklist.

## Next steps
After implementation exists, freeze test environment and criteria, execute cycle, record actual results, route defects, retest, and obtain independent signoff.
