---
種別: レポート（Issue）
ID: "iss-00407"
タイトル: "Fix Workbench Readme Only Git Ignore Contract"
関連GitHub: ["#407"]
最終更新: "2026-09-24"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00080", "init-00079"]
---

# Result Summary

詳細: [Report Guide](../../../../../../docs/authoring/report.md)

## Outcome

- provider の `spec-dock/.gitignore` は既に README-only の規則を持つため、内容は変更しなかった。実 Git で direct `README.md` は追跡候補、通常 payload と `README.md/child.txt` は ignored であることを確認した。
- installer は fresh init 時に root `.workbench/README.md` を生成する。既存 workspace では `.gitignore` が欠落、または配布済みの `.workbench/` 一括 ignore 版と完全一致するときだけ provider 版を配置する。独自編集と既存 Workbench 内容は保持する。
- 各利用先で既に Git 追跡された payload の追跡解除は行っていない。

## Verification

- `uv run pytest tests/unit/infra/test_directory_installation.py -q`: 13 passed。root README の欠落、部分 init 後の `.gitignore` 欠落、旧版保持を Red で確認してから Green にした。
- `uv run pytest`: 1553 passed, 25 skipped。
- `make lint`: ruff check / format、mypy とも pass。
- `./spec-dock/scripts/spec-dock validate`: `nodes=238`、pass。
- `git check-ignore --no-index`: この repo の Issue `.workbench/README.md` は exit 1、通常 payload と `README.md/child.txt` は exit 0。README は `git ls-files` に存在する。

## Residual Risks / Follow-ups

- 独自編集した利用先の `spec-dock/.gitignore` は update で変更されないため、利用先で ignore の実効性を確認する。
- `.gitignore` は既追跡ファイルや明示的な `git add -f` に効かない。既追跡 payload の手動解除は利用者が各 project で実施する。
- この dogfooding workspace の root `.workbench/README.md` は既存 scope への no-backfill 方針に従い追加していない。
