# Repository Guidelines

## Operating Mode

- This repository is now a `spec-dock` dogfooding repo: we develop `spec-dock` while also using `spec-dock` to manage this product's own specs and workflow.
- Treat repo documents as the source of truth.

## SpecDock Agent-First Operations

- Codex agents operate SpecDock through the installed external `spec-dock` package or its thin repository shim, which delegates through PATH. Inspect the verified candidate's current leaf help. Do not run the retired repository-local implementation as a fallback. When a user requests a SpecDock outcome or approves a plan that requires one, execute the in-scope commands and verify their results.
- The [Issue 413 requirement](docs/issue-plans/iss-00413-external-cli-state/requirement.md) and [implementation report](docs/issue-plans/iss-00413-external-cli-state/implementation-report.md) retain the dated 2026-10-03 rollout observations. PR #414 merged on 2026-10-04 at `0e7dc86841cb48d011270a1a2165cb6406ac0cea`; merge does not establish installation in any tool environment or worktree. Verify the external package, static assets in one explicit target, and its direct selection separately. Do not infer other-worktree migration, formal Issue 413 Start, or package publication from that historical handoff or merge.
- Treat the request or approved plan as authorization for the command's ordinary documented local, Git, and GitHub side effects. Inspect current root and leaf help, resolve exact targets, and preserve the CLI's fail-closed boundaries.
- Require an exact target and explicit destructive outcome in the request or approved plan before running `scope delete`, `installation uninstall`, or `worktree remove`. Once authorized, execute and verify them rather than handing them back for manual entry.
- Use SpecDock commands instead of hand-editing metadata, active pointers, dependency storage, generated projections, or worktree records.
- Keep the repository's human PR merge gate. That gate does not make `scope create/import`, Artifact creation, `work start/finish`, `scope close/reopen`, `workspace sync`, `installation update`, or other ordinary SpecDock operations human-only.

## Dogfooding Warning

- This repo contains both provider code and a local consumer workspace.
- `src/spec_dock/` is the provider-side source of truth.
- `spec-dock/` is the generated consumer-side workspace used for dogfooding, validation, and active docs.
- `src/spec_dock/assets/spec_dock/...` produces what later appears under `spec-dock/...`.
- Source edits or branch switches do not update the installed external package. A package update changes the user's tool environment; static installation/update changes only the explicitly targeted worktree.
- The ignored `spec-dock/.agent/work-target/` record belongs to that worktree at runtime. Its opaque file token is not a Scope ID and is not a provider or consumer static asset.
- When implementation and generated files look similar, edit the provider side first.
- Do not treat `spec-dock/` as the implementation source of truth unless the task is explicitly about dogfooding data or generated output.

## Canonical Paths

Read the canonical Requirement, Design, and Plan for the authorized work before changing code or tests.

- Resolve the current direct selection with `spec-dock active show --json`; resolve its current hierarchy and paths with `spec-dock scope show TARGET --json`.
- Read `requirement.md`, `design.md`, and `plan.md` under the returned Scope paths, including applicable Initiative and Epic documents.
- An explicitly authorized recovery planning pack remains authoritative when the consumer cannot resolve an active Scope. Keep that distinction in the implementation record; the pack is not evidence of a successful `work start`.
- With no selected context or explicit planning pack, read `spec-dock/system/active-none/`.
- Retained legacy `spec-dock/active/` links are not the new writer's direct selection. Observe the current record instead of guessing from a branch or old projection.

Accepted architecture and roadmap decisions are reflected in the current runtime structure and dogfooding workflow below.

## Project Structure & Module Organization

- `src/spec_dock/`: ordinary installed Python package for the public `spec-dock` CLI.
- `src/spec_dock/cli.py`: public console entrypoint; utilities run before project admission.
- `src/spec_dock/asset_layout.py`: shared shipped-asset path constants.
- `src/spec_dock/runtime/`: implementation of the installed CLI. Keep runtime code outside the consumer workspace.
- `src/spec_dock/shim_vnext.py`: source for the thin shim that delegates argv/cwd/exit to the external console.
- `src/spec_dock/assets/`: shipped scaffold assets copied into target repos.
- `src/spec_dock/assets/install_root/`: current provider-side authority for the two installed skills under `.agents/`.
  - `.agents/skills/spec-dock/SKILL.md`
  - `.agents/skills/spec-dock-grill-with-docs/SKILL.md`
