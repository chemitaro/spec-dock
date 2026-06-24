# stdout runbook handoff current-state research

## Summary

The current implementation is only partially aligned with the intended "run the script and consume the fresh workflow from stdout" model.

The skills for issue planning / execution already instruct the agent to run `./spec-dock/scripts/spec-dock workflow next ...` first, which is the right direction. However, the runtime command still writes generated `current-runbook.*` projection files on every successful `workflow next`, and current tests explicitly assert those files are produced. This leaves two handoff surfaces in play:

- fresh stdout from the command invocation
- generated ignored files under `spec-dock/.agent/runbooks/` and `spec-dock/active/`

That dual surface creates the risk described by the user: agents or future workflow text may accidentally treat generated files as the workflow source, may skip the runtime command, or may keep reading stale projections. The current skill wording says projections are ignored output, but the runtime contract and tests still make those projections part of normal command behavior.

## User Problem Statement

The original Epic discussion intended to avoid a two-stage file lookup pattern:

1. Agent reads a skill.
2. Skill tells the agent to read another workflow file or generated workflow projection.

The preferred model is:

1. Agent reads the skill.
2. Skill tells the agent to execute a script.
3. The script prints the current workflow/runbook to stdout.
4. The agent consumes that stdout as the current dynamic workflow guidance.

This has two important properties:

- It avoids relying on an additional generated file that the agent may not read.
- It guarantees the agent obtains the current workflow state at execution time instead of repeatedly reading stale generated output.

## Observed Current State

### Skills already contain stdout-first handoff language

`spec-dock-issue-execution` says:

- First ask the runtime for the current execution Runbook.
- Command: `./spec-dock/scripts/spec-dock workflow next issue-execution`.
- Generated projections such as `spec-dock/.agent/runbooks/current-runbook.*` or `spec-dock/active/current-runbook.*` are ignored output.

Evidence:

- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md:12-18`
- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md:12-18`

This is close to the intended model, but the wording still preserves canonical workflow markdown fallback as a separate authority path, and other skills still directly refer to `workflow_*.md`.

### Other skills still directly reference static workflow docs

Examples:

- `spec-dock-epic-planning` points to `spec-dock/docs/workflow_epic.md` and `workflow_spec_authoring.md`.
- `spec-dock-initiative-planning` points to `workflow_initiative.md`.
- adapters still say to follow `workflow_issue.md`.

Evidence:

- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-planning/SKILL.md`
- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-initiative-planning/SKILL.md`
- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-codex-adapter/SKILL.md`

Interpretation:

- This is not always wrong: canonical fallback docs are still useful when the runtime cannot produce guidance.
- But it is inconsistent with the "script stdout as first dynamic workflow handoff" principle if a skill leads with static workflow file reading for a dynamic workflow state.

### Runtime writes generated runbook projection files during normal `workflow next`

The application workflow layer compiles the runbook and immediately writes it through `runbook_store.write_current(runbook)`.

Evidence:

- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/workflow.py:96-107`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/workflow.py:134-147`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/workflow.py:148-165`

The infra layer writes four paths:

- `spec-dock/.agent/runbooks/current-runbook.json`
- `spec-dock/.agent/runbooks/current-runbook.md`
- `spec-dock/active/current-runbook.json`
- `spec-dock/active/current-runbook.md`

Evidence:

- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/runbook_store.py:16-21`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/runbook_store.py:28-63`

Interpretation:

- The runtime command is not currently "stdout only".
- Projection write failure can turn a dynamic stdout-ready runbook into `runbook-write-failure`, because writing projection is treated as part of command success.
- The symlink hardening is good, but it exists because generated projection is currently in the critical path.

### Tests currently encode projection as expected behavior

The CLI runtime tests assert that `workflow next issue-planning --format json` writes projection files and that the JSON response reports those paths.

Evidence:

- `tests/cli_runtime/test_workflow.py:185-210`

Interpretation:

- Any fix must update tests because the current test suite treats generated runbook files as a supported behavior.
- If the desired behavior is stdout-first / no generated runbook handoff, this test should be replaced by tests that assert stdout contains the runbook and projection is not required for workflow guidance.

## Risk Analysis

### Risk 1: stale generated workflow files

