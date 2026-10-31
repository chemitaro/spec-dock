---
種別: 実装計画書（Issue）
ID: "iss-00473"
タイトル: "Add Scope Check With CUE"
関連GitHub: ["#473"]
状態: "draft"
最終更新: "2026-10-31"
依存: ["requirement.md", "design.md"]
親: ["epic-00425", "init-00423"]
---

# iss-00473 Add Scope Check With CUE — 実装計画

詳細: [Issue Plan Guide](../../../docs/authoring/issue-plan.md)

## Planning Level

- 選んだ level：`strict`（Epic の `plan.md` の指定）。
- 理由：`work finish` を止める条件を変える。誤って止めると、利用者とエージェントが作業を終えられなくなる。検査の結果の形（K3）は、I-3、I-5、I-6、epic-00427 が使う公開の契約である。CLI の葉と、配布資産の文書も変わる。
- risk factor：配られる CLI の契約（新しい葉、`scope show` の鍵、終了の状態とコード）、`work finish` の止まり方、外の道具（`cue`）の子のプロセス、配布資産の変更。
- 再評価の条件：検査が、カタログや GitHub に書くことになったら、または利用者の秘密を扱うことになったら `critical` に上げる。今の範囲（読むだけの検査と、書く前に止まる `work finish`）では起きない。

## 目標

この Issue の `requirement.md` の AC-01〜AC-16 を満たし、I-3（作るときの一式。`scope check` で雛形を確かめる）と I-5（描画。`cue` の呼び出しと評価を使う）が、この部品の上で始められる状態にする。

## 順序・依存

- 前提：I-1（型）と I-4（説明資料の雛形）は `main` にマージ済み。`spec-dock work start iss-00473` は 2026-10-31 に通った。
- 手順は次の順に進める。1（`cue` の部品）と 2（説明資料の形）は独立なので、どちらから始めてもよい。3 は 1、2 に依る。4〜7 は 3 に依る。8 は 4 の葉に依る。

## 実装step

各手順は、テストを先に書き（Red）、通し（Green）、整える（Refactor）。区切りでコミットする（コードとテストと配布資産だけ。仕様はコミットしない）。

1. **`cue` の部品**：`runtime/infra/cue_tool.py`。`locate_cue`（PATH、版の読み取り、最低の版）、`export`（引数の並び、時間の上限）、`parse_cue_errors`（行頭と字下げ、道筋、相対パスの解決）。単体のテスト：偽の `cue`（ない、古い、読めない版、時間切れ、起動の失敗）と、実際の `cue` の誤りの文の解析（AC-07 の一部）。
2. **説明資料の形**：`runtime/domain/explanation_shape.py`。単体のテスト：I-4 の雛形のバイト、印を消したもの、壊し方ごと（AC-13 の一部）。
3. **1つの Scope の検査**：`runtime/application/scope_check.py`（`scope_format`、`read_assurance`、`check_scope_documents`）。単体のテスト：実際の `cue` で、誤りなし、形の誤り（派生の誤りを捨てる）、指摘、`schema` の誤りと持っていない版、`assurance` の置き場、リポジトリの型、文書の欠け、説明資料の重さ（AC-03〜AC-06、AC-13 の一部）。
4. **`scope check` のコマンド**：`canonical_scope_check.py`、`catalog.py`、`canonical_dispatch.py`、`runtime_dispatch.py`（schema 3）、`envelope.py`（テキスト）。CLI のテスト：`CanonicalWorld` で JSON とテキスト、インターネットなし、書かないこと、Markdown の Scope と `cue` なし、schema 3、ヘルプと completion（AC-02、AC-07、AC-08、AC-14、AC-15）。
5. **`scope show` の `assurance`**：`canonical_scope_read.py`。CLI のテスト（AC-01）。
6. **`workspace validate`・`doctor`**：`canonical_workspace.py`。CLI のテスト（AC-12）。
7. **`work finish`**：`canonical_work.py` の `_check_before_finish`。CLI のテスト（`WriteWorld`）：誤りで止まり何も書かない、dry-run、直して閉じる、警告付きで閉じる、既に閉じた Scope、Markdown の Scope と `cue` なし（AC-09〜AC-11）。
8. **葉の数と参照の文書**：配布資産 `docs/reference_cli.md`（C54）、`docs/README.md`、`docs/cli-redesign-guide.html` と、その dogfood の写し、`static-inventory.json` の `sha256`。葉の数を固定した既存のテストの期待を 54 にする（AC-15、AC-16）。
9. **全体の確かめ**：`make lint`、`PATH="$PWD/.workbench/bin:$PATH" uv run pytest`。カタログへのリンクがある worktree では `tests/unit/infra/test_authoring_kit_assets.py` の12件が、この Issue と関係なく落ちる（既知）。全体のテストは、リンクのない clean な clone（この PR の HEAD を clone し、`cue` を PATH に足す）で通す（AC-16）。
10. **レビューと品質ゲート**：`spec-review`（opus / xhigh）で3つの文書。`code-review`（opus / high）、指摘は `analyze-review-findings`。`final-quality-gate`（opus / xhigh、sonnet / high）。合格の証拠を `report.md` に書く。
11. **報告と PR**：`report.md`、`main` への PR（`Refs #473`、`Refs #425`）、`github-pr-checks` で CI を確かめる。マージは人が行い、`work finish` は統括の指示を待つ。

