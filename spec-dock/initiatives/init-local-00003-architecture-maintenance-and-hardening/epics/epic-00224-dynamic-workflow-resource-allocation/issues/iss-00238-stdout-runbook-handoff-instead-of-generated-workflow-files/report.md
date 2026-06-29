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

この report は `iss-00238` の観測証跡台帳である。現時点では S01 / S02 / S03 / S90 / S99 の実装・検証・レビュー証跡を記録している。

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

- S01 完了。`workflow next` primary command を削除し、`guidance <target>` の Markdown stdout handoff と Issue Planning / Execution Skill の first-read handoff を同一 step で更新した。
- S02 完了。Projection write failure は guidance state を block せず、stale projection は guidance 生成に影響せず、projection は human-only ignored artifact として明示される。

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

### セッションログ（2026-06-24 22:10 - 22:45 JST）

#### 対象
- Step: S02
- AC/EC: AC-004, AC-005, AC-007, EC-004
- Closure IDs: tc-003, tc-004, tc-009, tc-010

#### 実施内容
- `workflow_next` の projection write failure handling を best-effort に変更し、projection failure を `runbook-write-failure` blocked state へ変換しないようにした。
- Projection JSON / Markdown / stdout projection section に human-only / non-canonical / refresh command の境界を追加した。
- stale `spec-dock/.agent/runbooks/current-runbook.json` / `spec-dock/active/current-runbook.json` が存在しても、`guidance issue-planning` が current active issue から stdout / projection を再生成する CLI regression test を追加した。
- context packet write failure は既存どおり `context-packet-write-failure` blocked state を維持することを focused suite で確認した。
- tc-004 stale projection independence は実装前の現行 runtime でも projection を読まない形だったため、Red ではなく新規 regression coverage による代替証跡として採用した。

#### Red / 代替証跡

```bash
uv run pytest tests/unit/infra/test_runbook_store.py
# expected Red after S02 test update:
# 2 failed, 3 passed
# - projection payload lacked human-only metadata
# - projection write failure still returned blocked/runbook-write-failure

uv run pytest tests/cli_runtime/test_workflow.py
# expected Red after S02 test update:
# 2 failed, 9 passed
# - projection payload lacked human-only metadata
# - stale projection regression test initially used corrected current next_action expectation
```

#### Green 検証

```bash
uv run pytest tests/unit/infra/test_runbook_store.py
# 5 passed

uv run pytest tests/cli_runtime/test_workflow.py
# 11 passed

uv run pytest tests/cli_runtime/test_workflow_context_routing.py
# 26 passed

uv run pytest tests/cli_runtime/test_workflow.py tests/cli_runtime/test_workflow_context_routing.py
# 37 passed

git diff --check
# pass
```

#### レビューゲート状態（Reviewer Gate Status）

| step / phase | gate name | reviewer role | freshness | state | risk acceptance | promotion / completion decision | notes |
|---|---|---|---|---|---|---|---|
| S02 | code review | code-reviewer | fresh | passed | no | S02 can be committed | Findings: none. Reviewer confirmed projection non-blocking behavior, stale projection independence, human-only projection metadata, and context packet fail-closed handling. |

### セッションログ（2026-06-24 22:45 - 23:05 JST）

#### 対象
- Step: S03
- AC/EC: AC-003, AC-006
- Closure IDs: tc-005

#### 実施内容
- S01 reviewer-directed fix で既に provider Issue Planning / Execution Skill handoff が `guidance <target>` へ更新済みであることを確認した。
- Skill text が returned guidance の `state`, `next_action`, commands, stop conditions, selected step, verification / reviewer gate を task checklist へ登録するよう要求していることを確認した。
- Generated projections を ignored human/debug output とし、handoff authority として読まないことを Skill text と tests で確認した。
- S03 は追加 runtime / docs 変更なしの approved-no-op closure として扱う。

#### 検証

