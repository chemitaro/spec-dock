---
種別: 実装計画書（Issue）
ID: "iss-00474"
関連GitHub: ["#474"]
状態: "approved"
最終更新: "2026-10-31"
依存: ["requirement.md", "design.md"]
---

# iss-00474 Scaffold CUE Scopes With Assurance — 実装計画

詳細: [Issue Plan Guide](../../../docs/authoring/issue-plan.md)

## Planning Level

- **選んだ level**：strict（Epic の plan.md の表のとおり）。
- **理由**：配られる CLI の契約（schema 4 の `scope create`・`import` の必須の引数）を変える。GitHub に書く前の止め方を誤ると、半端な Issue が本物の GitHub に残り、利用者の手で直すことになる。
- **risk factor**：公開の CLI の契約、配布資産（15の新しいファイルと3つの文書）、既存のテストの書き換え、schema 3 との共存。
- **再評価の条件**：GitHub に書いた後に戻せない変更（Issue の本文の書き込みなど）や、既存の Scope のデータの書き換えが要るとわかったら、critical に上げる。該当しない（作るのは新しい Scope だけで、既存のデータに触れない）。
- **security / privacy / operability**：理由の文は利用者の入力で、カタログのファイルに入る。シェルや `cue` に渡さない（Q5）。CUE の文字列として逃がすので、文書の構造を壊さない（AC-03）。秘密を扱わない。観測は、今のエラーの封筒と `effects`。

## 目標

`requirement.md` の AC-01〜AC-12 を満たし、マージできる PR を作る。

## 順序・依存

1. 配布資産（雛形の移動と、写しと、目録）を先に置く。後の結合テストが、提供側の配布資産を種に使うため。
2. domain の `assurance.py`（純粋な関数）。
3. 引数と、canonical の作成・取り込み。
4. schema 3 の拒否。
5. 既存のテストの更新（引数の追加と、ファイルの期待）。
6. 文書（help、canonical.md、reference_cli.md、cli-redesign-guide.html）と目録の `sha256`。
2 と 1 は並べてよい。3 は 1、2 の後。5 は 3 の後。

## 実装step

各 step は、`tdd` のとおり、受け入れ条件のテストを先に書き（Red）、通し（Green）、整える（Refactor）。

- **S-01 雛形を配布資産に移す**（AC-10、AC-07）
  - Red：`tests/unit/infra/test_issue474_cue_templates.py`：提供側に15のファイルがある、`explanation.html` がスケルトンとバイト一致、目録にあり `sha256` が合う、dogfood の写しとバイト一致、`templates/<種類>/` は `.md` の4つのまま、`report.md` の依存が CUE の3つ。
  - Green：`git mv` で見本を移し、`explanation.html` と `report.md` を作り、目録と dogfood の写しを足す。`test_schema_v1_templates.py` の読む場所を変える。`test_issue413_assets.py` の数を直す（92→107、93→108）。
- **S-02 domain の保証レベル**（AC-03 の単体）
  - Red：`tests/unit/domain/test_assurance.py`：`parse_assurance` の欠け・空白・全角の空白・サロゲート・前後の空白、`cue_string_body` の本物の `cue` での往復（引用符、改行、タブ、バックスラッシュ、`\(`、制御文字、U+2028）、`assurance_replacements`。
  - Green：`runtime/domain/assurance.py`。`scope_check.LEVELS` を置き換える。
- **S-03 canonical の作成**（AC-01、AC-02、AC-03、AC-04、AC-06、AC-08）
  - Red：`tests/cli_runtime/test_issue474_scope_create.py`。
  - Green：`catalog.py` の引数、`canonical_scope_create.py` の `_require_assurance`、`_check_scaffold_sources`、`_publish`、`_import_command`、`canonical_scaffold.copy_scope_template_at` の `final_replacements`。
- **S-04 canonical の取り込み**（AC-02、AC-05、AC-06）
  - Red：同じファイルに import の場合。
  - Green：`import_scope` の `_require_assurance` と `ASSURANCE_NOT_WRITTEN`。
- **S-05 schema 3 の拒否**（AC-09）
  - Red：`tests/cli_runtime/test_issue474_schema3.py`。
  - Green：`direct_scope_publish._publish_scope`。
- **S-06 既存のテストの更新**（AC-12）
  - schema 4 の `scope create`・`import` を呼ぶ既存のテスト（`test_issue432_scope_create.py`、`test_issue432_titles_and_kinds.py`、`test_issue436_end_to_end.py`、`test_issue436_every_command.py` など、流して落ちたもの）に2つの引数を足し、作られるファイルの期待を CUE の一式に変える。ほかの確かめは変えない。変えた箇所と理由を記録する。
- **S-07 文書と help**（AC-11）
  - Red：`help scope create issue` に `--assurance` と `ASSURANCE_REQUIRED` があることのテスト（`test_issue474_scope_create.py`）、既存の `test_issue436_docs.py` の表の検査。
  - Green：`HELP_PRECONDITIONS`、`_example`、配布資産の3つの文書と dogfood の写し、目録の `sha256` と `known_old_sha256`。
- **S-08 全体の確かめ**：`make lint`、`PATH="$PWD/.workbench/bin:$PATH" uv run pytest`（裏で流し、終わりを待つ）。

## 検証

| AC | テスト |
|---|---|
| AC-01、AC-04、AC-08 | `tests/cli_runtime/test_issue474_scope_create.py`（本物の `cue`） |
| AC-02、AC-03、AC-05、AC-06 | 同上と `tests/unit/domain/test_assurance.py` |
| AC-07、AC-10 | `tests/unit/infra/test_issue474_cue_templates.py`、`tests/integration/test_issue413_assets.py`、schema 3 の既存の作成のテスト |
| AC-09 | `tests/cli_runtime/test_issue474_schema3.py` と、schema 3 の既存のテスト（変更なし） |
| AC-11 | `test_issue474_scope_create.py` の help、`tests/unit/infra/test_issue436_docs.py` |
| AC-12 | `make lint`、全テスト、`git diff --stat origin/main -- tests/` |

- negative test：F-01〜F-08 は、それぞれ上のテストで、止まることと、GitHub・カタログに書かないことを確かめる。
- regression：Markdown の Scope の `show`、`finish`、`validate`、`doctor` と schema 3 の作成の既存のテストを、変えずに流す。
- migration failure：N/A（データの移行がない）。
- 最終品質ゲート：`final-quality-gate`（主のレビュアー opus / xhigh、2人目 sonnet / high）。結果を `report.md` に書く。

## rollback

- この PR を戻せば、CLI と配布資産は元に戻る。データの戻しは要らない（この Issue の前に CUE の Scope はない。テストは一時のディレクトリだけを使う）。
- forward recovery：マージ後に問題が出たら、`--assurance` を任意に戻すのではなく、直す PR を出す（契約を2度変えないため）。

## exit / handoff

- 完了の条件：AC-01〜AC-12 のテストが通り、最終品質ゲートに合格し、PR の CI が通り、マージできる状態。`work finish` はマージの後に統括の指示で行う。
- 引き渡し：
  - I-6：`spec-dock` スキル、ガイド、`templates/README.md` に、2つの必須の引数、`templates/cue/`、3つのコードを書く。
  - I-7：`.md` の雛形 `templates/<種類>/` を外す。
  - 統括：利用者の手順（`coordinate` など）が `scope create` を呼ぶなら、2つの引数を足す必要がある。
- 残るリスク：`report.md` に書く。
