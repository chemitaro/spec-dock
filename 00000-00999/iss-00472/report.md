---
種別: レポート（Issue）
ID: "iss-00472"
タイトル: "Define CUE Spec Schema V1"
関連GitHub: ["#472"]
最終更新: "2026-10-31"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00425", "init-00423"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## Outcome

- **型 `specdock/v1`**：`src/spec_dock/cue/v1/` に5つのファイル（`base.cue`、`requirement_type.cue`、`design_type.cue`、`plan_type.cue`、`rules.cue`、`package spec`）を足した。`design.md` の3〜5節のとおりに、番号の項目（R、F、D、S、T、切り分け）、保証レベルで変わる必須の項目（`acceptance` は standard から、`impact`・`recovery` は strict から）、8つの規則（K2 の名前と段階）、種類ごとの違い、`execution` を持つ。
- **形の誤りの文**：`_rank` と `_specdock.issue` に既定を持たせ、保証レベルや種類のタグがないときに「cycle」の誤りで原因を隠さないようにした。文書が `_rank` を書いてレベルと違う段階にすると、`_specdock.rank` の照合で誤りになる。種類に合わない構造（Epic の `steps` など）は、直し方を示す1つの誤りになる。空白の判定は Python の `str.isspace()` と同じ範囲（全角の空白も空白）。
- **版の置き場**：`src/spec_dock/runtime/infra/cue_schemas.py`（`schema_directory`、`shipped_schemas`）。`pyproject.toml` のパッケージのデータに `cue/**/*.cue` を足し、wheel と sdist からの wheel に入る。`setup.py` は変えていない。
- **雛形**：3つの種類 × 3つのファイルを `tests/fixtures/cue/v1/templates/<種類>/` に置いた（I-3 が配布資産へ移す。`design.md` の Q2）。印 `{{ASSURANCE_LEVEL}}`、`{{ASSURANCE_REASON}}` は二重引用符の中にある。
- **見本の固定**：`tests/fixtures/cue/v1/samples/` に8つの見本（3つの種類、4つのレベル、形の誤りの2つ）と `expected.json`。
- **CI**：Provider CI の `provider-tests` に「Install pinned cue」を足した（v0.17.1、Linux amd64・arm64 の SHA-256 を確かめてから展開し、PATH に足す。ほかの環境では失敗）。`cue` を要するテストは、`cue` がないと入れ方を示して失敗する。
- **コミット**：`94d217e`、`bbf0cf9`、`bb3ec0d`、`681a24e`、`16ef1ec`、`f4b18f5`（`origin/main` `1c064f9e` から。最後の SHA は `f4b18f57730b278332bc874af9fd770266944ea5`。既存のファイルの変更は `pyproject.toml` と `provider-ci.yml` だけ）。
- **ゲートの P3 の手当て**（統括の判断(1)、2026-10-31）：FQG-001 は、`#Title` が Python の `str.splitlines()` と同じ改行の文字（CR だけ、`\v`、`\f`、U+001C〜U+001E、U+0085、U+2028、U+2029 を含む）を拒むようにした。FQG-002 は、取り下げた手順が存在しない番号・手順・セッションを指す3つの場合を、規則の表のテストに足した（実装は前から調べていた。調べないように変えるとテストが12件落ちることを確かめた）。`f4b18f5`。
- **Epic の文書の直し**（統括が行った）：K1 から `-c` を外した（`cue` 0.17.1 の `export` にはない）。K2 の `execution-reference` の出る条件に、`session` だけを書いた場合を足した。
- **実現していないこと**：配布資産としての雛形、`cue` を呼ぶ製品の部品、`scope check` などは、計画どおり I-2・I-3 以降。

## Verification

