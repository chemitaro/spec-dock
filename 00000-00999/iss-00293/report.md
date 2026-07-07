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

- 状態: 最終品質ゲートの証跡更新中。S01〜S04 と final local verification は実施済み。PR #294 は作成済み。Provider CI / mypy failure と Codex P1 finding 4件は修正済み。最新観測では CI pass、現行 Codex review は P2 non-blocking のみ、GitHub merge state は `CLEAN` / `MERGEABLE`。final issue-wide reviewer gate は、未コミット証跡と未完了レジャーを P1 として検出したため、本レポートで是正し、commit / push 後に再確認する。
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
  - この最終証跡更新を commit / push し、PR head 上で mergeability と reviewer gate を再確認する。
  - 過去 unresolved thread は platform conversation として残りうるが、current P0/P1 blocker がないことを final gate の判断材料にする。


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
| spec-reviewer | fresh final gate | planning pass: `019f3999-911a-7381-8155-3cda5fcf3403`; backend adapter amendment pass: `019f3a4c-0104-7562-bd52-a5bd9154057f`; final gate `019f3b1d-c36f-76b2-886e-b4a84a2f629f` found workflow P1 only: final evidence was still local-only and `tc-007` was pending | no spec-content P0/P1. This report update is the corrective action; commit / push and post-push confirmation are required before final close. |
| code-reviewer | required in this Issue final gate | S04 focused pass: `019f3ab7-5f18-7a00-9720-a26ba56a577b`; final issue-wide pass: `019f3b1d-ece6-7681-bbfc-165c6a8c2c39` | pass. No P0/P1 blocker; four P2 contract / safety hardening items are tracked as non-blocking follow-up decisions. |
| qa-reviewer | required in this Issue final gate | S04 focused pass: `019f3ab7-8932-7133-a1f3-d1089d86467d`; final gate `019f3b1e-4184-7da1-b712-d3434dd81136` found workflow P1 only: final evidence was local-only / ledger not closed, plus P2 traceability hardening | no separate implementation / test coverage P0/P1. This report update closes the ledger and adds durable P2 disposition. |

