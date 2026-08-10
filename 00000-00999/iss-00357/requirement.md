---
種別: 要件定義書（Issue）
ID: "iss-00357"
タイトル: "Reduce Runtime to Storage Core"
関連GitHub: ["#357"]
状態: "approved"
作成者: "ChatGPT-use-strict / main orchestrator"
最終更新: "2026-08-10"
親: ["epic-00356", "init-local-00003"]
承認: "Product Owner review completed 2026-08-10"
---

# iss-00357 Reduce Runtime to Storage Core — 要件定義

## 1. 目的

SpecDockのRuntimeを、認知的なworkflow、Profile、Assurance、reviewer gateから切り離し、構造管理だけを決定的に実行するStorage Coreへ縮小する。

本IssueはRuntime内部のモジュール削除だけを目的としない。利用者が次の一連の操作を、外部モデルや品質判定の仕組みなしで最後まで実行できる状態を成果とする。

1. Initiative / Epic / Issueと依存関係を読む。
2. 調査または計画対象をactiveに選択する。
3. 依存関係が解決したIssueを開始する。
4. scope-local Artifactを作成または単一ファイルからimportする。
5. linked GitHub Issueをcloseし、成功後にactiveをclearする。
6. `sync` / `validate` / `doctor`で構造状態を確認する。

## 2. 背景

対象baseline `2c75e0c02cb65a6e74040a72dc161d342d661091` では、構造操作と次の認知的責務がRuntime内で結合している。

- `assurance`、`authoring`、`guidance`、`workflow`、`delegated-authoring`のcommand登録
- active entryのauthority、grants、promotion record
- `issue finish`におけるRequirement / Design / Plan、review、Report、Evidence Adoption Ledgerの判定
- Assurance Profileに基づく`draft-design` / `draft-plan` routing
- provider固有の`artifact import chatgpt-output`
- repair / draft用ArtifactのCurrent作成経路
- workflow authorityを含むActive Manifest / Context Pack
- Assurance composeを前提とするfresh node scaffold

この状態では、nodeや依存関係を管理するだけの利用者も、SpecDock固有の計画・review・証跡規約に従う必要がある。本Issueはこの密結合を解消し、Epic 356のStorage Core境界をRuntimeで成立させる。

## 3. 親スコープから継承する契約

| Issue要件 | 親Epic要件 | 継承内容 |
|---|---|---|
| `RQ-357-001` | `E-RQ-001` | Runtime workflow、Profile、AssuranceをCurrent surfaceから撤去する |
| `RQ-357-002` | `E-RQ-004` | active selectionをreadinessと分離し、selection-onlyにする |
| `RQ-357-003` | `E-RQ-004` | `issue start`だけがunfinished guardとdependency-only readinessを判定する |
| `RQ-357-004` | `E-RQ-003` | `issue finish`をGitHub close、active clear、post-syncだけの便利操作にする |
| `RQ-357-005` | `E-RQ-005`, `E-RQ-008` | ArtifactのCurrent作成型とHistorical認識型を分離する |
| `RQ-357-006` | `E-RQ-006` | generic file importだけを残す |
| `RQ-357-007` | `E-RQ-007` | AssuranceなしでR/D/Pと薄いReportを作るscaffold mechanismを提供する |
| `RQ-357-008` | Epic互換性契約 | 既存データを保持し、旧workflowを再起動しない |
| `RQ-357-009` | Epic vertical slice契約 | 358 / 359 / 360へ安定したhandoffを提供する |

本Issueは親Epicの目的、Issue分割、依存方向、最終品質Issue候補の採否を再定義しない。

## 4. 対象範囲

### 4.1 対象

- Runtime parser / registry / bootstrap
- retained commandのcommand adapterとapplication use case
- active state model、serialization、Active Manifest、Context Pack
- dependency readinessとIssue start
- Issue finishとGitHub close / active clear / post-sync
- Artifact domain、type catalog、filename allocation、template resolution
- generic `artifact import file`とprovider固有importの分離
- Initiative / Epic / Issue scaffolderのRuntime mechanism
- `sync`、`validate`、`doctor`への影響
- filesystem / Git / GitHub部分失敗とprivacy-safe diagnostics
- provider Runtime sourceとdogfood Runtime projection
- CLI help、Runtime reference、migration notes
- unit、application、CLI、negative、historical compatibility、projection tests
- Issue 358 / 359 / 360へ渡すcontractとinventory

