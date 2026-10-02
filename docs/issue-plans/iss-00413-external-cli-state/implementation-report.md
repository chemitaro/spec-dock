# Issue #413 実装記録

## 作業契約

2026-09-30の利用者指示に基づき、レビュー合格済み要件・設計・計画に沿ってTDDで段階実装する。区切りごとに検証・コミット・GPT-5.6 Sol / ProによるChatGPT Code Review Strictを行い、必要な指摘の分析・修正・再レビューを実施する。最終候補ではStrict Final Quality Gateと独立した必須試験、実consoleによる手動動作確認を完了する。

必要な具体化にはImplementation Brief Strictを利用する。実装担当の当初契約はGPT-6.1 Sol / High。2026-09-30の追加指示で実装側の推論レベルはMaxへ引き上げた。外部Strictレビューは指定済みのGPT-5.6 Sol / Proを維持する。人間によるPRマージ、package公開、実環境適用は製品実装・検証と別の証拠として扱う。

- 製品基準: `6fec3099d8759b4e5b3b393b2987534b46dfa383`
- 独立仕様レビュー合格対象: `7e895803cba0d43957e504c9f97637d307bc6a78`
- 実装開始HEAD: `f0280a9e80ab50f960e8298ce11a2c7c7cc821f4`
- branch: `codex/iss-00413-external-cli-state`
- 正本: [要件](requirement.md)、[設計](design.md)、[計画](plan.md)、[CLI契約](artifacts/cli-contract.md)

## P-01 基準取得と最初のRed

変更前の通常試験を実行した。

| コマンド | 実結果 |
|---|---|
| `make lint` | exit 0。ruff check、format check、mypyすべて成功 |
| `uv run pytest` | exit 0。1217 passed、1 skipped、274.82秒 |
| catalogとC-01の照合 | 44 leafが各一回だけ対応。追加・欠落0 |

`tests/cli_runtime/test_issue413_contract.py`の最初の公開入口テストでは、GitHub-backed schema3の独立したconsumer fixtureを作り、controlなしのScope読取を要求した。`main(... scope show init-00001 --json)`は、固定配布レイアウト検証の`ENGINE_PREFLIGHT_FAILED`でexit 3になり、期待するexit 0との差を実際のassertionで検出した。collection/import障害ではない。P-02の通常package入口とP-04のcontrol不要contextでGreenにする対象である。

240件の実Scope metadata、workspace宣言、確定インタビューの変更前hashをWorkBenchに保存した。実Scopeの手編集・旧engineの起動・正式Startの代替操作は行っていない。

P-01は進行中。Git原文・親昇格・Start以外の共通排他の回帰は、それぞれの公開経路を実装する段階で一つずつRed→Greenを確認し、本記録へ追記する。

## P-02 通常packageとutilityの縦経路

138 Python moduleをasset配下から`src/spec_dock/runtime/`へ移し、source/testのimportを`spec_dock.runtime`へ統一した。旧asset directoryをsys.pathへ追加するtest導線を除去した。通常consoleは静的parser/presentationだけを読み、help/version/completionをv2 JSONで返す。業務は現時点で非0の`BUSINESS_NOT_CONNECTED`となり、旧fixed engineへfallbackしない。

installed metadataをversion正本とした。static資産は`importlib.resources.files`から取得する。dogfoodの旧runtimeは実切替前の資料として保持し、provider/static資産の比較からその退役対象だけを分離した。

| 検証 | 実結果 |
|---|---|
| fresh wheel →別venvの非editable install →実console | 成功。Git/ghなし、壊れたproject、root/44leaf help/version/3補完、v2 JSON |
| installed processのimport観測 | utilityでapplication/commands/infra/domain.operation/fixed_bundle/runtime_loaderのimportなし |
| 独自version.txtを9.9.9へ変更 | versionはpackage metadataの0.2.4を維持 |
| sdistから再buildしたwheel | 通常runtime138 moduleとhidden/static資産の収録集合が直接wheelと一致 |
| utility/catalog/TTY lifecycleの関連試験 | 48 passed |
| unit全体＋utility/catalog（static parity修正前） | 764 passed、1 skipped、旧runtime複製parityの1件失敗 |
| static parity修正＋validate/deps関連 | 37 passed |
| 旧fixed-entrypointのcharacterization | 14 passed、旧fixed engineによる2consumer initの1件失敗。新installationはP-12で置換する |
| Ruff check/format | 成功 |
| mypy | 未合格。正常subpackage化で旧namespaceのmissing-import/Anyが解消し、潜在的な型不整合が顕在化。共通fixtureをTypedDictに修正後も737件が残る。隠蔽・gate緩和はしない。退役module/testは担当stepで除去し、残存型はP-13の必須gateまでに修正する |

Implementation Brief Strictは実装開始SHA `f0280a9e80ab50f960e8298ce11a2c7c7cc821f4`に固定し、GPT-5.6 Sol / Proで完了した。[相談記録](https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6abcafd4-1f58-83e8-9592-c163a0a18244)。回答を正本と照合し、utilityとbusinessのimport分離を追加した。ブリーフの助言を製品試験成功とは扱わない。

2026-09-30の利用者指示で一時的にChatGPT Manual Useを選択したが、新規送信前にOracle復旧の指示で解除された。以降のレビューは通常Strict wrapperを使う。

## P-02 最初のコードレビューと修正

StrictコードレビューはP1が1件、fail。v2 parse診断の既知token秘匿漏れを公開入口で再現し、既存`_redact`適用で修正した。関連15試験が成功。[原文](artifacts/code-review-p02-01.json)、[原因・認可・対応分析](artifacts/code-review-p02-analysis.md)。独立再レビューによる閉鎖は未実施。

## P-03〜P-05 POSIX境界の途中checkpoint

直接対象のimmutable記録codecとworktree局所storeを追加した。捕捉したbasename・directory/file実体・bytes hashを照合して解除し、古いAの解除が後から開始したBを消さないことを検証した。破損JSON、複数記録、symlink、公開前fsync失敗はempty/正常選択とせず保全する。Scope番号やmetadata schemaを変更していない。

control不要contextとSchema3 Scope読取を通常入口へ接続した。退役status cacheを読まずGitHub状態は明示観測までunknown。Git inventoryをbinary porcelain -zで読み、改行/CRLFを含むpathを保持する。直接対象が現在treeから消えた場合はstaleとして記録を保持する。

POSIX StartLockは既存common-dirのread-only directory descriptorにOS flockを取得する。別processとの競合、強制終了後の解放、有限0〜300秒入力を検証した。独自Git entryの作成0。実際のwork startにはまだ接続していない。

新契約・store・inventory・lock・envelope・fresh wheelの選択試験は37 passed。旧cache採用を期待する既存試験1件は新契約と不一致だったため、unknown/非採用を要求する試験へ改定し3 passedを確認した。関連83試験は改定前82 passed/この1件failed。Ruff check/formatは全source/testで成功。

Windows identity/store/mutexは未実装で、対応を認定しない。Git inventoryの全異常行、ignore/tracked判定、doctor、GH live readiness、Start効果、Finish/Syncは後続作業。特に全WT全metadata読取は現時点の暫定実装であり、D-04の必要対象限定へ絞る必要がある。

## P-02 再レビューの内容と追加修正

二回目の新規Strict回答は、text parseの既知tokenとURL userinfo未秘匿をP1として指摘した。引用記法により機械JSON検査はexit20だったが、利用者指示に従って意味を分析し、原回答を保全した。[回答](artifacts/code-review-p02-02-response.txt)、[分析](artifacts/code-review-p02-02-analysis.md)。共通秘匿処理をJSON/textに適用し、URLのuserinfoだけを置換、host/pathを維持した。関連20試験が成功。P2/P3のhelp/AGENTS不一致は既存のP-12/P-14義務として記録し、単独のblocking条件に昇格しない。独立再レビューのpassは未取得。

## P-04〜P-06 観測限定と最初のStart縦経路

別WTでは直接recordを先に読み、必要な対象と現在の祖先だけのmetadataを読むように変更した。無関係な壊れmetadataを読まない試験をRed→Greenで確認。対象が消えた予約は残し、読めない対象でも既知recordのID/refを捨てない。

共通dir/rootの物理handleを保持し、同じpathnameの実体置換を検出する。POSIX StartLockで別process排他と強制終了後解放を維持。`--lock-timeout`はStartだけ、既定5秒、有限0〜300秒へ変更した。

通常consoleのStartへGH GET→lock内再観測→branch→checkout→immutable直接記録を接続した。GH GETはロック外。dry-runはlock/write/branch/checkoutなし。既存branchは明示`--branch`かつ`--base`なしを要求し、同じ妥当な対象/branchは記録bytesとtokenを変えずunchanged。Git自身のindex.lockでcheckoutが失敗する実fixtureでは、作成済みbranchを残しpartial6、Git原文のstderr/returncodeをJSON/textへ保持、selection.publishはnot_attemptedとした。ignore不足とlock取得後dirtyはGit効果前に拒否する。

| 選択検証 | 実結果 |
|---|---|
| 新contract/Start/lock/identity/inventory/store/observation/envelopeとfresh wheel | 101 passed、11.64秒 |
| Ruff check/format、全source/test | 成功 |
| 新しい10 source fileのmypy（follow-imports=silent） | 成功。全体型gateとは別 |
| 実Scope metadata 240件のhash | 変更0 |
| 実workspace宣言hash | 変更0 |

P-06はまだ途中。実効依存のlive readiness、切替先の全必要snapshot事前検証、branch tip/inventoryの最終照合、switch-activeと同Scope別branch置換、Git timeout/signalの事後照合、publish確認不能のeffect分類、expect-current/backendなどは未完了。Windows adapterも未実装。現時点の成功試験を全Start受入としない。

## 現在の段階

P-02の独立checkpointレビューはpass。P-03〜P-06は途中実装。P-07〜P-17は未着手。全機能受入、全体lint/test、最終品質ゲート、手動製品確認は未完了。実dogfoodのmetadata/workspace宣言は保持している。

## P-02第三回レビューの合格とP-06具体化

通常Strict wrapperによる第三回レビューはexit 0、`review_status=pass`、P0/P1=0。[原文](artifacts/code-review-p02-03.json)、[全件分析](artifacts/code-review-p02-03-analysis.md)。残ったP2/P3は秘匿metadata、helpのv1表記、repository guideの旧pathであり、既存P-06/P-12/P-14義務として追跡する。単独のP2/P3修正・再レビューcycleは開始しない。

P-06のImplementation Brief StrictはGPT-5.6 Sol / Pro、候補`ddef15e82abf24adf43ec1afc916c9f6b201c1de`のGitHub SHA完全一致を確認してexit 0。[ブリーフ（末尾空白のみ正規化、取得原文はWorkbenchに保全）](artifacts/implementation-brief-p06.md)、[会話](https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6abcc8fc-b194-83ee-a565-3068e1f30d71)。全体を読んで正本に照合した。candidate metadataをcheckout前に読む、実効依存をlive確認、local bytes/branch tip/inventoryを再照合、token限定置換、Git効果の事後観測、公開rename後unknownという順序を採用する。内部collaboratorをwrapするfixture提案はTDDスキルの外部境界原則に合わせ、実Git/OS/Git hookまたは外部API境界を優先する。

## P-03/P-05 Windows API契約とP-06入口

Windows physical identityはread-only/non-inheritableな既存directory handleからVolumeSerialNumber/FileId128を取得するadapterを追加した。各path componentのreparseを拒否し、handleを操作中保持する。Startのnamed mutexはcompact canonical identityのSHA256によるGlobal namespaceだけを使い、ACL変更、Local/PID/file fallbackなし。WAIT_ABANDONEDは所有取得として区別し、通常Startの現物再確認を省略しない。API代替によるread identity/abandoned/timeout/failure解放とcanonical hashをRed→Greenで検査し、POSIXの実別process排他・owner終了解放を保持した。

これはWindows native動作認定ではない。macOS上の外部kernel32 API契約試験とWindows platform指定の型検査を分ける。Windows実process/NTFS試験およびWindows immutable storeは未達であり、P-03/P-05完了とはしない。

直接recordの時刻はUTC RFC3339秒まで必須として、日付のみ/空白separator/分までの三つをinvalidとして保全する試験をRed→Greenで追加した。

P-06入口ではStartの`--source cache`、`--allow-stale`、`--resume`、`--rollback`をcontext前にARGUMENT_RETIRED/exit2で拒否し、help/補完から受付optionを除いた。欠損projectを指定した五通りが、読取/効果なしで拒否するRed→Greenを確認した。これはStart行の移行であり、他leafの旧option整理は既存担当stepへ残す。

選択試験103 passed（3.71秒）とinventory/lock option/fresh wheelの7 passed（6.51秒）。全source/testのRuff check/format成功、新しい4 sourceのmypyとWindows platform指定3 sourceのmypy成功。これらは全体型gate/全試験の代替ではない。

## P-06 切替先snapshotとreadinessの途中checkpoint

固定OIDのGit treeからworkspace宣言とScope metadataだけを一時領域へ読み、checkout前に新writer/schema、三階層、対象/祖先のID・backend・GitHub linkage、dependency graphを検証する境界を追加した。対象が切替先commitにないケースは、従来のbranch/checkout後partialから、副作用前exit3へRed→Greenで変更した。三階層のmetadata列挙も独立fixtureでRed→Green。切替先のタイトル差を同じScope identityで許し、checkout後はcandidateの全metadata paths/exact bytesへ照合する。旧control/cache helperは通常Startへ接続していない。

実効依存はtargetと祖先の宣言から既存domain規則で組み立て、必要なGitHub Scopeを各一回だけGETする。target/祖先はopen、依存自身はcompletedを要求し、未完了依存はREADINESS_NOT_SATISFIED/exit3/効果0、完了依存ならStart成立を検証した。真正の既存local-backedだけで構成されるStartはofflineを一律拒否しない。新規local作成を復活させる変更ではない。

`--expect-current`のcanonical IDを一度固定し、`--expect-backend`とともにpreflight/lock内で比較する。empty directの期待ID指定とbackend不一致は効果0で拒否する。

workspaceと読んだ全own metadataのexact bytes/file identityをmemoryに捕捉し、lock内で再照合する。Git update-indexのassume-unchangedによってstatusがcleanでも、GH GET待ち中に祖先metadataの末尾改行が増えたらGit効果前に停止する実fixtureをRed→Greenで追加した。guarded JSON境界から正確なbytesを返し、JSON再serializeで比較しない。特殊fileはnonblocking open後のregular/single-link検査で拒否する。

Start公開経路とinfra全体は435 passed、1 skipped、4.92秒。skipは既存試験でありWindows native成功を意味しない。Ruff check成功、変更した4 sourceの限定mypy成功。実Scope 240件とworkspace宣言のhash変更0。

このcheckpointもP-06全完了ではない。StartPlanへの純粋なselection決定、same-Scope別branch/switch-active置換、branch tip/全inventoryの最終再照合、Git異常後の現物判定、publish rename後unknown、recovery/C-04の残る公開情報、全platform受入は継続する。

## P-06 selection切替・inventory・途中失敗と第1回レビュー修正

same-Scope別branchは捕捉した旧tokenだけを解除し、新tokenへ置換する。異なるScopeは--switch-active必須。pureなSelectionPlanを一度作り、lock内で再計画と一致を確認する。既存branch tipがGH GET待ち中に変わった場合はGit効果前に停止する。branch名のASCII契約も公開入口で検証した。

Git inventoryの各行へ物理WT identityとGitのHEAD/branch/flagsを保持し、自WT判定にpathname文字列ではなく物理identityを使う。Start前、lock取得後、checkout後、公開直前、旧record解除後に再観測する。他WTの状態や一覧が変われば停止し、成功済みGitは残す。実post-checkout hookで別WTを追加するケースと、外部unlink境界で旧record解除後に別WTを追加するケースをRed→Greenで検査した。他WTにcheckout済みのbranchは効果0で拒否する。

Git mutationエラー時はlockを保持したままHEAD/ref/必要metadataとcleanを再観測し、確認済みの効果だけsucceededとする。実post-checkout hookのexit1でもHEAD/branchが切替済みならその現物を返し、新選択へ進まない。元stdout/stderr/returncodeを薄いGitProcessErrorに保持する。readonly probe失敗が直前の成功済みcheckoutをfailedへ再分類しないこともRed→Greenで検査した。timeout/signalのnative全境界はまだ受入未了である。

recordのrename後fsync/readback失敗はselection.publish unknown、stage同期のrename前失敗はfailed、unlink後fsync失敗はselection.clear unknownとして後続効果を止める。未着手のclear/publishはnot_attemptedを返す。新しいjournal/rollback/再送権は作っていない。既存C-04の秘匿metadata義務として、診断とGit detailsにredacted=trueとcredential/url-userinfo/sensitive-fieldの該当理由を付けるようにした。

独立Strict第1回は候補ad73a06a、GPT-5.6 Sol / Pro、exit10/P1四件でfail。[原文](artifacts/code-review-p06-01.json)、[全件分析](artifacts/code-review-p06-01-analysis.md)。全件分析後、以下を既存要件内で修正した。

- F1: tokenを効果前に一度生成し、exact stage/final pathをcurrentとfixed candidateの双方でGit check-ignoreする。candidateのGit ignoreファイルだけを一時metadata領域へ読み、既存common-dir/configによるread-only Git判定を使う。公開storeへ同tokenを渡す。zero probe専用規則のcurrent/candidateをいずれも効果前exit3とするRed→Greenを確認した。
- F2: required_featuresは省略または対応済みの空string arrayだけを許す。falsyな不正型、未知必須feature、workspaceのtype/control_epochをwriter admissionで拒否する。全current/candidate Scopeへwriter条件を適用し、必須nullable fieldの欠落も構造エラーにする。unknown任意fieldの書換えは行わない。current/candidate workspace16ケースとScope feature、必須field欠落の公開CLIをRed→Greenで確認した。
- F3: unchanged成功前にもcandidate全metadata path/bytesを照合する。assume-unchangedでGit statusがcleanでも未commit metadataが違えば、既存recordを変えず効果0/exit3となるRed→Greenを確認した。
- F4: storeをStartが保持したroot descriptorへ相対bindする。rootとrecordの物理identity一致、公開前・readback後・共通handleの最終照合を維持する。replacement pathを成功扱いせず、公開後の確認不能はunknownとする。held-root bindingの公開adapter試験はmissing capability(TypeError)をRedとして追加し、外部os.open境界でrootを置換したとき、replacementにもdisplaced rootにも.agentを作らず拒否するGreenを確認した。元候補のleakを実行再現したという証拠とは区別する。

二つの独立CLI processとbarrier付きGET専用gh実行fixtureで、同じScopeの同時Startを検証した。成立は一つ、敗者はSCOPE_ALREADY_SELECTED/exit3/効果0。macOS実Git・実processの証拠であり、Windows native認定ではない。

| 検証 | 実結果 |
|---|---|
| Start公開経路、infra全体、複数WT観測/同時Start、redaction/envelope | 497 passed、1 skipped、18.68秒 |
| 全source/test Ruff check・format check | 成功、355 files formatted |
| 変更した11 sourceの限定mypy | 成功。全体型gateの代替ではない |
| 実Scope240件/workspace宣言のhash | 変更0 |

P-06は引き続き途中。完全なpure StartPlanへの整理、OID/option境界、native timeout/signal/killの受入、Git inventory/context timeoutとraw failure整備、C-04の案内、Windows native/store、兄弟Issue同時Start/全platformの証拠が残る。四件の修正はローカル検証済みであり、独立再レビューのpassをまだ取得していない。P-07以降、全体lint/test、最終品質ゲート、手動製品確認、merge後の実dogfood切替は未完了。

## P-06 pure StartPlan・Git境界・兄弟Issueの並行開始

候補`c0389222a7defc891d9b56c10d9b10090db40151`をpushし、第2回の新規Strictレビューを通常Oracle wrapperで開始した。対象はGPT-5.6 Sol / Pro、固定点は`6fec3099d8759b4e5b3b393b2987534b46dfa383`。追記時点では元のセッションで回答生成が継続している。以下は既存P-06義務を進めた変更であり、そのレビュー対象SHAより後の実装である。

`plan_start(request, context, local_snapshot, live_observations)`をmemory-only APIとして追加した。対象ID/ref、branch、固定commit、作成有無、exact inputのSHA256、旧handle、switch許可、selection actionをimmutable StartPlanへまとめる。readiness、期待条件、直接対象重複、branch使用を同じ純粋判断に集約し、lock内の再観測で再計画した結果を照合する。GHアクセス・Git mutation・ファイル操作は計画関数に入れない。既知literalのhashと計画結果を公開API試験で確認した。

以下を縦にRed→Greenで検証した。

- project/context/inventoryおよび他WT探索のnative failureを、元stdout/stderr/returncode付きGIT_FAILED/exit5へ統一した。`--timeout`を各Git呼出しへ渡し、取得済み出力・returncode=null・timed_outを保持する。signal中断はunknownの可能性を保持して現物を再観測する。quiet probeのmissing扱いはexit1かつ両出力が空の場合だけに限定する。
- baseの解決に`--end-of-options`を使い、完全な40/64桁commit OIDだけを採用する。branchはGit ref-format結果が明示名と完全一致することを要求し、`@{-1}`をINVALID_BRANCH/効果0で拒否する。作成後のrefが固定OIDと違えばcheckoutへ進まず、branchを残してpartialを返す。
- same-Scope/same-branchのdry-runにもcandidate全metadata照合を適用する。Git statusがcleanでも未commit bytesが異なる場合はexit3/効果0。readiness待ち中に新しいignored Scopeが追加された場合もcaptured path集合を照合し、branch作成前に停止する。
- 同じEpicの兄弟Issueを二つの実CLI processでStartすると、従来は他方の先行Startを一覧変更として拒否していた。lock取得前の他WTのHEAD/branch/直接対象は最新観測で判定し直す。一覧のpath/物理identity/flags、自WT、効果開始後の全inventoryは変化を拒否する。兄弟Issue二件は両方成立、同じScope二件は成立一つ・敗者効果0となった。
- partial StartへC-04の人向けinstructionsを付ける。resume/rollbackはfalseであり、現物確認と新しい明示Startを案内する。Git原文はtext stderr末尾に保持し、実行権やjournalを作らない。

実CLIをpost-checkout barrierで強制停止する受入試験も追加した。JSONは返らずcheckout済みbranchを残し、OS lockは解放される。次processは既存branchを明示した新Startで成立し、journal/resumeを要求しない。これは既存挙動のGreen確認であり、新しい修正のRed証拠とは区別する。recordのstage/rename/unlinkに関する全kill境界とWindows native受入の代替ではない。

| 検証 | 実結果 |
|---|---|
| Start、infra全体、複数WT観測/並行/強制停止、Git境界、pure plan、OID、redaction/envelope | 519 passed、1 skipped、32.01秒 |
| 全source/test Ruff check・format check | 成功、360 files formatted |
| 変更した9 sourceの限定mypy | 成功。全体型gateの代替ではない |
| 実Scope240件/workspace宣言のhash | 変更0 |

P-06は独立レビュー待ちであり、Windows immutable store/native受入、record公開/解除の残るkill境界、branch leafの通常経路接続を含めて完了とはしない。P-07以後と最終品質ゲート・手動製品確認も未完了である。

## P-06 第2回独立レビューとnative境界の修正

第2回レビューは候補`c0389222a7defc891d9b56c10d9b10090db40151`、GPT-5.6 Sol / Pro、新規通常Oracle会話で完了した。exit10、`review_status=fail`、P1三件/P2一件。[原文JSON](artifacts/code-review-p06-02.json)を元stdout bytesのまま保存し、[全件分析](artifacts/code-review-p06-02-analysis.md)を完了してから修正した。P2だけによる新しい受入条件やレビューcycleは加えていない。

- fresh Git contextのroot/common physical identityを、Startが保持したdirectoryとlockのidentityへ毎回照合する。native Git参照をlock取得後に別cloneへ切り替える試験では、修正前は誤ったcloneへのbranch作成とrecord公開が成功した。修正後は効果前PROJECT_IDENTITY_CHANGED/exit3となった。
- Git checkout失敗後、HEAD/branch不変だけではfailedと断定しない。実required smudge filter失敗で追跡ファイル削除を再現し、元metadataとcleanを確認できない場合はunknown/partial6とした。元Git stdout/stderr/returncodeは保持する。
- 明示switchのcheckout後は、自WTの捕捉record/handleが同一であることを必須とし、旧対象のsemantic解釈だけを正規化する。候補から旧対象が欠落するケースのRed→Greenに加え、GitHub linkage差でstaleになるケースも成功した。
- publish/readback/held handle確認済みの成功効果をstore退出前に記録する。実os.close後のcleanup例外は公開失敗へ分類し直さず、recordを保全してpartialを返す。

| 検証 | 実結果 |
|---|---|
| Start、infra全体、複数WT観測/並行/強制停止、Git境界、pure plan、OID、redaction/envelope | 524 passed、1 skipped、37.74秒 |
| 全source/test Ruff check・format check | 成功、360 files formatted |
| 変更した9 sourceの限定mypy | 成功。全体型gateの代替ではない |
| 実Scope240件/workspace宣言のhash | 変更0 |

この修正候補は独立再レビュー前であり、passとは扱わない。Windows immutable store/native受入、record公開/解除の残るkill境界、branch leafの通常経路、P-07以後、全体lint/test、最終品質ゲート、手動製品確認は継続する。

## P-06 branchの通常経路とrecordの強制停止境界

修正を`8ad73cfdc75ca53e5cc505adf15b49765207699f`にcommit/pushし、同SHAの第3回StrictレビューをGPT-5.6 Sol / Proの新規Oracle会話で開始した。以下はそのSHAより後の実装であり、第3回レビューの合格範囲には含めない。

`branch show/create/switch`を共有registry/journalなしの通常dispatchへ接続した。明示`--name`または`<Scope ID>-<slug>`候補を使い、showはGit refの有無とtipを観測する。createは固定baseとcandidate Scope/祖先/schema/linkageを検査し、新refだけを作る。既存refをresetせずcheckoutもしない。switchはclean、candidate、他WTのbranch占有を効果前に検査し、checkout後のGit/metadata/physical identityを確認する。immutable直接選択記録は書き換えない。dry-runはref/checkoutを予約しない。新しい直接選択の取得は引き続きStartだけである。

通常branch経路、baseに対象がないケース、dry-run、Git hook非0終了後の確認済みcheckout、index.lockによる変更なしの確定、ref作成後の非0終了、誤ったtip、clone置換、占有と期待条件について公開CLIのRed→Greenを実施した。元Git stderr/returncodeを保持し、成功済み/unknown効果があればpartial6を返す。branchのjournal optionをcontext前にARGUMENT_RETIRED/exit2へ変更し、helpからregistryとresume/rollbackを除いた。Startのcandidate readerは、branch単機能では記録を作らないためtoken/ignore判定を要求しない。Startでは従来通り実tokenを必須で渡している。

