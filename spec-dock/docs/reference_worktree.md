# Git worktree（Current）

worktreeは同一Git common directoryに属する作業場です。`worktree create` は明示したbaseから作業場を作って登録します。tool導入や任意projectの初期化は実行しません。

```sh
spec-dock worktree create feature-a --base main
spec-dock worktree list
spec-dock worktree show feature-a
spec-dock worktree bootstrap feature-a --yes
spec-dock worktree remove feature-a --yes
```

`worktree bootstrap` は対象で `make init` を実行するため、実行先と副作用を先に確認してください。`worktree remove` はmain/current/bare、dirty、未登録などを拒否し、branch自体は残します。locked状態やignored payloadには個別の明示flagが必要です。Workbenchのscope-localコピーは `workbench copy --scope TARGET --to-worktree WORKTREE_REF` で行い、正本にはしません。旧版の詳説は[historical](historical/reference_worktree.md)です。

`worktree create` が停止した場合、Git common directory の `spec-dock/control/worktree-create/wtN.json` に対象・固定commit・停止段階が残ります。同じNAME（NAME省略時は同じrootとbase）への盲目的な再実行を拒否します。記録と `git worktree list --porcelain`、対象path、`refs/heads/worktree/wtN`、control登録を読み取り専用で照合してください。効果が残っていれば対象を保全して個別に復旧します。path・branch・Git登録がすべて存在しない状態に安全に戻した後だけ、同じ `--base`、NAME、`--root` で `worktree create ... --recover wtN` を実行できます。`--recover` は対象の同一性と効果なしを再確認し、元のstable IDを再利用します。
