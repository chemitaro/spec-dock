---
種別: 実装計画書（Issue）
ID: "iss-00147"
タイトル: "SpecDock uninstall command"
関連GitHub: ["#147"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-05-31"
依存: ["requirement.md", "design.md"]
親: ["epic-00054", "init-local-00002"]
---

# iss-00147 SpecDock uninstall command — 実装計画（実行契約 / Execution Contract）

## この計画で満たす要件ID
- AC:
  - AC-001, AC-002, AC-003, AC-004, AC-005, AC-006, AC-007, AC-008, AC-009, AC-010
- EC:
  - EC-001, EC-002, EC-003, EC-004, EC-005, EC-006, EC-007, EC-008
- 制約:
  - destructive operation は explicit `--apply` と specs mode を要求する
  - package/environment uninstall と GitHub remote mutation は対象外
  - unknown unmanaged paths / repo root / `.git` / target parent は削除しない
  - agent / skill noise removal を primary objective としつつ、product-reused/user-owned mismatch は preserve する

## 依存関係から導く実装順序
- 依存関係の正本:
  - `design.md` の `依存関係分析`、`Module Dependency Diagram`、`Directory / File 変更計画`
- 順序ルール:
  - Installer CLI public contract を先に固定し、inventory classification、apply、runtime wrapper、docs impact、final gate の順に進む。
  - runtime wrapper は installer command が stable になってから追加し、runtime 側に uninstall logic を重複実装しない。
- step 依存サマリー:
  - S01:
    - 依存: approved requirement/design
    - unblock: S02/S03/S04
    - 対象ファイル: `src/spec_dock/cli.py`, `tests/test_init_update.py`
  - S02:
    - 依存: S01 command surface
    - unblock: S03 apply engine
    - 対象ファイル: `src/spec_dock/cli.py`, `tests/test_init_update.py`
  - S03:
    - 依存: S02 inventory/action plan
    - unblock: S04 runtime wrapper, S90 docs
    - 対象ファイル: `src/spec_dock/cli.py`, `tests/test_init_update.py`
  - S04:
    - 依存: S01 command contract, S03 installer behavior
    - unblock: S90/S99
    - 対象ファイル: `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/uninstall.py`, `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/parser.py`, `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/registry.py`, `tests/cli_runtime/test_uninstall.py`
  - S90:
    - 依存: S01-S04 final command contract
    - unblock: S99
    - 対象ファイル: `src/spec_dock/assets/spec_dock/docs/reference_github.md`, `src/spec_dock/assets/spec_dock/docs/reference_sync.md` if needed
  - S99:
    - 依存: S01-S04 and S90 closed
    - unblock: PR delivery / issue readiness
    - 対象ファイル: `report.md` evidence only unless blockers require fixes

## ステップ一覧
- S01:
  - 観測可能な振る舞い: installer CLI `spec-dock uninstall` が dry-run default、usage guardrail、JSON output contract を持つ
  - 依存: approved requirement/design
  - unblock: S02, S03, S04
  - 対象ファイル: `src/spec_dock/cli.py`, `tests/test_init_update.py`
  - 閉じる要件: AC-001, AC-002, AC-010, EC-001, EC-002, EC-008
  - レビューゲート: code-reviewer
- S02:
  - 観測可能な振る舞い: dry-run が inventory/category/content-policy に基づく plan を表示する
  - 依存: S01
  - unblock: S03
  - 対象ファイル: `src/spec_dock/cli.py`, `tests/test_init_update.py`
  - 閉じる要件: AC-005, AC-006, AC-007, EC-006, EC-007
  - レビューゲート: code-reviewer
- S03:
  - 観測可能な振る舞い: `--apply --keep-specs` / `--apply --remove-specs` が plan に従って削除・保持・失敗報告・bounded cleanup を行う
  - 依存: S02
  - unblock: S04, S90
  - 対象ファイル: `src/spec_dock/cli.py`, `tests/test_init_update.py`
  - 閉じる要件: AC-003, AC-004, AC-009, AC-010, EC-003, EC-004, EC-005, EC-008
  - レビューゲート: code-reviewer
- S04:
  - 観測可能な振る舞い: repo-local runtime uninstall wrapper が installer CLI を `uvx --no-cache` で呼ぶ
  - 依存: S01, S03
  - unblock: S90, S99
  - 対象ファイル: `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/uninstall.py`, `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/parser.py`, `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/registry.py`, `tests/cli_runtime/test_uninstall.py`
  - 閉じる要件: AC-008, AC-010
  - レビューゲート: code-reviewer
- S90:
  - 観測可能な振る舞い: docs/help が uninstall の non-GitHub / non-package uninstall boundary と generated state cleanup を説明または no-op 判定する
  - 依存: S01-S04
  - unblock: S99
  - 対象ファイル: `src/spec_dock/assets/spec_dock/docs/reference_github.md`, `src/spec_dock/assets/spec_dock/docs/reference_sync.md`
  - 閉じる要件: docs contract, E-AC-006
  - レビューゲート: spec-reviewer docs/spec alignment
- S99:
  - 観測可能な振る舞い: issue-wide verification and final QA/code/spec gates pass
  - 依存: all previous steps
  - unblock: PR delivery / issue ready
  - 対象ファイル: `report.md` evidence
  - 閉じる要件: whole issue
  - レビューゲート: qa-reviewer, issue-wide code-reviewer, final spec-reviewer

## 要件 ↔ ステップ対応
- AC-001 -> S01
- AC-002 -> S01
- AC-003 -> S03
- AC-004 -> S03
- AC-005 -> S02
- AC-006 -> S02
- AC-007 -> S02
- AC-008 -> S04
- AC-009 -> S03
- AC-010 -> S01 / S03 / S04
- EC-001 -> S01
- EC-002 -> S01
- EC-003 -> S03
- EC-004 -> S03
- EC-005 -> S03 / S04
- EC-006 -> S02
- EC-007 -> S02
- EC-008 -> S01 / S03
- docs contract -> S90
- final workflow gates -> S99

## 仕様固定クロージャ索引（Spec-Locked Closure Index）

| 識別子（ID） | ステップ（step） | スライス（slice） | 種別（type） | 仕様リンク | 固定する期待値 | 観測可能な入力 / 状態 | 防ぐ bug class | 必須 | 証跡レベル（evidence level） | クロージャ証跡（closure evidence） |
|---|---|---|---|---|---|---|---|---|---|---|
| tc-001 | S01 | installer dry-run surface | acceptance | AC-001, EC-002 | `spec-dock uninstall <target>` は plan を表示し filesystem を変更しない | initialized temp repo, uninstall dry-run | accidental destructive default | yes | red-required | tests + report closure |
| tc-002 | S01 | apply preflight | negative | AC-002 | `--apply` without specs mode exits before mutation | initialized temp repo, apply without mode | implicit specs deletion | yes | red-required | tests + report closure |
| tc-003 | S01 | flag exclusivity | negative | design flag contract | `--keep-specs` and `--remove-specs` are mutually exclusive | CLI args with both flags | ambiguous destructive mode | yes | red-required | tests + report closure |
| tc-020 | S01 | target validation | negative | EC-001 | target without managed `spec-dock/` state fails before mutation with guidance | temp dir or repo lacking managed SpecDock state | running destructive workflow against unmanaged target | yes | red-required | tests + report closure |
| tc-023 | S01 | JSON dry-run output | acceptance | AC-010, EC-008 | `--json` dry-run emits one parseable JSON object with summary/actions/guidance and action-level status/category/reason for planned removal and preservation | initialized temp repo, uninstall dry-run with `--json` | agent cannot parse uninstall plan semantics | yes | red-required | tests + report closure |
| tc-004 | S02 | agent/skill classification | acceptance | AC-003, AC-007 | known managed agent/skill mismatch is planned for removal | modified known agent/skill file | leaving product-noise assets | yes | red-required | tests + report closure |
| tc-005 | S02 | unmanaged preservation | negative | AC-007 | unknown user-created files under managed-looking roots are preserved | unknown `.agents` / `.codex` / `.github` file | deleting user-created assets | yes | red-required | tests + report closure |
| tc-006 | S02 | bootstrap/product-reusable exact match | acceptance | AC-005 | exact-match bootstrap/product-reusable assets are planned for removal | matching `.codex/config.toml` / docs-managed file | stale managed residue | yes | red-required | tests + report closure |
| tc-007 | S02 | bootstrap/product-reusable mismatch | negative | AC-006, EC-006 | mismatch assets are preserved for manual review | edited product-reusable file | user edit loss | yes | red-required | tests + report closure |
| tc-021 | S02 | comparison-error preservation | negative | EC-006 | non-core comparison errors preserve with manual-review reason | symlink/type mismatch or read failure in product-reusable asset | deleting user-owned content when ownership cannot be proven | yes | red-required | tests + report closure |
| tc-008 | S02 | scaffold-managed policy | acceptance/negative | design mapping | scaffold-managed exact match removes; mismatch preserves | `spec-dock/docs/**` or scripts fixture | broken scaffold cleanup contract | yes | red-required | tests + report closure |
| tc-009 | S02 | repo-root shortcut | negative | EC-007 | matching `spec` symlink removes; nonmatching file/symlink preserves | repo-root `spec` variants | deleting unrelated shortcut | yes | red-required | tests + report closure |
| tc-010 | S03 | keep-specs apply | acceptance | AC-003 | apply removes tooling but preserves `spec-dock/initiatives/**` | apply with `--keep-specs` | losing restartable specs | yes | red-required | tests + report closure |
| tc-011 | S03 | remove-specs apply | acceptance | AC-004 | apply includes spec history and reports destructive choice | apply with `--remove-specs` | hidden specs deletion | yes | red-required | tests + report closure |
| tc-012 | S03 | bounded cleanup | negative | EC-003, EC-004 | empty dirs removed only inside boundary roots and not through preserved content | preserved file inside boundary root | over-broad directory deletion | yes | red-required | tests + report closure |
| tc-013 | S03 | idempotent rerun | acceptance | AC-009 | prior removals report already_removed/no-op without destructive failure | run uninstall twice | non-idempotent cleanup | yes | red-required | tests + report closure |
| tc-014 | S03 | partial failure | negative | requirement failure behavior | unlink/rmtree failure returns non-zero and reports failed separately | injected unlink failure | silent partial deletion | yes | red-required | tests + report closure |
| tc-022 | S03 | installer direct recovery guidance | acceptance | AC-008, EC-005 | apply output gives installer-direct retry/reinstall guidance after repo-local runtime removal | apply removes repo-local runtime wrapper | operator cannot recover after self-removal | yes | red-required | tests + report closure |
| tc-024 | S03 | JSON apply result | acceptance/negative | AC-010, EC-008 | `--json` apply emits parseable completed/partial_failure payload with action-level removed/already_removed/preserved/failed/empty_dir_removed statuses and no human-readable stdout mixing | apply success, rerun, preserved item, cleanup, and injected failure with `--json` | agent cannot parse destructive operation result semantics | yes | red-required | tests + report closure |
| tc-015 | S04 | runtime wrapper invocation | acceptance | AC-008 | wrapper calls `uvx --no-cache --from ... spec-dock uninstall TARGET` | runtime command with stubbed uvx | duplicated runtime implementation | yes | red-required | tests + report closure |
| tc-016 | S04 | runtime flag/output propagation | acceptance | AC-008 | wrapper forwards supported flags and propagates stdout/stderr/exit code | stubbed uvx output/failure | lost installer evidence | yes | red-required | tests + report closure |
| tc-017 | S04 | missing uvx | negative | design runtime command | missing `uvx` exits 127 with guidance | PATH without uvx | opaque tool failure | yes | red-required | tests + report closure |
| tc-025 | S04 | runtime JSON forwarding | acceptance | AC-010 | runtime wrapper forwards `--json` and preserves installer JSON stdout | runtime command with stubbed uvx and JSON stdout | repo-local agent execution loses machine-readable output | yes | red-required | tests + report closure |
| tc-018 | S90 | docs boundary | docs | E-AC-006 docs contract | docs/help state no GitHub mutation and no package/environment uninstall | docs diff / help output | misleading operator docs | yes | inspect-only | docs review + report closure |
| tc-019 | S99 | final quality gate | workflow | workflow_issue.md | focused/full tests, validate/sync, final QA/code/spec gates pass or block | whole issue diff and commands | incomplete handoff | yes | manual-required | final report evidence |

## レビュー / QA ゲート方針
- Per-step:
  - S01-S04: step-local `code-reviewer` pass before step commit.
  - S90: `spec-reviewer` docs/spec alignment; if test/help assertion code changes are included, also use `code-reviewer`.
  - S99: final `qa-reviewer`, issue-wide `code-reviewer`, final `spec-reviewer`.
- Gating rule:
  - Missing, stale, fail, unavailable, denied, waived, or provisional reviewer result is not pass.
  - Any required closure row changed or removed requires plan amendment and re-review.

## 実装ステップ

### 実装ステップ S01 — Installer uninstall command surface and dry-run contract
- 振る舞いの目標（behavior goal）:
  - `spec-dock uninstall [path]` exists, defaults to dry-run, renders stable plan/result buckets, supports JSON plan output, and never mutates without `--apply`.
- design 参照:
  - `Interface contract`, `Uninstall Model`, `Directory / File 変更計画`
- 依存:
  - approved requirement/design
- unblock:
  - S02 inventory/classification, S03 apply, S04 wrapper
- 対象ファイル:
  - `src/spec_dock/cli.py`
  - `tests/test_init_update.py`
- 計画済み契約（planned contract）:
  - scope:
    - Add installer parser for `uninstall [path] [--apply] [--keep-specs | --remove-specs] [--json]`.
    - Add dry-run renderer with status buckets and JSON output.
    - Add pre-mutation validation for target repo and specs mode.
  - テスト義務（test obligation）:
    - closure id: tc-001, tc-002, tc-003, tc-020, tc-023
    - coverage rationale: destructive default, explicit specs mode, CLI contract, invalid target fail-fast, agent-readable plan output.
  - Red / 代替証跡の要件:
    - red-required:
      - tests in `tests/test_init_update.py` fail before implementation for dry-run no-mutation, apply missing mode, mutually exclusive flags, invalid target fail-fast, and JSON dry-run output.
  - 実装範囲（implementation scope）:
    - allowed paths:
      - `src/spec_dock/cli.py`
      - `tests/test_init_update.py`
    - forbidden changes:
      - runtime wrapper, docs, broad module extraction, actual deletion logic beyond no-op skeleton.
  - Green 検証:
    - `python -m unittest tests.test_init_update -v`
  - Refactor / cleanup ガードレール:
    - Keep helpers local and focused; no unrelated installer refactor.
  - closure 証跡要件:
    - Step Contract Closure, Test Contract Closure, Closure Coverage, Reviewer Gate Status, Step Commit Gate in `report.md`.
  - amendment trigger:
    - Need to remove `--json` or change the JSON top-level contract.

#### 委任契約（delegation contract）
- 委任ロール（delegated role）:
  - dev-coder
- 入力 docs:
  - `requirement.md`, `design.md`, `plan.md`, `workflow_issue.md`, `tests/test_init_update.py`, `src/spec_dock/cli.py`
- 許可 paths:
  - `src/spec_dock/cli.py`
  - `tests/test_init_update.py`
- 禁止 changes:
  - runtime command files, docs, package metadata, GitHub state, broad restructuring.
- 受け入れ条件:
  - tc-001, tc-002, tc-003, tc-020, tc-023 close.
- 必須 tests または docs-only verification:
  - `python -m unittest tests.test_init_update -v`
- reviewer focus:
  - code-reviewer: CLI parser behavior, no-mutation default, usage exits, minimal scope.
- 必須出力（output required）:
  - changed files, test result, report ledger notes, unresolved risks.
- 停止条件（stop conditions）:
  - CLI contract conflict with design, need for new module extraction, inability to assert no mutation.

#### 具体テストケース一覧
- `tc-s01-001` acceptance: dry-run prints plan and mutates no files
  - 前提: temp repo initialized with SpecDock assets and representative files.
  - 操作: call `main(["uninstall", target])`.
  - 期待結果: exit `0`, output contains dry-run/plan buckets, pre/post filesystem snapshot is unchanged.
  - 失敗検出: uninstall accidentally deletes files by default.
  - 検証方法: `tests/test_init_update.py`.
  - 関連 closure id: tc-001
- `tc-s01-002` negative: apply without specs mode fails before mutation
  - 前提: temp repo initialized with specs and agent assets.
  - 操作: call `main(["uninstall", target, "--apply"])`.
  - 期待結果: exit `2`, error asks for `--keep-specs` or `--remove-specs`, files remain.
  - 失敗検出: specs mode is implicit or mutation happens before validation.
  - 検証方法: `tests/test_init_update.py`.
  - 関連 closure id: tc-002
- `tc-s01-003` negative: keep/remove specs flags are mutually exclusive
  - 前提: temp repo initialized.
  - 操作: call uninstall with `--apply --keep-specs --remove-specs`.
  - 期待結果: usage error before mutation.
  - 失敗検出: ambiguous destructive mode is accepted.
  - 検証方法: `tests/test_init_update.py`.
  - 関連 closure id: tc-003
- `tc-s01-004` negative: unmanaged target fails before mutation
  - 前提: temp directory or Git repo lacks managed `spec-dock/` state.
  - 操作: call `main(["uninstall", target])` and `main(["uninstall", target, "--apply", "--keep-specs"])`.
  - 期待結果: exit `2`, output explains the target is not a managed SpecDock repo, and filesystem snapshot is unchanged.
  - 失敗検出: invalid target proceeds to dry-run/apply or mutates non-managed repo content.
  - 検証方法: `tests/test_init_update.py`.
  - 関連 closure id: tc-020
- `tc-s01-005` acceptance: dry-run json output is parseable and machine-readable
  - 前提: temp repo initialized with representative remove/preserve candidates.
  - 操作: call `main(["uninstall", target, "--json"])`.
  - 期待結果: stdout is one parseable JSON object containing `schema_version`, `target`, `mode`, `apply`, `status`, `summary`, `actions`, `guidance`, and `errors`; `actions[]` entries expose `path`, `category`, `status`, and `reason` for `would_remove` and `preserved` examples; no human-readable lines are mixed into stdout.
  - 失敗検出: agent execution cannot reliably parse dry-run plan semantics.
  - 検証方法: `tests/test_init_update.py`.
  - 関連 closure id: tc-023

#### ステップ完了契約（step closure contract）
- closure id:
  - tc-001, tc-002, tc-003, tc-020, tc-023
- close 条件:
  - tests are red before implementation, green after, code-reviewer pass, report updated.
- 検証 evidence:
  - `python -m unittest tests.test_init_update -v`
- report evidence:
  - Step Contract Closure, Test Contract Closure, Closure Coverage, Reviewer Gate Status, Step Commit Gate.
- 残リスク:
  - inventory/apply behavior remains planned for S02/S03.

#### ステップゲート（step gate）
- step reviewer gate:
  - reviewer: code-reviewer
  - review 範囲: installer CLI surface and tests
  - pass 条件: review_status: pass
  - re-review rule: fix findings and rerun fresh reviewer
- commit / no-op gate:
  - closure 状態: committed unless all S01 behavior already exists and is approved-no-op.
  - commit 範囲: S01 files only
  - no-op 条件: only allowed when tests and code-reviewer prove tc-001/tc-002/tc-003/tc-020/tc-023 already pass without source changes.
  - report update: record Red/Green/Refactor, Step/Test Contract Closure, Reviewer Gate Status, and Step Commit Gate before commit or approved-no-op handoff.

### 実装ステップ S02 — Inventory, category classification, and content policy
- 振る舞いの目標（behavior goal）:
  - dry-run produces correct remove/preserve/manual-review decisions from shipped assets and target repo state.
- design 参照:
  - `Uninstall Model`, `要件 → 設計マッピング`, `テスト戦略`
- 依存:
  - S01
- unblock:
  - S03
- 対象ファイル:
  - `src/spec_dock/cli.py`
  - `tests/test_init_update.py`
- 計画済み契約（planned contract）:
  - scope:
    - Build inventory from install_root current files, bootstrap-only, obsolete exact paths, scaffold-managed files, generated state, specs, repo-root shortcut, unknown boundary-root files.
    - Apply category/content policies in dry-run only.
  - テスト義務:
    - closure id: tc-004, tc-005, tc-006, tc-007, tc-008, tc-009, tc-021
    - coverage rationale: over-delete/under-delete prevention for every high-risk category.
  - Red / 代替証跡の要件:
    - red-required for each listed category/policy.
  - 実装範囲:
    - allowed paths:
      - `src/spec_dock/cli.py`
      - `tests/test_init_update.py`
    - forbidden changes:
      - actual file removal, runtime wrapper, docs.
  - Green 検証:
    - `python -m unittest tests.test_init_update -v`
  - Refactor / cleanup ガードレール:
    - Keep classification deterministic and derived from approved design categories.
  - closure 証跡要件:
    - report ledgers for all closure ids.
  - amendment trigger:
    - New deletion candidate source outside approved inventory.

#### 委任契約（delegation contract）
- 委任ロール:
  - dev-coder
- 入力 docs:
  - `requirement.md`, `design.md`, `plan.md`, `src/spec_dock/cli.py`, `src/spec_dock/assets/install_root/.agents/host-adapters/meta.json`
- 許可 paths:
  - `src/spec_dock/cli.py`
  - `tests/test_init_update.py`
- 禁止 changes:
  - file deletion apply logic, runtime wrapper, docs.
- 受け入れ条件:
  - tc-004 through tc-009 and tc-021 close.
- 必須 tests:
  - `python -m unittest tests.test_init_update -v`
- reviewer focus:
  - code-reviewer: ownership classification, unknown-file preservation, comparison failure safety.
- 必須出力:
  - changed files, test result, report notes, any classification ambiguity.
- 停止条件:
  - Need to delete unknown files, need to alter requirement categories, comparison impossible to test hermetically.

#### 具体テストケース一覧
- `tc-s02-001` acceptance: known managed agent/skill mismatch planned for removal
  - 前提: temp repo has edited known `.agents/skills/...` or `.codex/agents/...` file.
  - 操作: dry-run uninstall.
  - 期待結果: path is listed as would_remove, not preserved.
  - 失敗検出: edited agent/skill remains as product noise.
  - 検証方法: `tests/test_init_update.py`.
  - 関連 closure id: tc-004
- `tc-s02-002` negative: unknown files under managed roots are preserved
  - 前提: temp repo has user-created `.agents/skills/custom/SKILL.md` or similar unknown file.
  - 操作: dry-run uninstall.
  - 期待結果: unknown file is preserved with unmanaged reason.
  - 失敗検出: broad prefix deletion owns user files.
  - 検証方法: `tests/test_init_update.py`.
  - 関連 closure id: tc-005
- `tc-s02-003` acceptance: exact-match bootstrap/product-reusable assets planned for removal
  - 前提: `.codex/config.toml` and representative product-reusable file equal shipped asset.
  - 操作: dry-run uninstall.
  - 期待結果: files are would_remove.
  - 失敗検出: shipped residue is left behind unnecessarily.
  - 検証方法: `tests/test_init_update.py`.
  - 関連 closure id: tc-006
- `tc-s02-004` negative: mismatch bootstrap/product-reusable assets preserved
  - 前提: `.codex/config.toml` or `.github/workflows/ci.yml` has user edit.
  - 操作: dry-run uninstall.
  - 期待結果: file is preserved with content mismatch/manual review reason.
  - 失敗検出: user/product config is deleted.
  - 検証方法: `tests/test_init_update.py`.
  - 関連 closure id: tc-007
- `tc-s02-007` negative: comparison errors preserve non-core assets
  - 前提: representative product-reusable path is a file type mismatch, symlink mismatch, or read-failure fixture instead of a comparable regular file.
  - 操作: dry-run uninstall.
  - 期待結果: path is preserved/manual-review with comparison-error reason unless it belongs to the core agent/skill category.
  - 失敗検出: comparison failure is treated as ownership proof and deletes user-owned content.
  - 検証方法: `tests/test_init_update.py` using symlink/type fixture or hermetic read-failure monkeypatch.
  - 関連 closure id: tc-021
- `tc-s02-005` acceptance/negative: scaffold-managed exact match removes, mismatch preserves
  - 前提: representative `spec-dock/docs/**` or `spec-dock/scripts/**` file has exact-match and mismatch variants.
  - 操作: dry-run uninstall.
  - 期待結果: exact-match is would_remove; mismatch is preserved/manual review.
  - 失敗検出: scaffold cleanup contract is untested.
  - 検証方法: `tests/test_init_update.py`.
  - 関連 closure id: tc-008
- `tc-s02-006` negative: repo-root spec shortcut target is verified
  - 前提: repo-root `spec` is matching symlink, nonmatching symlink, regular file, or directory across fixtures.
  - 操作: dry-run uninstall.
  - 期待結果: only matching SpecDock shortcut is would_remove; others are preserved.
  - 失敗検出: unrelated shortcut/file is deleted.
  - 検証方法: `tests/test_init_update.py`, with symlink availability guard if needed.
  - 関連 closure id: tc-009

#### ステップ完了契約
- closure id:
  - tc-004, tc-005, tc-006, tc-007, tc-008, tc-009, tc-021
- close 条件:
  - all classification tests pass; code-reviewer pass; report updated.
- 検証 evidence:
  - `python -m unittest tests.test_init_update -v`
- report evidence:
  - Step/Test Contract Closure and Closure Coverage.
- 残リスク:
  - apply semantics deferred to S03.

#### ステップゲート
- step reviewer gate:
  - reviewer: code-reviewer
  - review 範囲: inventory/classification/content policy
  - pass 条件: review_status: pass
- commit / no-op gate:
  - closure 状態: committed unless all S02 behavior already exists and is approved-no-op.
  - commit 範囲: S02 files only
  - no-op 条件: only allowed when tests and code-reviewer prove all S02 closure ids already pass without source changes.
  - report update: record Red/Green/Refactor, Step/Test Contract Closure, Reviewer Gate Status, and Step Commit Gate before commit or approved-no-op handoff.

### 実装ステップ S03 — Apply engine, idempotency, partial failure, and bounded cleanup
- 振る舞いの目標:
  - apply executes planned actions safely, reports results, supports rerun, and cleans empty directories within boundaries.
- design 参照:
  - `Sequence Delta`, `リスク / 移行 / ロールバック`
- 依存:
  - S02
- unblock:
  - S04, S90
- 対象ファイル:
  - `src/spec_dock/cli.py`
  - `tests/test_init_update.py`
- 計画済み契約:
  - scope:
    - Apply only actions produced by S02.
    - Implement `--keep-specs`, `--remove-specs`, generated state removal, bounded cleanup, idempotent rerun, partial failure summary, JSON apply result.
  - テスト義務:
    - closure id: tc-010, tc-011, tc-012, tc-013, tc-014, tc-022, tc-024
  - Red / 代替証跡:
    - red-required for apply modes, cleanup boundary, rerun, failure injection, JSON apply success/failure.
  - 実装範囲:
    - allowed paths: `src/spec_dock/cli.py`, `tests/test_init_update.py`
    - forbidden changes: runtime wrapper, docs, deletion outside target fixture.
  - Green 検証:
    - `python -m unittest tests.test_init_update -v`
  - amendment trigger:
    - Need for automatic rollback or out-of-target deletion.

#### 委任契約（delegation contract）
- 委任ロール:
  - dev-coder
- 入力 docs:
  - `requirement.md`, `design.md`, `plan.md`, S01/S02 implementation
- 許可 paths:
  - `src/spec_dock/cli.py`
  - `tests/test_init_update.py`
- 禁止 changes:
  - runtime wrapper, docs, package/environment deletion, GitHub mutation.
- 受け入れ条件:
  - tc-010 through tc-014, tc-022, and tc-024 close.
- 必須 tests:
  - `python -m unittest tests.test_init_update -v`
- reviewer focus:
  - code-reviewer: filesystem safety, cleanup traversal, failure/idempotency.
- 必須出力:
  - changed files, test results, failure simulation method, report notes.
- 停止条件:
  - Need to touch repo root/parent, inability to simulate failure hermetically, conflict with content policy.

#### 具体テストケース一覧
- `tc-s03-001` acceptance: keep-specs preserves spec history
  - 前提: temp repo has specs and managed tooling.
  - 操作: apply uninstall with `--keep-specs`.
  - 期待結果: tooling is removed; `spec-dock/initiatives/**` remains.
  - 失敗検出: development restart history is lost.
  - 検証方法: `tests/test_init_update.py`.
  - 関連 closure id: tc-010
- `tc-s03-002` acceptance: remove-specs removes spec history with explicit summary
  - 前提: temp repo has specs and managed tooling.
  - 操作: apply uninstall with `--remove-specs`.
  - 期待結果: specs are removed and result explicitly reports spec history removal.
  - 失敗検出: hidden or unreported destructive spec deletion.
  - 検証方法: `tests/test_init_update.py`.
  - 関連 closure id: tc-011
- `tc-s03-003` negative: bounded cleanup respects preserved files and root boundaries
  - 前提: boundary root contains removed files plus preserved file.
  - 操作: apply uninstall.
  - 期待結果: empty subdirs are removed, directories containing preserved files remain, repo root/`.git`/parent untouched.
  - 失敗検出: over-broad directory cleanup.
  - 検証方法: `tests/test_init_update.py`.
  - 関連 closure id: tc-012
- `tc-s03-004` acceptance: rerun is idempotent
  - 前提: uninstall has already removed managed files.
  - 操作: run same apply command again.
  - 期待結果: command reports already_removed/no-op and exits successfully when no failures remain.
  - 失敗検出: second run crashes or treats missing managed file as destructive error.
  - 検証方法: `tests/test_init_update.py`.
  - 関連 closure id: tc-013
- `tc-s03-005` negative: partial failure reports failed separately
  - 前提: unlink/rmtree is made to fail for a controlled target.
  - 操作: apply uninstall.
  - 期待結果: exit non-zero, failed path is reported separately from removed/preserved.
  - 失敗検出: partial deletion is hidden as success.
  - 検証方法: hermetic monkeypatch/mock in `tests/test_init_update.py`.
  - 関連 closure id: tc-014
- `tc-s03-006` acceptance: apply output provides installer-direct recovery guidance
  - 前提: apply uninstall removes repo-local runtime wrapper or `spec-dock/scripts/**` from a temp repo.
  - 操作: apply uninstall with an explicit specs mode.
  - 期待結果: result summary includes guidance to rerun/reinstall through installer CLI, not only through the repo-local runtime command that may have been removed.
  - 失敗検出: operator loses recovery path after self-removal.
  - 検証方法: `tests/test_init_update.py`.
  - 関連 closure id: tc-022
- `tc-s03-007` acceptance/negative: apply json output covers success and partial failure
  - 前提: temp repo has apply success fixture, preserved/manual-review item, bounded cleanup candidate, rerun fixture, and a separate injected unlink/rmtree failure fixture.
  - 操作: apply uninstall with `--json` and an explicit specs mode; then rerun with `--json`; run failure fixture with `--json`.
  - 期待結果: success returns JSON with `status: "completed"` and action-level `removed`, `preserved`, and `empty_dir_removed` examples; rerun returns `already_removed`; failure returns non-zero with parseable JSON containing `status: "partial_failure"`, `failed` action details, summary counts, and guidance. Each apply-side `actions[]` example includes `path`, `category`, `status`, `reason`, and `error`.
  - 失敗検出: agent execution cannot reliably parse destructive operation result semantics or failures.
  - 検証方法: `tests/test_init_update.py`.
  - 関連 closure id: tc-024

#### ステップ完了契約
- closure id:
  - tc-010, tc-011, tc-012, tc-013, tc-014, tc-022, tc-024
- close 条件:
  - apply behavior tests pass, code-reviewer pass, report updated.
- 検証 evidence:
  - `python -m unittest tests.test_init_update -v`
- report evidence:
  - Step/Test Contract Closure and Closure Coverage.
- 残リスク:
  - runtime wrapper still pending until S04.

#### ステップゲート
- step reviewer gate:
  - reviewer: code-reviewer
  - review 範囲: apply engine, cleanup, failure/idempotency
  - pass 条件: review_status: pass
- commit / no-op gate:
  - closure 状態: committed unless all S03 behavior already exists and is approved-no-op.
  - commit 範囲: S03 files only
  - no-op 条件: only allowed when tests and code-reviewer prove all S03 closure ids already pass without source changes.
  - report update: record Red/Green/Refactor, Step/Test Contract Closure, Reviewer Gate Status, and Step Commit Gate before commit or approved-no-op handoff.

### 実装ステップ S04 — Repo-local runtime uninstall wrapper
- 振る舞いの目標:
  - repo-local `uninstall` command delegates to installer CLI via `uvx --no-cache`.
- design 参照:
  - `Interface contract`, `Module Dependency Diagram`
- 依存:
  - S01, S03
- unblock:
  - S90, S99
- 対象ファイル:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/uninstall.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/parser.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/registry.py`
  - `tests/cli_runtime/test_uninstall.py`
- 計画済み契約:
  - scope:
    - Mirror update wrapper structure.
    - Forward target and supported flags, including `--json`.
    - Propagate stdout/stderr/exit code and handle missing `uvx`.
  - テスト義務:
    - closure id: tc-015, tc-016, tc-017, tc-025
  - Red / 代替証跡:
    - red-required with stubbed `uvx`.
  - 実装範囲:
    - allowed paths listed above.
    - forbidden changes: installer removal logic in runtime, arbitrary source/cache overrides.
  - Green 検証:
    - `python -m unittest tests.cli_runtime.test_uninstall -v`
  - amendment trigger:
    - Need to add arbitrary upstream/package source options.

#### 委任契約（delegation contract）
- 委任ロール:
  - dev-coder
- 入力 docs:
  - `requirement.md`, `design.md`, `plan.md`, `commands/update.py`, runtime parser/registry files
- 許可 paths:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/uninstall.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/parser.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/registry.py`
  - `tests/cli_runtime/test_uninstall.py`
- 禁止 changes:
  - installer code, docs, package metadata, arbitrary uvx override options.
- 受け入れ条件:
  - tc-015, tc-016, tc-017, tc-025 close.
- 必須 tests:
  - `python -m unittest tests.cli_runtime.test_uninstall -v`
- reviewer focus:
  - code-reviewer: wrapper parity with update, argument forwarding, missing uvx handling.
- 必須出力:
  - changed files, test result, report notes.
- 停止条件:
  - Runtime needs to reimplement installer logic or accepted flags diverge from installer CLI.

#### 具体テストケース一覧
- `tc-s04-001` acceptance: wrapper invokes uvx no-cache installer uninstall
  - 前提: runtime command test harness with stubbed `uvx`.
  - 操作: run repo-local `uninstall` with default target.
  - 期待結果: command args contain `uvx --no-cache --from git+https://github.com/chemitaro/spec-dock spec-dock uninstall <resolved-target>`.
  - 失敗検出: wrapper bypasses installer or omits no-cache upstream source.
  - 検証方法: `tests/cli_runtime/test_uninstall.py`.
  - 関連 closure id: tc-015
- `tc-s04-002` acceptance: wrapper forwards flags and propagates output/exit code
  - 前提: stubbed `uvx` emits stdout/stderr and exits non-zero.
  - 操作: run `uninstall --apply --keep-specs`.
  - 期待結果: flags are forwarded; stdout/stderr/exit code are propagated.
  - 失敗検出: installer evidence is lost or flags are dropped.
  - 検証方法: `tests/cli_runtime/test_uninstall.py`.
  - 関連 closure id: tc-016
- `tc-s04-004` acceptance: wrapper forwards json and preserves json stdout
  - 前提: stubbed `uvx` records args and emits JSON stdout.
  - 操作: run `uninstall --json --apply --keep-specs`.
  - 期待結果: `--json` is forwarded to installer CLI; stdout JSON is propagated unchanged.
  - 失敗検出: repo-local command drops machine-readable output for agent execution.
  - 検証方法: `tests/cli_runtime/test_uninstall.py`.
  - 関連 closure id: tc-025
- `tc-s04-003` negative: missing uvx exits with guidance
  - 前提: PATH lacks `uvx`.
  - 操作: run runtime uninstall.
  - 期待結果: exit `127` and actionable install/PATH guidance.
  - 失敗検出: opaque FileNotFoundError or wrong exit status.
  - 検証方法: `tests/cli_runtime/test_uninstall.py`.
  - 関連 closure id: tc-017

#### ステップ完了契約
- closure id:
  - tc-015, tc-016, tc-017, tc-025
- close 条件:
  - runtime tests pass, code-reviewer pass, report updated.
- 検証 evidence:
  - `python -m unittest tests.cli_runtime.test_uninstall -v`
- report evidence:
  - Step/Test Contract Closure and Closure Coverage.
- 残リスク:
  - docs impact remains for S90.

#### ステップゲート
- step reviewer gate:
  - reviewer: code-reviewer
  - review 範囲: runtime wrapper and tests
  - pass 条件: review_status: pass
- commit / no-op gate:
  - closure 状態: committed unless all S04 behavior already exists and is approved-no-op.
  - commit 範囲: S04 files only
  - no-op 条件: only allowed when tests and code-reviewer prove tc-015/tc-016/tc-017/tc-025 already pass without source changes.
  - report update: record Red/Green/Refactor, Step/Test Contract Closure, Reviewer Gate Status, and Step Commit Gate before commit or approved-no-op handoff.

### ドキュメント影響の解消ステップ S90 — docs impact resolution / docs refresh
- 対象:
  - `src/spec_dock/assets/spec_dock/docs/reference_github.md`
  - `src/spec_dock/assets/spec_dock/docs/reference_sync.md`
  - CLI help tests from S01/S04
- 対応:
  - `reference_github.md` に、uninstall が GitHub issue / remote state を変更せず、package/environment uninstall でもない repo-local managed artifact removal であることを追記する。
  - `reference_sync.md` は generated state と uninstall cleanup の説明が必要か点検し、不要なら `report.md` に no-op rationale を記録する。
  - installer/runtime help が final flag contract と一致することを tests で確認する。
- doc update owner:
  - doc-writer when updates are required
- spec/doc review:
  - reviewer: spec-reviewer
- 具体テストケース一覧:
  - `tc-s90-001` inspect-only: docs boundary matches uninstall contract
    - 前提: S01-S04 implementation complete.
    - 操作: inspect provider docs and help output.
    - 期待結果: docs/help state no GitHub mutation, no package/environment uninstall, and explain repo-local artifact removal.
    - 失敗検出: operator docs imply GitHub/package uninstall side effects.
    - 検証方法: docs diff inspection plus relevant unittest/help assertions.
    - 関連 closure id: tc-018
- step closure contract:
  - close 条件: docs updated or no-op rationale recorded, spec-reviewer pass.
  - report evidence: Docs Impact Resolution, Reviewer Gate Status.
- step gate:
  - reviewer: spec-reviewer; code-reviewer if tests/code changed.
  - no-op 条件: allowed only when docs inspection records that existing docs/help already cover tc-018, tc-022, and `--json` agent-execution guidance without changes.
  - report update: record Docs Impact Resolution and Reviewer Gate Status before S99.

### 最終品質ゲート S99 — final quality gate
- 対象:
  - whole issue integrated diff and evidence
- 対応:
  - Run focused tests and full baseline, validate/sync, diff checks.
  - Run final QA/code/spec reviewers.
  - Ensure all closure ids are covered in `report.md`.
- 必須コマンド / evidence:
  - `python -m unittest tests.test_init_update -v`
  - `python -m unittest tests.cli_runtime.test_uninstall -v`
  - `python -m unittest discover -v`
  - `./spec-dock/scripts/spec-dock validate`
  - `./spec-dock/scripts/spec-dock sync` or `./spec-dock/scripts/spec-dock sync --no-github` with opt-out reason
  - `git diff --check`
- final reviewers:
  - qa-reviewer: test sufficiency and integration-test need
  - code-reviewer: issue-wide integrated diff
  - spec-reviewer: requirement/design/plan/report/docs/implementation/test consistency
- 具体テストケース一覧:
  - `tc-s99-001` manual-required: final gate bundle complete
    - 前提: S01-S04 and S90 closed.
    - 操作: run required commands and reviewers.
    - 期待結果: commands pass or blockers are recorded; reviewers return pass.
    - 失敗検出: issue handed off with missing closure or stale reviewer state.
    - 検証方法: report final quality gate evidence.
    - 関連 closure id: tc-019
- step closure contract:
  - close 条件: all final gates pass and report evidence is complete.
  - report evidence: Final Quality Gate, Closure Coverage, Reviewer Gate Status.
- step gate:
  - reviewer: qa-reviewer, code-reviewer, spec-reviewer
  - no-op 条件: not applicable; S99 is evidence-only but required.
  - report update: record Final Quality Gate, complete Closure Coverage, final Reviewer Gate Status, and any blockers before issue handoff.

## Final Exit Contract
- Implementation readiness:
  - Plan gate must have fresh spec-reviewer pass before issue execution starts.
  - All required closure ids are mapped to steps and have planned verification evidence.
- Completion readiness after execution:
  - Every implementation step is committed or approved-no-op with report evidence.
  - S90 docs impact is resolved.
  - S99 final QA/code/spec gates pass.
  - `report.md` has no open decision ledger entries or unresolved blocking EAL entries.
- Not included:
  - This plan does not perform `issue finish`, PR creation, merge preparation, or lifecycle closure.
