---
種別: 計画書（Issue）
ID: "iss-00110"
タイトル: "Worktree create core use case"
関連GitHub: ["#110"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-05-22"
親: ["epic-00107", "init-local-00002"]
依存: ["requirement.md", "design.md"]
---

# iss-00110 Worktree create core use case — 計画

## この計画で満たす要件ID
- E-RQ-002, E-RQ-003, E-RQ-004, E-RQ-005, E-RQ-006
- E-AC-002, E-AC-003, E-AC-004, E-AC-006, E-AC-007, E-AC-008, E-AC-009, E-AC-010

## 依存関係から導く実装順序
1. application contracts / ports を追加する。
2. Git / make infra adapter を追加する。
3. `application/worktree.py` の use case を実装する。
4. temp repo integration tests で naming、retry、bootstrap、linked-worktree normalization を確認する。

## Spec-Locked Closure Index
| id | locked expectation | prevents | required | evidence level |
|---|---|---|---:|---|
| wt-core-001 | LABEL なしは `wtN`、LABEL ありは `<label>N` で collision retry する | branch/path 衝突で作成不能になる回帰 | yes | runtime test |
| wt-core-002 | container は main worktree の sibling `<repo>-worktrees/` | nested checkout / linked 起点 path 逸脱 | yes | runtime test |
| wt-core-003 | invalid label は作成前 fatal | unsafe path / branch name | yes | runtime test |
| wt-core-004 | bootstrap result は skipped/succeeded/failed/detection_failed を保持し、failure は non-fatal | setup failure で worktree 作成が消える回帰 | yes | runtime test |
| wt-core-005 | non-retryable path/Git failure は原因と `path_exists` / `branch_exists` / `record_exists` を出す | partial artifact state が見えない failure contract 回帰 | yes | runtime test |

## ステップ一覧

### S01 core use case and adapters
- behavior goal:
  - worktree creation の core contract を実装する。
- planned contract:
  - scope: `application/contracts.py`, `application/ports.py`, `application/worktree.py`, `infra/git_cli.py`, `infra/make_cli.py`, `tests/cli_runtime/test_worktree.py`
  - test obligation: closure index 全行を temp repo runtime tests へ対応させる。
  - red or alternative evidence requirement: new command 未実装のため targeted test は red から開始可能。
  - green verification: `python -m unittest tests.cli_runtime.test_worktree -v`
  - refactor guardrail: existing issue/new/sync command behavior へ触れない。
  - amendment trigger: Codex-managed worktree 管理や remove/list が必要になった場合。
- delegation contract:
  - delegated role: `dev-coder`
  - input docs: epic requirement/design/plan, this issue requirement/design/plan
  - allowed paths: planned contract scope の runtime / tests
  - forbidden changes: docs-only work, GitHub lifecycle close, unrelated commands
  - acceptance criteria: `wt-core-001`..`wt-core-005`
  - required tests: targeted runtime tests
  - reviewer focus: code-reviewer
  - stop conditions: real project checkout へ worktree を作る必要が出た場合
  - output required: changed files, verification result, ledger note
#### 具体テストケース一覧
- `tc-s01-001` acceptance: auto id creates sibling worktree
  - 前提: temp repo の initial commit がある。
  - 操作: `worktree create` を実行する。
  - 期待結果: `<repo>-worktrees/<repo>-wt1` と `<current-branch>-wt1` が作られる。
  - 失敗検出: nested path や branch naming の回帰を検出する。
  - 検証方法: `tests/cli_runtime/test_worktree.py`
  - 関連 closure id: `wt-core-001`, `wt-core-002`
- `tc-s01-002` acceptance: label collision retries
  - 前提: temp repo で同じ label を二回使う。
  - 操作: `worktree create feature` を二回実行する。
  - 期待結果: `feature` と `feature2` が作られる。
  - 失敗検出: collision retry 不足を検出する。
  - 検証方法: `tests/cli_runtime/test_worktree.py`
  - 関連 closure id: `wt-core-001`
- `tc-s01-003` negative: invalid label fails before mutation
  - 前提: temp repo に worktree container がない。
  - 操作: `worktree create bad_label` を実行する。
  - 期待結果: non-zero exit で container が作られない。
  - 失敗検出: unsafe label を受け入れる回帰を検出する。
  - 検証方法: `tests/cli_runtime/test_worktree.py`
  - 関連 closure id: `wt-core-003`
- `tc-s01-004` acceptance: make init status is reported
  - 前提: temp repo に `init` target のある Makefile を置く。
  - 操作: `worktree create setup` を実行する。
  - 期待結果: bootstrap `succeeded` で marker file が作られる。
  - 失敗検出: bootstrap 実行漏れを検出する。
  - 検証方法: `tests/cli_runtime/test_worktree.py`
  - 関連 closure id: `wt-core-004`
- `tc-s01-005` acceptance: linked worktree normalizes container
  - 前提: temp repo で linked worktree を作成済み。
  - 操作: linked worktree から `worktree create inner` を実行する。
  - 期待結果: main checkout の sibling container に worktree が作られる。
  - 失敗検出: linked 起点に nested container を作る回帰を検出する。
  - 検証方法: `tests/cli_runtime/test_worktree.py`
  - 関連 closure id: `wt-core-002`
- `tc-s01-006` negative: non-retryable failure reports artifact state
  - 前提: container creation failure または non-retryable `git worktree add` failure を発生させる。
  - 操作: `worktree create` または use case を実行する。
  - 期待結果: エラーに原因と `artifact_state=path_exists:<bool>,branch_exists:<bool>,record_exists:<bool>` が含まれる。
  - 失敗検出: partial artifact state を観測できない failure contract 回帰を検出する。
  - 検証方法: `tests/cli_runtime/test_worktree.py`
  - 関連 closure id: `wt-core-005`
- step closure contract:
  - `wt-core-001`..`wt-core-005` が targeted test で pass。
- report evidence destination:
  - `report.md` の Test Contract Closure / Step Contract Closure。
- step gate:
  - targeted test pass、code-reviewer pass、commit gate。

## S90 docs impact resolution / docs refresh
- この issue では docs 更新を行わず、iss-00109 に委譲する。

## S99 final quality gate
- epic final gate は iss-00109 で集約する。

## Final Exit Contract
- `python -m unittest tests.cli_runtime.test_worktree -v` が pass。
- core runtime files と tests の diff が issue requirement/design に追跡できる。
