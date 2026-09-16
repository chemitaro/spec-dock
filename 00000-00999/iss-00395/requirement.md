---
種別: 要件定義書（Issue）
ID: "iss-00395"
タイトル: "Regression Baseline Terminalization and Product Defect Repair"
関連GitHub: ["#395"]
状態: "draft"
最終更新: "2026-09-16"
依存:
  - "../../artifacts/20260913t144152z-adr-issue-392-provisional-merge-and-deferred-b1.md"
  - "../../requirement.md"
  - "../../design.md"
  - "../../plan.md"
  - "../../artifacts/active-failure-disposition-register.md"
  - "../../artifacts/provider-lifecycle-wire-contract.md"
  - "../../artifacts/epic-integration-branch-contract.md"
  - "../../artifacts/rolling-wave-issue-elaboration-contract.md"
親: ["epic-00384", "init-local-00003"]
実装開始許可: true
owner_decisions_required: []
repository_evidence:
  role: "elaboration-input-provenance"
  repository: "chemitaro/spec-dock"
  branch: "iss-00395-regression-baseline-terminalization-and-product-defect-repair"
  sha: "fe9ac410a23ca4ccce2de440ef0ddb6c76c48af9"
  tree: "4ee7cf0911ed6e4e51f8d50a09e2b34c71eae599"
p392_entry_evidence:
  sha: "921bf7512c72bfa2887673cb7ec9bc512cec6ff3"
  tree: "190bc566a18cd84813c4b7c043f8724e275cb55d"
support_history_evidence:
  sha: "c0736434503117d5d468d1438fb18da16d382a56"
  tree: "cec02ce70fbcbbbac811a04106dcc15540ad4d09"
---

# iss-00395 Regression Baseline Terminalization and Product Defect Repair — 要件定義

## 1. 結論と現在位置

Issue #395は、human-merged P392が残したpost-#387回帰baselineの14 active rowsを、親registerで確定済みの原因分類に従ってnormal passへterminalizeする。修復面はtest harness / observer 12件とProduct境界2件である。ただし、P392 exact treeではProduct row 12のthin-shell境界は既にapplication contract経由へ回復済みであり、現行Full Regressionは同rowを`coverage_mismatch`として観測している。したがってrow 12は、現行Product構造を保持し、normal pass観測とledgerの`fixed-in-place`解決で閉じる。現行構造を再編集すること自体を成果条件にしない。

本Issueのformal `issue start`は、指定Issue branchと添付generated contextで`iss-00395`がactiveである状態として扱う。formal startはbranch/active scopeの選択であり、Product実装許可ではない。本書、Design、Plan、LunaMax handoff、human guide、manifestをlocal canonical treeへ反映し、SpecDock validation、clean push、exact-tipの独立`chatgpt-spec-review-strict`で`review_status=pass`かつP0/P1=0を得たうえで、ユーザーが本メッセージで仕様の実装を明示的に許可したため、現在の`実装開始許可: true`を記録する。この許可は、実装前のexact identity／同時書き込みなしの確認、Product/test GREEN、code review、human merge、B1/B2、#392/#395 closureを完了扱いにしない。

## 2. Identity contract

### 2.1 P392と現行tipを混同しない

| Role | SHA | Tree | 意味 |
|---|---|---|---|
| P392 entry/product baseline | `921bf7512c72bfa2887673cb7ec9bc512cec6ff3` | `190bc566a18cd84813c4b7c043f8724e275cb55d` | PR #399のhuman merge tip。#395が受け取るProduct/test/ledger baseline。B1ではない。 |
| Current elaboration input | `fe9ac410a23ca4ccce2de440ef0ddb6c76c48af9` | `4ee7cf0911ed6e4e51f8d50a09e2b34c71eae599` | 指定Issue branchの検証済みtip。P392後のreceipt文書を含む仕様作成source。 |

`921bf7512c72bfa2887673cb7ec9bc512cec6ff3`から`fe9ac410a23ca4ccce2de440ef0ddb6c76c48af9`までの差分は、次の二つの文書だけである。

1. `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/plan.md`
2. `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/issues/iss-00392-provider-lifecycle-and-regression-gate-hard-cutover/report.md`

従って、`fe9ac410a23ca4ccce2de440ef0ddb6c76c48af9`のProduct source、tests、root ledger、timing、verifier、policy、workflowはP392と同一である。後続の本仕様pack commitは新しいspec freeze候補を作るが、P392のProduct entry identityを置換しない。実装開始時は、P392からspec freeze tipまでの差分が本Issueのcanonical docsとArtifactsに限定されることを再確認する。

