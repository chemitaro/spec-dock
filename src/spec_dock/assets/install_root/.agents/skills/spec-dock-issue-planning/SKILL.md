---
name: spec-dock-issue-planning
description: ChatGPT-first Issue planning entrypoint for creating canonical Issue requirement, design, and plan artifacts from requirement-heavy, draft-heavy, or context-heavy inputs.
---

# Spec-Dock Issue Planning

Use this skill for non-trivial Issue planning. This is the primary planning route and it is ChatGPT-first.

The old local/manual planning workflow is not the normal route. Use `spec-dock-issue-planning-manual` only as a human-approved emergency backup after the ChatGPT-first route is hard-failed and unrecoverable.

## Responsibility

This skill orchestrates canonical Issue planning. It does not split the workflow into separate planning modes. Different inputs change the context framing and review focus only.

Codex owns:

- confirming the active Issue and parent Epic context;
- collecting repository, branch, parent, prior Issue, dependency, artifact, ADR, code, test, operator intent, and development background context;
- invoking `spec-dock-chatgpt-authoring` for the main Issue planning draft;
- reviewing ChatGPT output as evidence;
- adopting or rejecting claims in the `report.md` Evidence Adoption Ledger;
- rewriting canonical Issue `requirement.md`, `design.md`, and `plan.md`;
- obtaining fresh `spec-reviewer` pass after canonical changes;
- handing execution off only when canonical docs are reviewer-gated and executable.

ChatGPT may produce:

- Issue requirement/design/plan candidates;
- review focus notes;
- risk and test strategy notes;
- optional supporting artifacts;
- `information_insufficient` with missing information and questions.

ChatGPT output is evidence only. It never grants canonical adoption, reviewer pass, assurance mutation, execution-ready, PR-ready, merge-ready, Issue finish, Epic completion, or PR delivery.

## Read First

- Runtime guidance: `./spec-dock/scripts/spec-dock guidance issue-planning`
- `spec-dock/docs/workflow_issue.md`
- `spec-dock/docs/workflow_spec_authoring.md`
- `spec-dock/docs/phase_plan_issue.md`
- `spec-dock/docs/authoring/issue-plan.md`
- `spec-dock/docs/authoring/chatgpt-pack.md`
- `spec-dock/docs/authoring/decision-routing.md`
- `spec-dock/docs/authoring/scope-layering.md`
- active Issue `requirement.md`, `design.md`, `plan.md`, `report.md`, and scope-local `artifacts/`
- parent Epic docs, prior completed Issues, dependency state, ADRs, code, tests, and user-provided material relevant to the Issue

## Input Context Framing

Issue Planning has one workflow. Use these labels only to frame the prompt and adoption review:

- `requirement-heavy`: a requirement or requirement candidate is the strongest input; design and implementation planning are the main work.
- `draft-heavy`: draft requirement/design/plan artifacts already exist; formalization, refresh, consistency repair, and adoption review are the main work.
- `context-heavy`: discussion, artifacts, ADRs, code, tests, or background context are the strongest inputs; requirement extraction and boundary definition are the main work.

The required output is always canonical Issue `requirement.md`, `design.md`, and `plan.md`, or `information_insufficient`. Do not create separate workflow modes from these labels.

## Operating Spine

1. Confirm active Issue and planning authority.
   - Use runtime guidance as current state guidance, not canonical authority.
   - Stop if active context, parent context, or reviewer obligations are contradictory.
2. Build a ChatGPT-first planning request.
   - Include repository and branch.
   - Prefer GitHub-synced context when the branch is pushed and visible.
   - Include explicit lower-authority labeling for local-context runs.
   - Include operator intent and development background as free-form context.
   - Include the input context framing: `requirement-heavy`, `draft-heavy`, or `context-heavy`.
   - Include parent Epic context, prior completed Issues, dependency state, unresolved report ledgers, and relevant artifacts.
   - Request Issue `requirement.md`, `design.md`, `plan.md`, and optional supporting artifacts.
   - Allow `information_insufficient` when the input cannot support planning.
3. Ask `spec-dock-chatgpt-authoring` for Issue planning evidence.
   - Wait, retry, or recover for capacity, timeout, stale sync, browser startup, or backend setup problems.
   - Do not auto-switch to manual planning.
4. Review the returned evidence.
   - Check that the three canonical artifacts are complete, mutually consistent, and executable as a planning set.
   - For `draft-heavy` input, refresh current repository state, prior completed Issues, dependency state, unresolved ledgers, and drift evidence before adopting draft claims.
   - If drift is Issue-local, repair it in Issue Planning.
   - If drift changes Epic boundaries, Issue order, scope allocation, shared architecture, or workflow policy, return to Epic Planning repair, clarification, or ADR.
   - Reject unsupported claims, stale repository assumptions, and any forbidden authority claims.
   - Record material adoption/rejection in the `report.md` Evidence Adoption Ledger.
5. Write canonical Issue artifacts.
   - Integrate only adopted claims into `requirement.md`, `design.md`, and `plan.md`.
   - Keep raw ChatGPT output and drafts in artifacts, not as canonical authority.
   - Do not treat validation pass, draft-only output, or raw ZIP/tree output as execution-ready.
6. Run the authoring gate.
   - Obtain fresh `spec-reviewer` pass after substantive canonical changes.
   - Proceed to Issue Execution only when canonical docs are reviewer-passed, current, non-template, and the plan is executable.

## Manual Backup

Manual backup requires all of:

- hard / unrecoverable ChatGPT, browser, backend, provider, or account-state failure;
- reasonable wait / retry / recover attempts have failed;
- explicit human approval to use `spec-dock-issue-planning-manual`;
- failure class, recovery attempts, approval evidence, and fallback decision recorded in `report.md`.

Queued tabs, slow responses, retryable timeouts, stale sync, missing prompt context, or fixable setup are not manual fallback reasons.

## Stop Conditions

- Active Issue or parent Epic context is missing, stale, or contradictory.
- Repository/branch evidence required for ChatGPT-first planning is unavailable and no explicit local-context run was approved.
- ChatGPT returns `information_insufficient`; ask the human for the missing information instead of fabricating artifacts.
- ChatGPT output has not been adopted or rejected in `report.md`.
- Requirement/design/plan artifacts are template-only, unresolved, stale, contradictory, or missing fresh reviewer pass.
- Draft-heavy input is being used to bypass canonical adoption, fresh `spec-reviewer`, or execution handoff gates.
- The Issue-local plan would change Epic boundaries, Issue order, scope allocation, shared architecture, or workflow policy without returning to the owning scope.
- Manual fallback is requested without explicit human approval.
