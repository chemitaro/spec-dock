---
種別: 実装計画書（Issue）
ID: "iss-00370"
タイトル: "Managed Distribution Deprovision"
関連GitHub: ["#370"]
状態: "planned"
最終更新: "2026-08-25"
依存: ["requirement.md", "design.md"]
親: ["epic-00365", "init-local-00003"]
---

# iss-00370 Managed Distribution Deprovision — 実装計画

詳細: [Issue Plan Guide](../../../../../../docs/authoring/issue-plan.md)

## Planning Level

**selected level: `critical`**

本 Issue は、利用者repository内のmanaged fileとdirectoryを不可逆に削除するpublic operationを変更する。誤ったownership判定、root/parent rebind、unknown childの見落とし、journal authorityの混同、legacy markerの推測変換は、spec historyまたは利用者所有contentの消失へ直結する。mutation開始後はwhole-operation rollbackを保証せず、partial stateをsame-plan forward recoveryで扱うため、失敗時の回復も容易ではない。public JSON schema version 1、text、exit code、retry guidanceを維持する必要もあり、filesystem safetyとcompatibilityの双方に高いblast radiusがある。

### protected data

- `spec-dock/initiatives/**` のspec history、Artifact、Discussion、ADR、metadata、empty directory
- `spec-dock/.workbench/**` のknown preserved payload
- managed root内に存在するunknown、modified、user-owned entry
- cleanup boundary外のrepository content
- symlinkが指すrepository外target
- partial failure後の`.distribution-retry.json`、`.distribution-journal.json`、private stage/quarantine evidence
- Issue 371が所有するexplicit purge authority

### threat / failure model

- pathnameまたはmanaged root membershipだけからownershipを推測する
- assessment後にroot、parent、target、directory child、provider sourceが置換される
- same-content別inode、hardlink、symlink、special fileをownedとして削除する
- safe actionだけを部分適用し、後からblockerが発見される
- legacy `.uninstall-retry.json` へcurrent invocationのroot/mode/planを捏造する
- deprovision journalを`--remove-specs`で再開しauthorityを昇格する
- guard/journal cleanup後にfallible directory cleanupを実行する
- JSON/text diagnosticへabsolute path、file content、credentialを漏らす

### blast radius

対象は一つのtarget rootだが、managed roots、generated state、root shortcut、external installed assets、preservation rootsへ跨る。CLI adapter、domain model、journal protocol、filesystem kernel、tests、shipped docsを同じchange setで変更する。runtime feature flagまたはdual writerを置かずhard cutoverするため、candidateがreleaseされる前のverification gateが唯一のrollout gateとなる。

### critical levelを維持する条件

本 Issueは実装中に`strict`へ下げない。次の条件が一件でも成立した場合は、実装を継続せずDecision Gateで停止する。

1. ownership sourceなしで削除対象を追加しなければpublic behaviorを成立させられない。
2. `spec-dock/initiatives`または`.workbench`のexact preservationを証明できない。
3. current journal schema 1 / protocol 2でdeprovision pre/postconditionをstrictに表現できない。
4. legacy markerを自動変換しなければdefault/keep routeをcut overできない。
5. `--remove-specs` compatibility routeをdeprovision intentへ接続しなければparser/output contractを維持できない。
6. existing descriptor-bound helperだけではunknown replacementを保持できず、pathname recursive deletionへ戻る必要がある。
7. LinuxまたはDarwinでrequired no-follow/rmdir semanticsをwrite前に検出できない。
8. public schema version 1のfield meaningを変更しなければtyped resultをmappingできない。

## 実装担当と操作境界

実装subagentは **coder / GPT-5.6 Luna / reasoning Max** とする。coderは本Planのstep順にred test、production change、focused verificationを一件ずつ進める。RequirementまたはDesignで固定したProduct、Policy、Security、authority、wire compatibility、architecture判断を再解釈しない。

coderのownership:

- listed source/test/docsのcandidate変更
- red testの追加または旧期待の置換
- focused commandの実行と結果記録
- failure時のrepository-relative evidence整理

coderの禁止事項:

- `--remove-specs` purgeの実装またはbehavior変更
- legacy markerへのfield追加、推測変換、自動削除
- public flag、JSON schema version、top-level/action/summary key setの変更
- unknown/modified contentをmanaged root membershipだけで削除する実装
- generic recursive deletion framework、新dependency、Windows support、Full Regression repair
- `.meta.json`、node ID、slug、Issue stateの手編集
- runtime feature flag、hidden fallback、default/keep dual writer
- commit、push、PR、merge、release、Issue完了の最終判断。これらはorchestratorまたは利用者のworkflowが担う
- Decision Gateに該当する事項を仮定で埋めること

## 実装開始時の正本と既実施evidence

実装事実の基準は次のexact revisionである。

- repository: `chemitaro/spec-dock`
- branch: `iss-00370-managed-distribution-deprovision`
- exact SHA: `fc02e1215d2b9e056a2c18bd1411fe489efdf2f2`

開始前に同じSHAまたはその明示的descendantであることを確認し、別branch、default branch、別revisionのsymbolを黙って採用しない。

既に成立したimplementation seam:

- `WorkspaceAssessment`
- `ExecutableMutationPlan`
- `OperationJournalStore`
- schema-2 forward guard
- schema version 1 / protocol version 2の`OperationJournal`
- `apply_distribution_plan()`とdescriptor-bound helper群
- `execute_recognized_distribution()` / `execute_fresh_distribution()`
- `DistributionProcessResult`
- `build_distribution_plan(..., operation="uninstall")`

Issue 369 Reportのfocused/full-regression結果はIssue 369 candidateに対する既実施evidenceである。本Issue candidateのpassとして転記しない。本Planのcommandはすべて予定であり、実行結果はcandidate実装後のReportへ記録する。

## 変更対象

### primary production files

- `src/spec_dock/managed_distribution.py`
- `src/spec_dock/cli.py`

### primary tests

- `tests/unit/infra/test_managed_distribution.py`
- `tests/unit/infra/test_init_update.py`
- `tests/cli_runtime/test_distribution_cutover.py`

### public / shipped docs

- `README.md`
- `src/spec_dock/assets/spec_dock/docs/README.md`
- `spec-dock/docs/README.md`
- `src/spec_dock/assets/spec_dock/docs/migration.md`
- `spec-dock/docs/migration.md`

### read-only reference unless Decision Gate is raised

- `src/spec_dock/assets/managed_distribution.json`
- `tests/conftest.py`
- Issue 368 full-regression verifier/ledger/timing artifacts

`managed_distribution.json`へCurrent inventoryまたはpurge authorityを追加しない。current/historical exact ownership evidenceが不足しているpathを発見した場合、そのpathをpathname推測でownedにせずDecision Gateで停止する。test laneは現行`tests/conftest.py`の`fast` / `full_regression` contractを使用し、lane policy自体を本Issueで変更しない。

## Test inventoryとstable test IDs

実装stepとRequirementのtraceabilityに次のtest IDを使用する。実際のpytest function名は`test_i370_...` prefixで、このIDをdocstringまたはparameter IDへ保持する。

