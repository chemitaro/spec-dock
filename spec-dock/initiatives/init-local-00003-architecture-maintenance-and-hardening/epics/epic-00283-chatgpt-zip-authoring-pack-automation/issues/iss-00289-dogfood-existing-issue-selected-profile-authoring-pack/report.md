---
種別: レポート（Issue）
ID: "iss-00289"
タイトル: "既存 Issue の選択済みプロファイル向けパックをドッグフードする"
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-07"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00283", "init-local-00003"]
関連GitHub: ["#289"]
---

# iss-00289 既存 Issue の選択済みプロファイル向けパックをドッグフードする — レポート

## 進捗サマリー

- 現在地:
  - ChatGPT ZIP 仕様作成パック由来の Issue-local draft artifacts を evidence-only handoff として配置済み。採否判断済みの内容は `requirement.md` / `design.md` / `plan.md` へ canonical Issue specs として再記述済み。
  - ChatGPT Use follow-up セッション `required-repository-connector-context-github-6` の助言を evidence-only planning input として採用し、selected-profile dogfood fixture / ZIP review report / validation report / section-level dry-run report を作成済み。
  - `review_chatgpt_authoring_pack.py` は preflight trace を report に反映できるようになり、`validate_selected_skeleton_fill.py` は selected skeleton の trace と section-level dry-run adoption report を出力できるようになった。
  - raw ZIP は repo に commit せず、展開済み pack tree、ZIP digest manifest、review / validation / dry-run reports を `artifacts/20260707t011500z-selected-profile-dogfood/` に保存済み。
  - Issue 単位の fresh `spec-reviewer` gate は `019f3999-911a-7381-8155-3cda5fcf3403` で pass 済み。
- 次のマイルストーン:
  - focused tests / `spec-dock validate` / `git diff --check` と fresh final reviewers を通し、local completion 可能なら `issue finish` する。
- ブロッカー:
  - 現時点で実装を止める blocker はない。

## 証跡採用台帳（Evidence Adoption Ledger）

| 識別子（ID） | 採用状態（adoption_status） | 出所（source） | 対象（target） | 判断理由（rationale） | 証跡（evidence） | 次アクション（next_action） |
|---|---|---|---|---|---|---|
| EAL-001 | `adopted` | ChatGPT ZIP authoring pack draft | `requirement.md` | 親 Epic の Issue candidate draft を Issue scope / AC / non-scope として正本化した。 | `artifacts/20260706t151020z-draft-requirement-draft-requirement-from-authoring-pack.md` | execute approved plan |
| EAL-002 | `adopted` | ChatGPT ZIP authoring pack draft | `design.md` | draft-design の責務境界、入出力契約、失敗設計、観測性、テスト戦略を canonical design として再記述した。 | `artifacts/20260706t151020z-01-draft-design-draft-design-from-authoring-pack.md` | execute approved plan |
| EAL-003 | `adopted` | ChatGPT ZIP authoring pack draft | `plan.md` | draft-plan の実装ステップ、検証計画、リスク、完了条件を canonical implementation plan として再記述した。 | `artifacts/20260706t151020z-02-draft-plan-draft-plan-from-authoring-pack.md` | execute approved plan |
| EAL-004 | `adopted` | ChatGPT Use follow-up planning evidence | implementation focus | selected-profile dogfood は validator 本体の大幅拡張ではなく、trace / dry-run report / durable evidence を補強する方針が妥当と確認した。artifact 自体は evidence-only であり、reviewer pass や canonical adoption の代替ではない。 | `artifacts/20260707t010930z-chatgpt-use-planning-summary.md` | adopted as implementation evidence; no further action |
| EAL-005 | `adopted` | selected-profile dogfood fixture | dogfood evidence | local assurance selected skeleton だけを ChatGPT fill candidate が埋め、profile suggestion は authority に使われないことを検証した。artifact 内の `adoption_status: unreviewed` は維持し、canonical rewrite には使っていない。 | `artifacts/20260707t011500z-selected-profile-dogfood/validation/selected-skeleton-fill-validation-report.json` | adopted as dogfood evidence; no canonical adoption |
| EAL-006 | `adopted` | section-level dry-run adoption report | staged adoption candidate | section-level dry-run が `canonical_written: false` / `assurance_mutated: false` を出し、正本直接上書きなしで reviewer input を残すことを確認した。staged sections は evidence-only である。 | `artifacts/20260707t011500z-selected-profile-dogfood/validation/selected-skeleton-fill-dry-run.json` | adopted as dry-run evidence; staged artifact remains evidence-only |

