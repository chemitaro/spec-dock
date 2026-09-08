---
種別: Normative Artifact
ID: "provider-lifecycle-wire-contract-v12"
タイトル: "Provider Lifecycle Wire Contract"
状態: "parent-contract-candidate"
最終更新: "2026-09-08"
対象: ["epic-00384", "iss-00392", "iss-00395", "iss-00396"]
repository_evidence:
  role: "authoring-source-provenance"
  repository: "chemitaro/spec-dock"
  branch: "codex/epic-00384-provider-test-strategy-planning"
  sha: "240e561e94b50250a4a6309452a7fd0fb511458a"
  tree: "181f7eb28da0edff3ca1352edf4cb2ae1f21d433"
---

# Provider Lifecycle Wire Contract

> **2026-09-08 v12 親契約改訂:** ユーザーがP392-001/002の親修正を承認した。準備・初期レコード公開の失敗をWIR-PREP-001で閉じる。旧35 public goldensと4 record goldensは保持し、closed codeを1個、relationを16行、public goldenを5個追加する。詳細は[準備失敗ADR](20260908t011139z-adr-lifecycle-preparation-and-initial-record-failure-contract.md)。以下のv11採用経緯は履歴であり、v12のreview/freezeは別候補として証明する。

> **v11履歴:** `E384-DEC-001` と `E384-DEC-002` はユーザー採用済みである。v11は初回だけの停止移行、以後のruntime/lifecycle共有coordination、同世代checkout、変更先worktreeの排他と公開/handoff境界を§16で固定する。v10のrecord/cleanup/replay契約を維持し、pre-observationのclosed code二つ・関係行四つ・public JSON例二つを追加した。前候補のwire-only fail/whole-plan blockedは履歴として保存し、本候補の独立review・公開freezeは候補hashに紐づく外部receiptで別に証明する。本書の存在だけをIssue startまたは実装許可のreceiptにしない。詳しくは[全体再評価ADR](20260907t234210z-adr-whole-plan-reassessment-and-executable-gates.md)。

## 1. Authority and closed-world rule

本ArtifactはEpic #384が固定するprovider lifecycle public wireの唯一のnormative authorityである。Issue #392はこのwireへ適合するproduction lifecycleのsole writerである。Issues #395と#396はread-only consumerであり、field、enum、code、phase、reason、path、relation、serialization、compatibility、retryまたはorderingを追加・変更・再解釈してはならない。Production enum、dataclass、constructor、serializer、CLI text/JSON、golden、fault/migration evidenceは本書のfinite tablesだけを使用する。未知のfield、enum、code、phase、reason、path、relationは生成・受理せずfail closedする。`other`、`unknown`、`generic`、`internal-error`、free-form reason、catch-all mapping、dictionary/filesystem orderはwire valueとして禁止する。予期しない未型付け例外は本wire codeへ丸めずprocess/test defectとして失敗させる。

### WIR-OWN-001 — Cross-Issue ownership and immutability

| Actor | Authority |
|---|---|
| Epic #384 parent | Freeze this artifact and adjudicate any proposed semantic change before an Issue starts. |
| Issue #392 | Sole production writer and sole implementation owner for lifecycle behavior and wire conformance. |
| Issue #395 | Read-only consumer. Product defect repairs must preserve lifecycle semantics and serialized values. |
| Issue #396 | Read-only consumer. Provider-gate and policy cutover may verify but not redefine this wire. |

Any semantic change requires a superseding parent ADR, revalidation of affected Issue drafts, dependency-chain restart from the affected state and independent review under the Rolling-Wave Contract. When Issue boundaries or copied values change, regenerate those draft portions. Before any Issue implementation is accepted, the restart point is B0; unchanged reference-only Issue drafts need no invented implementation detail. Revision v10 was governed by [Preimplementation Clarifications ADR](20260907t223933z-adr-preimplementation-recovery-and-qualification-clarifications.md); v11 adds the parent-adopted coordination boundary under [Whole-plan Reassessment ADR](20260907t234210z-adr-whole-plan-reassessment-and-executable-gates.md). The user-authorized v12 revision is governed by [Preparation Failure ADR](20260908t011139z-adr-lifecycle-preparation-and-initial-record-failure-contract.md). It is authored while #392 is selected but before any Product implementation. Rolling-wave elaboration may add implementation details and tests but cannot change this artifact.

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
| public code values | 41 |
| `phase` values | 23 |
| `last_completed_phase` values | 24 |
| durable record goldens | 4 |
| complete code/context relation rows | 168 |
| public JSON review goldens | 40 |

The implementation test extracts the §10 table and all fenced JSON review goldens from this file, verifies these counts, parses every JSON block, and asserts one terminal LF. It additionally parameterizes all seven cleanup-warning rows and requires `retry_command == continuation.next_command == active.cleanup_retry_command` with a matching hidden token. The forty public JSON review goldens include five preparation outcomes; the existing thirty-five and the four durable goldens are retained byte-for-byte. Warning tokenization remains proven by the seven finite matrix rows. WIR-COORD-004's four runtime bootstrap diagnostics are a separate pre-parser surface, not four additional lifecycle codes or lifecycle JSON goldens. A count drift is a specification/test defect and is not auto-accepted.

Table expressions are exact value functions:

- `request.candidate_digest`: validated packaged candidate digest selected for the invocation.
- `record.candidate_digest` / `record.seed_policy` / `record.operation`: exact values parsed from the valid record. In the existing resume-mismatch rows only, WIR-PREP-001 extends an "incomplete operation" context to a validated prepared ACTIVE: these three values then come from that bound recovery tuple, without asserting that an incomplete Consumer record exists. All non-resume rows keep their literal record meaning.
- `legacy_fixture.aggregate_digest`: exact deterministic aggregate of the recognized `0.2.3` roots/slots.
- `owned_target_digest`: `record.candidate_digest` for final-format state, otherwise `legacy_fixture.aggregate_digest` for exact legacy state.
- `null`: public JSON null. These expressions are not implementation choices.
- `active.operation` / `active.candidate_digest` / `active.seed_policy`: exact values from validated `ACTIVE.json`.
- `active.result_family`: exact private enum `install|legacy-migration|update|uninstall`, written before target mutation and used only to select the cleanup retry command. It is not part of the resume tuple or public result.
- `actual_request.mode` / `actual_request.apply` / `actual_request.specs_mode`: exact parser-normalized echo selected by WIR-CLEANUP-001 before repository locking. These values describe the invocation that encountered pending terminal cleanup; they do not change the old ACTIVE operation/digest/policy exposed by the result.
- `active.deferred_invocation`: private null or exact object with ordered keys `invocation_id,rendered_command`. `invocation_id` is one of `init|init-force|update|uninstall-dry-run|uninstall-dry-run-keep|uninstall-apply|uninstall-apply-keep`; `rendered_command` is the corresponding WIR-TEXT-001 command. Every no-token public invocation is a desired request. The first desired request is durably preserved until cleanup completes; tokenized retry, repeat, or later desired invocation cannot replace it.
- `active.operation_generation`: fresh 128-bit cryptographically random value serialized as 32 lowercase hex characters for each new mutation operation; persisted before target mutation and bound into ACTIVE and stage ownership. Resume preserves it. It is not part of the public resume tuple; repeated operations with the same tuple receive different generations.
- `active.cleanup_token`: exact 64-hex SHA-256 of UTF-8 compact JSON array `["spec-dock-terminal-cleanup-v2",repository_key,tuple_key,result_family,operation_generation]` (each element a string, no terminal LF). The generation binds a cleanup retry to one operation instance, not another operation with the same tuple. It is identity binding, not authorization.
- `active.cleanup_retry_invocation`: exact private invocation with `role=cleanup-retry`, the matching `active.cleanup_token`, and public base form `install/create-if-absent -> init-force`, `install/preserve-only -> update`, `legacy-migration -> update`, `update -> update`, `uninstall -> uninstall-apply-keep`.
- `receipt.*`: values from the validated, owner-bound `CLEANUP-COMPLETED.json` specified in WIR-CLEANUP-002. It retains operation, candidate_digest, seed_policy, result_family, operation_generation, cleanup_token, cleanup_retry_invocation and deferred_invocation from the completed ACTIVE. These fields may be read for replay only; they do not authorize lifecycle dispatch.
- `continuation_owner`: closed selection for every cleanup result. Use the validated matching completion receipt whenever it exists; use validated ACTIVE only when no receipt exists. An existing invalid or mismatched receipt is preserve-and-block, never an ACTIVE fallback. Resolve this owner again after any receipt/deferred durable update and before rendering success or failure, even if ACTIVE reconciliation failed. The selected owner's exact deferred_invocation controls both profile selection and command rendering.
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

Parser errors and `uninstall --remove-specs` are request-validation outcomes and do not enter lifecycle cleanup. Every other parser-valid lifecycle invocation normalizes its echo before WIR-COORD-001 repository locking. Coordination admission precedes target classification, ACTIVE/receipt observation, stage preparation and every cleanup/replay path:


### WIR-PREP-001 — Preparation admission and initial-record failure

This section closes preparation failures only; it does not catch arbitrary lifecycle exceptions. The finite new code is `lifecycle-preparation-failed`. A caught expected filesystem resource/access/I/O failure is mapped only at the operations listed below. Root/parent rebinding, unsupported type, hard links, foreign owner, record/schema invalidity, digest mismatch and unavailable native/lock capabilities retain their existing specific diagnostics and precedence. Programming defects remain untyped process/test defects.

**Owner-bound namespace and re-entry.** The private namespace remains outside Consumer data on the same filesystem. Its path is a deterministic function of the bound repository identity and effective user. Its fixed directory chain must be no-follow, owned by that user, mode0700, and on the bound filesystem; creation uses exclusive mkdir and fsync, then binding verification. An exactly bound empty reserved directory left by an interrupted mkdir is valid preparation, not foreign payload. Only the fixed metadata slots and their individually named atomic-write temporary slots are provider bookkeeping; regular/link1/user-owned/mode0600 temporary slots may contain incomplete bytes and may be discarded and recreated after owner/binding validation. An unlisted entry, unsafe directory, foreign owner or unsafe metadata/temp type is preserve-and-block, never a reason to sweep the directory. The Issue fixes the physical path and finite private filenames before implementation. Do not create a stage payload before a valid prepared ACTIVE is durable. Thus an interruption before ACTIVE publication leaves at most this re-enterable bounded namespace/bookkeeping, not an unregistered payload tree. No directory scan discovers other repositories, historical generations or cleanup candidates.

**Prepared operation.** Complete nonmutating admission determines the operation/candidate/seed tuple, result family and exact original record-or-absence before recording a fresh generation. Invalidate an old valid completion receipt only at the existing WIR-CLEANUP-002 accepted new-operation boundary. Atomically publish/fsync `ACTIVE.state=prepared` before stage payload creation or any Consumer write. It binds the tuple/generation, registered fixed stage entries, original fixed-root identities, original record bytes/identity-or-absence, the expected incomplete record bytes, and any same-generation bootstrap-container identity. These are bounded operation witnesses, not per-file history, arbitrary action checkpoints or a rollback image.

