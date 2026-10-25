---
種別: 実装計画書（Issue）
ID: "iss-00429"
タイトル: "Add Canonical Catalog And Link"
関連GitHub: ["#429"]
状態: "draft"
最終更新: "2026-10-26"
依存: ["requirement.md", "design.md"]
親: ["epic-00424", "init-00423"]
---

# iss-00429 Add Canonical Catalog And Link — 実装計画

詳細: [Issue Plan Guide](../../../../../../docs/authoring/issue-plan.md)

## Planning Level

- 選択：`strict`（Epic の `plan.md` の指定）。
- 理由：利用者のチェックアウトに、カタログ（Git の worktree）とリンクを作り、`.git` の登録と除外の設定を書く。誤ると、仕様のファイル、ほかのworktreeの登録、ホストの Git の記録を壊すおそれがある。後の I-3、I-4、I-5、I-7、I-8 が使う契約（C3、C4、C5、C6、C11）を決める。
- risk factor：リンクの置き換え（実体を消さない）、`git worktree repair` と作り直し（ほかの登録に触れない）、マウントしたチェックアウト、新しいリポジトリの判定（移行していない仕様を隠さない）、GitHub の canonical の削除との区別、サンドボックスの中の書き込み、従来モードの回帰。
- 再評価条件：利用者の実データ（本物の spec-dock のリポジトリ、`~/.local/state/spec-dock/`、ツールの設定）や本物の GitHub に書く必要、従来の処理の変更、`design.md` の testability に挙げたほかの版3のテストの変更が要るとわかったら、止まって統括に聞き、`critical` を検討する。

## 目標

- `requirement.md` の AC-429-01〜20 を、テスト先行の単体テストと CLI のテスト、全体のテスト、`make lint` で満たす。
- `design.md` の公開の形（C3、C4、C5、C6、C11、`link_after_command`）を、後の Issue がそのまま使える状態にする。
- 実機（macOS の外付けのボリューム、Codex のサンドボックス、OrbStack の Linux、Docker のコンテナ）での確かめの結果を、報告書に書く。

## 順序・依存

1. 文書（この3つ）を書き、独立のレビューを受けて直す（S0）。
2. 純粋な規則（S1）と環境の判定（S2）を先に作る。S3 以降が使う。
3. C6 の関数とカタログの Git の操作（S3）→ ファイルの部品（S4）→ 排他と変更の束と `catalog_tree`（S5）→ カタログの観察と `require_linked`（S6）。
4. `canonical link`（S7）→ `link_after_command` と `worktree create`（S8）→ `canonical status`（S9）→ コマンドの一覧と配布資産（S10）。S10 の一覧は S7 の CLI のテストより先に入れてよい。
5. 全体の確かめ（S11）、実機の確かめ（S12）、実装のレビュー（S13）、最終の品質の関門（S14）、報告書と PR（S15）。

並行の注意：I-7（`iss-00434`、`canonical check`）が、別の worktree で同時に進む。`cli/catalog.py`、`commands/canonical_dispatch.py`、`static-inventory.json`、`docs/reference_cli.md`、コマンドの数のテストで衝突しうる。衝突したら `origin/main` をこのブランチにマージして解く（rebase しない）。I-7 が先に入っていたら、`application/canonical_check.py` の無視の3行を、この Issue の `GITIGNORE_LINES` に置き換え、同じ値であることをテストで確かめる。

## 実装step

各 step は、`tdd` の Red → Green → Refactor で進め、区切りでコミットする。

