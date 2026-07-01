---
種別: ADR
ID: "adr-20260701t072851z-artifact-domain-filename-template-contract"
タイトル: "Artifact domain, filename, and draft template contract"
状態: "accepted"
authority: "accepted"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
親: ["epic-00259", "init-local-00003"]
supersedes_issue: ["iss-00261", "#261"]
---

# ADR: Artifact domain, filename, and draft template contract

## Status
Accepted.

## Context
The first issue decomposition created `iss-00261` as an implementation Issue for the artifact domain model and filename contract. That split was structurally wrong: this contract determines the Epic's scope, command behavior, validation behavior, template routing, Issue dependencies, and final quality gate.

Therefore the contract must be owned by this Epic through ADR authority and reflected into the Epic requirement, design, plan, and the remaining executable Issues. `iss-00261` / GitHub `#261` is abolished as a child implementation Issue for this Epic.

## Decision
- The artifact domain and filename contract is an Epic-level decision, not a child Issue deliverable.
- `Artifact` and `DiscussionDoc` remain separate domain concepts.
  - `Artifact` is future scope-local working evidence under `artifacts/`.
  - `DiscussionDoc` is legacy scope-local working evidence under `discussions/`.
  - Canonical `requirement.md`, `design.md`, `plan.md`, and `report.md` are not artifacts.
- The future artifact catalog is:
  - `blank`
  - `research`
  - `interview`
  - `disc`
  - `decision-candidate`
  - `pr-repair-batch`
  - `adr`
  - `draft-requirement`
  - `draft-design`
  - `draft-plan`
- `scratch` is legacy-only and must not be added to the future `new artifact` catalog.
- Artifact filenames use these patterns:
  - typed artifacts: `<timestamp>-<type>-<slug>.md`
  - typed collision suffix: `<timestamp>-<nn>-<type>-<slug>.md`
  - blank artifacts: `<timestamp>-<slug>.md`
  - blank collision suffix: `<timestamp>-<nn>-<slug>.md`
- `blank` omits `blank` from the filename, but its frontmatter records `template: "blank"`.
- Artifact validation must detect malformed artifact-intent filenames and duplicate artifact ids without weakening legacy `discussions/` validation.
- ADR originals may live in future `artifacts/` or legacy `discussions/`; ADR mirror collection must collect both without moving originals.
- `draft-requirement`, `draft-design`, and `draft-plan` are created by `new artifact`, but they do not get independent draft-only content templates.
  - `draft-requirement` reuses the existing requirement template contract.
  - `draft-design` reuses the existing design template contract.
  - `draft-plan` reuses the existing plan template contract.
  - For Issue scope, `draft-design` and `draft-plan` must continue using the existing Issue grade / authorized profile template selection and `.assurance.json` preflight.
  - Missing, stale, invalid, or unsupported profile state must fail before any file is written.
  - Initiative / Epic scope for safety-sensitive draft artifacts remains unsupported in this Epic unless a later ADR defines a non-Issue assurance model.

## Consequences
- `iss-00261` is removed from the implementation plan and dependency graph.
- Remaining Issues implement parts of this accepted contract rather than deciding it:
  - `iss-00262` owns artifact templates/rules and existing-template routing.
  - `iss-00263` owns `new artifact`, `new doc` removal, and draft preflight behavior.
  - `iss-00264` owns future scaffold defaults.
  - `iss-00265` owns validation, sync, ADR mirror, and projection behavior.
  - `iss-00266` owns delegated authoring artifact boundary.
  - `iss-00267` owns docs/skills guidance alignment.
  - `iss-00268` owns dogfooding and final Epic evidence.
- Any future change to artifact identity, filename shape, supported catalog, or draft template routing must update this ADR or supersede it before child Issue execution proceeds.

## Rejected Alternatives
- Keep `iss-00261` as the first child Issue:
  - Rejected because it would let a terminal implementation slice decide the whole Epic foundation.
- Add bespoke `draft-*` templates:
  - Rejected because it would fork existing requirement/design/plan template contracts and bypass the Issue grade/profile-aware behavior already used by SpecDock.
- Keep `new doc` as compatibility surface:
  - Rejected by the prior accepted command-unification ADR and user decision.
