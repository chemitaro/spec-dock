---
種別: 要件定義書（Issue）
ID: "iss-00370"
タイトル: "Managed Distribution Deprovision"
関連GitHub: ["#370"]
状態: "planned"
最終更新: "2026-08-25"
親: ["epic-00365", "init-local-00003"]
---

# iss-00370 Managed Distribution Deprovision — 要件定義

詳細: [Requirement Guide](../../../../../../docs/authoring/requirement.md)

## 目的

`spec-dock uninstall` のうち、default dry-run、`--keep-specs` dry-run、`--apply --keep-specs` を managed distribution deprovision として、Issue 368・369 で成立した共通の read-only `WorkspaceAssessment`、blocker-free `ExecutableMutationPlan`、schema-2 forward guard、`OperationJournalStore`、descriptor-bound filesystem kernel、post-assessment、`DistributionProcessResult` へ hard cutover する。

利用者が観測できる成果は次のとおりである。

- default dry-run と `--keep-specs` dry-run は、同じ deprovision assessment を副作用なしで表示する。
- `--apply --keep-specs` は、ownership と exact filesystem identity を証明できた managed distribution asset だけを削除する。
- `spec-dock/initiatives` 以下の spec history、known preserved Workbench、authority 外 content、repository 外 content は変更されない。
- blocker が一件でもあれば、journal、guard、staging、target mutation を一件も作らず operation 全体を停止する。
- mutation 開始後の失敗は、root、intent、authority、contract、plan、checkpoint、exact pre/postcondition に束縛された同一 plan の forward recovery へ進む。
- public `uninstall` text、JSON schema version 1、exit semantics、sanitized diagnostic、retry guidance は互換 mapper から維持する。

本 Issue は spec history purge を実装しない。`--remove-specs` dry-run/apply は Issue 371 の owner であり、本 Issue の deprovision intent、authority、journal、action plan へ接続しない。

## 背景と exact implementation baseline

実装事実の基準は repository `chemitaro/spec-dock`、branch `iss-00370-managed-distribution-deprovision`、exact commit `5d25f393dba95d1a71c5582714de43c82fa094f4` である。

この exact commit では、`src/spec_dock/managed_distribution.py` に次が存在する。

- `DistributionOperation = Literal["fresh", "update", "init-force", "uninstall"]`
- `JournaledDistributionIntent = Literal["fresh", "update", "init-force"]`
- common `DistributionActionName`: `create`、`adopt`、`upgrade`、`prune`、`preserve`、`block`、`ensure-directory`
- `DistributionAction`、`DistributionPlan`、`WorkspaceAssessment`、`ExecutableMutationPlan`
- `OperationJournalAction`、`OperationJournal`、`OperationJournalStore`
- schema version 1 / protocol version 2 の `.distribution-journal.json`
- schema version 2 の forward guard と、guard purpose から journal authority への mapping
- `apply_distribution_plan()` と descriptor-relative / no-follow mutation helper 群
- `execute_fresh_distribution()`、`execute_recognized_distribution()`、`DistributionProcessResult`
- `build_distribution_plan(..., operation="uninstall")` による uninstall classification seam
- `admit_distribution_operation()` の `uninstall` admission と legacy `.uninstall-retry.json` 検出

一方、`src/spec_dock/cli.py` には deprovision 固有の第二実装が残る。

- `_UninstallTargetIdentity`
- `_UninstallAction`
- `_build_uninstall_plan()`
- `_apply_uninstall_plan()`
- `_remove_uninstall_path()` と `_remove_uninstall_tree_fd()`
- `_cleanup_empty_uninstall_dirs()`
- `_verify_uninstall_postcondition()`
- `_write_uninstall_retry_marker()` と `.uninstall-retry.json` の phase/finalization
- `_uninstall_payload()` と `_render_uninstall_text()` による public mapping

現行 `.uninstall-retry.json` の payload は次の三項目だけである。

```json
{
  "schema_version": 1,
  "managed_by": "spec-dock",
  "purpose": "uninstall-rerun"
}
```

この payload は root、specs mode、original intent、authority、contract、plan digest、operation ID、action checkpoint、staging lease を証明しない。したがって、本 Issue は欠落情報を推測して new journal へ自動変換しない。

現行 runtime tests には、managed scaffold root 内の unknown/modified entry を root ごと削除する旧固定点が含まれる。一方、親 Epic の `E365-R03` と本 Issue の安全制約は、explicit spec history purge authority の外側で unknown/modified/user-owned content を保持する。本 Issue はこの不一致を canonical safety contract 側へ解消し、旧削除期待を新しい preserve-and-block 期待へ置換する。

## Issue 368・369 から受け取る成立済み契約

本 Issue は次を新規設計し直さず、成立済み seam として拡張する。

1. read-only observation と executable authority の分離。
2. blocker を持つ `WorkspaceAssessment` から `ExecutableMutationPlan` を発行しない規則。
3. root / intent / authority / contract / canonical plan digest に束縛された schema-2 forward guard。
4. schema version 1 / protocol version 2 の `OperationJournal` と monotonic checkpoint。
5. exact precondition / expected postcondition / staging lease / created-parent binding による same-plan forward recovery。
6. descriptor-bound、no-follow、root/parent/target再検証を行う `apply_distribution_plan()` kernel。
7. `DistributionProcessResult` から CLI output/exit を生成する adapter boundary。
8. root operation lock に協調する SpecDock writer の operation-wide serialization。
9. fresh intent の action grammarが `create`、`adopt`、`preserve`、`block`、`ensure-directory` に固定されていること。
10. Issue 369 Report の Full Regression 結果は Issue 369 candidate の既実施 evidence であり、本 Issue の成功 evidence ではないこと。

## 用語と authority

