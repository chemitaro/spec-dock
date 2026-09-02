---
種別: Normative Artifact
ID: "provider-lifecycle-wire-contract-v7"
タイトル: "Provider Lifecycle Wire Contract"
状態: "accepted"
最終更新: "2026-09-02"
対象: ["epic-00384", "iss-00392"]
repository_evidence:
  repository: "chemitaro/spec-dock"
  branch: "codex/epic-00384-provider-test-strategy-planning"
  sha: "ea168b745d3f443f11a24b975f32e3bb6fb17b1a"
---

# Provider Lifecycle Wire Contract

## 1. Authority and closed-world rule

本ArtifactはIssue #392のprovider lifecycle public wireに対する唯一のnormative authorityである。Production enum、dataclass、constructor、serializer、CLI text/JSON、golden、fault/migration evidenceは本書のfinite tablesだけを使用する。未知のfield、enum、code、phase、reason、path、relationは生成・受理せずfail closedする。`other`、`unknown`、`generic`、`internal-error`、free-form reason、catch-all mapping、dictionary/filesystem orderはwire valueとして禁止する。予期しない未型付け例外は本wire codeへ丸めずprocess/test defectとして失敗させる。

## 2. Canonical scalar and serialization conventions

| Type | Exact contract |
|---|---|
| UTF-8 | NULなし。JSON control charactersはescape。 |
| Version | Final `0.2.4`; exact legacy input only `0.2.3`. |
| SHA-256 | 64 lowercase hexadecimal characters. |
| Git commit/tree | 40 lowercase hexadecimal characters. |
| Boolean | JSON `true` / `false`; integer代用禁止。 |
| Null | JSON `null`; missing field代用禁止。 |
| Public path | repository-relative POSIX path or exact sentinel `@provider-stage`. Absolute、`..`、backslash禁止。 |
| JSON bytes | UTF-8、key orderは本書どおり、`ensure_ascii=False,separators=(",",":")`、末尾LF一つ。 |


### WIR-INV-001 — Mechanically checked inventory

The normative finite inventory is exact:

| Item | Count |
|---|---:|
| public status values | 6 |
| public code values | 38 |
| `phase` values | 23 |
| `last_completed_phase` values | 24 |
| durable record goldens | 4 |
| complete code/context relation rows | 142 |
| public JSON review goldens | 33 |

The implementation test extracts the §10 table and all fenced JSON review goldens from this file, verifies these counts, parses every JSON block, and asserts one terminal LF. A count drift is a specification/test defect and is not auto-accepted.

Table expressions are exact value functions:

- `request.candidate_digest`: validated packaged candidate digest selected for the invocation.
- `record.candidate_digest` / `record.seed_policy` / `record.operation`: exact values parsed from the valid record.
- `legacy_fixture.aggregate_digest`: exact deterministic aggregate of the recognized `0.2.3` roots/slots.
- `owned_target_digest`: `record.candidate_digest` for final-format state, otherwise `legacy_fixture.aggregate_digest` for exact legacy state.
- `null`: public JSON null. These expressions are not implementation choices.
- `active.operation` / `active.candidate_digest` / `active.seed_policy`: exact values from validated `ACTIVE.json`.
- `active.result_family`: exact private enum `install|legacy-migration|update|uninstall`, written before target mutation and used only to select the cleanup retry command. It is not part of the resume tuple or public result.
- `actual_request.mode` / `actual_request.apply` / `actual_request.specs_mode`: exact parser-normalized echo selected by WIR-CLEANUP-001 before repository locking. These values describe the invocation that encountered pending terminal cleanup; they do not change the old ACTIVE operation/digest/policy exposed by the result.
- `active.deferred_invocation`: private null or exact object with ordered keys `invocation_id,rendered_command`. `invocation_id` is one of `init|init-force|update|uninstall-dry-run|uninstall-dry-run-keep|uninstall-apply|uninstall-apply-keep`; `rendered_command` is the corresponding WIR-TEXT-001 command. Every no-token public invocation is a desired request. The first desired request is durably preserved until cleanup completes; tokenized retry, repeat, or later desired invocation cannot replace it.
- `active.cleanup_token`: exact 64-hex value stored in ACTIVE, computed as SHA-256 over `spec-dock-terminal-cleanup-v1\0` plus repository key, tuple key and result family in that order. It distinguishes an internal cleanup retry from an identically rendered desired lifecycle command; it is identity binding, not authorization.
- `active.cleanup_retry_invocation`: exact private invocation with `role=cleanup-retry`, the matching `active.cleanup_token`, and public base form `install/create-if-absent -> init-force`, `install/preserve-only -> update`, `legacy-migration -> update`, `update -> update`, `uninstall -> uninstall-apply-keep`.
- Public `continuation` is the only next-action authority. A caller never derives a desired command from `operation`, `result_family`, `retry_command`, mode or prose.

## 3. Canonical target and public array order

### WIR-ORD-001 — `TARGET_PATH_ORDER`

All `failed_paths`、`pending_paths`、`actions` are ordered by this rank only:

| Rank | Exact path |
|---:|---|
| 0 | `spec-dock` |
| 1 | `spec-dock/spec-dock.version` |
| 2 | `spec-dock/docs` |
| 3 | `spec-dock/templates` |
| 4 | `spec-dock/system` |
| 5 | `spec-dock/scripts` |
| 6 | `.agents/skills/spec-dock` |
| 7 | `.agents/skills/spec-dock-grill-with-docs` |
| 8 | `spec-dock/.gitignore` |
| 9 | `.github` |
| 10 | `.github/workflows` |
| 11 | `.github/workflows/ci.yml` |
| 12 | `@provider-stage` |

Rules:

1. `failed_paths` equals exactly the paths of actions whose status is `failed`.
2. `pending_paths` equals exactly the paths of actions whose status is `pending`.
3. Both arrays are unique and independently ordered by `TARGET_PATH_ORDER`.
4. `actions` contains at most one row per path and is ordered by `TARGET_PATH_ORDER`.
5. Blocked/error results expose no path detail: all three arrays are empty.
6. Protected consumer paths are never added to the public order; rejection uses a closed top-level code/message.
7. `warnings` and `errors` contain at most one string. `guidance` uses the exact code-bound sequence in §11.

## 4. Durable installation record

Path: `spec-dock/spec-dock.version`. Exact seven keys and order:

| Order | Key | Type | Nullability / relation |
|---:|---|---|---|
| 1 | `schema_version` | integer | non-null, exact `1` |
| 2 | `state` | string | `incomplete` / `ready` / `tooling-absent-preserved-data` |
| 3 | `operation` | string or null | incomplete: `install|update|uninstall`; terminal: null |
| 4 | `version` | string | exact `0.2.4` |
| 5 | `candidate_digest` | string | non-null lowercase SHA-256 |
| 6 | `seed_policy` | string | `create-if-absent|preserve-only` |
| 7 | `skill_slots` | object | exact ordered keys `spec-dock`,`spec-dock-grill-with-docs`, both `0.2.4` |

Parser: UTF-8、regular file、link count1、max4096 bytes、duplicate/unknown/missing key rejection。Writer mode0644、atomic replace only。

### WIR-REC-001 — State relations

| State | Operation | Seed policy | Required postcondition |
|---|---|---|---|
| incomplete | install | create-if-absent or preserve-only | Exact resume identity `(install,candidate_digest,seed_policy)`; payload may be partial. |
| incomplete | update | preserve-only | Ready payload is converging to candidate. |
| incomplete | uninstall | preserve-only | Owned roots/slots may be partially detached. |
| ready | null | create-if-absent or preserve-only | Four roots/two slots/markers match digest. |
| tooling-absent-preserved-data | null | preserve-only | Roots/slots absent; shared container and record remain. |

Terminal ready policy records the immediately completed operation only and never authorizes later seed writes. A new update/uninstall first publishes a preserve-only incomplete record.


### WIR-REC-002 — Command relations

| Invocation / observed state | Mode | Durable operation | Seed policy | Required terminal/result family |
|---|---|---|---|---|
| `init` or `init --force` / `absent` | apply | `install` | `create-if-absent` | `install-*` |
| `update` / `absent` | apply | `install` | `preserve-only` | `install-*` |
| `init`, `init --force` or `update` / `tooling-absent-preserved-data` | apply | `install` | `preserve-only` | `install-*` |
| `init --force` or `update` / exact `legacy-0.2.3` | apply | `install` | `preserve-only` | `legacy-migration-*` |
| `init --force` or `update` / `ready` | apply | `update` | `preserve-only` | `update-*` |
| `uninstall` / exact legacy | dry-run | `uninstall` | `preserve-only` | `uninstall-planned` |
| `uninstall` / `ready` | dry-run | `uninstall` | `preserve-only` | `uninstall-planned` |
| `uninstall` / `incomplete` with `operation=uninstall` | dry-run | `uninstall` | exact record `preserve-only` | `uninstall-planned` |
| `uninstall` / `tooling-absent-preserved-data` | dry-run | `uninstall` | `preserve-only` | `uninstall-already-absent` with status `planned` |
| `uninstall --apply` / exact legacy | apply | `uninstall` | `preserve-only` | `uninstall-completed*` |
| `uninstall --apply` / `ready` | apply | `uninstall` | `preserve-only` | `uninstall-completed*` |
| `uninstall --apply` / matching `incomplete(uninstall)` | apply | `uninstall` | exact record `preserve-only` | resume to `uninstall-completed*` or `uninstall-partial-failure` |
| `uninstall --apply` / `tooling-absent-preserved-data` | apply | `uninstall` | `preserve-only` | `uninstall-already-absent` with status `completed` |
| `uninstall --remove-specs` / any target state | request-selected dry-run or apply | `null` | `null` | `spec-history-purge-removed` before target observation |

Exact migration is not a fourth durable operation. It is preserve-only `install` plus a `legacy-migration-*` public code. A dry-run against `incomplete(uninstall)` does not change or resume the record; it reports the remaining deterministic uninstall plan. No other incomplete operation is accepted by uninstall.

### WIR-REC-003 — Record goldens

The digest fixture is exactly 64 lowercase `d` characters. Each block below is valid compact JSON followed by one LF; both the nested `skill_slots` object and the outer record object are closed.

```json
{"schema_version":1,"state":"ready","operation":null,"version":"0.2.4","candidate_digest":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","seed_policy":"create-if-absent","skill_slots":{"spec-dock":"0.2.4","spec-dock-grill-with-docs":"0.2.4"}}
```

```json
{"schema_version":1,"state":"incomplete","operation":"install","version":"0.2.4","candidate_digest":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","seed_policy":"preserve-only","skill_slots":{"spec-dock":"0.2.4","spec-dock-grill-with-docs":"0.2.4"}}
```

```json
{"schema_version":1,"state":"incomplete","operation":"update","version":"0.2.4","candidate_digest":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","seed_policy":"preserve-only","skill_slots":{"spec-dock":"0.2.4","spec-dock-grill-with-docs":"0.2.4"}}
```

```json
{"schema_version":1,"state":"tooling-absent-preserved-data","operation":null,"version":"0.2.4","candidate_digest":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","seed_policy":"preserve-only","skill_slots":{"spec-dock":"0.2.4","spec-dock-grill-with-docs":"0.2.4"}}
```

## 5. Observed-only state enum

Exact enum: `absent`、`legacy-0.2.3`、`incomplete`、`ready`、`tooling-absent-preserved-data`、`blocked`。Absent、legacy、blocked are never serialized. Blocked has no free-form reason outside the code enum.

## 6. Phase and last-completed-phase

### WIR-PHASE-001 — Exact enum

`phase` is exactly:

```text
request-validation
preflight
candidate-staging
bootstrap-container
publish-incomplete-record
publish-docs
publish-templates
publish-system
publish-scripts
publish-slot-spec-dock
publish-slot-spec-dock-grill-with-docs
create-seed-spec-dock-gitignore
create-seed-consumer-ci
detach-docs
detach-templates
detach-system
detach-scripts
detach-slot-spec-dock
detach-slot-spec-dock-grill-with-docs
verify-target
publish-terminal-record
cleanup-stage
complete
```

`last_completed_phase` is one of the same values plus `not-started`.

### WIR-PHASE-002 — Exact sequences

Install/create-if-absent:

```text
request-validation
preflight
candidate-staging
bootstrap-container
publish-incomplete-record
publish-docs
publish-templates
publish-system
publish-scripts
publish-slot-spec-dock
publish-slot-spec-dock-grill-with-docs
create-seed-spec-dock-gitignore
create-seed-consumer-ci
verify-target
publish-terminal-record
cleanup-stage
complete
```

Install/preserve-only:

```text
request-validation
preflight
candidate-staging
bootstrap-container
publish-incomplete-record
publish-docs
publish-templates
publish-system
publish-scripts
publish-slot-spec-dock
publish-slot-spec-dock-grill-with-docs
verify-target
publish-terminal-record
cleanup-stage
complete
```

Update:

```text
request-validation
preflight
candidate-staging
publish-incomplete-record
publish-docs
publish-templates
publish-system
publish-scripts
publish-slot-spec-dock
publish-slot-spec-dock-grill-with-docs
verify-target
publish-terminal-record
cleanup-stage
complete
```

Uninstall dry-run:

```text
request-validation
preflight
complete
```

Uninstall apply:

```text
request-validation
preflight
candidate-staging
publish-incomplete-record
detach-docs
detach-templates
detach-system
detach-scripts
detach-slot-spec-dock
detach-slot-spec-dock-grill-with-docs
verify-target
publish-terminal-record
cleanup-stage
complete
```

`bootstrap-container` is a no-mutation bind verification when the shared container exists. Uninstall staging is the external tombstone stage, so `candidate-staging` is retained.

### WIR-PHASE-003 — Pair rule and mandatory cleanup transition

- Partial lifecycle results use the exact expanded row in §10; no arbitrary adjacent pair is accepted.
- Planned/already-absent use `complete/preflight`.
- Clean completion uses `complete/cleanup-stage`.
- Cleanup warning uses `complete/publish-terminal-record` and leaves validated `ACTIVE.state=terminal-cleanup`.
- Mandatory pre-dispatch cleanup failure uses `cleanup-stage/publish-terminal-record`.
- Mandatory pre-dispatch cleanup success uses `complete/cleanup-stage`.
- Request errors use `request-validation/not-started`.
- Every blocked row uses its exact §10 pair. No derived rejected phase exists.

Parser errors and `uninstall --remove-specs` are request-validation outcomes and do not enter lifecycle cleanup. Every other parser-valid lifecycle invocation normalizes its echo before repository locking:

### WIR-CLEANUP-001 — Invocation role, durable desired request and cleanup-only return

Public desired invocations contain no private cleanup token:

| Normalized invocation ID | Exact desired invocation | `mode` | `apply` | `specs_mode` |
|---|---|---|---:|---|
| `init` | `spec-dock init -- ${QUOTED_TARGET}` | `apply` | `true` | `null` |
| `init-force` | `spec-dock init --force -- ${QUOTED_TARGET}` | `apply` | `true` | `null` |
| `update` | `spec-dock update -- ${QUOTED_TARGET}` | `apply` | `true` | `null` |
| `uninstall-dry-run` | `spec-dock uninstall -- ${QUOTED_TARGET}` | `dry-run` | `false` | `null` |
| `uninstall-dry-run-keep` | `spec-dock uninstall --keep-specs -- ${QUOTED_TARGET}` | `dry-run` | `false` | `keep` |
| `uninstall-apply` | `spec-dock uninstall --apply -- ${QUOTED_TARGET}` | `apply` | `true` | `null` |
| `uninstall-apply-keep` | `spec-dock uninstall --apply --keep-specs -- ${QUOTED_TARGET}` | `apply` | `true` | `keep` |

