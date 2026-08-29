---
種別: 要件定義書（Issue）
ID: "iss-00371"
タイトル: "Explicit Spec History Purge"
関連GitHub: ["#371"]
状態: "planned"
最終更新: "2026-08-28"
親: ["epic-00365", "init-local-00003"]
---

# iss-00371 Explicit Spec History Purge — 要件定義

詳細: [Requirement Guide](../../../../../../docs/authoring/requirement.md)

## 1. 目的

`spec-dock uninstall --remove-specs` dry-run と `spec-dock uninstall --apply --remove-specs` apply を、Issue 370 までに成立した共通の `WorkspaceAssessment`、`ExecutableMutationPlan`、`OperationJournalStore`、descriptor-bound filesystem kernel、post-assessment、`DistributionProcessResult` へ hard cutover する。

spec history の削除は、既存 public CLI の `--remove-specs` で選択された exact purge intent と、同じ invocation における `--apply` の二要素が揃った場合だけ mutation authority を持つ。default uninstall、`--keep-specs`、`init`、`init --force`、`update`、deprovision retry、legacy marker、journal recovery は、purge authority へ暗黙昇格してはならない。

本 Issue の完了状態では、`--remove-specs` の旧 CLI-owned recursive writer と `.uninstall-retry.json` writer は production executable path から物理削除され、remove-specs を実行する writer は Issue 370 の共通 journaled kernel だけとなる。

## 2. 監査基準と source of truth

本要件は、次の exact verified revision に固定する。

| 項目 | 値 |
|---|---|
| repository | `chemitaro/spec-dock` |
| branch | `iss-00371-explicit-spec-history-purge` |
| full commit SHA | `94546a138bd34b253c87ca8749f3c5678d172f2a` |
| current package version | `0.2.3` |
| public entry point | `spec-dock = "spec_dock.cli:main"` |

判断優先順位は、上記 SHA の production code、tests、public CLI behavior、README、Issue 370 canonical docs/report、Issue 371 文書の順とする。既存 Issue 371 文書に記載されていた独立 `ManagedHistoryPurgeAuthority`、`ManagedMutationPlan`、別 purge journal、別 recursive kernel は current code に存在しないため、本要件の前提にしない。

current implementation で成立済みの seam は次である。

- `src/spec_dock/managed_distribution.py`
  - `DistributionAction`
  - `DistributionPlan`
  - `WorkspaceAssessment`
  - `ExecutableMutationPlan`
  - `OperationJournalAction`
  - `OperationJournal`
  - `OperationJournalStore`
  - `DistributionProcessResult`
  - `build_deprovision_contract()`
  - `build_deprovision_generated_state_contract()`
  - `build_deprovision_workspace_assessment()`
  - `execute_deprovision_distribution()`
  - `_remove_distribution_target_if_bound()`
  - `_remove_distribution_directory_if_bound()`
- `src/spec_dock/cli.py`
  - default/keep route: `_run_uninstall_deprovision()` → `execute_deprovision_distribution()`
  - remove route: `_run_uninstall_remove_specs_compatibility()` → legacy `_build_uninstall_plan()` / `_apply_uninstall_plan()` / `.uninstall-retry.json` writer
  - public typed mapper: `_uninstall_payload_from_result()`
  - public text/exit mapper: `_render_uninstall_text()` / `_uninstall_exit_code_from_result()`

## 3. 用語と固定 authority

