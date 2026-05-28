---
種別: scratch
ID: "scratch-20260528t013400z"
タイトル: "ChatGPT template design response for requirement grill workflow"
状態: "draft"
作成者: "ChatGPT via Codex"
最終更新: "2026-05-28"
親: ["iss-00134"]
関連: ["scratch-20260528t012300z", "research-20260528t011700z"]
authority: "raw"
derived_from:
  - "discussions/20260528t012300z-scratch-chatgpt-template-design-followup-prompt.md"
reflected_to: []
---

# scratch-20260528t013400z ChatGPT template design response for requirement grill workflow

## メモ

Placement decision
結論

推奨: Option A — 新規 specialized templates を provider scaffold に追加。ただし nested path は増やさず、現行の flat layout を維持する。

追加する場合の推奨ファイル名は、category prefix 付きの flat templates です。

Provider-side authority:
src/spec_dock/assets/spec_dock/templates/discussions/research-source-grounding.md
src/spec_dock/assets/spec_dock/templates/discussions/interview-grill-session.md
src/spec_dock/assets/spec_dock/templates/discussions/disc-decision-tree.md
src/spec_dock/assets/spec_dock/templates/discussions/disc-adr-triage.md

Installed scaffold path:
spec-dock/templates/discussions/research-source-grounding.md
spec-dock/templates/discussions/interview-grill-session.md
spec-dock/templates/discussions/disc-decision-tree.md
spec-dock/templates/discussions/disc-adr-triage.md

前回案の src/spec_dock/assets/install_root/spec-dock/templates/... は、agent-tooling install_root と spec-dock scaffold templates の境界を混同していた可能性が高いです。今回の discussion templates は agent/tooling installed layout asset ではなく、spec-dock workspace scaffold template なので、提示された通り src/spec_dock/assets/spec_dock/templates/discussions/ を provider-side authority として扱うのが妥当です。

Option evaluation
Option	判断	理由
Option A: 新規 specialized templates を provider scaffold に追加	推奨	spec-dock-requirement-grill 専用の artifact shape を明確化できる。既存 generic templates を肥大化させない。flat layout を維持できる。docs-only / template-only change として review しやすい。
Option B: 既存 research.md / interview.md / disc.md を拡張	非推奨	generic template が grill workflow 専用の詳細で重くなる。通常の research/disc/interview の軽量性を損なう。
Option C: template は増やさず skill 内 guidance のみにする	初期回避策としては可。ただし本採用では非推奨	skill だけに guidance を置くと、artifact の形が agent ごとに揺れやすい。spec-dock の scaffold として再利用しにくい。
推奨ファイル名の理由

source-grounding.md のような完全に独立した名前より、次のように category prefix を付ける方がよいです。

research-source-grounding.md
interview-grill-session.md
disc-decision-tree.md
disc-adr-triage.md

理由:

現行の flat template layout と整合する。

research / interview / disc の artifact category がファイル名から分かる。

adr-triage は final ADR ではなく discussion-level triage なので、adr-*.md ではなく disc-adr-triage.md とする方が誤用を避けやすい。

nested template path を増やさないため、既存 scaffold logic への影響が小さい。

未検証: spec-dock の template discovery / CLI が arbitrary template filename を自動認識するか、固定名だけを扱うかはこの回答では確認していません。固定名のみの場合でも、この slice は template asset 追加として成立しますが、CLI integration は後続 slice になります。

Template contract summary
Template	Category	Purpose	Canonical?	Canonical reflection target
research-source-grounding.md	research	local source inspection の facts / inferences / unverified / implications を分離する	No	requirement/design/plan の source-grounded constraints、または follow-up
interview-grill-session.md	interview	one-question-at-a-time interview の Q/A と rationale を記録する	No	requirement/design/plan の confirmed updates、または open questions
disc-decision-tree.md	disc	options / tradeoffs / recommendation / open questions / adoption target を整理する	No	design decision、plan slice、requirement scope、または ADR candidate
disc-adr-triage.md	disc	final ADR ではなく ADR candidate 判定を行う	No	ADR draft handoff、design note、または no-ADR decision

共通 contract:

