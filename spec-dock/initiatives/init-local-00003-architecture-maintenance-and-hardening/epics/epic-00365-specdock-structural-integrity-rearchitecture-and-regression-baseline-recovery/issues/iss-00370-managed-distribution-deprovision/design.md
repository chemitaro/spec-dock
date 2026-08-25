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

基準commitは `fc02e1215d2b9e056a2c18bd1411fe489efdf2f2` である。

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
- failure時のrelative target、sanitized action/operation error、shell-safe retry command

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
- spec historyとknown preserved treeを`DistributionPreservationWitness`としてplan digestとpost-assessmentへ束縛する。
- default/keep dry-runはserviceのassessment resultからpublic planを生成し、guard/journal/marker/stageを書かない。
- applyはschema-2 guard、protocol-2 journal、per-action checkpoint、post-assessmentを使用する。
- legacy `.uninstall-retry.json`は変換せず、typed recovery stateを返す。
- CLIはdeprovisionについてparse/dispatch/presentationだけを行い、ownership、tree recursion、journal transition、target mutationを持たない。
- `--remove-specs`はIssue 371 ownerの明示的compatibility routeとして隔離し、本Issueのserviceから到達不能にする。

## Design element registry

三文書のtraceabilityで次のstable design element IDを使用する。

| Design ID | 設計要素 | 主なsection / owner |
|---|---|---|
| D370-CLI | CLI parse、root lock/binding、default/keepとremove routeの一回限りのdispatch | `src/spec_dock/cli.py` |
| D370-INT | `deprovision` intent、`uninstall` plan mapping、action allowlist、authority、guard purpose | Intent、authority、action grammar |
| D370-DATA | tree entry、directory mutation snapshot、preservation witnessのimmutable data model | Proposed data model |
| D370-CONTRACT | managed/preserved root contractとbounded inventory source | Distribution Contract |
| D370-ASSESS | no-follow observation、complete classification、blocker gate | Deprovision assessment algorithm |
| D370-PLAN | executable plan、action order、pre/postcondition、canonical digest | Executable plan |
| D370-JOURNAL | schema-2 guard、protocol-2 journal、checkpoint、resume、terminal cleanup | Journal / guard design |
| D370-KERNEL | exact regular/symlink pruneとbound empty-directory removal | Filesystem kernel |
| D370-SERVICE | dry-run、no-op、journaled apply、post-assessment、typed result | Service / flows |
| D370-MAP | schema-v1 JSON、text、phase、exit、sanitization、retry mapping | Public compatibility mapper |
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
7. `WorkspaceAssessment` / `DistributionProcessResult`をschema-v1 JSON、text、exit codeへmappingする。
8. exactly one stdout object、stderr、sanitization、retry commandを維持する。

禁止事項:

- ownership classification
- managed tree traversal
- recursive unlink/rmdir
- journal/guard writeまたはcheckpoint transition
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
- preservation witness
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

`fresh` grammarはIssue 369 Reportの契約から変更しない。`deprovision`で`create`、`upgrade`、`ensure-directory`を受理しない。already-absent owned targetは`prune`のmissing preconditionとして表現する。

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
- regularは`size`、`sha256`必須、`link_target=None`。
- symlinkは`link_target`必須、targetをfollowしない。
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
    child_entries: tuple[DistributionTreeEntrySnapshot, ...]
    child_digest: str
```

`binding`のdirectory identityはdevice/inode/typeを安定bindingとして使う。child mutationでdirectory ctimeが変わるため、child removal後のbinding比較にctime exactを要求しない。initial observationのctimeはaudit evidenceとして保持し、visible pathとheld descriptorが同じdevice/inodeを指すことを毎mutation境界で再検証する。

`child_digest`は次のcanonical recordをrelative path byte orderでsortしたSHA-256とする。

```text
version
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
```

absolute path、timestamp、process ID、random nonceをdigest inputにしない。

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

### Existing type extensions

```python
@dataclass(frozen=True)
class WorkspaceAssessment:
    intent: JournaledDistributionIntent
    root_identity: DistributionRootIdentity
    contract_identity: str
    distribution_plan: DistributionPlan
    actions: tuple[DistributionAction, ...]
    blockers: tuple[DistributionAction, ...]
    directory_snapshots: tuple[DistributionDirectoryMutationSnapshot, ...] = ()
    preservation_witnesses: tuple[DistributionPreservationWitness, ...] = ()

