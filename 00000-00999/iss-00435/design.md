---
種別: 設計書（Issue）
ID: "iss-00435"
タイトル: "Add Throwaway Canonical Migration Script"
関連GitHub: ["#435"]
状態: "draft"
最終更新: "2026-10-26"
依存: ["requirement.md"]
親: ["epic-00424", "init-00423"]
---

# iss-00435 Add Throwaway Canonical Migration Script — 設計

詳細: [Design Guide](../../../docs/authoring/design.md)

この設計書は、Epic の `design.md` の11章を、実装できる粒度にしたものである。Epic の設計を言い換えず、ファイルの構成、データの形、各サブコマンドの手順、失敗の扱いを決める。Epic にない判断は、統括の判断（`plan.md`）による。

## 設計目標
- **一度だけ使い、戻せる**：既定では何も書かず（予定の表示）、`--apply` でだけ書く。何度実行しても同じ結果になり、止まっても続きから進み、`undo` と `export-legacy` で戻せる（R-G2）。
- **本物を汚さない**：canonical の作成、切り離し、戻しのブランチは、使い捨てのクローンで作って `origin` に push する。対象のリポジトリの `.git` には、`move-local` のカタログの作成と `adopt-worktree` の外すコミットのほか、何も書かない。
- **止まって示す**：異常、食い違い、結果の分からない書き込みでは、推測で直さずに止まり、次の1手を示す（約束5）。
- **GitHub に負荷をかけない**：読み取りは GraphQL の一括、書き込みは1つずつ、1秒以上の間、1分80回、1時間500回まで（Epic の `design.md` 11章「速さ」）。
- **パッケージから独立**：`spec_dock` を読み込まない。写した値は、テストでパッケージの定数と比べる。

## Current / Target
- Current：移行の道具はない。`canonical link` は、GitHub に canonical がなく既定のブランチに `spec-dock/initiatives` があると `CANONICAL_NOT_MIGRATED` で止まり、`scripts/migrate-to-canonical/README.md` を示す（I-2）。`canonical check` は、版4の宣言の `writer_protocol` に古い `specdock.writer/v1` も通す（I-7）。
- Target：

```text
scripts/migrate-to-canonical/
  migrate.py        1つのファイル。標準ライブラリ、git、gh だけを使う
  README.md         準備、予行演習、本番、戻し方、Scope のないリポジトリ
  .gitignore        /.state/
  .state/<owner>-<repo>/   （Git で無視）
    idmap.json  undo.jsonl  build.json
```

- `canonical check` の調べること4は、`writer_protocol` が `specdock.worktree-writer/v1` であることを求める。

## 責務・Interface

### コマンドの形
```text
python3 scripts/migrate-to-canonical/migrate.py <サブコマンド> --project <mainのチェックアウト>
    [--repo OWNER/NAME] [--state-dir DIR] [--apply] [--json] [サブコマンドの引数]

plan | verify                       （--apply を受け付けない）
register | undo | build-canonical
cut [--branch spec-dock/migrate-to-canonical]
export-legacy [--branch spec-dock/export-legacy]
move-local <チェックアウト> [--pc-name NAME]
adopt-worktree <チェックアウト> [--pc-name NAME]
```

- `--project` は、Git の mainのチェックアウト（`git rev-parse --git-common-dir` の親）でなければならない。`move-local` と `adopt-worktree` の `<チェックアウト>` は、同じクローンのチェックアウト（mainを含む）でなければならない。
- `--pc-name` は、別名ファイルの PC名を明示する（テストと、ホスト名が使えない環境のため）。既定はホスト名から、Epic の `design.md` 5章「別名ファイルの名前」の規則で作る。
- 出力：文字では、行ったこと（または予定）、異常、次の1手を示す。`--json` では `{"command", "apply", "status", "exit_code", "repository", "default_branch", "data", "anomalies", "warnings", "next_steps"}` の1つの JSON を出す。`status` は `ok`、`problems`、`refused`、`stopped`。
- 終了コード：0 `ok`、1 `problems`（読むだけで止める異常か不一致を見つけた）、2 `refused`（書く前に止まった）、3 `stopped`（書いた後に止まった。もう一度の実行で続きから進む）。使い方の誤りも argparse の2で、どちらも何も書いていない。
- **古い `origin/D` の確かめ**：スクリプトは `fetch` しない（対象の `.git` を書くため）。書くサブコマンド（`register`、`build-canonical`、`cut`、`export-legacy`）は、`git ls-remote origin refs/heads/D` の先頭が手元の `origin/D` と違えば、書く前に止まる（次の1手 `git -C <project> fetch origin`）。`plan` と `verify` は警告する。

