# canonical への移行のスクリプト

宣言の版3（従来モード）のリポジトリを、仕様の構造を GitHub Issue に、内容を `spec-dock/canonical` ブランチに置く形（宣言の版4、canonical モード）へ、一度だけ移すための使い捨ての道具です。対象は利用者の5つのリポジトリ（spec-dock、taikyohiyou_project、housing-lifecycle、input-devices、company-os）だけです。SpecDock の撤去（0.4.0）で消しますが、版のタグ `v0.3.0` に残ります。

- 設計の正本：Epic `epic-00424` の `design.md` の11章、「移行・互換性・rollback」と、Issue `iss-00435`（I-8）と `iss-00456`（I-15、平らにする写し）の `design.md`。
- 使うもの：Python 3.10 以上、git 2.31 以上と `git subtree`（`adopt-worktree` は 2.40 以上。2026-10-29 に、git 2.34.1（Ubuntu 22.04）、2.39.5（Debian 12）、2.43.0（Ubuntu 24.04）、2.54.0（macOS）で `build-canonical`、`cut`、`move-local` を確かめ、`adopt-worktree` は 2.43.0 と 2.54.0 で確かめた。2.40 より古いと案内付きで止まる。どの版でも、スクリプトは始めに版を確かめ、2.31 より古ければ何もせずに止まる。Debian と Ubuntu の `git` の包みは `git subtree` を含む。SpecDock 本体の `canonical link` などは git 2.38 以上が要る）、`gh`（利用者自身のアカウントでログイン済み。作った Issue の見つけ直しで作成者の名前を比べるので、GitHub App のトークンでは使わない）。SpecDock のパッケージは読み込みません。

## 共通の決まり

```sh
M=scripts/migrate-to-canonical/migrate.py     # spec-dock のリポジトリの中のこのファイル
python3 $M <サブコマンド> --project <対象の mainのチェックアウト> [--json] [--apply]
```

- `--apply` を付けないと、予定を表示するだけで、リポジトリ、`.git`、GitHub、作業の記録に何も書きません。何度実行しても同じ結果になります。
- 既定のブランチは `origin/HEAD` から求めます（taikyohiyou_project は `develop`）。ないときは `git -C <project> remote set-head origin --auto`。
- スクリプトは `fetch` しません。書く前に、手元の `origin/<既定のブランチ>` が GitHub と同じか確かめ、違えば止まります（`git -C <project> fetch origin` をしてから、もう一度）。
- 作業の記録は `scripts/migrate-to-canonical/.state/<owner>-<repo>/`（Git では無視）に置きます。`--state-dir` で置き場を変えられます。`undo.jsonl`（GitHub に足したものの一覧）、`idmap.json`（ローカルの ID の置き換え）、`build.json`（canonical を作った記録）、`adopt/`（取り込んだブランチの構造の違い）です。消すと `undo` ができなくなるので、移行が終わるまで消さないでください。
- 終了コード：0 問題なし、1 読むだけで問題を見つけた（`plan` の止める異常、`verify` の不一致）、2 書く前に止まった（引数の誤りも2）、3 書いた後に止まった（同じコマンドをもう一度実行すると続きから進みます）。

