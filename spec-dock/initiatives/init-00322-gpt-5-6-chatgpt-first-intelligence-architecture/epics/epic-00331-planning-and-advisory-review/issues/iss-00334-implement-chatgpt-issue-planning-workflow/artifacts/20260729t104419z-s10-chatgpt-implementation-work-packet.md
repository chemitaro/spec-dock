# Oracle Browser Transcript

Conversation: https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a69d104-e27c-83e8-9613-75262f5afa68

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

Create a bounded implementation work packet for iss-00334 milestone S10 only. You MUST use the connected @GitHub app and inspect chemitaro/spec-dock current branch iss-00334-implement-chatgpt-issue-planning-workflow at exact HEAD aad5e2108b03d01c9efb506675ac58dce4845eb5. Never use the default branch or another branch; if exact repository, branch, and HEAD cannot be verified, return exactly repository access failed. Before answering, read the active Issue requirement.md, design.md, append-only plan.md, report.md, the S09 work packet and closure artifacts, and inspect current provider runtime/tests on this exact branch. S09 is closed. Concretize only Plan S10 Oracle Authoring ZIP to Existing Candidate Workflow, including the current v4 onboarding companion and the canonical GitBoundOperationBindingV1 closed schema. Respect existing architecture and decisions; do not amend canonical specs, redesign public command families, or propose optional improvements. Required S10 outcomes: validate and extract the authoring ZIP into canonical requirement.md/design.md/plan.md plus exactly one onboarding-companion; preserve logical/observed filename alias and same-stem root/archive safety/strict UTF-8/LF/closed inventory; connect typed OracleAuthoringZipSnapshot to create and Semantic Revision and remove legacy inline marker parsing from active paths; preserve Candidate ID/version/SOURCE-BASELINE/MANIFEST/CHECKSUMS/PLACEHOLDER-ORACLE-MAP and existing atomic publication; include companion role/path/SHA in Candidate and formal Review; derive one closed GitBoundOperationBindingV1 with top-level repository and branch, source_head, candidate_identity, onboarding_companion path/SHA, and canonical binding_sha256; keep canonical three-path tuple unchanged; require the same Candidate for git-bound Review and apply without scanning/latest/manual target; bind Review and Human decision to the same operation binding; write/rollback the companion only after Human approval while keeping three canonical documents byte-identical in git-bound mode; preserve archive mode, mechanical revision Oracle-call zero, transaction recovery, publication retry, privacy, single submit, exact source gates, and S01-S09 behavior. Include the GB-OB positive/negative fixtures and guide validation obligations from the append-only Plan. Explicit exclusions: S11 provider projection/dogfood sync/distribution/test migration, S12 full verification/live dogfood, S13/S14, docs beyond S10-managed contract, PlantUML executable product dependency, operator-local chatgpt-use or Oracle source changes. Produce one Markdown work packet in the response, not a patch or repository change. It must contain: exact source GO/STOP evidence; goal/non-goals; current code seams to reuse; the smallest exact writable production/resource/test allowlist; explicit read-only/excluded paths; domain/application/infra data-flow and ownership; closed schemas and canonical serialization bytes; Red-first test matrix with IDs covering positive, all fail-closed cases, archive/git-bound/mechanical/regression; implementation sequence; exact verification commands; material stop conditions; decision notes only where current code forces a bounded S10 choice; Report evidence checklist; and a final copy-ready dev-coder instruction. Keep the plan implementable by one bounded subagent and do not move S11 work into S10. This work packet itself does not require review.

## Answer

# S10 Bounded Implementation Work Packet

**Oracle Authoring ZIP to Existing Candidate Workflow**

## 0. Disposition

**GO**

| Source gate                                   | Verified observation                                                                                                 |
| --------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| Repository                                    | `chemitaro/spec-dock`                                                                                                |
| Current branch                                | `iss-00334-implement-chatgpt-issue-planning-workflow`                                                                |
| Required exact HEAD                           | `aad5e2108b03d01c9efb506675ac58dce4845eb5`                                                                           |
| Branch-to-HEAD comparison                     | GitHub connector returned `identical`, ahead `0`, behind `0`                                                         |
| Default/other branch used                     | No                                                                                                                   |
| S09 status                                    | Closed; the recorded closure review reports the S09 defect closed, no new P0/P1, and names S10 as the next activity. |
| Repository mutation performed for this packet | None                                                                                                                 |
| Test execution performed for this packet      | None; all commands below are implementation verification obligations, not claimed results                            |

The active Issue requires ZIP-only Planner and Semantic Revision output, exactly three canonical documents plus one onboarding companion, preservation of the existing Candidate and adoption boundaries, and a Candidate-derived git-bound operation binding without expanding the canonical target tuple.

---

## 1. S10 goal

Implement only the runtime and focused-test changes needed to:

1. Consume `OracleAuthoringZipSnapshot` directly in `planning create` and Semantic Revision.
2. Validate and extract exactly:

   * `requirement.md`
   * `design.md`
   * `plan.md`
   * one exact `artifacts/<expected-guide>.md`
3. Remove legacy marker-framed/inline payload processing from active production paths.
4. Package the four payload files into the existing deterministic immutable Candidate with the existing four controls.
5. Give the companion the MANIFEST role `onboarding-companion`, cover it through CHECKSUMS, and expose its verified path/SHA as Candidate-derived evidence.
6. Derive one closed `GitBoundOperationBindingV1`.
7. Require the same explicitly supplied Candidate for git-bound Review and apply.
8. Bind git-bound Review and Human decision to that exact binding.
9. Write the companion only after an approved Human decision:

   * archive mode: canonical three documents plus companion;
   * git-bound mode: companion only, while all three canonical document blobs remain byte-identical.
10. Extend the existing transaction, rollback, interrupted-operation recovery, and publication-retry machinery to cover the companion.
11. Preserve archive mode, Candidate identity/versioning, Mechanical Revision Oracle-call zero, privacy, single submission, exact-source gates, and all S01–S09 behavior.

The append-only Plan assigns these changes to S10 and requires the authoring ZIP safety negatives, Candidate zero on rejection, both revision lanes, archive/git-bound regression, PA-NF-01–10B, rollback, publication retry, and pre-Human mutation zero.

---

## 2. Non-goals

The implementation must not:

* Amend any active Requirement, Design, Plan, or parent specification.
* Add or redesign a public command family.
* Add `--companion-path`, `--companion-sha`, arbitrary `--target`, a Candidate registry, a database record, a custom Git ref, or hidden session state.
* Scan an output directory, select a “latest” Candidate, infer a Candidate from timestamps, or accept manually supplied companion identity.
* Change the canonical target tuple from its existing UTF-8-byte-sorted three paths:

  * `<issue-dir>/design.md`
  * `<issue-dir>/plan.md`
  * `<issue-dir>/requirement.md`
* Change provider Prompt resources, the direct Oracle adapter, Oracle artifact discovery, Oracle itself, or operator-local `chatgpt-use`.
* Perform S11 provider projection, installed-assets synchronization, wheel/sdist work, fresh init/update migration, dogfood projection, or distribution-test migration.
* Perform S12 live dogfood, full defect review, external PlantUML `-checkonly`, or complete verification.
* Perform S13/S14 commit/push/final-review work.
* Add PlantUML as a shipped product dependency.
* Implement semantic contradiction detection in deterministic runtime code. Contradiction and status correctness remain formal Reviewer responsibilities.
* Repair the two recorded S11-owned full-lane failures: provider/dogfood projection parity and the obsolete `classify_transport_frame` integration import.

The Plan explicitly reserves provider/projection/distribution parity for S11 and external PlantUML/full verification for S12.

---

## 3. Current code seams to reuse

### 3.1 Typed Oracle result contract

`OracleAuthoringZipSnapshot` already owns the expected and observed filenames, internal root, size, SHA-256, and private ZIP bytes. `PlanningInvocationResult` already admits typed authoring ZIP or Review JSON outputs, although it still exposes a temporary legacy `transient_payload` compatibility view.

**Reuse:** the typed objects and their size/SHA checks.
**S10 change:** remove the legacy compatibility field and migrate every active application consumer to `authoring_zip` or `review_json`.

### 3.2 Existing Prompt contract

The provider runtime already derives:

```text
<issue-id>-issue-planning-documents.zip
<issue-id>-issue-planning-documents/
```

and supplies an exact four-path inventory containing the three documents and the operation-derived companion path.

**Reuse unchanged:** `application/issue_planning_prompt.py` and its resources.

### 3.3 Existing Candidate pipeline

The Candidate domain already owns:

* canonical document front-matter validation and normalization;
* Candidate ID/version/logical filename/internal-root derivation;
* `SOURCE-BASELINE.json`;
* `MANIFEST.json`;
* `CHECKSUMS.sha256`;
* `PLACEHOLDER-ORACLE-MAP.json`;
* deterministic Candidate material;
* cross-file validation.

It currently assumes a fixed seven-path inventory and still has the marker parser/renderer.

The infra Candidate adapter already supplies bounded immutable reads, safe archive review, deterministic ZIP construction, and atomic no-replace publication.

**Reuse:** all identity, control, deterministic ZIP, and publication mechanics.
**S10 change:** make the payload inventory companion-aware and add safe authoring-ZIP extraction.

### 3.4 Existing Review/Human identity chain

`PlanningReviewResult` binds the exact `ReviewedPlanningIdentity` object and digest. `PlanningHumanDecisionV1` reparses the exact Review bytes and requires the same reviewed object and digest.

**Reuse unchanged:** the Review-to-Human raw-byte and identity binding mechanism.
**S10 change:** extend the git-bound identity variant with `git_bound_operation_binding`.

### 3.5 Existing apply transaction

`PlanningApplyOperation` already derives a deterministic operation ID from canonical operation-core bytes and carries Review, Human, Candidate, canonical-target, and pre-apply blob evidence.

The existing transaction already has:

* exact HEAD/branch and target-staleness gates;
* raw index snapshots;
* managed-state snapshots;
* regular-file snapshots with absent-file representation;
* decision artifact writing;
* canonical replacement;
* validation/sync;
* scoped staging and commit;
* rollback;
* interrupted-operation recovery;
* publication retry.

The transaction currently snapshots and mutates only the three canonical targets and the Human decision artifact.

**Reuse:** the same transaction, evidence directory, operation identity, recovery, and retry machinery.
**S10 change:** add one independently identified companion target and its prior-state snapshot.

### 3.6 Existing CLI option

`--candidate` already exists for both Review and apply parsers, but current mode validation describes it as archive-only and rejects it in git-bound mode.

**Reuse:** the option and request fields.
**S10 change:** require it for git-bound Review/apply; do not add a new option.

---

## 4. Exact writable allowlist

No new files are required.

