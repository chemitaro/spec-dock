---
種別: 実装報告書（Issue）
ID: "iss-00209"
タイトル: "Improve dependency PlantUML view rendering"
関連GitHub: ["#209"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-19"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00059", "init-local-00003"]
---

# iss-00209 Improve dependency PlantUML view rendering — Planning Report

## 仕様解釈・判断台帳（Spec Interpretation / Decision Ledger）

| ID | Status | Type | Raised By | Gap | Options | Decision | Rationale | Disposition | Evidence | Follow-up |
|---|---|---|---|---|---|---|---|---|---|---|
| D-001 | resolved | scope | user / clarification | Initial issue title was rendering-focused, but rendering and blocker readiness would diverge if fixed separately. | A: scope amendment; B: split issue; C: rendering-only | Adopt Option A: this issue covers readiness authority and PlantUML rendering together. | User explicitly selected Option A and confirmed blocker logic must change. | applied | `discussions/20260619t010926z-interview-dependency-disposition-scope-amendment.md`; `requirement.md`; `design.md`; `plan.md` | none |
| D-002 | resolved | interpretation | user / consultant / orchestrator | GitHub open/closed lifecycle differs from dependency readiness. | lifecycle-only; rendering-only visibility; lifecycle + disposition model | Separate `lifecycle_state` from `dependency_disposition`. | GitHub-open all-descendant-done high-level dependency is satisfied; empty GitHub-open high-level dependency remains blocking. | applied | `discussions/20260619t002902z-research-dependency-plantuml-rendering-clarification.md`; `discussions/20260619t002903z-interview-dependency-plantuml-closed-node-policy.md`; `requirement.md`; `design.md` | none |
| D-003 | resolved | compatibility | design reviewer | `.agent/deps-issues.json` must not lose satisfied-but-not-rendered context. | remove satisfied context; keep active graph only; separate active graph from context list | Keep schema v2 active graph `nodes` / `edges` separate from top-level `dependency_contexts`. | PUML can hide resolved noise while machine consumers still explain readiness. | applied | `design.md`; plan closure `cl-010`; `tc-s03-002` | none |
| D-004 | resolved | implementation | requirement/design/plan review | `deps-raw.puml` is raw direct view but should not become complete audit. | complete raw audit artifact; active raw direct view; readiness view | Keep `deps-raw.puml` as active raw direct visual/debug output; complete audit remains `.meta.json.depends_on` / `.agent/index-all.json`. | User accepted `raw_direct` for deps-raw; adding `deps-raw-all.puml` is out of scope. | applied | `requirement.md`; `design.md`; `plan.md` | none |

## 証跡採用台帳（Evidence Adoption Ledger）

| ID | adoption_status | source | target | rationale | evidence | next_action |
|---|---|---|---|---|---|---|
| EAL-001 | adopted | research | requirement / design / plan | Source-grounded analysis identified rendering, JSON authority, and high-level lifecycle gaps. | `discussions/20260619t002902z-research-dependency-plantuml-rendering-clarification.md` | none |
| EAL-002 | adopted | interview | requirement / design / plan | User accepted Option A visibility semantics for high-level nodes and clarified empty open high-level nodes remain active. | `discussions/20260619t002903z-interview-dependency-plantuml-closed-node-policy.md` | none |
| EAL-003 | adopted | interview | requirement / design / plan | User selected Option A scope amendment: readiness authority and rendering are one coherent issue. | `discussions/20260619t010926z-interview-dependency-disposition-scope-amendment.md` | none |
| EAL-004 | adopted | system-architect draft | design.md | Delegated architecture draft was inspected and integrated into canonical design; canonical `design.md` then passed fresh spec review after fixes. | `discussions/20260619t013310z-draft-design-dependency-disposition-plantuml-rendering.md`; `design.md` | none |
| EAL-005 | adopted | implementation-planner draft | plan.md | Delegated plan draft was inspected and rewritten into canonical executable plan; reviewer findings were fixed until pass. | `discussions/20260619t014201z-draft-plan-dependency-disposition-rendering.md`; `plan.md` | none |
| EAL-006 | adopted | spec-reviewer | requirement.md | Requirement review found closure gaps; fixes added descendant traversal, active raw view wording, and issue-start verification. | requirement review findings; `requirement.md` | none |
| EAL-007 | adopted | spec-reviewer | design.md | Design review found satisfied context would be lost; fix added top-level `dependency_contexts` separate from active graph. | design review findings; `design.md` | none |
| EAL-008 | adopted | spec-reviewer | plan.md | Plan review found executable-plan gaps; fixes added EC-003/EC-002 closure, concrete test cards, delegation contracts, field contracts, no-op gate, final exit contract, and exit-code expectations. | plan review findings; `plan.md` | none |

## 目的整合台帳（Objective Alignment Ledger）

| 対象 | 主要目的の証跡 | 副次要件の証跡 | 逆転リスク | レビュアー判定 |
|---|---|---|---|---|
| iss-00209 planning | `requirement.md` / `design.md` / `plan.md` now define one readiness authority consumed by `deps check`, active guards, JSON, and PlantUML. | PlantUML readability is still covered by active graph filtering, `blocks` labels, package high-level nodes, docs, and manual evidence. | low | requirement/design/plan reviewer gates passed after fixes |

## 仕様 authoring ゲート（Spec Authoring Gate）

| phase | investigated facts | open questions / answers | adoption decision | reviewer verdict | blocking | promotion / next_action |
|---|---|---|---|---|---|---|
| requirement | Active issue docs, reference deps/sync docs, runtime domain/application/presentation code, tests, user feedback, consultant analysis. | Closed/all-done high-level visibility answered in `20260619t002903z`; scope amendment answered in `20260619t010926z`. | adopted into `requirement.md` | passed after fixes; final P2 wording reflected | no | promoted to design |
| design | Reviewed requirement, research/interviews, runtime layer boundaries, JSON/PUML contracts, delegated system-architect draft. | No remaining user interview needed. | adopted into `design.md` | passed after fixing `dependency_contexts` separation | no | promoted to plan |
| plan | Reviewed requirement/design, `phase_plan_issue.md`, `authoring/issue-plan.md`, delegated implementation-planner draft, repeated spec-reviewer findings. | No remaining user interview needed. | adopted into `plan.md` | passed after final exit-code precision re-review | no | ready for issue execution handoff |

## 委任ドラフト証跡（Delegated Draft Evidence）

| created_by_role | scope_id | discussion draft path | source_paths | intended_targets | adoption_status | reflected_to | diff_guard_result | integration result | rejected portions | blockers | reviewer result | promotion decision |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| system-architect | iss-00209 | `discussions/20260619t013310z-draft-design-dependency-disposition-plantuml-rendering.md` | requirement, discussions, runtime source, reference docs | `design.md`, `plan.md`, `report.md` | adopted | `design.md`, `report.md` | `git diff --check` passed after integration | canonical design rewritten by orchestrator | none material | none | design spec-reviewer passed after one fix | promoted to plan |
| implementation-planner | iss-00209 | `discussions/20260619t014201z-draft-plan-dependency-disposition-rendering.md` | requirement, design, workflow/authoring docs, runtime source, discussions | `plan.md`, `report.md` | adopted | `plan.md`, `report.md` | `git diff --check` passed after integration | canonical plan rewritten by orchestrator and reviewer findings applied | draft was compressed and tightened to current plan schema | none | plan spec-reviewer passed after fixes | ready for execution handoff |

## ワークフロー委任同意の証跡（Workflow Delegation Consent）

| consent source | repo/worktree | active issue | session | named roles | boundary | expires / invalidation condition | denied / unavailable reason | next action |
|---|---|---|---|---|---|---|---|---|
| user instruction with `spec-dock-issue-planning` | `/Users/iwasawayuuta/.codex/worktrees/7d89/spec-dock` | iss-00209 | current session | deep-consultant, system-architect, implementation-planner, spec-reviewer | same repo, active issue, read-only/review or scope-local discussion drafts; canonical docs owned by orchestrator | issue completion, scope change, user revocation, host policy conflict | none | proceed to issue execution when user requests |

