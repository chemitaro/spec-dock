# 第6回コードレビューの指摘分析

## 対象と証拠

目的はIssue #413のP-03〜P-08通常POSIX経路を確定要件・設計・公開CLI契約へ照合すること。fixed point / merge-baseは`6fec3099d8759b4e5b3b393b2987534b46dfa383`、レビュー対象は`e6513650c419e827fba29746f91d8870ee4ab8aa`。clean worktree、configured GitHub upstreamとHEADのfull SHA一致を確認してfresh Strictを開始し、GPT-5.6 Sol / Pro、wrapper exit 10、`review_status=fail`で完了した。原文JSONは`code-review-p06-06.json`へbyte一致で保存した。44分09秒の外部レビューは静的照合であり、ローカルtestの実行証拠ではない。

関連262 tests、P-08の19 tests、直前のactive/Finish等166 tests、全Ruff check/formatと限定mypyの完了記録は実装記録を参照する。未コミットのP-09作成経路はレビュー対象外。現在、待機中のtest/validation laneはない。Windows native/store、P-09以後、旧runtime退役、full lint/test、手動製品確認、Final Quality Gateは既存の未完了義務であり、本レビューがそれらを認定したとは扱わない。

`analyze-review-findings`を適用し、5件とcoverage境界を一括分析した。authorityは利用者の確定判断、requirement/design、C-03/C-04、plan、AGENTS.md、実装/test、レビュー提案の順に扱う。P1はfresh Strict passまでブロッカー。P2はsource-nativeの分類を保ち、単独で修正campaignや再レビューを開始する条件にしない。今回は利用者が全Issue実装と「指摘があれば分析・修正・再レビュー」を明示許可した同一fail batch内で、確定仕様を満たす限定修正を行う。設計意味の変更、追加の永続化、包括的ロック、実環境cutoverをこの指摘から認可しない。

## F1: [P1] 未知のworktree属性が完全なinventoryとして通る

**妥当性・到達性**: `_parse_worktree_porcelain_nul`は未知keyを辞書へ受理して捨てる。重複keyは全体例外となる。`observe_worktrees`はその正常に見えるrecordからselectionを観測するので、未知属性を含む一覧でもStartの副作用前検査とSyncのcomplete判定を通過し得る。

**違反authority・根本原因**: D-04の完全な重複確認不能時のStart停止、行を残すunavailable観測、D-10の不完全読取を正常にしない保証。最初の誤りはGit inventory adapterの解析境界であり、行の構造を検証せず正常recordへ情報を落としていた。

**primary route**: `implementation-remediation`。既知の属性集合と形を検証し、識別できるpathを持つ不完全なrecordには行単位の診断を保持する。applicationはその行をunavailableとし、後続の健全な行を観測する。path自体を安全に識別できない出力も完全観測にしない。Startは既存の不完全inventory gateでGit効果前に停止、Syncはreadonly partial/7とする。

**検証**: native Git subprocess境界のfixtureで未知field、重複fieldを注入し、公開Startの効果0と公開Syncの健全行・不完全行保全を一つずつRed→Greenで確認する。NUL区切り、改行/空白を含むpath、locked/prunable、native stderrの既存回帰を維持する。

## F2: [P2] stale recordの既知Scopeとdirect件数が落ちる

**妥当性・到達性**: `direct_sync`は`row.views`だけを観測集合へ追加し、件数もstatus=selectedだけを数える。消えたmetadataや旧linkageでstale/unavailableとなってもrecordに既知ID/refが残る経路では、Scope観測や予約件数が欠落する。

**違反authority・根本原因**: D-04の既知ID/refの予約保全、D-10のknown件数とcomplete=falseの分離。最初の誤りはSyncの観測集合組立であり、直接記録と現在metadataを同一の完全観測条件で扱っていた。

**primary route**: `implementation-remediation`。読めた直接記録の既知identityをScope観測へ保持し、現在metadataから確定できないlifecycleはunknownとする。stale/unavailableでも既知direct件数を保ち、祖先が不明な部分は完全性を主張しない。過去の祖先、backend metadata、titleを捏造せず、別WT全Scope走査や保存台帳を追加しない。

**検証**: linked WTの対象metadata消失およびlinkage変更を公開Syncで観測し、旧ID/ref行、direct known件数、unknown、不完全性、元record bytes保全を確認する。

## F3: [P2] 同じGitHub refの異なるScope IDがconflictにならない

**妥当性・到達性**: ID→refだけを照合しているため、未選択の現tree Scopeと別WTの直接対象が異なるIDで同じrefを持つ場合にcomplete=trueとなる。Startは同じrefを同じ直接対象として重複確認するため、観測identityの整合性とも一致しない。

**違反authority・根本原因**: D-10の矛盾したidentityを一方へ黙って統合しない観測と不完全性。最初の誤りはSyncのidentity対応検査。F2と同じ観測集合の責任境界に属するが、対応関係の検査は独立して必要。

**primary route**: `implementation-remediation`。ID→refに加えてcanonical ref→IDも照合し、両観測を保全して`SCOPE_IDENTITY_CONFLICT`とcomplete=false/exit7を返す。IDやlinkageを自動改名/変換しない。GitHub GETのref単位deduplicationを維持する。

**検証**: current treeの未選択Scopeとlinked WTの別ID/同refを公開Syncへ入力し、両行・conflict・readonly effects=[]を確認する。

## F4: [P2] identity不一致recordを--yesなしでclearできる