The generated cleanup-only invocations are exact and carry the hidden parser option `--provider-cleanup-token`. The option is accepted only in these three forms, is suppressed from public help, and never changes public `mode/apply/specs_mode` echo:

| Cleanup base ID | Exact cleanup-only invocation |
|---|---|
| `init-force` | `spec-dock init --force --provider-cleanup-token ${ACTIVE_CLEANUP_TOKEN} -- ${QUOTED_TARGET}` |
| `update` | `spec-dock update --provider-cleanup-token ${ACTIVE_CLEANUP_TOKEN} -- ${QUOTED_TARGET}` |
| `uninstall-apply-keep` | `spec-dock uninstall --apply --keep-specs --provider-cleanup-token ${ACTIVE_CLEANUP_TOKEN} -- ${QUOTED_TARGET}` |

`uninstall --remove-specs` is resolved as the request-error trap before repository cleanup and is not cleanup-gated. A token on any unlisted command form, a non-64-lowercase-hex token, a token with no ACTIVE, or a token unequal to `active.cleanup_token` is exact `invalid-request`, exit 2, mutation false.

After repository lock/binding and before target classification or candidate construction, resolve the exact repository `ACTIVE.json` without scanning.

1. ACTIVE absent: fsync the repository-stage directory and continue normal dispatch; emit no cleanup result.
2. Terminal record plus `ACTIVE.state=ready`: atomically replace ACTIVE with identical content except `state=terminal-cleanup`; fsync.
3. Normalize the invocation role before cleanup.
   - Token absent: role is `desired`; atomically store the first exact desired invocation in `active.deferred_invocation` when null, even when its public base form equals the old result-family retry. If already non-null, preserve the first object byte-for-byte; later desired invocations are not queued.
   - Exact token present on the exact derived form: role is `cleanup-retry`; never create, replace or clear `deferred_invocation`.
4. Validate namespace, repository, tuple, result family, cleanup token, deferred invocation, stage owner and registered entries. Remove only registered entries and exact stage; an already-absent stage is accepted.
5. Remove ACTIVE only by expected-byte/content binding and fsync its parent. A crash after unlink but before parent fsync is recovered by rule 1.
6. Cleanup failure returns `terminal-cleanup-failed` and executes no lifecycle operation.
   - `continuation.next_action=retry-cleanup` and `next_command=active.cleanup_retry_command` containing the exact token.
   - `after_cleanup_action/run-request` and `after_cleanup_command` carry the immutable first desired request when present; otherwise `none/null`.
7. Cleanup success from present ACTIVE returns `terminal-cleanup-completed` and executes no lifecycle operation.
   - If the immutable desired request is present, `next_action=run-request` with that exact no-token desired command.
   - If no desired request is present, all continuation values are `none/null`.
8. Thus a no-token desired `update` or `init --force` is machine-distinct from a tokenized cleanup retry with the same public base form. A retry success returns the separately preserved desired command, never the durable old operation by inference. A pure cleanup retry with no desired request returns no next action.
9. Callers execute exactly `continuation.next_command` when `next_action` is not `none`; they never derive a command from actual invocation, `operation`, `result_family`, `retry_command` or prose.

## 7. Slot marker

Each `.spec-dock-provider-slot.json` has exact keys/order `schema_version,slot,version,candidate_digest`; schema1、version0.2.4、mode0644、max2048、regular/link1、one LF. Marker is excluded from candidate digest.

## 8. Public result object

Exact key order:

| Order | Field | Type | Relation |
|---:|---|---|---|
| 1 | schema_version | integer | 1 |
| 2 | target | string | normalized public target label |
| 3 | mode | string | dry-run/apply |
| 4 | apply | boolean | exact invocation echo |
| 5 | specs_mode | string/null | uninstall: null/keep/remove; otherwise null |
| 6 | status | string | §9 |
| 7 | code | string | §10 |
| 8 | operation | string/null | exact §10 |
| 9 | candidate_digest | string/null | exact §10 |
| 10 | seed_policy | string/null | exact §10 |
| 11 | mutation_started | boolean | exact §10 |
| 12 | bootstrap_rolled_back | boolean | exact §10 |
| 13 | phase | string | exact §10 |
| 14 | last_completed_phase | string | exact §10 |
| 15 | retry_command | string/null | compatibility echo; exact §10/§11; never sole continuation authority |
| 16 | continuation | object | exact keys/order `next_action,next_command,after_cleanup_action,after_cleanup_command`; WIR-CONT-001 |
| 17 | failed_paths | array[string] | WIR-ORD-001 |
| 18 | pending_paths | array[string] | WIR-ORD-001 |
| 19 | summary | object | keys planned,completed,preserved,pending,failed,warnings; action-status counts |
| 20 | actions | array[action] | §12 |
| 21 | guidance | array[string] | §11 |
| 22 | warnings | array[string] | §11 |
| 23 | errors | array[string] | §11 |

No additional field is permitted.

### WIR-CONT-001 — Closed continuation profiles

Exact action enums are `none|retry-cleanup|run-request` for `next_action` and `none|run-request` for `after_cleanup_action`.

| Profile | Exact object relation |
|---|---|
| `NONE` | `none,null,none,null` |
| `LIFECYCLE-RETRY` | `run-request,retry_command,none,null` |
| `CLEANUP-WARNING` | `retry-cleanup,retry_command,none,null` |
| `CLEANUP-FAILED-NONE` | `retry-cleanup,retry_command,none,null` |
| `CLEANUP-FAILED-DEFERRED` | `retry-cleanup,retry_command,run-request,render(active.deferred_invocation)` |
| `CLEANUP-COMPLETED-NONE` | `none,null,none,null` |
| `CLEANUP-COMPLETED-DEFERRED` | `run-request,render(active.deferred_invocation),none,null` |

`CLEANUP-FAILED-BY-ROLE-AND-DEFERRED` selects `CLEANUP-FAILED-DEFERRED` for every no-token desired invocation and for a tokenized retry when deferred is present; otherwise it selects `CLEANUP-FAILED-NONE`. `CLEANUP-COMPLETED-BY-ROLE-AND-DEFERRED` applies the parallel success rule.

`render()` uses WIR-CLEANUP-001 exact invocation strings. Action `none` iff paired command is null. `retry_command` equals `continuation.next_command` only for lifecycle retry, cleanup warning and cleanup failure. Cleanup success always has `retry_command=null`.

## 9. Status enum

| Status | Exit | Action statuses |
|---|---:|---|
| planned | 0 | planned,preserved |
| completed | 0 | completed,preserved |
| completed_with_warnings | 0 | completed,preserved,warning |
| blocked | 1 | actions empty |
| partial_failure | 1 | completed,preserved,pending,failed |
| error | 2 | actions empty |

## 10. Complete code/value/phase relation matrix

Every valid result matches exactly one row after evaluating its finite Variant. Duplicate/no match is a constructor defect. Blocked/error actions/failed_paths/pending_paths are empty.

