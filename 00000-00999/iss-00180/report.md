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
| S01 | planned delegation | runtime contract / tests / infra adapter | dev-coder | Runtime doctor capability diagnostics | `plan.md` S01 | S01 allowed paths | raw API checker, live GitHub tests, unrelated doctor findings | `uv run pytest tests/cli_runtime/test_runtime_doctor_s04.py` | broad command redesign, endpoint scope expansion, secret redaction cannot be asserted | changed files / tests / closure evidence / risks | pending |
| S02 | planned delegation | shipped script behavior / final JSON compatibility | dev-coder | PR observation permission limitation classification | `plan.md` S02 | S02 allowed paths | arbitrary API args, extra write probes, retired wrapper | focused `tests/unit/infra/test_init_update.py` selection | status enum conflict, JSON compatibility break | changed files / tests / final JSON examples / risks | pending |
| S03 | planned delegation | shipped asset guidance / dogfooding parity | dev-coder or doc-writer | Guidance and parity | `plan.md` S03 | S03 allowed paths | broad docs rewrite, credential storage guidance | parity inspection and focused tests | mirror overwrite risk, scope expansion | changed files / parity evidence / risks | pending |
| S99 | planned review gates | issue-wide closure | qa-reviewer / code-reviewer / spec-reviewer | final quality gates | `plan.md` S99 | issue-wide diff | unreviewed completion | required validation commands and reviewer pass | missing closure evidence | gate verdicts / final risk | pending |

## 実装記録
- 実装未着手。
- 次回実行時は `plan.md` S01 から開始する。

## 実行コマンド / 結果
```bash
# authoring validation commands are recorded after this report update.
```

## 最終品質ゲート
| gate | scope | result | evidence | next action |
|---|---|---|---|---|
| authoring requirement gate | `requirement.md` | pass | fresh spec-reviewer pass | complete |
| authoring design gate | `design.md` | pass | fresh spec-reviewer pass | complete |
| authoring plan gate | `plan.md` | pass | fresh spec-reviewer pass | complete |
| issue execution gate | S01-S99 | pending | implementation not started | start S01 |