別processが実directory flockを保持していてもbranch createが成立した。これはStart-only排他の独立したGreen証拠であり、新機能のRed証拠とは区別する。

実CLIを外部OSのfsync/unlink境界で強制停止する3件も成功した。stageのfile fsync後、最終rename後・directory fsync前、捕捉した旧recordのunlink後にSIGKILLし、JSON未返却・checkout保持・OS lock解放・独自common-dir stateなしを確認した。

- stageだけ残った場合は選択をinvalidとして保全し、新Startは効果0で拒否した。stageを有効な選択として扱わず、自動除去もしない。
- 最終recordが見える場合はactive showでselectedを観測し、既存branchへの新しい明示Startはunchangedとして成立した。
- 旧record解除後ならemptyを観測し、新しい明示Startで直接選択を取得した。旧選択は自動復活しない。

これらはprocess終了と実FS上の可視状態の試験であり、電源断耐久性やWindows native受入を認定するものではない。

| 検証 | 実結果 |
|---|---|
| branch、Start、infra全体、複数WT/native Git/record強制停止、CLI catalog/envelope | 597 passed、1 skipped、52.04秒 |
| 全source/test Ruff check・format check | 成功、363 files formatted |
| 変更した5 sourceの限定mypy | 成功。optionsの既存generic推論不整合も明示型で解消した |
| 実Scope240件/workspace宣言のhash | 変更0 |

P-06と全製品の完了認定は継続中。Windows immutable store/native受入、全体型gate、独立した現在候補のレビュー、P-07以後、最終品質ゲート、手動製品確認は未完了である。

## P-06 第3回Strict指摘の修正

レビュー対象8ad73cfd、GPT-5.6 Sol / Proの元JSONはexit10/fail、P1三件とP2二件。全件分析を記録してからTDDで修正した。現在branchへのcheckoutを省略して無変更とし、checkout後のdirty状態では選択変更へ進まない。候補commitのScope/containerはtreeとして事前確認し、公開不能ではtokenをnullにする。record公開後は自handle一件のvalid selectionを再確認する。追加entryや確認済みGit効果は保全し、rollback/新lock/台帳は追加しない。

公開CLIとOS/Git境界の関連選択は619 passed/1 skipped、52.50秒。対象Ruffと変更3 sourceの限定mypyが成功。詳細Red/Greenと各原文分類はartifacts/code-review-p06-03-analysis.mdへ記録した。再レビューpass、Windows native、全体mypy、P-07以後、最終gate/手動製品確認は未完了。並行して進めたP-07 active接続はこの修正commitから分離する。

## P-07 activeの通常経路

active set/clearをimmutable direct recordの通常dispatchへ接続した。setは同じ妥当なdirectだけunchangedで、空/別対象の取得はWORK_START_REQUIREDとなる。clear --fromは現在のdirect/祖先に一致するとdirect全体を解除し、既知チェーン外はunchanged、不明IDはexit4。親へ昇格しない。clear --allは捕捉した正規basenameとfile/directory identity・exact hashだけを対象とし、未知entry/redirect/stageは削除しない。壊れJSONの本実行には--yesを要求し、dry-runは承認なしで予定効果だけ返す。

外部OS境界で初回selection読取直後に新tokenへ置換するRedを確認し、--fromでは最初のhandleだけを解除するよう修正した。unlink直前に別process相当の解除/新公開を挿入するRedも確認し、旧basename消失はalready_absent/unchanged、新recordは保全する。unlink後fsync失敗はunknown/partial6として、確認済み効果と後の失敗を分ける。期待条件、破損/未知entry、dry-run、旧from-branch/resume/rollbackのcontext前拒否、helpを公開CLIでRed→Greenにした。動的roleの導出と、解除後に親が新選択されないことも確認した。

別processがnative flockを保持していてもclearが成功するGreen証拠を取得した。Start以外の共通排他は追加しない。Git/remote/lifecycleは変更しない。共有data型はpresentation/command_data.pyに置き、applicationからdispatchへの依存を作らない。

新activeの32件を含む関連選択は655 passed/1 skipped、54.66秒。全Ruff check/format（367 files）と変更6 sourceの限定mypyが成功。実Scope240件のhash変更0を確認した。Finish、Windows native/immutable adapter、全体mypy、現在候補の独立再レビュー、最終gate/製品手動確認は未完了。実dogfoodの選択や宣言を変更した証拠とは扱わない。

## P-06 branch switchの無変更分類

第3回レビューのC-04効果分類を同じGit checkout境界にも照合し、branch switchで既にcurrent branch/HEADと固定tipが一致するケースを追加した。修正前は不要なpost-checkout hookを起動しsucceeded/switched=trueだった。fresh physical context・source bytes・candidate・cleanを照合後、checkoutを省略してunchanged/switched=falseを返す。選択の記録は作らない。公開CLIのRed→Greenとbranch関連23件、対象Ruffと限定mypyが成功した。独立再レビューは次の現在SHAで実施する。

## P-07 GitHub-backed Finishの通常経路

GitHub-backedのFinishを通常package dispatchへ接続した。対象/selection handleをremote前に固定し、対象と子孫のlive状態を確認する。GitHub completedの確認後に、自WTの捕捉した対象/配下の正確なbasenameだけを解除し、親を選び直さない。既にcompletedならPATCHせず、Gatewayの最終GETで他actorの完了が見えた場合もunchangedを返す。dry-runは--yes不要、予定効果のみ。offline/期待条件/未完了子孫/unknown/not-plannedは効果前に停止する。

source bytes/identityとworkspace declaration、clone/worktree physical identityを捕捉し、Gatewayの最終GETの後、PATCH直前にも照合する。任意編集を禁止するロックや権限変更は追加しない。GH closeの結果unknownでは選択を保全し、confirmed close後の解除失敗はcompleted=trueとclose/clearの別effectで返す。新しい明示Finishではlive GETをし、完了確認済みなら重複PATCHを行わない。journalのresume/rollbackはcontext前にARGUMENT_RETIREDで拒否する。

native gh fixtureを外部プロセスとして起動し、GET/PATCHとcanonical repository/Issue bindingを検証した。最終GET中のmetadata変更、他actorのremote完了、503によるClose不明、unlink/fsync失敗に対する公開CLIのRed→Greenを確認した。別processが共通directory flockを保持したままでもFinishが成功した。Finishの最初のGET中に別のnative processでclear→Startを実行し、同じScopeの新tokenでも遅い旧token解除が新記録を消さないことを確認した。後二件は設計済み境界のGreen証拠であり、新規Redとは区別する。

拡張選択は229 passed/4 failed（43.10秒）。失敗4件は廃止対象のvnext_runtimeを直接呼び、通常catalogから削除済みのactive set --from-branch属性を参照する旧lifecycle CLIテストだった。旧runtimeのnonblocking inspection parityは現在catalogに合わせたが、廃止経路の復活はしない。P-12で退役module/testと新しい公開CLIの対応を整理する。全suite成功の証拠には扱わない。その後の最終context/metadata再照合を含むFinish/共有Gateway選択は37 passed（7.05秒）。変更した5 sourceの限定mypy、全source/test Ruff check/format（369 files）が成功した。

真正の既存local backend保全互換性はまだ未接続であり、このcheckpointをP-07完了とは扱わない。Windows adapter/native受入、P-08以後、全体mypy/test、現在候補の独立Strict再レビュー、最終品質ゲート、手動製品確認も継続する。実dogfood workspace/Scopeを変更した証拠ではない。

## P-07 既存local backend保全互換性と単一metadata更新

4fc5bd259210501c17e8d24e4332746a6f46ea8eをcommit/pushし、通常のStrict wrapperで第5試行（第4試行はunsupported native optionによる送信前失敗）をGPT-5.6 Sol / Proで開始した。GitHub upstreamとlocalのfull SHA一致、clean branch、固定baseからの非空差分を確認した。以下の変更はそのレビュー対象SHAより後であり、レビュー認定には含めない。

真正の既存local backendのFinishを、schema3の既存lifecycle codecによる保全更新へ接続した。新規local発行、backend変換、Scope ID変更は追加しない。unknown optional field、lifecycle内optional field、既存IDを保持し、revisionとcompletionだけを一fileのatomic replaceで更新する。already completedなら書き換えない。全writer lock/transaction intent/journalは作らず、同FSのignored .agent/stagingに実行中の一時fileだけを作る。実際のstage名がGitでignoredであることを作成前に検査する。

source bytes/identity、writer feature宣言、destination parent identityを公開直前とreadback時に確認する。nofollowのdirectory descriptorから不足するprivate directoryだけを作り、redirectされた.agentの外へstage directoryを作らない。stage名衝突では既存の他fileを削除しない。前提失敗時に自身のstageだけを片付け、rename結果unknownではrollbackせず選択を保持する。fsync/readbackまで確認済みのmetadata更新を、後のdescriptor cleanup例外で未実施へ降格しない。既存modeを保存し、編集を禁止する権限機構は追加しない。

公開CLIでlocal未接続、redirect親への外部stage生成、stage衝突時の他file削除、cleanup後の確認済み効果消失、rename後の親置換、umaskによる元mode喪失のRed→Greenを確認した。更新中の外部metadata編集はoverwriteせず、自stageだけを片付けるGreenも確認した。

Finishの動的selectorと期待selectorは最初のSelectionObservationを共有し、target解決とhandle捕捉で別々のcurrentを読まない。初回観測のstore退出直後に外部OS境界でtokenを入れ替えた場合にも、新tokenを保持するGreenを確認した。この試験とignore試験では初期fixtureの介入位置/ignore位置を訂正したため、初期失敗を製品Redの根拠にはしない。

関連公開CLI、Start/active、共有Gateway、複数WT観測は157 passed（35.62秒）。全source/test Ruff check/format（370 files）、変更3 sourceの限定mypyが成功した。前commitの自動生成bodyの「484件」はtest fileの行数であり、当時のFinishは18 tests、共有Gatewayを含む実測は37 passedである。履歴は書き換えず、実測の正本は本reportとpytest結果とする。

P-07のPOSIX機能検証は進んだが、現在候補の独立レビューとWindows native、P-08以後、全体gate/最終品質ゲート/手動製品確認、実dogfoodの移行は未完了である。元Scope240件や実workspace declarationを手編集して復旧した証拠ではない。

## P-07 第5回Strictの指摘分析と効果表示の修正

GPT-5.6 Sol / Proによる第5試行は、固定対象4fc5bd259210501c17e8d24e4332746a6f46ea8eに対してexit10、review_status=failで完了した。2件のP1と1件のP2を原文JSONのまま保存し、analyze-review-findingsで全件を現在コード/確定契約と照合した。単一selection観測からのFinish target/handle固定はa9e9997で先行修正済みだったが、この後続SHAはレビュー済みとは扱わない。

Closeの結果が不明/拒否、または確認済みClose後・解除前に処理を停止した場合、捕捉したclear handleをnot_attemptedとして表示するよう修正した。初期GETや最終PATCH直前の前提失敗でoperationを開始していない場合はeffects=[]を維持する。503のmissing clear effectを意図したRedとして確認し、422の確定拒否とClose確認後のmetadata変更でも記録保全・completed/effectsが整合した。新しい捕捉handleを採用し直さない。

明示されたIssue全実装/指摘修正の範囲で、非blocking P2の複数record clearもC-04の既存意味へ合わせた。失敗したhandleをfailed/unknown、その後の捕捉済みhandleすべてをnot_attemptedとして返す。適用済み/unknownがない初回失敗はfailed5/3であり、partialへ偽昇格させない。第2 unlinkでの停止と初回unlinkでeffectsが消えるRedを確認した。directory fsyncのunknown、先行unlink直後の外部bytes変更によるconflictでも、残る記録を保全した。capture順を辞書順とした初期fixtureは訂正しており、その仮定を製品保証へ追加しない。

Finish29 testsとactive36 testsが通過し、最終的な関連公開CLI/Start/record store/envelopeの選択は166 passed（35.83秒）。全source/test Ruff check/format（372 files）と変更2 sourceの限定mypyが成功した。並行して進めたP-08の変更は、この修正unitとは分けてcommitする。新しい全writer lock、journal、rollback、Scope ID、未知entry削除、別WT操作を追加していない。

現在候補のfresh Strict pass、Windows adapter/native受入、残る各stage、full gates、最終品質ゲート、手動製品確認、dogfood移行は継続する。実装側の推論レベルは2026-10-01の利用者指示によりGPT-6.1 Sol / Maxへ更新した。独立レビューのGPT-5.6 Sol / Pro指定は維持する。

## P-08 都度観測によるreadonly Sync

`workspace sync`を通常packageのdirect_syncへ接続した。現在treeの未選択Scopeを含む全Scopeと、Git inventoryが示す同clone各WTの直接対象/必要祖先をメモリ内で集計する。他WTの無関係なmetadataはロードしない。各Scopeの直接/子孫選択件数、各WTのselected/empty/invalid等とbranch差、lifecycle、観測時刻をJSON/textへ出力し、process_stateはnot_observedとする。GitHub-backedのlocal sourceはunknown、github sourceはcanonical refを重複排除してlive GETする。選択を完了や実行中processへ読み替えない。

他WTの読取不能、重複選択、Scope IDの異なるGitHub linkage、祖先関係や真正の既存local lifecycleの食い違いは、観測できた行/件数を保全し診断付きpartial/exit7を返す。件数のcomplete=falseを維持し、不明分を0へ補完しない。GitHub取得失敗/未知状態はunknown、effects=[]であり、古いcacheで補完しない。other-WTのGit失敗の元stderr/returncodeはJSON/textにも保持する。現treeの未知metadata schemaは--allow-invalidでも解釈を進めずexit7にする。同期によるmetadata/record/generated projection/controlへの書込はない。

public CLIを使う19件の統合テストで、選択中かつcompletedのAと未選択かつopenのB、同親の並行選択、親の直接/子孫件数、他WTにしかない必要祖先、無関係な壊れmetadataの非読取、GitHub ref dedup、取得失敗、旧cacheの非使用、矛盾、invalid record、native Git原文、text/helpを確認した。実出力をcli-schema.json/FormatCheckerで検証し、scopes欠落・不正lifecycleを拒否した。source cacheは両構文ともcontext前のARGUMENT_RETIRED/exit2へ変更した。schema検査には開発依存のjsonschemaを追加し、製品wheelの実行依存は増やしていない。

関連公開CLI/統合テストとstore/committed-workspace/Gateway/envelopeは262 passed（78.06秒）。この結果は後続のactive clear追加4件より前であり、その後の修正unitでは別途166 passed（35.83秒）を確認した。全source/test Ruff check/format（372 files）とSync/Finish/dispatch/data/envelope/catalog/optionsの7 source限定mypyが成功した。初期fixture/collectionの不備は訂正し製品Redと区別した。既存local矛盾の追加では集計前参照による3件の回帰を検出し、未追加identityのguardを修正した後で拡張選択を成功させた。

このunitはP-08の通常POSIX経路の機能検証であり、独立Strict合格、旧generation module/testの退役、Windows native、full suite/lint、最終品質ゲートや実dogfood移行の証拠ではない。P-09以後を継続する。

## 第6回Strictコードレビューと既存契約内の修正

`e6513650c419e827fba29746f91d8870ee4ab8aa`のP-03〜P-08通常POSIX経路をfresh Strictで再レビューした。configured upstreamとclean HEADのfull SHA一致を検証して開始し、GPT-5.6 Sol / Proで44分09秒後にwrapper exit10、`review_status=fail`となった。P1一件、P2四件の原文をbyte一致で[JSON](artifacts/code-review-p06-06.json)へ残し、全件のauthority・到達性・根本原因・認可・修正・検証を[分析記録](artifacts/code-review-p06-06-analysis.md)へ記録した。

未知/重複fieldのGit inventoryを完全観測にしない行単位診断を追加した。健全なWTはSyncで保持し、不完全行をunavailable/complete=false/exit7とする。Startは同じ不完全inventoryをGit効果前に拒否する。stale/unavailableでも読めた直接ID/refのScope観測とknown件数を保持し、GH modeでは既知refをdeduplicateして今回だけGETする。異なるID/同refもidentity conflictとして両観測を保全する。

`active clear --all`は捕捉recordのclone/worktree physical identity不一致をinvalidの明示確認条件へ含める。stage作成後のStart公開失敗は残存候補を無効果と偽らずpublication unknown/partial6とし、再観測案内を返す。native stage fsync拒否とnative POSIX rename拒否を公開CLIで確認した。stageの自動purge、rollback、resume、中央状態、全writer lock、UUID、編集権限制御は追加していない。

関連回帰の初回は251 passed/1 failed（69.70秒）。失敗は同じ残存stageの旧failed分類を期待する既存testであり、確定C-04へ合わせた訂正後は252 passed（65.38秒）。変更6 sourceの限定mypy、全source/test Ruff check/format（377 files）が成功した。collection指定やfixture fieldの誤りは製品Redから除外する。

P-09作成経路の未コミット作業は別unitとして保持する。この修正はローカル検証済みで、fresh Strict pass、Windows native/store、full lint/test、P-09以後、Final Quality Gateと手動製品確認は未完了。goalをactiveとして継続する。

## P-09 三階層のGitHub-only createを通常経路へ接続

`scope create initiative|epic|issue --backend github`を通常dispatchへ接続した。local新規発行はcontextへ入る前にARGUMENT_RETIRED/exit2、offline発行は効果前拒否とする。既存title/slug・親kind/階層・祖先openの純粋な規則を再利用し、originのcredential-free fetch/push endpointが一つの同じGitHub repositoryであることをnative Gitで検証する。Git lookup失敗の元stderr/returncodeはerror.details.gitへ残す。

必要なlocal metadataとworkspace bytes/identity、repositoryを固定し、GH POST前、応答後、directory公開直前にcooperativeな再照合を行う。GitHub createはoperation markerなしの一回だけ。確定番号#57から三kindの既存形式IDを生成し、同FSのignored `spec-dock/.agent/staging/.stage-<opaque>`でmetadata/文書/rules linkを完成してから、無上書きdirectory公開する。独自allocator、Scope UUID、control、journal、全writer lock、旧engine fallbackは使わない。

POST応答が不明ならscope=null、remote effect unknown、scaffold not_attempted、partial6としてblind retryをしない。確定refの後にmetadata/originが変わった場合やID/refが重複した場合は、確認済みGH refを返してlocal公開を止め、新しい明示importを案内する。local公開後のdescriptor cleanup失敗でも確認済みscaffold成功を失わない。missing template、redirected/unignored stagingはPOST前に停止する。実directory stageの全entryがGit管理外であることを検証した。

実TTYでの計画後確認・承認・取消を確認した。JSON/非対話で--yesがない場合とdry-runはwrite0。leaf helpはGH発行番号とv2結果を説明し、旧local creation/resume/journalの案内を撤去した。公開前stageへnative FIFOを注入するとopenがblockするRedを隔離子processで確認し、特殊entryの事前拒否とnonblocking openで、既知GH refを保ったlocal失敗を返すようにした。

22 creation testsにpublic contract/fresh wheelを合わせた29 testsが13.38秒で通過。対象Ruffと変更6 source限定mypyが成功した。最初の不足実装、POST unknown、既知remote後の変更・重複、hidden stage ignore、cleanup後の効果、repo変更、Git原文、TTY、FIFO、helpのRed→Greenを各公開境界で確認した。三階層の追加は既存pure規則で最初からGreenであり、fixture/collection不備をRedとして数えない。

このcheckpointはcreate縦経路の証拠である。import/edit/close/reopen/dependency、旧writer/helper importの抽出・退役、Windows native、全体gate、最新候補のStrict、Final Quality Gate、手動製品確認は未完了。実dogfood metadataやdeclaration、正式Issue #413の選択は変更していない。

## P-09 GET-only importと編集可能なmetadata

create unitを93b151129bf6e193aaa92605b729d83077fc3514にコミットし、設定済みoriginへ非強制pushした。clean branchとfull SHA一致を確認してfresh Strict r7（GPT-5.6 Sol/Pro）を送信した。r7はこのSHAを固定して実行中である。以下の追加はr7のレビュー対象には含まれない。

通常scope import githubをpublication usecaseへ接続した。完全gh参照、正確なIssue URL、--github-repo付き裸番号を既存parserで正規化し、originとの一致・現在treeのID/ref重複をGET前に確認する。GitHubのGET以外の変更を行わず、確定番号を既存三階層scaffoldへ渡す。remote状態は今回の応答から返し、metadata lifecycle=nullを維持してcacheを作らない。乾式実行はGETと計画のみでlocal write0。廃止resumeはcontext前にARGUMENT_RETIRED/2、helpもv2・明示再importを説明する。

GET中のactor編集を再照合して保全し、既知refとscaffold not_attemptedを返す。remote mutationのないimportを誤ってpartial6にする問題を修正した。公開後に異なるIDの同refが出現する競合は、scaffold succeeded/partial6として両pathを報告し、双方を自動削除しない。scope_treeの重複診断は従来のValueError意味を保つ型へ場所を付加した。

競合fixtureの最初の試行ではコピーしたreadonly metadataへの編集が阻まれ、目的の競合条件に届かなかった。このfixture failureを製品Redから除外して、actorが自身のfileを置換する試行で、場所欠落のRed→Greenを確認した。一方、通常createが旧fs_repoヘルパーからchmodでmetadataをreadonlyにする別の実不具合を発見した。新しい公開metadataを通常のwrite_textで編集できないPermissionErrorを製品Redとして再現し、専用のexclusive writerへ切替えてGreenとした。既存の実consumer filesのmodeは変更していない。

不足dispatch、事前二重登録GET、取得中の入力変化による不正partial、live状態欠落、競合path欠落、metadata編集制限、help、resumeの各focused cycleを確認した。既存純粋規則から継承できたreference形式・offline/foreign/PR/remote未検証の拒否・dry-runは最初からGreenの回帰確認であり、架空のRedを主張しない。作成23/取り込み17/public contract・fresh wheelを合わせた47 testsが18.79秒で通過した。共有tree変更の影響をStart/active/Finish/observation/Syncへ広げ、164 testsが42.02秒で通過した。全source/test Ruff checkとformat（379 files）、変更6 source限定mypy、diff checkも成功した。

close/reopen/dependency、旧moduleへのpure helper依存の抽出・退役、Windows native、全体gate、Final Quality Gate、手動製品確認、正式dogfood切替は未完了である。goalはactiveとして次の縦経路へ進む。

## P-09 close/reopenと第7回Strictの修正

93b151129bf6e193aaa92605b729d83077fc3514を固定したr7は46分11秒後にnative wrapper exit10、validated review_status=failで完了した。P1二件の原文を[JSON](artifacts/code-review-p06-07.json)へbyteを変えず保存し、05f60caeおよび未コミットclose/reopen unitと最新検証を区別して[完全batch分析](artifacts/code-review-p06-07-analysis.md)を記録した。レビューはtestsを実行していない。

Scope close/reopenは必要なtarget・子孫/祖先の今回のGitHub観測から既存pure規則で計画する。completed親の再Closeでも子孫完了を確認し、not-planned Closeは子孫IDを提示してtargetのみ変更する。再開は既にOpenでも祖先Openを要求する。GitHub PATCHは一回と確認GET、真正の既存localは未知metadataを保全してrevision/lifecycle revisionを増やすatomic置換とした。選択record、HEAD、branchを変更しない。部分成功/unknownは効果を保ち、unknown Scope statusへ落として再送しない。localの確認済み公開後cleanup失敗でも新しい状態とsucceeded effectを保持する。JSON・非対話では--yesを要求し、実TTYの計画後確認・取消を検証した。helpはv2へ更新し、旧resumeはcontextに入る前にARGUMENT_RETIRED/exit2で拒否する。

F1はFinishのGit例外を診断へ変換する際のdetails欠落だった。native Git executableで、PATCH直前の複数行stderrがWORK_FINISH_INCOMPLETEへ潰れるRedを確認し、GIT_FAILEDと元stderr/returncodeを返してGreenにした。確認済みClose後の同じGit失敗ではpartial6、completed=true、close succeeded、clear not_attemptedとなり捕捉recordを保全することも確認した。PATCHを再送しない。

F2はScopeのresult projectionの不備だった。create dry-runのcan_apply欠落と、確認済みdirectory公開後cleanup失敗時のscope=nullをRedとして確認した。create/importの有効な乾式計画にcan_apply=true/blockers=[]を返し、確認済み公開後はnamed-targetを安全に再観測してScopeViewを回復する。path・kind・parent・ref・title・revisionを公開時と照合し、不一致ならactorの編集を保全してscope=null、changed=trueと確認済み効果を維持する。close/reopen dry-runも同じ必須fieldのRed→Greenを確認した。全writer lockや台帳、UUID、権限制御、rollbackは追加していない。

作成・取り込み・close/reopen・Finishの公開CLI選択は88 passed（28.76秒）。public contract/fresh wheelの7 testsも6.27秒で通過した。mypyのLiteral不足はtyping-only correctionとして修正した。C-05の同じ乾式result invariantを既存branchにも照合し、can_apply欠落のRedを確認して共通成功projectionへ修正した。branchの23 testsが5.61秒で通過し、最終的な変更7 source限定mypyと全source/testsのRuff check/format（381 files）も成功した。実TTYのfixture配置不備やcollection errorは製品Redに含めない。現在unitの独立Strict pass、dependency、旧moduleの抽出・退役、native Windows、全体lint/test、Final Quality Gate、手動製品確認と実dogfood切替は未完了であり、goalをactiveに保つ。

## P-09 dependencyの通常経路とr8

三階層metadataから宣言/実効edgeを毎回求めるlist/checkと、一metadataだけを置換するadd/removeを接続した。新しいregistry、共有採番、cache、journal、Start lockを利用しない。checkのdefaultをlocalへ変え、GH未観測はunknownのblockerとして返す。明示--source githubは対象・祖先・実効前提だけをGETし、取得不能も元のremote診断とunknownを保つ。offlineで必要なGETは実行前に拒否する。既存の真正localのlifecycleは保全互換性として読み、GHの完了を選択件数で代用しない。

add/removeでは同じ捕捉直接選択からfrom/toとguardを解決し、全metadata bytesとphysical identityを再確認する。自己・祖先/子孫・継承WaitGraph循環を公開前に拒否し、未知fieldと元のfile modeを保つ。変更なしはunchanged、missing-okだけが不存在edgeを許す。確認済み置換後のcleanup失敗はsucceeded effectを保持してpartial6へ、不明な置換はunknown effectと操作前snapshotの明示へ進み、巻戻し/再送をしない。ネイティブfsync/replace境界とPOSIX別processで、並行編集保全とStart排他ロック中の更新を確認した。

