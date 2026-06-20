---
種別: 実装報告書（Issue）
ID: "iss-00219"
タイトル: "Carryover Unresolved Threads Stop Observation"
関連GitHub: ["#219"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-20"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00158", "init-local-00003"]
---

# iss-00219 Carryover Unresolved Threads Stop Observation — 実装報告（観測証跡台帳 / Observed Evidence Ledger）

## 仕様解釈・判断台帳（Spec Interpretation / Decision Ledger）

| 識別子（ID） | 状態（Status） | 種別（Type） | 起票元（Raised By） | 契機 / 差分（Gap） | 検討した選択肢 | 判断 / 解釈 | 根拠（Rationale） | 処置（Disposition） | 証跡（Evidence） | フォローアップ（Follow-up） |
|---|---|---|---|---|---|---|---|---|---|---|
| D-001 | resolved | interpretation | orchestrator + deep-consultants | Carryover unresolved thread と current review completion lifecycle が同時に関わる状態分類 | carryover immediate terminal; carryover audit-only; two-axis model | Current review lifecycle と actionable inventory を別軸にする | GitHub thread は actionable inventory だが current `@codex review` completion signal ではない | promoted_to_design | `discussions/20260619t221823z-disc-carryover-review-completion-policy-synthesis.md`, `design.md` | none |
| D-002 | resolved | compatibility | orchestrator + deep-consultant reason-taxonomy | Latency guard 満了後の exact `status_reason` | reuse `review_completion_unknown`; new combined reason; carryover-specific reason | `review_completion_unknown` を再利用し、carryover は structured fields で表す | Existing consumer compatibility と reason taxonomy の組み合わせ爆発回避 | promoted_to_design | `discussions/20260620t010354z-interview-carryover-unknown-status-reason-naming.md`, `design.md` | none |

## 証跡採用台帳（Evidence Adoption Ledger）

| 識別子（ID） | 採用状態（adoption_status） | 出所（source） | 対象（target） | 判断理由（rationale） | 証跡（evidence） | 次アクション（next_action） |
|---|---|---|---|---|---|---|
| EAL-001 | adopted | research | `requirement.md`, `design.md`, `plan.md` | Issue219 の source/code/tests analysis と #218 境界を canonical docs の前提に採用する | `discussions/20260619t164615z-research-carryover-observation-source-analysis.md` | plan へ closure と tests を反映 |
| EAL-002 | adopted | interview + deep-consultants | `requirement.md`, `design.md`, `plan.md` | Guard 未満 carryover-only を terminal feedback handling にしない判断を採用する | `discussions/20260619t164616z-interview-carryover-incomplete-stop-policy.md` | plan へ regression を反映 |
| EAL-003 | adopted | synthesis | `requirement.md`, `design.md`, `plan.md` | Current review lifecycle と actionable inventory の二軸モデルを採用する | `discussions/20260619t221823z-disc-carryover-review-completion-policy-synthesis.md` | plan へ step order と closure を反映 |
| EAL-004 | adopted | interview + deep-consultant | `requirement.md`, `design.md`, `plan.md` | Guard 満了後は `review_completion_unknown` を再利用し、carryover は structured fields で表す判断を採用する | `discussions/20260620t010354z-interview-carryover-unknown-status-reason-naming.md` | plan へ regression を反映 |
| EAL-005 | adopted | system-architect draft | `design.md` | Draft の分類表、module impact、JSON contract、test strategy が requirement と整合していたため採用する | `discussions/20260620t024411z-draft-design-carryover-observation-design.md`; diff guard: pass, direct child 1 file only | fresh design spec-reviewer を実行 |
| EAL-006 | adopted | spec-reviewer finding | delegated draft evidence | Delegated draft が自己採用を主張しているように見える metadata は playbook に反するため、draft は unreviewed/pending のままに戻し、採用事実は report ledger にだけ置く | design review `019ee2ef-8024-7781-b26c-a108df64c735` P1 finding | rerun design spec-reviewer |
| EAL-007 | adopted | implementation-planner draft | `plan.md` | Draft の closure index、step slicing、delegation contract、concrete test cases が reviewed design と整合していたため採用する | `discussions/20260620t025710z-draft-plan-carryover-observation-implementation-plan.md`; diff guard: pass, direct child 1 file only | fresh plan spec-reviewer を実行 |

