---
種別: 実装計画書（Issue）
ID: "iss-00435"
タイトル: "Add Throwaway Canonical Migration Script"
関連GitHub: ["#435"]
状態: "draft"
最終更新: "2026-10-26"
依存: ["requirement.md", "design.md"]
親: ["epic-00424", "init-00423"]
---

# iss-00435 Add Throwaway Canonical Migration Script — 実装計画

詳細: [Issue Plan Guide](../../../../../../docs/authoring/issue-plan.md)

## Planning Level
- strict（Epic の `plan.md` の一覧）。
- 理由：このスクリプトは、I-10 と I-12 で、GitHub に数百回書き、既定のブランチから仕様を外し、作業ツリーのファイルを動かす。誤ると、仕様や構造が失われ、戻しにくい。
- risk factor：GitHub の大量の書き込みと再開、作業ツリーのファイルの削除（`adopt-worktree`、`move-local`）、写した値のずれ、本物のリポジトリでの実行。
- 再評価の条件：Epic の契約（C1、C3、C5、C6、C7）や11章を変える必要が出たら、止まって統括に聞く。

## 目標
- `requirement.md` の AC-435-01〜15 を満たす `migrate.py`、`README.md` と、`canonical check` の調べること4の修正を、マージできるPRにする。
- 本物の5つのリポジトリで `plan` を読むだけで実行し、結果を `report.md` に書く。

## 順序・依存
- 依存：I-1、I-2、I-7（`main` にある。`d5c8cc943`）。並行：I-3、I-4（別の worktree）。`canonical_check.py` で衝突したら、後から入る側が `origin/main` のマージで取り込む。
- 進める順は、下の実装step の S0〜S12。S2〜S10 はスクリプトの中で積み上げるので、この順に行う。

## 統括の判断（2026-10-26、Orca の `ask` の答え）
- **Q1 move-local のカタログの作成**：カタログがなければ、`move-local --apply` が `canonical link` の手順3（GitHub に canonical がある場合）と同じ git の操作でカタログを作ってから移す。条件：C6 と同じ `-c`（フック、署名、fsmonitor、gc、maintenance）を付け、場所、ブランチの追跡、lock の理由を `canonical link` の手順3と同じにする（値は写して持ち、パッケージの定数と比べる）。その後の `spec-dock canonical link` が、そのカタログを「すでにある」と扱って成功することをテストで確かめる。`origin` に canonical がなく、移すファイルがあるときは止まる（空のディレクトリだけなら消す）。
- **Q2 adopt-worktree --apply**：統合は使い捨てのクローンで `merge-tree` で行い、競合は5章の規則（canonical の版が元の名前、ブランチの版が別名ファイル）で解き、`origin` に強制せずに push する（先に進まれたらやり直す）。その後、ブランチ B に `spec-dock/initiatives` を外すコミットを作り、取り込んだファイルを作業ツリーから消す（無視されたファイルは `move-local` のために残す）。条件：作業ツリーから消すのは、push が `origin` に届いたことと、消すファイルの中身が canonical の同じパス（名前の置き換えの後）と同じことを確かめた後だけにする。消す予定のファイルの一覧は `--apply` なしの出力に出す。どれかが一致しなければ、何も消さずに止める。
  - 実装の解釈（`design.md` の adopt-worktree の手順6）：ブランチで変えていないファイル（分岐点 M と同じ中身）は、canonical の履歴（C）に同じ中身があるので、「一致」として扱う。canonical が M の後に変えたファイルで、ブランチが変えていないものを、取り込みのたびに止めないためである。`.meta.json` は canonical に入れないので、構造の違いを作業の記録と出力に残してから消す。報告で統括に示す。
