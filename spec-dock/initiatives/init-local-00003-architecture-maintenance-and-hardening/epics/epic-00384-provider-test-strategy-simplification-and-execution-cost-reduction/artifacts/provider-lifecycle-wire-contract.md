---
種別: Normative Artifact
ID: "provider-lifecycle-wire-contract-v1"
タイトル: "Provider Lifecycle Wire Contract"
状態: "accepted"
最終更新: "2026-09-01"
対象: ["epic-00384", "iss-00392"]
repository_evidence:
  repository: "chemitaro/spec-dock"
  branch: "codex/epic-00384-provider-test-strategy-planning"
  sha: "ef183ae46febe52f0152431cb3a8b4846c9972fc"
---

# Provider Lifecycle Wire Contract

## 1. Authority and compatibility

本Artifactは、final `0.2.4` provider lifecycleのdurable record、observed states、operation wire values、resume relation、typed service result、public uninstall JSON/text/exitをexactに固定する。Epic/Issue R/D/P、accepted ADR、Luna handoffは本Artifactをnormative traceとして参照する。

Field、enum、nullability、relation、goldenを変更する場合はcanonical specification更新とStrict re-reviewが必要である。Implementationでunknown field、fallback code、catch-all enumを追加しない。

## 2. Durable installation record

Path: `spec-dock/spec-dock.version`。

Encoding: UTF-8、JSON object、sorted keys、2-space indent、terminal LF。Maximum 4096 bytes。Regular file、link count 1。Duplicate JSON key、unknown key、missing key、non-canonical scalarをrejectする。

### WIR-REC-001 — Exact seven keys

| Field | JSON type | Nullable | Enum / constraint | Relation |
|---|---|---:|---|---|
| `schema_version` | integer | no | exact `1`; boolean forbidden | all states |
| `state` | string | no | `incomplete`, `ready`, `tooling-absent-preserved-data` | observed-only states are never serialized |
| `operation` | string or null | yes | incomplete: `install`, `update`, `migrate-0.2.3`, `uninstall`; terminal: null | resume identity member while incomplete |
| `version` | string | no | exact `0.2.4` | package/final format version |
| `candidate_digest` | string | no | lowercase `[0-9a-f]{64}` | candidate governing the operation or last removed tooling |
| `seed_policy` | string | no | `create-if-absent`, `preserve-only` | immutable for one operation; resume identity member |
| `skill_slots` | object | no | exact two keys, each exact string `0.2.4` | additional/missing key rejected |

`skill_slots` exact object:

```json
{
  "spec-dock": "0.2.4",
  "spec-dock-grill-with-docs": "0.2.4"
}
```

### WIR-REC-002 — Durable state matrix

| Durable state | `operation` | `seed_policy` | `candidate_digest` | `skill_slots` | Required filesystem relation |
|---|---|---|---|---|---|
| incomplete fresh install | `install` | `create-if-absent` | requested candidate | exact two | partial target allowed; record/stage/request resume tuple equal |
| incomplete compatibility install (`update` on absent) | `install` | `preserve-only` | requested candidate | exact two | seeds never created |
| incomplete reinstall | `install` | `preserve-only` | requested candidate | exact two | tooling-absent predecessor; seeds never created |
| incomplete update | `update` | `preserve-only` | requested candidate | exact two | previous ready record owned roots/slots |
| incomplete migration | `migrate-0.2.3` | `preserve-only` | final candidate | exact two | exact legacy evidence was proven before first write |
| incomplete uninstall | `uninstall` | `preserve-only` | input ready candidate or final candidate governing legacy removal | exact two | tooling detach in progress |
| ready after fresh | null | `create-if-absent` | installed candidate | exact two | 4 roots/2 marked slots equal candidate |
| ready after update/reinstall/migration | null | `preserve-only` | installed candidate | exact two | 4 roots/2 marked slots equal candidate |
| tooling-absent-preserved-data | null | `preserve-only` | last governing candidate | exact two | 4 roots/2 slots absent; shared container/record/data remain |

