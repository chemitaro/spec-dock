---
種別: pr-repair-batch
ID: "20260710t122133z-pr-repair-batch"
タイトル: "PR 311 Repair Batch"
状態: "draft | proposed | archived"
作成者: "iwasawayuuta"
最終更新: "2026-07-10"
親: ["iss-00309"]
関連: []
authority: "proposed"
derived_from: []
reflected_to: []
---

# 20260710t122133z-pr-repair-batch PR 311 Repair Batch

## PR / Observation Metadata

- PR URL: https://github.com/chemitaro/spec-dock/pull/311
- PR number: 311
- Repository: chemitaro/spec-dock
- Base branch: main
- Head branch: iss-00309-chatgpt-first-planning-skills-and-fallback-route-redesign
- Latest head SHA: 6cb24d78105bb7f4a7d308a30bea6ac917dfe029
- Observation command: `wait_pr_observation.sh --repo chemitaro/spec-dock --pr 311 --head-sha 6cb24d78105bb7f4a7d308a30bea6ac917dfe029`
- Observation final JSON / evidence: status=timeout, Provider CI still running, latest review P1=3, P2=2
- Observation status: timeout with complete latest-head review evidence
- Trigger comment id: 4937568250
- Trigger created_at: 2026-07-10T16:50:22Z
- Trigger boundary: reviewed head 6cb24d78105bb7f4a7d308a30bea6ac917dfe029
- Resume metadata: available for unchanged head; not used because blocking repair produces a new head
- New trigger approved: yes; human approved an invariant-based second repair loop
- Observation limitation: GitHub Actions and Codex review only; external checks are not observed
- Batch status: iteration 4 repairing

## Batch Purpose

Use this repo-persistent batch to triage and repair blocking PR observation
results. A blocking result is a `P0`/`P1` review finding, required GitHub Actions
CI failure, visible merge conflict, blocking observation limitation, or other
merge-prepared blocker.

This batch separates raw intake from severity decisions, groups related findings
by `root_cause_family`, creates repair units only for blocking families, records
non-blocking findings only when a blocking repair commit is already being made,
and preserves residual risk for the final merge-prepared decision.

`root_cause_family` is documentation and LLM judgment vocabulary for this
discussion artifact. It is not a required runtime JSON field, parser contract,
blocker fingerprint, or stalled-observation contract.

## Persistence Policy

This file is for blocking repair work.

Use this repo-persistent batch when:

- `P0`/`P1` review findings exist.
- Required GitHub Actions CI failures exist.
- Merge blockers exist.
- Blocking observation limitations require repair or human-gate tracking.
- Branch mutation is already required for blocking repair and non-blocking
  findings can be recorded in the same commit without causing an extra CI run.

Do not update this batch solely to record terminal `P2`/`P3` findings after the
latest pushed head has no blockers. Record terminal `P2`/`P3` findings in the
final merge-prepared report instead, unless the user explicitly requests
separate follow-up tracking outside the current PR branch.

## Observation Batch Summary

| field | value |
| --- | --- |
| latest_head_sha | 6cb24d78105bb7f4a7d308a30bea6ac917dfe029 |
| observation_status | timeout with actionable review |
| required_ci_status | one Provider CI success, one duplicate run pending at timeout |
| review_status | unresolved |
| p0_count | 0 |
| p1_count | 3 |
| p2_count | 2 |
| p3_count | 0 |
| required_ci_failure_count | 0 |
| merge_blocker_count | 3 |
| blocking_family_count | 3 |
| non_blocking_family_count | 2 |
| terminal_non_blocking_only | no |
| branch_mutation_required | yes |
| ci_rerun_expected | yes |
| review_clean | no |
| merge_prepared_candidate | no |

## Raw Intake Inventory

Add one row per observed review finding, required CI failure, merge blocker, or
observation limitation from the same observation batch. Keep raw reviewer
priority separate from the final severity decision.

