# Oracle Browser Transcript

Conversation: https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a6a8aa2-0ef0-83e8-8a72-79da3c9baecf

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

Use the attached follow-up as the complete correction delta to your prior Blocker N amendment. Re-inspect the exact GitHub branch and HEAD; default fallback remains forbidden. Return only the requested corrected bounded format.

## Answer

# S12 Blocker N Allowlist Correction

## Verified incompatibility

The GitHub connector reinspection confirms that mandatory branch `iss-00334-implement-chatgpt-issue-planning-workflow` is identical to exact pushed HEAD `fd97aca1f005e2fe066a872343039c7e5b8889ca`, with ahead `0` and behind `0`. Default-branch fallback was not used. Per the correction delta, no Blocker N file has been edited and the independent dirty exact12 repair remains outside this scope. 

The prior nine-file allowlist is insufficient because changing the four application entry points to accept an application-owned dependency boundary affects every direct caller, not only bootstrap and the already-allowed application tests.

The exact-HEAD production inventory contains only the four planning closures in provider `cli/bootstrap.py` and its mechanical dogfood projection: create, review, revise, and apply.

The exact direct-call inventory is:

* Create: 22 calls — 17 in `tests/unit/application/test_issue_planning.py`, four in `tests/integration/test_issue_planning_chatgpt_transport.py`, and one in `tests/unit/infra/test_issue_planning_chatgpt.py`.
* Review: nine calls — seven in `tests/unit/application/test_issue_planning.py` and two in `tests/integration/test_issue_planning_chatgpt_transport.py`.
* Revise: nine calls — eight in `tests/unit/application/test_issue_planning.py` and one in `tests/integration/test_issue_planning_chatgpt_transport.py`.
* Apply: eight calls — seven in `tests/unit/application/test_issue_planning_apply.py` and one in `tests/integration/test_issue_planning_apply.py`. 

The three newly admitted files contain exactly the additional direct calls identified by that inventory: four create, two review, and one revise call in the transport integration test; one apply call in the apply integration test; and one create call in the ChatGPT infra test.

An optional dependency argument without a concrete fallback is not a valid compatibility strategy. Each use case unconditionally requires at least one gateway operation even when existing callable overrides are supplied:

* Create always validates the external output directory.
* Review always validates output and opens a safe repository descriptor; git-bound review also performs descriptor-relative bounded reads.
* Revise always validates output and performs bounded external-input reads, including external Review evidence.
* Apply always validates output, reads external evidence, and creates the apply operation.

Therefore the dependency object must be required and all direct callers must be updated in the same bounded repair.

## Required dependency contract

The previously selected architecture remains unchanged:

* `IssuePlanningDependencies` is application-owned.
* `IssuePlanningGateway` is application-owned.
* Structural candidate, publication, review, expected-target, operation, and execution views remain application-owned.
* Normalized application-port errors and their existing status/reason mappings remain unchanged.
* Bootstrap owns the concrete adapter and exception translation.
* Unknown concrete exceptions continue to propagate.

Each application entry point must accept the same required keyword-only argument with no default:

```python
dependencies: IssuePlanningDependencies
```

This applies to:

```text
run_issue_planning_create
run_issue_planning_review
run_issue_planning_revise
run_issue_planning_apply
```

`IssuePlanningDependencies` retains:

```text
clock: Clock
gateway: IssuePlanningGateway
```

The gateway retains the previously admitted operations:

```text
validate_candidate_output_directory
load_verified_issue_candidate
load_validated_issue_authoring_payload
build_and_publish_candidate
open_safe_directory_descriptor
read_bounded_regular_file
read_bounded_regular_file_at
read_external_review_result
publish_planning_review_evidence
load_expected_planning_targets
planning_apply_resume_available
create_planning_apply_operation
```

The existing application `Clock` protocol and `Ports` composition model remain the extension point.

There must be no application-layer concrete fallback. Concrete defaults are constructed only in provider `cli/bootstrap.py`, mechanically projected to dogfood bootstrap, and passed as one non-null dependency object to all four planning closures.

