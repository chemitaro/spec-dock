---
種別: Normative Artifact
ID: "provider-lifecycle-wire-contract-v2"
タイトル: "Provider Lifecycle Wire Contract"
状態: "accepted"
最終更新: "2026-09-01"
対象: ["epic-00384", "iss-00392"]
repository_evidence:
  repository: "chemitaro/spec-dock"
  branch: "codex/epic-00384-provider-test-strategy-planning"
  sha: "eaddf76806c338ee05463741f15fd3967bbceb57"
---

# Provider Lifecycle Wire Contract

## 1. Authority and closed-world rule

本ArtifactはIssue #392が実装するprovider lifecycleの唯一のnormative wire authorityである。Epic/Issue Requirement、Design、Plan、accepted ADR、Luna handoffは本Artifactへtraceする。Python enum、dataclass、serializer、CLI text/JSON、golden test、migration/fault evidenceはここに定義した値だけを使用する。

次を禁止する。

- implementation-defined phase、reason、code、status、operation、action category。
- `other`、`unknown`、`generic`、`internal-error`等のcatch-all wire value。
- unknown enumを既知値へfallbackすること。
- filesystem列挙順、dictionary insertion order、set orderをpublic array orderに利用すること。
- public adapterがrecord、stage owner、journal相当のprivate fileを独自解釈すること。

未知値、relation違反、欠落field、追加fieldはwire objectを生成せず、typed constructor/parserでfail closedする。予期しない未型付け例外は本wireのcodeへ丸めず、test/CI defectとしてprocessを失敗させる。

## 2. Canonical scalar conventions

| Type | Exact contract |
|---|---|
| UTF-8 text | UTF-8、NULなし。Public JSONはASCII control charactersをJSON escapeする。 |
| Version | `0.2.4`。Exact legacy recognition inputだけ`0.2.3`。 |
| SHA-256 | lowercase hexadecimal 64 characters。 |
| Git SHA/tree | lowercase hexadecimal 40 characters。 |
| Boolean | JSON `true` / `false` only。Integer 0/1は禁止。 |
| Null | JSON `null` only。Missing fieldで代用しない。 |
| Path | repository-relative POSIX path、またはclosed sentinel `@provider-stage`。Absolute path、`..`、backslash、empty componentは禁止。 |
| JSON bytes | `json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=False) + "\n"`。Object key orderは本Artifactのgolden順。 |

## 3. Canonical target and array order

### WIR-ORD-001 — `TARGET_PATH_ORDER`

全`failed_paths`、`pending_paths`、`actions`は次のrankで昇順に並べる。Dictionary順または辞書順は使用しない。

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

1. `failed_paths`と`pending_paths`はuniqueである。
2. `pending_paths`は`failed_paths`のsubsequenceではなくsubsetであり、それぞれ独立に`TARGET_PATH_ORDER`へsortする。
3. `actions`は一pathにつき最大一件。Same path duplicateは禁止。
4. `actions`はpath rank、同rankでは`ACTION_CATEGORY_ORDER`でsortする。現契約では一path一件なのでtieは発生しない。
5. Closed order外のpathをpublic arraysへ入れない。Protected user pathの詳細はpublic arrayへ出さず、top-level blocked codeと固定messageだけを返す。
6. `warnings`と`errors`はphase rank、path rank、code declaration orderでsortした固定文字列配列である。
7. `guidance`はtop-level codeに結合した固定配列で、生成時sortしない。

### WIR-ORD-002 — `ACTION_CATEGORY_ORDER`

```text
container
record
root
slot
seed
stage
preservation
```

## 4. Durable installation record

### WIR-REC-001 — Exact seven keys and byte format

Path: `spec-dock/spec-dock.version`。

Key order and types:

| Order | Key | Type | Nullability | Enum / relation |
|---:|---|---|---|---|
| 1 | `schema_version` | integer | non-null | exact `1` |
| 2 | `state` | string | non-null | `incomplete`、`ready`、`tooling-absent-preserved-data` |
| 3 | `operation` | string or null | conditional | `install`、`update`、`uninstall` or `null` |
| 4 | `version` | string | non-null | exact `0.2.4` for all final-format records |
| 5 | `candidate_digest` | string | non-null | lowercase SHA-256 of fixed roots and slots, excluding record/seeds/generated slot markers |
| 6 | `seed_policy` | string | non-null | `create-if-absent` or `preserve-only` |
| 7 | `skill_slots` | object | non-null | exact two keys in the order below; each value exact `0.2.4` |

`skill_slots` exact key order:

```text
spec-dock
spec-dock-grill-with-docs
```

Parser constraints: UTF-8、regular file、link count 1、maximum 4096 bytes、duplicate JSON key rejection、unknown/missing key rejection、boolean-as-integer rejection、canonical enum relation validation。Writer mode is `0644` and uses atomic replace; in-place truncate/overwrite is forbidden。

