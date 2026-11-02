---
種別: レポート（Issue）
ID: "iss-00497"
関連GitHub: ["#497"]
最終更新: "2026-11-02"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

## Outcome

- `spec-dock/.gitignore`（配布資産と dogfood の写し）に `!**/.workbench/` を `**/.workbench/*` より前に足した。ルートの `.gitignore` が `.workbench/` を無視していても、雛形 `spec-dock/templates/cue/{epic,initiative,issue}/.workbench/README.md` が `git add -f` なしにコミットの対象になる。README 以外は従来どおり無視される。
- 一時のリポジトリで `git check-ignore` と `git add` により、設計の見立てが正しいことを確かめ、テストにした。
- `static-inventory.json` の `spec-dock/.gitignore` のハッシュを更新し、0.4.2 のバイト（`b28e6f24…`）を `known_old_sha256` に足した。0.4.2 の利用側が `installation update` で上がることをテストした。
- `requirement.cue` は、採る案（`!` の行）と、R-02・R-03 を明記するために直した（統括の書き済みの R-01 を具体化）。

## 0.5.0 の「更新」の節に書くべき契約の変更

- 利用側の `spec-dock/.gitignore` が変わる。`installation update` が提案する（0.4.2 のバイトは手作業の統合なしに上がる）。
- 更新後、ルートが `.workbench/` を無視していても、`spec-dock/` の下の `.workbench/README.md` は追跡の対象になる（雛形の3つのほか、`spec-dock/` の下の任意の `.workbench/README.md`）。ほかの中身は無視のまま。既存の利用側は、`git add spec-dock/templates` で雛形の README を足してコミットする。
- 版は上げていない。`migration.md` には節を足していない。

## Verification

- 仕様レビュー（spec-reviewer opus/medium）：P0/P1 なし、P2 1件（雛形以外の README への影響の記述。設計の互換性に追記して対応）。
- コードレビュー（code-reviewer sonnet/high）：`92e821e4f` で指摘 0 件。
- 最終品質ゲート（quality-gate-reviewer opus/high、1人）：`92e821e4f26235d39b6ecc78d45da4ae551cf93b` で pass、P0〜P3 すべて 0 件、網羅完了。テストの記録：`make lint` 成功、`uv run pytest` は 4097 passed / 8 skipped（exit 0）。記録は `.workbench/final-quality-gate/c1/`（Git 管理外）。
- 新しいテスト：`tests/integration/test_issue497_workbench_readme.py`（5件）。

## Residual Risks / Follow-ups

- #496 と `static-inventory.json` で競合する可能性がある（別行の編集なので、取り込みで解決できる見込み）。
- 採らなかった案（置き場の名前の変更、`installation update` の警告）の理由は `design.cue` に記録した。
