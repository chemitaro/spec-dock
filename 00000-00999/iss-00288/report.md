---
種別: レポート（Issue）
ID: "iss-00288"
タイトル: "Epic から Issue 候補を作る候補専用パックをドッグフードする"
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-07"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00283", "init-local-00003"]
関連GitHub: ["#288"]
---

# iss-00288 Epic から Issue 候補を作る候補専用パックをドッグフードする — レポート

## 進捗サマリー

- 現在地:
  - ChatGPT ZIP 仕様作成パック由来の Issue-local draft artifacts を evidence-only handoff として配置済み。採否判断済みの内容は `requirement.md` / `design.md` / `plan.md` へ canonical Issue specs として再記述済み。
  - ChatGPT Use / GPT-5.5 Pro Extended による実装前具体化を `artifacts/20260707t000851z-chatgpt-use-planning-summary.md` に保存済み。material spec amendment は不要、`validate_issue_candidates.py` / `authoring_pack_issue_candidates.py` を dogfood-only helper として追加する方針を採用した。
  - 実装は完了。candidate-only Epic-to-Issue output を検証し、Issue 比較 summary を出す dogfood-only helper、CLI wrapper、focused manual tests、README usage を追加した。
  - Issue 単位の fresh `spec-reviewer` gate は `019f3999-911a-7381-8155-3cda5fcf3403` で pass 済み。
  - 実装後の fresh reviewer gates は `spec-reviewer` `019f39fc-adea-7701-8dde-f0e3b37fd8cb`、`code-reviewer` `019f39f7-f36f-7a52-85cc-2c0fbe72448d`、`qa-reviewer` `019f39f7-f47d-76e1-8387-204805b1b2cd` で pass 済み。
- 次のマイルストーン:
  - `issue finish` し、次 Issue `iss-00289` を `issue start` する。
- ブロッカー:
  - 現時点で blocker はない。

## 証跡採用台帳（Evidence Adoption Ledger）

| 識別子（ID） | 採用状態（adoption_status） | 出所（source） | 対象（target） | 判断理由（rationale） | 証跡（evidence） | 次アクション（next_action） |
|---|---|---|---|---|---|---|
| EAL-001 | `adopted` | ChatGPT ZIP authoring pack draft | `requirement.md` | 親 Epic の Issue candidate draft を Issue scope / AC / non-scope として正本化した。 | `artifacts/20260706t151020z-draft-requirement-draft-requirement-from-authoring-pack.md` | execute approved plan |
| EAL-002 | `adopted` | ChatGPT ZIP authoring pack draft | `design.md` | draft-design の責務境界、入出力契約、失敗設計、観測性、テスト戦略を canonical design として再記述した。 | `artifacts/20260706t151020z-01-draft-design-draft-design-from-authoring-pack.md` | execute approved plan |
| EAL-003 | `adopted` | ChatGPT ZIP authoring pack draft | `plan.md` | draft-plan の実装ステップ、検証計画、リスク、完了条件を canonical implementation plan として再記述した。 | `artifacts/20260706t151020z-02-draft-plan-draft-plan-from-authoring-pack.md` | execute approved plan |
| EAL-004 | `adopted` | ChatGPT Use / GPT-5.5 Pro Extended planning refresh | implementation scope / naming / test focus | 実装前に current branch を GitHub に push したうえで ChatGPT Use に具体化を依頼し、material spec amendment は不要、dogfood-only Issue candidate validator 追加が最小実装という判断を採用した。 | `artifacts/20260707t000851z-chatgpt-use-planning-summary.md` | final reviewer gates |

