---
種別: disc
ID: "20260623t-plan-static-analysis-execution-readiness-review"
title: "Static analysis execution readiness review"
タイトル: "Static analysis execution readiness review"
authority: proposed
adoption_status: unreviewed
reflected_to: []
created_by_role: implementation-planner
scope_id: iss-00225
source_paths:
  - AGENTS.md
  - spec-dock/active/context-pack.md
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/report.md
  - spec-dock/active/issue/discussions/20260623t024024z-research-ruff-mypy-preference-source-analysis.md
  - spec-dock/active/issue/discussions/20260623t024210z-interview-static-analysis-target-boundary.md
  - spec-dock/active/issue/discussions/20260623t025015z-interview-static-analysis-enforcement-entrypoint.md
  - spec-dock/active/issue/discussions/20260623t030652z-disc-static-analysis-final-configuration-proposal.md
  - spec-dock/active/issue/discussions/20260623t-design-static-analysis-architecture-review.md
  - spec-dock/docs/authoring/issue-plan.md
  - spec-dock/docs/workflow_issue.md
intended_targets:
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/report.md
diff_guard_result: passed
---

# 20260623t-plan Static analysis execution readiness review

## Plan Summary
- 対象: `iss-00225 Configure Ruff And Mypy Static Analysis Cleanup` の現行 `plan.md`。
- 目的: `requirement.md` / `design.md` に対して、実行開始前の粒度、command target、closure evidence、dogfooding impact、review gate が十分かを確認する。
- 結論: 計画の実装順序と静的解析 target はおおむね妥当。ただし `spec-dock/docs/authoring/issue-plan.md` の strict schema と reviewer fail condition に照らすと、canonical plan review 前に step-local contract を補強した方がよい。

This artifact is evidence only. It is not a reviewer pass and does not approve plan promotion, issue readiness, implementation readiness, or final authority.

## Reviewed Sources
- `requirement.md`: Option B target、CI enforcement、local grouped script + `Makefile`、pre-commit scope out、rule-by-rule inventory、dogfooding impact evidence、final green baseline を要求している。
- `design.md`: `pyproject.toml` central config、`scripts/static_analysis/run.sh`、root `Makefile` `lint`、provider CI `make lint`、`src/spec_dock tests` command target、`spec-dock/` direct exclusion、Ruff/mypy/format configuration を設計している。
- `plan.md`: S01-S18、S90、S99 に分け、Ruff rule group、mypy inventory/error cleanup、format isolation、CI wiring、docs/dogfooding impact、final gate を並べている。
- `report.md`: Evidence Adoption Ledger と Decision Ledger があり、target boundary、enforcement entrypoint、staged adoption、dogfooding refresh/inspection refinement、design review evidence を保持している。
- Prior discussions: research は reference project の Ruff/mypy 方針を翻訳し、interview 2 件は Option B と CI/local command scope を user-approved として固定し、final configuration proposal は最終 rule set と staged adoption を提案している。
- Architecture review discussion: `design.md` は review-ready で、layer-specific banned-api policy は optional deferral clarification として扱われている。
- `AGENTS.md`: provider source of truth は `src/spec_dock/`、dogfooding `spec-dock/` は validation / inspection 対象であり、generated copy を実装 source として扱わない。
- `issue-plan.md` / `workflow_issue.md`: issue plan は executable step schema、step-local delegation contract、具体テストケース一覧、step closure contract、report evidence destination、step gate、S90/S99、Final Exit Contract を要求し、不足は reviewer fail condition になり得る。