## 目的整合台帳（Objective Alignment Ledger）

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| iss-00289 specs | `requirement.md` の目的 / 親 Epic trace / AC | `design.md` と `plan.md` の権威境界、失敗設計、検証計画 | 低。ChatGPT 出力は evidence-only handoff として保持し、採否判断済みの内容だけを canonical docs へ再記述済みである。 | pass |
| selected-profile dogfood | `validation/selected-skeleton-fill-validation-report.json` の `trace` / `profile_validation` / `skeleton_validation` | `validation/selected-skeleton-fill-dry-run.json` の `canonical_written: false` / `assurance_mutated: false` | 低。ChatGPT の `profile_suggestion` は warning として記録され、`profile_suggestion_used_for_authority: false` が出力される。 | pass |

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
| active scope | `epic-00283` / `iss-00289` |
| named roles | `spec-reviewer`, `code-reviewer`, `qa-reviewer`, `dev-coder`, `doc-writer`, `spec-manager` as required by plan |
| boundary | canonical docs は main orchestrator single-writer。sub-agent / ChatGPT output は evidence であり、reviewer pass や local authority の代替にしない。 |
| invalidation | scope expansion、stale branch/source、failed reviewer、requirement/design/plan の material change、allowed path 外変更の必要性 |

## Grade Specialist Evidence Gate

| field | value |
|---|---|
| local authorized_profile | `standard` |
| assurance status | `provisional` |
| Epic obligation | strict 相当の追加 obligation |
| specialist / fallback evidence | ChatGPT Use planning evidence、ZIP review pass、selected skeleton validation pass、section-level dry-run report、focused tests を manual fallback evidence として記録する。strict 相当 Issue では skip reason だけを readiness evidence としない。 |
| promotion rule | `.assurance.json` / `authorized_profile` は ChatGPT 推奨や Epic 側の推奨で上書きしない。 |

| profile | required_or_fallback | usage | evidence | reviewer_verdict | readiness |
|---|---|---|---|---|---|
| standard | manual fallback | used | manual evidence: fresh spec-reviewer `019f3999-911a-7381-8155-3cda5fcf3403` passed and canonical docs were integrated by main orchestrator | pass | ready |
| standard | manual fallback | used | execution evidence: ChatGPT Use follow-up `required-repository-connector-context-github-6`; ZIP review pass; selected skeleton validation pass; dry-run report generated; focused tests and final reviewers passed | pass | ready |

## Reviewer Gate Status

| gate | required state | current state | promotion / completion decision |
|---|---|---|---|
| spec-reviewer | fresh `passed` | planning pass: `019f3999-911a-7381-8155-3cda5fcf3403`; execution pass: `019f3a43-f3e2-7df1-906a-6fe97194f2b7` | P1 dependency evidence findings were remediated; no P0/P1 blocker remains. |
| code-reviewer | fresh `passed` if implementation diff or risk profile warrants; final Epic-wide gate is owned by `iss-00293` | passed: `019f3a38-46d2-7bf0-88b5-2d3f1ca2f6d8` | P0/P1 blocker なし。trace / path / final count findings は修正済み。 |
| qa-reviewer | fresh `passed` if implementation diff or risk profile warrants; final Epic-wide gate is owned by `iss-00293` | passed: `019f3a38-6704-7ef0-a565-337bdc17f30e` | P0/P1 blocker なし。dry-run / trace / final evidence gaps は修正済み。 |

| phase | gate | reviewer_role | freshness | state | risk_acceptance | promotion_decision | evidence |
|---|---|---|---|---|---|---|---|
| planning | spec-authoring | spec-reviewer | fresh | pass | no | execute approved plan | fresh pass `019f3999-911a-7381-8155-3cda5fcf3403` |
| execution | code-review | code-reviewer | fresh | pass | no | continue final QA | fresh pass `019f3a38-46d2-7bf0-88b5-2d3f1ca2f6d8` |
| execution | spec-review | spec-reviewer | fresh | pass | no | execute approved plan / issue finish ready | fresh pass `019f3a43-f3e2-7df1-906a-6fe97194f2b7`; prior dependency evidence findings were remediated |
| execution | qa-review | qa-reviewer | fresh | pass | no | local completion ready | fresh pass `019f3a38-6704-7ef0-a565-337bdc17f30e`; prior QA P1/P2 findings were remediated by final evidence and trace safety tests |

