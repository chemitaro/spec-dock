---
artifact_type: s04-chatgpt-implementation-work-packet
created_at: 2026-07-28T12:38:50+09:00
created_by_role: chatgpt-pro
intended_issue: iss-00334
intended_step: S04
adoption_status: execution-input
review_required: false
source_repository: chemitaro/spec-dock
source_branch: iss-00334-implement-chatgpt-issue-planning-workflow
source_head: 18006b779c70cdb13e4e5baae29ac3d79e77a954
initial_session: iss00334-s04-implementa-brief
followup_session: required-repository-connector-context-github-109
initial_model_evidence: requested=Pro; resolved=Pro; verified=yes
followup_model_evidence: requested=Pro; resolved=(unavailable); verified=no
---

# Oracle Browser Transcript

Conversation: https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a6819c7-f980-83ee-bcbc-c53b81cbb3f6

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

Reassess your STOP using these verified repository facts and the JIT execution contract. D-20260727-EX012 authorizes each step work packet to fix implementation-local encodings without re-growing canonical planning; D-20260727-RB010 forbids speculative schema/proof-matrix expansion; D-20260726-RT002 explicitly rejected durable same-thread/session-locator continuity as a permanent product contract, keeping same-Blue continuity initiative-operational only. S04 may implement internal application/domain/infra orchestration and tests; S06 owns provider projection, installed workflow, docs/help parity and full E2E. Re-check whether exact Review ingress can be an explicit application-use-case input without changing the currently stubbed public parser at S04, whether Mechanical can be gated by the separately supplied exact Review (same Candidate identity and at least one P0/P1) while leaving the closed Mechanical request schema unchanged, whether same-callable/backend context plus complete prior Candidate/formal findings satisfies product behavior without durable session identity, and whether diff_budget can be fixed as an implementation-local deterministic UTF-8 byte delta under EX012. Do not accept these suggestions blindly. Inspect the GitHub branch and current contracts, distinguish true product-contract blockers from implementation-local/S04-vs-S06 integration details, and return either (A) a replacement implementation-ready S04 packet with exact allowlist/Red matrix/sequence/verification/stop conditions, or (B) a reduced STOP containing only choices that genuinely cannot be resolved without canonical/Human amendment. Do not propose a patch or S05+ work.

## Answer

# S04 Replacement Implementation Work Packet

## 1. Reassessment result and verified execution identity

**Result: A — the previous STOP is withdrawn.**

The four previously identified questions can be resolved inside the Human-authorized JIT execution boundary without changing the canonical Requirement, Design, Plan, public command family, or closed revision-request schema. D-20260727-EX012 authorizes step-local concretization; D-20260727-RB010 rejects speculative canonical expansion; and D-20260726-RT002 explicitly rejects a durable session locator as a permanent product contract.

This packet implements only the S04 brief supplied for this task.

| Field                         | Verified value                                                  |
| ----------------------------- | --------------------------------------------------------------- |
| Repository                    | `chemitaro/spec-dock`                                           |
| Current branch                | `iss-00334-implement-chatgpt-issue-planning-workflow`           |
| Default branch                | `main`                                                          |
| Required exact HEAD           | `18006b779c70cdb13e4e5baae29ac3d79e77a954`                      |
| GitHub connector comparison   | branch and required HEAD are `identical`; ahead `0`, behind `0` |
| Exact commit purpose          | S03 closure evidence and handoff to S04                         |
| Inspection mode               | read-only GitHub connector inspection                           |
| Test execution in this thread | not executed; no Red/Green count is claimed                     |

The exact commit exists, records S03 as committed, pushed, clean, and closed, and explicitly advances the Issue to S04 concretization.

Provider authority remains under `src/spec_dock/assets/`; root `spec-dock/` is the dogfood consumer workspace and is not a worker implementation surface for this milestone.

### Prior STOP disposition

| Prior concern              | Classification after reinspection                                           | S04 disposition                                                                                                                                                                                    |
| -------------------------- | --------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Exact Review ingress       | S04/S06 integration boundary, not a product-schema blocker                  | Supply exact Review bytes and digest through a new **internal application execution input**. Do not alter the public parser or `PlanningRevisionRequestV1`.                                        |
| Mechanical Review binding  | Application orchestration rule already determined by current contracts      | Require the separately supplied exact Review to be an archive Review of the same Candidate and to contain at least one P0/P1. Keep the Mechanical JSON schema unchanged.                           |
| Same-Blue continuity       | Initiative-operational concern explicitly rejected as durable product state | Use the same fixed backend adapter/callable with a self-contained prompt containing the complete prior Candidate and formal findings. Create no session locator, registry, or continuity identity. |
| `diff_budget` unit         | Deterministic implementation-local encoding                                 | Define it as the total UTF-8 bytes touched by the one replacement: deleted bytes plus inserted bytes.                                                                                              |
| Candidate revision version | Direct S04 integration seam                                                 | Generalize the existing v1 value encoding to positive Candidate version `N`; create remains v1 and revise emits `prior.version + 1`.                                                               |

The public `planning revise` parser presently accepts only Candidate, request, and output arguments, while the application use cases remain fail-closed stubs. That makes it possible to implement and test an explicit S04-only application evidence input without changing or wiring the public parser in this milestone.

---

## 2. S04 goal and bounded scope

### Goal

Implement fresh, read-only archive/git-bound planning Review and the Semantic and Mechanical revision lanes, with both lanes producing a new immutable Candidate through the existing S03 packager.

The canonical S04 work is limited to Reviewed identity construction, exact Review targets, defect-only result validation, immutability proof, complete Semantic replacement, exact Mechanical replacement, and new Candidate generation. Its exit requires create→Review and revise→fresh Review fake-backend chains, no PASS inheritance, and no reviewer patch/replacement/ZIP authority.

### In-scope obligations

