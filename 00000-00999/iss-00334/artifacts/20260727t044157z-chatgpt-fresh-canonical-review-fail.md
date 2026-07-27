# Oracle Browser Transcript

Conversation: https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a66d9ef-0340-83e8-9c23-7c234aad1bb1

## Prompt

Required repository connector context:
- @GitHub chemitaro/spec-dock
- Current branch: iss-00334-implement-chatgpt-issue-planning-workflow
- Default branch: main
- MUST inspect this GitHub repository with the GitHub connector before answering.
- First inspect the current branch. If the current branch does not exist or cannot be opened, inspect the default branch instead.
- Hard failure condition: if the GitHub connector/app is unavailable, or if the repository, current branch, and default branch cannot be accessed, return immediately with exactly: repository access failed.
- Do not continue from attached files, prompt context, memory, or general knowledge when repository access fails.
- Attached files and prompt-provided context are supplementary only after repository access succeeds.

Use the attached prompt file as the complete formal review contract. Perform the required fresh read-only Red Team review using GitHub connector context and return only the formal review artifact.

## Answer

# iss-00334 — Fresh Read-Only Red Team Canonical Planning Review

```text
review_status: fail
S01_disposition: blocked
P0_findings: 0
P1_findings: 4
P2_findings: 0
P3_findings: 0
repository_mutation: 0
patch_or_replacement_produced: no
tests_executed_by_reviewer: no
```

## 1. Review identity

| Field                   | Inspected value                                       |
| ----------------------- | ----------------------------------------------------- |
| Repository              | `chemitaro/spec-dock`                                 |
| Branch                  | `iss-00334-implement-chatgpt-issue-planning-workflow` |
| Required source HEAD    | `a0e273ac94ae71207bc4ecc188028022b2acfdc4`            |
| Actual inspected HEAD   | `a0e273ac94ae71207bc4ecc188028022b2acfdc4`            |
| Branch comparison       | `identical`; ahead `0`, behind `0`                    |
| Default-branch fallback | Not used                                              |
| Access verification     | GitHub connector access succeeded                     |
| Issue                   | `iss-00334`                                           |
| Initiative              | `init-00322`                                          |
| Epic                    | `epic-00331`                                          |

The exact commit exists and records the correction for public-status and Closure-graph planning contracts.

Canonical Issue directory:

```text
spec-dock/initiatives/
  init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/
  epics/epic-00331-planning-and-advisory-review/
  issues/iss-00334-implement-chatgpt-issue-planning-workflow/
```

The formal review contract supplied in `prompt.md` was applied as written.

### Active-path resolution

The immutable remote snapshot does not contain tracked objects under `spec-dock/active/` or `spec-dock/.agent/`; both are generated and ignored surfaces.  The runtime resolves active-manifest entries to canonical repository-relative paths and generates the active views from that state.

Accordingly, the canonical paths identified by the Assurance source binding and active display paths were inspected directly. `.assurance.json` maps the three canonical owner documents to `spec-dock/active/issue/{requirement,design,plan}.md`.

## 2. Files and repository surfaces inspected

### Canonical planning set and required artifacts

| Path                                                                     | Git blob at inspected HEAD                 |
| ------------------------------------------------------------------------ | ------------------------------------------ |
| `requirement.md`                                                         | `c180d4e801d9293e307a4334b5056c5c2fd8fc5c` |
| `design.md`                                                              | `ad0807ae4e498bea805312228ce03feff749c3fd` |
| `plan.md`                                                                | `9cdab44ac6660ce45cc644562302c89f7fa03c54` |
| `report.md`                                                              | `80b9f3496f608a7a6291c2115229a45d21da02dc` |
| `.assurance.json`                                                        | `6b4afcd3525d721e0ee4a01def06d406ede7677b` |
| `artifacts/20260727t033431z-chatgpt-fresh-canonical-review-fail.md`      | `1014e060bb6772dffa3864bb43da8ca0e6db164b` |
| `artifacts/20260727t035110z-chatgpt-blue-bounded-correction-followup.md` | `c442dc91b68c3e7906c4fe4433891c41d17980a9` |