| item_id | source_type | source_id | reported_priority | path | line | raw_summary | evidence_type | current_head_sha | family_id | intake_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| R001 | review | 3558754353 | P1 | zip_contract.py | 230 | Windows drive-qualified ZIP entry is accepted | code-path | 8c66118743ab55b3032d95eccd6eebf999fb06c2 | F001 | triaged |
| R002 | review | 3558754356 | P1 | candidate_contract.py | 774 | Windows drive/backslash draft path is accepted | code-path | 8c66118743ab55b3032d95eccd6eebf999fb06c2 | F001 | triaged |
| R003 | review | 3558754361 | P1 | pack_prepare.py | 376 | Broken output-dir symlink bypasses rejection | code-path | 8c66118743ab55b3032d95eccd6eebf999fb06c2 | F002 | triaged |
| R004 | review | 3558754366 | P1 | pack_prepare.py | 349 | Exact initiatives root bypasses canonical target rejection | repro | 8c66118743ab55b3032d95eccd6eebf999fb06c2 | F002 | triaged |
| R005 | ci | Provider CI / test_wrappers | CI | tests/cli_runtime/test_wrappers.py | 136 | Current skill no longer references workflow_clarification.md | failing-test | 8c66118743ab55b3032d95eccd6eebf999fb06c2 | F003 | triaged |
| R006 | review | 3559156685 | P1 | github_sync_preflight.py | 231 | Runtime import creates bytecode before git dirtiness observation | repro | 8046bc3e7f2d8817f9c6680f355e271707039172 | F004 | triaged |
| R007 | review | 3559156692 | P1 | pack_prepare.py | 386 | Existing descendant stops symlink ancestor traversal | repro | 8046bc3e7f2d8817f9c6680f355e271707039172 | F002 | triaged |
| R008 | review | 3559156702 | P2 | backend_invoke.py | 263 | Read-side prompt-pack path loses lexical symlink identity | repro | 8046bc3e7f2d8817f9c6680f355e271707039172 | F005 | triaged |
| R009 | review | 3559156706 | P2 | zip_contract.py | 83 | Tree review checks only direct input symlink | repro | 8046bc3e7f2d8817f9c6680f355e271707039172 | F006 | triaged |
| R010 | review | 3560105408 | P1 | draft_adoption_validation.py | 162 | Passing review report is not bound to selected fill source pack | code-path | c179811ee052467b87867275da3188fe71dd6f73 | F007 | triaged |
| R011 | review | 3560105414 | P1 | backend_invoke.py | 387 | Credential-looking manifest attachments bypass outbound filter | repro | c179811ee052467b87867275da3188fe71dd6f73 | F008 | triaged |
| R012 | review | 3560105422 | P1 | draft_adoption_contract.py | 356 | Truthy authority flags outside authority_claims bypass validation | repro | c179811ee052467b87867275da3188fe71dd6f73 | F009 | triaged |
| R013 | review | 3560105427 | P2 | pack_prepare.py | 123 | Existing unowned output directory can be clobbered | code-path | c179811ee052467b87867275da3188fe71dd6f73 | F010 | triaged |
| R014 | review | 3560105432 | P2 | zip_contract.py | 191 | Extracted tree fallback has no total byte cap | code-path | c179811ee052467b87867275da3188fe71dd6f73 | F011 | triaged |
| R015 | review | 3560691385 | P1 | review_chatgpt_authoring_pack.py | 37 | Legacy review arguments are parsed but ignored | code-path | 6cb24d78105bb7f4a7d308a30bea6ac917dfe029 | F012 | triaged |
| R016 | review | 3560691393 | P1 | invoke_chatgpt_backend.py | 102 | Legacy attachment symlink can disclose an external file | repro | 6cb24d78105bb7f4a7d308a30bea6ac917dfe029 | F013 | triaged |
| R017 | review | 3560691397 | P2 | pack_stage.py | 122 | Broken stage-dir symlink raises instead of structured rejection | code-path | 6cb24d78105bb7f4a7d308a30bea6ac917dfe029 | F014 | triaged |
| R018 | review | 3560691402 | P2 | pack_prepare.py | 333 | spec-dock/system is not classified as managed output | code-path | 6cb24d78105bb7f4a7d308a30bea6ac917dfe029 | F015 | triaged |
| R019 | review | 3560691405 | P1 | candidate_validation.py | 128 | Candidate gate does not validate report authority tuple | code-path | 6cb24d78105bb7f4a7d308a30bea6ac917dfe029 | F016 | triaged |
| R020 | observation | timeout | unknown | N/A | N/A | Provider CI remained in progress at observation deadline | timeout | 6cb24d78105bb7f4a7d308a30bea6ac917dfe029 | F017 | triaged |

Do not keep example rows as active inventory.

## Concern Family Catalog

Group inventory items by shared root cause. Do not repair comments one-by-one.

