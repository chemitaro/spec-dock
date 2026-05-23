---
種別: レポート（Issue）
ID: "iss-00120"
タイトル: "Authority Metadata and Promotion Record Schema"
関連GitHub: ["#120"]
状態: "approved"
作成者: "Codex"
最終更新: "2026-05-23"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00112", "init-local-00003"]
---

# iss-00120 Authority Metadata and Promotion Record Schema — レポート（進捗 / 決定 / 結果）

## 進捗サマリー
- 現在地: S90 dogfooding parity evidence completed after provider S01/S02; S01/S02 reviewer gates are passed.
- 未完了: S90 spec-reviewer gate and S99 remain pending in committed issue evidence.
- 次のマイルストーン: S90 spec-reviewer gate, then S99 final QA/code/spec gates.

## Workflow Delegation Consent
- source: user explicitly requested appropriate sub-agent use for issue requirement/design/plan authoring.
- scope: current repo/worktree, iss-00120, current session, named read-only specialist/reviewer roles.
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
  - Type: implementation-time interpretation
  - Source-agent: doc-writer `Parfit`
  - Topic: S01 explicit grant key spelling
  - Trigger: S01 required an explicit grant key set including write grants and lifecycle grants.
  - Ambiguity / constraint: approved plan names `can_write_requirement` etc. and requires implementation/ready/finish/phase completion grants, but not every lifecycle key spelling was pre-enumerated.
  - Observed facts: AC-003 requires exact grants; S01 closure requires no wildcard semantics; forbidden scope excludes runtime/tests.
  - Options considered: only document five `can_write_*` keys; add lifecycle keys using explicit names; defer lifecycle key names.
  - Decision: Document `can_write_implementation`, `can_mark_issue_ready`, `can_finish_issue`, and `can_complete_phase` alongside the five requested write keys.
  - Rationale: This keeps AC-003 exact and fail-closed without adding runtime behavior.
  - Affected files: `workflow_spec_authoring.md`, report templates, and active-none report placeholders.
  - Affected tests: none edited in S01; docs-only rg inspections passed.
  - Risk if wrong: later S02/runtime assertions may need different key names.
  - Rollback or revisit: revise key spelling during S01 spec-reviewer gate before S02 assertions.
  - Disposition: applied
  - Evidence: `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`, report templates, active-none report placeholders, S01 tc-001〜tc-003 rg evidence below, and Carson S01 `review_status: pass`.
- D-004:
  - Status: resolved
  - Type: implementation-time plan amendment
  - Source-agent: code-reviewer `James`
  - Topic: S02 planned pytest command unavailable
  - Trigger: S02 code-reviewer failed because `tc-004` was claimed with an unplanned unittest fallback after `uv run pytest tests/test_init_update.py` could not spawn `pytest`.
  - Ambiguity / constraint: the approved plan named pytest, while this repository documents and uses `unittest` and has no pytest dependency.
  - Observed facts: `uv run pytest tests/test_init_update.py` fails with `No such file or directory (os error 2)`; `README.md` documents `python -m unittest discover -v`; targeted `uv run python -m unittest tests.test_init_update.TestInitUpdate.test_init_creates_expected_structure` covers the managed scaffold/content assertion surface touched by S02.
  - Options considered: add pytest as a dependency; keep tc-004 open; amend S02 to allow the repo-supported unittest fallback after recording the failed pytest attempt.
  - Decision: Amend S02 `tc-004` to require the pytest attempt and approve targeted unittest fallback when pytest is unavailable in this repo.
  - Rationale: This preserves the originally planned command as observed evidence while aligning closure with the repository's actual supported test runner.
  - Affected files: `plan.md`, `report.md`, `tests/test_init_update.py`.
  - Affected tests: `uv run python -m unittest tests.test_init_update.TestInitUpdate.test_init_creates_expected_structure`.
  - Risk if wrong: broader `tests.test_init_update` failures remain and must be resolved by S90/S99 or later scoped issues before final closure.
  - Rollback or revisit: install/declare pytest and restore pytest-only closure, or split tc-004 into a separate full-suite gate.
  - Disposition: applied.
  - Evidence: S02 code-reviewer James P1 finding, plan amendment below, and Confucius S02 amendment `review_status: pass`.

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
- status: S01 and S02 implementation evidence recorded; S90/S99 and S02 code-reviewer gate remain pending.
- required evidence: see `plan.md` Spec-Locked Closure Index and final completion conditions.

