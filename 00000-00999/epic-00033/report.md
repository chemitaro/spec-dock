---
種別: レポート（Epic）
ID: "epic-00033"
タイトル: "GitHub backed identity and ADR mirror workflow"
状態: "draft"
作成者: "Codex CLI"
最終更新: "2026-03-30"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["init-local-00003"]
---

# epic-00033 GitHub backed identity and ADR mirror workflow — レポート（進捗 / 決定 / 結果）

## 進捗サマリー (必須)
- 現在地（何が完了し、何が未完か）:
  - `iss-00034` / `iss-00035` / `iss-00036` / `iss-00040` は完了済み。
  - `iss-00037` は GitHub `#37` が `CLOSED`、`status=done` / `effective_status=done` として反映済み。
  - `./spec-dock/scripts/spec-dock sync --github` 実行後の `spec-dock/.agent/index-all.json` では、epic progress は `total=6` / `done=5` / `open=1` / `unknown=0`。
  - 残る open issue は `iss-00038` のみで、`status=open` かつ `deps.ready=true` のため、次の着手対象は明確になっている。
- 次のマイルストーン:
  - `iss-00038` を着手し、docs parity、final spec review record、epic close-out evidence を閉じる。
  - `iss-00038` を完了させて、`epic-00033` の最後の open slice を解消する。
- ブロッカー:
  - 実装ブロッカーはなし。
  - 残作業は `iss-00038` の close-out 実行のみ。

## 決定事項（ADRリンク） (必須)
- epic 専用の新規 ADR はなし。
- 本 epic の確定判断は `iss-00034` / `iss-00035` / `iss-00036` / `iss-00037` / `iss-00040` の issue-level evidence に集約し、epic では close 順序と達成状況だけを管理する。

## 完了した Issue / PR / Release (必須)
- `iss-00034` / GitHub `#34`: Done
- `iss-00035` / GitHub `#35`: Done
- `iss-00036` / GitHub `#36`: Done
- `iss-00040` / GitHub `#40`: Done
- `iss-00037` / GitHub `#37`: Done（GitHub state: `CLOSED`）

## 受け入れ条件（E-AC）の達成状況 (必須)
- `E-AC-001`: Pass（証拠: `iss-00034` で GitHub mandatory node creation contract と canonical repo scope fail-closed 境界を固定）
- `E-AC-002`: Pass（証拠: `iss-00036` で timestamp-based discussion / ADR naming contract を固定）
- `E-AC-003`: Pass（証拠: `iss-00035` で ADR symlink mirror の clear-then-rebuild と stale link 除去を固定）
- `E-AC-004`: Pass（証拠: `iss-00034` / `iss-00036` の先行ガードに加え、`iss-00037` で migration boundary clause-1/2/3 の closure evidence を確定）
- `E-AC-005`: Partial（達成済み: `iss-00040` の stale-contract / test-realignment slice。残り: `iss-00038` の docs parity と final spec review close-out）

## ロールアウト結果（必要なら） (任意)
- 段階公開の状況:
  - 該当なし。repo 内 contract / docs / validation close-out として進行中。
- 監視値（エラー率/レイテンシなど）:
  - 該当なし。
- 障害/アラート:
  - 該当なし。

## フォローアップ（別Issue化） (必須)
- `iss-00038`:
  - docs parity の最終確認と provider / dogfooding docs の close-out evidence をまとめる。
  - final spec review record を `pass` で閉じ、`epic-00033` の最終 exit evidence を完成させる。
  - `status=open` かつ `deps.ready=true` の、単独で着手可能な最後の open issue として扱う。

## 省略/例外メモ (必須)
- 本レポート時点では `iss-00037` は `done` / `effective_status=done` / GitHub `CLOSED` まで反映済みであり、`sync --github` 後の epic progress も `total=6` / `done=5` / `open=1` / `unknown=0` に更新済みである。
- `iss-00038` は docs parity と final spec review close-out の owner であり、`iss-00040` が閉じた stale-contract/test-realignment slice を再実行する前提ではない。
