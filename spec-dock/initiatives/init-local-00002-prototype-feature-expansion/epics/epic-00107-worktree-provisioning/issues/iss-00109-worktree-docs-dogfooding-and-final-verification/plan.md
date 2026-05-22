---
種別: 計画書（Issue）
ID: "iss-00109"
タイトル: "Worktree docs dogfooding and final verification"
関連GitHub: ["#109"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-05-22"
親: ["epic-00107", "init-local-00002"]
依存: ["requirement.md", "design.md", "iss-00108"]
---

# iss-00109 Worktree docs dogfooding and final verification — 計画

## この計画で満たす要件ID
- E-RQ-008, E-RQ-009, E-RQ-010
- E-AC-011 and final E-AC rollup

## Spec-Locked Closure Index
| id | locked expectation | prevents | required | evidence level |
|---|---|---|---:|---|
| wt-doc-001 | provider and dogfooding docs explain command, layout, bootstrap, scope boundary | stale or misleading user docs | yes | docs diff + review |
| wt-doc-002 | dogfooding runtime exposes `worktree create` | provider-only implementation drift | yes | command/help smoke |
| wt-doc-003 | final validation/sync/tests pass | incomplete rollout | yes | commands |

## ステップ一覧

### S01 docs and dogfooding parity
- behavior goal: shipped docs と dogfooding docs/runtime を一致させる。
- planned contract:
  - scope: docs and generated dogfooding runtime parity files
  - test obligation: docs/spec alignment and command smoke
  - red or alternative evidence requirement: inspect-only for docs; command smoke for runtime parity
  - green verification: `./spec-dock/scripts/spec-dock worktree create --help`
  - refactor guardrail: workflow_issue semantics は変更しない。
  - amendment trigger: documented command が implementation と不一致の場合。
- delegation contract:
  - delegated role: `doc-writer`
  - input docs: epic requirement/design/plan and issue docs
  - allowed paths: docs and dogfooding parity files
  - forbidden changes: runtime behavior changes beyond provider parity
  - acceptance criteria: `wt-doc-001`, `wt-doc-002`
  - required tests/docs-only verification: command help smoke, docs review
  - reviewer focus: spec-reviewer
  - stop conditions: docs need new feature scope
  - output required: changed files, verification result, ledger note
#### 具体テストケース一覧
- `tc-s01-001` docs alignment: reference docs mention sibling container
  - 前提: provider docs and dogfooding docs exist.
  - 操作: docs diff / inspection.
  - 期待結果: command, layout, bootstrap, scope boundary が一致する。
  - 失敗検出: nested `.worktrees/` や Codex-managed replacement を示す stale docs を検出する。
  - 検証方法: spec-reviewer docs/spec alignment.
  - 関連 closure id: `wt-doc-001`
- `tc-s01-002` command smoke: dogfooding runtime exposes help
  - 前提: dogfooding runtime has been updated from provider assets.
  - 操作: `./spec-dock/scripts/spec-dock worktree create --help`
  - 期待結果: command help exits 0 and shows optional label.
  - 失敗検出: dogfooding runtime drift を検出する。
  - 検証方法: shell command.
  - 関連 closure id: `wt-doc-002`

### S99 final quality gate
- behavior goal: epic 全体の evidence を揃える。
- planned contract:
  - scope: final tests, validate/sync, report rollup
  - test obligation: `wt-doc-003`
  - red or alternative evidence requirement: final gate only
  - green verification: `python -m unittest discover -v`, `./spec-dock/scripts/spec-dock validate`, `./spec-dock/scripts/spec-dock sync`, `git diff --check`
  - refactor guardrail: test failure fixes must stay within epic scope.
  - amendment trigger: new requirement or untested failure class is discovered.
- delegation contract:
  - delegated role: reviewer gates
  - input docs: all epic and issue docs plus diff
  - allowed paths: report updates and bounded fixes if needed
  - forbidden changes: broad refactor
  - acceptance criteria: all epic E-AC evidence pass
  - required verification: final commands and reviewer passes
  - reviewer focus: qa-reviewer, code-reviewer, spec-reviewer
  - stop conditions: required gate unavailable/fail without fix
  - output required: verdicts and unresolved risks
#### 具体テストケース一覧
- `tc-s99-001` final verification: runtime and spec tree pass
  - 前提: implementation and docs are complete.
  - 操作: final verification commands.
  - 期待結果: tests, validate, sync, diff check pass.
  - 失敗検出: rollout 不足や spec tree 不整合を検出する。
  - 検証方法: listed commands.
  - 関連 closure id: `wt-doc-003`

## Final Exit Contract
- docs parity and runtime parity are confirmed.
- final reports contain verification and reviewer evidence.
- one epic-level PR is created after all three issues are complete.