query dry-runがparserで拒否されるRedを確認し、readonly previewを許可してC-05のcan_apply/blockersとplannedを返すようにした。listの--viewはtextを宣言/実効へ切り替え、JSONは必須の両配列を維持する。checkのtextはreadyとblockerを表示する。新依存helperのunconnected、不要なGH GET、offline実行、dry-run書込、unknown effect欠落、guard無視、actor競合分類、help/text不足、unignored stage許可を各focused Red→Greenで確認した。既存のgraph/local authority/readonly preview/Start lock非使用の確認はGreenの回帰検証で、架空のRedを数えない。

関連公開CLI/Start/Finish/Sync/observation/store/envelopeの332 testsは76.98秒で通過し、旧dependency/query/helpの24 testsは2.99秒で通過した。初回の旧runtime catalog guard collection errorは、通常経路へ移行済みScope leafを旧inspection表にも反映して解消した。通常dispatchへ旧writerを接続していない。全source/test Ruff check/format（383 files）と変更6 source限定mypyが成功した。

独立Strict r8は29d539254164f0daa814cd8d81e8c67e94ba10a2をGPT-5.6 Sol/Proでレビューし、38m22s、validated exit0/pass、P0/P1なし、P2二件となった。原文JSONをbyte保全し、関連検証完了後の完全batch分析をartifacts/code-review-p06-08-analysis.mdへ保存した。r7のP1修正はr8範囲で合格したが、今回のdependency unitはその後の未レビュー変更である。P2の分類とnon-blockingを保ち、利用者の指摘修正の明示指示に従って次のunitで対応する。P-10以後、旧helperの抽出・退役、native Windows、全体lint/test、Final Quality Gate、手動製品確認、実dogfood切替は未完了であり、goalはactiveである。

## r8のP2を明示認可されたTDDで修正

Startが切替前の同じtokenを捕捉し、Git checkout後のunlink直前に別processのactive clear --fromが削除するケースを公開境界で再現した。修正前は既に安全に解除済みでもselection.clear=failed、SELECTION_CHANGED/partial6で停止した。already_absentをunchangedとして扱い、conflictだけを拒否する最小変更により、後続の空状態・物理identity・HEAD・metadata・inventoryの再検査とsole new record公開まで完了した。scope_id/tokenの対象固定、変更recordの拒否、Start lockの範囲、rollback禁止は変わらない。

全44leafのproject不要helpを検査し、catalog defaultのv1表示をRedとして確認した。default一箇所をspecdock.cli/v2へ合わせ、実envelopeとhelpの表示を一致させた。未接続の業務leafの完成を示す変更ではない。二件ともreview-native P2とr8 passを保ち、レビュー自体ではなく利用者の指摘修正の既存明示指示から認可を得ている。

関連175 tests（36.78秒）、全Ruff check/format（383 files）、変更2 source限定mypyとdiff checkが通過した。fixtureのbranch/selected_branch誤記は製品のRedに含めない。dependency unit d76d34c01079b8bfa420658c750ec713f8251cadと合わせた現在候補を次のfresh Strictへ進める。P-10以後、旧writer/helper退役、native Windows、全体gate、Final Quality Gateと手動製品確認、実consumer切替は未完了であり、goalをactiveに維持する。

## P-10 Scope editを通常経路へ接続

3c68053e36f3476ab843b0f4e339b24c2d490e68までのP-02〜P-09とr8修正を非強制pushし、clean・設定済みsecure upstream・local/upstream/remote full SHA一致を検証して、独立Strict r9（GPT-5.6 Sol / Pro）を送信した。r9はこの固定候補で実行中であり、以下のScope editはレビュー範囲に含まれない。主実装の推論設定は利用者の最新指定によりGPT-6.1 Sol / Max、外部レビューモデルは従来指定を維持する。

Scope editはtitleのtrimと非空検査、同じ捕捉選択からのdynamic selector/guard解決、現在treeの入力bytes・identityと物理Git contextの再検査を行う。一つのmetadataのtitle/revisionだけをignored同FS stagingから置換し、ID/slug/path/backend、未知field、本文、既存mode、真正の既存local lifecycleを保全する。GH通信、選択更新、Start lock、control、共有状態、journal、編集権限制御を追加しない。無変更のtitleはstageなしで元のbytes/revision/inodeを維持し、有効dry-runは候補ScopeViewとcan_apply/blockersを返す。

未接続dispatch、dry-runの実書込、無変更のrevision更新、guard無視、確認済み公開後cleanup失敗の効果欠落、helpの旧cache/journal案内をfocused Red→Greenで修正した。置換が実行されて応答だけ失敗するネイティブos.replace境界ではpartial6/unknown、scope=null、変更済みと推定せず再送しない。fsync中のactor編集は置換前に検出して保全する。公開後のネイティブGit失敗は元の複数行stderr/returncodeとmetadata succeededを保持し、partial6を返す。POSIX別processでStart排他が保持されている間にも編集が完了することを確認した。

redirected stagingのtestは初めexit3を期待したが、実際のGit check-ignoreがsymlink先を原文stderrで拒否し、exit5/effects=[]/外部file・metadata不変を既に満たしていた。C-04に合わせた期待値訂正であり製品Redとして扱わない。真正の既存local、並行編集、Start lock非使用、置換不明の確認も初回Greenの回帰証拠である。存在しないtest fileを指定したcollection失敗は検証実績へ含めない。

関連124 tests（24.83秒）、全source/test Ruff check/format（385 files）、変更4 source限定mypyとdiff checkが通過した。Scope editのfresh Strict、P-10の残りfamily、P-11以後、旧writer/helper退役、native Windows、全体lint/test、Final Quality Gate、手動製品確認、正式dogfood切替は未完了である。実consumer metadata・workspace宣言・選択を変更せず、goalをactiveとして次のdelete縦経路へ進む。

## 第9回Strictの全三件を修正

3c68053e36f3476ab843b0f4e339b24c2d490e68を固定したr9は36m35sでnative exit10、review_status=fail（P1一件、P2二件）となった。実際の表示はGPT-5.6 Sol / Thinking time Pro。原文をbyte保全し、全件のauthority・最初の誤り・修正route・認可を[分析記録](artifacts/code-review-p06-09-analysis.md)へ残してから修正した。Scope editのde47237fと未コミットdeleteはこのレビューへ含まれない。

F1ではScope create/importが受け取ったexpect-current/backendを無視するRedを四ケースで確認した。現在treeと直接recordを一度捕捉し、既存canonical selectorで直接IDを比較、新規Scope backendはgithubと比較して、remote GET/POSTやstageより前に拒否する。dynamic parentも同じ捕捉選択を使う。合法なguard・dynamic parentを三階層/create・importの六ケースで確認し、選択bytesを保全した。

F2では成功するnative post-checkout hookによるtracked/untrackedの変更が、dirtyのままswitched=true/exit0になるRedを確認した。通常checkout成功後にもstatusを検査し、dirtyならCHECKOUT_VERIFICATION_FAILED/partial6へ進む。確認済みgit.checkout=succeededを保持し、branch、HEAD、hookの変更、選択recordを巻き戻さない。新testへ誤って継承された既存assertionのfixture配置を修正した失敗は、製品Redとして数えない。

F3ではmain/linkedの両方のScope資料が消えた場合、stale二行と件数2だけを返して重複findingが欠落するRedを確認した。既知recordのselected/stale/unavailable集合を重複診断にも使い、既存の状態findingとSELECTION_DUPLICATEを併記する。linked metadataが壊れても安全にdecode済みのrecordを保持し、invalidなrecordは件数・重複へ昇格させない。effects=[]、全record bytes不変、共通stateやcacheなしを確認した。

関連Scope発行・branch・Syncの83 testsが25.02秒で通過し、変更3 source限定mypy、変更6 fileのRuff check/formatが成功した。P2の元の分類とnon-blockingを保ち、利用者の全指摘修正指示に従った。fresh Strict pass、P-10以後、旧runtimeの退役、native Windows、全体gate、Final Quality Gate、手動製品確認、実consumer切替は未完了である。

## P-10 Scope deleteの実体保全と局所効果

r9の全三件の修正と原文・分析・検証記録を7ae4ebccedbda067a7e47ad1574072338b1fb5feへ保存した。親de47237f、branchとGit identityの維持、indexが空であることを確認した。その後、未完了だったScope delete unitを仕上げた。

明示したtargetと現在の直接recordを一度捕捉し、recursive、incoming依存のdetach、現在WTの選択解除、共通expect guardを検査する。不正・読取不能recordをemptyとみなさない。新しい--backup-dir ABSへ対象subtree、変更する参照元metadata、解除する捕捉recordの実体を保存する。source bytes・identity・tree内容とbackup内容を確認してから参照元metadata→捕捉token解除→subtree削除へ進み、GitHub Closeやbranch削除、別WTへの変更は行わない。metadataの未知fieldとmodeを維持し、Start共通lock・control・台帳・journal・権限制御や自動巻戻しを追加しない。

backupのpathをリンクを解決せず正規化し、.gitと削除対象の重複、既存path、redirected parentを拒否する。held directory descriptorから無上書きコピーし、本文・ignored成果物・mode・link文字列を保全する。リンク先の実体へ書き込まない。根拠のあるバックアップ確認後だけ業務変更を行う。sourceやbackupのredirect、途中の書込・mkdirの応答不明では実体を残し、backup unknownと後続not_attemptedを返す。

削除は捕捉したentryの集合とidentity/contentのstatを照合しながら、held descriptorでfile単位に進める。backup後に追加・変更されたfileを保全し、すでに削除したpathを失わず、remaining_pathsと各effectを返す。確認済みmetadata置換、captured clear、subtree削除後のcleanup/Git失敗もpartial6へ保持する。不明な置換・unlinkを成功と推定せず、再送・復元をしない。Git stderrとreturncodeは元の複数行を返す。全treeのserializable transactionや任意の外部writerに対するatomic CASを新しく保証する実装ではない。

実TTYで計画表示後の承認・取消を確認した。JSON/非対話は--yesを要求し、dry-runはbackup・stage・metadata・recordを変更せず、dependency editとclearを含む全予定効果とcan_apply/blockersを返す。redirected stagingはnative Gitが元の診断で拒否する。helpはv2のdeletion fieldと実backupを説明し、旧resume/rollbackはproject解決前にARGUMENT_RETIRED/2で拒否する。

公開CLIとnative mkdir/open/fsync/replace/unlink/listdir/close/Git境界を使い、制御なし通常削除、再帰・guard・incoming・選択条件、backup unknown、確認済み効果とcleanup、並行入力変更・新file保全をRed→Greenで検証した。POSIX実端末、モード/link保全、FIFOの非block拒否、別processでStart flock保持中の削除、同clone別WTの記録保全とcheckout後stale、古いtokenが既に解除された後の新token保全も確認した。既存保存原語から最初にGreenだったケースを、架空のRedへ数えない。FDコピー変更に合わせたfault fixtureのnative IO境界変更も、製品Redと区別する。

関連160 tests（26.86秒）、全source/testsのRuff check/format（389 files）、変更6 source限定mypyとdiff checkが成功した。初回の関連test collectionは旧vnext inspection表に新しい非journal deleteの行がなかったため失敗した。その表を補正し再実行した結果であり、旧writerを通常dispatchへ戻していない。全体mypy、native Windows、fresh Strict、Artifact/Workbench/worktree/bootstrap、P-11以後、Final Quality Gate、手動製品確認、実consumer切替は未完了。実dogfoodのmetadata、workspace宣言、直接選択は変更していない。


## P-10 Artifactを通常経路へ接続

Scope deleteを3e300afaa3b286074139f3b6ccc6a2494ca7c691へコミットし、親7ae4ebcc、branch、Git identityと空indexを確認した。通常push後にclean・secure upstream・local/upstreamと二回のremote full SHA一致を検証し、GPT-5.6 Sol / Pro指定のfresh Strict r10を送信した。以下のArtifact unitはその固定範囲に含まれない。

Artifact list/show/create/import fileをdirect_artifactから通常dispatchへ接続した。所有者の現存ファイルだけから従来のtimestamp/suffixを選び、六creation type、既存Markdown・generic・sequentialのfilename、未知evidence、opaque bytesとbasename、既存custom templateのScope/GitHub置換tokenを保つ。root createは従来どおり拒否し、rootのimport/list/showは無関係なScope metadataを必要としない。dynamic ownerとexpect guardは捕捉した同じ直接選択で解決し、そのrecordを書き換えない。

完成した実候補bytesを同directoryの排他的stageへ書き、捕捉入力、stageのbytes・identity、directory bindingを検査して無上書きlinkで公開する。deterministicなslot名は候補file自身の一時名であり、共有採番台帳、予約marker、journal、counterや共通writer lockではない。並行する同slot・異なるslug/typeの候補は副作用なしの競合として止まり、勝手に別番号で再送しない。失敗した候補の不明な実体を自動回収せず、確認できた公開済みfileを巻き戻さない。

一覧はheld directory FDから安全に列挙し、本文・hash・外部source pathを開示しない。symlink、hardlink、directory、FIFOのsource、unsafe destination、stageの置換を拒否する。root importでもworkspace宣言・物理Git identityを再確認する。確認済み公開後のnative Git失敗は元の複数行stderr/returncodeとartifact succeededを保持してpartial6、linkの応答不明はunknown、mkdirの応答不明はdirectory unknownと後続not_attempted、確認済み公開後のdescriptor cleanup失敗はsucceededを返す。Start共通flockが別processで保持されていてもArtifact作成が完了することを確認した。

未接続の公開leaf、custom token欠落、無関係なScope破損へのroot依存、公開後Git失敗の欠落、置換されたstageの誤公開、catalog列挙中の外部alias開示、mkdir結果不明、help契約不足をfocused Red→Greenで確認した。六type・採番・候補衝突・dry-run・source safety・unknown link等の最初からGreenだった回帰も区別した。ADRのtemplate fieldとcleanup faultの注入位置に対する初回の誤ったfixture期待は修正し、製品Redへ数えない。

Artifact全体と関連contract/fresh wheel/helpの227 passed/1 skipped（14.12秒）、source/testsのRuff check/format（392 files）、変更7 source限定mypyが通過した。追加でrepository全体にRuffを向けたところ、CI対象外の既存.github/scripts二fileにimport/formatの問題があった。無関係なfileを変更せず、source/testsの通常対象と区別した。全体mypy、native Windows、Workbench/worktree/bootstrap、P-11以後、fresh Strict・Final Quality Gate・手動製品確認・実consumer切替は未完了である。実dogfood metadata・宣言・選択を変更していない。

コミット前の差分点検で、このArtifact unitが使わない将来の置換分岐をfile_publicationから除き、無上書き公開だけに限定した。その後の公開Artifact全30ケースが4.50秒で通過した。置換が必要なWorkbenchは次の独立したRedから実装する。

## 第10回Strictの二件を修正

固定候補3e300afaa3b286074139f3b6ccc6a2494ca7c691のr10が43分34秒、GPT-5.6 Sol / Proのverified browser経路で完了した。wrapper exit10、P1一件/P3一件、review_status=fail。原文JSONをbyte保全し、SHA-256 `922aa2ef0b62a0f75253d8dc71b80634898c80c7ecf7f42895ea1c3ce872112e` と[全件分析](artifacts/code-review-p06-10-analysis.md)を記録した。Artifact 35068763753bed493f7a8fb608bbd6726581d4f1と進行中Workbenchはこの固定gateへ含まれない。

F1のcheckout成功hookによるignored direct recordの削除・basename置換・同一inodeのbytes変更を公開CLI/実GitでRedとして確認した。Git前にStoredSelectionとhash/identity付きhandleを一度捕捉し、dynamic target/expect guard、Git前後/no-op/native failureを同じ観測に結び付ける。branch createのreference-transaction hookでも同じ不変条件違反をRedにして照合を追加した。空からのhook選択、観測不能記録の変更前停止、古い成功・no-op・dirty・原文Gitエラーを回帰確認した。直接状態を新規作成/編集/復元する処理、Start共通lock、権限制御、hook無効化を追加しない。

非zeroのcheckout hookが記録を消した場合は、実際のcheckout=succeeded、switched=false、partial6、GIT_FAILEDと元のstderr/returncodeを保持し、追加のverification_errorで直接状態の差異を説明する。hookがexit17でも実Git checkoutのnative returncodeは1だったため、新testの期待を実測した1へ訂正した。このnative値の仮定誤りを製品Redとして数えない。git.checkout効果の成立と操作全体の成功を混同せず、hookが残した記録/checkoutを巻き戻さない。

F2のP3は通常Scope list/show helpへ残ったcached stateの誤説明をRedとして確認し、current metadata・dynamic selector用の当該記録・未観測GitHub stateはunknownという現行契約へ限定した。元のP3とnon-blockingを変更せず、利用者の全指摘修正の明示認可を適用した。通常readのネットワーク・保存・状態authorityを変更していない。

branch/contract/観測/active/Start/store/helpの関連171 tests（35.84秒）、変更5 fileのRuff check/format、変更3 source限定mypy、diff checkが通過した。全source/testsの再認定や全体mypy、native Windows、fresh Strict、P-10残り、P-11以後、Final Quality Gate、手動製品確認、実consumer切替は未完了。Workbenchの進行中変更はこの修正コミットに含めない。

## P-10 Workbenchの同cloneコピーを通常経路へ接続

`workbench copy --scope TARGET --to-worktree ABS` をexternal runtimeへ接続した。main/linkedのnative Git inventoryと物理clone/WT identityで明示先を確認し、既存ScopeのID/kind/parent/backend kind/正規化GitHub refが同じであることを検査する。台帳・wt alias・採番・新Scope IDを作らない。無関係なprunable WTが消えていても、明示コピー先の確認にはその実体を要求しない。

source treeは実file bytes/mode、relative link文字列、空directoryまでメモリで捕捉する。destinationはsourceに対応するpathとその実directoryだけをno-followで観測し、destination-only evidenceは列挙対象外として保持する。errorは全衝突を最初に拒否し、overwriteは変更pathを提示して確認する。fileは実候補の同directory stageから無上書きlinkまたはatomic replaceで公開し、relative linkはdereferenceせず文字列を公開する。source modeは自分のprivate candidateに設定し、既存sourceや成果物の編集権限を管理しない。directoryはexclusive作成し、捕捉したmetadata/context/source/destinationを各段階で再確認する。

適用済みpath、結果不明path、未実施pathをeffectsとcopied_paths/remaining_pathsに分ける。mkdir/link/replaceの結果不明はpartial6として現状と候補を保全し、確認済み公開後のGit失敗は原文stderr/native codeとsucceeded効果を保持する。foreign stageやpathを削除せず、共通Start排他・全writer lock・journal・retry・全体rollbackを加えていない。dry-runは同じ差分を予定効果として返し、destinationやstageを作らない。

通常入口未接続、conflict/overwrite、nested/empty directory、mode、linkとregular file間の置換、unknown mkdir、絶対pathの構文、dry-run予定directoryとhelp/旧option分類を、各focused Red→Greenで確認した。同一GitHub linkageの大小文字差と無関係なmissing WTでの不要な停止も、実Gitの公開入口Red→Greenで解消した。初回のbackend fixture構造の誤り、link rootの安全なnative exit5をexit3と仮定した期待、存在しない関連test名でのcollection failureは製品Redに含めない。

元からGreenの回帰として、実TTYのyes/no、dynamic scope/guardと直接recordのbyte保全、foreign stage置換、destination-only opaque/FIFOの保全、source変更、atomic replacementの結果不明、native Git原文、別processで共通Start排他を保持中のcopyを確認した。既存CLI regressionのto-worktree aliasだけをC-05の絶対pathへ改め、preview/conflict/overwriteの検査を残した。旧application helper自体はP-12で別途退役し、通常のfallbackには接続していない。

関連検証コマンド `uv run pytest tests/cli_runtime/test_issue413_workbench.py tests/cli_runtime/test_issue413_artifact.py tests/cli_runtime/test_workbench_vnext.py tests/cli_runtime/test_artifact_vnext.py tests/cli_runtime/test_issue413_contract.py tests/cli_runtime/test_help_completion_vnext.py tests/integration/test_issue413_wheel.py tests/unit/infra/test_runtime_fs_repo_workbench_opacity.py tests/unit/infra/test_runtime_fs_cli_workbench.py tests/unit/infra/test_runtime_resolver_workbench_opacity.py -q` は153 passed（27.36秒）。`uv run ruff check src tests` と `uv run ruff format --check src tests`（396 files）、変更7 sourceの `uv run mypy --follow-imports=silent ...`、`git diff --check` が成功した。限定型検査は全体gateの代替ではない。native Windows、worktree/bootstrap、P-11以後、fresh Strict、Final Quality Gate、手動製品確認、実consumer切替を継続する。実dogfood metadata・workspace宣言・直接選択は変更していない。

## P-10 native Worktree create/list/showを接続

`worktree create NAME --base REF [--root ABS]`、`worktree list`、`worktree show ABS`を通常external runtimeへ接続した。main/linkedのnative Git inventoryを同じcloneで観測し、Scope metadataや旧controlへの不要な依存を外す。配置は明示`--root`、既存`SPEC_DOCK_WORKTREE_ROOT`の順で、明示empty値を環境設定で置き換えない。NAMEから`root/NAME`と`worktree/NAME`を作り、baseをcommitへ固定する。bootstrapやScope開始を自動実行しない。

公開CLIで未接続経路、NAME/path/recover syntax、dry-runのwrite、環境root、dirty source、Git登録が残る消失path、結果不明なmkdir、nested root、expect guard、empty root、旧controlを案内するhelpのRed→Greenを確認した。native Git hookによるselection/ref変更、hook失敗の確認済みeffect、hookが残すdirty tree、actorが作ったtarget path、別cloneの直接record、fsync中の配置parent置換でもRed→Greenを確認した。sourceのselection/branch/HEAD/workspaceとphysical identityを再照合し、確認済み/unknown/未実施をpartial 6に残す。元Gitのstderr/returncodeを保持し、自動巻戻ししない。

元からGreenの回帰はmain/linked両方からのlocked/detached/prunable表示、workspaceのないtarget、別clone/subdirectory/symlinkの拒否、既知EEXISTでactor directoryを自分のunknown effectと呼ばないことを確認した。配置directoryのhandleを同期中も保持し、置換後のactor領域へ次のdirectoryを作らない。guardを省略したqueryは無関係なScope metadataを走査せず、指定時は同じ自WTの直接対象をcanonical selectorで照合する。対象Scopeのない`--expect-backend`は副作用前に拒否する。台帳・receipt・共有Start lock・権限制御は追加していない。

`uv run pytest tests/cli_runtime/test_issue413_worktree.py tests/cli_runtime/test_issue413_contract.py tests/cli_runtime/test_help_completion_vnext.py tests/integration/test_issue413_wheel.py -q` は52 passed（14.16秒）。旧createの六testsは4.10秒で成功。旧parserのrecover成功assertionはC-02/C-05の退役拒否と明示NAME/base/rootへ変更し、legacy helperの退役はP-12へ残す。Ruff check/format（398 files）、変更四source限定mypyが成功した。dict invarianceを明示型で修正した。expect-current testの不存在Epic fixtureは補正し、fixture誤りのexit 4を製品Redと混同していない。

第11回Strictはこのnative unit前の`8c59994c`を対象にpass/P0-P1なし/P2五件で終了した。原文と完全batch分析を別artifactで保全し、利用者の指摘修正指示に従って次のunitで対応する。このcommitはそのcode修正を含めない。worktree remove/bootstrap、P-11以後、native Windows、full-suite/type gate、fresh Strict、Final Quality Gate、手動製品確認、実consumer切替は未完了。実dogfood metadata・宣言・直接選択を変更せず、goalはactiveである。

## 第11回Strictの五件を修正

原文のpass/P2/non-blocking分類を保ち、[完全batch分析](artifacts/code-review-p06-11-analysis.md)を完了してから、利用者の全指摘修正指示を適用した。review単独を修正認可にせず、現在候補のfresh Strictを別に実施する。

root Artifact createは六typeの実作成・dry-runに接続し、root ownerを既存catalogから解決する。Scope専用の旧template置換文字列は空にし、root ScopeやUUIDを作らない。六typeの12 casesとroot旧置換の一case、Workbenchの同一bytes・異なるregular-file modeの四casesをRed→Greenで確認した。既存Scope置換の回帰も含むroot作成関連14 casesが成功した。error policyはmode差でも副作用前拒否、overwriteはsource modeで公開、dry-runは変更せず予定差分を示す。これは既存fileの編集権限を管理する仕組みではない。

読取用expect guardをstateless helperに接続し、branch show、Scope show/list、dependency list/check、Artifact list/show、active show、Syncで受理した条件を無視しない。dynamic targetとguardは同じ捕捉選択から解決し、canonical GitHub selector、不一致、empty/stale、root ownerを22公開CLI casesで確認した。対象Scopeのないbackend guardは明示拒否し、dependency/Syncの条件不一致ではGitHub GET前に停止する。新しいlock、record、cache、global CASは追加していない。

Artifact importのsource readは、外部pathや本文を診断に開示せず、不存在をexit4、環境IOをexit5、unsafe inputをexit3へ分類する。missing/native permission/EIOの三casesをRed→Greenで確認し、symlink/hardlink/directory/FIFOを含む七casesで回帰確認した。部分適用後の既存partial/unknown規則を変更しない。

補完は同じcatalogのcommand depthとoption arityからcommand componentだけを抽出する。common optionのprefix/suffix/inline値、leaf operand、値を待つoption、double-dash後のoperand、flag、未知prefixをBash/Zsh実processで確認し、公開help/completion全26 casesが成功した。Fishの同じ生成経路も変更したが、この環境にnative Fishはなく、実shellでの検証済みとは扱わない。CLI utilityはGit/通信/状態書込を行わない。Artifact helpもScopeまたはroot ownerの契約へ同期した。

関連検証 `uv run pytest tests/cli_runtime/test_issue413_branch.py tests/cli_runtime/test_issue413_artifact.py tests/cli_runtime/test_issue413_dependency.py tests/cli_runtime/test_issue413_query_guards.py tests/cli_runtime/test_issue413_active.py tests/cli_runtime/test_issue413_workbench.py tests/cli_runtime/test_issue413_worktree.py tests/cli_runtime/test_issue413_contract.py tests/cli_runtime/test_scope_query_vnext.py tests/cli_runtime/test_artifact_vnext.py tests/cli_runtime/test_workbench_vnext.py tests/cli_runtime/test_dependency_vnext.py tests/cli_runtime/test_help_completion_vnext.py tests/integration/test_issue413_sync.py tests/integration/test_issue413_wheel.py -q` は344 passed（63.50秒）。全source/testsのRuff check/format（400 files）、変更9 source限定mypy、diff checkが成功した。Scope listのfixtureに既存Epicが四件目としてあることをassertionへ反映した修正を、製品Redに数えない。