### WIR-REC-002 — Durable relation matrix

| Durable state | `operation` | Allowed `seed_policy` | Required tooling postcondition |
|---|---|---|---|
| `incomplete` | `install` | `create-if-absent` or `preserve-only` | Candidate operation may be partially published. Resume identity is exact `(install,candidate_digest,seed_policy)`. |
| `incomplete` | `update` | `preserve-only` only | Ready workspace is converging tocandidate. |
| `incomplete` | `uninstall` | `preserve-only` only | Owned roots/slots may be partially detached. |
| `ready` | `null` | `create-if-absent` or `preserve-only` | Four roots andtwo slots match `candidate_digest`; slot markers match; seeds are outside authority. |
| `tooling-absent-preserved-data` | `null` | `preserve-only` only | Four roots andtwo slots absent; shared `spec-dock` container andrecord remain. |

The terminal `ready.seed_policy` records the seed authority used by the immediately completed install/update operation. It does not authorize future seed writes. Every new update/uninstall operation first publishes an `incomplete` record with `preserve-only`。

### WIR-REC-003 — Exact command-to-record operation values

| Invocation / observed state | Durable operation wire | Seed policy | Terminal code family |
|---|---|---|---|
| `init` or `init --force` / never-installed `absent` | `install` | `create-if-absent` | `install-*` |
| `update` / never-installed `absent` | `install` | `preserve-only` | `install-*` |
| `init`、`init --force` or `update` / `tooling-absent-preserved-data` | `install` | `preserve-only` | `install-*` |
| `init --force` or `update` / exact `legacy-0.2.3` | `install` | `preserve-only` | `legacy-migration-*` |
| `init --force` or `update` / `ready` | `update` | `preserve-only` | `update-*` |
| `uninstall` / exact legacy、ready、incomplete uninstall、tooling absent | `uninstall` | `preserve-only` | `uninstall-*` |
| `uninstall --remove-specs` | `null` | `null` in public result; no record read/write | `spec-history-purge-removed` |

Exact migration is therefore not a fourth durable operation enum. It is `operation="install"` plus `seed_policy="preserve-only"` and a `legacy-migration-*` public code. Once the first new incomplete record is published, resume is indistinguishable from a preserve-only install by design and does not re-read legacy authority。

### WIR-REC-004 — Golden durable records

Ready after fresh init, where `D` is a lowercase 64-hex digest:

```json
{"schema_version":1,"state":"ready","operation":null,"version":"0.2.4","candidate_digest":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","seed_policy":"create-if-absent","skill_slots":{"spec-dock":"0.2.4","spec-dock-grill-with-docs":"0.2.4"}}
```

Incomplete exact migration/update-on-absent/reinstall:

```json
{"schema_version":1,"state":"incomplete","operation":"install","version":"0.2.4","candidate_digest":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","seed_policy":"preserve-only","skill_slots":{"spec-dock":"0.2.4","spec-dock-grill-with-docs":"0.2.4"}}
```

Incomplete ready update:

```json
{"schema_version":1,"state":"incomplete","operation":"update","version":"0.2.4","candidate_digest":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","seed_policy":"preserve-only","skill_slots":{"spec-dock":"0.2.4","spec-dock-grill-with-docs":"0.2.4"}}
```

Tooling absent:

```json
{"schema_version":1,"state":"tooling-absent-preserved-data","operation":null,"version":"0.2.4","candidate_digest":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","seed_policy":"preserve-only","skill_slots":{"spec-dock":"0.2.4","spec-dock-grill-with-docs":"0.2.4"}}
```

Each code block represents the exact single-line bytes followed by one LF. The displayed `D` placeholder is replaced by the actual digest; no placeholder is emitted at runtime。

## 5. Observed-only state enum

`TargetObservation.state` is exactly:

```text
absent
legacy-0.2.3
incomplete
ready
tooling-absent-preserved-data
blocked
```

`absent`、`legacy-0.2.3`、`blocked` are never serialized into the installation record。`blocked` requires one exact top-level public blocked code from §10; there is no observed reason string outside the code enum。

## 6. Phase and last-completed-phase contract

### WIR-PHASE-001 — Exact enum

`phase` is exactly one of:

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

`last_completed_phase` is one of the same values plus exact `not-started`。

### WIR-PHASE-002 — Exact operation sequences

Install with `create-if-absent`:

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

Install with `preserve-only`:

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

`bootstrap-container` is retained in the sequence even when the shared container already exists; it completes as a no-mutation bind/identity verification。

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

Removed purge trap and parser/request errors do not enter a lifecycle sequence. Their exact pair is `phase="request-validation"`、`last_completed_phase="not-started"`。

### WIR-PHASE-003 — Pair relation

