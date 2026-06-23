---
created_by_role: system-architect
scope_id: iss-00227
source_paths:
  - spec-dock/active/context-pack.md
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/epic/requirement.md
  - spec-dock/active/epic/design.md
  - spec-dock/active/epic/plan.md
  - spec-dock/active/issue/discussions/20260623t033541z-draft-requirement-draft-requirement.md
  - spec-dock/active/issue/discussions/20260623t033545z-draft-design-draft-design.md
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/
  - tests/
intended_targets:
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/plan.md
adoption_status: unreviewed
reflected_to: []
diff_guard_result: not_run
---

# iss-00227 System Architect Design Draft

This is delegated architecture evidence for the main orchestrator. It is not an accepted design, does not edit canonical artifacts, and does not authorize implementation.

## 1. Requirement Coverage

- Source requirement revision: `iss-00227` requirement front matter has `状態: "approved"` and `最終更新: "2026-06-23"`.
- In scope:
  - Issue-local tracked `assurance.json`.
  - Assurance Profile values: `lite`, `standard`, `strict`, `critical`.
  - Complexity Tier values: `routine`, `normal`, `complex`, `deep`.
  - Deterministic classification from risk facts, hard triggers, and policy version.
  - Separation of `lite_candidate` and `lite_authorized`.
  - CLI surface: `assurance show`, `assurance classify`, `assurance verify`.
  - Strict-legacy detection when an existing Issue has no `assurance.json`.
- Explicit non-goals for this Issue:
  - Runbook compiler.
  - Artifact composition.
  - Context packet or agent context routing.
  - GitHub review trigger.
  - PR blocker policy implementation.
  - Skill kernel switching or profile-specific `.agents/skills/**` replacement.

## 2. Existing Context Findings

- The runtime already follows a layered structure under `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/`:
  - `cli/` builds the parser and command registry.
  - `commands/` owns typed CLI args and invokes use cases through `CommandSpec`.
  - `application/` owns use-case contracts and orchestration.
  - `domain/` owns pure rules and models.
  - `infra/` owns filesystem, active state, JSON, Git/GitHub, and persistence adapters.
  - `presentation/` renders CLI text, JSON-oriented state, Markdown, and PUML.
- Command addition pattern:
  - Add a command module under `commands/`.
  - Export `command_specs()`.
  - Register specs in `cli/registry.py`.
  - Add parser shape in `cli/parser.py`, binding leaf subcommands to registry keys.
- Store patterns to reuse:
  - `infra/json_store.py` provides UTF-8 JSON read/write and standard parse/read failures.
  - `infra/fs_repo.py` demonstrates atomic write behavior for managed JSON and tree metadata.
  - `application/ports.py` exposes store abstractions via `Protocol` and `Ports`.
- Tests are split by surface:
  - Domain rules in `tests/unit/domain/`.
  - Application orchestration in `tests/unit/application/`.
  - Infra store behavior in `tests/unit/infra/`.
  - Presentation output in `tests/unit/presentation/`.
  - Runtime CLI flows in `tests/cli_runtime/`.

## 3. Design Decisions

- Put classification policy in a pure domain module. It should accept structured facts and return a structured decision without reading files, active state, GitHub, or CLI args.
- Keep `assurance.json` as the tracked Issue-local authority. Generated projections or future Runbooks must read it later, but are out of scope here.
- Use `standard` as the authoritative default for new adaptive classification unless hard triggers escalate it.
- Treat `lite_candidate` as measurement-only and never as execution authority.
- Treat `lite_authorized` as false in this Issue unless explicit opt-in and evidence gate fields are present and valid. The initial policy must not reduce obligations from an all-positive predicate alone.
- Represent missing contracts as a separate strict-legacy mode, not as invalid JSON.
- Use deterministic JSON serialization for persisted contract output. Implementation should define stable field order and stable list ordering for reason codes, facts, and bindings.

## 4. Alternatives Considered

- Single monolithic `commands/assurance.py` with embedded policy:
  - Rejected because it would bypass the existing layered runtime architecture and make deterministic policy tests harder.