discussion artifact は source of truth ではない。
canonical docs への反映は adoption / reflection を経て行う。
unverified / unresolved / candidate は requirement/design/plan に confirmed として混ぜない。
Full template drafts
1. research-source-grounding.md

Provider-side path:

src/spec_dock/assets/spec_dock/templates/discussions/research-source-grounding.md

Installed path:

spec-dock/templates/discussions/research-source-grounding.md

Draft:

Markdown
# Research: Source grounding for requirement grill

## Metadata

- Issue ID:
- Issue title:
- Initiative:
- Epic:
- Date:
- Author / agent:
- Related skill: `spec-dock-requirement-grill`
- Status: draft | ready-for-reflection | reflected | archived

## Canonical status

This research artifact is not a source of truth by itself.

Findings in this document become canonical only after they are reflected into one or more adopted artifacts, such as:
- issue requirement;
- issue design;
- issue plan;
- accepted ADR;
- parent epic or initiative docs, if explicitly adopted there.

Do not treat unverified findings or inferences in this document as accepted requirements.

## Purpose

Use this artifact to record local source inspection before asking the human requirement/design questions.

The goal is to avoid asking humans questions that the repo, spec-dock docs, discussion history, generated state, source files, or tests can already answer.

## Inspection scope

### Current task instruction

- Prompt / request inspected:
- Explicit constraints:
- Requested output:
- File edits allowed? yes | no | unclear

### Active issue docs inspected

List files inspected.

- `...`
- `...`

### Parent epic / initiative docs inspected

List files inspected.

- `...`
- `...`

### Issue-local discussions inspected

List files inspected.

- `discussions/research/...`
- `discussions/disc/...`
- `discussions/interview/...`
- `discussions/scratch/...`
- `discussions/adr/...`

### Generated state inspected

List generated state files inspected, if available.

- `spec-dock/.agent/...`

### Source / tests / assets inspected

List relevant repo files inspected.

- `...`

### External sources inspected

Normally leave empty.

Use only when explicitly requested, permitted, or required.

- None

## Facts

Facts are statements directly supported by inspected sources.

| Fact | Source | Confidence | Notes |
|---|---|---:|---|
|  |  | high |  |

## Inferences

Inferences are conclusions drawn from facts. They are not direct facts.

| Inference | Based on facts | Confidence | Implication |
|---|---|---:|---|
|  |  | medium |  |

## Unverified

Use this section for claims that may be true but were not confirmed by inspected sources.

| Unverified item | Why it matters | How to verify | Blocking? |
|---|---|---|---:|
|  |  |  | yes / no |

## Implications

Use this section to explain what the facts and inferences mean for requirement, design, plan, or ADR triage.

### Requirement implications

- 

### Design implications

- 

### Plan implications

- 

### ADR implications

- 

## Questions resolved by source inspection

These questions should not be asked to the human because local inspection already answered them.

| Question | Answer from source | Source | Artifact affected |
|---|---|---|---|
|  |  |  |  |

## Human questions still needed

Only list questions that cannot be answered from local sources and affect requirement/design/plan/ADR validity.

Rank from most blocking to least blocking.

| Rank | Question | Why source cannot answer it | Why it matters | Affected artifacts |
|---:|---|---|---|---|
| 1 |  |  |  |  |

## Reflection target

State where this research should be reflected after review.

- Requirement:
- Design:
- Plan:
- ADR triage:
- Follow-up issue:
- No canonical reflection needed:

## Ready for reflection?

- [ ] Facts are separated from inferences.
- [ ] Unverified items are labeled.
- [ ] Source-answerable questions are not forwarded to the human.
- [ ] Remaining human questions are ranked.
- [ ] Reflection targets are identified.
2. interview-grill-session.md

Provider-side path:

src/spec_dock/assets/spec_dock/templates/discussions/interview-grill-session.md

Installed path:

spec-dock/templates/discussions/interview-grill-session.md

Draft:

Markdown
# Interview: Requirement grill session

## Metadata

- Issue ID:
- Issue title:
- Initiative:
- Epic:
- Date:
- Interviewer / agent:
- Human participant:
- Related skill: `spec-dock-requirement-grill`
- Status: draft | active | ready-for-reflection | reflected | archived

## Canonical status

This interview artifact is not a source of truth by itself.

