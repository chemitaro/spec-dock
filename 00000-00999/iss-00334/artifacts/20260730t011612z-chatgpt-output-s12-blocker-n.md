# S12 Blocker N Amendment

## Source lock

* Repository: `chemitaro/spec-dock`
* Mandatory branch: `iss-00334-implement-chatgpt-issue-planning-workflow`
* Exact pushed HEAD: `fd97aca1f005e2fe066a872343039c7e5b8889ca`
* GitHub connector comparison: the mandatory branch and exact HEAD are identical; ahead `0`, behind `0`.
* Default-branch fallback: forbidden and not used. Every cited repository file was read at the exact HEAD.
* The independent dirty exact12 repair is excluded from this diagnosis and from the allowlist.
* Review scope is the bounded application/infra dependency defect defined by the admission brief. 

## Root cause

`application/issue_planning.py` imports concrete implementations and concrete implementation-owned types from four infra modules:

* `infra.clock`
* `infra.issue_planning_apply`
* `infra.issue_planning_candidate`
* `infra.issue_planning_review`

Those imports are not merely annotations. They bind concrete clocks, filesystem operations, archive loaders and publishers, review publication operations, apply factories, result types, and exception classes as module-level defaults. Bootstrap’s existing injection of the ChatGPT adapter, repository resolver, dependency loader, and transaction runner therefore does not remove the hidden concrete coupling.

The structural contract intentionally scans every import in every `application/*.py` module. An infra import is legal only when its normalized name is exactly `infra.contracts`; there is no exemption for default callables, type-only intent without `TYPE_CHECKING`, or Issue Planning.

The reported `infra.clock` failure is consequently only the first observed member of one defect class. Removing that import alone would expose the three remaining concrete infra imports.

## Admitted architecture repair

Admit repair shape **1**: extend the existing application dependency model with one narrowly scoped, application-owned Issue Planning port and compose it in `cli/bootstrap.py`.

### Application contract

Add these application-owned contracts to `application/ports.py`:

* `IssuePlanningDependencies`

  * `clock: Clock`
  * `gateway: IssuePlanningGateway`
* `IssuePlanningGateway`, a `Protocol` exposing only the operations required by `application/issue_planning.py`.
* Structural result views for values inspected by application orchestration:

  * `VerifiedIssueCandidateView`
  * `PublishedCandidateView`
  * `PublishedPlanningReviewView`
  * `ExpectedPlanningTargetsView`
  * `PlanningApplyOperationView`
  * `PlanningApplyExecutionView`
  * an opaque candidate-output guard token
* Application-owned normalized port errors:

  * `IssuePlanningCandidateArchiveRejected`, preserving `findings`
  * `IssuePlanningCandidateBuildFailed`
  * `IssuePlanningCandidateCollision`
  * `IssuePlanningCandidateOutputRejected`
  * `IssuePlanningCandidatePublicationFailed`
  * `IssuePlanningApplyOutputRejected`

Add `issue_planning: IssuePlanningDependencies | None = None` to the existing `Ports` dataclass. Keeping the field optional preserves all unrelated `Ports` construction sites. The repository already defines application-owned protocols, a clock port, and the composed `Ports` object in this module, so this extends the established pattern rather than adding a parallel framework.

### Exact operations crossing the port

`IssuePlanningGateway` shall expose these operations, using application-owned views rather than concrete infra types:

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

`create_planning_apply_operation` is the port operation bound to the existing concrete `PlanningApplyOperation.create`; the application must not import that class.

The existing separately injected dependencies remain separate:

```text
repo_slug_resolver
backend_invoker
dependency_loader
preflight_runner
prompt_synthesizer
transport_runner
transaction_runner
validation_runner
sync_runner
```

In particular, `transaction_runner` remains the explicit apply mutation boundary already wired by bootstrap. It is not absorbed into a generic gateway.

### Bootstrap composition

`cli/bootstrap.py` shall implement a private `_IssuePlanningGateway` adapter. Its methods bind the exact concrete implementations listed above and translate only the six known concrete infra exception classes into the corresponding application-owned port errors. Unknown exceptions must not be caught or rewritten.

`build_runtime` shall:

1. Construct one `_Clock`.
2. Construct one `_IssuePlanningGateway`.
3. Construct one `IssuePlanningDependencies(clock=..., gateway=...)`.
4. Store that dependency object on `Ports`.
5. Pass the same dependency object to planning create, review, revise, and apply.

Bootstrap is already the concrete composition root and already injects the ChatGPT adapter, repository resolution, dependency loading, and apply transaction runner.

### Application use

`application/issue_planning.py` shall:

* Remove all four concrete infra imports.
* Accept `IssuePlanningDependencies` on create, review, revise, and apply.
* Resolve the current concrete defaults through `dependencies.gateway` and `dependencies.clock.now_iso`.
* Preserve existing optional callable overrides. An explicitly supplied test callable continues to take precedence over the composed default.
* Pass the gateway into the bounded-file helper functions instead of importing concrete file helpers.
* Catch only application-owned normalized port errors.
* Type transaction results through `PlanningApplyExecutionView`.
* Retain all orchestration, decisions, status/reason mapping, and business behavior in the application module.

This is real dependency inversion: the application defines the required capability and failure vocabulary; bootstrap adapts concrete infra to it. No concrete implementation or concrete exception class is re-exported through another module.

### Test injection

Application unit tests shall construct local fake `Clock`, `IssuePlanningGateway`, and `IssuePlanningDependencies` objects using the application contract only. Fakes may:

* return local structural candidate, publication, expected-target, operation, and execution objects;
* raise the application-owned normalized errors;
* record calls and inputs;
* combine with the existing explicit callable overrides.

Application-orchestration tests therefore need no concrete infra import. Concrete infra tests and end-to-end tests remain responsible for exercising the real implementations. Existing tests already demonstrate explicit fake candidate loaders, expected-target loaders, resume probes, clocks, preflight runners, and transaction runners; the new dependency object consolidates only the missing default boundary.

## Exact file allowlist

Only these nine files are admitted.

Provider authority:

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/ports.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/bootstrap.py
```

Mechanical dogfood projections:

```text
spec-dock/scripts/spec_dock_runtime/application/ports.py
spec-dock/scripts/spec_dock_runtime/application/issue_planning.py
spec-dock/scripts/spec_dock_runtime/cli/bootstrap.py
```

Focused tests:

```text
tests/unit/application/test_issue_planning.py
tests/unit/application/test_issue_planning_apply.py
tests/cli_runtime/test_chatgpt_cli.py
```

The three projection pairs must be byte-identical. At the locked HEAD, each pair already has the same Git blob identity:

* provider/dogfood `application/ports.py`: `4d689e7101399735f079c20ff05da4af327603db`
* provider/dogfood `application/issue_planning.py`: `9a09d25183df3708029e953b03b3b03a0cc73aa7`
* provider/dogfood `cli/bootstrap.py`: `80b1249d1b3916e616a7340187d14ac0217bf078`

No new file is admitted. In particular, the following remain read-only:

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/contracts.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/clock.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_candidate.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_review.py
tests/cli_runtime/test_runtime_shell_s11.py
```

## Frozen behavior

The repair must preserve all of the following exactly:

* Public `spec-dock-chatgpt` commands, options, exit behavior, and output formats.
* Planning request and result classes.
* Candidate identity, archive validation, collision handling, publication, and output paths.
* Review identity, evidence construction, summary rendering, publication, and stale detection.
* Human Gate validation and decision semantics.
* Apply operation identity, resume behavior, preimage checks, transaction execution, rollback/recovery classifications, and publication behavior.
* Every existing `PlanningCommandResult.status`, `reason`, `details`, and `output` mapping.
* Existing exception distinctions:

  * archive rejection remains rejected with its findings;
  * output rejection and collision remain rejected;
  * build and publication failures remain blocked;
  * apply-output rejection remains rejected;
  * unmapped or unexpected exceptions continue to propagate.
* Existing explicit fake-callable seams.
* Existing ChatGPT, GitHub preflight, repository-resolution, validation, synchronization, and transaction injection.
* Provider authority under `src/spec_dock/assets/` and byte-identical dogfood projection.
* The structural regression test without deletion, weakening, allowlisting, or Issue Planning special cases.
* All orchestration in `application/issue_planning.py`; no business behavior moves into bootstrap, commands, presentation, or infra.

