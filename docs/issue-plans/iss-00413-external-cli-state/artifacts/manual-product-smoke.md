# 通常インストールした候補CLIの手動確認

2026-10-02、候補 `8a70a8b30e69fe0bda6db6c45ef555f44411236d` の製品source。provider source statusは空、source fold SHA256は `b07821e35492f31ba68516552f050a398d345dc8fc546e075c36c63d097576b4`、通常wheel SHA256は `74566c73083befd9bf20ab55e9c49cfd0589d4da183bd99e11d050bf18687b0e`。

macOS・Python 3.12.11の外部fresh venvへ通常installし、pip checkを実行。providerの所有コピーは別名へ移し、consoleはsite-packagesからimportした。Gitのない外部CWDから、各コマンドをツールで個別に実行し、stdout/stderr/実exit/変更entryとGitの現物を確認した。pytestのtest bodyは実行していない。環境準備だけは既存のwheel/fixture helperを再利用した。

fresh cloneとlinked worktree、実Gitを使用。GitHub番号1〜5に紐づく三階層は所有するtest fixtureで、正式Scopeのオフライン発行ではない。外部`gh` processだけをstateful fakeへ置換し、GET/PATCH内容を記録した。live GitHub、本repositoryのconsumer、正式#413は変更していない。

| 個別操作 | 実際の結果 |
|---|---|
| projectなしの`--help`、`work finish --help` | exit 0 / stderr空。control不要。Finishの条件付き解除・完了確認・branch保持を説明 |
| mainのIssue A Start dry-run | planned / exit 0。branch・記録・ファイル変更0 |
| mainでIssue A Start | branch作成・checkout・一件公開が成功。現在branch=`issue-a` |
| linkedで同じAをStart | `SCOPE_ALREADY_SELECTED` / exit 3 / effects=[] / linked entry変更0 |
| linkedで兄弟BをStart | `issue-b`へ切替、一件公開。A/Bの同時直接選択が成立 |
| GitHub-source Sync | selected A/B二行、Epic/Initiativeのdescendant count=2、direct count=0、process_state=not_observed。effects=[] / entry変更0 |
| A Finish dry-run | planned / entry変更0。Closeは送信しない |
| A Finish apply | PATCH closed/completed一回、確認GET後に捕捉Aだけ解除。branch=`issue-a`のまま。Bの記録は保持 |
| mainで次のC Start | switch flagなしで成功。branch=`issue-c`、新しいtoken一件 |
| 実post-checkout hookがstderr二行・exit 1を返すStart | Gitはbranch作成・checkout済み。CLI partial / exit 6 / started=false。native returncode=1と全stderrをJSONへ保存。selection clear/publishはnot_attempted、旧Cは保持。Git効果を巻き戻さない |
| 部分失敗後の`active show` text | Cの選択・祖先を保持し、current branchの違いをbranch_changed=trueで表示。entry変更0 |

最終確認ではseed/main/linkedのtracked spec fold SHA256が全て `fc82c99b584ca0eb73923a28b6818b759121d059f5661aad76916c210f79ab23`、各Git statusは空、`.git/spec-dock`は存在しない。部分失敗前後のC/B記録のhashは一致した。Git固有のrefs/reflog/HEADの変更と、独自control/registryの書き込みを区別した。

[原文・file観測・GitHub境界ログ](manual-console-8a70a8b3.json)を保存する。この確認は選択した主要フローの手動証拠であり、Windows、live GitHub、全CLI leaf、最終候補の全面認定、実導入の成功を主張しない。
