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

`requirement.md` の受け入れ条件 AC-01〜AC-15 を満たす SpecDock 0.3.0 を作り、spec-dock を canonical モードに切り替えて、運用を始める。実装は、Issue ごとに、別のworktreeで、この Epic の議論に参加していない実装担当のエージェントが行う。そのため、この計画書は、`requirement.md` と `design.md` とあわせて読めば、ほかの資料なしで各 Issue を始められるように書く。

## 実装担当への共通の指示

各 Issue の担当は、始める前に次を読む。

1. リポジトリの `AGENTS.md`（提供側の `src/spec_dock/` と利用側の `spec-dock/` の区別、層の置き場、テストの置き場、コミットとPRの規則）。
2. `.agents/skills/spec-dock/SKILL.md`（SpecDock の CLI の使い方）。
3. この Epic の `requirement.md`（R-* と AC-*）、`design.md`（担当する章）、この計画書（担当する Issue の節と「Issue をまたぐ契約」）。
4. 必要に応じて、調査の記録 `artifacts/20261025t080353z-research-verified-git-github-behaviors.md`。

作業のしかた：

- Issue ごとに、作業用のworktreeとブランチを1つ使い、PRを1つ作る。`spec-dock work start <Issue の ID>` で始め、`spec-dock work finish` で終える。
- 実装の間、spec-dock のリポジトリは従来モード（宣言の版3）のままである。仕様の文書は、今までどおりコードと一緒にコミットする。
- 最初に、その Issue の `requirement.md`、`design.md`、`plan.md` を、この計画書の節から書く。Epic の目的、Issue の分け方、Issue をまたぐ契約は変えない。変える必要を見つけたら、推測で埋めずに止まり、Epic の文書の変更を提案する（Scope Layering Guide）。
- テストは、外のネットワークを使わない。GitHub は偽の `gh` で、リモートは一時ディレクトリの bare のリポジトリで置き換える（`design.md` の testability）。
- 毎回、`make lint` と `uv run pytest` を通す。従来モードの回帰テスト（AC-15）を壊してはならない。
- してはならないこと：
  - 利用者のツールの設定（`~/.claude/settings.json`、`~/.codex/config.toml` など）を変える。
  - 本物の spec-dock のリポジトリで、I-10 より前に `canonical` のコマンドを実行する（版3なので止まるはずだが、試さない）。
  - 本物の GitHub に、ラベル、sub-issue、依存、`spec-dock/canonical` ブランチを作る（I-10 の切り替えでだけ行う）。
  - 利用者の `~/Library/LaunchAgents/` に、実機の確かめ以外でジョブを置く。実機で確かめるときは、別の名前（例 `local.specdock.test.<Issue>`）のジョブを内蔵のディスクの一時ディレクトリの plist から読み込み、終わったら `launchctl bootout` で外す。
- コミットは、AGENTS.md のとおり、日本語の Conventional Commits にする。PRはマージできる状態で止め、マージは人が行う。PRの検査が通っていないPRを、マージできる状態として渡さない。

## 順序・依存

### Issue の一覧

| 番号 | 題名（作成時の英語の題名 / slug） | 担当する設計の章 | 依存 | Planning Level |
|---|---|---|---|---|
| I-1 | Add Canonical Mode And GitHub Structure Gateway / `canonical-mode-structure` | 1、2 | なし | standard |
| I-2 | Add Canonical Catalog Link Status And Remove / `canonical-catalog-link` | 3、4、9 | I-1 | strict |
| I-3 | Add Periodic Canonical Sync / `canonical-periodic-sync` | 5 | I-2 | strict |
| I-4 | Read Scopes From GitHub In Canonical Mode / `canonical-scope-read` | 6（読む側） | I-1、I-2 | standard |
| I-5 | Write Scopes To GitHub In Canonical Mode / `canonical-scope-write` | 6（書く側） | I-3、I-4 | strict |
| I-6 | Accept Japanese Titles In Canonical Mode / `canonical-japanese-titles` | 7 | I-5 | standard |
| I-7 | Add Default Branch Spec Check And Workflow / `canonical-branch-check` | 8 | I-1 | standard |
| I-8 | Add Throwaway Canonical Migration Script / `canonical-migration-script` | 11 | I-1 | strict |
| I-9 | Integrate Agent Rules Docs And Release / `canonical-rules-docs-release` | 10、12、testability | I-2〜I-8 | standard |
| I-10 | Migrate Spec Dock To Canonical Storage / `spec-dock-canonical-cutover` | 移行・互換性・rollback | I-9 | strict |