### 2.2 P392 witness

P392 receiptは次を固定する。

- `uv run pytest`: `1367 passed, 847 skipped`
- `make lint`: Ruff check、Ruff format、mypyがpass
- `uv run pytest tests/unit/provider_lifecycle`: `513 passed`
- `./spec-dock/scripts/spec-dock validate`: `nodes=236`
- root ledger: 15 total / 14 active / 1 resolved
- timing: 243 entries
- required-fast: exact 4 node
- current full verifier: `2214 tests collected`、`status=ledger-mismatch`、10 violations
- 10 violationsはrows 4–12、15だけであり、rows 4–11と15は`signature_mismatch`、row 12は`coverage_mismatch`
- rows 1、3、13、14は`active_verified`、row 2は`resolved_verified`
- #392-owned unexpected failureは0
- Code Review StrictとFinal Quality Gate StrictはP392 merged treeに対してpass

このwitnessは#395 entryを許す限定証拠であり、full verifier GREEN、B1、#392 closure、#395実装許可を意味しない。

### 2.3 Canonical specification packとpreserved support history

本Issueのcurrent canonical specification packは、次のexact 6 pathsである。

1. `requirement.md`
2. `design.md`
3. `plan.md`
4. `artifacts/iss-00395-luna-max-implementation-handoff.md`
5. `artifacts/iss-00395-human-guide.html`
6. `artifacts/iss-00395-chatgpt-spec-pack-manifest.md`

Elaboration input後に既に作成されていた次のexact 16 artifactsは、
`c0736434503117d5d468d1438fb18da16d382a56` / `cec02ce70fbcbbbac811a04106dcc15540ad4d09`を
support-history checkpointとして、grandfathered support historyに分類する。

| Support history path |
|---|
| `artifacts/design-luna-max-ready.md` |
| `artifacts/iss-00395-design-tdd-ready.md` |
| `artifacts/iss-00395-lunamax-handoff-tdd-ready.md` |
| `artifacts/iss-00395-plan-review-analysis.md` |
| `artifacts/iss-00395-plan-tdd-ready.md` |
| `artifacts/iss-00395-requirement-tdd-ready.md` |
| `artifacts/iss-00395-spec-pack.zip` |
| `artifacts/iss-00395-tdd-ready-manifest.md` |
| `artifacts/iss-00395-tdd-ready-pack.receipt.md` |
| `artifacts/iss-00395-tdd-ready-pack.zip` |
| `artifacts/luna-max-implementation-handoff-ready.md` |
| `artifacts/luna-max-readiness-analysis.md` |
| `artifacts/luna-max-readiness-manifest.md` |
| `artifacts/luna-max-readiness-pack.receipt.md` |
| `artifacts/luna-max-readiness-pack.zip` |
| `artifacts/plan-lunamax-ready.md` |

Support historyは、現在のcanonical R/D/P、実装入力、owned write surface、
implementation permission、owner decisionを上書きしない。内容に古いSHA、tree、
permission値またはidentityが残っていても、履歴snapshotとして扱う。編集、削除、
rename、copy substitution、再生成、再圧縮、内容の最新化、新規support artifact追加を
行わない。current canonical packと内容が矛盾する場合は、current canonical R/D/Pを
authorityとし、support historyを修正して整合させない。

このadmission/history分類の追加は、Product、Row 3のsecurity/no-secret、lifecycle、
policy、protected-data、workflowの意味を変更しない。Row 3のcredential-bearing origin
処理、same-repository validation、publication strictness、secret non-exposureは、従来どおり
実装とsecurity matrixで検証する。

## 3. Observable outcome

Issue #395のhuman merge後、同一exact integration tipで次を順に成立させる。

1. **B1:** current required PR gate、ordinary test lane、provider parity、current full verifierがGREENで、unexpected failureが0である。
2. **B2:** root ledgerの15 rowsが15 resolved、0 activeであり、14 rowsは`fixed-in-place`、row 2は既存の`superseded`、approved failure 0、unexpected failure 0である。

B1とB2は同じfull SHAを証拠にする。#392 lifecycle output、current ledger/timing/sharder/policy hook、Provider CI、main-push Full Regressionを保持したまま成立させる。Issue #396のtooling、`E384-QUAL-001`実装、policy retirementを先取りしない。

## 4. Entry gate

Product/test/ledger変更へ進む前に、すべての条件を満たす。