```bash
rg -n "workflow next|guidance issue-|task checklist|projection|handoff authority" \
  src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md \
  src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md \
  tests/unit/infra/test_init_update.py \
  tests/cli_runtime/test_wrappers.py
# expected guidance / checklist / projection boundary text found.
# `workflow next` remains only in a negative assertion.

uv run pytest tests/unit/infra/test_init_update.py -k "issue_skills or guidance or workflow_next"
# 8 passed

uv run pytest tests/cli_runtime/test_wrappers.py
# 6 passed

git diff --check
# pass
```

#### レビューゲート状態（Reviewer Gate Status）

| step / phase | gate name | reviewer role | freshness | state | risk acceptance | promotion / completion decision | notes |
|---|---|---|---|---|---|---|---|
| S03 | initial spec review | spec-reviewer | fresh before report fix | failed | no | blocked until S03 closure evidence is recorded | P1 finding: Skill text matched S03, but report still listed tc-005 as partial and had stale exception memo. |
| S03 | post-report-fix spec re-review | spec-reviewer | fresh | passed | no | S03 approved-no-op can be committed | Findings: none. Prior P1 closure-traceability finding resolved. |

### セッションログ（2026-06-24 23:05 - 23:30 JST）

#### 対象
- Step: S90
- Scope: docs impact resolution / dogfooding mirror refresh

#### 実施内容
- `rg` で provider docs / Skill assets / active issue docs の `workflow next` 残存を確認し、shipped Issue Planning / Execution Skill には残っていないことを確認した。
- `uv run spec-dock update .` を実行し、dogfooding workspace の `.agents/skills` と `spec-dock/scripts/spec_dock_runtime` を provider asset から更新した。
- dogfooding runtime の `./spec-dock/scripts/spec-dock --help` に `guidance` top-level command が表示され、`workflow` が status-only になっていることを確認した。
- dogfooding runtime の `./spec-dock/scripts/spec-dock guidance issue-planning` / `issue-execution` が Markdown stdout guidance を返すことを確認した。
- human projection Markdown の見出しを `Workflow Runbook` から `Guidance Projection` に調整し、projection が agent handoff authority ではないことを読み取りやすくした。

#### 検証

```bash
uv run spec-dock update .
# spec-dock: ok (update) -> /Volumes/990p2t/offloaded/home/iwasawayuuta/.codex/worktrees/dbca/spec-dock

./spec-dock/scripts/spec-dock --help
# top-level guidance command is listed.
# workflow help is status-only.

./spec-dock/scripts/spec-dock guidance issue-planning
# Markdown stdout guidance returned.
# Projection section: audience=human, authority=non-canonical.

./spec-dock/scripts/spec-dock guidance issue-execution
# Markdown stdout guidance returned with Step Assurance and Context Packets.
```

#### レビューゲート状態（Reviewer Gate Status）

| step / phase | gate name | reviewer role | freshness | state | risk acceptance | promotion / completion decision | notes |
|---|---|---|---|---|---|---|---|
| S90 | docs / mirror impact review | spec-reviewer | fresh | passed | no | S90 can be committed | Findings: none. Reviewer confirmed dogfooding context packet change is acceptable mirror parity from update step. |

### セッションログ（2026-06-24 23:30 - 23:55 JST）

#### 対象
- Step: S99
- Scope: final quality gate / issue-wide integrated diff
- Closure IDs: tc-006

#### 実施内容
- issue-wide focused regression suites を再実行した。
- `tests/unit tests/cli_runtime` の広範囲 pytest を実行し、dogfooding `.meta.json` snapshot drift 1件だけが失敗することを確認した。
- `iss-00237` / `iss-00238` / `iss-00239` の checked-in dogfooding `.meta.json` path snapshot を追加し、該当 failure を解消した。
- Provider / mirror context routing helper の lint 指摘を最小修正した。
- Full ruff は repo 既存の `setup.py` import ordering と dogfooding mirror 既存 Unicode literal で失敗するため、changed-file ruff を品質証跡として採用した。

#### 検証

