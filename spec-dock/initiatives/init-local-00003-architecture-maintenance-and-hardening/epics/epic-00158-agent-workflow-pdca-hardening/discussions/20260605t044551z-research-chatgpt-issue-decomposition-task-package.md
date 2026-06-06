---
種別: research
ID: "20260605t044551z-research"
タイトル: "ChatGPT Issue Decomposition for Skill Docs Workflow Spine"
状態: "completed"
作成者: "iwasawayuuta"
最終更新: "2026-06-05"
親: ["epic-00158"]
関連:
  - "iss-00159"
authority: "evidence"
source: "chatgpt-use task package"
answer_now_used: false
thread_url: "https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a22552c-1a04-83a9-b39b-b5eeb6ff7129"
report_path: "spec-dock/active/epic/discussions/20260605t050037z-research-chatgpt-issue-decomposition-report.md"
---

# 20260605t044551z-research ChatGPT Issue Decomposition for Skill Docs Workflow Spine

## 実行状態

- thread_url: "https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a22552c-1a04-83a9-b39b-b5eeb6ff7129"
- project_boundary: "Codex-only Project URL under for codex app"
- model_visible: "じっくり思考 Pro"
- state: "completed"
- answer_now_used: false
- visible_state:
  - "Prompt was submitted in a new Project conversation, but ChatGPT displayed a request-frequency limit notice: リクエストが多すぎます"
  - "今すぐ回答 was visible and was not clicked"
  - "After the first cooldown check, the same thread showed research/progress text and 回答を仕上げ中, so the thread is treated as generating until completion/error is confirmed"
  - "Final assistant response was present; stop control absent; thinking text absent; stable after second check"
- next_action:
  - "Use the report as evidence for issue decomposition synthesis; do not treat it as canonical backlog until adopted into discussion or issue docs"
- completed_at: "2026-06-05T05:00:37Z"
- report_path: "spec-dock/active/epic/discussions/20260605t050037z-research-chatgpt-issue-decomposition-report.md"

## 目的

ChatGPT `GPT-5.5 Pro` / strongest visible model に、`epic-00158 Agent Workflow PDCA Hardening` の次の PDCA issue backlog を具体化してもらう。

抽象方針は既に見えた:

- agent が最初に守るべき mandatory workflow spine は skill に薄く置く。
- artifact の意味、field semantics、schema、詳細 policy、例、edge cases は docs に置く。
- first issue は `iss-00159` として `spec-dock-issue-planning` skill に限定する。

今回の依頼は、ここからさらに具体的に「どの修正項目を、どの issue に分割すべきか」を徹底的に洗い出すことである。

## Repo / Branch

- GitHub repo URL: `https://github.com/chemitaro/spec-dock`
- Current local branch: `codex/epic-00158-agent-workflow-pdca-hardening`
- Intended branch URL: `https://github.com/chemitaro/spec-dock/tree/codex/epic-00158-agent-workflow-pdca-hardening`
- Latest local commit containing current analysis reports: `75ca36486de64bb4819d0dd8eaa0329a67e1024d`
- GitHub issue already created: `https://github.com/chemitaro/spec-dock/issues/159`

If the branch URL or commit is not visible from GitHub, rely on the supplied excerpts below and explicitly mark any conclusion that depends on uninspected repository state.

## 現在の状況

- Active epic:
  - `epic-00158 Agent Workflow PDCA Hardening`
- Active issue:
  - `iss-00159 Make Issue Planning Skill Expose Mandatory Authoring Gates`
- `iss-00159` scope:
  - first small implementation issue.
  - target only `spec-dock-issue-planning` skill.
  - no runtime gate / CLI / validation / hub rewrite / issue execution rewrite / harness in this first issue.
- Dirty worktree note:
  - Two Deep Research task packages may be independently updated in parallel; ignore them unless relevant to issue decomposition.

## 既に得られた中核知見

### Skill / docs boundary

Skills should be agent runbooks, not manuals.

Skills should answer:

- what must the agent do next;
- what must it read now;
- when must it stop;
- what evidence must it record;
- what exit condition permits handoff.

Docs should answer:

- exact lifecycle policy;
- command semantics;
- field meanings;
- schemas;
- examples;
- edge cases;
- long policy;
- historical rationale.

Template files should remain scaffolds, not compliance authorities.

### Non-skippable invariants to expose in skills

- Spec authoring advances only:
  - requirement -> fresh `spec-reviewer` pass -> design -> fresh `spec-reviewer` pass -> plan -> fresh `spec-reviewer` pass -> downstream handoff.
- Missing / stale / failed / unavailable / denied / waived / provisional reviewer output is not pass.
- Canonical `requirement.md`, `design.md`, `plan.md`, and `report.md` are main-orchestrator-owned.
- Delegated drafts, worker notes, discussions, and research are evidence only until adopted into canonical artifacts and recorded in `report.md`.
- Unresolved requirement / design / plan ambiguity stops the current path and returns to clarification or the relevant authoring phase.
- Issue execution starts only after issue-specific, non-template, reviewer-pass artifacts and executable `plan.md` handoff exist.
- Issue execution is step-by-step, with actual evidence in `report.md`.
- Completion is not `issue finish` alone; completion requires validation / review / docs / final gates / PR delivery evidence before lifecycle closure.
- Shipped docs / templates / skills / workflow text changes route through doc-writing workflow.

### Recommended generic skill section structure

For workflow skills:

- `Use this skill when`
- `Source-of-truth boundary`
- `Must read before acting`
- `Entry gate`
- `Must-follow checklist`
- `Stop and return conditions`
- `Evidence to record`
- `Exit / handoff criteria`
- `Keep out of this skill`

Use this writing pattern:

`Must do X. Read doc Y for exact schema/details. Stop if Z. Record evidence in W.`

## Current provider-side skill facts

Source of truth for installed agent-tooling assets:

`src/spec_dock/assets/install_root/.agents/skills/`

Dogfooding mirror may also need updates:

`.agents/skills/`

Relevant current skill excerpts:

### `spec-driven-tdd-workflow`

- Current hub says:
  - `spec-dock/docs/` is source of truth; skills stay concise.
  - templates are minimum scaffolds, not compliance targets.
  - spec authoring rules and workflow explanations live in docs.
  - fresh `spec-reviewer` pass is required.
  - missing / stale / failed / unavailable / denied / waived / provisional reviewer results are not pass.
  - leaf skills own workflow details.
- Potential issue:
  - It may still imply that workflow explanations live in docs rather than mandatory workflow spine living in leaf skills.
  - It is a dense bullet list; routing and non-negotiable invariants could be visually clearer.

### `spec-dock-issue-planning`

Current skill is short:

- routes to `workflow_issue.md`, `workflow_spec_authoring.md`, `workflow_clarification.md`, `phase_plan_issue.md`, `authoring/issue-plan.md`;
- states canonical artifacts are main-orchestrator-owned;
- states delegated drafts are evidence only;
- states fresh `spec-reviewer` pass required before phase promotion;
- states unresolved gaps return to clarification / authoring phase;
- states `Spec Authoring Gate` evidence goes to `report.md`.

Potential issue:

- It lacks visible step-by-step mandatory workflow.
- It is first target in `iss-00159`.

### `spec-dock-issue-execution`

Current skill is more runbook-like already:

- entry readiness;
- reviewer-pass planning artifacts;
- non-executable plan as plan gap;
- unresolved gaps return to clarification / authoring;
- `plan.md` as executable workflow contract;
- `report.md` as evidence ledger and decision ledger;
- delegation obligations;
- completion / PR merge-preparer reminders;
- runtime command reminders.

Potential issue:

- It may be dense and flat.
- It might need visual sectioning and stronger entry/final gate surfacing rather than more policy.
- It must not duplicate issue-plan schema or workflow_issue long policy.

### `spec-dock-clarification`

Current skill already has a clear concise workflow:

- read source first;
- do not ask the user about local-context-answerable facts;
- ask at most one essential question at a time through orchestrator;
- create unanswered interview artifact for important decisions;
- support analysis-only / draft-only mode;
- adoption through canonical docs/report in authoring mode.

Potential issue:

- It may need alignment wording for when clarification returns to issue planning / prior phase.
- It may already be good enough and should not be over-expanded.

### `spec-dock-epic-planning` / `spec-dock-initiative-planning`

Current skills are short:

- reuse/update existing node first;
- primary workflow doc;
- spec authoring workflow doc;
- fresh `spec-reviewer` pass before decomposition;
- report Spec Authoring Gate evidence;
- do not default to create/import.

Potential issue:

- They may need compact parity with issue planning:
  - reuse-before-create;
  - phase gates;
  - decomposition handoff;
  - evidence obligations;
  - not issue-internal TDD cadence.

## `iss-00159` current boundary

Already created issue:

`iss-00159 Make Issue Planning Skill Expose Mandatory Authoring Gates`

Current scope:

- Add mandatory workflow spine to `spec-dock-issue-planning`.
- Put a short named section near the top, such as `Mandatory Issue Authoring Workflow`.
- Make visible:
  - requirement -> fresh `spec-reviewer` pass -> design -> fresh `spec-reviewer` pass -> plan -> fresh `spec-reviewer` pass -> execution handoff.
  - non-pass reviewer states are not pass.
  - minimal `fresh` definition.
  - canonical ownership / delegated draft evidence boundary.
  - unresolved gaps return to clarification / prior phase.
  - non-executable issue `plan.md` blocks execution handoff.
  - doc routing for lifecycle / authoring / clarification / issue-plan details.
- Non-scope:
  - runtime gate;
  - CLI command;
  - validation logic;
  - workflow policy changes;
  - hub skill rewrite;
  - issue execution skill rewrite;
  - epic / initiative skill parity;
  - manual compliance harness;
  - `gate status --json`.

## ChatGPT への依頼

You are GPT-5.5 Pro / the strongest available deep reasoning model, acting as a senior product architect and instruction-design lead for coding-agent workflows.

Please produce a concrete issue decomposition plan for `epic-00158`.

Primary question:

Do we already have enough information to split the next fixes into concrete issues? If yes, propose the issue backlog. If not, identify exactly what additional information is missing and how to gather it.

Please assume `iss-00159` already exists and should remain the first small issue unless you find a serious reason to change that.

## Required output

Please answer in Japanese with these sections:

1. 情報充足度
   - Is the available information enough for issue decomposition?
   - What is still uncertain?
   - Which uncertainties block issue creation vs can be handled inside each issue?
2. 修正項目の全体棚卸し
   - Exhaustively list concrete correction items.
   - Group by skill/docs/runtime/harness/templates/reviewer workflow.
3. 推奨 issue backlog
   - For each issue:
     - proposed title in English, ASCII-friendly for SpecDock/GitHub;
     - objective;
     - scope;
     - non-scope;
     - affected files;
     - dependencies;
     - acceptance criteria;
     - verification method;
     - risk / why this should be separate;
     - priority and sequencing.
4. `iss-00159` との境界
   - What stays in `iss-00159`?
   - What must be follow-up?
   - What should not be mixed into it?
5. 最小 PDCA sequence
   - Recommend the smallest sequence of 3-6 issues that produces measurable improvement quickly.
6. 大きすぎる issue の分割提案
   - Identify any tempting issues that are too broad and split them.
7. 採用しない方がよい案
   - Runtime gate first?
   - Copy docs into skills?
   - Rewrite all skills at once?
   - Any other anti-patterns.
8. SpecDock issue creation notes
   - Titles should satisfy a strict ASCII title constraint if needed.
   - Which issues should initially be docs-only / skill-only / harness-only.
   - Which ones need requirement/design/plan versus discussion-only bootstrap.

Quality bar:

- Be concrete enough that Codex can create the issues without another broad research pass.
- Do not invent repository facts not provided or not visible from the GitHub URL.
- Distinguish confirmed facts from assumptions.
- Keep `iss-00159` small.
- Preserve the principle: skill contains mandatory operational workflow; docs contain meaning/schema/detail.
- Do not recommend implementation changes before issue planning.
- Do not use ordinary ChatGPT memory, prior chats, or hidden Project history. If anything depends on outside memory, flag it.
