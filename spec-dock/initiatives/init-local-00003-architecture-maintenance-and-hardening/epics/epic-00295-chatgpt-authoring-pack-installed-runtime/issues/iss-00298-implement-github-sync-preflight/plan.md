---
種別: 実装計画書（Issue）
ID: "iss-00298"
タイトル: "GitHub Sync Preflight"
関連GitHub: ["#298"]
状態: "planning-ready"
作成者: "iwasawayuuta"
最終更新: "2026-07-08"
依存: ["requirement.md", "design.md"]
親: ["epic-00295", "init-local-00003"]
Issue Grade: "standard"
---

# iss-00298 GitHub Sync Preflight — Issue 実装計画書

## 1. 実行前提

この計画は、`requirement.md` と `design.md` が fresh `spec-reviewer` pass を得た後に実行する。実行中の観測結果、Red / Green / Refactor、reviewer output、commit evidence、Issue finish evidence は `report.md` に記録する。

実装開始前 gate:

- `./spec-dock/scripts/spec-dock guidance issue-execution` が execution を許可している。
- `requirement.md` / `design.md` / `plan.md` が template-only ではない。
- draft artifacts の採用判断が `report.md` に記録されている。
- 中間 Issue として PR delivery を行わない方針が記録されている。

## 2. 変更範囲

### 2.1 許可変更

| 種別 | パス | 変更内容 | 関連Design |
|---|---|---|---|
| provider runtime | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/authoring.py` | `authoring preflight github-sync` を deferred skeleton から実 command へ接続 | DES-CLI |
| provider runtime | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/authoring_pack/` | preflight use case を追加 | DES-APP |
| provider runtime | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/` | preflight contract / source manifest contract を追加 | DES-DOM |
| provider runtime | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/authoring_pack/` | diagnostics rendering を追加 | DES-PRES |
| dogfood mirror | `spec-dock/scripts/spec_dock_runtime/commands/authoring.py`、`spec-dock/scripts/spec_dock_runtime/application/authoring_pack/`、`spec-dock/scripts/spec_dock_runtime/domain/authoring_pack/`、`spec-dock/scripts/spec_dock_runtime/presentation/authoring_pack/` | provider runtime と同じ installed behavior を反映 | DES-PARITY |
| tests | `tests/cli_runtime/test_authoring.py` または `tests/cli_runtime/test_authoring_preflight.py` | hermetic git fixture による focused CLI/runtime tests | DES-TEST |
| report | `spec-dock/active/issue/report.md` | 実行証跡、reviewer evidence、PR defer evidence を記録 | DES-EVD |

### 2.2 禁止変更

| 対象 | 禁止理由 | 必要になった場合 |
|---|---|---|
| ChatGPT backend invocation | `iss-00300` の責務 | 停止して follow-up / issue boundary を記録 |
| ZIP review / staging | `iss-00301` の責務 | 停止して follow-up / issue boundary を記録 |
| canonical docs 自動 adoption | Epic authority boundary に反する | 停止して再計画 |
| `.assurance.json` mutation command | authoring runtime command が reviewer/assurance authority を持たない | 停止して再計画 |
| workflow-owned `.assurance.json` source binding refresh | planning / execution gate を成立させる SpecDock workflow metadata であり、authoring runtime command の機能ではない | `assurance classify` / `assurance verify` の証跡を report に記録する |
| broad `--force` / `-f` bypass | `local-context` を低 authority mode として分離する設計に反する | 停止して再計画 |
| 中間 Issue の PR 作成 | final quality Issue `iss-00307` に defer する Epic policy | report に defer evidence を記録 |

## 3. Spec-Locked Closure Index

