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

実装事実の基準は repository `chemitaro/spec-dock`、branch `iss-00370-managed-distribution-deprovision`、exact commit `fc02e1215d2b9e056a2c18bd1411fe489efdf2f2` である。

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
| requested operation | public command `uninstall`。CLI surface と output wording に使用する。 |
| effective intent | internal journal intent `deprovision`。spec history purge を含まない。 |
| deprovision authority | exact authority string `managed-distribution-deprovision`。current/historical ownership が証明された tooling/generated/managed asset と、計画に列挙された owned empty directory だけを削除できる。 |
| purge authority | Issue 371 が所有する `--remove-specs` 専用 authority。本 Issue では作成、推測、再開、昇格しない。 |
| preservation witness | mutation 対象外 tree/path の no-follow observation、content digest、type、mode、link topology、root/parent bindingを固定した read-only evidence。 |
| bounded child set | contract が列挙した managed root 内で、assessment 時に descriptor-relative に観測し、各 child を remove/preserve/block のいずれかへ完全分類した集合。 |
| forward recovery | operation 全体を元に戻すのではなく、同一 plan の exact checkpoint と pre/postconditionから安全に前進する回復。 |

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

| Observation | Ownership / authority | Deprovision action | Apply可否 | 必須postcondition |
|---|---|---|---|---|
| current regular assetがbytes、mode、type、single-link identityまでexact | current package ownership | `prune` | 可 | path absent。 |
| historical catalog assetがexact historical SHA/mode/type/single-link identity | historical ownership | `prune` | 可 | path absent。catalog indexではなくexact SHAを使用。 |
| owned assetが既にabsent | ownershipはcontractで証明、targetはmissing | `prune` with missing precondition | 可、mutationなし | path absent、public statusは`already_removed`。 |
| current bytesだがmode mismatch | removal対象としてcontent ownershipは証明できるが、exact current identityではない | `block` | 不可 | target不変、operation write 0。 |
| modified regular file | ownershipを現在状態へ拡張できない | `preserve` + `block` | 不可 | bytes/mode/path不変。 |
| unknown file/dirがmanaged boundary内に存在 | authority外 | `preserve` + `block` | 不可 | entry不変、他のsafe subsetも削除しない。 |
| exact current/historical managed symlink | link targetとno-follow identityがcontract一致 | `prune` | 可 | symlink pathname absent。targetはfollowしない。 |
| unknown/rebound symlink | authority不明 | `block` | 不可 | linkとlink targetの外部contentを変更しない。 |
| removal対象regular fileの`st_nlink != 1` | unsafe hardlink topology | `block` | 不可 | 全link不変。 |
| preservation tree内のunproven hardlink | outside aliasを一意に証明できない | `block` | 不可 | tree不変。 |
| socket/device/FIFO等special file | mutation・preservation検証不能 | `block` | 不可 | entry不変。 |
| exact root shortcut `spec -> spec-dock/scripts/spec-dock` | current managed shortcut | `prune` | 可 | shortcutだけabsent。targetはfollowしない。 |
| generated `spec-dock/active` / `.agent` entryがcurrent generated contract一致 | generated authority | `prune` | 可 | entry absent。 |
| `spec-dock/initiatives` tree | explicit keep-preservation authority | `preserve`、non-mutating witness | 可 | path、child set、regular bytes、mode、symlink text、link topologyがpreflight witnessと一致。 |
| `spec-dock/.workbench` tree | known user-owned preserved root | `preserve`、non-mutating witness | 可 | preflight witnessと一致。 |
| repository rootのcleanup boundary外sentinel | authority外・scan対象外 | actionなし | 可 | path/bytes/type不変。mutation syscallのtargetにならない。 |
| managed directory whose all children are planned absent and child set is closed | directory ownership + exact binding | `remove-empty-directory` | 可 | same bound directoryがemptyであることを再検証後、path absent。 |
| directoryにunknown childがpreflight時に存在 | child set not fully authorized | `block` | 不可 | directoryと全child不変。 |
| directoryにunknown childがassessment後に出現 | plan precondition mismatch | recovery required | 追加mutation不可 | unknown childを削除せずjournal/guard保持。 |
| valid legacy `.uninstall-retry.json` | root/intent/authority/plan/checkpoint不明 | recovery blocker | 自動変換不可 | marker bytes/identity不変、target write 0。 |

