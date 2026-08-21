---
種別: 設計書（Issue）
ID: "iss-00369"
タイトル: "Fresh Distribution Provisioning"
関連GitHub: ["#369"]
状態: "planned"
最終更新: "2026-08-21"
依存: ["requirement.md"]
親: ["epic-00365", "init-local-00003"]
---

# iss-00369 Fresh Distribution Provisioning — 設計

詳細: [Design Guide](../../../../../../docs/authoring/design.md)

## 設計判断

fresh provisioning を新しい別engineとして作らない。Issue 368 が実装した `WorkspaceAssessment` → `ExecutableMutationPlan` → schema-2 forward guard → `OperationJournalStore` → `apply_distribution_plan()` → post-assessment → `DistributionProcessResult` を一般化し、fresh-specific差分を次の四点に限定する。

1. admission が requested entrypoint を effective intent `fresh` へ正規化する。
2. contract に fresh-only Workbench seed と required directories を追加する。
3. journal格納先を作るため、top-level `spec-dock` に限定した pre-journal bootstrapを持つ。
4. fresh intent は destructive `upgrade` / `prune` を発行せず、schema-1 legacy markerをstate-derivedにone-way conversionする。

recognized `update` / `init-force` は既存wrapperとwire authorityを維持する。Issue 369 は Issue 368 のjournal protocolを置換せず、そのextension seamを使用する。

## Current implementation

### 既に共通化されている部分

`src/spec_dock/managed_distribution.py` は次を既に提供する。

- `_current_assets()` — `install_root` のphysical Current regular filesとcaptured source identity
- `_scaffold_assets()` — `.gitignore`、`docs`、`templates`、`scripts`、`system` とmode policy
- `_CURRENT_SHORTCUTS` — root `spec` symlink
- `build_distribution_plan()` — Current/historical contractとtarget classification
- `_observe_target()` — descriptor-relative no-follow observation
- `DistributionAction` — `create` / `adopt` / `upgrade` / `prune` / `preserve` / `block`
- `WorkspaceAssessment` と `ExecutableMutationPlan`
- canonical contract identity、plan digest、full parent/target pre/postcondition
- `OperationJournalStore`、schema-2 forward guard、journal checkpoints、stage/GC leases、created-parent bindings
- `apply_distribution_plan()` — regular/symlink create/upgrade/pruneのdescriptor-bound kernel
- `execute_recognized_distribution()` — recognized serviceと`DistributionProcessResult`

`src/spec_dock/cli.py` は次を既に提供する。

- `_exclusive_distribution_operation()` と `_bound_distribution_root()` によるroot lock/binding
- `_active_fallback_distribution_assets()` による generated `active` pointer / pathfile / context pack contract
- recognized stateのprivate snapshotとrevalidation
- public output、exit、retry command adapter

### freshに残っている旧経路

現行 fresh path は次の二つである。

- `_install_fresh_distribution_unlocked()`
- `_install_fresh_compatibility_distribution_unlocked()`

両者はCLI-owned schema-1 markerを発行し、`apply_distribution_plan()`へ`scaffold_applier`を渡す。callback内では `_install_spec_dock_bound()` が `_sync_tree()`、`_copy_managed_scaffold_tree()`、`_copy_managed_directory_contents()`、`_copy_managed_regular_file_at()`、direct `mkdir`、`_ensure_active_fallback_entrypoints()`を呼ぶ。その後、versionを `_write_spec_dock_version()` でplan外から書く。

この経路はIssue 368のrecognized serviceからは切断済みであり、Issue 369が唯一のownerとして置換する。

## Target architecture

```text
CLI requested entrypoint
  -> root directory validation
  -> exclusive root lock / bound root
  -> admit_distribution_operation()
       requested_operation + effective_intent
  -> fresh bootstrap preflight
       provider contract + external collision + workspace boundary
  -> [spec-dock absent only] exact top-level bootstrap
  -> build_workspace_assessment(intent="fresh")
  -> build_executable_mutation_plan()
  -> schema-2 forward guard
  -> OperationJournalStore
  -> apply_distribution_plan()
       ensure-directory + create + adopt
  -> build_workspace_assessment(intent="fresh") postcondition
  -> mark verified/completed
  -> remove guard, then completed journal
  -> DistributionProcessResult
  -> CLI output/exit/retry mapping
```

