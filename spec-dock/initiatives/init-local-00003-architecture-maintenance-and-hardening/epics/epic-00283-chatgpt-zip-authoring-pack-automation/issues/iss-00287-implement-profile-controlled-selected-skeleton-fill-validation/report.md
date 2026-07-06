---
種別: レポート（Issue）
ID: "iss-00287"
タイトル: "プロファイル制御されたスケルトン記入検証を実装する"
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-07"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00283", "init-local-00003"]
関連GitHub: ["#287"]
---

# iss-00287 プロファイル制御されたスケルトン記入検証を実装する — レポート

## 進捗サマリー

- 現在地:
  - ChatGPT ZIP 仕様作成パック由来の Issue-local draft artifacts を evidence-only handoff として配置済み。採否判断済みの内容は `requirement.md` / `design.md` / `plan.md` へ canonical Issue specs として再記述済み。
  - selected skeleton fill validator、CLI wrapper、README usage、focused tests の実装は完了済み。
  - Issue 単位の fresh `spec-reviewer` gate は `019f39c3-2f19-7a70-9bc7-3d071e11d90d` で pass 済み。
  - 実装後の code-reviewer、qa-reviewer、final spec-reviewer は pass 済み。
- 次のマイルストーン:
  - `issue finish` でこの Issue を閉じ、Epic plan のリレー順に従って `iss-00288` を開始する。PR delivery は引き続き `iss-00293` に延期する。
- ブロッカー:
  - 現時点で local completion / issue finish を止める blocker はない。

## 証跡採用台帳（Evidence Adoption Ledger）

| 識別子（ID） | 採用状態（adoption_status） | 出所（source） | 対象（target） | 判断理由（rationale） | 証跡（evidence） | 次アクション（next_action） |
|---|---|---|---|---|---|---|
| EAL-001 | `adopted` | ChatGPT ZIP authoring pack draft | `requirement.md` | 親 Epic の Issue candidate draft を Issue scope / AC / non-scope として正本化した。 | `artifacts/20260706t151019z-draft-requirement-draft-requirement-from-authoring-pack.md` | execute approved plan |
| EAL-002 | `adopted` | ChatGPT ZIP authoring pack draft | `design.md` | draft-design の責務境界、入出力契約、失敗設計、観測性、テスト戦略を canonical design として再記述した。 | `artifacts/20260706t151019z-01-draft-design-draft-design-from-authoring-pack.md` | execute approved plan |
| EAL-003 | `adopted` | ChatGPT ZIP authoring pack draft | `plan.md` | draft-plan の実装ステップ、検証計画、リスク、完了条件を canonical implementation plan として再記述した。 | `artifacts/20260706t151019z-02-draft-plan-draft-plan-from-authoring-pack.md` | execute approved plan |
| EAL-004 | `adopted` | ChatGPT Use planning | `requirement.md` / `design.md` / `plan.md` | 既存 review / stage を大きく変えず、dogfood-only の selected skeleton fill validator を追加する方針を採用した。local selected skeleton manifest を authority とし、ChatGPT profile suggestion は advisory evidence に限定する。 | `artifacts/20260706t232344z-chatgpt-use-planning-summary.md`; session `specdock-iss-00287-planning` | planning spec-review |
| EAL-005 | `adopted` | implementation | `scripts/authoring-pack/authoring_pack_selected_skeleton_fill.py` | review report / pack digest / local `.assurance.json` / selected skeleton manifest / candidate section fill を照合し、profile suggestion を advisory-only に保つ dogfood-only validator を実装した。code-reviewer P2 を受け、candidate `issue_id` と selected skeleton `issue_id` の不一致を `stale` にし、`allowed_section_ids` が `section_inventory` 外を含む manifest を `fail` にした。 | `uv run pytest tests/manual_tests/test_validate_selected_skeleton_fill.py` = 19 passed | code / QA reviewer confirmation |
| EAL-006 | `adopted` | implementation | `scripts/authoring-pack/validate_selected_skeleton_fill.py` | CLI wrapper を追加し、owned output directory に `selected-skeleton-fill-validation-report.json` と summary を出すようにした。 | ruff check / format check passed | code / QA reviewer gate |
| EAL-007 | `adopted` | implementation | `tests/manual_tests/test_validate_selected_skeleton_fill.py` | valid、profile/hash stale、extra section rejected、missing required fail、unsafe claim rejected、review non-pass、pack digest mismatch、output ownership / redaction を検証した。QA reviewer P2/P3 を受け、non-pass review が missing pack validation を skip すること、metadata authority claim rejection、canonical docs bytes 不変、selected skeleton profile drift を追加検証した。 | authoring-pack focused pytest 169 passed | QA reviewer confirmation |
| EAL-008 | `adopted` | docs | `scripts/authoring-pack/README.md` | selected skeleton fill validation helper の dogfood-only usage を追加した。runtime command や正本昇格とは記述していない。 | README diff inspection passed | final spec-review |

