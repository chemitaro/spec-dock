---
種別: 実装報告書（Issue）
ID: "iss-00257"
タイトル: "Severity Aware Codex PR Review Policy And Non Blocking Repair Loop Hardening"
関連GitHub: ["#257"]
状態: "reviewed"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00224", "init-local-00003"]
---

# iss-00257 Severity Aware Codex PR Review Policy And Non Blocking Repair Loop Hardening — 実装報告

この report は、Issue Planning / clarification / implementation / verification / review の観測証跡台帳である。要件定義書、設計書、実装計画書の段階的 authoring、S10-S90 の実装・検証、fresh reviewer gate、commit / PR 前の残状態を記録する。

## Spec Interpretation / Decision Ledger

| ID | Status | Type | Raised By | Gap | Options | Decision | Rationale | Disposition | Evidence | Follow-up |
|---|---|---|---|---|---|---|---|---|---|---|
| D-001 | resolved | scope | user | 親 Epic には旧 P2 promotion 方針があるが、この Issue では新方針を採用する必要がある | 親 docs も更新 / Issue 内限定 override | Issue 内限定で `P2 + protected_domain + machine_evidence` promotion を廃止し、親 Epic docs は編集しない | 親 Epic は別 worktree で作業中というユーザー制約がある | applied | `discussions/20260701t022257z-interview-parent-epic-p2-promotion-policy.md`, `requirement.md` | none |
| D-002 | resolved | implementation | user | bundle は `root_cause_family` を強く示すが現行 runtime は `blocker_fingerprint` contract | runtime first-class / docs-only / optional metadata | Option B: docs / LLM judgement / operational triage vocabulary に限定する | runtime parser と stalled semantics を広げず、主目的の P2/P3 non-blocking 化に集中する | applied | `discussions/20260701t023858z-interview-root-cause-family-runtime-scope.md`, `design.md` | none |
| D-003 | resolved | operation | orchestrator | Issue Planning 導入初回運用で、workflow の違和感を残す必要がある | product requirement に混ぜる / discussion と report に分離 | Dogfooding note を discussion artifact に分離し、採用分だけ report に反映する | 本筋の PR review policy 要件と workflow 改善観察を混ぜない | applied | `discussions/20260701t025116z-research-issue-planning-dogfooding-notes.md` | Possible future workflow polish, non-blocking |
| D-004 | resolved | operation | orchestrator | 誤って no-op spec-reviewer を起動した | 採用 / 不採用 | no-op reviewer は workflow evidence として不採用 | 対象 artifact をレビューしていないため | rejected | subagent `019f1ba9-9921-7212-83a5-e26b782610c3` | none |
| D-005 | resolved | test-strategy | spec-reviewer | Plan の CLOS-004 が terminal P2/P3-only no-mutation 境界を具体的に閉じていなかった | そのまま / CLOS と step を追加 | `CLOS-004A` と `S40` を追加し、batch persistence / commit-push / re-review / repair loop の証跡を要求 | Plan phase review P1 finding | applied | plan review `019f1baf-8f38-7833-bca6-21c4a48fe275`, `plan.md` | none |
| D-006 | resolved | test-strategy | spec-reviewer | Parent Epic 非編集 evidence が symlink path だけだと弱い | symlink path / real parent docs path | 実体 parent Epic docs path を plan の検証コマンドと report evidence requirement に明示 | Plan re-review P2 finding | applied | plan re-review `019f1bb1-e3c3-7b70-a79a-94be1be82475`, `plan.md` | none |
| D-007 | resolved | operation | user | SpecDock workflow が必要とする named sub-agent / reviewer を追加許可待ちで省略する判断が発生した | 現状維持 / runtime consent schema / instruction hardening | SpecDock workflow invocation を workflow-scoped named role authorization として instruction / docs / skill に明文化する | SpecDock は workflow-defined named roles を orchestrator が自律的に使い分ける前提であり、複雑な runtime consent schema は不要 | applied | supplemental user instruction, `requirement.md`, `design.md`, `plan.md` | none |

## Evidence Adoption Ledger