If an agent reads `spec-dock/active/current-runbook.md` or `.json` without running `workflow next`, it may consume a stale workflow generated for a previous active issue, previous step, previous dirty/clean worktree state, or previous assurance state.

This is especially risky because:

- active issue can change;
- plan/report state can change;
- worktree cleanliness changes continuation eligibility;
- assurance classification can be missing, invalid, or updated.

### Risk 2: multi-stage file lookup is brittle for agents

The user is concerned that skill instructions that route agents to additional workflow files or generated files can be skipped or misread. The current skill wording improves this for issue planning/execution, but the broader skill ecosystem still contains direct workflow file references.

### Risk 3: projection write failure blocks stdout handoff

The manual retest confirmed symlink projection fails closed. That safety is correct for file writes, but it also means the command reports `runbook-write-failure` instead of simply returning the fresh runbook to stdout if projection is unsafe.

If stdout is the intended handoff surface, generated projection should not be required for the agent to receive current guidance.

### Risk 4: canonical fallback and dynamic handoff are not clearly separated

The current model has three concepts that need explicit separation:

- canonical static policy docs: durable rules and fallback authority;
- dynamic runtime runbook stdout: current next action and state-dependent guidance;
- generated projection files: optional cache/debug/evidence, not a handoff interface.

Today these concepts are partially separated in prose but still coupled in runtime behavior and tests.

## Likely Fix Direction

The new issue should plan a change with these goals:

1. Make skill entrypoints explicitly stdout-first.
   - Required wording: run `./spec-dock/scripts/spec-dock workflow next <target> --format markdown` or `--format json` and use that stdout as the current dynamic workflow.
   - Do not tell agents to read `current-runbook.*`.
   - Static `workflow_*.md` remains only canonical fallback / policy reference, not the first dynamic handoff.

2. Decouple `workflow next` stdout from generated runbook projection.
   - Either stop writing `current-runbook.*` by default, or add an explicit opt-in flag such as `--write-projection`.
   - If projection remains for debug/evidence, it must be non-authoritative and should not block stdout handoff by default.

3. Update tests to encode the intended contract.
   - Assert stdout contains fresh runbook content.
   - Assert generated projection is absent by default, or only present when explicitly requested.
   - Assert stale generated runbook files are not part of normal guidance.
   - Keep symlink protection tests for explicit projection mode.

4. Audit installed skills and docs for handoff phrasing.
   - Replace "read generated workflow/runbook" style instructions with "run the workflow command and consume stdout".
   - Keep references to `workflow_*.md` as fallback / canonical policy, not state-specific dynamic runbook retrieval.

## Open Questions For Planning

### Q-001: Should generated runbook projection be removed or opt-in?

Recommended answer: opt-in first, not immediate removal.

Rationale:

- Existing tests and manual tests rely on projection behavior.
- Some debugging and manual evidence workflows benefit from projection files.
- Opt-in preserves utility while removing it from the default agent handoff path.

### Q-002: Which stdout format should skills require?

Recommended answer: markdown for human/agent instruction reading, json for automated assertions.

Rationale:

- `--format markdown` is readable in the skill handoff path.
- `--format json` is better for tests and any future machine parser.

### Q-003: Should projection write failure ever block `workflow next`?

Recommended answer: only when projection is explicitly requested.

Rationale:

- If stdout is the authoritative dynamic handoff, unsafe projection should not prevent the agent from receiving current guidance.
- In explicit projection mode, fail closed remains correct.

## Proposed Next Artifact Work

This research should feed the issue requirement/design/plan for `iss-00238`.

Suggested implementation slices:

- S01: adjust issue planning/execution skill wording and tests for stdout-first handoff.
- S02: add runtime flag or mode to make runbook projection opt-in.
- S03: update CLI/runtime tests around projection default vs explicit projection.
- S04: audit and update related skills/docs for fallback wording.

## Current Issue Lifecycle Evidence

- Previous issue `iss-00237` was finished with `spec-dock: ok (issue finish) issue=iss-00237 github=#237 state=CLOSED active_cleared=true`.
- New issue `iss-00238` / GitHub `#238` was created under `epic-00224`.
- New issue `iss-00238` was started and branch `iss-00238-stdout-runbook-handoff-instead-of-generated-workflow-files` was checked out.
