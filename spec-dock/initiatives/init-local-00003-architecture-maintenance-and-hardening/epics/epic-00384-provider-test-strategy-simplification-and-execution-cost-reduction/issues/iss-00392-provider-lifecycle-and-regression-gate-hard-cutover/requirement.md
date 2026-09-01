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
  sha: "3c24bae76e86651f958bde7c716c5453fff73e56"
---

# iss-00392 Provider Lifecycle And Regression Gate Hard Cutover — 要件定義

## 1. Acceptance unit

This is Epic #384's sole implementation-and-verification Issue. It remains blocked until Issue #387 is human-merged and S00 admits the actual result. No investigation-only, decision-only, test-only or verification-only Issue is created. Internal PR-A/PR-B/PR-C and a canary PR remain inside #392.

## 2. End-to-end requirements

### I392-RQ-001 — Specification freeze

The replacement manifest, all canonical/support payload SHA-256 values and owner-recorded `SPEC_FREEZE_COMMIT` must match exact repository blobs. The implementation base must contain that commit and the independently admitted Issue #387 merge. Repository evidence SHA `3c24bae76e86651f958bde7c716c5453fff73e56` is provenance, not a future blanket diff base.

### I392-RQ-002 — Issue #387 evidence-only tail and unique PR

The tracked #387 report records only its semantic candidate SHA/tree and 12 remove/retain/split mappings. It contains no PR number or future merge facts. The candidate is the last commit changing production, tests, workflows/config, package metadata, provider/dogfood assets or operator policy. It must be an ancestor of the final PR head.

Candidate-to-final-head diff is exactly required `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00356-specdock-core-simplification-and-external-intelligence-boundary/issues/iss-00387-current-surface-workflow-residue-cleanup/report.md` plus optional `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00356-specdock-core-simplification-and-external-intelligence-boundary/issues/iss-00387-current-surface-workflow-residue-cleanup/.meta.json`; the optional meta change is limited to existing `updated_at`. S00 intersects candidate-associated GitHub PRs with Issue #387 timeline-connected PRs and requires exactly one merged PR in `chemitaro/spec-dock` with base `main`, exact tail, candidate ancestry and final-head/merge tree equality. Report PR-number dependency is prohibited.

### I392-RQ-003 — Conditional failure admission

All 27 source identities and all #387-permitted branches are governed by `active-failure-disposition-register.md`, rule `ISS387-THREE-WAY-V2`. Removed, retained-unchanged and split-or-renamed are mechanically admitted. Post-#387 row count is formula-derived. Missing mapping, invalid tail, zero/multiple PR, signature drift, ambiguous lineage, failed positive successor or unaccounted row stops before S10 and requires canonical amendment plus Strict rereview.

### I392-RQ-004 — Fixed target authority

Durable target authority is exactly:

```text
spec-dock/docs
spec-dock/templates
spec-dock/system
spec-dock/scripts
.agents/skills/spec-dock
.agents/skills/spec-dock-grill-with-docs
spec-dock/spec-dock.version
```

Fresh init alone may additionally create absent `spec-dock`, `spec-dock/.gitignore`, `.github`, `.github/workflows`, `.github/workflows/ci.yml` under exact constraints. Shared container is never whole-replaced/deleted.

### I392-RQ-005 — Protected data and exact exclusions

Every repository `spec-dock/.workbench/**` path is read-only protected. Initiatives/artifacts, seeds, unknown paths, unrelated skills and user data are protected except exact `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/issues/iss-00392-provider-lifecycle-and-regression-gate-hard-cutover/report.md` and `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/issues/iss-00392-provider-lifecycle-and-regression-gate-hard-cutover/.meta.json`. A separate external exclusion ledger limits report changes to its pre-merge evidence sections and meta changes to `updated_at`; all other fields/paths remain exact.

### I392-RQ-006 — Ephemeral external workspace

Admission, local builds, Full Regression output, witnesses, API snapshots, downloads, fresh consumers and attestation drafts use an external owner-bound OS-temp workspace. Purpose enum is exact, creation is `mkdtemp`, realpath must be outside the repository, mode 0700/current UID/no symlink, `OWNER.json` is exclusive mode 0600 and cleanup is handle/identity/sentinel/registered-entry bound. Repository workbench is never a destination or cleanup target.

### I392-RQ-007 — Persistent cross-process stage namespace

