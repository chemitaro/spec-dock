---
種別: ADR（Architecture Decision Record）
ID: "20260722t031603z-21-adr"
タイトル: "Scope Specific Planning Adoption Gate Before Execution Ready"
状態: "accepted"
作成者: "GPT-5.6 Pro"
最終更新: "2026-07-22"
親: ["init-00322"]
authority: "accepted"
accepted_authority: "user-directed Candidate v12 review resolution"
accepted_at: "2026-07-22"
accepted_by: "Human"
mirror_eligible: true
artifact_type: "adr"
derived_from:
  - "Candidate v12 Red-Team finding RTV12-P1-001"
  - "Universal Planning Candidate lifecycle"
  - "Candidate v13 Red-Team finding INIT-00322-V13-RT-001"
  - "Candidate v14 Red-Team finding INIT-00322-V14-RT-001"
  - "Candidate v15 Red-Team finding INIT-00322-V15-RT-001"
reflected_to:
  - "Candidate v15"
  - "Candidate v16"
  - "requirement.md"
  - "design.md"
  - "plan.md"
  - "Epic 1 Requirement／Design／Plan／Issue Boundary Map"
  - "Epic 2 execution pre-start contract"
  - "Epic 2 Issue Boundary Map"
---

# Scope Specific Planning Adoption Gate Before Execution Ready

## 位置づけ

Universal Planning Candidateは、Review PASS、Scope Human Gate、canonical adoption／parityを別のauthority boundaryとして定義する。Candidate v12ではIssue Planningの局所Acceptanceが`Review PASS → execution-ready`と読め、Human Gateとcanonical adoptionを正の条件として固定できていなかった。

## ADR 化基準

- hard to reverse: yes。Issue execution開始条件とHuman authorityを決める。
- surprising without context: yes。Review PASSだけではIssue実装を開始できない。
- real tradeoff: yes。Human Gateの追加固定費と、誤ったPlanからの実装開始防止を交換する。

## 結論（Decision）

1. Planning Review PASSはHuman decisionの入力であり、`execution-ready`を直接成立させない。
2. Initiative、Epic、Issueの各Scopeにpositive Human Gateを置く。
3. Issue Scopeでは`Human Issue Plan Adoption and Implementation-Start Authorization`を必須とする。
4. archive-candidate pathは、fresh Review PASS、Humanによるexact logical filename／ZIP SHA承認、deterministic canonical adoption、candidate-to-canonical parity、required validation／planning publication後にだけ`execution-ready`となる。
5. git-bound pathは、fresh Review PASS on exact reviewed HEAD／exact target paths、Humanによるそのexact HEAD／path set承認、exact reviewed-content canonical／commit parity、required validation／planning publication後にだけ`execution-ready`となる。
6. archiveまたはGit Review PASSだけでExecutorを開始するfixtureを明示的に拒否する。
7. Human rejection、source drift、parity failure、adoption中のsemantic mutationはPlanningへ戻す。
8. Human Gate判断はSkill／Human、決定的adoptionとstate transitionはMain、検証はRuntime／wrapperが所有する。
9. archive-candidateとgit-boundはReview transportだけが異なる。archiveは`Review PASS`、exact logical filename／ZIP SHAへbindされたHuman authorization、canonical adoption、candidate-to-canonical parity、required validation／planning publicationの論理積を必要とする。git-boundは`Review PASS`、exact reviewed HEAD／exact target pathsへbindされたHuman authorization、exact reviewed-content canonical／commit parity、required validation／planning publicationの論理積を必要とする。git-bound Review PASSを独立したpre-start alternativeとして扱わない。
10. Planning Adoption negative fixturesをclosed ID set `PA-NF-01`〜`PA-NF-10`として固定する: `PA-NF-01` archive Review PASS only、`PA-NF-02` git-bound Review PASS only、`PA-NF-03` Human Gate only、`PA-NF-04` parity only、`PA-NF-05` wrong logical Candidate filename／Candidate SHA、`PA-NF-06` wrong reviewed HEAD／exact target paths、`PA-NF-07` source drift、`PA-NF-08` semantic mutation during adoption、`PA-NF-09` parity failure、`PA-NF-10` validation／planning-publication failure。
11. PLANNING-ADOPTION-GATE、Human Review、Materialization evidence、All-Issue Map、Initiative／Epic local Requirement／Design／Plan／Issue handoffは、10 IDと意味を省略せずlocal normative acceptance contractとして持つ。中央参照またはgeneric `negative fixtures`だけでは適合しない。

## 背景（Context）

Issue Planningは各Issue開始時にJITで行うが、Reviewと実装開始は同じauthorityではない。Reviewは仕様品質を評価し、HumanはそのPlanを採用して実装へ進むかを決める。Candidate v12のEpic 2はadopted canonical Issue Planを要求していたが、Epic 1のE1-I1 success pathがReview PASSから直接`execution-ready`へ進めたため、producerとconsumerの契約が不一致だった。Candidate v13では上位契約を修正したものの、Epic 2 Issue Boundary Mapの`またはfresh Git-bound Planning Review PASS`という局所handoffが同じ抜け道を再導入したため、両transportを同じ正のauthority chainへ固定する。

## 選択肢（Options considered）

### Review PASSをIssue execution authorityとする

却下。Human authorityとcanonical parityを飛ばす。

### Human GateをInitiative／Epicだけに限定する

却下。Issue Planの具体的実装契約をHumanが採用する正の境界がなくなる。

### Scope-specific positive Human Gate

採用。ScopeごとにApproval内容を最小化しつつ、Review、adoption、execution authorityを分離できる。

## 判断理由（Rationale）

- ReviewerとHumanのauthorityを混同しない。
- archive／Gitの両transportで同じ意味契約を保てる。
- Candidate-to-canonical parityを実装開始条件として強制できる。
- Epic 1 producerとEpic 2 consumerの契約が一致する。

## 影響（Consequences）

### Positive

- Review PASSだけの誤ったExecutor開始を防ぐ。
- Issue Plan採用Evidenceが監査可能になる。
- source driftやadoption差分をfail closedで扱える。

### Negative

- Issue PlanningごとにHumanの明示decisionが必要になる。
- archive／Git modeそれぞれにapproval identity記録が必要になる。

### Follow-up

- Planning SkillsへScope Gate selectorを実装する。
- E1-I1にarchive／Gitのnegative fixturesを追加し、validation／planning-publication failureとwrong target-path authorizationを必ず拒否する。
- E2-I1はpositive gate／parity EvidenceなしのExecutor開始を拒否する。
- E1-I1 producerとE2-I1 consumerの双方で`PA-NF-01`〜`PA-NF-10`を各10／10 PASS、合計20／20、violations 0として証明する。