## Requirement / Design Traceability
- AC-001: S01 と S14 で dependency / config を扱う。
- AC-002: `command target: src/spec_dock tests` と shipped runtime coverage note、`spec-dock/` exclusion で扱う。
- AC-003: S01 / S17 で `scripts/static_analysis/run.sh` と `make lint` を扱う。
- AC-004: S18 で provider CI `make lint` wiring を扱う。
- AC-005: S02-S13 で Ruff final rule setを段階導入する。
- AC-006: S14-S15 で mypy inventory と 0 件化を扱う。
- AC-007: S16 で format-only 差分を隔離する。
- AC-008: S17-S99 で final local gate、pytest、SpecDock validate、dogfooding impact を閉じる。
- AC-009: S08/S11/S12/S13/S15/S99 で ignore / suppression rationale を扱う。
- EC-006: S90/S99 で shipped runtime asset 変更時の dogfooding refresh/inspection 判断を扱う。

## Findings / Recommendations Ordered by Severity

### High: step-local executable schema is still too thin for canonical plan review
- Finding: `plan.md` has a useful global step list and per-step prose, but individual S01-S18/S90/S99 sections do not yet carry the full `issue-plan.md` executable step schema: `delegation contract`, `具体テストケース一覧`, `step closure contract`, `report evidence destination`, and `step gate`.
- Why it matters: `spec-dock/docs/authoring/issue-plan.md` lists missing concrete test cases or missing delegation contract fields as reviewer fail conditions. The current global `## 委任契約（全 implementation step）` helps, but it still leaves per-step allowed paths, forbidden changes, reviewer focus, stop conditions, and output evidence partially implicit.
- Recommendation: Before canonical plan spec review, expand `## 実装ステップ` so each step has a compact repeated structure:
  - behavior goal / scope
  - delegation contract
  - 具体テストケース一覧 or explicit inspect-only/manual-required alternative
  - step closure contract
  - report evidence destination
  - step gate
- Exact plan sections to change:
  - `## 実装ステップ`
  - each subsection `### S01` through `### S18`, `### S90`, `### S99`
  - `## 委任契約（全 implementation step）`, either keep as common defaults or replace with per-step contracts plus shared defaults
  - add `## Final Exit Contract` if the canonical template/reviewer expects that heading.

### Medium: S18 CI closure should distinguish workflow wiring from observed CI enforcement
- Finding: S18 currently allows `workflow diff inspection / CI result`, while AC-004 requires static analysis gate execution in provider CI.
- Why it matters: Workflow inspection proves the YAML was changed, but it does not prove provider CI actually ran the new `make lint` gate. If GitHub Actions cannot be observed during implementation, the plan should say what evidence is acceptable and whether AC-004 remains open until PR/CI evidence is available.
- Recommendation: Make S18 closure two-tiered:
  - local/pre-PR closure: workflow diff inspection proves provider CI calls `make lint`.
  - external closure: GitHub Actions result or PR delivery/merge-prep evidence proves the static-analysis gate ran.
- Exact plan sections to change:
  - `### S18 — Provider CI Static Analysis Gate` `検証` and `close 条件`
  - `### S99 — Final Quality Gate` required validation / reviewer gates
  - `## 仕様固定クロージャ索引` row `tc-s18-001`, clarify evidence level as `inspection + CI/PR evidence when available`.

### Medium: S01 command skeleton closure is ambiguous
- Finding: S01 says `make lint` skeleton inspection and allows the script to include only currently enabled checks. This is reasonable for staged adoption, but the expected command behavior at S01 is not fully observable.
- Why it matters: AC-003 is ultimately a one-command entrypoint. At S01, implementation could accidentally create a script that is executable but not root-safe, target-safe, or summary-safe, and still pass "inspection" unless the plan states what to inspect.
- Recommendation: In S01, add explicit inspect-only or command evidence:
  - `test -x scripts/static_analysis/run.sh`
  - inspect that script targets only `src/spec_dock tests`
  - inspect that `Makefile` `lint` invokes the script
  - if any phase runs at S01, run `make lint` and record expected pass/fail scope in `report.md`.
- Exact plan sections to change:
  - `### S01 — Dependency / Config / Local Command Skeleton`
  - closure index row `tc-s01-001`.

