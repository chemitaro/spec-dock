# 導入・移行・保全（Current）

## 外部CLI

対応OSはLinuxとmacOS、Pythonは3.10以上です。Windowsを含む他のOSでは業務操作を開始せず `UNSUPPORTED_PLATFORM`（exit 3）を返します。help・version・completionはrepositoryなしでも利用できます。直接作業記録はPOSIX identityのみを受け付け、未知の記録を自動変換・削除しません。

package managerでレビュー・通常試験が済んだwheelをworktree外へ導入します。例えば `uv tool install /absolute/path/spec_dock-VERSION-py3-none-any.whl` です。PATH上の `spec-dock` が全コマンドの入口です。packageの更新とcheckoutのstatic資産更新は別操作です。

`spec-dock/scripts/spec-dock` はPATH上の外部consoleへ引数と終了値を渡すshimです。Git共有controlやcheckout内Pythonを探しません。旧branchの古いshimが戻っても外部 `spec-dock` は直接使えます。外部consoleがなければ導入/PATH確認へ戻り、自動installや旧engineへのfallbackはしません。

## canonical モードへの移行

SpecDock 0.5.0 は、`spec-dock/workspace.json` の `schema_version` が 4 のリポジトリ（canonical モード）だけを扱います。版3の宣言のリポジトリでは、`canonical check` のほかのどのコマンドも、何も書かずに `CANONICAL_NOT_MIGRATED`（終了コード3）で止まります（`canonical check` は版3の宣言を問題の1件として返します）。

版3のまま残ったリポジトリは、SpecDock 0.4.2（両方のモードを持つ最後の版）を入れ直し、版のタグ `v0.4.2` の `scripts/migrate-to-canonical/README.md` の手順で、リポジトリごとに一度だけ移します。移行のスクリプトは 0.5.0 のリポジトリから外したので、タグから取り出します（`git show v0.4.2:scripts/migrate-to-canonical/README.md`）。その手順書が「0.3.0」「`v0.3.0`」と書くところ（移行の前に上げる配布資産と、CI の SpecDock の固定の版、撤去の後の戻し方）は、「0.4.2」「`v0.4.2`」と読み替えます。移した後に 0.5.0 へ上げます（「0.5.0 への更新」）。

移行の後の使い方、ツールの設定の1行、同期が止まったときの扱いは[canonical モードの使い方](canonical.md)にあります。`installation init` は版4の宣言を置くので、新規導入のリポジトリは canonical モードで始まり、`spec-dock canonical link` が要ります。

## 0.4.0 への更新

0.4.0 は、canonical モード（宣言の版4）のリポジトリで、新しく作る Scope の要件・設計・計画を CUE で書く版です。版3のリポジトリの動きは変わりません。

- パッケージを 0.4.0 に上げた後、各リポジトリで `spec-dock installation update` を実行して配布資産を上げます。新しい雛形 `spec-dock/templates/cue/<種類>/`、デザインシステム `spec-dock/design-system/`、ガイド `spec-dock/docs/authoring/cue.md` と `explanation.md`、スキルが入ります。上げる前の配布資産のままだと、`scope create` と `scope import github` は GitHub に何も書かずに `SCOPE_TEMPLATES_OUTDATED` で止まります。
- CLI の契約の変更（版4だけ）：
  - `spec-dock scope create` と `spec-dock scope import github` に、`--assurance <light|standard|strict|critical>` と `--assurance-reason <理由>` が必須になりました。ないと何も読まず何も書かずに `ASSURANCE_REQUIRED`（終了コード2）で止まります。これらを呼ぶスクリプトや手順に、2つの引数を足します。版3のリポジトリで付けると `CANONICAL_NOT_MIGRATED` で止まります。
  - 新しい Scope は CUE の Scope（`requirement.cue`、`design.cue`、`plan.cue`、`explanation.html`、`report.md`）です。既存の Markdown の Scope は移さず、そのまま動きます。
  - 公開の葉が2つ増えて55になりました：`spec-dock scope check <ID>`（CUE の Scope を検査する）と `spec-dock scope render <ID>`（要件・設計・計画を HTML に描く）。
  - `spec-dock scope show --json` は、`data.result.assurance`（`level`、`reason`、`source`）を返します。
  - CUE の Scope の `spec-dock work finish` は、閉じる前に `scope check` と同じ検査を行い、誤りが残れば何も書かずに `SCOPE_CHECK_FAILED` で止まります。
- 道具：CUE の Scope の検査には `cue` v0.17.1 以上が PATH に要ります（例 `go install cuelang.org/go/cmd/cue@v0.17.1`）。ないと `CUE_NOT_FOUND` で止まります。Markdown の Scope と版3のリポジトリには要りません。
- 書き方は [CUE Authoring Guide](authoring/cue.md) と [Explanation Guide](authoring/explanation.md)、エラーと次の1手は [canonical モードの使い方](canonical.md) にあります。

