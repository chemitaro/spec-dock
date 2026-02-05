# spec-dock

`spec-dock` scaffolds a lightweight spec-driven documentation workspace into an existing repository.

It is designed to be executed via `uvx` (ephemeral install). After scaffolding, your project uses the
generated files (Markdown templates, scripts, Codex skill); the `spec-dock` package itself is not
required at runtime.

## Usage (uvx)

```bash
# Install into the current directory
uvx --from git+https://github.com/chemitaro/spec-dock spec-dock init

# Install into a target path
uvx --from git+https://github.com/chemitaro/spec-dock spec-dock init /path/to/project

# Overwrite managed files if '.spec-dock' already exists
uvx --from git+https://github.com/chemitaro/spec-dock spec-dock init --force

# Skip installing the Codex skill (optional)
uvx --from git+https://github.com/chemitaro/spec-dock spec-dock init --no-skill

# Update managed files (docs/templates/scripts/skill)
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

Troubleshooting:
- If `.spec-dock/initiative/current` or `spec-dock-close*.sh` are generated, you're running the legacy (v1) scaffold.
  v2 generates `.spec-dock/initiatives/`, `.spec-dock/active/`, and `.spec-dock/.work/`.
- If your local clone contains the v2 files but `uvx` still behaves like v1, try one of:
  - Avoid the shared cache for a single run: `uvx --no-cache --from ~/src/spec-dock spec-dock init`
  - Use a dedicated cache directory: `uvx --cache-dir /tmp/uv-cache-spec-dock --from ~/src/spec-dock spec-dock init`
  - Remove stale build outputs in the tool repo (this often causes mixed v1/v2 assets): `rm -rf ~/src/spec-dock/build`
  - (If possible) clear the cache: `uv cache clean`

## Usage (local scripts)

After `init`, day-to-day operations are done via the runtime script installed into your repo:
`./.spec-dock/scripts/spec-dock`.

```bash
# Create nodes (all-lowercase ids; e.g. init-0001, epic-0001, iss-0001)
./.spec-dock/scripts/spec-dock new initiative --title "Auth platform"
./.spec-dock/scripts/spec-dock new epic --initiative 0001 --title "JWT auth"   # also accepts init-0001
./.spec-dock/scripts/spec-dock new issue --epic 0001 --title "Add refresh token" --github-issue 123  # also accepts epic-0001
./.spec-dock/scripts/spec-dock new adr --issue iss-0123 --title "Token rotation strategy"

# Set active issue pointers (symlinks) and generate context-pack
./.spec-dock/scripts/spec-dock active set --issue 0123  # also accepts iss-0123

# Generate state.json (local scan; optionally enrich from GitHub via gh)
./.spec-dock/scripts/spec-dock sync
./.spec-dock/scripts/spec-dock sync --github

# Validate the spec tree structure
./.spec-dock/scripts/spec-dock validate
```

See `docs/sync-aggregation.md` for how `sync` aggregates local + GitHub state.

## What it creates

- `.spec-dock/`
  - `spec-dock.version` (installed spec-dock version)
  - `docs/` (guide)
  - `templates/` (initiative/epic/issue/adr templates)
  - `scripts/` (runtime scripts; local operations)
  - `initiatives/` (spec tree root; always-on)
  - `active/` (generated pointers; gitignored)
  - `.work/` (generated state; gitignored)
  - `.gitignore` (ignores `active/` and `.work/`)
- `.codex/skills/spec-driven-tdd-workflow/` (Codex skill)

## Testing

```bash
python -m unittest discover -v
```

---

## 日本語（概要）

`spec-dock` は、既存リポジトリに `.spec-dock/`（仕様書駆動開発のためのドキュメント一式）と
Codex Skill を生成するためのスキャフォルディングツールです。

実行は `uvx` を想定しており、導入後は生成されたファイル（Markdown/スクリプト/Skill）を使って運用します。

v2 では `.spec-dock/initiatives/` に Initiative → Epic → Issue の仕様ツリーを **常置**し、
`.spec-dock/active/` を “現在取り組んでいる対象” の固定入口（symlink）として使います。
状態の集計は `.spec-dock/.work/state.json` を `./.spec-dock/scripts/spec-dock sync` で自動生成します（Git 管理しません）。
