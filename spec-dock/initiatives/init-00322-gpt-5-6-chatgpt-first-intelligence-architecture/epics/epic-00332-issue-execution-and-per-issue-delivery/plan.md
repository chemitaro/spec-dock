---
種別: 計画書（Epic）
ID: "epic-00332"
タイトル: "Analysis Guided Issue Execution and Per Issue Delivery"
関連GitHub: ["chemitaro/spec-dock#332"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-23"
依存: ["requirement.md", "design.md"]
親: ["init-00322"]
candidate_semantic_key: "issue-execution-and-per-issue-delivery"
canonical_path: "spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00332-issue-execution-and-per-issue-delivery/plan.md"
---

# epic-00332 Analysis Guided Issue Execution and Per Issue Delivery — 計画（Issue と実施順序）

## 1. Epic Outcome

承認済みIssue Planから実装、formal gates、dedicated PR、Human merge、Issue finishまでを、一つのvertical Issueで完了できる。

## 2. Issue Boundary Map

### E2-I1 — Analysis Guided Issue Execution and Per Issue Delivery

- Actor: Main／Executor／Human。
- Pre-start gate: archive modeはfresh Planning Review PASS＋exact logical Candidate filename／ZIP SHAへbindされたpositive Human Issue Plan Adoption Gate＋deterministic canonical adoption＋candidate-to-canonical parity＋required validation／planning publicationを、git-bound modeはfresh Planning Review PASS on exact reviewed HEAD／exact target paths＋同identityへbindされたpositive Human Gate＋exact reviewed-content canonical／commit parity＋required validation／planning publicationをすべて満たす。Review PASSのみ、Human Gateのみ、parityのみ、wrong identity、source drift、semantic adoption mutation、validation／publication failureではExecutorを開始しない。
- Closed negative-fixture acceptance: `PA-NF-01` archive Review PASS only、`PA-NF-02` git-bound Review PASS only、`PA-NF-03` Human Gate only、`PA-NF-04` parity only、`PA-NF-05` wrong logical Candidate filename／Candidate SHA、`PA-NF-06` wrong reviewed HEAD／exact target paths、`PA-NF-07` source drift、`PA-NF-08` semantic mutation during adoption、`PA-NF-09` parity failure、`PA-NF-10` validation／planning-publication failureを相互に独立した必須negative fixtureとして拒否し、どれか1件でも該当する場合は`execution-ready`／Executor startを禁止する。 E2-I1 consumer acceptanceは10／10 PASS、violations 0。
- Merge後Outcome: 承認済みIssue PlanからArchitecture-Aware Execution Brief、bounded implementation、Checkpoint／Repair、Issue Delivery Review、専用PR、external gates、Human merge、reviewed HEAD確認、Issue finishまで完走できる。
- End-to-end責務: Brief prompt／retrieval／lifecycle、single custom Executor、limited read-only specialists、Checkpoint、Repair Batch、Final Completion Summary、Issue Delivery Review、PR create／observe、CI、ChatGPT Review、Codex Review、blocking repair、merge-prepared、Human merge、finish、tests／docs／projection。
- Separate PR理由: 一つのIssue Outcomeを実装からrepository publication／Node completionまで追跡し、途中のdelivery-ready handoffによる追加PR／context再構築を避けるため。
- Dependency: Epic 1完了。
- Acceptance evidence:
  - representative IssueでPlan→Architecture-Aware Execution Brief→custom Executor→semantic-BASE Checkpoint／Repair→semantic-BASE Issue Delivery Review→dedicated PR→merge-base PR Review／CI／GitHub Codex Review→Human merge→reviewed HEAD確認→issue finishを完走したE2E report。
  - exact agent-set testがprovider／installed／dogfoodでwrite=`executor`、read-only=`explorer`,`researcher`,`consultant`,`deep-consultant`、built-in explorer overrideなし、missing／extra／renamed／write権限誤り／Grade routing拒否を証明する。
  - Executor／adapterのhidden commit／push／stash／force／mergeが0であるGit／Workflow audit。
  - Brief／Repair／Handoff／Artifact／reportへのsensitive-data exposure 0、direct-argv process spawn、shell-injection negative fixture PASS、各shell exceptionのrollback mechanism／trigger／tested rollback evidence。
  - Brief finding、first Checkpoint result、failure cycle／手戻り、tool call／探索／handoff proxy、Human intervention、wall-clockのrun-level evidence。
- Milestoneではない理由: Issue実装とpublication／finishを含む一つの利用可能なvertical Actor Journeyであり、内部のformal gatesはMilestoneとして管理できる。

## 3. Dependency

```text
Epic 1 completion → E2-I1
```

## 4. Internal Milestones（JIT Issue Planningで具体化）

1. Brief生成／採用とcustom Executor implementation candidate。
2. Checkpoint／Repair loop、Final Completion Summary、Issue Delivery Review。
3. dedicated PR、external gates、blocking repair、Human merge、reviewed HEAD確認、finish。

Milestoneは同じIssue／branch／PRの内部単位であり、別Issueへ分割しない。

## 5. Per-Issue Delivery

E2-I1は1 dedicated branch／1 PR／CI／required Review／Human merge／finish。必要なcode、tests、docs、configuration、projection、Representative Real-Use Validationを同じIssueへ含める。

## 6. Epic Delivery Review

E2-I1 merge後、別のrepresentative Issueを同じWorkflowで完走し、Agent topology、Git ownership、Brief、Checkpoint、Repair、P2／P3 no-mutation、PR／merge／finish、parityをEpic Contractとして検証する。
