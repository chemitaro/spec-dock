---
種別: 要件定義書（Epic）
ID: "epic-00333"
タイトル: "Multi Issue Epic Completion and Global Cutover"
関連GitHub: ["chemitaro/spec-dock#333"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-23"
親: ["init-00322"]
candidate_semantic_key: "epic-completion-and-global-cutover"
canonical_path: "spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00333-epic-completion-and-global-cutover/requirement.md"
---

# epic-00333 Multi Issue Epic Completion and Global Cutover — 要件定義（何を、なぜ行うか）

## 1. Epic Outcome

Main／Maintainer／Humanが、複数Issue Epicのdependencyとmerge状態を管理し、全Issue merge後にdefault branch上でEpic Delivery ReviewとEpic finishを完了し、Human-authorized global cutover、post-cutover evaluation、release decision、Initiative closure handoffまでを順序立てて完了できる。

## 2. Scope

- Issue dependency、safe parallelism、default branch refresh。
- all-Issue merged判定。
- Epic Delivery Review、cross-Issue integration validation。
- P0／P1時のJIT bounded repair Issue／PR。
- Epic finish。
- legacy surface removal、provider／installed／dogfood parity。
- existing Scope replay、compatibility、known-good baseline、rollback activation。
- Human mergeによるofficial global cutover activation。
- post-cutover 4週間／5件評価、週次集計、final decision package、release decision。
- release後のEpic finish／Initiative closure handoff。

## 3. Non-scope

- aggregate Epic PR。
- 事前Final QA Issue。
- E3-I2 merge前のpost-cutover evidence projection。
- Human mergeを伴わないofficial cutover／release activation。
- 新しいWorkflow database。
- closed historical Scopeの書換え。

## 4. Requirements

| ID | Requirement |
|---|---|
| E3-REQ-001 | MainがEpic PlanのIssue dependencyとHuman merge状態を追跡し、dependent Issueを安全なdefault branch baselineから開始する。 |
| E3-REQ-002 | 独立vertical Issueだけをparallel実行し、dependency merge前に下流Issueを開始しない。 |
| E3-REQ-003 | 全Issueがdefault branchへmerge後、最初のincluded Issue変更前に定めたsemantic BASEからreview対象default-branch HEADまでをEpic ContractのDelivery Review対象とし、mutation frontierとEpic Contract全体を評価する。BASE ancestryを解決できなければ`insufficient-evidence`とする。 |
| E3-REQ-004 | Epic Reviewでmutationが必要なP0／P1が見つかった場合だけJIT bounded Issueと個別PRを作成する。 |
| E3-REQ-005 | Epic Review PASS後、全Issue／repair PRのmerged HEADとEpic evidenceを確認してEpic finishする。 |
| E3-REQ-006 | vNext capability完成後、Epic 1が所有しないremaining shared／execution／delivery legacy surfaceを順序立てて除去する。Epic 1のplanning-specific surfaceはabsence verificationだけを行い再変更しない。 |
| E3-REQ-007 | provider／installed／dogfood surfaceとdocs／templates／scriptsの責務parityを確認する。 |
| E3-REQ-008 | 既存open Scopeが文書一括migrationなしでvNextへ入り、不足契約だけ局所refreshできる。 |
| E3-REQ-009 | `E3-I2 Official Global Cutover and Rollback Activation`のreviewed dedicated PRをHumanがmergeした時点だけをofficial global cutover activation eventとする。merge前のIssue Delivery Reviewはpre-cutover readiness、parity、replay、security、rollback capabilityを評価し、post-cutover evidenceを要求または捏造しない。 |
| E3-REQ-010 | E3-I2はcutover前のknown-good HEAD、rollback mechanism／trigger、rollback drill、remaining legacy removal、provider／installed／dogfood parity、existing Scope replay、security auditを証拠化する。merge後にreviewed HEAD、official route、rollback readinessを確認してE3-I2をfinishする。 |
| E3-REQ-011 | `E3-I3 Post Cutover Evaluation Release Decision and Initiative Closure`はE3-I2のHuman merge／cutover確認後に開始し、post-cutover default branchから一つのdedicated branch／draft PRを作り、週次Evidenceとfinal decision packageを所有する。 |
| E3-REQ-012 | 各代表runのraw evidenceは発生元の`report.md`、CI／GitHub evidence、Oracle session等の既存SSOTへ保持し、E3-I3は自Issueの`report.md`／Artifactでsource reference、weekly aggregation、baseline comparison、decision statusを永続化する。ChatGPT／ExecutorはGit transactionを行わず、Mainだけが明示的commit／pushする。 |
| E3-REQ-013 | E3-I3はcutover後の最低4週間かつ5件以上の代表Workflow、直近3件以上の旧Workflow baseline、required task-shape diversity、operational M-001〜M-016を満たし、M-017 materialization、M-018 publication、M-019 signed Human Gate／canonical parity／implementation Evidenceのimmutable referencesを検証するまでfinal Issue Delivery Reviewへ進まない。 |
| E3-REQ-014 | E3-I3 final Issue Delivery Review PASS後、Human mergeがrelease decision packageとrelease notesをrepositoryへ公開する。reviewed HEAD確認後にE3-I3をfinishし、その後default branch上のEpic Delivery Review、Epic finish、Initiative closureを別々のgateとして実施する。 |
| E3-REQ-015 | floor／target／Evidence未達時はE3-I3をfinishせず、同Issueで継続計測するか、実装修正用bounded follow-up Issue／PRをHuman mergeして評価期間をHuman-approved decisionでrestart／extendするか、known-goodへのrollback Issue／PRを実行するか、Initiativeを中止する。未達状態をPASS／releaseへ読み替えない。 |
| E3-REQ-016 | sensitive-data exclusionとdirect-argv defaultをrepository-wideに検証する。shell例外はHuman-approved Epic Design、固定template、untrusted input拒否／safe encoding、injection regression evidence、明示的rollback mechanism／trigger、tested rollback evidenceをすべて必要とし、欠落時はcutover／release gateをFAILとする。 |
| E3-REQ-017 | E3-I3のnormative final packageは`FINAL-METRIC-PACKAGE-CONTRACT.md`に従うM-001〜M-019 complete packageである。M-001〜M-016はE3-I3が評価し、M-017〜M-019はownerが生成したimmutable locator／identityを参照する。final Review、Human merge、Epic Review、Epic finish、Initiative closureでM-001〜M-016-only packageを使用しない。 |

| E3-REQ-018 | Epic Delivery Reviewとcutover／release ReviewはGit-bound default-branch／PR evidenceを使用し、Planning Candidate ZIP PASSを代替しない。 |
| E3-REQ-019 | E3-I3は各Planning runのScope、Review mode、Revision lane、Candidate version／Git HEAD、Codex resource proxy、latencyをM-011／M-013 evidenceとして集計し、archive／Gitの一方を無条件固定せず品質／resource tradeoffを評価する。 |

## 5. Acceptance Criteria

| ID | Acceptance Criteria |
|---|---|
| E3-AC-001 | dependencyを持つ複数Issue Epicを個別PRで順次mergeし、明示semantic BASEからreviewed default-branch HEADまでのEpic Review PASSへ進める。 |
| E3-AC-002 | independent Issueのparallel pathとdependent Issueのblocked pathが正しく動く。 |
| E3-AC-003 | Epic Review P1からJIT repair Issue／PRを作り、再Review PASS後にfinishできる。 |
| E3-AC-004 | aggregate Epic PRと事前Final QA IssueなしでEpicをfinishできる。 |
| E3-AC-005 | Epic 1のplanning-specific surfaceを再変更せずabsence verificationし、remaining legacy required surface、stale reference、provider／installed／dogfood差分が0。 |
| E3-AC-006 | E3-I2のpre-cutover Reviewがremaining legacy 0、parity 100%、existing Scope replay、known-good HEAD、rollback drill、security／shell-exception rollback evidenceを確認し、Human mergeだけがofficial cutoverをactivateする。 |
| E3-AC-007 | E3-I3がcutover後default branchからdedicated branch／draft PRを作成し、発生元Evidenceのsource reference、weekly aggregation、baseline、task-shape、decision statusを自Issue report／Artifactへ継続保存する。 |
| E3-AC-008 | cutover後4週間かつ5件以上、旧Workflow baseline 3件以上、required task-shape coverageを満たし、5件中4件以上の予定外介入0、raw transcript必須読込0、handoff中央値30%以上削減、旧認知route 0、Human Gate violation 0、semantic state DB 0、parity 100%をM-001〜M-016として判定する。さらにM-017〜M-019 immutable referencesを検証し、complete M-001〜M-019 packageがない限りfinal Review／merge／releaseへ進まない。 |
| E3-AC-009 | repository-wide security auditがsensitive-data exposure 0、unsafe shell interpolation 0、未承認shell exception 0、rollback mechanism／trigger／tested evidence欠落0を示す。 |
| E3-AC-010 | E3-I3 final Issue Delivery Review PASS後、Human mergeでfinal decision package／release notesを公開し、reviewed HEAD確認後にE3-I3をfinishできる。 |
| E3-AC-011 | E3-I3 merge後のdefault branch Epic Review PASS、Epic finish、Initiative Final Completion Summary／Human closureが順番に実行され、cutover／release／Epic finish／Initiative closureが混同されない。 |
| E3-AC-012 | floor／target未達時にcontinue、bounded follow-up、Human-approved evaluation restart／extension、rollback、terminationのいずれかへfail closedでrouteできる。 |
| E3-AC-013 | E3-I3 report／Artifact／reviewed PRがM-001〜M-019の各metric ID、owner、status、evidence locator、evidence identity、blocking、next actionを持ち、M-017〜M-019を再生成せず解決可能なimmutable referenceとして保持する。 |
| E3-AC-014 | Epic Delivery Review／cutover／release fixtureがGit-bound HEAD／BASE／CI evidenceを必須とし、Planning Candidate ZIPだけからPASSを生成しない。 |
| E3-AC-015 | evaluation packageがPlanning Scope／Review mode／Revision lane別のCodex resource proxyとwall-clockを記録し、品質非劣化のもとでmode selectionを評価できる。 |
