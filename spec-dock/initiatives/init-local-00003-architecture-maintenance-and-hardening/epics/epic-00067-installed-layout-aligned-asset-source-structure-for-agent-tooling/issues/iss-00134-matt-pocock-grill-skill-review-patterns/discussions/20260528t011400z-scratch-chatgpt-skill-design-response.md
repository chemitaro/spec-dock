---
種別: scratch
ID: "scratch-20260528t011400z"
タイトル: "ChatGPT skill design response for spec-dock-requirement-grill"
状態: "draft"
作成者: "ChatGPT via Codex"
最終更新: "2026-05-28"
親: ["iss-00134"]
関連: ["scratch-20260528t010300z", "disc-20260528t010000z"]
authority: "raw"
derived_from:
  - "discussions/20260528t010300z-scratch-chatgpt-skill-design-followup-prompt.md"
reflected_to: []
---

# scratch-20260528t011400z ChatGPT skill design response for spec-dock-requirement-grill

## メモ

Proposed SKILL.md draft

配置先:

src/spec_dock/assets/install_root/.agents/skills/spec-dock-requirement-grill/SKILL.md

前提: 以下は Matt Pocock skills の原文コピーではなく、提示された essence を spec-dock の lifecycle / artifact model に合わせて再設計した draft です。追加 Web 確認はしていません。なお、前回アップロードされた source capture file はこの環境では expired 表示のため、今回はユーザーが今回プロンプトで再提示した採用方針と要約を根拠にしています。

Markdown
# spec-dock-requirement-grill

Use this skill to clarify an active spec-dock issue before implementation planning or execution.

This skill turns an under-specified issue into a source-grounded requirement/design/plan update proposal by:
- reading the active spec-dock context first,
- inspecting local repo evidence before asking the human,
- asking at most one human question at a time,
- separating facts, inferences, assumptions, open questions, and decisions,
- recording the clarification path in discussion artifacts,
- proposing updates to requirement/design/plan only after ambiguity is resolved or explicitly labeled,
- routing durable architectural decisions to ADR triage instead of silently embedding them in issue docs.

This skill is not a generic chat interview. It is an issue-local clarification workflow for spec-dock.

## When to use

Use this skill when:
- an active issue has scaffold-like, vague, or incomplete requirement/design/plan docs;
- the user asks for requirement clarification, design wall-kicking, planning analysis, or pre-implementation alignment;
- an implementation plan depends on unresolved scope, artifact authority, lifecycle, validation, or user-facing behavior;
- a discussion needs to become actionable updates to issue docs;
- an issue may require ADR triage before implementation.

Prefer this skill before `spec-dock-issue-execution` when the issue is not yet implementation-ready.

## Do not use this skill for

Do not use this skill as the primary workflow for:
- creating a new initiative;
- creating a new epic;
- implementing code;
- writing final ADRs;
- reviewing finished implementation;
- replacing spec-dock's requirement/design/plan docs with discussion artifacts;
- creating a mandatory root `CONTEXT.md`.

If the task is initiative-level, use `spec-dock-initiative-planning`.
If the task is epic-level, use `spec-dock-epic-planning`.
If the task is ready for code execution, use `spec-dock-issue-execution`.
If an ADR is required, hand off to `spec-dock-adr-facilitation`.

## Core contract

Before asking the human any question:

1. Read the available local spec-dock context.
2. Inspect local repo evidence that can reasonably answer the question.
3. Separate what is known, inferred, unverified, and blocked.
4. Ask the human only for the highest-impact ambiguity that remains.
5. Ask exactly one question.
6. Record why the question matters and which artifacts it affects.

Never ask the human to answer something that local issue docs, parent docs, discussion artifacts, generated state, source files, or tests already answer.

Never treat an unresolved ambiguity as an accepted requirement, design decision, plan step, or ADR decision.

## Context source priority

Use the following sources in order. Later sources may clarify or challenge earlier sources, but do not silently override higher-priority explicit task instructions.

### 1. Current task instruction

Read the user's current request and any explicit constraints for this run.

Examples:
- scope requested by the user;
- whether file edits are requested or only analysis is requested;
- whether Web access is allowed or discouraged;
- requested output format.

### 2. Active issue docs

Read the active issue's own docs first.

Preferred active issue entrance:
- `spec-dock/active/issue/`