| 用語 | 定義 |
|---|---|
| purge planning intent | `uninstall --remove-specs` が選択する read-only `purge` intent。dry-run は plan を作るが mutation authority、guard、journal、stage、target write を作らない。 |
| purge mutation authority | 同一 invocation に `--apply` と `--remove-specs` が揃い、pre-write assessment が blocker-free である場合だけ成立する authority。exact internal authority string は `explicit-spec-history-purge`。 |
| history root | exact repository-relative path `spec-dock/initiatives`。別 root、prefix pattern、glob、caller-provided root は認めない。 |
| deprovision component | Issue 370 の `managed-distribution-deprovision` authority で削除可能な owned tooling、generated state、shortcut、exact historical managed asset、owned empty directory。purge operation はこの component と history root removal を一つの operation として実行する。 |
| authority 外 content | history root 外で、deprovision component の current/historical/generated ownership を証明できない content。pathname proximity、親 directory、旧 marker、retry state から ownership を推測しない。 |
| pre-write blocker | guard、journal、legacy marker、stage、target を一件も作成・更新する前に検出できる不安全または不整合。blocker が一件でもあれば safe subset を実行しない。 |
| same-plan forward recovery | exact root、intent、authority、contract identity、plan digest、journal protocol、package compatibility、action pre/postcondition が一致する current invocation だけが pending checkpoint を前進させる回復。deleted history の rollback ではない。 |

## 4. Current behavior の維持境界

### 4.1 Public command surface

次の command/flag grammar を維持する。

```text
spec-dock uninstall [--apply] [--keep-specs | --remove-specs] [--json] [path]
```

- `uninstall` は dry-run が既定である。
- apply には exactly one of `--keep-specs` / `--remove-specs` を要求する。
- new command、new flag、interactive confirmation、plan token、public authority token を追加しない。
- `--json` は stdout に schema version 1 の JSON object を exactly one 件出力する。

### 4.2 Public remove-specs presentation

current remove-specs presentation の次の意味を維持する。

- spec history の public action category は `spec_history`。
- public action path は `spec-dock/initiatives`。
- present history の dry-run reason は explicit remove-specs intent を示す。
- apply 成功は `removed`、既に absent の apply は `already_removed` として表現できる。
- internal journal は leaf/directory 単位で checkpoint を持ってよいが、public action list は spec history subtree を root action 一件へ集約し、internal staging path や journal detail を公開しない。
- exact internal failed/pending relative paths は既存 top-level `failed_paths` / `pending_paths` で表現する。
- schema version、field names、one-object contract、status/exit mapping を変更しない。

### 4.3 Dry-run と apply の関係

dry-run は advisory plan であり、後続 apply へ権限または cached plan を渡さない。public schema/flag を増やさないため、apply は lock 取得後の current filesystem を再 assessment し、その時点の exact plan から journal authority を作る。dry-run 後に filesystem が変化した場合、apply plan が変化または blocker になることは正常であり、過去 dry-run を根拠に mutation を継続してはならない。

## 5. 観測可能な要件

### 5.1 Intent、authority、route

| ID | 要件 |
|---|---|
| I371-R01 | `uninstall --remove-specs` は read-only `purge` assessment を実行する。`uninstall --apply --remove-specs` だけが purge mutation authority を作る。 |
| I371-R02 | `--apply` 単独、default dry-run、`--keep-specs`、`init`、`init --force`、`update` は purge intent または purge authority を作らない。 |
| I371-R03 | purge の exact internal intent は `purge`、authority は `explicit-spec-history-purge` とし、deprovision の `deprovision` / `managed-distribution-deprovision` と一致させない。 |
| I371-R04 | CLI は authority string、journal field、checkpoint を組み立てたり解釈したりしない。remove-specs adapter は fixed purge service を呼び、service が intent と authority を内部で固定する。 |
| I371-R05 | remove-specs dry-run/apply は同じ read-only contract builder、assessment、action grammar、common mutation kernel、journal store、typed result を使用する。dry-run だけの別 plan builderを持たない。 |
| I371-R06 | `_run_uninstall_remove_specs_compatibility()` とその legacy writer/mutator call graph は、new service cutover と同じ change で production から削除する。runtime toggle、fallback、dual writer を残さない。 |

### 5.2 Purge scope と ownership

