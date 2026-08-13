---
種別: 実装報告書（Issue）
ID: "iss-00360"
タイトル: "Cut Over Distribution and Retire Legacy Workflow Surfaces"
関連GitHub: ["#360"]
最終更新: "2026-08-13"
親: ["epic-00356", "init-local-00003"]
依存: ["requirement.md", "design.md", "plan.md"]
---

# Result Summary

## Outcome

Issue 360のRequirement / Design / Planを、Issue 357〜359の実装handoff、IC-1 / IC-2、現行installer、ChatGPT-Use-Strictのexact-main authoring分析に基づいて具体化した。S20のCurrent catalog検証をS40A / S40Bのphysical cutover後へ移すPlan amendmentを完了し、fresh local `spec-reviewer`とcurrent exact-upstream `ChatGPT-SpecReview-Strict`のP0 / P1なし`pass`を確認した。S00 / S10、S40A / S40B、S20 / S25 / S30を完了し、S35でversion / retry marker admissionとCLIのzero-write rejectionを実装・検証した。S35のfresh code review、step commit、clean/upstream一致後にS45へ進む。PR、Issue close、IC-3判定は実装・最終品質gate後まで開始しない。

## Verification

* Current branch: `iss-00360-cut-over-distribution-and-retire-legacy-workflow-surfaces`
* Initial planning baseline HEAD: `27b8682cb6e5262c980f3b04c7f01459a87685e9`
* Integrated main baseline: `a6ded0d9a838b40cdcd741fa473cd264b801f245`
* Issue 359 final head: `948d0cf0dedb84ca34e51a4adc0995820aa011f6`
* Initial approved planning commit: `3147c80bbbd6a8d4f76685ed5228d1d4495f1aef`
* Current branch upstream: `origin/iss-00360-cut-over-distribution-and-retire-legacy-workflow-surfaces`

* Current implementation-admission SHA: `8c01c9fd2e76d7d7bccc754bca902e8010026703`（local HEAD = upstream、clean）
* Plan amendment local review: fresh `spec-reviewer` pass（S40A verificationは既存`test_storage_core_cli.py`のみ）
* Plan amendment Strict review: session `issue-360-admission-current-strict`、GitHub exact SHA `8c01c9fd2e76d7d7bccc754bca902e8010026703`、resolved `GPT-5.5` verified、P0 / P1なしでpass
* S00 revalidation: branch / active Issue / dependency `ready=true` / blockers 0 / `validate nodes=221` / local HEAD = upstream `9916af139e01a322d092e6fc0434b49f6a567e37` / clean

* Push verification at planning commit: local `HEAD` = upstream = `3147c80bbbd6a8d4f76685ed5228d1d4495f1aef`
* `origin/main` merge: fast-forward success、Issue 360文書差分を保持
* `active set iss-00360`: success
* Initial `issue start iss-00360`: dependency `iss-00359`未完了でblocked
* Post-merge dependency check: `ready=true`、blockers=0
* Post-merge `issue start iss-00360`: 未コミットIssue 360文書を保護するcheckout safetyで停止。active selection unchanged
* Approved planning docs / IC evidence commit: success、対象7 pathだけ、commit `3147c80bbbd6a8d4f76685ed5228d1d4495f1aef`
* Issue 360 branch first push / same-name upstream setup: success
* Formal `issue start iss-00360`: success。Issue checkoutはcurrent Issue 360 branch、auto-sync success
* Post-start active context: Initiative `init-local-00003`、Epic `epic-00356`、Issue `iss-00360`
* Post-start dependency: `ready=true`、blockers 0、authority `github`、effective status `open`
* Post-start validation: `spec-dock: ok (validate) nodes=221`
* ChatGPT-Use-Strict: GitHub connectorで`chemitaro/spec-dock` `main` = `a6ded0d9a838b40cdcd741fa473cd264b801f245`を検証し、session `required-strict-github-connector-verificati-65`、resolved model `5.5Pro`でR/D/P authoring案を取得。main orchestratorがrepository factsとIC evidenceへ照合して正本候補へ統合
* Requirement fresh spec review: round 1 / round 2 fail、round 3 pass（P0/P1なし）
* Design fresh spec review: round 1 / round 2 fail、round 3 pass（P0/P1なし、confidence 0.98）
* Plan fresh spec review: round 1 / round 2 fail、round 3 pass（P0/P1なし、confidence 0.99）
* ChatGPT-SpecReview-Strict pre-submit attempt: session `required-strict-github-connector-verificati-66`はrate-limit dialogで停止。`promptSubmitted=false`、conversation IDなし、leaseなしでreview未成立
* ChatGPT-SpecReview-Strict round 1: session `required-strict-github-connector-verificati-67`、GitHub connectorでcurrent branch exact SHA `e7520e6a433c0b6345b4f52f1172c32f56fad9d3`を検証、resolved model `GPT-5.5` verified。Lifecycle current-state矛盾1件をP1として`fail`
* ChatGPT-SpecReview-Strict round 2: session `required-strict-github-connector-verificati-68`、GitHub connectorでcurrent branch exact SHA `4b325885b82dbffa26cdd5cd372d3914e8d604ef`を検証、resolved model `GPT-5.5` verified。P0 / P1なしで`pass`、親Epic Reportの進捗drift 1件だけをP2として検出
* IC-1 fresh verification: Storage Core `4 passed`、S09 Authoring Kit `23 passed`、Fresh node / Artifact `3 passed`
* IC-2 fresh verification: Issue 359 static / collision `11 passed`、finalizer `9 passed`、route / zero-write `7 passed`

