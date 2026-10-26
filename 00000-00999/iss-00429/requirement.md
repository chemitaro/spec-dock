---
種別: 要件定義書（Issue）
ID: "iss-00429"
タイトル: "Add Canonical Catalog And Link"
関連GitHub: ["#429"]
状態: "draft"
最終更新: "2026-10-26"
親: ["epic-00424", "init-00423"]
---

# iss-00429 Add Canonical Catalog And Link — 要件定義

詳細: [Requirement Guide](../../../docs/authoring/requirement.md)

表示名：カタログとリンクを作る `canonical link` と、状態を示す `canonical status` を足す（Epic の I-2）

## 目的

`spec-dock canonical link` の1回で、どのチェックアウトからでも仕様が `spec-dock/initiatives/` に見える。状態を確かめられる。

- 材料：Epic の `plan.md` の「I-2 Add Canonical Catalog And Link」の節（価値、作るもの、受け入れ、注意、実機の確かめ）と、Epic の `design.md` の担当の章（2章の C3 に関わる部分、3章（登録と基準を除く。Git の版とマウントの確かめを含む）、4章、5章の C5・C6・C11 に関わる部分、9章、6章と12章の I-2 の行）。Issue をまたぐ契約は、Epic の `plan.md` の「Issue をまたぐ契約」の表に従う。
- 依存：I-1（`iss-00428`）。Planning Level：strict（理由は `plan.md`）。
- この Issue は、契約 C3（カタログとリンクの場所、正しいリンクの判定、無視の3行、`catalog_tree`、`link_after_command`）、C4（カタログの排他と変更の束の形式）、C5（canonical の中身、形式1）、C6（カタログに対する Git の呼び出しの関数）、C11（環境の判定。systemd と linger は I-3 が足す）の持ち主である。後の Issue（I-3、I-4、I-5、I-7、I-8）は、ここで作る部品を変えずに使う。
- Epic の文書で決まっていなかった点は、統括の判断（2026-10-26。`plan.md` の「統括の判断」）を正本とする。

## 背景

- Epic は、仕様の内容の正本を、既定のブランチと共通の祖先を持たない `spec-dock/canonical` ブランチに置き、クローンごとに1つのカタログ（mainのチェックアウトの `spec-dock/.canonical/` にある canonical のworktree）を作る。各チェックアウトの `spec-dock/initiatives` は、カタログを直接指すリンクにする（Epic の R-B1〜R-B3）。
- I-1 が、宣言の版4による canonical モードの判定と、振り分けの表（`CANONICAL_HANDLERS`、`REPOSITORY_INDEPENDENT_HANDLERS`）、エラーのコードの置き場（`application/canonical_errors.py`。`CANONICAL_NOT_LINKED` を含む）、状態の置き場の根（`infra/state_root.py`）を置いた。版4のリポジトリでは、`installation` と `workspace migrate` のほかのコマンドが `CANONICAL_NOT_IMPLEMENTED` で止まる。
- カタログとリンクがないと、仕様を読み書きする後の Issue（I-4、I-5）と、定期の同期（I-3）を始められない。この Issue は、カタログとリンクの用意と、その状態の表示と、後の Issue が使う部品（カタログの中の Scope の探し方、排他、変更の束、canonical の中身、カタログに対する Git の呼び出し、環境の判定）を作る。
- 関係者：
  - 利用者とエージェント：どのチェックアウトでも、`spec-dock canonical link` の1回で仕様が `spec-dock/initiatives/` に見え、足りない設定と次の1手が示されること（約束2、約束4、約束5）。
  - 後の Issue の実装担当：C3、C4、C5、C6、C11 の公開の形を、`design.md` だけで使えること。
  - 移行していないリポジトリ（版3）：今と同じに動くこと（AC-15）。

## 観測可能な要件

### R-429-01 カタログとリンクの場所（C3）

- mainのチェックアウトは、Git の共通ディレクトリの名前が `.git` で、その親の `.git` が共通ディレクトリそのものであるときの、その親である。そうでない構成（bare など）では、`CANONICAL_UNSUPPORTED_LAYOUT`（終了コード3）で止まる。
- カタログは `<main>/spec-dock/.canonical`、リンクは `<チェックアウト>/spec-dock/initiatives` である。リンクの値は、mainのチェックアウトでは `.canonical`、作業用のworktreeでは `<main>/spec-dock/.canonical` の絶対パスとする。リンクのリンクは使わない。
- **正しいリンク**とは、`spec-dock/initiatives` がシンボリックリンクで、値が上の値と同じで、たどった先の実際のパスがカタログの実際のパスと同じものをいう。