- During a running, blocked, or partial result, `phase` is the phase being attempted or rejected and `last_completed_phase` is the immediately preceding member of the selected sequence. At the first phase, the predecessor is `not-started`。
- `planned/uninstall-planned`: `phase="complete"`、`last_completed_phase="preflight"`。
- `completed/uninstall-already-absent`: `phase="complete"`、`last_completed_phase="preflight"`、`mutation_started=false`。
- Clean terminal completion: `phase="complete"`、`last_completed_phase="cleanup-stage"`。
- `completed_with_warnings` caused by stage cleanup: `phase="complete"`、`last_completed_phase="publish-terminal-record"`。
- A phase pair that is not one of these exact adjacent/terminal relations is invalid wire data。
- `pending_paths` may contain only paths whose mutation phase is strictly after `last_completed_phase` in the selected sequence。

## 7. Slot marker wire

Each owned slot contains `.spec-dock-provider-slot.json` with exact bytes/order:

```json
{"schema_version":1,"slot":"spec-dock","version":"0.2.4","candidate_digest":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd"}
```

For the grill slot, `slot` is exact `spec-dock-grill-with-docs`。Exact keys only; max 2048 bytes; regular file; link count 1; mode `0644`; one LF。Marker is excluded from candidate digest to avoid self-reference。

## 8. Public result object

### WIR-RES-001 — Exact top-level fields

Key order, types, and nullability:

| Order | Field | Type | Nullability / rule |
|---:|---|---|---|
| 1 | `schema_version` | integer | exact `1` |
| 2 | `target` | string | non-null; normalized public target label |
| 3 | `mode` | string | `dry-run` or `apply` |
| 4 | `apply` | boolean | exact CLI request echo; init/update are always `true` |
| 5 | `specs_mode` | string or null | `null`、`keep`、`remove`; only uninstall may be non-null |
| 6 | `status` | string | §9 enum |
| 7 | `code` | string | §10 enum |
| 8 | `operation` | string or null | `install`、`update`、`uninstall` or `null` |
| 9 | `candidate_digest` | string or null | non-null after candidate identity is known; null before candidate admission and for purge trap |
| 10 | `seed_policy` | string or null | non-null iff operation is non-null and seed policy has been admitted |
| 11 | `mutation_started` | boolean | true iff incomplete record was published or bootstrap cleanup failed |
| 12 | `bootstrap_rolled_back` | boolean | true only when a newly-created shared container was restored to exact absent pre-state before returning |
| 13 | `phase` | string | §6 enum |
| 14 | `last_completed_phase` | string | §6 enum plus `not-started` |
| 15 | `retry_command` | string or null | exact relation in §10/§11 |
| 16 | `failed_paths` | array of string | unique, `TARGET_PATH_ORDER` |
| 17 | `pending_paths` | array of string | unique, `TARGET_PATH_ORDER`; each appears in `failed_paths` or is later than the failed phase |
| 18 | `summary` | object | exact keys/order: `planned`,`completed`,`preserved`,`pending`,`failed`,`warnings`; nonnegative integers |
| 19 | `actions` | array of action | exact action schema andorder §12 |
| 20 | `guidance` | array of string | exact code-bound lines §11; never null |
| 21 | `warnings` | array of string | exact fixed messages; never null |
| 22 | `errors` | array of string | exact fixed messages; never null |

No additional field is permitted。`summary` counts `actions.status`: `planned`、`completed`、`preserved`、`pending`、`failed`、`warning` respectively。For action-free blocked/error results all six counts are0。

## 9. Status enum and global relation

| Status | Exit | Mutation relation | Allowed action statuses |
|---|---:|---|---|
| `planned` | 0 | false | `planned`,`preserved` |
| `completed` | 0 | false or true asfixed bycode | `completed`,`preserved` |
| `completed_with_warnings` | 0 | true | `completed`,`preserved`,`warning` |
| `blocked` | 1 | false | actions must beempty |
| `partial_failure` | 1 | true | `completed`,`preserved`,`pending`,`failed` |
| `error` | 2 | false | actions must beempty |

`blocked` never exposes a partial plan because doing so would reveal untrusted path details and could be misread as mutation authority。

## 10. Closed code relation matrix

`apply=request` below means exact echo of the request boolean; `operation=request` means the exact operation selected by §4.3. These are deterministic functions, not implementation choices。

