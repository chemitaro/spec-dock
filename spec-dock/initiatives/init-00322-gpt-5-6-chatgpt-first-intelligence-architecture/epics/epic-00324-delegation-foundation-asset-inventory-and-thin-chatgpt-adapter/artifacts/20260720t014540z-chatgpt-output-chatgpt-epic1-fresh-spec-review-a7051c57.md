review_status: fail

# Fresh SpecDock Epic Planning Bundle Review

## 1. Reviewed binding

| Field                          | Reviewed value                                      |
| ------------------------------ | --------------------------------------------------- |
| Repository                     | `chemitaro/spec-dock`                               |
| Branch                         | `codex/init-00322-chatgpt56-planning-pack-adoption` |
| Commit                         | `a7051c57810bd24f5898391b733da4d997743e1a`          |
| Epic                           | `epic-00324`                                        |
| GitHub Issue                   | `#324`                                              |
| Parent Initiative              | `init-00322`                                        |
| Parent GitHub Issue            | `#322`                                              |
| Evidence mode                  | `github-synced`                                     |
| GitHub exact revision verified | **Yes**                                             |

The GitHub branch reference resolves to commit `a7051c57810bd24f5898391b733da4d997743e1a`; the branch and requested commit compare as identical, with no commits ahead or behind. The commit is the pushed Epic Planning Bundle adoption revision.

GitHub Issue `#324` resolves to the expected Epic title, and the committed Epic metadata binds `epic-00324` to parent `init-00322` and repository issue `#324`.   Parent Issue `#322` also resolves to the expected Initiative.

## 2. Executive verdict

**Fail for Planning promotion.**

There are no P0 authority or safety violations. The requirement is independently acceptable and keeps Epic 1 within its intended foundation boundary. The per-Issue branch, PR, review, Human-merge, and dependent-start topology correctly implements the Human decision.

Promotion is blocked by two P1 defects:

1. The Human Relay design does not carry or reference the complete request that must be reproduced, despite the requirement that the relay preserve the same task and request contract.
2. The advertised `E1-I03` / `E1-I05` parallel lane does not give `E1-I05` an independently satisfiable acceptance boundary: `E1-I05` owns a changeability criterion that exercises backend configuration owned by later, non-merged `E1-I04`.

The first is a design completeness defect. The second is a plan dependency and independent-delivery defect. Consequently, the design and plan gates fail even though the overall scope, authority model, and proposed per-Issue delivery model are otherwise strong.

## 3. Finding counts

| Severity | Count |
| -------- | ----: |
| P0       |     0 |
| P1       |     2 |
| P2       |     4 |
| P3       |     1 |

## 4. Findings

