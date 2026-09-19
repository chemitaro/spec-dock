---

kind: "tdd-ready-requirement-candidate"
issue: "iss-00395"
title: "Regression Baseline Terminalization and Product Defect Repair — TDD実装準備版Requirement"
generated_at: "2026-09-15"
repository: "chemitaro/spec-dock"
branch: "iss-00395-regression-baseline-terminalization-and-product-defect-repair"
verified_tip_sha: "25b33cfaf6214d8c78494f0e0520ef8738bc862f"
verified_tip_tree: "ad6c2fdc2434e514a4b23eb29dbabf33c33b8db8"
p392_entry_sha: "921bf7512c72bfa2887673cb7ec9bc512cec6ff3"
p392_entry_tree: "190bc566a18cd84813c4b7c043f8724e275cb55d"
implementation_allowed: false
owner_decisions_required: []
human_merge_only: true
authority: "advisory-canonical-replacement-candidate"
---

# Regression Baseline Terminalization and Product Defect Repair — TDD実装準備版Requirement

## 1. 目的

Issue #395は、human-merged P392が保持するpost-#387 regression baselineの14 active rowsについて、各rowが表すaccepted behaviorをnormal passへ戻し、root ledgerを15 resolved / 0 activeへ終端化します。

価値は「ledgerをGREEN表示へ変えること」ではありません。既知の回帰が示すProductまたはtest observerの責務不整合を、原因に対応する最小修復で解消し、current regression systemが同一candidateを正常として観測できる状態へ戻すことです。

## 2. 現在位置と権限

* Repositoryは`chemitaro/spec-dock`です。
* Issue branchは`iss-00395-regression-baseline-terminalization-and-product-defect-repair`です。
* 本候補の分析sourceはverified tip `25b33cfaf6214d8c78494f0e0520ef8738bc862f`、tree `ad6c2fdc2434e514a4b23eb29dbabf33c33b8db8`です。
* Product/test/ledger baselineはhuman-merged P392 `921bf7512c72bfa2887673cb7ec9bc512cec6ff3`、tree `190bc566a18cd84813c4b7c043f8724e275cb55d`です。
* P392はB1、#392 acceptance、#392 closure、#395 implementation permission、#396 start permissionではありません。
* 本Requirement、Design、Plan、handoff、manifestの作成または採用だけでは実装許可になりません。
* `implementation_allowed=false`を維持します。
* merge、revert、Issue closure、#396 startはhuman/Codex側の別authorityです。

## 3. 利用者に見える最終成果

Human merge後の同一exact integration tipで、次を順に満たします。

### 3.1 B1 — Current gate GREEN

* current required PR gateが成功する
* ordinary laneが成功する
* current full verifierが成功する
* provider lifecycle、distribution、package、dogfood parityが成功する
* unexpected failureが0である
* #392 lifecycle/wire/protected-data contractが保持される

### 3.2 B2 — Baseline terminal state

* root ledgerは15 rowsのままである
* activeは0である
* resolvedは15である
* rows 1、3–15は14件すべて`fixed-in-place`である
* row 2は既存の`superseded`である
* approved failureは0である
* unexpected failureは0である
* B1とB2は同じSHA/treeを証拠にする

## 4. Entry acceptance

Product/test/ledger/dogfoodへ変更する前に、次を満たします。

1. Repository、Issue branch、specification SHA/tree、upstream、remote tipがexact一致する
2. Worktreeがcleanである
3. P392がspecification tipのancestorである
4. P392からspecification tipまでの差分に、許可されていないProduct、test、ledger、timing、policy、workflow変更がない
5. active Issueが`iss-00395`である
6. `.meta.json`のID、GitHub #395 linkage、`depends_on=[]`が保たれる
7. Ledgerはexact 15 rowsで、row 1とrows 3–15がactive、row 2がresolved/supersededである
8. Nodeid、signature、row order、row 2 successorが§6と一致する
9. Timingは243 entries、required-fastはexact 4 nodeである
10. Entry full verifierの差異がP392で認められたrows 4–12、15だけであり、#392-owned failureとunexpected failureが0である
11. Independent specification reviewがexact tipに対してpass、P0=0、P1=0である
12. Explicit implementation dispatchとscoped concurrent-writer absenceが存在する

一つでも不一致なら、Product/test/ledger/dogfoodを変更せず停止します。

## 5. Scope

### 5.1 Issue #395が所有する成果

