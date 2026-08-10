---
種別: 要件定義書（Issue）
ID: "iss-00358"
タイトル: "Simplify Authoring Kit and Document Contracts"
関連GitHub: ["#358"]
状態: "approved"
作成者: "ChatGPT-use-strict / main orchestrator"
最終更新: "2026-08-10"
親: ["epic-00356", "init-local-00003"]
承認: "Product Owner review completed 2026-08-10"
---

# iss-00358 Simplify Authoring Kit and Document Contracts — 要件定義

## 1. 目的

特定のmodel、provider、Skill、workflow state、Assurance Profileに依存せず、利用者がFresh Initiative / Epic / Issueの仕様をMarkdownで作成・理解できるAuthoring Kitを提供する。

本Issueはtemplateファイルの削減だけを目的としない。利用者がFresh nodeを作成し、各文書の責務を理解し、IssueのPlanning Levelに応じた完成基準を選び、Artifactの証拠をdurableな仕様へ反映できるend-to-end authoring experienceを、template、Guide、navigation、tests、dogfood projection、migration / compatibilityまで含めて成立させる。

## 2. 背景

対象baseline `2c75e0c02cb65a6e74040a72dc161d342d661091` では、次の認知的workflow policyがAuthoring assetに混在している。

- Requirement / Design / Plan template内のGrade、reviewer gate、promotion、EAL、delegated authoring、change-set status
- Assurance classification / composeを前提とするIssue Design / Plan placeholder
- `templates/issue-profiles/<profile>/`と`draft-*` routing
- 大規模なledger / gate scaffoldである`report.md`
- phase promotion、fresh reviewer、ChatGPT authoring packをCurrent導線とするdocs
- Current / Historical Artifact catalogの混在
- Planning Levelを文書だけで扱うというProduct Owner承認が未反映のasset構造

この構成では、利用者が単一のR/D/Pを編集するだけでもSpecDock固有のworkflow authorityを理解する必要がある。本Issueは、Thin TemplateとDetailed Guideを分離し、Authoring Kitをprovider-neutralかつscope-awareな文書契約へ戻す。

## 3. 採用済みProduct Owner判断

| ID | 採用日 | 判断 |
|---|---|---|
| `PD-358-001` | 2026-08-08 | Runtime上のProfile / Assurance / `draft-*` routingを新規作成surfaceから完全に外す。既存証拠はHistoricalとして保持する |
| `PD-358-002` | 2026-08-08 | 各Issueのcanonical `plan.md`は一つだけとし、共通Plan Guideと`light` / `standard` / `strict` / `critical`のCompletion Guideを用意する |
| `PD-358-003` | 2026-08-09 | `new artifact`のtypeはoptional positionalとし、未指定時は`blank`。typeを指定するときは`research`等を明示する |
| `PD-358-004` | 2026-08-09 | Fresh全scopeに薄い`report.md`を常設する。内容は任意、空でもvalid、Runtime gateにはしない |
| `PD-358-005` | 2026-08-10 | Epic R/D/PとIssue 358 Draft 1を採用し、ユーザーレビュー完了とする |

## 4. 親スコープから継承する契約

| Issue要件 | 親Epic要件 | 継承内容 |
|---|---|---|
| `RQ-358-001` | `E-RQ-001`, `E-RQ-007` | Profile / Assurance非依存のthin R/D/P/Reportを提供する |
| `RQ-358-002` | `E-RQ-009`, Epic Authoring Kit境界 | R/D/P/Reportの責務を分離し、durableな判断の置き場を説明する |
| `RQ-358-003` | Epic vertical slice / scope layering契約 | Initiative / Epic / Issueの責務差と継承境界を説明する |
| `RQ-358-004` | `E-RQ-002` | Planning Levelをdocs-only conceptとして提供する |
| `RQ-358-005` | `E-RQ-005`, `E-RQ-008` | Current六種とHistorical evidenceの意味を説明する |
| `RQ-358-006` | `E-RQ-009` | durable decision、Artifact、Reportのauthority境界を明示する |
| `RQ-358-007` | `E-RQ-001`, `E-RQ-008` | CurrentとHistoricalの導線を分離し、旧workflowを再推奨しない |
| `RQ-358-008` | Epic互換性 / parity / vertical slice契約 | Existing文書の保持、provider / dogfood parity、357 / 359 / 360へのhandoffを提供する |

本IssueはRuntime parser / lifecycle / filename allocation、skill実装、installer prune、最終deliveryを所有しない。

## 5. 対象範囲

### 5.1 対象

