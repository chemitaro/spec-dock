---
種別: レポート（Issue）
ID: "iss-00392"
タイトル: "Provider Lifecycle And Regression Gate Hard Cutover"
関連GitHub: ["#392"]
状態: "approved"
最終更新: "2026-09-11"
依存:
  - "requirement.md"
  - "design.md"
  - "plan.md"
  - "artifacts/20260908t011846z-luna-max-implementation-handoff.md"
  - "artifacts/20260908t011846z-01-lifecycle-test-ownership-and-migration.md"
  - "artifacts/issue-392-human-guide.html"
親: ["epic-00384", "init-local-00003"]
実装開始許可: true
repository_evidence:
  role: "implementation-candidate-source"
  repository: "chemitaro/spec-dock"
  branch: "iss-00392-provider-lifecycle-and-regression-gate-hard-cutover"
  sha: "ee356a3bbad2168e337d223f084270b02fd03f64"
  tree: "b2ce649b566ae8405725da3d52485857a84a0e4a"
implementation_evidence:
  candidate_sha: "ee356a3bbad2168e337d223f084270b02fd03f64"
  candidate_tree: "b2ce649b566ae8405725da3d52485857a84a0e4a"
---

# #392 仕様・実装レポート

## 1. Outcome

Issue #392の実装可能な仕様候補として、Requirement、Design、critical-level Plan、Luna Max checkpoint handoff、test ownership/migration Artifact、日本語HTMLガイドを一つのpackへ整列しました。

初回仕様作成時に行ったのは調査、仕様作成、静的自己検証です。その後、仕様を実装candidateへ反映し、CP1–CP4、focused test、package/dogfood parity、default fast、current full verifierを実行しました。P1修正、First Red再修正、dogfood projection、最終remediation、承認済み`seed_admission` v2、固定seedの危険型をmutation前に拒否する追加修正、初回適用時のadmission snapshot保持、unsafe parent bindingのWire収束、public record/private stateのexpected witness bindingを含む直近の実装candidateは`ee356a3bbad2168e337d223f084270b02fd03f64`です。実装時点の詳細な証拠は§9〜§19に記録します。

## 2. Source verification facts

- GitHub connectorでrepository `chemitaro/spec-dock`、branch `iss-00392-provider-lifecycle-and-regression-gate-hard-cutover`を取得しました。
- 仕様確認時のbranch tipのfull object IDは`dc638e936e763cc7a6087f258201ed9ed654e7fb`で、strict wrapperのexpected SHAと完全一致しました。実装candidateの現在値はrepository_evidenceと§9に分離して記録しています。
- 仕様確認時のverified commit treeは`17ce38234033393c385c4b17e40c0ccdc78bfc19`です。
- 最初にroot `AGENTS.md`を読み、`src/spec_dock/`をProduct source、checked-in `spec-dock/`をdogfood projection、PR mergeをhuman-onlyとして扱いました。
- `attachments-bundle.zip`を一時directoryへ展開し、relative pathを維持した68 filesを列挙・検索しました。内訳の19 `.pyc` filesは入力ノイズとして無視し、成果物へ含めていません。
- 添付内のEpic/Issue canonical documentsとselected source filesは、verified commitのGitHub blob/pathへ照合しました。相違時はGitHubを優先する規則で処理しました。
- 仕様確認時のGitHub上の`spec-dock/spec-dock.version`はexact bytes `0.2.3\n`でした。

## 3. Reviewed scope facts

次の範囲を仕様根拠として確認しました。

- Epic #384 Requirement、Design、Plan。
- `provider-lifecycle-wire-contract.md` v12、`active-failure-disposition-register.md`、`epic-integration-branch-contract.md`、`rolling-wave-issue-elaboration-contract.md`。
- Accepted ADR群。特に`20260908t011139z-adr-lifecycle-preparation-and-initial-record-failure-contract.md`。
- Issue #392の既存Requirement、Design、Plan、Report、全direct-child Artifact。
- `src/spec_dock/cli.py`、`src/spec_dock/managed_distribution.py`、`src/spec_dock/assets/managed_distribution.json`、runtime wrapperとapplication/commands/infraのlifecycle・checkout・worktree・make関連symbol。
- `pyproject.toml`、provider workflow、`tests/conftest.py`、root ledger/timing、distribution/runtime/checkout/worktree tests。
- Provider assetsとchecked-in dogfoodの二skill/runtime/docs境界。

確認した現行symbolには、installer側の`_exclusive_distribution_operation`、`_admit_distribution_cli`、`_install_fresh_distribution`、`_install_recognized_distribution_unlocked`、`_run_uninstall_deprovision`、`_run_uninstall_explicit_spec_history_purge`、runtime側の`checkout_active_target`、`issue_start`、`worktree_create`、`worktree_remove`、Git CLIのdirect checkout/worktree helpers、`run_make_init_if_available`が含まれます。

## 4. Specification decisions recorded

本packは親Wireのpublic inventoryを変更せず、`RECORD-TEMP`のmodeだけ既存atomic-publication要件から一意に導かれるclarificationとして親Wireへ反映し、次をIssue実装判断として閉じます。

1. Four fixed roots、two exact skill slots、strict seven-key compact JSON record、two fresh-only seeds、protected consumer data。
2. Six-domain candidate digest、digest外のslot marker、verified Git objects由来のexact-clean 0.2.3 fixture。
3. Consumer外・same-filesystem・repository inode/euid-bound private namespace。
4. `prepared|running|ready|terminal-cleanup` ACTIVE、completion receipt、bounded inode witnessのclosed schema。
5. WIR-PREP-001を含むwrite orderとP0/P1/P2。P2はdurable stageを検証・再利用しstage write 0。
6. Linux `renameat2`、macOS `renameatx_np`のnative atomic Adapter。Unsafe fallbackなし。
7. Stdlib-only pre-import bootstrap、runtime SH、installer EX、release-to-exec、direct stream/status propagation。
8. Managed helperの`pass_fds` lifetime、parent-only SIGKILL proof、same-generation pinned checkout。
9. Worktree B create/remove、entrypoint-last、path C preservation、make terminal handoff。
10. Old writer/manifest/test retirementをsuccessor GREEN後へ限定し、provider-first packaging/dogfood/current gatesを維持。
11. 四つのcausal checkpointを一つの#392 PRへ収束。#392→#395→#396の順序、人間merge、B1を維持。

## 5. Static self-verification actually executed

成果物作成directoryに対して次を機械検査し、すべてpassしました。

