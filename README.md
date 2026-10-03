# spec-dock

SpecDockはGitHub Issueに結び付いたInitiative・Epic・Issueの三階層で仕様・依存・成果物を管理するPython CLIです。番号はGitHubを正本にし、新規Scopeのオフライン作成やUUIDを使いません。業務CLIは `scope`（仕様ノード）、`active`（現在の直接対象）、`work`（開始・完了）を分け、branch、dependency、artifact、worktree、workspace、installationを独立した操作群として提供します。

対応OSはLinuxとmacOS、Pythonは3.10以上です。業務コマンドは他のOSでは変更前に `UNSUPPORTED_PLATFORM`（exit 3）で停止します。help・version・completionはrepositoryや業務用のOS原語に依存しません。

## 入口

- [現行CLIの全44コマンド](src/spec_dock/assets/spec_dock/docs/reference_cli.md)
- [日本語のオフライン説明資料](src/spec_dock/assets/spec_dock/docs/cli-redesign-guide.html)
- [導入・移行・保全](src/spec_dock/assets/spec_dock/docs/migration.md)
- [文書作成ガイド](src/spec_dock/assets/spec_dock/docs/authoring/overview.md)

通常packageとしてworktree外に導入した `spec-dock` が入口です。`./spec-dock/scripts/spec-dock` はPATH上の外部consoleへ委譲するshimです。Git共有controlやcheckout内Pythonに依存しません。`spec-dock help` と各leafの `--help` が正確な引数のauthorityです。

CLIはagent-firstで運用します。依頼または承認済み計画の範囲にある普通のlocal/Git/GitHub操作をagentが実行して結果を検証し、破壊的操作には正確な対象と明示的な削除等の許可を求めます。PR mergeは人間が行います。

以下の番号は例です。実際には各作成結果から返されたIDと、存在するbaseを使います。

```sh
spec-dock scope create initiative --backend github --title "Platform" --json
spec-dock scope create epic --backend github --parent init-00123 --title "Authentication" --json
spec-dock scope create issue --backend github --parent epic-00124 --title "Refresh tokens" --json
spec-dock work start iss-00125 --base main --json
spec-dock active show --json
spec-dock workspace sync --source github --json
spec-dock work finish iss-00125 --yes --json
```

Startはlive readiness確認、branch作成またはcheckout、worktree自身の直接対象一件の取得まで行います。同cloneのmain/linked worktreeを必要時に観測し、Startだけ短い排他で重複確認から記録公開までを守ります。別cloneや別PCは集計せず、通常編集のlock、共有台帳、journal、cacheを追加しません。

Finishはbackendのcompletedを確認して、捕捉した直接記録だけを解除します。GitHub Issueは完了理由でclosedとなり、branchには留まります。commit、test、review、push、PR、mergeは別途確認します。`active clear` は選択だけ、`scope close` は完了状態だけを変えます。`active set` は同じ妥当な直接対象へのunchangedだけを許し、空/別対象の取得はStartへ戻します。


## 実行package・配布資産・worktree状態の境界

同じ「SpecDock」に見えるものでも、更新単位と正本は異なります。

- `src/spec_dock/` はproviderの開発sourceです。CLI実装は主に `src/spec_dock/runtime/`、配布する文書・template・skill・shimは `src/spec_dock/assets/` にあります。
- 利用者が実行するのは、worktree外のtool環境へ通常packageとして導入した `spec-dock` です。sourceの編集やbranch切替だけでは、導入済みpackageは更新されません。package更新はその利用者のtool環境に対する更新で、consumerごとにPython runtimeをコピーする操作ではありません。
- 各consumer worktreeに置く `spec-dock/docs`、`spec-dock/system`、`spec-dock/templates`、root `.agents/skills`、shim、workspace宣言は静的資産です。新しいconsumerはこれらを受け取りますが、Python runtimeは受け取りません。既存consumerの静的資産更新は、明示したworktree一つずつ行います。
- `spec-dock/.agent/work-target/target-<32桁token>.json` は、そのworktreeだけのignoredな直接作業記録です。file tokenは記録実体を安全に捕捉するための識別子であり、GitHub番号から作るScope ID、UUID、operation IDではありません。

このrepositoryの `spec-dock/` とroot `.agents/` はconsumer側の投影です。製品sourceや配布元を変更するときはprovider側を正本とし、consumer側はCLIによる明示更新と現物確認を別に行います。

## 導入と更新

レビュー・通常試験が済んだwheelを、例えば `uv tool install /absolute/path/spec_dock-VERSION-py3-none-any.whl` でworktree外に導入します。packageの更新とcheckoutの静的資産更新は別操作です。

```sh
spec-dock installation init /absolute/project --dry-run --json
spec-dock installation init /absolute/project --yes --json
spec-dock installation show --target /absolute/project --json
spec-dock installation update --target /absolute/project --backup-dir /absolute/new-static-backup --yes --json
```

対象は明示したGit worktree一つです。initは静的資産とworkspace宣言を置きます。updateは既知path/hashの資産だけを保全・更新・個別退役し、未知改変はmanual mergeへ戻します。runtimeをcheckoutへ配布せず、Git内の独自領域を作りません。

旧schema3 writerの移行は旧writer停止、実体保全と復元確認を先行し、`workspace migrate --to-schema 3 --to-writer-protocol specdock.worktree-writer/v1` で自workspace宣言だけを切り替えます。適用時の外部backupと確認条件、部分失敗のeffectsは[移行ガイド](src/spec_dock/assets/spec_dock/docs/migration.md)で確認してください。自動巻戻し、resume、rollbackによるjournal replayはありません。

`SPEC_DOCK_WORKTREE_ROOT` はnative linked worktreeの配置先です。使う場合は絶対pathを指定し、worktree作成時には `--base REF` を明示します。project-owned `make init` は別のbootstrap操作です。

## 開発

provider側の正本は `src/spec_dock/`、通常runtimeは `src/spec_dock/runtime/` です。`src/spec_dock/assets/` の静的文書・template・skill・shimを導入先へ配布します。このrepositoryの `spec-dock/` はdogfooding用consumer workspaceで、候補sourceの編集と実環境への切替は分けて検証します。

```sh
make lint
uv run pytest
```

Provider CIもlintと通常のpytestを実行します。仕様と検証記録は対象IssueのRequirement、Design、Plan、Reportで追跡します。
