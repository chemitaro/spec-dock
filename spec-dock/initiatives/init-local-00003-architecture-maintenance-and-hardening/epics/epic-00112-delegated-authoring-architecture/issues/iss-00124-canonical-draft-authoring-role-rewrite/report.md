---
種別: レポート（Issue）
ID: "iss-00124"
タイトル: "Canonical Draft Authoring Role Rewrite"
関連GitHub: ["#124"]
状態: "approved"
作成者: "Codex"
最終更新: "2026-05-23"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00112", "init-local-00003"]
---

# iss-00124 Canonical Draft Authoring Role Rewrite — レポート（進捗 / 決定 / 結果）

## 進捗サマリー
- 現在地: S90 dogfooding parity review fixes are applied; S90 spec-reviewer re-review is pending.
- 完了済み: S01/S02/S03 implementation and reviewer gates; first implementation commit; S90 dogfooding update and inspection evidence.
- 未完了: S90 spec-reviewer gate, S99 final QA/code/spec gates, S90/S99 commits, issue finish.
- 次のマイルストーン: run S90 spec-reviewer, fix findings, then continue to S99.

## Workflow Delegation Consent
- source: user explicitly requested appropriate sub-agent use for issue requirement/design/plan authoring.
- scope: current repo/worktree, iss-00124, current session, named read-only specialist/reviewer roles.
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
  - Type: verification
  - Decision: Planned `uv run pytest tests/test_init_update.py` remains the named closure command for tc-004, but this environment cannot spawn `pytest`; the corrected unittest alternative must include the scaffold creation assertion plus the delegated authoring / bundled skill / adapter assertions.
  - Disposition: superseded_initial_three_test_alternative
  - Evidence: `uv run pytest tests/test_init_update.py` -> `Failed to spawn: pytest / os error 2`; initial three-test alternative was insufficient because it missed `test_init_creates_expected_structure`; corrected command `uv run python -m unittest tests.test_init_update.TestInitUpdate.test_init_creates_expected_structure tests.test_init_update.TestInitUpdate.test_issue_116_delegated_authoring_phase_gate_contract_assets tests.test_init_update.TestInitUpdate.test_bundled_skill_routing_contract tests.test_init_update.TestInitUpdate.test_issue_117_codex_delegated_author_adapters_are_thin_skill_wrappers` -> `Ran 4 tests ... OK`.

