---
種別: レポート（Issue）
ID: "iss-00473"
タイトル: "Add Scope Check With CUE"
関連GitHub: ["#473"]
最終更新: "2026-10-31"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00425", "init-00423"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

CUE の Scope を `spec-dock scope check <ID>` でインターネットなしに検査できるようにし、`work finish` が誤りの残る CUE の Scope を閉じないようにした。`scope show --json` は保証レベルを返し、`workspace validate`・`doctor` は Scope の形式ごとに必須の文書を変える。最終品質ゲートは `79688170ff27e81fe77e1edad2f551d2d8f08514` で合格した。

## Outcome

### 実装したこと

| 部品 | 中身 |
|---|---|
| `runtime/infra/cue_tool.py` | `cue` を PATH から探し、`cue version` で v0.17.1 以上を確かめる（`CUE_NOT_FOUND`、`CUE_VERSION_UNSUPPORTED`、exit 3）。引数の並びで（シェルを通さず）時間の上限付きで `cue export` を呼ぶ（`CUE_TIMEOUT`、`CUE_FAILED`、exit 5）。誤りの文を、道筋・文・位置（絶対パス）に分ける |
| `runtime/domain/explanation_shape.py` | K5 の薄い説明資料の形（`ds-source` がちょうど1つ、前付けの `title`、`ds.css` と `ds.js` の読み込み）と、雛形の印の判定 |
| `runtime/application/scope_check.py` | 形式の判定（`scope_format`）、`requirement.cue` だけからの保証レベルの読み取り（`read_assurance`）、K1 の並べ方（`k1_files`）、1つの Scope の検査（`check_scope_documents`）。結果は K3 の `Diagnostic` の一覧（`CUE_INVALID`、`SPEC_FINDINGS`、`ASSURANCE_UNREADABLE`、`SCOPE_FORMAT_CONFLICT`、`SCOPE_DOCUMENT_MISSING`、`EXPLANATION_*`）。評価の JSON の全体も `evaluation` に持つ（I-5 用） |
| `scope check`（`canonical_scope_check.py`、CLI） | 新しい葉（54番目）。誤りがあれば exit 7（`SCOPE_CHECK_FAILED`）。テキストでも1件ずつ、ファイル、行、項目、直し方を示す。schema 3 は `CANONICAL_NOT_MIGRATED` |
| `work finish`（`canonical_work.py`） | GitHub の読み直しの後、保存の確かめと書き込みの前に検査する。開いている Scope は誤り・道具の失敗で止まる（何も書かない。dry-run も同じ）。既に完了の Scope は警告にして選択を外す。保存を待つ間に開き直されたら、2回目の読み直しの後に止まる |
| `scope show`（`canonical_scope_read.py`） | `data.result.assurance = {level, reason, source(cue/unset/unreadable), problem}`。読めなくても成功する |
| `workspace validate`・`doctor`（`canonical_workspace.py`） | CUE の Scope は `requirement.cue`、`design.cue`、`plan.cue`、`report.md` を求める。両方の `requirement` は `SCOPE_FORMAT_CONFLICT`。`cue` を呼ばない |
| 配布資産（と dogfood の写し） | `docs/reference_cli.md`（C54、公開54 leaf）、`docs/README.md`、`docs/cli-redesign-guide.html`（全54コマンドと C54 の行）、`docs/canonical.md`（エラーの表に `SCOPE_CHECK_FAILED`、`SCOPE_FORMAT_CONFLICT`、`CUE_*`。`SCOPE_DOCUMENT_MISSING` に CUE の文書の組）。`static-inventory.json` の4つの `sha256` |

コミット（`origin/main` `2cf4e961a` から）：`f0da47d88`（部品）、`83b3d278c`（コマンドと統合）、`4c44014ef`（`canonical.md` の文書の組）、`79688170f`（コードのレビューの指摘の修正）。

### 統括と決めたこと（2026-10-31）

Q1〜Q8 は `design.md` の「決めたこと」のとおり。Q7 は統括の変更で、既に完了の Scope の `work finish` では止めずに警告にする。

## Verification

### 受け入れ条件

| AC | 確かめたテスト | 結果 |
|---|---|---|
| AC-01 | `tests/cli_runtime/test_issue473_scope_show.py`（cue・unset・unreadable の各場合、`--offline`、GitHub に届かない場合） | 合格 |
| AC-02 | `tests/cli_runtime/test_issue473_scope_check.py`（JSON、テキスト、前後のファイルの一致、`--offline`、GitHub の 503） | 合格 |
| AC-03 | `tests/unit/application/test_scope_check.py::test_every_v1_sample_checks_as_recorded`（I-1 の見本8つ） | 合格 |
| AC-04〜AC-06 | `tests/unit/application/test_scope_check.py`（リポジトリの型、レベルの書き換え、`assurance` の置き場、`schema` の誤りと持っていない版） | 合格 |
| AC-07 | `tests/unit/infra/test_cue_tool.py`、`test_issue473_scope_check.py`（偽の `cue`、K1 の引数の並び） | 合格 |
| AC-08 | `test_issue473_scope_check.py`（`cue` なしの Markdown の Scope、両方の形式） | 合格 |
| AC-09〜AC-11 | `tests/cli_runtime/test_issue473_work_finish.py`（8件。開き直しの場合を含む）、既存の `test_issue432_work_finish.py` ほか（変更なし） | 合格 |
| AC-12 | `tests/cli_runtime/test_issue473_workspace.py`、既存の `test_issue431_workspace.py` | 合格 |
| AC-13 | `tests/unit/domain/test_explanation_shape.py`、`test_scope_check.py`（種類ごとの重さ） | 合格 |
| AC-14、AC-15 | `test_issue473_scope_check.py`（schema 3、ヘルプ、completion） | 合格 |
| AC-16 | `make lint`、clean な clone での全体のテスト。既存のテストの変更は、葉の数（53→54）と、全部の葉を流す一覧への `scope check` の追加、読むだけの葉の一覧だけ。`src/spec_dock/cue/`、`spec-dock/templates/`、`src/spec_dock/assets/spec_dock/templates/` は変えていない | 合格 |

