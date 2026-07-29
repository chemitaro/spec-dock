# S11 Implementation Work Packet — Provider Authority, Distribution Parity, Dogfood Projection, and Test Migration

## 1. Decision

**GO — bounded S11 implementation.**

### Source lock

| Field                         | Required value                                        |
| ----------------------------- | ----------------------------------------------------- |
| Repository                    | `chemitaro/spec-dock`                                 |
| Branch                        | `iss-00334-implement-chatgpt-issue-planning-workflow` |
| Exact source HEAD             | `7e4257955af699cbad456a53cd3be06cb2871527`            |
| Default-branch fallback       | Forbidden                                             |
| Source of repository evidence | GitHub connector snapshot inspected on 2026-07-29 JST |

The GitHub connector resolved the current branch identically to the required SHA, with ahead/behind `0/0`. No default-branch file content is used by this packet.

### GO evidence

1. The canonical S11 goal is specifically to distribute the repaired contract through provider assets, installed assets, wheel/sdist, fresh init/update, and dogfood projection, while replacing old personal-wrapper tests. Its exit gate is focused unit/integration/installer/projection Green plus provider-first parity.
2. Section 28.3 assigns the same companion contract to provider Prompt, runtime layers, CLI details, installer inventory, official Skill, workflow docs, and all distribution surfaces, while keeping personal `chatgpt-use`, Project, profile, config, and wrapper dependencies at zero.
3. S10 closed with a fresh final Review of `PASS`, zero new P0/P1 findings, and an effective 387-test focused suite. The exact-head baseline still has only two known S11-owned failures: provider/dogfood Prompt parity and the obsolete `classify_transport_frame` collection failure.
4. The provider runtime already implements the required direct PATH Oracle boundary: `shutil.which("oracle")`, resolved regular executable validation, version/capability preflight, direct argv, one prompt submission, session recovery, and typed authoring-ZIP/review-JSON collection.
5. The acceptance contract explicitly requires parity across provider, wheel, sdist, fresh init, update, and dogfood, including direct Oracle, exact-branch Prompt, reference-only attachments, ZIP plus companion, and zero personal or legacy `--write-output` dependency.

### Initial STOP evidence

There is no input-level STOP condition. The remaining failures and projection drift are explicitly assigned to S11. S11 must not reopen the already-reviewed S08–S10 runtime, Candidate, Review, Human-decision, or apply design.

---

## 2. Bounded objective

Make the already-completed direct Oracle implementation the single shipped and dogfooded Issue Planning contract.

S11 is complete only when:

* `src/spec_dock/assets/` remains the implementation authority.
* Wheel, sdist, fresh init, update, installed Skill/resources/runtime, and root dogfood projection expose the same contract and bytes.
* The official Skill and docs describe:

  * repo-local `spec-dock-chatgpt`;
  * PATH-resolved `oracle`;
  * exact current branch and HEAD verification with no default fallback;
  * Planner/Semantic Revision exactly-one authoring ZIP;
  * canonical `requirement.md`, `design.md`, `plan.md` plus exactly one onboarding companion;
  * Reviewer closed JSON;
  * the same Candidate required by git-bound Review and apply;
  * exact Human approval before managed writes.
* The installed Skill reaches the installed repo-local CLI, which reaches a fake PATH Oracle through a real subprocess boundary.
* Product code and active product resources have zero dependency on:

  * personal home paths;
  * personal `chatgpt-use` installation;
  * `oracle-chatgpt`;
  * Project/profile/host/config setup;
  * arbitrary backend command strings;
  * legacy marker frames;
  * active `--write-output`.
* The obsolete frame-classifier integration test is migrated, not repaired by restoring the classifier.
* A second official update is a byte-for-byte no-op.
* No canonical specification amendment or live dogfood is performed.

The provider/projection authority and denylist are already normative in the design. Root `spec-dock/` is generated dogfood, not an implementation surface.

---

## 3. Current exact-HEAD drift

| Surface                      | Current observation                                                                                                                                                                                   | Required S11 disposition                                                                                                                           |
| ---------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| Provider Planner resource    | `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/resources/planner-prompt.md` has the ZIP-plus-companion authoring contract.                                                | Keep as provider authority. No Prompt tuning.                                                                                                      |
| Dogfood Planner resource     | `.agents/skills/spec-dock-issue-planning/resources/planner-prompt.md` still demands the legacy three-document marker frame.                                                                           | Replace mechanically through official update; never edit by hand.                                                                                  |
| Provider transport resource  | Provider `transport-output-contract.md` describes authoring ZIP or reviewer JSON and rejects other output forms.                                                                                      | Keep unchanged unless a functional contract test proves a defect.                                                                                  |
| Dogfood transport resource   | Dogfood `transport-output-contract.md` still defines the old response and document markers.                                                                                                           | Mechanically overwrite with provider bytes.                                                                                                        |
| Provider Oracle adapter      | Current provider adapter is direct PATH Oracle and typed-output based. It does not construct a wrapper command or use `--write-output`.                                                               | Treat as read-only implementation input for S11.                                                                                                   |
| Dogfood Oracle adapter       | Root dogfood still imports the generic backend invocation path, uses `shlex`, hard-codes `/Users/iwasawayuuta/.agents/skills/chatgpt-use/scripts/oracle-chatgpt`, and retains an end-marker constant. | Mechanically replace from provider runtime.                                                                                                        |
| Provider/dogfood CLI details | Provider help requires `--candidate` for both archive and git-bound modes; dogfood still describes it as archive-only.                                                                                | Project current provider commands into dogfood.                                                                                                    |
| Official Skill               | Provider and dogfood Skill bytes currently match, but the text still presents a three-document output and does not close the direct Oracle, companion, or same-Candidate git-bound obligations.       | Update provider Skill, then project it.                                                                                                            |
| Workflow docs                | Current workflow docs state the lifecycle at a high level but do not document the completed direct PATH Oracle, typed output, companion, and same-Candidate details.                                  | Make the smallest functional documentation update.                                                                                                 |
| Top-level README             | Current command examples cover the archive path but do not state the direct Oracle prerequisite or the same-Candidate git-bound command form.                                                         | Update command reference and boundary notes.                                                                                                       |
| Transport integration        | `tests/integration/test_issue_planning_chatgpt_transport.py` imports deleted `classify_transport_frame`; its old success case manufactures the outer marker frame and extracts `transient_payload`.   | Remove the import and replace the test with typed ZIP/review-JSON integration. Never restore the classifier.                                       |
| Installed E2E                | `tests/integration/test_issue_planning_e2e.py` still creates marker payloads, monkeypatches `invoke_backend_with_capture`, asserts active `--write-output`, and writes a wrapper-style output file.   | Replace with a real fake executable on PATH plus versioned Oracle session artifacts.                                                               |
| Installer                    | Managed scaffold directories are copied from provider assets, and both repo-local runtime executables receive executable bits during init/update.                                                     | No installer implementation change expected. Prove behavior with Red-first distribution tests.                                                     |
| Package inventory            | Current package data already includes `assets/**/*` and hidden `install_root/.agents/**`.                                                                                                             | No `pyproject.toml` change expected.                                                                                                               |
| Legacy managed paths         | The current obsolete-path manifest contains no Issue Planning transport-resource path.                                                                                                                | Treat the same-path resource overwrite plus zero active references as the explicit non-active migration. Do not invent an obsolete manifest entry. |

