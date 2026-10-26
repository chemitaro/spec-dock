---
種別: 要件定義書（Issue）
ID: "iss-00435"
タイトル: "Add Throwaway Canonical Migration Script"
関連GitHub: ["#435"]
状態: "draft"
最終更新: "2026-10-26"
親: ["epic-00424", "init-00423"]
---

# iss-00435 Add Throwaway Canonical Migration Script — 要件定義

詳細: [Requirement Guide](../../../../../../docs/authoring/requirement.md)

表示名：使い捨ての移行のスクリプトを足す（Epic の I-8）

## 目的
R-J1 の5つのリポジトリを、安全に移行でき、必要なら戻せる。各リポジトリで、本番の前に予行演習ができる。

- 材料：Epic の `plan.md` の「I-8 Add Throwaway Canonical Migration Script」の節（価値、作るもの、受け入れ、I-7 から引き継ぐもの、注意）と、Epic の `design.md` の11章（移行のスクリプト）、2章の表し方（C1）、3章の無視の設定（C3）、5章の canonical の中身と別名ファイルの名前（C5）、8章（C7 の見本と版のファイル、`canonical check` の調べること4）、「移行・互換性・rollback」。Issue をまたぐ契約は、Epic の `plan.md` の「Issue をまたぐ契約」の表に従う。
- 依存（`plan.md` の I-番号）：I-1（C1、C2）、I-2（C3、C5、C6）、I-7（C7）。どれも `main` に入っている。Planning Level：strict。
- この Issue は、どの契約の持ち主でもない。C1、C3、C5、C6、C7 の値を、パッケージを読み込まない1つのファイルに写して持ち、写した値がパッケージの定数と同じことをテストで確かめる（Epic の `plan.md` の「Issue をまたぐ契約」の注）。
- Epic の文書にない判断は、統括に聞いて決めた（`plan.md` の「統括の判断」）。

## 背景
- Epic は、仕様の構造の正本を GitHub Issue に、内容の正本を `spec-dock/canonical` ブランチに移す。今の5つのリポジトリ（R-J1）は、構造を各 Scope の `.meta.json` に、内容を既定のブランチの `spec-dock/initiatives/` に持っている。これを一度だけ移す道具が要る（R-G1）。
- 移行は、GitHub への数百回の書き込みと、既定のブランチからの仕様の切り離しを含み、戻しにくい。そのため、既定では何も書かず、止まっても続きから再開でき、取り消せ、使い捨てのクローンで予行演習できなければならない（R-G2、R-J3）。
- SpecDock の CLI とパッケージには入れない（R-G1）。撤去（I-13）で消した後も、版のタグ `v0.3.0` から取り出して戻すのに使えるよう、パッケージを読み込まない1つのファイルにする。
- 関係者：
  - 統括のエージェント（I-10、I-12）：`README.md` の手順で、各リポジトリの準備、予行演習、本番、戻しを行う。
  - 利用者：今の運用を止めずに準備でき（R-G3、R-J2）、必要なら戻せること。
  - 5つのリポジトリ：既定のブランチ（taikyohiyou_project は `develop`）、CIの形、作業用のworktreeの数、Scope の有無が、それぞれ違う（Epic の `design.md` の Current の表）。

## 観測可能な要件

### R-435-01 1つのファイルと手順書（R-G1、R-G6）
- `scripts/migrate-to-canonical/migrate.py` を置く。Python 3.10 以上の標準ライブラリと、`git` と `gh` のコマンドだけを使い、`spec_dock` を読み込まない。
- 同じ場所に `README.md` を置き、各リポジトリの準備、予行演習（Epic の `design.md` 11章の6つの手順）、本番（「各リポジトリの切り替え」の手順）、戻し方、Scope のないリポジトリの扱いを短く書く。
- 作業の記録は `<置き場>/<owner>-<repo>/` に置く。置き場の既定は `scripts/migrate-to-canonical/.state/`（Git で無視）で、`--state-dir` で変えられる。記録は、取り消しの一覧 `undo.jsonl`、ID の置き換えの表 `idmap.json`、canonical を作った記録 `build.json` である。