- 題名は、今の CLI が英数字しか受け付けないため、英語で作る（requirement.md の合意）。
- Planning Level は、失敗したときの影響と戻しにくさで選んだ。I-2、I-3、I-5 は利用者の仕様のファイルを書き、I-8 と I-10 は GitHub に大量に書くので strict にした。

### 進め方

```text
I-1 ─┬─ I-2 ── I-3 ─┐
     ├─ I-4 ────────┴─ I-5 ── I-6 ─┐
     ├─ I-7 ────────────────────────┼─ I-9 ── I-10
     └─ I-8 ────────────────────────┘
```

- I-1 の後は、I-2、I-4、I-7、I-8 を並べて進めてよい。
- I-5 は、カタログの排他と変更の束（I-2）、同期の状態のファイル（I-3）、読む側の部品（I-4）を使う。
- I-9 で全体をつないで確かめ、版を 0.3.0 にする。I-10 は、0.3.0 を利用者の環境に入れた後に行う。

### Issue をまたぐ契約

各契約は、持ち主の Issue が `design.md` のとおりに作り、使う側の Issue は変えずに使う。変える必要があれば、Epic の `design.md` を先に変える。

| 契約 | 持ち主 | 使う側 | `design.md` |
|---|---|---|---|
| C1 構造の表し方（種類のラベル、本文の slug の印、ID の作り方）と `StructureSnapshot`、`ScopeNode` | I-1 | I-4、I-5、I-6、I-8 | 2章 |
| C2 宣言の版4とモードの判定 | I-1 | すべて | 1章 |
| C3 カタログとリンクの場所、正しいリンクの判定、`CANONICAL_NOT_LINKED` | I-2 | I-3、I-4、I-5 | 3章 |
| C4 カタログの排他と、変更の束の形式 | I-2 | I-3（読む）、I-5（書く） | 4章 |
| C5 canonical の中身（形式1の管理ファイル） | I-2 | I-3、I-8 | 5章 |
| C6 同期の状態のファイル `state.json` の形式 | I-3 | I-2（`status` の同期の項目は I-3 で足す）、I-5（`work finish`） | 5章 |
| C7 版のファイルと、検査のワークフローの見本 | I-7 | I-8（`cut`）、I-9、I-10 | 8章 |
| C8 エラーのコードと次の1手 | 各コマンドの持ち主 | I-9（一覧の確認） | 12章 |

- I-8 の移行のスクリプトは、パッケージを読み込まない1つのファイルなので、C1 と C5 の値を写して持つ。写した値が同じであることを、I-8 のテストで、パッケージの定数と比べて確かめる。

## 実装step

各 Issue の節は、その Issue の要件定義書の材料である。「受け入れ」は、その Issue の受け入れ条件にそのまま使う。

### I-1 Add Canonical Mode And GitHub Structure Gateway

- **価値**：canonical モードの土台になる、モードの判定と、GitHub の構造の読み書きができる。利用者から見える変化はまだない。
- **作るもの**：
  - `application/project_context.py` の宣言の読み取りを、版3と4の受け付けとモードの判定に変える（`design.md` 1章）。`dispatch()` に、モードによる振り分けの入口を作る（canonical の処理は、まだ `CANONICAL_NOT_IMPLEMENTED` などで止めてよい）。
  - `infra/github_structure.py`：一覧（ページ送り）、取得、作成（ラベル付き）、題名の変更、ラベルの追加と削除とラベル自体の作成、sub-issue の一覧と追加と削除と親の取得、blocked by の一覧と追加と削除、担当者の追加、`GET /user`。GET だけ再試行する（2章）。
  - `domain/canonical_structure.py`：`StructureSnapshot`、`ScopeNode`、本文の印の解析と生成、ラベルからの種類の判定、階層と種類の規則の検査、循環の検査（今の `domain/dependency_vnext.py` の規則を使う）。
  - `read_all` と、一部を読む関数（`read_node`、`read_ancestors`、`read_children`、`read_blockers`）。
  - テスト用の偽の `gh` に、上の API を足す。
