# Oracle Browser Transcript

Conversation: https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a69bcc4-0858-83ee-b7c6-87fda11dc61f

## Prompt

Use the repository app connected to this Project. Inspect repository chemitaro/spec-dock, branch iss-00334-implement-chatgpt-issue-planning-workflow, exact pushed HEAD 1bc4109c094137bd2b42f9f09273ac0451aaf59d. Never use the default or another branch; if exact remote identity cannot be verified, return STOP. Act as the implementation concretizer for iss-00334 S09 only. Read active Issue requirement/design/append-only plan, especially Plan sections 19, 28.1, 30.2 and related traceability; read current Report and S08 direct Oracle adapter/domain/tests; inspect provider-managed prompt resources, application/issue_planning_prompt.py, relevant contracts and focused tests. Respect the accepted design and do not propose redesign, canonical amendments, public command changes, S10 ZIP parsing/Candidate adoption, S11 projection migration, S12+, or operator-local chatgpt-use dependency. Produce one concise but implementation-complete Markdown work packet, not a patch and not a review. Include exact source identity evidence and GO/STOP; S09 goal/non-goals; repository-grounded exact production/test path allowlist; current seams to reuse; required prompt-body contract for Planner, fresh Reviewer, and Semantic Revision; exact repository/branch/HEAD and no-default fallback behavior; reference-attachment data-only split; role-specific ZIP/closed-JSON output expectations; onboarding companion prompt obligations and at least four diagram-role expectations; drift/redaction/fail-closed behavior; Red-first test matrix with concrete cases; implementation sequence; verification commands; material stop conditions; and a final bounded dev-coder instruction. Minimize diff and preserve S08/S01-S07 behavior. Work-packet review is not required.

## Answer

# iss-00334 S09 Implementation Work Packet

## 1. Source identity and admission

```text
Repository:        chemitaro/spec-dock
Branch:            iss-00334-implement-chatgpt-issue-planning-workflow
Required HEAD:     1bc4109c094137bd2b42f9f09273ac0451aaf59d
GitHub comparison: identical
Ahead / behind:   0 / 0
Default fallback: not used
Decision:          GO
```

The connected GitHub app resolved the requested branch and compared it directly with `1bc4109c094137bd2b42f9f09273ac0451aaf59d`; the result was `identical`, with zero commits ahead or behind. The exact commit was also fetched successfully.

Every repository file used below was opened with that exact commit as its `ref`. No source file was read from `main` or another branch.

The current Report closes S08 after the final fresh review found all five prior P1 findings closed, zero new P0/P1 findings, and `review_status=pass`; it explicitly identifies S09 JIT concretization as the next operation. The S08 typed-output compatibility lane is temporary until S10 and must remain intact.

**GO rationale:** the accepted S09 scope, current provider seams, and S08 handoff align without requiring a canonical amendment, public command change, or S10 implementation. S09 is explicitly limited to Prompt-body authority, exact-current-branch enforcement, reference-only attachments, role-specific output expectation, and post-run drift rejection.

This packet is execution input, not a patch, implementation review, or authority amendment.

---

## 2. S09 goal

Make the complete ChatGPT task instruction authoritative in the Oracle `--prompt` value, while limiting Oracle attachments to untrusted source or evidence data.

All formal roles must:

1. independently inspect the exact GitHub repository, current branch, and HEAD through the connected GitHub app;
2. fail closed without default-branch, other-branch, attachment-only, or memory fallback;
3. use a role-specific formal output contract;
4. preserve Human approval and Runtime adoption authority;
5. produce no Candidate, Review publication, or repository mutation when source access or post-run identity validation fails.

The accepted design represents the role-specific output contract as an explicit application-to-adapter expectation carrying either an authoring ZIP identity and inventory or the closed Reviewer JSON schema.

### Non-goals

S09 must not:

* modify Requirement, Design, append-only Plan, Report, `.assurance.json`, or parent canonical documents;
* change public `planning create|revise|review|apply` commands or CLI options;
* add a public repository, branch, HEAD, companion-path, or backend override;
* parse the authoring ZIP inventory into documents;
* connect authoring ZIP bytes to the Candidate builder;
* add companion MANIFEST, CHECKSUMS, Candidate binding, Review identity, Human decision, apply, rollback, or publication logic;
* migrate installed, wheel, sdist, fresh-init, update, or root dogfood projections;
* perform S12 PlantUML validation or issue-wide verification;
* restore legacy marker parsing as a formal output contract;
* introduce `chatgpt-use`, a personal wrapper, a personal ChatGPT Project, browser profile, absolute user path, API fallback, or arbitrary backend command;
* remove the S08 `transient_payload` compatibility lane before S10.