@dataclass(frozen=True)
class ExecutableMutationPlan:
    intent: JournaledDistributionIntent
    root_identity: DistributionRootIdentity
    contract_identity: str
    plan_digest: str
    distribution_plan: DistributionPlan
    actions: tuple[DistributionAction, ...]
    directory_snapshots: tuple[DistributionDirectoryMutationSnapshot, ...] = ()
    preservation_witnesses: tuple[DistributionPreservationWitness, ...] = ()
```

Default値によりfresh/recognized call sitesのwire shapeを不必要に変更しない。`plan_digest`は新fieldをcanonical serializationへ含める。deprovisionでfieldが欠落したexecutable planは拒否する。

### Process result extension

```python
@dataclass(frozen=True)
class DistributionProcessResult:
    status: Literal[
        "planned",
        "completed",
        "blocked",
        "recovery_required",
    ]
    intent: JournaledDistributionIntent
    actions: tuple[DistributionAction, ...]
    plan_digest: str | None = None
    reason: str | None = None
    applied_paths: tuple[str, ...] = ()
    pending_paths: tuple[str, ...] = ()
```

`planned`を追加する。public uninstall statusへのmappingはCLI adapterが所有する。

## Proposed service interfaces

### Assessment

既存`build_workspace_assessment()`を拡張し、deprovision-specific tree contractをexplicit argumentで渡す。

```python
def build_workspace_assessment(
    install_root: Path,
    *,
    manifest_path: Path,
    scaffold_root: Path | None,
    target_root: Path,
    intent: JournaledDistributionIntent,
    root_identity: DistributionRootIdentity,
    deprovision_contract: DistributionDeprovisionContract | None = None,
    generated_assets: tuple[DistributionAsset, ...] = (),
) -> WorkspaceAssessment:
    ...
```

```python
@dataclass(frozen=True)
class DistributionDeprovisionContract:
    managed_roots: tuple[str, ...]
    preserved_roots: tuple[str, ...]
    removable_shortcuts: tuple[DistributionAsset, ...]
    generated_assets: tuple[DistributionAsset, ...]
```

Canonical values:

- managed roots: physical install-root managed assetのparent closure、`spec-dock/{docs,templates,scripts,system}`、generated `spec-dock/{active,.agent}`、exact root shortcutのparent closureのcanonical unionとする。
- preserved roots: `spec-dock/initiatives`、`spec-dock/.workbench`。
- protocol metadata `.distribution-retry.json` / `.distribution-journal.json`はcontract assetではなくjournal ownerが管理する。
- `.uninstall-retry.json`はlegacy recovery evidenceであり、remove actionへ入れない。

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

- `apply=False`: assessmentを返すだけ。guard/journal/stage/target writeを禁止する。
- `apply=True`: callerであるCLI adapterがexisting `_exclusive_distribution_operation()` / `_bound_distribution_root()`を取得済みであることを前提とし、`expected_root_identity`を必須にする。serviceはroot lockを再取得せず、entry・各mutation boundary・return直前にbound identityを再検証する。
- specs modeはservice parameterにしない。deprovision serviceはkeep-only contractであり、purge modeを表現できない。

CLI adapterは`--remove-specs`をこのfunctionへ渡せない。

### Presentation view

current `_UninstallAction`はmutation authorityとpresentationを混在させるため、default/keep routeでは使用しない。CLIに置く場合はpure viewのみとする。

```python
@dataclass(frozen=True)
class _UninstallActionView:
    path: str
    category: str
    status: str
    reason: str
    error: str | None = None
