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

この report は `iss-00238` の観測証跡台帳である。現時点では Issue Planning phase と S01 implementation step の証跡を記録している。

## 仕様解釈・判断台帳（Spec Interpretation / Decision Ledger）

| ID | Status | Type | Raised By | Gap | Options Considered | Decision / Interpretation | Rationale | Disposition | Evidence | Follow-up |
|---|---|---|---|---|---|---|---|---|---|---|
| D-20260624-001 | resolved | follow-up | user / orchestrator | Issue 作成直後の `design.md` / `plan.md` が通常 scaffold だと Assurance 分類前に設計・計画を書き始めるリスクがある。 | `iss-00238` に混ぜる; 別 Issue に切る | 別 Issue として `iss-00239` を作成し、`iss-00238` は stdout guidance handoff に集中する。 | 変更対象が issue template / assurance compose / preflight / validate に広がり、`iss-00238` の guidance command 変更と実装境界が異なるため。 | converted_to_followup | `iss-00239`; `iss-00239/.../discussions/20260624t113051z-research-assurance-compose-scaffold-analysis.md` | `iss-00239` で対応。`iss-00238` の implementation handoff blocker ではない。 |
| D-20260624-002 | resolved | test-strategy | spec-reviewer | closure index が AC/EC 全体を明示的に覆っていなかった。 | broad final row のままにする; missing AC/EC を closure row と concrete cases に追加する | missing AC/EC を `tc-007`〜`tc-010` として追加し、S01/S02 の step closure contract に紐付ける。 | final regression row だけでは実装者と reviewer が requirement coverage を追跡しにくいため。 | promoted_to_plan | `plan.md` の Spec-Locked Closure Index / S01 / S02 | なし |
| D-20260624-003 | resolved | scope | code-reviewer | S01 で `workflow next` を削除すると、S03 まで Skill handoff が古い command を指し続ける。 | `workflow next` alias を残す; S01 で Skill handoff も更新する; S01 を戻して S03 後に削除する | `workflow next` alias は禁止のため、S01 の reviewer-directed fix として Issue Planning / Execution Skill の first-read handoff も同じ commit で `guidance <target>` へ更新する。 | command surface と shipped Skill は agent-facing handoff の atomic contract であり、分けると S01 commit 時点で利用者 workflow が壊れるため。 | promoted_to_plan | code-reviewer finding; `plan.md` S01 target files / forbidden changes exception; Skill asset diff | S03 は S01 で完了した skill handoff を確認し、必要なら approved-no-op として閉じる。 |

## 証跡採用台帳（Evidence Adoption Ledger）

| ID | adoption_status | source | target | rationale | evidence | next_action |
|---|---|---|---|---|---|---|
| EAL-20260624-001 | adopted | research | `requirement.md`, `design.md`, `plan.md` | `guidance <target>`、target 分離、互換 alias 不要、projection は人間向け自動生成 ignored artifact、context packet は対象外という判断を canonical issue docs に採用した。 | `discussions/20260624t083737z-research-stdout-runbook-handoff-current-state.md` | なし |
| EAL-20260624-002 | adopted | user discussion | `requirement.md`, `design.md`, `plan.md`, research artifact | `guidance <target>` は引数なしで Markdown stdout を返す単純な agent handoff とし、今回の issue では JSON output contract を用意しない判断を採用した。 | ユーザー発言: 「そもそもJSONのフォーマット用意しなくてよい」「引数なし、マークダウン」 | なし |
| EAL-20260624-003 | adopted | spec-reviewer | `plan.md`, `report.md` | planning reviewer の P1 指摘を採用し、report scaffold の削除、S02/S03 delegation contract 補完、closure coverage 補完、failure detection 補完を実施した。 | initial spec-reviewer `review_status: fail`; re-review `review_status: pass` on 2026-06-24 | なし |
| EAL-20260624-004 | adopted | code-reviewer | `plan.md`, `report.md`, Skill assets | S01 の code-reviewer 指摘を採用し、Skill handoff 更新を S01 atomic scope に追加した。 | initial S01 code-reviewer `review_status: fail`; Skill asset / test diff | fresh code-reviewer re-review を実施する。 |

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

- S01 実装中。`workflow next` primary command を削除し、`guidance <target>` の Markdown stdout handoff と Issue Planning / Execution Skill の first-read handoff を同一 step で更新した。

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

### セッションログ（2026-06-24 21:20 - 22:10 JST）

