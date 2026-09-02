---
種別: 要件定義書（Issue）
ID: "iss-00392"
タイトル: "Provider Lifecycle And Regression Gate Hard Cutover"
関連GitHub: ["#392"]
状態: "draft"
最終更新: "2026-09-02"
依存: ["iss-00387", "../../requirement.md", "../../design.md", "../../artifacts/20260831t152024z-adr-single-implementation-unit-and-provider-hard-cutover-policy.md", "../../artifacts/provider-lifecycle-wire-contract.md", "../../artifacts/active-failure-disposition-register.md"]
親: ["epic-00384", "init-local-00003"]
repository_evidence:
  repository: "chemitaro/spec-dock"
  branch: "codex/epic-00384-provider-test-strategy-planning"
  sha: "ea168b745d3f443f11a24b975f32e3bb6fb17b1a"
---

# iss-00392 Provider Lifecycle And Regression Gate Hard Cutover — 要件定義

## 1. Acceptance unit

This is Epic #384's sole implementation-and-verification Issue. It remains blocked until Issue #387 is human-merged and S00 admits the actual result. No investigation-only, decision-only, test-only or verification-only Issue is created. Internal PR-A/PR-B/PR-C and one required-context canary remain inside #392.

## 2. End-to-end requirements

### I392-RQ-001 — Specification freeze

The replacement manifest, all canonical/support payload SHA-256 values and owner-recorded `SPEC_FREEZE_COMMIT` must match exact repository blobs. The implementation base must contain that commit and the independently admitted #387 merge. Repository evidence SHA `ea168b745d3f443f11a24b975f32e3bb6fb17b1a` is provenance, not a future blanket diff base.

### I392-RQ-002 — Mapping-only #387 report

The #387 report disposition block has exact keys `schema_version,kind,issue_id,rule_id,entries`, schema 4, rule `ISS387-THREE-WAY-V2` and exactly twelve entries. It contains no repository, branch, PR number, candidate/head/tree, merge, timestamp, ledger or collection identity. #392 requires no new #387 commit boundary and no semantic-candidate/evidence-tail convention.

### I392-RQ-003 — Unique #387 merged PR

After human merge, S00 independently reads Issue #387 timeline/cross-reference PR references, fetches each PR and verifies each exact PR head through commit-association evidence. It filters to `chemitaro/spec-dock`, base `main`, merged state, report present and merge reachable from admitted main/implementation base. Exactly one PR is required. Its head tree must equal merge-commit tree. Report, ledger and pytest collection are read from the merge tree.

### I392-RQ-004 — Conditional failure admission

All 27 source identities and every #387-permitted removed/retained/split branch are governed by `active-failure-disposition-register.md`. Post-#387 row count is formula-derived. Missing/identity-bearing report fields, zero/multiple PR, signature drift, ambiguous lineage, failed successor or unaccounted row stops before S10 and requires canonical amendment plus Strict rereview.

### I392-RQ-005 — Fixed target authority

Durable target authority is exactly four roots, two slots and `spec-dock/spec-dock.version`. Fresh init alone may additionally create absent `spec-dock`, `spec-dock/.gitignore`, `.github`, `.github/workflows`, `.github/workflows/ci.yml` under exact constraints. Shared container is never whole-replaced/deleted.

### I392-RQ-006 — Protected data and exact exclusions

Every repository `spec-dock/.workbench/**` path is read-only protected. Initiatives/artifacts, seeds, unknown paths, unrelated skills and user data are protected except exact #392 `report.md` and `.meta.json`; a separate external exclusion ledger limits report to pre-freeze evidence sections and meta to `updated_at` only.

### I392-RQ-007 — Private owner roots and exact reserved trees

Each purpose creates an independent private owner root and live non-serializable handle. The owner root is never exported. The Design table maps each purpose to one exported `ISS392_WS_*` variable whose value is one exact reserved child tree. Before spawn, the live owner pre-registers every exact file or closed subtree policy; children cannot register, widen or clean. Every child command receives the reserved tree, never owner root. Unknown owner-root entry, unregistered or policy-invalid descendant, owner death or premature cleanup fails closed and preserves data. Paths, sentinels, nonces and child PIDs do not confer registration or cleanup authority.

### I392-RQ-008 — Persistent stage namespace

Candidate/tombstone stage uses the same-filesystem `.spec-dock-provider-stages-v1` namespace. Exact sentinels, repository key, tuple key, ACTIVE and stage owner survive process exit. Discovery reads only exact index/path; no scan or orphan adoption. ACTIVE and stage owner include private result family in addition to resume tuple.

### I392-RQ-009 — Mandatory terminal cleanup and deterministic continuation

