---
種別: 実装計画書（Issue）
ID: "iss-00405"
タイトル: "Directory Replacement Final Cleanup"
関連GitHub: ["#405"]
状態: "仕様候補draft"
最終更新: "2026-09-20"
依存: ["requirement.md", "design.md"]
親: ["epic-00384", "init-local-00003"]
---

# iss-00405 Directory Replacement Final Cleanup — 実装計画

詳細: [Issue Plan Guide](../../../../../../docs/authoring/issue-plan.md)

> 本計画はmodel非依存のcanonical planです。Luna Max向け実行補助は[artifacts/20260920t055027z-luna-max-handoff.md](artifacts/20260920t055027z-luna-max-handoff.md)に分離します。

## Planning Level

**selected level: `strict`**

理由:

- runtime Git interface、worktree filesystem safety、installer failure recovery、package/dogfood compatibilityへ横断的に影響します。
- public CLIを増やさない一方、誤った削除はcheckout拒否の緩和、worktree target誤操作、旧保証復活につながります。
- rollbackは可能ですが、types/ports/adapters/consumer/tests/docsを一つの整合したchangeとして扱う必要があります。
- security/privacy boundaryを一部保持し一部撤去するため、negative testと明示的なhandoffが必要です。

`critical`ではありません。現在のscopeは不可逆な利用者data mutation、credential disclosureの容認、incident responseを必要とするmigrationを含みません。

### 再評価条件

次のいずれかが発生した場合、実装を停止し`critical`またはRequirement/Design再審議へ戻します。

- 利用者dataを削除・変換する必要が生じる。
- credential/private data露出を許容しなければ実装できない。
- worktree cleanupが別inodeを削除しうる。
- target-bound helperを廃止してpath-based cwdだけにする必要が生じる。
- automatic installer rollback/journalなど対象外のpublic contractが必要になる。

## 基点と入口条件

- code investigation baseline (not the adopted specification commit): `chemitaro/spec-dock` / `iss-00405-directory-replacement-final-cleanup` / `457faf31df8840d1f2fc87417d297dc318903fbe`
- Issue #405はOPEN、active Issueは`iss-00405`、実装branchは`iss-00405-directory-replacement-final-cleanup`。
- 前回監査ZIPはblob `252cc71326e58639dbdd35220e391c21dd81854c` / SHA-256 `9d7f1813c2d724f0089f0a5ef0197c7a501629e108a96b70647bee52114a90b7`としてexact artifact確認済み。
- ChatGPTは実装・tests・browser validatorを実行していません。
- Codex側限定証拠: `uv run pytest tests/unit/infra/test_directory_installation.py -q` → `11 passed in 0.96s`, exit 0。これはpre-implementation 11 nodeだけの証拠です。

実装開始時は次を再確認します。

```bash
git branch --show-current
git rev-parse HEAD
git status --short
git config user.name
git config user.email
./spec-dock/scripts/spec-dock active show
```

期待:

- branchが`iss-00405-directory-replacement-final-cleanup`
- adopted spec commitをHEADとして記録し、その同一SHAを対象とする独立仕様review証跡と照合（457faf31はコード調査履歴であり、この仕様固定点ではない）
- working tree clean
- identityが`chemitaro` / `84865385+chemitaro@users.noreply.github.com`
- active Issueが`iss-00405`

不一致は自動修正せず停止します。

## 目標

1. F001〜F009を同一Issueで解消します。
2. provider generation/shared leaseを撤去しつつworktree target/data-operation safetyを保持します。
3. installerの不足coverageを追加し、不要なProduct変更を避けます。
4. provider-first編集とdogfood同期を行います。
5. normal quality pathでmerge-ready PRまで進め、人間merge前に停止します。

## 順序・依存

```text
S0 specification adoption
  → S1 successor tests and exact disposition
  → S2 runtime Git boundary implementation
  → S3 focused runtime checkpoint
  → S4 installer/test-harness cleanup
  → S5 docs/dogfood/parent authority update
  → S6 local integrated qualification
  → S7 PR creation / CI / independent review / report / handoff
```

S1とS2を逆転しません。先に残す安全性と撤退するgateのsuccessorを固定します。S4のmid-copy testは現行実装でGreenでもよく、Redを作るためのProduct変更は行いません。S5のdogfood updateはS2/S4がprovider側で安定してから行います。

## 実装step

### S0 — 仕様採用とbaseline checkpoint

**入口**

- 本packの`requirement.md`、`design.md`、`plan.md`がcanonical Issue pathへ完全置換済み。
- independent specification reviewの対象bytesが固定されている。

**作業**

1. frontmatter ID/parent/GitHub/stateを確認します。
2. `artifacts/test-disposition.csv`をparseし、current exact nodeがcollect-only出力と対応することを確認します。
3. browser validatorで`artifacts/cleanup-guide.html`のPlantUML 2図、contract v2、diagnostic rejection、zoom modalを検証します。
4. `./spec-dock/scripts/spec-dock validate`を実行します。
5. specification reviewのblocking findingを解消します。

**出口**

- specification candidateのhashとreview結果がCodex側evidenceへ記録される。
- Product sourceは未変更。

**checkpoint commit候補**

```text
docs(spec): Issue 405の最終cleanup仕様を固定
```

### S1 — F001 successor testsとtest処置を先に固定

**入口**

- S0 pass、clean tree。

**変更path / node**

- `tests/cli_runtime/test_generation_checkout.py`
- `tests/cli_runtime/test_worktree.py`
- `tests/cli_runtime/test_runtime_handoff.py`
- `tests/cli_runtime/test_worktree_lifecycle_coordination.py`

**作業**

1. `TestGenerationCheckout`を`TestCheckoutSafety`へ改名します。
2. new/existing checkout testをfixed commit/clean tree contractへREWRITEします。
3. dirty tree successorを追加します。
4. hooks/fsmonitor/diff/merge/sparseのpositive parameterized successor 5 caseを追加します。
5. old diff/merge/sparse rejection nodesをDELETEします。
6. submodule testをworktree materializer/entrypoint-last successorへ移します。
7. target-bound helper shadowingとread-tree target cwd successorをREWRITEします。
8. target EX/inode、consumer hook、cross-filesystem、safe cleanup testsはbehaviorを変えず名称だけcurrent責務へ変更します。

**期待差分**

- positive gate-removal casesはfirst runをそのまま記録します。現行broad gateでRedになり得ますが、Greenなら`covered-existing`です。
- dirty、target safety、consumer hook testsはGreenを維持します。
- native Gitがconfiguration自体を拒否した場合はtest setupを安全な設定へ修正し、Productに回避コードを追加しません。

**command**

```bash
uv run pytest \
  tests/cli_runtime/test_generation_checkout.py \
  tests/cli_runtime/test_worktree.py \
  tests/cli_runtime/test_runtime_handoff.py \
  tests/cli_runtime/test_worktree_lifecycle_coordination.py \
  -q
```

**出口**

- Redがある場合はprovider broad gate由来に限定され、Green caseは`covered-existing`として記録済み。
- KEEP safety testの新規failureは0。

**stop**

- target inode/entrypoint-last/data safety testが失敗したらS2へ進みません。
- test削除だけでGreenにしません。

**checkpoint境界**

S1はRed/Greenの観測段階であり、単独ではコミットしません。S1のtest変更とS2のproduction変更を同一の作業単位とし、S3までの必要な検証がGreenになった時点でまとめてコミットします。意図的に失敗するtestだけのcheckpointは作りません。

### S2 — F001 runtime Git boundaryを実装

**入口**

- S1 first runのRed/Green（`covered-existing`を含む）が記録済み。

