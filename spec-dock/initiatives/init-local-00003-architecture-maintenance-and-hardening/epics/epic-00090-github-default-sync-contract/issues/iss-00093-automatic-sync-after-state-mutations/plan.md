---
種別: 実装計画書（Issue）
ID: "iss-00093"
タイトル: "Automatic Sync After State Mutations"
関連GitHub: ["#93"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-05-13"
依存: ["requirement.md", "design.md"]
親: ["epic-00090", "init-local-00003"]
---

# iss-00093 Automatic Sync After State Mutations — 実装計画（Execution Contract）

## この計画で満たす要件ID
- AC:
  - AC-001: `new initiative` 成功後の GitHub enabled post-mutation sync。
  - AC-002: `new epic` 成功後の GitHub enabled post-mutation sync。
  - AC-003: `new issue` 成功後の GitHub enabled post-mutation sync。
  - AC-004: `deps add/remove` 更新後の deps projection refresh。
  - AC-005: `delete` 成功後の index / dashboard / deps projection refresh。
  - AC-006: `close` / `issue finish` 後の GitHub 状態取得、finish active clear 維持。
  - AC-007: mutation success + auto-sync failure の non-zero exit と recovery guidance。
  - AC-008: opt-out option を追加しない。
- EC:
  - EC-001: mutation failure では post-mutation sync を実行しない。
  - EC-002: `deps add/remove` unchanged では sync を skip する。
  - EC-003: artifact writer failure は stale / partial risk として表現する。
  - EC-004: GitHub fetch failure / incomplete index は post-mutation sync failure に昇格する。
  - EC-005: `issue finish` 後の sync は branch-derived active restoration を起こさない。
- 制約:
  - provider-side `src/spec_dock/assets/spec_dock/...` を正本にする。
  - live GitHub に依存しない hermetic test を使う。
  - `workflow_spec_authoring.md` / `workflow_issue.md` / `phase_plan_issue.md` の gate を満たす。

## マイルストーン一覧
- M1: post-sync contract foundation
  - 対象: outcome 型、no-migrate wrapper、failure predicate、helper contract。
  - 完了条件: mutation use case が共通 outcome を返せる土台ができ、sync exception / fatal GitHub warning / artifact failure を同じ contract で扱える。
- M2: mutation behavior slices
  - 対象: `new`、`deps`、`delete`、`close`、`issue finish`。
  - 完了条件: 各 target mutation の成功 path と skip/failure path が post-mutation sync contract に接続される。
- M3: command rendering, docs, and final quality
  - 対象: CLI / JSON exit behavior、workflow docs、dogfooding docs refresh/inspection、三者 final quality gate。
  - 完了条件: ユーザーが mutation success と auto-sync success/failure を観測でき、docs と実装が矛盾しない。

## 依存関係から導く実装順序
- 依存関係の正本:
  - `design.md` の `依存関係分析`
  - `design.md` の `Module Dependency Diagram`
  - `design.md` の `ディレクトリ / ファイル変更計画`
- 順序ルール:
  - downstream command behavior より先に application contract / helper を固定する。
  - local source-of-truth mutation の `new` / `deps` を先に接続し、destructive / lifecycle mutation の `delete` / `close` / `issue finish` を後続にする。
  - CLI / JSON rendering と docs は mutation result shape が固まってから更新する。
- step 依存 summary:
  - S01: 依存なし。contracts/helper を追加し、S02-S06 を unblock。
  - S02: S01 に依存。`new initiative/epic/issue` を接続し、create 系 acceptance を unblock。
  - S03: S01 に依存。deps updated / unchanged を接続し、deps projection acceptance を unblock。
  - S04: S01 に依存。delete success / failure を接続し、destructive mutation acceptance を unblock。
  - S05: S01 と close/delete 周辺理解に依存。direct close と issue finish lifecycle を接続し、active preservation acceptance を unblock。
  - S06: S01-S05 に依存。command exit / rendering / JSON / no opt-out assertions を統合する。
  - S90: S05-S06 に依存。workflow docs を実装済み contract へ更新する。
  - S99: S01-S90 に依存。Issue 全体の QA / code / spec review を閉じる。

## ステップ一覧
- S01: Post-mutation sync contract foundation
  - 観測可能な振る舞い: post-sync outcome が success / skipped / failed を一貫して表現する。
  - 依存: requirement / design gate pass。
  - unblock: S02-S06。
  - 対象ファイル: `contracts.py`, `sync_state.py`, helper tests。
  - 閉じる要件: AC-007, EC-001, EC-003, EC-004, EC-005。
- S02: `new initiative/epic/issue` auto-sync
  - 観測可能な振る舞い: `new` 成功直後に index / dashboard が更新される。
  - 依存: S01。
  - unblock: create 系 command integration。
  - 対象ファイル: `create_node.py`, `commands/new.py`, `tests/cli_runtime/test_new.py`。
  - 閉じる要件: AC-001, AC-002, AC-003, EC-001。
- S03: `deps add/remove` auto-sync and unchanged skip
  - 観測可能な振る舞い: deps 更新時だけ projection が更新され、unchanged は sync 成功扱いにしない。
  - 依存: S01。
  - unblock: deps projection integration。
  - 対象ファイル: `mutate_deps.py`, `commands/deps.py`, `tests/cli_runtime/test_deps.py`。
  - 閉じる要件: AC-004, EC-001, EC-002。
- S04: `delete` auto-sync
  - 観測可能な振る舞い: delete 成功後に削除対象が index / dashboard / deps projection から消える。
  - 依存: S01。
  - unblock: delete JSON / rendering integration。
  - 対象ファイル: `delete_node.py`, `commands/delete.py`, `tests/cli_runtime/test_delete.py`。
  - 閉じる要件: AC-005, EC-001, EC-003。
- S05: `close` and `issue finish` lifecycle sync
  - 観測可能な振る舞い: direct close は close 後に sync し、issue finish は active clear 後に1回だけ sync して active clear を維持する。
  - 依存: S01。
  - unblock: final lifecycle behavior and docs update。
  - 対象ファイル: `close_node.py`, `issue_lifecycle.py`, `commands/close.py`, `commands/issue.py`, `tests/cli_runtime/test_close.py`, `tests/cli_runtime/test_issue_lifecycle.py`。
  - 閉じる要件: AC-006, EC-001, EC-004, EC-005。
- S06: CLI / JSON post-sync result integration
  - 観測可能な振る舞い: post-sync failure が non-zero exit、stderr guidance、JSON payload で観測でき、opt-out flag は存在しない。
  - 依存: S01-S05。
  - unblock: docs and final review。
  - 対象ファイル: `presentation/cli_text.py`, `commands/*.py`, `tests/presentation_runtime/test_runtime_sync_s07.py`, relevant CLI parser tests。
  - 閉じる要件: AC-007, AC-008, EC-003, EC-004。
- S90: docs impact resolution / docs refresh
  - 観測可能な振る舞い: provider workflow docs と dogfooding docs が `issue finish` の新 contract と矛盾しない。
  - 依存: S05-S06。
  - unblock: S99。
  - 対象ファイル: `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`, `spec-dock/docs/workflow_issue.md`。
  - 閉じる要件: docs design mapping。
- S99: final quality gate
  - 観測可能な振る舞い: qa-reviewer / issue-wide code-reviewer / spec-reviewer が全体整合を pass する。
  - 依存: S01-S90。
  - unblock: final report ledger and handoff。
  - 対象ファイル: issue-wide diff, `report.md`。

## 要件 ↔ ステップ対応
- AC-001 -> S02
- AC-002 -> S02
- AC-003 -> S02
- AC-004 -> S03
- AC-005 -> S04
- AC-006 -> S05
- AC-007 -> S01, S06
- AC-008 -> S06
- EC-001 -> S01 helper precondition, S02 create failure path, S03 deps failure path, S04 delete failure path, S05 close / finish failure paths
- EC-002 -> S03
- EC-003 -> S01, S04, S06
- EC-004 -> S01, S05, S06
- EC-005 -> S01, S05
- docs design mapping -> S90

## Spec-Locked Closure Index（仕様固定クロージャ索引）

| id | phase / step | slice | type | spec link | locked expectation | observable input/state | bug class guarded | required | evidence level | closure evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| cl-001 | S01 | post-sync contract | acceptance | AC-007, EC-003, EC-004 | `PostMutationSyncOutcome` expresses sync success, skip, artifact failure, sync exception, fatal GitHub warning, and non-fatal GitHub index warning without erasing mutation success. | helper result object from success, exception, artifact failure, `gh_fetch_failed`, `gh_index_incomplete` cases | silent sync failure, ambiguous partial success | yes | red-required | Step Contract Closure S01 |
| cl-002 | S01 | sync request policy | invariant | EC-005 | post-mutation sync uses GitHub enabled, no branch active update, no migrate active manifest behavior. | constructed sync request / wrapper behavior | active restoration after finish, stale GitHub state | yes | red-required | Step Contract Closure S01 |
| cl-003 | S01 | helper precondition boundary | negative | EC-001 | shared post-mutation sync helper is only reachable from explicit mutation-success call sites and has no command-handler auto-run side effect. | helper-level tests or inspection of public helper entrypoints before target wiring | accidental helper invocation outside success boundary | yes | red-required | Step Contract Closure S01 |
| cl-004 | S02 | create auto-sync | acceptance | AC-001, AC-002, AC-003 | successful `new initiative`, `new epic`, and `new issue` refresh `.agent/index-all.json`, `.agent/index.json`, and `dashboard.md` without manual sync. | CLI runtime create commands in temp repo with gh stub | stale create artifacts | yes | red-required | Step Contract Closure S02 |
| cl-005 | S02 | local-only preservation | regression | requirement 前提 | existing local-only nodes remain projected locally while linked nodes use GitHub fetch. | temp repo with local-only node plus create mutation | dropping local-only nodes during GitHub-enabled sync | yes | red-required | Step Contract Closure S02 |
| cl-006 | S03 | deps update auto-sync | acceptance | AC-004 | `deps add/remove` updated path refreshes `.agent/deps-issues.json` and `deps-issues.puml`. | CLI deps add/remove commands and projection reads | stale dependency projection | yes | red-required | Step Contract Closure S03 |
| cl-007 | S03 | deps unchanged skip | negative | EC-002 | duplicate add or no-op remove reports unchanged and does not claim post-sync success. | unchanged deps command result and CLI output | misleading sync success, unnecessary GitHub call | yes | red-required | Step Contract Closure S03 |
| cl-008 | S04 | delete auto-sync | acceptance | AC-005 | successful delete removes the target from index, dashboard, and deps projection without manual sync. | CLI delete command and artifact reads | stale deleted node, dangling deps | yes | red-required | Step Contract Closure S04 |
| cl-009 | S04 | delete sync failure | negative | AC-007, EC-003 | delete source mutation success plus post-sync artifact failure returns non-zero and recovery guidance. | injected artifact writer failure after delete | silent destructive partial state | yes | red-required | Step Contract Closure S04 |
| cl-010 | S05 | direct close sync | acceptance | AC-006, EC-004 | direct close and already-closed success fetch GitHub state and refresh derived state. | gh stub close/already-closed runtime tests | stale GitHub close state | yes | red-required | Step Contract Closure S05 |
| cl-011 | S05 | issue finish active preservation | acceptance | AC-006, EC-005 | `issue finish` runs lifecycle-owned sync after active clear and does not restore active from issue branch. | issue branch finish, `.agent/active.json`, active symlink, artifacts | active restoration regression | yes | red-required | Step Contract Closure S05 |
| cl-012 | S05 | issue finish composition | negative | AC-006, EC-001 | `issue finish` does not run direct-close post-sync before active clear; close failure prevents clear and sync; clear failure skips post-sync with guidance. | instrumentation or observable output/state around lifecycle paths | double sync, wrong active state, hidden stale state | yes | red-required | Step Contract Closure S05 |
| cl-013 | S06 | CLI failure semantics | acceptance | AC-007, EC-003, EC-004 | post-sync failure returns exit code 1 and displays mutation succeeded plus auto-sync failed guidance. | CLI command with sync exception / fatal warning / artifact failure | false success after mutation | yes | red-required | Step Contract Closure S06 |
| cl-014 | S06 | JSON payload | acceptance | design JSON delete | `delete --json` includes post-sync outcome and non-zero exit on post-sync failure. | delete JSON command output | machine consumers miss partial failure | yes | red-required | Step Contract Closure S06 |
| cl-015 | S06 | no opt-out | negative | AC-008 | help/parser expose no `--no-auto-sync` or equivalent opt-out. | CLI help / parser tests | unsupported escape hatch | yes | red-required | Step Contract Closure S06 |
| cl-016 | S90 | workflow docs alignment | docs | design Docs mapping | provider `workflow_issue.md` and dogfooding docs describe the new automatic finish sync contract without contradicting active-clear behavior. | docs diff and spec-reviewer docs alignment | docs/runtime contradiction | yes | inspect-only | Step Contract Closure S90 |
| cl-017 | S99 | integrated quality | review | workflow_issue final gate | QA, issue-wide code review, and final spec review all pass with closure coverage recorded in `report.md`. | final reviewer outputs and validation commands | incomplete handoff | yes | inspect-only | Final Quality Gate |
| cl-018 | S02 | create failure boundary | negative | EC-001 | failed `new initiative` / `new epic` / `new issue` paths do not run post-mutation sync. | create preflight/write failure with sync helper call observation or artifact mtime/content unchanged evidence | sync after failed create | yes | red-required | Step Contract Closure S02 |
| cl-019 | S03 | deps failure boundary | negative | EC-001 | failed `deps add/remove` paths do not run post-mutation sync. | invalid dependency target or write failure with sync helper call observation or artifact mtime/content unchanged evidence | sync after failed deps mutation | yes | red-required | Step Contract Closure S03 |
| cl-020 | S04 | delete failure boundary | negative | EC-001 | failed `delete` paths do not run post-mutation sync. | blocked delete / preflight failure with sync helper call observation or artifact mtime/content unchanged evidence | sync after failed destructive mutation | yes | red-required | Step Contract Closure S04 |
| cl-021 | S05 | close / finish failure boundary | negative | EC-001 | failed direct close does not sync; failed internal close prevents active clear and sync; active clear failure skips lifecycle-owned post-sync. | gh stub failure and active clear failure cases with state/output observation | sync after failed lifecycle mutation | yes | red-required | Step Contract Closure S05 |

## レビュー / QA ゲート方針
- RG1 implementation review:
  - 実施タイミング: 各 implementation step の commit 前。
  - reviewer: fresh `code-reviewer`。
  - pass 条件: `review_status: pass`。
  - 範囲: 現在 step の diff、tests、docs/report 更新、spec 影響。
- QG1 QA review:
  - 実施タイミング: S99 final quality gate。
  - reviewer: fresh `qa-reviewer`。
  - 範囲: Issue 全体の test 十分性、integration test 要否、failure / recovery coverage。
- SG1 spec review:
  - 実施タイミング: S90 docs impact resolution と S99 final quality gate。
  - reviewer: fresh `spec-reviewer`。
  - 範囲: requirement / design / plan / report / docs / implementation / tests 整合。
- 全 step:
  - `report.md` を code-reviewer 前に更新し、closure / verification / delegation evidence を step diff に含める。
  - `1 implementation step = 1 review scope = 1 commit` を標準にする。

## 実行ルール（全ステップ共通）
- 実行 policy、approval cadence、completion contract は `workflow_issue.md` を正本にする。
- step / behavior slice の書き方は `phase_plan_issue.md` を正本にする。
- required closure row の削除、locked expectation 変更、required 変更、spec link 意味変更は plan amendment と re-review を先に通す。
- `approved-no-op` は差分なしの場合だけ許可し、理由、確認対象、差分なし確認コマンドを `report.md` に残す。
- 各 implementation step の開始前に Implementation Delegation Gate を記録する。この issue は runtime / CLI / docs / active state / GitHub stub に跨るため、実装 step は原則 `dev-coder` delegation または明示的な approved-local-execution rationale を必要とする。
- live GitHub へ依存しない。GitHub 状態取得は gh stub / port stub で検証する。
- 各 implementation step は verification 後に refactor / tidy decision point を置く。目的は step 内で発生した重複や命名崩れだけを整えること、guardrail は closure id / public CLI behavior / docs contract を変更しないこと。cleanup が step scope を超える場合は report に残し、別 step または plan amendment へ送る。

## 実装ステップ

### S01 — Post-mutation sync contract foundation
- 観測可能な振る舞い:
  - post-mutation sync helper が `PostMutationSyncOutcome` を返し、failure predicate と no-migrate request policy を一箇所で固定する。
- design 参照:
  - `インターフェース契約`
  - `Module Dependency Diagram`
  - `Sequence Delta`
- 依存:
  - requirement / design gate pass。
- unblock:
  - S02-S06。
- 対象ファイル:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/sync_state.py`
  - focused runtime tests under `tests/cli_runtime/` or `tests/domain_runtime/` depending on existing pattern.
- test bundle:
  - closure id: cl-001, cl-002, cl-003
  - test id: tc-s01-001, tc-s01-002, tc-s01-003, tc-s01-004, tc-s01-005, tc-s01-006, tc-s01-007, tc-s01-008
  - acceptance: helper returns outcome for success / skipped / failure.
  - negative: sync exception, artifact failure, GitHub fatal warnings, mutation failure boundary.
  - invariant: request disables branch active update and uses no-migrate active manifest mode.
- 具体テストケース:
  | test id | closure id | category | setup | action | expected observation | red-first expectation |
  |---|---|---|---|---|---|---|
  | tc-s01-001 | cl-001 | unit / acceptance | fake sync wrapper が success `SyncCommandResult` を返す | post-mutation sync helper を実行 | `PostMutationSyncOutcome.failed == false`、`sync_result` が保持され、`exception_reason` / `skipped_reason` は空 | helper / outcome 未実装で fail |
  | tc-s01-002 | cl-001 | unit / negative | fake sync wrapper が exception を投げる | post-mutation sync helper を実行 | mutation success を取り消さず `sync_result=None`、`exception_reason` と recovery guidance を持つ `failed == true` outcome | exception が未捕捉なら fail |
  | tc-s01-003 | cl-001 | unit / negative | fake sync result に `artifact_failure` を含める | post-mutation sync helper を実行 | `failed == true`、artifact stale / partial risk guidance を持つ | artifact failure を failed 判定しなければ fail |
  | tc-s01-004 | cl-001 | unit / negative | fake sync result の warning code が `gh_fetch_failed` | post-mutation sync helper を実行 | `failed == true`、GitHub fetch failure と recovery guidance を持つ | warning のまま success 扱いなら fail |
  | tc-s01-005 | cl-001 | unit / warning | fake sync result の warning code が `gh_index_incomplete` | post-mutation sync helper を実行 | warning は保持されるが `failed == false`、`fatal_warnings == []`、recovery guidance は空 | index warning 単独で fatal failure になれば fail |
  | tc-s01-006 | cl-002 | unit / invariant | fake sync boundary が受け取った request を記録する | post-mutation sync helper を実行 | request は `github_enabled=True`、`issue_limit=10000`、`force=False`、`update_active_from_branch=False`、no-migrate active manifest mode | request policy が既存 manual sync と同じなら fail |
  | tc-s01-007 | cl-003 | inspection / negative | helper 追加後、command handler と helper public entrypoint を確認 | target mutation wiring 前の S01 diff を検査 | helper は explicit success call site から呼ぶ設計で、command handler の汎用 finally / post hook では自動実行されない | command-level finally hook で呼ばれていれば fail |
  | tc-s01-008 | cl-001 | unit / acceptance | helper に skip reason を渡す、または unchanged caller 用 skip outcome factory を実行する | post-mutation sync helper の skip outcome path を実行 | `sync_result=None`、`skipped_reason` が保持され、`failed == false`、recovery guidance は出ない | skip が `None` や failure と混同されれば fail |
- pre-implementation evidence:
  - expected red: tests asserting missing outcome/helper/fatal warning behavior fail before implementation.
- bounded implementation batch:
  - 許可範囲: outcome dataclass / helper / no-migrate wrapper / narrow tests.
  - 禁止範囲: target mutation use case wiring beyond helper-level characterization.
- verification:
  - targeted command: `uv run pytest tests/cli_runtime tests/domain_runtime`
  - related command: `./spec-dock/scripts/spec-dock validate`
- refactor / tidy:
  - 目的: outcome 型と helper の命名・重複を step 内に限って整える。
  - guardrail: public sync command の migrate behavior と existing import sync contract を変更しない。
- step closure contract:
  - closure ids: cl-001, cl-002, cl-003
  - close 条件: helper contract tests pass and report records request policy / failure predicate evidence.
  - 残リスク: sync output wording may still change in S06.
- step gate:
  - delegation 判断: delegated preferred; approved-local-execution requires documenting why the change is tightly coupled and small enough.
  - code-reviewer gate: review S01 diff only.
  - commit gate: commit only S01 source/tests/report changes after reviewer pass.
  - no-op gate: not expected.

### S02 — `new initiative/epic/issue` auto-sync
- 観測可能な振る舞い:
  - `new initiative`、`new epic`、`new issue` が source-of-truth 作成後に GitHub enabled sync を実行し、index / dashboard に反映する。
- design 参照:
  - `要件 → 設計マッピング` AC-001-AC-003。
  - `ディレクトリ / ファイル変更計画` create / new / tests。
- 依存:
  - S01。
- unblock:
  - create 系 command の user-visible behavior。
- 対象ファイル:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/new.py`
  - `tests/cli_runtime/test_new.py`
- test bundle:
  - closure id: cl-004, cl-005, cl-018
  - test id: tc-s02-001, tc-s02-002, tc-s02-003, tc-s02-004, tc-s02-005
  - acceptance: initiative / epic / issue create artifacts update without manual sync.
  - regression: local-only node remains projected while linked node fetch path is used.
  - negative: create preflight/write failure does not call post-sync and does not claim refreshed artifacts.
- 具体テストケース:
  | test id | closure id | category | setup | action | expected observation | red-first expectation |
  |---|---|---|---|---|---|---|
  | tc-s02-001 | cl-004 | cli / acceptance | temp repo、gh stub、親なし作成可能な状態 | `spec-dock new initiative ...` | manual `sync` なしで `.agent/index-all.json`、`.agent/index.json`、`dashboard.md` に新 initiative が出る | 現状の stale artifact で fail |
  | tc-s02-002 | cl-004 | cli / acceptance | temp repo、既存 initiative、gh stub | `spec-dock new epic --initiative <id> ...` | manual `sync` なしで index / dashboard に新 epic が出る | 現状の stale artifact で fail |
  | tc-s02-003 | cl-004 | cli / acceptance | temp repo、既存 epic、gh stub | `spec-dock new issue --epic <id> ...` | manual `sync` なしで index / dashboard に新 issue が出る | 現状の stale artifact で fail |
  | tc-s02-004 | cl-005 | cli / regression | temp repo に local-only node と linked node が混在、gh stub は linked node のみ返す | `spec-dock new issue --epic <id> ...` | local-only node は index / dashboard のローカル投影に残り、新規 linked node も反映される | GitHub index だけで投影すると fail |
  | tc-s02-005 | cl-018 | cli / negative | create preflight が失敗する入力、sync helper call observation か artifact mtime/content 記録 | `spec-dock new issue` を失敗させる | post-sync は呼ばれず、artifact は create 前と同等で、post-sync success 表示もない | failure path で sync すれば fail |
- pre-implementation evidence:
  - expected red: artifact assertions fail before create wiring.
- bounded implementation batch:
  - 許可範囲: create result post-sync wiring and create CLI exit propagation needed for this slice.
  - 禁止範囲: deps/delete/close lifecycle behavior.
- verification:
  - targeted command: `uv run pytest tests/cli_runtime/test_new.py`
  - related command: `./spec-dock/scripts/spec-dock validate`
- refactor / tidy:
  - 目的: create wiring で重複した post-sync handling を step 内に限って整える。
  - guardrail: deps/delete/close の behavior と common outcome contract を変更しない。
- step closure contract:
  - closure ids: cl-004, cl-005, cl-018
  - close 条件: all three create scopes refresh artifacts, local-only projection is preserved, and create failure paths do not invoke post-sync.
  - 残リスク: shared CLI wording may be normalized later in S06.
- step gate:
  - delegation 判断: delegated preferred due to runtime CLI behavior and fixture setup.
  - code-reviewer gate: review S02 diff only.
  - commit gate: commit S02 after reviewer pass.
  - no-op gate: only if existing implementation already satisfies cl-004/cl-005 with evidence.

### S03 — `deps add/remove` auto-sync and unchanged skip
- 観測可能な振る舞い:
  - deps edge が更新された場合だけ deps projection / PUML が更新され、unchanged path は explicit skip outcome になる。
- design 参照:
  - `要件 → 設計マッピング` AC-004, EC-002。
- 依存:
  - S01。
- unblock:
  - dependency graph freshness。
- 対象ファイル:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/mutate_deps.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/deps.py`
  - `tests/cli_runtime/test_deps.py`
- test bundle:
  - closure id: cl-006, cl-007, cl-019
  - test id: tc-s03-001, tc-s03-002, tc-s03-003, tc-s03-004
  - acceptance: add/remove updates `.agent/deps-issues.json` and `deps-issues.puml`.
  - negative: duplicate add / no-op remove returns unchanged, skips sync, and does not claim refreshed state.
  - negative: invalid target or write failure does not call post-sync.
- 具体テストケース:
  | test id | closure id | category | setup | action | expected observation | red-first expectation |
  |---|---|---|---|---|---|---|
  | tc-s03-001 | cl-006 | cli / acceptance | temp repo に issue A/B、gh stub | `spec-dock deps add --from A --to B` | manual `sync` なしで `.agent/deps-issues.json` と `deps-issues.puml` に edge が出る | projection stale で fail |
  | tc-s03-002 | cl-006 | cli / acceptance | temp repo に issue A/B と既存 edge、gh stub | `spec-dock deps remove --from A --to B` | manual `sync` なしで deps projection / PUML から edge が消える | projection stale で fail |
  | tc-s03-003 | cl-007 | cli / negative | temp repo に issue A/B と既存 edge | duplicate `deps add --from A --to B` | result は unchanged / skip、post-sync success と refreshed 表示を出さない | unchanged で sync success 表示すれば fail |
  | tc-s03-004 | cl-019 | cli / negative | invalid dependency target、sync helper call observation か artifact mtime/content 記録 | `deps add/remove` を失敗させる | post-sync は呼ばれず、deps projection は失敗前と同等 | failure path で sync すれば fail |
- pre-implementation evidence:
  - expected red: projection refresh assertion fails before wiring; unchanged skip assertion fails if helper is called.
- bounded implementation batch:
  - 許可範囲: deps result post-sync outcome, updated/unchanged branching, command exit propagation for deps.
  - 禁止範囲: create/delete/close lifecycle changes.
- verification:
  - targeted command: `uv run pytest tests/cli_runtime/test_deps.py`
  - related command: `./spec-dock/scripts/spec-dock validate`
- refactor / tidy:
  - 目的: updated / unchanged / failure branching が読みやすい範囲で整理する。
  - guardrail: deps source-of-truth mutation rule と existing deps error wording を変更しない。
- step closure contract:
  - closure ids: cl-006, cl-007, cl-019
  - close 条件: updated projection tests, unchanged skip tests, and deps failure no-sync tests pass.
  - 残リスク: common rendering wording may be finalized in S06.
- step gate:
  - delegation 判断: delegated preferred due to source mutation plus projection tests.
  - code-reviewer gate: review S03 diff only.
  - commit gate: commit S03 after reviewer pass.
  - no-op gate: only with existing passing evidence and no diff.

### S04 — `delete` auto-sync
- 観測可能な振る舞い:
  - delete success 後に削除対象が index / dashboard / dependency projection から消え、post-sync failure は destructive partial state として non-zero になる。
- design 参照:
  - `要件 → 設計マッピング` AC-005, AC-007, EC-003。
- 依存:
  - S01。
- unblock:
  - delete JSON outcome and full CLI integration。
- 対象ファイル:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/delete_node.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/delete.py`
  - `tests/cli_runtime/test_delete.py`
- test bundle:
  - closure id: cl-008, cl-009, cl-020
  - test id: tc-s04-001, tc-s04-002, tc-s04-003
  - acceptance: deleted node absent from `.agent/index-all.json`, `.agent/index.json`, `dashboard.md`, deps projection.
  - negative: sync artifact failure after delete returns non-zero and recovery guidance while mutation success remains visible.
  - negative: blocked delete / preflight failure does not call post-sync.
- 具体テストケース:
  | test id | closure id | category | setup | action | expected observation | red-first expectation |
  |---|---|---|---|---|---|---|
  | tc-s04-001 | cl-008 | cli / acceptance | temp repo に削除対象 issue と依存 edge、gh stub | `spec-dock delete <issue>` | manual `sync` なしで削除対象が index / dashboard / deps projection から消える | stale deleted node で fail |
  | tc-s04-002 | cl-009 | cli / negative | delete source mutation は成功、post-sync artifact writer failure を注入 | `spec-dock delete <issue>` | exit code 1、mutation succeeded と auto-sync failed / recovery guidance が観測できる | sync failure を success 扱いなら fail |
  | tc-s04-003 | cl-020 | cli / negative | delete preflight が失敗する対象、sync helper call observation か artifact mtime/content 記録 | `spec-dock delete <target>` を失敗させる | post-sync は呼ばれず、artifact は失敗前と同等 | failure path で sync すれば fail |
- pre-implementation evidence:
  - expected red: artifact stale assertions and failure semantics fail before wiring.
- bounded implementation batch:
  - 許可範囲: delete result post-sync outcome, delete command exit propagation, delete tests.
  - 禁止範囲: close/finish lifecycle changes and docs update.
- verification:
  - targeted command: `uv run pytest tests/cli_runtime/test_delete.py`
  - related command: `./spec-dock/scripts/spec-dock validate`
- refactor / tidy:
  - 目的: destructive mutation の post-sync outcome handling を局所的に読みやすくする。
  - guardrail: remote close barrier、dependency scrub、active repair の既存責務を広げない。
- step closure contract:
  - closure ids: cl-008, cl-009, cl-020
  - close 条件: delete success refresh, post-sync failure, and delete failure no-sync tests pass.
  - 残リスク: JSON payload closure is finalized in S06.
- step gate:
  - delegation 判断: delegated preferred because destructive mutation and partial failure behavior are high risk.
  - code-reviewer gate: review S04 diff only.
  - commit gate: commit S04 after reviewer pass.
  - no-op gate: not expected.

### S05 — `close` and `issue finish` lifecycle sync
- 観測可能な振る舞い:
  - direct `close` syncs after close/already-closed success; `issue finish` suppresses internal close sync and runs one lifecycle-owned sync after active clear.
- design 参照:
  - `Close / finish composition`
  - `Close / issue finish sequence delta`
  - `Domain Model Delta`
- 依存:
  - S01。
- unblock:
  - workflow docs update and final lifecycle confidence。
- 対象ファイル:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/close_node.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_lifecycle.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/close.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/issue.py`
  - `tests/cli_runtime/test_close.py`
  - `tests/cli_runtime/test_issue_lifecycle.py`
- test bundle:
  - closure id: cl-010, cl-011, cl-012, cl-021
  - test id: tc-s05-001, tc-s05-002, tc-s05-003, tc-s05-004, tc-s05-005, tc-s05-006, tc-s05-007, tc-s05-008
  - acceptance: direct close and already-closed close refresh GitHub-backed derived state.
  - acceptance: issue finish clears active then syncs without branch-derived restoration.
  - negative: close failure prevents active clear and sync; clear failure skips post-sync and emits guidance; no double sync before clear.
- 具体テストケース:
  | test id | closure id | category | setup | action | expected observation | red-first expectation |
  |---|---|---|---|---|---|---|
  | tc-s05-001 | cl-010 | cli / acceptance | linked GitHub issue を open -> closed にする gh stub | direct `spec-dock close <issue>` | close 後 GitHub state fetch を含む sync が走り、derived state が closed を反映する | close 後に stale open state なら fail |
  | tc-s05-002 | cl-010 | cli / acceptance | linked GitHub issue が already closed の gh stub | direct `spec-dock close <issue>` | already-closed success 後にも sync が走り、derived state が closed を反映する | already-closed で sync しなければ fail |
  | tc-s05-003 | cl-011 | cli / acceptance | issue branch 上で active issue が set 済み、linked GitHub issue close 可能な gh stub | `spec-dock issue finish` | active clear 後に lifecycle-owned sync が1回走り、`.agent/active.json` と active symlink が対象 issue を復元しない | branch-derived active restoration が起きれば fail |
  | tc-s05-004 | cl-012 | cli / negative | sync helper call count を観測できる fixture | `spec-dock issue finish` | internal close では sync せず、active clear 後の lifecycle-owned sync だけが1回実行される | close 前後で二重 sync すれば fail |
  | tc-s05-005 | cl-021 | cli / negative | direct close が gh stub failure になる | `spec-dock close <issue>` | post-sync は呼ばれず、既存 close failure guidance を維持する | failed close 後に sync すれば fail |
  | tc-s05-006 | cl-021 | cli / negative | `issue finish` の internal close が失敗する gh stub | `spec-dock issue finish` | active clear も post-sync も実行しない | close failure 後に clear / sync すれば fail |
  | tc-s05-007 | cl-021 | cli / negative | internal close は成功、`clear_active()` failure を注入 | `spec-dock issue finish` | command failure、既存 active clear failure guidance、post-sync skip、stale derived state risk guidance | clear failure 後に lifecycle sync すれば fail |
  | tc-s05-008 | cl-011 | cli / acceptance | issue branch 上で active issue が set 済み、linked GitHub issue が already closed の gh stub | `spec-dock issue finish` | already-closed 確認後に active clear、lifecycle-owned sync が1回、active issue は復元されない | already-closed finish で sync/active clear が崩れれば fail |
- pre-implementation evidence:
  - expected red: active clear preservation and no-double-sync assertions fail before lifecycle wiring.
- bounded implementation batch:
  - 許可範囲: close request policy, issue finish sequencing, active preservation tests.
  - 禁止範囲: broad active set behavior changes, manual sync behavior changes outside post-mutation path.
- verification:
  - targeted command: `uv run pytest tests/cli_runtime/test_close.py tests/cli_runtime/test_issue_lifecycle.py`
  - related command: `./spec-dock/scripts/spec-dock validate`
- refactor / tidy:
  - 目的: direct close と lifecycle-owned finish sync の分岐を明確に保つ。
  - guardrail: manual `sync`、`active set`、existing finish failure guidance の contract を変えない。
- step closure contract:
  - closure ids: cl-010, cl-011, cl-012, cl-021
  - close 条件: direct close, already-closed, finish active clear, no-double-sync, close/finish failure no-sync, and clear failure contracts pass.
  - 残リスク: docs still need S90 update after implementation.
- step gate:
  - delegation 判断: delegated strongly preferred because GitHub stub, lifecycle sequencing, and active state interact.
  - code-reviewer gate: review S05 diff only.
  - commit gate: commit S05 after reviewer pass.
  - no-op gate: not expected.

### S06 — CLI / JSON post-sync result integration
- 観測可能な振る舞い:
  - command output and exit code distinguish mutation failure, mutation success + sync success, mutation success + sync failure, and sync skip.
- design 参照:
  - `CLI contract`
  - `JSON delete`
  - `テスト戦略`
- 依存:
  - S01-S05。
- unblock:
  - docs update and final gate。
- 対象ファイル:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/cli_text.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/new.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/deps.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/delete.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/close.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/issue.py`
  - `tests/presentation_runtime/test_runtime_sync_s07.py`
  - relevant CLI parser/help tests.
- test bundle:
  - closure id: cl-013, cl-014, cl-015
  - test id: tc-s06-001, tc-s06-002, tc-s06-003, tc-s06-004
  - acceptance: non-zero exit and guidance for post-sync failure.
  - acceptance: `delete --json` includes post-sync outcome.
  - negative: help/parser expose no opt-out.
- 具体テストケース:
  | test id | closure id | category | setup | action | expected observation | red-first expectation |
  |---|---|---|---|---|---|---|
  | tc-s06-001 | cl-013 | cli / negative | 任意の対象 mutation success 後に sync exception を注入 | target mutation command | exit code 1、stdout/stderr で mutation succeeded と auto-sync failed が区別できる | exit 0 または mutation failure と混同すれば fail |
  | tc-s06-002 | cl-013 | cli / negative | sync result に `gh_fetch_failed` を含める | target mutation command | exit code 1、GitHub fetch failure guidance が出る | warning-only success なら fail |
  | tc-s06-003 | cl-014 | cli / json | `delete --json` で post-sync success / failure を観測できる fixture | `spec-dock delete --json <issue>` | JSON payload に post-sync outcome が入り、failure 時は non-zero exit | JSON に post-sync がなければ fail |
  | tc-s06-004 | cl-015 | cli / parser | CLI help / parser surface | target mutation command help を確認 | `--no-auto-sync` または同等 opt-out が存在しない | opt-out が追加されていれば fail |
- pre-implementation evidence:
  - expected red: output / JSON / help assertions fail before rendering integration.
- bounded implementation batch:
  - 許可範囲: presentation helpers, command exit code propagation, JSON shape for delete, parser/help assertions.
  - 禁止範囲: changing sync engine behavior or mutation sequencing already owned by S01-S05.
- verification:
  - targeted command: `uv run pytest tests/presentation_runtime/test_runtime_sync_s07.py tests/cli_runtime`
  - related command: `./spec-dock/scripts/spec-dock validate`
- refactor / tidy:
  - 目的: post-sync summary rendering と exit-code handling の重複を presentation / command 境界内で整理する。
  - guardrail: command-specific success wording、JSON compatibility、sync command の既存 failure semantics を不要に変えない。
- step closure contract:
  - closure ids: cl-013, cl-014, cl-015
  - close 条件: output, exit, JSON, and no-opt-out assertions pass.
  - 残リスク: user-facing wording may need docs alignment in S90.
- step gate:
  - delegation 判断: delegated preferred because command/presentation changes are cross-cutting.
  - code-reviewer gate: review S06 diff only.
  - commit gate: commit S06 after reviewer pass.
  - no-op gate: only if S02-S05 fully covered the output contract and no presentation diff remains.

### S90 — docs impact resolution / docs refresh
- 観測可能な振る舞い:
  - workflow docs no longer say `issue finish` lacks sync guarantee in a way that contradicts this issue's implementation.
- design 参照:
  - `ディレクトリ / ファイル変更計画`
  - `要件 → 設計マッピング` Docs row。
- 依存:
  - S05-S06。
- unblock:
  - S99 final spec review。
- 対象ファイル:
  - `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
  - `spec-dock/docs/workflow_issue.md`
  - issue `report.md`
- test bundle:
  - closure id: cl-016
  - test id: tc-s90-001
  - docs inspection: provider docs and dogfooding docs have consistent `issue finish` / active clear / auto-sync guidance.
  - regression: no stale instruction recommends avoiding finish post-sync as if it did not exist.
- 具体テストケース:
  | test id | closure id | category | setup | action | expected observation | red-first expectation |
  |---|---|---|---|---|---|---|
  | tc-s90-001 | cl-016 | docs / inspection | provider docs と dogfooding docs | `rg -n "issue finish|sync|active" ...` と docs diff review | `issue finish` が active clear 後に lifecycle-owned sync する新 contract と矛盾しない | old manual-sync caveat が矛盾として残れば fail |
- pre-implementation evidence:
  - inspect-only: current docs contain the previous manual-sync caveat; update need is already identified by design reviewer.
- bounded implementation batch:
  - 許可範囲: workflow docs wording and dogfooding refresh/inspection evidence.
  - 禁止範囲: new runtime behavior beyond already implemented steps.
- verification:
  - targeted command: `rg -n "issue finish|sync|active" src/spec_dock/assets/spec_dock/docs/workflow_issue.md spec-dock/docs/workflow_issue.md`
  - related command: `./spec-dock/scripts/spec-dock validate`
- refactor / tidy:
  - 目的: workflow docs の重複・古い caveat を新 contract に沿って整理する。
  - guardrail: issue lifecycle の completion contract や delivery completion の別 evidence 要件を削らない。
- step closure contract:
  - closure ids: cl-016
  - close 条件: docs updated or explicitly inspected as refreshed, and fresh spec-reviewer docs/spec alignment pass.
  - 残リスク: none expected after spec-reviewer pass.
- step gate:
  - delegation 判断: delegated to `doc-writer` when substantial docs rewrite is needed; approved-local-execution allowed for narrow wording alignment.
  - spec-reviewer gate: docs/spec alignment pass required.
  - commit gate: commit S90 after docs review pass.
  - no-op gate: allowed only if implementation did not require docs change and reviewer accepts the existing docs as non-contradictory.

### S99 — final quality gate
- 観測可能な振る舞い:
  - issue-wide verification and three reviewer gates prove requirement / design / plan / report / implementation / tests / docs are aligned.
- 依存:
  - S01-S90 committed or approved-no-op.
- branch diff 範囲:
  - issue branch diff against base after all step commits.
- test bundle:
  - closure id: cl-017
  - test id: tc-s99-001, tc-s99-002, tc-s99-003
  - integration: end-to-end mutation chain が manual sync なしで artifact freshness を維持するか確認する。
  - review: qa-reviewer / issue-wide code-reviewer / spec-reviewer が closure coverage を確認する。
- 具体テストケース:
  | test id | closure id | category | setup | action | expected observation | red-first expectation |
  |---|---|---|---|---|---|---|
  | tc-s99-001 | cl-017 | review / integration | S01-S90 が committed / approved-no-op | final validation + qa/code/spec reviewers | all final gates pass and closure coverage is recorded in `report.md` | reviewer fail または closure evidence 不足で fail |
  | tc-s99-002 | cl-017 | integration / smoke | temp repo、gh stub、initiative/epic/issue/deps/delete を順に実行できる fixture | create issue -> deps add -> deps remove -> delete を manual sync なしで連続実行 | 各 mutation 後に index / dashboard / deps projection が最新で、最後に削除対象が残らない | step-local tests は通っても連続操作で stale artifact が出れば fail |
  | tc-s99-003 | cl-017 | integration / lifecycle | issue branch、active issue、already-closed GitHub issue stub | `issue finish` 後に final validation と artifact / active state inspection | GitHub closed state が反映され、active clear が維持され、branch-derived active restoration がない | final lifecycle integration で active が復元されれば fail |
- 必須 validation:
  - `./spec-dock/scripts/spec-dock validate`
  - `uv run pytest tests/cli_runtime tests/domain_runtime tests/presentation_runtime`
  - targeted `rg` docs alignment command from S90 if docs are changed.
- final QA gate:
  - reviewer: fresh `qa-reviewer`
  - 範囲: Issue 全体の test 十分性、post-mutation sync failure / active lifecycle / GitHub fetch coverage。
  - pass 条件: `review_status: pass`。必要なら先に integration test を追加する。
- final code review ゲート:
  - reviewer: fresh issue-wide `code-reviewer`
  - 範囲: integrated diff, layered architecture, failure semantics, active preservation, docs/report changes。
  - pass 条件: `review_status: pass`。
- final spec review ゲート:
  - reviewer: fresh `spec-reviewer`
  - 範囲: requirement / design / plan / report / implementation / tests / docs alignment。
  - pass 条件: `review_status: pass`。
- final report ledger:
  - `report.md` に Step Contract Closure、Test Contract Closure、Closure Coverage、Implementation Delegation Gate、Step Commit Gate、Final QA Gate、Final Code Review Gate、Final Spec Review Gate を記録する。
- commit gate:
  - final report ledger commit を作成する。
  - final commit hash と final clean check は最終応答または PR / issue comment の external delivery evidence として残す。

## Final Exit Contract
- 実装開始前:
  - requirement / design / plan gate がすべて fresh `spec-reviewer` pass。
  - `report.md` の Spec Authoring Gate に各 phase の evidence がある。
- 実装中:
  - 各 S01-S90 step は closure ids、pre-implementation evidence、verification、delegation decision、code-reviewer pass、commit / approved-no-op evidence を `report.md` に残す。
  - required closure id を変更する場合は plan amendment と re-review を先に通す。
- 実装完了:
  - S99 で validation、qa-reviewer、issue-wide code-reviewer、final spec-reviewer が pass。
  - final report ledger が更新済み。
  - final commit 済みで、意図しない staged / unstaged 変更なし。