### R-435-02 共通の振る舞い（R-G2）
- サブコマンドは `plan`、`register`、`verify`、`build-canonical`、`cut`、`move-local`、`adopt-worktree`、`undo`、`export-legacy` である。対象は `--project <対象の mainのチェックアウト>` で選ぶ。
- どのサブコマンドも、既定では予定を表示するだけで、リポジトリ、`.git`、GitHub、作業の記録に何も書かない。`--apply` を付けたときだけ書く（`plan` と `verify` は `--apply` を受け付けない）。何度実行しても同じ結果になる。
- 既定のブランチは、対象の `origin/HEAD` から求める。`main` を決め打ちしない。
- GitHub の owner と repo は、`origin` の URL から求める。`origin` が GitHub でない（予行演習の bare のリポジトリ）ときだけ `--repo OWNER/NAME` を要し、`origin` が GitHub なのに `--repo` が違えば止まる。
- 結果は文字で、`--json` を付けると1つの JSON で出す。終了コードは、0（問題なし）、1（読むだけで問題を見つけた。`plan` の止める異常、`verify` の不一致）、2（書く前に止まった。引数の誤りも argparse の2で、何も書かない）、3（書いた後に止まった。もう一度の実行で続きから進む）である。
- 書くサブコマンドは、手元の `origin/<既定のブランチ>` が `origin` の今の先頭（`git ls-remote`）と違えば、書く前に止まる（次の1手 `git fetch origin`）。`plan` は警告する。

### R-435-03 `plan`（R-G4、R-J5）
- `.meta.json`（`origin/<既定のブランチ>` のコミットのもの）と GitHub を読むだけで、次を一覧にする。
  - Scope の数（種類ごと）と依存の数、登録の予定（書き込みの種類ごとの回数と、かかる時間の見込み）。
  - データの異常：循環する依存、種類の規則の違反、親や依存先が見つからない、閉じた親の下の開いた子、ID と番号の不一致、GitHub との題名の食い違い、ローカルの Scope、GitHub との食い違い（違う種類のラベル、違う slug の印、違う親）、GitHub にない Issue。
  - ローカルの Scope（`init-local-00002` と `init-local-00003` の形）ごとの置き換えの予定（結び付いた Issue の題名が同じなら、その番号の ID。違えば新しい Issue を作る）。
  - SpecDock を呼ぶ今のCIの手順：`.github/` の下で `spec-dock` か `specdock` を含む行（ファイル、行番号、行）。
  - 作業用のworktreeごとの、既定のブランチにない仕様の変更（コミット済みと未コミット）の有無とパス。Git が prunable と示すworktreeは、そう示す。
  - mainのチェックアウトの `spec-dock/initiatives/` の、追跡されていないファイルと無視されたファイルの数（`move-local` で移すもの）。
  - mainのチェックアウトの HEAD が `origin/<既定のブランチ>` と違えば、警告。

### R-435-04 `register` と `undo`（R-G2、R-G3）
- 種類のラベル3つの定義（ないときだけ作る）、各 Issue の種類のラベル、本文の slug の印、sub-issue、blocked by を、足すだけで登録する。題名と状態は変えない。リポジトリのファイルは変えない。
- GitHub に違うもの（違う種類のラベル、違う slug の印、違う親）があるときは上書きせず、異常として示して、その項目を飛ばす。
- ローカルの Scope は、`plan` の予定のとおりに、既にある Issue の番号に結び付けるか、`.meta.json` の題名で新しい Issue を作り、`idmap.json` に記録する。
- 書き込みは1つずつ送り、間を1秒以上あけ、1分に80回、1時間に500回を超えない。レート制限の応答では待って続ける。
- 書く前に意図を、書いた後に結果を `undo.jsonl` に足す。途中で止まっても、もう一度の実行が、GitHub の今の状態から重複なく続きを行う。
- `undo` は、`undo.jsonl` に記録した、`register` が足したものだけを、新しいものから順に外す（依存、親子、本文の印、ラベル、作った Issue は `not_planned` で閉じて種類のラベルを外す、作ったラベルの定義は消す）。もとからあったラベルや Issue には触れない。