Terminal `ready.seed_policy=create-if-absent` is provenance only and does not grant future seed mutation. Every next update/uninstall/reinstall publishes a new incomplete record with `preserve-only` before mutation.

### WIR-REC-003 — Golden records

Ready after fresh:

```json
{
  "schema_version": 1,
  "state": "ready",
  "operation": null,
  "version": "0.2.4",
  "candidate_digest": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "seed_policy": "create-if-absent",
  "skill_slots": {
    "spec-dock": "0.2.4",
    "spec-dock-grill-with-docs": "0.2.4"
  }
}
```

Incomplete update:

```json
{
  "schema_version": 1,
  "state": "incomplete",
  "operation": "update",
  "version": "0.2.4",
  "candidate_digest": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "seed_policy": "preserve-only",
  "skill_slots": {
    "spec-dock": "0.2.4",
    "spec-dock-grill-with-docs": "0.2.4"
  }
}
```

Tooling absent:

```json
{
  "schema_version": 1,
  "state": "tooling-absent-preserved-data",
  "operation": null,
  "version": "0.2.4",
  "candidate_digest": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "seed_policy": "preserve-only",
  "skill_slots": {
    "spec-dock": "0.2.4",
    "spec-dock-grill-with-docs": "0.2.4"
  }
}
```

## 3. Observed-only states

The classifier may return the following values, but none is serialized as `state`:

| Observed state | Evidence | Mutation authority |
|---|---|---|
| `absent` | record absent、4 roots/2 slots absent、shared container absent or real | command-specific admission only |
| `legacy-0.2.3` | exact plain marker、exact 4 roots、each slot absent/exact、no recovery marker | migrate/uninstall only, preserve-only |
| `blocked` | ownership/binding/record/slot/candidate mismatch | none |
| `bootstrap-incomplete` | stage owner proves created shared container before record and cleanup could not complete | exact same resume tuple only |

`bootstrap-incomplete` is an observed recovery condition backed byexternal `STAGE-OWNER.json`; it is not an installation record state.

## 4. Operation wire values and command mapping

| Wire operation | Entry points | Seed policy | Terminal state |
|---|---|---|---|
| `install` | fresh `init`, fresh `init --force`, `update` on absent, reinstall | fresh init: create-if-absent; other install cases: preserve-only | ready |
| `update` | `update` on ready, `init --force` on ready | preserve-only | ready |
| `migrate-0.2.3` | `update` or `init --force` on exact legacy | preserve-only | ready |
| `uninstall` | default/`--keep-specs` dry-run/apply on ready or exact legacy | preserve-only | tooling-absent-preserved-data |
| null | invalid request and `--remove-specs` trap before lifecycle dispatch | null | no record change |

The exact resume identity is `(operation, candidate_digest, seed_policy)`. All three values must match request、record、stage owner。Alias choice is not part of identity; aliases must map deterministically to the same tuple.

## 5. Slot marker wire

Path: `<slot>/.spec-dock-provider-slot.json`。Exact keys:

| Field | Type | Constraint |
|---|---|---|
| `schema_version` | integer | `1` |
| `slot` | string | `spec-dock` or `spec-dock-grill-with-docs`, matching physical slot |
| `version` | string | `0.2.4` |
| `candidate_digest` | string | record digest exact match |

Marker is excluded from candidate digest to avoid self-reference.

## 6. Service result wire

### WIR-RES-001 — Top-level fields

