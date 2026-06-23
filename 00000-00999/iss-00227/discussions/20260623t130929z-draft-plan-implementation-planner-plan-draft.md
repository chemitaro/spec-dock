---
created_by_role: implementation-planner
scope_id: iss-00227
source_paths:
  - spec-dock/active/context-pack.md
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/report.md
  - spec-dock/docs/phase_plan_issue.md
  - spec-dock/docs/authoring/issue-plan.md
  - spec-dock/docs/workflow_issue.md
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/
  - tests/
intended_targets:
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/report.md
adoption_status: unreviewed
reflected_to: []
diff_guard_result: pending
---

# iss-00227 delegated implementation plan draft

This is delegated planning evidence only. It does not edit canonical `plan.md`, does not claim accepted authority, does not claim reviewer pass, and does not claim implementation readiness.

## 1. Plan Summary

Issue `iss-00227` should be implemented as the first runtime slice for Epic `epic-00224`: introduce Issue-local `assurance.json`, deterministic Assurance Profile / Complexity Tier classification, strict-legacy compatibility for missing contracts, and `spec-dock assurance show|classify|verify`.

Scope is intentionally narrow:

- In scope: Assurance Contract v1, deterministic classification policy v1, schema validation, source binding, target resolution, application results, text/json presentation, CLI registration, provider/mirror sync inspection, focused tests.
- Out of scope: Runbook compiler, artifact composition, step assurance, context routing, GitHub review trigger policy, PR blocker policy, automatic Lite default, skill kernel switching, telemetry, rollout/rollback formal close.

Delivery note: the user requested one Epic-level PR. Per-issue PR delivery is deferred to Epic delivery. Local step commits, step reviews, report evidence, and final QA/code/spec gates still apply per Issue workflow.

Planned source revision observed during this draft:

- Repository HEAD: `b56b16cb`
- Requirement source: `spec-dock/active/issue/requirement.md`, task input says `review_status pass`
- Design source: `spec-dock/active/issue/design.md`, task input says `review_status pass`
- Report source: `spec-dock/active/issue/report.md`, used as evidence ledger destination contract

## 2. Requirement / Design Traceability

### Requirement IDs Covered

- `AC-001`: Requirement-stage classification writes valid `assurance.json` with profile, tier, reasons, policy version, stage, source binding, `lite_candidate`, and `lite_authorized`.
- `AC-002`: Same canonical input, stage, and policy version produce byte-identical deterministic JSON.
- `AC-003`: Lite safety: false/unknown predicate, hard trigger, or missing opt-in/evidence gate prevents Lite authorization.
- `AC-004`: Missing `assurance.json` is detected as strict-legacy candidate without breaking existing workflow.
- `AC-005`: `assurance verify` distinguishes valid, invalid schema, invalid JSON, unknown/missing strict-legacy.
- `AC-006`: Layer boundary: domain remains pure; runtime follows existing layered architecture and does not worsen Ruff/MyPy baseline.
- `EC-001`: Unknown Lite predicate fails closed for Lite authorization.
- `EC-001b`: All predicates true without opt-in/evidence may set candidate but not authorization.
- `EC-002`: Hard triggers escalate monotonically and cannot be overridden downward.
- `EC-003`: Missing contract is strict-legacy, distinct from invalid schema/JSON.
- `EC-004`: Invalid JSON or required field omission fails verification with reason.

### Design Constraints Covered

- `DC-001`: Provider-side authority is `src/spec_dock/assets/spec_dock/...`; dogfooding `spec-dock/...` is mirror/validation target.
- `DC-002`: Domain policy is pure stdlib logic with no filesystem, GitHub, CLI, or presentation dependency.
- `DC-003`: Persisted JSON has no volatile timestamp and keeps stable field/list ordering.
- `DC-004`: Assurance Profile and Complexity Tier are separate concepts.
- `DC-005`: `lite_candidate` is shadow measurement only; only `lite_authorized` can later reduce obligations, and this Issue does not auto-authorize Lite.
- `DC-006`: Missing contract is not schema validation failure; persisted `strict-legacy` mode is not allowed in v1 contract.
- `DC-007`: `classification` and `risk_facts[]` reject semantics-changing unknown fields.
- `DC-008`: `--issue` target resolution supports active issue default, issue id / GitHub number, and repo-contained issue path with explicit target precedence.
- `DC-009`: Target path escape, non-issue path, missing path, and ambiguous symlink escape fail closed.
- `DC-010`: Public CLI default classification uses deterministic default facts, not free-form natural-language extraction.

## 3. Milestones

1. `M1 Domain contract locked`: Assurance enums, RiskFact, SourceBinding, AssuranceContract, policy matrix, schema serializer, deterministic JSON contract.
2. `M2 Store and target resolution locked`: issue target resolution, source binding hash, missing/invalid/valid store results, schema validation.
3. `M3 Runtime behavior exposed`: application use cases and presentation results for `show`, `classify`, and `verify`.
4. `M4 CLI surface wired`: parser/registry/bootstrap command wiring with CLI runtime tests.
5. `M5 Provider/mirror/docs impact resolved`: provider-side changes mirrored/inspected in dogfooding workspace and docs impact disposition recorded.
6. `M6 Final quality gates`: qa-reviewer, issue-wide code-reviewer, and spec-reviewer gates completed before Epic-level PR delivery.

## 4. Dependency-Derived Execution Order

The order follows `design.md` module dependencies:

```text
S01 domain.assurance
  -> S02 infra.assurance_store
    -> S03 application.assurance + presentation.assurance_text
      -> S04 commands.assurance + cli parser/registry/bootstrap
        -> S90 provider/mirror/docs impact
          -> S99 final quality gates
```