| Code | Variant | Status | Mode | Apply | Operation | `candidate_digest` | `seed_policy` | Mutation | Bootstrap rollback | Phase | Last completed | Retry | Actions | Exit | Continuation |
|---|---|---|---|---:|---|---|---|---:|---:|---|---|---|---|---:|---|
| `install-completed` | `create-if-absent install` | `completed` | `apply` | `true` | `install` | `request.candidate_digest` | `create-if-absent` | true | false | `complete` | `cleanup-stage` | `null` | `install-create terminal action set` | 0 | `NONE` |
| `install-completed` | `preserve-only install/reinstall` | `completed` | `apply` | `true` | `install` | `request.candidate_digest` | `preserve-only` | true | false | `complete` | `cleanup-stage` | `null` | `install-preserve terminal action set` | 0 | `NONE` |
| `install-completed-with-cleanup-warning` | `create-if-absent install` | `completed_with_warnings` | `apply` | `true` | `install` | `request.candidate_digest` | `create-if-absent` | true | false | `complete` | `publish-terminal-record` | `install/create-if-absent retry` | `install-create terminal + one stage warning` | 0 | `CLEANUP-WARNING` |
| `install-completed-with-cleanup-warning` | `preserve-only install/reinstall` | `completed_with_warnings` | `apply` | `true` | `install` | `request.candidate_digest` | `preserve-only` | true | false | `complete` | `publish-terminal-record` | `install/preserve-only retry` | `install-preserve terminal + one stage warning` | 0 | `CLEANUP-WARNING` |
| `update-completed` | `ready update` | `completed` | `apply` | `true` | `update` | `request.candidate_digest` | `preserve-only` | true | false | `complete` | `cleanup-stage` | `null` | `update terminal action set` | 0 | `NONE` |
| `update-completed-with-cleanup-warning` | `ready update` | `completed_with_warnings` | `apply` | `true` | `update` | `request.candidate_digest` | `preserve-only` | true | false | `complete` | `publish-terminal-record` | `update retry` | `update terminal + one stage warning` | 0 | `CLEANUP-WARNING` |
| `legacy-migration-completed` | `legacy migration` | `completed` | `apply` | `true` | `install` | `request.candidate_digest` | `preserve-only` | true | false | `complete` | `cleanup-stage` | `null` | `install-preserve terminal action set` | 0 | `NONE` |
| `legacy-migration-completed-with-cleanup-warning` | `legacy migration` | `completed_with_warnings` | `apply` | `true` | `install` | `request.candidate_digest` | `preserve-only` | true | false | `complete` | `publish-terminal-record` | `update retry` | `install-preserve terminal + one stage warning` | 0 | `CLEANUP-WARNING` |
| `uninstall-planned` | `ready dry-run` | `planned` | `dry-run` | `false` | `uninstall` | `record.candidate_digest` | `preserve-only` | false | false | `complete` | `preflight` | `null` | `AP-U-READY-PLAN` | 0 | `NONE` |
| `uninstall-planned` | `exact legacy dry-run` | `planned` | `dry-run` | `false` | `uninstall` | `legacy_fixture.aggregate_digest` | `preserve-only` | false | false | `complete` | `preflight` | `null` | `AP-U-LEGACY-PLAN` | 0 | `NONE` |
| `uninstall-planned` | `matching incomplete-uninstall dry-run` | `planned` | `dry-run` | `false` | `uninstall` | `record.candidate_digest` | `record.seed_policy=preserve-only` | false | false | `complete` | `preflight` | `null` | `AP-U-INCOMPLETE-PLAN` | 0 | `NONE` |
| `uninstall-already-absent` | `tooling-absent dry-run` | `planned` | `dry-run` | `false` | `uninstall` | `record.candidate_digest` | `preserve-only` | false | false | `complete` | `preflight` | `null` | `AP-U-ABSENT` | 0 | `NONE` |
| `uninstall-completed` | `ready apply` | `completed` | `apply` | `true` | `uninstall` | `record.candidate_digest` | `preserve-only` | true | false | `complete` | `cleanup-stage` | `null` | `AP-U-READY-TERM` | 0 | `NONE` |
| `uninstall-completed` | `exact legacy apply` | `completed` | `apply` | `true` | `uninstall` | `legacy_fixture.aggregate_digest` | `preserve-only` | true | false | `complete` | `cleanup-stage` | `null` | `AP-U-LEGACY-TERM` | 0 | `NONE` |
| `uninstall-completed` | `successful matching incomplete-uninstall resume apply` | `completed` | `apply` | `true` | `uninstall` | `record.candidate_digest` | `record.seed_policy=preserve-only` | true | false | `complete` | `cleanup-stage` | `null` | `AP-U-INCOMPLETE-TERM` | 0 | `NONE` |
| `uninstall-already-absent` | `tooling-absent apply` | `completed` | `apply` | `true` | `uninstall` | `record.candidate_digest` | `preserve-only` | false | false | `complete` | `preflight` | `null` | `AP-U-ABSENT` | 0 | `NONE` |
| `uninstall-completed-with-cleanup-warning` | `ready apply` | `completed_with_warnings` | `apply` | `true` | `uninstall` | `record.candidate_digest` | `preserve-only` | true | false | `complete` | `publish-terminal-record` | `uninstall retry` | `AP-U-READY-WARN` | 0 | `CLEANUP-WARNING` |
| `uninstall-completed-with-cleanup-warning` | `exact legacy apply` | `completed_with_warnings` | `apply` | `true` | `uninstall` | `legacy_fixture.aggregate_digest` | `preserve-only` | true | false | `complete` | `publish-terminal-record` | `uninstall retry` | `AP-U-LEGACY-WARN` | 0 | `CLEANUP-WARNING` |
| `uninstall-completed-with-cleanup-warning` | `matching incomplete-uninstall resume apply` | `completed_with_warnings` | `apply` | `true` | `uninstall` | `record.candidate_digest` | `record.seed_policy=preserve-only` | true | false | `complete` | `publish-terminal-record` | `uninstall retry` | `AP-U-INCOMPLETE-WARN` | 0 | `CLEANUP-WARNING` |
| `already-initialized` | `plain init on ready` | `blocked` | `apply` | `true` | `install` | `record.candidate_digest` | `record.seed_policy` | false | false | `preflight` | `request-validation` | `null` | `empty` | 1 | `NONE` |
| `already-initialized` | `plain init on exact legacy` | `blocked` | `apply` | `true` | `install` | `legacy_fixture.aggregate_digest` | `preserve-only` | false | false | `preflight` | `request-validation` | `null` | `empty` | 1 | `NONE` |
| `tooling-not-installed` | `uninstall dry-run on absent` | `blocked` | `dry-run` | `false` | `uninstall` | `null` | `preserve-only` | false | false | `preflight` | `request-validation` | `null` | `empty` | 1 | `NONE` |
| `tooling-not-installed` | `uninstall apply on absent` | `blocked` | `apply` | `true` | `uninstall` | `null` | `preserve-only` | false | false | `preflight` | `request-validation` | `null` | `empty` | 1 | `NONE` |
| `installation-record-invalid` | `apply invocation` | `blocked` | `apply` | `true` | `null` | `null` | `null` | false | false | `preflight` | `request-validation` | `null` | `empty` | 1 | `NONE` |
| `installation-record-state-inconsistent` | `apply invocation after valid record parse` | `blocked` | `apply` | `true` | `null` | `record.candidate_digest` | `record.seed_policy` | false | false | `preflight` | `request-validation` | `null` | `empty` | 1 | `NONE` |
| `installation-record-invalid` | `dry-run invocation` | `blocked` | `dry-run` | `false` | `null` | `null` | `null` | false | false | `preflight` | `request-validation` | `null` | `empty` | 1 | `NONE` |
| `installation-record-state-inconsistent` | `dry-run invocation after valid record parse` | `blocked` | `dry-run` | `false` | `null` | `record.candidate_digest` | `record.seed_policy` | false | false | `preflight` | `request-validation` | `null` | `empty` | 1 | `NONE` |
| `resume-operation-mismatch` | `apply request against incomplete record` | `blocked` | `apply` | `true` | `record.operation` | `record.candidate_digest` | `record.seed_policy` | false | false | `preflight` | `request-validation` | `null` | `empty` | 1 | `NONE` |
| `resume-operation-mismatch` | `uninstall dry-run against non-uninstall incomplete record` | `blocked` | `dry-run` | `false` | `record.operation` | `record.candidate_digest` | `record.seed_policy` | false | false | `preflight` | `request-validation` | `null` | `empty` | 1 | `NONE` |
| `resume-candidate-mismatch` | `install resume` | `blocked` | `apply` | `true` | `install` | `record.candidate_digest` | `record.seed_policy` | false | false | `candidate-staging` | `preflight` | `null` | `empty` | 1 | `NONE` |
| `resume-candidate-mismatch` | `update resume` | `blocked` | `apply` | `true` | `update` | `record.candidate_digest` | `preserve-only` | false | false | `candidate-staging` | `preflight` | `null` | `empty` | 1 | `NONE` |
| `resume-seed-policy-mismatch` | `install resume` | `blocked` | `apply` | `true` | `install` | `record.candidate_digest` | `record.seed_policy` | false | false | `preflight` | `request-validation` | `null` | `empty` | 1 | `NONE` |
| `candidate-invalid` | `install/create-if-absent` | `blocked` | `apply` | `true` | `install` | `null` | `create-if-absent` | false | false | `candidate-staging` | `preflight` | `null` | `empty` | 1 | `NONE` |
| `candidate-digest-mismatch` | `install/create-if-absent` | `blocked` | `apply` | `true` | `install` | `request.candidate_digest` | `create-if-absent` | false | false | `candidate-staging` | `preflight` | `null` | `empty` | 1 | `NONE` |
| `candidate-invalid` | `install/preserve-only` | `blocked` | `apply` | `true` | `install` | `null` | `preserve-only` | false | false | `candidate-staging` | `preflight` | `null` | `empty` | 1 | `NONE` |
| `candidate-digest-mismatch` | `install/preserve-only` | `blocked` | `apply` | `true` | `install` | `request.candidate_digest` | `preserve-only` | false | false | `candidate-staging` | `preflight` | `null` | `empty` | 1 | `NONE` |
| `candidate-invalid` | `update/preserve-only` | `blocked` | `apply` | `true` | `update` | `null` | `preserve-only` | false | false | `candidate-staging` | `preflight` | `null` | `empty` | 1 | `NONE` |
| `candidate-digest-mismatch` | `update/preserve-only` | `blocked` | `apply` | `true` | `update` | `request.candidate_digest` | `preserve-only` | false | false | `candidate-staging` | `preflight` | `null` | `empty` | 1 | `NONE` |
| `unsafe-repository-binding` | `apply` | `blocked` | `apply` | `true` | `null` | `null` | `null` | false | false | `preflight` | `request-validation` | `null` | `empty` | 1 | `NONE` |
| `unsafe-repository-binding` | `dry-run` | `blocked` | `dry-run` | `false` | `null` | `null` | `null` | false | false | `preflight` | `request-validation` | `null` | `empty` | 1 | `NONE` |
| `unsafe-parent-binding` | `install/create-if-absent` | `blocked` | `apply` | `true` | `install` | `null` | `create-if-absent` | false | false | `preflight` | `request-validation` | `null` | `empty` | 1 | `NONE` |
| `unsafe-parent-binding` | `install/preserve-only` | `blocked` | `apply` | `true` | `install` | `null` | `preserve-only` | false | false | `preflight` | `request-validation` | `null` | `empty` | 1 | `NONE` |
| `unsafe-parent-binding` | `update` | `blocked` | `apply` | `true` | `update` | `null` | `preserve-only` | false | false | `preflight` | `request-validation` | `null` | `empty` | 1 | `NONE` |
| `unsafe-parent-binding` | `uninstall dry-run` | `blocked` | `dry-run` | `false` | `uninstall` | `null` | `preserve-only` | false | false | `preflight` | `request-validation` | `null` | `empty` | 1 | `NONE` |
| `unsafe-parent-binding` | `uninstall apply` | `blocked` | `apply` | `true` | `uninstall` | `null` | `preserve-only` | false | false | `preflight` | `request-validation` | `null` | `empty` | 1 | `NONE` |
| `unsafe-target-type` | `install/create-if-absent` | `blocked` | `apply` | `true` | `install` | `null` | `create-if-absent` | false | false | `preflight` | `request-validation` | `null` | `empty` | 1 | `NONE` |
| `unsafe-target-type` | `install/preserve-only` | `blocked` | `apply` | `true` | `install` | `null` | `preserve-only` | false | false | `preflight` | `request-validation` | `null` | `empty` | 1 | `NONE` |
| `unsafe-target-type` | `update` | `blocked` | `apply` | `true` | `update` | `null` | `preserve-only` | false | false | `preflight` | `request-validation` | `null` | `empty` | 1 | `NONE` |
| `unsafe-target-type` | `uninstall dry-run` | `blocked` | `dry-run` | `false` | `uninstall` | `null` | `preserve-only` | false | false | `preflight` | `request-validation` | `null` | `empty` | 1 | `NONE` |
| `unsafe-target-type` | `uninstall apply` | `blocked` | `apply` | `true` | `uninstall` | `null` | `preserve-only` | false | false | `preflight` | `request-validation` | `null` | `empty` | 1 | `NONE` |
| `foreign-tooling-root` | `install/create-if-absent` | `blocked` | `apply` | `true` | `install` | `null` | `create-if-absent` | false | false | `preflight` | `request-validation` | `null` | `empty` | 1 | `NONE` |
| `foreign-tooling-root` | `install/preserve-only` | `blocked` | `apply` | `true` | `install` | `null` | `preserve-only` | false | false | `preflight` | `request-validation` | `null` | `empty` | 1 | `NONE` |
| `foreign-tooling-root` | `update` | `blocked` | `apply` | `true` | `update` | `null` | `preserve-only` | false | false | `preflight` | `request-validation` | `null` | `empty` | 1 | `NONE` |
| `foreign-tooling-root` | `uninstall dry-run` | `blocked` | `dry-run` | `false` | `uninstall` | `null` | `preserve-only` | false | false | `preflight` | `request-validation` | `null` | `empty` | 1 | `NONE` |
| `foreign-tooling-root` | `uninstall apply` | `blocked` | `apply` | `true` | `uninstall` | `null` | `preserve-only` | false | false | `preflight` | `request-validation` | `null` | `empty` | 1 | `NONE` |
| `foreign-skill-slot` | `install/create-if-absent` | `blocked` | `apply` | `true` | `install` | `null` | `create-if-absent` | false | false | `preflight` | `request-validation` | `null` | `empty` | 1 | `NONE` |
| `foreign-skill-slot` | `install/preserve-only` | `blocked` | `apply` | `true` | `install` | `null` | `preserve-only` | false | false | `preflight` | `request-validation` | `null` | `empty` | 1 | `NONE` |
| `foreign-skill-slot` | `update` | `blocked` | `apply` | `true` | `update` | `null` | `preserve-only` | false | false | `preflight` | `request-validation` | `null` | `empty` | 1 | `NONE` |
| `foreign-skill-slot` | `uninstall dry-run` | `blocked` | `dry-run` | `false` | `uninstall` | `null` | `preserve-only` | false | false | `preflight` | `request-validation` | `null` | `empty` | 1 | `NONE` |
| `foreign-skill-slot` | `uninstall apply` | `blocked` | `apply` | `true` | `uninstall` | `null` | `preserve-only` | false | false | `preflight` | `request-validation` | `null` | `empty` | 1 | `NONE` |
| `atomic-rename-unavailable` | `install/create-if-absent` | `blocked` | `apply` | `true` | `install` | `null` | `create-if-absent` | false | false | `preflight` | `request-validation` | `null` | `empty` | 1 | `NONE` |
| `atomic-rename-unavailable` | `install/preserve-only` | `blocked` | `apply` | `true` | `install` | `null` | `preserve-only` | false | false | `preflight` | `request-validation` | `null` | `empty` | 1 | `NONE` |
| `atomic-rename-unavailable` | `update` | `blocked` | `apply` | `true` | `update` | `null` | `preserve-only` | false | false | `preflight` | `request-validation` | `null` | `empty` | 1 | `NONE` |
| `atomic-rename-unavailable` | `uninstall dry-run` | `blocked` | `dry-run` | `false` | `uninstall` | `null` | `preserve-only` | false | false | `preflight` | `request-validation` | `null` | `empty` | 1 | `NONE` |
| `atomic-rename-unavailable` | `uninstall apply` | `blocked` | `apply` | `true` | `uninstall` | `null` | `preserve-only` | false | false | `preflight` | `request-validation` | `null` | `empty` | 1 | `NONE` |
| `unsupported-legacy-version` | `init-force/update legacy path` | `blocked` | `apply` | `true` | `install` | `null` | `preserve-only` | false | false | `preflight` | `request-validation` | `null` | `empty` | 1 | `NONE` |
| `unsupported-legacy-version` | `uninstall legacy dry-run` | `blocked` | `dry-run` | `false` | `uninstall` | `null` | `preserve-only` | false | false | `preflight` | `request-validation` | `null` | `empty` | 1 | `NONE` |
| `unsupported-legacy-version` | `uninstall legacy apply` | `blocked` | `apply` | `true` | `uninstall` | `null` | `preserve-only` | false | false | `preflight` | `request-validation` | `null` | `empty` | 1 | `NONE` |
| `active-legacy-recovery` | `init-force/update legacy path` | `blocked` | `apply` | `true` | `install` | `null` | `preserve-only` | false | false | `preflight` | `request-validation` | `null` | `empty` | 1 | `NONE` |
| `active-legacy-recovery` | `uninstall legacy dry-run` | `blocked` | `dry-run` | `false` | `uninstall` | `null` | `preserve-only` | false | false | `preflight` | `request-validation` | `null` | `empty` | 1 | `NONE` |
| `active-legacy-recovery` | `uninstall legacy apply` | `blocked` | `apply` | `true` | `uninstall` | `null` | `preserve-only` | false | false | `preflight` | `request-validation` | `null` | `empty` | 1 | `NONE` |
| `modified-legacy-workspace` | `init-force/update legacy path` | `blocked` | `apply` | `true` | `install` | `null` | `preserve-only` | false | false | `preflight` | `request-validation` | `null` | `empty` | 1 | `NONE` |
| `modified-legacy-workspace` | `uninstall legacy dry-run` | `blocked` | `dry-run` | `false` | `uninstall` | `null` | `preserve-only` | false | false | `preflight` | `request-validation` | `null` | `empty` | 1 | `NONE` |
| `modified-legacy-workspace` | `uninstall legacy apply` | `blocked` | `apply` | `true` | `uninstall` | `null` | `preserve-only` | false | false | `preflight` | `request-validation` | `null` | `empty` | 1 | `NONE` |
| `stage-owner-mismatch` | `install/create-if-absent` | `blocked` | `apply` | `true` | `install` | `request.candidate_digest` | `create-if-absent` | false | false | `candidate-staging` | `preflight` | `null` | `empty` | 1 | `NONE` |
| `stage-owner-mismatch` | `install/preserve-only` | `blocked` | `apply` | `true` | `install` | `request.candidate_digest` | `preserve-only` | false | false | `candidate-staging` | `preflight` | `null` | `empty` | 1 | `NONE` |
| `stage-owner-mismatch` | `update` | `blocked` | `apply` | `true` | `update` | `request.candidate_digest` | `preserve-only` | false | false | `candidate-staging` | `preflight` | `null` | `empty` | 1 | `NONE` |
| `stage-owner-mismatch` | `uninstall dry-run` | `blocked` | `dry-run` | `false` | `uninstall` | `record.candidate_digest` | `preserve-only` | false | false | `candidate-staging` | `preflight` | `null` | `empty` | 1 | `NONE` |
| `stage-owner-mismatch` | `uninstall apply` | `blocked` | `apply` | `true` | `uninstall` | `record.candidate_digest` | `preserve-only` | false | false | `candidate-staging` | `preflight` | `null` | `empty` | 1 | `NONE` |
| `bootstrap-container-conflict` | `fresh create policy before accepted creation` | `blocked` | `apply` | `true` | `install` | `request.candidate_digest` | `create-if-absent` | false | false | `bootstrap-container` | `candidate-staging` | `null` | `empty` | 1 | `NONE` |
| `bootstrap-container-conflict` | `preserve-only install before accepted creation` | `blocked` | `apply` | `true` | `install` | `request.candidate_digest` | `preserve-only` | false | false | `bootstrap-container` | `candidate-staging` | `null` | `empty` | 1 | `NONE` |
| `bootstrap-container-conflict` | `created container fully rolled back` | `blocked` | `apply` | `true` | `install` | `request.candidate_digest` | `create-if-absent` | false | true | `bootstrap-container` | `candidate-staging` | `null` | `empty` | 1 | `NONE` |
| `bootstrap-cleanup-failed` | `install/create-if-absent` | `partial_failure` | `apply` | `true` | `install` | `request.candidate_digest` | `create-if-absent` | true | false | `bootstrap-container` | `candidate-staging` | `install/create-if-absent retry` | `bootstrap cleanup-failed action set` | 1 | `LIFECYCLE-RETRY` |
| `bootstrap-cleanup-failed` | `install/preserve-only` | `partial_failure` | `apply` | `true` | `install` | `request.candidate_digest` | `preserve-only` | true | false | `bootstrap-container` | `candidate-staging` | `install/preserve-only retry` | `bootstrap cleanup-failed action set` | 1 | `LIFECYCLE-RETRY` |
| `terminal-cleanup-completed` | desired `init; specs_mode=null` | `completed` | `apply` | `true` | `active.operation` | `active.candidate_digest` | `active.seed_policy` | true | false | `complete` | `cleanup-stage` | `null` | `terminal cleanup completed action set` | 0 | `CLEANUP-COMPLETED-DEFERRED` |
| `terminal-cleanup-completed` | desired `init --force; specs_mode=null` | `completed` | `apply` | `true` | `active.operation` | `active.candidate_digest` | `active.seed_policy` | true | false | `complete` | `cleanup-stage` | `null` | `terminal cleanup completed action set` | 0 | `CLEANUP-COMPLETED-DEFERRED` |
| `terminal-cleanup-completed` | desired `update; specs_mode=null` | `completed` | `apply` | `true` | `active.operation` | `active.candidate_digest` | `active.seed_policy` | true | false | `complete` | `cleanup-stage` | `null` | `terminal cleanup completed action set` | 0 | `CLEANUP-COMPLETED-DEFERRED` |
| `terminal-cleanup-completed` | desired `uninstall dry-run default; specs_mode=null` | `completed` | `dry-run` | `false` | `active.operation` | `active.candidate_digest` | `active.seed_policy` | true | false | `complete` | `cleanup-stage` | `null` | `terminal cleanup completed action set` | 0 | `CLEANUP-COMPLETED-DEFERRED` |
| `terminal-cleanup-completed` | desired `uninstall dry-run keep; specs_mode=keep` | `completed` | `dry-run` | `false` | `active.operation` | `active.candidate_digest` | `active.seed_policy` | true | false | `complete` | `cleanup-stage` | `null` | `terminal cleanup completed action set` | 0 | `CLEANUP-COMPLETED-DEFERRED` |
| `terminal-cleanup-completed` | desired `uninstall apply default; specs_mode=null` | `completed` | `apply` | `true` | `active.operation` | `active.candidate_digest` | `active.seed_policy` | true | false | `complete` | `cleanup-stage` | `null` | `terminal cleanup completed action set` | 0 | `CLEANUP-COMPLETED-DEFERRED` |
| `terminal-cleanup-completed` | desired `uninstall apply keep; specs_mode=keep` | `completed` | `apply` | `true` | `active.operation` | `active.candidate_digest` | `active.seed_policy` | true | false | `complete` | `cleanup-stage` | `null` | `terminal cleanup completed action set` | 0 | `CLEANUP-COMPLETED-DEFERRED` |
| `terminal-cleanup-failed` | desired `init; specs_mode=null` | `partial_failure` | `apply` | `true` | `active.operation` | `active.candidate_digest` | `active.seed_policy` | true | false | `cleanup-stage` | `publish-terminal-record` | `active.cleanup_retry_command` | `terminal cleanup retry-failed action set` | 1 | `CLEANUP-FAILED-DEFERRED` |
| `terminal-cleanup-failed` | desired `init --force; specs_mode=null` | `partial_failure` | `apply` | `true` | `active.operation` | `active.candidate_digest` | `active.seed_policy` | true | false | `cleanup-stage` | `publish-terminal-record` | `active.cleanup_retry_command` | `terminal cleanup retry-failed action set` | 1 | `CLEANUP-FAILED-DEFERRED` |
| `terminal-cleanup-failed` | desired `update; specs_mode=null` | `partial_failure` | `apply` | `true` | `active.operation` | `active.candidate_digest` | `active.seed_policy` | true | false | `cleanup-stage` | `publish-terminal-record` | `active.cleanup_retry_command` | `terminal cleanup retry-failed action set` | 1 | `CLEANUP-FAILED-DEFERRED` |
| `terminal-cleanup-failed` | desired `uninstall dry-run default; specs_mode=null` | `partial_failure` | `dry-run` | `false` | `active.operation` | `active.candidate_digest` | `active.seed_policy` | true | false | `cleanup-stage` | `publish-terminal-record` | `active.cleanup_retry_command` | `terminal cleanup retry-failed action set` | 1 | `CLEANUP-FAILED-DEFERRED` |
| `terminal-cleanup-failed` | desired `uninstall dry-run keep; specs_mode=keep` | `partial_failure` | `dry-run` | `false` | `active.operation` | `active.candidate_digest` | `active.seed_policy` | true | false | `cleanup-stage` | `publish-terminal-record` | `active.cleanup_retry_command` | `terminal cleanup retry-failed action set` | 1 | `CLEANUP-FAILED-DEFERRED` |
| `terminal-cleanup-failed` | desired `uninstall apply default; specs_mode=null` | `partial_failure` | `apply` | `true` | `active.operation` | `active.candidate_digest` | `active.seed_policy` | true | false | `cleanup-stage` | `publish-terminal-record` | `active.cleanup_retry_command` | `terminal cleanup retry-failed action set` | 1 | `CLEANUP-FAILED-DEFERRED` |
| `terminal-cleanup-failed` | desired `uninstall apply keep; specs_mode=keep` | `partial_failure` | `apply` | `true` | `active.operation` | `active.candidate_digest` | `active.seed_policy` | true | false | `cleanup-stage` | `publish-terminal-record` | `active.cleanup_retry_command` | `terminal cleanup retry-failed action set` | 1 | `CLEANUP-FAILED-DEFERRED` |
| `terminal-cleanup-completed` | `cleanup-retry init-force token; specs_mode=null` | `completed` | `apply` | `true` | `active.operation` | `active.candidate_digest` | `active.seed_policy` | true | false | `complete` | `cleanup-stage` | `null` | `terminal cleanup completed action set` | 0 | `CLEANUP-COMPLETED-BY-ROLE-AND-DEFERRED` |
| `terminal-cleanup-completed` | `cleanup-retry update token; specs_mode=null` | `completed` | `apply` | `true` | `active.operation` | `active.candidate_digest` | `active.seed_policy` | true | false | `complete` | `cleanup-stage` | `null` | `terminal cleanup completed action set` | 0 | `CLEANUP-COMPLETED-BY-ROLE-AND-DEFERRED` |
| `terminal-cleanup-completed` | `cleanup-retry uninstall-apply-keep token; specs_mode=keep` | `completed` | `apply` | `true` | `active.operation` | `active.candidate_digest` | `active.seed_policy` | true | false | `complete` | `cleanup-stage` | `null` | `terminal cleanup completed action set` | 0 | `CLEANUP-COMPLETED-BY-ROLE-AND-DEFERRED` |
| `terminal-cleanup-failed` | `cleanup-retry init-force token; specs_mode=null` | `partial_failure` | `apply` | `true` | `active.operation` | `active.candidate_digest` | `active.seed_policy` | true | false | `cleanup-stage` | `publish-terminal-record` | `active.cleanup_retry_command` | `terminal cleanup retry-failed action set` | 1 | `CLEANUP-FAILED-BY-ROLE-AND-DEFERRED` |
| `terminal-cleanup-failed` | `cleanup-retry update token; specs_mode=null` | `partial_failure` | `apply` | `true` | `active.operation` | `active.candidate_digest` | `active.seed_policy` | true | false | `cleanup-stage` | `publish-terminal-record` | `active.cleanup_retry_command` | `terminal cleanup retry-failed action set` | 1 | `CLEANUP-FAILED-BY-ROLE-AND-DEFERRED` |
| `terminal-cleanup-failed` | `cleanup-retry uninstall-apply-keep token; specs_mode=keep` | `partial_failure` | `apply` | `true` | `active.operation` | `active.candidate_digest` | `active.seed_policy` | true | false | `cleanup-stage` | `publish-terminal-record` | `active.cleanup_retry_command` | `terminal cleanup retry-failed action set` | 1 | `CLEANUP-FAILED-BY-ROLE-AND-DEFERRED` |
| `install-partial-failure` | `install/create-if-absent/publish-docs` | `partial_failure` | `apply` | `true` | `install` | `request.candidate_digest` | `create-if-absent` | true | false | `publish-docs` | `publish-incomplete-record` | `install/create-if-absent retry` | `exact install partial action set at publish-docs` | 1 | `LIFECYCLE-RETRY` |
| `install-partial-failure` | `install/create-if-absent/publish-templates` | `partial_failure` | `apply` | `true` | `install` | `request.candidate_digest` | `create-if-absent` | true | false | `publish-templates` | `publish-docs` | `install/create-if-absent retry` | `exact install partial action set at publish-templates` | 1 | `LIFECYCLE-RETRY` |
| `install-partial-failure` | `install/create-if-absent/publish-system` | `partial_failure` | `apply` | `true` | `install` | `request.candidate_digest` | `create-if-absent` | true | false | `publish-system` | `publish-templates` | `install/create-if-absent retry` | `exact install partial action set at publish-system` | 1 | `LIFECYCLE-RETRY` |
| `install-partial-failure` | `install/create-if-absent/publish-scripts` | `partial_failure` | `apply` | `true` | `install` | `request.candidate_digest` | `create-if-absent` | true | false | `publish-scripts` | `publish-system` | `install/create-if-absent retry` | `exact install partial action set at publish-scripts` | 1 | `LIFECYCLE-RETRY` |
| `install-partial-failure` | `install/create-if-absent/publish-slot-spec-dock` | `partial_failure` | `apply` | `true` | `install` | `request.candidate_digest` | `create-if-absent` | true | false | `publish-slot-spec-dock` | `publish-scripts` | `install/create-if-absent retry` | `exact install partial action set at publish-slot-spec-dock` | 1 | `LIFECYCLE-RETRY` |
| `install-partial-failure` | `install/create-if-absent/publish-slot-spec-dock-grill-with-docs` | `partial_failure` | `apply` | `true` | `install` | `request.candidate_digest` | `create-if-absent` | true | false | `publish-slot-spec-dock-grill-with-docs` | `publish-slot-spec-dock` | `install/create-if-absent retry` | `exact install partial action set at publish-slot-spec-dock-grill-with-docs` | 1 | `LIFECYCLE-RETRY` |
| `install-partial-failure` | `install/create-if-absent/create-seed-spec-dock-gitignore` | `partial_failure` | `apply` | `true` | `install` | `request.candidate_digest` | `create-if-absent` | true | false | `create-seed-spec-dock-gitignore` | `publish-slot-spec-dock-grill-with-docs` | `install/create-if-absent retry` | `exact install partial action set at create-seed-spec-dock-gitignore` | 1 | `LIFECYCLE-RETRY` |
| `install-partial-failure` | `install/create-if-absent/create-seed-consumer-ci` | `partial_failure` | `apply` | `true` | `install` | `request.candidate_digest` | `create-if-absent` | true | false | `create-seed-consumer-ci` | `create-seed-spec-dock-gitignore` | `install/create-if-absent retry` | `exact install partial action set at create-seed-consumer-ci` | 1 | `LIFECYCLE-RETRY` |
| `install-partial-failure` | `install/create-if-absent/verify-target` | `partial_failure` | `apply` | `true` | `install` | `request.candidate_digest` | `create-if-absent` | true | false | `verify-target` | `create-seed-consumer-ci` | `install/create-if-absent retry` | `exact install partial action set at verify-target` | 1 | `LIFECYCLE-RETRY` |
| `install-partial-failure` | `install/create-if-absent/publish-terminal-record` | `partial_failure` | `apply` | `true` | `install` | `request.candidate_digest` | `create-if-absent` | true | false | `publish-terminal-record` | `verify-target` | `install/create-if-absent retry` | `exact install partial action set at publish-terminal-record` | 1 | `LIFECYCLE-RETRY` |
| `install-partial-failure` | `install/preserve-only/publish-docs` | `partial_failure` | `apply` | `true` | `install` | `request.candidate_digest` | `preserve-only` | true | false | `publish-docs` | `publish-incomplete-record` | `install/preserve-only retry` | `exact install partial action set at publish-docs` | 1 | `LIFECYCLE-RETRY` |
| `install-partial-failure` | `install/preserve-only/publish-templates` | `partial_failure` | `apply` | `true` | `install` | `request.candidate_digest` | `preserve-only` | true | false | `publish-templates` | `publish-docs` | `install/preserve-only retry` | `exact install partial action set at publish-templates` | 1 | `LIFECYCLE-RETRY` |
| `install-partial-failure` | `install/preserve-only/publish-system` | `partial_failure` | `apply` | `true` | `install` | `request.candidate_digest` | `preserve-only` | true | false | `publish-system` | `publish-templates` | `install/preserve-only retry` | `exact install partial action set at publish-system` | 1 | `LIFECYCLE-RETRY` |
| `install-partial-failure` | `install/preserve-only/publish-scripts` | `partial_failure` | `apply` | `true` | `install` | `request.candidate_digest` | `preserve-only` | true | false | `publish-scripts` | `publish-system` | `install/preserve-only retry` | `exact install partial action set at publish-scripts` | 1 | `LIFECYCLE-RETRY` |
| `install-partial-failure` | `install/preserve-only/publish-slot-spec-dock` | `partial_failure` | `apply` | `true` | `install` | `request.candidate_digest` | `preserve-only` | true | false | `publish-slot-spec-dock` | `publish-scripts` | `install/preserve-only retry` | `exact install partial action set at publish-slot-spec-dock` | 1 | `LIFECYCLE-RETRY` |
| `install-partial-failure` | `install/preserve-only/publish-slot-spec-dock-grill-with-docs` | `partial_failure` | `apply` | `true` | `install` | `request.candidate_digest` | `preserve-only` | true | false | `publish-slot-spec-dock-grill-with-docs` | `publish-slot-spec-dock` | `install/preserve-only retry` | `exact install partial action set at publish-slot-spec-dock-grill-with-docs` | 1 | `LIFECYCLE-RETRY` |
| `install-partial-failure` | `install/preserve-only/verify-target` | `partial_failure` | `apply` | `true` | `install` | `request.candidate_digest` | `preserve-only` | true | false | `verify-target` | `publish-slot-spec-dock-grill-with-docs` | `install/preserve-only retry` | `exact install partial action set at verify-target` | 1 | `LIFECYCLE-RETRY` |
| `install-partial-failure` | `install/preserve-only/publish-terminal-record` | `partial_failure` | `apply` | `true` | `install` | `request.candidate_digest` | `preserve-only` | true | false | `publish-terminal-record` | `verify-target` | `install/preserve-only retry` | `exact install partial action set at publish-terminal-record` | 1 | `LIFECYCLE-RETRY` |
| `update-partial-failure` | `update/preserve-only/publish-docs` | `partial_failure` | `apply` | `true` | `update` | `request.candidate_digest` | `preserve-only` | true | false | `publish-docs` | `publish-incomplete-record` | `update retry` | `exact update partial action set at publish-docs` | 1 | `LIFECYCLE-RETRY` |
| `update-partial-failure` | `update/preserve-only/publish-templates` | `partial_failure` | `apply` | `true` | `update` | `request.candidate_digest` | `preserve-only` | true | false | `publish-templates` | `publish-docs` | `update retry` | `exact update partial action set at publish-templates` | 1 | `LIFECYCLE-RETRY` |
| `update-partial-failure` | `update/preserve-only/publish-system` | `partial_failure` | `apply` | `true` | `update` | `request.candidate_digest` | `preserve-only` | true | false | `publish-system` | `publish-templates` | `update retry` | `exact update partial action set at publish-system` | 1 | `LIFECYCLE-RETRY` |
| `update-partial-failure` | `update/preserve-only/publish-scripts` | `partial_failure` | `apply` | `true` | `update` | `request.candidate_digest` | `preserve-only` | true | false | `publish-scripts` | `publish-system` | `update retry` | `exact update partial action set at publish-scripts` | 1 | `LIFECYCLE-RETRY` |
| `update-partial-failure` | `update/preserve-only/publish-slot-spec-dock` | `partial_failure` | `apply` | `true` | `update` | `request.candidate_digest` | `preserve-only` | true | false | `publish-slot-spec-dock` | `publish-scripts` | `update retry` | `exact update partial action set at publish-slot-spec-dock` | 1 | `LIFECYCLE-RETRY` |
| `update-partial-failure` | `update/preserve-only/publish-slot-spec-dock-grill-with-docs` | `partial_failure` | `apply` | `true` | `update` | `request.candidate_digest` | `preserve-only` | true | false | `publish-slot-spec-dock-grill-with-docs` | `publish-slot-spec-dock` | `update retry` | `exact update partial action set at publish-slot-spec-dock-grill-with-docs` | 1 | `LIFECYCLE-RETRY` |
| `update-partial-failure` | `update/preserve-only/verify-target` | `partial_failure` | `apply` | `true` | `update` | `request.candidate_digest` | `preserve-only` | true | false | `verify-target` | `publish-slot-spec-dock-grill-with-docs` | `update retry` | `exact update partial action set at verify-target` | 1 | `LIFECYCLE-RETRY` |
| `update-partial-failure` | `update/preserve-only/publish-terminal-record` | `partial_failure` | `apply` | `true` | `update` | `request.candidate_digest` | `preserve-only` | true | false | `publish-terminal-record` | `verify-target` | `update retry` | `exact update partial action set at publish-terminal-record` | 1 | `LIFECYCLE-RETRY` |
| `uninstall-partial-failure` | `uninstall/preserve-only/detach-docs` | `partial_failure` | `apply` | `true` | `uninstall` | `record.candidate_digest` | `preserve-only` | true | false | `detach-docs` | `publish-incomplete-record` | `uninstall retry` | `exact uninstall partial action set at detach-docs` | 1 | `LIFECYCLE-RETRY` |
| `uninstall-partial-failure` | `uninstall/preserve-only/detach-templates` | `partial_failure` | `apply` | `true` | `uninstall` | `record.candidate_digest` | `preserve-only` | true | false | `detach-templates` | `detach-docs` | `uninstall retry` | `exact uninstall partial action set at detach-templates` | 1 | `LIFECYCLE-RETRY` |
| `uninstall-partial-failure` | `uninstall/preserve-only/detach-system` | `partial_failure` | `apply` | `true` | `uninstall` | `record.candidate_digest` | `preserve-only` | true | false | `detach-system` | `detach-templates` | `uninstall retry` | `exact uninstall partial action set at detach-system` | 1 | `LIFECYCLE-RETRY` |
| `uninstall-partial-failure` | `uninstall/preserve-only/detach-scripts` | `partial_failure` | `apply` | `true` | `uninstall` | `record.candidate_digest` | `preserve-only` | true | false | `detach-scripts` | `detach-system` | `uninstall retry` | `exact uninstall partial action set at detach-scripts` | 1 | `LIFECYCLE-RETRY` |
| `uninstall-partial-failure` | `uninstall/preserve-only/detach-slot-spec-dock` | `partial_failure` | `apply` | `true` | `uninstall` | `record.candidate_digest` | `preserve-only` | true | false | `detach-slot-spec-dock` | `detach-scripts` | `uninstall retry` | `exact uninstall partial action set at detach-slot-spec-dock` | 1 | `LIFECYCLE-RETRY` |
| `uninstall-partial-failure` | `uninstall/preserve-only/detach-slot-spec-dock-grill-with-docs` | `partial_failure` | `apply` | `true` | `uninstall` | `record.candidate_digest` | `preserve-only` | true | false | `detach-slot-spec-dock-grill-with-docs` | `detach-slot-spec-dock` | `uninstall retry` | `exact uninstall partial action set at detach-slot-spec-dock-grill-with-docs` | 1 | `LIFECYCLE-RETRY` |
| `uninstall-partial-failure` | `uninstall/preserve-only/verify-target` | `partial_failure` | `apply` | `true` | `uninstall` | `record.candidate_digest` | `preserve-only` | true | false | `verify-target` | `detach-slot-spec-dock-grill-with-docs` | `uninstall retry` | `exact uninstall partial action set at verify-target` | 1 | `LIFECYCLE-RETRY` |
| `uninstall-partial-failure` | `uninstall/preserve-only/publish-terminal-record` | `partial_failure` | `apply` | `true` | `uninstall` | `record.candidate_digest` | `preserve-only` | true | false | `publish-terminal-record` | `verify-target` | `uninstall retry` | `exact uninstall partial action set at publish-terminal-record` | 1 | `LIFECYCLE-RETRY` |
| `invalid-request` | `any apply request` | `error` | `apply` | `true` | `null` | `null` | `null` | false | false | `request-validation` | `not-started` | `null` | `empty` | 2 | `NONE` |
| `invalid-request` | `uninstall dry-run request` | `error` | `dry-run` | `false` | `null` | `null` | `null` | false | false | `request-validation` | `not-started` | `null` | `empty` | 2 | `NONE` |
| `spec-history-purge-removed` | `uninstall remove dry-run` | `error` | `dry-run` | `false` | `null` | `null` | `null` | false | false | `request-validation` | `not-started` | `null` | `empty` | 2 | `NONE` |
| `spec-history-purge-removed` | `uninstall remove apply` | `error` | `apply` | `true` | `null` | `null` | `null` | false | false | `request-validation` | `not-started` | `null` | `empty` | 2 | `NONE` |