**変更path / symbol**

- `application/contracts.py`: `GitCapabilityAssessment`, `PinnedCheckout`
- `application/ports.py`: `GitGateway`
- `application/set_active.py`: `checkout_active_target`, global witness
- `application/issue_lifecycle.py`: `issue_start`
- `application/worktree.py`: source/target binding flow
- `cli/bootstrap.py`: `_GitGateway`
- `infra/git_cli.py`: `_run_git_write`, capability/checkout/worktree functions
- `infra/git_helper.py`: parser/validation/child execution

**作業順**

1. typesとProtocolをTarget interfaceへ変更します。
2. infra direct fixed-ref checkoutとtarget-bound cwd executorを実装します。
3. bootstrap adapterを更新します。
4. `set_active`/`issue_lifecycle`からglobal witnessと二重再認証を削除します。
5. worktree source shared lockをunlocked filesystem probeへ変更します。
6. add/remove/materializeの`source_fd`/`lease_fd` couplingを削除しtarget FDを保持します。
7. active provider sourceでold symbol scanを0件にします。

**期待差分**

- no public CLI/schema change。
- `git_helper.py`は残るが`lease`語彙とrepository shared flockを持たない。
- `GuardedExplicitFileSource`、create/import lock、target `LOCK_EX`は残る。

**focused command**

```bash
uv run pytest \
  tests/cli_runtime/test_generation_checkout.py \
  tests/cli_runtime/test_worktree.py \
  tests/cli_runtime/test_runtime_handoff.py \
  tests/cli_runtime/test_worktree_lifecycle_coordination.py \
  tests/cli_runtime/test_issue_lifecycle.py \
  -q
```

**static command**

```bash
rg -n 'GitCapabilityAssessment|PinnedCheckout|assess_capabilities|pinned_checkout|verify_pinned_checkout|runtime-generation-drift|_LAST_PINNED_CHECKOUT|last_pinned_checkout|lease-retaining|--lease-fd' \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime
```

期待: 0件。

**出口**

- S1 successor全Green。
- issue lifecycle ordering tests Green。
- source provider old terms 0件。

**recovery**

- checkpoint前はworking treeを破棄せずdiffを保存し、types→infra→adapter→consumerの順で欠落を直します。
- checkpoint後のregressionはcommit全体をrevertします。old provider mechanismの一部だけを戻しません。

**checkpoint commit候補（S3の必要検証完了後、S1〜S3をまとめる）**

```text
refactor(runtime): provider世代認証を通常Git操作から撤去
```

### S3 — runtime focused checkpoint

**入口**

- S2 implementation complete。

**作業**

1. provider sourceでfocused testsを再実行します。
2. `tests/cli_runtime`全体を実行します。
3. create/import/artifact/security focused regressionを実行します。
4. `make lint`を実行します。

**command**

```bash
uv run pytest tests/cli_runtime -q
uv run pytest \
  tests/unit/application \
  tests/unit/infra/test_binary_artifact_publisher.py \
  tests/cli_runtime/test_artifact_import_file.py \
  tests/cli_runtime/test_import.py \
  tests/cli_runtime/test_new.py \
  -q
make lint
```

**出口**

- runtime laneとdata/security regressionがGreen。
- secret/credentialを含むfailure出力が増えていない。

**stop**

- security/privacy assertionを緩和しなければ通らない場合。
- new public error/schema changeが必要な場合。

### S4 — F003/F004/F006/F007/F009 test・harness cleanup

**入口**

- S3 pass。

**変更path / symbol**

- `tests/unit/infra/test_directory_installation.py`
- `tests/unit/infra/test_init_update.py::_managed_tree_bytes`ほか3 node
- `tests/unit/infra/conftest.py`
- `tests/cli_runtime/conftest.py`
- `tests/cli_runtime/harness.py`
- `tests/cli_runtime/test_distribution_cutover.py`
- runtime handoff/worktree lifecycle test names

**作業**

1. runtime smokeのmarker単独assertを削除しcurrent catalog smokeへ改名します。
2. `_managed_tree_bytes`のmarker例外を削除します。
3. old skill単独absence、provider_lifecycle fixture語、backward_compat lock名をcleanupします。
4. mid-copy failure testを4th-copy injectionへREWRITEします。
5. unit conftestのdead 3 prefixを削除し、live `test_checked_in_dogfooding_`だけを保持します。
6. CLI conftestのdead distribution special branchを削除します。
7. harnessのretired skill列挙を削除し、全installed `*/SKILL.md`がexact 2件であるpositive equalityへ変更します。
8. S40B/S45/T01/T04/T10/T11/ProviderLifecycleの指定nodeをcurrent責務名へ変更します。

**mid-copy test command**

```bash
uv run pytest tests/unit/infra/test_directory_installation.py -q
```

期待: 11 node pass。pre-implementationの`11 passed in 0.96s`は旧内容であり、新内容のpassを別途記録します。new testが最初からpassする場合は`covered-existing`です。

**追加command**

```bash
uv run pytest tests/cli_runtime/test_distribution_cutover.py -q
```

`tests/unit/infra/test_init_update.py`の全件実行はprovider/dogfood parityを含むため、S5の同期直後に行います。S4ではテスト内容を変更し、上記同期非依存のfocused検証を実施します。KEEP parityを削除・skip・弱化しません。S4変更のcheckpointはS5の同期後suite Greenまで保留し、S4/S5を一つのworking unitとしてコミットします。

**出口**

- F003/F004/F006/F007/F009の変更と上記focused検証が完了。同期依存suiteの確認はS5に明示的に引き継ぐ。
- exact inventory/parityは弱くならない。
- installer Product source変更は、new testがfailし契約上のbugが確認された場合だけ。

**checkpoint commit候補**

```text
test(installer): 中間copy失敗とcurrent catalog契約を固定
```

### S5 — F002/F005/F008 docs、dogfood、親authority

**入口**

- S3およびS4の同期非依存focused testsがGreen。
- S4変更は未コミットで引き継ぎ可能。同期依存のtest_init_update全件Greenを入口条件にしない。protected dataは直前checkpointと一致。

**provider-first編集**

1. `README.md`の管理対象説明を6directory exact listへ変更します。
2. `src/spec_dock/assets/spec_dock/docs/README.md`から旧descriptor/source-resume 2 bulletを削除し、6directory/nontransactional contractへ統一します。
3. `src/spec_dock/assets/spec_dock/scripts/README.md`の3directory表現を6directoryへ修正します。

**dogfood同期**

この時点では親Epic/Issueのtracked data文書をまだ変更しません。protected pathがHEADと一致することを確認して次を実行します。

```bash
git diff --exit-code HEAD -- spec-dock/initiatives
uvx --no-cache --from . spec-dock update .
git diff --exit-code HEAD -- spec-dock/initiatives
```

期待:

- `spec-dock/docs`、`spec-dock/templates`、`spec-dock/system`、`spec-dock/scripts`、`.agents/skills/spec-dock`、`.agents/skills/spec-dock-grill-with-docs`のtooling mirrorだけがproviderと同期。
- `spec-dock/initiatives`を含むdataは変わらない。

**同期後の必須検証**

```bash
uv run pytest tests/unit/infra/test_init_update.py -q
```

S4で変更したhelper/testとKEEP parityを全件確認します。失敗はこの作業単位で修正し、suite Green前にS4/S5完了やworking checkpointを記録しません。

**親authority更新**

protected path不変を確認した後に、親Epic `plan.md`へ#404/main mergeの履歴と#405 final cleanupの位置付けを記録します。親Epic `report.md`冒頭はcurrent outcomeへ更新し、旧shared coordination/qualification chronologyをHistorical appendixへ移します。S5時点ではverificationを`pending`として扱い、S7で実測値へ更新します。完了を先書きしません。

