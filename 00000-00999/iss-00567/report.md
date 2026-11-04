---
種別: レポート（Issue）
ID: "iss-00567"
関連GitHub: ["#567"]
最終更新: "2026-11-04"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## Outcome

- `cue.md`（実行の割り当ての節と全体の例）と Issue の `plan.cue` 雛形のコメントの例を、`spec`（仕様化）と `impl`（実装）の2セッションに分けた。手順の `session` は `impl` を指すと書き、「セッションのモデルと推論は起動のときに決まるので、計画で選べるのは、計画の後に起動するセッション（実装担当）の値。計画を書いたセッションの値は事実として記録する」を添えた。`execution` の型と検査は変えていない。
- epic・initiative の雛形の例は `coord` のセッションで、仕様化と実装の混在がないため変えていない。
- dogfood の写し（`spec-dock/docs/authoring/cue.md`、`spec-dock/templates/cue/issue/plan.cue`）と `static-inventory.json` の sha256 を合わせ、前の sha256 を `known_old_sha256` に足した。
- テスト：`tests/integration/test_issue567_execution_example.py` を追加。`test_issue489_cue_plan_template.py` と `test_issue477_authoring_docs.py` は、旧版が複数になった期待に合わせた。
- 次の版の移行の注記に要る契約の変更：`cue.md` と Issue の `plan.cue` 雛形の内容が変わった（`installation update` で更新される。旧版の sha256 は既知として受け付ける）。型・CLI・検査の挙動の変更はない。

## Verification

- 仕様のレビュー：`spec-reviewer`（opus / medium）。P0〜P3 は 0 件。requirement／design／plan の sha256 は 8f106230…、3eaa1d41…（plan は完了後の状態に更新）。
- コードのレビュー：`code-reviewer`（sonnet / high）、`ef06748aa` で P0〜P3 は 0 件。
- 最終品質ゲート：`quality-gate-reviewer`（opus / high、1人）と テスト lane が、`origin/main`（5944fe1e1）を取り込んだ `4d9946bcb0adb75f702f8557fd183f2b7739fe5a` で合格。レビューは P0/P1 が 0、網羅は完了、P3 が 1。`make lint` は exit 0、`uv run pytest` は 3700 passed / 7 skipped。
- 記録：`.workbench/final-quality-gate/iss-00567/`（campaign.json、attempts/01/）。

## Residual Risks / Follow-ups

- P3（FQG-001）：T-01 のテストは、cue.md の全体の例に `spec` が残ることまで厳密には確かめない（回帰の見逃しの可能性は小さい）。対応しない。
- ゲート後の変更は、この `report.md` と `plan.cue` の status 更新（record_paths）に限る。