No other code/variant/relation is valid.
## 11. Retry, continuation, messages and guidance

### WIR-TEXT-001 — Retry and invocation commands

| Token | Exact value |
|---|---|
| install/create-if-absent retry | `spec-dock init --force -- ${QUOTED_TARGET}` |
| install/preserve-only retry | `spec-dock update -- ${QUOTED_TARGET}` |
| update retry | `spec-dock update -- ${QUOTED_TARGET}` |
| uninstall retry | `spec-dock uninstall --apply --keep-specs -- ${QUOTED_TARGET}` |
| active.cleanup_retry_command | Select the result-family base command, insert exact `--provider-cleanup-token ${ACTIVE_CLEANUP_TOKEN}` before `--`, and preserve public flags/order exactly as WIR-CLEANUP-001 |
| render(`init`) | `spec-dock init -- ${QUOTED_TARGET}` |
| render(`init-force`) | `spec-dock init --force -- ${QUOTED_TARGET}` |
| render(`update`) | `spec-dock update -- ${QUOTED_TARGET}` |
| render(`uninstall-dry-run`) | `spec-dock uninstall -- ${QUOTED_TARGET}` |
| render(`uninstall-dry-run-keep`) | `spec-dock uninstall --keep-specs -- ${QUOTED_TARGET}` |
| render(`uninstall-apply`) | `spec-dock uninstall --apply -- ${QUOTED_TARGET}` |
| render(`uninstall-apply-keep`) | `spec-dock uninstall --apply --keep-specs -- ${QUOTED_TARGET}` |
| null | JSON null |

