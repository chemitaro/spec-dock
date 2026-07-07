---
種別: 実装報告書（Issue）
ID: "iss-00298"
タイトル: "GitHub Sync Preflight"
関連GitHub: ["#298"]
状態: "execution-complete"
作成者: "iwasawayuuta"
最終更新: "2026-07-08"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00295", "init-local-00003"]
---

# iss-00298 GitHub Sync Preflight — 実装報告

この文書は観測証跡台帳である。`requirement.md`、`design.md`、`plan.md` は planned contract を持ち、この文書は draft adoption、reviewer gate、実装中の観測結果、verification、commit、Issue finish、PR defer evidence を記録する。

## 仕様解釈・判断台帳（Spec Interpretation / Decision Ledger）

| ID | Status | Type | Raised By | Gap | Options | Decision | Rationale | Disposition | Evidence | Follow-up |
|---|---|---|---|---|---|---|---|---|---|---|
| D-001 | resolved | scope | orchestrator | draft は GitHub connector-visible HEAD を要求しているが、この Issue では実 connector invocation まで実装すると `backend invocation` scope に食い込む | A: 実 connector をこの Issue で呼ぶ; B: remote tracking comparison と adapter slot を実装し、実 connector invocation は後続に残す | B を採用 | 本 Issue は preflight gate の core contract 実装が目的で、backend / connector invocation は `iss-00300` に分離されているため | applied | `design.md` §3.2, §3.4 | none |
| D-002 | resolved | operation | orchestrator | 同期できない場合の実行許容をどう扱うか | A: fail only; B: broad force; C: explicit `local-context` evidence mode | C を採用 | ユーザー要望と Epic 要件は同期不能時の作業継続を許すが、GitHub synced evidence と同じ authority にはしないため | applied | `requirement.md` RQ-010/RQ-011/RQ-012; `design.md` §2, §3.2.1, §3.5; `plan.md` SLCI-007 | none |
| D-003 | resolved | test-strategy | spec-reviewer | source hash mismatch の baseline が未定義で、RQ-008 が観測不能だった | A: source hash mismatch を後続へ defer; B: expected manifest/hash option を本 Issue の baseline とする | B を採用 | preflight の stale 判定をこの Issue で検証可能にするため | applied | `requirement.md` RQ-008/RQ-009; `design.md` §3.2.1; `plan.md` SLCI-006 | none |
| D-004 | resolved | operation | spec-reviewer | `local-context` provenance が抽象的で broad force bypass 化するリスクがあった | A: mode のみ残す; B: provided context / diff / unsynced reason を必須 provenance とする | B を採用 | GitHub sync を検証しない低 authority evidence として境界を固定するため | applied | `requirement.md` RQ-012; `design.md` §3.2.1, §3.5; `plan.md` SLCI-007 | none |
| D-005 | resolved | test-strategy | spec-reviewer | connector/default-branch failure coverage が plan closure に不足していた | A: connector failure を後続に defer; B: adapter/fake observer と default-branch unknown fixture で本 Issue の fail-closed contract を閉じる | B を採用 | 実 connector invocation は後続へ残しつつ、preflight use case の observer failure semantics は本 Issue で検証できるため | applied | `design.md` §4.1; `plan.md` SLCI-004, TC-010, TC-011 | none |
| D-006 | resolved | test-strategy | spec-reviewer | source manifest の path / per-path hash provenance が closure test に固定されていなかった | A: opaque manifest hash だけ検証; B: default inventory、`source_paths`、per-path `source_hashes`、manifest hash をテスト義務化 | B を採用 | RQ-007 は対象 source path と content hash を含む manifest を求めており、opaque hash だけでは誤った inventory を検出できないため | applied | `plan.md` SLCI-006, TC-016 | none |
| D-007 | resolved | test-strategy | spec-reviewer | step-local concrete test-case cards が不足し、global test matrix から worker が推論する必要があった | A: global TC matrix のまま進める; B: HC-S02 から HC-S99 に premise / operation / expected / failure detection / verification method を持つ step-local test cards を追加する | B を採用 | `spec-dock/docs/authoring/issue-plan.md` が step-local concrete cases を required handoff としているため | applied | `plan.md` §6 Step-local handoff cards | none |
| D-008 | resolved | test-strategy | spec-reviewer | step-local concrete cases が横長 table 形式で、issue-plan schema の card-style requirement に合っていなかった | A: table 形式のまま進める; B: 各 test case を top-level bullet card に変換する | B を採用 | `spec-dock/docs/authoring/issue-plan.md` が horizontal table を reviewer fail condition としているため | applied | `plan.md` §6 Step-local handoff cards | none |
| D-009 | resolved | implementation | dev-coder / orchestrator | CLI contract に expected-origin option はないが、origin mismatch failure を観測可能にする必要があった | A: expected origin option を追加する; B: upstream が `origin/*` 以外を tracking している状態を `origin_mismatch` として扱う | B を採用 | 本 Issue の CLI surface を approved plan に限定しつつ、GitHub-visible authoring の前提である origin tracking 逸脱を fail-closed で検出できるため | applied | `github_sync_preflight.py`, `tests/cli_runtime/test_authoring.py::test_authoring_preflight_github_sync_blocks_non_origin_upstream` | future expected-origin semantics が必要になった場合は別 Issue で再設計 |
| D-010 | resolved | workflow-metadata | spec-reviewer / orchestrator | `.assurance.json` の working-tree diff が runtime command の forbidden mutation と混同される | A: `.assurance.json` を戻して `assurance verify` stale を許容する; B: authoring runtime command mutation と workflow-owned source binding refresh を区別する | B を採用 | `assurance verify` は最新 requirement/design/plan の source binding を要求するため、workflow metadata refresh は Issue closure gate の一部であり、authoring runtime command の権限拡張ではない | applied | `requirement.md`, `design.md`, `plan.md`, `./spec-dock/scripts/spec-dock assurance classify --stage requirement` | none |