---

## 4. Exact scope and path allowlist

### 4.1 Required writable authority paths

These are the only expected normative source edits:

```text
README.md
src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md
src/spec_dock/assets/spec_dock/docs/README.md
src/spec_dock/assets/spec_dock/docs/workflow_issue.md
```

Required content changes:

* Document `oracle` on `PATH` as the sole external product execution dependency.
* State that missing or unsupported Oracle blocks without wrapper, arbitrary backend, or API fallback.
* State exact current repository/branch/HEAD GitHub verification and no default fallback.
* State that Planner and Semantic Revision return exactly one ZIP.
* State that the ZIP has canonical three documents plus exactly one runtime-selected onboarding companion.
* State that the companion is subordinate evidence, not a fourth canonical specification.
* State that Reviewer returns closed JSON.
* State that archive and git-bound Review/apply use the exact same Candidate produced by create.
* Include current git-bound command examples with both `--candidate` and `--reviewed-head`.
* Preserve the Human-decision boundary and evidence-only status before apply.
* Describe operator-local `chatgpt-use` only as optional/reference-only and explicitly not a shipped dependency.

### 4.2 Provider resources: verification-only, no expected semantic diff

```text
src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/resources/planner-prompt.md
src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/resources/reviewer-prompt.md
src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/resources/revision-prompt.md
src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/resources/transport-output-contract.md
```

These current provider resources already carry the functional ZIP/JSON and companion contract. They are byte authorities for installation and dogfood projection.

**Do not edit them for wording, model behavior, tone, or GPT-5.6 optimization.** Any proposed semantic change to these files is a STOP requiring a separate allowlist amendment backed by a failing functional test.

### 4.3 Required writable test paths

```text
tests/unit/infra/test_init_update.py
tests/cli_runtime/test_chatgpt_cli.py
tests/integration/test_issue_planning_chatgpt_transport.py
tests/integration/test_issue_planning_e2e.py
```

Responsibilities:

| Test path                                                    | S11 ownership                                                                                                                                                                                                                                                          |
| ------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `tests/unit/infra/test_init_update.py`                       | Provider/package/install/update/dogfood byte parity; wheel and sdist inventory; stale managed target migration; update no-op; scoped product denylist; user-spec preservation. Reuse existing build/install helpers rather than creating a parallel installer harness. |
| `tests/cli_runtime/test_chatgpt_cli.py`                      | Freeze same-Candidate git-bound help and argument semantics; update direct `PlanningReviewRequest` and `PlanningApplyRequest` fixtures to include the Candidate.                                                                                                       |
| `tests/integration/test_issue_planning_chatgpt_transport.py` | Remove `classify_transport_frame`, marker-frame fixtures, and `transient_payload`; drive application integration with `OracleAuthoringZipSnapshot` and `OracleReviewJsonPayload`.                                                                                      |
| `tests/integration/test_issue_planning_e2e.py`               | Fresh init → installed Skill contract → installed repo-local CLI subprocess → fake PATH Oracle → versioned session artifact → typed ZIP/JSON → Candidate/Review/apply. Remove all wrapper monkeypatch and positive `--write-output` behavior.                          |

### 4.4 Guarded installer fallback

```text
src/spec_dock/cli.py
```

This path may change only when a newly added Red test proves one of the following:

* a current provider file is absent from wheel/sdist;
* fresh init omits a current managed asset;
* update cannot overwrite the known stale managed file;
* update cannot project a newly added current provider module;
* a distinct obsolete managed file is positively identified.

Any change must be limited to package inventory, exact managed mapping, or exact obsolete-path handling. No installer redesign, generic migration framework, or unrelated cleanup is allowed.

If all distribution tests pass with the current installer, this file must remain unchanged.

### 4.5 Append-only observational Report path

```text
spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00334-implement-chatgpt-issue-planning-workflow/report.md
```

Only append an S11 execution/result ledger after evidence exists. Do not alter historical entries or normative Requirement/Design/Plan wording.

### 4.6 Mechanical projection outputs

These paths may change only as output of:

```bash
uv run python -m spec_dock.cli update .
```

Do not edit them directly.

#### Installed Skill and resources

```text
.agents/skills/spec-dock-issue-planning/SKILL.md
.agents/skills/spec-dock-issue-planning/resources/planner-prompt.md
.agents/skills/spec-dock-issue-planning/resources/reviewer-prompt.md
.agents/skills/spec-dock-issue-planning/resources/revision-prompt.md
.agents/skills/spec-dock-issue-planning/resources/transport-output-contract.md
```

#### Dogfood docs

```text
spec-dock/docs/README.md
spec-dock/docs/workflow_issue.md
```

#### Dogfood executable/runtime parity set

```text
spec-dock/scripts/spec-dock-chatgpt
spec-dock/scripts/spec_dock_runtime/application/issue_planning.py
spec-dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py
spec-dock/scripts/spec_dock_runtime/commands/issue_planning.py
spec-dock/scripts/spec_dock_runtime/domain/authoring_pack/authority_boundary.py
spec-dock/scripts/spec_dock_runtime/domain/authoring_pack/zip_contract.py
spec-dock/scripts/spec_dock_runtime/domain/issue_planning_candidate.py
spec-dock/scripts/spec_dock_runtime/domain/issue_planning_contracts.py
spec-dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py
spec-dock/scripts/spec_dock_runtime/infra/issue_planning_candidate.py
spec-dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py
spec-dock/scripts/spec_dock_runtime/infra/issue_planning_oracle_artifact.py
```

Some entries may already match. The parity test must compare every listed path; only actual differences should appear in the final diff.

### 4.7 Read-only regression inputs

The following current provider files and tests are verification inputs, not expected S11 edits:

```text
src/spec_dock/assets/spec_dock/scripts/spec-dock-chatgpt
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/issue_planning.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/authority_boundary.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/zip_contract.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/issue_planning_candidate.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/issue_planning_contracts.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_candidate.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_oracle_artifact.py
tests/unit/application/test_issue_planning.py
tests/unit/application/test_issue_planning_apply.py
tests/unit/application/test_issue_planning_prompt.py
tests/unit/domain/test_issue_planning_candidate.py
tests/unit/domain/test_issue_planning_contracts.py
tests/unit/infra/test_issue_planning_apply.py
tests/unit/infra/test_issue_planning_candidate.py
tests/unit/infra/test_issue_planning_chatgpt.py
tests/unit/infra/test_issue_planning_oracle_artifact.py
tests/integration/test_issue_planning_apply.py
```

The current Prompt tests already require exact repository/branch/HEAD, no default fallback, ZIP name/root, the four-entry authoring inventory, and absence of legacy marker tokens.  The current Oracle unit tests already verify PATH resolution, direct argv, no `--write-output`, safe environment, typed ZIP/review JSON, and no transient payload.

---

## 5. Explicit exclusions

S11 must not include:

* S12 full-suite closure, real Oracle run, live ChatGPT dogfood, first-guide acceptance evidence, or PlantUML executable verification.
* S13/S14 delivery, final PR preparation, merge, Issue closure, or final integrated reviews.
* Any change to:

  * `requirement.md`;
  * `design.md`;
  * `plan.md`;
  * parent Epic or Initiative documents;
  * Candidate/Review/Human/apply schemas or reason codes;
  * canonical path rules;
  * Human authority;
  * direct Oracle session/recovery semantics;
  * source preflight or exact-branch design.
* Any modification to personal `chatgpt-use`, Oracle source, browser profile, Project configuration, host service, LaunchAgent, or user files.
* Restoring:

  * `classify_transport_frame`;
  * `transient_payload`;
  * response/document marker-frame parsing;
  * generic backend command invocation;
  * positive `--write-output`.
* Prompt wording, template structure, tone, model strategy, or GPT-5.6 optimization.
* New public commands, flags, aliases, environment variables, configuration files, or fallbacks.
* Optional refactors, formatting sweeps, test-framework redesign, or unrelated installer cleanup.
* Removal or rewriting of historical artifacts/report entries that mention prior wrappers.
* Direct edits to root `.agents/**` or `spec-dock/**` projection files.

S12 is the owner of full verification and new-boundary live dogfood.

---

## 6. Red-first test specification

Add or migrate tests before authority and projection changes. Capture the first failing run.

### S11-R01 — Provider/dogfood Prompt byte parity

Owner: `tests/unit/infra/test_init_update.py`

Assert exact byte equality for:

```text
SKILL.md
resources/planner-prompt.md
resources/reviewer-prompt.md
resources/revision-prompt.md
resources/transport-output-contract.md
```

Expected initial Red:

* `planner-prompt.md`;
* reviewer/revision/transport resources where stale;
* Skill semantic-contract assertion, even though current provider/dogfood Skill bytes match.

Do not normalize whitespace, line endings, or front matter before comparison.

### S11-R02 — Provider/dogfood runtime byte parity

Owner: `tests/unit/infra/test_init_update.py`

For every runtime path in §4.6, assert:

* source file exists;
* dogfood file exists after update;
* bytes match;
* executable bit is present for `spec-dock-chatgpt`;
* no generated Python cache is compared.

The test must identify an absent provider-owned file such as `issue_planning_oracle_artifact.py` as a parity failure, not silently skip it.

### S11-R03 — Wheel and sdist inventory

Owner: `tests/unit/infra/test_init_update.py`

Build both artifacts and prove they contain:

* current `spec_dock/assets/spec_dock/scripts/spec-dock-chatgpt`;
* current Issue Planning runtime modules;
* `issue_planning_oracle_artifact.py`;
* current installed Skill;
* all four Prompt resources;
* updated distributed docs.

Do not merely inspect the source tree. Test the built wheel and sdist.

### S11-R04 — Fresh wheel/sdist init parity

Owner: `tests/unit/infra/test_init_update.py`

For wheel and sdist independently:

1. install into an isolated environment;
2. create an empty external target;
3. run installed `spec-dock init <target>`;
4. compare managed files against source provider authority;
5. assert installed `spec-dock-chatgpt` is executable;
6. assert user-authored/non-managed files are absent or untouched as appropriate.

### S11-R05 — Update migration and no-op

Owner: `tests/unit/infra/test_init_update.py`

Create a target containing:

* a valid `spec-dock/initiatives/**` user file;
* stale Planner and transport resources with legacy marker text;
* stale dogfood Oracle adapter text containing the personal wrapper path and `--write-output`;
* an unrelated unmanaged file.

Run update and assert:

* all stale managed files equal provider bytes;
* user specifications and unmanaged files are preserved;
* legacy frame and wrapper content is absent from active installed surfaces;
* a second update changes no bytes and no mode bits.

Because the old transport resource occupies the same managed path, replacement plus zero active references is the required migration. Do not add an obsolete-path manifest entry unless a distinct obsolete file is actually found.

### S11-R06 — Official Skill contract

Owner: `tests/unit/infra/test_init_update.py`

Validate the source Skill, wheel-installed Skill, sdist-installed Skill, update target, and root dogfood Skill.

Each must state, without contradiction:

* `./spec-dock/scripts/spec-dock-chatgpt`;
* `oracle` resolved through PATH;
* no personal wrapper or API fallback;
* exact current branch and HEAD;
* no default branch fallback;
* Planner/Semantic Revision ZIP;
* three canonical documents plus exactly one onboarding companion;
* Reviewer JSON;
* companion subordinate authority;
* same Candidate for git-bound Review and apply;
* exact Human decision before managed writes.

Use semantic assertions for required phrases and forbidden contradictions. Do not require incidental prose identity beyond managed byte-parity surfaces.

### S11-R07 — Installed Skill → repo-local CLI → fake PATH Oracle

Owner: `tests/integration/test_issue_planning_e2e.py`

Replace the in-process monkeypatched backend with a subprocess chain:

```text
fresh init target
  → installed .agents/.../SKILL.md
  → target/spec-dock/scripts/spec-dock-chatgpt
  → shutil.which("oracle")
  → fake executable on PATH
  → versioned ORACLE_HOME_DIR/session/<id>/meta.json and artifacts
  → typed runtime output
```

The fake Oracle must:

* be a regular executable;
* answer the supported `--version`;
* expose required root help capabilities;
* expose required `session --help` recovery capabilities;
* record argv and environment externally;
* on the single prompt submission:

  * read the role/output expectation from the received prompt;
  * write one expected authoring ZIP for Planner/Semantic Revision, or one closed JSON Answer transcript for Reviewer;
  * write valid session metadata and exact size/SHA;
  * terminate successfully;
* support `session <id> --harvest --no-recover` only for explicit recovery fixtures.

Assertions:

* exactly one argv contains `--prompt`;
* `shell` mediation is impossible because a real executable is invoked;
* no argv contains `--write-output`, project/profile/host options, wrapper path, or arbitrary backend;
* API credential sentinel variables are absent from the child environment;
* prompt text contains exact repository/branch/HEAD, no-default rule, and typed output expectation;
* no instruction attachment is present.

### S11-R08 — Typed authoring ZIP and companion

Owner: `tests/integration/test_issue_planning_e2e.py`

The fake Planner must derive the dynamic expectation from the prompt and create:

```text
<expected-root>/
  requirement.md
  design.md
  plan.md
  artifacts/<exact-runtime-selected-companion>.md
```

The guide fixture must satisfy the already-completed S10 validator, including:

* subordinate-authority statement;
* required non-empty sections;
* direct Oracle/reference-only operator-tool boundary;
* exact-branch explanation;
* current/remaining roadmap;
* at least four valid fenced `plantuml` blocks representing the required diagram roles.

Assert:

* create returns `ok/candidate_created`;
* Candidate MANIFEST distinguishes three canonical roles and one `onboarding-companion` role;
* Candidate CHECKSUMS cover the guide;
* canonical target paths remain exactly three;
* no legacy marker payload is used.

Do not add a PlantUML executable invocation; that belongs to S12.

### S11-R09 — Typed Reviewer JSON

Owner: `tests/integration/test_issue_planning_e2e.py`

The fake Reviewer must read the exact reviewed identity attachment and return one JSON object with exactly:

```text
reviewed_identity
reviewed_identity_sha256
verdict
findings
```

Each finding, when present, must have only the current closed finding fields.

Assert:

* no authoring ZIP is accepted for Reviewer;
* no private prompt, transcript path, or Oracle session path is emitted in public results;
* review reaches `ok/review_completed`.

### S11-R10 — Same-Candidate git-bound chain

Owners:

```text
tests/cli_runtime/test_chatgpt_cli.py
tests/integration/test_issue_planning_e2e.py
```

Update the git-bound flow to pass the exact create-result Candidate to both:

```text
review planning --mode git-bound --candidate <same.zip> --reviewed-head <sha>
planning apply --mode git-bound --candidate <same.zip> --reviewed-head <sha> ...
```

Assert:

* missing Candidate is rejected;
* another Candidate is rejected;
* correct Candidate produces the same operation-binding digest through create, Review, Human decision, and apply;
* companion write/no-op behavior remains S10 behavior;
* canonical documents are not changed by git-bound apply;
* no repository mutation precedes Human approval.

### S11-R11 — Legacy integration migration

Owner: `tests/integration/test_issue_planning_chatgpt_transport.py`

Required migration:

* delete the `classify_transport_frame` import;
* delete or replace `test_real_outer_frame_extraction_feeds_exact_inner_candidate_grammar`;
* delete `_planner_payload` marker-frame helper;
* stop constructing `PlanningInvocationResult.transient_payload`;
* create typed `OracleAuthoringZipSnapshot` and `OracleReviewJsonPayload` fixtures;
* update payload binding to use authoring ZIP SHA and size;
* convert the old “fourth document” case into an authoring ZIP extra-entry rejection;
* preserve source-evidence binding, stale detection, semantic revision, mechanical revision, and fresh Review-chain assertions.

**Forbidden repair:** reintroducing a compatibility classifier solely to satisfy this test.

### S11-R12 — Scoped active-dependency denylist

Owner: `tests/unit/infra/test_init_update.py`

Scan active Issue Planning product surfaces in:

* source provider;
* wheel;
* sdist;
* fresh init;
* update target;
* root dogfood.

In executable/runtime paths, forbid:

```text
/Users/
.agents/skills/chatgpt-use
oracle-chatgpt
SPECDOCK_CHATGPT_COMMAND
invoke_backend_with_capture
--write-output
SPECDOCK-ISSUE-PLANNING-RESPONSE-V1
SPECDOCK-ISSUE-PLANNING-DOCUMENT-V1
```

Also forbid code or argv construction for:

```text
--project
--profile
--host
LaunchAgent
arbitrary backend command
```

Allow only:

* explanatory `chatgpt-use` references in the official Skill, functional docs, or Planner guide obligation when the same local context explicitly says `reference-only`, `operator-local`, or “not a product dependency”;
* negative-test literals;
* historical Issue report/artifact material, which must be outside the scan roots;
* the existing environment-sanitization test literal used to prove that `SPECDOCK_CHATGPT_COMMAND` is not inherited.

The test must distinguish a token mention from an executable dependency.

---

## 7. Implementation sequence

### Step 0 — Reconfirm source lock

Verify exact branch, exact HEAD, remote parity, and clean worktree. Stop immediately on mismatch.

Do not fetch, inspect, or merge the default branch as part of this work packet.

### Step 1 — Introduce the Red/migration tests

Modify test allowlist paths only.

First expected observations:

* provider/dogfood Prompt parity Red;
* dogfood direct-runtime parity Red;
* official Skill semantic-contract Red;
* obsolete frame integration test removed rather than restored;
* installed E2E no longer contains wrapper-style fake behavior.

Record which new tests are already Green because S08–S10 provider functionality exists. Do not weaken an already-Green test merely to manufacture Red.

### Step 2 — Update official authority documentation

Update only:

```text
README.md
src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md
src/spec_dock/assets/spec_dock/docs/README.md
src/spec_dock/assets/spec_dock/docs/workflow_issue.md
```

Do not touch the four provider Prompt resources. They already represent the functional contract.

### Step 3 — Project through the branch-local official installer

Run:

```bash
uv run python -m spec_dock.cli update .
```

This is the required branch-local provider projection command.

Do **not** use the repo-local self-update wrapper for this step. The documented repo-local update resolves a fixed upstream package source rather than serving as the exact-branch local projection mechanism.

Inspect the diff immediately:

* only mechanical paths in §4.6 may appear;
* any unrelated managed file change is a STOP;
* any `spec-dock/initiatives/**` change is a STOP;
* do not manually correct a generated file after update.

### Step 4 — Complete integration-test migration

Migrate the transport integration to typed snapshots and the E2E to the fake executable/session model.

Keep existing test coverage for:

* exact Git synchronization;
* source evidence;
* Candidate immutability;
* archive apply;
* git-bound apply;
* semantic revise to fresh PASS;
* forbidden repository mutation.

Remove only behavior that was specific to the retired wrapper/frame contract.

### Step 5 — Close distribution tests

Build wheel and sdist and run isolated:

* package inventory;
* fresh init;
* stale-target update;
* installed Skill/Prompt/runtime parity;
* installed fake Oracle chain;
* second-update no-op;
* denylist.

Change `src/spec_dock/cli.py` only if a concrete Red demonstrates a package/install/update omission.