```bash
uv run pytest tests/unit tests/cli_runtime
# 1 failed, 1533 passed, 76 skipped
# failure: test_checked_in_dogfooding_initiatives_do_not_ship_legacy_deps_json
# cause: dogfooding meta snapshot did not include iss-00237 / iss-00238 / iss-00239.

uv run pytest tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_initiatives_do_not_ship_legacy_deps_json
# 1 passed

uv run pytest tests/unit/infra/test_init_update.py
# 515 passed

uv run pytest tests/unit/domain/test_context_routing.py tests/cli_runtime/test_workflow_context_routing.py tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_initiatives_do_not_ship_legacy_deps_json
# 34 passed

uv run pytest tests/cli_runtime/test_wrappers.py
# 6 passed

uv run pytest tests/cli_runtime/test_workflow.py::TestCliWorkflow::test_workflow_status_and_next_detect_scaffold_requirement tests/cli_runtime/test_workflow.py
# 11 passed

uv run ruff check src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/context_packets.py spec-dock/scripts/spec_dock_runtime/application/context_packets.py src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/runbook_store.py spec-dock/scripts/spec_dock_runtime/infra/runbook_store.py tests/unit/infra/test_init_update.py
# All checks passed

uv run ruff check tests/cli_runtime/test_workflow.py
# All checks passed

uv run ruff check src spec-dock/scripts tests setup.py
# failed on existing broader lint surface: setup.py import ordering and dogfooding mirror existing ambiguous Unicode literals outside this issue's changed files.

./spec-dock/scripts/spec-dock validate
# spec-dock: ok (validate) nodes=151

git diff --check
# pass
```

#### レビューゲート状態（Reviewer Gate Status）

| step / phase | gate name | reviewer role | freshness | state | risk acceptance | promotion / completion decision | notes |
|---|---|---|---|---|---|---|---|
| S99 | final QA review | qa-reviewer | fresh | passed | no | P2 addressed before final commit | P2 finding: planning guidance test asserted state mostly through projection. Added direct stdout assertions and reran `tests/cli_runtime/test_workflow.py` -> `11 passed`. |
| S99 | final code review | code-reviewer | fresh | passed | no | S99 can proceed to final spec review | Findings: none. |
| S99 | final spec review | spec-reviewer | fresh | passed | no | S99 can be committed | P3 finding: stale report summary / final gate prose. This report update resolves it before commit. |

## ステップ契約の完了証跡（Step Contract Closure）

| step | closure ids | close condition from plan | observed evidence | result | notes |
|---|---|---|---|---|---|
| S01 | tc-001, tc-002, tc-007, tc-008 | `guidance` CLI tests pass; `workflow next` is not primary command; no-active / unknown target / malformed assurance / stale source binding covered. | `uv run pytest tests/cli_runtime/test_workflow.py tests/cli_runtime/test_workflow_context_routing.py` -> `36 passed`; combined S01 + Skill fix run -> `38 passed`; `git diff --check` -> pass; `rg` confirms provider Skill assets use `guidance issue-*` and `workflow next` remains only in negative assertion. | passed | Initial code-review failed because shipped skills still called `workflow next`; reviewer-directed fix updated Skill assets and focused tests. Fresh code-reviewer re-review passed. |
| S02 | tc-003, tc-004, tc-009, tc-010 | Projection failure / stale projection tests pass; context packet fail-closed tests are maintained. | `uv run pytest tests/unit/infra/test_runbook_store.py` -> `5 passed`; `uv run pytest tests/cli_runtime/test_workflow.py` -> `11 passed`; `uv run pytest tests/cli_runtime/test_workflow_context_routing.py` -> `26 passed`. | passed | Projection errors remain observable via `result.projection.errors` / Markdown `Projection Errors`; they no longer change guidance state. |
| S03 | tc-005 | Provider / installed Issue Planning / Execution Skill tests pass and Skill text uses `guidance <target>` with task checklist registration. | `rg` inspection confirms `guidance issue-planning`, `guidance issue-execution`, task checklist registration, and projection non-authority text; `uv run pytest tests/unit/infra/test_init_update.py -k "issue_skills or guidance or workflow_next"` -> `8 passed`; `uv run pytest tests/cli_runtime/test_wrappers.py` -> `6 passed`. | passed | No additional code changes were required because S01 already updated Skill handoff atomically with command removal. Fresh spec-reviewer re-review passed. |
| S90 | docs / mirror impact | Provider docs / Skill handoff / dogfooding mirror no longer expose `workflow next` as active agent handoff; local dogfooding runtime supports `guidance`. | `uv run spec-dock update .`; `./spec-dock/scripts/spec-dock --help`; `./spec-dock/scripts/spec-dock guidance issue-planning`; `./spec-dock/scripts/spec-dock guidance issue-execution`; `rg` inspection. | passed | Dogfooding mirror includes one pre-existing provider-side context routing update from the source asset; spec-reviewer confirmed it is acceptable mirror parity. |
| S99 | tc-006 | issue-wide tests / docs / specs are integrated and remaining failures are either fixed or recorded with scope. | `tests/unit/infra/test_init_update.py` -> `515 passed`; context/workflow focused suites pass; `tests/cli_runtime/test_workflow.py` -> `11 passed`; changed-file ruff pass; validate pass; diff check pass; final QA/code/spec review pass. | passed | Full `tests/unit tests/cli_runtime` initially failed only on dogfooding meta snapshot drift, then the snapshot failure was fixed and the owning suite passed. Full ruff remains blocked by broader existing lint surface outside changed files. |

