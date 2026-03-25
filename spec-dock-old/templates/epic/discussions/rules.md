# discussions/rules.md

このディレクトリは、epic に紐づく検討資料（ADR/議論/調査/メモ）を記録する場所です。

## 1. 種類（type）
- `adr`: 意思決定（Architecture Decision Record）
- `disc`: 議論シート（選択肢比較、推奨案）
- `research`: 調査メモ（結果と結論）
- `note`: 軽量メモ（会議・作業・思考）

## 2. 命名規約
- ファイル名は `NNN-type-slug.md`（`NNN` は 3 桁固定）
- 例:
  - `001-adr-token-rotation.md`
  - `002-disc-doc-structure.md`
  - `003-research-naming-rules.md`
  - `004-note-kickoff-memo.md`

## 3. 作成方法（runtime command）
- `./spec-dock/scripts/spec-dock new doc adr --epic <id> --title "<title>"`
- `./spec-dock/scripts/spec-dock new doc disc --epic <id> --title "<title>"`
- `./spec-dock/scripts/spec-dock new doc research --epic <id> --title "<title>"`
- `./spec-dock/scripts/spec-dock new doc note --epic <id> --title "<title>"`

## 4. ルール
- `discussions/` 配下に `new-*` などのラッパスクリプトを置かない。
- 採番は type ごとではなく `discussions/` 全体で共有します（new-format files の最大 `NNN` + 1）。
- 採番対象は `NNN-type-slug.md` に一致する new-format files のみです。
- `rules.md` と legacy/nonconforming files（例: `adr-00001-...`, `foo.md`）は採番対象外です。既存ファイルは rename しません。
- `999` を超える採番は失敗します。follow-up issue を作成し、archive または桁拡張を判断してください。
- 公開済みファイルの番号を振り直さない。