| Test ID | 固定する契約 | 主なfile |
|---|---|---|
| I370-T-CLI-001 | seven-row CLI matrix、parser、route owner、exit | `test_init_update.py`, `test_distribution_cutover.py` |
| I370-T-CHAR-001 | current JSON/text/action/summary field golden | `test_init_update.py` |
| I370-T-DRY-001 | default/keep dry-runの同一assessmentとzero-write | `test_init_update.py` |
| I370-T-DOM-001 | `deprovision` intent、`uninstall` mapping、action allowlist | `test_managed_distribution.py` |
| I370-T-OWN-001 | current/historical/generated/obsolete exact ownership inventory | `test_managed_distribution.py` |
| I370-T-TREE-001 | bounded traversal、complete classification、deterministic digest | `test_managed_distribution.py` |
| I370-T-PRES-001 | initiatives byte identity、empty dir、safe symlink、mode/link topology | `test_managed_distribution.py`, `test_init_update.py` |
| I370-T-PRES-002 | Workbenchとoutside sentinelのpreservation | `test_init_update.py`, `test_distribution_cutover.py` |
| I370-T-BLK-001 | unknown/modified childとmixed safe/unsafeのwhole-operation write zero | `test_init_update.py`, `test_distribution_cutover.py` |
| I370-T-ID-001 | regular/symlink/hardlink/special exact identity | `test_managed_distribution.py` |
| I370-T-RACE-001 | cooperating root-lock serializationとroot/parent/target/child/source rebind | `test_managed_distribution.py` |
| I370-T-PLAN-001 | executable plan completeness、canonical digest、forged grammar rejection | `test_managed_distribution.py` |
| I370-T-JRN-001 | guard purpose、intent、authority、schema/protocol、strict condition parser | `test_managed_distribution.py` |
| I370-T-KRN-001 | exact `prune`と`remove-empty-directory`、no recursion | `test_managed_distribution.py` |
| I370-T-NOOP-001 | already-absent no-op applyのprotocol metadata write zero | `test_init_update.py` |
| I370-T-REC-001 | partial failure、checkpoint、same-plan resume、crash windows | `test_managed_distribution.py`, `test_distribution_cutover.py` |
| I370-T-AUTH-001 | deprovision/purge authority non-switching | `test_managed_distribution.py`, `test_init_update.py` |
| I370-T-LEG-001 | legacy marker non-conversion、dual/malformed/copied marker | `test_managed_distribution.py`, `test_init_update.py` |
| I370-T-JSON-001 | schema v1、exactly-one stdout object、field mapping | `test_init_update.py` |
| I370-T-TEXT-001 | text section order、phase、exit、sanitization、shell-safe retry | `test_init_update.py` |
| I370-T-ABS-001 | default/keep legacy symbol/call-edge/fallback absence | `test_init_update.py`, `test_distribution_cutover.py` |
| I370-T-OPS-001 | bounded linear observation、determinism、capability fail-closed | `test_managed_distribution.py` |
| I370-T-DOC-001 | shipped/dogfood docs parityとnew recovery guidance | `test_init_update.py` |

## 実装順序

```text
P0 Characterization
 -> P1 Intent / grammar / authority
 -> P2 Bounded observation / preservation
 -> P3 Executable plan / journal condition
 -> P4 Descriptor-bound remove kernel
 -> P5 Read-only service / no-op
 -> P6 Journaled apply / recovery
 -> P7 CLI mapper / route split
 -> P8 Legacy marker fail-closed
 -> P9 Legacy call-edge removal / docs
 -> P10 Integrated verification / release gate
```

P0〜P4はpublic default/keep routeを切り替えない。P5でdry-runだけをnew assessmentへ接続し、P6のapply serviceが完成してからP7でdefault/keep applyを一度にhard cutoverする。P7完了後にlegacy fallbackを残さない。

## Step P0 — Current behavior characterizationとred-test inventory

### dependency

なし。production codeを変更する前に実施する。

### owned files

- `tests/unit/infra/test_managed_distribution.py`
- `tests/unit/infra/test_init_update.py`
- `tests/cli_runtime/test_distribution_cutover.py`

### red tests / characterization

1. `I370-T-CLI-001`として次のmatrixを固定する。
   - default dry-run
   - `--keep-specs` dry-run
   - `--remove-specs` dry-run
   - `--apply` without mode
   - both modes
   - `--apply --keep-specs`
   - `--apply --remove-specs`
2. `I370-T-CHAR-001`でcurrent schema version 1のtop-level/action/summary key、status、phase、last-completed、text section order、exit mappingをfixture化する。
3. existing keep behaviorから、initiatives、Workbench、outside sentinel、safe symlink、empty directoryのbefore snapshot helperを抽出する。
4. current source inspectionでdefault/keep routeが `_build_uninstall_plan()`、`_apply_uninstall_plan()`、`_verify_uninstall_postcondition()`、`_write_uninstall_retry_marker()`へ到達する事実をcharacterizationする。
5. 次の旧削除期待を安全契約のred testへ置換する。
   - `test_s70_uninstall_apply_removes_unproven_legacy_scaffold_entry_with_managed_root`
   - `test_s70_uninstall_apply_removes_modified_managed_scaffold_with_managed_root`
   - `test_s70_uninstall_apply_removes_unknown_scaffold_entry_with_managed_root`
6. 置換後の期待は「unknown/modified childを列挙し、owned siblingを含むoperation全体をwrite 0でblockする」とする。旧期待と新期待を併存させない。
7. `--remove-specs` testsはcurrent compatibility characterizationとして残し、expected output/actionを本Issueで書き換えない。
8. legacy `.uninstall-retry.json` marker-only dry-runのcurrent acceptance testは、本Issue target behaviorである`recovery_required`/exit 1のred testへ置換する。marker bytes/identity不変を同時にassertする。

### focused verification

```bash
uv run pytest -q tests/unit/infra/test_managed_distribution.py -k "uninstall or deprovision or i370"
uv run pytest -q --run-full-regression --full-regression-shard tests/unit/infra/test_init_update.py -k "uninstall or deprovision"
uv run pytest -q --run-full-regression --full-regression-shard tests/cli_runtime/test_distribution_cutover.py -k "uninstall or deprovision"
```

このstepではfuture red testsが失敗することを確認し、current characterizationだけがpassする。ordinary focused runでheavy testsがpolicy skipされた場合、そのskipをbehavior passとして扱わない。

### step exit

- current factとtarget contractが別test名で識別できる。
- public schema/text/exit goldenがfixtureとして存在する。
- unknown/modified managed-root deletionの旧期待が残っていない。
- production codeに差分がない。

## Step P1 — `deprovision` intent、action grammar、authority mapping

### dependency

P0完了。

### owned files / symbols

- `src/spec_dock/managed_distribution.py`
  - `JournaledDistributionIntent`
  - `DistributionActionName`
  - `_plan_operation_for_intent()`
  - `_DEPROVISION_DISTRIBUTION_ACTIONS`
  - `_intent_allows_distribution_action()`
  - `_DISTRIBUTION_DEPROVISION_JOURNAL_GUARD_PURPOSE`
  - `_DISTRIBUTION_JOURNAL_AUTHORITIES`
  - `_journal_authority_for_intent()`
  - `_journal_guard_purpose_for_intent()`
- `tests/unit/infra/test_managed_distribution.py`

### red tests first

- `I370-T-DOM-001`: `deprovision -> uninstall`だけが有効なplan-operation mapping。
- `I370-T-DOM-001`: deprovisionで許可されるactionが`prune`、`preserve`、`block`、`remove-empty-directory`だけ。
- `I370-T-DOM-001`: fresh allowlistが`create`、`adopt`、`preserve`、`block`、`ensure-directory`のまま。
- `I370-T-PLAN-001`: freshへ`prune`、deprovisionへ`create`/`upgrade`/`ensure-directory`を偽装したassessment/plan/journalを全mutation boundaryで拒否。
- `I370-T-JRN-001`: purpose/intent/authorityのforged pair、unknown purposeを拒否。
- `I370-T-AUTH-001`: deprovision typeにpurge intent/authorityを渡せない。