## Evidence Adoption Ledger
| ID | adoption_status | source | target | rationale | evidence | next_action |
|---|---|---|---|---|---|---|
| EAL-001 | adopted | doc-writer Ampere | S01/S02 provider skills and phase docs | Reinforced narrow verified-write exception, fail-closed fallback, no previous-phase rewrite, and no final authority. | subagent notification in current thread; diff in provider skills/docs | no further action; step reviewers verify canonical text |
| EAL-002 | adopted | spec-reviewer Socrates | `phase_design.md` and S01/S02 report evidence | Fixed a P1 ambiguity where verified `design.md` draft writes were allowed while broad canonical artifact edits were also forbidden; added line-level source/probe evidence to make tc-001/tc-002 auditable. | Socrates `review_status: fail`; `phase_design.md:82-84`; `workflow_spec_authoring.md:101-111`; role skill snippets listed in Step/Test Closure | rerun S01/S02 spec-reviewer |
| EAL-003 | adopted | code-reviewer Godel | `tests/test_init_update.py`, `phase_design.md`, S03 report evidence | Fixed a P1 stale managed-content assertion caught by `test_init_creates_expected_structure`; removed the broad `canonical artifact edit` phrase from design gate and updated assertions to pin the narrow verified target-draft exception. | Godel `review_status: fail`; `uv run python -m unittest ...test_init_creates_expected_structure ...` first failed, then targeted 4-test rerun passed | rerun S03 code-reviewer |
| EAL-004 | adopted | `uv run python -m spec_dock.cli update .` | dogfooding `.agents/skills` and `spec-dock/docs` | S90 synced provider changes into dogfooding-visible installed assets and docs without provider/runtime/test edits. | update command ok; `./spec-dock/scripts/spec-dock validate` -> `nodes=63`; dogfooding `rg` output lists authority/proposal/fallback fragments | run S90 spec-reviewer |
| EAL-005 | adopted | spec-reviewer Descartes | S01/S02 provider `workflow_spec_authoring.md` corrective follow-up, dogfooding `workflow_spec_authoring.md`, report summary | Fixed a P1 contradiction discovered during S90 where bounded depth=2 text broadly forbade `canonical edit` while verified target draft updates were allowed elsewhere; provider source fix is classified as an S01/S02 corrective follow-up, and S90 will retain only generated dogfooding parity plus report evidence after that corrective commit. | Descartes `review_status: fail`; provider line narrowed; dogfooding re-synced with `uv run python -m spec_dock.cli update .` | commit provider corrective fix, then rerun S90 dogfooding-only review |
| EAL-006 | adopted | spec-reviewer Descartes | S90 scope separation | Accepted S90 reviewer finding that provider source edits cannot be claimed as S90 dogfooding-only work; corrective provider change is separated from S90 parity. | Descartes re-review `review_status: fail` with P1 scope finding | stage provider corrective commit separately from dogfooding-only S90 diff |

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
- Socrates (`019e564e-e225-78c1-bb5f-9a05dabd7565`): `review_status: fail`
  - scope: S01/S02 step reviewer gate.
  - findings:
    - P1: `phase_design.md` allowed verified `design.md` draft writes while also broadly forbidding canonical artifact edits.
    - P2: S01/S02 report evidence summarized probe/source-revision conditions without exact line-level evidence.
  - disposition:
    - P1 fixed by narrowing the forbidden canonical edit statement to edits outside the verified target `design.md` draft.
    - P2 fixed by adding source_revision / positive probe / negative probe / exact path evidence in Step/Test Closure.
- Godel (`019e564e-e2ae-7241-b8c2-f7128da17012`): `review_status: fail`
  - scope: S03 code-reviewer gate.
  - findings:
    - P1: `test_init_creates_expected_structure` still pinned the old `Delegated authoring は draft-only evidence` text and failed against the new scaffold output.
    - P2: `phase_design.md` still used the broad `canonical artifact edit` phrase in the forbidden action bullet.
  - disposition:
    - P1 fixed by updating the scaffold assertion to require `Delegated authoring は authority: proposed / status: draft の draft-only evidence` and previous-phase / implementation/test/config forbidden wording.
    - P2 fixed by replacing the broad phrase with `対象 design.md draft 更新以外の requirement/design/plan/report 正本編集`.
    - verification: `uv run python -m unittest tests.test_init_update.TestInitUpdate.test_init_creates_expected_structure tests.test_init_update.TestInitUpdate.test_issue_116_delegated_authoring_phase_gate_contract_assets tests.test_init_update.TestInitUpdate.test_bundled_skill_routing_contract tests.test_init_update.TestInitUpdate.test_issue_117_codex_delegated_author_adapters_are_thin_skill_wrappers` -> `Ran 4 tests in 0.079s / OK`.
- Socrates (`019e564e-e225-78c1-bb5f-9a05dabd7565`): `review_status: pass`
  - scope: S01/S02 re-review gate.
  - findings: none.
  - rationale: prior P1/P2 findings closed; tc-001/tc-002 have verified target-draft exception, source_revision/probe evidence, and no final-authority/promotion bypass.
- Godel (`019e564e-e2ae-7241-b8c2-f7128da17012`): `review_status: pass`
  - scope: S03 re-review gate.
  - findings: P2 cleanup only, non-blocking.
  - disposition: D-003 updated to supersede the insufficient three-test alternative and name the corrected four-test command.
  - rationale: no remaining P0/P1 findings; scaffold assertion and broad design-gate contradiction fixed.
