# spec-dock

`spec-dock` scaffolds a lightweight spec-driven documentation workspace into an existing repository.

It is designed to be executed via `uvx` (ephemeral install). After scaffolding, your project uses the
generated files (Markdown templates, scripts, agent skills); the `spec-dock` package itself is not
required at runtime.

## Usage (uvx)

```bash
# Install into the current directory
uvx --from git+https://github.com/chemitaro/spec-dock spec-dock init

# Install into a target path
uvx --from git+https://github.com/chemitaro/spec-dock spec-dock init /path/to/project

# Overwrite managed files if 'spec-dock' already exists
uvx --from git+https://github.com/chemitaro/spec-dock spec-dock init --force

# Installer-level refresh of managed files (docs/templates/scripts/skills only)
uvx --from git+https://github.com/chemitaro/spec-dock spec-dock update
```

## Usage (uvx from a local clone)

If you want to try `spec-dock` without fetching from GitHub each time, clone this repository and
point `uvx --from` to the local directory.

Note: `--from` must point to the repository root that contains `pyproject.toml`
(do not point it at `src/spec_dock/`).

```bash
# Clone spec-dock somewhere on your machine
git clone https://github.com/chemitaro/spec-dock ~/src/spec-dock

# Install into your target project (current directory)
cd /path/to/your/project
uvx --from ~/src/spec-dock spec-dock init

# Or: specify the target path explicitly
uvx --from ~/src/spec-dock spec-dock init /path/to/your/project

# Update managed files later
uvx --from ~/src/spec-dock spec-dock update
```

`spec-dock update` refreshes the recognized managed distribution through one plan/apply path. It
preserves user-owned and unknown paths, blocks before writing when ownership or workspace identity is
ambiguous, and records a root/intent/authority/contract/plan/protocol-bound operation journal when an apply starts. It is distinct from
`init --force`; older or incompatible workspaces may still require manual normalization or rebuild.

既存環境の更新手順と、旧配布面からの移行・復旧方針は [移行ガイド](spec-dock/docs/migration.md) を参照してください。

## Worktree Root Setup

`./spec-dock/scripts/spec-dock worktree create` requires `SPEC_DOCK_WORKTREE_ROOT`.
Set it once in the shell startup file used by your local environment, such as `~/.zshenv` for zsh
or `~/.bashrc` / `~/.bash_profile` for bash.

```bash
export SPEC_DOCK_WORKTREE_ROOT="${SPEC_DOCK_WORKTREE_ROOT:-$HOME/workspace/worktrees}"
```

SpecDock uses this directory as the central root for managed linked worktrees. Runtime reference
docs describe the command contract and placement rules, but shell setup belongs here as onboarding.

Troubleshooting:
- If `.spec-dock/current` or `spec-dock-close*.sh` are generated, you're running the legacy (v1) scaffold.
  v2 generates `spec-dock/initiatives/`, `spec-dock/active/`, and `spec-dock/.agent/`.
- If you already have a legacy `.spec-dock/` directory from older v2 versions, rename it:
  - `mv .spec-dock spec-dock`
- If your local clone contains the v2 files but `uvx` still behaves like v1, try one of:
  - Avoid the shared cache for a single run: `uvx --no-cache --from ~/src/spec-dock spec-dock init`
  - Use a dedicated cache directory: `uvx --cache-dir /tmp/uv-cache-spec-dock --from ~/src/spec-dock spec-dock init`
  - Remove stale build outputs in the tool repo (this often causes mixed v1/v2 assets): `rm -rf ~/src/spec-dock/build`
  - (If possible) clear the cache: `uv cache clean`

## Usage (local scripts)

After `init`, Core operations use `./spec-dock/scripts/spec-dock`. The installed skill surface is
limited to the Storage Core guide and the optional operator-owned documentation grill; planning,
review, and execution orchestration are not shipped as repository-local workflow engines.

### Agent-first operation

