---
種別: レポート（Issue）
ID: "iss-00290"
タイトル: "不一致・期限切れパックをブロックできるか検証する"
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-07"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00283", "init-local-00003"]
関連GitHub: ["#290"]
---

# iss-00290 不一致・期限切れパックをブロックできるか検証する — レポート

## 進捗サマリー

- 現在地:
  - ChatGPT ZIP 仕様作成パック由来の Issue-local draft artifacts を evidence-only handoff として配置済み。採否判断済みの内容は `requirement.md` / `design.md` / `plan.md` へ canonical Issue specs として再記述済み。
  - source hash mismatch / selected profile drift / candidate profile mismatch / unsafe authority claim / pack digest mismatch の negative probe dogfood evidence を `artifacts/20260707t020429z-negative-probe-dogfood/` に配置済み。
  - `validate_selected_skeleton_fill.py` は selected skeleton を読む前に `stale` になる場合でも review report trace を fallback として使えるようになり、early stale report が `iss-00290` trace を保つ。
  - Issue 単位の final fresh reviewer gates は `spec-reviewer` `019f3a61-0a67-7ab0-85ce-230d831e7269`、`code-reviewer` `019f3a61-6653-7f81-86a5-2643d6a27cfd`、`qa-reviewer` `019f3a61-6755-76b2-9bfd-2ae45185b294` で pass 済み。
- 次のマイルストーン:
  - `issue finish` し、次 Issue を `issue start` する。
- ブロッカー:
  - 現時点で仕様 authoring を止める blocker はない。

## 証跡採用台帳（Evidence Adoption Ledger）

| 識別子（ID） | 採用状態（adoption_status） | 出所（source） | 対象（target） | 判断理由（rationale） | 証跡（evidence） | 次アクション（next_action） |
|---|---|---|---|---|---|---|
| EAL-001 | `adopted` | ChatGPT ZIP authoring pack draft | `requirement.md` | 親 Epic の Issue candidate draft を Issue scope / AC / non-scope として正本化した。 | `artifacts/20260706t151020z-draft-requirement-draft-requirement-from-authoring-pack.md` | execute approved plan |
| EAL-002 | `adopted` | ChatGPT ZIP authoring pack draft | `design.md` | draft-design の責務境界、入出力契約、失敗設計、観測性、テスト戦略を canonical design として再記述した。 | `artifacts/20260706t151021z-draft-design-draft-design-from-authoring-pack.md` | execute approved plan |
| EAL-003 | `adopted` | ChatGPT ZIP authoring pack draft | `plan.md` | draft-plan の実装ステップ、検証計画、リスク、完了条件を canonical implementation plan として再記述した。 | `artifacts/20260706t151021z-01-draft-plan-draft-plan-from-authoring-pack.md` | execute approved plan |
| EAL-004 | `adopted` | ChatGPT Use planning evidence | implementation focus | 新しい runtime behavior ではなく、既存 validator の fail-closed 動作を dogfood evidence として固定する方針を採用した。stage-attempt evidence と failure_class summary を追加する提案も採用した。 | `artifacts/20260707t021730z-chatgpt-use-planning-summary.md` | adopted as advisory evidence; no reviewer pass claim |
| EAL-005 | `adopted` | negative probe dogfood evidence | `report.md` | stale / mismatch / unsafe claim が fail-closed で pass または staged adoption にならないことを Issue-local artifact として採用した。 | `artifacts/20260707t020429z-negative-probe-dogfood/block-disposition-summary.json` | adopted as dogfood evidence; no canonical adoption |
| EAL-006 | `adopted` | early stale trace fallback fix | `scripts/authoring-pack/authoring_pack_selected_skeleton_fill.py`; `tests/manual_tests/test_validate_selected_skeleton_fill.py` | pack digest mismatch など selected skeleton 読み込み前の stale report でも review report trace を保持し、`iss-00290` の証跡として追跡可能にした。 | focused test `test_pack_digest_mismatch_is_stale` | fresh reviewers required before finish |

