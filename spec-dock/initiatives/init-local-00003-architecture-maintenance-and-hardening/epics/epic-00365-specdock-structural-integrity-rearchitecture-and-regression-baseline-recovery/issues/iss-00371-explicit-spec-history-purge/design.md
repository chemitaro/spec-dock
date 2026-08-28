---
種別: 設計書（Issue）
ID: "iss-00371"
タイトル: "Explicit Spec History Purge"
関連GitHub: ["#371"]
状態: "planned"
最終更新: "2026-08-28"
依存: ["requirement.md"]
親: ["epic-00365", "init-local-00003"]
---

# iss-00371 Explicit Spec History Purge — 設計

詳細: [Design Guide](../../../../../../docs/authoring/design.md)

## 1. 設計結論

Issue 371 は新しい purge engine を作らない。exact verified revision `94546a138bd34b253c87ca8749f3c5678d172f2a` に存在する Issue 370 の destructively safe seamへ、別 intent・別 authority・別 contract・別 recovery discriminatorとして explicit spec history purgeを追加する。

選択する構成は次である。

```text
public CLI
  uninstall --remove-specs [--apply]
        |
        v
_run_uninstall_explicit_spec_history_purge
        |
        v
execute_explicit_spec_history_purge_distribution
        |
        v
_build / assess exact purge contract
  - Issue 370 deprovision component
  - exact history root: spec-dock/initiatives
  - preserved root: spec-dock/.workbench
        |
        v
WorkspaceAssessment(intent="purge")
        |
        v
ExecutableMutationPlan
        |
        v
OperationJournalStore
  .distribution-retry.json schema 2 guard
  .distribution-journal.json schema 1 / protocol 2
        |
        v
existing descriptor-bound action kernel
  regular prune
  remove-empty-directory
        |
        v
DistributionProcessResult(intent="purge")
        |
        v
existing public uninstall JSON/text/exit mapper
```

hard cutover後、remove-specs mutation の writer は上記一系統だけである。`_run_uninstall_remove_specs_compatibility()`、`_build_uninstall_plan()`、`_apply_uninstall_plan()`、CLI recursive remover、`.uninstall-retry.json` writerは削除する。legacy markerのread-only detectionとambiguity rejectionは`managed_distribution.py`に残す。

## 2. Current exact implementation seams

### 2.1 Current common model

`src/spec_dock/managed_distribution.py` には次が既に存在する。

```python
DistributionOperation = Literal["fresh", "update", "init-force", "uninstall"]
JournaledDistributionIntent = Literal["fresh", "update", "init-force", "deprovision"]
DistributionActionName = Literal[
    "create",
    "adopt",
    "upgrade",
    "prune",
    "preserve",
    "block",
    "ensure-directory",
    "remove-empty-directory",
]
```

共通 model / service seam は次である。

- `DistributionAction`
- `DistributionPlan`
- `WorkspaceAssessment`
- `ExecutableMutationPlan`
- `OperationJournalAction`
- `OperationJournal`
- `OperationJournalStore`
- `DistributionRetryMarker`
- `DistributionProcessResult`
- `build_executable_mutation_plan()`
- `_execute_journaled_action()`
- `_remove_distribution_target_if_bound()`
- `_remove_distribution_directory_if_bound()`

Issue 370 の deprovision seam は次である。

- `DistributionDeprovisionContract`
- `build_deprovision_generated_state_contract()`
- `build_deprovision_contract()`
- `build_deprovision_workspace_assessment()`
- `execute_deprovision_distribution()`
- `_deprovision_action_conditions()`
- `_validate_deprovision_recovery_action_semantics()`
- deprovision recoveryのroot/parent/leaf/directory validators

`OperationJournal` は既に `intent`、`authority`、`contract_identity`、`plan_digest`、action pre/postconditions、checkpoint、staging leases、preservation/absence witnessesを保持する。`DistributionProcessResult` はpublic mapper入力であり、authorityやjournal bytesを公開しない。

### 2.2 Current journal files

current filesとversionを維持する。

| path | current role | Issue 371 |
|---|---|---|
| `spec-dock/.distribution-retry.json` | schema version 2 forward guard | purge用purpose/operation discriminatorを既存field shapeへ追加する。 |
| `spec-dock/.distribution-journal.json` | schema version 1 / protocol version 2 common journal | purgeも同じschema/protocolを使用する。 |
| `spec-dock/.uninstall-retry.json` | legacy three-field uninstall marker | writerを削除する。readerはambiguity detectionのため維持する。purgeへ変換しない。 |

### 2.3 Current CLI split

`src/spec_dock/cli.py` のcurrent routeは次である。

- default/keep: `_run_uninstall_deprovision()` → `execute_deprovision_distribution()` → `_emit_uninstall_deprovision_result()`
- remove: `_run_uninstall_remove_specs_compatibility()` → `_build_uninstall_plan()` → `_write_uninstall_retry_marker()` → `_apply_uninstall_plan()` → `_verify_uninstall_postcondition()` → `_finalize_uninstall_retry_marker()`

current public mapperとして維持するseamは次である。

