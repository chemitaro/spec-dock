# P-03〜P-06 Strict第2回レビューの全件分析

## 証拠と判定

対象は`6fec3099d8759b4e5b3b393b2987534b46dfa383..c0389222a7defc891d9b56c10d9b10090db40151`。通常Oracle wrapper、GPT-5.6 Sol / Pro、新規会話で完了し、exit10、review_status=fail。P1三件とP2一件を原文分類のまま保持する。[取得JSON](code-review-p06-02.json)はstdoutの元bytesと完全一致している。レビューはローカル試験を実行した証拠ではない。

レビュー待ちの後続P-06実装では519 passed/1 skipped、全Ruff check/format、変更9 sourceの限定mypyが成功した。Git初期branchがmasterの外部設定でもfixtureのmainを明示して公開Start試験1件が成功した。現在の変更は未commitであり、レビュー済みSHAと同一とは扱わない。以下の四つの経路は現行変更にも残っていることをsource照合で確認した。関連する実行中試験はない。

## 全件の原因・経路・認可

| ID / 原文分類 | 妥当性・到達条件・影響 | 権威・最初の誤り | primary route / 対応と検証 |
|---|---|---|---|
| F1 / P1 | 保持したroot/common handle自体のverifyと、Gitが再解決したcontextのidentity照合は別の条件。現在は前者だけでfresh cloneの不一致を検出しない。commondirが切替わると別cloneへのGit効果や旧identity record公開を許し得る。source経路として妥当。native再現は次の試験で確認する | D-03/D-05/D-06。implementationのcontext binding不足 | implementation-remediation。全fresh contextを利用前にheld root/common identityへ照合する共通判定を用いる。外部OS flock境界でseparate git-dirのclone参照を切り替え、Git効果0の公開CLI試験を行う |
| F2 / P1 | 非0 checkout後にHEAD/branchが元のままでも、途中でtracked file/indexが変わり得る。現行分岐はclean再確認なしでfailed/exit5を確定する。source経路として妥当。native smudge失敗を次の試験で再現する | RQ-413-09、C-04、D-06。implementationの効果観測不足 | implementation-remediation。元HEAD/branchと元のclean/必要metadataまで確認できたときだけfailed、それ以外はunknown/partial。既存branch再利用とrequired smudge filterの実Git失敗で検証する |
| F3 / P1 | Aが有効な状態で、Aを含まない有効candidateのBへ明示switchした後、同じ旧recordがstaleへ再解釈される。現在のinventory照合はsemantic status/祖先/reasonを正規化せず、record自体が同じでも停止する。source経路として妥当 | D-03の明示解除、D-04、D-06 step6。implementationのsnapshot比較層の誤り | implementation-remediation。自WTのcheckout後は捕捉したrecord/handle/physical identityの同一性を必須とし、candidateが変えた旧対象のsemantic解釈だけを許す。A欠落/linkage差/祖先差のcandidateへのB明示switchを公開CLIで検証する。Start前からstaleな旧対象の暗黙採用は許さない |
| F4 / P2 | rename/fsync/readback/held handle確認後のstore close失敗で、記録済みpublish成功を後の汎用catchがfailedと扱う。source上のeffect追加位置から妥当。P2は今回の不合格理由ではない | C-04、D-03公開成立点、D-06。implementationの効果記録位置 | implementation-remediation。既存P-06の途中効果分類義務内で、確認済みpublishをcleanupより前に記録する。外部os.close境界の失敗試験で公開効果とcleanup失敗を区別する。P2単独で新しいgateや再レビューcycleを作らない |

全件は利用者の実装・指摘分析・修正・再レビューの明示認可と、確定済み要件/設計の範囲内で対応する。仕様・状態所有者・保存先・排他範囲・回復権を変更しないため、人間による新たな意思決定は不要。

## 保つ保証と親workflowへの帰結

GitHub番号のScope ID、Startだけの短いOS排他、worktree局所のimmutable record、readonly Sync、捕捉tokenだけの解除、raw Git出力、自動巻戻し/registry/journal/cacheなしを維持する。新たなlock、永続状態、retry/resume権は加えない。F3では明示switch後のsemantic解釈だけを許し、record/handleや他WTの変化を隠さない。

P1三件が候補をblockする。全件分析を終えた上で縦のRed→Greenを行い、修正結果・試験・計画をcheckpoint commitし、現在のGitHub完全一致SHAに対する新規Strict再レビューを実施する。ローカル修正やこの分析だけでreview_status=passへ変更しない。P-06全体、Windows native、P-07以後、全体gate、製品手動確認は別途継続する。

## 修正後のローカル証拠

全件分析後に次の外部境界試験を実行した。Redは修正前の公開CLI結果、Greenは修正後の結果であり、独立再レビューの合格とは区別する。

- F1: main rootとcommon-dirが同じ実Git fixtureで、OS flock取得直後にGit参照先を別commonへ切り替えた。保持directory自体は同一でも、修正前は別cloneへのbranch作成と旧identityのrecord公開が成功した。fresh contextをheld root/common identityへ照合する共通判定を全利用箇所へ接続後はPROJECT_IDENTITY_CHANGED/exit3、Git効果0、recordなしとなった。初期separate-git-dir fixtureはGit自身のworktree一覧が前提を満たさず、製品バグ再現のRedには数えない。
- F2: 実Gitのrequired smudge filter失敗で、HEAD/branchが元のままでも追跡ファイルが削除された。修正前のexit5/checkout failedを、元metadataとcleanの再確認を必須にしてexit6/checkout unknownへ変更した。Gitの元stderr/returncodeを保持し、自動巻戻しはしない。
- F3: A選択後にAがないcandidate Bへ明示switchすると、同じ旧recordがstaleへ再解釈されてpartialとなるRedを確認した。checkout後の自WTではexact record/handle同一性を必須とし、旧対象のsemantic解釈だけを正規化後、Startは成功した。AのGitHub linkageだけがcandidateで変わるケースも含め、2件が成功した。
- F4: 実os.close完了後に外部OS境界でcleanup例外を発生させた。修正前は確認済みpublishをfailedと誤分類した。publish/readback/held handle確認後、store退出前にsucceededを記録して、公開済みrecordと成功効果を保持したままcleanupのpartialを返す。

native fixtureはmacOS上の証拠であり、Windows native受入ではない。原文JSONの分類は変更しない。
