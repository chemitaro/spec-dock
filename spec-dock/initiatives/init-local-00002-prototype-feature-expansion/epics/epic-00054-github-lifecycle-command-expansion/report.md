---
種別: レポート（Epic）
ID: "epic-00054"
タイトル: "GitHub lifecycle command expansion"
状態: "draft | approved"
作成者: "Codex CLI"
最終更新: "2026-04-09"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["init-local-00002"]
---

# epic-00054 GitHub lifecycle command expansion — レポート（進捗 / 決定 / 結果）

## 進捗サマリー (必須)
- 現在地（何が完了し、何が未完か）:
  - `iss-00055` と `iss-00056` の 2 issue はともに完了し、epic が要求した GitHub close capability と local delete capability は dogfooding repo 上で実装・検証・close-out まで完了した。
  - `epic-00054` の linked GitHub issue `#54` は CLOSED、`iss-00056` も GitHub / local ともに close-out 済みである。
  - implementation review / qa review は最終差分で pass、dogfooding sync 後の progress は `done=2 / open=0` である。
- 次のマイルストーン:
  - なし。epic close-out 完了。
- ブロッカー:
  - なし。

## 決定事項（ADRリンク） (必須)
- 決定:
  - GitHub-side issue delete は事故リスクが高いため、この epic の success path から除外し、remote handling は close-only とする。
  - local spec node delete は issue / epic / initiative の directory removal を対象に含める。

## 完了した Issue / PR / Release (必須)
- `iss-00055`:
  - close command 実装、review、commit、GitHub close dogfooding を完了。
- `iss-00056`:
  - local spec node delete、parent recursive delete、dependency scrub、partial failure handling、epic final close-out を完了。

## 受け入れ条件（E-AC）の達成状況 (必須)
- E-AC-001: 完了（証拠: `iss-00055` で `close` command を実装し、`close --id iss-00055` / `sync --github` を dogfooding 実行）
- E-AC-002: 完了（証拠: `iss-00056` で issue / epic / initiative target の local delete guardrail と parent recursive delete を実装）
- E-AC-003: 完了（証拠: `iss-00056` で `close --id iss-00056` と `close --id epic-00054` を実行し、`sync --github` 後に `iss-00056.status=done`, `epic-00054.github.state=CLOSED`, `epic-00054.progress.done=2` を確認）
- E-AC-004: 完了（証拠: epic requirement / design / plan / issue reports / provider+dogfooding docs / generated dashboard を更新）

## ロールアウト結果（必要なら） (任意)
- 段階公開の状況:
  - 該当なし。planning-stage のみ。
- 監視値（エラー率/レイテンシなど）:
  - 該当なし。
- 障害/アラート:
  - 該当なし。

## フォローアップ（別Issue化） (必須)
- optional-hardening:
  - raw int dependency ref 専用 scrub 回帰、`json_store` 経路 scrub 回帰、childless parent の `--recursive` 専用回帰は non-blocking follow-up 候補として残る。

## 実装更新（2026-04-10）
- `iss-00055` は close command 実装と close-out まで完了済みである。
- `iss-00056` は close-out まで完了し、parent recursive delete、remote close barrier、dependency scrub、partial failure payload、topology load failure fail-closed が provider-side runtime に実装された。
- 最新検証は `python -m unittest -v tests.cli_runtime.test_runtime_delete_s13 tests.cli_runtime.test_delete tests.cli_runtime.test_runtime_shell_s11 tests.cli_runtime.test_runtime_close_s12 tests.cli_runtime.test_runtime_active_s06 tests.cli_runtime.test_runtime_deps_s04 tests.cli_runtime.test_close` で `Ran 108 tests ... OK`、`./spec-dock/scripts/spec-dock validate` で `spec-dock: ok (validate) nodes=17` である。
- `iss-00056` の implementation review / qa review は pass。non-blocking として raw int dependency ref 専用回帰と `json_store` 経路 scrub 回帰に追加余地が残る。
- close-out 実行として `close --id iss-00056`、`sync --github`、`close --id epic-00054`、`sync --github` を通し、epic final evidence を固定した。

## 省略/例外メモ (必須)
- 本 epic は dogfooding feedback の記録と今後の実装計画を固定するために開いたものであり、2026-04-08 時点では code change を伴う execution は行っていない。