- Legacy `src/spec_dock/assets/codex_skills/` tree was retired and removed from the current repo; use historical issue records under `spec-dock/initiatives/**` when legacy context is needed.
- `src/spec_dock/assets/spec_dock/`: provider-side scaffold source of truth for files that are generated into managed repos.
- `src/spec_dock/assets/spec_dock/scripts/spec-dock`: static repository shim; it does not import a checkout-local runtime.
- `spec-dock/`: local dogfooding workspace scaffolded into this repository. Use it for validation, dogfooding, and active docs, not as the primary implementation source.
- `tests/`: regression suite for installed CLI, static assets, safety boundaries, and real distribution behavior.

### Provider-Side Directory Map

```text
src/spec_dock/
|-- cli.py
|-- shim_vnext.py
|-- runtime/
|   |-- cli/
|   |-- commands/
|   |-- application/
|   |-- domain/
|   |-- infra/
|   `-- presentation/
|-- assets/
|   |-- install_root/
|   |   `-- .agents/
|   `-- spec_dock/
|       |-- docs/
|       |-- templates/
|       |-- system/
|       `-- scripts/
|           `-- spec-dock
`-- __init__.py

tests/
|-- cli_runtime/
|-- integration/
`-- unit/
```

Read it like this:

- Change distribution behavior: start at `pyproject.toml`, `setup.py`, and `src/spec_dock/cli.py`; verify a fresh wheel and non-editable external environment.
- Change static installation: start at `src/spec_dock/runtime/application/{direct_installation,direct_static_update}.py` and `src/spec_dock/runtime/infra/static_assets.py`.
- Change the two installed skills: start at `src/spec_dock/assets/install_root/`.
- Treat `src/spec_dock/assets/install_root/` as the only current authority for the installed skills.
- Change shipped docs/templates/system files: start at `src/spec_dock/assets/spec_dock/{docs,templates,system}/`.
- Change runtime command entrypoints: start at `src/spec_dock/runtime/{cli,commands}/`.
- Change orchestration or use cases: start at `src/spec_dock/runtime/application/`.
- Change business rules or models: start at `src/spec_dock/runtime/domain/`.
- Change filesystem/git/github/persistence behavior: start at `src/spec_dock/runtime/infra/`.
- Change public JSON/text/diagnostic output: start at `src/spec_dock/runtime/presentation/`.
- Choose tests by surface: installer/scaffold in `tests/unit/infra/`, runtime in `tests/cli_runtime/`, application/domain/presentation in `tests/unit/{application,domain,presentation}/`, and external boundary smoke in `tests/integration/`.

### Runtime Architecture

The current runtime architecture is a hybrid layered architecture.

- `cli/`: current options, catalog, context-free utilities, and argument admission.
- `commands/`: user-facing command handlers and command contracts.
- `application/`: orchestration and use-case layer.
- `domain/`: core rules, models, status/deps/tree/validation logic.
- `infra/`: filesystem, Git/GitHub, worktree-local direct records, artifact publication, and OS adapters.
- `presentation/`: typed public JSON, text, and diagnostic rendering.

Do not collapse new work back into monolithic command files when a layer-specific home already exists.

## Dogfooding Rules

- Assume `spec-dock` in this repo is an active consumer of the shipped scaffold.
- Expect duplication-by-design for static assets between `src/spec_dock/assets/spec_dock/...` and `spec-dock/...`. Runtime implementation is shipped only in the installed package.
- For static changes, edit provider assets first and verify a fresh isolated consumer against them. Inspect the actual dogfood workspace and apply changes only in its approved installation/migration step.
- When changing shipped assets under `src/spec_dock/assets/`, consider the impact on both newly initialized repos and this local dogfooding repo.
- Prefer commands and flows that will also work for a real consumer repo; avoid one-off local shortcuts unless they are explicitly test-only.
- If a change affects scaffold structure, docs, templates, scripts, or runtime contracts, treat it as a shipped asset API change.

## Development Workflow

1. Read the canonical documents for the authorized plan, using the current direct selection when available.
2. Identify the layer or surface you are changing:
   - external CLI and distribution: `src/spec_dock/cli.py`, `pyproject.toml`, `setup.py`, and fresh wheel verification
   - static installation and migration: `src/spec_dock/runtime/application/{direct_installation,direct_static_update,direct_migration}.py` and guarded publication/backup adapters
   - installed skills: `src/spec_dock/assets/install_root/` is the current authority; use historical issue records for retired-artifact context
   - runtime command surface: `.../runtime/cli/` and `.../commands/`
   - orchestration or business logic: `.../application/` and `.../domain/`
   - external adapters or persistence: `.../infra/`
   - output/rendering: `.../presentation/`
3. Make the smallest coherent change in the correct layer.
4. Update tests that cover the changed contract or scaffold behavior.
5. Verify whether the local dogfooding workspace under `spec-dock/` should be refreshed, inspected, or intentionally left as-is.

## Build, Test, and Development Commands

```bash
# Run all selected tests directly; no policy skip or regression ledger.
uv run pytest
uv run pytest tests/unit
uv run pytest tests/unit/infra/test_provider_distribution.py