- `_uninstall_payload_from_result()`
- `_validate_uninstall_process_result()`
- `_uninstall_exit_code_from_result()`
- `_summarize_uninstall_outcomes()`
- `_uninstall_guidance_from_result()`
- `_render_uninstall_text()`

current remove routeだけがtyped result mapperを使用しておらず、本Issueはこの最後のlegacy routeをcutoverする。

## 3. Internal intent、authority、guard discriminator

### 3.1 Intent domain

`JournaledDistributionIntent` にexact literal `"purge"`を追加する。

```python
JournaledDistributionIntent = Literal[
    "fresh",
    "update",
    "init-force",
    "deprovision",
    "purge",
]
```

`DistributionOperation` は変更しない。purgeのfilesystem action grammarはuninstallと同じため、`_plan_operation_for_intent("purge")` は `"uninstall"` を返す。

`_intent_allows_distribution_action()` は `purge` に対して `prune`、`preserve`、`block`、`remove-empty-directory` だけを許可する。`create`、`adopt`、`upgrade`、`ensure-directory` はpurge executable planで拒否する。

### 3.2 Fixed authority

purge authorityはcaller inputにしない。`_journal_authority_for_intent("purge")` が常にexact stringを返す。

```text
explicit-spec-history-purge
```

public CLI、JSON、marker、retry commandから任意authorityを渡すAPIは作らない。`execute_explicit_spec_history_purge_distribution()` が `intent="purge"` を固定し、authorityは既存mappingから一意に導出する。

### 3.3 Forward guard purpose

既存 guard schema version 2 のfield setを変更せず、purpose discriminatorを一つ追加する。

```python
_DISTRIBUTION_PURGE_JOURNAL_GUARD_PURPOSE = "purge-journal-forward-only"
```

`_DISTRIBUTION_JOURNAL_AUTHORITIES` に次を追加する。

```text
purge-journal-forward-only -> explicit-spec-history-purge
```

`_read_distribution_retry_marker()` は次をexactに検証する。

- `operation="purge"` は purpose=`purge-journal-forward-only` のschema-2 guardだけで有効。
- deprovision purpose + purge operation、purge purpose + deprovision operationは`marker-invalid`。
- schema version、field set、root identity、operation ID、contract identity、plan digest、journal anchorの既存validationを維持する。
- legacy schema-1 distribution retry markerや`.uninstall-retry.json`からpurge operationを作らない。

### 3.4 Retry policy

internal `DistributionRetryPolicy` にexact literal `"same-remove-command"` を追加する。

- purge dry-run: applyを要求するguidance。retry commandは作らない。
- purge applyのsame-plan recovery: `same-remove-command`。
- legacy marker、dual state、authority/plan ambiguity: `manual-recovery`。
- default/keep:既存 `same-keep-command` を変更しない。

## 4. Purge contract

### 4.1 New data type

`src/spec_dock/managed_distribution.py` に次のinternal dataclassを追加する。

```python
@dataclass(frozen=True)
class DistributionExplicitSpecHistoryPurgeContract:
    deprovision_contract: DistributionDeprovisionContract
    history_root: str
    history_root_binding: PathIdentitySnapshot
    history_entries: tuple[DistributionTreeEntrySnapshot, ...]
    history_tree_digest: str
    authority: str
    contract_digest: str
```

builderは次を固定し、外部から変更可能にしない。

```text
history_root = "spec-dock/initiatives"
authority = "explicit-spec-history-purge"
deprovision_contract.preserved_roots = ("spec-dock/.workbench",)
```

`history_entries` はhistory root以下のreal directoryとsingle-link regular fileのno-follow snapshotである。symlink、multi-link regular、special、unreadable/rebound entryはcontract entryにせずblockerにする。

### 4.2 Existing deprovision contractの再利用

current `build_deprovision_contract()` のpublic signatureとdeprovision behaviorを変更しない。bodyのうち preserved rootsだけを選択する部分をprivate factoryへ抽出する。

```python
def _build_deprovision_contract(
    ...,
    preserved_roots: tuple[str, ...],
    recovery_journal: OperationJournal | None = None,
) -> DistributionDeprovisionContract:
    ...
```

呼び分けはinternal fixed valuesだけで行う。

- `build_deprovision_contract()` → `("spec-dock/initiatives", "spec-dock/.workbench")`
- `build_explicit_spec_history_purge_contract()` → `("spec-dock/.workbench",)`

この抽出はdeprovision ownership、generated-state producer、physical source contract、managed roots、manifest semanticsを変更しない。caller-supplied purge rootsやgeneric preservation policyは公開しない。

### 4.3 New contract builder

追加するexact symbolは次である。

```python
def build_explicit_spec_history_purge_contract(
    install_root: Path,
    *,
    manifest_path: Path,
    scaffold_root: Path,
    target_root: Path,
    expected_root_identity: DistributionRootIdentity,
    recovery_journal: OperationJournal | None = None,
) -> DistributionExplicitSpecHistoryPurgeContract:
    ...
```

責務は次に限定する。