## 観測可能な要件

### Functional requirements

| ID | 要件 | 検証可能な受け入れ条件 |
|---|---|---|
| I370-F01 | default/`--keep-specs` dry-runと`--apply --keep-specs`は同じ `deprovision` assessment、contract、action grammarを使用する。 | 同一workspaceで二つのdry-runのaction path/reasonがspecs mode表示以外で一致し、applyのjournal actionsがdry-runのmutating actionsとcanonicalに一致する。 |
| I370-F02 | dry-runはcomplete read-only assessmentを返し、apply authorityを発行しない。 | filesystem snapshot、guard、journal、legacy marker、stage inventoryがbefore/afterで完全一致する。 |
| I370-F03 | deprovision removal setはcurrent/historical exact managed assets、generated state、exact shortcut、proven-owned obsolete asset、明示的owned empty directoryだけである。 | inventory fixtureの全owned pathが`prune`/`remove-empty-directory`へ分類され、authority sourceのないpathは含まれない。 |
| I370-F04 | `spec-dock/initiatives`以下をbyte-identicalに保持する。 | nested regular files、empty dirs、safe symlinkを含むtree witnessがapply前後で一致し、reinit後も同じbytesを読める。 |
| I370-F05 | known preserved Workbenchとauthority外contentを保持する。 | `.workbench` payload、cleanup boundary外sentinel、非対象rootがbefore/afterで一致する。 |
| I370-F06 | blockerが一件でもあればoperation全体をwrite 0で停止し、safe subsetを適用しない。 | removable owned assetとunknown/modified blockerのmixed fixtureで、owned assetを含むtree全体、guard、journal、stageが不変である。 |
| I370-F07 | deprovisionはspec history purge authorityを作成・推測・実行しない。 | deprovision plan/journal/guardに`remove-specs`、purge intent、purge authorityが存在せず、initiatives pathにmutating actionがない。 |
| I370-F08 | successは全mutating actionとpreservation witnessのpost-assessment成功後だけ返す。 | path absenceだけでなくspec history witness、root/parent binding、unknown closed setを再検証し、任意のmismatchでcompletedにならない。 |
| I370-F09 | already-absent owned assetはidempotentに成功し、unproven appearanceは失敗する。 | missing precondition fixtureは`already_removed`、assessment後appearance fixtureはtargetを保持してrecovery requiredとなる。 |
| I370-F10 | `--remove-specs` dry-run/applyはIssue 371 compatibility routeに明示的に隔離される。 | source/AST testでdefault/keep routeからremove-specs compatibility entrypointへのcall edgeが0、逆方向も0である。 |

### Safety requirements