本unitは実dogfoodのmetadata・workspace宣言・直接選択を変更していない。native Worktree create/list/showと本修正を含むfresh Strict、remove/bootstrap、P-11以後、native Windows、full-suite/type gate、最終gate、手動製品確認、実consumer切替は引き続き未完了。goalはactiveである。

## P-10 native Worktree removeを接続

`worktree remove ABS [--unlock] [--discard-ignored] --yes`を通常external runtimeへ接続した。Gitの現行inventoryと同じ物理cloneを参照し、main/current/bareの削除とtracked/untracked dirtyを拒否する。locked targetは明示unlock、ignored内容は明示discardと確認を要求する。dry-runでは同じ条件を読み取り、予定効果だけを返す。branchは残し、ignoredな外部向けsymlinkを含む対象を削除しても外部fileの内容を変更しない。

sourceのworkspace/branch/HEAD/物理identityと一度捕捉した直接選択を再確認し、targetのdirectory handleを操作中保持する。native branch/HEAD/flagsとdirty/ignored条件もunlock前・remove前・dry-runに再確認する。unlock後に新しいuntracked/ignored内容、別branch、同pathの別directory、sourceの選択変更が現れた場合はactorの変更を保全して後続削除を止める。権限制御、registry、receipt、Start共通lock、force、branch削除、自動巻戻しは追加していない。

公開CLIの未接続経路と、処理中のignored追加・同path置換・unlock前のbranch変更・実unlock後にネイティブエラーを返すケース・削除確認後のhandle close失敗をfocused Red→Greenで確認した。実unlockと実removeの確認にはnative inventoryを使い、removeはpath消失も確認する。exit zeroだけで成功と呼ばず、Gitエラー後でも確認できた効果はsucceededとしてpartial6へ残す。timeout/signalはunknown、process開始不能はfailed、後続はnot_attemptedとし、原文stderr/stdout/returncodeを保持する。textでもGitの複数行エラーを保つ。process faultや元から通る安全guardの回帰を、架空のRedとして数えない。

`uv run pytest tests/cli_runtime/test_issue413_worktree_remove.py tests/cli_runtime/test_issue413_worktree.py tests/cli_runtime/test_issue413_contract.py tests/cli_runtime/test_help_completion_vnext.py tests/integration/test_issue413_wheel.py -q` は119 passed（24.90秒）。`uv run ruff check src tests`、`uv run ruff format --check src tests`（401 files）、変更三source限定のmypy、`git diff --check`が成功した。限定型検査は全体gateの代替ではない。bootstrap、native Windows、P-11以後、full-suite/type gate、fresh Strict、Final Quality Gate、手動製品確認、実consumer切替は未完了である。実dogfood metadata・宣言・直接選択は変更していない。

fresh Strict準備の通常非force pushは自動承認審査で二回、process開始前に拒否された。HEAD `9b829ec6d3ebf75cbd0667321b670e7a2781c895`とupstream/remote `8c59994c8dad473697dcd8314721aeeef3f52d79`の差は既知のローカル二commitで、remote変更は実行されていない。AGENTS.mdのremote操作の明示認可要件について、このIssue/branchのレビュー用push許可を利用者へ質問中である。Strict skillの一般的なpreapproval文は審査で認可根拠として認められなかった。回答前にpushを再試行せず、SHA一致を満たさないStrictを実行しない。既存の実装認可に基づくローカル作業は継続し、goalをactiveに保つ。

## P-10 native Worktree bootstrapを接続

`worktree bootstrap ABS --yes`を通常external runtimeへ接続した。同cloneのnative Git targetでproject-owned `make init`を一回実行し、main/currentやworkspace宣言のない初期化対象も扱う。bareとunsafe pathは拒否する。実実行の確認がない場合とoffline applyは副作用前に停止し、dry-runはmakeの構文を評価しない。makefileはGNUmakefile/makefile/Makefileの優先順位で、安全なregular fileだけを捕捉し、必要bytes/identityとsourceのGit context・一度捕捉した直接選択を実行前に再確認する。途中で変わった内容や選択を復元しない。

任意hookのstdout/stderrは保持・開示せず、継承MAKEFILES/MAKEFLAGS/GNUMAKEFLAGS/MFLAGS/MAKELEVELとGit context overrideを渡さない。process起動不能はfailed/exit5、開始後の非zero/signal/timeoutはunknown/partial6としてprojectの現物確認へ渡す。makeが完了した後のtarget置換とhandle cleanup失敗は、実行済みのsucceeded効果を維持してpartial6にする。POSIXではtimeout後に子process groupを停止し、途中で作られたfileを残す。receipt、recover、共有Start lock、権限制御、rollback、暗黙再実行を加えていない。非POSIXのprocess adapterは未接続で、Windows対応を実装済みとしない。

未接続dispatch、project makefile欠落、継承追加makefile注入、捕捉後の直接選択変更、実行後のtarget置換、確認済み実行後のclose失敗、実行前のmakefile変更、process停止のIOエラーでstarted効果が失われるケースをfocused Red→Greenで確認した。元からGreenの回帰として、実dry-run/offline/no確認でmake呼出し0、native timeout後の子process停止、任意hook出力の非公開、新しい明示依頼だけで二回目の実行、main/current/target宣言なし、canonical guard、native signal、process開始不能、別processがStart排他を保持する間の実行を確認した。初回Greenを架空のRedとして記録しない。

`uv run pytest tests/cli_runtime/test_issue413_worktree_bootstrap.py tests/cli_runtime/test_issue413_worktree_remove.py tests/cli_runtime/test_issue413_worktree.py tests/cli_runtime/test_issue413_contract.py tests/cli_runtime/test_help_completion_vnext.py tests/cli_runtime/test_worktree_bootstrap_vnext.py tests/cli_runtime/test_worktree_remove_vnext.py tests/cli_runtime/test_worktree_create_vnext.py tests/integration/test_issue413_wheel.py -q` は168 passed（44.82秒）。全source/testsのRuff check/format（404 files）、変更四source限定mypyとdiff checkが成功した。旧bootstrapのCLI recovery assertionだけを退役拒否/絶対pathへ更新し、旧helperとreceiptはP-12で別に退役させる。設計D-14の実装推論設定も利用者の最新指定Maxへ同期した。

native Windowsのprocess/file adaptersと実OS確認、fresh Strict、P-11以後、full-suite/type gate、Final Quality Gate、手動製品確認、実consumer切替は未完了。実dogfood metadata・workspace宣言・直接選択は変更していない。レビュー用pushの明示許可への回答を待ちながらローカル作業を継続し、goalをactiveに保つ。

## P-11 control非依存の通常/raw/legacy Doctorを接続

通常 `workspace doctor` をexternal runtimeへ接続し、現在のScope構造・依存・Artifact・直接選択を読み取る。共通controlやgeneration cacheを要求せず、構造不良や不完全な選択をeffects=[]の診断不完全/exit7で返す。依存snapshotのpure readerを独立moduleへ抽出し、通常dependency操作から旧writer moduleへのimportを除いた。旧helperの互換性は残し、P-12の退役を完了したとは扱わない。

`--raw`はGit-only contextから入り、通常の既知schema/protocol admissionと分離した。未知・不在・不正workspaceでも安全なentry type/size/schema情報まで表示し、通常writerの制約を迂回しない。JSON重複memberと非JSON constantを拒否し、任意bodyを出力しない。`--expect-current`は検証できる現在の対象だけを比較し、未知workspaceでは検証不能として停止する。解決対象のないbackend guardを無視しない。

`--legacy`だけが旧engine/control/registry/active、通常operation、migration、installation group、finalization、engine handoverのfileを読む。single-link regular file・安全なancestor・読取前後のidentity/content属性を確認し、1 MiB/fileと4096 entries/directoryの上限を設けた。symlink/hardlink/directory/FIFO、未知schema、破損JSON、欠落journal、未確定効果、移行やinstallationの途中を別に分類する。headerのshapeを読めたことをremoteや所有状態の確認と混同せず、unverifiedへ明示する。旧実行物の起動、復旧、phase移植、再送、旧activeの自動採用、control修復、Start lock、権限制御、state writeを行わない。分類後は旧bodyを保持せずschema情報だけを残す。

既存GitHub PR capability optionsも通常/raw双方へ接続した。repository/PR/headの全指定と形式を副作用前に検査し、offline probeを拒否する。repository名・PR番号・HEADの応答を固定要求と照合し、異なるHEADを成功として表示しない。明示probeは有限timeoutでread-only `gh` commandsを実行し、stderrは分類/hashだけを残す。今回実試験はhermeticなnative executable stubで行い、実GitHubへのprobeや業務書込はしていない。

raw flags未接続のexit2、旧pending操作を無視したexit0、GitHub指定不備を無視したexit0、構造不良のexit3/未検査、重複JSONの誤った既知判定、固定HEAD不一致の誤成功、既知schemaだけの不完全headerの誤成功、migration/installation途中記録の見落としをfocused Red→Greenで確認した。元からGreenのunsafe file・秘密body非公開・old active非採用・native probe failure/timeoutも回帰として記録する。fixture path、patch配置、外部processの起動まで待てない実験timeoutの訂正を製品Redに数えない。

検証 `uv run pytest tests/cli_runtime/test_issue413_workspace_doctor.py tests/cli_runtime/test_workspace_doctor_vnext.py tests/cli_runtime/test_issue413_contract.py tests/cli_runtime/test_help_completion_vnext.py tests/cli_runtime/test_issue413_work_start.py tests/cli_runtime/test_issue413_active.py tests/cli_runtime/test_issue413_finish.py tests/cli_runtime/test_issue413_dependency.py tests/cli_runtime/test_dependency_vnext.py tests/cli_runtime/test_issue413_worktree.py tests/cli_runtime/test_issue413_worktree_remove.py tests/cli_runtime/test_issue413_worktree_bootstrap.py tests/integration/test_issue413_observation.py tests/integration/test_issue413_sync.py tests/integration/test_issue413_wheel.py tests/unit/infra/test_work_target_store.py tests/unit/infra/test_start_lock.py -q` は460 passed（88.15秒）。全source/testsのRuff check/format（410 files）、変更12 source限定mypy、diff checkが成功した。限定型検査は全体gateの代替ではない。

局所migrationとvalidate、P-12以後、native Windows、full-suite/type gate、fresh Strict、Final Quality Gate、手動製品確認、実consumer切替は未完了。実dogfood metadata・workspace宣言・直接選択は変更していない。レビュー用pushの回答を待ち、SHA一致を満たさないStrictは起動せず、既存の実装認可に基づくローカル作業を継続する。goalはactiveである。

## P-11 schema3 workspaceの局所移行を接続

`workspace migrate --to-schema 3 --to-writer-protocol specdock.worktree-writer/v1`を通常external runtimeへ接続した。現在のschema3 workspace宣言だけをatomicに切り替え、存在する旧control_epochだけを除去する。既存のtitle/project_linkageがなければ追加せず、未知任意設定、全Scope ID/path/backend/linkage/親子/依存/本文のbytesを保全する。整数schema以外、未知protocol、unsupported required_features、構造不適合は副作用前に拒否する。既に新しい妥当な宣言ならunchangedとし、旧journalの再開やactiveの自動取得を行わない。

applyには`--backup-dir ABS --confirm-old-writers-stopped --yes`を必要とする。旧writer停止は利用者の運用確認であり、flagをprocess停止の観測証拠や強制封鎖として扱わない。保全先は既存の物理親directoryの下にある未存在directoryで、同cloneの全worktree・Git管理領域・installed packageとの重なりを拒否する。現在checkoutの仕様・Artifact・Workbench・static資産・未commit/ignored/untrackedの利用者成果物とGit実体を`checkout/`へ、linked等で外部にあるcommon-Gitを`common-git/`へコピーする。任意symlinkのtargetをたどらずlink値を保全し、特殊fileは適用前停止する。バックアップを別の隔離directoryへ復元して比較し、manifestだけで保全済みとしない。

保全先とsourceの物理identity・bytes/type/mode/linkを確認し、公開前後もsourceと保全内容を再確認する。新しいignored stage自身と新規の空親directoryだけを比較から除く。別のuser editや保全先の改変を見つけたら宣言の変更を止め、他actorの変更を戻さない。外部backup作成後の失敗はpartial6とし、確認済み/不明のbackup・未実行/確認済み/不明の宣言公開を分けてeffectsへ残す。Git由来の失敗は原文stderr/stdout/returncodeを維持する。旧activeの所在とpreserved-not-imported方針を出力し、未確定旧記録は手動の現物照合へ戻す。旧.git独自領域、別worktree、Git ref/index、GitHub、Start lock、ACL、registry、永続operation record、rollbackを変更・追加しない。

公開CLIの新option未接続、浮動小数schemaの誤受入、確認済みbackupの事後改変の見落とし、公開後中断時の誤ったafter_protocol、unsafe backup parentのIO分類、途中Gitエラーの隠蔽をfocused Red→Greenで確認した。240 Scope fixtureの全metadata bytes・二つの旧local綴りGitHub ID・未知任意fieldを保持した。Artifact構造検査が各Scopeのたびに全treeをロードして57,840 metadata readsになったため、取得済みviewsを同じ検査内だけで再利用し、240 readsまで減らした。永続cacheを導入せず、read-count試験をRed→Greenで検証した。

native POSIX別processを宣言公開の直前/直後で実際にSIGKILLし、fresh processが現protocolからplanned/unchangedを返すことを確認した。保全コピー/隔離復元の失敗、確認flag不足、旧remote unknownの拒否、外部symlink target非追跡、linked worktreeだけの切替、同cloneのcommon-Gitとmain workspace不変、後続user edit保全も回帰試験を通した。patch配置のfixture修正や初回からGreenのguardを、製品Redとして数えない。

関連25 fileのrunは643 passed/1 failed（131.65秒）。失敗は旧mapping移行を期待したhelp assertionで、新しい宣言切替と旧syntax退役の契約へportした。migration/helpのfresh runは60 passed（10.98秒）。全source/testsのRuff check/format（413 files）、変更9 source限定mypy、diff checkが成功した。限定検査と個別修正後のfocused runをfull-suite/type gateの合格と混同しない。

validate、P-12以後、native Windows、fresh Strict、Final Quality Gate、手動製品確認、実consumer切替は未完了。実dogfood metadata・workspace宣言・直接選択は変更していない。通常非force pushの利用者回答を待ちながらローカル実装を続け、goalをactiveに保つ。

## P-11 control不要の構造validateを接続

`workspace validate [--ci] [--require-nodes]`を通常external runtimeへ接続した。通常は現在のworking-tree構造を読み、CIはlive workspace宣言を読まないGit-only admissionからHEADを一度固定する。CIは固定OIDでtreeを列挙し、固定blob IDでworkspace宣言と認識された三階層Scope metadataだけを一時領域へ読み取る。Artifactは名前とregular/nonregular種類だけを再現して既存catalog検査へ渡し、本文やsymlink先を取得しない。RDP、Workbench、直接record、consumer runtime、旧controlのbodyも取得しない。永続cache・inspection record・Git内の独自fileを追加せず、一時領域はcontext終了時に除去する。

dataはC-05のvalidation familyで、valid/findings/snapshot_sourceにnode_countとCIのsnapshot_oidを加えた。構造不適合・不完全はfailed/7・effects=[]で返す。空workspaceはrequire-nodesなしでvalid、同optionありではNODES_REQUIREDとする。検査はGitHub lifecycleの成功証明ではない。Git環境の失敗は原文argv/stderr/stdout/returncodeを保ったfailed/5で返す。通常の既知schema/protocol admissionを弱めず、既知旧writer宣言は変更せず検査できる。

通常は実行状態を検査しない。明示expect-currentがある場合だけ同じ構造viewsと捕捉選択で条件を確認し、対象Scopeのないexpect-backendは拒否する。CIでlive expect-current/expect-backendを指定した場合は明示拒否し、受理した条件を無視しない。dry-runは同じ読取結果とcan_apply/blockersを返し、作業やbranchを予約しない。helpの旧generation/pending recovery説明をこのleafでは新契約へ置換した。

未接続の公開CLI、CIがworking workspace宣言を参照する不具合、未commit修正でcommit破損を隠す挙動、空workspace/require-nodes、root/Scope Artifact slot衝突の20 casesをRed→Greenで確認した。helpの固定HEAD説明不足もfocused Red→Greenで確認した。追加回帰は元からGreenとして区別し、検査中に実GitでHEADを移動しても初期OIDを使用すること、Artifact等のbodyへのcat-fileを禁止してmetadata blobだけを取得すること、root/Scope Artifact directory/file symlinkの非追跡、三階層の依存/親子/metadata破損、同ID別path、無関係entry非採用を検証した。linkedとmainで異なるHEAD・件数を検査し、linkedの未commit宣言をCIに混ぜないことも確認した。

公開CLI 50 testsは5.26秒で成功。fresh wheel・sdistからのwheel・外部venv・実consoleの通常/CI validateを含むfresh runは51 passed（11.51秒）。配布版はsource checkout外から実行し、privateな未commit宣言/metadataでもCIがcommitの一Scopeを検査できた。全source/testsのRuff check/format（416 files）、変更source/test六file限定mypy、diff checkが成功した。限定型検査は全体type gateの代替ではない。

関連run `uv run pytest tests/cli_runtime/test_issue413_workspace_doctor.py tests/cli_runtime/test_workspace_doctor_vnext.py tests/cli_runtime/test_issue413_contract.py tests/cli_runtime/test_help_completion_vnext.py tests/cli_runtime/test_issue413_work_start.py tests/cli_runtime/test_issue413_active.py tests/cli_runtime/test_issue413_finish.py tests/cli_runtime/test_issue413_dependency.py tests/cli_runtime/test_dependency_vnext.py tests/cli_runtime/test_issue413_worktree.py tests/cli_runtime/test_issue413_worktree_remove.py tests/cli_runtime/test_issue413_worktree_bootstrap.py tests/integration/test_issue413_observation.py tests/integration/test_issue413_sync.py tests/unit/infra/test_work_target_store.py tests/unit/infra/test_start_lock.py tests/integration/test_issue413_migration.py tests/cli_runtime/test_issue413_artifact.py tests/cli_runtime/test_issue413_workbench.py tests/cli_runtime/test_issue413_scope_delete.py tests/cli_runtime/test_artifact_vnext.py tests/cli_runtime/test_artifact_commands_vnext.py tests/cli_runtime/test_scope_delete_vnext.py tests/unit/infra/test_issue413_committed_workspace.py -q --tb=short` は646 passed（114.68秒）。修正済みmigration helpもfresh runで成功した。元processの完了とexit0を確認し、quiet outputを理由にjobを再起動していない。

P-12以後、native Windows、full-suite/type gate、fresh Strict、Final Quality Gate、手動製品確認、実consumer切替は未完了。実dogfood metadata・workspace宣言・直接選択を変更していない。通常非force pushの利用者回答が未着であるため、現在SHAの一致を満たさないStrictは起動せず、認可済みローカル実装を継続する。goalはactiveである。

## P-12 PATH委譲の静的shimを実装

provider `shim_vnext.py`と配布`assets/spec_dock/scripts/spec-dock`を同じstandalone shimへ置換した。PATH上の外部consoleを解決し、argv・cwd・native stdout/stderr・終了値を保持してexecする。Git common-dir、engine locator/control、distribution digest、consumer Pythonを読まず、固定engineへの別経路を作らない。自身と同inodeのcandidate、symlink/hardlink、同shimのコピー、既知旧shimは実行前にSHIM_RECURSIONで拒否する。copy識別は先頭4096 bytesに限定し、正常な外部consoleへのsymlinkは受理する。

外部console不在や起動不能は導入/PATH確認の案内とexit3を返す。JSON指定時はv2 diagnostic envelope・effects=[]・stderr空で返し、double-dash後のjson文字列は制御指定にしない。shim自身はisolated Pythonで起動し、外部consoleにもcallerのPYTHONPATH/PYTHONHOME/PYTHONUSERBASE/PYTHONSTARTUPを渡さない。通常の利用者設定は保持する。Git stateやproject bindingの検査は外部CLIが担当する。

Git不在での10 failuresをRedとして確認し、native standalone委譲へ接続して10 passedになった。追加二casesは元からGreenとして記録し、実行可能な`./spec -h` symlink、shim directoryのjson/shutil moduleとcaller PYTHONPATHによるimport置換の防止を検証した。引数のspace・Unicode・改行・shell文字列、nested cwd、missing project、外部stderr/非0終了値もそのまま保持した。fake executableはhermetic fixtureであり、実GitHub通信の実績ではない。

provider scriptsと未切替dogfood scriptsの全bytes一致を期待した旧testは、意図した供給版更新で一件失敗した。P-16の実consumer切替と混同しないよう、このtestをstatic asset集合の検査へ更新し、供給sourceとstatic shimの完全bytes一致を維持した。fresh wheel内のshim/README bytesをproviderと比較し、sdistからのwheelとの資産集合一致も確認する。外部venvの実consoleを配布shimから起動してpackage metadataのversionを確認した。現consumerのshimは変更していない。

`uv run pytest tests/integration/test_issue413_shim.py tests/integration/test_issue413_wheel.py tests/unit/infra/test_provider_distribution.py -q --tb=short` は16 passed（6.71秒）。全source/testsのRuff check/format（417 files）、変更四source/test限定mypy、diff checkが成功した。`uv run pytest tests/integration/test_cli_entrypoint_vnext.py -q --tb=short` は13 passed/2 failed（3.92秒）。PATHを無視してpinを使う旧保証の一件はD-02と異なり、旧group initの一件はP-02から未完了の経路である。旧pin/tamper/group-init test群は後続のinstallationとfixed helper退役で新契約へportし、成功したことにせずfull gate前に閉じる。

static inventory・installation・配布skills・旧実装退役、native Windows、full-suite/type gate、fresh Strict、Final Quality Gate、手動製品確認、実consumer切替は未完了。P-12は実装中であり、goalをactiveに維持する。

## P-12 単worktreeのstatic初期導入と確認

`installation init ABS`と`installation show --target ABS`を、workspaceが未導入でも使えるGit-only admissionへ接続した。従来dispatchは明示された導入先を使わずCWDを解決していた。新しい処理は対象を正確なGit rootへ照合し、`--project`との矛盾、相対path、subdirectory、解決対象のないbackend guard、検証不能なcurrent guardを副作用前に拒否する。showはpackage version、workspaceの限定header、各static資産の分類を読む。任意bodyを出力せず、control/登録WT/engine digestを要求しない。

package内の`assets/static-inventory.json`に86 filesの許可target、resource source、SHA-256、mode、init専用区分を固定し、`importlib.resources.files`のTraversableからbytesを取得・検証する。initは新writer protocolのworkspace宣言と静的資産だけを置く。runtimeコピー、.agent、Git内のSpecDock独自領域は作らず、既存project内容を保持する。既存fileが一件でもあれば計画時に全適用を止め、symlink/hardlink/FIFOとunsafeな親を追跡して上書きしない。既知旧hash・退役inventoryとupdate/uninstallは次の単位で実装し、現時点の空のknown-old集合を移行所有権の証明には使わない。

適用は安全な親descriptorと一件ごとの候補・no-replace公開を使う。directory/fileの確認済み効果、unknown publication/残った候補、未実施資産をpartial6へ残す。成功済みのfileを削除して元へ戻さず、途中記録やjournalを新設しない。dry-runはdirectory、stage、backup、直接記録、Git/GitHub mutation、Start lockを一切行わない。実linked worktreeの導入ではmainとcommon-Gitの全実体が不変だった。

最初の6ケースはCWDの誤解決または未接続dispatchでRedになった。衝突テストの初回3 Greenは、誤ったrepoでの未接続exit3による偶然であり、衝突pathと診断まで検査して6 Redとして取り直した。途中失敗の2 casesは未実施資産と残った候補の表示欠落でRed、help/recoveryの4 casesは旧group/engine説明と廃止引数の遅い判定でRedになり、それぞれGreenへ修正した。親symlinkのexit5/3不一致もRedとして分類を訂正した。FIFOを全tree digestへ渡したfixture失敗は製品Redに数えず、FIFO自身のidentity/typeと周辺treeを別々に比較した。他のguard、別WT、archive資産の回帰は元からGreenとして区別する。

`uv run pytest tests/integration/test_issue413_assets.py tests/integration/test_issue413_wheel.py tests/integration/test_issue413_shim.py tests/unit/infra/test_provider_distribution.py tests/cli_runtime/test_help_completion_vnext.py -q --tb=short` は67 passed（18.05秒）。そのうち新asset suiteは25 cases。fresh wheel/sdist/外部venvから実consoleでinit/showし、新宣言・runtime不在・control不在・show副作用0を確認した。sourceの通常Path以外にTraversable ZIPでも同じshim bytesを配置できた。全source/tests Ruff check/format（420 files）と変更七file限定mypy、diff checkが成功した。型注釈だけのfault fixture修正後にも部分失敗の2 casesを再実行し、2 passed（0.19秒）を確認した。

installation update/uninstall、配布docs/skillsと旧実装退役、native Windows、full-suite/type gate、fresh Strict、Final Quality Gate、手動製品確認、実consumer適用は未完了。実dogfood workspace・metadata・shim・状態は変更していない。レビュー用pushの利用者回答を待ちながら、認可済みローカル実装を続ける。P-12とgoalは進行中である。

## P-12 単worktreeのstatic更新・退役・アンインストール

`installation update/uninstall --target ABS --backup-dir ABS --yes`を通常packageからの単worktree処理へ接続した。新writer workspaceを要求し、宣言の未知設定を含めてbytesを保持する。current/known-old hashに一致するstatic filesだけを計画し、ユーザー改変・未知hash・unsafe entryは副作用前に停止する。native Git inventoryは外部backupの配置境界を確認するためにだけ使い、他WTの資産・Scopeを一括更新しない。GitHub通信とStart lockを行わず、旧controlの状態を適用判断へ使わない。

外部backupは置換・退役対象の旧static bytesとmodeだけを`backup/static/<relative>`へ保全する。独立した一時場所へ実際に復元して比較し、backupの実体と内容も公開・退役の各境界で再検証する。仕様、Artifact、Workbench、直接記録、Git metadataをstatic backupへ混ぜない。新規fileだけの更新でも空のstatic保全先を確認し、workspace宣言を変更しない。既存fileのmodeを保持し、欠けたfile/directoryだけを作る。

