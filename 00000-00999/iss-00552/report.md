---
種別: レポート（Issue）
ID: "iss-00552"
関連GitHub: ["#552"]
最終更新: "2026-11-04"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## Outcome

ダッシュボードに出すリポジトリを、設定のファイルで決められるようにした（ブランチ `chemitaro/iss-00552`、最終のコミット `00ca86a50`）。

- 利用者の設定 `config.json`（`specdock.config/v1`）の `dashboard` の節：`visible`（全体の既定）と `repositories.<鍵>.visible`。
- リポジトリの設定：カタログの根の `dashboard.json`（`specdock.dashboard-settings/v1`、`visible`）。
- 優先：初めの値 true < 利用者の `visible` < 利用者の `repositories[鍵]` < リポジトリ（最も強い。統括と利用者の判断、2026-11-04）。`dashboard hide` の印は常に隠す。
- 壊れた設定は隠す側：利用者の設定のファイルが壊れていれば全部、カタログの `dashboard.json` が壊れているか2つのクローンで食い違えばそのリポジトリ。
- 規則は `domain/dashboard_visibility.py` の1か所。サーバー（`DashboardSite`）、`dashboard list`／`hide`／`show`、`dashboard summary`、`todo list`、隠れたリポジトリの直接のURLの案内が同じ答え（`read_visibility` は新しく作った `DashboardSite` の答え）を使う。
- 常駐（`dashboard service install`）は、install のときの絶対の `XDG_CONFIG_HOME` を launchd／systemd の環境に入れ、CLI と同じ設定のファイルを読む。

## Verification

- 仕様のレビュー（spec-reviewer opus/high）：round-1 合格（P2 3、P3 2 を取り込み）、round-2 合格（P2 1 を計画に取り込み）。
- コードのレビュー（code-reviewer opus/high、標準と仕様の2人）：1c4592c55 で両方合格。P2 3件（一覧の署名を読み取りの前に取る、葉のヘルプ、テストの閉じ方）を 35c164a38 で修正。
- 最終品質ゲート（quality-gate-reviewer opus/high、1人）：attempt 01（35c164a38）で P1 FQG-001（常駐が別の設定のファイルを読みうる）→ 00ca86a50 で修正。attempt 02（00ca86a50）でレビューの段 pass（P0 0、P1 0、P2 1、P3 3、範囲は完全）、テストの段 pass（`make lint` exit 0、`uv run pytest` exit 0：3640 passed、7 skipped）。記録はチェックアウトの `.workbench/final-quality-gate/iss-00552-gate-1/closure.md`。
- `spec-dock scope check iss-00552`：誤り0、警告0。

## 次の版の移行の注記に要る契約の変更

- `dashboard list`：各行に `mark`、`config {visible, source}`（`default`／`user`／`repository`／`invalid`、分からない行は `null`）、`hidden_by` を足し、data に `config_problems [{layer, path, reason}]` を足した。文字の出力は `hidden by=… config=…`。
- `dashboard hide`／`show`：data に `mark`、`config`、`hidden_by` を足した。`hidden` は書いた後の最終の値（`show` でも設定が隠せば true）。`show` は設定が隠すとき警告 `DASHBOARD_HIDDEN_BY_CONFIG`。
- `dashboard summary` と `todo list` の `hidden`：設定を含む最終の値。印のファイルが読めないときは true（前は false）。
- 隠れたリポジトリの直接のURL（`DASHBOARD_REPOSITORY_HIDDEN` の `next_steps` と HTML）：印なら `dashboard show`、設定なら `dashboard list` と `edit <道>`。
- 利用者の設定のファイルが読めない／JSON でない／`schema` が違う／`dashboard` の節が壊れていると、全リポジトリが隠れる（`todo` だけを使う利用者も。前は `todo` の段を飛ばす警告だけ）。
- 常駐の定義に `XDG_CONFIG_HOME`（install のときに絶対の道で設定されていれば）が入る。0.6.0 で常駐を入れ、`XDG_CONFIG_HOME` を使う利用者は、更新の後に `spec-dock dashboard service install` をやり直す（FQG-005）。
- 配布資産：`reference_cli.md`、`cli-redesign-guide.html` の sha256 を更新し、前の値を `known_old_sha256` に足した。

## Residual Risks / Follow-ups

- FQG-005（P2）：上の常駐のやり直しは自動ではない。
- FQG-002（P3）：`visible: null` と綴りを誤った項目は「値なし」として下の段に落ちる。
- FQG-003（P3）：チェックアウトの中の `todo list` の `hidden` を CLI で確かめるテストはない（`read_visibility` の `fallback_catalog` は単体で確かめた）。
- FQG-004（P3）：`serve` の「出るものがない」案内は設定のファイルの名を出さず、`dashboard list` を示す。
- 利用者が設定のファイルを編集の途中で壊すと、その間は全リポジトリが隠れる（安全側）。
