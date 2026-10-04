# 導入・移行・保全（Current）

## 外部CLI

対応OSはLinuxとmacOS、Pythonは3.10以上です。Windowsを含む他のOSでは業務操作を開始せず `UNSUPPORTED_PLATFORM`（exit 3）を返します。help・version・completionはrepositoryなしでも利用できます。直接作業記録はPOSIX identityのみを受け付け、未知の記録を自動変換・削除しません。

package managerでレビュー・通常試験が済んだwheelをworktree外へ導入します。例えば `uv tool install /absolute/path/spec_dock-VERSION-py3-none-any.whl` です。PATH上の `spec-dock` が全コマンドの入口です。packageの更新とcheckoutのstatic資産更新は別操作です。

`spec-dock/scripts/spec-dock` はPATH上の外部consoleへ引数と終了値を渡すshimです。Git共有controlやcheckout内Pythonを探しません。旧branchの古いshimが戻っても外部 `spec-dock` は直接使えます。外部consoleがなければ導入/PATH確認へ戻り、自動installや旧engineへのfallbackはしません。

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
