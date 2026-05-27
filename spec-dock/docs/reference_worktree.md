# 作業ツリー参照（reference: worktree）

`spec-dock worktree` は、長命の手動管理 Git linked worktree を作るための補助コマンドです。
Codex app が `$CODEX_HOME/worktrees` 配下に作る短命 worktree は、このコマンドの管理対象ではありません。

## コマンド（command）

```bash
./spec-dock/scripts/spec-dock worktree create [LABEL]
```

`LABEL` は任意です。指定する場合は lowercase letters、digits、hyphen のみを使います。
underscore、dot、space、slash、uppercase、shell metacharacters は拒否されます。

## ディレクトリ構成（directory layout）

`worktree create` は `SPEC_DOCK_WORKTREE_ROOT` で指定した central root 配下に、repo basename の namespace directory を作り、その中に worktree を作ります。
`SPEC_DOCK_WORKTREE_ROOT` は必須です。未設定、空文字、空白のみの場合は fatal error になり、Git branch、worktree directory、bootstrap side effect は作られません。

設定例:

```bash
export SPEC_DOCK_WORKTREE_ROOT="$HOME/workspace/worktrees"
```

layout:

```text
~/workspace/worktrees/
  spec-dock/
    spec-dock-wt1/
    spec-dock-feature/
```

worktree path は `$SPEC_DOCK_WORKTREE_ROOT/<repo-basename>/<repo-basename>-<id>` です。
central root directory と namespace directory は、必要に応じて command が作成します。
main checkout の中に nested `.worktrees/` は作りません。

`SPEC_DOCK_WORKTREE_ROOT` は `~` 展開後に absolute path である必要があります。
通常 directory と directory を指す symlink は許可されます。
relative path、file、壊れた symlink、directory として使えない path は fatal error です。

linked worktree から実行した場合も、Git が認識する main worktree を基準に namespace と repo basename を決めます。
branch name は実行元 checkout の current branch を基準にします。

過去バージョンで作られた sibling `<repo-basename>-worktrees/` は legacy placement です。
この command は既存 sibling worktree を移動・削除・migration しません。
future `worktree create` は central root を使い、missing env var 時に sibling placement へ fallback しません。

## 命名（naming）

LABEL なし:

```text
id: wt1, wt2, wt3, ...
path: $SPEC_DOCK_WORKTREE_ROOT/<repo-basename>/<repo-basename>-<id>
branch: <current-branch>-<id>
```

LABEL あり:

```text
id: <label>, <label>2, <label>3, ...
path: $SPEC_DOCK_WORKTREE_ROOT/<repo-basename>/<repo-basename>-<id>
branch: <current-branch>-<id>
```

directory、branch、Git worktree record の collision がある場合は次候補へ進みます。
candidate exhaustion は fatal error です。

## 初期化（bootstrap）

worktree 作成後、new worktree root で `make init` を任意 bootstrap として実行します。

- `make init` target がない場合は `skipped`。
- `make` が見つからない、Makefile parse error など detection に失敗した場合は `detection_failed` warning。
- `make init` が失敗した場合は `failed` warning。
- `make init` が成功した場合は `succeeded`。

bootstrap の detection / execution failure は worktree 作成成功を取り消さず、command exit code も `0` のままです。

## 出力（output）

成功時は absolute worktree path、id、branch、bootstrap status を出力します。
bootstrap warning は既存 CLI warning path に流れます。

```text
spec-dock: ok (worktree create) id=wt1 branch=main-wt1 path=/abs/path/worktrees/spec-dock/spec-dock-wt1
spec-dock: worktree bootstrap status=skipped command=-
```

## 失敗条件（failure）

次は fatal error です。

- Git repo 外での実行。
- detached HEAD での実行。
- invalid label。
- missing / blank `SPEC_DOCK_WORKTREE_ROOT`。
- invalid `SPEC_DOCK_WORKTREE_ROOT`。
- central root / namespace directory の作成失敗。
- non-retryable `git worktree add` failure。
- candidate retry ceiling exhaustion。

## スコープ境界（scope boundary）

この command は create のみを扱います。
`worktree list`、`status`、`remove`、`prune`、Codex-managed worktree cleanup は future extension です。