| 用語 | 本 Issue での意味 |
|---|---|
| requested operation | public command `uninstall`。CLI surface、target label、output wordingに使用する。 |
| effective intent | internal journal intent `deprovision`。spec history purgeを含まない。 |
| deprovision authority | exact authority string `managed-distribution-deprovision`。current/historical ownership、current generated-state producer contract、またはexact shortcut contractのいずれかで証明されたpathと、計画済みowned empty directoryだけを削除できる。 |
| purge authority | Issue 371が所有する`--remove-specs`専用authority。本Issueでは作成、推測、再開、昇格しない。 |
| canonical generated-state producer | `build_deprovision_generated_state_contract()`。`spec-dock/active`と`spec-dock/.agent`の許可slot、kind、semantic identity、current/legacy境界を一度だけ構築する。deprovision assessmentはこのproducer以外からgenerated assetsを受け取らず、独立`generated_assets`入力はdeprovision call graphから到達不能である。 |
| current generated entry | fixed SHAのruntime producerが現在生成する予約pathであり、Designに定めるexact kind、schema/discriminator、cross-reference、single-link/mode条件を満たすentry。観測bytesまたはlink textはsemantic validation後にexact identityとして束縛する。 |
| legacy generated entry |過去に生成された可能性があるが、current producerのexact identity predicateを満たさないentry。exact historical identity catalogで別途ownershipを証明できる場合を除き、pathnameだけでは削除せず`preserve` + `block`とする。 |
| preservation witness | mutation対象外tree/pathのno-follow observation、content digest、type、mode、link topology、root/parent bindingを固定したread-only evidence。journal actionではなくplan/journalのimmutable witnessである。 |
| collapsed absence witness | proven-owned ancestorがassessment時点で既にabsentであることを、operation中に削除されないsurviving bound ancestor、そこからのmissing suffix、owned subtree semantic digestへ束縛したread-only evidence。その配下のdescendant mutation actionを発行しない。 |
| surviving absence anchor | collapsed absence witnessを再検証するためoperation完了までpathnameとdirectory objectが存続するbound real directory。nearest existing ancestorがplan内の`remove-empty-directory`対象なら、そのancestorをanchorにせず、削除closure外の最も近い上位directoryへcanonicalにre-anchorする。target rootは最終surviving anchorである。 |
| immediate child evidence | `remove-empty-directory`が参照できる唯一のdependency evidence。leaf childは対応leaf actionの`published` checkpointとexact absent、directory childは対応directory actionの`published` checkpointとそのdirectory path absentで充足する。published directory actionは配下subtreeのdescendant evidenceをdurably subsumeする。 |
| directory child semantic projection | directory namespace digestへ入れるtype-specific record。directory childではpath/name、kind、device、inode、mode、classification、owner sourceを含み、authorized child mutationで変わるdirectory `ctime_ns`と`link_count`を除外する。full descriptor snapshotは別のruntime TOCTOU guardである。 |
| semantic source projection | durable contract、plan、guard、journal equalityに使用するprovider source identity。canonical source path、asset kind、SHA-256、mode、symlink target、schema/protocol等だけを含み、device/inode/ctime/mtime等のphysical identityを含めない。 |
| invocation source snapshot | current `DistributionSourceSnapshot`相当のdevice/inode/ctime/mtime/size/modeを含むfull physical observation。一invocation内のcapture/read/apply TOCTOU guardだけに使い、durable digestまたはcompatible newer equalityへ保存しない。 |
| mutating action | journal checkpointを持つ`prune`または`remove-empty-directory`。`preserve`、`block`、preservation witness、collapsed absence witnessはjournal actionではない。 |
| bounded child set | contractが列挙したmanaged root内で、assessment時にdescriptor-relativeに観測し、各childをremove/preserve/block/collapsed-absentのいずれかへ完全分類した集合。 |
| published checkpoint | mutating actionのexpected postconditionをfilesystemでexact再観測し、journalへdurableに記録した状態。directory dependencyはprior childの`published`とexact expected-absent postconditionを要求し、`verified`を要求しない。 |
| forward recovery | operation全体を元に戻すのではなく、同一planのexact checkpoint、witness、pre/postconditionから安全に前進する回復。 |
| typed mapper input | serviceが返す`DistributionProcessResult`とそのtyped action/error records。CLI mapperはこれとstatic request contextだけを読み、journal/guardを再解釈しない。 |

## スコープ

### 対象

- default `spec-dock uninstall [path]` dry-run
- `spec-dock uninstall [path] --keep-specs` dry-run
- `spec-dock uninstall [path] --apply --keep-specs`
- `uninstall` requested operation から internal `deprovision` intent への正規化
- current/historical exact ownership に基づく managed asset removal
- generated state、root shortcut、obsolete proven-owned asset、owned empty directory cleanup
- `spec-dock/initiatives` と known preserved Workbench の preservation witness
- unknown/modified/unsafe state の pre-write blocker
- schema-2 deprovision forward guard、common journal、same-plan resume
- legacy `.uninstall-retry.json` の fail-closed admission と manual recovery guidance
- public uninstall JSON schema version 1、text、exit、sanitization、retry mapping
- deprovision route の legacy plan/apply/postverify/marker writer からの hard cutover
- shipped README / migration guidance の deprovision recovery 更新

### 対象外

- `--remove-specs` dry-run/apply の purge contract、purge authority、purge execution、purge recovery（Issue 371）
- distribution 全surface・package・platform parity の最終 gate（Issue 372）
- public command/flag/schema version の追加または変更
- `.meta.json`、Issue path、ID、title の rename
- Windows support
- generic recursive deletion framework
- operation 全体の atomic rollback
- new external dependency
- Full Regression の approved failure 修復または ledger変更
- Issue 369 の既実施 Full Regression evidence を本 Issue の success として再利用すること

## CLI behavior matrix

| Invocation | Issue owner / route | Effective intent | Mutation | Required public result |
|---|---|---|---|---|
| `uninstall` | Issue 370 deprovision dry-run | `deprovision` | 0。guard、journal、legacy marker、stagingも0 | `mode="dry-run"`、`specs_mode=null`、通常は`status="planned"`、exit 0。eligibility errorは`status="error"`、exit 2。recovery stateは`status="partial_failure"`、exit 1。 |
| `uninstall --keep-specs` | Issue 370 deprovision dry-run | `deprovision` | 0 | `mode="dry-run"`、`specs_mode="keep"`。default dry-runと同一assessment。 |
| `uninstall --remove-specs` | Issue 371 compatibility route | D4 legacy/current contract | 本Issueでは0件も追加・変更しない。dry-runはread-only | 本Issueは既存behaviorをcharacterizationし、deprovision service、guard、journalへ接続しない。 |
| `uninstall --apply` | parser後のpreflight error | なし | 0 | exactly one specs mode不足。JSON要求時はschema v1 `status="error"`、それ以外はstderr、exit 2。 |
| `uninstall --keep-specs --remove-specs` | `argparse` mutually-exclusive group | なし | handler未到達、0 | parser error、exit 2。 |
| `uninstall --apply --keep-specs` | Issue 370 journaled deprovision | `deprovision` | blocker-free executable planだけmutation可 | success=`completed`/0、pre-write blocker=`blocked`/1、partial/recovery=`partial_failure`/1、preflight error=`error`/2。 |
| `uninstall --apply --remove-specs` | Issue 371 compatibility route | D4 legacy/current contract | 本Issueのdeprovision authorityではmutation不可 | 本Issueは既存routeを変更せず、deprovision journalの作成・再開・authority昇格を禁止する。 |

`--remove-specs` compatibility route が存在することは、deprovision route の fallback を意味しない。dispatch は specs mode により一度だけ確定し、default/keep route から remove-specs route、または remove-specs routeから deprovision serviceへ移る分岐を持たない。

## Ownership / preservation / action authority matrix

### Managed distribution と preservation