## 証跡採用台帳（Evidence Adoption Ledger）

| ID | adoption_status | source | target | rationale | evidence | next_action |
|---|---|---|---|---|---|---|
| EAL-001 | adopted | ChatGPT ZIP draft requirement | `requirement.md` | fail-closed GitHub sync preflight、`local-context` authority、PR defer の主要要件が親 Epic と一致したため採用 | `artifacts/20260707t171243z-draft-requirement-implement-github-sync-preflight-draft-requirement.md` | fresh spec-reviewer |
| EAL-002 | adopted | ChatGPT ZIP draft design | `design.md` | scope / non-scope、target runtime boundary、failure modes、validation impact を採用し、connector invocation は adapter slot に調整した | `artifacts/20260707t171243z-01-draft-design-implement-github-sync-preflight-draft-design.md` | fresh spec-reviewer |
| EAL-003 | adopted | ChatGPT ZIP draft plan | `plan.md` | step sequence と verification focus を採用し、Spec-Locked Closure Index と relay policy を追加して executable plan にした | `artifacts/20260707t171243z-02-draft-plan-implement-github-sync-preflight-draft-plan.md` | fresh spec-reviewer |

## 目的整合台帳（Objective Alignment Ledger）

| 対象 | primary objective evidence | secondary requirement evidence | inversion risk | reviewer verdict |
|---|---|---|---|---|
| GitHub sync preflight | `requirement.md` §1-§6 が repo-aware invocation 前の fail-closed gate を主目的としている | `local-context` mode と PR defer は主目的を補助する境界として記載 | low | pass |

## 仕様 authoring ゲート（Spec Authoring Gate）

| phase | investigated facts | open questions / answers | adoption decision | reviewer verdict | blocking | promotion / next_action |
|---|---|---|---|---|---|---|
| requirement | 親 Epic 要件、issue draft requirement、assurance classify 結果 | open question なし。Issue grade は `standard`。 | draft requirement を正式 requirement へ採用 | pass | no | execute approved plan |
| design | issue draft design、親 Epic non-scope、provider/dogfood source-of-truth boundary | connector invocation は後続 Issue へ残す | draft design を調整して正式 design へ採用 | pass | no | execute approved plan |
| plan | issue draft plan、SpecDock issue execution policy、中間 PR defer policy | open question なし | draft plan を executable plan へ採用 | pass | no | execute approved plan |