| ID | adoption_status | source | target | rationale | evidence | next_action |
|---|---|---|---|---|---|---|
| EAL-001 | adopted | research | `requirement.md`, `design.md`, `plan.md` | 添付 bundle と現行 repo 差分、tests、edge cases を突き合わせ済み | `discussions/20260701t023648z-research-pr-review-policy-clarification-research.md` | none |
| EAL-002 | adopted | discussion / user answer | `requirement.md`, `design.md`, `plan.md` | Issue-local P2 promotion 廃止と親 Epic docs 非編集が明確化された | `discussions/20260701t022257z-interview-parent-epic-p2-promotion-policy.md` | none |
| EAL-003 | adopted | discussion / user answer | `requirement.md`, `design.md`, `plan.md` | `root_cause_family` を runtime contract にしない範囲が確定した | `discussions/20260701t023858z-interview-root-cause-family-runtime-scope.md` | none |
| EAL-004 | adopted | command evidence | design.md and plan.md and report.md | assurance classify and compose produced standard profile planning artifacts | command evidence recorded in Implementation Session Log | none |
| EAL-005 | adopted | research / dogfooding | this report | Issue Planning workflow の初回運用観察を正本 report に反映した | `discussions/20260701t025116z-research-issue-planning-dogfooding-notes.md` | Track future polish outside this Issue if needed |
| EAL-006 | adopted | reviewer | `requirement.md` | Requirement phase pass により design phase へ進める | spec-reviewer `019f1ba9-6a28-7890-8dcc-6e17cca335b2` | none |
| EAL-007 | adopted | reviewer | `design.md` | Design phase pass により plan phase へ進める | spec-reviewer `019f1bac-2f1c-7720-bf8b-4e95f443562b` | none |
| EAL-008 | partially_adopted | reviewer | `plan.md` | Initial plan review failed with one P1 finding; finding was fixed and re-reviewed | spec-reviewer `019f1baf-8f38-7833-bca6-21c4a48fe275` | none |
| EAL-009 | adopted | reviewer | `plan.md` | Re-review passed; P2 evidence-path correction was incorporated | spec-reviewer `019f1bb1-e3c3-7b70-a79a-94be1be82475` | none |
| EAL-010 | rejected | reviewer | none | Accidental no-op reviewer reviewed no artifacts and is not valid workflow evidence | spec-reviewer `019f1ba9-9921-7212-83a5-e26b782610c3` | none |
| EAL-011 | adopted | user instruction | requirement.md and design.md and plan.md | SpecDock workflow invocation authorization hardening was added to planning scope | supplemental user instruction in current session | fresh spec-reviewer after scope update |
| EAL-012 | adopted | reviewer | requirement.md and design.md and plan.md and report.md | Supplemental authorization scope re-review passed after P1/P2 fixes | spec-reviewer `019f1bc3-0837-73c2-841d-6c935120e3a7` | none |

## Objective Alignment Ledger

| Target | Primary objective evidence | Secondary requirement evidence | Inversion risk | Reviewer verdict |
|---|---|---|---|---|
| Severity-aware PR review policy | `requirement.md` defines P0/P1 blocking, P2/P3 reportable non-blocking, and no P2 promotion | Dogfooding notes and `root_cause_family` docs-only vocabulary are captured but scoped | low | pass |

## Spec Authoring Gate

| Phase | Investigated facts | Open questions / answers | Adoption decision | Reviewer verdict | Blocking | Promotion / next_action |
|---|---|---|---|---|---|---|
| requirement | ZIP bundle, current code/tests/assets, parent Epic constraint, discussions, supplemental authorization scope | Parent docs do not edit; root_cause_family Option B docs-only; workflow-scoped named role authorization | adopted into requirement artifact | passed | no | promote |
| design | Requirement pass, current runtime and asset structure, mirror parity tests, authorization docs surfaces | none | adopted into design artifact | passed | no | promote |
| plan | Design pass, closure IDs, target files, focused tests, forbidden changes, authorization hardening step | Initial no-mutation verification gap fixed via CLOS-004A and S40; CLOS-010 added | adopted into plan artifact | passed | no | promote |

## Delegated Draft Evidence

| Role | Scope | Draft path | Source paths | Intended targets | Adoption status | Reflected to | Diff guard result | Integration result | Rejected portions | Blockers | Reviewer result | Promotion decision |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| N/A | iss-00257 | N/A | N/A | N/A | not used | [] | not_run | manual authoring by main orchestrator | N/A | none | passed | promote |

## Grade Specialist Evidence Gate

| Profile | Required or fallback | Usage | Evidence | Reviewer verdict | Readiness |
|---|---|---|---|---|---|
| standard | manual authoring fallback | not used | manual-authored canonical docs reviewed by fresh spec-reviewer passes | passed | ready |

## Reviewer Gate Status

| Step | Gate | Reviewer role | Freshness | State | Risk acceptance | Completion decision | Notes |
|---|---|---|---|---|---|---|---|
| requirement | requirement authoring review | spec-reviewer | fresh | passed | no | promote | `019f1ba9-6a28-7890-8dcc-6e17cca335b2` |
| design | design authoring review | spec-reviewer | fresh | passed | no | promote | `019f1bac-2f1c-7720-bf8b-4e95f443562b` |
| plan | plan authoring review | spec-reviewer | fresh | passed | no | promote | P1 fixed via `CLOS-004A` and `S40`; pass from `019f1bb1-e3c3-7b70-a79a-94be1be82475` |
| ignored | accidental no-op review | spec-reviewer | stale | rejected | no | no_action | `019f1ba9-9921-7212-83a5-e26b782610c3`; no artifacts reviewed |

## Implementation Session Log

### セッションログ（2026-07-01）

#### 対象

- Phase: issue planning authoring redo
- Closures: CLOS-009 authoring evidence

#### 実施内容

- User instruction に従い、先行して一括具体化した canonical docs を template 状態へ戻した。
- Requirement のみを具体化し、spec-reviewer pass を取得した。
- `assurance classify --stage requirement` と `assurance compose --artifact all` を実行した。
- Design のみを具体化し、spec-reviewer pass を取得した。
- Plan を具体化し、spec-reviewer review を実施した。
- Plan review P1 finding に従い、terminal P2/P3-only no-mutation 境界を `CLOS-004A` / `S40` として追加した。
- Plan re-review pass 後、P2 finding に従い parent Epic docs 実体 path の diff evidence を plan に明記した。
- User supplemental instruction に従い、SpecDock workflow-scoped named role authorization hardening を requirement/design/plan scope に追加した。

#### 実行コマンド / 結果

