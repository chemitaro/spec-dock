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
- 戻し方：0.5.0 に問題があれば、パッケージを 0.4.2 に戻します。0.4.2 は canonical モードと CUE の Scope を持つので、配布資産を 0.5.0 に上げる前のリポジトリはそのまま動きます。配布資産を 0.5.0 に上げた後なら、その更新の PR（版のファイル `spec-dock/system/spec-dock-version` を含む）を `git revert` して、配布資産を 0.4.2 のバイトに戻します。版のファイルだけを戻すと、0.4.2 の `canonical check` が 0.5.0 の資産を知らない変更として CI を止め、0.4.2 の `scope create` が外した `docs/rules/initiative/epics.md`・`docs/rules/epic/issues.md` を求めて止まります（0.4.2 の `installation update` も 0.5.0 のバイトを知らないので、戻す手段になりません）。

## 0.5.1 への更新

0.5.1 は、0.5.0 の後に入れた、確認と実行の間の変化・部分失敗の返し方・宣言の検査の直しを届ける版です。canonical モード（宣言の版4）だけの版で、コマンドと JSON の形は増えません。

- パッケージを 0.5.1 に上げた後、各リポジトリで `spec-dock installation update --target <チェックアウト> --backup-dir <新しい外のディレクトリ> --yes` を実行して配布資産を上げ、通常の PR でコミットします。0.5.0 の配布資産のままでも動きますが、`reference_cli.md`、`cli-redesign-guide.html`、スキル `SKILL.md`、`finalize-artifact.py`、この `migration.md` が新しくなります。CI の見本は `spec-dock/system/spec-dock-version` の版（0.5.1）の SpecDock を入れて動きます。
- 契約の変更：
  - `scope close --reason completed` と `work finish` は、子孫がすべて完了（completed）か不採用（not-planned）で閉じていれば親を閉じます。0.5.0 では不採用の子孫があると終了コード3で止まっていました。開いている子孫と状態が分からない子孫があれば、今までどおり `DESCENDANT_NOT_COMPLETED`（終了コード3）で止まります。
  - `canonical check` は、重複したキーを持つ宣言を `WORKSPACE_DECLARATION_INVALID`（`details.reason=duplicate-member`）の失敗1件にします。ほかのコマンドは、重複したキーを持つ宣言を版4として受け付けず、`PRECONDITION_FAILED`（終了コード3）で止まります。観測の間に消えた版3の worktree は、`workspace sync` と `work start` で unavailable の行になります。
- 確認と実行の間の変化（何も書かずに止まる）：
  - `scope close` と `scope reopen` は、端末での確認の後に直接の選択が変わっていれば、何も書かずに `PRECONDITION_FAILED`（終了コード3）で止まります。
  - `scope create` は、確認の後に `origin` が変わっていれば止まります。何も書いていなければ `PRECONDITION_FAILED`（終了コード3）、種類のラベルを作った後なら `CANONICAL_WRITE_INCOMPLETE`（`partial`、終了コード6）、Issue を作った後なら `SCOPE_PUBLICATION_INCOMPLETE`（`partial`、終了コード6）です。
  - `worktree remove` は、無視されたものが `spec-dock/initiatives` のリンクだけかを、削除の直前（`--unlock` なら unlock の後）まで繰り返し確かめます。確かめの後に無視されたファイルができていれば、`--discard-ignored` なしでは何も消さずに止まります。止まる時点で終了コードが違います：最初の判定では `PRECONDITION_FAILED`（終了コード3）、unlock の前の確かめでは `WORKTREE_REMOVE_FAILED`（`failed`、終了コード3）、unlock の後では `WORKTREE_REMOVE_FAILED`（`partial`、終了コード6）です。
- 部分失敗の返し方：
  - `artifact create` と `artifact import file` は、`artifacts/` を作った後の失敗を `ARTIFACT_PUBLICATION_INCOMPLETE`（`partial`、終了コード6）で返します。`effects` に `artifact.directory` が付き、作ったディレクトリは残ります。
  - `scope delete` は、途中で失敗したときの `effects` を起きたとおりに返します（例：`selection.clear` が succeeded、`scope.delete` が unknown）。
- スキル `spec-dock-grill-with-docs` の `finalize-artifact.py` は、`spec-dock/initiatives` のカタログへのリンク越しの Artifact のパスを受け付けます。契約の変更はありません。
- 戻し方：0.5.1 に問題があれば、パッケージを 0.5.0 に戻します。配布資産を 0.5.1 に上げた後なら、その更新の PR（版のファイル `spec-dock/system/spec-dock-version` を含む）を `git revert` して、配布資産を 0.5.0 のバイトに戻します。版のファイルだけを戻すと、0.5.0 の `canonical check` が 0.5.1 の資産を知らない変更として CI を止めます（0.5.0 の `installation update` も 0.5.1 のバイトを知らないので、戻す手段になりません）。

## 0.6.0 への更新

0.6.0 は、HTML のダッシュボードを届ける版です。canonical モード（宣言の版4）だけの版で、今までの Markdown・PlantUML のダッシュボードは撤去されました。

- パッケージを 0.6.0 に上げた後、各リポジトリで `spec-dock installation update --target <チェックアウト> --backup-dir <新しい外のディレクトリ> --yes` を実行して配布資産を上げ、通常の PR でコミットします。0.5.1 の配布資産のままでも動きますが、`reference_cli.md`、`canonical.md`、`cli-redesign-guide.html`、`docs/README.md`、`.gitignore`、この `migration.md` が新しくなります。CI の見本は `spec-dock/system/spec-dock-version` の版（0.6.0）の SpecDock を入れて動きます。
- 最初の1手：`spec-dock dashboard serve` を実行してブラウザーで開きます（既定は `http://127.0.0.1:47800`）。iPhone など別の端末からは `spec-dock dashboard serve --tailscale` で、Tailscale の住所にも待ち受けます。
- 新しいコマンド（公開のコマンドは 53 から 61 になります）：
  - `dashboard summary`（#528）：リポジトリの概況を JSON `specdock.dashboard-summary/v1` で返します。
  - `dashboard serve`・`dashboard hide`・`dashboard show`・`dashboard list`（#529）：利用者ごとに1つのサーバーを `127.0.0.1:47800` で前面で動かし、登録した全リポジトリを見るだけで配ります。`hide` と `show` はリポジトリの表示を切り替え、`list` は登録を示します。
  - `dashboard service install`・`dashboard service status`・`dashboard service uninstall`（#530）：ログインのときに起動する常駐を、明示して入れたときだけ入れます（macOS は launchd、Linux は systemd のユーザーの単位。定期の同期の常駐とは別のラベル）。`installation update` や `canonical link` は入れません。
  - 版の更新の後、常駐は起動し直します（サーバーが終了コード75で終わり、launchd と systemd が新しい版で起動し直す）。前面の `dashboard serve` は、利用者が起動し直します。
- 新しい契約：
  - 画面の道 `/r/<host>/<owner>/<name>/scopes/<ID>`、`?embed=1`、API、埋め込みの契約 `specdock.embed/v1`、`frame-ancestors`。CORS を許すのは `/ds/` と `/vendor/` だけです。詳しくは `reference_cli.md` の「ダッシュボードのサーバーの契約」。
  - 主な新しいエラーのコード（各コマンドのほかのコードは `reference_cli.md` のコマンド表にあります）：`DASHBOARD_SERVICE_UNSUPPORTED`・`DASHBOARD_SERVICE_FAILED`（終了コード3）、`DASHBOARD_STATE_ROOT_INVALID`（終了コード2）。
- 利用者の状態の置き場（`~/.local/state/spec-dock/`）に増えるもの：`dashboard/server.json`（`specdock.dashboard-server/v1`）、`dashboard/repositories.json`（`specdock.dashboard-repositories/v1`）、`dashboard/seen.json`（`specdock.dashboard-seen/v1`）、`dashboard/server.lock`。常駐を入れたときだけ、launchd の plist か systemd の単位が増えます。`dashboard/service.log` が増えるのは launchd のときだけで、systemd では出力が journal（`journalctl --user -u spec-dock-dashboard`）に出ます。
- 構造のスナップショットは版2になります（#537。PR の状態を持つ）。新しい版は版1も読みます。前の版に戻すと、一度取り直します。定期の同期は PR の状態を取るため、成功か rate limit の後はリポジトリごとに約2分に1回、ほかの失敗が続く間は60秒に1回、GitHub の GraphQL に問い合わせます（1回あたり約3ポイント）。
- Markdown・PlantUML のダッシュボードの撤去（#533）：
  - `canonical status` の JSON から `dashboard` の項目と、`CANONICAL_DASHBOARD_OCCUPIED`・`CANONICAL_DASHBOARD_FAILED` の警告が消えます。
  - `canonical sync` の `dashboards_written` は常に0です（後の版で消す予定）。
  - `canonical remove` は、5つのファイルを消しません。`state.json` に dashboard を書きません（前の版に戻しても読めます）。
  - 配布の `spec-dock/.gitignore` から、`dashboard.md`・`tree.puml`・`tree-all.puml`・`deps-issues.puml`・`deps-raw.puml` の5つの名前が外れます。`installation update` の後、残っているこれらのファイルが `git status` に出ます。使わないので、消してかまいません（Git で管理していなければ、ただ消します）。
