---
種別: レポート（Issue）
ID: "iss-00536"
関連GitHub: ["#536"]
最終更新: "2026-11-04"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## Outcome

SpecDock 0.8.0 のリリース変更を作り、マージできる状態の PR にした。epic-00547 の iss-00555（画面の版）も兼ねる。マージ、タグ、導入、配布は統括が行う。

- 版を 0.8.0 にした（`pyproject.toml`、`uv.lock`、`system/spec-dock-version` の提供側と dogfood の写し）。
- `migration.md`（提供側と dogfood の写しはバイト一致）に「## 0.8.0 への更新」を足した。内容：文書の描画（#535：`/scopes/<ID>/doc[/<道>]`、scopes の `details` の spec・check・progress・adrs と `view`、`SERVER_RESTART_REQUIRED` の帯）、人のタスクの画面（#554：`/api/v1/todos`、`/api/v1/r/<repo>/todos[/<ID>]`、`specdock.todo-list/v1`、`DASHBOARD_TODO_FILTER_INVALID`、画面の道 `/todos` と印）、常駐の自動の起動し直し、戻し方。
- `static-inventory.json`：`migration.md` と版のファイルの今のハッシュを入れ、0.7.0 のバイト（タグ v0.7.0）を既知の古い版に足した。`reference_cli.md` は #535 が足し済み。fixture は `tests/fixtures/issue536/`。
- 統合テスト `tests/integration/test_issue536_release_0_8_0.py`：版、節と写しの一致、inventory、0.7.0 の配布資産を持つリポジトリが `installation update` で 0.8.0 に上がること。0.7.0 のテストの版固定は外した。機能のコードは変えていない。
- #567 と #568 は、PR を作る時点（origin/main = 5944fe1e1）で main に入っていないので書いていない。

## Verification

- 仕様のレビュー（spec-reviewer opus/medium）：合格（P0・P1 なし、P3 2件のうち文言2点を直した）。requirement 6ea59b89…、design 5f8f09c9…、plan 2ce223c7…（直す前の値）。
- コードのレビュー（code-reviewer sonnet/high、69fc8d73d）：合格。P3 1件（人のタスク1件の API の 409）を cb14d1b29 で直した。
- 最終品質ゲート（quality-gate-reviewer opus/high、1人、cb14d1b29104046b0b83f2e7dc4f45a7929d40e5）：レビューの段は P0〜P3 すべて 0、範囲は完全。テストの段は `make lint` 合格、`uv run pytest` 3699 passed、7 skipped、失敗 0（41分）。記録は `.workbench/final-quality-gate/iss-00536-g1/`。ChatGPT のレーンは使っていない（無効）。
- `spec-dock scope check iss-00536`：誤り0、警告0。

## Residual Risks / Follow-ups

- `spec-dock work start iss-00536` は、GitHub 上で iss-00535 が未完了のため `READINESS_NOT_SATISFIED` で止まった。統括が #535 を閉じた後に必要なら行う。この Issue の `work finish` もマージの後に統括が行う。
- #567・#568 がマージされたら、migration.md に足すかを統括が決める（足すなら provider の写し、dogfood の写し、inventory の sha256 の更新が要る）。
- マージの後：タグ v0.8.0、パッケージの導入、5つのリポジトリへの配布、画面の確かめは統括が行う。