## 委任ドラフト証跡（Delegated Draft Evidence）

| created_by_role | scope_id | artifact draft path | source_paths | intended_targets | adoption_status | reflected_to | diff_guard_result | integration result | rejected portions | blockers | reviewer result | promotion decision |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ChatGPT ZIP authoring | iss-00298 | `artifacts/20260707t171243z-draft-requirement-implement-github-sync-preflight-draft-requirement.md` | `epic-00295/requirement.md`, `epic-00295/plan.md` | `requirement.md` | adopted | [`requirement.md`] | manual diff inspection pass | integrated | none | none | pass | execute approved plan |
| ChatGPT ZIP authoring | iss-00298 | `artifacts/20260707t171243z-01-draft-design-implement-github-sync-preflight-draft-design.md` | `requirement.md`, `epic-00295/design.md` | `design.md` | adopted | [`design.md`] | manual diff inspection pass | integrated with connector boundary adjustment | direct connector invocation in this Issue | none | pass | execute approved plan |
| ChatGPT ZIP authoring | iss-00298 | `artifacts/20260707t171243z-02-draft-plan-implement-github-sync-preflight-draft-plan.md` | `requirement.md`, `design.md` | `plan.md` | adopted | [`plan.md`] | manual diff inspection pass | integrated with SLCI / relay policy | none | none | pass | execute approved plan |

## ワークフロー単位の named role 許可（Workflow-Scoped Authorization）

| authorization source | repo/worktree | active issue | session | named roles | boundary | expires / invalidation condition | denied / unavailable / host conflict reason | next action |
|---|---|---|---|---|---|---|---|---|
| ユーザーによる Epic 実装依頼 | `/Users/iwasawayuuta/.codex/worktrees/aa9c/spec-dock` | iss-00298 | current session | spec-reviewer / code-reviewer / qa-reviewer / dev-coder / doc-writer | active repo/worktree、active SpecDock scope、current session、SpecDock-defined role responsibility に限定。外部公開、credentialed mutation、scope expansion は含まない | issue complete / scope change / user revocation | none | continue workflow |

## グレード別専門家証跡ゲート（Grade Specialist Evidence Gate）

| Grade | required specialist / fallback | usage | evidence | fresh spec-reviewer verdict | execution readiness |
|---|---|---|---|---|---|
| standard | manual authoring fallback | used | manual evidence from `EAL-001` から `EAL-003`、`requirement.md`、`design.md`、`plan.md` | pass | ready |

## 実装記録（Session Log）

### Planning session 2026-07-08

#### 対象

- Phase: Issue planning
- AC/EC: requirement / design / plan formalization

#### 実施内容

- active issue が `iss-00298` であることを確認した。
- `guidance issue-planning` / `guidance issue-execution` が `requirement-capture` / `requirement-scaffold` を返し、実装不可であることを確認した。
- draft requirement / design / plan artifacts を読み、正式 `requirement.md` / `design.md` / `plan.md` へ採用した。
- `assurance classify --stage requirement` で `authorized_profile: standard` を確認した。
- `assurance compose --artifact all` で planning artifact template を合成した後、issue 固有 contract に置き換えた。

#### 実行コマンド / 結果

```bash
./spec-dock/scripts/spec-dock guidance issue-planning
# state=requirement-capture, next_action=requirement-capture-required, may_execute_approved_plan=false

./spec-dock/scripts/spec-dock assurance classify --stage requirement
# authorized_profile=standard

./spec-dock/scripts/spec-dock assurance compose --artifact all
# changed design.md, plan.md, report.md
```

## Verification Evidence