recognized target は従来どおり `execute_recognized_distribution()` wrapperから同じprivate execution coreへ入る。

## Admission と compatibility route

### admission result

`DistributionAdmission` に requested operation と effective intent を同時に保持する。

```python
JournaledDistributionIntent = Literal["fresh", "update", "init-force"]

@dataclass(frozen=True)
class DistributionAdmission:
    operation: DistributionOperation          # requested CLI operation
    intent: JournaledDistributionIntent | Literal["uninstall"]
    status: Literal[
        "fresh",
        "existing",
        "recognized",
        "retry",
        "uninstall-retry",
    ]
    ...
```

既存field名を変更すると広範囲のcall siteを壊すため、`operation`はrequested operationとして残し、`intent`を追加する。`RecognizedDistributionIntent = Literal["update", "init-force"]` はpublic type aliasとして維持する。

### admission matrix

| Target state | `init` | `init --force` | `update` |
|---|---|---|---|
| `spec-dock` absent | effective `fresh` | effective `fresh` | effective `fresh`（Issue 369で追加） |
| exact empty `spec-dock` | effective `fresh` | effective `fresh` | effective `fresh`（Issue 369で追加） |
| exact preserved-specs workspace | effective `fresh` | effective `fresh` | effective `fresh`（Issue 369で追加） |
| recognized workspace | `existing` + current guidance | effective `init-force` | effective `update` |
| schema-2 fresh recovery | effective `fresh`としてresume | effective `fresh`としてresume | effective `fresh`としてresume |
| recognized recovery | mismatch | matching `init-force`だけresume | matching `update`だけresume |
| unrecognized/unsafe workspace | block | block | block |

`uninstall` はfresh recoveryをresumeしない。

### CLI wrappers

- `execute_recognized_distribution()` はsignatureとbehaviorを維持する。
- `execute_fresh_distribution()` を追加する。
- journal/apply共通部は private `_execute_distribution_reconciliation()` に抽出する。
- CLIは`DistributionAdmission.intent`でwrapperを選び、requested operationはresult mappingにのみ渡す。
- `_install_fresh_distribution()` は薄いcompatibility wrapperとして一時的に新serviceへ委譲した後、call sites移行完了時に削除する。旧writerを内部fallbackとして残さない。

## Fresh Distribution Contract

### Current sourceの一意性

fresh desired set は次のsourceから構築する。

| Contract component | Source |
|---|---|
| external Current regular files | `_current_assets(install_root)` |
| managed scaffold regular files | `_scaffold_assets(scaffold_root, operation="fresh")` |
| root shortcut | `_CURRENT_SHORTCUTS["spec"]` |
| root Workbench seed | `_scaffold_assets(..., operation="fresh")` が `templates/root/.workbench/README.md` から生成 |
| active fallback | `_active_fallback_distribution_assets(specdock_snapshot)` |
| package version | `_generated_regular_asset("spec-dock/spec-dock.version", ...)` |
| required directories | `_fresh_required_directories()` |
| historical/obsolete evidence | `managed_distribution.json` |

`managed_distribution.json` にCurrent filesまたはfresh directory listを複製しない。

### required directories

新しいimmutable value objectを追加する。

```python
@dataclass(frozen=True)
class DistributionDirectoryRequirement:
    path: str
```

`DistributionPlan`に次を追加する。

```python
required_directories: tuple[DistributionDirectoryRequirement, ...] = ()
```

`_fresh_required_directories()` は実装基線から導出し、少なくとも次を含む。

- `spec-dock/initiatives`
- `spec-dock/active`
- `spec-dock/.agent`
- `spec-dock/.workbench`
- Current/scaffold/generated assetの全parent directories

`spec-dock/docs`、`templates`、`scripts`、`system` 等はasset parentとして同じ集合に入る。duplicateはcanonical POSIX pathで除去し、top-down deterministic orderにする。top-level `spec-dock` はcontract上requiredだが、journal storage bootstrapとして別処理する。