### Step 6 — Run focused Green and regressions

Run the S11-focused suite, then the S09/S10 read-only regression inputs and selected Core/authoring-pack/Issue-lifecycle tests.

Do not begin S12’s full or live lanes.

### Step 7 — Enforce projection and change allowlists

* Re-run official update and prove no diff change.
* Run byte parity comparisons.
* Run changed-path allowlist validation.
* Run `git diff --check`.
* Confirm clean generated caches and no untracked distribution output.

### Step 8 — Append Report evidence and obtain S11 reviews

Append only observed results.

Before S11 Result Approval:

* implementation commit or explicitly approved no-op exists;
* exact pushed SHA is available;
* fresh code-reviewer passes;
* fresh spec-reviewer passes;
* local/remote branch parity is confirmed;
* worktree is clean.

Do not open or merge a final Delivery PR under this packet.

---

## 8. Exact verification commands

### 8.1 Source lock

```bash
set -euo pipefail

BRANCH='iss-00334-implement-chatgpt-issue-planning-workflow'
BASE='7e4257955af699cbad456a53cd3be06cb2871527'

test "$(git branch --show-current)" = "$BRANCH"
test "$(git rev-parse HEAD)" = "$BASE"
test -z "$(git status --porcelain)"

git fetch --no-tags origin "$BRANCH"
test "$(git rev-parse "refs/remotes/origin/$BRANCH")" = "$BASE"
```

### 8.2 Red-first focused run

Run after test-only migration/additions and before authority/projection changes:

```bash
uv run pytest -q \
  tests/unit/infra/test_init_update.py \
  tests/cli_runtime/test_chatgpt_cli.py \
  tests/integration/test_issue_planning_chatgpt_transport.py \
  tests/integration/test_issue_planning_e2e.py
```

Record exact collection/test failures. At least the current provider/dogfood parity drift or stale Skill contract must remain Red before source authority is changed.

### 8.3 Official dogfood projection

```bash
uv run python -m spec_dock.cli update .
```

### 8.4 Byte-parity checks

```bash
set -euo pipefail

PROVIDER_SKILL='src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning'
DOGFOOD_SKILL='.agents/skills/spec-dock-issue-planning'

cmp "$PROVIDER_SKILL/SKILL.md" "$DOGFOOD_SKILL/SKILL.md"

for name in \
  planner-prompt.md \
  reviewer-prompt.md \
  revision-prompt.md \
  transport-output-contract.md
do
  cmp "$PROVIDER_SKILL/resources/$name" "$DOGFOOD_SKILL/resources/$name"
done

for rel in \
  docs/README.md \
  docs/workflow_issue.md \
  scripts/spec-dock-chatgpt \
  scripts/spec_dock_runtime/application/issue_planning.py \
  scripts/spec_dock_runtime/application/issue_planning_prompt.py \
  scripts/spec_dock_runtime/commands/issue_planning.py \
  scripts/spec_dock_runtime/domain/authoring_pack/authority_boundary.py \
  scripts/spec_dock_runtime/domain/authoring_pack/zip_contract.py \
  scripts/spec_dock_runtime/domain/issue_planning_candidate.py \
  scripts/spec_dock_runtime/domain/issue_planning_contracts.py \
  scripts/spec_dock_runtime/infra/issue_planning_apply.py \
  scripts/spec_dock_runtime/infra/issue_planning_candidate.py \
  scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py \
  scripts/spec_dock_runtime/infra/issue_planning_oracle_artifact.py
do
  cmp "src/spec_dock/assets/spec_dock/$rel" "spec-dock/$rel"
done
```

### 8.5 Focused S11 Green

```bash
uv run pytest -q \
  tests/unit/application/test_issue_planning_prompt.py \
  tests/unit/infra/test_issue_planning_chatgpt.py \
  tests/unit/infra/test_issue_planning_oracle_artifact.py \
  tests/unit/infra/test_init_update.py \
  tests/cli_runtime/test_chatgpt_cli.py \
  tests/integration/test_issue_planning_chatgpt_transport.py \
  tests/integration/test_issue_planning_e2e.py
```

### 8.6 S09/S10 functional regression

```bash
uv run pytest -q \
  tests/unit/application/test_issue_planning.py \
  tests/unit/application/test_issue_planning_apply.py \
  tests/unit/application/test_issue_planning_prompt.py \
  tests/unit/domain/test_issue_planning_candidate.py \
  tests/unit/domain/test_issue_planning_contracts.py \
  tests/unit/infra/test_issue_planning_apply.py \
  tests/unit/infra/test_issue_planning_candidate.py \
  tests/unit/infra/test_issue_planning_chatgpt.py \
  tests/unit/infra/test_issue_planning_oracle_artifact.py \
  tests/cli_runtime/test_chatgpt_cli.py \
  tests/integration/test_issue_planning_apply.py \
  tests/integration/test_issue_planning_chatgpt_transport.py \
  tests/integration/test_issue_planning_e2e.py
```

### 8.7 Selected Core, authoring-pack, and lifecycle regression

```bash
uv run pytest -q \
  tests/unit/authoring_pack \
  tests/cli_runtime/test_delegated_authoring.py \
  tests/cli_runtime/test_issue_lifecycle.py
```

Do not expand this into the S12 full-regression or live lane.

### 8.8 Build wheel and sdist

```bash
rm -rf build dist
uv build

test -n "$(find dist -maxdepth 1 -type f -name '*.whl' -print -quit)"
test -n "$(find dist -maxdepth 1 -type f -name '*.tar.gz' -print -quit)"
```

### 8.9 Isolated wheel/sdist init and update smoke

```bash
set -euo pipefail

DIST_TMP="$(mktemp -d)"
WHEEL="$(find dist -maxdepth 1 -type f -name '*.whl' -print -quit)"
SDIST="$(find dist -maxdepth 1 -type f -name '*.tar.gz' -print -quit)"

uv venv "$DIST_TMP/wheel-venv"
uv pip install --python "$DIST_TMP/wheel-venv/bin/python" "$WHEEL"
mkdir "$DIST_TMP/wheel-target"
"$DIST_TMP/wheel-venv/bin/spec-dock" init "$DIST_TMP/wheel-target"
"$DIST_TMP/wheel-venv/bin/spec-dock" update "$DIST_TMP/wheel-target"

uv venv "$DIST_TMP/sdist-venv"
uv pip install --python "$DIST_TMP/sdist-venv/bin/python" "$SDIST"
mkdir "$DIST_TMP/sdist-target"
"$DIST_TMP/sdist-venv/bin/spec-dock" init "$DIST_TMP/sdist-target"
"$DIST_TMP/sdist-venv/bin/spec-dock" update "$DIST_TMP/sdist-target"
```