### R-435-05 `verify`（AC-04）
- `.meta.json` の構造（`idmap.json` で置き換えた後）と GitHub の構造が一致するかを比べ、不一致を一覧にする。題名の食い違いは警告で、一致の判定に入れない（GitHub の題名を正とする）。
- 既定のブランチから仕様を外した後は、外す前のコミットの `.meta.json` と比べる。手元に canonical があれば、その中に `.meta.json` がないことも確かめる。

### R-435-06 `build-canonical`
- 使い捨てのクローンで `git subtree split --prefix=spec-dock/initiatives` を行い、その先に、`idmap.json` に従ってディレクトリの名前を変え、形式1の管理ファイル（C5）を足し、`.meta.json` を消したコミットを作って、`origin` の `spec-dock/canonical` に push する。対象のリポジトリの `.git` には何も残さない。
- `spec-dock/initiatives` の下に追跡されたファイルが1つもないリポジトリ（Scope のないリポジトリ）では何もしない。止める異常（ID と番号の不一致など）があるとき、ローカルの Scope が `idmap.json` にないときは、書く前に止まる。
- `origin` の `spec-dock/canonical` がすでに同じコミットなら何もしない。違うコミットなら、強制せずに止まる。

### R-435-07 `cut`（R-J5）
- `origin/<既定のブランチ>` から、仕様のツリーを外し、宣言を版4（`writer_protocol` は `specdock.worktree-writer/v1`）にし、`.github/workflows/spec-dock-check.yml`（C7 の見本。`branches` はそのリポジトリの既定のブランチ）を足したコミットのブランチを作り、`origin` に push する。PRは作らない。
- 今のCIの SpecDock の手順は書き換えず、一覧を示す。
- 0.3.0 の配布資産（版のファイルと無視の3行）がないとき、仕様のファイルがあるのに `origin` に canonical がないとき、`build.json` に記録した元の仕様のツリーと今の仕様のツリーが違うとき（canonical を作った後に仕様が変わった）、既定のブランチの名前が見本の形に入らないときは、書く前に止まる。

### R-435-08 `move-local <チェックアウト>`
- そのチェックアウトの `spec-dock/initiatives/` の下の、追跡されていないファイルと無視されたファイルを、カタログの同じ相対パス（`idmap.json` で置き換えた後）へ移す。同じ名前があれば上書きせず、`.local-<PC名>` を付けた名前にする。移した後、空になったディレクトリを消し、`canonical link` がリンクを置けるようにする。
- カタログがまだなければ、`canonical link` の手順3と同じ方法でカタログを作ってから移す（統括の判断 Q1）。`origin` に canonical がなく、移すファイルがあるときは止まる。手元の `spec-dock/canonical` が `origin` のものと同じかその祖先でないときは止まる。追跡されたファイルが残っているとき（既定のブランチの取り込みか `adopt-worktree` の前）と、移すものに `.meta.json` があるとき（canonical に入れてはならない）は、何も移さずに止まる。

### R-435-09 `adopt-worktree <チェックアウト>`（R-G5、AC-05）
- 移行前のブランチのチェックアウトの仕様を、コミットしていない変更も含めて canonical に3者マージで取り込み、`origin` に push する（Epic の `design.md` 11章の手順1〜3）。競合は5章の規則で解く。
- push が届き、作業ツリーのファイルの中身が canonical の同じパス（または分岐点と同じ中身）と同じことを確かめた後で、そのブランチに `spec-dock/initiatives` を外すコミットを作り、取り込んだファイルを作業ツリーから消す。無視されたファイルは `move-local` のために残す。どれかが一致しなければ、何も消さずに止まる（統括の判断 Q2）。
- 仕様の変更がないチェックアウトでも、外すコミットと削除は同じように行う（push は行わない）。そのため、各チェックアウトの手順は、`adopt-worktree`、`move-local`、既定のブランチの取り込み、`canonical link` の順でよい。
- もう一度の実行は、取り込み済みなら push を行わない（取り込むコミットの日時を固定する）。
- `.meta.json` の構造の違い（親、依存、題名の変更、増えた Scope と消えた Scope）を一覧にする。登録はしない。

