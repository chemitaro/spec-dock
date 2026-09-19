---
種別: 実装計画書（Issue）
ID: "iss-00396"
タイトル: "Build Once Provider Gate and Regression Policy Cutover"
関連GitHub: ["#396"]
状態: "approved"
詳細化状態: "scope-simplified; product-implementation-gated"
最終更新: "2026-09-19"
依存:
  - "requirement.md"
  - "design.md"
  - "iss-00395"
  - "../../plan.md"
  - "../../artifacts/rolling-wave-issue-elaboration-contract.md"
親: ["epic-00384", "init-local-00003"]
Planning Level: "implementation-ready"
実装開始許可: false
owner_decisions_required: []
external_prerequisites:
  - "#395 PR #403 is human-merged and corrected-tip B1/B2 are accepted; keep GitHub Issue #395 OPEN and read it as a read-only predecessor."
  - "P02 runner capability and retention horizon must be proven before product/workflow implementation."
human_merge_only: true
repository_evidence:
  role: "authoring-source-provenance"
  repository: "chemitaro/spec-dock"
  branch: "iss-00396-build-once-provider-gate-and-regression-policy-cutover"
  sha: "4d68bce3f3ee977548a3c467476da39c15f43594"
  tree: "80ade10f57cd5f4140daa03ca8a40b844f1fcc53"
current_spec_freeze: "resolve after this revision is reviewed, projected, committed, and pushed"
qualification_authority: "E384-QUAL-001"
---

# iss-00396 Build Once Provider Gate and Regression Policy Cutover — 実装計画

このPlanは、Epic #384のaccepted qualification contractを保持したまま、Issue #396の実装表現と作業手順を最小化する。#395を再実装・再open・closeせず、PR #403のcorrected merge `3c69af78843b04a13bde2f93eb3b1eb4081cdb33` と同一corrected tip上のB1/B2をread-only predecessor evidenceとして使う。

## 1. Goal, non-goal and fixed parent contract

### Goal

一つのcandidateを一度だけbuildし、同じwheel/sdist actual bytesを全roleへ渡し、Linux canonical、sdist smoke、macOS delta、static analysis、candidate-bound fault campaign、chronological historyを一つのfinal provider gateへ集約する。consumer-zeroとrequired-contextのno-gap cutoverを確認した後、旧ledger/timing/sharder/policy machineryを撤去する。

### Non-goal

- #395のProduct修正、register、Issue stateの変更。
- Epic Requirement、E384-QUAL-001、#392 lifecycle/wire、retained installed-consumer workflow、GitHub settingsをIssue側で変更すること。
- 新しい恒久runner probe、background service、追加approval gate、別Issue、別のqualification thresholdを作ること。
- first five、latest twenty、100% fault detection、zero skip/retry/approved failure、Linux x86_64 standard/general-purpose、effective <=2 vCPU / <=8 GiB、single pytest root/no shard、independent wall/CPU predicatesを弱めること。

### 固定する親契約

E384-QUAL-001が定めるcandidate binding、environment fingerprint、process topology、first-five population、latest-twenty window、per-run wall/CPU conjunction、correctness zero、fault detection 100%、failure/cancel/missingの非選別、no retry/rerun/shardを唯一のquantitative authorityとする。Issueは値を再定義せず、generated projectionまたは機械評価で参照する。

## 2. Admission and current stop

Product/test/workflow/policy mutationは、次のS0を完了するまで行わない。

1. local branch、configured upstream、GitHub branch tipが同一full SHAでcleanであることを確認する。
2. #395 PR #403のcorrected merge identity、B1、B2、ancestor proofをread-onlyでEvidenceIndexへ記録する。#395はOPENのまま保持する。
3. このscope-simplified R/D/Pのsame-Red Strict reviewを新しいclean freeze SHAで通し、P0/P1=0を確認する。旧review receiptは再利用しない。
4. GitHub Issue #396 projectionをreadbackしてR/D/Pのcurrent candidateと一致させる。
5. explicit implementation dispatch、同時writer不在、SpecDock validationを確認する。

P02はS0後の一回限りのexternal preflightである。現時点の停止理由は次の二つであり、推測で埋めない。

- 現行provider-ci.ymlとprovider-full-regression.ymlには、effective cpu.max、memory.max、cgroup membershipを測る既存diagnostic channelがない。ownerが既存raw capability recordを提供するか、owner指定の一回限りの外部channelでephemeral measurementを行う。後者を実施する場合だけ、P02のread-only境界を一文明確化する。
- Actions retentionはD=90、M=90をread-onlyで取得済みだが、artifact uploadからcampaign/window/rollback/audit完了までのbounded horizon Hが未確定である。H <= chosen retention <= Mを証明するまで停止する。