旧standalone shimの既知hashを記録し、旧runtime138 filesと旧version一fileを退役inventoryへ追加した。139件の`source_basis`はすべて基準`6fec3099d8759b4e5b3b393b2987534b46dfa383`のblobと照合済みである。旧shim/control-storeのfixtureはそのblobの不活性bytesであり、旧実装を実行しない。既知path/hashに一致するfileだけを保全後に一件ずつunlinkし、directoryや同じ場所のユーザー追加fileをまとめて削除しない。uninstallは仕様・状態の保持に加えてworkspace宣言、ignore規則、directoryを残し、二回目はunchangedになる。

途中失敗では確認済みbackup・file/directory効果、結果unknownの公開/削除、残った候補、未実施対象を区別してpartial6へ返す。backup作成後の一時capture cleanup失敗を「副作用なし」のexit5へ落としていた経路を実Redで確認し、backup succeeded/残りnot_attemptedへ修正した。native unlinkの直前/直後故障では結果を推測せずunknownとし、実体とbackupを保持する。自動rollback、journal、operation replay、共通writer lockを設けない。

TDDではupdate二cases、欠けたfile/directory、既知runtime退役、uninstall二cases、help二cases、cleanup失敗、redirected current/retired entry二cases、runtimeを配布してしまう不正inventoryを、それぞれ公開CLIからRed→Greenで確認した。fault fixtureの一時directoryがmacOSの`/var` aliasだった不成立はtool管理の実体pathへ修正した。追加testの配置ミスはfixture修正後に元init二casesと退役Redを取り直し、製品成功に混同しない。旧runtimeの削除直前/直後、未知改変、backup guard、廃止引数、linked WT隔離等は既にある実装の回帰としてGreenを確認した。

`uv run pytest tests/integration/test_issue413_assets.py tests/integration/test_issue413_wheel.py tests/integration/test_issue413_shim.py tests/unit/infra/test_provider_distribution.py tests/cli_runtime/test_help_completion_vnext.py -q --tb=short` は98 passed（75.93秒）。asset suiteは56 cases。fresh wheel→sdist由来wheelの資産一致、外部venvの実consoleによるinit/show/update/uninstall、外部backup、仕様・ignore保持とGit副作用0まで確認した。全source/testsのRuff check/format（421 files）と変更八file限定mypyは成功した。限定mypyのtest trap注釈をNoneへ修正し、follow-imports=skipでも戻り値不整合を残していない。

provider旧helpersの退役、配布docs/skills、native Windows、full-suite/type gate、fresh Strict、Final Quality Gate、最終手動製品確認、実consumer適用は未完了。実dogfood workspace・metadata・shim・状態は変更していない。通常非force pushの利用者回答を待ちながら認可済みローカル実装を続け、P-12とgoalを進行中に維持する。

## P-12 配布docs・skillsと実配布の整合性

root README、providerのCurrent reference/migration、単独offline HTML、二つの配布skillを通常外部CLIへ合わせた。GitHub番号と既存IDを正本にし、新規local/offline Scope、UUID、中央control、engine pin、cache/generation、journal再開を操作案内から外した。Historical六fileは同じpathに退役通知とCurrentへの入口を残し、旧操作を新規作成手順へ戻さない。ユーザーの実dogfood資料を直接差し替えた実績ではない。

改稿時は確定requirement/design/CLI契約と現行公開handlerを照合した。active setのchain内focus変更という誤った草稿を、同一妥当directのunchangedだけへ訂正した。Syncの観測値はdata直下であり、FamilyDataと同じdata.resultではない。worktree createのNAMEは必須で、旧optional表記を現在helpへ合わせた。Startだけの短い排他、通常編集の権限制度なし、FinishのGitHub完了確認・捕捉記録だけ解除・branch保持を明示する。

Grill skillは明示起動用frontmatterを持ち、外部CLIのexit0/v2/succeeded/artifactを確認してdata.result.artifact.pathを受け取る。partial/unknownなら本文確定や自動再作成をしない。既存finalizerのidentity/finalize境界は変更していない。公開CLIで生成したresearch Artifactを実helper processで確定し、元frontmatter/title/prefixを保持して本文だけを完成できた。16 canonical文書、全Scope metadata、Git bytesは不変で、直接記録も作らない。この追加は既存実装のGreen回帰であり、新しい製品不具合のRedとは呼ばない。

provider parityは新CLIで初期化した一時consumerへportした。実dogfood切替前のbyte差を理由にruntime/controlを再配布しない。最初の関連runは旧S01のREADME/guide比較二casesが失敗し、211 passedだった。これらも一時consumerとの同じbyte比較へ移し、削除/skipせず維持した。wheel内の全86 static payloadとhash、実consoleが新規consumerへ置いた全86 payloadもproviderへ照合する。18変更資産のknown-old hashはfb42d21fe53e993439c293a1412e746665a81399のGit blobと個別照合し、86 current / 139 retiredのpath・mode・退役根拠は保持した。

`uv run pytest tests/unit/infra/test_authoring_kit_assets.py tests/unit/infra/test_provider_distribution.py tests/unit/infra/test_issue_359_skill_helpers.py tests/integration/test_cli_docs_vnext.py tests/integration/test_issue413_artifact_skill.py -q --tb=short` は213 passed（2.35秒）。`uv run pytest tests/integration/test_issue413_assets.py tests/integration/test_issue413_wheel.py tests/integration/test_issue413_shim.py tests/unit/infra/test_provider_distribution.py tests/cli_runtime/test_help_completion_vnext.py -q --tb=short` は98 passed（74.42秒）。両runは一部重なるため、独立件数の合算とはしない。全source/tests Ruff check/format（423 files）、変更五test file限定mypy、diff checkが成功した。offline HTMLは24 unique IDs、35解決済みlinks、script/外部stylesheet/通信依存0とCSPを静的確認した。最終ブラウザ・Tailscale資料検査の代替ではない。

最終差分確認でworktree参照のNAME省略案内も必須名へ訂正し、同じ旧commit hashを保持してpackage inventoryを更新した。その候補を文書/配布/helper suiteとfresh wheelで再検証し、214 passed（15.57秒）を確認した。最終候補の全86 resource hashと、新規導入先の全86 bytesが一致する。

provider旧helpersの退役、native Windows、full-suite/type gate、fresh Strict、Final Quality Gate、最終手動製品確認、実consumer切替は未完了。通常非force pushへの回答が未着で、Strictのlocal/upstream SHA一致も未成立である。actual dogfood workspace・metadata・shim・.agents・状態は変更せず、認可済みローカル実装を続ける。

## P-12 公開help・補完と旧CLI契約のport

workspace migrateのparser catalogが、廃止済み--resume/--rollbackをusage/optionsと補完へ注入していた。public mainのhelpを使う一件のRedで検出し、注入loopを削除して同じtestをGreenにした。非公開の旧dispatcher用対応表は後続の旧実装退役まで隔離して残すが、公開syntaxを生成しない。optionsから未使用の旧recovery案内・operation ID検査を除き、未使用backend/source/rollback定数も退役させた。通常のbranch createのbase必須検査は保持する。

旧CLI契約suiteの11 failed/17 passedは、mapping-file、local作成、engine pin/journal復旧、cache既定、readのdry-run拒否、worktree alias等の旧期待値だった。確定#413契約へportし、Scope作成の明示backend/parent/title、共通option位置と重複、finite timeout、廃止診断、44 leaf構成とhelp、原文/JSONという検査目的を保持した。旧四recovery leafはvalid/invalid tokenと二flagの16 casesで、副作用前ARGUMENT_RETIRED/exit2、effects空、未導入projectへの書込み0を確認する。syntaxのportで新要求を決め直した実績ではなく、既に実装された新契約を確認する回帰である。

help suiteは旧run_vnextを直接起動せず、実public mainから stdout/stderr/終了値を捕捉する。repositoryがないproject指定でも全44 leafのusage/optionsから復旧flagが消え、全例が現在parserで解釈できることを確認した。native bash/zshの実補完はmigrationの新optionを提示し、旧二flagを提示しない。root version、help、usage errorはv2 utility/diagnostic envelopeへ照合する。

`uv run pytest tests/cli_runtime/test_cli_vnext_contract.py tests/cli_runtime/test_help_completion_vnext.py tests/cli_runtime/test_issue413_contract.py tests/integration/test_issue413_migration.py tests/integration/test_issue413_wheel.py -q --tb=short` は113 passed（22.36秒）。全source/tests Ruff check/format（423 files）と変更四file限定mypyが成功した。限定mypyではpytest.skipをAnyと見なすとnative executableがstrへ絞れなかったため、skip後の明示assertを追加した。製品変更ではなくtest helperの型境界であり、help/native補完の29 testsをfresh runで再確認（0.78秒）した。全体type gateの代替ではない。

legacy provider/runtime helpersの退役、native Windows、full-suite/type gate、fresh Strict、Final Quality Gate、最終手動製品確認、実consumer切替は未完了。実dogfoodの状態を変更せず、レビュー用pushの回答を待ちながら認可済みローカル作業を続ける。

## P-12 公開入口の通常wheel・実consoleへのport

旧fixed入口suiteの全15 testsを本文と確定仕様で照合し、廃止するpin/digest/builder/control APIと維持する公開保証を[移行根拠](artifacts/test-port-entrypoint.md)へ記録した。通常wheelをcheckout外のfresh venvへ非editable・no-index導入し、import元が外部site-packagesであることを確認する。fake固定bin/libや旧run_vnextを入口にしない。root/leafのparse、環境分離、対象Git rootと読取不変の目的は実consoleへ移した。

三階層のGitHub-backed fixtureで実consoleによるIssue Start→Sync→Finishを確認した。Gitは実programでbranch作成とcheckoutを行い、開始後と完了後のbranchを独立したnative Git呼出しでも照合する。stateful gh executableは別の一時場所にあり、Issue #3だけを一度PATCHしてcompletedにする。Syncはdirectと祖先の件数を表示し、記録bytesを変更しない。Finishは捕捉記録だけを解除し、祖先のremote状態、全Scope metadata、workspace宣言とbranchを保持する。独自`.git/spec-dock`を作らない。これはhermetic fake GitHubとmacOS実processの証拠で、live GitHubやWindows受入ではない。

旧locatorの不正JSON/相対path/欠けたpackage/digest不一致は通常Scope読取の実行権限を持たず、元のGit bytesも変更しない。通常/CI validateはcontrolなしで成功してtree不変。実wheelのstatic shimはconsumer sitecustomize/local package/runtimeを実行せず、GIT_DIR/GIT_WORK_TREEで別repoへ誤誘導されない。外部consoleへの正当なsymlinkを許し、同じpackageを使う二つのcloneではCWD/明示projectの各Scopeとinventoryだけを観測する。明示subdirectoryは拒否する。origin shimへの拘束と独自pinによるprogram改変検出を新契約へ戻さない。

最初の実console lifecycle一件は1 passed（3.84秒）、port後entrypoint suiteは14 passed（6.23秒）で、いずれも既存実装のGreen回帰。新しい製品不具合のRedとは扱わない。native Gitによるbranch照合を補強してから `uv run pytest tests/integration/test_cli_entrypoint_vnext.py tests/integration/test_issue413_wheel.py tests/integration/test_issue413_shim.py tests/unit/infra/test_provider_distribution.py -q --tb=short` を実行し、30 passed（23.84秒）を確認した。全source/tests Ruff check/format（423 files）、変更test一file限定mypy、diff checkも成功した。formatで余分な空行とlayoutを整えた修正は製品不具合ではない。

旧CI固定bundle routeとprovider/runtime helpersの退役、native Windows、full-suite/type gate、fresh Strict、Final Quality Gate、最終手動製品確認、実consumer切替は未完了。実dogfood workspace・metadata・shim・.agents・状態は保持する。レビュー用pushの回答を待ちながら認可済みローカル実装を続け、P-12とgoalは進行中とする。

## P-12 CI検証経路の通常wheelへの切替え

CI scriptのfixed bin/lib生成、asset copy、version.txt、digest preflightと旧external_cli起動を、確認済みcommitのpackageを通常wheelへbuildする経路に置換した。full SHA、正確なGit root、clean sourceの事前検査を保持する。Git archiveでcommitを専用scratchへ取り出してbuildし、外部fresh venvへ非editable installする。wheel hashは実行結果の識別表示にとどめ、Git内のpinを書かない。実consoleは`workspace validate --ci --json`だけを実行する。

最初にsource fixtureの不足build入力でsetupが不成立になったため、存在するREADME/setup.pyだけへ訂正した。旧targetが検証対象HEADにworkspaceを持たない構成も現在のcommit済みfixtureへ変更した。これらは製品Redに数えない。成立したfixtureでは旧CI経路が新writerをworkspace_schema_mismatch/exit7/v1として拒否した。同じ公開scriptを通常wheelへ改修した後、1 passed（2.09秒）、v2/HEAD/valid/効果0を確認した。旧builderを不活性sentinelに置換した回帰では、それを実行せず通常package経路だけが動く。

旧CI七casesの判断は[移行根拠](artifacts/test-port-ci.md)へ記録した。tracked/untracked dirty、短縮/不正SHAとSHA不一致はbuild前に拒否する。旧engine digest形式検査はwheel build故障に置換し、故障時の実console未実行、source/target不変を確認する。全casesでentry type/mode/bytesのsource/target snapshotを比較した。`uv run pytest tests/integration/test_ci_fixed_validation.py -q --tb=short` は7 passed（4.42秒）。native Bashのsyntax checkと変更test一file限定mypyも成功した。CI workflowへPython 3.11とuvの明示導入を追加し、既存Provider配布laneを新wheel/単WT static installationへ変更した。通常lintと全pytestを削らない。

これはmacOSローカルのscript実行とhermetic fixtureの証拠であり、GitHub Actionsの実ジョブ成功ではない。provider/runtime helpersの退役、native Windows、full-suite/type gate、fresh Strict、Final Quality Gate、最終手動製品確認、実consumer適用は未完了。実dogfoodとGit内の旧独自領域は変更せず、P-12とgoalを進行中に維持する。

## P-12 実consumerのCI読取と全件pytestの途中確認

cleanな`323caf28084f7d7087e8ea96999e3ee2e2fad033`から、通常wheelを外部へbuild/installする同じCI scriptで実consumerのHEADを読み取った。最初の通常python3（3.12.6）はfresh venvの標準libraryを解決できず、wheel install前にexit2となった。元logはWorkbenchに保持した。グローバルPythonや製品依存を変更せず、試験で使う有効な`uv run python`（3.12.11）の環境で再確認した。

後者はexit0/v2/succeeded、snapshot_source=HEAD、snapshot_oid=`323caf28084f7d7087e8ea96999e3ee2e2fad033`、valid=true/node_count=240/findings=0/effects=[]だった。実metadata集約hashは前後とも`0d380bdcfb2efd492eaaae8b072e105538b75c1d6099de8df321b6f9ea449e74`、workspace宣言は前後とも`53920a4d2f3fd34c51e37f47d1e0baa87227f34bef7b5d2cb8f2f07700fea8b0`。旧writerの宣言や実Scopeは変更していない。read-only CIの実console確認であり、正式Start・migration・dogfood切替や最終手動製品受入ではない。

同じsource候補で未除外の`uv run pytest -q --tb=short`を全件実行し、exit1/79 failed/2056 passed/1 skipped（417.10秒）だった。失敗は旧CLI adapter、旧内部dispatcher、全WT installation/recoveryなど18 filesにある。廃止引数、旧Namespace属性、旧v1 payload/中央controlの期待が目立つが、名前だけで全件を不要と判断しない。各fileを本文/正本/現行回帰へ対応させ、full gate前に閉じる。成功件数を全体合格へ読み替えず、policy skip/除外ledgerを追加しない。

完全なraw logとJSON要約は既存Epicのignored Workbench `iss-00413-implementation/ci-current-323caf28{,-uv}.{log,json}` と `pytest-p12-323caf28.log` に保持する。実repoのbranch/HEADは保持され、tracked差分0だった。

## P-12 Writer admissionの公開境界へのport

中央登録/engine digest/epoch、maintenance mode、global pending recovery、全writer leaseを要求する旧14 casesの判断を[移行根拠](artifacts/test-port-writer-admission.md)へ記録し、自WTのwriter宣言と公開Scope編集の四casesへ置換した。新protocolは中央登録なしでも動き、自WTの旧protocolではeffect0/exit3で拒否する。別linked WTが旧protocolでも自WTを編集でき、他WTと旧control/opaque記録を変更しない。Git common-dirの実共有は維持する。

さらに実common-dirのStartLockを保持した親processから、別linked WTのpublic mainを別processで起動してScope編集が成功することを確認した。自WT/旧controlのbytesは不変、直接記録の生成0で、短いStart排他を全編集の権限やleaseに広げない。既存の別process競合・owner強制終了後の解放・同Scope重複/兄弟並行開始は現行Start試験で維持し、旧leaseの内部呼出し順を製品保証へ戻さない。

新しい四casesは4 passed（0.77秒）。続いて公開Scope編集、Start排他・同時開始、migrationと合わせた `uv run pytest tests/integration/test_cli_writer_compatibility_vnext.py tests/cli_runtime/test_issue413_scope_edit.py tests/unit/infra/test_start_lock.py tests/integration/test_issue413_start.py tests/integration/test_issue413_migration.py -q --tb=short` は63 passed（14.63秒）。全source/tests Ruff check/format（423 files）、変更一test file限定mypy、diff checkも成功した。既存実装のGreen回帰であり、製品修正のRedではない。元old writer APIsを新しい製品経路へつなぐ変更は行っていない。旧runtime/provider helperの退役、79旧経路失敗の個別port、native Windows、全体gate、fresh Strict、Final Quality Gate、最終手動確認、実consumer適用は未完了。goalをactiveのまま継続する。

## P-12 Work / branch adapterの公開入口移行

旧三files・七関数を全文確認し、[移行根拠](artifacts/test-port-work-branch.md)へ各保証の維持/撤去を記録した。旧WorkContext/run_vnext/active_storeを公開main、GH-backed三階層と実Gitへ置換する。三kindそれぞれで一件選択→対象Issueだけcompleted→捕捉解除・branch保持を確認した。Finish/Startのpreviewはref・metadata・remote・選択を変更せず、Finishは--yesなしでremote観測前に拒否する。

branch create/show/switchのtipとdry-runはnative Gitでも比較し、既存refの再createでresetが起きないことを確認した。空からのactive setはWORK_START_REQUIRED、ancestor clearは親へ昇格せずemptyになり、remote/checkoutは不変である。独自engine digestの拒否を実行権へ戻さず、自WT旧writer宣言での効果前停止を確認した。

最初の四失敗は移行testが既存branchの明示--branchを欠き、旧v1 target欄を期待したものだった。確定契約へ期待を訂正し、製品Red/新しい互換要求とは扱わない。三filesの九casesは9 passed（7.31秒）。hook、直接記録、同時Start、遅いFinishの現行suiteも含む `uv run pytest tests/cli_runtime/test_work_commands_vnext.py tests/cli_runtime/test_branch_commands_vnext.py tests/cli_runtime/test_vnext_runtime_work.py tests/cli_runtime/test_issue413_branch.py tests/cli_runtime/test_issue413_active.py tests/cli_runtime/test_issue413_work_start.py tests/cli_runtime/test_issue413_finish.py -q --tb=short` は186 passed（62.83秒）。全source/tests Ruff check/format（423 files）、変更三test file限定mypy、diff checkも成功した。macOS/hermetic GitHubの回帰であり、Windows native、全件gate、fresh Strict、最終手動確認と実consumer適用は未完了である。

## P-09/P-12 Scope確認中の直接選択変更の再検査

旧Scope lifecycle suiteを仕様へ照合する中で、保持すべき端末確認の競合検査を公開mainへ移し、不具合を再現した。元Scope #1の確認表示中に別processの実Startで#2へ切り替えると、元processはyes後に#1をCloseしてexit0を返した。Redは1 failed（1.34秒）、native Git/PTY/二CLI processとstateful ghによる製品挙動の失敗である。[分析と修正](artifacts/scope-confirmation-recheck.md)に旧testとの対応を残す。

確認を必要とするScope close/reopenだけで、metadata/physical contextの再検査に加え、捕捉した自WTのselection status/record/handleを再読取結果へ照合する。選択が変わればremote変更前にexit3で止め、新記録を保全する。全編集lockや権限制御を追加せず、Finish/--yesの契約は維持した。同じClose testは1 passed（1.31秒）。関連Scope lifecycle/Finish/active/writer suiteは90 passed（20.90秒）。その後Close/Reopen二casesへ広げ、2 passed（2.31秒）で両経路の新記録・metadata・remote不変とPATCH0を確認した。全source/tests Ruff check/format（423 files）と変更source/test二file限定mypyも成功した。fresh Strict、全体gate、Windows、実consumer適用は未完了である。

## P-12 Scope lifecycle / query / deleteの公開入口移行

旧三files・十一関数を全文確認し、[個別の移行判断](artifacts/test-port-scope-lifecycle-query-delete.md)を記録した。新規local発行・control登録・旧run_vnext・journalをfixture/入口から除き、既存localのclose/reopen/not-planned codec、GH-backed current selectorとguard、kind/parent読取、title/revision編集・本文保全、確認/dry-run・外部backup後削除を公開mainと現物へ比較する。端末代替のstdin試験は実PTYの証拠とは区別する。

native Gitのcontext故障をread/edit双方で注入し、元stderr/returncode/effects空とrepo不変を確認した。削除後の再操作は旧journalのreplayではなく、既存backupを上書きせず拒否する。最初の移行runで、その拒否をexit4と期待した一件は実装契約のexit3へ訂正した。製品Redには数えない。三filesは10 passed（3.04秒）。さらに元の確認競合testにあったguard省略条件を、guard有無×Close/Reopenの四実process casesで確認した。

`uv run pytest tests/cli_runtime/test_scope_lifecycle_commands_vnext.py tests/cli_runtime/test_vnext_runtime_scope.py tests/cli_runtime/test_scope_delete_commands_vnext.py tests/cli_runtime/test_issue413_scope_lifecycle.py tests/cli_runtime/test_issue413_scope_edit.py tests/cli_runtime/test_issue413_scope_delete.py -q --tb=short` は81 passed（21.05秒）。全source/tests Ruff check/format（423 files）、変更四test file限定mypy、diff checkも成功した。実consumer・Git内の旧独自領域は保持する。旧create/import/installation/recovery経路とprovider/runtime退役、native Windows、全件type/pytest gate、fresh Strictと最終手動確認は未完了で、goal/P-12をactiveのまま継続する。


## P-12 Scope create / importの公開入口移行

旧二ファイルの二十関数を全文確認し、[対応表](artifacts/test-port-scope-create-import.md)へ保存した。新規local発行は三kindともproject読取前のexit2で拒否し、真正の既存local codecのshow/editと日本語本文の保全は維持する。新規作成は確認済みGH番号から正式IDを生成し、previewではIDを割り当てない。importはexact refをGETし、POSTとlifecycle cache書込みを行わない。

確認回答時にnative Gitでoriginを変更すると、捕捉したrepositoryとの相違によりPOST前に停止する。GH作成が確定した直後に別actorがローカルpathを占有するケースでは、partialに確定refを表示し、既存pathを保全する。旧resumeを拒否した後、利用者がpath衝突を解消して新しい明示importを実行すると、同じIssueへGETだけで正式IDを復旧できた。合計通信はPOST一回・GET一回であり、旧journal・prepared ID・自動rollbackは追加しない。

初回の十三cases中一失敗は、作成前の不正なScope pathがPOST前に拒否されるfixtureを、remote後のpartialと誤って期待したものだった。実装の安全な事前拒否を保持し、衝突をremote確定後に発生させるfixtureへ訂正した。製品Redには数えない。訂正後は13 passed（3.55秒）。関連publication/import/editを含む `uv run pytest tests/cli_runtime/test_scope_create_commands_vnext.py tests/cli_runtime/test_scope_import_commands_vnext.py tests/cli_runtime/test_issue413_scope_publish.py tests/cli_runtime/test_issue413_scope_import.py tests/cli_runtime/test_issue413_scope_edit.py -q --tb=short` は78 passed（24.92秒）。

全source/testsのRuff check/format（423 files）、変更二test限定 `mypy --follow-imports=silent`、diff checkを実施した。stdin代替の型を修正した後は限定mypyが成功し、変更したorigin確認testも1 passed（0.45秒）。限定type結果を全体mypy合格とは扱わない。実consumer・旧独自Git領域・live GitHubは変更していない。残るdiagnostics/migration/sync/worktree/installation/recoveryの移行、provider/runtime退役、native Windows、全体type/pytest、fresh Strict、最終製品手動確認を継続する。

## P-12 Workspace diagnosticsの公開入口移行

旧二ファイルの九関数を全文確認して[対応表](artifacts/test-port-workspace-diagnostics.md)を記録した。旧run_vnext/private diagnosis/control admission/new local fixtureを外し、公開mainで空workspaceの通常validate・require-nodes・doctor、HEADの有効/無効schema検査を行う。通常Doctorは旧control/generationをauthorityにしない。--legacyを明示した診断だけで旧controlのinvalid_jsonを報告し、private bodyを露出せず全treeを保持する。依存とartifactの二不整合を同時に置く試験では、validate/doctor双方が二findingを報告し、外部symlink先も書き換えない。

後継二ファイルは5 passed（0.78秒）。現行Doctor/validationの公開suiteを合わせた `uv run pytest tests/cli_runtime/test_workspace_diagnostics_commands_vnext.py tests/cli_runtime/test_workspace_doctor_vnext.py tests/cli_runtime/test_issue413_workspace_doctor.py tests/cli_runtime/test_issue413_workspace_validate.py -q --tb=short` は122 passed（16.75秒）。全source/testsのRuff check/format（423 files）、変更二test限定 `mypy --follow-imports=silent`、diff checkも成功。限定Greenであり、full type/pytest、native Windows、fresh Strict、実consumer切替と最終手動動作確認は未完了である。

## P-12 Workspace migrate / syncの公開入口移行

旧二ファイル・十二関数を全文確認し、[移行判断](artifacts/test-port-workspace-migrate-sync.md)を保存した。migration previewは別WTの未知宣言を編集せず、明示した自workspaceの宣言だけを計画する。applyは外部backup、旧writer停止の明示確認、--yesを要求し、保全物の実copy/restoreを検証してから宣言だけを更新する。全Scope bytes/未知設定を保全し、旧mapping-file/rollback/operation IDを復活させない。

Syncは通常/previewともdirect記録とopaqueな旧generationを更新せず、現物からscope lifecycle・選択件数を返す。真正の既存localと空treeの互換を保つ。GH GETが失敗するとpartial/exit7とunknownを返し、記録を消さない。安全に解釈できないparent metadataは--allow-invalidでも完全な観測にしない。初回の一失敗はpreview statusをsucceededと期待したものだったが、公開dispatcherの契約はplannedのため期待を訂正した。製品Redには数えない。

