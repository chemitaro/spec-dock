---
種別: 実装計画書（Epic）
ID: "epic-00384"
タイトル: "Provider Test Strategy Simplification and Execution Cost Reduction"
関連GitHub: ["#384"]
状態: "draft"
最終更新: "2026-09-01"
依存: ["requirement.md", "design.md", "artifacts/20260831t152024z-adr-single-implementation-unit-and-provider-hard-cutover-policy.md", "artifacts/provider-lifecycle-wire-contract.md", "artifacts/active-failure-disposition-register.md"]
親: ["init-local-00003"]
repository_evidence:
  repository: "chemitaro/spec-dock"
  branch: "codex/epic-00384-provider-test-strategy-planning"
  sha: "d145f0f0d6f35535eebc0da89b7b708824279f1f"
---

# epic-00384 Provider Test Strategy Simplification and Execution Cost Reduction — Epic計画

## 1. Governance

Epic #384 authorizes one implementation-and-verification Issue only: `iss-00392` / GitHub #392. #388–#390 remain superseded historical nodes. Research, decisions, test restructuring, CI proof and final verification are performed inside #392 rather than delegated to new Issues. Human review and merge remain mandatory.

### E384-P-001 — Dependency gate

No #392 implementation begins before #387 human merge. S00 verifies replacement manifest and `SPEC_FREEZE_COMMIT`, then independently verifies #387 repository/PR/head/tree/merge/tree equality and lineage. It parses the #387 pre-merge report mapping and the register, then derives post-merge admission from the actual merge tree, ledger and collection. Any unsupported outcome stops before S10.

### E384-P-002 — External evidence root

Before S00 reads or writes any temporary evidence, it creates a dedicated owner-bound OS temporary directory outside repository realpath. Every baseline build, admission JSON, protected witness, API snapshot, downloaded artifact, receipt and attestation file is beneath that directory. Repository `spec-dock/.workbench` is read-only protected input and is never created, modified or cleaned by #392.

## 2. Ordered execution and merge points

| PR | Internal steps | Sole main gate | State after human merge |
|---|---|---|---|
| PR-A | S10 -> S20 -> S30 | S30 | Old public lifecycle and exact legacy dogfood remain; dormant successor is tested; current gates are releasable. |
| PR-B | S40 -> S50 -> S60 | S60 | Complete `0.2.4` public lifecycle/wire/docs/AGENTS lifecycle guidance; exact old-package proof; old engine removed; admitted failures terminal; current PR and main-push gates independently GREEN; complete S60 dogfood migration. |
| PR-C | S70 -> S80 | S80 | Final consumer-first provider gate, stable environment, self-contained evidence, final AGENTS/test-policy docs, old machinery absent and S70 complete dogfood update; S80 final proof GREEN. |

S40, S50 and S70 are internal checkpoints and are not merge candidates. Main never observes an intermediate public generation, partial dogfood projection, broken workflow or missing provider/consumer.

## 3. Step governance

### E384-P-003 — PR-A

S10 implements model/candidate/record/marker and closed wire tables. S20 implements descriptor-safe external stage, shared-container bootstrap and fresh install. S30 implements update and exact resume convergence. Public route and checked-in dogfood are unchanged. PR-A may merge only after current ordinary/full gates remain GREEN.

### E384-P-004 — PR-B

S40 hard-cuts public CLI, uninstall and lifecycle docs on the PR-B branch, but explicitly leaves checked-in dogfood roots, slots, record and markers untouched. S50 proves exact migration and downgrade mutation-zero on external synthetic consumers only. S60 terminalizes the actual post-#387 admitted rows, retargets current workflow references, removes old engine/tests, updates lifecycle docs and only the lifecycle/uninstall sections of root AGENTS, then performs one complete checked-in dogfood migration. S60 is the only PR-B handoff.

### E384-P-005 — PR-C

S70 adds replacement gate/environment/tests/workflow and final test-policy docs/AGENTS sections, inventories and removes all old consumers before old providers, deletes old policy machinery on the same non-main branch and performs the second complete dogfood update. Local S70 builds are tool smoke only. S80 owns no tracked path: it freezes the head, dispatches final Provider CI, downloads actual candidate/evidence bytes into the external workspace, runs the exact verifier, completes qualification/context transition/external attestation and hands off the merge-ready PR.

## 4. Evidence contract

### E384-P-006 — Tracked report

The tracked #392 report records static methodology, admission identities available at authoring/implementation time, step RED/GREEN summaries, path ownership, terminalization rationale, dogfood/protection summaries and external attestation schemas/locations. It excludes its own hash, final frozen head/tree, final source-bound artifact hashes, future merge identity and post-merge closure facts.

### E384-P-007 — External evidence

After report commit and head freeze, all final data is external and content-addressed. The pre-merge attestation binds the frozen head/tree, report blob observed externally, exact Actions run/jobs/needs/artifact metadata, candidate and nine-file evidence bytes, environment/qualification, dogfood read-only identity and required-context snapshots. Post-merge closure binds the pre-attestation hash, human merge commit/tree, tree equality, SpecDock issue finish and GitHub #392 close. Epic closure references the post-merge record and #384 close.

### E384-P-008 — Protected witness

S00 captures a complete external witness for repository `spec-dock/.workbench` and all other protected paths. S40/S50/S60/S70/S80 compare it at their boundaries. The witness captures types, modes, ownership, symlink targets and regular-file bytes. Its storage path is outside the repository and therefore cannot alter the witnessed tree.

## 5. Required-context transition

Human admin executes exactly:

1. capture current required contexts/reviews;
2. run the new provider gate GREEN while old contexts remain;
3. add the new context as required without removing old;
4. read back old+new required;
5. create a dedicated non-merge canary where only the new gate is RED;
6. prove merge blocked;
7. close canary and restore implementation PR GREEN;
8. read back new GREEN;
9. remove only the old provider context;
10. read back final contexts and review requirement.

Any unreadable state, unblocked RED or unrelated setting drift stops the transition.

## 6. Stop and forward-fix policy

Stop the relevant gate for: spec/hash/lineage mismatch; #387 report/merge/ledger/collection mismatch; any repository workbench write; unsafe external temp identity; fixed-path or seed-policy ambiguity; unavailable native primitive; unexpected old-package mutation; unknown wire token; partial or modified dogfood; protected drift; active/unmapped failure; S60 dependency on S70 tooling; broken current workflow; old consumer remaining at S70; additional final packager; candidate/evidence/receipt byte mismatch; environment/budget/fault/flake failure; context gap; tracked report cycle; merge-tree mismatch; or stale AGENTS guidance.

The remedy is forward-fix in #392 from the appropriate prior step. Do not create a new Issue, add a runtime toggle, restore the old engine, approve a failure, introduce a skip or shard the gate.

## 7. Closure

- **Implementation complete**: S70 tracked branch is complete, report committed and no tracked change remains.
- **Pre-merge attested**: S80 frozen-head Provider CI, downloaded byte verifier, qualification and context transition are GREEN; immutable attestation exists.
- **PR merge ready**: human review and rollback information are complete.
- **Human merged**: human performs merge; PR-head tree equals merge-commit tree.
- **Issue finished**: external closure attestation records SpecDock finish and GitHub #392 close.
- **Epic closed**: #392 is finished, all Epic acceptance is rechecked and GitHub #384 closure is externally recorded.

Owner decisions required: none.