If the active symlink entrance is unavailable, use the issue path provided by the user or the current working context.

Expected issue-local docs may include:
- `requirement.md`
- `design.md`
- `plan.md`
- issue metadata or README-like files
- any local status or notes files

Do not assume exact filenames if they are not present. Inspect the directory.

### 3. Parent epic and initiative docs

Read parent context to understand the boundary of the issue.

Preferred active entrances:
- `spec-dock/active/epic/`
- `spec-dock/active/initiative/`

Use parent docs to answer:
- why this issue exists;
- what scope belongs to the epic rather than the issue;
- what source-of-truth or lifecycle constraints already exist;
- what must not be changed by this issue.

Do not modify parent docs unless the current task explicitly asks for it. If parent docs appear stale or incomplete, propose a follow-up instead.

### 4. Issue-local discussions

Read existing discussion artifacts under the active issue.

Expected categories:
- `discussions/research/`
- `discussions/disc/`
- `discussions/interview/`
- `discussions/scratch/`
- `discussions/adr/`

Treat discussion artifacts as evidence and reflection material, not as canonical decisions by themselves.

A discussion artifact becomes authoritative only when adopted into:
- requirement docs;
- design docs;
- plan docs;
- an accepted ADR;
- another explicitly canonical project document.

### 5. Generated agent state

Inspect generated spec-dock state when available.

Expected location:
- `spec-dock/.agent/`

Use generated state for:
- tree navigation;
- dependency awareness;
- current active issue/epic/initiative mapping;
- generated indexes;
- issue relationship hints.

Generated state helps navigation and consistency checks. It should not override canonical docs unless the project explicitly defines it as authoritative for a specific field.

### 6. Relevant source files and tests

Inspect local source files, tests, scripts, templates, installed assets, and provider assets that are directly relevant to the issue.

For agent-tooling asset issues, pay special attention to provider-side authority paths such as:
- `src/spec_dock/assets/install_root/`

Also inspect installed-layout counterparts when relevant, such as:
- `.agents/skills/`
- `.codex/agents/`
- `.codex/prompts/`
- `.github/agents/`
- `spec-dock/templates/`

Use source/tests to answer:
- what already exists;
- what names and conventions are already used;
- how installation/sync behavior works;
- what validation commands are likely relevant;
- whether a proposed artifact path fits the current layout.

### 7. External sources

Do not use external sources by default.

Use external sources only when:
- the current task explicitly allows or requests external verification;
- local source capture is insufficient for a claim that must be verified;
- host policy requires fresh verification for the specific claim.

When external sources are used, clearly separate:
- locally verified facts;
- externally observed facts;
- inferences;
- unverified claims.

## Local inspection rule

Before asking a question, perform a local inspection pass sufficient for the issue.

Minimum inspection checklist:

1. Identify the active issue directory.
2. Read active issue requirement/design/plan or equivalent docs.
3. Read parent epic/initiative docs when available.
4. Search issue-local discussions for the topic.
5. Inspect `.agent` generated state when available.
6. Inspect relevant source files/tests/assets named by the issue.
7. Search for existing skills, agents, templates, scripts, or conventions that match the proposed change.
8. Write down facts, inferences, and unknowns separately.

A human question is allowed only if:
- the answer is not available from local context;
- the ambiguity affects requirement, design, plan, artifact authority, validation, or ADR triage;
- the question is needed to avoid guessing;
- the question can be stated as one decision or one missing fact.

If local inspection is impossible because files are unavailable, say so explicitly and mark the affected claims as unverified.

## Output artifacts

This skill may create or propose the following issue-local artifacts.

Use paths relative to the active issue directory unless the task gives an explicit path.

### Research artifact

Use for source-grounded findings.

Suggested path:
- `discussions/research/YYYY-MM-DD-source-grounding.md`
- `discussions/research/YYYY-MM-DD-requirement-grill-source-grounding.md`

Use this when the clarification depends on local source inspection or external source capture.

Required sections:
- `Facts`
- `Inferences`
- `Unverified`
- `Implications`
- `Questions resolved by source inspection`
- `Human questions still needed`

### Interview artifact

Use for human clarification.

Suggested path:
- `discussions/interview/YYYY-MM-DD-requirement-grill.md`