| ID | 要件 |
|---|---|
| I371-R07 | purge history authority は exact path `spec-dock/initiatives` とその実在する descendant directory/regular file に限定する。別 path、prefix collision、absolute path、`..`、repository root 外 path を action にしない。 |
| I371-R08 | history root 内の directory と single-link regular file は、filename、extension、content bytes、既知 schema への一致に依存せず explicit purge authority の対象とする。spec history は user が `--remove-specs` で明示した destructive data である。 |
| I371-R09 | history root 自体または descendant に symlink、hard-linked regular file、special file、unreadable entry、unstable/rebound identity が一件でもある場合、purge operation 全体を pre-write block する。symlink target、hardlink peer、special endpoint を変更しない。 |
| I371-R10 | history root 外の unknown/modified/user-owned content は purge authority を得ない。`spec-dock/.workbench` は preservation witness として保持し、repository root の authority 外 sentinel は scan/action対象にしない。 |
| I371-R11 | purge operation は Issue 370 の deprovision component も同時に実行する。managed tooling/generated assets は既存 deprovision ownership rules だけで削除し、unknown managed-boundary content は既存どおり preserve-and-block とする。 |
| I371-R12 | `spec-dock` やその ancestor directory は、planned child actions の expected-absent postconditionがすべて published され、exact empty で、unknown sibling が存在しない場合だけ `remove-empty-directory` できる。recursive parent deletionで history root 外 contentを巻き込まない。 |

### 5.3 Read-only assessment と write boundary

| ID | 要件 |
|---|---|
| I371-R13 | dry-run は target tree、mode、mtime/ctime、link topology、guard、journal、legacy marker、stage inventory を変更しない。lock file や一時 artifact を target に残さない。 |
| I371-R14 | apply は complete purge + deprovision assessment を終え、全 blocker を統合してから guard/journal prepare に進む。pre-write blocker が一件でもあれば operation-wide write count は 0。 |
| I371-R15 | blocker-free plan の mutating actions だけを `ExecutableMutationPlan` と `OperationJournalAction` に変換する。`preserve`、`block`、preservation witness、absence witness を checkpoint action にしない。 |
| I371-R16 | history root が既に absent の場合、その absence を exact surviving ancestor に束縛する。apply 中または recovery 前に history root/descendant が出現しても新しい purge authority を自動発行しない。 |
| I371-R17 | purge operation 全体が no-op で、all preserved/absence witness が再検証できる場合、guard、journal、stage、target write を作らず `completed` を返す。 |

### 5.4 Filesystem safety

| ID | 要件 |
|---|---|
| I371-R18 | root、各 parent、leaf、directory binding は no-follow observation と held descriptor で assessment 時に捕捉し、各 mutation 直前と postcondition 検証時に再検証する。 |
| I371-R19 | regular file deletion は exact device/inode/type/mode/ctime/link-count/size/SHA-256 precondition と `link_count == 1` を要求する。どれかが変化した場合は unlink しない。 |
| I371-R20 | directory deletion は exact root/parent/directory identity continuity、immediate child evidence、child checkpoint、expected remaining child digest、actual empty namespace を要求し、`_remove_distribution_directory_if_bound()` と同じ guard を使用する。authorized child mutationで必然的に変わるdirectory/parentの`ctime`と`link_count`はinitial semantic digestの不一致にせず、各時点のvisible pathとheld descriptorのfull identity一致、device/inode/type/mode continuity、expected namespace transitionで検証する。 |
| I371-R21 | visible path と held descriptor の rebind、parent replacement、root replacement、child appearance、content rewrite、mode drift、link-count drift を mutation 前に検出した場合、それ以降の target mutation を停止し journal/guard を回復 evidence として保持する。 |
| I371-R22 | purge syscall は repository-relative planned path の held parent descriptor に対してのみ実行する。symlinkをfollowせず、repository外 path をopen/remove対象にしない。 |

### 5.5 Journal、recovery、legacy state