A failure publishing prepared ACTIVE has no stage payload and no Consumer mutation. After the I/O condition is repaired, the exact ordinary retry may establish ACTIVE afresh; existing validated prepared authority instead retains its tuple and generation. New candidate bytes may be re-read, but a mismatching tuple does not replace prepared authority. Mismatch uses the existing operation/candidate/seed diagnostics and `stage-owner-mismatch` where appropriate. The diagnostics referring to an incomplete operation include this durable prepared operation; they do not imply that a Consumer record already exists.

**Prepared re-entry.** A no-token request must resolve to the same operation/candidate/seed tuple. Compare the bound target to either (a) the original record-or-absence and fixed-root witnesses or (b) this generation's exact expected incomplete record and still-unpublished fixed roots. Validate both bytes and safe identity; case (b) permits the atomically published replacement inode, not an arbitrary content-equal foreign substitution. The record publication temporary inode is bound before rename in the fixed private witness; it is not a per-file payload journal. If (b) is present after a rename/fsync interruption, re-fsync/revalidate it before advancing. No root is published/detached while ACTIVE remains prepared. Stage payload may be rebuilt only within its already registered, safely bound entries; foreign data is preserved. A preserved same-generation bootstrap container is re-bound, not recreated or inferred from seed presence.

After expected incomplete record and its parent are fsynced and revalidated, atomically publish/fsync `ACTIVE.state=running`, then begin the fixed root sequence. Failure updating ACTIVE at this boundary is still an initial-record preparation failure. Prepared plus expected incomplete is a valid re-entry pair. Neither prepared nor running plus an old terminal record is interpreted as completed work. Once all target content is verified, durably set ACTIVE to `ready` **before** publishing the terminal record; ready plus incomplete retries terminal publication, and ready plus the matching terminal record enters WIR-CLEANUP-001. This closes same-candidate updates whose old and new terminal bytes can be identical.

**Closed failure regions and result selection.**

| Region | Exact boundary | Result |
|---|---|---|
| P0 | Expected I/O while establishing/reading/fsyncing initial private authority, before it can be trusted and before Consumer writes. | §10 preflight apply/dry-run rows; operation/digest/policy null; no retry; Consumer mutation false. Invalid owner/type uses the two preflight stage-owner-mismatch rows, not this code. |
| P1 | After nonmutating candidate/tuple admission, prepared ACTIVE publication and candidate/tombstone stage mkdir/write/fsync, before bootstrap or incomplete publication. | Four §10 candidate-staging rows; Consumer mutation false; exact ordinary tuple retry. No payload exists without durable prepared ACTIVE. |
| P2a | Initial record temporary write/rename/fsync or prepared-to-running update fails, and the original Consumer pre-state is still exact: no same-generation container remains created and no expected incomplete record has been published. | Four blocked §10 publish-incomplete-record rows, empty actions, exact ordinary tuple retry. |
| P2b | The same P2 failure with a same-generation created bootstrap container remaining or own expected incomplete record visible/published (including rename success with parent fsync failure). | Four partial_failure §10 publish-incomplete-record rows and AP-PREP-PARTIAL; exact ordinary tuple retry. |

For P2 the flag describes whether this prepared operation has left a Consumer mutation relative to its recorded original state, including a previous interrupted attempt. Private namespace/stage writes alone never make this flag true. Inability to verify ownership/binding or distinguish the recorded original versus own publication uses the existing safety failure, preserving data; it is not guessed as P2a. P0 is an unadmitted current invocation and does not assert that a previous operation never mutated the Consumer.

The preceding table cannot replace a terminal cleanup result. Once matching terminal cleanup authority is established, failures persisting a desired request, reconciling ACTIVE, removing owned stage, publishing/replaying a completion receipt, or unlinking ACTIVE keep WIR-CLEANUP-001/002 and continuation-owner precedence. The four P1 and eight P2 rows apply only to apply operations. Uninstall dry-run observes prepared state without resuming it: when the original/expected-incomplete state is a validated uninstall preparation, report the ordinary remaining uninstall plan; another prepared operation is a resume-operation-mismatch. Do not capture a desired request as deferred terminal cleanup for a prepared operation.

All preparation retries are non-tokenized WIR-TEXT-001 commands. A token is valid only for already-defined terminal cleanup/replay; prepared/running never accept it as a preparation bypass. No retry queue, implicit operation switch, auto rollback or private-state manual deletion is introduced.

Required fault evidence includes every P0/P1 mkdir/write/fsync boundary, initial ACTIVE before/after durable publication, expected incomplete record before/after rename and parent fsync, prepared-to-running publication failure, same-candidate update, fresh bootstrap retained versus unchanged ready pre-state, interruption before/after ACTIVE ready and terminal record, token rejection during preparation, safe namespace/temp re-entry, and foreign/malformed state preservation. Each uses the exact §10 outcome and repeats the exact continuation when present until the I/O condition is repaired and ready/tooling-absent is reached.

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

`uninstall --remove-specs` is resolved as the request-error trap before repository cleanup and is not cleanup-gated. A token on any unlisted command form or a non-64-lowercase-hex token is exact `invalid-request`, exit 2, mutation false. With ACTIVE present, require its exact generation-bound token and derived invocation form; a receipt cannot override a different active generation. With ACTIVE absent, only the exact matching completion receipt under WIR-CLEANUP-002 permits replay. Missing, mismatched or invalid receipt/token/form is `invalid-request`, exit 2, mutation false; it never falls through to desired lifecycle dispatch.

After repository lock/binding and before target classification or candidate construction, resolve the exact repository `ACTIVE.json` without scanning.

1. ACTIVE absent: fsync the repository-stage directory. An exact token retry with a valid matching completion receipt returns the WIR-CLEANUP-002 replay result only. A no-token invocation continues normal dispatch and retains any valid receipt until the accepted new-mutation boundary; dry-run, admission failure and already-absent observation do not consume it. Emit no cleanup result for this normal no-token dispatch.
2. Terminal record plus `ACTIVE.state=ready`: atomically replace ACTIVE with identical content except `state=terminal-cleanup`; fsync.
3. Normalize the invocation role before cleanup.
   - Token absent: role is `desired`; before any completion receipt exists, atomically store the first exact desired invocation in `active.deferred_invocation` when null, even when its public base form equals the old result-family retry. If already non-null, preserve the first object byte-for-byte; later desired invocations are not queued. Once a matching completion receipt exists, its deferred_invocation is authoritative; use only the one-time null-to-first-request durable update and ACTIVE reconciliation defined in WIR-CLEANUP-002.
   - Exact token present on the exact derived form: role is `cleanup-retry`; never create, replace or clear `deferred_invocation`.
4. Validate namespace, repository, tuple, operation generation, result family, cleanup token, deferred invocation, stage owner and registered entries. Remove only registered entries and exact stage; an already-absent stage is accepted. Fsync removal before publishing its completion receipt.
5. Atomically publish and fsync the exact completion receipt under WIR-CLEANUP-002 before removing ACTIVE. Then remove ACTIVE only by expected-byte/content binding and fsync its parent. A crash after unlink, before parent fsync or before returning the response is recovered through the receipt; never discard its continuation. Receipt publication failure leaves ACTIVE retryable and is a cleanup failure.
6. Cleanup failure returns `terminal-cleanup-failed` and executes no lifecycle operation.
   - `continuation.next_action=retry-cleanup` and `next_command=active.cleanup_retry_command` containing the exact token.
   - `after_cleanup_action/run-request` and `after_cleanup_command` carry the immutable first desired request when present; otherwise `none/null`.
7. Cleanup success from present ACTIVE returns `terminal-cleanup-completed` and executes no lifecycle operation.
   - If the immutable desired request is present, `next_action=run-request` with that exact no-token desired command.
   - If no desired request is present, all continuation values are `none/null`.
8. Thus a no-token desired `update` or `init --force` is machine-distinct from a tokenized cleanup retry with the same public base form. A retry success returns the separately preserved desired command, never the durable old operation by inference. A pure cleanup retry with no desired request returns no next action.
9. Callers execute exactly `continuation.next_command` when `next_action` is not `none`; they never derive a command from actual invocation, `operation`, `result_family`, `retry_command` or prose.

### WIR-CLEANUP-002 — Bounded completion receipt and idempotent replay

The repository's already owner-bound private stage namespace contains at most one fixed `CLEANUP-COMPLETED.json`. It is lifecycle bookkeeping, not a new provider-owned Consumer target. It accepts no arbitrary path, cleanup list or user-data ownership. No scanning, unbounded history or timed deletion is introduced.

1. **Closed receipt identity.** The receipt is a private object containing exactly `schema_version=1`, `repository_key`, `tuple_key`, `operation_generation`, `operation`, `candidate_digest`, `seed_policy`, `result_family`, `terminal_record_digest`, `cleanup_token`, `cleanup_retry_invocation`, and `deferred_invocation`. The last two use the same closed structures as ACTIVE. The terminal digest is SHA-256 of the actual durable terminal record bytes. Existing owner/no-follow/regular-file/link-count/atomic-publication rules apply. Receipt publication cannot overwrite a foreign or unvalidated object.
2. **Durability order.** Validate the terminal record and generation; remove registered stage payload and fsync; atomically publish this receipt and fsync; expected-byte unlink ACTIVE and fsync its parent; only then return completion. No receipt is published for incomplete target state or unfinished stage removal. A crash before receipt publication leaves ACTIVE responsible for retry; a crash after publication leaves the receipt responsible for continuation.
3. **Both records present.** Matching ACTIVE and receipt are one cleanup operation, not two writers. Repository, tuple, generation, result family, token and terminal-record digest must agree. The receipt owns continuation once published. A non-null receipt deferred request with a null ACTIVE field is a recoverable mirror lag: reconcile ACTIVE to the receipt. Different non-null requests, ACTIVE non-null with receipt null, different generations or identity drift are preserve-and-block conditions under existing owner/record validation rules.
4. **First request during completion.** If both records remain and a no-token desired request arrives while both deferred fields are null, durably change only receipt `null -> first exact request`, fsync, then reconcile ACTIVE. A crash between those writes uses rule 3. A later desired request cannot replace the first. A token retry never creates or replaces a desired request. No receipt-only no-token invocation is captured as old cleanup work: WIR-CLEANUP-001 rule 1 dispatches it as a new explicit request.
5. **Receipt-only replay.** With ACTIVE absent, an exact token retry on the exact stored derived form validates repository ownership, generation, recomputed token and actual terminal record digest against the receipt. It performs no lifecycle operation, removes no path and changes neither receipt nor Consumer state. It returns `terminal-cleanup-completed`, `mutation_started=false`, `phase=complete`, `last_completed_phase=cleanup-stage`, null retry_command, empty actions/failed_paths/pending_paths, zero summary and the receipt-derived continuation. Its operation/candidate/seed describe the completed operation, while mode/apply/specs_mode echo the actual retry form. With a deferred request, continuation says `run-request` and carries its exact stored command; without one it is all `none/null`. The six §10 replay rows close these combinations.
6. **Retention and invalidation.** Retain the receipt through repeat token replay, dry-run, admission failure and already-absent observations. Only after a subsequent no-token mutation request passes complete admission, immediately before its new generation/ACTIVE publication and before any target mutation, invalidate the old receipt by expected-byte binding and fsync. Then establish the fresh generation. If interrupted between invalidation and new ACTIVE, the target is unchanged and the explicit no-token request may be retried; the expired old token is invalid. Unknown receipt bytes are never deleted to make progress.
7. **No token collision by tuple reuse.** A later accepted operation, including the same operation/candidate/seed/result-family tuple, has a fresh generation and a different token. An old token cannot clean, acknowledge, select a continuation for, or replay against the new operation. A missing receipt is not inferred from current target success or from the token alone.