### R-429-02 `spec-dock canonical link`

どのチェックアウトから実行しても、次を順に行う（Epic の `design.md` 3章の手順1〜5と8。番号も Epic のまま使う。手順6の登録と手順7の基準は I-3 が足す）。何度実行しても結果は同じで、行ったことを `effects` に、利用者に残る作業を `warnings` に返す。

1. **前提**：宣言の版4（版3は I-1 のとおり `CANONICAL_NOT_MIGRATED`）、git が 2.38 以上（足りなければ `CANONICAL_GIT_TOO_OLD`）、mainのチェックアウトが見つかること（なければ `CANONICAL_UNSUPPORTED_LAYOUT`）。
2. **先に確かめる**（書く前にすべて）：マウントしたチェックアウトでないこと（`CANONICAL_FOREIGN_CHECKOUT`）、カタログの場所にカタログでないものがないこと（`CANONICAL_PATH_OCCUPIED`）、`spec-dock/canonical` がカタログの場所でないほかのパスの登録でチェックアウトされていないこと（そのパスが存在してもしなくても `CANONICAL_PATH_OCCUPIED`）、リンクを置くチェックアウトのリンクの場所に実体がないこと（`CANONICAL_LINK_OCCUPIED`。パスと中のファイルの数を示し、消さない）、書く場所にこのプロセスが書けること（`CANONICAL_SANDBOX_DENIED`。ネットワークを使う前に確かめる）。新しいリポジトリで、GitHub に canonical がなく、既定のブランチのツリーに `spec-dock/initiatives` があるときは、`CANONICAL_NOT_MIGRATED` で止まる。ここで止まるときは、何も書かずに `failed`（終了コード3。接続の失敗は `GITHUB_UNAVAILABLE`、終了コード5）で返す。
3. **カタログ**：Git の登録と場所から、何もしない、lock だけ、`git worktree repair <カタログ>`、作り直し（`git worktree add -f -f <カタログ> spec-dock/canonical` と lock。`git worktree prune` は使わない）、新しく作る、のどれかを行う。新しく作るときは、GitHub の canonical を取り込んで使う。GitHub になければ、ローカルのブランチを使い、それもなければ、形式1の管理ファイルだけを持つ親のないコミットを作って push する。
4. **除外の設定**：`<共通ディレクトリ>/info/exclude` に、無視の3行のうち足りない行を足す。
5. **リンク**：mainのチェックアウトと、実行したチェックアウトに、正しいリンクを置く。ただし、作業用のworktreeから実行し、mainのチェックアウトの宣言が版4でないときは、mainのリンクを置かず、警告 `CANONICAL_MAIN_NOT_MIGRATED` を返す（mainの従来のコマンドを壊さないため）。
8. **ツールの設定**：足りない設定を、正確な1行で `warnings` に返す（R-429-07）。

- 3〜5の途中で失敗したときは、それまでの効果を `succeeded`、残りを `not_attempted` とした `partial`（終了コード6）で返し、`recovery` に `spec-dock canonical link` を入れる。
- 書く手順は、クローンの StartLock の中で行う（取れなければ `START_LOCK_BUSY`）。書くことがなければ StartLock を取らない。
- `--dry-run` では、何も書かずに、行う予定を `planned` の効果で返す。

### R-429-03 SpecDock のほかのコマンドから（C3、R-B4）