| Command / check | Scope | Observed result | Evidence owner | Notes |
|---|---|---|---|---|
| `uv run pytest tests/cli_runtime/test_authoring.py` | focused authoring CLI/runtime behavior | pass, `32 passed` | orchestrator | Clean synced, dirty/staged/untracked, ahead/behind/diverged, missing branch, origin mismatch, connector unavailable observer, fallback, github-synced/local-context source hash mismatch, Python cache exclusion, exact negative exit codes, default inventory smoke, `local-context`, forbidden authority claim, dogfood path smoke を含む |
| `uv run pytest tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_mirror_match_provider_assets` | provider / dogfood mirror parity | pass, `1 passed` | orchestrator | installed dogfood runtime mirror が provider assets と一致することを確認 |
| `./spec-dock/scripts/spec-dock validate` | SpecDock graph validation | pass, `spec-dock: ok (validate) nodes=202` | orchestrator | issue / epic graph の破損なし |
| `git diff --check` | whitespace / patch hygiene | pass | orchestrator | output なし |
| `./spec-dock/scripts/spec-dock authoring preflight github-sync --repo-root . --evidence-mode local-context --diff-summary smoke --unsynced-reason local-smoke --format json` | dogfood CLI smoke | pass | orchestrator | `github_sync=not_verified`, `sync_state=local_context`; `source_hashes` に `__pycache__` / `.pyc` が含まれないことを確認 |
| `./spec-dock/scripts/spec-dock authoring pack prepare` | deferred command smoke | expected non-zero, deferred | orchestrator | `status=deferred`, `authority=evidence_only`, `next_issue=iss-00299` を確認 |
| `./spec-dock/scripts/spec-dock assurance classify --stage requirement` | workflow-owned source binding refresh | pass | orchestrator | authoring runtime command の mutation ではなく、latest canonical docs に対する assurance source binding refresh |
| `./spec-dock/scripts/spec-dock assurance verify` | workflow-owned source binding verification | pass | orchestrator | D-010 の判断に基づき、latest canonical docs と `.assurance.json` source binding が一致することを確認 |

## Step Contract Closure

| Step | Closure IDs | Plan close condition | Observed evidence | Result | Notes |
|---|---|---|---|---|---|
| S01 | investigation | target file list and fixture strategy are recorded before S02 starts | inspected provider `commands/authoring.py`, `tests/cli_runtime/test_authoring.py`, `tests/cli_runtime/harness.py`, existing git fixture usage, and authoring_pack directories | pass | Existing `authoring` command is deferred skeleton; focused tests live in `tests/cli_runtime/test_authoring.py`; `CliRuntimeHarness` provides `_run_git` and `_init_origin_repo`; authoring_pack application/domain directories exist with only `__init__.py`; presentation authoring_pack directory is absent and may be added. |
| S02-S04 | SLCI-001 through SLCI-008 | domain contract, local git observation, CLI options, diagnostics, and `local-context` behavior are implemented with focused tests | provider runtime files, dogfood mirror files, and `tests/cli_runtime/test_authoring.py` updated; focused pytest passes | pass | Other authoring commands remain deferred/fail-closed. Backend invocation, ZIP review/stage, adoption, authoring runtime command assurance mutation, reviewer-pass, execution-ready, PR-ready are not implemented by this Issue. |
| S05 | SLCI-009 | provider and dogfood mirror parity is preserved | mirror parity unit test passes; dogfood installed path smoke is covered by focused authoring test | pass | New authoring_pack presentation/application/domain files exist in provider and dogfood mirror. |
| S90 | SLCI-010 | report records no-per-Issue-PR rationale and final quality Issue defer | PR delivery defer evidence points to `iss-00307`; this row records closure | pass | No PR is created for this intermediate Issue. |

## Test Contract Closure