Required fault checks explicitly include receipt deferred=null -> first uninstall request saved and fsynced, ACTIVE reconciliation I/O failure, then cleanup-failed with the exact receipt-owned after_cleanup_command (never run-request/null or NONE fallback). Required fault checks also cover before/after receipt publication and fsync, ACTIVE unlink and parent fsync, response loss, receipt-only replay with/without a deferred request, receipt-authoritative mirror lag, a late first desired request, new-operation invalidation crash, stale token against the same tuple's new generation, record/binding mismatch and foreign receipt preservation.

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
| `CLEANUP-WARNING` | `retry-cleanup,active.cleanup_retry_command,none,null` |
| `CLEANUP-FAILED-NONE` | `retry-cleanup,retry_command,none,null` |
| `CLEANUP-FAILED-DEFERRED` | `retry-cleanup,retry_command,run-request,render(continuation_owner.deferred_invocation)` |
| `CLEANUP-COMPLETED-NONE` | `none,null,none,null` |
| `CLEANUP-COMPLETED-DEFERRED` | `run-request,render(continuation_owner.deferred_invocation),none,null` |
| `CLEANUP-REPLAY-NONE` | `none,null,none,null` |
| `CLEANUP-REPLAY-DEFERRED` | `run-request,render(continuation_owner.deferred_invocation),none,null` |

`CLEANUP-FAILED-BY-ROLE-AND-DEFERRED` and `CLEANUP-COMPLETED-BY-ROLE-AND-DEFERRED` both select DEFERRED iff `continuation_owner.deferred_invocation` is non-null, otherwise NONE. A no-token desired invocation must first persist its first request as specified by WIR-CLEANUP-001/002. Failure after receipt persistence but before ACTIVE reconciliation still selects and renders the receipt's exact deferred request; a cached null ACTIVE value cannot select NONE or produce run-request/null. An invalid/mismatched receipt blocks before these cleanup profiles are used.

`render()` uses WIR-CLEANUP-001 exact invocation strings. Action `none` iff paired command is null. Lifecycle partial-failure rows use the un-tokenized lifecycle retry tokens. Every cleanup-warning and terminal-cleanup-failure row instead sets both `retry_command` and `continuation.next_command` to the exact token-bearing `active.cleanup_retry_command`; substituting an un-tokenized desired command is invalid. Cleanup success always has `retry_command=null`.

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
| `install-completed-with-cleanup-warning` | `create-if-absent install` | `completed_with_warnings` | `apply` | `true` | `install` | `request.candidate_digest` | `create-if-absent` | true | false | `complete` | `publish-terminal-record` | `active.cleanup_retry_command` | `install-create terminal + one stage warning` | 0 | `CLEANUP-WARNING` |
| `install-completed-with-cleanup-warning` | `preserve-only install/reinstall` | `completed_with_warnings` | `apply` | `true` | `install` | `request.candidate_digest` | `preserve-only` | true | false | `complete` | `publish-terminal-record` | `active.cleanup_retry_command` | `install-preserve terminal + one stage warning` | 0 | `CLEANUP-WARNING` |
| `update-completed` | `ready update` | `completed` | `apply` | `true` | `update` | `request.candidate_digest` | `preserve-only` | true | false | `complete` | `cleanup-stage` | `null` | `update terminal action set` | 0 | `NONE` |
| `update-completed-with-cleanup-warning` | `ready update` | `completed_with_warnings` | `apply` | `true` | `update` | `request.candidate_digest` | `preserve-only` | true | false | `complete` | `publish-terminal-record` | `active.cleanup_retry_command` | `update terminal + one stage warning` | 0 | `CLEANUP-WARNING` |
| `legacy-migration-completed` | `legacy migration` | `completed` | `apply` | `true` | `install` | `request.candidate_digest` | `preserve-only` | true | false | `complete` | `cleanup-stage` | `null` | `install-preserve terminal action set` | 0 | `NONE` |
| `legacy-migration-completed-with-cleanup-warning` | `legacy migration` | `completed_with_warnings` | `apply` | `true` | `install` | `request.candidate_digest` | `preserve-only` | true | false | `complete` | `publish-terminal-record` | `active.cleanup_retry_command` | `install-preserve terminal + one stage warning` | 0 | `CLEANUP-WARNING` |
| `uninstall-planned` | `ready dry-run` | `planned` | `dry-run` | `false` | `uninstall` | `record.candidate_digest` | `preserve-only` | false | false | `complete` | `preflight` | `null` | `AP-U-READY-PLAN` | 0 | `NONE` |
| `uninstall-planned` | `exact legacy dry-run` | `planned` | `dry-run` | `false` | `uninstall` | `legacy_fixture.aggregate_digest` | `preserve-only` | false | false | `complete` | `preflight` | `null` | `AP-U-LEGACY-PLAN` | 0 | `NONE` |
| `uninstall-planned` | `matching incomplete-uninstall dry-run` | `planned` | `dry-run` | `false` | `uninstall` | `record.candidate_digest` | `record.seed_policy=preserve-only` | false | false | `complete` | `preflight` | `null` | `AP-U-INCOMPLETE-PLAN` | 0 | `NONE` |
| `uninstall-already-absent` | `tooling-absent dry-run` | `planned` | `dry-run` | `false` | `uninstall` | `record.candidate_digest` | `preserve-only` | false | false | `complete` | `preflight` | `null` | `AP-U-ABSENT` | 0 | `NONE` |
| `uninstall-completed` | `ready apply` | `completed` | `apply` | `true` | `uninstall` | `record.candidate_digest` | `preserve-only` | true | false | `complete` | `cleanup-stage` | `null` | `AP-U-READY-TERM` | 0 | `NONE` |
| `uninstall-completed` | `exact legacy apply` | `completed` | `apply` | `true` | `uninstall` | `legacy_fixture.aggregate_digest` | `preserve-only` | true | false | `complete` | `cleanup-stage` | `null` | `AP-U-LEGACY-TERM` | 0 | `NONE` |
| `uninstall-completed` | `successful matching incomplete-uninstall resume apply` | `completed` | `apply` | `true` | `uninstall` | `record.candidate_digest` | `record.seed_policy=preserve-only` | true | false | `complete` | `cleanup-stage` | `null` | `AP-U-INCOMPLETE-TERM` | 0 | `NONE` |
| `uninstall-already-absent` | `tooling-absent apply` | `completed` | `apply` | `true` | `uninstall` | `record.candidate_digest` | `preserve-only` | false | false | `complete` | `preflight` | `null` | `AP-U-ABSENT` | 0 | `NONE` |
| `uninstall-completed-with-cleanup-warning` | `ready apply` | `completed_with_warnings` | `apply` | `true` | `uninstall` | `record.candidate_digest` | `preserve-only` | true | false | `complete` | `publish-terminal-record` | `active.cleanup_retry_command` | `AP-U-READY-WARN` | 0 | `CLEANUP-WARNING` |
| `uninstall-completed-with-cleanup-warning` | `exact legacy apply` | `completed_with_warnings` | `apply` | `true` | `uninstall` | `legacy_fixture.aggregate_digest` | `preserve-only` | true | false | `complete` | `publish-terminal-record` | `active.cleanup_retry_command` | `AP-U-LEGACY-WARN` | 0 | `CLEANUP-WARNING` |
| `uninstall-completed-with-cleanup-warning` | `matching incomplete-uninstall resume apply` | `completed_with_warnings` | `apply` | `true` | `uninstall` | `record.candidate_digest` | `record.seed_policy=preserve-only` | true | false | `complete` | `publish-terminal-record` | `active.cleanup_retry_command` | `AP-U-INCOMPLETE-WARN` | 0 | `CLEANUP-WARNING` |
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
| `repository-operation-busy` | `apply` | `blocked` | `apply` | `true` | `null` | `null` | `null` | false | false | `preflight` | `request-validation` | `null` | `empty` | 1 | `NONE` |
| `repository-operation-busy` | `dry-run` | `blocked` | `dry-run` | `false` | `null` | `null` | `null` | false | false | `preflight` | `request-validation` | `null` | `empty` | 1 | `NONE` |
| `repository-coordination-unavailable` | `apply` | `blocked` | `apply` | `true` | `null` | `null` | `null` | false | false | `preflight` | `request-validation` | `null` | `empty` | 1 | `NONE` |
| `repository-coordination-unavailable` | `dry-run` | `blocked` | `dry-run` | `false` | `null` | `null` | `null` | false | false | `preflight` | `request-validation` | `null` | `empty` | 1 | `NONE` |
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
| `terminal-cleanup-completed` | receipt-only token replay `init-force; specs_mode=null; deferred=present` | `completed` | `apply` | `true` | `receipt.operation` | `receipt.candidate_digest` | `receipt.seed_policy` | false | false | `complete` | `cleanup-stage` | `null` | `empty` | 0 | `CLEANUP-REPLAY-DEFERRED` |
| `terminal-cleanup-completed` | receipt-only token replay `init-force; specs_mode=null; deferred=null` | `completed` | `apply` | `true` | `receipt.operation` | `receipt.candidate_digest` | `receipt.seed_policy` | false | false | `complete` | `cleanup-stage` | `null` | `empty` | 0 | `CLEANUP-REPLAY-NONE` |
| `terminal-cleanup-completed` | receipt-only token replay `update; specs_mode=null; deferred=present` | `completed` | `apply` | `true` | `receipt.operation` | `receipt.candidate_digest` | `receipt.seed_policy` | false | false | `complete` | `cleanup-stage` | `null` | `empty` | 0 | `CLEANUP-REPLAY-DEFERRED` |
| `terminal-cleanup-completed` | receipt-only token replay `update; specs_mode=null; deferred=null` | `completed` | `apply` | `true` | `receipt.operation` | `receipt.candidate_digest` | `receipt.seed_policy` | false | false | `complete` | `cleanup-stage` | `null` | `empty` | 0 | `CLEANUP-REPLAY-NONE` |
| `terminal-cleanup-completed` | receipt-only token replay `uninstall-apply-keep; specs_mode=keep; deferred=present` | `completed` | `apply` | `true` | `receipt.operation` | `receipt.candidate_digest` | `receipt.seed_policy` | false | false | `complete` | `cleanup-stage` | `null` | `empty` | 0 | `CLEANUP-REPLAY-DEFERRED` |
| `terminal-cleanup-completed` | receipt-only token replay `uninstall-apply-keep; specs_mode=keep; deferred=null` | `completed` | `apply` | `true` | `receipt.operation` | `receipt.candidate_digest` | `receipt.seed_policy` | false | false | `complete` | `cleanup-stage` | `null` | `empty` | 0 | `CLEANUP-REPLAY-NONE` |

