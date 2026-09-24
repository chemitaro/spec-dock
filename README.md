# spec-dock

SpecDockは既存GitリポジトリにInitiative・Epic・Issueの仕様ツリーとCLIを導入する個人用ツールです。業務CLIは `scope`（仕様ノード）、`active`（現在の選択）、`work`（開始・完了）を分け、branch、dependency、artifact、worktree、workspace、installationを独立した操作群として提供します。

## 入口

- [現行CLIの全44コマンド](src/spec_dock/assets/spec_dock/docs/reference_cli.md)
- [日本語の対話的な説明資料](src/spec_dock/assets/spec_dock/docs/cli-redesign-guide.html)
- [導入・一括移行・復旧](src/spec_dock/assets/spec_dock/docs/migration.md)
- [文書作成ガイド](src/spec_dock/assets/spec_dock/docs/authoring/overview.md)

導入済みリポジトリでは、外部の固定distributionにある `spec-dock` コマンド、または `./spec-dock/scripts/spec-dock` shimを使います。どちらも同じengine pinを検証します。`spec-dock help` と各leafの `--help` が引数のauthorityです。CLIはagent-firstで運用し、依頼または承認済み計画の範囲にある操作をagentが実行して結果を検証します。

```sh
spec-dock scope create initiative --backend github --title "Platform"
spec-dock scope create epic --backend github --parent init-00123 --title "Authentication"
spec-dock scope create issue --backend github --parent epic-00124 --title "Refresh tokens"
spec-dock work start epic-00124 --base main
spec-dock active show
spec-dock work finish epic-00124 --yes
```

`work start` と `work finish` はIssue、Epic、Initiativeに使えます。開始は依存確認、branch作成またはcheckout、選択を実行します。完了はScopeをcompletedにし、選択中ならその対象以下を解除します。commit、push、PR、merge、test、reviewは別途確認してください。選択だけを変える場合は `active set TARGET`、状態だけを変える場合は `scope close TARGET` を使います。

## 導入と更新

新しい配布物はworktree外の固定distributionから実行します。初回導入は `spec-dock installation init PATH --yes`、固定commitへの更新は `spec-dock installation update --target PATH --commit SHA --maintenance --yes` を使います。既存導入先は停止・backup・inventoryを揃え、全登録worktreeを同じwriter protocolへ移行する必要があります。schema変換は `workspace migrate --to-schema 3 --yes` で別に実行します。途中失敗時はjournalのoperation IDを確認し、対象leafの `--resume` または `--rollback` に従います。詳細な手順とガードは[移行ガイド](src/spec_dock/assets/spec_dock/docs/migration.md)にあります。

`SPEC_DOCK_WORKTREE_ROOT` は管理対象linked worktreeの配置先です。使う場合は環境で絶対pathを指定してください。worktree作成には `--base REF` が必要です。

## 開発

provider側の正本は `src/spec_dock/` です。`src/spec_dock/assets/spec_dock/` の文書・テンプレート・runtimeが導入先に配布され、このリポジトリの `spec-dock/` はdogfooding用のconsumer workspaceです。仕様の変更はactive IssueのRequirement、Design、Planで追跡します。

```sh
make lint
uv run pytest
```

Provider CIもlintと通常のpytestを実行します。PRのmergeは人間が行います。