### 対象の解決（全サブコマンド）
1. `git -C <project> rev-parse --path-format=absolute --git-common-dir` の名前が `.git` で、その親が `--project` の実体と同じこと（Epic の `design.md` 3章「場所の決め方」と同じ判定）。
2. 既定のブランチ D：`git symbolic-ref --quiet refs/remotes/origin/HEAD` の `refs/remotes/origin/` より後ろ。ないときは止まり、次の1手 `git -C <project> remote set-head origin --auto` を示す。
3. GitHub の owner と repo：`git remote get-url origin` が `https://github.com/O/R(.git)`、`git@github.com:O/R(.git)`、`ssh://git@github.com/O/R(.git)` のどれかなら、そこから求める。`--repo` があれば、大文字と小文字を区別せずに同じでなければ止まる。`origin` が GitHub でなければ `--repo` を要する（予行演習）。
4. 作業の記録の置き場：`(--state-dir または <スクリプトの場所>/.state)/<owner>-<repo>`（小文字）。読むだけのサブコマンドは作らない。
5. 読むだけの Git の呼び出しには `--no-optional-locks` を付ける（`git status` がインデックスを書き換えないため）。

### 移行元の `.meta.json`（統括の判断 Q5）
- 読み取り元は、既定では `origin/D` のコミット S である（作業ツリーではない）。S の `spec-dock/initiatives` がないとき（切り離しの後）は、「切り離し前のコミット」を使う：`build.json` の `source_commit`、なければ `git log --first-parent -1 --format=%H origin/D -- spec-dock/initiatives` のコミットの第1の親。
- `git ls-tree -r -z S -- spec-dock/initiatives` で、名前が `.meta.json` のファイルを読み、Scope の一覧を作る。ディレクトリの相対パス、`type`、`id`、`title`、`slug`、`parent_id`、`depends_on`、`github.issue_number`、`github.repo_owner`、`github.repo_name` を使う。
- 必須のキー（Epic の `design.md` Current の13個）がない、JSON でない、`type` が3つのどれでもないものは、`META_INVALID`（止める異常）。

### ID の扱い
- ID の形は `^(init|epic|iss)-([0-9]+)$`（GitHub の番号）か、`^(init|epic|iss)-local-([0-9]+)$`（ローカル）。新しい ID は `<接頭辞>-<5桁にそろえた番号>`（C1 の `scope_id`、`domain/ids.py` の `format_id`）。
- ローカルの ID（統括の判断と Epic 11章「ローカルの Scope と番号の不一致」）：
  - `github.issue_number` があり、その Issue の題名が `.meta.json` の題名と同じなら、その番号の ID に置き換える（`how: "existing"`）。
  - 題名が違うか、番号がないか、その Issue がないなら、`register` が `.meta.json` の題名で新しい Issue を作り、その番号の ID に置き換える（`how: "created"`）。
  - `plan` はどちらにするかを示し、`register --apply` が `idmap.json` に書く。名前の置き換えは、`build-canonical`、`move-local`、`adopt-worktree` だけが、パスの各部分の `<古い ID>-` を `<新しい ID>-` にして行う。
- GitHub の番号の ID で、番号が `github.issue_number` と違うものは `ID_NUMBER_MISMATCH`（止める異常）。

### データの異常
| コード | 意味 | 止めるか |
|---|---|---|
| `META_INVALID` | `.meta.json` が読めない、キーが足りない、`backend` が `github` でない | 止める |
| `DUPLICATE_ID` / `DUPLICATE_NUMBER` | 同じ ID、同じ Issue の番号が2つ以上 | 止める |
| `ID_NUMBER_MISMATCH` | GitHub の番号の ID と `issue_number` が違う | 止める（統括の判断 Q4） |
| `ISSUE_MISSING` | 結び付いた Issue がない、PRである（ローカルの Scope を除く） | 止める |
| `KIND_RULE` | Initiative に親がある、Epic の親が Initiative でない、Issue の親が Epic でない | 止める |
| `PARENT_MISSING` / `DEPENDENCY_MISSING` | 親や依存先の ID が、どの Scope でもない | 止める |
| `DEPENDENCY_CYCLE` | 依存が循環する | 止める |
| `LOCAL_SCOPE` | ローカルの ID（置き換えの予定を添える） | 止めない |
| `TITLE_MISMATCH` | `.meta.json` と GitHub の題名が違う（GitHub を正とする） | 止めない |
| `CLOSED_PARENT_OPEN_CHILD` | GitHub で親が閉じ、子が開いている | 止めない |
| `KIND_LABEL_CONFLICT` / `SLUG_MARKER_CONFLICT` / `PARENT_CONFLICT` | GitHub に違う種類のラベル、違う印（複数や規則外を含む）、違う親がある | 止めない。`register` はその項目を飛ばし、`verify` は不一致にする（Q4） |
| `GITHUB_SCOPE_UNKNOWN` | 種類のラベルを持つ Issue に、対応する `.meta.json` がない | 止めない。`verify` は不一致にする |

- 「止める」異常があると、`plan` は1で終わり、`register --apply` と `build-canonical --apply` は書く前に2で止まる。直し方（従来の CLI で直す）を次の1手に書く。