Answers become canonical only after they are reflected into adopted requirement/design/plan docs or an accepted ADR.

Do not copy partially resolved or ambiguous answers into canonical docs as confirmed decisions.

## Purpose

Use this artifact to record a one-question-at-a-time clarification session for an active spec-dock issue.

The session should clarify only questions that:
- cannot be answered from local repo/docs;
- affect requirement, design, plan, artifact authority, validation, or ADR triage;
- are necessary to avoid guessing.

## Source-grounded pre-read

Link or summarize the source-grounding artifact used before asking questions.

- Related research artifact:
- Local inspection completed? yes | no | partial
- If partial, explain why:

## Session constraints

- Ask exactly one question at a time.
- Do not ask compound questions.
- Do not ask the human to answer facts already available in repo/docs.
- Record why each question matters.
- Record affected artifacts.
- Mark each answer as resolved, partially resolved, unresolved, or superseded.
- Do not treat interview answers as canonical until reflected.

## Current blocking ambiguity

Describe the highest-impact ambiguity currently being clarified.

```text

Question log
Question 1

Status: pending | answered | partially-resolved | unresolved | superseded

Question:

Why this matters:

Source-grounded context:

Summarize what local inspection already found.

Why local sources were insufficient:

Affected artifacts:

Requirement:

Design:

Plan:

ADR triage:

Follow-up issue:

Other:

Answer:

Interpretation of answer:

Separate direct answer from inference.

Resolution status:

 Resolved

 Partially resolved

 Unresolved

 Superseded

Follow-up needed?

If yes, do not list multiple new questions for the human in the chat response. Record candidates here and ask only the next highest-priority question.

Question 2

Status: pending | answered | partially-resolved | unresolved | superseded

Question:

Why this matters:

Source-grounded context:

Why local sources were insufficient:

Affected artifacts:

Requirement:

Design:

Plan:

ADR triage:

Follow-up issue:

Other:

Answer:

Interpretation of answer:

Resolution status:

 Resolved

 Partially resolved

 Unresolved

 Superseded

Follow-up needed?

Resolved answers

List answers that are ready for reflection.

Question	Resolved answer	Reflection target	Notes
			
Partially resolved answers

List answers that need qualification before canonical reflection.

Question	Partial answer	Remaining ambiguity	Next step
			
Open questions

List unresolved questions. Do not reflect these into canonical docs as confirmed decisions.

Priority	Question	Blocking?	Affected artifacts	Next action
1		yes / no		
Reflection proposal
Requirement updates proposed
Design updates proposed
Plan updates proposed
ADR triage proposed
Follow-up issues proposed
Ready for reflection?

 Local inspection was done before human questions.

 Each human question was asked one at a time.

 Each question has why-it-matters context.

 Each question has affected artifacts.

 Resolved answers are separated from partially resolved answers.

 Open questions are not presented as confirmed decisions.


---

## 3. `disc-decision-tree.md`

Provider-side path:

```text
src/spec_dock/assets/spec_dock/templates/discussions/disc-decision-tree.md

Installed path:

spec-dock/templates/discussions/disc-decision-tree.md

Draft:

Markdown
# Discussion: Decision tree

## Metadata

- Issue ID:
- Issue title:
- Initiative:
- Epic:
- Date:
- Author / agent:
- Related skill:
- Status: draft | ready-for-decision | reflected | archived

## Canonical status

This discussion artifact is not a source of truth by itself.

The recommendation in this document becomes canonical only after it is adopted into:
- requirement docs;
- design docs;
- plan docs;
- accepted ADR;
- parent epic or initiative docs, if explicitly reflected there.

Do not treat rejected options, draft recommendations, or open questions as accepted decisions.

## Purpose

Use this artifact to compare options for a requirement, design, plan, or workflow decision.

This template is useful when source grounding and/or interview answers reveal multiple viable paths.

## Decision summary

### Decision needed