## テスト契約の完了証跡（Test Contract Closure）

| closure id / test id | step | required | evidence level | pre-implementation evidence | verification command or path | observed result | notes |
|---|---|---|---|---|---|---|---|
| tc-001 | S01 | yes | red-required | `./spec-dock/scripts/spec-dock guidance issue-planning` -> invalid choice before implementation. | `uv run pytest tests/cli_runtime/test_workflow.py tests/cli_runtime/test_workflow_context_routing.py` | pass: `36 passed`; combined S01 + Skill fix run pass: `38 passed` | Markdown stdout guidance contract covered. |
| tc-002 | S01 | yes | red-required | Existing `workflow next unknown-target --format json` contract was removed; `guidance unknown-target` expected non-zero. | `tests/cli_runtime/test_workflow.py` | pass | Unknown target rejection covered. |
| tc-007 | S01 | yes | red-required | No-active guidance needed to remain available after command rename. | `tests/cli_runtime/test_workflow.py` | pass | `issue-start-required` guidance covered via Markdown command and projection payload inspection. |
| tc-008 | S01 | yes | red-required | Malformed assurance / stale source binding needed to remain fail-closed after command rename. | `tests/cli_runtime/test_workflow.py` | pass | `classification-required` / `authority-invalid` cases covered. |
| tc-003 | S02 | yes | red-required | Updated `test_workflow_next_keeps_guidance_current_when_projection_write_fails` failed because old implementation returned `blocked/runbook-write-failure`. | `tests/unit/infra/test_runbook_store.py` | pass | Projection write failure preserves current guidance state and exposes projection errors. |
| tc-004 | S02 | yes | justified-alternative | Existing runtime already ignored stale projection; added regression to prevent reintroducing stale projection authority. | `tests/cli_runtime/test_workflow.py` | pass | Guidance regenerated from current active issue `iss-00301`, not stale `iss-99999`. |
| tc-009 | S02 | yes | covered-existing | Existing context packet write failure test already asserted `context-packet-write-failure`. | `tests/cli_runtime/test_workflow_context_routing.py` | pass: `26 passed` | Context packet failure remains fail-closed while projection remains best-effort. |
| tc-010 | S02 | yes | red-required | Updated projection tests failed because old projection payload lacked human-only metadata. | `tests/unit/infra/test_runbook_store.py`; `tests/cli_runtime/test_workflow.py` | pass | Projection remains ignored and marks audience=`human`, authority=`non-canonical`, refresh command. |
| tc-005 | S03 | yes | inspect-only | S01 reviewer-directed fix changed Skill handoff before S03 to avoid breaking shipped skills. | `tests/unit/infra/test_init_update.py -k "issue_skills or guidance or workflow_next"`; `tests/cli_runtime/test_wrappers.py`; `rg` inspection | pass | Skill handoff contract is implemented; report closure evidence added after initial S03 spec-reviewer finding and fresh re-review passed. |
| tc-006 | S99 | yes | issue-wide | Full pytest found one dogfooding meta snapshot failure after S90 created/retained new issue meta paths; snapshot was updated. QA P2 stdout assertion gap was also fixed. | `tests/unit/infra/test_init_update.py`; focused workflow/context suites; `tests/cli_runtime/test_workflow.py`; changed-file ruff; validate; diff check | pass | Full `tests/unit tests/cli_runtime` was not fully rerun after snapshot fix because the owning full init-update suite and affected focused suites passed. Final QA/code/spec review passed. |

