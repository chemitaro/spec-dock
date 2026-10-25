---
種別: 計画書（Epic）
ID: "epic-00424"
タイトル: "Centralize Specs On Canonical Branch And GitHub Issues"
関連GitHub: ["#424"]
状態: "draft"
最終更新: "2026-10-25"
依存: ["requirement.md", "design.md"]
親: ["init-00423"]
---

# epic-00424 Centralize Specs On Canonical Branch And GitHub Issues — 計画

詳細: [Scope Layering Guide](../../../docs/authoring/scope-layering.md)

表示名：仕様の正本を `spec-dock/canonical` ブランチと GitHub Issue に集約する

## 目標

`requirement.md` の受け入れ条件 AC-01〜AC-18 を満たす SpecDock 0.3.0 を作り、spec-dock を canonical モードに切り替えて、運用を始める。実装は、Issue ごとに、別のworktreeで、この Epic の議論に参加していない実装担当のエージェントが行う。そのため、この計画書は、`requirement.md` と `design.md` とあわせて読めば、ほかの資料なしで各 Issue を始められるように書く。

## 実装担当への共通の指示

各 Issue の担当は、始める前に次を読む。

1. リポジトリの `AGENTS.md`（提供側の `src/spec_dock/` と利用側の `spec-dock/` の区別、層の置き場、テストの置き場、コミットとPRの規則）。
2. `.agents/skills/spec-dock/SKILL.md`（SpecDock の CLI の使い方）。
3. この Epic の `requirement.md`（R-* と AC-*）、`design.md`（担当する章と、6章の表の担当の行）、この計画書（担当する Issue の節と「Issue をまたぐ契約」）。
4. 必要に応じて、調査の記録 `artifacts/20261025t080353z-research-verified-git-github-behaviors.md`。

作業のしかた：

- Issue ごとに、作業用のworktreeとブランチを1つ使い、PRを1つ作る。`spec-dock work start <Issue の ID>` で始め、`spec-dock work finish` で終える。
- 実装の間、spec-dock のリポジトリは従来モード（宣言の版3）のままである。仕様の文書は、今までどおりコードと一緒にコミットする。
- 最初に、その Issue の `requirement.md`、`design.md`、`plan.md` を、この計画書の節から書く。Epic の目的、Issue の分け方、Issue をまたぐ契約は変えない。変える必要を見つけたら、推測で埋めずに止まり、Epic の文書の変更を提案する（Scope Layering Guide）。
- テストは、外のネットワークを使わない。GitHub は偽の `gh` で、リモートは一時ディレクトリの bare のリポジトリで置き換える（`design.md` の testability）。
- 毎回、`make lint` と `uv run pytest` を通す。従来モードの回帰（AC-15）を壊してはならない。版3の振る舞いを確かめるテストは変えない。変えてよいテストは、`design.md` の testability の「従来モードの回帰」に挙げたものだけである。
- canonical モードの途中の Issue では、まだ作っていないコマンドの処理が残る。そのときは、`CANONICAL_NOT_IMPLEMENTED`（終了コード3、`recovery` に「SpecDock 0.3.0 を待つ」）で止めてよい。I-9 で、これが残っていないことを確かめる（`design.md` の G7）。
- してはならないこと：
  - 利用者のツールの設定（`~/.claude/settings.json`、`~/.codex/config.toml` など）を変える。
  - 本物の spec-dock のリポジトリで、I-10 より前に `canonical` のコマンドを実行する（版3なので止まるはずだが、試さない）。
  - 本物の GitHub に、ラベル、sub-issue、依存、`spec-dock/canonical` ブランチを作る（I-10 の切り替えでだけ行う）。
  - 利用者の `~/Library/LaunchAgents/` と `~/.config/systemd/user/` に、実機の確かめ以外でジョブを置く。実機で確かめるときは、別の名前（例 `local.specdock.test.<Issue>`）のジョブを、内蔵のディスクの一時ディレクトリの plist から読み込み、別の状態の置き場（`--state-root` に一時ディレクトリ）を使い、終わったら `launchctl bootout` で外す。
  - 利用者の本物の状態の置き場（`~/.local/state/spec-dock/`）に、テストのスナップショットや登録簿を書く。テストと実機の確かめでは、いつも環境変数 `XDG_STATE_HOME` を一時ディレクトリにし、`canonical sync` には `--state-root` も一時ディレクトリで渡す（ふつうのコマンドは `XDG_STATE_HOME` から状態の置き場を求めるため）。
  - Linux の実機の確かめで、利用者の `gh` の資格情報を仮想マシンやコンテナに写す。作った仮想マシン、コンテナ、取得したイメージは、確かめた後に消す（`design.md` の testability の「Linux の実機」）。
- コミットは、AGENTS.md のとおり、日本語の Conventional Commits にする。PRはマージできる状態で止め、マージは人が行う。PRの検査が通っていないPRを、マージできる状態として渡さない。

## 順序・依存

### Issue の一覧