- 必須成果物6 files（Report/manifest作成前段階）の存在・non-empty。
- Canonical Markdownと二ArtifactのYAML front matter、ID、parent、`関連GitHub`、`実装開始許可=false`。
- Markdown relative links 4件がpackage内に閉じ、全targetが存在。
- 未解決作業マーカーとplaceholder-only行なし。
- Wire v12 actual extraction: status 6、code 41、phase 23、last-completed-phase 24、relation 168、public JSON goldens 40、record goldens 4。全JSON block parse成功。
- Baseline actual extraction: total 15、active 14、resolved 1、timing count 243、exact resolved successor一致。
- `tests/conftest.py` actual extraction: required-fast exact four一致。
- 添付sourceの23 existing path/symbol checksが一致。
- HTML: `lang=ja`、`data-plantuml-contract=2`、`@plantuml/core@1.2026.6`、six PlantUML sources/targets/source copies、remote PlantUML includeなし。
- HTML modal: click/Enter/Space、50%–300% zoom、focus trap、Escape、backdrop close、focus restoreを静的確認。
- HTML classic/module JavaScript 2 blocksを`node --check`し、syntax error 0。

このself-verificationは仕様packの構造・整合性を対象とし、Product behaviorのGREENを意味しません。

## 6. Independent review and remediation

- Reviewed SHA: `449fefc7864aa1f983aa66e6e768faee74a7eda1`
- Reviewer session: `required-strict-github-connector-verificati-763`
- Review artifact SHA-256: `4f5820536480bd5456316d7ab2aa3865b8b1f43f5174d150cf06e6bab9047fbb`
- Result: `review_status=fail`、P1×4、P2×1

P1は、CP2のT12/version ownership、directory mode identity、`RECORD-TEMP` mode、CP3/CP4 dogfood順序です。P2はclosed `rendered_command`へabsolute targetが入り得る事実とprivacy説明の不一致です。これは仕様review時点の記録であり、実装と実装後のreview結果は§9に記録します。

同じブルーチームauthoring conversationによる分析で5件を再現しました。T12/version ownership、`RECORD-TEMP`、dogfood順序、privacy説明は既存authorityから一意に訂正し、Directory modeはcanonical値を確認した上で仕様へ反映しました。実装後の独立Code Review Strictで検出された指摘と修正は§9へ移管します。

## 7. Implementation and merge gate

`実装開始許可=true`です。CP1–CP4、独立レビューのP1修正、First Red再修正、provider-first dogfood projection、最終remediation、stageの凍結候補再検証、承認済み`seed_admission` v2、固定seedの危険型をmutation前に拒否する追加修正、初回適用時のadmission snapshot保持、unsafe parent bindingのWire収束、public record/private stateのexpected witness bindingを含む実装candidate commit `ee356a3bbad2168e337d223f084270b02fd03f64`を固定しました。report更新前のclean実装SHAとbranch upstreamの一致確認、および次の最終ゲートが残っています。

1. このReport更新を含む最終SHAのclean pushとupstream SHA一致。
2. 実装candidate `c6a9278bb752571a4cb3305aa41c8d2d47036522`に対する独立Code Review StrictのP0/P1ゼロ・pass。直近のv8はP1×1を検出し、修正を反映済みです。
3. 最終Quality Gate Strictの実施条件成立。
4. 人間による#392 PRのEpic integration branchへのmergeと、merged tip B1再検証。

CP4後もagentはmergeしません。人間が#392 PRを`codex/epic-00384-provider-test-strategy-planning`へmergeし、merged tipでB1を再検証します。B1 GREEN後だけ#395を開始します。

## 8. Residual blocker and uncertainty

前回の`29a61963`時点のレビュー記録に続き、stage再構築後の凍結候補digest再検証を`467fe0e`、承認済みACTIVE schema v2の`seed_admission`（固定seedの入場時`absent|present`を永続化し、再入場・action provenance・create判定で再観測しない）を`ec626c03`へ回帰テスト付きで反映しました。以下の過去レビュー記録は履歴として保持し、現行candidateの検証結果は§9末尾の追補を正とします。

親public valueまたはIssue責務の追加は不要です。`RECORD-TEMP`のparent clarificationはpublic inventoryを変えません。実装candidateのfocused/package/default-fast検証とclean pushは完了しています。実装後の独立 Code Review Strict（`699d54bf`固定、browser、GPT-5.6 Sol、Extra High、完全bundle）は、#395 baselineを除きP1×2、P2×3を指摘しました。Blue Team分析でP1×2を有効なblocking指摘として実装修正対象に確定し、`4a6aba91`で修正、`0d993252`でdogfood projectionを完了しました。続くFirst Red分析でP1×5とcoverage gapを同一batchの修正対象に確定し、`c7d6dd62`へ回帰テスト付き修正を反映しました。さらにfresh Code Review Strict（`29a61963`固定）で検出されたP1×8をBlue Teamがすべてvalid/blockingと判定し、`29a61963`へ追加の回帰修正を反映しました。P2×3は現在の親ポリシーによりreport-onlyとして保持しています。`01f2631b`で検出された再入場のfixed seed型preflight迂回を修正し、同じreviewerによるfresh Strict re-review v5-3は`41e0e3e3330c0b1bcec54a46310ead4c8d538bef`に対して本文JSON `review_status=pass`（P0/P1=0）となりました。Final Quality Gate Strict、人間PR merge、merged-tip B1は未完了です。

current full verifierの`ledger-mismatch` 10件は#395が所有するactive baselineのsignature/coverage mismatchであり、#392の責務へ取り込まず、skip/xfailやledger変更で隠していません。残るgateはReport更新後のclean push、Final Quality Gate Strict、#395 baselineと#392 GREEN要求の権限判断、人間PR review/merge、merged-tip B1です。これらが未完了のため、本ReportはIssueの最終certification、Product GREEN、merge完了を主張しません。

## 9. Implementation verification update

2026-09-10時点の実装candidate commit `29a6196342327338c45e8f14455665fe41f931b4`（tree
`451623f3bff9d14c7f7883c622fd7fc5ffc07110`）に対して、次の証拠を採取しました。

