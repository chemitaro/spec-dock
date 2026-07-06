---
種別: レポート（Issue）
ID: "iss-00286"
タイトル: "仕様作成パックの差分表示と段階配置を実装する"
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-07"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00283", "init-local-00003"]
関連GitHub: ["#286"]
---

# iss-00286 仕様作成パックの差分表示と段階配置を実装する — レポート

## 進捗サマリー

- 現在地:
  - ChatGPT ZIP 仕様作成パック由来の Issue-local draft artifacts を evidence-only handoff として配置済み。採否判断済みの内容は `requirement.md` / `design.md` / `plan.md` へ canonical Issue specs として再記述済み。
  - `scripts/authoring-pack/authoring_pack_stage.py` と `stage_chatgpt_authoring_pack.py` を追加し、pass review result と pack digest が一致する隔離済み tree だけを dry-run diff / staged artifact / `unreviewed` EAL candidate へ変換できるようにした。
  - Issue 単位の fresh `spec-reviewer` gate は `019f3998-4d04-7ee3-9efe-2d809315f1ca` で pass 済み。
  - code-reviewer / qa-reviewer 初回 P1 は digest binding、unsafe output path test、real review output test、report evidence update で対応し、再レビュー pass 済み。
- 次のマイルストーン:
  - final spec-reviewer pass 済み。`issue finish` へ進む。
- ブロッカー:
  - 現時点で仕様 authoring を止める blocker はない。

## 証跡採用台帳（Evidence Adoption Ledger）

| 識別子（ID） | 採用状態（adoption_status） | 出所（source） | 対象（target） | 判断理由（rationale） | 証跡（evidence） | 次アクション（next_action） |
|---|---|---|---|---|---|---|
| EAL-001 | `adopted` | ChatGPT ZIP authoring pack draft | `requirement.md` | 親 Epic の Issue candidate draft を Issue scope / AC / non-scope として正本化した。 | `artifacts/20260706t151019z-draft-requirement-draft-requirement-from-authoring-pack.md` | spec-reviewer review |
| EAL-002 | `adopted` | ChatGPT ZIP authoring pack draft | `design.md` | draft-design の責務境界、入出力契約、失敗設計、観測性、テスト戦略を canonical design として再記述した。 | `artifacts/20260706t151019z-01-draft-design-draft-design-from-authoring-pack.md` | fresh spec-reviewer review |
| EAL-003 | `adopted` | ChatGPT ZIP authoring pack draft | `plan.md` | draft-plan の実装ステップ、検証計画、リスク、完了条件を canonical implementation plan として再記述した。 | `artifacts/20260706t151019z-02-draft-plan-draft-plan-from-authoring-pack.md` | fresh spec-reviewer review |
| EAL-004 | `adopted` | ChatGPT Use / GPT-5.5 Pro Extended planning pass | `requirement.md` / `design.md` / `plan.md` | pass review result 限定 staging、`unreviewed` EAL candidate、diagnostic redaction、output ownership の要件を正本へ反映した。 | `artifacts/20260706t223858z-chatgpt-use-planning-summary.md` | fresh spec-reviewer review |

## 目的整合台帳（Objective Alignment Ledger）

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| iss-00286 specs | `requirement.md` の目的 / 親 Epic trace / AC | `design.md` と `plan.md` の権威境界、失敗設計、検証計画 | 低。ChatGPT 出力は evidence-only handoff として保持し、採否判断済みの内容だけを canonical docs へ再記述済みである。 | pending |

## 仕様 authoring ゲート（Spec Authoring Gate）

| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| requirement | 親 Epic docs、Issue-local draft requirement | blocking question なし | EAL-001 を採用 | pass | いいえ | execute approved plan |
| design | canonical requirement、Issue-local draft design | blocking question なし | EAL-002 を採用し canonical design へ再記述 | pass | いいえ | execute approved plan |
| plan | canonical requirement / design、Issue-local draft plan | blocking question なし | EAL-003 を採用し canonical implementation plan へ再記述 | pass | いいえ | execute approved plan |
| implementation-readiness | ChatGPT Use `specdock-iss-00286-planning`、canonical requirement / design / plan | EAL candidate は `unreviewed` 固定、v1 target は Issue-local 3 docs に限定 | EAL-004 を採用し AC / component contract / focused tests を締め直した | pass | いいえ | execute approved plan |

