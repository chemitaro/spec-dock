---
種別: 実装報告書（Issue）
ID: "iss-00238"
タイトル: "Use Stdout Runbook Handoff Instead Of Generated Workflow Files"
関連GitHub: ["#238"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-24"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00224", "init-local-00003"]
---

# iss-00238 Use Stdout Runbook Handoff Instead Of Generated Workflow Files — 実装報告

この report は `iss-00238` の観測証跡台帳である。現時点では Issue Planning phase の証跡を記録し、実装 step の実行結果はまだ記録しない。

## 仕様解釈・判断台帳（Spec Interpretation / Decision Ledger）

| ID | Status | Type | Raised By | Gap | Options Considered | Decision / Interpretation | Rationale | Disposition | Evidence | Follow-up |
|---|---|---|---|---|---|---|---|---|---|---|
| D-20260624-001 | resolved | follow-up | user / orchestrator | Issue 作成直後の `design.md` / `plan.md` が通常 scaffold だと Assurance 分類前に設計・計画を書き始めるリスクがある。 | `iss-00238` に混ぜる; 別 Issue に切る | 別 Issue として `iss-00239` を作成し、`iss-00238` は stdout guidance handoff に集中する。 | 変更対象が issue template / assurance compose / preflight / validate に広がり、`iss-00238` の guidance command 変更と実装境界が異なるため。 | converted_to_followup | `iss-00239`; `iss-00239/.../discussions/20260624t113051z-research-assurance-compose-scaffold-analysis.md` | `iss-00239` で対応。`iss-00238` の implementation handoff blocker ではない。 |
| D-20260624-002 | resolved | test-strategy | spec-reviewer | closure index が AC/EC 全体を明示的に覆っていなかった。 | broad final row のままにする; missing AC/EC を closure row と concrete cases に追加する | missing AC/EC を `tc-007`〜`tc-010` として追加し、S01/S02 の step closure contract に紐付ける。 | final regression row だけでは実装者と reviewer が requirement coverage を追跡しにくいため。 | promoted_to_plan | `plan.md` の Spec-Locked Closure Index / S01 / S02 | なし |

## 証跡採用台帳（Evidence Adoption Ledger）

| ID | adoption_status | source | target | rationale | evidence | next_action |
|---|---|---|---|---|---|---|
| EAL-20260624-001 | adopted | research | `requirement.md`, `design.md`, `plan.md` | `guidance <target>`、target 分離、互換 alias 不要、projection は人間向け自動生成 ignored artifact、context packet は対象外という判断を canonical issue docs に採用した。 | `discussions/20260624t083737z-research-stdout-runbook-handoff-current-state.md` | なし |
| EAL-20260624-002 | adopted | user discussion | `requirement.md`, `design.md`, `plan.md`, research artifact | `guidance <target>` は引数なしで Markdown stdout を返す単純な agent handoff とし、今回の issue では JSON output contract を用意しない判断を採用した。 | ユーザー発言: 「そもそもJSONのフォーマット用意しなくてよい」「引数なし、マークダウン」 | なし |
| EAL-20260624-003 | adopted | spec-reviewer | `plan.md`, `report.md` | planning reviewer の P1 指摘を採用し、report scaffold の削除、S02/S03 delegation contract 補完、closure coverage 補完、failure detection 補完を実施した。 | initial spec-reviewer `review_status: fail`; re-review `review_status: pass` on 2026-06-24 | なし |

## 目的整合台帳（Objective Alignment Ledger）

| 対象 | primary objective evidence | secondary requirement evidence | inversion risk | reviewer verdict |
|---|---|---|---|---|
| OAL-20260624-001 | `requirement.md` は agent-facing handoff を generated workflow files から command stdout へ移すことを目的に固定している。 | `design.md` / `plan.md` は projection を human-only ignored artifact とし、Skill handoff と checklist 登録まで含めている。 | 低。`iss-00239` を分離したため、Assurance compose template lifecycle が `iss-00238` の実装目的を圧迫しない。 | pass |

## 仕様 authoring ゲート（Spec Authoring Gate）

| phase | investigated facts | open questions / answers | adoption decision | reviewer verdict | blocking | promotion / next_action |
|---|---|---|---|---|---|---|
| requirement | `requirement.md`; `discussions/20260624t083737z-research-stdout-runbook-handoff-current-state.md`; `./spec-dock/scripts/spec-dock workflow next issue-planning`; `./spec-dock/scripts/spec-dock validate` | 未確定事項なし。`guidance <target>`、互換 alias 不要、projection は agent 非関与の自動生成 artifact、Markdown stdout のみでユーザー確認済み。 | adopted | passed | no | promoted to execution handoff readiness. |
| design | `design.md`; provider runtime paths; provider Skill asset paths; tests paths; `workflow_spec_authoring.md`; `workflow_issue.md` | 未確定事項なし。`workflow status` の扱いは実装時確認事項として design / plan に containment 済み。 | adopted | passed | no | promoted to execution handoff readiness. |
| plan | `plan.md`; `phase_plan_issue.md`; `authoring/issue-plan.md`; spec-reviewer findings | reviewer 指摘により missing closure coverage、S02/S03 delegation contract、failure detection、report scaffold を修正した。 | adopted | passed | no | implementation may start from S01 under `spec-dock-issue-execution`. |