1. Construct `ReviewedPlanningIdentity` for both modes.
2. In archive mode, review the exact validated Candidate ZIP bytes.
3. In git-bound mode, review the exact three canonical document bytes at the exact synchronized HEAD.
4. Keep supplemental context explicitly separate from reviewed targets and outside reviewed identity.
5. Invoke a fresh defect-only, read-only Reviewer.
6. Parse and validate exact `PlanningReviewResult` JSON and its runtime-constructed identity.
7. Derive PASS only from zero P0/P1 findings.
8. Save exact machine-readable Review bytes and a deterministic Human-readable summary outside the repository.
9. Prove the Candidate and tracked repository state did not change during Review.
10. Perform Semantic revision from the prior Candidate, exact Review, selected P0/P1 findings, and preserved assumptions.
11. Perform Mechanical revision as one exact, unique, target-body-only replacement within its deterministic byte budget.
12. Require exact prior Review evidence for both lanes.
13. Block revision for a P2/P3-only Review with backend call count zero.
14. Route both revision lanes through the existing S03 validation and atomic no-replace publication path.
15. Preserve the old Candidate and emit a new version, Candidate ID, filename, and ZIP SHA.
16. Exercise create→Review and revise→fresh Review chains hermetically.

The Requirement fixes exact Candidate identity, exact Review modes and target paths, read-only Review, the P0/P1 blocking rule, explicit Semantic and Mechanical request fields, old-Candidate immutability, and new Candidate identity after revision.

### Explicit non-goals

* No change to `planning create`, `planning revise`, `review planning`, or `planning apply` public arguments.
* No parser, command-handler, bootstrap, `UseCases`, or runtime-construction wiring.
* No official Skill workflow wiring, projection refresh, help/docs parity, wheel/sdist, or full installed E2E.
* No S05 Human decision, canonical adoption, rollback, commit, push, publication retry, or remote divergence handling.
* No dogfood projection edits.
* No live ChatGPT/browser dogfood.
* No canonical `requirement.md`, `design.md`, `plan.md`, `report.md`, `.assurance.json`, or Issue-artifact edits by the worker.
* No generic Review framework, database, registry, custom Git ref, or persistent session identity.
* No semantic “meaning evaluator” for Mechanical revision.
* No PASS inheritance or Review-result registry.

---

## 3. Repository findings and exact reuse map

| Existing symbol or primitive    | Current behavior                                                                                                                 | Required S04 use                                                                                                                      |
| ------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| `PlanningReviewRequest`         | Already carries issue, explicit mode, external output, Candidate path or reviewed HEAD.                                          | Reuse unchanged as the Review application request.                                                                                    |
| `PlanningReviseRequest`         | Carries Candidate, closed request JSON, and external output only.                                                                | Reuse unchanged. Exact Review evidence is a separate internal application input, not a new public/request field.                      |
| `ReviewedPlanningIdentity`      | Closes archive versus git-bound identity, validates exact canonical paths, and computes canonical SHA-256.                       | Runtime constructs it; the model may only echo the exact object.                                                                      |
| `PlanningReviewResult`          | Strict closed JSON; unique findings; verdict must match the P0/P1 rule.                                                          | Parse exact backend payload and compare the complete returned identity with the runtime identity.                                     |
| `PlanningRevisionRequestV1`     | Semantic includes Review digest and finding IDs; Mechanical includes exact textual operation and budget.                         | Keep its field sets unchanged. Reuse `validate_against()` for Semantic; add Mechanical Review gating in application orchestration.    |
| Existing S01 tests              | Already protect P0/P1 verdict derivation, exact raw Review bytes, selected finding eligibility, and the closed Mechanical shape. | Run as regression; do not duplicate their schema matrix.                                                                              |
| `run_github_sync_preflight`     | Supports explicit source paths and an expected source-manifest hash.                                                             | Run before and after Review/revision to prove exact HEAD, clean tree, and source stability.                                           |
| Candidate ZIP profile           | Validates exact seven-file inventory, path safety, modes, encryption, binary content, limits, and cross-file controls.           | Use for Candidate loading before Review or revision; leave generic no-profile behavior untouched.                                     |
| `build_and_publish_candidate`   | Temp build, named-profile validation, actual ZIP SHA, output revalidation, atomic no-replace publication.                        | Reuse as the only revised-Candidate publisher.                                                                                        |
| Candidate domain builder        | Currently fixes Candidate version and naming to v1.                                                                              | Add positive `version` input with default `1`; revise passes `prior.version + 1`.                                                     |
| `SynthesizedPlanningPrompt`     | Supports role, prompt text, and UTF-8 text attachments.                                                                          | Add an optional exact-byte attachment collection without changing existing S02 text-attachment behavior.                              |
| `invoke_issue_planning_chatgpt` | Uses fixed direct argv, a unique temporary-directory-derived slug, and the existing outer frame.                                 | Reuse the invocation and frame classifier; extend prompt-pack writing for exact binary/text attachments. No durable session identity. |
| Backend attachment assembly     | Adds every safe regular manifest file as a repeated `--file`; it does not impose a text-only extension contract.                 | The exact Candidate ZIP can be attached through the existing backend interface; no backend ABI change is needed.                      |
| Current Reviewer resource       | Already denies patch, replacement, ZIP, mutation, and authority.                                                                 | Extend it only with the exact `PlanningReviewResult` JSON output contract.                                                            |
| Current presentation module     | Owns deterministic planning text/JSON rendering.                                                                                 | Add a pure Human-readable Review-summary renderer without changing existing CLI rendering.                                            |

---

## 4. Exact S04 implementation-local contracts

### 4.1 Explicit Review ingress for revision

Do **not** change `PlanningReviseRequest`, `PlanningRevisionRequestV1`, or the public parser.

Add an application-only immutable input:

```text
PlanningRevisionEvidenceInput
- review_result_path: Path
- review_result_sha256: lowercase 64-hex
```

Use it through an internal function boundary:

```text
run_issue_planning_revise(
    *,
    request: PlanningReviseRequest,
    review_evidence: PlanningRevisionEvidenceInput,
    records,
    repo_root,
    ...
) -> PlanningCommandResult
```

Validation order:

1. Validate the Candidate path and load the verified Candidate.
2. Parse the closed revision request.
3. Verify `request.candidate_identity == loaded_candidate.identity`.
4. Validate the Review-result input path:

   * existing regular file;
   * no symlink component;
   * outside the repository;
   * bounded size;
   * strict UTF-8 JSON.
5. Read the file once as exact bytes.
6. Require the actual SHA-256 to equal `review_evidence.review_result_sha256`.
7. Parse `PlanningReviewResult` from those exact bytes.
8. Require archive mode and exact Candidate identity.
9. Preserve those bytes and digest through the operation; do not rediscover or scan for another Review result.

For Semantic revision, also require:

```text
request.review_result_sha256
== review_evidence.review_result_sha256
== sha256(exact review_result_bytes)
```

For Mechanical revision, the separate execution evidence supplies the exact Review digest without adding fields to the Mechanical JSON contract.

This is an internal S04 orchestration input. How an installed workflow constructs it is outside this milestone; public parser and `UseCases` remain untouched and unconfigured.

### 4.2 Mechanical Review gate without schema expansion

A Mechanical request may proceed only when all of the following hold:

```text
review.mode == archive-candidate
review.candidate_identity == request.candidate_identity
review.candidate_identity == loaded_candidate.identity
review.verdict == fail
at least one review finding has severity p0 or p1
```

Mechanical requests do not select finding IDs because the approved closed Mechanical schema deliberately contains no `finding_ids` field. The exact target, old text, new text, invariant, and budget are the explicit requested correction. The supplied exact Review establishes that revision is eligible.

A Review containing only P2/P3 observations returns:

```text
status = blocked
reason = revision_not_required
```

Required side effects:

```text
revision backend calls = 0
new Candidate files = 0
old Candidate SHA unchanged
repository state unchanged
```

### 4.3 Stateless Semantic revision

Do not persist or expose a session locator.

Semantic revision uses:

* the existing fixed backend adapter;
* role `planner`;
* a new provider-managed `revision-prompt.md`;
* the exact prior Candidate ZIP;
* extracted prior `requirement.md`, `design.md`, and `plan.md`;
* exact Review-result bytes;
* the selected formal P0/P1 findings;
* `preserve_assumptions`;
* exact repository, branch, source HEAD, and Candidate identity;
* the existing exact three-document output framing.

Each invocation remains independently reconstructable. The current adapter already creates a unique invocation slug from transient state, so no PASS, conversation, or session identity is persisted.

Initiative-level same-Blue continuity may still be used operationally by the surrounding workflow, but it is not a runtime product invariant and must not appear in Candidate controls, Review identity, request JSON, result JSON, or repository state.

### 4.4 Exact Review targets and attachment separation

Add an internal attachment record:

```text
PlanningPromptAttachment
- name: safe basename or safe relative pack path
- classification:
    - review-target
    - supplemental-context
    - formal-evidence
- source_label: safe repository-relative or logical label
- content: exact bytes, excluded from repr
- sha256: derived, not caller-authored
```

Rules:

* Existing S02 `attachments: tuple[(path, text)]` remains unchanged.
* New exact attachments are additive and optional.
* Duplicate attachment names or source labels are rejected.
* Absolute paths, parent traversal, hidden paths, credential-like names, and symlinks are rejected.
* Attachment bytes are hashed before writing and rehashed after writing the prompt pack.
* Prompt text contains a deterministic attachment index with classification, logical source label, and SHA-256.

Archive mode:

```text
review-target:
  target-candidate.zip        # exact validated input bytes

formal-evidence:
  reviewed-identity.json      # runtime-generated canonical identity

supplemental-context:
  explicit bounded context only
```

Git-bound mode:

```text
review-target:
  target-requirement.md
  target-design.md
  target-plan.md

formal-evidence:
  reviewed-identity.json

supplemental-context:
  explicit bounded files that are not any of the three targets
```

The three target paths remain the only git-bound paths in `ReviewedPlanningIdentity`; supplemental paths never enter identity or verdict binding. The canonical documents expressly permit supplemental read-only context while excluding it from reviewed target identity.

### 4.5 Candidate loading and version generalization

Add `load_verified_issue_candidate()` to the Candidate infra owner.

It must:

1. Reject missing, symlinked, non-file, repository-internal, or unsafe Candidate paths.
2. Read the exact ZIP bytes and SHA-256.
3. Derive one safe internal root from the archive inventory.
4. Run `issue_candidate_v1_profile()` and `verify_issue_candidate_files()`.
5. Read the seven verified files only after profile PASS.
6. Reconstruct the logical filename, Candidate ID, version, root, source repository, branch, HEAD, and source baseline from controls.
7. Build `IssueCandidateIdentity` with the actual observed transport filename and actual ZIP SHA.
8. Accept only the existing closed ` (N)` transport alias.
9. Return immutable verified files and source controls.
10. Never extract to the repository.

Generalize the Candidate builder:

```text
build_candidate_material(..., version: int = 1)
```

Rules:

* integer only; reject `bool`;
* `version >= 1`;
* create continues to omit the argument and remains v1;
* revise supplies `prior.version + 1`;
* logical filename root uses `candidate-v<version>`;
* Candidate ID uses `<issue>-v<version>-<timestamp>`;
* control-file schema versions remain `...v1`;
* inventory remains the exact seven files;
* no new manifest or baseline field is added.

For a Mechanical revision, Runtime constructs the same exact three-document inner payload from the replaced documents and supplies those bytes to the existing Candidate builder. This reuses the existing `planner_payload_sha256`/size control fields without expanding the S03 control schema.