Required sections:
- `Context`
- `Question log`
- `Resolved answers`
- `Partially resolved answers`
- `Open questions`
- `Affected artifacts`
- `Reflection notes`

Each question entry must include:
- the question;
- why it matters;
- source-grounded context;
- affected artifacts;
- the human answer;
- resolution status.

### Discussion artifact

Use for options, tradeoffs, recommendation, and open questions.

Suggested path:
- `discussions/disc/YYYY-MM-DD-requirement-options.md`
- `discussions/disc/YYYY-MM-DD-design-tradeoffs.md`
- `discussions/disc/YYYY-MM-DD-decision-tree.md`

Required sections:
- `Problem`
- `Options`
- `Tradeoffs`
- `Recommendation`
- `Open questions`
- `Adoption target`

### ADR triage artifact

Use when the clarification reveals a possible architectural decision.

Suggested path:
- `discussions/disc/YYYY-MM-DD-adr-triage.md`

Required sections:
- `Decision candidate`
- `Why this might need an ADR`
- `Why this might not need an ADR`
- `Affected scope`
- `Reversibility`
- `Tradeoff summary`
- `Recommendation`
- `Next step`

Do not write a final ADR from this skill unless the current task explicitly asks for ADR drafting and the handoff criteria for `spec-dock-adr-facilitation` are satisfied.

### Requirement/design/plan patch proposal

This skill may propose patches to:
- requirement docs;
- design docs;
- plan docs.

A patch proposal must distinguish:
- confirmed updates;
- assumptions requiring validation;
- unresolved open questions;
- out-of-scope items;
- follow-up issues;
- ADR candidates.

Do not merge unresolved ambiguity into canonical requirement/design/plan language.

If the current task explicitly asks you to edit files, update the files accordingly while preserving the above distinctions.
If the current task asks only for analysis, provide patch-ready Markdown instead of editing files.

## One-question-at-a-time interview rule

When human clarification is needed:

1. Ask exactly one question.
2. Make it the most blocking or highest-risk question.
3. Avoid compound questions.
4. Do not include a list of additional questions in the same turn.
5. Include only enough context to make the question answerable.
6. Explain why the question matters.
7. State which artifact will change based on the answer.
8. Wait for the answer before asking the next question.

A question may offer options if the options represent one decision.

Good shape:

