---
種別: レポート（Issue）
ID: "iss-00491"
関連GitHub: ["#491"]
最終更新: "2026-11-01"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

SpecDock 0.4.1 の版と文書を用意した。製品コードの振る舞いは変えていない。

## Outcome

- 版を 0.4.1 にした（pyproject.toml、uv.lock、system/spec-dock-version と dogfood の写し、版を固定したテスト）。
- migration.md（提供側と dogfood の写し）に「## 0.4.1 への更新」を足した。
- static-inventory.json に、migration.md と spec-dock-version の 0.4.0 のバイトを既知の古い版として足した。ほかに変わった配布資産は #488・#490 で済んでいた。
- scripts/migrate-to-canonical/README.md の撤去の版を 0.5.0 にした。
- コミット：8b0be3687、889d9f2b0（整形）。

## Verification

- 仕様のレビュー（opus/medium）：P0/P1 なし、P3 1件（前のラウンドなし、1回で合格）。
- コードのレビュー（sonnet/high）：8b0be3687 で指摘なし。
- 最終品質ゲート（opus/high、1人）：889d9f2b0 で合格、P0/P1 なし、P3 1件（変わった配布資産8件のうち2件だけ 0.4.0 のバイトで更新を試している。残り6件の既知の古い版は #488・#490 のテストが担う）。
- テスト：同じ 889d9f2b0 で make lint と uv run pytest -q が終了コード0（4051 passed、8 skipped）。
- 新しい wheel を一時の venv に入れ、spec-dock --version が 0.4.1 を返した。

## Residual Risks / Follow-ups

- マージで release-tag.yml が v0.4.1 を作る。タグは作っていない。