| family_id | root_cause_family | family_title | protected_domain | invariant_or_contract | related_items | max_reported_priority | decided_priority | merge_blocking | disposition | repair_unit | family_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F001 | authoring-pack.windows-path-boundary | Windows形式パスの境界検証 | yes | reviewed/staged pack内の参照はportable relative pathに限定する | R001,R002 | P1 | P1 | yes | fix-now | U001 | unit-created |
| F002 | prompt-pack.output-boundary | prompt-pack出力先の境界検証 | yes | resolve/write前に全lexical componentを検査する | R003,R004,R007 | P1 | P1 | yes | fix-now | U002,U005 | unit-created |
| F003 | planning-skill.current-contract | ChatGPT-first skillの回帰契約 | no | scaffold testは現行skillの必要参照だけを要求する | R005 | CI | required-ci | yes | fix-now | U003 | unit-created |
| F004 | authoring-preflight.observer-purity | preflight観測者の無副作用性 | yes | git状態を観測するruntimeは観測前にworktreeを変更しない | R006 | P1 | P1 | yes | fix-now | U004 | unit-created |
| F005 | backend-prompt-pack-symlink-ancestor | backend read-side lexical path | yes | read-side入力もresolve前のlexical identityを保つ | R008 | P2 | P2 | no | follow-up | N/A | triaged |
| F006 | pack-review-symlink-ancestor-input | tree review lexical path | yes | tree fallback入力もsymlink ancestorを識別する | R009 | P2 | P2 | no | follow-up | N/A | triaged |
| F007 | review-gate-digest-binding | review gateとexact evidenceの結合 | yes | pass reportは検証中evidenceと同一packに結合される | R010 | P1 | P1 | yes | fix-now | U006 | unit-created |
| F008 | backend-secret-attachment-filter | outbound attachment機密path policy | yes | 全attachmentはcopy前とbackend argv生成前に同じpolicyを通る | R011 | P1 | P1 | yes | fix-now | U007 | unit-created |
| F009 | authority-claim-recursive-scan | evidence payload全体のauthority否定 | yes | payload内のどのoperational shapeにも肯定的authority flagを許さない | R012 | P1 | P1 | yes | fix-now | U008 | unit-created |
| F010 | prompt-pack-output-clobber | output ownership | yes | 既存directoryへの上書きはownershipを要求する | R013 | P2 | P2 | no | follow-up | N/A | triaged |
| F011 | tree-review-resource-bound | tree fallback resource cap | yes | lower-authority tree reviewにもtotal size boundを持つ | R014 | P2 | P2 | no | follow-up | N/A | triaged |
| F012 | compatibility-review-wrapper | legacy review adapter parity | yes | accepted legacy flags retain their safety semantics | R015 | P1 | P1 | yes | fix-now | U009 | unit-created |
| F013 | legacy-backend-attachment-symlink | legacy attachment source identity | yes | source symlinks cannot be laundered through generated names | R016 | P1 | P1 | yes | fix-now | U010 | unit-created |
| F014 | stage-target-symlink-detection | stage output error normalization | yes | unsafe stage targets return structured rejection | R017 | P2 | P2 | no | follow-up | N/A | triaged |
| F015 | managed-output-boundary | complete managed output roots | yes | spec-dock system content is not authoring scratch output | R018 | P2 | P2 | no | follow-up | N/A | triaged |
| F016 | candidate-review-gate-authority | review report authority tuple | yes | pass requires evidence-only authority and exact pack identity | R019 | P1 | P1 | yes | fix-now | U011 | unit-created |
| F017 | observation-timeout | latest-head CI observation | yes | merge preparation requires terminal required CI evidence | R020 | unknown | platform | yes | covered-by | N/A | triaged |

## Classification Values

- `reported_priority`: `P0` / `P1` / `P2` / `P3` / `CI` / `unknown`
- `decided_priority`: `P0` / `P1` / `P2` / `P3` / `required-ci` / `platform` / `unknown`
- `merge_blocking`: `yes` / `no` / `platform-only` / `unknown`
- `validity`: `valid` / `partially-valid` / `false-positive` / `duplicate` / `unknown`
- `failure_class`: `check_failure:<actions_job_or_workflow_name>` / `review_feedback:<stable_topic>` / `merge_conflict` / `base_branch_conflict` / `permission_or_auth` / `external_or_flaky` / `platform_conversation_resolution` / `timeout` / `unknown`
- `need_to_fix`: `yes` / `no` / `follow-up` / `human-decision`
- `disposition`: `fix-now` / `follow-up` / `no-action` / `covered-by` / `needs-human`
- `status`: `untriaged` / `triaged` / `unit-needed` / `unit-created` / `implemented` / `reobserved-pass` / `blocked`

## Per-Family Analysis

Create one subsection per real family.

### F001 authoring-pack.windows-path-boundary

- Related inventory IDs: R001, R002
- Reported priorities: P1, P1
- Decided priority: P1
- Merge-blocking: yes
- Protected domain: path traversal and writes/reads outside reviewed evidence
- Contract / invariant: ZIP entry names and candidate draft paths must be portable, relative, and contained.
- Root cause: POSIX parsing alone did not reject drive-qualified or backslash Windows path forms.
- Why this is one family: both paths cross an evidence boundary through the same missing portable-path invariant.
- Validity analysis: valid and deterministic.
- Need-to-fix decision: yes.
- Options considered: platform-specific resolution; lexical portable-path rejection.
- Recommended disposition: lexical rejection before any Path join.
- Repair scope: ZIP relative-path validator, candidate draft validator, regression tests.
- Out of scope: host-specific Oracle paths.
- Quality gates: focused authoring tests and full provider suite.
- Residual risk: other path consumers remain covered by their existing validators.
- Follow-up handling: none.

### F002 prompt-pack.output-boundary

- Related inventory IDs: R003, R004, R007
- Reported priorities: P1, P1, P1
- Decided priority: P1
- Merge-blocking: yes
- Protected domain: generated-file writes and symlink safety.
- Contract / invariant: prompt packs cannot write until every lexical path component has been inspected before resolve.
- Root cause: the first repair closed leaf/exact-root cases but retained `exists()` as an implicit trust anchor, so an existing descendant reached through an earlier symlink stopped traversal.
- Why this is one family: all three defects bypass output-target rejection before generated-file writes.
- Validity analysis: valid and deterministic.
- Need-to-fix decision: yes.
- Options considered: first-existing-parent trust; resolved containment; full lexical component traversal with an explicit root-level system-alias exception.
- Recommended disposition: full lexical traversal with no existence-based early exit; trust only OS-managed root-level aliases.
- Repair scope: provider/dogfooding output guard and regression tests.
- Out of scope: redesign of all canonical path classification.
- Quality gates: focused authoring tests and full provider suite.
- Residual risk: read-side symlink ancestors, TOCTOU swaps, hardlinks, and Windows reparse points remain separate follow-up risks.
- Follow-up handling: none.

### F003 planning-skill.current-contract

