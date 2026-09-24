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
