---
種別: 設計書（Epic）
ID: "epic-00384"
タイトル: "Provider Test Strategy Simplification and Execution Cost Reduction"
関連GitHub: ["#384"]
状態: "draft"
最終更新: "2026-09-01"
依存: ["requirement.md", "artifacts/20260831t152024z-adr-single-implementation-unit-and-provider-hard-cutover-policy.md", "artifacts/provider-lifecycle-wire-contract.md", "artifacts/active-failure-disposition-register.md"]
親: ["init-local-00003"]
repository_evidence:
  repository: "chemitaro/spec-dock"
  branch: "codex/epic-00384-provider-test-strategy-planning"
  sha: "d145f0f0d6f35535eebc0da89b7b708824279f1f"
---

# epic-00384 Provider Test Strategy Simplification and Execution Cost Reduction — 設計

## 1. Architecture

```text
public CLI
  -> closed public-result adapter
  -> provider lifecycle service
       -> fixed target classifier
       -> packaged candidate builder
       -> exact legacy-0.2.3 recognizer
       -> descriptor-bound filesystem
            -> external owner-bound stage, never repository .workbench

PR-A/S30: dormant successor, old public route
PR-B/S60: complete 0.2.4 lifecycle + current gates + complete dogfood migration
PR-C/S80: final provider gate + self-contained evidence + old policy removed
```

The production source of truth is `src/spec_dock/`. Dogfood is a checked-in consumer, not an independently edited source. The two normative artifacts close public wire values and #387 disposition branching.

## 2. Lifecycle boundary

### E384-D-001 — Code-fixed targets

The lifecycle service derives all persistent target paths from constants. Four roots are `spec-dock/docs`, `templates`, `system`, `scripts`; two slots are the fixed `.agents/skills` slots; the record is `spec-dock/spec-dock.version`. Seeds are fresh-only absent creation. The shared `spec-dock` directory may be bootstrapped but is never disposable as a whole.

### E384-D-002 — State and resume

Final record keys are exactly `schema_version,state,operation,version,candidate_digest,seed_policy,skill_slots`. Durable states are incomplete, ready and tooling-absent-preserved-data. Observed-only states are absent, legacy-0.2.3 and blocked. Resume identity is exact operation/candidate/policy. The wire artifact is the sole authority for each durable relation, public code, phase pair and serializer output.

### E384-D-003 — Candidate and slot marker

Candidate digest covers version and canonical sorted logical path/kind/mode/content records for four roots and two slot payloads. It excludes seeds, record and generated slot markers. Source and stage digests must match. Each new slot contains `.spec-dock-provider-slot.json` bound to slot/version/candidate digest.

### E384-D-004 — Fresh bootstrap and publication

Repository root and parents are held by no-follow descriptors under an exclusive lock. Candidate is fully staged and validated outside the repository before mutation. If `spec-dock` is absent, `mkdirat` creates it exclusively; it is immediately opened no-follow, identity-checked and fsynced, and the external owner record is updated before the incomplete record is published. Pre-record rollback may remove only that exact empty identity. Roots/slots publish in the fixed order and use native no-replace/exchange primitives. Terminal record is last; post-terminal external cleanup failure alone may become completed-with-warnings.

## 3. External workspace and protection

### E384-D-005 — Portable external workspace

A single helper creates operation workspaces using `tempfile.mkdtemp(prefix="spec-dock-iss-00392-", dir=os.environ.get("TMPDIR") or tempfile.gettempdir())`. It captures repository realpath and workspace realpath, rejects equality or descendant containment using component-aware comparison, rejects symlink components and wrong ownership, requires mode `0700`, and writes `OWNER.json` with exclusive no-follow create. Sentinel fields are schema version, Issue ID, purpose, repository realpath SHA-256, UID, nonce, root device/inode and creation time. An existing or colliding path is never reused; a fresh random workspace is attempted and collision evidence is recorded.

### E384-D-006 — Cleanup authority

Cleanup receives the captured workspace handle, not an arbitrary path. It reopens the parent and workspace no-follow, matches device/inode/uid/mode and exact sentinel bytes, proves the workspace remains outside the repository, then deletes only entries whose relative paths were registered by that operation. Any unknown entry, replaced identity, missing sentinel or ownership mismatch preserves the workspace and reports a hard stop. Repository `.workbench` is neither a workspace root nor a cleanup target.

### E384-D-007 — Complete protected witness

The baseline witness is stored outside the repository and recursively captures every repository `spec-dock/.workbench` entry plus initiatives, artifacts, seeds and other declared protected roots. Each row records relative path, kind, mode, UID/GID, link target bytes for symlinks, size and content SHA-256 for regular files. Directory order is UTF-8 bytewise. Before/after comparison is exact and the witness files themselves are outside the witnessed tree. Special entries are recorded by kind/device identity and never opened as regular files.

## 4. #387 admission and failure disposition

### E384-D-008 — Pre-merge #387 evidence

Issue #387's tracked report may contain only candidate-time data: schema, repository, PR number, candidate head SHA/tree, report version and one conditional mapping for each original row 4–15. It does not contain a future merge SHA/tree, merge time or post-merge ledger blob. The accepted mapping enum is removed, retained-unchanged or split-or-renamed, with exact fields defined by the register.

### E384-D-009 — Post-merge independent verification

S00 queries GitHub after merge and verifies exact repository, PR number, merged state, report candidate head/tree, merge commit, merge tree and PR-head-tree/merge-tree equality. It verifies ancestry and reads the report blob, post-merge ledger and full collection from the merge tree. The register's closed formula derives admitted rows. A report cannot assert its own future merge identity and no implementation agent chooses a disposition.