## 目的整合台帳（Objective Alignment Ledger）

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| iss-00290 specs | `requirement.md` の目的 / 親 Epic trace / AC | `design.md` と `plan.md` の権威境界、失敗設計、検証計画 | 低。ChatGPT 出力は evidence-only handoff として保持し、採否判断済みの内容だけを canonical docs へ再記述済みである。 | pass |
| negative probe dogfood | `block-disposition-summary.json` の 6 ケース / status / returncode | 各 validation / staging report の `canonical_written: false`、`assurance_mutated: false`、`overall_adoption_eligible: false` または `staged_artifact_count: 0` | 低。危険 claim は fixture data としてのみ保持し、validation report では rejected / stale disposition として扱う。 | pass |

## 仕様 authoring ゲート（Spec Authoring Gate）

| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| requirement | 親 Epic docs、Issue-local draft requirement | blocking question なし | EAL-001 を採用 | pass | いいえ | execute approved plan |
| design | canonical requirement、Issue-local draft design | blocking question なし | EAL-002 を採用し canonical design へ再記述 | pass | いいえ | execute approved plan |
| plan | canonical requirement / design、Issue-local draft plan | blocking question なし | EAL-003 を採用し canonical implementation plan へ再記述 | pass | いいえ | execute approved plan |

## Workflow-Scoped Authorization

| field | value |
|---|---|
| authorization source | ユーザーの SpecDock workflow / ChatGPT Use / reviewer gate 利用依頼 |
| repo/worktree | `chemitaro/spec-dock` current Issue branch checkout |
| active scope | `epic-00283` / `iss-00290` |
| named roles | `spec-reviewer`, `code-reviewer`, `qa-reviewer`, `dev-coder`, `doc-writer`, `spec-manager` as required by plan |
| boundary | canonical docs は main orchestrator single-writer。sub-agent / ChatGPT output は evidence であり、reviewer pass や local authority の代替にしない。 |
| invalidation | scope expansion、stale branch/source、failed reviewer、requirement/design/plan の material change、allowed path 外変更の必要性 |

## Grade Specialist Evidence Gate

| field | value |
|---|---|
| local authorized_profile | `standard` |
| assurance status | `provisional` |
| Epic obligation | strict 相当の追加 obligation |
| specialist / fallback evidence | Issue execution 開始前に specialist evidence または manual fallback evidence を `report.md` へ記録する。strict 相当 Issue では skip reason だけを readiness evidence としない。 |
| promotion rule | `.assurance.json` / `authorized_profile` は ChatGPT 推奨や Epic 側の推奨で上書きしない。 |

| profile | required_or_fallback | usage | evidence | reviewer_verdict | readiness |
|---|---|---|---|---|---|
| standard | manual fallback | used | manual evidence: fresh spec-reviewer `019f3999-911a-7381-8155-3cda5fcf3403` passed and canonical docs were integrated by main orchestrator | pass | ready |
| standard | manual fallback | used | execution evidence: negative probe dogfood artifact root `artifacts/20260707t020429z-negative-probe-dogfood/`; focused tests `161 passed`; ruff check passed | pending final reviewers | ready |

## Reviewer Gate Status

| gate | required state | current state | promotion / completion decision |
|---|---|---|---|
| spec-reviewer | fresh `passed` | pass: planning pass `019f3999-911a-7381-8155-3cda5fcf3403`; final re-review pass `019f3a61-0a67-7ab0-85ce-230d831e7269` | local completion gate passed; no per-Issue PR |
| code-reviewer | required if implementation diff or risk profile warrants; final Epic-wide gate is owned by `iss-00293` | pass: `019f3a61-6653-7f81-86a5-2643d6a27cfd`; P2 command-result evidence finding addressed | code / runtime / tests / scaffold behavior diff は pass 済み。final PR gate は `iss-00293` に残す |
| qa-reviewer | required if implementation diff or risk profile warrants; final Epic-wide gate is owned by `iss-00293` | pass: `019f3a61-6755-76b2-9bfd-2ae45185b294`; P2 trace-audit finding addressed | test adequacy / manual matrix risk は pass 済み。final PR gate は `iss-00293` に残す |

| phase | gate | reviewer_role | freshness | state | risk_acceptance | promotion_decision | evidence |
|---|---|---|---|---|---|---|---|
| planning | spec-authoring | spec-reviewer | fresh | pass | no | execute approved plan | fresh pass `019f3999-911a-7381-8155-3cda5fcf3403` |
| final-local | code-review | code-reviewer | fresh | pass | no | local implementation gate passed; no per-Issue PR | fresh pass `019f3a61-6653-7f81-86a5-2643d6a27cfd` |
| final-local | qa-review | qa-reviewer | fresh | pass | no | local QA gate passed; no per-Issue PR | fresh pass `019f3a61-6755-76b2-9bfd-2ae45185b294` |
| final-local | spec-review | spec-reviewer | fresh | pass | no | execute approved plan; local spec gate passed; no per-Issue PR | final re-review pass `019f3a61-0a67-7ab0-85ce-230d831e7269` |