| ID | 要件 | 検証可能な受け入れ条件 |
|---|---|---|
| I370-S01 | applyはroot operation lockを保持し、root device/inodeへoperation全体を束縛する。 | cooperating concurrent invocationが直列化され、root rebind injectionは最初のmutation前または次のmutation境界で停止する。 |
| I370-S02 | root、parent、target、directory childはdescriptor-relative / no-followで観測・変更する。 | parent/target symlink、visible path rebind、held descriptor mismatchで外部targetが不変のまま停止する。 |
| I370-S03 | regular removalはexact type、device、inode、ctime、mode、size、SHA-256、link countを用途に応じて検証する。 | same-content別inode、mode drift、hardlink、ctime/identity差し替えを拒否する。 |
| I370-S04 | symlink removalはexact managed link targetとno-follow identityだけをauthorityとする。 | external symlink、link target変更、symlink replacementをfollowせず保持する。 |
| I370-S05 | special fileとunsafe hardlinkはfail closedとする。 | FIFO/socket/device/multi-link fixtureでguard/journal/target write 0。 |
| I370-S06 | managed root membershipだけでchild ownershipを推測しない。 | `spec-dock/docs`等にunknown/modified childを置いたfixtureがrootごと削除されず、operation全体をblockする。 |
| I370-S07 | mutation前に全bounded child setをdeterministicに列挙し、remove/preserve/blockへ完全分類する。 | duplicate、unclassified child、unsafe name/type、enumeration errorがplan発行を拒否する。 |
| I370-S08 | directory cleanupはplanに列挙した`remove-empty-directory` actionだけで行い、汎用recursive cleanupを実行しない。 | hidden cleanup helperやpost-journal recursive scanへのcall edgeがなく、unknown empty directoryが残る。 |
| I370-S09 | each mutation直前にroot/parent/target/directory bindingとexpected remaining child setを再検証する。 | assessment後のunknown child appearance、target replacement、parent replacementで次のmutationを行わない。 |
| I370-S10 | preservation witnessはapply前にjournal planへ束縛し、post-assessmentでexact一致を要求する。 | initiatives bytes、mode、child set、symlink textのいずれかをconcurrent変更するとcompletedにならない。 |
| I370-S11 | provider contract/manifest/scaffold source identityがassessment後に変化した場合はapplyを開始・継続しない。 | source bytes/mode/identity mutation injectionでtarget write 0またはjournal保持のrecovery requiredとなる。 |
| I370-S12 | blocker planからforward guardまたはjournalを作らない。 | blocker fixtureで`.distribution-retry.json`、`.distribution-journal.json`、private stageが不存在。 |
| I370-S13 | repository外pathとcleanup boundary外sentinelはmutation syscallのtargetにしない。 | external symlink targetとoutside sentinelのidentity/bytesが全failure matrixで不変。 |
| I370-S14 | apply中の失敗後もunknown/replacement entryをcleanup authorityへ昇格しない。 | stage-like unknown、replacement inode、unknown childを保持してjournal/guardを残す。 |
| I370-S15 | mutation開始後のwhole-operation rollbackを保証・試行しない。 | partial fixtureでcompleted checkpointは戻さず、未完了actionだけsame-plan recovery対象になる。 |
| I370-S16 | recovery metadataが存在せず、全removal targetが既にabsentで、preservation witnessとroot/parent identityがvalidなno-op applyは、forward guard、journal、legacy marker、stage、target mutationを作らずread-only post-assessment後に`completed`を返す。 | all-owned paths already absent fixtureでtarget syscall 0かつ`.distribution-retry.json`、`.distribution-journal.json`、`.uninstall-retry.json`、private stageがbefore/after同一で、public resultが`completed`/exit 0となる。 |

### Compatibility requirements

| ID | 要件 | 検証可能な受け入れ条件 |
|---|---|---|
| I370-C01 | public command、flags、mutually-exclusive parser contractを変更しない。 | existing parser testsとhelp goldenが一致する。 |
| I370-C02 | public uninstall JSONは`schema_version: 1`と既存top-level field meaningを維持する。 | key set、types、nullability、summary/action field setのgolden testが一致する。 |
| I370-C03 | `--json`はstdoutへexactly one JSON objectを出し、diagnostic fragmentを前後に出さない。 | success/planned/blocked/recovery/errorの各caseを`json.loads(stdout)`一回で読め、stderr contractも既存どおりである。 |
| I370-C04 | text outputはheader、specs mode、status、phase、last completed phase、retry、failed paths、summary、actions、errors、guidanceの意味と順序を維持する。 | text goldenが既存section orderとstable labelsを固定する。 |
| I370-C05 | exit mappingはsuccess/planned=0、blocked/partial recovery=1、parser/preflight error=2を維持する。 | CLI matrix全行のexit code testが一致する。 |
| I370-C06 | blocked/partial failure diagnosticはrepository-relative pathとstable sanitized messageだけを公開する。 | token、absolute source path、file contentを注入してもJSON/textに現れない。 |
| I370-C07 | retry guidanceはsame target、`--apply --keep-specs`、shell-safe relative targetを示し、authorityを`--remove-specs`へ昇格しない。 | leading-hyphen/spaceを含むtargetのretry commandが`shlex.split`後に同じkeep invocationとなる。legacy ambiguous markerではunsafeな自動retry commandを出さない。 |
| I370-C08 | shipped README/migrationとdogfooding copyはcurrent journal、legacy marker fail-closed、keep/remove owner境界を説明する。 | packaged assetとrepository copyのcontent parity test、doc assertion、SpecDock validateが成功する。 |

### Recovery requirements