- 戻し方：0.6.0 に問題があれば、常駐を入れていれば先に `spec-dock dashboard service uninstall` を実行し、パッケージを 0.5.1 に戻します。配布資産を 0.6.0 に上げた後なら、その更新の PR（版のファイル `spec-dock/system/spec-dock-version` を含む）を `git revert` して、配布資産を 0.5.1 のバイトに戻します。版のファイルだけを戻すと、0.5.1 の `canonical check` が 0.6.0 の資産を知らない変更として CI を止めます（0.5.1 の `installation update` も 0.6.0 のバイトを知らないので、戻す手段になりません）。

## 0.7.0 への更新

0.7.0 は、人のタスク（`spec-dock todo`）を届ける版です。canonical モード（宣言の版4）の版で、カタログの形式（format 1）、`workspace.json` の版（4）、構造のスナップショットは変わりません。

- パッケージを 0.7.0 に上げた後、各リポジトリで `spec-dock installation update --target <チェックアウト> --backup-dir <新しい外のディレクトリ> --yes` を実行して配布資産を上げ、通常の PR でコミットします。`todo` のコマンドはパッケージだけで使えますが、配布のスキルの「人のタスク」の規則は静的な資産なので、`installation update` で入れ替わります。0.6.0 の配布資産のままでも動きますが、スキル（`.agents/skills/spec-dock/SKILL.md`）、`docs/todo.md`（新しい）、`docs/README.md`、`docs/guide.md`、`canonical.md`、`reference_cli.md`、`cli-redesign-guide.html`、この `migration.md` が新しくなります。CI の見本は `spec-dock/system/spec-dock-version` の版（0.7.0）の SpecDock を入れて動きます。
- 最初の1手：`spec-dock todo list` を実行します。`todos/` は最初の `todo add` が作るので、それまでは空の一覧が返り、`todo check` は「記録がない」で成功します。使い方は `spec-dock/docs/todo.md` にあります。
- 新しいコマンド（公開のコマンドは 61 から 71 になります。#549・#550）：`todo add`・`todo list`・`todo show`・`todo update`・`todo done`・`todo snooze`・`todo cancel`・`todo reopen`・`todo check`・`todo settings`。
  - 人にしかできない判断・確認・操作を、そのリポジトリのカタログの `todos/<YYYY-MM>/t-xxxx.json` に1件1つの記録（`specdock.todo/v1`）として登録して追います。GitHub には何も送りません。
  - `todo list --all-repositories`・`--repository R`：この PC の登録簿にある全リポジトリの人のタスクを集めます（`specdock.todo-list/v1`、`mode: repository` か `all_repositories`）。`todo show <REF>`（`owner/name/t-xxxx`）は、チェックアウトの外から1件を返します。
  - `dashboard summary`（と API の `/api/v1/r/<repo>/summary`）に `todos`（`open`・`blocking`・`overdue`）の数が足されます。読めないときは `status: unavailable` で、要約は成功します。
  - 設定は3段です。初めの値 < 利用者の設定（`$XDG_CONFIG_HOME/spec-dock/config.json`、`specdock.config/v1`）< リポジトリの設定（`todos/settings.json`、`specdock.todo-settings/v1`）。SpecDock は設定のファイルを作りません。なくても初めの値で動きます。
  - `todo check` は、Python の検査に加えて、`cue`（v0.17.1 以上）があれば CUE の型でも確かめます。なければ警告 `TODO_CUE_SKIPPED` を出して Python の検査で決めます。
  - 主な新しいエラーのコード（全部は `reference_cli.md`）：`TODO_*`（`TODO_INVALID`、`TODO_NOT_FOUND`、`TODO_SUBTASKS_OPEN`、`TODO_CHECK_FAILED`、`TODO_REPOSITORY_UNREADABLE`、`TODO_REGISTRY_UNREADABLE` など）。`canonical.md` に次の1手があります。
- 配布するスキルと文書（#551）：スキルに「人のタスク」の規則（登録する場面としない場面、`todo add --by agent --role --kind`、束、`todo done --record` での閉じ方）が足されます。`docs/todo.md` が新しく配られ、`canonical.md`、`docs/README.md`、`docs/guide.md` が変わります。
- 構造の図（ホーム。#556・#560）：既定で、親が開いていれば終わった Scope も出し、図に出ている箱どうしの終わった依存も薄い線で出します。同じ段は活動順に並べます。配置は #560 で改まり、依存の矢印でつながったものは同じ行に左から右へ並び、つながっていないまとまりは画面の見える幅でまとまりの境目ごとに折り返して、ウィンドウの幅が変わると並べ直されます（#556 の「折り返さず右へ」を改めたものです。API と保存の形は変わりません）。ブラウザーの保存のキーが `specdock.graph.v1` から `specdock.graph.v2` になり、表し方・凡例などは引き継がれますが、「終わったものも」と依存の線の選択は一度だけ新しい既定に戻ります。構造の API の各 Scope に `active_at` が足されます。
- ダッシュボードに出すリポジトリの設定（#552）：利用者の設定 `config.json`（`specdock.config/v1`）の `dashboard` の節（`visible` と `repositories.<鍵>.visible`）と、カタログの根の `dashboard.json`（`specdock.dashboard-settings/v1`、`visible`）で決めます。優先は、初めの値（表示）< 利用者の `visible` < 利用者の `repositories` < リポジトリの `dashboard.json`。`dashboard hide` の印は常に隠します。壊れた設定は隠す側に倒れます（利用者の設定のファイルが壊れていると全リポジトリが隠れます）。
  - `dashboard list` の各行に `mark`・`config {visible, source}`・`hidden_by` が、data に `config_problems` が足されます。`dashboard hide`・`dashboard show` の data にも `mark`・`config`・`hidden_by` が足され、`show` は設定が隠すとき警告 `DASHBOARD_HIDDEN_BY_CONFIG` を出します。`dashboard summary` と `todo list` の `hidden` は設定を含む最終の値です。
  - 常駐の定義に、install のときの絶対の `XDG_CONFIG_HOME` が入ります。0.6.0 で常駐を入れ、`XDG_CONFIG_HOME` を使っている場合は、更新の後に `spec-dock dashboard service install` をやり直します。
- 前の版との同居：前の版の SpecDock が別の PC で同じカタログを同期しても、`todos/` はふつうのファイルとして保存と push がされ、検査に引っかかりません（前の版では `todo` のコマンドがないだけです）。
- 戻し方：0.7.0 に問題があれば、パッケージを 0.6.0 に戻します。配布資産を 0.7.0 に上げた後なら、その更新の PR（版のファイル `spec-dock/system/spec-dock-version` を含む）を `git revert` して、配布資産を 0.6.0 のバイトに戻します。版のファイルだけを戻すと、0.6.0 の `canonical check` が 0.7.0 の資産を知らない変更として CI を止めます（0.6.0 の `installation update` も 0.7.0 のバイトを知らないので、戻す手段になりません）。カタログの `todos/` のファイルは残してかまいません（前の版のほかのコマンドに影響せず、版を上げ直せばそのまま読めます）。

## 0.8.0 への更新

0.8.0 は、ダッシュボードの文書の描画（#535）と人のタスクの画面（#554）を届ける版です。コマンドの数（71）、カタログの形式（format 1）、`workspace.json` の版（4）は変わりません。足すものだけで、0.7.0 のコマンドと API は変わりません。