| Observation | Ownership / authority | Deprovision disposition | Apply可否 | 必須postcondition |
|---|---|---|---|---|
| current regular assetがbytes、mode、type、single-link identityまでexact | current package ownership | `prune` | 可 | path absent。 |
| historical catalog assetがexact historical SHA/mode/type/single-link identity | historical ownership | `prune` | 可 | path absent。catalog indexではなくexact SHAを使用。 |
| exact current/historical managed symlink | link targetとno-follow identityがcontract一致 | `prune` | 可 | symlink pathname absent。targetはfollowしない。 |
| exact root shortcut `spec -> spec-dock/scripts/spec-dock` | current managed shortcut | `prune` | 可 | shortcutだけabsent。targetはfollowしない。 |
| current bytesだがmode mismatch | current identity全体は不一致 | `preserve` + `block` | 不可 | target不変、operation write 0。 |
| modified regular file、unknown file/dir | current/historical/generated authorityなし | `preserve` + `block` | 不可 | entry不変、safe subsetも適用しない。 |
| removal対象regular fileの`st_nlink != 1` | unsafe hardlink topology | `block` | 不可 | 全link不変。 |
| unknown/rebound symlink、socket/device/FIFO | authorityまたは安全なidentityなし | `block` | 不可 | entryと外部target不変。 |
| `spec-dock/initiatives` tree | explicit keep-preservation authority | preservation witness | 可 | path、child set、regular bytes、mode、symlink text、link topologyがpreflight witnessと一致。 |
| `spec-dock/.workbench` tree | known user-owned preserved root | preservation witness | 可 | preflight witnessと一致。 |
| repository rootのcleanup boundary外sentinel | authority外・scan対象外 | disposition/actionなし | 可 | mutation syscallのtargetにならず、identity/bytes/type不変。 |
| managed directory whose removable children are all`published` and exact absent、preserved childが0、child setがclosed | directory ownership + exact binding | `remove-empty-directory` | 可 | same bound directoryがemptyであることを再検証後、path absent。 |
| directoryにunknown/preserved childが存在 | directory removalのclosed setを満たさない | `preserve` + `block`、directory actionなし | 不可 | directoryと全child不変。 |
| directoryにunknown childがassessment後に出現 | plan/witness mismatch | recovery required | 追加mutation不可 | unknown childを削除せずjournal/guard保持。 |
| valid legacy `.uninstall-retry.json` | root/intent/authority/plan/checkpoint不明 | recovery blocker | 自動変換不可 | marker bytes/identity不変、target write 0。 |

### Current generated-state authority

`build_deprovision_generated_state_contract()`だけが次のcurrent slotをgenerated authorityへ変換する。各present entryはDesignのexact predicateを満たし、観測したbytes/link textを含むno-follow identityへ束縛されなければならない。

| Root | Current removable slot | Required kind / identity boundary | Conflict / legacy handling |
|---|---|---|---|
| `spec-dock/active` | layerごとの`initiative` / `epic` / `issue` symlink、または対応する`*.path` regular fallbackのexactly one | symlinkはsingle-linkでnormalized relative targetを持ち、valid active selectionまたは`spec-dock/system/active-none/<layer>`へrepository内解決する。path fileはsingle-link regular、UTF-8一行のnormalized relative targetで同じ解決先を指す。 | 同一layerでsymlinkと`.path`が併存、absolute/out-of-root target、wrong kind/content、unknown siblingは`block`。 |
| `spec-dock/active` | `context-pack.md` | single-link regular、validated active selectionからcurrent rendererが生成するexact bytes。 | `current-runbook.json`、`current-runbook.md`はfixed SHAのcurrent producerが出力しないlegacy slotであり、historical exact identityがなければ`preserve` + `block`。 |
| `spec-dock/.agent` | `active.json` | single-link regular、exact top-level field `schema_version` / `updated_at` / `initiative` / `epic` / `issue`、schema `2`。`updated_at`はtimezone offset付きsecond-precision ISO-8601。各layerは`null`またはexact `id` / `path` objectで、canonical layer IDと`spec-dock/initiatives`配下のnormalized repository-relative existing node pathを指し、initiative→epic→issue hierarchyが成立する。semantic validation後のobserved SHAをpreconditionにする。 | malformed、extra field、invalid timestamp/id/path/hierarchy、wrong kind/hardlinkは`block`。 |
| `spec-dock/.agent` | `index-all.json` | single-link regular、schema `2`、projection `full-history`、current index renderer contractを満たすJSON。 | schema/projection/shape不一致は`block`。 |
| `spec-dock/.agent` | `tree-all.json` | single-link regular、schema `2`、exact full-tree renderer field set（`generated_at`、`active`、`warnings`、`root`、`deps`、`tree`）を満たし、unsupported `projection`を持たないJSON。 | field/shape不一致は`block`。 |
| `spec-dock/.agent` | `index.json` | single-link regular、schema `2`、projection `current-future`、current index renderer contractを満たすJSON。 | schema/projection/shape不一致は`block`。 |
| `spec-dock/.agent` | `tree.json` | single-link regular、schema `2`、exact todo-tree renderer field set（`generated_at`、`active`、`warnings`、`root`、`deps`、`tree`）を満たし、unsupported `projection`を持たないJSON。 | field/shape不一致は`block`。 |
| `spec-dock/.agent` | `deps-issues.json` | single-link regular、schema `2`、projection `issue-readiness-with-dependency-context`。valid resultとdocumented fail-closed placeholderの双方をcurrent predicateとして扱う。 | unknown schema/projection/shapeは`block`。 |
| `spec-dock/.agent` | `deps.json`、`deps.puml`、`deps.todo.puml` | current producerではなくlegacy v1 name | exact historical identity catalogが一致する場合だけhistorical `prune`。name/typeだけではauthorityを得ず、それ以外は`preserve` + `block`。 |
| `spec-dock/.agent` / `spec-dock/active` | 上記以外のchild | authorityなし | unknown contentとして`preserve` + `block`。root全体をrecursive deleteしない。 |

Current generated entryがmissingであること自体はblockerではない。present entry同士が同一logical slotを競合する場合、active manifest・pointer/path fallback・context pack・index/tree `active` fieldが同じselectionを表さない場合、同一sync batchのpresent artifactsで`generated_at`またはindex/tree node集合が矛盾する場合、またはcurrent/legacy identityが曖昧な場合は、operation全体をwrite 0でblockする。runtime writerはdynamic generated filesへcanonical chmodを強制しないため、生成ownershipのsemantic predicateに固定mode値を置かない。ただしassessmentで観測したexact modeはpreconditionへ含め、assessment後のmode変更はidentity mismatchとして拒否する。

### Proven-owned ancestor absence