#### 対象
- Step: S01
- AC/EC: AC-001, AC-002, AC-003, EC-001, EC-002, EC-003
- Closure IDs: tc-001, tc-002, tc-007, tc-008

#### 実施内容
- dev-coder に S01 runtime command rename / CLI tests を委任した。
- `workflow next` を primary command surface から外し、`guidance issue-planning` / `guidance issue-execution` を Markdown stdout handoff とした。
- code-reviewer failed because shipped Issue Planning / Execution Skills still referenced `workflow next`.
- doc-writer に reviewer-directed Skill handoff fix を委任した。
- S01 scope amended so removing `workflow next` and updating Issue Planning / Execution Skill handoff are atomic.

#### 実行コマンド / 結果

```bash
./spec-dock/scripts/spec-dock guidance issue-planning
# invalid choice: 'guidance'
# S01 pre-implementation Red: guidance command was missing in the dogfooding runtime.

uv run pytest tests/cli_runtime/test_workflow.py
# 10 passed

uv run pytest tests/cli_runtime/test_workflow_context_routing.py
# 26 passed

uv run pytest tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_skills_provider_assets_are_fixed_guidance_kernels tests/unit/infra/test_init_update.py::TestInitUpdate::test_bundled_skill_routing_contract
# 2 passed

uv run pytest tests/cli_runtime/test_workflow.py tests/cli_runtime/test_workflow_context_routing.py tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_skills_provider_assets_are_fixed_guidance_kernels tests/unit/infra/test_init_update.py::TestInitUpdate::test_bundled_skill_routing_contract
# 38 passed

git diff --check
# pass
```

#### レビューゲート状態（Reviewer Gate Status）

| step / phase | gate name | reviewer role | freshness | state | risk acceptance | promotion / completion decision | notes |
|---|---|---|---|---|---|---|---|
| S01 | initial code review | code-reviewer | fresh before Skill fix | failed | no | blocked until Skill handoff fix | P1 finding: shipped Issue Planning / Execution Skills still called `workflow next`, which would break first-read handoff after command removal. |
| S01 | post-fix code re-review | code-reviewer | fresh | passed | no | S01 can be committed | Findings: none. Remaining projection behavior is explicitly left to S02 closure. |

## ステップ契約の完了証跡（Step Contract Closure）

| step | closure ids | close condition from plan | observed evidence | result | notes |
|---|---|---|---|---|---|
| S01 | tc-001, tc-002, tc-007, tc-008 | `guidance` CLI tests pass; `workflow next` is not primary command; no-active / unknown target / malformed assurance / stale source binding covered. | `uv run pytest tests/cli_runtime/test_workflow.py tests/cli_runtime/test_workflow_context_routing.py` -> `36 passed`; combined S01 + Skill fix run -> `38 passed`; `git diff --check` -> pass; `rg` confirms provider Skill assets use `guidance issue-*` and `workflow next` remains only in negative assertion. | passed | Initial code-review failed because shipped skills still called `workflow next`; reviewer-directed fix updated Skill assets and focused tests. Fresh code-reviewer re-review passed. |

## テスト契約の完了証跡（Test Contract Closure）

| closure id / test id | step | required | evidence level | pre-implementation evidence | verification command or path | observed result | notes |
|---|---|---|---|---|---|---|---|
| tc-001 | S01 | yes | red-required | `./spec-dock/scripts/spec-dock guidance issue-planning` -> invalid choice before implementation. | `uv run pytest tests/cli_runtime/test_workflow.py tests/cli_runtime/test_workflow_context_routing.py` | pass: `36 passed`; combined S01 + Skill fix run pass: `38 passed` | Markdown stdout guidance contract covered. |
| tc-002 | S01 | yes | red-required | Existing `workflow next unknown-target --format json` contract was removed; `guidance unknown-target` expected non-zero. | `tests/cli_runtime/test_workflow.py` | pass | Unknown target rejection covered. |
| tc-007 | S01 | yes | red-required | No-active guidance needed to remain available after command rename. | `tests/cli_runtime/test_workflow.py` | pass | `issue-start-required` guidance covered via Markdown command and projection payload inspection. |
| tc-008 | S01 | yes | red-required | Malformed assurance / stale source binding needed to remain fail-closed after command rename. | `tests/cli_runtime/test_workflow.py` | pass | `classification-required` / `authority-invalid` cases covered. |

## クロージャ網羅（Closure Coverage）

