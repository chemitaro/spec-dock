---
種別: 実装計画書（Issue）
ID: "iss-00472"
タイトル: "Define CUE Spec Schema V1"
関連GitHub: ["#472"]
状態: "draft"
最終更新: "2026-10-31"
依存: ["requirement.md", "design.md"]
親: ["epic-00425", "init-00423"]
---

# iss-00472 Define CUE Spec Schema V1 — 実装計画

詳細: [Issue Plan Guide](../../../docs/authoring/issue-plan.md)

## Planning Level

- 選んだ level：`strict`（Epic の `plan.md` の指定）。
- 理由：すべての CUE の Scope が従う型で、出した版は互換を壊して変えられない（K6）。I-2、I-3、I-5、I-6 が、この型の項目と規則の名前に依る。誤ると、後の Issue と、I-7 の後の利用者の文書のすべてに広がる。
- risk factor：配られる型の公開の契約（項目の名前、規則の名前、指摘の形）、CI の新しい外の道具（`cue`）、wheel の中身の変更。
- 再評価の条件：型が、利用者の秘密や、戻せないデータを扱うことになったら `critical` に上げる。今の範囲（読むだけの型、テスト、CI の手順）では起きない。

## 目標

この Issue の `requirement.md` の AC-01〜AC-10 を満たし、I-2（検査）、I-3（雛形の配置）、I-5（描画）が、この型の上で始められる状態にする。

## 順序・依存

- 前提：`spec-dock work start iss-00472` が通っている（2026-10-31 時点では、古い依存 epic-00424 で止まる。統括が利用者に確かめている）。実装（手順1から）は、その後に始める。
- 型の項目の一覧とレベルの表は、2026-10-31 に統括が確かめた（Epic の `plan.md` の I-1 の注意。`design.md` の「決めたこと」）。
- 手順は、次の順に進める。テストの補助（1）が、ほかのすべてのテストの前提である。2 と 9、10 は、型と独立なので、型の作業と並べてよい。

## 実装step

各手順は、テストを先に書き（Red）、通し（Green）、整える（Refactor）。区切りでコミットする（コードとテストだけ。仕様はコミットしない）。

1. **テストの補助**：`tests/support/cue.py`（`cue` を PATH から探し、なければ入れ方を示して失敗する。K1 の並べ方で評価し、終了の状態、JSON、誤りの文を返す。CUE の文字列の書き方に変える関数）。`cue` がないときの失敗のテスト（AC-09 の後半）。
2. **版の置き場**：`runtime/infra/cue_schemas.py` の `schema_directory` と `shipped_schemas`、そのテスト（AC-08 の後半）。
3. **共通の項目**：`cue/v1/base.cue`。形の誤りのテスト（`schema`、`assurance`、種類のタグ。AC-06 の一部）。
4. **3つの文書の項目**：`requirement_type.cue`、`design_type.cue`、`plan_type.cue`。番号のキーの形、種類ごとの違い、`execution` の形、レベルの表のテスト（AC-02、AC-06 の残り）。
5. **つながりの規則**：`rules.cue`。規則 × レベル × 種類の表のテスト（AC-01）、`execution-reference` のテスト（AC-03）。
6. **リポジトリの型**：テストの中の型の見本で、制約と規則が加わることのテスト（AC-04）。
7. **雛形**：3つの種類 × 3つのファイル（`tests/fixtures/cue/v1/templates/<種類>/`）。印を置き換えて、4つのレベルで通るテスト（AC-05）。
8. **見本の固定**：`tests/fixtures/cue/v1/samples/` の見本と `expected.json`。一致のテスト（AC-07）。期待の結果は、規則の表と照らして、手で読んで確かめてから置く。
9. **パッケージのデータ**：`pyproject.toml`。wheel と sdist からの wheel の中身のテスト（AC-08 の前半）。
10. **CI**：`provider-ci.yml` の `provider-tests` に、`uv run pytest` の前の `cue` の導入の手順。ワークフローの文面のテスト（AC-09 の前半）。
11. **全体の確かめ**：`make lint`、`PATH="$PWD/.workbench/bin:$PATH" uv run pytest`（AC-10）。
12. **レビューと品質ゲート**：`code-review`（opus / high）、`final-quality-gate`（opus / xhigh、sonnet / high）。指摘を直し、ゲートを最後の SHA で通す。
13. **報告と PR**：`report.md`、`main` への PR、PR の CI の確かめ。マージは人が行い、`work finish` は統括の指示を待つ。

