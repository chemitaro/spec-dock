---
種別: 要件定義書（Issue）
ID: "iss-00108"
タイトル: "Worktree create CLI and output"
関連GitHub: ["#108"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-05-22"
親: ["epic-00107", "init-local-00002"]
---

# iss-00108 Worktree create CLI and output — 要件定義

## 目的
- core use case を `./spec-dock/scripts/spec-dock worktree create [LABEL]` として公開する。
- 成功時に absolute path、id、branch、bootstrap status を読める CLI output を提供する。

## スコープ
- 必須:
  - `worktree create` parser / registry / command wiring。
  - `UseCases.worktree_create` bootstrap wiring。
  - CLI text rendering。
- 禁止:
  - core naming / bootstrap rule の再定義。
  - docs-only の拡張。

## 受け入れ条件
- AC-001: `worktree create` が runtime help と dispatch に存在する。
- AC-002: 成功時 output が id、branch、absolute path、bootstrap status を含む。
- AC-003: invalid label や fatal use-case error は existing dispatch error path で non-zero になる。

## 未確定事項
- なし。
