---
種別: disc
ID: "20260719t135413z-06-disc"
タイトル: "init-00322 完全Planning Bundle Traceability"
状態: "revision-candidate"
作成者: "GPT-5.6 Pro"
最終更新: "2026-07-19"
親: ["init-00322"]
authority: "verification evidence"
derived_from:
  - "requirement.md"
  - "design.md"
  - "plan.md"
reflected_to: []
---

# init-00322 完全Planning Bundle Traceability

## Scope

このTraceabilityは、完全置換用のRequirement、Design、Plan全体と、Plan Review指摘を反映したAC責任分離およびEpic 7 handoff boundaryを対象とする。

## AC責任の読み方

- `主実装責任Epic`は、ACを成立させるcapability、Workflow、test、documentation、cutover処理とEpic-level evidenceを所有する。
- `共同実装／証拠提供Epic`は、主実装責任Epicへ必要なintegration surfaceと証拠を渡す。主実装責任は移転しない。
- `Initiative-level final verification／closure owner`はEpic 7であり、AC-001〜AC-025をHuman merge済み成果上で最終確認する。未実装または証拠不足は元の主実装責任Epicへ戻す。

## Requirement coverage

| Requirement | 主なDesign | 主な実装Epic | Initiative-level final verification／closure |
|---|---|---|---|
| REQ-001〜REQ-005 | Actor／CLI／Planning／Context | 1、2 | 7 |
| REQ-006〜REQ-009 | Review Architecture | 3 | 7 |
| REQ-010 | Repair Batch | 4 | 7 |
| REQ-011〜REQ-013 | Actor／Brief／Executor／Issue Execution | 4 | 7 |
| REQ-014〜REQ-015 | Issue／Epic／PR Delivery | 5 | 7 |
| REQ-016〜REQ-018 | Authority／State／Cutover／Parity | 1〜6 | 7 |
| REQ-019 | Evaluation／Final Quality | 7 | 7 |
| REQ-020〜REQ-024 | Architecture-Aware Execution Brief | 1、4 | 7 |
| REQ-025 | Comparative evaluation | 7 | 7 |

## Acceptance Criteria ownership

