---
種別: research
ID: "20260612t072453z-research"
タイトル: "Spec Dock Hub Rename Surface Inventory"
状態: "completed"
作成者: "iwasawayuuta"
最終更新: "2026-06-12"
親: ["iss-00184"]
関連: []
authority: "synthesized"
derived_from:
  - "20260612t070646z-interview"
  - "20260612t071326z-interview"
reflected_to: []
---

# 20260612t072453z-research Spec Dock Hub Rename Surface Inventory

## 調査目的

`spec-driven-tdd-workflow` を互換 alias なしで `spec-dock-hub` へ完全移行するために、現行 surface の更新対象、dogfooding mirror、tests、historical evidence として残す対象を切り分ける。

## sources / 調査方法

- 参照先:
  - `AGENTS.md`
  - `spec-dock/active/issue/requirement.md`
  - `spec-dock/active/epic/requirement.md`
  - `spec-dock/docs/workflow_spec_authoring.md`
  - `spec-dock/docs/workflow_issue.md`
  - `spec-dock/docs/phase_plan_issue.md`
  - `spec-dock/docs/authoring/issue-plan.md`
  - `src/spec_dock/cli.py`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-driven-tdd-workflow/SKILL.md`
  - `.agents/skills/spec-driven-tdd-workflow/SKILL.md`
  - `README.md`
  - `src/spec_dock/assets/spec_dock/docs/README.md`
  - `spec-dock/docs/README.md`
  - `tests/cli_runtime/test_wrappers.py`
  - `tests/cli_runtime/harness.py`
  - `tests/unit/infra/test_init_update.py`
- 検証手順:
  - `rg -n "spec-driven-tdd-workflow|spec-dock-hub|Spec-driven TDD Workflow|Hub:" README.md src/spec_dock/cli.py src/spec_dock/assets/spec_dock/docs/README.md spec-dock/docs/README.md tests/cli_runtime tests/unit/infra src/spec_dock/assets/install_root/.agents/skills .agents/skills`
  - `find src/spec_dock/assets/install_root/.agents/skills -maxdepth 2 -name SKILL.md -print`
  - `find .agents/skills -maxdepth 2 -name SKILL.md -print`
  - Spot inspection of `src/spec_dock/cli.py`, README current skill list, and parity mapping in `tests/unit/infra/test_init_update.py`.

## facts / 観測できた事実

- Provider-side source of truth for installed skills is `src/spec_dock/assets/install_root/.agents/skills/`.
- Dogfooding mirror is `.agents/skills/`.
- Current hub skill exists at:
  - `src/spec_dock/assets/install_root/.agents/skills/spec-driven-tdd-workflow/SKILL.md`
  - `.agents/skills/spec-driven-tdd-workflow/SKILL.md`
- Current hub skill frontmatter uses `name: spec-driven-tdd-workflow`.
- Current hub skill heading is `# Spec-driven TDD Workflow (Hub)`.
- `src/spec_dock/cli.py` contains old name in:
  - `_MANAGED_SKILL_NAMES`
  - `_LEGACY_MANAGED_SKILL_NAMES`
- Current user-facing docs contain old hub path:
  - `README.md`
  - `src/spec_dock/assets/spec_dock/docs/README.md`
  - `spec-dock/docs/README.md`
- Current tests contain old hub path/name in:
  - `tests/cli_runtime/test_wrappers.py`
  - `tests/cli_runtime/harness.py`
  - `tests/unit/infra/test_init_update.py`
- `tests/unit/infra/test_init_update.py` has checked-in dogfooding parity mapping from `.agents/skills/spec-driven-tdd-workflow/SKILL.md` to provider source path.
- Historical specs and discussions under `spec-dock/initiatives/**` contain many old-name references. These include prior issue designs, reports, research, and discussions.
- User answered:
  - Do not keep compatibility alias / forwarding skill.
  - Fully migrate to a new integrated name.
  - Canonical new name is `spec-dock-hub`.

## current surface classification