1. target root identityをexact再検証する。
2. `.workbench`だけをpreserveするdeprovision component contractを構築する。
3. exact history rootをno-followで捕捉する。
4. initial applyではcurrent treeからhistory entries/digestを作る。
5. same-plan recoveryではpurge journal preconditionsから既削除entryを再構成し、present pending entryとjournal evidenceを照合する。
6. canonical contract digestを計算する。

### 4.4 Tree capture seam

current `_capture_preservation_witness()` のdescriptor-bound recursive walkを複製しない。nested walkをprivate helperへ抽出し、preservationとpurge双方が使用する。

```python
def _capture_distribution_tree(
    target_root: Path,
    relative_root: str,
    *,
    reject_symlinks: bool,
    require_single_link_regulars: bool,
) -> tuple[
    PathIdentitySnapshot,
    tuple[DistributionTreeEntrySnapshot, ...],
    str,
]:
    ...
```

purge callは次を固定する。

```text
relative_root = spec-dock/initiatives
reject_symlinks = true
require_single_link_regulars = true
```

helperは次を保証する。

- target rootとhistory rootを`O_NOFOLLOW | O_DIRECTORY`でopenする。
- visible entryとopened descriptorのdevice/inode/type/ctimeを照合する。
- regular fileは`O_NOFOLLOW`でopenし、`link_count == 1`、size、mode、SHA-256、read前後identityを固定する。
- directoryはheld fdでchild namesをbyte-order sortし、walk前後identityを固定する。
- symlinkはtargetをread/followせず即blockerとする。
- FIFO、socket、device、unknown typeを即blockerとする。
- root absentはabsent binding + empty entries + canonical digestとして表現する。

`.workbench` preservationはcurrent `_capture_preservation_witness()` behaviorを維持する。purge policyをpreservation policyへ逆流させない。

### 4.5 Contract digest

`contract_digest` はcanonical JSONをSHA-256する。payloadは次に固定する。

```text
format_version: 1
intent: purge
authority: explicit-spec-history-purge
history_root: spec-dock/initiatives
history_tree_digest: <exact digest>
deprovision_contract_digest: <component digest>
preserved_roots: [spec-dock/.workbench]
journal_protocol_version: 2
```

`history_tree_digest` はhistory root bindingと各entryのrelative path、kind、device、inode、ctime、mode、link count、size、SHA-256をcanonical orderで含む。absolute path、file bytes、provider physical pathを含めない。

plan digestは`build_executable_mutation_plan()`からjournal preparationへ渡されるcurrent canonical digest seamを使用し、`intent="purge"`、上記contract identity、action pre/postconditions、directory/absence witnessesを通じてauthorityへ束縛される。別のcaller-provided authority fieldは追加しない。

## 5. WorkspaceAssessment と action construction

### 5.1 WorkspaceAssessment extension

`WorkspaceAssessment` にadditive optional fieldを追加する。

```python
explicit_spec_history_purge_contract: (
    DistributionExplicitSpecHistoryPurgeContract | None
) = None
```

既存 fresh/update/init-force/deprovision constructorはdefault `None`で不変とする。purge assessmentだけがnon-Noneを持ち、`deprovision_contract` fieldにはcomponent contractも保持する。

### 5.2 New assessment builder

追加するexact symbolは次である。

```python
def build_explicit_spec_history_purge_assessment(
    install_root: Path,
    *,
    manifest_path: Path,
    scaffold_root: Path,
    target_root: Path,
    expected_root_identity: DistributionRootIdentity,
    recovery_journal: OperationJournal | None = None,
) -> WorkspaceAssessment:
    ...
```

処理順を固定する。

1. legacy/new recovery stateのread-only admission evidenceを確定する。
2. `build_explicit_spec_history_purge_contract()` を呼ぶ。
3. component deprovision actionsをcurrent Issue 370 classifierで作る。
4. history treeからleaf prune actionsを作る。
5. history treeとcomponent treeを一度のdirectory augmentationへ渡す。
6. `.workbench` preservation witnessを捕捉する。
7. history absence witnessを含むcollapsed absence witnessesを構築する。
8. component blockers、history blockers、preservation blockersを統合する。
9. `WorkspaceAssessment(intent="purge", ...)` を返す。

### 5.3 History leaf actions

history root内の各regular entryに次のinternal actionを一件作る。

```text
operation: uninstall
action: prune
provenance: unknown
reason: explicit-spec-history-purge
blocked: false
```

`provenance="unknown"` はownership不足を意味しない。history contentのbytes/name catalogではなく、explicit root authorityが削除根拠だからである。`purge` intent以外でこのreason/provenance pairをexecutableにしてはならない。

preconditionはexisting action condition shapeに次を含める。

- root binding
- full parent bindings
- target exists/device/inode/ctime/type/link count
- mode
- size
- regular SHA-256 identity

postconditionはexact absentである。

### 5.4 Directory actions

history rootを含む各directoryに `remove-empty-directory` actionを作る。

```text
operation: uninstall
action: remove-empty-directory
provenance: unknown
reason: explicit-spec-history-purge-directory
```

各 `DistributionDirectoryMutationSnapshot` は次を持つ。