## Planning Verification

| check | result | evidence |
|---|---|---|
| `git diff --check` after plan fixes | pass | no whitespace errors |
| requirement reviewer gate | pass | requirement reviewer passed after fixes |
| design reviewer gate | pass | design reviewer passed after `dependency_contexts` separation fix |
| plan reviewer gate | pass | final plan reviewer returned `review_status: pass` after P2 exit-code precision was reflected |

## Execution Handoff Readiness

- Requirement, design, and plan are concrete enough to start implementation under `spec-dock-issue-execution`.
- No additional user interview is currently required.
- Implementation must proceed step by step from S01 to S99, with per-step reviewer pass and commit/no-op closure.
- This report currently records planning evidence only. Runtime implementation evidence, test output, reviewer gates, commits, and final closeout evidence must be appended during issue execution.

## 実装記録（セッションログ）

### S01 — Domain Disposition Contract（2026-06-19）

#### 対象
- Step: S01
- AC/EC: AC-001, AC-002, AC-003, AC-006, EC-001, EC-002, EC-003
- Closure IDs: `cl-001`, `cl-002`, `cl-003`, `cl-004`, `cl-021`

#### 実施内容
- `dev-coder` に S01 allowed paths のみを委任した。
- `DepsDependencyContext` / `DepsNodeBlocker` に lifecycle / disposition / basis fields を追加した。
- Domain readiness evaluation で empty open、empty unknown、closed empty、local done、all-descendant-done、unknown descendant を分類するようにした。
- Application / presentation / docs / storage mutation は S01 では変更していない。

#### 実行コマンド / 結果
```bash
uv run pytest tests/unit/domain/test_deps.py
# baseline before S01 worker: 14 passed

uv run pytest tests/unit/domain/test_deps.py
# red evidence from worker after adding S01 assertions before implementation: 6 failed, 9 passed

uv run pytest tests/unit/domain/test_deps.py
# green verification after S01 implementation: 15 passed

git diff --check
# pass
```

#### TDD / Red / Green / Refactor Evidence
| step | phase | planned evidence | observed evidence | method | result | notes |
|---|---|---|---|---|---|---|
| S01 | Red | red-required for `cl-001`, `cl-002`, `cl-003`, `cl-021` | worker reported `6 failed, 9 passed` after adding S01 assertions | `uv run pytest tests/unit/domain/test_deps.py` | pass | failures covered missing lifecycle/disposition fields and unknown descendant context |
| S01 | Green | domain suite passes | `15 passed` | `uv run pytest tests/unit/domain/test_deps.py` | pass | parent re-ran and confirmed |
| S01 | Refactor guard | no broad model rewrite / no storage mutation change | whitespace check clean and changed files limited to S01 allowed paths | `git diff --check`; `git status --short` | pass | application/presentation/docs untouched |
| S01 | Reviewer follow-up Red | code-reviewer P2 closed-source blocker regression | worker reported `1 failed, 15 passed` before fix | `uv run pytest tests/unit/domain/test_deps.py` | pass | closed source issue incorrectly received empty-open node blocker |
| S01 | Reviewer follow-up Green | code-reviewer P2 fix | `16 passed` | `uv run pytest tests/unit/domain/test_deps.py` | pass | parent re-ran and confirmed |
| S01 | Reviewer follow-up Red | code-reviewer P1 open-descendant context gap | worker reported `1 failed, 16 passed` before fix | `uv run pytest tests/unit/domain/test_deps.py` | pass | expanded high-level dependency with open descendant returned no evaluated context |
| S01 | Reviewer follow-up Green | code-reviewer P1 fix | `17 passed` | `uv run pytest tests/unit/domain/test_deps.py` | pass | parent re-ran and confirmed |

#### Implementation Delegation Gate
| step | decision | required reason | delegated role | delegated scope | source of truth | allowed changes | forbidden changes | required verification | stop conditions | output required | observed result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S01 | delegated | runtime/domain behavior step | dev-coder | domain models, domain deps, domain tests | `requirement.md`, `design.md`, `plan.md` S01 | `domain/models.py`, `domain/deps.py`, `tests/unit/domain/test_deps.py` | app/presentation/docs/report/storage mutation | `uv run pytest tests/unit/domain/test_deps.py`; `git diff --check` | storage/schema/app behavior needed | changed files, verification, risks, ledger note | pass; worker reported no material implementation decisions beyond approved plan |

#### Delegated Worker Evidence
| step | delegated role | worker summary | changed files | tests run | reviewer verdict | unresolved risks | parent integration decision |
|---|---|---|---|---|---|---|---|
| S01 | dev-coder | Added lifecycle/disposition/basis fields and domain classification for high-level dependency contexts. | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/models.py`; `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/deps.py`; `tests/unit/domain/test_deps.py` | `uv run pytest tests/unit/domain/test_deps.py` -> 15 passed; `git diff --check` -> pass | code-reviewer pass with P2 follow-up | S03 may project fields into JSON; application/presentation intentionally untouched | accepted with bounded P2 follow-up |
| S01 | dev-coder | Fixed code-reviewer P2 so closed source issues skip high-level node blockers. | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/deps.py`; `tests/unit/domain/test_deps.py` | `uv run pytest tests/unit/domain/test_deps.py` -> 16 passed; `git diff --check` -> pass | pending final code-reviewer | S02+ still out of scope | accepted for re-review |
| S01 | dev-coder | Fixed code-reviewer P1 so open descendant high-level dependency emits blocking evaluated context. | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/deps.py`; `tests/unit/domain/test_deps.py` | `uv run pytest tests/unit/domain/test_deps.py` -> 17 passed; `git diff --check` -> pass | pending final code-reviewer | S02+ still out of scope | accepted for re-review |

#### Step Contract Closure
| step | closure ids | close condition from plan | observed evidence | result | notes |
|---|---|---|---|---|---|
| S01 | `cl-001` | empty open high-level dependency is blocking | test asserts node blocker `dependency_disposition=blocking`, `disposition_basis=empty_open_container` | pass | `tests/unit/domain/test_deps.py` |
| S01 | `cl-002` | GitHub-open all-done high-level dependency is satisfied | test asserts satisfied context `dependency_disposition=satisfied`, `disposition_basis=all_descendant_issues_done` | pass | full graph descendant done case |
| S01 | `cl-003` | unknown high-level/descendant state fails closed | tests assert empty unknown blocker and unknown descendant `dependency_disposition=indeterminate` with basis | pass | `empty_unknown_container` / `descendant_issue_unknown` |
| S01 | `cl-004` | raw storage/mutation rules unchanged | existing domain suite remains green | pass | no storage/mutation code changed |
| S01 | `cl-021` | closed empty high-level dependency is satisfied | test asserts `dependency_disposition=satisfied`, `disposition_basis=lifecycle_closed` | pass | closed empty parent case |

#### Test Contract Closure
| closure id / test id | step | required | evidence level | pre-implementation evidence | verification command | observed result | notes |
|---|---|---|---|---|---|---|---|
| `tc-s01-001` / `cl-001` | S01 | yes | red-required | worker red run failed before implementation | `uv run pytest tests/unit/domain/test_deps.py` | pass | empty open high-level blocker |
| `tc-s01-002` / `cl-002` | S01 | yes | red-required | worker red run failed before implementation | `uv run pytest tests/unit/domain/test_deps.py` | pass | open all-done high-level satisfied |
| `tc-s01-003` / `cl-003` | S01 | yes | red-required | worker red run failed before implementation | `uv run pytest tests/unit/domain/test_deps.py` | pass | unknown states indeterminate |
| `tc-s01-004` / `cl-021` | S01 | yes | red-required | worker red run failed before implementation | `uv run pytest tests/unit/domain/test_deps.py` | pass | closed empty high-level satisfied |
| `tc-s01-005` / `cl-004` | S01 | yes | covered-existing | baseline domain suite passed before S01 | `uv run pytest tests/unit/domain/test_deps.py` | pass | raw dependency behavior unchanged |
| reviewer P2 / `cl-021` | S01 | yes | red-required follow-up | worker red run: `1 failed, 15 passed` | `uv run pytest tests/unit/domain/test_deps.py` | pass | closed source issue no longer receives empty-open node blocker |
| reviewer P1 / `cl-003` | S01 | yes | red-required follow-up | worker red run: `1 failed, 16 passed` | `uv run pytest tests/unit/domain/test_deps.py` | pass | open descendant high-level dependency emits `dependency_disposition=blocking`, `disposition_basis=descendant_issue_open` |

#### Reviewer Gate Status
| step | gate name | reviewer role | freshness | state | risk acceptance | promotion / completion decision | notes |
|---|---|---|---|---|---|---|---|
| S01 | step reviewer | code-reviewer | stale after follow-up | passed | N/A | re-review required | first reviewer pass had P2, bounded fix applied |
| S01 | step reviewer re-review | code-reviewer | stale after follow-up | failed | N/A | re-review required | second reviewer found P1 open-descendant context gap |
| S01 | step reviewer final re-review | code-reviewer | fresh | passed | N/A | proceed to S01 commit gate | no findings |

#### Step Commit Gate
| step | closure state | commit scope | commit hash / final ledger | post-commit clean check | no-op rationale | no-op checked contracts / files | no-op diff-clean command | no-op read-only confirmation |
|---|---|---|---|---|---|---|---|---|
| S01 | committed | domain disposition implementation and S01 report evidence | `95be339c` | clean | N/A | N/A | N/A | N/A |

### S02 — Application Readiness Consumers（2026-06-19）

#### 対象
- Step: S02
- AC/EC: AC-001, AC-002, AC-003, AC-006, EC-001, EC-002, EC-003
- Closure IDs: `cl-005`, `cl-006`, `cl-007`, `cl-008`, `cl-022`, `cl-023`

#### 実施内容
- `dev-coder` に S02 allowed paths のみを委任した。
- Application readiness result が保持する `dependency_disposition` / `disposition_basis` を `deps check` application tests で明示的に固定した。
- `active set` の high-level node blocker エラーに disposition / basis を含め、empty open high-level blocker の理由を確認できるようにした。
- GitHub-open high-level dependency でも descendant issues が all done の場合、`deps check` / `active set` が ready と判断することを application tests で固定した。
- `deps check --json` の field exposure は S03 の Presentation JSON Contract の責務として維持し、S02 では presentation serializer を変更していない。

#### 実行コマンド / 結果
```bash
uv run pytest tests/unit/application/test_check_deps.py tests/unit/application/test_set_active.py
# baseline before S02 worker: 21 passed