- Initiative / Epic / IssueのR/D/P/Report template
- Authoring Overview
- Requirement / Design / Plan / Report Guide
- Scope Layering Guide
- Artifact GuideとCurrent / Historical catalog
- canonical Issue Plan一つ
- Base Plan Guideと四つのCompletion Guide
- Current / Historical navigation
- provider-side Authoring assetsとdogfood projection
- template catalog、heading、link、vocabulary、parity test
- Existing consumer preservation fixture
- removed / historical-only asset inventory
- Issue 357とのIC-1、Issue 359 / 360へのhandoff

### 5.2 対象外

- Runtime parser / registry / active / lifecycle / dependency / Artifact filename実装（Issue 357）
- node scaffolderのfilesystem mechanism（Issue 357）
- repo-local skill本文（Issue 359）
- installer prune、fresh / update / uninstall consumerの最終移行（Issue 360）
- Existing node-local文書の一括rewrite
- External Intelligence
- Runtime quality gateまたはPlanning Level parser
- 新しいArtifact type
- level別canonical Plan file
- 最終release / PR / change-set handoff

## 6. 文書責務要件

### RQ-358-001 Thin scope templates

Fresh Initiative / Epic / Issueには、それぞれ一つの`requirement.md`、`design.md`、`plan.md`、`report.md`を生成するためのthin templateを提供する。

templateに含めるもの:

- 完成文書に残る見出し
- R/D/Pでは各sectionの目的を示す短いprompt。Reportは`AC-358-006`のempty-valid契約を優先し、三つの必須sectionを空本文で開始する
- 最小限のplaceholder
- optional sectionの明示
- 対応するstable Guideへのlink

templateに含めないもの:

- workflow state / phase promotion
- reviewer / Grade / EAL / authority / delegated authoring
- full example / anti-pattern catalog
- provider、model、browser、Oracleの利用手順
- PR / change-set status
- Report内容を完了条件にするgate

### RQ-358-002 Document responsibility

#### `requirement.md`

- problem、why now、stakeholder / user outcome
- scope / non-scope
- observable behavior
- constraints、compatibility、acceptance
- risks、assumptions、open human decisions

実装順、class / module設計、test実装詳細を置かない。

#### `design.md`

- Current / Target architecture
- responsibility boundary
- data / interface / failure contract
- migration / compatibility strategy
- testability / observability design
- 理解に有用な図

business acceptanceを再定義せず、Requirementを実現する構造を扱う。

#### `plan.md`

- Planning Level選択と理由
- vertical implementation sequence
- dependency / parallelism
- verification strategy
- migration / rollback
- completion / exit criteria
- handoff / residual risk

未解決のdurable design decisionはPlan内で隠して決めず、DesignまたはADRへ戻す。

#### `report.md`

- Outcome
- Verification
- Residual Risks / Follow-ups
- optional Notes

内容の記入は任意で、空のsectionでもvalidとする。Decision Ledger、EAL、Authoring Gate、Reviewer Status、Delegated Draft Evidence、Promotion、Completion GateをFresh templateへ含めない。

### RQ-358-003 Scope layering

Authoring Guideは次の責務差を明示する。

- Initiative: 複数Epicにまたがる戦略的problem / outcome、投資境界、portfolio dependency、広いrisk
- Epic: coherentなproduct / architecture outcome、vertical Issue slice、cross-Issue contract、rollout / integration
- Issue: 一つのend-to-end observable value、具体的acceptance、implementation / tests / docs / migration、rollback / handoff

Initiative / EpicにIssueの実装micro-stepやIssue Planning Levelを要求しない。Issueは親Epicの目的・分割・依存方向を再定義しない。

### RQ-358-004 Planning Level

各Issueのcanonical Planは`plan.md`一つとする。Authoring Kitは次を提供する。

- 共通Base Plan Guide
- `light` Completion Guide
- `standard` Completion Guide
- `strict` Completion Guide
- `critical` Completion Guide

各Completion GuideはBase Guideへの独立差分であり、別levelの順読を要求しない。Planning Levelは通常のMarkdown本文にselected level、理由、risk factor、再評価条件として記録する。

Levelは文書量、実装工数、Priority、Severityではなく、失敗した場合の影響と回復困難性で選ぶ。dependency readiness、implementation handoff status、Runtime上の実行可否を表す状態にはしない。未指定時に`standard`を執筆上の推奨として案内してよいが、Runtime defaultや暗黙metadataにはしない。

RuntimeはPlanning Levelをparse、persist、validate、route、enforceしない。`.meta.json`や`.assurance.json`をauthorityとしない。level変更は同じ`plan.md`のGit diffとして扱う。