| サブコマンド | すること |
|---|---|
| `plan` | `.meta.json` と GitHub を読み、登録の予定、データの異常、ローカルの Scope の置き換え、平らにする写しの結果（平らにできないもの、書き換えるリンクと書き換えられないリンク）、SpecDock を呼ぶ今のCIの行、作業用のworktreeの仕様の変更、mainのチェックアウトの追跡外と無視されたファイルの数を示す。対象のリポジトリには何も書かない |
| `register` | 種類のラベル、sub-issue、blocked by を、足すだけで登録する。Issue の本文、題名、状態は変えない。違うものがあれば上書きせずに異常として示す |
| `verify` | `.meta.json` の構造と GitHub の構造を比べる（切り替えの後は、切り替え前のコミットと比べる）。origin の canonical があれば、`.meta.json` がないことと、Scope のディレクトリがすべて `<区切り>/<ID>/` にあることも確かめる |
| `undo` | `register` が足したものだけを外す（作った Issue は `not_planned` で閉じてラベルを外す） |
| `build-canonical` | 使い捨てのクローンで `git subtree split` を行い、各コミットに平らにする写しを当てて履歴を作り直し、管理ファイルを足して、`origin` の `spec-dock/canonical` に push する |
| `cut` | 既定のブランチから仕様を外し、宣言を版4にし、`.github/workflows/spec-dock-check.yml` を足したブランチ `spec-dock/migrate-to-canonical` を push する |
| `move-local <チェックアウト>` | `spec-dock/initiatives/` の追跡外と無視されたファイルを、平らにした位置でカタログへ移し、リンクを書き換える（カタログがなければ作る。同じ名前は `.local-<PC名>` を付ける） |
| `adopt-worktree <チェックアウト>` | 移行前のブランチの仕様（未コミットを含む）を平らにして canonical に取り込み、そのブランチから仕様のツリーを外すコミットを作る |
| `export-legacy` | 戻すときに、canonical の `<区切り>/<ID>/` を GitHub の親子で入れ子に戻し、リンクを戻し、GitHub から作った `.meta.json` と版3の宣言を持つブランチ `spec-dock/export-legacy` を push する |

## 平らにする写し

canonical では、Scope のディレクトリは `spec-dock/initiatives/<区切り>/<ID>/` に平らに並びます。区切りは番号の1,000ごとの範囲で、桁は ID の番号と同じ幅です（`00000-00999/iss-00454/`、`02000-02999/iss-02114/`、`100000-100999/iss-100454/`）。

- Scope のディレクトリは置き場で決めます：`spec-dock/initiatives/` の直下と、Scope の `epics/`・`issues/` のすぐ下にある、`.meta.json` を持つディレクトリです。ID は `.meta.json` の `type`、`id`、`github.issue_number`（ローカルの ID は `idmap.json`）から決めます。
- 各ファイルは、最も深い Scope からの残りのパスで `<区切り>/<ID>/<残り>` に移ります。`.meta.json`、`epics/rules.md`、`issues/rules.md` は持ち込みません。
- 平らにできないもの（`plan` の `FLATTEN_*` の異常）：`epics/`・`issues/` の直下の `rules.md` でも子の Scope でもないもの（仮置きのディレクトリなど）、どの Scope にも入らないファイル、ID を決められない Scope、同じ ID の2つのディレクトリ。従来の SpecDock のコマンドで直して（ファイルを Scope の中へ移す、要らないものを消す）マージしてから、もう一度 `plan` します。`build-canonical` は、既定のブランチの今のツリーにこれがあると止まります。
- 相対のリンク（シンボリックリンク、Markdown の `[…](…)` と `[…]: …`、HTML の `href` と `src`）は、新しい位置から同じ先を開くように書き換えます。Markdown のコードの中は変えません。捨てる `rules.md` へのリンクはその先の `spec-dock/docs/rules/…` に、なくなる `epics/`・`issues/` へのリンクは親の Scope のディレクトリに向けます。
- `plan` と `build-canonical` の `data.flatten.links` の見方：`rewritten` は書き換えるリンクの数、`unrewritable` は移行の前は開けたのに後で開けなくなるリンク（書き換えずに残します。直すか、切れることを受け入れるかを決めます）、`broken_before` は移行の前から切れているリンク（数えません）です。
- 登録の前の `plan` では、新しく Issue を作る予定のローカルの Scope は仮の場所 `pending/<ローカルの ID>` に写して数えます（`data.flatten.pending`）。
- `build-canonical` の履歴：古いコミットの平らにできないもの（`idmap.json` にない古いローカルの ID、仮置きのディレクトリなど）は、そのコミットからだけ落とします。`data.history` に、作り直したコミットの数、落としたコミットの数、落としたパスの数（異常のコードごと）と例が出ます。落としたものは、既定のブランチの履歴に残ります。

## 準備（今の運用は止めない）

