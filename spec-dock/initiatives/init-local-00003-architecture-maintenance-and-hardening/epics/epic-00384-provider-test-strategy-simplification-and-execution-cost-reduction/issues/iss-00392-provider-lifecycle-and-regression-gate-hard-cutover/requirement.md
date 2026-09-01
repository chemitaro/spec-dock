---
種別: 要件定義書（Issue）
ID: "iss-00392"
タイトル: "Provider Lifecycle And Regression Gate Hard Cutover"
関連GitHub: ["#392"]
状態: "draft"
最終更新: "2026-09-01"
依存: ["iss-00387", "../../requirement.md", "../../design.md", "../../artifacts/20260831t152024z-adr-single-implementation-unit-and-provider-hard-cutover-policy.md", "../../artifacts/provider-lifecycle-wire-contract.md", "../../artifacts/active-failure-disposition-register.md"]
親: ["epic-00384", "init-local-00003"]
repository_evidence:
  repository: "chemitaro/spec-dock"
  branch: "codex/epic-00384-provider-test-strategy-planning"
  sha: "d145f0f0d6f35535eebc0da89b7b708824279f1f"
---

# iss-00392 Provider Lifecycle And Regression Gate Hard Cutover — 要件定義

Normative wire authority is `../../artifacts/provider-lifecycle-wire-contract.md`. Normative failure-disposition authority is `../../artifacts/active-failure-disposition-register.md`. Their finite values and branches are not delegated to implementation.

## 1. Objective and acceptance unit

This Issue is the sole implementation-and-verification unit for Epic #384. It delivers the fixed provider lifecycle, exact legacy migration, tooling-only uninstall, public compatibility, old-package mutation-zero, failure terminalization, build-once provider gate, stable Linux qualification, dogfood convergence, and external closure evidence. No decision-only、research-only、test-only、CI-only、or verification-only Issue may be added. Any unmet acceptance remains in #392 and is forward-fixed fail closed.

## 2. End-to-end requirements

### I392-RQ-001 — Specification freeze

Before implementation, verify all replacement-manifest payload hashes against the exact repository blobs in an owner-recorded `SPEC_FREEZE_COMMIT`; require that commit to be an ancestor of the implementation base. Repository evidence SHA `d145f0f0d6f35535eebc0da89b7b708824279f1f` is research provenance, not a blanket future-main diff base.

### I392-RQ-002 — #387 pre-merge report and post-merge identity

Issue #387 remains a hard dependency and its canonical R/D/P are read-only. Its tracked report may contain only pre-merge facts: exact immutable implementation candidate head/tree and one closed disposition entry for each conditional source row. It must not contain future PR/merge/close identity. After human merge, S00 independently fetches GitHub PR and merge data and verifies repository、PR、head SHA/tree、merge SHA/tree、tree equality、main ancestry、report blob、post-merge ledger、collection、and #387 allowlisted delta.

### I392-RQ-003 — Conditional failure admission

Apply `ISS387-THREE-WAY-V2` from the normative register to rows 4–15. Removed、retained unchanged、and split/renamed are all accepted only when their exact evidence relations hold. Post-#387 row count is formula-derived. Missing report evidence、unmapped row、signature drift、ambiguous lineage、failed successor、or #387-contract-external result stops before S10 and requires spec-owner amendment plus independent Strict re-review. `owner_decisions_required` remains empty.

### I392-RQ-004 — Fixed durable mutation paths

Provider durable mutation authority is limited to:

```text
spec-dock/docs
spec-dock/templates
spec-dock/system
spec-dock/scripts
.agents/skills/spec-dock
.agents/skills/spec-dock-grill-with-docs
spec-dock/spec-dock.version
```

Fresh `init` may additionally create absent shared `spec-dock` container、the absent exact `.github/workflows` parent chain for the consumer CI seed、and the two absent seeds. No arbitrary path list、wildcard、manifest-provided target、or whole-container delete authority exists.

### I392-RQ-005 — Protected consumer-owned data

