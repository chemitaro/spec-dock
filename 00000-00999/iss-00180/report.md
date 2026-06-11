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
  - S01 Runtime doctor capability diagnostics: 実装済み、focused tests pass、code-reviewer pass、commit 済み。
  - S02 PR observation permission limitation classification: 実装済み、focused / nearby tests pass、code-reviewer pass、commit 済み。
  - S03 Guidance / dogfooding parity: 実装済み、provider/mirror parity pass、code-reviewer pass、commit 済み。
  - S99 final gate: 初回 final reviewers の P1/P2 指摘を反映済み。`doctor` malformed target rejection、PR metadata / commit status / statusCheckRollup permission coverage、`Resource not accessible by integration` 分類を追補実装済み。fresh final QA / code / spec reviewer pass。
- handoff readiness:
  - PR #181 created and repair loop in progress。
  - 初回 PR observation で provider-tests failure と Codex P2 comments を検出し、repair batch `discussions/20260611t161800z-disc-pr-repair-batch.md` の U001 を実装・検証済み。local code-review P2 で PR metadata / trigger write の `GITHUB_TOKEN` source coverage と trigger integration wording も追補済み。final repair commit、push、再観測が残作業。

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
| S02 | delegated | shipped script behavior / final JSON compatibility | dev-coder | PR observation permission limitation classification | `plan.md` S02 | S02 allowed paths | arbitrary API args, extra write probes, retired wrapper | focused `tests/unit/infra/test_init_update.py` selection; nearby regression selector; `git diff --check` | status enum conflict, JSON compatibility break | changed files / tests / final JSON examples / risks | pass: dev-coder implemented S02, focused/nearby tests pass, code-reviewer pass after follow-ups |
| S03 | delegated | shipped asset guidance / dogfooding parity | dev-coder | Guidance and parity | `plan.md` S03 | S03 allowed paths | broad docs rewrite, credential storage guidance | provider/mirror diff inspection; focused install/parity tests; `validate`; `git diff --check` | mirror overwrite risk, scope expansion | changed files / parity evidence / risks | pass: provider guidance updated and dogfooding mirrors synced; code-reviewer pass |
| S99 | delegated / passed | issue-wide closure | qa-reviewer / code-reviewer / spec-reviewer / dev-coder | final quality gates and reviewer follow-ups | `plan.md` S99 | issue-wide diff; bounded follow-up paths | unreviewed completion, live GitHub tests, arbitrary API expansion | required validation commands and reviewer pass | missing closure evidence, implementation reviewer finding | gate verdicts / final risk | pass: first final reviewers failed on stale report and P2 coverage gaps; follow-up implementation verified; final QA/code/spec reviewers passed |

## 実装記録
- S01 complete:
  - Runtime doctor capability diagnostics を追加した。
  - `DoctorResult.ok` / structural `DoctorFinding` と GitHub capability diagnostics を分離した。
  - `doctor` command surface は fixed target fields と optional extended flag に限定した。
  - `GitHubCapabilityGateway` port と fixed `gh` CLI adapter を追加した。
  - `tc-001`-`tc-006` を focused runtime tests で閉じた。
- S02 complete:
  - PR observation scripts が GitHub token permission denied を machine-readable limitation として返すようにした。
  - Checks / statuses / statusCheckRollup の read permission failure は `unknown` semantic non-success として扱う。
  - Fixed trigger comment write permission failure は `trigger_comment_write` limitation と `human_gate` として扱う。
  - auth missing / rate limit / transient / schema unavailable / invalid input を permission denied と分離した。
  - `tc-007`-`tc-011` を focused script tests で閉じた。
- S03 complete:
  - Provider `github-pr-observation/SKILL.md` に permission limitation semantics を追記した。
  - Provider-side PR observation skill assets を dogfooding `.agents/skills/github-pr-observation/` に反映した。
  - Provider-side runtime S01 changes を dogfooding `spec-dock/scripts/spec_dock_runtime/` に反映した。
  - `tc-012` を parity inspection と focused install/parity tests で閉じた。
- S99 in progress:
  - 初回 final QA / code / spec reviewer で stale report evidence と追補 coverage gaps を確認した。
  - `doctor --github-repo/--github-pr/--github-head-sha` の malformed target を CLI misuse として reject する追補を実装した。
  - PR observation read permission coverage を PR metadata `pull_request_read`、commit status `/status`、`statusCheckRollup` に拡張した。
  - PR metadata permission denied でも raw stderr / token marker を出さず、`stderr_sha256` と `secret_redacted=true` を返す。
  - code-reviewer P2 により、GitHub App / `GITHUB_TOKEN` 系の `Resource not accessible by integration` を permission denied として扱う追補が必要と判定されたため、dev-coder に委任し、provider / dogfooding mirror とテストを更新した。

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

