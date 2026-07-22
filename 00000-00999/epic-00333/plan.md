---
種別: 計画書（Epic）
ID: "epic-00333"
タイトル: "Multi Issue Epic Completion and Global Cutover"
関連GitHub: ["chemitaro/spec-dock#333"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-23"
依存: ["requirement.md", "design.md"]
親: ["init-00322"]
candidate_semantic_key: "epic-completion-and-global-cutover"
canonical_path: "spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00333-epic-completion-and-global-cutover/plan.md"
---

# epic-00333 Multi Issue Epic Completion and Global Cutover — 計画（Issue と実施順序）

## 1. Epic Outcome

複数Issue Epicをdefault branch上でReview／finishし、SpecDockのremaining global surfaceをHuman mergeでvNextへcutoverし、post-cutover評価とrelease decisionを別のIssue／PRで完了できる。

## 2. Issue Boundary Map

### E3-I1 — Multi Issue Epic Coordination and Finish

- Actor: Main／Human。
- Merge後Outcome: Epic dependency graph、個別Issue merge、default branch Epic Review、JIT repair Issue、Epic finishを完了できる。
- End-to-end責務: ready Issue selection、safe parallelism、merge verification、Epic Review、repair routing、finish、tests／docs／projection。
- Separate PR理由: multi-Issue orchestrationとEpic completionはIssue executionとは異なるActor／Contract／rollback boundaryを持つ。
- Dependency: Epic 2完了。
- Acceptance evidence:
  - dependencyを持つ複数vertical Issueのdedicated PR／Human merge、default branch refresh、ready判定、parallel／blocked laneを示すintegration report。
  - all-Issue merged後、明示semantic BASEからreviewed default-branch HEADまでのEpic Delivery Review PASS、aggregate Epic PRなし、JIT repair Issue経路、epic finishのE2E evidence。
  - merged commitとdefault branch反映を照合するGitHub／Runtime verification。
- Milestoneではない理由: 複数Issueを一つのEpic Outcomeへ統合する独立公開Workflowである。

### E3-I2 — Official Global Cutover and Rollback Activation

- Actor: Maintainer／Human／Main。
- Merge後Outcome: remaining shared／global legacy surfaceが除去され、vNext official routeがHuman mergeによりactivateされ、parity、existing Scope compatibility、known-good rollback readinessが成立する。release／Initiative closureはまだ成立しない。
- End-to-end責務: Epic 1が所有しないremaining shared／execution／delivery legacy removal、docs／templates／scripts、provider／installed／dogfood parity、existing Scope replay、known-good HEAD、rollback mechanism／trigger／drill、pre-cutover security audit、cutover PR／Human merge／merged-HEAD verification。Epic 1のplanning-specific surfaceはabsence verificationだけを行い再変更しない。
- Separate PR理由: official route切替とrollback activationは独立した高リスクrepository／Human decision boundaryである。
- Dependency: E3-I1。
- Acceptance evidence:
  - Epic 1 planning-specific surfaceを再変更せずabsence verificationだけを行ったownership audit。
  - remaining shared／global legacy surface 0、provider／installed／dogfood parity 100%、existing Scope replay PASS。
  - known-good pre-cutover HEAD、rollback mechanism／trigger、rollback drill result。
  - sensitive-data exposure 0、direct-argv default、unsafe shell interpolation 0、各shell exceptionのapproval／fixed template／safe input／injection evidence／rollback mechanism／trigger／tested rollback evidence。
  - pre-cutover Issue Delivery Review PASS、Human merge、reviewed HEAD一致、official route activation confirmation。
- Milestoneではない理由: Human mergeでofficial routeを切り替える独立運用Outcomeとrollback boundaryを持つ。

### E3-I3 — Post Cutover Evaluation Release Decision and Initiative Closure

- Actor: Maintainer／Human／Main。
- Merge後Outcome: mandatory post-cutover evaluation、final decision package、release notesがrepositoryへ公開され、release decisionがHuman mergeで確定し、Epic／Initiative closureへ進める。
- End-to-end責務: E3-I2 cutover確認、post-cutover branch／draft PR、run evidence source reference、weekly aggregation、baseline comparison、required task-shape coverage、operational M-001〜M-016、M-017 materialization／M-018 publication／M-019 signed Human Gate・canonical parity・implementation Evidenceのimmutable reference verification、M-001〜M-019 final package、changeability、Brief comparison、final Issue Delivery Review、Human release decision、reviewed HEAD、closure handoff。
- Separate PR理由: 4週間／5件Evidenceはcutover merge後にしか生成できず、cutover activationとは別のtemporal、Human decision、rollback／continuation boundaryを持つ。QA工程だけの分割ではない。
- Dependency: E3-I2 Human merge／cutover confirmation。
- Acceptance evidence:
  - E3-I2 merged HEAD／official route／known-good rollback reference。
  - post-cutover default branchから作成したdedicated branch／draft PRと、各runのsource `report.md`／CI／GitHub／Oracle reference。
  - cutover後4週間かつ5件以上、旧Workflow baseline 3件以上、required task-shape coverage、M-001〜M-016のweekly／final operational evaluation。
  - M-017／M-018／M-019のimmutable evidence locatorとidentity、および`FINAL-METRIC-PACKAGE-CONTRACT.md`に従うM-001〜M-019 complete decision package。
  - 5件中4件以上の予定外介入0、raw transcript必須読込0、handoff中央値30%以上削減、旧認知route 0、Human Gate violation 0、semantic state DB 0、parity 100%、Brief Evidence finding 0等の判定。
  - repository-wide sensitive-data exposure 0、direct-argv default、shell exception rollback evidence欠落0。
  - final Issue Delivery Review PASS、Human merge、reviewed HEAD一致、release decision package／release notes publication。
  - 未達時のcontinue／bounded follow-up／Human-approved evaluation restart／extension／rollback／termination disposition。
- Milestoneではない理由: cutover後にしか成立しない長期EvidenceとHuman release decisionを所有する独立operational Outcomeである。

## 3. Dependency

```text
E3-I1 → E3-I2 → E3-I3
```

## 4. Per-Issue Delivery

3 Issueとも専用branch／PR／Human mergeを持つ。

- E3-I2はE3-I1 merge後のdefault branchから開始する。
- E3-I2 Human mergeがofficial cutoverをactivateする。
- E3-I3はE3-I2 merge／cutover確認後のdefault branchから開始し、評価期間中は一つのdraft PRへweekly evidenceをMainが明示的にcommit／pushする。
- E3-I3はfloor／target／Evidenceを満たすまでready／PASS／Human mergeへ進めない。

## 5. Git-bound Epic Delivery Review

E3-I3 merge後、default branch上で次を検証する。

- 全3 Capability EpicのE2E。
- per-Issue PR／Human merge／finish。
- cutover activationとrelease decisionが別Issue／PR／Human eventであること。
- default branch Epic Review。
- Candidate ZIP Planning／Review／materialization。
- existing Scope replay。
- provider／installed／dogfood parity。
- planning-specific surfaceはEpic 1で除去済みかつEpic 3ではverification-onlyであること。
- remaining legacy／stale reference 0。
- 4週間／5件floor、baseline、task-shape、M-001〜M-016 operational evaluation（Planning Scope／Review mode／Revision lane／Candidate or Git identity／Codex resource proxyを含む）とM-017〜M-019 immutable referencesを含むM-001〜M-019 final package。
- Briefなし／generic／Architecture-Aware比較。
- changeability／rollback。
- shell exception rollback evidence欠落0。

PASS後にEpic finishし、Initiative Final Completion Summary／Human closureへhandoffする。
