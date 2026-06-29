# Manual Tests

This directory is reserved for local manual test workspaces.

- The main repository must not track manual test workspaces, fixtures, logs, captures, or evidence files under `manual-tests/`.
- The only file intended to stay tracked in this repository is this `README.md`.
- Manual tests that need SpecDock state should create a trial directory under `manual-tests/` and initialize an independent Git repository inside that trial directory.
- Keep trial repositories self-contained. Do not rely on the parent repository's Git history, index, or active SpecDock state as test data.
- If a manual test produces artifacts worth preserving, summarize them in the relevant SpecDock issue or epic artifact instead of adding the raw workspace to the parent repository.

Recommended structure (examples):

- `manual-tests/spec-dock-deps/trial-01-baseline/`
- `manual-tests/spec-dock-deps/trial-02-deps-guard/`
- `manual-tests/spec-dock-deps/trial-03-github-sync/`
