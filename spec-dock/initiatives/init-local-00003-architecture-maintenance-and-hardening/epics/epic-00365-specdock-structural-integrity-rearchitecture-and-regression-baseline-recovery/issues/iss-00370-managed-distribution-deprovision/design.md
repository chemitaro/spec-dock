---
種別: 設計書（Issue）
ID: "iss-00370"
タイトル: "Managed Distribution Deprovision"
関連GitHub: ["#370"]
状態: "planned"
最終更新: "2026-08-25"
依存: ["requirement.md"]
親: ["epic-00365", "init-local-00003"]
---

# iss-00370 Managed Distribution Deprovision — 設計

詳細: [Design Guide](../../../../../../docs/authoring/design.md)

## 設計目標

Requirement の default/`--keep-specs` dry-run、`--apply --keep-specs`、data preservation、forward recovery、public compatibilityを、Issue 368・369の既存vertical architectureへ追加する。

```text
CLI Adapter
  -> Deprovision request normalization
  -> Distribution Operation Service
       -> Distribution Contract
       -> read-only WorkspaceAssessment
       -> blocker-free ExecutableMutationPlan
       -> schema-2 Forward Guard + OperationJournalStore
       -> apply_distribution_plan() descriptor-bound kernel
       -> post-assessment
       -> DistributionProcessResult
  -> uninstall schema-v1 / text / exit compatibility mapper
```

中心設計は「managed rootを再帰削除する」ことではない。bounded treeをread-onlyに完全列挙し、ownershipを証明したleafと、leaf除去後にexact emptyを再証明できるdirectoryを、common actionとして一件ずつjournalする。unknown/modified childが一件でもあるtreeにはexecutable authorityを発行しない。

## Current / Target

### Current: exact SHAで確認した実装事実

基準commitは `7301800263eae1a78ea710ff1935ab4ce0f138e7` である。

#### `src/spec_dock/managed_distribution.py`

Current types:

```python
DistributionOperation = Literal["fresh", "update", "init-force", "uninstall"]
JournaledDistributionIntent = Literal["fresh", "update", "init-force"]
DistributionActionName = Literal[
    "create",
    "adopt",
    "upgrade",
    "prune",
    "preserve",
    "block",
    "ensure-directory",
]
```

Current domain/result types:

- `DistributionIdentity`
- `DistributionAsset`
- `DistributionDirectoryRequirement`
- `DistributionAction`
- `PathIdentitySnapshot`
- `DistributionTargetSnapshot`
- `DistributionPlan`
- `WorkspaceAssessment`
- `ExecutableMutationPlan`
- `OperationJournalAction`
- `OperationJournal`
- `DistributionProcessResult`

Current journal contract:

- journal path: `spec-dock/.distribution-journal.json`
- journal schema version: `1`
- current protocol version: `2`
- forward guard path: `spec-dock/.distribution-retry.json`
- forward guard schema version: `2`
- current guard purposes:
  - `recognized-journal-forward-only`
  - `fresh-journal-forward-only`
- current authorities:
  - `recognized-workspace-reconciliation`
  - `fresh-distribution-provisioning`

Current service/kernel seam:

- `build_workspace_assessment()`
- `build_executable_mutation_plan()`
- `OperationJournalStore`
- `apply_distribution_plan()`
- `execute_recognized_distribution()`
- `execute_fresh_distribution()`
- descriptor-bound root/parent/target/stage/journal helpers

Current uninstall extension seam:

- `DistributionOperation`は`uninstall`を含む。
- `build_distribution_plan(..., operation="uninstall")`はexact owned/current/historical targetを`prune`、unsafe/unknown/mode driftを`preserve`または`block`へ分類する。
- `admit_distribution_operation(..., operation="uninstall")`はlegacy `.uninstall-retry.json`を`uninstall-retry` statusとして検出する。
- `JournaledDistributionIntent`、journal authority、guard purposeにはdeprovisionがまだない。

#### `src/spec_dock/cli.py`

Current parser:

```text
spec-dock uninstall [path] [--apply] [--keep-specs | --remove-specs] [--json]
```

Current private deprovision engine:

- `_UninstallTargetIdentity`
- `_UninstallAction`
- `_build_uninstall_plan()`
- `_append_distribution_uninstall_actions()`
- `_add_managed_scaffold_uninstall_actions()`
- `_remove_uninstall_tree_fd()`
- `_remove_uninstall_path()`
- `_apply_uninstall_plan()`
- `_cleanup_empty_uninstall_dirs()`
- `_verify_uninstall_postcondition()`
- `_write_uninstall_retry_marker()` / `_finalize_uninstall_retry_marker()`

Current path recursively removes `spec-dock/{docs,templates,scripts,system}` as root actions after type-only tree safety checks.そのためmanaged root内のunknown/modified regular fileをownership evidenceなしで削除するcurrent testsが存在し、parent Epicのunknown/modified preservation contractと一致しない。

Current public mapper:

- `_uninstall_payload()`
- `_render_uninstall_text()`
- schema version 1 top-level/action/summary fields
- success/planned=0、blocked/partial=1、parser/preflight=2
- `blocked`/`partial_failure`時のrelative target、status別target contract、sanitized action/operation error、shell-safe retry command

Current legacy marker:

```json
{
  "schema_version": 1,
  "managed_by": "spec-dock",
  "purpose": "uninstall-rerun"
}
```

root、specs mode、intent、authority、contract、plan、checkpointを持たない。

### Target

- public `uninstall`はCLI wordingとして維持し、default/keep routeだけをinternal `deprovision` intentへ正規化する。
- `JournaledDistributionIntent`、journal authority、guard purposeへdeprovisionを追加する。
- common action grammarへ`remove-empty-directory`を追加する。fresh allowlistは変更しない。
- `build_workspace_assessment()` / `build_executable_mutation_plan()` / `OperationJournalStore` / `apply_distribution_plan()`をdeprovisionで再利用する。
- managed treeをper-entry actionへflattenし、unknown/modified childをroot membershipだけでowned扱いしない。
- generated stateは`build_deprovision_generated_state_contract()`の一つのproducerだけから構築し、`active` / `.agent`のcurrent slot、semantic identity、legacy境界、conflict blockerを固定する。
- spec historyとknown preserved treeを`DistributionPreservationWitness`、already-absent owned subtreeを`DistributionCollapsedAbsenceWitness`としてplan digest、journal、post-assessmentへ束縛する。
- default/keep dry-runはserviceのassessment resultからpublic planを生成し、guard/journal/marker/stageを書かない。
- applyはschema-2 guard、protocol-2 journal、per-action checkpoint、post-assessmentを使用する。
- legacy `.uninstall-retry.json`は変換せず、typed recovery stateを返す。
- serviceはpublic phase/errorへ必要な情報をtyped `DistributionProcessResult`へ確定し、CLIはparse/dispatch/presentationだけを行う。CLIはownership、tree recursion、journal interpretation、journal transition、target mutationを持たない。
- `--remove-specs`はIssue 371 ownerの明示的compatibility routeとして隔離し、本Issueのserviceから到達不能にする。

## Design element registry

三文書のtraceabilityで次のstable design element IDを使用する。

| Design ID | 設計要素 | 主なsection / owner |
|---|---|---|
| D370-CLI | CLI parse、root lock/binding、default/keepとremove routeの一回限りのdispatch | `src/spec_dock/cli.py` |
| D370-INT | `deprovision` intent、`uninstall` plan mapping、action allowlist、authority、guard purpose | Intent、authority、action grammar |
| D370-DATA | tree entry、directory mutation snapshot、preservation witness、collapsed absence witnessのimmutable model | Proposed data model |
| D370-CONTRACT | physical/historical/generated/preserved contract、single generated-state producer、current/legacy境界 | Distribution Contract |
| D370-ASSESS | no-follow observation、top-down absence collapse、complete classification、blocker gate | Deprovision assessment algorithm |
| D370-PLAN | mutating-only executable plan、dependency、pre/postcondition、canonical digest | Executable plan |
| D370-JOURNAL | schema-2 guard、protocol-2 journal、witness metadata、reachable checkpoint/status state machine、resume、terminal cleanup | Journal / guard design |
| D370-KERNEL | exact regular/symlink pruneとbound empty-directory removal | Filesystem kernel |
| D370-SERVICE | dry-run、metadata-free no-op、journaled apply、post-assessment、durable-state-to-result conversion | Service / flows |
| D370-RESULT | typed action outcome、phase、last-completed、failed/pending paths、errors、retry policy | Process result / population rules |
| D370-MAP | schema-v1 JSON、text、exit、sanitization、retry mapping。typed result以外を読まない | Public compatibility mapper |
| D370-LEGACY | legacy `.uninstall-retry.json` non-conversionとadmission matrix | Legacy marker / new journal admission |
| D370-MIG | hard route split、legacy call-edge removal、no dual writer、docs migration | Migration strategy |
| D370-PLAT | Darwin/Linux capability boundary、failure injection、bounded performance | Platform / testability |

## Moduleと責務境界

### `src/spec_dock/cli.py` — CLI adapter / presentation mapper

Issue 370でdefault/keep routeに許可する責務:

1. `argparse`でcurrent public surfaceをparseする。
2. specs mode matrixを一度だけ解決する。
3. default/keepを`deprovision` requestへdispatchする。
4. `--remove-specs`をD4 compatibility routeへ明示dispatchする。
5. apply routeではexisting `_exclusive_distribution_operation()` / `_bound_distribution_root()`でroot lockとbound root identityを取得し、そのcontextをservice callとterminal finalizationが返るまで保持する。dry-runはtarget mutationを伴うlock artifactを新規作成せずread-only bound-root validationを行う。
6. package asset path、executing package version、bound root identityをserviceへ渡す。
7. static request contextとfully-populated `DistributionProcessResult`だけをschema-v1 JSON、text、exit codeへmappingする。
8. exactly one stdout object、stderr、sanitization、retry commandを維持する。

禁止事項:

- ownership classification
- managed tree traversal
- recursive unlink/rmdir
- journal/guard readによるpublic phase/error補完、journal/guard write、checkpoint transition
- stage/GC lease cleanup
- deprovision postcondition判定
- default/keep routeからlegacy uninstall helperへのfallback

