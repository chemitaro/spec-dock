---
種別: 実装報告書（Issue）
ID: "iss-00126"
タイトル: "Write Capable Delegated Draft Authoring Correction"
関連GitHub: ["#126"]
状態: "draft"
作成者: "Codex"
最終更新: "2026-05-24"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00112", "init-local-00003"]
---

# iss-00126 Write Capable Delegated Draft Authoring Correction — 実装報告

## 進捗サマリー

- 現在地: S05/S06 fail-closed implementation repair complete; S07 dogfooding actual write pilot substantive draft delta evidence collected; main orchestrator promotion metadata recorded; post-Zeno-P1 positive-probe authority gate repair, focused matrix, `validate`, and `git diff --check` pass; QA, deep-consultant, fresh code-reviewer, and fresh spec-reviewer G10 gates passed.
- 未完了: PR #119 update / push and post-push PR checks。
- 次のマイルストーン: update PR #119 with the completed corrective implementation and verify PR checks/status。

## 仕様解釈・判断台帳

| ID | Status | Type | Raised By | Gap | Options | Decision | Rationale | Disposition | Evidence | Follow-up |
|---|---|---|---|---|---|---|---|---|---|---|
| D-001 | resolved | scope | user / v2 review | Existing implementation is fallback-only and cannot be accepted. | Align to old fallback; implement v2 correction. | Implement v2 correction as additive issue. | Epic v1 requires actual delegated draft authoring. | applied | `discussions/20260524t001711z-disc-write-capable-draft-authoring-resolution-plan-v2.md` | none |
| D-002 | resolved | interface | spec-reviewer Mendel / Meitner / McClintock | CLI helper surface lacked a fixed upstream authority evidence input and reviewer evidence resolution. | Many flags; automatic report inference; required authority file with reviewer evidence path. | Use required `--input-authority-file` containing source revisions, input_authority, promotion_record_path, and reviewer_evidence_path, then verify both referenced evidence sources before profile/probe generation. | This preserves main ownership and prevents helper implementations from inferring approval from raw artifact content or trusting self-attested reviewer verdict/hash fields. | promoted_to_design / promoted_to_plan | `design.md` D-001; `plan.md` S02 | none |
| D-003 | resolved | plan | spec-reviewer McClintock | Implementation steps were not executable step-local contracts. | Keep high-level steps; expand step-local contracts. | Add Step-local 実行契約 with delegation contract, tests, evidence, closure, guardrail, and amendment trigger for S02..G10. | `docs/authoring/issue-plan.md` requires implementation-ready command queue semantics. | promoted_to_plan | `plan.md` Step-local 実行契約 | none |
| D-004 | resolved | gate | spec-reviewer Sartre | EC-004 fixed unresolved ledger entries as blockers, but design/plan did not wire them into runtime authority gate tests. | Treat EAL as observation only; wire EAL into authority gate. | Runtime authority gate reads scope-local report EAL and blocks promotion, implementation start, issue ready, issue finish, and phase completion when unresolved `blocked` / `stale` entries exist. | This makes unresolved review/research debt fail-closed instead of invisible implementation risk. | promoted_to_design / promoted_to_plan | `design.md` D-004/D-005; `plan.md` tc-010 and S05 | none |
| D-005 | resolved | host-surface | spec-reviewer Sartre | Desktop fallback was stated in requirements but not pinned to concrete tests. | Omit Desktop tests; add fallback/non-acceptance test. | `--host-surface desktop` must produce fallback/proposal-only evidence with `acceptance_counted=false` unless CLI-equivalent probes are verified. | This prevents divergent Desktop behavior from satisfying CLI-first acceptance by accident. | promoted_to_design / promoted_to_plan | `design.md` risks; `plan.md` tc-011 and S07 | none |
| D-006 | resolved | invocation | spec-reviewer Gibbs | Plan did not prove the actual delegated author session ran under the generated Permission Profile. | Trust manifest/probe paths only; require session invocation contract. | Add `session-invocation.toml`, supported invocation evidence, selected `default_permissions`, profile identity/hash, and positive probe binding to requirement/design/plan. | This prevents manual, unprofiled, or static broad-profile edits from being reported as write-capable delegated draft authoring. | promoted_to_requirement / promoted_to_design / promoted_to_plan | `requirement.md` AC-006/AC-009; `design.md` D-001; `plan.md` tc-004/S02/S07 | none |
| D-007 | resolved | implementation-scope | spec-reviewer Mencius | S02 added a new CLI command but omitted the manually maintained runtime command registry from allowed implementation paths. | Rely on parser/command discovery; include registry update. | Add `cli/registry.py` to design impact files and S02 allowed paths, and align S06 closure mapping to tc-001..tc-013. | The contracted CLI surface must be reachable through the runtime registry, and closure audit must cover every planned test contract. | promoted_to_design / promoted_to_plan | `design.md` impact files; `plan.md` S02/S06 | none |
| D-008 | resolved | runtime-profile | main orchestrator review | Generated `permission-profile.toml` initially used a custom `[permissions] mode/read/write` shape rather than Codex Permission Profile config syntax. | Keep custom fragment; emit official `default_permissions` / `[permissions.<name>.filesystem]` fragment. | Emit Codex-compatible profile fragments and test that custom mode/read/write shape is absent. | The generated profile must be usable as an actual CLI config layer, not just a project-local manifest. | implemented | `src/.../domain/delegated_authoring.py`; tests `test_delegated_authoring.py`; OpenAI Codex Permissions docs | none |
| D-009 | superseded | host-surface | dogfooding pilot | CLI and Desktop manifest generation initially shared the same task directory and Desktop fallback overwrote CLI evidence. | Accept overwrite; include host surface in task id. | Add `host_surface` to generated task id and regression tests so CLI host-surface eligibility and Desktop fallback evidence remain separate. Manifest generation itself now records `acceptance_counted=false`; acceptance is counted only after actual write/probe/diff/report evidence. | This preserves CLI evidence independently from Desktop fallback without treating manifest generation as final acceptance. | superseded_by_D-012 | `application/delegated_authoring.py`; `tests/domain_runtime/test_delegated_authoring.py`; S07 generated artifacts | regenerate S07 evidence under updated contract |
| D-010 | resolved | dogfooding-parity | doc-writer ledger note | Provider docs/templates were updated; dogfooding `spec-dock/` mirror parity was not yet refreshed. | Leave dogfooding mirror untouched; run repo-local update. | Ran `uv run python -m spec_dock.cli update .` after provider changes. | S90 requires provider/dogfooding parity before final gates and the CLI pilot needs the dogfooding runtime command surface. | applied | `spec-dock/docs`, `spec-dock/templates`, `spec-dock/system`, `spec-dock/scripts` refreshed | none |
| D-011 | resolved | probe-safety | S07 probe closure | Generated negative probe sentinel was initially placed inside the write-allowed task directory, so it could not prove denial. | Keep sentinel in task_dir; move sentinel to scope-local write-denied disposable path. | Move generated sentinel to `discussions/.<task-id>.spec-dock-permission-probe-denied`, outside task_dir and outside generated workspace write rules. | Negative probe must test a denied boundary without touching real artifacts/source/tests/config/secrets. | implemented | `src/.../application/delegated_authoring.py`; `tests/domain_runtime/test_delegated_authoring.py`; `tests/cli_runtime/test_delegated_authoring.py`; regenerated probe plans | none |
| D-012 | resolved | plan-review | fresh spec-reviewer Turing / Lorentz | Parent Epic design still treated discussions ledger as canonical, S05 gate surfaces were not executable enough, `stale_check` used both `pass` and `fresh`, and negative probe tests were not boundary-specific. | Ignore because implementation is already underway; repair the correction plan before further acceptance claims. | Update Epic design / v2 discussion / issue requirement-design-plan so canonical EAL is report-owned, S05 names validate/context-pack/issue-finish surfaces, `stale_check=fresh` is the only pass value, and negative probes cover each forbidden boundary category. | The correction issue exists to repair requirement drift; accepting a vague or inconsistent plan would reproduce the same failure mode. | promoted_to_epic_design / promoted_to_requirement / promoted_to_design / promoted_to_plan / fresh_re-review_passed | `spec-dock/active/epic/design.md`; `requirement.md` AC-001/AC-005/AC-007; `design.md` D-001/D-003/D-004; `plan.md` S02/S05 contracts; Lorentz fresh spec-reviewer `review_status=pass`, findings none | none |
| D-013 | resolved | invocation-environment | S07 pilot | The first nested `codex exec --ignore-user-config --profile-v2 ...` run still entered `sandbox: read-only`, so the generated Permission Profile was not the effective write boundary. | Treat as pass because negative probes failed; isolate the actual author session config. | Use temporary `CODEX_HOME` copies containing auth plus the generated Permission Profile as `config.toml`, then run `codex exec` and require `sandbox: custom permissions` before counting S07. | S07 must prove write-capable delegated drafting under the generated profile, not merely show that a read-only sandbox blocks writes. | applied | `discussions/delegated-authoring/iss-00126-system-architect-design-cli-85455ab6a889/delegated-write-result.md`; `discussions/delegated-authoring/iss-00126-implementation-planner-plan-cli-98a21ff9ddee/delegated-write-result.md` | remove temporary profile files before close |
| D-014 | resolved | diff-gate | S07 pilot | Nested author sessions could not run `git diff/status` because their restricted profile did not allow the external gitdir referenced by the worktree. | Broaden delegated write profile to include `.git/worktrees`; keep delegated profile narrow and let main run the diff gate. | Treat delegated-session git failure as expected permission-boundary evidence and perform final diff/validate checks from the main orchestrator session. | The delegated author should not need write or read access to external worktree metadata; authoritative diff and validation gates belong to the main orchestrator. | applied | `git diff --check`; `./spec-dock/scripts/spec-dock validate`; targeted unittest matrix | none |
| D-015 | resolved | authority-grants | fresh spec-reviewer Heisenberg | The proposed plan metadata carried `grants=implementation_start`, contradicting the rule that proposed artifacts cannot grant downstream implementation authority. | Keep implementation_start because the file is plan.md; restrict proposed grants to review/planning input. | Change proposed plan metadata and delegated write result evidence to `grants=review_input,planning_input`; implementation authority remains available only after main promotion and approval. | Draft authoring proves write capability, not downstream authority. The main orchestrator owns promotion and implementation-start authority. | applied | `plan.md#delegated-draft-pilot-metadata`; `discussions/delegated-authoring/iss-00126-implementation-planner-plan-cli-98a21ff9ddee/delegated-write-result.md`; Heisenberg finding; later authority-boundary reviewers | none |
| D-016 | resolved | host-enforcement | QA reviewer Kant / deep-consultant Lagrange / S07 rerun | S07 evidence was metadata-only, and rerunning substantive body edits under exact-file and issue-cwd Permission Profiles inside the parent sandbox failed before filesystem operation with `sandbox-exec: sandbox_apply: Operation not permitted`. | Count metadata-only evidence; broaden to workspace write; run the delegated CLI session outside the parent sandbox with issue-cwd Permission Profile only. | Use the issue-cwd Permission Profile as the supported dogfooding invocation for S07, run nested `codex exec` outside the parent sandbox boundary, and count only the resulting non-metadata body deltas plus manifest/session/profile/probe/diff-gate evidence. | The initial failure was caused by nesting Codex's sandbox helper inside the parent sandbox. The supported invocation still keeps the delegated author profile narrow: only the target artifact and its task evidence directory are writable, while requirement/peer/report/source/tests/config/secrets boundaries remain denied. | applied | failed nested sessions `019e5838-7429-71f3-8a64-1db94879bc17`, `019e5838-9547-7122-a740-389effdd9ed5`, `019e583a-8e24-7cb3-8792-aef2b303ee8f`, `019e583a-bf2a-7de3-8444-3ee706d91bc9`; successful issue-cwd sessions `019e583f-3894-7893-b083-9d22024b6067`, `019e583f-7723-7570-8633-31d1b3b78b24`; `design.md` D-001 body delta; `plan.md` tc-s07-009 body delta; delegated write result files | final promotion completed; fresh spec/code G10 re-review passed; PR update is unblocked |

