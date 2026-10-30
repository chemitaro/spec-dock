---
種別: 要件定義書（Issue）
ID: "iss-00436"
タイトル: "Integrate Agent Rules Docs And Release"
関連GitHub: ["#436"]
状態: "approved"
最終更新: "2026-10-30"
親: ["epic-00424", "init-00423"]
---

# iss-00436 Integrate Agent Rules Docs And Release — 要件定義

詳細: [Requirement Guide](../../../docs/authoring/requirement.md)

表示名：canonical モードの全体をつないで確かめ、エージェント向けの規則と使い方の文書をそろえ、SpecDock 0.3.0 として出せる状態にする（Epic の I-9）

## 目的

全体がつながって動き、エージェントと人が文書だけで使える。0.3.0 として出せる。

- 材料：Epic の `plan.md` の「I-9 Integrate Agent Rules Docs And Release」の節（価値、作るもの、受け入れ、各 Issue から引き継ぐもの）と、Epic の `design.md` の担当の章（10章の規則の節、12章のエラーのコードと次の1手、testability。置き場と ID は2章と3章）。Issue をまたぐ契約（C1〜C11）は、Epic の `plan.md` の表に従い、変えない。
- 依存：I-3〜I-5、I-7、I-8、I-11、I-14〜I-16（`iss-00430`、`iss-00431`、`iss-00432`、`iss-00434`、`iss-00435`、`iss-00438`、`iss-00455`、`iss-00456`、`iss-00460`）。すべてマージ済み（`origin/main` `ea3d3c9ee`）。I-6 は取りやめ。Planning Level：standard。
- 統括の判断（2026-10-30 の依頼。Epic の `plan.md` の I-9 の節にないもの）：12章の表を実装に合わせる（`CANONICAL_SAVE_UNCONFIRMED` の終了コード、`CANONICAL_PROGRESS_MARK_FAILED` の行）。I-5 の実機で確かめられなかったもの（外の console での `work finish`、Linux の実機、Codex のサンドボックス）を実機の確かめに含める。`migrate.py undo` の作業の記録なしの終了（I-8 の ST-1）と、undo の後の再 register のテスト（I-15 の P3）を、I-10 の前にここで片付ける。3章の `structure` の形（`anomalies`。I-14）に文書をそろえる。

## 背景

- I-1〜I-5、I-7、I-8、I-11、I-14〜I-16 で、canonical モードの各コマンド、定期の同期、検査、移行のスクリプト、ダッシュボードが別々の Issue で入った。各 Issue のテストはそれぞれの範囲を確かめたが、`link` から `work finish` までを2つのクローンで通す横断の確かめと、53のコマンドのすべてが版4で答えることの確かめ（Epic の G7）はまだない。
- エージェント向けの規則の節（Epic の R-H1、10章）は、まだ配布するスキルにも `AGENTS.md` にもない。利用者向けの使い方の文書（R-H3）もない。`reference_cli.md` は52の行で、平らな置き場と ID、I-4 以降の新しいコードを書いていない。配布する `cli-redesign-guide.html` は「全44コマンド」のままである。
- 2026-10-29 の利用者の決定で、Scope のディレクトリは `spec-dock/initiatives/<区切り>/<ID>/`、ID は `<種類>-<番号5桁>`、slug はなく、題名は GitHub の題名が正本、入力は0埋めしなくてよく、既定のブランチ名は `<ID>`、親子と依存は GitHub だけにある。これを文書と `help` に書く必要がある。
- 版はまだ 0.2.4 である。版のタグ `v0.3.0`（I-7 の `release-tag.yml`）は、版を 0.3.0 にしたコミットのマージの後に作られる。I-10（spec-dock の切り替え）は、0.3.0 を利用者の環境に入れた後に行う。
- 関係者：
  - エージェント：規則の節だけを読んで、仕様を読み書きし、検索し、別名ファイルを統合できること。
  - 利用者：使い方の文書だけで、ツールの1行の設定、同期が止まったときの扱い、Linux とコンテナの制約が分かること。0.3.0 を入れても、移行していないリポジトリが今と同じに動くこと（AC-15）。
  - 統括（I-10、I-12）：0.3.0 の wheel と配布資産、移行のスクリプトの安全な `undo` が使えること。