- **Q3 export-legacy の `.meta.json`**：構造の項目は GitHub から作り、それ以外（`_spec_dock`、`created_at`、`updated_at`、キーの順、変化がなければバイト列）は切り替え前のコミットの `.meta.json` を引き継ぐ。移行の後に作った Scope は今の13キーの形（`revision` 0、`lifecycle` null）。題名は GitHub の値。宣言も切り替え前のバイト列に戻す。条件：GitHub の題名が日本語のとき（I-6 の後）も、作った `.meta.json` で、従来モードの `workspace validate` と `scope show` が通ることをテストで確かめる。通らない場合は、推測で直さずに統括に知らせる。
- **Q4 register は足すだけ**：GitHub に違う種類のラベル、違う slug の印、違う親があるときは上書きせず、異常として残し、`verify` は不一致にする。ローカルでない ID の番号の不一致は `build-canonical` を止める（`design.md` では、`.meta.json` の身元の異常をすべて「止める」にし、`register --apply` も止める。安全側）。
- **Q5 読み取り元**：`.meta.json` は `origin/<既定のブランチ>` のコミットから読む。mainのチェックアウトの HEAD と違えば `plan` が警告する。`--repo OWNER/NAME` は予行演習（bare の `origin`）のときだけ要るようにし、本物では `origin` の URL から求めたものと一致しなければ止まる。
- **Q6 lint**：`scripts/static_analysis/run.sh` の対象に `scripts/migrate-to-canonical` を足してよい。I-13 でスクリプトを消すときに、この行も外す（I-13 への申し送り）。
- **Q7 undo**：`register` が作った Issue は `not_planned` で閉じて種類のラベルを外す。ラベルの定義は、`register` が作ったと `undo.jsonl` に記録したものだけを消す。もとからあったラベルや Issue には触れない。

## レビューの指摘の対応（文書の独立レビュー、2026-10-26）
| 指摘 | 判断 | 対応 |
|---|---|---|
| 1 P1 R-435-11 は main に入り済み | 反論 | レビューが読んだのは、この worktree のまだコミットしていない変更だった（`HEAD` の `canonical_check.py` は古い値も通す）。対応なし |
| 2 P1 `git commit -- <パス>` が削除をコミットしない | 妥当 | パスを付けないコミット（ステージ済みの変更がないことを先に確かめる）と、`ls-tree HEAD` の確かめにした |
| 3 P2 adopt の再実行が毎回 push する | 妥当 | 日時を固定し、取り込み済みなら push を飛ばす。止まった後の手順を README に書く。別名ファイルとの一致は Q2 の範囲外なので入れない |
| 4 P2 統合の基点の名前の変更の検出 | 妥当 | 置き換え後の基点 C' と `--merge-base` を使う（git 2.40 以上） |
| 5 P2 変更のないworktreeで外すコミットがない | 妥当 | 変更がなくても外すコミットと削除を行う |
| 6 P2 move-local が `.meta.json` を移す | 妥当 | 移すものに `.meta.json` があれば止まる |
| 7 P2 export-legacy の照合と AC | 一部妥当 | 照合はすでに `idmap.json` の番号で行う設計（手順2に明記）。AC から ID の置き換えと題名を除き、B0 の書き方を保つ |
| 8 P2 古い `origin/D`、build と cut の間の変更 | 妥当 | `ls-remote` との比較と、`build.json` の元の仕様のツリーとの比較を足した |
| 9 P2 Scope なしの判定 | 妥当 | 追跡されたファイルの有無で判定する |
| 10 P2 AC の抜け | 妥当 | AC-435-16〜20 を足した |
| 11 P3 予行演習の `idmap.json` | 妥当 | README に、本番の `idmap.json` を写す手順を書く |
| 12 P3 結果の記録のない作成の undo | 妥当 | 同じ探し方で探す |
| 13 P3 手元の canonical と origin の食い違い | 妥当 | 祖先でなければ止まる |
| 14 P3 `backend` が local | 妥当 | `META_INVALID` に入れた |
| 15 P3 終了コードの重なり | 妥当 | 文書に書いた（どちらも何も書いていない） |