## 委任ドラフト証跡（Delegated Draft Evidence）

| created_by_role | scope_id | discussion draft path | source_paths | intended_targets | adoption_status | reflected_to | diff_guard_result | integration result | rejected portions | blockers | reviewer result | promotion decision |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| N/A | iss-00238 | N/A | N/A | N/A | not_used | [] | not_run | manual authoring by orchestrator | N/A | none | N/A | no delegated draft used for phase promotion |

## 実装サマリー

- 未開始。現在は Issue Planning phase の requirement / design / plan / report を execution handoff 可能な状態へ整備している。

## 実装記録（セッションログ）

### セッションログ（2026-06-24 20:30 - 21:20 JST）

#### 対象
- Phase: issue planning
- Artifacts: `requirement.md`, `design.md`, `plan.md`, `report.md`

#### 実施内容
- `iss-00239` を作成し、Assurance 分類後の Issue planning template 合成課題を `iss-00238` から分離した。
- `iss-00239` の research artifact を作成した。
- `iss-00238` の planning artifact に対して fresh spec-reviewer を実行した。
- spec-reviewer の P1 findings を `plan.md` / `report.md` に反映した。

#### 実行コマンド / 結果

```bash
./spec-dock/scripts/spec-dock active show
# active issue: iss-00238

./spec-dock/scripts/spec-dock workflow next issue-planning
# state: ready
# reason_code: strict-legacy-missing-assurance

./spec-dock/scripts/spec-dock guidance issue-planning
# invalid choice: 'guidance'
# Note: `guidance` command missing is expected Red for S01.

./spec-dock/scripts/spec-dock validate
# spec-dock: ok (validate) nodes=151
```

#### ワークフロー委任同意の証跡（Workflow Delegation Consent）

| consent source | repo/worktree | active issue | session | named roles | boundary | expires / invalidation condition | denied / unavailable reason | next action |
|---|---|---|---|---|---|---|---|---|
| user instruction: `$spec-dock-issue-planning` workflow に従う依頼 | `/Users/iwasawayuuta/.codex/worktrees/dbca/spec-dock` | iss-00238 | current session | spec-reviewer | same repo, active issue, current session, read-only review only; no destructive action, publishing, credentialed external access, scope expansion, or canonical write delegation | issue planning completion / session end / scope change / user revocation | none | proceed with fresh spec-reviewer re-review |

#### レビューゲート状態（Reviewer Gate Status）

| step / phase | gate name | reviewer role | freshness | state | risk acceptance | promotion / completion decision | notes |
|---|---|---|---|---|---|---|---|
| issue planning | initial planning spec review | spec-reviewer | fresh before fixes | failed | no | blocked until fixes | P1 findings: report scaffold rows, incomplete S02/S03 delegation contracts, missing AC/EC closure coverage, missing failure-detection fields. |
| issue planning | planning spec re-review | spec-reviewer | fresh | passed | no | proceed to issue execution | Findings: none. Prior P1 findings resolved; reviewer confirmed no new blocker. |

## ステップ契約の完了証跡（Step Contract Closure）

Implementation steps are not started. Step closure evidence will be recorded per S01 / S02 / S03 / S90 / S99 during issue execution.

## テスト契約の完了証跡（Test Contract Closure）

Implementation tests are not started. Pre-implementation Red for `guidance` command absence was observed and is expected for S01.

## クロージャ網羅（Closure Coverage）

Planning coverage has been amended in `plan.md` so required closure IDs `tc-001` through `tc-010` cover AC-001 through AC-007 and EC-001 through EC-004.

## クロージャ差分（Closure Delta）

| change | closure id | test id alias | resolved closure id | reason | plan amendment required | re-review required |
|---|---|---|---|---|---|---|
| added | tc-007 | tc-s01-004 | tc-007 | EC-001 no-active behavior needed explicit closure coverage. | yes | yes |
| added | tc-008 | tc-s01-005 | tc-008 | EC-003 malformed assurance / stale binding behavior needed explicit closure coverage. | yes | yes |
| added | tc-009 | tc-s02-004 | tc-009 | EC-004 context packet fail-closed behavior needed explicit closure coverage. | yes | yes |
| added | tc-010 | tc-s02-003 | tc-010 | AC-005 ignored human projection behavior needed explicit closure coverage. | yes | yes |

## 実装委任ゲート（Implementation Delegation Gate）

Implementation has not started. Delegation gates are defined in `plan.md` and will be recorded here per step during execution.

## 親実装例外（Parent Implementation Exception）

なし。Implementation has not started.

## 最終品質ゲート（Final Quality Gate）

Final QA / code review / spec review gates are not started. They are planned in S99 and will be executed after S01-S03 and S90 are closed.

## 省略/例外メモ

- `guidance issue-planning` command failure is expected before S01 implementation because `guidance` is the command being introduced by this issue.
- `workflow next issue-planning` still exists because this issue has not been implemented yet; it is used only as the current skill-mandated planning handoff until S01 replaces the command surface.
