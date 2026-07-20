review_status: pass

# Fresh Re-Review — SpecDock Epic 1 Planning Bundle

## 1. Exact revision verification

GitHub connector access succeeded. Attachments were not used as a substitute for repository access.

| Field                               | Verified value                                                                                                               |
| ----------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| Repository                          | `chemitaro/spec-dock`                                                                                                        |
| Default branch                      | `main`                                                                                                                       |
| Requested branch                    | `codex/init-00322-chatgpt56-planning-pack-adoption`                                                                          |
| Requested commit                    | `caad34bc9590e1a25d321e7b850c4583a35eee2c`                                                                                   |
| Branch/commit comparison            | `identical`; ahead `0`, behind `0`                                                                                           |
| Relationship to prior review target | Current commit is exactly one commit ahead of `a7051c57810bd24f5898391b733da4d997743e1a`, with that commit as the merge base |
| Epic                                | `epic-00324` / GitHub Issue `#324`                                                                                           |
| Parent                              | `init-00322` / GitHub Issue `#322`                                                                                           |
| Evidence mode                       | `github-synced`                                                                                                              |
| Verification date                   | July 20, 2026, JST                                                                                                           |

The requested commit exists with the repair commit message for Human Relay reproducibility, the `E1-I03`/`E1-I05` dependency correction, and the per-Issue merge gate.  GitHub Issue #324 and parent Issue #322 resolve to the expected Epic and Initiative titles.   The committed Epic metadata independently binds `epic-00324` to `init-00322`, Issue #324, and `chemitaro/spec-dock`.

The full canonical files were read from the exact commit:

| File                            | Git blob SHA                               |
| ------------------------------- | ------------------------------------------ |
| `requirement.md`                | `7e98c126392d783296f339fc4d15378afe3a6231` |
| `design.md`                     | `4472c7ed1e3bc0f9943ce3309c82016d066e27d3` |
| `plan.md`                       | `3dc453d235b6a22da5f8a60574483388a2220bf1` |
| `report.md`                     | `f5e68530b366877ae867f4987b9b1533d39859f4` |
| Preserved prior review artifact | `21df6f89300c16d8d07778ad4bb789b4d386ad65` |

These identities are returned with the exact-commit file contents.

## 2. Executive verdict

**Pass for Planning promotion and separate Human Issue-slice approval.**

The repaired bundle is internally coherent, remains within the parent Epic 1 boundary, fits the repository architecture, preserves the Human-approved per-Issue delivery topology, and has no unresolved blocking specification defects.

| Severity | Count |
| -------- | ----: |
| P0       |     0 |
| P1       |     0 |
| P2       |     0 |
| P3       |     0 |

All seven prior findings are resolved without regression. No new severity finding was identified in the full Requirement, Design, or Plan review.

This pass does **not** itself:

* grant canonical authority independently of Human adoption;
* approve materialization of the proposed actual Issue nodes;
* establish execution readiness;
* establish PR readiness or Epic completion.

The bundle itself explicitly preserves those boundaries.

## 3. Prior-finding disposition