### GitHub の読み書き（`gh` の部品）
- 呼び出しは、パッケージの I-1 と同じ形 `gh api --hostname github.com --include --method M <endpoint> [-H …] [--input -]` で、本文は標準入力の JSON。GraphQL は `POST graphql` に `{"query", "variables"}` を送る。状態コードは、終了コードではなく、出力の状態行で判定する。
- 読み取り：
  - **番号で読む**：`.meta.json` の番号（と `idmap.json` の番号）を50個ずつ、別名付きの `issue(number: N)` の GraphQL で読む（`number databaseId title body state stateReason labels(first:20){totalCount nodes{name}} parent{number repository{nameWithOwner}} blockedBy(first:100){totalCount nodes{number state title repository{nameWithOwner}}}`）。PRや存在しない番号は `null` かエラーで、`ISSUE_MISSING` にする。`labels.totalCount` が20を、`blockedBy.totalCount` が100を超える Issue だけ、REST の一覧で読み直す。
  - **種類のラベルで読む**：Epic の `design.md` 2章の問い合わせ（3つのラベルの OR、ページ送り）で、種類のラベルを持つ Issue をすべて読む（`GITHUB_SCOPE_UNKNOWN`、作った Issue の再発見、`export-legacy`）。
  - 読み取りの失敗：403 か 429 のレート制限（`retry-after`、`x-ratelimit-remaining: 0`、本文の rate limit）は、待ち（`retry-after`、なければ `x-ratelimit-reset` まで）が60秒以下なら待って3回まで再試行する。500番台は1、2、4秒の間で3回まで。ほかの失敗は止まる。
- 書き込み（`register`、`undo`）：
  - **速さ**：書き込みの前に、前の書き込みから1秒以上、直近60秒の書き込みが80回未満、直近3600秒が500回未満になるまで待つ。時計（`monotonic`、`now`、`sleep`）は注入できる。
  - **レート制限**：書き込みでも、スクリプトは待って同じ書き込みを続けてよい（Epic 11章）。待ちが3600秒を超えるか、5回続けば止まる（3）。
  - **結果の分からない書き込み**（500番台、時間切れ、接続の失敗）：対象を読み直し、効いていれば成功として記録する。効いていなければ止まる（3）。
  - 422 は、ラベルの作成の「すでにある」と、依存の「すでにある」を、読み直して確かめてから成功として扱う。ほかは止まる。
- 呼び出しは並べない。

### `register` の手順
1. 対象を解決し、`.meta.json` と GitHub を読み、異常を求める。止める異常があれば2で止まる。
2. 予定を作る（順は、ラベルの定義、ローカルの Scope の Issue の作成、Issue ごとの種類のラベル、本文の印、親子、依存。Issue は番号の昇順）。GitHub にすでにあるものは予定に入れない。違うものがある項目は飛ばし、異常にする。
   - ラベルの定義：`GET /repos/{o}/{r}/labels/{name}` が404の種類のラベルだけ `POST /repos/{o}/{r}/labels`（C1 の色と説明）。
   - Issue の作成：`POST /repos/{o}/{r}/issues`（`title` は `.meta.json` の題名、`body` は印の1行、`labels` は種類のラベル）。作る前に、種類のラベルで読んだ一覧に、同じ種類のラベル、同じ印、同じ題名で、ほかの Scope に結び付いていない Issue があれば、それを使う（前の実行で作ったが記録できなかったもの）。
   - 種類のラベル：`POST …/issues/{n}/labels`（`{"labels": [<種類のラベル>]}`）。
   - 本文の印：印がなければ、`PATCH …/issues/{n}`（`body` は C1 の `append_slug_marker` と同じ規則で末尾に足したもの）。
   - 親子：GitHub に親がなければ `POST …/issues/{親}/sub_issues`（`{"sub_issue_id": <子の databaseId>, "replace_parent": false}`）。
   - 依存：GitHub にない依存先ごとに `POST …/issues/{n}/dependencies/blocked_by`（`{"issue_id": <依存先の databaseId>}`）。GitHub にだけある依存は外さない（`verify` が示す）。
3. `--apply` なら、予定を順に送る。各書き込みの前に `undo.jsonl` に意図（`phase: "intent"`）を、成功の後に結果（`phase: "done"`）を足す。ローカルの Scope の置き換えは、決まった時点で `idmap.json` に書く（作成のときは、作った番号が分かった後）。
4. 途中で止まったら3で終わる。もう一度の実行は1から行い、GitHub の今の状態から予定を作り直すので、済んだものを送らない。

