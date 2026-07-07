---
種別: 実施レポート（Issue）
ID: "iss-00293"
タイトル: "最終品質ゲートとマージ可能な Pull Request を作成する"
関連GitHub: ["#293"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-07"
親: ["epic-00283", "init-local-00003"]
---

# iss-00293 最終品質ゲートとマージ可能な Pull Request を作成する — 実施レポート

## 現在の状態

- 状態: 実行中。S01〜S04 と final local verification は実施済み。最終 PR delivery / merge preparation gate は未完了。
- 目的: Epic 全体の品質ゲート、手動テスト、Pull Request 作成、レビュー / CI 指摘対応、mergeable 確認を最後に集約する。
- 前提: `iss-00284` から `iss-00292` までを順番に完了し、この Issue で PR を作成または更新する。
- 追加責務: PR 作成前に ChatGPT Use / Oracle 実行まわりの個人環境絶対パス依存を解消し、backend command adapter / invocation contract を品質ゲート対象に含める。
- readiness: `assurance classify --stage requirement` と `assurance verify` を実行し、`authorized_profile=standard` / `complexity_tier=normal` を確認済み。fresh `spec-reviewer` gate を再取得してから実装へ進む。

## 実行証跡

- S04 backend adapter:
  - `scripts/authoring-pack/invoke_chatgpt_backend.py` を追加し、`SPECDOCK_CHATGPT_COMMAND` / `ORACLE_CHATGPT_COMMAND` で backend command を差し替える薄い adapter とした。
  - 個人環境の `oracle-chatgpt` / ChatGPT Use wrapper 絶対パスは repo 内の正式 workflow / script に直書きしない。
  - 未設定、parse error、missing file、timeout は backend 推測へ進まず `blocked` として fail-closed する。
- Verification:
  - `python -m py_compile scripts/authoring-pack/invoke_chatgpt_backend.py` -> pass。
  - `uv run pytest tests/manual_tests/test_invoke_chatgpt_backend.py -q` -> `10 passed in 0.41s`。
  - `uv run pytest tests/manual_tests/test_prepare_chatgpt_authoring_pack.py tests/manual_tests/test_review_chatgpt_authoring_pack.py tests/manual_tests/test_stage_chatgpt_authoring_pack.py tests/manual_tests/test_validate_selected_skeleton_fill.py tests/manual_tests/test_validate_issue_candidates.py tests/manual_tests/test_invoke_chatgpt_backend.py -q` -> `211 passed in 9.81s`。
  - `git diff --check --cached` -> pass after staging S04 files。
  - `./spec-dock/scripts/spec-dock validate` -> `spec-dock: ok (validate) nodes=189`。
  - scoped local wrapper hardcode guard over `scripts/authoring-pack`, `tests/manual_tests`, and active Issue docs -> no matches。
- Remaining:
  - PR URL と base/head。
  - CI / review / mergeable 状態。
  - PR 作成後のレビュー / CI 指摘と修正再検証。


## 証跡採用台帳（Evidence Adoption Ledger）

| 識別子（ID） | 採用状態（adoption_status） | 出所（source） | 対象（target） | 判断理由（rationale） | 証跡（evidence） | 次アクション（next_action） |
|---|---|---|---|---|---|---|
| EAL-001 | adopted | Epic plan / user workflow decision | `requirement.md`; `design.md`; `plan.md`; `report.md` | `iss-00293` は final quality gate / PR delivery / merge preparation を集約する Issue として必要である。 | Epic `plan.md`; this Issue `requirement.md`; `design.md`; `plan.md` | execute approved plan |
| EAL-002 | adopted | user supplemental requirement | Epic `plan.md`; this Issue `requirement.md`; `design.md`; `plan.md`; `report.md` | SpecDock の正式ワークフローやスクリプトが個人環境の ChatGPT Use / Oracle wrapper 絶対パスに依存すると他環境で再現できないため、PR 作成前の final gate に backend command adapter / invocation contract を追加する。 | user instruction on 2026-07-07; amended Epic and Issue docs | fresh spec-reviewer gate before execution |
| EAL-003 | adopted | `assurance classify --stage requirement` / `assurance verify` | `.assurance.json`; `report.md` | docs amendment 後に source binding hash が stale になっていたため、実行前 gate として local assurance を再分類し、`authorized_profile=standard` を確認した。 | `.assurance.json`; `assurance verify: ok` | fresh spec-reviewer gate before execution |
| EAL-004 | adopted | ChatGPT Use session `specdock-iss00293-final-gate-planning` | S04 backend adapter implementation / tests / report | ChatGPT は `scripts/authoring-pack/invoke_chatgpt_backend.py` と `tests/manual_tests/test_invoke_chatgpt_backend.py` の最小実装、未設定 `blocked`、configured argv ABI、timeout / parse error / missing file diagnostics、PR 前 S04 gate を推奨した。repo ABI v1 と一致するため採用した。 | ChatGPT Use answer; `scripts/authoring-pack/invoke_chatgpt_backend.py`; `tests/manual_tests/test_invoke_chatgpt_backend.py` | run final verification |

## 仕様 authoring ゲート（Spec Authoring Gate）

| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| requirement | Epic docs、Issue requirement、final PR aggregation policy | blocking question なし | EAL-001 を採用 | pass | いいえ | execute approved plan |
| design | canonical requirement、Epic final gate boundary、workflow docs | blocking question なし | final quality gate / PR delivery / merge preparation design を採用 | pass | いいえ | execute approved plan |
| plan | canonical requirement / design、Epic relay execution policy | blocking question なし | final QA / code / spec review、PR delivery、merge preparation plan を採用 | pass | いいえ | execute approved plan |

## Workflow-Scoped Authorization

| field | value |
|---|---|
| authorization source | ユーザーの SpecDock workflow / ChatGPT Use / reviewer gate 利用依頼 |
| repo/worktree | `chemitaro/spec-dock` future final gate branch checkout |
| active scope | `epic-00283` / `iss-00293` |
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
| standard | manual fallback | used | manual evidence: fresh spec-reviewer `019f3999-911a-7381-8155-3cda5fcf3403` passed and canonical docs were integrated by main orchestrator | pass | ready |

## Reviewer Gate Status

| gate | required state | current state | promotion / completion decision |
|---|---|---|---|
| spec-reviewer | fresh `passed` | planning pass: `019f3999-911a-7381-8155-3cda5fcf3403`; backend adapter amendment pass: `019f3a4c-0104-7562-bd52-a5bd9154057f` | backend adapter contract amendment は P0/P1 blocker なし。final execution 後に fresh gate を再実行する。 |
| code-reviewer | required in this Issue final gate | S04 focused pass: `019f3ab7-5f18-7a00-9720-a26ba56a577b`; final issue-wide gate not yet run | S04 P2/P3 findings were fixed; final issue-wide pass is still required before completion |
| qa-reviewer | required in this Issue final gate | S04 focused pass: `019f3ab7-8932-7133-a1f3-d1089d86467d`; final issue-wide gate not yet run | S04 P2 findings were fixed; final issue-wide pass is still required before completion |

| phase | gate | reviewer_role | freshness | state | risk_acceptance | promotion_decision | evidence |
|---|---|---|---|---|---|---|---|
| planning | spec-authoring | spec-reviewer | fresh | pass | no | execute approved plan | fresh pass `019f3999-911a-7381-8155-3cda5fcf3403` |
| planning-amendment | backend-adapter-contract | spec-reviewer | fresh | pass | no | execute approved plan | fresh pass `019f3a4c-0104-7562-bd52-a5bd9154057f` |
| planning-readiness | backend-adapter-abi | spec-reviewer | fresh | pass | no | execute approved plan | `019f3aa2-e9cc-7a20-9939-627fbc235385`; prior P1 fixed and focused re-review passed |
| S04-implementation | backend-adapter-code | code-reviewer | fresh | pass | no | P2/P3 fixed and verification rerun | `019f3ab7-5f18-7a00-9720-a26ba56a577b` |
| S04-verification | backend-adapter-qa | qa-reviewer | fresh | pass | no | P2 fixed and verification rerun | `019f3ab7-8932-7133-a1f3-d1089d86467d` |

## Delegated Draft Evidence

| field | value |
|---|---|
| delegated draft use | not used; この Issue は ChatGPT ZIP draft 由来ではなく、Epic リレー実行方針の final quality gate として追加された。 |
| source evidence | EAL / Issue-local `artifacts/*from-authoring-pack.md` を参照する。 |
| integration rule | draft artifact は evidence-only。採用済み内容だけ canonical docs に再記述し、追加採用または差分変更は Closure Delta と fresh reviewer gate を通す。 |
| reviewer caveat | ChatGPT self-review / reviewer-focus は SpecDock reviewer pass として扱わない。 |

| created_by_role | scope_id | draft_artifact_path | source_paths | intended_targets | adoption_status | reflected_to | diff_guard_result | integration_result | reviewer_focus | blockers | reviewer_result | promotion_decision |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 該当なし | iss-00293 | 該当なし | Epic `plan.md`; Issue `requirement.md`; `design.md`; `plan.md` | `report.md` | not used | `requirement.md`; `design.md`; `plan.md`; `report.md` | pass | manual-authored canonical docs integrated through Evidence Adoption Ledger | none | none | pass | execute approved plan |

## Final PR Delivery / Merge Preparation Gate

| gate | owner | required evidence | current evidence | next_action |
|---|---|---|---|---|
| PR Delivery Gate | `iss-00293` | PR URL、selected base、head branch / SHA、issue linkage、existing PR reuse / new PR creation decision | 未実施 | `iss-00292` 完了後、この Issue execution で記録する |
| Merge Preparation Gate | `iss-00293` | required checks、non-required checks / waiver、blocking review、merge conflict、unresolved blockers、final merge-prepared decision | 未実施 | PR 作成 / 更新後に記録する |
| Backend Adapter Gate | `iss-00293` | backend command adapter / invocation contract、未設定 fail-closed、設定時 command 解決、個人環境絶対パス非直書き確認 | pass: S04 implemented, reviewer P2/P3 fixed, focused tests and full suite passed | final aggregate reviewer gate で再確認する |
| Epic report update | `iss-00293` | Epic report の final gate evidence、manual test matrix、review / CI correction summary | partial: S04 evidence reflected; final PR evidence pending | S90 / S99 で記録する |

## Prior Issue Completion Matrix

| issue | GitHub state | local / report evidence | PR policy |
|---|---|---|---|
| `iss-00284` / #284 | CLOSED | final spec / code / QA reviewer evidence recorded; closure ledger pass | PR deferred to `iss-00293` |
| `iss-00285` / #285 | CLOSED | closure ledger pass; safe review / schema validation evidence recorded | PR deferred to `iss-00293` |
| `iss-00286` / #286 | CLOSED | closure ledger pass; staging / diff evidence recorded | PR deferred to `iss-00293` |
| `iss-00287` / #287 | CLOSED | closure ledger pass; selected skeleton validation evidence recorded | PR deferred to `iss-00293` |
| `iss-00288` / #288 | CLOSED | closure ledger pass; candidate Issue dogfood evidence recorded | PR deferred to `iss-00293` |
| `iss-00289` / #289 | CLOSED | closure ledger pass; selected profile dogfood evidence recorded | PR deferred to `iss-00293` |
| `iss-00290` / #290 | CLOSED | closure ledger pass; mismatch / stale probe evidence recorded | PR deferred to `iss-00293` |
| `iss-00291` / #291 | CLOSED | closure ledger pass; workflow docs / adoption ledger evidence recorded | PR deferred to `iss-00293` |
| `iss-00292` / #292 | CLOSED | `issue finish` completed; metrics / runtime criteria evidence recorded | PR deferred to `iss-00293` |
| `iss-00293` / #293 | OPEN | active final gate issue; `deps check iss-00293` ready with blockers=0 | this Issue creates the Epic PR |

Supporting commands:

- `./spec-dock/scripts/spec-dock active show` -> active `init-local-00003` / `epic-00283` / `iss-00293`.
- `./spec-dock/scripts/spec-dock deps check iss-00293` -> `ready=true`, `blockers=0`, `effective_status=open`, `source=github`, `stale=false`.
- `gh issue list --repo chemitaro/spec-dock --state all --search "284 285 286 287 288 289 290 291 292 293"` -> #284〜#292 CLOSED、#293 OPEN。

## Final Local Verification Evidence

| check | result | evidence |
|---|---|---|
| `spec-dock validate` | pass | `spec-dock: ok (validate) nodes=189` |
| whitespace / patch hygiene | pass | `git diff --check` pass after snapshot fix |
| backend adapter focused tests | pass | `uv run pytest tests/manual_tests/test_invoke_chatgpt_backend.py -q` -> `10 passed in 0.41s` |
| authoring-pack focused suite | pass | `uv run pytest tests/manual_tests/test_prepare_chatgpt_authoring_pack.py tests/manual_tests/test_review_chatgpt_authoring_pack.py tests/manual_tests/test_stage_chatgpt_authoring_pack.py tests/manual_tests/test_validate_selected_skeleton_fill.py tests/manual_tests/test_validate_issue_candidates.py tests/manual_tests/test_invoke_chatgpt_backend.py -q` -> `211 passed in 9.81s` |
| full baseline first run | fail -> fixed | `uv run pytest` initially failed 1 test: checked-in dogfooding `.meta.json` snapshot did not include `epic-00283` / `iss-00284`〜`iss-00293` metadata |
| focused failure rerun | pass | `uv run pytest tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_initiatives_do_not_ship_legacy_deps_json -q` -> `1 passed in 1.52s` |
| full baseline after fix | pass | `uv run pytest` -> `1910 passed, 74 skipped in 934.21s (0:15:34)` |

## Epic Manual Test Matrix

| scenario | status | evidence |
|---|---|---|
| preflight / prompt pack | pass | `iss-00284` closure ledger and full baseline covered preflight output, source manifest, stale / forbidden claim negative cases |
| safe ZIP / tree review | pass | `iss-00285` closure ledger and full baseline covered status taxonomy, redaction, valid / invalid no-mutation behavior |
| staged rendering / diff | pass | `iss-00286` closure ledger and full baseline covered staging output, canonical byte snapshot, EAL candidate boundary |
| selected skeleton fill | pass | `iss-00287` closure ledger and full baseline covered profile-controlled section filling and mismatch protection |
| candidate Issue slicing | pass | `iss-00288` closure ledger and full baseline covered candidate-only pack validation and profile boundary metadata |
| selected profile dogfood | pass | `iss-00289` closure ledger records ZIP review / selected skeleton validation / dry-run pass |
| mismatch / stale probes | pass | `iss-00290` closure ledger records negative probe evidence and stale review command coverage |
| workflow docs / adoption examples | pass | `iss-00291` closure ledger and README updates covered prompt contract, status examples, fallback boundary |
| metrics / promotion criteria | pass | `iss-00292` artifacts and report recorded dogfood metrics, runtime promotion criteria, and defer stance |
| backend command adapter | pass | S04 adapter evidence, reviewer finding disposition, focused tests, scoped local wrapper hardcode guard |
| dogfooding metadata snapshot | pass | `tests/unit/infra/test_init_update.py` updated to include `epic-00283` / `iss-00284`〜`iss-00293` `.meta.json` paths and empty `depends_on` baseline |

## ChatGPT Use Planning Evidence

| field | value |
|---|---|
| session slug | `specdock-iss00293-final-gate-planning` |
| requested scope | final gate / backend adapter implementation recommendation |
| branch state | branch pushed before live ChatGPT Use run |
| adopted recommendations | new `invoke_chatgpt_backend.py`; new `test_invoke_chatgpt_backend.py`; `SPECDOCK_CHATGPT_COMMAND` primary; `ORACLE_CHATGPT_COMMAND` fallback; argv prefix via `shlex.split`; `shell=False`; unset / parse / missing file / timeout as `blocked`; stdout / stderr / exit code passthrough |
| rejected recommendations | none materially; exact JSON field names are local implementation details |
| authority boundary | advisory evidence only; local tests and reviewer gates remain authoritative |

## Backend Adapter Evidence

| check | result | evidence |
|---|---|---|
| implementation path | pass | `scripts/authoring-pack/invoke_chatgpt_backend.py` added as dogfood-only helper, not shipped runtime |
| backend env precedence | pass | `SPECDOCK_CHATGPT_COMMAND` primary, `ORACLE_CHATGPT_COMMAND` compatibility fallback |
| unset fail-closed | pass | unset env returns `blocked` without guessing local wrapper path |
| argv ABI | pass | configured command is parsed with `shlex.split(..., posix=True)` and invoked with `shell=False` as `backend_argv + ["--slug", slug, "-p", prompt, "--file", ...]` |
| dry-run | pass | dry-run reports resolved invocation and does not start backend |
| execution passthrough | pass | backend stdout / stderr / exit code are preserved |
| timeout / malformed command / missing file | pass | adapter returns `blocked` before or while controlling backend execution |
| local wrapper dependency | pass | no Oracle / ChatGPT automation is bundled; personal wrapper is only a user-provided env value |
| focused tests | pass | `uv run pytest tests/manual_tests/test_invoke_chatgpt_backend.py -q` -> `10 passed in 0.41s` |
| authoring-pack focused suite | pass | `uv run pytest tests/manual_tests/test_prepare_chatgpt_authoring_pack.py tests/manual_tests/test_review_chatgpt_authoring_pack.py tests/manual_tests/test_stage_chatgpt_authoring_pack.py tests/manual_tests/test_validate_selected_skeleton_fill.py tests/manual_tests/test_validate_issue_candidates.py tests/manual_tests/test_invoke_chatgpt_backend.py -q` -> `211 passed in 9.81s` |
| syntax / diff / validation | pass | `python -m py_compile scripts/authoring-pack/invoke_chatgpt_backend.py`; `git diff --check` pass; `git diff --check --cached` pass after staging S04 files; `./spec-dock/scripts/spec-dock validate` -> `spec-dock: ok (validate) nodes=189` |
| scoped local wrapper hardcode guard | pass | scoped `rg` over authoring-pack scripts/tests and active Issue docs found no host-local Oracle / ChatGPT wrapper absolute-path matches |

## Reviewer Finding Disposition

| reviewer | finding | priority | disposition | evidence |
|---|---|---|---|---|
| code-reviewer `019f3ab7-5f18-7a00-9720-a26ba56a577b` | directory attachments were accepted because validation checked only existence | P2 | fixed | `_validate_files` now requires `Path.is_file()` and `test_directory_attachment_fails_before_backend_execution` covers the blocked diagnostic |
| code-reviewer `019f3ab7-5f18-7a00-9720-a26ba56a577b` | untracked new files were not covered by `git diff --check` evidence | P2 | fixed | staged S04 files and reran `git diff --check --cached` successfully |
| code-reviewer `019f3ab7-5f18-7a00-9720-a26ba56a577b` | README still said adapter is not implemented | P3 | fixed | stale sentence removed; manual fallback wording updated to current adapter behavior |
| qa-reviewer `019f3ab7-8932-7133-a1f3-d1089d86467d` | repeatable attachment argv ordering had only one attachment in tests | P2 | fixed | `test_backend_receives_oracle_compatible_argv_without_shell` now asserts two ordered `--file` pairs |
| qa-reviewer `019f3ab7-8932-7133-a1f3-d1089d86467d` | Backend Adapter Gate row was stale | P2 | fixed | gate table now records S04 implementation and focused verification status without claiming final issue completion |

## Parent Implementation Exception Record

| field | value |
|---|---|
| scope | S04 ChatGPT backend command adapter / invocation contract |
| reason direct implementation was used | Approved `plan.md` lists S04 owner as `main orchestrator / dev-coder`; the change is a bounded dogfood helper plus focused tests and report evidence, with no shipped runtime promotion or cross-layer runtime change. |
| user approval / trigger | User supplemental requirement requested this fix before final `iss-00293` PR creation and allowed it at a suitable work boundary. |
| allowed files | `scripts/authoring-pack/**`; `tests/manual_tests/**`; `scripts/authoring-pack/README.md`; `iss-00293/report.md`; Epic `report.md` |
| allowed operation | Add a thin configurable backend adapter, focused tests, README usage note, and evidence updates. |
| forbidden operation | Bundling Oracle / ChatGPT automation, hardcoding personal absolute paths, changing shipped runtime behavior, changing `.assurance.json`, or broad runtime promotion. |
| rollback plan | Revert S04 adapter commit and report evidence if reviewer finds the adapter contract invalid before PR creation. |
| post-change verification | `py_compile`, adapter focused pytest, authoring-pack focused pytest, `git diff --check`, `spec-dock validate`, scoped local wrapper hardcode guard. |
| reviewer gate | Fresh code-reviewer / qa-reviewer before S04 commit, and final issue-wide spec / code / QA gates before PR-ready completion. |

## Execution Readiness Evidence

| check | result | evidence |
|---|---|---|
| branch pushed before ChatGPT Use | pass | `git push -u origin iss-00293-final-epic-quality-gate-and-mergeable-pr` succeeded |
| assurance classify | pass | `./spec-dock/scripts/spec-dock assurance classify --stage requirement` -> `authorized_profile=standard`, `complexity_tier=normal` |
| assurance verify | pass | `./spec-dock/scripts/spec-dock assurance verify` -> ok |
| runtime guidance after assurance | blocked until reviewer | `guidance issue-execution` reported `report-spec-review-missing`; fresh `spec-reviewer` re-review `019f3aa2-e9cc-7a20-9939-627fbc235385` passed after ABI fix |

## Closure Evidence Ledger

| closure id | status | required evidence | current evidence | next_action |
|---|---|---|---|---|
| tc-001 | pass | 先行 Issue 完了 / scope isolation | #284〜#292 CLOSED、#293 OPEN、`deps check iss-00293` ready / blockers=0。working tree diff は snapshot/report final evidence に限定。 | closed |
| tc-002 | pass | `spec-dock validate` / `git diff --check` / 関連テスト | `spec-dock validate` pass、`git diff --check` pass、focused adapter 10 passed、authoring-pack suite 211 passed、full baseline after snapshot fix 1910 passed / 74 skipped。 | closed |
| tc-003 | pass | Epic manual test matrix | scenario-by-scenario matrix を記録。preflight / safe review / staging / profile / dogfood / docs / metrics / backend adapter / metadata snapshot を確認済み。 | closed |
| tc-004 | pass | backend command adapter / invocation contract | S04 adapter implemented; ChatGPT Use advisory recommendations adopted; focused tests and authoring-pack suite passed; no local wrapper dependency added | closed |
| tc-005 | pending | PR URL / CI / review / mergeable status | 未実施 | PR 作成後に記録する |
| tc-006 | pending | Epic / Issue report 更新 / docs impact | Issue report 更新中。Epic report には S04 evidence と final local verification / manual matrix / PR evidence を反映する必要がある。 | S90 で記録する |
| tc-007 | pending | fresh reviewer results / blocker disposition | 未実施 | S99 で記録する |

## 残リスク

- この Issue 開始時点で先行 Issue に未完了または未記録の作業がある場合、PR 作成前に戻って補完する必要がある。
- PR が mergeable にならない場合、ブロッカーをこのレポートに記録し、Epic 外の課題は別途切り出す。

## Spec Interpretation / Decision Ledger

| ID | decision | status | evidence | next_action |
|---|---|---|---|---|
| SID-iss-00293-001 | `iss-00293` は Epic 最後の品質ゲート / manual test / PR 作成 / mergeable 確認を担当する final gate Issue として扱う。 | accepted | Epic `plan.md` C09 -> C10; `requirement.md`; `design.md`; `plan.md` | `iss-00292` 完了後に開始する |
| SID-iss-00293-002 | 個別 Issue ごとに PR を作成せず、PR 作成と CI / review 修正はこの Issue に集約する。 | accepted | Epic `plan.md` リレー実行 / PR 方針; EAL-009 | PR 作成時に PR URL、CI、review、mergeable 状態を記録する |
| SID-iss-00293-003 | 品質ゲートで見つかった不具合は、Epic スコープ内の最小修正としてこの Issue で扱う。 | accepted | `requirement.md` AC-006 / AC-009; `design.md` 不具合修正ループ | 修正、再検証、再 push の証跡を残す |
| SID-iss-00293-004 | PR 作成前に、SpecDock 側の ChatGPT backend command adapter / invocation contract を実装または検証し、個人環境 wrapper 絶対パスを正式ワークフローの必須依存にしない。 | accepted | user supplemental requirement; EAL-002; amended `requirement.md`; `design.md`; `plan.md`; S04 adapter implementation evidence | closed; include in final reviewer gate |
| SID-iss-00293-005 | Backend adapter ABI v1 は、設定値を shell ではなく argv prefix として解釈し、`--slug`、`-p/--prompt`、repeatable `--file` を Oracle 互換 backend へ `shell=False` で渡す。ABI 不一致の backend はユーザー環境の shim で吸収する。 | accepted | spec-reviewer P1 `019f3aa2-e9cc-7a20-9939-627fbc235385`; updated `design.md`; updated `plan.md`; focused re-review pass | 実装へ進む |
| SID-iss-00293-006 | Adapter diagnostics for unset command、malformed command、missing file、timeout are `blocked` rather than fallback to a guessed backend. | accepted | ChatGPT Use recommendation; focused tests; `invoke_chatgpt_backend.py` | closed; include in final reviewer gate |