The current canonical blob identities are confirmed in the corresponding connector responses.

### Parent and shared workflow contracts

* Initiative `init-00322` Requirement and Plan.
* Epic `epic-00331` Requirement and Design.
* `spec-dock/docs/workflow_issue.md`.
* Current one-Issue/one-branch/one-PR, PR-delivery, Human-merge, and Issue-finish boundaries. The shared workflow distinguishes planning readiness from execution and delivery completion and keeps merge Human-owned.

### Provider runtime, implementation primitives, and tests

The following relevant surfaces were statically inspected:

```text
src/spec_dock/cli.py
src/spec_dock/assets/spec_dock/scripts/spec-dock
src/spec_dock/assets/spec_dock/scripts/spec-dock-chatgpt
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/runbook_store.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/active_store.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/zip_contract.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/authoring_pack/git_fetch.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/authoring_pack/backend_invoke.py
src/spec_dock/assets/spec_dock/scripts/authoring-pack/invoke_chatgpt_backend.py
tests/unit/authoring_pack/test_github_fetch_policy.py
tests/manual_tests/test_invoke_chatgpt_backend.py
```

The current runtime already has direct-argv backend invocation and bounded backend-failure handling.   It also has an existing stage/backup/replace/restore pattern suitable for bounded extraction into a shared transaction primitive.

The intended architecture is therefore broadly feasible. The verdict below is caused by remaining contract defects, not by a conclusion that the repository cannot support the feature.

## 3. Review scope and perspectives applied

The review covered:

1. Requirement completeness and internal consistency.
2. Design feasibility against current provider/runtime primitives.
3. Deterministic public result, status, reason, and exit semantics.
4. Review/Human authority and exact source/evidence binding.
5. Transaction, crash recovery, retry, wrong-output, and observability semantics.
6. Closure Index owner sets, owner portions, dependency direction, S99, and Final Exit.
7. REQ/AC/EC-to-step/test/evidence traceability.
8. Scope, compatibility, one-Issue/one-branch/one-PR, and Human-only merge.
9. Report and Assurance truthfulness and freshness.
10. Additional implementation-blocking ambiguities not limited to the previous finding set.

This was a read-only static review. No repository command, test suite, validator, build, or assurance command was executed by this reviewer.

## 4. Prior-finding closure and preservation assessment

### P1-17, P1-18, P1-19, and P2-05

| Prior finding                                                         | Current disposition                | Assessment                                                                                                                                                                                                                                                                                                                                           |
| --------------------------------------------------------------------- | ---------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **P1-17 — nondeterministic public status and PA-NF oracle**           | **Partially closed; remains open** | The correction splits PA-NF-10 into 10A/10B, establishes 11 exact fixtures, removes the previously undeclared `failed` result, and fixes exact Git-preflight mappings. However, the public result contract remains inconsistent outside that repaired subset, including command-success semantics and archive reason codes. Detailed below as P1-17. |
| **P1-18 — impossible wrong-output recovery after stage-only crash**   | **Closed**                         | Stage-only clean-H0 orphans are now separated from repository-visible partial state. Same-output cleanup, different-output clean-H0 new attempts, repository-visible wrong-output failure, committed wrong-workspace failure, and the prohibition on broad scans/registries are independently defined.                                               |
| **P1-19 — circular Closure Index/S99/Final Exit graph**               | **Closed**                         | Summary aliases are stateless; required rows have executable owners; S99 admission requires only pre-S99 portions; S99 owns only its declared portions; Final Exit owns no Closure portion and is an external handoff. The prescribed structural checks cover owner correspondence, allowed ordering, Final Exit owner count zero, and acyclicity.   |
| **P2-05 — Report described a published correction as commit-pending** | **Closed**                         | The Report now identifies published snapshot `3fc0e61ef8425abc0b4a5488d51e7060b0ed03cc`, records the fresh FAIL against it, and distinguishes that result from the later bounded correction and pending fresh review.                                                                                                                                |