### `undo` の手順
- `undo.jsonl` の、`register` の書き込み（意図か結果）を新しいものから順に見て、GitHub の今の状態にまだあるものだけを外す。外したら `phase: "undone"` を足す。
  - 依存：`DELETE …/issues/{n}/dependencies/blocked_by/{依存先の databaseId}`。親子：`DELETE …/issues/{親}/sub_issue`（`{"sub_issue_id"}`）。
  - 本文の印：今の本文が、足した後の本文と同じなら、足す前の本文に戻す。違えば、印の行（と、足すときに入れた直前の空行）だけを除いた本文にする。
  - 種類のラベル：`DELETE …/issues/{n}/labels/{name}`。
  - 作った Issue：`PATCH …/issues/{n}`（`state: closed`、`state_reason: not_planned`）と、種類のラベルを外す。`idmap.json` から、その `created` の項目を消す。意図だけで結果の記録がない作成は、`register` と同じ探し方（種類のラベル、印、題名）で Issue を探し、見つかればそれを外す。
  - 作ったラベルの定義：`DELETE /repos/{o}/{r}/labels/{name}`（`undo.jsonl` に作ったと記録したものだけ。Q7）。
- `--apply` なしでは、外す予定を示す。書き込みの速さは `register` と同じ。

### `verify` の手順
- `.meta.json`（「移行元」の規則）を `idmap.json` で置き換えた後の各 Scope について、Issue があり、種類のラベルがちょうど1つで `type` と同じ、印がちょうど1つで `slug` と同じ、GitHub の親が `parent_id` の番号と同じ、GitHub の blocked by のうち Scope であるものの集合が `depends_on` の番号の集合と同じかを比べる。種類のラベルを持つが `.meta.json` にない Issue も不一致にする。
- 題名の食い違いは警告にする。Scope でない Issue への blocked by は、情報として示す。
- canonical に `.meta.json` がないこと（AC-04）：`refs/remotes/origin/spec-dock/canonical` かmainのチェックアウトのカタログ `spec-dock/.canonical` があれば、その中に `.meta.json` がないことを確かめる。どちらもなければ「未確認」と示す（`fetch` は対象の `.git` を書くので行わない）。
- 一致すれば0、不一致があれば1。

### `build-canonical` の手順
1. 対象を解決し、S を求める。S の `spec-dock/initiatives` の下に追跡されたファイルが1つもなければ、何もせずに0で終わる（Scope のないリポジトリ。次の1手は「`move-local` の後の `canonical link` が最初の canonical を作る」）。
2. 止める異常（`.meta.json` だけで分かるもの）があれば止まる。ローカルの ID が `idmap.json` になければ止まる（次の1手 `register --apply`）。`git subtree` がなければ止まる。
3. `git ls-remote --exit-code origin refs/heads/spec-dock/canonical` で、GitHub の canonical を確かめる。
4. 使い捨てのクローン（`tempfile` の一時ディレクトリ）：`git clone --quiet --no-hardlinks --no-checkout --origin source <project> <tmp>` の後、`git fetch source +refs/remotes/origin/D:refs/heads/migrate-source` で S を取る。`git subtree split --prefix=spec-dock/initiatives migrate-source` の結果を P とする。
5. P のツリーから、名前が `.meta.json` のファイルを除き、パスに名前の置き換えを当て、C5 の3つの管理ファイルを足したツリー T を、一時のインデックスで作る。T を確かめる（管理ファイルのほかが、S の `spec-dock/initiatives` の `.meta.json` 以外のファイルと、置き換えの後のパス、モード、オブジェクトで一致する）。
6. コミット K（親は P、メッセージ `spec-dock: migrate to canonical`）。作者と日時は、同じ入力から同じ K になるよう、日時を S のコミットの日時に固定する（名前とメールは対象のリポジトリの設定）。
7. `--apply` なしなら、予定（S、ファイルの数、名前の置き換え、GitHub の canonical の有無）を示して終わる。`--apply` なら、GitHub の canonical がないとき `git -C <tmp> push <origin の URL> K:refs/heads/spec-dock/canonical`（強制しない）。すでに K なら何もしない。違うなら止まる（2）。
8. `build.json` に `{"version": 1, "source_commit": S, "split_commit": P, "canonical_commit": K}` を書く。一時ディレクトリを消す。

### `cut` の手順
1. S を求める。S に 0.3.0 の配布資産がないとき（`spec-dock/system/spec-dock-version` がない、`spec-dock/.gitignore` に C3 の3行が効く順でない）は止まる（次の1手 `spec-dock installation update` のPR）。S の宣言が版3でないときも止まる。
2. D が C7 の規則 `^[A-Za-z][A-Za-z0-9._/-]*$` に合わなければ止まる。S の `spec-dock/initiatives` に追跡されたファイルがあるのに、GitHub に canonical がないか、`build.json` がないか、`build.json` の `source_commit` の仕様のツリーが S の仕様のツリーと違えば止まる（canonical を作った後に仕様が変わった。次の1手 `build-canonical`。canonical は強制で書き換えないので、差分は切り替えの後に `adopt-worktree` で取り込む）。
3. 使い捨てのクローンで、S のツリーから `spec-dock/initiatives` の下を除き、`spec-dock/workspace.json` を版4の宣言のバイト列（配布資産と同じ `{"schema_version":4,"writer_protocol":"specdock.worktree-writer/v1"}` と改行）にし、`.github/workflows/spec-dock-check.yml` を見本のバイト列の `branches: [main]` を `branches: [D]` にしたものにしたツリーで、親を S とするコミットを作る（メッセージ `spec-dock: move specs to the canonical branch`、日時は S に固定）。
4. `--apply` なら、`<branch>`（既定 `spec-dock/migrate-to-canonical`）として `origin` に push する（強制しない。同じなら何もしない。違えば止まる）。
5. 出力に、SpecDock を呼ぶ今のCIの手順の一覧（`plan` と同じ）と、「統括がその手順を外すコミットを足してPRを作る」を示す。`spec-dock/` の下に、ほかの `.meta.json` が残るときは警告する（`canonical check` の調べること3で失敗するため）。