**妥当性・到達性**: `read_selection`は物理identity不一致をinvalidとするが、`clear --all`はstoreのJSON/件数だけのselected判定を使う。copyされた正規fileを`--yes`なしで解除できる。

**違反authority・根本原因**: D-03のidentity不一致を自動採用しない規則、invalid recordの明示`--all --yes`確認。最初の誤りはclear applicationの捕捉観測への意味付け境界。metadata消失のstale解除と物理identity不一致を混同していた。

**primary route**: `implementation-remediation`。同じcaptured recordと現contextの物理identityを検査し、不一致はinvalid確認条件へ含める。確認後も捕捉した安全なbasenameだけを解除し、新record・未知entry・別WTへ触れない。clearにStart lockやGit checkoutを追加しない。

**検証**: clone/worktree identityを変えた正規fileについて、公開clearの無確認失敗・bytes保全、dry-run無書込、`--all --yes`の捕捉fileだけの解除を検証する。

## F5: [P2] 残存stageがexit5の無効果失敗になる

**妥当性・到達性**: branch/checkoutがunchangedのStartでもpublishはdirectory/stage作成後にfsync/renameで停止する。storeはpre-renameのOSErrorをそのまま投げるため、applicationはfailed/5かつrecoveryなしを返し、残存stageで次回Startがinvalidとなる。

**違反authority・根本原因**: D-03のstage残骸を自動resume/purgeしない規則、C-04/D-06の現物と一致する効果・partial/recovery表示。最初の誤りはstoreの公開失敗分類であり、最終rename前の永続した候補を無効果としていた。

**primary route**: `implementation-remediation`。今回のpublishによるstage作成後の未確認失敗をpublication unknownとして伝え、Startはpartial/6と再観測手順を返す。残存stageの自動purge、rollback、次回の自動resumeは追加しない。空directoryの準備だけで最終record/stageが作られなかった失敗と、残存stageによる次回invalidを区別する。既存record/未知entryの事前拒否は効果なしのまま維持する。

**検証**: 既存の現在branchでselectionが空の公開Startへstage fsync/rename失敗を注入し、Git unchanged、selection.publish unknown、partial6、recovery、残存stage、最終recordなしを確認する。directory作成後の同期失敗、最終公開後の不明、衝突と遅い解除の既存回帰も照合する。

## 認可・保証・親workflowへの帰結

全件のrouteは既存意味を保つ`implementation-remediation`である。新しいSSOT、Scope UUID、registry、cache、daemon、journal、lock、state machine、編集権限制度、rollbackは導入しない。public JSONの既存状態・finding・effectの意味を満たす限定修正で、設計判断を変更しないため追加の人間判断は不要。

F1修正が必要な同一fail batchの中で、明示的に認可されたF2〜F5をTDDで検証・修正し、coherent checkpoint、clean/pushed SHA検証、fresh Strictへ進む。P-09の未コミット作業は分離して保持する。ローカルGreenをStrict passに置き換えず、goalをactiveとして継続する。

## ローカル修正と検証

F1は公開Syncが未知fieldを完全観測としてexit0にするRed、重複HEADが全体exit3になるRedを確認した。行単位の`inventory_error`を持つメモリrecordを追加し、未知field・重複field・値を持つbare flag・不正branch refの既知pathをunavailableとして保持する。健全な行は継続観測する。公開Startの未知/重複fieldではrefs・branch・selectionを変更せず効果0を確認した。新inventory diagnosticsの6 testsが通過した。

F2は両WTから対象metadataが消えた時に`scopes=[]`になるRedを確認した。読めたstale/unavailableの直接recordのidentityを観測集合へ保持し、未知lifecycleとknown direct件数を返す。GH modeでその既知refを取得しないRedも確認し、metadataを捏造せずcanonical refからrepository-bound GETを一回行うようにした。現在metadataがない祖先は作らずcomplete=falseを維持する。

F3は未選択current Scopeとlinked WTの旧local綴りGH-backed Scopeが同一ref/別IDでexit0になるRedを確認した。全identity観測をID→refとref→IDの両方向で照合し、両行を保全してconflict/exit7を返す。GH GETは同じrefに一回のまま。

F4はfixtureのfield名誤りを訂正してから、clone/worktree device不一致を無確認で解除できるRedを確認した。captured recordの物理identityだけを確認条件へ含め、無確認時の保全、dry-run無書込、`--all --yes`で捕捉basenameだけの解除が通過した。stale metadata消失時の既存clearは維持する。

F5は現在branchのままstage fsyncが失敗した公開Startがfailed5/no recoveryになるRedを確認した。所有stageを排他的作成した後のwrite/flush/fsync/rename/readback失敗をtyped publication unknownとする。native POSIX directory permissionでrename拒否を起こし、残存stage/最終recordなし/partial6を確認した。空directoryだけの準備失敗を架空の選択成立にしない。残存stageの自動削除や次回resumeを足さない。

既存unitのraw OSError期待と、branch作成済みの既存Start testのpublish failed期待は、同じF5の旧分類を固定していた。原文分類を変えず、typed unknownを期待する証拠へ更新した。初回関連選択は251 passed/1 failed（69.70秒）でこの旧期待を検出し、訂正後の同選択は252 passed（65.38秒）。source/test全Ruff check、format check（377 files）、変更6 source限定mypyが成功した。最初の存在しないtest path指定によるcollection失敗は製品Redや回帰結果として数えない。

Windows native/store、全体mypy/test、P-09以後、Strict再レビュー、Final Quality Gate、手動製品確認は未完了。P-09の15 testsは別の未コミット単位の証拠であり、このレビュー修正の合格証拠へ合算しない。
