# File change plan

## Purpose

Map the ChatGPT-first redesign output to concrete repository changes.

## Skill Changes

- Rewrite primary planning skills around ChatGPT-first orchestration:
  - `spec-dock-initiative-planning`
  - `spec-dock-epic-planning`
  - `spec-dock-issue-planning`
- Preserve old local/Codex-first planning route in:
  - `spec-dock-initiative-planning-manual`
  - `spec-dock-epic-planning-manual`
  - `spec-dock-issue-planning-manual`
- Strengthen `spec-dock-chatgpt-authoring` as shared evidence lane.

## Script Changes

- Add or adjust a context composer for ChatGPT-first planning.
- Support free-form operator intent and development background.
- Support configured backend command.
- Enforce synced mode by default and explicit local-context mode when needed.
- Treat `information_insufficient` as a valid output.

## Documentation Changes

- Document ChatGPT-first as the normal route.
- Document manual fallback as explicit-human emergency route.
- Document Option 3+ Epic Planning and just-in-time Issue Planning.
- Document final quality Issue policy for Multi-Issue implementation Epics.

## Template Changes

- Epic plan template should include Issue draft handoff index and final quality Issue requirement.
- Issue planning template should avoid separate workflow modes and describe input context types.

## Test Changes

- Assert manual skills are installed.
- Assert primary skills mention ChatGPT-first route.
- Assert manual skills require explicit human approval.
- Assert forbidden authority claims are absent.
- Assert Issue Planning docs do not introduce separate workflow modes for different input sources.