## 観測可能な要件

### R-436-01 規則の節（Epic の R-H1、10章）

- 配布するスキル（`src/spec_dock/assets/install_root/.agents/skills/spec-dock/SKILL.md`）と、spec-dock の `AGENTS.md` に、見出し「仕様の扱い（canonical モード）」の節を置く。中身は Epic の `design.md` 10章の節の項目をすべて含み（表現は整えてよいが、項目を減らさない）、次を足す。
  - ID の入力は0埋めしなくてよい（`iss-454` は `iss-00454`）。canonical モードの `scope create` と `scope import github` に `--slug` を付けると `CANONICAL_NOT_APPLICABLE` で止まる。既定のブランチ名は `<ID>`。
  - `scope move <ID> --parent <親>` は GitHub の親だけを付け替え、ディレクトリは動かない。
  - `SCOPE_KIND_CHANGED` で止まったときは、利用者に確かめる（次の1手は `recovery` に従う）。
  - `work start` が警告 `SCOPE_IN_PROGRESS` を返したら、別のPCで作業中でないかを利用者に確かめる。
  - `work finish` は、保存が確かめられるまで最大180秒待つ。
- 2つの節は同じ項目を持つ（片方だけを直したずれを、テストで見つける）。
- `AGENTS.md` の「対象と結果を明示した指示が要る破壊的なコマンド」と、スキルの「Destructive boundary」に `canonical remove` を足す。

### R-436-02 使い方の文書（Epic の R-H3）

- 配布する `spec-dock/docs/canonical.md` を新しく置き、`docs/README.md`、`guide.md`、`migration.md`、`reference_cli.md` から参照する。リポジトリの `README.md` にも、canonical モードの短い説明と、この文書へのリンクを置く。
- `canonical.md` は次を書く。
  1. モード（宣言の版3と4）、置き場（`spec-dock/initiatives/<区切り>/<ID>/`、区切りの計算と例）、ID（`<種類>-<番号5桁>`、0埋めしない入力、slug がなく `--slug` は `CANONICAL_NOT_APPLICABLE` で止まること）、題名（GitHub の題名が正本、どの言語でもよい）、既定のブランチ名 `<ID>`、親子と依存は GitHub だけにあり `scope show <ID> --json` で確かめること、`scope move`。
  2. 用意：`canonical link`（`--no-schedule`）、`canonical status`（項目と `--structure`。`structure` の形は `{status, next_step, snapshot, anomalies: [...]}`）。
  3. ツールごとの設定（Claude Code と Codex）：足す1行（`canonical status` が示すものと同じ文字列）、設定のファイルの場所（Claude Code は `CLAUDE_CONFIG_DIR` があればその下）、R-J1 の5つのカタログを1行の配列に並べた例、足さないときの拒否の文言、要らない場合（mainのチェックアウト）、書けない場合（Claude Code の隔離セッション）、確かめ方（`canonical status` の `tools`）。利用者が1回だけ手で足し、SpecDock は書き換えないこと。
  4. 保存と同期：自動で1〜2分のうちに保存と共有、別名ファイル、保留（`canonical accept`、`canonical restore`）、`work finish` の保存の確認（最大180秒）。
  5. 同期が止まったとき：一時停止の理由ごとの `canonical resume` の引数（`remote_rewritten` と `merge_failed` は `--adopt-remote`、`remote_deleted` は `--push-local`。`merge_failed` は2回目の `resume` が要ることがある。取り込み直しの途中は `--push-local` を拒む）、macOS のプライバシーの保護、カタログで手で Git を使わないこと。
  6. Linux：systemd のユーザーと linger、コンテナ（中でクローンすること、起動し直しの1行）、マウントしたチェックアウトでは止まること、Git 2.38 以上が要ること（Ubuntu 22.04 の標準の Git では足りない）。
  7. 構造のスナップショットとダッシュボード：置き場、新しさ（変化は1〜2分、親子と依存だけの変更は最大30分）、急ぐときの `workspace sync --source github`、`dependency check` と `workspace sync` の `--source` の既定の意味、共通の引数 `--offline`（GitHub に送らず、保存したスナップショットを古いものとして示す）、ダッシュボードの5つのファイルと警告（`CANONICAL_DASHBOARD_OCCUPIED`、`CANONICAL_DASHBOARD_FAILED`）の次の1手。
  8. 制約：main が sparse-checkout だと仕様が見えない（ST-2）。カタログへの Git の呼び出しは `GIT_ASKPASS` を通さない（ST-13）。登録済みのカタログへの `--no-schedule` は登録を外さない（外すのは `canonical remove`）。予行演習では `XDG_STATE_HOME` を必ず一時ディレクトリにする（`--no-schedule` でも基準を書くため）。`worktree remove` は SpecDock が置いたリンクだけなら `--discard-ignored` なしで消す。
  9. 検査のワークフローの見本は 0.3.0 以降で使う（版のタグは 0.3.0 から作るので、0.2.4 の版のファイルでは `pipx install` が失敗する）。
  10. エラーのコードと次の1手の一覧（下の R-436-04）。