### `move-local <チェックアウト>` の手順
1. チェックアウトの `spec-dock/initiatives` が、ない、シンボリックリンクなら、何もしない。`git ls-files -- spec-dock/initiatives` に追跡されたファイルがあれば止まる（次の1手「`adopt-worktree` か、既定のブランチ（切り替えのPR）の取り込み」）。移すものに名前が `.meta.json` のファイルがあれば、何も移さずに止まり、一覧を示す（canonical に `.meta.json` を入れないため）。
2. ディレクトリの下のファイルとシンボリックリンクを、たどらずにすべて集める（追跡されていないものと無視されたもの）。行き先は `<main>/spec-dock/.canonical/<名前を置き換えた相対パス>`。行き先があれば `<本体>.local-<PC名>[.<拡張子>]`、それもあれば本体の後に `-2`、`-3`（本体と拡張子と PC名の規則は Epic の `design.md` 5章「別名ファイルの名前」と同じ）。
3. カタログ（`<main>/spec-dock/.canonical` を `spec-dock/canonical` でチェックアウトしている worktree）がなければ、移すファイルがあるときだけ作る（Q1）。作り方は `canonical link` の手順3と同じで、C6 の `-c` の設定を付ける：`git ls-remote --exit-code origin refs/heads/spec-dock/canonical`（なければ止まる）、取得の対象に入っていなければ `git remote set-branches --add origin spec-dock/canonical`、`git fetch --no-tags --no-recurse-submodules origin +refs/heads/spec-dock/canonical:refs/remotes/origin/spec-dock/canonical`、ローカルのブランチがなければ `git worktree add --track -b spec-dock/canonical <カタログ> origin/spec-dock/canonical`、あれば `git worktree add <カタログ> spec-dock/canonical`、最後に `git worktree lock --reason "spec-dock canonical catalog" <カタログ>`。`<main>/spec-dock/.canonical` に、カタログでないものがあれば止まる。手元の `spec-dock/canonical` があり、取得した `origin/spec-dock/canonical` と同じかその祖先でなければ、worktree を作る前に止まる（古い初期のコミットなどを戻さないため）。
4. 移す（`os.rename`、別のファイルシステムならコピーしてから元を消す。行き先を上書きしない）。空になったディレクトリを、深いものから消し、最後に `spec-dock/initiatives` を消す。
5. 移すファイルがなく、空のディレクトリだけなら、カタログを作らずに消す（Scope のないリポジトリ）。
6. `--apply` なしでは、移す予定、名前を変えるもの、消すディレクトリ、カタログを作るかを示す。

