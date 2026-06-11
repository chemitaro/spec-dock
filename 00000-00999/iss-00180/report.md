---
種別: 実装報告書（Issue）
ID: "iss-00180"
タイトル: "Github Token Capability Preflight"
関連GitHub: ["#180"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-11"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00067", "init-local-00003"]
---

# iss-00180 Github Token Capability Preflight — 実装報告（観測証跡台帳）

## 現在の状態
- 仕様 authoring:
  - `requirement.md`: 作成済み、fresh spec-reviewer pass。
  - `design.md`: 作成済み、fresh spec-reviewer pass。
  - `plan.md`: 作成済み、fresh spec-reviewer pass。
- 実装:
  - 未着手。次工程は `plan.md` S01 からの dev-coder 委任。
- handoff readiness:
  - ready for issue execution。
  - 実行者は `plan.md` の S01 -> S02 -> S03 -> S99 の順に進める。

## 仕様解釈・判断台帳
| ID | Status | Type | Raised By | Gap | 検討した選択肢 | 判断 / 解釈 | Rationale | Disposition | Evidence | Follow-up |
|---|---|---|---|---|---|---|---|---|---|---|
| D-001 | resolved | scope | clarification | `doctor` だけか PR observation も含めるか | A: doctor only; B: PR observation only; C: both | Option C を採用し、`doctor` と PR observation の両方を scope に含める | ユーザーが Option C を採用。権限不足は手動診断と runtime observation の両面で露出する必要がある | promoted_to_requirement | `discussions/20260611t135317z-interview-github-token-capability-scope.md`; `requirement.md` | none |
| D-002 | resolved | scope | clarification | probe profile を固定するか拡張可能にするか | A: minimal; B: broad; C: fixed core + optional extensions | Option C を採用。Core は metadata / PR read / check-runs / statuses / statusCheckRollup、doctor optional は actions / issue comments に限定 | ユーザーが Option C を採用。arbitrary API checker 化を避けつつ実用診断を確保する | promoted_to_requirement | `discussions/20260611t135608z-interview-github-capability-probe-profile.md`; `requirement.md` | none |
| D-003 | resolved | compatibility | clarification | capability failure を process error にするか semantic non-success にするか | A: fail fast; B: warning only; C: final JSON semantic non-success | Option C を採用。`doctor` は exit 0 + findings、PR observation は final JSON semantic non-success、malformed/runtime error は non-zero | ユーザーが Option C を採用。下流 workflow が stdout final JSON を authority として判断できる | promoted_to_requirement | `discussions/20260611t135901z-interview-github-capability-failure-semantics.md`; `requirement.md`; `design.md` | none |
| D-004 | resolved | implementation | design reviewer | Runtime GitHub probe の port / adapter / wiring が曖昧 | A: existing ports に暗黙追加; B: explicit Protocol / infra adapter | `GitHubCapabilityGateway` Protocol、`infra/github_capability_cli.py`、`cli/bootstrap.py` injection を design に明記 | 実装者が source-of-truth layer を迷わず変更できるようにする | applied | spec-reviewer finding; `design.md` | none |
| D-005 | resolved | compatibility | design reviewer | PR observation permission failure 時の status mapping が曖昧 | A: new top-level `permission_denied`; B: existing enum + limitation | top-level status は増やさず、read failure は `unknown`、trigger write failure は `human_gate`、next action は `fix_github_token_permissions` に固定 | Existing callers の enum compatibility を維持しつつ machine-readable limitation を足す | applied | spec-reviewer finding; `design.md` | none |
| D-006 | resolved | test-strategy | plan reviewer | EC-001/EC-002/EC-003 と exit-code semantics の closure が不足 | A: implementation 中に補う; B: plan closure に固定 | `tc-005` / `tc-006` / `tc-009` と `tc-007` / `tc-008` の `exit_code=0` 義務を追加 | 実装者が edge cases と process/semantic 分離を省略できないようにする | promoted_to_plan | spec-reviewer finding; `plan.md` | none |

