---
種別: レポート（Issue）
ID: "iss-00122"
タイトル: "Evidence Adoption Ledger and Bounded Depth2 Delegation"
関連GitHub: ["#122"]
状態: "approved"
作成者: "Codex"
最終更新: "2026-05-23"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00112", "init-local-00003"]
---

# iss-00122 Evidence Adoption Ledger and Bounded Depth2 Delegation — レポート（進捗 / 決定 / 結果）

## 進捗サマリー
- 現在地: S01 and S02 are implemented, reviewed, and committed; S90 dogfooding-visible parity output is generated and under spec-reviewer cleanup.
- 未完了: S90 non-blocking audit cleanup/re-review and S99 final QA/code/spec gates.
- 次のマイルストーン: resolve S90 reviewer cleanup items, re-run S90 spec-reviewer, then continue to S99.

## Workflow Delegation Consent
- source: user explicitly requested appropriate sub-agent use for issue requirement/design/plan authoring.
- scope: current repo/worktree, iss-00122, current session, named read-only specialist/reviewer roles.
- allowed roles: system-architect, implementation-planner, repo-analyst, consultant/deep-consultant if needed, spec-reviewer.
- boundary: no destructive action, no credentialed private browsing, no write-capable delegation without separate approval.

## Delegated Draft Evidence
- evidence artifact path: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/discussions/20260523t144246z-disc-v1-issue-authoring-delegated-evidence.md`
- system-architect `Lovelace`:
  - role: `system-architect`
  - phase: requirement/design input
  - source artifacts: parent Epic requirement/design/plan/report, v0 historical Issue #113〜#118 docs, current Issue scaffold, workflow/phase docs.
  - status: `integrated`
  - integration result: AC/EC/non-scope/provider/test/rollback guidance reflected into this Issue requirement/design.
  - rejected portions: none.
  - blockers: none.
  - reviewer result: Heisenberg `review_status: pass` on canonical docs.
  - promotion decision: not promoted by itself; used as draft evidence only.
- repo-analyst `Mencius`:
  - role: `repo-analyst`
  - phase: design path/test surface input
  - source artifacts: provider source tree, dogfooding paths, test directories.
  - status: `integrated`
  - integration result: provider source, dogfooding validation surface, likely tests, and risk reflected into design/plan.
  - rejected portions: none.
  - blockers: Permission/Profile behavior remains probe-driven and fail-closed where relevant.
  - reviewer result: Heisenberg `review_status: pass`.
  - promotion decision: not promoted by itself; used as draft evidence only.
- implementation-planner `Archimedes`:
  - role: `implementation-planner`
  - phase: plan slicing input
  - source artifacts: workflow_issue.md, phase_plan_issue.md, authoring/issue-plan.md, parent Epic v1 amendment, current Issue docs.
  - status: `integrated_after_canonicalization`
  - integration result: step slicing, delegated roles, closure ids, reviewer mapping reflected into plan.
  - rejected portions: treating original scaffold plans as implementation-ready.
  - blockers: none after canonical docs were rewritten.
  - reviewer result: Heisenberg `review_status: pass`.
  - promotion decision: not promoted by itself; used as draft planning input only.

## Spec Interpretation / Decision Ledger
- D-001:
  - Status: resolved
  - Type: scope
  - Decision: This Issue is an additive v1 amendment and must not rewrite v0 Issue 001〜006 / #113〜#118 plans or reports.
  - Disposition: promoted_to_requirement_design_plan
  - Evidence: parent Epic v1 amendment and this Issue docs.
- D-002:
  - Status: resolved
  - Type: authority
  - Decision: final authority and phase promotion remain with main orchestrator plus fresh reviewer gates.
  - Disposition: promoted_to_requirement_design_plan
  - Evidence: requirement constraints and design interface contract.
- D-003:
  - Status: resolved
  - Type: scope
  - Decision: S90 may include generated dogfooding parity output under `.agents/skills/`, `spec-dock/docs/`, and `spec-dock/templates/` when produced from provider assets by `uv run python -m spec_dock.cli update .`; provider/runtime/test behavior changes remain owned by S01/S02 or a separately amended implementation step.
  - Disposition: promoted_to_plan
  - Evidence: Chandrasekhar S02 P1 finding on out-of-scope dogfooding writes; amended S90 contract in `plan.md`; S90 generated parity command and validation evidence below.

## Spec Authoring Gate
- Requirement Gate:
  - state: passed
  - reviewer: Heisenberg (`019e5570-9ebf-72f0-bdfc-762f906a2c7a`)
  - review_status: pass
  - reviewed scope: requirement.md, design.md, plan.md, report.md, parent epic v1 amendment.
  - investigated facts: parent Epic docs, v0 issue historical evidence, delegated evidence artifact, Avicenna failed-review findings, and Heisenberg re-review evidence.
  - promotion: approved for issue execution; implementation remains not started.
- Design Gate:
  - state: passed
  - reviewer: Heisenberg (`019e5570-9ebf-72f0-bdfc-762f906a2c7a`)
  - review_status: pass
  - finding closure: role/gate/probe-scope issues from Avicenna were fixed before pass.
- Plan Gate:
  - state: passed
  - reviewer: Heisenberg (`019e5570-9ebf-72f0-bdfc-762f906a2c7a`)
  - review_status: pass
  - execution boundary: issue specs are approved, but no issue implementation has started.

## Reviewer History
- Avicenna (`019e556c-cf16-7d23-a773-3a7b23cf89df`): `review_status: fail`
  - findings: iss-00123 required real positive/negative write probe steps; iss-00123 S01 had `.codex/agents` and manual probe evidence under spec-reviewer scope; iss-00122 S01 had `.agents/skills` under spec-reviewer scope.
  - disposition: fixed in plan.md before re-review.
- Heisenberg (`019e5570-9ebf-72f0-bdfc-762f906a2c7a`): `review_status: pass`
  - findings: none.
  - rationale: prior findings closed; no P0/P1 blockers in reviewed scope.

## 受け入れ条件の現在状況
- status: S01/S02/S90 closure evidence recorded and reviewer gates passed; S99 final QA/code/spec gates remain.
- required evidence: see `plan.md` Spec-Locked Closure Index and final completion conditions.

## 実行証跡
- S01 evidence adoption ledger schema:
  - changed files:
    - `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`
    - `src/spec_dock/assets/spec_dock/templates/initiative/report.md`
    - `src/spec_dock/assets/spec_dock/templates/epic/report.md`
    - `src/spec_dock/assets/spec_dock/templates/issue/report.md`
  - implementation summary:
    - Added Evidence Adoption Ledger semantics for `adopted`, `partially_adopted`, `rejected`, `deferred`, `stale`, and `blocked`.
    - Added unresolved `blocked` / `stale` promotion-blocking rule.
    - Added report template table fields for source, target, rationale, evidence, and next action.
  - tc-001 command:
    - `rg -n 'adopted|partially_adopted|rejected|deferred|blocked|stale' src/spec_dock/assets/spec_dock/docs src/spec_dock/assets/spec_dock/templates src/spec_dock/assets/spec_dock/system/active-none`
    - result: pass; provider docs/templates now expose adoption status values and active-none already exposes delegated evidence failure states.
  - tc-002 command:
    - `rg -n 'unresolved|blocked|promotion|cannot promote|must not promote|stale' src/spec_dock/assets/spec_dock/docs src/spec_dock/assets/spec_dock/templates`
    - result: pass; workflow docs/templates state that unresolved `blocked` / `stale` Evidence Adoption Ledger entries block promotion / implementation start / issue ready / issue finish / phase completion.
  - guardrail:
    - `git diff --check`
    - result: pass.
  - reviewer gate:
    - Nash (`019e5613-b432-7c61-a7db-4af725486a01`) `review_status: fail`.
    - finding: P1, tc-001 plan command still searched delegated draft lifecycle state `partially_integrated` instead of Evidence Adoption Ledger state `partially_adopted`.
    - disposition: fixed by amending tc-001 in `plan.md` to search `partially_adopted`, matching requirement AC-001 and the implemented EAL schema.
    - re-review: pass; no findings.
  - final reviewer gate:
    - Nash (`019e5613-b432-7c61-a7db-4af725486a01`) `review_status: pass`.
    - reason: plan tc-001, report evidence, AC-001, and implemented Evidence Adoption Ledger schema now use `partially_adopted`; changed files remain limited to S01 provider docs/templates plus active issue plan/report.
- S02 bounded depth=2 role graph and managed asset assertions:
  - changed files:
    - `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`
    - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-system-architect/SKILL.md`
    - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-implementation-planner/SKILL.md`
    - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-planning/SKILL.md`
    - `tests/test_init_update.py`
  - implementation summary:
    - Added allowed depth=2 graph: main orchestrator -> authoring specialist -> leaf-only evidence producer.
    - Added forbidden depth=3 / grandchild delegation rule.
    - Added child canonical edit, implementation edit, final authority, reviewer-pass, phase promotion, issue ready, and issue finish prohibitions.
    - Added reviewer independence language separating preflight reviewer output from final fresh reviewer pass.
    - Added managed asset assertions in `test_bundled_skill_routing_contract`.
  - tc-003 commands:
    - `rg -n 'depth=2|depth 2|leaf-only|child specialist|reviewer independence|final reviewer' src/spec_dock/assets/install_root/.agents/skills src/spec_dock/assets/spec_dock/docs`
    - result: pass; skills/docs expose allowed depth=2, leaf-only evidence, reviewer independence, and final reviewer semantics.
    - `uv run pytest tests/test_init_update.py`
    - result: unavailable; failed to spawn `pytest` with `No such file or directory (os error 2)`.
    - disposition: plan amended to record this local-runtime fallback condition; the same managed asset assertion gate is executed through unittest below.
    - `uv run python -m unittest tests.test_init_update.TestInitUpdate.test_bundled_skill_routing_contract`
    - result: pass; `Ran 1 test ... OK`.
  - tc-004 commands:
    - `rg -n 'depth=3|grandchild|canonical edit|promotion claim|final authority|forbidden' src/spec_dock/assets/install_root/.agents/skills src/spec_dock/assets/spec_dock/docs`
    - result: pass; skills/docs expose forbidden depth=3, grandchild delegation, canonical edit, promotion/final authority constraints.
    - `uv run pytest tests/test_init_update.py`
    - result: unavailable; failed to spawn `pytest` with `No such file or directory (os error 2)`.
    - disposition: plan amended to record this local-runtime fallback condition; the same managed asset assertion gate is executed through unittest below.
    - `uv run python -m unittest tests.test_init_update.TestInitUpdate.test_bundled_skill_routing_contract`
    - result: pass; `Ran 1 test ... OK`.
  - guardrail:
    - `git diff --check`
    - result: pass.
  - reviewer gate:
    - Chandrasekhar (`019e5619-187e-7ac0-a6a9-536bad87e553`) `review_status: fail`.
    - finding 1: P1, current uncommitted tree contained generated dogfooding parity writes under `.agents/skills/`, `spec-dock/docs/`, and `spec-dock/templates/` while S02 changed-file evidence listed only provider docs/managed assets/tests.
    - disposition 1: plan amended to make S90 explicitly own generated dogfooding parity output and inspection evidence; S02 changed-file evidence remains provider docs/managed assets/tests only.
    - finding 2: P1, planned `uv run pytest tests/test_init_update.py` gate was not recorded.
    - disposition 2: attempted the planned command and recorded its local `pytest` spawn failure; plan amended to permit the unittest managed-asset assertion fallback when pytest is unavailable.
    - re-review: pass.
    - final reviewer gate:
      - Chandrasekhar (`019e5619-187e-7ac0-a6a9-536bad87e553`) `review_status: pass`.
      - reason: no remaining findings; prior P1s are addressed by recorded pytest-unavailable fallback evidence and by moving generated dogfooding parity output into an explicit S90 contract.