SpecDock is intended to be operated by a Codex agent. When a user requests a SpecDock outcome or
approves a plan that requires one, the agent runs the applicable repository-local commands and
verifies their results. The examples below are command references, not instructions to hand routine
execution back to the user. Removing bundled orchestration does not make the CLI human-operated.

Ordinary in-scope creation, import, Artifact, active, dependency, sync, issue lifecycle, worktree
creation, Workbench copy, close, and managed update operations do not require command-by-command
confirmation. Destructive operations (`delete`, `uninstall --apply`, `uninstall --remove-specs`,
`worktree remove`, and guard-bypassing `--force`) require an exact target and destructive outcome in
the user request or approved plan. PR merge remains human-operated where repository instructions say
so.

```bash
# Create nodes:
# - initiative/epic/issue default: create and link a GitHub issue.
#   Requires: GitHub CLI `gh` and a GitHub repository.
./spec-dock/scripts/spec-dock new initiative --title "Auth platform"                # creates GH issue, id=init-00123
./spec-dock/scripts/spec-dock new epic --initiative init-00123 --title "JWT auth"  # creates GH issue, id=epic-00124

# - issue default: create and link a GitHub issue; ids follow GitHub issue numbers.
./spec-dock/scripts/spec-dock new issue --epic epic-00124 --title "Add refresh token"  # creates GH issue, id=iss-00123

# `--create-github-issue` is an explicit alias for the default create path.
./spec-dock/scripts/spec-dock new initiative --create-github-issue --title "Auth platform"                # id=init-00123
./spec-dock/scripts/spec-dock new epic --create-github-issue --initiative init-00123 --title "JWT auth"  # id=epic-00124

# Or: link to an existing GitHub issue number (without creating a new one)
./spec-dock/scripts/spec-dock new issue --epic epic-00124 --title "Add refresh token" --github-issue 123  # id=iss-00123

# Node creation does not accept `--no-github`; use `--github-issue <n>` to link an existing issue.

# Working artifacts such as ADR originals are created via runtime command.
./spec-dock/scripts/spec-dock new artifact adr --issue iss-00123 --title "Token rotation strategy"

# Copy one Initiative/Epic/Issue Workbench to an existing linked worktree (experimental, one-shot).
./spec-dock/scripts/spec-dock workbench copy --scope iss-00123 --to /path/to/linked-worktree

# Preserve one explicit evidence file as opaque, evidence-only Artifact content.
./spec-dock/scripts/spec-dock artifact import file \
  --issue iss-00123 --file spec-dock/initiatives/.../.workbench/report.md

# Import an existing GitHub issue into the spec tree (does not create/update the issue on GitHub)
./spec-dock/scripts/spec-dock import initiative 10 --title "Auth platform"                 # id=init-00010
./spec-dock/scripts/spec-dock import epic 11 --title "JWT auth" --initiative init-00010    # id=epic-00011
./spec-dock/scripts/spec-dock import issue 123 --title "Add refresh token" --epic epic-00011  # id=iss-00123
#
# Note: canonical GitHub issue URLs are checked against the current repo; owner/repo mismatch is rejected.
# Note: numeric initiative/epic/issue imports read from the resolved current repo (or explicit owner/repo when provided); if neither explicit repo scope nor a resolvable current repo scope from `origin` is available, import fails before local writes.

# Normal issue execution lifecycle (primary path)
./spec-dock/scripts/spec-dock issue start 123             # active + branch checkout/create
./spec-dock/scripts/spec-dock issue start iss-local-00001 # local node id
./spec-dock/scripts/spec-dock issue finish                # lifecycle closure: GitHub close + active clear

# Manual / recovery active-set path (low-level)
./spec-dock/scripts/spec-dock active set 123             # default: active only (no checkout)
./spec-dock/scripts/spec-dock active set iss-local-00001 # local node id (no checkout)
./spec-dock/scripts/spec-dock active set 123 --checkout  # active + branch checkout/create

# Generate index.json/tree.json (local scan; optionally enrich from GitHub via gh)
./spec-dock/scripts/spec-dock sync
./spec-dock/scripts/spec-dock sync --github

# Validate the spec tree structure
./spec-dock/scripts/spec-dock validate

# Refresh this managed repo from the fixed upstream package (target defaults to the current directory)
./spec-dock/scripts/spec-dock update

# Or refresh an explicit managed repo path
./spec-dock/scripts/spec-dock update /path/to/project
```