uv run pytest tests/unit/application/test_set_active.py -k 'high_level_node_blocker or all_descendants_done'
# red evidence from worker: 1 failed, 1 passed

uv run pytest tests/unit/application/test_check_deps.py tests/unit/application/test_set_active.py
# green verification after S02 implementation: 23 passed

uv run pytest tests/cli_runtime/test_deps.py -k 'empty_open_high_level_dependency or empty_closed_epic_context'
# focused CLI regression: 1 passed, 107 deselected

uv run pytest tests/cli_runtime/test_issue_lifecycle.py
# lifecycle CLI regression: 28 passed

git diff --check
# pass
```

#### TDD / Red / Green / Refactor Evidence
| step | phase | planned evidence | observed evidence | method | result | notes |
|---|---|---|---|---|---|---|
| S02 | Red | red-required for `cl-006` guard observability | worker reported `1 failed, 1 passed` before error message included disposition/basis | `uv run pytest tests/unit/application/test_set_active.py -k 'high_level_node_blocker or all_descendants_done'` | pass | empty open blocker existed but error did not expose disposition/basis |
| S02 | Alternative Red | JSON field exposure belongs to S03 | worker observed focused CLI JSON assertion failed because `presentation/json_state.py` drops disposition fields | `uv run pytest tests/cli_runtime/test_deps.py -k 'empty_open_high_level_dependency or empty_closed_epic_context'` | pass | S02 did not expand into presentation layer; S03 keeps `cl-009` |
| S02 | Green | application readiness consumers agree on disposition | `23 passed` | `uv run pytest tests/unit/application/test_check_deps.py tests/unit/application/test_set_active.py` | pass | parent re-ran and confirmed |
| S02 | Green | issue lifecycle guard regressions remain green | `28 passed` | `uv run pytest tests/cli_runtime/test_issue_lifecycle.py` | pass | parent re-ran and confirmed |
| S02 | Focused CLI regression | existing deps high-level open/closed CLI behavior remains green | `1 passed, 107 deselected` | `uv run pytest tests/cli_runtime/test_deps.py -k 'empty_open_high_level_dependency or empty_closed_epic_context'` | pass | full `test_deps.py` is very slow in this environment |
| S02 | Refactor guard | no presentation/storage mutation change | whitespace check clean and changed files limited to S02 application/test paths | `git diff --check`; `git diff --stat` | pass | presentation JSON deferred to S03 |

#### Implementation Delegation Gate
| step | decision | required reason | delegated role | delegated scope | source of truth | allowed changes | forbidden changes | required verification | stop conditions | output required | observed result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S02 | delegated | runtime/application readiness behavior step | dev-coder | application readiness consumers and application/CLI tests | `requirement.md`, `design.md`, `plan.md` S02 | `application/check_deps.py`, `application/set_active.py`, `application/sync_state.py`, application/CLI tests | presentation rendering/JSON formatting, docs, storage mutation, new CLI flags | S02 unit/CLI commands and `git diff --check` | new option, force behavior change, persistence/schema change | changed files, verification, risks, ledger note | partial pass; parent kept S02 scoped to application and deferred JSON field exposure to S03 |

#### Delegated Worker Evidence
| step | delegated role | worker summary | changed files | tests run | reviewer verdict | unresolved risks | parent integration decision |
|---|---|---|---|---|---|---|---|
| S02 | dev-coder | Added application assertions for disposition/basis and active-set guard message details; identified presentation JSON field exposure belongs to `presentation/json_state.py`. | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/set_active.py`; `tests/unit/application/test_check_deps.py`; `tests/unit/application/test_set_active.py`; `tests/cli_runtime/test_deps.py` | application suite -> 23 passed; lifecycle CLI -> 28 passed; `git diff --check` -> pass; focused CLI JSON assertion exposed S03 gap | pending code-reviewer re-review | full `tests/cli_runtime/test_deps.py` too slow for routine S02 gate; JSON field exposure remains S03 | accepted after removing S03-owned JSON field assertions from S02 diff |

#### Step Contract Closure
| step | closure ids | close condition from plan | observed evidence | result | notes |
|---|---|---|---|---|---|
| S02 | `cl-005` | `deps check --json` reports ready satisfied context | application check now asserts GitHub-open parent with all descendants done is ready and has satisfied context | pass | machine-readable additional fields remain S03 `cl-009` |
| S02 | `cl-006` | `active set` / `issue start` reject empty open blocker | `active set` rejects empty open high-level blocker and reports `dependency_disposition=blocking`, `disposition_basis=empty_open_container` | pass | issue-start shares readiness guard via lifecycle path covered by `test_issue_lifecycle.py` |
| S02 | `cl-007` | descendant count uses full graph | application check asserts expanded parent dependency with done descendants is not treated as empty | pass | protects todo-projection false empty case |
| S02 | `cl-022` | commands do not block on closed empty high-level dependency | application check and focused CLI deps test confirm closed empty parent is satisfied | pass | no presentation fields required in S02 |
| S02 | `cl-023` | commands fail closed on unknown high-level or descendant state | application check asserts unknown empty high-level context remains `indeterminate` / `empty_unknown_container` | pass | unknown descendant domain branch covered by S01 |
| S02 | `cl-008` | mutation CLI behavior unchanged | focused deps CLI regression and lifecycle CLI suite remain green; no mutation/storage files changed | pass | full `test_deps.py` omitted due known runtime slowness |