| ID         | Severity | File / section                                                    | Evidence                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | Impact                                                                                                                                                                                                                                                                                                                                      | Required fix                                                                                                                                                                                                                                                                                                                                                                                                   |
| ---------- | -------- | ----------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| E1-REV-001 | **P1**   | `design.md` §13 Human Relay; `requirement.md` SC-R02 and E-AC-006 | The requirement says the relay package includes the **request body**, binding, anchor digest, constraints, output contract, and external-file digests, and requires the relay and backend routes to preserve the same task and contract.   The design’s relay schema contains `request_digest`, `task_kind`, binding, anchors, context/file digests and an output-contract reference, but contains neither the request text nor a content-addressed request-package reference.  The backend port separately recognizes “request text or request package reference,” demonstrating that this is a modeled input which was omitted from the relay contract. | A Human receiving only the specified relay package cannot deterministically reconstruct the semantic request whose digest is recorded. The Human Relay therefore cannot prove same-request equivalence or satisfy E-RQ-007/E-AC-006. This blocks a core REQ-005 recovery capability.                                                        | Add either the complete immutable request body or a content-addressed, durable request-package reference to `RelayPackage`. Include safe logical references for Operator Context and external files, not just their digests. Require the returned output or re-entry record to echo the request digest, and require Main to verify equality before adoption.                                                   |
| E1-REV-002 | **P1**   | `plan.md` §4, §6, §7; `requirement.md` E-AC-011                   | `E1-I05` owns E-AC-010 and E-AC-011 and depends only on `E1-I01` and `E1-I02`, allowing it to run in parallel with `E1-I03`.  E-AC-011 requires a rehearsal covering changes to Prompt resources, backend command/model configuration, and output fields.  The actual backend port, configuration precedence, failure mapping, and relay integration are owned by `E1-I04`, which starts only after `E1-I03`.  The DAG nevertheless places `E1-I05` before `E1-I04` and advertises `E1-I03` and `E1-I05` as parallel.                                                                                                                                     | Under the mandated per-Issue PR topology, `E1-I05` cannot independently prove its owned E-AC-011 against the actual backend configuration surface without either implementing `E1-I04` scope, depending on unmerged work, or deferring part of its owned acceptance criterion. Therefore the stated parallel lane is not demonstrably safe. | Choose one coherent model: **(a)** narrow `E1-I05` to measurement-schema and fixture-only feasibility, make actual backend/config changeability supporting evidence owned by `E1-I04` and verified by `E1-QA`; or **(b)** add `E1-I04` as an `E1-I05` dependency and remove the `E1-I03`/`E1-I05` parallel claim. Update the candidate table, DAG, lane table, closure matrices, and checkpoints consistently. |
| E1-REV-003 | **P2**   | `requirement.md` §9.4; `design.md` §8.3 and §10.2                 | The requirement permits an explicit external file that is Git-untracked **or** repository-external.  The command design similarly advertises `--context-file` and `--file` for external-or-untracked files.  Strict preflight, however, requires the entire working tree, index, and untracked state to be clean.                                                                                                                                                                                                                                                                                                                                         | An explicitly selected, safe but non-ignored untracked file appears both allowed and preflight-blocking. Implementations could diverge on whether the selected file is exempted from cleanliness checks.                                                                                                                                    | Define one rule explicitly: either permit only repository-external or ignored Workbench files, or calculate cleanliness after excluding the exact set of validated explicit input files. Add positive and negative tests for ignored, non-ignored untracked, tracked, symlinked, secret-like, and repository-external inputs.                                                                                  |
| E1-REV-004 | **P2**   | `plan.md` §4, §19, §20; `E1-QA` ownership terminology             | The candidate table says `E1-QA` owns **all E-RQ and all E-AC**.  The detailed matrices instead assign primary E-RQ and verification responsibility to implementation Issues, while `E1-QA` provides integration verification.  Its allowed scope is bounded repair, fixture/docs correction, and evidence summary—not catch-all implementation.                                                                                                                                                                                                                                                                                                          | “Owned: all” can be read as transferring incomplete implementation responsibilities to the final-quality Issue, contrary to the stated no-aggregate/no-scope-expansion boundary.                                                                                                                                                            | Replace `Owned E-RQ/E-AC: all` with `Integration verification coverage: all` or equivalent. Preserve the implementation Issues as primary owners and describe `E1-QA` as final verification plus bounded repair only.                                                                                                                                                                                          |
| E1-REV-005 | **P2**   | `plan.md` §7.1 and §8 checkpoints                                 | The global lifecycle correctly requires dependency PR merge and merged-SHA verification before branch creation.  The G1–G4 checkpoint tables, however, use evidence completion to “unblock” later candidates without restating that the owner Issue’s PR must be Human-merged and its SHA observed in updated `main`.                                                                                                                                                                                                                                                                                                                                     | A workflow implementation using the checkpoint tables as its operational source could start a dependent Issue after evidence handoff but before merge, violating the Human decision.                                                                                                                                                        | Add an invariant to every checkpoint transition: “unblocks only after every owning Issue PR is Human-merged and each merged SHA is verified in updated `main`.” Treat handoff readiness and branch-start readiness as separate states.                                                                                                                                                                         |
| E1-REV-006 | **P2**   | `design.md` §20.4 PlantUML                                        | The per-Issue delivery diagram says `Main -> Branch : implement and verify one Issue`.  The accepted actor contract assigns implementation and verification to Executor, while Main inspects the diff and verification before committing and pushing.                                                                                                                                                                                                                                                                                                                                                                                                     | The diagram is structurally inconsistent with the prose and could normalize Main-owned implementation, weakening the delegation boundary.                                                                                                                                                                                                   | Add an Executor participant and show Main delegating implementation/verification to it, followed by Main’s diff/verification inspection and explicit Git transition. Alternatively relabel the current arrow as “orchestrate Executor for one Issue,” but an explicit participant is preferable.                                                                                                               |
| E1-REV-007 | **P3**   | `report.md` progress bookkeeping                                  | The report says committing and pushing the review target remain unfinished.  The reviewed GitHub branch now resolves to the exact pushed commit.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | The report is one transition behind the actual review state. This does not affect the canonical contract but reduces gate-bookkeeping precision.                                                                                                                                                                                            | When recording this review disposition, replace the pending commit/push action with the exact reviewed SHA and review verdict. Leave execution readiness and Issue materialization pending as appropriate.                                                                                                                                                                                                     |

## 5. Separate gate verdicts

### Requirement gate: **pass**

The requirement is independently acceptable.

It limits Epic 1 to inventory, a separate thin adapter, exact target/revision binding, deterministic anchors, backend invocation, Human Relay, compatibility, and metrics feasibility. It expressly excludes final Planning, Review, Execution Brief, Repair, Issue Execution, Delivery, cutover, and semantic-state responsibilities.

