---
種別: 計画書（Epic）
ID: "epic-00331"
タイトル: "ChatGPT Planning and Advisory Review"
関連GitHub: ["chemitaro/spec-dock#331"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-23"
依存: ["requirement.md", "design.md"]
親: ["init-00322"]
candidate_semantic_key: "planning-and-advisory-review"
canonical_path: "spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/plan.md"
---

# epic-00331 ChatGPT Planning and Advisory Review — 計画（Issue と実施順序）

## 1. Epic Outcome

Epic完了後、Main／HumanはIssue Planning、Initiative／Epic Portfolio Planning、Planning Review、Targeted Review、Human-approved Node materializationをvNextだけで完了できる。

## 2. Issue Boundary Map

### E1-I1 — Implement ChatGPT Issue Planning Workflow

- Actor: SpecDock Maintainer／Main。
- Merge後Outcome: SpecDockに、既存Issue NodeまたはSeedからIssueのRequirement／Design／PlanをJIT生成・セルフレビュー・配置し、archive modeではfresh Planning Review PASS、exact logical Candidate filename／ZIP SHAへbindされたpositive Human Issue Plan Adoption Gate、deterministic canonical adoption、candidate-to-canonical parity、required validation／planning publicationを、git-bound modeではfresh Planning Review PASS on exact reviewed HEAD／exact target paths、同identityへbindされたpositive Human Gate、exact reviewed-content canonical／commit parity、required validation／planning publicationを完了した後にだけexecution-readyへ昇格できる再利用可能Workflowが実装される。
- End-to-end責務: minimal adapter、target binding、Git preflight、Oracle、Prompt、Issue Candidate package、archive-candidate Review default、git-bound fallback、Semantic／Mechanical Revision routing、file retrieval、content-preserving placement、Planning Review integration、tests、docs、provider／installed／dogfood projection。
- Non-goals（mandatory four-item matrix）:
  - Current Portfolio replanning: 現在のHuman-approved Initiative／Epic Portfolioを再設計・再分割しない。
  - Downstream Issue pre-authoring: 後続IssueのRequirement／Design／Planを先行作成せず、他IssueのPlanningをこのIssueの成果物として代行しない。
  - Human approval bypass: Human Portfolio Approval、Issue-local Human gate、merge判断を自動化・代行・迂回しない。
  - Planning-only completion: Planning文書またはPlanning runだけを成果物として完了せず、Workflow implementation、tests、docs、projectionまで完了する。
- Separate PR理由: merge直後から各Issueが自分自身をJIT Planningできる公開Workflow capabilityとなり、後続Portfolio Planning Workflowのcurrent consumerになる。
- Dependency: なし。
- Acceptance evidence:
  - Planning command／Skill／wrapper、Issue Candidate template、archive／Git mode selector、Semantic／Mechanical lane selector、Prompt resources、placement、Review integration、tests、docs、projectionの実装差分。
  - representative IssueでPlanning create→complete三文書→mode-specific fresh Planning Review PASS→exact identityへbindされたHuman Issue Plan Adoption Gate→archive canonical adoption＋candidate-to-canonical parityまたはgit-bound exact reviewed-content canonical／commit parity→required validation／planning publication→execution-ready handoffを完走したsubordinate dogfood E2E report。
  - exact repository／branch／HEAD preflight、output placement、no-hidden-Git、provider／installed／dogfood parityのautomated test結果。
  - 生成三文書のhash、Oracle session reference、Formal Review Markdown。
  - sensitive-data fixtureがPrompt／Relay／Workbench／Artifactへ残らないpreflight／redaction testと、direct-argv／shell-injection negative test、各shell exceptionのrollback mechanism／trigger／tested rollback evidence。
  - planned／unplanned Human intervention、handoff byte／文字数、Agent／Skill invocation、Review result、wall-clockをrun単位で記録したevaluation evidence。
  - current Portfolio／downstream Issue specsへunauthorized mutationが0であるnegative test。
  - `PA-NF-01` archive Review PASS only、`PA-NF-02` git-bound Review PASS only、`PA-NF-03` Human Gate only、`PA-NF-04` parity only、`PA-NF-05` wrong logical Candidate filename／Candidate SHA、`PA-NF-06` wrong reviewed HEAD／exact target paths、`PA-NF-07` source drift、`PA-NF-08` semantic mutation during adoption、`PA-NF-09` parity failure、`PA-NF-10` validation／planning-publication failureを相互に独立した必須negative fixtureとして拒否し、どれか1件でも該当する場合は`execution-ready`／Executor startを禁止する。 E1-I1 producer acceptanceは10／10 PASS、violations 0。
- Milestoneではない理由: Human／Mainがmerge直後に利用できる独立したSpecDock製品能力であり、単なるPlanning活動や内部実装gateではない。

### E1-I2 — Implement Initiative Epic Portfolio Planning Workflow

- Actor: SpecDock Maintainer／Main／Human。
- Merge後Outcome: SpecDockに、Human GoalからThin Initiative Bundle、全Epic Bundles、Issue Boundary Maps、Candidate ZIP、Review、Human Approval、旧Portfolio retirement、新Node materializationまでを一貫してオーケストレーションできる再利用可能Portfolio Planning Workflowが実装される。
- End-to-end責務: Initiative orchestration、Epic Planning reuse、Initiative／Epic Candidate templates、Slicing Contract、decomposition Review、archive／Git Review selection、Semantic／Mechanical revision policy、safe extraction、approval、legacy evidence preservation、reverse-topological retirement、materialization、parity。
- Non-goals（mandatory four-item matrix）:
  - Current Portfolio replanning: 本Issue自身が現在のHuman-approved Candidate Portfolioを再設計・再分割しない。
  - Downstream Issue pre-authoring: materialize後の各IssueのJIT Requirement／Design／Planを先行作成しない。
  - Human approval bypass: Human Portfolio Approval、Issue-slice approval、merge判断を自動化・代行・迂回しない。
  - Planning-only completion: Candidate ZIP、Planning Bundle、Review結果だけを成果物として完了せず、Portfolio Planning Workflow implementation、tests、docs、materialization safeguardsまで完了する。
- Separate PR理由: Issue Planning capabilityとは異なるPortfolio／Human Gate／destructive migration／Node orchestration capabilityを独立して受入・rollbackできる。
- Dependency: E1-I1。
- Acceptance evidence:
  - Portfolio Planning command／Skill／Prompt／Initiative／Epic Candidate packaging／dual Review transport／dual Revision lane／Review orchestration／materialization implementation差分。
  - Initiative Bundle、全Epic Bundles、Issue Boundary Maps、ADR、MANIFEST／CHECKSUMSを含むCandidate ZIPと外部ZIP SHA。
  - fresh `decomposition-quality` Review PASSとHumanによるexact ZIP SHA承認記録。
  - observed 17-edge graph fixtureに対するactive preflight、checked `deps remove`、`delete --recursive --yes`、edge restore／resume recovery、old-node／edge absence、validate／sync PASS。
  - supported Runtime outcome fixtureでremote-only／partial local／cleanup failure／post-sync failureを再現し、semantic-key ledger、`--github-issue` link-existing、valid Node no-rerun、bounded cleanup、exact 9 dependency、partial Bundle placement resume、candidate-to-canonical parity、validate／sync PASS。
  - Candidate revisionがversion N→N+1で新filename／MANIFEST／SHAとなり、旧versionが不変であるversioning test。
  - exact source Runtime pure validatorで全10 Node title／slug／parentがPASSし、invalid fixtureがC0 no-mutationで停止するEvidence。
  - exact source Epic templatesからのRuntime scaffold render parity、9 bound canonical Epic docs、partial resume、verified scaffold rollback。
  - exact source Artifact parser／duplicate scanner、全Artifact canonical／package-only disposition、filename-derived ID／type parity。
  - pre-commit report dispositionとGit／remote-ref publication evidenceの分離、report second mutation 0。
  - current approved Portfolioを入力fixtureとして使用しても、Human feedbackなしにEpic／Issue境界が変更されないtest。
- Milestoneではない理由: Initiative／Epic Planning capability、Human approval boundary、old-to-new Portfolio materializationという独立Actor Outcomeを持つ。

### E1-I3 — Implement Targeted Review and Planning Surface Cutover

- Actor: SpecDock Maintainer／Human／Main。
- Merge後Outcome: SpecDockに任意対象のadvisory Targeted Review capabilityが実装され、Planning／Reviewのofficial routeがvNextへ安全に切り替わる。
- End-to-end責務: Targeted Review Skill、archive-candidate／git-bound Review request normalization、Prompt／result、planning-specific legacy authoring／manual Planning／local planning reviewer removal、parity、representative use validation。
- Non-goals（mandatory four-item matrix）:
  - Current Portfolio replanning: Targeted Review結果だけで現在のHuman-approved Portfolioを再設計・再分割・自動変更しない。
  - Downstream Issue pre-authoring: 後続IssueのRequirement／Design／Planを先行作成しない。
  - Human approval bypass: Targeted ReviewでFormal Gate、Human approval、merge判断を代行・迂回せず、repository mutationを行わない。
  - Planning-only completion: advisory MarkdownまたはPlanning／Review結果だけを成果物として完了せず、Targeted Review capability、tests、docs、planning-specific cutoverまで実装する。
- Additional Non-goal:
  - planning-specific surface以外のglobal cutoverを所有しない。
- Separate PR理由: advisory Review capabilityとplanning-specific official route activation／rollback boundaryを持つ。
- Dependency: E1-I1、E1-I2。
- Acceptance evidence:
  - Targeted Review implementation差分、dual Review request normalization、指定target／Perspectiveへadvisory Markdownを返しFormal Gate／repository mutationを発生させないE2E。
  - vNext Planning／Review official routeのprovider／installed／dogfood smoke。
  - `spec-dock-chatgpt-authoring`、manual Planning Skills、local planning reviewer等のplanning-specific legacy surface不在を示すrepository search。
- Milestoneではない理由: merge後に利用者とmaintainer双方へ独立価値があり、Epic 3のglobal cutoverとはmutation ownershipが重複しない。

## 3. Dependency

```text
E1-I1 ──> E1-I2 ──> E1-I3
   └────────────────> E1-I3
```

## 4. Per-Issue Delivery

各Issueは1 branch／1 PR／CI／required Review／Human merge／finish。Issue内で必要なtests、docs、provider／installed／dogfoodを完了する。

## 5. Epic Delivery Review

全3 Issueがdefault branchへmerge後、次を検証する。

- Issue／Epic／Initiative PlanningのE2E。
- Initiative／Epic／Issue Candidate generation、archive／Git Review mode、Semantic／Mechanical Revision lane、Human Approval／deterministic adoption／materialization。
- Targeted Review advisory behavior。
- decomposition-quality over／under slicing fixtures。
- planning-specific legacy route不在。
- parity。

P0／P1でmutationが必要な場合だけJIT bounded Issueを作る。aggregate Epic PRは作らない。