#### Test Contract Closure
| closure id / test id | step | required | evidence level | pre-implementation evidence | verification command | observed result | notes |
|---|---|---|---|---|---|---|---|
| `tc-s02-001` / `cl-005` | S02 | yes | red-required | worker added application readiness coverage | `uv run pytest tests/unit/application/test_check_deps.py tests/unit/application/test_set_active.py` | pass | open all-done high-level dependency ready |
| `tc-s02-002` / `cl-006` | S02 | yes | red-required | worker red run showed missing guard message fields | `uv run pytest tests/unit/application/test_check_deps.py tests/unit/application/test_set_active.py` | pass | empty open blocker rejected and explained |
| `tc-s02-003` / `cl-007` | S02 | yes | red-required | worker added application assertion against false empty parent | `uv run pytest tests/unit/application/test_check_deps.py tests/unit/application/test_set_active.py` | pass | full graph descendants counted |
| `tc-s02-004` / `cl-022` | S02 | yes | red-required | existing S01 semantics projected into application test | `uv run pytest tests/cli_runtime/test_deps.py -k 'empty_open_high_level_dependency or empty_closed_epic_context'` | pass | closed empty high-level dependency does not block |
| `tc-s02-005` / `cl-008` | S02 | yes | covered-existing | baseline lifecycle CLI passed before S02 | `uv run pytest tests/cli_runtime/test_issue_lifecycle.py` | pass | no force/bypass lifecycle regression observed |
| `tc-s02-006` / `cl-023` | S02 | yes | red-required | worker added/strengthened indeterminate field assertions | `uv run pytest tests/unit/application/test_check_deps.py tests/unit/application/test_set_active.py` | pass | unknown high-level context fails closed |

#### Reviewer Gate Status
| step | gate name | reviewer role | freshness | state | risk acceptance | promotion / completion decision | notes |
|---|---|---|---|---|---|---|---|
| S02 | step reviewer | code-reviewer | stale after report update | failed | N/A | re-review required | first reviewer found missing S02 report evidence |
| S02 | step reviewer re-review | code-reviewer | fresh | passed | N/A | proceed to S02 commit gate | no findings |

#### Step Commit Gate
| step | closure state | commit scope | commit hash / final ledger | post-commit clean check | no-op rationale | no-op checked contracts / files | no-op diff-clean command | no-op read-only confirmation |
|---|---|---|---|---|---|---|---|---|
| S02 | committed | application readiness consumers and S02 report evidence | `ac917309` | clean | N/A | N/A | N/A | N/A |

### S03 — Presentation JSON Contract（2026-06-19）

#### 対象
- Step: S03
- AC/EC: AC-003, AC-004, AC-006, EC-004
- Closure IDs: `cl-009`, `cl-010`, `cl-011`

#### 実施内容
- `dev-coder` に S03 allowed paths のみを委任した。
- `deps check --json` の `node_blockers` / `satisfied_dependencies` に `lifecycle_state`, `lifecycle_source`, `dependency_disposition`, `disposition_basis` を additive に追加した。
- `.agent/deps-issues.json` に top-level `dependency_contexts` を追加し、active `nodes` / `edges` と evaluated dependency context を分離した。
- satisfied-only high-level context は active graph noise として `nodes` / `edges` に出さず、`dependency_contexts` に保持するようにした。
- inherited high-level blocker の raw 宣言元を失わないよう、`dependency_contexts_by_issue_id` の `source_node_id` を合成 blocker context より優先した。
- `schema_version: 2` と既存 JSON keys は維持した。

#### 実行コマンド / 結果
```bash
uv run pytest tests/unit/presentation/test_runtime_sync_s07.py -k deps_issues_does_not_include_historical_satisfied_high_level_context
# red evidence from worker: failed with KeyError: 'dependency_contexts'

uv run pytest tests/unit/presentation/test_runtime_sync_s07.py -k 'deps_issues or deps_check_json'
# green verification after S03 implementation and follow-up: 2 passed, 56 deselected

uv run python -m py_compile src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/json_state.py
# pass

git diff --check
# pass
```

#### 未完了 / 代替検証
- `uv run pytest tests/cli_runtime/test_deps.py::TestCliDeps::test_deps_check_json_reports_empty_open_epic_as_node_blocker tests/cli_runtime/test_deps.py::TestCliDeps::test_deps_check_json_exits_zero_for_empty_closed_epic_context`
  - selected 2 tests but no tests completed after about 4m47s; interrupted.
- `uv run pytest tests/cli_runtime/test_sync.py -k 'sync_deps_issues_marks_empty_closed_epic_dependency_satisfied or records_all_done_expanded_high_level_dependency_as_satisfied'`
  - selected 2 tests but did not complete after about 4m48s; interrupted.
- CLI JSON expectations were updated in allowed test files, but local CLI runtime slowness prevented green confirmation. `render_deps_check_json()` and `render_deps_issues_artifact()` are covered directly by presentation unit tests instead.

#### TDD / Red / Green / Refactor Evidence
| step | phase | planned evidence | observed evidence | method | result | notes |
|---|---|---|---|---|---|---|
| S03 | Red | red-required for `cl-010` top-level `dependency_contexts` | worker reported `KeyError: 'dependency_contexts'` before implementation | `uv run pytest tests/unit/presentation/test_runtime_sync_s07.py -k deps_issues_does_not_include_historical_satisfied_high_level_context` | pass | `.agent/deps-issues.json` lacked separated context list |
| S03 | Alternative Red | `cl-009` was missing after S02 | S02 worker observed `deps check --json` dropped disposition/basis fields in presentation serializer | focused CLI JSON assertion during S02/S03 handoff | pass | S03 owns presentation serializer |
| S03 | Green | JSON projection exposes lifecycle/disposition and separates active graph/context | `2 passed, 56 deselected` | `uv run pytest tests/unit/presentation/test_runtime_sync_s07.py -k 'deps_issues or deps_check_json'` | pass | direct serializer coverage for `render_deps_check_json()` and `render_deps_issues_artifact()` |
| S03 | Green | serializer syntax remains valid | no output | `uv run python -m py_compile src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/json_state.py` | pass | syntax check |
| S03 | Refactor guard | additive fields only / schema v2 unchanged | whitespace clean and changed files limited to S03 allowed paths plus report evidence | `git diff --check`; `git diff --stat` | pass | no domain/application changes |

#### Implementation Delegation Gate
| step | decision | required reason | delegated role | delegated scope | source of truth | allowed changes | forbidden changes | required verification | stop conditions | output required | observed result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S03 | delegated | runtime/presentation JSON contract step | dev-coder | JSON projection and JSON tests | `requirement.md`, `design.md`, `plan.md` S03 | `presentation/json_state.py`, presentation/CLI JSON tests | PUML renderer, schema version bump, existing key removal, domain/application behavior | S03 JSON commands and `git diff --check` | schema bump or existing key removal needed | changed files, JSON before/after, verification, risks | pass with parent follow-up for stable unit coverage and reviewer P2 fix |

