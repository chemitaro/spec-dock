---
種別: 実装計画書（Issue）
ID: "iss-00126"
タイトル: "Write Capable Delegated Draft Authoring Correction"
関連GitHub: ["#126"]
状態: "approved"
作成者: "Codex"
最終更新: "2026-05-24"
依存: ["requirement.md", "design.md"]
親: ["epic-00112", "init-local-00003"]
---

# iss-00126 Write Capable Delegated Draft Authoring Correction — 実装計画

## この計画で満たす要件ID

- AC-001..AC-010
- EC-001..EC-004

## 実装順序

1. S01: Issue spec gate and Epic addendum。
2. S02: delegated authoring manifest / permission helper。
3. S03: workflow docs / templates / issue-plan authoring contract。
4. S04: adapter / config / role skill alignment。
5. S05: runtime authority gate。
6. S06: managed asset and runtime tests。
7. S07: dogfooding actual write pilot。
8. S90: docs impact / provider-dogfooding parity。
9. S99: final issue quality gates。
10. G10: Epic-wide pre-PR gate。

## 仕様固定クロージャ索引

| ID | Step | 種別 | 固定する期待値 | 必須 | 証跡レベル | 証跡 |
|---|---|---|---|---|---|---|
| tc-001 | S02 | acceptance | manifest includes target, input_authority, allowed/forbidden paths, probes, diff gate, fallback | yes | red-required | domain test |
| tc-002 | S02 | negative | missing/stale/mismatched upstream authority blocks profile/probe generation | yes | red-required | domain test |
| tc-003 | S02 | negative | negative probe uses disposable sentinel and cleanup/dirty diff abort, not real artifact mutation | yes | red-required | domain test |
| tc-004 | S02/S07 | acceptance | generated `session-invocation.toml` binds actual write session to profile identity/hash, config overrides, default_permissions, and positive probe ID | yes | red-required | domain/cli test + report evidence |
| tc-005 | S03 | acceptance | workflow/report/issue-plan docs expose consent, manifest, invocation, probe, diff, ledger evidence | yes | inspect-only | managed asset tests |
| tc-006 | S04 | acceptance | adapters are not proposal-only fixed and do not mix old sandbox settings | yes | inspect-only | TOML/content tests |
| tc-007 | S04 | acceptance | `agents.max_depth = 2` with child constraints | yes | inspect-only | config/skill tests |
| tc-008 | S05 | acceptance | proposed artifacts cannot satisfy implementation/finish authority gates | yes | red-required | runtime tests |
| tc-009 | S05 | acceptance | draft artifact metadata fields are required and missing fields block/incomplete | yes | red-required | domain/runtime tests |
| tc-010 | S05 | negative | unresolved `blocked` / `stale` Evidence Adoption Ledger entries block promotion, implementation start, ready, finish, and phase completion | yes | red-required | domain/runtime tests |
| tc-011 | S07 | negative | Desktop host surface is fallback/proposal-only and `acceptance_counted=false` unless verified by CLI-equivalent probes | yes | manual-required | report evidence / inspect test |
| tc-012 | S07 | manual-required | dogfooding actual `design.md` and `plan.md` draft write with full metadata and no forbidden diff | yes | manual-required | report evidence |
| tc-013 | S99/G10 | acceptance | fresh reviewers and Epic-wide gate pass before PR update | yes | manual-required | report evidence |

## 実装ステップ

### S01 — Issue spec gate and Epic addendum

- 目標:
  - Corrective issue の requirement/design/plan/report を v2 計画に合わせる。
  - Epic plan/report に corrective issue と G10 gate を記録する。
- 対象:
  - this issue docs。
  - `epic-00112/plan.md`, `epic-00112/report.md`。
- 検証:
  - `./spec-dock/scripts/spec-dock validate`
  - fresh spec-reviewer pass。
- 委任:
  - spec-reviewer。

### S02 — delegated authoring manifest / permission helper

- 目標:
  - task manifest / Permission Profile helper を runtime に追加する。
  - main orchestrator が実行時に呼び出せる CLI surface を追加する。