- パッケージを 0.8.0 に上げた後、各リポジトリで `spec-dock installation update --target <チェックアウト> --backup-dir <新しい外のディレクトリ> --yes` を実行して配布資産を上げ、通常の PR でコミットします。変わる配布資産は `docs/reference_cli.md`、`docs/authoring/cue.md`、Issue の計画の雛形 `templates/cue/issue/plan.cue`、この `docs/migration.md`、版のファイル `spec-dock/system/spec-dock-version`（0.8.0）の5つです。0.7.0 の配布資産のままでも動きます。CI の見本は版のファイルの版（0.8.0）の SpecDock を入れて動きます。
- 文書の描画（#535）：Scope の詳しい画面の「文書」のタブで、仕様をその場で描いて読めます。
  - 画面の道が足されます：`/r/<host>/<owner>/<name>/scopes/<ID>/doc`（`render_scope` の HTML）と `…/scopes/<ID>/doc/<道>`（`requirement.md`・`design.md`・`plan.md`・`report.md` と、`artifacts/`・`discussions/` の直下の名前に `adr-` を含む `.md`）。`sandbox="allow-scripts allow-popups"` の枠で示し、インターネットは使いません。
  - API の `/api/v1/r/<repo>/scopes/<ID>` の `details` に、`spec`・`check`（検査の結果）・`progress`（計画の進み具合）・`adrs` と、文書ごとの `view` が足されます（画面のための JSON で、契約にはしません）。`cue` がないなどで検査できないときは `check.status: failed` と次の1手を示します。
  - 前面の `serve` が古い版で動いていると、画面の上に起動し直しを促す帯（`SERVER_RESTART_REQUIRED`）が出ます。
- 人のタスクの画面（#554）：見るだけで、書く口や完了のボタンはありません。
  - API が足されます：`GET /api/v1/todos` と `GET /api/v1/r/<repo>/todos`（中身は `specdock.todo-list/v1`。`?status=open|snoozed|done|cancelled|all`、既定は `open`。ほかの値は 400 `DASHBOARD_TODO_FILTER_INVALID`）、`GET /api/v1/r/<repo>/todos/<ID>`（`todo show` と同じ1件の形。404 `TODO_NOT_FOUND`／`TODO_INVALID`、記録の誤りなどは 409 `TODO_RECORD_INVALID` など、503 はカタログが読めないとき）。`/api/v1/todos/revision` と、`structure`・`scopes/<ID>` の `todos` の項目は画面のためのもので、契約にしません。
  - 画面の道が足されます：`/todos`、`/r/<repo>/todos`、`/r/<repo>/todos/<ID>`。上の帯に「人のタスク」のタブが出ます。
  - 構造の図の箱、ボードのカード、詳しい画面の見出しに「人 n」の印（Epic と Initiative は配下も数えます）、詳しい画面に「人のタスク」のタブ、横断の概況の札に「人のタスク n」「期限切れ m」が出ます。`dashboard hide` やダッシュボードの設定で隠したリポジトリは、人のタスクの一覧と1件からも外れます。
- 配布の文書の例の直し（#567）：`docs/authoring/cue.md` の CUE の書き方と、Issue の計画の雛形 `templates/cue/issue/plan.cue` の `execution` の例が、仕様化（`spec`）と実装（`impl`）の2つのセッションに分けた例になります。型・CLI・検査は変わりません（例だけの変更です）。
- 古さの表示の直し（#568）：`dashboard summary` の `fetched_at`・`stale` と、API の `snapshot.fetched_at`・`age_seconds`・`stale` の意味が「最後に構造を確かめた時刻」（スナップショットの取得と、変更の確認（probe）のうち新しいほう）になります。構造に変化がない間に誤って「古い」と警告することがなくなります。欄の名前と型は変わりません。
- 常駐のダッシュボードは、パッケージの版の更新の後に、自動で起動し直します（60秒ごとの版の確認。`dashboard service install` のやり直しは要りません）。前面の `serve` は自分で起動し直します。
- 戻し方：0.8.0 に問題があれば、パッケージを 0.7.0 に戻します。配布資産を 0.8.0 に上げた後なら、その更新の PR（版のファイル `spec-dock/system/spec-dock-version` を含む）を `git revert` して、配布資産を 0.7.0 のバイトに戻します。版のファイルだけを戻すと、0.7.0 の `canonical check` が 0.8.0 の資産を知らない変更として CI を止めます。

## 0.9.0 への更新

0.9.0 は、ダッシュボードの状態の色と形（#574）、構造の図の並べ方の改善（#575・#578）、細かい直し（#572）を届ける版です。コマンドの数（71）、カタログの形式（format 1）、`workspace.json` の版（4）は変わりません。コマンドの引数と配布の文書の内容も変わらず、変わる配布資産は、この `docs/migration.md` と版のファイル `spec-dock/system/spec-dock-version`（0.9.0）の2つです。

- パッケージを 0.9.0 に上げた後、各リポジトリで `spec-dock installation update --target <チェックアウト> --backup-dir <新しい外のディレクトリ> --yes` を実行して配布資産を上げ、通常の PR でコミットします。0.8.0 の配布資産のままでも動きます。CI の見本は版のファイルの版（0.9.0）の SpecDock を入れて動きます。
- 状態の色と形（#574）：ダッシュボードの状態の印が変わります。
  - 着手できる＝深い青の再生の丸、作業中＝鮮やかな緑の区切りの輪、止められている＝黄色の一時停止の丸（赤から変更）、不明＝紫の「?」の丸（黄から変更）です。人のタスクが Scope を止めている印も黄色になります。
  - 作業中の輪は、Issue では `plan.cue` の手順（dropped を除く）の進み（終わった手順が太い緑）、Epic と Initiative では配下の Issue の終わった割合です。最後に動いてから30分以内なら次の区切りが点滅し、超えると「N分動きなし」と出ます。サーバーは `cue` で `plan.cue` を読み、更新の時刻と大きさで覚えます。
  - API：構造の API と詳しい画面の API の各 Scope に `progress`（作業中の Issue だけ。画面のための項目で、契約にはしません）が足されます。`revision` は、作業中の Issue の `plan.cue` の書き換えでも変わります。
- Initiative の横並び（#575）：構造の図の最上位を、全体を画面に収めたときの倍率が最大になる行の幅で並べます。ウィンドウの大きさが変わり終わったときだけ並べ直します。
- 構造の図の隙間の直し（#578）：左右・上下の広すぎる隙間を直します。配線の寄せと広げを通り道ごとに見積もり、線の多い入口の辺は 8px おきに置き、線が枠の外へ遠回りしません（図の検査に `frameExits` が足されます）。
- 細かい直し（#572）：`GET /favicon.ico` と `/assets/favicon.svg` が足されます（ファビコンの 404 がなくなります）。Scope が 0 件のリポジトリの札に「Scope はまだありません」と出ます。390px の幅で、帯の下の図の領域の線を直します。
- 0.8.0 の節の訂正：0.8.0 の節の冒頭は「足すものだけで、0.7.0 のコマンドと API は変わりません」と書いていますが、同じ節の古さの表示の直し（#568）は、既存の欄の意味を変えています。正しくは次のとおりです。`dashboard summary` の `fetched_at`・`stale` と、API の `snapshot.fetched_at`・`age_seconds`・`stale` は、構造の古さを `max(スナップショットの fetched_at, 確かめた checked_at)`（最後に構造を確かめた時刻）で表します。ただし、変更の確認（probe）が失敗中のとき、記録がないか壊れているとき、時刻が未来のときは、`fetched_at` だけで判定します。欄の名前と型は変わりません。0.8.0 の節の本文は、配布済みのバイトのまま残しています。
- 常駐のダッシュボードは、パッケージの版の更新の後に、自動で起動し直します（60秒ごとの版の確認。`dashboard service install` のやり直しは要りません）。前面の `serve` は自分で起動し直します。
- 戻し方：0.9.0 に問題があれば、パッケージを 0.8.0 に戻します。配布資産を 0.9.0 に上げた後なら、その更新の PR（版のファイル `spec-dock/system/spec-dock-version` を含む）を `git revert` して、配布資産を 0.8.0 のバイトに戻します。版のファイルだけを戻すと、0.8.0 の `canonical check` が 0.9.0 の資産を知らない変更として CI を止めます。

## 0.9.1 への更新

0.9.1 は、構造の図の並べ方の直し（#584）を届ける版です。コマンドの数（71）、カタログの形式（format 1）、`workspace.json` の版（4）は変わりません。コマンドの引数、API と JSON の契約も変わらず、変わる配布資産は、この `docs/migration.md` と版のファイル `spec-dock/system/spec-dock-version`（0.9.1）の2つです。

