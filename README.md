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

# Update managed files (docs/templates/scripts/skill) without touching .spec-dock/current by default
uvx --from git+https://github.com/chemitaro/spec-dock spec-dock update

# Reset '.spec-dock/current' from templates (optional)
uvx --from git+https://github.com/chemitaro/spec-dock spec-dock update --reset-current
```

## What it creates

- `.spec-dock/`
  - `docs/` (guide)
  - `templates/` (requirement/design/plan/report)
  - `scripts/` (helper scripts)
  - `current/` (initialized from templates)
  - `completed/` (empty directory)
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