- canonical モードの `worktree create` は、今の作成の処理の後に、作ったworktreeについて、`canonical link` と同じ手順を行う。リンクの手順の失敗（`START_LOCK_BUSY` と例外を含む）は、`worktree create` の結果を変えず、警告と次の1手として返す。作ったworktreeの宣言が版4でなければ、リンクせずに警告 `CANONICAL_CHECKOUT_NOT_MIGRATED` を返す。`--expect-current` を付けたときは、`CANONICAL_NOT_IMPLEMENTED` で止まる（選択の解決は I-4）。
- 同じ手順を、公開の関数 `link_after_command` として提供する。canonical の `work start`（I-5）が、選択を記録して StartLock を放した後に呼ぶ。
- 仕様を使う canonical モードのコマンド（I-4、I-5）のために、リンクとカタログが正しいことを確かめる部品を提供する。正しくなければ、自分では直さずに `CANONICAL_NOT_LINKED`（`recovery` に `spec-dock canonical link`）で止まり、マウントしたチェックアウトでは `CANONICAL_FOREIGN_CHECKOUT`、git が古ければ `CANONICAL_GIT_TOO_OLD` で止まる。
- エージェントが `spec-dock/initiatives/` の中（カタログのworktree）へ移動して SpecDock を実行したとき、宣言がないための止まり方を、`CANONICAL_INSIDE_CATALOG`（終了コード3、次の1手「チェックアウトのルートで実行するか、`--project <チェックアウト>` を付ける」）にする。判定は、解決したworktreeが `spec-dock/canonical` をチェックアウトし、ルートに `.spec-dock-canonical.json` があるときだけで、版3のリポジトリの振る舞いは変えない。

### R-429-04 `spec-dock canonical status`（読むだけ。R-B7）

- 次の項目を、`data` のキーとしてすべて返す：`catalog`、`link`、`exclude`、`access`、`tools`、`sync`、`changes`、`format`、`git`、`snapshot`、`dashboard`、`structure`。
- この Issue が中身を返すのは、`catalog`（場所、ブランチ、lock、HEAD、登録のパスとの一致）、`link`、`exclude`（`info/exclude` と、このチェックアウトの `spec-dock/.gitignore`）、`access`（このプロセスがカタログを読めるか、書けるか）、`tools`、`format`、`git`（今の `PATH` の git のパスと版）、`changes`（未保存の数、未pushのコミットの数と最も古い時刻、別名ファイル）である。`sync`、`snapshot`、`changes` の `state.json` の部分（保留と統合の阻害）は I-3、`dashboard` は I-11、`structure` は I-4 が足し、この Issue では、その項目の状態を「未対応」の値にする。
- 問題ごとに、次の1手を1つ示す。問題があっても、結果は `succeeded`（終了コード0）で、問題を `warnings`（`details.next_step`）と各項目に示す。mainのチェックアウトが見つからない構成では `CANONICAL_UNSUPPORTED_LAYOUT` で止まる。
- リポジトリ、カタログ、`.git`、GitHub に何も書かない。GitHub とリモートに問い合わせない。カタログに対する Git の呼び出しは `--no-optional-locks` で行う。

### R-429-05 無視の3行（C3）

- 次の3行を使う：`/spec-dock/.canonical/`、`/spec-dock/initiatives`、`!/spec-dock/initiatives/`。`spec-dock/initiatives` がシンボリックリンクのときだけ無視し、実体のディレクトリのときは中の新しいファイルを無視しない。
- `canonical link` が `<共通ディレクトリ>/info/exclude` に足す。配布資産の `spec-dock/.gitignore` に、`spec-dock/` からの相対の形（`/.canonical/`、`/initiatives`、`!/initiatives/`）で足し、`static-inventory.json` を直す。利用側の `spec-dock/`（この repo の dogfooding の workspace）は変えない（I-9、I-10）。

### R-429-06 カタログの排他と変更の束（C4）、canonical の中身（C5）、Git の呼び出し（C6）、環境の判定（C11）