`${QUOTED_TARGET}` is `shlex.join([normalized_target])`; `${ACTIVE_CLEANUP_TOKEN}` is exact `active.cleanup_token`. Callers act only on `continuation`; `retry_command` is a compatibility echo. Cleanup failure independently conveys cleanup retry and optional desired-after-cleanup command.

### WIR-TEXT-002 — Exact diagnostics

Cleanup warning: `Provider tooling reached the requested terminal state, but the owned external stage could not be removed.`

| Code | Exact error string |
|---|---|
| `already-initialized` | `SpecDock tooling is already installed; use init --force or update.` |
| `tooling-not-installed` | `SpecDock tooling is not installed for this target.` |
| `installation-record-invalid` | `The SpecDock installation record is invalid.` |
| `installation-record-state-inconsistent` | `The SpecDock installation record does not match the observed tooling state.` |
| `resume-operation-mismatch` | `The incomplete operation can be resumed only with the same operation.` |
| `resume-candidate-mismatch` | `The incomplete operation can be resumed only with the same candidate digest.` |
| `resume-seed-policy-mismatch` | `The incomplete operation can be resumed only with the same seed policy.` |
| `candidate-invalid` | `The packaged provider candidate is invalid.` |
| `candidate-digest-mismatch` | `The staged provider candidate digest does not match the packaged candidate.` |
| `unsafe-repository-binding` | `The repository root binding is unsafe or changed during the operation.` |
| `unsafe-parent-binding` | `A required parent directory binding is unsafe or changed during the operation.` |
| `unsafe-target-type` | `A fixed provider target has an unsupported filesystem type.` |
| `foreign-tooling-root` | `A fixed tooling root exists without provider ownership evidence.` |
| `foreign-skill-slot` | `A fixed skill slot exists without matching provider ownership evidence.` |
| `unsupported-legacy-version` | `This legacy SpecDock version is not eligible for automatic migration.` |
| `active-legacy-recovery` | `Legacy recovery evidence is active; complete recovery with the last compatible package before migration.` |
| `modified-legacy-workspace` | `The legacy 0.2.3 tooling payload is not an exact clean migration source.` |
| `atomic-rename-unavailable` | `The required native atomic rename primitive is unavailable.` |
| `stage-owner-mismatch` | `The existing provider stage does not match this repository, operation, candidate, and seed policy.` |
| `bootstrap-container-conflict` | `The shared spec-dock container cannot be safely created or bound.` |
| `bootstrap-cleanup-failed` | `The fresh container bootstrap failed and could not be restored to the exact absent pre-state.` |
| `terminal-cleanup-failed` | `The requested tooling state is durable, but owned stage cleanup failed; follow the continuation object exactly.` |
| `install-partial-failure` | `SpecDock install stopped after durable mutation; rerun the exact retry command.` |
| `update-partial-failure` | `SpecDock update stopped after durable mutation; rerun the exact retry command.` |
| `uninstall-partial-failure` | `SpecDock uninstall stopped after durable mutation; rerun the exact retry command.` |
| `invalid-request` | `The SpecDock lifecycle request is invalid.` |
| `spec-history-purge-removed` | `Spec history purge has been removed; uninstall is tooling-only.` |

Success/planned codes, including `terminal-cleanup-completed`, have no error. Cleanup-warning codes have exactly one warning and no error. All other codes have warnings empty and exactly the listed error.

### WIR-TEXT-003 — Guidance

- `active-legacy-recovery`: `Run the last compatible SpecDock package with the same legacy operation until its recovery markers are cleared.` then `Do not delete, rename, or convert legacy recovery files manually.`
- Lifecycle partial: `Run continuation.next_command to resume the exact lifecycle operation.` then `Do not switch operation, candidate package, or seed policy.`
- Cleanup warning: `Run continuation.next_command to finish owned stage cleanup.` then `The requested terminal tooling state is already durable.`
- Cleanup failure with deferred request: `Run continuation.next_command to retry owned stage cleanup.` then `After cleanup succeeds, run continuation.after_cleanup_command.` then `The requested terminal tooling state is already durable.`
- Cleanup failure without deferred request: `Run continuation.next_command to retry owned stage cleanup.` then `No lifecycle request is pending after cleanup.` then `The requested terminal tooling state is already durable.`
- Cleanup success with deferred request: `Owned provider stage cleanup completed; no lifecycle operation was executed.` then `Run continuation.next_command to execute the preserved requested operation.`
- Cleanup success without deferred request: `Owned provider stage cleanup completed; no lifecycle operation was executed.` then `No lifecycle operation is pending.`
- `spec-history-purge-removed`: `Use tooling-only uninstall without --remove-specs.` then `Spec history and Workbench data remain consumer-owned.`
- Every other code: empty array.

## 12. Action wire

Exact keys/order `path,category,status,reason`; all non-null strings.

| Category | Reason | Allowed status | Operation/policy |
|---|---|---|---|
| container | fresh-container-create | planned,completed,pending,failed | install |
| container | shared-container-preserve | preserved | install,update,uninstall |
| record | incomplete-record-publish | planned,completed,pending,failed | install,update,uninstall |
| record | terminal-record-publish | planned,completed,pending,failed | install,update,uninstall |
| record | terminal-record-current | preserved | uninstall |
| root | candidate-root-create | planned,completed,pending,failed | install,update |
| root | candidate-root-replace | planned,completed,pending,failed | install,update |
| root | candidate-root-current | preserved | install,update |
| root | owned-root-remove | planned,completed,pending,failed | uninstall |
| root | owned-root-absent | preserved | uninstall |
| slot | candidate-slot-create | planned,completed,pending,failed | install,update |
| slot | candidate-slot-replace | planned,completed,pending,failed | install,update |
| slot | candidate-slot-current | preserved | install,update |
| slot | owned-slot-remove | planned,completed,pending,failed | uninstall |
| slot | owned-slot-absent | preserved | uninstall |
| seed | fresh-seed-create | planned,completed,pending,failed | install/create-if-absent |
| seed | consumer-seed-present | preserved | install/create-if-absent |
| seed | preserve-only-seed | preserved | install/update/uninstall preserve-only |
| stage | candidate-stage-create | completed,pending,failed | install,update,uninstall |
| stage | candidate-stage-reuse | preserved | install,update,uninstall |
| stage | candidate-stage-cleanup | completed,pending,failed | install,update,uninstall,terminal-cleanup |
| stage | candidate-stage-cleanup-warning | warning | install,update,uninstall |
| preservation | consumer-data-preserve | preserved | install,update,uninstall |


### WIR-ACT-005 — Closed uninstall action profiles

The `Actions` values `AP-U-*` in §10 are exact finite functions, not extension tokens.

- `AP-U-READY-PLAN`: shared container and two seeds are preserved; record, four present roots and two present slots are planned for terminal publish/removal.
- `AP-U-LEGACY-PLAN`: same rows/order as ready plan, with legacy ownership evidence and legacy aggregate digest.
- `AP-U-INCOMPLETE-PLAN`: container and seeds are preserved; record is planned with `terminal-record-publish`; each already-absent owned root/slot is preserved with `owned-root-absent`/`owned-slot-absent`; each still-present owned root/slot is planned for removal. At least one target is already absent or the state is not incomplete.
- `AP-U-ABSENT`: exactly four preserved actions: shared container, current terminal record, `spec-dock/.gitignore`, `.github/workflows/ci.yml`.
- `AP-U-READY-TERM` and `AP-U-LEGACY-TERM`: shared container and seeds preserved; record and all present roots/slots completed; stage cleanup completed.
- `AP-U-INCOMPLETE-TERM`: same finite target rows as the incomplete plan; previously absent roots/slots are preserved, still-present roots/slots and terminal record are completed, and stage cleanup is completed.
- `AP-U-READY-WARN`, `AP-U-LEGACY-WARN`, `AP-U-INCOMPLETE-WARN`: corresponding terminal profile with exactly one additional `@provider-stage` warning action and no completed stage-cleanup action.

All root/slot decisions are computed from the descriptor-bound observation captured for the accepted state. No unknown target, duplicate action or alternative reason is permitted.

Finite action profiles:

1. Planned uninstall emits container/record/existing owned roots/slots/seeds/preservation in target order.
2. Completed emits the same finite authorized rows with completed/preserved statuses.
3. Cleanup warning differs only by one `@provider-stage` warning row.
4. For root/slot/seed publication/detach partials, exactly the current path is failed; prior authorized paths completed/preserved; later authorized paths pending. For `publish-terminal-record`, the record row is failed with `terminal-record-publish` and the prior incomplete record is not a second row. For `verify-target`, every and only mismatching fixed root/slot is failed, matching rows completed/preserved, stage pending. Skipped preserve-only seed phases emit no action.
5. Bootstrap cleanup-failed has failed `spec-dock/fresh-container-create`, pending stage cleanup and later install rows.
6. `terminal-cleanup-completed` has exactly one action: `@provider-stage`, category `stage`, status `completed`, reason `candidate-stage-cleanup`; both path arrays are empty.
7. `terminal-cleanup-failed` has exactly one action: `@provider-stage`, category `stage`, status `failed`, reason `candidate-stage-cleanup`; `failed_paths=["@provider-stage"]`, `pending_paths=[]`.
8. `failed_paths`/`pending_paths` derive exactly from action statuses and target order. Blocked/error arrays are empty.

## 13. JSON goldens

Digest fixture is 64 lowercase `d` characters. Every block is independently parsed by the normative test and is serialized as the displayed compact line plus one LF.

### WIR-GOLDEN-U1 — Ready uninstall dry-run