| 番号 | 題名（作成時の英語の題名 / slug） | 担当する設計の章 | 依存 | Planning Level |
|---|---|---|---|---|
| I-1 | Add Canonical Mode And GitHub Structure Snapshot / `canonical-mode-structure` | 1、2（構造のスナップショットを含む）、6章の I-1 の行 | なし | strict |
| I-2 | Add Canonical Catalog And Link / `canonical-catalog-link` | 3（登録と基準を除く。Git の版とマウントの確かめを含む）、4、9、6章の I-2 の行 | I-1 | strict |
| I-3 | Add Periodic Canonical Sync / `canonical-periodic-sync` | 5（launchd、systemd、常駐のプロセス、周期の手順7のスナップショットの更新）、3章の登録と基準と `canonical remove` | I-2 | strict |
| I-4 | Read Scopes From GitHub In Canonical Mode / `canonical-scope-read` | 6章の I-4 の行 | I-1、I-2 | standard |
| I-5 | Write Scopes To GitHub In Canonical Mode / `canonical-scope-write` | 6章の I-5 の行 | I-3、I-4 | strict |
| I-6 | Accept Japanese Titles In Canonical Mode / `canonical-japanese-titles` | 7 | I-5 | standard |
| I-7 | Add Default Branch Spec Check And Workflow / `canonical-branch-check` | 8 | I-1 | standard |
| I-8 | Add Throwaway Canonical Migration Script / `canonical-migration-script` | 11 | I-1、I-2、I-7 | strict |
| I-9 | Integrate Agent Rules Docs And Release / `canonical-rules-docs-release` | 10、12、testability | I-3〜I-8、I-11 | standard |
| I-10 | Migrate Spec Dock To Canonical Storage / `spec-dock-canonical-cutover` | 移行・互換性・rollback | I-9 | strict |
| I-11 | Regenerate Dashboard From Structure Snapshot / `canonical-dashboard` | 13 | I-3、I-4 | standard |

- 番号は足した順で、進める順は下の「進め方」の図のとおりである（I-11 は2026-10-25 に足した。I-9 より前に終える）。
- 題名は、今の CLI が英数字しか受け付けないため、英語で作る（requirement.md の合意）。
- Planning Level は、失敗したときの影響と戻しにくさで選んだ。I-2、I-3、I-5 は利用者の仕様のファイルを書き、I-8 と I-10 は GitHub に大量に書き、既定のブランチを変えるので strict にした。I-1 は、すべての Issue が使う構造のスナップショット（C10）と、次の Epic が読む形式を決めるので strict にした。

### 進め方

```text
I-1 ─┬─ I-2 ─┬─ I-3 ─┐
     │       └─ I-4 ─┴─┬─ I-5 ── I-6 ─┐
     │                 └─ I-11 ───────┤
     ├─ I-7 ──────────────────────────┼─ I-9 ── I-10
     └─ (I-2 と I-7 の後) I-8 ─────────┘
```

- I-1 の後は、I-2 と I-7 を並べて進めてよい。I-2 の後は、I-3 と I-4 を並べてよい。
- I-8 は、canonical の中身（C5、I-2）と、検査のワークフローと版のファイル（C7、I-7）を使うので、両方の後に始める。
- I-5 は、カタログの排他と変更の束（I-2）、同期の状態と、すぐの実行の頼み方（I-3）、読む側の部品（I-4）を使う。
- I-11 は、周期の手順7（I-3）と、着手の判定の部品（I-4）を使うので、両方の後に始める。I-5 と並べて進めてよい。
- I-9 は、I-3〜I-8 と I-11 のすべての後に始める。
- I-9 で全体をつないで確かめ、版を 0.3.0 にする。I-10 は、0.3.0 を利用者の環境に入れた後に行う。

### Issue をまたぐ契約

各契約は、持ち主の Issue が `design.md` のとおりに作り、使う側の Issue は変えずに使う。変える必要があれば、Epic の `design.md` を先に変える。

| 契約 | 持ち主 | 使う側 | `design.md` |
|---|---|---|---|
| C1 構造の表し方（種類のラベル、本文の slug の印、ID の作り方）と `StructureSnapshot`、`ScopeNode`、GitHub の呼び出しの部品 | I-1 | I-4、I-5、I-6、I-8 | 2章 |
| C2 宣言の版4とモードの判定、`dispatch()` の振り分けの入口 | I-1 | すべて | 1章 |
| C3 カタログとリンクの場所、正しいリンクの判定、無視の3行、`CANONICAL_NOT_LINKED`、名前で Scope を探す `catalog_tree` | I-2 | I-3、I-4、I-5、I-8 | 2章、3章 |
| C4 カタログの排他と、変更の束の形式（`origin` を含む） | I-2 | I-3（読む）、I-5（書く） | 4章 |
| C5 canonical の中身（形式1の管理ファイル） | I-2 | I-3、I-8 | 5章 |
| C6 カタログに対する Git の呼び出しの関数（フックと署名を外す） | I-2 | I-3、I-5 | 5章 |
| C7 版のファイルと、検査のワークフローの見本、`specdock-ci-check.sh` | I-7 | I-8（`cut`）、I-9、I-10 | 8章 |
| C8 エラーのコードと次の1手、結果の状態の規則 | 各コマンドの持ち主 | I-9（一覧の確認） | 12章 |
| C9 状態の置き場（根、登録簿、`state.json` の形式と意味、基準）と、すぐの実行の頼み方（launchd、systemd、常駐のプロセス） | I-3 | I-2（`status` の同期の項目は I-3 が足す）、I-5（`work finish`）、I-11（`dashboard` の項目） | 5章 |
| C10 構造のスナップショット（置き場、`snapshot.json` と `probe.json` の版1の形式、`ensure_fresh` と3つの新しさの段階、書き込みの反映、書けないときのメモリーの上の扱い） | I-1 | I-3（周期の手順7）、I-4、I-5、I-11、次の Epic（epic-00425） | 2章 |
| C11 環境の判定（OS、コンテナ、git の版、systemd のユーザー、linger）と、その注入の仕方 | I-2（systemd と linger は I-3 が足す） | I-3、I-9 | 3章、5章 |