| phase | gate | reviewer_role | freshness | state | risk_acceptance | promotion_decision | evidence |
|---|---|---|---|---|---|---|---|
| planning | spec-authoring | spec-reviewer | fresh | pass | no | execute approved plan | fresh pass `019f3999-911a-7381-8155-3cda5fcf3403` |
| planning-amendment | backend-adapter-contract | spec-reviewer | fresh | pass | no | execute approved plan | fresh pass `019f3a4c-0104-7562-bd52-a5bd9154057f` |
| planning-readiness | backend-adapter-abi | spec-reviewer | fresh | pass | no | execute approved plan | `019f3aa2-e9cc-7a20-9939-627fbc235385`; prior P1 fixed and focused re-review passed |
| S04-implementation | backend-adapter-code | code-reviewer | fresh | pass | no | P2/P3 fixed and verification rerun | `019f3ab7-5f18-7a00-9720-a26ba56a577b` |
| S04-verification | backend-adapter-qa | qa-reviewer | fresh | pass | no | P2 fixed and verification rerun | `019f3ab7-8932-7133-a1f3-d1089d86467d` |
| final-gate | issue-wide-spec | spec-reviewer | fresh | corrective-action-required | no spec-content P0/P1 | commit this report and rerun final confirmation on pushed head | `019f3b1d-c36f-76b2-886e-b4a84a2f629f` found only local-only evidence / pending ledger P1 |
| final-gate | issue-wide-code | code-reviewer | fresh | pass | no | P2 follow-up tracked; no branch mutation for P2-only items | `019f3b1d-ece6-7681-bbfc-165c6a8c2c39` |
| final-gate | issue-wide-qa | qa-reviewer | fresh | corrective-action-required | no implementation P0/P1 | commit this report and rerun final confirmation on pushed head | `019f3b1e-4184-7da1-b712-d3434dd81136` found only local-only evidence / pending ledger P1 plus P2 traceability |

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
| PR Delivery Gate | `iss-00293` | PR URL、selected base、head branch / SHA、issue linkage、existing PR reuse / new PR creation decision | PR #294 created for `main` <- `iss-00293-final-epic-quality-gate-and-mergeable-pr`; issue linkage recorded; P1 repair head observed | final evidence report commit / push, then post-push confirmation |
| Merge Preparation Gate | `iss-00293` | required checks、non-required checks / waiver、blocking review、merge conflict、unresolved blockers、final merge-prepared decision | Provider CI / mypy failure fixed; carryover Codex P1 4件 fixed; latest observation on `9a1f939c106f5bc48b9280ac5718700223746ab2` shows CI pass, current P2 only, `MERGEABLE` / `CLEAN` | re-confirm after this report-only evidence commit |
| Backend Adapter Gate | `iss-00293` | backend command adapter / invocation contract、未設定 fail-closed、設定時 command 解決、個人環境絶対パス非直書き確認 | pass: S04 implemented, reviewer P2/P3 fixed, focused tests and full suite passed | final aggregate reviewer gate で再確認する |
| Epic report update | `iss-00293` | Epic report の final gate evidence、manual test matrix、review / CI correction summary | pass after this evidence update: S04、PR delivery、CI repair、P1 repair、terminal P2 disposition を反映 | commit / push and post-push confirmation |

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
| PR initial observation | fail -> fixed locally | PR #294 initial observation posted `@codex review`; `validate` check passed but Provider CI failed at `make lint` / mypy for manual test helper typing. |
| CI failure local reproduction | reproduced | `make lint` reproduced the same mypy failure in `tests/manual_tests/test_review_chatgpt_authoring_pack.py`, `test_stage_chatgpt_authoring_pack.py`, `test_validate_issue_candidates.py`, and `test_validate_selected_skeleton_fill.py`. |
| CI repair lint | pass | after type-only manual test helper fixes, `make lint` -> ruff check pass, ruff format check pass, mypy pass |
| CI repair focused tests | pass | `uv run pytest tests/manual_tests/test_review_chatgpt_authoring_pack.py tests/manual_tests/test_stage_chatgpt_authoring_pack.py tests/manual_tests/test_validate_issue_candidates.py tests/manual_tests/test_validate_selected_skeleton_fill.py tests/manual_tests/test_invoke_chatgpt_backend.py -q` -> `130 passed in 4.52s` |
| CI repair structure / diff | pass | `./spec-dock/scripts/spec-dock validate` -> `spec-dock: ok (validate) nodes=189`; `git diff --check` pass |
| PR re-observation after CI repair | timeout with CI pass | head `2a7456163a0ef78db8a049fa24e83c2d5e923387`; Actions runs 4/4 success; decision timed out because no current completion signal and 4 carryover unresolved Codex P1 threads remained. |
| Codex P1 repair focused tests | pass | after fixing the four carryover P1 findings, `uv run pytest tests/manual_tests/test_review_chatgpt_authoring_pack.py tests/manual_tests/test_validate_selected_skeleton_fill.py -q` -> `84 passed in 2.47s`; authoring-pack focused suite -> `215 passed in 9.59s` |
| Codex P1 repair lint / structure | pass | `make lint` -> pass; `./spec-dock/scripts/spec-dock validate` -> `spec-dock: ok (validate) nodes=189`; `git diff --check` pass |
| PR re-observation after P1 repair | human_gate / non-blocking only | head `9a1f939c106f5bc48b9280ac5718700223746ab2`; Actions runs 4/4 success; current Codex review completed and selected P2 findings only; blocker_policy `non_blocking_only`; observation status `human_gate` due unresolved review threads. |
| GitHub mergeability check | pass | `gh pr view 294 --json ...` -> `mergeable=MERGEABLE`, `mergeStateStatus=CLEAN`, state `OPEN`, `isDraft=false`, head `9a1f939c106f5bc48b9280ac5718700223746ab2` |

## PR Delivery / CI Repair Evidence

| item | value |
|---|---|
| PR URL | `https://github.com/chemitaro/spec-dock/pull/294` |
| base / head | `main` / `iss-00293-final-epic-quality-gate-and-mergeable-pr` |
| PR title | `feat(authoring-pack): ChatGPT ZIP仕様作成パックを追加` |
| issue linkage | PR body includes `Closes #293` and `Refs #283` |
| initial observed head | `40af0ea3fe7f7b0743a51532495338cfe6ffc246` |
| initial observation result | failed: Provider CI failed; validate check passed; PR remained `MERGEABLE` but `UNSTABLE` |
| failure | `make lint` / mypy type errors in manual test helper files |
| repair scope | type-only test helper annotations, import order, local variable naming to avoid mypy assignment conflicts |
| local repair evidence | `make lint` pass; focused manual tests `130 passed`; `spec-dock validate` pass; `git diff --check` pass |
| second observation result | CI passed for head `2a7456163a0ef78db8a049fa24e83c2d5e923387`, but observation timed out with 4 unresolved carryover Codex P1 threads from reviewed commit `40af0ea3fe`. |
| P1 repair scope | safe ZIP extraction rejects symlinked extract dirs; pack review rejects unsafe text payloads; provenance repository/ref must match preflight; selected skeleton fill rejects nested `authorized_profile` claims. |
| P1 repair evidence | focused authoring-pack suite `215 passed`; `make lint` pass; `spec-dock validate` pass; `git diff --check` pass |
| final observation | CI pass and no current P0/P1. Current P2 threads remain non-blocking; old P1 threads are fixed by code and not re-raised as current P1, but some GitHub conversation threads remain unresolved. |