* Rows 1、4–11、13–15のtest harness / observer修復
* Row 3のProduct responsibility boundary修復とcredential non-exposureの観測強化
* Row 12の既存thin-shell boundaryを変更せず保護すること
* Provider source変更のcomplete dogfood projection
* 14 active rowsのfinal ledger terminalization
* 修復結果をcurrent regression systemで証明すること

### 5.2 Read-only input

* Issue #392 lifecycle behavior、wire、schema、migration、uninstall、recovery、coordination
* Current ledger evaluator、verifier、timing、sharder、policy hook
* Provider CIとmain-push Full Regression workflow
* Parent Epic R/D/P、P392 ADR、failure disposition register、integration/rolling-wave contracts
* Row 12のcurrent Product boundary

### 5.3 Non-goals

* Provider lifecycle wireのfield、enum、code、phase、serialization、ordering変更
* `E384-QUAL-001`の実装または再定義
* Policy retirement、workflow redesign、required-context transition
* Timing、sharder、verifier scopeの変更
* Product feature追加、general refactor、unrelated cleanup
* New Issue作成
* Agent merge、automatic revert、Issue close、#396 start

## 6. Exact regression identity and accepted behavior

Row 2はread-onlyです。Rows 1、3–15が本Issueでnormal passへ移す14 active rowsです。Nodeidとhistorical signatureは変更しません。

| Row | Exact nodeid                                                                                                                                     | Historical signature SHA-256                                       | Accepted behavior                                                                        | Required disposition                                |
| --: | ------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------ | ---------------------------------------------------------------------------------------- | --------------------------------------------------- |
|   1 | `tests/cli_runtime/test_delete.py::TestCliDelete::test_delete_scrubbed_meta_is_not_reobserved_by_validate_sync_active`                           | `0d6c418e8c531ed77662b5bb0f166c6370f1b4d995a1ec6ac23452382c34869f` | 削除済みmetadataはvalidate、sync、active observation後も再観測されない                                   | Test observer修復後にnormal pass、fixed-in-place         |
|   2 | `tests/cli_runtime/test_distribution_cutover.py::test_s40b_retained_skill_identity_matches_issue359_final_source`                                | `8742959a307d18594743f6bec12a056268baab34024279dbeb4e57458b3a7637` | Fixed skill slotsがprovider assetsとdogfoodに一致する                                           | 既存resolved/supersededとsuccessorをread-only保持         |
|   3 | `tests/cli_runtime/test_import.py::TestCliImport::test_import_accepts_canonical_url_when_origin_is_credentialed_https_remote`                    | `f149be56ae07e7b774137b1f8f5912076a82838250be9750c886aca7a8392a5f` | Credential-bearing HTTPS originからcanonical same-repository URLをimportでき、credentialを露出しない | Product boundary修復後にnormal pass、fixed-in-place      |
|   4 | `tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_parent_fallback_regression`                                            | `3f7d32388f2d60f77ec1740aac53fd6d6481f7cb04ef3f3ae7ef09463a29a980` | Existing parent fallbackを解決する                                                            | Test double修復後にnormal pass、fixed-in-place           |
|   5 | `tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_load_active_manifest_chain_regression`                                 | `55f2d59d2e1ce7b337462feefbde5c5a84423d07f039ff5fb5dd7bc8b10762ce` | Current active manifest chainを二段階観測で読む                                                   | Test double修復後にnormal pass、fixed-in-place           |
|   6 | `tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_parent_fallback_re_resolves_inside_lock_when_parent_drifts_regression` | `ab1f703094ed3335d43ff943cb9194266ee2c162758b3c732b47c1c1cee9256a` | Parent drift時にlock内で再解決し、second parentを用いる                                               | Test double修復後にnormal pass、fixed-in-place           |
|   7 | `tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_import_numeric_target_uses_resolved_current_repo_slug_for_github_read` | `ea4df2e82010c5a2058e5bfd5b31bb7ada7f4776f8cff44a2457fb50b8a1df70` | Numeric importがcurrent repository slugをGitHub readへ渡す                                    | Test double修復後にnormal pass、fixed-in-place           |
|   8 | `tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_import_issue_uses_target_repo_slug_for_same_repo_url_when_present`     | `22d80f8db459620d13f14e34c9a7fc2ee60b73f4080ac7d181b3a7c69ab1d4f3` | Same-repo URLのexplicit target slugをGitHub readへ用いる                                       | Test double修復後にnormal pass、fixed-in-place           |
|   9 | `tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_import_then_sync_artifact_path_name_content_regression`                | `0dbf9314fa763929461775d43ae3e56c51bddcb742e2e329317736f5b1194ef7` | Import後syncがartifact path、name、contentを保持する                                              | Test double修復後にnormal pass、fixed-in-place           |
|  10 | `tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_post_import_sync_negative_path_regression`                             | `541c15d4ba9564d9256cb2651fe180c2e230760c2fa56ecb389f145fb8723d00` | Post-import sync失敗がobservableで、committed importを破損しない                                    | Test double修復後にnormal pass、fixed-in-place           |
|  11 | `tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_execute_create_plan_reuse_seam`                                        | `44894dc46328aad1a9352cb69a93975a99701b9a9e14f8d5c9dc25470dcf6efd` | Current create-plan reuse seamがsecond writerなしで結果を作る                                     | Test double修復後にnormal pass、fixed-in-place           |
|  12 | `tests/cli_runtime/test_runtime_shell_s11.py::TestRuntimeShellS11::test_final_api_call_site_and_structural_regression`                           | `0c1088f1a15dd18d672fe5707d9add3ffe1593b6ead070d90ba553019c498790` | `commands/new.py -> application.contracts -> domain.artifacts`を保つ                        | Product/test edit 0、node normal pass、fixed-in-place |
|  13 | `tests/cli_runtime/test_sync.py::TestCliSync::test_new_and_active_and_sync`                                                                      | `f9b206f85a7c0ee352b4019eaed232ee02dcf896c150659fa7e8191f125951a6` | New、selection-only active、syncがgenerated stateへ収束する                                      | Test observer修復後にnormal pass、fixed-in-place         |
|  14 | `tests/cli_runtime/test_sync.py::TestCliSync::test_sync_emits_tree_puml_ready_board_at_spec_dock_root`                                           | `3d1b673b92516964bd29b91cf29c8e03c553988dc9e0df7f0a9aee16dc545619` | Syncがroot tree、PUML、ready-boardを生成する                                                     | Test observer修復後にnormal pass、fixed-in-place         |
|  15 | `tests/cli_runtime/test_workbench.py::TestCliWorkbench::test_copied_workbench_readme_and_payloads_remain_opaque_to_runtime_commands`             | `20d53420c38ab501c64346e6e22a0b309b2358191fe74a54ed9c20717ddb09b9` | Copied Workbench bytesがruntime commandsに対してopaqueである                                     | Test observer修復後にnormal pass、fixed-in-place         |