- provider-firstでprivate namespaceのrepository parent、固定top、repository-key namespaceをdescriptor-relative/no-followで再認証し、dry-runと各private storeの実読取り経路へ同じfull-chain bindingを適用しました。topまたはnamespaceのowner、mode、device、type、inodeが変化した場合はforeign private authorityとしてfail-closedし、dry-runでは作成・修正を行いません。
- worktree Bはtarget reservation後の`OSError`、`RuntimeError`、`CalledProcessError`を候補再試行せず停止し、reservation、Git worktree add、materialization、pre/post-publication verification、consumer-hook bindingのphaseと、path、branch、Git record、payload path、entrypointのartifact stateを開示します。Git metadata取得後やmaterialization途中で失敗してもrollback・remove・別candidate retryを行いません。
- provider runtimeとchecked-in dogfood runtimeを同期し、二つのslot markerとdogfood `spec-dock.version`のcandidate digest `6339d918f2f3310e78550d6ed0f5038c815bc8646c9e2006711ac1309913cd40`を一致させました。`seed_policy=preserve-only`のdogfood update semanticsはfresh installの`create-if-absent`と混同していません。provider/dogfoodの同期対象はbyte一致を確認し、canonical `spec-dock update . --json` は`update-completed`でstage cleanupまで完了しました。
- 今回の回帰修正は、full private chainの再入場検証、ACTIVEとbootstrapのrepository identity binding、running中のtarget/STAGE混在からのforward recovery、exchange前のold root保持、expected incomplete recordのparent fsync/revalidation、prepared uninstall dry-runのread-only分類、ACTIVE/receipt実I/O fault seam、terminal target kind witness、狭いbootstrap admission catch、閉じたpackage facadeに加え、leased root FDへのprivate namespace結合、不確定な準備状態の安全側分類、invalid requestのwire準拠、receipt先行保存、foreign stage ownership/payload検証、部分失敗時のoperation/seed別action vector、incomplete uninstall precedence、呼び出し元cwd起点の外部handoffを実装しました。追加した回帰テストは全て実装契約に対応し、obsolete behaviorのassertionは残していません。
- `make lint`はruff check、ruff format、mypyすべてpass、`TMPDIR=/private/tmp uv run pytest`は`1101 passed, 848 skipped`でした。macOSの既定`TMPDIR`では`/var`のOS aliasがcomponent-wise `O_NOFOLLOW`に当たるため初期化系2件がcoordination-unavailableとなる環境差を確認し、product/CIのno-follow契約を弱めず、検証用作業領域を`/private/tmp`へ固定しました。clean fixed pointのdistribution cutoverは`10 passed`、Epic distributionは`11 passed`、provider lifecycleは`246 passed`、外部handoffは`8 passed`でした。追加したT01 relation witnessはWire partial action profileの全mutation rejectを含めて`176 passed, 3 deselected`、関連engineケースは`10 passed`でした。local `validate`は`nodes=236`、provider/dogfood parityは`parity-ok`でした。
- `TMPDIR=/private/tmp uv run python -m scripts.quality.verify_full_regression --shards 4`は`1949 tests collected`、4 shard exit 1、status=`ledger-mismatch`でした。ledgerはtotal15／active14／resolved1、timing 243 entriesを維持し、violationは10件（#395 active baselineのruntime import 8、runtime shell 1、workbench 1）で、#392起因の`unexpected_failure`は0件でした。候補の3実失敗はこの固定点の既知baseline行に対応するsignature/coverage mismatchであり、ledger／timing／required-fastの変更はありません。レートリミットを理由にbundleや検証範囲を縮小していません。
- `29a61963`を対象にした直近のfresh Code Review Strict（browser-only、GPT-5.6 Sol、Extra High、完全bundle、約351k tokens）は、本文JSONで`review_status=fail`、P1×8を返しました。P1はseed/action phase profile、preserve-onlyのlast-completed phase、再開uninstallの呼出開始時absence、ACTIVEなしincomplete uninstall、ACTIVE/receipt不一致、非directory target、regular-file FD witness、flock後のvisible root rebindでした。Blue Teamのfresh ChatGPT Use Strict分析（browser-only、GPT-5.6 Sol、Pro、完全packet）は8件すべてをvalid/blocking・同一batch修正と判定し、`29a61963`へ回帰テスト付き修正を反映しました。P2のunsafe repository root分類とGit closure属性はreport-onlyで保持しています。最終SHAを対象にした再Code Review Strict、Final Quality Gate Strict、PR merge後B1は未完了です。

以上により、#392のCP1–CP4実装candidate、P1 remediation、provider-first packaging、dogfood parity、回帰テスト、current gate観測の証拠は`29a6196342327338c45e8f14455665fe41f931b4`へ更新済みです。ただしcurrent full verifierの#395 baseline mismatchと、Report更新後の最終Strict review／Final Quality Gateが残るため、Issue完了・Product GREEN・merge完了はまだ主張しません。最終Strict reviewとFinal Quality Gateは、このReportを含む次のclean pushed SHAに対して実施します。

## 10. Prior candidate addendum (2026-09-11, before re-entry repair)

当時の実装candidateは`3a4884e1e4dab3c9ddf46573ffb65f7b835f2115`（tree `1b6b970adbac9274e9ab384872cd2d8ddebf1960`）です。`467fe0e`でstage再構築後に凍結候補digestを再検証し、`ec626c03`でRequirement/Design/Planに反映したACTIVE schema v2の`seed_admission`を実装しました。今回`3a4884e1`で、`_dispatch_new`の共通admissionに`SEED_PATHS`の型検証を追加しました。各seedをno-followで観測し、`absent`と`regular`だけを許可し、symlink・directory・FIFOなどの既存非regular seedは、receipt無効化、ACTIVE作成、stage作成、record/consumer mutationより前に既存の`unsafe-target-type` blocked resultとして返します。updateでは`operation=update`／`seed_policy=preserve-only`、legacy migrationでは`operation=install`／`seed_policy=preserve-only`を保持します。public Wire v12、`seed_admission`の`absent|present`、preserve-onlyの「削除機能を復活させない」契約、#395 baselineは変更していません。

- First Red: 追加したupdate 6ケース（2 seed paths × symlink/directory/FIFO）とlegacy migration 2ケース（2 seed paths × FIFO）は、修正前にすべて失敗し、late seed phaseの`WireValidationError`とmutationを確認
- First Green: `tests/unit/provider_lifecycle/test_engine.py -k 'unsafe_seed_type_blocks_before_admission_mutation or legacy_unsafe_seed_type_blocks_before_admission_mutation'` は `8 passed`
- focused provider-lifecycle（engine/private state）: `60 passed`
- provider-lifecycle全体: `258 passed`
- default fast: `1113 passed, 848 skipped`
- `make lint`: ruff check、ruff format、mypy pass
- full verifier: `1961 tests collected`、4 shard exit 1、status=`ledger-mismatch`、既知の#395 baseline violation 10件、#392起因の`unexpected_failure` 0件

full verifierの詳細は`spec-dock/.workbench/full-regression/20260910T180530.534640Z/result.json`にあり、`candidate_sha`は`3a4884e1e4dab3c9ddf46573ffb65f7b835f2115`と一致します。baseline violationはruntime import S10 signature mismatch 8件、runtime shell S11 coverage mismatch 1件、workbench signature mismatch 1件で、ledger・timing・required-fast・bundleを変更していません。レートリミットを理由にbundleや検証範囲は縮小していません。対象acceptance/dogfood/bootstrap/handoffは個別実行で`72 passed`でしたが、subset指定により全体ledger coverage mismatchの終了コード3となるため、full verifierの判定には使用していません。

