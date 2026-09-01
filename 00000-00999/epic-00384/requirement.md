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
  sha: "f96d031ea86d3757374f3de14d588f1ba09a0864"
---

# epic-00384 Provider Test Strategy Simplification and Execution Cost Reduction — 要件定義

Normative artifacts are `artifacts/provider-lifecycle-wire-contract.md` and `artifacts/active-failure-disposition-register.md`. Their finite public wire, failure-admission, evidence and closure rules are not delegated to implementation.

## 1. Outcome

SpecDock replaces the historical per-file provider lifecycle and sharded failure-approval gate with one fixed-ownership lifecycle and one build-once provider gate. Acceptance requires these outcomes together.

- Durable target authority is exactly four roots, two fixed skill slots and `spec-dock/spec-dock.version`; fresh seed/container creation is separately bounded.
- The seven-key record carries immutable `seed_policy`; lifecycle resume is exact `(operation,candidate_digest,seed_policy)`.
- Process-independent lifecycle staging uses one deterministic same-filesystem namespace and one exact `ACTIVE.json`; terminal cleanup is completed before dispatching any later operation.
- Every evidence/build/download workspace is an independently created owner-bound OS temporary directory for one exact purpose. No aggregate external root and no repository `.workbench` output exist.
- Exact clean `0.2.3` alone migrates to `0.2.4`. S40/S50 preserve checked-in legacy dogfood, S60 performs one complete migration, S70 one complete update, and S80 is tracked-read-only.
- Uninstall is tooling-only, dry-run by default, retains `tooling-absent-preserved-data`, and treats `--remove-specs` as mutation-zero exit 2.
- The public wire is closed at 37 codes and 123 relation rows, including terminal-cleanup recovery, with four valid record goldens and sixteen public JSON review goldens.
- Issue #387 remains a blocking dependency. Its tracked report contains only the twelve remove/retain/split mappings. S00 independently discovers exactly one merged PR and applies `ISS387-THREE-WAY-V2` to merge-tree evidence.
- The final provider evidence graph is byte-verifiable, self-contained and produced from one Linux packaging job. The compatibility context performs the same downloaded-byte verification as S80.
- Required-context cutover uses distinct compatibility/final heads and reruns authoritative evidence after removal of the compatibility job.
- Post-merge closure records only measured facts, in the order merge-tree equality, SpecDock finish, Issue close, post-close attestation, Epic close, Epic attestation.
- GitHub #392 is the sole implementation-and-verification Issue; human alone merges and changes required contexts.

## 2. Verified baseline

Repository authority for this authoring is `chemitaro/spec-dock`, branch `codex/epic-00384-provider-test-strategy-planning`, exact commit `f96d031ea86d3757374f3de14d588f1ba09a0864`. At that revision the current root `AGENTS.md`, provider workflows, Full Regression verifier and exact legacy dogfood still represent the transitional `0.2.3` system. Issue #387 is being implemented separately and its canonical R/D/P must not be changed by this Epic.

The repository evidence SHA is authoring provenance. Adopted bytes are later bound by `SPEC_FREEZE_COMMIT`; the implementation base must contain that commit and the independently verified #387 merge.

## 3. Terms

- **fixed roots**: `spec-dock/docs`, `spec-dock/templates`, `spec-dock/system`, `spec-dock/scripts`.
- **fixed slots**: `.agents/skills/spec-dock`, `.agents/skills/spec-dock-grill-with-docs`.
- **record**: `spec-dock/spec-dock.version`; exact `0.2.3
` legacy bytes or strict seven-key final JSON.
- **resume tuple**: exact operation, candidate digest and seed policy.
- **persistent stage namespace**: `<repository-real-parent>/.spec-dock-provider-stages-v1`, bound to repository device/inode and current UID.
- **terminal cleanup**: mandatory pre-dispatch completion of a durable terminal operation's registered stage cleanup and `ACTIVE.json` removal.
- **purpose workspace**: one independently-created owner-bound `mkdtemp` directory and non-serializable cleanup handle for one exact purpose.
- **Issue #387 mapping block**: pre-merge report JSON containing only schema/rule and twelve disposition entries; no repository/PR/commit/tree/merge identity.
- **PRC_COMPAT_HEAD**: external identity at which both old and new required contexts are emitted.
- **PRC_FINAL_HEAD**: distinct descendant that removes only the compatibility `provider-tests` job and owns final evidence.
- **comment receipt**: external `comment-receipt-v1` created after posting; it binds observed comment identity/body without being embedded in the attestation payload.

