# Repository Guidelines

## Operating Mode

- This repository is now a `spec-dock` dogfooding repo: we develop `spec-dock` while also using `spec-dock` to manage this product's own specs and workflow.
- Treat repo documents as the source of truth.

## SpecDock Agent-First Operations

- Codex agents are the default operators of `./spec-dock/scripts/spec-dock ...`. When a user requests a SpecDock outcome or approves a plan that requires one, execute the in-scope commands and verify their results; do not stop at command suggestions or ask the user to type ordinary commands.
- Treat the request or approved plan as authorization for the command's ordinary documented local, Git, and GitHub side effects. Inspect current root and leaf help, resolve exact targets, and preserve the CLI's fail-closed boundaries.
- Require an exact target and explicit destructive outcome in the request or approved plan before running `delete`, `uninstall --apply`, `uninstall --remove-specs`, `worktree remove`, or a guard-bypassing `--force`. Once authorized, execute and verify them rather than handing them back for manual entry.
- Use SpecDock commands instead of hand-editing metadata, active pointers, dependency storage, generated projections, or worktree records.
- Keep the repository's human PR merge gate. That gate does not make node creation, Artifact creation, `issue start`, `issue finish`, `close`, `sync`, `update`, or other ordinary SpecDock operations human-only.

## Dogfooding Warning

- This repo contains both provider code and a local consumer workspace.
- `src/spec_dock/` is the provider-side source of truth.
- `spec-dock/` is the generated consumer-side workspace used for dogfooding, validation, and active docs.
- `src/spec_dock/assets/spec_dock/...` produces what later appears under `spec-dock/...`.
- When implementation and generated files look similar, edit the provider side first.
- Do not treat `spec-dock/` as the implementation source of truth unless the task is explicitly about dogfooding data or generated output.

## Canonical Paths

Read these first before changing code or tests:

- When an active initiative / epic / issue is set, the source of truth is the symlink paths under `spec-dock/active/`. Read these first:
  - `spec-dock/active/initiative/requirement.md`
  - `spec-dock/active/initiative/design.md`
  - `spec-dock/active/initiative/plan.md`
  - `spec-dock/active/epic/requirement.md`
  - `spec-dock/active/epic/design.md`
  - `spec-dock/active/epic/plan.md`
  - `spec-dock/active/issue/requirement.md`
  - `spec-dock/active/issue/design.md`
  - `spec-dock/active/issue/plan.md`
- Accepted architecture and roadmap decisions are reflected in the current runtime structure and dogfooding workflow below.

## Project Structure & Module Organization

- `src/spec_dock/`: installer package for the top-level `spec-dock` CLI.
- `src/spec_dock/cli.py`: installer entrypoint for `init` / `update`.
- `src/spec_dock/assets/`: shipped scaffold assets copied into target repos.
- `src/spec_dock/assets/install_root/`: current provider-side authority for the two installed skills under `.agents/` and the retained `.github/workflows/ci.yml`.
  - `.agents/skills/spec-dock/SKILL.md`
  - `.agents/skills/spec-dock-grill-with-docs/SKILL.md`
  - `.github/workflows/ci.yml`
- Legacy `src/spec_dock/assets/codex_skills/` tree was retired and removed from the current repo; use historical issue records under `spec-dock/initiatives/**` when legacy context is needed.
- `src/spec_dock/assets/spec_dock/`: provider-side scaffold source of truth for files that are generated into managed repos.
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/`: provider-side runtime CLI shipped into managed repos.
- `spec-dock/`: local dogfooding workspace scaffolded into this repository. Use it for validation, dogfooding, and active docs, not as the primary implementation source.
- `tests/`: regression suite for installer behavior and shipped runtime behavior.

### Provider-Side Directory Map

```text
src/spec_dock/
|-- cli.py
|-- assets/
|   |-- install_root/
|   |   |-- .agents/
|   |   `-- .github/
|   `-- spec_dock/
|       |-- docs/
|       |-- templates/
|       |-- system/
|       `-- scripts/
|           |-- spec-dock
|           `-- spec_dock_runtime/
|               |-- cli/
|               |-- commands/
|               |-- application/
|               |-- domain/
|               |-- infra/
|               `-- presentation/
`-- __init__.py

tests/
|-- test_cli.py
|-- test_init_update.py
|-- cli_runtime/
|-- domain_runtime/
`-- presentation_runtime/
```

Read it like this:

- Change installer behavior: start at `src/spec_dock/cli.py`.
- Change the two installed skills or retained CI workflow: start at `src/spec_dock/assets/install_root/`.
- Treat `src/spec_dock/assets/install_root/` as the only current authority for the installed skills and retained CI workflow.
- Change shipped docs/templates/system files: start at `src/spec_dock/assets/spec_dock/{docs,templates,system}/`.
- Change runtime command entrypoints: start at `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/{cli,commands}/`.
- Change orchestration or use cases: start at `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/`.
- Change business rules or models: start at `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/`.
- Change filesystem/git/github/persistence behavior: start at `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/`.
- Change JSON/markdown/PUML/CLI output: start at `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/`.
- Choose tests by surface: installer/scaffold in `tests/unit/infra/`, runtime in `tests/cli_runtime/`, application/domain/presentation in `tests/unit/{application,domain,presentation}/`, and external boundary smoke in `tests/integration/`.

### Runtime Architecture

The current runtime architecture is a hybrid layered architecture.

- `cli/`: bootstrap, parser, registry, dispatch.
- `commands/`: user-facing command handlers and command contracts.
- `application/`: orchestration and use-case layer.
- `domain/`: core rules, models, status/deps/tree/validation logic.
- `infra/`: filesystem, git/github, active store, artifact writing, persistence adapters.
- `presentation/`: JSON, markdown, PUML, and CLI rendering.

Do not collapse new work back into monolithic command files when a layer-specific home already exists.

## Dogfooding Rules

- Assume `spec-dock` in this repo is an active consumer of the shipped scaffold.
- Expect duplication-by-design between `src/spec_dock/assets/spec_dock/...` and `spec-dock/...`.
- In normal development, edit `src/spec_dock/assets/spec_dock/...` and then verify the result in `spec-dock/...`.
- When changing shipped assets under `src/spec_dock/assets/`, consider the impact on both newly initialized repos and this local dogfooding repo.
- Prefer commands and flows that will also work for a real consumer repo; avoid one-off local shortcuts unless they are explicitly test-only.
- If a change affects scaffold structure, docs, templates, scripts, or runtime contracts, treat it as a shipped asset API change.

## Development Workflow

1. Read the relevant docs under `spec-dock/active/`, or `spec-dock/system/active-none/` if no active context is set.
2. Identify the layer or surface you are changing:
   - installer: `src/spec_dock/cli.py`, asset sync/update behavior
   - installed skills / retained CI workflow: `src/spec_dock/assets/install_root/` is the current authority; use historical issue records for retired-artifact context
   - runtime command surface: `.../spec_dock_runtime/cli/` and `.../commands/`
   - orchestration or business logic: `.../application/` and `.../domain/`
   - external adapters or persistence: `.../infra/`
   - output/rendering: `.../presentation/`
3. Make the smallest coherent change in the correct layer.
4. Update tests that cover the changed contract or scaffold behavior.
5. Verify whether the local dogfooding workspace under `spec-dock/` should be refreshed, inspected, or intentionally left as-is.

## Build, Test, and Development Commands

```bash
# Ordinary test commands run the fast lane. They retain the usual pytest
# interface and policy-skip selected full-regression tests.
uv run pytest
uv run pytest tests/unit

# Focused pytest commands follow the same default policy.
uv run pytest tests/unit/path_to_test.py

# Marker selection alone is diagnostic; it does not permit full-regression bodies.
uv run pytest -m full_regression

# Explicit full-regression permission.
uv run pytest --run-full-regression

# Explicit heavy-only execution.
uv run pytest --run-full-regression -m full_regression

# Run installer locally from the current checkout
uvx --from . spec-dock init /tmp/target-repo
uvx --from . spec-dock update /tmp/target-repo

# Dogfooding repo: installed local tool
spec-dock --version
spec-dock update .

# Module entrypoint
python -m spec_dock.cli init /tmp/target-repo
```

`full_regression test is disabled by default; use --run-full-regression to run
it` is the stable policy skip reason. Do not use `-m full_regression` alone as
an execution permission.

For pull requests, `Provider CI` / `provider-tests` is the merge-blocking fast
gate and runs `make lint` plus ordinary `uv run pytest`. `Provider Full
Regression` is an independent post-merge validation that runs on `main` push
or `workflow_dispatch`; it is not a PR merge blocker, and this repository has
no scheduled or cron full-regression trigger.

On a post-merge full-regression failure, the repository maintainer checks the
SHA, failed tests, logs, duration, and summary, then normally forward-fixes or
reruns the workflow. Reproduce the same SHA locally with `uv run pytest
--run-full-regression` when necessary. Do not add automatic rollback or
automatic Issue creation. If a selector omission, missing required check, or
unacceptable escape is found, stop the next merge decision, restore the PR
workflow command to `uv run pytest --run-full-regression`, and disable the
default conditional policy skip if it is unsafe. Preserve markers, the manual
full command, the post-merge workflow, and measurement evidence; only
reintroduce the fast gate after fresh review. Agents must stop at a
merge-ready PR: a human performs the merge.

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