### fresh active fallback

bootstrap後のbound `spec-dock` からprivate snapshotを作り、既存 `_active_fallback_distribution_assets()` を再利用する。fresh empty stateでは次を生成する。

- `spec-dock/active/initiative`
- `spec-dock/active/epic`
- `spec-dock/active/issue`

symlinkが利用できないplatformでは対応する `.path` regular fileを生成する。

加えて次を生成する。

- `spec-dock/active/context-pack.md`

既存 preserved stateがある場合はrecognized flowと同じsafe capture / refreshable identity ruleを使用し、外部symlinkまたはunproven pointerをfresh authorityへ昇格しない。

## Assessment と action grammar

### intent typeの一般化

`WorkspaceAssessment.intent`、`ExecutableMutationPlan.intent`、`OperationJournal.intent`、`DistributionProcessResult.intent` を `JournaledDistributionIntent` へ一般化する。class名はcompatibilityのため維持する。

`build_workspace_assessment()` は `fresh` を受け付け、`build_executable_mutation_plan()` のcontract/root/action consistency checksをそのまま適用する。

### action grammar

`DistributionActionName` を次へ拡張する。

```python
Literal[
    "ensure-directory",
    "create",
    "adopt",
    "upgrade",
    "prune",
    "preserve",
    "block",
]
```

| Action | freshでの意味 | mutation |
|---|---|---|
| `ensure-directory` | required directoryがabsent | exact parentにreal directoryを作る |
| `create` | desired regular/symlinkがabsent | stage + no-replace publish |
| `adopt` | exact desired assetまたはsafe required directoryが既に存在 | なし |
| `preserve` | authority外entryを保持 | なし |
| `block` | unsafe/unproven state | なし |
| `upgrade` | freshでは発行しない | recognized owner |
| `prune` | freshでは発行しない | recognized/deprovision owner |

### directory classification

`_classify_required_directory()` を追加する。

- absent targetかつsafe parent chain → `ensure-directory`
- real directory → `adopt`
- symlink、regular、special → `block`
- missing parent → top-down directory actionsを発行
- existing required directoryのunknown children → preserve、directory自体はadopt
- operation-created directoryのunknown childがresume時に出現 → created-directory closed-set mismatchでblock

directoryは`DistributionIdentity`へ無理に押し込まず、target snapshotの`file_type="directory"`とjournal bindingで扱う。

### fresh file classification

既存 `_classify_current_target()` のfresh semanticsを維持する。

- missing → `create`
- exact regular bytes/modeまたはexact symlink target → `adopt`
- historical identity → `preserve` + block
- unknown bytes/type/target → `preserve` + block
- same bytes wrong mode → `preserve` + block
- mutation対象のhard-link topology → block

freshはhistorical fileをupgradeせず、obsolete manifest entryをscan/pruneしない。

## Plan と digest

canonical plan digestに次を含める。

- intent `fresh`
- root device/inode
- contract identity
- deterministic required-directory set
- sorted action tuple
- full root/parent/target precondition
- postcondition
- authority-compatible generated identities

directory `ensure-directory` postconditionは、wire field shapeを変えず、既存condition fieldsにdirectory markerを入れる。

```json
{
  "root": {"...": "..."},
  "parents": [{"...": "..."}],
  "exists": true,
  "device": null,
  "inode": null,
  "ctime_ns": null,
  "file_type": "directory",
  "link_count": null,
  "identity": null
}
```

null identity fieldsは「任意のdirectoryを受理する」という意味ではない。`ensure-directory` recordだけはgeneric `_snapshot_matches_condition()` ではなくdirectory-specific validatorを使い、作成後のdevice/inode/ctime/typeを`created_parent_bindings`へexact bindingとして保存し、そのbindingとの一致を必須にする。existing real directoryを`adopt`するrecordはassessment時のexact target snapshotをpre/postconditionに保持する。wire field名はbackward compatibilityのため変更しない。parser、`_assert_journal_action_contract()`、closed-set validatorは、missing parentだけでなく`ensure-directory` target自体のbindingを許可する。

action orderingは次で固定する。