### `adopt-worktree <チェックアウト>` の手順（R-G5。Q2）
1. チェックアウトのブランチ B（detached なら止まる）、`M = merge-base(HEAD, origin/D)`。git が 2.40 より古ければ止まる（`merge-tree --merge-base` のため）。`spec-dock/initiatives` の外にステージ済みの変更があれば止まる（外すコミットに混ぜないため）。B の作業ツリーの `spec-dock/initiatives` を M と比べ、追跡しているファイルの変更、消したファイル、追跡されていない新しいファイル（無視されたものを除く）を求める。変更がなければ、2〜5（push）を飛ばして6に進む（外すコミットと削除は行う）。
2. 使い捨てのクローン（対象から `--no-checkout` で作り、B と M のオブジェクトを持つ）に、`origin` の canonical を `git fetch <origin の URL> +refs/heads/spec-dock/canonical:refs/heads/canonical` で取る。canonical の履歴（`git rev-list --format=%T`）から、ツリーが `M:spec-dock/initiatives` のツリーと同じコミット C を探す（新しいものから最初の1つ）。なければ止まる。
3. 作業ツリーの今の `spec-dock/initiatives`（追跡しているファイルと追跡されていない新しいファイル。消したファイルは除く）を、使い捨てのクローンのオブジェクトにして（`hash-object -w --no-filters`、シンボリックリンクは `120000`、実行の権限は `100755`）、`.meta.json` を除き、名前を置き換えたツリーで、親を C とするコミット X を作る。あわせて、C のツリーから `.meta.json` を除き名前を置き換えたツリーのコミット C'（親は C）を作り、統合の基点にする（両側の名前の置き換えを、名前の変更の検出に任せないため）。X、C'、Y の日時は M のコミットの日時に固定し、同じ入力から同じコミットにする。X が R の祖先なら（取り込み済み）、統合と push を飛ばして6に進む。
4. R を canonical の先頭とし、`git merge-tree --write-tree -z --merge-base=C' X R` で統合する。競合は Epic の `design.md` 5章の段の規則で解く（L = X、R = canonical）。両方の段があるパスは R の版を置き、X の版を別名ファイル `<本体>.conflict-<PC名>-<UTC の YYYYMMDDTHHMMSSZ>[.<拡張子>]` に置く。段2だけは X、段3だけは R を置く。終了コードが2以上なら止まる。親を R と X にしたコミット Y を作る。
5. `--apply` なしなら、取り込むファイル、競合と別名ファイルの名前、作業ツリーから消す予定のファイル、構造の違いを示して終わる。`--apply` なら、`git push <origin の URL> Y:refs/heads/spec-dock/canonical`（強制しない）。先に進まれて拒否されたら、2からやり直す（3回まで）。
6. push の後、`git ls-remote` で `origin` の canonical が Y か Y を含むことを確かめ、消す予定の各ファイル（`spec-dock/initiatives` の下の、無視されていないすべてのファイル）を確かめる。
   - `.meta.json` のほか：中身とモードが、Y の同じパス（名前の置き換えの後）と同じか、M の同じパスと同じ（ブランチで変えていない。中身は canonical の履歴の C にある）でなければならない。
   - `.meta.json`：canonical には入れない。8の構造の違いを、作業の記録の `adopt/<ブランチ名の / を - にしたもの>.json` と出力に残した後に消す。
   - どれかが確かめられなければ、何も消さずに止まり（3）、そのパスと、別名ファイルの名前を示す（両方で変えて競合したファイルや、git が中身を統合したファイルは、ここで止まる。人が canonical を確かめてから外す）。
7. チェックアウトで `git rm -r -q --cached -- spec-dock/initiatives` を行い、パスを付けない `git commit -q -m "spec-dock: move specs to the canonical branch"` で外すコミットを作る（パスを付けると作業ツリーを読み直すため付けない。ほかのステージ済みの変更がないことは1で確かめた。フックと署名は利用者の設定のまま）。コミットが失敗したら、`git reset -q -- spec-dock/initiatives` でインデックスを戻し、何も消さずに止まる。成功したら、`git ls-tree HEAD -- spec-dock/initiatives` が空であることを確かめてから、確かめたファイルを作業ツリーから消し、空になったディレクトリを消す。無視されたファイルは残す（次の1手 `move-local`）。
   - 止まったとき（中身が合わない、コミットの失敗）は、canonical にはすでに取り込んである。`README.md` に、カタログで中身を確かめてから、手で `git rm -r --cached spec-dock/initiatives` とコミットを行い、ファイルを消す手順を書く。
8. B の作業ツリーの `.meta.json` を M のものと比べ、親、依存、題名の違いと、増えた Scope、消えた Scope を一覧にする。次の1手は「SpecDock のコマンドで登録し直す」。

### `export-legacy` の手順（Q3）
1. S（`origin/D`）の宣言が版4でなければ止まる。GitHub の canonical を、使い捨てのクローンに取る。種類のラベルで GitHub の Scope をすべて読む。「切り離し前のコミット」B0 の `.meta.json` と宣言を読む。
2. Scope ごとの `.meta.json`：
   - 構造の項目：`type`（種類のラベル）、`id`（番号から）、`title`（GitHub の題名）、`slug`（印）、`parent_id`（GitHub の親の ID）、`initiative_id` と `epic_id`（親をたどる）、`depends_on`（Scope である blocked by の ID）、`backend: "github"`、`github`（番号と owner と repo）。
   - B0 に同じ番号の `.meta.json` があれば（ローカルの ID は `idmap.json` の番号で対応させる）、それを元にする。構造の項目を書き換えた結果が B0 と同じなら、B0 のバイト列をそのまま使う。違えば、B0 のキーの順と書き方（1行なら区切りの空白のない1行、そうでなければ `indent=2`。末尾の改行の有無も同じ）を保ち、`revision` を1つ上げる。`depends_on` は、集合が B0 と同じなら B0 の順、違えば番号の昇順にする。`_spec_dock`、`created_at`、`updated_at`、`lifecycle` は B0 のまま。
   - B0 にない Scope（移行の後に作ったもの）は、今の従来の CLI と同じ13個のキー（`revision: 0`、`lifecycle: null`）で書く。
