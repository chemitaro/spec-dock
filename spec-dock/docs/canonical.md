# canonical モードの使い方

SpecDock 0.3.0 から、仕様の置き場を2つの形から選べます。`spec-dock/workspace.json` の `schema_version` が 3 のリポジトリは従来モードで、仕様もコードと一緒にコミットします（今までと同じ）。4 のリポジトリは canonical モードで、仕様の構造（作成、親子、依存、状態、題名、種類）を GitHub Issue に、中身を `spec-dock/canonical` ブランチに置き、コードのブランチには仕様を入れません。版3から4への移行は、spec-dock のリポジトリの `scripts/migrate-to-canonical/README.md` の手順で一度だけ行います。

エージェントが守る規則は、配布するスキル（`.agents/skills/spec-dock/SKILL.md`）の「仕様の扱い（canonical モード）」の節にあります。この文書は、利用者が用意と困ったときの扱いを知るためのものです。

## モードと置き場

- 仕様は、どのチェックアウトからも `spec-dock/initiatives/` に見えます。これはシンボリックリンクで、先はそのクローンのカタログ（mainのチェックアウトの `spec-dock/.canonical`。`spec-dock/canonical` ブランチのworktree）です。普通のファイルとして読み書きします。
- Scope のディレクトリは、種類と親を問わず `spec-dock/initiatives/<区切り>/<ID>/` に平らに並びます。入れ子にしません。
  - ID は `<種類>-<番号5桁>`（`init-00423`、`epic-00424`、`iss-00454`）。5桁を超えた番号はそのまま（`iss-100454`）。
  - `<区切り>` は番号の千ごとの範囲で、`<下端>-<上端>` を ID の番号と同じ幅で0埋めします（1〜999 は `00000-00999`、1000 は `01000-01999`、100000 は `100000-100999`）。例：`spec-dock/initiatives/00000-00999/iss-00454/`、`spec-dock/initiatives/02000-02999/iss-02114/`。区切りは番号だけで決まり、親や種類を変えても動きません。
  - slug はありません。canonical モードの `scope create` と `scope import github` に `--slug` を付けると `CANONICAL_NOT_APPLICABLE` で止まります。`scope import github` の `--title` は受け付けますが使わず、GitHub の題名で進めます（違えば警告 `CANONICAL_TITLE_IGNORED`）。
  - コマンドの入力は0埋めしなくてよい（`iss-454` は `iss-00454`）。表示と出力は0埋めの形です。
- 題名は GitHub の題名が正本です。日本語を含むどの言語でもよく、空でなく、制御文字を含まず、256文字以下です。題名を変えても、ID、ディレクトリ名、ブランチ名は変わりません。
- 親子と依存は GitHub だけにあり、ディレクトリの位置には表れません。場所、親、子、依存は `spec-dock scope show <ID> --json`（`path`、`parent_id` など）で確かめます。
- `spec-dock scope move <ID> --parent <親>` は GitHub の親だけを付け替えます。ディレクトリは動きません。
- `work start` の既定のブランチ名は `<ID>`（例 `iss-00454`）です。移行前に作った `<ID>-<名前>` のブランチも `--branch` で使えます。
- GitHub で種類のラベルを付け替えると、ID が変わるため `SCOPE_KIND_CHANGED` になり、書くコマンドと `work start`、`branch` が止まります（下の「エラーと次の1手」）。

## 用意と状態

```sh
spec-dock canonical link            # このクローンのカタログを探すか作り、このチェックアウトにリンクを置き、定期の同期に登録する
spec-dock canonical status          # カタログ、リンク、読み書き、ツールの設定、同期、未保存と保留を示す（GitHub に問い合わせない）
spec-dock canonical status --structure   # 上に加えて、Scope のディレクトリと GitHub の対応の異常を確かめる
```

