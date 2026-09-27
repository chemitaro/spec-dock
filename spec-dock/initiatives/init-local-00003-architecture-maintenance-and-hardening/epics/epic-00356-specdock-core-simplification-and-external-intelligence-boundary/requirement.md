---
種別: 要件定義書（Epic）
ID: "epic-00356"
タイトル: "SpecDock Core Simplification and External Intelligence Boundary"
関連GitHub: ["#356"]
状態: "approved"
作成者: "ChatGPT-use-strict / main orchestrator"
最終更新: "2026-09-24"
親: ["init-local-00003"]
---

# epic-00356 SpecDock Core Simplification and External Intelligence Boundary — 要件定義

## 0. 後続決定と適用境界（2026-09-24）

Product Ownerが全面採用したIssue [#409](issues/iss-00409-scope-active-work-cli-redesign/requirement.md) のCLI再設計を、該当する現行契約と実装担当の正本とする。従来の `issue start/finish`、`active set` の旧引数、`new artifact [type]` とoptional positional type、Issue 357/360への旧CLI/installer再設計担当割当は、初回Core簡素化の履歴であり、#409の範囲では現行契約ではない。#409は三階層の `work start/finish`、明示 `artifact create --type`、一括cutoverを一つのIssueで所有する。Storage Core、External Intelligence境界、既存データ保全、正本R/D/Pとaccepted ADRの権威は引き続き本Epicで有効とする。以下の旧slice・checkpoint・検証記録は初回Core簡素化の履歴として読む。#409のCLI/installer受入条件にはそのR/D/PとACを適用し、旧記述を競合する第二の現行契約として使わない。

## 1. 目的

SpecDockを「認知的な作業手順を製品として所有する仕組み」から、次の二つを提供する小さな基盤へ縮小する。

1. **Storage Core**
   - Initiative / Epic / Issueの構造、GitHub linkage、依存DAG、active selection、三階層の薄いWork lifecycle、scope-local Artifact、Workbench / Worktree、sync / validate / doctorを保持する。
   - 構造操作と不変条件を決定的に扱う。
2. **Authoring Kit**
   - `requirement.md`、`design.md`、`plan.md`、薄い`report.md`、Artifactの意味、scope layering、Issue Planning Levelの文書ガイドを提供する。

Planning、Review、Execution、Assurance、Profile routing、provider固有import、PR workflow、モデル／ブラウザー／Oracle固有の判断は製品境界の外へ出す。外部IntelligenceはMarkdown、Git、CLI、安定したfile contractを利用する交換可能なclientであり、Runtimeのadapterやauthority sourceにはしない。

本Epicは`init-local-00003 Architecture Maintenance and Hardening`の下で、構造健全性、source-of-truth、runtime / scaffold / docs parity、運用可能性を改善する。

## 2. 現在の状態と問題

対象SHA `2c75e0c02cb65a6e74040a72dc161d342d661091` では、次の責務が同居している。

- Runtime parser / registryに`assurance`、`authoring`、`guidance`、`workflow`、`delegated-authoring`、provider固有の`artifact import chatgpt-output`が登録されている。
- Issue lifecycleがauthority / grants / promotion record、delegated artifact、Evidence Adoption Ledgerを判定する。
- Artifactの新規作成可能型と履歴認識型が混在し、draft / repair routingが残っている。
- Installerが多数のPlanning / Execution / ChatGPT / adapter / PR helper skillをmanaged assetとして配布する。
- provider docsがphase promotion、fresh reviewer gate、ChatGPT planning packを標準導線として案内する。
- Issue 357〜360のnode、GitHub linkage、dependency edgeは存在するが、各R/D/Pは未具体化のscaffoldである。

この複雑性により、構造管理の価値と、変更頻度が高い認知的workflowが密結合している。利用者が別のモデル、skill、作業方法を採用する場合も、SpecDock固有のgateやmetadataに従う必要が生じる。

## 3. Epic後に実現する利用者価値

- Fresh repositoryにはStorage Core、薄いAuthoring Kit、限定されたrepo-local skillだけが配布される。
- Existing repositoryはnode identity、GitHub linkage、正本文書、Artifact、Discussion、ADR、既存の重いReport、`.assurance.json`、profile由来文書を一括削除・rename・rewriteせずupdateできる。
- CLI helpとRuntime registryから撤去対象workflow surfaceが消え、別名fallbackも存在しない。
- `active set`、三階層の`work start` / `work finish`、dependency readiness、明示typeによるArtifact作成／importが#409の契約で動作する。
- Fresh Initiative / Epic / Issueは単一のR/D/Pと薄い常設`report.md`を持ち、Reportが空でもvalidである。
- Authoring Kitは一つのIssue `plan.md`、共通Plan Guide、`light` / `standard` / `strict` / `critical` Completion Guideを提供する。Runtimeはlevelを知らない。
- Provider source、dogfood projection、fresh installed consumer、updated existing consumerの契約を検証できる。
- External Intelligenceが存在しなくてもStorage Coreを利用でき、存在する場合もその出力を自動で正本化しない。

## 4. 採用済み要件

以下はProduct Ownerが採用済みであり、後続Issueで再質問・未決化しない。

### E-RQ-001 Runtime workflow、Profile、Assuranceを撤去する

parser、registry、domain、application、tests、docs、managed assetsのCurrent surfaceから除去する。履歴証跡は保持する。

### E-RQ-002 Planning Levelは文書だけで扱う

Issue `plan.md`は一つとし、共通Guideと4種類のCompletion Guideを用意する。levelをmetadata、Runtime state、gate、routingにしない。

### E-RQ-003 三階層の`work finish`を薄い便利操作にする

初回Core実装の`issue finish`に関するclose→全active clear→post-syncは履歴であり、#409の現行契約ではない。#409では対象Initiative / Epic / Issueをcompletedにし、選択チェーン内なら対象以下だけを解除して祖先を残す。未完了・取り止め・状態不明の子孫がいる親は完了できず、Git branch/HEADは変えない。Review、Plan、Test、Report、EAL、authorityを判定しない。close失敗時はactiveを保持する。

### E-RQ-004 activeとreadinessの意味を限定する

`active set`はselectionだけを行う。三階層の`work start`が開始条件とdependency readinessを確認する。旧`issue start --force`契約は#409で廃止し、別作業への選択切替は`--switch-active`で明示する。`ready`はdependency-onlyとする。blocked Scopeもplanning / researchのため選択できる。

### E-RQ-005 Artifact interfaceを単純化する

初回Coreのoptional positional typeは履歴である。#409の現行作成入口は`artifact create --scope TARGET --type TYPE --title TITLE`とし、typeを明示する。Currentの新規作成可能型は`blank`、`research`、`interview`、`disc`、`decision-candidate`、`adr`に限定する。`analysis`は追加しない。履歴型は認識できるが、新規作成経路には出さない。

### E-RQ-006 Importはfile onlyにする

任意provider専用のimport command、module、docs、testsをCurrent surfaceから外し、opaqueな単一ファイルを扱うgeneric importだけを残す。

### E-RQ-007 Fresh nodeに薄いReportを常設する

Fresh nodeは`Outcome`、`Verification`、`Residual Risks / Follow-ups`を持つ薄い`report.md`を常設する。空でもvalidで、Runtime gateにしない。Existing Report本文は保持する。

### E-RQ-008 repair badgeとdraftをCurrent surfaceから除く

既存証跡は保持するが、新規作成、Current navigation、workflow routingを終了する。

### E-RQ-009 durable decisionの置き場を限定する

長期に残す判断はEpic / IssueのRequirement、Design、Plan、またはaccepted ADRへ置く。ArtifactとReportはevidence / result summaryであり、正本判断の代替にしない。

## 5. Vertical slice要件

357〜360の行は初回Core簡素化のslice履歴である。後続のCLI再設計は#409の単一sliceとして追加し、初回担当を現在の再設計担当に読み替えない。各Issueは利用者に確認可能なend-to-end valueを閉じる。

| Slice | 利用者価値 | 同じIssue内で閉じる範囲 |
|---|---|---|
| `iss-00357`（初回Core） | 初回Storage Core CLIでnode / dependency / active / lifecycle / Artifactを安全に扱える | 初回Runtime code、CLI help、tests、historical compatibility。#409の再設計は所有しない |
| `iss-00358` | Fresh nodeの薄いR/D/P/ReportとAuthoring Guideだけで仕様を作成できる | templates、guides、navigation、artifact semantics、tests、projection、existing-doc preservation |
| `iss-00359` | Agent / operatorが二つのrepo-local skillからCoreとKitを正しく利用できる | skill contracts、provider assets、docs、negative behavior、tests、legacy handoff inventory |
| `iss-00360`（初回配布） | 初回Fresh / update / uninstall consumerが旧workflowを配布されず、既存データを失わない | 初回installer、managed prune、dogfood、migration、compatibility。#409の一括cutoverは所有しない |
| `iss-00409`（現行CLI再設計） | Initiative / Epic / Issueを同じWork lifecycleで扱い、明確なnamespaceと安全なcutoverを得る | 44 leafのCLI・Runtime・installer/schema migration・docs・testsを一つのIssueで所有する |
| 品質・統合・deliverable handoff候補 | 全implementation sliceを統合し、独立した最終検証と引渡し証跡を閉じる | full regression、cross-consumer smoke、defect-only fixes、diff audit、change-set handoff |

最後の品質・統合行は初回Core計画時の新規Issue候補であり、#409のIssue作成・一括実装判断とは別である。

## 6. スコープ

### 6.1 必須

- Epic 00356とIssue 357〜360のR/D/P再定義
- Runtime parser / registry / application / domain / infra / presentationのworkflow removal
- Active selection、三階層のWork start / finish、dependency semantics（#409を正本とする）
- ArtifactのCurrent / Historical分離、明示`--type`、generic file import（#409のCLI契約）
- Fresh node scaffoldとthin Report mechanism
- R/D/P/Report template、Authoring Guide、Planning Level Completion Guide
- Current / Historical docs navigation
- Repo-local skill boundary
- Provider assets、dogfood projection、installer init / update / uninstall
- Existing consumer preservation
- Unit、integration、CLI、consumer、negative、migration、link、parity tests
- 最終品質・統合・deliverable handoffの独立候補

### 6.2 対象外

- External model、browser、Oracle、provider APIの実装・運用
- Product-owned Planning / Review / Execution state machineの代替実装
- Runtime quality gate、reviewer adapter、EAL gate、PR gate
- Historical document / Artifact / Reportの一括書換え
- Existing `.assurance.json`のmigration変換
- `analysis` Artifact type
- 複数の正本Plan file
- provider固有importの再導入
- 新しいIssue numeric IDの仮付与

## 7. Authorityと互換性

- Epic / IssueのR/D/Pとaccepted ADRをdurable specificationとする。
- Artifactは調査・対話・比較・候補・reviewのevidence surfaceとする。
- `report.md`は結果要約であり、内容が空でもよい。
- Runtimeの`ready`はdependency-onlyとする。planning handoffの妥当性は文書上の契約であり、Runtime stateにしない。
- Existing node ID、parent chain、GitHub issue number、dependency metadata、正本file pathを保持する。
- Existing R/D/P/Report、Artifact、Discussion、ADR、profile由来文書、`.assurance.json`をpackage updateで書き換えない。
- Current creationを閉じた履歴Artifact typeをmalformed扱いしない。
- Generated stateはsource metadataから再生成可能にし、generated viewを履歴の正本にしない。
- Update pruneはmanaged inventoryとownership boundaryに限定し、user-owned pathを削除しない。
- Partial failureは再実行できる状態と診断を残す。

## 8. Epic受け入れ条件

### E-AC-001 Removed surface

撤去対象のRuntime command、registry key、module、Current docs entry、managed skillが消え、alias fallbackも存在しない。

### E-AC-002 Thin lifecycle

`active set`はselection-only。三階層の`work start`は#409の開始条件とdependencyを確認し、`work finish`は対象をcompletedにして選択中なら対象以下だけを解除する。親の完了には全子孫completedを要し、quality evidenceは読まない。旧`issue start/finish`の順序・`--force`・全active clearは初回Coreの履歴である。

### E-AC-003 Artifact contract

#409の現行CLIでは`--type`を明示してCurrent 6種だけを作成できる。旧type omitted/positionalは初回Coreの履歴である。Historical typeは認識されるが新規作成できない。Generic importは一ファイルだけをopaqueに保存し、provider固有routeは存在しない。

### E-AC-004 Fresh authoring contract

Fresh nodeは単一R/D/Pと薄いReportを持つ。Report空状態でもvalidate、active、deps、start、finishがReport gateによって失敗しない。

### E-AC-005 Planning Level

Issue Planは一つで、Base Guideと4 Completion Guideが存在し、Runtime code / metadataにPlanning Levelがない。

### E-AC-006 Skill boundary

Repo-local skillはCore / Kitを案内し、正本自動変更、provider-owned AI invocation、quality gateを行わない。

### E-AC-007 Consumer migration

Fresh / update / uninstallのconsumer matrixが、旧managed assetの除去と既存user-owned dataの保持を検証する。

### E-AC-008 Parityと否定検証

Provider / dogfood / installed parity、internal link、Currentで禁止する語彙、removed surface absenceを検証する。

### E-AC-009 Vertical slice completion

初回357〜360はそれぞれのcode / test / docs / migration or compatibilityを閉じる。後続のCLI/Runtime/installer/schema再設計は#409が一つのIssueで所有し、旧sliceへの二重割当をしない。

### E-AC-010 Final integration

人間が最終Issue候補を採用した場合、そのIssueは357〜360すべてに依存し、full regression、cross-slice integration、defect-only repair、diff audit、deliverable handoff evidenceを独立して扱う。

## 9. リスクと保護策

| リスク | 保護策 |
|---|---|
| workflow撤去時に構造invariantまで失う | Storage Core retain inventoryとremoved inventoryを分け、positive / negative testを置く |
| 初回357と358のshared fileが衝突する | 初回は357がmechanism、358がtemplate / guide contentを所有した。#409のCLI再設計所有権は#409に一本化する |
| Historical typeをunknownとして壊す | current creatableとhistorical recognizableを別API / test matrixにする |
| Updateがuser dataを削除する | managed ownership inventory、preflight、preservation fixture、partial-failure recoveryを用意する |
| docs-only LevelがRuntimeへ再侵入する | forbidden code / metadata scanとbehavior invariance testを置く |
| 最終品質が360へ埋没する | 人間承認後、独立した最終Issueとして357〜360すべてに依存させる |
| Evidenceが正本として誤用される | EALへ採否を記録し、main orchestratorが正本へ再記述し、fresh reviewを行う |

## 10. 残る人間判断

- 本書で定義したvertical-slice remapを採用するか。正本Requirementへの統合により採用し、fresh reviewで妥当性を確認する。
- 品質・統合・deliverable handoff候補を実Issueとして作成し、numeric ID / GitHub linkageを割り当てるか。これは未承認である。
- 357 / 358の並行実装開始前に、各Issueのexact file inventoryとshared-file ownershipをIssue planningで固定する。