---

## 3. Exact writable path allowlist

### Production code and managed Prompt resources

| Path                                                                                                               | S09 responsibility                                                                                                                                                                            |
| ------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py`                    | Add the closed role/output expectation, assemble the complete Prompt body, remove legacy frames, and preserve reference indexing and sensitive-input checks.                                  |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py`                           | Pass `semantic_revision` distinctly, determine the authoring companion path once, supply the output expectation, and add missing create-side post-Oracle drift rejection.                     |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/issue_planning_contracts.py`                      | Add the closed `blocked/github_exact_branch_unavailable` invocation reason only; preserve typed outputs and S10 compatibility.                                                                |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py`                         | Accept all three formal roles, verify role/expectation consistency before spawn, remove instruction-bearing pack files, enforce expected ZIP name/root, and map exact connector hard failure. |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_oracle_artifact.py`                 | Detect the exact content-free repository-access hard-failure answer inside the existing versioned Oracle session boundary; do not expose transcript content.                                  |
| `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/resources/planner-prompt.md`            | Complete Planner role, GitHub gate, ZIP, companion, and Human-boundary fragment.                                                                                                              |
| `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/resources/reviewer-prompt.md`           | Complete fresh read-only defect-only Reviewer and closed-JSON fragment.                                                                                                                       |
| `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/resources/revision-prompt.md`           | Complete Semantic Revision replacement-ZIP fragment.                                                                                                                                          |
| `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/resources/transport-output-contract.md` | Replace the legacy frame grammar with a common Prompt-body-only formal-output and hard-failure fragment. Keep the managed filename to avoid an S11 installer-inventory change.                |

### Writable focused tests

| Path                                                      | Required coverage                                                                                                                                         |
| --------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `tests/unit/application/test_issue_planning_prompt.py`    | Complete body, role contracts, exact identity, companion obligations, diagram roles, absence of legacy frames, and deterministic synthesis.               |
| `tests/unit/application/test_issue_planning.py`           | Role routing, no-fallback result propagation, create/review/revision publication gates, and post-run drift.                                               |
| `tests/unit/domain/test_issue_planning_contracts.py`      | Closed reason/status mapping and preservation of typed-output invariants.                                                                                 |
| `tests/unit/infra/test_issue_planning_chatgpt.py`         | Captured argv Prompt, reference-only pack inventory, three roles, name/root checks, connector hard failure, cross-kind rejection, and S08 non-regression. |
| `tests/unit/infra/test_issue_planning_oracle_artifact.py` | Exact hard-failure extraction, contradictory artifacts, malformed near-matches, and content-free errors.                                                  |

All other paths are read-only for S09. In particular, do not edit Candidate modules, CLI/bootstrap, integration tests, provider projection, root `spec-dock/`, canonical documents, or Report.

---

## 4. Current seams to reuse

1. **Exact local Git preflight.** `run_issue_planning_transport` already derives the repository, current branch, upstream, local and remote HEAD, source manifest, and snapshot evidence without a default-branch fallback. Retain that authority and feed the same values into the Prompt.

2. **Pure Prompt synthesis.** `issue_planning_prompt.py` already performs bounded source reads, deterministic UTF-8 ordering, dynamic-context sensitivity checks, exact-attachment indexing, and managed-resource resolution. Do not replace it with a second composer.

3. **S08 direct Oracle adapter.** `invoke_issue_planning_chatgpt` already resolves `oracle` through `PATH`, checks Oracle 0.16.1 capabilities, uses list argv with `shell=False`, sanitizes the child environment, submits once, recovers only the same session, and returns typed Planner ZIP or Reviewer JSON snapshots.

4. **S08 typed outputs.** `OracleAuthoringZipSnapshot` and `OracleReviewJsonPayload` already keep bytes private, enforce size/SHA correspondence, and allow exactly one output authority for a passing invocation. Preserve the temporary non-serialized compatibility projection into `transient_payload`; S10 owns its removal.

5. **Versioned artifact reader.** `issue_planning_oracle_artifact.py` already owns session metadata, safe artifact selection, bounded copying, ZIP root discovery, transcript answer extraction, and content-free `OracleArtifactError`. Connector hard-failure recognition belongs inside this boundary.

6. **Existing post-run gates.** Review and Semantic Revision already recheck source state before publication. Add the corresponding missing gate to create; do not redesign the other two paths.

### Active defects S09 must remove

The current composer supports only `planner|reviewer`, emits `SPECDOCK-ISSUE-PLANNING-RESPONSE-V1`, and still appends the legacy transport frame.

The current Oracle pack also writes `prompt.md`, `expected-output-contract.md`, and `safe-output-constraints.md` beside the reference files, even though the same Prompt is already supplied by argv. These are instruction-bearing attachments and must disappear from the active pack.

---

## 5. Required implementation contract

### 5.1 Closed role and output expectation

Add an immutable application-level `PlanningOutputExpectation`, carried by `SynthesizedPlanningPrompt`. Do not add a public CLI/request field.

Its effective fields are:

```text
kind:
  authoring_zip | review_json