直近のfresh Code Review Strict（`required-strict-github-connector-verificati-804`、`94c6c30f`固定、browser-only、GPT-5.6 Sol、Extra High、完全bundle）は本文JSONで`review_status=fail`、P1×1でした。Blue Teamのfresh分析（`required-strict-github-connector-verificati-805`、browser-only、GPT-5.6 Sol、Extra High、完全packet）はこのP1をvalid/blocking、実装/common admission修正、既存Wire v12の再利用と判定しました。`3a4884e1`の修正後、同じreviewerによるfresh Strict re-review、Final Quality Gate Strict、人間PR merge、merged-tip B1は未完了です。

## 11. Code implementation candidate addendum (2026-09-11, before report-only evidence freeze)

コード実装candidateは`01f2631b59ac4d1a27b095ab7508865db3afcf41`（tree `afdee8be47321d78ffe96ef4bc2ba83e00aa7ad6`）で、後続の`ca55d720`はReport-only evidence freezeです。`3a4884e1`の共通admission修正に対する同一reviewerの再入場指摘を受け、`_resume_or_block`の非uninstall再入場でも、stage準備およびrunning-stage検証、receipt/ACTIVE/record/consumer mutationより前に既存の`_admit_existing_seeds`を呼び出すよう修正しました。`active.operation`と`active.seed_policy`を使用し、symlink・directory・FIFOなどのunsafe fixed seedは既存の`unsafe-target-type` blocked resultへ収束します。`legacy-0.2.3`のtarget/record authorityを保持し、updateの`operation=update`／`seed_policy=preserve-only`、legacy migrationの`operation=install`／`seed_policy=preserve-only`、Wire v12、ACTIVE schema v2の`seed_admission`、uninstall分岐を変更していません。

- First Red: `update|legacy migration` × `prepared|running` × 2 fixed seed paths × `symlink|directory|FIFO`の24ケースが、修正前にunsafe type検出前のre-entry経路を通過することを確認
- First Green: `TMPDIR=/private/tmp uv run pytest tests/unit/provider_lifecycle/test_engine.py -k reentry_unsafe_seed_type_blocks_before_admission_mutation` は `24 passed, 51 deselected`
- engine: `TMPDIR=/private/tmp uv run pytest tests/unit/provider_lifecycle/test_engine.py` は `75 passed`
- provider lifecycle: `TMPDIR=/private/tmp uv run pytest tests/unit/provider_lifecycle` は `282 passed`
- default fast: `TMPDIR=/private/tmp uv run pytest` は `1137 passed, 848 skipped`
- static: `make lint` は ruff check、ruff format、mypyすべてpass
- full verifier: `TMPDIR=/private/tmp uv run python -m scripts.quality.verify_full_regression --shards 4` は `1985 tests collected`、4 shard exit 1、status=`ledger-mismatch`、`evaluation.verified=false`

full verifierの詳細は`spec-dock/.workbench/full-regression/20260910T191330.416991Z/result.json`にあり、`candidate_sha`は`01f2631b59ac4d1a27b095ab7508865db3afcf41`と一致します。violationは10件で、runtime import S10のsignature mismatch 8件、runtime shell S11のcoverage mismatch 1件、workbenchのsignature mismatch 1件です。4 shardの実結果で全件がcollect・executeされています。これらはactive-failure disposition registerでIssue #395が所有する既知baseline行であり、#392起因の新規lifecycle/provider `unexpected_failure`は0件です。#392ではledger、timing、evaluator、required-fast、skip/xfail、baseline行、bundleを変更していません。レートリミットを理由にbundleや検証範囲を縮小していません。従って、full verifierをGREENやexit 0として表現せず、#395所有baselineと#392のGREEN要求の権限矛盾は未解決のblocking issueとして保持します。

直近のCode Review Strict v7（reviewed SHA `22441c3a37effcb5e64371706338d8f651b228c1`、browser-only、GPT-5.6 Sol、Extra High、完全bundle）は本文JSONでP1×1、`review_status=fail`を返しました。レビューartifactのSHA-256は`3e8cd7b47bc87fd016e3cc103510e96e0f538a49d301e092ae8d08784f5bfc76`です。Blue Teamの同一目的再分析 v8（session `required-strict-github-connector-verificati-807`、browser-only、GPT-5.6 Sol、Extra High、9ファイル完全証拠束）は、P1を実質修正済み・正式クローズは同一reviewerの再レビュー待ちと判定し、full verifierの10件と#395境界を実証しました。分析packetは`issue-392-review-v8-evidence-packet.md`、応答ログはOracle session `required-strict-github-connector-verificati-807`に保存されています。

このaddendumは、機能削減後に不要となった旧機能を再導入せず、削除対象を確認するだけのobsolete testを追加・保持しない方針で記録しています。現候補では同一reviewerのfresh Strict re-review、`review_status=pass`（P0/P1=0）、Final Quality Gate Strict、人間PR merge、merged-tip B1が未完了です。人間の受入判断なしに#395のbaseline修正、ledger/evaluator変更、GREEN偽装、Issue finish、PR mergeは行いません。

## 12. Report-bound candidate addendum (2026-09-11)

Report-only evidence freeze後のbranch tipは`ca55d72007cf0b558985aa828520f9b2738a9f91`（tree `7deee611e66813c3470a075c633d350b1170fb67`）です。実装コードは`01f2631b`から変わらず、reportのcandidate/evidence bindingだけを更新しました。このSHAに対して、同じcanonical commandを再実行し、full verifierの`candidate_sha`が一致することを確認しました。

- `TMPDIR=/private/tmp uv run python -m scripts.quality.verify_full_regression --shards 4`: `1985 tests collected`、4 shard exit 1、status=`ledger-mismatch`、`evaluation.verified=false`
- violation: runtime import S10 signature mismatch 8件、runtime shell S11 coverage mismatch 1件、workbench signature mismatch 1件
- active verified: 4件、resolved verified: 1件、#392起因の新規lifecycle/provider `unexpected_failure`: 0件

full verifierの詳細は`spec-dock/.workbench/full-regression/20260910T221056.722381Z/result.json`です。4 shardの実結果は全件をcollect・executeし、前回の`01f2631b`実行と同じ#395所有baseline violation集合を示しました。full verifierはGREENでもexit 0でもなく、#392ではledger、timing、evaluator、required-fast、skip/xfail、baseline行、bundleを変更していません。従って、このreport-bound candidateは実装と証跡の束ね直しを完了していますが、同一reviewerのfresh Strict re-review、Final Quality Gate Strict、#395所有baselineと#392 GREEN要求の権限判断、人間PR merge、merged-tip B1は未完了です。

## 13. Uninstall unsafe-seed remediation addendum (2026-09-11)