- パッケージを 0.9.1 に上げた後、各リポジトリで `spec-dock installation update --target <チェックアウト> --backup-dir <新しい外のディレクトリ> --yes` を実行して配布資産を上げ、通常の PR でコミットします。0.9.0 の配布資産のままでも動きます。構造の図の直しはパッケージが配る画面にあるので、パッケージを上げるだけで届きます。CI の見本は版のファイルの版の SpecDock を入れて動きます。
- 構造の図の並べ方（#584）：
  - 同じ段の中で、依存でつながったまとまり（塊）を先に（左に）置き、つながりのない Scope を、塊の右や下の空きに詰めます。塊どうし、つながりのない Scope どうしの活動順は保ちます。塊のない段は今までと同じに並びます。
  - 最上位の Initiative も、ほかの段と同じく、100% の表示で見える幅で折り返します。0.9.0 の節の「全体を画面に収めたときの倍率が最大になる行の幅で並べます」を改めます。1つで見える幅より広い Initiative の行だけは、見える幅を超えます。ウィンドウの大きさが変わり終わったときだけ並べ直すのは同じです。
- 常駐のダッシュボードは、パッケージの版の更新の後に、自動で起動し直します（60秒ごとの版の確認。`dashboard service install` のやり直しは要りません）。前面の `serve` は自分で起動し直します。
- 戻し方：0.9.1 に問題があれば、パッケージを 0.9.0 に戻します。配布資産を 0.9.1 に上げた後なら、その更新の PR（版のファイル `spec-dock/system/spec-dock-version` を含む）を `git revert` して、配布資産を 0.9.0 のバイトに戻します。版のファイルだけを戻すと、0.9.0 の `canonical check` が 0.9.1 の資産を知らない変更として CI を止めます。

## 0.9.2 への更新

0.9.2 は、Scope の欄の作り直し（#588）と、文書のタブの詰め直し（#590）を届ける版です。コマンドの数（71）、カタログの形式（format 1）、`workspace.json` の版（4）は変わりません。コマンドの引数と、CLI の JSON の契約も変わりません。ダッシュボードの Scope の JSON では、文書の説明資料の項目に `skeleton`（雛形のままか。判定できないときは `null`）が足されるだけです。変わる配布資産は、この `docs/migration.md` と版のファイル `spec-dock/system/spec-dock-version`（0.9.2）の2つです。

- パッケージを 0.9.2 に上げた後、各リポジトリで `spec-dock installation update --target <チェックアウト> --backup-dir <新しい外のディレクトリ> --yes` を実行して配布資産を上げ、通常の PR でコミットします。0.9.1 と 0.9.0 の配布資産のままでも動き、どちらからでも上がります。画面の変更はパッケージが配るので、パッケージを上げるだけで届きます。CI の見本は版のファイルの版の SpecDock を入れて動きます。
- Scope の欄（#588）：
  - ボードの札と構造の図の箱で、同じ欄が開きます。ボードの札を普通に押すと、ページを移らずに欄が開きます。Ctrl・Cmd・Shift を押しながらのクリックや中クリックでは、今までどおり詳しい画面を新しいタブで開きます。
  - 欄のタブは、説明資料、概要、依存、配下、文書、Artifact、人のタスクの順で、詳しい画面と同じ中身です。説明資料が書かれていれば説明資料のタブが、雛形のままなら概要のタブが最初に選ばれます。詳しい画面にも、説明資料のタブが最初に出ます。
  - 欄は広くなり（見える幅の 44%、380〜720px）、欄から詳しい画面へ、同じタブでも新しいタブでも移れます。
  - スマホでは、下からの欄を、取っ手と見出しの帯のスワイプで、最小・通常・全体の3段に動かせます。最小からさらに下げて離すと閉じます。
- 文書のタブ（#590）：選べる文書は、仕様（要件・設計・計画）と報告の2つです（Markdown の Scope では要件・設計・計画・報告。説明資料は専用のタブで読みます）。大きな札をやめて1行の切り替えにし、右端に新しいタブで開くリンクを置きます。検査の帯は誤りがあるときだけ1行で出し、計画の進み具合は概要のタブだけに出します。埋め込んだ文書の枠は、残りの高さをすべて使います。説明資料のタブの上の帯も、同じ形の1行の細い帯にします。
- 常駐のダッシュボードは、パッケージの版の更新の後に、自動で起動し直します（60秒ごとの版の確認。`dashboard service install` のやり直しは要りません）。前面の `serve` は自分で起動し直します。
- 戻し方：0.9.2 に問題があれば、パッケージを 0.9.1 に戻します。配布資産を 0.9.2 に上げた後なら、その更新の PR（版のファイル `spec-dock/system/spec-dock-version` を含む）を `git revert` して、配布資産を前のバイトに戻します。版のファイルだけを戻すと、0.9.1 の `canonical check` が 0.9.2 の資産を知らない変更として CI を止めます。

## 0.9.3 への更新

0.9.3 は、ダッシュボードと同じPCの orca-web との連携を届ける版です（#596 の orca-web の場所と Scope と worktree の対応、#597 の稼働の印と「Orca で開く」、#598 のエージェントのタブとチャットの埋め込み）。コマンドの数（71）、カタログの形式（format 1）、`workspace.json` の版（4）は変わりません。コマンドの引数と、CLI の JSON の契約も変わりません。ダッシュボードの JSON に項目が足されるだけです（`/api/v1/repositories` の `server.orca_web`、構造の JSON の Scope ごとの `worktrees` と、全体の `worktrees`）。変わる配布資産は、この `docs/migration.md`、版のファイル `spec-dock/system/spec-dock-version`（0.9.3）、`docs/reference_cli.md`（「orca-web との連携」の節と、設定の3段の `orca_web`）の3つです。

- パッケージを 0.9.3 に上げた後、各リポジトリで `spec-dock installation update --target <チェックアウト> --backup-dir <新しい外のディレクトリ> --yes` を実行して配布資産を上げ、通常の PR でコミットします。0.9.2 以前（0.9.0 から）の配布資産のままでも動き、そこから上がります。画面の変更はパッケージが配るので、パッケージを上げるだけで届きます。CI の見本は版のファイルの版の SpecDock を入れて動きます。
- orca-web との連携（#596〜#598）：
  - 画面が同じPCの orca-web を直接読み、構造の図の箱と枠、ボードの札、横の欄の見出しに、その Scope に対応する worktree にいるエージェントの稼働の印を出します。横の欄の見出しには「Orca で開く」のボタンを置きます。サーバーは orca-web を読まず、Orca の CLI も呼びません。
  - 横の欄と詳しい画面のタブの2番目（説明資料の次）に「エージェント」のタブが足され、対応した worktree のエージェントを選んで、orca-web の詳細とチャットをその場で使えます。
  - Scope と worktree の対応は SpecDock が決めます（worktree のパスの一致、なければ同じリポジトリのブランチ名の一致）。
- 設定：利用者の設定 `config.json`（`$XDG_CONFIG_HOME/spec-dock/config.json`、なければ `~/.config/spec-dock/config.json`）に、最上位の節 `orca_web` が足されます：`{"schema": "specdock.config/v1", "orca_web": {"enabled": true, "port": 8791}}`。どちらも省け、既定は `enabled: true`、`port: 8791`（1〜65535 の整数）です。節がなければ既定で連携します。壊れた節は連携しない側に倒れ、理由は `spec-dock dashboard list` の `config_problems` と画面に出ます。ほかの節（`dashboard`、`todo`）には影響しません。変えると、起動し直さずに次の要求から効きます。
- 前提：orca-web の `ORCA_WEB_READ_ORIGINS` に、SpecDock のオリジン（`http://127.0.0.1:47800` と、Tailscale の IP の同じ番号）が入っていること（orca-web の既定）。ほかのオリジンからの読みは orca-web が断ります。`localhost` や MagicDNS の名前で画面を開くと読めません。
- orca-web がないとき、届かないとき、Orca に届いていないときは、稼働の印も「Orca で開く」も出ず、構造の図とボードは今までどおり動きます。エージェントのタブは、SpecDock の worktree の記録がある Scope でだけ出て、中に理由の知らせ（例「orca-web（<オリジン>）に届かない」）だけを示します。届くようになれば、次の読み（10秒ごと）で印が出ます。連携を止めるときは `config.json` に `"orca_web": {"enabled": false}` を書きます（画面は orca-web に何も要求しません）。
- 送信：チャットの送信は、エージェントのタブの枠の中の orca-web の画面だけが行います。送れるかは orca-web の設定の `sendEnabled`（既定は止まっている）で決まり、SpecDock は上書きも隠しもしません。送信だけを止めるときは、orca-web の `sendEnabled` を false にします。
- 常駐のダッシュボードは、パッケージの版の更新の後に、自動で起動し直します（60秒ごとの版の確認。`dashboard service install` のやり直しは要りません）。前面の `serve` は自分で起動し直します。
- 戻し方：0.9.3 に問題があれば、パッケージを 0.9.2 に戻します。配布資産を 0.9.3 に上げた後なら、その更新の PR（版のファイル `spec-dock/system/spec-dock-version` を含む）を `git revert` して、配布資産を前のバイトに戻します。版のファイルだけを戻すと、0.9.2 の `canonical check` が 0.9.3 の資産を知らない変更として CI を止めます。