### Preservation of P1-11 through P1-16

| Prior finding                                             | Preservation result                       | Evidence                                                                                                                                                             |
| --------------------------------------------------------- | ----------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **P1-11 — incorrect requested source identity**           | Preserved                                 | The required SHA is the exact inspected branch tip; no fallback source was substituted.                                                                              |
| **P1-12 — incompatible EC-005 mappings**                  | Preserved in its original scope           | Missing evidence, malformed/cross-bound evidence, source drift, Review-fail/Human-approved, unsupported revocation, and valid Human rejection retain exact mappings. |
| **P1-13 — incomplete Review/apply CLI identity**          | Preserved in its original syntactic scope | Both archive and Git-bound Review/apply forms retain explicit Issue, mode identity, evidence, expected HEAD, destination, and base contracts.                        |
| **P1-14 — rejection/revocation durability and authority** | Preserved                                 | Rejection remains a decision-only publication, old H0 evidence becomes stale, and revocation remains outside v1 and routed to the shared Human/Main boundary.        |
| **P1-15 — unclosed Candidate controls**                   | Preserved                                 | Canonical serialization, required keys, identity fields, inventory, checksums, source binding, and static placeholder semantics remain closed.                       |
| **P1-16 — prohibited content could reach backend argv**   | Preserved                                 | Prohibited content remains a pre-backend rejection class, while direct argv remains the default process boundary.                                                    |

The new findings below do not negate those scoped corrections. They identify additional semantic and observable-contract gaps left outside the previous repair set.

## 5. Findings