3. Scope のディレクトリは、カタログの中で名前が `<ID>-` で始まるディレクトリ（ちょうど1つ）とする。見つからない Scope、Scope のないディレクトリ、入れ子が GitHub の親子と違うものは、警告にする。
4. ツリー：S のツリーから `.github/workflows/spec-dock-check.yml` を除き、`spec-dock/workspace.json` を B0 の宣言のバイト列（なければ `{"schema_version":3,"writer_protocol":"specdock.worktree-writer/v1"}` と改行）にし、`spec-dock/initiatives/` に canonical のツリー（ルートの `.spec-dock-canonical.json`、`.gitignore`、`README.md`、`.runtime/` を除く）と作った `.meta.json` を置く。親を S とするコミット（日時は S に固定）を作る。
5. `--apply` なら `<branch>`（既定 `spec-dock/export-legacy`）として `origin` に push する（強制しない。同じなら何もしない。違えば止まる）。次の1手：切り替えのPRで外した今のCIの手順を戻すコミットを足してPRを作る、マージの後に各チェックアウトで `spec-dock canonical remove --yes`、必要なら `undo --apply`。

### 写して持つ値（契約。AC-435-13）
| 契約 | 写す値 | 比べる相手 |
|---|---|---|
| C1 | 種類のラベル3つ（名前、色、説明）、印の行の正規表現と書き方、slug の規則、末尾への足し方、ID の接頭辞と5桁 | `domain/canonical_structure.py` の `KIND_LABELS`、`LABEL_DEFINITIONS`、`read_slug_marker`、`format_slug_marker`、`append_slug_marker`、`ID_PREFIXES`、`scope_id`、`domain/ids.py` の `INPUT_SLUG_KEBAB_RE` |
| C2 | 版4の宣言のバイト列、`specdock.worktree-writer/v1` | 配布資産 `spec_dock/workspace.json`、`application/project_context.py` の `NEW_WRITER_PROTOCOL` |
| C3 | 無視の3行（`spec-dock/.gitignore` の形）、`spec-dock/.gitignore` のパス、カタログとリンクの場所、`spec-dock/canonical` とその参照、lock の理由、無視の3行が効く順の判定 | `domain/canonical_layout.py` の `GITIGNORE_LINES`、`GITIGNORE_PATH`、`CATALOG_RELATIVE`、`LINK_RELATIVE`、`CANONICAL_BRANCH`、`CANONICAL_REF`、`CANONICAL_TRACKING_REF`、`CATALOG_LOCK_REASON`、`missing_lines` |
| C5 | 3つの管理ファイルの名前とバイト列、`.runtime` | `domain/canonical_content.py` の `CANONICAL_ROOT_FILES`、`FORMAT_FILE`、`RUNTIME_DIRECTORY` |
| C6 | Git の `-c` の設定 | `infra/canonical_git.py` の `HOOKLESS_CONFIG` |
| C7 | `CI_VERSION_FILE`、`WORKFLOW_SAMPLE`、`WORKFLOW_DESTINATION`、`WORKFLOW_BRANCH_LINE`、見本のバイト列、既定のブランチの名前の規則 | `application/canonical_check.py` の定数、配布資産 `spec_dock/docs/ci/spec-dock-check.yml`、I-7 の `design.md` の規則 |

- 別名ファイルの名前（5章）は、パッケージにまだ部品がない（I-3 の担当）ので、Epic の規則を写し、規則の例でテストする。

### `canonical check` の調べること4（R-435-11）
- `application/canonical_check.py` の `_declaration_failure` で、版4のとき、`writer_protocol` が `NEW_WRITER_PROTOCOL` でなければ `WORKSPACE_DECLARATION_INVALID`（`reason: "unknown-writer-protocol"`（今の値のまま）、メッセージ「the workspace declaration's writer_protocol is not specdock.worktree-writer/v1」、次の1手は今の `_DECLARATION_NEXT_STEP`）にする。古い値と知らない値を同じ失敗にする。`OLD_WRITER_PROTOCOL` の取り込みは使わなくなるので外す。

## data / failure

### 作業の記録
- `idmap.json`：`{"version": 1, "repository": "github.com/<owner>/<repo>", "entries": {"init-local-00002": {"id": "init-00039", "number": 39, "how": "existing"}}}`。一時ファイルに書いてから `rename` する。
- `undo.jsonl`：1行に1つの JSON。`{"seq": n, "phase": "intent"|"done"|"undone", "op": "label.create"|"issue.create"|"issue.label"|"issue.marker"|"sub_issue"|"blocked_by", "at": "<UTC>", ...}`。`op` ごとの項目：`label.create` は `name`。`issue.create` は `number`、`database_id`、`label`、`title`、`slug`、`local_id`（`done` のとき）。`issue.label` は `number`、`label`。`issue.marker` は `number`、`before`、`after`。`sub_issue` は `parent`、`child`、`child_id`。`blocked_by` は `number`、`blocker`、`blocker_id`。`undone` は `ref`（元の `seq`）。追記だけで、書き換えない。
- `build.json`：`build-canonical` の結果（上）。`verify` と `export-legacy` の「切り離し前のコミット」に使う。
- `adopt/<ブランチ>.json`：`adopt-worktree --apply` が、作業ツリーを変える前に書く、構造の違いの一覧と、取り込んだコミット Y。
- 記録は Git で無視し、リポジトリごとに分ける。消すと、`undo` は外す対象を失う（README に書く）。