P02のcaptureはtracked file、GitHub settings、durable external state、恒久workflow、Product codeを変更しない。P02証拠はqualification attemptではない。

## 3. Simplified change inventory

### Current canonical inputs

- parent-generated qualification projection
- role baseline JSONとordered role delta JSON
- candidate-bound seeded fault catalogue
- old-policy retirement signatures
- persisted Candidate / Attempt / Qualification / Cutover / Stop recordsと共通 EvidenceIndex
- retained workflowとprotected-data read-only evidence

旧role-ownership-checkpoints、resolved-final、68-code一覧、authoring status、HTML、ZIP、P1/P2 receiptは歴史・比較用に保持できるが、current runtime input・追加schema authority・追加gateにしない。Final manifest、consumer scan、required-context receipt、protected comparisonは実行時またはone-shot evidenceとして生成する。

### Responsibility boundaries

実装者は次の責務を循環なく最小のmoduleへ統合できる。表の責務数、file name、path、test-node countは受入値ではない。

| Responsibility | Required observable behavior |
|---|---|
| candidate/materialization | source/tree、manifest、wheel/sdist actual bytes、one build、poisoned same-SHAを記録 |
| environment/process | effective limits、fingerprint、one pytest root、descendant-inclusive CPU、reapを記録 |
| ownership/plugin | baseline+deltaから全collectionを決定的に導出し、body前にunknown/duplicate/mismatchをreject |
| attempt/history/evaluator | append-only started outcomes、first-five/latest-twenty、parent predicates、no filtering |
| fault/cutover | candidate-bound catalogue 100%、old consumer zero、retained workflow equality |
| evidence/CLI | binding-scoped actual-byte evidence、thin command dispatch、truthful StopReturn |
| one-shot external checks | human-only context/settings/merge and protected-data readbackを保存。恒久serviceを作らない |

## 4. Phased execution

| Phase | Purpose | Entry | Exit |
|---|---|---|---|
| S0 | specification/admission | current clean branch、#395 read-only predecessor | new Strict pass、projection readback、dispatch |
| S1 | external preflight | S0 pass | runner capability、retention H、required-context facts、protected baseline |
| S2 | replacement implementation | S1 pass | RED→GREENのcandidate/materialization、environment/process、plugin、history/fault、packaging |
| S3 | shadow and human cutover | S2 pass | one candidate shadow、new context RED/GREEN、consumer migration |
| S4 | retirement and final local verification | S3 pass | consumer zero、old deletion、retained/protected/no-touch checks、ordinary suite/lint |
| S5 | review, merge and B3 | S4 pass and clean pushed source | Code Review Strict、Final Quality Gate Pro、human merge、post-merge B3 evidence |

### S0 — Specification and admission

R/D/PとIssue-local current inputsを同期し、historical artifactsをcurrent authorityから外す。Pack/HTMLを更新する場合もpresentation artifactをacceptance authorityへ戻さない。新freeze SHA/treeでspec-review Strictを一度行い、projection readbackを取得する。S0ではProduct/test/workflow/policy fileを変更しない。

### S1 — External preflight

Read-onlyで次を取得する。

- runner provider/class、x86_64、OS/image、CPU family、effective quota、memory limit、filesystem、tool versions、cgroup/collector version
- retention days D、maximum M、operatorがboundしたhorizon H
- effective required contexts、ruleset scope、merge queue/merge_group state、check-run names
- protected roots and retained workflow baseline

Runner capabilityの新規測定は、owner指定のone-time external channelとephemeral cleanupに限る。新workflow、CLI、schema、daemonを追加しない。S1が未完ならS2へ進まない。

### S2 — Replacement implementation

小さなvertical sliceで次の順に実装する。

1. parent projectionとpersisted records/evidence codec。内部helperはschemaへ複製しない。
2. one-time candidate materialization、manifest、actual bytes、same-SHA poison、retention refusal。
3. environment/process collector。parentのeffective limitとsingle-root/no-shardを証明する。
4. permanent pytest plugin。baseline+deltaから全collectionを導出し、role filterをbody前に適用する。root conftestはtemporary seamに留め、後で旧hookと一緒に除去する。
5. append-only attempt history/evaluator。started failure/cancel/missingを保持し、result filter、retry、rerun、campaign resetを拒否する。
6. candidate-bound fault executionとone-shot old-consumer scan。catalogue count/code番号を別のauthorityへ複写しない。
7. stored candidateを読むshadow roles、sdist parity、macOS delta、static analysis、thin workflow/CLI。

各sliceはfocused RED→GREEN、狭いテスト、diff checkを通し、coherent checkpoint commitを作る。Product implementation開始後もEpic parent valuesを変更しない。

