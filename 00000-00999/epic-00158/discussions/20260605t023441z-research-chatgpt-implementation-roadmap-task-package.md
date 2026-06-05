---
type: research
status: invalidated
source: chatgpt-use task package
created_at: "2026-06-05T02:34:41Z"
epic_id: "epic-00158"
title: "ChatGPT implementation roadmap task package"
---

# ChatGPT Implementation Roadmap Task Package

## Purpose

Use ChatGPT in the Codex-only ChatGPT Project, with the strongest visible deep reasoning model, to turn the first workflow-compliance diagnosis into an implementation-ready roadmap for SpecDock epic `epic-00158`.

This is not Deep Research. It is a follow-up reasoning thread based on the prior ChatGPT analysis and local runtime structure inspection.

## Repository

- Repository URL: <https://github.com/chemitaro/spec-dock>
- Local worktree: `/Users/iwasawayuuta/.codex/worktrees/8d9b/spec-dock`
- Active epic: `epic-00158 Agent Workflow PDCA Hardening`

## Prior ChatGPT Diagnosis Summary

Prior report: `spec-dock/active/epic/discussions/20260605t023034z-research-chatgpt-workflow-compliance-analysis-report.md`

Key conclusions from that report:

- SpecDock already has a rich workflow contract in docs and shipped skills.
- The main problem is not absence of policy; it is that rules are prose-level, distributed, and manually observed.
- Agents violate workflow because the legal next state is not exposed as a single fail-closed, machine-checkable transition.
- Highest-leverage direction:
  - centralize gate contract into a compact state-machine definition;
  - make gate state observable with manifests and read-only CLI preflight commands;
  - make noncompliance fail early through report templates, lints, state transitions, and eval scenarios;
  - iterate PDCA on one failure class at a time.
- Suggested immediate triage:
  - visible gate checklist / blocker format in skills and templates;
  - read-only `gate status --json` command.

## User-Reported Failure Modes

- Agents skip review gates.
- Agents skip commits.
- Agents do not use appropriate sub-agents.
- Agents create `requirement.md`, `design.md`, and `plan.md` together instead of sequentially.
- Agents proceed past phase gates without waiting for reviewer pass.
- Desired outcome: preserve high model performance while making agents stop, wait, route, review, commit, and proceed in the intended order.

## Local Runtime Structure Observed

Runtime source of truth for shipped CLI:

- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/parser.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/registry.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/`
- `tests/cli_runtime/`, `tests/domain_runtime/`, `tests/presentation_runtime/`

Current parser commands include:

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

No independent `gate`, `report lint`, `execution-preflight`, `step start`, or `step close` command was found in the inspected parser/registry.

Relevant existing runtime features:

- `delegated-authoring diff-guard` already models a narrow fail-closed guard for delegated discussion draft output.
- `validate` and `doctor` already exist for graph/state diagnostics.
- `active show` / `.agent/active.json` are already important active-state surfaces.
- `issue finish` already has lifecycle authority gates, but does not guarantee delivery completion.

## Constraints

- Prefer small, testable issues.
- Do not recommend a huge all-at-once workflow engine rewrite as the first move.
- Keep provider/source-of-truth paths in `src/spec_dock/assets/spec_dock/...`; local `spec-dock/` is dogfooding/generated workspace.
- The main orchestrator owns canonical issue/epic/initiative docs; sub-agent outputs are evidence only.
- Recommendations should become implementation issues with clear acceptance criteria and validation.
- Backward compatibility with existing nodes matters; avoid retroactive hard blockers without a migration or warning phase.

## Prompt To Submit

You are GPT-5.5 Pro / the strongest available deep reasoning model, acting as a product architect and implementation planner for SpecDock.

Do not rely on prior ChatGPT memory or ordinary history. Use only this prompt, the public repository URL, and any public repository context you can inspect from <https://github.com/chemitaro/spec-dock>. If repository inspection is incomplete, mark that uncertainty.

We already ran one analysis thread. Its diagnosis was:

- SpecDock has rich workflow policy, but it is prose-level, distributed, and manually observed.
- Agents skip gates because there is no compact fail-closed state-machine / gate-status affordance.
- The first durable improvements should expose legal next transitions, reviewer freshness, blocker states, and completion readiness through docs/templates and read-only CLI preflight commands.

Current local runtime facts:

- Parser/registry currently expose: `new`, `active`, `delegated-authoring`, `issue start|finish`, `worktree`, `sync`, `deps`, `import`, `validate`, `doctor`.
- No independent `gate status`, `report lint`, `execution-preflight`, `step start`, or `step close` command was found in the inspected parser/registry.
- Runtime is layered: `cli`, `commands`, `application`, `domain`, `infra`, `presentation`.
- Tests are organized under `tests/cli_runtime/`, `tests/domain_runtime/`, and `tests/presentation_runtime/`.
- There is already a `delegated-authoring diff-guard` pattern that could serve as precedent for fail-closed checking.

User problem:
Agents sometimes skip required review, skip commits, fail to use appropriate sub-agents, create requirement/design/plan in parallel, or continue past phase gates without waiting. We need a PDCA hardening program that improves compliance while preserving high model performance and avoiding a giant rewrite.

Please produce an implementation-ready roadmap with:

1. A recommended issue sequence for the next 5-8 issues.
2. For each issue:
   - title;
   - problem it addresses;
   - exact scope and non-scope;
   - primary files/layers likely affected;
   - acceptance criteria;
   - tests/validation;
   - expected risk;
   - rollback or compatibility note.
3. Which issue should be first and why.
4. A minimal viable `gate status --json` design:
   - command shape;
   - JSON schema;
   - status enum;
   - how to represent missing/stale/waived/provisional/unavailable reviewer results;
   - how to avoid false pass;
   - what can be conservative/warning-only in v1.
5. Whether report templates or CLI status should come first, with trade-offs.
6. How to define reviewer freshness in v1 without overengineering.
7. How to handle existing legacy issues with no gate evidence.
8. Concrete examples of adversarial eval prompts and expected compliant behavior.
9. Open implementation questions that should become discussions or ADRs before coding.

Bias toward small, testable, dogfoodable changes. Avoid generic advice; make the output usable to create SpecDock issues directly.

## Expected Output Handling

- Save the completed ChatGPT analysis as a separate `research` report under this epic's `discussions/`.
- Update this package with the ChatGPT thread URL, visible model/reasoning selection, completion status, and report path after retrieval.

## Submission Record

- Submitted at: `2026-06-05T02:36Z` (approximate; exact seconds not captured)
- ChatGPT Project: `for codex app`
- Thread URL: <https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a223643-8988-83a7-9e31-9a0056d30981>
- Visible model / reasoning selector before submission: `じっくり思考 Pro`
- Status: invalidated
- Report path: pending
- Wait policy: Do not select `今すぐ回答`; wait for full long-running reasoning completion.
- Invalidation note: Although this thread did not use `今すぐ回答`, the submitted prompt included a summary derived from the invalidated `今すぐ回答` report. Per user instruction, this output is discarded and must not be used as research evidence. Re-run required using only local inspected facts and user-provided problem context.