- `S01` must precede all downstream steps because schema validation, store behavior, application results, and CLI output all depend on stable domain value objects and deterministic serialization.
- `S02` depends on `S01` because target/source binding and contract validation must serialize/deserialize the domain contract without redefining policy.
- `S03` depends on `S02` because `show`, `classify`, and `verify` must orchestrate store outcomes and domain policy before command rendering.
- `S04` depends on `S03` because parser/registry/bootstrap should only expose the public CLI after use case contracts are stable.
- `S90` depends on `S04` because mirror/docs impact can be inspected meaningfully only after the shipped provider runtime surface exists.
- `S99` depends on all implementation and docs-impact steps and cannot substitute for step-level review or commit gates.

## 5. Issue / Step Slicing

Each implementation step is one observable behavior slice and one commit/review scope unless a plan amendment is approved.

### S01 Domain Assurance Model, Policy, Deterministic Serialization

- Behavior goal: pure domain logic can build and validate deterministic Assurance Contract v1 from supported risk facts.
- Depends on: approved requirement/design only.
- Unblocks: S02 store/schema validation, S03 use cases, all downstream CLI output.
- Target files:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/assurance.py`
  - `tests/unit/domain/test_assurance.py`
- Covered requirements: `AC-002`, `AC-003`, `AC-006`, `EC-001`, `EC-001b`, `EC-002`, design constraints `DC-002` through `DC-007`, `DC-010`.

### S02 Infra Assurance Store, Target Resolution, Source Binding, Schema Validation

- Behavior goal: runtime can resolve an issue target, read/write/verify issue-local `assurance.json`, bind requirement source hash, and distinguish missing strict-legacy from invalid data.
- Depends on: S01.
- Unblocks: S03 application `show/classify/verify`.
- Target files:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/assurance_store.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/ports.py` if a typed port is needed
  - `tests/unit/infra/test_assurance_store.py`
- Covered requirements: `AC-001`, `AC-004`, `AC-005`, `AC-006`, `EC-003`, `EC-004`, design constraints `DC-001`, `DC-003`, `DC-006`, `DC-008`, `DC-009`.

### S03 Application Use Cases and Presentation Outputs

- Behavior goal: `show`, `classify`, and `verify` have stable request/result contracts and renderable text/json outcomes independent of argparse.
- Depends on: S01, S02.
- Unblocks: S04 CLI command wiring.
- Target files:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/assurance.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/assurance_text.py`
  - `tests/unit/application/test_assurance.py`
  - `tests/unit/presentation/test_assurance_text.py`
- Covered requirements: `AC-001`, `AC-004`, `AC-005`, `AC-006`, `EC-003`, `EC-004`.

### S04 CLI Parser, Registry, Bootstrap Wiring and Runtime Tests

- Behavior goal: users can execute `spec-dock assurance show|classify|verify` with active/default or explicit issue target and text/json formats.
- Depends on: S03.
- Unblocks: S90 mirror/docs inspection and final gates.
- Target files:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/assurance.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/__init__.py` if needed by existing import style
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/parser.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/registry.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/bootstrap.py`
  - `tests/cli_runtime/test_assurance.py`
- Covered requirements: `AC-001`, `AC-004`, `AC-005`, `AC-006`, `EC-003`, `EC-004`, design constraints `DC-008`, `DC-009`.

### S90 Provider/Mirror/Docs Impact Sync and Inspection

- Behavior goal: provider implementation remains the authority, dogfooding mirror impact is resolved, and docs/template changes are either updated or explicitly recorded as no-op.
- Depends on: S04.
- Unblocks: S99.
- Target files if sync/update is required:
  - `spec-dock/scripts/spec_dock_runtime/`
  - `spec-dock/docs/`
  - `src/spec_dock/assets/spec_dock/docs/`
  - `src/spec_dock/assets/spec_dock/templates/`
- Covered requirements: `AC-006`, `DC-001`, S90 docs/mirror impact.

### S99 Final QA, Code, Spec Gate

- Behavior goal: issue-wide evidence is complete, required tests and reviews are passed, and the issue is ready for main orchestrator adoption decisions without per-issue PR delivery.
- Depends on: S01-S04 and S90.
- Target files:
  - `spec-dock/active/issue/report.md` for observed evidence ledger updates by the main orchestrator
  - no implementation changes except reviewer-driven bounded follow-up under amended/approved step scope
- Covered requirements: all AC/EC, all design constraints, final exit contract.

### Step Execution Contracts

#### S01 Contract

- Delegation contract:
  - Delegated role: `dev-coder`.
  - Input docs: approved requirement/design, this adopted plan, `workflow_issue.md`, `phase_plan_issue.md`, `authoring/issue-plan.md`, existing `domain/` test style.
  - Allowed paths:
    - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/assurance.py`
    - `tests/unit/domain/test_assurance.py`
  - Forbidden paths/changes:
    - no infra/application/CLI/presentation code;
    - no dogfooding mirror mutation;
    - no docs/templates/config/skill/GitHub state;
    - no policy duplication outside domain.
  - Acceptance criteria: closure IDs `cl-ac002-deterministic-json`, `cl-ac003-lite-safety`, `cl-ec002-hard-trigger-monotonic`, `cl-ac006-layer-boundary`, `cl-dc010-default-facts` have passing evidence.
  - Required tests: red-first `tests/unit/domain/test_assurance.py`, then green; import boundary inspection or static test.
  - Reviewer focus: `code-reviewer` checks pure domain boundary, deterministic serialization, policy matrix completeness, enum/profile/tier separation.
  - Stop conditions: design policy table contradiction, need for filesystem/CLI access in domain, inability to produce byte-identical JSON, or need to change public CLI before domain contract is stable.
  - Output required: changed files, test command/results, unresolved risks, material decision ledger note or `No material implementation decisions beyond the approved plan.`