| ID        | Severity | Exact evidence                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | Impact                                                                                                                                                                                                                                                                                                                                                                                  | Required correction direction                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| --------- | -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **P1-17** | **P1**   | REQ-013 says every public result has a closed `status` and Design-defined `reason`, with `ready` as the only exit-0 status.  The public command family nevertheless defines successful create, revise, and read-only Review outcomes without assigning any legal success status, reason, or text/JSON result shape.  Design places the closed status family under the common Public Command Design rather than explicitly limiting it to apply.  Existing reused backend primitives return internal `status="pass"` on successful invocation, but no public translation is specified.   Design also maps all unsafe archive/integrity failures to `rejected: archive_rejected`, while the Plan requires numerous different exact public reason codes such as `unsafe_root`, `absolute_path`, `path_collision`, `integrity_mismatch`, and `resource_limit`. | Implementers cannot determine whether non-apply commands return no status, return an undeclared success status, or misuse `ready`. Text and JSON renderers can diverge. Archive tests and the Design reason registry cannot both pass as written. The repaired PA-NF matrix is deterministic, but the complete public-result contract is not.                                           | Define command-specific public result schemas for all four commands, including exact success status/reason, text/JSON shape, output selection, and exit behavior. Reserve `ready` for the complete approved apply conjunction. Reconcile the authoritative archive reason-code registry between Design and Plan, and extend Closure evidence to cover the entire public result surface rather than PA-NF alone.                                                                                                          |
| **P1-20** | **P1**   | REQ-007 requires Semantic complete replacement and Mechanical revision constrained by path, field, old/new literal, meaning invariant, and diff budget.  The public `planning revise` command accepts only `--candidate`, `--lane`, and `--output`; it has no Review result, finding artifact, Human feedback, or versioned mechanical-change request.  Design only says that the Skill selects the lane.  S04 has one generic Semantic positive and one Mechanical out-of-scope negative; it has no closed request schema, positive Mechanical fixture, old-value mismatch case, invariant validation, diff-budget boundary, or exact predecessor/finding binding.   The Report explicitly rejected same-thread continuity as a permanent product contract, so hidden conversation state cannot close this input gap.                                     | Semantic revision has no deterministic way to know which Review findings or Human feedback it must address. Mechanical revision has no public or internal closed description of the permitted edit. An implementation must invent hidden state, free-form input, or an undeclared sidecar convention. The accepted `zip-or-tree` input also lacks a closed safe-tree identity contract. | Define a versioned revision-request/evidence contract for both lanes, bind it to the predecessor Candidate/source identity and applicable Review or Human feedback, provide an explicit CLI transport, and specify exact validation and output identity rules. Add positive and negative Mechanical tests for old-value, path/field, invariant, and budget boundaries, plus Semantic tests proving finding-to-replacement traceability. Alternatively, remove a lane from this Issue through a reviewed scope amendment. |
| **P1-21** | **P1**   | Issue Planning promises a complete Bundle and a Review/Human/apply lifecycle bound to the reviewed identity.  Git-bound `target_paths` need only be one or more sorted, unique, safe, tracked regular blobs; Design does not require Issue ownership or inclusion of the canonical `requirement.md`, `design.md`, and `plan.md`.  Parser tests cover missing, unsorted, duplicate, cross-mode, and base errors, but not an unrelated blob or an incomplete canonical planning set.  The S05 identity matrix similarly has no missing-canonical-document or unrelated-target negative.                                                                                                                                                                                                                                                                      | A Review and Human decision can bind perfectly to a single unrelated or partial target set and still satisfy the syntactic identity contract. The Runtime could then derive `ready` without a formal Review of the complete Issue planning contract. This weakens Review authority and makes archive and Git-bound modes materially non-equivalent.                                     | Define the Git-bound reviewed-scope rule for Issue Planning. It must either require the exact canonical three-document set or define another closed scope object that proves complete-bundle coverage. Reject omitted canonical documents and unrelated paths, bind the Review prompt and apply parity to that exact scope, and add corresponding negative fixtures.                                                                                                                                                     |
| **P1-22** | **P1**   | The Requirement defines the product as starting from an existing Issue Node **or Seed**.  The Product Outcome and in-scope target resolution likewise cover the Issue Planning walking skeleton.   Design’s `PlanningRequest` names an existing Issue or approved Seed, but the public command exposes only `--issue <id>` and supplies no Seed identity, approval evidence, location, parent/dependency source, or resolution rule.   The Plan’s positive and negative resolution oracles cover only a known-valid existing Issue and an unknown Issue.                                                                                                                                                                                                                                                                                                   | One explicitly required input class has no implementable or testable public contract. Implementations may silently reject all Seeds, infer them from untrusted context, or invent a new persistence/lookup mechanism, each contradicting a different part of the planning set.                                                                                                          | Define a closed Seed identity and approval/source-binding contract, its public input form, deterministic parent/dependency/relevant-path resolution, Git/source binding, and positive/negative tests. Otherwise remove Seed initiation from this Issue’s outcome through an owner-scope amendment and preserve it for the appropriate later Issue.                                                                                                                                                                       |

## 6. Closure-graph assessment

### Structural result

The corrected Closure Index is structurally coherent under static inspection.

* Summary aliases are explicitly `required=no`, have no owner, and are navigation-only.
* The executable owner set is:

```text
S01
S02A
S02B
S03
S04
S05
S06
S07
S08
S09A
S09B
S90
S99
```

* No required row assigns ownership to Final Exit.
* Multi-owner rows have step-local portions rather than a single prematurely closable state.
* Owner lists follow forward execution order.
* S99 admission requires only S01–S90 portions; S99-owned portions may remain open at entry.
* S99 owns only `CLOS-REQ-020 / S99` and `CLOS-S99-001 / S99`.
* Final Exit is an external delivery handoff and does not mutate Closure state.
* The planned graph oracle explicitly checks owner/step exact correspondence, Final Exit owner count zero, ordered edges, S08’s exact claim set, S99 admission, and acyclicity.