- **S0 文書**：`requirement.md`、`design.md`、`plan.md` を書き、この会話を知らないサブエージェントにレビューさせ、指摘を分析して直す。設計書で決まっていなかった判断は `ask` で統括に聞き、答え（下の「統括の判断」）を文書に入れた。
- **S1 純粋な規則**（`domain/canonical_layout.py`、`canonical_content.py`、`canonical_changeset.py`、`canonical_tools.py`）：場所と期待のリンクの値、`link_state` の各場合、無視の行の欠けと足し方、git の版の解析と比べ方、canonical の中身と形式の読み方、変更の束の正規化と JSON の往復と規則外の拒否、ファイル名、ツールの1行と `claude_allows`（`~`、相対、親、壊れた形、ファイルなし）。
- **S2 環境の判定**（`infra/runtime_environment.py`）：印のファイル（一時の `root`）と環境変数、git のパスと版（偽の実行器）、見つからない、読めない版。
- **S3 Git の呼び出し**（`infra/canonical_git.py`）：`run_catalog_git` の引数の形と環境、`read_only`、`pathspecs`、終了コード、時間切れの `uncertain`。各操作を一時のリポジトリで（worktree の一覧と管理ディレクトリ、lock、repair、`add` の3つの形、`ls-remote` の0と2、取得の対象の判定と追加、fetch、初期のコミットの作成と判定、push の `pushed` と `rejected`、変更の数と別名ファイル、未pushの数）。必ず失敗するフックと `commit.gpgSign=true`。
- **S4 ファイルの部品**（`infra/canonical_files.py`）：リンクの観察（ない、正しい、違う先、先がない、ディレクトリ、ファイル）、置く（作る、置き換える、実体なら止まる、置き換えの直前に実体へ変わったら止まる）、除外のファイルの追加（`info/` がない、末尾の改行、権限を保つ）、`.gitignore` の行の読み取り。
- **S5 排他、変更の束、`catalog_tree`**（`infra/catalog_lock.py`、`catalog_runtime.py`、`catalog_tree.py`）：別のプロセスが持つ間の待ちと失敗、`timeout` の範囲、束の原子的な書き込みと同じ名前の回避、`.runtime/` の作成、名前で探す（入れ子の位置によらない、2つは曖昧、`.runtime` と `.workbench` を探さない、リンクをたどらない、未追跡のディレクトリも見つける）。
- **S6 カタログの観察**（`application/canonical_catalog.py`）：`resolve_layout`（main、作業用のworktree、bare）、`observe_catalog` の表の各状態（`ready`、lock なし、`repair`（移動）、`readd`、`elsewhere`（存在する、しない）、`absent`、`occupied`、`foreign`）、`require_linked` の各コード、`catalog_changes`（排他、形式、束、例外のとき）。`canonical_errors.py` に13章のコードを足す。
- **S7 `canonical link`**（`application/canonical_link.py`、`CANONICAL_HANDLERS` への登録）：新しいリポジトリ、2つ目のクローン、作業用のworktree、2回目の `unchanged`、`--dry-run`、`git clean -ffdx` の後、移動の後（`repair`、`CANONICAL_MAIN_MOVED`、prune しない）、移行前のコミット、ふさがった場所とリンク、`elsewhere`、マウント（コンテナの印）、git 2.37、書けない場所（`CANONICAL_SANDBOX_DENIED` と、リンクだけのとき）、既定のブランチに仕様がある、4a と 4b、同時の作成（push の拒否）、浅いクローン、GitHub につながらない、書いた後の失敗の `partial`、StartLock が取れない、フックと署名、ツールの設定の警告、`.gitignore` の欠けの警告。
- **S8 ほかのコマンドから**（`link_after_command`、`application/canonical_worktrees.py`）：`worktree create` の後のリンク、`--dry-run`、`--expect-current` の `CANONICAL_NOT_IMPLEMENTED`、リンクの失敗と `START_LOCK_BUSY` の警告（結果の状態が変わらない）、版3の宣言のworktree。
- **S9 `canonical status`**：12の項目のキー、各状態と次の1手、警告、読むだけ（`tree_digest`）、git が古いとき、ツールの設定、`CODEX_SANDBOX` と書けないカタログ。
- **S10 コマンドの一覧と配布資産**：`cli/catalog.py`（46個、効果、前提、読むもの、書くもの、JSON）、`cli/options.py` の `_recovery_help`、`presentation`、配布資産の `.gitignore`、`docs/reference_cli.md`、`docs/README.md`、`README.md`、`static-inventory.json`（`sha256` と、変更の前の中身を `known_old_sha256` に）。コマンドの数のテスト（`design.md` の testability の表の5件）を直す。無視の3行の効き目のテスト（AC-429-04）。
- **S11 全体の確かめ**：`make lint`、`uv run pytest`。`git diff origin/main -- tests/` で変えた既存のテストを一覧にし、testability の表のほかにないことを確かめる。
- **S12 実機の確かめ**（`design.md` の testability の「実機の確かめ」）：macOS の外付けのボリューム、Codex のサンドボックス、Claude Code の1行（一時の `HOME` か一時の設定のファイル。利用者の設定は変えない）、OrbStack の Linux の仮想マシン（Git 2.43。この Issue のテストもそこで動かす）、Docker のコンテナ（ホストと別のパスにマウントする）。結果と「未確認」を報告書に書き、作った一時のものを消す。
- **S13 実装のレビュー**：`code-review` の観点で、規約と仕様を、独立した2つのサブエージェントにレビューさせ、指摘を `analyze-review-findings` で分析して直す。
- **S14 最終の品質の関門**：`origin/main` をマージし（PR #443 が入っていれば Epic の文書の正本はそれを含む）、すべてをコミットして通常の push をし、その SHA で `make lint` と `uv run pytest`、新しい2つのサブエージェントのレビュー（規約と仕様）。指摘を直したら、新しい SHA でやり直す。
- **S15 報告と PR**：`report.md` を書き、`github-pr-creator` で PR を作り、`github-pr-checks` で CI を確かめる。マージはしない。`work finish` は実行しない。