## Execution Admission / Blocker

2026-08-13のimplementation-start admissionでは、current exact upstream SHA `a3901a7ec2056bd392762c3d4efa71967f4ec232`に対するStrict reviewがS20順序のP1を検出したため、production / test / provider asset mutationを開始せずPlan amendmentへ戻した。その後、S10 → S40A → S40B → S20の順序、S45の依存、Requirement / Design / Reportのgate記述、S40Aの検証対象を修正し、fresh local `spec-reviewer`とStrictを再実行した。

最小修正として、Planの順序を`S10 → S40A → S40B → S20 → S25 → S30 → S35 → S45`へ変更し、S40Aの検証を既存`tests/cli_runtime/test_storage_core_cli.py`だけへ限定した。S10のread-only exact inventoryを先にlockし、S40A / S40Bでprovider physical cutoverを完了してからS20のCurrent catalog / historical manifest validationを行う契約は維持した。Plan amendment後のfresh local `spec-reviewer`とcurrent exact-upstream Strictがともにpassしたため、implementation-start gateを解消し、S00 / S10へ進む。

### S10 Exact inventory lock

S10はread-onlyで完了した。基準HEADは`9916af139e01a322d092e6fc0434b49f6a567e37`、provider-side historical sourceはIssue 359 final commit `948d0cf0dedb84ca34e51a4adc0995820aa011f6`（reachable branch `iss-00359-replace-managed-workflow-skills-with-specdock-skills`、package version `0.2.3`）とした。`git ls-tree` / `git show`でinstall_root 77 filesと旧scaffoldのexact mode/blob/SHA-256を再現できるため、旧surfaceのhistorical identityはGit provider-source provenanceとして採用できる。wheel / sdistの保存物は存在せず、配布済みpackage identityとは断定しない。

| 分類 | S10でlockした現物 | 実装上の扱い |
|---|---|---|
| Current Target | provider `spec_dock/{docs,templates,scripts,system}/**`、`.gitignore`、install_root二skill、`.github/workflows/ci.yml`、root `spec`、generated `active/.agent` | S40B後にphysical catalogとして導出し、Current全量manifestは作らない |
| Obsolete managed | 旧18 managed skill、host-adapter/native agent/config/prompt/rule、ChatGPT wrapper、authoring-pack、planning runtime、obsolete docs/templates | S40A/S40Bでproviderから除去。consumer pruneはGit-source exact identityまたはtrusted manifest + target identity一致時だけ |
| Preserve / user-owned | `initiatives/**`、node-local evidence、Workbench payload、unknown external skill/config/workflow、unproven same-name path | 自動置換・pruneせず、必要時はpreserve-and-block |
| Read-only evidence | Issue 357〜359 report、Epic IC artifacts、Git history/tree、package metadata、current provider/dogfood parity | source-of-truth照合とreport evidenceだけに使用 |

Provider / dogfoodの現行二skill、CI、`.gitignore`、`scripts/spec-dock`のselected bytes/modeは一致した。dogfood固有のgenerated filesは`spec-dock.version`、active/agent derived views、dashboard/deps/tree projectionに限定される。`meta.json`のowner/path claims、workspace marker、directory名だけでは個別ownershipを証明しない。S10で再現できない「過去wheel/sdistのpackage digest」は未採用候補としてpreserve-and-blockに記録し、S20のmanifestへ推測値を登録しない。

### S40A Legacy planning Runtime physical retirement

S40Aの実装を、S10でlockしたexact targetとPlanの共有symbol境界に従って完了した。実装commitは`abcea9c21669b64bdb2277e6a0cf212ff8ae9727`、旧専用test / fixture整理commitは`091a323225a5b8af854f6f5f16705354fcb761b6`であり、S40A後のclean HEAD / upstreamは`091a323225a5b8af854f6f5f16705354fcb761b6`で一致している。

| 観測 | 結果 | 証拠 |
|---|---|---|
| Old-only Runtime / wrapper removal | pass | provider / dogfoodそれぞれ63 path（60削除 + contracts/ports/bootstrap 3変更）。`spec-dock-chatgpt`、`scripts/authoring-pack/**`、runtimeのplanning / authoring_pack treeを除去 |
| Shared boundary safety | pass | `application/contracts.py` の planning use case 4 fields、`application/ports.py` の planning-only ports、`cli/bootstrap.py` の planning gateway / callback / importだけを除去。Storage Core / Artifact / lifecycle / sync / validate assemblyは保持 |
| Route / import absence | pass | `tests/cli_runtime/test_storage_core_cli.py` の removed module / help-route characterizationを更新 |
| Retained Storage Core characterization | pass | `uv run pytest --run-full-regression tests/cli_runtime/test_storage_core_cli.py -q` → `4 passed` |
| Adjacent retained surfaces | pass | `uv run pytest tests/cli_runtime/test_wrappers.py tests/unit/infra/test_authoring_kit_assets.py -q` → `304 passed, 9 skipped` |
| Formatting / review | pass | `git diff --check`、fresh `code-reviewer` pass（P0/P1なし、provider/dogfood parity確認） |

S40AのREDは、共有契約を先に切断した状態で旧planning modulesをretained listへ残したため、Storage Core testが旧存在期待で失敗したこと。GREENではremoved module / use case fieldへ期待値を移し、物理削除後に4件すべてpassした。旧専用test / fixture 53件も削除し、S40B対象の`test_wrappers.py`、`test_authoring_kit_assets.py`、`test_init_update.py`、`authoring_kit` fixtureは保持した。S40A実装commitとtest整理commitの後にworktree / upstream SHA一致を確認した。S40Bのprovider physical catalog cutoverへ進んだ。