No cycle was found in the declared dependency direction.

### Semantic qualification

The graph can reach a terminal structural state, but some rows do not yet have sufficient semantic oracles:

* `CLOS-REQ-013` overstates complete exact public-status/reason coverage while its cited implementation evidence primarily covers apply/PA-NF and recovery cases.
* `CLOS-REQ-007` claims a closed Mechanical edit contract without a revision-request schema or sufficient Mechanical tests.
* `CLOS-REQ-006` closes syntactic Git-bound identity but not complete Issue-review scope.
* The existing-Issue-or-Seed outcome has no Seed-specific owner/test portion.

The graph repair therefore closes P1-19, but graph validity does not compensate for incomplete contracts owned by individual rows.

## 7. Requirement, Design, Plan, Report, and Assurance consistency

| Surface                       | Assessment                                                                                                                                                                                                                                                                                     |
| ----------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Requirement ↔ Design**      | **Not implementation-ready.** Recovery, authority evidence, Candidate controls, and apply semantics are substantially aligned. Public success-result semantics, revision input, Git-bound reviewed scope, and Seed initiation remain incomplete or contradictory.                              |
| **Design ↔ provider code**    | **Broadly feasible, but underspecified at critical boundaries.** Existing direct-argv, safe-path, Git, archive, and stage/backup/restore primitives support the intended implementation. The missing contracts would nevertheless force implementation decisions not authorized by the Design. |
| **Plan ↔ Requirement/Design** | **Structurally strong but semantically incomplete.** Owner portions, S99, and Final Exit now form a valid DAG. The tests do not close the four P1 gaps identified above.                                                                                                                       |
| **Report**                    | **Truthful for the inspected state.** It records the prior published FAIL, treats the Blue output as correction evidence rather than Review authority, states that the corrected snapshot has not yet received a fresh Review, and states that product implementation has not started.         |
| **Assurance**                 | **Source-bound but non-admitting.** The file is `provisional`, binds the current Requirement/Design/Plan hashes, and does not claim Review PASS or implementation authority.                                                                                                                   |
| **Parent boundaries**         | **Preserved.** The current planning set retains the parent separation of Human approval, Runtime determinism, one Issue/one branch/one PR, and Human-only merge.                                                                                                                               |
| **Self-approval**             | **Absent.** Neither the Report nor provisional Assurance is used as a substitute for this fresh Review.                                                                                                                                                                                        |

## 8. Severity counts

| Severity | Count |
| -------- | ----: |
| P0       |     0 |
| P1       |     4 |
| P2       |     0 |
| P3       |     0 |

## 9. Final verdict

FAIL

## 10. S01 disposition

blocked

## 11. Assumptions and uncertainty

* The GitHub connector’s exact remote commit and blobs are the reviewed source. No claim is made about an unobserved local worktree.
* Generated `spec-dock/active/` views were not present as tracked objects at the immutable remote snapshot; their canonical targets were resolved through the tracked source bindings and runtime-generation contract.
* No planned product test, validator, lint command, build, archive check, graph parser, or assurance command was executed by this reviewer. Results written in `report.md` were inspected as historical evidence but not independently reproduced.
* The Closure graph assessment is a manual static analysis of the canonical Plan, not execution of `tc-s99-002`.
* The SHA-256 values stored inside `.assurance.json` were inspected but were not independently recomputed from locally downloaded raw bytes.
* The parent’s single PA-NF-10 condition is treated as permitting the Issue-level 10A/10B refinement because both branches are retained and independently tested. This does not resolve the separate public-result inconsistencies identified in P1-17.
* The separately supplied exception/failure-boundary design note concerns another design problem and was excluded from repository facts and verdict evidence.

This artifact is read-only. It does not authorize implementation, publication, PR delivery, merge, Issue completion, or any repository mutation.
