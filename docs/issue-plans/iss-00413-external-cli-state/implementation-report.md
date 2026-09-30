# Issue #413 実装記録

## 作業契約

2026-09-30の利用者指示に基づき、レビュー合格済み要件・設計・計画に沿ってTDDで段階実装する。区切りごとに検証・コミット・GPT-5.6 Sol / ProによるChatGPT Code Review Strictを行い、必要な指摘の分析・修正・再レビューを実施する。最終候補ではStrict Final Quality Gateと独立した必須試験、実consoleによる手動動作確認を完了する。

必要な具体化にはImplementation Brief Strictを利用する。実装担当の契約はGPT-6.1 Sol / High。人間によるPRマージ、package公開、実環境適用は製品実装・検証と別の証拠として扱う。

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