## 検証

| AC | 確かめ方 |
|---|---|
| AC-01 | `tests/unit/cue/test_schema_v1_rules.py`：3つの種類 × 規則ごとの違反 × 4つのレベル。出た規則の名前の集まりと、空でない一覧の集まりの両方を比べる |
| AC-02 | `tests/unit/cue/test_schema_v1_levels.py`：light→standard、standard→strict、下げたとき |
| AC-03 | `tests/unit/cue/test_schema_v1_execution.py` |
| AC-04 | `tests/unit/cue/test_schema_v1_overlay.py` |
| AC-05 | `tests/unit/cue/test_schema_v1_templates.py` |
| AC-06 | `tests/unit/cue/test_schema_v1_shape_errors.py`（失敗の各場合。負のテスト） |
| AC-07 | `tests/unit/cue/test_schema_v1_golden.py` |
| AC-08 | `tests/integration/test_cue_schema_wheel.py`、`tests/unit/infra/test_cue_schemas.py` |
| AC-09 | `tests/integration/test_provider_ci_cue.py`、`tests/unit/cue/test_cue_required.py`。PR の CI の `provider-tests` のログで、`cue version v0.17.1` と checksum の `OK` を読む |
| AC-10 | `make lint`、全テスト。`git diff --stat origin/main -- tests/` に、既存のファイルの変更がないこと。`git diff origin/main -- src/spec_dock/assets spec-dock/templates` が空であること |

- 回帰：全テストを、この worktree で、`cue` を PATH に足して流す。
- 互換：既存の CLI は型を呼ばないので、CLI の回帰は全テストで足りる。
- 失敗の確かめ：AC-06 の負のテスト、`cue` がないときの失敗、CI の checksum の不一致（`sha256sum -c` が失敗で止まることは、手順の文面で確かめる。CI で実際に不一致を起こすことはしない：未確認として報告に書く）。
- security / privacy / operability：型は読むだけで、秘密を扱わない（N/A）。CI は、固定した版と checksum で外の道具を取るので、取得物のすり替えを防ぐ。`cue` を呼ぶのはテストだけである。

## rollback

- この PR を戻せば、型、部品、CI の手順、テストがまとめて消える。どの Scope も、まだ型を使っていない（I-7 まで）ので、移行の戻しは要らない（migration：N/A。データを持たないため）。
- PR のマージの後に、I-2 以降が型の不具合を見つけたら、I-6 で版を出す前なら、v1 を直し、見本の期待の結果を理由と一緒に変える。出した後なら、互換を壊さない足し方か、v2 にする（forward recovery）。

## exit / handoff

- 終わりの条件：AC-01〜AC-10、レビューと品質ゲートの合格、`report.md`、マージできる PR。
- I-2 へ：評価の並べ方（`-c` なし）、`cue_schemas` の2つの関数、指摘の `id` と、ファイルの対応、`_rank` の既定、形の誤りの文の見本。`schema`・`assurance` が別のファイルにある場合の扱い。子の ID が本当の子かを比べるか。
- I-3 へ：雛形の置き場（`tests/fixtures/cue/v1/templates/<種類>/` から配布資産へ移す）、印の位置と、理由の文字列の書き方（`tests/support/cue.py` の関数を見本にできる）。
- I-5 へ：項目の一覧（描く順番の材料）、`after` の輪を v1 では見つけないこと。
- I-6 へ：項目の一覧、レベルの表、規則の表、リポジトリの型の決まり（`_specdock` を使わない、規則の名前を重ねない）。

## モデルと推論

- この Issue のセッション：opus / xhigh（Epic の `plan.md` の例外。型の設計から実装まで1つのセッション）。
- レビュアー：spec-reviewer opus / xhigh、code-reviewer opus / high、quality-gate-reviewer opus / xhigh と sonnet / high（Epic の `plan.md` の strict の行）。