- I-8 の移行のスクリプトは、パッケージを読み込まない1つのファイルなので、C1、C3（無視の3行）、C5、C7 の値を写して持つ。写した値が同じであることを、I-8 のテストで、パッケージの定数と比べて確かめる。

## 実装step

各 Issue の節は、その Issue の要件定義書の材料である。「受け入れ」は、その Issue の受け入れ条件にそのまま使う。

### I-1 Add Canonical Mode And GitHub Structure Snapshot

- **価値**：canonical モードの土台になる、モードの判定と、GitHub の構造の読み書きができる。構造は一括で取得して使い回し、GitHub に負荷をかけない。利用者から見える変化はまだない。
- **作るもの**：
  - `application/project_context.py` の宣言の読み取りを、版3と4の受け付けとモードの判定に変える（`design.md` 1章）。`dispatch()` に、モードによる振り分けの入口と、リポジトリによらないコマンドの振り分けの入口を作る。
  - 6章の I-1 の行：`workspace migrate` の版4での拒否、`installation init` の版4の宣言、`installation show`、`update`、`uninstall` の版3と4の受け付け。配布資産 `workspace.json` を版4にする。
  - `infra/github_structure.py`：2章の GraphQL の全体の読み取り（3つの種類のラベルを1回で）、変わったかの確かめ（条件付きの要求。304 を状態行で判定）、REST の一部の読み取りと書き込み。状態コードの扱い、レート制限、順に呼ぶこと、書き込みの間の1秒。
  - `infra/github_snapshot.py`：構造のスナップショット（C10）。置き場と排他、`snapshot.json` と `probe.json`、`ensure_fresh` と3つの新しさの段階、`decision` の読み直し、書き込みの反映（取り直しの途中の書き込みを消さない）、書けないときのメモリーの上の扱い。
  - `domain/canonical_structure.py`：`StructureSnapshot`、`ScopeNode`、本文の印の解析（`\r\n` と、本文のどこにあってもちょうど1つ）と生成、ラベルからの種類の判定、階層と種類の規則の検査、循環の検査（今の `domain/dependency_vnext.py` の規則を使う）。
  - テスト用の偽の `gh` に、上の API と条件付きの要求を足し、受けた要求を記録できるようにする。
- **受け入れ**：
  - 版3の宣言では、すべてのコマンドが今と同じに動く（版3の振る舞いのテストが変更なしで通る）。
  - 版4の宣言を読むと canonical モードと判定し、版5は今と同じく止まる。`workspace migrate` は版4で止まり、宣言を書き換えない。
  - 偽の `gh` の上で、全体の取り直しが、ラベル、親子、依存、印から正しいスナップショットを作り、規則の違反（種類のラベルが2つ、印がない、印が2つ、Epic の親が Issue、循環）を異常として返す。Scope でない依存先は `external` に入る。
  - `ensure_fresh` が、2章の表のとおりに確かめと取り直しを決める（時刻を注入して、60秒、5分、30分の境を確かめる）。304 のときは取り直さず、主のレート制限を消費する要求を送らない。取り直しに失敗したときは `ETag` を進めない。
  - 取り直しの途中に書き込みの反映があっても、その反映が消えない。状態の置き場に書けないとき、メモリーの上で動き、失敗しない。
  - `sub_issue_id` と `issue_id` に、番号ではなく Issue の id（数値）を送る（テストで送った本文を確かめる）。
  - 親の取得の404を「親なし」、ラベルの取得の404を「ラベルなし」として扱う。403 と `retry-after` の応答で、読み取りは待って再試行し、書き込みは `GITHUB_RATE_LIMITED` で止まる。1つのコマンドの中の書き込みの間が1秒以上ある（注入した時計で確かめる）。
- **注意**：従来モードの処理と `.meta.json` の読み書きのコードを変えてはならない。

### I-2 Add Canonical Catalog And Link

