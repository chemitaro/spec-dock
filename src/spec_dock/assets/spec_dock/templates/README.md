# .spec-dock/templates

このディレクトリは、ローカルスクリプト `./.spec-dock/scripts/spec-dock new ...` が
新規ノードを作成する際に参照するテンプレート群です。

- `initiative/` → `initiatives/init-xxxx-<slug>/`
- `epic/` → `.../epics/epic-xxxx-<slug>/`
- `issue/` → `.../issues/iss-xxxx-<slug>/`
- `adr.md` → `<scope>/adrs/adr-xxxx-<slug>.md`

注意:
- 生成後のファイルは自由に編集して構いません（テンプレは雛形）。
- 命名規則は **全て小文字**（macOS のケース非区別FS対策）。