### 4.2 対象外

- R/D/P/Report template本文、Authoring Guide、Planning Level Guideの執筆（Issue 358）
- repo-local skillの実装（Issue 359）
- installerの最終prune、fresh / update / uninstall consumer migration（Issue 360）
- release全体のfull regression、最終PR、deliverable handoff（人間承認待ちの最終Issue候補）
- 既存ユーザー文書、Report、Artifact、Discussion、ADRの一括削除・rename・rewrite
- External Intelligenceの実装
- 新しいquality / review / evidence gate
- `analysis` Artifact type

## 5. 機能要件

### RQ-357-001 Storage Core command surface

`spec-dock --help`とRuntime registryには、構造管理に必要なcommandだけをCurrent surfaceとして公開する。Targetのtop-level commandとsubcommandは次を正本inventoryとする。

| Top-level command | Targetで保持するsubcommand / leaf |
|---|---|
| `new` | `initiative`、`epic`、`issue`、`artifact` |
| `artifact` | `import file`だけ |
| `active` | `set`、`show`、`clear` |
| `issue` | `start`、`finish` |
| `deps` | `check`、`add`、`remove` |
| `import` | `initiative`、`epic`、`issue` |
| `worktree` | `create`、`list`、`show`、`remove` |
| `workbench` | `copy` |
| standalone | `delete`、`close`、`update`、`uninstall`、`sync`、`validate`、`doctor` |

保持するcommandの既存引数と正常系・失敗系は、本要件または親Epicが明示的に変更するものを除いて維持する。明示変更は次の二点である。

- `active set`はtarget positional、`--id`、`--github-issue`による選択だけを保持する。`--checkout`、`--no-checkout`、`--github`、`--no-github`、`--gh-limit`、`--force`は撤去し、branch操作、GitHub state取得、dependency迂回を行わない。
- `issue start`はtarget positional、`--id`、`--github-issue`、unfinished guardだけを迂回する`--force`、GitHub照会件数の既存上限指定を保持する。branch checkoutは`issue start`だけが所有する。

次の認知的command group、leaf、到達可能なalias / fallbackを撤去する。

- `assurance`
- `authoring`
- `guidance`
- `workflow`
- `delegated-authoring`
- provider固有のChatGPT import
- Profile / Grade classification、reviewer / EAL / promotion gate、draft routing

具体的には`assurance`、`authoring`、`guidance`、`workflow`、`delegated-authoring`、`artifact import chatgpt-output`をCurrent parser / registry / helpから除く。物理ファイル名だけで削除を判断せず、上記のretained / removed / shared inventoryとimport graphに基づいて到達性を確認する。正本inventoryにない新しいtop-level command、subcommand、互換aliasを実装判断だけで追加しない。

### RQ-357-002 active selection

`active set`はvalidなInitiative / Epic / IssueのIDとrepo-relative pathを選択する構造操作とする。

- dependency、unfinished Issue、Requirement / Design / Plan、review、Report、authorityを評価しない。
- dependencyでblockedなIssueも、調査・計画のためactiveにできる。
- Active Manifest / Context Packはnavigationに必要な構造情報だけを出力する。
- authority、grants、promotion record、Planning Level、review status、quality status、evidence adoption statusをtarget writeへ含めない。

### RQ-357-003 Issue start

`issue start <target>`は次の順序と境界を守る。

1. targetがIssueとして解決できる。
2. 別のunfinished active Issueがある場合は停止する。ただし`--force`はこのguardだけを迂回できる。
3. dependency DAGのdirect / inherited blockerを確認し、dependency-readyでなければ停止する。
4. branch checkoutを実行する。
5. checkout成功後にactiveを設定する。
6. 必要なpost-mutation syncを行う。