| Level | 想定用途 | 完成時に強く求めるもの |
|---|---|---|
| `light` | 局所的、低blast radius、容易なrevert | direct AC、targeted verification、残作業なし |
| `standard` | 通常のfeature / bug fix | end-to-end順序、主要error、regression、基本rollback |
| `strict` | public contract、Runtime、data、migration、compatibility | As-Is / To-Be、failure mode、negative test、rollback / forward recovery |
| `critical` | security / privacy、高blast radius、不可逆・回復困難 | threat / data、staged rollout、kill switch、backup / restore、incident response |

### RQ-358-005 Artifact semantics

Current Guideは次の六種だけを新規作成surfaceとして説明する。

| Type | 目的 | durableな反映先 |
|---|---|---|
| `blank` | 自由形式のevidence | 必要な内容をR/D/P/accepted ADRへ再記述 |
| `research` | 一つのsource-grounded investigation | facts / constraintsを適切な正本へ |
| `interview` | 明示的な質問と回答 | 採用回答をR/D/P/accepted ADRへ |
| `disc` | 複数証拠のsynthesis / trade-off | durable conclusionを正本へ |
| `decision-candidate` | 未採用decision option | 人間判断後に正本へ |
| `adr` | architecture decision candidate / record | accepted stateのADRのみauthorityになり得る |

`analysis`は追加しない。一つのsource調査は`research`、複数sourceの統合は`disc`を使う。`blank`は弱いtemplateによりmodelの分析能力を妨げない自由形式surfaceとする。

### RQ-358-006 Authority boundary

```text
Artifact evidence
  -> 人間またはagentによるsynthesis / review
    -> Requirement / Design / Plan または accepted ADR
      -> implementation
        -> thin Report result summary
```

- Artifactの存在やtypeは採用を意味しない。
- Reportはdurable decision storeまたはRuntime gateにならない。
- ADRは`accepted`が明示された場合だけdurable authorityになり得る。
- 外部生成ZIP、delegated draft、ChatGPT outputはevidenceであり、自動昇格しない。
- Current Guideはmandatory EAL schemaや特定review workflowを導入せず、このauthority境界を平易に説明する。

### RQ-358-007 Current / Historical navigation

Current navigationはStorage CoreとAuthoring Kitを第一導線とし、thin R/D/P/Report、Current六種、Authoring Guideへ案内する。

Historical navigationは、旧Profile / Assurance / workflow / draft / repair surfaceを次の意味で説明する。

- 既存証拠として保持する。
- 新規作成には使わない。
- 自動削除、rename、rewriteを要求しない。
- durableな内容は必要に応じてCurrent R/D/P/accepted ADRへ反映する。

Currentページは旧workflowを推奨してはならない。Historicalページやfixtureが旧語を含むことは許容する。

### RQ-358-008 Projection / compatibility / handoff

- provider sourceをAuthoring assetの正本とする。
- dogfood projectionはproviderと同じrelative treeと期待内容を持つ。
- user-owned node-local文書はmanaged parity対象にしない。
- template変更はFresh nodeにだけ適用し、Existingの次のuser-owned surfaceを更新時に書き換えない。
  - canonical R/D/P
  - thin / heavy Report
  - Current六種のArtifact
  - draft / repair / scratch / note / generic importを含むHistorical Artifact
  - Discussion
  - accepted / candidateを含むADR
  - `.assurance.json`
  - Profileから作成されたnode-local文書
- obsolete provider assetの最終pruneはIssue 360へ渡すinventoryとして確定する。
- Issue 357へscope file名、Current六種、Report path / empty-valid / non-gating、one-plan contractを渡す。
- Issue 359へAuthoring Guide pathとsemantic summaryを渡す。
- Issue 360へfresh asset inventory、obsolete asset inventory、preservation list、parity expectationを渡す。

## 7. 失敗・境界条件

| ID | 条件 | 必須結果 |
|---|---|---|
| `EC-358-001` | Current template / Guideに旧workflow用語が残る | vocabulary testが失敗する |
| `EC-358-002` | Historical page / fixtureに旧語がある | Current扱いせず許容する |
| `EC-358-003` | levelを`.meta.json`やRuntime stateへ追加しようとする | scope違反として停止する |
| `EC-358-004` | `plan-light.md`等を追加しようとする | one-plan契約違反として停止する |
| `EC-358-005` | Report templateがgate / ledgerへ再肥大化する | thin Report契約testが失敗する |
| `EC-358-006` | providerとdogfoodのmanaged assetがdriftする | parity testが失敗する |
| `EC-358-007` | Current navigation linkが切れる | link testが失敗する |
| `EC-358-008` | Existing consumer fixtureの文書hashが変わる | preservation testが失敗する |
| `EC-358-009` | 357のscaffolder contractとpath / catalogが不一致 | IC-1をfailとして後続handoffを止める |