| Finding        | Prior severity | Disposition  | Current evidence and regression assessment                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| -------------- | -------------: | ------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **E1-REV-001** |             P1 | **Resolved** | `RelayPackage` now contains `request_body` or `request_package_reference`, a SHA-256 package digest, safe logical context/file references with corresponding digests, an echoed `request_digest`, and a Main-side equality check that blocks adoption on mismatch. The re-entry boundary repeats the reconstructed-request and digest checks. No fallback to tracked attachments or automatic canonical adoption was introduced.                                                         |
| **E1-REV-002** |             P1 | **Resolved** | `E1-I05` is narrowed to metrics feasibility, baseline, and the M-008 measurement protocol/fixture. `E1-I04` supplies actual backend/config evidence and depends on both merged `E1-I03` and `E1-I05`. The candidate table, textual DAG, PlantUML DAG, parallel-lane table, and E-AC-011 closure row agree.                                                                                                                                                                               |
| **E1-REV-003** |             P2 | **Resolved** | The accepted rule is now unambiguous: file inputs must be repository-external or Git-ignored Workbench files. Tracked files and repository-internal non-ignored untracked files are rejected; no clean-preflight exclusion set is created. Positive and negative tests cover repository-external, ignored Workbench, tracked, non-ignored untracked, symlinked, and secret-like inputs.     The repository’s managed `spec-dock/.gitignore` explicitly ignores `.workbench/`.            |
| **E1-REV-004** |             P2 | **Resolved** | `E1-QA` now has “primary ownershipなし” for both E-RQ and E-AC, with full integration-verification coverage only. Its permitted mutation is accepted-blocker bounded repair, test/fixture/docs correction, and evidence summary; it may not absorb unfinished implementation or new scope.                                                                                                                                                                                                 |
| **E1-REV-005** |             P2 | **Resolved** | A global checkpoint transition invariant separates evidence/handoff readiness from branch-start readiness. Every `Unblocks` entry is expressly conditioned on all owning dependency PRs being Human-merged and their merged SHAs being observed in updated `main`. The Issue lifecycle independently repeats the same merge-and-observe rule.                                                                                                                                            |
| **E1-REV-006** |             P2 | **Resolved** | The per-Issue PlantUML now includes an explicit Executor. Main creates the branch and delegates; Executor implements and verifies; Main inspects the diff/evidence and performs the explicit commit/PR transition; Human merges; Main verifies the merged SHA. This matches the actor prose and parent authority model.                                                                                                                                                                  |
| **E1-REV-007** |             P3 | **Resolved** | The report records the exact pushed prior target `a7051c…`, its fail verdict and counts, the preserved review artifact and receipt, the adopted repair disposition, and the state `repair integrated → fresh re-review pending`. The prior target is no longer described as awaiting its initial push.    The current review is the re-review transition that report state was awaiting; its result must be integrated afterward by Main rather than anticipated by the reviewed commit. |

## 4. New findings

**None.**

No new P0, P1, P2, or P3 specification finding was identified.

The implementation-specific matters listed under **Residual JIT details** are intentionally delegated mechanics. They do not currently create an ambiguity in authority, scope, acceptance, dependency ordering, or delivery topology.

## 5. Separate gate verdicts

### Requirement gate: **pass**

The Requirement is independently acceptable.

It gives Epic 1 a narrow and defensible capability envelope:

* maintained asset inventory;
* a separate thin `spec-dock-chatgpt` boundary;
* exact target/branch/HEAD binding;
* deterministic anchors without semantic Artifact selection;
* operator-owned backend invocation;
* Human Relay;
* compatibility;
* baseline and telemetry feasibility.

It expressly excludes final Planning, Review, Execution Brief, Repair Batch, Issue Execution, PR Delivery, cutover, semantic state databases, automatic adoption, and automatic Node creation.  That boundary agrees with the parent Initiative’s Epic 1 guardrail and portfolio assignment.

The actor and evidence-authority rules are consistent: ChatGPT and the adapter produce evidence; Main owns adoption and explicit Git transitions; Runtime stays deterministic; Human retains decomposition and merge authority.

All E-RQ-001 through E-RQ-012 are observable. All E-AC-001 through E-AC-013 specify an operational precondition, action, expected outcome, and evidence surface. The corrected acceptance set covers exact binding, no-hidden-Git, file policy, Human Relay, compatibility, metrics, changeability, live smoke, rollback, and per-Issue PR delivery.

### Design gate: **pass**

The Design is independently acceptable.

Its placement follows the repository’s documented authority and layered architecture:

* provider source under `src/spec_dock/assets/spec_dock/`;
* agent-tooling authority under `src/spec_dock/assets/install_root/`;
* dogfood as a generated consumer projection;
* `cli`, `commands`, `application`, `domain`, `infra`, and `presentation` layers;
* filesystem/Git/backend concerns in infrastructure rather than a monolithic command implementation.

The proposed sibling repo-local package preserves dependency direction: `spec_dock_chatgpt` may reuse narrow deterministic Runtime reads, while Runtime may not depend on the ChatGPT adapter or Oracle/backend code.

The design adequately covers:

* exact ID/path resolution and parent/dependency traversal;
* clean named-branch and local/remote equality preflight;
* fail-closed classifications;
* explicit, logged fetch as the sole allowed Git observation side effect;
* deterministic binding and anchor digests;
* no semantic Artifact selection;
* direct-argv backend invocation;
* non-idempotent invocation handling and duplicate prevention;
* complete Human Relay request reconstruction;
* typed failure states;
* redaction and secret handling;
* structural observability;
* additive compatibility and rollback-by-revert;
* hermetic, CLI, installer, integration, and regression testing.