### 4.6 Review-result contract and publication

The Reviewer must return exactly one JSON object inside the existing outer response frame:

```json
{
  "reviewed_identity": {},
  "reviewed_identity_sha256": "<64-hex>",
  "verdict": "pass|fail",
  "findings": [
    {
      "id": "<non-empty>",
      "severity": "p0|p1|p2|p3",
      "exact_location": "<non-empty>",
      "violated_requirement_or_contradiction": "<non-empty>",
      "concrete_impact": "<non-empty>"
    }
  ]
}
```

No prose, Markdown summary, patch, replacement, ZIP, Human decision, or authority claim may appear in the payload. Unknown keys are already rejected by the current parser, and the verdict is already constrained by P0/P1 presence.

Runtime must compare:

```text
parsed.reviewed_identity == runtime_constructed_identity
parsed.reviewed_identity_sha256 == runtime_constructed_identity.sha256
```

Publish one atomically renamed external directory:

```text
review-<UTC-token>-<full-reviewed-identity-sha256>/
├── planning-review-result.json
└── planning-review-summary.md
```

Publication rules:

* build both files in an owned temporary directory under the guarded external output;
* keep the Review JSON bytes exactly as received after outer-frame extraction;
* generate summary deterministically from the parsed object;
* fsync files before publication;
* atomically rename the directory with the existing no-replace primitive;
* never overwrite;
* never return an absolute path;
* on pre-publication failure, leave no final directory.

Successful output keys:

```text
review_result_file
review_summary_file
review_result_sha256
reviewed_identity_sha256
verdict
```

The paths are relative to the supplied external output directory.

### 4.7 Review immutability proof

Before backend invocation:

* validate and hash the Candidate in archive mode;
* run exact Git preflight;
* retain branch, local/remote HEAD, source-manifest hash, and repository snapshot evidence.

After backend invocation, but before result publication:

* rehash the Candidate path in archive mode;
* rerun Git preflight with the original expected source hash;
* require the same repository, branch, local HEAD, remote HEAD, and source-manifest hash;
* require a clean tracked/index/untracked state;
* require the Review-result identity to match the pre-invocation identity.

Any change returns:

```text
status = stale
reason = review_target_changed
```

No Review artifact is published.

The Review itself returns `ok/review_completed` even when its verdict is `fail`; `ok` means command completion, not implementation readiness. The canonical result contract reserves `ready` for completed apply publication.

### 4.8 Semantic revision sequence

1. Load and verify old Candidate.
2. Load exact Review evidence.
3. Parse Semantic request.
4. Call existing `request.validate_against(review, exact_review_bytes)`.
5. Run source preflight against the Candidate’s recorded source paths/hash.
6. Synthesize a self-contained revision prompt.
7. Invoke the existing Planner adapter once.
8. Require exact transport payload digest.
9. Parse exact three-document replacement with the S03 parser.
10. Validate front matter, Issue identity, parents, and completeness.
11. Build Candidate version `old.version + 1`.
12. Publish through `build_and_publish_candidate`.
13. Rehash the old Candidate and recheck source state.
14. Return `ok/candidate_revised`.

No automatic Review is run inside this operation. The integration test invokes `run_issue_planning_review()` separately on the new Candidate, guaranteeing a fresh Reviewer operation.

### 4.9 Mechanical revision sequence and deterministic budget

Mechanical revision performs no backend call.

It must:

1. Decode the target document as strict UTF-8.
2. Parse and preserve its closed front matter.
3. Search only the substantive body, not front matter.
4. Require exactly one occurrence of `old_text`.
5. Compute:

```text
replacement_cost_bytes =
    len(old_text.encode("utf-8"))
  + len(new_text.encode("utf-8"))
```

6. Require:

```text
replacement_cost_bytes <= diff_budget
```

7. Replace the unique occurrence once.
8. Require the other two substantive document bodies to remain byte-identical.
9. Revalidate the full three-document set.
10. Permit only existing S03 runtime-owned front-matter normalization, including `最終更新`; this metadata normalization is outside the textual replacement budget.
11. Render the complete three-document payload.
12. Build and publish Candidate version `old.version + 1`.

This formula is deliberately not absolute length difference: an equal-length full replacement must not have zero cost. It is also not Levenshtein distance, which would add an unnecessary algorithmic contract.

`meaning_invariant` remains a required explicit operator/Skill assertion. Runtime enforces its structural boundary—one target body, one exact replacement, no fallback, and no other substantive body change—but does not invent a semantic theorem prover.

### 4.10 Closed S04 result mapping

| Condition                                                              | Status              | Reason                                           |
| ---------------------------------------------------------------------- | ------------------- | ------------------------------------------------ |
| Review completed, regardless of PASS/FAIL verdict                      | `ok`                | `review_completed`                               |
| Revision Candidate atomically published                                | `ok`                | `candidate_revised`                              |
| Existing transport blocked/rejected                                    | preserve            | preserve S02 reason                              |
| Review/revision Git preflight blocked                                  | `blocked`           | `git_preflight_blocked`                          |
| Candidate/source HEAD or source-manifest drift                         | `stale`             | `review_source_stale` or `revision_source_stale` |
| Candidate/profile/control rejection                                    | `rejected`          | `archive_rejected`                               |
| Review mode/options or target construction invalid                     | `rejected`          | `review_request_rejected`                        |
| Malformed/wrong-identity Review result                                 | `rejected`          | `review_result_rejected`                         |
| Review or tracked target changed during invocation                     | `stale`             | `review_target_changed`                          |
| Unsafe Review output                                                   | `rejected`          | `review_output_rejected`                         |
| Missing/unreadable exact revision Review evidence                      | `blocked`           | `revision_review_unavailable`                    |
| Review digest/Candidate/mode mismatch                                  | `rejected`          | `revision_evidence_mismatch`                     |
| P2/P3-only Review supplied to revision                                 | `blocked`           | `revision_not_required`                          |
| Malformed revision request                                             | `rejected`          | `revision_request_rejected`                      |
| Mechanical zero/multiple match, front-matter target, or budget failure | `rejected`          | `mechanical_revision_rejected`                   |
| Semantic replacement malformed/incomplete                              | `rejected`          | `planner_response_rejected`                      |
| Existing final Candidate or Review directory                           | `rejected`          | `output_collision`                               |
| Candidate build/publication failure                                    | existing S03 status | existing S03 reason                              |
| Review artifact publication failure                                    | `blocked`           | `review_publication_failed`                      |