### Low: dependency resolution evidence should be explicit
- Finding: The plan adds Ruff in S01 and mypy in S14, with an option to add mypy earlier. It does not explicitly name dependency resolution evidence such as tool version commands or lock/update verification.
- Why it matters: This issue depends on `uv` dev dependency behavior. A green static-analysis plan should prove the tools resolve before rule cleanup starts.
- Recommendation: Add S01/S14 evidence such as `uv run ruff --version` and `uv run mypy --version` when each tool is introduced, or document why `make lint` / individual commands subsume that evidence.
- Exact plan sections to change:
  - `### S01`
  - `### S14`
  - closure index rows `tc-s01-001` and `tc-s14-001`.

### Low: dogfooding impact is covered, but report destination can be more precise
- Finding: S90 and S99 correctly require shipped runtime asset diff inspection and dogfooding refresh/inspection judgment. The plan does not identify the exact `report.md` ledger/table rows where this will be recorded.
- Why it matters: EC-006 is a source-of-truth risk. A precise report destination makes it easier for spec-reviewer to confirm dogfooding impact was not skipped.
- Recommendation: Add a `report evidence destination` line for S90/S99 pointing to `Spec Interpretation / Decision Ledger`, `Step Contract Closure`, and `Closure Coverage` for `tc-s90-001` / `tc-s99-001`.
- Exact plan sections to change:
  - `### S90 — Docs / Dogfooding Impact Resolution`
  - `### S99 — Final Quality Gate`.

## Canonical Adoption Recommendation
- Recommendation: partially adopt.
- Rationale: The current plan's dependency-derived execution order, target boundary, rule slicing, and final quality gate are strong enough to preserve. The plan should not be rejected or rewritten from scratch. However, canonical plan spec review should not proceed until the executable step schema is expanded to match `issue-plan.md`.
- Required canonical `plan.md` changes:
  - Expand `## 実装ステップ` with per-step executable schema.
  - Add per-step `delegation contract` fields or transform the global common contract into step-local defaults plus overrides.
  - Add `具体テストケース一覧` / inspect-only alternatives for every step.
  - Add `step closure contract`, `report evidence destination`, and `step gate` for every step.
  - Clarify S18 CI evidence and S01 skeleton evidence.
  - Add `Final Exit Contract` if missing from the canonical template expectations.
- `requirement.md`: no required change found.
- `design.md`: no required change found.
- `report.md`: when this draft is adopted or rejected, add Evidence Adoption Ledger and Delegated Draft Evidence entries according to the orchestrator's decision.

## Milestones
- M1: Tooling surface and target boundary baseline: S01.
- M2: Ruff semantic/hygiene rule adoption: S02-S13.
- M3: Mypy adoption and error cleanup: S14-S15.
- M4: Format isolation and final local gate: S16-S17.
- M5: CI enforcement: S18.
- M6: Docs/dogfooding impact resolution and final quality gate: S90-S99.

## Dependency-Derived Execution Order
- S01 must precede all rule execution because commands and dependencies must exist.
- Ruff `F/E/I` should precede behavior-affecting or broader rules to remove obvious baseline noise.
- Ruff semantic and import hygiene rules should precede mypy so typecheck output is not polluted by simpler cleanup issues.
- Format-only work should remain after semantic/type fixes to prevent mixed review diffs.
- CI wiring should follow local `make lint` green state, but CI evidence remains external until workflow execution is observed.
- S90 must precede S99 because docs/dogfooding impact is part of final readiness.

## Issue / Step Slicing
- Current slicing is appropriately small at the rule-group level.
- The main slicing refinement is not more steps; it is richer step contracts.
- If any Ruff rule causes broad architecture rewrite, the current amendment triggers are adequate and should stop implementation before scope expansion.
- S14 characterization allowing non-zero mypy inventory is acceptable as long as S15 is the 0-error acceptance step.