All five PlantUML blocks are structurally consistent with their surrounding prose:

| Diagram                             | Verdict                                                |
| ----------------------------------- | ------------------------------------------------------ |
| Thin adapter component boundary     | Consistent                                             |
| Layered package dependency          | Consistent                                             |
| Normal backend/Human Relay recovery | Consistent                                             |
| Per-Issue branch and PR delivery    | Consistent; Executor/Main ownership repair present     |
| Issue-candidate dependency DAG      | Consistent with textual DAG and candidate dependencies |

The supplied PlantUML 1.2026.6 syntax-pass evidence was accepted. Syntax rendering was not independently rerun in this read-only connector review.

### Plan gate: **pass**

The Plan is independently acceptable.

The six implementation slices and one final-quality slice are appropriately separated by risk and ownership:

1. inventory and authority map;
2. executable/application boundary;
3. exact binding, anchors, preflight, file policy, and Git safety;
4. backend, relay, redaction, and workflow documentation;
5. metrics/baseline and changeability protocol;
6. distribution and compatibility;
7. merged-state final integration and bounded QA repair.

Each slice has owned requirements, acceptance responsibility, dependencies, allowed local delta, prohibited scope changes, evidence, and handoff.

The repaired dependency model is coherent, closure matrices cover every E-RQ and E-AC, and E-AC-011 now has an explicit split between `E1-I05` protocol/fixture evidence, `E1-I04` actual backend/config evidence, and `E1-QA` integrated rehearsal.

The completion contract correctly requires all implementation PRs and the independent E1-QA PR to be Human-merged, merged/reviewed heads to be verified, and only then Epic completion to be recorded.

## 6. Per-Issue PR topology verdict

**Verdict: pass — fully consistent with the mandatory Human-approved topology.**

| Mandatory condition                                                      | Verdict   |
| ------------------------------------------------------------------------ | --------- |
| One dedicated branch per Issue                                           | Satisfied |
| One reviewed PR per Issue                                                | Satisfied |
| Dependency PRs Human-merged before downstream branch creation            | Satisfied |
| Merged SHAs observed in updated `main` before unblocking                 | Satisfied |
| Human performs every merge                                               | Satisfied |
| No unmerged Issue branch used as another Issue’s base                    | Satisfied |
| Parallel stale bases refreshed before merge                              | Satisfied |
| Affected checks and review freshness reconfirmed                         | Satisfied |
| E1-QA has its own branch and PR                                          | Satisfied |
| E1-QA starts from already-merged implementation work                     | Satisfied |
| No aggregate Epic PR                                                     | Satisfied |
| Actual Issue nodes remain unmaterialized pending separate Human approval | Satisfied |

The Requirement states the topology directly.  The Design models dependency-ready, branch-created, review-ready, merge-ready, merged, and downstream-unblocked as distinct states.  The Plan then operationalizes the lifecycle and forbids bundling multiple Issue differences into a single Epic PR.

Candidate keys remain explicitly non-materialized planning identifiers; no actual SpecDock or GitHub Issue IDs are invented.  Materialization is gated on a separate Human decision and must use Runtime commands rather than manual metadata edits.

## 7. Dependency and parallelism verdict

**Verdict: pass.**

The effective DAG is:

```text
E1-I01
  → E1-I02
      ├→ E1-I03 ─┐
      └→ E1-I05 ─┴→ E1-I04
E1-I03 + E1-I04 + E1-I05
  → E1-I06
E1-I01 … E1-I06
  → E1-QA
```

The only intended parallel interval is `E1-I03` and `E1-I05` after `E1-I02`.

That parallelism is now safe because:

* `E1-I03` owns target binding, anchors, preflight, attachments, and no-hidden-Git;
* `E1-I05` owns measurement schema, feasibility, historical baseline, and protocol/fixture evidence only;
* neither needs the other’s implementation surface to exit independently;
* `E1-I04` starts only after both PRs are Human-merged and receives the binding foundation plus measurement protocol;
* actual backend/config changeability evidence is produced by `E1-I04`;
* `E1-I06` waits for the integrated implementation contracts;
* `E1-QA` waits for all six merged implementation PRs.

The textual DAG, diagram, lane table, and explanatory paragraph agree.

