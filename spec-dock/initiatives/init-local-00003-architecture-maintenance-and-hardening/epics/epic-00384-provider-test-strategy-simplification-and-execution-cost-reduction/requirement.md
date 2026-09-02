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
  sha: "ea168b745d3f443f11a24b975f32e3bb6fb17b1a"
---

# epic-00384 Provider Test Strategy Simplification and Execution Cost Reduction — 要件定義

Normative artifacts are `artifacts/provider-lifecycle-wire-contract.md` and `artifacts/active-failure-disposition-register.md`. Their finite public wire, failure-admission, evidence and closure rules are not delegated to implementation.

## 1. Outcome

SpecDock replaces the historical per-file provider lifecycle and sharded failure-approval gate with one fixed-ownership lifecycle and one build-once provider gate. Acceptance requires these outcomes together.

- Durable target authority is exactly four roots, two fixed skill slots and `spec-dock/spec-dock.version`; fresh seed/container creation is separately bounded.
- The seven-key record carries immutable `seed_policy`; lifecycle resume is exact `(operation,candidate_digest,seed_policy)`.
- Process-independent staging uses one deterministic namespace and `ACTIVE.json`; private cleanup token plus deferred invocation and public continuation separate tokenized cleanup retry from the desired next lifecycle command, and cleanup-only return never dispatches.
- Every evidence/build/download purpose has a private non-exported owner root and one exported exact reserved tree. A live FD-backed owner reserves, spawns, seals, upload-confirms and cleans; paths/nonces are never cleanup authority.
- Exact clean `0.2.3` alone migrates to `0.2.4`. S40/S50 preserve checked-in legacy dogfood, S60 performs one complete migration, S70 one complete update, and S80 is tracked-read-only.
- Uninstall is tooling-only, dry-run by default, retains `tooling-absent-preserved-data`, and treats `--remove-specs` as mutation-zero exit 2.
- The public wire is closed at 38 codes and 142 relation rows, including terminal-cleanup recovery, with four valid record goldens and thirty-three public JSON review goldens.
- Issue #387 remains a blocking dependency. Its tracked report contains only the twelve remove/retain/split mappings. S00 independently discovers exactly one merged PR and applies `ISS387-THREE-WAY-V2` to merge-tree evidence.
- The final evidence graph is produced by one Linux packager. All roles, attestation, compatibility and S80 preserve authenticated raw Actions ZIP bytes, recompute API/upload digests, safe-extract and verify actual bytes under exact least-privilege permissions.
- Required-context cutover uses distinct compatibility/final heads and reruns authoritative evidence after removal of the compatibility job.
- Post-merge closure records only measured facts. If issue finish closes #392 but post-sync fails, exact active restoration and at most three already-closed finish attempts produce one accepted final interval while preserving the original close event.
- GitHub #392 is the sole implementation-and-verification Issue; human alone merges and changes required contexts.

## 2. Verified baseline

Repository authority for this authoring is `chemitaro/spec-dock`, branch `codex/epic-00384-provider-test-strategy-planning`, exact commit `ea168b745d3f443f11a24b975f32e3bb6fb17b1a`. At that revision the current root `AGENTS.md`, provider workflows, Full Regression verifier and exact legacy dogfood still represent the transitional `0.2.3` system. Issue #387 is being implemented separately and its canonical R/D/P must not be changed by this Epic.

The repository evidence SHA is authoring provenance. Adopted bytes are later bound by `SPEC_FREEZE_COMMIT`; the implementation base must contain that commit and the independently verified #387 merge.

## 3. Terms

- **fixed roots**: `spec-dock/docs`, `spec-dock/templates`, `spec-dock/system`, `spec-dock/scripts`.
- **fixed slots**: `.agents/skills/spec-dock`, `.agents/skills/spec-dock-grill-with-docs`.
- **record**: `spec-dock/spec-dock.version`; exact `0.2.3\n` legacy bytes or strict seven-key final JSON.
- **resume tuple**: exact operation, candidate digest and seed policy.
- **persistent stage namespace**: `<repository-real-parent>/.spec-dock-provider-stages-v1`, bound to repository device/inode and current UID.
- **terminal cleanup**: mandatory cleanup-only prelude; private deferred invocation and public continuation preserve the desired next command across old-family cleanup retry.
- **purpose workspace**: one private `mkdtemp` owner root/live handle plus one exported exact reserved tree; owner root is never a child input or cleanup token.
- **Issue #387 mapping block**: pre-merge report JSON containing only schema/rule and twelve disposition entries; no repository/PR/commit/tree/merge identity.
- **PRC_COMPAT_HEAD**: external identity at which both old and new required contexts are emitted.
- **PRC_FINAL_HEAD**: distinct descendant that removes only the compatibility `provider-tests` job and owns final evidence.
- **comment receipt**: external `comment-receipt-v1` created after posting; it binds observed comment identity/body without being embedded in the attestation payload.

## 4. Requirements

### E384-RQ-001 — Fixed ownership and protection

Persistent target mutation authority is exactly the four roots, two slots and record. Fresh `init` may additionally create the absent shared container, absent seeds and exact absent `.github/workflows` parent chain. Consumer initiatives, artifacts, repository workbench, seeds after creation, unknown paths, unrelated skills and shared-container unknown children are preserved by type, mode, ownership, link target and bytes.