## クロージャ網羅（Closure Coverage）

| closure id | step | requirement coverage | status | evidence |
|---|---|---|---|---|
| tc-001 | S01 | AC-001, AC-002 | pass | CLI runtime tests, combined S01 focused run, and fresh code-reviewer pass. |
| tc-002 | S01 | EC-002 | pass | CLI runtime unknown target case and fresh code-reviewer pass. |
| tc-007 | S01 | EC-001 | pass | CLI runtime no-active guidance case and fresh code-reviewer pass. |
| tc-008 | S01 | EC-003 | pass | CLI runtime malformed assurance / stale source binding cases and fresh code-reviewer pass. |
| tc-003 | S02 | AC-004 | pass | Unit regression confirms projection write failure does not block current guidance. |
| tc-004 | S02 | AC-007 | pass | CLI regression confirms stale current-runbook projection is ignored. |
| tc-009 | S02 | EC-004 | pass | Context routing suite confirms context packet write failure remains fail-closed. |
| tc-010 | S02 | AC-005 | pass | Unit / CLI tests confirm ignored human projection metadata and no tracked diff. |
| tc-005 | S03 | AC-006 | pass | Skill handoff text and init-update / wrapper tests verify `guidance <target>`, task checklist registration, and projection non-authority wording; fresh spec-reviewer re-review passed. |
| tc-006 | S99 | 全 AC / EC | pass | Issue-wide focused tests, init-update full suite, validate, diff check, changed-file ruff, final QA review, final code review, and final spec review pass. |

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
| S02 | delegated | projection non-blocking / stale projection independence / human-only projection metadata | dev-coder | application workflow; runbook store; presentation; focused tests | Context packet semantics, assurance policy, `workflow next` alias | `5 passed`; `37 passed`; `git diff --check` pass | passed | Human projection warning wording can be final-inspected in S99. | Commit S02, then confirm S03 closure. |
| S03 | approved-no-op | Skill handoff closure confirmation | orchestrator inspection + spec-reviewer | report only; Skill assets already changed in S01 | Runtime behavior changes; new static workflow text; projection authority wording | `8 passed`; `6 passed`; `rg` inspection; `git diff --check` pass | passed | None. | Commit report-only closure, then run S90 docs impact inspection. |
| S90 | delegated-to-command | docs impact and dogfooding mirror refresh | orchestrator + `uv run spec-dock update .` | provider projection heading; dogfooding `.agents/skills`; dogfooding runtime mirror; report | Canonical docs broad rewrite; unrelated manual edits | `update` ok; dogfooding `guidance` ok | passed | mirror includes provider asset parity for context routing classifier from existing provider source | Commit S90, then run final quality gate. |
| S99 | orchestrated | final quality gate and report closeout | orchestrator + final reviewers | report; snapshot test; lint cleanup; stdout assertion test | Feature behavior changes outside issue scope | init-update full pass; focused workflow/context tests pass; `tests/cli_runtime/test_workflow.py` pass; changed-file ruff pass; validate pass; diff check pass; QA/code/spec review pass | passed | Full ruff has broader existing failures outside changed files; full unit/cli pytest was not fully rerun after snapshot fix. | Commit S99 closeout. |