- **排他**：カタログのディレクトリを読み取りで開いて `flock(LOCK_EX)` をかける。既定で10秒まで待ち、取れなければ `CANONICAL_LOCK_BUSY`（終了コード3）。ファイルを作らない。`StartLock` とは別のものとする。
- **変更の束**：`<カタログ>/.runtime/changesets/<UTC の時刻>-<乱数>.json` を、排他の中で、一時ファイルに書いてから `rename` で置く。形式は Epic の `design.md` 4章（版1、`origin` は `command` か `finish`、`paths` と `deletions` はカタログのルートからの相対パス）。作成の作業場所は `<カタログ>/.runtime/staging/`。
- **canonical の中身（形式1）**：ルートの `.spec-dock-canonical.json`（`{"format": 1}`）、`.gitignore`（`.runtime/` と `.workbench` の規則）、`README.md`。カタログに書く部品は、形式が1より大きいか読めないとき、書く前に `CANONICAL_FORMAT_UNSUPPORTED` で止まる。
- **Git の呼び出し**：カタログに対するすべての Git のコマンドを、1つの関数から、`-c core.hooksPath=/dev/null -c commit.gpgSign=false` と、`-c core.fsmonitor=false -c gc.auto=0 -c maintenance.auto=false`（fsmonitor のフックと、自動の gc による worktree の prune を動かさない。統括の判断 C5）を付けて呼ぶ。パスを渡すときは `--literal-pathspecs` と `--pathspec-from-file`、`--pathspec-file-nul` で渡す。読むだけの呼び出しには `--no-optional-locks` を付ける。
- **環境の判定**：OS、コンテナの印（`/.dockerenv`、`/run/.containerenv`、環境変数 `container`、`REMOTE_CONTAINERS`、`CODESPACES`）、git のパスと版を判定する。判定の結果は注入でき、テストで、どの OS の上でも各場合を確かめられる。

### R-429-07 ツールの設定（R-B6、Epic の9章）

- Codex：環境変数 `CODEX_SANDBOX` があり、このプロセスがカタログに書けないとき、`~/.codex/config.toml` の `[sandbox_workspace_write]` に足す1行 `writable_roots = ["<カタログ>"]` を示す。
- Claude Code：作業用のworktreeで実行したとき（環境変数 `CLAUDECODE` は `tools` の項目に示すだけで、判定の要否を変えない。統括の判断 C4）、`~/.claude/settings.json`、`<チェックアウト>/.claude/settings.json`、`<チェックアウト>/.claude/settings.local.json` を読むだけ読み、`permissions.additionalDirectories` にカタログかその親がなければ、`~/.claude/settings.json` に足す1行 `{ "permissions": { "additionalDirectories": ["<カタログ>"] } }` を示す。判定できないときは、判定できないと示す。
- mainのチェックアウトの中では、設定は要らない（示さない）。
- SpecDock は、ツールの設定のファイルを書き換えない。

### R-429-08 名前で Scope のディレクトリを探す（C3 の `catalog_tree`）

- カタログの中で、名前が `<ID>-<slug>` のディレクトリを、入れ子の位置によらずに探し、ちょうど1つ見つかったものを返す。2つ以上あれば、曖昧として止まる。未保存の新しい Scope も見つける（`git ls-files` を使わない）。
- シンボリックリンクをたどらず、`.` で始まる名前のディレクトリ（`.runtime`、`.workbench` など）の中を探さない。
- 呼び出しの経路では、リンクが正しいときだけカタログを開く（R-429-03）。

## スコープ

### 対象

- `canonical link`、`canonical status` のコマンド（`cli/catalog.py` の一覧、引数、ヘルプ）と、`CANONICAL_HANDLERS` への登録。
- canonical モードの `worktree create`（今の処理の後のリンク）と、`link_after_command`。
- `infra/canonical_git.py`（C6 と、カタログの worktree、lock、repair、作り直し、取得の対象、ls-remote、fetch、初期の canonical の作成）、`infra/catalog_lock.py`、変更の束を書く部品、`infra/catalog_tree.py`、`infra/runtime_environment.py`、リンクと除外のファイルの部品。
- 純粋な規則（場所、正しいリンクの判定、無視の行、git の版、変更の束、canonical の中身、ツールの設定の1行と判定）。
- エラーと警告のコード（`application/canonical_errors.py` に足す）。
- 配布資産 `spec-dock/.gitignore` の3行、`docs/reference_cli.md` の2つのコマンドの行、`static-inventory.json`。
- コマンドの数と一覧を確かめるテストの更新（44 から 46。I-7 の `canonical check` を取り込んだ後は47）。

### 対象外

- `canonical link` の手順6（登録簿と定期の実行）、手順7（基準）、`--no-schedule`、`canonical status` の `sync`、`snapshot`、`changes` の `state.json` の部分（I-3）。`dashboard`（I-11）。`structure` と `--structure`（I-4）。
- `canonical sync`、`accept`、`restore`、`resume`、`remove`（I-3）。`canonical check`（I-7）。
- 仕様を読むコマンドと書くコマンドの canonical の処理（I-4、I-5）。canonical の `work start` からの `link_after_command` の呼び出し（I-5）。
- 利用者向けの文書と規則の節（I-9）。利用側の `spec-dock/` の配布資産の更新（I-9、I-10）。