Notes:
- `update` and `init --force` use the same recognized distribution classifier and fail closed on
  unknown, modified, symlinked, hard-linked, or root-rebound targets. No pathname-based recursive
  cleanup is used for unknown paths.
- An interrupted recognized update or `init --force` may leave
  `spec-dock/.distribution-journal.json`. Rerun the same operation against the same repository root
  with the same package or a compatible newer package to resume from exact action pre/postconditions.
  Root, intent, authority, contract, plan, protocol, or exact target-state mismatches, downgrades, and
  incompatible packages stop before further mutation; inspect the reported repository-relative reason
  instead of rolling back to older installer code. Recovery is forward recovery; forward recovery is not code rollback.
- Recovery metadata role is schema/purpose-based, not pathname-based: the same pathname
  `spec-dock/.distribution-retry.json` carries schema 1 as a legacy migration input and schema 2 as the current forward guard. A schema-1 payload is converted one way only when it is the exact same-root,
  same-operation pre-write state and the executing package is the same or a compatible newer version.
  An exact legacy staging lease is accepted only when its action, private stage-name family, parent chain,
  device, inode, ctime, type, and link count all match the reconstructed plan; otherwise the payload and
  stage are preserved for manual diagnosis. The current `.distribution-journal.json` records the
  root-bound forward operation. A `.uninstall-retry.json` file is legacy reader-only/manual evidence and
  is never auto-converted, auto-deleted, or promoted to current recovery authority. Malformed,
  later-phase, cross-root, different-operation, downgrade, incompatible-package, unknown-stage, or dual
  recovery state is rejected without rewriting recovery authority.
- Managed distribution deprovision is the default/`--keep-specs` uninstall owner. Dry-run performs a
  complete read-only assessment; apply uses a schema-2 forward guard in
  `spec-dock/.distribution-retry.json` and a protocol-2 journal in
  `spec-dock/.distribution-journal.json`. Recovery is forward-only and resumes only the same root,
  intent, authority, contract, plan, and protocol with the same or a semantically compatible newer
  package.
- Generated `spec-dock/active` and `spec-dock/.agent` entries are removable only when the single
  runtime-derived producer proves their current identity. Unknown, modified, legacy, conflicting,
  hard-linked, or special entries block every mutation and remain preserved. Proven-owned absent
  subtrees collapse to one surviving-ancestor witness; a completely absent managed subtree completes
  without writing protocol metadata.
- Directory publication is bottom-up and depends on exact immediate-child absence. The journal moves
  through prepared, executing, verifying, and an atomic verified/completed terminal publication.
  Public fields come only from the typed `DistributionProcessResult`; the CLI does not interpret
  journal files. Those fields include phase, checkpoint, failed/pending paths, and action/top-level
  errors.
- A legacy `.uninstall-retry.json` is never converted automatically because it proves no root, specs
  mode, plan, or checkpoint. It is preserved as legacy reader-only/manual evidence for manual recovery.
  `--keep-specs` preserves initiatives, Workbench data, and unknown content. `--remove-specs` is the
  current explicit spec-history purge authority for shared,
  journaled spec-history purge: dry-run is write-free, and apply uses the same root-bound forward journal.
  A matching partial purge is retried only with `spec-dock uninstall --apply --remove-specs <target>`;
  legacy or conflicting recovery state remains manual and is never converted automatically.
- `./spec-dock/scripts/spec-dock update [path]` is the repo-local self-update path. It wraps the
  installer update command by running
  `uvx --no-cache --from git+https://github.com/chemitaro/spec-dock spec-dock update <target>`.
  The target defaults to the current working directory, and an explicit path is resolved before it is
  passed to the installer.
