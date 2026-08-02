---
種別: review content freeze receipt
ID: "iss-00346-s99-review-content-freeze"
対象: "iss-00346"
状態: "frozen-before-review"
---

# S99 review content freeze

- Candidate branch: `iss-00346-integration-distribution-and-final-quality`
- Candidate head: `PENDING_FREEZE_COMMIT`
- Base: `origin/main` (resolved before freeze)
- `review_content_hash`: `26201290c13add93e3dc6b7dabf4f3f4cc2dcc7a4e68d9f9e77b75e658b07896`
- Hash algorithm: sorted manifest TSV bytes; each line is `repo-relative-path<TAB>sha256(file-bytes)\n`; the SHA-256 above is over the complete manifest bytes.
- Scope: provider/consumer docs, Issue 346 canonical requirement/design/plan, runtime projections, tests, assurance metadata, and normalized Issue/Epic reports.
- Excluded from scope: `.workbench/`, advisory `artifacts/` (except this receipt as evidence), and the mutable S99 review-evidence/freeze blocks.
- Issue report normalization: remove `S99_REVIEW_CONTENT_FREEZE_BEGIN..END` and `S99_REVIEW_EVIDENCE_BEGIN..END`; replace the `EAL-015` row with `| EAL-015 | adopted | [reviewer fields normalized] |`.
- Epic report normalization: current report bytes are included as recorded; later PR/review evidence must be added only in the Issue S99 evidence block or by a new candidate/re-freeze.
- The review output is advisory evidence. It does not override the Issue requirement/design/plan or change the scope.
- This receipt is excluded from its own hash scope to avoid self-reference.

## Frozen manifest

```text
spec-dock/docs/README.md	ee5f433f66469aed9acc54e516dc0e2f4d8e69fb90987fe8ddd9063e9ecb2a7b
spec-dock/docs/guide.md	21fca9bcf9edc0a90185095ab0510fbaf6946c49dba9dcf8822ec326c09045cf
spec-dock/docs/rules/root/artifacts.md	e63c08ef5f332f963420eeb1780dcdb7bcd9f924beb80485bc2a3afb304f0abb
spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00343-workbench-shell-and-explicit-file-artifact-import/issues/iss-00346-integration-distribution-and-final-quality/.assurance.json	3306c639971da76a993c8ce97434206d88753d93c13870975a8cac7c84ecc3b2
spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00343-workbench-shell-and-explicit-file-artifact-import/issues/iss-00346-integration-distribution-and-final-quality/design.md	01854355ffa153c32663c3305fb2e2293766bcf16c3e8f5b03fcfa951fa92062
spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00343-workbench-shell-and-explicit-file-artifact-import/issues/iss-00346-integration-distribution-and-final-quality/plan.md	e61b25e82e2cd6a494ec17a53812ad99a8d95360b5b22bbb89d341caaeca84d7
spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00343-workbench-shell-and-explicit-file-artifact-import/issues/iss-00346-integration-distribution-and-final-quality/requirement.md	804865b55a8abf1fd4d258b3a03e96fb26b7906dce8b38abe86f6ff56aeed5a3
spec-dock/scripts/spec_dock_runtime/application/import_file_artifact.py	afa364ff4e2e73b3fa867f14a48428a055294b623017a7838bec1b0a12eee29e
spec-dock/scripts/spec_dock_runtime/domain/artifacts.py	2e5972715e21a5ef3968ce48de7884579619204e709c3545ec5554f8dac92b84
src/spec_dock/assets/spec_dock/docs/README.md	ee5f433f66469aed9acc54e516dc0e2f4d8e69fb90987fe8ddd9063e9ecb2a7b
src/spec_dock/assets/spec_dock/docs/guide.md	21fca9bcf9edc0a90185095ab0510fbaf6946c49dba9dcf8822ec326c09045cf
src/spec_dock/assets/spec_dock/docs/rules/root/artifacts.md	e63c08ef5f332f963420eeb1780dcdb7bcd9f924beb80485bc2a3afb304f0abb
tests/cli_runtime/test_artifact_import_s04.py	1be585b08cd8312a8b5ff08698e778b389464ec533b7748b78fd51114e0d6a90
tests/integration/iss346_platform_probe.py	6e4f78000c6130c346bc0405410f8e4a406ea3bb41384cc2c657ecca3c58ee43
tests/integration/test_epic_00343_distribution.py	bf4edf59e27c7c25d0ece5ec40c88cbd712ede88ce8de15691a2e7cfbf2b8ada
tests/unit/infra/test_init_update.py	1e02a1262c73d6f7dc0eb35c93277d28d2742087460ea0256e38fa6cb323e435
spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00343-workbench-shell-and-explicit-file-artifact-import/issues/iss-00346-integration-distribution-and-final-quality/report.md	4d2a13ca839c63892b933351b76110588a2bad3e98fbe9d659b87042f09458c8
spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00343-workbench-shell-and-explicit-file-artifact-import/report.md	68a139186176da15b0910e61a7eae345e632664106d0005063562faadd46e740
```

