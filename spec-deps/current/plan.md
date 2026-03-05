---
種別: 実装計画書（Issue）
ID: "iss-00014"
タイトル: "ディスカッション資料の格納先を discussions/ に統一（adrs/artifacts の統合）"
関連GitHub: ["#14", "https://github.com/chemitaro/spec-dock/issues/14"]
状態: "approved"
作成者: "Codex CLI"
最終更新: "2026-03-06"
依存: ["requirement.md", "design.md"]
親: []
---

# iss-00014 ディスカッション資料の格納先を discussions/ に統一（adrs/artifacts の統合） — 実装計画（TDD: Red → Green → Refactor）

## この計画で満たす要件ID (必須)
- 対象AC: AC-001, AC-002, AC-003, AC-004, AC-005, AC-006
- 対象EC: EC-001, EC-002
- 対象制約（Always / 非交渉）:
  - ADR 採番（`adr-00001-...`）を維持
  - 後方互換性は維持しない（破壊的変更を許容）

## 実行ルール（全ステップ共通） (必須)
- 各ステップは **Red → Green → Refactor → 品質ゲート → レビュー → コミット** の順で進める
- `update_plan` を使い、ステップ開始/終了（および reviewer 指摘の対応状況）を更新する
- `spec-deps/current/report.md` に、各ステップの実行ログ（コマンド/結果/変更ファイル/メモ/レビュー指摘）を必ず追記する
- 各ステップで reviewer のレビューを受け、**指摘対応→再レビュー** を繰り返して Approved を得る（次ステップへ進まない）
- コミットは「変更が入るステップ（S02〜S05、S04を実装する場合）」ごとに 1 回以上（Conventional Commits、日本語・複数行、本文に変更点/理由/影響/テスト結果を箇条書き）。S06 は品質ゲートのため、差分が無ければコミット不要（指摘対応が発生した場合は追加コミットで対応）
- 履歴の書き換え（`--amend`/rebase/force push 等）はしない（修正は追加コミットで積む）

## ステップ一覧（観測可能な振る舞い） (必須)
- [x] S01: `discussions/` 運用仕様（命名/連番/rules/テンプレ位置・種類/ラッパ廃止）を確定する
- [ ] S02: 新規テンプレ生成物が `discussions/` と `rules.md` を作る（`adrs/`, `artifacts/` を生成しない）
- [ ] S03: `spec-dock new adr` の出力先が `discussions/` になり、走査/採番も追随する（後方互換なし）
- [ ] S04: （任意）`spec-dock new doc` を追加し、`note/disc/research` を連番で作成できる
- [ ] S05: docs/tests を更新し、運用ルールと導線を固定する
- [ ] S06: 最終品質ゲート（main 差分レビュー + 承認）を通す

### UML（任意） (任意)
```plantuml
@startuml
skinparam monochrome true
title Implementation steps (iss-00014)

rectangle "S01\n(spec decision)" as S01
rectangle "S02\n(templates)" as S02
rectangle "S03\n(runtime new adr + scan)" as S03
rectangle "S04\n(optional: new doc)" as S04
rectangle "S05\n(docs + tests)" as S05
rectangle "S06\n(quality gate)" as S06

S01 --> S02
S02 --> S03
S03 --> S04
S04 --> S05
S05 --> S06
@enduml
```

### 要件 ↔ ステップ対応表 (必須)
- AC-001 → S02
- AC-002 → S03
- AC-003 → S02
- AC-004 → S02（テンプレ位置の案内）/ S04（生成する場合）
- AC-005 → S02, S05
- AC-006 → S02
- EC-001 → S03, S04
- EC-002 → S02
- 非交渉制約（採番維持/後方互換なし）→ S03

---

## 実装ステップ（各ステップは“観測可能な振る舞い”を1つ） (必須)

### S01 — `discussions/` 運用仕様を確定する（ドキュメント） (必須)
- 状態: Done
- Done 条件:
  - `spec-deps/current/requirement.md` が reviewer Approved
  - `spec-deps/current/design.md` が reviewer Approved
  - `spec-deps/current/artifacts/20260305-discussions-best-practice.md` が最新仕様に追随している
- 追加/更新するテスト: なし（仕様確定）

---

### S02 — 新規テンプレ生成物が `discussions/` を生成する (必須)
- 対象: AC-001, AC-003, AC-004, AC-005, AC-006
- Red（先にテストを固める）:
  - `tests/test_cli.py` で init/update の生成物を検証し、`<scope>/discussions/` が存在し `adrs/` と `artifacts/` が存在しないことをアサートする
  - `discussions/rules.md` が存在することをアサートする（AC-003 / EC-002）
  - `discussions/` 配下に `new-*` 等のラッパスクリプトが存在しないことをアサートする（AC-005）
  - `spec-dock/templates/discussions/` と type テンプレ（`adr.md`, `note.md`, `disc.md`, `research.md`）が存在することをアサートする（AC-006）
- Green（実装。最小差分）:
  - Add: `src/spec_dock/assets/spec_dock/templates/{initiative,epic,issue}/discussions/rules.md`
  - Add: `src/spec_dock/assets/spec_dock/templates/discussions/{note,disc,research}.md`
  - Move: `src/spec_dock/assets/spec_dock/templates/adr.md` → `src/spec_dock/assets/spec_dock/templates/discussions/adr.md`
  - Delete: `src/spec_dock/assets/spec_dock/templates/{initiative,epic,issue}/{adrs,artifacts}/`
  - Modify: `src/spec_dock/assets/spec_dock/templates/README.md`（マッピング/注意書きの更新）