- **受け入れ**：
  - 版3の宣言では、すべてのコマンドが今と同じに動く（今の回帰テストが変更なしで通る）。
  - 版4の宣言を読むと canonical モードと判定し、版5は今と同じく止まる。
  - 偽の `gh` の上で、`read_all` が、ラベル、親子、依存、印から正しい `StructureSnapshot` を作り、規則の違反（種類のラベルが2つ、印がない、Epic の親が Issue、循環）を異常として返す。
  - `sub_issue_id` と `issue_id` に、番号ではなく Issue の id を送る（テストで送った本文を確かめる）。
- **注意**：従来モードの処理と `.meta.json` の読み書きのコードを変えてはならない。

### I-2 Add Canonical Catalog Link Status And Remove

- **価値**：`spec-dock canonical link` の1回で、どのチェックアウトからでも仕様が `spec-dock/initiatives/` に見える。状態と取り外しのコマンドがある。
- **作るもの**：
  - `canonical link`、`canonical status`、`canonical remove`（`design.md` 3章）。`canonical status` の同期の項目は、I-3 で足す（ここでは「未対応」と返してよい）。
  - `infra/canonical_git.py` のうち、worktree、lock、除外、fetch、新しいリポジトリでの初期の canonical の作成。
  - `infra/catalog_lock.py` と、変更の束を書く部品（4章）。`.runtime/` と、作成の作業場所。
  - `infra/catalog_tree.py`：名前で Scope のディレクトリを探す。リンクは「正しいリンク」だけを受け付ける。
  - `worktree create` と `work start` の後のリンク（3章「SpecDock のほかのコマンドから」）。
  - ツールの設定の判定と、示す1行（9章）。
  - 配布資産 `spec-dock/.gitignore` への `/.canonical/` の追加と、`static-inventory.json` の更新。
- **受け入れ**：
  - 一時のリポジトリで、新しいクローン、`git worktree add` のworktree、`worktree create` のworktreeのそれぞれで、仕様を読み書きできる（AC-06）。
  - `git clean -ffdx`、mainのチェックアウトの移動、移行前のコミットへの checkout の後、`canonical status` が原因と次の1手を示し、`canonical link` で戻る（AC-08）。
  - リンクの場所に実体があるとき、何も消さずに止まる。
  - Codex のサンドボックスの代わりに書けないディレクトリで、`canonical status` が `writable_roots` の正確な1行を示す（AC-07 の一部）。
  - `canonical remove` は、未保存の変更があると止まり、`--yes` がないと何もしない。
- **実機の確かめ**：macOS で、外付けのボリュームの一時のリポジトリを使い、`canonical link` が作るジョブの登録（I-3 の後）とリンクを確かめる。結果は報告書に書く。

### I-3 Add Periodic Canonical Sync

- **価値**：保存、取り込み、push が、人もエージェントも意識せずに、60秒ごとに行われる。競合しても編集は失われない。
- **作るもの**：
  - `canonical sync`（`--registered` を含む）、`canonical accept`、`canonical restore`（`design.md` 5章）。
  - 保存するパスの選び方、保留、競合の段からの解決の計画は、`domain/` の純粋な関数にする。時刻は注入する。
  - 一時のインデックスでの保存、`merge-tree` による統合、`commit-tree` と `merge --ff-only`、push（`infra/canonical_git.py`）。
  - 状態のファイル `state.json`、登録簿、ログの切り替え。
  - launchd と systemd の登録、解除、すぐの実行。`canonical link` からの登録と、直後の1回の実行の確かめ。
  - `canonical status` の同期の項目。
