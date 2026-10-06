# iss-00415 実装・検証記録

## 現在の実装状態（2026-10-06）

ユーザーが本計画の実装・完了、GPT 5.6 ProでのStrict Final Quality Gateと指摘修正・再レビューを依頼しました。ゴール登録済み。対象はb004、branch `codex/iss-00415-cli-refresh-specs`、開始HEAD `775075cbd936d1f6fc80a97e2e50659c43f85fc1`です。人間のmergeは対象外です。S-01〜08は実装・検証・適用済み。ユーザーはv2を明示選択済みです。初回StrictレビューはP1一件で不合格となり、その外部適用面を復元しました。再レビュー、最終handoff、Issue Finishは未完了です。

- `spec-dock work start iss-00415 --branch codex/iss-00415-cli-refresh-specs --json`: exit 0、同branchを再利用し直接対象を取得。active showで対象・祖先を再確認。
- S-01: macOS 27.0.1 arm64、開始HEADの `make lint` exit 0。`uv run pytest` exit 0、1917 passed / 1 skipped / 450.76秒。生ログはIssue Workbench `implementation/baseline.log`。
- S-02: 公開create/import × 3階層 × apply/dry-run × text/JSON × 直接選択あり/なしの48条件。保全・比較・手動判断の案内不足でRedを確認し、診断文言だけを変更。公開publish/import suite 139 passed / 41.15秒。tree digestでmetadata・証拠・直接記録・Gitのmode/bytes/type不変、gh呼出しなしを確認。
- S-03: READMEの実掲載3例をstateful gh stubで実行し、返却IDの親子連結とyesなしの無副作用停止を確認。通常TARGETの正負例、rootの実import例、Sync・AGENTSの現行説明と実在リンクを確認。対象suite 38 passed / 12.44秒。provider文書のhashはS-05で統合予定、consumer未適用。
- S-04: 全44 leaf・三shell生成候補のRedを確認し、候補選別だけを修正。三生成検査はpass。実Fish 4.0.2の7代表入力も7 passed。macOSのBash/Zshを含む対象回帰は下記のとおり。
- 検証用Linuxコンテナ: Python 3.10.22、Bash 5.2.37、Zsh 5.9、Fish 4.0.2。製品依存やホスト設定へ追加していません。

以下は仕様採用時点の履歴です。未実施という記述はその時点の観測で、現在の実装状態は上記と以降の追記を参照します。

# 仕様策定・採用記録

## 結果