D4 compatibility exception:

- `--remove-specs` routeはIssue 371までcurrent behaviorを維持する。
- route名を `_run_uninstall_remove_specs_compatibility_unlocked()` に固定する。
- default/keep routeはこのentrypointを呼ばない。
- compatibility routeがdeprovision guard/journalを見つけた場合はintent mismatchとしてcheckpointを進めない。
- この一時的exceptionはD4 handoffに一覧化し、Issue 372のcleanup ownerへ先送りしない。

### `src/spec_dock/managed_distribution.py` — domain/service/journal/kernel owner

責務:

- deprovision intent/authority/guard purpose
- package Distribution Contract とmanaged/preserved root contract
- read-only tree observationとownership classification
- single generated-state contract producer、preservation witness、collapsed absence witness
- common action grammar/allowlist
- executable plan、canonical serialization、plan digest
- schema-2 guardとjournal admission/resume
- descriptor-bound leaf removalとempty-directory removal
- post-assessmentとtyped result

本Issueでは新しいgeneric filesystem classを作らない。current kernelは`apply_distribution_plan()`とdescriptor-bound helper群で成立しているため、そのseamに必要なtype-specific operationを追加する。

### Tests

- `tests/unit/infra/test_managed_distribution.py`
  - pure contract/assessment/plan/journal/kernel
- `tests/unit/infra/test_init_update.py`
  - installer behavior、preservation、source/route absence
- `tests/cli_runtime/test_distribution_cutover.py`
  - public CLI matrix、JSON/text/exit、failure injection、legacy route isolation
- `tests/conftest.py`
  -変更しない。full-regression lane contractを利用する。

### Shipped docs

実装と同じchange setで次を更新する。

- `README.md`
- `src/spec_dock/assets/spec_dock/docs/README.md`
- `spec-dock/docs/README.md`
- `src/spec_dock/assets/spec_dock/docs/migration.md`
- `spec-dock/docs/migration.md`

provider assetとdogfooding copyは同じ意味を持ち、package parityはIssue 372の最終gateへ渡す。

## Intent、authority、action grammar

### Type alias変更

```python
JournaledDistributionIntent = Literal[
    "fresh",
    "update",
    "init-force",
    "deprovision",
]

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

`DistributionOperation`のpublic/classification側`"uninstall"`はcurrent compatibilityのため維持する。journal intentは`"deprovision"`とし、requested operationとeffective intentを混同しない。

`build_executable_mutation_plan()`のcurrent `distribution_plan.operation == assessment.intent` 相当の検証は、次のexplicit mappingで置き換える。

```python
def _plan_operation_for_intent(intent: JournaledDistributionIntent) -> DistributionOperation:
    if intent == "deprovision":
        return "uninstall"
    return intent
```

このmapping以外で`uninstall` planをjournaled intentへ昇格しない。

### Intent-specific action allowlist

```python
_FRESH_DISTRIBUTION_ACTIONS = frozenset({
    "create",
    "adopt",
    "preserve",
    "block",
    "ensure-directory",
})

_DEPROVISION_DISTRIBUTION_ACTIONS = frozenset({
    "prune",
    "preserve",
    "block",
    "remove-empty-directory",
})
```

`fresh` grammarはIssue 369 Reportの契約から変更しない。`deprovision`で`create`、`upgrade`、`ensure-directory`を受理しない。already-absent owned targetはassessment diagnosticまたはcollapsed absence witnessであり、`ExecutableMutationPlan.actions`へ`prune`として入れない。

### Authority / guard mapping

```python
_DISTRIBUTION_DEPROVISION_JOURNAL_GUARD_PURPOSE = (
    "deprovision-journal-forward-only"
)

_DISTRIBUTION_JOURNAL_AUTHORITIES = {
    "recognized-journal-forward-only": "recognized-workspace-reconciliation",
    "fresh-journal-forward-only": "fresh-distribution-provisioning",
    "deprovision-journal-forward-only": "managed-distribution-deprovision",
}
```

```python
def _journal_authority_for_intent(intent: JournaledDistributionIntent) -> str:
    match intent:
        case "fresh":
            return "fresh-distribution-provisioning"
        case "deprovision":
            return "managed-distribution-deprovision"
        case "update" | "init-force":
            return "recognized-workspace-reconciliation"
```

```python
def _journal_guard_purpose_for_intent(intent: JournaledDistributionIntent) -> str:
    match intent:
        case "fresh":
            return "fresh-journal-forward-only"
        case "deprovision":
            return "deprovision-journal-forward-only"
        case "update" | "init-force":
            return "recognized-journal-forward-only"
```

Parser/serializerはpurposeとauthorityを独立に受理せず、mappingのexact pairだけを許可する。

## Proposed data model

### Tree entry snapshot

```python
DistributionTreeEntryKind = Literal["regular", "directory", "symlink"]

@dataclass(frozen=True)
class DistributionTreeEntrySnapshot:
    relative_path: str
    kind: DistributionTreeEntryKind
    device: int
    inode: int
    ctime_ns: int
    mode: int
    link_count: int
    size: int | None = None
    sha256: str | None = None
    link_target: str | None = None
```

Invariants:

- `relative_path`はsafe repository-relative POSIX path。
- `mode`はfile type bitsを除いた`stat.S_IMODE(st_mode)`である。
- regularは`size`、`sha256`必須、`link_target=None`。
- symlinkは`link_target`必須、targetをfollowしない。mutation対象symlinkは`link_count == 1`必須。
- directoryはcontent hashを持たない。
- special fileはsnapshotを発行せずblockerを返す。
- mutation対象regularは`link_count == 1`必須。
- preservation対象regularのunproven multi-linkもblockerとする。

### Directory mutation snapshot

```python
@dataclass(frozen=True)
class DistributionDirectoryMutationSnapshot:
    relative_path: str
    binding: PathIdentitySnapshot
    initial_entries: tuple[DistributionTreeEntrySnapshot, ...]
    initial_child_digest: str
    dependency_paths: tuple[str, ...]
    expected_remaining_child_digest: str
```

`binding`のstable comparisonはdevice/inode/type/modeを使用する。authorized child mutationはdirectory ctimeとlink countを変更し得るため、後続mutationのbinding comparisonへinitial ctime/link count exactを要求しない。initial ctime/link countはaudit evidenceとして保持し、visible pathとheld descriptorが同じdevice/inode/type/modeを指すことを各mutation境界で再検証する。namespace変化は後述のexpected child digestで別途検証する。

`dependency_paths`はそのdirectory直下またはdescendantを消すprior mutating action pathのcanonical tupleである。directory actionの実行条件は、全dependencyがjournal checkpoint `published`であり、各current targetがそのactionのexact expected-absent postconditionに一致することである。`verified`はdependency条件ではない。

child digestは次のrecordをrelative-path byte orderでsortしたcanonical JSONのSHA-256とする。

```text
format_version
relative_path
kind
device
inode
ctime_ns
mode
link_count
size-or-null
sha256-or-null
link_target-or-null
classification
owner_source
```

absolute path、wall-clock timestamp、process ID、random nonceをdigest inputにしない。

### Preservation witness

```python
@dataclass(frozen=True)
class DistributionPreservationWitness:
    relative_root: str
    root_binding: PathIdentitySnapshot
    entries: tuple[DistributionTreeEntrySnapshot, ...]
    tree_digest: str
    reason: str
```

初期対象:

- `spec-dock/initiatives`
-存在する場合の`spec-dock/.workbench`

preservation rootがmissingならmissing snapshotを保持する。apply中にappearanceした場合もpostcondition mismatchとする。root symlink、unsafe parent、special file、unproven hardlinkはblockerであり、witnessを発行しない。

Preservation witnessは`DistributionAction`でも`OperationJournalAction`でもない。checkpointを持たず、plan/journal immutable metadataとしてpreflight、first mutation前、verifyingのfull post-assessmentで再検証する。

### Collapsed absence witness

```python
@dataclass(frozen=True)
class DistributionCollapsedAbsenceWitness:
    relative_root: str
    nearest_existing_ancestor: PathIdentitySnapshot
    missing_suffix: tuple[str, ...]
    owned_descendant_paths_digest: str
    reason: Literal["owned-subtree-already-absent"]
```

Invariants:

- `relative_root`はcontract-owned pathである。
- `nearest_existing_ancestor`はroot descriptorからno-followで開いたreal directoryである。
- `missing_suffix`はancestorから`relative_root`までのnon-empty canonical path componentsであり、最初のmissing componentより下をfilesystemで列挙しない。
- `owned_descendant_paths_digest`はcontract上の`relative_root`と全owned descendants、expected kinds、owner sourcesをcanonicalにhashする。
- witnessが存在するsubtreeのdescendantへmutating actionを発行しない。
- recovery metadataがないfresh assessmentでだけcollapseを新規作成する。existing journal resumeではjournal action setをcurrent absenceに合わせて置換しない。

### Generated-state contract

```python
GeneratedStateOrigin = Literal[
    "current-active-producer",
    "current-agent-producer",
    "historical-exact",
]

@dataclass(frozen=True)
class DistributionGeneratedStateEntry:
    path: str
    origin: GeneratedStateOrigin
    expected_kind: Literal["regular", "symlink"]
    identity: DistributionIdentity
    observed: PathIdentitySnapshot
    semantic_contract: str

@dataclass(frozen=True)
class DistributionGeneratedStateContract:
    entries: tuple[DistributionGeneratedStateEntry, ...]
    current_slots: tuple[str, ...]
    legacy_unproven_paths: tuple[str, ...]
    blockers: tuple[DistributionAction, ...]
    contract_digest: str