`--force`はdependency blocker、invalid target、checkout失敗、active persistence失敗を迂回してはならない。

unfinished active guardは、現在branchではなくactive manifestとactive Issueのlinked GitHub stateを基準にする。現在branchは診断情報であり、guardの成否を変えない。

| Active状態 | Active IssueのGitHub state | targetとの関係 | `--force`なし | `--force`あり |
|---|---|---|---|---|
| active Issueなし | 該当なし | 任意 | dependency確認へ進む | dependency確認へ進む |
| active Issueあり | 任意 | 同じIssue | dependency確認へ進む | dependency確認へ進む |
| active Issueあり | `CLOSED` | 別Issue | finishedとしてdependency確認へ進む | dependency確認へ進む |
| active Issueあり | `OPEN` | 別Issue | unfinished guardで停止 | guardだけを迂回しdependency確認へ進む |
| active Issueあり | `UNKNOWN`、linkなし、取得失敗、active node解決不能 | 別Issue | finishedと推測せずactionableに停止 | guardだけを迂回しdependency確認へ進む |

main、non-Issue branch、detached HEAD、active Issueとは異なるbranchでもこの表を適用する。guard通過後のdependency blocker、checkout失敗、active write失敗は`--force`の有無にかかわらず停止する。

### RQ-357-004 Issue finish

`issue finish`は次の順序で実行する。

1. active IssueとGitHub linkageを解決する。
2. linked GitHub Issueをcloseする。already closedは成功として扱う。
3. close成功後にだけactiveをclearする。
4. clear後にpost-syncする。

`issue finish`はRequirement / Design / Plan、test、review、Report、EAL、authority、promotion recordを読まず、完了品質を判定しない。

### RQ-357-005 Artifact creation

`new artifact`のtypeはoptional positionalとし、省略時とexplicit `blank`を同じCurrent契約として扱う。

Currentの新規作成可能型は次の六つに限定する。

- `blank`
- `research`
- `interview`
- `disc`
- `decision-candidate`
- `adr`

`analysis`、`pr-repair-batch`、`draft-requirement`、`draft-design`、`draft-plan`などはCurrent作成候補に出さない。ただしHistorical認識契約に含まれる既存ファイルは、その理由だけでmalformedにしない。

Targetで認識するHistorical catalogは次を最低限のbaseline-valid形式とする。

| Historical形式 | 例 / grammar | Targetの扱い |
|---|---|---|
| 旧typed Artifact | timestamp形式の`pr-repair-batch`、`draft-requirement`、`draft-design`、`draft-plan`、`scratch`、`note` | 既存fileを認識するが新規作成しない |
| grandfathered sequential Artifact | `NNN-adr-<slug>.md`、`NNN-disc-<slug>.md`、`NNN-note-<slug>.md` | 既存fileを認識するが新規作成しない |
| generic imported Artifact | `YYYYMMDDtHHMMSSz[-NN]--<original-basename>` | opaqueな既存identityとして認識する |
| legacy Discussion | `discussions/`配下でbaseline parserが受理するtimestamp形式とsequential形式 | 履歴証跡として保持する |

Current六種の既存Artifact、blank filename、上表のHistorical形式は、形式がcatalogに属することだけを理由に`validate` / `doctor`でmalformedにしない。一方、duplicate slot / ID、path escape、symlink、壊れたtimestamp、catalog外のtimestamp-intent typeは従来どおり診断する。Historical fileをCurrent navigation、作成候補、workflow routingへ自動昇格しない。

### RQ-357-006 Generic file import

`artifact import file`だけをCurrent import surfaceとして保持し、`artifact import chatgpt-output`とそのprovider固有routingを撤去する。

generic importは次を維持する。

- 明示指定された一つのregular file
- opaque bytesの保持
- scope検証とdestination-side collision protection
- path traversal、symlink、unsafe sourceの拒否
- source pathや機密情報を漏らさない出力
- publication失敗時のcommitted / not committed区別と回復手順

