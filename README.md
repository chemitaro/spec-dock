# spec-dock

`spec-dock` scaffolds a lightweight spec-driven documentation workspace into an existing repository.

It is designed to be executed via `uvx` (ephemeral install). After scaffolding, your project uses the
generated files (Markdown templates, scripts, Codex skill); the `spec-dock` package itself is not
required at runtime.

## Usage (uvx)

```bash
# Install into the current directory
uvx --from git+https://github.com/<ORG>/<REPO> spec-dock init

# Install into a target path
uvx --from git+https://github.com/<ORG>/<REPO> spec-dock init /path/to/project

# Overwrite managed files if '.specdoc' already exists
uvx --from git+https://github.com/<ORG>/<REPO> spec-dock init --force

# Update managed files (docs/templates/scripts/skill) without touching .specdoc/current by default
uvx --from git+https://github.com/<ORG>/<REPO> spec-dock update

# Reset '.specdoc/current' from templates (optional)
uvx --from git+https://github.com/<ORG>/<REPO> spec-dock update --reset-current
```

## What it creates

- `.specdoc/`
  - `docs/` (guide)
  - `templates/` (requirement/design/plan/report)
  - `scripts/` (helper scripts)
  - `current/` (initialized from templates)
  - `completed/` (empty directory)
- `.codex/skills/spec-driven-tdd-workflow/` (Codex skill)

---

## 日本語（概要）

`spec-dock` は、既存リポジトリに `.specdoc/`（仕様書駆動開発のためのドキュメント一式）と
Codex Skill を生成するためのスキャフォルディングツールです。

実行は `uvx` を想定しており、導入後は生成されたファイル（Markdown/スクリプト/Skill）を使って運用します。
