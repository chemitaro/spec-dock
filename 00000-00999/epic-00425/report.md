---
種別: レポート（Epic）
ID: "epic-00425"
タイトル: "Build Html Spec Dashboard And Cue Documents"
関連GitHub: ["#425"]
最終更新: "2026-11-01"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["init-00423"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## Outcome

I-1〜I-6 の実装と 0.4.0 の公開、I-7 の spec-dock での導入まで終えた（2026-11-01）。

| Issue | PR | マージのコミット |
|---|---|---|
| I-1 #472 CUE の型 v1 | #480 | `2cf4e961a` |
| I-4 #475 デザインシステム | #479 | `056f070f0` |
| I-2 #473 `scope check`・`work finish`・`scope show`・`workspace validate`/`doctor` | #483 | `418c1f87b` |
| I-5 #476 `render_scope_html` と `scope render` | #484 | `411261e59` |
| I-3 #474 `--assurance` 付きの雛形 | #485 | `d53b24d64` |
| I-6 #477 文書、スキル、0.4.0 | #486 | `7f3cf7d3c`（タグ `v0.4.0`） |
| I-7 の試しの Issue #487 | #488 | `c43aadd5b` |
| 試しの改善の Issue #489 | #490 | `98ec261ea` |

### I-7 spec-dock での導入（AC-14）

- 2026-11-01、利用者の承認で、利用者の PC に `cue` 0.17.1（Homebrew）と SpecDock 0.4.0（タグ `v0.4.0` から作った wheel、`uv tool install --force`）を入れた。spec-dock（版4）と company-os（版3）で `workspace validate` が通る。
- spec-dock の配布資産は、各 PR が dogfood の写しを更新していたので、`installation update --dry-run` で差分がなかった（PR は作らない）。
- 今の `.md` の雛形は外さなかった。0.4.0 でも版3のリポジトリの `scope create` が使うので、epic-00424 の I-13（0.5.0）で外す（2026-11-01 に利用者が決めた。要件の R-H3、設計、計画、epic-00424 の計画・設計・要件を直した）。
- 実際の Issue #487（iss-00487、Polish CUE Authoring Guides And Leaf Help、light）を、0.4.0 の `scope create issue --assurance light` で CUE の雛形から作り、作業担当（opus / medium）が CUE の仕様で書き、仕様のレビュー、実装、コードのレビュー、最終品質ゲート、PR #488 まで回した。マージの後、統括が 0.4.0 の `work finish`（説明資料と CUE の検査を含む）で閉じた。詳しい記録は `iss-00487/report.md` の「CUE の仕様の試し」。

### 試しで分かったこと（`iss-00487/report.md` の要約）

- 書きやすさ：雛形のコメントと `cue.md` で迷わず書け、最初の `scope check` が通った。番号のキーと参照（`realizes`、`verifies`、`satisfies`）のつながりを検査に任せられ、仕様を書いて検査を通すまで約15分と、同じ規模の Markdown より短く感じた。計画の台帳、`execution`、説明資料の雛形の印の警告も役に立った。
- 書きにくさ：`status` を書く位置が自由で、同じ値が2つ入っても CUE は黙ってまとめる。既定値のある列挙の打ち間違いで、既定値との「conflicting values」の行が先に出て紛らわしい。`CUE_INVALID` の `hint` だけ英語。`scope render` の HTML は、デザインシステムを `file://` の絶対の道筋で読むので、別の機械では崩れる。

## Verification

### 受け入れ条件の確かめ（2026-11-01、main `c43aadd5b`）

読み取り専用の確認役（opus / high）が、AC ごとに証拠を集め、要所のテストを流した（`uv run pytest` の対象を絞って 629 passed と 134 passed、`node tests/browser/explanation-check.mjs` の全6場面と `iss-00487/explanation.html` が VALIDATED、`make lint` exit 0）。統括が、`main` の木が #487 の最終品質ゲートの `155d144d8` と同じこと（tree `2d518c46`）と、挙がったテストがあることを確かめた。全テストは `155d144d8` の最終品質ゲートで 4029 passed、8 skipped。

| AC | 判定 | 主な証拠 |
|---|---|---|
| AC-01 | 満たす | `tests/cli_runtime/test_issue474_scope_create.py`（`test_create_scaffolds_the_cue_set_with_the_given_assurance`、`test_a_missing_or_blank_assurance_stops_before_any_github_request`）。本物で #487・#489 を作った |
| AC-02 | 満たす | `tests/cli_runtime/test_issue473_scope_show.py`（CUE は値と理由、Markdown は unset、GitHub に触れない）。本物の `scope show iss-487 --json --offline` |
| AC-03 | 満たす | `tests/unit/cue/test_schema_v1_rules.py`（種類 × 規則 × レベルの全組） |
| AC-04 | 満たす | `tests/unit/cue/test_schema_v1_levels.py`、`tests/unit/application/test_scope_check.py::test_raising_the_level_requires_more_and_writing_it_passes`、白紙の試行 |
| AC-05 | 満たす | `tests/cli_runtime/test_issue473_scope_check.py`（ファイル、項目、行、hint、JSON、GitHub なし） |
| AC-06 | 満たす | `test_schema_v1_rules.py` の `execution-reference`、`tests/unit/cue/test_schema_v1_execution.py` |
| AC-07 | 満たす（版を固定する仕組みまで） | `tests/unit/cue/test_schema_v1_golden.py`、`tests/unit/infra/test_cue_schemas.py`。v2 はまだないので、design.md のテストの節が定める確かめ方による |
| AC-08 | 満たす | `tests/unit/cue/test_schema_v1_overlay.py`、`test_scope_check.py::test_a_repository_type_adds_its_constraint_and_rule` |
| AC-09 | 満たす | `application/scope_render.py::render_scope_html`（`docs/reference_cli.md` に入口）、`tests/unit/application/test_scope_render.py`、`tests/cli_runtime/test_issue476_scope_render.py` |
| AC-10 | 満たす | `tests/browser/explanation-check.mjs` の `local-http` 場面（CDN を止め、同梱の部品で図を描く）。手元で任意の検査（R-E4） |
| AC-11 | 満たす | 同じ道具の雛形の場面と、本物の `iss-00487/explanation.html` |
| AC-12 | 満たす | `tests/cli_runtime/test_issue477_mixed_repository.py`、`test_issue473_workspace.py`。本物（Markdown 281件と CUE 2件）で `workspace validate`・`doctor` が通る |
| AC-13 | 満たす | `iss-00477/report.md` の白紙のエージェントでの試行。ガイドを直した後の2回目は未確認（#487 の実際の作業担当が補う） |
| AC-14 | 満たす | 上の「I-7 spec-dock での導入」、`iss-00487/report.md` |
| AC-15 | 満たす | `make lint` exit 0（main）、全テスト 4029 passed（同じ木）、PR #488 の CI |
| AC-16 | 満たす | `tests/cli_runtime/test_issue473_work_finish.py`（誤りで止まる、直すと終わる、Markdown は今のまま）。本物の `work finish iss-00487` |
| AC-17 | 満たす | `test_scope_check.py::test_a_missing_or_skeleton_explanation_weighs_by_kind`、`::test_a_broken_explanation_is_an_error_for_every_kind`、`tests/unit/domain/test_explanation_shape.py` |
| AC-18 | 一部 | 前半は `test_issue474_scope_create.py::test_outdated_templates_stop_create_and_import_before_any_github_write`。後半（前の版の CLI が新しい配布資産で Markdown の Scope を作る）は、前の版の wheel を動かしていない。間接の証拠として、`test_issue474_schema3.py` が新しい資産のある版3のリポジトリで `.md` の一式を作ることを確かめ、`.md` の雛形はこの Epic の間に一度も変わっていない（git log が空） |

### 各 Issue の確かめ

- I-1〜I-6、#487：各 Issue の `report.md` に、仕様のレビュー、コードのレビュー、最終品質ゲート（`make lint`、`uv run pytest`）、PR の CI の結果がある。
- I-7：本物のカタログでの `scope create`（GitHub への作成、親への sub-issue、CUE の雛形）、`scope check iss-00487`（誤り0、警告0）、`scope render`、`work finish iss-00487`（Issue を閉じた）を、0.4.0 で確かめた。

## Residual Risks / Follow-ups

- 試しの改善の提案（`iss-00487/report.md`。優先度順）：(高) 既定値のある列挙の誤りの文の整理、(中) `CUE_INVALID` の `hint` の日本語化、(中) 雛形の手順の例で `status` を前に置く、(低) light でテストが1つもないことの情報、(低) `scope render` のデザインシステムの埋め込み・相対の道筋。利用者の承認で、Issue #489（iss-00489、CUE・standard）にまとめ、PR #490（`98ec261ea`）で直した（2026-11-01）。誤りの1件へのまとめ（`details.cue_related`）、`CUE_INVALID` の `hint` の日本語化、Issue の `plan.cue` の雛形の並び（Epic・Initiative の `plan.cue` には手順がないので変えていない）、light でテストがない Issue の警告 `SPEC_NO_TESTS`（K3 の形は変えない）、`scope render --design-system inline` と `render_scope_html` の既定値つきの `embed_design_system`（K5 に引数を足しただけ）。標準出力に出すので、相対の道筋は足していない。
- #489 の最終品質ゲートの P3（Issue にしていない）：制約のない列挙をまとめないことのテスト、`CUE_INVALID` 以外の `hint` の日本語化。
- #488 と #490 の変更は、まだ版を出していない（利用者の環境は 0.4.0）。次の版で届く。
- AC-18 の後半は間接の証拠だけ（上の表）。`.md` の雛形を外す epic-00424 の I-13 で、この条件は役目を終える。
- AC-10・AC-11 のブラウザーでの検査は手元で任意で、CI では回帰を拾わない。本物の配り手（ダッシュボードのサーバー）からの確かめは epic-00427 に残る。
- #487 の FQG-001（P3）：`-y` を help 用に argparse へ登録したため、`-yy` が誤りでなく受理になる（`--yes` の効果は付かない。安全側）。
- 未確認：祖先の `cue.mod` の評価への影響、`cue` の新しい版での誤りの文の形、`scope render` の `vendor_base` を渡した描画とブラウザーでの目視。
- `.md` の雛形の削除は epic-00424 の I-13 に移した。ほかの4つのリポジトリの `installation update` は、利用者の判断（epic-00424 の I-12 で 0.4.0 以上に上がる）。