## 目的整合台帳（Objective Alignment Ledger）

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| OAL-001 | `requirement.md` は carryover-only premature stop の解消を主目的にしている | Carryover inventory は消さず counts/ids と補助 field で保持する | low | requirement spec-reviewer pass |

## 仕様 authoring ゲート（Spec Authoring Gate）

| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| requirement | GitHub issue #219, active epic requirement, source analysis, interviews, policy synthesis, reason naming deep-consultant | Blocking question none; guard-under and reason naming answered in interviews | EAL-001..EAL-004 adopted into `requirement.md` | passed by spec-reviewer `019ee2e6-d0c4-7d42-ab37-2880ffb2fc5e`; P2 reflection metadata finding fixed | no | promoted to design |
| design | Requirement pass, runtime source inspection, system-architect draft, provider/mirror source map | Blocking question none; `actionable_inventory_reason` remains non-blocking implementation choice | EAL-005 adopted into `design.md`; EAL-006 applied to delegated evidence governance | passed by spec-reviewer `019ee2f2-5b0c-7f81-bfa8-85de08ae3f85` after fixing prior P1 governance findings | no | promoted to plan |
| plan | design reviewer pass, implementation-planner draft, phase plan docs, issue-plan authoring schema | Blocking question none; implementation choices captured as non-blocking S02/S03 decisions | EAL-007 adopted into `plan.md`; plan reviewer P1/P2 findings fixed | passed by spec-reviewer `019ee300-99ef-7fd3-b4d8-d1d10397a5c1` after fixing prior delegated-output/S90 gate findings | no | ready for issue execution |

## ワークフロー委任同意の証跡（Workflow Delegation Consent）
| 同意元（consent source） | リポジトリ / worktree（repo/worktree） | 対象課題（active issue） | セッション（session） | 指名ロール（named roles） | 境界（boundary） | 期限 / 無効化条件（expires / invalidation condition） | 拒否 / 利用不可理由（denied / unavailable reason） | 次アクション（next action） |
|---|---|---|---|---|---|---|---|---|
| user instruction invoking `$spec-dock-issue-planning` and requesting workflow-conformant requirement/design/plan authoring | `/Users/iwasawayuuta/.codex/worktrees/da42/spec-dock` | iss-00219 | current session | spec-reviewer, system-architect, implementation-planner | Same repo/worktree, active issue, named authoring/reviewer roles only; no destructive action, GitHub mutation, external publishing, credential expansion, or canonical direct-write by delegated agents | issue planning complete, session end, scope change, user revocation, or host policy conflict | none | proceed with named role gates and record evidence |

## 委任ドラフト証跡（Delegated Draft Evidence）
- 委任 authoring の使用:
  - used
- lifecycle state:
  - produced / integrated

| ロール（created_by_role） | 範囲（scope_id） | ドラフトパス（discussion draft path） | 参照元（source_paths） | 予定反映先（intended_targets） | 採用状態（adoption_status） | 反映先（reflected_to） | 差分ガード結果（diff_guard_result） | 統合結果 | 採用しなかった部分 | ブロッカー | レビュー結果（reviewer result） | 昇格判断（promotion decision） |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| system-architect | iss-00219 | `discussions/20260620t024411z-draft-design-carryover-observation-design.md` | requirement, evidence discussions, runtime sources, tests | `design.md`, `plan.md`, `report.md` | adopted in report ledger only | canonical `design.md` | pass: one new direct-child Markdown file; no forbidden path changes observed | integrated into canonical `design.md` by orchestrator | none material | none | design spec-reviewer pass | promoted to plan |
| implementation-planner | iss-00219 | `discussions/20260620t025710z-draft-plan-carryover-observation-implementation-plan.md` | reviewed requirement/design/report, phase plan docs, runtime sources, tests | `plan.md`, `report.md` | adopted in report ledger only | canonical `plan.md` | pass: one new direct-child Markdown file; no forbidden path changes observed | integrated into canonical `plan.md` by orchestrator | none material | none | pending plan spec-reviewer | plan reviewer required before execution |

