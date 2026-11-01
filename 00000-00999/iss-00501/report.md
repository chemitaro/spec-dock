---
種別: レポート（Issue）
ID: "iss-00501"
関連GitHub: ["#501"]
最終更新: "2026-11-02"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

SpecDock 0.4.2 の版と文書を用意した。製品コードの振る舞いは変えていない。

## Outcome

- 版を 0.4.2 にした（pyproject.toml、uv.lock、system/spec-dock-version と dogfood の写し、版を固定したテスト）。
- migration.md（提供側と dogfood の写し）に「## 0.4.2 への更新」を足した。
- static-inventory.json に、migration.md と spec-dock-version の 0.4.1 のバイトを既知の古い版として足した。#500 で変わった canonical.md と spec-dock-check.yml の 0.4.1 のバイトは、すでに既知の古い版に入っていた（足していない）。
- テスト：tests/integration/test_issue501_release_0_4_2.py を足し、0.4.1 の4資産（migration.md、spec-dock-version、canonical.md、spec-dock-check.yml）を持つリポジトリが `installation update` で上がることを確かめた。0.4.1 の版を固定していた旧テスト1件は削除した（新しいテストが担う）。
- コミット：24ecdae2c、5a7552b67。

## Verification

- 仕様のレビュー（opus/medium）：P0/P1/P2/P3 なし（1回で合格）。
- コードのレビュー（sonnet/high）：24ecdae2c で指摘なし。
- 最終品質ゲート（opus/high、1人）：1回目の 24ecdae2c で P1 1件（旧版固定テストの取り残し）。5a7552b67 で直し、2回目で P0〜P3 なし、範囲の確認は完了。
- テスト：5a7552b67 で make lint と uv run pytest -q が終了コード0（4092 passed、8 skipped）。
- 新しい wheel を一時の venv に入れ、spec-dock --version が 0.4.2 を返した。

## Residual Risks / Follow-ups

- マージで release-tag.yml が v0.4.2 を作る。タグは作っていない。
