---
種別: 要件定義書（Epic）
ID: "epic-00384"
タイトル: "Provider Test Strategy Simplification and Execution Cost Reduction"
関連GitHub: ["#384"]
状態: "draft"
最終更新: "2026-09-02"
親: ["init-local-00003"]
repository_evidence:
  repository: "chemitaro/spec-dock"
  branch: "codex/epic-00384-provider-test-strategy-planning"
  sha: "3c24bae76e86651f958bde7c716c5453fff73e56"
---

# epic-00384 Provider Test Strategy Simplification and Execution Cost Reduction — 要件定義

Normative artifacts are `artifacts/provider-lifecycle-wire-contract.md` and `artifacts/active-failure-disposition-register.md`. Their finite wire values and Issue #387 disposition rules are not delegated to implementation.

## 1. Outcome

SpecDock replaces the historical per-file provider lifecycle and sharded failure-approval gate with one fixed-ownership lifecycle and one build-once provider gate. Acceptance requires all of the following together.

- Durable provider authority is exactly four roots, two fixed skill slots and `spec-dock/spec-dock.version`; fresh-only seed creation and shared-container bootstrap are separately bounded.
- The strict seven-key record carries immutable `seed_policy`; resume is exact `(operation,candidate_digest,seed_policy)`.
- Runtime lifecycle staging survives process exit in a deterministic owner-bound namespace on the repository filesystem. Discovery uses one repository `ACTIVE.json` index and a tuple-key path; no repository temp path or temp-root scan is allowed.
- Exact clean `0.2.3` alone migrates to `0.2.4`. S40/S50 preserve checked-in legacy dogfood; S60 performs the sole complete migration; S70 performs the second complete candidate update; S80 is tracked-read-only.
- Uninstall is tooling-only, default dry-run, retains `tooling-absent-preserved-data`, and treats `--remove-specs` as mutation-zero exit 2.
- The public wire is closed at 36 codes and 123 context rows, with valid record/JSON goldens and every uninstall state/mode/resume relation fixed.
- Issue #387 remains a blocking dependency. Its report names a production/test/config candidate, not a future PR. The candidate is an ancestor of the final PR head and the only permitted tail is evidence-only. S00 discovers the unique merged PR from GitHub evidence and applies `ISS387-THREE-WAY-V2`.
- Every local admission/build/witness/download/API/attestation workspace is outside the repository. Every repository `spec-dock/.workbench/**` entry is protected and never used as a temporary target.
- The protected manifest excludes only Issue #392 `report.md` and Issue #392 `.meta.json`; both have a separate exact blob/history contract. All other initiatives and artifacts remain protected.
- S00/S30/S60 local Full Regression commands and the retained main-push workflow pass an owner-bound external `--artifact-dir`; no retained command writes repository workbench.
- `provider-evidence-<sha>` contains exactly nine actual byte files. Candidate, four receipts, four role evidence documents and all aggregate linkages are independently rehashed.
- Producer, role evidence, aggregate evidence and pre/post/Epic attestations have exact ordered schemas, compact UTF-8 plus LF serialization, hash relationships, typed failure contracts and canonical `EVIDENCE-FIXTURE-V1` byte/size/SHA-256 test vectors.
- PR-C uses two explicit heads. `PRC_COMPAT_HEAD` emits both `Provider CI / provider-tests` and `Provider CI / provider-gate`; after the new context is required and RED-tested, `PRC_FINAL_HEAD` removes only the compatibility job and reruns all authoritative evidence.
- Main remains releasable after S30, S60 and S80. S40, S50 and S70 are never main merge points.
- GitHub #392 is the sole implementation-and-verification Issue; human alone changes required contexts and merges.

## 2. Verified baseline

The repository authority for this authoring is `chemitaro/spec-dock`, branch `codex/epic-00384-provider-test-strategy-planning`, exact commit `3c24bae76e86651f958bde7c716c5453fff73e56`. At that revision, root `AGENTS.md` and the current workflows still describe the old lane/full-regression policy; `scripts.quality.verify_full_regression` defaults to repository `spec-dock/.workbench/full-regression` unless `--artifact-dir` is passed; and checked-in dogfood is exact plain `0.2.3` with markerless fixed slots. Issue #387 is separately approved and may remove, retain(reason) or split retirement candidates without owning provider lifecycle or provider-test architecture.

The repository evidence SHA is authoring provenance. The adopted bytes are bound by `SPEC_FREEZE_COMMIT`, and the later implementation base must contain both that commit and the independently verified Issue #387 merge.

## 3. Terms

