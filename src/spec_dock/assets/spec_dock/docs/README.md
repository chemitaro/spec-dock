# SpecDock文書入口

このディレクトリはmanaged installationが配布します。CLIはworktree外の固定distribution、または `spec-dock/scripts/spec-dock` shimから実行します。正確な文法は実際に動くengineの `spec-dock help` とleaf helpで確認してください。

## Current

- [全44 leafのCLI参照](reference_cli.md)
- [日本語の人間向け説明HTML（オフライン）](cli-redesign-guide.html)
- [導入・移行・復旧](migration.md)
- [命名](reference_naming.md)・[依存](reference_deps.md)・[GitHub](reference_github.md)・[生成状態](reference_sync.md)・[worktree](reference_worktree.md)
- [Authoring Kit](authoring/overview.md)

```sh
spec-dock scope list
spec-dock scope show iss-00123
spec-dock work start iss-00123 --base main
spec-dock active show
spec-dock branch show iss-00123
spec-dock dependency check iss-00123 --source github
spec-dock workspace validate
spec-dock workspace sync --source cache
spec-dock work finish iss-00123 --yes
```

`work start`/`work finish` はInitiative、Epic、Issueを同じ契約で扱います。選択だけなら `active set`/`active clear`、状態だけなら `scope close`/`scope reopen`、branchだけなら `branch create`/`branch switch` を使います。Artifactや生成index/treeは正本文書の代わりにはなりません。

## 運用と権限

通常操作はagentが対象を解決し、helpを読んで実行・post-stateを検証します。`scope delete`、`worktree remove`、`installation uninstall` など破壊的操作には、依頼または承認済み計画に正確な対象と結果が必要です。`--yes` は必要な最終確認を省略するだけで、ガードを迂回しません。PR mergeはrepositoryのhuman gateに従います。

## Historical

[過去版の参照](historical/README.md)と[Historical authoring](authoring/historical.md)は履歴資料です。現在の実行手順には使いません。