| Observation | Classification | Action emission | Witness / postcondition |
|---|---|---|---|
| contract-owned ancestorが存在し、descendant leafだけmissing | surviving anchor selectionを実行してleaf-level absenceを分類 | public diagnosticは`already_removed`、mutating action 0 | 最も近いexisting parentが削除closure外ならそのbinding、削除対象なら上位surviving ancestorへre-anchorし、anchorからmissing leafまでをcollapsed absence witnessへ束縛する。 |
| contract-owned ancestorそのものがassessment時点でabsent | そのancestor配下のcontract-owned descendantsを一つのcollapsed absenceへ集約 | ancestor、descendant、directoryのmutating actionを発行しない | deletion closure外のnearest surviving bound ancestor、そのanchorからのmissing suffix、owned subtree semantic digestを`DistributionCollapsedAbsenceWitness`へ記録する。 |
| nearest existing ancestorが同じplanで削除対象 |そのdirectoryはwitness anchorとして不適格 | descendant actionは増やさない | parentへ一段ずつ上がり、mutating actionもcollapsed subtreeも含まない最初のsurviving real directoryへcanonical re-anchorする。target rootまで到達した場合はrootをanchorにする。 |
| missing componentがcontract-owned ancestorより上位、またはsurviving ancestorをsafeに束縛できない | unproven namespace gap | actionなし、operation blocker | write 0。 |
| collapsed ancestorがassessment後またはresume前にappearance | witness mismatch | appearanceしたentryを削除するactionを新規発行しない | mutation開始前ならblocked、journal開始後ならrecovery required。 |
|全managed subtreeがcollapsed absentで、preservation witnessがvalid | completed no-op | mutating action 0 | guard、journal、legacy marker、stage、target syscall 0。 |
## 観測可能な要件

### Functional requirements

| ID | 要件 | 検証可能な受け入れ条件 |
|---|---|---|
| I370-F01 | default/`--keep-specs` dry-runと`--apply --keep-specs`は同じ`deprovision` assessment、contract、action grammarを使用する。 |同一workspaceで二つのdry-runのdiagnostic path/reasonがspecs mode表示以外で一致し、applyのjournal actionsがdry-runのmutating actionsとcanonicalに一致する。 |
| I370-F02 | dry-runはcomplete read-only assessmentを返し、apply authorityを発行しない。 | filesystem snapshot、guard、journal、legacy marker、stage inventoryがbefore/afterで完全一致する。 |
| I370-F03 | deprovision removal setはcurrent/historical exact managed assets、単一canonical producerが証明したcurrent generated entries、exact shortcut、proven-owned obsolete asset、明示的owned empty directoryだけである。 | `I370-T-OWN-001`がcurrent generated slotのpositive/negative/legacy/conflict matrixを固定し、deprovision assessmentへgenerated stateを二系統で渡せないことをtype/signature/source testで確認する。 |
| I370-F04 | `spec-dock/initiatives`以下をbyte-identicalに保持する。 | nested regular files、empty dirs、safe symlinkを含むtree witnessがapply前後で一致し、reinit後も同じbytesを読める。 |
| I370-F05 | known preserved Workbenchとauthority外contentを保持する。 | `.workbench` payload、cleanup boundary外sentinel、非対象rootがbefore/afterで一致する。 |
| I370-F06 | blockerが一件でもあればoperation全体をwrite 0で停止し、safe subsetを適用しない。 | removable owned assetとunknown/modified blockerのmixed fixtureで、owned assetを含むtree全体、guard、journal、stageが不変である。 |
| I370-F07 | deprovisionはspec history purge authorityを作成・推測・実行しない。 | deprovision plan/journal/guardに`remove-specs`、purge intent、purge authorityが存在せず、initiatives pathにmutating actionがない。 |
| I370-F08 | successは全mutating actionとpreservation/collapsed-absence witnessのpost-assessment成功後だけ返す。 | removed path absenceだけでなくspec history witness、absence witness、root/parent binding、unknown closed setを再検証し、任意のmismatchでcompletedにならない。 |
| I370-F09 | proven-owned ancestorが既にabsentなら、その配下のowned descendantsをcanonicalにcollapseし、mutating actionを発行しない。witness anchorはoperation中に削除されないnearest surviving bound ancestorとし、nearest existing ancestorが削除対象なら上位surviving ancestorへcanonical re-anchorする。assessment後のappearanceは新規削除authorityを得ない。 | 3階層以上のnested treeでanchor re-selection、descendant action 0、appearance時のblocked/recovery-required、entire managed subtree absentのprotocol metadata write 0を`I370-T-NOOP-001`で確認する。 |
| I370-F10 | `--remove-specs` dry-run/applyはIssue 371 compatibility routeに明示的に隔離される。 | source/AST testでdefault/keep routeからremove-specs compatibility entrypointへのcall edgeが0、逆方向も0である。 |

### Safety requirements

| ID | 要件 | 検証可能な受け入れ条件 |
|---|---|---|
| I370-S01 | applyはroot operation lockを保持し、root device/inodeへoperation全体を束縛する。 | cooperating concurrent invocationが直列化され、root rebind injectionは最初のmutation前または次のmutation境界で停止する。 |
| I370-S02 | root、parent、target、directory childはdescriptor-relative / no-followで観測・変更する。 | parent/target symlink、visible path rebind、held descriptor mismatchで外部targetが不変のまま停止する。 |
| I370-S03 | regular removalはexact type、device、inode、ctime、mode、size、SHA-256、link countを用途に応じて検証する。 | same-content別inode、mode drift、hardlink、ctime/identity差し替えを拒否する。 |
| I370-S04 | symlink removalはexact managed link target、no-follow identity、`link_count == 1`だけをauthorityとする。 | external symlink、link target変更、multi-link symlink、symlink replacementをfollowせず保持する。 |
| I370-S05 | special fileとunsafe hardlinkはfail closedとする。 | FIFO/socket/device/multi-link fixtureでguard/journal/target write 0。 |
| I370-S06 | managed root membership、generated root membership、予約filenameだけでchild ownershipを推測しない。 | `spec-dock/docs`、`spec-dock/active`、`spec-dock/.agent`のunknown/modified/legacy-unproven childがrootごと削除されずoperation全体をblockする。 |
| I370-S07 | mutation前に全bounded child setをdeterministicに列挙し、remove/preserve/block/collapsed-absentへ完全分類する。 | duplicate、unclassified child、unsafe name/type、enumeration errorがplan発行を拒否する。 |
| I370-S08 | directory cleanupはplanに列挙した`remove-empty-directory`だけで行い、dependencyを全descendantではなくimmediate child evidenceへ限定する。leaf childは対応leaf actionの`published` + exact absent、directory childは対応directory actionの`published` + directory path absentで充足する。published directory actionは配下subtree evidenceをdurably subsumeし、ancestor action、verifying、crash resumeはremoved subtree内pathを再openしない。`verified`をdependencyに使わない。 | `I370-T-DIR-001`と`I370-T-REC-001`が3階層以上のnested tree、各directory publish直後crash、ancestor resume、verifyingを同じimmediate-child/subsumption規則で固定し、removed subtree内のdescendant open/list/stat callが0である。汎用recursive cleanupへのcall edgeは0。 |
| I370-S09 | each mutation直前にroot/parent/target/directory binding、immediate child checkpoint、expected remaining namespaceを再検証する。directory child digestはtype-specific semantic projectionを使い、directory childからauthorized mutationで変わる`ctime_ns`と`link_count`を除外する。visible pathとheld descriptorのfull device/inode/type/mode/ctime/link comparisonは別のruntime TOCTOU guardとして維持し、digestへ暗黙rebindしない。 | `I370-T-DIR-001`がleaf removalによるparent ctime/link count変化でもsame-plan実行・resumeが収束することを確認する。directory inode/type/mode replacement、unknown child appearance、unexplained namespace changeは次のmutation前にfail closedとなる。 |
| I370-S10 | preservation witnessとcollapsed absence witnessはjournal actionではなくplan/journal immutable metadataとして束縛し、post-assessmentでexact一致を要求する。 | witnessにcheckpointがなく、initiatives bytes/mode/child set/symlink textまたはabsence appearanceを変更するとcompletedにならない。 |
| I370-S11 | full physical `DistributionSourceSnapshot`は各invocation内のcapture/read/apply TOCTOU guardだけに使う。durable contract identity、plan digest、forward guard、journal equalityはcanonical source path、asset kind、SHA-256、mode、symlink target、schema/protocol等のsemantic source projectionだけへ束縛し、device/inode/ctime/mtimeを含めない。compatible newer packageは自身のfull snapshotを再captureし、stored semantic projectionとexact一致した場合だけresumeする。 | `I370-T-SRC-001`が別physical install rootでsemantic source同一のsame-plan resumeを確認する。source path/kind/bytes/mode/link target/schema driftはwrite 0でblockし、same invocation中のsource replacementはfull snapshot mismatchでtarget mutation前または次boundaryに停止する。 |
| I370-S12 | blocker planからforward guardまたはjournalを作らない。 | blocker fixtureで`.distribution-retry.json`、`.distribution-journal.json`、private stageが不存在。 |
| I370-S13 | repository外pathとcleanup boundary外sentinelはmutation syscallのtargetにしない。 | external symlink targetとoutside sentinelのidentity/bytesが全failure matrixで不変。 |
| I370-S14 | apply中の失敗後もunknown/replacement/appeared entryをcleanup authorityへ昇格しない。 | stage-like unknown、replacement inode、unknown child、collapsed ancestor appearanceを保持してjournal/guardを残す。 |
| I370-S15 | mutation開始後のwhole-operation rollbackを保証・試行しない。 | partial fixtureでpublished checkpointは戻さず、未完了actionだけsame-plan recovery対象になる。 |
| I370-S16 | recovery metadataが存在せず、全removal targetが既にabsentまたはcollapsed absenceで説明され、preservation witnessとroot/nearest-existing-parent identityがvalidなno-op applyは、protocol metadataとtarget mutationを作らずread-only post-assessment後に`completed`を返す。 | all-owned paths/subtrees already absent fixtureでtarget syscall 0かつguard、journal、legacy marker、private stageがbefore/after同一。public resultは`completed`/exit 0で、typed phase ruleもgoldenに一致する。 |