後継二ファイルは9 passed（1.74秒）。現行migration/syncのintegrationを合わせた `uv run pytest tests/cli_runtime/test_workspace_migrate_vnext.py tests/cli_runtime/test_workspace_sync_vnext.py tests/integration/test_issue413_migration.py tests/integration/test_issue413_sync.py -q --tb=short` は67 passed（16.30秒）。全source/testsのRuff check/format（423 files）、変更二test限定 `mypy --follow-imports=silent`、diff checkも成功。実consumer/live GitHubは未変更で、旧worktree/installation/recovery入口とprovider退役、全体type/pytest、native Windows、fresh Strict、最終手動確認を継続する。

## P-12 Worktree adapterの公開入口移行

旧三関数を全文確認して[移行判断](artifacts/test-port-worktree-adapter.md)を記録した。registered ID・control・run_vnextを外し、公開mainでnative Gitのpath/branch/HEADとlist/showを比較する。壊れた無関係のScope metadataを読ませず、全tree不変を確認した。create/removeは明示root/name/base/pathと確認を保ち、previewでGit/targetを変更せず、実remove後もnative branch refのtipを保持する。明示bootstrapのmake initは該当WTだけで実行し、preview/offlineではmakeを評価せず、ファイルを作らない。

後継三casesは3 passed（1.57秒）。現在のnative worktree/remove/bootstrap suiteを合わせた `uv run pytest tests/cli_runtime/test_worktree_commands_vnext.py tests/cli_runtime/test_issue413_worktree.py tests/cli_runtime/test_issue413_worktree_remove.py tests/cli_runtime/test_issue413_worktree_bootstrap.py -q --tb=short` は115 passed（23.83秒）。全source/testsのRuff check/format（423 files）、変更一test限定 `mypy --follow-imports=silent`、diff checkも成功した。tmp fixtureだけを作成/削除しており、実consumer・既存worktree・live GitHubは未変更。旧installation/recoveryとprovider/runtime退役、full type/pytest、native Windows、fresh Strictと最終手動確認を継続する。


## P-12 旧recovery入口の退役診断と低水準保存試験の分離

旧31関数を[対応表](artifacts/test-port-recovery.md)へ保存した。新しい公開matrixでは十二操作×resume/rollbackの24 casesを実行し、project/Git/ghへ到達する前にexit2・ARGUMENT_RETIRED・effects空を返し、既存のopaque証拠とtreeを保全する。永続operation IDやblocking journalを後継へ移植しない。既存atomic JSON八関数とprocess helperは本文を変更せず別integration fileへ移し、低水準の保全条件を保持した。共有native read/rename helpersと旧transaction APIの退役判断はproviderの参照閉包確認に残す。

初回と訂正後の各24失敗はschema名とrecovery fieldのtest期待の誤りだった。確定CLI契約のspecdock.cli/v2・recovery=nullへ訂正し、製品Redには数えない。八既存atomic casesは最初から成功し、訂正後の二filesは32 passed（0.14秒）。`uv run pytest tests/integration/test_cli_recovery_vnext.py tests/integration/test_atomic_json_publication.py tests/cli_runtime/test_issue413_scope_publish.py tests/cli_runtime/test_issue413_scope_import.py tests/cli_runtime/test_issue413_finish.py tests/integration/test_issue413_migration.py -q --tb=short` は148 passed（39.36秒）。ログは既に選択したEpic Workbenchのiss-00413-implementation/pytest-recovery-related.logへ保持する。

全source/tests Ruff check/format（424 files）、変更二test限定mypy --follow-imports=silent、diff checkが成功した。実consumer・Git内の独自領域・live GitHubは未変更。旧installation/handoverとproviderの退役、full type/pytest、native Windows、fresh Strict、最終手動確認を続ける。このcheckpointは旧providerの全退役や全体gateの合格ではない。


## P-12 旧group installation / finalization / engine handover試験の退役

旧四ファイルの54関数（8/7/6/33）を読み、[個別判断](artifacts/test-port-installation-retirement.md)へ保存した。全WT中央control、ready/maintenance、epoch、fixed engine source、journal resume/rollback、whole-group finalizationは新仕様の保証にしない。既存公開assets/通常wheel/provider distribution/退役診断のsuiteへ必要な安全性を対応させ、obsolete fixtureの外部参照が二つの四ファイル内部だけであることを確認して一緒に退役した。pytestの条件除外やskipは増やしていない。製品側の旧source退役は参照閉包の別stepである。

旧試験のsame-content inode差替え条件を公開static操作に移した。native fsync後のbackup directoryを境界に、外部actorが観測済み資産を同bytes/mode・別inodeへ置換する。update一件は1 passed（2.42秒）、uninstallへ広げた二casesは2 passed（4.52秒）だった。既存実装のGreen確認であり、製品Redではない。CLIはpartial/6、backup/restore成功、全変更/退役not_attemptedを返し、actorのファイル・target/Git tree・実backupを保持した。

`uv run pytest tests/integration/test_issue413_assets.py tests/integration/test_cli_entrypoint_vnext.py tests/unit/infra/test_provider_distribution.py tests/integration/test_cli_recovery_vnext.py -q --tb=short` は99 passed（74.91秒）。既存Epic Workbenchのiss-00413-implementation/pytest-installation-retirement.logへ保持する。全source/tests Ruff check/format（420 files）、変更一test限定mypy --follow-imports=silent、diff checkも成功した。限定Greenを全体gateへ読み替えず、provider/runtime旧経路の退役、full type/pytest、native Windows、fresh Strict、最終手動製品確認を継続する。実consumer・既存WT・live GitHubへの適用は行っていない。


## P-12 fixed bundle入口の製品source退役

二つの旧sourceを全文確認し、[関数単位の移行判断](artifacts/provider-retirement-fixed-entrypoints.md)へ残した。普通のspec_dock.cli:mainへ既に統合された旧external preflight/control/locator経路と、bin/libを追加copyするfixed builderを退役する。sourceのinboundは旧builderのlauncher文字列だけで、両moduleを同時に削除した。testの禁止文字列とCI sentinelを実行参照と混同しない。runtime_loaderと旧runtime/application/commandは後続の参照整理へ残す。

実wheelの収録禁止を先に追加し、正常buildのartifactに二つの旧入口が存在するRedを確認した（1 failed/0.80秒）。二source削除後、同じtestは1 passed（14.34秒）。通常wheel/sdist、非editable外部venv、context不要utility、Scope/CI validate、shimとstatic操作を確認する既存受入れ経路を最後まで実行した。既存build_pyがbuild_libのpackageを新しく作り直すため、過去のbuild出力を同梱しない。新除外条件・builder fallbackは追加していない。

`uv run pytest tests/integration/test_cli_entrypoint_vnext.py tests/integration/test_ci_fixed_validation.py tests/unit/infra/test_provider_distribution.py -q --tb=short` は24 passed（13.03秒）。既存Epic Workbenchのiss-00413-implementation/pytest-fixed-entrypoint-retirement.logへ保持。全source/tests Ruff check/format（418 files）、変更wheel test限定mypy --follow-imports=silent、diff checkも成功した。実consumer/live GitHubを変更せず、旧source/README/AGENTSの退役整理、full type/pytest、native Windows/Python3.10、fresh Strictと最終手動確認を継続する。


## P-12 通常全pytestの再確認と最後の旧CLI adapter退役

clean a3844fc35dbc0065b95951d43109a1077a6a45ddで `uv run pytest -q --tb=short` を実行し、2048 passed/1 skipped（369.70秒）、exit0を確認した。以前の79失敗はこのsnapshotで解消した。ログは既存Epic Workbenchのiss-00413-implementation/pytest-p12-a3844fc3.logへ保持した。1 skipは成功件数に含めず、Windows native/別Python/full AC検証の代わりにしない。

同snapshotの通常 `make lint` はexit2。Ruff check/format（418 files）は成功したがmypyは559 errors/63 files（337 source filesを検査）だった。source 166/test 393 errorsで、旧control/dispatcher/applicationとそのprivate fixturesの型不整合が多数を占める。現行経路の型問題も含むため、退役と実際の型修正を行い、限定mypyの成功をfull gateへ読み替えない。元ログはiss-00413-implementation/lint-p12-a3844fc3.logへ保持した。

旧dispatcherをtestから参照する最後の四filesを全文確認し、[十二関数の対応表](artifacts/test-port-remaining-adapters.md)へ保存した。中央registration/group control・new local Scope・旧receiptを後継仕様に残さず、既存公開Dependency/Artifact/Workbench/Static installationの保証へ個別に対応づけて退役した。新しい非Git targetのInstallation show一件はv2/exit5・raw Git argv/stderrと双方tree不変を検査し、1 passed（0.15秒）。既存実装のGreenであり製品Redではない。

`uv run pytest tests/integration/test_issue413_assets.py tests/cli_runtime/test_issue413_dependency.py tests/cli_runtime/test_issue413_artifact.py tests/cli_runtime/test_issue413_workbench.py -q --tb=short` は182 passed（94.98秒）。ログはiss-00413-implementation/pytest-test-retirement-public.logへ保持した。全source/tests Ruff check/format（414 files）、変更assets test限定mypy --follow-imports=silent、diff checkも成功した。旧dispatcherとcommandsのsource側参照閉包整理は別stepとして残す。実consumer・Git内の独自領域・live GitHubは未変更。


## P-12 旧dispatcher / command層の製品退役

旧dispatcherとcommand 17 filesの全文・84 top-level symbolsを読み、[現行保証との対応](artifacts/provider-retirement-dispatcher.md)へ保存した。candidate外のsource/test importはTYPE_CHECKINGとfrom-importの子moduleを含め0だった。残るstatic inventoryのlegacy path/digestは既知旧資産のownership証拠として保持し、実行参照と混同しない。十八moduleを一緒に削除し、fallback/deprecated alias/新wheel除外は加えなかった。

通常wheelの受入れ試験へ十八moduleの明示収録禁止を先行し、正常buildしたartifactに旧codeが存在するRedを検出した（1 failed、0.79秒）。source削除後、同じtestは1 passed（14.41秒）。fresh wheel/sdist同一inventory・isolated console・help/version/completion・static installationと入力保全を検査した。ログは既存Epic Workbenchのiss-00413-implementation/pytest-dispatcher-retirement-{red,green}.logへ保持する。

`uv run pytest tests/integration/test_cli_entrypoint_vnext.py tests/integration/test_cli_recovery_vnext.py tests/integration/test_ci_fixed_validation.py tests/cli_runtime/test_cli_vnext_contract.py tests/unit/infra/test_provider_distribution.py -q --tb=short` は88 passed（13.37秒）。`uv run pytest --collect-only -q` は2038 tests collected（0.41秒）、exit0で旧moduleへのcollection importがない。全source/tests Ruff check/format（396 files）、変更wheel test限定mypy --follow-imports=silent、diff checkも成功。元ログはiss-00413-implementation/pytest-dispatcher-retirement-{related,collection}.logへ保持した。これは再度の全pytest/full mypy合格ではない。

旧application/control/journal/runtime_loaderにはprivate testや現行経路が共有するhelpersが残るため、このcheckpointでは削除しない。正常経路からの共有helpers分離と残るprovider退役、通常型gate、native Windows/別Python、fresh Strict、最終手動確認を続ける。実consumerとlive GitHubは未変更。


## P-12 Scope publicationからの旧writer import分離

公開create/importが旧create_node/create_github_scopeからhelpersを借り、実行しない旧control/WriterLock/journalをimportしていた。[十一helpersのauthority](artifacts/provider-scope-helper-isolation.md)をscope_scaffold.py/scope_ancestors.pyへ移し、現行publisherとscaffold builderは直接importする。元moduleのdefinitionsを削除し、実在する旧private callersも同じauthorityを使う。重複実装・fallback・新local作成・remote効果は加えなかった。

fresh processでpublic Scope create previewを実行し、七退役moduleの読込を実際に検出するRedを確認した（1 failed、0.44秒）。分離後の同testは1 passed（0.32秒）。その後GH import previewを含む二casesへ広げ、2 passed（0.92秒）。createはremote接触0、importは指定Issue GET一回だけで両local tree不変。元ログは既存Epic Workbenchのiss-00413-implementation/pytest-scope-helper-isolation-{red,green}.logに保存した。

移動した九scaffold処理と二親処理のAST本体が元HEADと同一であることを照合した（gatewayのProtocol注釈だけを正規化）。旧moduleに残る64/5 definitions、現行publisher四functions/scaffold builder一functionも不変だった。`uv run pytest tests/cli_runtime/test_issue413_scope_publish.py tests/cli_runtime/test_issue413_scope_import.py tests/cli_runtime/test_scope_github_vnext.py tests/cli_runtime/test_scope_local_vnext.py tests/cli_runtime/test_artifact_vnext.py -q --tb=short` は97 passed（23.72秒）。通常wheel/sdist/isolated consoleは1 passed（15.66秒）。ログはiss-00413-implementation/pytest-scope-helper-isolation-related.log、pytest-scope-helper-wheel.logへ保存した。

全source/tests Ruff check/format（398 files）、新二authority・現行publisher/scaffold/test限定mypy --follow-imports=silentの五files、diff checkが成功した。通常make lintも実行しRuffは成功、mypyは443 errors/49 files（317 source filesを検査）、make exit2で未完了だった。親e9437b74+今回helpers差分のcandidateであり、前回clean a3844fc3の559 errorsとはsnapshotが異なる。logはiss-00413-implementation/lint-p12-e9437b74-helper.logへ保持する。旧private writers/controlの退役、残る型問題、native Windows/別Python、fresh Strict、最終手動確認を続ける。実consumerとlive GitHubは未変更。


## P-12 fixed engine locator / group installationの製品退役

旧三module・48 symbolsの全文と候補内外のimportを確認し、[個別判断](artifacts/provider-retirement-engine-group.md)を保存した。candidate外source/test importはTYPE_CHECKINGを含め0で、閉じた三moduleを一緒に削除した。engine pin、全WT control/epoch、group journal、handover/finalization/resume/rollbackを通常配布から除去し、既存legacy証拠の読取・保全は維持する。互換alias・fallback・build除外は追加していない。

通常wheelへ三moduleの収録禁止を先行し、正常build後に旧codeが存在するRed 1 failed（0.96秒）を確認した。削除後、同じ受入れ試験は1 passed（14.12秒）。fresh wheel/sdist/外部非editable venv/実console/局所static操作とtree保全を検査した。公開assets/entrypoint/provider/retired-recoveryの関連100 tests（72.84秒）も成功。元ログは既存Epic Workbenchのiss-00413-implementation/pytest-engine-retirement-{red,green,related}.logへ保持した。

全source/tests Ruff check/format（395 files）、変更wheel test限定mypy --follow-imports=silent、diff checkが成功した。直近通常make lintの443 errors/49 filesは未合格のままで、この限定検証をfull gateへ読み替えない。旧private writers/journal/registry/shared helpersの参照整理、残る型問題、native Windows/別Python、fresh Strict、最終手動確認を続ける。実consumer・既存WT・旧Git領域・live GitHubは未変更。


## P-12 Scope完了判定の旧writer分離

現行close/reopenのpure plan七symbolsを[小moduleへ分離](artifacts/provider-scope-completion-isolation.md)し、旧control/WriterLock/journalを現行経路からimportしないようにした。移動七nodes、旧moduleに残る七nodes、現行adapterの四functionsはAST本体が元HEADと同一。旧private callersも同じauthorityを使い、三階層/既存codec/選択/checkoutの契約を変えない。

fresh processの公開close previewは旧六modules読込でRed 1 failed（0.61秒）、分離後の同testはGreen 1 passed（0.58秒）。reopenへ広げた二casesは2 passed（0.94秒）。GH GET一回だけ、v2/planned、tree不変を確認した。関連old lifecycle/current lifecycle/Finishの76 tests（22.00秒）、通常wheel一test（13.60秒）、全Ruff check/format（396 files）、変更三files限定mypy --follow-imports=silentとdiff checkも成功。元ログは既存Epic Workbenchのiss-00413-implementation/pytest-completion-isolation-{red,green,related,wheel}.logへ保存した。

通常全体lintは直近443 errors/49 filesで未合格のまま。通常source rootsの保守的AST closureは88 modules、未到達96 modulesだが、これだけを一括削除の根拠にしない。old writer/private testsの個別対応と製品参照確認、残る型問題、native Windows/別Python、fresh Strict、最終手動検証を継続する。実consumer/live GitHubは未変更。


## P-12 参照を失った旧入口・facade・派生保存adapterの退役

旧21 modules・136 top-level関数/classの全文と[個別責務](artifacts/provider-retirement-unused-entrypoints.md)を確認して削除した。AST importに加えてsource/tests/setup/pyproject/scripts/CIの文字列参照を検査し、候補外import 0・内部deps→ids一件だけを確認。未使用に見えたgit_helperは旧git_cliのpython -m呼出しがあったため保持した。現在の三階層/ID codec/業務/safetyと、明示操作の後継を照合し、中央control/cache/派生保存/復旧receiptを温存しない。

通常wheelは先行した収録禁止でRed 1 failed（0.75秒）、削除後の同testはGreen 1 passed（13.38秒）。通常collectionは2042 tests（0.38秒）、関連公開CLI/entrypoint/Doctor/Sync/依存/Workbenchは222 tests（36.58秒）が成功した。通常make lintはRuff成功・mypy 407 errors/45 files（294 source files）、exit2で未合格。source 58/test 349 errorsを個別に整理・修正する。変更wheel test限定mypyとdiff checkも成功。元ログは既存Epic Workbenchのiss-00413-implementation/pytest-unused-entrypoints-{red,green,collection,related}.log、lint-p12-c633-retirement.logへ保存した。

通常全pytestの再合格、full type gate、native Windows/別Python、fresh Strict、最終手動検証は未完了である。実consumer・既存WT・旧Git領域・live GitHubは未変更。


## P-12 新規local Scope作成試験の退役

旧local createの十二test関数と二helpersを全文確認し、[保証別の判断](artifacts/test-port-local-scope-retirement.md)で退役した。候補外helper importは0。独自local採番/high-water/cache/offline createの成功条件を残さず、GH番号SSOTと既存local metadata保全を維持する。親差替えsafetyはpublic main/native Git/stateful gh/OS fsyncの境界へ移し、replacement tree不変・元metadata/ref保全・partial/6を二casesで確認した（2 passed、1.15秒）。最初のnot_attempted期待はstage開始済みを反映したfailedへ訂正し、製品Redには数えない。

関連current publication/import/create/query/lifecycle/migrationの128 tests（38.34秒）、全Ruff check/format（374 files）、変更publication test限定mypy --follow-imports=silentとdiff checkが成功した。最初の存在しない二test file指定はexit4/zero testsで、実在fileへ訂正した結果だけを回帰証拠にする。元ログは既存Epic Workbenchのiss-00413-implementation/pytest-local-creation-retirement-related.log（中断）とpytest-local-creation-retirement-related-2.log（成功）へ保持した。全体lintは直近407 errorsで未合格のまま。旧source/private writersの整理、full gates、native Windows/別Python、fresh Strict、最終手動確認を継続する。実consumer/live GitHubは未変更。


## P-12 Scope照会・タイトル編集試験の公開CLI移行

旧三testを[公開CLIの保証へ置換](artifacts/test-port-scope-query-edit.md)した。既存local/GH metadataのkind/state/query、直接recordの@current、旧cache非採用、title/revision以外の未知field・仕様bytes・既存mode保存、同title noopを確認する。新local作成/control付きfixtureを残さず、gh request 0・effects空・tree保全を公開main/native境界で検査した。一件ずつ1 passed（0.34/0.24/0.34秒）で、既存Greenのcharacterizationであり製品Redではない。

参照を失った旧edit_scope.pyの二symbolsを全文・source/test import確認のうえ退役した。通常wheelの収録禁止はRed 1 failed（0.77秒）、source削除後の同testはGreen 1 passed（13.37秒）。関連query/edit/create/契約40 tests（6.23秒）、全Ruff check/format（373 files）、変更二test限定mypyとdiff checkも成功。元logは既存Epic Workbenchのiss-00413-implementation/pytest-scope-query-port.log、pytest-scope-query-source-{red,green}.log、pytest-scope-query-port-related.logへ保持する。

直近通常lintの407 errors/full gate・native Windows/別Python/fresh Strict・最終手動確認は未完了である。旧作業/Scope/private writersの整理を続ける。実consumer/live GitHubは未変更。


## P-12 旧Start/Finish試験・writerの退役

旧二filesの29 test関数・1002行と旧work_lifecycle.pyの26 symbols・1175行を全文確認し、[保証別の個別判断](artifacts/test-port-work-lifecycle-retirement.md)を残した。candidate外importはTYPE_CHECKING/from-import子moduleを含め0。暗黙祖先switch/Finish後の親昇格/registry/epoch/journal/cache resumeを廃止し、必要な保証は公開main/native Git/stateful ghへ対応づけた。skip/収集除外は増やさない。

新しい公開試験では、子だけのFinishが直接選択中の祖先を保持（1 passed/0.75秒）、既存local親がGH子のopenを拒否しlive completed後に親だけを完了・capture解除（1 passed/0.67秒）、親子どちら向きのStartも明示switch必須（2 passed/1.12秒）、candidate graphでの明示branch readiness（1 passed/0.82秒）、三kind×attached/detachedのbase必須とdetached明示開始（6 passed/2.96秒）を検査した。現行Greenのcharacterizationである。parametrizationのcollection誤りとreadonly GETも0とした過剰期待は訂正し、元失敗logを保持した。

通常wheelの旧writer収録禁止はRed 1 failed（1.11秒）、source削除後の同testはGreen 1 passed（14.59秒）。関連Start/Finish/Active/lifecycle/native並行Startは187 tests（66.63秒）が成功し、その後base六casesをfocused実行した。全Ruff check/format（370 files）、変更三test限定mypyとdiff checkも成功。元logは既存Epic Workbenchのiss-00413-implementation/pytest-work-lifecycle-port.log、pytest-work-start-candidate-readiness.log、pytest-work-lifecycle-source-{red,green}.log、pytest-work-lifecycle-retirement-related.logへ保持する。

旧source/private helpersの残り、通常full type/pytest、native Windows/別Python、fresh Strict、最終手動確認は継続中である。直近通常lintの407 errorsは別snapshotの未合格記録で、今回の限定成功で置換しない。実consumer/live GitHubは未変更。


## P-12 旧Scope lifecycle試験・writerの退役

旧八test・一fixture class（303行）と旧scope_completion.pyの七symbols（494行）を全文確認し、[個別対応](artifacts/test-port-scope-lifecycle-retirement.md)を保存した。pure completion planの本体を維持し、最後のScope delete helper importだけをauthorityへ向けた。一importのmodule field以外、全ASTは元HEADと同一で、退役二fileへのsource/test importはTYPE_CHECKING/子moduleを含め0。skip/収集除外を増やさない。

公開Close/Reopenの子/祖先三状態guardは六casesで6 passed（2.24秒）、terminal reason conflictは1 passed（0.46秒）、既存local noop/任意field/metadata/record/tree保全は1 passed（0.37秒）だった。collection parametrization誤りとnoop effectsの過剰な空期待を訂正し、失敗logも保持した。現行Greenのcharacterizationであり製品Redではない。

通常wheelの旧writer収録禁止はRed 1 failed（0.76秒）、source削除後の同testはGreen 1 passed（13.71秒）。関連Scope lifecycle/Finish/旧・現行Scope deleteの115 tests（34.01秒）、全Ruff check/format（368 files）、変更二test限定mypyとdiff checkも成功。元logは既存Epic Workbenchのiss-00413-implementation/pytest-scope-lifecycle-port.log、pytest-scope-lifecycle-source-{red,green}.log、pytest-scope-lifecycle-retirement.logへ保持する。

このunit前のclean 0c04677bada135dbb50ea0c48f7fc3b4aae368c9の通常make lintはRuff成功・mypy 313 errors/40 files（289 source files）、source 54/test 259 errors、make exit2で未合格だった。元logはiss-00413-implementation/lint-p12-0c04677b.logへ保持。旧407 errorsとはsnapshotが異なる。残る旧private writersの整理と現行型問題、full gates、native Windows/別Python、fresh Strict、最終手動確認を継続する。実consumer/live GitHubは未変更。

## P-12 旧Worktree試験・writerの退役

旧Worktree create/bootstrap/remove三filesの20 test関数・433行と、旧二writerの28 symbols・809行を全文確認し、[個別対応](artifacts/test-port-worktree-retirement.md)を保存した。明示NAME/base/path・Git inventory・branch/payload保全・明示makeと出力省略を公開CLIへ対応づけ、control/epoch/registry/receipt/recover/Start以外の共通排他を廃止した。まだ旧callerを持つworktree_target.pyはこのunitで削除しない。退役五filesへのsource/test importはTYPE_CHECKING/子moduleを含め0。skip/収集除外を増やさない。

新しい公開保証は元選択保持1 passed（0.50秒）、detached base1 passed（0.49秒）、base/path/branch拒否3 passed（0.39秒）、成功hookの大出力省略1 passed（0.26秒）、欠落/non-native target2 passed（0.30秒）。現行Greenのcharacterizationである。欠落pathをexit5とした初期期待はv2のLOCAL_TARGET_NOT_FOUND/exit4へ訂正し、失敗logを保持した。

通常wheelの収録禁止はRed 1 failed（0.78秒）、source削除後の同testはGreen 1 passed（13.87秒）。関連Worktree/native Git観測124 tests（23.14秒）、全Ruff check/format（363 files）、変更三test限定mypyとdiff checkも成功。元logは既存Epic Workbenchのiss-00413-implementation/pytest-worktree-retirement-port.log、pytest-worktree-retirement-source-{red,green}.log、pytest-worktree-retirement-related.logへ保持する。

直近通常lintの313 errors/full gate、残る旧source/private helpers、native OS/別Python、fresh Strict、最終手動確認は未完了である。実consumer/live GitHubは未変更。

## P-12 旧Active・branch・Scope deleteの退役

旧Active/branch/Scope deleteの三test files（28 test関数・815行）と三writer（53 symbols・1400行）を全文確認し、[個別判断](artifacts/test-port-selection-retirement.md)を保存した。dirty/候補graph/他WT占有、metadata/直接record/branch/backup保全を公開CLIへ対応づけた。親自動昇格・from-branch取得・永久binding・local ID tombstone・共通WriterLock・operation journal/recoveryを廃止する。退役六filesへのsource/test importはTYPE_CHECKING/子moduleを含め0。skip/収集除外を増やさない。

