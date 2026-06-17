---
種別: disc
ID: "20260617t043551z-disc"
タイトル: "PR Repair Unit U001"
状態: "proposed"
作成者: "iwasawayuuta"
最終更新: "2026-06-17"
親: ["iss-00188"]
関連:
  - "20260617t043527z-pr-repair-batch"
authority: "proposed"
derived_from:
  - "https://github.com/chemitaro/spec-dock/pull/195"
  - "/private/tmp/pr-195-observation/result.json"
reflected_to: []
---

# PR Repair Unit U001

## source_batch
- `20260617t043527z-pr-repair-batch`

## unit_id
- U001

## covered_ids
- I001

## source_links
- PR: https://github.com/chemitaro/spec-dock/pull/195
- Failed run: https://github.com/chemitaro/spec-dock/actions/runs/27665658157/job/81818953487
- Observation evidence: `/private/tmp/pr-195-observation/result.json`

## failure_class
- `check_failure:provider-tests`

## risk_class
- `blocking`

## disposition
- `fix-now`

## Validity Analysis
- Valid CI failure.
- `tests/cli_runtime/test_runtime_shell_s11.py::TestRuntimeShellS11::test_final_api_call_site_and_structural_regression` asserts `commands/*` does not directly import `domain`, `infra`, or `app`.
- CI log shows `commands/new.py` imports `domain.discussion_docs`, so the new shared catalog usage violates the existing runtime layering contract.

## Need-To-Fix Decision
- Need to fix now.
- The failing `provider-tests` check blocks merge-prepared status.

## Root Cause
- S02/S04 made `commands/new.py` use the shared discussion doc catalog for help text.
- The helper was placed under `domain/discussion_docs.py`, and importing it from `commands/new.py` crosses the thin shell layer boundary.

## Options Considered
- Move help text back to a command-local constant:
  - Pros: minimal and satisfies layer rule.
  - Cons: reintroduces catalog drift risk.
- Move the help-facing catalog into a command-safe contract/presentation boundary:
  - Pros: preserves shared behavior without forbidden import.
  - Cons: may broaden the repair beyond the CI failure.
- Change the structural test:
  - Rejected. The test encodes an accepted architecture guardrail.

## Recommended Design
- Preserve the architecture guardrail and avoid broad refactor.
- Remove the forbidden `domain` import from `commands/new.py`.
- Keep `pr-repair-batch` visible in CLI help and keep runtime/validation behavior unchanged.
- Prefer a minimal command-safe source for the help catalog that does not import `domain`, or route the value through an already allowed layer if one exists locally.

## Implementation Plan
1. Inspect `commands/new.py`, `domain/discussion_docs.py`, and nearby CLI/help patterns.
2. Remove the direct `domain.discussion_docs` import from `commands/new.py`.
3. Preserve `new doc` help output including `pr-repair-batch`.
4. Run:
   - `uv run pytest tests/cli_runtime/test_runtime_shell_s11.py::TestRuntimeShellS11::test_final_api_call_site_and_structural_regression`
   - relevant focused `new doc` tests.
   - `git diff --check`

## Validation Plan
- Local structural regression must pass.
- Focused new-doc tests must still prove `pr-repair-batch` appears in help and creates valid artifacts.
- After commit/push, rerun PR observation for latest head SHA.

## Implementation Result
- Removed the direct `domain.discussion_docs` import from provider and dogfooding `commands/new.py`.
- Restored a command-local help tuple that includes `pr-repair-batch` and approved draft doc types.
- Runtime creation and validation behavior remains application/domain-owned.
- Local verification:
  - `uv run pytest tests/cli_runtime/test_runtime_shell_s11.py::TestRuntimeShellS11::test_final_api_call_site_and_structural_regression` -> 1 passed.
  - `uv run pytest tests/cli_runtime/test_new.py tests/cli_runtime/test_runtime_new_doc_s09.py tests/cli_runtime/test_validate.py` -> 100 passed, 11 skipped.
  - `git diff --check` -> pass.
  - `./spec-dock/scripts/spec-dock validate` -> pass, `nodes=97`.

## Commit Evidence
- Repair code-reviewer `019ed3e4-f446-7b13-b18f-c29578773018` passed with findings=[].
- Commit pending.

## Re-observation Result
- pending PR re-observation after repair commit/push.

## Residual Risk / Follow-up
- Future creatable doc type additions must keep command help text in sync. If this becomes recurring drift, move the help-facing catalog to an approved command-safe contract.