## 統括の判断（2026-10-26、Orca の `ask` の答え）

統括は、この答えを Epic の文書より優先する正本とし、同じ内容を Epic の `design.md` と `plan.md` に反映する。この Issue は Epic の文書を変えない。

### 1回目

- **A1**：従来の `direct_worktrees.py` と `work_start.py` は変えない。公開の関数 `link_after_command` を C3 の公開の形とする。canonical の `worktree create` は I-2 が `CANONICAL_HANDLERS` に登録し、今の作成の関数の後にこれを呼ぶ。canonical の `work start`（I-5）は、選択を記録して StartLock を放した後にこれを呼ぶ（統括が Epic の I-5 に書く）。
- **A2**：canonical モードの `worktree create` に `--expect-current` を付けたときは `CANONICAL_NOT_IMPLEMENTED`。選択の解決は I-4（統括が Epic の I-4 に書く）。
- **A3**：GitHub に canonical がなく、既定のブランチ（`origin/HEAD`、なければmainのチェックアウトの HEAD）のツリーに `spec-dock/initiatives` があるときは、書く前に `CANONICAL_NOT_MIGRATED`（終了コード3）で止まる。次の1手は移行の手順書（`scripts/migrate-to-canonical/README.md`）。メッセージに、GitHub に `spec-dock/canonical` がなく、既定のブランチに `spec-dock/initiatives` があることを書く（`CANONICAL_BASE_HAS_SPECS` は work start のためのもので使わない）。
- **A4**：ローカルのブランチ `spec-dock/canonical` があり、GitHub にないときは、新しい初期のコミットを作らず、ローカルのブランチからカタログを作る。(a) ローカルのブランチが `canonical link` 自身が作って push できなかった初期のコミット（親のない1つのコミットで、ツリーが5章の管理ファイルだけ）なら、新しいリポジトリの場合と同じく push する（拒否されたら GitHub のものを取得して使う）。(b) それ以外は push せず、警告 `CANONICAL_REMOTE_MISSING` を返す。(a) と (b) を、一時の bare のリポジトリでテストする。
- **A5**：`spec-dock/canonical` が、カタログの場所ではない、存在する別のworktreeでチェックアウトされているときは、`CANONICAL_PATH_OCCUPIED`（そのworktreeのパスと「`spec-dock/canonical` がそこでチェックアウトされている」こと）。
- **A6**：mainのチェックアウトの移動は、`git worktree repair <カタログ>` だけを行い、警告 `CANONICAL_MAIN_MOVED` を返す。
- **A7**：`canonical status` の `structure` と `--structure` は I-4、`sync`、`snapshot`、`changes` の `state.json` の部分（保留と統合の阻害）は I-3、`dashboard` は I-11 が足す。`git` は、I-2 では今の `PATH` の git を返し、登録簿の git は I-3 が足す。足さない項目は、項目の状態を「未対応」の値にし、`data` のキー（3章の表の項目）はすべて置く。
- **A8**：`canonical status` は、問題があっても `succeeded`（終了コード0）で返し、問題ごとに `warnings`（`details.next_step`）と各項目に示す。mainのチェックアウトが見つからない構成だけ `CANONICAL_UNSUPPORTED_LAYOUT` で `failed`。版3は I-1 のとおり `CANONICAL_NOT_MIGRATED`。
- **A9**：新しい警告のコードは5つ（`CANONICAL_TOOL_SETTING_MISSING`、`CANONICAL_TOOL_SETTING_UNKNOWN`、`CANONICAL_IGNORE_RULES_MISSING`、`CANONICAL_MAIN_MOVED`、`CANONICAL_REMOTE_MISSING`）。コード、出す場面、`details.next_step` の一覧を `design.md` に書く（13章）。統括が Epic の12章に足す。`canonical status` の問題には、ほかは12章のコードを使う。
- **A10**：`canonical link` は、書く手順（3〜5）を、クローンの StartLock の中で行う。ネットワークの処理（`ls-remote`、`fetch`、初期の push）は排他の外。取れなければ `START_LOCK_BUSY`（終了コード3）。`link_after_command` の中で `START_LOCK_BUSY` になったときは、呼び出し元の結果を変えず、警告と次の1手（`spec-dock canonical link` をもう一度）で返す。
- **A11**：`HELP_EFFECTS` の `canonical link` の文は、I-2 の時点の正しい内容（登録を除く）にし、I-3 が Epic の12章の文に直す。配布資産の `docs/reference_cli.md` に2つのコマンドの行を足し、`static-inventory.json` の `sha256` と `known_old_sha256` を直す。