### S40B Shipped Target catalog physical cutover

S40Bのprovider-side physical cutoverを実施中である。Current install-rootは次の5ファイルへ縮小した。

* `.agents/skills/spec-dock/SKILL.md`
* `.agents/skills/spec-dock-grill-with-docs/SKILL.md`
* `.agents/skills/spec-dock-grill-with-docs/agents/openai.yaml`
* `.agents/skills/spec-dock-grill-with-docs/scripts/finalize-artifact.py`
* `.github/workflows/ci.yml`

旧18 managed skill、legacy 3 skill、host-adapter metadata、`.codex/**`、`.github/agents/**`、旧ChatGPT / planning / authoring-pack配布面はprovider treeから除去した。Current二skillのIssue 359 final bytesをSHA-256で固定し、retained CIはStorage Coreの`sync` / `validate`だけを実行することを確認した。`.gitignore`は`src/spec_dock/assets/spec_dock/.gitignore`を物理provider assetとして必須化し、`_DEFAULT_SPEC_DOCK_GITIGNORE` fallbackを削除した。provider source欠損時はmutation前に停止する境界を残している。

旧phase / workflow / authoring / host-adapter専用docsと、`discussions/**`、`assurance/**`、`issue-profiles/**`、`pr-repair-batch.md`のprovider scaffoldも除去した。S40Bではdogfood projectionを直接編集・更新せず、既存consumerのlegacy external surfaceは保持したままS20/S25 classifierとS55のproven pruneへ引き渡す。

| 観測 | 結果 | 証拠 |
|---|---|---|
| Provider install-root exact catalog | pass | `uv run pytest --run-full-regression tests/cli_runtime/test_distribution_cutover.py -q` → `5 passed` |
| Retained Storage Core / authoring kit | pass | `uv run pytest --run-full-regression tests/cli_runtime/test_storage_core_cli.py -q` → `4 passed`; `uv run pytest tests/cli_runtime/test_wrappers.py tests/unit/infra/test_authoring_kit_assets.py -q` → `304 passed, 9 skipped` |
| S40B focused contract | pass | `uv run pytest --run-full-regression tests/unit/infra/test_authoring_kit_assets.py tests/cli_runtime/test_storage_core_cli.py tests/cli_runtime/test_distribution_cutover.py -q -k "target_catalog or removed_surface or retained or gitignore or s40b or storage_core"` → `11 passed, 302 deselected` |
| Fresh external catalog | pass | temporary repository `init` materialized only the two skill trees and retained `ci.yml`; no `spec-dock-chatgpt` |
| Formatting | pass | `git diff --check` |

S40Bのprovider / test差分はstep commit前であり、fresh `code-reviewer`のpassとpost-commit clean / upstream一致を閉じるまでS20へ進まない。S20はこのphysical treeからCurrent catalogを導出し、historical-only manifestを追加する。既存consumerのclassifier、prune、uninstall mutationはS25以降の未着手範囲である。

### S20 Current / historical catalog validation

S20では、S40B後のphysical `install_root`からCurrent assetのpath、regular-file SHA-256、modeをread-onlyで導出する`src/spec_dock/managed_distribution.py`と、consumerへコピーしないprovider-private `src/spec_dock/assets/managed_distribution.json`を追加した。ManifestはCurrent catalogを複製せず、historical sectionのpath grammar、kind、lowercase SHA-256、trace source、duplicate / nested identity / ancestor-descendant / Current overlap、schema fieldsをfail-closedで検証する。`build_distribution_plan`は`actions=()`を返し、S20ではconsumer scan、classifier、CLI接続、write / deleteを行わない。

| 観測 | 結果 | 証拠 |
|---|---|---|
| RED seed | pass | module未作成状態で`uv run pytest tests/unit/infra/test_managed_distribution.py -q` → `ModuleNotFoundError` |
| S20 bounded GREEN | pass | `uv run pytest tests/unit/infra/test_managed_distribution.py -q` → `20 passed` |
| S20 required selection | pass | `uv run pytest tests/unit/infra/test_managed_distribution.py -q -k "catalog or manifest or overlap"` → `6 passed, 14 deselected` |
| S20 + S40B focused regression | pass | `uv run pytest --run-full-regression tests/unit/infra/test_managed_distribution.py tests/unit/infra/test_authoring_kit_assets.py tests/cli_runtime/test_storage_core_cli.py tests/cli_runtime/test_distribution_cutover.py -q` → `333 passed` |
| Read-only / formatting | pass | no target write in S20 tests、`git diff --cached --check` |

S20レビューで、recognized version anchors / trusted manifest claimsのnested identityをoverlap検査から漏らしていたP1を検出した。全historical sectionを再帰的に検査し、Current pathとの祖先・子孫衝突を拒否する実装とnegative testsへ修正した。S20のfresh re-review pass、S40B scope re-review pass、step commit / clean / upstream一致後にS25 classifierへ進む。

### S25 Ownership classifier / Current collision

