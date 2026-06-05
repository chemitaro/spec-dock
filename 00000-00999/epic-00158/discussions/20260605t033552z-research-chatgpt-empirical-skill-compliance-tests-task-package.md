---
type: research
status: completed
source: chatgpt-use task package
created_at: "2026-06-05T03:35:52Z"
epic_id: "epic-00158"
title: "ChatGPT empirical skill compliance tests task package"
answer_now_allowed: false
---

# ChatGPT Empirical Skill Compliance Tests Task Package

## Purpose

Use ChatGPT `じっくり思考 Pro` to design empirical tests for whether revised SpecDock skills cause agents to follow the intended workflow better.

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

## Hypothesis Under Test

Agent compliance may improve if:

- mandatory workflow is written directly in the skill;
- docs explain concepts, field meanings, examples, and detailed references;
- skills explicitly say which docs to read for each artifact/task;
- agents can follow the minimal required workflow even if they do not read every linked document.

Current failure mode suspected by the user:

- Skills are thin.
- Critical procedures are dispersed across many docs.
- Model may skip linked docs.
- Therefore the model may not know the workflow it is expected to follow.

## Prompt To Submit

You are GPT-5.5 Pro / the strongest available deep reasoning model, acting as an evaluator for agent instruction quality and empirical prompt tuning.

Important constraints:

- Do not rely on prior ChatGPT memory or ordinary history.
- Do not use or assume any output from a prior thread that used `今すぐ回答`.
- Use only this prompt and, if useful, public repository context from <https://github.com/chemitaro/spec-dock>.
- If repository inspection is incomplete, mark that uncertainty.

Task:
Design a lightweight empirical evaluation plan for revised SpecDock workflow skills.

The question is not whether runtime gates are stricter. The question is whether agents more reliably follow the intended workflow when mandatory procedure is present in skills and detailed semantics remain in docs.

Please produce:

1. A before/after evaluation design:
   - baseline skill;
   - revised skill;
   - same task prompts;
   - same repository fixtures;
   - same scoring rubric.
2. 6-10 realistic task prompts that expose failure modes:
   - create an issue but "requirements not needed yet";
   - update an issue plan with unresolved requirement gap;
   - execute an issue without fresh spec-reviewer pass;
   - delegate doc/skill changes correctly to doc-writer;
   - avoid claiming completion without report evidence;
   - handle sub-agent unavailable/denied states.
3. A scoring rubric with observable pass/fail criteria:
   - reads required docs at the right time;
   - asks user only after local investigation;
   - keeps canonical docs main-orchestrator-owned;
   - records discussion/research/interview evidence appropriately;
   - does not treat waived/unavailable as pass;
   - does not proceed to implementation prematurely.
4. Suggested metrics:
   - critical violation rate;
   - doc-read trigger accuracy;
   - phase-gate compliance;
   - over-ceremony / unnecessary blocking;
   - task completion quality.
5. A minimal manual evaluation harness that can be run during PDCA without building a full automated system.
6. What evidence to capture in each run.
7. How to decide whether the skill rewrite improved enough to proceed to the next issue.
8. Risks and how to avoid optimizing the skill for tests only.

Bias toward small, repeatable, dogfoodable evaluation. Avoid generic benchmark advice.

## Expected Output Handling

- Save the completed ChatGPT analysis as a separate `research` report under this epic's `discussions/`.
- Update this package with the ChatGPT thread URL, visible model/reasoning selection, completion status, and report path after retrieval.

## Submission Record

- Submitted at: `2026-06-05T03:39Z` (approximate; exact seconds not captured)
- ChatGPT Project: `for codex app`
- Thread URL: <https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a22452c-c3d0-83aa-b742-54f6aaec4072>
- Visible model / reasoning selector before submission: `じっくり思考 Pro`
- Status: completed
- Wait policy: `今すぐ回答` must not be selected.
- `今すぐ回答` / `Answer now`: not selected.
- Report path: `spec-dock/active/epic/discussions/20260605t035201z-research-chatgpt-empirical-skill-compliance-tests-report.md`