No new status is added. Non-success reasons remain lower snake case as permitted by the existing `PlanningCommandResult` contract.

---

## 5. Exact write allowlist

Only the following paths may be added or modified.

### Provider Prompt resources

```text
src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/resources/
├── reviewer-prompt.md                         # modify
└── revision-prompt.md                         # new
```

### Provider runtime

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/
├── application/
│   ├── issue_planning.py                      # modify
│   └── issue_planning_prompt.py               # modify
├── domain/
│   └── issue_planning_candidate.py            # modify
├── infra/
│   ├── issue_planning_candidate.py            # modify
│   ├── issue_planning_chatgpt.py              # modify
│   └── issue_planning_review.py               # new
└── presentation/
    └── issue_planning.py                      # modify
```

### Tests

```text
tests/
├── integration/
│   └── test_issue_planning_chatgpt_transport.py       # modify
└── unit/
    ├── application/
    │   ├── test_issue_planning.py                      # modify
    │   └── test_issue_planning_prompt.py               # modify
    ├── domain/
    │   └── test_issue_planning_candidate.py            # modify
    ├── infra/
    │   ├── test_issue_planning_candidate.py            # modify
    │   ├── test_issue_planning_chatgpt.py              # modify
    │   └── test_issue_planning_review.py                # new
    └── presentation/
        └── test_issue_planning.py                       # modify
```

**No other path is authorized.**

### Explicitly read-only compatibility surfaces

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/
├── application/contracts.py
├── application/authoring_pack/backend_invoke.py
├── application/authoring_pack/github_sync_preflight.py
├── commands/issue_planning.py
├── cli/chatgpt_parser.py
├── cli/chatgpt_registry.py
├── domain/issue_planning_contracts.py
├── domain/authoring_pack/zip_contract.py
└── infra/git_cli.py

src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/resources/
├── planner-prompt.md
└── transport-output-contract.md

tests/
├── cli_runtime/test_chatgpt_cli.py
├── unit/commands/test_issue_planning.py
├── unit/domain/test_issue_planning_contracts.py
├── unit/authoring_pack/test_zip_contract_profiles.py
└── unit/authoring_pack/test_backend_invoke_capture.py
```

The closed S01 contracts, parser, command layer, and generic archive validator are regression oracles, not S04 write surfaces.

---

## 6. Bounded Red-first test matrix

Do not count missing imports, collection errors, or syntax errors as Red evidence. Add minimal typed symbols if needed so tests collect; the first recorded Red run must fail on behavioral assertions.

