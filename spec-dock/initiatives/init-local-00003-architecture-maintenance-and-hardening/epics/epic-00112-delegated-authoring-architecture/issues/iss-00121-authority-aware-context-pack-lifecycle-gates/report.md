---
種別: レポート（Issue）
ID: "iss-00121"
タイトル: "Authority Aware Context Pack and Lifecycle Gates"
関連GitHub: ["#121"]
状態: "approved"
作成者: "Codex"
最終更新: "2026-05-23"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00112", "init-local-00003"]
---

# iss-00121 Authority Aware Context Pack and Lifecycle Gates — レポート（進捗 / 決定 / 結果）

## 進捗サマリー
- 現在地: S01/S02 code-reviewer gate, S90 spec-reviewer gate, and S99 final QA/code/spec gates are passed.
- 未完了: none for iss-00121 implementation scope.
- 次のマイルストーン: commit iss-00121 and run `spec-dock issue finish`.

## Workflow Delegation Consent
- source: user explicitly requested appropriate sub-agent use for issue requirement/design/plan authoring.
- scope: current repo/worktree, iss-00121, current session, named read-only specialist/reviewer roles.
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
  - Type: implementation-time plan amendment
  - Topic: Planned pytest commands unavailable
  - Trigger: `uv run pytest ...` commands for tc-001〜tc-004 could not spawn `pytest`.
  - Ambiguity / constraint: the approved plan named pytest commands, while this repository's documented and available runner is `unittest`.
  - Observed facts: each planned pytest command failed with `Failed to spawn: pytest` / `No such file or directory (os error 2)`; targeted unittest command `uv run python -m unittest tests.domain_runtime.test_authority tests.cli_runtime.test_issue_lifecycle tests.cli_runtime.test_runtime_active_s05` covers the added authority gate, lifecycle, and context-pack assertions.
  - Options considered: add pytest dependency in this issue; keep tc-001〜tc-004 open; amend plan to require pytest attempt plus repo-supported unittest fallback.
  - Decision: Use pytest attempts as required observed evidence and approve the targeted unittest fallback for tc-001〜tc-004 when pytest is unavailable.
  - Rationale: This preserves the planned command intent without introducing a test dependency outside the issue scope.
  - Affected files: `plan.md`, `report.md`.
  - Affected tests: `tests.domain_runtime.test_authority`, `tests.cli_runtime.test_issue_lifecycle`, `tests.cli_runtime.test_runtime_active_s05`.
  - Risk if wrong: a future pytest environment may need a narrower pytest selector; the fallback remains explicit and issue-scoped.
  - Rollback or revisit: add pytest to project tooling and restore pytest-only closure in a follow-up issue.
  - Disposition: applied.
  - Evidence: pytest attempt outputs and passing targeted unittest evidence below.

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
- status: implementation evidence recorded; reviewer gates pending.
- required evidence: see S01/S02/S90/S99 execution evidence below and `plan.md` Spec-Locked Closure Index.