The automated `test_init_update.py` cases remain authoritative for complete byte comparisons and preservation assertions.

### 8.10 Scoped static checks

```bash
uv run ruff check \
  src/spec_dock/cli.py \
  tests/unit/infra/test_init_update.py \
  tests/cli_runtime/test_chatgpt_cli.py \
  tests/integration/test_issue_planning_chatgpt_transport.py \
  tests/integration/test_issue_planning_e2e.py

uv run ruff format --check \
  src/spec_dock/cli.py \
  tests/unit/infra/test_init_update.py \
  tests/cli_runtime/test_chatgpt_cli.py \
  tests/integration/test_issue_planning_chatgpt_transport.py \
  tests/integration/test_issue_planning_e2e.py

uv run mypy \
  src/spec_dock \
  tests/unit/infra/test_init_update.py \
  tests/cli_runtime/test_chatgpt_cli.py \
  tests/integration/test_issue_planning_chatgpt_transport.py \
  tests/integration/test_issue_planning_e2e.py

./spec-dock/scripts/spec-dock validate
git diff --check
```

### 8.11 Direct-adapter forbidden-token smoke

This supplements, but does not replace, the semantic denylist test:

```bash
set -euo pipefail

! rg -n \
  '/Users/|oracle-chatgpt|SPECDOCK_CHATGPT_COMMAND|invoke_backend_with_capture|--write-output|SPECDOCK-ISSUE-PLANNING-(RESPONSE|DOCUMENT)-V1' \
  src/spec_dock/assets/spec_dock/scripts/spec-dock-chatgpt \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_oracle_artifact.py \
  spec-dock/scripts/spec-dock-chatgpt \
  spec-dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py \
  spec-dock/scripts/spec_dock_runtime/infra/issue_planning_oracle_artifact.py
```

### 8.12 Second-update no-op

Run after the first projection and all authority edits are complete:

```bash
set -euo pipefail

BEFORE="$(mktemp)"
AFTER="$(mktemp)"

git diff --binary > "$BEFORE"
uv run python -m spec_dock.cli update .
git diff --binary > "$AFTER"

cmp "$BEFORE" "$AFTER"
```

### 8.13 Exact changed-path enforcement

```bash
python - '7e4257955af699cbad456a53cd3be06cb2871527' <<'PY'
from __future__ import annotations

import subprocess
import sys

base = sys.argv[1]

allowed = {
    "README.md",
    "src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md",
    "src/spec_dock/assets/spec_dock/docs/README.md",
    "src/spec_dock/assets/spec_dock/docs/workflow_issue.md",
    "src/spec_dock/cli.py",
    "tests/unit/infra/test_init_update.py",
    "tests/cli_runtime/test_chatgpt_cli.py",
    "tests/integration/test_issue_planning_chatgpt_transport.py",
    "tests/integration/test_issue_planning_e2e.py",
    "spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/"
    "epics/epic-00331-planning-and-advisory-review/issues/"
    "iss-00334-implement-chatgpt-issue-planning-workflow/report.md",
    ".agents/skills/spec-dock-issue-planning/SKILL.md",
    ".agents/skills/spec-dock-issue-planning/resources/planner-prompt.md",
    ".agents/skills/spec-dock-issue-planning/resources/reviewer-prompt.md",
    ".agents/skills/spec-dock-issue-planning/resources/revision-prompt.md",
    ".agents/skills/spec-dock-issue-planning/resources/transport-output-contract.md",
    "spec-dock/docs/README.md",
    "spec-dock/docs/workflow_issue.md",
    "spec-dock/scripts/spec-dock-chatgpt",
    "spec-dock/scripts/spec_dock_runtime/application/issue_planning.py",
    "spec-dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py",
    "spec-dock/scripts/spec_dock_runtime/commands/issue_planning.py",
    "spec-dock/scripts/spec_dock_runtime/domain/authoring_pack/authority_boundary.py",
    "spec-dock/scripts/spec_dock_runtime/domain/authoring_pack/zip_contract.py",
    "spec-dock/scripts/spec_dock_runtime/domain/issue_planning_candidate.py",
    "spec-dock/scripts/spec_dock_runtime/domain/issue_planning_contracts.py",
    "spec-dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py",
    "spec-dock/scripts/spec_dock_runtime/infra/issue_planning_candidate.py",
    "spec-dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py",
    "spec-dock/scripts/spec_dock_runtime/infra/issue_planning_oracle_artifact.py",
}

changed = set(
    subprocess.check_output(
        ["git", "diff", "--name-only", base, "--"],
        text=True,
    ).splitlines()
)
changed.update(
    subprocess.check_output(
        ["git", "ls-files", "--others", "--exclude-standard"],
        text=True,
    ).splitlines()
)

unexpected = sorted(changed - allowed)
if unexpected:
    raise SystemExit("unexpected S11 paths:\n" + "\n".join(unexpected))

print("S11 path allowlist: PASS")
for path in sorted(changed):
    print(path)
PY
```

If `src/spec_dock/cli.py` appears, the Report must identify the exact failing distribution test that authorized it.

---

## 9. Stop conditions

Stop without broadening implementation when any of the following occurs:

1. Branch, source HEAD, remote branch HEAD, or clean-worktree precondition fails.
2. Exact branch cannot be used without consulting another branch or default branch.
3. A Red requires changes to Requirement, Design, Plan, parent documents, Candidate schema, Review schema, Human decision, apply semantics, canonical paths, or reason codes.
4. A provider Prompt resource would need semantic wording or model tuning.
5. A provider runtime defect is discovered rather than a distribution/projection defect.
6. The solution would reintroduce:

   * `classify_transport_frame`;
   * legacy markers;
   * `transient_payload`;
   * generic backend invocation;
   * active `--write-output`.
7. The installed E2E needs a real Oracle, real browser, real ChatGPT account, network access, or personal Project/profile/host setup.
8. Official update touches:

   * `spec-dock/initiatives/**`;
   * Requirement/Design/Plan;
   * unrelated Skills;
   * unrelated docs/runtime;
   * user-authored or unmanaged files.
9. A path outside the allowlist must change.
10. Wheel, sdist, fresh init, update, and dogfood cannot be made identical through provider authority and the existing installer model.
11. A distinct obsolete legacy path is discovered that would require changing `host-adapters/meta.json`; obtain an allowlist amendment first.
12. `pyproject.toml` or packaging architecture appears to require redesign rather than a narrowly demonstrated omission.
13. A second update is not a no-op.
14. An unrelated pre-existing test or formatting failure appears; record it separately rather than expanding scope.
15. Completion would require S12 live/full verification, S13/S14 delivery, or optional cleanup.

---

## 10. Report checklist

Append an S11 section to `report.md` containing all of the following:

### Source and GO