Every parser-valid lifecycle invocation locks/binds the repository and resolves terminal cleanup before normal dispatch. The private ACTIVE object stores immutable `cleanup_token` plus a nullable exact deferred-invocation object. A no-token public invocation is always desired, even when its base form is the same update/init-force form selected for old cleanup; only the generated hidden-token command is cleanup-retry. The first desired request is immutable. Tokenized retry, repeat, or any third desired request cannot replace it. Cleanup failure returns the tokenized retry as `continuation.next_command` and the first deferred desired command as `continuation.after_cleanup_command`. Cleanup success is cleanup-only and returns that desired command as the sole next command, or no action. No result says to rerun the same command, no caller infers intent from `result_family`, and no old install/update retry can replace a pending uninstall.

### I392-RQ-010 — Final version and strict record

Final version is `0.2.4`. Record path and all seven keys/types/state relations are exactly the wire artifact. `seed_policy` is immutable for one operation. Unknown/missing/duplicate keys, invalid JSON/type/link count/size or inconsistent state block.

### I392-RQ-011 — Candidate and slot ownership

Candidate is code-fixed to four roots/two slots and includes logical path/kind/mode/content/version. Seeds/record/generated markers are excluded. Source and stage digest match. New slots require strict markers; markerless slots are owned only by exact legacy recognition.

### I392-RQ-012 — Classification and fresh bootstrap

Classifier returns only `absent|legacy-0.2.3|incomplete|ready|tooling-absent-preserved-data|blocked`. Fresh absent container is created by descriptor-bound exclusive `mkdirat`, no-follow open, identity capture and stage-owner update before record. Pre-record rollback removes only exact empty created identity; otherwise exact-tuple recovery remains.

### I392-RQ-013 — Install/update publication

Stage/validation/preflight precede target mutation. Publish order is incomplete record, docs, templates, system, scripts, two slots, authorized seeds, verification, terminal record, cleanup. Existing targets use native exchange; absent targets use native no-replace. Linux/macOS primitives are mandatory.

### I392-RQ-014 — Immutable seed policy and resume

`create-if-absent` is only fresh init/init-force on never-installed absent. Update-on-absent, migration, reinstall, update and uninstall are preserve-only. Resume requires request/record/ACTIVE/stage-owner tuple equality. Seed presence never determines policy.

### I392-RQ-015 — Tooling-only uninstall

Uninstall is dry-run by default and applies with `--apply`. It preserves container/seeds/data, removes only owned roots/slots and retains tooling-absent record. Exact legacy, ready, matching incomplete-uninstall and tooling-absent dry/apply behavior are fixed by wire matrix/goldens. `--keep-specs` is an alias.

### I392-RQ-016 — Purge removal and compatibility

`--remove-specs` is processed before target observation and returns `spec-history-purge-removed`, mutation false, exit 2 in text/JSON. Existing command grammar, success lines, target resolution and wrapper forwarding remain except accepted lifecycle changes. No purge service/journal/recovery remains.

### I392-RQ-017 — Closed wire implementation

Production enums/constructors/serializers/tests match 38 codes, 142 relation rows, four valid record goldens, thirty-three public JSON review goldens, 23 phases, action relations and target order. The public result has exact 23-key order and a closed `continuation` object. Cleanup warning, cleanup failure, cleanup success and lifecycle partial rows have exact next/after-cleanup action-command relations. Unknown/catch-all branch or prose-derived next action is invalid.

### I392-RQ-018 — Exact legacy and old-package mutation-zero

Only exact clean `0.2.3` roots/slots/plain record migrate. Active recovery, modified/foreign/unsupported states block. Old exact package commands against final states run under composite Python/native pre-call tripwire; each has event zero/unchanged digest, while positive controls are caught.

### I392-RQ-019 — S40/S50 legacy dogfood preservation

S40 may update provider code/provider-side lifecycle docs/root README lifecycle sections. S40/S50 do not modify or sync checked-in dogfood roots, fixed slots, record or markers. External witness proves exact legacy identity unchanged.

### I392-RQ-020 — S60 complete dogfood/docs

After PR-B provider bytes settle, S60 applies new service once to repository root and commits all four roots, both slots, ready seven-key record and both markers for one digest. Protected data remains exact. Root README, provider/dogfood migration docs and AGENTS lifecycle/uninstall sections describe final tooling-only lifecycle; test-policy sections remain current until S70.

### I392-RQ-021 — Failure terminalization and retained current gates

S60 applies admitted register rows to normal pass/supersession, active/approved count zero, retargets current Provider CI and keeps current main-push Full Regression operational. Every local/current workflow verifier receives an independent full-regression purpose workspace path. S60 does not depend on S70 tooling.

### I392-RQ-022 — Consumer-first PR-C and second dogfood update