| Field | Type | Nullable | Contract |
|---|---|---:|---|
| `schema_version` | integer | no | `1` |
| `status` | string | no | status enum below |
| `code` | string | no | exact code enum below; no fallback code |
| `operation` | string or null | yes | operation enum above |
| `candidate_digest` | string or null | yes | null only before candidate selection or removed operation |
| `seed_policy` | string or null | yes | null only when operation is null |
| `mutation_started` | boolean | no | incomplete record published or uncleaned bootstrap exists |
| `bootstrap_rolled_back` | boolean | no | true only when exact empty bootstrap cleanup restored pre-state |
| `phase` | string | no | exact implementation phase token |
| `last_completed_phase` | string | no | exact phase token or `not-started` |
| `retry_command` | string or null | yes | only same tuple partial failure and safely representable target |
| `failed_paths` | array of string | no | sorted fixed repository-relative paths; never null |
| `pending_paths` | array of string | no | sorted fixed repository-relative paths; never null |
| `actions` | array | no | action wire below |
| `warnings` | array of string | no | never null |
| `errors` | array of string | no | sanitized; never null |
| `guidance` | array of string | no | never null |

### WIR-RES-002 — Status and exit

| Status | Exit | Required relation |
|---|---:|---|
| `planned` | 0 | dry-run; mutation_started false |
| `completed` | 0 | desired durable postcondition |
| `completed_with_warnings` | 0 | desired durable postcondition; only owned external cleanup warning |
| `blocked` | 1 | no durable mutation or fully rolled-back bootstrap |
| `partial_failure` | 1 | durable mutation or cleanup-failed bootstrap; exact retry tuple retained |
| `error` | 2 | invalid request/removed operation; mutation zero |

### WIR-RES-003 — Code enum

Allowed codes only:

```text
install-completed
reinstall-completed
update-completed
migration-completed
uninstall-planned
uninstall-completed
completed-with-cleanup-warning
target-ownership-unproven
unsafe-target-binding
invalid-installation-record
invalid-slot-marker
legacy-workspace-not-exact
legacy-recovery-active
candidate-invalid
resume-operation-mismatch
resume-candidate-mismatch
resume-seed-policy-mismatch
bootstrap-recovery-required
bootstrap-partial-failure
install-partial-failure
update-partial-failure
migration-partial-failure
uninstall-partial-failure
invalid-request
target-not-directory
tooling-not-installed
spec-history-purge-removed
```

### WIR-RES-004 — Action wire

Each `actions[]` object has exact keys `path`, `category`, `status`, `reason`, `error`。

- `path`: repository-relative fixed path; no absolute path/content.
- `category` enum: `bootstrap-container`, `publish-record`, `replace-root`, `replace-slot`, `create-seed`, `remove-root`, `remove-slot`, `cleanup-stage`, `preserve`。
- `status` enum: `planned`, `completed`, `already-satisfied`, `preserved`, `blocked`, `failed`。
- `reason`: exact stable lower-kebab token from the implementation's tested relation; arbitrary exception text forbidden。
- `error`: sanitized string or null; null on non-failed action。

## 7. Public uninstall JSON mapping

Existing fields remain: `schema_version`, `target`, `mode`, `apply`, `specs_mode`, `status`, `phase`, `last_completed_phase`, `retry_command`, `failed_paths`, `pending_paths`, `summary`, `actions`, `guidance`, `errors`。

Additive fields: `code`, `operation`, `candidate_digest`, `seed_policy`, `mutation_started`, `bootstrap_rolled_back`, `warnings`。

`summary` exact keys are `already_satisfied`, `blocked`, `completed`, `failed`, `planned`, `preserved`; values are non-negative integers。CLI serialization is exact `json.dumps(payload, sort_keys=True)` followed by one LF。

### WIR-GOLDEN-U1 — Uninstall dry-run parsed object