| ID | Owner step | Requirement / Design trace | Observable input / state | Locked expectation | Evidence level | Report destination | Required |
|---|---|---|---|---|---|---|---|
| SLCI-001 | S03 | RQ-001, RQ-002, AC-001, AC-002 | clean local repo fixture with upstream branch at same HEAD | `status=pass`, requested/effective ref, local HEAD, remote HEAD, source manifest hash are emitted | red-required | `report.md#Test Contract Closure` | yes |
| SLCI-002 | S03 | RQ-003, AC-003 | dirty tracked, staged, and untracked fixture cases | each unsafe worktree state returns `status=blocked` with blocker reason | red-required | `report.md#Test Contract Closure` | yes |
| SLCI-003 | S03 | RQ-004, AC-004 | ahead, behind, and diverged fixture cases | ahead/diverged return `blocked`; behind returns `stale` or `blocked` with remediation | red-required | `report.md#Test Contract Closure` | yes |
| SLCI-004 | S03 | RQ-005, AC-005 | missing upstream/remote branch, origin mismatch, connector unavailable, and default branch unknown fixtures | command or application use case fails closed and does not claim synced evidence | red-required | `report.md#Test Contract Closure` | yes |
| SLCI-005 | S04 | RQ-006, AC-006, AC-007 | requested ref cannot be resolved; fallback flag toggled | no fallback without opt-in; opt-in records distinct requested/effective ref | red-required | `report.md#Test Contract Closure` | yes |
| SLCI-006 | S02/S04 | RQ-007, RQ-008, RQ-009, AC-008, AC-009 | expected source hash / expected manifest fixtures, no-baseline fixture, and default inventory fixture | mismatch returns `stale`; no baseline emits `source_hash_mismatch_checked: false`; output includes `source_paths`, per-path `source_hashes`, and manifest hash for the actual inventory | red-required | `report.md#Test Contract Closure` | yes |
| SLCI-007 | S04 | RQ-010, RQ-011, RQ-012, AC-010, AC-011 | `local-context` with unsynced reason plus provided paths/diff, and missing-provenance cases | valid local-context emits required provenance; missing unsynced reason or missing context/diff is `blocked` | red-required | `report.md#Test Contract Closure` | yes |
| SLCI-008 | S02/S04 | RQ-013, AC-012 | JSON/text outputs for pass, blocked, stale, local-context | output lacks canonical adoption, reviewer pass, execution-ready, PR-ready claims | inspect plus tests | `report.md#Closure Coverage` | yes |
| SLCI-009 | S05 | AC-013 | provider and dogfood runtime paths after implementation | mirror parity check passes and relevant CLI tests use installed path | command verification | `report.md#Verification Evidence` | yes |
| SLCI-010 | S90 | AC-014 | final issue report before finish | report records no-per-Issue-PR rationale and `iss-00307` defer | inspection | `report.md#PR delivery defer evidence` | yes |

## 4. テストケース配置方針

具体テストケースは issue-wide table ではなく、`## 6. Step-local handoff cards` の各 implementation step に card-style nested list として置く。各 case は `前提`、`操作`、`期待結果`、`失敗検出`、`検証方法`、`関連 closure id` を持つ。

## 5. 実装ステップ

### S01: runtime / test pattern 調査

| Field | Contract |
|---|---|
| depends on | planning spec-reviewer pass |
| unblocks | S02 |
| target files | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/authoring.py`, `tests/cli_runtime/test_authoring.py`, nearby git fixture tests |
| planned obligation | 既存 dispatch / deferred skeleton / fixture pattern を確認し、実装先を確定する |
| pre-implementation evidence | `rg` / file inspection output summary |
| bounded implementation batch | 調査と report 記録のみ。production code は変更しない |
| verification path | direct inspection; no tests required |
| report destination | `report.md#実装記録`, `report.md#Step Contract Closure` |
| amendment trigger | 既存 command architecture が想定と異なる場合 |
| delegation contract | parent may inspect directly; no worker required |

### S02: domain contract / source manifest baseline

| Field | Contract |
|---|---|
| depends on | S01 |
| unblocks | S03, S04 |
| target files | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/preflight_contract.py`, `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/source_manifest.py`, mirrored dogfood paths, focused tests |
| planned obligation | status/evidence mode/source baseline/forbidden authority contract を定義する |
| pre-implementation evidence | failing tests for source manifest hash and forbidden authority output |
| bounded implementation batch | domain dataclasses/functions and serialization only |
| verification path | TC-014, TC-015, TC-016, TC-020 |
| report destination | `report.md#TDD Evidence`, `report.md#Test Contract Closure` |
| amendment trigger | source baseline needs external pack metadata not available in this Issue |
| delegation contract | dev-coder allowed for domain/test files; parent integrates and records evidence |

### S03: local git observation / remote comparison