| ID | 要件 |
|---|---|
| I371-R23 | purge は既存 `.distribution-journal.json` schema version 1 / protocol version 2 と `.distribution-retry.json` schema version 2 forward guard を使用する。new journal file、new marker file、new public schema を追加しない。 |
| I371-R24 | purge guard/journal は `intent=purge`、authority=`explicit-spec-history-purge`、root identity、contract identity、canonical plan digest、operation ID、action pre/postcondition、checkpoint、staging lease を保持する。 |
| I371-R25 | same root、same purge intent、same authority、same contract、same plan、supported protocol、compatible package、明示的な current `--apply --remove-specs` invocation が揃う場合だけ forward recovery を許可する。 |
| I371-R26 | deprovision journalをremove-specsで、purge journalをdefault/keep/update/initで、または別root/別plan/別authorityで再開しない。mismatch 時は checkpoint進行0、target write0。 |
| I371-R27 | valid `.uninstall-retry.json` は original root、specs mode、intent、authority、plan、checkpoint を証明しないため、purge guard/journalへ変換しない。current `--apply --remove-specs` が指定されても marker をauthority証拠として補完せず、marker/targetを変更せず manual recovery result を返す。 |
| I371-R28 | malformed、symlink、hardlink、special `.uninstall-retry.json` は invalid recovery evidence として write前に error とする。legacy marker と new guard/journal が併存する dual state は双方を進めない。 |
| I371-R29 | mutation開始後の失敗は whole-operation rollback を試みず、exact journal/guard が安全に残る場合は `recovery_required` とする。deleted history bytes の自動復元は提供しない。 |
| I371-R30 | success 後は全 mutating action の postcondition、history root absence、deprovision postcondition、`.workbench` preservation witness、authority外 sentinel を再検証してから guard/journalをfinalizeする。 |

### 5.6 Typed result と public compatibility

| ID | 要件 |
|---|---|
| I371-R31 | purge service は既存 `DistributionProcessResult` を返す。別 result class、CLI-owned filesystem outcome、journal parser を追加しない。 |
| I371-R32 | `DistributionProcessResult.intent` は `purge` を表現し、CLI mapper は `(deprovision, None|keep)` と `(purge, remove)` の組合せだけを受理する。cross pair は internal contract violation として拒否する。 |
| I371-R33 | public status mappingは `planned→planned/0`、`completed→completed/0`、`blocked→blocked/1`、`recovery_required→partial_failure/1`、`error→error/2` を維持する。 |
| I371-R34 | purge の automatic retry guidance は `spec-dock uninstall --apply --remove-specs <target>` の同一 explicit command だけを示す。legacy ambiguity、dual state、authority mismatch は automatic retry commandを出さず manual recovery guidance とする。 |
| I371-R35 | public JSON/text は absolute internal stage path、journal bytes、device/inode、contract digest、plan digest、provider source、file contentを公開しない。failed/pending pathはsanitized repository-relative pathだけとする。 |

### 5.7 Regression と documentation

| ID | 要件 |
|---|---|
| I371-R36 | `tests/unit/infra/test_managed_distribution.py` は purge contract/assessment/kernel/journal/recovery、pre-write write0、identity attack、preservationを検証する。 |
| I371-R37 | `tests/unit/infra/test_init_update.py` は public route matrix、JSON/text/exit/retry、legacy marker、non-escalationを検証する。 |
| I371-R38 | `tests/cli_runtime/test_distribution_cutover.py` は old purge writer/mutatorのproduction call edgeが0で、CLIがtyped resultだけをmappingすることをAST/source seamで固定する。 |
| I371-R39 | READMEはremove-specs compatibility routeという記述を除去し、shared journaled explicit purge、dry-run write0、two-part authority、legacy marker manual recovery、same-remove forward recoveryを記載する。 |
| I371-R40 | approved Full Regression failure ledger、verifier semantics、test expectationを変更してcandidateを通してはならない。candidate attributable failureを修正できない場合はIssueを未完了として停止する。 |