## 実行証跡
- S01 docs-only implementation:
  - changed files:
    - `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`
    - `src/spec_dock/assets/spec_dock/templates/initiative/report.md`
    - `src/spec_dock/assets/spec_dock/templates/epic/report.md`
    - `src/spec_dock/assets/spec_dock/templates/issue/report.md`
    - `src/spec_dock/assets/spec_dock/system/active-none/initiative/report.md`
    - `src/spec_dock/assets/spec_dock/system/active-none/epic/report.md`
    - `src/spec_dock/assets/spec_dock/system/active-none/issue/report.md`
  - tc-001 command:
    - `rg -n 'status|authority|owner_role|draft_author_role|approval|source_revision|approved_revision|approved_hash' src/spec_dock/assets/spec_dock/docs src/spec_dock/assets/spec_dock/templates src/spec_dock/assets/spec_dock/system/active-none`
    - result: pass; required authority metadata fields appear in provider docs, report templates, and active-none report placeholders.
  - tc-002 command:
    - `rg -n 'can_write_requirement|can_write_design|can_write_plan|can_write_report|can_write_discussions|wildcard|\*' src/spec_dock/assets/spec_dock/docs src/spec_dock/assets/spec_dock/templates`
    - result: pass; explicit grant keys appear in `workflow_spec_authoring.md` and report templates, and wildcard grant semantics are denied.
  - tc-003 command:
    - `rg -n 'Promotion Record|promotion_record|approved_hash|approved_revision|reviewer_target_hash|mismatch|stale|promotion' src/spec_dock/assets/spec_dock/docs src/spec_dock/assets/spec_dock/templates src/spec_dock/assets/spec_dock/system/active-none`
    - result: pass; promotion_record fields, approved hash/revision, reviewer target hash, mismatch handling, stale handling, and promotion blocking semantics appear in provider contracts/templates/placeholders.
  - reviewer gate: Carson (`019e55a8-d638-7101-a6a6-a55cbb01d5dc`) `review_status: pass`.
  - reviewer finding disposition: P2 ledger disposition naming fixed by changing D-003 disposition to `applied`.
  - material decision: integrated as D-003 and accepted by S01 spec-reviewer gate.
- S02 managed scaffold/content assertions:
  - changed files:
    - `tests/test_init_update.py`
  - Red / alternative evidence before implementation:
    - `uv run pytest tests/test_init_update.py`
    - result: blocked by missing `pytest` executable in this environment: `error: Failed to spawn: pytest` / `No such file or directory (os error 2)`.
    - fallback command: `uv run python -m unittest tests.test_init_update.TestInitUpdate.test_init_creates_expected_structure`
    - result before final fix: failed once because `docs/workflow_spec_authoring.md` contains `Wildcard grant semantics` while the preliminary assertion looked for lowercase `wildcard grant semantics`.
  - implementation:
    - added managed scaffold/content assertions for authority metadata fields, exact grant keys, and Promotion Record fragments in generated docs/templates/system active-none content.
    - adjusted promotion/grant fragment assertion to case-insensitive matching so contract vocabulary is checked without coupling to sentence-case prose.
  - tc-004 command:
    - `uv run python -m unittest tests.test_init_update.TestInitUpdate.test_init_creates_expected_structure`
    - result: pass; `Ran 1 test ... OK`.
  - broader discovery command:
    - `uv run python -m unittest tests.test_init_update`
    - result: failed; `Ran 174 tests ... FAILED (failures=16)`.
    - failure classes observed: environment missing `pip` for wheel/package tests, dogfooding provider/consumer parity not yet refreshed under S90, cutover snapshot expectations not yet updated for iss-00120〜iss-00125, and existing provider template English-primary prose lint.
    - S02 targeted assertion remained green after the case-insensitive fragment fix.
  - tidy checks:
    - `git diff --check`
    - result: pass.
    - `rg --files | rg '[A-Z]'`
    - result: existing uppercase paths only (`README.md`, `AGENTS.md`, `LICENSE` and existing README mirrors); no new uppercase paths added.
  - closure delta:
    - tc-004: pass by amended targeted unittest fallback because planned pytest command is unavailable in this repository environment.
  - first reviewer gate:
    - James (`019e55b5-77f0-71d2-a30b-7d70c9169518`) `review_status: fail`.
    - finding: P1, `tc-004` was closed with an unplanned fallback.
    - disposition: fixed by D-004 and S02 `tc-004` plan amendment requiring the pytest attempt plus approved unittest fallback.
  - plan amendment reviewer gate:
    - Confucius (`019e55b8-5beb-7eb2-b78d-7f81b2f59efd`) `review_status: pass`.
    - finding: none.
    - reason: the amendment keeps the pytest attempt as required evidence, constrains fallback to pytest unavailability in this repo, and targets the S02 managed scaffold/content assertion surface.
  - second reviewer gate:
    - Bohr (`019e55b9-f1c9-7e90-aa83-1bba5d624cc5`) `review_status: pass`.
    - finding: P2, wildcard grant assertion should prove explicit denial rather than mere mention.
    - disposition: fixed by requiring explicit denial wording and invalid wildcard token coverage in `tests/test_init_update.py`.
  - third reviewer gate:
    - Locke (`019e55bc-6848-74f1-ae44-d960b90d3c71`) `review_status: pass`.
    - finding: P2, invalid wildcard token checks should match exact token forms instead of raw substring `*` or `all`.
    - disposition: fixed by requiring backtick-delimited denied tokens `` `*` ``, `` `can_write_*` ``, and `` `all` ``.
  - final reviewer gate:
    - Hume (`019e55be-5c31-7a13-bd79-e85512a9ad2c`) `review_status: pass`.
    - finding: none.
    - reason: S02 assertions cover authority metadata, exact grant keys, Promotion Record fragments, explicit wildcard denial, and exact denied wildcard token forms.
  - reviewer gate: passed.
