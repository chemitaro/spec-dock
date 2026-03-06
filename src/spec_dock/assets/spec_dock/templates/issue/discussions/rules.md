# discussions/rules.md

このディレクトリは、issue に紐づく検討資料（ADR/議論/調査/メモ）を記録する場所です。

## 1. 種類（type）
- `adr`: 意思決定（Architecture Decision Record）
- `disc`: 議論シート（選択肢比較、推奨案）
- `research`: 調査メモ（結果と結論）
- `note`: 軽量メモ（会議・作業・思考）

## 2. 命名規約
- ファイル名は `<type>-00001-<slug>.md`
- 例:
  - `adr-00001-token-rotation.md`
  - `disc-00001-doc-structure.md`
  - `research-00001-naming-rules.md`
  - `note-00001-kickoff-memo.md`

## 3. 作成方法
- ADR:
  - `./spec-dock/scripts/spec-dock new adr --issue <id> --title "<title>"`
- 非ADR（コピー運用）:
  - 前提: リポジトリルートで実行する
  - `cp spec-dock/templates/discussions/note.md spec-dock/initiatives/<initiative-id>-<slug>/epics/<epic-id>-<slug>/issues/<issue-id>-<slug>/discussions/note-00001-<doc-slug>.md`
  - `cp spec-dock/templates/discussions/disc.md spec-dock/initiatives/<initiative-id>-<slug>/epics/<epic-id>-<slug>/issues/<issue-id>-<slug>/discussions/disc-00001-<doc-slug>.md`
  - `cp spec-dock/templates/discussions/research.md spec-dock/initiatives/<initiative-id>-<slug>/epics/<epic-id>-<slug>/issues/<issue-id>-<slug>/discussions/research-00001-<doc-slug>.md`

## 4. ルール
- `discussions/` 配下に `new-*` などのラッパスクリプトを置かない。
- 連番は type ごとに採番し、既存の最大番号 +1 を使う。
- 公開済みファイルの番号を振り直さない。
