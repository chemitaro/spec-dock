# spec-deps

`spec-dock` 自体の「deps（依存関係）機能」に関する、仕様書駆動開発の作業ディレクトリです。

## ディレクトリ構成
- `current/`: 現在進行中の仕様書（作業対象）
- `completed/`: 完了済み・過去仕様書（ディレクトリ単位でアーカイブ）

## 運用ルール（最小）
- 仕様確定・完了したら `current/` を `completed/<name>/` に移動します。
- `completed/<name>/` は `YYYYMMDDTHHMMSSZ-issue-queue-iss-xxxxx` のように、日時と種別/IDが分かる名前を推奨します。
- ADR / 議論 / 調査 / メモは `current/discussions/` に追加します。
- discussion docs の命名は `NNN-type-slug.md`（3 桁固定）です。
- `current/discussions/rules.md` と `spec-dock/templates/discussions/*.md` を基準に運用します。