- **価値**：`spec-dock canonical link` の1回で、どのチェックアウトからでも仕様が `spec-dock/initiatives/` に見える。状態を確かめられる。
- **作るもの**：
  - `canonical link`（`design.md` 3章の手順1〜5と8。手順6の登録と7の基準は I-3 が足す）と、`canonical status`（同期の項目は I-3 が足す。ここでは「未対応」と返してよい）。
  - `infra/canonical_git.py` のうち、Git の呼び出しの関数（C6）、worktree、lock、repair、除外、ls-remote、fetch、新しいリポジトリでの初期の canonical の作成（2台の同時の作成を含む）。
  - `infra/catalog_lock.py` と、変更の束を書く部品（4章）。`.runtime/` と、作成の作業場所。
  - `infra/catalog_tree.py`：名前で Scope のディレクトリを探す。リンクは「正しいリンク」だけを受け付ける。
  - `worktree create` と `work start` の後のリンク（3章「SpecDock のほかのコマンドから」。登録は I-3 の後に同じ経路で効く）。
  - ツールの設定の判定と、示す1行（9章）。サンドボックスの中での書き込みの可否の確かめと `CANONICAL_SANDBOX_DENIED`。
  - `infra/runtime_environment.py`（C11）：OS、コンテナの印、git の版の判定。注入できるようにする。`canonical link` の前提の `CANONICAL_GIT_TOO_OLD` と、マウントしたチェックアウトの `CANONICAL_FOREIGN_CHECKOUT`（3章の手順2。`repair` と `prune` の前に止まる）。
  - 配布資産 `spec-dock/.gitignore` への無視の3行の追加と、`static-inventory.json` の更新。
- **受け入れ**：
  - 一時のリポジトリで、新しいクローン、`git worktree add` のworktree、`worktree create` のworktreeのそれぞれで、仕様を読み書きできる（AC-06）。
  - `git clean -ffdx`、mainのチェックアウトの移動、移行前のコミットへの checkout の後、`canonical status` が原因と次の1手を示し、`canonical link` で戻る（AC-08）。移動の後は、`git worktree repair` で直し、`prune` しない。
  - リンクの場所に実体があるとき、何も書かずに `failed` で止まり、何も消さない。書いた後に失敗したときは `partial`（終了コード6）で、効果を正しく示す。
  - 無視の3行は、リンクを無視し、実体のディレクトリの中の新しいファイルを無視しない（従来モードのリポジトリで、新しい仕様のファイルが `git status` に出る）。
  - 書けないディレクトリ（サンドボックスの代わり）で、`canonical status` が `writable_roots` の正確な1行を示し、カタログの作成が要る `canonical link` は `CANONICAL_SANDBOX_DENIED` で止まる。リンクだけが要るときは通る。
  - 読むだけのコマンドが、カタログと `.git` を変えない。
  - git の版を 2.37 と注入すると、`canonical link` が何も書かずに `CANONICAL_GIT_TOO_OLD` で止まる。
  - コンテナの印を注入し、カタログの登録が指すパスを見えなくすると（マウントの代わり）、`canonical link` が `repair` も `prune` もせずに `CANONICAL_FOREIGN_CHECKOUT` で止まり、`.git/worktrees/` の記録が変わらない。コンテナの印がなければ、同じ状態を mainのチェックアウトの移動として `repair` で直す。
- **実機の確かめ**：macOS で、外付けのボリュームの一時のリポジトリを使い、リンクと、Codex のサンドボックス（`codex sandbox -- spec-dock canonical status` など）での判定を確かめる。Linux の仮想マシン（OrbStack）で、リンク、`flock`、書き込みの可否の判定を確かめる。Docker のコンテナに一時のリポジトリをマウントして、`CANONICAL_FOREIGN_CHECKOUT` で止まり、ホスト側の記録が変わらないことを確かめる。結果は報告書に書く。

### I-3 Add Periodic Canonical Sync

- **価値**：保存、取り込み、push が、人もエージェントも意識せずに、60秒ごとに行われる。競合しても、GitHub が書き換えられても、編集は失われない。
- **作るもの**：
  - `canonical sync`（`--registered` と `--state-root` を含む。リポジトリによらない振り分け）、`canonical accept`、`canonical restore`、`canonical resume`、`canonical remove`（`design.md` 5章と3章）。
  - 状態の置き場（C9）：根、登録簿、`state.json`、ログの切り替え。
  - 保存するパスの選び方、保留（秘密情報はトークンの全体の形）、競合の段からの解決の計画、別名ファイルの名前は、`domain/` の純粋な関数にする。時刻と PC名は注入する。
  - 一時のインデックスでの保存、`merge-tree` による統合（終了コード0、1、2以上の扱い）、`commit-tree` と `merge --ff-only`、push、書き換えと削除の検出と一時停止（`infra/canonical_git.py`）。
  - 定期の実行の選び方（5章。systemd のユーザーの判定の試し直しと、linger の判定を C11 に足す）。launchd、systemd、常駐のプロセス（`--loop`、`--detach`、`runner.lock`、`runner.json`、`kick`、SIGTERM での止まり方）の登録、解除、すぐの実行。`canonical link` の手順6（登録と直後の1回の実行の確かめ、push の認証の確かめ、linger と起動し直しの1行の案内）と7（基準）。
  - 周期の手順7のうち、`ensure_fresh(repository, cycle)` の呼び出し（C10 の部品を使う。ダッシュボードの作り直しは I-11 が足す）。
  - `canonical status` の同期、`git`、`snapshot` の項目。
