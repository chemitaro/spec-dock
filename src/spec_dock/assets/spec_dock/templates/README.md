# spec-dock/templates

このディレクトリは、ローカルスクリプト `./spec-dock/scripts/spec-dock new ...` が
新規ノードを作成する際に参照するテンプレート群です。

- `initiative/` → `initiatives/init-xxxx-<slug>/`
- `epic/` → `.../epics/epic-xxxx-<slug>/`
- `issue/` → `.../issues/iss-xxxx-<slug>/`
- `discussions/{adr,disc,research,note}.md` → `<scope>/discussions/NNN-<type>-<slug>.md`

注意:
- discussion docs の公開 CLI は `new doc <type>` のみです。
- discussion docs のファイル名は `NNN-type-slug.md`（3桁固定）です。
- discussion docs の採番は `discussions/` 配下の new-format（`NNN-type-slug.md`）だけを対象にします。
- `rules.md` と legacy/nonconforming files は採番対象外です（rename せず無視します）。
- `999` を超える採番は失敗します。follow-up issue で archive または桁拡張を判断してください。
- 生成後のファイルは自由に編集して構いません（テンプレは雛形）。
- 命名規則は **全て小文字**（macOS のケース非区別FS対策）。
- `new/import {initiative,epic,issue}` の `--slug` は kebab-case（小文字英数字 + `-`）です。`--slug` 省略時は `--title` から合成されます（詳細は `spec-dock/docs/reference_naming.md`）。
- 各ノードの子スコープ配下には canonical guidance への `rules.md` symlink が含まれます（例: `epics/rules.md`, `issues/rules.md`, `discussions/rules.md`）。`rules.md` は入口/ナビゲーション用です。
- 作成/運用ルールの正本は `spec-dock/docs/rules/**` です。runtime command はサポートされた実行経路です。
- 新規ノードにはテンプレ由来の `README.md` は生成されません。
