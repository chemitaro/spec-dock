---
kind: chatgpt-use-planning-summary
issue: iss-00288
epic: epic-00283
source: ChatGPT Use / GPT-5.5 Pro Extended
session: specdock-iss-00288-planning
created_at: 2026-07-07T00:08:51Z
authority: evidence_only
adoption_status: unreviewed
bundle_generation_not_promotion: true
---

# ChatGPT Use planning summary for iss-00288

## 結論

ChatGPT Use は、current branch を GitHub connector で参照できた前提で、`iss-00288` の実装は既存 ZIP safety / generic review pipeline を触らず、candidate-only Issue 候補専用の dogfood validator を 1 組追加する最小案がよいと判断した。

推奨追加ファイル:

- `scripts/authoring-pack/authoring_pack_issue_candidates.py`
- `scripts/authoring-pack/validate_issue_candidates.py`
- `tests/manual_tests/test_validate_issue_candidates.py`
- `tests/fixtures/authoring_pack/valid/issue-candidates/`
- `tests/fixtures/authoring_pack/invalid/issue-candidates-*/`
- `scripts/authoring-pack/README.md` の usage 追記

canonical `requirement.md` / `design.md` / `plan.md` への material amendment は不要。既存 docs は、candidate-only ZIP fixture、validation report、Issue 比較 summary、profile recommendation advisory-only、正本上書き禁止、fresh reviewer gate 必須、allowed path、negative fixture をすでに要求している。

## 命名判断

`authoring_pack_issue_candidates.py` は、既存の `authoring_pack_review.py`、`authoring_pack_stage.py`、`authoring_pack_selected_skeleton_fill.py` と同じ「authoring_pack + 対象 noun」の並びで、人間が「authoring pack 内の Issue candidates を扱う module」と読みやすい。

`validate_issue_candidates.py` は、既存 CLI wrapper の `validate_selected_skeleton_fill.py` と同じ verb-first style で、dogfood helper として分かりやすい。public SpecDock CLI ではない。

## 推奨処理順

```text
prepare_chatgpt_authoring_pack.py
  -> review_chatgpt_authoring_pack.py
  -> validate_issue_candidates.py
  -> report.md / artifacts へ sanitized evidence を手動反映
```

`review_chatgpt_authoring_pack.py` は generic ZIP safety / metadata / unsafe claim / stale source gate を担い、新 validator は `review_report.status == "pass"` のときだけ candidate-specific validation に進む。

## 推奨 input schema

```text
specdock-authoring-pack/
  manifest.json
  provenance.json
  source-manifest.json
  stale-if.json
  adoption/adoption-map.json
  candidates/issues/index.json
  candidates/issues/<candidate_id>/candidate.json
  candidates/issues/<candidate_id>/draft-requirement.md
  candidates/issues/<candidate_id>/draft-design-brief.md
  candidates/issues/<candidate_id>/draft-plan-brief.md
  candidates/issues/<candidate_id>/profile.json
  reviewer-focus/issue-candidates.md
```

`draft-design-brief.md` と `draft-plan-brief.md` を推奨。canonical に見える `design.md` / `plan.md` より、profile-specific canonical template body を出さない AC-006 に合う。

`index.json` と `candidate.json` は `authority: evidence_only`、`adoption_status: unreviewed`、`bundle_generation_not_promotion: true` を持つ。`candidate.json` には `parent_trace`、`scope`、`non_scope`、`dependencies`、`boundary_metadata`、`files` を含める。

`profile.json` は `profile_recommendation` を advisory-only とし、`authorized_profile: null`、`profile_authority: local_assurance_only`、`assurance_mutated: false` を固定する。`authorized_profile` が null 以外なら reject。

## 推奨 output schema

`validate_issue_candidates.py` は次を出す。

```text
issue-candidate-validation-report.json
issue-candidate-comparison-summary.json
issue-candidate-comparison-summary.md
issue-candidate-validation-summary.md
.specdock-issue-candidates-validation
```

出力 root は常に `authority: evidence_only`、`adoption_status: unreviewed`、`bundle_generation_not_promotion: true`、`canonical_written: false`、`assurance_mutated: false` を持つ。

comparison summary には candidate count、parent trace status、profile recommendation profile、dependencies、scope / non-scope counts、rejected / blocking reason、duplicate title / scope warnings、`canonical_written: false` を含める。

## status taxonomy

- `pass`: review report pass、digest match、candidate schema valid、parent trace valid、boundary metadata exact、profile recommendation advisory-only、selected skeleton / profile-specific / all-profile output なし。
- `fail`: malformed JSON、empty candidates array、missing `scope` / `non_scope` / `dependencies`、invalid candidate id などの non-safety schema error。
- `blocked`: required evidence cannot be observed、missing parent trace、missing boundary metadata、unreadable required candidate files。
- `stale`: review report digest mismatch、expected trace args と pack trace の不一致。
- `rejected`: `authority: canonical`、`adoption_status: adopted`、non-null `authorized_profile`、`.assurance.json` mutation claim、reviewer pass claim、selected skeleton fill、profile-specific canonical template body、all-profile variants、secret / host path / raw transcript。
- `deferred`: selected-skeleton fill / staging pack など candidate-only ではない later-stage pack。
- `unreviewed`: artifact adoption state only。execution status として扱わない。

missing parent trace と missing boundary metadata は `blocked` 推奨。明示的に危険な boundary value は `rejected` 推奨。

## focused tests

- valid pack で report と comparison summary が作られ、`canonical_written=false`、`assurance_mutated=false`、`adoption_status=unreviewed` になる。
- non-pass review report は同じ status を伝播し、candidate validation pass を主張しない。
- pack digest mismatch は `stale`。
- missing parent trace は `blocked`。
- missing boundary metadata は `blocked`。
- unsafe boundary value は `rejected`。
- `profile.json.authorized_profile` が null 以外なら `rejected`。
- profile recommendation が advisory-only でなければ `rejected`。
- `selected-skeleton-fill/section-fills.json` や `section_fills` key は `rejected`。
- `profiles/<profile>/`、`all-profiles/`、`template_sha256`、`skeleton_sha256`、`section_inventory_sha256` は profile-specific body / selected skeleton 混入として `rejected`。
- missing `scope` / `dependencies` / `non_scope` は `fail`。
- duplicate title / scope は reject せず comparison warning。
- output directory ownership guard / redaction。
- forbidden authority claim in markdown は sanitized `rejected`。

## reviewer focus

Spec review:

- Dogfood A に閉じているか。
- candidate output が canonical adoption、reviewer pass、`.assurance.json` mutation、local profile authority を示唆していないか。

Code review:

- helper が dogfood-only で、runtime / public CLI に昇格していないか。
- review pass evidence と digest match を前提に candidate-specific validation のみを行っているか。
- unsafe content を echo していないか。

QA review:

- fail-closed behavior。
- unsafe / incomplete candidate は adoption-ineligible。
- canonical docs overwrite なし、`.assurance.json` mutation なし、evidence-only boundary 維持。

## リスク

profile-specific canonical template body の検出は、純粋な全文スキャンだけでは brittle。最小で堅牢な方法は、高シグナルの path / metadata を reject すること。

混同リスクとして comparison summary が adoption と読まれる可能性があるため、全 output root に evidence-only boundary と `canonical_written: false` を固定する。

schema をこの Epic に過剰固定しないため、CLI には `--expected-parent-epic`、`--expected-requirement`、`--expected-acceptance` を持たせる。ただしこの Issue の output trace は `iss-00288` / E-RQ-011 / E-AC-007 / E-AC-011 を記録する。