- Must update as current runtime / shipped asset surface:
  - `src/spec_dock/assets/install_root/.agents/skills/spec-driven-tdd-workflow/SKILL.md` -> `src/spec_dock/assets/install_root/.agents/skills/spec-dock-hub/SKILL.md`
  - `.agents/skills/spec-driven-tdd-workflow/SKILL.md` -> `.agents/skills/spec-dock-hub/SKILL.md`
  - `src/spec_dock/cli.py` managed skill list.
  - README / shipped docs README references.
  - Tests that assert bundled skill paths, skill names, install/update parity, wrapper guidance, and current skill list.
- Must inspect and likely update as generated / dogfooding current docs:
  - `spec-dock/docs/README.md`
  - `spec-dock/.agent/*`, `spec-dock/*.puml`, `spec-dock/dashboard.md` after `sync` if generated projections change.
- Should preserve as historical evidence unless a test or current docs assertion depends on it:
  - Prior issue `requirement.md`, `design.md`, `plan.md`, `report.md`.
  - Prior `discussions/` files that describe the old state at that time.
  - Research transcripts and historical reports.

## inference / 推測

- This issue is not docs-only. It touches shipped installed assets, installer/update behavior, dogfooding mirror, and tests.
- A hard cutover pattern is appropriate because the user explicitly rejects compatibility aliasing and wants no contradictory mixed naming on current surfaces.
- `_LEGACY_MANAGED_SKILL_NAMES` needs careful handling. Keeping the old name there might be acceptable if it means "remove obsolete old managed skill during update", but it must not reintroduce the old skill as a usable compatibility entry.
- Historical specs should not be mass-rewritten because they are evidence of past work, not current runtime/discovery surface.

## unverified / 未検証事項

- Exact tests to update are not yet fully minimized.
  - Need inspect the surrounding assertions before writing the implementation plan.
- Whether `spec-dock sync` changes projections after docs / issue docs updates is not fully known.
  - Need include sync / validate / diff-check in plan.
- Whether there are generated files outside current targeted surfaces that should be updated by installer logic is not yet known.
  - Need use implementation-time `rg` negative inspection to catch current-surface stale references.

## question candidates

- Resolved:
  - Keep compatibility alias? Answer: no.
  - New canonical name? Answer: `spec-dock-hub`.
- No remaining user-intent blocker for requirement phase.
- Design phase may discover technical unknowns, but those should be answered by repository inspection unless they affect product scope.

## terminology conflicts

- Old name:
  - `spec-driven-tdd-workflow`
  - Emphasizes TDD/workflow, which can be confused with issue execution or implementation technique.
- New name:
  - `spec-dock-hub`
  - Emphasizes SpecDock-wide entrypoint. It needs description / heading to preserve "route selector and global invariant surface".
- Historical references:
  - Must be treated as old evidence, not current naming authority.

## edge cases / 具体シナリオ

- Existing consumer repo has `.agents/skills/spec-driven-tdd-workflow/`.
  - `spec-dock update` should not keep the old managed skill as a current entry if the new `spec-dock-hub` is installed.
  - `_LEGACY_MANAGED_SKILL_NAMES` can be used as cleanup metadata only if tests prove old path is removed and not copied back.
- Existing tests assume the old path.
  - Update tests to assert `spec-dock-hub` as the hub and add negative checks for old current-surface path where valuable.
- Historical specs contain old references.
  - Do not rewrite wholesale. Plan should define negative inspection scope narrowly for current surfaces.

## implications / 判断への含意

- Requirement should fix `spec-dock-hub` and no compatibility alias.
- Design should include:
  - Provider skill rename.
  - Dogfooding mirror rename.
  - `src/spec_dock/cli.py` managed / legacy list update.
  - README / shipped docs / dogfooding docs update.
  - Test update for path/name assertions and parity.
  - Negative inspection over current surfaces, excluding historical specs where appropriate.
- Plan should include at least:
  - Scaffold/installer skill asset hard cutover step.
  - Current docs/reference update step.
  - Tests/parity update and focused pytest step.
  - Dogfooding sync / validate / stale reference inspection step.
  - Final QA/code/spec review gates.

## リスク/制約

- Full migration has higher churn than metadata-only clarification.
- Incorrect negative `rg` scope can either miss stale current references or falsely fail on historical evidence.
- Removing old path without installer cleanup tests can leave existing consumer repos with both old and new hub skills after update.

## 反映先

- `requirement.md`
- `design.md`
- `plan.md`
- `report.md` Evidence Adoption Ledger