1. required directories、top-down
2. scaffold/current/generated regular and symlink creates、path order
3. adopt/preserve checkpoint
4. full post-assessment
5. verified/completed transition
6. forward guard cleanup
7. journal cleanup

freshにはobsolete-prune phaseを作らない。`apply_distribution_plan()` のcurrent phase nameに依存するlegacy outputはCLI result adapter側で吸収し、journal action checkpointをphase文字列に依存させない。

## Top-level `spec-dock` bootstrap

### 必要性

schema-2 forward guardと`.distribution-journal.json`は`spec-dock`配下にあるため、absent workspaceでは最初のjournalを作る前にdirectoryが必要である。別のroot-level markerを追加するより、現行admissionが認識するexact empty boundaryを利用する方が変更が小さい。

### `FreshWorkspaceBootstrap`

`execute_fresh_distribution()` 内に `_prepare_fresh_workspace_boundary()` を設ける。

1. provider assets、manifest、runtime mode、Workbench seed sourceをread-only preflightする。
2. root-level Current assets、root `spec`、`spec-dock` boundaryをassessmentする。
3. blockerがあれば何も作成しない。
4. `spec-dock` absentの場合、held root fdからno-follow / no-replace semanticsで一度だけmkdirし、parentをfsyncする。
5. visible pathとheld fdのdevice/inode/typeを照合する。
6. full fresh assessmentを再構築する。
7. schema-2 forward guardを発行し、そのexact identityを保持する。
8. journalを発行する。
9. synchronous failure時、guard未発行かつexact created inodeが空ならrollback rmdirする。
10. guard発行後はrollbackせずforward recoveryに移る。

process crashがstep 4〜7の間に起きた場合、次回admissionはexact empty `spec-dock`をfreshとして扱う。第三者childまたはreplacementがあればempty bootstrapとして採用しない。

preserved-specs workspaceまたはexisting empty workspaceではbootstrap mkdirを行わない。

## Journal protocol

### wire compatibility

新規 fresh operationは次の既存paths/shapeを使う。

- forward guard: `spec-dock/.distribution-retry.json`
- journal: `spec-dock/.distribution-journal.json`
- journal schema/protocol field shape: current schema 1 / protocol 1
- forward guard schema: current schema 2
- guard wire purpose: `recognized-journal-forward-only`

最後のliteralは旧installerとのcompatibility tokenとして維持する。fresh semantic authorityは次で分離する。

```text
guard.operation = "fresh"
journal.intent = "fresh"
journal.authority = "fresh-distribution-provisioning"
```

recognized journalは従来どおり次を維持する。

```text
journal.intent = "update" | "init-force"
journal.authority = "recognized-workspace-reconciliation"
```

parserはintent/authorityの有効な組合せを検証し、cross-authority replayを拒否する。field shapeを増やさないためprotocol bumpは不要である。実装中に新fieldが不可避となった場合だけprotocolを上げ、protocol 1 recognized journal resumeを残す。

### journal authority

fresh journalは少なくとも次に束縛する。

- operation ID
- root identity
- exact `spec-dock` workspace identity
- intent / authority
- package version
- contract identity
- canonical plan digest
- action tuple
- full pre/postcondition
- checkpoint
- staging/GC leases
- created-directory bindings

`OperationJournalStore._initial_journal()` のrecognized hard-codeをintent別authority builderへ置き換える。

### recovery state rules

- guard-only stateは同じroot/intent/contract/planをreconstructできる場合だけjournalを発行する。
- journal+guardは独立anchorを照合する。
- completed journal+guardはtarget actionを再適用せず、postcondition確認後cleanupする。
- completed journal-onlyはIssue 368と同じterminal cleanup compatibilityを維持する。
- downgrade、contract mismatch、plan mismatch、intent mismatch、dual state、unknown leaseはfail closedとする。
- forward-compatible newer packageはjournal contractがexactに再構築できる場合だけ旧journalを完了する。physical Current contractが変わった場合は自動resumeしない。

## Legacy schema-1 fresh marker conversion

legacy markerは次のshapeを持つ。

- `schema_version=1`
- `purpose="distribution-rerun"`
- `operation="fresh"`
- package version
- target root device/inode
- `last_completed_phase`
- optional exact `stage_ownership`

