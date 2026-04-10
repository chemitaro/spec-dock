---
種別: disc
ID: "20260410t003309z-disc"
タイトル: "Why dependency metadata unification belongs to architecture initiative"
状態: "proposed"
作成者: "Codex CLI"
最終更新: "2026-04-10"
親: ["epic-00059"]
関連: ["epic-00033", "epic-00058", "#58"]
---

# 20260410t003309z-disc Why dependency metadata unification belongs to architecture initiative

## 議題 (必須)
- dependency metadata の SoT を `deps.json` から `.meta.json` へ統合する変更を、どの initiative/epic を正本として進めるかを確定する。
- 誤作成された `epic-00058`（`init-local-00002` 配下、削除済み）を履歴として扱い、canonical な実行場所を明確化する。

## 背景 (必須)
- 現行 SSOT は `deps.json` + `.meta.json` 分離で、`deps` は `check` のみ提供され mutation command がない。
- ユーザー要望は JSON 直編集回避と command 経由の安全な depends 変更である。
- `.meta.json` への統合は source-of-truth / persistence boundary / migration / downstream contract の更新を伴い、architecture initiative の guardrail に該当する。
- `epic-00058` は誤作成として削除済みで、GitHub issue #58 も close 済みである。

## 選択肢 (必須)
- Option A: `init-local-00002` 配下に `epic-00058` 相当を再作成して正本化
  - Pros:
    - 一見すると既存文脈に合わせやすい。
  - Cons:
    - architecture boundary 変更を prototype initiative に混在させることになり、initiative guardrail と不整合。
    - portfolio 上で SoT 変更の責務境界が曖昧になる。
- Option B: `init-local-00003` 配下の `epic-00059` を正本として継続
  - Pros:
    - source-of-truth/persistence/migration を architecture トラックで管理できる。
    - downstream contract 変更（delete/sync/active/validate）を同一 portfolio で追跡できる。
    - `epic-00058` の削除済み履歴を前提に、正本を一意に保てる。
  - Cons:
    - epic が重複して見える期間が発生する。

## 推奨案 (必須)
- Option B を採用する。
- 理由:
  - 本件は機能追加よりも状態境界の再定義が主であり、`init-local-00003-architecture-maintenance-and-hardening` の対象。
  - `epic-00033` は GitHub identity/ADR mirror を中心とした別契約で、dependency SoT 統合を内包していない。
  - `epic-00058` は誤作成として削除済みであり、canonical 実装・計画は `epic-00059` に集約する。

## 未決事項 (任意)
- dual-read 期間の終了条件（hard cutover のタイミング）。

## 次アクション (必須)
- `epic-00059` の requirement/design/plan を architecture scope で確定する。
- initiative `init-local-00003` の plan portfolio に `epic-00059` を追加する。
- validate/sync 実行結果を記録し、canonical epic として運用開始する。