```text

Why this decision is needed now
What happens if this decision is deferred?
Source context

List the evidence and discussion artifacts used.

Supporting sources

...

Related research

discussions/research/...

Related interview

discussions/interview/...

Related prior discussion or ADR

discussions/disc/...

discussions/adr/...

Constraints

List constraints that options must respect.

Constraint	Source	Hard or soft?	Notes
		hard	
Options
Option A:

Summary

What changes

What stays unchanged

Pros

Cons

Risks

Validation

Impact on artifacts

Requirement:

Design:

Plan:

ADR:

Follow-up issue:

Option B:

Summary

What changes

What stays unchanged

Pros

Cons

Risks

Validation

Impact on artifacts

Requirement:

Design:

Plan:

ADR:

Follow-up issue:

Option C:

Summary

What changes

What stays unchanged

Pros

Cons

Risks

Validation

Impact on artifacts

Requirement:

Design:

Plan:

ADR:

Follow-up issue:

Tradeoff matrix
Criterion	Option A	Option B	Option C	Notes
Scope fit				
Simplicity				
Compatibility				
Provider/source-of-truth clarity				
Installed-layout impact				
Validation ease				
Reversibility				
Future extensibility				
User/developer experience				
Recommendation
Recommended option
Rationale
Why other options are not recommended

Option A:

Option B:

Option C:

Open questions

Do not hide these in the recommendation.

Question	Blocking?	Owner	Next step
	yes / no		
Adoption target

State where the recommendation should be reflected.

Requirement:

Design:

Plan:

ADR:

Follow-up issue:

No canonical reflection needed:

Proposed canonical wording

Use this section only for patch-ready wording.

Requirement wording
Markdown
Design wording
Markdown
Plan wording
Markdown
ADR candidate wording
Markdown
Ready for adoption?

 Options are concrete and comparable.

 Tradeoffs are explicit.

 Recommendation is separated from facts.

 Open questions are not hidden.

 Adoption target is clear.

 Proposed canonical wording does not include unresolved ambiguity as confirmed content.


---

## 4. `disc-adr-triage.md`

Provider-side path:

```text
src/spec_dock/assets/spec_dock/templates/discussions/disc-adr-triage.md

Installed path:

spec-dock/templates/discussions/disc-adr-triage.md

Draft:

Markdown
# Discussion: ADR triage

## Metadata

- Issue ID:
- Issue title:
- Initiative:
- Epic:
- Date:
- Author / agent:
- Related skill:
- Related decision discussion:
- Status: draft | triaged | handed-off | reflected | archived

## Canonical status

This artifact is ADR triage only.

It is not a final ADR and does not record an accepted architecture decision by itself.

A decision becomes canonical only after:
- it is reflected into issue requirement/design/plan where appropriate; or
- a formal ADR is created and accepted through the project's ADR workflow.

Use `spec-dock-adr-facilitation` for final ADR drafting and facilitation.

## Purpose

Use this artifact to decide whether a requirement/design clarification should become an ADR candidate.

Do not create ADRs for ordinary local implementation details, reversible choices, generic notes, or decisions already dictated by existing project conventions.

## Decision candidate

### Candidate decision

```text

Decision context
Trigger source

Where did this candidate come from?

 Source grounding

 Human interview

 Decision tree

 Design review

 Implementation planning

 Other:

Related artifacts:

...

ADR need assessment

Evaluate each criterion.

Criterion	Assessment	Evidence	Notes
Hard to reverse	yes / no / unclear		
Surprising to future maintainers	yes / no / unclear		
Real tradeoff	yes / no / unclear		
Long-term architecture impact	yes / no / unclear		
Cross-issue consequence	yes / no / unclear		
Cross-epic or initiative consequence	yes / no / unclear		
Source-of-truth boundary impact	yes / no / unclear		
Provider vs installed-layout impact	yes / no / unclear		
Public workflow or user-facing behavior impact	yes / no / unclear		
Why this might need an ADR
Why this might not need an ADR
Reversibility

Describe how easy or hard it would be to change this decision later.

Tradeoff summary

Describe the real tradeoff, if any.

Scope of impact
Local issue impact
Parent epic impact
Initiative impact
Consumer repo / installed scaffold impact
Agent/tooling impact
Existing decision coverage

Check whether this decision is already covered.

Existing ADR:

Existing design doc:

Existing requirement:

Existing convention:

Not found:

Triage recommendation

Choose one.

 ADR required

 ADR not required

 Defer ADR decision

 Already covered by existing ADR or design doc

Rationale
Handoff
If ADR required

Proposed ADR title:

Suggested ADR scope:

Questions for ADR facilitation:

Handoff target:

spec-dock-adr-facilitation

If ADR not required

Where should the decision be reflected instead?

Requirement:

Design:

Plan:

Discussion only:

No reflection needed:

If deferred

What must be learned before triage can complete?

Ready for handoff or reflection?

 This artifact does not present itself as a final ADR.

 ADR criteria were evaluated.

 Evidence is separated from judgment.

 Recommendation is explicit.

 Reflection or handoff target is clear.

 No unresolved candidate is written as an accepted architecture decision.


---

# Canonical reflection rules

## Directly reflect into requirement/design/plan only when

Information may be reflected into canonical issue docs when all of the following are true:

```text
- it is confirmed by source inspection or human answer;
- it belongs to the issue scope;
- it has a clear adoption target;
- it does not require unresolved ADR triage;
- it is not contradicted by parent initiative/epic docs;
- it is stated in testable or reviewable terms;
- any assumptions are explicitly labeled.
Keep information in discussion artifacts when