### implementation

1. `JournaledDistributionIntent`へ`"deprovision"`を追加する。
2. `DistributionOperation`の`"uninstall"`は維持する。
3. `DistributionActionName`へ`"remove-empty-directory"`を追加する。
4. assessment intentと`DistributionPlan.operation`の一致判定を`_plan_operation_for_intent()`経由へ変更する。
5. intentごとのallowlistをplan発行、journal再開検証、`apply_distribution_plan()`入口の三境界で共通使用する。
6. guard purposeとauthorityのexact mappingを追加し、文字列の独立指定を拒否する。
7. fresh/recognized serializer/parser fixtureがbyte/semantic互換を維持することを確認する。

### focused verification

```bash
uv run pytest -q tests/unit/infra/test_managed_distribution.py -k "i370 and (intent or grammar or authority or guard)"
uv run pytest -q tests/unit/infra/test_managed_distribution.py -k "fresh_action_grammar or forged_assessment_cannot_prune"
```

### step exit

- deprovision intentがtype、plan mapping、allowlist、guard、authorityへ一意に接続される。
- purgeを表現するfieldまたはbranchが追加されていない。
- existing fresh/recognized grammar testsが退行しない。

## Step P2 — Bounded tree observationとpreservation witness

### dependency

P1完了。

### owned files / symbols

- `src/spec_dock/managed_distribution.py`
  - `DistributionTreeEntryKind`
  - `DistributionTreeEntrySnapshot`
  - `DistributionDirectoryMutationSnapshot`
  - `DistributionPreservationWitness`
  - `DistributionDeprovisionContract`
  - bounded no-follow traversal helper
  - canonical child/tree digest helper
  - deprovision classification helper
  - `WorkspaceAssessment` extension
- `tests/unit/infra/test_managed_distribution.py`

### red tests first

- `I370-T-OWN-001`: Current/historical exact managed leaf、generated state、exact shortcut、proven obsolete、owned directoryだけがremoval candidate。
- `I370-T-TREE-001`: each bounded rootのchildを一度だけ完全列挙し、duplicate/unclassified entryを拒否。
- `I370-T-PRES-001`: nested initiatives treeのregular bytes、mode、safe symlink text、empty directory、child set、link topologyをwitness化。
- `I370-T-PRES-002`: `.workbench`とoutside sentinelがaction authorityに入らない。
- `I370-T-BLK-001`: managed root内unknown/modified child、unsafe name、enumeration errorがwhole-operation blocker。
- `I370-T-ID-001`: special file、multi-link regular、external symlink、unsafe parentでwitness/authorityを発行しない。
- `I370-T-OPS-001`: cleanup boundary外large treeのentry数を増やしてもobservation countが増えない。
- `I370-T-OPS-001`: randomized directory creation orderでもcanonical digest/action orderが同一。

### implementation

1. `DistributionDeprovisionContract`をphysical Current assets、historical manifest、scaffold roots、generated state、root shortcut、preserved rootsから構築する。
2. traversal rootをcontractのmanaged rootsとpreservation rootsへ限定する。repository root全体をscanしない。
3. child observationはheld directory fdと`follow_symlinks=False`を使用する。
4. regularはtype/device/inode/ctime/mode/link count/size/SHA-256、symlinkはno-follow identityとlink text、directoryはbindingとchild recordsを記録する。
5. special fileまたはunproven hardlinkはblockerにする。
6. managed root membershipだけではownershipを発行しない。各leafをCurrent/historical/generated/exact obsolete evidenceへ照合する。
7. managed directoryは全childがauthorized removalまたはexplicit preserveで完全分類できる場合だけ`remove-empty-directory`候補にする。
8. `spec-dock/initiatives`と存在する`.workbench`をnon-mutating `DistributionPreservationWitness`へ変換する。missing preservation rootもmissing identityとして固定する。
9. child/tree digestはDesignのcanonical field setとbyte orderで計算し、absolute path、wall clock、nonceを含めない。
10. blockerが一件でもあれば`ExecutableMutationPlan`発行前に停止する。

### focused verification

```bash
uv run pytest -q tests/unit/infra/test_managed_distribution.py -k "i370 and (tree or preserve or ownership or bounded or digest or hardlink or symlink or special)"
```

### step exit

- all removal/preservation/blocker pathがevidence sourceへtraceできる。
- unknown childを持つmanaged rootが削除候補にならない。
- initiatives/Workbench witnessがcompleteかつdeterministicである。
- bounded traversalが対象外treeへ入らない。

## Step P3 — Executable plan、digest、journal condition schema

### dependency

P2完了。

### owned files / symbols

- `src/spec_dock/managed_distribution.py`
  - `WorkspaceAssessment.directory_snapshots`
  - `WorkspaceAssessment.preservation_witnesses`
  - `ExecutableMutationPlan`同field
  - canonical contract/plan serialization
  - `_action_precondition_payload()`
  - `_action_postcondition_payload()`
  - journal parser/validator
  - `OperationJournalStore` initial journal/action construction
- `tests/unit/infra/test_managed_distribution.py`

### red tests first

- `I370-T-PLAN-001`: blocker、missing snapshot、duplicate path、dependency cycle、不完全parent chainからplanを発行できない。
- `I370-T-PLAN-001`: action permutation、child record permutation、preservation witness欠落でdigest mismatch。
- `I370-T-JRN-001`: deprovision journalがschema 1 / protocol 2を使用し、intent/authority/root/contract/planを保持する。
- `I370-T-JRN-001`: directory preconditionからbinding/child digest/dependencyを一fieldずつ欠落させてself-rehashしたjournalを拒否。
- `I370-T-JRN-001`: preservation witnessのentry/sha/mode/link textを変更してself-rehashしたjournalを拒否。
- `I370-T-AUTH-001`: deprovision journalへpurge path/action/authorityを挿入して拒否。

### implementation

1. assessmentのdirectory snapshotsとpreservation witnessesをexecutable planへimmutableにコピーする。
2. plan digestへintent、root、contract、ordered actions、full parent/target condition、directory child digest、preservation witness digest、action dependencyを含める。
3. leaf `prune` preconditionはexact observed identity、postconditionはabsentとする。already-absent targetはmissing pre/postでidempotentに表現する。
4. `remove-empty-directory` preconditionはexact directory binding、initial child digest、全child action dependency、runtime expected empty digestを持つ。
5. preserve recordはmutation handlerを持たず、pre/post witness exact一致を要求する。
6. journal top-level schema versionを1、protocolを2のまま維持し、deprovision condition shapeをprotocol-2 strict parserへ追加する。
7. fresh/recognized journal condition parserのexisting field contractを変更しない。
8. guard/journal serializationにabsolute path、source bytes、credentialを入れない。

### focused verification

```bash
uv run pytest -q tests/unit/infra/test_managed_distribution.py -k "i370 and (plan or digest or journal or condition or witness)"
```

### step exit

- plan digestから全mutation authorityとpreservation obligationを再構成できる。
- field omission/self-rehashでauthorityを拡張できない。
- journal schema/public schemaのversion bumpがない。

## Step P4 — Descriptor-bound `prune` / exact empty-directory kernel

### dependency

P3完了。

### owned files / symbols

- `src/spec_dock/managed_distribution.py`
  - existing exact regular/symlink removal helper reuse
  - `_remove_distribution_directory_if_bound()`
  - `apply_distribution_plan()` deprovision handlers
  - action ordering/dependency validation