### 2回目（作り直しと repair）

- **B1**：登録はあるがカタログがないときの作り直しは、`git worktree add -f -f <カタログ> spec-dock/canonical` の後に `git worktree lock` とし、`prune` と `unlock` は使わない。`git worktree prune` は、クローン全体の消えた登録（外れた外付けのボリュームのworktreeなど）を選ばずに消すため、SpecDock は prune を実行しない。`-f -f` は、`git worktree list --porcelain` で `spec-dock/canonical` をチェックアウトしている登録がちょうど1つで、そのパスが `<main>/spec-dock/.canonical` であり、ディレクトリがないときだけ使う。`spec-dock/canonical` がほかのパスの登録でチェックアウトされているときは、何も書かずに `CANONICAL_PATH_OCCUPIED` で止まる（そのパスが存在するときも、しないときも）。存在しないときの次の1手は「示した登録を確かめてから `git worktree remove` か `git worktree prune` を自分で実行し、もう一度 `spec-dock canonical link`」。テスト：カタログの登録だけが残っている（ほかの prunable な登録は消えない）、ほかの存在しないパスの登録でチェックアウトされている（止まる）。
- **B2**：`git worktree repair <カタログ>` が、同時に、ほかの作業用のworktreeの `.git` も直す（git の `repair_worktrees`。2026-10-26 に Git 2.54.0 で確認）ことを了承。`CANONICAL_MAIN_MOVED` の次の1手は「各作業用のworktreeで `spec-dock canonical link`（そのworktreeも動かしたなら、先にmainで `git worktree repair <パス>`）」。repair を行ったことは `effects` に入れ、git がほかのworktreeの `.git` も直すことがある、とメッセージに書く。

### 3回目（文書の独立レビューの後、2026-10-26）