```

このtypeはidentity、expected_absent、filesystem methodを持たない。`WorkspaceAssessment` / journal resultから一方向に生成する。

## Distribution Contract と bounded root inventory

### Contract source

1. `managed_distribution.json` current assets。
2. historical exact identity catalog。
3. `assets/install_root` managed files/symlinks。
4. `assets/spec_dock` shipped scaffold files。
5. generated state contract。
6. exact root shortcut contract。
7. preserved root policy。

current assetとhistorical ownershipは区別し、historical array indexをidentityとして使わない。

### Traversal boundary

assessmentがopen/list/hashできる範囲は次だけである。

- contractで宣言されたmanaged pathのparent chain
- contractで宣言されたmanaged root subtree
- preserved root subtree
- protocol metadataのexact paths

repository全体のrecursive traversalは禁止する。cleanup boundary外siblingは列挙しない。

### Complete classification

managed root内の各entryを次のいずれかへ一意に分類する。

- exact current/historical/generated/shortcut ownership: mutating action候補
- explicit preserved root/entry: `preserve`
- missing owned entry: idempotent `prune`
- unknown/modified/unsafe: `block`

classificationされないentry、duplicate path、親子で競合するaction、unsafe relative pathがあればassessment blockerとする。

## Deprovision assessment algorithm

### 1. Admission

1. targetがreal directoryであることを確認する。
2. executing package versionとmanifestを検証する。
3. root device/inodeをcaptureする。
4. recovery stateをread-onlyに読む。
5. `.distribution-retry.json`、`.distribution-journal.json`、`.uninstall-retry.json`のdual/ambiguous stateを検出する。
6. platform capabilityを確認する。
7. applyではCLI adapterが取得したroot operation lockを保持したまま、渡された`expected_root_identity`に対して同じadmissionを再確認する。

### 2. Package contract capture

- manifest/scaffold/install-root sourceをno-followでcaptureする。
- regular source bytes、mode、device/inode/ctime/mtime/size、SHA-256をcurrent kernel contractに従って保持する。
- assessment後、plan発行直前とfirst mutation直前にsource identityを再検証する。

### 3. Managed path observation

- root descriptorからparent chainを`O_NOFOLLOW|O_DIRECTORY`でopenする。
- targetは`stat(..., follow_symlinks=False)`で観測する。
- regular fileはheld fdからSHA-256を計算し、open前後identityを照合する。
- symlinkは`readlink`し、targetをfollowしない。
- directoryはheld descriptorからchild nameを列挙する。
- enumeration orderはcanonical relative POSIX path orderとする。

### 4. Ownership classification

- current exact regular/symlink: `prune`
- historical exact regular/symlink: `prune`
- missing owned path: `prune` with missing precondition
- modified/mode mismatch/unknown: `block`
- hardlink/special/unsafe parent/symlink boundary: `block`

### 5. Scaffold root expansion

`spec-dock/{docs,templates,scripts,system}`を一つのrecursive removal actionにしない。

- each exact owned leafを`prune`へ展開する。
-各directoryのinitial child setをcaptureする。
- unknown/modified childがあればblocker。
-全owned childがremoveまたはalready absentで、preserved childが0のdirectoryだけ`remove-empty-directory`を作る。
- directory actionはdeepest-firstで、parent actionより後に配置する。

### 6. Preservation witness

- `spec-dock/initiatives`をno-follow recursive snapshotする。
- `.workbench`が存在すれば同様にsnapshotする。
- regular bytes SHA、mode、type、link topology、symlink text、directory child setをdigestへ含める。
- content自体はjournalへ保存しない。
- special file、unproven hardlink、root/parent symlinkはblocker。

### 7. Blocker gate

blockerが一件でもあれば、assessmentをdiagnosticとして返し、`build_executable_mutation_plan()`を呼ばない。dry-runはplanned viewとしてblockerを表示できるが、applyはpublic `blocked`となる。

## Executable plan とcanonical digest

### Action order

1. non-mutating `preserve` recordsをcanonical path orderでplanへ保持する。
2. `prune` actionsをchild-before-parent dependencyとcanonical pathでtopological sortする。
3. `remove-empty-directory`をdepth descending、path ascendingでsortする。
4. protocol metadata cleanupはdomain actionに混ぜず、journal finalizationが所有する。

### Digest input

- digest format version
- root identity
- `intent="deprovision"`
- `authority="managed-distribution-deprovision"`
- contract identity
- ordered actions
- action reason/provenance
- exact precondition / expected postcondition
- directory binding、initial child digest、expected remaining child digest
- preservation witness root/digest

除外:

- absolute path
- execution timestamp
- random `operation_id`
- stage nonce
- process ID
- directory ctime that is expected to change solely due to planned child mutation

### Action pre/postcondition

Regular prune:

```text
pre: exists + regular + device + inode + ctime_ns + mode + link_count=1 + size + sha256 + full parent chain
post: absent + same parent/root binding
```

Symlink prune:

```text
pre: exists + symlink + device + inode + ctime_ns + link_count + link_target + full parent chain
post: absent + same parent/root binding
```

Missing prune:

```text
pre: absent + full parent chain
post: absent + same parent/root binding
```

Empty directory removal:

```text
pre:
  initial binding: directory + device + inode
  initial child digest
  dependencies: every child action verified
  runtime expected remaining child digest = empty