| Field | Contract |
|---|---|
| depends on | S02 |
| unblocks | S04 |
| target files | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/authoring_pack/github_sync_preflight.py`, possible infra helper, mirrored dogfood paths, CLI runtime tests |
| planned obligation | clean/synced, dirty, staged, untracked, ahead, behind, diverged, missing remote, origin mismatch を判定する |
| pre-implementation evidence | failing git fixture tests TC-001 through TC-009 |
| bounded implementation batch | local git command observation and result mapping only; no backend connector invocation |
| verification path | TC-001 through TC-011 |
| report destination | `report.md#TDD Evidence`, `report.md#Closure Coverage` |
| amendment trigger | hermetic fixture cannot represent a required git state |
| delegation contract | dev-coder allowed for runtime/test files; no docs/skill changes except report evidence |

### S04: CLI options / diagnostics / local-context

| Field | Contract |
|---|---|
| depends on | S02, S03 |
| unblocks | S05 |
| target files | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/authoring.py`, `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/authoring_pack/diagnostics.py`, mirrored dogfood paths, CLI tests |
| planned obligation | CLI options, exit code, text/JSON diagnostics, fallback handling, local-context provenance を接続する |
| pre-implementation evidence | failing CLI tests TC-010 through TC-016 |
| bounded implementation batch | authoring preflight command only; other authoring commands remain deferred |
| verification path | TC-012 through TC-020 |
| report destination | `report.md#TDD Evidence`, `report.md#Test Contract Closure` |
| amendment trigger | option shape conflicts with existing parser conventions |
| delegation contract | dev-coder allowed for command/presentation/test files; forbidden to implement backend invoke / ZIP stage |

### S05: provider / dogfood mirror parity

| Field | Contract |
|---|---|
| depends on | S04 |
| unblocks | S90 |
| target files | provider runtime files and `spec-dock/scripts/spec_dock_runtime/` mirror equivalents |
| planned obligation | provider source of truth and dogfood installed runtime behaviorを一致させる |
| pre-implementation evidence | provider/dogfood diff inventory |
| bounded implementation batch | mirror copy/patch only |
| verification path | TC-021 and existing mirror parity test |
| report destination | `report.md#Verification Evidence` |
| amendment trigger | provider and mirror intentionally diverge |
| delegation contract | parent may perform mirror patch; dev-coder can assist only within listed paths |

### S90: report / relay evidence

| Field | Contract |
|---|---|
| depends on | S05 |
| unblocks | S99 |
| target files | `spec-dock/active/issue/report.md` |
| planned obligation | draft adoption, SLCI closure, verification output, PR defer evidence を記録する |
| pre-implementation evidence | completed test output and reviewer outputs |
| bounded implementation batch | report-only update |
| verification path | report inspection and guidance issue-execution |
| report destination | this report |
| amendment trigger | any closure remains unproven |
| delegation contract | parent owned; no worker needed |

### S99: final local gate

| Field | Contract |
|---|---|
| depends on | S90 |
| unblocks | issue finish and next issue start |
| target files | no new implementation files unless reviewer findings require fixes |
| planned obligation | final local verification, reviewer gates, commit, post-commit clean check |
| pre-implementation evidence | all SLCI rows closed |
| bounded implementation batch | reviewer-finding fixes only; new behavior requires plan amendment |
| verification path | focused pytest, mirror parity test, `./spec-dock/scripts/spec-dock validate`, `git diff --check`, reviewer gates |
| report destination | `report.md#Reviewer Gate Status`, `report.md#Verification Evidence`, `report.md#PR delivery defer evidence` |
| amendment trigger | required reviewer finds P1/P0 or test coverage gap |
| delegation contract | code-reviewer / qa-reviewer / spec-reviewer are required gates; parent owns commit and issue finish |

## 6. Step-local handoff cards

### HC-S01: runtime / test pattern 調査