- 対象:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/delegated_authoring.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/delegated_authoring.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/delegated_authoring.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/parser.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/registry.py`
  - tests under `tests/domain_runtime/`
  - command tests under `tests/cli_runtime/`
- 契約:
  - `input_authority` missing/stale/mismatch blocks profile/probe generation。
  - generated profile never uses `sandbox_mode` / `[sandbox_workspace_write]`。
  - negative probe is non-destructive sentinel only。
  - command surface:
    - `spec-dock delegated-authoring manifest --role <system-architect|implementation-planner> --scope <node-id> --target <design|plan> --host-surface <cli|desktop> --input-authority-file <path>`
    - `--input-authority-file` is required. It points to an orchestrator-authored TOML or JSON evidence file containing `source_revisions` and `input_authority`.
    - The command may resolve canonical target paths from `--scope` and `--target`, but it must not infer upstream approval from raw artifact content alone.
    - The command must verify `input_authority` against the referenced promotion / reviewer evidence paths before generating any profile or probe plan.
    - output: manifest path, generated Permission Profile fragment path, positive probe plan, non-destructive negative probe plan, diff gate plan, and blocked reason if generation is refused.
    - output also includes `session-invocation.toml`, which records the only supported write-session invocation contract for the delegated author session.
  - output location:
    - issue-local `discussions/delegated-authoring/<task-id>/manifest.toml`
    - issue-local `discussions/delegated-authoring/<task-id>/permission-profile.toml`
    - issue-local `discussions/delegated-authoring/<task-id>/probe-plan.md`
    - issue-local `discussions/delegated-authoring/<task-id>/session-invocation.toml`
  - input authority file minimum fields:
    - `source_revisions.requirement`
    - `source_revisions.design` when role is `implementation-planner`
    - `input_authority.requirement.promotion_record_path`
    - `input_authority.requirement.reviewer_evidence_path`
    - `input_authority.requirement.approved_revision`
    - `input_authority.requirement.approved_content_hash`
    - `input_authority.requirement.reviewer_verdict`
    - `input_authority.requirement.reviewer_target_hash`
    - `input_authority.requirement.required_grants`
    - `input_authority.requirement.stale_check`
    - `stale_check` must be the literal value `fresh`. It means referenced promotion record and reviewer evidence still match the current approved revision/hash. `pass`, `stale`, missing, or unknown values block generation.
    - corresponding `input_authority.design.*` fields, including `reviewer_evidence_path`, when role is `implementation-planner`
    - helper must verify both `promotion_record_path` and `reviewer_evidence_path`; reviewer verdict/hash fields are observations to verify, not trusted self-attestation.
  - invocation evidence:
    - helper command, input authority file path/hash, stdout/stderr summary, generated paths, `session-invocation.toml` path/hash, blocked/pass status, and cleanup/diff gate evidence are recorded in `report.md`.
    - actual delegated write session must record the supported invocation command or host-equivalent execution record, config overrides, selected `default_permissions`, permission profile name/hash, manifest hash, positive probe ID/result, draft artifact metadata, and diff gate result.
- 検証:
  - `uv run python -m unittest tests.domain_runtime.test_delegated_authoring`
  - `uv run python -m unittest tests.cli_runtime.test_delegated_authoring`

### S03 — workflow docs / templates / issue-plan authoring contract

- 目標:
  - write-scoped delegated draft authoring の docs contract を provider-first で更新する。
- 対象:
  - `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
  - phase docs。
  - `src/spec_dock/assets/spec_dock/docs/authoring/issue-plan.md`
  - report templates / active-none reports。
- 契約:
  - read-only specialist consent と write-scoped delegated authoring consent を分離する。
  - report evidence destination を明示する。
  - issue-plan authoring contract に manifest/probe/diff/authority fields を入れる。
- 検証:
  - managed asset assertions in `tests/test_init_update.py`。

### S04 — adapter / config / role skill alignment

- 目標:
  - `system-architect` / `implementation-planner` を success-pathあり fail-closed にする。
  - depth=2 を安全制約付きで有効化する。
- 対象:
  - provider `.codex/agents/*.toml`
  - dogfooding `.codex/agents/*.toml`
  - provider / dogfooding `.codex/config.toml`
  - provider / dogfooding role skills。
- 契約:
  - proposal-only 固定文言を削除。
  - verified manifest/profile/probe 成功時だけ exact target write。
  - child allowlist / max child calls / no-grandchild / no peer-author / no dev-coder child。
- 検証:
  - TOML parse。
  - `tests/test_init_update.py` targeted tests。

### S05 — runtime authority gate

- 目標:
  - artifact-level metadata validator と executable lifecycle/context gate を追加する。
- 対象:
  - `domain/authority.py`
  - `spec-dock validate` surface。
  - active context-pack rendering / context-pack inclusion surface。
  - issue finish surface。
  - runtime tests。