- `tests/unit/infra/test_managed_distribution.py`

### red tests first

- `I370-T-KRN-001`: regular/symlink current exact leafをno-followでprune。
- `I370-T-KRN-001`: missing leafをalready-absentとしてtarget syscallなしでcheckpoint可能。
- `I370-T-KRN-001`: deepest-first child removal後にだけexact bound empty directoryをrmdir。
- `I370-T-KRN-001`: unknown empty directory、preserved directory、dependency未完了directoryを削除しない。
- `I370-T-RACE-001`: target appearance/replacement、same-content別inode、parent/root rebind、unknown child appearanceで次のmutationを停止。
- `I370-T-ID-001`: hardlink、external symlink、special fileを削除しない。
- `I370-T-BLK-001`: mixed planはkernelへ到達しない。
- `I370-T-ABS-001`: deprovision kernelにrecursive tree removal callback/call edgeがない。

### implementation

1. regular/symlink leaf removalはexisting descriptor-bound exact remove/quarantine pathを再利用する。CLI private remove helperを呼ばない。
2. `_remove_distribution_directory_if_bound()`をDesign signatureで追加する。
3. helperはroot/parent descriptor、visible/held device/inode/type、expected remaining child digest、parent/root identityをrmdir直前と直後に検証する。
4. helperにrecursionを持たせない。child removalはjournal action dependencyとして先に完了させる。
5. action orderをleaf `prune` deterministic path order、`remove-empty-directory` depth descending + path orderへ固定する。
6. deprovision intentからcreate/upgrade/ensure-directory handlerへ到達した場合はfilesystem observation前にprotocol errorとする。
7. unknown/replacement entryをcleanup authorityへ昇格しない。restorable quarantine transition以外でbest-effort unlinkしない。
8. Darwin/Linuxのexisting no-replace/exchange branchを維持し、Windows branchを追加しない。

### focused verification

```bash
uv run pytest -q tests/unit/infra/test_managed_distribution.py -k "i370 and (kernel or prune or remove_empty or rmdir or rebind or replacement)"
```

### step exit

- every deletion syscallがone journal actionとexact preconditionへ対応する。
- recursive deletionがproduction deprovision pathに存在しない。
- unknown child/replacementは削除されず、failure evidenceが残る。

## Step P5 — Deprovision serviceのdry-runとno-op apply

### dependency

P4完了。

### owned files / symbols

- `src/spec_dock/managed_distribution.py`
  - `execute_deprovision_distribution()`
  - deprovision assessment builder/wrapper
  - `DistributionProcessResult.status`への`planned`追加
  - no-op short-circuit
- `src/spec_dock/cli.py`
  - default/keep dry-runのthin dispatchだけを先行接続
- primary tests三file

### red tests first

- `I370-T-DRY-001`: defaultとkeep dry-runが同一action/reason/plan digestを返す。
- `I370-T-DRY-001`: guard/journal/legacy marker/stage/target/backup/versionのbefore/after完全一致。
- `I370-T-BLK-001`: dry-runはblocker inventoryを`planned`として表示するがmutation authorityを発行しない。
- `I370-T-NOOP-001`: recovery metadataなし、全removal target absent、witness validのapplyはguard/journal/stage/target syscall 0で`completed`。
- `I370-T-NOOP-001`: no-opでもpreservation witness mismatch/root rebindがあればcompletedにならない。
- `I370-T-OPS-001`: capability不足はfirst write前にstable error。

### implementation

1. `execute_deprovision_distribution(..., apply: bool)`を追加する。
2. specs modeをservice parameterにしない。serviceはkeep-only authorityで固定する。
3. `apply=False`はadmission、contract capture、full assessment、typed `planned` resultだけを返す。
4. dry-run blockerはaction/reasonへ含めるがjournalを作らない。malformed/unsupported eligibilityとrecovery metadataは別typed resultにする。
5. `apply=True`でblocker 0かつrecovery metadataなしの場合、mutating action countを評価する。
6. mutating action 0ならread-only post-assessmentを再実行し、root/parent/preservation witness一致後に`completed`を返す。forward guard、journal、legacy marker、stageを作らない。
7. mutating actionありの場合はP6のjournaled pathへ渡す。このstepではpublic apply routeをまだcut overしない。
8. default/keep dry-runだけをnew serviceへ接続し、`--remove-specs` dry-runはexisting compatibility branchに残す。

### focused verification

```bash
uv run pytest -q tests/unit/infra/test_managed_distribution.py -k "i370 and (dry or noop or planned or capability)"
uv run pytest -q --run-full-regression --full-regression-shard tests/unit/infra/test_init_update.py -k "i370 and (dry or noop)"
```

### step exit

- default/keep dry-runがnew assessmentをend-to-end使用する。
- dry-runとno-op applyがzero-write contractを満たす。
- apply mutation routeはまだlegacy public pathへ切り替わっていない。

## Step P6 — Guard、journal、apply、partial failure、forward recovery

### dependency

P5完了。

### owned files / symbols

- `src/spec_dock/managed_distribution.py`
  - `execute_deprovision_distribution()` apply branch
  - `OperationJournalStore` deprovision guard/journal admission
  - action checkpoint/post-assessment/finalization
  - deprovision recovery result mapping inputs
- `tests/unit/infra/test_managed_distribution.py`
- `tests/cli_runtime/test_distribution_cutover.py`

### red tests first

- `I370-T-JRN-001`: guardがjournalより先、first target mutationより前にdurable publishされる。
- `I370-T-REC-001`: guard publish failure、journal publish failureでtarget write 0。
- `I370-T-REC-001`: leaf publish直後、checkpoint前、directory rmdir直後、verifying、completed、guard cleanup、journal cleanupの各crash window。
- `I370-T-REC-001`: pending/published/verified checkpointの単調進行とsame-plan convergence。
- `I370-T-REC-001`: guard-only、guard+journal、completed+guard、completed-onlyを区別しtarget actionを重複実行しない。
- `I370-T-RACE-001`: source/root/parent/target/unknown child/preservation witness mutationで追加action停止。
- `I370-T-AUTH-001`: root/intent/authority/contract/plan/protocol mismatch、purge invocationでcheckpoint 0。
- `I370-T-JSON-001`: partial resultへapplied/pending/failed relative pathsだけを渡す。

### implementation

1. existing deprovision recovery metadataをread-only admissionし、normal new operationとresumeを分岐する。
2. mutating new planではschema-2 guardを`purpose="deprovision-journal-forward-only"`、operation/intent=`deprovision`、authority=`managed-distribution-deprovision`へ束縛してdurable publishする。
3. guard predecessor identityを再検証してprotocol-2 journalをprepare/bindする。
4. first mutation直前にprovider source、root、parent、all preservation witnesses、bounded child setを再検証する。
5. leaf `prune`、deepest-first `remove-empty-directory`を実行し、各actionを`pending -> published`へ進める。
6. action failureではjournal/guardを保持し、already completed actionをrollbackしない。
7. post-assessmentでremoved path absence、preservation witness、root/parent binding、unknown closed set、action coverageを検証する。
8.全actionを`verified`、journal statusを`completed`へ進める。
9. forward guardをexact cleanupし、その後completed journalをexact cleanupする。
10. guard/journal cleanup後にworkspace rmdir/unlinkを行わない。
11. completed cleanup failureはtarget actionを再実行せずcleanup-only retryにする。
12. mismatch/ambiguous stateではjournal、guard、stage、unknown entryを推測修復しない。

### focused verification