- `scripts/migrate-to-canonical/README.md` の予行演習に、`XDG_STATE_HOME` を一時ディレクトリにする理由（`--no-schedule` でも基準を書く）を書く。

### R-436-03 CLI 参照と `help`

- `reference_cli.md` の冒頭の文の数（今は52）を53にし（表の行は53ある）、平らな置き場と ID、0埋めしない入力、canonical モードの `--slug` の拒否と `scope import github` の `--title` の扱い、既定のブランチ名 `<ID>`、`scope move` を書く。`docs/README.md` の数も53にする。
- I-4 と I-5 の新しいコード（`SCOPE_IN_PROGRESS`、`CANONICAL_PROGRESS_MARK_FAILED`、`CANONICAL_TITLE_IGNORED`、`DESCENDANT_STATUS_UNKNOWN`、`CANONICAL_BASE_HAS_SPECS`、`CANONICAL_CATALOG_PROTECTED`、`CANONICAL_WORKBENCH_SHARED` など）は、`canonical.md` のエラーの一覧に載せ、`reference_cli.md` からその一覧へ参照する。`work start` の `help` に `SCOPE_IN_PROGRESS` を、`work finish` の `help` に最大180秒の保存の待ちと `CANONICAL_SAVE_UNCONFIRMED` を、`scope import github` の `help` に `CANONICAL_TITLE_IGNORED` を書く。
- 配布する `cli-redesign-guide.html` のコマンドの一覧に `canonical` の8つと `scope move` を足し、数を53にする。
- `help`（`cli/catalog.py`）：
  - `canonical link` の Writes に、fetch の refspec の追加（`remote set-branches`）と、手元のブランチ `spec-dock/canonical` の付け替え（`update-ref`）を足す（I-2 の ST-9）。12章が書くものとする登録簿、定期の実行、基準もないので足す。
  - `scope create` と `scope import github`、`work start` の `help` に、schema 4 での置き場 `spec-dock/initiatives/<bucket>/<ID>/`、`--slug` の拒否、既定のブランチ名 `<ID>` を書く。従来モードの説明は消さない。
- 版3のリポジトリでの `--help` の文法（引数の一覧）は変えない。`help` の文はモードによらず1つなので、足した文は版3のリポジトリの `--help` にも出る。これは Epic の testability の「文書の中身」の変化として扱う（AC-436-09 の比較で許す差）。

### R-436-04 エラーのコードと次の1手の一覧（Epic の 12章、C8）

