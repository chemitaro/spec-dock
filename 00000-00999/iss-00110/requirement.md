---
種別: 要件定義書（Issue）
ID: "iss-00110"
タイトル: "Worktree create core use case"
関連GitHub: ["#110"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-05-22"
親: ["epic-00107", "init-local-00002"]
---

# iss-00110 Worktree create core use case — 要件定義

## 目的
- `spec-dock worktree create` の中核となる application contract と Git / bootstrap adapter contract を実装する。
- main checkout の兄弟に `<repo-basename>-worktrees/` を作る長命 worktree 運用を、CLI surface から独立してテスト可能にする。

## スコープ
- 必須:
  - worktree id、directory、branch の候補生成。
  - Git main worktree を基準にした container path 正規化。
  - directory / branch / worktree record collision の retry。
  - optional / non-fatal `make init` bootstrap result aggregation。
- 禁止:
  - Codex app managed worktree の再実装。
  - `worktree remove` / `status` / `prune`。
  - spec tree metadata の mutation。
- 対象外:
  - CLI parser / text rendering の詳細。
  - shipped docs の追加。

## 受け入れ条件
- AC-001: main checkout から LABEL なしで作成すると、`wt1`、`<repo>-worktrees/<repo>-wt1`、`<current-branch>-wt1` が選ばれる。
- AC-002: 同じ条件で繰り返すと collision を検出し、次候補 `wt2` または `<label>2` に進む。
- AC-003: LABEL は `^[a-z0-9-]+$` のみ許可し、不正な値は worktree 作成前に fatal error になる。
- AC-004: linked worktree から実行しても container path は main worktree の兄弟になり、branch prefix は実行元 checkout の current branch になる。
- AC-005: `make init` がない場合は skipped、成功時は succeeded、検出失敗または実行失敗は warning として result に残り、worktree 作成自体は成功扱いになる。
- AC-006: detached HEAD、Git repo 外、path creation failure、non-retryable Git failure は fatal error になる。

## 例外・エッジケース
- EC-001: branch exists / path exists / Git worktree record exists は retryable collision。
- EC-002: retry ceiling `10000` を超えた場合は label mode、last attempted id、container path、reason を含む fatal error。
- EC-003: generated branch が Git ref として不正な場合は fatal error。

## 未確定事項
- なし。