* [ ] Repository, branch, and exact starting HEAD.
* [ ] Connector-visible branch identity and ahead/behind state.
* [ ] Clean starting worktree.
* [ ] S10 final PASS evidence referenced.
* [ ] S11-only GO decision and exclusions.

### Red evidence

* [ ] Exact Red-first command.
* [ ] Test names and exact initial failures.
* [ ] Explicit record of the provider/dogfood Prompt parity failure.
* [ ] Explicit record that obsolete `classify_transport_frame` was migrated, not restored.
* [ ] Any new test that was already Green because S08–S10 functionality pre-existed.

### Authority and projection

* [ ] Authority files changed.
* [ ] Provider Prompt resources confirmed unchanged.
* [ ] Official projection command used.
* [ ] Exact mechanical projection paths.
* [ ] Confirmation that root projection files were not hand-edited.
* [ ] Second update no-op evidence.

### Distribution

* [ ] Wheel filename and SHA-256.
* [ ] Sdist filename and SHA-256.
* [ ] Wheel package inventory result.
* [ ] Sdist package inventory result.
* [ ] Isolated wheel fresh-init result.
* [ ] Isolated sdist fresh-init result.
* [ ] Stale-target update result.
* [ ] Installed/provider/dogfood byte-parity result.
* [ ] User specification and unmanaged-file preservation result.

### Direct Oracle and typed output

* [ ] Fake executable identity and supported version fixture.
* [ ] Exact one-submit argv evidence.
* [ ] No `--write-output`.
* [ ] No personal wrapper/path/Project/profile/host/config dependency.
* [ ] Sanitized child environment result.
* [ ] Typed Planner ZIP result.
* [ ] Exact four-payload authoring inventory.
* [ ] Onboarding companion path and subordinate-authority validation.
* [ ] Typed Reviewer closed JSON result.
* [ ] Same-Candidate git-bound Review/apply result.
* [ ] Exact-branch failure fixture with Candidate/Review/mutation count zero.

### Tests and static checks

* [ ] Focused S11 counts.
* [ ] S09/S10 regression counts.
* [ ] Selected Core/authoring-pack/lifecycle counts.
* [ ] Ruff check result.
* [ ] Changed-file Ruff format result.
* [ ] Mypy result.
* [ ] SpecDock validate result and node count.
* [ ] Denylist result with explicit allowed evidence literals.
* [ ] `git diff --check`.
* [ ] Changed-path allowlist result.

### Closure

* [ ] Exact implementation commit or Human-approved no-op.
* [ ] Non-force push evidence when applicable.
* [ ] Local/remote HEAD and tree parity.
* [ ] Clean worktree.
* [ ] Fresh code-reviewer PASS on exact pushed SHA.
* [ ] Fresh spec-reviewer PASS on exact pushed SHA.
* [ ] No live dogfood or S12 acceptance claim.
* [ ] S11 Result Approval.
* [ ] Next owner recorded as S12.

---

## 11. Assumptions, uncertainty, and unverified claims

### Verified from the exact GitHub connector snapshot

* S11’s canonical ownership and exclusions.
* S10 final PASS and the two known S11-owned failures.
* Provider direct Oracle implementation.
* Provider/dogfood Prompt and runtime drift.
* Obsolete classifier import and wrapper-style E2E.
* Current package-data and installer inventory model.
* Current official Skill/docs gaps.

### Assumptions to validate through Red-first execution

* The current recursive installer and package-data configuration are sufficient without changing `src/spec_dock/cli.py`.
* Official update will touch only the listed Issue Planning projections.
* No separate obsolete transport-resource path exists beyond the same managed resource path now carrying new content.
* Existing distribution-test helpers can be extended without adding a parallel harness.

### Unverified until implementation runs

* Exact test counts after migration.
* Wheel/sdist artifact inventory.
* Fresh init and stale-target update parity.
* Second-update no-op.
* Installed subprocess E2E behavior.
* Final denylist and exact changed-path results.
* Fresh code/spec review verdicts.

---

## 12. Copy-ready bounded `dev-coder` instruction

