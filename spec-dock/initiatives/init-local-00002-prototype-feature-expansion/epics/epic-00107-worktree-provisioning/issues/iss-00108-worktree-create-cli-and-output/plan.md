---
種別: 計画書（Issue）
ID: "iss-00108"
タイトル: "Worktree create CLI and output"
関連GitHub: ["#108"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-05-22"
親: ["epic-00107", "init-local-00002"]
依存: ["requirement.md", "design.md", "iss-00110"]
---

# iss-00108 Worktree create CLI and output — 計画

## この計画で満たす要件ID
- E-RQ-001, E-RQ-007, E-RQ-010
- E-AC-001, E-AC-005, E-AC-007, E-AC-009, E-AC-010

## Spec-Locked Closure Index
| id | locked expectation | prevents | required | evidence level |
|---|---|---|---:|---|
| wt-cli-001 | `worktree create [LABEL]` が parser/registry/bootstrap を通って実行される | command 未登録回帰 | yes | runtime test |
| wt-cli-002 | output が id/branch/path/bootstrap status を含む | user が作成先を特定できない回帰 | yes | runtime test |
| wt-cli-003 | fatal error は non-zero で stderr に出る | failure が success に見える回帰 | yes | runtime test |

## ステップ一覧

### S01 CLI wiring and text output
- behavior goal: core use case を user-facing command にする。
- planned contract:
  - scope: `commands/worktree.py`, `cli/parser.py`, `cli/registry.py`, `cli/bootstrap.py`, `presentation/cli_text.py`, `tests/cli_runtime/test_worktree.py`
  - test obligation: `wt-cli-001`..`wt-cli-003`
  - red or alternative evidence requirement: command missing red / invalid-label fail path characterization
  - green verification: `python -m unittest tests.cli_runtime.test_worktree -v`
  - refactor guardrail: existing command groups の arguments を変更しない。
  - amendment trigger: JSON output や remove/status command が必要になった場合。
- delegation contract:
  - delegated role: `dev-coder`
  - input docs: this issue docs and iss-00110 contracts
  - allowed paths: planned contract scope
  - forbidden changes: core naming rule changes, docs-only updates
  - acceptance criteria: closure index all rows
  - required tests: targeted runtime command tests
  - reviewer focus: code-reviewer
  - stop conditions: command output contract に additional fields が必要になった場合
  - output required: changed files, verification result, ledger note
#### 具体テストケース一覧
- `tc-s01-001` acceptance: command creates worktree through CLI
  - 前提: temp repo の initial commit がある。
  - 操作: `worktree create` を実行する。
  - 期待結果: exit 0 で worktree が作られ、stdout に id/branch/path/bootstrap が出る。
  - 失敗検出: parser/registry/bootstrap/rendering の未接続を検出する。
  - 検証方法: `tests/cli_runtime/test_worktree.py`
  - 関連 closure id: `wt-cli-001`, `wt-cli-002`
- `tc-s01-002` negative: invalid label returns non-zero
  - 前提: temp repo に worktree container がない。
  - 操作: `worktree create bad_label` を実行する。
  - 期待結果: exit non-zero、stderr に invalid label が出る。
  - 失敗検出: fatal error が成功扱いになる回帰を検出する。
  - 検証方法: `tests/cli_runtime/test_worktree.py`
  - 関連 closure id: `wt-cli-003`
- step closure contract: closure index all rows pass via targeted tests.
- report evidence destination: issue report Step/Test Contract Closure.
- step gate: targeted test pass, code-reviewer pass, commit gate.

## S90 docs impact resolution / docs refresh
- docs は iss-00109 の rollout step で扱う。

## S99 final quality gate
- epic final gate は iss-00109 へ集約する。

## Final Exit Contract
- CLI runtime tests pass。
- command surface が reference docs と一致する状態へ iss-00109 で引き継がれる。