`spec-dock/initiatives/**`、every nested `artifacts/**`、the complete repository `spec-dock/.workbench` tree、consumer seeds、unknown non-target paths、unrelated skills、and shared-container unknown children are read-only protected data. Before/after witnesses compare bytes、type、mode、uid/gid、link target、size/hash、and link count as applicable. Witness output is stored outside the repository and outside the witnessed tree.

### I392-RQ-006 — External temporary workspace

Every admission file、baseline/final build、witness、download、receipt、API snapshot、run selector、tripwire output、and attestation staging file is created only in an owner-bound external temporary directory. Repository `.workbench` is never written or deleted. Creation uses the exact contract in Issue Design I392-D-016: realpath outside repository、0700 owner directory、nofollow binding、0600 exclusive sentinel、purpose enum、identity checks、collision rejection、and conservative cleanup. Unsafe cleanup preserves the entire directory and fails.

### I392-RQ-007 — Final version and strict record

Final package version is `0.2.4`. `spec-dock/spec-dock.version` is strict compact UTF-8 JSON with exactly seven ordered keys: `schema_version,state,operation,version,candidate_digest,seed_policy,skill_slots`. All field types、nullability、enum and cross-field relations are exactly those in the wire Artifact. Unknown、missing、duplicate、oversized、unsafe-type、or noncanonical records are blocked.

### I392-RQ-008 — Immutable seed-policy discriminator

Allowed values are `create-if-absent` and `preserve-only`. Only never-installed absent `init`/`init --force` selects create. Update-on-absent、reinstall、legacy migration、ready update、and uninstall select preserve. One operation keeps the policy from incomplete through terminal record. Resume requires exact `(operation,candidate_digest,seed_policy)` across request、stage owner、and record; current seed existence is never used to infer it.

### I392-RQ-009 — Skill-slot authority

Each final slot requires an exact `.spec-dock-provider-slot.json` matching slot、version、and candidate digest. Markerless slots are owned only through exact legacy recognition. Invalid/foreign marker、markerless modified tree、symlink、special entry、or hard-link ambiguity blocks before mutation.

### I392-RQ-010 — Candidate

Candidate source is code-fixed to four provider roots and two installed skill slots. Candidate digest is deterministic over version、logical path、kind、mode、size/content digest. Seeds、record、and generated slot markers are excluded. Source/stage digests must match; symlink、special file、hard link、path traversal、absolute path、case-fold/NFC collision blocks.

### I392-RQ-011 — Fresh shared-container bootstrap

Fresh state requires record/roots/slots absent and `spec-dock` absent or a real directory. If absent, stage and all preflight checks finish first; then exclusive `mkdirat`、nofollow open、visible/held identity comparison、parent fsync、and owner-marker identity update occur before incomplete record publication. Before-record failure may remove only the exact created empty identity. Cleanup failure/foreign child/identity drift yields a same-tuple resumable partial failure. Existing container and uninstall never delete the container.

### I392-RQ-012 — Classification

Observed states are exactly `absent,legacy-0.2.3,incomplete,ready,tooling-absent-preserved-data,blocked`. Record、container、binding、slot markers、candidate/stage、legacy recovery evidence are evaluated read-only in the design order. JSON-like invalid record never falls back to legacy.

### I392-RQ-013 — Install and update

All candidate validation and staging precede target mutation. Operation order is incomplete record、docs、templates、system、scripts、spec-dock slot、grill slot、policy-authorized seeds、target verification、terminal record、stage cleanup. Update repairs missing owned targets and whole-root replaces modified owned roots. Protected data and seeds remain unchanged under preserve-only.

### I392-RQ-014 — Atomic filesystem publication

Repository and parents are descriptor-bound under a repository lock. Existing root/slot replacement uses Linux `renameat2(RENAME_EXCHANGE)` or macOS `renameatx_np(RENAME_SWAP)`; absent publication and detach use native no-replace. Missing primitive、EXDEV、identity drift、or unsafe type fails closed without generic fallback.

### I392-RQ-015 — Tooling-only uninstall