| ID                | Test file / intended node                                                                                | Required assertion                                                                                                     | Expected initial Red                                               |
| ----------------- | -------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------ |
| S04-CAND-001      | `test_issue_planning_candidate.py::test_revision_candidate_uses_prior_version_plus_one`                  | v1 create remains unchanged; revision material can be v2 and validates under the same control schema.                  | Builder and verifier currently hard-code version 1.                |
| S04-CAND-002      | `test_issue_planning_candidate.py::test_candidate_vn_naming_is_self_consistent`                          | Version, Candidate ID, root, logical filename, and manifest agree for N > 1; bool/zero rejected.                       | Existing naming accepts only v1.                                   |
| S04-LOAD-001      | `test_issue_planning_candidate.py::test_load_verified_candidate_round_trips_exact_identity`              | Loader reconstructs controls plus actual observed filename and ZIP SHA.                                                | No Candidate loader exists.                                        |
| S04-LOAD-002      | `test_issue_planning_candidate.py::test_load_verified_candidate_accepts_only_closed_transport_alias`     | Logical filename and ` (N)` alias pass; fuzzy rename, repack, root mismatch, and wrong hash reject.                    | Current infra only builds Candidates.                              |
| S04-PROMPT-001    | `test_issue_planning_prompt.py::test_archive_review_prompt_has_one_exact_zip_target`                     | Exact ZIP is the sole reviewed target; identity and supplemental data are differently classified.                      | Current prompt model supports only text context tuples.            |
| S04-PROMPT-002    | `test_issue_planning_prompt.py::test_git_bound_review_prompt_has_exact_three_targets_in_utf8_order`      | Three canonical targets only; supplemental files excluded from identity.                                               | No S04 Review synthesis exists.                                    |
| S04-PROMPT-003    | `test_issue_planning_prompt.py::test_reviewer_prompt_requires_exact_result_and_denies_authority_outputs` | Prompt requires strict JSON and forbids patch, replacement, ZIP, decision, or authority.                               | Current resource has no machine-readable output contract.          |
| S04-PROMPT-004    | `test_issue_planning_prompt.py::test_semantic_revision_prompt_is_self_contained_without_session_locator` | Prior Candidate, exact Review, selected findings, assumptions, and output contract are present; no session key exists. | No revision Prompt exists.                                         |
| S04-TRANSPORT-001 | `test_issue_planning_chatgpt.py::test_prompt_pack_preserves_exact_binary_attachment_bytes`               | Written Candidate ZIP hash equals input hash and is attached through repeated direct-argv `--file`.                    | Current writer serializes only text context attachments.           |
| S04-TRANSPORT-002 | `test_issue_planning_chatgpt.py::test_each_review_invocation_uses_fresh_transient_slug`                  | Two calls use distinct transient slugs and persist no locator.                                                         | Freshness is incidental and currently unasserted for Review.       |
| S04-REVIEW-001    | `test_issue_planning.py::test_archive_review_constructs_exact_reviewed_identity`                         | Runtime identity uses the verified Candidate identity and source binding.                                              | No Review orchestration exists.                                    |
| S04-REVIEW-002    | `test_issue_planning.py::test_git_bound_review_constructs_exact_three_path_identity`                     | Exact resolver tuple and reviewed HEAD are required; wrong path/head rejects before backend.                           | No Review orchestration exists.                                    |
| S04-REVIEW-003    | `test_issue_planning.py::test_review_accepts_exact_bound_result_and_returns_review_completed`            | Exact result bytes parse, identity matches, verdict is preserved, and result is `ok/review_completed`.                 | No Review result application path exists.                          |
| S04-REVIEW-004    | `test_issue_planning.py::test_review_rejects_wrong_identity_mode_digest_and_unknown_authority_output`    | Parameterized result mismatches publish no evidence.                                                                   | Existing parser is not invoked by an application Review operation. |
| S04-REVIEW-005    | `test_issue_planning.py::test_archive_review_detects_candidate_change_after_backend`                     | Post-call Candidate SHA change yields `stale/review_target_changed`; final evidence count zero.                        | No pre/post Candidate guard exists.                                |
| S04-REVIEW-006    | `test_issue_planning.py::test_review_detects_repository_change_after_backend`                            | Dirty tree, changed HEAD, or changed source hash yields stale and publishes zero.                                      | No post-Review preflight exists.                                   |
| S04-REVIEW-007    | `test_issue_planning_review.py::test_review_evidence_directory_publishes_atomically_no_replace`          | Both files appear together; collision preserves old bytes; failure leaves no final directory.                          | No Review evidence publisher exists.                               |
| S04-REVIEW-008    | `test_issue_planning.py::test_repeated_review_never_inherits_prior_pass`                                 | Repeated call invokes backend again and validates new bytes; no cached PASS lookup.                                    | No Review operation exists.                                        |
| S04-SUMMARY-001   | `test_issue_planning.py::test_review_summary_is_deterministic_and_authority_neutral`                     | Stable Markdown; no patch/replacement/approval claim or absolute paths.                                                | No summary renderer exists.                                        |
| S04-SEM-001       | `test_issue_planning.py::test_semantic_revision_requires_explicit_exact_review_evidence`                 | Path SHA, internal expected SHA, and request SHA all bind to exact bytes.                                              | Revise has no implementation or Review ingress.                    |
| S04-SEM-002       | `test_issue_planning.py::test_semantic_revision_reuses_existing_p0_p1_validator`                         | Selected P0/P1 succeeds; unknown, P2/P3, mixed, wrong Candidate, or git-bound Review rejects before backend.           | Existing domain validator is not integrated.                       |
| S04-SEM-003       | `test_issue_planning.py::test_semantic_revision_backend_receives_prior_candidate_and_formal_findings`    | Exact Candidate plus selected findings and assumptions reach the same injected backend callable.                       | No Semantic orchestration exists.                                  |
| S04-SEM-004       | `test_issue_planning.py::test_semantic_complete_replacement_returns_new_candidate`                       | Complete replacement publishes version N+1 and `ok/candidate_revised`; old SHA unchanged.                              | No revision packaging path exists.                                 |
| S04-SEM-005       | `test_issue_planning.py::test_semantic_partial_extra_wrong_issue_or_scope_escape_publishes_zero`         | Malformed/partial/fourth/wrong-identity payload yields `planner_response_rejected`.                                    | No Semantic response parser path exists.                           |
| S04-SEM-006       | `test_issue_planning.py::test_semantic_transport_nonpass_preserves_existing_reason`                      | Backend timeout/nonzero/malformed classifications are preserved and no Candidate work begins.                          | No revision transport mapping exists.                              |
| S04-MECH-001      | `test_issue_planning.py::test_mechanical_revision_requires_same_candidate_blocking_review`               | Same exact Candidate plus at least one P0/P1 required; wrong Review/digest/mode rejects.                               | Mechanical structure currently has no application Review gate.     |
| S04-MECH-002      | `test_issue_planning.py::test_p2_p3_only_review_blocks_revision_with_backend_zero`                       | `blocked/revision_not_required`; Candidate and output unchanged; backend count zero.                                   | No Mechanical execution exists.                                    |
| S04-MECH-003      | `test_issue_planning_candidate.py::test_mechanical_revision_replaces_one_target_body_match`              | Exactly one body occurrence changes; front matter cannot be targeted.                                                  | No replacement primitive exists.                                   |
| S04-MECH-004      | `test_issue_planning_candidate.py::test_mechanical_revision_rejects_zero_and_multiple_matches`           | Both cases reject with no new Candidate.                                                                               | No match-count guard exists.                                       |
| S04-MECH-005      | `test_issue_planning_candidate.py::test_mechanical_diff_budget_is_deleted_plus_inserted_utf8_bytes`      | Multibyte fixtures prove exact byte formula; threshold equal passes, one below rejects.                                | `diff_budget` currently has structural validation only.            |
| S04-MECH-006      | `test_issue_planning_candidate.py::test_mechanical_non_target_bodies_remain_identical`                   | Only target body changes; runtime date normalization is the only permitted metadata delta.                             | No scope guard exists.                                             |
| S04-MECH-007      | `test_issue_planning.py::test_mechanical_failure_never_falls_back_to_semantic`                           | Zero/multiple match and budget failure call no backend and create no ZIP.                                              | No lane implementation exists.                                     |
| S04-CHAIN-001     | `test_issue_planning_chatgpt_transport.py::test_create_to_archive_review_fake_chain`                     | S03 create output feeds exact archive Review and produces external Review evidence.                                    | Current integration stops at Candidate creation.                   |
| S04-CHAIN-002     | `test_issue_planning_chatgpt_transport.py::test_git_bound_review_fake_chain`                             | Synchronized exact HEAD and canonical targets produce bound Review evidence.                                           | No git-bound Review chain exists.                                  |
| S04-CHAIN-003     | `test_issue_planning_chatgpt_transport.py::test_semantic_revise_to_fresh_review_chain`                   | Failed Review → selected Semantic revision → new Candidate → distinct Reviewer call.                                   | No revision or fresh re-Review chain exists.                       |
| S04-CHAIN-004     | `test_issue_planning_chatgpt_transport.py::test_mechanical_revise_to_fresh_review_chain`                 | Blocking Review → Mechanical revision → N+1 Candidate → distinct Reviewer call.                                        | No Mechanical or re-Review chain exists.                           |

