# Epic 00295 ChatGPT Authoring Final Pack

This ZIP is a ChatGPT-generated authoring pack for `epic-00295` `ChatGPT Authoring Pack Installed Runtime`.

## Authority boundary

- This pack is evidence-only.
- `authority` is `evidence_only`.
- `adoption_status` is `unreviewed`.
- `bundle_generation_not_promotion` is `true`.
- Codex / SpecDock must review, validate, and explicitly adopt any file or claim before it becomes canonical.
- Issue draft packs are not canonical Issue docs until adopted through `spec-dock-issue-planning` `draft-adoption` mode.
- The final Issue is the only PR delivery Issue.

## Repository provenance

- Repository: `chemitaro/spec-dock`
- Branch inspected: `codex/authoring-pack-installed-runtime`
- Default branch: `main`
- Epic path: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00295-chatgpt-authoring-pack-installed-runtime/`

GitHub connector inspection succeeded for the repository and current branch source files. The pack was synthesized from the current Epic requirement/design/plan, report ledger, and selected Epic-local research/interview artifacts.

## Structure

```text
epic-00295-chatgpt-authoring-final-pack/
  manifest.json
  README.md
  epic/
    requirement.md
    design.md
    plan.md
  issues/
    01-promote-authoring-pack-assets/
    ...
    12-final-quality-gate-and-mergeable-pr-delivery/
```

Each Issue directory contains:

- `draft-requirement.md`
- `draft-design.md`
- `draft-plan.md`

## Adoption guidance

1. Treat this ZIP as external evidence, not as an authoritative patch.
2. Review `manifest.json` and provenance before reading individual files.
3. Compare `epic/requirement.md`, `epic/design.md`, and `epic/plan.md` against the current canonical Epic docs.
4. For each Issue candidate, use `spec-dock-issue-planning` in `draft-adoption` mode to adopt, rewrite, reject, or defer claims.
5. Do not use this pack to create `.assurance.json`, mark reviewer pass, mark execution-ready, or mark PR-ready.
6. Follow the relay policy: Issues 01-11 do not create PRs; Issue 12 performs the final quality gate and mergeable PR delivery.