### RQ-357-007 Fresh node scaffold mechanism

RuntimeはAuthoring Kitが提供するdeterministicなscope templateから次を一つずつ作成できる。

- `requirement.md`
- `design.md`
- `plan.md`
- `report.md`

Profile選択、Assurance compose、Report本文解釈、draft routingを行わない。薄いReportと空の利用者記入欄を有効な入力として扱う。template本文の所有者はIssue 358とする。

Fresh scaffoldのpublicationは、同じcanonical IDを通常手順で作成する独立した`spec-dock` processと、processが継続する通常のI/O failureを対象にする。canonical treeは完成前に可視化せず、kernelのno-replace renameをcommit pointとし、既存canonical entryを上書き・削除・一時交換しない。commit前のhandled failureはidentityを証明できるowned stagingだけを回収し、identityを証明できないnamespace entryには触れない。

### RQ-357-008 互換性

- 既存`.assurance.json`はHistorical fileとして保持し、Storage Coreは通常操作で解釈しない。
- 既存Report bytesとcanonical R/D/Pを通常操作で変更・再合成しない。
- 既存Historical Artifact filenameを`RQ-357-005`の明示catalogに従って認識する。
- 既存generic imported Artifactのidentityとbyte semanticsを保持する。
- node / dependency metadata formatは、本Issue内で別途正当化された可逆migrationがない限り維持する。
- generated active / index / tree viewは再生成してよいが、source metadataとuser documentsは保持する。
- removed commandは明示的に拒否し、legacy backendやaliasへfallbackしない。

### RQ-357-009 Cross-Issue handoff

Issue 357は次を後続へ渡す。

- Issue 358: scope file名、六つのCurrent Artifact type、Report path / non-gating、one-plan contractを検証できるIC-1入力
- Issue 359: retained CLI inventory、Current command syntax、removed command absence
- Issue 360: removed Runtime / provider asset inventory、historical preservation obligation、migration上の注意

## 6. 失敗・境界条件

| ID | 条件 | 必須結果 |
|---|---|---|
| `EC-357-001` | invalid active / start target | 明確なerror、state変更なし |
| `EC-357-002` | dependency blocked Issueを`active set` | selectionは可能 |
| `EC-357-003` | dependency blocked Issueを`issue start --force` | blockerを表示して停止、state変更なし |
| `EC-357-004` | existing active IssueのGitHub state不明 | finishedと推測せずactionableに停止 |
| `EC-357-005` | checkout失敗 | active変更なし |
| `EC-357-006` | active persistence失敗 | 直前stateを復元し、部分変更を明示 |
| `EC-357-007` | GitHub close失敗 | active保持、retry guidance |
| `EC-357-008` | close成功後のactive clear失敗 | GitHub close済み / active残存を区別したpartial success |
| `EC-357-009` | close / clear成功後のpost-sync失敗 | close済み / active clear済み / projection staleを区別 |
| `EC-357-010` | Historical-only / unknown Artifact typeを作成 | Current六種を示して拒否、file作成なし |
| `EC-357-011` | collision exhaustion、symlink、path escape、scope mismatch | deterministic rejection、partial artifactなし |
| `EC-357-012` | existing heavy ReportやAssurance fixture | Core operationが旧gateを再開しない |

## 7. 受け入れ条件