post:
  absent + same parent/root binding
```

Preserve:

```text
pre/post: same preservation tree/path digest and root/parent binding
mutation handler: none
```

## Journal / guard design

### Wire versions

- `.distribution-journal.json`: schema version 1を維持。
- journal protocol: version 2を維持。
- `.distribution-retry.json` forward guard: schema version 2を維持。
-新規purpose/authority pairだけを追加する。

journal actionのexisting `precondition` / `postcondition` dictへdirectory snapshotとpreservation witnessをcanonical fieldとして追加する。top-level schema versionを増やさない。protocol version 2 parserがdeprovision condition shapeをstrict validationする。

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
    -> journal-prepared                # status=prepared; target write 0
    -> executing                       # per-action checkpoint
    -> verifying                       # all mutating actions published
    -> completed                       # post-assessment + all verified
    -> guard-removed
    -> journal-removed                 # terminal success
```

journal statusはexisting `prepared`、`executing`、`verifying`、`completed`を使用する。action checkpointは`pending`、`published`、`verified`を使用する。

### Write boundary

mutating actionがあるoperationのfirst target mutationはguardとjournalがdurableで、predecessor identityが再検証された後だけ許可する。guard/journalの作成自体はprotocol metadata writeであり、managed target mutationではないが、blockerがある場合はこれらも作らない。recovery metadataが存在しないno-op applyはprotocol metadataを作らずread-only post-assessmentだけで完了する。

### Journal action execution

- `prune` regular/symlinkはexisting exact remove/quarantine helperを再利用する。
- target unlink直前にheld descriptor、visible path、preconditionを再検証する。
- `remove-empty-directory`はnew exact directory helperを使う。
- unknown replacementを削除せず、可能な場合はcanonical pathへ復元してfail closedにする。
- checkpoint publish failure後はcurrent targetを再観測し、exact preまたはexact postの一方だけに一致する場合にstateを再構成する。
- preserve recordはmutationせず、verifying phaseでwitnessを再評価して`verified`へ進める。

### Exact empty-directory kernel

新helperはfunctional kernelに置く。

```python
def _remove_distribution_directory_if_bound(
    target_root: Path,
    relative_path: Path,
    *,
    expected_root_identity: DistributionRootIdentity,
    expected_directory_binding: PathIdentitySnapshot,
    expected_remaining_child_digest: str,
) -> None:
    ...
```

必須順序:

1. root/parent descriptor chainをno-follow open。
2. visible pathとheld directory fdのdevice/inode/type一致。
3. current child setをheld fdから列挙。
4. expected remaining digest（deprovisionではempty）とexact一致。
5. parent/root identityを再検証。
6. `rmdir(..., dir_fd=parent_fd)`。
7. parent/root identityとpath absenceを再検証。

recursive callを持たない。child removalは個別journal actionが先に完了する。

## Dry-run flow

