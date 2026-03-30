---
種別: レポート（Epic）
ID: "epic-00033"
タイトル: "GitHub backed identity and ADR mirror workflow"
状態: "approved"
作成者: "Codex CLI"
最終更新: "2026-03-30"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["init-local-00003"]
---

# epic-00033 GitHub backed identity and ADR mirror workflow — レポート（進捗 / 決定 / 結果）

## 進捗サマリー (必須)
- 現在地（何が完了し、何が未完か）:
  - `iss-00034` / `iss-00035` / `iss-00036` / `iss-00037` / `iss-00038` / `iss-00040` は完了済み。
  - `./spec-dock/scripts/spec-dock sync --github` 実行後の `spec-dock/.agent/index-all.json` では、GitHub issue `#38` が `CLOSED`、`iss-00038` は `status=done` / `effective_status=done` として反映されている。
  - 同じ generated state で epic progress は `total=6` / `done=6` / `open=0` / `unknown=0` である。
  - `spec-dock/dashboard.md` は `todo_total: 0`、`doing: 0`、`ready: 0`、`blocked: 0`、`unknown: 0` となっており、残る open issue summary は解消済みである。
- 次のマイルストーン:
  - issue-level completion evidence は揃っており、追加の open child issue はない。
- ブロッカー:
  - 実装ブロッカーはなし。

## 決定事項（ADRリンク） (必須)
- epic 専用の新規 ADR はなし。
- 本 epic の確定判断は `iss-00034` / `iss-00035` / `iss-00036` / `iss-00037` / `iss-00040` の issue-level evidence に集約し、epic では close 順序と達成状況だけを管理する。

## 完了した Issue / PR / Release (必須)
- `iss-00034` / GitHub `#34`: Done
- `iss-00035` / GitHub `#35`: Done
- `iss-00036` / GitHub `#36`: Done
- `iss-00037` / GitHub `#37`: Done（GitHub state: `CLOSED`）
- `iss-00038` / GitHub `#38`: Done（GitHub state: `CLOSED`）
- `iss-00040` / GitHub `#40`: Done（GitHub state: `CLOSED`）

## 受け入れ条件（E-AC）の達成状況 (必須)
- `E-AC-001`: Pass（証拠: `iss-00034` で GitHub mandatory node creation contract と canonical repo scope fail-closed 境界を固定）
- `E-AC-002`: Pass（証拠: `iss-00036` で timestamp-based discussion / ADR naming contract を固定）
- `E-AC-003`: Pass（証拠: `iss-00035` で ADR symlink mirror の clear-then-rebuild と stale link 除去を固定）
- `E-AC-004`: Pass（証拠: `iss-00034` / `iss-00036` の先行ガードに加え、`iss-00037` で migration boundary clause-1/2/3 の closure evidence を確定）
- `E-AC-005`: Pass（証拠: `iss-00040` の stale-contract / test-realignment slice と `iss-00038` の docs parity / final spec review close-out が完了し、`sync --github` 後の generated state が `done=6/open=0` と `todo_total: 0` を示している）

## ロールアウト結果（必要なら） (任意)
- 段階公開の状況:
  - 該当なし。repo 内 contract / docs / validation close-out として進行中。
- 監視値（エラー率/レイテンシなど）:
  - 該当なし。
- 障害/アラート:
  - 該当なし。

## フォローアップ（別Issue化） (必須)
- 現時点で追加の follow-up issue はなし。

## 省略/例外メモ (必須)
- child issue の authoritative state は `sync --github` 後に `done=6` / `open=0` / `todo_total: 0` まで揃っている。
- 一方で `spec-dock/.agent/index-all.json` 上の epic GitHub issue `#33` 自体の state は `OPEN` のままであり、この report の `状態: approved` は child issue completion と acceptance evidence の完了を表す。