Information should remain in research / interview / disc when it is:

- unverified;
- inferred but not confirmed;
- a rejected option;
- a raw human answer not yet interpreted;
- a partially resolved answer;
- an open question;
- an ADR candidate not yet triaged;
- a tradeoff discussion without adopted recommendation;
- a source excerpt or inspection note that is too detailed for canonical docs.
Requirement reflection boundary

Reflect into requirement docs:

- confirmed problem statement;
- confirmed goal;
- confirmed non-goals;
- confirmed scope boundary;
- source-grounded constraints;
- acceptance criteria that are testable or reviewable;
- explicitly labeled assumptions;
- explicitly labeled open questions, if the doc has an open-question section.

Do not reflect into requirement docs as confirmed content:

- undecided implementation approach;
- unresolved artifact authority;
- raw interview transcript;
- rejected options;
- untriaged ADR candidates;
- vague “should probably” language.
Design reflection boundary

Reflect into design docs:

- chosen approach;
- artifact paths;
- source-of-truth relationships;
- provider-side vs installed layout rules;
- lifecycle integration;
- interface or workflow shape;
- validation strategy;
- known tradeoffs after adoption.

Do not reflect into design docs as confirmed content:

- open decisions;
- design alternatives not selected;
- unresolved ADR candidates;
- speculative future extensions;
- assumptions without status label.
Plan reflection boundary

Reflect into plan docs:

- implementation slices;
- dependency order;
- HITL vs AFK classification;
- validation commands;
- done criteria;
- follow-up issue boundaries.

Do not reflect into plan docs as ordinary execution steps:

- unresolved requirement questions;
- implementation actions depending on undecided design;
- ADR drafting that has not passed triage;
- broad investigation without a defined outcome.
ADR reflection boundary

Use disc-adr-triage.md before an ADR when the candidate may be:

- hard to reverse;
- surprising;
- a real tradeoff;
- long-lived;
- cross-issue or cross-epic;
- about source-of-truth boundaries;
- about provider vs installed layout;
- about public workflow semantics.

Do not create an ADR for:

- local naming choices;
- reversible file placement;
- generic implementation notes;
- obvious conventions;
- one-off plan steps;
- ordinary test strategy.
Implementation slice recommendation
推奨

この template slice は、spec-dock-requirement-grill と同じ issue に含めてよい。ただし first skill slice とは分けて、独立した Slice 2 として扱うのがよいです。

理由:

issue title が “Adopt Matt Pocock grill skill review patterns” であれば、skill と templates は同じ統合目的に属する。

template-only change は review / validation しやすい。

first slice を provider-side shared skill asset だけに限定する方針を維持できる。

Slice 2 は scaffold template authority 側の追加なので、責務境界が明確。

CLI/template discovery のコード変更が必要になった場合だけ、別 issue または Slice 3 に切り出せる。