- initial directory binding
- initial child semantic digest
- immediate child evidence
- each child action path
- required child checkpoint=`published`
- expected child postcondition=`exists: false`
- expected remaining child digest=empty digest

orderはdepth descending、同depthは`os.fsencode` canonical orderとする。history root directoryの後、component actionsの結果`spec-dock`がexact emptyの場合だけparent cleanupを続ける。

### 5.5 Integration with current tree augmentation

current deprovision tree augmentationへ、history actionsを別recursive engineとして後付けしない。private augmentation seamにexact additive inputを追加する。

```text
additional_managed_roots = ("spec-dock/initiatives",)
additional_actions = history leaf/directory actions
additional_target_snapshots = history snapshots
```

existing deprovision callはempty defaultを使いbehavior不変とする。combined action mapを作ってからdirectory evidenceを捕捉するため、`spec-dock` parentは`initiatives`をunknown childではなくexplicitly authorized childとして認識する。一方、他のunknown siblingは従来どおり preserve-and-blockとなる。

### 5.6 Absence

history rootがinitial assessmentでabsentの場合、history mutating actionは0件とする。`DistributionCollapsedAbsenceWitness` をexact `spec-dock/initiatives`へ作り、nearest surviving bound ancestorとmissing suffixへ束縛する。

- dry-run: public `spec_history` actionを出さない。
- apply no-op: history部分は`already_removed`として集約可能だがtarget writeは0。
- assessment後appearance: pre-first-writeならblocked、journal開始後ならrecovery required。appearanceしたcontentへ新しいactionを発行しない。

## 6. Blocker semantics

blockerは全componentを統合してから判定する。次の一件でも存在すれば `build_executable_mutation_plan()` を呼ばず、guard/journal/stage/target writeを0にする。

### 6.1 History blockers

- history root symlinkまたはnon-directory
- descendant symlink
- hard-linked regular file
- FIFO/socket/device/unknown type
- unreadable root/entry/content
- path non-canonical、absolute、`..`、root escape
- root/parent/entry rebind during observation
- regular read前後のdevice/inode/ctime/size/link-count drift
- duplicate/colliding action path
- directory inventoryとaction graphの不一致

### 6.2 Component blockers

Issue 370のexisting blockersをそのまま使用する。

- unknown/modified current managed collision
- legacy generated identity unproven
- current mode mismatch
- unsafe hardlink/symlink/special
- unknown child under managed cleanup root
- preservation witness failure
- source semantic drift

history treeが安全でもcomponent blockerがあればhistoryを削除しない。componentが安全でもhistory blockerがあればmanaged toolingを削除しない。

### 6.3 Recovery-state blockers

- valid `.uninstall-retry.json`: `legacy-marker-unconvertible`
- invalid legacy marker: `legacy-marker-invalid`
- legacy marker + distribution guard/journal: `dual-recovery-state`
- deprovision guard/journal on purge invocation
- purge guard/journal on deprovision/update/init invocation
- root/intent/authority/contract/plan/protocol mismatch
- nonterminal journal without matching guard
- guard-only state whose plan cannot be reconstructed exactly

## 7. Executable plan と journal action conditions

### 7.1 Common plan

`build_executable_mutation_plan()` を再利用する。purge固有plan classを作らない。validationを次へ拡張する。

- `assessment.intent == "purge"`
- `assessment.explicit_spec_history_purge_contract is not None`
- blocker 0
- action operationはall `uninstall`
- allowed action grammarは`prune` / `remove-empty-directory`
- history actionsはexact root配下、exact reason/provenance pair
- component actionsはexisting deprovision semantics
- action pathsはcanonical unique order
- directory dependenciesはacyclicでchild published先行

### 7.2 Action condition builder

current `_deprovision_action_conditions()` のcondition shapeを再利用する。実装はprivate common bodyへ抽出し、deprovision/purge wrapperを持つ。

```python
def _destructive_action_conditions(...): ...
def _deprovision_action_conditions(...): ...
def _purge_action_conditions(...): ...
```

purge wrapperはhistory actionについてregular mode/size/SHA、directory child evidenceを必須にする。component actionはexisting deprovision wrapperと同じconditionを生成する。schema fieldを追加しない。

### 7.3 Journal authority binding

`OperationJournalStore.prepare()` が記録するfield shapeを変更しない。purge journalの値だけを次へ固定する。

```text
intent = purge
authority = explicit-spec-history-purge
contract_identity = purge contract digest
plan_digest = canonical executable plan digest
protocol_version = 2
```

journal actionはpublic aggregateではなく、leaf/directory単位のexact actionを持つ。これによりpartial subtree deletionをmonotonic checkpointで回復できる。

## 8. Mutation kernel

### 8.1 Single writer

purge actionはexisting `_execute_journaled_action()` へ渡す。CLIの`os.unlink`、`os.rmdir`、`os.walk`、recursive removerを使用しない。

- regular `prune`: existing descriptor-bound regular prune pathと `_remove_distribution_target_if_bound()` を使用する。
- directory `remove-empty-directory`: `_remove_distribution_directory_if_bound()` を使用する。
- history symlink actionは生成しない。symlinkはpre-write blockerである。