## Workflow-Scoped Authorization

| field | value |
|---|---|
| authorization source | ユーザーの SpecDock workflow / ChatGPT Use / reviewer gate 利用依頼 |
| repo/worktree | `/Users/iwasawayuuta/.codex/worktrees/aa9c/spec-dock` |
| active scope | `epic-00283` / `iss-00286` |
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
| standard | manual fallback | used | manual evidence: fresh spec-reviewer `019f3998-4d04-7ee3-9efe-2d809315f1ca` passed and canonical docs were integrated by main orchestrator | pass | ready |

## Reviewer Gate Status

| gate | required state | current state | promotion / completion decision |
|---|---|---|---|
| spec-reviewer | fresh `passed` | passed: fresh `spec-reviewer` 019f3998-4d04-7ee3-9efe-2d809315f1ca | pass まで execution-ready としない |
| code-reviewer | required if implementation diff or risk profile warrants; final Epic-wide gate is owned by `iss-00293` | pass: `019f39a3-abfb-7bb0-92a5-980e87d58827` after P1 fixes | code / runtime / tests / scaffold behavior diff がある場合は pass まで閉じない |
| qa-reviewer | required if implementation diff or risk profile warrants; final Epic-wide gate is owned by `iss-00293` | pass: `019f39a4-205c-7303-a386-022bc84326ce` after P1 fixes | test adequacy / manual matrix risk がある場合は pass まで閉じない |
| final spec-reviewer | fresh `passed` after implementation | pass: `019f39ae-410e-7201-826d-11c10357e059` | Issue finish へ進む |

| phase | gate | reviewer_role | freshness | state | risk_acceptance | promotion_decision | evidence |
|---|---|---|---|---|---|---|---|
| planning | spec-authoring | spec-reviewer | fresh | pass | no | execute approved plan | fresh pass `019f3998-4d04-7ee3-9efe-2d809315f1ca` |

## Delegated Draft Evidence

| field | value |
|---|---|
| delegated draft use | used; EAL-001〜EAL-003 の ChatGPT ZIP authoring pack draft を main orchestrator が採否判断し、採用部分だけ canonical docs へ再記述済み。 |
| source evidence | EAL / Issue-local `artifacts/*from-authoring-pack.md` を参照する。 |
| integration rule | draft artifact は evidence-only。採用済み内容だけ canonical docs に再記述し、追加採用または差分変更は Closure Delta と fresh reviewer gate を通す。 |
| reviewer caveat | ChatGPT self-review / reviewer-focus は SpecDock reviewer pass として扱わない。 |

| created_by_role | scope_id | draft_artifact_path | source_paths | intended_targets | adoption_status | reflected_to | diff_guard_result | integration_result | reviewer_focus | blockers | reviewer_result | promotion_decision |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ChatGPT Use / GPT-5.5 Pro Extended | iss-00286 | `artifacts/20260706t151019z-01-draft-design-draft-design-from-authoring-pack.md` | Epic `requirement.md`; Epic `design.md`; Epic `plan.md`; Issue-local draft artifacts | `requirement.md`; `design.md`; `plan.md`; `report.md` | adopted | `requirement.md`; `design.md`; `plan.md`; `report.md` | pass | manual-authored canonical docs integrated through Evidence Adoption Ledger | authority boundary; no direct canonical overwrite | none | pass | execute approved plan |

## Deferred PR Delivery Gate

| defer_target | dependency_basis | reason | intermediate_completion_boundary | final_pr_gate |
|---|---|---|---|---|
| `iss-00293` | Epic `plan.md` リレー実行 / PR 方針 | 個別 Issue ごとに Pull Request を作成せず、Epic 最後の品質ゲートで PR / CI / review / mergeable 確認を集約する。 | この Issue は local completion / `issue finish` まで進めても merge-prepared とは主張しない。 | `iss-00293` の PR Delivery Gate / Merge Preparation Gate が残る。 |