## 目的整合台帳（Objective Alignment Ledger）

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| iss-00287 specs | `requirement.md` の目的 / 親 Epic trace / AC | `design.md` と `plan.md` の権威境界、失敗設計、検証計画、EAL-004 の selected skeleton fill 方針 | 低。ChatGPT 出力は evidence-only handoff として保持し、採否判断済みの内容だけを canonical docs へ再記述済みである。 | pass |

## 仕様 authoring ゲート（Spec Authoring Gate）

| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| requirement | 親 Epic docs、Issue-local draft requirement、EAL-004 | blocking question なし | EAL-001 と EAL-004 を採用 | pass | いいえ | execute approved plan |
| design | canonical requirement、Issue-local draft design、EAL-004 | blocking question なし | EAL-002 と EAL-004 を採用し selected skeleton fill validator 設計へ反映 | pass | いいえ | execute approved plan |
| plan | canonical requirement / design、Issue-local draft plan、EAL-004 | blocking question なし | EAL-003 と EAL-004 を採用し implementation plan へ反映 | pass | いいえ | execute approved plan |

## Workflow-Scoped Authorization

| field | value |
|---|---|
| authorization source | ユーザーの SpecDock workflow / ChatGPT Use / reviewer gate 利用依頼 |
| repo/worktree | `/Users/iwasawayuuta/.codex/worktrees/aa9c/spec-dock` |
| active scope | `epic-00283` / `iss-00287` |
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
| standard | manual fallback | used | manual evidence: ChatGPT Use `specdock-iss-00287-planning` を採用し、canonical docs は main orchestrator が統合した。fresh spec-reviewer `019f39c3-2f19-7a70-9bc7-3d071e11d90d` が P0/P1 blocker なしを確認した。 | pass | ready |

## Reviewer Gate Status

| gate | required state | current state | promotion / completion decision |
|---|---|---|---|
| spec-reviewer | fresh `passed` | passed: fresh `spec-reviewer` `019f39c3-2f19-7a70-9bc7-3d071e11d90d` | execute approved plan |
| code-reviewer | required if implementation diff or risk profile warrants; final Epic-wide gate is owned by `iss-00293` | pass: `019f39cf-8c46-71b2-a803-67b4951ef11b` after P2 fixes | code / runtime / tests / scaffold behavior diff がある場合は pass まで閉じない |
| qa-reviewer | required if implementation diff or risk profile warrants; final Epic-wide gate is owned by `iss-00293` | pass: `019f39cf-8d36-7932-8777-6a14a8de84bf` after P2/P3 test fixes | test adequacy / manual matrix risk がある場合は pass まで閉じない |
| final spec-reviewer | fresh `passed` after implementation | pass: `019f39d6-f3df-7ea1-9310-f0e78d80302e`; P2 report freshness cleanup applied | Issue finish へ進む |

| phase | gate | reviewer_role | freshness | state | risk_acceptance | promotion_decision | evidence |
|---|---|---|---|---|---|---|---|
| planning | spec-authoring | spec-reviewer | fresh | pass | no | execute approved plan | fresh pass `019f39c3-2f19-7a70-9bc7-3d071e11d90d`; previous pass `019f3999-911a-7381-8155-3cda5fcf3403` is superseded |

## Delegated Draft Evidence

| field | value |
|---|---|
| delegated draft use | used; EAL-001〜EAL-003 の ChatGPT ZIP authoring pack draft を main orchestrator が採否判断し、採用部分だけ canonical docs へ再記述済み。 |
| source evidence | EAL / Issue-local `artifacts/*from-authoring-pack.md` を参照する。 |
| integration rule | draft artifact は evidence-only。採用済み内容だけ canonical docs に再記述し、追加採用または差分変更は Closure Delta と fresh reviewer gate を通す。 |
| reviewer caveat | ChatGPT self-review / reviewer-focus は SpecDock reviewer pass として扱わない。 |

| created_by_role | scope_id | draft_artifact_path | source_paths | intended_targets | adoption_status | reflected_to | diff_guard_result | integration_result | reviewer_focus | blockers | reviewer_result | promotion_decision |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ChatGPT Use / GPT-5.5 Pro Extended | iss-00287 | `artifacts/20260706t232344z-chatgpt-use-planning-summary.md` | Epic docs、Issue docs、既存 authoring-pack scripts/tests | `requirement.md`; `design.md`; `plan.md`; `report.md` | adopted | EAL-004 | pass | main orchestrator が採用範囲だけを canonical docs へ再記述した。raw draft / ChatGPT self-review は reviewer pass ではない。fresh reviewer ID は Reviewer Gate Status に記録する。 | authority boundary; no direct canonical overwrite; profile suggestion advisory only | none | pass | execute approved plan |

