---
種別: レポート（Issue）
ID: "iss-00123"
タイトル: "Role Scoped Permission Profiles and Task Manifest Probes"
関連GitHub: ["#123"]
状態: "approved"
作成者: "Codex"
最終更新: "2026-05-23"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00112", "init-local-00003"]
---

# iss-00123 Role Scoped Permission Profiles and Task Manifest Probes — レポート（進捗 / 決定 / 結果）

## 進捗サマリー
- 現在地: S01 committed; S02 role-scoped Permission Profile assets, assertions, and probe evidence implemented.
- 未完了: S02 code-reviewer gate, S90, S99.
- 次のマイルストーン: run S02 code-reviewer, fix findings, then commit S02.

## Workflow Delegation Consent
- source: user explicitly requested appropriate sub-agent use for issue requirement/design/plan authoring.
- scope: current repo/worktree, iss-00123, current session, named read-only specialist/reviewer roles.
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
  - Type: fallback
  - Decision: S02 installs role-scoped Permission Profile guardrails for delegated author adapters, but CLI/Desktop OS enforcement remains unverified in this execution environment; write-scoped delegation is therefore not enabled and the roles remain proposal-only until a future task manifest, canonical role skill contract, and host probe all explicitly pass.
  - Disposition: promoted_to_report_and_followup_context
  - Evidence: `codex --version` observed `codex-cli 0.133.0`; no confirmed non-interactive custom-agent enforcement path was available; Goodall P1/P2 findings; S02 report evidence below.

## 証跡採用台帳（Evidence Adoption Ledger / 必須）

| 識別子（ID） | 採用状態（adoption_status） | 出所（source） | 対象（target） | 判断理由（rationale） | 証跡（evidence） | 次アクション（next_action） |
|---|---|---|---|---|---|---|
| EAL-001 | adopted | delegated issue-authoring evidence | `requirement.md`, `design.md`, `plan.md` | Lovelace / Mencius / Archimedes の delegated evidence は issue requirement/design/plan の scope、provider path、step slicing に反映済みで、fresh spec-reviewer が pass したため採用。 | `discussions/20260523t144246z-disc-v1-issue-authoring-delegated-evidence.md`; Heisenberg `review_status: pass` | none |
| EAL-002 | adopted | S01 spec-reviewer `Anscombe` finding | `report.md` | tc-001 hit lines and missing-field checklist were required by the approved plan, so the S01 report evidence was expanded before pass. | Anscombe P1 finding; S01 Step/Test Closure; Anscombe re-review pass | none |
| EAL-003 | adopted | S02 code-reviewer `Goodall` findings | `report.md`, `src/spec_dock/assets/install_root/.codex/agents/*.toml`, `tests/test_init_update.py` | S02 needed exact closure evidence, a decision-ledger fallback entry, and no contradiction between write-scoped adapters and read-only canonical skills; the report and adapter language were updated accordingly. | Goodall P1/P2 findings; D-003; S02 Step/Test Closure evidence | re-run code-reviewer |

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
- status: S01 implementation evidence recorded; spec-reviewer gate pending.
- required evidence: see `plan.md` Spec-Locked Closure Index and final completion conditions.

## 実行証跡
- S01 task manifest and role-scoped Permission Profile contract:
  - changed files:
    - `src/spec_dock/assets/install_root/.codex/AGENTS.md`
    - `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`
  - implementation summary:
    - Added Task Manifest / Permission Profile Gate to spec authoring workflow docs.
    - Added bootstrap guidance requiring resolved target, input revision/hash, allowed paths, forbidden paths, probe commands, cleanup, fallback, and `default_permissions` / `[permissions]` profile evidence.
    - Defined fail-closed fallback for fail-open, unavailable, unreproducible, Desktop/CLI divergent, or mixed sandbox/Permission Profile behavior.
  - tc-001 command:
    - `rg -n 'task manifest|resolved target|input revision|allowed paths|forbidden paths|probe|fallback|default_permissions|permissions' src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md src/spec_dock/assets/install_root/.codex/AGENTS.md`
    - result: pass; provider docs and bootstrap bridge expose all task manifest fields, probe requirements, fallback, and Permission Profile keywords.
  - Step Contract Closure:
    - `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md:96`: defines write-scoped delegated authoring as enabled only when role-scoped Permission Profile and task manifest are both verified.
    - `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md:100`: records `resolved target` as real path, not `spec-dock/active/*` symlink.
    - `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md:101`: records `input revision` as upstream revision/hash/commit.
    - `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md:102`: records `allowed paths` for positive probe write targets.
    - `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md:103`: records `forbidden paths` for implementation/config/test/secrets.
    - `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md:104`: records `probe commands` with positive/negative targets and cleanup.
    - `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md:105`: records `fallback` for fail-open, unavailable, divergent, or unknown enforcement.
    - `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md:106`: records `default_permissions` / `[permissions]` profile evidence.
    - `src/spec_dock/assets/install_root/.codex/AGENTS.md:59`: bootstrap bridge requires resolved target, input revision/hash, allowed paths, forbidden paths, positive/negative probe command, cleanup, fallback, and role-scoped `default_permissions` / `[permissions]`.
  - Test Contract Closure:
    - tc-001: pass.
    - command output evidence: hit lines above from the recorded `rg` command.
    - missing-field checklist:
      - resolved canonical target: present.
      - input revision/hash: present.
      - allowed paths: present.
      - forbidden paths: present.
      - positive probe command: present.
      - negative probe command: present.
      - cleanup: present.
      - fallback policy: present.
      - `default_permissions` / `[permissions]` profile: present.
  - Closure Coverage:
    - AC-001 / EC-001: covered by provider workflow docs and `.codex/AGENTS.md` bootstrap contract.
    - open items: none for S01; S02 owns concrete agent assets, tests, and probe execution evidence.
  - guardrail:
    - `git diff --check`
    - result: pass.
  - reviewer gate:
    - Anscombe (`019e562c-efd4-7041-9fa5-fc387f1c3068`) `review_status: fail`.
    - finding: P1, tc-001 report evidence lacked exact hit lines and field-by-field checklist required by the plan.
    - disposition: added Step Contract Closure, Test Contract Closure, and Closure Coverage evidence with exact hit lines and checklist.
    - re-review: pass; no findings.
  - final reviewer gate:
      - Anscombe (`019e562c-efd4-7041-9fa5-fc387f1c3068`) `review_status: pass`.
      - reason: prior P1 closed; S01 report evidence now contains exact hit-line evidence, missing-field checklist, and Closure Coverage for AC-001 / EC-001.
