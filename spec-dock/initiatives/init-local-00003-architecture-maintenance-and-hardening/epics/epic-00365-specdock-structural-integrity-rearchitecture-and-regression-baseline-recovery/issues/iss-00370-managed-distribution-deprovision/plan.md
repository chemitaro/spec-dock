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
- exact SHA: `5d25f393dba95d1a71c5582714de43c82fa094f4`

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
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/active_store.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/artifact_writer.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/json_state.py`
- `src/spec_dock/assets/spec_dock/docs/reference_sync.md`
- `tests/conftest.py`
- Issue 368 full-regression verifier/ledger/timing artifacts

runtime generated-state filesはcurrent path/schema producer contractのevidenceであり、Issue 370から別writerを追加する対象ではない。`managed_distribution.json`へCurrent inventoryまたはpurge authorityを追加しない。current/historical/generated exact ownership evidenceが不足しているpathをpathname推測でownedにせずDecision Gateで停止する。test laneは現行`tests/conftest.py`の`fast` / `full_regression` contractを使用し、lane policy自体を本Issueで変更しない。

## Test inventoryとstable test IDs

実装stepとRequirementのtraceabilityに次のtest IDを使用する。実際のpytest function名は`test_i370_...` prefixで、このIDをdocstringまたはparameter IDへ保持する。

| Test ID | 固定する契約 | 主なfile |
|---|---|---|
| I370-T-CLI-001 | seven-row CLI matrix、parser、route owner、exit | `test_init_update.py`, `test_distribution_cutover.py` |
| I370-T-CHAR-001 | current JSON/text/action/summary field golden、current journal/result gaps | `test_init_update.py` |
| I370-T-DRY-001 | default/keep dry-runの同一assessmentとzero-write | `test_init_update.py` |
| I370-T-DOM-001 | `deprovision` intent、`uninstall` mapping、action allowlist | `test_managed_distribution.py` |
| I370-T-OWN-001 | single generated producer、active/.agent current slot/kind/schema identity、active selection/generated_at/index-tree cross-consistency、legacy/conflict/unknown blocker、current/historical/obsolete ownership | `test_managed_distribution.py`, `test_init_update.py` |
| I370-T-TREE-001 | bounded traversal、complete classification、surviving-anchor collapse/re-anchor、type-specific namespace digest、deterministic plan | `test_managed_distribution.py` |
| I370-T-PRES-001 | initiatives byte identity、empty dir、safe symlink、mode/link topology | `test_managed_distribution.py`, `test_init_update.py` |
| I370-T-PRES-002 | Workbenchとoutside sentinelのpreservation | `test_init_update.py`, `test_distribution_cutover.py` |
| I370-T-BLK-001 | unknown/modified/generated conflictとmixed safe/unsafeのwhole-operation write zero | `test_init_update.py`, `test_distribution_cutover.py` |
| I370-T-ID-001 | regular/symlink/hardlink/special exact identity | `test_managed_distribution.py` |
| I370-T-RACE-001 | root lockとroot/parent/target/child/source/absence-witness appearance race | `test_managed_distribution.py` |
| I370-T-PLAN-001 | mutating-only executable plan、directory dependencies、witness completeness、canonical digest、forged grammar rejection | `test_managed_distribution.py` |
| I370-T-JRN-001 | guard purpose、intent、authority、schema/protocol、witness/dependency parser、reachable status/checkpoint table | `test_managed_distribution.py` |
| I370-T-KRN-001 | exact `prune`、immediate child evidenceからの`remove-empty-directory`、published directory subtree subsumption、no recursion/reopen | `test_managed_distribution.py` |
| I370-T-NOOP-001 | owned-ancestor collapse、descendant action 0、entire managed subtree absentのprotocol metadata/target write zero | `test_init_update.py`, `test_managed_distribution.py` |
| I370-T-REC-001 | 3階層nested leaf/各directory publish、subtree subsumption、verifying、atomic verified+completed、terminal cleanupのcrash windowsとsame-plan resume | `test_managed_distribution.py`, `test_distribution_cutover.py` |
| I370-T-DIR-001 | immediate leaf/directory child evidence、directory semantic projection、parent ctime変化、directory replacement、removed descendant reopen 0 | `test_managed_distribution.py` |
| I370-T-SRC-001 | durable semantic source projection、semantic-equal別physical install root recovery、semantic drift、same-invocation full-snapshot replacement | `test_managed_distribution.py`, `test_distribution_cutover.py` |
| I370-T-RESULT-001 | durable stateからtyped phase/last/failed/pending/action errors/top errors/retry policyを一意生成し、pending pathのfailed/pending重複とnormal keep/legacy retry ruleを固定し、CLI journal access 0 | `test_managed_distribution.py`, `test_init_update.py`, `test_distribution_cutover.py` |
| I370-T-AUTH-001 | deprovision/purge authority non-switching | `test_managed_distribution.py`, `test_init_update.py` |
| I370-T-LEG-001 | legacy marker non-conversion、dual/malformed/copied marker | `test_managed_distribution.py`, `test_init_update.py` |
| I370-T-JSON-001 | schema v1、exactly-one stdout object、typed field mapping、status別targetとfailed/pending overlap | `test_init_update.py` |
| I370-T-TEXT-001 | text section order、typed phase、exit、status別target sanitization、normal keep/legacy retry nullability | `test_init_update.py` |
| I370-T-ABS-001 | default/keep legacy symbol/call-edge/fallback absence、CLI journal interpretation absence | `test_init_update.py`, `test_distribution_cutover.py` |
| I370-T-OPS-001 | bounded linear observation、determinism、capability fail-closed | `test_managed_distribution.py` |
| I370-T-DOC-001 | shipped/dogfood docs parity、generated boundary、new recovery guidance | `test_init_update.py` |

## 実装順序

```text
P0 Characterization / exact producer inventory / result gap
 -> P1 Intent / grammar / authority
 -> P2 Single generated/source contract / bounded observation / witnesses / surviving-anchor collapse
 -> P3 Mutating plan / immediate-child evidence / semantic digest / strict journal parser
 -> P4 Descriptor-bound prune / immediate-child-bound rmdir kernel
 -> P5 Read-only service / metadata-free no-op
 -> P6 Reachable journal state machine / recovery / typed result builder
 -> P7 CLI typed mapper / route split
 -> P8 Legacy marker fail-closed
 -> P9 Legacy call-edge removal / docs
 -> P10 Integrated verification / release gate
