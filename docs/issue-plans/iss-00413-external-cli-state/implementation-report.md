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