同一reviewerによるfresh Code Review Strict v4b（reviewed SHA `13a343e990227cf96be4f75fa1138510989fbc61`、browser-only、GPT-5.6 Sol、Extra High、完全37-file bundle）は、本文JSONでP1×1、`review_status=fail`を返しました。指摘は、valid ready/legacy workspaceの初回uninstallとprepared/running再入場uninstallが、fixed seedのsymlink・directory・FIFOを`present`として扱い、receipt/ACTIVE/stage/record/consumer mutationまたはplanへ進む共通admission迂回です。レビューartifactのSHA-256は`396fee8a419d374a2348eca5aa809ba4bc9382144ca129146f510d024865b423`です。

Blue Teamのfresh Strict分析（session `required-strict-github-connector-verificati-808`、browser-only、GPT-5.6 Sol、Extra High、full verifier evidence packet）は、このP1をvalid/reachable/in-scope/merge-blockingと判定しました。修正は既存`_admit_existing_seeds`を再利用し、Wire v12の`operation=uninstall`、`candidate_digest=null`、`seed_policy=preserve-only`、preflight、last-completed=`request-validation`、`mutation_started=false`、empty actionsを保持する実装修正としました。#395のfull-verifier baseline mismatchは別責務として扱い、ledger、timing、evaluator、skip/xfail、bundleは変更していません。

`86b219605d4c678c0f044acd16b81848995f9b41`では、初回uninstallのdry-run/applyとprepared/running再入場のdry-run/applyにseed admissionを接続しました。apply再入場はstage準備・running-stage検証前、dry-run再入場は既存のstage owner/payload検証後かつtarget plan前に分類します。新たなWire/schema/stateは追加せず、obsolete behaviorを確認するだけのtestも追加していません。

- First Red: `ready-origin|exact-legacy-origin` × 初回`dry-run|apply` × 2 seed paths × `symlink|directory|FIFO`（24件）、および同origin × `prepared|running` × 再入場`dry-run|apply` × 2 seed paths × 3 unsafe types（48件）を、合計72件すべて修正前に失敗させ、`completed|planned`への迂回を確認
- First Green: `TMPDIR=/private/tmp uv run pytest tests/unit/provider_lifecycle/test_engine.py -k 'initial_uninstall_unsafe_seed_type or uninstall_reentry_unsafe_seed_type' -q --tb=short` は `72 passed, 75 deselected`
- engine: `TMPDIR=/private/tmp uv run pytest tests/unit/provider_lifecycle/test_engine.py` は `147 passed`
- provider lifecycle: `TMPDIR=/private/tmp uv run pytest tests/unit/provider_lifecycle` は `354 passed`
- default fast: `TMPDIR=/private/tmp uv run pytest` は `1209 passed, 848 skipped`
- static: `make lint` は ruff check、ruff format、mypyすべてpass
- commit/push: `86b219605d4c678c0f044acd16b81848995f9b41`、branch upstreamと一致、worktree clean
- full verifier: `TMPDIR=/private/tmp uv run python -m scripts.quality.verify_full_regression --shards 4` は `2057 tests collected`、4 shard exit 1、status=`ledger-mismatch`、`evaluation.verified=false`

full verifierの詳細は`spec-dock/.workbench/full-regression/20260910T231201.276215Z/result.json`です。`candidate_sha`は`86b219605d4c678c0f044acd16b81848995f9b41`と一致し、active verifiedは4件、resolved verifiedは1件、violationは10件です。内訳はruntime import S10のsignature mismatch 8件、runtime shell S11のcoverage mismatch 1件、workbenchのsignature mismatch 1件で、前回と同じ#395所有baseline集合です。#392起因の新規lifecycle/provider `unexpected_failure`は0件です。full verifierはGREENまたはexit 0ではなく、Final Quality Gate Strict、#395 baselineと#392 GREEN要求の権限判断、人間PR merge、merged-tip B1が未完了です。

Final Quality Gate前の同一reviewer fresh Strict re-review v5-3は、`41e0e3e3330c0b1bcec54a46310ead4c8d538bef`を対象にbrowser-only、GPT-5.6 Sol、Extra High、完全37-file bundleで実施しました。本文JSONは`findings=[]`、`overall_correctness=patch is correct`、`review_status=pass`、P0/P1=0で、response SHA-256は`88051d6c27991fac5be69673c6cf31f62170ceae834b9de425e979cc8303f9e9`です。レビュー自身はテストを再実行しておらず、Report記録の証拠を参照しています。Report更新後の最終SHAを対象とするFinal Quality Gate Strictは未実施です。

## 14. Seed admission snapshot remediation addendum (2026-09-11)

実装candidate `5666bcc904ce6bbee3ddd1d5a97c928f35b2875f`（parent `7b1178713108ed159aabb417d1a2cd18484eaaa6`、tree `d7ffcf58545f69234cfb0dbd6624785ff258c05d`）に対して、Code Review Strict v6のP1「receipt無効化後のseed admission再観測」を修正しました。レビューはbrowser-only、GPT-5.6 Sol、Extra High、完全bundleで、review sessionは`issue-392-code-review-v6`、review responseのSHA-256は`e98042e7e7d234b09ac41eabc976b8cb8b02764628dbd1b9576b2065c7cedf46`です。Blue Teamのfresh Strict分析（session `required-strict-github-connector-verificati-812`、browser-only、GPT-5.6 Sol、Extra High、transcript SHA-256 `0439eff1f1eac3b139238a1714ba849f7d8dc404b7eb064e53dacb1462c7e65a`）は、このP1をvalid、reachable、in-scope、implementation-remediationとして判定しました。

修正は、初回の`_admit_existing_seeds`が同じ`_observe_target`結果から返す`absent|present` mappingを、updateおよび初回uninstallの`_start_or_run`から`_prepare_active`まで渡し、receipt無効化後に二度目の観測を行わないものです。re-entryの安全側admissionチェックは保持し、ACTIVEに保存済みのmappingを再入場で上書きしません。`_observe_seed_admission`は本番call-siteを確認した上で削除しました。Wire v12、ACTIVE schema v2、record、receipt、ledger、public API、#395 baseline、bundle、required-fast、skip/xfail方針は変更していません。

- First Red: `test_t04_initial_apply_persists_first_seed_admission_without_post_receipt_reobservation`を`update|uninstall`で追加し、修正前は2件とも失敗（171件deselected）。既存completion receiptを作成した後、receipt無効化直後にseedを変更するfault seamで、初回admission snapshotが失われることを確認
- First Green: 同focused testは`2 passed, 171 deselected`
- engine: `TMPDIR=/private/tmp uv run pytest tests/unit/provider_lifecycle/test_engine.py` は`173 passed`
- provider lifecycle: `TMPDIR=/private/tmp uv run pytest tests/unit/provider_lifecycle` は`380 passed`
- default fast: `TMPDIR=/private/tmp uv run pytest` は`1235 passed, 848 skipped`
- static and SpecDock validation: `make lint`（ruff check、ruff format、mypy）はpass、`./spec-dock/scripts/spec-dock validate`は`nodes=236`
- full verifier: `TMPDIR=/private/tmp uv run python -m scripts.quality.verify_full_regression --shards 4`は`2083 tests collected`、`507 passed, 6 skipped, 3 failed`、4 shard exit 1、status=`ledger-mismatch`、`evaluation.verified=false`