```

`identity`はsemantic validatorがcurrent producer outputと認定した後のobserved exact SHA/modeまたはlink targetである。`observed`は同じno-follow観測のdevice/inode/ctime/type/link countと`identity`を保持し、producer以外が同じpathを再分類して別authorityを作れないようにする。path membershipやfilenameだけからidentityを作らない。`blockers`が非空ならdeprovision executable authorityを発行しない。

### Assessment / plan / journal extensions

```python
@dataclass(frozen=True)
class WorkspaceAssessment:
    intent: JournaledDistributionIntent
    root_identity: DistributionRootIdentity
    contract_identity: str
    distribution_plan: DistributionPlan
    actions: tuple[DistributionAction, ...]              # diagnostic dispositions
    blockers: tuple[DistributionAction, ...]
    directory_snapshots: tuple[DistributionDirectoryMutationSnapshot, ...] = ()
    preservation_witnesses: tuple[DistributionPreservationWitness, ...] = ()
    absence_witnesses: tuple[DistributionCollapsedAbsenceWitness, ...] = ()

@dataclass(frozen=True)
class ExecutableMutationPlan:
    intent: JournaledDistributionIntent
    root_identity: DistributionRootIdentity
    contract_identity: str
    plan_digest: str
    distribution_plan: DistributionPlan
    actions: tuple[DistributionAction, ...]              # mutating actions only for deprovision
    directory_snapshots: tuple[DistributionDirectoryMutationSnapshot, ...] = ()
    preservation_witnesses: tuple[DistributionPreservationWitness, ...] = ()
    absence_witnesses: tuple[DistributionCollapsedAbsenceWitness, ...] = ()
```

For deprovision:

- `WorkspaceAssessment.actions`はpublic diagnostics用の`prune` / `preserve` / `block` / `remove-empty-directory` classificationを保持する。
- `ExecutableMutationPlan.actions`は現在存在してmutationが必要な`prune`と`remove-empty-directory`だけを保持する。
- already-absent entryはdiagnostic outcomeまたはabsence witnessでありjournal actionにしない。
- `preserve` / `block`はjournal actionにしない。

`OperationJournal`へprotocol-2 deprovision専用のimmutable metadataを追加する。

```python
preservation_witnesses: tuple[DistributionPreservationWitness, ...] = ()
absence_witnesses: tuple[DistributionCollapsedAbsenceWitness, ...] = ()
```

schema version 1は維持する。parserはdeprovision intentで両fieldをrequireし、fresh/recognized intentでnon-emptyなら拒否する。guard-only recoveryはfull witnessを持たないためcurrent assessmentからsame plan digestをexact再構成できる場合だけjournalをprepareする。

### Typed process result

existing `DistributionProcessResult`を置換する別result hierarchyは作らない。current fresh/recognized constructorを壊さないよう、deprovision presentation fieldsはdefault付きで末尾へ追加し、`intent="deprovision"`のservice return時だけcomplete populationを必須にする。

```python
DistributionProcessStatus = Literal[
    "planned",
    "completed",
    "blocked",
    "recovery_required",
    "error",
]
DistributionDeprovisionPhase = Literal[
    "preflight",
    "marker-write",
    "uninstall-apply",
    "root-cleanup",
    "post-verify",
    "marker-finalization",
    "complete",
]
DistributionDeprovisionCompletedPhase = Literal[
    "not-started",
    "preflight-complete",
    "marker-written",
    "uninstall-applied",
    "post-verified",
    "marker-finalized",
]
DistributionRetryPolicy = Literal["none", "same-keep-command", "manual-recovery"]
DistributionActionOutcomeStatus = Literal[
    "would_remove",
    "removed",
    "already_removed",
    "preserved",
    "failed",
    "pending",
    "empty_dir_removed",
]

@dataclass(frozen=True)
class DistributionActionOutcome:
    path: str
    category: str
    status: DistributionActionOutcomeStatus
    reason: str
    error: str | None = None

@dataclass(frozen=True)
class DistributionProcessError:
    code: str
    message: str
    path: str | None = None

@dataclass(frozen=True)
class DistributionProcessResult:
    # existing common fields; names/order/default behaviorを維持する
    status: DistributionProcessStatus
    intent: JournaledDistributionIntent
    actions: tuple[DistributionAction, ...]
    plan_digest: str | None = None
    reason: str | None = None
    applied_paths: tuple[str, ...] = ()
    pending_paths: tuple[str, ...] = ()

    # Issue 370 additive typed presentation fields
    action_outcomes: tuple[DistributionActionOutcome, ...] = ()
    phase: DistributionDeprovisionPhase | None = None
    last_completed_phase: DistributionDeprovisionCompletedPhase | None = None
    failed_paths: tuple[str, ...] = ()
    errors: tuple[DistributionProcessError, ...] = ()
    retry_policy: DistributionRetryPolicy = "none"
```

Invariants:

- `intent="deprovision"`でservice boundaryを出るresultは`phase`と`last_completed_phase`がnon-`None`で、action outcomes、failed/pending paths、errors、retry policyがdurable-state population tableに一致しなければならない。
- fresh/recognized existing resultは追加fieldのdefaultを使用でき、Issue 370はそのpublic output semanticsを変更しない。
- public uninstall mapperは`intent="deprovision"`かつcomplete presentation fieldsを持つresultだけを受理し、欠落時にjournalを読まずprogramming errorとして拒否する。
- `pending_paths`はexisting common fieldを唯一のpath tupleとして再利用し、presentation用の第二pending fieldを追加しない。

CLIがjournal、guard、legacy marker、filesystemを追加観測してfieldを補完してはならない。

## Proposed service interfaces

### Canonical generated-state producer

```python
def build_deprovision_generated_state_contract(
    target_root: Path,
    *,
    expected_root_identity: DistributionRootIdentity,
) -> DistributionGeneratedStateContract:
    ...
```

このfunctionが`spec-dock/active`と`spec-dock/.agent`をno-followで一度だけ観測し、current positive、missing、legacy-unproven、unknown/conflictを返す。CLI、caller、assessmentへ`generated_assets`を別途渡すAPIを作らない。

### Deprovision contract / assessment

```python
@dataclass(frozen=True)
class DistributionDeprovisionContract:
    managed_roots: tuple[str, ...]
    preserved_roots: tuple[str, ...]
    removable_shortcuts: tuple[DistributionAsset, ...]
    generated_state: DistributionGeneratedStateContract
    contract_digest: str


def build_deprovision_contract(
    install_root: Path,
    *,
    manifest_path: Path,
    scaffold_root: Path,
    target_root: Path,
    expected_root_identity: DistributionRootIdentity,
) -> DistributionDeprovisionContract:
    ...


def build_deprovision_workspace_assessment(
    install_root: Path,
    *,
    manifest_path: Path,
    scaffold_root: Path,
    target_root: Path,
    expected_root_identity: DistributionRootIdentity,
) -> WorkspaceAssessment:
    ...