| Acceptance Criteria | Canonical acceptance condition | 主実装責任Epic | 共同実装／証拠提供Epic | Initiative-level final verification／closure owner |
|---|---|---|---|---|
| AC-001 | `init-00322`の三文書が相互に矛盾せず、REQ-001〜REQ-025と7 Epicのtraceabilityを持つ。 | Epic 2 | Epic 1, Epic 3〜Epic 6 | Epic 7 |
| AC-002 | Actor responsibilityとHuman GateがPlanning、Review、Execution Brief、Repair、Execution、Deliveryで一貫し、ChatGPT evidenceの自己申告だけでauthorityが成立しない。 | Epic 1 | Epic 2〜Epic 6 | Epic 7 |
| AC-003 | Initiative／Epic／Issue Planningが完全Bundle生成、セルフレビュー、内容不変配置、必要なHuman分割承認を実行できる。 | Epic 2 | Epic 1 | Epic 7 |
| AC-004 | ChatGPT連携境界がGitHub exact repository／branch／HEADへfail closedでbindされ、default branchまたはtracked file添付へ黙ってfallbackしない。 | Epic 1 | Epic 2〜Epic 5 | Epic 7 |
| AC-005 | Planning、Checkpoint、Issue Delivery、Epic DeliveryのReviewがP0／P1、P2／P3、証拠不足を意図したsemanticsで扱う。 | Epic 3 | Epic 2, Epic 4, Epic 5 | Epic 7 |
| AC-006 | `repository-conventions`が規約あり／なしの双方で動作し、未定義規約を捏造しない。 | Epic 3 | — | Epic 7 |
| AC-007 | Targeted Reviewが対象とPerspectiveを受け、advisory結果だけを返し、Formal Gateやrepository mutationを発生させない。 | Epic 3 | — | Epic 7 |
| AC-008 | Repair BatchがSource HEADへbindされ、Mainの採用後にfreezeされ、materialな契約変更をPlanningへ返せる。 | Epic 4 | Epic 3 | Epic 7 |
| AC-009 | Executor、`spec-dock-chatgpt`、隠れたautomationがGit transactionを行わず、Mainが定義済みtransitionで明示的にcommit／pushし、Humanだけがmergeする。 | Epic 1 | Epic 4〜Epic 6 | Epic 7 |
| AC-010 | 主要write Agentがcustom Executor一つへ統合され、不要なWriter／Reviewer／Analyzer経路がmaintained surfaceから除去される。 | Epic 4 | Epic 6 | Epic 7 |
| AC-011 | Issue ExecutionがExecution Tranche、Architecture-Aware Execution Brief、Checkpoint、Repair、Issue Delivery、Issue Exit ContractをE2Eで処理できる。 | Epic 4 | Epic 3, Epic 5 | Epic 7 |
| AC-012 | Epic DeliveryがIssue ReviewとEpic Reviewを区別し、Delivery Ownerとintegration verificationを用いてPR Deliveryへ進める。 | Epic 5 | Epic 3, Epic 4 | Epic 7 |
| AC-013 | PR DeliveryがP0／P1またはrequired CI failureを修復し、新HEADで必要なgateを再観測してmerge-preparedで停止する。 | Epic 5 | Epic 3, Epic 4 | Epic 7 |
| AC-014 | P2／P3だけではbranch mutation、再CI、再Reviewを行わない。 | Epic 5 | Epic 3 | Epic 7 |
| AC-015 | Human merge前にMerge Exitの`issue finish`／`epic finish`を行わず、merge後に最終reviewed headを確認する。 | Epic 5 | — | Epic 7 |
| AC-016 | provider、installed、dogfoodでSkill／Agent／Workflow／Template／Scriptの責務parityが確認され、旧必須surfaceが残っていない。 | Epic 6 | Epic 1〜Epic 5 | Epic 7 |
| AC-017 | 既存open Scopeが文書migrationなしでvNext Workflowへ入り、不足契約だけを局所Planning refreshできる。 | Epic 6 | Epic 2, Epic 4 | Epic 7 |
| AC-018 | 代表dogfoodとInitiative-level final qualityが完了条件を満たし、各Epicが独立したmerge boundaryでHuman mergeまで完了する。 | Epic 7 | Epic 1〜Epic 6 | Epic 7 |
| AC-019 | 非機械的な代表Milestoneで、ChatGPTがexact HEADから関連Artifactとrepository evidenceを横断調査し、目的、現状、適用Concern、テスト戦略、実装戦略、停止条件を含むBriefを生成する。 | Epic 4 | Epic 1 | Epic 7 |
| AC-020 | DDD／イベント駆動を含むUnitでは該当Concernを選択し、CLI／build／documentation等のUnitでは非該当Concernを強制せず、存在しないdomain／event概念を捏造しない。 | Epic 4 | — | Epic 7 |
| AC-021 | `ready` BriefだけがWorkbench candidateからIssue Artifactへ昇格・freezeされ、`planning-gap`／`insufficient-evidence`ではExecutorを開始しない。 | Epic 4 | Epic 1 | Epic 7 |
| AC-022 | accepted Briefが`plan.md`を変更せず、特定Execution Unitのsubordinate contractとしてExecutorへ渡され、Briefと対応実装が同一candidate commitに含まれる。 | Epic 4 | Epic 2 | Epic 7 |
| AC-023 | ChatGPTが関連Artifactを意味的に選択し、Codex／wrapperは決定的なnavigation anchorsだけを提供する。Mainはraw Artifactを再分析せず、binding、status、evidence、scopeを確認する。 | Epic 4 | Epic 1 | Epic 7 |
| AC-024 | Briefなし、汎用Brief、Architecture-Aware Briefを代表Unitで比較し、Architecture-Aware BriefがEvidence completeness、test strategy、first-pass convergence、または手戻りで改善し、品質を悪化させない。 | Epic 7 | Epic 4 | Epic 7 |
| AC-025 | Codex tokenまたはproxyとしてのtool call、探索回数、failure cycle、handoff量の少なくとも一つが改善し、改善しない場合も品質効果と総遅延を含む継続判断が記録される。 | Epic 7 | Epic 1, Epic 4 | Epic 7 |