| Code | Status | Operation | Apply | `mutation_started` | Retry | Exit |
|---|---|---|---|---:|---|---:|
| `install-completed` | completed | install | true | true | null | 0 |
| `install-completed-with-cleanup-warning` | completed_with_warnings | install | true | true | null | 0 |
| `update-completed` | completed | update | true | true | null | 0 |
| `update-completed-with-cleanup-warning` | completed_with_warnings | update | true | true | null | 0 |
| `legacy-migration-completed` | completed | install | true | true | null | 0 |
| `legacy-migration-completed-with-cleanup-warning` | completed_with_warnings | install | true | true | null | 0 |
| `uninstall-planned` | planned | uninstall | false | false | null | 0 |
| `uninstall-completed` | completed | uninstall | true | true | null | 0 |
| `uninstall-already-absent` | completed | uninstall | true | false | null | 0 |
| `uninstall-completed-with-cleanup-warning` | completed_with_warnings | uninstall | true | true | null | 0 |
| `already-initialized` | blocked | install | true | false | null | 1 |
| `tooling-not-installed` | blocked | uninstall | request | false | null | 1 |
| `installation-record-invalid` | blocked | request | request | false | null | 1 |
| `installation-record-state-inconsistent` | blocked | request | request | false | null | 1 |
| `resume-operation-mismatch` | blocked | request | request | false | null | 1 |
| `resume-candidate-mismatch` | blocked | request | request | false | null | 1 |
| `resume-seed-policy-mismatch` | blocked | request | request | false | null | 1 |
| `candidate-invalid` | blocked | install or update | true | false | null | 1 |
| `candidate-digest-mismatch` | blocked | install or update | true | false | null | 1 |
| `unsafe-repository-binding` | blocked | request | request | false | null | 1 |
| `unsafe-parent-binding` | blocked | request | request | false | null | 1 |
| `unsafe-target-type` | blocked | request | request | false | null | 1 |
| `foreign-tooling-root` | blocked | request | request | false | null | 1 |
| `foreign-skill-slot` | blocked | request | request | false | null | 1 |
| `unsupported-legacy-version` | blocked | request | request | false | null | 1 |
| `active-legacy-recovery` | blocked | request | request | false | null | 1 |
| `modified-legacy-workspace` | blocked | request | request | false | null | 1 |
| `atomic-rename-unavailable` | blocked | request | request | false | null | 1 |
| `stage-owner-mismatch` | blocked | request | request | false | null | 1 |
| `bootstrap-container-conflict` | blocked | install | true | false | null | 1 |
| `bootstrap-cleanup-failed` | partial_failure | install | true | true | canonical install retry | 1 |
| `install-partial-failure` | partial_failure | install | true | true | canonical install retry | 1 |
| `update-partial-failure` | partial_failure | update | true | true | canonical update retry | 1 |
| `uninstall-partial-failure` | partial_failure | uninstall | true | true | canonical uninstall retry | 1 |
| `invalid-request` | error | null | request | false | null | 2 |
| `spec-history-purge-removed` | error | null | request | false | null | 2 |

No other code is valid。`candidate-invalid` and `candidate-digest-mismatch` cannot occur for uninstall because uninstall does not build a new candidate。`bootstrap-container-conflict` occurs only before a new container is accepted; a cleanup failure uses `bootstrap-cleanup-failed`。

## 11. Retry, guidance, warning, and error text

### WIR-TEXT-001 — Canonical retry commands

Target shell representation is `shlex.join([target])` after normalized target resolution. The exact commands are:

| Operation / policy | `retry_command` |
|---|---|
| install + `create-if-absent` | `spec-dock init --force -- <quoted-target>` |
| install + `preserve-only` | `spec-dock update -- <quoted-target>` |
| update | `spec-dock update -- <quoted-target>` |
| uninstall | `spec-dock uninstall --apply --keep-specs -- <quoted-target>` |

Only the four partial-failure codes have non-null retry。Blocked, error, planned, completed, andwarning-completed results have null retry。

### WIR-TEXT-002 — Exact code messages

| Code family | Exact `errors` or `warnings` string |
|---|---|
| `*-completed-with-cleanup-warning` | warning: `Provider tooling reached the requested terminal state, but the owned external stage could not be removed.` |
| `already-initialized` | error: `SpecDock tooling is already installed; use init --force or update.` |
| `tooling-not-installed` | error: `SpecDock tooling is not installed for this target.` |
| `installation-record-invalid` | error: `The SpecDock installation record is invalid.` |
| `installation-record-state-inconsistent` | error: `The SpecDock installation record does not match the observed tooling state.` |
| `resume-operation-mismatch` | error: `The incomplete operation can be resumed only with the same operation.` |
| `resume-candidate-mismatch` | error: `The incomplete operation can be resumed only with the same candidate digest.` |
| `resume-seed-policy-mismatch` | error: `The incomplete operation can be resumed only with the same seed policy.` |
| `candidate-invalid` | error: `The packaged provider candidate is invalid.` |
| `candidate-digest-mismatch` | error: `The staged provider candidate digest does not match the packaged candidate.` |
| `unsafe-repository-binding` | error: `The repository root binding is unsafe or changed during the operation.` |
| `unsafe-parent-binding` | error: `A required parent directory binding is unsafe or changed during the operation.` |
| `unsafe-target-type` | error: `A fixed provider target has an unsupported filesystem type.` |
| `foreign-tooling-root` | error: `A fixed tooling root exists without provider ownership evidence.` |
| `foreign-skill-slot` | error: `A fixed skill slot exists without matching provider ownership evidence.` |
| `unsupported-legacy-version` | error: `This legacy SpecDock version is not eligible for automatic migration.` |
| `active-legacy-recovery` | error: `Legacy recovery evidence is active; complete recovery with the last compatible package before migration.` |
| `modified-legacy-workspace` | error: `The legacy 0.2.3 tooling payload is not an exact clean migration source.` |
| `atomic-rename-unavailable` | error: `The required native atomic rename primitive is unavailable.` |
| `stage-owner-mismatch` | error: `The existing provider stage does not match this repository, operation, candidate, and seed policy.` |
| `bootstrap-container-conflict` | error: `The shared spec-dock container cannot be safely created or bound.` |
| `bootstrap-cleanup-failed` | error: `The fresh container bootstrap failed and could not be restored to the exact absent pre-state.` |
| `install-partial-failure` | error: `SpecDock install stopped after durable mutation; rerun the exact retry command.` |
| `update-partial-failure` | error: `SpecDock update stopped after durable mutation; rerun the exact retry command.` |
| `uninstall-partial-failure` | error: `SpecDock uninstall stopped after durable mutation; rerun the exact retry command.` |
| `invalid-request` | error: `The SpecDock lifecycle request is invalid.` |
| `spec-history-purge-removed` | error: `Spec history purge has been removed; uninstall is tooling-only.` |