- Descartes (`019e5656-d5ec-75e1-a4df-1c4e67e54867`): `review_status: fail`
  - scope: S90 dogfooding parity review.
  - findings:
    - P1: dogfooding `workflow_spec_authoring.md` bounded depth=2 text still broadly forbade `canonical edit`, conflicting with verified target-draft authoring.
    - P2: progress summary still described S01/S02/S03 step reviewer gates as pending.
  - disposition:
    - P1 fixed in provider `workflow_spec_authoring.md` and re-synced to dogfooding docs: the ban now excludes verified task-manifest target `design.md` / `plan.md` draft updates and keeps leaf producers canonical-edit-free.
    - P2 fixed by updating the progress summary to S90 re-review pending.
- Descartes (`019e5656-d5ec-75e1-a4df-1c4e67e54867`): `review_status: fail`
  - scope: S90 dogfooding parity re-review.
  - findings:
    - P1: provider source edit was mixed into S90 even though S90 plan forbids provider source changes.
    - P2: post-fix S90 validate / rg / diff-check evidence needed to be recorded after the canonical-edit wording change.
  - disposition:
    - P1 accepted. Provider `workflow_spec_authoring.md` fix is reclassified as S01/S02 corrective follow-up discovered during S90 and will be committed separately before S90 dogfooding-only parity.
    - P2 fixed by recording post-fix validate / rg / diff-check evidence below.

## 受け入れ条件の現在状況
- status: S01/S02/S03 draft implementation evidence recorded; reviewer gates pending.
- required evidence: see `plan.md` Spec-Locked Closure Index and final completion conditions.

## 実行証跡
- S01 implementation:
  - changed files:
    - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-system-architect/SKILL.md`
    - `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`
    - `src/spec_dock/assets/spec_dock/docs/phase_design.md`
  - result: system-architect role now allows bounded draft `design.md` updates only when a verified task manifest, role-scoped Permission Profile, exact target path/revision, and positive/negative probe evidence exist.
  - guardrails: `status: draft`, `authority: proposed`, main orchestrator ownership, no phase promotion, no reviewer-pass claim, no user-dialogue ownership, no previous phase rewrite, and proposal-only fallback on unverified/fail-open/stale host evidence.
  - verification: `rg -n 'system-architect|design.md|authority: proposed|draft|must not promote|final reviewer|previous phase|Permission Profile|proposal-only' src/spec_dock/assets/install_root/.agents/skills/spec-dock-system-architect/SKILL.md src/spec_dock/assets/spec_dock/docs` confirmed the required fragments.
  - reviewer-fix evidence:
    - `src/spec_dock/assets/spec_dock/docs/phase_design.md:82`: allows write-scoped design authoring only for the verified task manifest / role-scoped Permission Profile target `design.md` with `authority: proposed` / `status: draft`.
    - `src/spec_dock/assets/spec_dock/docs/phase_design.md:83`: forbids requirement/design/plan/report canonical edits outside the verified target `design.md` draft.
    - `src/spec_dock/assets/spec_dock/docs/phase_design.md:84`: forbids `requirement.md` / `plan.md` / `report.md` / previous phase artifact rewrites and implementation/test/config edits.
    - `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md:101-107`: requires resolved target, input revision, allowed paths, forbidden paths, positive/negative probe commands, fallback, and Permission Profile summary in the task manifest.
    - `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md:109-111`: requires positive probe success only on allowed artifact/evidence paths and negative probe failure on forbidden implementation/config/test paths; design probe is limited to target `design.md` or allowed design evidence path.
- S02 implementation:
  - changed files:
    - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-implementation-planner/SKILL.md`
    - `src/spec_dock/assets/spec_dock/docs/phase_plan.md`
    - `src/spec_dock/assets/spec_dock/docs/phase_plan_epic.md`
    - `src/spec_dock/assets/spec_dock/docs/phase_plan_issue.md`
  - result: implementation-planner role now allows bounded draft `plan.md` updates only when a verified task manifest, role-scoped Permission Profile, approved requirement/design revisions, exact target path/revision, and positive/negative probe evidence exist.
  - guardrails: `status: draft`, `authority: proposed`, main orchestrator ownership, no phase promotion, no reviewer-pass claim, no implementation-readiness claim, no previous phase rewrite, no completed issue plan/report rewrite, and proposal-only fallback on unverified/fail-open/stale host evidence.
  - verification: `rg -n 'implementation-planner|plan.md|authority: proposed|draft|must not promote|final reviewer|design input|Permission Profile|proposal-only|previous phase|completed issue' src/spec_dock/assets/install_root/.agents/skills/spec-dock-implementation-planner/SKILL.md src/spec_dock/assets/spec_dock/docs` confirmed the required fragments.
  - reviewer-fix evidence:
    - `src/spec_dock/assets/spec_dock/docs/phase_plan.md:73`: allows write-scoped plan authoring only for the verified task manifest / role-scoped Permission Profile target `plan.md` with `authority: proposed` / `status: draft`.
    - `src/spec_dock/assets/spec_dock/docs/phase_plan.md:74`: forbids `requirement.md` / `design.md` / `report.md` / previous phase artifact rewrites, completed issue `plan.md` / `report.md` edits, implementation/test/config edits, promotion, reviewer-pass claims, and implementation-readiness claims.
    - `src/spec_dock/assets/spec_dock/docs/phase_plan.md:76`: falls back to proposal-only / discussions path if Permission Profile / host probe / source revision is unverified, fail-open, Desktop/CLI divergent, or stale.
    - `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md:101-111`: provides shared source_revision, allowed/forbidden path, positive/negative probe, and target-phase probe requirements.