## レビューの指摘の対応（実装の独立レビュー、2026-10-26、対象 `d5c8cc943...d0a7c3c6c`）
| 指摘 | 判断 | 対応 |
|---|---|---|
| ST-1 P1 成功後の `adopt-worktree` の再実行が、空のツリーを canonical の削除として push する | 妥当（再現された） | HEAD とインデックスに仕様のツリーがなければ「取り込み済み」として何もしない。追跡しているのに作業ツリーにないファイルがあれば止まる。回帰のテストを2件足した |
| ST-2 P2 `GIT_*` の環境変数をそのまま渡す | 妥当 | パッケージと同じく、本人情報と SSH のほかの `GIT_*` を落とす。写した値のテストと、`GIT_DIR` と `GIT_INDEX_FILE` を設定しても動くテストを足した |
| ST-3 P3 / SP-4 P3 終了コードの2と3 | 妥当 | 実行が書いたか（push、カタログ、移動、外すコミット、GitHub への書き込み）を記録し、書いた後の失敗はすべて3にする。docstring と README の3の説明を「次の1手に従う」にした |
| ST-4 P3 canonical のコミットが決定的でない | 妥当 | 作者と日時を split のコミットから取る（既定のブランチに仕様と関係のないPRが入っても同じコミットになる） |
| ST-5 P3 `.meta.json` の中身が残らない | 妥当 | `adopt/<ブランチ>.json` に中身を残し、消す直前にもう一度ハッシュを確かめる |
| ST-6 P3 / SP-3 P2 AC-435-01 のテストが拒否の経路しか通らない | 妥当 | 各サブコマンドが予定の表示まで進む状態を順に作り、前後の状態と GitHub の書き込みを比べるテストに作り直した |
| ST-7 P3 使われない fetch、一時ディレクトリの消し忘れ | 一部妥当 | fetch は分岐点のオブジェクトのために要る（コメントを足した）。`__enter__` の失敗で一時ディレクトリを消すようにした |
| SP-1 P1 AC-435-05 が未実施 | 反論 | 対象の SHA の後に、本物の5つで `plan` を実行し、`report.md` に書いた（この対応のコミットに含む） |
| SP-2 P2 `build-canonical` が止める異常の一部しか見ない | 妥当 | `.meta.json` だけで分かる異常の判定を `metadata_problems` に分け、`register` と `build-canonical` の両方で使う。テストを足した |
| SP-5 P3 `move-local` の予定が `--apply` の拒否を予告しない | 妥当 | 予定の段階でも `origin` の canonical の有無を確かめ、手元の canonical の食い違いを警告する |
| SP-6 P3 `adopt-worktree` が切り替えのマージの前でも動く | 妥当 | `origin/<既定のブランチ>` に仕様のツリーがあれば止まる。テストを足した |
| SP-7 P3 ほかの人が作ったラベルの定義を `undo` が消すおそれ | 妥当 | この実行が確かに作った定義だけを記録する。テストを足した |
| SP-8 P3 GraphQL のレート制限を待たない | 妥当 | `RATE_LIMITED` のエラーでは60秒待って3回まで試す。テストを足した |
| SP-9 P3 検証の抜け | 妥当 | 競合のテストで元の名前に canonical の版が残ることを、`export-legacy` の古い参照で止まることを確かめるテストを足した |