This agrees with the Initiative guardrail for Epic 1: inventory, thin adapter, exact HEAD, command skeleton, deterministic anchors, and baseline, without implementing Brief semantics or legacy removal.

The E-RQ statements are outcome-oriented and observable, and the E-AC statements generally specify preconditions, operations, expected results, and evidence.   Actor authority and no-hidden-Git requirements are consistent with the parent Initiative.

E1-REV-003 is a cross-document clarification, not a blocking defect in the requirement’s intended security boundary.

### Design gate: **fail**

The design fits the current repository architecture:

* provider authority under `src/spec_dock/assets/spec_dock/`;
* installed agent-tooling authority under `src/spec_dock/assets/install_root/`;
* dogfood as a generated consumer projection;
* layered `cli` / `commands` / `application` / `domain` / `infra` / `presentation` organization.

Its exact binding, preflight, anchor, evidence-only result, security, idempotency, observability, compatibility, migration, and rollback sections are otherwise substantial and testable.    Existing backend configuration precedence and direct process invocation are supported by current provider code rather than unsupported repository assumptions.

The gate fails because E1-REV-001 leaves the Human Relay request contract incomplete. E1-REV-003 and E1-REV-006 are additional non-blocking design defects.

### Plan gate: **fail**

The six implementation slices plus one final-quality slice are generally coherent and close to minimal:

* inventory;
* command/application boundary;
* binding/anchors/preflight;
* backend/Human Relay;
* metrics/changeability;
* distribution/compatibility;
* final integration and quality.

The plan gives every candidate a purpose, allowed local delta, forbidden parent changes, required evidence, handoff, verification responsibility, and a per-Issue PR lifecycle.

The gate fails because E1-REV-002 means the advertised parallel lane and its independent Issue exit boundaries are not presently coherent. E1-REV-004 and E1-REV-005 should also be corrected to prevent QA ownership expansion and premature dependency unblocking.

## 6. Per-Issue branch / PR / merge topology verdict

**Topology verdict: acceptable and consistent with the Human decision.**

The bundle clearly requires:

* one dedicated branch and one PR per actual Issue;
* branch creation only after prerequisite PRs are Human-merged and their SHAs are present in updated `main`;
* no use of an unmerged Issue branch as another Issue’s base;
* required checks and review before Human merge;
* stale-base update plus affected-check and review-freshness reconfirmation;
* an independent `E1-QA` branch and PR based only on merged implementation results;
* Epic completion only after all Issue PRs are merged and merged/reviewed heads are verified.

`E1-QA` is conceptually a true final integration/quality unit, not an Epic-level aggregate delivery PR. Its allowed mutation is limited to accepted blockers, test/docs corrections, and evidence, and it starts from a `main` that already contains every implementation PR.

This topology itself does not need redesign. E1-REV-004 and E1-REV-005 require terminology and transition hardening so that the implementation cannot accidentally deviate from it.

## 7. Issue dependencies and parallelism verdict

### Dependency DAG

Apart from `E1-I05`, the dependency chain is coherent:

```text
E1-I01 → E1-I02 → E1-I03 → E1-I04
                      └─────────────┐
E1-I01 + E1-I02 → E1-I05           │
E1-I03 + E1-I04 + E1-I05 → E1-I06 ┘
E1-I01…E1-I06 → E1-QA
```

The sequencing appropriately establishes inventory before the command boundary, the command boundary before revision binding, revision binding before backend invocation, and all implementation capabilities before distribution and final quality.

### Parallel lane

**Parallelism verdict: not safe as currently specified.**

`E1-I03` and a metrics-schema-only `E1-I05` could safely run in parallel after `E1-I02`. The current `E1-I05`, however, also owns a changeability rehearsal that covers backend configuration, while the relevant backend surface is owned by `E1-I04`. Until E1-REV-002 is resolved, the plan cannot guarantee that `E1-I05` starts from dependency-ready `main`, stays within its own scope, and exits through an independently reviewable PR.

The safest minimal correction is to preserve the parallel lane but narrow `E1-I05` to the static measurement contract, fixture protocol, historical baseline, and measurable change procedure. Actual backend-command/model change evidence should then be supplied by `E1-I04` and integrated by `E1-QA`.

## 8. Traceability and acceptance coverage

### Requirement → design → plan

Coverage is broad and explicit:

* all E-RQ-001 through E-RQ-012 appear in the requirement;
* all E-AC-001 through E-AC-013 appear in the requirement;
* every design slice identifies the E-RQ/E-AC it closes and its owning candidate;
* the plan assigns primary and supporting candidate responsibilities;
* plan closure matrices cover every E-RQ and E-AC.

