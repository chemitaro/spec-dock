---
type: research
status: completed
source: chatgpt-use task package
created_at: "2026-06-05T02:50:42Z"
epic_id: "epic-00158"
title: "ChatGPT clean workflow hardening task package"
---

# ChatGPT Clean Workflow Hardening Task Package

## Purpose

Run a clean ChatGPT analysis for SpecDock workflow hardening using `じっくり思考 Pro`, without using any prior ChatGPT outputs that were obtained via or contaminated by `今すぐ回答`.

This task is not Deep Research. It is a long-running ChatGPT reasoning task grounded in local inspected repository facts and the public repository URL.

## Strict Wait Policy

- Do not select `今すぐ回答`.
- Wait for full long-running reasoning completion.
- If ChatGPT shows `今すぐ回答`, leave it untouched and continue polling.
- If a previous thread used `今すぐ回答`, or used a summary derived from such output, that data is invalid and must not be used.

## Repository

- Repository URL: <https://github.com/chemitaro/spec-dock>
- Local worktree: `/Users/iwasawayuuta/.codex/worktrees/8d9b/spec-dock`
- Active epic: `epic-00158 Agent Workflow PDCA Hardening`

## User-Reported Failure Modes

- Agents sometimes skip required review gates.
- Agents sometimes skip commits.
- Agents sometimes do not use appropriate sub-agents.
- Agents sometimes create `requirement.md`, `design.md`, and `plan.md` together instead of progressing sequentially.
- Agents sometimes proceed past phase gates without waiting for the required reviewer pass.
- Desired outcome: preserve high model performance while making agents stop, wait, route, review, commit, and proceed in the intended order.
- Desired improvement process: PDCA across multiple issues; revise skills/docs/instructions/runtime checks, dogfood, observe failures, then refine.

## Local Evidence Excerpts And Facts

### Source-of-truth workflow docs

`src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`:

- Spec authoring order is `requirement -> spec-reviewer pass -> design -> spec-reviewer pass -> plan -> spec-reviewer pass -> downstream handoff`.
- Each phase promotion requires a fresh `spec-reviewer` result with `review_status: pass`.
- Missing / stale / failed / unavailable / denied / waived / provisional reviewer results must block or remain incomplete; degraded mode must not be treated as reviewer-gate success.
- Canonical `requirement.md`, `design.md`, `plan.md`, and `report.md` are main-orchestrator single-writer authority.
- Sub-agent authoring output belongs under scope-local flat `discussions/` and must not self-claim accepted authority, reviewer pass, phase completion, implementation readiness, or issue readiness.
- Evidence Adoption Ledger, Promotion Record, delegated draft evidence, failure modes, and phase gates are already described.

`src/spec_dock/assets/spec_dock/docs/workflow_issue.md`:

- Issue planning routes through `.agents/skills/spec-dock-issue-planning/SKILL.md`.
- Issue execution routes through `.agents/skills/spec-dock-issue-execution/SKILL.md`.
- Requirement / design / plan promotion uses `workflow_spec_authoring.md` and must wait for fresh `spec-reviewer` pass before moving to the next artifact.
- Execution may start only after planning artifacts are approved / reviewer-pass and handoff readiness evidence exists.
- Issue execution requires implementation delegation gates, per-step reviewer gates, step commit gates, final QA / code / spec review gates, PR delivery / merge-preparation gates, and final commit evidence before `complete`.
- `1 implementation step = 1 review scope = 1 commit` is the standard.
- Unavailable / denied / waived / provisional reviewer or delegation states are not success.

### Skill facts

`src/spec_dock/assets/install_root/.agents/skills/spec-driven-tdd-workflow/SKILL.md`:

- Hub skill says docs are source of truth.
- It routes issue planning to `spec-dock-issue-planning` and issue execution to `spec-dock-issue-execution`.
- It repeats the fresh spec-reviewer pass rule and says missing/stale/failed/unavailable/denied/waived/provisional are not pass.

`src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md`:

- Planning skill is concise.
- It points to workflow docs and says canonical docs remain main-orchestrator-owned.
- It says not to move from requirement to design, design to plan, or plan to execution without fresh `spec-reviewer` pass.

`src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md`:

- Execution skill says execution starts only after `requirement.md`, `design.md`, and `plan.md` are approved / reviewer-pass and recorded as ready.
- It routes implementation to `dev-coder`, shipped docs/templates/skills/workflow text to `doc-writer`, and review failures to bounded delegated follow-up.
- It says unavailable tooling, denied access, host conflicts, waiver requests, and similar blockers are stop/incomplete unless explicit policy says they count as success.

### Runtime / CLI facts

Runtime source-of-truth paths:

- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/parser.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/registry.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/`

Current parser/registry expose these command families:

- `new initiative|epic|issue|doc`
- `active set|show|clear`
- `delegated-authoring manifest|baseline-status|diff-guard`
- `issue start|finish`
- `worktree create|list|show|remove`
- `sync`
- `deps check|add|remove`
- `import initiative|epic|issue`
- `validate`
- `doctor`

No independent parser/registry entry was found for:

- `gate status`
- `report lint`
- `execution-preflight`
- `step start`
- `step close`

Existing useful precedent:

- `delegated-authoring diff-guard` already models a narrow fail-closed guard for delegated discussion draft output.
- `validate` and `doctor` already exist for graph/state diagnostics.
- `active show` / `.agent/active.json` are already important active-state surfaces.
- `issue finish` already has lifecycle authority gates, but does not guarantee delivery completion.

### Constraints

- Prefer small, testable issues.
- Avoid a giant all-at-once workflow engine rewrite.
- Provider/source-of-truth edits belong in `src/spec_dock/assets/spec_dock/...`; local `spec-dock/` is dogfooding/generated workspace.
- Main orchestrator owns canonical issue/epic/initiative docs; sub-agent outputs are evidence only.
- Recommendations should become implementation issues with clear acceptance criteria and validation.
- Backward compatibility with existing nodes matters; avoid retroactive hard blockers without migration, warning mode, or explicit legacy handling.

## Prompt To Submit

You are GPT-5.5 Pro / the strongest available deep reasoning model, acting as an external product architect and implementation planner for SpecDock.

Important constraints:

- Do not rely on prior ChatGPT memory, ordinary history, or any previous ChatGPT analysis.
- Do not use or assume any output from a prior thread that used `今すぐ回答`.
- Use only this prompt, the public repository URL, and any public repository context you can inspect from <https://github.com/chemitaro/spec-dock>.
- If repository inspection is incomplete, mark that uncertainty.

Problem:
SpecDock's workflow is not reliably followed by agents. Agents sometimes skip required reviews, skip commits, fail to use appropriate sub-agents, create requirement/design/plan in parallel, or continue past phase gates without waiting. We need a PDCA hardening program that improves compliance while preserving high model performance and avoiding a giant rewrite.

Known local facts:

- The docs already require sequential spec authoring: `requirement -> fresh spec-reviewer pass -> design -> fresh spec-reviewer pass -> plan -> fresh spec-reviewer pass -> downstream handoff`.
- Missing/stale/failed/unavailable/denied/waived/provisional reviewer results are not pass.
- Canonical requirement/design/plan/report are main-orchestrator-owned.
- Sub-agent outputs are discussion evidence only until adopted and reviewed.
- Issue execution starts only after reviewer-pass planning artifacts and readiness evidence.
- Execution expects delegation gates, per-step reviewer gates, step commit gates, final QA/code/spec gates, PR delivery/merge-preparation gates, and final commit evidence.
- Runtime currently exposes `new`, `active`, `delegated-authoring`, `issue start|finish`, `worktree`, `sync`, `deps`, `import`, `validate`, and `doctor`.
- No parser/registry entry was found for `gate status`, `report lint`, `execution-preflight`, `step start`, or `step close`.
- Runtime is layered under `cli`, `commands`, `application`, `domain`, `infra`, and `presentation`.
- Tests are organized under `tests/cli_runtime/`, `tests/domain_runtime/`, and `tests/presentation_runtime/`.
- `delegated-authoring diff-guard` is an existing precedent for narrow fail-closed checking.

Please produce an implementation-ready analysis with:

1. Executive diagnosis based only on the facts above and public repo inspection.
2. Failure-mode taxonomy explaining why capable agents violate the workflow despite docs.
3. Recommended issue sequence for the next 5-8 PDCA hardening issues.
4. For each issue:
   - title;
   - problem addressed;
   - exact scope and non-scope;
   - likely affected files/layers;
   - acceptance criteria;
   - tests/validation;
   - expected risk;
   - rollback or compatibility note.
5. Which issue should be first and why.
6. A minimal viable `gate status --json` or alternative first guard design:
   - command shape;
   - JSON schema or report block schema;
   - status enum;
   - how to represent missing/stale/waived/provisional/unavailable reviewer results;
   - how to avoid false pass;
   - what can be conservative/warning-only in v1.
7. Whether docs/templates/skills or CLI status should come first, with trade-offs.
8. How to define reviewer freshness in v1 without overengineering.
9. How to handle existing legacy issues with no gate evidence.
10. Concrete adversarial eval prompts and expected compliant behavior.
11. Open implementation questions that should become discussions or ADRs before coding.

Bias toward small, testable, dogfoodable changes. Avoid generic advice; make the output usable to create SpecDock issues directly.

## Expected Output Handling

- Save the completed ChatGPT analysis as a separate `research` report under this epic's `discussions/`.
- Update this package with the ChatGPT thread URL, visible model/reasoning selection, completion status, and report path after retrieval.

## Submission Record

- Submitted at: `2026-06-05T02:52Z` (approximate; exact seconds not captured)
- ChatGPT Project: `for codex app`
- Thread URL: <https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a223a07-ac74-83a9-afa5-2c45c4f5a8e1>
- Visible model / reasoning selector before submission: `じっくり思考 Pro`
- Status: completed
- Wait policy: `今すぐ回答` must not be selected.
- Answer Now: not used
- Report path: `spec-dock/active/epic/discussions/20260605t030757z-research-chatgpt-clean-workflow-hardening-report.md`
- Last checked at: `2026-06-05T03:06:29Z`
- Last visible state: prompt and `今すぐ回答` control were visible; no completed answer/report was retrieved. Continue waiting or inspect later without selecting `今すぐ回答`.