## 4. Requirements

### E384-RQ-001 — Fixed ownership and protection

Persistent target mutation authority is exactly the four roots, two slots and record. Fresh `init` may additionally create the absent shared container, absent seeds and exact absent `.github/workflows` parent chain. Consumer initiatives, artifacts, repository workbench, seeds after creation, unknown paths, unrelated skills and shared-container unknown children are preserved by type, mode, ownership, link target and bytes.

### E384-RQ-002 — Independent purpose workspaces

The exact purposes are `admission`, `baseline-build`, `protected-witness`, `full-regression-s00`, `full-regression-s30`, `full-regression-s60`, `tripwire`, `fresh-consumer`, `workflow-api`, `artifact-download`, `attestation-draft`. Each invocation creates a separate owner-bound OS-temp directory and separate non-serializable cleanup handle. No aggregate root, subdirectory-derived cleanup authority or path-only reopen exists. The helper verifies outside-repository realpath, current UID, mode 0700, no symlink components and exact exclusive `OWNER.json`; cleanup accepts only the captured handle and registered entries.

### E384-RQ-003 — Persistent stage and terminal cleanup

Lifecycle candidate/tombstone staging is process-independent and uses the deterministic same-filesystem namespace. `ACTIVE.json` binds repository identity, operation, candidate digest, seed policy, tuple key and private result family. On every invocation, after repository lock/binding and before normal dispatch, any durable terminal stage is cleaned. Stage present, stage already absent, ACTIVE present/absent and crash after ACTIVE unlink are all deterministic. Successful cleanup permits any new intent; cleanup failure returns exact `terminal-cleanup-failed` with the old result-family retry and cannot permanently block the repository.

### E384-RQ-004 — Closed lifecycle wire

Durable states are `incomplete`, `ready`, `tooling-absent-preserved-data`; observed-only states are `absent`, `legacy-0.2.3`, `blocked`. Record, result, action, text, phase, retry and exit relations are exactly `provider-lifecycle-wire-contract.md`: 37 codes, 123 rows, 23 phase values, 24 last-completed values, four record goldens and sixteen public JSON review goldens. Unknown values, catch-all tokens or alternative path ordering are invalid.

### E384-RQ-005 — Filesystem safety and fresh bootstrap

Candidate validation and descriptor binding precede target mutation. Absent `spec-dock` is exclusively `mkdirat`-created, opened no-follow, identity-checked, fsynced and recorded in stage ownership before record publication. Pre-record rollback removes only the exact empty created identity. Roots/slots use Linux `renameat2` or macOS `renameatx_np` no-replace/exchange primitives; unavailable or changed bindings fail closed.

### E384-RQ-006 — Combined hard cutover and dogfood boundaries

No uninstall-first bridge, intermediate public generation, runtime toggle, dual writer or old-engine fallback exists. S40/S50 are non-main and preserve every checked-in dogfood byte. S60 merges complete lifecycle, legacy proof, old-engine removal, current-gate continuity, final lifecycle docs/operator guidance and one complete dogfood migration. S70 completes final gate/policy candidate changes and one complete dogfood update. S80 edits no tracked path.

### E384-RQ-007 — Tooling-only uninstall, exact legacy and downgrade safety

Uninstall removes only owned fixed roots/slots, preserves container/seeds/data and retains the durable absent record. `--keep-specs` is an alias; `--remove-specs` is the fixed removed-operation trap. Only exact clean `0.2.3` migrates. Old package commands against final states are mutation-zero under Python/native pre-call tripwires with positive controls.

### E384-RQ-008 — `ISS387-THREE-WAY-V2` admission without report identity

The #387 tracked report has exact top-level keys `schema_version,kind,issue_id,rule_id,entries` and twelve conditional mappings. It has no repository, PR number, candidate/head/tree, merge, ledger or collection identity. After human merge, S00 collects same-repository PR references from Issue #387 timeline/cross-reference evidence, fetches each PR, verifies its head commit association, filters to base `main` and merged state, and requires exactly one. It verifies PR-head-tree/merge-tree equality and main lineage, then reads report/ledger/collection from the merge tree and applies the register. No new #387 commit boundary or report-to-merge identity/tail rule is required.

### E384-RQ-009 — Protected witness and exact exclusions

