## Language
- User chat: Japanese. Internal reasoning: English.

## STT
- Expect STT typos; infer intent. If ambiguous, ask briefly. Verify identifiers via repo search/symbols before editing code.

## Constraints
- Commit messages: Conventional Commits; Japanese; multi-line (`type(scope): summary` + blank line + bullet body; optional footer: `BREAKING CHANGE:`/`Refs:`/`Closes #`).
- Paths: never create/rename/move files/dirs containing `A-Z`; use lowercase (prefer `a-z0-9._-`). Don’t increase existing uppercase paths; confirm with user before changing them. Verify after changes (e.g., `rg --files | rg '[A-Z]'`).