- テンプレ見直し（必須）:
  - `discussions/rules.md` に、命名規約・type 定義・テンプレのパス（`spec-dock/templates/discussions/*.md`）・コピー手順があることを確認する
  - `templates/discussions/{adr,note,disc,research}.md` の frontmatter/見出し/プレースホルダが運用意図と一致していることを確認する
- Refactor:
  - 生成物テンプレの重複表現（命名/リンク/見出し）を最小限に整理する
- 品質ゲート:
  - `python -m unittest discover -v`
- レビューゲート:
  - reviewer に差分レビューを依頼し、指摘対応→再レビューで Approved を得る
- 記録/コミット:
  - `spec-deps/current/report.md` にログを追記する
  - S02 の作業をコミットする（例: `feat(templates): discussions scaffolding`）

---

### S03 — `spec-dock new adr` が `discussions/` に作成する (必須)
- 対象: AC-002, EC-001
- Red:
  - `tests/test_cli.py` で `spec-dock/scripts/spec-dock new adr ...` が `<scope>/discussions/` に `adr-xxxxx-<slug>.md` を作成することをアサートする
  - EC-001: `--id` 省略時は max+1 採番、`--id` 明示重複は非0で失敗をアサートする
- Green:
  - Modify: `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/app.py`
    - `_new_adr`: 出力先 `adrs/` → `discussions/`、テンプレ参照 `templates/adr.md` → `templates/discussions/adr.md`
    - `_next_id`（prefix=="adr" fallback）: `adrs/adr-*.md` → `discussions/adr-*.md`
- 品質ゲート:
  - `python -m unittest discover -v`
- レビューゲート:
  - reviewer に差分レビューを依頼し、指摘対応→再レビューで Approved を得る
- 記録/コミット:
  - `spec-deps/current/report.md` にログを追記する
  - S03 の作業をコミットする（例: `fix(runtime): write adr into discussions`）

---

### S04 — （任意）`spec-dock new doc` を追加する (任意)
- 対象: （採用した場合）AC-004, EC-001
- Decision gate:
  - 実装する: `spec-dock new doc --{initiative|epic|issue} <id> --type {note|disc|research} --title ...`
  - 実装しない: `rules.md` の「テンプレコピー運用」を正とし、採番衝突時の手順を明記する
- Red（実装する場合）:
  - `tests/test_cli.py` に `new doc` の生成テストを追加する
    - 出力先: `<scope>/discussions/<type>-xxxxx-<slug>.md`
    - テンプレ選択: `spec-dock/templates/discussions/<type>.md`（無ければ `note.md`）
    - EC-001: `--id` 省略時は max+1、`--id` 明示時の重複は非0で失敗
- Green（実装する場合）:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/app.py` に `new doc` を追加し、テンプレ適用と採番を実装する（最小I/F）
- Refactor（実装する場合）:
  - 採番・テンプレ解決の重複を最小限に整理する
- 品質ゲート（実装する場合）:
  - `python -m unittest discover -v`
- レビューゲート（実装した場合）:
  - reviewer に差分レビューを依頼し、指摘対応→再レビューで Approved を得る
- 記録/コミット（実装した場合）:
  - `spec-deps/current/report.md` にログを追記する
  - S04 の作業をコミットする（例: `feat(runtime): new doc`）

---

### S05 — docs/tests を更新して導線を固定する (必須)
- 対象: AC-005（運用の固定）、周辺ドキュメントの追随
- 更新対象（例）:
  - `docs/discussion-sheets/01_tree_root_location.md`（ツリー例から `adrs/` を除去し `discussions/` に更新）
  - `spec-deps/README.md`（v1 記述の更新。必要なら）
  - `spec-deps/current/report.md`（実行コマンド/変更ファイルの記録）
- 品質ゲート:
  - `python -m unittest discover -v`
- レビューゲート:
  - reviewer に差分レビューを依頼し、指摘対応→再レビューで Approved を得る
- 記録/コミット:
  - `spec-deps/current/report.md` にログを追記する
  - S05 の作業をコミットする（例: `docs: update discussion docs`）

---

### S06 — 最終品質ゲート（main 差分レビュー + 承認） (必須)
- 対象: このブランチの実装差分（main との差分）すべて
- 品質ゲート:
  - `python -m unittest discover -v`
  - `git diff main...HEAD`（または `origin/main...HEAD`）で差分を確認し、スコープ外の変更が混入していないことを確認する
- レビューゲート（最終）:
  - reviewer に **main 差分**レビューを依頼し、指摘対応→再レビューを繰り返して Approved を得る
- 記録:
  - `spec-deps/current/report.md` に最終レビュー結果と修正履歴を追記する

---

## 未確定事項（TBD） (必須)
- Q-001: `spec-dock new doc` を実装するか（S04）
  - 選択肢:
    - A: 実装しない（手動コピー + `rules.md` で運用固定）
    - B: 実装する（採番衝突をツールで回避）
  - 推奨案（暫定）: B（ただし最小I/Fで）
  - 影響範囲: S04 / `design.md` / tests / 運用コスト

## 完了条件（Definition of Done） (必須)
- 対象AC/ECがすべて満たされ、テストで保証されている
- MUST NOT / OUT OF SCOPE を破っていない
- 品質ゲート（フォーマット/リント/テストのうち該当するもの）が満たされている

## 省略/例外メモ (必須)
- 該当なし