- S03 implementation:
  - changed files:
    - `tests/test_init_update.py`
  - result: managed content assertions now require the delegated authoring docs/skills to expose `authority: proposed`, `status: draft`, Permission Profile / host probe fallback, no previous-phase rewrite, and no completed issue plan/report rewrite.
  - planned command result: `uv run pytest tests/test_init_update.py` failed because `pytest` is not installed/spawnable in this environment: `Failed to spawn: pytest / os error 2`.
  - alternative verification: `uv run python -m unittest tests.test_init_update.TestInitUpdate.test_issue_116_delegated_authoring_phase_gate_contract_assets tests.test_init_update.TestInitUpdate.test_bundled_skill_routing_contract tests.test_init_update.TestInitUpdate.test_issue_117_codex_delegated_author_adapters_are_thin_skill_wrappers` -> `Ran 3 tests in 0.002s / OK`.
  - reviewer-fix verification: after Godel's P1 finding, `uv run python -m unittest tests.test_init_update.TestInitUpdate.test_init_creates_expected_structure tests.test_init_update.TestInitUpdate.test_issue_116_delegated_authoring_phase_gate_contract_assets tests.test_init_update.TestInitUpdate.test_bundled_skill_routing_contract tests.test_init_update.TestInitUpdate.test_issue_117_codex_delegated_author_adapters_are_thin_skill_wrappers` -> `Ran 4 tests in 0.079s / OK`.
- S01/S02/S03 commit:
  - commit: `366db6f feat(authoring): 委任ドラフト作成ロールを提案権限に更新`
  - scope: provider role skills, provider workflow/phase docs, managed content assertions, and issue report evidence.