- **受け入れ**：
  - 2つのクローンで、同じファイルを変えて両方で `sync` すると、両方に先着の版と別名ファイルが残り、競合のマーカーがない（AC-03）。変更と削除の競合では、変更が残る。拡張子のないファイルと `.` で始まるファイルの別名が、規則どおりになる。
  - 25件の削除は保留され、push されない（AC-10）。`accept --deletions` の後は保存される。`restore` で戻る。`origin: command` の束の削除は保留されず、`origin: finish` の束の削除は保留される。
  - bare のリポジトリで canonical を強制 push で書き換えると、`sync` は取り込まずに一時停止する。ブランチを消したときも、共通の祖先のない履歴のときも、一時停止する（AC-11）。`resume` で、定めたとおりに再開する。カタログを `git clean -ffdx` で消して作り直した後も、基準が残り、検出が働く。
  - 編集中のファイルに当たる取り込みは、何も壊さずに次の周期へ持ち越し、`blocking` に記録する。
  - 必ず失敗する `pre-commit`、`post-checkout`、`post-merge`、`pre-push` と、`commit.gpgSign=true` があっても、同期が成功する。
  - 書きかけの束を保存しない（排他のテスト）。誰かがカタログで `git add` していても、統合が止まらない。
  - 登録簿と状態の置き場のパスが、`XDG_STATE_HOME` のない環境（定期の実行の代わり）でも、`canonical link` のときと同じになる。
  - `canonical remove` は、未保存の変更か、`.runtime/` 以外の無視されたファイルがあると止まり、`--yes` がないと何もしない。
  - 常駐のプロセスは、2つ目が終了コード0で何もせずに終わり、`kick` ですぐに周期を動かし、SIGTERM で周期を終えてから止まる。環境の判定を注入して、macOS、systemd の Linux、systemd のない Linux で、正しい仕組みが選ばれる。systemd の判定は「Failed to connect to bus」の後に試し直す。
  - 構造が変わっていないとき、1周期が送る GitHub への要求は、304 の確かめだけである（AC-16 の一部）。GitHub につながらなくても、カタログの保存と push の結果は変わらない。
  - 最初の周期で `push --dry-run` を行い、認証の失敗を `push_auth` に記録して、`canonical status` が次の1手を示す。
- **実機の確かめ**：macOS の launchd（外付けのボリュームと内蔵のディスクの両方、利用者の `gh` での push、プライバシーの保護の案内。テスト用の別の名前のジョブと、別の状態の置き場で行う）。Linux の systemd のタイマー（OrbStack の Ubuntu の仮想マシン。一時の bare のリポジトリを相手に、AC-02、AC-03、AC-13 の代わりを確かめる）。systemd のないコンテナ（Docker。中でクローンした一時のリポジトリで、常駐のプロセスと、起動し直しの後の `canonical link`）。確かめられなかったことは、報告書と `design.md` の「未確認の事項」に残す。

### I-4 Read Scopes From GitHub In Canonical Mode

- **価値**：canonical モードで、Scope とその周りを読むコマンドが、すべて動く。
- **作るもの**（`design.md` 6章の I-4 の行）：`scope show`、`scope list`、`dependency list`、`dependency check`、`artifact list`、`artifact show`、`active show`、`active set`、`active clear`（`spec-dock/active/` のリンクの先をカタログからの相対で作る）、`branch show`、`branch create`、`branch switch`、`worktree list`、`worktree show`、`worktree bootstrap`、`worktree remove`（カタログの保護）、`workbench copy`（拒否）、`workspace sync`、`workspace validate`、`workspace doctor` の canonical の処理。構造は、すべて `ensure_fresh(display)` のスナップショットから読む（C10）。`workspace sync --source github` と `dependency check --source github` は全体を取り直し、`--source local` は止まる。`work start` とダッシュボード（I-11）が使う、スナップショットからの着手の判定の部品。
- **受け入れ**：
  - 偽の `gh` と一時のカタログで、各コマンドが GitHub の題名と状態と、ディレクトリの場所と、スナップショットの取得の時刻を示す（R-E4）。
  - 構造が変わっていないとき、`scope show` と `scope list` を続けて実行しても、304 の確かめのほかに GitHub への要求を送らない（AC-16 の一部）。GitHub につながらないときは、古いスナップショットで示し、`GITHUB_SNAPSHOT_STALE` を警告に入れる。
  - 作業用のworktreeで、`active set` の後の `spec-dock/active/` のリンクが、その Scope のディレクトリを開く。
  - `workspace validate` が、6章の検査の項目をすべて見つける。入れ子のずれは警告で、`scope move <ID>` を次の1手に示す。
  - `workspace validate --ci`、`workspace sync --source local`、`workbench copy`、カタログを対象にした `worktree remove` は、案内付きで止まる。
  - 読むだけのコマンドは、何も書かない（カタログと `.git` の変化がないことを確かめる）。

### I-5 Write Scopes To GitHub In Canonical Mode

