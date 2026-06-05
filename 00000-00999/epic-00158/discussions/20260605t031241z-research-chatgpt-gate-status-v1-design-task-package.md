---
type: research
status: completed
source: chatgpt-use task package
created_at: "2026-06-05T03:12:41Z"
epic_id: "epic-00158"
title: "ChatGPT gate status v1 design task package"
answer_now_allowed: false
---

# ChatGPT Gate Status v1 Design Task Package

## Purpose

Use ChatGPT `じっくり思考 Pro` to deepen the clean workflow-hardening recommendation into an implementation-ready design for the first proposed issue: read-only, fail-closed `gate status --json` v1.

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

## Valid Prior ChatGPT Finding

Valid clean report: `spec-dock/active/epic/discussions/20260605t030757z-research-chatgpt-clean-workflow-hardening-report.md`

The clean report was completed without selecting `今すぐ回答`. Its recommended first issue was:

- Add read-only `gate status --json` for spec-authoring gates.
- Make it fail-closed and conservative.
- Start with requirement/design/plan reviewer gate status.
- Treat missing/stale/failed/unavailable/denied/waived/provisional as non-pass.
- Use content hash freshness.
- Avoid giant rewrites; preserve layered runtime architecture.

## Local Runtime Facts For This Design Thread

Runtime source-of-truth paths:

- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/parser.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/registry.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/`

Existing command pattern:

- `commands/delegated_authoring.py` defines dataclass command args, registers `CommandSpec`s, converts CLI args, calls application functions, and renders `CommandOutcome`.
- `application/delegated_authoring.py` defines request dataclasses and performs read-only / guard logic.
- `domain/delegated_authoring.py` owns status/result dataclasses, regex/contracts, and fail-closed classification.
- `delegated-authoring diff-guard` returns `ok=False`, `status="blocked"`, and specific `reason`/`details` for missing baseline, invalid baseline, forbidden diffs, canonical doc edits, root path edits, and expected-count failures.
- `commands/validate.py` is smaller: args -> `use_cases.validate_tree(ValidateTreeRequest())` -> render text -> exit code.
- `application/contracts.py` centralizes request/result dataclasses and `UseCases`.

Current parser/registry command families:

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

No independent parser/registry entry was found for `gate status`, `report lint`, `execution-preflight`, `step start`, or `step close`.

## Workflow Facts To Preserve

- Spec authoring order: `requirement -> fresh spec-reviewer pass -> design -> fresh spec-reviewer pass -> plan -> fresh spec-reviewer pass -> downstream handoff`.
- Missing/stale/failed/unavailable/denied/waived/provisional reviewer results are not pass.
- Canonical `requirement.md`, `design.md`, `plan.md`, and `report.md` are main-orchestrator-owned.
- Sub-agent outputs are discussion evidence only until adopted and reviewed.
- v1 should not claim semantic quality; it should only classify structured evidence and current artifact freshness.
- False negatives are acceptable in v1; false pass is not.

## Prompt To Submit

You are GPT-5.5 Pro / the strongest available deep reasoning model, acting as a senior runtime architect for SpecDock.

Important constraints:

- Do not rely on prior ChatGPT memory or ordinary history.
- Do not use or assume any output from a prior thread that used `今すぐ回答`.
- Use only this prompt, the public repository URL, and any public repository context you can inspect from <https://github.com/chemitaro/spec-dock>.
- If repository inspection is incomplete, mark that uncertainty.

Task:
Design the first concrete implementation issue for SpecDock workflow hardening: read-only, fail-closed `gate status --json` v1 for spec-authoring gates.

Context:

- SpecDock docs already require sequential authoring: `requirement -> fresh spec-reviewer pass -> design -> fresh spec-reviewer pass -> plan -> fresh spec-reviewer pass`.
- Non-pass states include missing/stale/failed/unavailable/denied/waived/provisional.
- Runtime is layered: `cli`, `commands`, `application`, `domain`, `infra`, `presentation`.
- Existing fail-closed precedent: `delegated-authoring diff-guard`, with command args, application request, domain classification, `ok/status/reason/details`, and exit code 0/1.
- Parser/registry currently expose no `gate status`.
- Tests are under `tests/cli_runtime/`, `tests/domain_runtime/`, `tests/presentation_runtime/`.

Please produce an implementation-ready design with:

1. Recommended v1 scope and non-scope.
2. Command UX:
   - exact CLI shape;
   - target resolution behavior;
   - exit code policy;
   - text vs JSON output behavior.
3. Domain model:
   - dataclasses/enums;
   - gate IDs;
   - reviewer status enum;
   - freshness enum;
   - blocker and warning structure;
   - pass/non-pass truth table.
4. Evidence input strategy:
   - what v1 can parse safely from `report.md`;
   - whether v1 should require new structured blocks or accept legacy prose;
   - how to classify legacy/no-evidence cases without false pass.
5. Artifact freshness:
   - hash strategy;
   - which artifact hashes each gate requires;
   - how to treat upstream artifact changes;
   - how to treat uncommitted changes.
6. Application / command / presentation layering:
   - proposed file names;
   - request/result dataclasses;
   - how to integrate into `UseCases` or whether to follow direct application function style like `delegated_authoring`.
7. JSON schema v1 with example payloads for:
   - all pass;
   - requirement missing review;
   - design stale review;
   - waived reviewer result;
   - legacy no evidence.
8. Tests:
   - unit tests;
   - CLI runtime fixtures;
   - presentation JSON snapshots;
   - no-write/read-only verification.
9. Acceptance criteria for the issue.
10. Risks and rollback.
11. Follow-up issues this v1 intentionally leaves open.

Bias toward small, testable, dogfoodable implementation. Avoid generic advice. Make this directly usable as a SpecDock issue requirement/design/plan seed.

## Expected Output Handling

- Save the completed ChatGPT analysis as a separate `research` report under this epic's `discussions/`.
- Update this package with the ChatGPT thread URL, visible model/reasoning selection, completion status, and report path after retrieval.

## Submission Record

- Submitted at: `2026-06-05T03:14Z` (approximate; exact seconds not captured)
- ChatGPT Project: `for codex app`
- Thread URL: <https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a223f31-5e1c-83a9-9fd2-dcf40fb20090>
- Visible model / reasoning selector before submission: `じっくり思考 Pro`
- Status: completed
- Wait policy: `今すぐ回答` must not be selected.
- `今すぐ回答` / `Answer now`: not selected.
- Report path: `spec-dock/active/epic/discussions/20260605t033127z-research-chatgpt-gate-status-v1-design-report.md`