Slice 2 name
Slice 2: Add flat specialized discussion templates for requirement grill workflow
Files to add
src/spec_dock/assets/spec_dock/templates/discussions/research-source-grounding.md
src/spec_dock/assets/spec_dock/templates/discussions/interview-grill-session.md
src/spec_dock/assets/spec_dock/templates/discussions/disc-decision-tree.md
src/spec_dock/assets/spec_dock/templates/discussions/disc-adr-triage.md
Files not to change in Slice 2
src/spec_dock/assets/spec_dock/templates/discussions/research.md
src/spec_dock/assets/spec_dock/templates/discussions/interview.md
src/spec_dock/assets/spec_dock/templates/discussions/disc.md
src/spec_dock/assets/spec_dock/templates/discussions/scratch.md
src/spec_dock/assets/spec_dock/templates/discussions/adr.md

src/spec_dock/assets/install_root/.agents/skills/spec-dock-requirement-grill/SKILL.md
.codex/agents/*
CLI command implementation
template discovery implementation

例外: first skill slice で追加した SKILL.md に template names を参照させる微修正を同時に行う案もありますが、docs-only review を小さくするなら Slice 3 に回す方が安全です。

Acceptance criteria
Markdown
- Four new flat discussion templates exist under `src/spec_dock/assets/spec_dock/templates/discussions/`.
- No nested template directory is introduced.
- Existing generic templates remain unchanged.
- `disc-adr-triage.md` clearly states that it is not a final ADR.
- Each template states that discussion artifacts are not canonical source of truth.
- `research-source-grounding.md` separates facts, inferences, unverified items, and implications.
- `interview-grill-session.md` supports one-question-at-a-time interview records.
- `disc-decision-tree.md` separates options, tradeoffs, recommendation, open questions, and adoption target.
- `disc-adr-triage.md` evaluates hard-to-reverse, surprising, real tradeoff, long-term impact, and cross-issue consequences.
- Templates provide reflection targets for requirement/design/plan/ADR without treating discussion notes as adopted decisions.
Suggested validation
./spec-dock/scripts/spec-dock validate

Potential additional check, if available:

./spec-dock/scripts/spec-dock sync

未検証: sync が scaffold template asset changes に関係するか、agent-tooling install_root のみに関係するかはこの回答では確認していません。template-only validation の正確な command は repo implementation の後続確認対象です。

Risks / unresolved questions
Risks
Risk	内容	Mitigation
Template discovery が固定名しか見ない	新規 flat templates が CLI から使えない可能性がある。	Slice 2 は asset addition に限定し、CLI integration は後続確認にする。
Templates が重すぎる	issue-local discussions が過剰に長くなる。	skill 側で必要な template だけ使う。generic templates は維持する。
disc-adr-triage.md が ADR と誤解される	final ADR ではないのに決定記録として扱われる可能性。	ファイル名に disc- prefix を付け、本文で canonical status を明記する。
Generic templates との重複	research.md / interview.md / disc.md と役割が重なる。	specialized templates は requirement grill workflow 用、generic templates は汎用と明記する。
Provider path confusion	agent-tooling install_root と scaffold template authority を混同しやすい。	この slice は src/spec_dock/assets/spec_dock/templates/discussions/ のみを対象にする。
Discussion が shadow source-of-truth 化する	disc の recommendation が canonical と誤読される。	全 template に canonical status と reflection target を置く。
Unresolved questions

Template generation command の仕様
新規 template filename を CLI が選択肢として扱えるかは未確認です。

Installed scaffold path の正確な copy behavior
src/spec_dock/assets/spec_dock/templates/discussions/* が spec-dock/templates/discussions/* にそのまま入るという前提は、ユーザー提示の provider authority に基づく推定です。

Existing generic templates の文体・section convention
実ファイルの文体と粒度を見ていないため、見出しの style は後続で合わせる必要があります。

Date/file naming convention
Artifact instance は YYYY-MM-DD-... を想定していますが、spec-dock が別 convention を持つ場合は合わせる必要があります。

Next follow-up prompt
次の follow-up として、Slice 1 の `spec-dock-requirement-grill/SKILL.md` と Slice 2 の discussion templates を前提に、既存 skill との接続設計をしてください。

対象:
- `spec-dock-issue-execution`
- `spec-dock-implementation-planner`
- `spec-dock-adr-facilitation`
- 必要なら `spec-dock-system-architect`

出力:
- どの skill にどの short guidance を追加すべきか
- 追加しない方がよい skill と理由
- handoff 条件
- circular responsibility を避ける guardrails
- 最小 patch proposal
- follow-up issue に分けるべきか