- 契約:
  - full E-AC-001 metadata fields required。
  - `authority: proposed` cannot authorize implementation / ready / finish / phase completion。
  - validate、context-pack、issue finish は、proposed / stale / missing-metadata artifact が downstream authority になり得る場合に fail closed または incomplete を返す。
- 検証:
  - `tests/domain_runtime/test_authority.py`
  - validate tests。
  - context-pack / active rendering tests。
  - `tests/cli_runtime/test_issue_lifecycle.py`

### S06 — managed asset and runtime tests

- 目標:
  - S02..S05 の regression tests を固定する。
- 対象:
  - `tests/test_init_update.py`
  - `tests/domain_runtime/*`
  - `tests/cli_runtime/*`
- 検証:
  - targeted unittest。

### S07 — dogfooding actual write pilot

- 目標:
  - actual `design.md` / `plan.md` draft write を実証する。
- 対象:
  - corrective issue の dogfooding artifact。
  - candidate evidence / report ledger。
- 契約:
  - full metadata。
  - forbidden path diffなし。
  - proposed downstream gate block。
  - pilot sequence:
    1. Use an approved requirement revision as `system-architect` input and generate a design manifest/profile through the S02 command surface.
    2. `system-architect` writes actual target `design.md` as `status: draft` / `authority: proposed` with full E-AC-001 metadata.
    3. main orchestrator integrates the design draft, records Evidence Adoption Ledger disposition, obtains fresh `spec-reviewer` pass, and records promotion evidence for design.
    4. Use the approved requirement revision and newly approved design revision as `implementation-planner` input and generate a plan manifest/profile through the S02 command surface.
    5. `implementation-planner` writes actual target `plan.md` as `status: draft` / `authority: proposed` with full E-AC-001 metadata.
    6. Verify proposed plan remains non-authoritative for implementation / finish until main promotion and fresh reviewer pass.
  - The plan pilot must not rely on a proposed design as upstream authority. If design promotion cannot be completed, plan pilot is blocked rather than counted as AC-009 pass.
- 検証:
  - `git diff --check`
  - `./spec-dock/scripts/spec-dock validate`
  - targeted tests。
  - spec-reviewer。

### S90 — docs impact and parity

- 目標:
  - provider / dogfooding parity を確認する。
- 検証:
  - `./spec-dock/scripts/spec-dock validate`
  - `./spec-dock/scripts/spec-dock sync` if needed。
  - targeted docs/tests inspection。

### S99 — final issue quality gate

- 目標:
  - issue-wide diff を fresh reviewers で確認する。
- 検証:
  - code-reviewer。
  - qa-reviewer。
  - spec-reviewer。
  - all pointed findings fixed and re-reviewed。

### G10 — Epic-wide pre-PR gate

- 目標:
  - development branch と completed state の diff 全体を deep-consultant / spec-reviewer で確認する。
- 検証:
  - 指摘事項なし、または修正後 pass。

## レビュー / QA ゲート方針

- Specs:
  - requirement/design/plan/report は実装前に fresh spec-reviewer pass。
- Code/runtime:
  - dev-coder に実装委任。
  - code-reviewer pass。
- Docs/templates/skills:
  - doc-writer に文書実装委任。
  - spec-reviewer pass。
- Final:
  - qa-reviewer, spec-reviewer, deep-consultant gate。

## Step-local 実行契約

各 implementation step は以下の契約を満たさない限り実行完了にしない。詳細な observed result は `report.md` の該当 Sxx section に記録する。

### S02 step-local contract

- delegation contract:
  - delegated role: dev-coder
  - allowed paths: `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/delegated_authoring.py`, `application/delegated_authoring.py`, `commands/delegated_authoring.py`, `cli/parser.py`, `cli/registry.py`, `tests/domain_runtime/test_delegated_authoring.py`, `tests/cli_runtime/test_delegated_authoring.py`
  - forbidden changes: adapter TOML, workflow docs, unrelated runtime commands, completed issue reports
  - output required: changed files, command surface summary, generated artifact examples, test results, risks
