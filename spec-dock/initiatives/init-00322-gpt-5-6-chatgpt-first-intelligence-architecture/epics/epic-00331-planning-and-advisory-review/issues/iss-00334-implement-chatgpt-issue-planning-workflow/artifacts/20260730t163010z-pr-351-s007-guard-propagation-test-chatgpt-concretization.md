# Oracle Browser Transcript

Conversation: https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a6b79f1-d230-83e8-8c1c-324c87caf9a2

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

S007 bounded task: prove by object identity that the validated opaque output guard reaches both the application resume probe and transaction runner. Use the attached prompt as the complete task brief, inspect the required GitHub branch first, and return only the implementation work packet.

## Answer

## Implementation work packet

### Baseline

GitHub access succeeded for `chemitaro/spec-dock`. PR `#351` identifies the required branch as `iss-00334-implement-chatgpt-issue-planning-workflow` at exact HEAD `91715eecf306bd0c978da922f87193151764cdcd`.

### Assessment

The P1 is a **test-protection gap only**. The attached S007 implementation retains the return value from `validate_candidate_output_directory` in `output_guard` and forwards that same reference to `resume_probe` and both `transaction_runner` call sites. No production-code change is required, and no additional P0/P1 defect blocks this test. 

### Test target and seam

Modify only:

`tests/unit/application/test_issue_planning_apply.py`

Extend its existing `_run(...)` helper. `_run` already owns the injected `resume_probe` and `transaction_runner`, but currently the probe discards all keyword arguments and the transaction double records only the operation.  

Add narrowly scoped optional seams while preserving all existing defaults:

* an optional `IssuePlanningDependencies` override;
* an optional resume-probe override;
* an optional transaction-boundary observer or runner override.

Existing callers must continue to receive the same four-value return tuple and unchanged default execution behavior.

### Regression test

Add one test, for example:

`test_apply_propagates_validated_output_guard_by_identity`

Setup:

1. Create `opaque_guard = object()`.
2. Define a local `_FakeIssuePlanningGateway` subclass whose `validate_candidate_output_directory`:

   * first calls the existing implementation to retain normal path validation;
   * then returns `opaque_guard` instead of the resolved `Path`.
3. Construct `IssuePlanningDependencies(clock=_FakeClock(), gateway=<that gateway>)`.
4. Supply a resume probe that records its `output_guard` argument and returns `False`. Returning `False` deliberately exercises the complete preflight/revalidation path before transaction execution.
5. Supply a transaction observer/runner that records its `output_guard` argument and otherwise returns the existing successful `_PlanningApplyExecution`.

Required assertions:

```python
assert (result.status, result.reason) == ("ready", "adoption_published")
assert len(calls) == 1

assert len(resume_guards) == 1
assert len(transaction_guards) == 1

assert resume_guards[0] is opaque_guard
assert transaction_guards[0] is opaque_guard
assert resume_guards[0] is transaction_guards[0]
```

Use `is`, not equality, for all three guard assertions. This causes the test to fail if the application discards the validated token, substitutes `request.output_dir`, reconstructs another guard, or performs any copy/replacement before either boundary. This is the exact bounded protection requested by the task. 

### Production changes

None. Do not modify the application, port, guard protocol, public status/reason/schema, or Oracle/configuration behavior.

### Verification

```bash
uv run pytest -q \
  tests/unit/application/test_issue_planning_apply.py::test_apply_propagates_validated_output_guard_by_identity

uv run pytest -q tests/unit/application/test_issue_planning_apply.py

uv run ruff check tests/unit/application/test_issue_planning_apply.py
uv run ruff format --check tests/unit/application/test_issue_planning_apply.py
uv run mypy tests/unit/application/test_issue_planning_apply.py

git diff --check -- tests/unit/application/test_issue_planning_apply.py
```

These commands are prescribed verification and were not executed in this consultation.