新しい公開保証は既存ref/非ASCII拒否2 passed（0.30秒）、tracked/untracked拒否2 passed（0.49秒）、Scopeを失った候補refの切替拒否1 passed（0.31秒）、tracked subtreeのbackup/元branch/checkout/GH保全1 passed（0.39秒）。既存Greenのcharacterizationである。

通常wheel収録禁止はRed 1 failed（0.80秒）、source退役後の同testはGreen 1 passed（15.49秒）。関連Active/branch/Scope delete/Finish148 tests（34.11秒）、全Ruff check/format（357 files）、変更三test限定mypyとdiff checkも成功。元logは既存Epic Workbenchのiss-00413-implementation/pytest-selection-retirement-port.log、pytest-selection-retirement-source-{red,green}.log、pytest-selection-retirement-related.logへ保持。

直近通常lintの313 errorsは別snapshotの未合格記録である。残る旧Source/tests、現行型問題、full gates、native OS/別Python、fresh Strict、最終手動確認を継続する。実consumer/live GitHubは未変更。

## P-12 通常型gateと現行試験の型補正

clean `2c45e885ca48c32616d4899ee79844c553d96dc5` の通常 `make lint` はRuff成功、mypy 189 errors/32 files（276 source files）、make exit2で未合格だった。元logは既存Epic Workbenchの `iss-00413-implementation/lint-p12-2c45e885.log` に保持した。313 errorsは旧snapshotの記録である。

現行のGit診断・Windows外部API fixture・branch adapter・legacy doctor・migrationの五test filesについて29件の型問題を補正した。Git診断のdict形状をassertし、空list/JSON payloadの型、bytes refとtree digestの変数を区別した。migrationの障害注入callbackは実際のbackup/context/OS replaceの引数と返値へ揃え、検証条件と障害時機を保持した。ignore/cast/skip/収集除外を増やさず、製品sourceやconsumer状態は変更しない。

五suiteは108 passed（18.48秒）、全source/tests Ruff check/format（357 files）、変更五test限定mypy `--follow-imports=silent` とdiff checkが成功した。元logは `iss-00413-implementation/pytest-current-test-types.log`。これは既存試験の型補正であり、新機能Red→Green、Windows native、通常full gate、fresh Strictの合格ではない。残る旧実装の個別退役と全体検証を続ける。

## P-12 旧dependency writer・試験の退役

旧七test関数・二helpers（218行）と旧application/dependency_vnext.pyの十symbols（235行）を全文確認し、[個別対応](artifacts/test-port-dependency-retirement.md)を保存した。宣言/継承・循環・未知field/mode・直接record保全・必要対象だけのlive観測を公開CLIへ対応づける。control/epoch・共通WriterLock・旧selection/cache/stale opt-inのadapterを削除し、現行pure domainとraw snapshot helperは維持する。退役二filesへのsource/test importはTYPE_CHECKING/子moduleを含め0。skip/収集除外を増やさない。

公開確認は三kind×三kind 9 passed（2.02秒）、duplicate add全tree保全1 passed（0.37秒）、cross-tree継承/親完了待ちcycle 2 passed（0.57秒）、子の依存/完了を親と混同しないreadiness 2 passed（0.28秒）。既存Greenのcharacterizationである。

通常wheelの収録禁止はRed 1 failed（0.77秒）、source退役後の同testはGreen 1 passed（14.01秒）。関連dependency/Start/Scope delete/pure domain 188 tests（48.28秒）、全Ruff check/format（355 files）、変更二test限定mypyとdiff checkが成功した。元logは既存Epic Workbenchのiss-00413-implementation/pytest-dependency-retirement-port.log、pytest-dependency-retirement-source-{red,green}.log、pytest-dependency-retirement-related.logへ保持。

直近通常lintの189 errorsはclean 2c45e885の別snapshotである。残る旧source/private helpers、通常full gates、native OS/別Python、fresh Strict、最終手動確認を継続する。実consumer/live GitHubは未変更。

## P-12 旧Artifact writer・試験の退役

旧五test関数（111行）と旧application/artifact_vnext.py（152行・六関数/classと一type alias）を全文確認し、[個別対応](artifacts/test-port-artifact-retirement.md)を保存した。mixed catalog、本文非読取、重複slot拒否、六template、既存local/root、metadata/資料/privacy保全を公開CLIへ対応づけ、control/epoch・共通WriterLock・三段旧activeのadapterを削除した。現行artifact_queryと局所publicationは維持する。退役二filesへのsource/test importはTYPE_CHECKING/子moduleを含め0。skip/収集除外を増やさない。

追加確認はmixed catalog本文open 0で1 passed（0.23秒）、root/Scope重複slotと全tree保全2 passed（0.37秒）、既存local Initiativeの六type・metadata/仕様/mode/ref保全6 passed（1.45秒）。既存Greenのcharacterizationである。最初の本文open拒否を試験側digestまで延長したharness失敗1 failed（0.31秒）はCLIのcontextへ限定して訂正し、元logを保持した。

通常wheelの収録禁止はRed 1 failed（0.77秒）、source退役後の同testはGreen 1 passed（14.08秒）。Artifact/Grill finalizer/domain/templateの関連141 tests（8.89秒）、全Ruff check/format（353 files）、変更二test限定mypyとdiff checkが成功。元logは既存Epic Workbenchのiss-00413-implementation/pytest-artifact-retirement-port.log、pytest-artifact-retirement-source-{red,green}.log、pytest-artifact-retirement-related.logへ保持。

このunit前のclean 82240b58の通常make lintはRuff成功・mypy 95 errors/26 files（274 source files）、source 47/test 48 errors、make exit2で未合格。元logはiss-00413-implementation/lint-p12-82240b58.log。旧189 errorsとはsnapshotが異なる。残る旧source/tests、通常full gates、native OS/別Python、fresh Strict、最終手動確認を継続する。実consumer/live GitHubは未変更。

## P-12 旧Scope発行・取り込み・復旧の退役

**旧Scope発行・取り込み・復旧の退役**

旧十九test関数（698行）と旧五source files（1478行・27 symbols）を全文確認し、[個別対応](artifacts/test-port-scope-github-retirement.md)を保存した。GitHub番号、三階層、live open親、明示title/ref、GET-only import、効果と既存資料保全を公開CLIへ対応づける。新規local採番・marker・control/epoch・共通WriterLock・registry/tombstone・永続journal/resumeを除去した。pure github_scope_scaffold/scope_ancestors/scope_scaffoldと既存local codecは維持する。候補外source/test importはTYPE_CHECKING/子moduleを含め0。skip/収集除外を増やさない。

追加確認は階層import 2 passed（1.47秒）、terminal親/祖先のPOST前拒否6 passed（2.49秒）、GET後競合と新しい明示import 1 passed（0.88秒）、確定拒否のfailed/5・一POST・ID未発行3 passed（1.37秒）。既存Greenのcharacterizationである。最初の衝突fixtureを起動前から不正Scope pathにした期待誤り1 failed（0.20秒）は、確認済みGET中の競合を測るよう訂正し、失敗logも保持した。

通常wheelの五旧module収録禁止はRed 1 failed（0.76秒）、source/test退役後の同testはGreen 1 passed（13.82秒）。関連Scope create/import/GitHub gateway五suiteは99 passed（27.76秒）。全Ruff check/format（347 files）、変更三test限定mypyとdiff checkが成功した。元logは既存Epic Workbenchのiss-00413-implementation/pytest-scope-github-retirement-port.log、pytest-scope-github-retirement-source-{red,green}.log、pytest-scope-github-retirement-related.logに保持する。

95 errorsの通常lintはclean 82240b58の別snapshotであり、現在値としない。残る旧helpers、通常full gates、native OS/別Python、fresh Strict、最終手動確認を継続する。実consumer/live GitHubは未変更。

## P-12 GitHubの旧マーカー検索の退役

**GitHubの旧マーカー検索の退役**

[個別対応](artifacts/test-port-github-marker-retirement.md)に従い、最後の旧writer退役後にcallerを失ったGithubIssueGateway.find_by_markerと二private試験を削除した。全Issueページ走査/marker検索を現行writerへ移さない。専用array decoder optionを除去し、GET/POST/PATCHの単一Issue object返値を明確にした。repository/record/HTTP分類/完了処理のASTと元の残る13 test関数は同一で、skip/収集除外を増やさない。

array応答のGET/5・create unknown/6・再送なしを旧sourceで先に2 passed（0.03秒）、refactor後の同testも2 passed（0.03秒）で確認した。既存Greenのcharacterization/refactorであり、製品Redではない。POST endpointの初期期待をargv末尾としたfixture誤り1 passed/1 failed（0.04秒）は正しい--method後の位置へ訂正し、失敗logを保持した。関連七suiteは131 passed（40.62秒）、work finishは33 passed（11.93秒）、全Ruff check/format（347 files）・変更source/test限定mypy・diff/AST検査が成功。元logは既存Epic Workbenchのiss-00413-implementation/pytest-github-marker-retirement-{before,after,related}.logに保持。

このunit前のclean d7f47fc0の通常make lintはRuff成功・mypy 55 errors/19 files（266 source files）、source 40/test 15 errors、make exit2で未合格。元logはiss-00413-implementation/lint-p12-d7f47fc0.log。旧95 errorsとは別snapshotであり、残る旧helpers、full gates、native OS/別Python、fresh Strict、最終手動確認を継続する。実consumer/live GitHubは未変更。

## P-12 旧migration・共通writer admissionの退役

**旧migration・共通writer admissionの退役**

旧二test filesの22 test関数・920行と旧五source filesの52 symbols・1505行を全文確認し、[個別対応](artifacts/test-port-migration-retirement.md)を保存した。schema1変換、全WT登録/control/epoch/branch binding/local ID予約、UUID journal/resume/rollbackを廃止した。現schema3 bytes、current一宣言の切替、外部実backup/restore、途中user edit拒否、他WT/Git/旧activeの保全を公開CLIへ対応づける。現domain/writer_admission、migration_backup、legacy_reader、current writerは保持する。候補外source/test importはTYPE_CHECKING/子moduleを含め0。skip/収集除外を増やさない。

追加確認は不正metadata/旧active四casesで4 passed（0.46秒）、scoped Workbenchのopaque metadata/外部link保全で1 passed（0.25秒）。既存Greenのcharacterizationである。通常wheelの旧五module実収録禁止はRed 1 failed（0.82秒）、source/test退役後の同testはGreen 1 passed（14.40秒）。関連migration/doctor/validate/公開adapter四suiteは159 passed（23.91秒）。初回関連suiteの旧filename誤指定はpytest exit4、0 tests（0.00秒）で、実inventory確認後に訂正し元logを保持した。製品Redに数えない。

全Ruff check/format（340 files）、変更二test限定mypyとdiff checkが成功。元logは既存Epic Workbenchのiss-00413-implementation/pytest-migration-retirement-port.log、pytest-migration-retirement-source-{red,green}.log、pytest-migration-retirement-related.logへ保持。55 errorsの通常lintはclean d7f47fc0の別snapshotであり、残る旧helpers、full gates、native OS/別Python、fresh Strict、最終手動確認を継続する。実consumer/live GitHubは未変更。

## P-12 旧control・registry・writer lock helpersの退役

**旧control・registry・writer lock helpersの退役**

旧七source filesの1002行・38 top-level symbolsを全文確認し、[対応記録](artifacts/test-port-control-retirement.md)を保存した。絶対／相対／TYPE_CHECKING／子moduleを含む候補外importは0。Git共通領域のcontrol/epoch/engine登録、local採番予約・永久branch binding、operation/handover/finalization journal、全writer lock file／WT lifetime leaseを削除した。current Startだけの排他、直接選択・捕捉token解除、現schema/protocol検査、readonly legacy診断は維持する。旧Git内データと別packageのgroup journalはこのunitで変更しない。

通常wheelの旧七module収録禁止はRed 1 failed（0.90秒）、退役後の同testはGreen 1 passed（16.52秒）。Start/lock options/Doctor/別process競合・kill/migration/static assets七suiteは259 passed（120.89秒）、exit0。全Ruff check/format（333 files）・変更test限定mypy・diff checkが成功。既存test削除0、skip/収集除外追加0。元logは既存Epic Workbenchのiss-00413-implementation/pytest-control-retirement-source-{red,green}.logとpytest-control-retirement-related.logへ保持。残る旧source、通常full gates、native OS/別Python、fresh Strict、最終手動確認を継続する。実consumer/live GitHubは未変更。

## P-12 旧domain台帳・復旧契約の退役

**旧domain台帳・復旧契約の退役**

旧四source filesの435行・14 top-level symbolsを全文確認し、[対応記録](artifacts/test-port-domain-retirement.md)を保存した。local採番予約、高水位/tombstone/永久branch binding、UUID付き操作計画・epoch/engine/revision固定・intent再送/resumeの型とexecutorを削除した。候補外importは絶対／相対／TYPE_CHECKING／子moduleを含め0。既存ID/selector codec、current Git branch検査、今回操作のeffects/partial/unknown、readonly legacy診断は維持する。

通常wheelの旧四module収録禁止はRed 1 failed（0.73秒、exit1）、退役後の同testはGreen 1 passed（15.02秒、exit0）。公開Scope create/import/lifecycle/branch/recovery argument拒否の五suiteは156 passed（47.47秒）、exit0。全Ruff check/format（329 files）・変更test限定mypy・diff checkが成功。既存test削除0、skip/収集除外追加0。元logは既存Epic Workbenchのiss-00413-implementation/pytest-domain-retirement-source-{red,green}.logとpytest-domain-retirement-related.logへ保持。残る旧installation等、通常full gates、native OS/別Python、fresh Strict、最終手動確認を継続する。実consumer/live GitHubは未変更。

## P-12 旧fixed-source installer・journal・復旧executorの退役

**旧fixed-source installer・journal・復旧executorの退役**

旧五source filesの1750行・58 symbolsと旧三test filesの1378行・56 test関数を全文確認し、[個別対応](artifacts/test-port-fixed-installer-retirement.md)を保存した。package/相対/TYPE_CHECKING/子moduleを含む候補外importは0。固定GitHub sourceのtag/commit/archive取得、engine candidate照合、group/child UUID journal、recovery area/ignore marker、全root交換とresume/rollbackを削除した。current static manifest/bytes検査、明示一WT、外部実backup/restore、個別file公開・unknown/partial、user仕様/選択/未知file/Git保全は維持する。旧backup子inodeのrollback所有認証と現行root identity/bytes検査を同じ保証と主張しない。

公開CLIにhardlink拒否四case（4 passed、8.10秒）、候補hardlink化（1 passed、2.41秒）、asset/backup same-inode edit（2 passed、4.56秒）、実ZIP package bytes改変拒否（1 passed、0.20秒）を追加した。既存Greenのcharacterizationである。通常wheelの旧五module収録禁止はRed 1 failed（0.80秒、exit1）、退役後の同testはGreen 1 passed（14.77秒、exit0）。関連五suiteは208 passed（97.97秒）、exit0。後から追加したZIP改変一caseは別focused runであり、この208へ加算しない。全Ruff check/format（321 files）・変更二test限定mypy・diff checkが成功。skip/収集除外追加0。元logは既存Epic Workbenchのiss-00413-implementation/pytest-installation-retirement-{port,source-red,source-green,related}.logへ保持。残る旧helpers、通常full gates、native OS/別Python、fresh Strict、最終手動確認を継続する。実consumer/live GitHubは未変更。

## P-12 公開v2出力と維持する実file試験の型整合

**公開v2出力と維持する実file試験の型整合**

旧v1出力を固定していた七test関数は、同じ名前のまま公開v2・直接一件のActiveData・operation IDなし・can_resume/can_rollback=falseの案内へ更新した。成功/unknown効果をtop-levelで隠せない検査、stderr、秘密値秘匿、現行CLI補完を保持する。[対応記録](artifacts/test-port-public-output.md)へ記録した。既存local lifecycleはLocalBackendを実際に確認してからstateを検査する。原子的JSONの別process kill試験は保持し、代入するOS callbackのkeyword契約だけを合わせた。production変更0、test削除0、skip追加0。

clean e1397459の通常make lintはRuff成功・mypy 41 errors/16 files（240 source files）、make exit2。限定mypyはMYPYPATH未指定だとsource importを解決せず0と表示したが、MYPYPATH=srcを明示すると対象三filesの3 errorsを再現した。修正後は同条件で0、関連三suite 43 passed（0.13秒）、Ruff check/format・diff checkが成功。最初の型注釈importをfuture annotationsなしで追加したcollection error（0.09秒）はharness修正として別logを保持し、製品Redに数えない。元logsはiss-00413-implementation/lint-p12-e1397459.log、pytest-retained-output-type.log（collection error）、pytest-retained-output-type-2.log（成功）。通常full gate、旧helpers、native OS/別Python、fresh Strictは継続中。実consumer/live GitHubは未変更。

## P-12 旧target resolver・補完rendererの退役

**旧target resolver・補完rendererの退役**

旧二source filesの246行・10 symbolsと旧二test filesの185行・12 test関数を全文確認し、[個別対応](artifacts/test-port-target-resolver-retirement.md)を保存した。候補外importは0。旧三role保存snapshotとregistry ID/aliasを削除し、current tree/direct/guard/native inventory/外部shimのargv/cwdを維持する。補完は公開cli/optionsへ統一する。旧consumer静的資産の退役hash/pathは保持する。

公開project context/完全GH linkageの八caseを退役前に8 passed（0.60秒）、exit0で確認した。診断codeのfixture誤りによる初回3 failed/5 passed（0.62秒）はSCOPE_NOT_FOUNDへ訂正し、製品Redに数えない。通常wheelの旧二module収録禁止はRed 1 failed（0.77秒、exit1）→Green 1 passed（13.53秒、exit0）。関連七suiteは169 passed（18.55秒）、exit0。全Ruff check/format（317 files）、MYPYPATH=srcを明示した変更二test限定mypyとdiff checkが成功した。skip/収集除外追加0、旧helper以外のproduction変更0。元logsはiss-00413-implementation/pytest-resolve-retirement-{before,before-2,source-red,source-green,related}.log。残る旧helpers、通常full gates、native OS/別Python、fresh Strict、最終手動確認を継続する。実consumer/live GitHubは未変更。

## P-12 標準text表示と現行開発手順の整合

**標準text表示と現行開発手順の整合**

[C-01/C-04の表示不足](artifacts/public-text-output.md)を公開Scope/Activeと診断の三testで再現した（Red 3 failed/21 deselected、0.22秒、exit1）。typed dataを既存の秘匿処理後に表示する修正で同三testがGreen（3 passed/21 deselected、0.22秒、exit0）となり、関連九suite 176 passed（42.57秒）が成功した。JSON v2、既存Sync/依存表示、raw Git stderrは維持し、永続状態や書込を追加しない。

AGENTS.mdの実装path、現在選択の取得、通常wheel、独立consumerでの検証を現構成へ更新した。既存二suite 236 passed（2.37秒）、全source/tests Ruff check/format（317 files）、MYPYPATH=srcの変更三Python file限定mypyとdiff checkが成功した。通常wheel hash 97378c2ab1a8a9d88f23c926a0a2c7b0009b267ca355f19a5b439a552830538bを再照合し、provider外の非editable実consoleで五read-onlyコマンドの表示/JSON/全tree不変を確認した（0.66秒、exit0）。一時fixtureは削除済み。選択recordはtest準備であり、実Start/実dogfood適用ではない。初回確認scriptのcurrent_branch項目名誤りは別logへ保持した。

この変更前のclean 32c372e1で通常全pytestは1878 passed/1 skipped（340.17秒、exit0）。skip理由は元実行で収集していない。通常make lintはRuff成功・mypy 37 errors/12旧source files（236 source files）、make exit2で未合格。旧helpersの退役、full gates、native OS/別Python、fresh Strict、最終手動確認を継続する。実consumer/live GitHubは未変更。

## P-12 旧generation・状態cache・cache付きGit snapshotの退役

**旧generation・状態cache・cache付きGit snapshotの退役**

旧三source files（299行・11 symbols）と旧generation三test関数（60行）を全文確認し、[個別対応](artifacts/test-port-generated-state-retirement.md)を保存した。候補外importは絶対／相対／TYPE_CHECKING／子moduleを含め0。UUID付き世代/manifest/current pointerの公開・saved OPENの採用・cacheを混ぜる一時Git snapshotを削除した。通常Syncの必要時観測、unknown/partial、直接record、固定HEAD/候補OIDの読取と旧証拠保全を維持する。旧consumerのpath/hash inventoryは変更しない。

旧generation pointerが正常/不正でも旧filesと直接recordを全tree保全し、現在のlocal Syncだけを表示する二caseを退役前に確認した（2 passed/24 deselected、0.49秒、exit0）。既存Greenのcharacterizationである。通常wheelの旧三module収録禁止はRed 1 failed（0.71秒、exit1）→同test Green 1 passed（13.55秒、exit0）。関連Sync/Validate/Doctor/query/Start/wheelの六suiteは231 passed（65.73秒）、exit0。全Ruff check/format（313 files）、MYPYPATH=srcの変更二test限定mypy、diff checkが成功した。skip/収集除外を増やさない。旧generationのatomic pointer/rollback保証を新しい機能として温存しない。

元logsは既存Epic Workbenchのiss-00413-implementation/pytest-generated-state-retirement-{before,source-red,source-green,related}.logへ保持した。37 errorsの通常lintはclean 32c372e1の別snapshotである。残る旧source/tests、full gates、native OS/別Python、fresh Strict、最終手動確認を継続する。実consumer/live GitHubは未変更。

## P-12 旧三段Active保存・投影adapterの退役

**旧三段Active保存・投影adapterの退役**

旧infra/active_store.py（645行・29 functions）と旧二test files（1067行・18 test関数）を全文確認し、[個別対応](artifacts/test-port-active-projection-retirement.md)を保存した。候補外importは絶対／相対／TYPE_CHECKING／子moduleを含め0。固定active.jsonへの三段保存、旧manifest自動採用/.work prune、symlink/path/context-pack投影、index/tree patch、全体snapshot/restoreを削除した。直接一件/現存祖先、捕捉tokenだけの解除、legacy資料の安全な観測と保全は維持する。application/set_active等の残る旧graphは別の退役対象であり、このunitで全て削除したとは扱わない。

公開unchangedの四selectorと、旧manifest/projection/cache/不正directory/hardlink保全の二caseは退役前に6 passed/38 deselected（0.53秒）、exit0。通常wheelの旧module収録禁止はRed 1 failed（0.73秒、exit1）→同test Green 1 passed（14.47秒、exit0）。関連Active/record/Finish/native kill/Sync/Doctor/wheel七suiteは185 passed（49.75秒）、exit0。後から追加した現record hardlinkのSet/Clear拒否は別runで2 passed/44 deselected（0.25秒）、exit0であり、この185に加算しない。全Ruff check/format（310 files）、MYPYPATH=srcの変更二test限定mypy、diff checkが成功した。skip/収集除外を増やさない。

通常make lintはこのunitのPython差分を適用したc93100ba基準でRuff成功・mypy 32 errors/11旧source files（229 source files）、make exit2。37 errorsはclean 32c372e1の旧snapshotである。元logsは既存Epic Workbenchのiss-00413-implementation/pytest-old-active-infra-retirement-{before,source-red,source-green,related}.log、pytest-old-active-infra-hardlink.log、lint-p12-old-active-infra.logへ保持した。残る旧source/tests、full gates、native OS/別Python、fresh Strict、最終手動確認を継続する。実consumer/live GitHubは未変更。

## P-12 Validateの必須Scope文書検査の維持

**Validateの必須Scope文書検査の維持**

旧構造検査を照合し、現行経路が四canonical文書の欠落を見逃す差異を[記録](artifacts/validation-required-documents.md)した。公開CLIのRed 28 failed/2 passed（4.40秒、exit1）を、guarded descriptorで名前/通常fileだけを検査する修正でGreen 30 passed（4.44秒、exit0）にした。固定HEADでもmetadata以外の本文を取得せず、本文・承認・計画レベルをgateにしない。Doctorと明示移行前の構造検査にも接続し、旧validate source/testsはこのunitでは削除しない。

共有fixtureを完全なScope構造に揃えた。通常全pytestの初回は1863 passed/3 failed/1 skipped（355.05秒、exit1）。増えた文書に伴う三削除途中の一覧期待値を修正し、240件移行fixtureと合わせ4 passed、Validate/Scope Delete全二suiteは117 passed（16.52秒、exit0）。限定mypyは変更10 Python filesで成功し、全Ruff（311 files）も成功。通常make lintの旧graph 32 errors/11 filesと、修正後の通常全pytest再実行、native OS/別Python、fresh Strict、最終手動確認は未完了であり、部分成功をfull gate合格にしない。CLI help・配布reference・一行のstatic hashを更新し、実consumer/live GitHubは未変更。

## P-12 対応下限Pythonの予備検証

[Python 3.10互換性の記録](artifacts/python-compatibility.md)を保存した。実3.10.15の隔離venvとprovider import元を照合し、全pytestの初回1864 passed/2 failed/1 skipped（380.34秒、exit1）を切り分けた。spawn時に確認用runnerがpytestを再実行する不具合と、Path.statのaccessor差によるLinux模擬の不達を修正した。製品source、既存assertions、kill境界、test選択とskip条件は維持する。runnerだけの修正後も一件のfixture失敗が再現したことを別logへ保持し、製品Redと区別した。

修正後、3.10の関連二suiteは56 passed/1 skipped（0.30秒）、既定3.12の同suiteは56 passed/1 skipped（0.21秒）、実3.10の通常全pytestは1866 passed/1 skipped（365.74秒）、全てexit0。skipは既存Linux O_TMPFILE capability testでありDarwinでのnative成功ではない。全Ruff（311 files）、MYPYPATH=srcの変更test限定mypyとdiff checkが成功した。P-12中の予備検証であり、残る旧source/tests、実Linux/Python3.11、Windows native、通常full lint、fresh Strict、最終手動確認は継続中。実consumer/live GitHubは未変更。

## P-12 旧JSON transaction writerの退役

旧json_store.py全345行・16 functionsと旧八test（157行）を全文確認し、[個別対応](artifacts/test-port-json-journal-retirement.md)を保存した。guarded reader/物理directory/native no-replaceと基本JSON I/Oは残し、UUID付きintent/stage/done、exchange後復元、reconcileを退役した。旧六関数を削除し、flag切替helperを現行no-replaceへ統合した。候補外import/attribute参照は0。現行のbytes/identity再検査、一file置換、unknown/partialを維持し、任意writerの原子的CASや旧bytes常設保存と同じ保証を主張しない。旧consumerの証拠/path/hashは変更しない。