**scan**

```bash
rg -n 'immediate-child evidence|durable directory semantic digest|compatible newer package|semantic drift.*write 0|source replacement.*write 0' \
  README.md \
  src/spec_dock/assets/spec_dock/docs \
  src/spec_dock/assets/spec_dock/scripts \
  spec-dock/docs \
  spec-dock/scripts
```

期待: current docs 0件。historical artifactsはscan対象外。

**出口**

- F002/F005/F008解消。
- provider/dogfood bytes一致。
- parent docsは実測したstatusだけを記録。

**checkpoint commit候補**

```text
docs(epic): directory replacement契約へ現行資料を統一
```

### S6 — local integrated qualification

**入口**

- S1〜S5 checkpoints complete、clean tree。

**順序**

```bash
# focused
uv run pytest \
  tests/cli_runtime/test_generation_checkout.py \
  tests/cli_runtime/test_runtime_handoff.py \
  tests/cli_runtime/test_worktree.py \
  tests/cli_runtime/test_worktree_lifecycle_coordination.py \
  tests/cli_runtime/test_distribution_cutover.py \
  tests/unit/infra/test_directory_installation.py \
  tests/unit/infra/test_init_update.py \
  -q

# full normal suite
uv run pytest
make lint

# package/distribution surface
uv build
uv run pytest tests/integration/test_epic_00343_distribution.py -q

# repository contract
./spec-dock/scripts/spec-dock validate
```

**platform**

CIは`pull_request`で起動するため、S6ではlocal evidenceを完成させます。次の既存jobの実測はS7でPRを作成した後に取得し、それまでは`pending`です。

- `provider-tests`（Ubuntu）: `make lint`, `uv run pytest`
- `provider-distribution-parity`（Ubuntu/macOS）: `test_directory_installation.py`, `test_cli_smoke.py`

required job名やrepository settingsはagentが変更しません。

**provider/dogfood parity**

```bash
uv run pytest \
  tests/cli_runtime/test_distribution_cutover.py \
  tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_mirror_docs_match_provider_assets \
  tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_mirror_match_provider_assets \
  -q
```

**期待結果**

- commandごとのexit 0と実測件数をIssue Reportへ記録。
- skippedは理由とplatformを記録。
- 再実行していないものをpassと書かない。

**stop/escalation**

- full suite failureをold mechanism testと決めつけて削除しない。
- flaky retryでpassを作らない。first failureを保存し原因分類する。
- data/security failureはblocker。

### S7 — independent review、Report、PR handoff

**入口**

- S6 local evidence complete。PR起動CIはpendingでよく、入口条件にしません。

**作業**

1. Issue `report.md`へS6のlocal実測を記録し、未取得CIを`pending`とします。親Epic Plan/Reportも未完了の項目を完了扱いしません。
2. Conventional Commitsとidentityを確認し、実装candidateをcommit/pushします。PRがなければ作成し、既存PRがあれば更新します。この時点はCI/review待ちでmerge-readyとは記録しません。
3. PR起動の既存Ubuntu/macOS job結果を取得し、integrated diffに対するindependent code/spec/QA reviewを実施します。
4. blocking findingまたはrequired CI failureを修正し、修正後candidateをpushして必要なverification/reviewと当該PRの最新checksを確認します。
5. Issue Reportと親Epic Plan/Reportへlocal/platform/review実測を記録してcommit/pushします。最終pushに対応する最新PR checksもGreenであることを確認します。レビュー証跡はレビューしたcandidate SHAと後続の証拠記録のみのcommitを区別します。
6. AC-405-11/12を含む証拠、blocking review 0、最新PR checks Greenを確認してmerge-readyとし、human merge前に停止します。

**PR説明に含める内容**

- removed provider mechanisms
- retained Git/worktree/data/security checks
- exact test dispositionとsuccessors
- installer mid-copy observation
- provider/dogfood sync
- test/lint/package/platform/validate実測
- rollback/recovery
- remaining risks/none decisions

**出口**

- PR checks Green。
- blocking review finding 0。
- human merge未実行の状態でhandoff。

## チェックポイントcommit境界

| checkpoint | 内容 | commit例 | 混在禁止 |
|---|---|---|---|
| CP0 | canonical specs | `docs(spec): Issue 405の最終cleanup仕様を固定` | Product codeを含めない |
| CP1 | successor tests | `test(runtime): checkout cleanupの後継回帰を固定` | gate削除実装を含めない |
| CP2 | F001 runtime implementation | `refactor(runtime): provider世代認証を通常Git操作から撤去` | docs authority更新を含めない |
| CP3 | installer/test harness cleanup（CP4とまとめ、S5同期後suite Greenでcommit） | `test(installer): 中間copy失敗とcurrent catalog契約を固定` | unrelated module split禁止 |
| CP4 | docs/dogfood/parent docs（CP3と同一working commit） | `docs(epic): directory replacement契約へ現行資料を統一` | 実測前のpass記録禁止 |
| CP5 | verification/report fixes | finding内容に応じる | human merge禁止 |

各commit前にidentityと`git diff --check`を確認します。commit後はremote push前にそのcheckpointのfocused commandを再実行します。

## 要件追跡表

| Requirement | Design | Step | Verification |
|---|---|---|---|
| REQ-405-01 | DES-405-01〜03 | S1,S2 | checkout successor、dirty test、source term scan |
| REQ-405-02 | DES-405-04〜06 | S1,S2 | worktree/materializer/handoff/lifecycle focused tests |
| REQ-405-03 | DES-405-07 | S2,S6 | create/import lock、artifact/privacy/security existing regression |
| REQ-405-04 | DES-405-08 | S4 | mid-copy failure successor + existing 10 companion nodes |
| REQ-405-05 | test disposition | S1,S4 | `artifacts/test-disposition.csv`全行 |
| REQ-405-06 | docs sync design | S5 | provider/dogfood bytes、old guarantee scan |
| REQ-405-07 | parent authority design | S5,S7 | Epic Plan/Report diff + Issue Report evidence |
| REQ-405-08 | verification design | S6,S7 | full pytest/lint/package/platform/validate/review/PR |

## 旧テスト処置の完全一覧

以下は監査inventoryの全test caseを省略せず展開した実装時処置です。CSV版は`artifacts/test-disposition.csv`を正本とします。`KEEP`でsuccessorが異なる行はbehavior KEEP + RENAMEです。`NEW`はIssue #405で追加するsuccessorです。