Existing S01 verdict, Review-byte, selected-finding, closed-schema, and result-pair tests remain regression tests rather than being copied into this S04 matrix.

---

## 7. Ordered implementation sequence

### Step 1 — exact source and diff guard

Record:

```bash
git rev-parse HEAD
git branch --show-current
git status --short
```

Required starting identity:

```text
branch = iss-00334-implement-chatgpt-issue-planning-workflow
HEAD   = 18006b779c70cdb13e4e5baae29ac3d79e77a954
```

Stop on any pre-existing change outside the allowlist.

### Step 2 — Red tests and minimal typed seams

Add the S04 tests first.

If imports would otherwise fail, introduce only minimal typed symbols or sentinel unimplemented behavior. The recorded Red run must contain assertion failures for the missing S04 behavior, not collection failures.

Do not modify parser, commands, `UseCases`, or domain request schemas to make tests convenient.

### Step 3 — Candidate read path and vN value generalization

Implement:

* verified Candidate loading;
* exact observed filename/SHA reconstruction;
* source-control reconstruction;
* `build_candidate_material(version=1)`;
* generalized vN naming validation;
* exact three-document payload rendering;
* Mechanical body replacement and byte-cost helper.

Run Candidate domain/infra tests and all S03 Candidate/profile regressions before continuing.

### Step 4 — S04 Prompt and exact attachment transport

Add:

* `PlanningPromptAttachment`;
* Review Prompt synthesis;
* Semantic revision Prompt synthesis;
* `revision-prompt.md`;
* strict Reviewer result instructions;
* exact-byte prompt-pack writer support.

Keep existing S02 `synthesize_issue_planning_prompt()` output and existing text attachments byte-for-byte compatible for current fixtures.

Run Prompt, backend capture, and ChatGPT transport regressions.

### Step 5 — Review artifact presentation and publication

Implement:

* deterministic summary renderer;
* safe external Review-result input/output guards;
* owned temporary Review evidence directory;
* two-file atomic no-replace publication;
* safe relative output keys.

No Review backend orchestration yet.

### Step 6 — archive and git-bound Review orchestration

Implement `run_issue_planning_review()`:

1. request closure;
2. target resolution;
3. initial preflight;
4. exact identity;
5. exact target/supplemental Prompt;
6. fresh Reviewer invocation;
7. strict result parsing and identity comparison;
8. Candidate/repository post-guards;
9. atomic evidence publication;
10. `ok/review_completed`.

Close archive/git-bound positives and mutation negatives before revision work.

### Step 7 — exact revision evidence and Semantic lane

Add `PlanningRevisionEvidenceInput` and exact Review loader.

Implement Semantic validation by delegating to the existing closed-domain validator, then run the self-contained Planner invocation and existing S03 publication path.

Do not add a session argument, Review registry, or public CLI field.

### Step 8 — Mechanical lane

Implement:

* exact Review eligibility gate;
* target-body-only unique replacement;
* UTF-8 bytes-touched budget;
* no fallback;
* complete payload rendering;
* N+1 publication.

Prove every Mechanical rejection has backend count zero.

### Step 9 — fake chains and complete regression

Close:

* create→archive Review;
* git-bound Review;
* Semantic revise→fresh Review;
* Mechanical revise→fresh Review;
* P2/P3 no-revision path;
* no PASS inheritance.

Then run static, SpecDock, diff, and allowlist gates.

---

## 8. Verification commands

### Red-first and focused Green lane

```bash
uv run pytest \
  tests/unit/domain/test_issue_planning_candidate.py \
  tests/unit/application/test_issue_planning.py \
  tests/unit/application/test_issue_planning_prompt.py \
  tests/unit/infra/test_issue_planning_candidate.py \
  tests/unit/infra/test_issue_planning_chatgpt.py \
  tests/unit/infra/test_issue_planning_review.py \
  tests/unit/presentation/test_issue_planning.py \
  tests/integration/test_issue_planning_chatgpt_transport.py
```

Record the initial behavioral Red result, then rerun the same command to Green.

### S01 closed-contract and public-surface regression

```bash
uv run pytest \
  tests/unit/domain/test_issue_planning_contracts.py \
  tests/unit/commands/test_issue_planning.py \
  tests/cli_runtime/test_chatgpt_cli.py \
  tests/unit/presentation/test_issue_planning.py
```

The parser/help and command tests must remain unchanged and Green.

### S02 transport/security regression

```bash
uv run pytest \
  tests/unit/application/test_issue_planning_prompt.py \
  tests/unit/infra/test_issue_planning_chatgpt.py \
  tests/unit/authoring_pack/test_backend_invoke_capture.py \
  tests/integration/test_issue_planning_chatgpt_transport.py
```

### S03 Candidate and generic archive regression