1. 対象のリポジトリで `spec-dock installation update` を行い、配布資産を 0.3.0 に上げる。同じPRで、今のCIが入れる SpecDock の固定の版をタグ `v0.3.0` に上げる（spec-dock は不要）。PRの検査が通ってから、人がマージする。
2. `python3 $M plan --project <main>` を実行する。止める異常（`[blocking]`）は、従来の SpecDock のコマンドで直してマージし、もう一度 `plan` する。`TITLE_MISMATCH`（GitHub の題名を正とする）、`LOCAL_SCOPE`（置き換えの予定）、`CLOSED_PARENT_OPEN_CHILD` は、扱いを決めて報告書に書く。
3. `python3 $M register --project <main> --apply`、続けて `python3 $M verify --project <main>`。途中で止まったら、同じ `register --apply` をもう一度実行する。

## 予行演習（各リポジトリの切り替えの前に必ず行う）

本物のリポジトリ、GitHub への書き込み、利用者の定期の実行と状態の置き場には触れません。

```sh
T=$(mktemp -d /private/tmp/specdock-rehearsal.XXXXXX)     # 内蔵のディスクの一時ディレクトリ
D=<既定のブランチ>                                         # main か develop
git clone --bare --no-local <main> $T/origin.git
git -C $T/origin.git fetch <main> "+refs/remotes/origin/$D:refs/heads/$D"
git -C $T/origin.git symbolic-ref HEAD refs/heads/$D
git clone $T/origin.git $T/work
export XDG_STATE_HOME=$T/state
mkdir -p $T/records/<owner>-<repo>
cp scripts/migrate-to-canonical/.state/<owner>-<repo>/idmap.json $T/records/<owner>-<repo>/   # 本番の register の結果
R="--project $T/work --repo <owner>/<repo> --state-dir $T/records"
```

1. `python3 $M plan $R` と `python3 $M verify $R`（本物の GitHub を読むだけ。`register` は本物で済ませてある）。
2. `python3 $M build-canonical $R --apply` と `python3 $M cut $R --apply`（bare のリポジトリにだけ push される）。
3. 切り替えのブランチを、使い捨てのクローンの既定のブランチに取り込む（PRのマージの代わり）：`git -C $T/work merge --ff-only origin/spec-dock/migrate-to-canonical && git -C $T/work push origin HEAD:$D && git -C $T/work fetch origin`。
4. `python3 $M move-local $R $T/work --apply`、`spec-dock --project $T/work canonical link --no-schedule`、`spec-dock --project $T/work canonical sync --state-root $T/state/spec-dock` を実行し、仕様が読み書きでき、`spec-dock --project $T/work canonical check` が通ることを確かめる。
5. `python3 $M export-legacy $R --apply` で戻し、ブランチ `spec-dock/export-legacy` の `.meta.json` が、移行前のものと `revision`、`lifecycle`、ID の置き換え、GitHub で変えた題名のほかは一致すること、従来モードの `spec-dock workspace validate` が通ること、`data.links.unrewritable` が空であることを確かめる。
6. 結果を Issue の報告書に書き、`rm -rf $T` で消す。

## 本番（1つのリポジトリについて）

1. **凍結**：終わるまで、ほかのエージェントでそのリポジトリの仕様を編集しない。`plan` をもう一度実行し、`register --apply` と `verify` をもう一度行う。
2. `build-canonical --apply`、`cut --apply`。切り替えのブランチに、`cut` が示した今のCIの SpecDock の手順（SpecDock を入れるだけの手順を含む）を外すコミットを足し、PRを作る。PRの検査（既存のCIと `SpecDock check`）が通ったことを確かめ、人がマージする。
3. mainのチェックアウトで既定のブランチを取り込み（`git pull`）、`python3 $M move-local --project <main> <main> --apply`、`spec-dock canonical link` を実行し、`canonical link` が示すツールの1行を足す。
4. 各作業用のworktreeで、`python3 $M adopt-worktree --project <main> <worktree> --apply`、`python3 $M move-local --project <main> <worktree> --apply`、既定のブランチの取り込み（`git merge origin/<既定のブランチ>`）、`spec-dock canonical link` の順に行う。仕様の変更のないworktreeでも同じ手順でよい（`adopt-worktree` は仕様のツリーを外すコミットだけを作る）。
5. `verify` をもう一度実行し、凍結を解く。

### `adopt-worktree` が止まったとき

