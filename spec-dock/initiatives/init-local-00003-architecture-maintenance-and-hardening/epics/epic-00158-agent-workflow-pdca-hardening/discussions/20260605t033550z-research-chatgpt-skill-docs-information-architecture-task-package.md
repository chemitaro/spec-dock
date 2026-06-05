---
type: research
status: completed
source: chatgpt-use task package
created_at: "2026-06-05T03:35:50Z"
epic_id: "epic-00158"
title: "ChatGPT skill docs information architecture task package"
answer_now_allowed: false
---

# ChatGPT Skill Docs Information Architecture Task Package

## Purpose

Use ChatGPT `じっくり思考 Pro` to evaluate the user's hypothesis:

- The current SpecDock skills may be too thin.
- Critical workflow steps are buried in multiple docs.
- If an agent does not read those docs, it does not know the required workflow.
- Better split may be:
  - Skills: concise but explicit operational workflow that agents must follow.
  - Docs: conceptual meaning, field semantics, templates, detailed explanations, reference material.

This is a ChatGPT reasoning task, not Deep Research.

## Strict Wait Policy

- Do not select `今すぐ回答` / `Answer now`.
- Wait for full long-running reasoning completion.
- If `今すぐ回答` appears, leave it untouched and continue polling.
- Do not use any prior ChatGPT output that was obtained via or contaminated by `今すぐ回答`.

## Repository

- Repository URL: <https://github.com/chemitaro/spec-dock>
- Local worktree: `/Users/iwasawayuuta/.codex/worktrees/8d9b/spec-dock`
- Active epic: `epic-00158 Agent Workflow PDCA Hardening`

## Local Facts

Current hub skill says:

- Keep `spec-dock/docs/` as source of truth; skills stay concise.
- Put spec authoring rules and workflow explanations in `spec-dock/docs/` and route through these skills.
- Use `workflow_spec_authoring.md` as source of truth.
- Leaf skills own workflow details.

Current issue-planning skill includes some important workflow bullets:

- Read `workflow_issue.md`, `workflow_spec_authoring.md`, `workflow_clarification.md`, `phase_plan_issue.md`, and `authoring/issue-plan.md`.
- Keep canonical `requirement.md` / `design.md` / `plan.md` / `report.md` main-orchestrator-owned.
- Do not move from requirement to design, design to plan, or plan to execution until a fresh `spec-reviewer` returns `review_status: pass`.
- Record each `Spec Authoring Gate` in issue `report.md`.

However, detailed operational behavior is mostly in docs, including:

- `workflow_spec_authoring.md`: authoring lifecycle steps, promotion gates, delegated draft policy, evidence adoption ledger, bounded delegation.
- `workflow_issue.md`: issue start/finish, issue execution contract, implementation delegation gate, step closure, reviewer gates, completion conditions.
- `phase_plan_issue.md` and `authoring/issue-plan.md`: plan field semantics and executable step schema.

Representative workflow_doc facts:

- Authoring sequence: `requirement -> spec-reviewer pass -> design -> spec-reviewer pass -> plan -> spec-reviewer pass -> downstream handoff`.
- Missing/stale/failed/unavailable/denied/waived/provisional reviewer results are not pass.
- Sub-agent-created drafts are discussion evidence only until adopted by the main orchestrator and reviewed.
- The authoring lifecycle says agents should inspect target scope, read authoring docs/workflow docs, separate investigations/questions into `discussions/`, update artifact, run fresh `spec-reviewer`, fix failures, and record gate evidence.
- Issue execution requires checking approved planning artifacts and report evidence before implementation, using implementation delegation gates, per-step review, final QA/code/spec review, PR delivery and merge preparation evidence, and not claiming complete until all completion evidence exists.

## Prompt To Submit

You are GPT-5.5 Pro / the strongest available deep reasoning model, acting as a senior agent-workflow designer for SpecDock.

Important constraints:

- Do not rely on prior ChatGPT memory or ordinary history.
- Do not use or assume any output from a prior thread that used `今すぐ回答`.
- Use only this prompt and, if useful, public repository context from <https://github.com/chemitaro/spec-dock>.
- If repository inspection is incomplete, mark that uncertainty.

Task:
Evaluate this hypothesis and turn it into a practical improvement direction:

> SpecDock currently places too much agent-critical workflow in docs and keeps skills too thin. Because models reliably read the skill first but may skip linked docs, agent-mandatory workflow steps should be stated in skills. Docs should remain source-of-truth for concepts, field meanings, templates, and detailed explanations. Skills should then explicitly instruct which docs to read when producing a specific artifact.

Context:

- Current hub skill says skills stay concise and workflow explanations live in docs.
- Current leaf skills include a few key bullets, but many operational requirements are distributed across `workflow_spec_authoring.md`, `workflow_issue.md`, phase playbooks, and authoring docs.
- The user is not primarily asking for stricter runtime gates. The suspected root cause is model readability/compliance: the agent may not read enough docs to know the expected workflow.

Please produce:

1. A clear judgment on whether the hypothesis is sound.
2. The recommended information architecture:
   - what belongs in skills;
   - what belongs in workflow docs;
   - what belongs in authoring field docs;
   - what belongs in templates.
3. A concrete policy for "agent-mandatory workflow steps" versus "concept/reference details".
4. A risk analysis:
   - skill bloat;
   - duplicated truth between skill and docs;
   - stale skill summaries;
   - context overload;
   - compliance failures when docs are skipped.
5. Recommended safeguards to keep skills compact but operationally sufficient.
6. How this should change the current `spec-driven-tdd-workflow`, `spec-dock-issue-planning`, and `spec-dock-issue-execution` skills.
7. A small PDCA plan: first 3-5 issues to improve skills/docs iteratively without a big rewrite.
8. Success criteria and lightweight empirical tests for whether agents now follow the workflow better.

Bias toward practical, small, dogfoodable changes. Avoid generic prompt-engineering advice. Treat this as a SpecDock epic planning input.

## Expected Output Handling

- Save the completed ChatGPT analysis as a separate `research` report under this epic's `discussions/`.
- Update this package with the ChatGPT thread URL, visible model/reasoning selection, completion status, and report path after retrieval.

## Submission Record

- Submitted at: `2026-06-05T03:39Z` (approximate; exact seconds not captured)
- ChatGPT Project: `for codex app`
- Thread URL: <https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a224514-06f4-83a3-abc8-03ab87de881f>
- Visible model / reasoning selector before submission: `じっくり思考 Pro`
- Status: completed
- Wait policy: `今すぐ回答` must not be selected.
- `今すぐ回答` / `Answer now`: not selected.
- Report path: `spec-dock/active/epic/discussions/20260605t035200z-research-chatgpt-skill-docs-information-architecture-report.md`