- 12章の表を実装に合わせる：`GITHUB_STRUCTURE_INVALID`（runtime にないコード）の行を、実装が返す構造の異常のコード（`KIND_LABEL_MULTIPLE`、`PARENT_MISSING`、`PARENT_INVALID`、`PARENT_FOREIGN_REPOSITORY`、`SUB_ISSUE_FOREIGN_REPOSITORY`、`DEPENDENCY_CYCLE` など）の行に直す。`CANONICAL_SAVE_UNCONFIRMED` は、変更の束を書く前に止まれば終了コード3（`failed`）、書いた後なら6（`partial`）。`CANONICAL_PROGRESS_MARK_FAILED`（`work start` と `work finish` の警告。作業中の印の付け外しの失敗）の行を足す。`CANONICAL_NOT_IMPLEMENTED` の行は「0.3.0 では返さない」とする。
- `canonical.md` のエラーの一覧は、runtime が公開する canonical モードのコードをすべて載せ、どれにも次の1手がある。対象は、`application/canonical_errors.py` のすべてのコードの定数（`START_LOCK_BUSY`、`OS_ACCESS_DENIED` を含む）、canonical の各モジュールとGitHub の構造の部品のコードの定数、canonical のモジュールに字面で書かれた `CANONICAL_*` のコード（`CANONICAL_REMOVE_FAILED` など）、`canonical check` の失敗の種類。一覧と実装の対応をテストで確かめる。
- 従来モードと共有の汎用のコード（`PRECONDITION_FAILED`、`SCOPE_NOT_FOUND`、`WORK_START_REQUIRED` など。共有の `dispatch()` が `ValueError` から作るもの）は、版3の出力を変えないため、この Issue では `recovery` を足さない（残るリスクとして報告書に書く）。
- 失敗のコードは、`recovery` に次の1手を必ず入れる（R-H2）。

### R-436-05 すべてのコマンドが答える（Epic の G7）

- 版4のリポジトリで、53のすべてのコマンドが、canonical の処理か、案内付きの拒否で動く。`CANONICAL_NOT_IMPLEMENTED` を返す経路を runtime から消す。

### R-436-06 横断のシナリオ

- 2つのクローン（状態の置き場 `XDG_STATE_HOME` を別にして、2台のPCの代わりにする）と偽の `gh` と一時の bare のリポジトリで、クローン A の `canonical link` → `scope create`（日本語の題名）→ 仕様の編集 → `canonical sync` → クローン B の `canonical link` と `canonical sync` で見える → B の `work start` → B で編集 → `work finish` までが通る。定期の実行の仕組みを systemd と常駐のプロセス（`loop`）の両方に注入して通す。

### R-436-07 引き継ぎの直し

- ツールの設定の判定は、環境変数 `CLAUDE_CONFIG_DIR` があれば、ユーザーの設定を `$CLAUDE_CONFIG_DIR/settings.json` から読み、示す1行の設定のファイルの場所もそれにする（I-2 の ST-12）。
- `canonical resume --push-local` は、状態の `adopt_remote_pending` が真のとき（`--adopt-remote` の取り込み直しの途中）、何も書かずに止まり、次の1手を示す（I-3 のゲート8 ST-1）。
- `migrate.py undo` は、作業の記録（`undo.jsonl`）がないとき、何も書かずに終了コード2で止まり、`--state-dir` の確かめを次の1手に示す（I-8 の ST-1）。
- `undo --apply` の後の `register --apply` が、取り消した作成を使い直さず、新しく作ることを、テストで守る（I-15 の P3）。

### R-436-08 版 0.3.0 と配布資産

- `pyproject.toml` の版と、配布資産の版のファイル（`spec-dock/system/spec-dock-version`）を 0.3.0 にする（`uv.lock` の自分の版も）。版のファイルの前の中身の SHA-256 を `static-inventory.json` の `known_old_sha256` に足す（C7）。変えた配布資産の `sha256` と前の値を同じく更新する。
- この worktree の利用側の `spec-dock/` を、0.3.0 の候補の wheel の `installation update` で上げる。宣言は版3のまま（従来モード）。

### R-436-09 btrfs での選択の記録の確かめ（実機の確かめで見つけた不具合。2026-10-30 の統括の判断 A）

- `work start` は、選択の記録を書いた直後の確かめで、btrfs の Linux（OrbStack の仮想マシンとそのコンテナ）でも記録を見つけ、`succeeded` を返す。原因は、`infra/work_target_store.py` が使い回したディレクトリの記述子を2回列挙していたことで、btrfs では読み切った記述子に新しい項目が出ない。この部品は従来モードの `work start` と共有で、直しは振る舞いの契約を変えず、btrfs の上でだけ誤った `partial` を `succeeded` にする（ext4 と APFS の出力は変わらない）。AC-15 の例外として、理由と影響を報告書に書く。