| AC | 結果 | 証拠 |
|---|---|---|
| AC-01 | 通過。3つの種類 × 規則ごとの違反（Issue 15、Epic・Initiative 各11）× 4つのレベルで、出る規則と番号が表の期待と一致 | `tests/unit/cue/test_schema_v1_rules.py`（198件） |
| AC-02 | 通過。light→standard（`acceptance`）、standard→strict（`impact`・`recovery`）、critical で完全な文書は下げたどのレベルでも通る | `tests/unit/cue/test_schema_v1_levels.py` |
| AC-03 | 通過。存在しないセッション、存在しない手順・切り分けを指すレビュー、`execution` なしの `session` が `execution-reference` に出る。空、日本語、記号、改行を含む `model`・`effort` が通る | `test_schema_v1_rules.py`、`test_schema_v1_execution.py` |
| AC-04 | 通過。リポジトリの型の必須（`_rank` の条件つき）と規則が加わる。レベルがないときも `assurance.level` の誤りだけ | `tests/unit/cue/test_schema_v1_overlay.py` |
| AC-05 | 通過。3つの種類 × 4つのレベル × 5つの理由（引用符、`\`、改行、タブ、`\(`、制御文字）で、誤りも指摘もなく、理由がそのまま出る | `tests/unit/cue/test_schema_v1_templates.py` |
| AC-06 | 通過。共通の項目、番号のキー、各項目、種類のタグ、`_rank` の書き換え、Unicode の空白だけの値が、項目の道筋を含み `cycle` を含まない誤りになる | `tests/unit/cue/test_schema_v1_shape_errors.py` |
| AC-07 | 通過。8つの見本の結果が `expected.json` と一致（期待の結果は、規則の表と照らして手で確かめてから置いた） | `tests/unit/cue/test_schema_v1_golden.py` |
| AC-08 | 通過。ビルドの入力だけを写した場所から作った wheel、sdist からの wheel、インストールした wheel で確かめた | `tests/integration/test_cue_schema_wheel.py`、`tests/unit/infra/test_cue_schemas.py` |
| AC-09 | 通過。ワークフローの文面のテスト、`cue` がないときの失敗のテスト。手順の台本を手元で流し、amd64・arm64 の正しい実行ファイルが出ること、ほかの環境で止まること、書き換えた取得物で `sha256sum -c` が失敗することを確かめた。PR #480 の CI（GitHub の Linux amd64 のランナー）で、`cue_v0.17.1_linux_amd64.tar.gz: OK`、`cue version v0.17.1` の後に全テストが通った | `tests/integration/test_provider_ci_cue.py`、`tests/unit/cue/test_cue_required.py` |
| AC-10 | 通過。`make lint` 通過。全テスト 3705 passed、8 skipped（canonical のリンクのない clone、`16ef1ec`）。既存のテストのファイルと `.md` の雛形は変えていない（`git diff --diff-filter=M` は `pyproject.toml` と `provider-ci.yml` だけ） | 最終品質ゲートの test lane |
| AC-11 | 通過。各項目、`assurance`、トップレベル、`execution` に足した項目がそのまま出る。番号の形でないキーは誤り | `tests/unit/cue/test_schema_v1_flexibility.py` |
| AC-12 | 通過。すべての指摘が `id`、`message`、`hint` を持ち、`hint` が直すファイルを名指し、`id` の順に並ぶ | `test_schema_v1_rules.py` |

- テストが効いていることを、型の守りを一時的に外して確かめた（`_rank` の照合、`_rank` の既定、理由の型、`model` の型、項目を閉じたとき、パッケージのデータの行。どれも、外すとテストが失敗した）。
- 仕様のレビュー（`spec-review`、spec-reviewer opus / xhigh）：1回目で合格（P0・P1 なし、P2 3件、P3 2件）。合格の後に、P2・P3 を文書で手当てした（AC-01 の文言、AC-11・AC-12 の追加、種類のタグと `_rank` の書き換えの扱い。記録は Workbench の `spec-review/iss-00472/review-response.md`）。
- コードのレビュー（`code-review`、code-reviewer opus / high、standards と spec の2人）：どちらも合格。standards の P2 1件（RE2 の `\S` が全角の空白を空白と見ない）を直した（`16ef1ec`）。spec は指摘なし。
- 最終品質ゲート（`final-quality-gate`、キャンペーン `iss-00472-gate-1`、1回目）：合格の commit `16ef1ec`。主 opus / xhigh：pass、coverage complete、P3 2件。2人目 sonnet / high：pass、指摘なし。test lane：`make lint` 0、全テスト 0。記録は Workbench の `final-quality-gate/iss-00472-gate-1/closure.md`。
- PR #480 の CI（head `16ef1ec`、2026-10-31T10:12Z）：Provider CI（run 41191221155：`route`、`provider-tests`、配布の確かめ ubuntu・macos）、SpecDock check（41191221215）、Commit identity（41191221201、41191192918）がすべて成功。`provider-tests` は GitHub の `ubuntu-latest` で、pytest 3681 passed、32 skipped（手元の macOS では 3705 passed、8 skipped。合計は同じ 3713 で、違いは既存の、OS による skip。新しいテストに skip はない）。GitHub のマージの状態は OPEN、非下書き、MERGEABLE、CLEAN（`github-pr-checks` の observer：`OBSERVED_CI_PASS`、`READY`）。
- ゲートの P3 の FQG-001・FQG-002 は、統括の判断で、この PR で直した（`f4b18f5`）。統括の指示どおり、`16ef1ec` からの差分を、新しいレビュアー1人（code-reviewer opus / high、standards と spec）で確かめ、pass（指摘なし）。`f4b18f5` で `make lint` 0、全テスト 3732 passed、8 skipped（リンクのない clone）。PR #480 の CI（`f4b18f5`、2026-10-31T10:29Z）：Provider CI（run 41192162795、`provider-tests` で `cue_v0.17.1_linux_amd64.tar.gz: OK`、`cue version v0.17.1`、3708 passed、32 skipped）、SpecDock check、Commit identity がすべて成功。observer は `OBSERVED_CI_PASS`、`READY`。記録は Workbench の `followup-f4b18f5/`。

## Residual Risks / Follow-ups

- **既存の環境の問題（この Issue の外。統括が別の Issue で扱う）**：canonical のリンクのある worktree では、`tests/unit/infra/test_authoring_kit_assets.py` のリンクのテスト12件が、`spec-dock/initiatives` のリンクを辿って main のチェックアウトの `spec-dock/docs` を指すため失敗する。リンクのない clone と CI では通る。ほかの Issue の担当も、手元の全テストで同じ失敗を見る。
- **wheel のテストの残り物**：手元で `uv build` を木の中で流すと、`src/spec_dock.egg-info/SOURCES.txt` が残り、パッケージのデータの設定にないファイルも wheel に入る。新しいテストは、ビルドの入力を写した場所で作るので影響を受けないが、既存の `tests/integration/test_issue413_wheel.py` は木の中で作る。
- **`uv build` のビルド用の依存**：wheel のテストは、既存のテストと同じく、`setuptools` などのビルド用の依存を uv のキャッシュか PyPI から取る。
- **I-2 への引き渡し**：評価は `cue export --out json -t kind=<種類>`（`-c` なし）。`schema_directory` と `shipped_schemas`。指摘の `id` の頭とファイルの対応（R・F は `requirement.cue`、D は `design.cue`、ほかは `plan.cue`）。`schema` と `assurance` を `requirement.cue` 以外に書いても型は気づかないので、`scope show` が `requirement.cue` だけを読むことと合わせて扱いを決める。切り分けの子の ID が本当に子かは型では調べない。
- **I-3 への引き渡し**：雛形を `tests/fixtures/cue/v1/templates/<種類>/` から配布資産へ移す（テストの道筋も変える）。理由は、`tests/support/cue.py` の `cue_string_body` と同じ書き方で、二重引用符の中に入れる。理由が空白だけ（Unicode の空白を含む）なら型が誤りにするので、`--assurance-reason` で先に止める。
- **I-5 への引き渡し**：`after` の輪は v1 では見つけない。描画は輪があっても止まらないようにする。
- **I-6 への引き渡し**：項目の一覧、レベルの表、規則の表、リポジトリの型の決まり（`_rank` は読むだけ、`_specdock` を使わない、規則の名前を重ねない）、`findings` の文は日本語。
- **未確認**：自前の Linux arm64 のランナーでの `cue` の導入（今回の PR の CI では、`route` が GitHub のランナーを選んだ。arm64 の取得物の checksum と、arm64 の実行ファイルであることは、手元で確かめた）。外部の CheckRun（observer の範囲の外）。