| `lifecycle-preparation-failed` | `initial authority I/O/apply` | `blocked` | `apply` | true | `null` | `null` | `null` | false | false | `preflight` | `request-validation` | `null` | `empty` | `1` | `NONE` |
| `stage-owner-mismatch` | `initial private authority/apply` | `blocked` | `apply` | true | `null` | `null` | `null` | false | false | `preflight` | `request-validation` | `null` | `empty` | `1` | `NONE` |
| `lifecycle-preparation-failed` | `initial authority I/O/dry-run` | `blocked` | `dry-run` | false | `null` | `null` | `null` | false | false | `preflight` | `request-validation` | `null` | `empty` | `1` | `NONE` |
| `stage-owner-mismatch` | `initial private authority/dry-run` | `blocked` | `dry-run` | false | `null` | `null` | `null` | false | false | `preflight` | `request-validation` | `null` | `empty` | `1` | `NONE` |
| `lifecycle-preparation-failed` | `install/create-if-absent/staging` | `blocked` | `apply` | true | `install` | `request.candidate_digest` | `create-if-absent` | false | false | `candidate-staging` | `preflight` | `install/create-if-absent retry` | `empty` | `1` | `LIFECYCLE-RETRY` |
| `lifecycle-preparation-failed` | `install/create-if-absent/initial-record/original-state` | `blocked` | `apply` | true | `install` | `request.candidate_digest` | `create-if-absent` | false | false | `publish-incomplete-record` | `bootstrap-container` | `install/create-if-absent retry` | `empty` | `1` | `LIFECYCLE-RETRY` |
| `lifecycle-preparation-failed` | `install/create-if-absent/initial-record/consumer-mutated` | `partial_failure` | `apply` | true | `install` | `request.candidate_digest` | `create-if-absent` | true | false | `publish-incomplete-record` | `bootstrap-container` | `install/create-if-absent retry` | `AP-PREP-PARTIAL` | `1` | `LIFECYCLE-RETRY` |
| `lifecycle-preparation-failed` | `install/preserve-only/staging` | `blocked` | `apply` | true | `install` | `request.candidate_digest` | `preserve-only` | false | false | `candidate-staging` | `preflight` | `install/preserve-only retry` | `empty` | `1` | `LIFECYCLE-RETRY` |
| `lifecycle-preparation-failed` | `install/preserve-only/initial-record/original-state` | `blocked` | `apply` | true | `install` | `request.candidate_digest` | `preserve-only` | false | false | `publish-incomplete-record` | `bootstrap-container` | `install/preserve-only retry` | `empty` | `1` | `LIFECYCLE-RETRY` |
| `lifecycle-preparation-failed` | `install/preserve-only/initial-record/consumer-mutated` | `partial_failure` | `apply` | true | `install` | `request.candidate_digest` | `preserve-only` | true | false | `publish-incomplete-record` | `bootstrap-container` | `install/preserve-only retry` | `AP-PREP-PARTIAL` | `1` | `LIFECYCLE-RETRY` |
| `lifecycle-preparation-failed` | `update/preserve-only/staging` | `blocked` | `apply` | true | `update` | `request.candidate_digest` | `preserve-only` | false | false | `candidate-staging` | `preflight` | `update retry` | `empty` | `1` | `LIFECYCLE-RETRY` |
| `lifecycle-preparation-failed` | `update/preserve-only/initial-record/original-state` | `blocked` | `apply` | true | `update` | `request.candidate_digest` | `preserve-only` | false | false | `publish-incomplete-record` | `candidate-staging` | `update retry` | `empty` | `1` | `LIFECYCLE-RETRY` |
| `lifecycle-preparation-failed` | `update/preserve-only/initial-record/consumer-mutated` | `partial_failure` | `apply` | true | `update` | `request.candidate_digest` | `preserve-only` | true | false | `publish-incomplete-record` | `candidate-staging` | `update retry` | `AP-PREP-PARTIAL` | `1` | `LIFECYCLE-RETRY` |
| `lifecycle-preparation-failed` | `uninstall/preserve-only/staging` | `blocked` | `apply` | true | `uninstall` | `owned_target_digest` | `preserve-only` | false | false | `candidate-staging` | `preflight` | `uninstall retry` | `empty` | `1` | `LIFECYCLE-RETRY` |
| `lifecycle-preparation-failed` | `uninstall/preserve-only/initial-record/original-state` | `blocked` | `apply` | true | `uninstall` | `owned_target_digest` | `preserve-only` | false | false | `publish-incomplete-record` | `candidate-staging` | `uninstall retry` | `empty` | `1` | `LIFECYCLE-RETRY` |
| `lifecycle-preparation-failed` | `uninstall/preserve-only/initial-record/consumer-mutated` | `partial_failure` | `apply` | true | `uninstall` | `owned_target_digest` | `preserve-only` | true | false | `publish-incomplete-record` | `candidate-staging` | `uninstall retry` | `AP-PREP-PARTIAL` | `1` | `LIFECYCLE-RETRY` |

No other code/variant/relation is valid.
## 11. Retry, continuation, messages and guidance

### WIR-TEXT-001 — Retry and invocation commands

| Token | Exact value |
|---|---|
| install/create-if-absent retry | `spec-dock init --force -- ${QUOTED_TARGET}` |
| install/preserve-only retry | `spec-dock update -- ${QUOTED_TARGET}` |
| update retry | `spec-dock update -- ${QUOTED_TARGET}` |
| uninstall retry | `spec-dock uninstall --apply --keep-specs -- ${QUOTED_TARGET}` |
| active.cleanup_retry_command | Exact tokenized command selected by ACTIVE: `install/create-if-absent -> init-force token form`; `install/preserve-only|legacy-migration|update -> update token form`; `uninstall -> uninstall-apply-keep token form`. Insert exact `--provider-cleanup-token ${ACTIVE_CLEANUP_TOKEN}` before `--` and preserve WIR-CLEANUP-001 flag order. |
| render(`init`) | `spec-dock init -- ${QUOTED_TARGET}` |
| render(`init-force`) | `spec-dock init --force -- ${QUOTED_TARGET}` |
| render(`update`) | `spec-dock update -- ${QUOTED_TARGET}` |
| render(`uninstall-dry-run`) | `spec-dock uninstall -- ${QUOTED_TARGET}` |
| render(`uninstall-dry-run-keep`) | `spec-dock uninstall --keep-specs -- ${QUOTED_TARGET}` |
| render(`uninstall-apply`) | `spec-dock uninstall --apply -- ${QUOTED_TARGET}` |
| render(`uninstall-apply-keep`) | `spec-dock uninstall --apply --keep-specs -- ${QUOTED_TARGET}` |
| null | JSON null |

`${QUOTED_TARGET}` is `shlex.join([normalized_target])`; `${ACTIVE_CLEANUP_TOKEN}` is exact `active.cleanup_token`. Callers act only on `continuation`; `retry_command` is a compatibility echo. Cleanup warning and cleanup failure both expose the exact tokenized cleanup retry, never an un-tokenized lifecycle command. Cleanup failure independently conveys optional desired-after-cleanup command.

### WIR-TEXT-002 — Exact diagnostics

Cleanup warning: `Provider tooling reached the requested terminal state, but the owned external stage could not be removed.`

| Code | Exact error string |
|---|---|
| `lifecycle-preparation-failed` | `Lifecycle preparation could not be completed; preserve the current state and follow the continuation object exactly.` |
| `already-initialized` | `SpecDock tooling is already installed; use init --force or update.` |
| `tooling-not-installed` | `SpecDock tooling is not installed for this target.` |
| `installation-record-invalid` | `The SpecDock installation record is invalid.` |
| `installation-record-state-inconsistent` | `The SpecDock installation record does not match the observed tooling state.` |
| `resume-operation-mismatch` | `The incomplete operation can be resumed only with the same operation.` |
| `resume-candidate-mismatch` | `The incomplete operation can be resumed only with the same candidate digest.` |
| `resume-seed-policy-mismatch` | `The incomplete operation can be resumed only with the same seed policy.` |
| `candidate-invalid` | `The packaged provider candidate is invalid.` |
| `candidate-digest-mismatch` | `The staged provider candidate digest does not match the packaged candidate.` |
| `repository-operation-busy` | `Another SpecDock command holds repository coordination; retry after it exits.` |
| `repository-coordination-unavailable` | `Required repository coordination is unavailable; no operation was executed.` |
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
- Lifecycle partial (`install-partial-failure`, `update-partial-failure`, `uninstall-partial-failure` only): `Run continuation.next_command to resume the exact lifecycle operation.` then `Do not switch operation, candidate package, or seed policy.`
- `lifecycle-preparation-failed`: empty array in every region/status; its continuation alone owns the next action.
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
- `AP-U-INCOMPLETE-PLAN`: container and seeds are preserved; record is planned with `terminal-record-publish`; each already-absent owned root/slot is preserved with `owned-root-absent`/`owned-slot-absent`; each still-present owned root/slot is planned for removal. Zero through six owned roots/slots may already be absent. The descriptor-bound valid incomplete-uninstall record and matching ACTIVE identity determine the state, not the number of missing targets. A crash immediately after `publish-incomplete-record`, or failure before the first detach, legitimately leaves all six targets present; it uses this profile and may resume normally.
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


### WIR-ACT-006 — Initial-record failure actions

`AP-PREP-PARTIAL` has exactly one failed row: `spec-dock/spec-dock.version,record,failed,incomplete-record-publish`. Include the shared container as completed/fresh-container-create only if this generation created it, otherwise preserved/shared-container-preserve. No provider root/slot has been published or detached at this boundary.

