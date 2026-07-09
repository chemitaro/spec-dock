# ChatGPT-first planning redesign pack

This artifact pack records the ChatGPT GPT-5.5 Pro Extended planning output used to refine `iss-00309`.

## Purpose

The pack turns the latest discussion into concrete implementation material:

- formal Issue requirement/design/plan deltas;
- primary skill body drafts;
- manual fallback adjustment notes;
- prompt templates for ChatGPT-first planning;
- script and adoption-review references.

## Important decisions

- ChatGPT-first is the normal planning route.
- Manual planning remains only as a human-approved emergency fallback.
- Issue Planning has one workflow and different input-context shapes.
- Issue Planning input context types are `requirement-heavy`, `draft-heavy`, and `context-heavy`.
- ChatGPT may return `information_insufficient` instead of fabricating artifacts.
- Epic Planning generates Epic formal artifacts plus child Issue draft artifacts.
- Multi-Issue implementation Epics end with a quality-gate / mergeable-PR delivery Issue.

## Files

- `skill-drafts/spec-dock-chatgpt-authoring.SKILL.md`
- `skill-drafts/spec-dock-initiative-planning.SKILL.md`
- `skill-drafts/spec-dock-epic-planning.SKILL.md`
- `skill-drafts/spec-dock-issue-planning.SKILL.md`
- `skill-drafts/manual-skill-adjustment-notes.md`
- `prompt-templates/shared-base.md`
- `prompt-templates/initiative-planning.md`
- `prompt-templates/epic-planning.md`
- `prompt-templates/issue-planning.md`
- `references/prompt-composition-reference.md`
- `references/script-design-reference.md`
- `references/adoption-and-review-reference.md`
- `references/file-change-plan.md`