Success/planned codes, including `uninstall-already-absent`, have empty `errors`。Only cleanup-warning codes have one warning。All other codes have empty `warnings`。

### WIR-TEXT-003 — Exact guidance arrays

- `active-legacy-recovery`: `[
  "Run the last compatible SpecDock package with the same legacy operation until its recovery markers are cleared.",
  "Do not delete, rename, or convert legacy recovery files manually."
]`
- Four partial-failure codes: `[
  "Rerun only the retry_command shown in this result.",
  "Do not switch operation, candidate package, or seed policy."
]`
- `spec-history-purge-removed`: `[
  "Use tooling-only uninstall without --remove-specs.",
  "Spec history and Workbench data remain consumer-owned."
]`
- Every other code: `[]`。

## 12. Action wire contract

### WIR-ACT-001 — Exact fields

Each action has exact key order:

```json
{"path":"spec-dock/docs","category":"root","status":"planned","reason":"candidate-root-replace"}
```

Types: all four are non-null strings。No error/message field exists inside an action; top-level errors/warnings own diagnostics。

### WIR-ACT-002 — Closed category/status/reason matrix

| Category | Reason | Allowed action status | Allowed top-level operation |
|---|---|---|---|
| `container` | `fresh-container-create` | planned, completed, pending, failed | install |
| `container` | `shared-container-preserve` | preserved | install, update, uninstall |
| `record` | `incomplete-record-publish` | planned, completed, pending, failed | install, update, uninstall |
| `record` | `terminal-record-publish` | planned, completed, pending, failed | install, update, uninstall |
| `record` | `terminal-record-current` | preserved | uninstall |
| `root` | `candidate-root-create` | planned, completed, pending, failed | install, update |
| `root` | `candidate-root-replace` | planned, completed, pending, failed | install, update |
| `root` | `candidate-root-current` | preserved | install, update |
| `root` | `owned-root-remove` | planned, completed, pending, failed | uninstall |
| `root` | `owned-root-absent` | preserved | uninstall |
| `slot` | `candidate-slot-create` | planned, completed, pending, failed | install, update |
| `slot` | `candidate-slot-replace` | planned, completed, pending, failed | install, update |
| `slot` | `candidate-slot-current` | preserved | install, update |
| `slot` | `owned-slot-remove` | planned, completed, pending, failed | uninstall |
| `slot` | `owned-slot-absent` | preserved | uninstall |
| `seed` | `fresh-seed-create` | planned, completed, pending, failed | install + create-if-absent |
| `seed` | `consumer-seed-present` | preserved | install + create-if-absent |
| `seed` | `preserve-only-seed` | preserved | install/update/uninstall + preserve-only |
| `stage` | `candidate-stage-create` | completed, pending, failed | install, update, uninstall |
| `stage` | `candidate-stage-reuse` | preserved | install, update, uninstall |
| `stage` | `candidate-stage-cleanup` | completed, pending, failed | install, update, uninstall |
| `stage` | `candidate-stage-cleanup-warning` | warning | install, update, uninstall |
| `preservation` | `consumer-data-preserve` | preserved | install, update, uninstall |

No additional reason/category/status is valid。

### WIR-ACT-003 — Top-level status relation

- `planned`: uninstall dry-run actions contain only planned/preserved reasons valid for uninstall。
- `completed`: actions contain only completed/preserved。
- `completed_with_warnings`: exactly one `@provider-stage` action with category `stage`, status `warning`, reason `candidate-stage-cleanup-warning`; all other actions completed/preserved。
- `partial_failure`: exactly one failed action at`phase`; later authorized actions pending; earlier actions completed/preserved。The failed/pending arrays follow `TARGET_PATH_ORDER`。
- `blocked` and `error`: actions empty。

