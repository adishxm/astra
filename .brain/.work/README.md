# ECDAT planning workspace

This is a **planning-only** execution architecture for the ECDAT webapp project. It creates no application code and makes no claim that the application or any tests already exist. The supplied `merge_res.zip` is preserved byte-for-byte under `.ORG_research/`; the research index, synthesis, quality note, and manifest are in `.research/` / `.work/shared/`.

## Read order
1. `../.research/research_index.md` and `../.research/research_synthesis.md`
2. `traceability_matrix.md` and `00_master_plan.md`
3. `shared/acceptance_criteria.md`, `shared/interface_contracts.md`, and `shared/dependency_graph.md`
4. worker role/phase/handoff/status plans and tester plans
5. `merging_phase_mvp.md`, then `merging_allphase_prod.md`

## Navigation
- `webapp/worker_01`–`worker_04`: scoped MVP and post-MVP plans, phase indexes, handoffs, statuses.
- `testers/tester_01` and `tester_02`: validation cycles, defect routing, signoff criteria.
- `.report/`: one planning report per worker phase and tester cycle; these are report mappings/design reports, not completed execution results.
- `shared/`: assignment, interfaces, dependency graph, acceptance, conventions, decisions, assumptions, blockers, merge/test matrices, status board.
- `../.demo/`: synthetic-data demo runbook and explicit no-production-data guidance.

## Status at planning freeze
Research/archive indexed; no repository was supplied, no branch/commits exist to inspect, no application files were created, and no implementation or application tests were run. All worker/tester status files are `PLANNED`. Unknown official SIH constraints and product-owner policy inputs remain visible blockers/decisions.
