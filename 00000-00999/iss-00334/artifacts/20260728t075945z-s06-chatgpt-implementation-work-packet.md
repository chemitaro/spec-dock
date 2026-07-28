---
artifact_type: s06-chatgpt-implementation-work-packet
created_at: 2026-07-28T07:59:45Z
created_by_role: chatgpt-pro
intended_issue: iss-00334
intended_step: S06
adoption_status: execution-input
review_required: false
source_repository: chemitaro/spec-dock
source_branch: iss-00334-implement-chatgpt-issue-planning-workflow
source_head: 2ab5fedc7117218e2189d26eff8684455aadf33d
initial_session: iss00334-s06-implementa-brief
model_requested: Pro
model_resolved: Pro
model_selection_verified: true
---

# Oracle Browser Transcript

Conversation: https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a6857e6-be5c-83ee-8d0e-c1531f1a9073

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

Use the attached prompt as the complete task brief. Inspect the required GitHub branch and return only the bounded S06 implementation work packet.

## Answer

# S06 Implementation Work Packet — Provider Projection and End-to-End Regression

**Repository:** `chemitaro/spec-dock`
**Branch:** `iss-00334-implement-chatgpt-issue-planning-workflow`
**Required HEAD:** `2ab5fedc7117218e2189d26eff8684455aadf33d`
**Scope:** S06 only
**Packet status:** implementation-ready; packet review waived

## 1. Verified GitHub identity

GitHub connector inspection established:

| Identity item                          | Verified value                                          |
| -------------------------------------- | ------------------------------------------------------- |
| Repository                             | `chemitaro/spec-dock`                                   |
| Default branch                         | `main`                                                  |
| Required working branch                | `iss-00334-implement-chatgpt-issue-planning-workflow`   |
| Branch accessibility                   | The branch can be opened and files can be read from it. |
| Exact branch HEAD                      | `2ab5fedc7117218e2189d26eff8684455aadf33d`              |
| Branch-versus-required-HEAD comparison | `identical`; ahead `0`, behind `0`, file diff empty     |
| Package identity at that ref           | `spec-dock` version `0.2.3`                             |

The attached S06 brief is the binding task boundary for this packet. 

### Verification limits

The GitHub connector proves the remote repository/ref state. It does not prove a developer’s local working-tree cleanliness, local tool versions, generated-file state, or test results. Those are mandatory execution preconditions below.

The S01–S05 pass counts and S05 closure result are accepted here as supplied prerequisite evidence; they were not rerun while authoring this packet. No repository write, init, update, planning operation, build, or test was executed while producing this packet.

---

## 2. Final S06 interpretation

### 2.1 Selected interpretation

S06 is a **projection-and-integration milestone**, not another planning-domain milestone.

The provider already contains the S01–S05 command family, application logic, domain contracts, infrastructure implementations, prompt resources, and the `spec-dock-chatgpt` script. What remains is to:

1. make the installed runtime resolve the installed prompt resources;
2. wire the four existing planning application operations into the real `UseCases` bootstrap;
3. close the already-deferred public Semantic/Mechanical revision Review-ingress seam without expanding the CLI or JSON schemas;
4. install the existing `spec-dock-chatgpt` script as an executable managed asset;
5. replace the old Issue-planning Skill procedure with the implemented Candidate → Review → Human decision → apply procedure;
6. align only the relevant docs and command help;
7. prove provider, package, fresh-init, update, and dogfood byte parity;
8. run the three required full fake chains through the installed public boundary.

The canonical S06 plan explicitly calls for provider/distribution/installed/dogfood completion, managed byte parity, installed Skill reachability, the three fake chains, and zero unauthorized mutation.

### 2.2 Meaning of “new executable”

“New executable” means the already-present provider asset:

```text
src/spec_dock/assets/spec_dock/scripts/spec-dock-chatgpt
```

projected as:

```text
spec-dock/scripts/spec-dock-chatgpt
```

It does **not** mean a new package console script, second binary, renamed command, wrapper framework, or command merged into `spec-dock/scripts/spec-dock`.

The canonical design already assigns parser, dispatch, and rendering ownership to `spec-dock-chatgpt`, with the public commands fixed as `planning create`, `planning revise`, `review planning`, and `planning apply`.

### 2.3 Implementation-local defects to close

There are four concrete S06 integration defects.

#### A. Real bootstrap does not configure planning

`UseCases` declares all four planning callables, but their defaults raise `RuntimeError("<operation> is not configured")`.

`cli/bootstrap.py::build_runtime` currently configures Core, lifecycle, assurance, workflow, worktree, and workbench operations, but omits all four planning callables.

#### B. Prompt resources resolve only in the provider-source layout

`application/issue_planning_prompt.py::_provider_resource_root()` currently resolves:

```text
<parents[4]>/install_root/.agents/skills/spec-dock-issue-planning/resources
```

That is correct for:

```text
src/spec_dock/assets/spec_dock/scripts/...
```

because `parents[4]` is `src/spec_dock/assets/`.

It is wrong after init/update:

```text
<repo>/spec-dock/scripts/spec_dock_runtime/application/...
```

where `parents[4]` is the repository root and the actual managed resources are under:

```text
<repo>/.agents/skills/spec-dock-issue-planning/resources
```

The current source-layout-only resolver is visible in the provider implementation.

#### C. Public `planning revise` cannot currently supply the exact Review evidence required by S04

The public request remains deliberately closed to:

```text
--candidate
--request
--output
```

The application operation additionally requires `PlanningRevisionEvidenceInput`, containing the exact external Review path and SHA-256.

S04 explicitly deferred construction of that internal evidence input to the installed workflow and prohibited expanding the public parser or revision JSON contract.

#### D. Installer chmod covers only the Core runtime script

Installer init/update copies the whole managed `scripts/` directory, but it currently applies executable bits only to:

```text
spec-dock/scripts/spec-dock
```

It must apply the same best-effort executable-bit repair to `spec-dock-chatgpt`.

### 2.4 Explicit non-goals

S06 must not:

* amend `requirement.md`, `design.md`, or `plan.md`;
* add or rename public commands;
* add a package-level `spec-dock-chatgpt` console entrypoint;
* add a public `--review-result` or `--review-result-sha256` option to `planning revise`;
* modify `PlanningReviseRequest`, `PlanningRevisionRequestV1`, Review result, Human decision, Candidate, or operation schemas;
* add a session locator, registry, database, custom Git ref, environment-controlled resource root, or generic DI framework;
* change S01–S05 identity, archive, Review, Human authority, transaction, retry, rollback, or publication semantics;
* invoke real ChatGPT during tests;
* invoke a real GitHub remote during tests;
* run `planning apply` against this repository;
* perform S07 live dogfood, PR creation, Issue finish, delivery, merge preparation, or Human merge;
* change Initiative Portfolio materialization or downstream planning;
* edit generated dogfood runtime, docs, or Skill files directly.

---

## 3. Existing paths, symbols, and seams to reuse

## 3.1 Ownership and projection map