### Compatibility requirements

| ID | 要件 | 検証可能な受け入れ条件 |
|---|---|---|
| I370-C01 | public command、flags、mutually-exclusive parser contractを変更しない。 | existing parser testsとhelp goldenが一致する。 |
| I370-C02 | public uninstall JSONは`schema_version: 1`、既存top-level/action/summary field meaningを維持する。 | key set、types、nullability、summary/action field setのgolden testが一致する。 |
| I370-C03 | `--json`はstdoutへexactly one JSON objectを出し、diagnostic fragmentを前後に出さない。 | success/planned/blocked/recovery/errorの各caseを`json.loads(stdout)`一回で読め、stderr contractも既存どおりである。 |
| I370-C04 | text outputはheader、specs mode、status、phase、last completed phase、retry、failed paths、summary、actions、errors、guidanceの意味と順序を維持する。 | text goldenが既存section orderとstable labelsを固定する。 |
| I370-C05 | exit mappingはsuccess/planned=0、blocked/partial recovery=1、parser/preflight error=2を維持する。 | CLI matrix全行のexit code testが一致する。 |
| I370-C06 | public `target`は現行schema-v1規則を維持する。`blocked`/`partial_failure`だけはshell-safeなrelative target labelまたは`unavailable`へsanitizationし、`planned`/`completed`/`error`は既存どおりresolved target文字列を返す。action/top-level errorとdiagnostic pathはstatusにかかわらずallowlisted stable messageとrepository-relative pathへ限定し、provider source path、file content、credentialを公開しない。 | status別target goldenとtoken/source/content injection testが一致し、`blocked`/`partial_failure`にabsolute targetが出ず、preflight `error`を含む全error messageにsecret/raw exceptionが出ない。 |
| I370-C07 | normal deprovision resultのretry policyは`same-keep-command`とし、static specs modeが`keep`であるplanned/completed/blocked/recovery/errorでは現行どおりsame targetの`--apply --keep-specs` shell-safe commandを返す。default dry-runのspecs mode `null`とlegacy ambiguous/invalid markerの`manual-recovery`は`retry_command: null`とし、authorityを`--remove-specs`へ昇格しない。 | default dry-run、keep dry-run、keep success、blocked、partial recovery、preflight error、legacy markerをgolden化する。leading-hyphen/spaceを含むtargetのnon-null commandは`shlex.split`後に同じkeep invocationとなり、legacy markerではmanual guidanceだけを返す。 |
| I370-C08 | shipped README/migrationとdogfooding copyはcurrent journal、legacy marker fail-closed、generated identity boundary、keep/remove owner境界を説明する。 | packaged assetとrepository copyのcontent parity test、doc assertion、SpecDock validateが成功する。 |
| I370-C09 | CLI mapperはstatic request contextとone typed `DistributionProcessResult`だけから`status`、`phase`、`last_completed_phase`、`failed_paths`、`pending_paths`、per-action `error`、top-level `errors`、retry policyを決定する。CLIがjournal/guard/storeを読んで補完してはならない。 | `I370-T-RESULT-001`が全durable state fixtureをtyped resultへ変換し、mapperのjournal accessを禁止するsource/monkeypatch testとJSON/text goldenを通す。 |

### Recovery requirements