### 委任 invocation 境界（Delegated Authoring Invocation Boundary）
| invocation | role | allowed output | forbidden output/actions | source artifacts | invalidation conditions | observed result |
|---|---|---|---|---|---|---|
| design draft request `019ee2e9-0360-7912-8bfc-8e691481f32c` | system-architect | Exactly one new direct-child Markdown file under issue `discussions/`, filename `20260620t*-draft-design-*.md` or `20260620t*-disc-*.md`, front matter with `created_by_role`, `scope_id`, non-empty `source_paths`, non-empty `intended_targets`, `adoption_status: unreviewed`, `reflected_to: []`, `diff_guard_result: pending` | Canonical docs, implementation files, tests, config, `.agents`, `.codex`, `.github`, GitHub state, existing discussion updates, reviewer-pass claim, phase promotion claim, implementation-readiness claim | requirement, active epic requirement, four prior discussion evidence files, PR observation skill/runtime files, relevant tests | path outside allowed scope, more than one file, forbidden mutation, stale requirement/design input, blocked source conflict | produced one draft file; main orchestrator integrated adopted content into `design.md`; draft metadata kept unreviewed/pending and adoption recorded only in this report |
| plan draft request `019ee2f4-b927-79c1-b9a8-f87476a572a8` | implementation-planner | Exactly one new direct-child Markdown file under issue `discussions/`, filename `20260620t*-draft-plan-*.md` or `20260620t*-disc-*.md`, front matter with `created_by_role`, `scope_id`, non-empty `source_paths`, non-empty `intended_targets`, `adoption_status: unreviewed`, `reflected_to: []`, `diff_guard_result: pending` | Canonical docs, implementation files, tests, config, `.agents`, `.codex`, `.github`, GitHub state, existing discussion updates, reviewer-pass claim, phase promotion claim, implementation-readiness claim | reviewed requirement/design/report, phase plan docs, issue-plan authoring schema, PR observation skill/runtime files, relevant tests | path outside allowed scope, more than one file, forbidden mutation, stale design input, blocked source conflict | produced one draft file; main orchestrator integrated adopted content into `plan.md`; draft metadata remains unreviewed/pending and adoption recorded only in this report |

### 委任ドラフトの失敗モード（Delegated Draft Failure Modes）
| 失敗モード | 期待される判定 | 許可される次アクション | レポート証跡の記録先（report evidence destination） | 昇格可否 |
|---|---|---|---|---|
| none observed | N/A | N/A | this section | eligible after canonical integration and fresh reviewer pass |

## 実装サマリー
- 未実装。現在は issue authoring phase。

## 実装記録（セッションログ）

### セッションログ（2026-06-20 authoring）

#### 対象
- Phase: requirement / design authoring
- AC/EC: all requirement AC/EC

#### 実施内容
- Source-grounded clarification evidence を採用し、`requirement.md` を scaffold から issue-specific requirement に更新した。
- Fresh `spec-reviewer` を起動し、requirement gate は `review_status: pass`。
- Reviewer の P2 指摘に従い、adopted discussion files の `reflected_to` metadata を `requirement.md` へ更新した。
- `system-architect` に scope-local design draft を依頼し、出力を diff guard 後に `design.md` へ統合した。

#### 実行コマンド / 結果
```bash
git status --short

result: existing issue authoring changes and one system-architect draft observed; no forbidden design-draft side effects found.
```

#### レビューゲート状態（Reviewer Gate Status）
| ステップ（step） | ゲート名（gate name） | レビュアーロール（reviewer role） | 鮮度（freshness） | 状態（state） | リスク受容（risk acceptance） | 昇格 / 完了判断（promotion / completion decision） | メモ（notes） |
|---|---|---|---|---|---|---|---|
| authoring-requirement | requirement spec review | spec-reviewer | fresh | passed | N/A | proceed to design | P2 reflection metadata finding fixed |
| authoring-design | design spec review | spec-reviewer | pending | pending | N/A | pending | run after canonical `design.md` integration |
| authoring-design | design spec review attempt 1 | spec-reviewer | fresh | failed | N/A | fix delegated evidence governance and rerun | P1 findings: delegated draft self-claim metadata and missing consent/invocation evidence |
| authoring-design | design spec review attempt 2 | spec-reviewer | fresh | passed | N/A | proceed to plan | previous P1 findings fixed; no remaining findings |
| authoring-plan | plan spec review | spec-reviewer | pending | pending | N/A | pending | run after canonical `plan.md` integration |
| authoring-plan | plan spec review attempt 1 | spec-reviewer | fresh | failed | N/A | fix delegated output contracts and S90 gate, then rerun | P1: delegated output contract lacked worker summary/changed files/risks/report destination/ledger note; P2: S90 commit/no-op gate missing |
| authoring-plan | plan spec review attempt 2 | spec-reviewer | fresh | passed | N/A | execution handoff ready | previous P1/P2 findings fixed; no remaining findings |