- Store only derived profile strings in `.meta.json`:
  - Rejected because the requirement calls for tracked Issue-local `assurance.json` with source binding, policy version, stage, reason codes, and Lite candidate/authorization separation.
- Authorize Lite whenever all predicates are true:
  - Rejected by requirement. All-positive predicate may create `lite_candidate=true`, but cannot make `lite_authorized=true` without opt-in and evidence gate.
- Treat missing `assurance.json` as invalid:
  - Rejected because existing Issues must continue through strict-legacy compatibility.

## 5. Boundary / Contract Model

- Domain boundary:
  - Owns `AssuranceProfile`, `ComplexityTier`, `ClassificationStage`, `RiskFact`, `SourceBinding`, `AssuranceContract`, `ClassificationDecision`, and validation result concepts.
  - No filesystem, GitHub, CLI parser, active symlink, or presentation imports.
- Application boundary:
  - Resolves active or explicit Issue target.
  - Reads canonical requirement source and existing contract through ports.
  - Calls domain policy.
  - Writes or verifies `assurance.json`.
  - Returns structured result objects for presentation.
- Infra boundary:
  - Locates issue directory.
  - Reads/writes `assurance.json`.
  - Differentiates missing, invalid JSON, and invalid schema.
  - Computes source binding hashes for canonical input files.
- Command boundary:
  - Defines `assurance show`, `assurance classify`, `assurance verify` CLI args and exit behavior.
- Presentation boundary:
  - Produces stable text and JSON output without reclassifying.

## 6. Dependency Analysis

- New command depends on application use cases only.
- Application depends on domain policy and infra ports.
- Infra may serialize/deserialize domain contract shapes, but must not decide risk policy.
- Domain must not import application, infra, commands, or presentation.
- Implementation order should start with the domain contract and policy matrix, then store/ports, then application use cases, then CLI/presentation, then provider/mirror and runtime tests.
- Downstream dependency:
  - `iss-00228` can read `authorized_profile`, `lite_candidate`, `lite_authorized`, `mode`, `status`, and `source_binding`.
  - `iss-00229` can extend source binding and approval/stale behavior.
  - `iss-00230+` can later add step/context fields without changing the minimum contract semantics from this Issue.

## 7. Source of Record

- Provider source of truth:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/`
  - `src/spec_dock/assets/spec_dock/system/assurance/` if schema/policy static assets are introduced.
- Dogfooding mirror / installed runtime inspection target:
  - `spec-dock/scripts/spec_dock_runtime/`
  - `spec-dock/system/assurance/`
- Canonical Issue contract location:
  - `<issue-dir>/assurance.json`
- Discussion draft location:
  - This file only.

## 8. Data Flow / Domain Model / Interface Contract

### Data Flow

```text
CLI args
  -> command typed args
  -> application use case
  -> target issue resolver / active issue store
  -> source binding reader
  -> domain risk fact extraction and policy classification
  -> assurance store read/write/verify
  -> presentation text or JSON