- Related inventory IDs: R005
- Reported priorities: CI
- Decided priority: required-ci
- Merge-blocking: yes
- Protected domain: no.
- Contract / invariant: tests must assert the current minimal ChatGPT-first skill contract.
- Root cause: one wrapper test retained the retired clarification-document reference.
- Why this is one family: single stale assertion.
- Validity analysis: valid CI failure; product behavior is intentional.
- Need-to-fix decision: yes, update the test rather than reintroduce background guidance.
- Options considered: add the old reference back; remove stale assertion.
- Recommended disposition: remove stale assertion.
- Repair scope: tests/cli_runtime/test_wrappers.py only.
- Out of scope: skill body expansion.
- Quality gates: failed test and full provider suite.
- Residual risk: none.
- Follow-up handling: none.

### F004 authoring-preflight.observer-purity

- Related inventory IDs: R006
- Reported priorities: P1
- Decided priority: P1
- Merge-blocking: yes
- Protected domain: required GitHub-synced planning route.
- Contract / invariant: a state observer must not modify the state it evaluates.
- Root cause: the installed launcher imports local runtime modules before preflight checks git status, allowing Python bytecode generation in the managed consumer tree.
- Why this is one family: one process-level side effect makes a clean synchronized branch appear dirty.
- Validity analysis: valid and reproducible; existing tests masked it with `PYTHONDONTWRITEBYTECODE=1`.
- Need-to-fix decision: yes.
- Options considered: launcher bytecode suppression; scaffold gitignore; git-status filtering.
- Recommended disposition: set `sys.dont_write_bytecode = True` before the first local runtime import.
- Repair scope: provider/dogfooding installed launcher and fresh-consumer regression.
- Out of scope: status parser exceptions and gitignore policy expansion.
- Quality gates: run without bytecode env override, require pass, no cache files, and clean porcelain status.
- Residual risk: caches created by old versions must be removed by users before the first upgraded run.
- Follow-up handling: no current PR expansion.

### F005/F006 read-side lexical symlink identity

- Related inventory IDs: R008, R009
- Reported priorities: P2, P2
- Decided priority: P2
- Merge-blocking: no.
- Protected domain: evidence input integrity.
- Contract / invariant: resolve must not erase user-supplied lexical path identity before read-side validation.
- Root cause: backend validation resolves before ancestor inspection; tree review checks only the input leaf.
- Why this is one family: both are read-side ingress gaps, distinct from the P1 write escape.
- Validity analysis: valid material follow-up.
- Need-to-fix decision: follow-up, not this repair loop.
- Options considered: shared utility now; separate cross-ingress hardening.
- Recommended disposition: separate follow-up to avoid optional P2 scope expansion.
- Repair scope: none in this PR iteration.
- Out of scope: candidate/adoption/legacy helper ancestor audit, TOCTOU, hardlinks, Windows reparse points.
- Quality gates: terminal review classification only.
- Residual risk: non-default read-side paths may accept symlink ancestors.
- Follow-up handling: record below; no repair unit.

### F007 review-gate-digest-binding

- Related inventory IDs: R010
- Reported priorities: P1
- Decided priority: P1
- Merge-blocking: yes.
- Protected domain: reviewer gate and evidence adoption.
- Contract / invariant: a passing report grants a gate only to the exact pack identity it reviewed.
- Root cause: selected fill forwarded the report file hash but never compared `pack_digest.content_sha256` with detached fill metadata.
- Why this is one family: digest identity and review-report identity were conflated.
- Validity analysis: valid; unrelated passing reports can open the gate.
- Need-to-fix decision: yes.
- Options considered: recompute a raw pack; require detached `draft_pack_digest`; rely on source/template hashes.
- Recommended disposition: reuse Issue draft adoption's detached `draft_pack_digest` contract and bind it to the report pack digest.
- Repair scope: selected fill validation application/domain and fixtures.
- Out of scope: cryptographic report signatures and per-file post-review immutability.
- Quality gates: match, missing, mismatch, missing report digest, and independent review-file digest tests.
- Residual risk: digest equality does not authenticate the report author.
- Follow-up handling: none in this PR.

### F008 backend-secret-attachment-filter

- Related inventory IDs: R011
- Reported priorities: P1
- Decided priority: P1
- Merge-blocking: yes.
- Protected domain: external backend data disclosure.
- Contract / invariant: original and outbound attachment names must satisfy one credential-path policy before subprocess execution.
- Root cause: path classifiers drifted and the legacy rename could hide `.env` from hidden-path checks.
- Why this is one family: all bypasses arise from incomplete/fragmented filename classification.
- Validity analysis: valid; files can reach backend `--file`.
- Need-to-fix decision: yes.
- Options considered: add four backend strings; central domain classifier shared with prepare and legacy input.
- Recommended disposition: central credential-like path classifier and fail before copy/invocation.
- Repair scope: domain policy, prepare/backend consumers, legacy wrapper, regression sentinel.
- Out of scope: general content DLP and unknown credential naming.
- Quality gates: direct and legacy names blocked, backend sentinel absent, safe paths remain valid.
- Residual risk: filename policy cannot detect every secret.
- Follow-up handling: none in this PR.

### F009 authority-claim-recursive-scan