| ID | 観測可能な完了条件 |
|---|---|
| `AC-357-001` | parser / registry / helpにretained commandだけがあり、removed groupとprovider固有importに到達できない |
| `AC-357-002` | Active Manifest / Context Packのtarget outputからauthority / grants / promotion / reviewer / EAL情報が除かれる |
| `AC-357-003` | `active set`がselection-onlyで、blocked Issueを選択できるpositive / negative testが通る |
| `AC-357-004` | `RQ-357-003`の全truth-table rowをmain / Issue / non-Issue branchの代表ケースで検証し、unfinished guard、dependency blocker、`--force`境界、checkout / persistence失敗が順序付きtestで固定される |
| `AC-357-005` | `issue finish`のclose成功、already closed、close失敗、clear失敗、post-sync失敗、no-quality-gateがtestで固定される |
| `AC-357-006` | omitted type、explicit blank、五つのtyped form、unknown / historical-only type、collision / lock / symlink / path escapeがtestで固定される |
| `AC-357-007` | generic file importのbyte保持、安全性、privacy、partial failure testが維持される |
| `AC-357-008` | Fresh Initiative / Epic / Issue作成が`.assurance.json`なしでR/D/P/Reportを生成し、通常の同時作成では完成treeを一つだけno-replace publishする。commit前のhandled failureはcanonical partialを残さず、identityを確認できるowned stagingを回収する |
| `AC-357-009` | 空のthin Report、heavy Report、EAL文字列、delegated authority metadata、`.assurance.json`、Planning Level本文、legacy active fieldの有無や内容を変えてもdeps / start / finishの結果が変わらず、それらを理由に`validate` / `doctor`が失敗しない。構造破損の診断は維持する |
| `AC-357-010` | `RQ-357-005`の各Historical形式とCurrent形式のfixtureを保持したまま`validate` / `doctor`がmalformedとしないpositive test、およびcatalog外timestamp-intent / duplicate / unsafe pathを診断するnegative testが通る |
| `AC-357-011` | Runtime help / reference / migration notesがretained semanticsをCurrentとして説明し、removed workflowを推奨しない |
| `AC-357-012` | provider sourceとdogfood Runtime projectionのexpected parityが検証される |
| `AC-357-013` | IC-1入力、359向けretained inventory、360向けremoved inventoryがIssue-local reportへ記録される |
| `AC-357-014` | `deps check`とsync projectionがdirect / inheritedの未解決blockerを列挙して`ready=false`を返し、全blocker解決後は`ready=true`を返す正負testが通る。R/D/P/Report、review、authorityの内容はreadyを変えない |

## 8. 非機能要件・制約

- 既存のfilesystem safety、atomic publication、rollback、privacy-safe outputを弱めない。
- retained commandの正常系だけでなく、順序依存の部分失敗を型または明確なresultとして区別する。
- provider-side実装を正本とし、dogfood Runtimeはprojection / verification対象として扱う。
- 物理削除より先にregistrationとimport graphを切り離し、hidden dependencyをtestで検出する。
- shared componentを変更する場合はIssue 358との所有権表に従い、template proseをIssue 357で決めない。
- 同一権限の非協調processが予測不能なtransaction名やheld ancestryをsyscall間で意図的にrename / replaceする攻撃はRuntime command内のsecurity boundary外とする。namespace tamperingを検知した場合は競合entry保全をcleanupより優先し、identity不明entryを削除しない。
- SIGKILL、power loss、filesystem corruptionによるhidden orphanの完全回収は本Issueのhandled failure保証外とする。将来これを保証する場合はrecovery journal / GCまたは別UID / sandbox境界を別設計する。

## 9. 前提と未確定事項

- Product semantics、Current Artifact六種、lifecycle順序、one-plan / thin-report contractは親EpicとProduct Owner承認により確定済みである。
- 新しい品質・統合・deliverable handoff Issueのnode作成は本Issueの判断対象ではない。
- retained / removed moduleの正確な物理一覧は、`RQ-357-001`のCLI inventoryを変えない機械的inventoryとして実装Stepで確定してよい。
- 上位scopeへ戻す未解決の製品判断はない。実装中に境界を変える必要が生じた場合は、本Issueのplanを拡張せずEpicへ戻す。

## 10. 根拠

- 親Epic: `../../requirement.md`、`../../design.md`、`../../plan.md`
- 承認済みDraft 1: `artifacts/20260809t125145z-draft-requirement-strict-vertical-slice-requirement.md`
- 設計候補: `artifacts/20260809t125146z-draft-design-strict-vertical-slice-design.md`
- 計画候補: `artifacts/20260809t125147z-draft-plan-strict-vertical-slice-plan.md`
- Epic delivery index: `../../artifacts/20260809t122849z-disc-epic-00356-strict-planning-delivery-index.md`