- **fixed roots**: `spec-dock/docs`, `spec-dock/templates`, `spec-dock/system`, `spec-dock/scripts`.
- **fixed slots**: `.agents/skills/spec-dock`, `.agents/skills/spec-dock-grill-with-docs`.
- **record**: `spec-dock/spec-dock.version`; exact `0.2.3\n` legacy bytes or strict seven-key final JSON.
- **shared container**: repository-root `spec-dock`; create-only bootstrap authority, never whole-directory replacement/deletion authority.
- **ephemeral external workspace**: a `mkdtemp` directory below an OS temp root, realpath-proven outside the repository, used for evidence/build/download operations that need not survive an intentional cleanup.
- **persistent lifecycle stage namespace**: `<repository-real-parent>/.spec-dock-provider-stages-v1`, same-filesystem, owner-bound and process-independent.
- **resume tuple**: exact operation, candidate digest and seed policy.
- **Issue #387 implementation candidate**: last #387 commit changing production, tests, workflow/config, package metadata, provider/dogfood assets or operator policy.
- **Issue #387 evidence-only tail**: required #387 `report.md` and optional #387 `.meta.json` `updated_at` change only.
- **PRC_COMPAT_HEAD**: PR-C head that contains the final gate plus the still-emitted old required context.
- **PRC_FINAL_HEAD**: descendant that removes only the compatibility job and is the sole final source/evidence identity.
- **append-only attestation comment**: a newly created GitHub Issue comment whose canonical body hash, comment ID, author and `created_at == updated_at` are verified; editing or deletion invalidates closure.

## 4. Requirements

### E384-RQ-001 — Fixed ownership and consumer preservation

Persistent target mutation authority is exactly the four roots, two slots and record. Fresh `init` may additionally create the absent shared container, absent seeds and exact absent `.github/workflows` parent chain. Consumer initiatives, artifacts, workbench, seeds after creation, unknown paths, unrelated skills and shared-container unknown children are preserved by type, mode, ownership, link target and bytes.

### E384-RQ-002 — Ephemeral external workspaces

Admission files, baseline packages, Full Regression output, witnesses, API snapshots, downloads, run selectors and attestation drafts use an owner-bound external workspace created with `tempfile.mkdtemp(prefix="spec-dock-iss-00392-", dir=<validated OS temp root>)`. The helper verifies realpath outside repository, current UID, mode 0700, no symlink components and an exclusive canonical `OWNER.json`. Cleanup accepts only the captured handle, exact device/inode/sentinel and registered entries. Unknown content or identity drift preserves the workspace and stops.

### E384-RQ-003 — Cross-process lifecycle stage discovery

Lifecycle payload/tombstone staging uses the persistent namespace on the repository filesystem, not the ephemeral evidence workspace. The namespace has exact `NAMESPACE.json`, per-repository `REPOSITORY.json`, one deterministic `ACTIVE.json` and a deterministic tuple-key stage directory. `ACTIVE.json` is created before stage allocation, records `allocating|ready|terminal-cleanup`, and binds repository realpath hash/device/inode plus the resume tuple. The same tuple can recover after process exit, including bootstrap-before-record; a different tuple blocks. Directory scanning is forbidden.

### E384-RQ-004 — Lifecycle, record and closed wire

Final durable states are `incomplete`, `ready`, `tooling-absent-preserved-data`; observed-only states are `absent`, `legacy-0.2.3`, `blocked`. The strict record, result, action, text and exit relations are exactly the wire artifact. Unknown values, catch-all tokens or alternative path ordering are invalid.

### E384-RQ-005 — Filesystem safety and fresh bootstrap

Candidate validation and descriptor binding precede target mutation. Absent `spec-dock` is exclusively `mkdirat`-created, opened no-follow, identity-checked, fsynced and written into persistent stage ownership before record publication. Pre-record rollback removes only that exact empty identity. Roots/slots publish with Linux `renameat2` or macOS `renameatx_np` no-replace/exchange primitives; absence or mismatch fails closed.

### E384-RQ-006 — Combined hard cutover and dogfood boundaries

No uninstall-first bridge, intermediate public generation, runtime toggle, dual writer or old-engine fallback is introduced. S40/S50 remain non-main and preserve all checked-in dogfood bytes. S60 merges complete lifecycle, exact legacy proof, old-engine removal, current-gate continuity, lifecycle docs/operator guidance and one complete dogfood migration. S70 completes final gate/policy candidate changes and a second complete dogfood update. S80 edits no tracked path.

### E384-RQ-007 — Tooling-only uninstall, exact legacy and downgrade safety

Uninstall removes only owned fixed roots/slots, preserves container/seeds/data and keeps a durable absent record. `--keep-specs` is an alias; `--remove-specs` is the fixed removed-operation trap. Only exact clean `0.2.3` migrates. Old package commands against final states are mutation-zero under Python/native pre-call tripwires with positive controls.

### E384-RQ-008 — `ISS387-THREE-WAY-V2` admission

The #387 tracked report contains the candidate SHA/tree and exact 12 conditional mappings but no PR number or merge facts. Candidate-to-final-head diff is restricted to required `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00356-specdock-core-simplification-and-external-intelligence-boundary/issues/iss-00387-current-surface-workflow-residue-cleanup/report.md` and optional `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00356-specdock-core-simplification-and-external-intelligence-boundary/issues/iss-00387-current-surface-workflow-residue-cleanup/.meta.json` `updated_at` only. S00 intersects candidate-associated PRs with Issue #387 GitHub timeline links and requires exactly one merged PR; verifies candidate ancestry, tail semantics, final-head/merge tree equality, main reachability, merged report, ledger and collection; then applies the register. Any zero/multiple PR, tail drift, signature drift or unmapped node stops before S10.

