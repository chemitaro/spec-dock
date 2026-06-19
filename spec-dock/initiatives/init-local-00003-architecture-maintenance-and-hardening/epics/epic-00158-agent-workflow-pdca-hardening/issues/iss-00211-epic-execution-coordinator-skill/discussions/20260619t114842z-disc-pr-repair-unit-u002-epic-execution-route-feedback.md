---
種別: disc
ID: "20260619t114842z-disc"
タイトル: "PR Repair Unit U002"
状態: "proposed"
作成者: "iwasawayuuta"
最終更新: "2026-06-19"
親: ["iss-00211"]
関連: []
authority: "proposed"
derived_from: []
reflected_to: []
---

# 20260619t114842z-disc PR Repair Unit U002

## source_batch
- `20260619t113109z-pr-repair-batch-pr-repair-batch.md`

## unit_id
- U002

## covered_ids
- I002, I003, I004

## source_links
- PR: https://github.com/chemitaro/spec-dock/pull/217
- Review comments:
  - 3442232087 / thread `PRRT_kwDOQ99OK86K0kEi`
  - 3442232093 / thread `PRRT_kwDOQ99OK86K0kEo`
  - 3442232098 / thread `PRRT_kwDOQ99OK86K0kEt`

## failure_class
- `review_feedback:epic-execution-route-consistency`

## risk_class
- `blocking`

## disposition
- `fix-now`

## Validity Analysis
- I002 is valid: `/execute-initiative` still routes issue decomposition through `/execute-epic`, while `/execute-epic` now routes incomplete planning/decomposition back to `$spec-dock-epic-planning`.
- I003 is valid: `spec-dock-epic-execution` says active or requested Epic, but the stop rule requires an active Epic before explaining how requested Epics are resolved.
- I004 is valid: no ready Issue currently forces blocker/escalation before the no-op Epic completion gate can be used.

## Need-To-Fix Decision
- `need_to_fix: yes`
- The three review threads are unresolved and affect user-facing agent workflow contracts.
- Repair remains within Issue 211 scope because it aligns the coordinator split rather than adding new execution behavior.

## Root Cause
- The Issue 211 route split introduced a coordinator skill and changed `/execute-epic`, but adjacent initiative prompt and edge-case skill wording were not fully harmonized with the new boundary.

## Options Considered
- Option A: mark the comments as follow-up.
  - Rejected because the comments identify contradictions in the shipped route surface.
- Option B: broaden into implementation changes.
  - Rejected because no runtime command behavior is required; this is prompt/skill route wording plus regression tests.
- Option C: bounded prompt/skill wording updates and route/content tests.
  - Selected.

## Recommended Design
- Update provider and mirror `spec-dock-epic-execution/SKILL.md` so requested Epic invocation is resolved before active-state checks, and no-ready-Issue handling allows the explicit no-op completion gate.
- Update provider and mirror `execute-initiative.md` so initiative execution sends incomplete Epic decomposition/planning to `$spec-dock-epic-planning` instead of `/execute-epic`.
- Add/adjust regression tests to lock the new initiative route, requested Epic wording, and no-op ready-Issue exception.

## Implementation Plan
1. Inspect provider/mirror skill and prompt files plus existing Issue 211 route tests.
2. Update provider-side `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-execution/SKILL.md` and dogfooding mirror `.agents/skills/spec-dock-epic-execution/SKILL.md`.
3. Update provider-side `src/spec_dock/assets/install_root/.codex/prompts/execute-initiative.md` and dogfooding mirror `.codex/prompts/execute-initiative.md`.
4. Update focused regression tests in `tests/unit/infra/test_init_update.py`.
5. Run focused route/content tests, provider/mirror `cmp -s`, and `git diff --check`.
6. Commit, push, and re-observe PR #217.

## Validation Plan
- Focused Issue 211 route/content regression must pass.
- Existing execute prompt contract tests touched by route wording must pass.
- Provider/mirror skill and prompt `cmp -s` checks must pass.
- `git diff --check` must pass.
- PR re-observation must show no unresolved blocking review feedback on the latest head.

## Implementation Result
- Updated provider and mirror `spec-dock-epic-execution/SKILL.md` so requested Epic resolution happens before active-Epic checks.
- Updated provider and mirror `spec-dock-epic-execution/SKILL.md` so no-ready-Issue handling distinguishes explicit no-executable-Issue-work Epics from blocked executable work.
- Updated provider and mirror `execute-initiative.md` so planning/decomposition uses `$spec-dock-epic-planning`, while `/execute-epic` is reserved for reviewed planning outputs and ready Issue work.
- Updated provider and mirror `execute-epic.md` so its planning handback line explicitly covers initiative-driven decomposition.
- Added focused regression assertions for initiative route wording, requested-Epic resolution, and no-executable-Issue-work.
- Focused tests passed: `uv run pytest tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_211_epic_execution_skill_content_regression_contract tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_211_epic_execution_route_content_regression_contract tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_93_execute_prompts_contract` -> `3 passed`.
- Provider/mirror `cmp -s` checks passed for `spec-dock-epic-execution/SKILL.md` and `execute-initiative.md`.
- Additional focused tests passed after `execute-epic.md` anchor repair: `test_issue_211_epic_execution_route_content_regression_contract` and `test_issue_93_execute_prompts_contract` -> `2 passed`.
- Provider/mirror `cmp -s` check passed for `execute-epic.md`.
- `git diff --check` passed.

## Commit Evidence
- pending repair commit

## Re-observation Result
- pending after repair commit push

## Residual Risk / Follow-up
- A future Issue may still be useful to dogfood `/execute-initiative` end-to-end with an Epic that requires decomposition before Issue execution.