| Closure ID / Test ID | Step | Required | Evidence level | Pre-implementation evidence | Verification command or alternative path | Observed result | Notes |
|---|---|---|---|---|---|---|---|
| S01 investigation | S01 | yes | inspect-only | inspected existing runtime/test/git fixture pattern before implementation | direct file inspection and `rg` output | pass | No production code changes in S01. |
| SLCI-001 | S03 | yes | focused pytest | clean local repo fixture with upstream branch at same HEAD | `uv run pytest tests/cli_runtime/test_authoring.py` | pass | JSON payload includes `status=pass`, `sync_state=synced`, requested/effective ref, matching local/remote HEAD, and source manifest hash. |
| SLCI-002 | S03 | yes | focused pytest | dirty tracked, staged, and untracked fixture cases | `uv run pytest tests/cli_runtime/test_authoring.py` | pass | Each unsafe worktree state returns `blocked` with the expected blocker. |
| SLCI-003 | S03 | yes | focused pytest | ahead, behind, and diverged fixture cases | `uv run pytest tests/cli_runtime/test_authoring.py` | pass | ahead/diverged block; behind returns stale with blocker/remediation. |
| SLCI-004 | S03 | yes | focused pytest | missing remote branch, non-origin upstream, connector unavailable observer, default branch unknown | `uv run pytest tests/cli_runtime/test_authoring.py` | pass | Failure modes are fail-closed and do not claim verified synced evidence. |
| SLCI-005 | S04 | yes | focused pytest | unresolved requested ref with and without fallback | `uv run pytest tests/cli_runtime/test_authoring.py` | pass | Fallback is opt-in and records distinct requested/effective refs. |
| SLCI-006 | S02/S04 | yes | focused pytest | expected source hash / manifest mismatch, no baseline, default inventory | `uv run pytest tests/cli_runtime/test_authoring.py` | pass | Mismatch returns stale; no baseline records `source_hash_mismatch_checked=false`; output includes paths, per-path hashes, and manifest hash. |
| SLCI-007 | S04 | yes | focused pytest | `local-context` with provenance and missing-provenance cases | `uv run pytest tests/cli_runtime/test_authoring.py` | pass | Valid local-context emits low-authority provenance; missing unsynced reason or missing context/diff blocks. |
| SLCI-008 | S02/S04 | yes | focused pytest / output inspection | pass, blocked, stale, and local-context diagnostics | `uv run pytest tests/cli_runtime/test_authoring.py` | pass | Diagnostics avoid forbidden authority claims. |
| SLCI-009 | S05 | yes | focused pytest / mirror parity | provider and dogfood runtime paths after implementation | `uv run pytest tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_mirror_match_provider_assets` | pass | Dogfood installed runtime mirror matches provider assets. |
| SLCI-010 | S90 | yes | report inspection | final issue report before finish | direct report inspection | pass | `PR delivery defer evidence` records no per-Issue PR and final quality Issue `iss-00307`. |

## Closure Coverage

| Closure ID | Step | Verification evidence | Observed result | Notes |
|---|---|---|---|---|
| S01 investigation | S01 | provider/test/harness inspection | pass | Enables S02-S05 implementation delegation. |
| SLCI-001 through SLCI-008 | S02-S04 | focused CLI/runtime test suite | pass | `tests/cli_runtime/test_authoring.py` reports `32 passed`, including Python cache exclusion, local-context source hash mismatch stale handling, exact negative exit-code assertions, and default inventory coverage. |
| SLCI-009 | S05 | mirror parity test and dogfood path smoke | pass | Mirror parity unit test reports `1 passed`; dogfood path smoke is included in focused CLI/runtime test suite. |
| SLCI-010 | S90 | report PR defer evidence | pass | Intermediate PR delivery remains deferred to `iss-00307`. |

## Implementation Delegation Gate

| Step | decision | required reason | delegated role | delegated scope | source of truth | allowed changes | forbidden changes | required verification | stop conditions | output required | observed result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S02-S05 | delegated | runtime / CLI / tests / shipped scaffold behavior | dev-coder | provider authoring preflight runtime, dogfood mirror, focused CLI tests | `requirement.md`, `design.md`, `plan.md` | provider runtime authoring files, authoring_pack application/domain/presentation files, mirror paths, focused tests | backend invocation, prompt pack prepare, ZIP review/stage, adoption, `.assurance.json` mutation, reviewer-pass / execution-ready / PR-ready claims | focused pytest, mirror parity test, `git diff --check` | scope expansion, credentialed GitHub use, forbidden command implementation, unable fixture | changed files, commands, results, unresolved risks | pass: worker implemented only `authoring preflight github-sync`, left other authoring commands deferred, and reported focused tests / parity / validate / diff-check passing; orchestrator re-ran verification and adopted D-009 |