```json
{"schema_version":1,"target":"/tmp/consumer","mode":"dry-run","apply":false,"specs_mode":null,"status":"planned","code":"uninstall-planned","operation":"uninstall","candidate_digest":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","seed_policy":"preserve-only","mutation_started":false,"bootstrap_rolled_back":false,"phase":"complete","last_completed_phase":"preflight","retry_command":null,"continuation":{"next_action":"none","next_command":null,"after_cleanup_action":"none","after_cleanup_command":null},"failed_paths":[],"pending_paths":[],"summary":{"planned":7,"completed":0,"preserved":3,"pending":0,"failed":0,"warnings":0},"actions":[{"path":"spec-dock","category":"container","status":"preserved","reason":"shared-container-preserve"},{"path":"spec-dock/spec-dock.version","category":"record","status":"planned","reason":"terminal-record-publish"},{"path":"spec-dock/docs","category":"root","status":"planned","reason":"owned-root-remove"},{"path":"spec-dock/templates","category":"root","status":"planned","reason":"owned-root-remove"},{"path":"spec-dock/system","category":"root","status":"planned","reason":"owned-root-remove"},{"path":"spec-dock/scripts","category":"root","status":"planned","reason":"owned-root-remove"},{"path":".agents/skills/spec-dock","category":"slot","status":"planned","reason":"owned-slot-remove"},{"path":".agents/skills/spec-dock-grill-with-docs","category":"slot","status":"planned","reason":"owned-slot-remove"},{"path":"spec-dock/.gitignore","category":"seed","status":"preserved","reason":"preserve-only-seed"},{"path":".github/workflows/ci.yml","category":"seed","status":"preserved","reason":"preserve-only-seed"}],"guidance":[],"warnings":[],"errors":[]}
```

### WIR-GOLDEN-U2 — Exact legacy uninstall dry-run

```json
{"schema_version":1,"target":"/tmp/consumer","mode":"dry-run","apply":false,"specs_mode":"keep","status":"planned","code":"uninstall-planned","operation":"uninstall","candidate_digest":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","seed_policy":"preserve-only","mutation_started":false,"bootstrap_rolled_back":false,"phase":"complete","last_completed_phase":"preflight","retry_command":null,"continuation":{"next_action":"none","next_command":null,"after_cleanup_action":"none","after_cleanup_command":null},"failed_paths":[],"pending_paths":[],"summary":{"planned":7,"completed":0,"preserved":3,"pending":0,"failed":0,"warnings":0},"actions":[{"path":"spec-dock","category":"container","status":"preserved","reason":"shared-container-preserve"},{"path":"spec-dock/spec-dock.version","category":"record","status":"planned","reason":"terminal-record-publish"},{"path":"spec-dock/docs","category":"root","status":"planned","reason":"owned-root-remove"},{"path":"spec-dock/templates","category":"root","status":"planned","reason":"owned-root-remove"},{"path":"spec-dock/system","category":"root","status":"planned","reason":"owned-root-remove"},{"path":"spec-dock/scripts","category":"root","status":"planned","reason":"owned-root-remove"},{"path":".agents/skills/spec-dock","category":"slot","status":"planned","reason":"owned-slot-remove"},{"path":".agents/skills/spec-dock-grill-with-docs","category":"slot","status":"planned","reason":"owned-slot-remove"},{"path":"spec-dock/.gitignore","category":"seed","status":"preserved","reason":"preserve-only-seed"},{"path":".github/workflows/ci.yml","category":"seed","status":"preserved","reason":"preserve-only-seed"}],"guidance":[],"warnings":[],"errors":[]}
```

### WIR-GOLDEN-U3 — Matching incomplete-uninstall dry-run

```json
{"schema_version":1,"target":"/tmp/consumer","mode":"dry-run","apply":false,"specs_mode":null,"status":"planned","code":"uninstall-planned","operation":"uninstall","candidate_digest":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","seed_policy":"preserve-only","mutation_started":false,"bootstrap_rolled_back":false,"phase":"complete","last_completed_phase":"preflight","retry_command":null,"continuation":{"next_action":"none","next_command":null,"after_cleanup_action":"none","after_cleanup_command":null},"failed_paths":[],"pending_paths":[],"summary":{"planned":6,"completed":0,"preserved":4,"pending":0,"failed":0,"warnings":0},"actions":[{"path":"spec-dock","category":"container","status":"preserved","reason":"shared-container-preserve"},{"path":"spec-dock/spec-dock.version","category":"record","status":"planned","reason":"terminal-record-publish"},{"path":"spec-dock/docs","category":"root","status":"preserved","reason":"owned-root-absent"},{"path":"spec-dock/templates","category":"root","status":"planned","reason":"owned-root-remove"},{"path":"spec-dock/system","category":"root","status":"planned","reason":"owned-root-remove"},{"path":"spec-dock/scripts","category":"root","status":"planned","reason":"owned-root-remove"},{"path":".agents/skills/spec-dock","category":"slot","status":"planned","reason":"owned-slot-remove"},{"path":".agents/skills/spec-dock-grill-with-docs","category":"slot","status":"planned","reason":"owned-slot-remove"},{"path":"spec-dock/.gitignore","category":"seed","status":"preserved","reason":"preserve-only-seed"},{"path":".github/workflows/ci.yml","category":"seed","status":"preserved","reason":"preserve-only-seed"}],"guidance":[],"warnings":[],"errors":[]}
```

### WIR-GOLDEN-U4 — Tooling-absent dry-run

```json
{"schema_version":1,"target":"/tmp/consumer","mode":"dry-run","apply":false,"specs_mode":null,"status":"planned","code":"uninstall-already-absent","operation":"uninstall","candidate_digest":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","seed_policy":"preserve-only","mutation_started":false,"bootstrap_rolled_back":false,"phase":"complete","last_completed_phase":"preflight","retry_command":null,"continuation":{"next_action":"none","next_command":null,"after_cleanup_action":"none","after_cleanup_command":null},"failed_paths":[],"pending_paths":[],"summary":{"planned":0,"completed":0,"preserved":4,"pending":0,"failed":0,"warnings":0},"actions":[{"path":"spec-dock","category":"container","status":"preserved","reason":"shared-container-preserve"},{"path":"spec-dock/spec-dock.version","category":"record","status":"preserved","reason":"terminal-record-current"},{"path":"spec-dock/.gitignore","category":"seed","status":"preserved","reason":"preserve-only-seed"},{"path":".github/workflows/ci.yml","category":"seed","status":"preserved","reason":"preserve-only-seed"}],"guidance":[],"warnings":[],"errors":[]}
```

### WIR-GOLDEN-U5 — Ready uninstall apply

```json
{"schema_version":1,"target":"/tmp/consumer","mode":"apply","apply":true,"specs_mode":"keep","status":"completed","code":"uninstall-completed","operation":"uninstall","candidate_digest":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","seed_policy":"preserve-only","mutation_started":true,"bootstrap_rolled_back":false,"phase":"complete","last_completed_phase":"cleanup-stage","retry_command":null,"continuation":{"next_action":"none","next_command":null,"after_cleanup_action":"none","after_cleanup_command":null},"failed_paths":[],"pending_paths":[],"summary":{"planned":0,"completed":7,"preserved":3,"pending":0,"failed":0,"warnings":0},"actions":[{"path":"spec-dock","category":"container","status":"preserved","reason":"shared-container-preserve"},{"path":"spec-dock/spec-dock.version","category":"record","status":"completed","reason":"terminal-record-publish"},{"path":"spec-dock/docs","category":"root","status":"completed","reason":"owned-root-remove"},{"path":"spec-dock/templates","category":"root","status":"completed","reason":"owned-root-remove"},{"path":"spec-dock/system","category":"root","status":"completed","reason":"owned-root-remove"},{"path":"spec-dock/scripts","category":"root","status":"completed","reason":"owned-root-remove"},{"path":".agents/skills/spec-dock","category":"slot","status":"completed","reason":"owned-slot-remove"},{"path":".agents/skills/spec-dock-grill-with-docs","category":"slot","status":"completed","reason":"owned-slot-remove"},{"path":"spec-dock/.gitignore","category":"seed","status":"preserved","reason":"preserve-only-seed"},{"path":".github/workflows/ci.yml","category":"seed","status":"preserved","reason":"preserve-only-seed"}],"guidance":[],"warnings":[],"errors":[]}
```

### WIR-GOLDEN-U6 — Exact legacy uninstall apply

```json
{"schema_version":1,"target":"/tmp/consumer","mode":"apply","apply":true,"specs_mode":null,"status":"completed","code":"uninstall-completed","operation":"uninstall","candidate_digest":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","seed_policy":"preserve-only","mutation_started":true,"bootstrap_rolled_back":false,"phase":"complete","last_completed_phase":"cleanup-stage","retry_command":null,"continuation":{"next_action":"none","next_command":null,"after_cleanup_action":"none","after_cleanup_command":null},"failed_paths":[],"pending_paths":[],"summary":{"planned":0,"completed":7,"preserved":3,"pending":0,"failed":0,"warnings":0},"actions":[{"path":"spec-dock","category":"container","status":"preserved","reason":"shared-container-preserve"},{"path":"spec-dock/spec-dock.version","category":"record","status":"completed","reason":"terminal-record-publish"},{"path":"spec-dock/docs","category":"root","status":"completed","reason":"owned-root-remove"},{"path":"spec-dock/templates","category":"root","status":"completed","reason":"owned-root-remove"},{"path":"spec-dock/system","category":"root","status":"completed","reason":"owned-root-remove"},{"path":"spec-dock/scripts","category":"root","status":"completed","reason":"owned-root-remove"},{"path":".agents/skills/spec-dock","category":"slot","status":"completed","reason":"owned-slot-remove"},{"path":".agents/skills/spec-dock-grill-with-docs","category":"slot","status":"completed","reason":"owned-slot-remove"},{"path":"spec-dock/.gitignore","category":"seed","status":"preserved","reason":"preserve-only-seed"},{"path":".github/workflows/ci.yml","category":"seed","status":"preserved","reason":"preserve-only-seed"}],"guidance":[],"warnings":[],"errors":[]}
```

### WIR-GOLDEN-U7 — Successful matching incomplete-uninstall resume

```json
{"schema_version":1,"target":"/tmp/consumer","mode":"apply","apply":true,"specs_mode":"keep","status":"completed","code":"uninstall-completed","operation":"uninstall","candidate_digest":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","seed_policy":"preserve-only","mutation_started":true,"bootstrap_rolled_back":false,"phase":"complete","last_completed_phase":"cleanup-stage","retry_command":null,"continuation":{"next_action":"none","next_command":null,"after_cleanup_action":"none","after_cleanup_command":null},"failed_paths":[],"pending_paths":[],"summary":{"planned":0,"completed":6,"preserved":4,"pending":0,"failed":0,"warnings":0},"actions":[{"path":"spec-dock","category":"container","status":"preserved","reason":"shared-container-preserve"},{"path":"spec-dock/spec-dock.version","category":"record","status":"completed","reason":"terminal-record-publish"},{"path":"spec-dock/docs","category":"root","status":"preserved","reason":"owned-root-absent"},{"path":"spec-dock/templates","category":"root","status":"completed","reason":"owned-root-remove"},{"path":"spec-dock/system","category":"root","status":"completed","reason":"owned-root-remove"},{"path":"spec-dock/scripts","category":"root","status":"completed","reason":"owned-root-remove"},{"path":".agents/skills/spec-dock","category":"slot","status":"completed","reason":"owned-slot-remove"},{"path":".agents/skills/spec-dock-grill-with-docs","category":"slot","status":"completed","reason":"owned-slot-remove"},{"path":"spec-dock/.gitignore","category":"seed","status":"preserved","reason":"preserve-only-seed"},{"path":".github/workflows/ci.yml","category":"seed","status":"preserved","reason":"preserve-only-seed"}],"guidance":[],"warnings":[],"errors":[]}
```

### WIR-GOLDEN-U8 — Tooling-absent apply

```json
{"schema_version":1,"target":"/tmp/consumer","mode":"apply","apply":true,"specs_mode":null,"status":"completed","code":"uninstall-already-absent","operation":"uninstall","candidate_digest":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","seed_policy":"preserve-only","mutation_started":false,"bootstrap_rolled_back":false,"phase":"complete","last_completed_phase":"preflight","retry_command":null,"continuation":{"next_action":"none","next_command":null,"after_cleanup_action":"none","after_cleanup_command":null},"failed_paths":[],"pending_paths":[],"summary":{"planned":0,"completed":0,"preserved":4,"pending":0,"failed":0,"warnings":0},"actions":[{"path":"spec-dock","category":"container","status":"preserved","reason":"shared-container-preserve"},{"path":"spec-dock/spec-dock.version","category":"record","status":"preserved","reason":"terminal-record-current"},{"path":"spec-dock/.gitignore","category":"seed","status":"preserved","reason":"preserve-only-seed"},{"path":".github/workflows/ci.yml","category":"seed","status":"preserved","reason":"preserve-only-seed"}],"guidance":[],"warnings":[],"errors":[]}
```

### WIR-GOLDEN-U9 — Partial uninstall at templates

```json
{"schema_version":1,"target":"/tmp/consumer","mode":"apply","apply":true,"specs_mode":"keep","status":"partial_failure","code":"uninstall-partial-failure","operation":"uninstall","candidate_digest":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","seed_policy":"preserve-only","mutation_started":true,"bootstrap_rolled_back":false,"phase":"detach-templates","last_completed_phase":"detach-docs","retry_command":"spec-dock uninstall --apply --keep-specs -- /tmp/consumer","continuation":{"next_action":"run-request","next_command":"spec-dock uninstall --apply --keep-specs -- /tmp/consumer","after_cleanup_action":"none","after_cleanup_command":null},"failed_paths":["spec-dock/templates"],"pending_paths":["spec-dock/system","spec-dock/scripts",".agents/skills/spec-dock",".agents/skills/spec-dock-grill-with-docs","@provider-stage"],"summary":{"planned":0,"completed":2,"preserved":3,"pending":5,"failed":1,"warnings":0},"actions":[{"path":"spec-dock","category":"container","status":"preserved","reason":"shared-container-preserve"},{"path":"spec-dock/spec-dock.version","category":"record","status":"completed","reason":"incomplete-record-publish"},{"path":"spec-dock/docs","category":"root","status":"completed","reason":"owned-root-remove"},{"path":"spec-dock/templates","category":"root","status":"failed","reason":"owned-root-remove"},{"path":"spec-dock/system","category":"root","status":"pending","reason":"owned-root-remove"},{"path":"spec-dock/scripts","category":"root","status":"pending","reason":"owned-root-remove"},{"path":".agents/skills/spec-dock","category":"slot","status":"pending","reason":"owned-slot-remove"},{"path":".agents/skills/spec-dock-grill-with-docs","category":"slot","status":"pending","reason":"owned-slot-remove"},{"path":"spec-dock/.gitignore","category":"seed","status":"preserved","reason":"preserve-only-seed"},{"path":".github/workflows/ci.yml","category":"seed","status":"preserved","reason":"preserve-only-seed"},{"path":"@provider-stage","category":"stage","status":"pending","reason":"candidate-stage-cleanup"}],"guidance":["Rerun only the retry_command shown in this result.","Do not switch operation, candidate package, or seed policy."],"warnings":[],"errors":["SpecDock uninstall stopped after durable mutation; rerun the exact retry command."]}
```

### WIR-GOLDEN-U10 — Removed purge trap

