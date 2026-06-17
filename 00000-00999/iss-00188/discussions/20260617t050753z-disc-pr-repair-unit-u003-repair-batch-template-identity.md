---
種別: disc
ID: "20260617t050753z-disc"
タイトル: "PR Repair Unit U003"
状態: "proposed"
作成者: "iwasawayuuta"
最終更新: "2026-06-17"
親: ["iss-00188"]
関連: []
authority: "proposed"
derived_from:
  - "/private/tmp/pr-195-observation-b04c0b1d/result.json"
reflected_to: []
---

# 20260617t050753z-disc PR Repair Unit U003

## Repair Unit Metadata

- source_batch: `20260617t043527z-pr-repair-batch`
- unit_id: U003
- covered_ids: I003
- source_links:
  - `/private/tmp/pr-195-observation-b04c0b1d/result.json`
  - review comment id 3425692868
  - review thread `PRRT_kwDOQ99OK86KGvVo`
- failure_class: `review_feedback:repair-batch-template-identity`
- risk_class: blocking
- disposition: fix-now

## Validity Analysis

Valid. The workflow now creates a `pr-repair-batch` file via `new doc`, but the skill-local `templates/pr-repair-batch.md` still uses stale `disc` identity placeholders. Guidance that says to create/update from that template can overwrite or mix generated identity fields.

## Need-To-Fix Decision

Fix now. This is directly in scope for #188 because runtime-owned filename and identity generation must not be undermined by shipped skill guidance.

## Root Cause

The implementation updated the writable-scope creation path to `new doc pr-repair-batch`, but left the skill-local template semantics ambiguous: the template is still presented as the target artifact source rather than section/body scaffolding or a matching `pr-repair-batch` template.

## Options Considered

- Convert the skill-local template to a valid `pr-repair-batch` template with matching front matter.
- Keep the skill-local template as section/body reference only and explicitly preserve the generated front matter.
- Remove the skill-local template from writable-scope flow entirely.

## Recommended Design

Use the minimal guidance/template correction that prevents stale identity overwrite. When a writable SpecDock scope exists, the generated file from `new doc pr-repair-batch` owns front matter identity. Any skill-local template content must be body-section scaffolding only, or the template must be aligned so it no longer carries stale `disc` placeholders.

## Implementation Plan

1. Update provider-side `src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/SKILL.md` guidance to preserve generated front matter identity.
2. Update the corresponding provider-side skill template if it remains referenced by writable-scope flow.
3. Mirror required dogfooding install-root copies if the repo's asset tests expect parity.
4. Keep repair units as ordinary `disc`; do not add a `pr-repair-unit` doc type.

## Validation Plan

- Run targeted `rg` checks showing no guidance asks the agent to overwrite generated `pr-repair-batch` front matter from a stale `disc` template.
- Run relevant asset parity / installer tests if touched.
- Run `git diff --check`.

## Implementation Result

- Implemented by doc-writer `019ed3fd-7f45-7040-907e-5623693f1d5b`.
- Changed provider and dogfooding skill/template assets:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/templates/pr-repair-batch.md`
  - `.agents/skills/github-pr-merge-preparer/SKILL.md`
  - `.agents/skills/github-pr-merge-preparer/templates/pr-repair-batch.md`
- Guidance now says the `new doc pr-repair-batch` generated file owns front matter identity and the skill-local template is body-section scaffold only.
- Skill-local `templates/pr-repair-batch.md` no longer contains stale `disc` front matter or `<DISC_ID>`.
- Verification:
  - `rg -n "種別: disc|<DISC_ID>|Create or update a PR repair batch from|new doc pr-repair-unit" src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer .agents/skills/github-pr-merge-preparer` -> no matches, exit 1 expected.
  - provider/dogfooding `SKILL.md` diff -> no output.
  - provider/dogfooding `templates/pr-repair-batch.md` diff -> no output.
  - `uv run pytest tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_71_checked_in_dogfooding_agent_tooling_parity_matches_install_root_assets tests/unit/infra/test_init_update.py::TestInitUpdate::test_bundled_skill_assets_cover_managed_manifest tests/unit/infra/test_init_update.py::TestInitUpdate::test_spec_document_templates_keep_policy_out_of_scaffold` -> 3 passed.
  - `git diff --check` -> pass.

## Commit Evidence

- pending repair commit

## Re-observation Result

- pending PR re-observation after repair commit/push

## Residual Risk / Follow-up

- No known residual risk after targeted stale-guidance and parity verification; PR re-observation still required to close thread `PRRT_kwDOQ99OK86KGvVo`.