```json
{
  "actions": [
    {
      "category": "remove-root",
      "error": null,
      "path": "spec-dock/docs",
      "reason": "owned-tooling-root",
      "status": "planned"
    },
    {
      "category": "remove-root",
      "error": null,
      "path": "spec-dock/templates",
      "reason": "owned-tooling-root",
      "status": "planned"
    },
    {
      "category": "remove-root",
      "error": null,
      "path": "spec-dock/system",
      "reason": "owned-tooling-root",
      "status": "planned"
    },
    {
      "category": "remove-root",
      "error": null,
      "path": "spec-dock/scripts",
      "reason": "owned-tooling-root",
      "status": "planned"
    },
    {
      "category": "remove-slot",
      "error": null,
      "path": ".agents/skills/spec-dock",
      "reason": "owned-skill-slot",
      "status": "planned"
    },
    {
      "category": "remove-slot",
      "error": null,
      "path": ".agents/skills/spec-dock-grill-with-docs",
      "reason": "owned-skill-slot",
      "status": "planned"
    },
    {
      "category": "publish-record",
      "error": null,
      "path": "spec-dock/spec-dock.version",
      "reason": "tooling-absent-terminal-record",
      "status": "planned"
    }
  ],
  "apply": false,
  "bootstrap_rolled_back": false,
  "candidate_digest": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "code": "uninstall-planned",
  "errors": [],
  "failed_paths": [],
  "guidance": [
    "dry-run only; pass --apply to remove managed tooling while preserving specs"
  ],
  "last_completed_phase": "preflight",
  "mode": "dry-run",
  "mutation_started": false,
  "operation": "uninstall",
  "pending_paths": [],
  "phase": "preflight",
  "retry_command": null,
  "schema_version": 1,
  "seed_policy": "preserve-only",
  "specs_mode": null,
  "status": "planned",
  "summary": {
    "already_satisfied": 0,
    "blocked": 0,
    "completed": 0,
    "failed": 0,
    "planned": 7,
    "preserved": 0
  },
  "target": ".",
  "warnings": []
}
```

Exact stdout bytes are the following one line plus LF:

```text
{"actions": [{"category": "remove-root", "error": null, "path": "spec-dock/docs", "reason": "owned-tooling-root", "status": "planned"}, {"category": "remove-root", "error": null, "path": "spec-dock/templates", "reason": "owned-tooling-root", "status": "planned"}, {"category": "remove-root", "error": null, "path": "spec-dock/system", "reason": "owned-tooling-root", "status": "planned"}, {"category": "remove-root", "error": null, "path": "spec-dock/scripts", "reason": "owned-tooling-root", "status": "planned"}, {"category": "remove-slot", "error": null, "path": ".agents/skills/spec-dock", "reason": "owned-skill-slot", "status": "planned"}, {"category": "remove-slot", "error": null, "path": ".agents/skills/spec-dock-grill-with-docs", "reason": "owned-skill-slot", "status": "planned"}, {"category": "publish-record", "error": null, "path": "spec-dock/spec-dock.version", "reason": "tooling-absent-terminal-record", "status": "planned"}], "apply": false, "bootstrap_rolled_back": false, "candidate_digest": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", "code": "uninstall-planned", "errors": [], "failed_paths": [], "guidance": ["dry-run only; pass --apply to remove managed tooling while preserving specs"], "last_completed_phase": "preflight", "mode": "dry-run", "mutation_started": false, "operation": "uninstall", "pending_paths": [], "phase": "preflight", "retry_command": null, "schema_version": 1, "seed_policy": "preserve-only", "specs_mode": null, "status": "planned", "summary": {"already_satisfied": 0, "blocked": 0, "completed": 0, "failed": 0, "planned": 7, "preserved": 0}, "target": ".", "warnings": []}
```

### WIR-GOLDEN-U2 — Removed purge trap

```json
{
  "actions": [],
  "apply": true,
  "bootstrap_rolled_back": false,
  "candidate_digest": null,
  "code": "spec-history-purge-removed",
  "errors": [
    "spec history purge has been removed; no files were changed"
  ],
  "failed_paths": [],
  "guidance": [
    "run uninstall --apply without --remove-specs to remove tooling and preserve all specification data"
  ],
  "last_completed_phase": "not-started",
  "mode": "apply",
  "mutation_started": false,
  "operation": null,
  "pending_paths": [],
  "phase": "request",
  "retry_command": null,
  "schema_version": 1,
  "seed_policy": null,
  "specs_mode": "remove",
  "status": "error",
  "summary": {
    "already_satisfied": 0,
    "blocked": 0,
    "completed": 0,
    "failed": 0,
    "planned": 0,
    "preserved": 0
  },
  "target": ".",
  "warnings": []
}
```

