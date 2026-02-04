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

# Create nodes (all-lowercase ids; e.g. init-0001, epic-0001, iss-0001)
uvx --from git+https://github.com/chemitaro/spec-dock spec-dock new initiative --title "Auth platform"
uvx --from git+https://github.com/chemitaro/spec-dock spec-dock new epic --initiative init-0001 --title "JWT auth"
uvx --from git+https://github.com/chemitaro/spec-dock spec-dock new issue --epic epic-0001 --title "Add refresh token" --github-issue 123
uvx --from git+https://github.com/chemitaro/spec-dock spec-dock new adr --issue iss-0123 --title "Token rotation strategy"

# Set active issue pointers (symlinks) and generate context-pack
uvx --from git+https://github.com/chemitaro/spec-dock spec-dock active set --issue iss-0123

# Generate state.json (local scan; optionally enrich from GitHub via gh)
uvx --from git+https://github.com/chemitaro/spec-dock spec-dock sync
uvx --from git+https://github.com/chemitaro/spec-dock spec-dock sync --github

# Validate the spec tree structure
uvx --from git+https://github.com/chemitaro/spec-dock spec-dock validate
```

## What it creates

- `.spec-dock/`
  - `spec-dock.version` (installed spec-dock version)
  - `docs/` (guide)
  - `templates/` (initiative/epic/issue/adr templates)
  - `scripts/` (helper scripts; optional)
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
状態の集計は `.spec-dock/.work/state.json` を `spec-dock sync` で自動生成します（Git 管理しません）。
