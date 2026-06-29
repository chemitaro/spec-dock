# Template Pack Adoption Research

## Source

- Attachment: `/Users/iwasawayuuta/.codex/attachments/ed533576-0494-4554-8480-1ea2c23320e0/spec-dock-issue-grade-templates.zip`
- Extracted for inspection: `/private/tmp/spec-dock-issue-grade-templates/spec-dock-issue-grade-templates/`

## Observed Contents

The ZIP contains a deterministic Issue Grade Template Pack:

- `src/spec_dock/assets/spec_dock/templates/issue/requirement.md`
- `src/spec_dock/assets/spec_dock/templates/issue-profiles/lite/design.md`
- `src/spec_dock/assets/spec_dock/templates/issue-profiles/lite/plan.md`
- `src/spec_dock/assets/spec_dock/templates/issue-profiles/standard/design.md`
- `src/spec_dock/assets/spec_dock/templates/issue-profiles/standard/plan.md`
- `src/spec_dock/assets/spec_dock/templates/issue-profiles/strict/design.md`
- `src/spec_dock/assets/spec_dock/templates/issue-profiles/strict/plan.md`
- `src/spec_dock/assets/spec_dock/templates/issue-profiles/critical/design.md`
- `src/spec_dock/assets/spec_dock/templates/issue-profiles/critical/plan.md`
- `docs/template-matrix.md`
- `docs/final-review.md`
- `README.md`

## Key Findings

- The pack uses a common `issue/requirement.md` template.
- `design.md` and `plan.md` are profile-specific under `issue-profiles/<grade>/`.
- Actual Issue directories are still expected to contain one canonical `requirement.md`, `design.md`, `plan.md`, and `report.md` set.
- The pack intentionally does not replace the existing shared `issue/report.md`; plan templates map expected evidence into `report.md`.
- `lite`, `standard`, `strict`, and `critical` match current assurance profile terminology.

## Adoption Decision

Adopt the pack as the primary source material for iss-00247.

Requirement impact:

- Expand the Issue from only moving `design.md` / `plan.md` prose out of JSON to also updating the common Issue `requirement.md` template.
- Keep `report.md` migration out of scope.

Design impact:

- Treat this Issue as `strict`, because it changes scaffold/template contract and workflow-sensitive planning artifacts.
- Add provider-side `templates/issue-profiles/<profile>/{design,plan}.md`.
- Keep `authorized_profile` as the only runtime template selection authority.

Plan impact:

- Add implementation steps for template asset adoption, runtime template resolution, fail-closed validation, mixed-mode report compatibility, and installed scaffold parity.