```bash
./spec-dock/scripts/spec-dock guidance issue-planning
# requirement-capture / requirement-scaffold を確認

./spec-dock/scripts/spec-dock assurance classify --stage requirement
# assurance classify: ok
# authorized_profile: standard

./spec-dock/scripts/spec-dock assurance compose --artifact all
# assurance compose: ok

./spec-dock/scripts/spec-dock validate
# spec-dock: ok (validate)
```

#### Test / Review Evidence

| Step | Evidence | Result | Notes |
|---|---|---|---|
| requirement authoring | spec-reviewer `019f1ba9-6a28-7890-8dcc-6e17cca335b2` | pass | no findings |
| design authoring | spec-reviewer `019f1bac-2f1c-7720-bf8b-4e95f443562b` | pass | no findings |
| plan authoring | spec-reviewer `019f1baf-8f38-7833-bca6-21c4a48fe275` | fail | P1 no-mutation verification gap |
| plan re-review | spec-reviewer `019f1bb1-e3c3-7b70-a79a-94be1be82475` | pass | P1 fixed; P2 evidence path incorporated |
| final scope update review | spec-reviewer `019f1bc3-0837-73c2-841d-6c935120e3a7` | pass | supplemental authorization scope re-review passed |

#### 変更したファイル

- `spec-dock/active/issue/requirement.md` - Requirement concrete draft, reviewer-passed.
- `spec-dock/active/issue/design.md` - Design concrete draft, reviewer-passed.
- `spec-dock/active/issue/plan.md` - Plan concrete draft, reviewer-passed after one fix.
- `spec-dock/active/issue/report.md` - Authoring and reviewer evidence ledger.
- `spec-dock/active/issue/discussions/20260701t023858z-interview-root-cause-family-runtime-scope.md` - User answer captured.
- `spec-dock/active/issue/discussions/20260701t025116z-research-issue-planning-dogfooding-notes.md` - Dogfooding observations.

### セッションログ（2026-07-01 / issue execution）

#### S10 Markdown policy assets

| Evidence | Result | Notes |
|---|---|---|
| doc-writer `019f1bda-2d9b-76a2-8f75-57983b1412c7` | complete | Updated provider and dogfooding PR review / merge-preparer / repair-batch policy text for P0/P1 blocking and P2/P3 reportable-but-non-blocking handling. |
| `cmp -s` provider/dogfooding mirror pairs | pass | `codex-review-instructions.md`, `github-pr-merge-preparer/SKILL.md`, and `pr-repair-batch.md` mirror pairs matched. |
| `rg -n "P0/P1|P2/P3|reportable but non-blocking|non-blocking|protected domain|machine evidence|root_cause_family|re-review|push|repair batch|persistent" ...` | pass | Expected severity and no-mutation boundary language was present in the edited policy assets. |
| `git diff --check -- <S10 files>` | pass | No whitespace errors. |
| `git diff -- spec-dock/initiatives/.../epic-00224-*/{requirement.md,design.md,plan.md,report.md}` | pass | Parent Epic docs remained unchanged. |
| `uv run pytest tests/unit/infra/test_init_update.py -k "issue_176_s05b or issue_75_pr_monitor_assets_retired_and_observation_scaffold_present or issue_75_pr_workflow_guidance_uses_observation_without_pr_monitor_routing" -q --tb=short` | fail | Expected Red before S30: `test_issue_176_s05b...` still asserted legacy phrase `merge-blocking reviewer` in the installed instruction text. The S30 test-update step owns this stale expectation. |

#### S20 Runtime blocker policy

| Evidence | Result | Notes |
|---|---|---|
| dev-coder `019f1bdf-fa93-7f43-ac4f-7000c9e68bfa` | complete | Removed the `P2 + protected_domain + machine_evidence -> promoted_blocker` branch from provider and dogfooding `pr_review_snapshot.py`. |
| `git diff -- .agents/.../pr_review_snapshot.py src/spec_dock/assets/install_root/.../pr_review_snapshot.py` | pass | Diff was limited to deleting the promotion branch and changing `blocker_policy_blockers` to `disposition == "blocker"`. |
| `python -m py_compile .agents/skills/github-pr-observation/scripts/lib/pr_review_snapshot.py src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_review_snapshot.py` | pass | Worker-reported syntax check passed for both mirror files. |
| `cmp -s .agents/skills/github-pr-observation/scripts/lib/pr_review_snapshot.py src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_review_snapshot.py` | pass | Worker-reported mirror parity passed. |
| `uv run pytest tests/unit/infra/test_init_update.py -k "issue_232" -q --tb=short` | fail | Expected Red before S30: 1 failed / 20 passed. The remaining failure was the old `promoted_blocker` expectation in `test_issue_232_review_collector_promotes_protected_p2_with_machine_evidence`. |

#### S30 Test updates and focused verification

