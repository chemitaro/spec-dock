---
種別: レポート（Issue）
ID: "iss-00392"
タイトル: "Provider Lifecycle And Regression Gate Hard Cutover"
関連GitHub: ["#392"]
状態: "approved"
最終更新: "2026-09-10"
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
  sha: "e6a201471a0c07885807f866a81ed2a6b08359ee"
  tree: "053dd350c8e853fc81a55ba53ffecaf02bdded2d"
implementation_evidence:
  candidate_sha: "e6a201471a0c07885807f866a81ed2a6b08359ee"
  candidate_tree: "053dd350c8e853fc81a55ba53ffecaf02bdded2d"
---

# #392 仕様・実装レポート

## 1. Outcome

Issue #392の実装可能な仕様候補として、Requirement、Design、critical-level Plan、Luna Max checkpoint handoff、test ownership/migration Artifact、日本語HTMLガイドを一つのpackへ整列しました。

初回仕様作成時に行ったのは調査、仕様作成、静的自己検証です。その後、仕様を実装candidateへ反映し、CP1–CP4、focused test、package/dogfood parity、default fast、current full verifierを実行しました。P1修正とdogfood projectionを含む現行candidateは`e6a201471a0c07885807f866a81ed2a6b08359ee`です。実装時点の詳細な証拠は§9に記録します。

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

`実装開始許可=true`です。CP1–CP4、独立レビューのP1修正、provider-first dogfood projectionを含む実装candidate commit `e6a201471a0c07885807f866a81ed2a6b08359ee`を固定し、branch upstream と同一であることを確認しました。次の最終ゲートが残っています。

1. Report を現行candidateへ更新した最終SHAのclean pushとupstream SHA一致。
2. 現行candidateと更新後Reportを含む最終SHAに対する独立Code Review StrictのP0/P1ゼロ・pass。
3. 最終Quality Gate Strictの実施条件成立。
4. 人間による#392 PRのEpic integration branchへのmergeと、merged tip B1再検証。

CP4後もagentはmergeしません。人間が#392 PRを`codex/epic-00384-provider-test-strategy-planning`へmergeし、merged tipでB1を再検証します。B1 GREEN後だけ#395を開始します。

## 8. Residual blocker and uncertainty

親public valueまたはIssue責務の追加は不要です。`RECORD-TEMP`のparent clarificationはpublic inventoryを変えません。実装candidateのfocused/package/default-fast検証とclean pushは完了しています。実装後の独立 Code Review Strict（`699d54bf`固定、browser、GPT-5.6 Sol、Extra High、完全bundle）は、#395 baselineを除きP1×2、P2×3を指摘しました。Blue Team分析でP1×2を有効なblocking指摘として実装修正対象に確定し、`4a6aba91`で修正、`0d993252`でdogfood projectionを完了しました。P2×3は現在の親ポリシーによりreport-onlyとして保持しています。Report更新後のclean pushed SHAに対する再レビュー、Final Quality Gate Strict、人間PR merge、merged-tip B1は未完了です。

current full verifierの`ledger-mismatch` 10件は#395が所有するactive baselineのsignature/coverage mismatchであり、#392の責務へ取り込まず、skip/xfailやledger変更で隠していません。残るgateはReport更新後のclean pushed Strict review、Final Quality Gate Strict、人間PR review/merge、merged-tip B1です。これらが未完了のため、本ReportはIssueの最終certification、Product GREEN、merge完了を主張しません。

## 9. Implementation verification update

2026-09-10時点の実装candidate commit `e6a201471a0c07885807f866a81ed2a6b08359ee`（tree
`053dd350c8e853fc81a55ba53ffecaf02bdded2d`）に対して、次の証拠を採取しました。