#### Delegated Worker Evidence
| step | delegated role | worker summary | changed files | tests run | reviewer verdict | unresolved risks | parent integration decision |
|---|---|---|---|---|---|---|---|
| S03 | dev-coder | Added additive lifecycle/disposition JSON fields and top-level `dependency_contexts`; moved satisfied-only high-level context out of active graph. | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/json_state.py`; `tests/unit/presentation/test_runtime_sync_s07.py`; `tests/cli_runtime/test_sync.py`; `tests/cli_runtime/test_deps.py` | unit `-k deps_issues` -> 1 passed; py_compile -> pass; `git diff --check` -> pass; CLI focused tests did not complete | initial code-reviewer failed with P1 report evidence and P2 provenance issue | CLI runtime focused tests too slow locally | accepted with parent follow-up |
| S03 | dev-coder follow-up | Added direct `render_deps_check_json()` unit coverage for lifecycle/disposition fields. | `tests/unit/presentation/test_runtime_sync_s07.py` | `uv run pytest tests/unit/presentation/test_runtime_sync_s07.py -k 'deps_issues or deps_check_json'` -> 2 passed; py_compile -> pass; `git diff --check` -> pass | pending re-review | CLI runtime still not green-confirmed locally | accepted |
| S03 | parent follow-up | Fixed reviewer P2 by preserving original `dependency_contexts_by_issue_id` provenance before synthetic node blocker context fallback. | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/json_state.py`; `tests/unit/presentation/test_runtime_sync_s07.py` | `uv run pytest tests/unit/presentation/test_runtime_sync_s07.py -k 'deps_issues or deps_check_json'` -> 2 passed; py_compile -> pass; `git diff --check` -> pass | stale after follow-up | none beyond CLI runtime slowness | accepted for re-review |
| S03 | parent follow-up | Fixed reviewer P1 by deduplicating raw and evaluated dependency contexts on source issue / target node / expansion and merging evaluated lifecycle/disposition into the raw-provenance entry. | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/json_state.py`; `tests/unit/presentation/test_runtime_sync_s07.py` | `uv run pytest tests/unit/presentation/test_runtime_sync_s07.py -k 'deps_issues or deps_check_json'` -> 2 passed; py_compile -> pass; `git diff --check` -> pass | pending re-review | none beyond CLI runtime slowness | accepted for re-review |
| S03 | parent follow-up | Fixed reviewer P1 by removing satisfied direct issue dependency edges from the active graph while keeping the evaluated direct issue context in top-level `dependency_contexts`. | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/json_state.py`; `tests/unit/presentation/test_runtime_sync_s07.py`; `tests/cli_runtime/test_sync.py` | `uv run pytest tests/unit/presentation/test_runtime_sync_s07.py -k 'deps_issues or deps_check_json'` -> 2 passed; py_compile -> pass; `git diff --check` -> pass | pending re-review | CLI runtime focused test still not green-confirmed locally | accepted for re-review |
| S03 | parent follow-up | Fixed reviewer P1 by enriching raw direct issue satisfied contexts with lifecycle/disposition fields before serializing top-level `dependency_contexts`. | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/json_state.py`; `tests/unit/presentation/test_runtime_sync_s07.py` | `uv run pytest tests/unit/presentation/test_runtime_sync_s07.py -k 'deps_issues or deps_check_json'` -> 2 passed; py_compile -> pass; `git diff --check` -> pass | pending re-review | CLI runtime focused test still not green-confirmed locally | accepted for re-review |

#### Step Contract Closure
| step | closure ids | close condition from plan | observed evidence | result | notes |
|---|---|---|---|---|---|
| S03 | `cl-009` | `deps check --json` includes lifecycle and disposition context | direct `render_deps_check_json()` unit test asserts lifecycle/disposition fields for node blockers and satisfied dependencies | pass | CLI runtime test updated but not green-confirmed due local hang |
| S03 | `cl-010` | active graph and dependency contexts are separated | `render_deps_issues_artifact()` unit test asserts active graph omits satisfied-only context while top-level `dependency_contexts` preserves it | pass | blocker context provenance also covered |
| S03 | `cl-011` | schema v2 keys remain compatible | direct unit tests assert `schema_version == 2`; implementation keeps existing top-level keys and only adds fields | pass | no schema bump |

#### Test Contract Closure
| closure id / test id | step | required | evidence level | pre-implementation evidence | verification command | observed result | notes |
|---|---|---|---|---|---|---|---|
| `tc-s03-001` / `cl-009` | S03 | yes | red-required | S02/S03 handoff observed serializer dropped disposition fields | `uv run pytest tests/unit/presentation/test_runtime_sync_s07.py -k 'deps_issues or deps_check_json'` | pass | `render_deps_check_json()` direct unit |
| `tc-s03-002` / `cl-010` | S03 | yes | red-required | worker red run got missing `dependency_contexts` | `uv run pytest tests/unit/presentation/test_runtime_sync_s07.py -k 'deps_issues or deps_check_json'` | pass | active graph / top-level context separation |
| `tc-s03-003` / `cl-011` | S03 | yes | covered-existing | existing schema v2 tests existed before S03 | `uv run pytest tests/unit/presentation/test_runtime_sync_s07.py -k 'deps_issues or deps_check_json'`; `py_compile` | pass | additive fields only |

#### Reviewer Gate Status
| step | gate name | reviewer role | freshness | state | risk acceptance | promotion / completion decision | notes |
|---|---|---|---|---|---|---|---|
| S03 | step reviewer | code-reviewer | stale after follow-up | failed | N/A | re-review required | first reviewer found missing report evidence and blocker provenance issue |
| S03 | step reviewer re-review | code-reviewer | stale after follow-up | failed | N/A | re-review required | second reviewer found raw/evaluated dependency context duplication |
| S03 | step reviewer final re-review | code-reviewer | stale after follow-up | failed | N/A | re-review required | third reviewer found satisfied direct issue dependency still rendered in active graph |
| S03 | step reviewer fourth re-review | code-reviewer | stale after follow-up | failed | N/A | re-review required | fourth reviewer found direct issue satisfied context lost evaluated lifecycle/disposition after edge removal |
| S03 | step reviewer fifth re-review | code-reviewer | fresh | passed | accepted P2 provenance edge-case follow-up | proceed to S03 commit gate | only P2 finding: same issue/target/expansion declarations with different `source_node_id` can be collapsed |

#### Step Commit Gate
| step | closure state | commit scope | commit hash / final ledger | post-commit clean check | no-op rationale | no-op checked contracts / files | no-op diff-clean command | no-op read-only confirmation |
|---|---|---|---|---|---|---|---|---|
| S03 | committed | presentation JSON contract and S03 report evidence | `17f43501` | clean | N/A | N/A | N/A | N/A |

### S04 — PlantUML Rendering（2026-06-19）

#### 対象
- Step: S04
- AC/EC: AC-001, AC-004, AC-005, AC-006, EC-004
- Closure IDs: `cl-012`, `cl-013`, `cl-014`, `cl-015`

#### 実施内容
- `dev-coder` に S04 allowed paths のみを委任した。
- `deps-issues.puml` は active graph の blocking edge のみを描画し、edge label を `blocks` に統一した。
- `deps-issues.puml` から user-facing な `raw_direct` / `satisfied edge` 表記を除外した。
- `deps-raw.puml` は active raw direct view として、active な raw dependency edge だけを `raw_direct` で描画するようにした。
- done/closed issue、高水準 closed/done endpoint、evaluated context が `satisfied` の high-level dependency edge は `deps-raw.puml` から除外した。
- high-level node の package 表現は維持した。

#### 実行コマンド / 結果
```bash
uv run pytest tests/unit/presentation/test_runtime_sync_s07.py tests/unit/presentation/test_deps_raw_puml.py
# green verification after S04 implementation: 69 passed

uv run pytest tests/cli_runtime/test_sync.py::TestCliSync::test_sync_emits_deps_issues_json_and_puml_todo_only -q
# exact CLI PUML smoke: 1 passed