1. Repositoryは`chemitaro/spec-dock`、branchは`iss-00395-regression-baseline-terminalization-and-product-defect-repair`である。
2. Reviewed spec freeze SHA、local `HEAD`、configured upstream、remote branch tipがbyte-for-byte一致し、worktreeがcleanである。
3. `921bf7512c72bfa2887673cb7ec9bc512cec6ff3`がspec freeze tipのancestorである。
4. Specification admission historyは、次の三つのsegmentを独立に検証する。22 pathsを単一のcurrent-spec allowlistとして扱わない。
   - **P392からelaboration inputまで:** Epic PlanとIssue #392 Reportのexact 2 pathsだけが変化し、Product source、tests、ledger、timing、policy、workflowは変化しない。
   - **Elaboration inputからsupport-history checkpointまで:** current canonical specification packの6 pathsと、§2.3のgrandfathered support history 16 pathsのexact 22 pathsだけが存在し、それ以外の差分がない。
   - **Support-history checkpointからreviewed spec freezeまで:** current canonical specification packのexact 6 pathsだけが変更され、support history 16 pathsのpath、mode、object type、Git object IDがcheckpointと完全一致する。
   P392 receiptを保持する親文書は、上記のP392からelaboration inputまでのdoc-only契約に含めて確認する。
5. `./spec-dock/scripts/spec-dock active show`がIssue `iss-00395`を示す。generated active stateをtracked `.meta.json`やGitHub Issue bodyから推測しない。
6. `.meta.json`のID/GitHub linkageは`iss-00395` / `#395`、`depends_on=[]`である。`.meta.json`は手編集しない。
7. root ledgerはtable orderを含むexact 15 rowsで、row 1とrows 3–15がactive、row 2がresolved/supersededである。全nodeid/signatureが§6と一致する。
8. timingの`node_seconds`は243 entriesである。
9. fresh current full verifierの全violationはrows 4–12、15だけに限定され、#392-owned/unexpected failureは0である。rows 1、3、13、14はactive failure signatureが一致し、row 2のsuccessorはnormal passする。
10. `owner_decisions_required=[]`であり、同時に別Issue writerがいない。
11. implementation-ready packの独立Strict reviewがpassし、実装dispatchにexact spec freeze SHAと許可証跡が含まれる。

一つでも不一致ならProduct/test/ledgerを変更せず、expected/actual SHA、row、signature、count、path、symbol、verifier violationを返して停止する。

## 5. Scope and ownership

### 5.1 Owned write surfaces

| Category | Path / surface | Write rule |
|---|---|---|
| Product row 3 | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/git_cli.py` | Existing symbolsだけを用いてread-only repository identityとpublication endpoint policyを分離する。 |
| Generated dogfood candidate | `spec-dock/scripts/spec_dock_runtime/infra/git_cli.py`、`spec-dock/spec-dock.version`、`.agents/skills/spec-dock/.spec-dock-provider-slot.json`、`.agents/skills/spec-dock-grill-with-docs/.spec-dock-provider-slot.json` | Provider source GREEN後にSpecDock updateで一つのcandidateとして投影する。四fileとも手編集しない。Runtime mirror bytesを更新し、recordと二slot markerの`candidate_digest`を同じ新digestへ束縛する。 |
| Product row 12 | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/new.py`、`application/contracts.py`、`domain/artifacts.py` | 現行構造は既にaccepted correctionを満たすため、preflight一致時は変更しない。drift時だけstop-and-returnし、推測修正しない。 |
| Test rows 1、3–11、13–15 | `tests/cli_runtime/test_delete.py`、`test_import.py`、`test_runtime_import_s10.py`、`test_sync.py`、`test_workbench.py` | Node identityを保持し、observer/test doubleだけを現行contractへ追随させる。 |
| Structural observer row 12 | `tests/cli_runtime/test_runtime_shell_s11.py` | Existing assertionsとnode identityを保持する。assertion削除・弱化は禁止。 |
| Transitional state | `full-regression-ledger.json` | 14 active rowsを`resolved` / `fixed-in-place`へ移す。historical fieldsとrow 2を保持する。 |
| Canonical Issue docs | 本IssueのR/D/P | Stable parent contractを意味変更せず具体化する。 |
| Primary Issue Artifacts | 本Issueのhandoff、human guide、manifest | Current advisory artifacts。permission、identity、admission semanticsをcanonical R/D/Pと整合させる。canonical R/D/Pを置換しない。 |

Support history 16件はcurrent Issue Artifactsではなく、§2.3で定義したpreserved support historyである。これらはread-only evidenceとして扱い、今回のowned write surfaceに含めない。

### 5.2 Shared/read-only surfaces

- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/import_node.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/repo_context.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/ports.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/bootstrap.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/template_scaffolder.py`
- `scripts/quality/full_regression_baseline.py`
- `scripts/quality/verify_full_regression.py`
- `tests/unit/test_full_regression_baseline.py`
- `tests/conftest.py`
- `full-regression-timing-weights.json`
- `.github/workflows/provider-ci.yml`
- `.github/workflows/provider-full-regression.yml`
- #392 lifecycle source、wire record、migration、uninstall、recovery、bootstrap、coordination、package version

`§2.3`で列挙したexact 16 support-history artifactsもshared/read-only surfaceである。固定checkpointとのtree-entry equalityを保持し、edit、delete、rename、regenerate、recompress、reclassifyを行わない。これらをcurrent authorityまたはimplementation inputとして使用しない。

これらは本Issueのaccepted behaviorを観測するために読む。修復に意味変更が必要なら親へ戻す。

### 5.3 No-touch surfaces

- Parent Epic R/D/P、accepted ADR、Epic Integration Branch Contract、Rolling-Wave Contract、Provider Lifecycle Wire Contract、Post-#387 Registerのnormative content
- `E384-QUAL-001`のvalue、population、window、aggregation、rejection、platform scope
- lifecycle state/schema/wire、root/slot/seed ownership、0.2.4 migration/uninstall semantics
- timing 243 entries、sharder、policy skip machinery、policy hook、current workflowsの削除・再設計
- required contexts、branch protection、merge、revert、Issue closeを行うhuman authority
- Issue #396のE384-QUAL-001実装、lifecycle wire変更、policy retirement、main merge
- managed `.meta.json`、active pointer、dependency storage、generated index/tree/diagramの手編集

## 6. Exact 14-row acceptance contract

全14 rowsはnodeidとhistorical signatureを保持し、`resolved-fixed-in-place-normal-pass`へ移す。表の「修復」は最初の誤り層を示し、accepted assertionsを省略する許可ではない。

| Row | Exact nodeid | Historical signature SHA-256 | Accepted behavior | 確定原因 | 修復面とacceptance |
|---:|---|---|---|---|---|
| 1 | `tests/cli_runtime/test_delete.py::TestCliDelete::test_delete_scrubbed_meta_is_not_reobserved_by_validate_sync_active` | `0d6c418e8c531ed77662b5bb0f166c6370f1b4d995a1ec6ac23452382c34869f` | 削除済みnode metadataはvalidate、sync、active-state observation後も再観測されない。 | 廃止済み`active set --force`を使用。 | Test observer。`active set --id iss-00058`でselection-only操作を成功させ、delete後の非再観測assertionsを保持する。 |
| 3 | `tests/cli_runtime/test_import.py::TestCliImport::test_import_accepts_canonical_url_when_origin_is_credentialed_https_remote` | `f149be56ae07e7b774137b1f8f5912076a82838250be9750c886aca7a8392a5f` | Credential-bearing HTTPS originからcanonical same-repository URLをimportでき、credentialを露出しない。 | Read-only identity解析がpublication endpoint policyへ結合。 | Product。fetch originからread-only slugを解決し、target URLとのsame-repo照合を維持する。stdout/stderrへ`token`またはcredential-bearing URLを出さない。publication endpointはuserinfo拒否とfetch/push整合を維持する。 |
| 4 | `tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_parent_fallback_regression` | `3f7d32388f2d60f77ec1740aac53fd6d6481f7cb04ef3f3ae7ef09463a29a980` | Import parent fallbackがaccepted existing parentを解決する。 | `_StubTemplateScaffolder`が`copy_scaffolded_tree_at`を未実装。 | Test double。descriptor-bound portへ追随し、parent、GitHub read、active manifest assertionsを保持する。 |
| 5 | `tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_load_active_manifest_chain_regression` | `55f2d59d2e1ce7b337462feefbde5c5a84423d07f039ff5fb5dd7bc8b10762ce` | Retired workflow authorityなしにcurrent active manifest chainを読む。 | 同上。 | Test double。cheap precheckとlock-side再解決の2 read、active IDs、artifact failure handlingを保持する。 |
| 6 | `tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_parent_fallback_re_resolves_inside_lock_when_parent_drifts_regression` | `ab1f703094ed3335d43ff943cb9194266ee2c162758b3c732b47c1c1cee9256a` | 観測parentが変化した場合、existing lock内でfallbackを再解決する。 | 同上。 | Test double。2回のparent resolution、second parentへの作成、GitHub read assertionsを保持する。 |
| 7 | `tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_import_numeric_target_uses_resolved_current_repo_slug_for_github_read` | `ea4df2e82010c5a2058e5bfd5b31bb7ada7f4776f8cff44a2457fb50b8a1df70` | Numeric importがresolved current repository slugをGitHub readへ渡す。 | 同上。 | Test double。`origin_github_repo_slug` callとissue gateway `repo_slug`、stored repo identityを保持する。 |
| 8 | `tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_import_issue_uses_target_repo_slug_for_same_repo_url_when_present` | `22d80f8db459620d13f14e34c9a7fc2ee60b73f4080ac7d181b3a7c69ab1d4f3` | Same-repository canonical URLが明示するtarget repository slugをGitHub readへ用いる。 | 同上。 | Test double。explicit target slug、same-repo validation、stored linkageを保持する。 |
| 9 | `tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_import_then_sync_artifact_path_name_content_regression` | `0dbf9314fa763929461775d43ae3e56c51bddcb742e2e329317736f5b1194ef7` | Import後のsyncがaccepted artifact path、name、contentを保持する。 | 同上。 | Test double。index/tree/PUML/deps/dashboard pathsとimported node projection assertionsを保持する。 |
| 10 | `tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_post_import_sync_negative_path_regression` | `541c15d4ba9564d9256cb2651fe180c2e230760c2fa56ecb389f145fb8723d00` | Post-import sync失敗がobservableで、committed import resultを破損しない。 | 同上。 | Test double。failed_partial_or_stale、failure reason、committed `.meta.json`を保持する。 |
| 11 | `tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_execute_create_plan_reuse_seam` | `44894dc46328aad1a9352cb69a93975a99701b9a9e14f8d5c9dc25470dcf6efd` | Current create-plan reuse seamがsecond writerなしにaccepted import resultを作る。 | 同上。 | Test double。`execute_create_plan`一回、rules symlink、discussions/new-* absence assertionsを保持する。本番を旧copy APIへ戻さない。 |
| 12 | `tests/cli_runtime/test_runtime_shell_s11.py::TestRuntimeShellS11::test_final_api_call_site_and_structural_regression` | `0c1088f1a15dd18d672fe5707d9add3ffe1593b6ead070d90ba553019c498790` | Runtime shell call sitesがaccepted layered API structureを保持する。 | Historical causeは`commands/new.py`の`domain.artifacts`直接import。P392 sourceでは既にapplication contract経由。 | Product-boundary acceptance。`commands/new.py -> application.contracts -> domain.artifacts`を保持し、existing structural testをnormal passさせる。preflight一致時はProduct edit 0でledgerだけを解決する。 |
| 13 | `tests/cli_runtime/test_sync.py::TestCliSync::test_new_and_active_and_sync` | `f9b206f85a7c0ee352b4019eaed232ee02dcf896c150659fa7e8191f125951a6` | New node、selection-only active state、syncがaccepted generated stateへ収束する。 | 廃止済み`active set --force`を使用。 | Test observer。`active set iss-00003`へ置換し、active path、index/tree、symlink/pathfile、sync assertionsを保持する。 |
| 14 | `tests/cli_runtime/test_sync.py::TestCliSync::test_sync_emits_tree_puml_ready_board_at_spec_dock_root` | `3d1b673b92516964bd29b91cf29c8e03c553988dc9e0df7f0a9aee16dc545619` | SyncがSpecDock rootへaccepted tree、PUML、ready-board outputを生成する。 | 廃止済み`active set --force --no-checkout`を使用。 | Test observer。`active set 305`へ置換し、return code 0を確認してroot outputsの内容assertionsを保持する。 |
| 15 | `tests/cli_runtime/test_workbench.py::TestCliWorkbench::test_copied_workbench_readme_and_payloads_remain_opaque_to_runtime_commands` | `20d53420c38ab501c64346e6e22a0b309b2358191fe74a54ed9c20717ddb09b9` | Copied Workbench READMEとpayload bytesがruntime commandsに対してopaqueである。 | 廃止済み`active set --force`失敗後に未生成`active.json`を読む。 | Test observer。`active set --id scope_id`のsuccessを先にassertし、copy前後のbytes、active fields、index、validate/sync/deps/active observationsを保持する。 |

Row 2は本Issueのactive scopeではない。既存`resolved/superseded`、historical node、successor `tests/cli_runtime/test_distribution_cutover.py::test_s40b_retained_skill_identity_matches_current_provider_and_dogfood`をread-onlyで保持する。

## 7. Detailed requirements

### I395-RQ-001 — Exact baseline and specification-history admission

§4をすべて満たす。P392 entry、elaboration input、support-history checkpoint、current spec freezeを別のidentityとして記録し、current tipがP392 Product/test/ledgerを保持することをpath-level diffで証明する。GitHub IssueのOPEN/CLOSED、SpecDock `ready=true`、過去candidateのtest結果だけでentryを代替しない。

Canonical primary packはexact 6 pathsである。Exact 16 support artifactsはpreserved support historyとしてのみadmitし、current canonical packまたはowned write surfaceへadmitしない。Plan B5は三つのhistory segmentのpath-set検証と、16 support pathsのtree-entry equalityを実行する。Manifestの自己申告、working-tree上の存在、directory prefix allowlist、過去のZIP hashだけではこの検証を代替できない。

### I395-RQ-002 — Cause-appropriate repair

Rows 1、4–11、13–15はtest harness/observerを修正し、Productを廃止済みCLI/APIへ退行させない。Row 3はProduct identity boundaryを修正する。Row 12はcurrent compliant boundaryを保護し、不要なsource変更を行わない。修正後に同じaccepted behaviorがnormal passすることをrowごとに観測する。

### I395-RQ-003 — Read-only identity / publication separation

`infra/git_cli.py`のexisting symbolsで次を成立させる。

- `_parse_github_repo_slug`はread-only identity parserとしてcredential-bearing HTTPS originからowner/repo slugを抽出できる。
- `origin_github_repo_slug`はfetch originだけを読み、read-only identityを返す。push URLやpublication可否を要求しない。
- `origin_github_publication_endpoint`はfetch/push両方を読み、どちらかにuserinfoがあれば拒否し、両slug不一致を拒否する。
- `_remote_has_userinfo`と`_redact_remote_url`を維持し、credential-bearing URL、username、password、tokenをexception、stdout、stderrへ展開しない。
- `application.ports.GitGateway.origin_github_repo_slug`、`cli.bootstrap._GitGateway.origin_github_repo_slug`、`application.repo_context.require_current_repo_slug`のpublic/internal signatureを変更しない。
- `application.import_node`のsame-repository validation、numeric target current-scope requirement、foreign URL rejectionを弱めない。

### I395-RQ-004 — Descriptor-bound harness repair

`tests/cli_runtime/test_runtime_import_s10.py::_StubTemplateScaffolder`へ、current `TemplateScaffolder.copy_scaffolded_tree_at(src_dir, dest_dir, dest_dir_fd, replacements)`と同じcall shapeを実装する。test doubleはcurrent `infra.template_scaffolder.copy_scaffolded_tree_at`へ委譲してdescriptor-bound write、collision check、binary/text handling、mode/shebang preservationを再利用できる。Production `application.create_node.execute_create_plan`のheld descriptor経路を変更せず、旧`copy_scaffolded_tree`へ戻さない。

### I395-RQ-005 — Selection-only observer repair

Rows 1、13、14、15から`--force`と`--no-checkout`を除去する。現行`commands.active._add_active_set_arguments`が公開するpositional target、`--id`、`--github-issue`だけを使う。各active operationのreturn codeを後続file readより前に確認する。元のdelete/sync/Workbench invariantsは削除・緩和しない。

### I395-RQ-006 — Thin-shell application contract

Row 12のcurrent stateを次のstable boundaryとして保持する。

- `commands/new.py`は`CURRENT_CREATABLE_ARTIFACT_TYPES`を`application.contracts`からimportする。
- `application/contracts.py`が`domain.artifacts`のsingle catalogueをapplication contractとしてre-exportする。
- `domain/artifacts.py`だけがcatalogue valueの正本である。
- `commands/*`は`domain`、`infra`、`app`を直接importしない。
- Existing structural testのlegacy helper、commands layer、application-to-infra、infra-to-shell assertionsをすべて保持する。

Current blobsがP392と一致する限り、row 12のProduct sourceは変更しない。直接依存の再出現、catalogue複製、old type復活を検出した場合は、仕様と実装入力のdriftとして停止し、黙って別設計を選ばない。

### I395-RQ-007 — Ledger transition

14 rowsのProduct/test observationsがnormal passした後にだけ`full-regression-ledger.json`を変更する。

- Rows 1、3–15: `lifecycle`を`resolved`へ変更し、`resolution_mode`を`fixed-in-place`へ追加する。
- `nodeid`、`fixed_point_signature_sha256`、`current_signature_sha256`、historical status、disposition、historical top-level fieldsを変更しない。
- Row 2の`resolved`、`superseded`、successorを変更しない。
- Row追加、削除、rename、successor substitution、retired化を行わない。
- Current truthは修正後observationと`evaluate_baseline`のnormal-pass判定で証明する。JSON textだけで解決を宣言しない。

Targetはexact 15 total / 0 active / 15 resolved / 14 fixed-in-place / 1 superseded / approved 0 / unexpected 0である。

### I395-RQ-008 — No masking

Skip、xfail、approved failure、marker変更、policy skip reason変更、assertion削除、mock-only success、signature書換え、row削除、node rename、silent retirement、別successorへの置換、full verifier scope縮小、`continue-on-error`を禁止する。

### I395-RQ-009 — Transitional policy continuity

`full-regression-timing-weights.json`の243 entries、`tests/conftest.py`のfour required-fastとpolicy skip、`scripts/quality/full_regression_baseline.py`、`scripts/quality/verify_full_regression.py`、4-shard execution、Provider CI、main-push/workflow-dispatch Full Regressionを変更しない。Current verifierをIssue #396のfuture gateへ置き換えない。

### I395-RQ-010 — Lifecycle, protected data and dogfood

#392 lifecycle/wire/record/migration/uninstall/recovery/coordinationはread-onlyである。Row 3のprovider source変更はcandidate-changing shipped runtime変更なので、provider sourceを先にGREENにし、既存lifecycle commandでchecked-in dogfoodへcomplete projectionする。generated mirror、`spec-dock.version`、二つの`.spec-dock-provider-slot.json`を手編集しない。Projection後はruntime mirrorのbytesと、record／二slot markerの新`candidate_digest`が一致し、version 0.2.4、record state `ready`、operation `null`、`seed_policy=preserve-only`、skill slot names、two skill `SKILL.md` bytes、four roots、consumer data、Workbench、initiatives、Artifactsを保持する。

### I395-RQ-011 — Non-regression gates

次をすべて独立にpassさせる。

- 14 row focused RED/GREEN evidence
- Row 2 successor
- `tests/unit/test_full_regression_baseline.py`
- ordinary `uv run pytest`
- current full verifier 4 shards
- provider lifecycle focused suite
- source/wheel/sdist/installed/dogfood candidate parity
- Linux/macOS Provider distribution parity相当のfocused suites
- `make lint`
- `spec-dock validate`
- ledger/timing/required-fast/policy/workflow no-touch checks
- protected data and dogfood byte parity

### I395-RQ-012 — Same-tip B1/B2

HumanがIssue PRを`codex/epic-00384-provider-test-strategy-planning`へmergeした後、integration branchのexact full SHAを固定する。そのSHAでB1を先に確認し、同じSHAでB2を確認する。B1/B2 receiptにsource SHA/tree、commands、result artifacts、row counts、violations、dogfood/lifecycle protection、rollback readinessを記録する。別commit、rerunによる差替え、future SHAのtracked文書への先書きを行わない。

### I395-RQ-013 — Implementation permission separation

次の状態を別々に扱う。

1. formal Issue start
2. implementation-ready specification
3. independent spec review pass
4. explicit implementation dispatch
5. Product/test implementation GREEN
6. code review / Final Quality Gate pass
7. human PR merge
8. same-tip B1/B2
9. #392/#395 closure

本packの作成完了は2までである。独立spec review passを実効ゲートとして残したうえで、ユーザーが本メッセージで明示的なimplementation dispatchを行ったため、現在の実装許可はtrueである。`owner_decisions_required=[]`は設計判断が未決でないことだけを示し、実装完了やmerge許可を意味しない。

今回の仕様修正で、current canonical packをexact 6 paths、existing 16 artifactsをimmutable support historyとして分類する判断をRequirement、Design、Planへ明示した。`implementation_allowed=true`はこのowner dispatchを保持するが、spec review failまたはpendingの間は実効的なProduct/test/ledger/dogfood mutationを許可しない。修正後のexact SHA/treeでfresh Strict specification reviewが`review_status=pass`、P0=0、P1=0となり、Phase E execution packetとconcurrent-writer absenceが成立した後にだけmutationを開始できる。

### I395-RQ-014 — Evidence and traceability

各rowについて、entry observation、changed path/symbol、RED reason、GREEN assertion、focused command、ledger state、full-verifier resultを一対一で記録する。未commit working-tree verifierはdiff SHA-256付きのprovisional evidenceに限り、merge-readyへ使わない。Final evidenceはclean pushed implementation SHA/treeでfull verifierと全merge-blocking gatesを再実行して束縛し、secretを含めない。Handoff evidence schemaに欠落があればmerge-readyとしない。

### I395-RQ-015 — Rollback

Rollback unitはwhole Issue #395 mergeである。#396開始前にB1またはB2が失敗した場合、humanはwhole-merge revertでP392のknown 14-active baselineへ戻すか、#395 owned boundary内のforward-fixを選ぶ。Ledgerだけ、Productだけ、testだけを部分的に戻してcurrent policyを不整合にしない。#396 workが開始済みなら停止・保存し、dependent suffixを逆順に扱う。

### I395-RQ-016 — Stop and return

次の場合は変更を停止し、親ownerへexact evidenceを返す。

- Repository、branch、P392 SHA、spec freeze SHA、upstream/remoteの不一致
- P392からcurrent spec freezeまでに許可外Product/test/policy差分がある
- 15 rows、14/1 count、nodeid、signature、row order、row 2 successor、timing 243のdrift
- Entry verifierにrows 4–12、15以外のviolation、#392-owned failure、unexpected failureがある
- Current path/symbolが存在しない、またはrow 12のcompliant boundaryが失われている
- Accepted behaviorを満たすためにlifecycle wire、`E384-QUAL-001`、policy retirement、workflow redesign、main merge、new Issueが必要
- Publication strictness、secret non-exposure、same-repo validationを両立できない
- Dogfood projectionがversion/lifecycle/protected dataを変更する
- New owner decisionが必要、または`owner_decisions_required`がnon-empty

### I395-RQ-017 — Issue #392 boundary assertion synchronization

今回ユーザーが明示承認したスコープ拡張として、`tests/integration/test_issue_392_acceptance.py`をIssue #395のtracked implementation pathへ追加する。このpathで許可される変更は、`_ISSUE_BOUNDARY_SHA256`に記録されたIssue #395 Requirement／Design／Planの3つの期待SHA-256を、今回の最終spec freezeの実体へ同期することだけである。

Issue #392のbaseline、ledger、timing、required-fast、policy、workflow、その他のboundary assertionは変更しない。assertionの削除・弱化・skip・xfail化は行わず、同期後に同じテストをfull-regression laneでnormal passさせる。この同期は仕様修正との整合を回復するentry前提であり、Productの挙動やIssue #392の契約を変更するものではない。

## 8. Non-goals

- #392 lifecycle/wire、migration、uninstall、recovery、coordinationの変更
- #396のbuild-once gate、E384-QUAL-001 implementation/evidence、policy retirement、required-context transition
- Ledger/timing/sharder/policy/workflowの削除または再設計
- Product feature追加、general refactor、unrelated cleanup、new Issue作成
- Mainへの直接merge、agent merge、automatic rollback、Issue close
- Historical top-level 27-countのcurrent authority化
- Deleted active flags、old scaffolder API、direct domain importの復活

## 9. Traceability

| Parent / Issue contract | 本書 |
|---|---|
| E384-RQ-001–003 / C-001、C-002、C-010 | §2、§4、I395-RQ-013 |
| E384-RQ-007 / C-005 | §2.2、§6、I395-RQ-007 |
| E384-RQ-009 | §4、I395-RQ-009、I395-RQ-011 |
| E384-RQ-010 | §6、I395-RQ-002–008 |
| E384-RQ-011 / B1–B2 | §3、I395-RQ-009–012 |
| E384-RQ-015 | I395-RQ-010 |
| E384-RQ-016–018 | §8、I395-RQ-013–016 |
| E384-RQ-019 / Provider Lifecycle Wire | §5.2、I395-RQ-010、§8 |
| Register §6.1 | §6、I395-RQ-002–007 |
| Rolling-Wave Contract §4–5 | §4、I395-RQ-013–014 |

## 10. Decision state

今回の仕様修正で、Issue固有のadmission/history decisionを次のとおり確定した。current canonical specification packはexact 6 pathsを維持し、existing exact 16 support artifactsはimmutable、non-authoritative、grandfathered support historyとして保存する。新しいsupport artifactを追加せず、support historyの内容をcurrent authorityへ昇格させない。この決定はProduct、security、lifecycle、policy、parent contractを変更しない。

従って、親のE384-DEC-001、E384-DEC-002、E384-DEC-004、accepted P392 sequence ADRを再審議せず、`owner_decisions_required=[]`を維持する。ユーザーによる本明示承認により、`implementation_allowed=true`も維持する。ただし、これはProduct実装完了、code review、human merge、B1/B2、Issue closureを意味しない。修正後のfresh Strict specification reviewがpassするまで、実効的なmutation gateは閉じる。