new codeはこのmarkerを作らないが、existing consumer recoveryのため読む。

conversion procedure:

1. marker pathをno-followでopenし、device/inode/ctime/link count/bytes digestを保持する。
2. journalまたはschema-2 guardとのdual stateがないことを確認する。
3. root identity、operation、same package、supported phaseを確認する。
4. current packageからfresh contractを再構築する。
5. current treeをfresh rulesで再assessmentする。
6. exact desired entryは`adopt`、absent entryは`create`、unknown stateはblockとする。
7. markerのstage ownershipをpath、nonce family、device/inode/ctime/type/link count、known desired identityに照合する。
8. legacy phaseからaction checkpointを推測しない。
9. exact legacy markerをschema-2 guardへatomic swapし、contract/plan digestをanchorする。
10. journalを作り、normal fresh recoveryへ移る。

freshはcreate/adopt-onlyなので、current exact desired stateのadoptionはdestructive authorityを追加しない。recognized legacy markerのようにhistorical preconditionからupgrade/prune authorityを再構成する必要はない。same packageでcontractを再構築できない、modified scaffold、unknown child collision、invalid stage、marker replacementがある場合はconversionしない。

legacy markerにrequested entrypointはないため、operator retry guidanceは`spec-dock init`を使用する。

## Kernel changes

### `ensure-directory`

`apply_distribution_plan()` にdirectory action handlerを追加する。

- held root/parent chainを使用する。
- expected absentを再検証する。
- write-ahead missing bindingをjournalへ保存する。
- `mkdirat`相当のdescriptor-relative `os.mkdir(..., dir_fd=...)`を実行する。
- parent fdをfsyncする。
- created directoryをopenし、visible/held device/inode/typeを照合する。
- exact bindingをjournalへ昇格する。
- operation-created directoryのclosed setを、journal action、canonical target、stage lease、child directory bindingで説明できる集合に限定する。
- rollback目的でrecursive removeしない。

### regular/symlink create

既存kernelを変更せず再利用する。

- source snapshotとbytes/modeをplanに束縛
- write-ahead unique stage reservation
- partial writeのexact lease更新
- no-replace publish
- destination appearanceはpreserveしてfailure
- stage cleanupはnonce quarantine / GC lease
- no-follow root/parent/target revalidation

fresh actionは`upgrade` / `prune` handlerへ到達しないことをassertする。

### `scaffold_applier`の撤去

repository call graphで`scaffold_applier=`のproduction callerはlegacy fresh routeだけである。fresh cutover後にproduction callが0であることをtestし、次の順で削除する。

1. fresh callerからparameterを除去
2. `allow_blocked_scaffold_paths` callback exceptionを除去
3. callback phase branchを除去
4. testsで普通のaction kernelだけがscaffold filesを作ることを確認
5. 他のtest-only callerが必要ならprivate fixtureへ置換

recursive scaffold helpersはuninstallまたは別surfaceのcall graphを確認し、dead codeだけ削除する。

## Result と public mapping

`DistributionProcessResult` をfresh対応に一般化する。

```python
@dataclass(frozen=True)
class DistributionProcessResult:
    status: Literal["completed", "blocked", "recovery_required"]
    intent: JournaledDistributionIntent
    actions: tuple[DistributionAction, ...]
    plan_digest: str | None = None
    reason: str | None = None
    applied_paths: tuple[str, ...] = ()
    pending_paths: tuple[str, ...] = ()
```

CLI adapterは次を行う。

- `completed` → existing `spec-dock: ok (<requested command>) -> <absolute target>`、exit 0
- `blocked` → relative action reasonをsanitized errorとして出力、exit 1
- `recovery_required` → existing distribution partial-failure vocabulary、relative recovery target、applied/pending paths、copy-safe retry command、exit 1
- invalid target root → existing exit 2
- provider absolute path、temporary path、source bytes、credential-like textを出力しない

new fresh operationのrequested entrypointをjournalへauthorityとして保存しない。新規recovery guidanceだけCLI-local request contextから再現する。guard/journalから再開した場合、operatorが使用したcurrent requested entrypointを案内し、legacy schema-1 markerだけcanonical `init`へfallbackする。