- Red evidence path:
  - Add failing domain tests for deterministic serialization, Lite safety, hard triggers, and supported default facts.
- Green evidence path:
  - `uv run pytest tests/unit/domain/test_assurance.py`.
- Report evidence destination:
  - `report.md` Session Log, TDD evidence, Step Contract Closure, Test Contract Closure, Closure Coverage, Implementation Delegation Gate, Delegated Worker Evidence, Reviewer Gate Status, Step Commit Gate.
- Commit gate:
  - Commit S01 only after tests pass, fresh `code-reviewer` pass, report evidence is updated, and post-commit clean check is recorded.

#### S02 Contract

- Delegation contract:
  - Delegated role: `dev-coder`.
  - Input docs: S01 committed contract, approved design target resolution/schema validation sections, existing infra/json_store and target normalization patterns.
  - Allowed paths:
    - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/assurance_store.py`
    - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/ports.py` only if a typed port boundary is required
    - `tests/unit/infra/test_assurance_store.py`
  - Forbidden paths/changes:
    - no parser/registry/bootstrap command wiring;
    - no policy decisions outside S01 domain;
    - no mirror/docs/config/skill/GitHub state;
    - no migration of existing issues.
  - Acceptance criteria: closure IDs `cl-ac001-classify-contract-write`, `cl-ac004-strict-legacy-missing`, `cl-ac005-invalid-contract`, `cl-dc008-target-resolution` have passing evidence at infra level.
  - Required tests: red-first infra tests for source binding, missing strict-legacy, invalid JSON/schema, explicit target path safety.
  - Reviewer focus: `code-reviewer` checks path containment, symlink/escape handling, missing-vs-invalid distinction, schema validation strictness, source binding durability.
  - Stop conditions: existing target helpers cannot support required semantics without broader refactor, path resolution needs repo-global behavior change, or deterministic persistence conflicts with existing JSON helper.
  - Output required: changed files, test command/results, target resolution risks, material decision ledger note or no-decision statement.
- Red evidence path:
  - Add failing infra tests for each store/target/source-binding behavior before implementation.
- Green evidence path:
  - `uv run pytest tests/unit/infra/test_assurance_store.py`.
- Report evidence destination:
  - Same report ledgers as S01 plus Closure Delta if target-resolution closure IDs require amendment.
- Commit gate:
  - Commit S02 only after S01 remains green, S02 tests pass, fresh `code-reviewer` pass, and clean check is recorded.

#### S03 Contract