```text
CLI parse
 -> specs mode normalize (None or keep)
 -> package/root/recovery admission (read-only)
 -> contract capture
 -> full WorkspaceAssessment
 -> planned DistributionProcessResult
 -> compatibility mapper
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

blockerはactions/reasonsに表示する。dry-run自体はmutation authorityを発行しないため、normal blocker inventoryはpublic `planned`/exit 0でよい。recovery metadataが存在し、safe planを新規評価しても実行できない場合はinternal `recovery_required`、public `partial_failure`/exit 1とする。malformed/unsupported eligibilityは`error`/exit 2とする。

## Apply flow

1. CLIが`--apply --keep-specs`を確認する。
2. root operation lockをacquireする。
3. admission、source capture、root bindingを再実行する。
4. full assessmentを作る。
5. blockerがあれば`blocked`を返し、guard/journal/stage/target write 0。
6. executable planとdigestを発行する。
7. recovery metadataが存在せず、mutating actionが0件なら、guard/journal/legacy marker/stageを作らずfull read-only post-assessmentを行い、preservation witnessとroot/parent identityの一致を確認して`completed`を返す。
8. existing deprovision guard/journalがあればsame-plan admissionへ進む。mutating actionがありrecovery metadataがなければguardをdurable publishする。
9. journalをprepare/bindする。
10. source/root/parent/preservation witnessをfirst mutation直前に再検証する。
11. `prune` actionsを実行しcheckpointする。
12. `remove-empty-directory` actionsを実行しcheckpointする。
13. statusを`verifying`へ進め、full post-assessmentを行う。
14. removed paths、preserved witnesses、root/parent、unknown closed setをverifyする。
15. 全actionを`verified`、journalを`completed`へ進める。
16. forward guardをexact cleanupする。
17. completed journalをexact cleanupする。
18. 追加のworkspace cleanupを行わず`completed`を返す。

## Root / parent / child identity algorithm

### Root binding

- operation開始時にdevice/inode/typeをcaptureする。
- apply中はroot lockを保持する。
-各mutation boundaryでvisible rootとheld root fdを再照合する。
- root replacement/rebindは追加mutationを停止する。

### Parent chain

各actionはrootからtarget parentまでのordered `PathIdentitySnapshot`をpreconditionに持つ。

- existing parent: directory、device、inode、typeを固定。
- deprovisionはmissing parentを作成しない。
- parent missing/replaced/symlink/specialはblockまたはrecovery required。
- journal fieldを欠落・並べ替えたself-rehashed recordをplan mismatchとして拒否する。

### Directory child digest

- held directory fdから`listdir(fd)`する。
- childを`stat(..., follow_symlinks=False)`する。
- regular contentはheld fdからhashする。
- symlinkはreadlinkする。
- child recordをcanonical sortする。
- assessmentのinitial digest、各directory actionのexpected remaining digestをplan/journalへ記録する。
- action間でexpected changeはprior verified actionだけから導出する。
- unknown child appearance、owned child disappearance、same-content inode replacement、type/mode/link topology変化はmismatch。

### Preservation tree digest

- root bindingと全descendant recordをcanonical hashする。
- regular bytesのSHA-256を含む。
- content bytes、absolute pathはjournalへ書かない。
- apply前、first mutation前、post-assessmentで再評価する。
- mutation中のconcurrent changeはoperation successを拒否し、journalを保持する。

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

### Status / exit mapping

| Internal | Public `status` | Exit |
|---|---|---|
| `planned` | `planned` | 0 |
| `completed` | `completed` | 0 |
| `blocked` | `blocked` | 1 |
| `recovery_required` | `partial_failure` | 1 |
| parser/admission error | `error` | 2 |

### Phase mapping

Existing public phase vocabularyを維持する。

| Internal phase | Public `phase` | `last_completed_phase` |
|---|---|---|
| assessment | `preflight` | `not-started`または`preflight-complete` |
| guard/journal preparation | `marker-write` | `preflight-complete`または`marker-written` |
| leaf action execution | `uninstall-apply` | `marker-written`または`uninstall-applied` |
| directory action execution | `root-cleanup` | `uninstall-applied` |
| post-assessment | `post-verify` | `uninstall-applied`または`post-verified` |
| guard/journal terminal cleanup | `marker-finalization` | `post-verified`または`marker-finalized` |
| success | `complete` | `marker-finalized` |

`marker-written`はpublic compatibility labelとして「durable recovery evidenceがpublish済み」を意味し、legacy `.uninstall-retry.json`の作成を意味しない。

### Action mapping

| Domain action / state | Public status | Summary key |
|---|---|---|
| dry-run `prune` | `would_remove` | `would_remove` |
| `prune` postcondition already absent | `already_removed` | `already_removed` |
| `prune` verified | `removed` | `removed` |
| dry-run `remove-empty-directory` | `would_remove` | `would_remove` |
| verified `remove-empty-directory` | `empty_dir_removed` | `empty_dir_removed` |
| `preserve` | `preserved` | `preserved` |
| `block` | actionは`preserved`として表示しoverall `blocked` | `preserved` |
| journal pending | `pending` | `pending` |
| action failure | `failed` | `failed` |

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

categoryはownership authorityではない。mutation可否はdomain action/preconditionが決める。

### JSON field mapping

| Field | Source / rule |
|---|---|
| `schema_version` | constant `1` |
| `target` | planned/successではexisting target string。blocked/partialではshell-safe repository-relative labelまたは`unavailable` |
| `mode` | `dry-run` / `apply` |
| `apply` | request boolean |
| `specs_mode` | default dry-run=`null`、keep=`"keep"` |
| `status` | status mapping table |
| `phase` | phase mapping table |
| `last_completed_phase` | journal/service checkpoint mapping |
| `retry_command` | safe same-target keep retry only。legacy ambiguous stateは`null` |
| `failed_paths` | sanitized repository-relative failed/blocker paths |
| `pending_paths` | journal pending action paths |
| `summary` | mapped action status counts、existing keysを常に出す |
| `actions` | `_UninstallActionView`のpath/category/status/reason/error |
| `guidance` | dry-run/apply/recovery/reinstall guidance。purgeへ誘導しない |
| `errors` | stable sanitized operation errors |

### Exactly one stdout object

`--json` routeはservice/adapterの例外を全てpayloadへ変換してから一回だけ`json.dumps(..., sort_keys=True)`する。service、journal、kernelはstdout/stderrへprintしない。

### Sanitization

blocked/partial output:

- absolute targetをrelative labelへ変換する。
- exception textをそのまま公開しない。
- action errorはstable messageへ変換する。
- file bytes、SHA、credential、source absolute path、stage nonceを公開しない。
- journal internal reasonはallowlistされたstable reasonだけを公開する。

## Failure semantics and crash windows

| Window / failure | Durable state | Required next behavior |
|---|---|---|
| assessment failure | none | write 0、error/blocked |
| blocker found | none | write 0、blocked |
| guard publish failure | noneまたはrestored predecessor | target write 0、retry可能 |
| guard published / journal absent | guard only | same-plan reconstruction後journal prepare。mismatchは停止 |
| journal publish failure | guard retained | target write 0、same-plan retry |
| action before unlink failure | journal pending | target precondition一致時だけretry |
| unlink/rmdir後 checkpoint failure | target may be post | pre/post一方だけにexact一致すればcheckpoint再構成 |
| unknown replacement afterassessment | journal retained | replacementを削除せずrecovery required |
| directory unknown child appearance | journal retained | directoryを削除せずrecovery required |
| preservation tree change | journal retained | completedにせずmanual review |
| post-assessment failure | journal verifying | same-plan retryで再評価 |
| completed publish後guard cleanup failure | completed journal+guard | target再実行なし、cleanup-only retry |
| guard cleanup後journal cleanup failure | completed journal only | target再実行なし、journal cleanup-only retry |
| terminal cleanup完了 | none | completed。以降fallible workspace mutationなし |

whole-operation rollbackは行わない。already verified removalをrecreateしない。managed assetsの再導入はoperation recoveryではなく、terminal deprovision後の別explicit `spec-dock init`/`update`である。

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
| I370-F02 | D370-ASSESS, D370-SERVICE |
| I370-F03 | D370-CONTRACT, D370-ASSESS, D370-PLAN, D370-KERNEL |
| I370-F04 | D370-DATA, D370-ASSESS, D370-SERVICE |
| I370-F05 | D370-DATA, D370-ASSESS |
| I370-F06 | D370-ASSESS, D370-PLAN, D370-SERVICE |
| I370-F07 | D370-INT, D370-CONTRACT, D370-LEGACY |
| I370-F08 | D370-SERVICE, D370-JOURNAL |
| I370-F09 | D370-PLAN, D370-KERNEL, D370-SERVICE |
| I370-F10 | D370-CLI, D370-MIG |
| I370-S01 | D370-CLI, D370-SERVICE, D370-KERNEL |
| I370-S02 | D370-DATA, D370-KERNEL |
| I370-S03 | D370-DATA, D370-KERNEL |
| I370-S04 | D370-DATA, D370-KERNEL |
| I370-S05 | D370-DATA, D370-ASSESS |
| I370-S06 | D370-CONTRACT, D370-ASSESS |
| I370-S07 | D370-CONTRACT, D370-ASSESS, D370-PLAN |
| I370-S08 | D370-PLAN, D370-KERNEL, D370-MIG |
| I370-S09 | D370-KERNEL, D370-JOURNAL |
| I370-S10 | D370-DATA, D370-PLAN, D370-JOURNAL, D370-SERVICE |
| I370-S11 | D370-CONTRACT, D370-SERVICE, D370-JOURNAL |
| I370-S12 | D370-ASSESS, D370-SERVICE |
| I370-S13 | D370-CONTRACT, D370-KERNEL |
| I370-S14 | D370-KERNEL, D370-JOURNAL |
| I370-S15 | D370-JOURNAL, D370-SERVICE |
| I370-S16 | D370-SERVICE |
| I370-C01 | D370-CLI, D370-MAP |
| I370-C02 | D370-MAP |
| I370-C03 | D370-MAP |
| I370-C04 | D370-MAP |
| I370-C05 | D370-MAP |
| I370-C06 | D370-MAP |
| I370-C07 | D370-MAP, D370-LEGACY |
| I370-C08 | D370-MIG, D370-MAP |
| I370-R01 | D370-JOURNAL, D370-SERVICE |
| I370-R02 | D370-INT, D370-JOURNAL |
| I370-R03 | D370-JOURNAL |
| I370-R04 | D370-JOURNAL |
| I370-R05 | D370-JOURNAL |
| I370-R06 | D370-JOURNAL, D370-LEGACY |
| I370-R07 | D370-LEGACY |
| I370-R08 | D370-INT, D370-CLI, D370-LEGACY |
| I370-R09 | D370-JOURNAL, D370-SERVICE |
| I370-R10 | D370-MAP, D370-LEGACY |
| I370-O01 | D370-CONTRACT, D370-ASSESS |
| I370-O02 | D370-DATA, D370-PLAN, D370-MAP |
| I370-O03 | D370-PLAT, D370-KERNEL |
| I370-O04 | D370-JOURNAL, D370-MAP, D370-PLAT |

## Risks and controls

| Risk | Control |
|---|---|
| managed root membershipからunknownを誤削除 | per-entry ownership、unknown blocker、no recursive root action |
| preserved spec historyのconcurrent mutationをsuccess扱い | pre/first-write/post preservation witness |
| journal authorityからpurgeへ昇格 | explicit `deprovision` intent/authority、remove route隔離、mismatch test |
| legacy markerをcurrent invocationへ誤帰属 | automatic conversion禁止、marker保持 |
| directory ctimeを誤ってstable bindingに使用 | directory bindingとmutation snapshotを分離 |
| action後checkpoint失敗で二重削除 | exact pre/post一意判定、missing prune idempotence |
| CLI JSON drift | field-level mapper/golden、single print boundary |
| D4 compatibilityがhidden fallbackになる | explicit entrypoint、source/AST call-edge tests、no feature flag |
| implementationがgeneric filesystem frameworkへ膨張 | required helperはexact leaf unlinkとexact empty-directory rmdirだけ |

## Material decision gates

本設計時点でProduct、Policy、Security、architectureのmaterial decisionは未決ではない。実装者は次のいずれかを発見した時点で実装を停止し、Requirement/Designの更新を要求する。

1. current common journal protocol 2 の`precondition`/`postcondition` fieldでdirectory snapshotまたはpreservation witnessをlosslessに表現できない。
2. unknown/modified childを削除しなければcurrent public keep behaviorを維持できない。
3. legacy `.uninstall-retry.json`を変換しなければnew routeを開始できない。
4. `--remove-specs` behaviorまたはauthorityを変更しなければroute splitできない。
5. public schema version、key set、exit mappingを変更しなければtyped resultをmappingできない。
6. required POSIX capabilityなしでmutationを続けるfallbackが必要になる。

これらはcoderが推測で解消してはならない。