## 6. Scope

### 6.1 対象

- `uninstall --remove-specs` dry-run の read-only purge assessment
- `uninstall --apply --remove-specs` の journaled purge apply
- internal `purge` intent と `explicit-spec-history-purge` authority
- exact `spec-dock/initiatives` subtree の bounded recursive deletion
- Issue 370 deprovision component との一操作内 composition
- common `WorkspaceAssessment` / `ExecutableMutationPlan` / journal / kernel / typed resultへのcutover
- same-plan forward recoveryとcross-intent/authority rejection
- legacy `.uninstall-retry.json` ambiguityのfail-closed treatment
- current public JSON schema version 1、text、exit、root-level `spec_history` presentation
- old purge route、old recursive mutator、old marker writerの物理削除
- READMEとcanonical Issue文書の同期

### 6.2 対象外

- new public command、flag、confirmation prompt、plan token、JSON schema field
- update/init/deprovisionによるhistory cleanup
- `.uninstall-retry.json` の自動migration、mode推測、marker削除
- deleted spec history のbackup、restore、undelete、whole-operation rollback
- generic arbitrary subtree delete API、caller-supplied allowed roots、glob/prefix authority
- secure erase、forensic erase、storage-level overwrite
- Windows support
- Issue 370 common kernel/journal/resultの再設計
- Full Regression approved failureの修復、waiver追加、ledger rebaseline
- package version bump、release、deploy

## 7. Failure boundary

| 状態 | service result | public status / exit | write | recovery意味 |
|---|---|---|---|---|
| dry-run assessment success | `planned` | `planned` / 0 | 0 | applyは再assessmentする。dry-run planを再利用しない。 |
| apply no-op、witness stable | `completed` | `completed` / 0 | 0 | recovery stateなし。 |
| pre-write ownership/safety blocker | `blocked` | `blocked` / 1 | 0 | unsafe pathを修正後、明示commandで再assessment。 |
| target/preflight eligibility error | `error` | `error` / 2 | 0 | input/environment修正後に再実行。 |
| valid legacy marker ambiguity | `recovery_required` | `partial_failure` / 1 | 0 | current-compatible legacy completionまたはhuman-verified recovery。purge変換なし。 |
| invalid legacy marker | `error` | `error` / 2 | 0 | markerを自動修復・削除しない。 |
| new guard/journal mismatch | `recovery_required` | `partial_failure` / 1 | 0 | matching intent/authority/planを証明できない限り停止。 |
| first target mutation後のsafe failure | `recovery_required` | `partial_failure` / 1 | journal済みの一部write | same explicit remove command + same-plan compatible packageだけforward recovery。 |
| success | `completed` | `completed` / 0 | planned mutations + protocol finalization | history root absent、preserved witnesses unchanged。 |

pre-write write 0 は、target dataだけでなく `.distribution-retry.json`、`.distribution-journal.json`、`.uninstall-retry.json`、stage/quarantine、directory creation、mode/metadata changeを0とする。

## 8. Acceptance criteria

### 8.1 Route / authority

1. `uninstall --remove-specs` が `execute_explicit_spec_history_purge_distribution()` の dry-runを一回だけ呼び、legacy plan/writerを呼ばない。
2. `uninstall --apply --remove-specs` が同serviceをlock-bound root identity付きで一回だけ呼ぶ。
3. default/keepの6 public rowsは引き続き `execute_deprovision_distribution()` を使用し、purge serviceを呼ばない。
4. update/init/default/keep/legacy marker/retry mismatchからhistory mutating actionが0件である。

### 8.2 Scope / deletion

