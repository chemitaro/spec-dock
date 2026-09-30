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