| ID | current exact node | line/case | 処置 | successor exact node | step |
|---|---|---|---|---|---|
| TI-0001 | `tests/unit/infra/test_init_update.py::test_issue_334_init_and_update_install_current_target_catalog_byte_exact` | 65 / — | KEEP | `tests/unit/infra/test_init_update.py::test_issue_334_init_and_update_install_current_target_catalog_byte_exact` | S6 |
| TI-0002 | `tests/unit/infra/test_init_update.py::test_issue_334_update_preserves_unmanaged_content` | 84 / — | REWRITE | `tests/unit/infra/test_init_update.py::test_issue_334_update_preserves_unmanaged_content` | S4 |
| TI-0003 | `tests/unit/infra/test_init_update.py::test_issue_334_checked_in_dogfood_projection_matches_provider` | 100 / — | KEEP | `tests/unit/infra/test_init_update.py::test_issue_334_checked_in_dogfood_projection_matches_provider` | S6 |
| TI-0004 | `tests/unit/infra/test_init_update.py::test_grill_with_docs_source_boundary_separates_access_context_from_evidence` | 124 / — | KEEP | `tests/unit/infra/test_init_update.py::test_grill_with_docs_source_boundary_separates_access_context_from_evidence` | S6 |
| TI-0005 | `tests/unit/infra/test_init_update.py::test_issue_360_spec_dock_guidance_is_agent_first_and_not_present_only` | 159 / — | KEEP | `tests/unit/infra/test_init_update.py::test_issue_360_spec_dock_guidance_is_agent_first_and_not_present_only` | S6 |
| TI-0006 | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_init_gitignore_ignores_exact_workbench_directories_at_supported_scopes` | 1189 / — | KEEP | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_init_gitignore_ignores_exact_workbench_directories_at_supported_scopes` | S6 |
| TI-0007 | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_workbench_readme_assets_are_byte_identical_and_complete` | 1233 / — | KEEP | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_workbench_readme_assets_are_byte_identical_and_complete` | S6 |
| TI-0008 | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_78_init_allows_install_when_legacy_hidden_workspace_exists` | 1260 / — | KEEP | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_78_init_allows_install_when_legacy_hidden_workspace_exists` | S6 |
| TI-0009 | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_78_update_keeps_legacy_hidden_workspace_untouched_during_coexistence` | 1278 / — | KEEP | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_78_update_keeps_legacy_hidden_workspace_untouched_during_coexistence` | S6 |
| TI-0010 | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_init_and_update_ship_root_artifact_rules_and_import_links_them_safely[init]` | 1301 / init | KEEP | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_init_and_update_ship_root_artifact_rules_and_import_links_them_safely[init]` | S6 |
| TI-0011 | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_init_and_update_ship_root_artifact_rules_and_import_links_them_safely[update]` | 1301 / update | KEEP | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_init_and_update_ship_root_artifact_rules_and_import_links_them_safely[update]` | S6 |
| TI-0012 | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_69_native_build_venv_installs_backend_requirements_in_place` | 1343 / — | KEEP | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_69_native_build_venv_installs_backend_requirements_in_place` | S6 |
| TI-0013 | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_69_pip_unavailable_fallback_keeps_target_install_semantics` | 1405 / — | KEEP | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_69_pip_unavailable_fallback_keeps_target_install_semantics` | S6 |
| TI-0014 | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_built_wheel_replaces_stale_python_and_asset_output` | 1449 / — | REWRITE | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_built_wheel_replaces_stale_python_and_asset_output` | S4 |
| TI-0015 | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_distribution_full_install_root_inventory_is_packaged_in_wheel_sdist_and_installed_resources` | 1492 / — | KEEP | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_distribution_full_install_root_inventory_is_packaged_in_wheel_sdist_and_installed_resources` | S6 |
| TI-0016 | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_workbench_readme_distribution_inventory_and_bytes_match_all_surfaces` | 1506 / — | KEEP | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_workbench_readme_distribution_inventory_and_bytes_match_all_surfaces` | S6 |
| TI-0017 | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_surface_includes_doctor_and_explicit_target_hint` | 1568 / — | KEEP | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_surface_includes_doctor_and_explicit_target_hint` | S6 |
| TI-0018 | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_mirror_docs_match_provider_assets` | 1596 / — | KEEP | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_mirror_docs_match_provider_assets` | S6 |
| TI-0019 | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_active_none_reports_match_provider_assets` | 1600 / — | KEEP | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_active_none_reports_match_provider_assets` | S6 |
| TI-0020 | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_subprocess_deps_mutation_on_cutover_snapshot` | 1604 / — | KEEP | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_subprocess_deps_mutation_on_cutover_snapshot` | S6 |
| TI-0021 | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_mirror_match_provider_assets` | 1674 / — | KEEP | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_mirror_match_provider_assets` | S6 |
| TI-0022 | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_dogfooding_runtime_inventory_excludes_generated_python_caches` | 1678 / — | KEEP | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_dogfooding_runtime_inventory_excludes_generated_python_caches` | S6 |
| TI-0023 | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_keeps_repo_scoped_import_uniqueness_parity` | 1693 / — | KEEP | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_keeps_repo_scoped_import_uniqueness_parity` | S6 |
| TI-0024 | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_import_release_lock_backward_compat_parity` | 1917 / — | REWRITE | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_import_create_lock_ownership_and_release_parity` | S4 |
| TI-0025 | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_import_import_race_revalidation_parity` | 1967 / — | KEEP | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_import_import_race_revalidation_parity` | S6 |
| TI-0026 | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_import_new_race_revalidation_parity` | 2211 / — | KEEP | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_import_new_race_revalidation_parity` | S6 |
| TI-0027 | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_no_write_preflight_collision_with_active_parent_fallback_parity` | 2462 / — | KEEP | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_no_write_preflight_collision_with_active_parent_fallback_parity` | S6 |
| TI-0028 | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_keeps_repo_scoped_sync_snapshot_parity` | 2718 / — | KEEP | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_keeps_repo_scoped_sync_snapshot_parity` | S6 |
| TI-0029 | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_non_issue_deps_target_status_parity` | 2929 / — | KEEP | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_non_issue_deps_target_status_parity` | S6 |
| TI-0030 | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_issue_create_lock_scope_narrowing_parity` | 3087 / — | KEEP | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_issue_create_lock_scope_narrowing_parity` | S6 |
| TI-0031 | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_issue_create_pre_github_validation_parity` | 4013 / — | KEEP | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_issue_create_pre_github_validation_parity` | S6 |
| TI-0032 | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_non_issue_create_guidance_parity` | 4232 / — | KEEP | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_non_issue_create_guidance_parity` | S6 |
| TI-0033 | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_create_mode_graph_preflight_parity` | 4465 / — | KEEP | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_create_mode_graph_preflight_parity` | S6 |
| TI-0034 | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_keeps_unscoped_current_repo_fallback_sync_parity` | 4620 / — | KEEP | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_keeps_unscoped_current_repo_fallback_sync_parity` | S6 |
| TI-0035 | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_keeps_repo_scoped_validation_doctor_parity` | 4814 / — | KEEP | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_keeps_repo_scoped_validation_doctor_parity` | S6 |
| TI-0036 | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_keeps_numeric_branch_current_repo_overlap_parity` | 4974 / — | KEEP | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_keeps_numeric_branch_current_repo_overlap_parity` | S6 |
| TI-0037 | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_tool_version_fallback_reads_pyproject` | 5254 / — | KEEP | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_tool_version_fallback_reads_pyproject` | S6 |
| TI-0038 | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_no_skill_option_is_rejected` | 5271 / — | KEEP | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_no_skill_option_is_rejected` | S6 |
| TI-0039 | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_provider_ci_runs_normal_suite_without_a_policy_evaluator` | 5275 / — | KEEP | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_provider_ci_runs_normal_suite_without_a_policy_evaluator` | S6 |
| TI-0040 | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_360_readme_catalog_excludes_historical_artifact_routes` | 5283 / — | KEEP | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_360_readme_catalog_excludes_historical_artifact_routes` | S6 |
| TI-0041 | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_71_upstream_handoff_reports_expose_evidence_bearing_sections` | 5302 / — | KEEP | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_71_upstream_handoff_reports_expose_evidence_bearing_sections` | S6 |
| TI-0042 | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_reference_sync_doc_matches_bundled_asset` | 5382 / — | KEEP | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_reference_sync_doc_matches_bundled_asset` | S6 |
| TI-0043 | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_reference_deps_doc_matches_bundled_asset` | 5392 / — | KEEP | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_reference_deps_doc_matches_bundled_asset` | S6 |
| TI-0044 | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_subprocess_import_post_sync_no_crash_parity` | 5530 / — | KEEP | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_subprocess_import_post_sync_no_crash_parity` | S6 |
| TI-0045 | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_subprocess_issue_create_gateway_failure_pre_github_parity` | 5560 / — | KEEP | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_subprocess_issue_create_gateway_failure_pre_github_parity` | S6 |
| TI-0046 | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_subprocess_numeric_deps_overlap_parity` | 5617 / — | KEEP | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_subprocess_numeric_deps_overlap_parity` | S6 |
| TI-0047 | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_subprocess_scoped_deps_ref_parity` | 5666 / — | KEEP | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_subprocess_scoped_deps_ref_parity` | S6 |
| TI-0048 | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_subprocess_numeric_deps_ref_foreign_only_fail_closed_parity` | 5721 / — | KEEP | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_subprocess_numeric_deps_ref_foreign_only_fail_closed_parity` | S6 |
| TI-0049 | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_subprocess_keeps_lone_unscoped_legacy_without_backfill_parity` | 5765 / — | KEEP | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_subprocess_keeps_lone_unscoped_legacy_without_backfill_parity` | S6 |
| TI-0050 | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_subprocess_keeps_readonly_lone_unscoped_without_backfill_parity` | 5801 / — | KEEP | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_subprocess_keeps_readonly_lone_unscoped_without_backfill_parity` | S6 |
| TI-0051 | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_subprocess_validation_boundary_prefers_structure_error` | 5850 / — | KEEP | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_subprocess_validation_boundary_prefers_structure_error` | S6 |
| TI-0052 | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_subprocess_sync_fails_when_required_artifact_missing` | 5887 / — | KEEP | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_subprocess_sync_fails_when_required_artifact_missing` | S6 |
| TI-0053 | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_subprocess_import_fails_fast_when_required_artifact_missing` | 5905 / — | KEEP | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_subprocess_import_fails_fast_when_required_artifact_missing` | S6 |
| TI-0054 | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_subprocess_import_partial_write_doctor_first_parity` | 5948 / — | KEEP | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_subprocess_import_partial_write_doctor_first_parity` | S6 |
| TI-0055 | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_subprocess_sync_force_degrades_when_required_artifact_missing` | 6025 / — | KEEP | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_subprocess_sync_force_degrades_when_required_artifact_missing` | S6 |
| TI-0056 | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_subprocess_sync_validation_boundary_prefers_structure_error` | 6055 / — | KEEP | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_subprocess_sync_validation_boundary_prefers_structure_error` | S6 |
| TI-0057 | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_subprocess_validate_doctor_fail_when_required_artifact_missing` | 6078 / — | KEEP | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_subprocess_validate_doctor_fail_when_required_artifact_missing` | S6 |
| TI-0058 | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_subprocess_create_lock_missing_meta_diagnosis_parity` | 6102 / — | KEEP | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_subprocess_create_lock_missing_meta_diagnosis_parity` | S6 |
| TI-0059 | `tests/unit/infra/test_directory_installation.py::test_update_replaces_whole_directories_and_preserves_data` | 8 / — | KEEP | `tests/unit/infra/test_directory_installation.py::test_update_replaces_whole_directories_and_preserves_data` | S6 |
| TI-0060 | `tests/unit/infra/test_directory_installation.py::test_installed_runtime_starts_without_provider_markers` | 21 / — | REWRITE | `tests/unit/infra/test_directory_installation.py::test_installed_runtime_starts_from_current_catalog` | S4 |
| TI-0061 | `tests/unit/infra/test_directory_installation.py::test_failed_copy_can_be_retried_without_touching_data` | 37 / — | REWRITE | `tests/unit/infra/test_directory_installation.py::test_update_mid_copy_failure_is_nontransactional_and_rerunnable_without_touching_data` | S4 |
| TI-0062 | `tests/unit/infra/test_directory_installation.py::test_uninstall_dry_run_then_removes_only_tool_directories` | 58 / — | KEEP | `tests/unit/infra/test_directory_installation.py::test_uninstall_dry_run_then_removes_only_tool_directories` | S6 |
| TI-0063 | `tests/unit/infra/test_directory_installation.py::test_symlink_parent_is_rejected_before_any_replacement` | 71 / — | KEEP | `tests/unit/infra/test_directory_installation.py::test_symlink_parent_is_rejected_before_any_replacement` | S6 |
| TI-0064 | `tests/unit/infra/test_directory_installation.py::test_force_init_replaces_tools_without_reseeding_settings` | 88 / — | KEEP | `tests/unit/infra/test_directory_installation.py::test_force_init_replaces_tools_without_reseeding_settings` | S6 |
| TI-0065 | `tests/unit/infra/test_directory_installation.py::test_all_six_directories_match_package_and_discard_old_files` | 98 / — | KEEP | `tests/unit/infra/test_directory_installation.py::test_all_six_directories_match_package_and_discard_old_files` | S6 |
| TI-0066 | `tests/unit/infra/test_directory_installation.py::test_missing_source_is_rejected_before_deleting_anything` | 126 / — | KEEP | `tests/unit/infra/test_directory_installation.py::test_missing_source_is_rejected_before_deleting_anything` | S6 |
| TI-0067 | `tests/unit/infra/test_directory_installation.py::test_version_hard_link_does_not_modify_external_data` | 139 / — | KEEP | `tests/unit/infra/test_directory_installation.py::test_version_hard_link_does_not_modify_external_data` | S6 |
| TI-0068 | `tests/unit/infra/test_directory_installation.py::test_fresh_install_rejects_copy_into_its_scaffold_source` | 153 / — | KEEP | `tests/unit/infra/test_directory_installation.py::test_fresh_install_rejects_copy_into_its_scaffold_source` | S6 |
| TI-0069 | `tests/unit/infra/test_directory_installation.py::test_failed_fresh_init_is_retried_after_preserving_partial_scaffold` | 178 / — | KEEP | `tests/unit/infra/test_directory_installation.py::test_failed_fresh_init_is_retried_after_preserving_partial_scaffold` | S6 |
| TI-0070 | `tests/cli_runtime/test_update.py::TestUpdateCommand::test_update_help_describes_upstream_no_cache_and_default_target` | 7 / — | KEEP | `tests/cli_runtime/test_update.py::TestUpdateCommand::test_update_help_describes_upstream_no_cache_and_default_target` | S6 |
| TI-0071 | `tests/cli_runtime/test_update.py::TestUpdateCommand::test_update_rejects_unsupported_options` | 20 / — | KEEP | `tests/cli_runtime/test_update.py::TestUpdateCommand::test_update_rejects_unsupported_options` | S6 |
| TI-0072 | `tests/cli_runtime/test_uninstall.py::TestUninstallCommand::test_spec_purge_is_rejected_without_mutation` | 8 / — | KEEP | `tests/cli_runtime/test_uninstall.py::TestUninstallCommand::test_spec_purge_is_rejected_without_mutation` | S6 |
| TI-0073 | `tests/cli_runtime/test_uninstall.py::TestUninstallCommand::test_uninstall_help_describes_upstream_no_cache_and_default_target` | 18 / — | KEEP | `tests/cli_runtime/test_uninstall.py::TestUninstallCommand::test_uninstall_help_describes_upstream_no_cache_and_default_target` | S6 |
| TI-0074 | `tests/cli_runtime/test_uninstall.py::TestUninstallCommand::test_uninstall_rejects_unsupported_options` | 31 / — | KEEP | `tests/cli_runtime/test_uninstall.py::TestUninstallCommand::test_uninstall_rejects_unsupported_options` | S6 |
| TI-0075 | `tests/cli_runtime/test_distribution_cutover.py::test_s40b_provider_install_root_is_current_catalog_only` | 55 / — | KEEP | `tests/cli_runtime/test_distribution_cutover.py::test_provider_install_root_is_current_catalog_only` | S4 |
| TI-0076 | `tests/cli_runtime/test_distribution_cutover.py::test_s40b_retained_skill_identity_matches_current_provider_and_dogfood` | 61 / — | KEEP | `tests/cli_runtime/test_distribution_cutover.py::test_retained_skill_identity_matches_current_provider_and_dogfood` | S4 |
| TI-0077 | `tests/cli_runtime/test_distribution_cutover.py::test_s40b_only_runtime_wrapper_is_executable_across_current_surfaces` | 71 / — | KEEP | `tests/cli_runtime/test_distribution_cutover.py::test_only_runtime_wrapper_is_executable_across_current_surfaces` | S4 |
| TI-0078 | `tests/cli_runtime/test_distribution_cutover.py::test_fresh_init_copies_skill_directories_without_markers` | 93 / — | KEEP | `tests/cli_runtime/test_distribution_cutover.py::test_fresh_init_copies_exact_current_external_catalog` | S4 |
| TI-0079 | `tests/cli_runtime/test_distribution_cutover.py::test_s45_fresh_preserves_unrelated_and_obsolete_looking_external_paths` | 103 / — | KEEP | `tests/cli_runtime/test_distribution_cutover.py::test_fresh_init_preserves_unrelated_and_obsolete_looking_external_paths` | S4 |
| TI-0080 | `tests/cli_runtime/test_distribution_cutover.py::test_s45_existing_consumer_seed_is_preserved` | 127 / — | KEEP | `tests/cli_runtime/test_distribution_cutover.py::test_existing_consumer_workflow_is_preserved` | S4 |
| TI-0081 | `tests/cli_runtime/test_distribution_cutover.py::test_s45_foreign_fixed_root_is_preserved_and_blocks_fresh_install` | 138 / — | KEEP | `tests/cli_runtime/test_distribution_cutover.py::test_foreign_fixed_root_is_preserved_and_blocks_fresh_install` | S4 |
| TI-0082 | `tests/cli_runtime/test_distribution_cutover.py::test_init_replaces_the_fixed_skill_directory` | 150 / — | KEEP | `tests/cli_runtime/test_distribution_cutover.py::test_init_replaces_the_fixed_skill_directory` | S6 |
| TI-0083 | `tests/cli_runtime/test_generation_checkout.py::TestGenerationCheckout::test_t10_existing_and_new_checkout_are_pinned_and_generation_safe` | 13 / — | REWRITE | `tests/cli_runtime/test_generation_checkout.py::TestCheckoutSafety::test_issue_start_existing_and_new_checkout_use_fixed_commit_and_clean_tree` | S1 |
| TI-0084 | `tests/cli_runtime/test_generation_checkout.py::TestGenerationCheckout::test_existing_branch_can_use_different_tooling_version` | 54 / — | KEEP | `tests/cli_runtime/test_generation_checkout.py::TestCheckoutSafety::test_existing_branch_can_use_different_tooling_version` | S1 |
| TI-0085 | `tests/cli_runtime/test_generation_checkout.py::TestGenerationCheckout::test_t10_effective_diff_and_merge_attributes_are_rejected_before_mutation[diff=custom]` | 83 / diff=custom | DELETE | — | S1 |
| TI-0086 | `tests/cli_runtime/test_generation_checkout.py::TestGenerationCheckout::test_t10_effective_diff_and_merge_attributes_are_rejected_before_mutation[merge=custom]` | 83 / merge=custom | DELETE | — | S1 |
| TI-0087 | `tests/cli_runtime/test_generation_checkout.py::TestGenerationCheckout::test_capability_guard_covers_the_materialized_tree` | 123 / — | REWRITE | `tests/cli_runtime/test_worktree.py::TestCliWorktree::test_worktree_materializer_rejects_submodule_before_entrypoint_publication` | S1 |
| TI-0088 | `tests/cli_runtime/test_generation_checkout.py::TestGenerationCheckout::test_t10_sparse_checkout_effective_values_and_skip_worktree_are_rejected` | 160 / — | DELETE | — | S1 |
| TI-0089 | `tests/cli_runtime/test_runtime_handoff.py::TestProviderLifecycleHandoff::test_t11_consumer_hook_parent_io_failure_is_detection_failure_with_exit_zero` | 37 / — | KEEP | `tests/cli_runtime/test_runtime_handoff.py::TestRuntimeHandoff::test_consumer_hook_parent_io_failure_is_detection_failure_with_exit_zero` | S4 |
| TI-0090 | `tests/cli_runtime/test_runtime_handoff.py::TestProviderLifecycleHandoff::test_t11_consumer_hook_binding_mismatch_is_detection_failure_with_exit_zero` | 80 / — | KEEP | `tests/cli_runtime/test_runtime_handoff.py::TestRuntimeHandoff::test_consumer_hook_binding_mismatch_is_detection_failure_with_exit_zero` | S4 |
| TI-0091 | `tests/cli_runtime/test_runtime_handoff.py::TestProviderLifecycleHandoff::test_t04_terminal_handoff_preserves_symlink_target_for_external_admission` | 117 / — | KEEP | `tests/cli_runtime/test_runtime_handoff.py::TestRuntimeHandoff::test_external_installer_handoff_preserves_symlink_target` | S4 |
| TI-0092 | `tests/cli_runtime/test_runtime_handoff.py::TestProviderLifecycleHandoff::test_t01_relative_lifecycle_targets_use_invoking_cwd_and_preserve_symlink_text` | 152 / — | KEEP | `tests/cli_runtime/test_runtime_handoff.py::TestRuntimeHandoff::test_relative_update_and_uninstall_targets_use_invoking_cwd_and_preserve_symlink_text` | S4 |
| TI-0093 | `tests/cli_runtime/test_runtime_handoff.py::TestProviderLifecycleHandoff::test_t04_git_write_helper_cannot_be_shadowed_by_consumer_module` | 193 / — | REWRITE | `tests/cli_runtime/test_runtime_handoff.py::TestRuntimeHandoff::test_bound_cwd_git_helper_cannot_be_shadowed_by_consumer_module` | S1 |
| TI-0094 | `tests/cli_runtime/test_worktree_lifecycle_coordination.py::TestWorktreeLifecycleCoordination::test_t11_worktree_b_create_remove_and_make_handoff_are_inode_bound` | 18 / — | KEEP | `tests/cli_runtime/test_worktree_lifecycle_coordination.py::TestWorktreeSafetyCoordination::test_worktree_create_remove_and_consumer_handoff_are_inode_bound` | S4 |
| TI-0095 | `tests/cli_runtime/test_worktree_lifecycle_coordination.py::TestWorktreeLifecycleCoordination::test_t11_cross_filesystem_worktree_admission_is_rejected_before_git_mutation` | 84 / — | KEEP | `tests/cli_runtime/test_worktree_lifecycle_coordination.py::TestWorktreeSafetyCoordination::test_cross_filesystem_worktree_admission_is_rejected_before_git_mutation` | S4 |
| TI-0096 | `tests/cli_runtime/test_worktree_lifecycle_coordination.py::TestWorktreeLifecycleCoordination::test_t11_original_worktree_inode_is_preserved_when_git_leaves_it` | 102 / — | KEEP | `tests/cli_runtime/test_worktree_lifecycle_coordination.py::TestWorktreeSafetyCoordination::test_original_worktree_inode_is_preserved_when_git_leaves_it` | S4 |
| TI-0097 | `tests/cli_runtime/test_worktree_lifecycle_coordination.py::TestWorktreeLifecycleCoordination::test_t11_worktree_remove_reports_busy_target_before_git_mutation` | 160 / — | KEEP | `tests/cli_runtime/test_worktree_lifecycle_coordination.py::TestWorktreeSafetyCoordination::test_worktree_remove_reports_busy_target_before_git_mutation` | S4 |
| TI-0098 | `tests/cli_runtime/test_worktree.py::TestCliWorktree::test_nonlocking_hook_fd_rejects_replacement_of_locked_worktree` | 93 / — | KEEP | `tests/cli_runtime/test_worktree.py::TestCliWorktree::test_nonlocking_hook_fd_rejects_replacement_of_locked_worktree` | S6 |
| TI-0099 | `tests/cli_runtime/test_worktree.py::TestCliWorktree::test_materializer_rejects_foreign_existing_descendant_directory` | 473 / — | KEEP | `tests/cli_runtime/test_worktree.py::TestCliWorktree::test_materializer_rejects_foreign_existing_descendant_directory` | S6 |
| TI-0100 | `tests/cli_runtime/test_worktree.py::TestCliWorktree::test_materialize_worktree_passes_source_lease_to_read_tree_helper` | 721 / — | REWRITE | `tests/cli_runtime/test_worktree.py::TestCliWorktree::test_materialize_worktree_runs_read_tree_in_target_bound_cwd_without_source_lease` | S1 |
| I405-NEW-001 | `tests/cli_runtime/test_generation_checkout.py::TestCheckoutSafety::test_issue_start_accepts_clean_repo_without_provider_capability_gate[executable-hook]` | new / executable-hook | NEW | `tests/cli_runtime/test_generation_checkout.py::TestCheckoutSafety::test_issue_start_accepts_clean_repo_without_provider_capability_gate[executable-hook]` | S1 |
| I405-NEW-002 | `tests/cli_runtime/test_generation_checkout.py::TestCheckoutSafety::test_issue_start_accepts_clean_repo_without_provider_capability_gate[fsmonitor]` | new / fsmonitor | NEW | `tests/cli_runtime/test_generation_checkout.py::TestCheckoutSafety::test_issue_start_accepts_clean_repo_without_provider_capability_gate[fsmonitor]` | S1 |
| I405-NEW-003 | `tests/cli_runtime/test_generation_checkout.py::TestCheckoutSafety::test_issue_start_accepts_clean_repo_without_provider_capability_gate[diff-attribute]` | new / diff-attribute | NEW | `tests/cli_runtime/test_generation_checkout.py::TestCheckoutSafety::test_issue_start_accepts_clean_repo_without_provider_capability_gate[diff-attribute]` | S1 |
| I405-NEW-004 | `tests/cli_runtime/test_generation_checkout.py::TestCheckoutSafety::test_issue_start_accepts_clean_repo_without_provider_capability_gate[merge-attribute]` | new / merge-attribute | NEW | `tests/cli_runtime/test_generation_checkout.py::TestCheckoutSafety::test_issue_start_accepts_clean_repo_without_provider_capability_gate[merge-attribute]` | S1 |
| I405-NEW-005 | `tests/cli_runtime/test_generation_checkout.py::TestCheckoutSafety::test_issue_start_accepts_clean_repo_without_provider_capability_gate[sparse-checkout]` | new / sparse-checkout | NEW | `tests/cli_runtime/test_generation_checkout.py::TestCheckoutSafety::test_issue_start_accepts_clean_repo_without_provider_capability_gate[sparse-checkout]` | S1 |
| I405-NEW-006 | `tests/cli_runtime/test_generation_checkout.py::TestCheckoutSafety::test_issue_start_rejects_dirty_worktree_before_checkout` | new / — | NEW | `tests/cli_runtime/test_generation_checkout.py::TestCheckoutSafety::test_issue_start_rejects_dirty_worktree_before_checkout` | S1 |