## 証跡採用台帳
| ID | adoption_status | source | target | rationale | evidence | next_action |
|---|---|---|---|---|---|---|
| EAL-001 | adopted | discussion | `requirement.md` scope / AC | User-adopted Option C。`doctor` と PR observation の両 surface を scope に固定した | `discussions/20260611t135317z-interview-github-token-capability-scope.md` | none |
| EAL-002 | adopted | discussion | `requirement.md` scope / EC | User-adopted Option C。fixed core + limited optional extensions を採用した | `discussions/20260611t135608z-interview-github-capability-probe-profile.md` | none |
| EAL-003 | adopted | discussion | `requirement.md` / `design.md` failure semantics | User-adopted Option C。process exit と semantic status の分離を採用した | `discussions/20260611t135901z-interview-github-capability-failure-semantics.md` | none |
| EAL-004 | adopted | reviewer | `requirement.md` | Reviewer findings を反映し、target handling、optional extended set、trigger write surface を確定した | spec-reviewer rounds: fail -> fail -> fail -> pass | none |
| EAL-005 | adopted | reviewer | `design.md` | Reviewer findings を反映し、port / adapter / status mapping / capability code を確定した | spec-reviewer rounds: fail -> pass | none |
| EAL-006 | adopted | reviewer | `plan.md` | Reviewer findings を反映し、EC closure と exit-code obligation を追加した | spec-reviewer rounds: fail -> pass | none |

## 目的整合台帳
| 対象 | primary objective evidence | secondary requirement evidence | inversion risk | reviewer verdict |
|---|---|---|---|---|
| OAL-001 | `requirement.md` は GitHub token capability の事前診断と PR observation semantic non-success を主目的として固定 | fixed endpoint、secret redaction、provider/mirror parity を制約として固定 | low | requirement / design / plan spec-reviewer pass |

## 仕様 authoring ゲート
| phase | investigated facts | open questions / answers | adoption decision | reviewer verdict | blocking | promotion / next_action |
|---|---|---|---|---|---|---|
| requirement | GitHub issue #180、active issue docs、clarification discussions、existing `doctor` runtime、PR observation scripts | Option C x3 採用済み。未確定なし | adopted | pass | no | promoted to design |
| design | `application/contracts.py`、`application/doctor.py`、`commands/doctor.py`、`application/ports.py`、`cli/bootstrap.py`、`infra/github_cli.py`、PR observation scripts | reviewer 指摘により port / adapter / status mapping / capability code を修正済み | adopted | pass | no | promoted to plan |
| plan | requirement / design、existing doctor tests、PR observation tests in `tests/unit/infra/test_init_update.py` | reviewer 指摘により EC closure と exit-code obligation を修正済み | adopted | pass | no | ready for issue execution |

## 委任ドラフト証跡
- 委任 authoring の使用:
  - not used for system-architect / implementation-planner draft artifacts。
- 未使用理由:
  - `spec-dock-issue-planning` の delegated direct-write authoring は scope-local discussion direct-write consent と clean target discussions を前提にする。
  - この issue では clarification interview artifacts が target `discussions/` に未追跡状態で存在し、scope-local direct-write authoring consent も明示されていないため、delegated draft adoption eligibility を満たさない。
  - そのため design / plan は main orchestrator が canonical docs を直接 authoring し、fresh `spec-reviewer` gates で品質を担保した。

| created_by_role | scope_id | discussion draft path | source_paths | intended_targets | adoption_status | reflected_to | diff_guard_result | integration result | rejected portions | blockers | reviewer result | promotion decision |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| system-architect | iss-00180 | N/A | N/A | `design.md` | not used | [] | not_run | manual authoring fallback | N/A | direct-write precondition not met | design spec-reviewer pass | no delegated draft promotion |
| implementation-planner | iss-00180 | N/A | N/A | `plan.md` | not used | [] | not_run | manual authoring fallback | N/A | direct-write precondition not met | plan spec-reviewer pass | no delegated draft promotion |

## ワークフロー委任同意の証跡
| consent source | repo/worktree | active issue | session | named roles | boundary | expires / invalidation condition | denied / unavailable reason | next action |
|---|---|---|---|---|---|---|---|---|
| user instruction `$spec-dock-issue-planning` | `/Users/iwasawayuuta/.codex/worktrees/0799/spec-dock` | iss-00180 | current session | spec-reviewer | read-only review gates for requirement / design / plan | issue complete / session end / scope change / user revocation | none | proceed |
| none for delegated direct-write authoring | `/Users/iwasawayuuta/.codex/worktrees/0799/spec-dock` | iss-00180 | current session | system-architect / implementation-planner | discussion draft direct-write not granted | until explicit scope-local consent and clean target discussions | direct-write precondition not met | manual authoring fallback |

