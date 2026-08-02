---
種別: 設計書（Epic）
ID: "epic-00332"
タイトル: "Analysis Guided Issue Execution and Per Issue Delivery"
関連GitHub: ["chemitaro/spec-dock#332"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-23"
依存: ["requirement.md"]
親: ["init-00322"]
candidate_semantic_key: "issue-execution-and-per-issue-delivery"
canonical_path: "spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00332-issue-execution-and-per-issue-delivery/design.md"
---

# epic-00332 Analysis Guided Issue Execution and Per Issue Delivery — 設計（どう実現するか）

## 1. Single Vertical Actor Journey

```text
archive: fresh Planning Review PASS on exact logical Candidate filename／ZIP SHA
→ Human Issue Plan Adoption and Implementation-Start Authorization bound to exact logical Candidate filename／ZIP SHA
→ deterministic canonical adoption
→ candidate-to-canonical parity
→ required validation／planning publication

or

git-bound: fresh Planning Review PASS on exact reviewed HEAD／exact target paths
→ Human Issue Plan Adoption and Implementation-Start Authorization bound to exact reviewed HEAD／exact target paths
→ exact reviewed-content canonical／commit parity
→ required validation／planning publication
→ select Execution Unit
→ Architecture-Aware Execution Brief
→ custom Executor implementation
→ Checkpoint Review
→ P0/P1 Repair Batch when needed
→ next Unit or Final Completion Summary
→ Issue Delivery Review
→ dedicated Issue PR
→ CI / ChatGPT Delivery Review / GitHub Codex Review
→ blocking repair and fresh re-observation
→ merge-prepared
→ Human merge
→ reviewed HEAD verification
→ issue finish
```

`delivery-ready`を別Issue境界にせず、一つのvertical implementation Issue内部のMilestone／formal gateとして扱う。

## 2. Agent Topology

Closed role set:

```text
write-capable:
- executor

read-only:
- explorer        # Codex built-in; no override file
- researcher
- consultant
- deep-consultant
```

Authority／projection:

```text
provider:  src/spec_dock/assets/install_root/.codex/agents/
installed: <install-root>/.codex/agents/
dogfood:   .codex/agents/
```

Custom file setは`executor.toml`、`researcher.toml`、`consultant.toml`、`deep-consultant.toml`だけである。built-in `explorer`にはoverride fileを置かない。allowlist外の`dev-coder`、`code-reviewer`、`spec-reviewer`、`qa-reviewer`、`doc-writer`、`repo-analyst`、`spark-worker`、`utility-worker`、`spec-manager`、`system-architect`その他named roleをmaintained official pathから除去する。exact-set／permission／projection parity testを必須とする。

Main／ExecutorのmodelとreasoningはSpecDockが固定しない。Issue Gradeによる自動routingを行わず、Mainが必要時だけ明示overrideする。

## 3. Planning Adoption Boundary

Issue execution starts only after the complete mode-specific chain. Archive mode requires fresh Planning Review PASS, positive Human authorization bound to exact logical Candidate filename／ZIP SHA, deterministic canonical adoption, candidate-to-canonical parity, and required validation／planning publication. Git-bound mode requires fresh Planning Review PASS on exact reviewed HEAD／exact target paths, positive Human authorization bound to that exact HEAD／path set, exact reviewed-content canonical／commit parity, and required validation／planning publication. Review PASS alone, Human Gate alone, parity alone, wrong identity, source drift, semantic adoption mutation, or validation／publication failure does not authorize execution. Semantic planning changes return to a new Issue Candidate; closed mechanical corrections may use local edit＋commit／push＋Git-bound Review.

## Closed Planning Adoption consumer negative-fixture matrix

E2-I1 is the consumer pre-start authority. Its local Design explicitly rejects every fixture below before Executor start.

| ID | Required rejected condition | Expected result |
|---|---|---|
| `PA-NF-01` | archive Review PASSだけで`execution-ready`／Executor startを要求する | reject |
| `PA-NF-02` | git-bound Review PASSだけで`execution-ready`／Executor startを要求する | reject |
| `PA-NF-03` | Human Gateだけで`execution-ready`／Executor startを要求する | reject |
| `PA-NF-04` | parityだけで`execution-ready`／Executor startを要求する | reject |
| `PA-NF-05` | wrong logical Candidate filenameまたはwrong Candidate SHAでadoption／startを要求する | reject |
| `PA-NF-06` | wrong reviewed HEADまたはwrong exact target pathsでadoption／startを要求する | reject |
| `PA-NF-07` | source drift後にreview identityを再確立せずadoption／startを要求する | reject |
| `PA-NF-08` | adoption中にsemantic mutationが発生した内容からstartを要求する | reject |
| `PA-NF-09` | parity failure後に`execution-ready`／Executor startを要求する | reject |
| `PA-NF-10` | validationまたはplanning-publication failure後に`execution-ready`／Executor startを要求する | reject |

Both E1-I1 producer and E2-I1 consumer acceptance must prove every row independently; central-reference-only or generic `negative fixtures` wording is non-conforming.

## 4. Architecture-Aware Execution Brief

Codex／wrapperはdeterministic anchorだけを提示する。ChatGPTがexact HEADから関連Artifactとrepository evidenceを横断し、適用Concernを動的選択する。Brief candidateはWorkbench、`ready`採用後はIssue Artifactとしてfreezeする。

## 5. Checkpoint and Repair

Checkpoint ReviewはPlan上の明示semantic BASEからcurrent synchronized HEADへのDelta-bounded Snapshot Review。BASE ancestryをfail closedで検証し、mutation frontierとIssue Contract全体を評価する。P0／P1でmutationが必要な場合だけRepair Batchを作り、same Executorへ戻す。material Planning changeはIssue Planningへ戻す。

## 6. Issue Delivery and PR

Checkpoint／Issue Delivery／PR-style ReviewはすべてGit-boundであり、Planning Candidate ZIPを代替Evidenceにしない。Issue Delivery ReviewはIssue実装開始の明示semantic BASEからcurrent HEADまでを対象に、mutation frontierとIssue Contract OwnerのRequirement／Design／Plan／implementation／tests／Final Completion Summary全体を評価する。PASS後、Mainがdedicated PRを作成する。PR-style Reviewはtarget base branchとPR HEADのmerge-baseからPR HEADまでを評価し、CI／ChatGPT Review／GitHub Codex Reviewを観測する。BASE／merge-base／ancestryを解決できなければ`insufficient-evidence`で停止する。PR修復も同一Issue Actor Journeyの内部で行う。

## 7. Git、Human Gate、Sensitive Data、Process Invocation

ExecutorとChatGPTはGit transactionを行わない。Mainがdiff／verificationを確認してcommit／push／PRを行う。Humanだけがmergeする。Issue finishはmerged HEADとreviewed HEAD一致後だけ。

Execution Brief、Repair Batch、Executor Handoff、Operator Context、GitHub外file、Workbench、Artifact、report evidenceへsecret、token、cookie、credential、private key、`.env`、production dump、private customer dataを含めない。必要情報はHuman-approved redacted subsetへ限定する。

Executor、adapter、test helper、PR observer等のprocess launchはdirect argvをdefaultとする。通常経路でshell wrapper、pipe、redirect、heredoc、command substitution、Prompt／path interpolationを使用しない。shell例外はHuman-approved Design、固定command template、untrusted input拒否／encoding、injection regression test、明示的rollback mechanism／trigger、tested rollback evidenceをすべて必要とする。欠落時はCheckpoint／Issue Delivery／PR gateをPASSしない。

## 8. Internal Milestones

このEpicの唯一のIssue Seedは、JIT Issue Planningで少なくとも次のMilestoneへ分けられる。

1. Brief／Executor implementation candidate。
2. Checkpoint／Repair／Issue Delivery readiness。
3. PR external gates／Human merge／finish。

これらは同じIssueの内部Milestoneであり、別Issue／別PRにしない。
