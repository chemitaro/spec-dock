---
種別: レポート（Issue）
ID: "iss-00474"
関連GitHub: ["#474"]
最終更新: "2026-10-31"
依存: ["requirement.md", "design.md", "plan.md"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## Outcome

schema 4（canonical モード）の `scope create` と `scope import github` が、`--assurance` と `--assurance-reason` を必須にし、`spec-dock/templates/cue/<種類>/` から CUE の Scope の一式を作るようになった（epic-00425 の I-3、契約 K4）。

- **ブランチとコミット**：`chemitaro/iss-00474`。base `418c1f87b`（origin/main）。
  - `c3c083532` feat(spec-dock): 必須の保証レベルを指定してCUE Scopeを作成・取り込み
  - `2f4baf4c2` test: cueテンプレートのwheel収録を検証する（`pyproject.toml` の package-data の3行を含む）
  - `8a80a7b4a` fix(spec-dock): assurance拒否エラーの詳細形式を修正（コードのレビューの P3 2件）
  - 最終品質ゲートの合格のコミット：`8a80a7b4a`（下の Verification）
- **runtime**
  - `runtime/domain/assurance.py`（新しい）：`ASSURANCE_LEVELS`、`parse_assurance`（欠け・空白・全角の空白・UTF-8 にできない文字を拒む。前後の空白を除く）、`cue_string_body`（JSON の書き方に U+FEFF の逃がしを足す）、`assurance_replacements`。`scope_check.LEVELS` はこの定数を使う。
  - `runtime/cli/catalog.py`：6つの葉に `--assurance`（4つの値）と `--assurance-reason` を足した（argparse では任意）。help の前提と例に、2つの引数と3つのコードを書いた。
  - `runtime/application/canonical_scope_create.py`：`_require_assurance` を、確認・カタログ・GitHub を読む前に呼ぶ（`ASSURANCE_REQUIRED`、exit 2）。雛形の確かめ `_check_cue_templates`（`SCOPE_TEMPLATES_OUTDATED`、exit 3、`spec-dock installation update`）。写す場所を `templates/cue/<種類>/` に変えた。既にディレクトリがある import は書かずに警告 `ASSURANCE_NOT_WRITTEN`。復旧のコマンドに `--assurance <値>` と `'--assurance-reason=<理由>'` を含める。
  - `runtime/infra/canonical_scaffold.py`：`copy_scope_template_at` に `final_replacements`（ほかの置き換えとリンクの付け替えの後に、1回の走査で置き換える）。
  - `runtime/application/direct_scope_publish.py`：schema 3 で2つの引数のどちらかを付けたら、何もせずに `CANONICAL_NOT_MIGRATED`（`details.argument`）。
- **配布資産**（提供側と dogfood の写しを同じ PR で）
  - `templates/cue/{initiative,epic,issue}/`：`requirement.cue`、`design.cue`、`plan.cue`（I-1 の見本を `git mv`）、`explanation.html`（`design-system/explanation-skeleton.html` のバイト一致）、`report.md`（依存を CUE の3つにした新しい雛形）、`.workbench/README.md`（今の雛形のバイト一致）の18のファイル。今の `templates/<種類>/` は変えていない。
  - `docs/canonical.md`：冒頭に保証レベルの必須の1文、「エラーと次の1手」に `ASSURANCE_REQUIRED`、`SCOPE_TEMPLATES_OUTDATED`、`ASSURANCE_NOT_WRITTEN` の3行。`docs/reference_cli.md` と `docs/cli-redesign-guide.html` の C01〜C06 の引数の欄。
  - `static-inventory.json`：18のファイルを足し、3つの文書の `sha256` を新しくし、main の値を `known_old_sha256` に足した。
  - `pyproject.toml`：package-data に `templates/cue/<種類>/.workbench/README.md` の3行（統括の許可。2026-10-31）。

### 変えた既存のテストと理由

統括の決定（2026-10-31。schema 4 の `scope create`・`import` の呼び出しに2つの引数を足すことと、作られるファイルの期待を CUE の一式に変えることだけ）の範囲。ほかの確かめ（書き込みの順、題名、種類、親、復旧、エラーの形）は変えていない。ruff の整形で、引数を足した行が縦に並び直したため、差分の行数は多い。

| ファイル | 変えたこと | 理由 |
|---|---|---|
| `tests/cli_runtime/test_issue432_scope_create.py` | `ASSURANCE` を `_create`、`_import` と直接の呼び出し（確認・予行、`--offline`、`--slug`、import の復旧）に足した。作られるファイルの一覧を CUE の一式にした。front matter の確かめを `requirement.md` から `report.md` に移した。文書の見出しに題名があることの確かめ（`# epic-00002 中核の作業`、`# epic-00005 既存の作業`）は、CUE の雛形に題名を書く場所がないので、`report.md` の `ID` の確かめに変えた | K4 の必須の引数と、CUE の一式。題名の正本は GitHub で、GitHub の題名の確かめ（`issue.title`、`CANONICAL_TITLE_IGNORED`）はそのまま |
| `tests/cli_runtime/test_issue432_titles_and_kinds.py` | 3つの呼び出しに2つの引数を足した | 同上（引数がないと、種類の変更・題名の規則より前に `ASSURANCE_REQUIRED` で止まる） |
| `tests/cli_runtime/test_issue436_end_to_end.py` | 3つの `scope create` に2つの引数を足した | 同上 |
| `tests/cli_runtime/test_issue436_every_command.py` | 6つの create/import の葉の引数に2つの引数を足した | 同上 |
| `tests/integration/test_issue413_assets.py` | 配布資産の数 92→110、93→111 | 18のファイルを足した（I-4 の前例と同じ形） |
| `tests/unit/cue/test_schema_v1_templates.py` | 読む場所を配布資産に変え、ファイルの一覧の確かめを「3つの CUE の文書を含む」にした。`_fill` は runtime の置き換えを使い、テストの補助との比べ方を `cue` で読んだ値の一致にした | I-1 の見本を I-3 が移す（I-1 のテストの説明のとおり） |
| `tests/fixtures/cue/v1/templates/**` | 消した（配布資産へ `git mv`） | 同上 |

## Verification

### 最終品質ゲート（`final-quality-gate`、campaign `iss-00474-i3`、attempt 01）

- 候補：`8a80a7b4a26bde89fc74d5ccbe5f6fa14800c12f`（clean）。観点：functional-correctness、requirements-closure、test-adequacy。
- 主のレビュアー（quality-gate-reviewer、opus / xhigh）：pass。P0 0、P1 0、P2 0、P3 1。網羅は完全。
  - P3（FQG-01、情報のみ）：`canonical.md` の表の `ASSURANCE_REQUIRED` と `ASSURANCE_NOT_WRITTEN` の行を、テストが縛っていない（既存の表の検査は `SCOPE_` などの接頭辞のコードだけを集める）。成果物は揃っている。ゲートの規則により直していない。
- 2人目のレビュアー（quality-gate-reviewer、sonnet / high）：pass。指摘なし。網羅は完全。
- テストの側：TEST_LANE_RESULT
- ChatGPT のレーン：使っていない（無効）。

### それまでの確かめ

- 仕様のレビュー（spec-review、opus / xhigh、第1回）：pass（P0 0、P1 0、P2 1、P3 6）。P2（U+FEFF を含む理由で `cue` が読めない）と P3 のうち5つを設計と実装に取り込んだ（`design.md` の「決めたこと」）。
- コードのレビュー（code-review、opus / high、標準と仕様の2人、`2f4baf4c2`）：どちらも pass、P3 各1件。両方を直して `8a80a7b4a` にした（cli-redesign-guide.html の「通常操作の流れ」の例を元に戻した。schema 3 の拒否の `details` を `argument` にした）。
- `2f4baf4c2` で `make lint`（exit 0）と、`cue` を PATH に置いた `uv run pytest`（3969 passed、8 skipped、exit 0）。
- 受け入れ条件とテスト：
  - AC-01、AC-03、AC-04、AC-05、AC-06、AC-08、AC-10（作った説明資料のバイト一致）、AC-11（help）：`tests/cli_runtime/test_issue474_scope_create.py`（本物の `cue`）。
  - AC-02、AC-03（単体）：`tests/unit/domain/test_assurance.py`（本物の `cue` での往復。U+FEFF、`\(`、制御文字、サロゲート）。
  - AC-07、AC-10：`tests/unit/infra/test_issue474_cue_templates.py`（目録、写し、スケルトン、`templates/<種類>/` が今の5つのまま、新しく作った wheel の収録）、`tests/integration/test_issue413_assets.py`。
  - AC-09：`tests/cli_runtime/test_issue474_schema3.py` と、schema 3 の既存のテスト（変更なし）。
  - AC-11（表）：`tests/unit/infra/test_issue436_docs.py`（`SCOPE_TEMPLATES_OUTDATED` を縛る。ほかの2つは上の P3）。
  - AC-12：上の lint と全体のテスト。

### 確かめられなかったこと

- 未確認：前の版の SpecDock（インストール済みの古い wheel）を、新しい配布資産のリポジトリで実際に動かすこと。代わりに、`templates/<種類>/` の中身が今と同じであることと、今も `templates/<種類>/` を写す schema 3 の作成が `.md` の Scope を作ることを確かめた（AC-07）。
- 未確認：Linux での実行（手元は macOS。PR の CI で確かめる）。
- 未確認：本物の GitHub とカタログでの作成（依頼で禁止。I-7 で行う）。

## Residual Risks / Follow-ups

- **CLI の契約の変更**：schema 4 の `scope create`・`import` を引数なしで呼ぶ手順（`spec-dock` スキル、利用者の `coordinate` などの手順、スクリプト）は、`ASSURANCE_REQUIRED` で止まる（何も書かず、直し方を示す）。I-6 で、スキル、ガイド、`templates/README.md` を直す。利用者の手順は統括・利用者が直す。
- **`SCOPE_KIND_CHANGED` の復旧の文**（仕様のレビューの P3）：`canonical_errors.py` の文は「新しい種類で作り直し、古いディレクトリの中身を移す」と示す。この Issue の後は、作り直した Scope が CUE になるので、Markdown の中身を移すと `requirement.md` と `requirement.cue` が並んで `SCOPE_FORMAT_CONFLICT` になる。変更対象の外なので、I-6 か後の Issue で文を直す。
- **表の行のテスト**（最終品質ゲートの P3）：`canonical.md` の `ASSURANCE_REQUIRED` と `ASSURANCE_NOT_WRITTEN` の行を縛るテストがない。I-6 でガイドをまとめるときに足すとよい。
- **`.workbench/README.md` の Git の扱い**：利用者の `.git/info/exclude` に `.workbench/` があるため、6つの `.workbench/README.md` は `git add -f` で足した（今の雛形と同じ）。
- **`.md` の雛形の撤去**：I-7。それまでは、前の版の CLI が新しい配布資産でも `.md` の Scope を作る。