| Field | Contract |
|---|---|
| delegated role | parent-orchestrator direct inspection |
| input docs | `requirement.md`, `design.md`, `plan.md`, `spec-dock/docs/authoring/issue-plan.md`, existing `authoring.py`, existing `tests/cli_runtime` files |
| allowed paths | read-only inspection of `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/`, `spec-dock/scripts/spec_dock_runtime/`, `tests/cli_runtime/` |
| forbidden changes | production code edits, test edits, docs edits |
| concrete test cases | none; investigation step only |
| acceptance criteria | target file list and fixture strategy are recorded in `report.md` before S02 starts |
| required verification | inspection summary and `rg`/file-read evidence recorded |
| reviewer focus | spec-reviewer checks this plan; no code-reviewer needed for read-only inspection |
| stop conditions | existing architecture contradicts planned path; no hermetic git fixture pattern can be found |
| output required | report entry with source files inspected, selected test placement, and no material implementation decisions beyond the approved plan |

### HC-S02: domain contract / source manifest baseline

| Field | Contract |
|---|---|
| delegated role | dev-coder |
| input docs | `requirement.md` RQ-007 through RQ-014; `design.md` §3.2.1, §3.3; this plan SLCI-006 and SLCI-008 |
| allowed paths | provider/domain authoring_pack files, dogfood mirror domain files, focused CLI/runtime tests |
| forbidden changes | command parser behavior outside preflight, backend invocation, ZIP review/stage, canonical adoption command |
| concrete test cases | see the card-style list immediately below this HC-S02 contract |
| acceptance criteria | domain contract can serialize pass/blocked/stale/local-context results without forbidden authority claims |
| required verification | focused pytest for TC-014, TC-015, TC-016, TC-020 or equivalent test names recorded in report |
| reviewer focus | code-reviewer verifies deterministic serialization and forbidden-claim absence |
| stop conditions | expected source baseline requires pack metadata owned by later Issue; domain contract cannot represent no-baseline semantics |
| output required | changed files, tests run, unresolved risks, and Ledger Note if any design interpretation changed |

#### 具体テストケース一覧

- `TC-014` stale: expected source hash mismatch
  - 前提: computed manifest hash differs from `--expected-source-hash` or expected manifest hash.
  - 操作: run preflight serialization/use case with mismatched baseline.
  - 期待結果: `status=stale`, source hash mismatch blocker, no synced adoption claim.
  - 失敗検出: pass output, missing stale blocker, or missing expected/current hash fields.
  - 検証方法: focused pytest assertion on result dict / CLI JSON.
  - 関連 closure id: `SLCI-006`

- `TC-015` no-baseline: source mismatch is not claimed as checked
  - 前提: no expected manifest/hash is supplied.
  - 操作: compute source manifest for known files.
  - 期待結果: output includes current `source_manifest_hash` and `source_hash_mismatch_checked=false`.
  - 失敗検出: command claims mismatch was checked or omits manifest hash.
  - 検証方法: focused pytest assertion on result dict / CLI JSON.
  - 関連 closure id: `SLCI-006`

- `TC-016` provenance: source inventory path/hash output
  - 前提: default inventory fixture has two known text files.
  - 操作: compute source manifest.
  - 期待結果: output includes both `source_paths`, per-path `source_hashes`, and stable manifest hash.
  - 失敗検出: opaque-only hash, wrong path list, or missing per-path hash.
  - 検証方法: focused pytest comparing expected per-path hash values.
  - 関連 closure id: `SLCI-006`

- `TC-020` authority: serialized outputs avoid forbidden claims
  - 前提: serialized outputs for pass, blocked, stale, and local-context exist.
  - 操作: render text/JSON diagnostics.
  - 期待結果: no canonical adoption, reviewer pass, execution-ready, or PR-ready claim appears.
  - 失敗検出: forbidden authority tokens found in serialized output.
  - 検証方法: focused pytest scanning serialized strings and dict values.
  - 関連 closure id: `SLCI-008`

### HC-S03: local git observation / remote comparison

| Field | Contract |
|---|---|
| delegated role | dev-coder |
| input docs | `requirement.md` RQ-001 through RQ-006; `design.md` §3.2, §3.4, §4.1, §6; this plan SLCI-001 through SLCI-004 |
| allowed paths | provider/application authoring_pack preflight files, small infra helper if needed, dogfood mirror equivalents, CLI/runtime tests |
| forbidden changes | real GitHub connector invocation, credentialed network access, backend command execution, broad force bypass |
| concrete test cases | see the card-style list immediately below this HC-S03 contract |
| acceptance criteria | every unsafe state returns blocked/stale and no synced-evidence claim; clean synced fixture returns pass |
| required verification | focused pytest covering TC-001 through TC-011 |
| reviewer focus | code-reviewer verifies git-state coverage and no silent fallback |
| stop conditions | test fixture cannot model required state; implementation would need live GitHub mutation or credentials |
| output required | changed files, fixture strategy, test results, unresolved risks, and report closure rows for SLCI-001 through SLCI-004 |