Row 2 successorは`tests/cli_runtime/test_distribution_cutover.py::test_s40b_retained_skill_identity_matches_current_provider_and_dogfood`です。Row 2 object、successor、row orderを変更しません。

## 7. Behavioral requirements

### I395-RQ-001 — Exact baseline admission

§4と§6を満たすexact baselineからだけ実装を開始します。GitHub Issue state、SpecDock readiness表示、過去のtest結果をexact baseline evidenceの代用にしません。

### I395-RQ-002 — Cause-appropriate repair

* Rows 1、4–11、13–15はtest harness / observerをcurrent Product contractへ追随させます。
* Row 3はProduct側のidentity/publication responsibility boundaryを修復します。
* Row 12はcurrent compliant Product boundaryを変更しません。
* Productを廃止済みCLI/APIへ戻しません。
* Accepted assertionを削除・弱化しません。

### I395-RQ-003 — Read-only identity and publication separation

* Read-only repository identityはfetch originからowner/repo identityを解決できます。
* Credential-bearing HTTPS fetch URLでもread-only identityを解決できます。
* Publicationはfetchまたはpushのuserinfoを拒否します。
* Publicationはfetch/push repository identityの不一致を拒否します。
* Same-repository validation、numeric target scope、foreign URL rejectionを弱めません。
* Raw credential、username、password、token、credential-bearing URLをstdout、stderr、exception、distributed evidenceへ出しません。
* Existing public/internal signaturesを変更しません。

### I395-RQ-004 — Descriptor-bound harness fidelity

Rows 4–11のtest doubleはcurrent descriptor-bound scaffolder port `copy_scaffolded_tree_at`へ適合し、production descriptor-bound writerのcollision、binary/text、mode、shebang behaviorを再利用します。本番をobsolete pathname writerへ戻しません。

### I395-RQ-005 — Selection-only observer fidelity

Rows 1、13、14、15はcurrent `active set` surfaceだけを使用します。Obsolete `--force`と`--no-checkout`を使いません。Active operationの成功を後続state readより先に確認し、元のdelete、sync、tree、PUML、ready-board、Workbench opacity assertionを保持します。

### I395-RQ-006 — Thin-shell application boundary

Row 12は次を保持します。

