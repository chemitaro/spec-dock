# 最新候補の通常インストールCLIを個別操作で確認

2026-10-02、製品sourceはclean <code>75ac57604f5b95f1c50a2e7214d711bc720fb0eb</code>。source statusは空、コピー入力のfold SHA256は126058d7bcbe1d1a6d5cf77d60c96592016497dd9554e8000aa6f849a6f871c5、通常wheel SHA256は84001559f6ca328a42aa52d21f7fd0561dab12396818f107434335cc39302a9a。

macOS・実Python3.12.11の外部fresh venvへ非editable installし、pip checkを成功させた。所有コピーの元provider pathを別名へ移し、Gitのない外部CWDからsite-packagesの実consoleを起動した。PYTHONPATH/PYTHONHOMEによるsource fallbackは使用していない。

既存のwheel・Git fixture準備helperだけを再利用し、pytestのtest bodyを呼び出していない。全14操作を一つずつツールで起動し、stdout/stderr・実exit・前後entry・実Gitの状態を原文へ保存した。異常系exit3/6は意図した拒否・部分失敗であり、成功exitと合算しない。

fresh cloneのmainとlinked worktreeを使用した。GitHub番号1〜5と三階層は所有するtest fixtureで、正式Scopeのオフライン発行ではない。外部gh processだけをstateful fakeへ置換し、28 requestを保存した。live GitHubや本repositoryのconsumerは変更していない。

| 個別操作 | 実際の結果 |
|---|---|
| projectなしのhelp、Start/Sync/Finishのleaf help（4操作） | exit0・stderr空・entry変更0。controlなしで到達 |
| mainのIssue A Start dry-run | planned/exit0。branch・record・entry変更0 |
| mainのIssue A Start apply | branch作成・checkout・一件公開。branch=issue-a |
| linkedの同じA Start | SCOPE_ALREADY_SELECTED/exit3、effects=[]、linked entry変更0 |
| linkedの兄弟B Start | branch=issue-b、一件公開。A/Bが同時に直接選択 |
| GitHub-source Sync | 二worktreeのA/Bを表示。Epic/Initiativeのdescendant count=2、direct count=0、process_state=not_observed。effects=[]・entry変更0 |
| A Finish dry-run | planned/exit0、entry変更0。PATCHなし |
| A Finish apply | closed/completedのPATCH一回→確認GET→捕捉Aだけ解除。branch=issue-aを保持し、Bには触れない |
| mainの次Issue C Start | switch flagなしで成功。branch=issue-c、新しいtoken一件 |
| 実post-checkout hookが二行stderrとexit1を返すStart | Gitはbranch作成・checkout済み。partial/exit6、started=false。native returncode1と全stderrを保存。clear/publishはnot_attempted。旧Cを保持し、Git効果を巻き戻さない |
| 部分失敗後のactive show text | Cと祖先を保持し、branch_changed=true。entry変更0 |

seed/main/linkedのtracked spec fold SHA256は全てfc82c99b584ca0eb73923a28b6818b759121d059f5661aad76916c210f79ab23、各Git statusは空。独自.git/spec-dockは存在しない。Git本来のHEAD/refs/reflogの変化と独自control書込みを区別した。部分失敗前後でC/Bのrecord bytes/hashは同一だった。

[原文・file観測・GitHub境界log](manual-console-75ac5760.json)を保存した。同候補の[通常macOS全件](macos-full-75ac5760.md)は1900 passed/4 skipped、exit0。この手動結果は主要フローの観測であり、全CLI leaf、live GitHub、Windows、最終gate、実導入の全面合格を主張しない。[旧候補の手動証拠](manual-product-smoke.md)も別sourceとして保持する。