- S90 dogfooding-visible parity evidence:
  - status: generated parity output has been produced; spec-reviewer gate pending.
  - generated parity command:
    - `uv run python -m spec_dock.cli update .`
    - result: pass with warning only; `repo-root shortcut already exists (skipped): .../spec`, followed by `spec-dock: ok (update) -> ...`.
  - generated dogfooding parity files:
    - `.agents/skills/spec-dock-epic-planning/SKILL.md`
    - `.agents/skills/spec-dock-implementation-planner/SKILL.md`
    - `.agents/skills/spec-dock-system-architect/SKILL.md`
    - `spec-dock/docs/workflow_spec_authoring.md`
    - `spec-dock/templates/epic/report.md`
    - `spec-dock/templates/initiative/report.md`
    - `spec-dock/templates/issue/report.md`
  - scope note:
    - These dogfooding-visible files are generated parity output owned by S90 evidence. Provider behavior ownership remains with S01/S02, and S90 must not introduce provider/runtime/test edits.
  - tc-090 commands:
    - `./spec-dock/scripts/spec-dock validate`
    - result: pass; `spec-dock: ok (validate) nodes=63`.
    - `rg -n 'adopted|depth=2|reviewer independence|blocked' spec-dock/docs spec-dock/templates spec-dock/system/active-none .agents/skills`
    - result: pass; dogfooding-visible docs/templates/skills expose Evidence Adoption Ledger status values, blocked/stale promotion constraints, bounded depth=2 delegation, and reviewer independence language.
  - guardrail:
    - `git diff --check`
    - result: pass.
  - reviewer gate:
    - pending spec-reviewer.

## ブロッカー / 未完了
- S90 spec-reviewer gate pending.
- S99 not started.
