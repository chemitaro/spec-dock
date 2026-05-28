---
kind: source-capture-metadata
source_repo: "https://github.com/mattpocock/skills"
source_commit: "0288510dd61ff6ef7c2003834082ab8f2387e80e"
source_commit_url: "https://github.com/mattpocock/skills/commit/0288510dd61ff6ef7c2003834082ab8f2387e80e"
source_commit_date: "2026-05-27T12:36:22Z"
captured_at: "2026-05-28"
captured_for: "iss-00134"
license_file: "LICENSE"
---

# Matt Pocock Skills Source Capture

This directory contains a issue-local source capture of Markdown documentation and manifest files from `mattpocock/skills`.

## Capture Scope
- Included:
  - Root documentation and license files.
  - Skill `SKILL.md` files.
  - Supporting Markdown files under skill directories.
  - `.claude-plugin/plugin.json`.
- Excluded for now:
  - Executable helper scripts under `scripts/` or skill-local `scripts/`.

## Intended Use
- Use this directory as the stable local evidence base for research and ChatGPT-assisted analysis.
- Prefer referencing these local files in follow-up prompts instead of repeatedly asking ChatGPT to browse the upstream repository.
- Treat this as vendor/source evidence, not as an adopted spec-dock design decision.

## Follow-Up
- If script behavior becomes relevant to the design, capture the excluded scripts in a separate follow-up note before relying on them.