S25では`managed_distribution.py`へ読み取り専用のTarget分類を追加した。provider Current assetに加えてcanonical `spec -> spec-dock/scripts/spec-dock` shortcutを合成し、Fresh / update / `init --force` / uninstallのoperation別にmissing、current-identical、direct historical、trusted manifest + target identity、unknown collision、exact directory、symlink container、hard-link mutationを分類する。Freshではhistorical identityをupgradeせず`preserve-and-block`とし、recognized operationではknown historicalだけをupgrade / prune候補にする。consumer-side `owner`やmarker単独は信頼せず、manifest自身のknown bytesとprovider-private claim、実target identityの一致だけを補助証拠にした。`DistributionAction.diagnostic()`はrepository-relative path、classification、reason、operator actionだけを返し、source bytes・credential風文字列・repository外absolute pathを保持しない。S25ではwrite、delete、CLI接続、version / retry admissionを行わない。

| 観測 | 結果 | 証拠 |
|---|---|---|
| RED seed | pass | target_root / operation引数未実装時の`uv run pytest tests/unit/infra/test_managed_distribution.py -q -k "s25"` → `9 failed` |
| S25 bounded GREEN | pass | `uv run pytest tests/unit/infra/test_managed_distribution.py -q -k "s25"` → `17 passed, 20 deselected` |
| S20 + S25 + S40B focused regression | pass | `uv run pytest --run-full-regression tests/unit/infra/test_managed_distribution.py tests/cli_runtime/test_distribution_cutover.py tests/cli_runtime/test_storage_core_cli.py tests/unit/infra/test_authoring_kit_assets.py -q` → `350 passed` |
| Historical Current overlap / obsolete shape | pass | historical Current exact-path overlapを許可し祖先・子孫を拒否、obsolete exact recordのshapeを正規化してduplicate / Current collisionを検証 |
| Read-only / diagnostic sanitation | pass | target tree unchanged、diagnosticにsecret・source bytes・external absolute pathなし、`git diff --check` |

S25 fresh code reviewは、missing uninstallのno-op、canonical shortcutのhistorical evidence、synthetic Current overlap、Freshでのhistorical shortcut非materialization、current hard-link uninstallの5点を検出した。分類器と回帰テストを修正し、Freshでhistorical identityを`preserve-and-block`として明示分類する回帰も追加した。S25 bounded GREEN `17 passed`、S20 + S25 + S40B focused regression `350 passed`を再確認した。修正後のfresh re-review pass、step commit、clean / upstream一致後にS30へ進む。

### S30 No-follow apply / repository root rebind

S30では、S25で確定したblock-free planだけを対象に、provider Current bytesと合成shortcutをdescriptor-relativeなno-follow parent chainからmaterializeし、historical Current / obsolete targetをidentity再検証後にupgradeまたはpruneする`apply_distribution_plan`を追加した。Plan生成時にroot、ancestor、exact targetのdevice、inode、`ctime_ns`、type、link count、content/link identityをsnapshotし、apply開始前と各action直前に再照合する。missing regular fileは`O_CREAT | O_EXCL | O_NOFOLLOW`で作成し、regular upgradeはheld descriptorへ書き込み、pruneはheld parentのexact entryだけをunlinkする。symlink upgradeはplatformのno-replace rename capabilityを先に確認し、private staging symlinkとdescriptor-relative `RENAME_EXCL` / `RENAME_NOREPLACE`でpublishする。hard-link、symlink container、exact directory、root / parent差し替え、destination出現は例外で停止し、外部replacement・旧root・既存user bytesへ書き込まない。CLI、version marker、retry marker、recursive cleanupはS30の対象外である。

| 観測 | 結果 | 証拠 |
|---|---|---|
| S30 bounded GREEN | pass | `uv run pytest tests/unit/infra/test_managed_distribution.py -q -k "s30"` → `13 passed, 37 deselected` |
| S20 + S25 + S30 + S40B focused regression | pass | `uv run pytest --run-full-regression tests/unit/infra/test_managed_distribution.py tests/cli_runtime/test_distribution_cutover.py tests/cli_runtime/test_storage_core_cli.py tests/unit/infra/test_authoring_kit_assets.py -q` → `363 passed` |
| Root / parent rebind and destination race | pass | preflight前後、data write直前、既作成祖先の差し替え、destination出現を`DistributionApplyError`で停止し、replacement / 外部root / user bytesが不変 |
| No-follow / hard-link / shortcut | pass | missing Current、historical regular upgrade / prune、canonical shortcutのno-replace upgrade、hard-link uninstallをdescriptor-relativeに検証 |
| Syntax / formatting | pass | `python -m py_compile src/spec_dock/managed_distribution.py`、`git diff --check` |
| S30 fresh code review / re-review | pass | code-reviewerがTOCTOU、hard-link、symlink swap、staging cleanup、capability preflightを再確認し`findings=[]`, `review_status=pass` |

S30のfresh code reviewでは、書込み直前のroot / parent再bind、apply中に作成した祖先のidentity binding、hard-link countの最終検証、symlink upgradeのatomic swap、staging cleanupについて修正指摘を受けた。修正後は13件のS30テスト、focused regression 363件、mypy / ruff対象チェックを再実行した。no-follow / no-replace primitiveのcapabilityはparent作成前に検証し、未対応platformではempty parentを残すmutationも開始しない。再レビューpass、step commit、clean / upstream一致を閉じるまでS35へ進まない。

### S35 Version / retry marker admission