- `canonical link` はクローンごとに1回で足ります。何度実行しても同じ結果です。`spec-dock worktree create` と `spec-dock work start` で作ったworktreeには、自動でリンクを置きます。`git worktree add` で作ったworktreeと新しいクローンでは、`canonical link` を1回実行します。
- `canonical link` が書くもの：カタログのworktree（lock 付き）、`.git/info/exclude` の無視の3行、`.git/config` の取得の対象（`git remote set-branches --add origin spec-dock/canonical`）、手元のブランチ `spec-dock/canonical` の付け替え（`update-ref`）、リンク、状態の置き場の登録簿と基準、定期の実行（macOS は launchd、systemd の Linux はユーザーのタイマー、ほかは常駐のプロセス）。
- `canonical link --no-schedule` は、登録簿に載せず、定期の実行も作りません（予行演習で使う）。基準は記録します。登録済みのカタログに `--no-schedule` を付けても登録は外れません。外すのは `canonical remove` です。
- `canonical status` の項目：`catalog`、`link`、`exclude`、`access`、`tools`、`sync`、`changes`、`format`、`git`、`snapshot`、`dashboard`、`structure`。問題ごとに `next_step` を示します。読むだけなので、問題があっても終了コード0です。
- `structure` の形は `{status: ok / problem / unavailable, next_step, snapshot, anomalies: [{code, severity, message, details}]}` です（最初の版の `misplaced` は `anomalies` に置き換わりました）。`--structure` を付けたときだけ埋まります（`SCOPE_DIRECTORY_MISSING`、`SCOPE_ISSUE_MISSING`、`SCOPE_KIND_CHANGED`、`SCOPE_DIRECTORY_MISPLACED`）。
- 取り外しは `spec-dock canonical remove --yes`（このクローンのリンク、カタログ、除外、登録を外す。未保存か未pushがあれば止まる。ブランチは消さない）。破壊的な操作なので、対象と結果を明示して指示します。

## ツールの設定

作業用のworktreeで動く Claude Code と Codex は、作業ディレクトリの外にあるカタログに書くために、ツールごとに1行の設定が要ります。利用者が1回だけ手で足します。SpecDock は、`installation init` と `installation update` を含めて、ツールの設定のファイルを書き換えません。`<カタログ>` は、そのクローンのカタログの絶対パス（`<mainのチェックアウト>/spec-dock/.canonical`）で、`canonical status` の `tools` が、そのクローンでの正確な1行を示します。

- **Claude Code**：ユーザーの設定 `~/.claude/settings.json`（環境変数 `CLAUDE_CONFIG_DIR` があれば `$CLAUDE_CONFIG_DIR/settings.json`）の `permissions.additionalDirectories` に加えます。

  ```json
  { "permissions": { "additionalDirectories": ["<カタログ>"] } }
  ```

- **Codex**：`~/.codex/config.toml` の `[sandbox_workspace_write]` の `writable_roots` に加えます。

  ```toml
  [sandbox_workspace_write]
  writable_roots = ["<カタログ>"]
  ```

- カタログはクローンごとにあるので、移行したリポジトリが5つなら5つ並べます。どちらも配列なので1行に並べられます。

  ```json
  { "permissions": { "additionalDirectories": ["/path/to/spec-dock/spec-dock/.canonical", "/path/to/taikyohiyou_project/spec-dock/.canonical", "/path/to/housing-lifecycle/spec-dock/.canonical", "/path/to/input-devices/spec-dock/.canonical", "/path/to/company-os/spec-dock/.canonical"] } }
  ```

  ```toml
  [sandbox_workspace_write]
  writable_roots = ["/path/to/spec-dock/spec-dock/.canonical", "/path/to/taikyohiyou_project/spec-dock/.canonical", "/path/to/housing-lifecycle/spec-dock/.canonical", "/path/to/input-devices/spec-dock/.canonical", "/path/to/company-os/spec-dock/.canonical"]
  ```

- 足さないと：Claude Code は作業ディレクトリの外のファイルの読み書きの許可を求めるか拒みます（「outside the allowed working directories」などの文言）。Codex のサンドボックスでは書き込みが `Operation not permitted` で拒まれます。どちらも、エージェントは自分で設定を変えず、`canonical status` の1行を利用者に伝えます。
- 要らない場合：mainのチェックアウトの中で動くセッション（カタログが作業ディレクトリの中にある）。
- 書けない場合：Claude Code の隔離セッション（`--worktree`）は、設定を足しても書けません。仕様を読むだけにします。
- 確かめ方：作業用のworktreeで `spec-dock canonical status` を実行し、`tools` の `status` が `ok` で、警告 `CANONICAL_TOOL_SETTING_MISSING` がないこと。Claude Code の設定は、ユーザーの設定、`<チェックアウト>/.claude/settings.json`、`<チェックアウト>/.claude/settings.local.json` を読むだけ読んで判定します（Claude Code の中の判定は SpecDock から見えないので、判定できないときは `CANONICAL_TOOL_SETTING_UNKNOWN`）。Codex は環境変数 `CODEX_SANDBOX` があるときに、書けるかを確かめます。

