# Start修正後の通常インストールCLIを個別操作で確認

2026-10-02、製品sourceはclean `2b2be5e227ddf4d067da083bba15a8ec23d21367`。source statusは空、コピー入力のfold SHA256は `585aa7d3d1c206d4418765cb38fc0f55a726ff22af6581483e24ec5602b0ace3`、通常wheel SHA256は `45d494b7abf19b865d2cca4b9090bed80ff5b6fb81b4f106e35b2a20624c1551`。

macOS・実Python3.12.11の外部fresh venvへ非editable installし、pip checkを成功させた。所有コピーの元provider pathを別名へ移し、Gitのない外部CWDからsite-packagesの実consoleを起動した。PYTHONPATH/PYTHONHOMEによるsource fallbackは使用していない。

既存のwheel・Git fixture準備helperだけを再利用し、pytestのtest bodyを呼び出していない。全14操作を個別に起動し、stdout/stderr・実exit・前後entryとGitの状態を原文へ保存した。異常系のexit3/6は意図した拒否・部分失敗であり、成功exitへ合算しない。

fresh cloneのmainとlinked worktreeを使用した。GitHub番号1〜5と三階層は所有するtest fixtureで、正式Scopeのオフライン発行ではない。外部gh processだけをstateful fakeへ置換し、26 requestを保存した。live GitHubや本repositoryのconsumerは変更していない。

| 個別操作 | 実際の結果 |
|---|---|
| projectなしのhelp、Start/Sync/Finishのleaf help（4操作） | exit0・stderr空・entry変更0。controlなしで到達 |
| mainのIssue A Start dry-run | planned/exit0。branch・record・entry変更0 |
| mainのIssue A Start apply | branch作成・checkout・一件公開。branch=issue-a |
| linkedの同じA Start | SCOPE_ALREADY_SELECTED/exit3、effects=[]、linked entry変更0 |
| linkedの兄弟B Start | branch=issue-b、一件公開。A/Bが同時に直接選択 |
| GitHub-source Sync | A/Bを表示。Epic/Initiativeのdescendant count=2、direct count=0、process_state=not_observed。effects=[]・entry変更0 |
| A Finish dry-run | planned/exit0、entry変更0。PATCHなし |
| A Finish apply | state=closed/state_reason=completedのPATCH一回→確認GET→捕捉Aだけ解除。branch=issue-aを保持し、Bには触れない |
| mainの次Issue C Start | switch flagなしで成功。branch=issue-c、新しいtoken一件 |
| 実post-checkout hookが二行stderrとexit1を返すInitiative Start | Gitはbranch作成・checkout済み。partial/exit6、started=false。native returncode1と全stderrを保存。clear/publishはnot_attempted。旧Cを保持し、Git効果を巻き戻さない |
| 部分失敗後のactive show text | Cと祖先を保持し、branch_changed=true。entry変更0 |

seed/main/linkedのtracked spec fold SHA256は全て `fc82c99b584ca0eb73923a28b6818b759121d059f5661aad76916c210f79ab23`、Git statusは空。独自 `.git/spec-dock` は存在しない。Git本来のHEAD/refs/reflog変化と独自control書込みを区別した。部分失敗前後でC/B recordのbytes/hashは同一だった。

補助的な結果検査では、status=succeeded、text出力内JSON、fake保存値completedの三箇所で表記の取り違えがあった。保存した原文を再読して補正し、CLIの再実行や製品source変更で成功を作り直していない。原文と状態の十八項目の照合は成功した。

[原文・file観測・GitHub境界log](manual-console-2b2be5e2.json)のSHA256は `e7b99aae6d816775fa4cfbfea5d930ec87bb50095bc84173dcc662a78d758021`。同候補の[通常macOS全件](macos-full-2b2be5e2.md)は1916 passed/4 skipped、exit0。この手動結果は主要フローの観測であり、全CLI leaf、live GitHub、Windows、最終gate、実導入の全面合格を主張しない。[先行候補の手動証拠](manual-console-75ac5760.md)も別sourceとして保持する。