### 8.2 First mutation boundary

apply順序は次である。

1. exclusive operation lock取得
2. root identity binding
3. legacy/new recovery admission
4. complete read-only assessment
5. blocker統合
6. executable plan生成
7. forward guard durable write
8. journal durable prepare
9. first target mutation

step 7または8が失敗した場合、target mutationは0。first target mutation後はjournal/guardを消してerrorを隠さず、safe recovery evidenceとして保持する。

### 8.3 Root/parent/child revalidation

各regular prune直前に次を再検証する。

- visible target rootとheld root descriptorのdevice/inode/type
- journal root identity
- each visible parentとheld parent descriptor
- parent bindings from action precondition
- target visible identityとheld fd identity
- `link_count == 1`
- mode/size/SHA/ctime precondition
- current guardとjournal anchor

各directory removal直前に次を再検証する。

- root/parent/directoryのdevice/inode/type/mode continuity
- current visible pathとheld descriptorのfull identity一致
- journal action checkpoint
- immediate child actionsが`published`
- each expected childがabsent
- directory semantic child digestがexpected empty
- authorized child mutationで変わるparent/directoryの`ctime`と`link_count`はinitial digestと直接比較せず、published checkpointから導くexpected namespace transitionとcurrent visible/held identity一致で検証
- `os.listdir(held_fd)` がempty
- visible directoryとheld directoryが同一

mutation後はexpected absentとroot/parentsを再検証し、durable checkpointを更新する。

### 8.4 Unknown appearance

assessment後にhistory root内へunknown childが出現した場合、そのentryはexplicit invocation時に観測されていないためcurrent plan authorityを持たない。directory digest/namespace evidence mismatchとして停止し、新規actionを追加しない。同じcommandを再実行してもnonterminal journalが存在する限りplanを差し替えず、matching recoveryまたはmanual resolutionを要求する。

## 9. Recovery design

### 9.1 Current recovery compatibility gate

current `_assess_operation_journal_compatibility()`、guard/journal anchoring、package compatibilityを維持し、`purge` literalを追加する。次がすべて一致する場合だけresumeする。

- root identity
- workspace identity
- intent=`purge`
- authority=`explicit-spec-history-purge`
- guard purpose=`purge-journal-forward-only`
- contract identity
- canonical plan digest
- journal protocol version 2
- compatible package policy
- explicit current CLI request=`--apply --remove-specs`

### 9.2 Recovery contract reconstruction

partial purge後はhistory entriesの一部が既にabsentであるため、current filesystemだけからoriginal planを再生成してはならない。recovery builderはjournalをdurable sourceとして使用する。

追加するprivate seamは次である。

```python
def _reconstruct_explicit_spec_history_purge_contract(
    target_root: Path,
    *,
    deprovision_contract: DistributionDeprovisionContract,
    journal: OperationJournal,
) -> DistributionExplicitSpecHistoryPurgeContract:
    ...
```

検証規則は次である。

1. journal intent/authority/root/contract/planがpurge guardと一致する。
2. history actionはexact `spec-dock/initiatives`配下だけである。
3. leafは`prune` + `explicit-spec-history-purge`、directoryは`remove-empty-directory` + `explicit-spec-history-purge-directory`だけである。
4. duplicate、ancestor escape、action grammar mismatchを拒否する。
5. preconditionsからoriginal regular/directory snapshotsをlosslessに再構成する。
6. `published` actionはexpected absentを再観測する。
7. `pending` actionはexact precondition、既存 common transition lease、またはjournalが認めるinterrupted prune状態のいずれかだけを受理する。
8. directory child evidenceがjournal action graphと一致する。
9. reconstructed tree digestとpurge contract digestがjournal値に一致する。
10. current filesystemから新しいhistory entryを追加しない。

### 9.3 Recovery semantic validators

current deprovision recovery codeをcopy-pasteしない。hard-coded `intent == "deprovision"` / deprovision authority checkを、exact destructive intent引数へparameterizeするprivate bodyへ抽出する。

対象seamは少なくとも次である。

- recovery parent attachment validation
- pending leaf parent namespace validation
- leaf mutation validator
- directory mutation validator
- current guard/journal marker binding

expected authorityはcaller引数ではなく `_journal_authority_for_intent(intent)` から得る。

`_validate_deprovision_recovery_action_semantics()` はdeprovision behaviorのwrapperとして維持する。purge用に次を追加する。

```python
def _validate_explicit_spec_history_purge_recovery_action_semantics(
    target_root: Path,
    contract: DistributionExplicitSpecHistoryPurgeContract,
    journal: OperationJournal,
) -> None:
    ...
```

validatorはjournal actionsを二群へ分ける。

- history root配下: reconstructed purge contractとexact照合
- それ以外: component `DistributionDeprovisionContract` とexisting deprovision semanticsで照合

どちらにも属さないaction、history root配下のdeprovision reason、history root外のpurge reasonを拒否する。

### 9.4 Cross-intent protection