full verifierの詳細は`spec-dock/.workbench/full-regression/20260911T030914.314882Z/result.json`です。`candidate_sha`は`5666bcc904ce6bbee3ddd1d5a97c928f35b2875f`と一致します。violationは従来どおり10件（runtime import S10のsignature mismatch 8件、runtime shell S11のcoverage mismatch 1件、workbenchのsignature mismatch 1件）で、実際の3失敗も同じ#395所有baseline行に対応します。#392起因の新規lifecycle/provider `unexpected_failure`は0件です。#392では検証範囲、bundle、ledger、timing、evaluator、required-fast、skip/xfail、baseline行を変更していません。レートリミットを理由にbundleや検証範囲を縮小していません。

今回の回帰テストはreceipt境界の正しい実装契約を検証するものであり、削除した旧機能の存在だけを確認するobsolete testではありません。このReport更新時点では、最終clean push SHAに対するCode Review Strict fresh re-reviewとFinal Quality Gate Strict（Pro）が残っています。#395 baselineの修正、GREEN偽装、Issue finish、PR mergeは行いません。

## 15. Strict review and Final Quality Gate result addendum (2026-09-11)

`ddd150b344ca8f3678ae49564f4b742def24fbf3`に対するCode Review Strict v7は、browser-only、GPT-5.6 Sol、Extra High verified、complete relevant bundleで実施し、本文JSON `findings=[]`、`overall_correctness=patch is correct`、`review_status=pass`、P0/P1=0を返しました。review sessionは`issue-392-review-v7`、response bodyのSHA-256は`90a7178a1798054f0d736ce0355ab93fcfb681073a9312ae2e951f1de30e58d3`です。レビューはテスト実行を主張せず、同一SHAのCodex test laneを別証拠として扱いました。

同じFQG v2 campaign `issue-392-final-20260911`の既存レビュアー会話によるFinal Quality Gate Strict follow-upは、browser-only、GPT-5.6 Sol、Pro verifiedで`ddd150b344ca8f3678ae49564f4b742def24fbf3`をレビューし、`status=pass`、`coverage_complete=true`、P0/P1=0、`unresolved_items=[]`を返しました。Oracle sessionは`fqg-v2-ae0569fe-0da7c0f3`です。前回のP1 obligation `FQG-SEED-UNINSTALL-ALREADY-ABSENT`は`closed`です。P2は`FQG-UNSAFE-BINDING-WIRE-MAPPING`、`FQG-GIT-ATTRIBUTE-SCOPE`、`FQG-CANONICAL-GATE-STATE`の3件で、FQG規約どおり情報提供のみ・修正対象外です。

FQGは#392のP0/P1とselected scopeをpassと判定しましたが、required test commandsを実行したとは主張していません。同一SHAでCodexが実行したdefault fast、lint、full verifierの結果は§14およびcampaign `test-results/manifest.json`に記録しています。full verifierの`ledger-mismatch`は10件の#395所有baseline mismatchであり、#392起因の新規lifecycle/provider `unexpected_failure`は0件です。Code Review StrictとFinal Quality Gate Strictは、human PR mergeおよびmerged-tip B1とは別ゲートです。ここでのFQG passはIssue finish、#395 baseline修正、PR merge、Product GREENを意味しません。

## 16. Unsafe parent binding remediation addendum (2026-09-11)

`c6a9278bb752571a4cb3305aa41c8d2d47036522`（tree `e6f41598cc1c2ca6af506e4032852dfcb88414d1`）を、固定seedの中間parentがsymlinkまたはregular fileへ置換された場合に、既存Wire v12の`unsafe-parent-binding`へ収束させる実装candidateとして記録します。Code Review Strict v8（reviewed SHA `1141db29c93dec20c521e83d23cfc2eebc2122fd`、browser-only、GPT-5.6 Sol、Extra High、完全bundle、約55 files／約1.089M tokens）は、本文JSONでP1×1、`review_status=fail`を返しました。review sessionは`issue-392-review-v8`、response bodyのSHA-256は`4887102de2b639c6d7fbed710677dd81a8b7341290dfe148274e8611dfbceafc`です。指摘は、`.github`または`.github/workflows`の親がsymlink・regular fileのとき、`_observe_target`のno-follow parent openが発生させる`ELOOP|ENOTDIR`を、初回・再入場のinstall/update/uninstallでclosed Wireへ分類できず、wrong wireまたはraw `OSError`へ漏らし得る点でした。

Blue Teamのfresh ChatGPT Use Strict分析（session `required-strict-github-connector-verificati-814`、browser-only、GPT-5.6 Sol、Extra High、top-level `https://chatgpt.com/`から開始）は、このP1をvalid／reachable／in-scope／blockingと判定しました。分析packetは`.workbench/chatgpt-final-quality-gate-strict-v2/issue-392-final-20260911/code-review-analysis-packet-v8.md`です。最小修正として、`_admit_existing_seeds`の観測境界だけで`errno.ELOOP`と`errno.ENOTDIR`を既存の`_AdmissionFailure("unsafe-parent-binding")`へ変換し、それ以外の`OSError`は従来どおり再送出する方針を採用しました。`_observe_target`、Wire v12、ACTIVE schema、public JSON、ledger、evaluator、bundle、required-fast、skip/xfailは変更していません。

回帰テストは、初回install/update、初回uninstallのapply/dry-run、update/uninstallのprepared/running再入場について、`.github`と`.github/workflows`、symlinkとregular fileを組み合わせた40ケースです。すべて、admission前の`blocked`、`code=unsafe-parent-binding`、`candidate_digest=null`、適切なoperation／seed policy、`phase=preflight`、`last_completed_phase=request-validation`、`mutation_started=false`、empty actions、workspace/private state無変更を確認します。これは削除した旧機能の存在を確認するobsolete testではなく、既存Wireの公開分類と無変更契約を確認する実挙動回帰テストです。

