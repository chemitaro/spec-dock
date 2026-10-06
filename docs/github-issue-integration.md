# GitHub Issue 連携（現行）

現行の GitHub 連携は、worktree外に通常インストールした `spec-dock` packageの `scope` と `work` から利用します。正確な引数と副作用は[CLI 参照](../src/spec_dock/assets/spec_dock/docs/reference_cli.md)と[GitHub 連携参照](../src/spec_dock/assets/spec_dock/docs/reference_github.md)を正本とします。

- `scope create {initiative,epic,issue} --backend github` は GitHub Issue を新規作成して Scope に対応付けます。
- `scope import github {initiative,epic,issue}` は既存 Issue を確認して Scope に取り込みます。
- 既存local backendのScopeは保全互換として読み取り・lifecycle操作を維持し、ローカルmetadataが状態の正本です。新規`--backend local`作成はできません。GitHub backendでは対応するIssueが状態の正本です。
- `scope close TARGET` と `scope reopen TARGET` は状態を変更します。選択やブランチは変更しません。
- `work start TARGET` は依存を確認し、ブランチを作成または切り替えて対象を選択します。`work finish TARGET` は対象を完了し、completedを確認して捕捉した直接選択だけを解除します。

通常TARGETには完全なScope IDまたは`gh:OWNER/REPO#NUMBER`、各leafで許可された動的selectorを使います。裸番号やIssue URLは通常TARGETとして使えません。importのREFは別の文法で、完全gh ref・完全Issue URL・裸番号と`--github-repo OWNER/REPO`の組合せを受け付けます。矛盾するhintや別repositoryは拒否します。

以下の`OWNER/REPO`と親IDは実在する操作対象へ置き換えます。importはGitHubをGETするだけですが、ローカルscaffoldを作成する変更操作です。

```sh
spec-dock scope create initiative --backend github --title "Platform"
spec-dock scope import github epic 124 --github-repo OWNER/REPO --parent init-00123 --title "Authentication"
spec-dock scope show epic-00124
spec-dock work start epic-00124 --base main
spec-dock work finish epic-00124 --yes
```

GitHub 操作の失敗はローカルの状態変更で成功扱いにしません。旧 `new` / `import` / `issue start` の詳細は[歴史資料](../src/spec_dock/assets/spec_dock/docs/historical/README.md)に残しています。