- Related inventory IDs: R012
- Reported priorities: P1
- Decided priority: P1
- Merge-blocking: yes.
- Protected domain: evidence-only authority boundary.
- Contract / invariant: truthy readiness/adoption/review flags are forbidden anywhere in operational payload structure.
- Root cause: draft validators checked only the declared `authority_claims` object.
- Why this is one family: alternate top-level/nested placement bypasses the same partial scan.
- Validity analysis: valid and deterministic.
- Need-to-fix decision: yes.
- Options considered: raw substring scan; validator-local walkers; shared shape-aware exact-key walker.
- Recommended disposition: shared dict/list walker; exact keys; `True` rejected, `False`/null allowed, other scalar shapes fail closed.
- Repair scope: authority domain helper, candidate and draft validators, nested/top-level regressions.
- Out of scope: prose keyword policing.
- Quality gates: Issue draft, selected fill, and candidate approval matrices.
- Residual risk: future aliases must be added to the shared key policy.
- Follow-up handling: none in this PR.

### F010/F011 non-blocking lifecycle and resource bounds

- Related inventory IDs: R013, R014
- Reported priorities: P2, P2
- Decided priority: P2
- Merge-blocking: no.
- Protected domain: generated output safety and lower-authority review availability.
- Contract / invariant: owned outputs and bounded fallback resources.
- Root cause: independent lifecycle/resource contracts, unrelated to current P1 families.
- Validity analysis: valid material follow-up.
- Need-to-fix decision: follow-up.
- Recommended disposition: record only; no current repair unit or code mutation.
- Residual risk: mis-targeted clobber and large tree resource use remain possible.

### F012/F013 legacy adapter trust boundary

- Related inventory IDs: R015, R016
- Reported priorities: P1, P1
- Decided priority: P1
- Merge-blocking: yes.
- Contract / invariant: compatibility adapters must preserve legacy safety
  semantics and source identity before delegating to canonical runtime.
- Root cause: parsed legacy metadata and source paths were normalized away before
  the corresponding gates ran.
- Validity analysis: valid and deterministic.
- Need-to-fix decision: yes.
- Recommended disposition: explicit legacy argument gate plus pre-copy
  symlink/resolved-source validation.
- Repair scope: two compatibility wrappers, provider/dogfooding mirrors, and
  focused regressions.
- Out of scope: removal of legacy flags and content DLP.

### F014/F015 non-blocking output boundary follow-up

- Related inventory IDs: R017, R018
- Reported priorities: P2, P2
- Decided priority: P2
- Merge-blocking: no.
- Need-to-fix decision: follow-up.
- Recommended disposition: register only; do not expand the fourth blocking
  repair attempt.

### F016 candidate-review-gate-authority

- Related inventory IDs: R019
- Reported priority: P1
- Decided priority: P1
- Merge-blocking: yes.
- Contract / invariant: digest identity cannot substitute for evidence-only
  review authority.
- Root cause: pass status and digest were validated without validating the
  report's authority tuple.
- Validity analysis: valid and structurally shared with draft review gates.
- Need-to-fix decision: yes.
- Recommended disposition: shared structural authority helper across candidate,
  Issue draft, and selected-fill review gates.
- Out of scope: report signatures.

### F017 observation-timeout

- Related inventory IDs: R020
- Decided priority: platform.
- Merge-blocking: yes until a later observation obtains terminal CI evidence.
- Disposition: covered by the mandatory latest-head re-observation after repair.

## Blocking Repair Queue

Create repair units only for `P0`/`P1` families, required CI failures, or
blocking merge issues. Do not create repair units for `P2`/`P3` findings unless
they are directly and unavoidably covered by the same `P0`/`P1` root-cause fix.