| ID | 要件 | 検証可能な受け入れ条件 |
|---|---|---|
| I370-R01 | first target mutationより前にschema-2 deprovision forward guardとprotocol-2 journalをdurable publishする。 | syscall/failure injectionでguard/journal publish失敗時のmanaged target mutationが0。 |
| I370-R02 | new guardは`operation="deprovision"`、`purpose="deprovision-journal-forward-only"`、journalは`intent="deprovision"`、`authority="managed-distribution-deprovision"`へexact bindingする。 | forged purpose/intent/authority pairをparserとresumeの双方で拒否する。 |
| I370-R03 | resumeはsame root、same intent、same exact authority、same durable contract、same canonical plan digest、compatible protocol、exact action pre/postcondition、exact witnesses、exact semantic source projectionだけを許可する。physical provider inode/device/ctime/mtimeの一致はcross-invocation条件にせず、各invocationが新しくcaptureしたfull source snapshotをそのinvocation中のTOCTOU guardとして使う。 | `I370-T-SRC-001`と`I370-T-REC-001`でsemantic-equalな別physical install rootからのcompatible newer resumeが成功し、各field/witness/semantic sourceの単独mismatchとsame-invocation source replacementがwrite 0または次boundary停止になることを確認する。 |
| I370-R04 | deprovision journal state machineはreachableな一表へ固定する。`prepared`は全action`pending`、`executing`は`pending\|published`だけ、全mutating action`published`後に`verifying`、`verifying`は全action`published`のみ、full post-assessment成功後の一回のatomic publicationで全action`verified`かつ`completed`とする。directory actionのimmutable immediate-child evidenceはleaf/directory kindをlosslessに持ち、published directory actionはそのsubtreeをsubsumedとする。このvalidatorは`intent="deprovision"`へ限定する。 | `I370-T-DIR-001`、`I370-T-JRN-001`、`I370-T-REC-001`がstatus/checkpoint/dependency kind/subsumptionの不正組合せを拒否し、3階層nested leaf publish、各directory publish、executing-all-published、verifying、completedの各crash windowからdescendant再openなしでsame-plan retryが収束することを確認する。existing fresh/recognized fixtureは変更なしで通る。 |
| I370-R05 | guard-only、guard+journal、各nested directory `published`直後、completed journal+guard、completed journal-onlyを区別し、説明可能なstateだけをforwardする。published directoryのsubtree evidenceはjournalから再構成し、removed subtree内descendantを再観測してauthorityを再取得しない。 | 3階層crash-window matrixがmutation重複、removed descendant reopen、authority再発行、早期cleanupを起こさない。 |
| I370-R06 | journal/guard/root/plan/authority/witness mismatch時にmarker、journal、stage、targetを推測修復しない。 | malformed/self-rehashed/dual/missing guard/unknown lease/witness mismatch fixtureでevidenceが不変。 |
| I370-R07 | legacy `.uninstall-retry.json` は自動変換しない。 | valid marker-onlyとcopied markerはmarker bytes/identityとtarget不変でreason=`legacy-marker-unconvertible`、public `partial_failure`/exit 1。malformed/symlink/hardlink/special markerはevidence不変でreason=`legacy-marker-invalid`、public `error`/exit 2。legacy markerとnew guard/journalの併存はreason=`dual-recovery-state`、public `partial_failure`/exit 1。 |
| I370-R08 | deprovision retryからpurgeへ、purge invocationからdeprovisionへauthorityを切り替えない。 | deprovision journalに`--remove-specs`を実行、legacy purge markerに`--keep-specs`を実行するfixtureがcheckpointを進めない。 |
| I370-R09 | terminal successは全mutating action`published`、`verifying`、witnessを含むfull post-assessment、全action`verified`、journal`completed`、guard exact cleanup、journal exact cleanupの順とする。verifyingはpublished directory actionをsubtree absenceのdurable summaryとして扱い、removed subtree内descendant pathを再openしない。cleanup後にfallible workspace mutationを行わない。 | 3階層directory actionがimmediate child evidenceから順次実行され、各publish直後crashから収束する。verifyingでdescendant filesystem accessが0、preservation witnessはpost-assessmentで検証され、cleanup failureではcompleted evidenceを保持する。 |
| I370-R10 | serviceは各return pathでtyped phase、last-completed、failed/pending/action error/top-level error/retry policyを確定し、manual recovery guidanceはlegacy information不足、mismatch reason、same-plan retry条件を区別する。 | durable state population tableの全行が`I370-T-RESULT-001`とJSON/text goldenへ一対一対応し、秘密情報を含まない。 |

### Operability and performance requirements

| ID | 要件 | 検証可能な受け入れ条件 |
|---|---|---|
| I370-O01 | assessmentはrepository全体をscanせず、contractで列挙したmanaged rootsとpreservation rootsだけを一度ずつbounded traversalする。 | observation counter testで対象外large treeのentry数に比例せず、対象bounded child数に対して線形である。 |
| I370-O02 | action order、child enumeration、type-specific directory semantic projection、immediate child evidence、subsumption、semantic source projection、surviving-anchor selection、canonical digest、public action orderはplatform/physical install root間でdeterministicである。 | `I370-T-DIR-001`、`I370-T-SRC-001`、`I370-T-OPS-001`で同一fixtureを作成順だけ変えた場合とsemantic-equal sourceを別physical rootへ配置した場合にcontract/plan digest、collapsed witness、JSON action orderが一致する。directory ctime/link-countだけの変化ではdigest不変、inode/type/modeまたはsemantic source driftでは不一致となる。 |
| I370-O03 | required no-follow/directory-descriptor capabilityがないplatformはfirst write前にstable diagnosticで停止する。Windows supportは追加しない。 | capability monkeypatch testでwrite 0。Linux/Darwinのexisting kernel branchesをfocused testで検証する。 |
| I370-O04 | completed/blocked/recovery/error stateはtyped resultとdurable journal evidenceから監査でき、remote telemetryを追加しない。 | result/journalにrelative path、reason、phase、checkpoint、digestがあり、absolute path/content/credentialがない。 |

## Lifecycle boundary conditions

| Boundary | 必須挙動 |
|---|---|
| eligibility / preflight | target directory、managed workspace evidence、root binding、recovery-state exclusivity、package contract、platform capabilityをread-onlyに検証する。失敗はtyped `error`または`recovery_required`でwrite 0。 |
| generated contract | `build_deprovision_generated_state_contract()`をexactly once呼び、current slot、semantic identity、legacy/unrecognized entry、conflictを分類する。deprovision assessmentへ独立`generated_assets`引数を渡す経路は存在しない。 |
| assessment | full owned/removal set、preservation witness、collapsed absence witness、bounded child set、blockerを作る。legacy marker、guard、journal、stage、targetを変更しない。 |
| executable plan issuance | blockerが0で、intent/authority/contract/root/mutating action/pre-postcondition/witnessが完全な場合だけ発行する。`preserve`/`block`/witnessをjournal actionへ変換しない。 |
| apply preparation | root lock内でprovider sourceを再captureし、stored semantic source projectionとの一致を確認する。full physical snapshotはこのinvocationのTOCTOU guardとして保持する。recovery metadataがなくmutating action 0ならprotocol metadataを作らずread-only post-assessmentへ進む。mutating actionがある場合だけforward guard、journalの順にdurable publishし、ここまでtarget mutation 0。 |
| leaf apply (`executing`) | `prune`をdeterministic orderで実行し、exact postconditionを再観測して`published`へ進める。`verified` checkpointは許可しない。 |
| directory apply (`executing`) | 各`remove-empty-directory`はimmediate child evidenceだけを読む。leaf childはleaf action`published` + exact absent、directory childはdirectory action`published` + child directory path absentを要求する。published directory childは配下subtreeをsubsumedとし、descendantを再openしない。current directory semantic child digestがexpected empty projectionと一致した場合だけrmdirし、absence確認後にdirectory actionを`published`へ進める。 |
| verifying | 全mutating actionが`published`であることを確認してstatusを`verifying`へ進める。no pending action、no new target mutation。published directory actionをsubtree absence summaryとして用い、removed subtree内descendantを再openせず、top-level mutating postcondition、preservation witness、surviving-anchor absence witness、root/remaining parent binding、unknown closed setを検証する。成功後の一回のatomic publicationで全actionを`verified`かつjournalを`completed`へ進める。 |
| completed | 全journal actionが`verified`である場合だけjournal statusを`completed`にする。target actionを再実行しない。 |
| partial failure | failureをtyped action/top-level errorへ変換し、journal/guardを保持する。published actionをrollbackしない。 |
| resume | existing journalがある場合はjournal plan/action、immediate child evidence、subsumption、semantic source projectionがcanonicalであることを要求し、新規assessmentのcollapseでaction setを置換しない。pending actionはexact precondition、published leafはexact absent、published directoryはdirectory path absentを要求する。published directory配下のdescendantを再openしない。compatible newer packageは自身のfull source snapshotをcaptureし、stored semantic projection一致時だけ進む。 |
| compatible newer source admission | stored durable semantic source projectionをcurrent packageのcanonical producerから再構成する。exact一致ならcurrent invocationのfull physical snapshotを新規captureして進み、semantic driftまたはsame-invocation physical replacementではwrite 0/recovery required。physical install rootのdevice/inode/ctime/mtime差だけでは拒否しない。 |
| collapsed absence | recovery metadataなしのfresh assessmentでだけtop-down collapseを作る。anchor候補が削除closure内なら上位へre-anchorし、operation中に存続するsurviving bound ancestorからmissing suffixを再検証する。appearanceは新規actionへ変換せずblocked/recovery required。 |
| legacy marker | validであっても自動変換せず、markerを保持してrecovery-requiredを返す。marker bytesをroot/intent/authority evidenceとして扱わない。 |
| finalization | completed journalのpostconditionを再確認し、guard、journalをexact cleanupする。finalization後にworkspace cleanupを実行しない。 |
| presentation | serviceはreturn前にtyped resultを完成させる。CLIはresultとrequest contextだけからJSON/text/exitを生成し、journal pathをopenしない。 |