## Test Strategy Mapping
- Rule steps: command evidence via `uv run ruff check --select ... src/spec_dock tests`, plus report inventory.
- Mypy steps: `uv run mypy src/spec_dock tests`, first inventory then 0-error closure.
- Format step: `uv run ruff format --check src/spec_dock tests`, with format-only diff inspection if formatting is applied.
- Local gate: `make lint`, including summary and non-zero exit behavior.
- Regression: `uv run pytest`.
- SpecDock validation: `./spec-dock/scripts/spec-dock validate`.
- CI: provider workflow inspection plus GitHub Actions/PR evidence when available.

## Review Gates
- Per implementation step: code-reviewer pass before commit for code/config/workflow changes.
- S90 docs-only changes: doc-writer if needed, then spec-reviewer docs/spec alignment.
- Final gate: qa-reviewer, issue-wide code-reviewer, and final spec-reviewer pass.
- This discussion draft does not satisfy any reviewer gate.

## Rollback / Compatibility
- Rule adoption can be rolled back by removing the current rule group or converting it into a plan amendment/follow-up if it requires architecture rewrite.
- Python compatibility stays anchored to `py310` / `3.10`.
- Dogfooding compatibility is preserved by excluding `spec-dock/` from direct Ruff/mypy targets and using inspection/refresh evidence only when shipped runtime assets change.
- CI rollback is limited to removing `make lint` wiring if the local gate cannot be made green, but that would fail AC-004 unless a plan amendment is approved.

## Docs Impact
- Plan already includes S90 for docs impact and dogfooding refresh/inspection.
- Recommended refinement: S90 should explicitly record the exact report destination and spec-reviewer gate for docs impact `none` or docs updates.
- Permanent docs updates are likely if `make lint` becomes a standard developer command and existing developer command lists exist.

## Final Quality Gate
- Keep S99 independent.
- Required evidence should include:
  - `make lint`
  - `uv run pytest`
  - `./spec-dock/scripts/spec-dock validate`
  - `git status --short`
  - shipped runtime asset diff inspection and dogfooding impact evidence when applicable
  - qa-reviewer, issue-wide code-reviewer, final spec-reviewer pass
  - CI/PR evidence for AC-004 when available, or an explicit unresolved external evidence note if not yet observable.

## Plan Blockers
- Blocker for implementation readiness: missing step-local executable schema in `plan.md` relative to `issue-plan.md`.
- Blocker for canonical plan spec review: likely yes, unless the reviewer accepts the current global contract as sufficient. Based on documented reviewer fail conditions, tightening the plan first is safer.
- Requirement/design blocker: none found.
- Clarification candidates for orchestrator: none for user. This is a plan authoring refinement, not a product ambiguity.

## Integration Notes for Main Orchestrator
- Changed discussion artifact path: `spec-dock/active/issue/discussions/20260623t-plan-static-analysis-execution-readiness-review.md`.
- Source requirement/design revisions used:
  - `requirement.md`: ID `iss-00225`, 最終更新 `2026-06-23`.
  - `design.md`: ID `iss-00225`, 最終更新 `2026-06-23`.
- Lightweight provenance:
  - created_by_role: `implementation-planner`
  - scope_id: `iss-00225`
  - adoption_status: `unreviewed`
  - reflected_to: `[]`
  - diff_guard_result: `passed`
- Leaf evidence used: repository-local active docs, prior issue discussions, architecture review discussion, `AGENTS.md`, `issue-plan.md`, and `workflow_issue.md`.
- Forbidden actions avoided: no canonical docs edited, no implementation/tests/config/workflows edited, no GitHub state changed, no secrets accessed, no reviewer pass claimed.
- Unresolved design gaps: none.
- Unresolved plan gaps: step-local executable schema, S18 CI evidence specificity, S01 skeleton evidence specificity, dependency resolution evidence, S90 report destination precision.
- No canonical edit, final authority, promotion, reviewer-pass, implementation-readiness, or user-dialogue ownership is claimed.
