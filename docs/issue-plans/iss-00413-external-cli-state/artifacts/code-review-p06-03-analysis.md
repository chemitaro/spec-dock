# P-03〜P-06 Strict第3回レビューの全件分析

## 証拠と判定

固定範囲は`6fec3099d8759b4e5b3b393b2987534b46dfa383..8ad73cfdc75ca53e5cc505adf15b49765207699f`。通常Oracle wrapper、GPT-5.6 Sol / Pro、新規会話で完了し、exit10、review_status=fail。[原文JSON](code-review-p06-03.json)を元stdoutのbytesのまま保管する。原文P1三件/P2二件の分類は変更しない。レビュー自身は試験を実行していない。

レビュー対象のローカル証拠は524 passed/1 skipped。後続commit `12643cd70540568a143af1fb5b1ca339ef1a26fc`のbranch leafとrecord停止境界は597 passed/1 skipped、Ruffおよび限定mypyを通過したが、このSHAはレビュー対象外。さらに現在P-07 active接続は未commitで、公開CLIの17件が成功した。いずれも独立review passや全製品完成ではない。関連する実行中試験はなく、レビューも終了済み。以下全件のcontrol/data pathを現行sourceと確定契約に照合した。

## 全件の判断

| ID / 原文分類 | 妥当性・到達条件・影響 | 違反authority / 最初のfault layer | primary route / 対応と検証 |
|---|---|---|---|
| F1 / P1 | 空のselectionから現在branch/HEADと同じ既存refへStartしてもcheckoutを起動する。不要hookが動き、無変更をsucceededとするため効果前publish失敗がpartialへ誤分類される。source上で妥当 | D-06、C-04の既存無変更はunchanged。implementationのGit操作判断とeffect分類 | implementation-remediation。branch/HEAD/固定tipが全て一致する場合のみcheckoutを省略しunchangedにする。native hookを置き、呼出し0・公開成功と公開前失敗の分類を検証する。レビュー推奨の「実行checkoutを事後確認後だけsucceeded」は限定する。native checkout成功で確認済みの効果は、後のphysical identity/metadata不一致でも隠さない |
| F2 / P1 | checkoutが成功してbranch/HEAD/必要metadataが一致してもhookが他のtracked/untracked fileを変更し得る。現行Startはclean再確認なしに旧record解除/新record公開へ進む。source上で妥当 | D-06のclean条件と固定snapshot、RQ-413-09/C-04の途中効果保持。implementationの公開前postcondition不足 | implementation-remediation。checkout後、解除後の公開前に現物のGit cleanを確認し、dirtyならGit効果を保持したpartialで停止する。native post-checkout hookでtracked fileを変更し、旧selection保持・新recordなし・raw Git効果を検証する |
| F3 / P1 | candidateの非対象Scopeまたはepics/issues containerがblob/symlink/gitlinkの場合、recursive leaf列挙のmaterializerがその位置を捨てる。現在treeでは正常でもcandidate検証をすり抜け、Git効果後に初めて失敗する。source上で妥当 | D-06の切替先snapshot事前検証、D-09構造schema。implementationのcommitted tree投影欠落 | implementation-remediation。tree entryも列挙して、Scope/container位置の非tree entryをmaterialize前に拒否する。通常資料blobは許容する。実Git candidateで各構造位置のblob/symlink/gitlinkを作り、branch/checkout前のeffects=[]を検証する |
| F4 / P2 | rename後の同期/readback失敗でattempt tokenを確定selection_tokenとして返す。unconfirmed handleと確認済み結果を区別できない。source上で妥当。単独のgate blockerではない | C-03の未確定値null、D-03公開確認。implementationの結果data形成 | implementation-remediation。公開確認不能ではselection_token=null。unknown effectと現物再観測の案内は保持する。外部OS fsync失敗で確認する。P2単独の追加review cycleにはしない |
| F5 / P2 | 初回empty確認後に外部から別正規record/未知entryが追加されてもown bytesだけ確認してstarted=trueを返せる。協調Startは排他済みだが外部file変更は到達可能。source上で妥当。単独のgate blockerではない | D-03の0/1 recordとinvalid停止、C-03 started。implementationの公開後directory観測不足 | implementation-remediation。公開確認時にdirectoryが自handle一件の妥当selectionであることを再観測する。追加entryは保存しunknownで停止する。外部OS rename/fsync境界で第二record/未知entryを挿入して検証する。悪意ある変更までatomic CASとは主張しない |

## 認可・保証・帰結

全件は利用者の実装と指摘分析・修正・再レビューの明示認可に含まれる。必要な保証は確定済み要件/設計から導かれ、API・状態所有者・保存先・排他範囲・回復モデルを変更しないため、人間による新判断は不要。Startだけの短いOS排他、immutable record、捕捉token解除、Git原文と確認済み途中効果、rollback/registry/journal/cacheなしを維持する。

F1〜F3が現在review候補をblockする。全件分析後に縦のRed→Greenを実行する。修正・検証・計画をcommit/pushし、現在の完全一致GitHub SHAを新規Strictで再レビューする。P2を新しい合格条件として外部reviewへ貼らず、現在の契約と実装を独立に評価してもらう。ローカル修正やこの分析で原文failをpassへ置換しない。

Windows store/native、全体mypy、P-07以後、全体gateと製品手動確認は未完了の既存義務として維持する。今回レビューが明示的に対象外としたこれらをreview passの証拠に変えない。

## 修正後のローカル証拠

- F1: 実Gitの現在branchへのStartがpost-checkout hookを実行するRedを確認した。branch/HEAD/固定tipが一致する場合のみcheckoutを省略してunchangedとなり、hookは実行されなくなった。同条件のstage作成拒否は、実Git効果なしのfailed/exit5であることも確認した。
- F2: native post-checkout hookでtracked fileを変更する場合とuntracked fileを作成する場合の両方で、旧recordを置き換えてstarted=trueとなるRedを確認した。checkout後とselection変更/公開前のclean再確認後は、Git効果をsucceededとして保持したpartial/exit6となり、旧recordのexact bytesが残る。branchを戻さない。
- F3: 実Gitの候補commitで5種のScope/container位置にblob/symlink/gitlinkを置いた15ケースを検査した。9ケースが効果後失敗または成功を誤って返すRed、6ケースは既に効果前停止だった。tree entryを含む列挙と構造位置のmode/type確認後、15ケース全てがeffects=[]、元branch維持、新ref/recordなしでexit3となった。
- F4: rename後のdirectory fsync失敗を外部OS境界で発生させ、未確認tokenが返るRedを確認した。修正後はpublish unknown/exit6、started=false、selection_token=null。現物recordは保全する。
- F5: 公開後のnative directory fsync境界で第二正規recordまたは未知entryを挿入するとstarted=trueとなるRedを確認した。directoryの再観測でsole valid selectionを確認後は、両ケースでpublish unknown/exit6、token=null、追加entryも保全する。

関連選択は619 passed/1 skipped（52.50秒）。変更3 sourceの限定mypyと対象Ruff checkが成功した。これはmacOS上のnative Git/OS証拠であり、Windows native検証や再レビューpassではない。