### E384-RQ-009 — Protected witness and authorized exclusions

The protected witness covers every repository `spec-dock/.workbench/**` path and every initiative/artifact path except exact `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/issues/iss-00392-provider-lifecycle-and-regression-gate-hard-cutover/report.md` and `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/issues/iss-00392-provider-lifecycle-and-regression-gate-hard-cutover/.meta.json`. The report may change only in S00–S70 under the pre-merge report contract. `.meta.json` may change only its existing `updated_at` scalar. A separate external exclusion ledger records before/after blob OIDs, mode, path history and allowed-field diff. No glob, parent-directory or future metadata exclusion is allowed.

### E384-RQ-010 — Transitional Full Regression external output

Every S00/S30/S60 invocation calls `verify_full_regression --shards 4 --artifact-dir <owner-bound external directory>`. S60 minimally changes `.github/workflows/provider-full-regression.yml` to create the directory below `${{ runner.temp }}` through the external-workspace helper, pass it explicitly and upload that exact output. Workflow name, trigger, job identity, test policy and evaluation stay otherwise unchanged until S70.

### E384-RQ-011 — Failure terminalization and current-gate continuity

S00 admits every #387-permitted branch by the register. S60 mechanically fixes/supersedes admitted rows to active/approved count zero, retargets deleted distribution tests in current Provider CI, updates current lane consumers and keeps both current PR workflow and main-push Full Regression independently GREEN. S60 does not use final S70 tooling.

### E384-RQ-012 — Final CI byte graph and stable qualification

Only Linux `provider-build-artifacts` packages `PRC_FINAL_HEAD`, exactly once. Linux canonical, sdist and macOS jobs download identical candidate bytes and build zero times. `provider-attestation` needs exactly all four roles, verifies actual bytes and uploads one nine-file `provider-evidence-<sha>`. Linux qualification is bound to `specdock-linux-qualification-v1`, pinned image/resource/toolchain fingerprint, first-five 600-second/1.1 CPU ratio, 20 clean runs and 100% seeded-fault detection.

### E384-RQ-013 — Exact evidence and attestation schemas

Issue Design defines ordered keys/types/enums/nullability/units for candidate manifest, all four receipts, all four role evidence files, provider aggregate and three attestations. Serialization is compact UTF-8 plus one LF. Every child byte file is size/SHA-linked by its parent. `emit-attestation` has exact CLI, stdout, error and exit contracts. Attestations are posted as append-only GitHub Issue comments on #392 (pre/post) or #384 (Epic); identity, permissions and readback are verified.

### E384-RQ-014 — Two-head required-context transition

At `PRC_COMPAT_HEAD`, final evidence jobs and new `Provider CI / provider-gate` run together with compatibility `Provider CI / provider-tests`. The compatibility job independently validates provider-attestation and stays GREEN. Human adds the new context while old remains and reads both back. A dedicated non-merge canary makes only the new aggregate RED and proves block. After closing the canary and restoring GREEN, human removes old required context. `PRC_FINAL_HEAD` then removes only the compatibility job; all final CI/evidence/qualification is rerun on that final frozen head, followed by final required-context readback.

### E384-RQ-015 — Documentation and operator policy

S60 converges root README lifecycle, provider/dogfood migration docs and root AGENTS lifecycle/uninstall text with final `0.2.4`, while retaining current test-policy instructions. S70 converges final test-policy docs and AGENTS provider-gate instructions. S80 is read-only. Repository-wide forbidden-phrase and provider/dogfood parity checks are mandatory.

### E384-RQ-016 — Non-cyclic evidence and closure

Tracked #392 report contains pre-freeze methodology and implementation facts only. Final source/evidence/context facts are external. Human merge is verified by `PRC_FINAL_HEAD^{tree} == merge_commit^{tree}`. SpecDock finish, GitHub #392 close and #384 close are external post-merge attestations; report is not rewritten.

### E384-RQ-017 — Single Issue and human gates

GitHub #392 is the only implementation-and-verification Issue. #387 remains the dependency; #388–#390 remain superseded. Baselines/rebaselines are admission steps, not new Issues. All failure is forward-fixed in #392. Human alone changes required contexts and merges.

## 5. Accepted merge points

| Gate | Required main state |
|---|---|
| PR-A / S30 | Old public product, dormant successor, exact legacy dogfood, current gates GREEN. |
| PR-B / S60 | Complete final lifecycle/wire/docs/AGENTS lifecycle guidance, exact migration proof, old engine removed, failures zero, retained current workflows using external output, complete S60 dogfood. |
| PR-C / S80 | `PRC_FINAL_HEAD` final gate/evidence, compatibility job absent, final required-context readback, old policy absent, final docs/AGENTS, complete S70 dogfood, S80 read-only proof. |

S40, S50 and S70 are not main merge handoff points. Owner decisions required: none.