## 目的整合台帳（Objective Alignment Ledger）

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| iss-00288 specs | `requirement.md` の目的 / 親 Epic trace / AC | `design.md` と `plan.md` の権威境界、失敗設計、検証計画 | 低。ChatGPT 出力は evidence-only handoff として保持し、採否判断済みの内容だけを canonical docs へ再記述済みである。 | pass |

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
| repo/worktree | `/Users/iwasawayuuta/.codex/worktrees/aa9c/spec-dock` |
| active scope | `epic-00283` / `iss-00288` |
| named roles | `spec-reviewer`, `code-reviewer`, `qa-reviewer`, `dev-coder`, `doc-writer`, `spec-manager` as required by plan |
| boundary | canonical docs は main orchestrator single-writer。sub-agent / ChatGPT output は evidence であり、reviewer pass や local authority の代替にしない。 |
| invalidation | scope expansion、stale branch/source、failed reviewer、requirement/design/plan の material change、allowed path 外変更の必要性 |

## Grade Specialist Evidence Gate

| field | value |
|---|---|
| local authorized_profile | `standard` |
| assurance status | `provisional` |
| Epic obligation | standard obligation |
| specialist / fallback evidence | Issue execution 開始前に specialist evidence または manual fallback evidence を `report.md` へ記録する。strict 相当 Issue では skip reason だけを readiness evidence としない。 |
| promotion rule | `.assurance.json` / `authorized_profile` は ChatGPT 推奨や Epic 側の推奨で上書きしない。 |

| profile | required_or_fallback | usage | evidence | reviewer_verdict | readiness |
|---|---|---|---|---|---|
| standard | manual fallback | used | manual evidence: fresh spec-reviewer `019f3999-911a-7381-8155-3cda5fcf3403` passed and canonical docs were integrated by main orchestrator | pass | ready |

## Reviewer Gate Status

| gate | required state | current state | promotion / completion decision |
|---|---|---|---|
| spec-reviewer | fresh `passed` | planning pass: 019f3999-911a-7381-8155-3cda5fcf3403; final execution pass: 019f39fc-adea-7701-8dde-f0e3b37fd8cb | local completion ready |
| code-reviewer | required because implementation diff exists; final Epic-wide gate is owned by `iss-00293` | passed: fresh `code-reviewer` 019f39f7-f36f-7a52-85cc-2c0fbe72448d | local completion ready |
| qa-reviewer | required because validation surface changed; final Epic-wide gate is owned by `iss-00293` | passed: fresh `qa-reviewer` 019f39f7-f47d-76e1-8387-204805b1b2cd | local completion ready |

| phase | gate | reviewer_role | freshness | state | risk_acceptance | promotion_decision | evidence |
|---|---|---|---|---|---|---|---|
| planning | spec-authoring | spec-reviewer | fresh | pass | no | execute approved plan | fresh pass `019f3999-911a-7381-8155-3cda5fcf3403` |
| execution | final-spec | spec-reviewer | fresh | pass | no | execute approved plan | fresh pass `019f39fc-adea-7701-8dde-f0e3b37fd8cb` |
| execution | code | code-reviewer | fresh | pass | no | local completion ready | fresh pass `019f39f7-f36f-7a52-85cc-2c0fbe72448d` |
| execution | qa | qa-reviewer | fresh | pass | no | local completion ready | fresh pass `019f39f7-f47d-76e1-8387-204805b1b2cd` |

## Delegated Draft Evidence

| field | value |
|---|---|
| delegated draft use | used; EAL-001〜EAL-003 の ChatGPT ZIP authoring pack draft を main orchestrator が採否判断し、採用部分だけ canonical docs へ再記述済み。 |
| source evidence | EAL / Issue-local `artifacts/*from-authoring-pack.md` を参照する。 |
| integration rule | draft artifact は evidence-only。採用済み内容だけ canonical docs に再記述し、追加採用または差分変更は Closure Delta と fresh reviewer gate を通す。 |
| reviewer caveat | ChatGPT self-review / reviewer-focus は SpecDock reviewer pass として扱わない。 |

