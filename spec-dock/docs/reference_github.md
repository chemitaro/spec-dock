# GitHub連携（Current）

`--backend github` のScopeは対応するGitHub Issueを状態のauthorityとし、`--backend local` のScopeはlocal metadataがauthorityです。GitHub Issue番号は全Scope種別を通じて一意に解決します。Issueを新規作成する操作は `scope create`、既存Issueの読取りと取り込みは `scope import github` です。

```sh
spec-dock scope create initiative --backend github --title "Platform"
spec-dock scope import github epic 124 --parent init-00123 --title "Authentication"
spec-dock scope show epic-00124
spec-dock scope close epic-00124 --reason completed --yes
spec-dock scope reopen epic-00124 --yes
```

`scope close` と `scope reopen` は選択やbranchを変えません。`work finish TARGET` は完了と選択解除を一緒に行いますが、Git deliveryの完了証明ではありません。GitHub照会・更新失敗時にlocal stateで成功を偽装しません。GitHub repoを明示する場合は対象の対応を確認してください。詳細な旧版記録は[historical](historical/reference_github.md)です。