## ChatGPT Use Planning Evidence

| field | value |
|---|---|
| initial session | `specdock-iss-00289-planning` |
| initial result | completed but non-actionable; answer only stated that repository access would be checked |
| follow-up session | `required-repository-connector-context-github-6` |
| adopted recommendation | keep this Issue dogfood-only; add durable fixture / validation report / section-level dry-run report / report evidence; do not promote runtime command |
| full browser conversation log | not committed |
| durable summary | `artifacts/20260707t010930z-chatgpt-use-planning-summary.md` |

## Selected-Profile Dogfood Execution Evidence

| field | value |
|---|---|
| dogfood artifact root | `artifacts/20260707t011500z-selected-profile-dogfood/` |
| durable pack tree | `artifacts/20260707t011500z-selected-profile-dogfood/pack-tree/specdock-authoring-pack/` |
| ZIP digest manifest | `artifacts/20260707t011500z-selected-profile-dogfood/zip-fixture-manifest.json` |
| raw ZIP committed | `false` |
| preflight | `artifacts/20260707t011500z-selected-profile-dogfood/preflight.json` |
| local assurance snapshot | `artifacts/20260707t011500z-selected-profile-dogfood/local-assurance-snapshot.json` |
| selected skeleton | `artifacts/20260707t011500z-selected-profile-dogfood/selected-skeleton.json` |
| review report | `artifacts/20260707t011500z-selected-profile-dogfood/review/validation-report.json` |
| selected skeleton validation | `artifacts/20260707t011500z-selected-profile-dogfood/validation/selected-skeleton-fill-validation-report.json` |
| section-level dry run | `artifacts/20260707t011500z-selected-profile-dogfood/validation/selected-skeleton-fill-dry-run.json` |
| local authorized_profile | `standard` |
| candidate profile_suggestion | `strict`; advisory only, ignored for authority |
| validation status | `pass` |
| dry-run status | `pass` |
| missing optional sections | `missing-section-report` |
| canonical_written | `false` |
| assurance_mutated | `false` |
| reviewer_pass_claimed | `false` |
| trace | `iss-00289` / `epic-00283` / E-RQ-008, E-RQ-009, E-RQ-010 / E-AC-005, E-AC-006, E-AC-010, E-AC-011 |

## Final Verification Evidence

| command / check | result | evidence |
|---|---|---|
| ChatGPT Use initial planning | completed, but non-actionable | `specdock-iss-00289-planning` returned only a next-step statement; not used as implementation authority |
| ChatGPT Use follow-up planning | completed, adopted as evidence-only | `required-repository-connector-context-github-6`; durable summary `artifacts/20260707t010930z-chatgpt-use-planning-summary.md` |
| ZIP review | pass | `python scripts/authoring-pack/review_chatgpt_authoring_pack.py --input <untracked zip> --preflight artifacts/20260707t011500z-selected-profile-dogfood/preflight.json --output-dir artifacts/20260707t011500z-selected-profile-dogfood/review` -> `status: pass` |
| selected skeleton validation | pass | `python scripts/authoring-pack/validate_selected_skeleton_fill.py --review-report artifacts/20260707t011500z-selected-profile-dogfood/review/validation-report.json --pack-tree artifacts/20260707t011500z-selected-profile-dogfood/pack-tree/specdock-authoring-pack --assurance .assurance.json --selected-skeleton artifacts/20260707t011500z-selected-profile-dogfood/selected-skeleton.json --output-dir artifacts/20260707t011500z-selected-profile-dogfood/validation` -> `status: pass` |
| focused authoring-pack tests | pass | `uv run pytest tests/manual_tests/test_prepare_chatgpt_authoring_pack.py tests/manual_tests/test_review_chatgpt_authoring_pack.py tests/manual_tests/test_stage_chatgpt_authoring_pack.py tests/manual_tests/test_validate_selected_skeleton_fill.py tests/manual_tests/test_validate_issue_candidates.py` -> `201 passed` |
| focused ruff check | pass | `uv run ruff check scripts/authoring-pack/authoring_pack_review.py scripts/authoring-pack/authoring_pack_selected_skeleton_fill.py tests/manual_tests/test_review_chatgpt_authoring_pack.py tests/manual_tests/test_validate_selected_skeleton_fill.py` -> `All checks passed!` |
| focused format check | pass | `uv run ruff format --check scripts/authoring-pack/authoring_pack_review.py scripts/authoring-pack/authoring_pack_selected_skeleton_fill.py tests/manual_tests/test_review_chatgpt_authoring_pack.py tests/manual_tests/test_validate_selected_skeleton_fill.py` -> `4 files already formatted` |
| whitespace diff check | pass | `git diff --check` -> no output |
| dependency readiness | pass | `./spec-dock/scripts/spec-dock deps check iss-00289` -> `source=github`, `stale=false`, `ready=true`, `blockers=0`; `./spec-dock/scripts/spec-dock deps check --no-github iss-00289` -> `source=cache`, `stale=true`, `ready=true`, `blockers=0` |
| SpecDock structural validation | pass | `./spec-dock/scripts/spec-dock validate` -> `spec-dock: ok (validate) nodes=189` |
| assurance verification | pass | `./spec-dock/scripts/spec-dock assurance verify` -> `authorized_profile: standard`, `lite_authorized: false`, `reason: ok` |
| code-reviewer | pass | `019f3a38-46d2-7bf0-88b5-2d3f1ca2f6d8` |
| spec-reviewer | pass | `019f3a43-f3e2-7df1-906a-6fe97194f2b7`; prior dependency evidence findings were remediated |
| qa-reviewer | pass | `019f3a38-6704-7ef0-a565-337bdc17f30e`; no findings; prior dry-run / trace / final evidence gaps resolved |

