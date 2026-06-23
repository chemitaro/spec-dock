---
種別: disc
ID: "20260623t-design-static-analysis-architecture-review"
title: "Static analysis architecture review"
タイトル: "Static analysis architecture review"
authority: proposed
adoption_status: unreviewed
reflected_to: []
created_by_role: system-architect
scope_id: iss-00225
source_paths:
  - spec-dock/active/context-pack.md
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/report.md
  - spec-dock/active/issue/discussions/20260623t024024z-research-ruff-mypy-preference-source-analysis.md
  - spec-dock/active/issue/discussions/20260623t024210z-interview-static-analysis-target-boundary.md
  - spec-dock/active/issue/discussions/20260623t025015z-interview-static-analysis-enforcement-entrypoint.md
  - spec-dock/active/issue/discussions/20260623t030652z-disc-static-analysis-final-configuration-proposal.md
  - AGENTS.md
  - pyproject.toml
intended_targets:
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/report.md
diff_guard_result: passed
---

# 20260623t-design Static analysis architecture review

## Summary of Reviewed Sources
- `requirement.md`: Ruff / mypy dependency and configuration, Option B target boundary, `make lint`, grouped script, provider CI gate, staged violation inventory, dogfooding impact evidence, and final green baseline are required. It records a fresh requirement spec-reviewer pass in `report.md`.
- `design.md`: centralizes tool configuration in `pyproject.toml`, adds `scripts/static_analysis/run.sh`, root `Makefile` `lint`, provider CI `make lint`, staged rule adoption, format isolation, mypy settings, direct exclusion of `spec-dock/`, and dogfooding inspection when shipped runtime assets change.
- `plan.md`: decomposes implementation into dependency/command skeleton, rule-by-rule Ruff adoption, mypy inventory/fix, format isolation, final `make lint`, CI wiring, dogfooding evidence, and final quality gate.
- Prior discussions: research translates the reference project's Ruff/mypy preferences to SpecDock; interviews adopt Option B target boundary and CI + local grouped script while excluding pre-commit; final configuration proposal supplies the intended rule set and command shape.
- `AGENTS.md` and `pyproject.toml`: confirm provider source-of-truth under `src/spec_dock/`, dogfooding workspace under `spec-dock/`, Python `>=3.10`, current absence of Ruff/mypy/Makefile/static-analysis script.

This artifact is evidence only. It is not a reviewer pass and does not approve, promote, or modify canonical documents.

## Findings / Recommendations Ordered by Severity

### No blocking finding
- Severity: none.
- Finding: The current `design.md` is sufficient for canonical design review input.
- Reason: It covers the essential architecture: central `pyproject.toml` configuration, one local grouped command, CI reuse of that command, staged rule adoption, Option B target boundary, direct dogfooding exclusion, and report evidence for generated-copy impact.
- Recommendation: Adopt the design as-is for review. No required canonical `design.md` edits are identified.

### Low: clarify that layer-specific banned-api rules are intentionally deferred
- Severity: low / optional.
- Finding: The design adopts `TID` and relative-import banning but does not explicitly say that reference-project layer-specific `banned-api` overrides are not part of this issue.
- Why it matters: The research notes the reference project uses layer/bounded-context banned APIs. Without an explicit sentence, an implementer could over-expand `TID` into SpecDock layer-boundary policy work.
- Recommendation: Optional only. If the main orchestrator wants extra guardrail text, add one sentence to `Final Pyproject Configuration Design` or `採用しないもの`: "SpecDock layer-specific banned-api policy is not introduced in this issue; `TID` adoption is limited to tidy imports / relative import discipline unless a later design amendment promotes boundary rules."

### Low: keep direct command targets non-duplicated
- Severity: low / already handled.
- Finding: The final configuration proposal listed the shipped runtime asset as an explicit direct target, while `design.md` correctly reduces command targets to `src/spec_dock` and `tests` because the shipped runtime asset is already under `src/spec_dock`.
- Recommendation: Keep the `design.md` approach. It avoids duplicate Ruff/mypy traversal while still making coverage explicit in report evidence.

## Canonical Adoption Recommendation
- Recommendation: adopt.
- Required canonical changes: none.
- Optional canonical refinement:
  - `design.md` section `採用しないもの` or `Final Pyproject Configuration Design / Ruff sub-settings`: add the low-severity banned-api deferral sentence above if the orchestrator wants to prevent scope creep.
- `plan.md`: no required change. The plan already keeps rule-by-rule adoption and amendment triggers.
- `report.md`: if this artifact is considered during review, add an Evidence Adoption Ledger entry with `adoption_status=adopted` or `deferred` according to the orchestrator's decision.

## Requirement Coverage
- AC-001: Covered by dev dependencies and final `pyproject.toml` Ruff/mypy settings.
- AC-002: Covered by Option B target design, `src/spec_dock` / `tests` command targets, shipped runtime coverage note, and `spec-dock/` exclusion.
- AC-003: Covered by `scripts/static_analysis/run.sh` and root `Makefile` `lint`.
- AC-004: Covered by provider CI running `make lint`.
- AC-005/AC-006: Covered by staged Ruff and mypy adoption with inventory and zero confirmation.
- AC-007: Covered by isolated Ruff format step.
- AC-008: Covered by final `make lint`, individual Ruff/mypy checks, pytest, and `spec-dock validate`.
- AC-009: Covered by narrow ignore policy and report evidence for suppressions.