For install/update, each of the six fixed targets is pending, using candidate-root-create/candidate-slot-create when absent in the accepted original observation, otherwise candidate-root-replace/candidate-slot-replace. For uninstall, each original present fixed target is pending/owned-root-remove or owned-slot-remove; each absent target is preserved/owned-root-absent or owned-slot-absent. Preserve-only seeds are preserved/preserve-only-seed. Create-if-absent seeds are preserved/consumer-seed-present when already present, otherwise pending/fresh-seed-create; include absent required .github/.github/workflows parents as pending/container/fresh-container-create, and omit their rows when already present. End with pending `@provider-stage,stage,pending,candidate-stage-cleanup`. Do not expose temporary paths or add consumer-data rows. Use TARGET_PATH_ORDER and derived summary/failed/pending exactly. P0/P1/P2a remain empty-action blocked results regardless of private writes.

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
{"schema_version":1,"target":"/tmp/consumer","mode":"apply","apply":true,"specs_mode":"keep","status":"completed","code":"uninstall-completed","operation":"uninstall","candidate_digest":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","seed_policy":"preserve-only","mutation_started":true,"bootstrap_rolled_back":false,"phase":"complete","last_completed_phase":"cleanup-stage","retry_command":null,"continuation":{"next_action":"none","next_command":null,"after_cleanup_action":"none","after_cleanup_command":null},"failed_paths":[],"pending_paths":[],"summary":{"planned":0,"completed":8,"preserved":3,"pending":0,"failed":0,"warnings":0},"actions":[{"path":"spec-dock","category":"container","status":"preserved","reason":"shared-container-preserve"},{"path":"spec-dock/spec-dock.version","category":"record","status":"completed","reason":"terminal-record-publish"},{"path":"spec-dock/docs","category":"root","status":"completed","reason":"owned-root-remove"},{"path":"spec-dock/templates","category":"root","status":"completed","reason":"owned-root-remove"},{"path":"spec-dock/system","category":"root","status":"completed","reason":"owned-root-remove"},{"path":"spec-dock/scripts","category":"root","status":"completed","reason":"owned-root-remove"},{"path":".agents/skills/spec-dock","category":"slot","status":"completed","reason":"owned-slot-remove"},{"path":".agents/skills/spec-dock-grill-with-docs","category":"slot","status":"completed","reason":"owned-slot-remove"},{"path":"spec-dock/.gitignore","category":"seed","status":"preserved","reason":"preserve-only-seed"},{"path":".github/workflows/ci.yml","category":"seed","status":"preserved","reason":"preserve-only-seed"},{"path":"@provider-stage","category":"stage","status":"completed","reason":"candidate-stage-cleanup"}],"guidance":[],"warnings":[],"errors":[]}
```

### WIR-GOLDEN-U6 — Exact legacy uninstall apply

```json
{"schema_version":1,"target":"/tmp/consumer","mode":"apply","apply":true,"specs_mode":null,"status":"completed","code":"uninstall-completed","operation":"uninstall","candidate_digest":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","seed_policy":"preserve-only","mutation_started":true,"bootstrap_rolled_back":false,"phase":"complete","last_completed_phase":"cleanup-stage","retry_command":null,"continuation":{"next_action":"none","next_command":null,"after_cleanup_action":"none","after_cleanup_command":null},"failed_paths":[],"pending_paths":[],"summary":{"planned":0,"completed":8,"preserved":3,"pending":0,"failed":0,"warnings":0},"actions":[{"path":"spec-dock","category":"container","status":"preserved","reason":"shared-container-preserve"},{"path":"spec-dock/spec-dock.version","category":"record","status":"completed","reason":"terminal-record-publish"},{"path":"spec-dock/docs","category":"root","status":"completed","reason":"owned-root-remove"},{"path":"spec-dock/templates","category":"root","status":"completed","reason":"owned-root-remove"},{"path":"spec-dock/system","category":"root","status":"completed","reason":"owned-root-remove"},{"path":"spec-dock/scripts","category":"root","status":"completed","reason":"owned-root-remove"},{"path":".agents/skills/spec-dock","category":"slot","status":"completed","reason":"owned-slot-remove"},{"path":".agents/skills/spec-dock-grill-with-docs","category":"slot","status":"completed","reason":"owned-slot-remove"},{"path":"spec-dock/.gitignore","category":"seed","status":"preserved","reason":"preserve-only-seed"},{"path":".github/workflows/ci.yml","category":"seed","status":"preserved","reason":"preserve-only-seed"},{"path":"@provider-stage","category":"stage","status":"completed","reason":"candidate-stage-cleanup"}],"guidance":[],"warnings":[],"errors":[]}
```

### WIR-GOLDEN-U7 — Successful matching incomplete-uninstall resume

```json
{"schema_version":1,"target":"/tmp/consumer","mode":"apply","apply":true,"specs_mode":"keep","status":"completed","code":"uninstall-completed","operation":"uninstall","candidate_digest":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","seed_policy":"preserve-only","mutation_started":true,"bootstrap_rolled_back":false,"phase":"complete","last_completed_phase":"cleanup-stage","retry_command":null,"continuation":{"next_action":"none","next_command":null,"after_cleanup_action":"none","after_cleanup_command":null},"failed_paths":[],"pending_paths":[],"summary":{"planned":0,"completed":7,"preserved":4,"pending":0,"failed":0,"warnings":0},"actions":[{"path":"spec-dock","category":"container","status":"preserved","reason":"shared-container-preserve"},{"path":"spec-dock/spec-dock.version","category":"record","status":"completed","reason":"terminal-record-publish"},{"path":"spec-dock/docs","category":"root","status":"preserved","reason":"owned-root-absent"},{"path":"spec-dock/templates","category":"root","status":"completed","reason":"owned-root-remove"},{"path":"spec-dock/system","category":"root","status":"completed","reason":"owned-root-remove"},{"path":"spec-dock/scripts","category":"root","status":"completed","reason":"owned-root-remove"},{"path":".agents/skills/spec-dock","category":"slot","status":"completed","reason":"owned-slot-remove"},{"path":".agents/skills/spec-dock-grill-with-docs","category":"slot","status":"completed","reason":"owned-slot-remove"},{"path":"spec-dock/.gitignore","category":"seed","status":"preserved","reason":"preserve-only-seed"},{"path":".github/workflows/ci.yml","category":"seed","status":"preserved","reason":"preserve-only-seed"},{"path":"@provider-stage","category":"stage","status":"completed","reason":"candidate-stage-cleanup"}],"guidance":[],"warnings":[],"errors":[]}
```

### WIR-GOLDEN-U8 — Tooling-absent apply

```json
{"schema_version":1,"target":"/tmp/consumer","mode":"apply","apply":true,"specs_mode":null,"status":"completed","code":"uninstall-already-absent","operation":"uninstall","candidate_digest":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","seed_policy":"preserve-only","mutation_started":false,"bootstrap_rolled_back":false,"phase":"complete","last_completed_phase":"preflight","retry_command":null,"continuation":{"next_action":"none","next_command":null,"after_cleanup_action":"none","after_cleanup_command":null},"failed_paths":[],"pending_paths":[],"summary":{"planned":0,"completed":0,"preserved":4,"pending":0,"failed":0,"warnings":0},"actions":[{"path":"spec-dock","category":"container","status":"preserved","reason":"shared-container-preserve"},{"path":"spec-dock/spec-dock.version","category":"record","status":"preserved","reason":"terminal-record-current"},{"path":"spec-dock/.gitignore","category":"seed","status":"preserved","reason":"preserve-only-seed"},{"path":".github/workflows/ci.yml","category":"seed","status":"preserved","reason":"preserve-only-seed"}],"guidance":[],"warnings":[],"errors":[]}
```

### WIR-GOLDEN-U9 — Partial uninstall at templates

```json
{"schema_version":1,"target":"/tmp/consumer","mode":"apply","apply":true,"specs_mode":"keep","status":"partial_failure","code":"uninstall-partial-failure","operation":"uninstall","candidate_digest":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","seed_policy":"preserve-only","mutation_started":true,"bootstrap_rolled_back":false,"phase":"detach-templates","last_completed_phase":"detach-docs","retry_command":"spec-dock uninstall --apply --keep-specs -- /tmp/consumer","continuation":{"next_action":"run-request","next_command":"spec-dock uninstall --apply --keep-specs -- /tmp/consumer","after_cleanup_action":"none","after_cleanup_command":null},"failed_paths":["spec-dock/templates"],"pending_paths":["spec-dock/system","spec-dock/scripts",".agents/skills/spec-dock",".agents/skills/spec-dock-grill-with-docs","@provider-stage"],"summary":{"planned":0,"completed":2,"preserved":3,"pending":5,"failed":1,"warnings":0},"actions":[{"path":"spec-dock","category":"container","status":"preserved","reason":"shared-container-preserve"},{"path":"spec-dock/spec-dock.version","category":"record","status":"completed","reason":"incomplete-record-publish"},{"path":"spec-dock/docs","category":"root","status":"completed","reason":"owned-root-remove"},{"path":"spec-dock/templates","category":"root","status":"failed","reason":"owned-root-remove"},{"path":"spec-dock/system","category":"root","status":"pending","reason":"owned-root-remove"},{"path":"spec-dock/scripts","category":"root","status":"pending","reason":"owned-root-remove"},{"path":".agents/skills/spec-dock","category":"slot","status":"pending","reason":"owned-slot-remove"},{"path":".agents/skills/spec-dock-grill-with-docs","category":"slot","status":"pending","reason":"owned-slot-remove"},{"path":"spec-dock/.gitignore","category":"seed","status":"preserved","reason":"preserve-only-seed"},{"path":".github/workflows/ci.yml","category":"seed","status":"preserved","reason":"preserve-only-seed"},{"path":"@provider-stage","category":"stage","status":"pending","reason":"candidate-stage-cleanup"}],"guidance":["Run continuation.next_command to resume the exact lifecycle operation.","Do not switch operation, candidate package, or seed policy."],"warnings":[],"errors":["SpecDock uninstall stopped after durable mutation; rerun the exact retry command."]}
```

### WIR-GOLDEN-U10 — Removed purge trap

```json
{"schema_version":1,"target":"/tmp/consumer","mode":"apply","apply":true,"specs_mode":"remove","status":"error","code":"spec-history-purge-removed","operation":null,"candidate_digest":null,"seed_policy":null,"mutation_started":false,"bootstrap_rolled_back":false,"phase":"request-validation","last_completed_phase":"not-started","retry_command":null,"continuation":{"next_action":"none","next_command":null,"after_cleanup_action":"none","after_cleanup_command":null},"failed_paths":[],"pending_paths":[],"summary":{"planned":0,"completed":0,"preserved":0,"pending":0,"failed":0,"warnings":0},"actions":[],"guidance":["Use tooling-only uninstall without --remove-specs.","Spec history and Workbench data remain consumer-owned."],"warnings":[],"errors":["Spec history purge has been removed; uninstall is tooling-only."]}
```

### WIR-GOLDEN-I1 — Partial preserve-only install at system

```json
{"schema_version":1,"target":"/tmp/consumer","mode":"apply","apply":true,"specs_mode":null,"status":"partial_failure","code":"install-partial-failure","operation":"install","candidate_digest":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","seed_policy":"preserve-only","mutation_started":true,"bootstrap_rolled_back":false,"phase":"publish-system","last_completed_phase":"publish-templates","retry_command":"spec-dock update -- /tmp/consumer","continuation":{"next_action":"run-request","next_command":"spec-dock update -- /tmp/consumer","after_cleanup_action":"none","after_cleanup_command":null},"failed_paths":["spec-dock/system"],"pending_paths":["spec-dock/scripts",".agents/skills/spec-dock",".agents/skills/spec-dock-grill-with-docs","@provider-stage"],"summary":{"planned":0,"completed":3,"preserved":3,"pending":4,"failed":1,"warnings":0},"actions":[{"path":"spec-dock","category":"container","status":"preserved","reason":"shared-container-preserve"},{"path":"spec-dock/spec-dock.version","category":"record","status":"completed","reason":"incomplete-record-publish"},{"path":"spec-dock/docs","category":"root","status":"completed","reason":"candidate-root-replace"},{"path":"spec-dock/templates","category":"root","status":"completed","reason":"candidate-root-replace"},{"path":"spec-dock/system","category":"root","status":"failed","reason":"candidate-root-replace"},{"path":"spec-dock/scripts","category":"root","status":"pending","reason":"candidate-root-replace"},{"path":".agents/skills/spec-dock","category":"slot","status":"pending","reason":"candidate-slot-replace"},{"path":".agents/skills/spec-dock-grill-with-docs","category":"slot","status":"pending","reason":"candidate-slot-replace"},{"path":"spec-dock/.gitignore","category":"seed","status":"preserved","reason":"preserve-only-seed"},{"path":".github/workflows/ci.yml","category":"seed","status":"preserved","reason":"preserve-only-seed"},{"path":"@provider-stage","category":"stage","status":"pending","reason":"candidate-stage-cleanup"}],"guidance":["Run continuation.next_command to resume the exact lifecycle operation.","Do not switch operation, candidate package, or seed policy."],"warnings":[],"errors":["SpecDock install stopped after durable mutation; rerun the exact retry command."]}
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

### WIR-GOLDEN-CS1 — Tokenized retry completes cleanup and returns desired init command

```json
{"schema_version":1,"target":"/tmp/consumer","mode":"apply","apply":true,"specs_mode":null,"status":"completed","code":"terminal-cleanup-completed","operation":"install","candidate_digest":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","seed_policy":"create-if-absent","mutation_started":true,"bootstrap_rolled_back":false,"phase":"complete","last_completed_phase":"cleanup-stage","retry_command":null,"continuation":{"next_action":"run-request","next_command":"spec-dock init -- /tmp/consumer","after_cleanup_action":"none","after_cleanup_command":null},"failed_paths":[],"pending_paths":[],"summary":{"planned":0,"completed":1,"preserved":0,"pending":0,"failed":0,"warnings":0},"actions":[{"path":"@provider-stage","category":"stage","status":"completed","reason":"candidate-stage-cleanup"}],"guidance":["Owned provider stage cleanup completed; no lifecycle operation was executed.","Run continuation.next_command to execute the preserved requested operation."],"warnings":[],"errors":[]}
```

### WIR-GOLDEN-CF2 — Desired init --force encounters cleanup failure

```json
{"schema_version":1,"target":"/tmp/consumer","mode":"apply","apply":true,"specs_mode":null,"status":"partial_failure","code":"terminal-cleanup-failed","operation":"install","candidate_digest":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","seed_policy":"create-if-absent","mutation_started":true,"bootstrap_rolled_back":false,"phase":"cleanup-stage","last_completed_phase":"publish-terminal-record","retry_command":"spec-dock init --force --provider-cleanup-token eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee -- /tmp/consumer","continuation":{"next_action":"retry-cleanup","next_command":"spec-dock init --force --provider-cleanup-token eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee -- /tmp/consumer","after_cleanup_action":"run-request","after_cleanup_command":"spec-dock init --force -- /tmp/consumer"},"failed_paths":["@provider-stage"],"pending_paths":[],"summary":{"planned":0,"completed":0,"preserved":0,"pending":0,"failed":1,"warnings":0},"actions":[{"path":"@provider-stage","category":"stage","status":"failed","reason":"candidate-stage-cleanup"}],"guidance":["Run continuation.next_command to retry owned stage cleanup.","After cleanup succeeds, run continuation.after_cleanup_command.","The requested terminal tooling state is already durable."],"warnings":[],"errors":["The requested tooling state is durable, but owned stage cleanup failed; follow the continuation object exactly."]}
```

### WIR-GOLDEN-CS2 — Tokenized retry completes cleanup and returns desired init --force command

```json
{"schema_version":1,"target":"/tmp/consumer","mode":"apply","apply":true,"specs_mode":null,"status":"completed","code":"terminal-cleanup-completed","operation":"install","candidate_digest":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","seed_policy":"create-if-absent","mutation_started":true,"bootstrap_rolled_back":false,"phase":"complete","last_completed_phase":"cleanup-stage","retry_command":null,"continuation":{"next_action":"run-request","next_command":"spec-dock init --force -- /tmp/consumer","after_cleanup_action":"none","after_cleanup_command":null},"failed_paths":[],"pending_paths":[],"summary":{"planned":0,"completed":1,"preserved":0,"pending":0,"failed":0,"warnings":0},"actions":[{"path":"@provider-stage","category":"stage","status":"completed","reason":"candidate-stage-cleanup"}],"guidance":["Owned provider stage cleanup completed; no lifecycle operation was executed.","Run continuation.next_command to execute the preserved requested operation."],"warnings":[],"errors":[]}
```

### WIR-GOLDEN-CF3 — Desired update encounters cleanup failure

```json
{"schema_version":1,"target":"/tmp/consumer","mode":"apply","apply":true,"specs_mode":null,"status":"partial_failure","code":"terminal-cleanup-failed","operation":"update","candidate_digest":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","seed_policy":"preserve-only","mutation_started":true,"bootstrap_rolled_back":false,"phase":"cleanup-stage","last_completed_phase":"publish-terminal-record","retry_command":"spec-dock update --provider-cleanup-token eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee -- /tmp/consumer","continuation":{"next_action":"retry-cleanup","next_command":"spec-dock update --provider-cleanup-token eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee -- /tmp/consumer","after_cleanup_action":"run-request","after_cleanup_command":"spec-dock update -- /tmp/consumer"},"failed_paths":["@provider-stage"],"pending_paths":[],"summary":{"planned":0,"completed":0,"preserved":0,"pending":0,"failed":1,"warnings":0},"actions":[{"path":"@provider-stage","category":"stage","status":"failed","reason":"candidate-stage-cleanup"}],"guidance":["Run continuation.next_command to retry owned stage cleanup.","After cleanup succeeds, run continuation.after_cleanup_command.","The requested terminal tooling state is already durable."],"warnings":[],"errors":["The requested tooling state is durable, but owned stage cleanup failed; follow the continuation object exactly."]}
```

### WIR-GOLDEN-CS3 — Tokenized retry completes cleanup and returns desired update command

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

### WIR-JSON-034 — Busy apply before target observation

```json
{"schema_version":1,"target":"/tmp/consumer","mode":"apply","apply":true,"specs_mode":null,"status":"blocked","code":"repository-operation-busy","operation":null,"candidate_digest":null,"seed_policy":null,"mutation_started":false,"bootstrap_rolled_back":false,"phase":"preflight","last_completed_phase":"request-validation","retry_command":null,"continuation":{"next_action":"none","next_command":null,"after_cleanup_action":"none","after_cleanup_command":null},"failed_paths":[],"pending_paths":[],"summary":{"planned":0,"completed":0,"preserved":0,"pending":0,"failed":0,"warnings":0},"actions":[],"guidance":[],"warnings":[],"errors":["Another SpecDock command holds repository coordination; retry after it exits."]}
```

### WIR-JSON-035 — Coordination unavailable for dry-run

```json
{"schema_version":1,"target":"/tmp/consumer","mode":"dry-run","apply":false,"specs_mode":null,"status":"blocked","code":"repository-coordination-unavailable","operation":null,"candidate_digest":null,"seed_policy":null,"mutation_started":false,"bootstrap_rolled_back":false,"phase":"preflight","last_completed_phase":"request-validation","retry_command":null,"continuation":{"next_action":"none","next_command":null,"after_cleanup_action":"none","after_cleanup_command":null},"failed_paths":[],"pending_paths":[],"summary":{"planned":0,"completed":0,"preserved":0,"pending":0,"failed":0,"warnings":0},"actions":[],"guidance":[],"warnings":[],"errors":["Required repository coordination is unavailable; no operation was executed."]}
```

### WIR-GOLDEN-P1 — Initial authority I/O (apply)

```json
{"schema_version":1,"target":"/tmp/consumer","mode":"apply","apply":true,"specs_mode":null,"status":"blocked","code":"lifecycle-preparation-failed","operation":null,"candidate_digest":null,"seed_policy":null,"mutation_started":false,"bootstrap_rolled_back":false,"phase":"preflight","last_completed_phase":"request-validation","retry_command":null,"continuation":{"next_action":"none","next_command":null,"after_cleanup_action":"none","after_cleanup_command":null},"failed_paths":[],"pending_paths":[],"summary":{"planned":0,"completed":0,"preserved":0,"pending":0,"failed":0,"warnings":0},"actions":[],"guidance":[],"warnings":[],"errors":["Lifecycle preparation could not be completed; preserve the current state and follow the continuation object exactly."]}
```

### WIR-GOLDEN-P2 — Update staging I/O

```json
{"schema_version":1,"target":"/tmp/consumer","mode":"apply","apply":true,"specs_mode":null,"status":"blocked","code":"lifecycle-preparation-failed","operation":"update","candidate_digest":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","seed_policy":"preserve-only","mutation_started":false,"bootstrap_rolled_back":false,"phase":"candidate-staging","last_completed_phase":"preflight","retry_command":"spec-dock update -- /tmp/consumer","continuation":{"next_action":"run-request","next_command":"spec-dock update -- /tmp/consumer","after_cleanup_action":"none","after_cleanup_command":null},"failed_paths":[],"pending_paths":[],"summary":{"planned":0,"completed":0,"preserved":0,"pending":0,"failed":0,"warnings":0},"actions":[],"guidance":[],"warnings":[],"errors":["Lifecycle preparation could not be completed; preserve the current state and follow the continuation object exactly."]}
```

### WIR-GOLDEN-P3 — Update initial-record failure without Consumer mutation

```json
{"schema_version":1,"target":"/tmp/consumer","mode":"apply","apply":true,"specs_mode":null,"status":"blocked","code":"lifecycle-preparation-failed","operation":"update","candidate_digest":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","seed_policy":"preserve-only","mutation_started":false,"bootstrap_rolled_back":false,"phase":"publish-incomplete-record","last_completed_phase":"candidate-staging","retry_command":"spec-dock update -- /tmp/consumer","continuation":{"next_action":"run-request","next_command":"spec-dock update -- /tmp/consumer","after_cleanup_action":"none","after_cleanup_command":null},"failed_paths":[],"pending_paths":[],"summary":{"planned":0,"completed":0,"preserved":0,"pending":0,"failed":0,"warnings":0},"actions":[],"guidance":[],"warnings":[],"errors":["Lifecycle preparation could not be completed; preserve the current state and follow the continuation object exactly."]}
```

### WIR-GOLDEN-P4 — Update initial-record failure after own record publication

```json
{"schema_version":1,"target":"/tmp/consumer","mode":"apply","apply":true,"specs_mode":null,"status":"partial_failure","code":"lifecycle-preparation-failed","operation":"update","candidate_digest":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd","seed_policy":"preserve-only","mutation_started":true,"bootstrap_rolled_back":false,"phase":"publish-incomplete-record","last_completed_phase":"candidate-staging","retry_command":"spec-dock update -- /tmp/consumer","continuation":{"next_action":"run-request","next_command":"spec-dock update -- /tmp/consumer","after_cleanup_action":"none","after_cleanup_command":null},"failed_paths":["spec-dock/spec-dock.version"],"pending_paths":["spec-dock/docs","spec-dock/templates","spec-dock/system","spec-dock/scripts",".agents/skills/spec-dock",".agents/skills/spec-dock-grill-with-docs","@provider-stage"],"summary":{"planned":0,"completed":0,"preserved":3,"pending":7,"failed":1,"warnings":0},"actions":[{"path":"spec-dock","category":"container","status":"preserved","reason":"shared-container-preserve"},{"path":"spec-dock/spec-dock.version","category":"record","status":"failed","reason":"incomplete-record-publish"},{"path":"spec-dock/docs","category":"root","status":"pending","reason":"candidate-root-replace"},{"path":"spec-dock/templates","category":"root","status":"pending","reason":"candidate-root-replace"},{"path":"spec-dock/system","category":"root","status":"pending","reason":"candidate-root-replace"},{"path":"spec-dock/scripts","category":"root","status":"pending","reason":"candidate-root-replace"},{"path":".agents/skills/spec-dock","category":"slot","status":"pending","reason":"candidate-slot-replace"},{"path":".agents/skills/spec-dock-grill-with-docs","category":"slot","status":"pending","reason":"candidate-slot-replace"},{"path":"spec-dock/.gitignore","category":"seed","status":"preserved","reason":"preserve-only-seed"},{"path":".github/workflows/ci.yml","category":"seed","status":"preserved","reason":"preserve-only-seed"},{"path":"@provider-stage","category":"stage","status":"pending","reason":"candidate-stage-cleanup"}],"guidance":[],"warnings":[],"errors":["Lifecycle preparation could not be completed; preserve the current state and follow the continuation object exactly."]}
```

### WIR-GOLDEN-P5 — Initial authority I/O (explicit keep dry-run)

```json
{"schema_version":1,"target":"/tmp/consumer","mode":"dry-run","apply":false,"specs_mode":"keep","status":"blocked","code":"lifecycle-preparation-failed","operation":null,"candidate_digest":null,"seed_policy":null,"mutation_started":false,"bootstrap_rolled_back":false,"phase":"preflight","last_completed_phase":"request-validation","retry_command":null,"continuation":{"next_action":"none","next_command":null,"after_cleanup_action":"none","after_cleanup_command":null},"failed_paths":[],"pending_paths":[],"summary":{"planned":0,"completed":0,"preserved":0,"pending":0,"failed":0,"warnings":0},"actions":[],"guidance":[],"warnings":[],"errors":["Lifecycle preparation could not be completed; preserve the current state and follow the continuation object exactly."]}
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

For init/update coordination admission failures (`repository-operation-busy`, `repository-coordination-unavailable`, or pre-observation `unsafe-repository-binding`), stdout is empty; stderr is exactly `error: ${code}: ${WIR-TEXT-002 error}\n`, with one terminal LF and exit 1. There is no retry/next line because continuation is NONE.

Init/update `lifecycle-preparation-failed` writes no stdout and exactly `error: lifecycle-preparation-failed: Lifecycle preparation could not be completed; preserve the current state and follow the continuation object exactly.\nnext: ${NEXT_COMMAND_OR_NONE}\n` to stderr, exit 1. The command is taken from continuation; null renders `none`. Guidance is empty for this code, including its partial rows; do not apply the older lifecycle-partial guidance to it. Uninstall uses its ordinary ordered text/JSON renderer for the same code and result.

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

Required tests additionally cover every WIR-CLEANUP-002 fault boundary and all six receipt-only replay rows, including zero mutation and correct continuation. Required tests include desired uninstall during old install cleanup; cleanup failure -> tokenized retry -> deferred uninstall; no-token desired update/init-force distinct from the tokenized base form; cleanup retry with no deferred request; a third explicit command preserving the first deferred request; crash after ACTIVE update/unlink; and table-driven continuation rendering for all seven invocation IDs.

Table-driven tests enumerate all 168 §10 rows and all 41 codes and reject every unlisted relation; all seven actual invocation echoes for both terminal-cleanup success and failure; cleanup-only return/no-dispatch; all sequences/partial and mandatory-cleanup pairs; action relations; target ordering and exact failed/pending equality; all 4 durable record goldens, all 40 public JSON review goldens, and exact text goldens; duplicate/unknown values; CLI/service parity; exact terminal-cleanup crash/retry cases and the complete Issue #392 lifecycle/dogfood acceptance state.

Normative trace: Epic E384-RQ-004–006,008–009,019; Issue I392-RQ-002–009; cross-Issue ownership WIR-OWN-001. Required concurrency/admission proof is additionally fixed in WIR-COORD-006 below. Issues #395 and #396 consume this artifact read-only. Owner decisions required: none.

## 16. Runtime/lifecycle coordination

### WIR-COORD-001 — One repository identity, shared/exclusive admission

The coordination object is the **repository root directory inode itself**, not `system/.runtime/create.lock`, a file under any disposable root, or a new persistent namespace. Open it read-only with `O_DIRECTORY|O_NOFOLLOW` and close-on-exec by default. Bind `(st_dev,st_ino)` to the visible non-symlink directory before and after lock acquisition; keep that descriptor and the binding checks through the operation. A symlink, substitution, missing/changed root or unsafe binding fails as `unsafe-repository-binding`.

| Participant | Acquisition | Lifetime |
|---|---|---|
| Supported repo-local runtime entrypoint | `flock(LOCK_SH|LOCK_NB)` | Before importing replaceable runtime modules or reading provider payload; through observation, command output and completion of managed writes/helpers. |
| External installer: init/init-force/update/uninstall | `flock(LOCK_EX|LOCK_NB)` | After parser normalization but before target classification, record/ACTIVE/receipt observation, staging, cleanup or mutation; through all writes and output. Dry-run and receipt-only replay use the same exclusive admission. |

Only the already-defined parser errors and removed-purge trap precede coordination. On contention return immediately: no waiting queue, automatic retry, lock upgrade, stale-lock removal or second lock identity. Recheck root binding before classifying contention; unsafe binding takes precedence. A valid bound root plus EAGAIN/EWOULDBLOCK is `repository-operation-busy`. Absent required lock/descriptor capability or another expected lock-system failure on a safe root is `repository-coordination-unavailable`; untyped programming defects are not mapped here. No supported fallback lock protocol is selected.

For these two new lifecycle codes, §10's four rows completely determine the result. Mode/apply/specs_mode echo the actual normalized invocation (including explicit keep); operation, candidate_digest and seed_policy are null because no target was classified. All paths/actions/guidance/warnings are empty, summary counts zero, mutation/rollback false, retry null and continuation NONE; errors contain the one exact §11 diagnostic. No ACTIVE, completion receipt, stage, seed, marker or consumer file is created, read as lifecycle authority, repaired or changed. A human may submit a new invocation after the competing command finishes; this is not a generated lifecycle resume.

Ordinary runtime shared holders may coexist. Existing create/import serialization may keep `system/.runtime/create.lock` **inside** the outer shared lease. Lifecycle cannot replace that lock's containing root until all shared holders have ended, so it is not the cross-generation authority.

### WIR-COORD-002 — Pre-import bootstrap and ready admission

The supported operational entrypoint is `spec-dock/scripts/spec-dock`. Its minimal stdlib-only bootstrap obtains the root lease and validates admission before importing any `spec_dock_runtime` module, loading templates/system assets or writing bytecode. All 0.2.4 candidates under this protocol use the same bootstrap bytes, fixed and recorded at #392 acceptance; #395/#396 preserve those bytes. Do not embed the full candidate digest into its own bootstrap or add an external daemon/second public entrypoint.

The invariant bootstrap may already have been read by the interpreter just before a lifecycle replacement. After obtaining its lease it resolves and validates the **currently installed** payload, not cached old paths/modules. Strict seven-key ready record, supported 0.2.4 protocol, and safely bound fixed roots/slots and matching markers are required. Lifecycle terminal publication is the authority for complete candidate contents; do not rehash the entire candidate on every runtime command. Normal commands never attempt private cleanup or use incomplete data as an old-generation fallback.

Absent, invalid, incomplete, tooling-absent or incompatible ready metadata/payload is `runtime-installation-not-ready` before command dispatch. Root identity failures use the root-binding diagnostic instead. A terminal ready installation with cleanup pending is allowed: the complete payload is already published, and only the external installer owns that residual cleanup. The runtime does not need to inspect ACTIVE or the completion receipt to decide admission.

If the script itself is absent or cannot be loaded after interruption/uninstall, the interpreter cannot promise a structured bootstrap diagnostic; normal execution still cannot proceed. Use the external installer and the existing exact operation/candidate/seed-policy recovery contract. The wrapper is not a recovery bypass for a failed admission.

### WIR-COORD-003 — Managed helper lifetime and installer handoff

Normal runtime helpers that may write the repository (including Git operations) retain the root shared lease through their last write. The parent passes the already-acquired shared descriptor only to explicitly managed writing helpers, using a narrow inherited-descriptor allowlist; it remains closed-on-exec for unrelated children. Helpers must retain it through any writing descendants. No detached writer may outlive the lease. The parent normally waits/reaps all writers before closing its reference. If only the parent is killed, the writing helper's reference still prevents installer EX acquisition. Release references with close; an explicit LOCK_UN on a shared reference must not release the whole lease while another writer remains. A helper that cannot honor this lifetime is not admitted as an unprotected writer. #392 must prove the real managed helper paths, not merely a mocked context-manager finally block.

Descriptor inheritance above is **only lifetime retention**, never installer authorization. Repo-local `update` **and** `uninstall` wrappers, for dry-run/apply and same-root/cross-target requests, follow this separate handoff:

1. Under the invoking root's shared lease, validate the wrapper request and materialize the existing external command/target/flags as primitive data. Do not mutate the target as part of handoff.
2. Return control to the immutable bootstrap, finish/reap any invoking-root writers, close all shared-lease references, then `exec` the external `uvx` installer. Do not keep root A locked while acquiring target B.
3. The installer independently binds the requested target, obtains EX and repeats full preflight. No inherited descriptor, environment variable, argument token or “already locked” shortcut permits skipping admission.
4. Once the installer starts, never resume the old installed Python modules to render a result, sync or write state. Propagate the external process streams/status directly. If uvx cannot be executed, only the immutable bootstrap may emit the existing exit-127 diagnostic: `error: uvx could not be executed. Install uv/uvx or ensure uvx is on PATH, then retry.\n`. Do not fall back to the old lifecycle implementation.

Direct imports/internal module calls are test seams, not supported concurrent operational or recovery entrypoints. This cooperative protocol excludes lifecycle/runtime overlap; it does not claim exclusion against arbitrary manual Git/filesystem edits, arbitrary consumer hooks, external writers or nonparticipating legacy commands. Managed checkout and worktree creation/removal are **not** excluded: WIR-COORD-007 through 009 bind their generation, actual target and terminal handoff. E384-DEC-002 was explicitly adopted on 2026-09-08. An invoking-root lease alone never proves coordination of another root.

### WIR-COORD-004 — Closed pre-parser runtime diagnostics

These are entrypoint admission diagnostics, not lifecycle results and not additions to the lifecycle 23-key JSON object. Even if a runtime command requested JSON, admission failure has empty stdout, exit 1 and exactly one stderr line `error: ${code}: ${diagnostic}\n`. No payload import, command handler, user-data write or private cleanup occurs.

| Runtime code | Exact diagnostic |
|---|---|
| `repository-operation-busy` | `Another SpecDock command holds repository coordination; retry after it exits.` |
| `repository-coordination-unavailable` | `Required repository coordination is unavailable; no operation was executed.` |
| `unsafe-repository-binding` | `The repository root binding is unsafe or changed during the operation.` |
| `runtime-installation-not-ready` | `SpecDock tooling is not ready; use the external installer to complete recovery before running repository commands.` |

Busy is not evidence of corruption or incomplete state. Unavailable is not permission to bypass coordination. Not-ready recovery uses the external package, preserving exact existing resume/continuation rules; no new retry command is invented by the runtime.

### WIR-COORD-005 — Accepted one-time legacy maintenance boundary

E384-DEC-001 was explicitly adopted by the user on 2026-09-08. The first exact-clean 0.2.3→0.2.4 migration is an offline tooling operation:

1. The operator stops new SpecDock command/automation starts and waits for existing legacy commands and their writing helpers to finish. This is a human operating precondition, not something inferred from an empty process snapshot or absence of a lock file.
2. Invoke the external 0.2.4 installer directly, not the old repo-local update/uninstall wrapper. Exact clean legacy admission, protected-data preservation and all wire checks still apply.
3. Keep the window closed through interruption and recovery. After durable mutation, resume only with the admitted external operation/candidate/seed-policy and cleanup continuation; do not run old commands or patch their runtime in place.
4. Reopen normal commands after ready and complete candidate verification. If the attempt blocks before any mutation and preserves exact legacy state, the operator may explicitly end the window and resume the old installation. Tooling-only legacy uninstall likewise requires quiescence and ends with tooling absent, not permission to run old tooling.

There is no new maintenance-proof flag, automatic process kill, hidden pause of user automation, legacy bridge package or scheduler. From 0.2.4 onward, successful shared/exclusive coordination replaces the maintenance-window requirement for ordinary lifecycle operations.

### WIR-COORD-006 — #392 required acceptance cases

#392 owns executable evidence for:

- Runtime SH held → each installer invocation, including uninstall dry-run and cleanup replay, fails busy before target/private-state observation and with zero mutation.
- Installer EX held → representative new/import/active/sync runtime entrypoints fail before payload import or data writes. Two ordinary shared holders coexist, and the inner create/import lock still serializes their existing critical section.
- Bootstrap bytes loaded before an intervening successful replacement → admission/import uses the complete current generation. #395/#396 candidate checks reject bootstrap drift.
- Each durable lifecycle interruption boundary → normal runtime is busy while EX survives, then not-ready after lease loss if incomplete; exact external recovery alone reaches ready. Physically missing script and ready-with-cleanup-warning have the distinct behavior stated above.
- Root symlink/rebinding and unavailable lock facilities fail closed without creating bookkeeping. Linux and macOS prove real descriptor/flock semantics.
- Writing helper paused after launch, parent alone SIGKILLed → installer remains busy until the helper's last write/exit; afterward EX succeeds. No early LOCK_UN, unexpected descriptor leak or detached unprotected writer.
- Both wrappers, every retained target/flag form, same-root and crossed A→B/B→A: no held invoking-root lease, no installer bypass, no old-module return, external stdout/stderr/status preserved, and uvx-missing exit 127.
- Exact-clean legacy maintenance, pre-mutation rejection and post-mutation recovery preserve the agreed operating boundary; tests do not pretend to prove that all human/automation launchers are stopped.

- Same-closure existing-branch checkout and a new branch at current HEAD succeed. Different or unprovable target closure stops before checkout/active/sync. Post-checkout drift stops active/sync, reports the actual branch side effect and never silently rolls back.
- Installer EX on worktree B prevents invocation A from removing B before destructive Git/filesystem work; removal EX on B prevents B runtime/installer entry. Parent-only SIGKILL does not release B while a managed removal helper is writing.
- Removal followed by same-path creation of different-inode C preserves C during post-cleanup and reports partial removal instead of following the reused pathname.
- Creation pins the source closure, reserves and binds empty B, holds B EX through materialization, and publishes its public entrypoint last. Every interruption before publication leaves normal B runtime unavailable after lease loss; publication implies the complete verified candidate. Source mismatch and a root reservation/contamination race preserve other data and disclose any newly created partial root.
- Both make dry-run/detection and make init execute only after all A/B lease references are released, using a separately opened nonlocking binding to original B. Nested external installer admission is ordinary and does not self-contend. B→C pathname substitution must never execute C's hook.
- Missing/detection-failed/skipped/succeeded/failed bootstrap observations retain the existing worktree-create exit and warning semantics. A returned hook observation is not a claim that B remains ready after arbitrary consumer code.

These tests are part of the lifecycle implementation unit, not a separate investigation or final-verification Issue.


### WIR-COORD-007 — Accepted same-generation managed checkout

E384-DEC-002 was explicitly adopted by the user on 2026-09-08. Under the invoking root's lease, a managed checkout (including issue start and active branch selection) pins the target ref to one commit before any checkout, active update or sync. Compare its provider-owned closure with the admitted installed generation: the fixed four roots, two slots, record/markers and frozen entrypoint, with content/mode and safe binding sufficient to establish identity. User-authored specs outside that closure are not required to be identical. Different or unprovable provider generation is rejected **before checkout**, using the existing command error envelope with the reason `runtime-generation-change-blocked`; no active/sync side effect is allowed.

Creating a new branch at the admitted current HEAD remains the normal supported path. A moving ref cannot substitute a different commit after preflight. Immediately after checkout and before any active update, sync or other old-module write, revalidate the provider closure. Unexpected drift stops with reason `runtime-generation-drift`, reporting the before/after branch and the fact that checkout already occurred. Do not auto-rollback the branch, hot-reload modules, start an installer or fall through to old-generation writes. These two post-dispatch command reasons are not WIR-COORD-004 pre-parser diagnostics and do not add lifecycle codes or fields.

This does not authorize arbitrary manual Git changes during execution. It closes the known managed self-replacement path without changing every runtime SH lease to EX.

### WIR-COORD-008 — Actual worktree target admission and publication

A command invoked in root A that creates or removes worktree B must coordinate **B itself**, not merely retain A's SH. Preserve the existing target/containment, current/main-worktree and unsafe-removal guards. All acquisitions are nonblocking; never wait while holding another root, upgrade a lease, remove a lock or bypass a failed target guard.

**Removal.** Bind B and acquire its EX before destructive work. Repeat target/identity guards under the lease; retain B EX through managed Git removal helpers and subsequent filesystem cleanup, with the helper lifetime rules of WIR-COORD-003 applied to every necessary A/B descriptor. A valid busy/unavailable B rejects before destructive work using the existing worktree error envelope (`remove_blocked` plus the corresponding coordination reason); it is not a lifecycle 23-key result. Root substitution uses the unsafe-binding reason.

The open B inode does not reserve its pathname after removal. Before any post-remove cleanup, resolve without following symlinks and compare with original B. Expected absence is successful removal; a different inode/symlink C at the former path is preserved without cleanup and reported as `post_remove_cleanup_failed`, with the existing partial-removal facts and an unsafe-binding reason. Do not turn pathname reuse into authority to delete C. Existing actual partial outcomes remain visible; no low-level Git metadata workaround or speculative rollback is added.

**Creation.** Pin the intended source commit and verify its provider closure matches the admitted generation before materialization; do not silently copy legacy, incomplete or different-generation provider assets from a divergent HEAD. For the existing valid absent-target path, exclusive directory creation reserves empty B. Open/bind it without following symlinks, acquire B EX and recheck identity and emptiness before populating it. A collision, contention or contamination preserves others' data and stops. If this invocation already created the empty root, disclose that partial artifact in the existing creation failure envelope; do not falsely claim zero mutation or blindly remove it.

Populate the pinned Git worktree while withholding the public `spec-dock/scripts/spec-dock` entrypoint. No arbitrary consumer hook may run during this unpublished phase. Verify the complete intended payload, strict ready metadata/markers and source closure (accounting for the withheld entrypoint), then publish the frozen bootstrap by same-directory atomic rename **last**. Preserve the final tracked index/HEAD and mode consistency; a successful creation must not depend on hiding a dirty bootstrap. Exact Git materialization calls are selected and tested during #392 elaboration, but entrypoint-last and source/binding verification are fixed acceptance conditions.

A copied ready record alone is insufficient to expose an incomplete B: until final publication, its public runtime entrypoint is absent. A crash before publication therefore leaves normal runtime unable to dispatch even after all leases disappear; a crash after publication leaves the complete verified candidate. Preserve actual partial artifacts/errors on failure, without automatic migration, retry or guessed cleanup. This publication barrier does not add a new lifecycle ACTIVE/receipt state or a legacy bridge.

### WIR-COORD-009 — Consumer bootstrap hook as terminal external handoff

The existing optional `make -n init` detection and `make init` are both arbitrary consumer code; dry-run is not a safe read-only exemption. They run only after B's entrypoint-last publication. While B EX still proves its identity, independently open a **nonlocking** root directory descriptor and verify it is the same B inode. Do not duplicate the locking descriptor: a dup would retain its open-file-description lease.

Materialize the creation result and hook request as primitive data, return to the immutable bootstrap, finish/reap all managed A/B writers and close **all** A/B flock references. Only then terminally hand off hook execution, using the nonlocking original-B directory binding as cwd (fchdir or an equivalent descriptor-bound operation), without resolving the pathname to a replacement C. Never return to old installed modules for result rendering, sync or mutation. A binding mismatch before handoff skips the hook with the existing failed/detection observation; after directory removal, ordinary hook failure is reported, never redirected to C.

Hook-invoked SpecDock commands acquire their own ordinary admission; a nested external installer obtains B EX independently and is not given a bypass or self-conflicting inherited lease. The nonlocking directory descriptor preserves identity only, not authorization or exclusion. Arbitrary raw Git/filesystem writes by this user-owned hook remain outside the cooperative SpecDock protocol. That explicit consumer-code boundary must not be used to exclude managed worktree writes before handoff.

Preserve worktree-create's current compatibility: successful creation returns exit 0 with its existing bootstrap status (`skipped`, `detection_failed`, `succeeded` or `failed`) and warning as applicable; make failure does not undo creation or become the installer's directly propagated exit status. The returned result means “B was completely published, then this hook outcome was observed”; it does **not** recertify B's current ready state after arbitrary consumer code. No automatic cleanup, reinstall or new resume command follows hook failure.