### WIR-ACT-004 — Exact code-to-phase/action relation

| Code set | Exact phase pair | Exact action relation |
|---|---|---|
| `install-completed`、`update-completed`、`legacy-migration-completed`、`uninstall-completed` | `complete` / `cleanup-stage` | operation-complete action set; every authorized target is `completed` or `preserved`; stage cleanup is `completed` when present |
| four `*-completed-with-cleanup-warning` codes | `complete` / `publish-terminal-record` | exactly one `@provider-stage` warning action with reason `candidate-stage-cleanup-warning`; every other action is `completed` or `preserved` |
| `uninstall-planned` | `complete` / `preflight` | full uninstall dry-run action set; mutable owned targets are `planned`, protected/container/seed targets are `preserved` |
| `uninstall-already-absent` | `complete` / `preflight` | exact preserved set: shared container、record、two seeds; roots/slots are omitted because no mutation action exists |
| `bootstrap-cleanup-failed` | `bootstrap-container` / `candidate-staging` | one failed container action `fresh-container-create`; stage cleanup is pending; all later authorized actions are pending in `TARGET_PATH_ORDER` |
| `install-partial-failure`、`update-partial-failure`、`uninstall-partial-failure` | current operation sequence phase / its exact predecessor | exactly one action matching `phase` is `failed`; earlier actions are `completed` or `preserved`; later authorized actions are `pending` |
| all blocked codes | rejected phase / exact sequence predecessor or `not-started` | actions empty; failed/pending paths empty; the code itself is the only public rejection reason |
| `invalid-request`、`spec-history-purge-removed` | `request-validation` / `not-started` | actions, failed paths, and pending paths are empty |

The phrase “operation-complete action set” is not an extensibility token。It means the finite action rows admitted by WIR-ACT-002 for the selected WIR-REC-003 operation and the observed target state。Any action reason not listed in WIR-ACT-002, or any code/action relation not listed above, is invalid。

## 13. Exact public JSON goldens

The following objects are serialized compactly with one LF using §2. `D` is replaced by one actual digest; examples use 64 lowercase `d` characters。

### WIR-GOLDEN-U1 — Uninstall dry-run

```json
{"schema_version":1,"target":"/tmp/consumer","mode":"dry-run","apply":false,"specs_mode":null,"status":"planned","code":"uninstall-planned","operation":"uninstall","candidate_digest":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","seed_policy":"preserve-only","mutation_started":false,"bootstrap_rolled_back":false,"phase":"complete","last_completed_phase":"preflight","retry_command":null,"failed_paths":[],"pending_paths":[],"summary":{"planned":7,"completed":0,"preserved":3,"pending":0,"failed":0,"warnings":0},"actions":[{"path":"spec-dock","category":"container","status":"preserved","reason":"shared-container-preserve"},{"path":"spec-dock/spec-dock.version","category":"record","status":"planned","reason":"terminal-record-publish"},{"path":"spec-dock/docs","category":"root","status":"planned","reason":"owned-root-remove"},{"path":"spec-dock/templates","category":"root","status":"planned","reason":"owned-root-remove"},{"path":"spec-dock/system","category":"root","status":"planned","reason":"owned-root-remove"},{"path":"spec-dock/scripts","category":"root","status":"planned","reason":"owned-root-remove"},{"path":".agents/skills/spec-dock","category":"slot","status":"planned","reason":"owned-slot-remove"},{"path":".agents/skills/spec-dock-grill-with-docs","category":"slot","status":"planned","reason":"owned-slot-remove"},{"path":"spec-dock/.gitignore","category":"seed","status":"preserved","reason":"preserve-only-seed"},{"path":".github/workflows/ci.yml","category":"seed","status":"preserved","reason":"preserve-only-seed"}],"guidance":[],"warnings":[],"errors":[]}
```

### WIR-GOLDEN-U2 — Successful uninstall apply

```json
{"schema_version":1,"target":"/tmp/consumer","mode":"apply","apply":true,"specs_mode":"keep","status":"completed","code":"uninstall-completed","operation":"uninstall","candidate_digest":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","seed_policy":"preserve-only","mutation_started":true,"bootstrap_rolled_back":false,"phase":"complete","last_completed_phase":"cleanup-stage","retry_command":null,"failed_paths":[],"pending_paths":[],"summary":{"planned":0,"completed":7,"preserved":3,"pending":0,"failed":0,"warnings":0},"actions":[{"path":"spec-dock","category":"container","status":"preserved","reason":"shared-container-preserve"},{"path":"spec-dock/spec-dock.version","category":"record","status":"completed","reason":"terminal-record-publish"},{"path":"spec-dock/docs","category":"root","status":"completed","reason":"owned-root-remove"},{"path":"spec-dock/templates","category":"root","status":"completed","reason":"owned-root-remove"},{"path":"spec-dock/system","category":"root","status":"completed","reason":"owned-root-remove"},{"path":"spec-dock/scripts","category":"root","status":"completed","reason":"owned-root-remove"},{"path":".agents/skills/spec-dock","category":"slot","status":"completed","reason":"owned-slot-remove"},{"path":".agents/skills/spec-dock-grill-with-docs","category":"slot","status":"completed","reason":"owned-slot-remove"},{"path":"spec-dock/.gitignore","category":"seed","status":"preserved","reason":"preserve-only-seed"},{"path":".github/workflows/ci.yml","category":"seed","status":"preserved","reason":"preserve-only-seed"}],"guidance":[],"warnings":[],"errors":[]}
```