| closure id | step | requirement coverage | status | evidence |
|---|---|---|---|---|
| tc-001 | S01 | AC-001, AC-002 | pass | CLI runtime tests, combined S01 focused run, and fresh code-reviewer pass. |
| tc-002 | S01 | EC-002 | pass | CLI runtime unknown target case and fresh code-reviewer pass. |
| tc-007 | S01 | EC-001 | pass | CLI runtime no-active guidance case and fresh code-reviewer pass. |
| tc-008 | S01 | EC-003 | pass | CLI runtime malformed assurance / stale source binding cases and fresh code-reviewer pass. |
| tc-003, tc-004, tc-009, tc-010 | S02 | AC-004, AC-005, AC-007, EC-004 | not started | Pending S02 implementation. |
| tc-005 | S03 | AC-006 | partially covered by S01 reviewer-directed fix | Skill handoff text and init-update tests updated in S01; S03 still needs closure confirmation. |
| tc-006 | S99 | 全 AC / EC | not started | Pending final quality gate. |

## クロージャ差分（Closure Delta）

| change | closure id | test id alias | resolved closure id | reason | plan amendment required | re-review required |
|---|---|---|---|---|---|---|
| added | tc-007 | tc-s01-004 | tc-007 | EC-001 no-active behavior needed explicit closure coverage. | yes | yes |
| added | tc-008 | tc-s01-005 | tc-008 | EC-003 malformed assurance / stale binding behavior needed explicit closure coverage. | yes | yes |
| added | tc-009 | tc-s02-004 | tc-009 | EC-004 context packet fail-closed behavior needed explicit closure coverage. | yes | yes |
| added | tc-010 | tc-s02-003 | tc-010 | AC-005 ignored human projection behavior needed explicit closure coverage. | yes | yes |
| changed | tc-005 | tc-s03-001 / tc-s03-002 | tc-005 | Skill handoff update moved into S01 because removing `workflow next` first would break shipped skills. | yes | yes |

## 実装委任ゲート（Implementation Delegation Gate）

| step | status | delegated scope | role(s) | allowed paths | forbidden changes | verification | reviewer gate | open risk | next action |
|---|---|---|---|---|---|---|---|---|---|
| S01 | delegated | `guidance <target>` command surface and shipped agent handoff changes | dev-coder, doc-writer | runtime parser / command / presentation; CLI tests; Issue Planning / Execution Skill assets; focused init-update tests | Assurance policy, context packet semantics, `workflow next` alias | `38 passed`; `git diff --check` pass | passed | dogfooding mirror is not updated until a later validation/update step; provider source and generated init/update behavior are covered. | Commit S01, then start S02. |

## 委任 worker 証跡（Delegated Worker Evidence）

| step | role | summary | touched surfaces | verification | reviewer outcome | unresolved risk | adoption |
|---|---|---|---|---|---|---|---|
| S01 | dev-coder | Implemented `guidance <target>` and removed `workflow next` primary command. | runtime parser / command / presentation; CLI runtime tests | `uv run pytest tests/cli_runtime/test_workflow.py` -> `10 passed`; `uv run pytest tests/cli_runtime/test_workflow_context_routing.py` -> `26 passed`; `git diff --check` -> pass | initial code-review failed | dogfooding mirror stays stale until update / refresh step | accepted with reviewer-directed follow-up |
| S01 | doc-writer | Updated shipped Issue Planning / Execution Skill handoff to run `guidance issue-planning` / `guidance issue-execution` and register guidance into agent task checklist. | provider Skill assets; focused init-update tests | `uv run pytest tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_skills_provider_assets_are_fixed_guidance_kernels tests/unit/infra/test_init_update.py::TestInitUpdate::test_bundled_skill_routing_contract` -> `2 passed`; combined run -> `38 passed`; `git diff --check` -> pass | fresh code-reviewer re-review passed | none beyond S03 confirmation | accepted |

## 親実装例外（Parent Implementation Exception）

なし。S01 implementation は delegated worker に委任した。

## 最終品質ゲート（Final Quality Gate）

Final QA / code review / spec review gates are not started. They are planned in S99 and will be executed after S01-S03 and S90 are closed.

## 省略/例外メモ

- `guidance issue-planning` command failure is expected before S01 implementation because `guidance` is the command being introduced by this issue.
- `workflow next issue-planning` still exists because this issue has not been implemented yet; it is used only as the current skill-mandated planning handoff until S01 replaces the command surface.