## レビューゲート状態
| step / phase | gate name | reviewer role | freshness | state | risk acceptance | promotion / completion decision | notes |
|---|---|---|---|---|---|---|---|
| requirement | authoring gate round 1 | spec-reviewer | stale | failed | no | re-review | P1 target resolution ambiguity; P2 optional extended positive AC missing |
| requirement | authoring gate round 2 | spec-reviewer | stale | failed | no | re-review | Optional extended set was still open-ended |
| requirement | authoring gate round 3 | spec-reviewer | stale | failed | no | re-review | Doctor trigger write display contradiction |
| requirement | authoring gate round 4 | spec-reviewer | fresh at promotion | passed | N/A | promoted to design | No blockers |
| design | authoring gate round 1 | spec-reviewer | stale | failed | no | re-review | Missing explicit port / adapter; PR observation status mapping ambiguous; capability code mismatch |
| design | authoring gate round 2 | spec-reviewer | fresh at promotion | passed | N/A | promoted to plan | No blockers |
| plan | authoring gate round 1 | spec-reviewer | stale | failed | no | re-review | Missing EC closure rows; missing `exit_code=0` obligations |
| plan | authoring gate round 2 | spec-reviewer | fresh | passed | N/A | ready for issue execution | No blockers |

## 実装委任ゲート
| step | decision | required reason | delegated role | delegated scope | source of truth | allowed changes | forbidden changes | required verification | stop conditions | output required | observed result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S01 | delegated | runtime contract / tests / infra adapter | dev-coder | Runtime doctor capability diagnostics | `plan.md` S01 | S01 allowed paths | raw API checker, live GitHub tests, unrelated doctor findings | `uv run pytest tests/cli_runtime/test_runtime_doctor_s04.py`; forbidden raw API surface inspection; `git diff --check` | broad command redesign, endpoint scope expansion, secret redaction cannot be asserted | changed files / tests / closure evidence / risks | pass: dev-coder implemented S01, follow-up fixed schema classification, code-reviewer pass |
| S02 | planned delegation | shipped script behavior / final JSON compatibility | dev-coder | PR observation permission limitation classification | `plan.md` S02 | S02 allowed paths | arbitrary API args, extra write probes, retired wrapper | focused `tests/unit/infra/test_init_update.py` selection | status enum conflict, JSON compatibility break | changed files / tests / final JSON examples / risks | pending |
| S03 | planned delegation | shipped asset guidance / dogfooding parity | dev-coder or doc-writer | Guidance and parity | `plan.md` S03 | S03 allowed paths | broad docs rewrite, credential storage guidance | parity inspection and focused tests | mirror overwrite risk, scope expansion | changed files / parity evidence / risks | pending |
| S99 | planned review gates | issue-wide closure | qa-reviewer / code-reviewer / spec-reviewer | final quality gates | `plan.md` S99 | issue-wide diff | unreviewed completion | required validation commands and reviewer pass | missing closure evidence | gate verdicts / final risk | pending |

## 実装記録
- S01 complete:
  - Runtime doctor capability diagnostics を追加した。
  - `DoctorResult.ok` / structural `DoctorFinding` と GitHub capability diagnostics を分離した。
  - `doctor` command surface は fixed target fields と optional extended flag に限定した。
  - `GitHubCapabilityGateway` port と fixed `gh` CLI adapter を追加した。
  - `tc-001`-`tc-006` を focused runtime tests で閉じた。
- 次回実行時は `plan.md` S02 から開始する。

## 実行コマンド / 結果
```bash
uv run pytest tests/cli_runtime/test_runtime_doctor_s04.py
# 34 passed

rg -n -- '--(endpoint|method|jq|header|raw|api|graphql)|raw gh|GraphQL|headers' \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/doctor.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/doctor.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/github_capability_cli.py
# no matches

git diff --check
# pass
```

## テスト駆動開発証跡
| step | phase | planned evidence | observed evidence | method | result | notes |
|---|---|---|---|---|---|---|
| S01 | Red / characterization | tc-001-tc-006 red-required / inspect-only | S01 closure tests failed before capability contract / port implementation | dev-coder focused test run | fail as expected | `GitHubCapabilityDiagnostic` / `Ports.github_capability_gateway` missing caused failures |
| S01 | Green | tc-001-tc-006 pass | Runtime doctor focused suite passed | `uv run pytest tests/cli_runtime/test_runtime_doctor_s04.py` | pass | 34 passed |
| S01 | Refactor / guardrail | forbidden raw API surface absent | Implementation files have no forbidden raw API args | `rg -n -- ... commands/doctor.py application/doctor.py infra/github_capability_cli.py` | pass | Test forbidden-list strings exist only in tests |

## ステップ契約の完了証跡
| step | closure ids | close condition from plan | observed evidence | result | notes |
|---|---|---|---|---|---|
| S01 | tc-001-tc-006 | Runtime doctor capability diagnostics implemented, verified, and reviewed | Tests `34 passed`; forbidden surface inspection pass; code-reviewer pass | pass | S01 scope complete |