## 0.9.4 への更新

0.9.4 は、ダッシュボードの画面の直しを届ける版です（#604・#605 のエージェントのタブの直し、#606 の構造の図の見せる範囲の切り替え、#608 の依存の線の切り替えの廃止）。コマンドの数（71）、カタログの形式（format 1）、`workspace.json` の版（4）は変わりません。コマンドの引数、CLI の JSON の契約、ダッシュボードの JSON の契約も変わりません。変わる配布資産は、この `docs/migration.md`、版のファイル `spec-dock/system/spec-dock-version`（0.9.4）、`docs/reference_cli.md`（「orca-web との連携」のエージェントのタブの選びと、`orca-shape` の知らせの説明）の3つです。

- パッケージを 0.9.4 に上げた後、各リポジトリで `spec-dock installation update --target <チェックアウト> --backup-dir <新しい外のディレクトリ> --yes` を実行して配布資産を上げ、通常の PR でコミットします。0.9.3 以前（0.9.0 から）の配布資産のままでも動き、そこから上がります。画面の変更はパッケージが配るので、パッケージを上げるだけで届きます。CI の見本は版のファイルの版の SpecDock を入れて動きます。
- 構造の図の道具の帯（#606・#608）：「終わったものも」「片付けの候補を畳む」の2つのボタンと、依存の線の切り替え「待っている線｜すべての線｜線なし」がなくなります。代わりに、見せる範囲の1つの切り替え「全体｜いま｜これから」が入ります。入れ子と木のどちらでも効きます。
  - 全体：終わったものも片付けの候補もすべて出します（0.9.3 で「終わったものも」を入れ、候補を畳まない状態と同じ）。片付けの候補の Issue の箱にも、枠と同じ候補の印が付きます。
  - いま（既定）：0.9.3 の既定と同じ見え方です。開いている親の中の終わったものは灰色で出し、中がすべて終わった親は出さず、入れ子では片付けの候補を1つに畳みます。
  - これから：終わったものと片付けの候補を出しません。その下にまだ終わっていない Scope があるときだけ、その枠として出します。終わったものとの依存の線も出しません。
  - 依存の線は、いつも 0.9.3 の「すべての線」の描き方で出ます（終わった依存は薄く、待っている依存は目立つ）。図に出ていない相手との線は今までどおり描きません。
  - 画面に収めるボタンの見える文字が「全体」から「収める」になります（title は「画面に収める」。動きは同じ）。
- ブラウザーの保存：構造の図の選びの保存のキーが `specdock.graph.v2` から `specdock.graph.v3` になり、`{mode, range, legend}` を書きます。初めて開いたとき、版2の保存から一度だけ移し替えます：表し方（入れ子・木）と凡例は引き継ぎ、「終わったものも」（`showDone`）が真なら見せる範囲は「全体」、それ以外は「いま」になります。「片付けの候補を畳む」と依存の線の選びは捨て、線はすべての線になります。版1だけがあるときは、表し方と凡例だけを引き継ぎます。古いキーは消しません。
- エージェントのタブの直し（#604・#605）：
  - 問い合わせに `agent` がなく、その Scope で最後に開いた相手を開いたときも、その相手を問い合わせ（横の欄では欄の中）に書きます。帯の今の相手を押しても枠が読み込み直されず、書きかけの本文が消えません。
  - 横の欄の足の「詳しい画面」と「新しいタブで開く」は、欄の今の選びを、なければ同じ Scope で最後に開いた相手を、欄がどのタブを見ていても `agent` として持ちます。その相手がいなくなったと画面が知っていれば `gone:<id>` として持つので、新しいタブで別のエージェントが自動で開きません。
  - 帯のエージェントを修飾キー（Ctrl・Cmd・Shift・Alt）つきで押して新しいタブに開いても、元の画面の覚えは変わりません。
  - スマホの幅（640px 以下）の構造の図で、選んだ箱の稼働の印をもう一度押すと、詳しい画面に移らず、横の欄のエージェントのタブを開きます。印の外の2回目の押しは、今までどおり詳しい画面に移ります。
  - orca-web の要約で worktree の `agents` が並びでないときは、選んだ相手をいなくなったとは決めず、形の違う項目（`orca-shape`）として知らせ、選びを変えません。要約が直れば、その相手の枠に戻ります。
- 常駐のダッシュボードは、パッケージの版の更新の後に、自動で起動し直します（60秒ごとの版の確認。`dashboard service install` のやり直しは要りません）。前面の `serve` は自分で起動し直します。
- 戻し方：0.9.4 に問題があれば、パッケージを 0.9.3 に戻します。0.9.3 の画面は版2の保存を読むので、0.9.4 で選んだ見せる範囲は引き継がれません。配布資産を 0.9.4 に上げた後なら、その更新の PR（版のファイル `spec-dock/system/spec-dock-version` を含む）を `git revert` して、配布資産を前のバイトに戻します。版のファイルだけを戻すと、0.9.3 の `canonical check` が 0.9.4 の資産を知らない変更として CI を止めます。

## 0.9.5 への更新

0.9.5 は、ダッシュボードの直しを届ける版です（#618 の『これから』の親の絞り込み、#619 のリポジトリの一覧の入れ子と段の札、#622 の構造の図のエージェントの行）。コマンドの数（71）、カタログの形式（format 1）、`workspace.json` の版（4）は変わりません。コマンドの引数と CLI の JSON の契約も変わりません。ダッシュボードの JSON の契約は、`GET /api/v1/repositories` の各リポジトリに項目が2つ増えるだけで、今の項目は変わりません。変わる配布資産は、この `docs/migration.md`、版のファイル `spec-dock/system/spec-dock-version`（0.9.5）、`docs/reference_cli.md`（「orca-web との連携」の API の `parent`・`tier` の説明）の3つです。

- パッケージを 0.9.5 に上げた後、各リポジトリで `spec-dock installation update --target <チェックアウト> --backup-dir <新しい外のディレクトリ> --yes` を実行して配布資産を上げ、通常の PR でコミットします。0.9.4 以前（0.9.0 から）の配布資産のままでも動き、そこから上がります。画面と API の変更はパッケージが配るので、パッケージを上げるだけで届きます。CI の見本は版のファイルの版の SpecDock を入れて動きます。
- 構造の図の『これから』（#618）：子を持つ Scope（Initiative・Epic、子を持つ Issue）は、これからで見える子孫があるときだけ出ます。中が終わったものと片付けの候補だけの開いた親は、中のない枠として残らず、出なくなります。開いた子があっても、その子自身が子を持ち、中に見えるものがなければ、親も子も出ません。子のない開いた Scope、子のない開いた子孫を持つ親、選んでいる（focus の）Scope は今までどおり出ます。「全体」と「いま」の見え方は変わりません。
- リポジトリの一覧の API（#619）：`GET /api/v1/repositories` の各リポジトリに、`repository` から `problem` までの項目の後ろに、チェックアウトの入れ子の親 `parent`（同じ応答の `repositories` にある、いちばん近い出す祖先のリポジトリの鍵か `null`）と段の札 `tier`（途中のディレクトリの名前の配列。`businesses` は「事業」、`products` は「プロダクト」、`services` は「サービス」になり、ほかの名前はそのまま）が付きます。チェックアウトとカタログの道は返しません。隠したリポジトリ、クローンが2つのものの扱いは `docs/reference_cli.md` にあります。画面はまだこの2項目を使いません。
- 構造の図の稼働の印（#622）：箱と枠の AI エージェントの印（orca-web の稼働の印）は、専用の行（エージェントの行）に左寄せで出ます。箱では、ほかの印（保証レベル・PR・worktree・人のタスク・後に続く）の下に、入れ子の枠では、見出しの行の下、要約の行の上に置きます。前の上限（箱は2つ、枠は3つ）と「+N」はなくなり、対応した worktree のエージェントをすべて出して、箱の幅で折り返します。行1つにつき、箱（入れ子の枠では見出し）が縦に伸びます。エージェントのいない箱は前の高さのままです。「後に続く」の数は今までどおり出ます。ボードと横の欄の印（上限4）は変わりません。
- 常駐のダッシュボードは、パッケージの版の更新の後に、自動で起動し直します（60秒ごとの版の確認。`dashboard service install` のやり直しは要りません）。前面の `serve` は自分で起動し直します。
- 戻し方：0.9.5 に問題があれば、パッケージを 0.9.4 に戻します。`GET /api/v1/repositories` の `parent`・`tier` はなくなり、構造の図は前の印（上限と「+N」）に戻ります。ブラウザーの保存のキー（`specdock.graph.v3`）は変わらないので、選びはそのまま残ります。配布資産を 0.9.5 に上げた後なら、その更新の PR（版のファイル `spec-dock/system/spec-dock-version` を含む）を `git revert` して、配布資産を前のバイトに戻します。版のファイルだけを戻すと、0.9.4 の `canonical check` が 0.9.5 の資産を知らない変更として CI を止めます。

