# G10 Shared Diff Evidence

## Purpose

This document fixes the shared review scope for the Epic-wide pre-PR quality gate. Fresh spec-reviewer, deep-consultant, code-reviewer, and QA reviewer should use this same base/current framing instead of independently choosing a smaller issue-local diff.

## Scope

- repository: `chemitaro/spec-dock`
- current branch: `iss-00125-authority-aware-delegated-authoring-dogfooding-pilot`
- PR: `#119` (`https://github.com/chemitaro/spec-dock/pull/119`)
- PR base/head from GitHub at refresh time: `baseRefName=main`, `baseRefOid=421fd4c02fd2649b8c29ec9549a961b7824b9149`, `headRefName=iss-00118-delegated-authoring-dogfooding-pilot`, `headRefOid=4365d38f5d88ac4ace362837ce55fdf8e2d6e404`, `mergeable=MERGEABLE`, `isDraft=false`
- comparison base: immutable PR base OID `421fd4c02fd2649b8c29ec9549a961b7824b9149`; `main` is used only as a local convenience alias after confirming the same merge base.
- reason for base: this repository has no local `develop` ref; `origin/HEAD` points to `origin/main`.
- merge base: `421fd4c02fd2649b8c29ec9549a961b7824b9149`
- current HEAD: `4365d38f5d88ac4ace362837ce55fdf8e2d6e404`
- working tree: included. The gate is intentionally run against the completed local state before PR update, not only committed `HEAD`.
- refresh timestamp: `2026-05-24T06:34:30Z`, after `iss-00126` main promotion, post-P1 verification, Gauss report repair, Schrodinger Flow-A/B repair, Aristotle deep-consultant approve, Nietzsche stale working-tree supplement finding, Helmholtz/Rawls report-state reconciliation finding, Plato E-AC traceability cleanup, Zeno positive-probe authority gate repair, Dalton acceptance/design positive-probe contract cleanup, Boole D-016 follow-up cleanup, Carson P2 G10 exact working-tree scope clarification, James fresh spec re-review pass, Chandrasekhar fresh code-review pass, and report evidence update.

## Commands

```bash
git branch --show-current
git remote -v
git branch -a
git merge-base main HEAD
git rev-parse HEAD
git diff --stat 421fd4c02fd2649b8c29ec9549a961b7824b9149...HEAD
git diff --name-status 421fd4c02fd2649b8c29ec9549a961b7824b9149...HEAD
git diff --stat main
git diff --name-status main
git diff --stat
git diff --name-status
git ls-files --others --exclude-standard
gh pr view 119 --json baseRefName,baseRefOid,headRefName,headRefOid,url,state,isDraft,mergeable
git diff --check
./spec-dock/scripts/spec-dock validate
uv run python -m unittest discover -v
```

Attempted `develop` comparison failed because `develop` is not a valid local ref:

```text
fatal: Not a valid object name develop
fatal: ambiguous argument 'develop...HEAD': unknown revision or path not in the working tree.
```

## Diff Summary

### Immutable committed PR diff

The committed PR snapshot is fixed by base OID and current committed `HEAD`:

```bash
git diff --stat 421fd4c02fd2649b8c29ec9549a961b7824b9149...HEAD
git diff --name-status 421fd4c02fd2649b8c29ec9549a961b7824b9149...HEAD
```

Exact `--stat` terminal summary:

```text
270 files changed, 23075 insertions(+), 898 deletions(-)
```

Exact full file-level `--name-status` output is captured in the companion full-output artifact:

- `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/discussions/20260523t204806z-disc-g10-full-name-status.md`
- command recorded there: `git diff --name-status 421fd4c02fd2649b8c29ec9549a961b7824b9149...HEAD`
- entry count: `270`

This companion artifact is part of G10 evidence and is intentionally immutable to the committed `HEAD` snapshot. It does not include uncommitted working-tree or untracked corrective evidence; those are recorded below.

### Working tree tracked diff