#### 具体テストケース一覧

- `TC-001` positive: clean synced branch
  - 前提: local branch and upstream branch point to the same commit; worktree clean.
  - 操作: run preflight in `github-synced` mode.
  - 期待結果: `status=pass`, exit 0, local/remote heads and manifest hash emitted.
  - 失敗検出: missing pass status or missing head/provenance fields.
  - 検証方法: hermetic git fixture pytest via CLI.
  - 関連 closure id: `SLCI-001`

- `TC-002` negative: dirty tracked file
  - 前提: tracked file is modified but unstaged.
  - 操作: run preflight in `github-synced` mode.
  - 期待結果: `status=blocked`, dirty tracked blocker.
  - 失敗検出: command passes or reports unrelated blocker only.
  - 検証方法: hermetic git fixture pytest.
  - 関連 closure id: `SLCI-002`

- `TC-003` negative: staged file
  - 前提: staged file exists.
  - 操作: run preflight in `github-synced` mode.
  - 期待結果: `status=blocked`, staged blocker.
  - 失敗検出: command passes or omits staged blocker.
  - 検証方法: hermetic git fixture pytest.
  - 関連 closure id: `SLCI-002`

- `TC-004` negative: untracked file
  - 前提: untracked file exists.
  - 操作: run preflight in `github-synced` mode.
  - 期待結果: `status=blocked`, untracked blocker.
  - 失敗検出: command passes or omits untracked blocker.
  - 検証方法: hermetic git fixture pytest.
  - 関連 closure id: `SLCI-002`

- `TC-005` negative: local branch ahead
  - 前提: local branch is ahead of upstream.
  - 操作: run preflight in `github-synced` mode.
  - 期待結果: `status=blocked`, ahead/unpushed blocker.
  - 失敗検出: command passes or silently accepts unpushed commit.
  - 検証方法: hermetic git fixture pytest.
  - 関連 closure id: `SLCI-003`

- `TC-006` negative: local branch behind
  - 前提: local branch is behind upstream.
  - 操作: run preflight in `github-synced` mode.
  - 期待結果: `status=stale` or `blocked`, behind remediation.
  - 失敗検出: command passes or omits behind diagnosis.
  - 検証方法: hermetic git fixture pytest.
  - 関連 closure id: `SLCI-003`

- `TC-007` negative: diverged branch
  - 前提: local and upstream branches diverged.
  - 操作: run preflight in `github-synced` mode.
  - 期待結果: `status=blocked`, diverged blocker.
  - 失敗検出: command passes or treats as simple ahead/behind without blocker.
  - 検証方法: hermetic git fixture pytest.
  - 関連 closure id: `SLCI-003`

- `TC-008` negative: upstream branch missing
  - 前提: upstream branch is missing.
  - 操作: run preflight in `github-synced` mode.
  - 期待結果: `status=blocked`, branch missing blocker.
  - 失敗検出: command passes or falls back silently.
  - 検証方法: hermetic git fixture pytest.
  - 関連 closure id: `SLCI-004`

- `TC-009` negative: origin mismatch
  - 前提: observed origin URL differs from expected origin input/fixture metadata.
  - 操作: run preflight with expected origin mismatch.
  - 期待結果: `status=blocked`, origin mismatch blocker.
  - 失敗検出: command passes or omits origin mismatch.
  - 検証方法: hermetic git fixture or application fake observer pytest.
  - 関連 closure id: `SLCI-004`

- `TC-010` negative: connector unavailable
  - 前提: visible observer returns `connector_unavailable`.
  - 操作: run application use case with fake observer state.
  - 期待結果: `status=blocked`, connector unavailable blocker, no synced claim.
  - 失敗検出: command/use case passes or emits synced provenance.
  - 検証方法: application-level pytest.
  - 関連 closure id: `SLCI-004`