```

Risk fact extraction should be minimal for this Issue: enough to produce deterministic reason codes and hard trigger decisions from canonical requirement/design text or explicit fixtures. Later Issues can enrich facts, but must preserve the profile safety rules.

### Domain Model

- `AssuranceProfile`: ordered profile enum `lite < standard < strict < critical`.
- `ComplexityTier`: ordered tier enum `routine < normal < complex < deep`.
- `ClassificationStage`: at least `requirement`; reserve `design` for later approval paths without implementing artifact composition.
- `RiskFact`: stable key, tri-state value (`true`, `false`, `unknown`), source, and optional reason code.
- `HardTrigger`: risk code that escalates profile to `strict` or `critical` and cannot be overridden downward.
- `LiteEligibility`: all required predicates plus explicit opt-in and evidence gate result.
- `AssuranceContract`: persisted JSON contract and source binding.

### `assurance.json` Contract Outline

```json
{
  "schema_version": 1,
  "policy_version": "assurance-policy-v1",
  "issue_id": "iss-00227",
  "stage": "requirement",
  "status": "provisional",
  "mode": "adaptive",
  "generated_at": "2026-06-23T00:00:00Z",
  "source_binding": {
    "artifacts": [
      {
        "path": "spec-dock/active/issue/requirement.md",
        "sha256": "...",
        "role": "requirement"
      }
    ]
  },
  "classification": {
    "authorized_profile": "standard",
    "proposed_profile": "standard",
    "complexity_tier": "normal",
    "lite_candidate": false,
    "lite_authorized": false,
    "reason_codes": [
      "standard_default"
    ],
    "hard_triggers": [],
    "unknown_facts": []
  },
  "risk_facts": [
    {
      "key": "public_contract_change",
      "value": "unknown",
      "source": "requirement",
      "reason_code": "fact_unknown_public_contract_change"
    }
  ],
  "obligations": {
    "profile_preset": "standard",
    "notes": []
  }
}
```

Strict-legacy display should be a view result, not necessarily a persisted file:

```json
{
  "mode": "strict-legacy",
  "has_contract": false,
  "authorized_profile": "strict",
  "lite_candidate": false,
  "lite_authorized": false,
  "reason_codes": ["missing_assurance_contract_strict_legacy"]
}
```

### CLI Interface Contract

- `spec-dock assurance show [--issue <target>] [--format text|json]`
  - Shows existing contract.
  - If missing, returns strict-legacy view with success exit code unless `--require-contract` is later introduced.
  - Must distinguish missing contract from invalid JSON/schema.
- `spec-dock assurance classify --stage requirement [--issue <target>] [--format text|json] [--dry-run]`
  - Computes deterministic classification from current canonical input.
  - Writes `assurance.json` unless `--dry-run`.
  - Returns contract JSON or text summary.
  - Later stages may be added, but this Issue should not implement design approval or artifact composition.
- `spec-dock assurance verify [--issue <target>] [--format text|json]`
  - Valid contract: exit 0.
  - Missing contract: strict-legacy candidate, exit 0 or a non-fatal status agreed by implementation; the key point is not to break existing Issues.
  - Invalid JSON/schema: exit non-zero with machine-readable reason.

## 9. File / Module Change Plan

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/
|-- domain/
|   `-- assurance.py              # Add: enums, contract dataclasses, policy, validation helpers.
|-- application/
|   `-- assurance.py              # Add: show/classify/verify use cases and result contracts.
|-- infra/
|   `-- assurance_store.py        # Add: issue-local assurance.json read/write/verify, source binding hashes.
|-- commands/
|   `-- assurance.py              # Add: CommandSpec entries for assurance subcommands.
|-- cli/
|   |-- parser.py                 # Change: add assurance subparser and bind assurance_* keys.
|   `-- registry.py               # Change: register assurance command specs.
`-- presentation/
    `-- assurance_text.py         # Add: text/JSON rendering helpers or delegate JSON through CliText.

src/spec_dock/assets/spec_dock/system/
`-- assurance/
    |-- assurance.schema.json      # Optional: static schema if implementation chooses data-file validation.
    `-- policy-v1.json             # Optional: static policy table if domain should not hard-code tables.

spec-dock/scripts/spec_dock_runtime/
`-- ...                            # Dogfooding mirror after provider update/sync, not hand-edited first.

spec-dock/system/assurance/
`-- ...                            # Dogfooding mirror if provider introduces static assurance assets.

tests/
|-- unit/domain/test_assurance.py
|-- unit/application/test_assurance.py
|-- unit/infra/test_assurance_store.py
|-- unit/presentation/test_assurance_text.py
`-- cli_runtime/test_assurance.py
```

## 10. Migration / Compatibility / Rollback

- Existing Issues without `assurance.json` remain valid strict-legacy candidates.
- New adaptive Issues can opt into classification by running `assurance classify`.
- Rollback should be simple:
  - Removing or ignoring the new CLI leaves existing strict workflow intact.
  - Existing `assurance.json` files are tracked artifacts but should not be required by legacy commands until downstream rollout Issues make that policy explicit.
- Schema evolution should use `schema_version` and `policy_version` so later Issues can add fields without changing the v1 safety semantics.
- Profile downgrade must not be automatic. Reclassification may propose a lower profile later, but this Issue should preserve monotonic hard-trigger escalation and record reason codes.

## 11. Observability