## support fixture / helper処置の完全一覧

変更対象だけでなくKEEPするsetup optimizationも列挙します。provider機構と構造が似ていることだけを理由に、setup cacheやcopy-on-write helperを削除しません。

| ID | current exact support symbol | line | 処置 | successor / fixed action | 理由 |
|---|---|---|---|---|---|
| TI-0101 | `tests/unit/infra/conftest.py::_SETUP_ONLY_PREFIXES` | 12-17 | REWRITE | `tests/unit/infra/conftest.py::_reuse_infra_init_result` | `test_recognized_reconciliation_`、`test_uninstall_`、`test_update_`は現行test_init_update.pyのtest名に実在しないdead prefix。 |
| TI-0102 | `tests/unit/infra/conftest.py::_clone_tree_contents` | 20-31 | KEEP | `_clone_tree_contents` | production provider lifecycleではなくtest setup cost削減。 |
| TI-0103 | `tests/unit/infra/conftest.py::_infra_init_template` | 34-39 | KEEP | `_infra_init_template` | 対象testがinit自体を観測しない場合のsetup。 |
| TI-0104 | `tests/unit/infra/conftest.py::_reuse_infra_init_result` | 42-65 | KEEP | `_reuse_infra_init_result` | fault/cutover testへ適用されない現行条件を保持。 |
| TI-0105 | `tests/cli_runtime/conftest.py::_TEMPLATE_MODULES` | 24-42 | KEEP | `_TEMPLATE_MODULES` | init実装を観測しないmoduleだけを対象にする。 |
| TI-0106 | `tests/cli_runtime/conftest.py::_DISTRIBUTION_SETUP_OPERATIONS` | 44-59 | DELETE | `_DISTRIBUTION_CUTOVER_MODULE`を含むspecial branch全体を削除する。 | 現行8 node名にupdate/uninstall/recognizedがなく到達しない。 |
| TI-0107 | `tests/cli_runtime/conftest.py::_clone_tree_contents / _fresh_init_template / _reuse_fresh_init_result` | 62-117 | KEEP | `_clone_tree_contents / _fresh_init_template / _reuse_fresh_init_result` | 一般command testのsetup costを削減し、cutover/security testはreal initへ残す。 |
| TI-0108 | `tests/cli_runtime/harness.py::_EXPECTED_MANAGED_SKILL_NAMES` | 33-36 | KEEP | `_EXPECTED_MANAGED_SKILL_NAMES` | 現行2skillのpositive allowlist。 |
| TI-0109 | `tests/cli_runtime/harness.py::_DELETED_ROLE_SKILL_NAMES` | 37-59 | DELETE | 削除。 | current exact catalog/assertと重複し、旧名称を恒久固定する。 |
| TI-0110 | `tests/cli_runtime/harness.py::_assert_managed_skills_installed` | 560-576 | REWRITE | `tests/cli_runtime/harness.py::CliRuntimeHarness._assert_managed_skills_installed` | positive exact setは保持し、旧名称ごとのloopを削除。 |
| TI-0111 | `tests/unit/infra/test_init_update.py::_managed_tree_bytes` | 52-62 | REWRITE | `tests/unit/infra/test_init_update.py::_managed_tree_bytes` | `.spec-dock-provider-slot.json`だけを除外する旧例外が再混入を隠し得る。 |