```markdown
I need one decision before updating the requirement.

Question:
Should this issue define only the shipped `.agents/skills/spec-dock-requirement-grill/SKILL.md` asset, or should it also add discussion templates in the first slice?

Why this matters:
The answer determines whether the first implementation slice is a minimal provider asset or a broader workflow-template change.

Affected artifacts:
- requirement.md
- design.md
- plan.md

Bad shape:

Markdown
Here are five questions:
1. ...
2. ...
3. ...

Do not do this.

Ambiguity guardrails

Do not put unresolved ambiguity into requirement/design/plan as if it were decided.

Use explicit status labels.

Allowed labels:

Confirmed

Source-grounded

Assumption

Needs human confirmation

Open question

Out of scope

ADR candidate

Follow-up

Requirement docs should contain only confirmed or clearly labeled content.

Design docs should not hide unresolved authority, lifecycle, compatibility, or interface questions.

Plan docs should not create implementation steps that depend on unresolved decisions unless the step is explicitly a discovery or clarification step.

Acceptance criteria must be testable or reviewable. Do not write acceptance criteria for behavior that is still undecided.

If a decision is not settled, keep it in:

an interview artifact;

a discussion artifact;

an open question section;

an ADR candidate triage artifact.

Do not promote it to canonical docs until it has been adopted.

ADR triage connection

During clarification, route a decision to ADR triage when it appears to be:

hard to reverse;

surprising to future maintainers;

a real tradeoff rather than an obvious convention;

long-lived;

cross-issue, cross-epic, or cross-repo in impact;

related to source-of-truth boundaries;

related to provider-side vs installed-layout authority;

related to public workflow semantics;

likely to constrain future agent/tooling architecture.

Do not route to ADR triage when the decision is:

a local implementation detail;

a minor naming choice;

a reversible file placement detail;

already dictated by existing docs or conventions;

a one-off issue plan step;

an ordinary test strategy;

a generic note without architectural consequence.

When ADR triage is needed, produce an ADR candidate summary and hand off to spec-dock-adr-facilitation.

Do not silently write architectural decisions into requirement/design/plan without ADR consideration.

Workflow
Step 1: Establish scope

Identify:

active issue path;

issue title or ID;

current phase;

requested output;

whether file edits are allowed;

whether the task is analysis-only.

If scope is missing but enough context exists to proceed, proceed with explicit assumptions.
If active issue cannot be identified, ask one question to identify it.

Step 2: Perform source-grounded pre-read

Read the input sources in priority order.

Produce a compact internal or explicit source-grounding summary:

facts;

inferences;

unverified items;

implications;

already-resolved questions;

remaining ambiguities.

If the task asks for durable artifacts, write or propose a research artifact.

Step 3: Identify blocking ambiguities

List ambiguities that affect:

user-facing or repo-visible outcome;

scope boundary;

artifact path;

source-of-truth;

lifecycle timing;

provider vs installed layout;

compatibility;

validation;

execution order;

ADR need.

Rank ambiguities by implementation risk.

Step 4: Ask the next human question if required

Ask exactly one question only if local inspection cannot resolve the highest-risk ambiguity.

If no human question is required, continue to synthesis.

Step 5: Record interview result

For each human answer:

record the question;

record the answer;

record the rationale;

record affected artifacts;

mark resolution status.

Do not treat a partially answered question as fully resolved.

Step 6: Synthesize options and recommendation

When there are multiple viable approaches, produce a discussion artifact or patch-ready discussion section with:

options;

tradeoffs;

recommendation;

open questions;

adoption target.

Use spec-dock vocabulary and paths.

Step 7: Propose requirement/design/plan updates

Prepare patch-ready updates.

Requirement proposal should clarify:

problem;

goal;

non-goals;

scope boundary;

acceptance criteria;

source-grounded constraints;

unresolved questions, if any.

Design proposal should clarify:

selected approach;

artifact paths;

source-of-truth relationships;

lifecycle integration;

discussion artifact relationship;

compatibility;

validation strategy;

ADR candidates.

Plan proposal should clarify:

implementation slices;

dependency order;

HITL vs AFK work;

tests or validation commands;

done criteria.

Step 8: Run ADR triage

Check whether any recommendation should become an ADR candidate.

If yes:

produce ADR triage summary;

do not finalize ADR unless explicitly requested;

hand off to spec-dock-adr-facilitation.

Step 9: Completion summary

Finish with:

what was resolved;

what artifacts were created or proposed;

what requirement/design/plan patches are ready;

what remains unresolved;

whether implementation can start;

next recommended skill or phase.

Stop conditions

Stop the grilling loop when one of these is true:

Ready for synthesis

Stop asking questions and synthesize when:

all high-impact ambiguities are resolved;

remaining ambiguities are low-risk or explicitly out of scope;

requirement/design/plan can be updated without guessing;

ADR candidates, if any, have been identified;

implementation slices can be defined.

Need human answer

Stop and ask one question when:

local inspection cannot resolve the top blocking ambiguity;

proceeding would require guessing;

the ambiguity affects requirement/design/plan/ADR validity.

Need handoff

Stop and hand off when:

the issue is actually initiative-level or epic-level;

a final ADR is needed;

implementation should begin;

the user requested a different workflow;

required files are unavailable and cannot be inspected.

Done

This skill is complete when it has produced one or more of:

a source-grounding research artifact or equivalent section;

an interview artifact or recorded Q/A;

a discussion artifact with options/tradeoffs/recommendation;

requirement/design/plan patch proposals;

an ADR candidate triage result;

a clear statement that no further grilling is needed.

Completion criteria

A successful run must satisfy all applicable criteria:

Local context was inspected before human questioning.

No source-answerable question was asked to the human.

Human questions, if any, were asked one at a time.

Facts, inferences, assumptions, and unresolved questions were separated.

Discussion artifacts were treated as reflection/adoption material, not as canonical source of truth.

Requirement/design/plan updates did not contain hidden unresolved ambiguity.

ADR candidates were identified but not over-produced.

The next step is clear: continue clarification, update docs, run ADR facilitation, plan vertical slices, or execute the issue.

Prohibitions

Do not:

require or create a root CONTEXT.md as the canonical project source;

copy external skill text verbatim unless copy policy has been verified;

ask several human questions at once;

ask the human for facts that local files can answer;

treat discussion artifacts as canonical decisions without adoption;

hide assumptions inside acceptance criteria;

write final ADRs without ADR facilitation or explicit instruction;

mutate parent initiative/epic docs without explicit instruction;

mutate provider-side assets and installed-layout assets inconsistently;

skip source-of-truth checks for asset-installation issues;

begin implementation when requirement/design/plan are still blocked by unresolved ambiguity.


---

# Design notes

## 1. Skill の中心責務

`spec-dock-requirement-grill` は、単なる壁打ち skill ではなく、**active issue を implementation-ready に近づける clarification workflow** として設計するのがよいです。

中心の変換はこれです。

```text
曖昧な issue scaffold
  -> local source inspection
  -> one-question-at-a-time clarification
  -> research / interview / disc / ADR candidate
  -> requirement/design/plan patch proposal