| created_by_role | scope_id | draft_artifact_path | source_paths | intended_targets | adoption_status | reflected_to | diff_guard_result | integration_result | reviewer_focus | blockers | reviewer_result | promotion_decision |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ChatGPT Use / GPT-5.5 Pro Extended | iss-00288 | `artifacts/20260706t151020z-01-draft-design-draft-design-from-authoring-pack.md` | Epic `requirement.md`; Epic `design.md`; Epic `plan.md`; Issue-local draft artifacts | `requirement.md`; `design.md`; `plan.md`; `report.md` | adopted | `requirement.md`; `design.md`; `plan.md`; `report.md` | pass | manual-authored canonical docs integrated through Evidence Adoption Ledger | authority boundary; no direct canonical overwrite | none | pass | execute approved plan |

## Deferred PR Delivery Gate

| defer_target | dependency_basis | reason | intermediate_completion_boundary | final_pr_gate |
|---|---|---|---|---|
| `iss-00293` | Epic `plan.md` リレー実行 / PR 方針 | 個別 Issue ごとに Pull Request を作成せず、Epic 最後の品質ゲートで PR / CI / review / mergeable 確認を集約する。 | この Issue は local completion / `issue finish` まで進めても merge-prepared とは主張しない。 | `iss-00293` の PR Delivery Gate / Merge Preparation Gate が残る。 |

## 受け入れ条件（AC）の達成状況

- AC-001〜AC-004:
  - Done。`validate_issue_candidates.py` は expected parent trace / evidence-only boundary / advisory profile recommendation / canonical overwriteなしを検証し、reviewer が candidate comparison を読める report と summary を出す。
- AC-005〜AC-006:
  - Done。focused tests で複数 Issue 候補比較、missing metadata、profile-specific path / selected-skeleton-fill / non-null `authorized_profile` / advisory-only violation を検証した。


## 実装証跡（Execution Evidence）

| step | status | evidence | notes |
|---|---|---|---|
| S01 / tc-001 | pass | 親 Epic `E-RQ-011` / `E-AC-007` / `E-AC-011`、依存 Issue `iss-00284` / `iss-00285`、local `authorized_profile=standard` を確認。 | `.assurance.json` は変更していない。 |
| S02 / tc-002 | pass | `scripts/authoring-pack/authoring_pack_issue_candidates.py`、`scripts/authoring-pack/validate_issue_candidates.py`、`scripts/authoring-pack/README.md` を追加 / 更新。 | dogfood-only helper。`src/spec_dock/**` と public runtime CLI は変更していない。 |
| S03 / tc-003 | pass | `tests/manual_tests/test_validate_issue_candidates.py` 19 tests。 | valid candidate pack、generic review helper との連結、digest stale、missing parent trace、missing boundary metadata、unsafe boundary、non-null `authorized_profile`、selected skeleton path、profiles / all-profile path、profile-specific metadata key、duplicate comparison warning、保護ファイル不変、redaction を検証。 |
| S90 / tc-004 | pass | README usage を追加。canonical workflow docs / templates への直接矛盾はなし。 | ChatGPT output は evidence-only として Issue-local artifact に保存。 |
| S99 / tc-005 | pass | final reviewer gates pass、local verification pass。 | spec/code/QA reviewer pass。個別 PR は作成せず、PR delivery は `iss-00293` へ deferred。 |

## 検証証跡（Verification Evidence）

| command | result |
|---|---|
| `uv run pytest tests/manual_tests/test_validate_issue_candidates.py` | pass: 19 passed |
| `uv run pytest tests/manual_tests/test_prepare_chatgpt_authoring_pack.py tests/manual_tests/test_review_chatgpt_authoring_pack.py tests/manual_tests/test_stage_chatgpt_authoring_pack.py tests/manual_tests/test_validate_selected_skeleton_fill.py tests/manual_tests/test_validate_issue_candidates.py` | pass: 188 passed |
| `uv run ruff check scripts/authoring-pack/authoring_pack_issue_candidates.py scripts/authoring-pack/validate_issue_candidates.py tests/manual_tests/test_validate_issue_candidates.py` | pass |
| `uv run ruff format --check scripts/authoring-pack/authoring_pack_issue_candidates.py scripts/authoring-pack/validate_issue_candidates.py tests/manual_tests/test_validate_issue_candidates.py` | pass |
| `./spec-dock/scripts/spec-dock validate` | pass: `spec-dock: ok (validate) nodes=189` |
| `./spec-dock/scripts/spec-dock assurance verify` | pass: `authorized_profile: standard`, `complexity_tier: normal`, `reason: ok` |
| `git diff --check` | pass |