| Evidence | Result | Notes |
|---|---|---|
| dev-coder `019f1be2-041b-7790-8eb7-5844f4aec83f` | complete | Updated `tests/unit/infra/test_init_update.py` for severity-classifying review instructions, P0/P1 blocker fingerprints, and P2 protected-domain machine-evidence non-blocking behavior. |
| `git diff -- tests/unit/infra/test_init_update.py` | pass | Diff was limited to test phrase expectations and blocker-policy assertions. |
| `uv run pytest tests/unit/infra/test_init_update.py -k "issue_176_s05b or issue_232 or issue_75_pr_monitor_assets_retired_and_observation_scaffold_present or issue_75_pr_workflow_guidance_uses_observation_without_pr_monitor_routing or issue_197_pr_review_snapshot_provider_wrapper_invokes_python_entrypoint" -q --tb=short` | pass | Worker-reported 25 passed / 505 deselected. |
| `uv run pytest tests/unit/infra/test_init_update.py -k "issue_105_pr_merge_preparer_content_regression_contract or issue_176_s05b or issue_232 or issue_75_pr_monitor_assets_retired_and_observation_scaffold_present or issue_75_pr_workflow_guidance_uses_observation_without_pr_monitor_routing or issue_197_pr_review_snapshot_provider_wrapper_invokes_python_entrypoint" -q --tb=short` | pass | Worker-reported 26 passed / 504 deselected. |
| `uv run pytest tests/unit/infra/test_init_update.py -q --tb=short` | fail | Worker-reported 529 passed / 1 failed. Remaining failure was `test_checked_in_dogfooding_initiatives_do_not_ship_legacy_deps_json` due the active issue `.meta.json` dogfooding snapshot, not S30 test expectation behavior. |

#### S40 Terminal no-mutation boundary verification

| Evidence | Result | Notes |
|---|---|---|
| `uv run pytest tests/unit/infra/test_init_update.py -k "issue_232" -q --tb=short` | pass | 21 passed / 509 deselected. Covered `blocker_policy_no_action`, P2/P3 `non_blocking_only`, metadata preservation, and blocker fingerprint exclusion. |
| `rg -n "P2/P3|non-blocking|re-review|push|persistent|repair batch|blocker_policy_no_action" .agents/skills/github-pr-merge-preparer/SKILL.md spec-dock/templates/discussions/pr-repair-batch.md` | pass | Confirmed terminal P2/P3-only policy forbids repo-persistent repair batch creation/update, push, and re-review solely for non-blocking findings. |
| `rg -n "blocker_policy_no_action|non_blocking_only|merge_prepared|protected_domain|machine_evidence|blocker_fingerprints" tests/unit/infra/test_init_update.py .agents/skills/github-pr-observation/scripts/lib/pr_review_snapshot.py` | pass | Confirmed runtime/test evidence for non-blocking completion and metadata retention. |

#### S50 SpecDock workflow named role authorization instruction hardening

| Evidence | Result | Notes |
|---|---|---|
| doc-writer `019f1bf2-1777-7ff1-86f1-6f70d13d148b` | complete | Added bounded workflow-scoped authorization wording to provider and dogfooding Codex config, SpecDock skills, and workflow docs. |
| `rg -n "workflow-scoped authorization|SpecDock-defined named sub-agents|active repo/worktree|active SpecDock scope|documented role responsibility|ユーザーが SpecDock workflow の利用を依頼" <S50 files>` | pass | Confirmed central English and Japanese wording across changed surfaces. |
| `rg -n "workflow-scoped delegation consent|委任同意|issue-scoped workflow delegation consent|per-phase confirmation" <S50 files>` | pass | No stale consent wording remained in the changed S50 files. |
| CLOS-010 audit detail | pass | `authorization_scope`: active repo/worktree, active SpecDock scope, current session, SpecDock-defined named roles, documented role responsibility. `additional_confirmation_required`: scope expansion, destructive actions, external publishing, credentialed external mutation, private external systems, roles outside SpecDock workflow. `single_writer_authority`: canonical docs remain main orchestrator-owned; sub-agent / reviewer output is evidence and adoption is performed by the main orchestrator. |
| `cmp -s` across all 9 provider/dogfooding mirror pairs | pass | Main-orchestrator recheck reported `all mirror pairs match`. |
| `git diff --check -- <S50 files>` | pass | Worker-reported whitespace check passed. |
| doc-writer `019f1bfe-9282-73a0-a664-ee1126f333b5` | complete | Adjusted the 4 user-facing workflow docs to keep Japanese-primary prose while retaining the required English phrases as inline anchors. |
| `uv run pytest tests/unit/infra/test_init_update.py -k "test_spec_document_templates_keep_policy_out_of_scaffold" -q --tb=short` | pass | Worker-reported 1 passed / 529 deselected after Japanese-primary rewrite. |

#### Dogfooding snapshot drift closure

| Evidence | Result | Notes |
|---|---|---|
| dev-coder `019f1bf6-f9b6-76c2-a787-6d9e62cfd2ea` | complete | Added tracked `iss-00257.../.meta.json` to the checked-in dogfooding meta path and depends-on snapshots with empty dependency list. |
| `uv run pytest tests/unit/infra/test_init_update.py -k "checked_in_dogfooding_initiatives_do_not_ship_legacy_deps_json" -q --tb=short` | pass | Worker-reported 1 passed / 529 deselected after the snapshot update. |
| `uv run pytest tests/unit/infra/test_init_update.py -q --tb=short` | fail then pending recheck | Worker-reported first remaining failure was `test_spec_document_templates_keep_policy_out_of_scaffold`; doc-writer `019f1bfe-...` fixed the S50 docs-language violation. |

#### Code review P1 closure: workflow authorization contract vocabulary