この skill は、質問すること自体が目的ではありません。目的は、人間に聞くべきことを最小化し、聞いた結果を spec-dock の artifact model に正しく落とすことです。

2. CONTEXT.md を mandatory にしない設計

Matt Pocock 側の grill-with-docs の essence は「docs-aware clarification」ですが、spec-dock では root CONTEXT.md を新しい正本にしない方針なので、draft では context source set を次に分解しています。

current task instruction
active issue docs
parent epic / initiative docs
issue-local discussions
spec-dock/.agent generated state
relevant source/tests/assets
external sources only when allowed or required

これにより、CONTEXT.md 的な役割を 単一ファイルではなく spec-dock の既存構造に対応づけています。

3. Discussion artifact の扱い

skill draft では、discussion artifact を source of truth にしていません。

関係は次です。

discussion artifacts
  = evidence / reflection / options / interview history

canonical adoption targets
  = requirement docs
  = design docs
  = plan docs
  = accepted ADRs

この関係を明記した理由は、interview や disc に書かれた暫定案が、そのまま requirement/design/plan の決定として扱われるのを防ぐためです。

4. “Ask one question” の厳格さ

one-question-at-a-time は workflow の品質に直結します。

ただし、単に「1問だけ」とすると低品質な質問になる可能性があるため、draft では各質問に次を要求しています。

question
why this matters
source-grounded context
affected artifacts
resolution status

これにより、質問が artifact update に接続されます。

5. “local inspection before interview” の明文化

この skill では、質問前に local inspection を contract 化しています。

特に spec-dock の active epic は provider-side authority と installed layout の整合がテーマなので、agent-tooling asset issue では次のような path を確認対象に含めています。

src/spec_dock/assets/install_root/
.agents/skills/
.codex/agents/
.codex/prompts/
.github/agents/
spec-dock/templates/

この設計により、「ユーザーに聞けば早い」ではなく、「repo で確認できることは先に確認する」という運用になります。

Responsibility boundaries
spec-dock-requirement-grill vs spec-dock-initiative-planning
項目	spec-dock-requirement-grill	spec-dock-initiative-planning
主対象	active issue	initiative
粒度	issue-local clarification	strategic / program-level planning
主な成果物	issue requirement/design/plan patch proposal、issue-local discussions	initiative requirement/design/plan、initiative scope
触ってよい範囲	原則 active issue。parent docs は読む。変更は提案まで。	initiative docs
escalation 条件	issue の目的や scope が initiative-level に見える場合	N/A

境界ルール:

If clarification changes the initiative goal, stop and hand off to initiative planning.
spec-dock-requirement-grill vs spec-dock-epic-planning
項目	spec-dock-requirement-grill	spec-dock-epic-planning
主対象	active issue	epic
粒度	issue implementation-readiness	cross-issue structure / dependency / architecture
主な成果物	issue docs patch proposal	epic docs and issue breakdown
dependency handling	issue-local plan dependency awareness	cross-issue dependency design
escalation 条件	clarification reveals missing epic boundary or new sibling issue need	N/A

境界ルール:

If the answer requires changing epic decomposition, do not silently rewrite issue scope. Propose epic-planning follow-up.
spec-dock-requirement-grill vs spec-dock-issue-execution
項目	spec-dock-requirement-grill	spec-dock-issue-execution
主対象	before execution	execution
目的	ambiguity removal	implementation
主な成果物	clarified docs and patch proposals	code/docs changes, tests, validation
実装	原則しない	する
handoff 条件	requirement/design/plan が implementation-ready	N/A