Uninstall is dry-run by default and `--apply` confirms mutation. It detaches only verified four roots and two slots; preserves shared container、record parent、user history、unknown paths、seeds、unrelated skills; and finishes with a durable `tooling-absent-preserved-data` record using preserve-only. `--keep-specs` is the default compatibility alias.

### I392-RQ-016 — External convergence

Partial failure resumes only the exact request/record/stage tuple. Matching targets are no-op and remaining owned targets converge forward. Cross-operation、cross-candidate、cross-policy、invalid stage、or bootstrap identity mismatch blocks. No automatic rollback、persistent progress list、or old-engine fallback is implemented.

### I392-RQ-017 — Exact `0.2.3` migration

Only the post-#387 exact clean `0.2.3` cohort is one-shot migrated. Four roots must exactly match; each slot is absent or exact; active legacy recovery、unsupported version、modified root、or foreign markerless slot blocks. Migration durable operation is preserve-only install; legacy public code identifies the entry path. Seeds and protected data remain unchanged.

### I392-RQ-018 — Old-package mutation-zero

Final ready/tooling-absent workspaces are exercised with the exact old `0.2.3` package for init-force、update、tooling uninstall、and removed purge. Startup composite tripwire intercepts target-scoped Python filesystem mutations and native `renameat2`/`renameatx_np` before call. Each old command has event count 0 and unchanged target digest; Python/native positive controls must each be intercepted before mutation.

### I392-RQ-019 — Public CLI and purge removal

Preserve command grammar for `init`、`update`、and `uninstall`. `init --force` is the state-based alias; apply without specs mode is tooling-only; keep is default alias. `--remove-specs` is handled before target observation and always returns status `error`、code `spec-history-purge-removed`、mutation false、exit 2. Purge service、intent、journal/recovery、and history-deletion tests are removed.

### I392-RQ-020 — Closed public wire

Every result uses the normative wire Artifact. All 36 public codes and 116 context rows fix status、mode、apply、operation、candidate-digest source/nullability、seed-policy source/nullability、mutation、bootstrap rollback、phase、last completed phase、retry、action set、exit、message、guidance、warnings/errors and array order. Unknown or implementation-defined values are invalid. CLI/service mappings and exact JSON/text goldens are table-driven.

### I392-RQ-021 — S40/S50 dogfood preservation

Current dogfood is exact legacy evidence: record bytes `0.2.3\n` and markerless fixed slots. S40 may update provider source、root README lifecycle text、provider lifecycle docs and tests, but must not edit/sync any dogfood root、either fixed slot、record、or marker. S50 uses external synthetic consumers and must also leave checked-in dogfood byte-identical. Any dogfood drift before S60 blocks PR-B.

### I392-RQ-022 — S60 complete migration and lifecycle docs

S60 is the sole PR-B merge gate. It performs the one complete migration of checked-in dogfood: all four roots、two slots、seven-key ready record、two markers and candidate digest are committed together. It updates root README lifecycle sections、provider and dogfood lifecycle docs、and root AGENTS lifecycle/uninstall sections to tooling-only uninstall、removed purge exit2、and exact retry contract. It preserves AGENTS test-policy/provider-gate sections until S70. Partial projection or modified legacy is not mergeable.

### I392-RQ-023 — Conditional terminalization and transitional gates

S60 applies the admitted register mechanically, obtains active/approved failure count 0, removes old lifecycle engine/tests after successor proof, retargets current `provider-ci.yml` from deleted tests to existing successors without final redesign, and keeps the current main-push verifier and its remaining consumers coherent. Current PR workflow and main-push workflow must independently pass. S60 never depends on S70-only tooling.

### I392-RQ-024 — Consumer-first PR-C cutover

S70 adds replacement provider gate、environment、workflow、tests、final test-policy docs and AGENTS sections before deleting old consumers/providers. It retires/replaces every policy consumer including `test_provider_test_lanes.py` and `test_full_regression_baseline.py`, proves consumer zero, then removes conftest policy、ledger、timing、quality modules、markers and old workflow in the same non-main branch. S80 alone is the PR-C merge gate.