```text
Act as the bounded dev-coder for SpecDock Issue iss-00334, Plan step S11 only.

SOURCE LOCK
- Repository: chemitaro/spec-dock
- Branch: iss-00334-implement-chatgpt-issue-planning-workflow
- Required starting HEAD: 7e4257955af699cbad456a53cd3be06cb2871527
- Verify branch, exact HEAD, origin branch equality, and clean worktree before editing.
- Never inspect, use, merge, or fall back to the default branch.
- Stop immediately if any source-lock condition fails.

GOAL
Distribute the completed S08-S10 direct PATH Oracle, exact-current-branch, typed authoring ZIP/reviewer JSON, same-Candidate git-bound, and onboarding-companion contract through:
- provider authority;
- official Skill and functional docs;
- wheel and sdist;
- fresh init and update;
- installed assets/runtime;
- root dogfood projection;
- current integration/distribution tests.

Do not redesign or tune the already-completed functional implementation.

REQUIRED WRITABLE AUTHORITY PATHS
- README.md
- src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md
- src/spec_dock/assets/spec_dock/docs/README.md
- src/spec_dock/assets/spec_dock/docs/workflow_issue.md

REQUIRED WRITABLE TEST PATHS
- tests/unit/infra/test_init_update.py
- tests/cli_runtime/test_chatgpt_cli.py
- tests/integration/test_issue_planning_chatgpt_transport.py
- tests/integration/test_issue_planning_e2e.py

GUARDED INSTALLER FALLBACK
- src/spec_dock/cli.py
This file may change only if a new Red test proves a package inventory, fresh-init, update, or exact managed-removal defect. If no such Red exists, leave it unchanged.

REPORT
- Append observed S11 evidence only to:
  spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00334-implement-chatgpt-issue-planning-workflow/report.md
- Do not change requirement.md, design.md, or plan.md.

PROVIDER RESOURCES — EXPECTED NO DIFF
- src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/resources/planner-prompt.md
- src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/resources/reviewer-prompt.md
- src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/resources/revision-prompt.md
- src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/resources/transport-output-contract.md

These are current functional authorities. Do not perform Prompt wording, template, tone, model, or GPT-5.6 tuning. Any semantic change requires STOP and an allowlist amendment backed by a failing functional test.

MECHANICAL PROJECTION
After provider Skill/docs edits, run exactly:
  uv run python -m spec_dock.cli update .

Never hand-edit:
- .agents/skills/spec-dock-issue-planning/**
- spec-dock/docs/README.md
- spec-dock/docs/workflow_issue.md
- root spec-dock/scripts Issue Planning runtime projection

Expected projection coverage includes:
- the official Skill and four resources;
- docs README and workflow_issue;
- spec-dock-chatgpt;
- current application/issue_planning.py;
- current application/issue_planning_prompt.py;
- current commands/issue_planning.py;
- current authoring_pack authority_boundary.py and zip_contract.py;
- current issue_planning_candidate.py and issue_planning_contracts.py;
- current infra issue_planning_apply.py, issue_planning_candidate.py,
  issue_planning_chatgpt.py, and issue_planning_oracle_artifact.py.

RED-FIRST REQUIREMENTS
Before authority or projection changes:
1. Add provider/package/init/update/dogfood byte-parity tests.
2. Add official Skill semantic-contract tests.
3. Add stale managed-target update and second-update no-op tests.
4. Add scoped active-product dependency denylist tests.
5. Migrate test_issue_planning_chatgpt_transport.py away from
   classify_transport_frame, marker frames, and transient_payload.
6. Replace test_issue_planning_e2e.py’s invoke_backend_with_capture monkeypatch,
   marker payloads, and positive --write-output behavior with a real fake
   executable on PATH and versioned Oracle session artifacts.
7. Update CLI fixtures so git-bound Review and apply both receive the exact
   create-result Candidate.

FAKE ORACLE E2E CONTRACT
- Fresh-init an external target.
- Read/assert the installed official Skill.
- Execute the installed target/spec-dock/scripts/spec-dock-chatgpt as a subprocess.
- Prepend an executable named oracle to PATH.
- Set an external ORACLE_HOME_DIR.
- Fake Oracle must support the product’s exact version and required help flags.
- On one prompt submission, write valid session metadata and:
  - exactly one expected authoring ZIP for Planner/Semantic Revision; or
  - one closed Reviewer JSON Answer transcript for Reviewer.
- Derive the expected ZIP filename, root, and companion path from the received
  prompt expectation rather than hard-coding the current Issue path.
- Create a guide fixture that passes the completed S10 companion validator.
- Record argv/environment and assert:
  - one prompt submit;
  - no --write-output;
  - no personal wrapper/path;
  - no Project/profile/host/config arguments;
  - no arbitrary backend;
  - no API credential inheritance.
- Test exact repository-access failure with Candidate/Review/mutation count zero.
- Test archive and git-bound chains, including the same Candidate in git-bound
  Review and apply.

LEGACY MIGRATION
- Delete the classify_transport_frame import and old outer-frame success test.
- Do not restore any compatibility classifier.
- Replace marker-frame fixtures with OracleAuthoringZipSnapshot and
  OracleReviewJsonPayload.
- Remove active transient_payload use.
- Replace the old fourth-document marker test with a typed ZIP extra-entry
  rejection.
- Keep source binding, stale checks, revision, Review, Candidate, Human, apply,
  rollback, and no-mutation assertions.

PRODUCT DEPENDENCY DENYLIST
In active source, package, installed, update, and dogfood Issue Planning surfaces:
- no personal home path;
- no .agents/skills/chatgpt-use executable dependency;
- no oracle-chatgpt;
- no SPECDOCK_CHATGPT_COMMAND dependency;
- no invoke_backend_with_capture in the direct adapter path;
- no active --write-output;
- no SPECDOCK-ISSUE-PLANNING-RESPONSE-V1 or DOCUMENT-V1 frame;
- no Project/profile/host/LaunchAgent dependency;
- no arbitrary backend command.

Allow only:
- explicit reference-only/operator-local explanatory mentions in Skill/docs/Planner obligation;
- negative-test literals;
- the existing sanitization-test literal;
- historical report/artifact evidence outside active scan roots.

DOC/SKILL CONTRACT
Document:
- repo-local spec-dock-chatgpt entrypoint;
- PATH oracle as the only external product execution dependency;
- no wrapper/API fallback;
- exact repository/current branch/HEAD and no default fallback;
- Planner/Semantic Revision exactly-one ZIP;
- canonical requirement/design/plan plus exactly one onboarding companion;
- companion subordinate authority;
- Reviewer closed JSON;
- same Candidate required for git-bound Review and apply;
- exact Human approval before managed writes.

EXCLUSIONS
Do not:
- change requirement.md, design.md, plan.md, parents, canonical paths, schemas,
  reason codes, Candidate/Review/Human/apply semantics, or Oracle recovery;
- run real Oracle or live ChatGPT dogfood;
- perform S12 full closure or PlantUML executable acceptance;
- perform S13/S14 delivery, PR creation, merge, or Issue closure;
- edit personal chatgpt-use, Oracle source, Project/profile/config/host files;
- tune Prompts/templates;
- add public commands, flags, aliases, config, env vars, or fallbacks;
- perform optional refactors or broad formatting;
- hand-edit generated projection files.

REQUIRED VERIFICATION
Run:
1. the Red-first four-path suite;
2. official branch-local update;
3. provider/dogfood cmp checks;
4. focused S11 suite:
   - test_issue_planning_prompt.py
   - test_issue_planning_chatgpt.py
   - test_issue_planning_oracle_artifact.py
   - test_init_update.py
   - test_chatgpt_cli.py
   - test_issue_planning_chatgpt_transport.py
   - test_issue_planning_e2e.py
5. S09/S10 functional regression files;
6. selected authoring-pack/Core/Issue-lifecycle regression;
7. uv build for wheel and sdist;
8. isolated wheel and sdist init/update;
9. Ruff check and changed-file format check;
10. mypy on source and changed tests;
11. ./spec-dock/scripts/spec-dock validate;
12. scoped denylist;
13. git diff --check;
14. a second official update with identical before/after diff;
15. exact changed-path allowlist validation.

STOP CONDITIONS
Stop and report without broadening scope if:
- source lock fails;
- any path outside the allowlist must change;
- a provider runtime or schema defect is found rather than a distribution defect;
- a provider Prompt semantic change is proposed;
- classify_transport_frame, marker frames, transient_payload, generic backend,
  or --write-output would need restoration;
- real Oracle/network/personal setup is needed;
- official update changes canonical specs, initiatives, or unrelated assets;
- installer or packaging needs redesign rather than a narrow Red-backed fix;
- wheel/sdist/init/update/dogfood parity cannot be achieved;
- second update is not a no-op;
- S12/S13/S14 work is required.

DELIVERABLE
Return:
- exact changed paths grouped as authority, tests, and mechanical projection;
- initial Red evidence;
- final command results and counts;
- wheel/sdist/init/update parity evidence;
- fake Oracle argv/session/typed-output evidence;
- companion and same-Candidate evidence;
- denylist and allowlist evidence;
- second-update no-op evidence;
- remaining unrelated baseline failures, if any;
- whether src/spec_dock/cli.py changed and the exact Red that authorized it;
- Report checklist completion.

Do not open or merge a final PR and do not close the Issue under this S11 packet.
```