## 0.9.6 への更新

0.9.6 は、ダッシュボードの画面と構造の図の直しを届ける版です（#628 の『横断の構造』、#630 の枠の見出しの行の高さと線の通り道、#631 の横断の構造の並びと最初の表示、#636 の段の札の除去、#637 の稼働の印と worktree の印。#626 はテストの揺れの直しで、製品は変わりません）。コマンドの数（71）、カタログの形式（format 1）、`workspace.json` の版（4）は変わりません。コマンドの引数と CLI の JSON の契約も変わりません。ダッシュボードの JSON は、`GET /api/v1/repositories` の各リポジトリから段の札 `tier` がなくなるだけです（#636。0.9.5 だけで配った項目で、使う者がないため、`specdock.dashboard/v1` のまま消す版の規則の例外です）。入れ子の親 `parent` とほかの項目は変わりません。変わる配布資産は、この `docs/migration.md`、版のファイル `spec-dock/system/spec-dock-version`（0.9.6）、`docs/reference_cli.md`（「ダッシュボードのサーバーの契約」の画面の道に `/graph` と `/todos` を足し、API の説明から `tier` を消した）の3つです。

- パッケージを 0.9.6 に上げた後、各リポジトリで `spec-dock installation update --target <チェックアウト> --backup-dir <新しい外のディレクトリ> --yes` を実行して配布資産を上げ、通常の PR でコミットします。0.9.5 以前（0.9.0 から）の配布資産のままでも動き、そこから上がります。画面の変更はパッケージが配るので、パッケージを上げるだけで届きます。CI の見本は版のファイルの版の SpecDock を入れて動きます。
- 『横断の構造』（#628、#631）：横断の画面（リポジトリを選んでいないとき）の上の帯のタブが『横断の概況』『横断の構造』『人のタスク』の3つになり、『横断の構造』（`/graph`）は、表示しているすべてのリポジトリの構造の図を1枚に描きます。リポジトリは、一覧の API の `parent` に従い、チェックアウトの入れ子のまま、見出しに名前を持つ枠に入ります。枠の見出しに段の札（事業・プロダクトなど）は出しません（#636。ディレクトリの名前に意味を持たせません）。親の図の右に子の枠が入るときは同じ行に、入らないときは次の行に並べます。道具の帯の『全体・いま・これから』はすべての枠に当たり、既定は『これから』です（見えるものがないリポジトリは出さず、見える子を持つ親は入れ物として出ます）。選びはブラウザーの `specdock.allgraph.v1` に残り、構造の図の `specdock.graph.v3` には触れません。最初の表示は、PC の幅では図の幅に合わせ、左上から縦に読み進めます。スマホの幅では 74% で左に寄せ、横の移動で読みます。『収める』で全体を1枚に収め、拡大・縮小・移動は構造の図と同じ操作です。箱を押すと、そのリポジトリの横の欄が開き、稼働の印はエージェントの行に出ます。
- 構造の図の枠と線（#630）：各リポジトリの構造の図（`/r/<host>/<owner>/<name>/`）と『横断の構造』で、枠の見出しの行の高さが少し詰まります（題名の行 22px、要約の行 18px。Epic の上の余白 8px）。配置の見込みと画面の実寸がそろうので、依存の線が箱や枠の見出しに重ならなくなり、線どうしも車線の間隔（8px）より近づかなくなります（木の表示では、線どうしの近づきが一部に残ります）。題名が2行に折り返す、子のない縮めた枠は、描いた後に測って配置をやり直し、中身が下にはみ出しません。
- 稼働の印と worktree の印（#637）：作業中で worktree のある Epic・Initiative の枠に、Issue の箱と同じ worktree の印（title「worktree：<ブランチ>」）が、入れ子の枠では見出しの題名のすぐ後に、木の表示では枠の箱の印の行に出ます（『横断の構造』も同じ）。構造の図の箱と枠の見出し、『横断の構造』、ボードの札、横の欄の見出しの稼働の印を押すと、その Scope を選び、横の欄のエージェントのタブを、押した印のエージェントのチャットを選んだ状態で開きます（スマホでは下からのシート。『+N』を押したときは選びを変えません）。印の並びは orca-web の部品の並びのままです。ボードの札の稼働の印は、ほかの印（PR・配下の数・人のタスク・後に続く）の行の下の専用の行（エージェントの行）に移り、印のない札ではこの行は見えず、高さを取りません。上限4と「+N」は変わりません。
- 常駐のダッシュボードは、パッケージの版の更新の後に、自動で起動し直します（60秒ごとの版の確認。`dashboard service install` のやり直しは要りません）。前面の `serve` は自分で起動し直します。
- 戻し方：0.9.6 に問題があれば、パッケージを 0.9.5 に戻します。『横断の構造』のタブと `/graph` はなくなり、`GET /api/v1/repositories` に `tier` が戻り、構造の図の見出しと線は前の高さと通り道に、枠の worktree の印とボードの札のエージェントの行はなくなり、稼働の印を押したときはエージェントのタブを開くだけの前の動きに戻ります。ブラウザーの保存のキー（`specdock.graph.v3`）は変わらないので、構造の図の選びはそのまま残ります（`specdock.allgraph.v1` は使われずに残るだけです）。配布資産を 0.9.6 に上げた後なら、その更新の PR（版のファイル `spec-dock/system/spec-dock-version` を含む）を `git revert` して、配布資産を前のバイトに戻します。版のファイルだけを戻すと、0.9.5 の `canonical check` が 0.9.6 の資産を知らない変更として CI を止めます。

## 0.9.7 への更新

0.9.7 は、ダッシュボードの構造の図と『横断の構造』に Orca の指揮の関係を描き、表示を直す版です（#642 の各リポジトリの構造の図の指揮の線と『指揮の帯』、#644 の『横断の構造』の指揮の線と枠ごとの帯と見出しの文字、#639 の横断の構造の知らせのまとめ、#643 の横断の構造の帯の並び、#641 の木の表示の線の通り道）。コマンドの数（71）、カタログの形式（format 1）、`workspace.json` の版（4）は変わりません。コマンドの引数、CLI の JSON の契約、ダッシュボードの JSON（`specdock.dashboard/v1`）、画面の道も変わりません。変わる配布資産は、この `docs/migration.md` と、版のファイル `spec-dock/system/spec-dock-version`（0.9.7）の2つです。