| ID | 要件 | 検証可能な受け入れ条件 |
|---|---|---|
| I370-R01 | first target mutationより前にschema-2 deprovision forward guardとprotocol-2 journalをdurable publishする。 | syscall/failure injectionでguard/journal publish失敗時のmanaged target mutationが0。 |
| I370-R02 | new guardは`operation="deprovision"`、`purpose="deprovision-journal-forward-only"`、journalは`intent="deprovision"`、`authority="managed-distribution-deprovision"`へexact bindingする。 | forged purpose/intent/authority pairをparserとresumeの双方で拒否する。 |
| I370-R03 | resumeはsame root、same intent、same exact authority、same contract、same canonical plan digest、compatible protocol、exact action pre/postconditionだけを許可する。 |各fieldの単独mismatch fixtureがwrite 0でstable reasonを返す。 |
| I370-R04 | action checkpointは`pending`→`published`→`verified`の単調遷移とし、partial failureでjournal/guardを保持する。 | publish/checkpoint/postverify/finalization各停止点からsame-plan retryが収束する。 |
| I370-R05 | guard-only、guard+journal、completed journal+guard、completed journal-onlyを区別し、説明可能なstateだけをforwardする。 | crash-window matrixがmutation重複、authority再発行、早期cleanupを起こさない。 |
| I370-R06 | journal/guard/root/plan/authority mismatch時にmarker、journal、stage、targetを推測修復しない。 | malformed/self-rehashed/dual/missing guard/unknown lease fixtureでevidenceが不変。 |
| I370-R07 | legacy `.uninstall-retry.json` は自動変換しない。 | valid marker-onlyとcopied markerはmarker bytes/identityとtarget不変でreason=`legacy-marker-unconvertible`、public `partial_failure`/exit 1。malformed/symlink/hardlink/special markerはevidence不変でreason=`legacy-marker-invalid`、public `error`/exit 2。legacy markerとnew guard/journalの併存はreason=`dual-recovery-state`、public `partial_failure`/exit 1。 |
| I370-R08 | deprovision retryからpurgeへ、purge invocationからdeprovisionへauthorityを切り替えない。 | deprovision journalに`--remove-specs`を実行、legacy purge markerに`--keep-specs`を実行するfixtureがcheckpointを進めない。 |
| I370-R09 | terminal successはpost-assessment、mark verified/completed、guard exact cleanup、journal exact cleanupの順とし、cleanup後にfallible workspace mutationを行わない。 | marker/journal removal後のrmdir/unlink injection hookが呼ばれず、cleanup failureではcompleted evidenceを保持してretry可能。 |
| I370-R10 | manual recovery guidanceはlegacy information不足、mismatch reason、same-plan retry条件を区別し、秘密情報を含まない。 | JSON/text goldenがlegacy marker、plan mismatch、postcondition mismatchを区別する。 |

### Operability and performance requirements

| ID | 要件 | 検証可能な受け入れ条件 |
|---|---|---|
| I370-O01 | assessmentはrepository全体をscanせず、contractで列挙したmanaged rootsとpreservation rootsだけを一度ずつbounded traversalする。 | observation counter testで対象外large treeのentry数に比例せず、対象bounded child数に対して線形である。 |
| I370-O02 | action order、child enumeration、canonical digest、public action orderはplatform間でdeterministicである。 |同一fixtureを順序を変えて生成してもplan digestとJSON action orderが一致する。 |
| I370-O03 | required no-follow/directory-descriptor capabilityがないplatformはfirst write前にstable diagnosticで停止する。Windows supportは追加しない。 | capability monkeypatch testでwrite 0。Linux/Darwinのexisting kernel branchesをfocused testで検証する。 |
| I370-O04 | completed/blocked/recovery stateはpublic outputとdurable journal evidenceから監査でき、remote telemetryを追加しない。 | result/journalにrelative path、reason、checkpoint、digestがあり、absolute path/content/credentialがない。 |

## Lifecycle boundary conditions

