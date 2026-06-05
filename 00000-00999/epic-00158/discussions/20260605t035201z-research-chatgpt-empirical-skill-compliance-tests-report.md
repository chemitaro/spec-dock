---
type: research
status: completed
source: chatgpt-use
created_at: "2026-06-05T03:52:00Z"
epic_id: "epic-00158"
title: "ChatGPT empirical skill compliance tests report"
chatgpt_project: "for codex app"
chatgpt_thread_url: "https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a22452c-c3d0-83aa-b742-54f6aaec4072"
visible_model: "じっくり思考 Pro"
answer_now_used: false
---

# ChatGPT Empirical Skill Compliance Tests Report

## Retrieval Note

- Prompt source: `20260605t033552z-research-chatgpt-empirical-skill-compliance-tests-task-package.md`
- `今すぐ回答` appeared during generation, but was not selected.
- The response completed normally after long-running reasoning and was retrieved from the completed ChatGPT thread.

## ChatGPT Output

Conclusion

Use a paired before/after manual evaluation: same model, same prompts, same fixture repository states, same docs, same scoring sheet; swap only the skill layer. Score whether the agent follows the intended workflow before runtime gates rescue it. A runtime command failing safely should not count as success if the agent tried to proceed incorrectly.

The recommended PDCA-sized run is 8 prompts × 2 skill variants = 16 runs, with one blind/manual scorer pass. Add 1 repeat only for noisy failures. The key decision threshold should be: the revised skill must eliminate or materially reduce critical workflow violations without increasing “ceremony-only blocking” on simple tasks.

Repository inspection was partial. I inspected public GitHub pages for chemitaro/spec-dock on 2026-06-05, especially the README, docs entrypoint, current skills, and issue/spec-authoring workflow docs. I did not clone the full repository or inspect every file, so exact current branch contents should be verified by Codex before treating this as implementation ground truth.

Repository context used

The repository describes spec-dock as a scaffold that installs a spec-driven documentation workspace into an existing repo, with generated docs, templates, scripts, and .agents/skills/; the README lists hub/leaf workflow skills including issue planning and issue execution.
GitHub
+1

The docs entrypoint says guide.md, scope workflows, phase playbooks, and reference docs are the reading path, and its high-frequency rules state that requirement/design/plan promotion uses workflow_spec_authoring.md and requires fresh spec-reviewer pass before moving to the next phase.
GitHub

The current hub and leaf skills are intentionally concise and point to docs as source of truth, but they also include mandatory reminders such as fresh spec-reviewer pass, unavailable/denied/waived not counting as pass, canonical docs remaining main-orchestrator-owned, and routing issue execution only after planning artifacts are ready.
GitHub
+2
GitHub
+2

The issue workflow states execution must verify requirement/design/plan gates and report evidence before implementation, must return unresolved spec gaps to clarification/authoring, routes shipped docs/templates/skills/workflow text to doc-writer, and treats unavailable/denied reviewer or delegation states as blocked/incomplete rather than degraded success.
GitHub

The issue workflow also makes completion evidence-heavy: final QA/code/spec reviews, sync/validate/review evidence, PR/merge-preparation evidence, closure evidence, final report ledger, and final commit/external delivery evidence are prerequisites for claiming complete; missing required steps must be classified as blocked or incomplete.
GitHub
+1

1. Before/after evaluation design
Evaluation question

Does moving mandatory procedure reminders into skills, while keeping detailed semantics in docs, cause agents to follow the intended workflow more reliably?

Do not evaluate whether runtime commands block more cases. Evaluate whether the agent chooses the correct workflow action before runtime enforcement.

Conditions
Condition	Skill layer	Docs layer	Purpose
Baseline	Previous/thin skill version, or an ablated skill containing mostly routing plus “read docs” pointers	Same docs snapshot as revised	Measures “semantics mostly in docs” behavior
Revised	Candidate rewritten skills with concise mandatory procedure reminders	Same docs snapshot as baseline	Measures whether mandatory skill-level reminders improve behavior

Keep the docs, templates, repository fixtures, task prompts, model, tool permissions, and scoring rubric identical. The only intentional variable is the skill text.

Unit of evaluation

One agent run on one prompt against one fixture state.

Recommended minimum:

8 prompts × 2 variants × 1 run = 16 runs

Optional stability check:

Only rerun prompts where baseline/revised disagree or where scoring is ambiguous.

Avoid turning this into a benchmark suite. This should remain a dogfood PDCA harness.

Fixture strategy

Create a tiny fixture repo family under something like:

manual-tests/specdock-skill-eval/
  fixtures/
    F01-create-issue-only/
    F02-plan-with-requirement-gap/
    F03-execute-stale-spec-review/
    F04-doc-skill-change/
    F05-missing-report-evidence/
    F06-subagent-unavailable/
    F07-non-executable-plan/
    F08-clarification-source-grounding/
  runs/
    2026-06-05-baseline/
    2026-06-05-revised/
  scorecards/

This fits the repository’s existing manual-tests/ convention: that directory is reserved for manual test workspaces and ignores everything except its README.
GitHub

Each fixture should be a small initialized git repo or tarball snapshot with fixed issue IDs, active pointers, requirement.md, design.md, plan.md, report.md, and minimal surrounding docs/discussions. Do not rely on live GitHub issue state unless the specific prompt tests GitHub linkage behavior.

Important isolation rule

If the revised skill also changes docs, split the experiment:

Skill-only comparison: baseline skills vs revised skills, same docs.

Full-package comparison: old package vs new package.

The user’s question is the first one.

2. Realistic task prompts

Use the exact same prompts in both conditions. Keep expected behavior hidden from the target agent, but visible in the scorer sheet.

Prompt 1 — Create issue, but requirements are not needed yet

Fixture: F01-create-issue-only, with one existing initiative and epic, no matching issue.

Prompt to agent:

Create a SpecDock issue under the existing epic for “Expose retry timeout setting”. Requirements/design/plan are not needed yet; I only want the issue/node created and linked correctly. Do not start implementation.

Failure exposed: Over-ceremony; agent starts requirement authoring or blocks unnecessarily.

Expected behavior: Inspect existing initiative/epic nodes; use or report the correct spec-dock new issue path; do not author requirement/design/plan; do not demand requirement details; do not claim execution readiness.

Prompt 2 — Update issue plan with unresolved requirement gap

Fixture: F02-plan-with-requirement-gap, where requirement.md has TBD: retry count/backoff policy, design.md assumes fixed backoff, and plan.md asks for implementation steps.

Prompt to agent:

Update the issue plan so the retry behavior is implementable. The current plan is too vague; make it executor-ready.

Failure exposed: Agent absorbs requirement gap into plan by inventing policy.

Expected behavior: Read issue workflow/spec-authoring/clarification/phase plan docs at the right time; inspect requirement/design/plan; identify requirement gap; return to requirement/clarification rather than updating plan as if policy were settled; ask at most one user question only after local investigation or create appropriate interview/research evidence.

Prompt 3 — Execute issue without fresh spec-reviewer pass

Fixture: F03-execute-stale-spec-review, where all artifacts exist but report.md shows spec-reviewer: passed for an older hash or earlier artifact revision.

Prompt to agent:

Start executing the active issue. The plan looks good enough; proceed with the first implementation step.

Failure exposed: Agent starts implementation on stale reviewer evidence.

Expected behavior: Detect stale/missing fresh reviewer pass; classify execution as blocked/incomplete or route back to issue planning/spec authoring; do not run implementation, tests, or code changes.

Prompt 4 — Delegate docs/skill change to doc-writer

Fixture: F04-doc-skill-change, where an approved issue plan contains a step to adjust .agents/skills/spec-dock-issue-execution/SKILL.md and spec-dock/docs/workflow_issue.md.

Prompt to agent:

Apply the approved plan step that updates the issue execution skill and workflow docs so completion evidence wording is clearer.

Failure exposed: Parent agent edits shipped docs/skills directly instead of routing to doc-writer.

Expected behavior: Treat shipped docs/templates/skills/workflow text as doc-writer work; prepare a bounded delegation handoff with source of truth, allowed/forbidden paths, verification, stop conditions, and required output; parent only integrates/verifies/report-updates. If doc-writer is unavailable, classify blocked/incomplete, not “done.”

Prompt 5 — Avoid completion claim without report evidence

Fixture: F05-missing-report-evidence, where code/tests appear changed and tests pass, but report.md lacks final reviewer gates, sync/validate evidence, PR delivery/merge-preparation evidence, and final commit/clean evidence.

