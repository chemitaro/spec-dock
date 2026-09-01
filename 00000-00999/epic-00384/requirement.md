---
種別: 要件定義書（Epic）
ID: "epic-00384"
タイトル: "Provider Test Strategy Simplification and Execution Cost Reduction"
関連GitHub: ["#384"]
状態: "draft"
最終更新: "2026-09-01"
親: ["init-local-00003"]
repository_evidence:
  repository: "chemitaro/spec-dock"
  branch: "codex/epic-00384-provider-test-strategy-planning"
  sha: "d145f0f0d6f35535eebc0da89b7b708824279f1f"
---

# epic-00384 Provider Test Strategy Simplification and Execution Cost Reduction — 要件定義

Normative artifacts are `artifacts/provider-lifecycle-wire-contract.md` and `artifacts/active-failure-disposition-register.md`. Their closed wire and disposition rules are not delegated to implementation.

## 1. Outcome

SpecDock provider distribution lifecycle and provider test execution are replaced by one fixed-ownership lifecycle and one build-once gate. The outcome is accepted only when all of the following hold together.

- Persistent provider mutation authority is exactly four tooling roots, two fixed skill slots and `spec-dock/spec-dock.version`.
- The seven-key record carries immutable `seed_policy`; resume is exact `(operation,candidate_digest,seed_policy)`.
- A fresh absent shared `spec-dock` container is created only through descriptor-bound bootstrap and exact empty rollback.
- Exact clean `0.2.3` alone is migrated one-shot to `0.2.4`; active legacy recovery and modified or unsupported legacy states are not guessed.
- Uninstall is tooling-only, dry-run by default, and retains a durable `tooling-absent-preserved-data` record. `--remove-specs` is a mutation-zero exit-2 trap.
- The public result wire is closed: all codes, phase pairs, nullability, action reasons, path ordering, messages, retry commands, JSON and text goldens are fixed by the wire artifact.
- Issue #387 remains a blocking dependency. Its permitted remove, retain(reason) and split results are consumed deterministically without changing #387 canonical documents.
- Every temporary admission, build, witness, download, API snapshot and attestation workspace is outside the repository. All repository `spec-dock/.workbench/**` content is protected read-only consumer data.
- S40 and S50 preserve exact legacy dogfood. S60 performs the sole complete legacy-to-0.2.4 dogfood migration; S70 performs the second complete candidate-wide update; S80 is tracked-read-only.
- PR-B keeps current PR and main-push gates coherent. PR-C retires all old consumers before providers and replaces them atomically with the final provider gate.
- Only Linux `provider-build-artifacts` packages the frozen head. Downstream Linux canonical, sdist, macOS and attestation jobs consume the same downloaded bytes with build count zero.
- `provider-evidence-<sha>` is self-contained and contains exactly provider evidence, four receipts and four role evidence files with verified byte hashes.
- Root `AGENTS.md` lifecycle/uninstall guidance is corrected at S60; final test-policy/provider-gate guidance is corrected at S70.
- PR merge is human-only. New required context is added while old contexts remain, then intentional RED proves blocking, then GREEN is restored and old provider-only context is removed.
- Epic #384 has one implementation-and-verification Issue only: GitHub #392.

## 2. Current verified baseline

Repository authority for this authoring is `chemitaro/spec-dock`, branch `codex/epic-00384-provider-test-strategy-planning`, exact commit `d145f0f0d6f35535eebc0da89b7b708824279f1f`. At that commit, the current canonical set still describes the old per-file managed distribution, old failure ledger/sharder and old operator guidance, while the checked-in dogfood record is exact plain `0.2.3` and both fixed slots have no new marker. The current root `AGENTS.md` still describes `--remove-specs` as destructive and the current full-regression policy. Issue #387 is separately approved and may remove, retain or split retirement candidates, but must not redesign Epic #384 distribution or provider-test policy.

The repository evidence SHA is research provenance, not the future implementation-base diff authority. The imported replacement bytes are bound through `SPEC_FREEZE_COMMIT`; #387 is then verified from its own PR and merge graph.

## 3. Terms

- **fixed roots**: `spec-dock/docs`, `spec-dock/templates`, `spec-dock/system`, `spec-dock/scripts`.
- **fixed slots**: `.agents/skills/spec-dock`, `.agents/skills/spec-dock-grill-with-docs`.
- **shared container**: repository-root `spec-dock`; create-only bootstrap authority, never whole-directory replacement or deletion authority.
- **seeds**: `spec-dock/.gitignore` and `.github/workflows/ci.yml`; fresh-init-only absent creation, then consumer-owned.
- **record**: `spec-dock/spec-dock.version`; plain `0.2.3\n` only for exact legacy, strict seven-key JSON for final lifecycle.
- **external workspace**: an owner-bound `mkdtemp` directory below an OS temp root whose canonical real path is outside the repository real path.
- **protected workbench**: every path under repository `spec-dock/.workbench/**`, including pre-existing symlinks and special entries; never used for Epic #384 temporary data.
- **#387 pre-merge disposition block**: tracked report data containing only facts available before human merge, including candidate head/tree and mappings, not future merge identity.
- **external closure evidence**: immutable content-addressed GitHub/Actions evidence created after the tracked head is frozen.
- **main merge gates**: S30 for PR-A, S60 for PR-B and S80 for PR-C. S40, S50 and S70 are internal non-main checkpoints.