- provider-firstでprivate namespaceのrepository parent、固定top、repository-key namespaceをdescriptor-relative/no-followで再認証し、dry-runと各private storeの実読取り経路へ同じfull-chain bindingを適用しました。topまたはnamespaceのowner、mode、device、type、inodeが変化した場合はforeign private authorityとしてfail-closedし、dry-runでは作成・修正を行いません。
- worktree Bはtarget reservation後の`OSError`、`RuntimeError`、`CalledProcessError`を候補再試行せず停止し、reservation、Git worktree add、materialization、pre/post-publication verification、consumer-hook bindingのphaseと、path、branch、Git record、payload path、entrypointのartifact stateを開示します。Git metadata取得後やmaterialization途中で失敗してもrollback・remove・別candidate retryを行いません。
- provider runtimeとchecked-in dogfood runtimeを同期し、二つのslot markerとdogfood `spec-dock.version`のcandidate digest `531e39bb77cb6f6e2edf405b8e78f0c089da2bbd5246a47b3620c364e1aa04be`を一致させました。`seed_policy=preserve-only`のdogfood update semanticsはfresh installの`create-if-absent`と混同していません。provider/dogfoodの同期対象はbyte一致を確認し、canonical `spec-dock update . --json` は`update-completed`でstage cleanupまで完了しました。
- 今回の回帰修正は、full private chainの再入場検証、ACTIVEとbootstrapのrepository identity binding、running中のtarget/STAGE混在からのforward recovery、exchange前のold root保持、expected incomplete recordのparent fsync/revalidation、prepared uninstall dry-runのread-only分類、ACTIVE/receipt実I/O fault seam、terminal target kind witness、狭いbootstrap admission catch、閉じたpackage facadeに加え、leased root FDへのprivate namespace結合、不確定な準備状態の安全側分類、invalid requestのwire準拠、receipt先行保存、foreign stage ownership/payload検証を実装しました。追加した回帰テストは全て実装契約に対応し、obsolete behaviorのassertionは残していません。
- `make lint`はruff check、ruff format、mypyすべてpass、default fastは`1074 passed, 847 skipped`でした。clean fixed pointのdistribution cutover/integrationは`21 passed`で、Issue #392の受入・provider lifecycle・dogfood・handoff各suiteは最新SHAでそれぞれ`3 passed`、`49 passed`、`58 passed`、`7 passed`でした。distribution cutover focused suiteは`10 passed`、Epic distributionは`11 passed`、bootstrapは`3 passed`でした。追加したT01 relation witnessは168 relationsを全件検証し、関連するengineケースと合わせて`169 passed`でした。Git helperのconsumer-side module shadow回帰は`7 passed`でした。
- `TMPDIR=/private/tmp uv run python -m scripts.quality.verify_full_regression --shards 4`は`1921 tests collected`、4 shard exit 1、status=`ledger-mismatch`でした。ledgerはtotal15／active14／resolved1、timing 243 entriesを維持し、violationは10件（runtime import 8、runtime shell 1、workbench 1）で、親レジスタに登録済みの#395 active baselineと一致しました。今回追加したprovider lifecycle testsを含む#392の新規node failure、candidate receiptのdirty状態、ledger／timing／required-fastの変更はありません。レートリミットを理由にbundleや検証範囲を縮小していません。
- `40745c8a`を対象にした直近のfresh Code Review Strict（browser-only、GPT-5.6 Sol、Extra High、完全bundle、約303k tokens）は、本文JSONで`review_status=fail`、P1×3、P2×1を返しました。P1はconsumer cwdから起動するmanaged Git helperのmodule shadow、bootstrap cleanup failure action setの欠落、T01 relation coverageの不足でした。Blue Teamのfresh ChatGPT Use Strict分析は3件をvalid/blocking・同一batch修正と判定し、`e6a20147`へ回帰テスト付き修正を反映しました。P2のunsafe repository root分類はreport-onlyで保持しています。`e6a20147`を含む更新後のclean pushed SHAに対する再Code Review Strict、Final Quality Gate Strict、PR merge後B1は未完了です。

以上により、#392のCP1–CP4実装candidate、P1 remediation、provider-first packaging、dogfood parity、回帰テスト、current gate観測の証拠は`e6a20147`へ更新済みです。ただしcurrent full verifierの#395 baseline mismatchと、Report更新後の最終Strict review／Final Quality Gateが残るため、Issue完了・Product GREEN・merge完了はまだ主張しません。最終Strict reviewとFinal Quality Gateは、このReportを含む次のclean pushed SHAに対して実施します。