## Epic handoff responsibility

| Epic | 主実装責任AC | 共同実装／証拠提供AC | Handoff boundary |
|---|---|---|---|
| Epic 1 | AC-002, AC-004, AC-009 | AC-001, AC-003, AC-016, AC-018, AC-019, AC-021, AC-023, AC-025 | exact HEAD、authority、Git ownership、deterministic anchors、baseline evidenceをEpic 7へ渡す |
| Epic 2 | AC-001, AC-003 | AC-002, AC-004, AC-005, AC-016, AC-017, AC-018, AC-022 | complete Planning Bundle、content-preserving placement、Human decomposition evidenceをEpic 7へ渡す |
| Epic 3 | AC-005〜AC-007 | AC-001, AC-002, AC-004, AC-008, AC-011〜AC-014, AC-016, AC-018 | Formal／Targeted Review Protocolとresult evidenceをEpic 7へ渡す |
| Epic 4 | AC-008, AC-010, AC-011, AC-019〜AC-023 | AC-001, AC-002, AC-004, AC-005, AC-009, AC-012, AC-013, AC-016〜AC-018, AC-024, AC-025 | Brief／Repair／Executor／Issue E2Eと比較評価用raw evidenceをEpic 7へ渡す |
| Epic 5 | AC-012〜AC-015 | AC-001, AC-002, AC-004, AC-005, AC-009, AC-011, AC-016, AC-018 | Delivery Topology、PR gate、merge-prepared、Human merge／post-merge evidenceをEpic 7へ渡す |
| Epic 6 | AC-016, AC-017 | AC-001, AC-002, AC-009, AC-010, AC-018 | parity、no-migration replay、rollback rehearsal、single authority、known-good restoration evidenceをEpic 7へ渡す |
| Epic 7 | AC-018, AC-024, AC-025 | AC-001〜AC-025のHuman merge済み証拠を統合 | 独立merge boundaryでmerge-preparedに停止し、Human merge後にfinal verification／closureを反映する |

## Epic 7 boundary trace

- 依存: Epic 1〜Epic 6。原則として全依存EpicがHuman merge済みで、owner別AC evidenceが利用可能であること。
- 対象外: 新規feature workstream、Human未承認のEpic追加／分割／統合／責任再配分、未完実装の黙示的吸収、自動merge、merge前completion。
- Delivery Boundary: 独立merge boundary、latest HEAD gate後の`merge-prepared`停止、Human-only merge、post-merge reviewed head確認、`report.md`へのcompletion反映。

## Known JIT follow-up preservation

- Epic 6 JIT Planningはrollback rehearsal、authority single-source確認、known-good boundary restoration verificationを具体化する。
- 各Epic JIT PlanningはPlan §4.4のmetric責務を具体化する。特にM-006 parity、M-007 reliability、M-008 changeability、M-009 Brief quality、M-010 convergence、M-011 resourceをowner別に採取する。
- AC-023はRequirementのcanonical wordingどおり、ChatGPTの意味的Artifact選択、Codex／wrapperのdeterministic navigation anchors、Mainのbinding／status／evidence／scope確認を扱う。

## Cross-document consistency

- Requirementの25 REQ、7 NFR、25 AC、13 Metrics、15 RisksをDesignとPlanが扱う。
- Epic数は7で、依存DAGは`E1 → E2/E3 → E4 → E5 → E6 → E7`。
- `plan.md`はIssue全体のPlanning SSOTであり、Execution Briefは特定Execution Unitに限定されたfrozen subordinate contractである。
- `ready | planning-gap | insufficient-evidence`、Workbench candidateから内容不変Artifactへのfreeze、exact HEAD binding、same candidate commit、stale detectionを維持する。
- Execution Briefはproactive、Repair Batchはreactiveであり、MainだけがGit transactionを所有し、mergeはHumanだけが行う。
- Architecture-Aware Execution Briefはrepository evidenceから適用Concernだけを選択し、特定architectureを必須化しない。
- このTraceabilityとself-reviewはfresh Formal Plan Reviewを代替しない。