* Commands layerはcatalogueをapplication contractから得る
* Application contractがdomain catalogueをre-exportする
* Domain catalogueがvalueのsingle sourceである
* Commands layerからdomain/infraへのdirect dependencyを追加しない
* Existing structural assertionsをすべて保持する

Current boundaryがdriftしている場合は、推測修正せず停止します。

### I395-RQ-007 — Complete dogfood projection

Row 3のprovider sourceがGREENになった後、current lifecycle commandで一つのcandidateをchecked-in dogfoodへcomplete projectionします。

* Generated runtime mirrorはprovider sourceとbyte-equalである
* Ready recordと二つのslot markerは同じnew candidate digestを持つ
* New digestは旧digestと異なる
* Versionは`0.2.4`である
* Record stateは`ready`、operationは`null`である
* Seed policyは`preserve-only`である
* Fixed slot namesと二つの`SKILL.md` bytesを保持する
* Initiatives、Artifacts、Workbench、consumer-owned dataを保持する
* Generated filesを手編集しない

### I395-RQ-008 — Ledger as the last semantic transition

14 historical nodesとrow 2 successorがnormal passし、dogfood/protected-data proofがGREENになった後だけledgerを変更します。

Rows 1、3–15の許容差分は次の二点だけです。

* `lifecycle`: `active`から`resolved`
* `resolution_mode`: absentから`fixed-in-place`

Nodeid、signatures、historical status、disposition、row order、top-level historical fieldsを変更しません。Row 2 objectはbyte-semanticに同一でなければなりません。

### I395-RQ-009 — No masking

Skip、xfail、approved failure、marker変更、policy skip reason変更、signature書換え、row削除、node rename、silent retirement、別successorへの置換、verifier scope縮小、`continue-on-error`、mock-only successを禁止します。

### I395-RQ-010 — Transitional system continuity

Timing 243、required-fast 4、current ledger evaluator、four-shard verifier、policy hook、Provider CI、main-push Full Regressionを変更しません。Issue #396のfuture toolingを先取りしません。

### I395-RQ-011 — Same-tip B1/B2

Human merge後、exact integration SHA/treeを固定し、同じidentityでB1を先に、B2を続けて確認します。別commit、別tree、future rerunで証拠を差し替えません。

### I395-RQ-012 — Permission separation

Formal Issue start、implementation-ready specification、independent review、implementation dispatch、Product GREEN、commit/push、PR preparation、human merge、B1/B2、Issue closureを別々の状態として扱います。

### I395-RQ-013 — Evidence and traceability

各repair rowについて、entry observation、first RED、変更path/symbol、保護assertion、GREEN、ledger stateを追跡できます。Working-tree evidenceはdiff identity付きprovisionalとし、merge-ready evidenceはclean pushed exact SHA/treeへ再束縛します。

### I395-RQ-014 — Stop, recovery, rollback

Identity drift、baseline drift、expected REDとの差異、security weakening、row 12 drift、dogfood/protected-data drift、ledger invariant違反、policy/workflow/lifecycle越境、unexpected failure、新owner decisionが発生した場合は停止します。

Human merge前はIssue candidate全体を修正または破棄します。Human merge後かつ#396開始前は、humanがwhole-merge revertまたはIssue #395 owned boundary内のforward-fixを選びます。Ledger-only、Product-only、test-only、generated-mirror-only、automatic rollbackを禁止します。

## 8. Acceptance evidence

Merge-ready candidateは、一つのclean pushed implementation SHA/treeに対して次を満たします。

* 13 repair rowsのexpected first RED
* Row 12 evaluator REDとnode normal pass
* 14 historical nodesのnormal pass
* Row 2 successorのnormal pass
* Row 3 security matrixの全case成功
* Row 12 boundary unchanged
* Complete dogfood projectionとprotected-data equality
* Ledger 15/0/15、fixed-in-place 14、superseded 1
* Historical ledger fields preserved
* Current full verifier verified、violations 0
* Ordinary、lifecycle、distribution、platform、package、dogfood、lint、SpecDock validate成功
* Timing、required-fast、policy、workflow、wire no-touch
* Exact implementation surface以外のdiff 0
* Independent code review pass、P0=0、P1=0
* Final Quality Gate pass、coverage complete、unreviewed/unresolved 0

## 9. Decision state

Issue固有の新しいProduct、security、lifecycle、policy decisionはありません。`owner_decisions_required=[]`を維持します。

本候補はcanonical replacement candidateであり、repositoryへ未適用です。Implementation permissionは引き続きfalseです。