- S90 dogfooding refresh:
  - changed files:
    - `.agents/skills/spec-dock-system-architect/SKILL.md`
    - `.agents/skills/spec-dock-implementation-planner/SKILL.md`
    - `spec-dock/docs/workflow_spec_authoring.md`
    - `spec-dock/docs/phase_design.md`
    - `spec-dock/docs/phase_plan.md`
    - `spec-dock/docs/phase_plan_epic.md`
    - `spec-dock/docs/phase_plan_issue.md`
  - update command: `uv run python -m spec_dock.cli update .` -> `spec-dock: ok (update)`.
  - validation: `./spec-dock/scripts/spec-dock validate` -> `spec-dock: ok (validate) nodes=63`.
  - dogfooding inspection: `rg -n 'authority: proposed|status: draft|final reviewer|adoption ledger|Permission Profile|proposal-only|previous phase|completed issue|implementation-readiness' .agents/skills spec-dock/docs` found the delegated draft authority, Permission Profile fallback, previous phase rewrite, completed issue plan/report, and implementation-readiness guardrails in generated surfaces.
  - no provider/runtime/test edits in S90: initial `git status --short` after update showed only `.agents/skills/...` and `spec-dock/docs/...` generated dogfooding files modified.
  - Ledger Note: No material implementation decisions beyond the approved plan.
- S01/S02 corrective follow-up discovered during S90:
  - changed provider file:
    - `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`
  - reason: S90 spec-reviewer found that bounded depth=2 text still broadly forbade `canonical edit`, conflicting with verified target `design.md` / `plan.md` draft updates.
  - result: provider wording now forbids canonical edits outside verified target `design.md` / `plan.md` draft updates and keeps leaf-only evidence producers canonical-edit-free.
  - scope disposition: this provider change is not claimed as S90 dogfooding-only work; it is a corrective follow-up to S01/S02 source docs, to be committed separately before S90 parity.
  - post-fix validation:
    - `./spec-dock/scripts/spec-dock validate` -> `spec-dock: ok (validate) nodes=63`
    - `rg -n 'authority: proposed|status: draft|final reviewer|adoption ledger|Permission Profile|proposal-only|previous phase|completed issue|implementation-readiness|canonical edit' .agents/skills spec-dock/docs src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md` -> found provider and dogfooding narrowed canonical edit boundary plus delegated draft guardrails.
    - `git diff --check` -> pass.

## Step Contract Closure
| step | closure id | status | evidence |
|---|---|---|---|
| S01 | tc-001 | pass | `spec-dock-system-architect/SKILL.md:30` permits target `design.md` updates only with verified task manifest / Permission Profile / path revision; `:38-39` forbid all outside-manifest paths and unverified `design.md` writes; `:53-58` require `status: draft`, `authority: proposed`, and `source_revision`; `:64` falls back to proposal-only if requirement revision/profile/probe is missing or stale; `phase_design.md:82-86` clarifies the verified design draft exception and fallback; Socrates re-review pass. |
| S02 | tc-002 | pass | `spec-dock-implementation-planner/SKILL.md:34` permits target `plan.md` updates only with verified task manifest / Permission Profile / approved requirement-design revisions / path revision; `:42-44` forbid outside-manifest paths, unverified `plan.md` writes, previous phase rewrites, and completed issue plan/report rewrites; `:58-63` require `status: draft`, `authority: proposed`, and `source_revision`; `:69` falls back to proposal-only if design evidence/revisions/profile/probe are missing or stale; `phase_plan.md:73-76` records the same plan gate; Socrates re-review pass. |
| S03 | tc-003 | pass | rg inspection confirms adoption/promotion ownership, proposed draft status, narrow verified target-draft exception, and no final authority / reviewer-pass claim boundaries; Godel re-review pass with no P0/P1 findings. |
| S03 | tc-004 | pass | pytest unavailable was recorded; reviewer-identified missing scaffold assertion was added to the unittest alternative, the targeted 4-test unittest command passed, and D-003 supersedes the initial insufficient alternative; Godel re-review pass. |
| S90 | tc-090 | pending re-review | `uv run python -m spec_dock.cli update .`, `./spec-dock/scripts/spec-dock validate`, and dogfooding `rg` inspection confirm generated skill/docs surfaces expose the role rewrite semantics; provider corrective change has been separated from S90 scope and S90 awaits dogfooding-only spec-reviewer re-review. |

