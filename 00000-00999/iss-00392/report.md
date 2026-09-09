---
種別: レポート（Issue）
ID: "iss-00392"
タイトル: "Provider Lifecycle And Regression Gate Hard Cutover"
関連GitHub: ["#392"]
状態: "approved"
最終更新: "2026-09-09"
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
  role: "issue-elaboration-source-provenance"
  repository: "chemitaro/spec-dock"
  branch: "iss-00392-provider-lifecycle-and-regression-gate-hard-cutover"
  sha: "dc638e936e763cc7a6087f258201ed9ed654e7fb"
  tree: "17ce38234033393c385c4b17e40c0ccdc78bfc19"
implementation_evidence:
  candidate_sha: "d94b218a1344fbba65239a13dfaae4f19bb5d579"
  candidate_tree: "e5f3636e064605f3566b07420ea3a1d9da71dfac"
---

# #392 仕様・実装レポート

## 1. Outcome

Issue #392の実装可能な仕様候補として、Requirement、Design、critical-level Plan、Luna Max checkpoint handoff、test ownership/migration Artifact、日本語HTMLガイドを一つのpackへ整列しました。

初回仕様作成時に行ったのは調査、仕様作成、静的自己検証です。その後、仕様を実装candidateへ反映し、focused test、package/dogfood parity、default fast、current full verifierを実行しました。実装時点の詳細な証拠は§9に記録します。

## 2. Source verification facts

- GitHub connectorでrepository `chemitaro/spec-dock`、branch `iss-00392-provider-lifecycle-and-regression-gate-hard-cutover`を取得しました。
- Branch tipのfull object IDは`dc638e936e763cc7a6087f258201ed9ed654e7fb`で、strict wrapperのexpected SHAと完全一致しました。
- Verified commit treeは`17ce38234033393c385c4b17e40c0ccdc78bfc19`です。
- 最初にroot `AGENTS.md`を読み、`src/spec_dock/`をProduct source、checked-in `spec-dock/`をdogfood projection、PR mergeをhuman-onlyとして扱いました。
- `attachments-bundle.zip`を一時directoryへ展開し、relative pathを維持した68 filesを列挙・検索しました。内訳の19 `.pyc` filesは入力ノイズとして無視し、成果物へ含めていません。
- 添付内のEpic/Issue canonical documentsとselected source filesは、verified commitのGitHub blob/pathへ照合しました。相違時はGitHubを優先する規則で処理しました。
- GitHub上の`spec-dock/spec-dock.version`はexact bytes `0.2.3\n`でした。

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

`実装開始許可=true`です。CP1–CP4の実装candidateを固定し、次の最終ゲートが残っています。

1. 実装candidate `d94b218a1344fbba65239a13dfaae4f19bb5d579`のclean pushとupstream SHA一致（成立）。
2. このcandidateと更新後Reportを含む最終SHAに対する独立Code Review StrictのP0/P1ゼロ・pass。
3. 最終Quality Gate Strictの実施条件成立。
4. 人間による#392 PRのEpic integration branchへのmergeと、merged tip B1再検証。

CP4後もagentはmergeしません。人間が#392 PRを`codex/epic-00384-provider-test-strategy-planning`へmergeし、merged tipでB1を再検証します。B1 GREEN後だけ#395を開始します。

## 8. Residual blocker and uncertainty

親public valueまたはIssue責務の追加は不要です。`RECORD-TEMP`のparent clarificationはpublic inventoryを変えません。実装candidateのfocused/package/default-fast検証は完了していますが、Report更新後のclean pushed Strict review、Final Quality Gate Strict、current full verifierの#395 baseline解消、人間PR merge、merged-tip B1は未完了です。

current full verifierの`ledger-mismatch` 10件は#395が所有するactive baselineのsignature/coverage mismatchであり、#392の責務へ取り込まず、skip/xfailやledger変更で隠していません。残るgateはReport更新後のclean pushed Strict review、Final Quality Gate Strict、人間PR review/merge、merged-tip B1です。これらが未完了のため、本ReportはIssueの最終certification、Product GREEN、merge完了を主張しません。

## 9. Implementation verification update

2026-09-09時点の実装candidate `d94b218a1344fbba65239a13dfaae4f19bb5d579`（tree
`e5f3636e064605f3566b07420ea3a1d9da71dfac`）に対して、次の証拠を採取しました。

- Blue-teamのChatGPT UseをGPT-5.6 Sol／Extra High／fresh browser sessionで再試行しました。レートリミットをbundle縮小で回避せず、前回と同じ11ファイルの完全bundleを投入し、Issue仕様3ファイル、provider runtime 4ファイル、lifecycle test 3ファイルを対象に、Code Review StrictのP1を分析しました。結論は「Aのsource lease継承」と「B EX後のrecord再検証」の2件とも有効なmerge-blocking P1で、#395の責務外というものでした。
- Aの修正として`source_fd`をPorts→bootstrap→Git CLI→managed helperへ伝播し、`read-tree`子プロセスがsource Aとtarget Bのleaseを保持するようにしました。`worktree_create`はmaterialize・verification完了後の`finally`までsource fdを保持し、成功・例外の両経路で閉じます。Bの修正として、exclusive open後にinventory／record／blocker／containment／path bindingを再取得・再検証し、recordの消失・別パス・same-pathのinode交換時はGit removeを呼ばずfail closedにしました。
- provider runtimeとchecked-in dogfood runtimeを同期し、candidate digest `92f3d5716338bd458c5cb0840a5c3672ce5c6d5343179d628cf8a1c613ea7144`、二つのslot marker、dogfood `spec-dock.version`を一致させました。`seed_policy=create-if-absent`の既存fixture semanticsは保持しています。
- 追加した回帰は、直接infraでsource leaseをhelperへ渡すこと、record再検証後の別パス拒否、same-path異inode拒否、親SIGKILL中のread-tree子プロセスによるA/B lease保持です。Worktree／lifecycle focused suiteは`46 passed`、CP4のdistribution・dogfood・Issue #392 acceptance全件は`82 passed`でした。obsolete behaviorのassertionは残していません。
- `make lint`はruff check、ruff format、mypyすべてpass、`uv build`もpassしました。default fastは`878 passed, 834 skipped`です。
- `TMPDIR=/private/tmp uv run python -m scripts.quality.verify_full_regression --shards 4`は`1712 tests collected`、status=`ledger-mismatch`でした。ledgerはtotal15／active14／resolved1、timing 243 entriesを維持し、evaluationのviolationは10件（runtime import 8、runtime shell 1、workbench 1）で、いずれも#395 active baselineです。#392の新規node failure、ledger／timing／required-fastの変更はありません。
- 直前の独立Code Review Strictは、exact SHA `9f8a1e14a92d90c7e4a65b9e58be1cac61c2668b`でP1×2を検出しました。上記修正はその指摘に対応したものであり、Report更新後の最終SHAについてfresh Code Review Strictを未実施です。Final Quality Gate Strict、#395のbaseline修正、PR merge後B1も未完了です。

以上により、#392の実装candidate、provider-first packaging、dogfood parity、回帰テスト、current gate観測の証拠は揃っています。最終Strict reviewとFinal Quality Gateがpassするまで、Issue完了・Product GREEN・merge完了は主張しません。