```

P0〜P4はpublic default/keep routeを切り替えない。P5でdry-runとno-op serviceを完成させるが、mutating applyのpublic routeはまだ切り替えない。P6でjournal/recovery/result populationを完成させてから、P7でdefault/keep dry-run/applyを一度にhard cutoverする。P7完了後にlegacy fallbackまたはCLI journal interpretationを残さない。

## Step P0 — Current behavior characterization、producer inventory、result gap

### dependency

なし。production codeを変更する前に実施する。

### owned files

- `tests/unit/infra/test_managed_distribution.py`
- `tests/unit/infra/test_init_update.py`
- `tests/cli_runtime/test_distribution_cutover.py`

### red tests / characterization

1. exact SHAのcurrent `DistributionOperation`、`JournaledDistributionIntent`、`DistributionActionName`、journal status/checkpoint parserをsource-level snapshotにする。
2. current uninstall default/keep/remove CLI matrix、JSON/text golden、exit mapping、retry guidance、summary/action field setを固定する。
3. current `_add_generated_state_uninstall_actions()`が`active` / `.agent`全leafをpath membershipでwould-removeにする事実をcharacterizationし、target contractではないことをtest名で明示する。
4. fixed SHAのruntime producerから次をinventory化する。
   - active logical slots: initiative/epic/issue symlink XOR `.path`
   - `active/context-pack.md`
   - `.agent/active.json`
   - `.agent/{index-all,tree-all,index,tree,deps-issues}.json`
   - legacy names: active current-runbook、`.agent/deps*`、`.work/*`
5. real runtime output fixturesを`active_store.py` / `artifact_writer.py` / `json_state.py`経由で生成し、schema/discriminator/kindと「固定modeをownership条件にせず、観測modeをexact preconditionへ束縛する」規則をgolden化する。handwritten permissive fixtureだけでproducer contractを固定しない。
6. current `DistributionProcessResult`ではphase、last completed、failed paths、per-action error、top-level errorsを保持できずCLI-owned stateに依存するgapをred testで示す。
7. current successful deprovision後のsubtree-absent rerun、parent missing、directory cleanup checkpoint sequenceをcharacterizeし、target red testsと分離する。
8. heavy test laneのnode IDと`--full-regression-shard`使用条件をcollect-onlyで確認する。

### focused verification

```bash
uv run pytest -q tests/unit/infra/test_managed_distribution.py -k "uninstall or generated or journal"
uv run pytest -q --run-full-regression --full-regression-shard tests/unit/infra/test_init_update.py -k "uninstall"
uv run pytest -q --run-full-regression --full-regression-shard tests/cli_runtime/test_distribution_cutover.py -k "uninstall"
```

このstepではtarget red testが失敗することを記録する。既存behavior characterizationの失敗とfuture contract redを混同しない。

### step exit

- current factsとtarget changesがtest名/fixtureで分離される。
- generated current/legacy slot一覧とexact producer referenceが固定される。
- public mapperが必要とするtyped field gapが具体的なred testになる。
- P1以降で削除してよいdefault/keep legacy symbolとD4-owned symbolがcall graphで分離される。

## Step P1 — `deprovision` intent、action grammar、authority mapping

### dependency

P0 complete。

### owned files / symbols

- `src/spec_dock/managed_distribution.py`
  - `JournaledDistributionIntent`
  - `DistributionActionName`
  - `_intent_allows_distribution_action()`
  - `_journal_authority_for_intent()`
  - `_journal_guard_purpose_for_intent()`
  - guard parser/serializer mapping

### red tests first

- `intent="deprovision"`を型/parserが受理しない。
- deprovisionに`create` / `adopt` / `upgrade` / `ensure-directory`を偽装したplan/journal/kernelが拒否される。
- freshに`prune` / `remove-empty-directory`を偽装したplanが拒否される。
- purpose/intent/authorityのforged pairを拒否する。
- deprovision journalをpurge invocationで進めない。

### implementation

1. `JournaledDistributionIntent`へ`deprovision`を追加する。
2. `DistributionActionName`へ`remove-empty-directory`を追加する。
3. intent-specific allowlistを実行権限発行、journal parser/resume、kernel入口の三境界で同じhelperにより強制する。
4. authorityを`managed-distribution-deprovision`、guard purposeを`deprovision-journal-forward-only`へ固定する。
5. public requested operation `uninstall`とjournal intent `deprovision`を別fieldとして扱う。
6. purge intent/authority/actionを追加しない。

### focused verification

```bash
uv run pytest -q tests/unit/infra/test_managed_distribution.py -k "i370 and (intent or grammar or authority or guard)"
```

### step exit

- forged grammarがfilesystem observation前に拒否される。
- fresh/recognized intentの既存authority mappingに差分がない。
- deprovisionからpurgeへのtype/call edgeがない。

## Step P2 — Single generated/source contract、bounded observation、preservation / surviving-anchor absence witness

### dependency

P1 complete。

### owned files / symbols

- `src/spec_dock/managed_distribution.py`
  - `DistributionGeneratedStateEntry`
  - `DistributionGeneratedStateContract`
  - `build_deprovision_generated_state_contract()`
  - `_render_context_pack()`（current CLI helperをbehavior unchangedで移動・共有）
  - `DistributionSourceSemanticIdentity`
  - existing `DistributionSourceSnapshot` invocation-local usage
  - `DistributionTreeEntrySnapshot`
  - `DistributionImmediateChildEvidence`
  - `DistributionDirectoryMutationSnapshot`
  - `DistributionPreservationWitness`
  - `DistributionCollapsedAbsenceWitness`
  - `DistributionDeprovisionContract`
  - `build_deprovision_contract()`
  - `build_deprovision_workspace_assessment()`
- `tests/unit/infra/test_managed_distribution.py`
- `tests/unit/infra/test_init_update.py`

### red tests first

1. deprovision assessmentが`contract.generated_state`と独立`generated_assets`を同時に受け取れるsignature/call graphを拒否する。
2. real current active symlink、path fallback、context pack、active manifest、index/tree/deps outputsがcurrent generated ownershipになるpositive matrix。
3. active symlink + `.path`併存、out-of-root target、wrong kind/content、malformed/extra JSON、hardlink、unknown child、active selection不一致、present artifactの`generated_at`不一致、index/tree node集合不一致がwhole-operation blockerになるnegative matrix。
4. active current-runbook、legacy `.agent/deps*`、`.work/*`がpathnameだけではownedにならず、historical exact identityがなければblockする。
5. current physical sourceを二つの異なるinstall root/device/inode/mtimeへ配置し、canonical source path、kind、SHA-256、mode、link target、schema/protocolが同じなら`DistributionSourceSemanticIdentity`とcontract digestが一致する。
6. source bytes、mode、symlink target、canonical source path、asset kind、schema/protocolの各driftでsemantic projectionが不一致になる。
7. same invocationでsource capture後にinode/ctime/mtime/size/modeを差し替えるfixtureはfull `DistributionSourceSnapshot` mismatchになる。
8. `spec-dock/initiatives`と`.workbench`のbyte/mode/link topology witness。
9. 3階層以上のowned pathでancestor absent時にone collapsed witnessを発行しdescendant actionを0にする。
10. nearest existing ancestorが同じplanのdirectory removal対象なら、上位surviving ancestorへcanonical re-anchorする。target root fallbackも固定する。
11. unproven parent gap、surviving anchor symlink/rebind、collapsed root appearanceをblockする。
12. bounded traversal外large treeをscanしないcounter test。

### implementation

1. generated producerを`managed_distribution.py`へ一つだけ実装する。
2. current CLI `_render_context_pack()`を`managed_distribution.py`へbehavior unchangedで移し、fresh/recognized generated asset builderとdeprovision producerが同じhelperを使用する。shipped runtime rendererとのreal-fixture byte parityを固定する。
3. `.agent/active.json`を先にsemantic validationし、active logical slotsのallowed targetを一意に解決する。
4. generated current JSON/symlinkをsemantic validation後のexact target snapshotへ束縛し、legacy/unrecognized entryはhistorical exact identityがない限りblockする。
5. provider regular/symlink sourceごとにcanonical `DistributionSourceSemanticIdentity`を構築する。absolute extraction/cache pathとdevice/inode/ctime/mtimeをdurable projectionへ入れない。
6. existing `DistributionSourceSnapshot`はcurrent invocation内memory-only evidenceとしてcaptureし、source read前後、plan発行前、first mutation前に再検証する。journal/guard/plan serializationへ入れない。
7. deprovision専用assessment wrapperからgenerated producerをexactly once呼び、generic `generated_assets` routeをdeprovisionから到達不能にする。
8. managed path treeをtop-down観測し、最初のmissing contract-owned ancestorでcollapse rootを決める。
9. action closureを確定後、candidate anchorがdirectory-removal closure内ならparentへ上がり、削除されないnearest surviving bound ancestorへre-anchorする。
10. collapse配下をenumerateせず、surviving anchor path/binding、missing suffix、contract descendant semantic digestをwitness化する。
11. preservation/absence witnessとsemantic source projectionをassessment/contract identityへ含める。
12. current journal resumeではfresh collapseまたはphysical source locationでjournal action set/digestを置換しない。

### focused verification

```bash
uv run pytest -q tests/unit/infra/test_managed_distribution.py -k "i370 and (ownership or generated or source or tree or preserve or absence or anchor)"
uv run pytest -q --run-full-regression --full-regression-shard tests/unit/infra/test_init_update.py -k "i370 and (generated or preserve or absent or source)"
```

### step exit

- `I370-T-OWN-001`のcurrent/legacy/conflict matrixがpassする。
- deprovision assessmentへgenerated stateを二系統で渡せない。
- durable source identityがphysical install-root identityから独立し、same-invocation full snapshot guardを失っていない。
- initiatives/Workbench witnessとsurviving-anchor collapsed witnessがdeterministicである。
- unknown/legacy/generated conflictがblockerになりsafe subsetを適用しない。
## Step P3 — Mutating-only plan、immediate child evidence、semantic digest、strict journal parser

### dependency

P2 complete。

### owned files / symbols

- `src/spec_dock/managed_distribution.py`
  - `WorkspaceAssessment`
  - `ExecutableMutationPlan`
  - `DistributionImmediateChildEvidence`
  - type-specific child semantic projection helpers
  - semantic source serializer/digest helpers
  - `OperationJournal` deprovision witness/source fields
  - `OperationJournalAction` condition schema
  - journal parser/contract assertions
- `tests/unit/infra/test_managed_distribution.py`

### red tests first

1. deprovision executable planに`preserve` / `block` / already-absent diagnosticを混入すると拒否。
2. generated contract、semantic source projection、preservation witness、surviving-anchor absence witnessの欠落/改変/順序変更でdigest mismatch。
3. directory evidenceが対象directoryのimmediate childではない、future action、self、unknown action、preserve witness、またはdescendant actionを直接参照すると拒否。
4. leaf evidenceはleaf `prune` action、directory evidenceはchild `remove-empty-directory` actionへexact対応し、required checkpointは`published`だけを許可する。
5. directory child semantic recordから`ctime_ns`/`link_count`を除外する。directoryの両fieldだけを変えたfixtureではdigest不変、inode/type/modeを変えたfixtureではdigest mismatch。
6. regular/symlink childのexact identity/content/link fieldsを欠落・改変するとdigest mismatch。
7. parser state matrix:
   - prepared=all pending
   - executing=pending/published only
   - verifying=all published
   - completed=all verified
8. executing+verified、verifying+pending/verified、completed+published、parent directory published+immediate child pending、directory child kind/subsumption欠落を拒否。
9. published child directoryのdescendant evidenceをparent preconditionへ直接列挙したjournalを拒否。
10. durable source fieldへdevice/inode/ctime/mtime/absolute extraction pathを混入したjournal/guardを拒否。
11. deprovision validator追加後もexisting fresh/recognized protocol-2 journalsのcurrent valid fixtureを変更せず受理する。
12. witnessをjournal actionとしてcheckpoint化したfixture、self-rehashed field/parent/evidence omissionを拒否。

### implementation

1. deprovision `ExecutableMutationPlan.actions`をpresent targetの`prune`とexisting directoryの`remove-empty-directory`だけにする。
2. already-absent pathはdiagnostic outcome/surviving-anchor absence witnessとして残しmutating actionにしない。
3. each directory actionへimmediate child evidenceをcanonical orderで作る。leaf childはleaf action、directory childはchild directory actionだけを参照する。
4. directory child published checkpointをsubtree subsumption evidenceとしてjournal schemaへlosslessに保存する。
5. type-specific child semantic projectionを実装し、directory recordからctime/link countを除外する。runtime full snapshot typeとは分離する。
6. plan/contract digestへgenerated contract、semantic source projection、immediate child evidence、preservation/absence witnessesを追加する。
7. physical `DistributionSourceSnapshot` fieldをdurable serializer/digestから排除する。
8. protocol-2 deprovision journalへimmutable witness/source fieldsを追加しstrict parseする。
9. status/checkpoint/dependency/subsumption validatorをintent-specific helperへ集約し、prepare/write/load/resume全boundaryで呼ぶ。fresh/recognizedはexisting semanticsを維持する。
10. verifyingからcompletedは一回のatomic publicationでall published -> all verified/status completedとする。

### focused verification

```bash
uv run pytest -q tests/unit/infra/test_managed_distribution.py -k "i370 and (plan or digest or semantic or source or journal or parser or checkpoint or witness or immediate_child)"
```

### step exit

- first nested directory actionへ正規sequenceから到達できる。
- parser、digest、plan validatorが同じimmediate-child/subsumption/state tableを使う。
- directory parent ctime/link-countのauthorized変化でdigestを失わず、inode/type/mode replacementを拒否する。
- durable plan equalityがphysical install-root identityに依存しない。
- preserve/block/witnessに到達不能checkpointがない。
- no-op planはmutating action 0で表現できる。
## Step P4 — Descriptor-bound `prune` / immediate-child-bound exact empty-directory kernel

### dependency

P3 complete。

### owned files / symbols

- `src/spec_dock/managed_distribution.py`
  - existing exact remove/quarantine helpers
  - `_remove_distribution_directory_if_bound()`
  - type-specific immediate child observer/digest helper
  - apply dispatch/intent allowlist
- `tests/unit/infra/test_managed_distribution.py`

### red tests first

1. current/historical/generated regular/symlink prune success。
2. same-content different inode、mode drift、regular/symlink hardlink、special、symlink target changeを拒否。
3. 3階層以上の`root/a/b/file` cleanupを構築し、`file` leaf -> `b` directory -> `a` directory -> `root` directoryのimmediate-child chainだけを持つ。
4. leaf child pendingで`b` rmdirが呼ばれない。
5. leaf publishedだがleaf path present/replacedなら`b`を削除しない。
6. `b` publishedだが`b` path presentなら`a`を削除しない。`b` absentなら`a`は`b`配下descendantをopen/list/statせず進める。
7. each directory rmdir直後・checkpoint publish前crashからexact path absenceでそのdirectoryをpublishedへ再構成し、ancestorへ進む。
8. leaf removalでparent directory ctime/link countが変化してもsemantic child digestはexpected値へ収束する。
9. directory childのinode/type/mode replacement、unknown child appearance、parent/root rebindを保持して停止する。
10. runtime held descriptorとvisible directoryのfull snapshot mismatchを拒否する。
11. recursive function、pathname `shutil.rmtree`、boundary-wide scanへのcall edgeがない。

### implementation

1. leaf pruneはexisting descriptor-bound exact helpersを再利用する。
2. directory helper前にservice/parserがimmediate child evidenceを検証する。
3. leaf evidenceはleaf exact absence、directory evidenceはchild directory path absenceだけをdescriptor-relativeに確認する。published child directory配下を再openしない。
4. held target directoryとvisible pathのfull identityをruntime TOCTOU guardとして比較する。
5. current immediate child setをtype-specific semantic projectionでdigest化する。directory recordのctime/link countを除外し、inode/type/modeを含める。
6. expected empty digest、parent/root bindingを確認してexact one `rmdir(..., dir_fd=...)`を実行する。
7. path absence確認後だけdirectory checkpointをpublishedへ進め、そのcheckpointをsubtree subsumption evidenceとする。
8. EEXIST/ENOTEMPTY、unknown child、identity mismatchはcleanup retryせずrecovery required。
9. platform capability不足をfirst write前にtyped errorへする。

### focused verification

```bash
uv run pytest -q tests/unit/infra/test_managed_distribution.py -k "i370 and (kernel or prune or empty_directory or immediate_child or nested or subsumption or ctime or race)"
```

### step exit

- regular/symlink/directory mutationがroot descriptorとexact planへ束縛される。
- 3階層以上のnested directoryがimmediate child evidenceだけでbottom-upに収束する。
- published directory checkpoint後にancestor/resumeがremoved subtree descendantを再openしない。
- parent ctime/link-countのauthorized変化を受理し、directory replacement/unknown childを拒否する。
- generic recursive deletionを追加していない。
## Step P5 — Deprovision serviceのdry-runとmetadata-free no-op apply

### dependency

P2〜P4 complete。

### owned files / symbols

- `src/spec_dock/managed_distribution.py`
  - `execute_deprovision_distribution(..., apply=False)`
  - no-op apply branch
  - planned/completed typed result construction
- `src/spec_dock/cli.py`
  - public routeへ未接続のthin private service seam only
- tests

### red tests first

1. default dry-runと`--keep-specs` dry-runがsingle generated contractを含む同じassessment/outcomesを返す。
2. dry-runがguard/journal/legacy marker/stage/targetを一切変更しない。
3. all owned leaves/subtrees absent、preservation validでmutating action 0、protocol metadata/target syscall 0、completed。
4. nested owned ancestor absentでdescendant action/outcomeを展開せずone collapsed root `already_removed` outcome。
5. assessment後collapsed ancestor appearanceでnew pruneを発行せずblocked。
6. unproven missing parentはno-opとして受理しない。
7. no-op typed resultは`phase=complete`、`last_completed_phase=post-verified`でmarker finalizationを偽装しない。
8. blocker no-op candidateはwhole-operation write 0。

### implementation

1. `apply=False`はassessmentからfully-populated planned/recovery/error resultを返す。
2. no recovery metadataかつmutating action 0の`apply=True`はguard/journalを作らずwitness/root/nearest parentをread-only再検証する。
3. collapsed witnessはappearanceを検出したらtargetに触れずblocked resultへする。
4. no-op success action outcomesはcollapsed rootまたはmissing leafごとのcanonical `already_removed`、preservation witnessごとの`preserved`とする。
5. descendant outcome/actionを展開しない。
6. public route cutoverはP7まで行わない。

### focused verification

```bash
uv run pytest -q tests/unit/infra/test_managed_distribution.py -k "i370 and (dry_run or no_op or absence)"
uv run pytest -q --run-full-regression --full-regression-shard tests/unit/infra/test_init_update.py -k "i370 and (dry_run or no_op or absent)"
```

### step exit

- dry-runとno-opがtarget/protocol write 0。
- entire managed subtree absent fixtureがpassする。
- absence appearanceとunproven parent gapを安全に拒否する。
- result fieldsがCLI journal accessなしで完成している。

## Step P6 — Reachable journal state machine、nested forward recovery、semantic-source admission、typed result builder

### dependency

P3〜P5 complete。

### owned files / symbols

- `src/spec_dock/managed_distribution.py`
  - `OperationJournalStore`
  - deprovision guard/journal preparation
  - action publish/recovery
  - immediate child/subsumption validator
  - verifying/atomic completed transition
  - semantic source admission + invocation full-snapshot guard
  - additive defaulted fields on `DistributionProcessResult`
  - `_distribution_process_result_from_state()`
  - `execute_deprovision_distribution(..., apply=True)`
- tests

### red tests first

1. first mutationより前にguard+journalがdurableである。
2. guard-only、prepared、executing leaf、3階層各directory published直後、executing all-published、verifying、completed+guard、completed-onlyを個別fixture化する。
3. leaf unlink後、each directory rmdir後のcheckpoint failureをexact postconditionからpublishedへ再構成する。
4. published directory checkpointがsubtree evidenceをsubsumesし、ancestor action、resume、verifyingでそのdirectory配下のopen/list/stat/readlink hookが0である。
5. executingでverified checkpoint、verifyingでpending/verified、completedでpublished、parent published+child pending、invalid child kind/subsumptionをrejectする。
6. all published後verifying crashではtarget actionを再実行せず、published directory summariesとremaining witnessesだけを再検証する。
7. post-assessment後atomic completed publicationのbefore/after crashがverifying-all-publishedまたはcompleted-all-verifiedのどちらかだけになる。
8. separate temporary install roots A/Bへsemantic-equal package assetsを配置する。Aでguard/journalを作り、compatible newer Bで同じsemantic projection/plan digestを再構成してresumeする。
9. Bのcanonical source path、kind、bytes、mode、symlink target、schema/protocolいずれかをdriftさせるとwrite 0でplan mismatch。
10. same invocation中にsource capture後にinode/ctime/mtime/size/modeを差し替えるとfull snapshot mismatchで次target mutation 0。
11. surviving absence anchorがdeletion closure外であること、appearance/witness mismatch、preservation mismatch、unknown childをrecovery requiredにする。
12. planned dry-run、blocked apply、各durable fixtureからexact phase、last completed、failed/pending paths、action errors、top-level errors、retry policyを期待する。pending pathはfailed/pending両fieldへ一回ずつ入る。
13. cleanup failureでtarget action再実行0。
14. result errorsにraw absolute path/content/nonce/tokenが漏れない。
15. fresh/recognized existing `DistributionProcessResult` constructor/behavior testsが追加default fieldsにより変化しない。

### implementation

1. mutating operationだけguard、prepared journalを作る。
2. guard/journalのdurable equalityはsemantic source projectionを使用し、physical source snapshotを直列化しない。
3. new/compatible invocationはcurrent full source snapshotを新規captureし、stored semantic projection一致後にsame-plan admissionする。current invocation中はfull snapshotをmutation boundaryまで再検証する。
4. status/checkpoint/immediate-child/subsumption validatorを全journal read/write/transitionへ適用する。
5. executing中はpending->publishedだけを許可する。
6. leaf後、directoryをdeepest-firstにimmediate child evidenceから実行する。directory published checkpointをsubtree summaryとする。
7. crash resumeはpublished directory配下descendantを再openせず、child directory path absenceだけを確認してancestorへ進む。
8.全action published後だけverifyingへ進める。
9. verifyingではtarget mutationせず、published directory summaries、top-level postconditions、preservation/surviving-anchor witnesses、remaining namespaceを再検証する。
10.成功時に一回のatomic writeで全action verified + status completedへ進める。
11. guard、journalの順にexact cleanupする。
12. `DistributionProcessResult`へdefault付きpresentation fieldsを末尾追加し、deprovision returnだけcomplete populationを必須validateする。
13. private result builderがdurable state population tableをone placeで実装し、全return/exception pathをtyped resultへ変換する。
14. same-plan resumeはjournal action/witness/semantic source projectionを正本とし、current absence collapseまたはphysical install-root差でaction set/digestを変更しない。

### focused verification

```bash
uv run pytest -q tests/unit/infra/test_managed_distribution.py -k "i370 and (recovery or checkpoint or nested or subsumption or verifying or completed or source or compatible or result)"
uv run pytest -q --run-full-regression --full-regression-shard tests/cli_runtime/test_distribution_cutover.py -k "i370 and (partial or retry or nested or source or result)"
```

### step exit

- reachable state tableの全行とforbidden combinationがtestされる。
- 3階層nested cleanupの各directory publish直後からsame-plan retryが収束する。
- removed subtree descendantのreopenがancestor/resume/verifyingで0である。
- semantic-equal別physical install rootのcompatible newer resumeとsemantic drift rejectionが証明される。
- same-invocation full source snapshot TOCTOU safetyを維持する。
- typed resultだけでpublic mapperの全dynamic fieldを決められる。
## Step P7 — CLI adapter、typed public mapper、default/keep hard cutover

### dependency

P5、P6 complete。P0 public golden available。

### owned files / symbols

- `src/spec_dock/cli.py`
  - parser/matrixは維持
  - `_run_uninstall_deprovision()`
  - `_run_uninstall_remove_specs_compatibility()`
  - `_uninstall_payload_from_result()`
  - text renderer / exit mapping
- `src/spec_dock/managed_distribution.py`
  - public service exports
- tests

### red tests first

1. seven-row CLI matrix。
2. default/keep dry-run/applyがnew serviceへ一回だけdispatchする。
3. remove-specs routeがnew serviceへ入らない。
4. mapperへfully-populated resultを渡すだけでplanned/completed/blocked/recovery/error JSON/text goldenが生成できる。
5. journal/store openをmonkeypatchで例外にしてもmapperが成功する。
6. CLI sourceにjournal status/checkpoint/guard purpose/legacy marker payload解釈がない。
7. `phase`、`last_completed_phase`、`failed_paths`、`pending_paths`、per-action error、top-level errorsがresult fieldとexact一致し、全pending pathがfailed pathsにも含まれる。
8. no-op last completed=`post-verified`、mutating success=`marker-finalized`。
9. exactly one stdout object、sanitized errors、shell-safe keep retry。default dry-runはretry `null`、keep dry-run/completed/blocked/partial/preflight errorはsame keep command、legacy markerはmanual recoveryで`null`とする。
10. `target`はblocked/partialだけrelative/unavailableへsanitizationし、planned/completed/errorはcurrent resolved target fieldを維持する。
11. service failure時legacy fallbackが呼ばれない。

### implementation

1. specs modeをCLIで一度だけ解決する。
2. default/keep routeを`execute_deprovision_distribution()`へdispatchする。
3. apply routeはexisting root lock/bindingを保持してserviceへ渡す。
4. remove routeをexplicit compatibility functionへdispatchする。
5. mapperは`DistributionProcessResult`とstatic request contextだけを受けるpure functionにする。
6. summary/actions/failed/pending/errors/phase/last/retryをresultからmappingする。journalをopenしない。
7. JSONはpayload完成後にone `json.dumps`/printする。
8. textは同じresult/payloadからexisting section orderでrenderする。
9. retry policy=`same-keep-command`かつstatic specs mode=`keep`だけsafe commandを生成し、default dry-runのmode `null`、manual/noneはnullにする。normal keep resultではplanned/completed/blocked/partial/errorを問わずcommandを維持する。
10. status別target fieldをcurrent schema-v1 ruleへmappingし、blocked/partial以外を一律relative化しない。
11. default/keep service error時にlegacy routeへfallbackしない。

### focused verification

```bash
uv run pytest -q --run-full-regression --full-regression-shard tests/unit/infra/test_init_update.py -k "i370 and (cli or json or text or result or retry)"
uv run pytest -q --run-full-regression --full-regression-shard tests/cli_runtime/test_distribution_cutover.py -k "i370 and (cutover or result or uninstall)"
```

### step exit

- default/keep routeがnew serviceだけを使う。
- remove routeはD4 compatibilityだけを使う。
- public schema/text/exit semanticsがgolden一致する。
- CLI journal interpretation、dual writer、hidden fallbackがない。
- `I370-T-RESULT-001`がpassする。

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
- `I370-T-ABS-001`: CLI mapperが`OperationJournalStore`、`.distribution-journal.json`、forward guard、checkpointを読まず、`DistributionProcessResult`とstatic request contextだけを入力にする。
- `I370-T-ABS-001`: remove-specs compatibility routeだけがD4-owned legacy helperを参照する。shared helperの削除はcall graphでunusedを証明した場合だけ行う。
- `I370-T-DOC-001`: provider docsとdogfood docsのbytes/meaning parity。
- `I370-T-DOC-001`: docsがsingle generated-state authority、current/legacy境界、surviving-anchor collapsed no-op、immediate-child directory subsumption、type-specific directory semantic digest、semantic source compatible recovery、reachable journal state machine、typed result-only mapper、legacy marker fail-closed、keep/remove owner boundary、same-plan retryを記載。

### implementation

1. default/keep routeからlegacy plan/apply/postverify/marker/remove helperへのcall edgeを物理削除する。
2. helper自体がremove-specs compatibility routeからもunusedなら削除する。D4-owned callerが残るhelperは名前とcommentでcompatibility ownershipを明示し、本Issue serviceから到達不能にする。
3. `_UninstallTargetIdentity` / `_UninstallAction`のうちdefault/keep mutation authorityとして不要になったfield/typeを除去する。remove-specs routeが使用する部分はD4 handoff一覧に残す。
4. source/AST absence testでstring commentではなくactual function source/call dependencyを確認する。
5. CLI presentation adapterからjournal/guard parserへのimport、path read、checkpoint解釈を除去し、serviceが返す`DistributionProcessResult`とstatic request contextだけをmapperへ渡す。
6. READMEとshipped/dogfood docsを次へ更新する。
   - default/keep dry-runはread-only assessment
   - `spec-dock/active` / `spec-dock/.agent`はsingle canonical producerがcurrent identityを証明したslotだけを削除し、legacy/unrecognized/conflictはblockする
   - proven-owned ancestorが既にabsentならdescendant actionを発行せずcollapsed absence witnessとして扱い、entire managed subtree absent applyはprotocol metadata write 0のcompleted no-opになる
   - apply keepは`.distribution-retry.json` schema-2 guard + `.distribution-journal.json`
   - directory removalはprior child `published` + exact expected-absentへ依存し、`verifying`成功後のatomic terminal publicationで`verified` / `completed`へ進む
   - same root/intent/authority/contract/plan/protocolでforward recovery
   - public phase、last completed phase、failed/pending path、action/top-level errorはtyped service resultから生成し、CLIはjournalを解釈しない
   - legacy `.uninstall-retry.json`は自動変換しない
   - `--remove-specs`はseparate explicit authority / Issue 371 compatibility owner
   - unknown/modified contentとspec historyを保持
7. docsに未実行testやIssue 369のfull-regression結果を本Issue successとして書かない。

### focused verification

```bash
uv run pytest -q tests/unit/infra/test_managed_distribution.py -k "i370 and absence"
uv run pytest -q --run-full-regression --full-regression-shard tests/unit/infra/test_init_update.py -k "i370 and (absence or docs or uninstall)"
uv run pytest -q --run-full-regression --full-regression-shard tests/cli_runtime/test_distribution_cutover.py -k "i370 and cutover"
./spec-dock/scripts/spec-dock validate
```

### step exit

- default/keep routeにlegacy fallbackがない。
- CLI adapterがjournal/guard/checkpointを解釈せず、typed service resultだけからpublic outputを生成する。
- remove-specs compatibility seamの残存symbol/caller一覧がIssue 371 handoffとして確定する。
- shipped/dogfood docsがsingle generated authority、absence collapse、checkpoint state machine、typed result populationを含むimplementationと一致する。

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
  --timeout-seconds 1200 \
  --max-total-seconds 1800 \
  --shards 4
```

成功条件:

- verifier exit 0
- all collected node coverageに欠落/重複なし
- approved failure ledgerのnode IDとsignatureがexact一致
- unexpected failure/error 0
- Issue 370 attributable new failure 0

600秒は、Issue 369で発生した4時間超の改善を測る暫定的なperformance targetであり、Issue 370のhard pass/fail deadlineではない。candidate-wide runが600秒を超えても、上記のbounded execution window内に完走し、coverage・ledger・unexpected failure/error・Issue 370 attributable failureの条件を満たせば合格とする。実測total elapsedはReportへ記録し、600秒超過はadvisory performance follow-upとして分類する。設定したhard boundで終了した場合は未完了として扱い、完走できる十分なboundで再実行する。

Issue 369 Reportの27 approved failures、件数、時間をcurrent resultとして流用しない。600秒というadvisory boundを超えただけではtimeout扱いにせず、選択した最終hard boundで終了した場合、ledger mismatch、unexpected failure/errorの場合に本Issueを未完了とする。Full Regression repairまたはledger rebaselineを本Issueへ取り込まず、attributable failureを修正するかDecision Gateで停止する。

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
| N02 | removable owned asset + unknown/modified child | whole operation blocked、owned assetも不変 | I370-T-BLK-001 |
| N03 | initiatives nested bytes/mode/symlink/empty dirs | apply後byte/topology exact一致 | I370-T-PRES-001 |
| N04 | `.workbench` payload / outside sentinel | actionなし、identity/bytes不変 | I370-T-PRES-002 |
| N05 | active symlink XOR path fallback current positive | canonical generated producerがexact ownershipを発行 | I370-T-OWN-001 |
| N06 | active symlink+path併存 / escape / wrong kind/content | whole operation write 0 | I370-T-OWN-001, I370-T-BLK-001 |
| N07 | current `.agent` schema/projection outputs | semantic validation後observed SHAへbinding | I370-T-OWN-001 |
| N08 | malformed/extra/hardlinked `.agent` JSON | preserve+block、root recursive deleteなし | I370-T-OWN-001, I370-T-ID-001 |
| N09 | current-runbook / `.agent/deps*` / `.work` legacy names | historical exact identityなしではblock | I370-T-OWN-001 |
| N10 | deprovision assessmentへ二系統generated input | type/signature/source boundaryで不可能 | I370-T-OWN-001, I370-T-ABS-001 |
| N11 | fresh planにprune、deprovision planにcreate/upgrade | executable authority発行前に拒否 | I370-T-DOM-001, I370-T-PLAN-001 |
| N12 | preserve/block/already-absentをjournal action化 | parser/plan validator reject | I370-T-PLAN-001, I370-T-JRN-001 |
| N13 | purpose/intent/authority forged pair | parser/resume write 0 | I370-T-JRN-001 |
| N14 | deprovision journalを`--remove-specs`で再開 | checkpoint進行0、purge action 0 | I370-T-AUTH-001 |
| N15 | legacy marker-only / copied marker | marker/target不変、recovery required | I370-T-LEG-001 |
| N16 | malformed/symlink/hardlink/special legacy marker | public error/2、evidence保持 | I370-T-LEG-001 |
| N17 | legacy marker + new guard/journal | dual recovery、全evidence不変 | I370-T-LEG-001 |
| N18 | regular same-content別inode / mode drift / hardlink | target保持、block/recovery | I370-T-ID-001, I370-T-RACE-001 |
| N19 | symlink target change / external target | linkをfollowせず保持 | I370-T-ID-001 |
| N20 | FIFO/socket/device | guard/journal/target write 0 | I370-T-ID-001 |
| N21 | root/parent rebind |外部path不変、次mutationなし | I370-T-RACE-001 |
| N22 | proven-owned ancestor absent | one collapse witness、descendant mutation action 0 | I370-T-NOOP-001, I370-T-TREE-001 |
| N23 | unproven parent gap | actionなし、whole operation block | I370-T-NOOP-001, I370-T-BLK-001 |
| N24 | collapsed ancestor assessment後appearance | appeared entry保持、blocked/recovery required | I370-T-NOOP-001, I370-T-RACE-001 |
| N25 | entire managed subtree absent | protocol metadata/target syscall 0、completed | I370-T-NOOP-001 |
| N26 | directory dependency child pending | rmdir未実行 | I370-T-JRN-001, I370-T-KRN-001 |
| N27 | child published but target present/replaced | rmdir未実行、recovery required | I370-T-KRN-001, I370-T-RACE-001 |
| N28 | child published+exact absent、directory empty | directory action到達・published | I370-T-KRN-001, I370-T-REC-001 |
| N29 | executing+verified / verifying+pending / completed+published | strict parser reject | I370-T-JRN-001 |
| N30 | unlink/rmdir後checkpoint failure | exact postからpublishedへresume | I370-T-REC-001 |
| N31 | verifying crash | target action再実行0、post-assessment再実行 | I370-T-REC-001 |
| N32 | atomic completed publication crash | all-published verifying XOR all-verified completed | I370-T-REC-001 |
| N33 | guard/journal publish failure | managed target write 0 | I370-T-REC-001 |
| N34 | completed+guard / completed-only cleanup window | target action再実行0 | I370-T-REC-001 |
| N35 | each durable state fixture | typed phase/last/failed/pending/errors/retry exact | I370-T-RESULT-001 |
| N36 | CLI journal/store access monkeypatch raises | mapper仍成功、journal interpretation 0 | I370-T-RESULT-001, I370-T-ABS-001 |
| N37 | JSON planned/completed/blocked/recovery/error | schema v1、one stdout object | I370-T-JSON-001, I370-T-RESULT-001 |
| N38 | absolute path/content/token in internal exception | public outputへ非露出 | I370-T-TEXT-001, I370-T-RESULT-001 |
| N39 | targetにspace/leading hyphen | retryはsame keep invocation、shell-safe | I370-T-TEXT-001 |
| N40 | default/keep source call graph | legacy plan/apply/postverify/marker/remove edge 0 | I370-T-ABS-001 |
| N41 | remove-specs route | Issue 370 service call edge 0、existing behavior unchanged | I370-T-CLI-001, I370-T-AUTH-001 |
| N42 | random child creation order | same digest/collapse/public order | I370-T-TREE-001, I370-T-OPS-001 |
| N43 | required capability unavailable | first write前stable typed error | I370-T-OPS-001 |
| N44 | blocker diagnosticを含むdry-run vs同じworkspaceのapply | dry-run=`planned`/failed paths空、apply=`blocked`/blocker paths populated | I370-T-RESULT-001, I370-T-JSON-001 |
| N45 | final mutating checkpoint published後、`verifying` status write前crash | `executing` all-publishedを`post-verify`/`uninstall-applied`へmapし、target action再実行0 | I370-T-REC-001, I370-T-RESULT-001 |
| N46 | active manifest/pointer/context-pack/index-tree `active` conflict | single producerがwhole operationをwrite 0でblock | I370-T-OWN-001, I370-T-BLK-001 |
| N47 | present sync artifactsの`generated_at`不一致またはindex/tree node集合不一致 | partial current stateをownedへ昇格せずwrite 0 | I370-T-OWN-001 |
| N48 | existing fresh/recognized `DistributionProcessResult` constructor | additive default fieldsでsource/result semantics unchanged | I370-T-RESULT-001, I370-T-DOM-001 |
| N49 | prepared/executing/root-cleanupのpending action | same pathが`failed_paths`と`pending_paths`の双方にexactly once出て、recovery top-level errorが非空 | I370-T-RESULT-001, I370-T-JSON-001 |
| N50 | default dry-run、keep planned/completed/blocked/partial/error、legacy marker | current-compatible retry nullability/commandをexactに維持しpurgeへ昇格しない | I370-T-RESULT-001, I370-T-TEXT-001 |
| N51 | planned/completed/error vs blocked/partial target |前者はresolved target、後者だけrelative/unavailableへsanitization | I370-T-JSON-001, I370-T-TEXT-001 |
| N52 | planned/completed vs blocked/recovery/error |前者のtop-level errorsは空、後者はallowlisted errorが一件以上でraw exceptionを含まない | I370-T-RESULT-001, I370-T-JSON-001, I370-T-TEXT-001 |
| N53 | 3階層nested tree、leaf後に最深directory published | next ancestorはimmediate directory child published+path absentだけを使用し、descendant reopen 0 | I370-T-DIR-001, I370-T-REC-001 |
| N54 |各directory rmdir直後checkpoint crash | exact path absenceからそのdirectoryをpublishedへ再構成し、subtree subsumptionを維持してancestorへ収束 | I370-T-DIR-001, I370-T-REC-001 |
| N55 | leaf removalでparent directory ctime/link count変化 | directory semantic digestは再現可能、same-plan resume成功 | I370-T-DIR-001, I370-T-KRN-001 |
| N56 | directory child inode/type/mode replacement | semantic digest/full runtime binding mismatch、next mutation 0 | I370-T-DIR-001, I370-T-RACE-001 |
| N57 | nearest existing absence ancestorがplan内削除対象 | deletion closure外の上位surviving anchorへcanonical re-anchor | I370-T-NOOP-001, I370-T-TREE-001 |
| N58 | package A/Bが別physical install rootだがsemantic assets同一 | same contract/plan digest、Bのnew full snapshotでcompatible resume | I370-T-SRC-001, I370-T-REC-001 |
| N59 | source path/kind/bytes/mode/link target/schema drift | semantic mismatch、guard/journal/target write 0 | I370-T-SRC-001 |
| N60 | same invocation source capture後replacement | full source snapshot mismatch、次target mutation 0 | I370-T-SRC-001, I370-T-RACE-001 |
| N61 | verifyingでpublished directory配下descendant accessをtrap | trap未発火、directory summaryとremaining witnessesだけでcompletedへ進む | I370-T-DIR-001, I370-T-REC-001 |

## Requirement / Step / Test traceability

| Requirement ID | Design element | Implementation step | Verification test/evidence |
|---|---|---|---|
| I370-F01 | D370-CLI, D370-ASSESS, D370-SERVICE | P0, P5, P7 | I370-T-CLI-001, I370-T-DRY-001, I370-T-JRN-001 |
| I370-F02 | D370-ASSESS, D370-SERVICE, D370-RESULT | P0, P5 | I370-T-DRY-001, I370-T-RESULT-001 |
| I370-F03 | D370-CONTRACT, D370-ASSESS, D370-PLAN, D370-KERNEL | P0, P2, P3, P4 | I370-T-OWN-001, I370-T-PLAN-001, I370-T-KRN-001 |
| I370-F04 | D370-DATA, D370-ASSESS, D370-SERVICE | P2, P6 | I370-T-PRES-001, I370-T-REC-001 |
| I370-F05 | D370-DATA, D370-ASSESS | P2, P6 | I370-T-PRES-002 |
| I370-F06 | D370-ASSESS, D370-PLAN, D370-SERVICE | P0, P2, P5 | I370-T-BLK-001 |
| I370-F07 | D370-INT, D370-CONTRACT, D370-LEGACY | P1, P3, P7 | I370-T-AUTH-001 |
| I370-F08 | D370-DATA, D370-SERVICE, D370-JOURNAL | P2, P3, P6 | I370-T-PRES-001, I370-T-NOOP-001, I370-T-REC-001 |
| I370-F09 | D370-DATA, D370-ASSESS, D370-PLAN, D370-SERVICE | P2, P3, P5, P6 | I370-T-NOOP-001, I370-T-TREE-001, I370-T-RACE-001, I370-T-DIR-001 |
| I370-F10 | D370-CLI, D370-MIG | P0, P7, P9 | I370-T-CLI-001, I370-T-ABS-001 |
| I370-S01 | D370-CLI, D370-SERVICE, D370-KERNEL | P4, P6 | I370-T-RACE-001 |
| I370-S02 | D370-DATA, D370-KERNEL | P2, P4 | I370-T-ID-001, I370-T-RACE-001 |
| I370-S03 | D370-DATA, D370-KERNEL | P2, P4 | I370-T-ID-001 |
| I370-S04 | D370-DATA, D370-KERNEL | P2, P4 | I370-T-ID-001 |
| I370-S05 | D370-DATA, D370-ASSESS | P2, P4 | I370-T-ID-001 |
| I370-S06 | D370-CONTRACT, D370-ASSESS | P0, P2 | I370-T-OWN-001, I370-T-BLK-001 |
| I370-S07 | D370-CONTRACT, D370-ASSESS, D370-PLAN | P2, P3 | I370-T-TREE-001, I370-T-PLAN-001 |
| I370-S08 | D370-PLAN, D370-JOURNAL, D370-KERNEL, D370-MIG | P3, P4, P6, P9 | I370-T-JRN-001, I370-T-KRN-001, I370-T-DIR-001, I370-T-REC-001, I370-T-ABS-001 |
| I370-S09 | D370-DATA, D370-KERNEL, D370-JOURNAL | P2, P3, P4, P6 | I370-T-DIR-001, I370-T-KRN-001, I370-T-RACE-001, I370-T-REC-001 |
| I370-S10 | D370-DATA, D370-PLAN, D370-JOURNAL, D370-SERVICE | P2, P3, P6 | I370-T-PRES-001, I370-T-NOOP-001, I370-T-JRN-001 |
| I370-S11 | D370-CONTRACT, D370-PLAN, D370-SERVICE, D370-JOURNAL | P2, P3, P6 | I370-T-SRC-001, I370-T-RACE-001, I370-T-REC-001 |
| I370-S12 | D370-ASSESS, D370-SERVICE | P2, P5 | I370-T-BLK-001, I370-T-DRY-001 |
| I370-S13 | D370-CONTRACT, D370-KERNEL | P2, P4, P6 | I370-T-PRES-002, I370-T-ID-001 |
| I370-S14 | D370-DATA, D370-KERNEL, D370-JOURNAL | P2, P4, P6 | I370-T-NOOP-001, I370-T-RACE-001, I370-T-REC-001 |
| I370-S15 | D370-JOURNAL, D370-SERVICE | P6 | I370-T-REC-001 |
| I370-S16 | D370-DATA, D370-ASSESS, D370-SERVICE, D370-RESULT | P2, P5 | I370-T-NOOP-001, I370-T-RESULT-001 |
| I370-C01 | D370-CLI, D370-MAP | P0, P7 | I370-T-CLI-001 |
| I370-C02 | D370-RESULT, D370-MAP | P0, P7 | I370-T-CHAR-001, I370-T-JSON-001, I370-T-RESULT-001 |
| I370-C03 | D370-MAP | P7 | I370-T-JSON-001 |
| I370-C04 | D370-RESULT, D370-MAP | P0, P7 | I370-T-CHAR-001, I370-T-TEXT-001, I370-T-RESULT-001 |
| I370-C05 | D370-MAP | P0, P7 | I370-T-CLI-001, I370-T-TEXT-001 |
| I370-C06 | D370-RESULT, D370-MAP | P6, P7 | I370-T-TEXT-001, I370-T-RESULT-001 |
| I370-C07 | D370-RESULT, D370-MAP, D370-LEGACY | P7, P8 | I370-T-TEXT-001, I370-T-LEG-001, I370-T-RESULT-001 |
| I370-C08 | D370-MIG, D370-MAP | P9, P10 | I370-T-DOC-001, SpecDock validate |
| I370-C09 | D370-RESULT, D370-MAP, D370-CLI | P0, P6, P7 | I370-T-RESULT-001, I370-T-ABS-001, I370-T-JSON-001, I370-T-TEXT-001 |
| I370-R01 | D370-JOURNAL, D370-SERVICE | P3, P6 | I370-T-JRN-001, I370-T-REC-001 |
| I370-R02 | D370-INT, D370-JOURNAL | P1, P3, P6 | I370-T-JRN-001 |
| I370-R03 | D370-DATA, D370-CONTRACT, D370-JOURNAL | P2, P3, P6 | I370-T-SRC-001, I370-T-JRN-001, I370-T-AUTH-001, I370-T-REC-001 |
| I370-R04 | D370-JOURNAL, D370-DATA | P3, P4, P6 | I370-T-JRN-001, I370-T-DIR-001, I370-T-REC-001 |
| I370-R05 | D370-JOURNAL, D370-RESULT | P6 | I370-T-DIR-001, I370-T-REC-001, I370-T-RESULT-001 |
| I370-R06 | D370-DATA, D370-JOURNAL, D370-LEGACY | P3, P6 | I370-T-JRN-001, I370-T-REC-001 |
| I370-R07 | D370-LEGACY, D370-RESULT | P0, P8 | I370-T-LEG-001, I370-T-RESULT-001 |
| I370-R08 | D370-INT, D370-CLI, D370-LEGACY | P1, P7, P8 | I370-T-AUTH-001 |
| I370-R09 | D370-JOURNAL, D370-SERVICE, D370-KERNEL | P3, P4, P6 | I370-T-JRN-001, I370-T-KRN-001, I370-T-DIR-001, I370-T-REC-001 |
| I370-R10 | D370-RESULT, D370-MAP, D370-LEGACY | P6, P7, P8 | I370-T-RESULT-001, I370-T-TEXT-001, I370-T-LEG-001 |
| I370-O01 | D370-CONTRACT, D370-ASSESS | P2 | I370-T-OPS-001 |
| I370-O02 | D370-DATA, D370-CONTRACT, D370-PLAN, D370-MAP | P2, P3, P7 | I370-T-TREE-001, I370-T-DIR-001, I370-T-SRC-001, I370-T-OPS-001, I370-T-JSON-001 |
| I370-O03 | D370-PLAT, D370-KERNEL | P4, P5, P10 | I370-T-OPS-001, Linux/Darwin focused evidence |
| I370-O04 | D370-JOURNAL, D370-RESULT, D370-MAP, D370-PLAT | P3, P6, P7, P10 | I370-T-JRN-001, I370-T-RESULT-001, I370-T-JSON-001, I370-T-TEXT-001 |

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

| Gate | Stop condition |必要evidence |
|---|---|---|
| DG-01 Generated producer | fixed SHAのruntime outputがDesignのcurrent slot/schema/semantic predicateと矛盾する、またはdeprovisionへ二系統inputが必要 | exact path、producer symbol、real output fixture、conflicting contract |
| DG-02 Generated identity | current generated JSONをsemanticに証明できずpathnameだけで削除する必要がある | observed bytes/schema、validator gap、historical evidence有無 |
| DG-03 Ownership | unknown/modified/legacy-unproven entryを削除しなければacceptanceを満たせない | exact path、observation、authority source、preservation impact |
| DG-04 Journal witness | protocol-2 schemaへpreservation/absence witnessまたはdependencyをlosslessに保存できない | current parser/serializer fields、round-trip counterexample |
| DG-05 State reachability | immediate child evidenceとpublished directory subtree subsumptionからnested directory actionを安全に実行できず、descendant再openまたはverified dependencyへ戻す必要がある | exact 3階層crash state、parser result、kernel precondition、descendant access trace |
| DG-06 Absence proof | deletion closure外のsurviving bound ancestorへcanonical re-anchorしてowned subtree absenceを証明できず、削除対象anchorまたはunproven gapをtrustする必要がある | path tree、action closure、anchor candidates、binding failure |
| DG-07 Source identity | durable semantic source projectionだけではsame-plan compatible newer recoveryを再構成できず、physical device/inode/ctime/mtimeをguard/journal equalityへ保存する必要がある | semantic counterexample、package A/B fixture、current source snapshot behavior |
| DG-08 Typed result | resultだけからphase/last/failed/pending/action/top errors/retryを一意に生成できない | missing field、durable states with same result、public compatibility impact |
| DG-09 Legacy conversion | `.uninstall-retry.json`自動変換が必要 | exact marker bytes、injectivity proof、negative counterexample |
| DG-10 Purge boundary | remove-specs behavior/authorityを変更しなければroute splitできない | caller graph、current public behavior、Issue 371 impact |
| DG-11 Public compatibility | schema key/version/exit/text order変更が必要 | exact golden conflict、consumer impact |
| DG-12 Platform | Linux/Darwinの一方でwrite-before-capability-checkが避けられない | platform、capability、first-write trace |
| DG-13 Hidden fallback | default/keep routeからlegacy writer/remove helperまたはCLI journal interpretationを除去できない | exact caller/callee、remaining ownership、D4 boundary |

Decision Gateをtemporary workaround、compatibility fallback、test expectation緩和、legacy pathname ownership、Issue 371/372への責務先送りで通過してはならない。

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
- stored durable semantic source projectionとcurrent packageから再構成したsemantic projectionのexact一致
- current invocation内で新規captureしたfull source snapshotの安定性

を全て満たすcompatible newer packageだけがcheckpointを進める。physical install-rootのdevice/inode/ctime/mtime差だけでは拒否しない。completed actionをrollbackしない。mismatch、unknown child、replacement、legacy marker、purge invocationはwrite 0で停止する。

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
2. Requirementの49 IDが本PlanのDesign element、step、stable testへtraceされる。
3. default/keep dry-runがsingle generated-state producerを含むread-only new assessmentを使用する。
4. active/.agentのcurrent positive、legacy、unknown、conflict matrixがexact runtime producer fixtureでpassする。
5. mutating keep applyがschema-2 guard、protocol-2 journal、common kernel、post-assessmentを使用する。
6. 3階層以上のdirectory actionがimmediate child evidenceから到達し、leaf/directory child kind、published directory subtree subsumption、prepared/executing/verifying/completed parser table、各directory publish直後crash windowがpassする。
7. preserve/blockはjournal actionでなくimmutable witness/diagnosticであり、到達不能checkpointがない。
8. proven-owned ancestor absenceがdescendant actionなしでcollapseされ、削除対象anchorは上位surviving ancestorへre-anchorされ、entire managed subtree absent applyがprotocol metadata/target write 0でcompletedになる。
9. directory semantic projectionがauthorized parent ctime/link-count変化で再現でき、directory inode/type/mode replacement、absence appearance、unknown child、same-content replacement、root/parent raceをfail closedで保持する。
10. durable source equalityがsemantic projectionへ限定され、semantic-equalな別physical install rootのcompatible newer resume、semantic drift rejection、same-invocation full snapshot replacement rejectionがpassする。
11. initiatives byte identity、Workbench、outside sentinel、unknown/modified/generated conflictが保持される。
12. legacy markerを自動変換せず、marker/targetを保持する。
13. deprovision/purge authority switchが全routeで拒否される。
14. typed `DistributionProcessResult`または同等inputだけでphase、last completed、failed/pending paths、per-action error、top-level errors、retry policyを生成でき、pending pathのfailed/pending両field出現を含めてCLI journal interpretationがsource/monkeypatch testで0である。
15. public schema v1、one stdout object、text、exit、status別target sanitization、normal keep/legacy retry nullabilityがgoldenに一致する。
16. default/keep routeからlegacy plan/apply/postverify/marker/remove fallbackが物理的に除去される。
17. focused、fast、lint、validate、diff check、candidate full regressionが所定条件を満たす。
18. 未実行test、policy skip、Issue 369 evidenceをIssue 370 successとしてReportへ記録しない。
19. coderがDecision Gateを推測で通過していない。
20. Issue 371 purgeとIssue 372 parity/closureの責務を本Issueへ混入させていない。