### I392-RQ-025 — Sole frozen-head packaging producer

After tracked head freeze, only Linux job `provider-build-artifacts` may package. It invokes packaging once and uploads one candidate plus producer receipt. Linux canonical、sdist smoke、and macOS delta download identical bytes and have build count 0. Local S70 build is pre-freeze tool validation only; S80 never builds locally.

### I392-RQ-026 — Self-contained provider evidence

`provider-evidence-${SOURCE_SHA}` contains exactly nine UTF-8 files in the design order: aggregate JSON、four normalized receipts、and four role-specific evidence JSON bytes. Receipt and aggregate hashes bind the actual downloaded evidence bytes、metrics、run/job/artifact metadata、source/tree、candidate hashes and build counts. The evidence artifact is independently linked to Actions artifact metadata; no filename-only claim is accepted.

### I392-RQ-027 — Downloaded-artifact verifier

The exact `verify-downloaded-artifact` CLI consumes candidate directory、nine-file evidence directory、run/jobs/artifacts API JSON and expected source/run identity. It verifies actual entries and bytes、schemas/order、hashes/sizes、role/job/needs、artifact IDs/names/digests、one producer/zero consumers、and aggregate links. Exact success text/JSON and typed failures exits 2–12 are fixed in Design; no generic failure code.

### I392-RQ-028 — Stable Linux qualification

Environment ID is `specdock-linux-qualification-v1`; tracked descriptor pins base digest、runner label、x86_64、2 CPU、8 GiB、Python/uv/lock. Role evidence contains descriptor hash、image ID、runner/kernel/cgroup/fingerprint. All 20 runs are one environment or exact-fingerprint-equal; mismatch invalidates the series. First five each <=600s and CPU/wall <=1.1; all twenty failure/flake/retry 0; fault detection 100%.

### I392-RQ-029 — Required context transition

Old required contexts remain while new provider gate is added and read back as required. A dedicated non-merge canary then makes the new required gate RED and proves blocking. Canary closes, implementation PR returns GREEN, and only then is old provider-only context removed. Unrelated contexts and human review requirements remain unchanged; unreadable settings cause zero setting mutation.

### I392-RQ-030 — Tracked and external evidence

Tracked #392 report contains pre-freeze method and implementation facts only, not own hash、final head/artifact hashes、merge or close facts. After freeze, final CI evidence and required-context snapshots are placed in content-addressed external attestations. Human merge is verified by PR-head tree OID equals merge-commit tree OID. SpecDock finish、Issue/Epic close remain external; no tracked writeback cycle.

### I392-RQ-031 — S70 second dogfood update and S80 read-only

After all S70 candidate-byte changes, S70 performs one complete candidate-wide update and commits four roots、two slots、record、markers and new digest. Protected witnesses and seeds remain identical. S80 owns no tracked path and runs no build、update or sync; it performs read-only checks and downloaded CI verification only.

### I392-RQ-032 — Root operator guidance split

S60 owns only root AGENTS lifecycle/uninstall semantics: removed purge is mutation-zero exit2, uninstall is tooling-only, and partial failures use exact retry. S70 owns final pytest/provider-gate sections, replacing retired full-regression/ledger/shard/main-push guidance while preserving provider-first/dogfood and human-only merge.

### I392-RQ-033 — Main merge gates and closure

Only S30、S60、S80 are main merge gates. PR-A main remains old public product plus dormant successor; PR-B main is complete final lifecycle with current gates coherent; PR-C main is final build-once gate. S40、S50、S70 may not be merged independently. Human alone merges. #392 remains open until external post-merge tree equality and closure evidence; then Epic #384 may close.

## 3. Acceptance summary

Acceptance requires all requirements above on the same applicable source/tree identities, zero owner decisions, zero policy skips/approved failures in final state, no repository `.workbench` mutation, exact wire/register parsability, complete S60/S70 dogfood state, one frozen-head producer, nine-file evidence verification, no-gap required-context transition, and human merge tree equality.