- concrete tests:
  - `tc-s02-001`: valid input authority file produces manifest, profile fragment, probe plan, diff gate plan, and generated paths.
  - `tc-s02-002`: missing `reviewer_evidence_path` blocks generation.
  - `tc-s02-003`: stale / mismatched promotion record or reviewer hash blocks generation.
  - `tc-s02-004`: generated profile never contains `sandbox_mode` or `[sandbox_workspace_write]`.
  - `tc-s02-005`: negative probe plan contains boundary-specific disposable sentinels and cleanup/dirty diff abort for `requirement.md`, peer artifact, `report.md`, `src/`, `tests/`, `.codex/`, `.agents/`, and `.env*` categories without mutating real protected files.
  - `tc-s02-006`: generated `session-invocation.toml` includes executor, host surface, role, target artifact path, manifest hash, permission profile name/hash, `default_permissions`, config overrides, positive probe ID/target, negative probe plan path, diff gate plan path, `host_surface_acceptance_eligible`, and `acceptance_counted`.
  - `tc-s02-007`: CLI host surface sets `host_surface_acceptance_eligible=true` and `acceptance_counted=false` at manifest-generation time. Acceptance is counted only after actual delegated write, positive/negative probe, diff gate, and report-ledger adoption evidence are recorded.
  - `tc-s02-008`: `stale_check` accepts only `fresh`; `pass`, missing, stale, or unknown values block generation before profile/probe artifacts are written.
- Red / alternative evidence:
  - red-required tests above must fail before implementation or be justified as new tests against absent module/command.
- Green verification:
  - `uv run python -m unittest tests.domain_runtime.test_delegated_authoring`
  - `uv run python -m unittest tests.cli_runtime.test_delegated_authoring`
- Refactor guardrail:
  - do not refactor unrelated CLI registry or active/issue lifecycle code.
- report evidence destination:
  - `report.md` S02 session log, Step Contract Closure, Test Contract Closure, Closure Coverage.
- amendment trigger:
  - if CLI command cannot accept `--input-authority-file`, stop and amend plan before using another interface.

### S03 step-local contract

- delegation contract:
  - delegated role: doc-writer
  - allowed paths: provider/dogfooding workflow docs, phase docs, `docs/authoring/issue-plan.md`, report templates, active-none report scaffolds, managed asset tests that assert docs content
  - forbidden changes: runtime behavior, adapter TOML, completed issue reports
  - output required: changed docs/templates/tests, inspection evidence, unresolved docs risks
- concrete tests:
  - `tc-s03-001`: docs separate read-only specialist consent from write-scoped delegated authoring consent.
  - `tc-s03-002`: report templates include task manifest, input authority, probe, diff gate, fallback, and Evidence Adoption Ledger fields.
  - `tc-s03-003`: `docs/authoring/issue-plan.md` documents manifest/probe/diff/authority field requirements and report evidence destination.
- Red / alternative evidence:
  - inspect-only managed asset assertions in `tests/test_init_update.py`.
- Green verification:
  - targeted `uv run python -m unittest tests.test_init_update...` for affected managed asset assertions.
- Refactor guardrail:
  - avoid broad template rewrites unrelated to delegated authoring.
- report evidence destination:
  - `report.md` S03 session log and closure tables.
- amendment trigger:
  - if docs require new workflow policy beyond v2 scope, amend plan and re-review.

### S04 step-local contract

- delegation contract:
  - delegated role: doc-writer for adapter/skill/config text; dev-coder only for tests if needed
  - allowed paths: provider/dogfooding `.codex/config.toml`, `.codex/agents/system-architect.toml`, `.codex/agents/implementation-planner.toml`, role skills, `tests/test_init_update.py`
  - forbidden changes: source runtime behavior except tests, unrelated agents, secret files
  - output required: changed files, TOML parse result, managed asset assertion result
- concrete tests:
  - `tc-s04-001`: adapters remove read-only/proposal-only fixed language and describe success-path fail-closed authoring.
  - `tc-s04-002`: adapters do not use old sandbox settings with Permission Profiles.
  - `tc-s04-003`: config has `agents.max_depth = 2`.
  - `tc-s04-004`: skills define child allowlist, max child calls, leaf-only, no-grandchild, no peer author, no dev-coder child.
- Red / alternative evidence:
  - content assertions in `tests/test_init_update.py`.
- Green verification:
  - TOML parse command.
  - targeted `tests/test_init_update.py`.
- Refactor guardrail:
  - no unrelated agent model/policy changes.
- report evidence destination:
  - `report.md` S04 session log and closure tables.
- amendment trigger:
  - if Codex config schema rejects `max_depth = 2`, stop and amend.

### S05 step-local contract

- delegation contract:
  - delegated role: dev-coder
  - allowed paths: `domain/authority.py`, validate surface, context-pack/active rendering surface, issue-finish surface, runtime tests
  - forbidden changes: docs/templates/agent text except test fixture updates
  - output required: changed files, authority behavior summary, test results