削除前の後継九casesは9 passed（0.20秒）、既存Greenのcharacterizationである。通常wheelの旧writer収録禁止はRed 1 failed（0.73秒）→Green 1 passed（13.49秒）。関連九suiteは236 passed（79.68秒）、実Python 3.10.15の後継/native record kill/store三suiteは23 passed（4.14秒）、全てexit0。全Ruff（311 files）、MYPYPATH=srcの変更三Python files限定mypyとdiff checkが成功した。初回のregex/OS callback型の二指摘はfixtureの実契約へ修正し、ignore/cast/skip/収集除外を増やさない。

通常make lintは今回Python差分適用後にRuff成功・mypy 32 errors/11旧source files（230 source files）、make exit2。先行3.10全件成功は別候補であり、残る旧source/tests、今回の全件/native Linux/Python3.11/Windows、fresh Strict、最終手動確認は継続中。元logsはiss-00413-implementation/pytest-direct-json-retirement-{port,source-red,source-green,related,python310}.log、direct-json-test-typing.log、lint-direct-json-retirement.logへ保持。実consumer/live GitHubは未変更。

**実Linux / Python 3.11の予備検証**

[環境とfixture補正](artifacts/linux-python311-verification.md)を記録した。clean bdf44fe2のDocker Linux/Python 3.11.16全件は1844 passed/7 failed/17 skipped（870.24秒、exit1）。Artifact六casesのUSER未設定依存と、root capabilityがStart試験のnative書込み拒否を迂回する条件を切り分けた。capabilityだけを外した再実行は6 failed/1 passed（5.56秒）で、両原因を混同しない。試験のUSERを明示し、作成者文字列もassertした補正候補のLinux七casesは7 passed（5.53秒）、macOSのArtifact/Start全二suiteは139 passed（40.56秒）、全てexit0。全Ruff（311 files）、MYPYPATH=srcの変更test限定mypy、diff checkが成功した。製品挙動・元のnative拒否・skip条件は維持し、full Linux再合格と通常full lint、Windows、fresh Strict、最終手動確認は別途継続する。

**旧Workbench / Worktree helper群の退役**

旧application三files・1366行/54 symbolsと旧unit testの416行/13関数を全文・[個別判断](artifacts/test-port-workbench-helper-retirement.md)で確認し、外部production参照0の閉じた群を退役した。両WTの別slug、trim/大文字、真正の既存local ID、両側の不正metadata、missing/regular-file Workbench root、三階層のリンク差替えと外部metadata非読取を公開main/native Gitへ移す。無関係なmetadata linkの一律拒否・旧private結果型・登録ID/独自採番/Worktree flockは同等保証として温存しない。共有infraと別callerの残る旧rendererは保持する。

後継十八casesは18 passed（3.90秒）、root file二casesは2 passed（0.48秒）。wheel収録禁止はRed 1 failed（0.75秒）→Green 1 passed（12.86秒）。関連九suiteは245 passed（37.68秒）、実Python 3.10.15の新二十casesは20 passed（4.35秒）、全てexit0。初回collection/spy fixtureの失敗は元logsを保全し、製品Redとは区別した。全Ruff（307 files）、MYPYPATH=srcの変更二files限定mypy、diff checkが成功。通常make lintはRuff成功・mypy 30 errors/10旧files（226 filesを検査）、make exit2で未合格。残る旧source、Linux全件再検証、Windows、fresh Strict、最終手動確認を続ける。実consumer/live GitHubは未変更。

**旧Artifact composition adapterの退役**

未使用infra/artifact_ports.py全57行・四symbolsを全文確認し、候補外参照0をAST/文字列検索で確認して退役した。[対応記録](artifacts/test-port-artifact-adapter-retirement.md)に各wrapperの理由を保存する。現行Artifactと別callerのあるbinary publisher、その試験、旧静的inventoryのpath/hashは保持する。test削除・skip/型ignore/収集除外追加0。

wheel禁止のRed 1 failed（0.83秒）→Green 1 passed（17.35秒）、関連三suite 105 passed/1 skipped（10.89秒）、全て期待したexitとなった。skipは既存Linux O_TMPFILE試験でDarwinでは未実施。全Ruff（306 files）、MYPYPATH=srcの変更test限定mypy、diff checkが成功。Linux全件は別候補c4c26bdbで実行中、通常full lint・残る旧source・Windows・fresh Strict・最終手動確認は未完了。実consumer/live GitHubは未変更。

**旧Delete use caseとprivate resolver testの退役**

通常production参照0の旧Delete全1437行/42 symbolsと旧opacity test全44行/一関数を全文確認し、[個別判断](artifacts/test-port-delete-helper-retirement.md)に基づき退役した。公開CLIの三階層/.workbench・near-name/現存・ghost target十二casesへprivate metadata非読取・保全を移す。旧一般walkの列挙順、三段Active restore、GitHub自動Close、自動SyncはC-05/D-03の決定に従い残さない。退役後AST参照0、旧inventory path/hashと現在のDelete安全性suiteは保持する。

後継は削除前12 passed/37 deselected（2.22秒）。wheel禁止のRed 1 failed（0.77秒）→Green 1 passed（16.35秒）、関連三suite 56 passed（9.56秒）、実Python 3.10.15の後継12 passed/37 deselected（1.91秒）、全て期待したexitとなった。初回関連runの誤test path/no tests ranは別logへ保持した。全Ruff（304 files）、MYPYPATH=srcの変更二files限定mypy、diff checkが成功。通常make lintはRuff成功・mypy 30 errors/10旧files（223 files）、make exit2。Linux全件の別候補に残る失敗、残り旧source、Windows、fresh Strict、最終手動確認を継続する。実consumer/live GitHubは未変更。

**Linux全件の二回目とnative bootstrap fixture**

clean c4c26bdbの実Linux/Python 3.11.16全件は1839 passed/1 failed/17 skipped（921.27秒、exit1）。残る失敗はmake起動前のGit rev-parseが100msでtimeoutしたもので、同じSHAの単独再実行は1 passed（0.74秒）。[環境と切分け記録](artifacts/linux-python311-verification.md)へ結果を追記した。testの有限timeoutを2.0秒へ修正し、sleep5に対する実timeout・native process-group終了と応答OSError、unknown効果の元assertionsを維持する。製品挙動/test選択/skip条件は変更しない。

補正候補はLinux bootstrap全suite 32 passed（20.48秒）、macOSの同suite 32 passed（7.82秒）、全てexit0。Linux base/test hash・変更一file・実効capability0とprovider/prefix、主checkoutとの関連production bytes一致を照合した。全Ruff（304 files）、MYPYPATH=srcの変更test限定mypy、diff checkが成功。現在の全件再合格、通常full lint、残る旧source、Windows、fresh Strict、最終手動確認は別途継続する。実consumer/live GitHubは未変更。

## P-12 旧Create / Artifact writer群の退役

**旧Create / Artifact writer群の退役**

外部production参照0の旧application三files全3044行/120 symbolsと旧import test全965行/20関数を全文・[個別判断](artifacts/test-port-create-artifact-helper-retirement.md)で確認し退役した。一つの純粋分類testはdomainへ移し全assertionsを保持する。Create lock/UUID/PID/TTL回収、mutation journal、動的rules symlink/rollback、自動rescan/retryとprivate cleanup結果を廃止し、公開exact owner先行・source privacy・有限100slot・no-overwrite・actor/証拠保全を維持する。共有scope_scaffold、binary publisher/ports試験、旧inventory path/hashは保持。退役後AST参照0。

削除前の保全十一casesは11 passed/107 deselected（1.36秒）。通常wheel収録禁止はRed 1 failed（0.88秒）→Green 1 passed（15.35秒）、関連六suite 235 passed/1 skipped（37.91秒）、実Python 3.10.15の同十一cases 11 passed/107 deselected（1.32秒）、全て期待したexitとなった。skipは既存Linux O_TMPFILE capability testである。全Ruff（300 files）、変更三test限定mypy、diff checkが成功。通常make lintはRuff成功・mypy 17 errors/8旧source files（219 files）、make exit2。型ignore/収集除外/skip追加0。今回より前の0fd8764fのLinux全件成功を今回の全件証拠とは扱わない。残る旧source/Windows/full gates/fresh Strict/最終手動確認を継続し、実consumer/live GitHubは未変更。

## P-12 実Linux/Python 3.11のclean全件再検証

**実Linux/Python 3.11のclean全件再検証**

clean `0fd8764f0b1e64778344615e04c9d6428f1b827b` の通常全pytestは1851 passed/17 skipped（932.00秒）、exit0。[環境と元runの記録](artifacts/linux-python311-verification.md)へ保存した。capability0、USER未設定、offline、Linux tmpfs、HEAD/clean/source/prefixを再照合し、同一sessionで完了した。skipの内訳はZsh 12/macOS専用probe 1/Linux匿名stageで非該当cleanup 4でありnative成功に数えない。後続7d29648dの旧Create/Artifact退役は含まず、現在候補のfull lint・P-13・Windows native・fresh Strict・Final Quality Gate・最終手動確認は未完了。実consumer/live GitHubは未変更。

## P-12 旧Active / Sync / 依存チェック群の退役

**旧Active / Sync / 依存チェック群の退役**

外部production参照0の旧application三files全1647行/70 symbolsと旧test全991行/18 methodsを全文・[個別判断](artifacts/test-port-active-sync-deps-retirement.md)で確認し退役した。三段Active/context-pack、branch推定、中央ADR mirror/UUID probe、cache/full repo index採用、自動Sync/rollback、子doneから親を完了へ昇格するpolicyを撤去。現在のexact対象chain/prerequisite・自身のGH/local状態、同clone必要時観測/known counts、直接record・元資料/他WT保全を維持する。旧inventory path/hashと別callerのあるpure deps/validation/rendererは保持。退役後AST参照0。

削除前の保全十九casesは19 passed/47 deselected（4.33秒）、追加継承二casesは2 passed/66 deselected（0.53秒）。wheel収録禁止はRed 1 failed（0.83秒）→Green 1 passed（14.76秒）、関連六suite 243 passed（60.26秒）、実Python 3.10.15の後継二十一cases 21 passed/47 deselected（4.59秒）、全て期待したexitとなった。初回関連runの誤test path/no tests ranは別logへ保持。全Ruff（296 files）、変更二test限定mypy、diff checkが成功。通常make lintはRuff成功・mypy 10 errors/5保持source（215 source files）、make exit2。skip/型ignore/収集除外追加0。残るshared型契約、Windows/native full gates、fresh Strict、最終手動確認を継続し、実consumer/live GitHubは未変更。

## P-12 保持する共有コードの型契約

現在もvalidation・dependency・binary Artifact・rendererで使う共有コードの通常mypy十件を、実際の有限状態Literal、os.stat_result、返却型、JSON payload型と同一関数内の変数名へ合わせた。業務分岐、出力、試験選択、skip条件、型ignoreは変更しない。変更前の通常make lintは10 errors/5 files（215 source files）、exit2。修正後の通常make lintはRuff check/format（296 files）・mypy全215 source filesが成功し、exit0。関連dependency/validation/binary publisher/ports/presentation/Scope Delete八群は170 passed/1 skipped（10.06秒）、exit0。skipは既存Linux O_TMPFILE capability testでありDarwinでのnative成功ではない。元logsはiss-00413-implementation/lint-shared-source-typing.log、pytest-shared-source-typing-related.logへ保持した。現在候補の全pytest/native Windows/fresh Strict/Final Quality Gate/最終手動確認は別途継続する。

## P-13の準備: 配布consoleの一連の作業検証

[実consoleの記録](artifacts/fresh-console-lifecycle.md)に、fresh wheel/別venv/offline依存解決/pip check/source path改名から、実Gitのclone/linked WT、Start重複拒否、兄弟Issue並行、readonly Sync、completed GET確認後のFinish、次Issue Startまでを保存した。製品APIをmockせず、GitHubだけをstateful外部gh processで代替する。macOS/APFSの実Python 3.12は1 passed（8.73秒）、実3.10は1 passed（9.06秒）、共にexit0。初回の誤selectorによるfixture失敗は別logに残し、製品Redとは区別する。通常make lintはRuff（297 files）・mypy（216 source files）が成功、exit0。test追加前のclean e11f1879全macOS pytestは1843 passed/1 skipped（446.22秒）、exit0であり、追加caseを合算しない。P-12/fresh Strict、現在候補のLinux/Windows/native full gates、P-13完了認定、Final Quality Gate/手動確認、実consumer適用は未完了。

## P-12 現行helpのFinish説明

**現行helpのFinish説明を実処理へ合わせる**

公開work finishのhelpに残るselected subtree/canonical branch/derived stateを、captured direct recordの条件付き解除、completedのlive GET確認、現在branch保持、Start lockなし、正確なFinishDataへ変更した。Scope/Work/Workspaceの共通説明から旧cache/control/generation/共有branch bindingの前提も外した。既存公開help caseのRedは1 failed（0.06秒）、Greenは1 passed（0.03秒）。全help/completion、公開contract、Finish、fresh wheel四群は75 passed（31.92秒）、通常make lint（Ruff 297/mypy 216）も成功、exit0。業務処理や44 leafのsyntax、現consumerは未変更。元logsはpytest-current-finish-help-{red,green,related}.log、lint-current-finish-help.log。fresh Strict/Final Quality Gate/未完了のWindows接続・native受入をこのhelp補正で完了とは扱わない。

## P-12 OS排他のnative試験と配布CIの準備

**OS排他のnative試験と配布CIの準備**

[実OS境界の記録](artifacts/native-start-lock-boundary.md)へ、実Git common-dir、main/linkedと別clone、別processの保持/拒否/通常解放/強制終了を保存した。Mac 3.12のnative/identity/API契約三群は8 passed/1 skipped（0.82秒）、実3.10のnativeは3 passed/1 skipped（0.89秒）、共にexit0。Win32専用skipは未実施であり成功に数えない。製品adapterの変更はなく、test-onlyの受入準備とする。通常make lint（Ruff 298/mypy 217）、workflowのYAML/候補checkout/通常pytest維持の静的検査も成功。Windows native laneを追加したが実OSでの実行は未取得。

既存Ubuntu/macOS配布laneへ実console E2Eとprovenance出力を追加した。同じ五suiteのMacローカル検証は86 passed（122.39秒）、exit0。baseline 15bdcd05から製品source delta0、copy入力SHA256 b07821e35492f31ba68516552f050a398d345dc8fc546e075c36c63d097576b4、wheel SHA256 f8884f8d1e624fd8aa85c50f7eac763e646669df73431dab36eef7bd242c2761を元logへ保存した。CI実行/現在候補全pytest/Windows保存・公開/独立レビュー/P-13認定/最終手動確認/実consumer適用の完了へ転記しない。

## P-12 OS別の受入と未接続directory診断

**OS別の受入と未接続directory診断**

[OS別状態](artifacts/native-platform-status.md)と[Linux記録](artifacts/linux-python311-verification.md)へ、clean e11f1879の全件1827 passed/17 skipped（1016.04秒）と、製品source差分0のclean 6824b3f8の追加console case 1 passed（25.04秒）、共にexit0を保存した。合算/別SHAへの転記は行わない。

未接続OSでPOSIX専用O_DIRECTORYへ進む公開CLIのRed 1 failed/11 deselected（0.18秒）を、OS名先行確認の二行でGreen 1 passed/11 deselected（0.11秒）へ修正した。LOCAL_IO_FAILED/exit5/effects=[]、stderrなし、fixture/独自Git領域保全を確認。実3.10の同caseは1 passed/11 deselected（0.13秒）、関連八群は61 passed（28.82秒）、通常全lintも成功（Ruff 297/mypy 216）。provenance stdout追加後のconsole一caseは1 passed（9.03秒）。Windowsの保存/公開/nativeを完成・保証済みには変えず、ACL/namespace/別writerへのfallbackを追加しない。現在sourceのdelta/hashとbaseline HEADを区別して残す。fresh Strict/Final Quality Gate/手動確認とP-13完了認定・実consumer適用は未完了。

## 2026-10-02 全件結果・手動console・資料の現在状態

clean `8a70a8b30e69fe0bda6db6c45ef555f44411236d` の通常全件を固定して待機し、original sessionのexitとlogを取得した。Linux/実Python 3.11.16は1832 passed/18 skipped（1125.68秒）、exit0。macOS/実Python 3.12.11は1 failed/1847 passed/2 skipped（479.73秒）、exit1。失敗はinvalid dependency fixtureの公開validate前後のtree digest不一致で、[調査記録](artifacts/validation-readonly-investigation.md)に証拠を残した。製品sourceは変更せず、既存digest assertionと並べてfile mode/bytesの差分診断を追加。該当suite80 passed（12.70秒）と独立40回のfixture比較は成功したが、原因確定・全件合格の代わりにはしない。通常make lintはRuff298/mypy217でexit0。

別のowned fixtureへ通常wheelを非editable installし、sourceコピーを参照不能にした実consoleを外部CWDから個別に12回操作した。[手動証拠](artifacts/manual-product-smoke.md)と[stdout/stderr/実exit・現物](artifacts/manual-console-8a70a8b3.json)を保持。Start、同じIssueの拒否、兄弟の並行、無変更Sync、Finishの完了確認→捕捉record解除→現在branch保持、次Issue開始、native hookエラーのpartialと自動巻き戻しなしを確認した。GitHub境界はstateful fake ghであり、本consumer/live GitHubは未変更。tracked specのfold hashとC/B recordを照合した。最終候補の全面手動認定とは別。

人間向けHTML・READMEの「製品未着手」「High」の古い現在表示を、実装進行中・Max・候補単位の成功/失敗/未実施へ更新した。生成時のself-check/インタビュー/レビュー原文を保持し、[現在の検証証拠](artifacts/implementation-acceptance-evidence.md)を追加した。P-12進行中、P-13/P-14準備、Windows保存/native、macOS比較不一致、fresh Strict/FQ、人間merge、P-16/17は未完了。新しい業務commandやACL制度は追加していない。

## 2026-10-02 診断付きclean候補のmacOS全件

手動証拠・比較診断・資料を通常hooksのcheckpoint `1e5d2586678927866e9ec0eae804cdd4d55ff138` へ保存し、parent=8a70a8b3・branch不変・cleanを確認した。同候補の通常 `uv run pytest -q --tb=short -ra` は1848 passed/2 skipped（424.21秒）、exit0。実3.12.11・provider/prefix・clean SHAを開始時に照合。8a70a8b3から製品source deltaは0であり、異なるSHAのLinux件数とは合算しない。

外部owned logへのGit Trace2で該当fixtureの最初のcommitからmaintenance起動を捕捉したが、不一致やpack書換えは再現せず、原因の証明には使わない。製品の全GIT_*除去を変更していないため、traceの観測範囲も限定して[調査記録](artifacts/validation-readonly-investigation.md)へ保存した。元の失敗は撤回しない。Windowsの保存・公開・process境界とNTFS native受入、現在候補のStrict/FQは未完了。

## P-05 Windows物理directoryの親handle基準open

baseline ccf9637d後、[親path置換のAPI境界Red](artifacts/windows-directory-anchor.md)を確認し、filesystem anchor以外の子をNtOpenFileのRootDirectoryから開くようにした。属性検査・非継承・通常編集を許すshareを維持し、未完了openのhandle解放も別Red→Greenで確認。最終関連五suiteはMac/Python3.12で21 passed/1 skipped（1.49秒）、実3.10で21 passed/1 skipped（1.38秒）、通常make lintはRuff299/mypy218でexit0だった。Windows CIへ境界suiteを接続したが、native専用skipを実OS成功に数えない。過去の全件候補から製品source差分があるため、件数を現在候補へ転記しない。Windows保存・公開・processの接続、NTFS native、fresh Strict/FQと実consumer適用は未完了。

## 2026-10-02 Windows補強候補のmacOS全件

通常commit3b0c69e8のclean/parent/branchを照合し、実3.12.11・provider/prefixを固定した。[全件記録](artifacts/macos-full-3b0c69e8.md)に最初の2 failed/1851 passed/2 skipped（452.60秒）、修正runnerの該当二case 2 passed/7 deselected（0.16秒）、同SHAの全件1853 passed/2 skipped（402.78秒）、最終exit0を保存した。最初はCodexのignored診断runnerがmultiprocessing childでも実行される不備で、main guardを加える修正だけで解消した。製品source・既存tests・timeout・skipを変更しない。旧8a70a8b3のreadonly比較不一致と別件である。Linux/手動は別source、Windows保存/native・fresh Strict/FQ・実consumer適用は未完了。

## P-03 WindowsのJSON readerを親handleへ接続

baseline9a97f758から[読取境界](artifacts/windows-json-read.md)をTDDで接続した。NtOpenFileの保持した親から元bytesと全FileId128を取得し、regular/single-link、非redirect、失敗時解放を検査。関連八suiteはMac3.12/実3.10で各58 passed/3 skipped、通常make lintも成功。未知OSの公開CLI停止契約を保持した。新規native二caseとCI設定は実行待ちで、選択保存/無上書き公開/同期/捕捉解除・各公開/processは未接続のまま。過去の全件・手動を別sourceとして保持し、P-03全体や現在候補Strict/FQの完了を宣言しない。


## 2026-10-02 Windows JSON readerを含む通常全件

[clean6032621cの全件](artifacts/macos-full-6032621c.md)は独自runnerを使わず通常uv run pytestで1876 passed/4 skipped（366.99秒）、exit0。実Python3.12.11・provider/prefixと実行前後のclean/HEADを照合した。skipに実Windows JSON二caseを含め、native成功へ読み替えない。Linux/手動の別sourceと、旧比較不一致・旧runner不備の履歴も保持する。

## P-09 既知の未対応公開原語をGitHub変更前に拒否

[原語確認の修正](artifacts/scope-publication-capability.md)はbaseline6032621c。public Redは期待exit5に対してPOST後のpartial6で1 failed（0.74秒）、Greenは1 passed（0.29秒）。OS/libraryの能力照合をprobe書込みなしで追加し、実renameの選択も共用する。作成/取り込み・apply/dry-run・欠落platform/symbolの八caseでgh呼出し0・effects=[]・fixture bytes不変。関連九suiteはMac3.12で271 passed/2 skipped（66.61秒）、実3.10で271 passed/2 skipped（65.58秒）、通常lintはRuff300/mypy219でexit0。この後続sourceの全件、Windows保存/native、fresh Strict/FQ、実consumer適用は未完了。


## 2026-10-02 追記: 親GitHub取得より先の能力確認

Scope原語確認の最終差分でEpicのparent GETの順序も再現した（8 failed/63 deselected、3.83秒）。判定を親GET前へ移して同じ選択を8 passed/63 deselected（1.45秒）にし、三階層の24組合せを含む関連九suiteはMac3.12で287 passed/2 skipped（68.15秒）、実3.10で287 passed/2 skipped（68.17秒）。最終の通常lintもRuff300/mypy219でexit0。先の八case・271件は途中段階の実結果として保全し、今回の最終sourceと区別する。Windows保存/native、後続候補全件とStrict/FQは引き続き必要。


## 2026-10-02 clean75ac5760の全件と通常install CLIの手動確認

Scope公開の事前判定を通常checkpoint75ac5760へ保存し、parent6032621c・branch不変・cleanを確認した。[同候補のmacOS全件](artifacts/macos-full-75ac5760.md)は通常uv run pytestを直接実行して1900 passed/4 skipped（388.57秒）、実exit0。実3.12.11・prefix/providerと実行前後のHEAD/clean/source不変を照合した。旧候補・関連287件の結果へ合算しない。

[同じ製品sourceの通常install CLI](artifacts/manual-console-75ac5760.md)は14操作を個別実行した。非editable wheel・外部fresh venv・pip check・元provider pathを参照不能にしたsite-packages consoleを使用し、pytest bodyは呼び出していない。[原文](artifacts/manual-console-75ac5760.json)に実exit/stdout/stderr/前後entryと28件の外部gh requestを保持する。Start重複拒否、兄弟二件のSync、Close確認後の捕捉解除とbranch保持、次Issue開始、native hookエラーのpartialと自動rollbackなしを確認。Git本来のbranch/HEAD/reflog以外の独自controlは作らず、tracked仕様とC/B recordを照合した。

GitHub境界はstateful fake ghであり、live GitHubや本consumerは変更していない。Windows保存/各公開/process/native、現在候補Strict/FQ、人間merge後のP-16/17は未完了。旧macOS比較不一致・旧runner不備・別sourceのLinux/手動の証拠を保持し、今回の成功で撤回しない。

## 2026-10-02 Startの保存原語確認

2026-10-02、baseline578f27e3から[Startの保存原語確認](artifacts/start-publication-capability.md)を追加した。未対応symbolの公開RedはGit branch/checkout後のpartial6（1 failed、0.66秒）。計画が公開を必要とする場合だけ、dry-run成功・lock/Git変更前に既存の能力照合を行う。三階層と既存記録の保全・公開不要の同一Startを含む16組は成功。関連八suiteはMac3.12で266 passed（102.42秒）、実3.10で266 passed（102.77秒）、通常lintはRuff300/mypy219でexit0。既存の実rename/同期失敗とpartial/unknown、自動rollbackなしを維持する。75ac5760の全件・手動結果をこの後続sourceへ転記せず、Windows保存/nativeと現在候補Strict/FQは未完了。

## 2026-10-02 clean2b2be5e2の全件と通常install CLIの手動確認

Start保存原語確認を通常checkpoint2b2be5e2へ保存した後、[通常macOS全pytest](artifacts/macos-full-2b2be5e2.md)を直接実行し、1916 passed/4 skipped（434.98秒）、実exit0を元sessionで確認した。前後のHEAD/clean、実Python3.12.11のprefix/provider、製品source hash不変を照合。関連266件や先行1900件に合算しない。

[同じ製品sourceの手動14操作](artifacts/manual-console-2b2be5e2.md)はfresh wheel/外部venv/非editable install/pip check/コピー元source改名後の実consoleで個別に実行した。[原文](artifacts/manual-console-2b2be5e2.json)へstdout/stderr/実exit/前後entry、26件のstateful fake gh requestを保存した。Start重複拒否、兄弟二件のSync、completed GET後の捕捉解除とbranch保持、次Issue開始、Initiative Startのnative hookエラー/partial/rollbackなしを確認。tracked仕様のfold、C/B recordのbytes/hash、独自.git/spec-dock不在を照合した。補助検査の表記取り違えは保存原文を再読して補正し、CLIを再実行して成功を作り直していない。

同じbranchのlive上流はread-only ls-remoteで8c59994cを返し、cleanローカル2b2be5e2と不一致だった。新しいpush/Oracle/Strict/FQは実行していない。通常pushへの明示許可とv2 pilotの選択は以前の質問への回答待ち。Windows保存・各公開/process・native受入、人間merge後の実consumer適用・正式#413 import/Startも未完了であり、元の全実装goalを達成済みにしない。