## スコープ

- 対象：上の R-436-01〜08。提供側の `src/spec_dock/`、`tests/`、`scripts/migrate-to-canonical/`、`AGENTS.md`、`README.md`、`pyproject.toml`、`uv.lock`、この worktree の `spec-dock/` の配布資産（`installation update` が書くもの）、この Issue の Scope のディレクトリ、Epic の `design.md` の12章の表（実装と合わせる直しだけ）。
- 対象外：従来モード（宣言の版3）の処理と `.meta.json` の読み書きのコードと、その振る舞いのテスト（AC-15）。本物の spec-dock の切り替え（I-10）、ほかのリポジトリ（I-12）、撤去（I-13）。版のタグの作成（マージの後に `release-tag.yml` が行い、統括が確かめる）。利用者の本物の設定での確かめ（I-10）。本物の GitHub への書き込み。
- 親の契約として守る境界：C1〜C11 の公開の形を変えない。新しいコマンドと引数を足さない（53のまま）。

## 失敗・境界条件

- 規則の節と使い方の文書は、版3のリポジトリでも配布される。版3のリポジトリでは、今までどおり仕様もコードと一緒にコミットすることを、節の最初に書く。
- `CLAUDE_CONFIG_DIR` が空の文字列のときは、ないものとして `~/.claude` を使う。相対パスか `~` で始まるときは、場所を決められないので、Claude Code の判定を「判定できない」（`CANONICAL_TOOL_SETTING_UNKNOWN`）にする。
- Epic の `design.md` の9章は、ユーザーの設定を `~/.claude/settings.json` と固定で書いている。この Issue では9章を直さず、食い違いを報告書と統括への申し送りに書く。
- `resume --push-local` の拒否は、`adopt_remote_pending` が偽で、理由が `remote_deleted` のときの今の動き（作り直す）を変えない。
- `undo` の拒否は、`--apply` の有無にかかわらず、作業の記録のファイルがないときだけ。ファイルがあって取り消すものがないときは、今のとおり終了コード0。
- `installation update` が知らない中身の配布資産で止まったら、手で直さずに止まり、統括に報告する。

## 受け入れ条件