Lifecycle candidate/tombstone staging uses `<repository-real-parent>/.spec-dock-provider-stages-v1`, same device as repository. Namespace/repository sentinels, deterministic repository key, deterministic tuple key, exact `ACTIVE.json` and stage owner survive process exit. Discovery reads only exact ACTIVE and tuple paths; no root scan. Same tuple resumes; mismatch blocks. `allocating` supports bootstrap-without-record recovery. Cleanup removes stage then exact index and never adopts unknown content.

### I392-RQ-008 — Final version and strict record

Final version is `0.2.4`. Record path and all seven keys/types/state relations are exactly the wire artifact. `seed_policy` is immutable for one operation. Unknown/missing/duplicate keys, invalid JSON/type/link count/size or inconsistent state block.

### I392-RQ-009 — Candidate and slot ownership

Candidate is built from code-fixed four roots/two slots, includes logical path/kind/mode/content/version, and excludes seeds/record/generated markers. Source and stage digest must match. New slots require strict `.spec-dock-provider-slot.json`; markerless slots are owned only by exact legacy recognition.

### I392-RQ-010 — Classification and fresh bootstrap

Classifier returns only `absent|legacy-0.2.3|incomplete|ready|tooling-absent-preserved-data|blocked`. Fresh absent container is created through descriptor-bound exclusive `mkdirat`, no-follow open, identity capture and stage-owner update before record. Pre-record rollback removes only exact empty created identity; otherwise exact-tuple partial recovery remains.

### I392-RQ-011 — Install/update publication

Candidate stage/validation and all preflight checks precede persistent target mutation. Publish order is incomplete record, docs, templates, system, scripts, spec-dock slot, grill slot, authorized seeds, verification, terminal record, cleanup. Existing targets use native exchange; absent targets use native no-replace. Linux/macOS primitives are mandatory.

### I392-RQ-012 — Immutable seed policy and resume

`create-if-absent` is used only by `init`/`init --force` on never-installed absent. Update-on-absent, migration, reinstall, update and uninstall use `preserve-only`. Resume requires request/record/ACTIVE/stage owner tuple equality. Filesystem seed presence never determines policy.

### I392-RQ-013 — Tooling-only uninstall

Uninstall is dry-run by default and applies only with `--apply`. It preserves container/seeds/data, removes only owned roots/slots and retains tooling-absent record. Exact legacy, ready, matching incomplete-uninstall and tooling-absent dry/apply behavior are all defined by the wire matrix and goldens. `--keep-specs` is an alias.

### I392-RQ-014 — Purge removal and public compatibility

`--remove-specs` is processed before target observation and returns `spec-history-purge-removed`, mutation false, exit 2 in text/JSON. Existing command grammar, success lines, target resolution and wrapper forwarding are retained except accepted lifecycle semantics. No purge service/journal/recovery remains.

### I392-RQ-015 — Closed wire implementation

Production enums, constructors, serializers and tests must match 36 codes, 123 relation rows, 4 valid record goldens, 16 public JSON review goldens, 23 phases, action reason/status/category relations and `TARGET_PATH_ORDER`. Every blocked code has exact phase/last-completed/digest/policy relation. No unknown/catch-all branch exists.

### I392-RQ-016 — Exact legacy and old-package mutation-zero

Only exact clean `0.2.3` roots/slots/plain record migrate. Active recovery, modified/foreign/unsupported states block. Old `0.2.3` init-force/update/uninstall/remove commands against final states run under composite Python/native pre-call tripwire; each has event zero and unchanged target digest, while positive controls are caught.

### I392-RQ-017 — S40/S50 legacy dogfood preservation

S40 may update provider code, provider-side lifecycle docs and root README lifecycle sections. S40 and S50 must not modify/sync any checked-in dogfood root, fixed slot, record or marker. External before/after witness proves exact `0.2.3` record, marker absence and root/slot bytes unchanged.

### I392-RQ-018 — S60 complete dogfood and lifecycle documentation

After PR-B provider code/docs settle, S60 applies the new service once to repository root and commits all four roots, both slots, ready seven-key record and both markers for one digest. Initiatives/artifacts/workbench/seeds/user data remain protected. Root README, provider/dogfood migration docs and root AGENTS lifecycle/uninstall sections describe final tooling-only lifecycle. Test-policy AGENTS sections remain current until S70.