## 保存と同期

- 保存（カタログのコミット）、取り込み、push は、定期の実行が60秒ごとに自動で行います。最後の変更から30秒たったファイルを保存するので、1〜2分のうちに別のクローンから見えます。同じPCのほかのworktreeからは、保存の前にも見えます。
- 仕様を Git で扱いません（`git add`、`commit`、`stash`、`reset`、`checkout`、`clean`）。カタログ（`spec-dock/.canonical`）でも手で Git を使いません。手で行ったコミットは削除の保留の規則を通らず、毎周期の `git reset` は手でステージした内容を捨てます。
- 2台で同じファイルを変えたときは、先に保存された版が元の名前に、もう一方が `<名前>.conflict-<PC名>-<時刻>.<拡張子>` に残ります。中身を元のファイルに統合してから、別名のファイルを消します。
- 保留：秘密情報らしい中身、大きすぎるファイル、大量の削除（20件を超えるなど）は保存せずに止めます。`spec-dock canonical status` の `changes.holds` で確かめ、保存してよければ `spec-dock canonical accept <パス>`（削除は `--deletions`）、戻すなら `spec-dock canonical restore [<パス>]` を実行します。中身を直せば次の周期で保存されます。
- `spec-dock work finish` は、対象と子孫の `<区切り>/<ID>/` の未保存の変更を束にして、定期の実行にすぐの周期を頼み、保存と push が確かめられるまで最大180秒待ってから Issue を閉じます。確かめられなければ閉じずに `CANONICAL_SAVE_UNCONFIRMED` で止まります。保留があれば `CANONICAL_SAVE_HELD` で止まります。
- `work start` が警告 `SCOPE_IN_PROGRESS` を返したら、別のPCで作業中でないかを利用者に確かめます。古い印なら、そのPCで `spec-dock work finish` するか、GitHub で `spec-dock:in-progress` のラベルを外します。

## 同期が止まったとき

`spec-dock canonical status` の `sync.paused` に理由が出ます。GitHub の `spec-dock/canonical` が強制 push で書き換えられたか消されたときは、取り込まずに一時停止します（手元の編集を失わないため）。利用者が扱いを決めてから再開します。

| 理由 | 意味 | 再開 |
|---|---|---|
| `remote_rewritten` | GitHub の履歴が、手元の履歴を含まない形に書き換えられた | GitHub の今の履歴を正とするなら `spec-dock canonical resume --adopt-remote`。手元の中身を、GitHub の履歴の上の1つのコミットに重ね直し、GitHub が消した古い履歴は送りません |
| `merge_failed` | 統合が Git の失敗で止まった | `spec-dock canonical resume --adopt-remote`。重ね直しで保留（秘密情報など）に当たると止まったままになるので、保留を解いてから、もう一度 `resume --adopt-remote` が要ることがあります |
| `remote_deleted` | GitHub の `spec-dock/canonical` が消された | 手元から作り直すなら `spec-dock canonical resume --push-local`。ほかのPCがすでに作り直していれば `--adopt-remote` を案内します |

- `--adopt-remote` の重ね直しの途中（保留の修正を待っている間）に GitHub のブランチが消されたときは、`--push-local` を拒みます（手元の履歴には GitHub が消した履歴が残っているため）。別のPCかカタログで GitHub の状態を確かめ、戻っていれば `--adopt-remote` で再開します。手元から作り直すかは利用者が決めます。
- macOS のプライバシーの保護：外付けのボリュームのリポジトリでは、launchd のジョブが Python と git の読み書きを拒まれることがあります。`canonical status` に `CANONICAL_SYNC_NOT_CONFIRMED` が出たら、システム設定の「プライバシーとセキュリティ」で、示した Python と git にフルディスクアクセス（かリムーバブルボリュームへのアクセス）を許可し、もう一度 `canonical status` で確かめます。
- push の認証の失敗（`CANONICAL_PUSH_AUTH_FAILED`）：HTTPS なら `gh auth setup-git`。SSH は定期の実行にエージェントが渡らないことがあるので、HTTPS と `gh` の認証を使います。
- ログは `<状態の置き場>/canonical-sync.log` です（状態の置き場は `$XDG_STATE_HOME/spec-dock`、なければ `~/.local/state/spec-dock`）。

## Linux とコンテナ