git diff --check
# pass
```

#### 未完了 / 代替検証
- `uv run pytest tests/cli_runtime/test_sync.py -k deps_issues`
  - worker reported 4 selected tests but no progress; interrupted after about 137s.
- `uv run pytest tests/cli_runtime/test_sync.py::TestCliSync::test_sync_deps_issues_marks_empty_closed_epic_dependency_satisfied`
  - worker reported `sync --github` subprocess stalled and was interrupted after about 97s.
- The exact non-hanging CLI PUML smoke plus presentation unit lane were used as S04 automated evidence. Manual mixed-state evidence remains S90/S04-manual follow-up for `cl-015`.
- A final parent re-run of the same exact CLI smoke stalled before any test ran and was interrupted after about 136s; the earlier exact run remains the available CLI green evidence for S04.

#### TDD / Red / Green / Refactor Evidence
| step | phase | planned evidence | observed evidence | method | result | notes |
|---|---|---|---|---|---|---|
| S04 | Red | `deps-issues.puml` should not surface `raw_direct` in readiness view | worker reported focused test failed before implementation because PUML emitted `blocks (raw_direct)` | focused PUML assertion | pass | fixed to `blocks` only |
| S04 | Red | `deps-raw.puml` should omit done/resolved-only noise | worker reported focused test failed before implementation because done prerequisite issue and raw edge rendered | focused raw PUML assertion | pass | fixed active raw filtering |
| S04 | Green | PUML presentation lane passes | `71 passed` | `uv run pytest tests/unit/presentation/test_runtime_sync_s07.py tests/unit/presentation/test_deps_raw_puml.py` | pass | parent re-ran and confirmed after reviewer P1 fixes |
| S04 | Green | CLI PUML smoke passes | `1 passed` | `uv run pytest tests/cli_runtime/test_sync.py::TestCliSync::test_sync_emits_deps_issues_json_and_puml_todo_only -q` | pass | parent re-ran and confirmed |
| S04 | Refactor guard | no domain/application readiness change | whitespace check clean and changed files limited to S04 allowed paths plus report evidence | `git diff --check`; `git diff --stat` | pass | JSON filtering only for PUML/raw payload generation |

#### Implementation Delegation Gate
| step | decision | required reason | delegated role | delegated scope | source of truth | allowed changes | forbidden changes | required verification | stop conditions | output required | observed result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S04 | delegated | runtime/presentation PUML rendering step | dev-coder | PUML renderer, minimal JSON filtering, PUML tests | `requirement.md`, `design.md`, `plan.md` S04 | `presentation/puml.py`, `presentation/json_state.py` for PUML payload filtering, presentation/CLI sync tests | domain/application readiness, schema version, new raw-all artifact, docs | S04 unit/CLI commands and `git diff --check` | new UX rule or artifact needed | changed files, generated PUML observations, verification, risks | pass with CLI lane limitation recorded |

#### Delegated Worker Evidence
| step | delegated role | worker summary | changed files | tests run | reviewer verdict | unresolved risks | parent integration decision |
|---|---|---|---|---|---|---|---|
| S04 | dev-coder | Updated deps-issues PUML to show blocking edges as `blocks` only and filtered deps-raw active raw view to omit done/closed/satisfied-only noise. | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/puml.py`; `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/json_state.py`; `tests/unit/presentation/test_runtime_sync_s07.py`; `tests/unit/presentation/test_deps_raw_puml.py`; `tests/cli_runtime/test_sync.py` | presentation lane -> 69 passed; exact CLI smoke -> 1 passed; `git diff --check` -> pass | pending code-reviewer | full `test_sync.py -k deps_issues` slow/hanging locally; manual evidence remains S90 | accepted for review |
| S04 | parent follow-up | Fixed reviewer P1 so satisfied high-level raw dependencies declared on epic/initiative source nodes are filtered using descendant dependency contexts. | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/json_state.py`; `tests/unit/presentation/test_deps_raw_puml.py` | presentation lane -> 70 passed; exact CLI smoke -> 1 passed; `git diff --check` -> pass | pending re-review | full `test_sync.py -k deps_issues` slow/hanging locally; manual evidence remains S90 | accepted for re-review |
| S04 | parent follow-up | Fixed reviewer P1 using the actual sync data flow by scanning evaluated satisfied contexts across descendant issue evaluations when filtering high-level raw source edges. | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/json_state.py`; `tests/unit/presentation/test_deps_raw_puml.py` | presentation lane -> 71 passed; exact CLI smoke -> 1 passed; `git diff --check` -> pass | pending re-review | full `test_sync.py -k deps_issues` slow/hanging locally; manual evidence remains S90 | accepted for re-review |

#### Step Contract Closure
| step | closure ids | close condition from plan | observed evidence | result | notes |
|---|---|---|---|---|---|
| S04 | `cl-012` | `deps-issues.puml` omits satisfied-only context | presentation tests assert satisfied-only nodes/edges and `satisfied edge` legend are absent from readiness PUML | pass | S03 JSON context remains machine-readable |
| S04 | `cl-013` | active blockers render with `blocks` | presentation/CLI tests assert blocking edge renders as `blocks` and `raw_direct` is absent from deps-issues PUML | pass | active empty-open blockers remain visible |
| S04 | `cl-014` | `deps-raw.puml` is active raw direct view | raw PUML tests assert active raw edges use `raw_direct`, high-level nodes are packages, and done/satisfied-only noise is omitted | pass | no new raw-all artifact |
| S04 | `cl-015` | realistic mixed-state PlantUML remains visually usable | automated PUML evidence is present; manual mixed-state evidence is deferred to S90/manual | pending | manual-required closure not fully closed until S90 |

#### Test Contract Closure
| closure id / test id | step | required | evidence level | pre-implementation evidence | verification command | observed result | notes |
|---|---|---|---|---|---|---|---|
| `tc-s04-001` / `cl-012` | S04 | yes | red-required | worker reported failing assertion before implementation | `uv run pytest tests/unit/presentation/test_runtime_sync_s07.py tests/unit/presentation/test_deps_raw_puml.py` | pass | satisfied-only readiness graph noise removed |
| `tc-s04-002` / `cl-013` | S04 | yes | red-required | worker reported readiness PUML exposed `raw_direct` before implementation | `uv run pytest tests/unit/presentation/test_runtime_sync_s07.py tests/unit/presentation/test_deps_raw_puml.py`; exact CLI smoke | pass | `blocks` label only |
| `tc-s04-003` / `cl-014` | S04 | yes | red-required | worker reported raw PUML rendered done prerequisite before implementation | `uv run pytest tests/unit/presentation/test_deps_raw_puml.py` | pass | active raw direct view |
| `tc-s04-004` / `cl-015` | S04 | yes | manual-required | not applicable | S90/manual fixture pending | pending | manual evidence required before final closeout |

#### Reviewer Gate Status
| step | gate name | reviewer role | freshness | state | risk acceptance | promotion / completion decision | notes |
|---|---|---|---|---|---|---|---|
| S04 | step reviewer | code-reviewer | stale after follow-up | failed | N/A | re-review required | reviewer found satisfied high-level raw dependencies declared on epic/initiative source nodes were not filtered |
| S04 | step reviewer re-review | code-reviewer | stale after follow-up | failed | N/A | re-review required | reviewer found high-level raw source filtering did not scan evaluated contexts across descendant issue evaluations |
| S04 | step reviewer final re-review | code-reviewer | fresh | passed | N/A | proceed to S04 commit gate | no findings |

#### Step Commit Gate
| step | closure state | commit scope | commit hash / final ledger | post-commit clean check | no-op rationale | no-op checked contracts / files | no-op diff-clean command | no-op read-only confirmation |
|---|---|---|---|---|---|---|---|---|
| S04 | committed | PlantUML rendering and S04 report evidence | `d122e983` | clean | N/A | N/A | N/A | N/A |

### S90 — Docs / Manual Verification（2026-06-19）

#### 対象
- Step: S90
- AC/EC: AC-001, AC-002, AC-003, AC-004, AC-005, AC-006, EC-001, EC-002, EC-003, EC-004
- Closure IDs: `cl-015`, `cl-016`, `cl-017`