## Test Contract Closure
| test id | planned command / evidence | observed result | status |
|---|---|---|---|
| tc-001 | `rg -n 'source_revision|positive|negative|probe|Permission Profile|task manifest|authority: proposed|status: draft|previous phase' ...`; `nl -ba .../spec-dock-system-architect/SKILL.md`; `nl -ba .../phase_design.md`; `nl -ba .../workflow_spec_authoring.md` | exact evidence: role skill lines 30, 38-39, 53-58, 64; phase design lines 82-86; workflow gate lines 101-111; Socrates pass | pass |
| tc-002 | `rg -n 'source_revision|positive|negative|probe|Permission Profile|task manifest|authority: proposed|status: draft|previous phase|completed issue|implementation-readiness' ...`; `nl -ba .../spec-dock-implementation-planner/SKILL.md`; `nl -ba .../phase_plan.md`; `nl -ba .../workflow_spec_authoring.md` | exact evidence: role skill lines 34, 42-44, 58-63, 69; phase plan lines 73-76; workflow gate lines 101-111; Socrates pass | pass |
| tc-003 | `rg -n 'adoption ledger|evidence adoption|proposed|promotion record|final reviewer|owner|authority: proposed|status: draft|previous phase|completed issue|implementation-readiness' ...`; `rg -n 'canonical artifact edit|Delegated authoring は draft-only evidence' ...` | required handoff/adoption/forbidden-authority fragments present; obsolete broad/old fragments absent; Godel pass | pass |
| tc-004 | `uv run pytest tests/test_init_update.py`; corrected alternative `uv run python -m unittest tests.test_init_update.TestInitUpdate.test_init_creates_expected_structure tests.test_init_update.TestInitUpdate.test_issue_116_delegated_authoring_phase_gate_contract_assets tests.test_init_update.TestInitUpdate.test_bundled_skill_routing_contract tests.test_init_update.TestInitUpdate.test_issue_117_codex_delegated_author_adapters_are_thin_skill_wrappers` | pytest spawn unavailable; corrected 4-test alternative passed; Godel pass | pass |
| tc-090 | `./spec-dock/scripts/spec-dock validate`; `rg -n 'authority: proposed|status: draft|final reviewer|adoption ledger|Permission Profile|proposal-only|previous phase|completed issue|implementation-readiness|canonical edit' .agents/skills spec-dock/docs` | post-fix validate passed with nodes=63; dogfooding generated surfaces expose delegated draft authority, Permission Profile fallback, no previous-phase rewrite, completed issue plan/report, implementation-readiness guardrails, and narrowed canonical edit boundary | pending re-review |

## Closure Coverage
| AC / EC | covered by | current evidence |
|---|---|---|
| AC-001 / EC-001 | S01 / tc-001 | system-architect can author only proposed draft design under verified manifest/profile; otherwise proposal-only fallback. |
| AC-002 / EC-002 | S02 / tc-002 | implementation-planner can author only proposed draft plan under verified manifest/profile and approved requirement/design inputs; otherwise proposal-only fallback. |
| AC-003 / EC-003 | S01/S02/S03 / tc-003 | docs and tests preserve main orchestrator final ownership, no phase promotion, no reviewer-pass claim, no user dialogue ownership, and no implementation changes. |
| AC-004 | S01/S02/S03 / tc-004 | docs and tests preserve fail-closed Permission Profile / task manifest gate, no previous-phase rewrite, and no completed issue plan/report rewrite. |
| Dogfooding parity | S90 / tc-090 | generated `.agents/skills` and `spec-dock/docs` expose the same proposed-draft/fail-closed role rewrite semantics. |

## Closure Delta
- `tc-004`: planned pytest command is unavailable in this environment. Initial alternative unittest coverage was insufficient because it missed `test_init_creates_expected_structure`; the corrected 4-test unittest alternative passed and was accepted by the S03 code-reviewer re-review.

## ブロッカー / 未完了
- S90 spec-reviewer re-review is not yet run.
- S99 final quality gates are not yet run.