- **受け入れ**：
  - 2つのクローンで、同じファイルを変えて両方で `sync` すると、両方に先着の版と別名ファイルが残り、競合のマーカーがない（AC-03）。変更と削除の競合では、変更が残る。
  - 25件の削除は保留され、push されない（AC-10）。`accept --deletions` の後は保存される。`restore` で戻る。
  - bare のリポジトリで canonical を強制 push で書き換えると、`sync` は取り込まずに止まる（AC-11）。
  - 編集中のファイルに当たる取り込みは、何も壊さずに次の周期へ持ち越す。
  - コミットで、リポジトリのフックが動かない（テストで、失敗するフックを置いて確かめる）。
  - 書き換えの途中の状態（変更の束の書きかけ）を保存しない（排他のテスト）。
- **実機の確かめ**：macOS の launchd（外付けのボリュームと内蔵のディスクの両方、利用者の `gh` での push。テスト用の別の名前のジョブとリポジトリで行う）。Linux の systemd のタイマー（利用者の Lima の VM など）。確かめられなかったことは、報告書と `design.md` の「未確認の事項」に残す。

### I-4 Read Scopes From GitHub In Canonical Mode

- **価値**：canonical モードで、Scope の表示、一覧、依存の確かめ、状態の観測、構造の検査ができる。
- **作るもの**（`design.md` 6章の表の読む側）：`scope show`、`scope list`、`dependency list`、`dependency check`、`workspace sync`、`workspace validate`、`workspace doctor` の canonical の処理。`work start` の着手の判定を、GitHub の構造から行う部品。
- **受け入れ**：
  - 偽の `gh` と一時のカタログで、各コマンドが GitHub の題名と状態と、ディレクトリの場所を示す（R-E4）。
  - `workspace validate` が、6章の検査の項目をすべて見つける。入れ子のずれは警告で、`scope move <ID>` を次の1手に示す。
  - `workspace validate --ci` と `workspace sync --source local` は、canonical モードでは案内付きで止まる。
  - 読むだけのコマンドは、何も書かない（テストで、カタログと `.git` の変化がないことを確かめる）。

### I-5 Write Scopes To GitHub In Canonical Mode

- **価値**：canonical モードで、Scope の作成、取り込み、題名の変更、親の変更、完了、削除、依存の変更、Artifact の作成、作業の開始と終了ができる。
- **作るもの**（`design.md` 6章の表の書く側）：`scope create`、`scope import github`、`scope edit`、`scope move`（新設）、`scope close`、`scope reopen`、`scope delete`、`dependency add`、`dependency remove`、`artifact create`、`artifact import file`、`work start`（作業中の印とリンク）、`work finish`（保存の確認）。作成時に、前付けの `タイトル:` と `親:` の行を除く。
- **受け入れ**：
  - 偽の `gh` で、各コマンドが `design.md` の順に GitHub に書き、カタログには排他の中で書いて変更の束を残す。
  - Issue を作った後に失敗したとき、終了コード6と `scope import` の案内を返し、`scope import` で完了できる。
  - `work finish` は、未保存の変更があるとき、保存と push を待つ。確かめられないと、Issue を閉じずに止まる（AC-13）。
  - 依存の追加は、循環になるときに書く前に止まる。

### I-6 Accept Japanese Titles In Canonical Mode

- **価値**：日本語の題名で Scope を作れる。識別は英語の slug のまま。
- **作るもの**：`design.md` 7章の題名と slug の規則を、canonical モードの `scope create` と `scope import` と `scope edit` に入れる。
- **受け入れ**：
  - 日本語の題名と `--slug` で作った Scope のディレクトリとブランチが英語で、`scope show` と `workspace sync` に日本語の題名が出る（AC-09）。
  - 日本語の題名で `--slug` がないときは、案内付きで止まる。
  - 従来モードの題名の規則は変わらない。

### I-7 Add Default Branch Spec Check And Workflow