The protected witness covers every repository `spec-dock/.workbench/**` entry and all initiative/artifact paths except exact #392 `report.md` and `.meta.json`. A separate external exclusion ledger limits report changes to authorized pre-freeze sections and meta changes to the existing `updated_at` scalar. No parent/glob exclusion exists. Witness and exclusion artifacts are stored in their own purpose workspaces outside the repository.

### E384-RQ-010 — Transitional Full Regression external output

Every S00/S30/S60 invocation passes its exact purpose workspace path to `verify_full_regression --artifact-dir`. S60 minimally changes the retained main-push workflow to create an independent `full-regression-s60` workspace below `${{ runner.temp }}`, retain its cleanup handle for the job, pass the exact path, and upload that path. No repository workbench output is permitted.

### E384-RQ-011 — Failure terminalization and PR-B gate continuity

S00 admits every #387-permitted branch by the register. S60 mechanically fixes/supersedes admitted rows to active/approved count zero, retargets deleted distribution tests in current Provider CI, updates current lane consumers and keeps current PR and main-push workflows independently GREEN. S60 does not use final S70 tooling.

### E384-RQ-012 — Sole producer, compatibility verifier and final evidence

Only Linux `provider-build-artifacts` packages a frozen workflow head exactly once. Linux canonical, sdist and macOS download identical candidate bytes and build zero times. `provider-attestation` needs all four roles, verifies actual bytes and uploads exactly one nine-file `provider-evidence-<sha>`. At `PRC_COMPAT_HEAD`, `provider-tests` needs producer and attestation, downloads candidate/evidence and run/jobs/artifacts API snapshots, then invokes the same `verify-downloaded-artifact` interface as S80; it never reads the canary marker and remains independently GREEN.

### E384-RQ-013 — Stable qualification and evidence schemas

Linux qualification is bound to `specdock-linux-qualification-v1`, pinned descriptor/image/resources/toolchain and one fingerprint across twenty runs. Issue Design fixes ordered schemas, canonical UTF-8 compact+LF bytes and hash relations for candidate, four role evidence documents, four receipts, provider aggregate, three attestations and `comment-receipt-v1`. Every subordinate byte file is independently rehashed.

### E384-RQ-014 — Safe two-head required-context transition

`PRC_COMPAT_HEAD` emits old and new contexts. Human adds the new context while old remains, reads back both, and proves intentional new-gate RED blocking on a dedicated non-merge canary while compatibility `provider-tests` remains GREEN. After implementation GREEN, human removes old required. `PRC_FINAL_HEAD` then removes only the compatibility job and is distinct from compatibility head. All authoritative CI/evidence/qualification is rerun on final head before merge.

### E384-RQ-015 — Non-cyclic tracked/external evidence

Tracked #392 report contains pre-freeze methodology and implementation facts only. It contains neither actual compatibility/final head identities nor final source-bound artifacts or post-merge facts. Actual head/tree/run identities exist only in external evidence. Any final tracked change invalidates the evidence and requires a new compatibility/final sequence.

### E384-RQ-016 — Measured closure order

After human merge: verify final-head-tree equals merge-tree; run `python3 ./spec-dock/scripts/spec-dock issue finish`; verify its result; run `python3 ./spec-dock/scripts/spec-dock close --id iss-00392`; read actual #392 close event; create/post/read back post-merge closure on #392; re-evaluate Epic acceptance; close `epic-00384`; read actual #384 close event; create/post/read back Epic closure on #384. Payloads do not include their own future comment identities. Separate external comment receipts bind posted comments.

### E384-RQ-017 — Documentation, single Issue and human gates

S60 converges lifecycle README/provider/dogfood docs and AGENTS lifecycle/uninstall text while retaining current test-policy guidance. S70 converges final test-policy/provider-gate guidance. GitHub #392 is the only implementation Issue; #387 remains the dependency and #388–#390 remain superseded. Human alone changes settings and merges.

## 5. Accepted merge points

| Gate | Required main state |
|---|---|
| PR-A / S30 | Old public product, dormant successor, exact legacy dogfood, current gates GREEN. |
| PR-B / S60 | Complete final lifecycle/wire/docs/AGENTS lifecycle guidance, exact migration proof, old engine removed, failures zero, retained current workflows using purpose workspaces, complete S60 dogfood. |
| PR-C / S80 | Distinct final head, compatibility job absent, authoritative final evidence rerun, new required context read back, old policy absent, final docs/AGENTS, complete S70 dogfood, S80 tracked-read-only proof. |

S40, S50 and S70 are not main merge handoff points. `owner_decisions_required=[]`.