- `TC-011` negative: default branch unknown
  - 前提: fallback is requested but default branch cannot be resolved.
  - 操作: run application use case with default branch unknown.
  - 期待結果: `status=blocked`, default branch unknown blocker.
  - 失敗検出: command/use case passes or chooses arbitrary default.
  - 検証方法: application-level pytest.
  - 関連 closure id: `SLCI-004`

### HC-S04: CLI options / diagnostics / local-context

| Field | Contract |
|---|---|
| delegated role | dev-coder |
| input docs | `requirement.md` RQ-006 through RQ-014; `design.md` §3.5, §4, §5; this plan SLCI-005 through SLCI-008 |
| allowed paths | provider `commands/authoring.py`, provider presentation diagnostics files, dogfood mirror equivalents, CLI tests |
| forbidden changes | other authoring leaf commands, backend invoke implementation, ZIP review/stage, adoption or reviewer-pass commands |
| concrete test cases | see the card-style list immediately below this HC-S04 contract |
| acceptance criteria | CLI exposes only preflight options in this Issue, produces deterministic text/JSON diagnostics, and blocks missing local-context provenance |
| required verification | focused CLI pytest covering TC-012 through TC-020 |
| reviewer focus | code-reviewer verifies parser scope and diagnostics; qa-reviewer verifies user-visible blocked/stale/pass clarity |
| stop conditions | option naming conflicts with existing parser conventions; local-context cannot be bounded without additional user-facing input |
| output required | changed files, exact commands run, text/JSON sample behavior summary, unresolved risks, and closure rows for SLCI-005 through SLCI-008 |

#### 具体テストケース一覧

- `TC-012` negative: unresolved ref without fallback
  - 前提: requested ref cannot be resolved and fallback flag is absent.
  - 操作: run CLI with unresolved `--ref`.
  - 期待結果: `status=blocked`, no default fallback, exit 1.
  - 失敗検出: command falls back or exits 0.
  - 検証方法: focused CLI pytest.
  - 関連 closure id: `SLCI-005`

- `TC-013` fallback: requested/effective ref distinction
  - 前提: requested ref cannot be resolved, fallback flag is present, default branch known.
  - 操作: run CLI/use case with fallback allowed.
  - 期待結果: output records distinct `requested_ref` and `effective_ref`.
  - 失敗検出: missing distinction or silent requested-ref rewrite.
  - 検証方法: focused CLI/application pytest.
  - 関連 closure id: `SLCI-005`

- `TC-014` stale: expected hash mismatch through CLI
  - 前提: expected source hash mismatch through CLI option.
  - 操作: run CLI with mismatched `--expected-source-hash`.
  - 期待結果: `status=stale`, source hash mismatch diagnostics.
  - 失敗検出: command passes or omits mismatch fields.
  - 検証方法: focused CLI pytest.
  - 関連 closure id: `SLCI-006`

- `TC-015` no-baseline: CLI source mismatch check marker
  - 前提: no expected source baseline through CLI.
  - 操作: run CLI without expected manifest/hash.
  - 期待結果: `source_hash_mismatch_checked=false` and manifest hash emitted.
  - 失敗検出: command claims checked mismatch or omits manifest hash.
  - 検証方法: focused CLI pytest.
  - 関連 closure id: `SLCI-006`

- `TC-016` provenance: CLI source inventory
  - 前提: default source inventory through CLI.
  - 操作: run CLI over fixture source files.
  - 期待結果: output includes source paths and per-path hashes.
  - 失敗検出: opaque-only hash or wrong inventory.
  - 検証方法: focused CLI pytest.
  - 関連 closure id: `SLCI-006`

- `TC-017` local-context: valid lower-authority evidence
  - 前提: local-context includes `--unsynced-reason` plus context path or diff summary.
  - 操作: run CLI in `local-context` mode.
  - 期待結果: `sync_state=local_context`, `github_sync=not_verified`, adoption disposition required.
  - 失敗検出: output claims GitHub synced or omits lower authority fields.
  - 検証方法: focused CLI pytest.
  - 関連 closure id: `SLCI-007`