- CLI JSON output is the primary observability surface for this Issue.
- Contract fields should expose:
  - `policy_version`
  - `schema_version`
  - `stage`
  - `mode`
  - `status`
  - `authorized_profile`
  - `complexity_tier`
  - `lite_candidate`
  - `lite_authorized`
  - `reason_codes`
  - `hard_triggers`
  - `unknown_facts`
  - `source_binding.artifacts`
- Do not record private reasoning, secrets, raw external credentials, or child-agent transcripts.
- Later metrics/event stores are out of scope for this Issue.

## 12. Test Strategy

- Domain tests:
  - Standard default when no hard trigger or Lite authorization exists.
  - Lite predicate true/false/unknown matrix.
  - All-positive Lite predicate without opt-in/evidence keeps `lite_authorized=false`.
  - Hard trigger monotonic escalation to `strict` or `critical`.
  - Unknown facts fail closed for Lite.
  - Deterministic serialization order and byte-identical output for same input.
- Infra tests:
  - Missing contract -> strict-legacy view result.
  - Invalid JSON -> parse/schema error distinct from missing.
  - Valid JSON fixture -> contract object.
  - Atomic or safe write behavior for `assurance.json`.
  - Source binding hash stability.
- Application tests:
  - Active Issue target resolution.
  - Explicit Issue target resolution.
  - Classify writes or dry-runs expected contract.
  - Verify maps missing/invalid/valid to correct result.
- CLI runtime tests:
  - `assurance show` for missing contract.
  - `assurance classify --stage requirement --format json`.
  - `assurance verify` valid and invalid fixtures.
  - Provider/mirror parity if shipped assets are added.
- Static checks:
  - Focused `uv run pytest tests/unit/domain/test_assurance.py tests/unit/application/test_assurance.py tests/unit/infra/test_assurance_store.py tests/cli_runtime/test_assurance.py`.
  - Broader `uv run pytest tests/unit tests/cli_runtime` when command registry/parser changes are complete.

## 13. ADR Candidates

- Whether `assurance.json` v1 stores policy tables inline, references tracked `system/assurance/policy-v1.json`, or only stores `policy_version`.
- Whether `verify` missing-contract strict-legacy returns exit 0 with warning or a distinct non-zero non-schema status. Requirement emphasizes compatibility, so exit 0 is the safer default unless reviewers require stricter automation.
- Whether `generated_at` belongs in a byte-identical deterministic file. If byte-identical JSON is strict, use stable `classified_at` only when caller supplies a clock fixture or omit volatile timestamps from persisted deterministic output.

## 14. Risks

- Volatile timestamps can violate byte-identical deterministic output.
- Weak source binding can make later stale detection unreliable.
- If unknown facts are normalized as false instead of unknown, Lite could be authorized unsafely.
- If missing contract and invalid schema share the same error path, legacy compatibility and corruption detection will be ambiguous.
- Parser or registry changes can break existing commands if the assurance subparser is wired too broadly.
- Hand-editing dogfooding mirror before provider source would violate repository authority rules.

## 15. Requirement Clarification Requests

- None blocking.
- Review point: decide whether `verify` for strict-legacy missing contract exits `0` with warning or a distinct non-zero compatibility code. My recommendation is exit `0` plus explicit `mode=strict-legacy` for compatibility.
- Review point: decide whether persisted v1 JSON may include `generated_at`. My recommendation is to omit volatile timestamps from the deterministic persisted representation, or make them caller-supplied and fixture-controlled.

## 16. Integration Notes for Main Orchestrator

- This draft should be mined into canonical `design.md` and `plan.md` only after main-orchestrator review.
- Keep canonical scope narrow: Assurance Contract, deterministic classification, strict-legacy detection, and `assurance` CLI only.
- Do not import Runbook compiler, artifact composition, context routing, GitHub review trigger, or blocker policy details into `iss-00227` implementation steps.
- Implementation plan should begin with domain policy and serialization tests before CLI wiring.
- Dogfooding mirror should be refreshed or inspected after provider-side source changes, not used as the first implementation target.
- A fresh `spec-reviewer` pass remains required after canonical adoption.

No canonical edit, final authority, promotion, reviewer-pass, or user-dialogue ownership is claimed.