- **価値**：canonical モードで、Scope の作成、取り込み、題名の変更、親の変更、完了、削除、依存の変更、Artifact の作成、作業の開始と終了ができる。
- **作るもの**（`design.md` 6章の I-5 の行）：`scope create`、`scope import github`、`scope edit`、`scope move`（新設）、`scope close`、`scope reopen`、`scope delete`、`dependency add`、`dependency remove`、`artifact create`、`artifact import file`、`work start`（作業中の印と、移行前の基点の拒否）、`work finish`（保存の確認）。作成時に、前付けの `タイトル:` と `親:` の行を除く。
- **受け入れ**：
  - 偽の `gh` で、各コマンドが `design.md` の順に GitHub に書き、カタログには排他の中で書いて変更の束を残す。
  - 書く前に `ensure_fresh(decision)` で確かめ、判断に使う Issue を読み直す。GitHub につながらなければ、書く前に止まる。書いた結果は、すぐにスナップショットに反映され、次の `scope show` が取り直しなしで示す（AC-16 の一部）。
  - Issue を作った後に失敗したとき、`partial`（終了コード6）と `scope import` の案内を返し、`scope import` で完了できる。
  - `work finish` は、未保存の変更があるとき、保存と push を待つ。確かめられないと、Issue を閉じずに `partial` で止まる。Scope の下に保留があれば、`CANONICAL_SAVE_HELD` で止まる。他のクローンの push を取り込んだだけで自分が push しなかった場合も、確かめられて閉じる（AC-13）。
  - 依存の追加は、循環になるときに書く前に止まる。
  - 基点のツリーに `spec-dock/initiatives` がある `work start` は、`CANONICAL_BASE_HAS_SPECS` で止まる。

### I-6 Accept Japanese Titles In Canonical Mode

- **価値**：日本語の題名で Scope を作れる。識別は英語の slug のまま。
- **作るもの**：`design.md` 7章の題名と slug の規則を、canonical モードの `scope create` と `scope import` と `scope edit` に入れる。
- **受け入れ**：
  - 日本語の題名と `--slug` で作った Scope のディレクトリとブランチが英語で、`scope show` と `workspace sync` に日本語の題名が出る（AC-09）。
  - 日本語の題名で `--slug` がないときは、`SLUG_REQUIRED` で止まる。
  - 従来モードの題名の規則は変わらない。

### I-7 Add Default Branch Spec Check And Workflow

- **価値**：既定のブランチに仕様が入ったPRを、CIで見つけられる。各プロダクトは見本を写すだけで使える。
- **作るもの**（`design.md` 8章）：`canonical check`、ワークフローの見本、版のファイル（配布資産と、`pyproject.toml` の版と同じかを確かめる単体テスト）、`.github/scripts/specdock-ci-check.sh`、`.github/workflows/release-tag.yml`。spec-dock の `spec-dock-check.yml` を置くのと、`ci.yml` の変更は、I-10 の切り替えのPRで行う（それまでは失敗するため）。
- **受け入れ**：
  - 一時のリポジトリで、仕様のパス、`.canonical` の下のパス、`.meta.json`、版3の宣言、壊れた配布資産、無視の3行の欠けのそれぞれを、パスと次の1手付きで見つけ、終了コード7で終わる。正しいツリーでは通る。
  - ネットワークと GitHub のトークンなしで動く。
  - 見本のワークフローの手順のコマンド（SpecDock を入れて `canonical check` を実行する）と、`specdock-ci-check.sh` を、一時のリポジトリで確かめる。版のタグはまだないので、入れるのは手元で作った wheel でよい。実際の GitHub での動きは、I-10 で確かめる。
  - `release-tag.yml` の判定（版が変わり、0.3.0 以上で、タグがないときだけ作る）を、判定のスクリプトの単位で確かめる。

### I-8 Add Throwaway Canonical Migration Script

- **価値**：spec-dock と、後で利用者の個人のプロジェクトを、安全に移行でき、必要なら戻せる。
- **作るもの**（`design.md` 11章）：`scripts/migrate-to-canonical/migrate.py` と `README.md`。サブコマンド `plan`、`register`、`verify`、`build-canonical`、`cut`、`move-local`、`adopt-worktree`、`undo`、`export-legacy`。作業の記録（`undo.jsonl`、`idmap.json`）。
- **受け入れ**：
  - 既定では何も書かない（偽の `gh` への書き込みと、リポジトリの変化がないことを確かめる）。
  - 一時のリポジトリと偽の `gh` で、`register --apply` を途中で止めて再実行すると、重複なく続きから終わる。`undo --apply` で元に戻る。`register` はリポジトリのファイルを変えない。
  - `plan` が、`init-local-00002` と `init-local-00003` のような、ローカルの Scope と番号の不一致と、題名の食い違いを一覧にし、置き換えの予定を示す（R-G4）。
  - `build-canonical` の結果が、形式1の管理ファイルを持ち、`.meta.json` を持たず、元の `spec-dock/initiatives` の追跡されたファイルと（`idmap.json` の名前の置き換えの後で）一致する。
  - `move-local` が、無視された `.workbench` のファイルと追跡されていないファイルを、上書きせずにカタログへ移し、`canonical link` がリンクを置けるようになる。
  - `adopt-worktree` の後、コミットしていない変更も canonical に入り、ブランチを既定のブランチにマージしても、仕様のパスが入らない（AC-05）。構造の違いの一覧が出る。
  - `export-legacy` で作ったブランチの `.meta.json` が、移行前のものと、`revision` と `lifecycle` のほかは一致する。
  - 写した値（C1、C3 の無視の3行、C5、C7）が、パッケージの定数と同じ。