### S3 — Shadow and human cutover

Shadowでmaterialization producerが一度だけ動き、全roleが同一manifest/wheel/sdist bytesを使うことを確認する。新check/context名は実出力からread-onlyで取得する。Humanだけがold+new required contextを追加し、intentional REDがblockすること、GREEN recovery、merge_group scope、Uの不変をreadbackする。全consumerをreplacementへ移し、old emitterを維持したままconsumer-zeroを証明する。

### S4 — Retirement and final local verification

Consumer-zero、retained installed-consumer workflowの存在/byte equality、protected rootsのno-touch、plugin sole filter ownerを確認してから、old provider/data/workflow/tests/temp seamを同一Issue PRで削除する。One-shot scanner/context/snapshot helperは削除可能なtest/evidence helperとして扱う。ordinary suite、focused provider-gate tests、lifecycle/distribution non-regression、lint、SpecDock validationを実行する。

### S5 — Review, merge and B3

Clean pushed exact SHAでCode Review StrictをGPT-5.6 Sol Extra High、Final Quality Gate Strict v2の分析修正をGPT-5.6 Sol Proで実施する。P0/P1=0とpassを確認する。AgentはEpic integration branchへ向けたmerge-ready PRで停止し、人間だけがmergeする。

Human merge後はmerged SHA/treeを新candidateとして一度だけmaterializeし、CampaignFreezeを作る。first-five、fault catalogue 100%、latest-twenty、context final readback、consumer-zero、protected evidenceを親projectionで評価する。B3をtracked future factへ先書きせず、raw/API evidenceを確認した後にreceipt/reportへ反映する。

## 5. Verification matrix

| Surface | Narrow check | Acceptance evidence |
|---|---|---|
| SpecDock/R-D-P | spec-dock validate、markdown/frontmatter、artifact references | clean validation and new freeze |
| Projection | generate policy --check | zero diff |
| Persisted contracts | schema/codec contract tests | unknown/missing/identity mismatch reject |
| Candidate | materialization/actual-byte tests | one build, same bytes, poison/reject |
| Environment/process | collector and descendant tests | fingerprint, limits, reap, no shard |
| Ownership | baseline+delta generated collection tests | exact collection/owner/hash before body |
| History/evaluator | chronological table-driven tests | failure/cancel/missing retained, no filter |
| Fault/cutover | catalogue and one-shot scanner tests | 100% detection, consumer zero, retained equality |
| Local regression | provider-gate tests, lifecycle/distribution tests, ordinary pytest, make lint | pass, no old policy skip |
| External | context/settings/retention/runner readbacks | human boundary and bounded evidence |
| Final | Code Review Strict and Final Quality Gate Strict v2 | pass at same exact SHA |

## 6. Stop conditions and recovery

Stop with truthful StopReturn when any of the following occurs:

- #395 corrected identity/B1/B2/ancestor or current spec projection is missing or mismatched.
- Parent qualification values, population, aggregation, rejection, or escape prohibition would need a change.
- P02 runner capability, retention H, contexts, or protected baseline cannot be proven.
- Candidate producer is not unique, actual bytes/environment/retention are incomplete, or same-SHA rebuild would be needed.
- Ownership generation has unknown/duplicate/unplanned nodes or plugin sole ownership would be lost.
- Started failure/cancel/missing/rerun must be filtered to pass, or fault catalogue detection is incomplete.
- Old consumer remains, retained workflow/protected data drifts, context RED does not block, GREEN cannot be read back, or human settings boundary is unavailable.
- Strict review or final quality gate is not pass.

Valid recovery is a new source SHA and forward-fix. Do not reset/rewrite history, rerun a poisoned SHA, add a fallback writer, or perform automatic rollback. Before merge, preserve the Issue branch and repair or abandon it. After merge, human chooses whole-merge revert or owned forward-fix; Epic main remains a separate human gate.

## 7. Completion criteria

Implementation may start only when S0 and S1 exits are evidenced, this revised spec has a fresh Strict pass at its exact pushed SHA, projection readback is complete, explicit dispatch is recorded, and no concurrent writer exists.

Issue #396 is complete only after:

- replacement gate is implemented and locally verified;
- human merged the Issue PR into the Epic integration branch;
- consumer-zero and old policy retirement are proven on final source;
- retained workflow, protected data, and required-context final readback are GREEN;
- merged candidate is materialized once and parent first-five/fault/twenty evaluation is accepted;
- Code Review Strict, Final Quality Gate Strict v2, B3 evidence, and Issue/Epic reports are complete.

Epic main merge and Issue closure remain human-controlled boundaries.