The canonical design identifies provider runtime authority under `src/spec_dock/assets/spec_dock/`, installed Skill/prompt authority under `src/spec_dock/assets/install_root/.agents/`, and root `spec-dock/` as generated dogfood projection.

| Concern                 | Provider authority                                                                     | Installed/dogfood projection                         |
| ----------------------- | -------------------------------------------------------------------------------------- | ---------------------------------------------------- |
| ChatGPT executable      | `src/spec_dock/assets/spec_dock/scripts/spec-dock-chatgpt`                             | `spec-dock/scripts/spec-dock-chatgpt`                |
| Runtime package         | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/`                            | `spec-dock/scripts/spec_dock_runtime/`               |
| Issue-planning Skill    | `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md`   | `.agents/skills/spec-dock-issue-planning/SKILL.md`   |
| Prompt resources        | `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/resources/` | `.agents/skills/spec-dock-issue-planning/resources/` |
| Managed docs            | `src/spec_dock/assets/spec_dock/docs/`                                                 | `spec-dock/docs/`                                    |
| Provider installer      | `src/spec_dock/cli.py`                                                                 | Not copied into a target repository                  |
| Provider onboarding doc | `README.md`                                                                            | Not generated into consumer repositories             |

## 3.2 Existing installed Skill and prompt ownership

The official Skill exists at:

```text
src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md
```

Its current normal route is still the older authoring-evidence procedure: invoke `spec-dock-chatgpt-authoring`, review evidence, record an Evidence Adoption Ledger disposition, rewrite canonical documents, and obtain a fresh reviewer pass.

S06 must replace that normal operating spine with the already-implemented public workflow. The manual backup restrictions remain; they are not broadened.

The four provider-owned resources already exist and remain the authoritative bytes:

```text
src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/resources/
├── planner-prompt.md
├── reviewer-prompt.md
├── revision-prompt.md
└── transport-output-contract.md
```

No resource-content change is required by S06. The patch must make their packaging, installation, runtime resolution, and dogfood parity executable and test-proven.

## 3.3 Existing public CLI

Executable entry:

```text
src/spec_dock/assets/spec_dock/scripts/spec-dock-chatgpt
```

Application entry:

```text
spec_dock_runtime.chatgpt_app.main
```

Parser:

```text
spec_dock_runtime.cli.chatgpt_parser.build_parser
```

Registry:

```text
spec_dock_runtime.cli.chatgpt_registry.build_registry
```

Command adapter:

```text
spec_dock_runtime.commands.issue_planning.command_specs
```

Exact command keys:

```text
planning_create
planning_revise
planning_review
planning_apply
```

The parser already exposes the canonical hierarchy.

The command adapter already owns the exact argument models, mode-option closure checks, request construction, and text/JSON result routing.

Do not duplicate those responsibilities in bootstrap, the Skill, or a new wrapper.

## 3.4 Existing application operations

Reuse these functions directly:

```text
spec_dock_runtime.application.issue_planning.resolve_existing_issue_target
spec_dock_runtime.application.issue_planning.run_issue_planning_create
spec_dock_runtime.application.issue_planning.run_issue_planning_review
spec_dock_runtime.application.issue_planning.run_issue_planning_revise
spec_dock_runtime.application.issue_planning.run_issue_planning_apply
```

Request and internal evidence types:

```text
PlanningCreateRequest
PlanningReviewRequest
PlanningReviseRequest
PlanningRevisionEvidenceInput
PlanningApplyRequest
```

`run_issue_planning_create` already owns target resolution, current-document baseline proof, dependency snapshotting, transport, payload extraction, Candidate materialization, and atomic publication.

`run_issue_planning_review` already owns archive/git-bound mode closure, exact reviewed identity, target attachments, fresh transport, result parsing, source revalidation, and Review publication.

`run_issue_planning_revise` already owns exact Candidate verification, revision request validation, Review eligibility, Semantic/Mechanical execution, version increment, source revalidation, and immutable publication.

`run_issue_planning_apply` already owns Review/Human parsing, mode and identity binding, current-repository proof, preflight, operation construction, retry detection, and transaction invocation.

## 3.5 Existing runtime-state wiring primitives

Reuse:

```text
infra_fs_repo.load_node_records
domain.models.SpecNodeSeed
domain.tree.build_graph
infra_deps_reader.load_direct_dependency_resolutions
infra_git_cli.origin_github_repo_slug
```

Use the exact `StoredMetaRecord` → `SpecNodeSeed` field mapping already used by `application.validate_tree._to_spec_node_seed`:

```text
kind
id
title
slug
path
meta_path
parent_id
initiative_id
epic_id
github_issue_number
github_repo_owner
github_repo_name
```

For S06, copy this exact conversion into one private bootstrap-local helper. Do not refactor Core graph construction into a new shared framework.

Dependency context must use:

```text
infra_deps_reader.load_direct_dependency_resolutions(
    specdock_dir,
    graph,
    issue_id,
)
```

That function resolves direct dependency references against the current graph and repository scope.

## 3.6 Existing infrastructure operations

Reuse without alteration:

```text
infra.issue_planning_chatgpt.invoke_issue_planning_chatgpt
infra.issue_planning_chatgpt.resolve_issue_planning_github_repository
infra.issue_planning_candidate.load_verified_issue_candidate
infra.issue_planning_candidate.build_and_publish_candidate
infra.issue_planning_review.publish_planning_review_evidence
infra.issue_planning_review.read_external_review_result
infra.issue_planning_apply.load_expected_planning_targets
infra.issue_planning_apply.planning_apply_resume_available
infra.issue_planning_apply.execute_planning_apply_transaction
```

The fixed transport already writes a bounded prompt pack, invokes the existing backend boundary, and accepts only the exact framed response.

The Review publisher already creates an immutable external directory containing fixed filenames:

```text
planning-review-result.json
planning-review-summary.md
```

The apply transaction already runs validation, sync, exact-diff proof, planning-only commit, push, and remote parity. It permits only the Human-decision artifact and, for approved archive adoption, changed canonical planning documents in the Git commit.

## 3.7 Existing validation and sync wiring

Use:

```python
application_validate_tree(ValidateTreeRequest(), ports)
```

For planning apply, use a local deterministic sync:

```python
application_sync(
    SyncRequest(
        force=False,
        github_enabled=False,
        issue_limit=10000,
        update_active_from_branch=False,
    ),
    ports,
)
```

The existing Core `sync` command uses `10000` as its default issue limit and independently controls GitHub access and active-pointer updates.

This apply-time sync must not invoke GitHub. Remote commit parity remains the planning transaction’s own Git responsibility.

## 3.8 Installer behavior to reuse

`src/spec_dock/cli.py` already defines:

```text
_MANAGED_DIRS = ("docs", "templates", "scripts", "system")
```

and already lists `spec-dock-issue-planning` in `_MANAGED_SKILL_NAMES`.

Init/update replaces managed scaffold directories from `assets/spec_dock/` and separately projects managed install-root assets. The persistent `spec-dock/initiatives/**` tree is not removed.

Therefore:

* no new managed directory;
* no new installer registry;
* no package console entry;
* no explicit script file-copy code;
* only add executable-bit repair for `spec-dock-chatgpt`.

Package data already includes all normal assets and the hidden install-root `.agents` subtree.

`pyproject.toml` is outside the S06 allowlist unless a Red packaging test proves this current declaration insufficient.

## 3.9 User-facing surfaces

Update only:

```text
src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md
src/spec_dock/assets/spec_dock/docs/README.md
src/spec_dock/assets/spec_dock/docs/workflow_issue.md
README.md
```

The managed docs currently describe `./spec-dock/scripts/spec-dock ...` as the singular runtime command contract and omit the planning command family from their shortest-command section.

The top-level README similarly describes day-to-day operation through `./spec-dock/scripts/spec-dock` and needs the minimal second-executable note and planning command examples.

Do not rewrite general authoring, lifecycle, hard-cutover, GitHub, or authoring-pack references.

---

## 4. Smallest coherent S06 patch

## 4.1 Installed prompt-resource resolution

In:

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py
```

replace the source-layout-only `_provider_resource_root()` with one deterministic private resolver.

Required candidate roots, in this order:

```text
1. <Path(__file__).resolve().parents[4]>
   / install_root
   / .agents
   / skills
   / spec-dock-issue-planning
   / resources

2. <Path(__file__).resolve().parents[4]>
   / .agents
   / skills
   / spec-dock-issue-planning
   / resources
```

Rules:

1. Do not read an environment variable.
2. Do not search parent directories.
3. Do not accept an arbitrary CLI path.
4. Accept the first candidate containing all four required regular, non-symlink files.
5. Required inventory is exactly:

   * `planner-prompt.md`
   * `reviewer-prompt.md`
   * `revision-prompt.md`
   * `transport-output-contract.md`
6. If neither candidate is complete, raise a deterministic `FileNotFoundError` or `RuntimeError` that contains no private absolute path.
7. Keep the existing explicit `resource_root=` test seam.

This supports provider-source tests, wheel assets, fresh installation, update installation, and root dogfood from one closed resolver.

## 4.2 Fixed-sibling Review evidence for `planning revise`

Do not add a CLI option or schema field.

Selected convention:

```text
<external-review-directory>/
├── planning-review-result.json
├── planning-review-summary.md
└── planning-revision-request.json
```

The Skill writes or arranges the closed `PlanningRevisionRequestV1` file beside the exact published Review result. Public invocation is:

```bash
./spec-dock/scripts/spec-dock-chatgpt planning revise \
  --candidate <candidate.zip> \
  --request <external-review-directory>/planning-revision-request.json \
  --output <existing-external-output-directory>
```

Implementation:

1. Change the internal `run_issue_planning_revise` parameter to:

   ```python
   review_evidence: PlanningRevisionEvidenceInput | None = None
   ```

2. Preserve the explicit-evidence path used by existing S04 tests.

3. When omitted, derive exactly:

   ```python
   request.request_path.parent / "planning-review-result.json"
   ```

4. Do not glob, recurse, select newest, scan output roots, inspect another directory, or accept multiple candidates.

5. Read the derived file once with the existing external bounded-file guard.

6. Compute SHA-256 from those exact bytes.

7. Construct `PlanningRevisionEvidenceInput`.

8. Parse and validate from the same byte buffer.

9. Preserve Semantic proof:

   ```text
   request.review_result_sha256
   == derived evidence digest
   == sha256(exact Review bytes)
   ```

10. Mechanical revision uses the derived exact Review digest without adding a digest field to its closed request.

11. Map missing fixed sibling to:

```text
status=blocked
reason=revision_review_unavailable
```

12. Map unsafe, malformed, wrong-identity, or otherwise invalid Review evidence to:

```text
status=rejected
reason=revision_evidence_mismatch
```

The existing external file guard already requires an existing regular file, rejects symlink components and repository-internal inputs, imposes a one-MiB bound, and requires strict UTF-8.

Update the `--request` help text in `commands/issue_planning.py` to state that the exact `planning-review-result.json` must be in the same directory. No argument is added.

## 4.3 Real `build_runtime` planning wiring

In:

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/bootstrap.py
```

add one bootstrap-local state loader:

```text
_load_planning_state()
  -> (tuple[StoredMetaRecord, ...], SpecGraph)
```

It must:

1. load fresh records through the existing `_NodeReader`;
2. convert every record with the exact field map in §3.5;
3. call `build_graph`;
4. perform no caching across commands.

Configure the four `UseCases` callables.

### `planning_create`

Bind to `run_issue_planning_create` with:

```text
request
fresh records
resolved_repo_root
resolve_issue_planning_github_repository
invoke_issue_planning_chatgpt
dependency_loader
```

The dependency loader closes over the graph from the same fresh record snapshot and delegates to:

```text
infra_deps_reader.load_direct_dependency_resolutions(
    specdock_dir,
    graph,
    issue_id,
)
```

Do not populate speculative relevant-source or operator-context inputs.

### `planning_review`

Bind to `run_issue_planning_review` with:

```text
request
fresh records
resolved_repo_root
resolve_issue_planning_github_repository
invoke_issue_planning_chatgpt
```

Retain empty optional relevant-source/operator-context collections.

### `planning_revise`

Bind to `run_issue_planning_revise` with:

```text
request
review_evidence=None
fresh records
resolved_repo_root
resolve_issue_planning_github_repository
invoke_issue_planning_chatgpt
```

The application fixed-sibling convention constructs the internal Review evidence.

### `planning_apply`

Bind to `run_issue_planning_apply` with:

```text
request
fresh records
resolved_repo_root
resolve_issue_planning_github_repository
validation_runner
sync_runner
execute_planning_apply_transaction
```

Use the exact validation and no-GitHub/no-active-update sync closures from §3.7.

Do not add command-specific executor objects, a service container, provider registry, protocol hierarchy, or new persistence.

## 4.4 Installer projection

In `src/spec_dock/cli.py`, after managed script copying, apply `_make_executable` to both:

```text
spec-dock/scripts/spec-dock
spec-dock/scripts/spec-dock-chatgpt
```

Missing `spec-dock-chatgpt` after a managed install is an installation defect and must be caught by tests. The chmod operation itself remains best-effort in keeping with the existing cross-platform installer policy.

## 4.5 Skill procedure

Replace the current normal Issue-planning operating spine with:

1. verify existing Issue, repository, branch, clean synchronized HEAD, and external output directory;
2. run `planning create`;
3. use archive Review by default;
4. use git-bound Review only as the existing explicit fallback against current canonical documents;
5. consume only the exact published Review result;
6. for P0/P1 findings, create a closed revision request beside `planning-review-result.json`, run `planning revise`, and obtain a fresh Review of the new Candidate;
7. do not revise for P2/P3-only Review observations;
8. obtain an explicit Human decision bound to the exact Review bytes and reviewed identity;
9. run `planning apply` only after exact PASS plus exact approval;
10. accept implementation handoff only when result status is `ready`;
11. keep manual planning as Human-approved emergency backup only;
12. state that S07 live dogfood, PR, Issue finish, and merge are separate.

The Skill must use:

```text
./spec-dock/scripts/spec-dock-chatgpt
```

It must not invoke `spec-dock-chatgpt-authoring` as the normal S06 Issue-planning workflow.

## 4.6 Docs and help

Document the exact commands already exposed by the parser:

```bash
./spec-dock/scripts/spec-dock-chatgpt planning create ...
./spec-dock/scripts/spec-dock-chatgpt planning revise ...
./spec-dock/scripts/spec-dock-chatgpt review planning ...
./spec-dock/scripts/spec-dock-chatgpt planning apply ...
```

Document:

* archive versus git-bound identity options;
* external output requirement;
* fixed-sibling Review requirement for revise;
* Review PASS plus exact Human approval before apply;
* `ready` as the successful adoption result;
* evidence-only Candidate/Review status before apply;
* no implied PR, Issue finish, or merge.

Do not duplicate complete JSON schemas in docs.

---

## 5. Exact write allowlists

## 5.1 Provider production-authority writes

Only these production files may be edited directly:

```text
README.md

src/spec_dock/cli.py

src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md

src/spec_dock/assets/spec_dock/docs/README.md
src/spec_dock/assets/spec_dock/docs/workflow_issue.md

src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/bootstrap.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/issue_planning.py
```

Prompt-resource bytes are read-only in S06:

```text
src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/resources/planner-prompt.md
src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/resources/reviewer-prompt.md
src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/resources/revision-prompt.md
src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/resources/transport-output-contract.md
```

## 5.2 Test-authority writes

Only these tests may be edited or added:

```text
tests/cli_runtime/test_chatgpt_cli.py
tests/unit/application/test_issue_planning.py
tests/unit/application/test_issue_planning_prompt.py
tests/unit/commands/test_issue_planning.py
tests/unit/infra/test_init_update.py
tests/integration/test_issue_planning_e2e.py
```

`tests/integration/test_issue_planning_e2e.py` is new.

Do not modify existing S01–S05 test expectations merely to make the suite pass.

## 5.3 Mechanically generated dogfood outputs

These files may change only through:

```bash
uv run python -m spec_dock.cli update .
```

Never edit them directly.

```text
.agents/skills/spec-dock-issue-planning/SKILL.md
.agents/skills/spec-dock-issue-planning/resources/planner-prompt.md
.agents/skills/spec-dock-issue-planning/resources/reviewer-prompt.md
.agents/skills/spec-dock-issue-planning/resources/revision-prompt.md
.agents/skills/spec-dock-issue-planning/resources/transport-output-contract.md

spec-dock/docs/README.md
spec-dock/docs/workflow_issue.md

spec-dock/scripts/spec-dock-chatgpt
spec-dock/scripts/spec_dock_runtime/chatgpt_app.py

spec-dock/scripts/spec_dock_runtime/application/contracts.py
spec-dock/scripts/spec_dock_runtime/application/issue_planning.py
spec-dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py
spec-dock/scripts/spec_dock_runtime/application/authoring_pack/backend_invoke.py

spec-dock/scripts/spec_dock_runtime/cli/bootstrap.py
spec-dock/scripts/spec_dock_runtime/cli/chatgpt_parser.py
spec-dock/scripts/spec_dock_runtime/cli/chatgpt_registry.py

spec-dock/scripts/spec_dock_runtime/commands/issue_planning.py

spec-dock/scripts/spec_dock_runtime/domain/authoring_pack/authority_boundary.py
spec-dock/scripts/spec_dock_runtime/domain/authoring_pack/backend_invoke_contract.py
spec-dock/scripts/spec_dock_runtime/domain/authoring_pack/zip_contract.py
spec-dock/scripts/spec_dock_runtime/domain/issue_planning_candidate.py
spec-dock/scripts/spec_dock_runtime/domain/issue_planning_contracts.py

spec-dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py
spec-dock/scripts/spec_dock_runtime/infra/issue_planning_candidate.py
spec-dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py
spec-dock/scripts/spec_dock_runtime/infra/issue_planning_review.py

spec-dock/scripts/spec_dock_runtime/presentation/issue_planning.py
```

The list includes provider assets implemented in S01–S05 that are currently not yet fully projected into the repository’s dogfood runtime.

Any update-produced tracked change outside this exact set is a hard stop. In particular, do not accept changes to:

```text
spec-dock/spec-dock.version
spec-dock/scripts/spec-dock
spec-dock/templates/**
spec-dock/system/**
.agents/skills/<any-other-skill>/**
.codex/**
.github/**
spec-dock/initiatives/**
```

---

## 6. Red-first test matrix

| ID      | Red test                                                                        | Required proof                                                                                                                                                                                                              |
| ------- | ------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| S06-R01 | `test_build_runtime_configures_all_issue_planning_use_cases`                    | Real `build_runtime` returns four non-default planning callables. Calling them reaches the corresponding application operation rather than “not configured”.                                                                |
| S06-R02 | `test_installed_runtime_resolves_managed_issue_planning_resources`              | A runtime imported from a fresh-init target reads the root `.agents/.../resources` bytes, not a nonexistent `install_root` path.                                                                                            |
| S06-R03 | `test_revision_without_explicit_evidence_uses_exact_review_sibling`             | Public revise derives only the exact sibling filename, reads it once, computes its digest, and preserves Semantic/Mechanical evidence rules.                                                                                |
| S06-R04 | `test_revision_does_not_scan_for_review_evidence`                               | Another Review elsewhere, a newer Review, or multiple Review directories cannot be selected. Missing fixed sibling blocks; malformed/unsafe sibling rejects.                                                                |
| S06-R05 | `test_issue_planning_revise_help_states_review_sibling_contract`                | Actual `--help`, Skill, and docs all describe the same fixed-sibling requirement.                                                                                                                                           |
| S06-R06 | `test_issue_334_init_and_update_install_chatgpt_assets_byte_exact`              | Fresh init and update project executable, runtime, Skill, resources, and relevant docs byte-for-byte from provider authority; both runtime scripts are executable where the platform supports mode bits.                    |
| S06-R07 | `test_issue_334_update_restores_managed_assets_and_preserves_unmanaged_content` | Deliberately stale planning assets are restored; unmanaged sentinel content and `spec-dock/initiatives/**` remain byte-identical.                                                                                           |
| S06-R08 | `test_issue_334_wheel_sdist_and_installed_resources_are_byte_exact`             | Logical managed inventory and bytes match in provider tree, wheel, sdist, wheel-installed resources, and fresh-init target.                                                                                                 |
| S06-R09 | `test_issue_334_checked_in_dogfood_projection_matches_provider`                 | Every file in §5.3 equals its provider source byte-for-byte. No extra planning asset exists on only one side.                                                                                                               |
| S06-R10 | `test_installed_issue_planning_skill_reaches_repo_local_command`                | Installed Skill names `./spec-dock/scripts/spec-dock-chatgpt`; the script and every leaf `--help` execute with backend call count zero.                                                                                     |
| S06-R11 | `test_archive_full_fake_chain_reaches_ready`                                    | Public create → archive Review PASS → exact Human approval → apply returns `ready`; Candidate bytes are adopted; local and bare-remote heads match.                                                                         |
| S06-R12 | `test_git_bound_full_fake_chain_reaches_ready`                                  | Public create → git-bound Review PASS at exact HEAD → exact Human approval → apply returns `ready`; canonical docs remain unchanged; decision-only planning commit reaches the bare remote.                                 |
| S06-R13 | `test_failed_review_semantic_revision_reaches_fresh_pass`                       | Review FAIL with P1 → fixed-sibling Semantic request → new Candidate version/ID/SHA → fresh Review PASS. Prior Candidate stays byte-identical. No apply occurs.                                                             |
| S06-R14 | `test_full_fake_chains_have_zero_unauthorized_mutations`                        | `.assurance.json`, Portfolio sentinel tree, sibling Issue, and downstream Issue remain byte-identical. Create/review/revise do not mutate the repository. Apply’s tracked diff is exactly its existing operation allowlist. |
| S06-R15 | Existing Core/lifecycle/authoring regressions                                   | Core parser/runtime, Issue lifecycle, and authoring-pack suites remain Green without expectation weakening.                                                                                                                 |

## 6.1 Full fake E2E construction

Use a new single-purpose file:

```text
tests/integration/test_issue_planning_e2e.py
```

Do not introduce a generic E2E framework.

Each test must use:

1. a temporary target initialized through the provider installer;

2. an isolated temporary Git repository;

3. an isolated local bare origin;

4. a GitHub-shaped origin URL redirected locally with repository-local Git configuration, for example:

   ```text
   url.file://<bare-repo>/.insteadOf git@github.com:fixture-owner/fixture-repo.git
   ```

5. no network;

6. no credentials;

7. a deterministic fake at the existing low-level backend-capture seam;

8. the installed runtime modules loaded from the fresh target’s `spec-dock/scripts` directory;

9. real `chatgpt_app.main`, parser, registry, `build_runtime`, application operations, Candidate/Review publishers, validation, sync, apply transaction, commit, push, and remote parity.

When importing the installed runtime in-process:

* temporarily remove `spec_dock_runtime` modules from `sys.modules`;
* prepend the fresh target’s `spec-dock/scripts` directory;
* import the installed runtime;
* apply the fake backend patch;
* restore `sys.path` and prior modules after the test.

This is test isolation, not a product hook.

### Archive chain

```text
planning create
→ review planning --mode archive-candidate
→ exact PlanningHumanDecisionV1 approval
→ planning apply --mode archive-candidate
→ status=ready
```

Required assertions:

* candidate created externally;
* Review result and summary created externally;
* exact reviewed identity and digest binding;
* Human decision bytes preserved;
* canonical `requirement.md`, `design.md`, and `plan.md` equal Candidate bytes;
* decision artifact created;
* planning-only commit;
* pushed remote head equals local commit;
* operation output is `ready`;
* external operation record is complete;
* no forbidden mutation.

### Git-bound chain

```text
planning create
→ review planning --mode git-bound --reviewed-head <HEAD>
→ exact PlanningHumanDecisionV1 approval
→ planning apply --mode git-bound
→ status=ready
```

The externally created Candidate is not adopted in this chain. Git-bound Review targets the current canonical three documents at the exact synchronized HEAD.

Required assertions:

* canonical planning documents stay byte-identical;
* only the decision artifact is in the planning commit;
* pushed remote head equals local commit;
* no forbidden mutation.

### Semantic revision chain

```text
planning create
→ archive Review FAIL with one P1 finding
→ planning-revision-request.json beside planning-review-result.json
→ planning revise
→ Candidate v2
→ fresh archive Review PASS
```

Required assertions:

* exact failed Review bytes drive revision;
* selected finding is P0/P1 and matches the request;
* new Candidate version is prior version plus one;
* new Candidate identity and ZIP SHA differ;
* old Candidate remains byte-identical;
* fresh Review binds only to the new Candidate;
* no Human decision or apply is performed;
* repository tracked and forbidden content remains unchanged.

---

## 7. Ordered implementation and projection sequence

1. **Preflight remote/local identity**

   * verify branch;
   * verify exact HEAD;
   * require an approved clean local baseline;
   * record existing untracked files before making changes.

2. **Write and run Red tests**

   * resource resolution;
   * real bootstrap wiring;
   * fixed-sibling revision;
   * help parity;
   * init/update/package parity;
   * installed Skill reachability;
   * three fake chains;
   * unauthorized mutation.

3. **Fix installed resource resolution**

   * closed provider-versus-installed two-root resolver;
   * no resource-content edits.

4. **Close revision Review ingress**

   * optional internal evidence;
   * exact sibling only;
   * no CLI/schema expansion;
   * update one help string.

5. **Wire real runtime**

   * bootstrap-local record-to-graph adapter;
   * four `UseCases`;
   * existing backend, dependency, validation, sync, and transaction operations.

6. **Make the script executable on install/update**

   * retain whole-directory managed copying;
   * add only the second `_make_executable` call.

7. **Update Skill and minimum docs**

   * implemented public workflow;
   * fixed-sibling revision convention;
   * Human gate;
   * `ready`;
   * S07 separation.

8. **Run narrow S06 tests**

9. **Run the complete S01–S05 regression set**

10. **Run Core CLI, Issue lifecycle, and authoring-pack focused regressions**

11. **Run static analysis**

12. **Build wheel and sdist outside the repository**

13. **Verify wheel/sdist logical inventories and bytes**

14. **Run fresh init and update in temporary external targets**

15. **Install the wheel into an isolated venv and repeat init/update/help checks**

16. **Run the complete test suite**

17. **Refresh this repository’s dogfood projection only through:**

    ```bash
    uv run python -m spec_dock.cli update .
    ```

    Do not use:

    ```bash
    ./spec-dock/scripts/spec-dock update
    ```

    for branch projection. The repo-local wrapper intentionally obtains the fixed upstream package rather than the unmerged current branch. Its fixed-upstream behavior is documented in the repository README.

18. **Inspect the generated diff against §5.3**

19. **Run byte-parity checks against dogfood**

20. **Run validate → local sync → validate**

21. **Rerun S06 focused tests, static analysis, and full regression after projection**

22. **Run exact final diff allowlist and forbidden-mutation checks**

23. **Remove all temporary build/install/fake-remote state**

No planning operation may be run against this repository at any step.

---

## 8. Exact verification commands

## 8.1 Local identity and baseline

```bash
set -euo pipefail

test "$(git branch --show-current)" = \
  "iss-00334-implement-chatgpt-issue-planning-workflow"

test "$(git rev-parse HEAD)" = \
  "2ab5fedc7117218e2189d26eff8684455aadf33d"

git status --short
```

Stop unless the status is clean or every pre-existing path has been explicitly recorded and is outside the S06 write set.

## 8.2 Red/focused S06 lane

```bash
uv run pytest -q \
  tests/unit/application/test_issue_planning_prompt.py \
  tests/unit/application/test_issue_planning.py \
  tests/unit/commands/test_issue_planning.py \
  tests/cli_runtime/test_chatgpt_cli.py \
  tests/unit/infra/test_init_update.py \
  tests/integration/test_issue_planning_e2e.py \
  -k 'issue_334 or installed_runtime or planning_runtime_wiring or revision_review_sibling or full_fake_chain'
```

After implementation:

```bash
uv run pytest -q tests/unit/application/test_issue_planning_prompt.py
uv run pytest -q tests/unit/application/test_issue_planning.py
uv run pytest -q tests/unit/commands/test_issue_planning.py
uv run pytest -q tests/cli_runtime/test_chatgpt_cli.py
uv run pytest -q tests/unit/infra/test_init_update.py -k 'issue_334'
uv run pytest -q tests/integration/test_issue_planning_e2e.py
```

## 8.3 S01–S05 regression lane

```bash
uv run pytest -q \
  tests/unit/domain/test_issue_planning_contracts.py \
  tests/unit/domain/test_issue_planning_candidate.py \
  tests/unit/application/test_issue_planning_prompt.py \
  tests/unit/application/test_issue_planning.py \
  tests/unit/application/test_issue_planning_apply.py \
  tests/unit/commands/test_issue_planning.py \
  tests/unit/infra/test_issue_planning_chatgpt.py \
  tests/unit/infra/test_issue_planning_candidate.py \
  tests/unit/infra/test_issue_planning_review.py \
  tests/unit/infra/test_issue_planning_apply.py \
  tests/unit/presentation/test_issue_planning.py \
  tests/integration/test_issue_planning_chatgpt_transport.py \
  tests/integration/test_issue_planning_apply.py \
  tests/cli_runtime/test_chatgpt_cli.py \
  tests/integration/test_issue_planning_e2e.py
```

## 8.4 Core, lifecycle, and authoring-pack focused regressions

```bash
uv run pytest -q \
  tests/cli_runtime/test_runtime_shell_s11.py \
  tests/cli_runtime/test_issue_lifecycle.py \
  tests/cli_runtime/test_authoring.py
```

## 8.5 Static analysis

```bash
./scripts/static_analysis/run.sh
```

This remains the repository’s Ruff check, Ruff format check, and mypy gate.

## 8.6 External temporary workspace

```bash
export S06_TMP="$(
  mktemp -d "${TMPDIR:-/tmp}/specdock-s06.XXXXXX"
)"

cleanup_s06() {
  rm -rf "$S06_TMP"
}
trap cleanup_s06 EXIT

mkdir -p \
  "$S06_TMP/dist" \
  "$S06_TMP/fresh" \
  "$S06_TMP/from-wheel"
```

## 8.7 Wheel and sdist build

```bash
uv build --out-dir "$S06_TMP/dist"

test "$(find "$S06_TMP/dist" -maxdepth 1 -name '*.whl' | wc -l | tr -d ' ')" = "1"
test "$(find "$S06_TMP/dist" -maxdepth 1 -name '*.tar.gz' | wc -l | tr -d ' ')" = "1"

uv run pytest -q \
  tests/unit/infra/test_init_update.py \
  -k 'issue_334 and (wheel or sdist or installed_resources)'
```

The packaging test must compare logical inventory and bytes, not only file presence.

## 8.8 Fresh provider init and update

```bash
uv run python -m spec_dock.cli init "$S06_TMP/fresh"

test -x "$S06_TMP/fresh/spec-dock/scripts/spec-dock"
test -x "$S06_TMP/fresh/spec-dock/scripts/spec-dock-chatgpt"

"$S06_TMP/fresh/spec-dock/scripts/spec-dock-chatgpt" --help
"$S06_TMP/fresh/spec-dock/scripts/spec-dock-chatgpt" planning create --help
"$S06_TMP/fresh/spec-dock/scripts/spec-dock-chatgpt" planning revise --help
"$S06_TMP/fresh/spec-dock/scripts/spec-dock-chatgpt" review planning --help
"$S06_TMP/fresh/spec-dock/scripts/spec-dock-chatgpt" planning apply --help
```

Add preservation and stale-managed-asset sentinels:

```bash
mkdir -p "$S06_TMP/fresh/spec-dock/initiatives/preservation-sentinel"
printf 'persistent\n' \
  > "$S06_TMP/fresh/spec-dock/initiatives/preservation-sentinel/value.txt"

printf 'unmanaged\n' \
  > "$S06_TMP/fresh/unmanaged-s06-sentinel.txt"

printf 'stale\n' \
  > "$S06_TMP/fresh/spec-dock/scripts/spec-dock-chatgpt"

uv run python -m spec_dock.cli update "$S06_TMP/fresh"

test -x "$S06_TMP/fresh/spec-dock/scripts/spec-dock-chatgpt"

test "$(cat "$S06_TMP/fresh/spec-dock/initiatives/preservation-sentinel/value.txt")" = \
  "persistent"

test "$(cat "$S06_TMP/fresh/unmanaged-s06-sentinel.txt")" = \
  "unmanaged"

cmp \
  src/spec_dock/assets/spec_dock/scripts/spec-dock-chatgpt \
  "$S06_TMP/fresh/spec-dock/scripts/spec-dock-chatgpt"

diff -qr \
  src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning \
  "$S06_TMP/fresh/.agents/skills/spec-dock-issue-planning"
```

## 8.9 Isolated wheel installation

```bash
wheel="$(
  find "$S06_TMP/dist" -maxdepth 1 -name '*.whl' -print -quit
)"

python -m venv "$S06_TMP/venv"

"$S06_TMP/venv/bin/pip" install \
  --disable-pip-version-check \
  --no-deps \
  "$wheel"

"$S06_TMP/venv/bin/spec-dock" init "$S06_TMP/from-wheel"

test -x "$S06_TMP/from-wheel/spec-dock/scripts/spec-dock-chatgpt"

"$S06_TMP/from-wheel/spec-dock/scripts/spec-dock-chatgpt" --help
"$S06_TMP/from-wheel/spec-dock/scripts/spec-dock-chatgpt" planning create --help
"$S06_TMP/from-wheel/spec-dock/scripts/spec-dock-chatgpt" planning revise --help
"$S06_TMP/from-wheel/spec-dock/scripts/spec-dock-chatgpt" review planning --help
"$S06_TMP/from-wheel/spec-dock/scripts/spec-dock-chatgpt" planning apply --help

"$S06_TMP/venv/bin/spec-dock" update "$S06_TMP/from-wheel"

diff -qr \
  src/spec_dock/assets/spec_dock/scripts \
  "$S06_TMP/from-wheel/spec-dock/scripts"

diff -qr \
  src/spec_dock/assets/spec_dock/docs \
  "$S06_TMP/from-wheel/spec-dock/docs"

diff -qr \
  src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning \
  "$S06_TMP/from-wheel/.agents/skills/spec-dock-issue-planning"
```

Exclude generated `__pycache__` only if execution created it:

```bash
diff -qr --exclude='__pycache__' \
  src/spec_dock/assets/spec_dock/scripts \
  "$S06_TMP/from-wheel/spec-dock/scripts"
```

Do not exclude any managed source file.

## 8.10 Full regression before dogfood projection

```bash
uv run pytest -q
./scripts/static_analysis/run.sh
```

## 8.11 Official dogfood update

```bash
uv run python -m spec_dock.cli update .
```

Immediately inspect:

```bash
git status --short

git diff --name-status -- \
  spec-dock/scripts \
  spec-dock/docs \
  .agents/skills/spec-dock-issue-planning
```

Do not normalize or manually repair generated files after this command. A mismatch must be fixed in provider authority and the update rerun.

## 8.12 Dogfood byte parity

```bash
diff -qr --exclude='__pycache__' \
  src/spec_dock/assets/spec_dock/scripts \
  spec-dock/scripts

diff -qr \
  src/spec_dock/assets/spec_dock/docs \
  spec-dock/docs

diff -qr \
  src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning \
  .agents/skills/spec-dock-issue-planning

uv run pytest -q \
  tests/unit/infra/test_init_update.py \
  -k 'issue_334 and dogfood'
```

## 8.13 Dogfood validation

```bash
./spec-dock/scripts/spec-dock validate
./spec-dock/scripts/spec-dock sync --no-github --no-update-active
./spec-dock/scripts/spec-dock validate

git diff --check
```

Do not invoke `spec-dock-chatgpt planning apply` against this repository.

## 8.14 Exact final changed-path allowlist

Run this from the repository root:

```bash
python - <<'PY'
from __future__ import annotations

import subprocess


allowed = {
    # Provider production authority
    "README.md",
    "src/spec_dock/cli.py",
    "src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md",
    "src/spec_dock/assets/spec_dock/docs/README.md",
    "src/spec_dock/assets/spec_dock/docs/workflow_issue.md",
    "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py",
    "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py",
    "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/bootstrap.py",
    "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/issue_planning.py",

    # Test authority
    "tests/cli_runtime/test_chatgpt_cli.py",
    "tests/unit/application/test_issue_planning.py",
    "tests/unit/application/test_issue_planning_prompt.py",
    "tests/unit/commands/test_issue_planning.py",
    "tests/unit/infra/test_init_update.py",
    "tests/integration/test_issue_planning_e2e.py",

    # Mechanically generated Skill/resources
    ".agents/skills/spec-dock-issue-planning/SKILL.md",
    ".agents/skills/spec-dock-issue-planning/resources/planner-prompt.md",
    ".agents/skills/spec-dock-issue-planning/resources/reviewer-prompt.md",
    ".agents/skills/spec-dock-issue-planning/resources/revision-prompt.md",
    ".agents/skills/spec-dock-issue-planning/resources/transport-output-contract.md",

    # Mechanically generated docs
    "spec-dock/docs/README.md",
    "spec-dock/docs/workflow_issue.md",

    # Mechanically generated runtime
    "spec-dock/scripts/spec-dock-chatgpt",
    "spec-dock/scripts/spec_dock_runtime/chatgpt_app.py",
    "spec-dock/scripts/spec_dock_runtime/application/contracts.py",
    "spec-dock/scripts/spec_dock_runtime/application/issue_planning.py",
    "spec-dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py",
    "spec-dock/scripts/spec_dock_runtime/application/authoring_pack/backend_invoke.py",
    "spec-dock/scripts/spec_dock_runtime/cli/bootstrap.py",
    "spec-dock/scripts/spec_dock_runtime/cli/chatgpt_parser.py",
    "spec-dock/scripts/spec_dock_runtime/cli/chatgpt_registry.py",
    "spec-dock/scripts/spec_dock_runtime/commands/issue_planning.py",
    "spec-dock/scripts/spec_dock_runtime/domain/authoring_pack/authority_boundary.py",
    "spec-dock/scripts/spec_dock_runtime/domain/authoring_pack/backend_invoke_contract.py",
    "spec-dock/scripts/spec_dock_runtime/domain/authoring_pack/zip_contract.py",
    "spec-dock/scripts/spec_dock_runtime/domain/issue_planning_candidate.py",
    "spec-dock/scripts/spec_dock_runtime/domain/issue_planning_contracts.py",
    "spec-dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py",
    "spec-dock/scripts/spec_dock_runtime/infra/issue_planning_candidate.py",
    "spec-dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py",
    "spec-dock/scripts/spec_dock_runtime/infra/issue_planning_review.py",
    "spec-dock/scripts/spec_dock_runtime/presentation/issue_planning.py",
}

tracked = set(
    subprocess.check_output(
        ["git", "diff", "--name-only", "HEAD", "--"],
        text=True,
    ).splitlines()
)
untracked = set(
    subprocess.check_output(
        ["git", "ls-files", "--others", "--exclude-standard"],
        text=True,
    ).splitlines()
)
changed = tracked | untracked
unexpected = sorted(changed - allowed)

if unexpected:
    raise SystemExit(
        "S06 changed-path allowlist violation:\n"
        + "\n".join(f"- {path}" for path in unexpected)
    )

print(f"S06 changed-path allowlist pass: {len(changed)} changed paths")
PY
```

## 8.15 Explicit forbidden-mutation check

```bash
test -z "$(
  git diff --name-only HEAD -- \
    ':(glob)spec-dock/**/.assurance.json' \
    ':(icase,glob)spec-dock/**/portfolio/**'
)"
```

Also identify the actual sibling and downstream Issue paths used by the E2E fixture and assert their complete pre/post inventories and bytes in the test itself.

## 8.16 Final gates

```bash
uv run pytest -q \
  tests/unit/application/test_issue_planning_prompt.py \
  tests/unit/application/test_issue_planning.py \
  tests/unit/commands/test_issue_planning.py \
  tests/cli_runtime/test_chatgpt_cli.py \
  tests/unit/infra/test_init_update.py \
  tests/integration/test_issue_planning_e2e.py

uv run pytest -q
./scripts/static_analysis/run.sh

git diff --check
git status --short
```

---

## 9. Stop conditions

Stop without broadening the implementation when any of the following occurs:

1. Local branch or HEAD differs from the verified identity.
2. The initial local tree contains unexplained changes overlapping S06 paths.
3. Real planning wiring requires a new public command, CLI option, JSON field, registry, database, session identifier, or custom Git ref.
4. Exact revision evidence cannot be supplied by the fixed sibling convention without scanning or heuristic selection.
5. Provider and installed resource layouts cannot be supported by the closed two-candidate resolver.
6. A prompt-resource content change appears necessary rather than a resolution/projection fix.
7. `pyproject.toml` appears necessary without a Red packaging test proving the existing package-data declaration insufficient.
8. A real ChatGPT process or real GitHub network request is attempted by an S06 test.
9. A test requires adding a production-only test hook, environment override, fake provider, or generic DI framework.
10. Full fake E2E cannot exercise real `build_runtime`, parser, registry, application, validation, sync, and transaction code.
11. Apply produces a tracked path outside the existing canonical-document plus decision-artifact contract.
12. `.assurance.json`, Portfolio, sibling Issue, or downstream Issue bytes change.
13. Official update changes a tracked path outside §5.3.
14. A generated dogfood discrepancy is “fixed” by editing root `spec-dock/` or root `.agents/` directly.
15. Core CLI, Issue lifecycle, authoring-pack, or S01–S05 regressions require weakened expectations.
16. Wheel, sdist, installed resources, fresh init, update, and dogfood cannot achieve byte parity.
17. The installed Skill cannot reach the repo-local executable.
18. The supported execution platform cannot run the existing atomic publication operations used by the required full fake chains.
19. Work drifts into S07, including live product dogfood, PR creation, Issue finish, delivery, or merge.
20. Canonical Requirement, Design, or Plan semantics would need amendment.

A concrete stop must report the exact failing command, path, expected contract, observed result, and why it cannot be corrected inside the allowlist. It must not propose speculative architecture.

---

## 10. Cleanup requirements

Before final S06 handoff:

* remove all temporary target repositories;
* remove local bare remotes;
* remove temporary venvs;
* remove wheel/sdist output directories;
* remove temporary Candidate, Review, revision request, Human decision, and apply-operation outputs;
* ensure none of those outputs were created under this repository;
* remove test-generated `__pycache__`, `.pyc`, and `.pyo` files if they were created outside ignored locations;
* ensure no task-created `build/`, `dist/`, or additional `*.egg-info` remains;
* preserve any pre-existing build/cache path rather than deleting it blindly;
* remove temporary Git URL-rewrite configuration with its temporary repository;
* restore `sys.path`, `sys.modules`, monkeypatches, environment, and current directory after every installed-runtime test;
* ensure no backend transcript, credential, secret value, or private host path was written to test output or diagnostics;
* ensure final changed paths are exactly within §5;
* ensure all generated dogfood changes are mechanically attributable to provider sources.

---

## 11. Copy-ready `dev-coder` instruction

```text
Implement S06 only in chemitaro/spec-dock.

Required branch:
iss-00334-implement-chatgpt-issue-planning-workflow

Required starting HEAD:
2ab5fedc7117218e2189d26eff8684455aadf33d

The accompanying S06 implementation packet is binding and its review is waived. Do not amend the canonical requirement, design, or plan. Do not implement or review S07.

Goal:
Complete provider projection, real public wiring, distribution, installed/dogfood parity, and full fake end-to-end regression for the already-implemented S01–S05 Issue-planning workflow.

Implement exactly these production changes:

1. In application/issue_planning_prompt.py, replace the provider-source-only prompt-resource lookup with a closed two-layout resolver:
   - provider: <anchor>/install_root/.agents/skills/spec-dock-issue-planning/resources
   - installed: <anchor>/.agents/skills/spec-dock-issue-planning/resources
   Require exactly the four managed prompt files. No environment override, recursive search, arbitrary path, or new configuration.

2. In application/issue_planning.py, make PlanningRevisionEvidenceInput optional only at the internal run_issue_planning_revise boundary. When absent, derive exactly request.request_path.parent / "planning-review-result.json"; do not scan. Read once with the existing external bounded-file guard, compute the digest, and preserve the existing Semantic and Mechanical evidence rules. Missing fixed sibling blocks as revision_review_unavailable; unsafe/malformed/mismatched evidence rejects as revision_evidence_mismatch. Do not change the public request or JSON schemas.

3. In commands/issue_planning.py, update only the --request help text so actual help states that planning-review-result.json must be in the same directory. Add no argument.

4. In cli/bootstrap.py, wire real planning_create, planning_review, planning_revise, and planning_apply UseCases to the existing application operations. Load fresh StoredMetaRecord values per command, build the graph with the exact existing StoredMetaRecord-to-SpecNodeSeed mapping, and use the existing direct-dependency loader. Reuse the existing GitHub-repository resolver, fixed ChatGPT transport, validate-tree operation, no-GitHub/no-active-update sync, and execute_planning_apply_transaction. Do not add executor classes, a service container, registry, persistence, or generic DI.

5. In src/spec_dock/cli.py, apply the existing executable-bit repair to spec-dock/scripts/spec-dock-chatgpt as well as spec-dock/scripts/spec-dock.

6. Replace the normal operating spine in the provider spec-dock-issue-planning Skill with the implemented Candidate → archive/git-bound Review → optional revision → fresh PASS → exact Human decision → apply → ready workflow. Keep manual planning as Human-approved emergency backup. Do not treat Candidate or Review as canonical adoption. Do not imply PR, Issue finish, or merge.

7. Update only README.md, provider docs/README.md, and provider docs/workflow_issue.md with the exact repo-local command family and fixed-sibling revision convention. Do not rewrite unrelated authoring-pack or lifecycle documentation.

Use only the production and test write allowlists in the packet. Prompt-resource content and pyproject.toml are read-only unless a Red test proves a concrete S06 packaging defect.

Work Red-first. Add:
- real build_runtime wiring tests;
- installed-layout prompt-resource tests;
- fixed-sibling/no-scan revision tests;
- init/update/wheel/sdist/installed/dogfood byte-parity tests;
- installed Skill-to-command reachability tests;
- docs/help parity tests;
- one focused integration file covering all three required full fake chains;
- exact unauthorized-mutation assertions.

Full fake tests must:
- use a fresh provider-installed temporary repo;
- use a local bare remote only;
- use a GitHub-shaped origin redirected locally;
- patch the existing low-level backend capture seam;
- import and execute the installed runtime;
- run real parser, registry, build_runtime, application, validation, sync, transaction, commit, push, and remote-parity logic;
- make zero real ChatGPT or GitHub network calls.

Never run planning apply against the real spec-dock repository.

After provider tests, build wheel/sdist outside the repository, verify fresh init/update and isolated wheel installation, then refresh dogfood only with:

uv run python -m spec_dock.cli update .

Do not use the repo-local fixed-upstream update wrapper for branch projection. Do not directly edit generated root spec-dock or .agents files.

After projection, require exact provider/dogfood byte parity, validate → sync --no-github --no-update-active → validate, the packet’s exact changed-path allowlist, static analysis, and the full pytest suite.

Stop rather than broaden scope if a new public contract, schema, persistence mechanism, test-only production hook, prompt-content rewrite, canonical-doc amendment, unauthorized mutation, unrelated generated diff, or S07 operation would be required.

At completion, report:
- files changed, separated into provider/test/generated;
- Red tests observed before implementation;
- focused and full command results;
- wheel/sdist/fresh-init/update/dogfood parity evidence;
- the three fake-chain outcomes;
- forbidden-mutation count;
- final branch and HEAD;
- remaining limitations, if any.
```