- Runtime update always uses the fixed upstream `git+https://github.com/chemitaro/spec-dock` source
  with `uvx --no-cache`; it does not expose arbitrary package source, cache, or `--force` options.
- Runtime update refreshes recognized managed files through installer update. It is not `init --force`.
  Legacy or incompatible workspaces are preserved or blocked when identity cannot be proven; they are
  not silently rewritten.
- Workbench is an experimental, Git-ignored, non-canonical, disposable work area. The root
  `spec-dock/.workbench/` uses date buckets and manual file selection only; there is no root bulk-copy
  command. Initiative/Epic/Issue Workbenches can be copied explicitly to the same scope in one linked
  worktree. This is a source-wins, one-shot copy, not automatic synchronization or copy-back.
- Workbench copy applies to the complete directory without language, extension, MIME, or content
  classification. Keep material that must survive outside Workbench in an Artifact or canonical doc.
- `artifact import file` accepts one explicit regular file, preserves the source and its bytes, and
  stores it as an opaque generic Artifact. Imported content remains evidence-only until its adoption is
  recorded in the Evidence Adoption Ledger and accepted claims are rewritten into canonical docs. See
  [移行ガイド](spec-dock/docs/migration.md) for the replacement route and recovery notes.
- `update` preserves existing Workbench directories as unmanaged local content. It does not migrate,
  normalize, delete, or promote them.
- For `new/import {initiative,epic,issue}`, `--title` is restricted to ASCII (alphanumerics + single spaces) and `--slug` is kebab-case.
- Legacy sequential discussion docs are grandfathered only. New docs do not reuse legacy sequence names, and spec-dock does not auto-rename or auto-repair them to preserve forced backward compatibility.
- Normal issue execution should use `issue start <target>` / `issue finish` as the primary path. Use `issue start <target> -f` / `--force` only to bypass the unfinished active issue guard; dependency readiness still applies.
- `issue finish` is lifecycle closure only: it closes or confirms the linked GitHub issue and clears active state, but it does not guarantee commit, push, PR, merge, validate, test, or review completion. Record delivery completion evidence before running it.
- Treat direct `active set` / `active set --checkout` as manual / recovery / low-level commands. `active set` updates active pointers from local nodes first. Branch operations are opt-in via `--checkout`.
- With `active set --checkout`, the branch name is normalized to `<id>-<slug>` (fallback: `<id>`) to keep branch names ASCII.
- `github.issue_number` links (initiative/epic/issue) must be globally unique; duplicates are rejected/detected. See `src/spec_dock/assets/spec_dock/docs/reference_github.md` for details.
- Generated initiative/epic/issue nodes include `artifacts/rules.md` as the default working-artifact surface.
- New working artifacts are created under the target scope `artifacts/` direct child with `./spec-dock/scripts/spec-dock new artifact <type> --{initiative|epic|issue} <id> --title "..."`.
- Existing `discussions/` docs are legacy/preservation evidence; do not use them as the recommended destination for new working artifacts.
- Generated nodes do not include template-derived `README.md`.

See `docs/sync-aggregation.md` for how `sync` generates index/tree from local + GitHub state.

## What it creates

- `spec-dock/`
  - `spec-dock.version` (installed spec-dock version)
  - `docs/` (guide)
  - `templates/` (initiative/epic/issue/adr templates)
  - `scripts/` (runtime scripts; local operations)
  - `initiatives/` (spec tree root; always-on)
    - generated nodes include `artifacts/rules.md` for new working artifacts and do not include scope-local node creation wrappers
    - legacy `discussions/` content is preserved when present, but is not the default destination for new working artifacts
  - `active/` (generated pointers; gitignored)
  - `.agent/` (generated agent state; gitignored)
  - `.workbench/` (optional experimental root Workbench; date buckets/manual selection; gitignored)
  - `.gitignore` (ignores `active/`, `.agent/`, `.workbench/` (and legacy `.work/`))
- `.agents/skills/` (Codex-compatible installed surface)
  - `spec-dock/` (Storage Core and Authoring Kit guidance)
  - `spec-dock-grill-with-docs/` (optional operator-owned documentation Artifact helper)