## Removal / compatibility

Issue 369でretireするproduction fresh mutation paths:

- `_install_fresh_distribution_unlocked()`
- `_install_fresh_compatibility_distribution_unlocked()`
- fresh call from `_install_spec_dock_bound()`
- fresh `scaffold_applier`
- CLI-owned `_write_distribution_retry_marker()` / phase progression for new fresh ops
- fresh `_remove_distribution_retry_marker()` finalization path
- fresh plan外 `_write_spec_dock_version()`
- fresh direct `_ensure_active_fallback_entrypoints()` mutation

compatibility上残すもの:

- schema-1 marker parserとone-way converter
- `_distribution_retry_command()` public formatting helper
- recognized `execute_recognized_distribution()` wrapper
- recognized authority literal
- uninstall marker/protocol
- helpers thatuninstallまたはruntimeの別surfaceで使用される場合

## Test design

### ordinary focused lane

`tests/unit/infra/test_managed_distribution.py` に以下を追加する。

- fresh assessment / executable plan
- required directory grammar
- fresh authority / journal parser
- bootstrap-adjacent plan reconstruction
- schema-1 conversion
- ensure-directory crash/binding/closed-set
- stage/destination/source/root failure matrix
- terminal cleanup
- fresh intent isolation

このfileはheavy-prefix対象外のためordinary focused runで実行できる。

### public / runtime lane

`tests/unit/infra/test_init_update.py` と `tests/cli_runtime/test_distribution_cutover.py` に以下を追加する。

- fresh entrypoint matrix
- success output / exit
- second-init guidance
- fresh `update`
- unrelated preservation
- Workbench seed
- package bytes/mode/symlink parity
- legacy seam absence
- retry command quoting

両fileは`full_regression` laneであり、ordinary focused runではpolicy-skipされる。skipをpass evidenceにしない。

### provider lane

`tests/unit/test_provider_test_lanes.py` で次を維持する。

- ordinary heavy selectionはpolicy-skip
- `--run-full-regression`はrepository-wide ledger必須
- focused subset + `--run-full-regression`はmissing nodesによりexit 3
- final verifierだけがapproved baseline failuresを照合してexit 0に変換する

## リスクとtrade-off

### top-level bootstrapがjournal前である

journalをroot外へ移すより変更が小さく、現行empty-workspace admissionでcrash recoveryできる。代わりに、bootstrapだけはoperation journalに先行する。この例外を`spec-dock` exact empty inodeに限定し、他のasset mutationを許可しない。

### directory actionのprotocol拡張

`ensure-directory`はenum追加でありwire field shapeを変えない。既存`created_parent_bindings`を一般化して利用することで新しいparallel journal structureを避ける。旧packageはschema-2 guard/admissionでmutation前に停止する。

### schema-1 later-phase recovery

legacy phaseをauthorityにしない。current treeをfresh create/adopt semanticsで再評価するため、exact desired stateだけをadoptできる。unknown stateは自動cleanupせずmarkerを保持する。

### fresh `update`のbehavior change

current codeはmissing workspaceの`update`を拒否するが、Issue objectiveはfresh provisioningを要求する。success outputはexisting update formatを使い、recognized update behaviorは維持する。entrypoint matrixをgolden testで固定する。

### no prompt/backup

pre-Issue-368文書のprompt/backup前提はcurrent codeに存在しない。追加するとpublic UXとjournal boundaryを広げるため、本設計では非採用とする。

## 未確定点

- exact required-directory listは実装時にsource-derived inventory testで固定する。現行installerやpackageにないdirectoryを設計文だけで追加しない。
- platform別symlink fallbackはcurrent `_active_symlink_creation_supported()` contractを使用する。Issue 372のall-platform parityまで新platform supportを拡張しない。
- full-regression ledgerのapproved failuresをIssue 369で更新して新規failureを許可しない。baseline failure setが変化した場合は別の明示的governance判断を必要とする。
- 本設計は実行可能な変更境界を定義するが、test実行済みまたはbehavior検証済みとは主張しない。