## Terminal Non-Blocking Review Findings

| root_cause_family | priority | merge_blocking | branch_mutation | durable disposition |
|---|---|---|---|---|
| `expected-root-contract-drift` | P2 | no | no | deferred coverage decision: track as post-merge hardening. Candidate fix is to reject non-canonical roots in preflight or make review honor configured root. Not fixed in this PR because latest current review has no P0/P1 and merge-preparer policy avoids branch mutation solely for P2. |
| `stale-if-schema-contract-drift` | P2 | no | no | deferred coverage decision: track as post-merge hardening. Candidate fix is to reject or normalize non-reviewable `stale_if` shapes before preflight pass. Not fixed in this PR because it is a preflight/review contract hardening item, not a current merge blocker. |
| `tree-hardlink-type-check` | P2 | no | no | deferred coverage decision: track as post-merge hardening. Candidate fix is to reject hardlinked tree entries in fallback tree review. Not fixed in this PR because ZIP path safety P1 was fixed and this remaining tree fallback case is P2. |
| `source-manifest-superset-check` | P2 | no | no | deferred coverage decision: track as post-merge hardening. Candidate fix is to require pack source set to equal preflight source set or explicitly reject/stale extras. Not fixed in this PR because it is non-blocking provenance hardening after P1 provenance binding was fixed. |

Terminal P2/P3 policy: latest observation contains no current P0/P1 and no CI failure, so the PR branch is not mutated solely for these P2 findings. `review-clean: no`; `merge-prepared for human judgment: yes`; `branch mutation: no`; `ci rerun avoided: yes` for P2-only findings.

Traceability rule: the table above is the durable deferred-coverage record for the terminal P2 set. It intentionally records why each item is not part of the final PR repair loop and preserves the concrete follow-up fix direction without creating another branch mutation cycle in `iss-00293`.

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
| Codex PR review / PRRT_kwDOQ99OK86Oy07h | reject symlinked extract directories | P1 | fixed locally | `_safe_extract_zip` rejects symlinked or non-directory `extract_dir`; `test_symlinked_extract_dir_is_blocked_before_writing` confirms no write through symlink target |
| Codex PR review / PRRT_kwDOQ99OK86Oy07j | reject unsafe text in pack payloads | P1 | fixed locally | `_text_payload_error` applies unsafe text policy to decoded payloads; `test_unsafe_text_payload_is_rejected_without_echoing_payload` confirms raw transcript / host-local path rejection and redaction |
| Codex PR review / PRRT_kwDOQ99OK86Oy07m | require provenance to match preflight repository | P1 | fixed locally | provenance schema now compares `repository.full_name` and `requested_ref` with preflight; `test_provenance_repository_must_match_preflight_repository` covers mismatch |
| Codex PR review / PRRT_kwDOQ99OK86Oy07r | reject nested `authorized_profile` claims | P1 | fixed locally | candidate fill metadata now rejects `authorized_profile` recursively; `test_nested_candidate_authorized_profile_field_is_rejected` covers nested target claim |

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
| tc-005 | pass | PR URL / CI / review / mergeable status | PR #294 open, ready, base `main`, head `9a1f939c106f5bc48b9280ac5718700223746ab2`; CI 4/4 success; current Codex review has P2 non-blocking findings only; `gh pr view` reports `MERGEABLE` / `CLEAN`. | closed; record P2 follow-up / conversation residual risk |
| tc-006 | pass | Epic / Issue report 更新 / docs impact | Issue / Epic report updated with PR delivery, CI repair, P1 repair, terminal P2 findings, mergeability evidence, and final reviewer disposition. | commit / push this report-only evidence update |
| tc-007 | corrective-action-recorded | fresh reviewer results / blocker disposition | final code-reviewer `019f3b1d-ece6-7681-bbfc-165c6a8c2c39` pass with P2 only。final spec-reviewer `019f3b1d-c36f-76b2-886e-b4a84a2f629f` and qa-reviewer `019f3b1e-4184-7da1-b712-d3434dd81136` found workflow P1 because final evidence was local-only and the ledger was pending; this report update is the corrective action. | commit / push and run post-push final confirmation |

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