- **価値**：既定のブランチに仕様が入ったPRを、CIで見つけられる。各プロダクトは見本を写すだけで使える。
- **作るもの**（`design.md` 8章）：`canonical check`、ワークフローの見本、版のファイル（配布資産と、`pyproject.toml` の版と同じかを確かめる単体テスト）、`.github/workflows/release-tag.yml`。spec-dock の `spec-dock-check.yml` の中身は作るが、リポジトリに置くのは I-10 の切り替えのPRで行う（それまでは失敗するため）。
- **受け入れ**：
  - 一時のリポジトリで、仕様のパス、`.canonical` の下のパス、`.meta.json`、版3の宣言、壊れた配布資産のそれぞれを、パスと次の1手付きで見つけ、終了コード7で終わる。正しいツリーでは通る。
  - ネットワークと GitHub のトークンなしで動く。
  - 見本のワークフローの手順のコマンド（SpecDock を入れて `canonical check` を実行する）を、一時のリポジトリで確かめる。版のタグはまだないので、入れるのは手元で作った wheel でよい。実際の GitHub での動きは、I-10 で確かめる。
  - `release-tag.yml` が、版のタグがないときだけタグを作ることを、手順のスクリプトの単位で確かめる。

### I-8 Add Throwaway Canonical Migration Script

- **価値**：spec-dock と、後で利用者の個人のプロジェクトを、安全に移行できる。
- **作るもの**（`design.md` 11章）：`scripts/migrate-to-canonical/migrate.py` と `README.md`。サブコマンド `plan`、`register`、`verify`、`build-canonical`、`cut`、`adopt-branch`、`undo`。
- **受け入れ**：
  - 既定では何も書かない（テストで、偽の `gh` への書き込みがないことを確かめる）。
  - 一時のリポジトリと偽の `gh` で、`register --apply` を途中で止めて再実行すると、重複なく続きから終わる。`undo --apply` で元に戻る。
  - `plan` が、`init-local-00002` と `init-local-00003` のような、ローカルの Scope と番号の不一致と、題名の食い違いを一覧にする（R-G4）。
  - `build-canonical` の結果が、形式1の管理ファイルを持ち、`.meta.json` を持たず、元の `spec-dock/initiatives` の内容と一致する。
  - `adopt-branch` の後、ブランチを既定のブランチにマージしても、仕様のパスが入らない（AC-05）。
  - C1 と C5 の写した値が、パッケージの定数と同じ。
- **注意**：本物の GitHub への書き込みは、この Issue では行わない。

### I-9 Integrate Agent Rules Docs And Release

- **価値**：全体がつながって動き、エージェントと人が文書だけで使える。0.3.0 として出せる。
- **作るもの**：
  - 規則の節（`design.md` 10章）を、配布するスキルと spec-dock の `AGENTS.md` に置く。AGENTS.md の破壊的なコマンドに `canonical remove` を足す。
  - 使い方の文書（R-H3）：README と、配布する文書（`spec-dock/docs/canonical.md` を新しく作り、`guide.md`、`migration.md`、`reference_cli.md` から参照する）。ツールごとの設定の1行、設定の場所、拒否の文言、要らない場合と書けない場合、確かめ方を書く。
  - エラーのコードと次の1手の一覧（12章）が、実装と一致するかを確かめる。
  - 横断のシナリオのテスト：2つのクローンと偽の `gh` で、`link` → `scope create` → 編集 → `sync` → 別のクローンで見える → `work start` → `work finish` までを通す。
  - 版を 0.3.0 にする（`pyproject.toml` と版のファイル）。
- **受け入れ**：
  - AC-02、AC-07、AC-14、AC-15 を確かめる。AC-14 は、設計書を渡さない白紙のエージェントに規則の節だけを渡して試し、結果を報告書に書く。
  - wheel を作り、外の環境に入れて、`spec-dock help` と `spec-dock canonical --help` が動く（AGENTS.md の手順）。

### I-10 Migrate Spec Dock To Canonical Storage