文書の独立レビュー（blocker 1、major 7、minor 11）を分析し、判断が要る点と知らせる点を統括に確かめた。統括は、Epic の `design.md`（3章、5章の C6、9章、12章の表）に後で別の PR で反映する。そのほかの指摘は、Epic の契約を変えない範囲で、この Issue の判断で直した（下の「レビューの指摘の対応」）。

- **C1**：エージェントが `spec-dock/initiatives/…` へ移動して実行すると、`resolve_context` がカタログのworktreeを解決し、宣言がないので次の1手なしで止まる。新しいコード `CANONICAL_INSIDE_CATALOG`（終了コード3、次の1手「チェックアウトのルートで実行するか、`--project <チェックアウト>` を付ける」）で止める。判定は、解決したworktreeが `spec-dock/canonical` をチェックアウトし、ルートに `.spec-dock-canonical.json` があるときだけ。版3のリポジトリで振る舞いが変わらないことをテストで確かめる。
- **C2**：`canonical link` は、push が成功する前にローカルの参照を作らない。A4(a) は「ローカルのブランチの中身が親のない初期のコミットだけ（どう生じたかは問わない）」として実装し、テストはそのブランチを直接作る。
- **C3**：`require_linked` も、git が 2.38 より古いと `CANONICAL_GIT_TOO_OLD` で止める（カタログの観察が `git worktree list --porcelain -z` を使うため）。
- **C4**：Claude Code の判定は作業用のworktreeでだけ行い、`CLAUDECODE` は `tools` の項目に示すだけにする。
- **C5**：C6 の関数に `-c core.fsmonitor=false -c gc.auto=0 -c maintenance.auto=false` を足す（fsmonitor のフックと、fetch が誘発する gc の worktree の prune を動かさない。B1 を守るため）。I-3 と I-5 は同じ関数を使うので、そのまま引き継がれる。
- **C6**：作業用のworktreeから実行し、mainのチェックアウトの宣言が版4でないときは、mainのリンクを置かず、カタログの作成と除外と実行したworktreeのリンクを行い、新しい警告 `CANONICAL_MAIN_NOT_MIGRATED`（次の1手「mainのチェックアウトで移行後のコミットをチェックアウトしてから `spec-dock canonical link`」）を返す。`CANONICAL_NOT_MIGRATED` は止まるコードなので、警告に使い回さない。`canonical status` の `link` の項目も、同じコードと次の1手を示す。この状態で main の従来のコマンドが今までどおり動くことをテストで確かめる。
- **C7**：mainの移動の判定は、パスの文字列ではなく実体（samefile）で比べ、`repair` は、登録のパスか gitdir の先がこのプロセスから見えないときだけ行う。両方が見えて別の実体なら `CANONICAL_PATH_OCCUPIED` で止まる。
- **C8**：書き込みの可否の確かめを `ls-remote` の前に行う（Codex のサンドボックスは既定でネットワークがないので、作成が要るときに `CANONICAL_SANDBOX_DENIED` で止めるため）。

C6 の考え方（止まるコードを警告に使い回さない）に合わせて、`link_after_command` で、作ったworktreeの宣言が版4でないときの警告も、新しい `CANONICAL_CHECKOUT_NOT_MIGRATED` にした（この Issue の判断）。

### レビューの指摘の対応（文書の独立レビュー、2026-10-26）