### E384-D-010 — S60 terminalization

S60 fixes each admitted failure-lineage row to a normal pass or applies the already-fixed supersession. It updates the transitional ledger, timing and lane consumers without changing their policy, removes stale deleted-node references and requires active/approved failure counts zero. Current PR workflow and current main-push verifier remain separate, runnable and GREEN.

## 5. Dogfood and operator-document transitions

### E384-D-011 — S40/S50 preserve legacy dogfood

The baseline dogfood identity is exact plain record bytes `0.2.3\n` and markerless fixed slots. S40 changes provider lifecycle code and provider-side docs only; it does not edit any `spec-dock/{docs,templates,system,scripts}` path, fixed slot, record or marker. S50 uses only external synthetic consumers and leaves the checked-in dogfood byte-identical. Provider/dogfood parity is intentionally deferred until complete migration at S60; partial projection is forbidden.

### E384-D-012 — S60 complete migration and lifecycle guidance

After all PR-B provider code/docs are settled, S60 runs the final new lifecycle service once against repository root. It commits four roots, two slots, seven-key ready record and both markers for one candidate digest. It verifies the external protected witness unchanged. Root README and provider/dogfood lifecycle docs describe final `0.2.4`. Root `AGENTS.md` changes only lifecycle/uninstall paragraphs: purge removed, `--remove-specs` mutation-zero exit 2, exact same-tuple retry. Its current pytest/full-regression sections remain until S70.

### E384-D-013 — S70 second update and final operator policy

S70 first completes final provider-gate code, test-policy docs, workflow and AGENTS test-policy sections, retires old consumers before providers, deletes old policy machinery, then runs one candidate-wide update of checked-in dogfood and commits the second digest/record/markers. S80 performs read-only record/marker/digest/validate checks and no tracked operation.

## 6. Provider gate and evidence

### E384-D-014 — Consumer-first PR-C graph

Replacement tests and provider-gate modules are added before any old provider is removed. Every import/reference consumer of `tests.conftest`, full-regression baseline/verifier, ledger/timing and old workflow is retired or replaced. AST/import scan, repository grep, collection and workflow structural tests prove zero remaining consumer; only then are providers/data/workflow deleted on the same non-main branch.

### E384-D-015 — Sole packaging producer

Final jobs and needs are fixed:

```text
provider-build-artifacts: []
provider-linux-canonical: [provider-build-artifacts]
provider-sdist-smoke: [provider-build-artifacts]
provider-macos-delta: [provider-build-artifacts]
provider-attestation:
  [provider-build-artifacts, provider-linux-canonical,
   provider-sdist-smoke, provider-macos-delta]
provider-gate: [provider-attestation]
```

Only producer invokes packaging exactly once. Each consumer downloads `provider-candidate-<sha>`, verifies its Actions artifact metadata/content digest and emits one receipt artifact containing one receipt and one role evidence file, with build count zero.

### E384-D-016 — Self-contained provider evidence

`provider-attestation` downloads candidate, four receipt artifacts and Actions run/job/artifact API JSON. It validates actual bytes and creates `provider-evidence-<sha>` with exactly these names in order:

```text
provider-evidence.json
provider-receipt-producer.json
producer-build-evidence.json
provider-receipt-linux-canonical.json
linux-canonical-evidence.json
provider-receipt-sdist-smoke.json
sdist-smoke-evidence.json
provider-receipt-macos-delta.json
macos-delta-evidence.json
```

`provider-evidence.json` hashes every receipt and evidence byte file and binds repository, source commit/tree, run/job/artifact IDs and names, candidate manifest/wheel/sdist hashes, producer count 1, consumer count 0, stable environment, qualification metrics and role status. The downloaded verifier independently validates this nine-file directory and candidate bytes against API snapshots; stated hashes without matching bytes are invalid.

### E384-D-017 — Stable qualification

Linux role evidence binds `specdock-linux-qualification-v1`, tracked descriptor hash, immutable base image digest, built image ID, runner image, kernel/cgroup, x86_64, 2 CPU, 8 GiB, Python/uv/lock versions, exact 20 runs, first-five budget, CPU/wall, seeded faults and retry/flake counts. Mismatched fingerprint invalidates all runs.

### E384-D-018 — Required context and evidence graph

Human transition order is capture old -> new GREEN -> add new required while old remains -> read back both -> dedicated canary RED and blocked -> close canary -> implementation GREEN -> remove old provider-only -> final readback. Tracked report is finalized before head freeze. CI/evidence/context facts go to immutable external pre-merge attestation. Merge closure compares tree objects and records post-merge facts externally.

## 7. Failure and stop model

Pre-mutation invalidity returns a closed blocked/error wire result. Durable partial mutation permits only exact same-tuple forward retry. Unsafe temp identity, workbench drift, #387 evidence mismatch, unknown wire value, partial dogfood, broken current/final gate, extra packager, incomplete evidence, environment drift, context gap or tree mismatch stops the relevant gate. No fallback engine, policy skip, ledger approval, sharding workaround or new Issue is permitted.

## 8. Traceability

| Requirement | Design |
|---|---|
| E384-RQ-001–004 | D-001–007 |
| E384-RQ-005–007 | D-001–004, D-011–012 and wire artifact |
| E384-RQ-008–009 | D-008–010 and register artifact |
| E384-RQ-010–011 | D-011–014 |
| E384-RQ-012–013 | D-014–018 |
| E384-RQ-014–015 | D-018 and Issue closure protocol |