## Reviewer Gate Status

| Gate ID | Gate | Reviewer role | Freshness | State | Risk acceptance | Promotion decision | Evidence |
|---|---|---|---|---|---|---|---|
| RG-PLAN-001 | planning spec review | spec-reviewer | fresh | pass | no | execute approved plan | 019f3dfb-fcd8-7632-9732-dcb054852857 review_status pass |
| RG-CODE-001 | implementation code review | code-reviewer | fresh | pass | no | commit allowed after all gates pass | 019f3e0c-a8d3-7490-903a-db5e3f8f68d2 review_status pass; prior P1 local-context source hash mismatch skip fixed |
| RG-QA-001 | implementation QA review | qa-reviewer | fresh | pass | no | commit allowed after all gates pass | 019f3e0c-a9e1-72f1-8b2b-eb208c2adf18 review_status pass; prior P1 exact exit-code gap fixed; remaining P2 default inventory assertion strengthening accepted as non-blocking |
| RG-SPEC-002 | final spec/report review | spec-reviewer | fresh | pass | no | commit and issue finish allowed | 019f3e0c-aac2-7691-8c49-3f44236ad076 review_status pass; D-010 workflow-owned assurance refresh distinction and `assurance verify` evidence accepted |

## Reviewer Gate History

| Gate | Status | Evidence | Next action |
|---|---|---|---|
| planning spec-reviewer attempt 1 | fail | P1: source-hash baseline 未定義、step handoff 不足、local-context provenance 不足 | docs updated and fresh re-review |
| planning spec-reviewer attempt 2 | fail | P1: unsynced reason 必須化不足、connector/default-branch failure coverage 不足 | docs updated and fresh re-review |
| planning spec-reviewer attempt 3 | fail | P1: step-local handoff schema 不足、P2: local-context diagram、P3: stale trace reference | docs updated and fresh re-review |
| planning spec-reviewer attempt 4 | fail | P1: source manifest path/hash provenance closure 不足、P2: S05 parity test reference mismatch | docs updated and fresh re-review |
| planning spec-reviewer attempt 5 | fail | P1: step-local concrete test-case cards 不足、P2: HC-S02 verification ID mismatch | docs updated and fresh re-review |
| planning spec-reviewer attempt 6 | fail | P1: step-local concrete cases が horizontal table 形式 | docs updated and fresh re-review |
| planning spec-reviewer attempt 7 | pass | no findings; step-local card-style tests and prior fixes verified | execution handoff ready |
| final code-reviewer attempt 1 | fail | P1: `local-context` returned before expected source hash mismatch check | fixed and re-review requested |
| final qa-reviewer attempt 1 | fail | P1: negative preflight states did not assert exact exit code; P2: default source inventory not covered without `--source-path` | fixed and re-review requested |
| final spec-reviewer attempt 1 | fail | P1: `.assurance.json` mutation ambiguity in diff; P1: final reviewer gate rows absent | fixed by D-010 workflow-owned assurance refresh distinction and reviewer gate rows; re-review requested |
| final code-reviewer attempt 2 | pass | no actionable implementation / scope / parity / test adequacy defects | accepted |
| final qa-reviewer attempt 2 | pass | P2 default inventory full assertion strengthening only; no blocking QA finding | accepted |
| final spec-reviewer attempt 2 | fail | P1: `assurance verify` pass not recorded for D-010; P2: stale row said `.assurance.json` diff removed | fixed and re-review requested |
| final spec-reviewer attempt 3 | pass | no findings; D-010 assurance refresh distinction, reviewer gate rows, verification evidence, provider/dogfood parity, and PR defer verified | accepted |

## PR delivery defer evidence

この Issue は中間 Issue のため PR delivery を行わない。Epic-level PR delivery、CI / review repair、mergeable PR 作成は final quality gate Issue `iss-00307` で実施する。