- concrete tests:
  - `tc-s05-001`: proposed artifact cannot satisfy implementation / ready / finish / phase completion.
  - `tc-s05-002`: missing draft metadata field blocks/incomplete.
  - `tc-s05-003`: approved artifact requires exact grants and promotion record.
  - `tc-s05-004`: active synthetic approval is not treated as artifact approval.
  - `tc-s05-005`: unresolved Evidence Adoption Ledger entry with `adoption_status=blocked` or `adoption_status=stale` blocks draft promotion, implementation start, issue ready, issue finish, and phase completion, and returns the blocking ledger entry ID.
  - `tc-s05-006`: `spec-dock validate` reports proposed / stale / missing-metadata delegated draft artifacts as incomplete or blocked for downstream authority instead of silently passing them as implementation authority.
  - `tc-s05-007`: context-pack / active rendering for implementation or finish purpose excludes proposed artifacts from authoritative inputs and records the blocking reason when no approved artifact is available.
  - `tc-s05-008`: `issue finish` refuses to close / clear active state when downstream authority depends on proposed, stale, missing-metadata, or unresolved-ledger artifacts.
- Red / alternative evidence:
  - red-required runtime tests.
- Green verification:
  - `uv run python -m unittest tests.domain_runtime.test_authority`
  - `uv run python -m unittest tests.cli_runtime.test_validate`
  - targeted context-pack / active rendering tests。
  - targeted lifecycle/context tests.
- Refactor guardrail:
  - preserve existing active selection behavior unless explicitly covered by tests.
- report evidence destination:
  - `report.md` S05 session log and closure tables.
- amendment trigger:
  - if artifact metadata storage location changes, amend design/plan.

### S06 step-local contract

- delegation contract:
  - delegated role: dev-coder
  - allowed paths: tests only unless missing implementation is discovered and routed back to S02..S05
  - forbidden changes: broad fixture rewrites, weakening assertions to match flawed fallback behavior
  - output required: test list, coverage mapping to tc-001..tc-013, results
- concrete tests:
  - `tc-s06-001`: all planned closure IDs have a test or inspect-only evidence path.
  - `tc-s06-002`: tests fail against the old proposal-only/probe-only behavior.
- Red / alternative evidence:
  - red-required where code behavior changes; inspect-only for docs/config.
- Green verification:
  - targeted unittest matrix from S02..S05.
- Refactor guardrail:
  - do not remove existing regression coverage.
- report evidence destination:
  - `report.md` S06 session log and closure coverage.
- amendment trigger:
  - if a planned closure cannot be tested or inspected, amend plan.

### S07 step-local contract

- delegation contract:
  - delegated role: system-architect / implementation-planner only under verified manifest/profile/probe; main orchestrator owns promotion and report ledger
  - allowed paths: exact target `design.md` / `plan.md` and issue-local delegated evidence path from manifest
  - forbidden changes: requirement, peer artifact outside current phase, report by delegated author, implementation code/tests/config/secrets
  - output required: manifest paths, profile fragment, `session-invocation.toml`, supported invocation command or host-equivalent execution record, selected `default_permissions`, profile name/hash, probe results, changed draft artifact, metadata evidence, diff gate
- concrete tests:
  - `tc-s07-001`: design draft write uses approved requirement authority and full metadata.
  - `tc-s07-002`: design promotion occurs before plan manifest generation.
  - `tc-s07-003`: plan draft write uses approved requirement and approved design authority.
  - `tc-s07-004`: proposed plan is blocked by downstream authority gate.
  - `tc-s07-005`: forbidden path diff is empty after cleanup.
  - `tc-s07-006`: `--host-surface desktop` produces fallback/proposal-only evidence with `acceptance_counted=false` and is not counted as AC-009 / Epic acceptance without CLI-equivalent positive and negative probe evidence.
  - `tc-s07-007`: actual delegated author session evidence shows generated profile selected as `default_permissions`, `permission_profile_hash` matches manifest output, and positive probe ID is bound into the draft artifact metadata.
  - `tc-s07-008`: manual edit, unprofiled session, static broad profile, or missing invocation evidence is recorded as fallback and cannot satisfy AC-009.
  - `tc-s07-009`: S07 closure requires non-metadata body/frontmatter draft delta evidence plus manifest, session-invocation, profile/probe, and diff-gate evidence; metadata-only edits are incomplete and must be recorded as fallback, not acceptance-counted closure.
- Red / alternative evidence:
  - manual-required dogfooding evidence plus runtime authority tests.