- `canonical link` と定期の同期には Git 2.38 以上が要ります（`merge-tree --write-tree`）。Ubuntu 22.04 の標準の Git（2.34）では足りず、`CANONICAL_GIT_TOO_OLD` で止まります。新しい Git を入れてから、もう一度 `spec-dock canonical link` を実行します（登録簿の git を入れ替えるため）。
- systemd の動く Linux では、ユーザーのタイマー（`~/.config/systemd/user/`）で同期します。ログアウトの後も動かすには linger が要ります。`canonical status` に `CANONICAL_LINGER_DISABLED` が出たら `loginctl enable-linger <ユーザー>` を実行します（管理者の権限が要ることがあります）。
- systemd のない Linux（Docker などのコンテナ）では、SpecDock の常駐のプロセス（`spec-dock canonical sync --registered --loop`）が同期します。`canonical link` が起動します。コンテナを起動し直すと止まるので、`canonical link` が示す起動し直しの1行を、devcontainer の `postStartCommand` か起動のスクリプトに足します（足さなくても、次の `spec-dock canonical link` で動き直します）。
- コンテナでは、リポジトリをコンテナの中でクローンして `canonical link` します。ホストのチェックアウトをマウントしたコンテナでは、Git の記録がホストのパスを指すので、`canonical link` は `repair` も `prune` もせずに `CANONICAL_FOREIGN_CHECKOUT` で止まります（ホストの記録を壊さないため）。保存と同期はホストで行われ、コンテナでは仕様のファイルを読み書きするだけにします。

## 構造のスナップショットとダッシュボード

- SpecDock は、GitHub の構造（Scope の Issue の番号、種類、題名、状態、ラベル、担当者、親子、依存）を、リポジトリごとに一括で読んで `<状態の置き場>/github/<host>/<owner>/<repo>/snapshot.json` に持ち、表示に使い回します（書けない環境ではメモリーの上だけ）。変わったかの確かめは条件付きの要求（304）なので、GitHub の主のレート制限を消費しません。
- 新しさ：題名や状態などの変化は、定期の同期の確かめで1〜2分のうちに表示に出ます。親子と依存だけの変更は、Issue の更新の時刻が変わらないことがあるので、最大30分（全体の取り直しの間隔）かかります。SpecDock のコマンドで書いた変更は、次の表示にすぐ出ます。書くコマンドは、書く前に GitHub で確かめ直します。
- 急ぐとき：`spec-dock workspace sync --source github` か `spec-dock dependency check <ID> --source github` で、確かめを待たずに全体を取り直します。
- `dependency check` と `workspace sync` の `--source`：canonical モードでは、引数なしはスナップショットで判定し、`--source github` は全体を取り直してから判定し、明示した `--source local` は `CANONICAL_NOT_APPLICABLE` で止まります（従来モードの既定の意味は変わりません）。
- `--offline` を付けた読むコマンドは、GitHub に何も送らず、保存したスナップショットを古いもの（警告 `GITHUB_SNAPSHOT_STALE`）として示します。`--source github --offline` は止まります。`canonical sync` と `canonical resume` は `--offline` を受け付けません。
- GitHub につながらないとき、読むコマンドは古いスナップショットで示し、`GITHUB_SNAPSHOT_STALE` を警告に入れます。書くコマンドは書く前に止まります。
- ダッシュボード：定期の同期が、mainのチェックアウトの `spec-dock/` に、今までと同じ5つのファイル（`dashboard.md`、`tree.puml`、`tree-all.puml`、`deps-issues.puml`、`deps-raw.puml`）を、構造が変わったときだけ作り直します。題名は GitHub の題名、作業中はラベル `spec-dock:in-progress` で示します。書けなかったときは `canonical status` の `dashboard` に `CANONICAL_DASHBOARD_OCCUPIED`（書く場所にディレクトリかシンボリックリンクがある。退避すれば次の同期が書く）か `CANONICAL_DASHBOARD_FAILED`（`snapshot` と `sync` の項目を確かめる）が出ます。

## 制約