### WIR-GOLDEN-U3 — Partial uninstall after docs detach

```json
{"schema_version":1,"target":"/tmp/consumer","mode":"apply","apply":true,"specs_mode":"keep","status":"partial_failure","code":"uninstall-partial-failure","operation":"uninstall","candidate_digest":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","seed_policy":"preserve-only","mutation_started":true,"bootstrap_rolled_back":false,"phase":"detach-templates","last_completed_phase":"detach-docs","retry_command":"spec-dock uninstall --apply --keep-specs -- /tmp/consumer","failed_paths":["spec-dock/templates","spec-dock/system","spec-dock/scripts",".agents/skills/spec-dock",".agents/skills/spec-dock-grill-with-docs","@provider-stage"],"pending_paths":["spec-dock/system","spec-dock/scripts",".agents/skills/spec-dock",".agents/skills/spec-dock-grill-with-docs","@provider-stage"],"summary":{"planned":0,"completed":2,"preserved":3,"pending":5,"failed":1,"warnings":0},"actions":[{"path":"spec-dock","category":"container","status":"preserved","reason":"shared-container-preserve"},{"path":"spec-dock/spec-dock.version","category":"record","status":"completed","reason":"incomplete-record-publish"},{"path":"spec-dock/docs","category":"root","status":"completed","reason":"owned-root-remove"},{"path":"spec-dock/templates","category":"root","status":"failed","reason":"owned-root-remove"},{"path":"spec-dock/system","category":"root","status":"pending","reason":"owned-root-remove"},{"path":"spec-dock/scripts","category":"root","status":"pending","reason":"owned-root-remove"},{"path":".agents/skills/spec-dock","category":"slot","status":"pending","reason":"owned-slot-remove"},{"path":".agents/skills/spec-dock-grill-with-docs","category":"slot","status":"pending","reason":"owned-slot-remove"},{"path":"spec-dock/.gitignore","category":"seed","status":"preserved","reason":"preserve-only-seed"},{"path":".github/workflows/ci.yml","category":"seed","status":"preserved","reason":"preserve-only-seed"},{"path":"@provider-stage","category":"stage","status":"pending","reason":"candidate-stage-cleanup"}],"guidance":["Rerun only the retry_command shown in this result.","Do not switch operation, candidate package, or seed policy."],"warnings":[],"errors":["SpecDock uninstall stopped after durable mutation; rerun the exact retry command."]}
```

### WIR-GOLDEN-U4 — Removed purge trap

```json
{"schema_version":1,"target":"/tmp/consumer","mode":"apply","apply":true,"specs_mode":"remove","status":"error","code":"spec-history-purge-removed","operation":null,"candidate_digest":null,"seed_policy":null,"mutation_started":false,"bootstrap_rolled_back":false,"phase":"request-validation","last_completed_phase":"not-started","retry_command":null,"failed_paths":[],"pending_paths":[],"summary":{"planned":0,"completed":0,"preserved":0,"pending":0,"failed":0,"warnings":0},"actions":[],"guidance":["Use tooling-only uninstall without --remove-specs.","Spec history and Workbench data remain consumer-owned."],"warnings":[],"errors":["Spec history purge has been removed; uninstall is tooling-only."]}
```

### WIR-GOLDEN-U5 — Idempotent apply after tooling-only uninstall

```json
{"schema_version":1,"target":"/tmp/consumer","mode":"apply","apply":true,"specs_mode":null,"status":"completed","code":"uninstall-already-absent","operation":"uninstall","candidate_digest":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","seed_policy":"preserve-only","mutation_started":false,"bootstrap_rolled_back":false,"phase":"complete","last_completed_phase":"preflight","retry_command":null,"failed_paths":[],"pending_paths":[],"summary":{"planned":0,"completed":0,"preserved":4,"pending":0,"failed":0,"warnings":0},"actions":[{"path":"spec-dock","category":"container","status":"preserved","reason":"shared-container-preserve"},{"path":"spec-dock/spec-dock.version","category":"record","status":"preserved","reason":"terminal-record-current"},{"path":"spec-dock/.gitignore","category":"seed","status":"preserved","reason":"preserve-only-seed"},{"path":".github/workflows/ci.yml","category":"seed","status":"preserved","reason":"preserve-only-seed"}],"guidance":[],"warnings":[],"errors":[]}
```