```bash
uv run pytest \
  tests/unit/domain/test_issue_planning_candidate.py \
  tests/unit/infra/test_issue_planning_candidate.py \
  tests/unit/authoring_pack/test_zip_contract_profiles.py \
  tests/unit/application/test_issue_planning.py
```

The no-profile generic `review_pack_input()` behavior must remain unchanged.

### Static checks

```bash
uv run ruff check \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/issue_planning_candidate.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_candidate.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_review.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/issue_planning.py \
  tests/unit/application/test_issue_planning.py \
  tests/unit/application/test_issue_planning_prompt.py \
  tests/unit/domain/test_issue_planning_candidate.py \
  tests/unit/infra/test_issue_planning_candidate.py \
  tests/unit/infra/test_issue_planning_chatgpt.py \
  tests/unit/infra/test_issue_planning_review.py \
  tests/unit/presentation/test_issue_planning.py \
  tests/integration/test_issue_planning_chatgpt_transport.py
```

```bash
uv run mypy \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/issue_planning_candidate.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_candidate.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_review.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/issue_planning.py
```

### SpecDock and whitespace gates

```bash
./spec-dock/scripts/spec-dock validate
git diff --check
git status --short
```

### Exact allowlist gate

```bash
python - <<'PY'
from __future__ import annotations

import subprocess

BASE = "18006b779c70cdb13e4e5baae29ac3d79e77a954"

allowed = {
    "src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/resources/reviewer-prompt.md",
    "src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/resources/revision-prompt.md",
    "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py",
    "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py",
    "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/issue_planning_candidate.py",
    "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_candidate.py",
    "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py",
    "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_review.py",
    "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/issue_planning.py",
    "tests/integration/test_issue_planning_chatgpt_transport.py",
    "tests/unit/application/test_issue_planning.py",
    "tests/unit/application/test_issue_planning_prompt.py",
    "tests/unit/domain/test_issue_planning_candidate.py",
    "tests/unit/infra/test_issue_planning_candidate.py",
    "tests/unit/infra/test_issue_planning_chatgpt.py",
    "tests/unit/infra/test_issue_planning_review.py",
    "tests/unit/presentation/test_issue_planning.py",
}

def lines(command: list[str]) -> set[str]:
    output = subprocess.check_output(command, text=True)
    return {line for line in output.splitlines() if line}

observed = lines(["git", "diff", "--name-only", BASE, "--"])
observed |= lines(["git", "ls-files", "--others", "--exclude-standard"])

unexpected = sorted(observed - allowed)
missing_from_allowlist_check = sorted(observed & allowed)

if unexpected:
    raise SystemExit("unexpected changed paths:\n" + "\n".join(unexpected))

print("allowlist pass")
for path in missing_from_allowlist_check:
    print(path)
PY
```

Do not run distribution, projection, live dogfood, apply, commit, push, or PR commands as part of the delegated S04 worker scope.

---

## 9. Stop conditions

Stop and return control to Main if any of the following occurs:

1. The starting branch or HEAD differs from the verified identity.
2. A pre-existing or worker-created change appears outside the exact allowlist.
3. S04 cannot be implemented without modifying:

   * `commands/issue_planning.py`;
   * parser/registry/bootstrap;
   * `application/contracts.py`;
   * `PlanningRevisionRequestV1`;
   * `ReviewedPlanningIdentity`;
   * `PlanningReviewResult`;
   * Candidate inventory or control-file schema.
4. A new public `--review-result`, `--session`, `--prompt`, `--target`, `--repo`, or backend option appears necessary.
5. Exact Review evidence cannot be accepted as an internal application input without directory scanning or an authority registry.
6. Mechanical revision appears to require adding finding IDs or a Review digest to its closed JSON schema.
7. Mechanical scope enforcement would require a semantic model call or automatic Semantic fallback.
8. A durable conversation/session locator, database, custom Git ref, or PASS cache appears necessary.
9. The exact Candidate ZIP cannot be passed through the existing repeated `--file` backend attachment path.
10. Existing generic authoring-pack no-profile behavior changes.
11. Candidate version N requires changing identity fields, seven-file inventory, or control schema rather than generalizing existing values.
12. Review or revision would write inside the repository, canonical Issue tree, dogfood projection, or `.assurance.json`.
13. A raw transcript, secret, credential, absolute private path, backend stream, or untrusted payload would be serialized.
14. Candidate or repository mutation cannot be detected before evidence publication.
15. S05 Human Gate/apply, canonical replacement, transaction, commit, push, or publication retry becomes necessary.
16. Any S01–S03 closed regression, static check, SpecDock validation, diff check, or allowlist gate remains failing.
17. A test failure exposes a direct contradiction in the approved S04 semantics rather than an implementation-local encoding gap.

---

## 10. Copy-ready delegation instruction

> Implement S04 Review and Revision only for `chemitaro/spec-dock` on branch `iss-00334-implement-chatgpt-issue-planning-workflow`, starting from exact HEAD `18006b779c70cdb13e4e5baae29ac3d79e77a954`. Work strictly within the 17-path allowlist in this packet. First add collecting behavioral Red tests, then implement verified Candidate loading and vN packaging, exact archive/git-bound Review inputs, strict Review-result validation and external atomic evidence, pre/post immutability guards, explicit internal `PlanningRevisionEvidenceInput`, self-contained stateless Semantic revision, and exact Mechanical revision with `len(old_utf8) + len(new_utf8)` budget. Keep `PlanningReviseRequest`, `PlanningRevisionRequestV1`, parser, commands, `UseCases`, bootstrap, generic ZIP defaults, canonical documents, dogfood projection, and all S05+ behavior unchanged. P2/P3-only Review must produce no revision and zero backend calls. Both revision lanes must preserve the old Candidate and publish N+1 only through the existing S03 packager. Run every focused, regression, static, SpecDock, diff, and allowlist command before handoff; stop immediately on any listed boundary violation.