S35では、provider-private `managed_distribution.json`に実在する`0.2.3`のrecognized workspace entryと、`spec-dock/scripts/spec-dock` / `spec-dock/.gitignore`のSHA-256 anchorを登録した。`managed_distribution.py`へ読み取り専用の`admit_distribution_operation`を追加し、実行中package version、no-follow・link-count-oneのcanonical `MAJOR.MINOR.PATCH\n` marker、recognized allowlist、version-specific anchor、newer targetのdowngrade拒否を共通判定する。init / update / `init --force`では同一package・同一operation・同一repository rootのdevice / inodeへ束縛した`.distribution-retry.json`だけをforward retryとして許可し、uninstallでは既存`.uninstall-retry.json`のschemaを変更せず使用する。invalid、unknown、dual、operation / package / root mismatchは全mutation前に拒否し、`cli.py`のinit / update / uninstall入口へ接続した。

| 観測 | 結果 | 証拠 |
|---|---|---|
| S35 bounded GREEN | pass | `uv run pytest --run-full-regression tests/unit/infra/test_managed_distribution.py tests/cli_runtime/test_distribution_cutover.py -q -k "s35 or s40b"` → `16 passed, 50 deselected` |
| Version / marker focused regression | pass | `uv run pytest --run-full-regression tests/unit/infra/test_managed_distribution.py tests/unit/infra/test_init_update.py tests/cli_runtime/test_distribution_cutover.py -q -k "version or marker or force or cross_root"` → `16 passed, 2 skipped, 634 deselected` |
| Zero-write / cross-root | pass | malformed・BOM・CRLF・追加行、hard-link、newer、dual marker、A→B marker replayで`DistributionAdmissionError`を返し、consumer snapshot / marker bytes不変 |
| Legacy uninstall marker | pass | 既存`{"schema_version":1,"managed_by":"spec-dock","purpose":"uninstall-rerun"}`だけをversion欠損のuninstall retryとしてadmitし、新markerへ移行しない |
| Static checks | pass | `uv run ruff check src/spec_dock/managed_distribution.py tests/unit/infra/test_managed_distribution.py tests/cli_runtime/test_distribution_cutover.py`、`uv run mypy src/spec_dock/managed_distribution.py src/spec_dock/cli.py`、`python -m py_compile`、`git diff --check` |
| Broad regression | not adopted | 既存S40Bで削除済みlegacy assetを前提にした旧テスト群、およびanchor mismatchを意図的に作る旧updateテストが残るため、S35のstep gateにはfocused commandのみを採用 |

## Residual Risks / Follow-ups

* Issue 359 final headとmain mergeへR/D/Pを再照合した。S10でCurrent branch HEAD、Target二skill、provider / dogfood / packageのexact inventoryをlockした。
* Formal `issue start`はapproved planning commit / push後に成功し、active Issueは`iss-00360`である。
* Epic-local ArtifactとReportにIC-1 / IC-2 pass evidenceを記録し、Requirement / Design review、commit / push、formal start、Plan amendment、fresh local `spec-reviewer`、exact-current Strict pass、S00再確認、S10 inventory lock、S40A code review / focused test、S40B focused cutover / S20 catalog tests、S25 focused classifier tests、S30 no-follow apply、S35 admission focused testsを完了した。S35 fresh code review、step commit、clean/upstream一致後にS45へ進む。
* Historical digestは実際の過去package bytesから再現できるものだけをS10でlockする。再現不能なcandidateは推測登録せずpreserve-and-blockする。

## Notes

### Planning route

初期authoringでは利用者指示によりCodexが直接作成した。その後、利用者がChatGPT-Use-StrictとChatGPT-SpecReview-Strictの利用を明示したため、GitHub exact-mainをauthorityとするStrict routeへ切り替えた。通常の`planning create / apply`、`adoption_published`は使用していない。

ChatGPT-Use-Strictの出力はadvisory evidenceとして扱い、main orchestratorが現行source、test、Issue 357〜359 handoff、IC-1 / IC-2へ照合してcanonical候補へ統合した。最終authorityはrepository内のR/D/Pとfresh reviewer gateであり、Strict outputの自己主張ではない。

### Evidence inputs

* Epic 00356の承認済みRequirement / Design / Plan / Report
* Issue 357の360 handoff keep inventoryとStorage Core実装report
* Issue 358のTarget Authoring Kit、obsolete candidate、21-path preservation fixture、report
* Issue 359の二skill contract、18 managed + 3 legacy skill inventory、branch implementation / PR report
* Issue 360のevidence-only draft Requirement / Design / Plan
* `src/spec_dock/cli.py`の現行init / update / uninstall、exact obsolete path、bootstrap-only、collision-aware additive skill behavior
* provider / dogfood asset treeとinstaller test inventory

### Evidence Adoption Ledger

| ID | adoption_status | Source / role | Claim | Canonical target | Rationale / evidence | Blocking / next action |
|---|---|---|---|---|---|---|
| EAL-360-001 | adopted | ChatGPT-Use-Strict authoring evidence | Current physical authority、historical identity、deep module、operation × provenance、forward recovery、parityをR/D/Pへ具体化できる | Requirement / Design / Plan | GitHub connectorで`chemitaro/spec-dock` main SHA `a6ded0d9…`を確認し、session `required-strict-github-connector-verificati-65`の提案をlocal source / tests / IC evidenceへ照合した | no。canonical authorityはR/D/Pとfresh reviewer |
| EAL-360-002 | adopted | `implementation-planner` read-only draft | Plan round 1の5 P1をstep-local vertical TDD、Closure Index、delegation/review/commit gate、S90/S99/H10へ再構成する | Plan §4〜§9 | Canonical editなしのdraftをmain orchestratorがapproved R/Dとworkflow policyへ照合して統合した。S20順序・S45依存・S40A検証対象をamendし、fresh local reviewとStrict passを確認した | amendment後の現行Planは`approved` / `implementation-start-ready`。S10からstep executionへhandoff |
| EAL-360-003 | adopted | fresh `spec-reviewer` findings | Requirement / Design / PlanのP0/P1をphaseごとに検出し、修正範囲を限定する | R/D/P/report | Requirement round 3、Design round 3、Plan round 3のpassをraw authorityではなくreview evidenceとして採用した | no。Strict round 2 passで独立最終照合済み |

