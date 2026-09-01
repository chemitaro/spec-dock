---
種別: ADR
ID: "20260831t152024z-adr"
タイトル: "Single Implementation Unit and Provider Hard Cutover Policy"
状態: "accepted"
決定日: "2026-08-31"
最終更新: "2026-09-01"
対象: ["epic-00384", "iss-00392"]
repository_evidence:
  repository: "chemitaro/spec-dock"
  branch: "codex/epic-00384-provider-test-strategy-planning"
  sha: "d145f0f0d6f35535eebc0da89b7b708824279f1f"
---

# ADR: Single Implementation Unit and Provider Hard Cutover Policy

Normative artifacts: `artifacts/provider-lifecycle-wire-contract.md` and `artifacts/active-failure-disposition-register.md`.

## Context

Epic #384 changes managed provider ownership, migration, uninstall, public wire, dogfood, test failure disposition and CI artifact production. Splitting these decisions across implementation/research/test-only Issues or publishing an intermediate generation would create multiple writers, ambiguous recovery and broken merge points. Independent Strict review also established that temporary evidence cannot live under protected repository workbench, #387's tracked report cannot contain future merge facts, S40/S50 must preserve exact legacy dogfood, provider evidence must include actual role-evidence bytes, and operator guidance must match each main merge state.

## Decision

### ADR-D1 — One Issue

GitHub #392 is the sole implementation-and-verification Issue. Internal PRs, steps and a required-context canary are execution mechanisms, not new Issues. #387 remains a separate blocking dependency and its canonical documents are not changed by #392.

### ADR-D2 — Combined hard cutover and three main gates

PR-A merges only at S30 with old public product. PR-B keeps S40/S50 internal and merges only at S60 with complete final lifecycle. PR-C keeps S70 internal and merges only at S80 with final provider gate. No uninstall-first bridge, intermediate public generation, runtime toggle, dual writer or automatic old-engine fallback.

### ADR-D3 — Fixed lifecycle and immutable seed policy

Durable authority is four roots, two slots and one strict record. Fresh init alone may create absent seeds and shared container. The seven-key record includes immutable `seed_policy`; resume identity is `(operation,candidate_digest,seed_policy)`. Update-on-absent, migration, reinstall, update and uninstall are preserve-only. Uninstall is tooling-only, retains a tooling-absent record and never purges consumer history.

### ADR-D4 — Closed public wire

`provider-lifecycle-wire-contract.md` is the only wire authority. It enumerates every record relation, observed state, public code context, candidate/policy nullability, phase/last-completed pair, action reason/status/category, array ordering, retry, message, JSON/text golden and exit. Unknown/catch-all values and implementation choices are invalid.

### ADR-D5 — Exact legacy and safe filesystem

Only exact clean `0.2.3` is migrated. Shared container bootstrap and root/slot publication are descriptor-bound, no-follow and native-atomic. Active recovery, unsafe type/binding, unsupported version and modified legacy block. Old package mutation-zero is proved by composite Python/native pre-call tripwire.

### ADR-D6 — #387 pre-merge and post-merge evidence separation

Issue #387 tracked report records only pre-merge candidate head/tree and remove/retain/split mappings. It does not predict a merge commit/tree or post-merge ledger. After human merge, S00 independently queries GitHub, verifies exact repository/PR/head/tree/merge/tree equality and ancestry, then cross-checks merged report, ledger and collection. `active-failure-disposition-register.md` defines every admitted branch and S60 consequence; row count is formula-derived and Luna chooses nothing.

### ADR-D7 — External owner-bound temporary workspaces

Every #392 temporary file is stored below a freshly-created OS temporary directory whose real path is outside repository realpath and whose device/inode/UID/mode/sentinel are captured. Cleanup is limited to that exact identity and registered contents. Collision or unknown content fails closed. Repository `spec-dock/.workbench/**` is protected read-only and never a temp or cleanup location. Protected witnesses are external and compare the complete original tree, including kinds, modes and symlink targets.

### ADR-D8 — Dogfood transition boundaries

S40 and S50 preserve the checked-in exact legacy dogfood bytes, all roots, both slots, record and marker absence. S60 performs the one complete legacy migration and commits four roots, two slots, record and markers for one candidate digest. S70 performs the second complete candidate-wide update after final candidate changes. S80 has no tracked ownership and performs no update, sync or build. Partial dogfood projection is never mergeable.

### ADR-D9 — Operator documentation split

S60 changes root AGENTS lifecycle/uninstall sections to describe tooling-only uninstall, removed purge trap and exact retry while retaining current test-policy sections. S70 changes test-policy/provider-gate sections to final one-process/same-wheel policy and removes old ledger/shard/main-push instructions. README/provider/dogfood lifecycle docs converge at S60; final test-policy docs converge at S70.

### ADR-D10 — Transitional current-gate continuity

S60 removes old product engine/tests and terminalizes failures, but retargets current provider CI and keeps current full-regression consumers/providers coherent. Current PR and main-push gates are independently GREEN. S60 does not require final provider-gate tooling. S70 adds replacement consumers/providers before removing all old consumers and then old providers in one non-main change set.

### ADR-D11 — Sole frozen-head packaging producer

Only final Linux job `provider-build-artifacts` packages the frozen head, exactly once. Linux canonical, sdist and macOS jobs download the same immutable candidate and build zero times. Attestation needs exactly all four jobs. Local S70 build is pre-freeze tool smoke only; S80 never builds locally.

### ADR-D12 — Self-contained downloaded evidence

`provider-evidence-<sha>` contains exactly nine files: provider-evidence, four receipts and four role evidence files. Provider evidence hashes actual receipt and role-evidence bytes and binds source/tree, run/jobs/artifacts, candidate files, build counts, environment and metrics. The same `verify-downloaded-artifact` command is used in attestation and S80 and validates actual downloaded bytes, not assertions alone.

### ADR-D13 — Stable environment and no-gap context transition

Qualification is bound to `specdock-linux-qualification-v1`, pinned descriptor/image/resource/toolchain fingerprint. Any mismatch invalidates all runs. Human adds new required context while old remains, proves RED blocking, restores GREEN, then removes only old provider context.

### ADR-D14 — Non-cyclic evidence and human merge

Tracked report ends before head freeze and contains no self-referential/future facts. Final evidence is immutable external data. Human merge is verified by tree OID equality, not commit SHA equality. SpecDock finish and GitHub Issue/Epic close facts are external post-merge records.

## Rejected alternatives

- New investigation, decision, tests-only or verification-only Issues.
- S40, S50 or S70 main merge.
- Seed policy inferred from files or aliases.
- Repository workbench as temporary evidence storage.
- #387 report predicting a future merge identity.
- Fixed 15-row post-#387 assumption or implementer-selected successor.
- Partial dogfood sync at S40/S50/S60/S70.
- More than one frozen-head packager or local final build.
- Evidence bundle without role-evidence bytes.
- Old required context removal before new required RED proof.
- Runtime toggle, fallback engine, approved failure, skip or sharding workaround.

## Consequences

Main remains releasable at each merge boundary; lifecycle/data authority is closed; #387 results are admitted without modifying #387; protected workbench cannot be polluted by evidence; dogfood matches every candidate-changing main state; final artifacts and metrics are reproducible and byte-verifiable. Costs are larger non-main PR checkpoints, native filesystem dependency, external evidence handling and exact Linux environment maintenance.

## Supersession and consistency

#388–#390 remain superseded historical nodes. Epic/Issue R/D/P, this ADR, both normative artifacts and Luna handoff must state the same decisions. Any contradiction stops implementation for canonical correction and Strict rereview. `owner_decisions_required=[]`.