## 0.4.1 への更新

0.4.1 は、0.4.0 の後に入れた CUE の書き方と検査の改善を届ける版です。動きの変更は小さく、版3のリポジトリには影響しません。

- パッケージを 0.4.1 に上げた後、各リポジトリで `spec-dock installation update` を実行して配布資産を上げます。0.4.0 の配布資産のままでも動きますが、ガイド（`authoring/cue.md`、`issue-plan.md`、`scope-layering.md`）、`canonical.md`、`reference_cli.md`、Issue の `plan.cue` の雛形が新しくなります。
- 主な改善：
  - 個別のコマンドの `--help` に、共通の引数が出ます。
  - 既定値のある列挙（手順の `status` など）に許されない値を書いたときの `CUE_INVALID` が1件にまとまり、`hint` が日本語になりました。
  - Issue の `plan.cue` の雛形は、1手順を1行にし、`status` を `title` と `realizes` のすぐ後に置きます。
- CLI の契約の変更（版4だけ）：
  - `spec-dock scope check`：`CUE_INVALID` に、既定値との衝突の行を残す `details.cue_related` が付きます。保証レベルが light でテストが1つもない Issue には、警告 `SPEC_NO_TESTS` が付きます（誤りではありません）。
  - `spec-dock scope render` に `--design-system <file|inline>` が付きました（既定は `file`）。`inline` は `ds.css`、`ds.js`、`marked` を HTML に埋め込み、デザインシステムがなければ `DESIGN_SYSTEM_MISSING`（終了コード3）で止まります。Python の入口 `render_scope_html` には `embed_design_system` が付きました。

## 0.4.2 への更新

0.4.2 は、0.4.1 の後に入れた canonical の同期と CI の見本の改善を届ける版です。動きの変更は小さく、版3のリポジトリには影響しません。

- パッケージを 0.4.2 に上げた後、各リポジトリで `spec-dock installation update` を実行して配布資産を上げます。0.4.1 の配布資産のままでも動きますが、`canonical.md`（「CI の費用と、見本の合わせ方」の節と、不要ファイルの説明）と CI の見本 `ci/spec-dock-check.yml`（費用と合わせ方の注記）が新しくなります。
- 主な改善：
  - OS が作る不要なファイル（`.DS_Store`、`._*` など）を、canonical の同期で保存しません。不要ファイルの削除は、大量削除の保留に数えません。
  - CI の見本に、費用と合わせ方の注記が付きました。
- CLI の契約の変更（版4だけ）：
  - `spec-dock canonical status` の `changes` に `junk_files` が付きます。前の版が保存してしまった不要ファイルの一覧で、カタログから消すと次の周期が削除を保存します。
  - `spec-dock canonical remove` は、保存しないファイルがカタログに残っていると、何も消さずに `CANONICAL_IGNORED_FILES_PRESENT`（終了コード3）で止まります。示されたファイルを消すか移してから、もう一度実行します。

## 0.5.0 への更新

0.5.0 は、従来モード（宣言の版3、`.meta.json`）を撤去し、canonical モードだけを持つ版です。すべてのリポジトリが版4に移った後に入れます。

