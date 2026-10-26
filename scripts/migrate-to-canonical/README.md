# canonical への移行のスクリプト

宣言の版3（従来モード）のリポジトリを、仕様の構造を GitHub Issue に、内容を `spec-dock/canonical` ブランチに置く形（宣言の版4、canonical モード）へ、一度だけ移すための使い捨ての道具です。対象は利用者の5つのリポジトリ（spec-dock、taikyohiyou_project、housing-lifecycle、input-devices、company-os）だけです。SpecDock の撤去（0.4.0）で消しますが、版のタグ `v0.3.0` に残ります。

- 設計の正本：Epic `epic-00424` の `design.md` の11章、「移行・互換性・rollback」と、Issue `iss-00435` の `design.md`。
- 使うもの：Python 3.10 以上、git 2.38 以上（`git subtree` を含む。`adopt-worktree` は 2.40 以上）、`gh`（ログイン済み）。SpecDock のパッケージは読み込みません。

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
| `plan` | `.meta.json` と GitHub を読み、登録の予定、データの異常、ローカルの Scope の置き換え、SpecDock を呼ぶ今のCIの行、作業用のworktreeの仕様の変更、mainのチェックアウトの追跡外と無視されたファイルの数を示す |
| `register` | 種類のラベル、本文の slug の印、sub-issue、blocked by を、足すだけで登録する。題名と状態は変えない。違うものがあれば上書きせずに異常として示す |
| `verify` | `.meta.json` の構造と GitHub の構造を比べる（切り替えの後は、切り替え前のコミットと比べる） |
| `undo` | `register` が足したものだけを外す（作った Issue は `not_planned` で閉じてラベルを外す） |
| `build-canonical` | 使い捨てのクローンで `git subtree split` を行い、管理ファイルを足し、`.meta.json` を消して、`origin` の `spec-dock/canonical` に push する |
| `cut` | 既定のブランチから仕様を外し、宣言を版4にし、`.github/workflows/spec-dock-check.yml` を足したブランチ `spec-dock/migrate-to-canonical` を push する |
| `move-local <チェックアウト>` | `spec-dock/initiatives/` の追跡外と無視されたファイルを、カタログへ移す（カタログがなければ作る。同じ名前は `.local-<PC名>` を付ける） |
| `adopt-worktree <チェックアウト>` | 移行前のブランチの仕様（未コミットを含む）を canonical に取り込み、そのブランチから仕様のツリーを外すコミットを作る |
| `export-legacy` | 戻すときに、canonical の内容と GitHub から作った `.meta.json` と版3の宣言を持つブランチ `spec-dock/export-legacy` を push する |

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
5. `python3 $M export-legacy $R --apply` で戻し、ブランチ `spec-dock/export-legacy` の `.meta.json` が、移行前のものと `revision`、`lifecycle`、ID の置き換え、GitHub で変えた題名のほかは一致することを確かめる。
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
- **マージの後、撤去の前**：`python3 $M export-legacy --project <main> --apply` でブランチ `spec-dock/export-legacy` を作り、切り替えのPRで外した今のCIの手順を戻すコミットを足して、PRで戻す。マージの後、各チェックアウトで `spec-dock canonical remove --yes` を行い、必要なら `undo --apply`。SpecDock は 0.3.0 のままでよく、ほかのリポジトリには影響しません。
- **撤去（0.4.0）の後**：利用者の環境に 0.3.0 を入れ直し、版のタグ `v0.3.0` のこのスクリプトで、上と同じ手順で戻す。
- 戻すかどうかは利用者が判断します。