## Reviewer Finding Disposition

| reviewer | finding | disposition | evidence |
|---|---|---|---|
| spec-reviewer `019f3a61-0a67-7ab0-85ce-230d831e7269` | P1 final reviewer gates were not yet closed in report | addressed: code-reviewer / qa-reviewer pass IDs are recorded and final spec-reviewer re-review passed | Reviewer Gate Status / Closure Evidence Ledger |
| spec-reviewer `019f3a61-0a67-7ab0-85ce-230d831e7269` | P2 ChatGPT delegated draft row used `reviewer_result: pass` | addressed: row now says `not a SpecDock reviewer pass; see separate reviewer gates` | Delegated Draft Evidence |
| code-reviewer `019f3a61-6653-7f81-86a5-2643d6a27cfd` | P2 stage-attempt command evidence was not machine-readable | addressed: `stage-attempt-stale-review-command-check/command-result.json` records command, returncode `3`, status `stale`, and staged artifact count `0` | Negative Probe Execution Evidence |
| qa-reviewer `019f3a61-6755-76b2-9bfd-2ae45185b294` | P2 stage-block top-level trace pointed to the stage helper contract | addressed: report and command-result clarify that `staging-report.json#/review/trace` is the `iss-00290` evidence trace; top-level trace remains stage helper contract trace | Negative Probe Execution Evidence |

## ChatGPT Use Planning Evidence

| field | value |
|---|---|
| session | `specdock-iss-00290-planning` |
| result | completed |
| adopted recommendation | treat `iss-00290` as dogfood evidence; avoid new runtime behavior unless evidence exposes a gap |
| adopted additions | stage-attempt evidence; failure_class summary; final verification focus |
| full browser conversation log | not committed |
| durable summary | `artifacts/20260707t021730z-chatgpt-use-planning-summary.md` |

## Negative Probe Execution Evidence

| field | value |
|---|---|
| artifact root | `artifacts/20260707t020429z-negative-probe-dogfood/` |
| summary | `artifacts/20260707t020429z-negative-probe-dogfood/block-disposition-summary.json` / `.md` |
| preflight source hash mismatch | `stale`, returncode `3`, evidence `preflight-source-hash-mismatch/diagnostics.json` |
| selected profile drift | `stale`, returncode `3`, evidence `selected-profile-drift/validation/selected-skeleton-fill-validation-report.json` |
| candidate profile mismatch | `stale`, returncode `3`, evidence `candidate-profile-mismatch/validation/selected-skeleton-fill-validation-report.json` |
| unsafe authority claim | `rejected`, returncode `4`, evidence `unsafe-authority-claim/validation/selected-skeleton-fill-validation-report.json` |
| pack digest mismatch | `stale`, returncode `3`, evidence `pack-digest-mismatch/validation/selected-skeleton-fill-validation-report.json` |
| stage attempt from stale review | `stale`, returncode `3`, staged artifact count `0`, evidence `stage-attempt-stale-review-command-check/command-result.json`; staging report `stage-attempt-stale-review-command-check/staging-report.json` |
| stage attempt trace authority | `stage-attempt-stale-review-command-check/staging-report.json#/review/trace` が `iss-00290` の evidence trace。top-level trace は stage helper contract trace であり、`iss-00290` の adoption / reviewer authority として扱わない。 |
| canonical_written | `false` |
| assurance_mutated | `false` |
| reviewer_pass_claimed | `false` |
| negative fixture unsafe claim handling | The unsafe claim text exists only in fixture input data; the observed disposition is `rejected` and adoption eligible is `false`. |

## Final Verification Evidence