### E384-RQ-002 — Private owner roots and exact reserved trees

Each purpose independently creates a private owner root and live non-serializable handle. The root is never exported. Design maps every `ISS392_WS_*` variable to exactly one reserved child tree; all commands receive that tree only. Before spawn the owner pre-registers each fixed output or closed subtree policy, then seals the exact descendant inventory, remains alive through upload confirmation and cleans only by handle. Children cannot register or clean. Unknown, unregistered or policy-invalid entries, owner death or path-only authority fail closed.

### E384-RQ-003 — Persistent stage, deferred invocation and terminal cleanup

`ACTIVE.json` binds the old resume tuple/result family, an exact `cleanup_token`, and a nullable exact deferred-invocation object. A public no-token command is always a desired request, even when its base command equals the old operation retry; the generated cleanup-only command is machine-distinct because it carries hidden `--provider-cleanup-token <active token>`. The first desired request is immutable; tokenized retry, repeat, or third command cannot replace it. Cleanup failure returns the tokenized retry plus optional desired-after-cleanup command; cleanup success is cleanup-only and returns that desired command or no action. The caller uses only the public continuation object, so an old install/update can never replace a pending uninstall.

### E384-RQ-004 — Closed lifecycle wire

Durable/observed states and all public relations are exactly the wire artifact: 38 codes, 142 rows, 23 phases, four record goldens and thirty-three JSON review goldens. The 23-key result includes exact continuation `next_action,next_command,after_cleanup_action,after_cleanup_command`; no prose-derived action, catch-all token or alternative ordering exists.

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

### E384-RQ-012 — Sole producer, raw-byte verifier and permissions

Only Linux `provider-build-artifacts` packages a workflow head once. Every consuming job preserves authenticated raw artifact ZIP bytes, matches SHA-256 against API `sha256:<hex>` and upload output `<hex>`, safe-extracts, and verifies raw/extracted/API bytes. Provider-attestation and compatibility/S80 use the same verifier with exact repeated role order. Workflow-level permissions are empty and every job has the exact least-privilege override fixed in Issue Design; structural tests reject drift.

### E384-RQ-013 — Stable qualification and complete Provider Gate CLI

Qualification remains bound to `specdock-linux-qualification-v1`. Issue Design fixes exact argv/flags/path types/repeated ordering for all nine provider-gate subcommands, exact stdout/stderr/codes/exits, raw archive rules, evidence schemas, permissions and mechanically hashed fixture bytes. No CLI or evidence choice is deferred.

### E384-RQ-014 — Safe two-head required-context transition

`PRC_COMPAT_HEAD` emits old and new contexts. Human adds the new context while old remains, reads back both, and proves intentional new-gate RED blocking on a dedicated non-merge canary while compatibility `provider-tests` remains GREEN. After implementation GREEN, human removes old required. `PRC_FINAL_HEAD` then removes only the compatibility job and is distinct from compatibility head. All authoritative CI/evidence/qualification is rerun on final head before merge.

### E384-RQ-015 — Non-cyclic tracked/external evidence

Tracked #392 report contains pre-freeze methodology and implementation facts only. It contains neither actual compatibility/final head identities nor final source-bound artifacts or post-merge facts. Actual head/tree/run identities exist only in external evidence. Any final tracked change invalidates the evidence and requires a new compatibility/final sequence.

### E384-RQ-016 — Measured closure and bounded post-sync recovery

After tree equality, exact issue finish closes #392 before active clear/post-sync. Exit 0 is accepted. Exit 1 is recoverable only for measured closed+active-cleared+post-sync-failed: read the unique original close event, restore active with exact `active set --id iss-00392`, and rerun issue finish with `already_closed=true`, at most three attempts. The post payload records all attempts/restores and the final successful interval. Ambiguous close events, restore failure or repeated third failure stops. No redundant close command is used.

### E384-RQ-017 — Documentation, single Issue and human gates

S60 converges lifecycle README/provider/dogfood docs and AGENTS lifecycle/uninstall text while retaining current test-policy guidance. S70 converges final test-policy/provider-gate guidance and creates both compatibility and final tracked heads; S80 is read-only rerun/readback/comment. GitHub #392 is the only implementation Issue; #387 remains the dependency and #388–#390 remain superseded. Human alone changes settings and merges.

## 5. Accepted merge points

| Gate | Required main state |
|---|---|
| PR-A / S30 | Old public product, dormant successor, exact legacy dogfood, current gates GREEN. |
| PR-B / S60 | Complete final lifecycle/wire/docs/AGENTS lifecycle guidance, exact migration proof, old engine removed, failures zero, retained current workflows using purpose workspaces, complete S60 dogfood. |
| PR-C / S80 | Distinct final head, compatibility job absent, raw/extracted/API byte evidence and permission structure verified, new required context read back, old policy absent, final docs/AGENTS, complete S70 dogfood, S80 tracked-read-only proof. |

S40, S50 and S70 are not main merge handoff points. `owner_decisions_required=[]`.