- パッケージを 0.9.7 に上げた後、各リポジトリで `spec-dock installation update --target <チェックアウト> --backup-dir <新しい外のディレクトリ> --yes` を実行して配布資産を上げ、通常の PR でコミットします。0.9.6 以前（0.9.0 から）の配布資産のままでも動き、そこから上がります。画面の変更はパッケージが配るので、パッケージを上げるだけで届きます。CI の見本は版のファイルの版の SpecDock を入れて動きます。
- 指揮の線（#642、#644）：各リポジトリの構造の図（`/r/<host>/<owner>/<name>/`）と『横断の構造』（`/graph`）に、Orca の指揮の関係（親のエージェント → 子のエージェント）を、親のエージェントの稼働の印から子の印への黄色の線で描きます。子が working なら黄色の点が親から子へ流れ、waiting などの待ちなら止まった点線、done なら薄い線です。親の端には波紋が出ます。同じ箱（枠の見出し・帯の同じ項目も同じ）の親子は、外へふくらむ弧で結びます。ブラウザーやOSの動きを減らす設定（`prefers-reduced-motion`）では、点の流れも波紋も止まります。印を押すと、そのエージェントの線だけが目立ちます。凡例に「指揮（親 → 子）」の行が出ます。『横断の構造』では、線がリポジトリの枠をまたいで印から印へ引かれます。
- 『指揮の帯』（#642、#644）：箱を持たない親と子（main のチェックアウトの統括、Scope の箱に当たらない worktree、ほかのリポジトリのエージェント）は『指揮の帯』に並びます。構造の図ではすべての Initiative の上に1行の帯が出て、項目の札は「main のチェックアウト」、このリポジトリのほかの worktree はブランチ名、ほかのリポジトリは「<名前> · <ブランチ>」です。『横断の構造』では、各リポジトリの枠の見出しのすぐ下にそのリポジトリの帯が、全体のいちばん上にダッシュボードに出ていないリポジトリなどの帯『ほかの場所』が出ます（『これから』で見える Scope のないリポジトリも、帯に親がいれば見出しと帯だけの枠で出ます）。帯のエージェントを押すと、横の欄（スマホでは下からのシート）にそのエージェントのチャットが開きます。
- 線と帯を描くには、orca-web の要約がエージェントの親（`agents[].parent`）を返す必要があります（orca-web の iss-00043 以降）。親を返さない orca-web、Orca に届かないとき、組がないときは、線も帯も出ません（指揮の線と帯のほかの変更は、そのまま届きます）。
- 箱の中のエージェントの行（稼働の印の行）は、箱の底に寄ります。エージェントの行のある箱は少し高くなり、題名が2行でも切れません。
- 枠の見出しの文字（#644）：両方の画面で、指揮の線は枠の見出しの文字の下を通り、見出しの文字が線の上に読めるように出ます。
- 横断の構造の知らせのまとめ（#639）：『横断の構造』で、文の決まった種類の知らせ（構造が古い、スナップショットの異常、構造の異常、PR の状態が分からない）を、状態のチップの下に種類ごとに1行でまとめ、当てはまるリポジトリの名前を並べます。リポジトリの枠には、そのリポジトリにだけある知らせだけが残ります。最初の表示と『収める』は、まとめの行の下から始まります。
- 横断の構造の帯の並び（#643）：PC の幅で、上の帯が、状態の札 → 道具（『全体・いま・これから』など）→ 知らせのまとめの行の順に並びます。幅 1000 前後でも、道具の列がまとめの行の下に落ちません。スマホの並びは変わりません。
- 木の表示の線の通り道（#641）：構造の図の木の表示で、依存の線の詰めが範囲からあふれる束を詰め直し、線が箱や線に重ならないようにしました。入れ子の表示は変わりません。
- 常駐のダッシュボードは、パッケージの版の更新の後に、自動で起動し直します（60秒ごとの版の確認。`dashboard service install` のやり直しは要りません）。前面の `serve` は自分で起動し直します。
- 戻し方：0.9.7 に問題があれば、パッケージを 0.9.6 に戻します。指揮の線と『指揮の帯』はなくなり、箱のエージェントの行と枠の見出し、横断の構造の知らせと帯の並び、木の表示の線は 0.9.6 の形に戻ります。ブラウザーの保存のキーは変わりません。配布資産を 0.9.7 に上げた後なら、その更新の PR（版のファイル `spec-dock/system/spec-dock-version` を含む）を `git revert` して、配布資産を前のバイトに戻します。版のファイルだけを戻すと、0.9.6 の `canonical check` が 0.9.7 の資産を知らない変更として CI を止めます。

## 0.9.8 への更新

0.9.8 は、ダッシュボードの構造の図と『横断の構造』の指揮の線を軽く読みやすくし、図の操作と欄を使いやすくする版です（#649 の指揮の線の動きを軽く、#658 の上の縁から出て上の縁へ入るホップの弧、#660 の間 24px の点の組、#659 の帯の印から開くチャットの欄、#661 の矢印キーとマウスのホイール、#662 の Scope の欄の見出し）。コマンドの数（71）、カタログの形式（format 1）、`workspace.json` の版（4）は変わりません。コマンドの引数、CLI の JSON の契約、ダッシュボードの JSON（`specdock.dashboard/v1`）、画面の道、ブラウザーの保存のキーも変わりません。変わる配布資産は、この `docs/migration.md` と、版のファイル `spec-dock/system/spec-dock-version`（0.9.8）の2つです。

- パッケージを 0.9.8 に上げた後、各リポジトリで `spec-dock installation update --target <チェックアウト> --backup-dir <新しい外のディレクトリ> --yes` を実行して配布資産を上げ、通常の PR でコミットします。0.9.7 以前（0.9.0 から）の配布資産のままでも動き、そこから上がります。画面の変更はパッケージが配るので、パッケージを上げるだけで届きます。CI の見本は版のファイルの版の SpecDock を入れて動きます。
- 指揮の線の動きを軽く（#649）：点の流れと波紋を、線ごとの小さな絵に分け、ブラウザーの主スレッドで毎コマ描き直さない形にしました。図を動かしている間（止めてから0.3秒まで）、画面の外の線と波紋、ページが裏にあるときは、点の流れと波紋が止まります。構造の図と『横断の構造』の動きが重くなりません。動きを減らす設定（`prefers-reduced-motion`）では、今までどおり止まります。
- ホップの弧（#658）：指揮の線は、親の側（印のある箱・枠の見出し・帯の項目）の上の縁から上へ出て、子の側の上の縁へ上から入る、上にふくらむ弧になります。今までの、下から出て下から入る回り込みはなくなり、箱の中の短い線も引きません。子の端には下向きの小さな矢じりが出て、受けた子の印の縁が指揮の色になります。同じ箱の親子も、上の縁の小さな弧で結びます。線の色、状態（working・waiting・done）、波紋、『指揮の帯』は変わりません。
- 点の組（#660）：working の子への線の点は、間 24px の大小2つの点の組（大きな頭と、6px 後ろの小さく薄い尾）になり、ゆっくり（20px/秒）親から子へ流れます。組の形で進む向きが分かり、点滅には見えません。波紋も少しゆっくりになります。動きを減らす設定では止まった組を1つの絵で見せ、組の形で向きを示します。
- 帯の印から開くチャット（#659）：『指揮の帯』のエージェントの印を押して開くチャットが、Scope の欄のエージェントのタブと同じく、欄の高さいっぱいに広がります。スマホの下からの欄では、見出しかつまみを指で引いて、全面・半分・閉じるを選べます（Scope の欄と同じ動き）。片付けの候補の欄も同じく指で動かせます。
- 図の操作（#661）：構造の図と『横断の構造』で、矢印キーで図をその向きに見るように動かせます（1回 80px、Shift を押しながらで 4倍）。`+`（`=`）で拡大、`-` で縮小、`0` で全体を収めます（フォーカスが入力欄・ボタン・リンク・チャットの枠や、欄・道具の棒など図の外にあるとき、Ctrl・Cmd・Alt を押しているときは働きません）。マウスのホイールを回すと、カーソルの位置を中心に拡大・縮小します（Shift を押しながらのホイールは横に動かします）。トラックパッドは今のままで、2本指でなぞると動き、ピンチで拡大・縮小します。マウスのホイールと見分けられないときは、動かすほうに倒します。
- Scope の欄の見出し（#662）：欄の見出しは、1行目の祖先のパンくず・今の Scope の ID と番号・種類・状態の札（とエージェントの印・Orca で開く・閉じる）と、2行目の題名（長ければ2行で切る）の2行にまとまります。状態の名前を繰り返すだけの帯は出さず、理由が足す情報を持つとき（待っているもの、配下の作業中、PR の状態など）や『N分動きなし』があるときだけ、1行の帯が出ます。マージの札は帯の理由にまとめました。説明資料のタブの上の、タブの名前を繰り返す帯はなくなり、枠を新しいタブで開く印がタブの行の右端（詳しい画面ではタブの並びのすぐ右）に移りました。見出しが低くなり、タブの中身が広がります。スマホで片付けの候補の欄を全面にしたとき、描き直しで段が半分に戻らなくなりました。欄の下の行（詳しい画面・新しいタブで開く・GitHub）は変わりません。
- 常駐のダッシュボードは、パッケージの版の更新の後に、自動で起動し直します（60秒ごとの版の確認。`dashboard service install` のやり直しは要りません）。前面の `serve` は自分で起動し直します。
- 戻し方：0.9.8 に問題があれば、パッケージを 0.9.7 に戻します。指揮の線、帯の印から開くチャット、図の操作、Scope の欄の見出しは 0.9.7 の形に戻ります。ブラウザーの保存のキーは変わりません。配布資産を 0.9.8 に上げた後なら、その更新の PR（版のファイル `spec-dock/system/spec-dock-version` を含む）を `git revert` して、配布資産を前のバイトに戻します。版のファイルだけを戻すと、0.9.7 の `canonical check` が 0.9.8 の資産を知らない変更として CI を止めます。

## 0.9.9 への更新