境界ルール:

If unresolved ambiguity affects implementation behavior, do not start issue execution.
If remaining ambiguity is low-risk and explicitly labeled, issue execution may proceed with a bounded assumption.
spec-dock-requirement-grill vs spec-dock-adr-facilitation
項目	spec-dock-requirement-grill	spec-dock-adr-facilitation
主対象	ADR candidate discovery	ADR drafting / facilitation
目的	ADR が必要か判定する	ADR として decision record を作る
主な成果物	ADR triage summary	ADR artifact
判断基準	hard-to-reverse / surprising / real tradeoff / long-term impact	ADR lifecycle and decision documentation
禁止	final ADR を勝手に作らない	N/A

境界ルール:

Requirement grill can say “this looks like an ADR candidate.”
It should not finalize the ADR unless explicitly instructed and ADR facilitation criteria are met.
Artifact contract
Input sources priority
Priority	Source	Role	Notes
1	Current task instruction	Run-specific authority	出力形式、制約、編集可否を決める。
2	Active issue docs	Primary issue context	requirement/design/plan scaffold を読む。
3	Parent epic / initiative docs	Boundary context	issue の scope と上位制約を読む。
4	Issue-local discussions	Evidence and reflection	source of truth ではない。adoption が必要。
5	.agent generated state	Navigation / dependency state	canonical docs を無言で上書きしない。
6	Relevant source/tests/assets	Implementation facts	repo で確認できることはここで確認する。
7	External sources	Exceptional verification	今回の方針ではデフォルト使用しない。
Output artifacts
Artifact	作成/更新可否	Canonical?	Purpose
discussions/research/*source-grounding*.md	可	No	local inspection の facts/inferences/unverified を分離する。
discussions/interview/*requirement-grill*.md	可	No	human Q/A と rationale を残す。
discussions/disc/*requirement-options*.md	可	No	options/tradeoffs/recommendation を整理する。
discussions/disc/*design-tradeoffs*.md	可	No	design alternatives を整理する。
discussions/disc/*adr-triage*.md	可	No	ADR candidate を判定する。
requirement.md	明示指示があれば更新。通常は patch proposal。	Yes	採用済み requirement。
design.md	明示指示があれば更新。通常は patch proposal。	Yes	採用済み design。
plan.md	明示指示があれば更新。通常は patch proposal。	Yes	採用済み execution plan。
discussions/adr/*.md	原則 handoff。明示指示があれば ADR facilitation 経由。	Yes, if accepted	長期 architecture decision。
Patch proposal status labels

requirement/design/plan に反映する場合は、次の status label を使う想定です。

Confirmed
Source-grounded
Assumption
Needs human confirmation
Open question
Out of scope
ADR candidate
Follow-up

最重要 guardrail:

Open question を acceptance criteria に変換しない。
Assumption を confirmed design decision のように書かない。
Discussion recommendation を adopted decision のように扱わない。
First implementation slice
推奨する最初の slice

最初は skill asset 1個だけを provider-side に追加する slice がよいです。

理由:

active epic の provider-side authority 方針に合う。

CLI phase、Codex agent、discussion templates まで同時追加すると scope が膨らむ。

SKILL.md 単体でも既存 consultant / deep-consultant / spec-manager などから参照可能。

Matt Pocock 原文コピーの license/copy policy 未確認リスクを最小化できる。

後続で template / agent / command を追加しやすい。

Slice name
Slice 1: Add provider-side spec-dock-requirement-grill skill asset
Files to add
src/spec_dock/assets/install_root/.agents/skills/spec-dock-requirement-grill/SKILL.md
Files to avoid in slice 1
.agents/skills/spec-dock-requirement-grill/SKILL.md
.codex/agents/requirement-grill-facilitator.md
spec-dock/templates/discussions/interview/grill-session.md
spec-dock/templates/discussions/research/source-grounding.md
spec-dock/templates/discussions/disc/decision-tree.md
spec-dock/templates/discussions/disc/adr-triage.md
CLI command additions
installer behavior changes

Installed-layout files may appear after sync, but the source commit should primarily modify provider authority unless the repo’s dogfooding convention requires checked-in installed assets too. That convention is 未検証.

Acceptance criteria
Markdown
- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-requirement-grill/SKILL.md` exists.
- The skill does not require a root `CONTEXT.md`.
- The skill defines context source priority.
- The skill requires local inspection before human questioning.
- The skill enforces one-question-at-a-time interview.
- The skill defines allowed output artifacts.
- The skill states that discussion artifacts are not canonical until adopted.
- The skill prevents unresolved ambiguity from being written into requirement/design/plan as confirmed content.
- The skill defines ADR triage criteria and handoff to `spec-dock-adr-facilitation`.
- The skill defines stop conditions and completion criteria.
- The skill does not copy Matt Pocock skills wording verbatim.
Suggested validation
./spec-dock/scripts/spec-dock sync
./spec-dock/scripts/spec-dock validate

未検証: 上記 commands がこの exact asset addition に対して必要十分かは、現在の repo validation implementation を見ていないため後続確認対象です。

Follow-up slices
Slice 2: Add discussion templates
src/spec_dock/assets/install_root/spec-dock/templates/discussions/research/source-grounding.md
src/spec_dock/assets/install_root/spec-dock/templates/discussions/interview/grill-session.md
src/spec_dock/assets/install_root/spec-dock/templates/discussions/disc/decision-tree.md
src/spec_dock/assets/install_root/spec-dock/templates/discussions/disc/adr-triage.md
Slice 3: Add optional Codex agent wrapper
src/spec_dock/assets/install_root/.codex/agents/requirement-grill-facilitator.md
Slice 4: Integrate into existing skill references

Potentially update existing skills to mention this one as a pre-execution clarification option:

spec-dock-issue-execution
spec-dock-implementation-planner
spec-dock-adr-facilitation

This should be done only after checking existing skill wording and avoiding responsibility overlap.

Risks / unresolved questions
Risks
Risk	Why it matters	Mitigation
Skill becomes too broad	It may overlap initiative/epic planning, ADR facilitation, and issue execution.	Keep it focused on issue-local clarification and patch proposals.
Agent asks too many questions	Violates the core one-question-at-a-time principle and creates user fatigue.	Enforce a strict single-question rule and ranking of blocking ambiguity.
Discussion artifacts become shadow source-of-truth	Leads to conflicting decisions between disc and requirement/design/plan.	Explicit adoption rule: discussions are not canonical until reflected.
Unresolved ambiguity leaks into plan	Implementation may proceed on hidden assumptions.	Require status labels and forbid undecided acceptance criteria.
ADR overproduction	Every clarification could become an ADR candidate.	Use hard-to-reverse / surprising / real-tradeoff / long-term impact criteria.
Provider vs installed asset confusion	Active epic requires provider authority under install_root.	First slice modifies provider-side asset only.
Existing skill format mismatch	Existing spec-dock skills may have a convention not shown here.	Adjust heading/frontmatter style after inspecting existing skill files.
License/copy risk	Matt Pocock exact text reuse policy is未確認.	Use original spec-dock wording; do not copy source text verbatim.
Unresolved questions

Existing skill format
この draft は generic SKILL.md 形式です。既存 spec-dock skills に front matter、section naming、language convention がある場合は合わせる必要があります。

Dogfooding installed asset policy
provider-side だけを commit するのか、dogfooding installed .agents/skills/... も commit するのかは未確認です。

Issue doc filenames
requirement.md / design.md / plan.md を想定していますが、実 repo の exact naming は未確認です。

Template location convention
discussion template を spec-dock/templates/discussions/<category>/... に分けるか、flat に置くかは既存 template layout 確認が必要です。

Whether to add issue clarify command
今回の first slice では入れないのが安全です。workflow が定着してから CLI command 化する方が低リスクです。

Next follow-up prompt
次の follow-up として、今回の `spec-dock-requirement-grill/SKILL.md` draft を前提に、Slice 2 の discussion templates を実際に設計してください。

対象:
- `source-grounding.md`
- `grill-session.md`
- `decision-tree.md`
- `adr-triage.md`

制約:
- discussion artifact は source of truth ではない。
- facts / inference / unverified / implications を分ける。
- interview は one-question-at-a-time に対応する。
- decision-tree は options / tradeoffs / recommendation / open questions を分ける。
- adr-triage は final ADR ではなく candidate 判定に限定する。
- spec-dock provider-side path に入れる前提で artifact path も提案する。