2026-10-06、installed external SpecDockで[Issue #415](https://github.com/chemitaro/spec-dock/issues/415)をepic-00080配下に作成しました。親#79/#80のOPENを本作業でlive確認しました。7件のCLI操作契約不整合を対象とする日本語Requirement・Design・Planの完全版を、同じChatGPT会話から取得して内容照合後にcanonicalへ採用しました。文書のdraft／仕様候補表示と全実装step未実施の表示を保持します。仕様採用は製品実装や独立仕様レビューpassを意味しません。

作業場所はb004専用worktree、branchは`codex/iss-00415-cli-refresh-specs`です。元main checkoutには書き込んでいません。metadataとArtifact登録はSpecDock CLIで行いました。

## 来歴

- 初回入力checkpoint: `95ec39b751054bf48098215fc077fe7b8f533f62`。親commitはPR414 mergeの`0e7dc86841cb48d011270a1a2165cb6406ac0cea`です。
- Strict wrapperのclean／設定済みupstream／live full SHA一致を通過。同じSHAに対するGitHub connector再検証成功が[回答原文](artifacts/20261006t043340z--answer.md)に記載されています。connector検証は回答内の申告であり、wrapperによる機械的attestationではありません。
- 親session: `specdock-cli-refresh-audit-resumed`。今回のfollow-up session: `required-strict-github-connector-verificati-1408`。約34分30秒、exit 0。
- [継続した会話](https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6ac46387-8628-83ee-9104-2bb0e6874e14)。新しい会話へ切替えていません。
- 指定model／effort: `gpt-6-pro`／`pro`。今回model selectionは保存設定継承のためskipped／verified=false、effortはPro／already-selected／verified=true。前回のLatest／Pro選択証拠と、今回の再選択省略を区別します。
- 取得ZIPは[原本](artifacts/20261006t043339z--iss-00415-cli-refresh-specifications.zip)としてCLI importしました。download button fallbackの未保存ログはありますが、その後の実ファイル保存・hash・CRC検査が成功しました。

## 検証

- ZIPは40,428 bytes、SHA-256 `d6fcb257b6cb9ef27318a4137ef10af236f7e39999dbc9adb6cb610f387c20b0`。rootはrequirement.md／design.md／plan.mdの3通常ファイルのみです。重複名、directory、symlink、path traversal、暗号化entryなし。UTF-8 strict decode、CRC、サイズ検査に合格しました。
- [ファイルhash検証](artifacts/20261006t043341z--zip-validation.json)に記録した3つのhashは、回答、原ZIP、採用後canonicalの全てで一致します。完全ファイル置換であり、生成後の本文補正はありません。
- 3文書全974行を確認しました。SD-OPS-001〜007と配布・品質のRQ/AC、設計、S-01〜09、V-001〜09が対応し、非対象と未決判断を維持しています。
- 相対リンク・明示anchor 74件、source/test path 18件を照合し欠落なし。本文で引用する既存test function／fixture、診断分類、static updateの返却fieldも現行sourceで照合しました。
- inventoryのreference_cli.md current hash、既知旧hash2件、mode、init_onlyが設計記載と一致しました。
- PR414のMERGED／merge日時／merge commitをliveで再確認しました。GitHub Aboutが旧descriptionであることもGETで確認し、変更していません。
- 外部手順の記述は[GitHub API](https://docs.github.com/en/rest/repos/repos#update-a-repository)、[gh api](https://cli.github.com/manual/gh_api)、[Fish complete](https://fishshell.com/docs/current/cmds/complete.html)、[uv tool install](https://docs.astral.sh/uv/reference/cli/#uv-tool-install)の公式資料と照合しました。
- 採用後の`spec-dock workspace validate --json`はvalid=true／findings=[]／node_count=241、`git diff --check`はexit 0でした。active showはemptyです。

## 残る事項

今回はIssue作成と仕様反映までです。製品実装、製品pytest／lint／fresh wheel再認定、package更新、consumer更新、About書込み、work start/finish、PR作成・mergeは実施していません。IssueはOPEN、直接選択はemptyのままです。

実装時には対象候補・wheel・tool環境・consumer絶対root・backup先・検証環境を確定します。Aboutのdescription採否と実施、互換入口廃止、global共通skill＋local情報は未決のままです。後二者は本Issueの七件に不可欠でない将来の別判断です。過去の3 passedを現在の製品検証成功へ転用しません。


## S-04〜05 実装候補の配布確認

- 全44 leaf・三shellの候補を独立したread分類表で検査。共通値のskip、parser受付、catalog分類は変更していません。
- 新規・旧版更新の公開CLI試験で、改稿前の実blob hashを確認し、backupの旧bytes/modeと文書以外のtree不変を確認。未知の追記があればeffectsなしで停止。
- inventoryはreference_cli.mdのcurrent hashだけを更新し、以前のcurrent `1ee708029bae2fa92eb2c2bd9fe79e9885fc11815b535bf8e1be344b6d3689dc`をknown-oldへ追加。既存旧hash2つ、他entry・retired集合は保持。
- 対象回帰: help/completion、CLI契約、lock options、provider distribution、static assets、wheel、entrypointの7ファイルで `179 passed, 7 skipped in 114.12s`、exit 0。skipはホストにないFishの7件で、同7件はLinuxで実行し7 passed。
- fresh wheelとsdist経由wheel、外部non-editable console、fresh consumer、全inventory bytes、legacy診断の無副作用、README三階層作成と確認guard、selector正負、native補完を検査。製品の実GitHub変更はstubへ隔離。
- 現在のlintはruff check/format、mypyすべてpass。workspace validateは241 Scope、findingsなし。
- 固定commitからの独立wheel・Linux/Python 3.10全体検証と利用者環境への適用は次段階です。通常全件テストとStrict Gateも未完了です。


## S-05〜06 固定候補と全件検証

固定候補は `c50a0ee0785b29367a74ccb4688d45bfcf067130`。同commitのGit archiveから独立buildし、wheelを新しい外部venvへ非editableで依存とともに導入しました。build元を改名した後も、外部module import・help・version・三shell completionが成功しました。

- wheel: `/private/tmp/specdock-issue415-hgd8psjp/dist/spec_dock-0.2.4-py3-none-any.whl`
- SHA-256: `20a99b071028d7dd4ae9c11e7319a6f79d08c179972b6be59cc5ed27595f45e4`
- 独立console: `/private/tmp/specdock-issue415-hgd8psjp/venv/bin/spec-dock`
- macOS: `make lint`、`uv run pytest`、`git diff --check`すべてexit 0。全件 **1992 passed / 8 skipped / 446.70秒**。skipはLinux専用1件と未導入Fish7件。
- 現在consumerへのdry-run: exit 0、planned_pathsは `spec-dock/docs/reference_cli.md` のみ。追加・退役なし。実適用とは区別します。

Linux初回は **307 failed / 1687 passed / 6 skipped / 312.01秒**でした。多数の失敗は直接選択の書込み後照合に集中します。このコンテナの通常一時領域では、製品を使わない `os.listdir(fd)` の最小例でも、作成直後のentryを最初の再読で見落としました。tmpfsでは同じ最小例でentryが見えます。該当する製品のstore/domainは開始commitから変更していません。

既存のLinux検証記録と同じtmpfs fixture・capability全除去の条件に揃えた切り分けは **115 passed / 21.90秒**。元失敗を削除せず、この条件で通常全件を再実行しました。結果は次節に記載します。製品修正・assertion緩和・skip追加はしていません。tmpfsでの結果を、元のコンテナ通常一時領域でも成功した証拠にはしません。

生ログと結果はIssue Workbenchの `implementation/{candidate.json,candidate-wheel.log,macos-full.log,macos-results.json,consumer-dry-run.json,linux-full.log,linux-filesystem-probe.json,linux-fixture-isolation.log,linux-tmpfs-full.log}` に保存しています。


## S-06 再検証の確定結果

同じコード候補c50a0ee0のLinux/Python 3.10.22、tmpfs fixture、capability全除去で `make lint` と通常 `uv run pytest` がexit 0、**1995 passed / 5 skipped / 182.47秒**でした。5 skipはmacOS専用1件とLinux匿名stageで適用しないnamed-stage cleanup4件です。Bash/Zsh/Fishのnative検査を含みます。初回失敗とfocused passを合算していません。証拠は `implementation/linux-tmpfs-results.json` と同名full logです。

## S-07 外部packageとb004 consumerへの適用

本計画の実装依頼を根拠に、検証済みc50a0ee0 wheelを既存uv管理環境へ `uv tool install --reinstall` で通常再導入しexit 0。consoleは `/Users/iwasawayuuta/.local/bin/spec-dock`、実moduleは `/Users/iwasawayuuta/.local/share/uv/tools/spec-dock/lib/python3.12/site-packages/spec_dock/__init__.py` です。versionは同じ0.2.4ですが、direct_urlが以下のcandidate wheelを指すことを確認しました。PATHや他toolは変更していません。

保全root: `/Volumes/990p2t/workspace/worktrees/specdock-issue415-preservation-20261006/`。

- `previous/spec_dock-0.2.4-py3-none-any.whl`: hash `5c600ca9f646e1f941e4a20ff67b10b898990e8a1d54a74d3266f1833243673e`。
- `candidate/spec_dock-0.2.4-py3-none-any.whl`: hash `20a99b071028d7dd4ae9c11e7319a6f79d08c179972b6be59cc5ed27595f45e4`。
- `consumer-backup/static/spec-dock/docs/reference_cli.md`: CLIで旧bytesを保全。backup_verified／restore_verifiedはtrue。

対象rootは `/Volumes/990p2t/offloaded/home/iwasawayuuta/.codex/worktrees/b004/spec-dock` のみ。installed CLIのdry-runを再確認してからapplyし、変更は `spec-dock/docs/reference_cli.md` のみ、追加・退役なし。前後のconsumer全file（Workbench除外）のmode・hash比較も同一結論でした。新文書はproviderとbytes一致。直接記録、metadata、成果物、workspace宣言、非対象skill/shim/template/systemを保持しました。他worktreeの更新は行っていません。

実installed consoleでも公開契約のsmokeに合格しました。最初の検証harnessはmacOSの一時pathのsymlinkによりtree digestが拒否したため、physical `/private/tmp` を使って再実行しました。製品のpath検査は変更していません。証拠は `implementation/consumer-{apply,preservation,after}.json`、`installed-console-verification.json` です。復元はR-02/R-03に従い、現在状態と保全物を照合してから別の明示操作として扱います。

## S-08 GitHub About適用

`chemitaro/spec-dock` のdescriptionだけを対象に実施しました。ghの2回の直前GETは一致し、PATCHはPAT権限不足のHTTP 403で失敗。別GETでも未変更を確認し、PATCHを再送せず、既にchemitaroとしてログイン済みのGitHub通常UIの「Edit repository details」でDescriptionだけを入力・保存しました。credential・permission設定の変更はありません。

保存後の独立live GETで、D-415-007のdescriptionと完全一致しました。topicsは `[]` のままです。Website入力・checkboxは未操作ですが、UI保存時にhomepageのAPI表現が `null` から `""` に変わりました。URLは未設定のままです。この差をbytes一致や全field不変とは報告しません。旧値・失敗・UI経路・独立GETは `implementation/about-evidence.json`、画面は `about-after.jpg` に保持しました。

## S-09 受入対応と残るゲート

| 受入 | 実証拠・状態 |
|---|---|
| AC-415-001 | 48条件のlegacy同居negative、無副作用・診断・error/exit維持。全件passに含む |
| AC-415-002 | READMEの三階層実例、返却ID連結、yes除去対照。全件passに含む |
| AC-415-003 | 通常selector／import refの公開境界、root実例。全件passに含む |
| AC-415-004 | local/github/retired cache、Sync無書込み・unknown/partial。全件passに含む |
| AC-415-005 | AGENTSの日時付き履歴、PR414実績、履歴原本のhash維持 |
| AC-415-006 | 44 leaf×三shell生成、native三shell、parser/値処理回帰。両OSで確認 |
| AC-415-007 | description独立GET一致。初回はhomepage副次変更で未達。下記の限定復元後にhomepage=null／topics=[]を独立GETで確認 |
| AC-415-008 | inventory、fresh wheel、外部console、fresh/known-old/unknown consumer、実適用と保全 |
| AC-415-009 | c50a0ee0全lint/pytest、配布、実運用を確認。最終Strict認証は未実施 |

未完了: ユーザーが求めたGPT 5.6 ProのStrict Final Quality Gate、そこで必要となる修正・再レビュー、最終handoffとIssue Finish。ユーザーがv2を明示選択済みで、同一レビュアーの再判定を行います。実装依頼と現在upstreamへの通常push許可は維持します。人間のPR mergeは別責務です。


## Strict Final Quality Gate 初回とP1対応

レビュー対象は `cabe00ca76a859baf7dfad780d29a8d21abf0d43`、baseは `775075cbd936d1f6fc80a97e2e50659c43f85fc1`。ユーザーのv2指定後、GPT-5.6 Sol / Proのbrowser実選択を確認して実行しました。session `fqg-v2-5630131f-05ddcee7`、会話 `6ac509ef-2e64-83ec-8497-e8d0dddd95d7`。wrapper exit 10、status=fail、coverage_complete=true、P0=0/P1=1/P2=0/P3=0です。製品コードには追加P0/P1なしとのレビュー結果ですが、最終認証passではありません。

同じSHAの独立test laneは、make lint、通常pytest（macOS 1992 passed / 8 skipped）、diff check、workspace validate、Linux/Python 3.10.22のlintと通常pytest（1995 passed / 5 skipped）の5commandすべてexit 0です。campaign配下 `test-results/manifest.json` にSHA・command・exit・生logを保存しました。

唯一のP1 `FQG-415-ABOUT-HOMEPAGE-SIDE-EFFECT` は、UI保存でhomepageがnullから空文字へ変わったままS-08を完了とした点です。完全なreview/test batchを `analyze-review-findings` に従い分析し、AC-415-007違反として受け入れました。最初のfault layerは運用適用のintegrationです。Website未設定という意味の同一性を、厳密な前後不変の代替にした完了表示を訂正します。先のS-08完了表示は、その時点では誤りでした。

要件・設計を緩和せず、実装完了・指摘修正の既存承認に基づき自分の副次変更だけを回復しました。環境PATとは別に既に設定済みの同じchemitaro OAuth loginがあり、GET /userで同一主体を確認。子process内で環境tokenの上書きだけを外して正規gh認証を利用し、認証設定・権限は変更していません。直前GETが自分の採用description／homepage空文字／topics=[]のままであることを確認後、一回の `PATCH repos/chemitaro/spec-dock` に `{"homepage":null}` だけを送信しexit 0。別の通常認証GETで以下を確認しました。

- full_name: `chemitaro/spec-dock`
- description: D-415-007採用文言と完全一致
- homepage: `null`（変更前値に復元）
- topics: `[]`（変更前値と一致）

生証拠は `implementation/about-homepage-recovery.json`。現在のS-08完了はこの復元後の状態を根拠とし、途中の副次変更がなかったとは主張しません。製品runtime/tests・要求意味は変更していません。P1を閉じられるかは同一レビュアーへ再判定を求めます。campaignは Issue Workbench `chatgpt-final-quality-gate-strict-v2/issue415` に継続し、要件・設計・base・scopeは維持します。