| 指摘 | 判定 | 対応 |
|---|---|---|
| F-01 要件定義書が B1・B2 と食い違う | 妥当 | `requirement.md` を B1・B2 に合わせ、B1 のテスト（ほかの prunable な登録が残る、存在しないパスの登録で止まる）を AC-429-02、03 に入れた |
| F-02 A4(a) が起きない | 妥当 | C2 として統括に知らせ、言い直した |
| F-03 浅いクローンの新しいリポジトリで `--track` が失敗する | 実装は取得の対象を足していたが、文書が違った | 作り方のすべての行で、StartLock の中で `set-branches` を行う。AC-429-11 に新しいリポジトリを足し、テストを足した |
| F-04 書き込みの確かめが `ls-remote` の後 | 妥当 | C8。ネットワークの前に確かめ、テストを足した |
| F-05 repair の条件（安全） | 妥当 | C7。AC-429-20 とテストを足した |
| F-06 カタログの中から実行 | 妥当（Epic の抜け） | C1。AC-429-19 とテストを足した |
| F-07 I-3 の差し込み口 | 一部妥当 | `canonical status` の `sync` と `snapshot` を、I-3 が置き換える関数 `sync_item`、`snapshot_item` にした。`link_checkout` と `link_after_command` への `schedule: bool = True` は、既定値のある引数なので I-3 が足しても呼ぶ側は変わらない。使わない引数を今は置かない（lint の未使用の引数を避ける）。手順6、7の置き場は `design.md` 8章に書いた |
| F-08 Claude Code の1行の実地の確かめがない | 妥当 | S12 に入れた |
| F-09 `elsewhere` の次の1手 | 妥当 | 存在するときは別のブランチへの切り替え、存在しないときは `git worktree unlock` と `git worktree remove <パス>` を示す（Git 2.54.0 で確かめた） |
| F-10 `set-branches` が排他の外 | 妥当 | StartLock の中に移し、確かめ直してから足す |
| F-11 曖昧の扱いと ID の正規化 | 妥当 | `ScopeDirectoryAmbiguous` を `ValueError`（`PRECONDITION_FAILED`）にし、`find` が ID を5桁にそろえる |
| F-12 統括の判断にないずれ | 妥当 | (a) C3、(b) C4、(c) 10分の警告は `state.json` の `unpushed_since` を使う I-3 の担当（A7）と `design.md` に書いた |
| F-13 fsmonitor と gc | 妥当 | C5 |
| F-14 安全の細部 | 妥当 | (a) ENOENT だけを「ない」に、(b) `update-ref <ref> <新> <旧>`、(c) 別のブランチは戻す次の1手、(d) C6 |
| F-15 `link_after_command` | 妥当 | 例外も警告にすることを書いた。書くことがなければ StartLock を取らない。待ちの記述を「5秒で `START_LOCK_BUSY`」に直した |
| F-16 紛らわしい次の1手 | 妥当 | (a) サンドボックスの外は権限の確かめ、(b) 形式のファイルがないときの文、(c) 書くときの拒否を `CANONICAL_SANDBOX_DENIED` に、(d) AC-429-02 に明記 |
| F-17 AC の穴 | 妥当 | AC-429-03、05、10、13 に足した（bare は AC-429-14 の部品と `canonical status` のテストで確かめる） |
| F-18 文書どうしの整合 | 一部妥当 | 章の参照と手順の番号を直した。`reference_cli.md` の C45、C46 は末尾に置く（C 番号を振り直さないため。反論）。統括の判断を `plan.md` に置くのは I-1 と同じ形で、`design.md` から参照する（反論）。「未対応」の項目も `next_step: null` を持つ（実装のとおり）。`worktree create` のヘルプの記述は I-9 へ申し送る |
| F-19 実機の注意 | 妥当 | S12 に、別のパスでのマウントと、仮想マシンの Git 2.43 でのテストを入れた。2.38 は手元にないので未確認と書く |

## 検証

