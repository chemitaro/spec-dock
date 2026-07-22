---
種別: 設計書（Epic）
ID: "epic-00333"
タイトル: "Multi Issue Epic Completion and Global Cutover"
関連GitHub: ["chemitaro/spec-dock#333"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-23"
依存: ["requirement.md"]
親: ["init-00322"]
candidate_semantic_key: "epic-completion-and-global-cutover"
canonical_path: "spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00333-epic-completion-and-global-cutover/design.md"
---

# epic-00333 Multi Issue Epic Completion and Global Cutover — 設計（どう実現するか）

## 1. Multi-Issue Coordination

```text
Epic Plan dependency graph
→ select ready vertical Issues
→ dedicated PR／Human merge per Issue
→ refresh default branch
→ unlock dependents
→ all Issues merged
→ Epic Delivery Review on default branch
```

MainはIssue statusだけでなくmerged commitとdefault branch反映を確認する。parallel実行はDAG上で独立したIssueに限定する。

## 2. Git-bound Epic Delivery Review

Epic Delivery ReviewはGit-bound default-branch Reviewであり、Planning Candidate ZIP PASSを代替Evidenceにしない。

Contract OwnerはEpic。Issue Reviewを再実行せず、cross-Issue integration、Epic Requirement／Design、integration／E2E、compatibility、operabilityを評価する。

```text
PASS → epic finish candidate
P0/P1 + mutation → JIT repair Issue / dedicated PR
P2/P3 only → no branch mutation
```

## 3. No Aggregate Epic PR

Epicの全変更は個別Issue PRでdefault branchへmergeする。Epic Reviewは、最初のincluded Issue変更前に明示したsemantic BASEからreview対象default-branch HEADまでを対象とし、BASE ancestryをfail closedで検証する。mutation frontierとEpic Contract全体を評価し、aggregate Epic PRを作らない。

## 4. Explicit temporal lifecycle

```text
E3-I1 merged and finished
→ E3-I2 dedicated PR pre-cutover Review
→ Human merge of E3-I2 = official global cutover activation
→ merged HEAD／official route／rollback readiness verification
→ E3-I2 finish
→ E3-I3 starts from post-cutover default branch
→ one dedicated branch／draft PR
→ ≥4 weeks and ≥5 representative runs
→ weekly evidence aggregation
→ final Issue Delivery Review
→ Human merge of E3-I3 = release decision package publication
→ reviewed HEAD verification
→ E3-I3 finish
→ default-branch Epic Delivery Review
→ Epic finish
→ Initiative Final Completion Summary／Human closure
```

cutover、release decision、Epic finish、Initiative closureは異なるauthority eventであり、同一gateへ短絡しない。

## 5. E3-I2 — Official Global Cutover and Rollback Activation

E3-I2はrepository-wide mutationとofficial route切替の高リスク境界を所有する。

- Epic 1が所有しないremaining shared／execution／delivery Skill／Agent／Workflow／Template／Scriptを除去する。planning-specific surfaceはverification-only。
- provider／installed／dogfood parity、current docs／prompt／help／testsのstale reference 0、existing Scope replayをpre-cutoverに検証する。
- known-good pre-cutover HEAD、rollback mechanism、rollback trigger、rollback drill evidenceを固定する。
- Issue Delivery Reviewはpre-cutover evidenceだけで判定する。post-cutover runを仮定しない。
- Human mergeがofficial cutoverをactivateする。merge前の自動activationを禁止する。

## 6. E3-I3 — Post Cutover Evaluation Release Decision and Initiative Closure

E3-I3は単なるQA Issueではない。cutover後にしか取得できないEvidence、Human release decision、失敗時の継続／rollbackを所有する独立operational outcomeである。

- E3-I2 merged HEADからIssueを開始し、post-cutover default branchをbaseにdedicated branchを作る。
- 早期にdraft PRを作成し、Human mergeまではrelease decisionを確定しない。
- floorを満たすまでMainが明示的commit／pushでweekly report／Artifactを更新する。ChatGPT／ExecutorはGit transactionを行わない。
- 4週間／5件、baseline 3件、required task shapes、operational M-001〜M-016を満たし、M-017 materialization、M-018 publication、M-019 signed Human Gate／canonical parity／implementation Evidenceのimmutable referencesが解決したcurrent HEADだけをfinal Issue Delivery Reviewへ渡す。
- PASS後のHuman mergeがrelease decision package／release notesをrepositoryへ公開する。

## 7. Evidence ownership and persistence

| Evidence | Owner | Persistent location |
|---|---|---|
| individual E1／E2 run evidence | originating Main／Issue | originating `report.md`、CI／GitHub evidence、Oracle session、accepted Artifact |
| pre-cutover parity／replay／rollback／security | E3-I2 Main | E3-I2 `report.md`／ArtifactとPR evidence |
| weekly post-cutover aggregation | E3-I3 Main／Maintainer | E3-I3 `report.md`／evaluation Artifact on dedicated branch／draft PR |
| operational M-001〜M-016 evaluation | E3-I3 Main／Maintainer | E3-I3 weekly／final Artifact |
| immutable M-017 materialization reference | P3 materialization gate | Candidate-SHA ledger／canonical parity／report marker |
| immutable M-018 publication reference | publication gate | commit／push／remote ref／publication ledger |
| immutable M-019 Human-Gate reference | Human Portfolio Approval／E1 implementation | canonical approval Evidence Artifact／source record SHA／canonical parity／implementation evidence |
| final M-001〜M-019 decision package | E3-I3 Main／Maintainer | E3-I3 final Artifact／release notes／reviewed PR |
| Epic completion verdict | Epic Reviewer／Main | default-branch Epic Review evidence／Epic report |
| Initiative closure | Human／Main | Initiative Final Completion Summary／report disposition |
## 7.5 Complete metric package

E3-I3 follows `FINAL-METRIC-PACKAGE-CONTRACT.md`.

```text
M-001〜M-016: evaluate and aggregate
M-017: resolve materialization identity Evidence
M-018: resolve publication Evidence
M-019: resolve signed Human Gate／canonical parity／implementation Evidence
→ one M-001〜M-019 final package
```

Each metric record includes owner, status, evidence locator, evidence identity, observed time, blocking state, and next action. Missing or unresolved M-017〜M-019 is `insufficient-evidence`, not a reason to regenerate the historical fact. E3-I3 final Review／Human merge, default-branch Epic Review, Epic finish, and Initiative closure all consume the same complete package.


## 8. Failure, continuation, and rollback

- floor未達だがcontract変更不要: E3-I3 draft PRを開いたまま継続計測する。
- 実装修正が必要: bounded follow-up Issue／dedicated PRを作り、Human merge後に評価期間をHuman-approved decisionでrestartまたはextendする。
- release-blocking failure: known-goodへ戻すbounded rollback Issue／PRを作り、Human mergeする。E3-I3はrelease PASSを記録しない。
- rollbackまたはInitiative中止時: official route、Evidence、Issue／Epic state、Human decisionをreportへ記録し、success completionを禁止する。

## 9. Sensitive data and process invocation closure

Prompt／Operator Context／Human Relay／GitHub外file／Workbench／Artifact／Execution Brief／Repair Batch／report evidenceのsensitive-data exposureをscan／fixtureで検証する。

Official process launchはdirect argvをdefaultとする。shell exceptionは次の全Evidenceが必要である。

```text
Human-approved Epic Design
fixed command template
untrusted-input rejection or safe encoding
injection regression evidence
explicit rollback mechanism and trigger
tested rollback evidence
```

一つでも欠ければE3-I2 cutover Review、E3-I3 final Review、release closureはFAILである。
