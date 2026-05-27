---
kind: research
id: "20260526t105722z-research-subagent-permission-profile-callability"
title: "Codex subagent Permission Profile callability analysis"
created_at: "2026-05-26T10:57:22Z"
created_by_role: "main-orchestrator"
scope_id: "iss-00131"
source_paths:
  - ".codex/agents/system-architect.toml"
  - ".codex/agents/implementation-planner.toml"
  - ".codex/agents/spec-manager.toml"
  - ".codex/AGENTS.md"
  - ".agents/skills/spec-dock-system-architect/SKILL.md"
  - ".agents/skills/spec-dock-implementation-planner/SKILL.md"
  - "src/spec_dock/assets/install_root/.codex/agents/system-architect.toml"
  - "src/spec_dock/assets/install_root/.codex/agents/implementation-planner.toml"
  - "tests/test_init_update.py"
  - "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00126-write-capable-delegated-draft-authoring-correction/report.md"
  - "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00127-scoped-discussion-draft-authoring-correction/report.md"
intended_targets:
  - "spec-dock/active/issue/requirement.md"
  - "spec-dock/active/issue/design.md"
  - "spec-dock/active/issue/plan.md"
adoption_status: "unreviewed"
reflected_to: []
diff_guard_result: "not_run"
---

# Codex subagent Permission Profile callability analysis

## Executive Summary

`system-architect` / `implementation-planner` fresh spawn failure is best treated as a spec-dock contract mismatch exposed by a Codex multi-agent v1 limitation.

Observed behavior:

- `fork_context=true` plus `agent_type=...` fails by Codex API contract. This is not a spec-dock bug.
- `fork_context=false` fresh spawn with `agent_type=system-architect` or `implementation-planner` fails with `agent type is currently not available`.
- Other project-local agent roles using legacy `sandbox_mode`, such as `spec-manager`, are callable.
- The unavailable roles are the only project-local roles using static `default_permissions` Permission Profiles with broad discussion glob write rules.

Recommended direction:

- Do not try to solve this by making the main orchestrator config Permission Profile based and expecting child roles to override it.
- Convert static `system-architect` / `implementation-planner` adapters to callable read-only or no-static-write fallback roles.
- Keep write-capable delegated authoring on the generated exact-file Permission Profile path, using `delegated-authoring scoped-context --discussion-file`.
- Update provider assets, dogfooding mirror assets, role skills, `.codex/AGENTS.md`, and tests so the contract is explicit and internally consistent.

## Investigation Findings

### Forked role override is out of scope

Codex rejects full-history forked subagents when `agent_type`, `model`, or `reasoning_effort` is also provided. The error is explicit:

```text
Full-history forked agents inherit the parent agent type, model, and reasoning effort; omit agent_type, model, and reasoning_effort, or spawn without a full-history fork.
```

That path should be documented as unsupported. The fix for this issue should not attempt to make forked role override work.

### Fresh spawn failure is role/config specific

Fresh spawn with `system-architect` and `implementation-planner` failed with:

```text
agent type is currently not available
```

However, `spec-manager` fresh spawn succeeded. This proves project-local agents are being discovered and the multi-agent tool itself is available. The failure is not "all local agents are unavailable".

Current role config contrast:

- `.codex/agents/system-architect.toml` uses `default_permissions = "spec_dock_system_architect_draft_authoring"` and defines `permissions.spec_dock_system_architect_draft_authoring`.
- `.codex/agents/implementation-planner.toml` uses `default_permissions = "spec_dock_implementation_planner_draft_authoring"` and defines `permissions.spec_dock_implementation_planner_draft_authoring`.
- `.codex/agents/spec-manager.toml` uses `sandbox_mode = "workspace-write"` and is callable.

Provider and dogfooding mirror assets are currently byte-identical for the affected adapter files, so this is not a mirror drift issue.

### Current static Permission Profile grants write globs

`system-architect` currently grants these static write rules:

```toml
"spec-dock/initiatives/*/discussions/*.md" = "write"
"spec-dock/initiatives/*/epics/*/discussions/*.md" = "write"
"spec-dock/initiatives/*/epics/*/issues/*/discussions/*.md" = "write"
```

The same shape exists for `implementation-planner`.

These rules are intentionally broad within spec-dock scope-local `discussions/`, but they are not exact-file grants. They also require Codex multi-agent spawn to honor a custom Permission Profile embedded in an agent role file.

### Repo contract is internally inconsistent

`iss-00127` report says the intended corrected contract is:

- generated scoped context requires `--discussion-file`
- generated Permission Profile grants write only to the exact selected direct child Markdown file
- static `system-architect` / `implementation-planner` adapters remain read-mostly fallback surfaces with no static write roots
- taxonomy should say scoped delegated authors have no static write roots