## Legacy marker conversion decision

本 Issue の canonical decision は **automatic conversionを禁止する** である。

理由は、current marker payloadが同一bytesのまま次の相互に異なる状態を表し得るためである。

-異なるrepository rootで開始されたoperation
- `--keep-specs` または `--remove-specs`
- marker write直後、任意のfile removal後、post-verify前、marker finalization失敗後
-異なるpackage contract、異なるaction order、異なるpartial checkpoint
- marker fileが別rootからcopyされたstate

同一入力bytesからroot、intent、authority、plan、checkpointを一意に復元できないため、変換は非単射である。欠落fieldをcurrent invocationやcurrent treeから補うと、deprovisionからpurgeへのauthority誤昇格、already-mutated pathの再削除、unknown replacementのcleanup authority取得が起こり得る。

将来の自動変換を許可するには、少なくとも marker 自身または独立したdurable evidenceから exact root identity、original specs mode、intent、authority、contract identity、canonical plan digest、operation ID、action checkpoint、stage/GC leaseを一意に証明し、同一bytesが複数stateに対応しないことをnegative counterexample testで示す必要がある。current schemaはこの条件を満たさない。

## Public JSON compatibility contract

schema version 1 のtop-level fieldは次を維持する。

- `schema_version`
- `target`
- `mode`
- `apply`
- `specs_mode`
- `status`
- `phase`
- `last_completed_phase`
- `retry_command`
- `failed_paths`（action-specific failure、blocker/witness diagnostic、および全`pending_paths`のcanonical union。pending pathは両fieldへ現れる）
- `pending_paths`（checkpoint `pending`のmutating action pathだけ）
- `summary`
- `actions`
- `guidance`
- `errors`

各action fieldは次を維持する。

- `path`
- `category`
- `status`
- `reason`
- `error`

summary key setは次のexisting keyをexactに維持する。

- `would_remove`
- `removed`
- `already_removed`
- `preserved`
- `failed`
- `pending`
- `empty_dir_removed`

internal status `recovery_required` はpublic `partial_failure`へmappingする。internal `error`はpublic `error`へmappingする。internal action grammar、witness schema、journal schemaをpublic JSONへ露出しない。

### Typed mapper input completeness

`DistributionProcessResult`または同等のone typed mapper inputは、少なくとも次を保持する。

- internal `status`
- public-compatible `phase`
- `last_completed_phase`
- ordered typed action outcomes（path、category、status、reason、sanitized error）
- `failed_paths`（action-specific failure、blocker/witness diagnostic、および全`pending_paths`のcanonical union。pending pathは両fieldへ現れる）
- `pending_paths`（checkpoint `pending`のmutating action pathだけ）
- ordered top-level sanitized errors
- retry policy（same keep retry / manual recovery / none）
- `plan_digest`とstable reason

service/journal adapterはdurable stateをこのtyped inputへ変換してからCLIへ返す。CLIはjournal status/checkpoint、guard purpose、legacy marker bytesを直接読まず、static request context（target label、apply、specs mode、JSON選択）だけを追加してschema-v1 payloadとtextを生成する。

### Durable stateからtyped fieldへの最低規則

| Durable/service state | `phase` | `last_completed_phase` | failed / pending / errors |
|---|---|---|---|
| eligibility開始前error | `preflight` | `not-started` | operation errorのみ。 |
| planned dry-run（blocker diagnosticを含む） | `preflight` | `preflight-complete` | ordered action outcomeへ`preserved` reasonを含めるが、`failed_paths`、`pending_paths`、top-level errorsは空。dry-runはoverall `planned`/exit 0。 |
| blocked apply | `preflight` | `preflight-complete` | blocker pathを`failed_paths`、action outcomeを`preserved`とし、現行failure semanticsどおりallowlisted top-level operation errorを一件以上返す。overall `blocked`/exit 1。 |
| valid legacy marker-only | `preflight` | `not-started` | top-level `legacy-marker-unconvertible` operation error、retry policy=`manual-recovery`、target action pendingなし。 |
| guard-only | `marker-write` | `marker-written` | journal planから全mutating pathsを`pending_paths`へ入れ、同じpathsとjournal pathを`failed_paths`に含め、allowlisted recovery errorを返す。 |
| journal `prepared` | `uninstall-apply` | `marker-written` | checkpoint `pending` pathsを`pending_paths`と`failed_paths`の双方へ入れ、allowlisted recovery errorを返す。 |
| journal `executing`、leaf未完了 | `uninstall-apply` | `marker-written` | action failure pathとcheckpoint `pending` pathを`failed_paths`へ、checkpoint `pending`を`pending_paths`へ入れ、allowlisted recovery errorを返す。 |
| leaf全て`published`、directory未完了 | `root-cleanup` | `uninstall-applied` | pending directory pathsを`pending_paths`と`failed_paths`の双方へ入れ、allowlisted recovery errorを返す。 |
| journal `executing`、全mutating action `published` | `post-verify` | `uninstall-applied` | final action checkpoint後・status transition前のcrash window。target pendingなし、allowlisted recovery errorを返し、target action再実行0でpost-assessmentだけを再開する。 |
| journal `verifying` | `post-verify` | `uninstall-applied` | target mutation pendingなし。witness/postcondition pathを`failed_paths`、対応するallowlisted recovery errorをtop-level errorsへ。 |
| journal `completed` + guard | `marker-finalization` | `post-verified` | target pendingなし。guard pathを`failed_paths`、guard cleanup errorをtop-level errorsへ。 |
| completed journal-only | `marker-finalization` | `marker-finalized` | target pendingなし。journal pathを`failed_paths`、journal cleanup errorをtop-level errorsへ。 |
| mutating success | `complete` | `marker-finalized` | failed/pending/errors空。 |
| protocol-metadata-free no-op success | `complete` | `post-verified` | failed/pending/errors空。`marker-finalized`と偽装しない。 |