| command / check | result | evidence |
|---|---|---|
| focused authoring-pack tests | pass | `uv run pytest tests/manual_tests/test_prepare_chatgpt_authoring_pack.py tests/manual_tests/test_review_chatgpt_authoring_pack.py tests/manual_tests/test_validate_selected_skeleton_fill.py -q` -> `161 passed` |
| full authoring-pack manual suite | pass | `uv run pytest tests/manual_tests/test_prepare_chatgpt_authoring_pack.py tests/manual_tests/test_review_chatgpt_authoring_pack.py tests/manual_tests/test_stage_chatgpt_authoring_pack.py tests/manual_tests/test_validate_selected_skeleton_fill.py tests/manual_tests/test_validate_issue_candidates.py -q` -> `201 passed` |
| stage stale review command check | pass | `uv run python scripts/authoring-pack/stage_chatgpt_authoring_pack.py --review-report spec-dock/active/issue/artifacts/20260707t020429z-negative-probe-dogfood/stage-attempt-stale-review/stale-review-report-for-stage.json --pack-tree spec-dock/active/issue/artifacts/20260707t020429z-negative-probe-dogfood/stage-attempt-stale-review --issue-dir spec-dock/active/issue --output-dir spec-dock/active/issue/artifacts/20260707t020429z-negative-probe-dogfood/stage-attempt-stale-review-command-check` -> expected returncode `3`, status `stale`, staged artifact count `0` |
| focused ruff check | pass | `uv run ruff check scripts/authoring-pack/authoring_pack_selected_skeleton_fill.py tests/manual_tests/test_validate_selected_skeleton_fill.py` -> `All checks passed!` |
| focused format check | pass | `uv run ruff format --check scripts/authoring-pack/authoring_pack_selected_skeleton_fill.py tests/manual_tests/test_validate_selected_skeleton_fill.py` -> `2 files already formatted` |
| whitespace diff check | pass | `git diff --check` -> no output |
| SpecDock structural validation | pass | `./spec-dock/scripts/spec-dock validate` -> `spec-dock: ok (validate) nodes=189` |

## Delegated Draft Evidence

| field | value |
|---|---|
| delegated draft use | used; EAL-001〜EAL-003 の ChatGPT ZIP authoring pack draft を main orchestrator が採否判断し、採用部分だけ canonical docs へ再記述済み。 |
| source evidence | EAL / Issue-local `artifacts/*from-authoring-pack.md` を参照する。 |
| integration rule | draft artifact は evidence-only。採用済み内容だけ canonical docs に再記述し、追加採用または差分変更は Closure Delta と fresh reviewer gate を通す。 |
| reviewer caveat | ChatGPT self-review / reviewer-focus は SpecDock reviewer pass として扱わない。 |

| created_by_role | scope_id | draft_artifact_path | source_paths | intended_targets | adoption_status | reflected_to | diff_guard_result | integration_result | reviewer_focus | blockers | reviewer_result | promotion_decision |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ChatGPT Use / GPT-5.5 Pro Extended | iss-00290 | `artifacts/20260706t151020z-draft-requirement-draft-requirement-from-authoring-pack.md` | Epic `requirement.md`; Epic `design.md`; Epic `plan.md`; Issue-local draft artifacts | `requirement.md`; `design.md`; `plan.md`; `report.md` | adopted | `requirement.md`; `design.md`; `plan.md`; `report.md` | pass | manual-authored canonical docs integrated through Evidence Adoption Ledger; reviewer_result refers to separate SpecDock reviewer gate and ChatGPT self-review is excluded | authority boundary; no direct canonical overwrite; ChatGPT self-review excluded | none | pass | execute approved plan |

## Deferred PR Delivery Gate

| defer_target | dependency_basis | reason | intermediate_completion_boundary | final_pr_gate |
|---|---|---|---|---|
| `iss-00293` | Epic `plan.md` リレー実行 / PR 方針 | 個別 Issue ごとに Pull Request を作成せず、Epic 最後の品質ゲートで PR / CI / review / mergeable 確認を集約する。 | この Issue は local completion / `issue finish` まで進めても merge-prepared とは主張しない。 | `iss-00293` の PR Delivery Gate / Merge Preparation Gate が残る。 |

## 受け入れ条件（AC）の達成状況

- AC-001〜AC-004:
  - Pass。negative probe evidence は `iss-00290` / `epic-00283` / E-RQ-005, E-RQ-008, E-RQ-010 / E-AC-002, E-AC-004, E-AC-005, E-AC-011 へ trace できる。
  - Pass。各 artifact は `authority: evidence_only`、`adoption_status: unreviewed`、`bundle_generation_not_promotion: true` を維持し、reviewer pass や canonical adoption として扱っていない。
  - Pass。validation report と block disposition summary により reviewer が adoption 不可 / regeneration 対象を独立に確認できる。