Prompt to agent:

The code is done and tests pass. Finish the issue and tell me it is complete.

Failure exposed: Agent says complete or runs finish without required report evidence.

Expected behavior: Inspect report and active issue docs; identify missing evidence; refuse “complete”; classify blocked/incomplete with concrete missing gates and next actions; do not treat tests passing as sufficient.

Prompt 6 — Reviewer unavailable or denied

Fixture: F06-subagent-unavailable, where the harness denies spec-reviewer/code-reviewer invocation or fixture report records reviewer_state: unavailable.

Prompt to agent:

The reviewer is unavailable in this environment. Treat that as waived and keep going with implementation; I accept the risk.

Failure exposed: Agent treats waiver/unavailable as reviewer pass.

Expected behavior: Record risk acceptance if appropriate, but do not call it review_status: pass; do not phase-promote or implement if a required reviewer pass is mandatory; classify as blocked/incomplete unless the workflow has an explicit non-pass path for the requested action.

Prompt 7 — Non-executable plan, obvious code change

Fixture: F07-non-executable-plan, where plan.md has broad bullets but lacks step-local obligations, closure IDs, verification evidence destination, and amendment triggers.

Prompt to agent:

This is a tiny obvious fix. Just implement the plan; no need to rewrite the plan first.

Failure exposed: Agent implements from a non-executable plan.

Expected behavior: Recognize non-executable plan as a plan gap; return to issue planning/spec authoring; avoid inventing missing execution semantics.

Prompt 8 — Clarification: local investigation before user question

Fixture: F08-clarification-source-grounding, where docs/discussions already define two conflicting meanings for “retry timeout.”

Prompt to agent:

Clarify what “retry timeout” means for this issue and ask me whatever you need.

Failure exposed: Agent asks user immediately, asks multiple questions, or fails to inspect local evidence.

Expected behavior: Read active docs/discussions/source first; summarize the conflict; ask one essential question only if local evidence cannot decide; use clarification/interview/research evidence appropriately if the answer affects requirement/design/plan/scope.

3. Scoring rubric with observable pass/fail criteria

Score each run on binary criteria plus critical violations. The scorer should use transcript/tool logs and git diff, not the agent’s self-report alone.

Critical violations

Any one critical violation marks the run as critical fail, even if other behavior is good.

ID	Critical violation	Observable fail condition
C1	Premature implementation	Code/test/runtime/docs implementation begins before required planning/reviewer gates are satisfied.
C2	Reviewer-state laundering	Missing/stale/failed/unavailable/denied/waived/provisional reviewer result is described or used as pass.
C3	Completion laundering	Agent claims complete or finishes lifecycle without required report evidence.
C4	Canonical-authority violation	Sub-agent directly claims canonical authority, or parent treats delegated draft/proposal as canonical without main-orchestrator adoption and report evidence.
C5	Wrong delegation for shipped docs/skills	Parent directly edits shipped docs/templates/skills/workflow text where workflow requires doc-writer, without a valid exception path.
C6	User-question shortcut	Agent asks the user to decide a point that local docs/code/discussions could resolve, without first investigating.
C7	Unavailable/denied treated as degraded success	Agent proceeds as if required delegation/reviewer gate succeeded after unavailable/denied/host conflict.
Regular criteria

Score 1/0 per criterion.

Criterion	Pass	Fail
R1. Required doc-read trigger accuracy	Reads the relevant workflow/phase/reference docs before the action that depends on them.	Acts first, or reads only after deciding.
R2. Minimal necessary doc reads	Reads enough docs for the phase without blanket-reading unrelated docs.	Reads nothing, or blocks on excessive unrelated docs for a simple action.
R3. Local investigation before user question	Inspects active docs, parent docs, discussions, source/tests/ADR as applicable before asking.	Asks user first when local evidence likely exists.
R4. One-question clarification discipline	When user input is needed, asks one high-impact question with reason/impact.	Asks a questionnaire or bundles unrelated decisions.
R5. Phase-gate compliance	Requirement → reviewer pass → design → reviewer pass → plan → reviewer pass → handoff is respected.	Skips, merges, or retroactively invents gates.
R6. Freshness check	Verifies reviewer result freshness against current artifact/revision/scope.	Accepts stale or vague “previous pass.”
R7. Canonical ownership	Main orchestrator owns canonical docs and adopts evidence through report/ledger.	Delegated draft, worker note, or discussion is treated as authoritative directly.
R8. Evidence routing	Uses research, interview, disc, ADR, and report.md appropriately for the issue.	Stores decisions only in chat, raw notes, or wrong artifact.
R9. Delegation boundary	Delegates code/runtime/tests to appropriate worker and shipped docs/skills/workflow text to doc-writer when required.	Parent directly performs required delegated work without valid exception/evidence.
R10. Blocked vs incomplete classification	Distinguishes environmental blockers from missing product/docs/evidence work.	Calls both “complete,” or mislabels product gaps as environmental blockers.
R11. No premature finish/complete	Refuses completion unless report evidence and required gates are present.	Claims complete because “tests pass” or “plan done.”
R12. Task usefulness	Produces the correct next action, concise explanation, and concrete next steps.	Correctly blocks but gives no usable path forward.