```json
{"schema_version":1,"target":"/tmp/consumer","mode":"apply","apply":true,"specs_mode":"remove","status":"error","code":"spec-history-purge-removed","operation":null,"candidate_digest":null,"seed_policy":null,"mutation_started":false,"bootstrap_rolled_back":false,"phase":"request-validation","last_completed_phase":"not-started","retry_command":null,"continuation":{"next_action":"none","next_command":null,"after_cleanup_action":"none","after_cleanup_command":null},"failed_paths":[],"pending_paths":[],"summary":{"planned":0,"completed":0,"preserved":0,"pending":0,"failed":0,"warnings":0},"actions":[],"guidance":["Use tooling-only uninstall without --remove-specs.","Spec history and Workbench data remain consumer-owned."],"warnings":[],"errors":["Spec history purge has been removed; uninstall is tooling-only."]}
```

### WIR-GOLDEN-I1 — Partial preserve-only install at system

```json
{"schema_version":1,"target":"/tmp/consumer","mode":"apply","apply":true,"specs_mode":null,"status":"partial_failure","code":"install-partial-failure","operation":"install","candidate_digest":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","seed_policy":"preserve-only","mutation_started":true,"bootstrap_rolled_back":false,"phase":"publish-system","last_completed_phase":"publish-templates","retry_command":"spec-dock update -- /tmp/consumer","continuation":{"next_action":"run-request","next_command":"spec-dock update -- /tmp/consumer","after_cleanup_action":"none","after_cleanup_command":null},"failed_paths":["spec-dock/system"],"pending_paths":["spec-dock/scripts",".agents/skills/spec-dock",".agents/skills/spec-dock-grill-with-docs","@provider-stage"],"summary":{"planned":0,"completed":3,"preserved":3,"pending":4,"failed":1,"warnings":0},"actions":[{"path":"spec-dock","category":"container","status":"preserved","reason":"shared-container-preserve"},{"path":"spec-dock/spec-dock.version","category":"record","status":"completed","reason":"incomplete-record-publish"},{"path":"spec-dock/docs","category":"root","status":"completed","reason":"candidate-root-replace"},{"path":"spec-dock/templates","category":"root","status":"completed","reason":"candidate-root-replace"},{"path":"spec-dock/system","category":"root","status":"failed","reason":"candidate-root-replace"},{"path":"spec-dock/scripts","category":"root","status":"pending","reason":"candidate-root-replace"},{"path":".agents/skills/spec-dock","category":"slot","status":"pending","reason":"candidate-slot-replace"},{"path":".agents/skills/spec-dock-grill-with-docs","category":"slot","status":"pending","reason":"candidate-slot-replace"},{"path":"spec-dock/.gitignore","category":"seed","status":"preserved","reason":"preserve-only-seed"},{"path":".github/workflows/ci.yml","category":"seed","status":"preserved","reason":"preserve-only-seed"},{"path":"@provider-stage","category":"stage","status":"pending","reason":"candidate-stage-cleanup"}],"guidance":["Rerun only the retry_command shown in this result.","Do not switch operation, candidate package, or seed policy."],"warnings":[],"errors":["SpecDock install stopped after durable mutation; rerun the exact retry command."]}
```

### WIR-GOLDEN-B1 — Invalid record during update

```json
{"schema_version":1,"target":"/tmp/consumer","mode":"apply","apply":true,"specs_mode":null,"status":"blocked","code":"installation-record-invalid","operation":null,"candidate_digest":null,"seed_policy":null,"mutation_started":false,"bootstrap_rolled_back":false,"phase":"preflight","last_completed_phase":"request-validation","retry_command":null,"continuation":{"next_action":"none","next_command":null,"after_cleanup_action":"none","after_cleanup_command":null},"failed_paths":[],"pending_paths":[],"summary":{"planned":0,"completed":0,"preserved":0,"pending":0,"failed":0,"warnings":0},"actions":[],"guidance":[],"warnings":[],"errors":["The SpecDock installation record is invalid."]}
```

### WIR-GOLDEN-B2 — Resume candidate mismatch

```json
{"schema_version":1,"target":"/tmp/consumer","mode":"apply","apply":true,"specs_mode":null,"status":"blocked","code":"resume-candidate-mismatch","operation":"install","candidate_digest":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","seed_policy":"preserve-only","mutation_started":false,"bootstrap_rolled_back":false,"phase":"candidate-staging","last_completed_phase":"preflight","retry_command":null,"continuation":{"next_action":"none","next_command":null,"after_cleanup_action":"none","after_cleanup_command":null},"failed_paths":[],"pending_paths":[],"summary":{"planned":0,"completed":0,"preserved":0,"pending":0,"failed":0,"warnings":0},"actions":[],"guidance":[],"warnings":[],"errors":["The incomplete operation can be resumed only with the same candidate digest."]}
```

### WIR-GOLDEN-B3 — Candidate invalid

```json
{"schema_version":1,"target":"/tmp/consumer","mode":"apply","apply":true,"specs_mode":null,"status":"blocked","code":"candidate-invalid","operation":"update","candidate_digest":null,"seed_policy":"preserve-only","mutation_started":false,"bootstrap_rolled_back":false,"phase":"candidate-staging","last_completed_phase":"preflight","retry_command":null,"continuation":{"next_action":"none","next_command":null,"after_cleanup_action":"none","after_cleanup_command":null},"failed_paths":[],"pending_paths":[],"summary":{"planned":0,"completed":0,"preserved":0,"pending":0,"failed":0,"warnings":0},"actions":[],"guidance":[],"warnings":[],"errors":["The packaged provider candidate is invalid."]}
```

### WIR-GOLDEN-B4 — Stage owner mismatch

```json
{"schema_version":1,"target":"/tmp/consumer","mode":"apply","apply":true,"specs_mode":null,"status":"blocked","code":"stage-owner-mismatch","operation":"install","candidate_digest":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","seed_policy":"create-if-absent","mutation_started":false,"bootstrap_rolled_back":false,"phase":"candidate-staging","last_completed_phase":"preflight","retry_command":null,"continuation":{"next_action":"none","next_command":null,"after_cleanup_action":"none","after_cleanup_command":null},"failed_paths":[],"pending_paths":[],"summary":{"planned":0,"completed":0,"preserved":0,"pending":0,"failed":0,"warnings":0},"actions":[],"guidance":[],"warnings":[],"errors":["The existing provider stage does not match this repository, operation, candidate, and seed policy."]}
```

### WIR-GOLDEN-CF1 — Desired init encounters cleanup failure

```json
{"schema_version":1,"target":"/tmp/consumer","mode":"apply","apply":true,"specs_mode":null,"status":"partial_failure","code":"terminal-cleanup-failed","operation":"install","candidate_digest":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","seed_policy":"create-if-absent","mutation_started":true,"bootstrap_rolled_back":false,"phase":"cleanup-stage","last_completed_phase":"publish-terminal-record","retry_command":"spec-dock init --force --provider-cleanup-token eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee -- /tmp/consumer","continuation":{"next_action":"retry-cleanup","next_command":"spec-dock init --force --provider-cleanup-token eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee -- /tmp/consumer","after_cleanup_action":"run-request","after_cleanup_command":"spec-dock init -- /tmp/consumer"},"failed_paths":["@provider-stage"],"pending_paths":[],"summary":{"planned":0,"completed":0,"preserved":0,"pending":0,"failed":1,"warnings":0},"actions":[{"path":"@provider-stage","category":"stage","status":"failed","reason":"candidate-stage-cleanup"}],"guidance":["Run continuation.next_command to retry owned stage cleanup.","After cleanup succeeds, run continuation.after_cleanup_command.","The requested terminal tooling state is already durable."],"warnings":[],"errors":["The requested tooling state is durable, but owned stage cleanup failed; follow the continuation object exactly."]}
```

### WIR-GOLDEN-CS1 — Tokenized retry completes cleanup and continues desired init

```json
{"schema_version":1,"target":"/tmp/consumer","mode":"apply","apply":true,"specs_mode":null,"status":"completed","code":"terminal-cleanup-completed","operation":"install","candidate_digest":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","seed_policy":"create-if-absent","mutation_started":true,"bootstrap_rolled_back":false,"phase":"complete","last_completed_phase":"cleanup-stage","retry_command":null,"continuation":{"next_action":"run-request","next_command":"spec-dock init -- /tmp/consumer","after_cleanup_action":"none","after_cleanup_command":null},"failed_paths":[],"pending_paths":[],"summary":{"planned":0,"completed":1,"preserved":0,"pending":0,"failed":0,"warnings":0},"actions":[{"path":"@provider-stage","category":"stage","status":"completed","reason":"candidate-stage-cleanup"}],"guidance":["Owned provider stage cleanup completed; no lifecycle operation was executed.","Run continuation.next_command to execute the preserved requested operation."],"warnings":[],"errors":[]}
```

### WIR-GOLDEN-CF2 — Desired init --force encounters cleanup failure

```json
{"schema_version":1,"target":"/tmp/consumer","mode":"apply","apply":true,"specs_mode":null,"status":"partial_failure","code":"terminal-cleanup-failed","operation":"install","candidate_digest":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","seed_policy":"create-if-absent","mutation_started":true,"bootstrap_rolled_back":false,"phase":"cleanup-stage","last_completed_phase":"publish-terminal-record","retry_command":"spec-dock init --force --provider-cleanup-token eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee -- /tmp/consumer","continuation":{"next_action":"retry-cleanup","next_command":"spec-dock init --force --provider-cleanup-token eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee -- /tmp/consumer","after_cleanup_action":"run-request","after_cleanup_command":"spec-dock init --force -- /tmp/consumer"},"failed_paths":["@provider-stage"],"pending_paths":[],"summary":{"planned":0,"completed":0,"preserved":0,"pending":0,"failed":1,"warnings":0},"actions":[{"path":"@provider-stage","category":"stage","status":"failed","reason":"candidate-stage-cleanup"}],"guidance":["Run continuation.next_command to retry owned stage cleanup.","After cleanup succeeds, run continuation.after_cleanup_command.","The requested terminal tooling state is already durable."],"warnings":[],"errors":["The requested tooling state is durable, but owned stage cleanup failed; follow the continuation object exactly."]}
```

### WIR-GOLDEN-CS2 — Tokenized retry completes cleanup and continues desired init --force

```json
{"schema_version":1,"target":"/tmp/consumer","mode":"apply","apply":true,"specs_mode":null,"status":"completed","code":"terminal-cleanup-completed","operation":"install","candidate_digest":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","seed_policy":"create-if-absent","mutation_started":true,"bootstrap_rolled_back":false,"phase":"complete","last_completed_phase":"cleanup-stage","retry_command":null,"continuation":{"next_action":"run-request","next_command":"spec-dock init --force -- /tmp/consumer","after_cleanup_action":"none","after_cleanup_command":null},"failed_paths":[],"pending_paths":[],"summary":{"planned":0,"completed":1,"preserved":0,"pending":0,"failed":0,"warnings":0},"actions":[{"path":"@provider-stage","category":"stage","status":"completed","reason":"candidate-stage-cleanup"}],"guidance":["Owned provider stage cleanup completed; no lifecycle operation was executed.","Run continuation.next_command to execute the preserved requested operation."],"warnings":[],"errors":[]}
```

### WIR-GOLDEN-CF3 — Desired update encounters cleanup failure

```json
{"schema_version":1,"target":"/tmp/consumer","mode":"apply","apply":true,"specs_mode":null,"status":"partial_failure","code":"terminal-cleanup-failed","operation":"update","candidate_digest":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","seed_policy":"preserve-only","mutation_started":true,"bootstrap_rolled_back":false,"phase":"cleanup-stage","last_completed_phase":"publish-terminal-record","retry_command":"spec-dock update --provider-cleanup-token eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee -- /tmp/consumer","continuation":{"next_action":"retry-cleanup","next_command":"spec-dock update --provider-cleanup-token eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee -- /tmp/consumer","after_cleanup_action":"run-request","after_cleanup_command":"spec-dock update -- /tmp/consumer"},"failed_paths":["@provider-stage"],"pending_paths":[],"summary":{"planned":0,"completed":0,"preserved":0,"pending":0,"failed":1,"warnings":0},"actions":[{"path":"@provider-stage","category":"stage","status":"failed","reason":"candidate-stage-cleanup"}],"guidance":["Run continuation.next_command to retry owned stage cleanup.","After cleanup succeeds, run continuation.after_cleanup_command.","The requested terminal tooling state is already durable."],"warnings":[],"errors":["The requested tooling state is durable, but owned stage cleanup failed; follow the continuation object exactly."]}
```

### WIR-GOLDEN-CS3 — Tokenized retry completes cleanup and continues desired update

```json
{"schema_version":1,"target":"/tmp/consumer","mode":"apply","apply":true,"specs_mode":null,"status":"completed","code":"terminal-cleanup-completed","operation":"update","candidate_digest":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","seed_policy":"preserve-only","mutation_started":true,"bootstrap_rolled_back":false,"phase":"complete","last_completed_phase":"cleanup-stage","retry_command":null,"continuation":{"next_action":"run-request","next_command":"spec-dock update -- /tmp/consumer","after_cleanup_action":"none","after_cleanup_command":null},"failed_paths":[],"pending_paths":[],"summary":{"planned":0,"completed":1,"preserved":0,"pending":0,"failed":0,"warnings":0},"actions":[{"path":"@provider-stage","category":"stage","status":"completed","reason":"candidate-stage-cleanup"}],"guidance":["Owned provider stage cleanup completed; no lifecycle operation was executed.","Run continuation.next_command to execute the preserved requested operation."],"warnings":[],"errors":[]}
```

### WIR-GOLDEN-CF4 — Terminal cleanup failure: uninstall dry-run default

```json
{"schema_version":1,"target":"/tmp/consumer","mode":"dry-run","apply":false,"specs_mode":null,"status":"partial_failure","code":"terminal-cleanup-failed","operation":"install","candidate_digest":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","seed_policy":"create-if-absent","mutation_started":true,"bootstrap_rolled_back":false,"phase":"cleanup-stage","last_completed_phase":"publish-terminal-record","retry_command":"spec-dock init --force --provider-cleanup-token eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee -- /tmp/consumer","continuation":{"next_action":"retry-cleanup","next_command":"spec-dock init --force --provider-cleanup-token eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee -- /tmp/consumer","after_cleanup_action":"run-request","after_cleanup_command":"spec-dock uninstall -- /tmp/consumer"},"failed_paths":["@provider-stage"],"pending_paths":[],"summary":{"planned":0,"completed":0,"preserved":0,"pending":0,"failed":1,"warnings":0},"actions":[{"path":"@provider-stage","category":"stage","status":"failed","reason":"candidate-stage-cleanup"}],"guidance":["Run continuation.next_command to retry owned stage cleanup.","After cleanup succeeds, run continuation.after_cleanup_command.","The requested terminal tooling state is already durable."],"warnings":[],"errors":["The requested tooling state is durable, but owned stage cleanup failed; follow the continuation object exactly."]}
```

### WIR-GOLDEN-CS4 — Terminal cleanup success: uninstall dry-run default

```json
{"schema_version":1,"target":"/tmp/consumer","mode":"dry-run","apply":false,"specs_mode":null,"status":"completed","code":"terminal-cleanup-completed","operation":"install","candidate_digest":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","seed_policy":"create-if-absent","mutation_started":true,"bootstrap_rolled_back":false,"phase":"complete","last_completed_phase":"cleanup-stage","retry_command":null,"continuation":{"next_action":"run-request","next_command":"spec-dock uninstall -- /tmp/consumer","after_cleanup_action":"none","after_cleanup_command":null},"failed_paths":[],"pending_paths":[],"summary":{"planned":0,"completed":1,"preserved":0,"pending":0,"failed":0,"warnings":0},"actions":[{"path":"@provider-stage","category":"stage","status":"completed","reason":"candidate-stage-cleanup"}],"guidance":["Owned provider stage cleanup completed; no lifecycle operation was executed.","Run continuation.next_command to execute the preserved requested operation."],"warnings":[],"errors":[]}
```