Existing explicit callable overrides remain valid test seams. When supplied, they continue to take precedence over the corresponding gateway method, but they do not make `dependencies` optional.

Every direct positive call in the allowed tests must explicitly pass an object conforming to the application-owned dependency contract. Negative tests that terminate before dependency use must also pass the same explicit fake where needed to preserve one uniform required signature. Application unit-test fakes must not depend on concrete infra modules; concrete infra and integration tests retain responsibility for concrete implementation behavior.

## Corrected exact 12-file allowlist

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/ports.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/bootstrap.py
spec-dock/scripts/spec_dock_runtime/application/ports.py
spec-dock/scripts/spec_dock_runtime/application/issue_planning.py
spec-dock/scripts/spec_dock_runtime/cli/bootstrap.py
tests/unit/application/test_issue_planning.py
tests/unit/application/test_issue_planning_apply.py
tests/cli_runtime/test_chatgpt_cli.py
tests/integration/test_issue_planning_chatgpt_transport.py
tests/integration/test_issue_planning_apply.py
tests/unit/infra/test_issue_planning_chatgpt.py
```

No thirteenth file is admitted.

## Frozen boundaries

* No production file beyond the three provider files and their three byte-identical dogfood projections may change.
* `infra.contracts`, all concrete infra implementation modules, commands, presentation, public request/result contracts, and public CLI files remain read-only.
* `tests/cli_runtime/test_runtime_shell_s11.py` remains read-only and must not be weakened, special-cased, or given an Issue Planning exemption.
* No concrete infra symbol or exception may be re-exported through an application-owned contract.
* Issue Planning orchestration remains in `application/issue_planning.py`.
* Bootstrap may compose dependencies and translate the previously enumerated concrete exceptions, but it may not make Candidate, Review, Human Gate, stale-state, or apply decisions.
* Existing CLI commands, arguments, output formats, exit behavior, schemas, Candidate identities, Review identities, Human Gate behavior, apply operation identity, resume behavior, transaction behavior, and rollback/recovery classifications remain unchanged.
* Every existing `PlanningCommandResult.status`, `reason`, `details`, and `output` mapping remains unchanged.
* Existing explicit callable overrides retain their behavior and precedence.
* Unknown exceptions must not be normalized or swallowed.
* Each provider/dogfood projection pair must remain byte-identical.
* The independent dirty exact12 repair must not be inspected, absorbed, or serialized into this repair.
* Any required change outside the exact 12-file allowlist is a stop condition.

## Corrected Green gates

All direct-call compatibility tests must pass together:

```text
python -m pytest -q \
  tests/unit/application/test_issue_planning.py \
  tests/unit/application/test_issue_planning_apply.py \
  tests/cli_runtime/test_chatgpt_cli.py \
  tests/integration/test_issue_planning_chatgpt_transport.py \
  tests/integration/test_issue_planning_apply.py \
  tests/unit/infra/test_issue_planning_chatgpt.py
```

The unchanged concrete behavior and end-to-end tests must remain green:

```text
python -m pytest -q \
  tests/unit/infra/test_issue_planning_candidate.py \
  tests/unit/infra/test_issue_planning_review.py \
  tests/unit/infra/test_issue_planning_apply.py \
  tests/integration/test_issue_planning_e2e.py
```

The original measured structural regression node must pass unchanged:

```text
python -m pytest -q \
  tests/cli_runtime/test_runtime_shell_s11.py::TestRuntimeShellS11::test_final_api_call_site_and_structural_regression
```

Provider/dogfood projection parity must pass for all three runtime pairs:

```text
cmp -s \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/ports.py \
  spec-dock/scripts/spec_dock_runtime/application/ports.py

cmp -s \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py \
  spec-dock/scripts/spec_dock_runtime/application/issue_planning.py

cmp -s \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/bootstrap.py \
  spec-dock/scripts/spec_dock_runtime/cli/bootstrap.py
```

DISPOSITION: GO_CORRECTED_BLOCKER_N_EXACT12