### 親契約として維持する境界

- 従来モード（版3）の処理と、`.meta.json` を読み書きするコード（`application/direct_worktrees.py`、`work_start.py` を含む）を変えない。版3の振る舞いを確かめるテストは、Epic の `design.md` の testability の「従来モードの回帰」に挙げたもの（コマンドの数と一覧、配布資産の一覧と値、文書の中身）のほかは変えない（AC-15）。
- 読むだけのコマンドは、リポジトリ、カタログ、`.git`、GitHub に何も書かない。
- `StartLock` と選択の記録の形式を変えない。利用者のツールの設定のファイルを書き換えない。
- テストと実機の確かめで、利用者の `~/.local/state/spec-dock/`、`~/.claude/settings.json`、`~/.codex/config.toml`、本物の GitHub、利用者のほかのリポジトリに触れない。

## 失敗・境界条件

- **リンクの場所に実体がある**（移行前のコミットなど）：何も書かずに `CANONICAL_LINK_OCCUPIED` で止まり、パスと中のファイルの数を示す。中身を消さない。
- **カタログの場所にカタログでないものがある**（カタログが別のブランチにいるときは、そのブランチへ戻す次の1手を示す）、または `spec-dock/canonical` がカタログの場所でないほかのパスの登録でチェックアウトされている（そのパスが存在するときも、しないときも）：`CANONICAL_PATH_OCCUPIED` で止まる。SpecDock は、ほかのworktreeにも登録にも触れない。
- **`git clean -ffdx` の後**：登録はあるがカタログがない。`git worktree add -f -f <カタログ> spec-dock/canonical` と lock で作り直す（統括の判断 B1。`git worktree prune` は、クローン全体の消えた登録を選ばずに消すので使わない。ほかの消えたworktreeの登録は残る）。保存済みのコミットは `.git` に残る。カタログが「ない」とするのは `lstat` が ENOENT を返したときだけで、権限の失敗は「ない」と扱わない。
- **mainのチェックアウトの移動の後**：カタログを `git worktree repair <カタログ>` で直し、`prune` しない。git は、動いていないほかの作業用のworktreeの `.git` も同時に直す。警告 `CANONICAL_MAIN_MOVED` で「各作業用のworktreeで `spec-dock canonical link`（そのworktreeも動かしたなら、先にmainで `git worktree repair <パス>`）」を示す（統括の判断 B2）。移動の判定は、パスの文字列ではなく実体で比べ、登録のパスか gitdir の先がこのプロセスから見えないときだけ `repair` する。両方が見えて別の実体なら、`CANONICAL_PATH_OCCUPIED` で止まる（統括の判断 C7）。
- **mainで移行前のコミットへ移った**：mainのリンクが実体のディレクトリに置き換わり、mainの宣言は版3になる。作業用のworktreeの `canonical link` は、mainのリンクに触れずに `CANONICAL_MAIN_NOT_MIGRATED` を警告し、`canonical status` も同じコードと次の1手を示す。mainのチェックアウトそのものは版3の宣言なので、そこでの `canonical` のコマンドは I-1 のとおり `CANONICAL_NOT_MIGRATED` で止まる（AC-08 の原因と次の1手は、作業用のworktreeから示す）。元のブランチに戻ってから、mainで `spec-dock canonical link` を実行すれば戻る。
- **マウントしたチェックアウト**（コンテナの印があり、カタログの Git の登録が指すパスが見えない）：`repair` も `prune` もせずに `CANONICAL_FOREIGN_CHECKOUT` で止まる。コンテナの印がなければ、mainのチェックアウトの移動として直す。
- **Git が古い**（2.38 より前）：何も書かずに `CANONICAL_GIT_TOO_OLD` で止まる。
- **サンドボックスの中**：書く必要のある場所に書けなければ、ネットワークを使う前に、書く前に `CANONICAL_SANDBOX_DENIED` で止まる（サンドボックスの外の単なる権限の不足なら、次の1手は権限の確かめ）。カタログと除外がそろっていて、リンクを置くだけなら通る。`os.access` が許しても書くときに拒否されたら（Linux の Landlock など）、`CANONICAL_SANDBOX_DENIED` の `partial` か `failed` で、同じ次の1手を示す。
- **新しいリポジトリ**（GitHub にも手元にも canonical がない）：形式1の管理ファイルだけを持つ親のないコミットを作って push する。2台が同時に作って push が拒否されたら、GitHub のものを取得して使う。既定のブランチ（`origin/HEAD`、なければ mainのチェックアウトの HEAD）のツリーに `spec-dock/initiatives` があるときは、空の canonical を作らず、`CANONICAL_NOT_MIGRATED` で止まる。
- **ローカルのブランチがあり、GitHub にない**：初期のコミットを新しく作らない。ローカルのブランチの中身が、親のない初期のコミット（ツリーが管理ファイルだけ）だけなら push する（拒否されたら GitHub のものを取得し、ローカルのブランチを元の値を確かめてから付け替えて使う）。`canonical link` は push が成功する前にローカルの参照を作らないので、push に失敗した後のもう一度の実行は、新しいリポジトリの経路で整う（統括の判断 C2）。それ以外のブランチなら push せず、ローカルのブランチからカタログを作り、警告 `CANONICAL_REMOTE_MISSING` を返す。
- **浅いクローン**（取得の対象に `spec-dock/canonical` がない）：GitHub に canonical があるときも、新しいリポジトリで作って push したときも、StartLock の中で `git remote set-branches --add origin spec-dock/canonical` を（重ならないように確かめ直してから）行い、追跡するブランチでカタログを作る。
- **`spec-dock/initiatives/` の中から実行した**：`CANONICAL_INSIDE_CATALOG` で止まり、チェックアウトのルートか `--project` を示す。
- **GitHub につながらない**：canonical の有無を確かめられないときは、何も書かずに `GITHUB_UNAVAILABLE`（終了コード5）で止まる。カタログがすでにあるときは、GitHub に問い合わせない。
- **途中で失敗した**：`partial`（終了コード6）で、効果ごとに `succeeded`、`failed`、`unknown`、`not_attempted` を示す。もう一度実行すれば続きから整う。
- **同じクローンの2つのチェックアウトから同時に実行した**：書く手順はクローンの StartLock の中で行う。取れなければ `START_LOCK_BUSY`（終了コード3）。
- **canonical の形式が新しい**：`canonical link` はカタログを作るが警告 `CANONICAL_FORMAT_UNSUPPORTED` を返し、カタログに書く部品は書く前に止まる。
- **フックと署名**：リポジトリの必ず失敗する `post-checkout` と `pre-push`、`commit.gpgSign=true` があっても、`canonical link` は成功する。