## 証跡採用台帳（Evidence Adoption Ledger）

| ID | adoption_status | source | source_role | claim | target_artifact | target_section | rationale | evidence_strength | evidence_path | adopter | reviewer | blocking | next_action |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| EAL-001 | adopted | gap analysis v1 | main orchestrator + consultants | Current adapter/config/tests/docs contradict Epic v1 actual delegated draft authoring. | requirement.md, design.md, plan.md | scope, affected files, acceptance | The gap analysis inventories concrete contradictions and affected surfaces that define this corrective issue. | high | `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/discussions/20260523t235448z-disc-write-capable-draft-authoring-gap-analysis.md` | main orchestrator | Banach spec-reviewer pass | no | none |
| EAL-002 | adopted | resolution plan v2 | deep-consultant / researcher / repo-analyst / spec-reviewer | CLI-first task manifest, input_authority, non-destructive probe, report-owned ledger, exact file write acceptance, and depth=2 constraints are the correction baseline. | requirement.md, design.md, plan.md | requirements, architecture decisions, implementation steps | The plan v2 resolved prior open questions and is adopted through this issue's S01 fresh spec-reviewer gate rather than a self-attested prose reviewer claim. | high | `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/discussions/20260524t001711z-disc-write-capable-draft-authoring-resolution-plan-v2.md`; reviewer evidence: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00126-write-capable-delegated-draft-authoring-correction/report.md#spec-authoring-gate` | main orchestrator | Banach spec-reviewer pass | no | none |
| EAL-003 | adopted | dev-coder runtime implementation | dev-coder Carver | S02/S05 runtime helper, CLI command, authority metadata validation, and EAL issue-finish block are implemented and tested. | code/tests/report.md | S02, S05, S06 | Worker results were re-run by the orchestrator and targeted runtime suite passed. | high | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/{domain,application,commands}/delegated_authoring.py`; `tests/domain_runtime/test_delegated_authoring.py`; `tests/cli_runtime/test_delegated_authoring.py`; `tests/domain_runtime/test_authority.py`; `tests/cli_runtime/test_issue_lifecycle.py` | main orchestrator | Poincare QA pass; Aristotle deep approve; Chandrasekhar code-review pass; James spec-review pass | no | none |
| EAL-004 | adopted | doc-writer docs/config implementation | doc-writer Leibniz | S03/S04 docs/templates/agent/config now separate read-only specialist consent from write-scoped authoring, use depth=2 constraints, and keep Desktop/manual fallback out of acceptance. | docs/templates/agent-config/report.md | S03, S04 | Targeted managed asset tests passed and repo-local update refreshed dogfooding mirrors. | high | `src/spec_dock/assets/spec_dock/docs/*`; `src/spec_dock/assets/install_root/.codex/*`; `tests/test_init_update.py` | main orchestrator | Poincare QA pass; Aristotle deep approve; Chandrasekhar code-review pass; James spec-review pass | no | none |
| EAL-005 | adopted | S07 dogfooding pilot | codex-cli write sessions | Updated D-012 CLI issue-cwd profiles produced substantive non-metadata body deltas in exact target `design.md` and `plan.md`, preserved draft/proposed authority until main promotion, and recorded manifest/session/profile/probe/diff-gate evidence without granting downstream authority. | design.md, plan.md, report.md | S07 | The evidence proves generated profiles can be selected, delegated authors can edit the intended draft artifact body, negative boundaries deny forbidden writes, proposed artifacts remain fail-closed until main promotion, and main promotion then records approved lifecycle grants. Fresh code/QA/spec findings were repaired, QA/deep/code/spec G10 gates passed, and post-P1 verification passed. | high | `design.md#d-001-delegated-write-session-contract`; `plan.md#s07-step-local-contract`; `design.md#delegated-draft-pilot-metadata`; `plan.md#delegated-draft-pilot-metadata`; `discussions/delegated-authoring/iss-00126-system-architect-design-cli-85455ab6a889/session-invocation.toml`; `discussions/delegated-authoring/iss-00126-system-architect-design-cli-85455ab6a889/delegated-write-result.md`; `discussions/delegated-authoring/iss-00126-implementation-planner-plan-cli-98a21ff9ddee/session-invocation.toml`; `discussions/delegated-authoring/iss-00126-implementation-planner-plan-cli-98a21ff9ddee/delegated-write-result.md`; successful sessions `019e583f-3894-7893-b083-9d22024b6067`, `019e583f-7723-7570-8633-31d1b3b78b24`; failed nested sessions retained as fallback evidence `019e5838-7429-71f3-8a64-1db94879bc17`, `019e5838-9547-7122-a740-389effdd9ed5`, `019e583a-8e24-7cb3-8792-aef2b303ee8f`, `019e583a-bf2a-7de3-8444-3ee706d91bc9`; post-P1 `validate` / full-suite pass; G10 shared diff exact working-tree scope | main orchestrator | Fermat prior code pass; Poincare QA pass; Aristotle deep approve; Chandrasekhar code-review pass; James spec-review pass | no | update PR #119 |

## Spec Authoring Gate

- Plan Review Repair Gate:
  - first reviewer: Turing (`019e57f5-9cb6-7880-89f0-ab879558c034`)
  - first review_status: fail
  - findings fixed:
    - parent Epic design canonical EAL now points to scope-local `report.md`; delegated authors write candidate evidence only.
    - S05 plan contract names executable validate / context-pack-active rendering / issue-finish surfaces.
    - `stale_check` is standardized to literal `fresh`.
    - negative probe contract is boundary-specific for requirement, peer artifact, report, source, tests, Codex config, agent assets, and env-like boundaries.
  - re-reviewer: Lorentz (`019e57fe-195a-7482-a471-a696c5d1702e`)
  - re-review_status: pass
  - re-review findings: none
  - validation:
    - `git diff --check`: pass
    - `./spec-dock/scripts/spec-dock validate`: pass (`nodes=64`)

- Requirement Gate:
  - state: passed
  - reviewer: Banach (`019e57af-ff52-76d2-9f07-28c5d41f9530`)
  - review_status: pass
  - promotion_record:
    - promotion_id: `iss-00126-requirement-promotion-20260524t025618z`
    - authority: approved
    - grants: `review_input`, `planning_input`
    - approved_hash: `99443200ee057f3ab194dc7fbd1717ace06ceb31d28552d8a8a2d3095c40fcd2`
    - promotion_record_path: `discussions/delegated-authoring/input-authority/requirement-promotion.json`
    - reviewer_evidence_path: `discussions/delegated-authoring/input-authority/requirement-reviewer.json`
- Design Gate:
  - state: passed
  - reviewer: Banach (`019e57af-ff52-76d2-9f07-28c5d41f9530`)
  - review_status: pass
  - promotion_record:
    - promotion_id: `iss-00126-design-promotion-20260524t025618z`
    - authority: approved
    - grants: `design_baseline`
    - approved_hash: `59db046e937ae8c36a48e2f81979c79a35fdcdbfd61e603dad02329047c328db`
    - promotion_record_path: `discussions/delegated-authoring/input-authority/design-promotion.json`
    - reviewer_evidence_path: `discussions/delegated-authoring/input-authority/design-reviewer.json`
- Plan Gate:
  - state: passed
  - reviewer: Banach (`019e57af-ff52-76d2-9f07-28c5d41f9530`)
  - review_status: pass
  - note: Plan Gate authorizes the issue plan itself; implementation-planner dogfooding input uses Requirement Gate grants plus Design Gate `design_baseline` as recorded above.

## Workflow Delegation Consent

| consent source | repo/worktree | issue | session | named roles | boundary | expires | denied/unavailable | next action |
|---|---|---|---|---|---|---|---|---|
| user instruction | current repo/worktree | iss-00126 | current session | spec-reviewer, code-reviewer, qa-reviewer, deep-consultant, doc-writer, dev-coder | same repo, active issue, bounded role scope; no destructive action, credentialed private browsing, PR merge, or scope expansion | issue complete / scope change / host policy conflict / user revocation | none | proceed |

## 実装記録

### S01 issue spec authoring

- target:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - `report.md`
- result:
  - complete
- evidence:
  - `git diff --check`: pass
  - `./spec-dock/scripts/spec-dock validate`: pass (`nodes=64`)
  - fresh spec-reviewer Banach: pass, findings none, confidence 0.88

### S02 delegated authoring manifest / permission helper

- result:
  - complete
- implemented:
  - `spec-dock delegated-authoring manifest --role ... --scope ... --target ... --host-surface ... --input-authority-file ...`
  - JSON/TOML `input_authority` validation。
  - generated `manifest.toml`, Codex-compatible `permission-profile.toml`, `probe-plan.md`, and `session-invocation.toml`。
  - CLI/Desktop host surface separation so fallback evidence does not overwrite CLI acceptance evidence。
- red / alternative evidence:
  - absent module/command tests failed before implementation, per dev-coder report。
- green evidence:
  - `uv run python -m unittest tests.domain_runtime.test_delegated_authoring tests.cli_runtime.test_delegated_authoring tests.domain_runtime.test_authority tests.cli_runtime.test_issue_lifecycle`: pass (`Ran 44 tests`)。

### S03 workflow docs / templates / issue-plan authoring contract

- result:
  - complete
- implemented:
  - workflow docs and report templates record task manifest, input authority, session invocation, probe, diff gate, fallback, and Evidence Adoption Ledger destinations。
  - read-only specialist consent and write-scoped delegated authoring consent are separated。
- green evidence:
  - targeted `tests.test_init_update` managed asset tests: pass (`Ran 4 tests`)。

### S04 adapter / config / role skill alignment

- result:
  - complete
- implemented:
  - provider and dogfooding `.codex/config.toml` use `agents.max_depth = 2`。
  - `system-architect` / `implementation-planner` adapters describe fail-closed write-scoped authoring instead of fixed read-only/proposal-only blocking language。
  - role skills include child allowlist, max child calls, leaf-only, no-grandchild, no peer author, and no dev-coder child。
- green evidence:
  - TOML parse reported `toml ok` from doc-writer。
  - targeted managed asset tests: pass。

### S05 runtime authority gate

- result:
  - complete
- implemented:
  - draft metadata validation requires manifest/profile/session/probe fields。
  - proposed artifacts cannot satisfy lifecycle authority gates。
  - active synthetic approval is not artifact approval。
  - issue finish blocks when scope-local Evidence Adoption Ledger has unresolved `blocked` / `stale` entries。
- green evidence:
  - `uv run python -m unittest tests.domain_runtime.test_authority tests.cli_runtime.test_issue_lifecycle`: included in 44-test targeted runtime pass。

### S06 managed asset and runtime tests

- result:
  - complete
- coverage:
  - `tc-001`..`tc-004`: delegated authoring domain/CLI tests。
  - `tc-005`..`tc-007`: managed asset tests。
  - `tc-008`..`tc-010`: authority/lifecycle tests。
  - `tc-011`..`tc-012`: dogfooding manifest/session evidence, exact target draft writes, positive probe results, denied negative sentinels, and Desktop fallback non-acceptance evidence。
  - `tc-013`: QA/deep/code/spec G10 gates passed after latest evidence refresh and Carson P2 repair。

### S07 dogfooding actual write pilot

- result:
  - complete; delegated draft evidence was promoted by the main orchestrator after fresh review / fail-closed repair, and fresh spec/code G10 re-review passed before PR update.
  - metadata-only write evidence is retained as partial fallback evidence, but final S07 evidence now includes non-metadata body deltas in both target artifacts.
- superseded pre-D-012 evidence:
  - design CLI manifest:
    - `discussions/delegated-authoring/iss-00126-system-architect-design-cli-be50b225875f/manifest.toml`
    - `permission_profile_name=spec-dock-iss-00126-system-architect-design-cli-be50b225875f`
    - `acceptance_counted=true` (stale pre-D-012 evidence; must be regenerated and not reused for final acceptance)
    - `manifest_hash=def423816fb282794608050bf39741765071a51a48d03e202df4d26c8e68a310`
    - `session_invocation_hash=2036ce127c521fd4a252c6dbb94344d5d83eb14a7b5b070a4313524e08d846c2`
  - plan CLI manifest:
    - `discussions/delegated-authoring/iss-00126-implementation-planner-plan-cli-e03b5e56572a/manifest.toml`
    - `permission_profile_name=spec-dock-iss-00126-implementation-planner-plan-cli-e03b5e56572a`
    - `acceptance_counted=true` (stale pre-D-012 evidence; must be regenerated and not reused for final acceptance)
    - `manifest_hash=76904f5528514d097ce0196891ff09ec4732b43469ba8f7fae70329bb8160b33`
    - `session_invocation_hash=54550c4c283e6e97fcf356058d21c650236ead2bb615b16687a5ebb778750dab`
  - Desktop fallback manifest:
    - `discussions/delegated-authoring/iss-00126-system-architect-design-desktop-be50b225875f/manifest.toml`
    - `acceptance_counted=false`
- regenerated D-012 evidence:
  - design CLI manifest:
    - `discussions/delegated-authoring/iss-00126-system-architect-design-cli-85455ab6a889/manifest.toml`
    - `permission_profile_name=spec-dock-iss-00126-system-architect-design-cli-85455ab6a889`
    - `permission_profile_hash=e4c7fa0f464ac3556cf7e0df8861b25e87c312a449f124f9a18d1b0f44accbdf`
    - `manifest_hash=898427a15c869b7fce26aee647c4537b1ed4f0dda98e9931d6f67b4ed530e9ab`
    - `session_invocation_hash=1659b5cbca0fbdf93d6328fe6b94925d08801b7bb61c306208f9f9bc7aed23f1`
    - `acceptance_counted=false` at manifest generation time by design.
  - plan CLI manifest:
    - `discussions/delegated-authoring/iss-00126-implementation-planner-plan-cli-98a21ff9ddee/manifest.toml`
    - `permission_profile_name=spec-dock-iss-00126-implementation-planner-plan-cli-98a21ff9ddee`
    - `permission_profile_hash=05529d47e9aa802b46dfb5eb3bb4fe1f12a3a1a661f5f0876b5ced3a93134b59`
    - `manifest_hash=10bf95dfc8f112527f7cce3482ab4d4a210f51208efa5c330efe5821ca48a59f`
    - `session_invocation_hash=ecf6ee59bdb484fe9735478eab768e74fa5eb4e03353b42cadd0cafd685a17dc`
    - `acceptance_counted=false` at manifest generation time by design.
  - Desktop fallback manifest:
    - `discussions/delegated-authoring/iss-00126-system-architect-design-desktop-85455ab6a889/manifest.toml`
    - `permission_profile_name=spec-dock-iss-00126-system-architect-design-desktop-85455ab6a889`
    - `host_surface_acceptance_eligible=false`
    - `acceptance_counted=false`
  - `acceptance_counted=false` in delegated result / manifest artifacts is a pre-promotion, delegated-author-local marker. It means the delegated session itself does not claim final acceptance or downstream authority. S07 / E-AC-003 / E-AC-004 are counted only after the main orchestrator adopts the substantive delegated draft body deltas, records approved metadata / promotion evidence, and verifies positive probe, negative boundary probes, and diff gate evidence.
- actual write evidence:
  - first attempted nested `codex exec --ignore-user-config --profile-v2 ...` was not counted because it still ran as `sandbox: read-only` and could not prove write-capable delegated drafting.
  - external `codex exec` system-architect session ran with the generated Permission Profile as the effective `config.toml` under isolated temporary `CODEX_HOME`, reported `sandbox: custom permissions`, and updated the `## Delegated Draft Pilot Metadata` block in `design.md` only。
  - external `codex exec` implementation-planner session ran with the generated Permission Profile as the effective `config.toml` under isolated temporary `CODEX_HOME`, reported `sandbox: custom permissions`, and updated the `## Delegated Draft Pilot Metadata` block in `plan.md` only。
  - both sessions returned no final authority, promotion, reviewer-pass, implementation-readiness, or user-dialogue ownership claim。
  - fresh QA/deep review rejected metadata-only updates as insufficient substantive draft evidence.
  - substantive body-delta reruns under exact-file profiles and issue-cwd relative profiles failed inside the parent sandbox before read/write with `sandbox-exec: sandbox_apply: Operation not permitted`; no files were modified by those reruns.
  - escalated outer execution removed the parent sandbox nesting failure while preserving the delegated issue-cwd Permission Profile. The system-architect session `019e583f-3894-7893-b083-9d22024b6067` updated `design.md` D-001 body text and its task-local `delegated-write-result.md` only.
  - escalated outer execution removed the parent sandbox nesting failure while preserving the delegated issue-cwd Permission Profile. The implementation-planner session `019e583f-7723-7570-8633-31d1b3b78b24` updated `plan.md` S07 body text and its task-local `delegated-write-result.md` only.
  - the issue-cwd profile is the supported S07 invocation shape for this dogfooding run: target artifact plus task evidence directory are writable; requirement, peer artifact, report, source, tests, Codex config, agent assets, and env-like boundaries remain denied.
- positive / negative probe evidence:
  - design:
    - `positive_probe_result=pass` in `design.md` metadata。
    - `delegated-write-result.md` records profile `spec-dock-iss-00126-system-architect-design-cli-85455ab6a889`, `default_permissions` match, `permission_profile_hash=e4c7fa0f464ac3556cf7e0df8861b25e87c312a449f124f9a18d1b0f44accbdf`, and all required negative categories denied with `Operation not permitted`。
    - denied categories: `requirement.md`, peer artifact, `report.md`, `src/`, `tests/`, `.codex/`, `.agents/`, `.env*`。
    - orchestrator post-check confirmed no `85455ab6a889` negative sentinel path exists。
  - plan:
    - `positive_probe_result=pass` in `plan.md` metadata。
    - `delegated-write-result.md` records profile `spec-dock-iss-00126-implementation-planner-plan-cli-98a21ff9ddee`, `default_permissions` match, `permission_profile_hash=05529d47e9aa802b46dfb5eb3bb4fe1f12a3a1a661f5f0876b5ced3a93134b59`, and all required negative categories denied with `Operation not permitted`。
    - denied categories: `requirement.md`, peer artifact, `report.md`, `src/`, `tests/`, `.codex/`, `.agents/`, `.env*`。
    - orchestrator post-check confirmed no `98a21ff9ddee` negative sentinel path exists。
- diff gate:
  - delegated sessions could not run `git diff/status` because the restricted profile could not read the external worktree gitdir; this is not counted as delegated diff evidence.
  - main orchestrator owns final diff validation for the S07 adoption gate.
  - `git diff --check`: pass。
  - after fail-closed bottom metadata parsing was implemented, `./spec-dock/scripts/spec-dock validate` now correctly fails while `design.md` / `plan.md` remain `authority=proposed`。
  - current failure reason: `Delegated draft authority incomplete/blocked ... reason=authority_not_approved`。
  - S07 closure intentionally stops at `authority=proposed`; final `authority=approved` metadata is a main-orchestrator promotion step after fresh review.

## レビュー履歴

- Mendel: fail。CLI helper invocation surface、dogfooding pilot approval order、EAL fields を指摘。
- Meitner: fail。`--input-authority-file` と reviewer evidence path の固定不足を指摘。
- McClintock: fail。reviewer evidence path と step-local plan 契約不足を指摘。
- Sartre: fail。EAL `blocked` / `stale` gate と Desktop fallback concrete test 不足を指摘。
- Gibbs: fail。actual delegated write session invocation evidence と resolvable EAL evidence path 不足を指摘。
- Mencius: fail。runtime command registry scope と S06 closure mapping 不足を指摘。
- Banach: pass。findings none。prior Mencius/Gibbs/Sartre closure points resolved。
- Huygens: fail。proposed draft grants に `design_baseline` が残っていたこと、S07 probe / invocation evidence 不足、G10 findings disposition rule の弱さを指摘。
- Raman: pass。Huygens findings の修正後、proposed draft grants、S07 incomplete evidence handling、G10 disposition rule が Epic v1 と整合すると確認。
- Heisenberg: fail。proposed `plan.md` metadata に `implementation_start` grant が残り、authority separation と AC-009 に反すると指摘。
- Heisenberg finding response: `plan.md` と delegated write result の proposed grants を `review_input,planning_input` に修正。後続の authority-boundary review で downstream grant separation を再確認。
- Nash: fail。bottom metadata が runtime に読まれない、localized EAL headers が fail-closed にならない、unstructured authority evidence が substring fallback で通る、の P1 を指摘。
- Nash finding response: dev-coder Laplace が bottom metadata parser、localized EAL header normalization、structured JSON/TOML evidence requirement、regression tests を実装。targeted `Ran 105 tests OK`。
- Noether: fail。purpose-specific artifact grants、`spec-dock validate` の EAL fail-closed、context-pack authoritative input 表示の3つの P1 authority-boundary gaps を指摘。
- Noether finding response: dev-coder Planck が provider/dogfooding runtime と focused tests を修正。artifact metadata validation は `implementation_start` / `issue_ready` / `issue_finish` / `phase_completion` の purpose-specific grant を要求し、validate は scope-local report EAL `blocked` / `stale` を fail-closed にし、context-pack は proposed artifact または unresolved EAL がある場合に `authoritative_input=none` と downstream block reason を表示する。
- Mill: fail。EAL `adoption_status` が Markdown code span の `` `blocked` `` / `` `stale` `` 形式だと fail-closed gate を迂回できると指摘。
- Mill finding response: provider/dogfooding `domain/authority.py` で EAL status/target/id/next_action の Markdown code span を正規化し、domain と CLI validate の回帰テストを追加。
- Fermat: pass。Noether / Mill の P1 authority-boundary repairs は解消済み、EAL code-span normalization と purpose-specific grants / validate / context-pack fail-closed behavior に追加 findings なし。
- Kant: fail。S07 metadata-only write は substantive delegated draft evidence にならない、full suite failure を残せない、と指摘。
- Kant finding response: S07 substantive delegated write は parent sandbox nesting failure を切り分け、issue-cwd profile + escalated outer executionで design/plan 本文差分を取得済み。pre-promotion full-suite failure 2 件は main promotion 後に解消し、post-P1 full suite も pass。fresh QA re-review Poincare は pass。
- Lagrange: fail。runtime metadata mismatch、proposed downstream grant、role skill `grants` contract、G10 shared diff、full verification を指摘。
- Lagrange finding response: runtime metadata mismatch、proposed grant、role skill grants contract、S07 substantive write、G10 shared diff artifact は修正済み。post-promotion `validate` と full suite も pass。fresh G10 deep-consultant re-review は後続の Aristotle approve で解消。
- Erdos: fail。Epic plan が `iss-00126` を G10 / PR 更新前 gate に含めておらず、S07 Green verification が pre-promotion fail-closed validate と post-promotion pass validate を分離していないと指摘。
- Erdos finding response: Epic plan の G10 / epic-wide pre-PR / v1 amendment table に corrective `iss-00126` / `#126` を追加。issue plan S07 Green verification を pre-promotion `authority_not_approved` expected fail と post-promotion validate pass に分離。fresh re-review は Linnaeus pass で解消。
- Linnaeus: pass。Erdos P1 findings は解消。P2 として v1 dependency graph に corrective `iss-00126` ノードがないと指摘。
- Linnaeus P2 response: Epic plan の v1 Amendment dependency graph に corrective Issue `iss-00126` / `#126` node と `I12 --> I13` dependency を追加。
- Aquinas: approve。correction architecture は Epic 本来の目的に戻っており、write-capable draft author + proposed authority + main promotion の分離は妥当と判断。PR update は final main promotion、fresh spec-reviewer、`spec-dock validate` pass、full suite pass、G10 artifact refresh/re-review まで block 継続と指摘。
- Aquinas finding response: PR update block は維持。S07 evidence は promotion 前レビュー入力として採用し、Desktop 等価性は主張せず CLI-first supported path として記録。G10 artifact は final promotion/verification 後に更新する。
- Curie: fail。P1 として promoted artifact が `authority=approved` / lifecycle grants を持ちながら `status=draft` のままになっており、runtime も status/authority compatibility を検証していないと指摘。P2 として Epic design Flow-A/B が delegated author に canonical Evidence Adoption Ledger を更新させるように読めると指摘。
- Curie finding response: active issue `design.md` / `plan.md` の promoted metadata を `status=approved` に修正。Epic design Flow-A/B は delegated author が candidate ledger / handoff evidence のみを更新し、main orchestrator が scope-local `report.md` canonical EAL disposition を記録する表現へ修正。dev-coder Halley が runtime で `authority=approved` + `status!=approved` を `status_not_approved` として fail-closed にし、domain / CLI validate regression tests を追加。
- Ampere: fail。P1 として promotion record の `reviewer_evidence_path` と `input_authority.*.reviewer_evidence_path` の結合が検証されず、別チェーンの promotion/reviewer evidence を混ぜた manifest/profile/probe 生成を防げないと指摘。
- Ampere finding response: dev-coder Halley が provider/dogfooding `domain/delegated_authoring.py` に reviewer evidence path binding check を追加し、不一致時は `promotion_reviewer_evidence_path_mismatch=<source>` で artifacts 生成前に拒否。negative regression test を追加。
- Poincare: pass。Curie/Ampere P1 repairs 後、approved-authority/draft-status metadata と promotion reviewer evidence path mismatch が fail-closed になり、direct regression coverage と targeted/full-suite evidence が揃っていることを確認。QA findings none。
- Gauss: fail。P1 として古い full-suite failure evidence が final pass の後に未解決のまま残っており、canonical report の Green status が曖昧になると指摘。
- Gauss finding response: 古い `Ran 862` failure は Historical stale environment failure として明示し、`.venv` pip 修復後の representative packaging pass、pre-promotion `Ran 886` failure、post-promotion `Ran 890` pass、post-P1 `Ran 892` pass の順に解消関係を整理。
- Schrodinger: fail。P1 として G10 shared diff artifact が `baseRefOid...HEAD` 固定の `git diff --stat` / `git diff --name-status` 証跡ではなく、可変 `main` 中心の要約に見えると指摘。P2 として Epic design Flow-A/B の canonical EAL 記録順が delegated draft production より前に読めると指摘。
- Schrodinger finding response: G10 shared diff artifact に immutable PR base OID `421fd4c02fd2649b8c29ec9549a961b7824b9149...HEAD` の exact command、stat terminal summary、full name-status companion artifact path / entry count、working-tree tracked diff summary、untracked supplement を明記。Epic design Flow-A/B は delegated author が candidate ledger / handoff evidence を更新し、draft artifact を書いた後に main orchestrator が scope-local `report.md` canonical EAL disposition を記録する順序へ修正。
- Aristotle: approve。G10 gate、depth=2 leaf-only constraints、main promotion ownership、authority fail-closed repairs、post-P1 validate / targeted / full-suite pass は PR update 前提として妥当と判断。residual risk は depth policy が host config + skill/document contract + tests による enforcement である点だが、今回の PR 更新判断では許容範囲。
- Nietzsche: fail。P1 として G10 shared artifact の working-tree supplement が Epic report 追記後の最新作業ツリー数値とずれていると指摘。
- Nietzsche finding response: G10 shared artifact の refresh timestamp、`git diff --stat main` summary、post-HEAD `git diff --stat` summary を最新の read-only verification endpoint に更新。immutable committed diff evidence は既存の base-OID companion artifactのまま維持。
- Helmholtz / Rawls: fail。P1 として active issue report / G10 artifact に QA/deep gate が未了とも通過済みとも読める stale remaining-gate text が残っていると指摘。
- Helmholtz / Rawls finding response: active issue report と G10 artifact の remaining gate を「QA pass / deep approve 済み、PR update 前に fresh spec/code re-review が必要」へ一本化。
- Plato: pass。P0/P1 spec blockers なし。P2 として Epic v1 E-AC-003 / E-AC-004 が `pending correction closure` のままで、`iss-00126` の write-capable delegated draft authoring evidence と traceability がずれていると指摘。
- Plato P2 response: Epic report の E-AC-003 / E-AC-004 を pass に更新し、`iss-00126` の substantive delegated `design.md` / `plan.md` body delta、issue-cwd Permission Profile、boundary denial、main promotion、post-promotion verification を evidence として明記。
- Zeno: fail。P1 として approved delegated artifact metadata が `positive_probe_result` 欠落または non-pass でも `validate_draft_artifact_metadata(..., purpose="implementation_start")` を通過し、unproven delegated write session を downstream authoritative に扱えると指摘。
- Zeno finding response: dev-coder Copernicus が provider/dogfooding `domain/authority.py` に `positive_probe_result` 必須化と `positive_probe_result != "pass"` の `positive_probe_not_passed` fail-closed gate を追加。domain / CLI validate / issue lifecycle fixtures and regressions を更新し、main rerunで focused matrix pass、provider/dogfooding `authority.py` parity pass、`validate` pass、`git diff --check` pass を確認。
- Dalton: fail。P1 として Zeno repair は runtime/report/G10 へ反映されたが、canonical acceptance/design contract の AC-006 と D-004 metadata required fields が `positive_probe_result` を必須化しておらず、正本が実装より弱いままだと指摘。
- Dalton finding response: active issue `requirement.md` AC-006 と `design.md` D-001/D-004 metadata contract に `positive_probe_result` を必須 field として追加し、`pass` だけを downstream authority として受け付け、欠落は `incomplete_draft_metadata`、pass 以外は `positive_probe_not_passed` とする契約へ整合。
- Boole: pass。P0/P1 code/evidence blockers なし。P2 として D-016 follow-up が final promotion pending と読める古い表現のままだと指摘。
- Boole P2 response: D-016 follow-up を「final promotion completed; fresh spec/code G10 re-review remains before PR update」へ更新。
- Chandrasekhar: pass。fresh code-reviewer。P0/P1/P2 implementation/evidence blockers なし。残リスクとして depth=2 delegation は host config / skill contract / tests による enforcement であり、deeper runtime child-agent graph monitor ではないが、今回の PR update gate では許容。
- Carson: pass。fresh spec-reviewer。P0/P1 blockers なし。P2 として G10 working-tree exact file scope と `acceptance_counted=false` の pre-promotion 意味づけの明確化を指摘。
- Carson P2 response: G10 shared diff evidence に exact `git diff --name-status` と exact untracked file list を追記し、`acceptance_counted=false` は delegated-author-local / pre-promotion marker であり、main orchestrator adoption + approved metadata + promotion evidence + probe/diff gate 後にだけ final acceptance として counted されることを明記。
- James: pass。fresh spec-reviewer re-review。Carson P2-1 / P2-2 は解消、P0/P1/P2 spec blockers なし。Chandrasekhar code-review pass と合わせて PR update 可能と判断。

## 検証結果

- `git diff --check`: pass。
- `./spec-dock/scripts/spec-dock validate`: pass (`nodes=64`)。
- Huygens finding 修正後 `git diff --check`: pass。
- Huygens finding 修正後 `./spec-dock/scripts/spec-dock validate`: pass (`nodes=64`)。
- Fresh spec-reviewer Raman: pass (`findings=[]`, residual risk: S07/S90/S99/G10 are honestly unfinished rather than accepted completion)。
- `uv run python -m unittest tests.domain_runtime.test_delegated_authoring tests.cli_runtime.test_delegated_authoring tests.domain_runtime.test_authority tests.cli_runtime.test_issue_lifecycle`: pass (`Ran 44 tests`)。
- Negative sentinel contract fix:
  - `uv run python -m unittest tests.domain_runtime.test_delegated_authoring tests.cli_runtime.test_delegated_authoring`: pass (`Ran 8 tests`)。
- D-012 S02/S05 combined targeted matrix:
  - `uv run python -m unittest tests.domain_runtime.test_delegated_authoring tests.cli_runtime.test_delegated_authoring tests.domain_runtime.test_authority tests.cli_runtime.test_validate tests.cli_runtime.test_runtime_active_s05 tests.cli_runtime.test_issue_lifecycle -v`: pass (`Ran 113 tests`)。
- D-012 S07 regenerated evidence gate:
  - actual write sessions used generated `default_permissions` profiles under `sandbox: custom permissions`。
  - design / plan proposed metadata blocks reference current generated manifest hashes, permission profile hashes, session invocation hashes, positive probe IDs, and `stale_check=fresh`。
  - negative probes denied all required boundary categories and left no sentinels。
  - post-S07 `git diff --check`: pass。
  - post-S07 validation after runtime metadata parser fix: expected fail while delegated artifacts remain proposed (`reason=authority_not_approved`)。
- D-015/D-016 authority and fail-closed repair:
  - `uv run python -m unittest tests.domain_runtime.test_authority tests.test_init_update.TestInitUpdate.test_bundled_skill_routing_contract tests.test_init_update.TestInitUpdate.test_issue_117_codex_delegated_author_adapters_are_thin_skill_wrappers -v`: pass (`Ran 24 tests`)。
  - dev-coder Laplace targeted matrix: `uv run python -m unittest tests.domain_runtime.test_authority tests.cli_runtime.test_validate tests.cli_runtime.test_issue_lifecycle tests.domain_runtime.test_delegated_authoring tests.cli_runtime.test_delegated_authoring -v`: pass (`Ran 105 tests`)。
  - dev-coder Laplace QA targeted closure: `uv run python -m unittest tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_initiatives_do_not_ship_legacy_deps_json tests.test_init_update.TestInitUpdate.test_init_creates_expected_structure -v`: pass (`Ran 2 tests`)。
  - main combined targeted rerun after Laplace/Arendt fixes: `uv run python -m unittest tests.domain_runtime.test_authority tests.cli_runtime.test_validate tests.cli_runtime.test_issue_lifecycle tests.domain_runtime.test_delegated_authoring tests.cli_runtime.test_delegated_authoring tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_initiatives_do_not_ship_legacy_deps_json tests.test_init_update.TestInitUpdate.test_init_creates_expected_structure tests.test_init_update.TestInitUpdate.test_bundled_skill_routing_contract tests.test_init_update.TestInitUpdate.test_issue_117_codex_delegated_author_adapters_are_thin_skill_wrappers -v`: pass (`Ran 111 tests`)。
  - `git diff --check`: pass。
- S07 substantive write repair:
  - failed nested sandbox attempts retained as non-acceptance evidence: `019e5838-7429-71f3-8a64-1db94879bc17`, `019e5838-9547-7122-a740-389effdd9ed5`, `019e583a-8e24-7cb3-8792-aef2b303ee8f`, `019e583a-bf2a-7de3-8444-3ee706d91bc9`。
  - successful system-architect issue-cwd session: `019e583f-3894-7893-b083-9d22024b6067`; changed `design.md` body and task-local `delegated-write-result.md` only。
  - successful implementation-planner issue-cwd session: `019e583f-7723-7570-8633-31d1b3b78b24`; changed `plan.md` body and task-local `delegated-write-result.md` only。
  - final issue-local authority is now promoted by the main orchestrator to `authority=approved`; pre-promotion `authority=proposed` evidence remains retained only as S07 proof that delegated authors did not self-approve downstream authority。
- Noether P1 authority-boundary repair:
  - Red evidence before fix:
    - `test_artifact_metadata_uses_purpose_specific_lifecycle_grant`: failed because `validate_draft_artifact_metadata()` lacked a `purpose` argument。
    - `test_validate_blocks_scope_local_evidence_adoption_ledger_entries`: failed because validate returned ok despite blocked/stale EAL。
    - `test_context_pack_blocks_authoritative_input_when_scope_report_has_unresolved_eal`: failed because context-pack rendering did not accept repository/root authority context。
  - Green evidence after fix:
    - `uv run python -m unittest tests.domain_runtime.test_authority tests.cli_runtime.test_runtime_active_s05 tests.cli_runtime.test_issue_lifecycle tests.cli_runtime.test_validate -v`: pass (`Ran 103 tests`)。
    - `git diff --check`: pass。
  - provider/dogfooding parity: Planck reported touched runtime mirror pairs are byte-identical by `diff -q`。
- Mill P1 EAL code-span normalization repair:
  - added domain regression: `test_evidence_ledger_gate_normalizes_markdown_code_span_statuses`。
  - extended CLI validate regression with `` `blocked` `` / `` `EAL-023` `` table values。
  - `uv run python -m unittest tests.domain_runtime.test_authority tests.cli_runtime.test_validate tests.cli_runtime.test_runtime_active_s05 tests.cli_runtime.test_issue_lifecycle -v`: pass (`Ran 104 tests`)。
  - `git diff --check`: pass。
- Main orchestrator promotion after fresh review and fail-closed repair:
  - promoted active issue `design.md` metadata:
    - `authority=approved`
    - `approval=fresh-reviewer-pass-main-promotion`
    - `approved_hash=3703cddbe1b119572b82b2c0a921db21dd4029732c00b0cc9a4d28e03e21576d`
    - `grants=review_input,planning_input,implementation_start,issue_ready,issue_finish,phase_completion`
  - promoted active issue `plan.md` metadata:
    - `authority=approved`
    - `approval=fresh-reviewer-pass-main-promotion`
    - `approved_hash=0e07b86b77deebafa1e073d6f4270979be1ec5ec114095b8cfa821f78d159393`
    - `grants=review_input,planning_input,implementation_start,issue_ready,issue_finish,phase_completion`
  - `./spec-dock/scripts/spec-dock validate`: pass (`spec-dock: ok (validate) nodes=64`)。
  - `git diff --check`: pass。
  - `uv run python -m unittest discover -v`: pass before Curie/Ampere P1 repairs (`Ran 890 tests in 431.312s OK`)。
- Curie/Ampere P1 repairs:
  - Red evidence before fix:
    - `test_approved_authority_requires_approved_status`: failed because `authority=approved` + `status=draft` was accepted.
    - `test_promotion_reviewer_evidence_path_mismatch_blocks_without_artifacts`: failed because mixed promotion/reviewer evidence paths were accepted.
  - accepted decision:
    - Adopt normalized path comparison with `Path(...).expanduser().resolve(strict=False).as_posix()` for promotion record reviewer evidence path binding. This preserves fail-closed mismatch behavior while avoiding false mismatches for equivalent absolute/relative path spellings in the same filesystem view.
  - Green evidence:
    - `uv run python -m unittest tests.domain_runtime.test_authority tests.domain_runtime.test_delegated_authoring tests.cli_runtime.test_delegated_authoring tests.cli_runtime.test_validate tests.cli_runtime.test_runtime_active_s05 tests.cli_runtime.test_issue_lifecycle -v`: pass (`Ran 125 tests in 115.036s OK`)。
    - `./spec-dock/scripts/spec-dock validate`: pass (`spec-dock: ok (validate) nodes=64`)。
    - `git diff --check`: pass。
    - provider/dogfooding runtime mirror parity for `domain/authority.py` and `domain/delegated_authoring.py`: pass (`diff -u` output empty)。
  - post-P1 full suite:
    - `uv run python -m unittest discover -v`: pass (`Ran 892 tests in 436.168s OK`)。
- Zeno P1 positive-probe authority repair:
  - Red evidence before fix:
    - missing `positive_probe_result`, `fail`, `failed`, and empty string were accepted by `validate_draft_artifact_metadata()` for approved delegated artifacts.
  - Green evidence after fix:
    - `uv run python -m unittest tests.domain_runtime.test_authority -v`: pass (`Ran 28 tests ... OK`)。
    - `uv run python -m unittest tests.domain_runtime.test_authority tests.cli_runtime.test_validate tests.cli_runtime.test_issue_lifecycle -v`: pass (`Ran 95 tests in 109.130s OK`)。
    - provider/dogfooding runtime mirror parity for `domain/authority.py`: pass (`diff -u` output empty)。
    - `./spec-dock/scripts/spec-dock validate`: pass (`spec-dock: ok (validate) nodes=64`)。
    - `git diff --check`: pass。
- QA final verification gate:
  - `uv run python -m unittest discover -v`: fail (`Ran 886 tests`, `failures=2`) while `design.md` / `plan.md` remain `authority=proposed`。
  - failures:
    - `test_checked_in_dogfooding_runtime_subprocess_validate_and_sync_on_cutover_snapshot`
    - `test_checked_in_dogfooding_runtime_subprocess_deps_mutation_on_cutover_snapshot`
  - observed reason: checked-in dogfooding cutover snapshot now correctly fails validation with `authority_not_approved` for `iss-00126` delegated draft artifacts until main promotion metadata is recorded。
  - disposition: expected pre-promotion blocker; resolved by main promotion and post-promotion / post-P1 full-suite pass. Fresh QA re-review Poincare passed with findings none。
- G10 shared diff artifact:
  - path: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/discussions/20260524t043441z-disc-g10-shared-diff-evidence.md`
  - base: immutable PR base OID `421fd4c02fd2649b8c29ec9549a961b7824b9149`; `main` is a local convenience alias only (`develop` is not a valid local ref; `origin/HEAD -> origin/main`)
  - merge-base: `421fd4c02fd2649b8c29ec9549a961b7824b9149`
  - current HEAD: `4365d38f5d88ac4ace362837ce55fdf8e2d6e404`
  - committed diff exact stat: `git diff --stat 421fd4c02fd2649b8c29ec9549a961b7824b9149...HEAD` -> `270 files changed, 23075 insertions(+), 898 deletions(-)`
  - committed diff exact full name-status: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/discussions/20260523t204806z-disc-g10-full-name-status.md` (`270` entries, command fixed to base OID)
  - scope: working tree included through `git diff --stat main`, `git diff --stat`, `git diff --name-status`, and untracked list, including corrective issue, runtime modules, and tests.
- Final corrective G10 reviewer gate:
  - Fresh `code-reviewer` Chandrasekhar: pass (`findings=[]`)。
  - Fresh `spec-reviewer` Carson: pass with P2 auditability findings。
  - Carson P2 dispositions: fixed by adding exact working-tree tracked/untracked scope to the G10 artifact and clarifying `acceptance_counted=false` as a pre-promotion delegated-author-local marker。
  - Fresh `spec-reviewer` James re-review: pass (`findings=[]`)。
  - Final post-report verification:
    - `uv run python -m unittest discover -v`: pass (`Ran 895 tests in 432.904s OK`)。
    - `./spec-dock/scripts/spec-dock validate`: pass (`spec-dock: ok (validate) nodes=64`)。
    - `git diff --check`: pass。
  - Gate result: PR #119 update is unblocked from the issue-local S90/S99/G10 perspective.
- Local verification environment:
  - `.venv/bin/python3 -m pip --version`: pass after `uv pip install pip` (`pip 26.1.1`)。
  - representative issue-69 / isolated wheel packaging tests: pass (`Ran 4 tests`)。
- Targeted managed asset tests:
  - `tests.test_init_update.TestInitUpdate.test_issue_102_agentic_tdd_contract_assets`
  - `tests.test_init_update.TestInitUpdate.test_issue_116_delegated_authoring_phase_gate_contract_assets`
  - `tests.test_init_update.TestInitUpdate.test_issue_117_codex_delegated_author_adapters_are_thin_skill_wrappers`
  - `tests.test_init_update.TestInitUpdate.test_bundled_skill_routing_contract`
  - result: pass (`Ran 4 tests`)。
- Historical stale environment failure:
  - `uv run python -m unittest discover -v`: fail (`Ran 862 tests`, `failures=12`)。
  - Primary observed failure family: issue-69 / isolated wheel packaging tests could not run because current `.venv/bin/python3` reported `No module named pip` when installing from `tests/fixtures/wheelhouse`。
  - disposition: resolved. `.venv/bin/python3 -m pip --version` passed after `uv pip install pip`, representative issue-69 / isolated wheel packaging tests passed (`Ran 4 tests`), and later full suites passed (`Ran 890 tests` before Curie/Ampere P1 repairs; `Ran 892 tests` after Curie/Ampere P1 repairs; `Ran 895 tests in 432.904s OK` after final G10 report refresh)。