- mainのチェックアウトが sparse-checkout だと、カタログがその設定を引き継ぎ、仕様が見えないことがあります。カタログでは sparse-checkout を使わないでください。
- カタログに対する Git の呼び出しは、フックと署名を外し、`GIT_ASKPASS` を通しません。askpass で HTTPS の認証をしている端末（VS Code の中など）では、push と fetch が失敗しえます。`gh auth setup-git` の認証を使います。
- 予行演習や試しでは、環境変数 `XDG_STATE_HOME` を必ず一時ディレクトリにします。`--no-schedule` でも基準を状態の置き場に書くためです。`canonical sync` を直接呼ぶときは `--state-root` も一時ディレクトリで渡します。
- `spec-dock worktree remove` は、SpecDock が置いたリンク `spec-dock/initiatives` だけが無視されたファイルなら、`--discard-ignored` なしで消します（リンクを消すだけで、カタログの中身は消えません）。カタログのworktreeを対象にすると `CANONICAL_CATALOG_PROTECTED` で止まります。
- リンクを手で消すときは `rm spec-dock/initiatives`（末尾に `/` を付けない）。mainのチェックアウトで `git clean -ff` を使いません（カタログのworktreeを消すため）。
- `workbench copy` は、どのworktreeからも同じカタログの `.workbench` が見えるので要らず、`CANONICAL_WORKBENCH_SHARED` で止まります。
- `workspace validate --ci` は `CANONICAL_NOT_APPLICABLE` で止まります。CI では `canonical check` を使います。

## 既定のブランチの検査

- `spec-dock canonical check [--commit REV]` は、コードのツリーのコミットに仕様のパス、`.canonical` の下のパス、`.meta.json` がなく、版4の宣言、配布資産、無視の3行、版のファイルがそろうかを確かめます。ネットワークと GitHub のトークンなしで動き、問題はパスと次の1手付きで終了コード7です。
- ワークフローの見本は `spec-dock/docs/ci/spec-dock-check.yml` です。`spec-dock/system/spec-dock-version` の版のタグ（`v0.3.0` など）の SpecDock を入れて `canonical check` を実行します。版のタグは 0.3.0 から作るので、見本は 0.3.0 以降の配布資産で使います（0.2.4 の版のファイルのままでは入れる段階で失敗します）。
- 検査は PR をきっかけに動き、結果を PR に表示します。人は通過を確かめてからマージします。

## エラーと次の1手

どのエラーも、JSON の `recovery`（警告は `details.next_step`）に次の1手を入れます。終了コードの「警告」は、結果の状態を変えずに `warnings` に出るものです。