The principal coverage defects are semantic rather than missing rows:

* E-AC-011 is assigned to an Issue whose declared dependencies do not provide the real surface it is supposed to exercise.
* `E1-QA` is described as owning all requirements and acceptance criteria in one table, while the detailed closure model correctly treats it as integration verification.

### Parent Initiative and ADR trace

The Epic correctly traces to parent REQ-001, REQ-004, REQ-005, REQ-018, and REQ-022, and to the parent acceptance responsibilities identified for Epic 1.

Its authority, exact-HEAD, no-tracked-attachment, Main/Executor Git ownership, minimal-state, and Plan-driven delivery decisions are aligned with the accepted ADRs.

No material Epic 2–7 semantic responsibility is silently pulled into Epic 1. Reserved command names and an `execution-brief generate` structural skeleton do not implement final Prompt semantics, concern selection, Brief statuses, adoption/freeze, review protocols, Repair Batch semantics, or delivery workflows.

### Repository-claim support

No blocking unsupported repository claim was found. The important claims are supported at the reviewed SHA:

* provider, installed, and dogfood authority layout;
* layered runtime organization;
* current ChatGPT authoring compatibility lane;
* backend command precedence;
* Python 3.10, pytest, Ruff, and mypy configuration;
* current authoring and Oracle-selector regression surfaces.

## 9. PlantUML structural assessment

Five PlantUML blocks were assessed against the prose:

| Diagram                          | Structural verdict                                                                   |
| -------------------------------- | ------------------------------------------------------------------------------------ |
| Thin adapter component boundary  | Consistent                                                                           |
| Layered package dependency       | Consistent                                                                           |
| Backend / Human Relay recovery   | Consistent apart from the missing request-carriage contract identified in E1-REV-001 |
| Per-Issue branch and PR delivery | **Inconsistent actor label**, E1-REV-006                                             |
| Issue candidate dependency DAG   | Consistent with the textual DAG                                                      |

The user-provided PlantUML 1.2026.6 syntax-pass evidence was accepted as supplied evidence; syntax rendering was not independently rerun during this read-only connector review.

## 10. Residual risks and JIT details

The following can remain for Issue-level planning after the P1 defects are repaired:

* exact module, class, and helper names;
* numeric exit-code allocation;
* bounded timeout values and operator-approved retry limits;
* backend command tokenization and platform-specific executable behavior;
* concrete session/output discovery for uncertain backend completion;
* relay and baseline artifact filenames;
* actual historical baseline samples and privacy classification;
* exact changed-file and test-set accounting for M-008;
* branch-update mechanism and the definition of “affected” checks/reviews;
* rollback rehearsal mechanics for merge, squash, or rebase-shaped Git history;
* actual Issue IDs, GitHub Issue numbers, PR numbers, and final delivery SHAs.

These details must not change the exact binding, no-hidden-Git, evidence-only, per-Issue merge, Human Gate, or semantic-scope boundaries.

## 11. Assumptions, uncertainties, and unverified claims

* GitHub repository, branch, commit, Epic metadata, and Issue identities were independently verified through the GitHub connector.
* CI, unit tests, integration tests, live ChatGPT connector smoke, Human Relay smoke, rollback rehearsal, and metric collection have not yet been executed; they remain future implementation evidence.
* PlantUML syntax success is based on the evidence stated in the review request rather than an independent render in this review.
* The report is treated only as evidence and gate bookkeeping, not as authority for requirement, design, or plan correctness.
* Supplementary attachments were not used as a substitute for the GitHub-tracked revision. The repository-excerpt bundle was used only for secondary cross-checking after GitHub verification; the separate design-judgment note was not used to establish any finding.  

## 12. Final promotion recommendation

**Do not promote this Epic Planning Bundle and do not materialize the proposed actual Issue nodes yet.**

Required sequence:

1. Repair E1-REV-001 by making the Human Relay request package complete and reproducible.
2. Repair E1-REV-002 by narrowing `E1-I05` or correcting its dependency and the parallel-lane declaration.
3. Reconcile the affected requirement/design/plan tables, DAG, checkpoints, closure matrices, and diagrams.
4. Preferably resolve E1-REV-003 through E1-REV-006 in the same complete revision so that delivery semantics have one unambiguous reading.
5. Push the revised complete Epic Planning Bundle.
6. Run a new fresh review bound to the new exact GitHub commit.
7. Request the separate Human approval for candidate Issue materialization only after the fresh review has P0=0 and P1=0.

**Final recommendation: Planning promotion rejected for commit `a7051c57810bd24f5898391b733da4d997743e1a`; revise and re-review.**