uv run pytest tests/unit/infra/test_init_update.py -k 'issue_180_s02'
# 6 passed

uv run pytest tests/unit/infra/test_init_update.py -k 'github_pr_observation or codex_review or checks_snapshot'
# 6 passed

uv run pytest tests/unit/infra/test_init_update.py -k 'issue_180_s02 or issue_75_pr_observation_checks_collector or issue_170_pr_observation_checks_collector or issue_176_s01_trigger_helper or issue_176_s04_wait'
# 41 passed

uv run pytest tests/unit/infra/test_init_update.py
# 326 passed / 4 failed
# failures are outside S02 allowed scope: dogfooding mirror/S03 parity and existing dogfooding snapshot mismatch

diff -qr src/spec_dock/assets/install_root/.agents/skills/github-pr-observation .agents/skills/github-pr-observation
# clean

diff -qr -x __pycache__ src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime spec-dock/scripts/spec_dock_runtime
# clean

uv run pytest tests/unit/infra/test_init_update.py -k 'github_pr_observation or checked_in_dogfooding_runtime'
# 40 passed

uv run pytest tests/cli_runtime/test_runtime_doctor_s04.py
# 37 passed

uv run pytest tests/unit/infra/test_init_update.py -k 'issue_180_s02 or github_pr_observation or codex_review or checks_snapshot or checked_in_dogfooding_runtime'
# 56 passed, 279 deselected

uv run pytest tests/unit/infra/test_init_update.py -k 'issue_180_s02 and pr_metadata'
# 2 passed, 333 deselected

diff -qr -x __pycache__ src/spec_dock/assets/install_root/.agents/skills/github-pr-observation .agents/skills/github-pr-observation
# clean

diff -qr -x __pycache__ src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime spec-dock/scripts/spec_dock_runtime
# clean

./spec-dock/scripts/spec-dock validate
# spec-dock: ok (validate) nodes=92