### I392-RQ-019 — Failure terminalization and retained current gates

S60 applies the admitted register rows to normal pass/supersession, active and approved counts zero. It retargets current Provider CI deleted tests and updates current lane consumers. S00/S30/S60 Full Regression calls pass external `--artifact-dir`. S60 minimally edits retained `.github/workflows/provider-full-regression.yml` to create an owner-bound directory under `${{ runner.temp }}`, pass it explicitly and upload it. Current PR and main-push gates are independently GREEN; final gate redesign is not advanced.

### I392-RQ-020 — Consumer-first PR-C and second dogfood update

S70 adds final provider tooling/workflow/tests/environment/docs before retiring all old policy consumers; proves consumer zero; removes old providers/data/workflow; performs complete second dogfood update and finalizes tracked report. S70 is non-main.

### I392-RQ-021 — Sole producer and exact job graph

Only `provider-build-artifacts` packages final frozen head once. Linux canonical, sdist smoke and macOS delta need only producer, download identical candidate and build zero. `provider-attestation` needs exactly all four roles; `provider-gate` needs only attestation. Compatibility `provider-tests` exists only at `PRC_COMPAT_HEAD`, needs attestation and independently validates evidence.

### I392-RQ-022 — Exact candidate/receipt/evidence schemas

Issue Design fixes exact ordered fields, types, enum/nullability, units and compact LF serialization for candidate manifest, four receipts, four role evidence files and provider aggregate. `EVIDENCE-FIXTURE-V1` supplies canonical bytes, byte sizes and SHA-256 values for candidate, all receipts/roles, aggregate and all three attestations. Parent documents hash/size actual child bytes. `provider-evidence-<sha>` contains exactly nine files in exact order. Downloaded verifier checks actual bytes plus run/job/needs/artifact metadata.

### I392-RQ-023 — Stable Linux qualification

Linux evidence uses `specdock-linux-qualification-v1`, exact descriptor/image/runner/kernel/cgroup/Python/uv/lock fingerprint, one pytest process/worker, 20 ordered runs, first five each <=600 seconds and CPU/wall <=1.1, no failure/flake/retry and 100% seeded-fault detection. Any fingerprint mismatch invalidates all runs.

### I392-RQ-024 — Two-head context transition

`PRC_COMPAT_HEAD` emits old/new contexts. New context is required while old remains and both settings are read back. A dedicated canary containing only `.github/provider-gate-canary-red` makes new gate RED while compatibility old context remains GREEN and proves merge block. After canary closure/implementation GREEN, human removes old required. `PRC_FINAL_HEAD` then removes only compatibility job from provider workflow; final CI/evidence/qualification and final context readback rerun on that head.

### I392-RQ-025 — Attestation schema and immutable object

Pre-merge, post-merge and Epic closure attestation payloads follow exact ordered schemas in Issue Design, compact LF serialization and the `EVIDENCE-FIXTURE-V1` payload/comment byte hashes. `emit-attestation` has exact args, success output and typed exits. Canonical JSON is posted verbatim in a new append-only GitHub Issue comment with a content-hash marker. Pre/post target #392; Epic targets #384. Identity, author, URL, marker/hash/bytes and `created_at==updated_at` are verified. Edit/delete invalidates evidence.

### I392-RQ-026 — Tracked report and closure

Tracked #392 report has pre-freeze methodology/implementation facts only; no own hash, final source/artifact, merge or close facts. S80 owns no tracked path. Human merge is checked by final-head tree equals merge tree. SpecDock finish and Issue/Epic close stay in external attestations.

### I392-RQ-027 — Main gates and operator policy

Only S30/S60/S80 are main gates. S60 owns lifecycle AGENTS text; S70 owns final test-policy/provider-gate text. PR-A main is old product+dormant successor; PR-B main is complete lifecycle+coherent current gates; PR-C main is final gate on `PRC_FINAL_HEAD`. Human only merges/settings. Owner decisions required: none.

## 3. Acceptance summary

Acceptance requires every requirement on the applicable exact source/tree, no repository workbench mutation, no unapproved protected exclusion, deterministic process-restart stage recovery, wire/register parsability, complete S60/S70 dogfood, independently GREEN PR-B current gates, final evidence actual-byte verification, two-head no-gap context transition, append-only attestations and human merge tree equality.