- 上げる手順：使っているすべてのリポジトリ（とそのクローン）の `spec-dock/workspace.json` が `"schema_version": 4` であることを確かめてから、パッケージを 0.5.0 に上げ、各リポジトリで `spec-dock installation update --target <チェックアウト> --backup-dir <新しい外のディレクトリ> --yes` を実行して配布資産を上げ、通常の PR でコミットします。CI の見本は `spec-dock/system/spec-dock-version` の版（0.5.0）の SpecDock を入れて動きます。
- 撤去したもの：
  - 版3の宣言を読むと、`canonical check` のほかのどのコマンドも、何も読み書きせずに `CANONICAL_NOT_MIGRATED`（終了コード3）で止まり、`recovery` に「SpecDock 0.4.2 を入れ直し、版のタグ v0.4.2 の scripts/migrate-to-canonical/README.md に従って移す」を示します（「canonical モードへの移行」）。`installation` のコマンドと `workspace doctor --raw` も止まります。版5以上と壊れた宣言は、今までどおり `PRECONDITION_FAILED` です。
  - コマンド `spec-dock workspace migrate` と `spec-dock workbench copy` がなくなりました（引数の誤り、終了コード2）。公開の葉は 53 になりました。Scope の `.workbench/` はカタログの中にあり、どの worktree からも見えるので、写す必要はありません。
  - 引数 `workspace validate --ci`（CI では `spec-dock canonical check`）、`workspace sync --source local` と `dependency check --source local`（`--source` は `github` だけ。省くとスナップショットを読みます）、`scope create` と `scope import github` の `--slug` がなくなりました（引数の誤り）。`artifact create --slug` は残ります。
  - エラーのコード `CANONICAL_NOT_APPLICABLE` と `CANONICAL_WORKBENCH_SHARED` は、もう返りません。
  - `.md` の Scope の雛形 `spec-dock/templates/{initiative,epic,issue}/`（各 `requirement.md`、`design.md`、`plan.md`、`report.md`、`.workbench/README.md`）と、入れ子の置き場の `epics/rules.md`・`issues/rules.md` の先だった `spec-dock/docs/rules/initiative/epics.md`・`spec-dock/docs/rules/epic/issues.md` を外しました。`installation update` は、変えていなければ退避してから消します。変えていれば手で合わせるよう止まります（`legacy static resource is modified or unknown; merge manually`）。
  - CUE の雛形の `report.md`（`spec-dock/templates/cue/<種類>/report.md`）の前付けから `タイトル:` と `親:` の行を外し、作るときにその2行を除く処理と「詳細:」のリンクを書き換える処理をやめました。作られる `report.md` は 0.4.2 と同じです。0.4.2 の配布資産のまま 0.5.0 で作ると、その2行が残ります（正本ではありません）。`installation update` の後は残りません。
  - 移行のスクリプト `scripts/migrate-to-canonical/` を、spec-dock のリポジトリから外しました（版のタグ `v0.4.2` に残ります）。
- 0.4.2 の後に入った改善：
  - `installation update`（`--dry-run` と、途中で止まった場合を含む）が `.claude/skills/spec-dock*` の古い写しを外すとき、リンクがない枠ごとに、外枠の `warnings[]` に `CLAUDE_SKILL_LINK_MISSING`（`details`：`slot`、`link_target`、`command`）が出ます。終了コード、`status`、`effects`、`data.result` は変わりません。示された `command` でリンクを置きます（SpecDock はリンクを作りません）。
  - 配布する `spec-dock/.gitignore` に `!**/.workbench/` を足しました。ルートの `.gitignore` が `.workbench/` を無視していても、`spec-dock/` の下の `.workbench/README.md`（雛形の README を含む）がコミットの対象になります。ほかの中身は無視のままです。すでに使っているリポジトリは、更新の後に `git add spec-dock/templates` で、それまで無視されていた雛形の README を足してコミットします。
- 戻し方：0.5.0 に問題があれば、パッケージを 0.4.2 に戻します。0.4.2 は canonical モードと CUE の Scope を持つので、移したリポジトリはそのまま動きます。配布資産を 0.5.0 に上げた後なら、版のファイル（`spec-dock/system/spec-dock-version`）を戻す PR も作ります（CI の見本はその版を入れるため）。

## 新規導入

```sh
spec-dock installation init /absolute/project --dry-run --json
spec-dock installation init /absolute/project --yes --json
spec-dock installation show --target /absolute/project --json
spec-dock --project /absolute/project workspace validate --json
```

対象は正確なGit worktree root一つです。initは新writerのworkspace宣言と静的資産だけを置き、既存の配布先fileがあれば書込み前に停止します。main/linkedを一括導入せず、runtime、直接作業記録、Git内の独自領域を作りません。

## static資産の更新・削除

```sh
spec-dock installation update --target /absolute/project --dry-run --json
spec-dock installation update --target /absolute/project --backup-dir /absolute/new-static-backup --yes --json
# 正確な対象のtool資産削除が許可されている場合だけ
spec-dock installation uninstall --target /absolute/project --backup-dir /absolute/new-uninstall-backup --yes --json
```

版4（新writer）のworkspaceで既知path/hashのstatic filesだけを変更します。更新は欠けたfileを補い、既知旧bytesを置換し、既知旧runtime filesと外した雛形を個別退役させます。削除も所有権検証を行い、workspace宣言・ignore規則・仕様・Artifact・Workbench・直接記録・directoryを残します。未知改変は人間によるmergeへ戻し、directoryごとの削除はしません。

旧static bytes/modeを `backup/static/<relative>` へ保存し、別の一時場所へ実際に復元して比較します。backup先は全clone worktree、Git metadata、installed packageの外で、既存の通常parent下の新しい絶対pathです。既存backupを再利用しません。

## 途中で停止した場合

dry-runは書込み・backup・GitHub更新・Start lockを行いません。適用途中のexit6は確認済み・unknown・未実施effectsを区別します。残った候補、backup、実体pathを保全し、観測してから新しい明示操作を判断します。自動巻戻しやjournal replayはありません。コードrevertはGitHubへの完了・作成効果を元へ戻しません。