```

`build_deprovision_workspace_assessment()`は内部で`build_deprovision_contract()`をexactly once呼ぶ。既存generic `build_workspace_assessment(..., generated_assets=...)`はfresh/recognized compatibility用に残せるが、`intent="deprovision"`を受け付けず、deprovision wrapperから到達不能とする。これにより`contract.generated_state`と独立`generated_assets`の二系統入力を型とcall graphの両方で禁止する。

Canonical contract values:

- managed roots: physical install-root managed assetのparent closure、`spec-dock/{docs,templates,scripts,system}`、generated `spec-dock/{active,.agent}`、exact root shortcutのcanonical union。
- preserved roots: `spec-dock/initiatives`、`spec-dock/.workbench`。
- protocol metadata `.distribution-retry.json` / `.distribution-journal.json`はcontract assetではなくjournal ownerが管理する。
- `.uninstall-retry.json`はlegacy recovery evidenceでありremove actionへ入れない。

### Service

```python
def execute_deprovision_distribution(
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

- `apply=False`: assessmentとtyped planned/recovery/error resultを返すだけ。guard/journal/stage/target writeを禁止する。
- `apply=True`: CLI adapterがexisting `_exclusive_distribution_operation()` / `_bound_distribution_root()`を取得済みであることを前提とし、`expected_root_identity`を必須にする。serviceはentry、各mutation boundary、return直前にbound identityを再検証する。
- specs modeはservice parameterにしない。deprovision serviceはkeep-only contractであり、purge modeを表現できない。
- service内のprivate result builderだけがjournal/guard/durable stateをtyped resultへ変換する。例外をCLIへ投げてjournal解釈を要求しない。

CLI adapterは`--remove-specs`をこのfunctionへ渡せない。

### Presentation view

current `_UninstallAction`はmutation authorityとpresentationを混在させるため、default/keep routeでは使用しない。CLIに置く場合はpure viewだけとする。

```python
@dataclass(frozen=True)
class _UninstallActionView:
    path: str
    category: str
    status: str
    reason: str
    error: str | None = None
```

このtypeはidentity、expected_absent、filesystem method、journal checkpointを持たない。`DistributionProcessResult.action_outcomes`から一方向に生成する。

## Distribution Contract と bounded root inventory

### Contract source

1. `managed_distribution.json`のhistorical recognition / obsolete exact identity。
2. physical `assets/install_root` current files/symlinks。
3. physical `assets/spec_dock` shipped scaffold files。
4. `build_deprovision_generated_state_contract()`のcurrent generated-state entries。
5. exact root shortcut contract。
6. preserved root policy。

Current physical asset、historical exact identity、semantic generated identityを混同しない。historical array index、managed root membership、reserved filenameはownership identityではない。

### Single generated-state producer

provider-side context-pack bytesは二重実装しない。current `src/spec_dock/cli.py::_render_context_pack()`をbehavior unchangedで`src/spec_dock/managed_distribution.py::_render_context_pack()`へ移し、既存`_active_fallback_distribution_assets()`と`build_deprovision_generated_state_contract()`の双方がこのhelperを呼ぶ。shipped runtimeの`spec_dock_runtime.presentation.json_state.render_context_pack()`はinstaller runtimeからimportせず、real fixtureによるbyte-parity sourceとして扱う。三者のbyte差分はcurrent generated identityを推測で受理せずtest failure / Decision Gateとする。

`build_deprovision_generated_state_contract()`はfixed SHAのprovider runtime contractを次のtableへ正規化する。

| Logical slot | Current path(s) | Exact current predicate | Missing / conflict / legacy |
|---|---|---|---|
| active initiative | `spec-dock/active/initiative` XOR `initiative.path` | symlinkはsingle-linkでnormalized relative targetを持ち、valid selected initiativeまたは`system/active-none/initiative`へin-root解決。path fallbackはsingle-link regular、UTF-8一行で同じtargetへ解決。 | both present、wrong kind/content、escape、invalid targetはblock。both absentはalready absent。 |
| active epic | `spec-dock/active/epic` XOR `epic.path` | initiativeと同じpredicateをepic selectionへ適用。 |同上。 |
| active issue | `spec-dock/active/issue` XOR `issue.path` | initiativeと同じpredicateをissue selectionへ適用。 |同上。 |
| context pack | `spec-dock/active/context-pack.md` | single-link regular、validated active selectionからshared provider-side `managed_distribution._render_context_pack()`が生成するexact bytes。 | missingはalready absent。不一致はblock。 |
| active manifest | `spec-dock/.agent/active.json` | single-link regular、UTF-8 JSON object、exact top-level field set `schema_version` / `updated_at` / `initiative` / `epic` / `issue`、`schema_version == 2`。`updated_at`は`now_iso()`と同じtimezone offset付きsecond-precision ISO-8601。各layer valueは`null`またはexact field set `id` / `path`で、`id`はcanonical layer ID、`path`は`spec-dock/initiatives`配下のnormalized repository-relative existing real directoryで、その`.meta.json`のid/kindと一致する。issue non-nullならepic/initiative、epic non-nullならinitiativeもnon-nullでparent chainが一致する。semantic validation後のobserved SHAをidentityにする。 | malformed/extra/invalid timestamp/id/path/hierarchy/hardlinkはblock。missingはallowed。 |
| full index projection | `.agent/index-all.json` | single-link regular、exact top-level field set `schema_version` / `generated_at` / `active` / `warnings` / `root` / `projection` / `deps` / `nodes`、schema `2`、`root="spec-dock/initiatives"`、projection `full-history`。observed SHAをidentityにする。 | field/shape/projection/schema不一致はblock。 |
| full tree artifact | `.agent/tree-all.json` | single-link regular、schema `2`、exact top-level field set `schema_version` / `generated_at` / `active` / `warnings` / `root` / `deps` / `tree`、`root="spec-dock/initiatives"`。`projection` fieldは存在しない。 | extra/missing fieldまたはshape不一致はblock。 |
| todo index projection | `.agent/index.json` | single-link regular、exact top-level field set `schema_version` / `generated_at` / `active` / `warnings` / `root` / `projection` / `deps` / `nodes`、schema `2`、`root="spec-dock/initiatives"`、projection `current-future`。 | field/shape/projection/schema不一致はblock。 |
| todo tree artifact | `.agent/tree.json` | single-link regular、schema `2`、exact top-level field set `schema_version` / `generated_at` / `active` / `warnings` / `root` / `deps` / `tree`、`root="spec-dock/initiatives"`。`projection` fieldは存在しない。 | extra/missing fieldまたはshape不一致はblock。 |
| dependency projection | `.agent/deps-issues.json` | single-link regular、exact top-level field set `schema_version` / `generated_at` / `projection` / `source` / `deps` / `nodes` / `edges` / `dependency_contexts` / `edge_direction`、schema `2`、projection `issue-readiness-with-dependency-context`、`source={"sync_state":"readiness_evaluation","schema_version":2}`、exact edge direction。normal outputまたはdocumented `deps.valid=false` placeholder。 | field/source/projection/schema不一致はblock。 |

Producer implementation rules:

1. target root、`spec-dock`、`active`、`.agent`をdescriptor-relative/no-followでopenする。
2. `.agent/active.json`がpresentならexact timestamp/id/path/`.meta.json`/parent hierarchyをsemantic validationし、active selectionを一度だけ解決する。invalidなら他entryをfallback推測せずblockする。
3.各logical active slotをXORとして検証する。
4. current JSON entryはsemantic validation後にopened fdのexact device/inode/ctime/mode/link count/size/SHAへ束縛する。
5. current symlink entryはno-follow device/inode/ctime/mode/link count/link textへ束縛する。
6. active manifestがpresentなら、active pointer/path fallback、`context-pack.md`、presentなindex/tree artifactの`active` fieldを同じnormalized selectionへcross-validateする。manifestがmissingならselectionは`none`だけを許可し、active pointerは`active-none`、artifact `active`は`null`でなければblockする。
7. presentな`.agent/{index-all,tree-all,index,tree,deps-issues}.json`は同一batchの`generated_at`を持つことを要求する。`index-all`のnode ID集合と`tree-all` flatten集合、`index`のnode ID集合と`tree` flatten集合はexact一致しなければblockする。missing slotは許可するが、present slot間のcross-reference conflictをpartial current stateとして自動受理しない。
8. observed contractをcanonical path orderでsortし、`contract_digest`を作る。
9. runtime writerはdynamic filesへcanonical chmodを強制しないため、producer semantic validationは固定mode値をownership条件にしない。観測modeはexact preconditionへ保存し、後続mode driftを拒否する。
10.同じ情報を`DistributionAsset` tupleとしてcallerから受け取らない。

### Current / legacy boundary

- `spec-dock/active/current-runbook.json`、`current-runbook.md`はcurrent `apply_active_pointers()`が予約cleanup nameとして知るが、fixed SHAのcurrent renderer outputではない。pathnameだけではdelete authorityを与えない。
- `spec-dock/.agent/deps.json`、`deps.puml`、`deps.todo.puml`は`reference_sync.md`がlegacy v1 generated outputとして明示するが、current producer identityではない。
- `spec-dock/.work/**`はlegacy stateでありcurrent generated rootsに含めない。
-上記legacy pathは`managed_distribution.json`等のexact historical identityがcurrent observationと一致する場合だけhistorical `prune`へ入る。それ以外は`legacy-generated-identity-unproven` blocker。
- active/.agentの上記current/legacy allowlist外childは`unknown-generated-state-entry` blocker。
- rootがsymlink、non-directory、special、またはchild enumerationに失敗した場合はroot全体をblockする。

### Traversal boundary

assessmentがopen/list/hashできる範囲は次だけである。

- contractで宣言されたmanaged pathのparent chain
- contractで宣言されたmanaged root subtree
- generated producerの`active` / `.agent` exact roots
- preserved root subtree
- protocol metadataのexact paths

repository全体のrecursive traversalは禁止する。cleanup boundary外siblingは列挙しない。

### Complete classification

managed root内の各entryを次のいずれかへ一意に分類する。

- exact current/historical/generated/shortcut ownership: mutating action候補
- explicit preserved root/entry: preservation witness
- missing contract-owned entry/subtree: diagnostic already-absentまたはcollapsed absence witness
- unknown/modified/unsafe/legacy-unproven/conflict: `block`

classificationされないentry、duplicate path、親子で競合するaction、unsafe relative path、single generated producer外のinputがあればassessment blockerとする。

## Deprovision assessment algorithm

### 1. Admission

1. targetがreal directoryであることを確認する。
2. executing package versionとmanifestを検証する。
3. root device/inodeをcaptureする。
4. recovery stateをread-onlyに読む。
5. `.distribution-retry.json`、`.distribution-journal.json`、`.uninstall-retry.json`のdual/ambiguous stateを検出する。
6. platform capabilityを確認する。
7. applyではCLI adapterが取得したroot operation lockを保持したまま、渡された`expected_root_identity`に対して同じadmissionを再確認する。

### 2. Package and generated contract capture

- manifest/scaffold/install-root sourceをno-followでcaptureする。
- regular source bytes、mode、device/inode/ctime/mtime/size、SHA-256をcurrent kernel contractに従って保持する。
- `build_deprovision_generated_state_contract()`をexactly once呼ぶ。
- producer blockerが一件でもあればgenerated entryをpartial adoptionせずassessment blockerにする。
- assessment後、plan発行直前とfirst mutation直前にsource identityとgenerated contract root bindingsを再検証する。

### 3. Top-down owned-ancestor observation and collapse

contract-owned path treeをtop-down canonical orderで観測する。

1. nearest existing ancestorをroot fdからno-followでopenし、device/inode/typeへ束縛する。
2. next componentが存在する場合は通常のparent/target observationへ進む。
3. next componentがmissingで、そのcomponentから下がcontract-owned subtreeである場合、その最上位owned pathへ一つの`DistributionCollapsedAbsenceWitness`を発行する。
4. witness発行後はそのfilesystem subtreeを列挙せず、contract上のdescendant path digestだけを作る。
5. witness配下のleaf/directory mutation actionは発行しない。
6. missing componentがcontract-owned subtreeより上位、またはnearest existing ancestorをexact bindingできない場合は`unproven-parent-gap` blocker。

Recovery metadataなしのassessmentだけがnew collapseを作る。journal resumeではjournal actions/witnessesを正本とし、現在absentだからという理由でactionを消さない。

### 4. Managed path observation

- root descriptorからexisting parent chainを`O_NOFOLLOW|O_DIRECTORY`でopenする。
- targetは`stat(..., follow_symlinks=False)`で観測する。
- regular fileはheld fdからSHA-256を計算し、open前後identityを照合する。
- symlinkは`readlink`し、targetをfollowしない。
- directoryはheld descriptorからchild nameを列挙する。
- enumeration orderはcanonical relative POSIX path orderとする。

### 5. Ownership classification

- current exact regular/symlink: diagnostic `prune`; target presentならmutating `prune`候補。
- historical exact regular/symlink:同上。
- current generated producer entry: diagnostic `prune`; presentならmutating `prune`候補。
- missing owned leaf underexisting ancestor: diagnostic `prune` + `already-absent` outcome、mutating actionなし、leaf-level absence witness。
- collapsed owned subtree: one collapsed witness、descendant mutating actionなし。
- modified/mode mismatch/unknown/generated conflict/legacy-unproven: `block`。
- hardlink/special/unsafe parent/symlink boundary: `block`。

### 6. Scaffold and generated root expansion

`spec-dock/{docs,templates,scripts,system,active,.agent}`を一つのrecursive removal actionにしない。

- each exact owned leafをclassificationする。
-各directoryのinitial child setをcaptureする。
- unknown/modified/preserved/legacy-unproven childがあればそのdirectory actionを作らずoperation blocker。
-全present owned childがmutating `prune`、already absent、またはcollapsed absenceで説明され、preserved childが0のexisting directoryだけ`remove-empty-directory`を作る。
- directory actionはdeepest-firstで、dependency child actionより後に配置する。

### 7. Preservation and absence witnesses

- `spec-dock/initiatives`をno-follow recursive snapshotする。
- `.workbench`が存在すれば同様にsnapshotする。
- regular bytes SHA、mode、type、link topology、symlink text、directory child setをpreservation digestへ含める。
- collapsed absenceはnearest existing ancestor binding、missing suffix、contract-owned descendant digestを保持する。
- content bytes、absolute pathをjournalへ保存しない。
- special file、unproven hardlink、root/parent symlinkはblocker。

### 8. Blocker gate

blockerが一件でもあればassessmentをdiagnosticとして返し、`build_executable_mutation_plan()`を呼ばない。dry-runはplanned viewとしてblockerを表示できるが、applyはpublic `blocked`となる。generated contract conflict、unproven missing parent、witness capture failureもsafe actionと分離せずwhole-operation blockerにする。

## Executable plan とcanonical digest

### Mutating action set and order

For deprovision、`ExecutableMutationPlan.actions`はmutating actionだけを保持する。

1. present exact-owned regular/symlink `prune`をdepth descending、path ascendingでsortする。
2. `remove-empty-directory`をdependency topological order、depth descending、path ascendingでsortする。
3. `preserve` / `block`、already-absent diagnostics、preservation witness、collapsed absence witnessはjournal actionにしない。
4. protocol metadata cleanupはdomain actionに混ぜずjournal finalizationが所有する。

mutating actionが0件でrecovery metadataもなければ、executable planはno-op planとして発行できるがguard/journalを作らない。

### Digest input

- digest format version
- root identity
- `intent="deprovision"`
- `authority="managed-distribution-deprovision"`
- contract identity
- generated-state contract digest（各entryのsemantic contract、identity、no-follow `observed` snapshotを含む）
- ordered mutating actions
- each action path/action/provenance/reason
- complete root/parent/target pre/postcondition
- each action parent-chain stable bindingsとprior published actionsから導出するexpected parent child digests
- directory initial/expected child digestと`dependency_paths`
- preservation witness canonical records/digests
- collapsed absence witness canonical records/digests
- source snapshot identity

次を含めない。

- absolute target path
- wall-clock timestamp
- operation ID / nonce
- current journal/guard file identity
- public category/wording

`preserve`/`block`をjournal actionから除外しても、witnessとdiagnostic disposition digestがcontract identityへ含まれるため、unknown/preserved stateをplan外にしない。

### Action pre/postcondition

#### Existing regular prune

Precondition:

- root/parent chain full ordered identity
- `exists=true`
- file type regular
- device/inode/ctime
- link count exactly 1
- mode、size、SHA-256

Postcondition:

- same root/parent binding
- target `exists=false`

#### Existing symlink prune

Precondition:

- root/parent chain
- `exists=true`
- symlink no-follow identity
- exact link text

Postcondition: target absent。

#### Already-absent owned leaf

- assessment diagnosticは`already_removed`へmappingする。
- `ExecutableMutationPlan.actions`とjournalには入れない。
- leaf-level `DistributionCollapsedAbsenceWitness`でnearest existing parentとmissing suffixを束縛する。
- apply前/post-assessmentでappearanceした場合はblock/recovery required。

#### Remove-empty-directory

Precondition:

- root/parent chain
- exact directory device/inode/type
- initial child digest
- ordered `dependency_paths`
- expected remaining child digest = empty digest
-全dependency actionのexpected postcondition = target absent

Execution admission:

- journal status `executing`
- directory action checkpoint `pending`
-各dependency checkpoint `published`
-各dependency pathがcurrent filesystemでexact absent
- current directory child digestがexpected empty digest

Postcondition:

- directory path absent
- parent/root binding unchanged

#### Preservation / collapsed absence

journal actionではない。`OperationJournal.preservation_witnesses` / `absence_witnesses`へ保存し、first mutation前とverifyingでrevalidateする。

### Plan validation

`build_executable_mutation_plan()`はdeprovisionで次を拒否する。

- blocker非空
- action allowlist外
- `preserve` / `block` / already-absent actionがmutating action tupleに混入
- generated contractがmissingまたは二系統input由来
- duplicate/conflicting/ancestor-overlap action
- directory dependencyがaction orderでpriorでない
- dependency actionが`prune`/`remove-empty-directory`以外
- incomplete parent chain/pre/postcondition
- witness overlap/conflict
- plan digestの非canonical入力

## Journal / guard design

### Wire versions and deprovision metadata

- `.distribution-journal.json`: schema version 1を維持。
- journal protocol: version 2を維持。
- `.distribution-retry.json` forward guard: schema version 2を維持。
-新規purpose/authority pairを追加する。
- protocol-2 deprovision journalへ`preservation_witnesses`、`absence_witnesses`をimmutable top-level metadataとして追加する。
- directory dependencyは`OperationJournalAction.precondition["dependency_paths"]`とexpected child digestへ保存する。

Parser rules:

- deprovision journalは両witness fieldを必須とし、canonical sort/digest/relative path/typeをstrict validationする。
- fresh/recognized journalでnon-empty deprovision witness fieldを拒否する。
- `preserve`/`block` action recordをdeprovision journalで拒否する。
- action/witness/condition field omissionをself-rehashしてもplan mismatchとして拒否する。

### Deprovision guard

```text
schema_version = 2
purpose = deprovision-journal-forward-only
operation = deprovision
root_identity = exact bound root
contract_identity = current contract
plan_digest = canonical deprovision plan
operation_id = fresh unpredictable ID
journal_digest = absent before journal, exact after journal binding
```

`purpose`だけを書き換えたforged guard、authority mapping不一致、self-rehashed journal、action field omissionを拒否する。

### Reachable journal state table

次のtableはprotocol 2の`intent="deprovision"`にだけ適用する。journal parserはintent/authority/purposeのexact pairを検証してからintent-specific state validatorへdispatchし、fresh/recognized journalの成立済みcheckpoint semanticsを本Issueで変更しない。

| Journal status | Allowed checkpoints | Required invariant | Next durable transition |
|---|---|---|---|
| `prepared` | all `pending` | target mutation 0。action order、dependencies、witnesses、plan digest valid。 | status=`executing`。 |
| `executing` | each action `pending` or `published`; `verified`は0 | published actionはexact postcondition一致。published setはdeterministic action orderのprefix/topological closure。directoryをpublishedにする前に全dependencyがpublished + exact absent。 | all actions published後だけstatus=`verifying`。 |
| `verifying` | all actions `published` | pending/verifiedは0。target mutationを新規実行しない。full post-assessmentで全action postcondition、preservation witness、absence witness、root/parent/unknown closed setを確認する。 |一回のatomic journal publicationで全action=`verified`かつstatus=`completed`。 |
| `completed` | all actions `verified` | full post-assessment成功済み。target action再実行不可。 | guard cleanup、journal cleanup。 |

Forbidden examples:

- `executing` + any `verified`
- `verifying` + any `pending` or `verified`
- `completed` + any non-`verified`
- directory `published` while dependency `pending`
- dependency `published` but target not exact absent
- preservation witness represented ascheckpointed action

### State transition

```text
read-only
  absent
    -> assessment
    -> planned                         # dry-run; write 0

apply, blocker-free, no recovery metadata
  no mutating action
    -> read-only post-assessment
    -> completed                       # protocol metadata write 0

apply, blocker-free, mutating actionあり
  absent
    -> guard-prepared                  # durable guard; target write 0
    -> journal-prepared                # prepared / all pending
    -> executing                       # pending -> published only
       -> leaf prune published
       -> directory dependency check
       -> directory rmdir published
    -> verifying                       # all published; mutation 0
    -> completed                       # atomic all verified + status completed
    -> guard-removed
    -> journal-removed                 # terminal success
```

### Write boundary

mutating actionがあるoperationのfirst target mutationはguardとjournalがdurableで、predecessor identity、witness、source、root bindingが再検証された後だけ許可する。blockerがある場合はprotocol metadataも作らない。recovery metadataが存在しないno-op applyはprotocol metadataを作らずread-only post-assessmentだけで完了する。

### Journal action execution

- `prune` regular/symlinkはexisting exact remove/quarantine helperを再利用する。
- target unlink直前にheld descriptor、visible path、preconditionを再検証する。
- unlink/rmdir後にexpected absenceを再観測してからactionを`published`へ進める。
- checkpoint publish failure後はcurrent targetを再観測し、exact preまたはexact postの一方だけに一致する場合だけ`pending`/`published`を再構成する。
- `remove-empty-directory`は全dependency `published` + exact absentをjournalとfilesystemの両方で確認する。
- unknown replacement、appeared absence witness、unknown childを削除せずfail closedにする。
- preservation/absence witnessはexecuting中にcheckpointを進めず、first mutation前とverifyingで再評価する。

### Exact empty-directory kernel

```python
def _remove_distribution_directory_if_bound(
    target_root: Path,
    relative_path: Path,
    *,
    expected_root_identity: DistributionRootIdentity,
    expected_directory_binding: PathIdentitySnapshot,
    dependency_postconditions: tuple[tuple[str, dict[str, object]], ...],
    expected_remaining_child_digest: str,
) -> None:
    ...
```

必須順序:

1. journal parser/serviceでdependency checkpointが全て`published`であることを確認。
2. root/parent descriptor chainをno-follow open。
3.各dependency targetをdescriptor-relativeに再観測し、exact expected-absentを確認。
4. visible directory pathとheld fdのdevice/inode/type一致。
5. current child setをheld fdから列挙し、expected empty digestとexact一致。
6. parent/root identityを再検証。
7. `rmdir(..., dir_fd=parent_fd)`。
8. parent/root identityとpath absenceを再検証。
9. callerがjournal actionを`published`へdurable更新。

recursive callを持たない。

## Dry-run flow

```text
CLI parse
 -> specs mode normalize (None or keep)
 -> package/root/recovery admission (read-only)
 -> build_deprovision_workspace_assessment()
      -> build_deprovision_contract()
      -> build_deprovision_generated_state_contract() exactly once
 -> typed planned/recovery/error DistributionProcessResult
 -> compatibility mapper(result + static request context)
```

禁止write:

- `.distribution-retry.json`
- `.distribution-journal.json`
- `.uninstall-retry.json`
- private stage/quarantine
- managed target
- backup
- version file
- directory creation/removal

blockerはtyped action outcomes/reasonsに表示する。normal blocker inventoryはpublic `planned`/exit 0で表示できる。recovery metadataが存在しsafe new operationを開始できない場合はinternal `recovery_required`、public `partial_failure`/exit 1。malformed/unsupported eligibilityはinternal/public `error`/exit 2。

## Apply flow

1. CLIが`--apply --keep-specs`を確認する。
2. root operation lockをacquireする。
3. admission、source capture、root bindingを再実行する。
4. `build_deprovision_workspace_assessment()`でsingle generated contract、preservation witness、collapsed absence witnessを作る。
5. blockerがあれば`blocked` resultを返し、guard/journal/stage/target write 0。
6. executable planとdigestを発行する。mutating action tupleはpresent targetの`prune` / existing directoryの`remove-empty-directory`だけ。
7. recovery metadataが存在せずmutating actionが0件なら、guard/journal/legacy marker/stageを作らずfull read-only post-assessmentを行う。preservation/absence witnessとroot/nearest parent bindingが一致すればtyped `completed`、`phase=complete`、`last_completed_phase=post-verified`を返す。
8. existing deprovision guard/journalがあればsame-plan admissionへ進む。journalがある場合はjournal action set/witnessを正本としcurrent collapseで置換しない。
9. mutating actionがありrecovery metadataがなければguardをdurable publishする。
10. journalをprepareし、全action`pending`、witness metadata、dependencyをdurable bindする。
11. journalを`executing`へ進め、source/root/parent/witnessをfirst mutation直前に再検証する。
12. leaf `prune`を実行し、exact absence後に各actionを`published`へ進める。
13.各directory actionについてdependency childが全て`published`かつexact absentであることを確認し、empty digest一致後にrmdirし、directoryを`published`へ進める。
14. 全mutating actionが`published`であることを確認してjournalを`verifying`へ進める。
15. target mutationなしでfull post-assessmentを行い、removed paths、preservation witnesses、absence witnesses、root/parent、unknown closed setをverifyする。
16.一回のatomic journal publicationで全actionを`verified`、statusを`completed`へ進める。
17. forward guardをexact cleanupする。
18. completed journalをexact cleanupする。
19. 追加のworkspace cleanupを行わずtyped `completed` resultを返す。
20.任意のfailure return前にprivate result builderがphase、last completed、action outcomes、failed/pending paths、errors、retry policyを確定する。CLIへjournal interpretationを委ねない。

## Root / parent / child identity algorithm

### Root binding

- operation開始時にdevice/inode/typeをcaptureする。
- apply中はroot lockを保持する。
-各mutation boundaryでvisible rootとheld root fdを再照合する。
- root replacement/rebindは追加mutationを停止する。

### Parent chain and absence collapse

通常のmutating actionはrootからtarget parentまでのordered `PathIdentitySnapshot`をpreconditionに持つ。ただしauthorized earlier actionがancestor directoryのctime/link countを変えるため、execution時のstable parent bindingはdevice/inode/type/modeで比較し、namespaceはprior `published` actionから導出したexpected child digestで比較する。

- existing parent: directory、device、inode、type、modeを固定。initial ctime/link countはaudit evidenceであり、authorized prior child mutation後のidentity equality条件にしない。
- executorはactionごとに`current_parent_bindings` / expected child digestを更新する。更新可能なのは直前までのjournal `published` actionのexact postconditionだけであり、plan/journal authorityを変更しない。
- crash resumeはjournalのpublished setからsame expected parent child digestを再構成し、filesystemと一致する場合だけ前進する。同じinodeでもunknown appearance/disappearance、mode change、unexplained child setはblockする。
- deprovisionはmissing parentを作成しない。
- top-down observationでcontract-owned ancestorがmissingなら、最初のmissing owned ancestorへcollapseし、nearest existing parent bindingとmissing suffixをwitness化する。
- collapse配下のdescendant parent snapshot/actionを生成しない。
- contract-owned ancestorより上位のmissing component、unbound nearest ancestor、symlink/special parentはblock。
- assessment後のcollapsed root appearanceはnew actionへ再分類せず、journal前はblocked、journal後はrecovery required。
- existing journal resumeではjournalのfull parent chain/pre/postconditionを使い、新規collapseでactionを消さない。
- journal fieldを欠落・並べ替えたself-rehashed recordをplan mismatchとして拒否する。

### Directory child digest and dependency

- held directory fdから`listdir(fd)`する。
- childを`stat(..., follow_symlinks=False)`する。
- regular contentはheld fdからhashする。
- symlinkはreadlinkする。
- child recordをcanonical sortする。
- assessmentのinitial digest、各directory actionのexpected remaining digest、ordered dependency pathsをplan/journalへ記録する。
- action間のexpected changeはprior child actionが`published`で、current targetがそのexact expected-absent postconditionに一致する場合だけ導出する。
- `verified` checkpointをdirectory execution dependencyに使用しない。
- unknown child appearance、owned child unexpected disappearance、same-content inode replacement、type/mode/link topology変化はmismatch。

### Preservation tree digest

- root bindingと全descendant recordをcanonical hashする。
- regular bytesのSHA-256を含む。
- content bytes、absolute pathはjournalへ書かない。
- apply前、first mutation前、verifyingのfull post-assessmentで再評価する。
- mutation中のconcurrent changeはoperation successを拒否しjournalを保持する。

### Collapsed absence digest

- nearest existing ancestorのdevice/inode/type、missing suffix、owned descendant contract digestをhashする。
- missing subtreeをfilesystem traversalしない。
- no-op post-assessment、first mutation前、verifyingでmissing suffixが依然absentであることをnearest existing held ancestorから再検証する。
- appearanceしたpathのcontent/typeをownershipへ昇格しない。

## Legacy marker / new journal admission matrix

| Observed state | default/keep dry-run | `--apply --keep-specs` | Mutation authority |
|---|---|---|---|
| no recovery metadata | normal assessment | new guard/journal | new deprovision planのみ |
| valid legacy `.uninstall-retry.json` only | `recovery_required`; marker保持 | write前停止 | なし。自動変換禁止 |
| malformed/symlink/hardlink/special legacy marker | reason=`legacy-marker-invalid`、public `error`/exit 2、evidence保持 | write前停止 | なし |
| legacy marker + distribution guard/journal | reason=`dual-recovery-state`、public `partial_failure`/exit 1 | write前停止 | なし |
| deprovision schema-2 guard only | same root/intent/authority/contract/planが再構成できればpre-journal resume | journal prepare後same-plan resume | guardに記録されたplanだけ |
| deprovision guard + nonterminal journal | diagnostic inspection | exact journal resume | exact pending actionsだけ |
| completed journal + guard | cleanup-only state | postcondition再検証後cleanup | target action再実行不可 |
| completed journal only | cleanup-only state | postcondition再検証後journal cleanup | target action再実行不可 |
| nonterminal journal withoutguard | recovery mismatch | write前停止 | なし |
| recognized/fresh guard or journal | intent mismatch | write前停止 | なし |
| deprovision journal + `--remove-specs` | D4 routeでdiagnostic | checkpointを進めず停止 | purgeへ昇格不可 |
| legacy purge marker + keep invocation | ambiguous legacy state | write前停止 | deprovisionへ再解釈不可 |

### Legacy marker negative proof

current legacy bytesは複数root、keep/remove、複数phase、複数planで同一になる。current treeだけからoriginal deleted actionsとcheckpointを再構成しても、already-removed assetとoriginally-absent assetを区別できない。したがって`replace_marker=`等のexisting conversion seamへlegacy uninstall markerを渡さない。

stable internal reason:

- `legacy-marker-unconvertible`
- `legacy-marker-invalid`
- `dual-recovery-state`
- `journal-intent-mismatch`
- `journal-authority-mismatch`
- `journal-plan-mismatch`
- `journal-root-mismatch`
- `journal-protocol-incompatible`
- `journal-precondition-mismatch`
- `preservation-witness-mismatch`
- `directory-child-set-mismatch`

## Public compatibility mapper

### Mapper boundary

CLI mapper signatureはconceptually次で固定する。

```python
def _uninstall_payload_from_result(
    result: DistributionProcessResult,
    *,
    target_label: str,
    apply: bool,
    specs_mode: Literal["keep"] | None,
) -> dict[str, object]:
    ...
```

CLIが追加できるのはstatic request contextだけである。mapperはjournal path、guard path、legacy marker、filesystemをopenしない。serviceが返すresultに必要fieldが欠けている場合はfallback解釈せずprogramming errorとしてtestで拒否する。

### Status / exit mapping

| Internal | Public `status` | Exit |
|---|---|---|
| `planned` | `planned` | 0 |
| `completed` | `completed` | 0 |
| `blocked` | `blocked` | 1 |
| `recovery_required` | `partial_failure` | 1 |
| `error` | `error` | 2 |

### Durable-state-to-result population

Private service helper `_distribution_process_result_from_state()`だけがjournal/guard stateを読む。最低規則:

| Observed service/durable state | Result status | `phase` | `last_completed_phase` | path/error rules |
|---|---|---|---|---|
| eligibility before assessment error | `error` | `preflight` | `not-started` | top-level errorのみ。 |
| planned assessment | `planned` | `preflight` | `preflight-complete` | dry-run outcomes、failed/pending/errors空。 |
| blocker apply | `blocked` | `preflight` | `preflight-complete` | blocker pathsを`failed_paths`、outcome=`preserved`、allowlisted top-level operation errorを一件以上。 |
| valid legacy marker-only | `recovery_required` | `preflight` | `not-started` | top-level `legacy-marker-unconvertible` operation error、retry=`manual-recovery`。 |
| invalid legacy marker | `error` | `preflight` | `not-started` | top-level `legacy-marker-invalid`。 |
| guard-only | `recovery_required` | `marker-write` | `marker-written` | reconstructed planの全mutating pathsをpending/failed、journal pathをfailedへ入れ、allowlisted recovery errorを返す。 |
| journal `prepared` | `recovery_required` | `uninstall-apply` | `marker-written` | checkpoint pending pathsをpending/failedへ入れ、allowlisted recovery errorを返す。 |
| `executing`、leaf pendingあり | `recovery_required` | `uninstall-apply` | `marker-written` | failed actionとpending checkpoint pathをfailedへ、pending checkpointをpendingへ入れ、allowlisted recovery errorを返す。 |
| leaf actions全published、directory pendingあり | `recovery_required` | `root-cleanup` | `uninstall-applied` | pending directory pathsをpending/failedへ入れ、allowlisted recovery errorを返す。 |
| journal `executing`、全mutating action `published` | `recovery_required` | `post-verify` | `uninstall-applied` | final checkpoint後・status transition前。target pendingなし、allowlisted recovery errorを返し、post-assessmentだけを再開。 |
| journal `verifying` | `recovery_required` | `post-verify` | `uninstall-applied` | target pendingなし。witness/postcondition failure pathをfailed、allowlisted recovery errorをtop-levelへ。 |
| journal `completed` + guard | `recovery_required` | `marker-finalization` | `post-verified` | guard pathをfailed、guard cleanup errorをtop-levelへ。target action再実行なし。 |
| completed journal only | `recovery_required` | `marker-finalization` | `marker-finalized` | journal pathをfailed、journal cleanup errorをtop-levelへ。 |
| mutating success | `completed` | `complete` | `marker-finalized` | failed/pending/errors空。 |
| metadata-free no-op success | `completed` | `complete` | `post-verified` | marker finalizationを実行したと偽装しない。 |

Retry policy populationは次で固定する。normal deprovision result（planned、completed、blocked、same-plan recovery、preflight error）は`same-keep-command`、legacy marker ambiguity/invalidityは`manual-recovery`、public retryを持たないprogramming errorだけ`none`とする。CLI mapperはstatic `specs_mode == "keep"`かつpolicy=`same-keep-command`のときだけcommandを生成するため、default dry-runの`specs_mode=None`は`null`、keep dry-run/success/blocked/recovery/errorはnon-null、legacy markerは`null`となる。

### Action outcome population

| Domain observation / journal state | `DistributionActionOutcome.status` | Public summary |
|---|---|---|
| dry-run existing `prune` / planned directory | `would_remove` | `would_remove` |
| missing leaf / collapsed absence root | `already_removed` | `already_removed` |
| published/verified leaf prune | `removed` | `removed` |
| published/verified directory rmdir | `empty_dir_removed` | `empty_dir_removed` |
| preservation witness | `preserved` | `preserved` |
| blocker | `preserved`、overall blocked/planned | `preserved` |
| journal checkpoint pending | `pending` | `pending` |
| action-specific failure | `failed` with sanitized `error` | `failed` |

Collapsed absenceはrootごとにone public `already_removed` outcomeを生成し、descendant action outcomeを展開しない。これによりaction emissionとplan digestをdeterministicに保つ。

### Failed paths、pending paths、errors

- `pending_paths`: journal checkpoint `pending`のmutating action pathだけをdeduplicateしcanonical sortする。`published`だが未verifiedのpathをpendingと表示しない。
- `failed_paths`: action-specific failure、blocker、preservation/absence witness mismatch、および**全`pending_paths`**のrepository-relative pathをcanonical unionする。現行schema-v1 compatibilityとして、pending pathは`failed_paths`と`pending_paths`の双方へ現れる。
- action `error`:そのpath固有のallowlisted sanitized message。存在しない場合は`null`。
- top-level `errors`: `blocked` / `recovery_required` / `error`では少なくとも一件のallowlisted operation errorを持つ。protocol、admission、guard/journal cleanup、global postcondition errorを収容し、action固有errorのraw textを重複させない。`planned` / `completed`では空。
- exception raw text、absolute path、SHA、content、nonce、credentialを含めない。

### Category mapping

current category valuesをpath/contract evidenceからpureに生成する。

- `agent_skill`
- `native_agent`
- `bootstrap_only`
- `product_reusable`
- `obsolete_managed`
- `scaffold_managed`
- `generated_state`
- `spec_history`
- `shortcut`
- `unmanaged`
- `empty_dir`

categoryはownership authorityではない。mutation可否はdomain contract/action/preconditionが決める。

### JSON field mapping

| Field | Source / rule |
|---|---|
| `schema_version` | constant `1` |
| `target` | static resolved target。public statusが`blocked`または`partial_failure`のときだけshell-safe relative labelまたは`unavailable`へsanitizationする。`planned`、`completed`、`error`は現行どおりresolved target文字列。 |
| `mode` | static request: `dry-run` / `apply` |
| `apply` | request boolean |
| `specs_mode` | default dry-run=`null`、keep=`"keep"` |
| `status` | result status mapping |
| `phase` | `result.phase` |
| `last_completed_phase` | `result.last_completed_phase` |
| `retry_command` | `result.retry_policy` + static target/specs mode。`same-keep-command`かつ`specs_mode="keep"`ならplanned/completed/blocked/partial/errorを問わずshell-safe `--apply --keep-specs` command、default dry-runのmode `null`と`manual-recovery`/`none`は`null`。 |
| `failed_paths` | `result.failed_paths` |
| `pending_paths` | `result.pending_paths` |
| `summary` | `result.action_outcomes`のstatus count、existing keysを常に出す |
| `actions` | action outcomesのpath/category/status/reason/error |
| `guidance` | result status/retry policy/reasonのpure allowlist mapping。purgeへ誘導しない。 |
| `errors` | `result.errors`のsanitized message list |

### Exactly one stdout object

`--json` routeはservice resultをpayloadへ変換してから一回だけ`json.dumps(..., sort_keys=True)`する。service、journal、kernelはstdout/stderrへprintしない。

### Text output

text rendererも同じpayload/resultを使用し、header、mode、status、phase、last completed、retry、failed paths、summary、actions、errors、guidanceのexisting orderを維持する。JSON用とtext用でjournal stateを別解釈しない。

### Sanitization

- `blocked` / `partial_failure`のabsolute targetだけをrelative labelまたは`unavailable`へ変換する。`planned` / `completed` / `error`のtarget fieldはcurrent schema-v1 behaviorを維持する。
- exception textをそのまま公開しない。
- action/top-level errorはstable allowlist messageへ変換する。
- file bytes、SHA、credential、source absolute path、stage nonceを公開しない。
- unknown internal reasonはgeneric sanitized errorへmappingし、raw valueを公開しない。

## Failure semantics and crash windows

| Window / failure | Durable state | Required next behavior / typed result |
|---|---|---|
| assessment failure | none | write 0、`error/preflight/not-started`。 |
| blocker found | none | write 0、planned dry-runまたはblocked apply、`preflight-complete`。 |
| generated-state conflict / legacy-unproven | none | all target write 0。conflicting entriesを保持。 |
| collapsed absence appearance before guard | none | appeared entryを削除せずblocked。 |
| guard publish failure | noneまたはrestored predecessor | target write 0、typed error/recovery。 |
| guard published / journal absent | guard only | same-plan reconstruction後journal prepare。mismatch/absence appearanceは停止。 |
| journal publish failure | guard retained | target write 0、same-plan retry。 |
| leaf action before unlink failure | journal executing / action pending | exact precondition一致時だけretry。 |
| unlink後checkpoint failure | target may be absent | pre/post一方だけにexact一致すればpending/publishedを再構成。 |
| child published / directory pending | executing | child exact absentを再確認してdirectoryへ進む。verifiedを待たない。 |
| directory rmdir後checkpoint failure | directory absent / checkpoint pending | exact postconditionからdirectoryをpublishedへ再構成。 |
| all published / verifying transition failure | executing or verifying | atomic predecessor stateを読み、all publishedならverifyingへ。 |
| verifying中crash | verifying / all published | target mutationを再実行せずfull post-assessmentを再実行。 |
| atomic completed publication failure | verifying or completed | verifyingならall published、completedならall verified。mixed stateはparser拒否。 |
| unknown replacement/child/absence appearance after journal | journal retained | entryを削除せずrecovery required。 |
| preservation tree change | journal retained | completedにせずwitness mismatch。 |
| completed publish後guard cleanup failure | completed journal+guard | target再実行なし、cleanup-only retry、last=`post-verified`。 |
| guard cleanup後journal cleanup failure | completed journal only | target再実行なし、journal cleanup-only、last=`marker-finalized`。 |
| metadata-free no-op | none | full post-assessment後completed、last=`post-verified`、protocol/target write 0。 |
| terminal cleanup完了 | none | completed、last=`marker-finalized`。以降fallible workspace mutationなし。 |

whole-operation rollbackは行わない。published/verified removalをrecreateしない。managed assetsの再導入はoperation recoveryではなく、terminal deprovision後の別explicit `spec-dock init`/`update`である。

全failure returnはservice内でtyped resultへ変換する。CLIがdurable stateを開いてphase、failed path、errorを補完しない。

## Darwin / Linux kernel差とtestability

- current POSIX kernelの`fcntl.flock`、`O_NOFOLLOW`、`O_DIRECTORY`、`dir_fd`、held descriptor、atomic rename/exchange/no-replace helperを再利用する。
- LinuxとDarwinの既存branchを保ち、platform policyをservice/CLIへ漏らさない。
- POSIX/Darwinにはexpected inodeを条件にpathnameをdeleteする一般的primitiveがないため、advisory lockを無視するsame-UID processによるlast-checkとsingle syscall間だけの差し替えをatomic CASとして約束しない。
-観測できたrebind/replacement/unknown childはmutation boundaryで必ずfail closedにする。
- Windows fallbackを追加しない。required capability不足はfirst write前にdiagnosticする。
- unit testsはkernel helperへfailure/interposition hookを置き、productionにruntime toggleを追加しない。

## Migration strategy

### Explicit route split

`_run_uninstall()`はspecs modeを一度だけ解決し、次へdispatchする。

```python
if specs_mode == "remove":
    return _run_uninstall_remove_specs_compatibility(...)
return _run_uninstall_deprovision(...)
```

- default/keep routeはnew serviceだけを呼ぶ。
- new serviceがerrorを返してもlegacy helperへfallbackしない。
- remove compatibility routeがerrorを返してもdeprovisionへfallbackしない。
- environment variable、feature flag、automatic fallbackを作らない。

### Deprovision legacy call-edge removal

同じchange setでdefault/keep routeから次のcall edgeを除去する。

- `_build_uninstall_plan()`
- `_apply_uninstall_plan()`
- `_remove_uninstall_path()`
- `_remove_uninstall_tree_fd()`
- `_cleanup_empty_uninstall_dirs()`
- `_verify_uninstall_postcondition()`
- `_write_uninstall_retry_marker()`
- `_finalize_uninstall_retry_marker()`

`_UninstallTargetIdentity` / `_UninstallAction`はdefault/keep presentation/authorityから除去する。D4 compatibilityが物理的に必要とするlegacy symbolはsource comment、route test、Issue 371 handoffで明示し、deprovision routeから到達不能にする。

### No dual writer

- deprovision applyは`.distribution-retry.json` schema-2 guardと`.distribution-journal.json`だけを書く。
- `.uninstall-retry.json`を新規作成・更新・削除しない。
- existing legacy markerを見つけた場合は保持して停止する。

### Documentation migration

- shipped docsの「partial failureでは`.uninstall-retry.json`をretry」の記述をdefault/keepについてnew journalへ更新する。
- `--remove-specs`はIssue 371 compatibilityでlegacy markerを使い得ることをowner付きで分離する。
- automatic legacy conversionを案内しない。

## Testability design

### Pure assessment tests

- current/historical/missing managed leaf
- modified/mode drift/unknown
- exact/unknown symlink
- hardlink/special file
- managed root unknown child
- initiatives/workbench witness
- deterministic child digest/action order
- blockerからplan発行不可

### Journal tests

- deprovision purpose/authority roundtrip
- forged purpose-authority pair
- guard-only resume
- journal action field omission/self-rehash
- root/intent/authority/contract/plan/protocol mismatch
- action pre/post recovery
- preservation witness mismatch
- completed cleanup-only states

### Kernel tests

- exact regular/symlink prune
- exact empty directory removal
- unknown child appearance
- directory/parent/root rebind
- same-content inode replacement
- hardlink/special file
- rmdir failure/checkpoint failure
- no generic recursive path

### CLI tests

- required seven-row CLI matrix
- schema-v1 golden for planned/completed/blocked/partial/error
- exactly one stdout object
- text golden
- exit mapping
- relative/shell-safe retry
- secret/absolute path sanitization
- remove-specs route isolation
- legacy symbol/call-edge absence for default/keep

## Requirement / Design traceability

| Requirement ID | Design element |
|---|---|
| I370-F01 | D370-CLI, D370-ASSESS, D370-SERVICE |
| I370-F02 | D370-ASSESS, D370-SERVICE, D370-RESULT |
| I370-F03 | D370-CONTRACT, D370-ASSESS, D370-PLAN, D370-KERNEL |
| I370-F04 | D370-DATA, D370-ASSESS, D370-SERVICE |
| I370-F05 | D370-DATA, D370-ASSESS |
| I370-F06 | D370-ASSESS, D370-PLAN, D370-SERVICE |
| I370-F07 | D370-INT, D370-CONTRACT, D370-LEGACY |
| I370-F08 | D370-DATA, D370-SERVICE, D370-JOURNAL |
| I370-F09 | D370-DATA, D370-ASSESS, D370-PLAN, D370-SERVICE |
| I370-F10 | D370-CLI, D370-MIG |
| I370-S01 | D370-CLI, D370-SERVICE, D370-KERNEL |
| I370-S02 | D370-DATA, D370-KERNEL |
| I370-S03 | D370-DATA, D370-KERNEL |
| I370-S04 | D370-DATA, D370-KERNEL |
| I370-S05 | D370-DATA, D370-ASSESS |
| I370-S06 | D370-CONTRACT, D370-ASSESS |
| I370-S07 | D370-CONTRACT, D370-ASSESS, D370-PLAN |
| I370-S08 | D370-PLAN, D370-JOURNAL, D370-KERNEL, D370-MIG |
| I370-S09 | D370-KERNEL, D370-JOURNAL |
| I370-S10 | D370-DATA, D370-PLAN, D370-JOURNAL, D370-SERVICE |
| I370-S11 | D370-CONTRACT, D370-SERVICE, D370-JOURNAL |
| I370-S12 | D370-ASSESS, D370-SERVICE |
| I370-S13 | D370-CONTRACT, D370-KERNEL |
| I370-S14 | D370-DATA, D370-KERNEL, D370-JOURNAL |
| I370-S15 | D370-JOURNAL, D370-SERVICE |
| I370-S16 | D370-DATA, D370-ASSESS, D370-SERVICE, D370-RESULT |
| I370-C01 | D370-CLI, D370-MAP |
| I370-C02 | D370-RESULT, D370-MAP |
| I370-C03 | D370-MAP |
| I370-C04 | D370-RESULT, D370-MAP |
| I370-C05 | D370-MAP |
| I370-C06 | D370-RESULT, D370-MAP |
| I370-C07 | D370-RESULT, D370-MAP, D370-LEGACY |
| I370-C08 | D370-MIG, D370-MAP |
| I370-C09 | D370-RESULT, D370-MAP, D370-CLI |
| I370-R01 | D370-JOURNAL, D370-SERVICE |
| I370-R02 | D370-INT, D370-JOURNAL |
| I370-R03 | D370-DATA, D370-JOURNAL |
| I370-R04 | D370-JOURNAL |
| I370-R05 | D370-JOURNAL, D370-RESULT |
| I370-R06 | D370-DATA, D370-JOURNAL, D370-LEGACY |
| I370-R07 | D370-LEGACY, D370-RESULT |
| I370-R08 | D370-INT, D370-CLI, D370-LEGACY |
| I370-R09 | D370-JOURNAL, D370-SERVICE |
| I370-R10 | D370-RESULT, D370-MAP, D370-LEGACY |
| I370-O01 | D370-CONTRACT, D370-ASSESS |
| I370-O02 | D370-DATA, D370-PLAN, D370-MAP |
| I370-O03 | D370-PLAT, D370-KERNEL |
| I370-O04 | D370-JOURNAL, D370-RESULT, D370-MAP, D370-PLAT |

## Risks and controls

| Risk | Control |
|---|---|
| active/.agent membershipからunknownを誤削除 | single generated producer、exact slot/kind/schema/semantic predicate、unknown/legacy conflict blocker |
| contract.generated stateとcaller generated assetsがdiverge | deprovision専用assessment wrapper、generic generated-assets inputをtype/call graphで禁止 |
| preserved spec historyのconcurrent mutationをsuccess扱い | pre/first-write/verifying preservation witness |
| already-absent subtreeでmissing parentをunsafe扱い、またはdescendant actionを大量発行 | top-down owned-ancestor collapse、nearest existing binding、one root outcome、no mutating action |
| absence witness後にexternal entryがappearance | new authorityを発行せずblocked/recovery required |
| directory actionがunreachable verified dependencyを要求 | dependencyをprior `published` + exact absentに固定、reachable parser table、crash tests |
| preserve recordに到達不能checkpointを持たせる | preserve/blockはjournal actionではなくimmutable witness/diagnostic |
| journal authorityからpurgeへ昇格 | explicit `deprovision` intent/authority、remove route隔離、mismatch test |
| legacy markerをcurrent invocationへ誤帰属 | automatic conversion禁止、marker保持 |
| directory ctimeを誤ってstable bindingに使用 | directory bindingとmutation snapshotを分離 |
| action後checkpoint失敗で二重削除 | exact pre/post一意判定、pending/published再構成 |
| CLIがjournalを再解釈しJSON/textでdrift | fully-populated typed result、mapper source/monkeypatch test、single payload boundary |
| D4 compatibilityがhidden fallbackになる | explicit entrypoint、source/AST call-edge tests、no feature flag |
| implementationがgeneric filesystem frameworkへ膨張 | exact leaf unlinkとexact dependency-bound empty-directory rmdirだけ |

## Material decision gates

本設計時点でProduct、Policy、Security、architectureのmaterial decisionは上記で固定する。実装者は次のいずれかを発見した時点で実装を停止し、Requirement/Designの更新を要求する。

1. fixed SHAのruntime outputについて、Designのcurrent generated slot/schema/semantic predicateと矛盾するproducerが見つかる。
2. current generated JSONをsemanticに検証できず、pathnameだけで削除する必要が生じる。
3. deprovision assessmentへcanonical producer以外のgenerated inputを渡さなければ既存fresh/recognized routeを維持できない。
4. protocol-2 journalへpreservation/absence witness、directory dependencyをlosslessに保存できず、preserveをcheckpointed actionへ戻す必要が生じる。
5. prior child `published` + exact absentではdirectory actionを安全に実行できず、`verified`をexecuting dependencyに戻す必要が生じる。
6. owned ancestor absenceをnearest existing bound ancestorから証明できず、unproven missing parentをtrustedとして扱う必要が生じる。
7. unknown/modified childを削除しなければcurrent public keep behaviorを維持できない。
8. legacy `.uninstall-retry.json`を変換しなければnew routeを開始できない。
9. `--remove-specs` behaviorまたはauthorityを変更しなければroute splitできない。
10. `DistributionProcessResult`または同等のtyped inputだけからphase、last completed、failed/pending paths、action/top-level errors、retry policyを一意に生成できない。
11. public schema version、key set、exit mappingを変更しなければtyped resultをmappingできない。
12. required POSIX capabilityなしでmutationを続けるfallbackが必要になる。

これらはcoderが推測で解消してはならない。Issue 371 purgeまたはIssue 372 parity/closureへ責務を移してIssue 370を見かけ上完了させることも禁止する。