git diff --check
# pass
```

## テスト駆動開発証跡
| step | phase | planned evidence | observed evidence | method | result | notes |
|---|---|---|---|---|---|---|
| S01 | Red / characterization | tc-001-tc-006 red-required / inspect-only | S01 closure tests failed before capability contract / port implementation | dev-coder focused test run | fail as expected | `GitHubCapabilityDiagnostic` / `Ports.github_capability_gateway` missing caused failures |
| S01 | Green | tc-001-tc-006 pass | Runtime doctor focused suite passed | `uv run pytest tests/cli_runtime/test_runtime_doctor_s04.py` | pass | 34 passed |
| S01 | Refactor / guardrail | forbidden raw API surface absent | Implementation files have no forbidden raw API args | `rg -n -- ... commands/doctor.py application/doctor.py infra/github_capability_cli.py` | pass | Test forbidden-list strings exist only in tests |
| S02 | Red / characterization | tc-007-tc-011 red-required | Focused `issue_180_s02` tests failed before implementation | dev-coder focused test run | fail as expected | 4 failed / 1 passed for planned permission/secret/status semantics gaps |
| S02 | Green | tc-007-tc-011 pass | Focused and nearby PR observation suites passed | `uv run pytest tests/unit/infra/test_init_update.py -k 'issue_180_s02'`; nearby selector | pass | 6 passed; 41 passed nearby |
| S02 | Reviewer follow-up | code-reviewer P2 generic permission denied | Generic `permission denied` fixture failed before follow-up and passed after classifier broadening | `uv run pytest tests/unit/infra/test_init_update.py -k 'issue_180_s02'` | pass | `tc-007` strengthened for S01/S02 classifier parity |
| S02 | Reviewer follow-up | code-reviewer P2 trigger generic permission denied | Generic `permission denied while posting issue comment` fixture failed before follow-up and passed after trigger classifier broadening | `uv run pytest tests/unit/infra/test_init_update.py -k 'issue_180_s02'` | pass | `tc-008` strengthened for read/trigger classifier parity |
| S02 | Refactor / guardrail | fixed contract retained | Diff stayed within S02 allowed paths; no raw endpoint/method args added | diff inspection; `git diff --check` | pass | Dogfooding mirror intentionally left for S03 |
| S03 | Red / alternative | tc-012 inspect-only | Provider/mirror diff failed before sync; focused parity test failed 1/40 before dogfooding runtime sync | `diff -qr ...`; focused pytest selector | fail as expected | S01/S02 provider changes had not yet been mirrored |
| S03 | Green | tc-012 pass | Provider/mirror diffs clean and focused parity tests pass | `diff -qr ...`; `uv run pytest tests/unit/infra/test_init_update.py -k 'github_pr_observation or checked_in_dogfooding_runtime'` | pass | 40 passed |
| S03 | Refactor / guardrail | guidance/mirror only | Diff limited to SKILL guidance and dogfooding mirrors | diff inspection; `git diff --check` | pass | No broad docs rewrite or credential storage guidance |
| S99 | Red / reviewer follow-up | final reviewer P2 coverage gaps | Malformed doctor target test failed before follow-up; PR metadata permission denied mapped to generic path before follow-up | dev-coder focused red runs | fail as expected | `malformed_github_targets`: 3 failed before fix; `pr_metadata` permission path: 1 failed / 2 passed before fix |
| S99 | Green / follow-up | tc-004 / tc-007 / tc-011 strengthened | Runtime doctor suite and PR observation issue-wide selector passed | `uv run pytest tests/cli_runtime/test_runtime_doctor_s04.py`; PR observation selector | pass | 37 passed; 56 passed / 279 deselected |
| S99 | Red / reviewer follow-up | code-reviewer P2 integration permission wording | `Resource not accessible by integration` PR metadata classification gap found | code-reviewer review; dev-coder red test | fail as expected | `recommended_next_action` fell to `human_gate` before fix |
| S99 | Green / reviewer follow-up | code-reviewer P2 integration permission wording | Integration-denied PR metadata fixture passes and maps to token permission limitation | `uv run pytest tests/unit/infra/test_init_update.py -k 'issue_180_s02 and pr_metadata'`; broader PR observation selector | pass | 2 passed; 56 passed / 279 deselected |
| PR repair U001 | Red / observation | PR #181 initial observation | Provider CI failed; Codex review returned 3 unresolved P2 comments | `wait_pr_observation.sh` on PR #181 head `2fa6da0d...`; `gh run view`; local focused reproduction | fail as expected | failure classes: `check_failure:provider-tests`, `review_feedback:github-capability-classifier`, `review_feedback:token-source`, `review_feedback:missing-gh` |
| PR repair U001 | Green | I001-I007 repair | Full provider unit lane and focused repair tests passed | focused pytest commands; full `tests/unit/infra/test_init_update.py`; mirror diffs; validate; diff check | pass | 41 runtime doctor tests passed; focused trigger selector 4 passed; 338 `test_init_update.py` tests passed |

## ステップ契約の完了証跡
| step | closure ids | close condition from plan | observed evidence | result | notes |
|---|---|---|---|---|---|
| S01 | tc-001-tc-006 | Runtime doctor capability diagnostics implemented, verified, and reviewed | Tests `34 passed`; forbidden surface inspection pass; code-reviewer pass | pass | S01 scope complete |
| S02 | tc-007-tc-011 | PR observation permission limitation classification implemented, verified, and reviewed | Focused tests 6 passed; nearby regression 41 passed; code-reviewer pass after generic permission follow-ups | pass | S02 provider-side scope complete; S03 parity pending |
| S03 | tc-012 | Guidance and dogfooding parity implemented, verified, and reviewed | Provider/mirror diffs clean; focused parity tests 40 passed; code-reviewer pass | pass | S03 scope complete |
| S99 | tc-013 | Issue-wide validation / QA / code / spec review / handoff gates pass | Focused runtime tests 37 passed; PR observation selector 56 passed; `issue_180_s02 and pr_metadata` 2 passed; provider/mirror diffs clean; validate ok; `git diff --check` pass; final QA pass; final code-reviewer pass; final spec-reviewer pass | pass | S99 scope complete before final commit / PR delivery |

## テスト契約の完了証跡
| closure id / test id | step | required | evidence level | pre-implementation evidence | verification command or path | observed result | notes |
|---|---|---|---|---|---|---|---|
| tc-001 | S01 | yes | red-required | Added test failed before implementation due missing capability contract / port | `uv run pytest tests/cli_runtime/test_runtime_doctor_s04.py` | pass | `check_runs_read` permission denied renders status/api/source/action without token value |
| tc-002 | S01 | yes | red-required | Added test failed before implementation due missing no-target diagnostic | `uv run pytest tests/cli_runtime/test_runtime_doctor_s04.py` | pass | No target returns `target_unavailable`, gateway not called, structural success retained |
| tc-003 | S01 | yes | red-required | Added test failed before implementation due missing extended diagnostics | `uv run pytest tests/cli_runtime/test_runtime_doctor_s04.py` | pass | `actions_read` / `issue_comments_read` render as `[github:extended]` |
| tc-004 | S01 | yes | inspect-only | Parser surface lacked explicit fixed GitHub args before S01; malformed target arguments were accepted before S99 follow-up | parser negative test; implementation `rg` inspection; malformed target parser test | pass | No raw endpoint / method / jq / header / raw surface in implementation; malformed `--github-repo`, non-positive `--github-pr`, and non-hex `--github-head-sha` reject at parse time |
| tc-005 | S01 | yes | red-required | Added test failed before implementation due missing auth diagnostics | `uv run pytest tests/cli_runtime/test_runtime_doctor_s04.py` | pass | `auth_missing` remains distinct from `permission_denied` and token source is non-secret |
| tc-006 | S01 | yes | red-required | Initial implementation classified `Unknown JSON field` as `transient_unknown`; follow-up red evidence reproduced it | `uv run pytest tests/cli_runtime/test_runtime_doctor_s04.py` | pass | rate limit / transient / schema unavailable render distinctly; `Unknown JSON field` maps to `schema_unavailable` |
| tc-007 | S02 | yes | red-required | Focused S02 test failed before implementation because checks permission denied stayed generic; PR metadata permission denied mapped to generic path before S99 follow-up; integration wording mapped to `human_gate` before final follow-up | `uv run pytest tests/unit/infra/test_init_update.py -k 'issue_180_s02 and pr_metadata'`; S99 PR observation selector | pass | check-runs, commit status `/status`, statusCheckRollup, PR metadata PAT wording, and PR metadata integration wording permission denied paths are covered |
| tc-008 | S02 | yes | red-required | Focused S02 test failed before implementation because trigger permission denied leaked raw marker and did not map to human gate | `uv run pytest tests/unit/infra/test_init_update.py -k 'issue_180_s02'` | pass | trigger comment permission denied exits 0 and yields `trigger_comment_write` / `human_gate` |
| tc-009 | S02 | yes | red-required | Focused S02 test failed before implementation because non-permission failures collapsed into generic failure | `uv run pytest tests/unit/infra/test_init_update.py -k 'issue_180_s02'` | pass | auth/rate/transient/schema are distinct and not `github_token_permission_denied` |
| tc-010 | S02 | yes | red-required | Existing usage contract characterized invalid input as exit 64 | `uv run pytest tests/unit/infra/test_init_update.py -k 'issue_180_s02'` | pass | invalid `--head-sha` remains usage error and emits no token limitation |
| tc-011 | S02 | yes | red-required | Focused S02 tests failed before implementation because token marker could leak in trigger helper JSON | `uv run pytest tests/unit/infra/test_init_update.py -k 'issue_180_s02'` | pass | raw token-like stderr marker absent; limitation includes `stderr_sha256` and `secret_redacted=true` |
| tc-012 | S03 | yes | inspect-only | Provider/mirror diffs and focused dogfooding parity test failed before sync | provider/mirror `diff -qr`; `uv run pytest tests/unit/infra/test_init_update.py -k 'github_pr_observation or checked_in_dogfooding_runtime'` | pass | PR observation skill mirror and dogfooding runtime mirror match provider-side sources excluding `__pycache__` |
| tc-013 | S99 | yes | manual-required | First final reviewer pass failed on stale report and P2 coverage gaps | final QA / code / spec reviewer gates; final validation commands | pass | Final QA pass with P2 ledger update request; final code-reviewer pass; final spec-reviewer pass |

## クロージャ網羅
| closure id | step | verification evidence | result | notes |
|---|---|---|---|---|
| tc-001 | S01 | `test_doctor_renders_targeted_github_permission_diagnostic_without_secret` | pass | Secret token marker excluded from rendered output |
| tc-002 | S01 | `test_doctor_without_github_target_skips_capability_probe_without_structural_failure` | pass | No false permission failure |
| tc-003 | S01 | `test_doctor_renders_optional_extended_diagnostics_separately` | pass | Core and extended groups separated |
| tc-004 | S01 | `test_doctor_command_surface_rejects_raw_github_api_arguments`; implementation `rg` | pass | Fixed command surface only |
| tc-005 | S01 | `test_doctor_distinguishes_auth_missing_from_permission_denied_without_gh_token` | pass | Auth missing and token source handled without secret |
| tc-006 | S01 | `test_doctor_renders_rate_transient_and_schema_statuses_distinctly`; `test_github_capability_cli_classifies_unknown_json_field_as_schema_unavailable` | pass | EC-003 classification covered |
| tc-007 | S02 | `test_issue_180_s02_snapshot_maps_check_runs_permission_denied_to_unknown_limitation` | pass | Read permission failure semantic non-success covered |
| tc-008 | S02 | `test_issue_180_s02_wait_maps_trigger_comment_permission_denied_to_human_gate` | pass | Trigger write failure semantic non-success covered |
| tc-009 | S02 | `test_issue_180_s02_checks_collector_keeps_non_permission_failures_distinct` | pass | Auth/rate/transient/schema classification covered |
| tc-010 | S02 | `test_issue_180_s02_checks_collector_invalid_input_remains_usage_error` | pass | Usage error remains non-zero |
| tc-011 | S02 | `test_issue_180_s02_trigger_helper_classifies_comment_permission_denied_without_secret`; snapshot permission test | pass | Secret marker excluded from final JSON |
| tc-012 | S03 | provider/mirror diff inspections; checked-in dogfooding parity tests | pass | Shipped guidance and dogfooding mirrors align |
| tc-013 | S99 | focused tests, parity diff, `validate`, `git diff --check`, final reviewer gates | pass | S99 final gate closed |

## クロージャ差分
| change | closure id | test id alias | resolved closure id | reason | plan amendment required | re-review required |
|---|---|---|---|---|---|---|
| none | tc-001-tc-006 | S01 runtime doctor focused tests | tc-001-tc-006 | Planned closure ids closed as written | no | no |
| changed | tc-007 | generic permission denied fixture | tc-007 | code-reviewer P2 requested parity with S01 runtime classifier | no | yes, S02 code-reviewer re-review |
| changed | tc-008 | generic trigger permission denied fixture | tc-008 | code-reviewer P2 requested parity with read-side classifier | no | yes, S02 code-reviewer re-review |
| none | tc-009-tc-011 | S02 PR observation focused tests | tc-009-tc-011 | Planned closure ids closed as written | no | no |
| none | tc-012 | S03 parity inspection and focused tests | tc-012 | Planned closure id closed as written | no | yes, S03 code-reviewer re-review |
| changed | tc-004 | malformed GitHub target parser test | tc-004 | final code-reviewer requested malformed local target rejection instead of accepting invalid target values | no | yes, S99 code-reviewer re-review |
| changed | tc-007 | PR metadata / commit status / statusCheckRollup permission fixtures | tc-007 | final QA/code reviewers requested branch coverage for all PR observation read permission paths | no | yes, S99 code-reviewer re-review |
| changed | tc-007 | PR metadata integration permission fixture | tc-007 | code-reviewer P2 identified `Resource not accessible by integration` as unclassified permission wording | no | yes, S99 code-reviewer re-review |
| changed | tc-011 | PR metadata secret redaction fixture | tc-011 | final reviewers requested secret redaction evidence for PR metadata permission failure path | no | yes, S99 code-reviewer re-review |
| changed | tc-013 | final reviewer gates | tc-013 | Final QA/code/spec reviewers passed after S99 follow-up implementation and report evidence update | no | no |

## 委任 worker 証跡
| step | delegated role | delegated worker summary | changed files | tests run or docs-only verification | reviewer verdict | unresolved risks | parent integration decision |
|---|---|---|---|---|---|---|---|
| S01 | dev-coder | Added runtime GitHub capability diagnostics, fixed CLI probe port/adapter, added focused tests; follow-up fixed `Unknown JSON field` schema classification | `application/contracts.py`; `application/ports.py`; `application/doctor.py`; `commands/doctor.py`; `cli/bootstrap.py`; `infra/github_capability_cli.py`; `presentation/cli_text.py`; `tests/cli_runtime/test_runtime_doctor_s04.py` | `uv run pytest tests/cli_runtime/test_runtime_doctor_s04.py` -> 34 passed; `git diff --check` -> pass | code-reviewer pass after follow-up | Live GitHub API behavior intentionally not tested per plan; S02 remains pending | accepted |
| S02 | dev-coder | Added PR observation permission limitation classification for checks/status/rollup and trigger comment write, with focused script tests; follow-ups broadened generic `permission denied` matching for read and trigger paths | `fetch_pr_checks_snapshot.sh`; `fetch_pr_observation_snapshot.sh`; `trigger_codex_review.sh`; `wait_pr_observation.sh`; `tests/unit/infra/test_init_update.py` | `issue_180_s02` -> 6 passed; nearby PR observation selector -> 41 passed; `git diff --check` -> pass | code-reviewer pass after follow-ups | Full `test_init_update.py` has 4 failures in S03 parity / existing dogfooding snapshot scope | accepted |
| S03 | dev-coder | Updated provider skill guidance and mirrored PR observation assets plus runtime dogfooding files | provider `github-pr-observation/SKILL.md`; `.agents/skills/github-pr-observation/**`; `spec-dock/scripts/spec_dock_runtime/**` | provider/mirror diffs clean; focused parity tests -> 40 passed; `validate` -> ok; `git diff --check` -> pass | code-reviewer pass | Live GitHub API not exercised per plan | accepted |
| S99 follow-up 1 | dev-coder | Added malformed doctor target rejection and expanded read permission coverage for PR metadata, commit status, and statusCheckRollup | `commands/doctor.py`; `fetch_pr_observation_snapshot.sh`; dogfooding mirrors; `tests/cli_runtime/test_runtime_doctor_s04.py`; `tests/unit/infra/test_init_update.py` | runtime doctor suite -> 37 passed; PR observation selector -> 55 passed; provider/mirror diffs clean; `validate` -> ok; `git diff --check` -> pass | code-reviewer fail | live GitHub API intentionally not exercised; integration wording gap found | accepted with follow-up |
| S99 follow-up 2 | dev-coder | GitHub App / `GITHUB_TOKEN` integration permission wording classification | `fetch_pr_observation_snapshot.sh`; dogfooding mirror; `tests/unit/infra/test_init_update.py` | `issue_180_s02 and pr_metadata` -> 2 passed; PR observation selector -> 56 passed; provider/mirror diff clean; `git diff --check` -> pass | final code-reviewer pass | live GitHub API intentionally not exercised | accepted |
| PR repair U001 | dev-coder | Closed PR #181 provider-tests failures and Codex P2 review comments by updating dogfooding snapshot, rate-limit expectation, integration wording classifiers, `GITHUB_TOKEN` token source, and missing `gh` diagnostic handling | runtime doctor adapter/contracts; PR observation scripts; dogfooding mirrors; runtime doctor tests; `test_init_update.py`; repair batch discussion | runtime doctor -> 41 passed; focused trigger selector -> 4 passed; full `test_init_update.py` -> 338 passed; mirror diffs clean; `validate` -> ok; `git diff --check` -> pass | code-reviewer pass with P2 follow-up applied; PR re-observation pending | live GitHub API limited to PR observation; previous review threads unresolved until new head is pushed and reobserved | accepted |

## ステップ commit ゲート
| step | closure state | commit scope | commit hash / final ledger | post-commit clean check | no-op rationale | no-op checked contracts / files | no-op diff-clean command | no-op read-only confirmation |
|---|---|---|---|---|---|---|---|---|
| S01 | committed | Runtime doctor capability diagnostics and S01 report evidence | `a8d128d5` | clean after commit | N/A | N/A | N/A | N/A |
| S02 | committed | Provider-side PR observation permission limitation classification and S02 report evidence | `0bfe1049` | clean after commit | N/A | N/A | N/A | N/A |
| S03 | committed | Guidance and dogfooding mirror parity plus S03 report evidence | `8499971d` | clean after commit | N/A | N/A | N/A | N/A |
| S99 follow-up | ready_to_commit | Final reviewer implementation follow-ups and final report evidence | pending final commit | pending | N/A | N/A | N/A | N/A |

## 最終品質ゲート
| gate | scope | result | evidence | next action |
|---|---|---|---|---|
| authoring requirement gate | `requirement.md` | pass | fresh spec-reviewer pass | complete |
| authoring design gate | `design.md` | pass | fresh spec-reviewer pass | complete |
| authoring plan gate | `plan.md` | pass | fresh spec-reviewer pass | complete |
| issue execution gate | S01-S99 | pass | S01 complete; S02 complete; S03 complete; S99 final QA/code/spec reviewers passed | commit final follow-up and create PR |
| PR delivery gate | PR #181 | in progress | PR created against `main`; initial observation failed; repair batch U001 implemented and verified locally | run code-reviewer on repair diff, commit, push, reobserve PR |
