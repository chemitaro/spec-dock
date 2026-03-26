# discussions/rules.md

このディレクトリには initiative に紐づく議論資料を置きます。

- Discussion workflow: `spec-dock/docs/workflow_adr.md`
- Naming rules: `spec-dock/docs/reference_naming.md`
- 実行場所: コマンドはリポジトリ root から実行してください。`./spec-dock/scripts/spec-dock ...` はその位置で保証される実行経路で、nested directory では相対 path が変わります。
- Create commands:
  - `./spec-dock/scripts/spec-dock new doc adr --initiative <id> --title "<title>"`
  - `./spec-dock/scripts/spec-dock new doc disc --initiative <id> --title "<title>"`
  - `./spec-dock/scripts/spec-dock new doc research --initiative <id> --title "<title>"`
  - `./spec-dock/scripts/spec-dock new doc note --initiative <id> --title "<title>"`