- **AC-436-01**（R-436-01、Epic の AC-14）：配布するスキルと `AGENTS.md` の規則の節が、10章の項目と R-436-01 の追加の項目をすべて含むことを、テストが項目ごとの語の対応表（項目 → 1つ以上の語）で確かめる。2つの節の項目がそろうこと、2つの破壊的なコマンドの一覧に `canonical remove` があることも確かめる。白紙のエージェント（設計書を渡さない新しいサブエージェント。sonnet/medium）に規則の節だけを渡し、版4のリンク済みの一時のリポジトリ（0.3.0 の候補の console と、PATH の偽の `gh`）で、次の課題をさせる：(1) 指定の Scope の `design.md` を読んで1行足す、(2) ある語を含む仕様を検索する、(3) `*.conflict-*` のファイルを元のファイルに統合して消す、(4) ある Scope の親を確かめる、(5) 作業を終える手順を答える。合格の基準：仕様に Git の操作（`git add`、`commit`、`stash`、`reset`、`checkout`、`clean`）を使わない、検索でパスを明示する、別名ファイルを統合して消す、ディレクトリの名前と位置を変えない、親を `scope show <ID> --json` で確かめる、終わりを `spec-dock work finish` と答える。試行の記録（使ったコマンド）と判定を報告書に書く。
- **AC-436-02**（R-436-02、Epic の AC-07）：`canonical.md` が R-436-02 の1〜10の節を持ち、4つの文書と `README.md` から参照されることをテストで確かめる。`canonical status` が示す Claude Code と Codex の1行（コードの定数から作った文字列）が、`canonical.md` にそのまま書かれていることをテストで確かめる。
- **AC-436-03**（R-436-03）：`reference_cli.md` と `cli-redesign-guide.html` が53のコマンドの行を持ち、`LEAF_PATHS` と一致することをテストで確かめる。`canonical link --help` の Writes に refspec とブランチの付け替えがあり、`scope create issue --help` と `work start --help` に `<bucket>/<ID>` と `<ID>` のブランチ名があることを確かめる。版3のリポジトリの `--help` の引数の一覧は変わらない（今のテストが通る）。
- **AC-436-04**（R-436-04）：R-436-04 の対象のコードがすべて `canonical.md` のエラーの一覧にあり、一覧のほかのコードも runtime のソースに字面があり、一覧のどの行にも次の1手があることをテストで確かめる。Epic の12章の表の3つの直し（`CANONICAL_SAVE_UNCONFIRMED` の終了コード、`CANONICAL_PROGRESS_MARK_FAILED` の行、`GITHUB_STRUCTURE_INVALID` の行の置き換え）と、`CANONICAL_NOT_IMPLEMENTED` の行の注記がされている。
- **AC-436-05**（R-436-05、Epic の G7）：runtime のソースに `CANONICAL_NOT_IMPLEMENTED` がない。`LEAF_PATHS` の53のどれもが、canonical の表、リポジトリによらない表、またはモードによらない経路（`installation`、`help`、`completion`）に入ることをテストで確かめる。版4のリンク済みのクローンと偽の `gh` で、53のコマンドのそれぞれを1回実行し、どれも例外で落ちず、JSON の結果を返し、`CANONICAL_NOT_IMPLEMENTED` を返さず、canonical モードのコード（`CANONICAL_*`、`GITHUB_*`、`SCOPE_KIND_CHANGED`）の失敗なら `recovery` があることを確かめる。
- **AC-436-06**（R-436-06、Epic の AC-02、AC-13、AC-16、AC-18 の自動の部分）：横断のシナリオのテストが、systemd と `loop` の注入の両方で通る。A の `worktree create` のworktreeから、保存の前に A の編集が読める。B で `canonical sync` の後に A の Scope のファイルが読める。B の新しいスナップショットの後の `scope show` と `scope list` が全体の取り直しをしない。`work finish` が B の編集を push してから Issue を閉じる。
- **AC-436-07**（R-436-07）：`CLAUDE_CONFIG_DIR` の下の設定の1行を判定に使い、示す場所もそれになるテストと、相対の `CLAUDE_CONFIG_DIR` が `CANONICAL_TOOL_SETTING_UNKNOWN` になるテスト。`adopt_remote_pending` のときの `resume --push-local` が何も push せずに止まるテスト。作業の記録のない `undo`（`--apply` の有無）が終了コード2で止まるテスト。`undo --apply` の後の `register --apply` が新しい Issue を作るテスト。
- **AC-436-08**（R-436-08）：`pyproject.toml`、版のファイル、`uv.lock` が 0.3.0 で、版のファイルの一致のテスト（I-7）が通る。wheel を作り、外の一時の環境に入れて、`spec-dock --version` が 0.3.0、`spec-dock help` と `spec-dock canonical --help` が動く。この worktree の `spec-dock/` の `installation show` が、`spec-dock/workspace.json`（`init_only` の宣言。dogfood の宣言は 0.2.4 のときから配布物と違うバイト列で `unknown`、新しく作った版3の作り物では `known-old` になりうる。どちらも Epic の testability の許した分類）のほかの配布資産をすべて `current` と示し、宣言が版3のままで、`spec-dock workspace validate` と `.github/scripts/specdock-ci-validate.sh` が通る。
- **AC-436-09**（Epic の AC-15）：`make lint` と `uv run pytest` の全体が通る。版3の振る舞いのテストを、Epic の testability の「従来モードの回帰」の許された変更のほかに変えていないことを、`git diff ea3d3c9ee` で確かめ、変えたテストを報告書に一覧で書く（canonical モードのテストを変えたもの、例えば `CANONICAL_NOT_IMPLEMENTED` の暫定の経路のテストは、別の区分で書く）。版3の作り物のリポジトリで、0.2.4（`ea3d3c9ee` から作った wheel）と 0.3.0 の候補の代表のコマンド（`scope list`、`scope show`、`dependency check`、`workspace validate`、`workspace validate --ci`、`workspace doctor`、`workspace sync`、`installation show`、`work start --dry-run`、`--help` のいくつか）の出力を比べ、差が、先に決めた許す差（`package_version` などの版の値、配布資産の分類、`help` の文）だけであることを確かめ、結果を報告書に書く。
- **AC-436-10**（Epic の AC-18、AC-07 の実機）：実機で次を確かめ、結果と確かめられなかったことを報告書に書く。
  - 確かめられないもの（資格情報が要るもの、利用者の設定を変えないとできないもの）は「未確認」と理由を書く。
  - OrbStack の Ubuntu の仮想マシン（systemd）：一時の bare のリポジトリを相手に、2つのクローンで link、systemd のタイマーでの同期、別のクローンから見えること（AC-02）、同じファイルの競合で別名ファイルが残ること（AC-03）、`work finish` が保存を待って閉じること（AC-13。偽の `gh`）。systemd の止め方の設定（`KillMode`、`TimeoutStopSec`）が要るか。
  - Docker のコンテナ（systemd なし、中でクローン）：常駐のプロセスで同じことと、起動し直しの後の `canonical link`。ホストのフォルダーをマウントしたチェックアウトで `CANONICAL_FOREIGN_CHECKOUT` で止まり、ホストの記録が変わらないこと。Git 2.38 ちょうどの環境での `canonical link`。
  - Linux の Codex のサンドボックス（Landlock）での `canonical status` の判定と `flock`（仮想マシンに Codex を入れ、一時の `CODEX_HOME` の `codex sandbox` で。資格情報は入れない）。
  - macOS：外の console（0.3.0 の候補の wheel）での `work finish`（一時の `HOME`、`XDG_STATE_HOME`、PATH の偽の `gh`、`--no-schedule` のリンクと、待ちの間に別のプロセスで回す `canonical sync`。カタログのworktreeだけの設定で push を一時の bare のリポジトリに向け、利用者の launchd と本物の GitHub に触れない）。Codex のサンドボックスでの `canonical status` の1行と `writable_roots` の効き目（一時の `CODEX_HOME` と `codex sandbox`）。Claude Code の1行を、一時の `CLAUDE_CONFIG_DIR` のユーザーの設定ファイルに書いたときの SpecDock の判定。Claude Code 自身がその1行で書けるかは、利用者の資格情報を写さずには確かめられないので、`--settings` のファイルで確かめ、ユーザーの設定ファイルでの動きは I-10 に残す。
  - 作った仮想マシン、コンテナ、イメージ、一時ディレクトリを消したこと。資格情報を写していないこと。