- **注意**：本物の GitHub への書き込みは、この Issue では行わない。

### I-9 Integrate Agent Rules Docs And Release

- **価値**：全体がつながって動き、エージェントと人が文書だけで使える。0.3.0 として出せる。
- **作るもの**：
  - 規則の節（`design.md` 10章）を、配布するスキルと spec-dock の `AGENTS.md` に置く。AGENTS.md の破壊的なコマンドに `canonical remove` を足す。
  - 使い方の文書（R-H3）：README と、配布する `spec-dock/docs/canonical.md`（新設。`guide.md`、`migration.md`、`reference_cli.md` から参照する）。ツールごとの設定の1行（利用者が1回だけ手で足すこと）、設定の場所、拒否の文言、要らない場合と書けない場合、確かめ方、同期が止まったとき（一時停止と `resume`、macOS のプライバシーの保護）を書く。Linux の節に、systemd の Linux と linger、コンテナ（中でクローンすることと、起動し直しの1行）、マウントしたチェックアウトでは止まること、Git 2.38 以上が要ること（Ubuntu 22.04 の標準の Git では足りない）を書く。構造のスナップショットとダッシュボードの節に、置き場、新しさ（変化は1〜2分、親子と依存だけの変更は最大30分）、急ぐときの `workspace sync --source github` を書く。
  - エラーのコードと次の1手の一覧（12章）が、実装と一致するかを確かめる。
  - 版4で、53のすべてのコマンドが、canonical の処理か案内付きの拒否で動き、`CANONICAL_NOT_IMPLEMENTED` が残っていないことを確かめるテスト（G7）。
  - 横断のシナリオのテスト：2つのクローンと偽の `gh` で、`link` → `scope create` → 編集 → `sync` → 別のクローンで見える → `work start` → `work finish` までを通す。
  - spec-dock の利用側の配布資産を、`installation update` で 0.3.0 に上げる（従来モードのまま）。
  - 版を 0.3.0 にする（`pyproject.toml` と版のファイル）。
- **受け入れ**：
  - AC-02、AC-07、AC-14、AC-15、AC-16、AC-18 を確かめる。AC-14 は、設計書を渡さない白紙のエージェントに規則の節だけを渡して試し、結果を報告書に書く。AC-18 は、横断のシナリオのテストを、環境の判定を注入して systemd と `loop` の両方で通し、実機では OrbStack の仮想マシンと Docker のコンテナで通す。
  - wheel を作り、外の環境に入れて、`spec-dock help` と `spec-dock canonical --help` が動く（AGENTS.md の手順）。

### I-10 Migrate Spec Dock To Canonical Storage

- **価値**：spec-dock 自身が、新しい仕組みで動き始める。
- **前提**：I-9 までのPRがマージされている。利用者の環境に 0.3.0 が入っている（`spec-dock installation show` などで確かめる）。開いている仕様の変更のPRと、作業用のworktreeとその仕様の変更を一覧にしてある。
- **手順**（`design.md`「移行・互換性・rollback」）：
  1. `migrate.py plan` の結果を確かめ、異常の扱い（ローカルの Scope の置き換えなど）を決めて記録する。
  2. `register --apply` と `verify` を行う。この間、今の運用は止めない。
  3. 切り替えを始めることを利用者に知らせ、ほかのエージェントで仕様を編集しないようにしてもらう（凍結）。凍結の後に、`register --apply` と `verify` をもう一度行う。
  4. `build-canonical --apply` と `cut --apply` で、canonical を push し、既定のブランチから仕様を外すPRを作る。PRには、`spec-dock-check.yml` の追加、`ci.yml` の `validate --ci` の手順の削除、宣言の版4を入れる。
  5. PRの検査が通ったことを確かめ、マージできる状態で止める。人がマージする。
  6. mainのチェックアウトで既定のブランチを取り込み、`move-local` で無視されたファイル（`.workbench` の99個など）をカタログへ移し、`spec-dock canonical link` を実行する。示されたツールの1行を利用者に伝える。定期の同期が動いていることを `canonical status` で確かめる。最初の周期で、mainのチェックアウトの古いダッシュボード（2026-09-21 のもの）が、日本語の題名の新しいものに置き換わることを確かめる（AC-17）。
  7. 各作業用のworktreeで、`adopt-worktree` と `move-local` を行い、既定のブランチを取り込んでから、`spec-dock canonical link` を実行する。`adopt-worktree` が示した構造の違いは、SpecDock のコマンドで登録し直す。
  8. 切り替えの終わりを利用者に知らせ、凍結を解く。
- **受け入れ**：AC-01、AC-04、AC-05、AC-12（実際の GitHub でのPRの検査）、AC-16 と AC-17（実際の GitHub で）を確かめる。切り替えの後、3日間の通常の運用で、仕様の失われがなく、`canonical status` に未解決の異常がない。
- **ついでに確かめること**：`register --apply` で親子と依存を登録するとき、登録の前後で、その Issue の `updated_at` と、変わったかの確かめの応答（304 か 200 か）を記録する。親子と依存の変更で更新の時刻が変わるなら、`design.md` の「未確認の事項」から外し、30分ごとの取り直しを見直す提案を、この Epic の報告書に書く。
- **注意**：GitHub への書き込みと、既定のブランチを変えるPRは、利用者の目の前で行う。止まったら、`design.md` の戻し方に従い、利用者に判断を求める。