### 4.1 Production files

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/issue_planning_contracts.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/issue_planning_candidate.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/zip_contract.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_candidate.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/issue_planning.py
```

### 4.2 Resource files

```text
None.
```

The S09 provider Prompt already has the exact four-entry output expectation; changing it would be S09 redesign or S11 projection work.

### 4.3 Test files

```text
tests/unit/domain/test_issue_planning_contracts.py
tests/unit/domain/test_issue_planning_candidate.py
tests/unit/authoring_pack/test_zip_contract_profiles.py
tests/unit/application/test_issue_planning.py
tests/unit/commands/test_issue_planning.py
tests/unit/infra/test_issue_planning_candidate.py
tests/unit/infra/test_issue_planning_apply.py
tests/unit/infra/test_issue_planning_chatgpt.py
tests/integration/test_issue_planning_apply.py
```

`tests/unit/infra/test_issue_planning_chatgpt.py` is writable only to remove assertions against the temporary `transient_payload` view and replace them with typed-output assertions. Adapter implementation behavior must not change. The current S09 tests already verify that the adapter constructs typed results without supplying `transient_payload`; several failure tests still inspect the compatibility property.

---

## 5. Explicitly read-only or excluded paths

### 5.1 Canonical specifications and evidence

Read only:

```text
spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/
  epics/epic-00331-planning-and-advisory-review/
    design.md
    issues/iss-00334-implement-chatgpt-issue-planning-workflow/
      requirement.md
      design.md
      plan.md
      report.md
      artifacts/**
```

The current v4 guide at:

```text
.../artifacts/20260729t044600z-guide-new-member-chatgpt-first-issue-planning.md
```

is a positive completeness fixture, not a writable S10 document. It declares itself subordinate to the three canonical documents and contains the required architecture, lifecycle, roadmap, failure-mode, and first-day sections.

Its embedded `source_head` is historical; runtime completeness must not treat guide front matter as source authority. Candidate `SOURCE-BASELINE.json` and reviewed identity remain authoritative.

### 5.2 Provider, Oracle, and projection

Read only:

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_oracle_artifact.py
src/spec_dock/assets/install_root/.agents/**
spec-dock/.agents/**
spec-dock/scripts/**            # dogfood projection
tests/unit/application/test_issue_planning_prompt.py
tests/unit/infra/test_issue_planning_oracle_artifact.py
tests/unit/cli/test_cli_smoke.py
```

Also excluded:

```text
pyproject.toml
packaging metadata
installer/bootstrap implementation
wheel/sdist fixtures
fresh init/update fixtures
operator-local Oracle/chatgpt-use source or configuration
PlantUML binaries or product dependencies
```

---

## 6. Domain, application, and infra ownership

| Layer            | S10 ownership                                                                                                                                                    | Must not own                                                        |
| ---------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------- |
| Domain contracts | Closed binding schema; companion path/SHA value; reviewed-identity mode rules; canonical serialization/digest; typed-output-only invocation result               | ZIP filesystem access, Git mutation, directory scanning             |
| Candidate domain | Authoring expectation validation; canonical payload map; guide completeness; dynamic Candidate inventory/roles/checksums; mechanical companion target validation | Browser artifact lookup, destination writes                         |
| Application      | Mode orchestration; exact Candidate carry; source/identity equality; Review attachment selection; Human/apply gates; result reason classification                | Archive traversal internals, direct Git subprocess calls            |
| Candidate infra  | Immutable authoring snapshot review/extraction; Candidate loading; actual checksum verification; deterministic ZIP publication                                   | Review policy, Human approval                                       |
| Apply infra      | Operation-core evidence; companion destination snapshot/write/no-op; staging; rollback; recovery; commit/push retry                                              | Candidate discovery, manual target inference, semantic guide review |
| Commands         | Accept existing `--candidate` in git-bound mode and forward it                                                                                                   | Companion path/SHA options or Candidate discovery                   |

---

## 7. Required data flow

### 7.1 Create

```text
clean exact-source preflight
  -> existing Planner Prompt and direct Oracle adapter
  -> PlanningInvocationResult.authoring_zip
  -> validate expected/observed filename, root, safe exact four-file inventory
  -> extract immutable four-file payload map
  -> normalize/validate canonical documents
  -> validate companion completeness without changing its bytes
  -> build existing controls plus four payload entries
  -> deterministic Candidate ZIP
  -> atomic no-replace publication
  -> revalidated Candidate identity and companion path/SHA
  -> derive GitBoundOperationBindingV1
  -> return candidate_path, candidate_identity, binding digest, byte count
```

`transient_payload`, marker parsing, inline document framing, and a text fallback are not present in this flow.

### 7.2 Semantic Revision

```text
prior immutable Candidate + exact archive Review + selected P0/P1 findings
  -> existing Semantic Revision Prompt
  -> PlanningInvocationResult.authoring_zip
  -> validate a complete replacement four-file ZIP
  -> new operation-derived companion path
  -> Candidate version N+1
  -> old Candidate unchanged
  -> return new candidate_path, identity, binding digest
```

The new ZIP must replace all three canonical documents and the guide. It is not a patch or partial file set.

### 7.3 Mechanical Revision

```text
prior immutable Candidate
  -> no Oracle call
  -> target must be one canonical document or the exact companion path derived from that Candidate
  -> one unique literal replacement within diff budget
  -> revalidate the changed canonical document or guide
  -> package all four payload files as Candidate N+1
  -> old Candidate unchanged
```

Mechanical Revision preserves the prior companion path. It does not invent a new timestamped guide path because no new authoring run occurred.

### 7.4 Archive Review

```text
explicit Candidate path
  -> validate entire Candidate including one companion role and checksum
  -> attach exact Candidate ZIP as Review target
  -> archive ReviewedPlanningIdentity remains Candidate-identity based
  -> Candidate ZIP identity covers companion role/path/bytes
```

Archive identity remains unchanged structurally. The active Design says the Candidate identity and MANIFEST/ZIP identity cover the companion in archive mode.

### 7.5 Git-bound Review

```text
explicit --reviewed-head
explicit --candidate
  -> validate same Candidate
  -> derive operation binding
  -> verify Candidate issue/repository/branch/source_head against synchronized source
  -> read only canonical three documents from reviewed HEAD
  -> obtain only companion bytes from Candidate
  -> attach three canonical files + companion bytes as Review targets
  -> embed GitBoundOperationBindingV1 separately in ReviewedPlanningIdentity
  -> keep canonical_target_paths at exactly three
  -> after Oracle return, revalidate source and Candidate before publishing Review
```

The Candidate’s copies of `requirement.md`, `design.md`, and `plan.md` must never become git-bound canonical targets. This separation is explicit in the append-only Plan.

### 7.6 Human decision and apply

```text
review bytes + Human decision bytes + explicit same Candidate
  -> strict parse
  -> exact reviewed identity equality
  -> exact Review digest equality
  -> revalidate Candidate and rederive binding
  -> binding equality before any repository mutation
  -> exact source/pre-apply target checks
  -> approved:
       archive: replace canonical docs, write/no-op companion
       git-bound: prove canonical docs unchanged, write/no-op companion
     rejected:
       decision artifact only
  -> validate/sync
  -> scoped stage/commit/push
  -> rollback or publication retry through existing transaction
```

---

## 8. Closed contracts

### 8.1 Oracle authoring ZIP contract

For issue `iss-NNNNN`:

```text
expected logical filename:
  iss-NNNNN-issue-planning-documents.zip

accepted observed transport filename:
  iss-NNNNN-issue-planning-documents.zip
  iss-NNNNN-issue-planning-documents (N).zip
```

`N` must match `[1-9][0-9]*`. No other rename or suffix is accepted.

The internal root is always:

```text
iss-NNNNN-issue-planning-documents
```

It never includes the browser download suffix.

The exact root-relative inventory is:

```text
requirement.md
design.md
plan.md
artifacts/<operation-derived-guide-filename>.md
```

No directory entries, fourth specification, patch, control file, nested archive, or undeclared payload are accepted.

All four payloads must be:

* non-empty regular files;
* strict UTF-8;
* no UTF-8 BOM;
* no NUL;
* no CR;
* LF terminated;
* within the existing bounded archive limits;
* free of duplicate, case-fold-colliding, or NFC-colliding names.

Archive rejection must remain content-free. Details may contain only normalized finding identifiers, never raw path contents, document text, Oracle session paths, prompt material, or private diagnostics.

Suggested internal value, not a new public JSON schema:

```python
@dataclass(frozen=True)
class ValidatedIssueAuthoringPayload:
    expected_logical_filename: str
    observed_transport_filename: str
    internal_root: str
    zip_sha256: str
    zip_size_bytes: int
    documents: Mapping[str, bytes]  # exact requirement/design/plan
    onboarding_companion_path: str
    onboarding_companion_bytes: bytes
```

### 8.2 Guide completeness contract

The deterministic S10 validator must verify:

1. Exact Candidate-relative path:

   ```text
   artifacts/<expected-guide-filename>.md
   ```
2. Strict UTF-8, LF-only, final LF, no BOM/NUL, and substantive content.
3. A subordinate-authority statement identifying:

   * `requirement.md`
   * `design.md`
   * `plan.md`
   * their precedence over the guide.
4. Non-empty sections covering:

   * init/Epic/Issue lineage;
   * purpose and scope;
   * system context;
   * authority/responsibility boundary;
   * current and target architecture;
   * ChatGPT First planning lifecycle;
   * direct Oracle versus reference-only `chatgpt-use`;
   * Candidate, Review, Human, and apply lifecycle;
   * exact current-branch gates;
   * S01–S07 status;
   * S08–S14 remaining roadmap;
   * provider authority and projection;
   * failure modes;
   * first-day checklist.
5. At least four fenced blocks tagged exactly `plantuml`.
6. At least one non-empty block for each role, identified through a normalized title or role marker:

   * `system context`
   * `responsibility boundary`
   * `planning sequence`
   * `implementation roadmap`
7. Each extracted block has one `@startuml` and one terminating `@enduml`.

The current v4 guide contains the four required role blocks and the required sections and therefore serves as the positive completeness fixture.

S10 must not invoke PlantUML. Executable syntax validation remains S12.

### 8.3 Candidate inventory

The Candidate has exactly eight entries:

```text
CHECKSUMS.sha256
MANIFEST.json
PLACEHOLDER-ORACLE-MAP.json
SOURCE-BASELINE.json
artifacts/<expected-guide-filename>.md
design.md
plan.md
requirement.md
```

The actual deterministic ZIP order is UTF-8-byte order.

MANIFEST roles are:

| Path                          | Role                             |
| ----------------------------- | -------------------------------- |
| `CHECKSUMS.sha256`            | existing control role            |
| `MANIFEST.json`               | existing control role            |
| `PLACEHOLDER-ORACLE-MAP.json` | existing control role            |
| `SOURCE-BASELINE.json`        | existing control role            |
| `requirement.md`              | existing canonical-document role |
| `design.md`                   | existing canonical-document role |
| `plan.md`                     | existing canonical-document role |
| exact companion path          | `onboarding-companion`           |

Constraints:

* Exactly one MANIFEST entry has role `onboarding-companion`.
* Its path is exactly the one validated from the authoring operation.
* Its declared checksum in `CHECKSUMS.sha256` equals the SHA-256 of actual bytes.
* No unmanifested file exists.
* No MANIFEST entry lacks a corresponding archive file.
* No checksum line is missing, duplicated, or extra.
* `PLACEHOLDER-ORACLE-MAP.json` remains document-only; the companion is static unless a later canonical amendment says otherwise.
* Candidate ID, version, logical/observed Candidate filenames, Candidate internal root, source repository/branch/HEAD, and Candidate ZIP SHA retain their existing semantics.

### 8.4 `SOURCE-BASELINE.json`

Do not rename, remove, or add keys merely to record the authoring ZIP.

For create and Semantic Revision:

```text
planner_payload_sha256 = SHA-256 of exact Oracle authoring ZIP bytes
planner_payload_size   = length of exact Oracle authoring ZIP bytes
```

For Mechanical Revision:

* copy the preceding Candidate’s `planner_payload_sha256` and `planner_payload_size`;
* do not synthesize marker bytes;
* do not imply that a new Oracle payload existed.

All other source-baseline semantics remain unchanged.

### 8.5 `GitBoundOperationBindingV1`

Closed top-level schema:

```json
{
  "schema_version": 1,
  "issue_id": "iss-NNNNN",
  "repository": "owner/repository",
  "branch": "exact-current-branch",
  "source_head": "40-lowercase-hex",
  "candidate_identity": {
    "issue_id": "iss-NNNNN",
    "candidate_id": "...",
    "version": 1,
    "logical_filename": "...zip",
    "observed_transport_filename": "...zip",
    "internal_root": "...",
    "source_repository": "owner/repository",
    "source_branch": "exact-current-branch",
    "source_head": "40-lowercase-hex",
    "zip_sha256": "64-lowercase-hex"
  },
  "onboarding_companion": {
    "path": "artifacts/<exact-guide>.md",
    "sha256": "64-lowercase-hex"
  },
  "binding_sha256": "64-lowercase-hex"
}
```

Required equalities:

```text
binding.issue_id
  == candidate_identity.issue_id
  == reviewed_identity.issue_id

binding.repository
  == candidate_identity.source_repository
  == reviewed_identity.repository

binding.branch
  == candidate_identity.source_branch
  == reviewed_identity.branch

binding.source_head
  == candidate_identity.source_head
  == reviewed_identity.source_head
  == reviewed_head
```

The companion path is Candidate-relative and must have exactly two components:

```text
artifacts/<safe-markdown-filename>
```

At apply time, it is resolved beneath the canonical Issue directory. It is not a full repository path and is not a fourth canonical target.

Reject:

* top-level `source_repository`;
* top-level `source_branch`;
* both naming families;
* aliases;
* unknown keys;
* value mismatches;
* noncanonical digests;
* a Candidate path field inside the binding.

These key and equality requirements are fixed by the latest append-only amendment.

### 8.6 Canonical serialization

For `binding_sha256`:

```python
json.dumps(
    object_without_binding_sha256,
    ensure_ascii=False,
    sort_keys=True,
    separators=(",", ":"),
    allow_nan=False,
).encode("utf-8")
```

There is **no trailing LF**.

The following fixture fixes the implementation bytes. The line shown in each code block is one physical JSON line; the newline used by Markdown to terminate the code block is not part of the fixture.

Preimage, 888 bytes:

```json
{"branch":"feature/issue","candidate_identity":{"candidate_id":"iss-00003-v1-20260729t120000z","internal_root":"20260729t120000z-iss-00003-issue-planning-candidate-v1","issue_id":"iss-00003","logical_filename":"20260729t120000z-iss-00003-issue-planning-candidate-v1.zip","observed_transport_filename":"20260729t120000z-iss-00003-issue-planning-candidate-v1.zip","source_branch":"feature/issue","source_head":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","source_repository":"owner/repo","version":1,"zip_sha256":"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"},"issue_id":"iss-00003","onboarding_companion":{"path":"artifacts/20260729t120000z-guide-new-member-chatgpt-first-issue-planning.md","sha256":"cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"},"repository":"owner/repo","schema_version":1,"source_head":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"}
```

Expected digest:

```text
fa3640fd9a5aaab6f261297a94bece94845e8749c2acb497ccd3568c74e91ad1
```

Full binding serialization, 972 bytes:

```json
{"binding_sha256":"fa3640fd9a5aaab6f261297a94bece94845e8749c2acb497ccd3568c74e91ad1","branch":"feature/issue","candidate_identity":{"candidate_id":"iss-00003-v1-20260729t120000z","internal_root":"20260729t120000z-iss-00003-issue-planning-candidate-v1","issue_id":"iss-00003","logical_filename":"20260729t120000z-iss-00003-issue-planning-candidate-v1.zip","observed_transport_filename":"20260729t120000z-iss-00003-issue-planning-candidate-v1.zip","source_branch":"feature/issue","source_head":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","source_repository":"owner/repo","version":1,"zip_sha256":"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"},"issue_id":"iss-00003","onboarding_companion":{"path":"artifacts/20260729t120000z-guide-new-member-chatgpt-first-issue-planning.md","sha256":"cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"},"repository":"owner/repo","schema_version":1,"source_head":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"}
```

Candidate control JSON continues using its existing canonical representation, including its existing terminal LF. Do not reuse the Candidate-control serializer for binding preimage bytes.

### 8.7 Reviewed identity variants

Archive mode:

```text
mode
issue_id
repository
branch
source_head
candidate_identity
```

Git-bound mode:

```text
mode
issue_id
repository
branch
source_head
canonical_target_paths     # exactly the existing three paths
git_bound_operation_binding
```

Rules:

* Archive mode forbids canonical paths and operation binding.
* Git-bound mode forbids top-level `candidate_identity`.
* Git-bound mode requires the closed binding.
* Canonical target paths remain the exact three byte-sorted paths.
* `ReviewedPlanningIdentity.sha256` covers the full nested binding.
* Review and Human decision carry exactly the same identity object and identity digest.
* Apply rederives the binding from the explicitly supplied Candidate rather than trusting the serialized object alone.

### 8.8 Structured result and reason contract

Successful create/revise output adds only:

```json
{
  "candidate_path": "<verified external Candidate path>",
  "candidate_identity": {},
  "git_bound_operation_binding_sha256": "<sha256>",
  "zip_byte_count": 0
}
```

`candidate_path` is:

* success output only;
* never part of Candidate identity, reviewed identity, binding, operation ID, error detail, or diagnostic repr;
* the actual external file that the official Skill will later pass as `--candidate`.

Required classifications:

| Condition                                                                        | Result                                                           |
| -------------------------------------------------------------------------------- | ---------------------------------------------------------------- |
| Invalid authoring ZIP content/inventory                                          | `rejected/archive_rejected`                                      |
| No Candidate supplied for git-bound Review/apply                                 | `rejected/operation_candidate_required`                          |
| Candidate has zero/multiple companion roles, invalid manifest/checksum/path/blob | `rejected/operation_binding_rejected`                            |
| Candidate source/identity/binding differs from Review or Human evidence          | `rejected/operation_binding_mismatch`                            |
| Reviewed repository state or managed companion destination drifted               | `stale/apply_target_changed` or existing equivalent stale reason |
| Unsafe output/evidence path                                                      | existing content-free rejected/blocked reason                    |
| Human rejected                                                                   | decision artifact only; no canonical or companion mutation       |

---

## 9. Per-file implementation instructions

### 9.1 `domain/issue_planning_contracts.py`

1. Add closed immutable values:

   * `OnboardingCompanionBindingV1`
   * `GitBoundOperationBindingV1`
2. Implement:

   * strict construction;
   * `create(...)` deriving `binding_sha256`;
   * `from_dict(...)` with exact closed keys;
   * `to_dict()`;
   * preimage byte generation;
   * digest verification.
3. Extend `ReviewedPlanningIdentity` with:

   ```python
   git_bound_operation_binding: GitBoundOperationBindingV1 | None
   ```
4. Enforce the archive/git-bound truth table described above.
5. Validate all issue/repository/branch/HEAD equality relationships in the identity constructor.
6. Preserve the existing canonical-target tuple validation.
7. Extend `PlanningRevisionRequestV1.from_json_bytes(...)` with a nonserialized `expected_companion_path` validation input:

   * canonical files remain always permitted;
   * a companion target is permitted only when exactly equal to the Candidate-derived path;
   * arbitrary `artifacts/*.md` is not sufficient.
8. Remove `PlanningInvocationResult.transient_payload`.
9. Require:

   * Planner/Semantic pass → exactly one `authoring_zip`;
   * Reviewer pass → exactly one `review_json`;
   * blocked/rejected → neither typed output.
10. Do not change public `PlanningReviewResult` or `PlanningHumanDecisionV1` top-level schemas.

### 9.2 `domain/issue_planning_candidate.py`

1. Delete production marker constants, `parse_planner_payload`, and `render_planner_payload`.
2. Add:

   * authoring ZIP naming/alias validation;
   * exact four-payload inventory helper;
   * `ValidatedIssueAuthoringPayload`;
   * guide completeness validator;
   * dynamic `candidate_paths(companion_path)`;
   * dynamic checksum path helper;
   * Candidate companion extraction from verified files/MANIFEST.
3. Change `CandidateMaterial` to carry the exact companion path.
4. Change `build_candidate_material(...)` to accept:

   * canonical document bytes;
   * companion path and bytes;
   * exact source payload SHA/size evidence.
5. Continue applying existing canonical-document front-matter/date normalization.
6. Preserve companion bytes exactly after validation; do not rewrite its front matter or line endings.
7. Generate one MANIFEST `onboarding-companion` entry.
8. Include the companion in CHECKSUMS.
9. Keep placeholder authority document-only.
10. Update `verify_issue_candidate_files(...)` to:

    * derive exactly one companion role;
    * derive the expected eight-file inventory;
    * validate role/path/checksum/actual bytes;
    * reject missing, duplicate, extra, or unmanifested guide entries.
11. Generalize Mechanical Revision over the four-file payload map:

    * canonical target → existing document parser/completeness validation;
    * exact companion target → guide completeness validation;
    * all other targets → reject.
12. Preserve old Candidate immutability and Candidate N+1 semantics.

### 9.3 `domain/authoring_pack/zip_contract.py`

Keep default generic archive behavior unchanged.

Add only the named profile support needed for:

```python
issue_authoring_v1_profile(
    expected_root: str,
    expected_companion_path: str,
    cross_file_validator: ...
)
```

and extend the existing Candidate profile so its required paths are supplied from the verified companion path.

Use the existing safety machinery for:

* exact root;
* exact inventory;
* duplicate/case-fold/NFC collision;
* unsafe path;
* encrypted/symlink/special/executable entries;
* nested archive;
* suffix;
* entry/total sizes;
* entry/total compression ratio;
* unreadable/CRC failure;
* strict text decoding.

The current profile implementation already centralizes these checks.

Do not alter the unprofiled `review_pack_input` contract.

### 9.4 `infra/issue_planning_candidate.py`

1. Add a bounded loader for `OracleAuthoringZipSnapshot`.
2. Validate expected/observed filename relation before extraction.
3. Review the immutable snapshot bytes through the named four-entry profile.
4. Extract only after the safety profile passes.
5. Return a domain `ValidatedIssueAuthoringPayload`.
6. Never expose the original Oracle/session artifact path.
7. Normalize all archive exceptions to content-free findings.
8. Update Candidate publication validation to supply the dynamic companion path.
9. Update Candidate loading:

   * bounded immutable ZIP snapshot;
   * derive the sole possible extra payload path from archive names without extracting it;
   * run the full eight-entry profile;
   * parse MANIFEST and CHECKSUMS;
   * expose verified companion path, SHA, and bytes.
10. Extend `VerifiedIssueCandidate` with an immutable companion value.
11. Extend `PublishedCandidate` with the actual external Candidate path and verified companion identity.
12. Keep deterministic ZIP parameters and atomic no-replace publication unchanged.

### 9.5 `application/issue_planning.py`

#### Create

* Require `transport.authoring_zip`.
* Reject absent/wrong typed authority.
* Call the new authoring loader.
* Build/publish Candidate.
* Derive binding from the published identity and companion.
* Return path, Candidate identity, binding digest, and byte count.
* Remove all marker/inline processing.

#### Semantic Revision

* Require `transport.authoring_zip`.
* Use the new operation-time guide path.
* Build a complete N+1 Candidate.
* Return the same structured fields as create.
* Preserve prior Candidate bytes and path.

#### Mechanical Revision

* Load the exact companion path from prior Candidate.
* Pass that path to `PlanningRevisionRequestV1` validation.
* Do not call transport/backend.
* Preserve the companion path.
* Apply the literal edit to a canonical document or that exact companion.
* Preserve prior authoring-payload SHA/size baseline fields.
* Build N+1 through the same four-payload Candidate builder.

#### Review

* Archive:

  * existing Candidate requirement remains;
  * entire Candidate remains exact Review target.
* Git-bound:

  * `candidate_path` and `reviewed_head` are both required;
  * load Candidate before invoking Reviewer;
  * derive binding;
  * attach canonical documents read from synchronized source;
  * attach companion bytes from Candidate;
  * embed binding separately in reviewed identity;
  * revalidate Candidate and source after Oracle return and before publication.
* Require `transport.review_json`, not a legacy byte view.
* Parse Review with `target.canonical_issue_paths` supplied as the expected tuple; do not recover expected targets from untrusted Review JSON.

#### Apply

* Require a Candidate in both modes.
* Archive keeps existing logical filename and ZIP SHA option checks.
* Git-bound forbids archive-only logical/SHA options.
* Load Candidate once as an immutable snapshot.
* Rederive binding before accepting Review/Human evidence.
* Rederive or reload immediately before starting the transaction; a changed external Candidate is stale/mismatched.
* Resolve the companion destination beneath the canonical Issue directory.
* Build:

  * archive approved replacements: three documents + companion;
  * git-bound approved replacement: companion only;
  * rejected replacement set: empty.
* Pass companion identity and bytes into `PlanningApplyOperation`.

### 9.6 `infra/issue_planning_apply.py`

Extend `PlanningApplyOperation` and its operation core with explicit companion evidence:

```text
candidate_identity
git_bound_operation_binding_sha256   # git-bound only
companion_target_path
companion_sha256
replacement_companion_present
```

Do not serialize raw companion bytes into `operation.json`.

Creation invariants:

* approved archive:

  * exact three canonical replacements;
  * one companion replacement.
* approved git-bound:

  * zero canonical replacements;
  * one companion replacement.
* rejected:

  * no canonical or companion replacement.
* replacement companion SHA equals the binding/checksum/actual byte SHA.
* target path is repository-relative and beneath the exact Issue `artifacts/` directory.

Before mutation:

1. Prove canonical target blob OIDs.
2. Snapshot canonical files.
3. Snapshot companion destination, including absence.
4. Reject symlink, special file, unsafe parent, or ambiguous target.
5. If the destination is a regular file:

   * exact bytes → qualified no-op;
   * different bytes → stale before mutation.
6. Snapshot decision path, managed state, and raw index.
7. Persist all prior-state evidence in the existing private transaction directory.

Mutation order:

1. Write Human decision artifact.
2. If approved archive, replace canonical documents.
3. If approved, write companion unless it is an exact-byte no-op.
4. Prove:

   * archive Candidate-to-target parity;
   * git-bound canonical three-document byte/blob identity;
   * companion Candidate-to-target parity.
5. Run existing validation/sync.
6. Stage only the computed expected paths.
7. Commit and publish through existing logic.

Rollback must restore:

* companion exact prior bytes or exact absence;
* canonical documents;
* Human decision artifact prior absence;
* managed state;
* raw index;
* HEAD/tree according to existing recovery rules.

Add companion-aware fault checkpoints without renaming existing ones, for example:

```text
after_companion_write
after_companion_parity
```

Existing recovery and publication records must continue to accept a retry only when operation-core bytes match exactly.

### 9.7 `commands/issue_planning.py`

1. Update `--candidate` help to state that it is required for archive-candidate and git-bound modes.
2. Git-bound Review:

   * accepts Candidate;
   * requires reviewed HEAD;
   * forbids archive-only fields.
3. Git-bound apply:

   * accepts Candidate;
   * requires reviewed HEAD;
   * forbids logical filename and ZIP SHA options.
4. Keep the argparse option technically optional so a missing Candidate reaches the application and returns the required structured:

   ```text
   rejected/operation_candidate_required
   ```
5. Add no options or commands.

The append-only Plan explicitly requires the existing Candidate option in both git-bound calls and prohibits companion/manual-target options or discovery.

---

## 10. Red-first test matrix

All new test function names should contain either `s10_` or `gb_ob_`, permitting an exact Red/Green selection.

### 10.1 Contract and serialization

| ID            | Red assertion                                                                                                                                     | Primary file                                         |
| ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------- |
| `S10-CT-P01`  | Canonical binding fixture produces the exact 888-byte preimage and `fa3640…1ad1` digest                                                           | `tests/unit/domain/test_issue_planning_contracts.py` |
| `S10-CT-NF01` | Unknown binding key, top-level `source_repository`, top-level `source_branch`, both families, alias, nonfinite value, or wrong digest is rejected | same                                                 |
| `S10-CT-NF02` | Repository/branch/HEAD/issue mismatch between binding, Candidate, and reviewed identity is rejected                                               | same                                                 |
| `S10-CT-NF03` | Archive identity with binding or git-bound identity without binding is rejected                                                                   | same                                                 |
| `S10-CT-NF04` | Review and Human decision with different nested operation bindings fail exact identity validation                                                 | same                                                 |
| `S10-CT-P02`  | `PlanningInvocationResult` accepts only typed role-correct output and has no `transient_payload` attribute                                        | same                                                 |
| `S10-CT-NF05` | Legacy-only bytes, dual typed outputs, cross-kind output, or payload on blocked/rejected result is rejected                                       | same                                                 |

### 10.2 Authoring ZIP and guide

| ID               | Red assertion                                                                                                                                                                          | Primary file                                              |
| ---------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------- |
| `S10-AZ-P01`     | Exact logical filename/root/four files produce a verified immutable payload map                                                                                                        | `tests/unit/infra/test_issue_planning_candidate.py`       |
| `S10-AZ-P02`     | Closed browser ` (N)` alias is accepted while internal root remains the logical stem                                                                                                   | same                                                      |
| `S10-AZ-NF01`    | Wrong basename, malformed alias, wrong root, or alias-derived root is rejected; Candidate count 0                                                                                      | same                                                      |
| `S10-AZ-NF02`    | Missing file, extra file, fourth spec, directory entry, or partial inventory is rejected                                                                                               | `tests/unit/authoring_pack/test_zip_contract_profiles.py` |
| `S10-AZ-NF03`    | Duplicate entry, case-fold collision, or NFC collision is rejected                                                                                                                     | same                                                      |
| `S10-AZ-NF04`    | Traversal, absolute/drive path, backslash, hidden component, symlink, special, executable, encrypted, or nested archive is rejected                                                    | same                                                      |
| `S10-AZ-NF05`    | Invalid UTF-8, BOM, NUL, CR, empty file, or missing terminal LF is rejected                                                                                                            | `tests/unit/domain/test_issue_planning_candidate.py`      |
| `S10-AZ-NF06`    | Entry/total size, count, compression ratio, unreadable payload, CRC corruption, or unsupported compression is rejected                                                                 | `tests/unit/authoring_pack/test_zip_contract_profiles.py` |
| `S10-AZ-NF07`    | Typed snapshot size/SHA mismatch or wrong typed authority cannot enter create/revise                                                                                                   | `tests/unit/domain/test_issue_planning_contracts.py`      |
| `S10-AZ-NF08`    | Inline marker payload or single text payload cannot create a Candidate                                                                                                                 | `tests/unit/application/test_issue_planning.py`           |
| `S10-GUIDE-P01`  | Current v4 guide satisfies deterministic completeness and four-role PlantUML presence                                                                                                  | `tests/unit/domain/test_issue_planning_candidate.py`      |
| `S10-GUIDE-NF01` | Wrong path, missing authority, missing required section, missing S-step coverage, fewer than four blocks, wrong fence tag, missing role, or unbalanced `@startuml/@enduml` is rejected | same                                                      |

### 10.3 Candidate and revision

| ID               | Red assertion                                                                                                                            | Primary file                                         |
| ---------------- | ---------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------- |
| `S10-CAND-P01`   | Candidate has exactly eight paths, one companion role, complete CHECKSUMS, and deterministic ZIP bytes                                   | `tests/unit/domain/test_issue_planning_candidate.py` |
| `S10-CAND-P02`   | Existing Candidate ID/version/logical/observed/root/source/ZIP-SHA contracts remain unchanged                                            | same                                                 |
| `S10-CAND-P03`   | `SOURCE-BASELINE` key set is unchanged and its payload hash/size describe the exact authoring ZIP                                        | same                                                 |
| `S10-CAND-P04`   | Placeholder authority remains limited to the canonical documents                                                                         | same                                                 |
| `S10-CAND-NF01`  | Zero/multiple companion roles, wrong path, missing/unmanifested guide, checksum mismatch, or actual-blob mismatch rejects Candidate load | `tests/unit/infra/test_issue_planning_candidate.py`  |
| `S10-CREATE-P01` | Typed Planner ZIP creates Candidate, returns path/identity/binding digest, and leaves tree/index/HEAD unchanged                          | `tests/unit/application/test_issue_planning.py`      |
| `S10-SEM-P01`    | Typed Semantic ZIP creates complete Candidate N+1; old Candidate remains byte-identical                                                  | same                                                 |
| `S10-MECH-P01`   | Canonical-document Mechanical Revision returns N+1 with Oracle/backend call count 0                                                      | same                                                 |
| `S10-MECH-P02`   | Exact Candidate-derived companion path is a valid Mechanical target and still has Oracle call count 0                                    | same                                                 |
| `S10-MECH-NF01`  | Different artifact path, ambiguous match, diff-budget overflow, or guide-invalidating replacement rejects with new Candidate count 0     | same                                                 |

### 10.4 Review and operation binding

Use the Plan’s exact fixture IDs and outcomes.

| ID           | Red assertion                                                                            | Expected                                                        |
| ------------ | ---------------------------------------------------------------------------------------- | --------------------------------------------------------------- |
| `GB-OB-P01`  | Create result Candidate → git-bound fresh Review → approved apply with same Candidate    | binding exact; canonical tuple unchanged; guide parity; `ready` |
| `GB-OB-NF01` | Candidate omitted from Review or apply                                                   | `rejected/operation_candidate_required`; Oracle/mutation 0      |
| `GB-OB-NF02` | Wrong Candidate, Candidate identity/SHA mismatch, source repository/branch/HEAD mismatch | `operation_binding_mismatch` or stale; mutation 0               |
| `GB-OB-NF03` | Zero/multiple companion role, wrong path, CHECKSUMS mismatch, actual SHA mismatch        | `operation_binding_rejected`; Oracle/mutation 0                 |
| `GB-OB-NF04` | Candidate replaced after Review or binding digest altered                                | apply rejected before mutation                                  |
| `GB-OB-NF05` | Directory scan/latest selection/manual companion identity/arbitrary target attempted     | no implementing code path; request/contract rejected            |

Additional Review cases:

| ID                 | Red assertion                                                                                                             | Primary file                                    |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------- |
| `S10-REV-A-P01`    | Archive Review target is the complete guide-inclusive Candidate                                                           | `tests/unit/application/test_issue_planning.py` |
| `S10-REV-G-P01`    | Git-bound Reviewer receives canonical docs from reviewed source plus companion from Candidate and exact reviewed identity | same                                            |
| `S10-REV-NF01`     | Candidate swaps or source drift after Oracle return prevent Review publication                                            | same                                            |
| `S10-REV-NF02`     | Candidate copies of canonical docs are never used as git-bound canonical Review targets                                   | same                                            |
| `S10-REV-PRIV-P01` | Review/result/repr contains no Candidate bytes, guide body, private Oracle path, prompt, or diagnostic                    | same                                            |

### 10.5 Apply, rollback, recovery, retry

| ID                | Red assertion                                                                                                        | Primary file                                     |
| ----------------- | -------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------ |
| `S10-APPLY-A-P01` | Approved archive apply writes three Candidate documents and companion in one operation                               | `tests/integration/test_issue_planning_apply.py` |
| `S10-APPLY-G-P01` | Approved git-bound apply writes companion and retains exact pre-apply bytes/blob OIDs for all three canonical docs   | same                                             |
| `S10-APPLY-G-P02` | Existing exact companion bytes are an evidence-qualified no-op; transaction still completes correctly                | same                                             |
| `S10-APPLY-R-P01` | Human rejected writes decision artifact only; documents and companion remain unchanged/absent                        | same                                             |
| `S10-APPLY-NF01`  | Existing different companion bytes return stale before repository mutation                                           | `tests/unit/application/test_issue_planning.py`  |
| `S10-APPLY-NF02`  | Symlink/special/unsafe companion destination is rejected before mutation                                             | `tests/unit/infra/test_issue_planning_apply.py`  |
| `S10-TX-RB-P01`   | Failure after companion write restores prior companion bytes, docs, decision absence, managed state, index, and HEAD | `tests/integration/test_issue_planning_apply.py` |
| `S10-TX-RB-P02`   | Failure after writing a previously absent companion restores exact absence                                           | same                                             |
| `S10-TX-REC-P01`  | Interrupted transaction recovery understands companion prior-state evidence and restores/rejects deterministically   | same                                             |
| `S10-TX-PUB-P01`  | Push failure retains local commit and retry publishes the same commit without remutation                             | same                                             |
| `S10-TX-NF01`     | Tampered companion backup, operation core, state, attempt, or publication evidence is rejected                       | `tests/unit/infra/test_issue_planning_apply.py`  |

### 10.6 Required regression

| ID                      | Obligation                                                                                                   |
| ----------------------- | ------------------------------------------------------------------------------------------------------------ |
| `S10-REG-PA-NF`         | Existing PA-NF-01 through PA-NF-10B remain Green                                                             |
| `S10-REG-ARCHIVE`       | Existing archive Review/apply behavior remains Green                                                         |
| `S10-REG-GIT`           | Existing git-bound exact-source and canonical-target gates remain Green                                      |
| `S10-REG-SINGLE-SUBMIT` | Planner/Semantic/Reviewer still submit exactly once and recover only the same session                        |
| `S10-REG-PRIVACY`       | Raw ZIP/document/guide/private paths remain absent from diagnostics and repr                                 |
| `S10-REG-SOURCE`        | Pre-invocation local gate, fresh ChatGPT exact-branch gate, and post-output local revalidation remain intact |
| `S10-REG-S01-S09`       | Focused S01–S09 suites used by the modified seams remain Green                                               |
| `S10-REG-NO-PROJECTION` | Known S11 projection/import failures remain unchanged and are not repaired                                   |

---

## 11. Implementation sequence

1. **Reverify source before editing**

   * repository;
   * current branch;
   * exact HEAD;
   * clean tracked tree/index;
   * S09 closure present.

2. **Add all S10 Red tests**

   * contracts and canonical bytes;
   * authoring ZIP;
   * current v4 guide;
   * Candidate inventory;
   * typed create/Semantic;
   * Mechanical companion target;
   * GB-OB fixtures;
   * companion transaction/rollback/retry.
   * Run the selected Red command and record exact failures.

3. **Implement domain contracts**

   * binding values;
   * reviewed identity extension;
   * typed-output-only invocation result;
   * exact Mechanical target validation.

4. **Implement authoring and Candidate domain changes**

   * delete marker parser/renderer;
   * add four-file payload and guide validation;
   * dynamic eight-file Candidate;
   * preserve controls and source baseline.

5. **Implement named ZIP profiles and infra extraction**

   * authoring snapshot extraction;
   * dynamic Candidate profile;
   * verified companion exposure;
   * published Candidate path.

6. **Migrate application create/Semantic/Reviewer**

   * typed fields only;
   * exact Review targets;
   * post-output Candidate/source revalidation.

7. **Implement same-Candidate git-bound command/application contract**

   * existing `--candidate`;
   * structured missing-Candidate rejection;
   * binding derivation/equality.

8. **Extend apply operation and transaction**

   * companion target evidence;
   * approved write/no-op;
   * git-bound canonical byte identity;
   * rollback/recovery/retry.

9. **Run focused Green**

   * resolve only S10 failures;
   * do not broaden allowlist.

10. **Run S08/S09 and transaction regressions**

    * single submit;
    * privacy;
    * source gates;
    * PA-NF;
    * recovery and retry.

11. **Run static and specification validation**

    * ruff;
    * mypy;
    * active legacy scan;
    * SpecDock validate;
    * diff checks;
    * exact allowlist check.

12. **Return evidence to Main**

    * no Report/specification/artifact edits by the bounded subagent;
    * no commit or push unless separately delegated.

---

## 12. Exact verification commands

```bash
set -euo pipefail

BASE='aad5e2108b03d01c9efb506675ac58dce4845eb5'
BRANCH='iss-00334-implement-chatgpt-issue-planning-workflow'

test "$(git rev-parse HEAD)" = "$BASE"
test "$(git branch --show-current)" = "$BRANCH"
test -z "$(git status --porcelain=v1)"
git diff --quiet
git diff --cached --quiet
```

### 12.1 Red-first selection

Run after adding tests but before changing production:

```bash
S10_TESTS=(
  tests/unit/domain/test_issue_planning_contracts.py
  tests/unit/domain/test_issue_planning_candidate.py
  tests/unit/authoring_pack/test_zip_contract_profiles.py
  tests/unit/application/test_issue_planning.py
  tests/unit/commands/test_issue_planning.py
  tests/unit/infra/test_issue_planning_candidate.py
  tests/unit/infra/test_issue_planning_apply.py
  tests/unit/infra/test_issue_planning_chatgpt.py
  tests/integration/test_issue_planning_apply.py
)

set +e
uv run pytest -q "${S10_TESTS[@]}" -k 's10_ or gb_ob_'
RED_EXIT=$?
set -e

test "$RED_EXIT" -ne 0
```

Record the exact failing IDs. Collection failure caused only by newly missing S10 symbols is acceptable for the first Red; unrelated failure is a stop condition.

### 12.2 Focused Green

```bash
uv run pytest -q "${S10_TESTS[@]}"
```

### 12.3 Read-only S08/S09/CLI regression

```bash
uv run pytest -q \
  tests/unit/application/test_issue_planning_prompt.py \
  tests/unit/infra/test_issue_planning_oracle_artifact.py \
  tests/unit/cli/test_cli_smoke.py
```

### 12.4 Static checks

```bash
PRODUCTION_CHANGED=(
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/issue_planning_contracts.py
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/issue_planning_candidate.py
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/zip_contract.py
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_candidate.py
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/issue_planning.py
)

TEST_CHANGED=(
  tests/unit/domain/test_issue_planning_contracts.py
  tests/unit/domain/test_issue_planning_candidate.py
  tests/unit/authoring_pack/test_zip_contract_profiles.py
  tests/unit/application/test_issue_planning.py
  tests/unit/commands/test_issue_planning.py
  tests/unit/infra/test_issue_planning_candidate.py
  tests/unit/infra/test_issue_planning_apply.py
  tests/unit/infra/test_issue_planning_chatgpt.py
  tests/integration/test_issue_planning_apply.py
)

uv run ruff check "${PRODUCTION_CHANGED[@]}" "${TEST_CHANGED[@]}"

uv run mypy "${PRODUCTION_CHANGED[@]}"
```

Do not run repository-wide auto-formatting to repair unrelated baseline differences. `ruff check` and `git diff --check` are required gates.

### 12.5 Active legacy-removal scan

```bash
LEGACY_ACTIVE_PATHS=(
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/issue_planning_contracts.py
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/issue_planning_candidate.py
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py
)

if rg -n \
  'parse_planner_payload|render_planner_payload|transient_payload|SPECDOCK-ISSUE-PLANNING-(RESPONSE|DOCUMENT)-V1' \
  "${LEGACY_ACTIVE_PATHS[@]}"; then
  echo 'legacy active planning payload contract remains' >&2
  exit 1
fi
```

### 12.6 Exact diff allowlist

```bash
python - "$BASE" <<'PY'
from __future__ import annotations

import subprocess
import sys

base = sys.argv[1]
allowed = {
    "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/issue_planning_contracts.py",
    "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/issue_planning_candidate.py",
    "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/zip_contract.py",
    "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py",
    "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_candidate.py",
    "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py",
    "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/issue_planning.py",
    "tests/unit/domain/test_issue_planning_contracts.py",
    "tests/unit/domain/test_issue_planning_candidate.py",
    "tests/unit/authoring_pack/test_zip_contract_profiles.py",
    "tests/unit/application/test_issue_planning.py",
    "tests/unit/commands/test_issue_planning.py",
    "tests/unit/infra/test_issue_planning_candidate.py",
    "tests/unit/infra/test_issue_planning_apply.py",
    "tests/unit/infra/test_issue_planning_chatgpt.py",
    "tests/integration/test_issue_planning_apply.py",
}

changed = {
    line
    for line in subprocess.check_output(
        ["git", "diff", "--name-only", base, "--"],
        text=True,
    ).splitlines()
    if line
}
unexpected = sorted(changed - allowed)
missing = sorted(path for path in changed if path not in allowed)

if unexpected or missing:
    print("unexpected changed paths:", *unexpected, sep="\n  ", file=sys.stderr)
    raise SystemExit(1)

print("\n".join(sorted(changed)))
PY
```

### 12.7 Read-only specification and S11 boundary checks

```bash
ISSUE_ROOT='spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00334-implement-chatgpt-issue-planning-workflow'

git diff --exit-code "$BASE" -- \
  "$ISSUE_ROOT/requirement.md" \
  "$ISSUE_ROOT/design.md" \
  "$ISSUE_ROOT/plan.md" \
  "$ISSUE_ROOT/report.md" \
  "$ISSUE_ROOT/artifacts" \
  src/spec_dock/assets/install_root/.agents \
  spec-dock/.agents \
  spec-dock/scripts
```

### 12.8 Final repository checks

```bash
./spec-dock/scripts/spec-dock validate
git diff --check
git status --short
test "$(git rev-parse HEAD)" = "$BASE"
test "$(git branch --show-current)" = "$BRANCH"
```

The bounded implementation does not commit or push. Main owns any later Report update, review evidence, Result Approval, and milestone commit.

---

## 13. Material stop conditions

Return **STOP** with evidence and do not broaden the diff when:

1. The repository, branch, or starting HEAD differs from the exact source above.
2. S09 is no longer closed at the starting source.
3. A canonical requirement cannot be implemented without amending Requirement, Design, or Plan.
4. The same Candidate cannot be explicitly passed to both git-bound Review and apply.
5. Correctness would require directory scanning, “latest” selection, manual companion path/SHA, persistent registry, database, custom Git ref, or hidden session state.
6. Correctness would require adding a companion to `canonical_target_paths`.
7. A public command or option other than accepting the existing `--candidate` would be required.
8. A provider Prompt, installed Skill/resource, projection, bootstrap, package, wheel/sdist, fresh-init/update, or dogfood change would be required.
9. The direct Oracle adapter or Oracle source would need modification.
10. Another active production consumer of `transient_payload` exists outside the production allowlist.
11. Existing Candidate control key sets would have to be renamed or expanded beyond adding the companion MANIFEST entry and checksum coverage.
12. Binding semantics would require accepting top-level `source_repository` or `source_branch`, aliases, or unknown keys.
13. Guide completeness would require shipping or executing PlantUML.
14. Companion apply cannot use the existing transaction while preserving rollback, interrupted-operation recovery, and publication retry.
15. Any path could mutate the repository before an exact Human decision is validated.
16. Git-bound apply cannot prove all three canonical document blobs remain unchanged.
17. A failure exposes raw ZIP bytes, document/guide content, Oracle session paths, prompt material, secret-like values, or private diagnostics.
18. Resolving a failure would require repairing the two known S11-owned projection/import failures.
19. Any production or test file outside the exact allowlist must change.

The Plan independently requires stopping rather than introducing Candidate discovery, pre-Human repository writes, canonical tuple expansion, or a persistent registry.

---

## 14. Bounded decision notes

These decisions fill gaps forced by current code; they are not optional redesigns.

### D1 — Binding schema version

Use integer:

```json
"schema_version": 1
```

This matches the existing `PlanningRevisionRequestV1` and `PlanningHumanDecisionV1` convention. The active canonical text fixes the key but does not provide another literal. Discovery of a conflicting active literal is a stop condition.

### D2 — Companion path coordinate system

`GitBoundOperationBindingV1.onboarding_companion.path` is the Candidate-relative path:

```text
artifacts/<guide>.md
```

Apply resolves it beneath the canonical Issue directory. It is not a repository-absolute path, Candidate filesystem path, or canonical target.

### D3 — Authoring evidence in the existing baseline

Keep the existing `planner_payload_sha256` and `planner_payload_size` keys. For typed authoring runs they describe the exact authoring ZIP. Mechanical Revision preserves the previous values.

### D4 — Semantic versus Mechanical companion path

* Create/Semantic: operation-time-derived new guide path.
* Mechanical: prior Candidate’s exact guide path.

This preserves exact authoring expectations and Mechanical Oracle-call zero.

### D5 — Guide validation boundary

Runtime performs deterministic completeness and static block-presence checks. Formal Review owns contradiction, wrong status, and authority defects. S12 owns PlantUML executable validation.

### D6 — Missing Candidate classification

The CLI forwards a missing Candidate to the application so the required structured result is produced:

```text
rejected/operation_candidate_required
```

Argparse does not terminate first with an unstructured conditional-option error.

### D7 — Create/revise Candidate path result

The verified external Candidate path is returned only as structured success output. It is deliberately excluded from Candidate identity and operation binding, as required by the Design.

---

## 15. Report evidence checklist

The bounded subagent returns these facts to Main. Main, not the subagent, updates `report.md`.

### Source and scope

* [ ] Repository, branch, and starting HEAD recorded.
* [ ] Starting tree/index clean.
* [ ] S09 closure confirmed.
* [ ] Exact changed-path set is within the 16-path allowlist.
* [ ] No resource, specification, projection, packaging, Oracle, or dogfood path changed.

### Red/Green

* [ ] Red command, exit status, and exact failing S10 IDs recorded before production changes.
* [ ] Focused nine-file Green command and count recorded.
* [ ] Read-only S08/S09/CLI regression command and count recorded.
* [ ] No new unrelated failure.
* [ ] Known S11-owned failures neither changed nor repaired.

### Authoring ZIP and guide

* [ ] Exact logical name, alias, root, and four-entry positive recorded.
* [ ] Every grouped archive fail-closed class recorded.
* [ ] Invalid authoring ZIP produces Candidate count zero.
* [ ] Inline/marker-only payload rejected.
* [ ] Current v4 guide passes deterministic completeness.
* [ ] Guide negative mutations cover authority, sections, four roles, and block framing.
* [ ] PlantUML executable was not invoked or added.

### Candidate

* [ ] Exact eight-entry inventory recorded.
* [ ] One `onboarding-companion` role recorded.
* [ ] Companion CHECKSUMS line and actual SHA equality recorded.
* [ ] Existing Candidate identity/version/logical-observed/root/source/ZIP-SHA behavior recorded.
* [ ] Existing control key sets recorded as unchanged.
* [ ] Placeholder authority remains document-only.
* [ ] Create and Semantic produce new immutable Candidates.
* [ ] Prior Candidate remains byte-identical.
* [ ] Mechanical Oracle/backend call count is zero.

### Binding and evidence

* [ ] Canonical 888-byte fixture and digest `fa3640fd…e91ad1` pass.
* [ ] Closed-key and alias negatives pass.
* [ ] Repository/branch/source identity equalities pass.
* [ ] `GB-OB-P01` and `GB-OB-NF01`–`NF05` pass.
* [ ] Same Candidate is explicitly carried; no scan/latest/manual state exists.
* [ ] Git-bound reviewed identity retains exactly three canonical paths.
* [ ] Review and Human decision contain the exact same binding-bearing identity and digest.

### Apply transaction

* [ ] Archive approved apply writes three documents and companion.
* [ ] Git-bound approved apply leaves all three canonical documents byte-identical.
* [ ] Exact existing companion is a qualified no-op.
* [ ] Different/symlink/special companion destination fails before mutation.
* [ ] Human rejected writes decision evidence only.
* [ ] Rollback restores existing companion bytes.
* [ ] Rollback restores companion absence.
* [ ] Interrupted-operation recovery covers companion evidence.
* [ ] Publication retry publishes the same retained commit.
* [ ] PA-NF-01–10B remains Green.
* [ ] Pre-Human tracked tree, raw index, HEAD, and companion destination equal baseline.

### Static and safety

* [ ] `ruff check` passes.
* [ ] focused `mypy` passes.
* [ ] active legacy scan has zero matches.
* [ ] `spec-dock validate` passes.
* [ ] `git diff --check` passes.
* [ ] Privacy, single-submit, same-session recovery, and three exact-source gates remain Green.

After implementation, the Plan requires fresh code-reviewer and QA-reviewer PASS before S10 Result Approval; that is closure work for the implementation, not a review requirement for this packet.

---

## 16. Copy-ready dev-coder instruction

```text
Implement iss-00334 milestone S10 only in repository chemitaro/spec-dock, branch
iss-00334-implement-chatgpt-issue-planning-workflow, starting from exact HEAD
aad5e2108b03d01c9efb506675ac58dce4845eb5. Reverify repository, branch, HEAD,
and clean tracked tree/index before editing. If any source gate differs, return STOP.

Use Red-first development. Write only the S10 tests in the exact test allowlist,
run the S10/GB-OB selection and record the exact Red failures, then implement only
the seven production files listed in this packet. No new files are required.

Migrate active create and Semantic Revision from the legacy transient/marker payload
to PlanningInvocationResult.authoring_zip. Migrate Reviewer consumption to
review_json. Remove transient_payload and production marker parsing/rendering.
Validate the exact authoring ZIP name, closed browser (N) alias, same-stem root,
safe exact four-file inventory, strict UTF-8/LF, and the current onboarding-guide
completeness contract. Package the three canonical documents plus exactly one
onboarding companion into the existing immutable Candidate with the existing four
control files. Preserve Candidate ID/version, logical/observed Candidate filename,
root, source binding, SOURCE-BASELINE key set, MANIFEST schema, CHECKSUMS format,
PLACEHOLDER-ORACLE-MAP authority, deterministic ZIP, and atomic no-replace
publication. The companion must have exactly one MANIFEST role
onboarding-companion and a CHECKSUMS/actual-byte SHA match.

Add closed OnboardingCompanionBindingV1 and GitBoundOperationBindingV1 domain
contracts. Use schema_version integer 1. Use only top-level repository and branch;
reject top-level source_repository/source_branch, aliases, unknown keys, and all
identity mismatches. Compute binding_sha256 from canonical UTF-8 JSON excluding
binding_sha256, ensure_ascii=false, sorted keys, comma/colon separators,
allow_nan=false, and no terminal LF. The exact fixture digest is
fa3640fd9a5aaab6f261297a94bece94845e8749c2acb497ccd3568c74e91ad1.

Require the existing --candidate option for git-bound Review and apply. Do not add
any option. Missing Candidate must reach the application and return
rejected/operation_candidate_required. Never scan directories, select latest,
accept manual companion identity, or use persistent/hidden state. Derive exactly
one binding from the validated Candidate. Git-bound Review reads the canonical
three documents only from the reviewed source HEAD and reads only the companion
bytes from the Candidate. Keep canonical_target_paths at exactly the existing
three byte-sorted paths and store the binding in the separate
git_bound_operation_binding field. Review and Human decision must bind to the same
exact reviewed identity and digest. Apply must revalidate the explicitly supplied
same Candidate and rederive the binding before mutation.

Extend the existing apply operation and transaction rather than adding another
transaction path. Archive approved apply writes the three Candidate documents and
the companion. Git-bound approved apply writes or exact-byte-no-ops the companion
and proves all three canonical documents remain byte-identical. Human rejected
writes decision evidence only. Snapshot companion prior bytes or absence, reject
different/symlink/special destinations before mutation, include companion parity
in validation/staging, and restore companion state, canonical files, managed
state, raw index, and HEAD through existing rollback/recovery semantics. Preserve
publication_pending retry behavior and the same retained commit.

Mechanical Revision must keep Oracle/backend call count zero. Permit only one of
the three canonical filenames or the exact companion path derived from the prior
Candidate. Preserve the prior companion path and authoring-payload baseline
SHA/size, validate the changed file, and package Candidate N+1 without changing
the prior Candidate.

Do not edit specifications, Report, evidence artifacts, Prompt resources, the
Oracle adapter/source, provider/installed/dogfood projections, packaging,
bootstrap, wheel/sdist, fresh init/update, or PlantUML dependencies. Do not repair
the known S11 projection/import failures. If another active transient_payload
consumer or any required change lies outside the exact allowlist, return STOP
rather than broadening the diff.

Run the exact focused, regression, static, legacy-scan, validate, diff, and
allowlist commands from this packet. Return to Main: source evidence, Red and
Green results, exact changed paths, canonical binding fixture result, guide and
archive-negative evidence, Candidate inventory/control evidence, GB-OB-P01 and
NF01-NF05 results, archive/git-bound/Mechanical results, pre-Human mutation-zero
evidence, rollback/recovery/publication-retry results, privacy/single-submit/source
gate regressions, and any material stop condition. Do not commit, push, or edit
report.md unless separately delegated.
```