Authoring-only:
  logical_filename
  internal_root
  exact_inventory
  onboarding_companion_path

Reviewer-only:
  closed_json_top_level_keys
  closed_json_finding_keys
```

`SynthesizedPlanningPrompt.role` becomes:

```text
planner | semantic_revision | reviewer
```

Required role mapping:

| Role                | Output kind     |
| ------------------- | --------------- |
| `planner`           | `authoring_zip` |
| `semantic_revision` | `authoring_zip` |
| `reviewer`          | `review_json`   |

Before Oracle capability probing or process creation, reject:

* role/expectation mismatch;
* authoring expectation without all authoring fields;
* Reviewer expectation carrying ZIP fields;
* unsafe or non-relative companion path;
* duplicate or non-closed inventory;
* filename/root mismatch with the Issue ID.

Use the existing `planning_context_rejected` result for malformed internally synthesized requests. Process count must remain zero.

After Oracle returns an authoring snapshot, the adapter must compare:

```text
snapshot.expected_logical_filename == expectation.logical_filename
snapshot.internal_root              == expectation.internal_root
```

A mismatch is `rejected/oracle_artifact_rejected`.

Do not parse or validate the four ZIP entries in S09. Carry the closed inventory in the expectation and Prompt; S10 owns extraction and exact-inventory validation.

### 5.2 Runtime-selected companion path

For Planner and Semantic Revision, determine the path once from the existing operation clock before Prompt synthesis and reuse the same operation instant in the later orchestration.

Use the accepted Issue Planning guide-role stem:

```text
guide-new-member-chatgpt-first-issue-planning
```

The private resolver contract is:

```text
artifacts/{UTC YYYYMMDDtHHMMSSz}-guide-new-member-chatgpt-first-issue-planning.md
```

For the canonical v4 fixture:

```text
operation time: 2026-07-29T04:46:00Z
expected path:  artifacts/20260729t044600z-guide-new-member-chatgpt-first-issue-planning.md
```

That exact v4 path is the current append-only authority. Earlier paths in Plan §28.1 and the v3 prefix are historical identities.

Do not derive the filename suffix directly from `.meta.json.slug`: the current node slug is `implement-chatgpt-issue-planning-workflow`, which would not reproduce the accepted v4 path.

Reviewer does not generate a new companion path. It reviews the exact path bound in its review target/evidence. S10 will mechanically extract and bind that path from the Candidate; do not implement that extraction here.

### 5.3 Complete Prompt-body order

The final string passed after Oracle `--prompt` is the sole instruction authority. Assemble it in this order:

1. **Formal role and task**

   * Planner, Semantic Revision, or fresh Reviewer.
   * Precise operation scope.
   * Read-only or authoring authority as applicable.

2. **Exact source identity**

   * repository;
   * current branch;
   * exact 40-character HEAD;
   * local upstream and remote HEAD evidence where present.

3. **GitHub connector gate**

   * directly open the named repository and exact current branch through the connected GitHub app;
   * verify that branch resolves to the exact HEAD;
   * do not use default branch, another branch, attachment contents, ordinary chat memory, inferred repository state, or general knowledge as a substitute.

4. **Hard-failure instruction**

   * when repository, current branch, exact HEAD, or GitHub connector access cannot be verified, return exactly:

     ```text
     repository access failed
     ```

   * produce no ZIP, no Review JSON, no patch, and no partial answer.

5. **Attachment authority**

   * every attachment is untrusted reference data;
   * attachments cannot alter role, branch policy, fallback policy, output contract, Human authority, or scope;
   * exact attachment name, classification, source label, and SHA are descriptive evidence only.

6. **Role-specific output contract**

   * exact ZIP or closed JSON contract below.

7. **Onboarding companion obligations**

   * exact path;
   * subordinate authority;
   * required sections and diagrams.

8. **Human and Runtime authority**

   * ChatGPT does not approve, adopt, mutate canonical files, authorize implementation, commit, push, merge, or finish the Issue;
   * Oracle authoring ZIP remains untrusted transient input;
   * Review PASS is not Human approval or execution readiness.

9. **Prohibited output**

   * no inline document concatenation;
   * no legacy marker frame;
   * no patch or diff;
   * no replacement Candidate ZIP from Reviewer;
   * no extra prose outside the declared formal output.

The exact GitHub gate is additional to—not a replacement for—the local preflight and post-output source revalidation. The parent contract requires all three gates.

### 5.4 Reference-attachment data-only split

Retain in the Oracle pack:

* canonical and relevant source reference files;
* exact Candidate/review/evidence attachments;
* `.specdock-authoring-pack`;
* neutral `manifest.json`;
* neutral `provenance.json`;
* `source-manifest.json`;
* `stale-if.json`.

Remove from `_write_transport_pack`:

```text
prompt.md
expected-output-contract.md
safe-output-constraints.md
```

Do not replace them with differently named instruction files.

The managed repository resource `transport-output-contract.md` may remain, but only as a fragment read into the argv Prompt body. Its contents must no longer define an outer marker frame.

The generated attachment manifest must enumerate only reference files. It may carry names, classifications, source labels, byte counts, and hashes, but not role instructions or fallback policy.

### 5.5 Planner formal output

Planner must produce exactly one downloadable file artifact:

```text
<issue-id>-issue-planning-documents.zip
└── <issue-id>-issue-planning-documents/
    ├── requirement.md
    ├── design.md
    ├── plan.md
    └── artifacts/
        └── <exact onboarding companion filename>.md