| コード | 終了コード | 次の1手 |
|---|---|---|
| `CANONICAL_NOT_MIGRATED` | 3 | 宣言が版3のリポジトリです。移行するなら spec-dock の `scripts/migrate-to-canonical/README.md` に従う（`canonical link` では、GitHub に canonical がなく既定のブランチに仕様があるときも） |
| `CANONICAL_CHECKOUT_NOT_MIGRATED`、`CANONICAL_MAIN_NOT_MIGRATED` | 3／警告 | そのチェックアウト（mainのチェックアウト）で移行後のコミットをチェックアウトしてから `spec-dock canonical link` |
| `CANONICAL_NOT_APPLICABLE` | 3 | 示した代わりのコマンドを使う（`canonical check`、`--slug` なしの作成、`--source` なしなど） |
| `CANONICAL_UNSUPPORTED_LAYOUT` | 3 | mainのチェックアウトのある構成（bare でないクローン）で使う |
| `CANONICAL_GIT_TOO_OLD` | 3 | Git 2.38 以上を入れ、`spec-dock canonical link` をもう一度実行する |
| `CANONICAL_FOREIGN_CHECKOUT` | 3 | 保存と同期はホストで行う。コンテナでは仕様のファイルを読み書きするだけにするか、コンテナの中でクローンして `spec-dock canonical link` |
| `CANONICAL_NOT_LINKED` | 3 | `spec-dock canonical link` |
| `CANONICAL_PATH_OCCUPIED`、`CANONICAL_LINK_OCCUPIED` | 3 | 示したパスの中身を確かめて退避してから `spec-dock canonical link`（SpecDock は消さない）。worktree の登録だけが残っているときは、確かめてから `git worktree remove` か `git worktree prune` を自分で実行する |
| `CANONICAL_INSIDE_CATALOG` | 3 | チェックアウトのルートで実行するか、`--project <チェックアウト>` を付ける |
| `CANONICAL_SANDBOX_DENIED` | 3 | サンドボックスの外（普通の端末）で同じコマンドを実行する |
| `CANONICAL_LOCK_BUSY` | 3 | しばらく待って同じコマンドを実行する |
| `START_LOCK_BUSY` | 3 | 同じクローンで別の `work start` か `branch switch` が動いている。しばらく待って同じコマンドを実行する（Git を直接使わない） |
| `OS_ACCESS_DENIED` | 警告（`canonical link`、`status`）／`last_error` | 定期の実行がカタログを読めない。macOS はプライバシーの保護の許可（上の「同期が止まったとき」）、ほかは示したパスの権限を確かめる |
| `CANONICAL_FORMAT_UNSUPPORTED` | 3 | SpecDock を更新する |
| `CANONICAL_UNSAVED_CHANGES` | 3 | `spec-dock canonical status` で確かめ、保存を待つ |
| `CANONICAL_IGNORED_FILES_PRESENT` | 3 | 示したファイルを退避してから同じコマンドを実行する |
| `CANONICAL_SAVE_HELD` | 3（`work finish`）／警告（`status`） | 保留の種類ごとに、`spec-dock canonical accept <パス>`（削除は `--deletions`）、`spec-dock canonical restore`、中身の修正 |
| `CANONICAL_SAVE_UNCONFIRMED` | 3（束を書く前）／6（partial。束を書いた後） | `spec-dock canonical status` で同期を確かめてから、もう一度 `spec-dock work finish` |
| `CANONICAL_PAUSED` | 3（`resume`）／警告（`status`） | `spec-dock canonical status` で理由を見て、上の「同期が止まったとき」に従う |
| `CANONICAL_BASE_HAS_SPECS` | 3 | 移行の後のコミット（仕様のないもの）を基点にする |
| `CANONICAL_CATALOG_PROTECTED` | 3 | 取り外すなら `spec-dock canonical remove` |
| `CANONICAL_WORKBENCH_SHARED` | 3 | 何もしなくてよい（どのworktreeからも見える） |
| `CANONICAL_CHECK_FAILED` | 7 | 失敗ごとに示したパスを、既定のブランチから外す（下の `canonical check` の失敗の種類） |
| `SPEC_PATH_TRACKED`、`CATALOG_PATH_TRACKED`、`SCOPE_METADATA_TRACKED` | 7（`canonical check` の失敗） | 示したパスを、コードのブランチから外すPRを作る |
| `WORKSPACE_NOT_MIGRATED`、`WORKSPACE_DECLARATION_INVALID` | 7（同上） | 宣言を版4の正しい形にする（移行の `cut` のブランチを使う） |
| `STATIC_ASSET_INVALID`、`SPEC_DOCK_VERSION_MISMATCH` | 7（同上） | `spec-dock installation update` で配布資産を上げる。知らない中身は手でマージする |
| `IGNORE_RULES_MISSING` | 7（同上） | `spec-dock installation update`（`.gitignore` が配布物のとき）か、無視の3行を手で足す |
| `CANONICAL_IGNORE_RULES_MISSING` | 警告 | 無視の3行（`/.canonical/`、`/initiatives`、`!/initiatives/`）を足す（`spec-dock installation update` か `spec-dock canonical link`） |
| `CANONICAL_TOOL_SETTING_MISSING`、`CANONICAL_TOOL_SETTING_UNKNOWN` | 警告 | 上の「ツールの設定」の1行を足す。判定できないときは設定を自分で確かめる |
| `CANONICAL_MAIN_MOVED` | 警告 | 各作業用のworktreeで `spec-dock canonical link`（worktree も動かしたなら、先に mainで `git worktree repair <パス>`） |
| `CANONICAL_REMOTE_MISSING` | 警告 | GitHub の `spec-dock/canonical` が消されていないか確かめ、`spec-dock canonical status` の案内に従う |
| `CANONICAL_SYNC_NOT_SCHEDULED` | 警告 | `spec-dock canonical link`（`--no-schedule` なしで） |
| `CANONICAL_SYNC_NOT_CONFIRMED` | 警告 | macOS はプライバシーの保護の許可（上）、Linux はログを確かめる |
| `CANONICAL_PUSH_AUTH_FAILED` | 警告 | `gh auth setup-git`（SSH なら HTTPS と `gh` の認証にする） |
| `CANONICAL_LINGER_DISABLED` | 警告 | `loginctl enable-linger <ユーザー>` |
| `CANONICAL_RUNNER_RESTART` | 警告 | 起動し直しの1行を、devcontainer の `postStartCommand` か起動のスクリプトに足す |
| `CANONICAL_RUNNER_STOPPED` | 警告 | 起動し直しの1行を実行する（か `spec-dock canonical link`） |
| `CANONICAL_UNPUSHED_STALE` | 警告 | `gh auth status` と接続を確かめ、`spec-dock canonical status` の `sync` を見る |
| `CANONICAL_SYNC_BLOCKED` | 警告 | 示したファイルの編集を終える（遅くとも5分で保存されて統合される） |
| `CANONICAL_SYNC_FAILED`、`SYNC_FAILED`、`GIT_FAILED` | 警告（`last_error`） | `spec-dock canonical status` とログ（`<状態の置き場>/canonical-sync.log`）を確かめる |
| `CANONICAL_STATE_UNREADABLE`、`CANONICAL_REGISTRY_UNREADABLE` | 3／警告 | 示したファイルを確かめ、退避してから `spec-dock canonical link` |
| `CANONICAL_GIT_IN_PROGRESS` | 警告（`last_error`） | カタログで途中の Git の操作を終える（`git -C <カタログ> merge --abort` など） |
| `CANONICAL_STATE_ROOT_MISMATCH` | 3（`link`）／警告（`status`） | そのジョブの状態の置き場（リンクしたときの `XDG_STATE_HOME`）で実行するか、そこに登録したカタログを先に `spec-dock canonical remove` |
| `CANONICAL_SCHEDULER_FAILED` | 6（partial） | 示した出力を確かめて `spec-dock canonical link` |
| `CANONICAL_WRITE_INCOMPLETE` | 6（partial）／失敗 | 書くコマンドが途中で止まった。`effects` の `succeeded`、`unknown`、`not_attempted` を確かめ、GitHub とカタログの今の状態を見てから、`recovery` の手順に従う（同じコマンドの再実行で続きから進むものが多い） |
| `CANONICAL_REMOVE_FAILED` | 6（partial） | `spec-dock canonical status` で確かめてから `spec-dock canonical remove --yes` |
| `CANONICAL_NOT_HELD` | 3 | `spec-dock canonical status` の `changes.holds` のパスを指定する |
| `CANONICAL_NOT_RESTORABLE` | 3 | ファイルを自分で直すか消す。保存してよければ `spec-dock canonical accept <パス>` |
| `CANONICAL_PATH_NOT_FOUND` | 3 | カタログの中の、今あるファイルのパスを指定する |
| `CANONICAL_CONFLICT_COPY` | 警告（`workspace validate`） | 別名ファイルの中身を元のファイルに統合し、別名ファイルを消す |
| `CANONICAL_DASHBOARD_OCCUPIED` | 警告（`status` の `dashboard`） | 示したパスを退避する。次の同期が書く |
| `CANONICAL_DASHBOARD_FAILED` | 警告（同上） | `spec-dock canonical status` の `snapshot` と `sync` を確かめる |
| `CANONICAL_TITLE_IGNORED` | 警告（`scope import github`） | 題名を変えるなら `spec-dock scope edit <ID> --title <題名>` |
| `SCOPE_IN_PROGRESS` | 警告（`work start`） | 別のPCで作業中でないか利用者に確かめる。古い印なら `spec-dock work finish` か GitHub でラベルを外す |
| `SCOPE_CHECK_FAILED` | 7（`scope check`）／3（`work finish`。何も書かない）／警告（既に完了の Scope の `work finish`） | 誤りごとに示したファイルと `hint` のとおりに直し、`spec-dock scope check <ID>` で確かめてから、もう一度 `spec-dock work finish <ID> --yes` |
| `SCOPE_FORMAT_CONFLICT` | 7（`scope check`、`workspace validate`） | `requirement.md` と `requirement.cue` の片方を外し、Scope の形式を1つにする |
| `CUE_NOT_FOUND`、`CUE_VERSION_UNSUPPORTED` | 3（`scope check`、CUE の Scope の `work finish`） | `cue` v0.17.1 以上を PATH に入れる（例 `go install cuelang.org/go/cmd/cue@v0.17.1`）。Markdown の Scope には要らない |
| `CUE_TIMEOUT`、`CUE_FAILED` | 5（同上） | `--timeout` を延ばして同じコマンドを実行する。`cue version` が動くか確かめ、動かなければ入れ直す |
| `CUE_SCHEMA_UNSUPPORTED` | 3（同上） | `requirement.cue` の `schema` の版を持つ SpecDock に上げる（持っている版を示す） |
| `SCOPE_NOT_CUE` | 7（`scope render`） | Markdown の Scope は描けない。`requirement.md`、`design.md`、`plan.md` を直接読む |
| `SCOPE_RENDER_INCOMPLETE` | 警告（`scope render`） | 評価が通らないので、検査の結果だけを描いた。`spec-dock scope check <ID>` の誤りを直してから、もう一度描く |
| `DESIGN_SYSTEM_MISSING` | 警告（`scope render`） | このチェックアウトに `spec-dock/design-system/` がない。`spec-dock installation update` で入れる |
| `CANONICAL_PROGRESS_MARK_FAILED` | 警告（`work start`、`work finish`） | GitHub で `spec-dock:in-progress` のラベルと担当者を確かめ、付け外す |
| `READINESS_NOT_SATISFIED` | 3（`work start`） | `spec-dock dependency check <ID>` で止めているものを確かめ、前提を完了させる |
| `READINESS_UNKNOWN`、`DEPENDENCY_NOT_IN_SNAPSHOT` | 警告（読むコマンド、`dependency check`） | `spec-dock workspace sync --source github` で取り直す。続くなら示した依存先を GitHub で確かめる |
| `DEPENDENCY_NOT_SCOPE` | 警告 | Scope でない Issue への依存です。意図どおりならそのまま、違えば `spec-dock dependency remove` |
| `DEPENDENCY_CYCLE`、`DEPENDENCY_INVALID`、`DEPENDENCY_FOREIGN_REPOSITORY` | 3（`dependency add`）／警告（構造の異常） | 循環や別のリポジトリへの依存を GitHub で外す（`spec-dock dependency remove`） |
| `PARENT_MISSING`、`PARENT_INVALID`、`PARENT_FOREIGN_REPOSITORY`、`SUB_ISSUE_FOREIGN_REPOSITORY`、`KIND_LABEL_MULTIPLE` | 3（書くコマンド）／警告（構造の異常、`workspace validate`） | 示した Issue のラベルと親子を GitHub で直す（`spec-dock scope move <ID> --parent <親>` など） |
| `DESCENDANT_STATUS_UNKNOWN` | 3（`scope close` など） | 子の Issue（別のリポジトリの sub-issue や、ID を決められない子）を GitHub で確かめて直す |
| `SCOPE_KIND_CHANGED` | 3（書くコマンド、`work start`、`branch`）／警告（読むコマンド、`workspace validate`） | GitHub の種類のラベルを元に戻す。種類を変えるのが意図なら、新しい種類で Issue を作り直し、古いディレクトリの中身を新しい `<区切り>/<ID>/` に移し、古い Scope を今の ID で `spec-dock scope delete` |
| `SCOPE_DIRECTORY_MISSING` | 警告（`workspace validate`） | その Scope の `<区切り>/<ID>/` を作る（`spec-dock scope import github <種類> <番号>`）か、別のクローンの保存を待つ |
| `SCOPE_ISSUE_MISSING` | 警告（同上） | 示した `<ID>/` の Issue を GitHub で確かめる。要らなければ中身を確かめてからディレクトリを消す |
| `SCOPE_DIRECTORY_MISPLACED` | 警告（同上） | 中身を `<区切り>/<ID>/`（`details.expected`）に移し、空になったディレクトリを消す |
| `SCOPE_DOCUMENT_MISSING` | 警告（同上） | 示した文書を足す（Markdown の Scope は `requirement.md`、`design.md`、`plan.md`、`report.md`、CUE の Scope は `requirement.cue`、`design.cue`、`plan.cue`、`report.md`） |
| `SCOPE_METADATA_PRESENT` | 警告（同上） | カタログの `.meta.json` を消す（canonical モードでは使わない） |
| `GITHUB_SNAPSHOT_STALE` | 警告 | 表示は取得の時刻の時点のもの。つながったら、次の表示か定期の同期で新しくなる |
| `GITHUB_RATE_LIMITED` | 5 | 示した時刻の後に同じコマンドを実行する |
| `GITHUB_UNAVAILABLE` | 5 | 接続と `gh auth status` を確かめる |
| `GITHUB_ACCESS_DENIED`、`GITHUB_REQUEST_REJECTED`、`GITHUB_RESPONSE_INVALID` | 5 | 権限と `gh auth status`、示した GitHub の応答を確かめる |
| `GITHUB_EFFECT_UNKNOWN`、`GITHUB_CREATE_IDENTITY_UNKNOWN` | 6（partial） | GitHub の今の状態を確かめてから、`recovery` の手順に従う（作成なら `spec-dock scope import github <種類> <番号>`） |