## 最終品質ゲート（Final Quality Gate）

### ドキュメント影響の解消ステップ S90（Docs Impact Resolution）
| 対象 | 更新要否 | 担当（owner） | 証跡（evidence） | 仕様レビュアー結果（spec-reviewer result） |
|---|---|---|---|---|
| docs / skill / runtime contract | pending | doc-writer or dev-coder per plan | pending implementation | pending |

### 最終 QA ゲート（Final QA Gate）
| レビュアー（reviewer） | 範囲 | 統合テスト判断（integration test decision） | 証跡（evidence） | 結果（result） |
|---|---|---|---|---|
| qa-reviewer | whole issue obligation coverage | pending | pending | pending |

### 最終コードレビューゲート（Final Code Review Gate）
| レビュアー（reviewer） | 範囲 | 指摘 / 修正（findings / fixes） | 再 review 回数（re-review count） | 結果（result） |
|---|---|---|---|---|
| code-reviewer | issue-wide integrated diff | pending | 0 | pending |

### 最終 spec review ゲート（Final Spec Review Gate）
| レビュアー（reviewer） | 範囲 | 指摘 / 修正（findings / fixes） | 再 review 回数（re-review count） | 結果（result） |
|---|---|---|---|---|
| spec-reviewer | requirement / design / plan / report / implementation / tests / docs alignment | pending | 0 | pending |

### 最終 commit（Final Commit）
| 最終 report 台帳（final report ledger） | 最終 commit 範囲（final commit scope） | コミット後の外部証跡送付先（post-commit external evidence destination） | 結果（result） |
|---|---|---|---|
| pending | pending | final response / PR | pending |

## 実行引き渡し準備（Execution Handoff Readiness）

| 項目 | 状態 | 証跡 | 次アクション |
|---|---|---|---|
| requirement authoring gate | passed | spec-reviewer `019ee2e6-d0c4-7d42-ab37-2880ffb2fc5e` | proceed |
| design authoring gate | passed | spec-reviewer `019ee2f2-5b0c-7f81-bfa8-85de08ae3f85` | proceed |
| plan authoring gate | passed | spec-reviewer `019ee300-99ef-7fd3-b4d8-d1d10397a5c1` | issue execution may start with S01 |
| unresolved blocking questions | none | `requirement.md` / `design.md` / `plan.md` | none |
| implementation start point | ready | `plan.md` S01 Regression Tests | start S01 under issue execution workflow |

## 遭遇した問題と解決
- 問題: Requirement reviewer が adopted evidence の `reflected_to` metadata が空のままと指摘した。
  - 解決: requirement へ反映済みの discussion files に `reflected_to: ["requirement.md"]` を追加し、design 統合時に `design.md` も追加した。
- 問題: Design reviewer が delegated draft metadata の self-claim と report の委任境界証跡不足を指摘した。
  - 解決: Delegated draft の front matter は `adoption_status: unreviewed`, `reflected_to: []`, `diff_guard_result: pending` に戻し、採用判断・diff guard・同意・invocation 境界は `report.md` に記録した。
- 問題: Plan reviewer が delegated step の必須出力不足と S90 commit/no-op gate 不足を指摘した。
  - 解決: S01/S02/S03 の必須出力に worker summary、changed files、verification、unresolved risks、report evidence destination、`Ledger Note` / no-material-decision requirement を追加し、S90 に reviewer gate と commit/no-op gate を追加した。

## 学んだこと
- Carryover unresolved thread は actionable inventory として残す必要があるが、current review lifecycle の completion signal と混同すると premature stop になる。

## 今後の推奨事項
- Plan authoring では Issue219 regression を first-class closure とし、guard-under / guard-satisfied / trusted-completion / current-selected priority の matrix を分ける。

## 省略/例外メモ
- 実装、step reviewer、step commit、final quality gate、PR delivery gate、merge preparation gate は未実施。現在は issue planning authoring phase。