| Evidence | Result | Notes |
|---|---|---|
| code-reviewer `019f1c06-30ac-7a61-98d8-0475aa8fdb0d` | fail | P1: stale `Workflow Delegation Consent` / `consent source` report contracts remained after workflow-scoped authorization hardening. |
| doc-writer `019f1c0a-14a4-7660-a27b-4f2dad5c4a20` | complete | Replaced old consent vocabulary in `workflow_issue.md`, `workflow_spec_authoring.md`, `authoring/issue-plan.md`, and `templates/issue/report.md` with `Workflow-Scoped Authorization` / `authorization source` vocabulary. |
| `rg -n "Workflow Delegation Consent|delegation consent|consent source|consent_source|委任同意|missing consent" <P1 docs/templates>` | pass | No stale consent vocabulary remained in the updated docs/templates. |
| `cmp -s` across the 4 P1 provider/dogfooding doc/template mirror pairs | pass | Main-orchestrator check reported all P1 doc mirror pairs match. |
| dev-coder `019f1c10-69ab-7693-8254-74f5b0aae467` | complete | Updated `tests/unit/infra/test_init_update.py` assertions from old consent vocabulary to workflow-scoped authorization vocabulary. |
| `uv run pytest tests/unit/infra/test_init_update.py -k "test_spec_document_templates_keep_policy_out_of_scaffold" -q --tb=short` | pass | Worker-reported 1 passed / 529 deselected after test expectation update. |
| `rg -n "Workflow Delegation Consent|consent source|missing consent|ワークフロー委任同意" tests/unit/infra/test_init_update.py` | pass | Worker-reported no matches. |
| focused issue lane | pass | Worker-reported 28 passed / 502 deselected after P1 closure. |
| doc-writer `019f1c18-6643-7c00-969f-404dce88074f` | complete | Added the new `missing workflow-scoped authorization evidence` failure-mode row to initiative/epic report templates. |
| doc-writer `019f1c1b-3095-7e63-a559-098bb6e9c5bf` and dev-coder `019f1c1b-67d8-78f3-9d0e-1530e552b929` | complete | Removed temporary bare `consent` delegated-evidence field compatibility and updated the schema helper to expect `authorization source`. |
| doc-writer `019f1c1d-c7cd-76c0-a322-b1d972cf4198` | complete | Aligned `system/active-none/{initiative,epic,issue}/report.md` provider/dogfooding assets with the same `authorization source` / `missing workflow-scoped authorization evidence` schema. |
| `uv run pytest tests/unit/infra/test_init_update.py -k "test_init_creates_expected_structure" -q --tb=short` | pass | Worker-reported 1 passed / 529 deselected after active-none alignment. |

#### S90 / pre-review verification

| Evidence | Result | Notes |
|---|---|---|
| `uv run pytest tests/unit/infra/test_init_update.py -k "issue_176_s05b or issue_232 or issue_75_pr_monitor_assets_retired_and_observation_scaffold_present or issue_75_pr_workflow_guidance_uses_observation_without_pr_monitor_routing or issue_197_pr_review_snapshot_provider_wrapper_invokes_python_entrypoint or issue_105_pr_merge_preparer_content_regression_contract or checked_in_dogfooding_initiatives_do_not_ship_legacy_deps_json or test_spec_document_templates_keep_policy_out_of_scaffold" -q --tb=short` | pass | 28 passed / 502 deselected. |
| `uv run pytest tests/unit/infra/test_init_update.py -q --tb=short` | pass | 530 passed in 324.94s. |
| `./spec-dock/scripts/spec-dock validate` | pass | `spec-dock: ok (validate) nodes=163`. |
| `./spec-dock/scripts/spec-dock assurance verify` | pass | `assurance verify: ok`; issue `iss-00257`, authorized profile `standard`. |
| `uv run pytest tests/unit/infra/test_init_update.py -k "issue_176_s05b or issue_232 or issue_75_pr_monitor_assets_retired_and_observation_scaffold_present or issue_75_pr_workflow_guidance_uses_observation_without_pr_monitor_routing or issue_197_pr_review_snapshot_provider_wrapper_invokes_python_entrypoint or issue_105_pr_merge_preparer_content_regression_contract or checked_in_dogfooding_initiatives_do_not_ship_legacy_deps_json or test_spec_document_templates_keep_policy_out_of_scaffold or test_init_creates_expected_structure" -q --tb=short` | pass | 29 passed / 501 deselected after P1 workflow authorization contract closure. |
| `uv run pytest tests/unit/infra/test_init_update.py -q --tb=short` | pass | 530 passed in 324.44s after P1 workflow authorization contract closure. |
| `./spec-dock/scripts/spec-dock validate` | pass | Re-run after P1 closure: `spec-dock: ok (validate) nodes=163`. |
| `./spec-dock/scripts/spec-dock assurance verify` | pass | Re-run after P1 closure: `assurance verify: ok`; issue `iss-00257`, authorized profile `standard`. |

#### PR observation / CI repair