## Existing Context Findings
- `pyproject.toml` currently has pytest only; the design's config-first approach is appropriate.
- `AGENTS.md` strongly supports provider-first changes and dogfooding inspection rather than direct generated-copy linting.
- Existing report ledger already records the key user decisions and the requirement reviewer pass; design/plan reviewer gates are still pending.

## Design Decisions
- Use `pyproject.toml` as the tool configuration source of record.
- Use a grouped static-analysis script as the local contract and have `make lint` call it.
- Reuse `make lint` in provider CI to avoid local/CI drift.
- Enable Ruff rules in reviewable increments and separate format-only changes.
- Keep `spec-dock/` outside direct Ruff/mypy targets.

## Alternatives Considered
- One-shot final configuration: rejected by current design because it would mix unrelated violation classes and create a large review surface.
- Full dogfooding direct target: rejected by user-approved Option B to avoid generated-copy source-of-truth confusion.
- Pre-commit integration: correctly deferred to a separate issue.
- Layer-specific banned-api policy: not required for this issue; optional future design/ADR candidate.

## Boundary / Contract Model
- Public command contract: `make lint` returns non-zero if any static-analysis phase fails and prints a summary.
- Script contract: `scripts/static_analysis/run.sh` runs Ruff check, Ruff format check, and mypy, continuing to later phases where practical.
- Config contract: `pyproject.toml` owns Ruff/mypy behavior.
- CI contract: provider CI calls the same local command.
- Dogfooding contract: generated `spec-dock/` is inspected/validated when shipped runtime assets change but is not a direct static-analysis target.

## Dependency Analysis
- Configuration and dependencies must precede any static-analysis command.
- Local script and `Makefile` should be stable before CI wiring.
- Ruff semantic rules should precede mypy and format-only cleanup.
- CI should be wired after the local command is green to avoid a broken duplicated command surface.

## Source of Record
- Canonical source remains `requirement.md`, `design.md`, `plan.md`, and later `report.md`.
- This discussion draft is non-canonical evidence for the main orchestrator.
- `pyproject.toml`, `scripts/static_analysis/run.sh`, `Makefile`, and provider CI will become implementation surfaces only during issue execution.

## Data Flow / Domain Model / Interface Contract
```text
developer / CI
  -> make lint
  -> scripts/static_analysis/run.sh
  -> pyproject.toml tool settings
  -> src/spec_dock and tests
  -> command summary / exit code
  -> report.md evidence during implementation
```

## File / Module Change Plan
- No canonical or implementation changes are made by this draft.
- Current design's future implementation plan remains:
  - modify `pyproject.toml`;
  - add `scripts/static_analysis/run.sh`;
  - add root `Makefile`;
  - update `.github/workflows/provider-ci.yml`;
  - fix violations in `src/spec_dock/**/*.py` and `tests/**/*.py`;
  - inspect dogfooding impact when shipped runtime assets change.

## Migration / Compatibility / Rollback
- Python compatibility is aligned with `requires-python = ">=3.10"` via `py310` / `3.10`.
- Rollback can remove one rule group or defer a problematic rule through plan amendment.
- Dogfooding rollback is avoided by not directly editing generated copies for lint/type fixes.

## Observability
- The design's main observability surface is command output plus `report.md` violation inventory.
- CI logs provide PR-level enforcement evidence.
- Dogfooding impact evidence should be recorded when shipped runtime asset diffs appear.

## Test Strategy
- Static checks: `uv run ruff check src/spec_dock tests`, `uv run ruff format --check src/spec_dock tests`, `uv run mypy src/spec_dock tests`, and `make lint`.
- Regression checks: `uv run pytest`.
- SpecDock checks: `./spec-dock/scripts/spec-dock validate`.
- Review checks: inspect ignore/suppression diffs for scope and rationale.

## ADR Candidates
- Not required for this issue.
- Potential future ADR: whether SpecDock should encode runtime layer boundaries as Ruff `banned-api` rules or another architecture-check mechanism.

## Risks
- Ruff preview rules may produce churn; staged adoption and amendment triggers mitigate this.
- Mypy may produce package/path noise from shipped runtime assets; command target and exclude design mitigate this.
- Format-only churn could obscure semantic fixes; isolated formatting step mitigates this.
- Generated-copy stale risk remains if shipped runtime assets change; dogfooding inspection evidence mitigates this.

## Requirement Clarification Requests
- none.
- Existing issue materials already resolve target boundary and enforcement entrypoint.

## Integration Notes for Main Orchestrator
- Treat this artifact as design-review preparation evidence only.
- Canonical adoption recommendation is `adopt`.
- No required `design.md` edits are recommended.
- Optional refinement is limited to clarifying that layer-specific banned-api policy is deferred.
- A fresh spec-reviewer pass remains required before design approval or execution handoff.

## Explicit Non-Reviewer Note
- This is not a spec-reviewer pass.
- This does not claim canonical approval, phase promotion, implementation readiness, or final authority.