## Delegated Draft Evidence

| field | value |
|---|---|
| delegated draft use | used; EAL-001〜EAL-003 の ChatGPT ZIP authoring pack draft を main orchestrator が採否判断し、採用部分だけ canonical docs へ再記述済み。 |
| source evidence | EAL / Issue-local `artifacts/*from-authoring-pack.md` を参照する。 |
| integration rule | draft artifact は evidence-only。採用済み内容だけ canonical docs に再記述し、追加採用または差分変更は Closure Delta と fresh reviewer gate を通す。 |
| reviewer caveat | ChatGPT self-review / reviewer-focus は SpecDock reviewer pass として扱わない。 |

| created_by_role | scope_id | draft_artifact_path | source_paths | intended_targets | adoption_status | reflected_to | diff_guard_result | integration_result | reviewer_focus | blockers | reviewer_result | promotion_decision |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ChatGPT Use / GPT-5.5 Pro Extended | iss-00289 | `artifacts/20260706t151020z-01-draft-design-draft-design-from-authoring-pack.md` | Epic `requirement.md`; Epic `design.md`; Epic `plan.md`; Issue-local draft artifacts | `requirement.md`; `design.md`; `plan.md`; `report.md` | adopted | `requirement.md`; `design.md`; `plan.md`; `report.md` | pass | manual-authored canonical docs integrated through Evidence Adoption Ledger | authority boundary; no direct canonical overwrite | none | pass | execute approved plan |

## Deferred PR Delivery Gate

| defer_target | dependency_basis | reason | intermediate_completion_boundary | final_pr_gate |
|---|---|---|---|---|
| `iss-00293` | Epic `plan.md` リレー実行 / PR 方針 | 個別 Issue ごとに Pull Request を作成せず、Epic 最後の品質ゲートで PR / CI / review / mergeable 確認を集約する。 | この Issue は local completion / `issue finish` まで進めても merge-prepared とは主張しない。 | `iss-00293` の PR Delivery Gate / Merge Preparation Gate が残る。 |

## 受け入れ条件（AC）の達成状況

- AC-001〜AC-004:
  - Pass。dogfood preflight / review report / validation report / dry-run report が `iss-00289` / `epic-00283` / E-RQ-008, E-RQ-009, E-RQ-010 / E-AC-005, E-AC-006, E-AC-010, E-AC-011 へ trace できる。
  - Pass。`authority: evidence_only`、`adoption_status: unreviewed`、`bundle_generation_not_promotion: true` を維持し、ChatGPT output を reviewer pass や正本採用として扱っていない。
  - Pass。local validation / canonical rewrite / fresh reviewer gate が引き続き必須であることを dry-run `next_action` と EAL に残した。
  - Pass。review report、validation report、dry-run report により reviewer が adoption 可否を独立に確認できる。