- `TC-018` local-context negative: missing unsynced reason
  - 前提: local-context omits `--unsynced-reason`.
  - 操作: run CLI in `local-context` mode.
  - 期待結果: `status=blocked`, missing unsynced reason blocker.
  - 失敗検出: command passes or treats reason as optional.
  - 検証方法: focused CLI pytest.
  - 関連 closure id: `SLCI-007`

- `TC-019` local-context negative: missing context provenance
  - 前提: local-context has reason but no context path and no diff summary.
  - 操作: run CLI in `local-context` mode.
  - 期待結果: `status=blocked`, missing context provenance blocker.
  - 失敗検出: command passes without bounded evidence package.
  - 検証方法: focused CLI pytest.
  - 関連 closure id: `SLCI-007`

- `TC-020` authority: CLI diagnostics avoid forbidden claims
  - 前提: pass/blocked/stale/local-context diagnostics rendered as text and JSON.
  - 操作: run CLI with representative states.
  - 期待結果: no forbidden authority claims in any output.
  - 失敗検出: forbidden claim token appears.
  - 検証方法: focused CLI pytest scanning text and JSON.
  - 関連 closure id: `SLCI-008`

### HC-S05: provider / dogfood mirror parity

| Field | Contract |
|---|---|
| delegated role | dev-coder or parent-orchestrator for mechanical mirror patch |
| input docs | `AGENTS.md` provider-side source-of-truth guidance; `design.md` §3; this plan SLCI-009 |
| allowed paths | provider runtime files changed by S02-S04 and matching `spec-dock/scripts/spec_dock_runtime/` mirror paths |
| forbidden changes | unrelated dogfood data, active issue specs except report evidence, generated runbook authority edits |
| concrete test cases | see the card-style list immediately below this HC-S05 contract |
| acceptance criteria | provider source and dogfood runtime mirror expose matching preflight behavior |
| required verification | mirror parity pytest and focused authoring CLI test using dogfood path |
| reviewer focus | code-reviewer verifies source-of-truth boundary; qa-reviewer verifies installed path behavior |
| stop conditions | provider/mirror intentional divergence is required; installer contract changes become necessary |
| output required | mirror diff summary, parity test output, unresolved risks, and SLCI-009 closure evidence |

#### 具体テストケース一覧

- `TC-021` parity: provider and dogfood runtime mirror
  - 前提: provider runtime files and dogfood mirror files have been updated after S02-S04.
  - 操作: run mirror parity test and focused dogfood-path CLI test.
  - 期待結果: parity test passes and dogfood `./spec-dock/scripts/spec-dock authoring preflight github-sync` exposes implemented behavior.
  - 失敗検出: parity failure, dogfood command still deferred, or provider-only implementation.
  - 検証方法: `uv run pytest tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_mirror_match_provider_assets` plus focused CLI pytest.
  - 関連 closure id: `SLCI-009`

### HC-S90: report / relay evidence

| Field | Contract |
|---|---|
| delegated role | parent-orchestrator |
| input docs | all implemented diffs, test outputs, reviewer outputs, `epic-00295` relay policy |
| allowed paths | `spec-dock/active/issue/report.md` |
| forbidden changes | implementation files except reviewer-finding fixes routed through S99; PR creation |
| concrete test cases | SLCI-010 report inspection for PR defer evidence |
| acceptance criteria | report includes EAL, delegated worker evidence, SLCI closure, test closure, reviewer status, PR defer rationale |
| required verification | `./spec-dock/scripts/spec-dock guidance issue-execution` no longer blocked by report evidence after reviewer pass |
| reviewer focus | spec-reviewer verifies report evidence does not self-claim reviewer pass before actual reviewer output |
| stop conditions | any SLCI row lacks observed evidence; unresolved decision ledger entry remains open |
| output required | updated report with no-per-Issue-PR rationale and final Issue `iss-00307` defer evidence |

#### 具体テストケース一覧

- `TC-S90-001` report: PR delivery defer evidence
  - 前提: implementation and verification evidence are complete for this intermediate Issue.
  - 操作: inspect `report.md` before finish.
  - 期待結果: report records no-per-Issue-PR rationale, final Issue `iss-00307`, and no merge-prepared claim.
  - 失敗検出: report omits defer evidence or claims PR readiness.
  - 検証方法: manual inspection plus `guidance issue-execution`.
  - 関連 closure id: `SLCI-010`