Latest `git diff --stat main` reported:

- 281 tracked files changed
- 25,361 insertions
- 910 deletions

Latest `git diff --stat` for tracked changes after committed `HEAD` reported:

- 63 tracked files changed
- 2,470 insertions
- 196 deletions

The broad tracked scope includes:

- provider agent/config assets under `src/spec_dock/assets/install_root/.agents/` and `.codex/`
- dogfooding agent/config mirrors under `.agents/` and `.codex/`
- provider workflow docs/templates/system assets under `src/spec_dock/assets/spec_dock/`
- dogfooding workflow docs/templates/system mirrors under `spec-dock/`
- runtime authority, delegated authoring, active lifecycle, validation, and issue lifecycle surfaces under provider and dogfooding `spec_dock_runtime`
- active Epic documentation, discussion research, child issue specs, and corrective issue `iss-00126`
- runtime and managed asset tests under `tests/`
- packaging metadata `pyproject.toml` / `uv.lock`

Untracked files are part of the review scope. They include:

- the corrective Epic discussions:
  - `discussions/20260523t235448z-disc-write-capable-draft-authoring-gap-analysis.md`
  - `discussions/20260524t001711z-disc-write-capable-draft-authoring-resolution-plan-v2.md`
  - this G10 shared diff evidence file
- the corrective issue tree:
  - `issues/iss-00126-write-capable-delegated-draft-authoring-correction/`
- new delegated authoring runtime modules:
  - `spec-dock/scripts/spec_dock_runtime/application/delegated_authoring.py`
  - `spec-dock/scripts/spec_dock_runtime/commands/delegated_authoring.py`
  - `spec-dock/scripts/spec_dock_runtime/domain/delegated_authoring.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/delegated_authoring.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/delegated_authoring.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/delegated_authoring.py`
- new delegated authoring tests:
  - `tests/cli_runtime/test_delegated_authoring.py`
  - `tests/domain_runtime/test_delegated_authoring.py`

Exact `git diff --name-status` for tracked working-tree changes at this endpoint:

```text
M	.agents/skills/spec-dock-implementation-planner/SKILL.md
M	.agents/skills/spec-dock-system-architect/SKILL.md
M	.codex/agents/implementation-planner.toml
M	.codex/agents/system-architect.toml
M	.codex/config.toml
M	spec-dock/docs/authoring/issue-plan.md
M	spec-dock/docs/phase_design.md
M	spec-dock/docs/phase_plan.md
M	spec-dock/docs/phase_plan_epic.md
M	spec-dock/docs/phase_plan_issue.md
M	spec-dock/docs/workflow_issue.md
M	spec-dock/docs/workflow_spec_authoring.md
M	spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/design.md
M	spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/discussions/20260523t204806z-disc-g10-full-name-status.md
M	spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/plan.md
M	spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/report.md
M	spec-dock/scripts/spec_dock_runtime/application/delete_node.py
M	spec-dock/scripts/spec_dock_runtime/application/issue_lifecycle.py
M	spec-dock/scripts/spec_dock_runtime/application/set_active.py
M	spec-dock/scripts/spec_dock_runtime/application/sync_state.py
M	spec-dock/scripts/spec_dock_runtime/application/validate_tree.py
M	spec-dock/scripts/spec_dock_runtime/cli/parser.py
M	spec-dock/scripts/spec_dock_runtime/cli/registry.py
M	spec-dock/scripts/spec_dock_runtime/domain/authority.py
M	spec-dock/scripts/spec_dock_runtime/infra/active_store.py
M	spec-dock/system/active-none/epic/report.md
M	spec-dock/system/active-none/initiative/report.md
M	spec-dock/system/active-none/issue/report.md
M	spec-dock/templates/epic/report.md
M	spec-dock/templates/initiative/report.md
M	spec-dock/templates/issue/report.md
M	src/spec_dock/assets/install_root/.agents/skills/spec-dock-implementation-planner/SKILL.md
M	src/spec_dock/assets/install_root/.agents/skills/spec-dock-system-architect/SKILL.md
M	src/spec_dock/assets/install_root/.codex/agents/implementation-planner.toml
M	src/spec_dock/assets/install_root/.codex/agents/system-architect.toml
M	src/spec_dock/assets/install_root/.codex/config.toml
M	src/spec_dock/assets/spec_dock/docs/authoring/issue-plan.md
M	src/spec_dock/assets/spec_dock/docs/phase_design.md
M	src/spec_dock/assets/spec_dock/docs/phase_plan.md
M	src/spec_dock/assets/spec_dock/docs/phase_plan_epic.md
M	src/spec_dock/assets/spec_dock/docs/phase_plan_issue.md
M	src/spec_dock/assets/spec_dock/docs/workflow_issue.md
M	src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md
M	src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/delete_node.py
M	src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_lifecycle.py
M	src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/set_active.py
M	src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/sync_state.py
M	src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/validate_tree.py
M	src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/parser.py
M	src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/registry.py
M	src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authority.py
M	src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/active_store.py
M	src/spec_dock/assets/spec_dock/system/active-none/epic/report.md
M	src/spec_dock/assets/spec_dock/system/active-none/initiative/report.md
M	src/spec_dock/assets/spec_dock/system/active-none/issue/report.md
M	src/spec_dock/assets/spec_dock/templates/epic/report.md
M	src/spec_dock/assets/spec_dock/templates/initiative/report.md
M	src/spec_dock/assets/spec_dock/templates/issue/report.md
M	tests/cli_runtime/test_issue_lifecycle.py
M	tests/cli_runtime/test_runtime_active_s05.py
M	tests/cli_runtime/test_validate.py
M	tests/domain_runtime/test_authority.py
M	tests/test_init_update.py
```