- 「files differ from canonical」：canonical にはすでに取り込んであります。両方で同じファイルを変えたときは、canonical の版が元の名前に、ブランチの版が `*.conflict-<PC名>-<時刻>` のファイルに残っています。カタログ（`<main>/spec-dock/.canonical`）で中身を確かめてから、そのworktreeで `git rm -r -q --cached spec-dock/initiatives && git commit -m "spec-dock: move specs to the canonical branch"` を行い、`spec-dock/initiatives` の追跡外のファイルのうち、カタログにあるものを消してください（無視されたファイルは `move-local` で移します）。
- 「the commit removing … failed」：フックや署名の設定を直して、もう一度 `adopt-worktree --apply` を実行してください。
- 構造の違い（親、依存、題名の変更、増えた Scope）は自動では登録しません。`adopt/<ブランチ>.json` を見て、SpecDock のコマンドで登録し直してください。

## Scope のないリポジトリ（company-os）

`spec-dock/initiatives/` に追跡されたファイルがないので、`register` は種類のラベルだけを作り、`build-canonical` は何もしません。`cut` は canonical がなくても切ります。切り替えのPRのマージの後、`move-local` が空のディレクトリを消し、`spec-dock canonical link` が、GitHub に canonical のない新しいリポジトリとして最初の canonical を作ります。

## 戻し方

- **切り替えのPRのマージ前**：PRを閉じ、GitHub の `spec-dock/canonical` と `spec-dock/migrate-to-canonical` を消し、必要なら `python3 $M undo --project <main> --apply` で登録を外す。
- **マージの後、撤去の前**：`python3 $M export-legacy --project <main> --apply` でブランチ `spec-dock/export-legacy` を作り（下の「入れ子への戻し方」）、切り替えのPRで外した今のCIの手順を戻すコミットを足して、PRで戻す。マージの後、各チェックアウトで `spec-dock canonical remove --yes` を行い、必要なら `undo --apply`。SpecDock は 0.3.0 のままでよく、ほかのリポジトリには影響しません。
- **撤去（0.4.0）の後**：利用者の環境に 0.3.0 を入れ直し、版のタグ `v0.3.0` のこのスクリプトで、上と同じ手順で戻す。
- 戻すかどうかは利用者が判断します。

### 入れ子への戻し方（`export-legacy`）

- 入れ子のパスは GitHub の親子で作ります：Initiative は `<ID>-<slug>/`、Epic は `<親>/epics/<ID>-<slug>/`、Issue は `<親>/issues/<ID>-<slug>/`。slug は切り替え前の `.meta.json` の値です。切り替えの後に作った Scope は、題名が英数字と1つの空白だけ（`Add Refresh Token`）なら題名から（`add-refresh-token`）、ほかは `untitled` です。各 Initiative に `epics/rules.md`、各 Epic に `issues/rules.md` を置き直します。
- 次のものがあると、`--apply` がなくても、何も書かずに終了コード2で止まり、異常の一覧を示します。GitHub かカタログで直してから、もう一度実行します：親のない Epic と Issue（`PARENT_MISSING`）、親の種類が規則に合わない Scope（`KIND_RULE`）、外のリポジトリの親（`PARENT_CONFLICT`）、種類のラベルが2つ以上の Issue（`KIND_LABEL_MULTIPLE`）、`<区切り>/<ID>/` のない Scope（`SCOPE_DIRECTORY_MISSING`）、Issue のない `<ID>/`（`SCOPE_ISSUE_MISSING`）、種類の付け替え（`SCOPE_KIND_CHANGED`）、区切りの外れや `<ID>/` の下の `epics/`・`issues/`（`SCOPE_DIRECTORY_MISPLACED`）、`<区切り>/<ID>/` の外のファイル（`CATALOG_PATH_OUTSIDE_SCOPE`）。
- リンクは平らにする写しの逆に戻ります。字面が元に戻らないのは、正規化していない元の文字列（`./a/../b` など）、捨てた `rules.md` へのリンク（`spec-dock/docs/rules/…` を指したまま）、`epics/`・`issues/` のディレクトリへのリンク（親の Scope のディレクトリを指したまま）の3種類だけで、どれも同じ先を開きます。
