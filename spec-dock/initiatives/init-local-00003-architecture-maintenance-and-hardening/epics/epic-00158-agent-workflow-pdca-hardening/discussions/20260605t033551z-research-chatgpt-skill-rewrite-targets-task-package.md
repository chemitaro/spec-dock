---
type: research
status: completed
source: chatgpt-use task package
created_at: "2026-06-05T03:35:51Z"
epic_id: "epic-00158"
title: "ChatGPT skill rewrite targets task package"
answer_now_allowed: false
---

# ChatGPT Skill Rewrite Targets Task Package

## Purpose

Use ChatGPT `じっくり思考 Pro` to propose concrete skill-level rewrites for the SpecDock workflow skills, based on the user's new hypothesis that mandatory procedures should live in skills while conceptual details remain in docs.

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

## Current Skill Excerpts

Hub skill: `.agents/skills/spec-driven-tdd-workflow/SKILL.md`

- "Keep `spec-dock/docs/` as the source of truth; skills stay concise."
- "Put spec authoring rules and workflow explanations in `spec-dock/docs/` and route through these skills."
- "Route once the main output is clear; leaf skills own the workflow details."
- Quick reminders include: inspect existing nodes before creating, put boundary rationale in discussions, record gates in `report.md`, use `spec-dock/active/context-pack.md`, and use `./spec-dock/scripts/spec-dock ...`.

Issue planning skill: `.agents/skills/spec-dock-issue-planning/SKILL.md`

- Use for issue requirement/design/plan planning.
- Read `workflow_issue.md`, `workflow_spec_authoring.md`, `workflow_clarification.md`, `phase_plan_issue.md`, `authoring/issue-plan.md`.
- Keep canonical docs main-orchestrator-owned.
- Do not move phases until fresh `spec-reviewer` pass.
- Return unresolved gaps to clarification or authoring.
- Record each authoring gate in `report.md`.

Issue execution skill: expected to be the entry for approved planning artifacts and issue execution. Related workflow docs require:

- Verify approved / reviewer-pass planning artifacts before implementation.
- Execute plan steps in order.
- Each implementation step has implementation delegation decision, bounded batch, verification, report update, step reviewer gate, fix/re-review loop, commit, clean check.
- Runtime/code/tests/scaffold behavior should go to `dev-coder`; shipped docs/templates/skills/workflow text should go to `doc-writer`.
- Required reviewer gates are not satisfied by unavailable/denied/waived/provisional states.
- Do not claim complete until report contains required evidence and final gates pass.

## Prompt To Submit

You are GPT-5.5 Pro / the strongest available deep reasoning model, acting as a senior prompt/skill editor for SpecDock.

Important constraints:

- Do not rely on prior ChatGPT memory or ordinary history.
- Do not use or assume any output from a prior thread that used `今すぐ回答`.
- Use only this prompt and, if useful, public repository context from <https://github.com/chemitaro/spec-dock>.
- If repository inspection is incomplete, mark that uncertainty.

Task:
Propose concrete rewrites for SpecDock's workflow skills so that model-mandatory operational procedure is visible in the skill itself, while docs remain the detailed conceptual/reference authority.

The target skills are:

- `spec-driven-tdd-workflow`
- `spec-dock-issue-planning`
- `spec-dock-issue-execution`
- optionally `spec-dock-epic-planning` / `spec-dock-initiative-planning` if the same pattern should apply.

Please produce:

1. A recommended section structure for each skill.
2. A compact "must follow" workflow checklist for:
   - issue planning;
   - issue execution;
   - epic/initiative planning if needed.
3. A "read these docs when..." matrix:
   - when creating/updating `requirement.md`;
   - when creating/updating `design.md`;
   - when creating/updating `plan.md`;
   - when executing an issue;
   - when updating shipped docs/templates/skills/workflow text.
4. Specific wording that should move from docs into skills, and wording that should stay in docs.
5. How to avoid skill bloat while preventing agents from skipping critical workflow.
6. A recommended invariant: what an agent must know even if it reads no linked docs.
7. A minimal first issue that edits only one or two skills and is easy to review.
8. Follow-up issues for the remaining skill/doc cleanup.

Output should be implementation-oriented and suitable for turning into SpecDock issues. Use concise but concrete proposed text snippets where helpful.

## Expected Output Handling

- Save the completed ChatGPT analysis as a separate `research` report under this epic's `discussions/`.
- Update this package with the ChatGPT thread URL, visible model/reasoning selection, completion status, and report path after retrieval.

## Submission Record

- First send attempt: `2026-06-05T03:39Z` (approximate; exact seconds not captured)
- ChatGPT Project: `for codex app`
- Visible model / reasoning selector before attempted submission: `じっくり思考 Pro`
- Status: completed
- Retry submitted at: `2026-06-05T03:47Z` (approximate; exact seconds not captured)
- Thread URL: <https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a224793-bae4-83aa-b587-b140081b9bc2>
- Note: First send attempt was blocked by a temporary request-frequency limit; after dismissing the notice, the same prompt was submitted as the thread above.
- Wait policy: `今すぐ回答` must not be selected.
- `今すぐ回答` / `Answer now`: not selected.
- Report path: `spec-dock/active/epic/discussions/20260605t040000z-research-chatgpt-skill-rewrite-targets-report.md`