#### 実施内容
- `doc-writer` に S90 allowed paths のみを委任した。
- provider docs と dogfooding docs に lifecycle fact と dependency disposition の違いを明記した。
- high-level dependency の empty open / open all-descendant-done / closed / unknown 判定表を `reference_deps.md` に追加した。
- `deps-issues.*` が readiness / blocker authority、`deps-raw.puml` が active raw direct visual/debug artifact であることを docs に明記した。
- `manual-tests/iss-00209-dependency-view/` に deterministic fake GitHub を使う realistic manual fixture を作成した。
- manual evidence では `dependency_contexts` に satisfied high-level context が残り、`deps-issues.puml` / `deps-raw.puml` から satisfied-only high-level noise が省かれることを確認した。
- spec-reviewer P1 を受け、empty unknown high-level dependency の fail-closed manual case（`iss-01942 -> epic-01941`）を追加した。

#### 実行コマンド / 結果
```bash
cmp -s src/spec_dock/assets/spec_dock/docs/reference_deps.md spec-dock/docs/reference_deps.md
# pass

cmp -s src/spec_dock/assets/spec_dock/docs/reference_sync.md spec-dock/docs/reference_sync.md
# pass

uv run pytest tests/unit/presentation/test_runtime_sync_s07.py tests/unit/presentation/test_deps_raw_puml.py
# 71 passed

./capture_evidence.py
# sync-github: exit=0
# deps-check-ready-iss-01940-github: exit=0
# deps-check-blocked-iss-01933-github: exit=3
# deps-check-blocked-iss-01933-no-github: exit=3
# deps-check-unknown-iss-01942-github: exit=3
# verifier: exit=0

./verify_projection.py
# RESULT PASS

git diff --check
# pass
```

#### Manual Evidence
| artifact | path | result |
|---|---|---|
| test plan | `manual-tests/iss-00209-dependency-view/test-plan.md` | PASS |
| progress log | `manual-tests/iss-00209-dependency-view/progress-log.md` | PASS |
| summary report | `manual-tests/iss-00209-dependency-view/summary-report.md` | PASS |
| generated JSON evidence | `manual-tests/iss-00209-dependency-view/evidence/.agent__deps-issues.json` | PASS |
| PlantUML evidence | `manual-tests/iss-00209-dependency-view/evidence/deps-issues.puml`; `manual-tests/iss-00209-dependency-view/evidence/deps-raw.puml` | PASS |
| verifier | `manual-tests/iss-00209-dependency-view/verify_projection.py` | PASS |

#### Docs / Manual Verification Evidence
| step | phase | planned evidence | observed evidence | method | result | notes |
|---|---|---|---|---|---|---|
| S90 | Docs | docs explain lifecycle vs disposition and artifact authority | provider and dogfooding docs include lifecycle/disposition table and active view authority notes | docs diff inspection; `cmp -s` mirror checks | pass | `reference_deps.md`, `reference_sync.md` |
| S90 | Manual | realistic fixture validates active graph and machine-readable context | fake GitHub fixture covers open all-done satisfied, empty open blocker, closed empty satisfied, empty unknown fail-closed, and issue blocker | `./capture_evidence.py`; `./verify_projection.py` | pass | no real GitHub repository required |
| S90 | Regression | presentation PUML/JSON behavior remains green | presentation lane passed | `uv run pytest tests/unit/presentation/test_runtime_sync_s07.py tests/unit/presentation/test_deps_raw_puml.py` | pass | 71 passed |
| S90 | Refactor guard | docs/manual only | runtime source and tests unchanged in S90 diff | `git diff --check`; `git status --short` | pass | manual fixture is committed with `git add -f` because `manual-tests/*` is ignored by default |

#### Implementation Delegation Gate
| step | decision | required reason | delegated role | delegated scope | source of truth | allowed changes | forbidden changes | required verification | stop conditions | output required | observed result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S90 | delegated | docs/manual verification step | doc-writer | provider docs, dogfooding docs, manual fixture | `requirement.md`, `design.md`, `plan.md` S90 | reference docs and `manual-tests/**` | runtime source, canonical issue docs, workflow policy, skills/templates | docs mirror checks, manual capture/verifier, presentation lane | runtime change needed | changed files, commands, manual evidence path, risks | pass; no material implementation decisions beyond approved plan |

#### Delegated Worker Evidence
| step | delegated role | worker summary | changed files | checks run | reviewer verdict | unresolved risks | parent integration decision |
|---|---|---|---|---|---|---|---|
| S90 | doc-writer | Documented lifecycle/disposition semantics and created deterministic manual fixture for active dependency views. | `src/spec_dock/assets/spec_dock/docs/reference_deps.md`; `src/spec_dock/assets/spec_dock/docs/reference_sync.md`; `spec-dock/docs/reference_deps.md`; `spec-dock/docs/reference_sync.md`; `manual-tests/iss-00209-dependency-view/**` | manual capture/verifier passed; presentation lane 71 passed; docs mirror checks passed | spec-reviewer failed P1 | fake GitHub did not initially cover unknown fail-closed | accepted with parent follow-up |
| S90 | parent follow-up | Added empty unknown high-level manual case and regenerated evidence for spec-reviewer P1. | `manual-tests/iss-00209-dependency-view/**`; `spec-dock/active/issue/report.md` | manual capture/verifier passed with `deps-check-unknown-iss-01942-github: exit=3`; `git diff --check` -> pass | pending re-review | fake GitHub does not cover live API failure modes; fixture is targeted rather than exhaustive | accepted for re-review |

#### Step Contract Closure
| step | closure ids | close condition from plan | observed evidence | result | notes |
|---|---|---|---|---|---|
| S04/S90 | `cl-015` | realistic mixed-state PlantUML remains visually usable | `manual-tests/iss-00209-dependency-view` verifies active blockers render and satisfied-only high-level noise is omitted from PUML | pass | closes S04 manual-required evidence |
| S90 | `cl-016` | docs explain lifecycle vs disposition and artifact authority | `reference_deps.md` / `reference_sync.md` explain lifecycle fact, disposition result, `dependency_contexts`, and active PUML authority | pass | provider and dogfooding docs match |
| S90 | `cl-017` | realistic manual evidence matches runtime | fake GitHub trial repo evidence shows ready/blocker/unknown exits, JSON context, and PUML active views | pass | no real GitHub repo required |

#### Test Contract Closure
| closure id / test id | step | required | evidence level | pre-implementation evidence | verification command | observed result | notes |
|---|---|---|---|---|---|---|---|
| `tc-s04-004` / `cl-015` | S90 | yes | manual-required | S04 deferred manual evidence | `manual-tests/iss-00209-dependency-view/./capture_evidence.py`; `./verify_projection.py` | pass | manual fixture validates mixed-state active PUML |
| `cl-016` | S90 | yes | inspect-only | docs were incomplete for lifecycle/disposition distinction | docs diff inspection; `cmp -s` mirror checks | pass | docs aligned across provider/dogfooding copies |
| `cl-017` | S90 | yes | manual-required | not applicable | manual capture/verifier; presentation lane | pass | fake GitHub deterministic fixture includes unknown fail-closed case |

#### Reviewer Gate Status
| step | gate name | reviewer role | freshness | state | risk acceptance | promotion / completion decision | notes |
|---|---|---|---|---|---|---|---|
| S90 | step reviewer | spec-reviewer | stale after follow-up | failed | N/A | re-review required | reviewer found missing unknown fail-closed manual evidence |
| S90 | step reviewer re-review | spec-reviewer | fresh | passed | N/A | proceed to S90 commit gate | no findings; prior P1 resolved |

#### Step Commit Gate
| step | closure state | commit scope | commit hash / final ledger | post-commit clean check | no-op rationale | no-op checked contracts / files | no-op diff-clean command | no-op read-only confirmation |
|---|---|---|---|---|---|---|---|---|
| S90 | committed | docs/manual verification and S90 report evidence | `HEAD` (S90 commit) | clean | N/A | N/A | N/A | N/A |

### S99 — Final Quality Gate（2026-06-19）

#### 対象
- Step: S99
- AC/EC: all AC/EC
- Closure IDs: `cl-018`, `cl-019`, `cl-020`; final audit also rechecks `cl-021`, `cl-022`, `cl-023`

