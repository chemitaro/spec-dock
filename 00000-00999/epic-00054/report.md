---
種別: レポート（Epic）
ID: "epic-00054"
タイトル: "GitHub lifecycle command expansion"
状態: "draft | approved"
作成者: "Codex CLI"
最終更新: "2026-04-08"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["init-local-00002"]
---

# epic-00054 GitHub lifecycle command expansion — レポート（進捗 / 決定 / 結果）

## 進捗サマリー (必須)
- 現在地（何が完了し、何が未完か）:
  - 2026-04-08 の dogfooding feedback を受けて epic を起票し、requirement / design / plan を planning-stage として作成した。
  - 実装、テスト、review は未着手であり、現時点では docs 上で feature scope と safety boundary を固定した段階である。
  - review-only issue は不自然という判断に基づき、epic は 2 issue 構成へ再整理した。各 issue 自身が review と success verification を持ち、第2 issue が epic final close-out を担う。
- 次のマイルストーン:
  - planned-issue-01-close-linked-github-issues を起票し、close command の contract を issue 単位へ分解する。
- ブロッカー:
  - 現時点で実装ブロッカーは未調査。`gh` 権限、partial failure design、destructive guardrail の確定は follow-up issue で扱う。

## 決定事項（ADRリンク） (必須)
- 決定:
  - GitHub-side issue delete は事故リスクが高いため、この epic の success path から除外し、remote handling は close-only とする。
  - local spec node delete は issue / epic / initiative の directory removal を対象に含める。

## 完了した Issue / PR / Release (必須)
- 該当なし:
  - epic 起票直後の planning-stage であり、完了済み implementation issue はまだない。

## 受け入れ条件（E-AC）の達成状況 (必須)
- E-AC-001: 未着手（証拠: planning only、implementation 未着手）
- E-AC-002: 未着手（証拠: planning only、implementation 未着手）
- E-AC-003: 未着手（証拠: planning only、implementation 未着手）
- E-AC-004: 進行中（証拠: 2026-04-08 に epic requirement / design / plan を作成し、docs scope を固定）

## ロールアウト結果（必要なら） (任意)
- 段階公開の状況:
  - 該当なし。planning-stage のみ。
- 監視値（エラー率/レイテンシなど）:
  - 該当なし。
- 障害/アラート:
  - 該当なし。

## フォローアップ（別Issue化） (必須)
- planned-issue-01-close-linked-github-issues:
  - linked GitHub issue close command。docs/tests/review/success verification までこの issue で閉じる。
- planned-issue-02-delete-local-spec-nodes-with-guardrails:
  - local delete and subtree safety。docs/tests/review/success verification に加えて、epic final review / final validation / close-out evidence をこの issue で閉じる。

## 実装更新（2026-04-10）
- `iss-00055` は close command 実装と close-out まで完了済みである。
- `iss-00056` は S03 I1 まで完了し、parent recursive delete、remote close barrier、dependency scrub、partial failure payload、topology load failure fail-closed が provider-side runtime に実装された。
- 最新検証は `python -m unittest -v tests.cli_runtime.test_runtime_delete_s13 tests.cli_runtime.test_delete tests.cli_runtime.test_runtime_shell_s11 tests.cli_runtime.test_runtime_close_s12 tests.cli_runtime.test_runtime_active_s06 tests.cli_runtime.test_runtime_deps_s04 tests.cli_runtime.test_close` で `Ran 108 tests ... OK`、`./spec-dock/scripts/spec-dock validate` で `spec-dock: ok (validate) nodes=17` である。
- `iss-00056` の implementation review / qa review は pass。non-blocking として raw int dependency ref 専用回帰と `json_store` 経路 scrub 回帰に追加余地が残る。
- 未完は commit、`sync --github` を含む final evidence 固定、`iss-00056` close、epic close-out である。

## 省略/例外メモ (必須)
- 本 epic は dogfooding feedback の記録と今後の実装計画を固定するために開いたものであり、2026-04-08 時点では code change を伴う execution は行っていない。