## テスト契約の完了証跡
| closure id / test id | step | required | evidence level | pre-implementation evidence | verification command or path | observed result | notes |
|---|---|---|---|---|---|---|---|
| tc-001 | S01 | yes | red-required | Added test failed before implementation due missing capability contract / port | `uv run pytest tests/cli_runtime/test_runtime_doctor_s04.py` | pass | `check_runs_read` permission denied renders status/api/source/action without token value |
| tc-002 | S01 | yes | red-required | Added test failed before implementation due missing no-target diagnostic | `uv run pytest tests/cli_runtime/test_runtime_doctor_s04.py` | pass | No target returns `target_unavailable`, gateway not called, structural success retained |
| tc-003 | S01 | yes | red-required | Added test failed before implementation due missing extended diagnostics | `uv run pytest tests/cli_runtime/test_runtime_doctor_s04.py` | pass | `actions_read` / `issue_comments_read` render as `[github:extended]` |
| tc-004 | S01 | yes | inspect-only | Parser surface lacked explicit fixed GitHub args before S01 | parser negative test; implementation `rg` inspection | pass | No raw endpoint / method / jq / header / raw surface in implementation |
| tc-005 | S01 | yes | red-required | Added test failed before implementation due missing auth diagnostics | `uv run pytest tests/cli_runtime/test_runtime_doctor_s04.py` | pass | `auth_missing` remains distinct from `permission_denied` and token source is non-secret |
| tc-006 | S01 | yes | red-required | Initial implementation classified `Unknown JSON field` as `transient_unknown`; follow-up red evidence reproduced it | `uv run pytest tests/cli_runtime/test_runtime_doctor_s04.py` | pass | rate limit / transient / schema unavailable render distinctly; `Unknown JSON field` maps to `schema_unavailable` |

## クロージャ網羅
| closure id | step | verification evidence | result | notes |
|---|---|---|---|---|
| tc-001 | S01 | `test_doctor_renders_targeted_github_permission_diagnostic_without_secret` | pass | Secret token marker excluded from rendered output |
| tc-002 | S01 | `test_doctor_without_github_target_skips_capability_probe_without_structural_failure` | pass | No false permission failure |
| tc-003 | S01 | `test_doctor_renders_optional_extended_diagnostics_separately` | pass | Core and extended groups separated |
| tc-004 | S01 | `test_doctor_command_surface_rejects_raw_github_api_arguments`; implementation `rg` | pass | Fixed command surface only |
| tc-005 | S01 | `test_doctor_distinguishes_auth_missing_from_permission_denied_without_gh_token` | pass | Auth missing and token source handled without secret |
| tc-006 | S01 | `test_doctor_renders_rate_transient_and_schema_statuses_distinctly`; `test_github_capability_cli_classifies_unknown_json_field_as_schema_unavailable` | pass | EC-003 classification covered |

## クロージャ差分
| change | closure id | test id alias | resolved closure id | reason | plan amendment required | re-review required |
|---|---|---|---|---|---|---|
| none | tc-001-tc-006 | S01 runtime doctor focused tests | tc-001-tc-006 | Planned closure ids closed as written | no | no |

## 委任 worker 証跡
| step | delegated role | delegated worker summary | changed files | tests run or docs-only verification | reviewer verdict | unresolved risks | parent integration decision |
|---|---|---|---|---|---|---|---|
| S01 | dev-coder | Added runtime GitHub capability diagnostics, fixed CLI probe port/adapter, added focused tests; follow-up fixed `Unknown JSON field` schema classification | `application/contracts.py`; `application/ports.py`; `application/doctor.py`; `commands/doctor.py`; `cli/bootstrap.py`; `infra/github_capability_cli.py`; `presentation/cli_text.py`; `tests/cli_runtime/test_runtime_doctor_s04.py` | `uv run pytest tests/cli_runtime/test_runtime_doctor_s04.py` -> 34 passed; `git diff --check` -> pass | code-reviewer pass after follow-up | Live GitHub API behavior intentionally not tested per plan; S02 remains pending | accepted |

## ステップ commit ゲート
| step | closure state | commit scope | commit hash / final ledger | post-commit clean check | no-op rationale | no-op checked contracts / files | no-op diff-clean command | no-op read-only confirmation |
|---|---|---|---|---|---|---|---|---|
| S01 | ready_to_commit | Runtime doctor capability diagnostics and S01 report evidence | pending commit | pending | N/A | N/A | N/A | N/A |

## 最終品質ゲート
| gate | scope | result | evidence | next action |
|---|---|---|---|---|
| authoring requirement gate | `requirement.md` | pass | fresh spec-reviewer pass | complete |
| authoring design gate | `design.md` | pass | fresh spec-reviewer pass | complete |
| authoring plan gate | `plan.md` | pass | fresh spec-reviewer pass | complete |
| issue execution gate | S01-S99 | in progress | S01 complete; S02 pending | start S02 |