- First Red: `TMPDIR=/private/tmp uv run pytest tests/unit/provider_lifecycle/test_engine.py -k unsafe_seed_parent_binding -q --tb=short` は、修正前に40件すべて失敗し、初回のwrong wireと再入場のraw `OSError`漏出を確認
- First Green: 同じfocused testは`40 passed, 173 deselected`
- provider lifecycle: `TMPDIR=/private/tmp uv run pytest tests/unit/provider_lifecycle -q --tb=short` は`420 passed`
- default fast: `TMPDIR=/private/tmp uv run pytest -q --tb=short` は`1275 passed, 848 skipped`
- static and SpecDock validation: `make lint`（ruff check、ruff format、mypy）はpass、`./spec-dock/scripts/spec-dock validate`は`nodes=236`
- implementation commit/push: `c6a9278bb752571a4cb3305aa41c8d2d47036522`、upstream SHAと一致、worktree clean
- full verifier: `TMPDIR=/private/tmp uv run python -m scripts.quality.verify_full_regression --shards 4` は`2123 tests collected`、4 shard exit 1、status=`ledger-mismatch`、`evaluation.verified=false`

full verifierの詳細は`spec-dock/.workbench/full-regression/20260911T052030.524878Z/result.json`です。`candidate_sha`は`c6a9278bb752571a4cb3305aa41c8d2d47036522`と一致し、violationは10件（#395 active baselineのruntime import S10 signature mismatch 8件、runtime shell S11 coverage mismatch 1件、workbench signature mismatch 1件）でした。#392起因の新規lifecycle/provider `unexpected_failure`は0件です。前回のdirty実行で出たcandidate wheelのunexpected failureは未commit変更による作業ツリー汚染だったため、clean実行の結果には含めていません。レートリミットを理由にbundleや検証範囲を縮小せず、#395の台帳・timing・evaluator・baseline行を変更していません。

このReport追記後のreport-bound SHAに対する同一reviewerのfresh Code Review Strict、Final Quality Gate Strict（Pro）、および人間PR merge／merged-tip B1は未完了です。full verifierの#395 baseline mismatchを#392へ取り込まず、Issue finish、Product GREEN、PR merge完了も主張しません。

## 17. Filesystem identity-boundary remediation addendum (2026-09-11)

`1c26266a814ceac341b9b559cd5b0489267fa7db`（parent `9898bfcba47a923b4270841347bcfcaedb0171ae`）では、直前のFinal Quality Gate StrictおよびBlue Team分析で特定されたfilesystem identity-boundaryのP1を修正しました。engine内に残っていた重複domain scannerを削除し、provider filesystemの単一bound captureへ統合しました。captureはrootのpre/open/post/visible identity、nested directoryのpre/open/post/visible identity、regular fileのpre/open/post/hash/visible identity、symlinkのreadlink pre/post identityを確認し、regular hard linkを拒否します。engineのstage validation、running-stage validation、re-entry observation、stage cleanup、stage removal、target observationはこのbound captureを使用します。engine固有のregular modeおよび相対symlink target制約はengine側に保持し、generic filesystemの挙動を過剰に狭めていません。

同時に、repository rootのno-follow openでは`ENOENT`、`ENOTDIR`、`ELOOP`だけを既存Wire v12の`unsafe-repository-binding`へ分類し、その他のOS errorは従来のunavailable扱いを保持しました。seed parent chainのadmissionでは`ELOOP`、`ENOTDIR`だけを既存の`unsafe-parent-binding`へ収束させ、missing `.agents`をfresh installで合法的に作成できる経路を壊さないよう、`.agents`および`.agents/skills`のmatrixも追加しました。Wire、ACTIVE schema、ledger、evaluator、required-fast、skip/xfail、bundle、rate-limitを理由とした検証範囲は変更していません。

回帰証拠は次のとおりです。

- `TMPDIR=/private/tmp uv run pytest tests/unit/provider_lifecycle/test_atomic_filesystem.py tests/unit/provider_lifecycle/test_authority.py -q`: `20 passed`
- `TMPDIR=/private/tmp uv run pytest tests/unit/provider_lifecycle/test_engine.py -q`: `255 passed`
- `TMPDIR=/private/tmp uv run pytest tests/unit/provider_lifecycle -q`: `469 passed`
- `TMPDIR=/private/tmp uv run pytest -q --tb=short`: `1324 passed, 848 skipped`
- `make lint`: ruff check、ruff format、mypyすべてpass
- `TMPDIR=/private/tmp uv run python -m scripts.quality.verify_full_regression --shards 4`: `2172 tests collected`、4 shard exit 1、`status=ledger-mismatch`、`evaluation.verified=false`

full verifierの詳細は`spec-dock/.workbench/full-regression/20260911T081102.979354Z/result.json`です。`candidate_sha`は上記実装candidateと一致し、violationは10件（runtime import S10のsignature mismatch 8件、runtime shell S11のcoverage mismatch 1件、workbenchのsignature mismatch 1件）でした。これは#395が所有する既知baselineであり、#392起因の新規lifecycle/provider `unexpected_failure`は0件です。検証範囲、ledger、timing、evaluator、required-fast、skip/xfail、baseline行、bundleを変更していません。機能削減に伴うobsolete-only testは追加・保持していません。

この追補時点では、上記commitを含むReport-bound SHAのpush後に行うfresh Code Review Strict（Extra High）とFinal Quality Gate Strict（Pro）、人間PR merge、merged-tip B1が未完了です。従って、Issue finish、Product GREEN、PR merge完了はまだ主張しません。

## 18. Target binding and slot-marker race remediation addendum (2026-09-11)

Code Review Strict v10およびBlue Teamのfresh Strict分析で特定されたP1「観測済み対象と公開直前のスロット／対象が別inodeへ置換されても、pathname再オープンの結果を採用し得る」を、`ed49ee25e41be899dc2f579bdbfbf9d5e3216b0e`（parent `0260ccf9204d2867bd79e8d0fd50c4b7ecbc9cd3`）で修正しました。入場時に得た固定対象の`_ObservedTarget`をACTIVE準備とdry-run計画まで渡し、receipt無効化後やACTIVE準備後に対象を再観測して元のownership証拠を上書きしないようにしました。公開・detach前には、ACTIVEの元対象または正当なterminal candidateだけを許可します。

スロットマーカー判定は、入場時に観測した対象のinode witnessと、同じ対象をdescriptor-relativeに開いたdirectoryのidentity、およびvisible entryのidentityを比較してから、同じdirectory descriptor上でマーカーを読みます。読み取り後にもdescriptor／visible identityを再確認し、A/Bスロット置換、marker pathnameの別対象読み取り、candidate判定のpathname再オープンを拒否します。元状態が`absent`のfresh installと、マーカーを持たない`legacy-0.2.3`の旧対象は従来どおり扱い、Wire v12、ACTIVE schema、public JSON、record、receipt、ledger、evaluator、required-fast、skip/xfail、bundleは変更していません。