- deprovision journal + remove-specs: `recovery_required`、write0
- purge journal + default/keep: `recovery_required`、write0
- purge journal + update/init: admission block、write0
- purge guard only + different current tree: plan mismatch、write0
- purge journal + legacy marker: dual state、write0

journal/guardの存在自体はpurge authorityではない。明示的なcurrent remove commandがないrouteはpurge recovery functionへ到達しない。

### 9.5 Completion and cleanup

success時は次を順に行う。

1. each action expected postcondition再検証
2. history root absence再検証
3. component deprovision post-assessment
4. `.workbench` preservation witness再検証
5. collapsed absence witness再検証
6. authority外 sentinelがmutation action graphに存在しないことをservice invariantで確認
7. journal completed checkpoint
8. forward guard cleanup
9. terminal journal cleanup

completed journal onlyのexisting cleanup behavior、guard+journalのanchored cleanup behaviorを維持する。target actionを再実行してterminal metadataだけを消さない。

## 10. Service interface と result semantics

### 10.1 New service

追加するexact symbolとsignatureは次である。

```python
def execute_explicit_spec_history_purge_distribution(
    install_root: Path,
    *,
    manifest_path: Path,
    scaffold_root: Path,
    target_root: Path,
    package_version: str,
    apply: bool,
    expected_root_identity: DistributionRootIdentity | None = None,
) -> DistributionProcessResult:
    ...
```

signatureはcurrent `execute_deprovision_distribution()` と一致させる。callerがintent、authority、history root、journal pathを渡す引数は作らない。

### 10.2 Common orchestration

current `execute_deprovision_distribution()` のorchestration bodyをprivate `deprovision|purge`限定executorへ抽出する。

```python
def _execute_destructive_distribution(
    ...,
    intent: Literal["deprovision", "purge"],
    apply: bool,
    expected_root_identity: DistributionRootIdentity | None,
) -> DistributionProcessResult:
    ...
```

このfunctionはarbitrary strategy/callback frameworkにしない。intent二値でexact builder/validatorを選択する。

- `deprovision` → current builder/validator/contract
- `purge` → new builder/validator/contract

lock、legacy admission、guard/journal state machine、apply kernel、checkpoint、post-assessment、typed result populationは共通body一つを使用する。

### 10.3 Status and failure meaning

| service status | condition | retry policy |
|---|---|---|
| `planned` | dry-run assessment completed | `same-remove-command`をautomatic retryとしては出さず、apply guidanceのみ |
| `completed` | apply successまたはstable no-op | `none` |
| `blocked` | pre-write ownership/safety blocker | `same-remove-command`。環境修正後にfresh assessment。 |
| `recovery_required` | legacy ambiguity、journal mismatch、partial mutation | matching plan時だけ`same-remove-command`、ambiguity時`manual-recovery` |
| `error` | request/preflight/invalid evidence | `none`または`manual-recovery` |

non-success resultはexisting result invariantどおりoperation errorを少なくとも一件持つ。pending pathsはfailed pathsのsubsetとする。

### 10.4 Public action outcome aggregation

journal actionはleaf/directory単位だが、current public remove behaviorはhistory root一件である。service result構築時にhistory subtreeだけをroot outcomeへ集約する。

```text
path = spec-dock/initiatives
category = spec_history
```

public reason/statusは次に固定する。

| internal state | public status | public reason |
|---|---|---|
| dry-run、history present | `would_remove` | `explicit remove-specs mode` |
| apply completed、history present | `removed` | `explicit remove-specs mode` |
| apply、history initially absent | `already_removed` | `explicit remove-specs mode; spec history already absent` |
| history safety blocker | `preserved` | safe sanitized manual-review reason |
| partial action failureあり | `failed` | `explicit remove-specs mode` + generic public action error |
| pendingのみ | `pending` | `explicit remove-specs mode` |

priorityは`failed > pending > removed > already_removed > would_remove > preserved`。exact leaf failure/pending pathはtop-level listsへ残す。normal deprovision component outcomesはexisting projectionを変更しない。summaryはaggregated public outcomesをcountし、internal leaf countを公開しない。

## 11. CLI adapter and mapper

### 11.1 New adapter

`src/spec_dock/cli.py` に次を追加する。

```python
def _run_uninstall_explicit_spec_history_purge(
    target_root: Path,
    ns: argparse.Namespace,
    *,
    specs_mode: str,
    expected_root_identity: DistributionRootIdentity | None = None,
) -> int:
    ...
```

invariant:

- `specs_mode == "remove"` 以外はRuntimeError。
- dry-runはlockなしでservice `apply=False`。
- applyは `_exclusive_distribution_operation()` で取得したroot identityを渡す。
- packaged assetsはcurrent `_assets_dir()`、`managed_distribution.json`、`spec_dock`を使用する。
- CLIはjournal/guard/legacy markerをreadしない。

### 11.2 Dispatch

`_run_uninstall()` のdispatchを次へ固定する。