- Delegation contract:
  - Delegated role: `dev-coder`.
  - Input docs: S01/S02 committed contracts, approved application/presentation design, existing `application/contracts.py` and presentation style.
  - Allowed paths:
    - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/assurance.py`
    - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py`
    - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/assurance_text.py`
    - `tests/unit/application/test_assurance.py`
    - `tests/unit/presentation/test_assurance_text.py`
  - Forbidden paths/changes:
    - no argparse/parser/registry/bootstrap wiring;
    - no infra path-resolution redesign beyond S02 contract;
    - no new classification policy in presentation;
    - no docs/mirror/config/skill/GitHub state.
  - Acceptance criteria: classify dry-run/write behavior, show/verify valid/missing/invalid mapping, and stable text/json render paths are covered.
  - Required tests: red-first application and presentation tests for result mapping and rendering.
  - Reviewer focus: `code-reviewer` checks use case orchestration, result dataclass clarity, presentation as rendering only, exit behavior readiness for CLI.
  - Stop conditions: use case needs a new design decision about exit semantics, result model conflicts with schema, or presentation must infer policy not present in domain/application result.
  - Output required: changed files, test command/results, unresolved output contract risks, material decision ledger note or no-decision statement.
- Red evidence path:
  - Add failing application/presentation tests for classify/show/verify behavior before implementation.
- Green evidence path:
  - `uv run pytest tests/unit/application/test_assurance.py tests/unit/presentation/test_assurance_text.py`.
- Report evidence destination:
  - Session Log, TDD evidence, Step/Test Contract Closure, Closure Coverage, Implementation Delegation Gate, Delegated Worker Evidence, Reviewer Gate Status, Step Commit Gate.
- Commit gate:
  - Commit S03 only after S01/S02 focused tests remain green as needed, S03 tests pass, fresh `code-reviewer` pass, and clean check is recorded.

#### S04 Contract

- Delegation contract:
  - Delegated role: `dev-coder`.
  - Input docs: S01-S03 committed contracts, approved CLI interface design, existing parser/registry/bootstrap and `commands/*` style, CLI runtime harness.
  - Allowed paths:
    - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/assurance.py`
    - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/__init__.py` if required by local import style
    - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/parser.py`
    - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/registry.py`
    - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/bootstrap.py`
    - `tests/cli_runtime/test_assurance.py`
  - Forbidden paths/changes:
    - no domain policy changes unless S01 closure is amended and re-reviewed;
    - no broad command registry refactor;
    - no docs/mirror changes in this step;
    - no GitHub/network behavior.
  - Acceptance criteria: public CLI supports `show`, `classify --stage requirement`, `verify`, `--format text|json`, `--issue`, `--dry-run` where designed, with required exit behavior.
  - Required tests: red-first CLI runtime tests for classify write, strict-legacy show/verify, invalid verify failure, explicit target precedence.
  - Reviewer focus: `code-reviewer` checks parser registration, command argument contracts, bootstrap wiring, exit codes, regression risk to existing commands.
  - Stop conditions: command surface requires new requirement/design semantics, existing parser pattern cannot express subcommands cleanly without broad refactor, or CLI tests require live network.
  - Output required: changed files, CLI test command/results, unresolved command compatibility risks, material decision ledger note or no-decision statement.
- Red evidence path:
  - Add failing `tests/cli_runtime/test_assurance.py` cases before CLI wiring.
- Green evidence path:
  - `uv run pytest tests/cli_runtime/test_assurance.py`.
  - If parser/bootstrap changes are broad, also run `uv run pytest tests/cli_runtime`.
- Report evidence destination:
  - Same step ledgers plus command output snippets sufficient to prove exit behavior.
- Commit gate:
  - Commit S04 only after CLI runtime tests pass, relevant prior focused tests remain green as needed, fresh `code-reviewer` pass, and clean check is recorded.

#### S90 Contract

- Delegation contract:
  - Delegated role: `doc-writer` if docs/templates/mirror text changes are required; otherwise inspect-only no-op with spec-reviewer confirmation.
  - Input docs: S01-S04 completed diff, provider/mirror authority rules, docs/templates affected by public CLI surface.
  - Allowed paths when changes are required:
    - `spec-dock/scripts/spec_dock_runtime/`
    - `spec-dock/docs/`
    - `src/spec_dock/assets/spec_dock/docs/`
    - `src/spec_dock/assets/spec_dock/templates/`
  - Forbidden paths/changes:
    - no domain/application/infra/CLI implementation edits unless sent back to the owning S01-S04 step;
    - no canonical issue requirement/design/plan/report edits by delegated worker;
    - no skills/config/GitHub state.
  - Acceptance criteria: provider/mirror impact is synced or explicitly no-op with inspected paths; docs/templates impact is updated or no-op justified.
  - Required verification: docs diff/inspection, mirror inspection, `./spec-dock/scripts/spec-dock validate` if spec tree or dogfooding workspace changed.
  - Reviewer focus: `spec-reviewer` checks docs/spec alignment and no unresolved S90 impact remains.
  - Stop conditions: docs change would alter requirement/design scope, mirror sync produces unrelated churn, or implementation files need correction.
  - Output required: changed files or no-op inspected paths, verification results, docs impact disposition, unresolved docs/mirror risks.
- Red/alternative evidence path:
  - Inspect-only first: list docs/mirror surfaces that would fail if omitted; docs code tests are not required unless a template/runtime fixture exists.
- Green evidence path:
  - If changed: focused docs/template inspection plus `./spec-dock/scripts/spec-dock validate` when applicable.
  - If no-op: report inspected paths and no-op rationale.
- Report evidence destination:
  - Docs Impact Resolution, Delegated Worker Evidence if doc-writer used, Reviewer Gate Status, Step Commit Gate or approved-no-op evidence.
- Commit gate:
  - Commit S90 only if docs/mirror files changed and spec-reviewer passes; otherwise record approved-no-op with diff-clean command and read-only evidence.

#### S99 Contract

- Delegation contract:
  - Delegated roles: `qa-reviewer`, issue-wide `code-reviewer`, final `spec-reviewer`; no implementation worker unless a reviewer finding sends work back to an owning step.
  - Input docs: final requirement/design/plan/report, full issue diff, all step evidence, S90 disposition, test outputs.
  - Allowed paths:
    - report ledger updates by the main orchestrator;
    - reviewer-driven bounded follow-up only through the affected S01-S04/S90 scope after recording the finding.
  - Forbidden paths/changes:
    - no new implementation hidden inside final commit;
    - no per-issue PR creation;
    - no claiming complete without all required gates;
    - no reviewer waiver treated as pass.
  - Acceptance criteria: all required closure IDs are pass/approved-no-op, all step commits/reviews are recorded, S90 resolved, final QA/code/spec reviewers pass, Epic-level PR deferral note is present.
  - Required verification: focused tests, broader regression lanes as risk-calibrated, validate/sync evidence if required by touched surfaces.
  - Reviewer focus: QA coverage gaps, integrated architecture risk, spec/report/docs alignment, and PR delivery boundary.
  - Stop conditions: any final reviewer fails/unavailable/denied without explicit blocking classification, missing closure evidence, uncommitted step diff, unresolved docs impact, or per-issue PR delivery attempted.
  - Output required: final reviewer results, final report ledger status, unresolved risks or none, Epic-level PR deferral evidence.
- Red/alternative evidence path:
  - Reviewers inspect existing closure/test evidence; new red tests are added only if QA/code/spec reviewer identifies missing coverage and sends work back to the owning step.
- Green evidence path:
  - All relevant focused tests and selected broader lanes pass; final reviewers pass.
- Report evidence destination:
  - Final QA Gate, Final Code Review Gate, Final Spec Review Gate, Final Commit, PR Delivery Gate note deferring per-issue PR to Epic-level PR.
- Commit gate:
  - Final commit closes report/delivery evidence only; it must not bundle uncommitted implementation from prior steps.

## 6. Test Strategy Mapping

### Spec-Locked Closure Index

| ID | Step | Type | Spec link | Locked expectation | Observable input/state | Bug class guarded | Required | Evidence level | Closure evidence |
|---|---|---|---|---|---|---|---|---|---|
| `cl-ac001-classify-contract-write` | S02/S03/S04 | acceptance | AC-001 | `classify --stage requirement` writes valid v1 `assurance.json` with profile, tier, reasons, policy, stage, source binding, candidate/auth flags | temp spec repo with active or explicit issue and requirement artifact | classification does not persist machine-readable contract | yes | red-required | report Step/Test Contract Closure and CLI runtime result |
| `cl-ac002-deterministic-json` | S01 | invariant | AC-002/DC-003 | repeated classification/serialization for same input is byte-identical and omits volatile timestamps | same facts, issue id, source binding, policy version | timestamp/order nondeterminism | yes | red-required | domain deterministic serialization test |
| `cl-ac003-lite-safety` | S01 | negative | AC-003/EC-001/EC-001b | false/unknown predicates or missing opt-in/evidence keep `lite_authorized=false` and authorized profile at least `standard` | policy matrix with false, unknown, and all-positive-no-opt-in cases | unsafe Lite authorization | yes | red-required | domain policy matrix test |
| `cl-ec002-hard-trigger-monotonic` | S01 | negative | EC-002/DC-004 | hard triggers escalate to `strict`/`critical` and lower profiles cannot override them | facts with public contract, migration, security, rollback triggers | downscoped hard-risk profile | yes | red-required | hard trigger matrix test |
| `cl-ac004-strict-legacy-missing` | S02/S03/S04 | compatibility | AC-004/EC-003/DC-006 | missing `assurance.json` returns strict-legacy candidate and exit 0 for show/verify | issue dir without `assurance.json` | legacy issues blocked as corrupted | yes | red-required | infra/app/CLI missing-contract tests |
| `cl-ac005-invalid-contract` | S02/S03/S04 | negative | AC-005/EC-004 | invalid JSON/schema fails verify with reason and is distinct from missing | malformed JSON and required-field-missing fixtures | corruption hidden as legacy missing | yes | red-required | schema validation and CLI exit-code tests |
| `cl-ac006-layer-boundary` | S01-S04 | architecture | AC-006/DC-002 | domain imports no filesystem/GitHub/CLI/presentation modules; command policy is not duplicated outside domain | static import inspection and focused tests | policy leaking into command/infra | yes | inspect-only plus test | import inspection and code-review evidence |
| `cl-dc008-target-resolution` | S02/S04 | acceptance/negative | DC-008/DC-009 | explicit issue target wins over active; issue id/GitHub number/path accepted; path escape/non-issue/missing target rejected | temp repo with active issue plus explicit targets | wrong issue classified or path escape | yes | red-required | infra and CLI runtime target tests |
| `cl-dc010-default-facts` | S01/S03 | invariant | DC-010 | public CLI classification emits every supported fact in stable order with deterministic defaults and consequence reasons | no explicit structured facts | free-form extraction or missing audit facts | yes | red-required | domain/app JSON fixture assertion |
| `cl-s90-provider-mirror-docs` | S90 | docs/mirror | DC-001/S90 | provider changes are mirrored or intentionally not mirrored with evidence; docs impact is updated or no-op justified | provider diff and dogfooding workspace inspection | shipped asset and dogfooding drift | yes | inspect-only | S90 Docs Impact Resolution report entry |
| `cl-s99-final-quality` | S99 | final gate | workflow_issue.md | QA, issue-wide code, and final spec review pass; per-issue PR is deferred to Epic PR by explicit note | final branch diff, report ledgers, test results | final gate replacing step gates or accidental per-issue PR | yes | manual-required plus review | Final QA/Code/Spec Gate report entries |

### Step-Local Test Case Cards

#### S01 Concrete Test Case Cards

- `tc-s01-001` acceptance: deterministic default contract serialization
  - Premise: domain receives issue id `iss-00227`, stage `requirement`, policy version `assurance-policy-v1`, source binding, and no structured fact overrides.
  - Action: build and serialize the contract twice.
  - Expected: serialized JSON bytes are identical, include all supported facts in stable order, and omit `generated_at` / `classified_at`.
  - Failure detection: unstable dict/list order, missing default facts, or volatile timestamp breaks equality.
  - Verification method: `tests/unit/domain/test_assurance.py` red-first test.
  - Related closure IDs: `cl-ac002-deterministic-json`, `cl-dc010-default-facts`.

- `tc-s01-002` negative: Lite authorization remains false for unknown and no-opt-in cases
  - Premise: facts include unknown Lite predicate values, then a separate all-positive Lite candidate case without explicit opt-in/evidence.
  - Action: classify both fact sets.
  - Expected: `lite_authorized=false`; authorized profile is at least `standard`; all-positive/no-opt-in may set `lite_candidate=true` only.
  - Failure detection: all-positive predicate alone authorizes Lite or unknown facts are treated as safe.
  - Verification method: `tests/unit/domain/test_assurance.py` matrix test.
  - Related closure IDs: `cl-ac003-lite-safety`.

- `tc-s01-003` negative: hard trigger escalation is monotonic
  - Premise: public contract, migration/persistence, rollback-high, and security/privacy hard triggers appear individually and in combination.
  - Action: classify each matrix case.
  - Expected: strict triggers yield at least `strict`, security/privacy yields `critical`, and the highest profile wins.
  - Failure detection: lower profile override or complexity/profile conflation.
  - Verification method: `tests/unit/domain/test_assurance.py` hard-trigger matrix test.
  - Related closure IDs: `cl-ec002-hard-trigger-monotonic`.

- `tc-s01-004` inspect-only: domain layer import boundary
  - Premise: `domain/assurance.py` is added.
  - Action: inspect imports or add a small static assertion over source imports.
  - Expected: no imports from `infra`, `commands`, `cli`, `presentation`, GitHub adapters, or filesystem-specific runtime modules.
  - Failure detection: policy becomes coupled to runtime adapters.
  - Verification method: inspect-only or focused static test in `tests/unit/domain/test_assurance.py`.
  - Related closure IDs: `cl-ac006-layer-boundary`.

#### S02 Concrete Test Case Cards

- `tc-s02-001` acceptance: source binding uses resolved issue-local requirement path and sha256
  - Premise: temp repo has active issue requirement and the active symlink path points to it.
  - Action: resolve target and create source binding.
  - Expected: persisted `path` is repo-relative issue-local path, optional `display_path` may be `spec-dock/active/issue/requirement.md`, and `sha256` is lowercase 64-hex.
  - Failure detection: durable binding stores only mutable active symlink or wrong hash.
  - Verification method: `tests/unit/infra/test_assurance_store.py`.
  - Related closure IDs: `cl-ac001-classify-contract-write`.

- `tc-s02-002` compatibility: missing contract is strict-legacy
  - Premise: target issue exists and has no `assurance.json`.
  - Action: store read/verify is called.
  - Expected: result mode is strict-legacy/missing, not invalid schema, and callers can map it to show/verify exit 0.
  - Failure detection: missing file raises invalid/corrupt error.
  - Verification method: `tests/unit/infra/test_assurance_store.py`.
  - Related closure IDs: `cl-ac004-strict-legacy-missing`.

- `tc-s02-003` negative: invalid JSON and invalid schema are distinct failures
  - Premise: one fixture has malformed JSON; another omits required fields such as `schema_version` or uses unsupported enum values.
  - Action: verify/read contract.
  - Expected: both fail, but machine-readable reason distinguishes parse failure from schema validation failure.
  - Failure detection: invalid data is accepted or collapsed into strict-legacy missing.
  - Verification method: `tests/unit/infra/test_assurance_store.py`.
  - Related closure IDs: `cl-ac005-invalid-contract`.

- `tc-s02-004` negative: explicit path target cannot escape repo or select non-issue dir
  - Premise: temp repo includes valid issue dir, non-issue dir, missing path, and if supported a symlink escape candidate.
  - Action: resolve each explicit `--issue` path target.
  - Expected: repo-contained issue path is accepted; escape, missing, non-issue, and ambiguous symlink escape fail closed.
  - Failure detection: arbitrary path is classified or active target is silently used after explicit target failure.
  - Verification method: `tests/unit/infra/test_assurance_store.py`.
  - Related closure IDs: `cl-dc008-target-resolution`.

#### S03 Concrete Test Case Cards

- `tc-s03-001` acceptance: classify writes or dry-runs through application use case
  - Premise: application receives `ClassifyAssuranceRequest(stage="requirement", dry_run=False)` for a valid issue.
  - Action: run use case.
  - Expected: non-dry-run writes `assurance.json`; dry-run returns the same deterministic contract without writing.
  - Failure detection: dry-run mutates disk, or persisted JSON differs from returned JSON.
  - Verification method: `tests/unit/application/test_assurance.py`.
  - Related closure IDs: `cl-ac001-classify-contract-write`, `cl-ac002-deterministic-json`.

- `tc-s03-002` acceptance: show/verify result mapping preserves missing vs invalid
  - Premise: application sees valid contract, missing contract, invalid JSON, and invalid schema cases.
  - Action: run `show` and `verify` use cases.
  - Expected: valid and missing strict-legacy return successful result kinds; invalid cases return failure kinds with reasons.
  - Failure detection: invalid data is rendered as strict-legacy or missing exits as failure.
  - Verification method: `tests/unit/application/test_assurance.py`.
  - Related closure IDs: `cl-ac004-strict-legacy-missing`, `cl-ac005-invalid-contract`.

- `tc-s03-003` presentation: text/json output exposes stable fields without policy duplication
  - Premise: presentation receives representative valid, strict-legacy, and invalid result objects.
  - Action: render text and json output.
  - Expected: json uses stable keys; text names mode/profile/tier/reasons; presentation does not recompute policy decisions.
  - Failure detection: renderer changes classification semantics or omits strict-legacy/invalid reason.
  - Verification method: `tests/unit/presentation/test_assurance_text.py`.
  - Related closure IDs: `cl-ac004-strict-legacy-missing`, `cl-ac005-invalid-contract`, `cl-ac006-layer-boundary`.

#### S04 Concrete Test Case Cards

- `tc-s04-001` acceptance: CLI classify creates deterministic `assurance.json`
  - Premise: CLI runtime harness initializes a temp repo with active issue and requirement.
  - Action: run `spec-dock assurance classify --stage requirement --format json`.
  - Expected: exit 0, stdout JSON reports adaptive standard/default classification, and issue-local `assurance.json` exists with matching deterministic fields.
  - Failure detection: command missing, parser not registered, no file written, or output contract differs.
  - Verification method: `tests/cli_runtime/test_assurance.py`.
  - Related closure IDs: `cl-ac001-classify-contract-write`.

- `tc-s04-002` compatibility: CLI show/verify strict-legacy missing exits 0
  - Premise: temp repo issue has no `assurance.json`.
  - Action: run `assurance show --format json` and `assurance verify --format json`.
  - Expected: exit 0 and JSON indicates `mode: strict-legacy` / `has_contract: false`.
  - Failure detection: legacy issue is blocked or missing is confused with invalid JSON.
  - Verification method: `tests/cli_runtime/test_assurance.py`.
  - Related closure IDs: `cl-ac004-strict-legacy-missing`.

- `tc-s04-003` negative: CLI verify invalid contract exits 1
  - Premise: temp repo issue contains malformed or schema-invalid `assurance.json`.
  - Action: run `spec-dock assurance verify --format json`.
  - Expected: exit 1 with machine-readable invalid reason.
  - Failure detection: corrupted contract is accepted, hidden as missing, or exits 0.
  - Verification method: `tests/cli_runtime/test_assurance.py`.
  - Related closure IDs: `cl-ac005-invalid-contract`.

- `tc-s04-004` target resolution: explicit issue target precedence
  - Premise: temp repo has active issue A and explicit issue B.
  - Action: run classify/show with `--issue <B id|GitHub number|path>`.
  - Expected: issue B is used and active issue A remains unaffected.
  - Failure detection: command silently uses active issue despite explicit target.
  - Verification method: `tests/cli_runtime/test_assurance.py`.
  - Related closure IDs: `cl-dc008-target-resolution`.

#### S90 Concrete Evidence Cards

- `tc-s90-001` inspect-only: provider/mirror runtime impact
  - Premise: S01-S04 provider runtime changes are complete.
  - Action: run the project-approved scaffold update/mirror inspection path or explicitly inspect provider vs dogfooding mirror diff.
  - Expected: mirror impact is either synchronized or recorded as intentionally deferred with non-blocking rationale accepted by spec-reviewer.
  - Failure detection: provider and dogfooding runtime drift without evidence.
  - Verification method: report S90 Docs Impact Resolution entry and `git diff`/inspection evidence.
  - Related closure IDs: `cl-s90-provider-mirror-docs`.

- `tc-s90-002` inspect-only: docs/templates impact
  - Premise: new public CLI command `assurance` exists.
  - Action: inspect docs/templates/README/workflow/skill surfaces for command references and user-facing contract impact.
  - Expected: required docs are updated by doc-writer, or no-op is justified with concrete inspected paths.
  - Failure detection: public command ships without docs impact disposition.
  - Verification method: report S90 entry and spec-reviewer docs/spec alignment.
  - Related closure IDs: `cl-s90-provider-mirror-docs`.

#### S99 Concrete Evidence Cards

- `tc-s99-001` final QA: issue-wide test sufficiency
  - Premise: S01-S04 and S90 are complete with report evidence.
  - Action: qa-reviewer reviews closure coverage and decides whether integration tests are sufficient.
  - Expected: qa-reviewer pass or bounded follow-up tests added and re-reviewed.
  - Failure detection: closure IDs closed only by unit tests while CLI/integration risk remains untested.
  - Verification method: report Final QA Gate.
  - Related closure IDs: `cl-s99-final-quality`.

- `tc-s99-002` final code/spec: integrated diff and spec alignment
  - Premise: final branch diff and report ledger are ready.
  - Action: issue-wide code-reviewer and spec-reviewer review the integrated result.
  - Expected: both pass; any findings are fixed through bounded follow-up and re-reviewed.
  - Failure detection: final review substitutes for missing step review, or spec/docs/report drift remains.
  - Verification method: report Final Code Review Gate and Final Spec Review Gate.
  - Related closure IDs: `cl-s99-final-quality`.

## 7. Review Gates

### Per-Step Gates

For S01-S04:

- Delegation: primary worker `dev-coder`; parent orchestrator records Implementation Delegation Gate.
- Reviewer: `code-reviewer`.
- Required before commit:
  - step closure IDs have observed evidence in `report.md`;
  - targeted tests pass;
  - reviewer returns fresh pass;
  - report ledger records changed files, tests, risks, closure coverage, and worker evidence.
- Commit gate:
  - one step equals one commit;
  - commit only that step scope and report evidence;
  - post-commit `git status --short` clean or intentional remaining work recorded for the next step.

For S90:

- Delegation: `doc-writer` when docs/templates need mutation; otherwise inspect-only no-op is allowed only with explicit evidence.
- Reviewer: `spec-reviewer` docs/spec alignment.
- Commit gate:
  - committed if docs/mirror changes are needed;
  - approved-no-op only if inspected paths and no-op rationale are recorded.

For S99:

- Reviewers:
  - `qa-reviewer` for obligation coverage and integration test sufficiency;
  - issue-wide `code-reviewer` for integrated diff and maintainability;
  - `spec-reviewer` for requirement/design/plan/report/docs alignment.
- No final reviewer may substitute for missing per-step review.
- Any fail result requires bounded follow-up in the owning step scope or plan amendment if the finding expands scope.

### PR Gate Note

- No per-issue PR should be created for `iss-00227`.
- Report should explicitly state: user requested one Epic-level PR, so per-issue PR delivery is deferred to Epic delivery.
- Epic-level PR delivery must still include this issue's step commits, reviewer evidence, test output, and final gate evidence.

## 8. Rollback / Compatibility

- Rollback strategy:
  - S01 rollback removes domain assurance module and its tests before downstream steps depend on it.
  - S02 rollback removes store/target/source-binding code and infra tests; no tracked user data migration is introduced.
  - S03 rollback removes use cases/presentation output and associated contract additions.
  - S04 rollback removes CLI registration and `assurance` command surface; existing commands remain unaffected.
  - S90 rollback reverts mirror/docs changes or records no-op.
- Compatibility:
  - Existing issues without `assurance.json` remain usable as strict-legacy candidates.
  - Invalid `assurance.json` fails verification and is not silently accepted.
  - v1 persisted contract does not contain volatile timestamps, avoiding churn in tracked files.
  - v1 does not automatically authorize Lite or reduce obligations.
  - Provider-side source remains authority; mirror update is validation/inspection target.
- Data migration:
  - No migration is planned for existing issues.
  - Creation of new tracked `assurance.json` occurs only when `assurance classify` is run against a target issue.

## 9. Docs Impact

S90 must resolve these surfaces before S99:

- Provider docs/templates:
  - `src/spec_dock/assets/spec_dock/docs/`
  - `src/spec_dock/assets/spec_dock/templates/`
- Dogfooding mirror docs/runtime:
  - `spec-dock/docs/`
  - `spec-dock/scripts/spec_dock_runtime/`
- User-facing CLI references:
  - command list/help examples if maintained in shipped docs;
  - workflow docs only if they reference assurance contract or dynamic workflow resource allocation behavior.

Docs update decision:

- If public `assurance` CLI is discoverable from `--help` only and no docs surface currently inventories every command, S90 may record inspected paths and no-op rationale.
- If docs/templates describe runtime commands, active issue workflow, or future adaptive assurance contracts, S90 must update them through `doc-writer`.
- Any docs/mirror changes require `spec-reviewer` docs/spec alignment pass.

## 10. Final Quality Gate

S99 final quality gate must not start until S01-S04 and S90 are closed as committed or approved-no-op.

Required validation candidates:

- Focused unit/domain: `uv run pytest tests/unit/domain/test_assurance.py`
- Focused infra/application/presentation:
  - `uv run pytest tests/unit/infra/test_assurance_store.py`
  - `uv run pytest tests/unit/application/test_assurance.py`
  - `uv run pytest tests/unit/presentation/test_assurance_text.py`
- CLI runtime: `uv run pytest tests/cli_runtime/test_assurance.py`
- Broader regression if touched command/bootstrap surfaces warrant it:
  - `uv run pytest tests/unit`
  - `uv run pytest tests/cli_runtime`
- Static/lint/type baseline according to current repo commands, at minimum the project-approved lint/type lane if available.
- `./spec-dock/scripts/spec-dock validate` after docs/mirror updates if the spec tree or dogfooding workspace is touched.

Final reviewer gates:

- `qa-reviewer`: confirms AC/EC closure coverage, negative path coverage, deterministic behavior coverage, CLI/runtime coverage, and whether integration tests are sufficient.
- `code-reviewer`: reviews issue-wide diff for layering, contract clarity, deterministic serialization, target resolution safety, and regression risk.
- `spec-reviewer`: checks requirement/design/plan/report/docs alignment, S90 disposition, closure index coverage, and deferred per-issue PR note.

S99 pass cannot be claimed unless all three reviewers pass and report evidence is recorded by the main orchestrator.

### Final Exit Contract

The issue may be treated as exit-ready by the main orchestrator only when all of the following are true:

- Canonical `plan.md` has adopted or rejected this draft through Evidence Adoption Ledger, and fresh `spec-reviewer` has passed the canonical plan.
- S01-S04 are each closed as `committed` with step-local tests, fresh `code-reviewer` pass, report closure evidence, and post-commit clean check.
- S90 is closed as `committed` or valid `approved-no-op`, with docs/mirror impact evidence and `spec-reviewer` docs/spec alignment pass.
- Every required closure ID in the Spec-Locked Closure Index is recorded as pass or approved-no-op in `report.md` Step Contract Closure, Test Contract Closure, and Closure Coverage.
- `qa-reviewer`, issue-wide `code-reviewer`, and final `spec-reviewer` all pass S99.
- Final report ledger records unresolved risks as `none` or records blocking/non-blocking disposition with next action.
- No per-issue PR is opened; report records that delivery is deferred to the user-requested Epic-level PR.
- Any final commit contains only final report/delivery evidence and does not bundle uncommitted implementation from prior steps.

## 11. Plan Blockers

No design blocker found in the read-only evidence for this draft.

Planning concerns to preserve for the main orchestrator:

- `report.md` currently contains older ledger text saying design re-review was pending; task input states requirement/design are now pass. Main orchestrator should reconcile report ledger status before canonical plan adoption.
- Exact implementation of issue path target resolution should reuse existing target/normalization patterns where possible; if no suitable helper exists, any new helper must stay in infra/application boundaries and be covered by S02/S04 negative tests.
- Deterministic JSON may need a domain-owned serializer or explicit canonical dict builder because existing `infra/json_store.py` writes indented JSON without `sort_keys`. Do not rely on incidental dict insertion order unless tests lock the exact byte output.
- If docs surfaces have no canonical command inventory, S90 can be approved-no-op only after explicit inspected-path evidence and spec-reviewer agreement.
- If reviewer/sub-agent tools are unavailable, the issue remains incomplete or blocked under `workflow_issue.md`; availability failure is not a reviewer pass.

## 12. Integration Notes for Main Orchestrator

Suggested adoption flow:

1. Verify this discussion draft is the only delegated implementation-planner output being considered for plan adoption.
2. Run a diff guard before adoption and record the result in `report.md` Delegated Draft Evidence and Evidence Adoption Ledger.
3. Reconcile report ledger status with current passed requirement/design reviewer evidence.
4. Integrate selected planning content into canonical `plan.md`; do not copy the delegated provenance claims as accepted authority.
5. Run fresh `spec-reviewer` on canonical `plan.md`.
6. During execution, keep one step at a time: delegate, implement, test, review, record, commit, clean check, then proceed.
7. Keep per-issue PR delivery deferred and record that final GitHub delivery happens through the user-requested Epic-level PR.

Lightweight provenance summary:

- Leaf evidence used: issue requirement/design/report, issue plan authoring docs, workflow issue docs, runtime source layout, tests layout.
- Forbidden actions avoided: no canonical docs edited, no implementation files edited, no tests/configs/skills/GitHub state edited, no reviewer pass or implementation readiness claimed.
- Unresolved design gaps: none identified as blockers; planning concerns above require orchestrator reconciliation/evidence handling.

No canonical edit, final authority, promotion, reviewer-pass, implementation-readiness, or user-dialogue ownership is claimed.