### I-11 Regenerate Dashboard From Structure Snapshot

- **価値**：今までと同じ Markdown と PlantUML のダッシュボードが、日本語の題名と、どのPCで作業中かを含めて、いつも新しい状態で mainのチェックアウトにある。次の Epic の HTML のダッシュボードまでのつなぎになる。
- **作るもの**（`design.md` 13章）：
  - 始めるときに、spec-dock のmainのチェックアウト（`/Volumes/990p2t/workspace/tools/spec-dock/spec-dock/`）の、2026-09-21 に作られた5つのファイル（`dashboard.md`、`tree.puml`、`tree-all.puml`、`deps-issues.puml`、`deps-raw.puml`）を、テストの見本として写す。どれも Git では無視されているので、写さないと残らない。
  - `application/canonical_dashboard.py`：スナップショットから、今の描く関数（`presentation/markdown.py`、`puml.py`）の入力の辞書を作る部品と、5つのファイルを書く部品。状態の決め方は、I-4 の着手の判定の部品を使う。
  - 定期の同期の周期の手順7に、ダッシュボードの作り直しを足す（`state.json` の `dashboard`。C9 に項目を足す）。
  - `canonical status` の `dashboard` の項目。`canonical remove` で5つのファイルを消すこと。
- **受け入れ**：
  - 一時のカタログと偽の `gh` で、周期の後に5つのファイルが作られ、見本と同じ形である（違いは、題名、作業中の決め方、Observability の行だけ）。日本語の題名が、PlantUML の文字列として正しく入る。
  - 作業中のラベルのある Issue が DOING、閉じた Issue が DONE、開いた依存先のある Issue が BLOCKED になる。Scope でない開いた Issue への依存も BLOCKED になる。
  - 構造が変わらない次の周期では、5つのファイルを書かない（更新の時刻が変わらない）。題名を変えた後の周期では書き直す（AC-17）。
  - 書く場所にディレクトリかシンボリックリンクがあると、そのファイルを書かずに `dashboard.error` に記録する。作業用のworktreeには書かない。従来モードでは作らない。
- **注意**：描く関数は、従来モードからは呼ばれていない。直すときも、出力の形を変えてはならない。

## 検証

- **毎回**：各 Issue のPRで、`make lint` と `uv run pytest` を通す。従来モードの回帰（AC-15）は、すべての Issue で確かめる。
- **契約の確認**：使う側の Issue は、持ち主の Issue が作った契約を、テストで直接使う（写しを作らない）。I-8 だけは、写した値をパッケージの定数と比べる。
- **横断の確認**：I-9 の横断のシナリオのテストと、全コマンドのテストと、受け入れ条件ごとの確かめ（`design.md` の testability の表）。
- **Linux**：提供側のCIは `uv run pytest` を `ubuntu-latest` で動かすので、すべてのテストは毎回 Linux でも通る。環境に依る部分（定期の実行の仕組み、コンテナ、linger、git の版）は、環境の判定を注入したテストで、どの OS の上でもすべての場合を確かめる。
- **実機の確認**：I-2、I-3、I-9、I-10 の報告書に、macOS（外付けのボリュームを含む）、Linux（OrbStack の仮想マシンと Docker のコンテナ）、Codex のサンドボックス、Claude Code での結果を書く。確かめられなかったことは「未確認」と書き、対応したとは書かない。

## rollback

- **I-1〜I-9**：どれも、PRを `git revert` すれば戻る。宣言の版が3の spec-dock では、canonical の処理は動かないので、利用者の運用への影響はない。
- **I-10**：`design.md` の「戻し方」に従う。切り替えのPRのマージ前なら、PRを閉じ、canonical を消し、`undo --apply` で登録を外す。マージの後なら、`export-legacy --apply` で戻すPRを作り、各チェックアウトで `canonical remove --yes` を行う。戻すかどうかは、利用者が判断する。
- 戻した後は、何が起きたかを、この Epic の報告書に書く。

## exit / handoff

- **Issue の完了**：その Issue の受け入れを満たし、PRが人にマージされ、`work finish` で閉じる。報告書に、実装したこと、確かめたこと、実機の確かめの結果、残ったリスクを書く。
- **Epic の完了**：AC-01〜AC-18 をすべて確かめ、I-10 の後の3日間の運用で問題がない。`design.md` の「未確認の事項」に残ったものは、別の Issue にするか、理由を付けて閉じる。この Epic の報告書に、結果と、ほかのプロダクトを移行するときの注意をまとめる。
- **この後**：
  - 次の Epic（epic-00425）で、HTML のダッシュボードと、仕様の文書の CUE と HTML への移行を議論する。構造のスナップショット（C10）は、その入力として、この Epic の形のまま渡す。
  - 利用者の個人のプロジェクト（退去費用プロダクト、housing-lifecycle、company-os）の移行は、各プロジェクトで、移行のスクリプトの手順書に従って行う。すべて移行したら、別の Epic で、従来モードのコードと移行のスクリプトを消す。