- S90 dogfooding parity and docs impact:
  - commands:
    - `uv run python -m spec_dock.cli update .`
    - result: pass; local dogfooding workspace updated from provider assets. Warning only: repo-root shortcut already existed and was skipped.
    - `./spec-dock/scripts/spec-dock sync`
    - result: pass; active unchanged for `iss-00120`, generated state/dashboard refreshed.
    - `./spec-dock/scripts/spec-dock validate`
    - result: pass; `spec-dock: ok (validate) nodes=63`.
    - `rg -n "authority metadata|owner_role|draft_author_role|Promotion Record|promotion_record|wildcard grant semantics|reviewer_target_hash" spec-dock/docs/workflow_spec_authoring.md spec-dock/templates/initiative/report.md spec-dock/templates/epic/report.md spec-dock/templates/issue/report.md spec-dock/system/active-none/initiative/report.md spec-dock/system/active-none/epic/report.md spec-dock/system/active-none/issue/report.md`
    - result: pass; dogfooding docs/templates/system active-none expose authority metadata, Promotion Record / `promotion_record`, exact wildcard denial, and reviewer target hash terms.
  - changed files:
    - `spec-dock/docs/workflow_spec_authoring.md`
    - `spec-dock/templates/initiative/report.md`
    - `spec-dock/templates/epic/report.md`
    - `spec-dock/templates/issue/report.md`
    - `spec-dock/system/active-none/initiative/report.md`
    - `spec-dock/system/active-none/epic/report.md`
    - `spec-dock/system/active-none/issue/report.md`
  - closure delta:
    - tc-090: pass by update/sync/validate plus dogfooding inspection evidence.
  - first reviewer gate:
    - Boole (`019e55c7-b291-7613-a920-e653df84b2fc`) `review_status: fail`.
    - findings:
      - P1: S90 plan said dogfooding paths were inspection-only while report listed generated dogfooding updates.
      - P2: S90 output lacked a Ledger Note or no-material-decision statement.
    - disposition:
      - P1 fixed by amending S90 plan to permit tool-generated dogfooding parity updates via `spec-dock update .` while continuing to forbid manual dogfooding edits and provider edits.
      - P2 fixed by recording no-material-decision for S90 below.
  - material decision: No material interpretation changes in S90; generated dogfooding parity refresh implements the already accepted S01 provider contract.
  - final reviewer gate:
    - Copernicus (`019e55ca-352f-7b71-9da9-fe3bdf84a9b5`) `review_status: pass`.
    - finding: none.
    - reason: prior P1/P2 are closed; dogfooding parity update is tool-generated by `spec-dock update .`, manual dogfooding edits remain forbidden, and no-material-decision is recorded.
  - reviewer gate: passed.

## ブロッカー / 未完了
- S99 is still pending in committed issue evidence.