- **価値**：spec-dock 自身が、新しい仕組みで動き始める。
- **前提**：I-9 までのPRがマージされている。利用者の環境に 0.3.0 が入っている（`spec-dock --version` などで確かめる）。開いている仕様の変更のPRと、作業用のworktreeの仕様の変更を一覧にしてある。
- **手順**（`design.md`「移行・互換性・rollback」）：
  1. `migrate.py plan` の結果を確かめ、異常の扱いを決めて記録する（ローカルの Scope は、11章の規則に従う）。
  2. `register --apply` と `verify` を行う。この間、今の運用は止めない。
  3. 切り替えを始めることを利用者に知らせ、ほかのエージェントで仕様を編集しないようにしてもらう。
  4. `build-canonical --apply` と `cut --apply` で、canonical を push し、既定のブランチから仕様を外すPRを作る。PRには、`spec-dock-check.yml` の追加、`ci.yml` の `validate --ci` の手順の削除、宣言の版4を入れる。
  5. PRの検査が通ったことを確かめ、マージできる状態で止める。人がマージする。
  6. mainのチェックアウトと各作業用のworktreeで `spec-dock canonical link` を実行し、示されたツールの1行を利用者に伝える。定期の同期が動いていることを `canonical status` で確かめる。
  7. 作業用のworktreeに残った仕様の変更を、`adopt-branch` で取り込む。
  8. 切り替えの終わりを利用者に知らせる。
- **受け入れ**：AC-01、AC-04、AC-05、AC-12（実際の GitHub でのPRの検査）を確かめる。切り替えの後、3日間の通常の運用で、仕様の失われがなく、`canonical status` に未解決の異常がない。
- **注意**：GitHub への書き込みと、既定のブランチを変えるPRは、利用者の目の前で行う。止まったら、`design.md` の戻し方に従い、利用者に判断を求める。

## 検証

- **毎回**：各 Issue のPRで、`make lint` と `uv run pytest` を通す。従来モードの回帰（AC-15）は、すべての Issue で確かめる。
- **契約の確認**：使う側の Issue は、持ち主の Issue が作った契約を、テストで直接使う（写しを作らない）。I-8 だけは、写した値をパッケージの定数と比べる。
- **横断の確認**：I-9 の横断のシナリオのテストと、受け入れ条件ごとの確かめ（`design.md` の testability の表）。
- **実機の確認**：I-2、I-3、I-9、I-10 の報告書に、macOS（外付けのボリュームを含む）、Linux、Codex のサンドボックス、Claude Code での結果を書く。確かめられなかったことは「未確認」と書き、対応したとは書かない。

## rollback

- **I-1〜I-9**：どれも、PRを `git revert` すれば戻る。宣言の版が3の spec-dock では、canonical の処理は動かないので、利用者の運用への影響はない。
- **I-10**：`design.md` の「戻し方」に従う。切り替えのPRのマージ前なら、PRを閉じ、canonical を消し、`undo --apply` で登録を外す。マージの後なら、PRの取り消し、宣言の版3への戻し、canonical の後の変更の写し、`.meta.json` の作り直し、各チェックアウトでの `canonical remove --yes` を行う。戻すかどうかは、利用者が判断する。
- 戻した後は、何が起きたかを、この Epic の報告書に書く。

## exit / handoff

- **Issue の完了**：その Issue の受け入れを満たし、PRが人にマージされ、`work finish` で閉じる。報告書に、実装したこと、確かめたこと、実機の確かめの結果、残ったリスクを書く。
- **Epic の完了**：AC-01〜AC-15 をすべて確かめ、I-10 の後の3日間の運用で問題がない。`design.md` の「未確認の事項」に残ったものは、別の Issue にするか、理由を付けて閉じる。この Epic の報告書に、結果と、ほかのプロダクトを移行するときの注意をまとめる。
- **この後**：利用者の個人のプロジェクト（退去費用プロダクト、housing-lifecycle、company-os）の移行は、各プロジェクトで、移行のスクリプトの手順書に従って行う。すべて移行したら、別の Epic で、従来モードのコードと移行のスクリプトを消す。