| request | adapter |
|---|---|
| default dry-run | `_run_uninstall_deprovision()` |
| `--keep-specs` dry-run | `_run_uninstall_deprovision()` |
| `--apply` modeなし | existing deprovision request error |
| `--apply --keep-specs` | lock → `_run_uninstall_deprovision()` |
| `--remove-specs` dry-run | `_run_uninstall_explicit_spec_history_purge()` |
| `--apply --remove-specs` | lock → `_run_uninstall_explicit_spec_history_purge()` |

argparse grammar、help flags、mutual exclusionは変更しない。

### 11.3 Result mapper

`_emit_uninstall_deprovision_result()` は `_emit_uninstall_result()` へgeneralizeし、deprovision/purge両adapterが使用する。

`_validate_uninstall_process_result()` はstatic request contextの`specs_mode`を受け、次のpairだけを認める。

```text
result.intent=deprovision + specs_mode in {None, keep}
result.intent=purge       + specs_mode=remove
```

次を拒否する。

- purge result + keep/default
- deprovision result + remove
- `same-keep-command` + purge
- `same-remove-command` + deprovision
- missing phase/last completed phase
- non-canonical failed/pending paths
- success resultにfailure state
- failure resultにoperation errorなし

`_uninstall_payload_from_result()`、`_render_uninstall_text()`、`_uninstall_exit_code_from_result()`、schema version 1、field setを維持する。

### 11.4 Guidance and public errors

`_uninstall_guidance_from_result()` を次へ拡張する。

- `same-keep-command`: existing keep text
- `same-remove-command` + apply: `spec-dock uninstall <target> --apply --remove-specs`
- `same-remove-command` + dry-run: `--apply --remove-specs`を要求するdestructive guidance
- `manual-recovery`: legacy/dual/mismatchの既存sanitized guidance

`_UNINSTALL_PUBLIC_OPERATION_ERRORS` にpurge-specific codeを追加する。

```text
purge-preflight-failed
purge-target-not-directory
purge-root-binding-required
purge-root-binding-mismatch
purge-preflight-blocked
purge-recovery-required
purge-recovery-mismatch
```

public messageはinternal digest/path/contentを含めない。legacy codesは既存mappingを維持する。

## 12. Legacy route deletion

### 12.1 Delete production owners

new route green後、`src/spec_dock/cli.py` から少なくとも次を削除する。削除前にAST/source call graphで他callerがないことを確認する。

- `_run_uninstall_remove_specs_compatibility`
- `_UninstallTargetIdentity`
- `_UninstallAction`
- `_build_uninstall_plan`
- `_apply_uninstall_plan`
- `_remove_uninstall_path`
- `_remove_uninstall_tree_fd`
- `_write_uninstall_retry_marker`
- `_finalize_uninstall_retry_marker`
- `_restore_uninstall_retry_marker_action`
- `_ensure_uninstall_retry_marker_action`
- `_verify_uninstall_postcondition`
- `_cleanup_empty_uninstall_dirs`
- `_uninstall_apply_blockers`
- legacy `_uninstall_payload`
- `_emit_uninstall_preflight_error`
- old plan-only identity capture/classification/walker helpers whose only callerが上記cluster

削除対象を名前だけで一括削除せず、current public mapperに必要なhelperを保持する。

### 12.2 Retain public mapper

次は削除せずgeneralizeする。

- `_uninstall_retry_command`
- `_safe_retry_target_label`
- `_uninstall_payload_from_result`
- `_validate_uninstall_process_result`
- `_uninstall_exit_code_from_result`
- `_summarize_uninstall_outcomes`
- `_uninstall_guidance_from_result`
- `_uninstall_public_operation_error`
- `_uninstall_public_action_error`
- `_render_uninstall_text`

### 12.3 Retain legacy detection, not writer

`src/spec_dock/managed_distribution.py` の次の意味は維持する。

- `_UNINSTALL_RETRY_MARKER_REL`
- no-follow single-link regular validation
- valid marker ambiguity detection
- invalid marker rejection
- dual recovery state rejection

legacy markerをcreate、rewrite、finalize、deleteするproduction symbolは0にする。

## 13. Compatibility

### 13.1 Public compatibility

変更しないもの:

- command/flags
- argparse mutual exclusion
- dry-run default
- JSON schema version 1
- JSON field set
- exactly one stdout JSON object
- exit code mapping
- action category `spec_history`
- root-level history action path
- keep/default behavior

意図的に変わるinternal implementation:

- remove routeがtyped service/resultへ移る。
- recovery stateがschema-2 guard + protocol-2 journalになる。
- old marker writerが消える。
- partial purgeがentry checkpoint単位でforward recovery可能になる。

### 13.2 Package/protocol compatibility

purge journalを作成したpackageからold packageへdowngradeしない。same protocolを理解し、semantic source compatibilityとexact purge contract/planを再構成できるcompatible newer packageだけがforward recoveryする。

journal schema/protocol versionを上げないため、parserはintent/purpose literal追加をstrict discriminatorとして扱う。purge literalを知らないold packageは安全に停止することを前提とし、old packageでmarkerを手動削除して続行しない。

### 13.3 README

root `README.md` のuninstall sectionを更新する。