## 実行証跡
- S01 authority/grant read model and validation contract:
  - changed files:
    - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authority.py`
    - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/contracts.py`
    - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/active_store.py`
    - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/set_active.py`
    - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/sync_state.py`
    - `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`
    - `tests/domain_runtime/test_authority.py`
  - implementation summary:
    - exact grant constants: `review_input`, `planning_input`, `design_baseline`, `implementation_start`, `issue_ready`, `issue_finish`, `phase_completion`.
    - fail-closed authority evaluation covers missing/proposed authority, missing exact grant, wildcard grant, incomplete promotion record including `promotion_decision`, stale hash, stale revision, and copied active promotion records.
    - generated active manifest entries include `authority=approved`, exact grants, and runtime active selection promotion records.
  - pytest attempts:
    - `uv run pytest tests/domain_runtime tests/cli_runtime -k 'authority or grants or metadata'`
    - `uv run pytest tests/domain_runtime tests/cli_runtime -k 'stale or promotion or authority'`
    - result: unavailable; `Failed to spawn: pytest` / `No such file or directory (os error 2)`.
  - fallback verification:
    - `uv run python -m unittest tests.domain_runtime.test_authority tests.cli_runtime.test_issue_lifecycle tests.cli_runtime.test_runtime_active_s05`
    - result: pass; `Ran 41 tests ... OK`.
  - closure delta:
    - tc-001: missing authority metadata fails closed.
    - tc-002: proposed authority, missing grant, wildcard grant, stale promotion hash/revision, missing `promotion_decision`, and copied active promotion record fail closed.
  - reviewer gate:
    - Euclid (`019e55ee-8acc-7231-9db0-996da1852fa3`) `review_status: pass`; no findings.

- S02 purpose-aware context-pack and lifecycle blocking:
  - changed files:
    - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authority.py`
    - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_lifecycle.py`
    - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/set_active.py`
    - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/sync_state.py`
    - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/active_store.py`
    - `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
    - `tests/cli_runtime/test_issue_lifecycle.py`
    - `tests/cli_runtime/test_runtime_active_s05.py`
  - implementation summary:
    - `issue_finish` checks active issue authority before GitHub close / active clear.
    - non-finish lifecycle purposes use shared `require_lifecycle_authority`; current runtime has no dedicated implementation-start / issue-ready / phase-completion CLI commands.
    - active-set and sync branch auto-update use the same authority-aware context-pack renderer.
  - pytest attempts:
    - `uv run pytest tests/cli_runtime -k 'context_pack or lifecycle or proposed'`
    - `uv run pytest tests/cli_runtime tests/domain_runtime -k 'grant or lifecycle or approved'`
    - result: unavailable; `Failed to spawn: pytest` / `No such file or directory (os error 2)`.
  - fallback verification:
    - `uv run python -m unittest tests.domain_runtime.test_authority tests.cli_runtime.test_issue_lifecycle tests.cli_runtime.test_runtime_active_s05`
    - result: pass; `Ran 41 tests ... OK`.
  - closure delta:
    - tc-003: proposed/missing authority blocks lifecycle finish before close.
    - tc-004: approved active issue requires exact `issue_finish`; approved entry with only `issue_finish` cannot satisfy `phase_completion`; sync branch auto-update emits authority-aware context-pack guidance.
  - reviewer dispositions:
    - Mendel (`019e55e5-8014-73c3-a7f7-52e1978a8ee1`) failed P1 copied promotion record binding; fixed by `active:<entry.id>` expected revision/hash binding and copied-record tests.
    - Kepler (`019e55e9-c823-7ec1-9f6f-c35f5ef47186`) failed P1 stale test evidence; fixed by refreshing evidence to `Ran 41 tests ... OK`.
    - Euler (`019e55f2-398f-7df3-9f29-cfd2dcb6d923`) failed P1/P2 non-finish coverage and stale revision test gap; fixed by shared lifecycle gate tests and `test_stale_promotion_revision_fails_closed`.
    - Cicero (`019e55f7-5d89-7cf2-9e53-05f666b0c2d4`) failed P1 requested grant/purpose pass-through; fixed by `test_lifecycle_authority_gate_uses_requested_non_finish_grant`.
    - Hooke (`019e55f7-77ba-7420-8e61-4e80872121ab`) passed with P2 context-pack `issue ready` gap; fixed in both renderers and generated active context-pack.
    - Newton (`019e55f2-8f71-7d43-b9b3-bda86b2930b6`) failed P1/P2 helper hard-code, S01 ledger contradiction, missing Hooke/Newton dispositions, and stale counts; fixed by requested grant/purpose helper parameters, Euclid pass ledger, explicit dispositions, and 41-test evidence.
    - Lagrange (`019e55f7-9774-7af2-af70-65de152b4dac`) failed P1/P2 report-ledger gaps; fixed by explicit failed-reviewer dispositions and 41-test evidence.
    - Jason (`019e55fc-98d4-7f03-9b72-1b5dd1c8f05a`) passed with P2 active-set/sync generated context-pack coverage gap; fixed by active-set path assertion.
    - Hypatia (`019e5602-a741-7d43-97eb-da86204152d5`) passed with P2 sync auto-update applied-path coverage gap; fixed by `test_sync_auto_update_from_branch_writes_authority_context_pack`.
    - Turing (`019e5602-a80e-7ea3-bd78-bb99e5501cd9`) passed with P2 missing `promotion_decision` requirement; fixed by required field and `test_missing_promotion_decision_fails_closed`.
  - reviewer gate:
    - Euclid (`019e55ee-8acc-7231-9db0-996da1852fa3`) `review_status: pass`; no findings.
    - Lorentz (`019e55fc-ad6a-7f92-94b7-3d09d67e88ed`) `review_status: pass`; no findings after requested grant/purpose and parity fixes.

- S90 docs impact and dogfooding parity:
  - changed files:
    - generated dogfooding docs copies under `spec-dock/docs/`.
    - generated dogfooding runtime copies under `spec-dock/scripts/spec_dock_runtime/`.
    - issue-local `plan.md` and `report.md` to record generated parity scope and evidence.
  - scope statement:
    - S90 performs no provider docs/runtime/test behavior edits. Provider behavior remains owned by S01/S02 code-reviewer scope. Generated dogfooding docs/runtime files are parity outputs from provider assets and are inspected/recorded under S90.
  - commands:
    - `uv run python -m spec_dock.cli update .`
    - result: pass; local dogfooding workspace updated from provider assets. Warning only: repo-root shortcut already existed and was skipped.
    - `./spec-dock/scripts/spec-dock active set iss-00121`
    - result: pass; active manifest and context-pack regenerated with authority metadata for current issue.
    - `./spec-dock/scripts/spec-dock sync`
    - result: pass; `spec-dock: sync: active unchanged (matched id in branch: iss-00121)`.
    - `./spec-dock/scripts/spec-dock validate`
    - result: pass; `spec-dock: ok (validate) nodes=63`.
    - `rg -n "authority=|issue_finish|promotion_record|proposed or missing authority|Authority" spec-dock/active/context-pack.md spec-dock/.agent/active.json spec-dock/docs/workflow_issue.md spec-dock/docs/workflow_spec_authoring.md`
    - result: pass; docs, active manifest, and context-pack expose matching authority/grant semantics.
  - closure delta:
    - tc-090: pass by update/sync/active regeneration/validate plus rg inspection evidence.
  - reviewer dispositions:
    - Hegel (`019e55e5-b485-71e1-939a-5ab74c9e4084`) failed P1/P2 S90 boundary and runtime active selection promotion record definition; fixed by no-runtime/test-edit statement and workflow doc semantics.
    - Ramanujan (`019e55ea-0c19-7741-bd91-0fe9ca4a6058`) failed P1/P2 provider doc scope and stale count; fixed by assigning provider edits to S01/S02 and refreshing to 41-test evidence.
    - Feynman (`019e55ee-a58f-72e1-b3e7-6efddd64c07d`) `review_status: pass`; no findings.
    - Gauss (`019e5602-a8b4-7a52-a744-f05e5074a317`) failed P1/P2 generated parity scope and sync evidence gap; fixed by amending S90 plan allowed paths for generated dogfooding runtime parity and recording fresh sync/test evidence.

- S99 final quality gates:
  - validation commands:
    - `uv run python -m unittest tests.domain_runtime.test_authority tests.cli_runtime.test_issue_lifecycle tests.cli_runtime.test_runtime_active_s05`
    - result: pass; `Ran 41 tests ... OK`.
    - `./spec-dock/scripts/spec-dock sync`
    - result: pass; `spec-dock: sync: active unchanged (matched id in branch: iss-00121)`.
    - `./spec-dock/scripts/spec-dock validate`
    - result: pass; `spec-dock: ok (validate) nodes=63`.
    - `git diff --check`
    - result: pass.
  - final re-review gates:
    - Kierkegaard (`019e560c-5793-7470-bd59-ee33f316509e`) `review_status: pass`; no findings.
    - Boyle (`019e560c-5845-7f63-9461-f4806531db92`) `review_status: pass`; no findings.
    - Sagan (`019e560c-58e9-7d83-a7a8-06f5de3f8b9f`) `review_status: pass`; no findings after S90 generated docs/runtime parity scope amendment.

## ブロッカー / 未完了
- none.