### 失敗の扱い
- 書く前の失敗はすべて2。書いた後の失敗は3で、行った書き込みは記録に残り、もう一度の実行で続きから進む。
- 使い捨てのクローンは、成功しても失敗しても消す。
- `adopt-worktree` は、push の確かめと中身の確かめの後にだけ、作業ツリーを変える。外すコミットに失敗したら、インデックスを戻す。
- push は、すべて強制しない。参照がすでに違う中身なら止まる。

## 変更対象
- 足す：`scripts/migrate-to-canonical/{migrate.py,README.md,.gitignore}`、`tests/integration/migration/`（受け入れのテスト）、`tests/unit/infra/test_migration_contract_copies.py`（写した値）。
- 変える：`src/spec_dock/runtime/application/canonical_check.py`（調べること4）と、そのテスト（I-7 のテストに1件足す）。`tests/support/fake_github.py`（番号で読む GraphQL、本文の PATCH、ラベルの定義の削除を足す。今の振る舞いは変えない）。`scripts/static_analysis/run.sh`（対象に足す。Q6）。
- 変えない：従来モードの処理と、版3の振る舞いのテスト。パッケージのほかのコマンドと契約。

## 移行・互換性・rollback
- スクリプトはパッケージの外にあり、配布物を変えない。`canonical check` の変更は、版4の宣言で古い `writer_protocol` のときだけ結果が変わる（その宣言は SpecDock のコマンドでは作られず、書くコマンドは `require_writer` で止まる）。版3の宣言の扱いは変わらない。
- 戻し方：PRを `git revert` すれば戻る。スクリプトを使った後の各リポジトリの戻し方は、`README.md` と Epic の `design.md` の「戻し方」による。
- 撤去（I-13）で、`scripts/migrate-to-canonical/` と `scripts/static_analysis/run.sh` の対象の行を消す（申し送り）。

## testability
- スクリプトは、テストからファイルのパスで読み込み（`importlib`）、時計と `gh` の実行器を注入して呼ぶ（速さの確かめ）。受け入れのテストは、`python3 migrate.py` を別のプロセスで実行し、`PATH` の先頭の偽の `gh`（`tests/support/fake_github.py` の `install_fake_gh`）と、一時ディレクトリの bare のリポジトリ（`origin`）を使う。`XDG_STATE_HOME`、`HOME`、作業の記録の置き場は一時ディレクトリにする。
- 移行前のリポジトリの作り物：版3の宣言、0.3.0 の配布資産（版のファイルと無視の3行）、`.meta.json` と仕様のファイルを持つ Scope、ローカルの Scope、依存、`.workbench` の無視されたファイルを、bare のリポジトリの既定のブランチ（`main` か `develop`）に置き、偽の GitHub に対応する Issue を置く。
- 書かないことの確かめ：実行の前後で、対象の `git for-each-ref`、`git status --porcelain --ignored`、`.git/config`、`origin` の参照、作業の記録の置き場、偽の `gh` の書き込みの記録を比べる。
- `move-local` の後の `canonical link`：パッケージの `spec_dock.cli.main` を `--project` で呼び、`succeeded` で、カタログを作り直さないことを確かめる（`isolate_user_state` と注入した環境）。
- `export-legacy` の後の従来モード：作ったブランチをチェックアウトし、パッケージの `workspace validate` と `scope show` を呼んで通ることを確かめる（日本語の題名を含む）。
- 本物の5つのリポジトリの `plan`：読むだけで実行し、実行の前後で、各リポジトリの参照と `git status` が同じことを確かめ、結果を `report.md` に書く。

## risk
| リスク | 影響 | 軽減 |
|---|---|---|
| `register` の途中の停止で、重複や取りこぼしが出る | 中 | 意図と結果の記録、GitHub の今の状態からの予定の作り直し、作成の再発見 |
| 二次のレート制限 | 中 | 1秒の間、1分80回、1時間500回、待って続ける |
| 写した値がパッケージとずれる | 中 | 値ごとにパッケージの定数と資産と比べるテスト |
| `adopt-worktree` が作業ツリーの変更を失う | 大 | push と中身の確かめの後にだけ消す。合わなければ何も消さない。無視されたファイルは消さない |
| `git subtree split` が遅い（spec-dock は約2000コミット） | 低 | 使い捨てのクローンで行い、本番の前の予行演習で時間を測る |
| `export-legacy` の `.meta.json` が従来モードで読めない | 中 | 従来モードの `workspace validate` と `scope show` をテストで通す |
| 本物のリポジトリを誤って書き換える | 大 | 既定は予定の表示だけ。この Issue では本物で `plan` だけを実行し、前後の状態を比べる |