## 受け入れ条件

Epic の `plan.md` の I-2 の「受け入れ」と、統括の判断を、テストで確かめられる形にしたものである。テストは、一時ディレクトリの bare のリポジトリを `origin` にし、外のネットワークを使わない。

- **AC-429-01（AC-06）**：一時のリポジトリで、新しいクローン（最初の `canonical link` が canonical を作る）、2つ目の新しいクローン（GitHub の canonical を取り込む）、`git worktree add` のworktree（`canonical link` の1回の後）、`worktree create` のworktree（追加のコマンドなし）のそれぞれで、`spec-dock/initiatives/` から仕様を読み書きでき、同じクローンのチェックアウトのあいだで、書いた内容がすぐに見える。
- **AC-429-02（AC-08）**：`git clean -ffdx`、mainのチェックアウトの移動、移行前のコミット（実体の `spec-dock/initiatives` を持つコミット）への checkout の後、`canonical status` が原因と次の1手を示し、`canonical link`（移行前のコミットでは元のブランチに戻ってから）で、正しいリンクとカタログに戻る。移行前のコミットの原因と次の1手は、作業用のworktreeの `canonical status` で確かめる（mainは版3になるため）。`git clean -ffdx` の後の作り直しは `git worktree add -f -f` で行い、ほかの消えたworktreeの登録が残る。移動の後は `git worktree repair` で直し、`prune` しない（`.git/worktrees/` の登録の名前が変わらない）。移動の後の `canonical link` は `CANONICAL_MAIN_MOVED` を警告する。登録が同じ実体の別名のパスを指すだけのときは `repair` しない。
- **AC-429-03**：リンクの場所に実体があるとき、`canonical link` は `failed`（終了コード3、`CANONICAL_LINK_OCCUPIED`、パスと中のファイルの数）で止まり、チェックアウトと `.git` が変わらない（ツリーの要約で確かめる）。カタログの場所がふさがっているとき、カタログが別のブランチにいるとき、`spec-dock/canonical` がほかのパスの登録（存在するものと、存在しないもの）でチェックアウトされているとき、登録が別の存在するディレクトリを指すときも、`CANONICAL_PATH_OCCUPIED` で何も書かずに止まる。書いた後に失敗したときは `partial`（終了コード6）で、書いた効果が `succeeded`、残りが `not_attempted` になる。StartLock が取れないときは `START_LOCK_BUSY`（ネットワークの手順の効果があれば `partial`）で、書くことがなければ StartLock を待たない。
- **AC-429-04**：無視の3行は、シンボリックリンクの `spec-dock/initiatives` を無視し、実体のディレクトリの中の新しいファイルを無視しない（従来モードのリポジトリで、新しい仕様のファイルが `git status` に出る）。`canonical link` の後の `info/exclude` と、配布資産の `spec-dock/.gitignore` の両方で確かめる。
- **AC-429-05**：書けないディレクトリ（サンドボックスの代わり）で、`CODEX_SANDBOX` を設定し、カタログの権限を 555 にすると、作業用のworktreeの `canonical status` が `writable_roots = ["<カタログ>"]` の正確な1行を示す。共通ディレクトリ（`.git`）を 555 にすると、カタログの作成が要る `canonical link` は、`ls-remote` を呼ぶ前に、`CANONICAL_SANDBOX_DENIED` で何も書かずに止まる。共通ディレクトリとmainの `spec-dock` を 555 にしても、カタログと除外がそろっていて作業用のworktreeにリンクを置くだけのときは通る。書くときに拒否されたら、`CANONICAL_SANDBOX_DENIED` と次の1手を示す。
- **AC-429-06**：読むだけのコマンド（`canonical status`）の前後で、カタログ、チェックアウト、`.git` が変わらない。
- **AC-429-07**：git の版を 2.37 と注入すると、`canonical link` が何も書かずに `CANONICAL_GIT_TOO_OLD`（終了コード3）で止まる。
- **AC-429-08**：コンテナの印を注入し、カタログの Git の登録が指すパスを見えなくすると（mainのチェックアウトの移動で代わりにする）、`canonical link` が `repair` も `prune` もせずに `CANONICAL_FOREIGN_CHECKOUT` で止まり、`.git/worktrees/` が変わらない。コンテナの印がなければ、同じ状態を `repair` で直す。カタログを使う部品（R-429-03）も、同じ状態で `CANONICAL_FOREIGN_CHECKOUT` を返す。
- **AC-429-09**：2回目の `canonical link` は、何も変えずに `unchanged`（効果はすべて `unchanged`）で終わる。`--dry-run` は何も書かずに予定を返す。
- **AC-429-10**：新しいリポジトリで作った canonical のコミットは、親がなく、ツリーが形式1の管理ファイルだけである。2つのクローンが同時に作り、後の push が拒否されると、後のクローンは GitHub のものを使う。ローカルのブランチの中身が初期のコミットだけ（テストではそのブランチを直接作る）なら、`canonical link` が push して整う。中身のあるローカルのブランチがあって GitHub にないときは push せず、`CANONICAL_REMOTE_MISSING` を警告する。既定のブランチに `spec-dock/initiatives` があって GitHub に canonical がないときは、`CANONICAL_NOT_MIGRATED` で何も書かずに止まる。origin につながらないときは、`GITHUB_UNAVAILABLE` で何も書かずに止まる。
- **AC-429-11**：取得の対象に `spec-dock/canonical` がないクローン（`--single-branch`）で、GitHub に canonical があるときも、新しいリポジトリで作るときも、`canonical link` が取得の対象を1行だけ足し、追跡するブランチでカタログを作る。
- **AC-429-12**：必ず失敗する `post-checkout` と `pre-push` のフック、`commit.gpgSign=true` があっても、`canonical link` が成功する（新しいリポジトリの作成と、既存の canonical の取り込みの両方）。C6 の関数が、どの呼び出しにもフックと署名を外す設定を付け、読むだけの呼び出しに `--no-optional-locks` を付ける。
- **AC-429-13**：作業用のworktreeで、Claude Code の設定にカタログがないとき `canonical link` と `canonical status` が `additionalDirectories` の正確な1行を示し、設定にカタログかその親があるときは示さない。設定のファイルが壊れているときは判定できないと示す。mainのチェックアウトでは示さない。ツールの設定のファイルは変わらない。配布資産の `spec-dock/.gitignore` に無視の3行が足りないチェックアウトでは `CANONICAL_IGNORE_RULES_MISSING`（次の1手 `spec-dock installation update`）、canonical の形式が1より大きいか読めないときは `CANONICAL_FORMAT_UNSUPPORTED` を警告する。
- **AC-429-14**：C3 と C4 の部品が、テストで直接使える。`catalog_tree` は名前で Scope のディレクトリをちょうど1つ見つけ、2つあれば曖昧（`PRECONDITION_FAILED` になる値の誤り）として止まり、`.runtime` と `.workbench` の中とシンボリックリンクの先を探さない。カタログを使う部品は、正しくないリンクで `CANONICAL_NOT_LINKED` を返す。カタログの排他は、別のプロセスが持つ間 `CANONICAL_LOCK_BUSY` になる。変更の束は版1の形で、排他の中で原子的に置かれる。形式が1より大きいカタログには、書く前に `CANONICAL_FORMAT_UNSUPPORTED` で止まる。
- **AC-429-15（AC-15）**：版3の宣言では、すべてのコマンドが今と同じに動く。版3の振る舞いを確かめる今のテストが、許された変更（コマンドの数と一覧、配布資産の一覧と値、文書の中身）のほかは変更なしで通る。版3の `canonical link` と `canonical status` は `CANONICAL_NOT_MIGRATED` で止まる。
- **AC-429-16**：canonical モードの `worktree create` は、`--expect-current` があると `CANONICAL_NOT_IMPLEMENTED` で止まる。リンクの手順が失敗（`START_LOCK_BUSY` を含む）しても、`worktree create` の結果の状態と終了コードは変わらず、警告と次の1手 `spec-dock canonical link` が付く。
- **AC-429-17**：`make lint` と `uv run pytest` が通る。
- **AC-429-18**：mainのチェックアウトが版3の宣言のコミットにいるとき、作業用のworktreeの `canonical link` は、mainの `spec-dock/initiatives` に触れずに、カタログと除外とそのworktreeのリンクを整え、`CANONICAL_MAIN_NOT_MIGRATED` を警告する。mainの従来のコマンド（`scope list` など）は今までどおり動き、mainの `git status` に何も出ない。
- **AC-429-19**：カタログのworktreeの中（`spec-dock/initiatives/…`）から実行したコマンドは `CANONICAL_INSIDE_CATALOG`（終了コード3、`--project` を含む次の1手）で止まる。宣言のないふつうの Git のリポジトリでは、今と同じ `PRECONDITION_FAILED` で止まる。
- **AC-429-20**：mainのチェックアウトで、カタログの Git の登録と `.git` ファイルが、同じ実体の別名のパスを指すとき、`canonical link` は `repair` をせずに `unchanged` で終わり、`.git/worktrees/` が変わらない。

## 制約・前提

- Python 3.10 以上、macOS と Linux。Git 2.38 以上（テストの手元は 2.54.0、提供側の CI は `ubuntu-latest`）。
- テストは外のネットワークを使わない。リモートは一時ディレクトリの bare のリポジトリ、状態の置き場は `XDG_STATE_HOME` を一時ディレクトリに、`HOME` も一時ディレクトリにする（利用者のツールの設定を読まないため）。
- 層の置き場は `AGENTS.md` に従う（`domain/` は純粋な規則、`infra/` は Git とファイル、`application/` は手順、`commands/` は振り分け、`presentation/` は出力）。
- 版4のリポジトリは、この Issue の後も、`canonical link`、`canonical status`、`worktree create`、`installation`、`workspace migrate` のほかは `CANONICAL_NOT_IMPLEMENTED` で止まる（0.3.0 まで。Epic の計画のとおり）。