```

For this Issue fixture:

```text
logical filename:
  iss-00334-issue-planning-documents.zip

internal root:
  iss-00334-issue-planning-documents

closed expected inventory:
  requirement.md
  design.md
  plan.md
  artifacts/20260729t044600z-guide-new-member-chatgpt-first-issue-planning.md
```

The ZIP is content-only. ChatGPT must not add MANIFEST, CHECKSUMS, Candidate ID, source-baseline controls, approval records, or a fourth canonical specification. The accepted design assigns those controls to Runtime and S10.

### 5.6 Semantic Revision formal output

Semantic Revision must:

* run as role `semantic_revision`, not as an indistinguishable Planner session;
* consume the exact prior Candidate, exact closed Review JSON, selected P0/P1 IDs, and preserve-assumption evidence as references;
* retain the same repository, branch, source HEAD, and Issue identity;
* produce one complete replacement authoring ZIP with the same four-role inventory shape;
* include all three complete canonical documents and exactly one complete companion;
* never return a patch, selected-file fragment, marker text, or in-place Candidate mutation;
* make no Human-approval or adoption claim.

A new Oracle session is required. Same-session actions remain recovery-only for that invocation.

### 5.7 Fresh Reviewer formal output

Reviewer must be:

* a fresh Oracle/ChatGPT session;
* read-only;
* defect-only;
* independently bound to the exact repository, current branch, and HEAD;
* prohibited from creating a patch, replacement ZIP, corrected documents, approval, or repository mutation.

The only normal formal output is one closed JSON object. The current Runtime contract requires exactly these top-level keys:

```json
{
  "reviewed_identity": {},
  "reviewed_identity_sha256": "<64 lowercase hex>",
  "verdict": "pass | fail",
  "findings": []
}
```

Every finding has exactly:

```json
{
  "id": "<unique>",
  "severity": "p0 | p1 | p2 | p3",
  "exact_location": "<non-empty>",
  "violated_requirement_or_contradiction": "<non-empty>",
  "concrete_impact": "<non-empty>"
}
```

`verdict` is `fail` iff at least one P0 or P1 finding exists; otherwise it is `pass`. Unknown keys and prose outside the JSON object are rejected by the existing parser.

### 5.8 Onboarding companion Prompt obligations

Planner and Semantic Revision must author a new-member guide that:

* declares itself a subordinate explanatory artifact;
* names `requirement.md`, `design.md`, and `plan.md` as the canonical authorities;
* says canonical documents prevail on contradiction;
* does not claim to be a fourth canonical specification or implementation authorization;
* explains Initiative, Epic, and Issue lineage;
* explains purpose, scope, and authority;
* explains current and target architecture;
* distinguishes provider-owned direct Oracle from reference-only operator `chatgpt-use`;
* explains authoring ZIP, Runtime Candidate, fresh Review, Human decision, managed apply, and execution-readiness gates;
* explains the exact-current-branch policy and no-fallback failure;
* reports implementation status without claiming uncompleted steps;
* explains provider authority versus installed/dogfood projection;
* covers material failure modes;
* provides a first-day checklist.

It must contain at least four valid `plantuml` fenced blocks with these distinct roles:

| Diagram role                              | Minimum required meaning                                                                                                                                                                                                       |
| ----------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **System context**                        | Human, official Skill, Runtime, provider adapter, PATH Oracle, ChatGPT, GitHub exact branch, authoring ZIP, Candidate, and canonical repository.                                                                               |
| **Responsibility and authority boundary** | Planner, fresh Reviewer, Runtime, Human, adapter, and the actions each owns or cannot perform.                                                                                                                                 |
| **Planning sequence**                     | Local preflight → adapter → PATH Oracle → fresh role → GitHub exact branch → ZIP or closed JSON → post-run drift check → Human gate. The Reviewer leg must show closed JSON returning `Reviewer → Oracle → adapter → Runtime`. |
| **Implementation roadmap**                | Historical closed work, S08 closure, S09 current scope, and remaining S10–S14 ownership without claiming future completion.                                                                                                    |

The accepted guide contract requires those four semantic diagram roles and treats the guide as a reviewed but subordinate Candidate payload.

Reviewer must report an actual defect for:

* contradiction with canonical Requirement, Design, or Plan;
* incorrect current implementation status;
* direct-Oracle, exact-branch, or Human-authority misstatement;
* missing mandatory section;
* fewer than four required diagram roles;
* invalid or materially misleading PlantUML;
* Reviewer bypass of Runtime → provider adapter → PATH Oracle;
* missing fresh exact-branch inspection;
* missing closed-JSON return path.

Style preference, optional rewording, diagram aesthetics, or an unsolicited redesign is not a defect and must not independently cause `fail`.

### 5.9 Exact-branch hard failure

Inside the versioned Oracle artifact reader:

* inspect only the terminal answer portion of the bounded transcript artifact;
* compare trimmed bytes to the exact ASCII/UTF-8 sentinel `repository access failed`;
* never serialize or expose the transcript, Prompt, private session path, or surrounding content.

Expected mapping:

```text
exact sentinel and no formal artifact:
  blocked/github_exact_branch_unavailable

