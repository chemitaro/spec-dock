# spec-dock/templates

このディレクトリは、ローカルスクリプト `./spec-dock/scripts/spec-dock new ...` が
新規ノードを作成する際に参照するテンプレート群です。

- `initiative/` → `initiatives/init-xxxx-<slug>/`
- `epic/` → `.../epics/epic-xxxx-<slug>/`
- `issue/` → `.../issues/iss-xxxx-<slug>/`
- `adr.md` → `<scope>/adrs/adr-xxxx-<slug>.md`

注意:
- 生成後のファイルは自由に編集して構いません（テンプレは雛形）。
- 命名規則は **全て小文字**（macOS のケース非区別FS対策）。
- `new/import {initiative,epic,issue}` の `--slug` は kebab-case（小文字英数字 + `-`）です。`--slug` 省略時は `--title` から合成されます（詳細は `spec-dock/docs/reference_naming.md`）。
- 各ノードには `artifacts/_template.md` が含まれます（補足資料の雛形）。
- 各スコープ配下には wrapper が含まれます（`epics/new-epic`, `issues/new-issue`, `adrs/new-adr`）。
- 新規ノードにはテンプレ由来の `README.md` は生成されません。