| Boundary | 必須挙動 |
|---|---|
| eligibility / preflight | target directory、managed workspace evidence、root binding、recovery-state exclusivity、package contract、platform capabilityをread-onlyに検証する。失敗はexit 2またはtyped recoveryでwrite 0。 |
| assessment | full owned/removal set、preservation witness、bounded child set、blockerを作る。legacy marker、guard、journal、stage、targetを変更しない。 |
| executable plan issuance | blockerが0で、intent/authority/contract/root/action/pre-postcondition/preservation witnessが完全な場合だけ発行する。 |
| apply preparation | root lock内でsourceとtargetを再検証する。recovery metadataがなくmutating action 0ならprotocol metadataを作らずread-only post-assessmentへ進む。mutating actionがある場合だけforward guard、journalの順にdurable publishし、ここまでtarget mutation 0。 |
| action apply | deterministic orderでexact `prune`、次にdeepest-first `remove-empty-directory`を実行し、各actionをjournal checkpointへ反映する。preserve/blockにmutation handlerを持たせない。 |
| partial failure |失敗actionと未実行actionを区別し、journal/guardを保持する。already completed actionをrollbackしない。 |
| resume | guard/journal/current treeからsame canonical planを再構成し、pre/postの一方だけにexact一致するactionを前進させる。ambiguous stateは停止する。 |
| legacy marker | validであっても自動変換せず、markerを保持してrecovery-requiredを返す。marker bytesをroot/intent/authority evidenceとして扱わない。 |
| postcondition | removed path absence、preserved tree exact witness、root/parent binding、unknown closed set、journal action coverageを再評価する。 |
| finalization | mark verified/completed後にguard、journalをexact cleanupする。finalization後にworkspace cleanupを実行しない。 |

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
- `failed_paths`
- `pending_paths`
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

internal status `recovery_required` はpublic `partial_failure`へmappingする。internal action grammarやjournal schemaをpublic JSONへ露出しない。

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

1. `I370-F01`〜`I370-O04` の各要件が、Planのstepとtest IDへtraceされる。
2. default/`--keep-specs` dry-runはread-onlyで同一deprovision assessmentを表示する。
3. `--apply --keep-specs`はnew forward guard、common journal、common kernel、post-assessmentをend-to-end使用する。
4. `spec-dock/initiatives`のbyte-preservation、unknown/modified preservation、outside sentinel不変がnegative testsで確認される。
5. mixed safe/unsafe planはguard/journal/stage/target write 0でblockする。
6. unknown child appearance、root/parent rebind、same-content replacement、unsafe hardlink、special file、symlink traversalをfail closedで拒否する。
7. partial failureのsame-plan retryが収束し、intent/authority/root/contract/plan/protocol/pre-postcondition mismatchはwrite 0で停止する。
8. legacy `.uninstall-retry.json` は自動変換されず、marker bytesとtargetを保持する。
9. public JSON schema version 1、exactly one stdout object、text section、exit mapping、sanitization、keep-only retry guidanceがgolden testsに一致する。
10. deprovision routeから `_UninstallAction` plan/apply/postverify/legacy marker writerへのcall edgeがなく、hidden fallbackがない。
11. `--remove-specs` dry-run/applyはIssue 371 compatibility routeから変更されず、deprovision journal/authorityへ接続されない。
12.実装candidate自身でfocused tests、fast tests、lint、SpecDock validate、必要なFull Regression evidenceを取得し、未実行testをsuccessとしてReportへ記録しない。

## 制約・前提

- exact implementation fact は commit `fc02e1215d2b9e056a2c18bd1411fe489efdf2f2` を基準とする。
- parent Epic `E365-R01`〜`E365-R13`、accepted unified reconciliation / forward recovery decisionを継承する。
- public compatibilityはCLI、data preservation、JSON schema semantics、text/exit behaviorに適用する。private Python symbolとlegacy marker schemaは恒久互換対象ではない。
- root operation lockは協調するSpecDock writerを直列化するadvisory authorityである。非協調same-UID processに対するdelete-by-inode相当のkernel guaranteeは約束しないが、各mutation境界で観測できたreplacement/rebind/unknown childは必ず拒否する。
- no-follow / directory descriptor / exact identity capabilityがない場合はwrite前に停止する。
-新しい依存関係、Windows、generic transaction/deletion framework、purge、Full Regression repairを追加しない。
- material decisionは本書とDesignで固定済みである。実装中に本契約では一意に決められないauthority、preservation、wire compatibility、crash-stateが見つかった場合、coderは推測実装せずPlanのdecision gateで停止する。