### WIR-GOLDEN-CF5 — Terminal cleanup failure: uninstall dry-run keep

```json
{"schema_version":1,"target":"/tmp/consumer","mode":"dry-run","apply":false,"specs_mode":"keep","status":"partial_failure","code":"terminal-cleanup-failed","operation":"install","candidate_digest":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","seed_policy":"create-if-absent","mutation_started":true,"bootstrap_rolled_back":false,"phase":"cleanup-stage","last_completed_phase":"publish-terminal-record","retry_command":"spec-dock init --force --provider-cleanup-token eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee -- /tmp/consumer","continuation":{"next_action":"retry-cleanup","next_command":"spec-dock init --force --provider-cleanup-token eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee -- /tmp/consumer","after_cleanup_action":"run-request","after_cleanup_command":"spec-dock uninstall --keep-specs -- /tmp/consumer"},"failed_paths":["@provider-stage"],"pending_paths":[],"summary":{"planned":0,"completed":0,"preserved":0,"pending":0,"failed":1,"warnings":0},"actions":[{"path":"@provider-stage","category":"stage","status":"failed","reason":"candidate-stage-cleanup"}],"guidance":["Run continuation.next_command to retry owned stage cleanup.","After cleanup succeeds, run continuation.after_cleanup_command.","The requested terminal tooling state is already durable."],"warnings":[],"errors":["The requested tooling state is durable, but owned stage cleanup failed; follow the continuation object exactly."]}
```

### WIR-GOLDEN-CS5 — Terminal cleanup success: uninstall dry-run keep

```json
{"schema_version":1,"target":"/tmp/consumer","mode":"dry-run","apply":false,"specs_mode":"keep","status":"completed","code":"terminal-cleanup-completed","operation":"install","candidate_digest":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","seed_policy":"create-if-absent","mutation_started":true,"bootstrap_rolled_back":false,"phase":"complete","last_completed_phase":"cleanup-stage","retry_command":null,"continuation":{"next_action":"run-request","next_command":"spec-dock uninstall --keep-specs -- /tmp/consumer","after_cleanup_action":"none","after_cleanup_command":null},"failed_paths":[],"pending_paths":[],"summary":{"planned":0,"completed":1,"preserved":0,"pending":0,"failed":0,"warnings":0},"actions":[{"path":"@provider-stage","category":"stage","status":"completed","reason":"candidate-stage-cleanup"}],"guidance":["Owned provider stage cleanup completed; no lifecycle operation was executed.","Run continuation.next_command to execute the preserved requested operation."],"warnings":[],"errors":[]}
```

### WIR-GOLDEN-CF6 — Terminal cleanup failure: uninstall apply default

```json
{"schema_version":1,"target":"/tmp/consumer","mode":"apply","apply":true,"specs_mode":null,"status":"partial_failure","code":"terminal-cleanup-failed","operation":"install","candidate_digest":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","seed_policy":"create-if-absent","mutation_started":true,"bootstrap_rolled_back":false,"phase":"cleanup-stage","last_completed_phase":"publish-terminal-record","retry_command":"spec-dock init --force --provider-cleanup-token eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee -- /tmp/consumer","continuation":{"next_action":"retry-cleanup","next_command":"spec-dock init --force --provider-cleanup-token eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee -- /tmp/consumer","after_cleanup_action":"run-request","after_cleanup_command":"spec-dock uninstall --apply -- /tmp/consumer"},"failed_paths":["@provider-stage"],"pending_paths":[],"summary":{"planned":0,"completed":0,"preserved":0,"pending":0,"failed":1,"warnings":0},"actions":[{"path":"@provider-stage","category":"stage","status":"failed","reason":"candidate-stage-cleanup"}],"guidance":["Run continuation.next_command to retry owned stage cleanup.","After cleanup succeeds, run continuation.after_cleanup_command.","The requested terminal tooling state is already durable."],"warnings":[],"errors":["The requested tooling state is durable, but owned stage cleanup failed; follow the continuation object exactly."]}
```

### WIR-GOLDEN-CS6 — Terminal cleanup success: uninstall apply default

```json
{"schema_version":1,"target":"/tmp/consumer","mode":"apply","apply":true,"specs_mode":null,"status":"completed","code":"terminal-cleanup-completed","operation":"install","candidate_digest":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","seed_policy":"create-if-absent","mutation_started":true,"bootstrap_rolled_back":false,"phase":"complete","last_completed_phase":"cleanup-stage","retry_command":null,"continuation":{"next_action":"run-request","next_command":"spec-dock uninstall --apply -- /tmp/consumer","after_cleanup_action":"none","after_cleanup_command":null},"failed_paths":[],"pending_paths":[],"summary":{"planned":0,"completed":1,"preserved":0,"pending":0,"failed":0,"warnings":0},"actions":[{"path":"@provider-stage","category":"stage","status":"completed","reason":"candidate-stage-cleanup"}],"guidance":["Owned provider stage cleanup completed; no lifecycle operation was executed.","Run continuation.next_command to execute the preserved requested operation."],"warnings":[],"errors":[]}
```

### WIR-GOLDEN-CF7 — Terminal cleanup failure: uninstall apply keep

```json
{"schema_version":1,"target":"/tmp/consumer","mode":"apply","apply":true,"specs_mode":"keep","status":"partial_failure","code":"terminal-cleanup-failed","operation":"install","candidate_digest":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","seed_policy":"create-if-absent","mutation_started":true,"bootstrap_rolled_back":false,"phase":"cleanup-stage","last_completed_phase":"publish-terminal-record","retry_command":"spec-dock init --force --provider-cleanup-token eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee -- /tmp/consumer","continuation":{"next_action":"retry-cleanup","next_command":"spec-dock init --force --provider-cleanup-token eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee -- /tmp/consumer","after_cleanup_action":"run-request","after_cleanup_command":"spec-dock uninstall --apply --keep-specs -- /tmp/consumer"},"failed_paths":["@provider-stage"],"pending_paths":[],"summary":{"planned":0,"completed":0,"preserved":0,"pending":0,"failed":1,"warnings":0},"actions":[{"path":"@provider-stage","category":"stage","status":"failed","reason":"candidate-stage-cleanup"}],"guidance":["Run continuation.next_command to retry owned stage cleanup.","After cleanup succeeds, run continuation.after_cleanup_command.","The requested terminal tooling state is already durable."],"warnings":[],"errors":["The requested tooling state is durable, but owned stage cleanup failed; follow the continuation object exactly."]}
```

### WIR-GOLDEN-CS7 — Terminal cleanup success: uninstall apply keep

```json
{"schema_version":1,"target":"/tmp/consumer","mode":"apply","apply":true,"specs_mode":"keep","status":"completed","code":"terminal-cleanup-completed","operation":"install","candidate_digest":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","seed_policy":"create-if-absent","mutation_started":true,"bootstrap_rolled_back":false,"phase":"complete","last_completed_phase":"cleanup-stage","retry_command":null,"continuation":{"next_action":"run-request","next_command":"spec-dock uninstall --apply --keep-specs -- /tmp/consumer","after_cleanup_action":"none","after_cleanup_command":null},"failed_paths":[],"pending_paths":[],"summary":{"planned":0,"completed":1,"preserved":0,"pending":0,"failed":0,"warnings":0},"actions":[{"path":"@provider-stage","category":"stage","status":"completed","reason":"candidate-stage-cleanup"}],"guidance":["Owned provider stage cleanup completed; no lifecycle operation was executed.","Run continuation.next_command to execute the preserved requested operation."],"warnings":[],"errors":[]}
```

### WIR-GOLDEN-CRF1 — Tokenized update cleanup retry fails with no desired request

```json
{"schema_version":1,"target":"/tmp/consumer","mode":"apply","apply":true,"specs_mode":null,"status":"partial_failure","code":"terminal-cleanup-failed","operation":"update","candidate_digest":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","seed_policy":"preserve-only","mutation_started":true,"bootstrap_rolled_back":false,"phase":"cleanup-stage","last_completed_phase":"publish-terminal-record","retry_command":"spec-dock update --provider-cleanup-token eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee -- /tmp/consumer","continuation":{"next_action":"retry-cleanup","next_command":"spec-dock update --provider-cleanup-token eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee -- /tmp/consumer","after_cleanup_action":"none","after_cleanup_command":null},"failed_paths":["@provider-stage"],"pending_paths":[],"summary":{"planned":0,"completed":0,"preserved":0,"pending":0,"failed":1,"warnings":0},"actions":[{"path":"@provider-stage","category":"stage","status":"failed","reason":"candidate-stage-cleanup"}],"guidance":["Run continuation.next_command to retry owned stage cleanup.","No lifecycle request is pending after cleanup.","The requested terminal tooling state is already durable."],"warnings":[],"errors":["The requested tooling state is durable, but owned stage cleanup failed; follow the continuation object exactly."]}
```

### WIR-GOLDEN-CRS1 — Tokenized update cleanup retry succeeds with no desired request

```json
{"schema_version":1,"target":"/tmp/consumer","mode":"apply","apply":true,"specs_mode":null,"status":"completed","code":"terminal-cleanup-completed","operation":"update","candidate_digest":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","seed_policy":"preserve-only","mutation_started":true,"bootstrap_rolled_back":false,"phase":"complete","last_completed_phase":"cleanup-stage","retry_command":null,"continuation":{"next_action":"none","next_command":null,"after_cleanup_action":"none","after_cleanup_command":null},"failed_paths":[],"pending_paths":[],"summary":{"planned":0,"completed":1,"preserved":0,"pending":0,"failed":0,"warnings":0},"actions":[{"path":"@provider-stage","category":"stage","status":"completed","reason":"candidate-stage-cleanup"}],"guidance":["Owned provider stage cleanup completed; no lifecycle operation was executed.","No lifecycle operation is pending."],"warnings":[],"errors":[]}
```

### WIR-GOLDEN-CRF2 — Tokenized init-force cleanup retry fails while desired uninstall remains deferred

```json
{"schema_version":1,"target":"/tmp/consumer","mode":"apply","apply":true,"specs_mode":null,"status":"partial_failure","code":"terminal-cleanup-failed","operation":"install","candidate_digest":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","seed_policy":"create-if-absent","mutation_started":true,"bootstrap_rolled_back":false,"phase":"cleanup-stage","last_completed_phase":"publish-terminal-record","retry_command":"spec-dock init --force --provider-cleanup-token eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee -- /tmp/consumer","continuation":{"next_action":"retry-cleanup","next_command":"spec-dock init --force --provider-cleanup-token eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee -- /tmp/consumer","after_cleanup_action":"run-request","after_cleanup_command":"spec-dock uninstall --apply --keep-specs -- /tmp/consumer"},"failed_paths":["@provider-stage"],"pending_paths":[],"summary":{"planned":0,"completed":0,"preserved":0,"pending":0,"failed":1,"warnings":0},"actions":[{"path":"@provider-stage","category":"stage","status":"failed","reason":"candidate-stage-cleanup"}],"guidance":["Run continuation.next_command to retry owned stage cleanup.","After cleanup succeeds, run continuation.after_cleanup_command.","The requested terminal tooling state is already durable."],"warnings":[],"errors":["The requested tooling state is durable, but owned stage cleanup failed; follow the continuation object exactly."]}
```

### WIR-GOLDEN-CRS2 — Tokenized init-force cleanup retry succeeds and returns deferred uninstall

```json
{"schema_version":1,"target":"/tmp/consumer","mode":"apply","apply":true,"specs_mode":null,"status":"completed","code":"terminal-cleanup-completed","operation":"install","candidate_digest":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","seed_policy":"create-if-absent","mutation_started":true,"bootstrap_rolled_back":false,"phase":"complete","last_completed_phase":"cleanup-stage","retry_command":null,"continuation":{"next_action":"run-request","next_command":"spec-dock uninstall --apply --keep-specs -- /tmp/consumer","after_cleanup_action":"none","after_cleanup_command":null},"failed_paths":[],"pending_paths":[],"summary":{"planned":0,"completed":1,"preserved":0,"pending":0,"failed":0,"warnings":0},"actions":[{"path":"@provider-stage","category":"stage","status":"completed","reason":"candidate-stage-cleanup"}],"guidance":["Owned provider stage cleanup completed; no lifecycle operation was executed.","Run continuation.next_command to execute the preserved requested operation."],"warnings":[],"errors":[]}
```

## 14. Public text

Init/update clean success remains `spec-dock: ok (init) -> /tmp/consumer
` or `spec-dock: ok (update) -> /tmp/consumer
`. Cleanup-warning success appends `warning: Provider tooling reached the requested terminal state, but the owned external stage could not be removed.
` and `next: ${continuation.next_command}
`.

`terminal-cleanup-completed` stdout is exactly `spec-dock: terminal cleanup completed; no lifecycle operation was executed.
next: ${NEXT_COMMAND_OR_NONE}
`. `terminal-cleanup-failed` stderr is exactly `error: terminal-cleanup-failed: The requested tooling state is durable, but owned stage cleanup failed; follow the continuation object exactly.
next: ${continuation.next_command}
after-cleanup: ${AFTER_COMMAND_OR_NONE}
`. Values use the continuation object; null is rendered `none`. A displayed cleanup retry includes the hidden token exactly as supplied by `continuation.next_command`; text never strips or reconstructs it.

Uninstall text exact line order:

```text
spec-dock uninstall <mode> for <target>
status: <status>
code: <code>
phase: <phase>
last-completed-phase: <last_completed_phase>
operation: <operation-or-none>
candidate-digest: <digest-or-none>
seed-policy: <policy-or-none>
mutation-started: <true|false>
bootstrap-rolled-back: <true|false>
next-action: <continuation.next_action>
next-command: <command-or-none>
after-cleanup-action: <continuation.after_cleanup_action>
after-cleanup-command: <command-or-none>
summary: planned=<n> completed=<n> preserved=<n> pending=<n> failed=<n> warnings=<n>
```

Action, guidance, warning and error lines follow in array order. JSON mode emits only the exact 23-key object.

## 15. Required tests and trace

Required tests include desired uninstall during old install cleanup; cleanup failure -> tokenized retry -> deferred uninstall; no-token desired update/init-force distinct from the tokenized base form; cleanup retry with no deferred request; a third explicit command preserving the first deferred request; crash after ACTIVE update/unlink; and table-driven continuation rendering for all seven invocation IDs.

Table-driven tests enumerate all 142 §10 rows and all 38 codes and reject every unlisted relation; all seven actual invocation echoes for both terminal-cleanup success and failure; cleanup-only return/no-dispatch; all sequences/partial and mandatory-cleanup pairs; action relations; target ordering and exact failed/pending equality; all 4 durable record goldens, all 33 public JSON review goldens, and exact text goldens; duplicate/unknown values; CLI/service parity; exact terminal-cleanup crash/retry cases and dogfood record/markers at S60/S70.

Normative trace: Epic E384-RQ-003,006–010,022; Issue I392-RQ-004–020,028; Design I392-D-001–012; Plan S10–S70. Owner decisions required: none.