sentinel plus a ZIP or other contradictory formal artifact:
  rejected/oracle_artifact_rejected

near-match, extra prose, malformed transcript, or unrecognized plain text:
  not a verified connector failure;
  continue normal artifact validation, which must end missing/rejected
```

Add `github_exact_branch_unavailable` to the closed invocation-reason set and require `status="blocked"`.

No retry may submit a second Prompt. S08 same-session recovery remains unchanged.

### 5.10 Post-Oracle drift and publication gate

Preserve the three exact-source gates:

1. local pre-invocation Git preflight;
2. fresh ChatGPT role’s GitHub exact-current-branch verification;
3. local post-output branch, HEAD, and source-manifest revalidation.

Review and Semantic Revision already have post-output checks. Add the missing create-side recheck after a passing transport result but before legacy payload parsing, Candidate construction, or publisher invocation.

For create drift, return:

```text
status: stale
reason: planning_source_stale
Candidate publication count: 0
repository mutation count: 0
```

Retain the existing command-specific stale reasons for Review and Semantic Revision.

### 5.11 Redaction and fail-closed rules

* Prompt or attachment sensitivity rejection occurs before Oracle process creation.
* Attachment name/content/SHA inconsistency occurs before Oracle process creation.
* Shell metacharacters remain literal argv Prompt content; no command-string interpolation.
* Public results contain only closed status, reason, source evidence, byte count, SHA, and content-free details.
* No raw Prompt, transcript, ZIP bytes, JSON bytes, session locator, Oracle home, private path, token, stdout, or stderr is serialized or included in exception text.
* A blocked or rejected invocation carries no typed payload.
* A role mismatch, cross-kind artifact, wrong ZIP name/root, connector failure ambiguity, or drift never falls back to legacy text, API, personal wrapper, default branch, or attachment-only continuation.

---

## 6. Red-first test matrix

| ID        | Concrete case                                                                                                                                                    | Expected result                                                                                                                                                                                                                        |
| --------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `S09-R01` | Planner Prompt synthesized for `owner/repo`, `feature/issue`, exact HEAD.                                                                                        | Prompt contains all three exact values, `@GitHub`/connected-app gate, and explicit default/other-branch prohibition.                                                                                                                   |
| `S09-R02` | Planner expectation at fixed `2026-07-29T04:46:00Z`.                                                                                                             | Exact ZIP name/root and four-entry inventory include the v4 companion path once.                                                                                                                                                       |
| `S09-R03` | Semantic Revision with prior Candidate, Review JSON, selected P1, and preserve assumption.                                                                       | Role is `semantic_revision`; complete replacement ZIP contract appears; patch and partial-file output are forbidden.                                                                                                                   |
| `S09-R04` | Reviewer Prompt synthesis.                                                                                                                                       | Fresh, read-only, defect-only, independent exact-branch gate, closed JSON keys, no replacement ZIP or approval claim.                                                                                                                  |
| `S09-R05` | Captured fake-Oracle submit for each of three roles.                                                                                                             | One Prompt-bearing submit; argv Prompt exactly equals synthesized body; role-specific output expectation matches.                                                                                                                      |
| `S09-R06` | Inspect generated Oracle pack.                                                                                                                                   | Source/evidence files and neutral metadata only; `prompt.md`, `expected-output-contract.md`, `safe-output-constraints.md`, and other instruction files are absent.                                                                     |
| `S09-R07` | Exact repository-access sentinel for Planner with no ZIP.                                                                                                        | `blocked/github_exact_branch_unavailable`; ZIP, Candidate, publisher, fallback, and duplicate submit counts are zero.                                                                                                                  |
| `S09-R08` | Exact sentinel for Reviewer instead of JSON.                                                                                                                     | Same blocked reason; no Review publication or JSON payload.                                                                                                                                                                            |
| `S09-R09` | Sentinel plus authoring ZIP, or sentinel plus another contradictory formal artifact.                                                                             | `rejected/oracle_artifact_rejected`, no payload.                                                                                                                                                                                       |
| `S09-R10` | `repository access failed: using main instead`, additional prose, or malformed transcript.                                                                       | Must not be classified as verified branch failure; missing/rejected artifact path, no publication.                                                                                                                                     |
| `S09-R11` | Default-branch-only and attachment-only continuation fixtures.                                                                                                   | Prompt requires hard failure; fake Oracle returns sentinel; formal artifact and Candidate counts remain zero.                                                                                                                          |
| `S09-R12` | Planner JSON, Reviewer ZIP, or role/expectation disagreement.                                                                                                    | Cross-kind or malformed request rejected; no fallback.                                                                                                                                                                                 |
| `S09-R13` | Correct ZIP type but wrong logical basename or wrong internal root.                                                                                              | `rejected/oracle_artifact_rejected`. Closed `(N)` download suffix remains accepted only when normalized logical name/root match.                                                                                                       |
| `S09-R14` | Companion Prompt fixture.                                                                                                                                        | Exact path, subordinate authority, canonical precedence, required sections, and all four diagram-role labels are present.                                                                                                              |
| `S09-R15` | Reviewer guide fixtures: canonical contradiction, wrong S08 status, adapter bypass, default-branch use, Human-gate weakening, missing diagram, invalid PlantUML. | Each is eligible for a concrete finding; equivalent style-only fixture does not create a blocking finding.                                                                                                                             |
| `S09-R16` | Source branch, HEAD, or manifest changes after Planner output and before create publication.                                                                     | `stale/planning_source_stale`; publisher and repository mutation counts zero.                                                                                                                                                          |
| `S09-R17` | Existing Review and Semantic Revision post-run drift fixtures.                                                                                                   | Existing stale paths remain Green and publication zero; no behavior regression.                                                                                                                                                        |
| `S09-R18` | Secret in dynamic context, private absolute path, or reference hash mismatch.                                                                                    | Oracle process count zero; result content-free.                                                                                                                                                                                        |
| `S09-R19` | Prompt contains shell metacharacters and quotes.                                                                                                                 | Literal bytes appear in the `--prompt` argv element; `shell=False`; no generated command string.                                                                                                                                       |
| `S09-R20` | Scoped production/resource scan.                                                                                                                                 | No `SPECDOCK-ISSUE-PLANNING-RESPONSE-V1`, document-marker instruction, attached output-contract instruction, personal wrapper, or `--write-output` active contract. S10-owned legacy parser may remain outside the active Prompt path. |
| `S09-R21` | S08 typed result and recovery regression.                                                                                                                        | Typed ZIP/JSON privacy, exactly-one output, single submit, same-session harvest, sanitized environment, and no serialized bytes remain Green.                                                                                          |

---

## 7. Implementation sequence

1. Add the Red tests for role/output expectation, exact path, complete Prompt body, reference-only pack, hard-failure mapping, wrong name/root, and create-side drift.

2. Add `PlanningOutputExpectation` and extend `SynthesizedPlanningPrompt.role` to the three formal roles. Enforce all role/field invariants in constructors or private builders.

3. Add the private authoring companion-path resolver. Move create’s operation-time acquisition before Prompt synthesis and call the clock exactly once. Pass the same operation time forward to the existing later operation. Reuse Semantic Revision’s existing operation instant.

4. Rewrite the four provider resources:

   * Planner authoring fragment;
   * fresh Reviewer fragment;
   * Semantic Revision fragment;
   * common Prompt-body output/hard-failure fragment.

5. Rewrite both Prompt synthesis functions to:

   * receive the explicit expectation;
   * include role, exact source, connector gate, output contract, companion obligations, and Human boundary;
   * remove outer response frames and inner-document output instructions;
   * keep deterministic attachment indexing and sensitivity checks.

6. Route Semantic Revision as `semantic_revision` through transport and adapter. Continue returning an authoring ZIP typed result.

7. Remove `prompt.md`, `expected-output-contract.md`, and `safe-output-constraints.md` from `_write_transport_pack`. Preserve source/evidence files, hashes, exact binary bytes, and neutral metadata.

8. Add bounded exact-sentinel recognition to the Oracle artifact reader. Add the closed blocked reason and adapter mapping without exposing transcript bytes.

9. Have the adapter validate role/expectation consistency before process start and authoring ZIP logical filename/internal root after snapshot.

10. Add create’s post-Oracle exact-source recheck before parsing or Candidate publication. Do not alter Candidate parsing.

11. Run the focused suites, S08 regressions, static checks, validation, active-contract scan, and clean-diff checks.

12. Return evidence to Main. Do not edit Report, commit, push, open a PR, migrate projection, or begin S10.

---

## 8. Verification commands

```bash
uv run pytest -q \
  tests/unit/application/test_issue_planning_prompt.py \
  tests/unit/application/test_issue_planning.py \
  tests/unit/domain/test_issue_planning_contracts.py \
  tests/unit/infra/test_issue_planning_chatgpt.py \
  tests/unit/infra/test_issue_planning_oracle_artifact.py

