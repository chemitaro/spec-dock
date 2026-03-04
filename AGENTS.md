# Repository Guidelines

## Project Structure & Module Organization

- `src/spec_dock/`: Python package for the installer CLI (`spec-dock`).
- `src/spec_dock/assets/`: Scaffolded runtime assets copied into target repos (templates, docs, runtime scripts, agent skill).
- `tests/`: `unittest`-based regression tests (focus on `init/update` outputs and runtime script behavior).
- `docs/`: Design/notes about aggregation and GitHub integration.
- `manual-tests/`: Local manual test workspaces (gitignored except `manual-tests/README.md`).

## Build, Test, and Development Commands

```bash
# Run unit tests (preferred baseline)
python -m unittest discover -v

# Try the installer CLI locally (no publish required)
uvx --from . spec-dock init /tmp/target-repo
uvx --from . spec-dock update /tmp/target-repo

# Or run the module directly
python -m spec_dock.cli init /tmp/target-repo
```

## Coding Style & Naming Conventions

- Python 3.10+; use type hints and keep imports sorted and minimal.
- Indentation: 4 spaces; prefer clear, small helper functions over clever abstractions.
- Assets under `src/spec_dock/assets/` are part of the shipped scaffold—treat changes as API changes and update tests/docs accordingly.

## Testing Guidelines

- Framework: `unittest` (see `tests/test_cli.py`).
- When changing scaffolding behavior, add/adjust assertions that validate generated file structure and content.
- Keep tests hermetic: prefer temp dirs and command stubs (e.g., `gh` stubs) over network calls.

## Commit & Pull Request Guidelines

- Commits follow Conventional Commits in practice, e.g.:
  - `feat(deps): ...`, `fix(active): ...`, `docs(...): ...`, `chore(...): ...`
- Use a multi-line message: summary line, blank line, then bullet list of changes/reasoning/tests.
- PRs should include: problem statement, linked issue, test output (`python -m unittest discover -v`), and notes on any scaffold/template changes.

## Security & Configuration Tips

- Do not commit secrets (tokens, `.env`, local trial repos). Keep experiments under `manual-tests/`.