- remove-specsをIssue 371 compatibility authorityと呼ぶ記述を削除
- shared journaled explicit purgeであること
- dry-run write0、apply再assessment
- exact history root
- symlink/hardlink/specialはpre-write block
- `.workbench`/authority外 preservation
- same-remove forward recovery
- `.uninstall-retry.json` automatic conversionなし


## 14. Failure semantics

### 14.1 Before first target mutation

- assessment/blocker: `blocked`, write0
- invalid request/evidence: `error`, write0
- legacy ambiguity/mismatch: `recovery_required`, write0
- guard publish failure: `error`または`recovery_required`、target write0
- journal prepare failure: guard cleanupがexactに安全ならcleanup、そうでなければrecovery evidenceとして保持。target write0

### 14.2 After possible target mutation

- action identity mismatch
- root/parent rebind
- unknown child appearance
- quarantine/staging cleanup failure
- checkpoint write failure
- post-assessment failure

上記は`recovery_required`とし、journal/guardを保持する。completed actionをrollbackしない。pending actionをfresh assessmentの別planへ差し替えない。

### 14.3 Irrecoverable ambiguity

次はautomatic retryを出さない。

- legacy marker only
- legacy + new state
- nonterminal journal without guard
- cross-intent/authority
- contract/plan mismatch
- history tree/journal reconstruction mismatch
- root identity mismatch
- unknown transition entry not owned by staging lease

public resultはsanitized manual recovery guidanceを返し、marker/journal/stageを自動削除しない。

## 15. Test design

### 15.1 `tests/unit/infra/test_managed_distribution.py`

追加するtest groups:

- contract fixed values/digest
- `.workbench` only preservation in purge component
- exact history root and canonical path guard
- arbitrary regular history tree action construction
- depth ordering and immediate child evidence
- absence witness/no-op write0
- dry-run write0
- mixed blocker operation-wide write0
- root/child symlink block
- hardlink/special/unreadable block
- root/parent/leaf/directory rebind
- unknown child appearance
- same-plan interruption/recovery
- cross-intent/authority/plan/root mismatch
- journal reconstruction after partial deletion
- public root outcome aggregation source data

### 15.2 `tests/unit/infra/test_init_update.py`

追加・更新するtest groups:

- 8-row uninstall route matrix
- remove dry/apply service call count
- default/keep never purge
- typed mapper accepted/rejected intent/specs_mode pairs
- schema/field/one-object/text/exit parity
- root-level `spec_history` outcome
- same-remove retry command
- legacy marker valid/invalid/copied/symlink/hardlink/special/dual state
- CLI journal/store interpretation 0
- outside sentinel and `.workbench` preservation

### 15.3 `tests/cli_runtime/test_distribution_cutover.py`

source/AST invariants:

- `_run_uninstall_remove_specs_compatibility` absent
- `_write_uninstall_retry_marker` absent from production call graph
- `_apply_uninstall_plan` / `_remove_uninstall_tree_fd` absent
- remove route calls `execute_explicit_spec_history_purge_distribution`
- CLI mapper does not import/read `OperationJournalStore`、`.distribution-journal.json`、checkpoint
- only `managed_distribution.py` owns purge target mutation
- legacy marker reader exists、writer不存在

## 16. Security and privacy boundary

- journal/public outputへabsolute path、file bytes、credentials、tokensを保存しない。
- history digestはSHA-256 evidenceでありbackupではない。
- symlinkをfollowしない。history symlinkはblockerでありunlinkもしない。
- hardlink peerを変更しない。
- path error messageはrepository-relative sanitized pathだけを使用する。
- outside sentinelはaction graph外であり、test fixtureがbefore/after identity/bytesを比較する。

## 17. Rollback and release safety

### 17.1 New purge journal作成前

candidate codeを通常revertできる。test fixtureでtarget/guard/journal/legacy marker/stage write0を確認してからdiffを破棄する。

### 17.2 New purge journal作成後

old packageへrollbackしない。次を満たすcompatible packageだけでforward recoveryする。

- intent=`purge`
- authority=`explicit-spec-history-purge`
- same root/contract/plan
- protocol version 2
- explicit `--apply --remove-specs`

history bytesのautomatic restoreはない。release withdrawal時もrecovery-capable binaryを先に確保する。

### 17.3 Human handoff evidence

manual recoveryへ移る場合、次だけを保全する。

- candidate/package version
- root identity
- public JSON
- guard/journal digestsとrelative inventory
- staging lease names/relative paths
- test/full-regression artifact

file content、credential、absolute consumer pathを外部共有しない。guard/journal/legacy marker/stageを手動削除・renameしない。

## 18. Design completion criteria

- current Issue 370 model/journal/kernel/resultを再設計せずreuseしている。
- separate `purge` intent/authority/contractがexactに定義されている。
- history root、symlink/hardlink/special policy、unknown regular content policyが一意である。
- dry-runとapplyの再assessment関係が明確である。
- partial deletionからjournal-based plan reconstructionが定義されている。
- public root-level action aggregationとretry commandが定義されている。
- old writerの削除対象と維持するmapper/readerが分離されている。
- implementation時に人間が追加判断するauthority、root、schema、failure policy、recovery policyが残っていない。
