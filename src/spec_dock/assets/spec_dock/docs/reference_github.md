# GitHub連携（Current）

新規Initiative・Epic・Issueは必ずGitHub Issueに対応します。同じrepositoryの番号をScope IDの正本にし、新しい番号をローカルで割り当てたりUUIDをScope identityにしたりしません。repositoryと明示refを照合して作成・取込みします。

```sh
spec-dock scope create initiative --backend github --title "Platform"
spec-dock scope import github epic gh:OWNER/REPO#124 --parent init-00123 --title "Authentication"
spec-dock scope show epic-00124 --json
spec-dock scope close epic-00124 --reason completed --yes --json
spec-dock scope reopen epic-00124 --yes --json
```

作成はGitHubの番号発行成功後にローカルScopeを公開します。取込みは既存Issueのread-only確認後に公開します。unknownなremote作成/更新を盲目的に繰り返さず、返されたrefと現物を照合します。offlineで新規作成は行いません。

GitHub Scopeのopen/closedはGitHubがauthorityで、未観測ならunknownです。close/reopenは状態だけを変え、selection/branchを変更しません。Finishはclosed(completed)確認後に捕捉済み直接記録だけを解除し、branchに留まります。未完了子がある親の完了は拒否します。delivery・test・review・mergeの完了証明は別に必要です。

既存true-local metadataのread/Finish互換性は新しいlocal Scope作成を許可しません。GitHub照会失敗をlocal成功へ置き換えません。
