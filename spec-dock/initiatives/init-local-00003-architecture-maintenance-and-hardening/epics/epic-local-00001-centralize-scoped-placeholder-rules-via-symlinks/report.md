---
種別: レポート（Epic）
ID: "epic-local-00001"
タイトル: "Centralize scoped placeholder rules via symlinks"
状態: "approved"
作成者: "Codex CLI"
最終更新: "2026-03-26"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["init-local-00003"]
---

# epic-local-00001 Centralize scoped placeholder rules via symlinks — レポート（進捗 / 決定 / 結果）

## 進捗サマリー (必須)
- 現在地（何が完了し、何が未完か）:
  - `iss-00031` で provider assets / installed docs / checked-in mirror / checked-in runtime mirror / runtime create-import flow / tests / packaging evidence まで branch 上の実装・検証は完了しており、epic scope の残実装タスクはない。generated-state も `sync --github` 後は `authority=github` / `state=OPEN` / `stale=false` まで反映済み。
- 次のマイルストーン:
  - GitHub issue / PR lifecycle の close-out を別アクションで反映する。
- ブロッカー:
  - なし。

## 決定事項（ADRリンク） (必須)
- `spec-dock/active/issue/discussions/001-disc-rules-source-of-truth-placement.md`: canonical な user-facing rules source-of-truth は `spec-dock/docs/rules/**` とし、provider-side `src/spec_dock/assets/spec_dock/docs/rules/**` は package に同梱する authoring/source files として扱う。
- `iss-00031` requirement / design / plan: wrapper は復活させず、新規 node 作成時に `rules.md` symlink を明示配置する最小実装で揃える。

## 完了した Issue / PR / Release (必須)
- `iss-00031`: branch 上の実装・証拠は完了（証拠: `spec-dock/active/issue/report.md` S01-S03, S99）。`./spec-dock/scripts/spec-dock sync --github` 後の generated-state では `authority=github` / `state=OPEN` / `stale=false` まで反映済みで、issue lifecycle close は GitHub issue close 後の別アクションとなる。
- PR:
  - なし（local repository 作業として完了）。
- Release:
  - なし。

## 受け入れ条件（E-AC）の達成状況 (必須)
- E-AC-001: Pass（証拠: `spec-dock/active/issue/report.md` S02; `tests/test_init_update.py` 75 tests OK）
- E-AC-002: Pass（証拠: `spec-dock/active/issue/report.md` S01; `tests.cli_runtime.test_runtime_new_s08`, `tests.cli_runtime.test_new`）
- E-AC-003: Pass（証拠: `spec-dock/active/issue/report.md` S03, S99; `tests.cli_runtime.test_wrappers`, `tests.cli_runtime.test_import`, `tests.cli_runtime.test_runtime_import_s10`, `python -m unittest discover -v` 464 tests OK）

## ロールアウト結果（必要なら） (任意)
- 段階公開の状況:
  - 該当なし（local CLI / docs / tests contract change のため段階公開なし）。
- 監視値（エラー率/レイテンシなど）:
  - 該当なし。
- 障害/アラート:
  - なし。

## フォローアップ（別Issue化） (必須)
- なし。

## 省略/例外メモ (必須)
- PR / release は今回の close-out 時点では未作成で、generated-state 上の close 反映も未実施。
