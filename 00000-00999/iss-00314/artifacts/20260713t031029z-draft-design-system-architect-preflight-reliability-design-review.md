---
created_by_role: system-architect
scope_id: iss-00314
source_paths:
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/design.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00295-chatgpt-authoring-pack-installed-runtime/requirement.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00295-chatgpt-authoring-pack-installed-runtime/design.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00295-chatgpt-authoring-pack-installed-runtime/issues/iss-00314-harden-github-sync-preflight-fetch-and-receipt-contract/artifacts/20260713t014710z-research-chatgpt-pro-github-sync-preflight-reliability-analysis.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00295-chatgpt-authoring-pack-installed-runtime/issues/iss-00314-harden-github-sync-preflight-fetch-and-receipt-contract/artifacts/20260713t024106z-research-chatgpt-pro-issue-planning-candidate-set.md
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/authoring_pack/github_sync_preflight.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/preflight_contract.py
intended_targets:
  - issue design.md
  - issue plan.md
  - provider runtime and its dogfood projection
adoption_status: unreviewed
reflected_to: []
diff_guard_result: passed
---

# System-architect review: preflight reliability design

## 1. Requirement Coverage

The requirement correctly preserves mandatory `git fetch --prune origin`, fail-closed `github-synced` semantics, explicit `local-context`, secret redaction, safe output ownership, and post-fetch repository/source evidence. It also identifies retry, typed diagnostics, receipt publication, and TOCTOU as the missing contract. This review covers design only; it does not adopt the candidate claims.

## 2. Existing Context Findings

`github_sync_preflight.py` currently orchestrates request validation, one `_refresh_origin()` subprocess, ref observation, and result construction. `PreflightResult` has no fetch-attempt, classification, snapshot, schema, or publication fields. The command renders stdout and the existing application has no dedicated receipt writer. Existing tests already exercise the CLI and `--output-dir` in nearby authoring flows, so compatibility must be checked rather than assumed. The ChatGPT research is useful evidence, but its suggested timeout/retry values are not repository facts.

## 3. Design Decisions

1. Keep orchestration in `application/authoring_pack/github_sync_preflight.py`; add small typed contracts in `domain/authoring_pack/preflight_contract.py` and a filesystem adapter in `infra/` for atomic receipt publication. Do not create a generic workflow framework.
2. Introduce `FetchAttempt`/`FetchOutcome` (argv identity, exit/timeout, duration, conservative classification, confidence, retry decision) and `RepositorySnapshot` (before/after identity). Keep raw stderr ephemeral and redact bounded diagnostic text before persistence.
3. A single preflight transaction owns fetch, optional one retry, post-fetch observation, TOCTOU comparison, result evaluation, and publication. Retry uses exactly the same executable, argv, cwd, environment policy, permission shape, and output policy; no escalation or fallback.
4. Receipt publication is opt-in via `--output-dir`, writes a fixed filename through same-directory temporary file + flush/fsync + atomic replace, refuses canonical paths, symlinks, traversal, and outside-repository destinations, and never changes command success semantics when publication itself is blocked (it must add a typed blocker).

## 4. Alternatives Considered

- Caller-owned retry/raw `git fetch`: rejected; recreates the incident and breaks capability invariance.
- Treat cached refs as success after fetch failure: rejected; violates freshness.
- Shell redirect/pipe or automatic `require_escalated`: rejected; changes command shape and leaks authority to the caller.
- Large new service layer: rejected; unnecessary coupling. A narrow adapter and immutable dataclasses are sufficient.

## 5. Boundary / Contract Model

CLI parses `--output-dir` into a request. Application service calls a Git executor, snapshot observer, evaluator, then receipt writer. Domain types carry only sanitized, serializable data. Presentation renders the same `PreflightResult` as JSON/text. `pack prepare` must accept only a receipt whose schema, repository identity, source hash, and completed post-fetch observation bind to its input; it must not infer freshness from fields omitted by older receipts.

## 6. Dependency Analysis

Provider assets are authoritative; `spec-dock/` is a generated dogfood projection. Application/domain/infra/presentation tests must cover both installed runtime and projection. No new external dependency is required. A receipt schema change affects `pack prepare` and any fixtures; it must be versioned and backward compatibility explicitly tested.