- S02 agent assets/assertions and probe evidence:
  - changed files:
    - `src/spec_dock/assets/install_root/.codex/agents/system-architect.toml`
    - `src/spec_dock/assets/install_root/.codex/agents/implementation-planner.toml`
    - `.codex/agents/system-architect.toml`
    - `.codex/agents/implementation-planner.toml`
    - `.codex/AGENTS.md`
    - `spec-dock/docs/workflow_spec_authoring.md`
    - `tests/test_init_update.py`
    - `spec-dock/.../iss-00123.../plan.md`
    - `spec-dock/.../iss-00123.../report.md`
    - `spec-dock/.../iss-00123.../discussions/__permission_probe_allowed__.md`
  - implementation summary:
    - Replaced read-only sandbox mode in system architect / implementation planner Codex adapters with role-scoped `default_permissions` profiles.
    - Granted write only to `spec-dock/initiatives` while keeping workspace root, `src`, `tests`, `.codex`, `.agents`, and `spec-dock/system/active-none` read-only and denying `.env*`.
    - Added fail-closed role instructions: Permission Profile is a guardrail for future write-scoped task manifests, not a grant by itself; missing/divergent/unavailable/fail-open probe evidence keeps the role in proposal-only mode with no writes.
    - Reconciled adapter language with canonical read-only skills by requiring proposal-only mode unless the canonical role skill, active issue contract, and host probe all explicitly allow write-scoped draft authoring.
    - Updated managed asset assertions to require Permission Profiles and forbid legacy `sandbox_mode` / `[sandbox_workspace_write]` mixing for delegated author adapters.
    - Ran provider-to-dogfooding update so checked-in `.codex` agent assets and docs remain byte/parity aligned where tests require it.
  - tc-002 commands:
    - `rg -n 'default_permissions|permissions\.|write|read|deny|positive probe|allowed artifact|discussions' src/spec_dock/assets/install_root/.codex src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`
    - result: pass; provider docs/agents expose Permission Profile names, read/write/deny rules, positive probe contract, and discussions evidence path.
    - `uv run pytest tests/test_init_update.py`
    - result: unavailable; failed to spawn `pytest` with `No such file or directory (os error 2)`.
    - fallback command: `uv run python -m unittest tests.test_init_update.TestInitUpdate.test_issue_117_codex_delegated_author_adapters_are_thin_skill_wrappers`
    - result: pass; `Ran 1 test ... OK`.
    - positive probe command: `printf ... > spec-dock/.../iss-00123.../discussions/__permission_probe_allowed__.md`
    - result: pass; issue-local evidence artifact was created and retained as allowed-path evidence.
  - tc-003 commands:
    - `rg -n 'negative probe|forbidden path|implementation code|tests/|package.json|pyproject|deny|blocked' src/spec_dock/assets/install_root/.codex src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`
    - result: pass; provider docs/agents expose forbidden implementation/config/test path and deny/block semantics.
    - hermetic profile resolver for `system-architect.toml`
    - result: pass; `allowed_write ['spec-dock/initiatives']`; forbidden targets under `src/`, `tests/`, and `.codex/` resolved as `blocked_by_read_or_more_specific_rule`.
    - hermetic profile resolver for `implementation-planner.toml`
    - result: pass; `allowed_write ['spec-dock/initiatives']`; forbidden targets under `src/`, `tests/`, and `.codex/` resolved as `blocked_by_read_or_more_specific_rule`.
    - host enforcement note: `codex --version` returned `codex-cli 0.133.0`, but this execution path did not provide a confirmed non-interactive way to bind the custom agent file as an OS-enforced role-scoped profile. Therefore CLI/Desktop enforcement remains unverified and write-scoped delegation is not claimed as enabled.
  - tc-004 command:
    - `rg -n 'fail closed|fail-open|unavailable|divergent|fallback|disable write-scoped delegation|Desktop|CLI' src/spec_dock/assets/install_root/.codex src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`
    - result: pass; docs/agents require proposal-only fallback or disabled write-scoped delegation on unavailable, divergent, unreproducible, fail-open, or unresolved profile behavior.
  - guardrails:
    - `python3 -c 'import tomllib, pathlib; ...'`
    - result: pass; modified provider agent TOML parses.
    - `git diff --check`
    - result: pass.
  - Step Contract Closure:
    - Permission Profile presence:
      - `src/spec_dock/assets/install_root/.codex/agents/system-architect.toml:11`: `default_permissions = "spec_dock_system_architect_draft_authoring"`.
      - `src/spec_dock/assets/install_root/.codex/agents/implementation-planner.toml:11`: `default_permissions = "spec_dock_implementation_planner_draft_authoring"`.
    - Write/read/deny allowlist:
      - `system-architect.toml:55-63` and `implementation-planner.toml:55-63`: `"." = "read"`, `"spec-dock/initiatives" = "write"`, `"src" = "read"`, `"tests" = "read"`, `".codex" = "read"`, `".agents" = "read"`, `".env" = "deny"`, `".env.*" = "deny"`.
    - Network disable:
      - `system-architect.toml:65-66` and `implementation-planner.toml:65-66`: profile network `enabled = false`.
    - Proposal-only / fail-closed guardrail:
      - `system-architect.toml:28-35` and `implementation-planner.toml:28-35`: profile is a future guardrail, not a grant; role remains proposal-only unless canonical skill, issue contract, and host probe explicitly pass; fail-open/unavailable/divergent probes keep no-write mode.
    - Managed asset assertions:
      - `tests/test_init_update.py:2068-2070`: parsed TOML must not contain `sandbox_mode`, must contain `default_permissions`, and that profile must exist under `[permissions]`.
      - `tests/test_init_update.py:2083-2103`: adapter text must include guardrail/proposal-only/no-write, Permission Profile, read/write/deny, network disable, and fail-open evidence fragments.
      - `tests/test_init_update.py:2120-2124`: adapter text must not mix `sandbox_mode =` or `[sandbox_workspace_write]`.
  - Test Contract Closure:
    - tc-002: pass by provider profile rg evidence, unittest fallback managed asset assertion, and retained positive allowed evidence file.
    - tc-003: pass for hermetic profile resolver negative behavior; host OS enforcement remains unverified and is explicitly fail-closed rather than claimed enabled.
    - tc-004: pass by provider fallback policy evidence and D-003 decision.
    - exact managed assertion command: `uv run python -m unittest tests.test_init_update.TestInitUpdate.test_issue_117_codex_delegated_author_adapters_are_thin_skill_wrappers`.
    - exact managed assertion result: `Ran 1 test ... OK`.
    - exact positive probe target: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00123-role-scoped-permission-profiles-task-manifest/discussions/__permission_probe_allowed__.md`.
    - exact hermetic negative resolver output:
      - system architect: `profile spec_dock_system_architect_draft_authoring`; `allowed_write ['spec-dock/initiatives']`; forbidden `src/`, `tests/`, `.codex/` targets -> `blocked_by_read_or_more_specific_rule`.
      - implementation planner: `profile spec_dock_implementation_planner_draft_authoring`; `allowed_write ['spec-dock/initiatives']`; forbidden `src/`, `tests/`, `.codex/` targets -> `blocked_by_read_or_more_specific_rule`.
  - Closure Coverage:
    - AC-002: covered by positive allowed-path profile contract, retained issue-local evidence artifact, and managed assertions.
    - AC-003 / EC-002: covered by read-only/deny profile entries, hermetic negative resolver, and fail-closed decision when host enforcement is unverified.
    - AC-004 / EC-003: covered by proposal-only fallback instructions, D-003, and `workflow_spec_authoring.md` fallback policy.
    - unresolved host/runtime ambiguity: resolved for this issue as disabled / proposal-only, not as verified write-scoped delegation.
  - reviewer gate:
    - Goodall (`019e5634-40ca-72e2-8136-f967f7b66e1f`) `review_status: fail`.
    - findings: P1 missing S02 closure evidence; P1 missing fallback decision ledger; P2 adapter/skill contradiction.
    - disposition: added S02 Step/Test Closure and Closure Coverage, added D-003 fallback decision, and changed adapter contract to proposal-only unless canonical skill/issue/host probe all explicitly permit write-scoped authoring.
    - re-review: pass; no findings.
    - final reviewer gate:
      - Goodall (`019e5634-40ca-72e2-8136-f967f7b66e1f`) `review_status: pass`.
      - reason: prior closure-evidence, fallback-ledger, and adapter/skill contradiction findings are addressed; no remaining S02 defects.

## ブロッカー / 未完了
- S90 and S99 remain.