追加テストは、削除した旧機能の存在だけを確認するobsolete-only testではなく、実際の公開境界を検証する回帰テストです。valid markerを持つA/Bスロットの差し替えをupdate admission中に発生させ、foreign slotとしてpreflightで停止するケースと、update/uninstallのadmission後・publication前に固定docs対象をforeign directoryへ差し替え、観測済みACTIVE bindingを再利用して`verify-target`で停止するケースを追加しました。A/B競合テストではmarker読み取りの同一descriptor要件も検証します。

- focused race tests: `TMPDIR=/private/tmp uv run pytest tests/unit/provider_lifecycle/test_engine.py -k 'slot_marker_admission_rejects_replaced_slot_root or admission_target_observation_is_reused_before_publication' -q --tb=short` は`3 passed`
- engine: `TMPDIR=/private/tmp uv run pytest tests/unit/provider_lifecycle/test_engine.py -q --tb=short` は`258 passed`
- provider lifecycle: `TMPDIR=/private/tmp uv run pytest tests/unit/provider_lifecycle -q --tb=short` は`472 passed`
- default fast: `TMPDIR=/private/tmp uv run pytest -q --tb=short` は`1327 passed, 848 skipped`
- static and SpecDock validation: `make lint`（ruff check、ruff format、mypy）はpass、`./spec-dock/scripts/spec-dock validate`は`nodes=236`
- implementation commit: `ed49ee25e41be899dc2f579bdbfbf9d5e3216b0e`、parentは`0260ccf9204d2867bd79e8d0fd50c4b7ecbc9cd3`、commit直後のworktreeはclean
- full verifier at implementation SHA: `TMPDIR=/private/tmp uv run python -m scripts.quality.verify_full_regression --shards 4` は`2175 tests collected`、4 shard exit 1、status=`ledger-mismatch`、`evaluation.verified=false`

full verifierの詳細は`spec-dock/.workbench/full-regression/20260911T092128.196303Z/result.json`です。`candidate_sha`は実装commitと一致し、violationは10件（#395 active baselineのruntime import S10 signature mismatch 8件、runtime shell S11 coverage mismatch 1件、workbench signature mismatch 1件）でした。#392起因の新規lifecycle/provider `unexpected_failure`は0件です。既知baselineのledger mismatchを#392の修正として隠さず、#395の台帳・timing・evaluator・required-fast・skip/xfail・baseline行・bundleを変更していません。レートリミットを理由としたbundleまたは検証範囲の縮小も行っていません。

この追補後は、reportを含む最終clean push SHAに対する同一reviewerのfresh Code Review Strict（Extra High）と、同じFQG v2 campaignによるFinal Quality Gate Strict（Pro）が未完了です。Code Review v10のP2「nested driftのunsafe-parent-binding分類」はreport-onlyとして残しており、P1修正でWire分類を変更していません。human PR merge、merged-tip B1、Issue finish、Product GREENは別ゲートであり、ここでは完了を主張しません。

## 19. Public predecessor and private expected-witness remediation addendum (2026-09-11)

実装candidate `ee356a3bbad2168e337d223f084270b02fd03f64`（parent `244a6badd0c5ac49bfa80b71e3d1bb9120550908`、tree `b2ce649b566ae8405725da3d52485857a84a0e4a`）へ、Final Quality Gate Strictで検出されたP1を修正しました。直前のFQG v2（browser-only、GPT-5.6 Sol、Pro、top-level `https://chatgpt.com/`から開始、reviewed SHA `244a6badd0c5ac49bfa80b71e3d1bb9120550908`、Oracle session `fqg-v2-e33906bb-0376134b`）は、`status=fail`、P1×3、P2×2を返しました。P2のGit attribute scopeとcoordination error分類はreport-onlyとして保持し、修正対象をP1に限定しました。

P1修正では、ACTIVE private schemaをv3へ更新し、operation-owned public `spec-dock.version`の`public_record_witness`をdurableに保存します。初回公開はACTIVEのoriginal predecessor、終端公開はACTIVEのexpected incomplete predecessorへbytesとinode identityを束縛し、foreignまたはcontent-equalな別inodeを交換・削除せずpreserve-and-blockします。exchange residueは対応するexpected predecessorとして再検証し、再入場時にも安全にcleanupします。`ActiveStateStore`／`CompletionReceiptStore`にはreadと同時にwitnessを返す経路と、expected witnessまたはexpected absentを要求するatomic saveを導入し、receipt invalidation、ACTIVE更新、terminal cleanupのunlinkまで同じvalidated witnessを引き回します。Wire v12、public result、receipt schema、ledger、required-fast、skip/xfail、bundleは変更していません。

追加した回帰テストは、削除した旧機能の存在だけを確認するobsolete-only testではなく、public record predecessor、private ACTIVE／receipt、terminal cleanupのforeign inode置換と、exchange residueの再入場cleanupを実際のmutation境界で検証します。レートリミットを理由にテストまたはbundleを縮小していません。

- provider-lifecycle focused: `uv run pytest tests/unit/provider_lifecycle/test_private_state.py tests/unit/provider_lifecycle/test_engine.py -q` は `274 passed`
- default fast: `TMPDIR=/private/var/folders/0v/jkf8ysk1621277d4xmr584cc0000gn/T uv run pytest -q` は `1334 passed, 848 skipped`
- static and SpecDock validation: `make lint`（ruff check、ruff format、mypy）はpass、`./spec-dock/scripts/spec-dock validate`は`nodes=236`
- clean full verifier: `TMPDIR=/private/var/folders/0v/jkf8ysk1621277d4xmr584cc0000gn/T uv run python -m scripts.quality.verify_full_regression --shards 4` はcandidate SHAが`ee356a3bbad2168e337d223f084270b02fd03f64`に一致し、`2182 tests collected`、4 shard exit 1、`status=ledger-mismatch`、`evaluation.verified=false`

clean full verifierの詳細は`spec-dock/.workbench/full-regression/20260911T124545.962807Z/result.json`です。violationは1件のみで、`tests/cli_runtime/test_runtime_shell_s11.py::TestRuntimeShellS11::test_final_api_call_site_and_structural_regression`の既知#395 active baseline `coverage_mismatch`です。#392起因の新規`unexpected_failure`は0件で、#395の台帳・timing・evaluator・required-fast・skip/xfail・baseline行は変更していません。clean実装commit後のworktreeはcleanでした。

直前のCode Review Strict v11（browser-only、GPT-5.6 Sol、Extra High、reviewed SHA `244a6badd0c5ac49bfa80b71e3d1bb9120550908`）は本文JSON `findings=[]`、`review_status=pass`、P0/P1=0でしたが、public/private witness remediationを含む`ee356a3b`は未レビューです。このreport更新後に、更新済みreportを含むclean pushed SHAへfresh Code Review Strict（Extra High）とFinal Quality Gate Strict（Pro）を実施します。human PR merge、merged-tip B1、Issue finish、Product GREENは別ゲートとして未完了です。
