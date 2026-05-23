---
種別: disc
ID: "20260523t144246z-disc"
タイトル: "V1 Issue Authoring Delegated Evidence"
状態: "proposed"
作成者: "Codex"
最終更新: "2026-05-23"
親: ["epic-00112"]
関連: ["iss-00120", "iss-00121", "iss-00122", "iss-00123", "iss-00124", "iss-00125"]
authority: "proposed"
derived_from: ["epic-00112/requirement.md", "epic-00112/design.md", "epic-00112/plan.md", "epic-00112/report.md"]
reflected_to: ["iss-00120", "iss-00121", "iss-00122", "iss-00123", "iss-00124", "iss-00125"]
---

# 20260523t144246z-disc V1 Issue Authoring Delegated Evidence

## 位置づけ
- この discussion は、v1 追加 Issue `iss-00120`〜`iss-00125` の requirement / design / plan 作成に使った delegated specialist output の永続証跡である。
- authority は `proposed`。この文書自体は promotion evidence ではなく、各 Issue の canonical docs に反映された内容と fresh `spec-reviewer` pass が phase gate の根拠になる。
- 完了済み v0 Issue 001〜006 / #113〜#118 は historical evidence として参照し、計画・報告を上書きしない。

## Delegated Inputs

### system-architect: Lovelace
- role: `system-architect`
- phase: requirement / design input
- scope: `epic-00112` v1 additive Issues `iss-00120`〜`iss-00125`
- status: `produced`
- source artifacts:
  - `epic-00112/requirement.md`
  - `epic-00112/design.md`
  - `epic-00112/plan.md`
  - `epic-00112/report.md`
  - v0 historical issue docs `iss-00113`〜`iss-00118`
  - current template docs for `iss-00120`〜`iss-00125`
- output summary:
  - Issue ごとの AC / EC / non-scope を具体化した。
  - provider source、dogfooding validation surface、rollback、test strategy を Issue ごとに整理した。
  - 危険な順序破りとして、schema before runtime, ledger before permission profile, gates/profiles before role rewrite, role rewrite before pilot を指摘した。
- integration result:
  - Reflected into each Issue `requirement.md` and `design.md`.
- rejected portions:
  - none.
- blockers:
  - none.
- reviewer result:
  - Pending fresh `spec-reviewer` on integrated canonical issue docs.
- promotion decision:
  - Integrated as draft evidence only; not sufficient for phase promotion.

### repo-analyst: Mencius
- role: `repo-analyst`
- phase: design path / test surface input
- scope: provider source and dogfooding validation paths for `iss-00120`〜`iss-00125`
- status: `produced`
- source artifacts:
  - provider docs/templates/runtime/assets under `src/spec_dock/assets/`
  - dogfooding workspace paths under `spec-dock/`, `.agents/`, `.codex/`
  - existing test directories under `tests/`
- output summary:
  - `iss-00120`: provider docs/templates/system active-none, dogfooding docs/templates/system active-none, managed asset tests.
  - `iss-00121`: runtime context-pack/lifecycle paths and active/sync/validate tests.
  - `iss-00122`: docs/templates/skills paths for ledger/depth policy.
  - `iss-00123`: `.codex/agents` and Permission Profile probe evidence paths.
  - `iss-00124`: role skill and phase/workflow docs paths.
  - `iss-00125`: dogfooding-only pilot evidence paths.
- integration result:
  - Reflected into each Issue `design.md` provider source, dogfooding validation surface, tests, and rollback sections.
- rejected portions:
  - none.
- blockers:
  - Permission Profile enforcement remains probe-driven and fail-closed.
- reviewer result:
  - Pending fresh `spec-reviewer` on integrated canonical issue docs.
- promotion decision:
  - Integrated as draft evidence only; not sufficient for phase promotion.

### implementation-planner: Archimedes
- role: `implementation-planner`
- phase: plan slicing input
- scope: implementation-ready step decomposition for `iss-00120`〜`iss-00125`
- status: `produced_with_blockers`
- source artifacts:
  - `workflow_issue.md`
  - `phase_plan_issue.md`
  - `docs/authoring/issue-plan.md`
  - parent Epic v1 amendment plan
  - current Issue scaffolds
- output summary:
  - Suggested S01/S02/S90/S99 step structure per Issue.
  - Mapped delegated roles (`doc-writer`, `dev-coder`, `qa-reviewer`, `system-architect`, `implementation-planner`) and reviewer gates.
  - Flagged that template Issue docs were not implementation-ready until requirement/design/plan placeholders were replaced.
- integration result:
  - Reflected into each Issue `plan.md` after requirement/design concretization.
- rejected portions:
  - Treating the original scaffold plans as implementation-ready was rejected.
- blockers:
  - none after canonical issue docs were rewritten from placeholders.
- reviewer result:
  - Pending fresh `spec-reviewer` on integrated canonical issue docs.
- promotion decision:
  - Integrated as draft planning input only; not sufficient for phase promotion.

## Reflected Decisions
- Each v1 Issue is additive and must not rewrite v0 Issue 001〜006 / #113〜#118 plans or reports.
- Each v1 Issue must list concrete provider source, dogfooding validation surface, tests, rollback/fallback, reviewer gates, and final quality gates.
- `iss-00125` must require complete-or-explicit-fallback evidence for `iss-00120`〜`iss-00124` before actual dogfooding draft authoring begins.

## 次アクション
- Reflect this discussion path in each Issue report as delegated draft artifact path.
- Re-run fresh `spec-reviewer` after Issue plan/report fixes.
