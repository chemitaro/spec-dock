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

`spec-dock update` refreshes managed files/docs/templates/scripts/skills, but it is not `init --force`
and does **not** guarantee in-place migration of older workspaces. If an older tree still has legacy
`meta.json`, partial linkage, or current-repo mismatches, current runtime commands may
reject/fail-fast; normalize manually or rebuild the workspace instead of expecting auto-migration.

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

After `init`, day-to-day operations are done via the runtime script installed into your repo:
`./spec-dock/scripts/spec-dock`.

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

# Note: `--no-github` remains only as a compatibility flag and is rejected for node create/import paths.

# Scope-local wrappers created in generated nodes (single title arg)
<initiative-dir>/epics/new-epic "JWT auth"
<epic-dir>/issues/new-issue "Add refresh token"

# ADRs are created via runtime command (no scope-local ADR wrapper)
./spec-dock/scripts/spec-dock new doc adr --issue iss-00123 --title "Token rotation strategy"

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
- `./spec-dock/scripts/spec-dock update [path]` is the repo-local self-update path. It wraps the
  installer update command by running
  `uvx --no-cache --from git+https://github.com/chemitaro/spec-dock spec-dock update <target>`.
  The target defaults to the current working directory, and an explicit path is resolved before it is
  passed to the installer.
- Runtime update always uses the fixed upstream `git+https://github.com/chemitaro/spec-dock` source
  with `uvx --no-cache`; it does not expose arbitrary package source, cache, or `--force` options.
- Runtime update refreshes managed files through installer update. It is not `init --force` and is
  not an automatic migration tool for legacy or incompatible workspaces.
- For `new/import {initiative,epic,issue}`, `--title` is restricted to ASCII (alphanumerics + single spaces) and `--slug` is kebab-case.
- Legacy sequential discussion docs are grandfathered only. New docs do not reuse legacy sequence names, and spec-dock does not auto-rename or auto-repair them to preserve forced backward compatibility.
- Normal issue execution should use `issue start <target>` / `issue finish` as the primary path. Use `issue start <target> -f` / `--force` only to bypass the unfinished active issue guard; dependency readiness still applies.
- `issue finish` is lifecycle closure only: it closes or confirms the linked GitHub issue and clears active state, but it does not guarantee commit, push, PR, merge, validate, test, or review completion. Record delivery completion evidence before running it.
- Treat direct `active set` / `active set --checkout` as manual / recovery / low-level commands. `active set` updates active pointers from local nodes first. Branch operations are opt-in via `--checkout`.
- With `active set --checkout`, the branch name is normalized to `<id>-<slug>` (fallback: `<id>`) to keep branch names ASCII.
- `github.issue_number` links (initiative/epic/issue) must be globally unique; duplicates are rejected/detected. See `src/spec_dock/assets/spec_dock/docs/reference_github.md` for details.
- Generated initiative/epic/issue nodes include `discussions/` (`rules.md` included).
- For non-ADR notes/discussions/research docs, copy templates from `spec-dock/templates/discussions/{note,disc,research}.md`.
- ADR docs are created by `./spec-dock/scripts/spec-dock new doc adr --{initiative|epic|issue} <id> --title "..."`.
- Generated nodes do not include template-derived `README.md`.

See `docs/sync-aggregation.md` for how `sync` generates index/tree from local + GitHub state.

## What it creates

- `spec-dock/`
  - `spec-dock.version` (installed spec-dock version)
  - `docs/` (guide)
  - `templates/` (initiative/epic/issue/adr templates)
  - `scripts/` (runtime scripts; local operations)
  - `initiatives/` (spec tree root; always-on)
    - generated nodes include wrappers (`epics/new-epic`, `issues/new-issue`) and `discussions/` (`rules.md`)
  - `active/` (generated pointers; gitignored)
  - `.agent/` (generated agent state; gitignored)
  - `.gitignore` (ignores `active/` and `.agent/` (and legacy `.work/`))
- `.agents/skills/` (Codex-compatible multi-skill set)
  - `spec-driven-tdd-workflow/` (hub; entry point)
  - `spec-dock-initiative-planning/` (leaf: initiative workflow)
  - `spec-dock-epic-planning/` (leaf: epic workflow)
  - `spec-dock-issue-execution/` (leaf: issue workflow)
  - `spec-dock-adr-facilitation/` (leaf: ADR workflow)

## Testing

```bash
python -m unittest discover -v
```

---

## 日本語（概要）

`spec-dock` は、既存リポジトリに `spec-dock/`（仕様書駆動開発のためのドキュメント一式）と
Codex 互換 Skill セット（hub + 4 leaf）を生成するためのスキャフォルディングツールです。

実行は `uvx` を想定しており、導入後は生成されたファイル（Markdown/スクリプト/Skill）を使って運用します。

v2 では `spec-dock/initiatives/` に Initiative → Epic → Issue の仕様ツリーを **常置**し、
`spec-dock/active/` を “現在取り組んでいる対象” の固定入口（symlink）として使います。
状態の集計は `spec-dock/.agent/index.json` と `spec-dock/.agent/tree.json` を `./spec-dock/scripts/spec-dock sync` で自動生成します（Git 管理しません）。

補足: 通常の issue 実行開始/終了は `issue start <target>` / `issue finish` を primary path とし、unfinished active issue guard だけを bypass する場合は `issue start <target> -f` / `--force` を使います。`active set` / `active set --checkout` は manual / recovery 向けの low-level path として扱います。`new/import {initiative,epic,issue}` の `--title`/`--slug` には入力制約（ASCII / kebab-case）があり、`active set --checkout` を使う場合はブランチ名が `<id>-<slug>`（不適合なら `<id>`）へ正規化されます。
また、`github.issue_number` は initiative/epic/issue をまたいで一意です（重複は検知されます）。詳細は導入先の `spec-dock/docs/reference_github.md`（このリポジトリでは `src/spec_dock/assets/spec_dock/docs/reference_github.md`）を参照してください。