EAL-360-002の旧promotion gateはPlan amendment、fresh local `spec-reviewer`、current exact-upstream Strict passにより解消された。現行Planは`approved` / `implementation-start-ready`であり、S00再確認後にS10 inventory lockへ進む。

### Delegated Draft Evidence

| Draft | created_by_role | Scope / source | Allowed output | Diff guard | Adoption | Reviewer |
|---|---|---|---|---|---|---|
| Issue 360 Plan restructuring draft | `implementation-planner` | Issue 360 approved Requirement / Design、draft Plan / report、`phase_plan_issue.md`、`workflow_issue.md`、Plan round 1 findings | Chat response内のread-only section draft。Canonical、implementation、Artifactへのwrite禁止 | Workerはfile / Artifact変更なし。Main orchestrator統合後の`git diff --check` pass、`spec-dock validate` pass | EAL-360-002でadopted。Authority自己主張、promotion、readiness claimは不採用 | fresh Plan round 3 pass |

### Grade Specialist Evidence Gate

| Grade | Specialist | Availability / route | Output | Integration decision | Gate |
|---|---|---|---|---|---|
| strict | `implementation-planner` | available / used | 5件のP1を閉じるstep構造、Closure Index、concrete RED、delegation / reviewer / commit、S90 / S99 / H10 draft | main orchestratorがapproved R/Dと現行workflowへ照合しcanonical Planへ統合 | closed。fresh `spec-reviewer` round 3 pass |

### Spec Interpretation / Decision Ledger

| ID | Status | Type | Options considered | Disposition | Decision / evidence | Canonical promotion / follow-up |
|---|---|---|---|---|---|---|
| D-360-001 | resolved | authority | Current全量manifest / physical provider tree + historical-only manifest | adopted | Current catalogは物理provider treeから導出し、JSONへ全量複製しない。Provider-private manifestはhistorical identityとobsolete policyだけを持つ | Design §2、§4、Plan S10 / S30 |
| D-360-002 | resolved | safety | path / marker自己申告 / trusted manifest + target identity | adopted | Exact path、workspace marker、consumer manifestの自己申告だけではownershipを認めない。Known target identity、またはknown manifest bytes + provider-private target identityの一致だけを証拠にする | Requirement I360-RQ-009、Design §4.2 / §6、Plan S10 / S30 |
| D-360-003 | resolved | product boundary | CI削除 / cognitive CI維持 / deterministic Storage Core CI維持 | adopted | `.github/workflows/ci.yml`はcognitive workflowではなくdeterministic Storage Core CIとしてTargetへ維持し、Current reusable collision policyを適用する | Requirement I360-RQ-002 / 009、Design §4 / §6、Plan S40B |
| D-360-004 | resolved | migration safety | Freshでもobsolete prune / provenance別prune | adopted | Genuine Freshではobsolete pruneをせず、update / uninstallもunknown / modified assetをpreserve-and-blockする | Requirement I360-RQ-007〜009、Design §6 / §7、Plan S45 / S55 / S70 |
| D-360-005 | resolved | recovery | 全体atomic rollback / phase markerによるforward recovery | adopted | Portable atomic rollbackを主張せず、full preflight、apply-time identity再検証、phase marker、same-package forward retry、post-verifyを採用する | Requirement I360-RQ-012 / 013、Design §6.3 / §8、Plan S30 / S60 / S70 |
| D-360-006 | resolved | compatibility | marker統合 / operation別marker維持 | adopted | Init / updateは新`.distribution-retry.json`、uninstallは既存`.uninstall-retry.json`を維持する。両marker / invalid markerはblockし、暗黙移行しない | Design §8.1、Plan S35 / S60 / S65 / S70 |
| D-360-007 | resolved | package authority | fallback / marker単独 / provider asset + recognized version anchors | adopted | `.gitignore`は必須provider assetだけをsourceとし、version markerはcanonical exact allowlist、version固有anchor、downgrade拒否を一体で検証する | Design §4.1 / §7.3、Plan §3.1 / S10 / S35 / S40B |
| D-360-008 | resolved | recovery | adversarial完全防御 / detected raceのfail-closed境界 | adopted | Operation全体のatomicityではなく、通常process / handled filesystem failureを保証する。Same-UID hostile tampering等は検知時fail-closedとforward recoveryの境界にする | Design §6.3 / §8、Plan S30 / S60 |
| D-360-009 | resolved | lifecycle | gate統合 / 独立gate | adopted | IC-1 / IC-2、dependency readiness、formal `issue start`、R/D/P review、Strict reviewを別gateとして扱う | Requirement I360-RQ-001、Plan §2 / S00 |
| D-360-010 | resolved | downstream | Issue 360内でIC-3を自己承認 / Epic ownerへhandoff | deferred | IC-3 pass、未承認final Issue候補、Epic completionはIssue 360自身で自己承認しない。Planningをblockしない理由は、IC-3が実装・検証後にだけ判定できるEpic-owned downstream gateだからである | Plan H10でEpic ownerへread-only handoffし、Issue 360 closure時に再判定する |