# S01-S08 and no-public-command regressions; these files are read-only in S09.
uv run pytest -q \
  tests/unit/domain/test_issue_planning_candidate.py \
  tests/unit/cli/test_cli_smoke.py

PY_CHANGED=(
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/issue_planning_contracts.py
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_oracle_artifact.py
  tests/unit/application/test_issue_planning_prompt.py
  tests/unit/application/test_issue_planning.py
  tests/unit/domain/test_issue_planning_contracts.py
  tests/unit/infra/test_issue_planning_chatgpt.py
  tests/unit/infra/test_issue_planning_oracle_artifact.py
)

uv run ruff check "${PY_CHANGED[@]}"
uv run ruff format --check "${PY_CHANGED[@]}"

uv run mypy \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/issue_planning_contracts.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_oracle_artifact.py

ACTIVE_PROMPT_PATHS=(
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py
  src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/resources/planner-prompt.md
  src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/resources/reviewer-prompt.md
  src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/resources/revision-prompt.md
  src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/resources/transport-output-contract.md
)

if rg -n \
  'SPECDOCK-ISSUE-PLANNING-(RESPONSE|DOCUMENT)-V1|--write-output|_FIXED_CHATGPT_USE|oracle-chatgpt' \
  "${ACTIVE_PROMPT_PATHS[@]}"; then
  echo "legacy active Prompt/adapter contract remains" >&2
  exit 1