## repository-wide test surfaceの群別処置

focused node以外の全repository test surfaceは、次の群単位で棚卸しします。KEEP群ではproduction API縮退に伴うmock/adapter修正だけを許容し、一般behaviorを失いません。HISTORICALはexact target treeに存在しないため再導入しません。

| ID | repository test surface | 処置 | current contract / reason |
|---|---|---|---|
| TI-0112 | `tests/cli_runtime/test_active.py; tests/cli_runtime/test_artifact_import_file.py; tests/cli_runtime/test_artifact_import_s04.py; tests/cli_runtime/test_close.py; tests/cli_runtime/test_delete.py; tests/cli_runtime/test_deps.py; tests/cli_runtime/test_doctor.py; tests/cli_runtime/test_import.py; tests/cli_runtime/test_issue_lifecycle.py; tests/cli_runtime/test_new.py; tests/cli_runtime/test_post_mutation_sync_s01.py; tests/cli_runtime/test_storage_core_cli.py; tests/cli_runtime/test_sync.py; tests/cli_runtime/test_validate.py; tests/cli_runtime/test_workbench.py; tests/cli_runtime/test_wrappers.py` | KEEP | active/import/delete/deps/sync/validate/artifact/issue lifecycle — F001のprovider capability symbolsを直接所有せず、現行Storage Core/Authoring Kitの一般機能を検証する。adapter変更に伴うfixture修正だけ行い、behaviorは保持。 |
| TI-0113 | `tests/cli_runtime/test_runtime_active_s05.py; tests/cli_runtime/test_runtime_active_s06.py; tests/cli_runtime/test_runtime_close_s12.py; tests/cli_runtime/test_runtime_delete_s13.py; tests/cli_runtime/test_runtime_deps_s04.py; tests/cli_runtime/test_runtime_doctor_s04.py; tests/cli_runtime/test_runtime_import_s10.py; tests/cli_runtime/test_runtime_shell_s11.py; tests/cli_runtime/test_runtime_validate_s02.py` | KEEP | runtime layer contracts and regression observers — 旧番号を含むものがあるが、現行command/application/infra/presentation責務を守る一般test。provider generation call pathが確認されたnodeは別表へ抽出済み。 |
| TI-0114 | `tests/unit/application/**` | KEEP | application use cases — data/application contractを検証。provider lifecycle engine撤去とは独立。 |
| TI-0115 | `tests/unit/cli/**` | KEEP | CLI parser and smoke — 公開parser/CLI基本動作。 |
| TI-0116 | `tests/unit/commands/**` | KEEP | thin command wrappers — current command layer。 |
| TI-0117 | `tests/unit/domain/**` | KEEP | domain ids/models/deps/tree/naming — 固定directory installerとは独立したdomain contract。 |
| TI-0118 | `tests/unit/infra/* except conftest.py, test_directory_installation.py, test_init_update.py` | KEEP | active store, artifact publisher, workbench opacity, template scaffolder, deps reader — 利用者dataとruntime infraの一般機能。旧provider engine fileはcurrent treeから削除済み。 |
| TI-0119 | `tests/unit/presentation/**` | KEEP | text/JSON rendering — current output contract。 |
| TI-0120 | `tests/integration/**` | KEEP | package artifact parity, installed runtime, platform probes — exact package/runtime配布を検証。旧provider marker/journal/lease語のcurrent assertionは確認されていない。 |
| TI-0121 | `tests/unit/test_discovery.py; tests/integration/test_discovery.py; tests/unit/test_static_analysis_script.py` | KEEP | test discovery and lint runner — pytest discoveryとstatic analysis scriptの一般品質gate。 |
| TI-0122 | `tests/unit/infra/test_managed_distribution.py` | HISTORICAL | old per-file plan/journal/reconciliation engine suite — PR #404でcurrent treeから撤去済み。旧artifact内の言及はhistoryであり再導入義務ではない。 |
| TI-0123 | `tests/unit/test_full_regression_baseline.py` | HISTORICAL | old regression ledger/baseline evaluator suite — PR #404でcurrent treeから撤去済み。旧artifact内の言及はhistoryであり再導入義務ではない。 |
| TI-0124 | `tests/unit/test_provider_test_lanes.py` | HISTORICAL | old policy skip/provider lanes suite — PR #404でcurrent treeから撤去済み。旧artifact内の言及はhistoryであり再導入義務ではない。 |
| TI-0125 | `tests/conftest.py` | HISTORICAL | old full-regression policy collection hooks — PR #404でcurrent treeから撤去済み。旧artifact内の言及はhistoryであり再導入義務ではない。 |
| I405-GROUP-001 | `manual-tests/README.md` | KEEP | manual testing reference documentation — verified treeではREADMEだけであり、provider generation/shared leaseのactive test implementationを所有しない。 |

