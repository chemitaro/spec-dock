---
種別: レポート（Issue）
ID: "iss-00494"
関連GitHub: ["#494"]
最終更新: "2026-11-01"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

## Outcome

- 見本 `spec-dock-check.yml` の先頭に、ホスト runner の費用、`on` と `runs-on` を変えてよいこと、`workflow_dispatch` のみ、`.githooks/pre-push` で `spec-dock canonical check --json` を回す形を注記のコメントで足した。`branches: [main]` の行などは変えていない（CLI の動きは不変）。
- `canonical.md` に「CI の費用と、見本の合わせ方」の節を足した。dogfood の写し（`spec-dock/docs/`）も同じ内容。
- `static-inventory.json` のハッシュを更新し、前の版（canonical.md `4ee1612f…`、見本 `715ba586…`）を `known_old_sha256` に足した。
- 仕様レビューの P2 を受け入れ、`scripts/migrate-to-canonical/migrate.py` の `WORKFLOW_SAMPLE_BYTES`（見本のバイトの写し。`test_migration_contract_copies` が一致を縛る）にも同じ注記を足した。`migrate.py cut` が生成する workflow にも注記が入る。
- `test_issue434_version_file.py` は見本が `name:` で始まることを縛っていたので、先頭のコメント行を除いて構造を比べるよう直した。
- 要件（`requirement.cue`）は変えていない。

## Verification

- コミット `5c26f5ac7c3191220c7628eb065a508881118dfc`。
- 仕様レビュー（spec-reviewer opus/medium）: P0/P1 なし、P2 1件（上記 migrate.py、対応済み）。
- コードレビュー（code-reviewer sonnet/high）: 指摘なし。
- 最終品質ゲート（quality-gate-reviewer opus/high、1人）: review pass、P0〜P3 なし、coverage 完全。テストレーン pass（`make lint` exit 0、`uv run pytest` exit 0、4056 passed / 8 skipped）。同一コミットで、作業ツリーは clean。証拠: `.workbench/final-quality-gate/iss-00494/attempts/01/`。
- `spec-dock scope check iss-00494`: 誤り・警告 0。

## Residual Risks / Follow-ups

- なし。版の番号は変えていない（0.4.2 は別の Issue）。