### WIR-GOLDEN-I1 — Partial preserve-only install

```json
{"schema_version":1,"target":"/tmp/consumer","mode":"apply","apply":true,"specs_mode":null,"status":"partial_failure","code":"install-partial-failure","operation":"install","candidate_digest":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","seed_policy":"preserve-only","mutation_started":true,"bootstrap_rolled_back":false,"phase":"publish-system","last_completed_phase":"publish-templates","retry_command":"spec-dock update -- /tmp/consumer","failed_paths":["spec-dock/system","spec-dock/scripts",".agents/skills/spec-dock",".agents/skills/spec-dock-grill-with-docs","@provider-stage"],"pending_paths":["spec-dock/scripts",".agents/skills/spec-dock",".agents/skills/spec-dock-grill-with-docs","@provider-stage"],"summary":{"planned":0,"completed":3,"preserved":3,"pending":4,"failed":1,"warnings":0},"actions":[{"path":"spec-dock","category":"container","status":"preserved","reason":"shared-container-preserve"},{"path":"spec-dock/spec-dock.version","category":"record","status":"completed","reason":"incomplete-record-publish"},{"path":"spec-dock/docs","category":"root","status":"completed","reason":"candidate-root-replace"},{"path":"spec-dock/templates","category":"root","status":"completed","reason":"candidate-root-replace"},{"path":"spec-dock/system","category":"root","status":"failed","reason":"candidate-root-replace"},{"path":"spec-dock/scripts","category":"root","status":"pending","reason":"candidate-root-replace"},{"path":".agents/skills/spec-dock","category":"slot","status":"pending","reason":"candidate-slot-replace"},{"path":".agents/skills/spec-dock-grill-with-docs","category":"slot","status":"pending","reason":"candidate-slot-replace"},{"path":"spec-dock/.gitignore","category":"seed","status":"preserved","reason":"preserve-only-seed"},{"path":".github/workflows/ci.yml","category":"seed","status":"preserved","reason":"preserve-only-seed"},{"path":"@provider-stage","category":"stage","status":"pending","reason":"candidate-stage-cleanup"}],"guidance":["Rerun only the retry_command shown in this result.","Do not switch operation, candidate package, or seed policy."],"warnings":[],"errors":["SpecDock install stopped after durable mutation; rerun the exact retry command."]}
```

## 14. Public text contract

### WIR-PUB-001 — Init/update success

Stdout, one LF:

```text
spec-dock: ok (init) -> /tmp/consumer
```

```text
spec-dock: ok (update) -> /tmp/consumer
```

Exact legacy migration invoked through update uses the update success line. `init --force` uses the init success line. Cleanup warning appends exactly one second line:

```text
warning: Provider tooling reached the requested terminal state, but the owned external stage could not be removed.
```

### WIR-PUB-002 — Init/update blocked/partial/error

Stderr first line:

```text
error: <code>: <exact error message from §11.2>
```

If `retry_command` is non-null, stderr second line:

```text
retry: <retry_command>
```

No other line is emitted by the installer adapter。Parser-generated argparse usage remains argparse-owned and is outside this lifecycle result wire。

### WIR-PUB-003 — Uninstall text mode

Exact line order:

```text
spec-dock: uninstall <status> (<code>)
target: <target>
mode: <dry-run|apply>
phase: <phase>
last-completed-phase: <last_completed_phase>
seed-policy: <seed_policy|null>
retry-command: <retry_command|null>
failed-paths: <comma-separated paths or none>
pending-paths: <comma-separated paths or none>
actions:
  <status> <category> <path> <reason>
warnings:
  <warning or none>
errors:
  <error or none>
```

Actions and path lists use `TARGET_PATH_ORDER`。Null renders exact `null`; empty collection renders exact `none`。Exit is §10。

## 15. Required tests and trace

The implementation must include table-driven tests that reject every value not present in this Artifact and cover:

1. all record state/operation/seed-policy relations;
2. all phase sequences andinvalid non-adjacent pairs;
3. all code/status/operation/apply/mutation/retry/exit rows;
4. all action category/status/reason relations;
5. `TARGET_PATH_ORDER` for all three arrays andgoldens;
6. exact compact JSON bytes for WIR-GOLDEN-U1〜U5 and I1;
7. exact text bytes for WIR-PUB-001〜003;
8. unknown field/enum/reason/code andduplicate path rejection;
9. CLI andservice result mapping parity;
10. exact dogfood record andslot marker bytes after S60 andS70 updates。

Normative traces:

- Epic: E384-RQ-003、006〜010、022、E384-D-006〜013、026。
- Issue: I392-RQ-004〜019、028、I392-D-001〜010、017。
- Plan: I392-S10、S20、S30、S40、S50、S60、S70。

Owner decisions required: none。