| 対象 | 方法 |
|---|---|
| AC-429-01〜13、16、18〜20 | `tests/cli_runtime/test_issue429_canonical_link.py`、`test_issue429_canonical_status.py`、`tests/integration/test_issue429_ignore_rules.py`、`tests/unit/**`（`design.md` の testability の対応表） |
| AC-429-14 | `tests/unit/infra/test_catalog_tree.py`、`test_catalog_lock.py`、`test_catalog_runtime.py`、`tests/unit/application/test_canonical_catalog.py` |
| AC-429-15（AC-15） | 変更の前の全体のテスト（`origin/main` = `41a4c57c0`）と同じテストが、testability の表の5件のほかは変更なしで通る。`git diff origin/main -- tests/` を報告書に書く |
| AC-429-17 | `make lint`、`uv run pytest` |
| negative test | ふさがった場所とリンク、置き換えの直前の実体、`elsewhere`、マウント、古い git、書けない場所、既定のブランチの仕様、4b、push の拒否、接続の失敗、書いた後の失敗、StartLock、形式が新しい、排他が取れない、壊れたツールの設定、規則外の変更の束のパス |
| rollback / migration | N/A（自動のテストはない）。理由：データの移行がなく、版3のリポジトリにはカタログもリンクも作らないため、戻すのは PR の `git revert` である。配布資産の `.gitignore` の3行が従来モードを壊さないことは、AC-429-04 と、`installation init` の後に `spec-dock/initiatives/` を作ってコミットする今のテストの全体で確かめる |

- テストは外のネットワークを使わない。`HOME`、`XDG_STATE_HOME` はいつも一時ディレクトリにする。
- security / privacy：ツールの設定は読むだけで、書かない。資格情報を扱わない（push と fetch は利用者の Git の設定に任せ、`GIT_TERMINAL_PROMPT=0` で端末で待たない）。エラーの出力は今の `redact` を通る。
- operability：`canonical status` が、問題ごとの次の1手を示す。`canonical link` の `effects` で、行ったことを示す。
- migration：配布資産の `.gitignore` と文書の値だけ。版3の利用側の `.gitignore` は `known_old_sha256` で `known-old` になり、`installation update` で上がる（I-9、I-10 が行う）。

## rollback

- マージの前：ブランチを捨てるか、コミットを revert する。
- マージの後で、後の Issue が C3〜C6、C11 を使っていない間：PR を `git revert` する。版3のリポジトリには、カタログもリンクも作られていない。
- 後の Issue がマージされた後：forward recovery で、この部品を直す PR を作る。契約の不足は、Epic の `design.md` とこの `design.md` を先に直す。
- 実機の確かめで作ったもの（一時のリポジトリ、仮想マシン、コンテナ、イメージ）は、確かめた後に消す。

## exit / handoff

- 完了の条件：AC-429-01〜20 をテストで確かめ、最終の品質の関門に合格し、`report.md` に証拠と実機の確かめの結果を書き、PR がマージできる状態（CI が通っている）で止まる。マージは人が行い、`work finish` は統括の指示で行う。
- 後の Issue への引き渡し：
  - I-3：手順5と8のあいだに手順6（登録簿と定期の実行）と7（基準）を足す（`canonical_link.py` の `link_checkout` の、最後の確かめの前）。`link_checkout` と `link_after_command` に `schedule: bool = True` を足し、`--no-schedule` に使う。`canonical status` の `sync_item`、`snapshot_item` を置き換え、`changes` の `holds` と `blocking`、`git` の登録簿の git、未pushが10分を超えたときの警告（R-C6）を足す。同期は `run_catalog_git`、`CatalogLock(timeout=0)`、`Changeset.from_json`、`read_format`、`format_writable`、`CANONICAL_ROOT_FILES`、`RuntimeEnvironment`（systemd と linger を足す）を使う。
  - I-4：`require_linked`、`CatalogTree`、`LinkedCatalog`、`canonical status --structure`、`worktree create --expect-current` などの選択の解決。
  - I-5：`require_linked`、`catalog_changes`、`staging_directory`、`link_after_command`（canonical の `work start` が、StartLock を放した後に呼ぶ）。
  - I-7：`GITIGNORE_LINES`、`EXCLUDE_LINES`。
  - I-8：`GITIGNORE_LINES`、`CANONICAL_ROOT_FILES`、`CANONICAL_BRANCH` を写し、テストで比べる。
- 残るリスク：Linux の Codex のサンドボックス（Landlock）での `os.access` と `flock`（実機で確かめられなければ未確認）、Claude Code の1行をユーザーの設定ファイルに書いたときの動き（Epic の未確認の事項）。