## 検証の区分

- **静的網羅**: exact tree/search/AST/test inventory。実行passではありません。
- **focused dynamic**: 指定file/nodeだけの実行。
- **full dynamic**: `uv run pytest`。
- **platform dynamic**: GitHub Actions Ubuntu/macOS。
- **browser dynamic**: attached validatorによるHTML DOM/SVG独立検査。
- **review**: exact integrated diffへの独立判定。

区分をReportで混同しません。

## Git実行とcheckpointの補足

各Gitコマンドは一回のtool callに一つだけ実行します。commit前にbranch・HEAD・status・identityを確認し、明示pathだけstageしてstaged diffを確認した後、`git-commit`スキルの`commit-codex -a`を使います。本書のmessageは候補でありskillの生成結果を優先します。revert・stash・push・PR作成は現在のユーザー認可と適用ルールを確認し、未認可のhistory/remote変更を本書だけで実施しません。S1のRed-only commitは行わず、S1〜S3の変更と必要検証を一つのworking checkpointにまとめます。

## rollback / forward recovery

### runtime source

- CP2を単位にrevertします。
- typesだけ、helperだけ、consumerだけを部分revertしません。
- rollback後はprovider source focused testsを実行し、dogfoodを外部installerで再同期します。

### installer test

- testがcurrent implementationでGreenならProduct source変更なし。
- failして契約bugが確認された場合だけ`installer.py`を最小修正し、testと同じCPへ含めます。
- update実行中failureは自動rollbackせず、原因修正後に外部installerを再実行します。

