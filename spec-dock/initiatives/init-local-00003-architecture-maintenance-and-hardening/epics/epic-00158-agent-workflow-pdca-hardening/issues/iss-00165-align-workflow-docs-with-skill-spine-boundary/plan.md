---
種別: 実装計画書（Issue）
ID: "iss-00165"
タイトル: "Align Workflow Docs With Skill Spine Boundary"
関連GitHub: ["#165"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-06"
依存: ["requirement.md", "design.md"]
親: ["epic-00158", "init-local-00003"]
---

# iss-00165 Align Workflow Docs With Skill Spine Boundary — 実装計画

## この計画で満たす要件ID

- AC:
  - AC-001 docs are not the only mandatory first-read workflow surface.
  - AC-002 docs retain detailed semantics / hard cases / policy detail.
  - AC-003 clarification docs are bridge/reference for `spec-dock-clarification`.
  - AC-004 provider/mirror validation evidence.
  - AC-005 no scope absorption into skills/templates/runtime.
- EC:
  - EC-001 keep long policy detail in docs when moving it would bloat skills.
  - EC-002 update bridge/link wording safely.
  - EC-003 record follow-up instead of absorbing skill rewrite if needed.

## 依存関係から導く実装順序

- S01 updates provider docs and dogfooding mirror docs together as one docs-only wording slice.
- S90 runs sync / validate / docs impact inspection after S01 commit.
- S99 runs final QA/code/spec review and final report commit.
- `iss-00163` / `iss-00164` completion is a prerequisite for provider docs wording changes.

## 仕様固定クロージャ索引（Spec-Locked Closure Index）

| 識別子（ID） | ステップ | スライス | 種別 | 仕様リンク | 固定する期待値 | 観測可能な入力 / 状態 | 防ぐ bug class | 必須 | 証跡レベル | クロージャ証跡 |
|---|---|---|---|---|---|---|---|---|---|---|
| cl-001 | S01 | docs boundary wording | acceptance | AC-001 | Docs identify skills as operational entrypoints / first-read workflow spine and docs as detail/reference layer | provider docs diff | hidden mandatory workflow remains docs-only | yes | inspect-only | report Step/Test Closure |
| cl-002 | S01 | detail retention | acceptance | AC-002, EC-001 | Workflow / phase / authoring docs retain detailed semantics, lifecycle policy, hard cases, and field meanings | manual read-through / diff inspection | over-thinning docs | yes | inspect-only | report Step/Test Closure |
| cl-003 | S01 | clarification bridge | acceptance | AC-003, EC-002 | Clarification docs and entry docs point to `spec-dock-clarification` as skill-owned workflow and docs as bridge/reference | targeted `rg` | clarification workflow becomes docs-owned again | yes | inspect-only | report Step/Test Closure |
| cl-004 | S01 | scope boundary | regression | AC-005, EC-003 | No skill/template/runtime changes are included; any required skill rewrite is recorded as follow-up / no-op rationale | `git diff --name-only` | scope absorption | yes | inspect-only | report Closure Coverage |
| cl-005 | S01 | prerequisite evidence | prerequisite | AC-001, AC-003 | `iss-00163` and `iss-00164` completion evidence exists before docs wording changes | GitHub / git log inspection | docs alignment based on incomplete prior surfaces | yes | inspect-only | report Step Closure |
| cl-006 | S90 | provider/mirror validation | regression | AC-004 | `sync`, `validate`, mirror inspection, and diff-check pass; generated changes are recorded | commands and status | provider/mirror drift | yes | manual-required | Docs Impact Resolution |
| cl-007 | S99 | final gate | final | all AC/EC | QA/code/spec reviewers pass and final report ledger is committed | reviewers / commands / commit | incomplete issue finish evidence | yes | manual-required | Final Quality Gate |

## 実装ステップ S01 — Workflow Docs Boundary Wording

- 振る舞いの目標:
  - Workflow / phase / authoring / entry docs are readable as detail/reference surfaces reached from skill-owned operational entrypoints.
- design 参照:
  - Boundary Wording Contract。
- 依存:
  - `iss-00163` and `iss-00164` completed.
- 対象ファイル:
  - `src/spec_dock/assets/spec_dock/docs/README.md`
  - `src/spec_dock/assets/spec_dock/docs/guide.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_clarification.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
  - `src/spec_dock/assets/spec_dock/docs/phase_plan_issue.md`
  - `src/spec_dock/assets/spec_dock/docs/authoring/issue-plan.md`
  - dogfooding mirror equivalents under `spec-dock/docs/`
- planned contract:
  - allowed paths:
    - Provider docs and dogfooding mirror docs listed above.
    - `report.md` evidence.
  - forbidden changes:
    - `.agents/skills/`, `src/spec_dock/assets/install_root/.agents/skills/`
    - `src/spec_dock/assets/spec_dock/templates/`, `spec-dock/templates/`
    - runtime scripts / Python code / tests.
  - Red / alternative evidence:
    - Inspect old entry docs and workflow docs for wording that can read as docs-only mandatory workflow authority.
    - Confirm completion of prerequisite issues.
  - Green verification:
    - Positive `rg` for skill-first / detail-reference / bridge wording.
    - Negative `rg` for stale clarification docs-as-source-of-truth wording.
    - `git diff --name-only` scope check.
    - `git diff --check`.
  - closure ids:
    - cl-001..cl-005.
  - amendment trigger:
    - A required change touches skills/templates/runtime.
    - A lifecycle policy change is needed rather than wording alignment.
    - `workflow_clarification.md` full retirement becomes necessary.

### S01 delegation contract

- delegated role:
  - `doc-writer`
- required reason:
  - shipped docs / workflow text changes are delegated worker work under `workflow_issue.md`.
- source of truth:
  - approved requirement / design / plan.
  - Epic ADRs and `iss-00162` inventory.
  - provider docs under `src/spec_dock/assets/spec_dock/docs/`.
- allowed changes:
  - S01 target provider docs and dogfooding mirror docs.
- forbidden changes:
  - skills, templates, runtime, tests, GitHub state, issue metadata.
- required verification:
  - changed file list, targeted positive / negative `rg`, `git diff --check`.
- required output:
  - changed files, verification result, unresolved risks, and `Ledger Note` or `No material implementation decisions beyond the approved plan.`
- stop conditions:
  - Need for skill/template/runtime change.
  - Need for user intent clarification.
  - Verification cannot run.

### S01 concrete checks

- `tc-s01-001` inspect-only: docs boundary positive wording
  - expected: changed docs include skill-first operational entrypoint wording and docs detail/reference wording.
  - verification: targeted `rg` over provider and mirror docs.
  - related closure id: cl-001.
- `tc-s01-002` inspect-only: detail retention
  - expected: workflow policy/detail sections remain present; diff does not delete lifecycle semantics wholesale.
  - verification: diff inspection and manual read-through.
  - related closure id: cl-002.
- `tc-s01-003` inspect-only: clarification bridge
  - expected: `workflow_clarification.md` and entry docs mention `spec-dock-clarification` as skill-owned / entry workflow and docs as bridge/reference.
  - verification: targeted `rg`.
  - related closure id: cl-003.
- `tc-s01-004` inspect-only: scope boundary
  - expected: no skills/templates/runtime files changed.
  - verification: `git diff --name-only`.
  - related closure id: cl-004.
- `tc-s01-005` inspect-only: prerequisites
  - expected: GitHub issues #163 and #164 are closed and local history has their final gate commits.
  - verification: `gh issue view 163`, `gh issue view 164`, `git log --grep`.
  - related closure id: cl-005.

### S01 step gate

- reviewer:
  - `spec-reviewer`
- pass condition:
  - `review_status: pass`
- commit boundary:
  - docs changes + report S01 evidence.

## ドキュメント影響の解消ステップ S90

- 対象:
  - generated projections / dogfooding mirror after docs change.
- 対応:
  - `./spec-dock/scripts/spec-dock sync`
  - `./spec-dock/scripts/spec-dock validate`
  - `git diff --check`
  - `git status --short`
  - mirror docs inspection for changed provider docs.
- spec/doc review:
  - reviewer: `spec-reviewer`
  - pass 条件: cl-006 pass.
- allowed paths:
  - `spec-dock/.agent/*`, `spec-dock/*.puml`, `spec-dock/dashboard.md`, `report.md` evidence only if sync rewrites projections.
- forbidden changes:
  - Additional provider docs / skills / templates / runtime changes after S01 without returning to S01.
- concrete check:
  - `tc-s90-001` manual-required: sync / validate / mirror validation.
  - related closure id: cl-006.

## 最終品質ゲートステップ S99

- branch diff 範囲:
  - issue planning commit to HEAD.
- 必須 validation:
  - `./spec-dock/scripts/spec-dock validate`
  - `git diff --check`
  - final `git status --short`
  - issue-wide diff inspection.
- final QA gate:
  - reviewer: `qa-reviewer`
  - scope: obligation coverage and verification adequacy.
- final code review:
  - reviewer: `code-reviewer`
  - scope: issue-wide integrated diff, scope boundary, markdown safety.
- final spec review:
  - reviewer: `spec-reviewer`
  - scope: requirement / design / plan / report / implementation / docs alignment.
- final commit gate:
  - final report ledger committed.
- concrete check:
  - `tc-s99-001` manual-required: final gates and report commit.
  - related closure id: cl-007.

## 未確定事項

- Blocking question:
  - なし。
- Amendment trigger:
  - Required scope expands into skills/templates/runtime.
  - Lifecycle policy semantics must change rather than wording boundary.
  - Full retirement of `workflow_clarification.md` becomes necessary.

## 最終完了条件

- AC-001..AC-005 / EC-001..EC-003 達成。
- cl-001..cl-007 pass。
- S01/S90/S99 reviewer gates pass。
- Final report commit complete。
- `issue finish` succeeds。