## 7. Source of Record

Normative order remains ADR/initiative/epic, then requirement, design, plan. The two ChatGPT artifacts are evidence only. This draft itself is unreviewed and must enter the report Evidence Adoption Ledger before any canonical edit.

## 8. Data Flow / Domain Model / Interface Contract

`Request -> pre_snapshot -> FetchAttempt[] -> post_snapshot -> concurrent_change check -> status evaluation -> sanitized Receipt -> atomic publish/stdout`.

Classification must be conservative: `timeout`, `authentication`, `configuration`, `lock`, `transport`, `policy`, and `unknown` are observations, not guesses. Only an explicitly allow-listed transient transport case may retry once; timeout/auth/config/lock/unknown block without retry. Exit code and bounded diagnostic fingerprint may be persisted, never credentials or full output.

## 9. File / Module Change Plan

- Domain: extend preflight contracts with schema version, fetch outcomes, snapshots, and publication evidence.
- Application: replace string `_refresh_origin` result with typed executor outcome; take snapshots immediately before and after fetch and compare identity.
- Infra: add Git executor (fixed argv, `GIT_TERMINAL_PROMPT=0`, timeout) and receipt writer (safe destination + atomic replace).
- CLI/presentation: add explicit `--output-dir`; preserve existing stdout fields and exit codes unless a new typed blocker is required.
- Tests: unit-test classification/writer/path safety; CLI-test retry, timeout, blocked receipt, TOCTOU, and old payload compatibility; refresh provider projection only after provider tests pass.

## 10. Migration / Compatibility / Rollback

Use additive JSON fields and a schema version. Existing consumers continue to read status/blockers; consumers requiring freshness must reject receipts without the new binding fields. Rollback is code-only: disable new receipt publication while retaining mandatory fetch; do not delete or rewrite existing receipts.

## 11. Observability

Expose attempt count, elapsed duration, exit/timeout state, classification/confidence, retry decision, snapshot identities, publication path (repository-relative), and blocker codes. Keep URLs, environment, stdout/stderr, and secret-bearing helper output out of durable artifacts.

## 12. Test Strategy

Use hermetic fake executors and temporary repositories. Prove fixed argv/environment and same-capability retry; prove no retry for auth/config/lock/unknown; prove timeout is bounded; prove atomic writer rejects symlink/traversal/canonical destinations; prove failed fetch never yields `verified`; mutate branch/HEAD/ref/source between snapshots to prove `concurrent_repo_change`; run provider and installed-runtime regression lanes.

## 13. ADR Candidates

Record an ADR only if the project wants the receipt schema, retry allow-list, or output ownership to become a cross-Issue contract. Otherwise keep these decisions Issue-local and trace them in design/plan.

## 14. Risks

Git stderr classification is inherently heuristic; default to `unknown` and block. Git operations may update refs while snapshots run; compare all identity fields and treat any mismatch as concurrent change. Atomic replace semantics differ across filesystems; require same-directory temporary files and test supported platforms. The requirement's exact retry categories, timeout, filename, and schema fields remain unspecified and must be resolved before implementation.

## 15. Requirement Clarification Requests

Resolve (a) timeout value and whether timeout classification is always non-retryable, (b) exact transient allow-list, (c) receipt filename/schema version, (d) whether publication failure changes process exit code, and (e) snapshot fields sufficient for source-manifest binding. Do not silently invent these values from ChatGPT output.

## 16. Integration Notes for Main Orchestrator

Adopt only claims corroborated by repository code/tests and record accepted/rejected items in `report.md`. Update canonical design/plan with the narrow module split and transaction boundary above, then obtain a fresh `spec-reviewer` pass. Do not treat this artifact as execution-ready.

**Diff guard:** only this pre-existing scope-local artifact was replaced; no canonical docs, code, tests, GitHub state, or metadata were edited. `adoption_status: unreviewed`, `reflected_to: []`.

No canonical edit, final authority, promotion, reviewer-pass, or user-dialogue ownership is claimed.