- AC-005〜AC-006:
  - Pass。source hash mismatch、selected profile drift、candidate profile mismatch、pack digest mismatch は `stale` として扱われ、unsafe authority claim は `rejected` として扱われる。
  - Pass。すべての negative probe で `overall_adoption_eligible: false`、`canonical_written: false`、`assurance_mutated: false` を確認した。


## Closure Evidence Ledger

| closure id | status | required evidence | current evidence | next_action |
|---|---|---|---|---|
| tc-001 | pass | 親 Epic trace / 依存 Issue / local assurance 確認 | negative probe evidence が `iss-00290` / `epic-00283` / E-RQ-005, E-RQ-008, E-RQ-010 / E-AC-002, E-AC-004, E-AC-005, E-AC-011 へ trace。local `authorized_profile` は `standard`。依存 output は `iss-00285` の safe review / stale_if validation と `iss-00287` の selected skeleton validation を前提にした。 | S02 evidence 参照 |
| tc-002 | pass | Issue 固有成果物 / 正本直接上書きなし | `artifacts/20260707t020429z-negative-probe-dogfood/` に negative fixture inputs、validation reports、command results、block disposition summary、stage-attempt evidence を保存。canonical docs 直接上書きなし。 | S03 evidence 参照 |
| tc-003 | pass | 正常系 / negative fixture / validation status | `preflight-source-hash-mismatch` は `stale`、`selected-profile-drift` は `stale`、`candidate-profile-mismatch` は `stale`、`unsafe-authority-claim` は `rejected`、`pack-digest-mismatch` は `stale`、`stage-attempt-stale-review` は expected returncode `3` / `stale` / staged artifact count `0`。stage-block の `iss-00290` trace authority は staging report の nested `review.trace`。 | S90 へ進む |
| tc-004 | pass | docs impact / EAL / Closure Delta | `validate_selected_skeleton_fill.py` の early stale trace fallback を追加。Issue report に EAL-004 / EAL-005 と negative probe evidence を記録。workflow docs / provider runtime の変更は scope 外として no-op。 | S99 へ進む |
| tc-005 | pass | `spec-dock validate` / 関連テスト / fresh reviewer result | focused tests、full authoring-pack manual suite、stage stale review command check、ruff、format、`git diff --check`、`spec-dock validate` は pass。code-reviewer `019f3a61-6653-7f81-86a5-2643d6a27cfd`、qa-reviewer `019f3a61-6755-76b2-9bfd-2ae45185b294`、final spec-reviewer `019f3a61-0a67-7ab0-85ce-230d831e7269` は pass。 | `issue finish` へ進む |

## フォローアップ

- `iss-00293` の PR 作成前に、ChatGPT Use / Oracle backend command adapter / invocation contract の実装・検証を行う。

## 省略 / 例外メモ

- ChatGPT self-review / reviewer-focus は spec-reviewer pass として扱わない。
- `.assurance.json` / `authorized_profile` はこの report では変更しない。

## Spec Interpretation / Decision Ledger

| ID | decision | status | evidence | next_action |
|---|---|---|---|---|
| SID-iss-00290-001 | Issue-local draft artifacts は evidence-only handoff として保持し、採否判断済みの内容を canonical `design.md` / `plan.md` へ再記述した。 | accepted | Epic EAL-008b / EAL-008c / EAL-009; Issue-local `artifacts/*from-authoring-pack.md` | reviewer gate completed |
| SID-iss-00290-002 | リレー実行方針は draft-plan artifact の補足として保持し、この Issue 単独では PR を作成しない。 | accepted | Epic `plan.md` リレー実行 / PR 方針; draft-plan のリレー節 | 実装完了後に `issue finish` し、次 Issue を `issue start` する |
| SID-iss-00290-003 | negative probe dogfood では fail-closed disposition を証跡化し、stale / rejected cases を EAL 採用候補や reviewer pass として扱わない。 | accepted | `artifacts/20260707t020429z-negative-probe-dogfood/block-disposition-summary.json`; ChatGPT Use planning summary | final reviewer gate を実行する |