Exact stdout bytes in `--json` mode:

```text
{"actions": [], "apply": true, "bootstrap_rolled_back": false, "candidate_digest": null, "code": "spec-history-purge-removed", "errors": ["spec history purge has been removed; no files were changed"], "failed_paths": [], "guidance": ["run uninstall --apply without --remove-specs to remove tooling and preserve all specification data"], "last_completed_phase": "not-started", "mode": "apply", "mutation_started": false, "operation": null, "pending_paths": [], "phase": "request", "retry_command": null, "schema_version": 1, "seed_policy": null, "specs_mode": "remove", "status": "error", "summary": {"already_satisfied": 0, "blocked": 0, "completed": 0, "failed": 0, "planned": 0, "preserved": 0}, "target": ".", "warnings": []}
```

### WIR-GOLDEN-R1 — Partial update service result

```json
{
  "actions": [
    {
      "category": "replace-root",
      "error": null,
      "path": "spec-dock/docs",
      "reason": "candidate-published",
      "status": "completed"
    },
    {
      "category": "replace-root",
      "error": "injected failure",
      "path": "spec-dock/templates",
      "reason": "publish-failed",
      "status": "failed"
    }
  ],
  "bootstrap_rolled_back": false,
  "candidate_digest": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
  "code": "update-partial-failure",
  "errors": [
    "managed tooling update did not reach the ready state"
  ],
  "failed_paths": [
    "spec-dock/templates"
  ],
  "guidance": [
    "retry the same update command with the same candidate and seed policy"
  ],
  "last_completed_phase": "publish-docs",
  "mutation_started": true,
  "operation": "update",
  "pending_paths": [
    "spec-dock/templates",
    "spec-dock/system",
    "spec-dock/scripts",
    ".agents/skills/spec-dock",
    ".agents/skills/spec-dock-grill-with-docs"
  ],
  "phase": "publish-templates",
  "retry_command": "spec-dock update .",
  "schema_version": 1,
  "seed_policy": "preserve-only",
  "status": "partial_failure",
  "warnings": []
}
```

## 8. Public text

Successful init/update stdout:

```text
spec-dock: ok (init) -> <resolved-target>
spec-dock: ok (update) -> <resolved-target>
```

Fatal request/block/partial stderr first line:

```text
error: <code>: <sanitized-message>
```

Uninstall text starts exactly:

```text
spec-dock: uninstall <plan|result> (<dry-run|apply>) -> <safe-target>
specs_mode: <unspecified|keep|remove>
status: <status>
code: <code>
operation: <uninstall|unavailable>
seed_policy: <preserve-only|unavailable>
mutation_started: <true|false>
bootstrap_rolled_back: <true|false>
phase: <phase>
last_completed_phase: <phase>
retry_command: <command|unavailable>
failed_paths: <comma-list|none>
```

Then `summary:`, `actions:`, optional `warnings:`, optional `errors:`, and `guidance:` in that order. Warning lines use `spec-dock: warning: <message>` on stderr for init/update; uninstall text keeps warnings in the rendered section. No stack trace or consumer content is public.

## 9. Tests and trace

Required tests:

```text
tests/unit/infra/test_provider_lifecycle_wire_contract.py
tests/unit/infra/test_provider_lifecycle_model.py
tests/unit/infra/test_provider_lifecycle_public_result.py
tests/cli_runtime/test_provider_lifecycle.py
tests/cli_runtime/test_uninstall.py
tests/cli_runtime/test_update.py
```

Tests cover exact keys、types、nullability、enum rejection、state relations、resume tuple、golden parsed objects、exact sorted JSON bytes、text/exit、sanitization。No implementation default may silently map unknown values.

Normative trace:

- Epic: E384-RQ-003、006〜010、022; E384-D-007、011〜013、026。
- Issue: I392-RQ-004〜019、028; I392-D-001〜010、017。
- Plan: I392-S10、S20、S40、S60。