## Closure Evidence Ledger

| closure id | status | required evidence | current evidence | next_action |
|---|---|---|---|---|
| tc-001 | pass | 親 Epic trace / 依存 Issue / local assurance 確認 | E-RQ-011 / E-AC-007 / E-AC-011、`iss-00284` / `iss-00285`、`assurance verify` pass | closed |
| tc-002 | pass | Issue 固有成果物 / 正本直接上書きなし | dogfood-only issue candidate validator / CLI / README usage。canonical docs overwrite なし、`.assurance.json` mutation なし。 | closed |
| tc-003 | pass | 正常系 / negative fixture / validation status | focused tests 19 passed、authoring-pack manual tests 188 passed。status は pass / fail / blocked / stale / rejected を検証。 | closed |
| tc-004 | pass | docs impact / EAL / Closure Delta | README usage 追加、ChatGPT Use planning artifact 追加、workflow docs / templates no-op。 | closed |
| tc-005 | pass | `spec-dock validate` / 関連テスト / fresh reviewer result | local checks pass。fresh spec-reviewer / code-reviewer / qa-reviewer pass。 | issue finish |

## フォローアップ

- この Issue を `issue finish` し、次 Issue `iss-00289` を `issue start` する。

## 省略 / 例外メモ

- ChatGPT self-review / reviewer-focus は spec-reviewer pass として扱わない。
- `.assurance.json` / `authorized_profile` はこの report では変更しない。

## Spec Interpretation / Decision Ledger

| ID | decision | status | evidence | next_action |
|---|---|---|---|---|
| SID-iss-00288-001 | Issue-local draft artifacts は evidence-only handoff として保持し、採否判断済みの内容を canonical `design.md` / `plan.md` へ再記述した。 | accepted | Epic EAL-008b / EAL-008c / EAL-009; Issue-local `artifacts/*from-authoring-pack.md` | fresh reviewer gate を実行する |
| SID-iss-00288-002 | リレー実行方針は draft-plan artifact の補足として保持し、この Issue 単独では PR を作成しない。 | accepted | Epic `plan.md` リレー実行 / PR 方針; draft-plan のリレー節 | 実装完了後に `issue finish` し、次 Issue を `issue start` する |
| SID-iss-00288-003 | ChatGPT Use planning refresh は material spec amendment 不要と判断したため、canonical docs は変更せず、dogfood-only Issue candidate validator の実装判断だけを採用した。 | accepted | `artifacts/20260707t000851z-chatgpt-use-planning-summary.md` | issue finish |
| SID-iss-00288-004 | code-reviewer P1 と qa-reviewer P2 を反映し、generic review gate との整合、boundary metadata の未知キー reject、profile-specific rejection coverage、保護ファイル不変 coverage を追加した。 | accepted | CD-iss-00288-001 / CD-iss-00288-002、fresh code-reviewer / qa-reviewer pass | issue finish |

## Closure Delta

| delta id | trigger | change | verification |
|---|---|---|---|
| CD-iss-00288-001 | code-reviewer P1 | candidate pack が generic review gate を通るよう、入力 boundary metadata の `reviewer_pass_claimed` を `review_gate_claimed` に変更し、`non_scope` valid fixture から禁止語そのものを除外した。`boundary_metadata` の未知キーは rejected にした。 | focused tests 19 passed、authoring-pack manual tests 188 passed |
| CD-iss-00288-002 | qa-reviewer P2 | `profiles/` path、profile-specific metadata key、generic review helper 連結、canonical docs / `.assurance.json` 不変の regression tests を追加した。 | focused tests 19 passed、authoring-pack manual tests 188 passed |