実物のカタログでの読むだけの確かめ（この worktree）：`scope check iss-473`（Markdown の Scope）は `checked=false` で成功、`scope show iss-473 --json` の `assurance` は `unset`、`workspace validate` は誤りなし。

### レビュー

- 仕様のレビュー（spec-reviewer opus / xhigh）：第1回 合格（P2×3、P3×1。すべて直した）、第2回 合格（P3×2。文言を直した）。記録は worktree の `.workbench/spec-review/iss-00473/`。
- コードのレビュー（code-reviewer opus / high、Standards と Spec の2本）：どちらも合格。Standards の P2（型にしか位置のない誤りの `hint` が同梱の型を直すよう示す）、P3（`_export` の型注釈）、Spec の P3（`requirement.cue` の読み取りの失敗で `cue_output` が空）を `79688170f` で直した。

### 最終品質ゲート（`final-quality-gate`、キャンペーン `iss-00473-fqg1`）

- 合格の SHA：`79688170ff27e81fe77e1edad2f551d2d8f08514`（第1回、clean な worktree）。
- 主のレビュアー（quality-gate-reviewer opus / xhigh）：合格。P0 0、P1 0、P3 1、範囲は完全。
- 2人目のレビュアー（quality-gate-reviewer sonnet / high）：合格。指摘なし、範囲は完全。
- テスト：`make lint` → exit 0。`.workbench/bin/full-tests-clean-clone.sh`（その SHA をカタログへのリンクのない clean な clone に取り出し、`PATH` に `cue` v0.17.1 を足して `uv run pytest`）→ exit 0（3879 passed、9 skipped、20分20秒）。
- ChatGPT のレーンは使っていない（スキルが無効）。
- 記録：worktree の `.workbench/final-quality-gate/iss-00473-fqg1/closure.md`。

### PR と CI

- PR：https://github.com/chemitaro/spec-dock/pull/483（`chemitaro/iss-00473` → `main`、head `79688170ff27e81fe77e1edad2f551d2d8f08514`、`Refs #473`、`Refs #425`）。
- CI（2026-10-31T12:45Z の観測）：Provider CI（run 41201674344）、SpecDock check（run 41201674360）、Commit identity（run 41201674388、41201647154）がすべて success。GitHub は OPEN、MERGEABLE、CLEAN。観測は base リポジトリの Actions と Commit Status に限る（外部の CheckRun は対象外）。
- マージは人が行う。`spec-dock work finish` は、マージの後に統括の指示で行う。

### 既知の問題

- カタログへのリンクがある worktree では、`tests/unit/infra/test_authoring_kit_assets.py` の12件が、この Issue と関係なく落ちる（I-1・I-4 と同じ）。このため、全体のテストはリンクのない clean な clone で通した。

## Residual Risks / Follow-ups

- **P3（ゲートの主のレビュアー、情報だけ）**：`docs/canonical.md` のエラーの表は、保存を待つ間に開き直された CUE の Scope の `work finish` が `partial`（exit 6）になる場合を書いていない（`design.md` 6 と AC-11 にはある）。I-6（ガイド）で書き足すとよい。
- **未確認**：祖先のディレクトリにある `cue.mod` が評価に影響しないこと（型は外部のモジュールを使わないので影響しない見込み）。
- **未確認**：`cue` の v0.17.1 より新しい版での誤りの文の形（解析は行頭と字下げの2つの形だけに依り、読めない行も誤りの文として残す）。
- **未確認**：本物の CUE の Scope での `scope check` と `work finish`（I-7 まで本物のカタログに CUE の Scope はない。テストの中のカタログで確かめた）。
- `scope check` の1回で `cue` を最大4回起動する。大きな Scope で遅ければ、I-7 で読み取りをまとめる。
- slices のキーが GitHub の本当の子かは調べない（Q5）。I-7 で要れば足す。
- I-3 へ：作った直後の Scope は、Issue と Initiative では `EXPLANATION_SKELETON` の警告だけ、Epic では誤りになる。`read_assurance`、`scope_format` を使える。
- I-5 へ：`k1_files`、`ScopeCheckReport.evaluation`、`cue_tool.locate_cue`。
- I-6 へ：`scope check` の使い方、K3 のコードの表、`work finish` の止まり方、`scope show` の `assurance`、`cue` の最低の版 v0.17.1、上の P3。