### Spec Authoring Gate / Planning gate ledger

| Phase | Canonical artifact | Reviewer | Status | Evidence / next action |
|---|---|---|---|---|
| Requirement | `requirement.md` | fresh `spec-reviewer` | pass | round 3でP0/P1なし。IC-1 / IC-2、Design promotion、formal start、implementation handoffは非承認 |
| Design | `design.md` | fresh `spec-reviewer` | pass | round 3でP0/P1なし、confidence 0.98。Plan phaseへ昇格 |
| Plan | `plan.md` | amendment後fresh review | passed | S40A verificationを既存Storage Core CLI testへ限定し、S20本文順・依存graph・gate metadataを確認 | Plan `approved` / `implementation-start-ready`、S10へhandoff |

### Reviewer Gate Status

| Gate | Reviewer | Freshness | State | Risk acceptance | Promotion decision |
|---|---|---|---|---|---|
| Requirement | `spec-reviewer` | fresh round 3 | passed | none | Requirement approved |
| Design | `spec-reviewer` | fresh round 3 | passed | none | Design approved |
| Plan | `spec-reviewer` | amendment後fresh review | passed | S40A verificationを既存Storage Core CLI testへ限定し、S20本文順・依存graph・gate metadataを確認 | Plan `approved` / `implementation-start-ready`、S10へhandoff |
| ChatGPT-SpecReview-Strict | ChatGPT browser-only exact-upstream review | amendment後exact-current review | passed | session `issue-360-admission-current-strict`でGitHub exact SHA `8c01c9fd2e76d7d7bccc754bca902e8010026703`を検証、resolved `GPT-5.5` verified、P0/P1なし | implementation admissionを解消し、S00 / S10を開始 |

### ChatGPT-SpecReview-Strict round 1

Pre-submit session `required-strict-github-connector-verificati-66`はChatGPTのrate-limit dialog再表示で停止した。Recovery診断では`promptSubmitted=false`、conversation IDなし、leaseなしであり、review結果として数えない。共有Pro sessionのterminal完了後、new-submission gateを満たすことを確認してfresh reviewを開始した。

Session `required-strict-github-connector-verificati-67`はGitHub connectorで`chemitaro/spec-dock`、current Issue 360 branch、exact SHA `e7520e6a433c0b6345b4f52f1172c32f56fad9d3`を検証し、requested `gpt-5.5-pro`、resolved label `GPT-5.5`、model verification `yes`で完了した。Requirement / Designにformal start前のcheckout-safety停止とreview未完了が現在形で残る一方、Report / Planはformal startとphase reviewの成功を記録しているため、S00の現在地が一意でないというP1を1件検出し、`review_status=fail`となった。

Findingはrepository factsと一致したため採用し、Requirement I360-RQ-001とDesign §1を最新lifecycle evidenceへ同期した。Product scope、migration contract、acceptance criteria、implementation stepは変更していない。修正commitを同名upstreamへpushし、別のfresh Strict conversationでexact-SHA re-reviewするまでimplementation blockを維持する。

### ChatGPT-SpecReview-Strict round 2

Session `required-strict-github-connector-verificati-68`はGitHub connectorで`chemitaro/spec-dock`、current Issue 360 branch、exact SHA `4b325885b82dbffa26cdd5cd372d3914e8d604ef`を検証し、requested `gpt-5.5-pro`、resolved label `GPT-5.5`、model verification `yes`で完了した。P0 / P1はなく、`review_status=pass`、overall confidence 0.91である。Requirement / Design / Planはhard cutover、ownership / provenance、path safety、retry / recovery、Fresh / update / uninstall、parity、docs、IC-3 handoffを相互にtraceでき、実装開始を妨げる矛盾または必須欠落はないと判定された。

唯一のfindingは、親Epic Reportの進捗サマリーがIssue 360のDesign / Plan具体化中、formal start未完了のまま残るというP2であった。これは旧Planに対する履歴であり、S20順序のP1を受けてPlan amendmentとfresh gateを再開した。後続のround 3でamendment後SHAを再検証し、implementation-start-readyへ戻した。

### ChatGPT-SpecReview-Strict round 3（current admission）

Session `issue-360-admission-current-strict`はGitHub connectorで`chemitaro/spec-dock`、current Issue 360 branch、exact SHA `8c01c9fd2e76d7d7bccc754bca902e8010026703`を検証し、requested `gpt-5.5-pro`、resolved label `GPT-5.5`、model verification `yes`で完了した。S20がS40A legacy Runtime retirementとS40B shipped Target physical cutoverの後に配置され、S40Aの検証が既存`tests/cli_runtime/test_storage_core_cli.py`へ限定され、S45がS35を前提とすることを確認した。Requirement / Design / Plan / Reportのgate状態もfresh local `spec-reviewer` passと整合し、P0 / P1なし、`review_status=pass`、overall confidence 0.92となった。この結果によりPlanを`approved` / `implementation-start-ready`へ維持し、S00 / S10を開始する。

### Design review round 1

Fresh reviewerは次のP1を検出し、Design / Plan / Decision Ledgerへ反映した。

* Preflight後も各mutationでrootからno-follow再bindし、device / inode / `ctime_ns` / type / link count / content identityを再検証する。差異時はpathname cleanupを行わない。
* Consumer-side manifestの自己申告を信頼せず、manifest自身のknown historical identityとprovider-private target path + target identityの両方を必須にした。
* Init / update用`.distribution-retry.json`と既存uninstall用`.uninstall-retry.json`を統合せず、dual / invalid markerをblockする一意なmigration契約へ決定した。
* `.gitignore`を必須provider assetとして単一distribution planへ含め、hard-coded fallbackを削除する方針を固定した。
* Provider / dogfood / testのAdd / Modify / Delete / Read-only treeとshared-symbol dependency deltaを追加した。