### HC-S99: final local gate

| Field | Contract |
|---|---|
| delegated role | parent-orchestrator with required reviewers |
| input docs | completed report evidence, changed files, test output, reviewer outputs |
| allowed paths | reviewer-finding fixes within S02-S05 allowed paths, report evidence, commit metadata |
| forbidden changes | new feature scope, PR creation, final Epic delivery, next Issue implementation |
| concrete test cases | focused pytest, mirror parity pytest, `./spec-dock/scripts/spec-dock validate`, `git diff --check`, post-commit clean check |
| acceptance criteria | code-reviewer pass, qa-reviewer pass, final spec-reviewer pass, commit created, worktree clean, issue finish succeeds |
| required verification | exact command output summarized in report |
| reviewer focus | code-reviewer for implementation risk, qa-reviewer for user-visible CLI behavior, spec-reviewer for spec/report closure |
| stop conditions | P0/P1 reviewer finding, failing required command, uncommitted unrelated changes, PR delivery requested before final Issue |
| output required | commit hash, post-commit clean evidence, issue finish output, next issue dependency readiness evidence |

#### 具体テストケース一覧

- `FINAL-001` final commands: required verification passes
  - 前提: all SLCI rows closed in report.
  - 操作: run final focused pytest and validation commands.
  - 期待結果: all required commands pass.
  - 失敗検出: any required command fails.
  - 検証方法: command output recorded in report.
  - 関連 closure id: `SLCI-001` through `SLCI-010`

- `FINAL-002` final reviewers: required reviewers pass
  - 前提: implementation diff is complete and report evidence is updated.
  - 操作: run code-reviewer, qa-reviewer, and final spec-reviewer.
  - 期待結果: all reviewers return pass.
  - 失敗検出: any reviewer returns P0/P1/P2 blocking finding.
  - 検証方法: reviewer outputs recorded in report.
  - 関連 closure id: `SLCI-001` through `SLCI-010`

- `FINAL-003` lifecycle: commit and finish without PR delivery
  - 前提: final local gates pass and no PR delivery is attempted.
  - 操作: commit and check worktree clean, then run `issue finish`.
  - 期待結果: commit hash recorded, `git status --short` clean, `issue finish` succeeds.
  - 失敗検出: dirty worktree, no commit, or PR created prematurely.
  - 検証方法: git status and `issue finish` output.
  - 関連 closure id: `SLCI-010`

## 7. 想定コマンド

```bash
uv run pytest tests/cli_runtime/test_authoring.py
uv run pytest tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_mirror_match_provider_assets
./spec-dock/scripts/spec-dock validate
git diff --check
```

If focused tests move to `tests/cli_runtime/test_authoring_preflight.py`, record the exact command in `report.md`.

## 8. reviewer focus

Spec reviewer:

- preflight pass が adoption / reviewer pass / execution-ready を意味しないこと。
- `local-context` が broad force bypass ではなく低 authority evidence mode になっていること。
- source hash mismatch には expected baseline が定義されていること。
- silent fallback がないこと。
- 中間 Issue の PR delivery defer が明示されていること。

Code reviewer:

- git fixture 判定が deterministic であること。
- dirty / staged / untracked / ahead / behind / diverged の判定漏れがないこと。
- source manifest baseline と no-baseline semantics が誤解されないこと。
- command output に forbidden authority claims が混入していないこと。
- provider / dogfood mirror の差分が意図どおりであること。

QA reviewer:

- clean synced / unsafe states / local-context の CLI behavior が利用者視点で区別できること。
- text / JSON diagnostics が machine-readable かつ誤解を招かないこと。
- blocked/stale 時の remediation hint があること。

## 9. 完了条件

- `SLCI-001` から `SLCI-010` が report evidence で閉じている。
- fresh `spec-reviewer` / `code-reviewer` / `qa-reviewer` pass がある。
- 必須検証コマンドが通っている。
- commit が作成され、post-commit `git status --short` が clean。
- `issue finish` が成功している。
- 次 Issue の `deps check` と `issue start` に進める状態である。

## 10. PR delivery policy

この Issue は中間 Issue のため PR を作成しない。PR delivery、CI / PR review repair、mergeable PR 作成は final quality gate Issue `iss-00307` で実施する。
