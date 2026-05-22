---
種別: 設計書（Issue）
ID: "iss-00110"
タイトル: "Worktree create core use case"
関連GitHub: ["#110"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-05-22"
親: ["epic-00107", "init-local-00002"]
依存: ["requirement.md"]
---

# iss-00110 Worktree create core use case — 設計

## 方針
- `application/worktree.py` に pure orchestration を置き、Git と make の副作用は ports 経由に分離する。
- worktree list の stable input は `git worktree list --porcelain` とし、main worktree は Git の出力順の先頭として扱う。
- bootstrap は `BootstrapGateway` で `BootstrapResult` に集約し、failure を例外化しない。

## 変更点
- `application/contracts.py`
  - `GitWorktreeRecord`
  - `BootstrapResult`
  - `WorktreeCreateRequest`
  - `WorktreeCreateResult`
  - `UseCases.worktree_create`
- `application/ports.py`
  - `GitGateway.worktree_list`
  - `GitGateway.add_worktree_with_new_branch`
  - `BootstrapGateway`
  - `Ports.bootstrap_gateway`
- `application/worktree.py`
  - label validation、candidate generation、collision retry、bootstrap aggregation。
- `infra/git_cli.py`
  - porcelain parser、linked worktree add wrapper。
- `infra/make_cli.py`
  - `make -n init` detection と `make init` execution。

## 依存関係
```mermaid
flowchart TD
  command["commands/worktree.py"] --> usecase["application/worktree.py"]
  usecase --> gitport["GitGateway"]
  usecase --> bootport["BootstrapGateway"]
  gitport --> gitcli["infra/git_cli.py"]
  bootport --> makecli["infra/make_cli.py"]
```

## テスト戦略
- `tests/cli_runtime/test_worktree.py` で temp repo を作り、real Git worktree による integration evidence を取る。
- make は controlled Makefile で success path を検証し、missing target は real `make -n init` の skipped path で検証する。
- live checkout には worktree を作らず、temp directory のみ使う。

## ロールバック
- `application/worktree.py`、`infra/make_cli.py`、追加 contract と adapter method を削除すれば既存 command surface への影響を戻せる。