0.9.9 は、ダッシュボードの構造の図と『横断の構造』の『指揮の帯』を `Unscoped` の行に変え、主のチェックアウトと、どの Scope にも紐づかない worktree を並べる版です（#669）。コマンドの数（71）、カタログの形式（format 1）、`workspace.json` の版（4）は変わりません。コマンドの引数、CLI の JSON の契約、ダッシュボードの JSON の版（`specdock.dashboard/v1`）、画面の道、ブラウザーの保存のキーも変わりません。変わる配布資産は、この `docs/migration.md` と、版のファイル `spec-dock/system/spec-dock-version`（0.9.9）の2つです。

- パッケージを 0.9.9 に上げた後、各リポジトリで `spec-dock installation update --target <チェックアウト> --backup-dir <新しい外のディレクトリ> --yes` を実行して配布資産を上げ、通常の PR でコミットします。0.9.8 以前（0.9.0 から）の配布資産のままでも動き、そこから上がります。画面の変更はパッケージが配るので、パッケージを上げるだけで届きます。CI の見本は版のファイルの版の SpecDock を入れて動きます。
- `Unscoped` の行（#669）：構造の図と『横断の構造』の帯が `Unscoped` の行になりました。行の先頭に、いつも主のチェックアウト（印 `Primary`）が出ます。Orca を使わなくても、誰も指揮していなくても出ます。
- `Unlinked` の worktree（#669）：`git worktree list` に出る worktree のうち、どの Scope にも紐づかないものが `Unlinked` で並びます。`spec-dock work start` をせずに作業している worktree に、すぐ気づけます。エージェントのいない worktree は薄く出て、2つ以上あれば `+N` に畳まれます（押すと一覧）。仕様の置き場の worktree、bare、prunable の worktree は出ません。
- 1つの worktree は1つの項目で、そこにいるエージェントの印をすべて並べます（1行4つ、それより多いと項目の中で折り返します）。項目を押すと、ブランチ・パス・エージェントの詳細の欄が出ます（orca-web につながるときは『Orca で開く』も出ます。もう一度押すか Esc で閉じます）。エージェントの印を押すと、今までどおりそのエージェントのチャットが開きます。
- 『これから』（#669）：『これから』では、指揮の線を引かなくなりました。代わりに、主のチェックアウトと、指揮している `Unlinked` の worktree に、子の数が付きます（title に内訳）。『これから』の行には、主のチェックアウトと指揮している `Unlinked` の worktree だけが出て、指揮していない worktree とエージェントのいない worktree は出ません（全体・いまで出ます）。全体・いまの線は今までどおりです。
- 0.9.10 の注：0.9.10（#679）から、『これから』でも指揮の線と `Unscoped` の行（並ぶ worktree を含む）が『いま』と同じ規則で出て、上の項目の子の数は出なくなりました（「0.9.10 への更新」）。
- 今までの札「main のチェックアウト」は、ブランチ名と `Primary` の印に変わりました。
- 構造の API（`/api/v1/r/<host>/<owner>/<name>/structure`）の `worktrees` に `items`（各 worktree の `path`・`branch`・`head`・`main`・`detached`・`locked`）が加わりました。`status` と `paths` は変わりません。画面の中の JSON なので契約ではありません。
- エージェントの印と指揮の線を描くには、今までどおり orca-web の要約が要ります。orca-web に届かないときも、`Unscoped` の行と worktree の項目は出ます。
- 常駐のダッシュボードは、パッケージの版の更新の後に、自動で起動し直します（60秒ごとの版の確認。`dashboard service install` のやり直しは要りません）。前面の `serve` は自分で起動し直します。
- 戻し方：0.9.9 に問題があれば、パッケージを 0.9.8 に戻します。帯は 0.9.8 の『指揮の帯』の形に戻り、`Unlinked` の worktree と『これから』の数は出なくなります。ブラウザーの保存のキーは変わりません。配布資産を 0.9.9 に上げた後なら、その更新の PR（版のファイル `spec-dock/system/spec-dock-version` を含む）を `git revert` して、配布資産を前のバイトに戻します。版のファイルだけを戻すと、0.9.8 の `canonical check` が 0.9.9 の資産を知らない変更として CI を止めます。

## 0.9.10 への更新

0.9.10 は、作業用のworktreeの Antigravity（`agy`）がカタログに読み書きするための設定を確かめて案内し（#677）、ダッシュボードがエージェントの種類を名前で出し（#678）、『これから』でも指揮の線を出す（#679）版です。コマンドの数（71）、カタログの形式（format 1）、`workspace.json` の版（4）は変わりません。コマンドの引数、ダッシュボードの JSON の版（`specdock.dashboard/v1`）、画面の道、ブラウザーの保存のキーも変わりません。CLI の JSON の契約は、`canonical status` の `data.tools` に `antigravity` の項目が増えるだけです（項目の追加）。変わる配布資産は、`docs/canonical.md`（Antigravity の項）、`docs/reference_cli.md`（C45）、この `docs/migration.md`、版のファイル `spec-dock/system/spec-dock-version`（0.9.10）の4つです。

- パッケージを 0.9.10 に上げた後、各リポジトリで `spec-dock installation update --target <チェックアウト> --backup-dir <新しい外のディレクトリ> --yes` を実行して配布資産を上げ、通常の PR でコミットします。0.9.9 以前（0.9.0 から）の配布資産のままでも動き、そこから上がります。画面の変更はパッケージが配るので、パッケージを上げるだけで届きます。CI の見本は版のファイルの版の SpecDock を入れて動きます。
- Antigravity の設定（#677）：作業用のworktreeで動く Antigravity は、作業ディレクトリの外にあるカタログに書くために、ユーザーの設定 `~/.gemini/antigravity-cli/settings.json` の `permissions.allow` に、`read_file(<カタログ>)` と `write_file(<カタログ>)` の2つの規則を1回だけ足します。足す1行は、作業用のworktreeで `spec-dock canonical status` が示します（`docs/canonical.md` の『ツールの設定』）。mainのチェックアウトの中で動くときは要りません。SpecDock はツールの設定のファイルを書き換えません。
- `canonical status --json` の `data.tools` に `antigravity` の項目（`session`、`needed`、`configured`、`sources`、`file`、`line`）が増えました。Antigravity の中（環境変数 `ANTIGRAVITY_AGENT`）の作業用のworktreeで規則がないと、警告 `CANONICAL_TOOL_SETTING_MISSING`（`details.tool` は `antigravity`）と足す1行を示します。`permissions.deny`・`permissions.ask` がカタログを覆うかを確かめられないときは `CANONICAL_TOOL_SETTING_UNKNOWN` を示します。Antigravity の外では、警告と `tools.status`・`tools.next_step` は前と同じです。配るスキルと `AGENTS.md` の『仕様の扱い』は変わりません。
- エージェントの種類の名前（#678）：ダッシュボードは、エージェントの種類を orca-web の部品の名前（Claude、Codex、Antigravity、Gemini など）で出すようになりました。orca-web の部品が知らない種類は、今までどおり種類の文字列で出ます。Antigravity と Gemini の名前を出すには、orca-web の main `4ad7471` 以降が要ります。利用者がすることはありません。
- 『これから』の指揮の線（#679）：リポジトリの構造の図と『横断の構造』のどちらでも、『これから』で、指揮の黄色い点線、同じ箱の親子の弧、動き、波紋、`Unscoped` の行が『いま』と同じ規則で出ます。『これから』で隠れた Scope の worktree のエージェントの線は、いちばん近い見える祖先の枠に落ちます。0.9.9 で『これから』だけにあった子の数の札はなくなり、『いま』と同じ見え方になります。既定が『これから』の『横断の構造』を開いたときにも、線が出ます。
- 常駐のダッシュボードは、パッケージの版の更新の後に、自動で起動し直します（60秒ごとの版の確認。`dashboard service install` のやり直しは要りません）。前面の `serve` は自分で起動し直します。
- 戻し方：0.9.10 に問題があれば、パッケージを 0.9.9 に戻します。`canonical status` の `tools.antigravity` と Antigravity の警告はなくなり、エージェントの種類は種類の文字列に、『これから』は線のない子の数の形に戻ります。ユーザーの設定に足した Antigravity の規則は、残しても害はありません。ブラウザーの保存のキーは変わりません。配布資産を 0.9.10 に上げた後なら、その更新の PR（版のファイル `spec-dock/system/spec-dock-version` を含む）を `git revert` して、配布資産を前のバイトに戻します。版のファイルだけを戻すと、0.9.9 の `canonical check` が 0.9.10 の資産を知らない変更として CI を止めます。

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