| unit_id | source_batch | family_id | covered_items | decided_priority | merge_blocking | disposition | repair_unit_disc | status | implementation_plan | quality_gate | commit_evidence | re_observation_result | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| U001 | 20260710t122133z-pr-repair-batch | F001 | R001,R002 | P1 | yes | fix-now | 20260710t122142z-disc-pr-repair-unit-windows-path-boundary.md | implemented | reject drive/backslash forms before joining | focused authoring tests | pending | pending | low |
| U002 | 20260710t122133z-pr-repair-batch | F002 | R003,R004 | P1 | yes | fix-now | 20260710t122142z-01-disc-pr-repair-unit-prompt-pack-output-boundary.md | implemented | close symlink and exact-root guard gaps | focused authoring tests | pending | pending | low |
| U003 | 20260710t122133z-pr-repair-batch | F003 | R005 | required-ci | yes | fix-now | 20260710t122142z-02-disc-pr-repair-unit-planning-skill-contract.md | implemented | remove stale test expectation | wrapper test and full provider suite | pending | pending | none |
| U004 | 20260710t122133z-pr-repair-batch | F004 | R006 | P1 | yes | fix-now | 20260710t142702z-disc-pr-repair-unit-runtime-self-dirtiness.md | implemented | suppress bytecode before local runtime import | fresh consumer preflight passed | pending | pending | low |
| U005 | 20260710t122133z-pr-repair-batch | F002 | R007 | P1 | yes | fix-now | 20260710t142702z-01-disc-pr-repair-unit-lexical-symlink-ancestors.md | implemented | inspect every lexical component below trusted root alias | symlink ancestor regression passed | pending | pending | low |
| U006 | 20260710t122133z-pr-repair-batch | F007 | R010 | P1 | yes | fix-now | 20260710t160942z-disc-pr-repair-unit-review-gate-digest-binding.md | implemented | bind selected fill draft_pack_digest to review pack digest | focused and full suite passed | enclosing repair commit | pending | low |
| U007 | 20260710t122133z-pr-repair-batch | F008 | R011 | P1 | yes | fix-now | 20260710t160942z-01-disc-pr-repair-unit-backend-secret-attachments.md | implemented | central credential path policy before copy/invoke | focused and full suite passed | enclosing repair commit | pending | medium |
| U008 | 20260710t122133z-pr-repair-batch | F009 | R012 | P1 | yes | fix-now | 20260710t160943z-disc-pr-repair-unit-recursive-authority-claims.md | implemented | shared shape-aware recursive authority scan | focused and full suite passed | enclosing repair commit | pending | low |
| U009 | 20260710t122133z-pr-repair-batch | F012 | R015 | P1 | yes | fix-now | 20260710t172152z-disc-pr-repair-unit-compatibility-review-wrapper.md | implemented | honor legacy preflight/input-kind/extraction gates | focused and full suite passed | enclosing final repair commit | pending | low |
| U010 | 20260710t122133z-pr-repair-batch | F013 | R016 | P1 | yes | fix-now | 20260710t172152z-01-disc-pr-repair-unit-legacy-attachment-symlink.md | implemented | reject source symlink laundering before copy | focused and full suite passed | enclosing final repair commit | pending | medium |
| U011 | 20260710t122133z-pr-repair-batch | F016 | R019 | P1 | yes | fix-now | 20260710t172152z-02-disc-pr-repair-unit-candidate-review-authority.md | implemented | require shared review authority tuple | focused and full suite passed | enclosing final repair commit | pending | low |

## Non-Blocking Follow-up Register

Use this section only when a blocking repair commit is already being made and
`P2`/`P3` findings can be recorded without causing an additional record-only
push.

If the latest observation has only `P2`/`P3` findings and no blockers, do not
update this file. Put those findings in the terminal merge-prepared report
instead.

| followup_id | family_id | related_items | priority | rationale_for_no_action | residual_risk | suggested_followup_target |
| --- | --- | --- | --- | --- | --- | --- |
| NB001 | F005 | R008 | P2 | non-blocking read-side gap; not unavoidable for P1 write fix | symlinked prompt-pack ancestor may pass validation | future authoring path-boundary hardening |
| NB002 | F006 | R009 | P2 | non-blocking tree fallback gap; not unavoidable for P1 write fix | symlinked tree ancestor may pass review | future authoring path-boundary hardening |
| NB003 | F010 | R013 | P2 | output ownership is independent of current P1 fixes | existing unrelated pack filenames may be overwritten | future prompt-pack output ownership |
| NB004 | F011 | R014 | P2 | lower-authority resource cap is independent of current P1 fixes | large extracted trees may consume excess resources | future tree review bounds |
| NB005 | F014 | R017 | P2 | stage target normalization is independent of current P1 fixes | broken stage symlink may raise FileExistsError | future stage output boundary hardening |
| NB006 | F015 | R018 | P2 | managed output completeness is independent of current P1 fixes | prompt pack may target spec-dock/system | future managed-root policy |

## Quality Gate Plan

Define family-level gates, not comment-level checks.

| gate_id | family_id | command_or_check | expected_result | covers_items | required_before_push |
| --- | --- | --- | --- | --- | --- |
| G001 | F001 | targeted authoring path tests | unsafe Windows forms are rejected: pass | R001,R002 | yes |
| G002 | F002 | targeted prepare output tests | broken symlink and initiatives root are rejected: pass | R003,R004 | yes |
| G003 | F003 | test_scaffold_docs_point_to_runtime_commands_and_rules_docs | pass without retired reference | R005 | yes |
| G004 | all | uv run pytest | 2272 passed, 75 skipped | R001-R005 | yes |
| G005 | all | ./scripts/static_analysis/run.sh | ruff, format, mypy pass | R001-R005 | yes |
| G006 | all | ./spec-dock/scripts/spec-dock validate | ok, nodes=203 | R001-R005 | yes |
| G007 | F004 | fresh consumer preflight without PYTHONDONTWRITEBYTECODE | pass, no bytecode, clean git status: pass | R006 | yes |
| G008 | F002 | existing output below symlinked parent | rejected with no generated files: pass | R007 | yes |
| G009 | F002,F004 | uv run pytest | 2274 passed, 75 skipped | R006,R007 | yes |
| G010 | F002,F004 | ./scripts/static_analysis/run.sh | ruff, format, mypy pass | R006,R007 | yes |
| G011 | F002,F004 | provider/dogfooding cmp | exact match | R006,R007 | yes |
| G012 | all | ./spec-dock/scripts/spec-dock validate | ok, nodes=203 | R001-R009 | yes |
| G013 | F007 | selected fill digest binding matrix | exact report pack required; stale/blocked otherwise | R010 | yes |
| G014 | F008 | direct and legacy credential attachment matrix | blocked before backend sentinel | R011 | yes |
| G015 | F009 | Issue draft/selected fill/candidate authority matrices | top-level/nested truthy flags rejected | R012 | yes |
| G016 | F007-F009 | uv run pytest | 2286 passed, 75 skipped | R010-R012 | yes |
| G017 | F007-F009 | ./scripts/static_analysis/run.sh | ruff, format, mypy pass | R010-R012 | yes |
| G018 | F007-F009 | provider/dogfooding cmp and spec-dock validate | exact match; ok, nodes=203 | R010-R012 | yes |
| G019 | F012 | legacy review compatibility matrix | stale/blocked preflight cannot pass; extraction only after pass | R015 | yes |
| G020 | F013 | direct/ancestor symlink backend sentinel matrix | rejected before backend execution | R016 | yes |
| G021 | F016 | candidate/draft review authority matrix | malformed tuple rejected before gate pass | R019 | yes |
| G022 | F012,F013,F016 | uv run pytest | full provider suite passes | R015,R016,R019 | yes |
| G023 | F012,F013,F016 | static analysis, mirror cmp, spec-dock validate | all pass | R015,R016,R019 | yes |
| G024 | F012,F013,F016 | uv run pytest | 2294 passed, 75 skipped | R015,R016,R019 | yes |
| G025 | F012,F013,F016 | tests/cli_runtime/test_authoring.py | 378 passed, 1 skipped | R015,R016,R019 | yes |