P2のrecognized / unrecognized `init --force`とmarker matrix、AC別verification trace、Decision Ledgerも同時に追加した。

### Design review round 2

別のfresh reviewerはround 1の5件が解消済みであることを確認したうえで、次の追加findingを検出した。

* `spec-dock.version`を「valid」とする構文、known-version admission、version固有anchor、実行中version、downgrade、retry例外を明文化した。
* Decision Ledgerの`Status`を解決状態、`Disposition`をadopted / rejected / deferredとして分離し、IC-3 deferredの非blocking理由とrevisit条件を記録した。
* Dependency diagramにTitle / Question / Scope / Excluded / Update triggerとedge labelを追加した。

Round 2のP1 / P2を反映済みとした。

### Design review round 3

別のfresh reviewerが最新Design / Reportをapproved RequirementとDesign phase基準へ再照合した。Round 2のversion admission predicate、Decision Ledger分離、dependency diagram metadata / edge意味はいずれも解消済みで、新規P0 / P1なし、confidence 0.98の`pass`と判定した。このpassによりDesignを`approved`へ昇格し、Plan reviewへ進む。

### Plan review round 1

Fresh reviewerはproduct scope / migration設計を概ね反映済みとしつつ、実装開始可能なcommand queueとして次のP1を検出した。

* S20〜S70のhorizontalなRED / layer batchingを、一つのobservable behaviorごとにRED / GREEN / review / commitを閉じるvertical sliceへ分解する。
* 全ACとfilesystem / marker / package / scope riskを追跡する`Spec-Locked Closure Index`を置く。
* 各implementation stepへdepends / unblocks、source、target、allowed / forbidden、delegated role、verification、stop、report、review / re-review、commit / cleanを固定する。
* S90をdocs impact、S99をqa / issue-wide code / specの三者final gateとし、IC-3 input handoffをその後のH10へ分離する。
* Repository root rebindとcross-root retry marker replayをzero-writeで拒否するnegative closureを追加する。

`implementation-planner`のread-only draftを上記findingへ限定して採用し、Plan §4〜§9をS00 / S10 / S20 / S25 / S30 / S35 / S40A / S40B / S45 / S50 / S55 / S60 / S65 / S70 / S80 / S85 / S90 / S95 / S99 / H10へ再構成した。Fresh round 2はpendingである。

### Plan review round 2

別のfresh reviewerはround 1の5件すべてが解消済みであることを確認した。新規P1として、Requirement / Designが要求するdiagnostic sanitationがrequired Closure Indexとstep-local negative testへ固定されていない点を検出した。

`C360-RISK-DIAGNOSTIC-SANITATION`をrequired closureとして追加し、S25 classifier diagnosticとS60 fault / retry diagnosticへcredential風文字列、source bytes、repository外absolute pathの非包含test、owner、verification command、report destinationを固定した。Fresh round 3を待つ。

### Plan review round 3

別のfresh reviewerがapproved Requirement / Designと最新Plan / Reportを再照合した。Diagnostic sanitationはrequired Closure Index、S25 / S60のstep-local negative test、verification command、report destination、S95 / S99まで追跡可能であり、round 1の5件にも回帰なし、新規P0 / P1なし、confidence 0.99の`pass`と判定した。このpassによりPlanを`approved`へ昇格した。

### Requirement review round 1

Fresh reviewerは次のP1を検出し、Requirementへ反映した。

* Planning selection、IC-1 / IC-2 handoff approval、Runtime dependency readinessを分離した。
* Storage Coreの決定論的な`.github/workflows/ci.yml`をTargetへ維持した。
* Obsolete pruneをexact pathではなくoperation × provenanceで判定し、ownership未証明時は全mutation前に停止する契約へ修正した。
* Root `README.md`、installed migration guide、retained scripts / system / template / Workbench MarkdownをCurrent docs auditへ追加した。

### Requirement review round 2

Fresh reviewerは、retained `.github/workflows/ci.yml`が利用者所有の同名workflowと衝突した場合の挙動をP1として検出した。Current target全般をmissing、byte-identical、proven historical、ownership unknownへ分類し、最後のclassは既存bytesを保持して全mutation前に停止する契約とacceptanceを追加した。

### Requirement review round 3

別のfresh reviewerがRequirementを親Epic、Issue 357〜359 handoff、installer / asset現物と再照合し、P0 / P1なしの`pass`と判定した。このpassはRequirement単体の品質gateであり、IC-1 / IC-2の充足、Design promotion、formal `issue start`、実装着手を承認しない。

### Lifecycle state

初回`issue start`はdependency readinessを満たさず実行開始を拒否した。利用者が指定したfallbackに従い、`active set iss-00360`でIssue 360を選択し、ユーザーがIssue 359 branchからIssue 360 branchを作成した。Issue 359 merge後はdependency `ready=true`となったが、再試行はdirty worktree safetyで停止した。IC-1 / IC-2とR/D/P reviewを閉じ、planning commitを同名upstreamへpushした後、formal `issue start iss-00360`を再実行してIssue checkout / auto-syncを含めsuccessした。Post-startもactive Issue、dependency、validation、local / upstream SHAを実測している。