Exact `git ls-files --others --exclude-standard` for untracked files at this endpoint:

```text
spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/discussions/20260523t235448z-disc-write-capable-draft-authoring-gap-analysis.md
spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/discussions/20260524t001711z-disc-write-capable-draft-authoring-resolution-plan-v2.md
spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/discussions/20260524t043441z-disc-g10-shared-diff-evidence.md
spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00126-write-capable-delegated-draft-authoring-correction/.meta.json
spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00126-write-capable-delegated-draft-authoring-correction/design.md
spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00126-write-capable-delegated-draft-authoring-correction/discussions/delegated-authoring/input-authority/design-authority.json
spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00126-write-capable-delegated-draft-authoring-correction/discussions/delegated-authoring/input-authority/design-promotion.json
spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00126-write-capable-delegated-draft-authoring-correction/discussions/delegated-authoring/input-authority/design-reviewer.json
spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00126-write-capable-delegated-draft-authoring-correction/discussions/delegated-authoring/input-authority/plan-authority.json
spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00126-write-capable-delegated-draft-authoring-correction/discussions/delegated-authoring/input-authority/requirement-promotion.json
spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00126-write-capable-delegated-draft-authoring-correction/discussions/delegated-authoring/input-authority/requirement-reviewer.json
spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00126-write-capable-delegated-draft-authoring-correction/discussions/delegated-authoring/iss-00126-implementation-planner-plan-cli-98a21ff9ddee/delegated-write-result.md
spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00126-write-capable-delegated-draft-authoring-correction/discussions/delegated-authoring/iss-00126-implementation-planner-plan-cli-98a21ff9ddee/manifest.toml
spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00126-write-capable-delegated-draft-authoring-correction/discussions/delegated-authoring/iss-00126-implementation-planner-plan-cli-98a21ff9ddee/permission-profile.toml
spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00126-write-capable-delegated-draft-authoring-correction/discussions/delegated-authoring/iss-00126-implementation-planner-plan-cli-98a21ff9ddee/probe-plan.md
spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00126-write-capable-delegated-draft-authoring-correction/discussions/delegated-authoring/iss-00126-implementation-planner-plan-cli-98a21ff9ddee/session-invocation.toml
spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00126-write-capable-delegated-draft-authoring-correction/discussions/delegated-authoring/iss-00126-implementation-planner-plan-cli-e03b5e56572a/manifest.toml
spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00126-write-capable-delegated-draft-authoring-correction/discussions/delegated-authoring/iss-00126-implementation-planner-plan-cli-e03b5e56572a/permission-profile.toml
spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00126-write-capable-delegated-draft-authoring-correction/discussions/delegated-authoring/iss-00126-implementation-planner-plan-cli-e03b5e56572a/probe-plan.md
spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00126-write-capable-delegated-draft-authoring-correction/discussions/delegated-authoring/iss-00126-implementation-planner-plan-cli-e03b5e56572a/probe-result.md
spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00126-write-capable-delegated-draft-authoring-correction/discussions/delegated-authoring/iss-00126-implementation-planner-plan-cli-e03b5e56572a/session-invocation.toml
spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00126-write-capable-delegated-draft-authoring-correction/discussions/delegated-authoring/iss-00126-system-architect-design-cli-85455ab6a889/delegated-write-result.md
spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00126-write-capable-delegated-draft-authoring-correction/discussions/delegated-authoring/iss-00126-system-architect-design-cli-85455ab6a889/manifest.toml
spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00126-write-capable-delegated-draft-authoring-correction/discussions/delegated-authoring/iss-00126-system-architect-design-cli-85455ab6a889/permission-profile.toml
spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00126-write-capable-delegated-draft-authoring-correction/discussions/delegated-authoring/iss-00126-system-architect-design-cli-85455ab6a889/probe-plan.md
spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00126-write-capable-delegated-draft-authoring-correction/discussions/delegated-authoring/iss-00126-system-architect-design-cli-85455ab6a889/session-invocation.toml
spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00126-write-capable-delegated-draft-authoring-correction/discussions/delegated-authoring/iss-00126-system-architect-design-cli-be50b225875f/manifest.toml
spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00126-write-capable-delegated-draft-authoring-correction/discussions/delegated-authoring/iss-00126-system-architect-design-cli-be50b225875f/permission-profile.toml
spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00126-write-capable-delegated-draft-authoring-correction/discussions/delegated-authoring/iss-00126-system-architect-design-cli-be50b225875f/probe-plan.md
spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00126-write-capable-delegated-draft-authoring-correction/discussions/delegated-authoring/iss-00126-system-architect-design-cli-be50b225875f/probe-result.md
spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00126-write-capable-delegated-draft-authoring-correction/discussions/delegated-authoring/iss-00126-system-architect-design-cli-be50b225875f/session-invocation.toml
spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00126-write-capable-delegated-draft-authoring-correction/discussions/delegated-authoring/iss-00126-system-architect-design-desktop-85455ab6a889/manifest.toml
spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00126-write-capable-delegated-draft-authoring-correction/discussions/delegated-authoring/iss-00126-system-architect-design-desktop-85455ab6a889/permission-profile.toml
spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00126-write-capable-delegated-draft-authoring-correction/discussions/delegated-authoring/iss-00126-system-architect-design-desktop-85455ab6a889/probe-plan.md
spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00126-write-capable-delegated-draft-authoring-correction/discussions/delegated-authoring/iss-00126-system-architect-design-desktop-85455ab6a889/session-invocation.toml
spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00126-write-capable-delegated-draft-authoring-correction/discussions/delegated-authoring/iss-00126-system-architect-design-desktop-be50b225875f/manifest.toml
spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00126-write-capable-delegated-draft-authoring-correction/discussions/delegated-authoring/iss-00126-system-architect-design-desktop-be50b225875f/permission-profile.toml
spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00126-write-capable-delegated-draft-authoring-correction/discussions/delegated-authoring/iss-00126-system-architect-design-desktop-be50b225875f/probe-plan.md
spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00126-write-capable-delegated-draft-authoring-correction/discussions/delegated-authoring/iss-00126-system-architect-design-desktop-be50b225875f/session-invocation.toml
spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00126-write-capable-delegated-draft-authoring-correction/discussions/rules.md
spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00126-write-capable-delegated-draft-authoring-correction/plan.md
spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00126-write-capable-delegated-draft-authoring-correction/report.md
spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00126-write-capable-delegated-draft-authoring-correction/requirement.md
spec-dock/scripts/spec_dock_runtime/application/delegated_authoring.py
spec-dock/scripts/spec_dock_runtime/commands/delegated_authoring.py
spec-dock/scripts/spec_dock_runtime/domain/delegated_authoring.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/delegated_authoring.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/delegated_authoring.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/delegated_authoring.py
tests/cli_runtime/test_delegated_authoring.py
tests/domain_runtime/test_delegated_authoring.py
```