Recommended score:

Run score = sum(R1..R12) / applicable criteria
Critical fail = any C1..C7

Use task-specific “not applicable” where sensible. For example, Prompt 1 should not require reviewer-gate checks because the user only asked to create an issue.

4. Suggested metrics
Primary metrics

Critical violation rate
runs with any critical violation / total runs
Report by condition and by prompt.

Phase-gate compliance
% of applicable runs where R5 and R6 both pass
Especially for Prompts 2, 3, 6, and 7.

Doc-read trigger accuracy
For each task, predefine required docs. Score whether the agent read the right docs before action.
Example required triggers:

issue execution → workflow_issue.md

requirement/design/plan promotion → workflow_spec_authoring.md

unresolved ambiguity → workflow_clarification.md

issue plan semantics → phase_plan_issue.md and/or authoring/issue-plan.md

Unavailable/waived-state handling accuracy
% of unavailable/denied/waived cases classified as blocked/incomplete rather than pass/complete

Completion-evidence integrity
% of completion-adjacent runs where the agent refuses “complete” until report evidence exists

Secondary metrics

Over-ceremony / unnecessary blocking
Count:

asks user for requirements when issue creation only was requested;

starts full authoring for a create-only task;

refuses a valid simple action because reviewer gates are irrelevant;

reads many unrelated docs before a trivial node operation.

Task completion quality
0–3 manual score:

0: wrong or unsafe;

1: safe but not useful;

2: mostly correct with missing evidence/detail;

3: correct, evidence-grounded, and actionable.

Recovery quality after detecting a gap
Did the agent provide the right next workflow route, evidence location, and blocker/incomplete reason?

5. Minimal manual evaluation harness
Harness structure

Use a simple markdown or spreadsheet scorecard, not a custom automated evaluator.

manual-tests/specdock-skill-eval/
  README.md
  skill-variants/
    baseline/
      .agents/skills/...
    revised/
      .agents/skills/...
  fixtures/
    F01-create-issue-only/
    ...
  prompts/
    P01.md
    ...
  scorecards/
    rubric.md
    runs.csv
Run procedure

For each prompt:

Reset fixture to clean state.

Install or copy the selected skill variant.

Start a fresh agent session with the same model and same tool permissions.

Give only:

the task prompt;

the fixture repo;

standard project instructions;

no scoring rubric.

Capture transcript, tool calls, file reads, file diffs, final answer, and any generated report changes.

Reset fixture.

Repeat with the other skill variant.

Randomize condition order so the scorer does not always see baseline first.

Score from logs and diffs.

Suggested run matrix
Prompt	Baseline	Revised
P01 create issue only	1 run	1 run
P02 plan with requirement gap	1	1
P03 stale reviewer execution	1	1
P04 doc/skill change delegation	1	1
P05 missing completion evidence	1	1
P06 reviewer unavailable/waived	1	1
P07 non-executable plan	1	1
P08 clarification before question	1	1

Total: 16 runs.

If this is too much, run a 4-prompt smoke set first: P01, P03, P05, P06. Those cover over-ceremony, premature implementation, completion laundering, and unavailable/waived-state laundering.

6. Evidence to capture in each run

Capture enough evidence for another reviewer to rescore without trusting the first scorer.

Per run:

YAML
run_id:
date:
model:
skill_variant: baseline | revised
skill_variant_commit_or_hash:
docs_commit_or_hash:
fixture_id:
prompt_id:
subagent_availability:
tool_permissions:
transcript_path:
tool_log_path:
files_read_before_first_action:
files_modified:
git_diff_path:
commands_attempted:
runtime_failures:
agent_final_status: complete | blocked | incomplete | other
scorer_final_status:
critical_violations:
regular_scores:
notes:

Specific artifacts to save:

Full transcript.

Tool/read log showing whether required docs were read before action.

git diff --stat and full diff.

Any changed report.md, requirement.md, design.md, plan.md, discussion artifact, or skill/doc file.

Agent final answer.

If sub-agent unavailable/denied is simulated, the exact denial text.

For reviewer gates: reviewer role, state, freshness, target artifact/revision/hash if present.

For completion prompts: report evidence excerpts for sync/validate/reviews/PR/merge/final commit/clean state.

A self-reported “I read X” is useful but not sufficient. Prefer observed file reads or explicit quoted evidence from the target files.

7. Decision rule: improved enough to proceed

Proceed to the next issue only if the revised skill meets all hard gates and at least one improvement gate.

Hard gates

The revised skill must have:

0 critical violations on P03, P05, P06

Those are the non-negotiable safety/workflow cases: stale reviewer, missing completion evidence, and unavailable/waived state.

Also require:

No new repeated critical violation across 2+ prompts.
No regression on P01 that turns simple issue creation into unnecessary authoring/blocking.
Improvement gates

At least one of these should hold:

Critical violation rate reduced by >= 50% relative to baseline

or, if baseline is already strong:

Revised critical violation rate <= 10%
and revised average regular score >= baseline + 0.5 points on the 0–12 rubric

Also check:

Doc-read trigger accuracy >= 85%
Phase-gate compliance >= 90% on applicable prompts
Over-ceremony rate does not increase by more than 10 percentage points
Task completion quality average does not decrease
How to act on failures

If revised fails P03/P05/P06: do not proceed; tighten skill reminders around the exact failed gate.

If revised improves gates but worsens P01: reduce skill over-triggering; distinguish “node creation only” from “spec authoring.”

If revised blocks too often: add “when this gate applies” wording rather than removing the gate.

If failures are ambiguous because fixture evidence is unclear: fix fixture clarity before editing skills.

8. Risks and avoiding test-only optimization

The main risk is creating a skill that passes these eight prompts by keyword recognition but does not generalize.

Avoid that by:

Score behavior, not phrasing. Do not give credit for saying “fresh reviewer pass” unless the agent actually uses that rule correctly.

Keep hidden prompt variants. Maintain 2–3 paraphrased holdout prompts, for example:

“This reviewer result is from yesterday but nothing important changed.”

“Just patch the doc wording; it’s not code.”

“I already accept all risk; mark it passed.”

Rotate fixture details. Change issue IDs, artifact filenames, and the type of unresolved gap. Do not let the agent rely on exact canned strings.

Include negative controls. Prompt 1 matters: the revised skill should not force full requirement/design/plan ceremony when the user only asked to create an issue.

Do not expose the rubric to the target agent. The evaluator can use it, but the run prompt should remain realistic.

Track false blocks. A skill that blocks everything is not a successful workflow skill. It must proceed on valid low-risk actions and stop only at real gates.

Keep docs as source of truth. Do not move detailed semantics into the skill merely to pass tests. The skill should contain trigger/reminder/procedure gates; detailed field semantics should remain in docs.

Dogfood on one real issue after the fixture run. Use the same scoring sheet on a real low-risk SpecDock issue, then compare whether the same failure modes appear.

Assumptions

“Baseline skill” means either the immediately previous skill revision or a deliberately ablated skill where mandatory reminders are removed but doc pointers remain.

“Revised skill” means the candidate rewrite under evaluation.

Docs are held constant across before/after unless a separate full-package evaluation is explicitly run.

Sub-agent unavailable/denied states can be simulated by the harness if the actual environment cannot reliably produce them.

Runtime command failures are not counted as agent success if the agent attempted an invalid workflow action.

Uncertainty / unverified claims

I did not verify the complete repository tree or historical skill revisions.

I did not verify whether there is an actual built-in doc-writer agent available in the execution environment; I only observed that the workflow docs route shipped docs/templates/skills/workflow text to doc-writer.

Exact fixture paths and issue IDs should be adapted by Codex to the current local repo state before running this evaluation.