```bash
uv run pytest -q tests/unit/infra/test_managed_distribution.py -k "i370 and (journal or recovery or checkpoint or crash or partial or postcondition)"
uv run pytest -q --run-full-regression --full-regression-shard tests/cli_runtime/test_distribution_cutover.py -k "i370 and (partial or retry or marker or journal)"
```

### step exit

- mutating applyはcommon guard/journal/kernel/post-assessmentをend-to-end使用する。
- crash-window matrixがsame-plan retryへ収束する。
- mismatchとauthority switchがwrite 0で停止する。
- terminal cleanup後のfallible workspace mutationがない。

## Step P7 — CLI adapter、public mapper、default/keep hard cutover

### dependency

P6完了。

### owned files / symbols

- `src/spec_dock/cli.py`
  - `_run_uninstall_unlocked()` route split
  - `_UninstallActionView`
  - `_uninstall_payload()` pure compatibility mapper
  - `_render_uninstall_text()`
  - retry command builder
  - status/phase/last-completed/exit mapping
- primary tests三file

### red tests first

- `I370-T-CLI-001`: seven-row matrixを全て再実行。
- `I370-T-JSON-001`: planned/completed/blocked/recovery/errorのschema v1 golden、exactly one stdout object。
- `I370-T-TEXT-001`: section order、phase、last-completed、summary/action mapping、exit。
- `I370-T-TEXT-001`: absolute path、source bytes、credential注入時のsanitization。
- `I370-T-TEXT-001`: space/leading hyphenを含むtargetのshell-safe keep-only retry。
- `I370-T-AUTH-001`: deprovision resultから`--remove-specs` retryを生成しない。
- `I370-T-ABS-001`: default/keep branchがlegacy plan/apply/postverify/marker writerを呼ばない。

### implementation

1. parserとmutually-exclusive groupを変更しない。
2. `_run_uninstall_unlocked()`を明示的に二routeへ分ける。
   - `args.remove_specs is False`: Issue 370 deprovision adapter
   - `args.remove_specs is True`: Issue 371 compatibility adapter
3. default dry-runと`--keep-specs` dry-runをsame deprovision service `apply=False`へ送る。
4. `--apply --keep-specs`をsame service `apply=True`へ送る。
5. apply without modeはservice entry前にexisting parser/business error contractでexit 2。
6. `_UninstallAction`をdefault/keep mutation authorityに使わず、presentation用`_UninstallActionView`だけをtyped resultから生成する。
7. internal mappingを固定する。
   - `planned -> planned / exit 0`
   - `completed -> completed / exit 0`
   - `blocked -> blocked / exit 1`
   - `recovery_required -> partial_failure / exit 1`
   - eligibility/preflight error -> error / exit 2
8. top-level/action/summary field set、types、nullabilityを維持する。
9. public `marker-written`等のphase labelはdurable recovery evidenceの意味としてmappingし、legacy marker writerへの依存を持たせない。
10. stdoutはJSON modeでexactly one object、text modeでexisting section orderとする。
11. retry commandはsame target + `--apply --keep-specs`だけを生成し、legacy ambiguous markerでは`null`または既存field contractに対応するno-command表現とmanual guidanceを返す。
12. `--remove-specs` branchのpayload/exit/action semanticsを変更しない。

### focused verification

```bash
uv run pytest -q --run-full-regression --full-regression-shard tests/unit/infra/test_init_update.py -k "i370 and (uninstall or json or text or retry or parser)"
uv run pytest -q --run-full-regression --full-regression-shard tests/cli_runtime/test_distribution_cutover.py -k "i370 and (uninstall or deprovision or cutover)"
```

### step exit

- default/keep public flowがnew serviceだけを使用する。
- remove-specs compatibility routeと双方向call edgeがない。
- public JSON/text/exit/sanitization goldenが一致する。
- hidden fallbackまたはruntime toggleがない。

## Step P8 — Legacy `.uninstall-retry.json` fail-closed admission

### dependency

P7完了。

### owned files / symbols

- `src/spec_dock/managed_distribution.py`
  - existing `_read_uninstall_retry_marker_for_admission()`のread-only evidence拡張
  - admission reason/result mapping
- `src/spec_dock/cli.py`
  - legacy manual recovery guidance mapping
- primary tests三file

### red tests first

- `I370-T-LEG-001`: exact current three-field marker-only stateを自動変換せず、bytes/inode/target不変。
- `I370-T-LEG-001`:別rootからcopyしたsame bytes markerも同じ結果。
- `I370-T-LEG-001`: malformed、symlink、hardlink、special markerをwrite前に拒否。
- `I370-T-LEG-001`: legacy marker + schema-2 guard/journalのdual stateを変更せず拒否。
- `I370-T-AUTH-001`: markerがkeep/remove modeを証明しないため、current invocationのflagからauthorityを補わない。
- `I370-T-TEXT-001`: `legacy-marker-unconvertible`とplan/postcondition mismatchのguidanceを区別し、legacy markerにはunsafe retry commandを出さない。

### implementation

1. legacy markerをregular single-link no-follow evidenceとして読むが、root/intent/authority/plan/checkpointへ変換しない。
2. valid marker-onlyまたはcopied marker存在時、default/keep dry-run/applyはreason=`legacy-marker-unconvertible`のread-only `recovery_required`を返し、public `partial_failure`/exit 1へmappingする。
3. marker fileのbytes、identity、mode、link topologyを変更しない。
4. `.distribution-retry.json`または`.distribution-journal.json`と併存する場合はdual recovery stateとして停止する。
5. malformed/symlink/hardlink/special markerはreason=`legacy-marker-invalid`のeligibility `error`を返し、public exit 2へmappingする。dual recovery stateはreason=`dual-recovery-state`の`recovery_required`を返し、public exit 1へmappingする。
6. manual guidanceは「legacy installerが作成した状態のroot/mode/checkpointを自動証明できない」ことを示し、delete/rename/convert commandを自動提示しない。
7. remove-specs compatibility routeがlegacy markerを現行契約で扱う部分はIssue 371 ownerとして残す。ただしdeprovision guard/journalがある状態ではcheckpointを進めない。

### focused verification

```bash
uv run pytest -q tests/unit/infra/test_managed_distribution.py -k "i370 and legacy"
uv run pytest -q --run-full-regression --full-regression-shard tests/unit/infra/test_init_update.py -k "i370 and legacy"
```

### step exit

- current markerのautomatic conversion pathが0。
- copied/malformed/dual markerでevidenceとtargetが不変。
- deprovision/purge authorityがmarkerから復元されない。

## Step P9 — Legacy deprovision call-edge removalとdocs更新

### dependency

P8完了。

### owned files / symbols

- `src/spec_dock/cli.py`
- primary tests三file
- public / shipped docs五file

### red tests first

- `I370-T-ABS-001`: default/keep dispatch sourceに次のcall edgeがない。
  - `_build_uninstall_plan(`
  - `_apply_uninstall_plan(`
  - `_verify_uninstall_postcondition(`
  - `_write_uninstall_retry_marker(`
  - `_remove_uninstall_tree_fd(`
  - `_remove_uninstall_path(`
  - `_cleanup_empty_uninstall_dirs(`
- `I370-T-ABS-001`: `execute_deprovision_distribution(`がdefault/keep routeのsingle service call。
- `I370-T-ABS-001`: remove-specs compatibility routeだけがD4-owned legacy helperを参照する。shared helperの削除はcall graphでunusedを証明した場合だけ行う。
- `I370-T-DOC-001`: provider docsとdogfood docsのbytes/meaning parity。
- `I370-T-DOC-001`: docsがnew journal、legacy marker fail-closed、keep/remove owner boundary、same-plan retryを記載。