| Evidence | Result | Notes |
|---|---|---|
| PR creation | pass | PR #260 created against `main` from `iss-00257-severity-aware-pr-review-policy`, head `7515ecd6ef416a2c103cdc3102d3acccd89e324d`. |
| `wait_pr_observation.sh --repo chemitaro/spec-dock --pr 260 --head-sha 7515ecd6...` | failed | Observation triggered Codex review comment and found Provider CI failed in `make lint`; recommended action `fix_ci`. |
| `gh run view 28495918351 --job 84462042332 --log` | fail evidence | `ruff format check` reported `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_review_snapshot.py` would be reformatted at `blocker_policy_blockers`. |
| dev-coder `019f1c2b-a184-7212-b453-4733b308127c` | complete | Applied formatter-equivalent one-line change to provider and dogfooding `pr_review_snapshot.py` mirror files only. |
| `uv run ruff format --check .agents/.../pr_review_snapshot.py src/spec_dock/assets/install_root/.../pr_review_snapshot.py` | pass | Worker-reported `2 files already formatted`. |
| `cmp -s .agents/.../pr_review_snapshot.py src/spec_dock/assets/install_root/.../pr_review_snapshot.py` | pass | Worker-reported mirror parity passed. |
| `make lint` | pass | Worker-reported ruff check pass, ruff format check pass, mypy pass. |
| `wait_pr_observation.sh --repo chemitaro/spec-dock --pr 260 --head-sha 56bf7660...` | failed | Observation triggered Codex review comment and returned `human_gate` / `address_review_feedback`; selected unresolved inline Codex review thread `PRRT_kwDOQ99OK86NevIt` was blocking because inline review comments were not included in `blocker_policy_findings`. |
| `gh run view 28496070249 --job 84462500420 --log` | fail evidence | Provider CI static analysis passed; pytest failed only at `tests/cli_runtime/test_new.py::TestCliNew::test_new_doc_creates_pr_repair_batch_with_generated_identity_and_template` because the test still expected old phrase `observed GitHub Actions CI failures`. |
| dev-coder `019f1c42-0ecd-7681-a4d1-0a7d8bda1aeb` | complete | Included `selected_comment_signals` in blocker policy classification, added inline comment thread metadata, excluded P2/P3 selected unresolved inline threads from actionable gate, preserved P0/P1 blockers and platform gates, and updated the stale `pr-repair-batch` assertion. |
| `uv run pytest tests/unit/infra/test_init_update.py -k "issue_232" -q --tb=short` | pass | 23 passed / 509 deselected. Covers inline `[P2]` selected unresolved thread as `non_blocking_followup` with `kind=pull_review_comment`, thread metadata, empty `actionable_unresolved_thread_ids`, and `blocker_policy_no_action`; also covers inline `[P1]` selected unresolved thread as `blocker_policy_validated_blocker`. |
| `uv run pytest tests/cli_runtime/test_new.py -k "pr_repair_batch" -q --tb=short` | pass | 1 passed / 48 deselected after aligning the test to current blocking repair wording. |
| `uv run ruff format --check .agents/.../pr_review_snapshot.py src/spec_dock/assets/install_root/.../pr_review_snapshot.py tests/unit/infra/test_init_update.py tests/cli_runtime/test_new.py` | pass | 4 files already formatted. |
| `cmp -s .agents/.../pr_review_snapshot.py src/spec_dock/assets/install_root/.../pr_review_snapshot.py` | pass | Runtime mirror parity passed after inline severity repair. |
| `uv run pytest tests/unit/infra/test_init_update.py -q --tb=short` | pass | 532 passed in 323.09s after inline severity repair tests were added. |
| `make lint` | pass | ruff check pass, ruff format check pass (`277 files already formatted`), mypy pass (`167 source files`). |
| `./spec-dock/scripts/spec-dock validate` | pass | Re-run after PR observation repair: `spec-dock: ok (validate) nodes=163`. |
| `./spec-dock/scripts/spec-dock assurance verify` | pass | Re-run after PR observation repair: `assurance verify: ok`; issue `iss-00257`, authorized profile `standard`. |
| `git diff -- <parent epic requirement/design/plan/report>` | pass | Parent Epic docs remained unchanged after PR observation repair. |
| code-reviewer `019f1c4c-1907-7212-b698-14b5b0386b90` | fail | P1: collector emitted empty `actionable_unresolved_thread_ids` for P2/P3 inline threads, but downstream `pr_observation_snapshot.py` / `pr_observation_wait.py` still treated raw selected unresolved counts as `current_selected_unresolved_thread`. |
| plan amendment | complete | Added `pr_observation_snapshot.py` and `pr_observation_wait.py` mirror pairs to the Observation runtime allowed surface and S20/S40 downstream classifier verification text. |
| dev-coder `019f1c4e-fd8d-7050-aa6f-7934dc28565c` | complete | Updated downstream snapshot/wait classifiers to prefer explicit actionable unresolved fields; raw selected counts remain legacy fallback only when explicit actionable fields are absent. |
| `uv run pytest tests/unit/infra/test_init_update.py -k "issue_222_s03 or issue_232" -q --tb=short` | pass | 31 passed / 503 deselected. Covers explicit empty actionable unresolved fields overriding raw selected counts in snapshot/wait classifiers and preserves explicit actionable unresolved blocking. |
| `uv run ruff format --check .agents/.../pr_observation_snapshot.py src/spec_dock/assets/install_root/.../pr_observation_snapshot.py .agents/.../pr_observation_wait.py src/spec_dock/assets/install_root/.../pr_observation_wait.py tests/unit/infra/test_init_update.py` | pass | 5 files already formatted. |
| `cmp -s` for `pr_observation_snapshot.py` and `pr_observation_wait.py` mirror pairs | pass | Both downstream classifier mirror pairs matched after P1 fix. |
| `uv run pytest tests/unit/infra/test_init_update.py -q --tb=short` | pass | 534 passed in 332.26s after downstream classifier tests were added. |
| `make lint` | pass | Re-run after downstream classifier fix: ruff check pass, ruff format check pass (`277 files already formatted`), mypy pass (`167 source files`). |
| `./spec-dock/scripts/spec-dock validate` | pass | Re-run after plan/report update: `spec-dock: ok (validate) nodes=163`. |
| `./spec-dock/scripts/spec-dock assurance verify` | pass | Re-run after `assurance classify --stage requirement` refreshed source binding; issue `iss-00257`, authorized profile `standard`. |
| `./spec-dock/scripts/spec-dock assurance compose --artifact all` | expected fail-closed | `substantive_content_conflict` because concrete `design.md` / `plan.md` contain authored content outside managed sections; compose did not overwrite them automatically. `assurance verify` is the final binding check and passed. |
| code-reviewer `019f1c5b-7638-75a3-ba7d-c8b5100df8f9` | fail | P1: downstream classifiers honored explicit empty actionable fields but did not treat positive explicit actionable unresolved fields as blocking when raw selected counts were zero. |
| dev-coder `019f1c5e-4b6e-7f72-be40-37187c3c0ff3` | complete | Updated snapshot/wait classifiers so positive explicit actionable unresolved fields return `actionable_unresolved_thread` before empty-actionable raw-count suppression; empty explicit fields still suppress raw selected P2/P3-only counts; legacy payload fallback remains. |
| `uv run pytest tests/unit/infra/test_init_update.py -k "issue_222_s03 or issue_232" -q --tb=short` | pass | 33 passed / 503 deselected after adding wait and snapshot tests for explicit positive actionable unresolved with raw selected count zero. |
| `uv run ruff format --check .agents/.../pr_observation_snapshot.py src/spec_dock/assets/install_root/.../pr_observation_snapshot.py .agents/.../pr_observation_wait.py src/spec_dock/assets/install_root/.../pr_observation_wait.py tests/unit/infra/test_init_update.py` | pass | 5 files already formatted after positive explicit actionable fix. |
| `cmp -s` for `pr_observation_snapshot.py` and `pr_observation_wait.py` mirror pairs | pass | Both downstream classifier mirror pairs matched after positive explicit actionable fix. |
| spec-reviewer `019f1c5b-bbf9-7b32-a2a7-9622f58eba6c` | pass | P2 docs consistency notes recorded; plan handoff summary updated to mention downstream snapshot/wait classifier mirror pairs. |
| qa-reviewer `019f1c5b-9e3a-7091-beee-81ef48fcc1ec` | pass | P2 mixed-thread coverage recommendation recorded as non-blocking follow-up risk; no P0/P1 QA gaps. |
| dev-coder `019f1c67-5e55-7071-b22a-0538a6cca602` | complete | Repaired the positive explicit actionable follow-up without breaking existing reason precedence: current-selected still wins, carryover remains waitable where required, and positive actionable is considered in the trusted submitted-review path after carryover. |
| focused Red before precedence fix | fail evidence | Worker-reported 3 failed / 41 passed / 492 deselected for `issue_187_s420 or issue_218_s02 or issue_222_s03 or issue_232`, showing the early positive-actionable return broke current-selected/carryover reason precedence. |
| `uv run pytest tests/unit/infra/test_init_update.py -k "issue_187_s420 or issue_218_s02 or issue_222_s03 or issue_232" -q --tb=short` | pass | 44 passed / 492 deselected after precedence-aware positive actionable fix. |
| `uv run pytest tests/unit/infra/test_init_update.py -q --tb=short` | pass | Worker-reported 536 passed in 331.87s after precedence-aware positive actionable fix. |
| `uv run ruff format --check ... pr_observation_snapshot.py ... pr_observation_wait.py tests/unit/infra/test_init_update.py` | pass | Worker-reported 5 files already formatted; main-orchestrator recheck with `tests/cli_runtime/test_new.py` included reported 6 files already formatted. |
| `cmp -s` for `pr_observation_snapshot.py` and `pr_observation_wait.py` mirror pairs | pass | Worker-reported and main-orchestrator rechecked mirror parity. |
| `make lint` | pass | Re-run after precedence-aware positive actionable fix: ruff check pass, ruff format check pass (`277 files already formatted`), mypy pass (`167 source files`). |
| `./spec-dock/scripts/spec-dock validate` | pass | Re-run after precedence-aware positive actionable fix: `spec-dock: ok (validate) nodes=163`. |
| `./spec-dock/scripts/spec-dock assurance verify` | pass | Re-run after precedence-aware positive actionable fix: issue `iss-00257`, authorized profile `standard`. |
| `git diff --check` | pass | No whitespace errors in the final diff. |
| `git diff -- spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00224-dynamic-workflow-resource-allocation/requirement.md spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00224-dynamic-workflow-resource-allocation/design.md spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00224-dynamic-workflow-resource-allocation/plan.md spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00224-dynamic-workflow-resource-allocation/report.md` | pass | Exact parent Epic doc path diff produced no output. |
| qa-reviewer `019f1c71-fc03-7893-a8d8-f5cc69cf09ae` | pass | Final QA review found only P2 mixed selected inline/human thread coverage recommendation; no P0/P1 QA gaps. Recommendation recorded as follow-up risk, not blocking. |