### docs/dogfood

- provider sourceを正本としてrevertし、`uvx --no-cache --from . spec-dock update .`でmirrorを再生成します。
- protected data diffが出た場合は自動cleanupせず停止し、元inode/file内容を保存して調査します。

## stop / escalation条件

即時停止:

- repository/branch/active Issueが入口条件と不一致
- 予期しないdata path mutation
- target inode safetyまたはentrypoint-last regression
- credential/private contentがstdout/stderrへ現れる
- testを削除しなければsecurity boundaryを維持できない
- public CLI/schema/error code変更が必要
- historical ledger/sharder/qualification再導入が必要

owner判断へ昇格:

- cross-filesystem対応追加
- same-EUID adversary保証追加
- atomic installer/journal/rollback導入
- new Product feature/option
- irreversible data migration

通常のtest failure、lint error、名前変更、内部interface調整はowner判断ではなく本Plan内で修正します。

## exit / handoff

完了条件:

- AC-405-01〜12の証拠がIssue Reportへ記録済み。
- F001〜F009がcurrent source/test/docsで解消。
- old provider mechanism active-term scan 0。
- full normal quality pathとplatform jobが実測Green。
- independent review blocking 0。
- merge-ready PR作成済み。
- human merge未実行で停止。

残余リスク:

- installerは意図的にnontransactionalであり、途中混在は外部再実行でforward recoveryします。
- Git native hook/config failureはprovider gate撤去後も起こり得ます。
- same-EUID非協調actorとcross-filesystem worktreeは新保証を追加しません。

実装担当向けの限定補助は[artifacts/20260920t055027z-luna-max-handoff.md](artifacts/20260920t055027z-luna-max-handoff.md)、人間向け説明は[artifacts/cleanup-guide.html](artifacts/cleanup-guide.html)、test処置のmachine-readable正本は[artifacts/test-disposition.csv](artifacts/test-disposition.csv)です。
