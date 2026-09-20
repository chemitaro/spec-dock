---
種別: レポート（Issue）
ID: "iss-00396"
タイトル: "固定ディレクトリ再配置への実装切替"
関連GitHub: ["#396"]
最終更新: "2026-09-19"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00384", "init-local-00003"]
---

# Result Summary

詳細: [Report Guide](../../../../../../docs/authoring/report.md)

## Outcome

EpicとIssueの要件・設計・計画を再構成し、固定6ディレクトリの削除・コピー方式へ切り替えた。旧provider lifecycle、世代認証、専用性能認証・台帳・旧保証のテストを撤去した。利用者データは固定ツール領域の外に置き、変更しない。

- `ec58f902`: Epic/Issueの仕様再構成。
- `57fb67b2`: installer/runtime/テスト/CI/配布文書の切替。730行追加・28,462行削除（生成物と廃止テストを含む）。
- Strictレビューで新規initの配布元全体に対する重複検査漏れを検出。独立分析後、既存preflightに同じ重複判定を5行追加する修正を実施した。

## Verification

`57fb67b23e6316311fa2c801b5d819781581d737`:

- `uv run pytest -q --tb=short`: 1546 passed / 25 skipped / 0 failed、703.46秒。
- `make lint`: Ruff check/format、Mypy成功。
- `./spec-dock/scripts/spec-dock validate`: 236 nodes、成功。
- Strictコードレビュー（GPT-5.6 Extra High）: P1 1件、P2 1件。新規コピーの配布元重複検査不足がP1。

修正検証:

- 上記SHAにテストだけを追加したFirst Red: `overlapping source reached copy` で失敗。
- 5行の修正後、installer 10テスト成功、lint成功。
- 最終候補の全試験・再レビュー・Final Quality Gateは別の証拠として取得する。最終結果と対象SHAはPRに記録する。

## Residual Risks / Follow-ups

- 更新は非transactional。更新中はruntimeを停止し、失敗後は外部installerのupdateを再実行する。
- 管理ディレクトリ内のローカル変更は全て置換する。個別ファイル保持、自動rollback、世代証明は提供しない。
- レビューのP2は配布README内の旧recovery説明の残存。レビュー方針に従い情報として記録し、この修正では変更していない。
- 人間によるPR merge前の段階であり、このレポートはFinal Quality Gate合格やIssue完了を宣言しない。

## 第2回レビューと契約の整理

`dabdf0a2`: 全pytestは1547 passed / 25 skipped、lint/validate成功。PR #404の全CIも成功（Linux provider-tests 1542 passed / 30 skipped、macOS/Ubuntuの基本試験各11 passed）。第2回Strictレビューでは初回失敗後の初期設定修復についてP1が残った。ユーザーが要求した個別管理の撤去を優先し、要件と設計でupdate再配置と初回initやり直しを明確に区別した。新しい状態管理やファイル別seed処理は追加していない。修正後のレビュー結果は別途取得する。