## 委任 worker 証跡（Delegated Worker Evidence）

| step | role | summary | touched surfaces | verification | reviewer outcome | unresolved risk | adoption |
|---|---|---|---|---|---|---|---|
| S01 | dev-coder | Implemented `guidance <target>` and removed `workflow next` primary command. | runtime parser / command / presentation; CLI runtime tests | `uv run pytest tests/cli_runtime/test_workflow.py` -> `10 passed`; `uv run pytest tests/cli_runtime/test_workflow_context_routing.py` -> `26 passed`; `git diff --check` -> pass | initial code-review failed | dogfooding mirror stays stale until update / refresh step | accepted with reviewer-directed follow-up |
| S01 | doc-writer | Updated shipped Issue Planning / Execution Skill handoff to run `guidance issue-planning` / `guidance issue-execution` and register guidance into agent task checklist. | provider Skill assets; focused init-update tests | `uv run pytest tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_skills_provider_assets_are_fixed_guidance_kernels tests/unit/infra/test_init_update.py::TestInitUpdate::test_bundled_skill_routing_contract` -> `2 passed`; combined run -> `38 passed`; `git diff --check` -> pass | fresh code-reviewer re-review passed | none beyond S03 confirmation | accepted |
| S02 | dev-coder | Made runbook projection best-effort for guidance, added human-only projection metadata, and covered stale projection independence. | application workflow; runbook store; presentation; unit / CLI runtime tests | `uv run pytest tests/unit/infra/test_runbook_store.py` -> `5 passed`; `uv run pytest tests/cli_runtime/test_workflow.py tests/cli_runtime/test_workflow_context_routing.py` -> `37 passed`; `git diff --check` -> pass | fresh code-reviewer passed | wording can be final-inspected in S99 | accepted |
| S03 | orchestrator | Confirmed Skill handoff closure as approved-no-op because S01 already made the required atomic Skill asset changes. | report; Skill assets; init-update / wrapper tests | `rg` inspection; `uv run pytest tests/unit/infra/test_init_update.py -k "issue_skills or guidance or workflow_next"` -> `8 passed`; `uv run pytest tests/cli_runtime/test_wrappers.py` -> `6 passed` | fresh spec-reviewer re-review passed | none | accepted |
| S90 | orchestrator | Refreshed dogfooding workspace from provider assets and adjusted projection heading to `Guidance Projection`. | `.agents/skills`; `spec-dock/scripts/spec_dock_runtime`; provider runbook store; report | `uv run spec-dock update .`; dogfooding `--help`; dogfooding `guidance issue-planning`; dogfooding `guidance issue-execution` | fresh spec-reviewer passed | mirror includes pre-existing provider context routing parity update | accepted |
| S99 | orchestrator | Ran final verification, fixed dogfooding meta snapshot drift, cleaned changed-file lint findings, and addressed QA stdout assertion gap. | report; `tests/unit/infra/test_init_update.py`; provider / mirror context packet helpers; `tests/cli_runtime/test_workflow.py` | `tests/unit/infra/test_init_update.py` -> `515 passed`; context/workflow focused suites pass; `tests/cli_runtime/test_workflow.py` -> `11 passed`; changed-file ruff pass; validate pass; diff check pass | final QA/code/spec review passed | full ruff broader existing failures; full unit/cli pytest not rerun after snapshot fix | accepted |

## 親実装例外（Parent Implementation Exception）

なし。S01/S02 implementation は delegated worker に委任し、S03/S90/S99 は report / dogfooding verification / snapshot maintenance の範囲で orchestrator が実施した。

## 最終品質ゲート（Final Quality Gate）

Final QA, code review, and spec review gates passed. S99 is ready to commit.

## 省略/例外メモ

- Pre-S01 `guidance issue-planning` command failure was used only as Red evidence. The implemented command surface is now `guidance <target>`.
- `workflow next` is no longer a primary handoff command and must not be referenced by shipped Issue Planning / Execution Skills except as a negative regression assertion.