## Final Quality Gate

### Docs Impact Resolution

| Target | Update needed | Owner | Evidence | spec-reviewer result |
|---|---|---|---|---|
| Issue-local requirement/design/plan/report | yes | main orchestrator | this report includes planning, implementation, verification, and review evidence; latest downstream classifier/design amendment re-review is tracked below | pending final re-review |
| Parent Epic docs | no | N/A | `git diff -- <parent epic requirement/design/plan/report>` produced no output | N/A |
| Non-issue workflow docs / skill docs / orchestrator instructions | yes | doc-writer | S50 evidence above; provider/dogfooding mirror parity passed | pass |

### Final Spec Review Gate

| Reviewer | Scope | Findings / fixes | Re-review count | Result |
|---|---|---|---|---|
| spec-reviewer | requirement/design/plan/report alignment after supplemental authorization scope during planning | Fresh review found report/docs-impact and skill-scope issues; fixes applied; re-review passed | 2 | pass |
| spec-reviewer | final implementation/report alignment after S10-S90 | P1 stale final report completion statements; this section updated to reflect implementation completed, commit/PR still pending | 1 | pass |
| code-reviewer | final integrated diff | P1 stale delegation-consent contract; docs/templates/tests/active-none assets updated to workflow-scoped authorization vocabulary; fresh re-review found no findings | 2 | pass |
| qa-reviewer | final test adequacy | P2 stale report wording; report opening/final sections updated; focused/full lanes passed | 1 | pass |
| spec-reviewer | final implementation/docs/tests/report alignment after P1 closure | P2 CLOS-010 audit detail; `authorization_scope`, `additional_confirmation_required`, and `single_writer_authority` recorded above | 2 | pass |
| code-reviewer | PR observation repair after inline severity and downstream classifier fix | First fresh review found P1 downstream raw selected count re-blocking; second fresh review found P1 positive explicit actionable bypass; both fixes applied; final fresh review passed with no findings | 3 | pass |
| qa-reviewer | PR observation repair test adequacy | Fresh review found only P2 mixed selected inline thread coverage recommendation; final QA review passed with the P2 recorded as follow-up risk | 2 | pass |
| spec-reviewer | Plan/report/design alignment after downstream classifier plan amendment | Fresh review passed after design surface and exact parent Epic evidence fixes; remaining P2 final gate row staleness fixed here | 2 | pass |