### R-435-10 `export-legacy`（戻し方）
- `origin/<既定のブランチ>` から新しいブランチを作り、`spec-dock/initiatives` にカタログ（`origin` の canonical）の内容を置き、GitHub の構造から `.meta.json`（schema 3）を作り直し、宣言を版3に戻し、`spec-dock-check.yml` を外して、`origin` に push する。PRは作らない。
- 作り直した `.meta.json` は、切り替え前のもの（`idmap.json` で番号を対応させる）と、`revision` と `lifecycle` と、切り替えの後に GitHub で変わった項目（題名など）と、`idmap.json` による ID の置き換えのほかは一致する。何も変わっていなければバイト列まで同じで、変わったものは切り替え前のファイルの書き方（1行か字下げか、キーの順）を保つ。外した今のCIの手順は手で戻すことを示す。

### R-435-11 `canonical check` の調べること4（I-7 から引き継ぐもの）
- 版4の宣言の `writer_protocol` が `specdock.worktree-writer/v1` でなければ（古い `specdock.writer/v1` を含む）、調べること4の失敗の1件（パスと次の1手付き）にする。

## スコープ

### 対象
- `scripts/migrate-to-canonical/migrate.py`、`README.md`、`.gitignore`（`.state/` を無視する）。
- `src/spec_dock/runtime/application/canonical_check.py` の調べること4（R-435-11）。
- `scripts/static_analysis/run.sh` の対象に `scripts/migrate-to-canonical` を足す（統括の判断 Q6）。
- テスト：`tests/integration/migration/`（スクリプトの受け入れ）、`tests/unit/application/test_canonical_check.py` か `tests/cli_runtime/test_issue434_canonical_check.py`（R-435-11）、偽の `gh`（`tests/support/fake_github.py`）への追加（番号で Issue を読む GraphQL、本文の PATCH、ラベルの定義の削除）。
- 本物の5つのリポジトリでの `plan` の読むだけの実行と、その結果の報告書への記録。

### 対象外
- 本物の GitHub への書き込み、本物のリポジトリへの書き込み（I-10、I-12）。
- 各リポジトリの 0.3.0 の配布資産のPR、切り替えのPRの作成、今のCIの手順を外すコミット（I-10、I-12）。
- `canonical link`、`canonical sync` などのパッケージのコマンドの変更（R-435-11 のほか）。
- 利用者向けの使い方の文書（I-9）。

### 親契約として維持する境界
- 従来モード（版3）の処理、`.meta.json` を読み書きするコード、版3の振る舞いを確かめるテストを変えない（AC-15）。
- 契約 C1〜C11 を変えない。写した値はパッケージの定数と同じでなければならない。
- 利用者のツールの設定、`~/.local/state/spec-dock/`、利用者の定期の実行、本物の GitHub、利用者のほかのリポジトリに書かない。

## 失敗・境界条件
- `--project` が Git の mainのチェックアウトでない、`origin` がない、`origin/HEAD` がない（次の1手 `git remote set-head origin --auto`）：書く前に止まる（2）。
- `git subtree` がない、git が 2.38 より古い（`merge-tree --write-tree` が要る）：その操作の前に止まる（2）。
- `.meta.json` が読めない、必須のキーがない、`backend` が `github` でない、同じ ID や同じ番号が2つ：止める異常。`register --apply` と `build-canonical --apply` は書く前に止まる。
- GitHub の読み取りの失敗（つながらない、権限、レート制限で待ちが長すぎる）：書く前なら2、書いた後なら3で止まり、もう一度の実行を示す。
- 結果の分からない書き込み：今の状態を読み直して確かめ、分からなければ3で止まる。Issue の作成は、種類のラベルと slug の印と題名で探して、重複して作らない。
- `origin` の `spec-dock/canonical` や `cut`、`export-legacy` のブランチが、違う中身ですでにある：強制せずに止まる（2）。
- `move-local`：カタログに同じ名前があれば `.local-<PC名>`、それもあれば `-2`、`-3` を足す。シンボリックリンクはリンクのまま移す。
- `adopt-worktree`：分岐点の仕様のツリーと同じツリーの canonical のコミットが見つからない、ブランチでない（detached）、push が3回続けて先に進まれる：何も消さずに止まる。
- `export-legacy`：GitHub の Scope のディレクトリがカタログにない、カタログのディレクトリに GitHub の Scope がない、入れ子が GitHub の親子と違う：警告として示す。