全行に共通して、normal deprovision resultは`retry_policy="same-keep-command"`を保持する。CLI mapperはstatic specs modeが`keep`のときだけcurrent-compatible retry commandを生成し、default dry-runの`specs_mode=null`では`null`とする。legacy markerの`manual-recovery`と明示的`none`では`null`とする。

詳細なfield-level mappingとaction error populationはDesignを正本とする。

## Issue boundary and handoff

### Issue 369から受け取るもの

- shared assessment/plan/journal/kernel/result seam
- fresh-specific action allowlistとguard authority
- provider/source/root/parent/target identity validation
- deterministic plan digest、checkpoint、post-assessment
- Issue 369 candidateで実行されたtest evidence（本Issue candidateの成功証拠にはしない）

### Issue 371へ渡すもの

- `deprovision` intentと`managed-distribution-deprovision` authority
- spec history preservation witnessとpurge非許可contract
- deprovision journalが存在する場合に`--remove-specs`がcheckpointを進めないadmission rule
-明示的に隔離された`--remove-specs` compatibility routeと、そのcurrent behavior characterization
- purge actionを追加してもdeprovision plan digest/authorityを再利用できないtype/validation boundary

### Issue 372へ渡すもの

- default/keep routeがnew serviceへhard cutover済みであるabsence evidence
-残存するD4-owned compatibility seamの一覧
- public JSON/text/exit golden
- Linux/Darwin focused evidence
- package/dogfood parityの最終確認対象

Issue 372 は、本 Issue で削除すべきdeprovision legacy call edgeを後からcleanupするownerではない。default/keep routeにlegacy plan/apply/marker fallbackが残る場合、本 Issueは未完了である。

## 受け入れ条件

1. `I370-F01`〜`I370-O04`の49要件が、Design element、Plan step、stable test IDへtraceされる。
2. default/`--keep-specs` dry-runはread-onlyで同一deprovision assessmentを表示する。
3. `--apply --keep-specs`はnew forward guard、common journal、common kernel、post-assessmentをend-to-end使用する。
4. generated stateはsingle canonical producerからのみcontract化され、active/.agentのcurrent positive、legacy、unknown、conflict matrixが`I370-T-OWN-001`で固定される。
5. `spec-dock/initiatives`のbyte-preservation、unknown/modified preservation、outside sentinel不変がnegative testsで確認される。
6. mixed safe/unsafe planはguard/journal/stage/target write 0でblockする。
7. `remove-empty-directory`はimmediate child evidenceだけから到達でき、leaf `published` + absent、directory `published` + path absent、published directoryによるsubtree subsumption、executing/verifying/completedのparser・digest・crash windowが一つのstate tableへ一致する。3階層以上のnested cleanupで各directory publish直後からresumeでき、removed subtree内descendantを再openしない。
8. proven-owned ancestor absenceはdescendant actionなしのcollapsed witnessとなり、anchor候補が削除対象なら上位surviving ancestorへcanonical re-anchorする。entire managed subtree absent applyはprotocol metadata/target syscall 0でcompletedになり、assessment後appearanceは削除されない。
9. directory child semantic projectionはdirectory `ctime_ns`/`link_count`を除外し、authorized child removal後のparent ctime変化を正常に受理する一方、directory inode/type/mode replacement、unknown child appearance、root/parent rebind、same-content replacement、unsafe hardlink、special file、symlink traversalをfail closedで拒否する。
10. partial failureのsame-plan retryが収束する。別physical install rootのcompatible newer packageはsemantic source projectionがexact一致する場合だけresumeでき、bytes/mode/link target/canonical source path/schema driftはwrite 0で停止する。同一invocation中のsource replacementはfull snapshot guardで拒否する。intent/authority/root/contract/plan/protocol/pre-postcondition/witness mismatchもwrite 0で停止する。
11. legacy `.uninstall-retry.json`は自動変換されず、marker bytesとtargetを保持する。
12. public JSON schema version 1、exactly one stdout object、text section、exit mapping、status別target contract、keep-only retry guidanceがgolden testsに一致する。
13. `DistributionProcessResult`または同等のtyped inputだけでphase、last completed、failed/pending paths、action errors、top-level errors、retry policyを生成でき、pending pathが`failed_paths`と`pending_paths`の双方へ現れるcurrent contractと、planned/completed/blocked/recovery/errorのretry nullabilityを`I370-T-RESULT-001`で証明し、CLIにjournal interpretationがない。
14. deprovision routeから`_UninstallAction` plan/apply/postverify/legacy marker writerへのcall edgeがなく、hidden fallbackがない。
15. `--remove-specs` dry-run/applyはIssue 371 compatibility routeから変更されず、deprovision journal/authorityへ接続されない。
16.実装candidate自身でfocused tests、fast tests、lint、SpecDock validate、必要なFull Regression evidenceを取得し、未実行testをsuccessとしてReportへ記録しない。

## 制約・前提

- exact implementation factと現行canonical文書の基準はcommit `5d25f393dba95d1a71c5582714de43c82fa094f4` とする。
- parent Epic `E365-R01`〜`E365-R14`、accepted unified reconciliation / forward recovery decisionを継承する。
- public compatibilityはCLI、data preservation、JSON schema semantics、text/exit behaviorに適用する。private Python symbolとlegacy marker schemaは恒久互換対象ではない。
- current generated-state path/schema contractはfixed SHAの`active_store.py`、`artifact_writer.py`、`json_state.py`、`reference_sync.md`から導出する。pathnameだけでlegacy ownershipを推測しない。
- provider sourceのdurable equalityはsemantic source projectionを正本とし、`DistributionSourceSnapshot`のphysical fieldsは一invocation内TOCTOU guardに限定する。compatible newer recoveryをphysical install-root identityへ束縛しない。
- root operation lockは協調するSpecDock writerを直列化するadvisory authorityである。非協調same-UID processに対するdelete-by-inode相当のkernel guaranteeは約束しないが、各mutation境界で観測できたreplacement/rebind/unknown childは必ず拒否する。
- current legacy `.uninstall-retry.json`に存在しないroot、intent、authority、plan、checkpointをfixtureまたはmigrationで捏造しない。
- `--remove-specs` purge、Issue 372 parity/closure、Windows、generic recursive deletion、new dependency、Full Regression repairは本Issueへ追加しない。
- production code、commit、push、PR、Issue stateは本仕様改訂作業では変更しない。