#### Final Quality Gate
| check | command | result | notes |
|---|---|---|---|
| domain regression | `uv run pytest tests/unit/domain/test_deps.py` | PASS: 17 passed | S01 domain disposition lane |
| application regression | `uv run pytest tests/unit/application/test_check_deps.py tests/unit/application/test_set_active.py` | PASS: 23 passed | S02 application readiness lane |
| presentation regression | `uv run pytest tests/unit/presentation/test_runtime_sync_s07.py tests/unit/presentation/test_deps_raw_puml.py` | PASS: 71 passed | S03/S04 JSON/PUML lane |
| CLI runtime targeted repair check | `PYTHONDONTWRITEBYTECODE=1 uv run pytest tests/cli_runtime/test_deps.py::TestCliDeps::test_deps_check_returns_ready_and_blockers_and_closure_json tests/cli_runtime/test_sync.py::TestCliSync::test_sync_generates_index_deps_and_deps_issues_artifacts -q -p no:cacheprovider` | PASS: 2 passed | refreshed stale CLI assertions for lifecycle/disposition contexts and active graph filtering |
| CLI runtime full lane | `PYTHONDONTWRITEBYTECODE=1 uv run pytest tests/cli_runtime/test_deps.py tests/cli_runtime/test_sync.py tests/cli_runtime/test_issue_lifecycle.py -p no:cacheprovider` | PASS: 152 passed, 12 skipped | resolved local hang by making the CLI fake `gh` harness deterministic under `/bin/bash` and adding `issue view` support |
| dogfooding validation | `./spec-dock/scripts/spec-dock validate` | PASS: `spec-dock: ok (validate) nodes=131` | no validation errors |
| dogfooding sync | `./spec-dock/scripts/spec-dock sync` | PASS: wrote generated artifacts | post-sync `git status --short` was clean |
| manual realistic fixture | `manual-tests/iss-00209-dependency-view/./capture_evidence.py`; `./verify_projection.py` | PASS | ready/blocker/unknown exits and verifier `RESULT PASS` |
| whitespace | `git diff --check`; `git diff --cached --check` before S90 commit | PASS | no whitespace errors |

#### Closure Coverage
| closure id | step | required evidence | observed evidence | result | notes |
|---|---|---|---|---|---|
| `cl-001` | S01 | empty open high-level dependency blocks | domain tests and S90 manual `iss-01933 -> epic-01930` | pass | `dependency_disposition=blocking` |
| `cl-002` | S01 | open all-descendant-done high-level dependency is satisfied | domain tests and S90 manual `iss-01940 -> epic-01929` | pass | `all_descendant_issues_done` |
| `cl-003` | S01 | unknown high-level/descendant state fails closed | domain tests and S90 manual `iss-01942 -> epic-01941` | pass | `indeterminate`, `empty_unknown_container` |
| `cl-004` | S01 | raw storage/mutation rules unchanged | domain regression suite and full CLI lane passed; no storage mutation contract changed | pass | no raw metadata mutation introduced |
| `cl-005` | S02 | `deps check --json` reports ready satisfied context | presentation JSON tests and manual ready check evidence | pass | `satisfied_dependencies` / `dependency_contexts` retained |
| `cl-006` | S02 | active/issue-start guard rejects empty open blocker | application tests passed | pass | lifecycle CLI suite previously passed in S02 |
| `cl-007` | S02 | descendant count uses full graph | application/domain tests and manual all-done fixture | pass | guards todo projection false-empty |
| `cl-008` | S02 | mutation CLI behavior unchanged | S02 focused CLI evidence and S99 full CLI lane passed; no mutation code changed | pass | active/sync lifecycle lane remained green |
| `cl-009` | S03 | JSON surfaces lifecycle/disposition fields | presentation tests and manual evidence | pass | schema v2 additive fields |
| `cl-010` | S03 | active graph and dependency contexts separated | presentation tests and manual evidence | pass | satisfied-only context kept in `dependency_contexts` |
| `cl-011` | S03 | schema v2 compatibility | presentation tests assert schema v2 | pass | no schema bump |
| `cl-012` | S04 | `deps-issues.puml` omits satisfied-only context | presentation tests and manual PUML evidence | pass | active blocker view |
| `cl-013` | S04 | active blockers render with `blocks` | presentation tests and manual PUML evidence | pass | `raw_direct` absent from readiness PUML |
| `cl-014` | S04 | `deps-raw.puml` is active raw direct view | presentation tests and manual PUML evidence | pass | raw active view, not complete audit |
| `cl-015` | S90 | realistic mixed-state PlantUML remains usable | manual fixture and spec-reviewer S90 re-review | pass | reviewer passed after unknown case was added |
| `cl-016` | S90 | docs explain lifecycle vs disposition and artifact authority | reference docs and S90 spec-reviewer pass | pass | provider/dogfooding docs match |
| `cl-017` | S90 | realistic manual evidence matches runtime | manual capture/verifier and S90 spec-reviewer pass | pass | fake GitHub fixture |
| `cl-018` | S99 | focused regression lane passes | unit lanes, targeted CLI repair check, and full CLI lane passed | pass | local fake `gh` harness hang repaired |
| `cl-019` | S99 | `validate` and `sync` pass | both commands passed and worktree stayed clean | pass | dogfooding state valid |
| `cl-020` | S99 | final QA/code/spec reviewers pass | QA/spec/code reviewers passed | pass | code reviewer accepted one P2 provenance risk |
| `cl-021` | S01 | closed empty high-level dependency is satisfied | domain regression suite and S01 report evidence passed | pass | `lifecycle_closed` prevents empty-open blocker misread |
| `cl-022` | S02 | commands do not block on closed empty high-level dependency | application regression and focused CLI evidence passed | pass | guard consumes domain disposition |
| `cl-023` | S02 | commands fail closed on unknown high-level or descendant state | application regression and S90 manual unknown fixture passed | pass | unknown lifecycle/disposition remains blocking |

#### Closure Delta
| item | status | rationale |
|---|---|---|
| full CLI runtime lane | closed | Required S99 command completed after repairing the CLI fake `gh` harness and stale assertions. |
| live GitHub API behavior | residual risk | Manual fixture uses deterministic fake `gh`; live API failure modes are not covered by this issue. |
| `dependency_contexts` source-node provenance | residual risk | Code reviewer P2: if one issue has multiple raw high-level dependencies that expand to the same target node with the same expansion mode, `.agent/deps-issues.json` may retain only one `source_node_id`. Readiness and PUML remain correct; this can be followed up for machine-consumer provenance fidelity. |
| runtime/docs changes after S90 | test harness and report only | S99 repaired CLI test harness/expectations and updated final evidence; runtime product code did not change after S04. |

#### Reviewer Gate Status
| step | gate name | reviewer role | freshness | state | risk acceptance | promotion / completion decision | notes |
|---|---|---|---|---|---|---|---|
| S99 | final QA reviewer | qa-reviewer | fresh after CLI harness/test/report repair | pass | N/A | accepted | no findings; active graph/dependency_contexts split and harness determinism accepted |
| S99 | final code reviewer | code-reviewer | fresh after CLI harness/test/report repair | pass | accept P2 | accepted | P2 source-node provenance risk remains non-blocking; no P0/P1 |
| S99 | final spec reviewer | spec-reviewer | fresh after CLI harness/test/report repair | pass | N/A | accepted | cl-001..cl-023 coverage and S99 evidence accepted |

#### Step Commit Gate
| step | closure state | commit scope | commit hash / final ledger | post-commit clean check | no-op rationale | no-op checked contracts / files | no-op diff-clean command | no-op read-only confirmation |
|---|---|---|---|---|---|---|---|---|
| S99 | pass | final CLI gate, reviewer evidence, and report closure | S99 commit | pending until commit completes | N/A | N/A | N/A | N/A |