## 8. 受け入れ条件

| ID | 観測可能な完了条件 |
|---|---|
| `AC-358-001` | Initiative / Epic / Issueの各Fresh template catalogがR/D/P/Report一つずつである |
| `AC-358-002` | templateがthinで、完成文書に不要なworkflow policyや削除用commentを含まない |
| `AC-358-003` | Authoring Overview、R/D/P/Report Guide、Scope Layering Guide、Artifact GuideがCurrent navigationから到達でき、Guide contract testとfresh spec reviewが`RQ-358-002`の四文書責務、禁止する責務混在、`RQ-358-003`の三scopeの責務差と親scope非再定義を確認する |
| `AC-358-004` | canonical Issue Planは一つで、Base Guideと四つのCompletion Guideが独立に参照できる |
| `AC-358-005` | Planning Level本文を変更してもRuntime behavior / metadataが変わらない |
| `AC-358-006` | Fresh Reportが3〜4 section、内容任意、空でもvalid、non-gatingとして説明・testされる |
| `AC-358-007` | Current Artifact六種の用途が区別され、`analysis` / repair / `draft-*`がCurrent作成・navigationにない |
| `AC-358-008` | durable decision guidanceがR/D/Pまたはaccepted ADRを指し、Artifact / Reportの自動昇格を認めない |
| `AC-358-009` | Current template / GuideにGrade、Assurance、promotion、EAL、delegated authoring、provider固有の必須語がない |
| `AC-358-010` | provider / dogfood catalog、link、expected bytesまたはnormalized contentのparity testが通る |
| `AC-358-011` | Existing consumer preservation fixtureにcanonical R/D/P、thin / heavy Report、Current六種、Historical Artifact、Discussion、ADR、`.assurance.json`、Profile由来node-local文書を含め、358-owned asset適用の前後で全byte hashが変わらない |
| `AC-358-012` | IC-1で357のfresh scaffold outputと358のfile / catalog / Report / one-plan contractが一致する |
| `AC-358-013` | 359向けGuide manifestと360向けretain / replace / historical-only / prune inventoryがreportへ記録される |
| `AC-358-014` | failure impact / recovery difficultyの組合せを用いたlevel選択例と、Priority / Severity / 工数 / dependency readinessだけではlevelを決めないnegative exampleがBase GuideまたはCompletion Guide contract testで確認される |

## 9. 非機能要件・制約

- 日本語を本文の第一言語とし、command、path、identifier、外部固有名詞は正確性のため原文を保持する。
- templateは最小限、Guideは具体的で丁寧にし、同じpolicyを複数fileへ複製しない。
- Guideは人間とagentのどちらも、他levelの文書を順番に読まなくても必要な契約へ到達できる構造にする。
- provider / dogfoodの重複はprojectionとして明示し、片側だけの編集を完了扱いにしない。
- shared fileを変更するときはIssue 357のRuntime mechanism、Issue 359のskill、Issue 360のinstaller ownershipを侵食しない。

## 10. 前提と未確定事項

- Profile撤去、one-plan、Base + Completion Guide、Current六種、thin ReportはProduct Owner承認済みであり再質問しない。
- target provider treeの最終file名は既存pathとlink migrationを調査して確定するが、上記の意味契約を変更してはならない。
- 新しい品質・統合・deliverable handoff Issueのnode作成は本Issueの対象外である。
- 上位scopeへ戻す未解決の製品判断はない。実装中にcross-Issue責務またはEpic契約を変更する必要が生じた場合は、本Issue内で決めずEpicへ戻す。

## 11. 根拠

- 親Epic: `../../requirement.md`、`../../design.md`、`../../plan.md`
- 承認済みDraft 1: `artifacts/20260809t125148z-draft-requirement-strict-vertical-slice-requirement.md`
- 設計候補: `artifacts/20260809t125149z-draft-design-strict-vertical-slice-design.md`
- 計画候補: `artifacts/20260809t125150z-draft-plan-strict-vertical-slice-plan.md`
- Profile / routing判断: `artifacts/20260808t083300z-interview-issue-profile-and-draft-routing.md`
- Planning Level構造判断: `artifacts/20260808t085519z-interview-planning-level-authoring-architecture-adoption.md`
- Report契約判断: `artifacts/20260809t025001z-interview-target-report-contract.md`
- Epic delivery index: `../../artifacts/20260809t122849z-disc-epic-00356-strict-planning-delivery-index.md`