### implementation

1. default/keep routeからlegacy plan/apply/postverify/marker/remove helperへのcall edgeを物理削除する。
2. helper自体がremove-specs compatibility routeからもunusedなら削除する。D4-owned callerが残るhelperは名前とcommentでcompatibility ownershipを明示し、本Issue serviceから到達不能にする。
3. `_UninstallTargetIdentity` / `_UninstallAction`のうちdefault/keep mutation authorityとして不要になったfield/typeを除去する。remove-specs routeが使用する部分はD4 handoff一覧に残す。
4. source/AST absence testでstring commentではなくactual function source/call dependencyを確認する。
5. READMEとshipped/dogfood docsを次へ更新する。
   - default/keep dry-runはread-only assessment
   - apply keepは`.distribution-retry.json` schema-2 guard + `.distribution-journal.json`
   - same root/intent/authority/contract/plan/protocolでforward recovery
   - legacy `.uninstall-retry.json`は自動変換しない
   - `--remove-specs`はseparate explicit authority / Issue 371 compatibility owner
   - unknown/modified contentとspec historyを保持
6. docsに未実行testやIssue 369のfull-regression結果を本Issue successとして書かない。

### focused verification

```bash
uv run pytest -q tests/unit/infra/test_managed_distribution.py -k "i370 and absence"
uv run pytest -q --run-full-regression --full-regression-shard tests/unit/infra/test_init_update.py -k "i370 and (absence or docs or uninstall)"
uv run pytest -q --run-full-regression --full-regression-shard tests/cli_runtime/test_distribution_cutover.py -k "i370 and cutover"
./spec-dock/scripts/spec-dock validate
```

### step exit

- default/keep routeにlegacy fallbackがない。
- remove-specs compatibility seamの残存symbol/caller一覧がIssue 371 handoffとして確定する。
- shipped/dogfood docsがimplementationと一致する。

## Step P10 — Integrated verification、release gate、evidence作成

### dependency

P0〜P9完了。

### candidate identity

全commandの前にcandidate full SHA、dirty state、Python/platformを記録する。異なるSHAで得た結果を一つのsuccess evidenceへ混在させない。

### focused tests

```bash
uv run pytest -q tests/unit/infra/test_managed_distribution.py -k "i370 or deprovision or uninstall"
uv run pytest -q --run-full-regression --full-regression-shard tests/unit/infra/test_init_update.py -k "uninstall or deprovision"
uv run pytest -q --run-full-regression --full-regression-shard tests/cli_runtime/test_distribution_cutover.py -k "uninstall or deprovision"
```

heavy file selectionで`--full-regression-shard`を付けるのは、global ledger completeness checkを要求せずselected nodesを実行するためである。`--run-full-regression`なしでこのflagを使わない。

### fast / static / structural gates

```bash
uv run pytest -q
make lint
./spec-dock/scripts/spec-dock validate
git diff --check
```

`uv run pytest -q`でheavy testsがpolicy skipされることはexpectedであり、focused heavy commandの代替ではない。

### full regression evidence

必要なcandidate-wide evidenceはexisting repository-native verifierで取得する。

```bash
uv run python spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00365-specdock-structural-integrity-rearchitecture-and-regression-baseline-recovery/issues/iss-00368-recognized-workspace-reconciliation/artifacts/verify-full-regression.py \
  --timeout-seconds 600 \
  --max-total-seconds 600 \
  --shards 4
```

成功条件:

- verifier exit 0
- total deadline 600秒以内
- all collected node coverageに欠落/重複なし
- approved failure ledgerのnode IDとsignatureがexact一致
- unexpected failure/error 0
- Issue 370 attributable new failure 0

Issue 369 Reportの27 approved failures、件数、時間をcurrent resultとして流用しない。candidate runがtimeout、ledger mismatch、unexpected failure/errorになった場合、本Issueは未完了である。Full Regression repairまたはledger rebaselineを本Issueへ取り込まず、attributable failureを修正するかDecision Gateで停止する。

### Linux / Darwin evidence

- local platformでfocused safety suiteを実行し、platform名とcandidate SHAを記録する。
- CIまたは別approved environmentで他方platformの同じfocused suiteを実行する。
-一方のplatformを未実行のまま「Linux/Darwin確認済み」とReportへ書かない。
- required capabilityが存在しないplatformはwrite 0のstable diagnosticをtest evidenceとする。Windows evidenceは収集しない。

### step exit

- all planned commandsのresultがcandidate SHAへ紐づく。
- red/negative/adversarial matrixがpassする。
- public golden、preservation、recovery、absence evidenceが揃う。
- test failure、skip、timeout、approved failureを別カテゴリでReportへ記録できる。

## Negative / adversarial test matrix

| Matrix ID | Scenario | Expected result | Test ID |
|---|---|---|---|
| N01 | default dry-run / keep dry-run | tree・guard・journal・marker・stage完全不変 | I370-T-DRY-001 |
| N02 | removable owned asset + unknown child | whole operation blocked、owned assetも不変 | I370-T-BLK-001 |
| N03 | initiatives nested bytes/mode/symlink/empty dirs | apply後byte/topology exact一致 | I370-T-PRES-001 |
| N04 | `.workbench` payload / outside sentinel | actionなし、identity/bytes不変 | I370-T-PRES-002 |
| N05 | fresh planにprune、deprovision planにcreate/upgrade | executable authority発行前に拒否 | I370-T-DOM-001, I370-T-PLAN-001 |
| N06 | purpose/intent/authority forged pair | parser/resume write 0 | I370-T-JRN-001 |
| N07 | deprovision journalを`--remove-specs`で再開 | checkpoint進行0、purge action 0 | I370-T-AUTH-001 |
| N08 | purge/legacy remove stateを`--keep-specs`で再解釈 | authority switch拒否 | I370-T-AUTH-001, I370-T-LEG-001 |
| N09 | legacy marker-only / copied marker | marker/target不変、recovery required | I370-T-LEG-001 |
| N10 | malformed/symlink/hardlink/special legacy marker | reason=`legacy-marker-invalid`、public error/2、markerをcleanupしない | I370-T-LEG-001 |
| N11 | legacy marker + new guard/journal | reason=`dual-recovery-state`、public partial_failure/1、全evidence不変 | I370-T-LEG-001 |
| N12 | regular same-content別inode / mode drift / hardlink | target保持、block/recovery | I370-T-ID-001, I370-T-RACE-001 |
| N13 | symlink target change / external target | linkをfollowせず保持 | I370-T-ID-001 |
| N14 | FIFO/socket/device | guard/journal/target write 0 | I370-T-ID-001 |
| N15 | root/parent rebind |外部path不変、次mutationなし | I370-T-RACE-001 |
| N16 | assessment後unknown child appearance | child保持、journal/guard保持、recovery required | I370-T-RACE-001 |
| N17 | provider source mutation | first write前停止またはjournal保持 | I370-T-RACE-001 |
| N18 | guard/journal publish failure | managed target write 0 | I370-T-REC-001 |
| N19 | action publish/checkpoint failure | exact pre/postの一方だけならresume、曖昧なら停止 | I370-T-REC-001 |
| N20 | completed+guard / completed-only cleanup window | target action再実行0 | I370-T-REC-001 |
| N21 | all owned paths already absent | protocol metadata/target syscall 0、completed | I370-T-NOOP-001 |
| N22 | JSON planned/completed/blocked/recovery/error | schema v1、one stdout object | I370-T-JSON-001 |
| N23 | absolute path/content/token in internal exception | public outputへ非露出 | I370-T-TEXT-001 |
| N24 | targetにspace/leading hyphen | retryはsame keep invocation、shell-safe | I370-T-TEXT-001 |
| N25 | default/keep source call graph | legacy plan/apply/postverify/marker/remove edge 0 | I370-T-ABS-001 |
| N26 | remove-specs route | Issue 370 service call edge 0、existing behavior unchanged | I370-T-CLI-001, I370-T-AUTH-001 |
| N27 | random child creation order | same digest/action/public order | I370-T-TREE-001, I370-T-OPS-001 |
| N28 | required capability unavailable | first write前stable error | I370-T-OPS-001 |