- AC-005〜AC-006:
  - Pass。selected skeleton と candidate target の profile / template hash / skeleton hash / section inventory hash が一致する場合だけ `overall_adoption_eligible: true` になる。
  - Pass。section-level dry run が eligible section、optional missing section、canonical write なし、`.assurance.json` mutation なしを出力する。


## Closure Evidence Ledger

| closure id | status | required evidence | current evidence | next_action |
|---|---|---|---|---|
| tc-001 | pass | 親 Epic trace / 依存 Issue / local assurance 確認 | dogfood reports が `iss-00289` / `epic-00283` / E-RQ-008, E-RQ-009, E-RQ-010 / E-AC-005, E-AC-006, E-AC-010, E-AC-011 へ trace。local `authorized_profile` は `standard`。依存 output は `iss-00286` の staged artifact / EAL candidate 境界と `iss-00287` の selected skeleton fill validation を前提にし、今回の dogfood では review / selected skeleton validation / section-level dry-run を再実行済み。`deps check iss-00289` は GitHub refresh ありで `source=github`, `stale=false`, `ready=true`, `blockers=0`。offline cache fallback も `ready=true`, `blockers=0`。 | S02 evidence 参照 |
| tc-002 | pass | Issue 固有成果物 / 正本直接上書きなし | `artifacts/20260707t011500z-selected-profile-dogfood/` に pack tree、ZIP digest manifest、review report、validation report、dry-run report を保存。raw ZIP は未 commit。canonical docs 直接上書きなし。 | S03 evidence 参照 |
| tc-003 | pass | 正常系 / negative fixture / validation status | 正常系: ZIP review `pass`、selected skeleton validation `pass`、dry-run `pass`。既存 focused tests が profile mismatch / hash mismatch / missing required / extra section / unsafe claim / pack digest mismatch を fail-closed で確認する。 | S90 へ進む |
| tc-004 | pass | docs impact / EAL / Closure Delta | README に dry-run report 出力を明記。EAL-004〜EAL-006 を追加。runtime docs / provider runtime の変更は scope 外として no-op。 | S99 へ進む |
| tc-005 | pass | `spec-dock validate` / 関連テスト / fresh reviewer result | final verification table に `201 passed`、ruff、format、`git diff --check`、dependency readiness、`spec-dock validate`、`assurance verify`、code-reviewer pass、spec-reviewer pass、qa-reviewer pass を記録済み。 | `issue finish` へ進む |

## フォローアップ

- `iss-00293` の PR 作成前に、ユーザー補足に基づき ChatGPT Use / Oracle 実行の個人環境絶対パス依存を解消する backend command adapter / invocation contract を Epic plan または final Issue specs に追加し、最終品質ゲート対象に含める。

## 省略 / 例外メモ

- ChatGPT self-review / reviewer-focus は spec-reviewer pass として扱わない。
- `.assurance.json` / `authorized_profile` はこの report では変更しない。

## Spec Interpretation / Decision Ledger

| ID | decision | status | evidence | next_action |
|---|---|---|---|---|
| SID-iss-00289-001 | Issue-local draft artifacts は evidence-only handoff として保持し、採否判断済みの内容を canonical `design.md` / `plan.md` へ再記述した。 | accepted | Epic EAL-008b / EAL-008c / EAL-009; Issue-local `artifacts/*from-authoring-pack.md` | reviewer gate completed |
| SID-iss-00289-002 | リレー実行方針は draft-plan artifact の補足として保持し、この Issue 単独では PR を作成しない。 | accepted | Epic `plan.md` リレー実行 / PR 方針; draft-plan のリレー節 | 実装完了後に `issue finish` し、次 Issue を `issue start` する |
| SID-iss-00289-003 | selected-profile dogfood の durable evidence では raw ZIP を repo に commit せず、展開済み pack tree、ZIP digest manifest、review / validation / dry-run reports を証跡として残す。 | accepted | `artifacts/20260707t011500z-selected-profile-dogfood/zip-fixture-manifest.json`; `review/validation-report.json`; `validation/selected-skeleton-fill-dry-run.json` | reviewer gate completed |
