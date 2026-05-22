---
種別: 設計書（Issue）
ID: "iss-00108"
タイトル: "Worktree create CLI and output"
関連GitHub: ["#108"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-05-22"
親: ["epic-00107", "init-local-00002"]
依存: ["requirement.md", "iss-00110"]
---

# iss-00108 Worktree create CLI and output — 設計

## 方針
- 既存 command pattern に合わせて `commands/worktree.py` を追加し、parser の `worktree` group へ `create` leaf を bind する。
- text rendering は `presentation/cli_text.py` に閉じ、command handler は request/result 変換だけを行う。

## 変更点
- `commands/worktree.py`: argument parsing と use case call。
- `cli/parser.py`: `worktree create [LABEL]` subcommand。
- `cli/registry.py`: command specs registration。
- `cli/bootstrap.py`: application use case と infra gateways wiring。
- `presentation/cli_text.py`: `render_worktree_create_text`。

## テスト戦略
- `tests/cli_runtime/test_worktree.py` の runtime command tests で parser/registry/bootstrap/rendering を統合確認する。
- invalid label の non-zero は dispatch error path の smoke として確認する。

## ロールバック
- `worktree` command spec と parser group を削除すれば command surface を戻せる。