## Requirement / Step / Test traceability

| Requirement ID | Design element | Implementation step | Verification test/evidence |
|---|---|---|---|
| I370-F01 | D370-CLI, D370-ASSESS, D370-SERVICE | P0, P5, P7 | I370-T-CLI-001, I370-T-DRY-001, I370-T-JRN-001 |
| I370-F02 | D370-ASSESS, D370-SERVICE | P0, P5 | I370-T-DRY-001 |
| I370-F03 | D370-CONTRACT, D370-ASSESS, D370-PLAN, D370-KERNEL | P2, P3, P4 | I370-T-OWN-001, I370-T-PLAN-001, I370-T-KRN-001 |
| I370-F04 | D370-DATA, D370-ASSESS, D370-SERVICE | P2, P6 | I370-T-PRES-001, I370-T-REC-001 |
| I370-F05 | D370-DATA, D370-ASSESS | P2, P6 | I370-T-PRES-002 |
| I370-F06 | D370-ASSESS, D370-PLAN, D370-SERVICE | P0, P2, P5 | I370-T-BLK-001 |
| I370-F07 | D370-INT, D370-CONTRACT, D370-LEGACY | P1, P3, P7 | I370-T-AUTH-001 |
| I370-F08 | D370-SERVICE, D370-JOURNAL | P3, P6 | I370-T-PRES-001, I370-T-REC-001 |
| I370-F09 | D370-PLAN, D370-KERNEL, D370-SERVICE | P3, P4, P5 | I370-T-KRN-001, I370-T-NOOP-001, I370-T-RACE-001 |
| I370-F10 | D370-CLI, D370-MIG | P0, P7, P9 | I370-T-CLI-001, I370-T-ABS-001 |
| I370-S01 | D370-CLI, D370-SERVICE, D370-KERNEL | P4, P6 | I370-T-RACE-001 |
| I370-S02 | D370-DATA, D370-KERNEL | P2, P4 | I370-T-ID-001, I370-T-RACE-001 |
| I370-S03 | D370-DATA, D370-KERNEL | P2, P4 | I370-T-ID-001 |
| I370-S04 | D370-DATA, D370-KERNEL | P2, P4 | I370-T-ID-001 |
| I370-S05 | D370-DATA, D370-ASSESS | P2, P4 | I370-T-ID-001 |
| I370-S06 | D370-CONTRACT, D370-ASSESS | P0, P2 | I370-T-BLK-001 |
| I370-S07 | D370-CONTRACT, D370-ASSESS, D370-PLAN | P2, P3 | I370-T-TREE-001, I370-T-PLAN-001 |
| I370-S08 | D370-PLAN, D370-KERNEL, D370-MIG | P3, P4, P9 | I370-T-KRN-001, I370-T-ABS-001 |
| I370-S09 | D370-KERNEL, D370-JOURNAL | P4, P6 | I370-T-RACE-001 |
| I370-S10 | D370-DATA, D370-PLAN, D370-JOURNAL, D370-SERVICE | P2, P3, P6 | I370-T-PRES-001, I370-T-JRN-001, I370-T-REC-001 |
| I370-S11 | D370-CONTRACT, D370-SERVICE, D370-JOURNAL | P2, P6 | I370-T-RACE-001 |
| I370-S12 | D370-ASSESS, D370-SERVICE | P2, P5 | I370-T-BLK-001, I370-T-DRY-001 |
| I370-S13 | D370-CONTRACT, D370-KERNEL | P2, P4, P6 | I370-T-PRES-002, I370-T-ID-001 |
| I370-S14 | D370-KERNEL, D370-JOURNAL | P4, P6 | I370-T-RACE-001, I370-T-REC-001 |
| I370-S15 | D370-JOURNAL, D370-SERVICE | P6 | I370-T-REC-001 |
| I370-S16 | D370-SERVICE | P5 | I370-T-NOOP-001 |
| I370-C01 | D370-CLI, D370-MAP | P0, P7 | I370-T-CLI-001 |
| I370-C02 | D370-MAP | P0, P7 | I370-T-CHAR-001, I370-T-JSON-001 |
| I370-C03 | D370-MAP | P7 | I370-T-JSON-001 |
| I370-C04 | D370-MAP | P0, P7 | I370-T-CHAR-001, I370-T-TEXT-001 |
| I370-C05 | D370-MAP | P0, P7 | I370-T-CLI-001, I370-T-TEXT-001 |
| I370-C06 | D370-MAP | P7 | I370-T-TEXT-001 |
| I370-C07 | D370-MAP, D370-LEGACY | P7, P8 | I370-T-TEXT-001, I370-T-LEG-001 |
| I370-C08 | D370-MIG, D370-MAP | P9, P10 | I370-T-DOC-001, SpecDock validate |
| I370-R01 | D370-JOURNAL, D370-SERVICE | P3, P6 | I370-T-JRN-001, I370-T-REC-001 |
| I370-R02 | D370-INT, D370-JOURNAL | P1, P3, P6 | I370-T-JRN-001 |
| I370-R03 | D370-JOURNAL | P3, P6 | I370-T-JRN-001, I370-T-AUTH-001, I370-T-REC-001 |
| I370-R04 | D370-JOURNAL | P6 | I370-T-REC-001 |
| I370-R05 | D370-JOURNAL | P6 | I370-T-REC-001 |
| I370-R06 | D370-JOURNAL, D370-LEGACY | P3, P6 | I370-T-JRN-001, I370-T-REC-001 |
| I370-R07 | D370-LEGACY | P0, P8 | I370-T-LEG-001 |
| I370-R08 | D370-INT, D370-CLI, D370-LEGACY | P1, P7, P8 | I370-T-AUTH-001 |
| I370-R09 | D370-JOURNAL, D370-SERVICE | P6 | I370-T-REC-001 |
| I370-R10 | D370-MAP, D370-LEGACY | P7, P8 | I370-T-TEXT-001, I370-T-LEG-001 |
| I370-O01 | D370-CONTRACT, D370-ASSESS | P2 | I370-T-OPS-001 |
| I370-O02 | D370-DATA, D370-PLAN, D370-MAP | P2, P3, P7 | I370-T-TREE-001, I370-T-OPS-001, I370-T-JSON-001 |
| I370-O03 | D370-PLAT, D370-KERNEL | P4, P5, P10 | I370-T-OPS-001, Linux/Darwin focused evidence |
| I370-O04 | D370-JOURNAL, D370-MAP, D370-PLAT | P3, P7, P10 | I370-T-JRN-001, I370-T-JSON-001, I370-T-TEXT-001 |

## Rollout、kill switch、backup / restore、incident response

### rollout

runtime toggleまたは長期dual modeは作らない。rollout sequenceは次で固定する。