## 受け入れ条件（AC）の達成状況

- AC-001〜AC-004:
  - Pass。親 Epic trace、権威境界、ローカル検証必須、独立レビュー surface は `requirement.md` / `design.md` / `plan.md` / EAL-004 / fresh spec-reviewer pass で確認済み。
- AC-005〜AC-007:
  - Pass。`authoring_pack_stage.py` / `stage_chatgpt_authoring_pack.py` と `tests/manual_tests/test_stage_chatgpt_authoring_pack.py` で、pass review result 限定 staging、pack digest mismatch の `stale`、正本 byte snapshot 不変、`unreviewed` EAL candidates、unsafe path / secret / raw transcript の no-leak / no-stage、unsafe output dir block、output ownership を確認済み。


## Closure Evidence Ledger

| closure id | status | required evidence | current evidence | next_action |
|---|---|---|---|---|
| tc-001 | pass | 親 Epic trace / 依存 Issue / local assurance 確認 | `iss-00285` safe review output を前提にし、E-RQ-006 / E-RQ-007 と E-AC-008 / E-AC-009 へ trace。`.assurance.json` / `authorized_profile` は ChatGPT 推奨で変更しない方針を維持。 | issue finish へ進む |
| tc-002 | pass | Issue 固有成果物 / 正本直接上書きなし | `authoring_pack_stage.py`、`stage_chatgpt_authoring_pack.py`、README usage、focused tests を追加。staged artifact / diff / EAL candidate は output directory 配下だけに固定名で作成し、canonical docs は read-only byte snapshot で確認。 | issue finish へ進む |
| tc-003 | pass | 正常系 / negative fixture / validation status / diagnostic non-leakage | `uv run pytest tests/manual_tests/test_stage_chatgpt_authoring_pack.py` が 21 passed。`uv run pytest tests/manual_tests/test_prepare_chatgpt_authoring_pack.py tests/manual_tests/test_review_chatgpt_authoring_pack.py tests/manual_tests/test_stage_chatgpt_authoring_pack.py` が 150 passed。 | issue finish へ進む |
| tc-004 | pass | docs impact / EAL / Closure Delta | `scripts/authoring-pack/README.md` に stage helper usage を追加し、EAL-004 と ChatGPT Use planning artifact を記録。v1 は dogfood-only helper で runtime/provider 昇格なし。 | issue finish へ進む |
| tc-005 | pass | `spec-dock validate` / 関連テスト / fresh reviewer result | `./spec-dock/scripts/spec-dock validate`、`git diff --check`、targeted ruff、150 pytest pass。code-reviewer `019f39a3-abfb-7bb0-92a5-980e87d58827` pass、qa-reviewer `019f39a4-205c-7303-a386-022bc84326ce` pass、final spec-reviewer `019f39ae-410e-7201-826d-11c10357e059` pass。 | issue finish へ進む |

## フォローアップ

- spec-reviewer pass 後、Epic plan の依存順に従って実装対象として扱う。

## 省略 / 例外メモ

- ChatGPT self-review / reviewer-focus は spec-reviewer pass として扱わない。
- `.assurance.json` / `authorized_profile` はこの report では変更しない。

## Spec Interpretation / Decision Ledger

| ID | decision | status | evidence | next_action |
|---|---|---|---|---|
| SID-iss-00286-001 | Issue-local draft artifacts は evidence-only handoff として保持し、採否判断済みの内容を canonical `design.md` / `plan.md` へ再記述した。 | accepted | Epic EAL-008b / EAL-008c / EAL-009; Issue-local `artifacts/*from-authoring-pack.md` | fresh reviewer gate を実行する |
| SID-iss-00286-002 | リレー実行方針は draft-plan artifact の補足として保持し、この Issue 単独では PR を作成しない。 | accepted | Epic `plan.md` リレー実行 / PR 方針; draft-plan のリレー節 | 実装完了後に `issue finish` し、次 Issue を `issue start` する |