## Deferred PR Delivery Gate

| defer_target | dependency_basis | reason | intermediate_completion_boundary | final_pr_gate |
|---|---|---|---|---|
| `iss-00293` | Epic `plan.md` リレー実行 / PR 方針 | 個別 Issue ごとに Pull Request を作成せず、Epic 最後の品質ゲートで PR / CI / review / mergeable 確認を集約する。 | この Issue は local completion / `issue finish` まで進めても merge-prepared とは主張しない。 | `iss-00293` の PR Delivery Gate / Merge Preparation Gate が残る。 |

## 受け入れ条件（AC）の達成状況

- AC-001〜AC-004:
  - Pass。親 Epic trace、権威境界、ローカル検証必須、独立レビュー surface は `requirement.md` / `design.md` / `plan.md` / EAL-004 / fresh spec-reviewer pass で確認済み。
- AC-005:
  - Pass。`profile_suggestion` mismatch は warning/advisory に留め、candidate `target.profile` mismatch は `stale` にするテストを追加した。validator は `.assurance.json` を読み取り専用 snapshot として扱い、テストで bytes 不変を確認した。
- AC-006:
  - Pass。`template_sha256`、`skeleton_sha256`、`section_inventory_sha256` mismatch を `stale` にし、extra section を `rejected`、missing required section を `fail` にする検証を追加した。
- AC-007〜AC-008:
  - Pass。report は section-level result、eligible / missing / extra section ids、`canonical_written=false`、`assurance_mutated=false` を出す。validator output は output dir に限定し、owned marker / no-leak / no canonical overwrite を検証した。


## Closure Evidence Ledger

| closure id | status | required evidence | current evidence | next_action |
|---|---|---|---|---|
| tc-001 | pass | 親 Epic trace / 依存 Issue / local assurance 確認 | E-RQ-008 / E-RQ-009、E-AC-005 / E-AC-006 へ trace。`assurance verify` は authorized_profile=`standard` を確認済み。 | issue finish へ進む |
| tc-002 | pass | Issue 固有成果物 / 正本直接上書きなし | `authoring_pack_selected_skeleton_fill.py` と CLI wrapper を追加。validator は `.assurance.json` と canonical docs を直接変更せず、output dir に report / summary だけを書く。 | issue finish へ進む |
| tc-003 | pass | 正常系 / negative fixture / validation status | `uv run pytest tests/manual_tests/test_validate_selected_skeleton_fill.py` が 19 passed。authoring-pack focused suite は 169 passed。 | issue finish へ進む |
| tc-004 | pass | docs impact / EAL / Closure Delta | README に dogfood-only usage を追加。runtime/provider 昇格や PR delivery は扱わない。 | issue finish へ進む |
| tc-005 | pass | `spec-dock validate` / 関連テスト / fresh reviewer result | `spec-dock validate`、`git diff --check`、ruff check / format check、focused pytest は pass。code-reviewer `019f39cf-8c46-71b2-a803-67b4951ef11b` pass、qa-reviewer `019f39cf-8d36-7932-8777-6a14a8de84bf` pass、final spec-reviewer `019f39d6-f3df-7ea1-9310-f0e78d80302e` pass。 | issue finish へ進む |

## フォローアップ

- `iss-00287` 単体の PR は作成しない。`issue finish` 後、Epic plan の依存順に従って `iss-00288` を `issue start` する。
- Epic 単位の PR delivery / mergeable 確認は `iss-00293` に延期する。

## 省略 / 例外メモ

- ChatGPT self-review / reviewer-focus は spec-reviewer pass として扱わない。
- `.assurance.json` / `authorized_profile` はこの report では変更しない。

## Spec Interpretation / Decision Ledger

| ID | decision | status | evidence | next_action |
|---|---|---|---|---|
| SID-iss-00287-001 | Issue-local draft artifacts は evidence-only handoff として保持し、採否判断済みの内容を canonical `design.md` / `plan.md` へ再記述した。 | accepted | Epic EAL-008b / EAL-008c / EAL-009; Issue-local `artifacts/*from-authoring-pack.md` | fresh reviewer gate を実行する |
| SID-iss-00287-002 | リレー実行方針は draft-plan artifact の補足として保持し、この Issue 単独では PR を作成しない。 | accepted | Epic `plan.md` リレー実行 / PR 方針; draft-plan のリレー節 | 実装完了後に `issue finish` し、次 Issue を `issue start` する |