## Review Questions

- Does the full Epic diff satisfy the original Epic objective of write-capable delegated draft authoring rather than returning to proposal-only consultants?
- Are `system-architect` and `implementation-planner` constrained to draft-authoring authority, with final promotion retained by the main orchestrator?
- Are Permission Profile / task manifest / probe / diff-gate contracts implemented provider-first and mirrored into dogfooding assets?
- Does `agents.max_depth = 2` improve specialist evidence gathering without allowing peer authoring, dev-coder child delegation, or uncontrolled recursion?
- Are proposed artifacts fail-closed for implementation start, ready, finish, and phase completion until approved metadata exists?
- Is S07 dogfooding evidence substantive enough: target-body delta, generated profile, session invocation, positive probe, negative boundary probes, and main-owned diff gate?
- Do docs/templates/skills and runtime behavior tell the same story, in Japanese-facing docs where appropriate?
- Are tests and manual evidence sufficient for the risk introduced by this harness change?

## Current Known Gate State

- Targeted runtime/managed asset matrix after the authority-boundary fixes: pass (`Ran 111 tests`).
- Fresh code-review after Noether/Mill P1 repairs: pass (Fermat; findings none).
- Main orchestrator promotion recorded `authority=approved` and lifecycle grants on active issue `design.md` / `plan.md` after fresh review and fail-closed verification.
- `git diff --check`: pass.
- `./spec-dock/scripts/spec-dock validate`: pass (`spec-dock: ok (validate) nodes=64`).
- Full `uv run python -m unittest discover -v`: pass after the latest Curie/Ampere P1 repairs (`Ran 892 tests in 436.168s OK`).
- Post-P1 targeted matrix after Curie/Ampere fixes: pass (`Ran 125 tests in 115.036s OK`).
- Post-Zeno positive-probe authority repair focused matrix: pass (`Ran 95 tests in 109.130s OK`).
- Latest P1 repairs included:
  - `authority=approved` + `status!=approved` now fails closed with `status_not_approved`.
  - active issue `design.md` / `plan.md` promoted metadata now use `status=approved`.
  - promotion record `reviewer_evidence_path` must bind to `input_authority.*.reviewer_evidence_path`; mismatch blocks manifest/profile/probe generation before artifacts are written.
  - `positive_probe_result` is now required for approved delegated artifact metadata; missing probe result fails as `incomplete_draft_metadata`, and non-pass values fail as `positive_probe_not_passed`.
  - Epic design Flow-A/B now state delegated authors write candidate ledger / handoff evidence only; the main orchestrator records canonical EAL disposition in scope-local `report.md`.
- Remaining pre-PR gate: none from the corrective G10 review scope. QA has passed (Poincare), the Epic-wide deep-consultant has approved (Aristotle), fresh code-reviewer Chandrasekhar passed with no findings, and fresh spec-reviewer James passed with no findings after Carson P2 fixes. PR update / push and post-push checks remain as delivery steps.