fi

./spec-dock/scripts/spec-dock validate
git diff --check
git status --short
```

Do not repair the known full-suite collection failure caused by the S11-owned integration import of removed `classify_transport_frame`; the current Report explicitly assigns that migration outside S09.

---

## 9. Material stop conditions

Return `STOP` to Main without broadening the diff when any of the following occurs:

1. The working source is not the requested repository, branch, and exact HEAD before implementation begins.

2. The accepted v4 companion path cannot be reproduced without introducing a public path option, using the node’s incompatible `.meta.json.slug`, scanning artifacts, selecting “latest,” or inventing a persistent registry.

3. Oracle 0.16.1 does not expose the terminal hard-failure answer through the already bounded session metadata/transcript boundary, and recognizing connector failure would require raw stdout/stderr, browser scraping, home-wide search, Oracle modification, or a personal wrapper.

4. Exact-current-branch verification requires default branch, another branch, attachment contents, memory, local Git evidence alone, or any fallback.

5. Enforcing S09 requires parsing the four ZIP payload entries, changing Candidate controls, constructing Candidate identity, adding MANIFEST/CHECKSUMS, or adopting the guide. Those are S10.

6. Reviewer exact-path binding requires adding Candidate-derived operation binding, canonical target expansion, or public companion-path input. Those are S10.

7. Implementation requires a public command/parser/bootstrap change, arbitrary backend abstraction, API fallback, personal Project/profile/configuration, or operator-local `chatgpt-use`.

8. Provider projection, installed assets, wheel/sdist, fresh init/update, root dogfood, workflow documentation, or integration-test migration must be edited. Those are S11 or later.

9. PlantUML must become a production dependency or diagrams must be rendered/validated to close S09. Syntax validation belongs to S12; S09 only fixes the authoring and Reviewer obligation in the Prompt.

10. The S08 typed-result privacy, same-session recovery, direct argv, sanitized environment, or temporary S10 compatibility lane must be weakened.

11. The hard-failure mapping would need to store or expose raw Prompt, transcript, private path, credential, or session locator.

12. A canonical document or Report amendment appears necessary. Do not silently absorb it into implementation.

---

## 10. Assumptions and unverified claims

* Repository identity and source contents were verified through the connected GitHub app; no tests or commands were executed in a checkout during this concretization.
* The exact hard-failure sentinel is an S09 Prompt/adapter contract to be proven against the fake Oracle and the current versioned Oracle 0.16.1 session reader. If the real supported Oracle cannot surface it through that bounded boundary, the applicable stop condition must be raised.
* The accepted current guide-role stem is `issue-planning`; no claim is made here about a new cross-product naming policy.
* The uploaded `設計判断と提案.txt` discusses an unrelated exception-taxonomy design and was not used as repository evidence or S09 authority.

---

## 11. Bounded dev-coder instruction

> Work only on iss-00334 S09 at repository `chemitaro/spec-dock`, branch `iss-00334-implement-chatgpt-issue-planning-workflow`, starting from exact HEAD `1bc4109c094137bd2b42f9f09273ac0451aaf59d`. Begin with the Red cases above, edit only the writable allowlist, and implement the smallest production change that establishes complete Prompt-body authority, reference-only Oracle attachments, three closed formal roles, exact-current-branch hard failure, Planner/Semantic ZIP expectation, fresh Reviewer closed JSON, onboarding companion obligations, and pre/post source gates. Preserve the S08 direct adapter, typed-output privacy, same-session recovery, temporary S10 compatibility lane, existing public commands, Candidate behavior, and all S01–S07 behavior. Do not edit canonical documents or Report; do not implement S10/S11/S12+, projection, ZIP-to-Candidate parsing, Candidate adoption, public options, commit, push, PR, merge, or Issue closure. Return the changed-file inventory, Red-to-Green evidence, captured argv/Prompt and reference-pack inventory assertions, focused/static/validation results, stop-condition assessment, and either a bounded implementation decision note or `No material implementation decisions beyond the approved plan.`
