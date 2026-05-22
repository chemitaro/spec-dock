---
種別: 要件定義書（Issue）
ID: "iss-00109"
タイトル: "Worktree docs dogfooding and final verification"
関連GitHub: ["#109"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-05-22"
親: ["epic-00107", "init-local-00002"]
---

# iss-00109 Worktree docs dogfooding and final verification — 要件定義

## 目的
- `worktree create` の shipped docs と dogfooding workspace を整え、epic 全体の verification evidence を集約する。

## スコープ
- 必須:
  - provider-side docs under `src/spec_dock/assets/spec_dock/docs/`。
  - dogfooding docs / runtime parity。
  - targeted tests、full relevant tests、`validate`、`sync`。
  - Codex-managed worktree は scope 外であることの明記。
- 禁止:
  - feature scope を `remove` / `status` / `prune` へ広げる。

## 受け入れ条件
- AC-001: shipped docs と dogfooding docs が `worktree create [LABEL]`、sibling container、bootstrap rule、scope boundary を説明する。
- AC-002: dogfooding runtime で `worktree create` command が存在する。
- AC-003: final verification で targeted runtime tests、validate、sync が pass する。
- AC-004: final report が E-AC-001..E-AC-011 を closure evidence に紐付ける。

## 未確定事項
- なし。