## 検証

| AC | 確かめ方 |
|---|---|
| AC-01 | `tests/cli_runtime/test_issue473_scope_show.py` |
| AC-02 | `tests/cli_runtime/test_issue473_scope_check.py`（JSON、テキスト、`--offline`、偽の `gh` の失敗、前後のファイルの一致） |
| AC-03 | `tests/unit/application/test_scope_check.py`（I-1 の見本のすべて） |
| AC-04、AC-05、AC-06 | `tests/unit/application/test_scope_check.py` と `tests/cli_runtime/test_issue473_scope_check.py` |
| AC-07 | `tests/unit/infra/test_cue_tool.py`、`tests/cli_runtime/test_issue473_scope_check.py`（偽の `cue`） |
| AC-08 | `tests/cli_runtime/test_issue473_scope_check.py`（PATH から `cue` を外す） |
| AC-09、AC-10、AC-11 | `tests/cli_runtime/test_issue473_work_finish.py`、既存の `tests/cli_runtime/test_issue432_work_finish.py` を変えずに通す |
| AC-12 | `tests/cli_runtime/test_issue473_workspace.py` |
| AC-13 | `tests/unit/domain/test_explanation_shape.py`、`tests/unit/application/test_scope_check.py` |
| AC-14、AC-15 | `tests/cli_runtime/test_issue473_scope_check.py` |
| AC-16 | `make lint`、clean な clone での全テスト。`git diff --stat origin/main -- tests/` で、既存ファイルの変更が葉の数の更新だけ。`git diff origin/main -- src/spec_dock/cue spec-dock/templates src/spec_dock/assets/spec_dock/templates` が空 |

- 回帰：全テスト（Markdown の Scope の `work finish`、`scope show`、`workspace validate`・`doctor` の既存のテストを含む）。
- 互換：`scope show` の既存の鍵が変わらないこと（既存のテスト）。配布資産の写しと inventory の一致（既存の資産のテスト）。
- negative test：失敗・境界条件ごと（`cue` の5つの失敗、文法、`schema` の3つ、`assurance` の置き場、両方の形式、文書の欠け、説明資料の5つの壊し方、`work finish` の誤り・道具の失敗）。
- migration failure と rollback：N/A（データの移行がない。PR を戻せば元に戻る）。
- security / privacy：`cue` は引数の並びで呼び、シェルを通さない（Scope のファイルの道筋に特殊な文字があっても、コマンドにならない）。検査は秘密を扱わず、外へ送らない。テストで、引数の並びを確かめる。
- operability / observability：誤りごとに、ファイル、位置、直し方、次の手順を示す。`cue` の誤りの文の全体も返す。時間の上限は `--timeout` で変えられる。

## rollback

- この PR を戻せば、葉、部品、`work finish` の検査、`scope show` の鍵、配布資産の文書の変更が、まとめて元に戻る。データの戻しは要らない（migration：N/A。CUE の Scope は I-7 まで本物のカタログにない）。
- マージの後に、`work finish` を誤って止める不具合が見つかったら：forward recovery として、修正の PR を出す。急ぐときは、統括がこの PR を戻す PR を出す（Markdown の Scope は影響を受けない）。担当は統括、順番は「戻す PR → 原因の修正 → 入れ直し」。

## exit / handoff

- 終わりの条件：AC-01〜AC-16、仕様のレビューとコードのレビュー、最終品質ゲートの合格、`report.md`、マージできる PR。
- I-3 へ：作った直後の Scope を `scope check` で確かめるときの期待（Issue と Initiative は `EXPLANATION_SKELETON` の警告だけ、Epic は誤り）。`read_assurance` と `scope_format` を使える。
- I-5 へ：`cue_tool.locate_cue` と `CueTool.export`、`check_scope_documents` の評価の並べ方（`scope_check.py` の中の関数として切り出してある K1 の並べ方）、`findings` の扱い。
- I-6 へ：`scope check` の使い方、誤りのコードの表（K3）、`work finish` の止まり方、`scope show` の `assurance`、`cue` の最低の版。
- epic-00427 へ：K3（誤りのコードと `details` の鍵）、`scope show` の `assurance`。
- 残るリスク：祖先のディレクトリの `cue.mod` の影響（未確認）。`cue` の新しい版での誤りの文の形の変化。

## モデルと推論

- この Issue のセッション：opus / high（Epic の `plan.md` の「モデルと推論」の strict の実装）。
- レビュアー：spec-reviewer opus / xhigh、code-reviewer opus / high、quality-gate-reviewer opus / xhigh と sonnet / high（Epic の `plan.md` の strict の行）。