### Final Commit

| Final report ledger | Final commit scope | Post-commit evidence destination | Result |
|---|---|---|---|
| this report | S10-S50 implementation/docs/tests, PR observation repairs, and issue report evidence | final response and PR observation artifact | final verification and reviewer gates passed; commit, push, and PR observation re-run pending |

## 遭遇した問題と解決

- 誤って no-op spec-reviewer を一件起動したが、対象 artifact をレビューしていないため workflow evidence として不採用にした。
- Plan review で terminal P2/P3-only no-mutation の検証不足が見つかったため、`CLOS-004A` と `S40` を追加して再レビュー pass を得た。
- Supplemental authorization scope review で stale docs impact gate と epic/initiative skill path ambiguity が見つかったため、`report.md` と `plan.md` を更新した。
- Final spec review で planning 時点の stale completion statements が残っていることを P1 として指摘されたため、final gate / commit / exception notes を implementation-complete but pre-commit / pre-PR 状態へ更新した。
- Full `test_init_update.py` lane で dogfooding `.meta.json` snapshot drift と scaffold docs language policy failure が順に見つかったため、snapshot と S50 workflow docs prose を最小修正して 530 passed へ戻した。
- Final code review で stale delegation-consent contract が P1 として見つかったため、workflow/report/template/test の語彙を `Workflow-Scoped Authorization` / `authorization source` へ更新し、旧 consent vocabulary を除去した。
- PR observation で inline review comment の P2/P3 が blocker policy に入らず selected unresolved thread として human gate になる P1 が見つかったため、inline comments を severity classification に含め、P2/P3 は actionable unresolved gate から外し、P0/P1 は blocker policy で止める回帰テストを追加した。
- Provider CI で `pr-repair-batch` template の旧 phrase assertion が残っていることが見つかったため、現行の blocking repair wording にテストを合わせた。
- Fresh code review で downstream observation classifier が raw selected unresolved count を再ブロックする P1 が見つかったため、explicit actionable unresolved fields がある場合はそれを blocking 判定の正本にし、旧 payload だけ raw selected count fallback を残した。
- Fresh code review で positive explicit actionable unresolved fields が raw selected count zero のとき bypass できる P1 が見つかったため、downstream classifier で positive actionable を先に `actionable_unresolved_thread` として扱うようにした。
- Full regression lane で上記 positive actionable の早期 return が current-selected / carryover / waitable precedence を壊すことが分かったため、positive actionable は trusted submitted-review path で current-selected と carryover の後に評価するよう修正した。
- QA review は mixed selected inline P2 thread with human reply の追加テストを P2 follow-up risk として推奨した。現行 gate は P0/P1 なしで pass のため、この Issue の blocking closure にはしない。

## 省略/例外メモ

- 実装変更と実装テストは完了している。追加 PR observation repair は final verification 後に commit / push し、external PR observation を再実行する。
- Parent Epic docs は編集していない。
