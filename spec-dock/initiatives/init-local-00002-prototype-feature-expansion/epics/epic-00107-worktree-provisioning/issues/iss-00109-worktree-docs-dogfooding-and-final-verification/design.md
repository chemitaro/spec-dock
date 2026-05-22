---
種別: 設計書（Issue）
ID: "iss-00109"
タイトル: "Worktree docs dogfooding and final verification"
関連GitHub: ["#109"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-05-22"
親: ["epic-00107", "init-local-00002"]
依存: ["requirement.md", "iss-00108"]
---

# iss-00109 Worktree docs dogfooding and final verification — 設計

## 方針
- provider docs を先に更新し、dogfooding workspace は shipped asset parity として同内容を持たせる。
- final verification は runtime tests と spec-dock validate/sync を分けて記録する。

## 変更点
- `src/spec_dock/assets/spec_dock/docs/reference_worktree.md`
- `src/spec_dock/assets/spec_dock/docs/guide.md`
- `spec-dock/docs/reference_worktree.md`
- `spec-dock/docs/guide.md`
- dogfooding `spec-dock/scripts/spec_dock_runtime/**` parity after update/copy path。

## テスト戦略
- docs は spec-reviewer の docs/spec alignment で確認する。
- runtime parity は `./spec-dock/scripts/spec-dock worktree create --help` と targeted tests で確認する。
- final tree は `./spec-dock/scripts/spec-dock validate` / `sync` で確認する。

## ロールバック
- docs additions と dogfooding copied runtime changes を provider assets と同期前の状態へ戻す。