- **AC-436-11**（R-436-09）：読み切った記述子では新しい項目を返さない偽の列挙で `WorkTargetStore.publish` が `SelectionPublicationUnknown` にならないテスト（直しの前に落ちることを確かめる）。btrfs の実機（OrbStack の仮想マシン）で `work start` が `succeeded` を返す。版3の既存のテストは変えない。

## 制約・前提

- 従来モードの処理、`.meta.json` の読み書き、版3の振る舞いのテストを変えない（AC-15）。
- テストは外のネットワークを使わない（偽の `gh`、一時の bare のリポジトリ、`XDG_STATE_HOME` と `--state-root` は一時ディレクトリ）。
- 利用者の環境（`~/.claude/settings.json`、`~/.codex/config.toml`、`~/Library/LaunchAgents/`、`~/.config/systemd/user/`、`~/.local/state/spec-dock/`、ほかのリポジトリ）を変えない。本物の GitHub にラベル、sub-issue、依存、`spec-dock/canonical` を作らない。本物の spec-dock のリポジトリで `canonical` のコマンドを実行しない。
- 手元の CI の Lima の仮想マシン `spec-dock-ci`、`ci-shadow`、それらのランナーと LaunchAgent に触れない。確かめの仮想マシンとコンテナは1台ずつ動かし、終わったら消す。
- ChatGPT、Deep Research などの OpenAI を前提とするスキルは使わない（利用者の設定で無効）。
