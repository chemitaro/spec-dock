# iss-00290 negative probe dogfood summary

Authority:

- authority: evidence_only
- adoption_status: unreviewed
- bundle_generation_not_promotion: true
- canonical_written: false
- assurance_mutated: false
- reviewer_pass_claimed: false

Trace:

- issue: iss-00290
- parent epic: epic-00283
- requirements: E-RQ-005, E-RQ-008, E-RQ-010
- acceptance: E-AC-002, E-AC-004, E-AC-005, E-AC-011

| case | validator | expected | observed | returncode | adoption eligible | evidence |
|---|---|---|---|---:|---|---|
| preflight-source-hash-mismatch | prepare_chatgpt_authoring_pack.py | stale | stale | 3 | false | preflight-source-hash-mismatch/diagnostics.json |
| selected-profile-drift | validate_selected_skeleton_fill.py | stale | stale | 3 | false | selected-profile-drift/validation/selected-skeleton-fill-validation-report.json |
| candidate-profile-mismatch | validate_selected_skeleton_fill.py | stale | stale | 3 | false | candidate-profile-mismatch/validation/selected-skeleton-fill-validation-report.json |
| unsafe-authority-claim | validate_selected_skeleton_fill.py | rejected | rejected | 4 | false | unsafe-authority-claim/validation/selected-skeleton-fill-validation-report.json |
| pack-digest-mismatch | validate_selected_skeleton_fill.py | stale | stale | 3 | false | pack-digest-mismatch/validation/selected-skeleton-fill-validation-report.json |
| stage-attempt-stale-review | stage_chatgpt_authoring_pack.py | stale | stale | 3 | false | stage-attempt-stale-review-command-check/command-result.json |

Overall result: pass.

All cases remain evidence-only. None of these outputs may be treated as reviewer pass, canonical adoption, `.assurance.json` mutation, or staged canonical content.

Stage attempt trace note: for the stage-block case, `stage-attempt-stale-review-command-check/staging-report.json#/review/trace` is the `iss-00290` evidence trace. The top-level staging report trace is the stage helper contract trace and is not used as `iss-00290` evidence authority.