5. normal history treeでは、single-link regular filesとdirectoriesがdeepest-first checkpointで削除され、`spec-dock/initiatives` がabsentとなる。
6. history root内のunknown filename/bytes/depthはexplicit purge対象となり、catalog一致を要求しない。
7. root symlink、child symlink、hardlink、FIFO/socket/device、unreadable entry、root/parent/child rebindの各fixtureでoperation-wide write0またはmutation開始後の安全停止となり、external target/peerは不変である。
8. `spec-dock/.workbench`、history root外unknown sibling、repository root outside sentinelがbefore/afterで一致する。
9. unknown managed-boundary contentとのmixed fixtureではsafe history subsetも適用せず、全write0でblockする。

### 8.3 Journal / recovery

10. purge guard/journalがexact `purge` intent、`explicit-spec-history-purge` authority、root、contract、plan、protocolへ束縛される。
11. interruption fixtureがsame explicit remove commandとsame-plan evidenceでforward recoveryし、completed checkpointを逆行させず収束する。
12. deprovision→purge、purge→deprovision、purge→update/init、別root、別plan、history appearance/rewriteでcheckpoint進行0となる。
13. valid/copy済み/malformed/symlink/hardlink/special legacy markerとdual-state fixtureでmarker/guard/journal/targetの不正な更新が0件である。

### 8.4 Public compatibility / cutover

14. JSONはschema version 1、one object、既存field set、既存status/exit mappingを維持する。
15. present historyはpublic `path="spec-dock/initiatives"`、`category="spec_history"` のroot-level outcome一件へ集約される。internal leaf/checkpointはpublic actionとして展開しない。
16. purge retry可能時だけ `--apply --remove-specs` retry commandを返し、legacy/mismatch時はautomatic retry commandを返さない。
17. `_run_uninstall_remove_specs_compatibility`、`_build_uninstall_plan`、`_apply_uninstall_plan`、old recursive removal、old `.uninstall-retry.json` writerへのproduction call edgeが0である。
18. legacy markerのread-only detectionは`managed_distribution.py`に残り、legacy stateを無視してpurge開始するrouteが0である。

### 8.5 Quality gates

19. focused purge/deprovision/CLI suites、fast lane、default suite、`make lint`、`./spec-dock/scripts/spec-dock validate`、`git diff --check` が成功する。
20. Full Regression verifierがfresh artifact directoryで`verified`となり、approved ledger exactnessとunexpected failure/error 0を示す。approved ledger自体は変更されていない。
21. final diffにnew public command/flag/schema、second journal/writer、runtime fallback、unresolved P0/P1がない。

## 9. 制約

- production filesystem writerは一つのimplementation sessionで直列変更する。purge serviceとlegacy writerを並行有効にした中間releaseを作らない。
- `build_workspace_assessment()` の fresh/update/init-force contractをpurge用に拡張しない。deprovision/purgeはdedicated destructive assessment seamを使用する。
- current journal schema version 1、protocol version 2、forward guard schema version 2を維持し、purgeはfield追加ではなく既存 intent/authority discriminantを拡張する。
- current Issue 370 P3 advisory（contract schema literalとjournal schemaの名称差、POSIX最終検証からunlinkまでの狭い非原子的窓）は本Issueで再設計しない。purge固有のregressionがそのseamに起因する場合だけ、Issue 371 acceptanceを満たす最小修正として扱う。
- implementation code、tests、READMEの変更は本Issue実装時に行う。本authoring成果物自体はrepository codeを変更しない。

## 10. 完了定義

本Issueは、I371-R01〜R40、Acceptance 1〜21がcandidate SHAの再現可能 evidenceへ結び付けられ、remove-specs production writerがcommon journaled kernel一つだけとなり、purge authority外のpathを削除できないことがnegative testsで証明された時点で完了する。

Issue 372へ渡す残作業は、D1〜D4で削除済みのlegacy seam absenceとpackage/platform parityの確認に限定する。Issue 371 ownerのlegacy purge writer、authority decision、recovery decisionをIssue 372へ先送りしない。