## 4. Requirements

### E384-RQ-001 — Fixed ownership and protection

Durable target authority is exactly the four roots, two slots and record. Fresh `init` may additionally create the absent shared container, absent seeds and the exact absent `.github/workflows` parent chain. Initiatives, artifacts, generated state outside fixed roots, all repository workbench content, seeds after creation, unknown paths and unrelated skills are byte/type/mode/link-target preserved.

### E384-RQ-002 — External temporary workspace

All admission files, package builds, legacy fixtures, protected witnesses, downloads, receipts, API snapshots, run selectors and attestations are written only to an external owner-bound workspace. Creation uses `tempfile.mkdtemp(prefix="spec-dock-iss-00392-", dir=<OS temp root>)`, captures real path/device/inode/uid/mode, proves the real path is outside the repository, creates an exclusive `OWNER.json` sentinel with repository realpath hash, Issue ID, process UID and nonce, and accepts cleanup only after exact identity/sentinel verification. Collision, symlink, replaced directory, wrong owner, group/other write or repository containment fails closed. No command writes or deletes repository `.workbench`.

### E384-RQ-003 — Lifecycle and resume identity

The lifecycle classifies `absent`, `legacy-0.2.3`, `incomplete`, `ready`, `tooling-absent-preserved-data` and `blocked`. Final records serialize only the three durable states. `seed_policy` is `create-if-absent` only for never-installed fresh `init`; update-on-absent, migration, reinstall, update and uninstall are `preserve-only`. One operation preserves its policy through incomplete and terminal records. Resume requires exact operation, candidate digest and seed policy across request, record and stage.

### E384-RQ-004 — Safe shared-container bootstrap and atomic publication

Candidate validation and parent binding precede target mutation. An absent shared container is exclusively created with `mkdirat`, immediately opened no-follow, identity-checked and recorded in the external stage owner before record publication. A pre-record failure removes it only when exact identity and emptiness are proven; otherwise it remains a partial failure recoverable only by the same resume tuple. Roots/slots use native no-replace/exchange publication on Linux/macOS and fail closed without the required primitive.

### E384-RQ-005 — Combined hard cutover and exact legacy boundary

No uninstall-first bridge, intermediate public generation, runtime toggle, dual writer or old-engine fallback is introduced. S40 and S50 run on one PR-B branch and may not be merged. S60 merges complete `0.2.4` lifecycle, exact migration proof, old-engine removal, final lifecycle docs, current-gate continuity and complete dogfood migration together. Only exact clean `0.2.3` is migrated; active recovery, modified payload, invalid record and unsupported version block pre-mutation.

### E384-RQ-006 — Tooling-only uninstall and closed public wire

Uninstall is default dry-run and `--apply` confirmation. It removes only owned fixed roots and slots, preserves container, seeds and consumer data, and retains a tooling-absent record. `--keep-specs` is a compatibility alias. `--remove-specs` returns exact code `spec-history-purge-removed`, mutation false and exit 2 before target observation. All public record/result/action/text relations are exactly those in `provider-lifecycle-wire-contract.md`; no implementation-defined code, token, catch-all, path order or message exists.

### E384-RQ-007 — Old-package mutation-zero

Old exact `0.2.3` package commands against final ready and tooling-absent workspaces are executed under a startup composite tripwire. Python filesystem mutation and Linux `renameat2` or macOS `renameatx_np` calls are intercepted before the underlying call. Positive controls must be caught and every old command must produce zero target mutation events and an identical target digest.

### E384-RQ-008 — Deterministic #387 admission

The source ledger's 27 original node/signature identities remain the register authority. #387 tracked report contains one pre-merge disposition block for conditional rows with candidate repository, PR number, head SHA/tree, report schema and remove/retain/split mapping only. S00 independently obtains the merged PR from GitHub after merge, requires exact repository/PR/head/tree match, obtains merge SHA/tree, verifies head-tree equals merge-tree, verifies ancestry, reads the merged report blob and post-merge ledger/collection, then applies the closed register branch. Missing mapping, unexpected node, signature drift, multiple failure-lineage nodes or out-of-contract tree result stops before S10 for spec-owner amendment and Strict rereview. Post-#387 row count is formula-derived, never fixed to 15.

### E384-RQ-009 — Failure terminalization and transitional gate continuity

S60 mechanically fixes every admitted active row or applies the register's supersession rule, resulting in active count zero and approved failure count zero. It retargets only deleted distribution tests in the current `.github/workflows/provider-ci.yml`, updates current lane consumers and keeps the current main-push Full Regression graph operational. S60 does not depend on S70-only tooling. PR-B current PR workflow and current main-push verifier are independently GREEN.