## Re-observation Plan

- Latest head before repair: 8046bc3e7f2d8817f9c6680f355e271707039172
- Expected head after repair:
- Re-observation command: wait_pr_observation.sh with the repaired head SHA
- Trigger mode: post-once
- Resume trigger comment id:
- Resume trigger created_at:
- New trigger approved: yes, required for the new pushed head
- Re-observation required because: all blocking findings and required CI must be checked on the repaired head
- Re-observation skipped because:

## Loop Control

| iteration | head_sha | observation_status | family_id | action_taken | fix_commit | reappeared_after_fix | next_action |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 8c66118743ab55b3032d95eccd6eebf999fb06c2 | human_gate | F001-F003 | repair implemented and validated | pending | no | commit, push, re-observe |
| 2 | 8046bc3e7f2d8817f9c6680f355e271707039172 | human_gate | F002,F004 | human approved invariant-based second strategy; Deep Consultant analysis adopted; implementation validated | pending | F002=yes | commit, push, re-observe |
| 3 | c179811ee052467b87867275da3188fe71dd6f73 | timeout | F007-F009 | Deep Consultant second analysis adopted; three family-scoped repairs implemented and locally validated | 6cb24d78105bb7f4a7d308a30bea6ac917dfe029 | no | pushed and re-observed |
| 4 | 6cb24d78105bb7f4a7d308a30bea6ac917dfe029 | timeout | F012,F013,F016,F017 | Deep Consultant third analysis adopted; final bounded P1 repair implemented and locally validated | pending | F013,F016 share prior trust-boundary families | commit, push, re-observe |

## Deep Consultant Synthesis

- Role: `deep-consultant`, read-only, GPT-5.6 Sol max reasoning.
- Adopted analysis:
  - treat bytecode dirtiness as observer side effect, not a git-status parsing problem;
  - suppress bytecode in the installed launcher before local imports;
  - replace existence-gated output traversal with a complete lexical component check;
  - keep P2 read-side gaps outside this P1 repair and record them as follow-up;
  - no additional deterministic write-escape P1 was found in the changed surface.
- Validation refinement:
  - the first implementation exposed macOS `/var -> /private/var` as a system-level alias;
  - root-level symlinks require administrative control and are trusted, matching the existing backend output guard;
  - every component below that root-level boundary remains fail-closed and is never skipped because it exists.
- Rejected / deferred:
  - gitignore and status filtering hide rather than eliminate the observer side effect;
  - broad shared-helper rollout would unnecessarily turn P2 findings into current repair scope.
- Residual audit targets: candidate/adoption input ancestors, legacy helpers, TOCTOU swaps, hardlinks, Windows junctions/reparse points.

### Second Analysis

- Shared meta-cause: trust-boundary validators accepted partial declarations instead of validating evidence identity, outbound filename policy, and authority semantics across the complete operational payload.
- Unit boundary decision: keep F007, F008, and F009 separate because protected assets, rollback boundaries, and tests differ.
- Adopted existing precedents:
  - Issue draft `draft_pack_digest` and candidate pack digest binding;
  - pack prepare's credential path policy, promoted to domain and applied before legacy copy/backend invocation;
  - candidate approval's recursive exact-key authority scan, promoted to a shape-aware shared helper.
- P2 decision: F010 and F011 are independent lifecycle/resource concerns and remain register-only.
- Observation timeout: resume metadata was preserved for head `c179811e`; no resume is needed because these P1 repairs require a new head.

### Third Analysis

- Legacy wrapper findings share an adapter trust-boundary meta-cause but remain
  separate units because review parity and attachment disclosure have distinct
  rollback and test surfaces.
- The attachment finding extends the earlier filename-only F008 repair to source
  path identity; the authority finding extends F007 from pack identity to report
  authority. The user's standing request to repair all merge blockers authorizes
  this final bounded strategy.
