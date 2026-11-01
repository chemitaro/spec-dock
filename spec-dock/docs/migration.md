# 導入・移行・保全（Current）

## 外部CLI

対応OSはLinuxとmacOS、Pythonは3.10以上です。Windowsを含む他のOSでは業務操作を開始せず `UNSUPPORTED_PLATFORM`（exit 3）を返します。help・version・completionはrepositoryなしでも利用できます。直接作業記録はPOSIX identityのみを受け付け、未知の記録を自動変換・削除しません。

package managerでレビュー・通常試験が済んだwheelをworktree外へ導入します。例えば `uv tool install /absolute/path/spec_dock-VERSION-py3-none-any.whl` です。PATH上の `spec-dock` が全コマンドの入口です。packageの更新とcheckoutのstatic資産更新は別操作です。

`spec-dock/scripts/spec-dock` はPATH上の外部consoleへ引数と終了値を渡すshimです。Git共有controlやcheckout内Pythonを探しません。旧branchの古いshimが戻っても外部 `spec-dock` は直接使えます。外部consoleがなければ導入/PATH確認へ戻り、自動installや旧engineへのfallbackはしません。

## canonical モードへの移行

宣言の版3（従来モード）から版4（canonical モード）への移行は、spec-dock のリポジトリの `scripts/migrate-to-canonical/README.md` の手順で、リポジトリごとに一度だけ行います。移行の前に `installation update` で配布資産を 0.3.0 に上げます（従来モードのまま動きます）。移行の後の使い方、ツールの設定の1行、同期が止まったときの扱いは[canonical モードの使い方](canonical.md)にあります。`installation init` は版4の宣言を置くので、新規導入のリポジトリは canonical モードで始まり、`spec-dock canonical link` が要ります。

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

## 新規導入

```sh
spec-dock installation init /absolute/project --dry-run --json
spec-dock installation init /absolute/project --yes --json
spec-dock installation show --target /absolute/project --json
spec-dock --project /absolute/project workspace validate --json
```

対象は正確なGit worktree root一つです。initは新writerのworkspace宣言と静的資産だけを置き、既存の配布先fileがあれば書込み前に停止します。main/linkedを一括導入せず、runtime、直接作業記録、Git内の独自領域を作りません。

## schema3の旧writerから移行

旧writer・自動起動の停止を確認し、仕様、ignored成果物、旧Git独自領域を含む実体の外部保全と復元確認を先行します。旧writer停止を確認できない状態では適用しません。

```sh
spec-dock --project /absolute/project workspace doctor --raw --legacy --json
spec-dock --project /absolute/project workspace migrate --to-schema 3 --to-writer-protocol specdock.worktree-writer/v1 --dry-run --json
spec-dock --project /absolute/project workspace migrate --to-schema 3 --to-writer-protocol specdock.worktree-writer/v1 --backup-dir /absolute/new-migration-backup --confirm-old-writers-stopped --yes --json
```

自workspaceのschema3宣言のwriter_protocolだけを切り替え、旧control_epochがある場合だけ除きます。Scope ID/path/linkage、文書、未知設定は保持します。旧activeを新予約へ取り込まず、旧Git独自領域に新値を書きません。schema3未満や未知protocolは本版の対象外です。切替後の新Startで直接対象を取得します。

## static資産の更新・削除

```sh
spec-dock installation update --target /absolute/project --dry-run --json
spec-dock installation update --target /absolute/project --backup-dir /absolute/new-static-backup --yes --json
# 正確な対象のtool資産削除が許可されている場合だけ
spec-dock installation uninstall --target /absolute/project --backup-dir /absolute/new-uninstall-backup --yes --json
```

新writer workspaceで既知path/hashのstatic filesだけを変更します。更新は欠けたfileを補い、既知旧bytesを置換し、既知旧runtime filesを個別退役させます。削除も所有権検証を行い、workspace宣言・ignore規則・仕様・Artifact・Workbench・直接記録・directoryを残します。未知改変は人間によるmergeへ戻し、directoryごとの削除はしません。

旧static bytes/modeを `backup/static/<relative>` へ保存し、別の一時場所へ実際に復元して比較します。backup先は全clone worktree、Git metadata、installed packageの外で、既存の通常parent下の新しい絶対pathです。既存backupを再利用しません。

## 途中で停止した場合

dry-runは書込み・backup・GitHub更新・Start lockを行いません。適用途中のexit6は確認済み・unknown・未実施effectsを区別します。残った候補、backup、実体pathを保全し、観測してから新しい明示操作を判断します。自動巻戻しやjournal replayはありません。コードrevertはGitHubへの完了・作成効果を元へ戻しません。