## 受け入れ条件
Epic の `plan.md` の I-8 の「受け入れ」を、テストで確かめられる形にしたものである。テストは外のネットワークを使わない（GitHub は偽の `gh`、`origin` は一時ディレクトリの bare のリポジトリ、`XDG_STATE_HOME` と作業の記録の置き場は一時ディレクトリ）。

- **AC-435-01**：どのサブコマンドも、`--apply` なしでは、偽の `gh` への書き込み（GET と GraphQL のほか）がなく、対象のリポジトリの参照、作業ツリー、`.git/config`、`origin` の参照、作業の記録が変わらない。
- **AC-435-02**：既定のブランチが `develop` の一時のリポジトリで、`cut --apply` が `develop` から切り、`spec-dock-check.yml` の `branches` が `[develop]` で、ほかのバイトは見本と同じである。
- **AC-435-03**：Scope のない一時のリポジトリ（`spec-dock/initiatives/` が空のディレクトリだけ）で、`build-canonical --apply` が何もせずに0で終わり、`move-local --apply` が空のディレクトリを消す。
- **AC-435-04**：`origin` を一時の bare のリポジトリにした使い捨てのクローンで、`build-canonical --apply`、`cut --apply`、`export-legacy --apply` が bare のリポジトリにだけ push し、偽の `gh` に書き込みを送らない。対象のクローンの `.git` の参照が変わらない。
- **AC-435-05**：本物の5つのリポジトリで `plan` を読むだけで実行し（GitHub への書き込みなし、リポジトリの変化なし）、異常、CIの手順、作業用のworktreeの一覧を `report.md` に書く。
- **AC-435-06**：一時のリポジトリと偽の `gh` で、`register --apply` を途中で止めて（書き込みの失敗を注入）再実行すると、同じ書き込みを2回送らずに終わり、`verify` が一致を報告する。`undo --apply` で、登録の前の GitHub の状態（ラベル、本文、親子、依存、作った Issue は閉じてラベルなし、作ったラベルの定義なし）に戻り、もとからあったラベルは残る。`register` は対象のリポジトリのファイルを変えない。
- **AC-435-07**：注入した時計で、`register --apply` の書き込みの間が1秒以上あり、どの60秒にも80回、どの3600秒にも500回を超えない。403 と `retry-after` の応答では待って同じ書き込みを続ける。
- **AC-435-08**：`plan` が、`init-local-00002`（結び付いた Issue と同じ題名）と `init-local-00003`（違う題名で閉じた Issue）を異常として示し、前者を既にある番号の ID に、後者を新しい Issue に置き換える予定を示す。ローカルでない ID の番号の不一致と、題名の食い違いも一覧にする。`register --apply` の後、`idmap.json` にその置き換えがある。
- **AC-435-09**：`build-canonical` の結果のツリーが、形式1の管理ファイル（`.spec-dock-canonical.json`、`.gitignore`、`README.md` がパッケージのバイト列と同じ）を持ち、`.meta.json` を持たず、ほかのファイルが元の `spec-dock/initiatives` の追跡されたファイルと（`idmap.json` の名前の置き換えの後で）パスと中身まで一致する。もう一度の実行は何もしない。
- **AC-435-10**：`move-local --apply` が、無視された `.workbench` のファイルと追跡されていないファイルを、上書きせずにカタログへ移し（同じ名前は `.local-<PC名>` の名前）、カタログがなければ作り、その後の `spec-dock canonical link` が、そのカタログを「すでにある」と扱って成功する。
- **AC-435-11**：`adopt-worktree --apply` の後、コミットしていない変更とコミットした変更が canonical に入り、そのブランチを既定のブランチにマージしても仕様のパスが入らない（AC-05）。構造の違いの一覧が出る。canonical と同じパスを両方で変えたとき、canonical の版が元の名前に、ブランチの版が別名ファイルに残る。消す予定のファイルの一覧は `--apply` なしで出る。作業ツリーのファイルが canonical と一致しなければ、何も消さずに止まる。
- **AC-435-12**：`export-legacy --apply` で作ったブランチの `.meta.json` が、移行前のものと、`revision`、`lifecycle`、`idmap.json` による ID の置き換え、GitHub で変えた題名のほかは一致し（何も変わっていなければバイト列まで同じ）、宣言が移行前のバイト列に戻り、`spec-dock-check.yml` がない。GitHub の題名が日本語のときも、作ったツリーで、従来モードの `workspace validate` と `scope show` が通る（統括の判断 Q3）。
- **AC-435-13**：写した値（C1 の種類のラベルとその色と説明、印の読み方と書き方、ID の形、C3 の無視の3行とカタログとリンクとブランチと lock の理由、C5 の管理ファイルのバイト列、C6 の Git の設定、C7 の4つの定数と見本のバイト列と既定のブランチの名前の規則、版4の宣言のバイト列）が、パッケージの定数と資産と同じである。
- **AC-435-14**：版4の宣言で `writer_protocol` が `specdock.writer/v1` のとき、`canonical check` が調べること4の失敗の1件（`WORKSPACE_DECLARATION_INVALID`、パスと次の1手付き）を返し、終了コード7で終わる。
- **AC-435-16**：`plan` が、偽の `gh` と一時のリポジトリで、SpecDock を呼ぶCIの行、作業用のworktree（コミット済みと未コミットの仕様の変更、prunable）、mainのチェックアウトの追跡外と無視されたファイルの数、HEAD と `origin/<既定のブランチ>` の違いの警告を示す。
- **AC-435-17**：GitHub に違う種類のラベル、違う印、違う親があるとき、`register --apply` はそれを上書きせずに飛ばし、異常として示し、`verify` は不一致として1で終わる。
- **AC-435-18**：`origin/HEAD` がないとき、`origin` が GitHub なのに `--repo` が違うとき、`origin` が GitHub でないのに `--repo` がないとき、手元の `origin/<既定のブランチ>` が古いとき（書くサブコマンド）は、何も書かずに2で終わる。
- **AC-435-19**：`cut` が書く `spec-dock/workspace.json` が、配布資産の版4の宣言とバイト単位で同じ（`writer_protocol` は `specdock.worktree-writer/v1`）で、切った後のツリーで `spec-dock canonical check` が通る。`build.json` の元の仕様のツリーと今の仕様のツリーが違うと、`cut` は止まる。
- **AC-435-20**：`README.md` があり、準備、予行演習（本番の `idmap.json` を予行演習の作業の記録へ写すことを含む）、本番、戻し方、Scope のないリポジトリの扱いを書いている。
- **AC-435-15（AC-15）**：版3の振る舞いを確かめる今のテストが、変更なしで通る。`make lint`（`migrate.py` を含む）と `uv run pytest` が通る。

## 制約・前提
- Python 3.10 以上、macOS と Linux。`migrate.py` は標準ライブラリと `git`（2.38 以上、`git subtree` を含む）と `gh` だけを使う。
- 本物の GitHub への書き込みと本物のリポジトリへの書き込みは、この Issue では行わない（Epic の `plan.md` の I-8 の注意）。
- 予行演習と本番の実行は、I-10 と I-12 で、統括のエージェントが行う。