1. P0〜P6をpublic apply route未接続で完成させる。
2. P7でdefault/keep routeをsingle change setとしてhard cutoverする。
3. P8/P9でlegacy marker fail-closedとlegacy call-edge absenceを固定する。
4. P10の全gateがcandidate SHAで成功するまでmerge/releaseしない。
5. package release後にnew journalが存在し得るため、old packageへ自動downgradeしない。

### kill switch

- merge前: candidate diffをrevertし、releaseを行わない。
- merge後・release前: releaseを停止し、corrective commitを作成する。
- release後・new guard/journal作成前: fixed packageへ更新する。unsafe candidateの再実行を停止する。
- release後・new guard/journal作成後: same protocolを理解するcompatible newer packageでforward recoveryする。old installerへ戻さない。
- automatic remote kill switch、telemetry-driven disable、feature flagはN/A。理由はlocal ephemeral installerであり、remote control surfaceを追加しないためである。

### backup / restore

- automatic backupは作らない。managed assetはpackage Current contractから再materializeできるが、user-owned/spec historyは削除してはならないためbackupをmutation authorityの代替にしない。
- test fixturesではoperation前のfull target snapshotとoutside sentinelを保存し、byte/topology comparisonを行う。
- whole-operation rollbackはN/A。理由はRequirementがforward recoveryを正規経路とし、completed deletionを逆向きに再作成するauthorityをjournalが持たないためである。
- user-owned data lossが疑われる場合、自動restoreを行わず、repository VCS、利用者backup、filesystem snapshotからの人間主導restoreへ切り替える。

### incident response

1. 同じtargetへのuninstall retryを停止する。
2. candidate/package version、root identity、public JSON、guard/journal bytes digest、relative filesystem inventoryを保全する。file contentやcredentialを外部共有しない。
3. `.distribution-retry.json`、`.distribution-journal.json`、`.uninstall-retry.json`、stage/quarantineを手動削除・renameしない。
4. `--keep-specs`から`--remove-specs`へ切り替えない。
5. same-plan compatible recoveryが証明できる場合だけcorrective packageで再開する。
6. user-owned/spec history mutationが確認された場合はsecurity/data-loss incidentとしてorchestratorと利用者へ明示し、VCS/backup restoreを人間判断へ渡す。
7. root/authority/planが曖昧な場合はautomatic cleanupを行わず停止状態を維持する。

### privacy / auditability / monitoring

- remote telemetryは追加しない。
- public outputはrepository-relative path、stable reason、phase、checkpoint、digestのsanitized subsetに限定する。
- absolute path、provider source bytes、target file content、credential、tokenをjournal/public outputへ入れない。
- audit evidenceはlocal guard/journal、public JSON、test artifact、candidate SHAで構成する。
- remote monitoringはN/A。理由はoperationがlocal CLIであり、new external serviceをscope外とするためである。

## Stop conditions / Decision Gates

coderは次のいずれかで作業を停止し、Requirement/Designの更新判断をorchestratorへ返す。

| Gate | Trigger |停止時に返すevidence |
|---|---|---|
| DG-01 Ownership |削除対象pathにCurrent/historical/generated/exact obsolete evidenceがない | relative path、observed identity、調査したcontract source |
| DG-02 Preservation | initiatives/Workbenchのsafe witnessを構築できない | blocker reason、type/link/root/parent evidence |
| DG-03 Journal wire | schema 1 / protocol 2でrequired conditionをstrict validationできない |不足field、forged counterexample、compatibility impact |
| DG-04 Legacy marker | automatic conversionを要求するcaseが出る | marker field set、non-injective counterexample、authority risk |
| DG-05 Purge boundary | remove-specsをdeprovision serviceへ渡す必要が出る | current call graph、public impact、Issue 371 dependency |
| DG-06 Kernel | exact no-follow removalがgeneric recursionなしで実装不能 | platform/syscall evidence、unsafe race counterexample |
| DG-07 Public schema | schema v1 field meaning変更が必要 | current golden、target mapping gap、consumer impact |
| DG-08 Regression | verifier timeout/ledger mismatch/unexpected failureがIssue 370にattributable | candidate SHA、node ID、normalized signature、focused reproduction |
| DG-09 Platform | Linux/Darwinの一方でwrite-before-capability-checkが避けられない | platform、capability、first-write trace |
| DG-10 Hidden fallback | default/keep routeからlegacy writer/remove helperを除去できない | exact caller/callee、remaining ownership、D4 boundary |

Decision Gateを「temporary workaround」「compatibility fallback」「test expectation緩和」で通過してはならない。

## Rollback / forward recovery

### code rollback before new journal

new deprovision guard/journalをconsumerで作成していないcandidateは、normal code revertが可能である。test failure時はtarget write 0のfixtureを確認してからcandidate diffを破棄する。

### operation recovery after journal creation

- same root
- intent=`deprovision`
- authority=`managed-distribution-deprovision`
- same contract identity
- same canonical plan digest
- compatible protocol
- exact pre/postcondition

を全て満たすcompatible newer packageだけがcheckpointを進める。completed actionをrollbackしない。mismatch、unknown child、replacement、legacy marker、purge invocationはwrite 0で停止する。

### terminal cleanup failure

- completed journal + guard: postcondition再検証後にguard cleanup、journal cleanupだけを行う。
- completed journal only: target actionを再実行せずjournal cleanupだけを行う。
- guard only: same-plan reconstruction後にjournal prepareへ進む。
- nonterminal journal without guard: authorityアンカー不足として停止する。

## Issue 371 / 372 handoff

### Issue 371へ渡すexact boundary

- `deprovision` intentとauthority string
- deprovision journalがある状態で`--remove-specs` checkpointを進めないadmission test
- `spec-dock/initiatives` preservation witnessとpurge非許可invariant
- remove-specs compatibility routeのcurrent parser/output/action tests
- D4 ownerとして残したlegacy helper/symbol/call-edgeの一覧
- purgeを追加してもdeprovision plan digest/authorityを再利用できないvalidation seam

Issue 371はdeprovision journalをpurgeへupgradeしない。purgeは別intent、別authority、別plan、別postconditionとして実装する。

### Issue 372へ渡すexact boundary

- default/keep routeのlegacy call-edge absence test
- public JSON/text/exit golden
- provider/dogfood docs parity
- Linux/Darwin focused evidence
- candidate full-regression evidence
- D4 ownerとして意図的に残るcompatibility seam一覧

Issue 372はdefault/keep legacy writerを後から削除するownerではない。P9 absence gate未達ならIssue 370を完了しない。

## Completion criteria

1. P0〜P10が順にexit条件を満たす。
2. Requirementの48 IDが本Planのstepとtestへtraceされる。
3. default/keep dry-runがread-only new assessmentを使用する。
4. mutating keep applyがschema-2 guard、protocol-2 journal、common kernel、post-assessmentを使用する。
5. no-op keep applyがprotocol metadata/target write 0でcompletedになる。
6. initiatives byte identity、Workbench、outside sentinel、unknown/modified childが保持される。
7. mixed blocker、symlink、hardlink、special file、root/parent/child/source raceがfail closedである。
8. legacy markerを自動変換せず、marker/targetを保持する。
9. deprovision/purge authority switchが全routeで拒否される。
10. public schema v1、one stdout object、text、exit、sanitization、retry guidanceがgoldenに一致する。
11. default/keep routeからlegacy plan/apply/postverify/marker/remove fallbackが物理的に除去される。
12. focused、fast、lint、validate、diff check、candidate full regressionが所定条件を満たす。
13.未実行test、policy skip、Issue 369 evidenceをIssue 370 successとしてReportへ記録しない。
14. coderがDecision Gateを推測で通過していない。