- External regular-file compatibility is preserved; only direct symlinks and
  repo-local lexical symlink escapes are rejected.
- Review authority validation is shared across candidate, Issue draft, and
  selected-fill gates to avoid another partial-gate recurrence.
- F014 and F015 remain P2 register-only, and F017 is satisfied only by fresh
  latest-head observation.

Stop at a human gate when the same `root_cause_family` reappears after a repair
commit, unless a human explicitly approves a new strategy.

## Fifth Repair Iteration (Deep Consultant)

### Raw Intake Inventory

| id | reported_priority | failure_class | summary | status |
|---|---|---|---|---|
| R021 | P1 | review_feedback:default-source-path-symlink-gap | 既定source pathsがblocker検査に渡らずsymlinkを見逃す | implemented |
| R022 | P1 | review_feedback:pack-review-provenance-state-gap | pack reviewがprovenance状態間整合性を検証しない | implemented |
| R023 | P1 | review_feedback:backend-stream-sensitive-payload | backend stdout/stderr本文がsummaryへ永続化される | implemented |
| R024 | P1 | review_feedback:review-report-symlink-gate | review証跡入力がleaf/ancestor symlinkを受理する | implemented |

### Root Cause Families

- `authoring-pack.effective-input-boundary`: R021, R024。検証した入力集合・字句pathと後段が利用する実効入力が一致していない。
- `authoring-pack.semantic-state-contract`: R022。field型検証だけで複数fieldが構成する許容状態を検証していない。
- `authoring-pack.sensitive-output-retention`: R023。信頼できないsubprocess本文をheuristic redaction後にdurable evidenceへ保持している。

### Deep Consultant Decision

- 4件はいずれもvalid、P1、merge-blocking、fix-now。
- 個別条件追加ではなく、実効入力の単一化、共有状態機械、stream非永続化、入力証跡identity検証を採用する。
- 修正ユニット: U012、U013、U014、U015。
- ユーザー承認により修正回数上限を撤廃し、最新HEADがmerge-preparedになるまでDeep Consultant分析を伴う再観測ループを継続する。

## Terminal Non-Blocking Report Boundary
## Sixth Repair Iteration (Deep Consultant)

| id | reported_priority | failure_class | root_cause_family | disposition | status |
|---|---|---|---|---|---|
| R025 | CI | check_failure:provider-tests | provider-ci.final-static-gate-omission | fix-now | implemented |

- Provider CIの`make lint`でruff format 3件とmypy 1件が失敗した。
- Deep Consultantは環境差やflakeではなく、最終HEADへCI同等static gateを実行しなかったプロセス漏れと判定した。
- U016で機械format、変数意味分離、provider/dogfood同期、`make lint`再検証を行う。

## Terminal Non-Blocking Report Boundary

When final re-observation contains only `P2`/`P3` findings:

- Do not update this batch solely to record them.
- Do not push a record-only commit.
- Do not trigger another review.
- Report those findings in the final response grouped by `root_cause_family`.
- State `branch mutation: no`.
- State `ci rerun avoided: yes`.
- State `review-clean: no`.
- State `merge-prepared: yes` if all blocking predicates are satisfied.

## Stop Conditions

Stop at a human gate when any condition applies:

- Any blocking inventory item remains `untriaged`.
- Any unresolved blocking `needs-human` item remains.
- A `P0`/`P1` `fix-now` repair unit is incomplete or repeatedly fails.
- The same `root_cause_family` reappears after a repair commit.
- Observation output is not for the latest head SHA.
- Timeout or observation limitation lacks resume metadata.
- Resume would cross the recorded trigger boundary.
- A new trigger would be required but has not been approved.
- Scope expansion, requirement expansion, breaking change, migration, secret,
  deployment setting, permission/auth, external/flaky, or ambiguous review
  intent is involved.
- Loop limits for the same root-cause family or total repair attempts are
  reached.
- GitHub branch protection requires conversation resolution for unresolved
  `P2`/`P3` threads; this is a platform human gate, not a code repair target.

## Merge-Prepared Gate

Report `merge-prepared: yes` only when all conditions are true:

- PR is open.
- Latest observation is complete and matches the latest head SHA.
- No observed required GitHub Actions CI failure remains.
- External/non-Actions check state has either been confirmed outside PR
  observation or is recorded as a human gate/residual risk.
- No unresolved `P0`/`P1` review feedback remains.
- Remaining `P2`/`P3` findings, if any, are grouped and reported as
  non-blocking terminal findings or recorded here because a blocking repair
  commit was already required.
- No visible merge conflict or equivalent semantic merge blocker remains.
- No blocking `untriaged` inventory item remains.
- No unresolved blocking `needs-human` item remains.
- No blocking item has an incomplete `fix-now` repair unit.
- Every repo-persistent `follow-up`, `no-action`, `covered-by`, `duplicate`, or
  `false-positive` item has rationale and residual risk where relevant.
- Observation limitation handling, resume metadata, trigger boundary, and new
  trigger approval status are recorded.
- Review-thread unresolved state is known, or unresolved-thread limitations are
  disclosed. If platform conversation resolution is required, stop at a human
  gate instead of claiming GitHub mergeability.
- `review-clean` is reported separately from `merge-prepared`.
- `github-mergeable` is not claimed unless platform requirements were confirmed.
