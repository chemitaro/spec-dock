---
種別: レポート（Issue）
ID: "iss-00520"
関連GitHub: ["#520"]
最終更新: "2026-11-02"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## Outcome

- 親を `completed` で閉じる判定を `require_descendants_settled`（`scope_completion_plan.py`）に1か所にまとめ、`plan_close`（scope close）と `_finish_rules`（work finish）が呼ぶ。子孫が `completed` か `not-planned` なら通り、`open` か `unknown` なら `DESCENDANT_NOT_COMPLETED`（終了コード3）で止まる。
- `reference_cli.md`（C10）、`cli-redesign-guide.html`、`SKILL.md`、`scope close` のヘルプ文言を更新。dogfood の写しと `static-inventory.json` のハッシュを揃え、0.5.0 のバイトを `known_old_sha256` に追加（テスト `test_issue520_descendant_docs.py`）。
- 契約の変更（0.5.1 の migration.md 向け）: 不採用の子孫を持つ親の `scope close` / `work finish` は、終了コード3（`DESCENDANT_NOT_COMPLETED`）から0（成功）に変わる。コード・JSON の形は不変。
- `requirement.cue` は変更なし。

## Verification

- 仕様レビュー（spec-reviewer opus/medium）: pass、P0/P1=0、P2=2（計画に既存テストの書き換えを追記、design の compatibility に migration 引き継ぎを追記）。
- コードレビュー（code-reviewer sonnet/high）: pass、P2=1（help 文言の取り残し → 修正済み ae2872c5b）。
- 最終品質ゲート（quality-gate-reviewer opus/high）: ae2872c5bc309ecbcdb89f0a2b5bb7bc1420bd33 で pass、coverage complete、P0/P1=0、P2=1（unknown 子孫のテスト欠如。情報のみ）。
- テストレーン同コミット: `make lint` exit 0、`uv run pytest` exit 0（3261 passed, 7 skipped）。証拠: `.workbench/final-quality-gate/iss-00520/closure.md`。

## Residual Risks / Follow-ups

- `unknown` の子孫で止まるテストは、既存の `require_known_descendants` の経路に依存し、本 Issue では追加していない（P2）。
- #506 と `scope close` の流れ・`static-inventory.json` で衝突しうる。後にマージするほうが main を取り込む。