## 実装step
- **S0 文書**：`requirement.md`、`design.md`、`plan.md` を書き、Epic にない判断を統括に聞いた（上）。この会話を知らないサブエージェントにレビューさせ、指摘を分析して直す。
- **S1 I-7 の引き継ぎ**（AC-435-14）：`canonical_check.py` の調べること4を直し、版4で `specdock.writer/v1` の宣言が失敗の1件になるテストを足す（Red → Green）。
- **S2 偽の `gh` の追加**：番号で読む GraphQL（別名付きの `issue(number: N)`）、本文の PATCH、`DELETE /repos/{o}/{r}/labels/{name}` を足す。今のテストの振る舞いは変えない。
- **S3 写した値**（AC-435-13）：`migrate.py` の骨組み（引数、対象の解決、出力、終了コード）と、写した値。値をパッケージと比べるテスト。
- **S4 読み取りと `plan`**（AC-435-01、03 の一部、05、08）：`.meta.json` の読み取り、GitHub の読み取り、異常、ローカルの Scope の予定、CIの手順、作業用のworktree、無視されたファイル。
- **S5 `register` と速さ**（AC-435-06、07）：予定、書き込みの部品（速さ、レート制限、結果の分からない書き込み）、`undo.jsonl`、`idmap.json`、途中の停止と再開。
- **S6 `verify` と `undo`**（AC-435-06）。
- **S7 `build-canonical`**（AC-435-03、04、09）。
- **S8 `cut`**（AC-435-02、04）。
- **S9 `move-local`**（AC-435-03、10）：カタログの作成と、その後の `spec-dock canonical link`。
- **S10 `adopt-worktree`**（AC-435-11）。
- **S11 `export-legacy`**（AC-435-04、12）：従来モードの `workspace validate` と `scope show`。
- **S12 仕上げ**：`README.md`、`.gitignore`、`run.sh` の対象、本物の5つのリポジトリでの `plan`（AC-435-05）、`make lint`、全テスト、実装のレビュー、最終の品質の関門、`report.md`、PR。

## 検証
| AC | テスト |
|---|---|
| AC-435-01 | 各サブコマンドを `--apply` なしで実行し、前後の参照、`git status --ignored`、`.git/config`、`origin`、作業の記録、偽の `gh` の書き込みを比べる |
| AC-435-02 | `develop` の作り物で `cut --apply`、bare の `origin` のブランチのツリーと、ワークフローのバイト列 |
| AC-435-03 | Scope のない作り物で `build-canonical --apply` と `move-local --apply` |
| AC-435-04 | 使い捨てのクローンの形で3つの `--apply`、bare にだけ参照ができ、偽の `gh` に書き込みがない |
| AC-435-05 | 本物の5つで `plan`（読むだけ）。前後の `git for-each-ref` と `git status --porcelain` を比べ、`report.md` に書く |
| AC-435-06 | 書き込みの失敗を注入して `register --apply` を止め、再実行、`verify`、`undo --apply`、`register` の前後のファイル |
| AC-435-07 | `register` を読み込んで、注入した時計と偽の `gh` で呼び、書き込みの時刻の列と、`retry-after` の待ち |
| AC-435-08 | 2つのローカルの Scope と、番号の不一致、題名の食い違いの作り物で `plan`、`register --apply` の後の `idmap.json` |
| AC-435-09 | `build-canonical --apply` の結果のツリーを、元のツリーと比べる。2回目は何もしない |
| AC-435-10 | `.workbench` と追跡外のファイルと同じ名前のファイルで `move-local --apply`、続けて `spec_dock.cli.main` の `canonical link` |
| AC-435-11 | 移行前のブランチの worktree（コミット済みと未コミットの変更、両方で変えたファイル）で `adopt-worktree`、マージの後のツリー |
| AC-435-12 | `export-legacy --apply` の `.meta.json` と宣言、従来モードの `workspace validate` と `scope show`（日本語の題名） |
| AC-435-13 | 写した値とパッケージの定数、資産の比較 |
| AC-435-14 | `canonical check` の単体と CLI のテスト |
| AC-435-15 | `make lint`、`uv run pytest`（全体）。版3のテストは変えない |

## rollback
- マージの前：PRを閉じる。マージの後：PRを `git revert` する。スクリプトはまだどこでも本番で使われていない（I-10 の前）。
- `canonical check` の変更だけを戻すときも、`git revert` でよい（版4の宣言は本物にまだない）。

## exit / handoff
- 完了：AC-435-01〜15 を満たし、最終の品質の関門に合格し、PRがマージできる状態で、`report.md` を書いた。`work finish` は、マージの後に統括の指示で行う。
- I-10、I-12 への引き渡し：`README.md` の手順、`plan` の本物の結果（`report.md`）、予行演習の手順。
- I-13 への申し送り：`scripts/migrate-to-canonical/` と `scripts/static_analysis/run.sh` の対象の行を消す。