## 8. Traceability and acceptance coverage

### Epic-level coverage

Coverage is complete:

* E-RQ-001 through E-RQ-012 are present in the Requirement.
* E-AC-001 through E-AC-013 are present in the Requirement.
* Every Design slice identifies the E-RQ/E-AC it closes and its candidate owner.
* Every E-RQ has a primary and supporting closure assignment.
* Every E-AC has named verification owners and required evidence.
* E1-QA integration coverage does not replace implementation ownership.

The closure matrices substantiate this coverage.

### Parent-Initiative trace

The Epic correctly implements or supports the parent responsibility set:

* REQ-001: actor and Human Gate separation;
* REQ-004: thin boundary and exact GitHub binding;
* REQ-005: GitHub SSOT, supplemental external context, and Human Relay;
* REQ-018: provider/installed/dogfood alignment;
* REQ-022: deterministic anchors without Codex semantic Artifact selection.

These parent boundaries and prohibitions are explicit.

No Epic 2–7 semantic responsibility is silently pulled into Epic 1. Reserved command groups and the `execution-brief generate` skeleton remain structural only; Prompt semantics, review protocols, Brief statuses, Artifact adoption/freeze, Repair semantics, Executor integration, delivery workflow, and legacy cutover remain assigned to later Epics.

## 9. Residual JIT details

The following details may be decided during Human-approved Issue planning without reopening the Epic bundle:

* concrete Python modules, classes, helper names, and parser/registry split;
* numeric exit-code allocation, while retaining `pass == 0` and every non-pass status as nonzero;
* the discriminated representation of inline request bodies versus immutable request-package references;
* canonical request serialization and digest-byte rules, while preserving SHA-256 and equality verification;
* immutable staging/final re-hash mechanics for context and external files to prevent content changes between validation and invocation;
* the exact bounded fetch refspec, tag policy, and diagnostic accounting for explicitly permitted fetch effects;
* backend-command tokenization, timeout values, bounded operator-approved retry, and session/output discovery;
* inventory scan granularity, schema-validation implementation, and projection comparison mechanism;
* exact historical baseline samples, privacy classifications, and unavailable-telemetry dispositions;
* stale-base refresh mechanism and the concrete definition of “affected” checks and reviews;
* rollback rehearsal mechanics for merge-, squash-, or rebase-shaped history;
* actual Issue IDs, GitHub Issue numbers, branch names, PR numbers, base SHAs, reviewed heads, and merged SHAs.

These details may not weaken exact binding, no-hidden-Git, evidence-only authority, external-file restrictions, per-Issue PR delivery, Human merge ownership, or the reviewed dependency DAG. The bundle already requires a fresh planning revision and Human approval if an Issue-local decision would change an Epic invariant.

## 10. Evidence limitations and unverified implementation claims

* This is a specification review. No implementation, unit suite, integration smoke, live backend/Human Relay run, rollback rehearsal, or metric collection has yet occurred.
* The report correctly leaves E-AC-001 through E-AC-013 unachieved because implementation has not begun.
* The prior review artifact exists in the exact GitHub revision and the report records its SHA-256, byte size, and preservation receipt. Those byte-level values were reviewed as committed evidence rather than independently recomputed from the attachment in this connector session.
* The uploaded repository bundle was used only as a supplementary cross-check after exact GitHub access succeeded, never as a replacement for the GitHub revision. 
* The separate uploaded design-judgment note was not used to establish this verdict.

## 11. Final promotion recommendation

**Promote the Planning Bundle at commit `caad34bc9590e1a25d321e7b850c4583a35eee2c` to the next Human gate.**

Recommended transition:

1. Main records this exact re-review disposition in `report.md`.
2. Human separately reviews and approves the proposed `E1-I01`–`E1-I06` plus `E1-QA` slicing, dependency DAG, and per-Issue PR topology.
3. Only after that approval may Main materialize actual Issue nodes and dependency edges through SpecDock Runtime.
4. Each materialized Issue then receives JIT Requirement/Design/Plan work from the then-current merged `main`.
5. No Issue implementation branch may begin before its dependency PRs are Human-merged and their SHAs are observed in updated `main`.

**Final recommendation: Planning promotion approved; actual Issue materialization and execution remain gated on the separate Human approval.**

No repository files were edited.