S70 first creates replacement gate/environment/workflow/tests, then retires/replaces all old consumers, proves zero, deletes old providers/ledger/timing/sharder/conftest/workflow, updates final test-policy docs/AGENTS, performs one complete candidate-wide dogfood update, creates compatibility head, completes context transition and commits the final descendant by removing only `provider-tests`. S70 is non-main. S80 has no tracked ownership or commit instruction.

### I392-RQ-023 — Sole producer and role graph

Only `provider-build-artifacts` packages each workflow head once. Linux canonical, sdist, macOS download same candidate and build zero. `provider-attestation` needs producer+three roles and uploads one nine-file evidence artifact. `provider-gate` needs attestation only.

### I392-RQ-024 — Compatibility and aggregate actual-byte verification

Compatibility `provider-tests`, provider-attestation and S80 use the same closed verifier. Each authenticated Actions artifact download preserves the exact raw ZIP bytes, recomputes SHA-256 over the complete archive, and matches the REST `sha256:`-prefixed digest. Within the producing workflow, role-set verification also matches each bare `artifact-digest` job output. The verifier safely extracts into an empty registered reserved tree and receives both raw and extracted paths plus run/jobs/artifacts snapshots. Exact repeated role order and artifact inventory are mandatory. Compatibility packages nothing, ignores the canary marker and remains independently GREEN.

### I392-RQ-025 — Stable Linux qualification

Environment ID is `specdock-linux-qualification-v1`, bound to tracked descriptor, pinned image/resources/toolchain and one fingerprint. Twenty runs share exact fingerprint; first five meet 600 seconds/CPU ratio 1.1; failures/flakes/retries zero; seeded-fault detection 100%.

### I392-RQ-026 — Complete Provider Gate CLI, evidence schemas and permissions

Issue Design D-013–D-026 fixes all nine subcommand argv arrays, required flags, absolute/reserved path types, repeated-option order, outputs, success/failure stdout/stderr, codes/exits, raw archive semantics, safe extraction, ordered schemas, units, nullability, digest inputs, fixture bytes and parent-child relations. Workflow-level permissions are empty; every job has an exact least-privilege override. Structural tests reject missing/extra/inherited/write permissions, wrong needs, raw download, archive path, verifier argument, packager or upload.

### I392-RQ-027 — Distinct external two-head identities

Tracked report records only method and expected one-job diff, never actual compatibility/final SHA/tree/run. Actual identities are external. Final head is a distinct descendant that removes only compatibility job. All authoritative evidence reruns on final head; equal identities or additional diff is invalid.

### I392-RQ-028 — Required-context transition

Compatibility head emits both contexts. Human adds new while old remains, reads both, uses a dedicated non-merge canary where new RED/old GREEN blocks, restores compatibility GREEN, removes old required, then creates/finalizes final head and reads new-only context after final rerun.

### I392-RQ-029 — Tracked report and pre-merge attestation

Tracked report has pre-freeze method/implementation facts only. S80 owns no tracked path. Pre-merge payload includes external compatibility/final SHA/tree/run identities and final byte evidence, but not its own future comment identity. Human posts it to #392 and external comment receipt verifies actual comment.

### I392-RQ-030 — Ordered post-merge closure with post-sync recovery

After human merge/tree equality, automation runs exact `issue finish`, whose current implementation closes #392 before active clear/post-sync. If exit 0, that interval is accepted. Exit 1 is recoverable only when measured facts prove #392 closed, active cleared and post-sync failed: read the unique original close event, restore active with exact `active set --id iss-00392`, require successful readback, and rerun issue finish against the already-closed Issue. At most three finish attempts are allowed; later attempts require `already_closed=true` and must not create a new close event. The accepted post payload includes all attempts/restores and identifies the final successful interval. Repeated sync failure, ambiguous close event or failed restore stops. No `close --id iss-00392` is run.

### I392-RQ-031 — Comment receipts

After each append-only comment is posted, external `comment-receipt-v1` records target issue, comment ID/URL/actor, created/updated, payload SHA, body SHA/size and verification time. Receipt is not embedded in payload or tracked tree. Pre/post target #392; Epic target #384. Editing/deletion/timestamp/body mismatch invalidates dependent closure.

### I392-RQ-032 — Main gates and operator policy

Only S30/S60/S80 are main gates. S60 owns lifecycle AGENTS text; S70 final test-policy/provider-gate text. PR-A main is old product+dormant successor; PR-B main complete lifecycle+coherent current gates; PR-C main final gate on final head. Human only merges/settings. `owner_decisions_required=[]`.

## 3. Acceptance summary

Acceptance requires every requirement on the applicable exact source/tree, no repository workbench mutation, one private owner root and exported reserved tree per purpose, deterministic cleanup continuation, mapping-only #387 report, complete S60/S70 dogfood, independently GREEN current gates, raw-archive actual-byte verification with exact permissions, post-sync recovery and measured closure, and human merge tree equality.