- Green verification:
  - `git diff --check`
  - S07 pre-promotion authority gate: `./spec-dock/scripts/spec-dock validate` must fail closed with `authority_not_approved` while delegated draft artifacts remain `authority=proposed`.
  - Post-promotion S90/S99/G10 gate: `./spec-dock/scripts/spec-dock validate` must pass only after fresh review and main-orchestrator promotion metadata are recorded.
  - targeted runtime tests from S02/S05.
- Refactor guardrail:
  - no hidden broad write or manual edit substituted for delegated write without recording fallback as non-acceptance.
- report evidence destination:
  - `report.md` Delegated Draft Evidence, Evidence Adoption Ledger, S07 session log.
- amendment trigger:
  - if actual exact file write cannot be verified, record fallback and amend before claiming AC-009 pass.
  - if Desktop behavior is used as a substitute for CLI-verified write, record fallback and amend before claiming acceptance.

### S90/S99/G10 step-local contract

- delegation contract:
  - delegated role: code-reviewer, qa-reviewer, spec-reviewer, deep-consultant
  - allowed paths: review only unless follow-up fix is delegated in a bounded patch
  - output required: review_status, findings, fixed/re-review evidence
- concrete tests:
  - `tc-s90-001`: provider/dogfooding parity and validate pass.
  - `tc-s99-001`: issue-wide code/spec/QA review pass.
  - `tc-g10-001`: Epic-wide development-branch diff review by deep-consultant and spec-reviewer pass.
- Green verification:
  - `git diff --check`
  - `./spec-dock/scripts/spec-dock validate`
  - targeted unittest matrix.
- report evidence destination:
  - `report.md` S90/S99/G10 sections.
- amendment trigger:
  - every reviewer finding must receive a recorded `fixed`, `superseded`, or `explicitly_deferred_with_user_acceptance` disposition before PR update.
  - `fixed` and `superseded` findings require revalidation and fresh re-review.
  - `explicitly_deferred_with_user_acceptance` is allowed only for non-acceptance-impacting findings and must record the user acceptance evidence.
  - no P0/P1 or acceptance-impacting P2 finding may be deferred for PR update.

## 実行ルール

- 完了済み issue report を改ざんしない。
- 既存実装に合わせて scope を縮小しない。
- 実装中に helper injection が不可能と判明した場合は、plan amendment と fresh spec-review を行う。
- Fallback は安全路であり acceptance pass ではない。

## Delegated Draft Pilot Metadata

- status=approved
- authority=approved
- owner_role=main-orchestrator
- draft_author_role=implementation-planner
- approval=fresh-reviewer-pass-main-promotion
- grants=review_input,planning_input,implementation_start,issue_ready,issue_finish,phase_completion
- source_revision=0e07b86b77deebafa1e073d6f4270979be1ec5ec114095b8cfa821f78d159393
- approved_revision=0e07b86b77deebafa1e073d6f4270979be1ec5ec114095b8cfa821f78d159393
- approved_hash=0e07b86b77deebafa1e073d6f4270979be1ec5ec114095b8cfa821f78d159393
- manifest_hash=10bf95dfc8f112527f7cce3482ab4d4a210f51208efa5c330efe5821ca48a59f
- permission_profile_name=spec-dock-iss-00126-implementation-planner-plan-cli-98a21ff9ddee
- permission_profile_hash=05529d47e9aa802b46dfb5eb3bb4fe1f12a3a1a661f5f0876b5ced3a93134b59
- write_session_invocation_hash=ecf6ee59bdb484fe9735478eab768e74fa5eb4e03353b42cadd0cafd685a17dc
- probe_run_id=iss-00126-implementation-planner-plan-cli-98a21ff9ddee-positive
- positive_probe_result=pass
- acceptance_counted=true
- stale_check=fresh
- promotion_record.status=approved
- promotion_record.authority=approved
- promotion_record.source_revision=0e07b86b77deebafa1e073d6f4270979be1ec5ec114095b8cfa821f78d159393
- promotion_record.approved_revision=0e07b86b77deebafa1e073d6f4270979be1ec5ec114095b8cfa821f78d159393
- promotion_record.approved_hash=0e07b86b77deebafa1e073d6f4270979be1ec5ec114095b8cfa821f78d159393
- promotion_record.reviewer_target_hash=0e07b86b77deebafa1e073d6f4270979be1ec5ec114095b8cfa821f78d159393
- promotion_record.promotion_decision=main_orchestrator_promotion_after_fresh_review
