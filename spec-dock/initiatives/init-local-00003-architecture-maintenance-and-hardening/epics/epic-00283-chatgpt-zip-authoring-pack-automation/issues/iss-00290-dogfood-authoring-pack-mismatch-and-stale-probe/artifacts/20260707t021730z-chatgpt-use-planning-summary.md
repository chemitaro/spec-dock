# ChatGPT Use planning summary for iss-00290

Session: `specdock-iss-00290-planning`

## Adopted recommendation

ChatGPT Use recommended treating `iss-00290` as a dogfood evidence Issue, not as a new runtime behavior Issue. The smallest path is to use existing validators to prove fail-closed behavior and store durable Issue-local evidence.

## Key guidance adopted

- Keep implementation out of `src_spec_dock` runtime paths.
- Prefer Issue-local artifacts and `report.md` updates.
- Add tests or source changes only when evidence exposes a real gap.
- Distinguish `failure_class` from validator `status`; source/profile mismatch may remain `stale` while summary records the semantic class.
- Include stage-attempt evidence showing `stale` / `rejected` reports do not produce staged artifacts.

## Local adoption decision

- Adopted: negative probe artifact package under `artifacts/20260707t020429z-negative-probe-dogfood/`.
- Adopted: `block-disposition-summary.json` / `.md`.
- Adopted: stage-attempt stale review evidence.
- Adopted: a small trace fallback fix for early stale selected skeleton validation reports, because local dogfood exposed a trace mismatch before selected skeleton loading.

## Non-adopted or deferred

- Runtime promotion: deferred outside this Issue.
- New public command: deferred outside this Issue.
- Broad new validators: not needed for this Issue unless final reviewers find a gap.

## Verification focus

- Negative cases must not return `pass`.
- Negative cases must not produce staged adoption artifacts.
- `.assurance.json` and canonical docs must not be mutated.
- Artifact evidence must not claim reviewer pass, canonical adoption, PR creation, or runtime availability.