### E384-RQ-010 — Dogfood and documentation boundaries

S40 may modify provider source, root README lifecycle sections and provider-side lifecycle docs but must not directly edit or synchronize any dogfood root, either fixed slot, record or marker. S50 also leaves exact legacy dogfood unchanged. S60 applies the new service once to the repository root and commits all four roots, both slots, seven-key ready record and both markers as one complete `0.2.4` candidate while preserving protected data. S60 also updates root `AGENTS.md` lifecycle/uninstall sections only. S70 owns final candidate/test-policy docs, final AGENTS test-policy sections and a second complete candidate-wide dogfood update. S80 owns no tracked path and runs no update/sync/build.

### E384-RQ-011 — Consumer-first PR-C replacement

On one non-main PR-C branch, S70 first creates the replacement gate, stable environment, workflow and tests; then retires or replaces all remaining old-policy consumers, including lane/baseline tests and imports; proves consumer zero; deletes old providers, ledger, timing, sharder, root policy hook and main-push workflow; and performs the second complete dogfood update. S70 is not mergeable. S80 proves the final gate before PR-C merge.

### E384-RQ-012 — Sole producer and self-contained evidence

After tracked head freeze, only Linux job `provider-build-artifacts` may invoke packaging. It uploads one candidate and producer receipt. Linux canonical, sdist smoke and macOS delta download the same candidate and invoke no build. `provider-attestation` needs exactly producer plus three consumers, downloads candidate, all receipts and all role evidence bytes, verifies them and uploads exactly one `provider-evidence-<sha>`. That artifact contains exactly nine files: `provider-evidence.json`, four role receipt JSON files and four role evidence JSON files. The verifier validates actual bytes, schemas, SHA-256 linkages, source/tree, run/job/artifact metadata, build counts and role metrics.

### E384-RQ-013 — Stable qualification and no-gap context transition

Linux qualification environment ID is `specdock-linux-qualification-v1` and is bound to the tracked descriptor, pinned container base digest, x86_64, 2 CPU, 8 GiB, Python, uv and lock fingerprints. Mismatch invalidates the whole 20-run series. First five runs are each <=600 seconds with process-tree CPU/wall <=1.1; all 20 have zero flake/retry and seeded-fault detection is 100%. Human admin adds the new required context while old contexts remain, reads back both, proves intentional RED blocking on a non-merge canary, restores GREEN, then removes only the old provider context.

### E384-RQ-014 — Non-cyclic evidence and closure

Tracked #392 report contains pre-freeze methodology and implementation facts only, with no own hash, final head, final source-bound artifact hash or post-merge facts. Frozen-head build/qualification/context data is stored in immutable external pre-merge attestation. Human merge is verified by PR-head tree OID equality with merge-commit tree OID. SpecDock finish and Issue/Epic closure are external post-merge attestations; tracked report is not rewritten.

### E384-RQ-015 — One Issue and human-only merge

GitHub #392 is the sole implementation-and-verification Issue. Baseline and rebaseline are admissions, not new Product decisions. Internal PRs and canary PR are execution mechanisms, not Issues. Failure is forward-fixed in #392; no research-only, decision-only, tests-only or verification-only Issue is added. Human performs all main merges and required-context writes.

## 5. Non-scope

- User-owned spec-history purge.
- Migration catalog beyond exact `0.2.3`.
- Release publication, tags or PyPI.
- Sharding, xdist or larger hardware as a budget escape.
- Reimplementation or modification of Issue #387 canonical documents.
- Changes to Issue #372 canonical evidence.
- Automatic rollback, automatic Issue creation or agent merge.

## 6. Accepted merge-point policy

| Main gate | Required state after human merge |
|---|---|
| PR-A / S30 | Old public product; dormant successor only; current gates and exact legacy dogfood unchanged. |
| PR-B / S60 | Complete final lifecycle and wire; exact legacy proof; old engine removed; active failures zero; current PR/main-push gates GREEN; lifecycle docs/AGENTS aligned; complete S60 dogfood candidate committed. |
| PR-C / S80 | Final consumer-first provider gate; self-contained evidence; old policy machinery absent; final AGENTS/test-policy docs; complete S70 dogfood candidate; S80 tracked-read-only evidence GREEN. |

S40, S50 and S70 are never main merge handoff points.

## 7. Trace to Issue #392

| Epic requirement | Issue authority |
|---|---|
| E384-RQ-001–004 | I392-RQ-004–016; I392-D-001–018; S10–S30 |
| E384-RQ-005–007 | I392-RQ-017–021; wire artifact; S40–S50 |
| E384-RQ-008–009 | register artifact; I392-RQ-002–003/023; I392-D-013–015/022; S00/S60 |
| E384-RQ-010–011 | I392-RQ-021–024/031–032; I392-D-019–024; S40/S60/S70 |
| E384-RQ-012–013 | I392-RQ-025–029; I392-D-025–033; S70/S80 |
| E384-RQ-014–015 | I392-RQ-030/033; S80 and external closure protocol |

Owner decisions required: none.