## Testing

```bash
# Ordinary local test commands: run the fast lane. Selected full-regression
# tests are skipped with a stable policy reason.
uv run pytest
uv run pytest tests/unit

# Focused pytest commands use the same default policy.
uv run pytest tests/unit/path_to_test.py

# Inspect the full-regression selection only. This does not grant permission
# to run its test bodies.
uv run pytest -m full_regression

# Intentional full regression: the only local command that permits all test bodies.
uv run pytest --run-full-regression

# Local static-analysis gate: Ruff check, Ruff format check, and mypy
make lint
```

The policy skip reason is `full_regression test is disabled by default; use
--run-full-regression to run it`. Add `--run-full-regression` to a marker
selection when deliberately running only the heavy lane, for example
`uv run pytest --run-full-regression -m full_regression`.

### Provider test workflows and post-merge operation

`Provider CI` / `provider-tests` runs on pull requests and remains the merge
blocker. It runs `make lint` and the ordinary `uv run pytest` command only; it
does not run the full regression. `Provider Full Regression` is an independent
workflow that runs `uv run pytest --run-full-regression` after a push to `main`
or when started with `workflow_dispatch`. It is post-merge validation, not a
retroactive merge blocker. No scheduled or cron execution is configured.

If `Provider Full Regression` fails, the repository maintainer checks the
run's SHA, failed tests, logs, duration, and summary. Reproduce the same SHA
locally with `uv run pytest --run-full-regression` when needed, then normally
apply a forward fix or rerun the GitHub Actions workflow. The workflow does
not automatically roll back a merge or create an Issue.

If a selector omission, missing required check, or unacceptable escape is
found, stop the next merge decision and return the PR test command in
`.github/workflows/provider-ci.yml` to `uv run pytest --run-full-regression`.
If the default policy skip itself is unsafe, disable that conditional skip.
Keep the markers, explicit full command, full workflow, and measurement
evidence; reintroduce the fast gate only after a fresh review. A merge-ready
PR still requires a human to perform the merge.

---

## 日本語（概要）

`spec-dock` は、既存リポジトリに `spec-dock/`（仕様書駆動開発のためのドキュメント一式）と
Codex 互換の二つの補助Skillを生成するためのスキャフォルディングツールです。

実行は `uvx` を想定しており、導入後は生成されたファイル（Markdown/スクリプト/Skill）を使って運用します。

SpecDockの通常操作はCodex agentが実行するagent-first運用を想定しています。利用者の依頼または承認済み計画に必要なコマンドはagentが実行・検証し、コマンド例の提示だけで利用者へ返しません。破壊的操作は対象と結果が依頼または承認済み計画に明記されている場合に限り、PRのmergeはrepositoryのhuman gateに従います。

v2 では `spec-dock/initiatives/` に Initiative → Epic → Issue の仕様ツリーを **常置**し、
`spec-dock/active/` を “現在取り組んでいる対象” の固定入口（symlink）として使います。
状態の集計は `spec-dock/.agent/index.json` と `spec-dock/.agent/tree.json` を `./spec-dock/scripts/spec-dock sync` で自動生成します（Git 管理しません）。

補足: 通常の issue 実行開始/終了は `issue start <target>` / `issue finish` を primary path とし、unfinished active issue guard だけを bypass する場合は `issue start <target> -f` / `--force` を使います。`active set` / `active set --checkout` は manual / recovery 向けの low-level path として扱います。`new/import {initiative,epic,issue}` の `--title`/`--slug` には入力制約（ASCII / kebab-case）があり、`active set --checkout` を使う場合はブランチ名が `<id>-<slug>`（不適合なら `<id>`）へ正規化されます。
また、`github.issue_number` は initiative/epic/issue をまたいで一意です（重複は検知されます）。詳細は導入先の `spec-dock/docs/reference_github.md`（このリポジトリでは `src/spec_dock/assets/spec_dock/docs/reference_github.md`）を参照してください。