## Red and Green gates

### Measured Red

The required starting red is:

```text
python -m pytest -q \
  tests/cli_runtime/test_runtime_shell_s11.py::TestRuntimeShellS11::test_final_api_call_site_and_structural_regression
```

At the locked HEAD it fails first on:

```text
application layer must not import infra concrete module:
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py:
spec_dock_runtime.infra.clock
```

### Focused Green

The bounded implementation must pass:

```text
python -m pytest -q \
  tests/unit/application/test_issue_planning.py \
  tests/unit/application/test_issue_planning_apply.py \
  tests/cli_runtime/test_chatgpt_cli.py
```

The bootstrap test must additionally prove that create, review, revise, and apply receive the same non-null composed `IssuePlanningDependencies` object. The existing bootstrap test already exercises all four use-case closures and is the correct bounded location for that assertion.

Concrete behavior must remain green without modifying its tests:

```text
python -m pytest -q \
  tests/unit/infra/test_issue_planning_candidate.py \
  tests/unit/infra/test_issue_planning_review.py \
  tests/unit/infra/test_issue_planning_apply.py
```

The existing integration chain must remain green:

```text
python -m pytest -q \
  tests/integration/test_issue_planning_apply.py \
  tests/integration/test_issue_planning_chatgpt_transport.py \
  tests/integration/test_issue_planning_e2e.py
```

The explicit full-regression node must then pass unchanged:

```text
python -m pytest -q \
  tests/cli_runtime/test_runtime_shell_s11.py::TestRuntimeShellS11::test_final_api_call_site_and_structural_regression
```

Each provider/dogfood pair must also pass a byte-for-byte comparison.

### Stopping conditions

Stop and return the work for a new amendment if any of these occurs:

* Implementation is not based on the locked branch and HEAD.
* Any concrete `infra.*` import other than exact `infra.contracts` remains in `application/issue_planning.py`.
* Repair requires modifying `infra.contracts`, a concrete infra implementation, the structural regression test, commands, presentation, or public contracts.
* A concrete implementation or exception is merely re-exported through an allowed module.
* Bootstrap must catch an unknown exception or alter its public classification.
* A public request, result, CLI, reason, status, detail, or output changes.
* Business decisions or orchestration must move out of the application layer.
* Unit fakes cannot be expressed against the application-owned port.
* Any provider/dogfood pair differs after projection.
* Any focused, integration, or explicit full-regression gate remains red.
* Work must extend outside the exact allowlist.

## Rejected alternatives

### Option 2: use `infra.contracts` as an Issue Planning façade

Rejected. The current `infra.contracts` module contains neutral shared records such as `StoredMetaRecord`, `DirectDependencyResolution`, manifests, and state snapshots; it is not a concrete composition boundary.

Re-exporting candidate, review, apply, filesystem, or clock implementations through it would make the AST test green while retaining the same hidden dependency. Moving all Issue Planning protocols, errors, and result views into that infra-owned module would also invert ownership incorrectly and enlarge a repository-wide shared boundary.

### Keep every concrete dependency as an individual function parameter

Rejected as the primary shape. Making every current default a separately required parameter would technically remove imports, but it would expand four large signatures, duplicate bootstrap wiring, and scatter one cohesive dependency boundary across many call sites. A single narrow dependency object preserves existing explicit override seams while centralizing only the missing defaults.

### Move concrete types or implementations into application or domain

Rejected. Candidate filesystem handling, review publication, apply transactions, and clock implementations are correctly owned by infra. Relocating them would broaden the repair, disturb concrete infra tests, and violate the frozen architecture.

### Move orchestration into bootstrap, commands, or presentation

Rejected. Bootstrap may compose and adapt dependencies but must not own Candidate, Review, Human Gate, stale-state, or apply decisions.

### Weaken or special-case the structural test

Rejected. The test states the accepted layered architecture and accurately detected four concrete-module dependencies. An exemption would conceal the defect rather than repair it.

DISPOSITION: GO_BOUNDED_BLOCKER_N_APPLICATION_INFRA_BOUNDARY