Current implementation and tests do not match that report:

- `.codex/agents/system-architect.toml` and provider mirror still contain `default_permissions` and static discussion write globs.
- `.codex/AGENTS.md` says static adapters are write-capable for scope-local `discussions/` Markdown drafts.
- `.agents/skills/spec-dock-system-architect/SKILL.md` and `spec-dock-implementation-planner` say static adapters are the write-capable path.
- `tests/test_init_update.py` asserts no `sandbox_mode`, requires `default_permissions`, and expects the three static discussion write glob roots.

This means the current source of truth is split:

- issue report outcome points to "static no-write fallback + generated exact-file write profile"
- shipped assets and tests point to "static adapter is write-capable via Permission Profile write globs"

This issue should first resolve that contract conflict.

## Codex Runtime Evidence

Official Codex docs and source indicate `default_permissions` is valid configuration syntax, but it does not prove that a multi-agent v1 fresh spawn can safely apply a child role's custom Permission Profile as an override.

Evidence:

- Codex custom agents can include config keys from `config.toml`.
- Codex config supports `default_permissions` and `[permissions.<name>]`.
- Codex source parses role TOML as `ConfigToml` via a flattened config struct, so a role file containing `default_permissions` is syntactically plausible.
- Codex multi-agent spawn applies the requested role config, then reapplies runtime turn overrides, including the parent turn's active permission profile.
- The role application path maps role config application failure to `agent type is currently not available`, which hides the underlying config-layer failure from the model/tool caller.

Relevant upstream source references:

- `agent_roles.rs`: role TOML contains `#[serde(flatten)] config: ConfigToml`.
  - https://github.com/openai/codex/blob/main/codex-rs/core/src/config/agent_roles.rs
- `role.rs`: role application maps failures to `agent type is currently not available`.
  - https://github.com/openai/codex/blob/main/codex-rs/core/src/agent/role.rs
- `spawn.rs`: spawn applies role config before later runtime overrides.
  - https://github.com/openai/codex/blob/main/codex-rs/core/src/tools/handlers/multi_agents/spawn.rs
- `multi_agents_common.rs`: runtime overrides set the child permission profile from the parent turn.
  - https://github.com/openai/codex/blob/main/codex-rs/core/src/tools/handlers/multi_agents_common.rs
- Official docs:
  - https://developers.openai.com/codex/subagents
  - https://developers.openai.com/codex/config-reference

Current feature state observed during investigation:

- `multi_agent` is stable and enabled.
- `multi_agent_v2` is under development and disabled.

Therefore the current issue should target the stable multi-agent v1 behavior, not assume v2 semantics.

## Why "make the main agent use Permission Profiles" is insufficient

Moving the main orchestrator from legacy `sandbox_mode = "workspace-write"` to a Permission Profile may be useful long-term configuration hygiene, but it is not the core fix for this failure.

Reasons:

1. Codex v1 spawn reapplies the parent turn's permission profile after role config application. If the parent uses a Permission Profile, the child may still inherit that parent effective profile rather than keeping its role-specific scoped profile.
2. This would not prove that `system-architect` can select its own static `default_permissions` safely.
3. It changes global/session behavior for all roles, not only the failing delegated authoring roles.
4. It still leaves spec-dock's internal contract conflict unresolved.

The likely result is at best "remove one legacy/profiles syntax conflict", not "enable child role-specific scoped write override".

## Recommended Resolution

Adopt this contract:

1. Static Codex subagent roles for `system-architect` and `implementation-planner` are callable fallback/advisory roles.
2. Static roles must not carry write-capable custom Permission Profiles.
3. Static roles should use `sandbox_mode = "read-only"` unless there is a separately proven Codex-supported way to apply child-specific custom Permission Profiles in multi-agent v1.
4. Write-capable delegated authoring must use generated exact-file Permission Profiles produced by `delegated-authoring scoped-context --discussion-file`.
5. The generated profile grants write only to the named discussion Markdown file and any explicitly allowed task evidence path.
6. The main orchestrator remains responsible for post-run diff guard, adoption ledger, canonical promotion, and final reviewer gates.

This aligns the active implementation with the safer half of `iss-00127`:

- exact-file write boundary for actual delegated authoring
- no static broad write roots
- fallback when Codex host role callability is unavailable or degraded

## Candidate Change Plan

### Provider assets

Update:

- `src/spec_dock/assets/install_root/.codex/agents/system-architect.toml`
- `src/spec_dock/assets/install_root/.codex/agents/implementation-planner.toml`

Expected changes:

- remove `default_permissions`
- remove `[permissions.*]` tables
- set `sandbox_mode = "read-only"` or an equivalent non-write fallback supported by current Codex
- keep `approval_policy = "never"`
- update developer instructions to say static adapter cannot write and should return a proposed draft body or handoff when direct writing is unavailable

### Dogfooding mirror

Mirror the same changes in:

- `.codex/agents/system-architect.toml`
- `.codex/agents/implementation-planner.toml`

Provider and dogfooding mirror must remain byte-for-byte aligned after sync/update verification.

### Skills and AGENTS guidance

Update:

- `.codex/AGENTS.md`
- `src/spec_dock/assets/install_root/.codex/AGENTS.md`
- `.agents/skills/spec-dock-system-architect/SKILL.md`
- `.agents/skills/spec-dock-implementation-planner/SKILL.md`
- provider mirror skill files under `src/spec_dock/assets/install_root/.agents/skills/`

Expected wording:

- static adapters are callable advisory/fallback surfaces
- static adapters do not directly write discussion files unless a future Codex runtime explicitly supports role-specific scoped Permission Profiles
- write-capable runs require generated scoped context with an exact `--discussion-file`
- post-run diff guard and adoption ledger remain required

### Tests

Update taxonomy and adapter tests in `tests/test_init_update.py`.

Expected assertions:

- `system-architect` / `implementation-planner` static adapters use `sandbox_mode = "read-only"` or another explicit no-write setting
- they do not define static `default_permissions`
- they do not define static discussion write globs
- generated scoped-context tests continue to assert exact-file write profile behavior
- docs/skills do not claim static broad discussion write capability

Add or preserve coverage that generated `delegated-authoring scoped-context --discussion-file`:

- emits `default_permissions`
- writes only the exact selected direct child Markdown file
- rejects nested paths, non-Markdown files, bad discussion filenames, symlinks, and out-of-scope targets

### Manual validation

After implementation, run manual Codex subagent probes from the Desktop/API environment:

1. fresh `system-architect` spawn should be callable
2. fresh `implementation-planner` spawn should be callable
3. static roles must not create files directly
4. generated scoped-context write path must remain the only supported write-capable delegated authoring path
5. `fork_context=true` plus `agent_type` remains documented unsupported behavior

If manual multi-agent probes cannot be automated in unittest, record the evidence in `report.md` as manual validation.

## Draft Requirement Shape

The eventual `requirement.md` should avoid starting from an implementation preference. It should specify the externally observable contract:

- AC-001: fresh `system-architect` and `implementation-planner` roles are callable in Codex multi-agent v1 without `agent type is currently not available`.
- AC-002: static delegated authoring roles do not grant broad workspace write, canonical write, or static discussion glob write.
- AC-003: write-capable delegated authoring uses generated exact-file Permission Profile context only.
- AC-004: docs, role skills, adapter TOMLs, and tests agree on the static-vs-generated write boundary.
- AC-005: forked role override remains explicitly unsupported and documented as not part of the fix.
- AC-006: provider assets and dogfooding mirror stay in sync.

Non-goals:

- Do not try to patch Codex itself.
- Do not depend on `multi_agent_v2`.
- Do not require changing the user's global `~/.codex/config.toml` to make spec-dock shipped roles callable.
- Do not broaden static adapter write permissions to `workspace-write`.

## Risks

- Switching static adapters to read-only may reduce convenience if users expected static role direct discussion writes.
- If Codex later supports role-specific Permission Profile override in multi-agent v2, the static read-only contract may be more conservative than necessary.
- Existing documentation has already diverged; partial edits could leave users with contradictory guidance.
- Manual multi-agent spawn validation is host-surface dependent and may not be reproducible in hermetic unit tests.

## Open Questions

1. Should the static fallback role return draft content only, or should it also be allowed to suggest the exact `delegated-authoring scoped-context --discussion-file` command?
2. Should `system-architect` / `implementation-planner` use `sandbox_mode = "read-only"` specifically, or a built-in read-only Permission Profile if Codex docs recommend one?
3. Should previous historical report wording in `iss-00127` remain untouched as historical evidence, with `iss-00131` recording the correction, or should any current docs summarize that `iss-00127` left implementation/test drift?

## Integration Notes

This document is a pre-requirement analysis draft. It should be adopted into `iss-00131/requirement.md` only after the main orchestrator chooses the contract. No canonical docs have been updated by this discussion draft.

Suggested adoption:

- use "Recommended Resolution" as the core requirement boundary
- use "Candidate Change Plan" to seed design/plan
- use "Manual validation" as report evidence requirements
- record the existing `iss-00127` report-vs-asset/test contradiction as the main background problem
