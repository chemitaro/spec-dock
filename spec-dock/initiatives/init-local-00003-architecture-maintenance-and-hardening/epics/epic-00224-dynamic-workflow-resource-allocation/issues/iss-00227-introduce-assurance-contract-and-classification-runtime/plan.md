---
種別: 実装計画書（Issue）
ID: "iss-00227"
タイトル: "Introduce Assurance Contract And Classification Runtime"
関連GitHub: ["#227"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-23"
依存: ["requirement.md", "design.md"]
親: ["epic-00224", "init-local-00003"]
---

# iss-00227 Introduce Assurance Contract And Classification Runtime — 実装計画（実行契約 / Execution Contract）

## この計画で満たす要件ID

- AC: AC-001, AC-002, AC-003, AC-004, AC-005, AC-006
- EC: EC-001, EC-001b, EC-002, EC-003, EC-004
- 設計制約:
  - Provider source が authority、dogfooding mirror は validation target。
  - Domain policy は pure stdlib logic。
  - persisted JSON は volatile timestamp を含まず deterministic。
  - `lite_candidate` と `lite_authorized` を分離し、automatic Lite default は有効化しない。
  - missing contract は strict-legacy view、invalid JSON/schema は failure。
  - `classification` / `risk_facts[]` 配下の semantics-changing unknown fields は invalid。
  - `--issue` explicit target は active issue より優先し、issue id / GitHub number / repo-contained issue path を扱う。

## 依存関係から導く実装順序

```text
S01 domain.assurance
  -> S02 infra.assurance_store
    -> S03 application.assurance + presentation.assurance_text
      -> S04 commands.assurance + cli parser/registry/bootstrap
        -> S90 provider/mirror/docs impact
          -> S99 final quality gates
```

- S01: domain contract / policy / deterministic serialization を固定する。
- S02: issue target resolution / source binding / store / schema validation を固定する。
- S03: `show` / `classify` / `verify` use case と text/json presentation を固定する。
- S04: public CLI surface を parser / registry / bootstrap へ接続する。
- S90: provider/mirror/docs impact を更新または no-op 証跡で閉じる。
- S99: final QA / code / spec review を通し、per-issue PR を Epic-level PR へ defer する。

## ステップ一覧

- S01 Domain Assurance Model, Policy, Deterministic Serialization
  - 対象: `domain/assurance.py`, `tests/unit/domain/test_assurance.py`
  - 閉じる要件: AC-002, AC-003, AC-006, EC-001, EC-001b, EC-002
  - reviewer: code-reviewer
- S02 Infra Assurance Store, Target Resolution, Source Binding, Schema Validation
  - 対象: `infra/assurance_store.py`, 必要時 `application/ports.py`, `tests/unit/infra/test_assurance_store.py`
  - 閉じる要件: AC-001, AC-004, AC-005, AC-006, EC-003, EC-004
  - reviewer: code-reviewer
- S03 Application Use Cases and Presentation Outputs
  - 対象: `application/assurance.py`, `application/contracts.py`, `presentation/assurance_text.py`, related unit tests
  - 閉じる要件: AC-001, AC-004, AC-005, AC-006
  - reviewer: code-reviewer
- S04 CLI Parser, Registry, Bootstrap Wiring and Runtime Tests
  - 対象: `commands/assurance.py`, `cli/parser.py`, `cli/registry.py`, `cli/bootstrap.py`, `tests/cli_runtime/test_assurance.py`
  - 閉じる要件: AC-001, AC-004, AC-005, AC-006
  - reviewer: code-reviewer
- S90 Docs / Mirror Impact Resolution
  - 対象: provider/mirror/docs/templates inspection or update
  - reviewer: spec-reviewer
- S99 Final Quality Gate
  - 対象: issue-wide evidence, final report, final reviewers
  - reviewers: qa-reviewer, issue-wide code-reviewer, spec-reviewer

## 要件 ↔ ステップ対応

- AC-001 -> S02, S03, S04
- AC-002 -> S01, S03
- AC-003 -> S01
- AC-004 -> S02, S03, S04
- AC-005 -> S02, S03, S04
- AC-006 -> S01, S02, S03, S04, S90, S99
- EC-001 / EC-001b / EC-002 -> S01
- EC-003 / EC-004 -> S02, S03, S04

## 仕様固定クロージャ索引（Spec-Locked Closure Index）

| ID | Step | Type | Spec link | Locked expectation | Observable input/state | Bug class guarded | Required | Evidence level | Closure evidence |
|---|---|---|---|---|---|---|---|---|---|
| `cl-ac001-classify-contract-write` | S02/S03/S04 | acceptance | AC-001 | `classify --stage requirement` writes valid v1 `assurance.json` | temp issue with requirement artifact | no machine-readable contract | yes | red-required | report Step/Test Closure and CLI result |
| `cl-ac002-deterministic-json` | S01 | invariant | AC-002 | same input serializes byte-identically and omits volatile timestamps | same facts/source binding/policy | timestamp/order churn | yes | red-required | domain deterministic test |
| `cl-ac003-lite-safety` | S01 | negative | AC-003/EC-001/EC-001b | unknown/false/missing opt-in keeps `lite_authorized=false` | policy matrix | unsafe Lite authorization | yes | red-required | domain matrix test |
| `cl-ec002-hard-trigger-monotonic` | S01 | negative | EC-002 | hard triggers escalate and cannot be overridden downward | hard-trigger facts | downscoped profile | yes | red-required | hard trigger matrix test |
| `cl-ac004-strict-legacy-missing` | S02/S03/S04 | compatibility | AC-004/EC-003 | missing contract returns strict-legacy view and show/verify exit 0 | issue without `assurance.json` | legacy issue blocked | yes | red-required | infra/app/CLI tests |
| `cl-ac005-invalid-contract` | S02/S03/S04 | negative | AC-005/EC-004 | invalid JSON/schema fails verify with reason | malformed / missing-field fixtures | corruption hidden as legacy | yes | red-required | schema + CLI tests |
| `cl-ac006-layer-boundary` | S01-S04 | architecture | AC-006 | domain imports no infra/CLI/presentation and policy is not duplicated | source imports / focused tests | layer leak | yes | inspect-only plus test | import inspection + review |
| `cl-dc008-target-resolution` | S02/S04 | acceptance/negative | design DC-008/DC-009 | explicit target wins; valid path accepted; escape/non-issue/missing rejected | active issue plus explicit targets | wrong issue / path escape | yes | red-required | infra + CLI target tests |
| `cl-dc010-default-facts` | S01/S03 | invariant | design DC-010 | public CLI emits every supported fact and default reason/consequence codes in stable order | no structured fact input | missing fail-closed audit facts | yes | red-required | domain/app fixture assertion |
| `cl-s90-provider-mirror-docs` | S90 | docs/mirror | design DC-001 | provider changes are mirrored or no-op justified; docs impact resolved | provider diff + mirror/docs inspection | shipped/mirror drift | yes | inspect-only | S90 report entry |
| `cl-s99-final-quality` | S99 | final gate | workflow_issue.md | QA/code/spec reviewers pass and per-issue PR is deferred to Epic PR | final diff/report/tests | final gate skips step gates | yes | manual-required plus review | final gate report entries |

## レビュー / QA ゲート方針

- S01-S04:
  - primary worker: `dev-coder`
  - step reviewer: `code-reviewer`
  - commit: one step = one review scope = one commit
- S90:
  - `doc-writer` を使うのは docs/templates/mirror text mutation が必要な場合だけ。
  - no-op の場合も inspected paths と rationale を `report.md` に記録し、`spec-reviewer` pass を取る。
- S99:
  - `qa-reviewer`: obligation coverage / integration test sufficiency
  - issue-wide `code-reviewer`: integrated diff / layering / regression risk
  - final `spec-reviewer`: requirement / design / plan / report / docs alignment
- User requested one Epic-level PR. This Issue must not create a per-issue PR; delivery evidence is deferred to the Epic-level PR after all Epic issues are complete.

## 実行ルール（全ステップ共通）

- 各 implementation step は 1 behavior slice / 1 review scope / 1 commit boundary。
- `plan.md` は planned contract、`report.md` は observed evidence ledger。
- Step 実行中に新しい requirement / bug class / external contract risk が出たら、report 記録だけで足りるか、plan amendment + fresh re-review が必要か判断する。
- Reviewer pass は fresh pass のみ有効。waiver / unavailable / provisional は pass ではない。

## 実装ステップ

### S01 Domain Assurance Model, Policy, Deterministic Serialization

- behavior goal:
  - pure domain logic can build and validate deterministic Assurance Contract v1 from supported risk facts.
- allowed paths:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/assurance.py`
  - `tests/unit/domain/test_assurance.py`
- forbidden changes:
  - infra / application / CLI / presentation / dogfooding mirror / docs / config / skill / GitHub state
- concrete tests:
  - `tc-s01-001` acceptance: deterministic default contract serialization
    - 前提: issue id、stage、policy version、resolved source binding を固定し、public CLI default と同じ supported facts を使う。
    - 操作: domain builder で contract を2回作成し、canonical JSON bytes に serialize する。
    - 期待結果: bytes が一致し、全 supported facts、default fact reason codes、policy consequence reason codes を stable order で含み、`generated_at` / `classified_at` を含まない。
    - 失敗検出: dict/list order、volatile timestamp、reason code 欠落、fact 欠落による非決定性を検出する。
    - 検証方法: `tests/unit/domain/test_assurance.py` red-first test。
    - 関連 closure id: `cl-ac002-deterministic-json`, `cl-dc010-default-facts`
  - `tc-s01-002` negative: Lite authorization safety
    - 前提: Lite predicate unknown case と all-positive-without-opt-in/evidence case を用意する。
    - 操作: domain policy で各 case を classify する。
    - 期待結果: `lite_authorized=false`、authorized profile は少なくとも `standard`。all-positive case は `lite_candidate=true` を許容する。
    - 失敗検出: unknown を safe と扱う、または all-positive predicate だけで Lite を authorize する回帰を検出する。
    - 検証方法: `tests/unit/domain/test_assurance.py` matrix test。
    - 関連 closure id: `cl-ac003-lite-safety`
  - `tc-s01-003` negative: hard trigger monotonic escalation
    - 前提: public contract、migration/persistence、rollback-high、security/privacy の hard trigger facts を個別・複合で用意する。
    - 操作: domain policy で各 fact set を classify する。
    - 期待結果: public/migration/rollback は少なくとも `strict`、security/privacy は `critical`、複合時は最高 profile が勝つ。
    - 失敗検出: lower profile override、profile/tier 混同、hard trigger reason 欠落を検出する。
    - 検証方法: `tests/unit/domain/test_assurance.py` hard-trigger matrix test。
    - 関連 closure id: `cl-ec002-hard-trigger-monotonic`
  - `tc-s01-004` inspect-only: domain import boundary
    - 前提: `domain/assurance.py` が追加される。
    - 操作: source import を inspect する、または import-boundary static assertion を実行する。
    - 期待結果: `infra`、`commands`、`cli`、`presentation`、GitHub adapter、filesystem-specific runtime module に依存しない。
    - 失敗検出: domain policy が runtime adapter へ依存する layering regression を検出する。
    - 検証方法: `tests/unit/domain/test_assurance.py` static assertion または report inspection evidence。
    - 関連 closure id: `cl-ac006-layer-boundary`
- green command:
  - `uv run pytest tests/unit/domain/test_assurance.py`
- report destination:
  - Session Log, TDD evidence, Step/Test Contract Closure, Closure Coverage, Delegated Worker Evidence, Reviewer Gate Status, Step Commit Gate.
- delegation contract:
  - delegated role: `dev-coder`
  - input docs: `requirement.md`, `design.md`, `plan.md`, `workflow_issue.md`, `phase_plan_issue.md`, `authoring/issue-plan.md`
  - acceptance criteria: `cl-ac002-deterministic-json`, `cl-ac003-lite-safety`, `cl-ec002-hard-trigger-monotonic`, `cl-ac006-layer-boundary`, `cl-dc010-default-facts`
  - required output: changed files, tests run, verification result, unresolved risks, report ledger note, material decision note or `No material implementation decisions beyond the approved plan.`
  - reviewer focus: pure domain boundary, deterministic serializer, profile/tier separation, Lite safety, hard trigger monotonicity, default fact / reason-code completeness
  - stop conditions: domain needs filesystem/CLI/GitHub access; policy table conflicts with design; deterministic bytes cannot be produced; implementation requires changing downstream layers
- Red / alternative evidence requirement:
  - red-required: add failing domain tests for deterministic default serialization, Lite safety, hard-trigger escalation, and default facts before implementation.
  - inspect-only: import-boundary check may be implemented as a static assertion or documented inspection before reviewer gate.
- Refactor / cleanup guardrail:
  - Keep cleanup inside `domain/assurance.py` and its tests. Do not introduce generic policy framework or shared serializer abstraction unless needed by the S01 contract.
- step closure contract:
  - close condition: all S01 closure IDs pass, `uv run pytest tests/unit/domain/test_assurance.py` passes, fresh `code-reviewer` passes, report evidence is updated.
  - commit gate: commit only S01 files and report evidence after reviewer pass and post-commit clean check.
- amendment trigger:
  - need for filesystem/CLI access in domain, new profile semantics, or non-deterministic serializer requirement.

### S02 Infra Assurance Store, Target Resolution, Source Binding, Schema Validation

- behavior goal:
  - runtime can resolve an issue target, read/write/verify issue-local `assurance.json`, bind requirement source hash, and distinguish missing strict-legacy from invalid data.
- allowed paths:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/assurance_store.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/ports.py` only if a typed port is required
  - `tests/unit/infra/test_assurance_store.py`
- forbidden changes:
  - parser / registry / bootstrap wiring, policy decisions outside domain, mirror/docs/config/skill/GitHub state
- concrete tests:
  - `tc-s02-001` acceptance: durable source binding
    - 前提: temp repo に active issue と issue-local `requirement.md` があり、`spec-dock/active/issue` がその issue を指す。
    - 操作: assurance store が source binding を作成する。
    - 期待結果: persisted `path` は resolved repo-relative issue-local path、`display_path` は optional active path、`sha256` は requirement content の lowercase 64-hex。
    - 失敗検出: mutable active path だけを永続化する、hash が不安定、absolute path を保存する回帰を検出する。
    - 検証方法: `tests/unit/infra/test_assurance_store.py`。
    - 関連 closure id: `cl-ac001-classify-contract-write`
  - `tc-s02-002` compatibility: strict-legacy missing
    - 前提: target issue dir は存在するが `assurance.json` がない。
    - 操作: store read/verify を実行する。
    - 期待結果: missing / strict-legacy result になり、invalid JSON/schema とは区別される。
    - 失敗検出: missing file を corrupt contract と扱う、または例外で既存 Issue を止める回帰を検出する。
    - 検証方法: `tests/unit/infra/test_assurance_store.py`。
    - 関連 closure id: `cl-ac004-strict-legacy-missing`
  - `tc-s02-003` negative: invalid JSON and schema distinction
    - 前提: malformed JSON fixture と required field 欠落 / unsupported enum の schema-invalid fixture を用意する。
    - 操作: store verify/read を実行する。
    - 期待結果: どちらも failure だが、parse failure と schema invalid の machine-readable reason が区別される。
    - 失敗検出: invalid data を valid/missing と扱う、または failure reason を潰す回帰を検出する。
    - 検証方法: `tests/unit/infra/test_assurance_store.py`。
    - 関連 closure id: `cl-ac005-invalid-contract`
  - `tc-s02-004` negative: explicit path target safety
    - 前提: valid issue dir、non-issue dir、missing path、repo外 escape path、可能なら symlink escape candidate を用意する。
    - 操作: explicit `--issue` path 相当の target resolution を実行する。
    - 期待結果: repo-contained issue path だけが受理され、escape / non-issue / missing / ambiguous symlink は exit-failure 相当になる。
    - 失敗検出: arbitrary path classify、explicit failure 後の active fallback、symlink escape を検出する。
    - 検証方法: `tests/unit/infra/test_assurance_store.py`。
    - 関連 closure id: `cl-dc008-target-resolution`
- green command:
  - `uv run pytest tests/unit/infra/test_assurance_store.py`
- report destination:
  - Same ledgers as S01 plus target-resolution risk notes if any.
- delegation contract:
  - delegated role: `dev-coder`
  - input docs: S01 committed contract, `requirement.md`, `design.md`, `plan.md`, existing `infra/json_store.py`, active/target resolution patterns
  - acceptance criteria: `cl-ac001-classify-contract-write`, `cl-ac004-strict-legacy-missing`, `cl-ac005-invalid-contract`, `cl-dc008-target-resolution`, `cl-ac006-layer-boundary`
  - required output: changed files, tests run, verification result, target/path safety notes, unresolved risks, report ledger note
  - reviewer focus: path containment, symlink/escape behavior, missing vs invalid distinction, schema strictness, source binding durability, no policy duplication
  - stop conditions: target resolution needs broad architecture refactor; path behavior conflicts with design; schema validator needs domain semantic changes; deterministic persistence cannot be preserved
- Red / alternative evidence requirement:
  - red-required: add failing infra tests for source binding, missing strict-legacy, invalid JSON/schema, and explicit path target safety before implementation.
- Refactor / cleanup guardrail:
  - Keep helper extraction local to `infra/assurance_store.py` unless existing target-resolution helpers are reused. Do not refactor unrelated active/deps/new command target code.
- step closure contract:
  - close condition: all S02 closure IDs pass, `uv run pytest tests/unit/infra/test_assurance_store.py` passes, relevant S01 tests remain green if touched, fresh `code-reviewer` passes, report evidence is updated.
  - commit gate: commit only S02 files and report evidence after reviewer pass and post-commit clean check.
- amendment trigger:
  - existing target helpers require broad refactor or path semantics conflict with design.

### S03 Application Use Cases and Presentation Outputs

- behavior goal:
  - `show`, `classify`, and `verify` have stable request/result contracts and renderable text/json outcomes independent of argparse.
- allowed paths:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/assurance.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/assurance_text.py`
  - `tests/unit/application/test_assurance.py`
  - `tests/unit/presentation/test_assurance_text.py`
- forbidden changes:
  - argparse/parser/registry/bootstrap wiring, infra redesign, policy inference in presentation, docs/mirror/config/skill/GitHub state
- concrete tests:
  - `tc-s03-001` acceptance: classify write and dry-run
    - 前提: valid issue target と S01/S02 の deterministic default contract / store fake を用意する。
    - 操作: `ClassifyAssuranceRequest(stage="requirement", dry_run=false)` と `dry_run=true` を実行する。
    - 期待結果: non-dry-run は `assurance.json` を write し、dry-run は同じ canonical contract を返すが write しない。
    - 失敗検出: dry-run mutation、returned/persisted JSON mismatch、stage/policy/source binding 欠落を検出する。
    - 検証方法: `tests/unit/application/test_assurance.py`。
    - 関連 closure id: `cl-ac001-classify-contract-write`, `cl-ac002-deterministic-json`
  - `tc-s03-002` compatibility/negative: show and verify result mapping
    - 前提: valid contract、missing strict-legacy、invalid JSON、invalid schema の store outcomes を用意する。
    - 操作: application `show` / `verify` use cases を実行する。
    - 期待結果: valid/missing は success result、invalid JSON/schema は failure result になり、reason が区別される。
    - 失敗検出: invalid を strict-legacy と表示する、missing を failure にする、reason を失う回帰を検出する。
    - 検証方法: `tests/unit/application/test_assurance.py`。
    - 関連 closure id: `cl-ac004-strict-legacy-missing`, `cl-ac005-invalid-contract`
  - `tc-s03-003` presentation: stable text/json rendering
    - 前提: valid adaptive result、strict-legacy missing result、invalid result の representative objects を用意する。
    - 操作: text/json renderer を実行する。
    - 期待結果: JSON は stable keys を持ち、text は mode/profile/tier/reason を表示し、presentation は policy を再計算しない。
    - 失敗検出: renderer が classification semantics を作る、strict-legacy/invalid reason を落とす、field order が不安定な回帰を検出する。
    - 検証方法: `tests/unit/presentation/test_assurance_text.py`。
    - 関連 closure id: `cl-ac004-strict-legacy-missing`, `cl-ac005-invalid-contract`, `cl-ac006-layer-boundary`
- green command:
  - `uv run pytest tests/unit/application/test_assurance.py tests/unit/presentation/test_assurance_text.py`
- report destination:
  - Session Log, TDD evidence, Step/Test Contract Closure, Closure Coverage, Delegated Worker Evidence, Reviewer Gate Status, Step Commit Gate.
- delegation contract:
  - delegated role: `dev-coder`
  - input docs: S01/S02 committed contracts, `requirement.md`, `design.md`, `plan.md`, existing `application/contracts.py`, presentation rendering patterns
  - acceptance criteria: `cl-ac001-classify-contract-write`, `cl-ac004-strict-legacy-missing`, `cl-ac005-invalid-contract`, `cl-ac006-layer-boundary`, `cl-dc010-default-facts`
  - required output: changed files, application/presentation test results, result-model risks, unresolved risks, report ledger note
  - reviewer focus: orchestration only in application, presentation renders without recomputing policy, result dataclasses are stable, exit behavior is ready for CLI layer
  - stop conditions: use case needs new exit semantics; presentation must infer policy; app result model conflicts with schema or store outcome
- Red / alternative evidence requirement:
  - red-required: add failing application tests for classify dry-run/write and show/verify result mapping; add failing presentation tests for valid, strict-legacy, and invalid output.
- Refactor / cleanup guardrail:
  - Keep changes within assurance use cases/results/rendering. Do not alter existing command dispatch, bootstrap, or unrelated presentation helpers beyond minimal reuse.
- step closure contract:
  - close condition: all S03 closure IDs pass, S03 focused tests pass, relevant S01/S02 tests remain green if touched, fresh `code-reviewer` passes, report evidence is updated.
  - commit gate: commit only S03 files and report evidence after reviewer pass and post-commit clean check.
- amendment trigger:
  - use case needs new exit semantics or presentation must infer policy.

### S04 CLI Parser, Registry, Bootstrap Wiring and Runtime Tests

- behavior goal:
  - users can execute `spec-dock assurance show|classify|verify` with active/default or explicit target and text/json formats.
- allowed paths:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/assurance.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/__init__.py` if required by local import style
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/parser.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/registry.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/bootstrap.py`
  - `tests/cli_runtime/test_assurance.py`
- forbidden changes:
  - domain policy changes, broad command registry refactor, docs/mirror changes, GitHub/network behavior
- concrete tests:
  - `tc-s04-001` acceptance: CLI classify writes contract
    - 前提: CLI runtime temp repo に active issue と `requirement.md` があり、`assurance.json` はない。
    - 操作: `spec-dock assurance classify --stage requirement --format json` を実行する。
    - 期待結果: exit 0、stdout JSON が adaptive standard/default classification を返し、issue-local `assurance.json` が同じ deterministic fields で作成される。
    - 失敗検出: command 未登録、write 不実行、stdout/persisted mismatch、non-deterministic output を検出する。
    - 検証方法: `tests/cli_runtime/test_assurance.py`。
    - 関連 closure id: `cl-ac001-classify-contract-write`, `cl-ac002-deterministic-json`
  - `tc-s04-002` compatibility: CLI show/verify strict-legacy
    - 前提: temp repo issue に `assurance.json` がない。
    - 操作: `spec-dock assurance show --format json` と `spec-dock assurance verify --format json` を実行する。
    - 期待結果: exit 0、JSON が `mode: strict-legacy` と `has_contract: false` 相当を示す。
    - 失敗検出: missing contract を error にする、または invalid と混同する回帰を検出する。
    - 検証方法: `tests/cli_runtime/test_assurance.py`。
    - 関連 closure id: `cl-ac004-strict-legacy-missing`
  - `tc-s04-003` negative: CLI verify invalid contract
    - 前提: temp repo issue に malformed JSON または schema-invalid `assurance.json` を置く。
    - 操作: `spec-dock assurance verify --format json` を実行する。
    - 期待結果: exit 1、machine-readable invalid reason を stdout/stderr contract に従って返す。
    - 失敗検出: corrupted contract を success / strict-legacy と扱う、reason を落とす回帰を検出する。
    - 検証方法: `tests/cli_runtime/test_assurance.py`。
    - 関連 closure id: `cl-ac005-invalid-contract`
  - `tc-s04-004` target resolution: explicit target precedence
    - 前提: temp repo に active issue A と explicit issue B があり、B は id / GitHub number / repo-contained path で指定可能。
    - 操作: `--issue <B>` 付きで classify/show を実行する。
    - 期待結果: B が対象になり、A の `assurance.json` は作成・変更されない。
    - 失敗検出: explicit target を無視して active issue を使う、または path target を拒否する回帰を検出する。
    - 検証方法: `tests/cli_runtime/test_assurance.py`。
    - 関連 closure id: `cl-dc008-target-resolution`
- green command:
  - `uv run pytest tests/cli_runtime/test_assurance.py`
  - If parser/bootstrap risk is broad: `uv run pytest tests/cli_runtime`
- report destination:
  - Session Log, TDD evidence, Step/Test Contract Closure, Closure Coverage, Delegated Worker Evidence, Reviewer Gate Status, Step Commit Gate, command output snippets proving exit behavior.
- delegation contract:
  - delegated role: `dev-coder`
  - input docs: S01-S03 committed contracts, `requirement.md`, `design.md`, `plan.md`, existing `commands/*`, `cli/parser.py`, `cli/registry.py`, `cli/bootstrap.py`
  - acceptance criteria: `cl-ac001-classify-contract-write`, `cl-ac004-strict-legacy-missing`, `cl-ac005-invalid-contract`, `cl-dc008-target-resolution`, `cl-ac006-layer-boundary`
  - required output: changed files, CLI test results, parser/registry compatibility notes, unresolved risks, report ledger note
  - reviewer focus: argparse shape, command key registration, bootstrap wiring, exit codes, explicit target precedence, no regression to existing commands
  - stop conditions: parser requires broad refactor; CLI behavior needs new requirement/design decision; tests need live network; command wiring forces policy duplication
- Red / alternative evidence requirement:
  - red-required: add failing CLI runtime tests for classify write, strict-legacy show/verify, invalid verify failure, and explicit target precedence before wiring command implementation.
- Refactor / cleanup guardrail:
  - Keep parser/registry changes additive. Do not rewrite command dispatch, registry design, or existing command APIs.
- step closure contract:
  - close condition: all S04 closure IDs pass, `uv run pytest tests/cli_runtime/test_assurance.py` passes, broader `tests/cli_runtime` runs if parser/bootstrap risk warrants, fresh `code-reviewer` passes, report evidence is updated.
  - commit gate: commit only S04 files and report evidence after reviewer pass and post-commit clean check.
- amendment trigger:
  - parser cannot express the subcommands cleanly without broad refactor.

### S90 Docs / Mirror Impact Resolution

- behavior goal:
  - provider implementation remains authority; dogfooding mirror impact is resolved; docs/template impact is updated or explicitly no-op.
- inspect/update surfaces:
  - `spec-dock/scripts/spec_dock_runtime/`
  - `src/spec_dock/assets/spec_dock/docs/`
  - `src/spec_dock/assets/spec_dock/templates/`
  - `spec-dock/docs/`
- verification:
  - changed docs/templates/mirror: targeted inspection and `./spec-dock/scripts/spec-dock validate` if spec tree changed.
  - no-op: inspected paths and rationale in `report.md`, then `spec-reviewer` pass.
- delegation contract:
  - delegated role: `doc-writer` when docs/templates/mirror text mutation is required; otherwise no implementation worker and main orchestrator records inspect-only no-op evidence.
  - input docs: final S01-S04 diff, provider/mirror authority rules, public CLI surface, current docs/templates/mirror paths.
  - acceptance criteria: `cl-s90-provider-mirror-docs`
  - required output: changed files or inspected no-op paths, verification result, docs/mirror impact disposition, unresolved docs risks.
  - stop conditions: docs change would alter requirement/design scope; mirror sync creates unrelated churn; implementation correction is needed in S01-S04.
- step closure contract:
  - close condition: S90 impact is committed or approved-no-op, `spec-reviewer` passes docs/spec alignment, report records inspected paths and rationale.
  - commit gate: commit docs/mirror changes only after spec-reviewer pass; no-op requires diff-clean command and read-only evidence in report.
- reviewer:
  - `spec-reviewer`

### S99 Final Quality Gate

- prerequisites:
  - S01-S04 committed with step tests, fresh `code-reviewer` pass, report closure evidence, and post-commit clean check.
  - S90 committed or approved-no-op with `spec-reviewer` pass.
- required validation candidates:
  - `uv run pytest tests/unit/domain/test_assurance.py`
  - `uv run pytest tests/unit/infra/test_assurance_store.py`
  - `uv run pytest tests/unit/application/test_assurance.py`
  - `uv run pytest tests/unit/presentation/test_assurance_text.py`
  - `uv run pytest tests/cli_runtime/test_assurance.py`
  - broader `uv run pytest tests/unit`, `uv run pytest tests/cli_runtime`, and `make lint` when touched surfaces warrant.
- final reviewers:
  - `qa-reviewer`
  - issue-wide `code-reviewer`
  - final `spec-reviewer`
- delegation contract:
  - delegated roles: `qa-reviewer`, issue-wide `code-reviewer`, final `spec-reviewer`
  - input docs: final requirement/design/plan/report, issue diff, all step test outputs, S90 disposition, closure ledger.
  - acceptance criteria: `cl-s99-final-quality`
  - required output: final reviewer verdicts, unresolved risks or none, final report ledger status, Epic-level PR deferral evidence.
  - stop conditions: any final reviewer fails/unavailable/denied without explicit blocking classification; missing closure evidence; uncommitted step diff; unresolved docs impact; per-issue PR attempted.
- final closure contract:
  - close condition: all final reviewers pass, all required closure IDs are pass/approved-no-op, final report records per-issue PR deferral to Epic-level PR.
  - final commit gate: final commit may contain only final report/delivery evidence and must not bundle uncommitted implementation from prior steps.
- delivery:
  - no per-issue PR; record that PR delivery is deferred to the user-requested Epic-level PR.

## 未確定事項

- なし。

## 最終完了条件

- Fresh `spec-reviewer` has passed this canonical `plan.md`.
- Every required closure ID is pass / approved-no-op in `report.md`.
- S01-S04 are each committed after step tests and fresh `code-reviewer` pass.
- S90 docs/mirror impact is committed or approved-no-op after `spec-reviewer` pass.
- S99 `qa-reviewer`, issue-wide `code-reviewer`, and final `spec-reviewer` pass.
- `make lint` and required focused tests are recorded in `report.md`.
- No per-issue PR is created; Epic-level PR delivery remains the final delivery path.