# Choose unused absolute candidate directories outside all worktrees.
uv build --wheel --out-dir /private/tmp/spec-dock-candidate-dist
uv venv /private/tmp/spec-dock-candidate
# Replace this path with the actual wheel just built.
uv pip install --python /private/tmp/spec-dock-candidate/bin/python /absolute/path/spec_dock-VERSION-py3-none-any.whl
/private/tmp/spec-dock-candidate/bin/spec-dock help

# After the approved installation and migration, use the installed console or shim.
spec-dock workspace validate
```

`Provider CI` runs `make lint` and ordinary `uv run pytest` on pull requests.
There is no separate full-regression policy, ledger, sharder, or post-merge evaluator.
Keep tests hermetic and verify installer basics on supported platforms. Agents stop at a
merge-ready PR; a human performs the merge.

## Testing Guidelines

- Framework: `pytest`.
- Installer/scaffold coverage: `tests/unit/infra/`.
- Runtime / CLI coverage: `tests/cli_runtime/`.
- Application/domain/presentation coverage: `tests/unit/{application,domain,presentation}/`.
- Keep tests hermetic: use temp directories and `gh` stubs instead of live network calls.
- When changing shipped scaffold behavior, update or add assertions for generated file structure, content, and runtime behavior.

## Coding Style & Change Boundaries

- Python 3.10+; use type hints and keep imports minimal and ordered.
- Prefer small helpers and explicit contracts over clever abstractions.
- Keep edits aligned with the accepted layered architecture.
- The implementation source of truth is under `src/spec_dock/`, especially `src/spec_dock/assets/spec_dock/...` for shipped scaffold behavior.
- For agent-tooling assets, `src/spec_dock/assets/install_root/` is the single current authority.
- `spec-dock/` is for dogfooding confirmation and consumer-side inspection.
- However, do inspect `spec-dock/` after scaffold-affecting changes because it is now part of dogfooding validation.

## Commit & Pull Request Guidelines

- Commits follow Conventional Commits in Japanese.
- Use a multi-line message: `type(scope): summary`, blank line, bullet body.
- Before committing, verify both `git config user.name` and `git config user.email` resolve to `chemitaro` and `84865385+chemitaro@users.noreply.github.com`.
- Preserve verified GitHub App, Bot, and third-party identities; never reassign them merely to increase contributions.
- PRs should include the problem statement, linked issue, test output, and notes on scaffold/template/runtime impact.

## Security & Configuration Tips

- Do not commit secrets, tokens, `.env`, or local experimental artifacts.
- Keep ad hoc experiments under `manual-tests/`.
- Avoid assuming the local dogfooding workspace is disposable; confirm before deleting or rewriting data under `spec-dock/`.
