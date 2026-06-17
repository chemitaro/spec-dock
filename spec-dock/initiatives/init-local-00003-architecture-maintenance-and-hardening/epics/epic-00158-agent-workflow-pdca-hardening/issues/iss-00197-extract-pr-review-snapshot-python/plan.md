---
種別: 実装計画書（Issue）
ID: "iss-00197"
タイトル: "Extract Python From PR Review Snapshot Script"
関連GitHub: ["#197"]
状態: "draft | approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-17"
依存: ["requirement.md", "design.md"]
親: ["epic-00158", "init-local-00003"]
---

# iss-00197 Extract Python From PR Review Snapshot Script — 実装計画

## この計画で満たす要件ID
- AC-001:
  - provider-side と dogfooding mirror の `fetch_pr_review_snapshot.sh` から Python heredoc を完全に取り除く。
- AC-002:
  - public wrapper invocation 経由で既存 review snapshot behavior と JSON contract を維持する。
- AC-003:
  - provider-side source と dogfooding mirror の file structure / meaning / scaffold installation を揃える。
- EC-001:
  - invalid usage / Python entrypoint failure / stderr handling の互換性を保つ。
- EC-002:
  - malformed GitHub API / fake `gh` output に対する classification / fallback / redacted metadata を保つ。
- 制約:
  - public wrapper path を維持する。
  - review completion / unresolved thread / fallback signal policy は変更しない。
  - provider-side source を正本、dogfooding mirror を validation surface とする。

## 依存関係から導く実装順序
- 参照元:
  - `design.md` の dependency analysis、interface contract、file change plan。
- 順序:
  - S10 baseline characterization が先。抽出前の public wrapper behavior と heredoc removal target を固定する。
  - S20 provider extraction が次。正本である provider-side source を先に変更する。
  - S30 dogfooding mirror / scaffold parity が次。provider の形に mirror と installed asset assertion を揃える。
  - S90 docs impact を最後に判定する。最終 file layout 確定後でなければ stale docs の有無を判断できない。
  - S99 final quality gate で issue-wide closure と reviewers を確認する。

## ステップ一覧
- S10 Characterize wrapper and static extraction guard:
  - 依存: reviewed `requirement.md` / `design.md`
  - unblock: S20
  - 対象: `tests/unit/infra/test_init_update.py`, `report.md`
  - 閉じる要件: AC-001 baseline, EC-001 baseline
  - reviewer: `code-reviewer`
- S20 Provider extraction to `pr_review_snapshot.py`:
  - 依存: S10
  - unblock: S30
  - 対象:
    - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_review_snapshot.sh`
    - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_review_snapshot.py`
    - `tests/unit/infra/test_init_update.py`
  - 閉じる要件: AC-001, AC-002, EC-001, EC-002
  - reviewer: `code-reviewer`
- S30 Dogfooding mirror and scaffold parity:
  - 依存: S20
  - unblock: S90
  - 対象:
    - `.agents/skills/github-pr-observation/scripts/lib/fetch_pr_review_snapshot.sh`
    - `.agents/skills/github-pr-observation/scripts/lib/pr_review_snapshot.py`
    - `tests/unit/infra/test_init_update.py`
  - 閉じる要件: AC-001, AC-003
  - reviewer: `code-reviewer`
- S90 Docs / scaffold / mirror impact resolution:
  - 依存: S30
  - unblock: S99
  - 対象: affected docs / skill text only if inspection finds stale text; otherwise no-op evidence
  - 閉じる要件: non-negotiable constraints, docs impact
  - reviewer: `spec-reviewer`
- S99 Final quality gate:
  - 依存: S10/S20/S30/S90
  - 対象: report evidence and final checks only in success path
  - 閉じる要件: all AC/EC
  - reviewers: `qa-reviewer`, issue-wide `code-reviewer`, `spec-reviewer`

## 要件 ↔ ステップ対応
- AC-001 -> S10, S20, S30, S99
- AC-002 -> S10, S20, S99
- AC-003 -> S30, S99
- EC-001 -> S10, S20, S99
- EC-002 -> S20, S99
- Provider / mirror / no behavior change constraints -> S20, S30, S90, S99

## 仕様固定クロージャ索引（Spec-Locked Closure Index）

| ID | Step | Slice | Type | Spec link | Locked expectation | Observable input / state | Bug class guarded | Required | Evidence level | Closure evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| tc-001 | S10 | baseline | inspection | AC-001 | Current wrappers are confirmed to contain heredoc before extraction and final no-match search pattern is fixed. | `rg -n "python3 - <<'PY'|<<PY|<<'PY'"` against provider/mirror wrappers. | vague inspection hides incomplete extraction | yes | inspect-only | report Test Contract Closure |
| tc-002 | S10/S20 | wrapper compatibility | negative / acceptance | EC-001 | `--help` exits 0; invalid args exit 64 before `gh`; public wrapper remains executable. | direct provider wrapper invocation | validation/usage regression | yes | red-required or covered-existing | focused pytest / report |
| tc-003 | S20 | provider extraction | acceptance | AC-001 | Provider wrapper has no embedded Python heredoc and invokes sibling `pr_review_snapshot.py`. | provider wrapper text and Python file existence | partial extraction | yes | red-required | static test / inspection |
| tc-004 | S20 | review JSON semantics | regression | AC-002, EC-002 | Public wrapper emits compatible S04 JSON with unchanged key contracts and redacted failure metadata. | fake `gh` fixtures through provider wrapper | behavior drift during extraction | yes | covered-existing plus focused regression | pytest / report |
| tc-005 | S20 | `--out` artifact semantics | regression | AC-002 | `--out` and body-mode behavior remain compatible, including `raw/review_bodies.json`. | provider wrapper with body modes and `--out` | artifact/body leakage regression | yes | covered-existing | pytest / report |
| tc-006 | S30 | dogfooding mirror parity | acceptance | AC-003 | Mirror wrapper and `pr_review_snapshot.py` match provider meaning and are heredoc-free. | provider/mirror comparison and static search | provider/mirror drift | yes | red-required | static parity test / report |
| tc-007 | S30 | init/update scaffold | acceptance | AC-003 | `spec-dock init` and `update` install `pr_review_snapshot.py` byte-for-byte from provider source. | temp target repo after init/update | new asset missing from scaffold | yes | red-required | `test_init_update.py` |
| tc-008 | S90 | docs impact | docs / inspection | constraints | docs/skill/scaffold impact is updated or explicitly closed as no-op. | affected docs/skill search | silent docs drift | yes | inspect-only or docs-only | report + spec-reviewer |
| tc-009 | S99 | final gate | quality gate | all AC/EC | all closure IDs have evidence; focused tests/static checks pass; final reviewers pass. | integrated diff, tests, report ledgers | premature completion | yes | manual-required | final gates / report |

## レビュー / QA ゲート方針
- Step reviewer:
  - S10/S20/S30: `code-reviewer`
  - S90: `spec-reviewer`; if text changes are required, `doc-writer` performs the docs-only change before review
  - S99: final `qa-reviewer`, issue-wide `code-reviewer`, and final `spec-reviewer`
- Non-pass handling:
  - `failed`, `unavailable`, `denied`, `waived`, `provisional` は pass ではない。
  - reviewer fail は bounded follow-up step または plan amendment + fresh re-review で処理する。

## 実行ルール（全ステップ共通）
- 1 implementation step = 1 review scope = 1 commit boundary とする。
- runtime / tests / scaffold behavior は `dev-coder` に委任する。
- docs / skill text のみの変更が必要な場合は `doc-writer` に委任する。
- 観測結果、Red / Green / Refactor evidence、reviewer verdict、commit/no-op evidence は `report.md` に記録する。
- 新しい behavior policy、GitHub API signal contract、completion semantics が必要になった場合は実装を止め、requirement/design/plan amendment と fresh spec-review を行う。

## 実装ステップ

### 実装ステップ S10 — Characterize wrapper and static extraction guard
- 振る舞いの目標:
  - 抽出前に public wrapper contract と heredoc removal target を固定する。
- design 参照:
  - interface contract / test strategy
- 依存:
  - reviewed `requirement.md` / `design.md`
- unblock:
  - S20
- 対象ファイル:
  - `tests/unit/infra/test_init_update.py`
  - `report.md` evidence
- 計画済み契約:
  - scope:
    - focused characterization/static guard tests を追加する。
    - baseline heredoc presence と current wrapper behavior を report に記録する。
  - test obligation:
    - closure id: `tc-001`, `tc-002`
    - coverage rationale: Python extraction が wrapper-facing behavior を変える回帰を先に固定する。
  - Red / 代替証跡:
    - `tc-001`: inspect-only baseline。現時点の heredoc presence と final no-match command を記録する。
    - `tc-002`: characterization test。抽出前後で pass すべき current contract を固定する。
  - Green 検証:
    - focused pytest for S10 tests
    - baseline `rg` evidence
  - Refactor guardrail:
    - helper extraction はしない。
  - amendment trigger:
    - wrapper validation が `design.md` と異なる、または heredoc が抽出前から存在しない。

#### 委任契約
- delegated role:
  - `dev-coder`
- input docs:
  - `requirement.md`, `design.md`, `plan.md`, `phase_plan_issue.md`, `authoring/issue-plan.md`, current provider wrapper, focused test sections
- allowed paths:
  - `tests/unit/infra/test_init_update.py`
- forbidden changes:
  - runtime implementation, mirror assets, docs/skills, package/config, GitHub state
- acceptance criteria:
  - `tc-001` / `tc-002` evidence recorded; no behavior change
- required tests / verification:
  - focused pytest for S10 characterization tests
  - baseline heredoc `rg`
- reviewer focus:
  - tests observe public wrapper behavior and avoid private implementation coupling beyond static heredoc guard
- stop conditions:
  - current wrapper contradicts design, implementation changes are needed, or allowed paths are insufficient
- output required:
  - changed files, commands/results, report evidence, Ledger Note or no-material-decision statement

#### 具体テストケース一覧
- `tc-s10-001` inspect-only: baseline heredoc target is fixed
  - 前提: provider and mirror `fetch_pr_review_snapshot.sh` exist.
  - 操作: run `rg -n "python3 - <<'PY'|<<PY|<<'PY'"` against both wrappers.
  - 期待結果: baseline finds current heredoc before implementation; final expectation is no matches after S20/S30.
  - 失敗検出: prevents closing AC-001 with an imprecise manual search.
  - 検証方法: report Test Contract Closure records command and expected transition.
  - 関連 closure id: `tc-001`
- `tc-s10-002` negative: wrapper rejects invalid args before `gh`
  - 前提: provider wrapper is invoked with a fake `PATH` containing a `gh` stub that fails if called.
  - 操作: call `fetch_pr_review_snapshot.sh --repo bad --pr 13` and `--help`.
  - 期待結果: invalid args return `64` with usage and do not call `gh`; `--help` returns `0`.
  - 失敗検出: catches validation moving into Python in a user-visible way.
  - 検証方法: focused pytest in `tests/unit/infra/test_init_update.py`.
  - 関連 closure id: `tc-002`

#### ステップ完了契約
- close 条件:
  - S10 tests pass, baseline `rg` evidence recorded, `code-reviewer` pass, report closure entries complete, step commit/no-op gate closed.

### 実装ステップ S20 — Provider extraction to `pr_review_snapshot.py`
- 振る舞いの目標:
  - provider heredoc を sibling Python entrypoint へ抽出し、public wrapper behavior を維持する。
- 依存:
  - S10
- unblock:
  - S30
- 対象ファイル:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_review_snapshot.sh`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_review_snapshot.py`
  - `tests/unit/infra/test_init_update.py`
- 計画済み契約:
  - scope:
    - provider `pr_review_snapshot.py` を追加する。
    - provider wrapper を薄い wrapper にする。
    - provider no-heredoc / wrapper behavior tests を追加または更新する。
  - test obligation:
    - closure id: `tc-002`, `tc-003`, `tc-004`, `tc-005`
  - Red / 代替証跡:
    - provider static no-heredoc test は抽出前 fail / 抽出後 pass。
    - JSON / body-mode behavior は既存 wrapper tests を regression として再利用し、不足分だけ focused issue-197 assertion を足す。
  - Green 検証:
    - focused issue-197 tests
    - existing direct wrapper review tests for S410, body modes, fallback/no-completion, redacted failures
  - Refactor guardrail:
    - mechanical extraction only; shared helper extraction and behavior cleanup are forbidden.
  - amendment trigger:
    - JSON keys、decision semantics、accepted args、downstream caller behavior の変更が必要になる。

#### 委任契約
- delegated role:
  - `dev-coder`
- input docs:
  - `requirement.md`, `design.md`, `plan.md`, current provider wrapper, existing review snapshot tests
- allowed paths:
  - provider wrapper, provider `pr_review_snapshot.py`, focused tests
- forbidden changes:
  - mirror assets, docs, unrelated observation scripts, completion policy, CI/check collector behavior
- acceptance criteria:
  - provider wrapper no heredoc, provider Python exists, wrapper behavior and JSON contract preserved
- required tests:
  - `uv run pytest tests/unit/infra/test_init_update.py -k "issue_197 or issue_187_s410 or issue_75_pr_observation_review_collector_explicit_trigger_body_caps_and_threads or issue_176_s03_review_collector_returns_codex_review_contract"`
- reviewer focus:
  - behavior preservation, subprocess boundary, path resolution, bash compatibility, no new public env requirements, no semantics drift
- stop conditions:
  - extraction requires review decision policy changes, failure path leaks traceback/stderr, or mirror changes are needed before provider behavior passes
- output required:
  - changed files, commands/results, material Ledger Note or no-material-decision statement, unresolved risks

#### 具体テストケース一覧
- `tc-s20-001` acceptance: provider wrapper has no embedded Python
  - 前提: S20 extraction is applied to provider source.
  - 操作: inspect provider wrapper text for heredoc markers and Python-only definitions from the previous heredoc.
  - 期待結果: no heredoc markers or embedded Python body remain; wrapper invokes sibling `pr_review_snapshot.py`.
  - 失敗検出: catches partial extraction or moving Python into another heredoc.
  - 検証方法: static pytest or `rg` inspection.
  - 関連 closure id: `tc-003`
- `tc-s20-002` acceptance: public wrapper still emits compatible S04 JSON
  - 前提: fake `gh` fixture returns comments, reviews, inline comments, PR metadata, and GraphQL thread state.
  - 操作: call provider wrapper with repo, PR, head SHA, trigger comment, and trigger timestamp.
  - 期待結果: JSON keeps `script`, `collector`, `decision`, `review`, `codex_review`, fingerprints, and limitations contract.
  - 失敗検出: catches semantics drift from module/global initialization changes.
  - 検証方法: existing review collector pytest plus focused issue-197 assertion if needed.
  - 関連 closure id: `tc-004`
- `tc-s20-003` regression: `--out` and body modes remain stable
  - 前提: fake `gh` fixture includes body content and review thread bodies.
  - 操作: invoke wrapper with `--body-mode none`, `out-only`, `trigger-window-truncated`, and `--out`.
  - 期待結果: body inclusion, omission reasons, caps, and `raw/review_bodies.json` behavior match existing assertions.
  - 失敗検出: catches artifact/body leakage or missing output directory behavior.
  - 検証方法: existing body-mode/out pytest.
  - 関連 closure id: `tc-005`

#### ステップ完了契約
- close 条件:
  - provider extraction passes focused tests and static no-heredoc check; `code-reviewer` pass; report closure entries complete; step commit closed.

### 実装ステップ S30 — Dogfooding mirror and scaffold parity
- 振る舞いの目標:
  - provider extraction を dogfooding mirror と installed scaffold assertions へ反映する。
- 依存:
  - S20
- unblock:
  - S90/S99
- 対象ファイル:
  - `.agents/skills/github-pr-observation/scripts/lib/fetch_pr_review_snapshot.sh`
  - `.agents/skills/github-pr-observation/scripts/lib/pr_review_snapshot.py`
  - `tests/unit/infra/test_init_update.py`
- 計画済み契約:
  - scope:
    - mirror wrapper / Python entrypoint を provider と同等にする。
    - `init` / `update` が `pr_review_snapshot.py` を install することを assertion する。
  - test obligation:
    - closure id: `tc-006`, `tc-007`
  - Red / 代替証跡:
    - new asset install/update test は asset assertion 追加前に fail し、実装後 pass。
    - mirror no-heredoc guard は mirror 更新前に fail し、更新後 pass。
  - Green 検証:
    - focused install/update pytest
    - provider/mirror static no-heredoc and parity check
  - Refactor guardrail:
    - test suite reorganization はしない。
  - amendment trigger:
    - provider/mirror equivalence に installer semantics change が必要になる。

#### 委任契約
- delegated role:
  - `dev-coder`
- input docs:
  - `plan.md`, dogfooding rules, existing asset install tests, provider extraction output
- allowed paths:
  - mirror wrapper/Python file, focused scaffold assertions in `test_init_update.py`
- forbidden changes:
  - provider behavior changes except exact parity fixes, docs, config, GitHub state
- acceptance criteria:
  - mirror no heredoc, mirror Python present, init/update installs new asset byte-for-byte, provider/mirror evidence recorded
- required tests:
  - focused install/update pytest for new asset
  - static no-heredoc/parity tests
- reviewer focus:
  - provider-first discipline, shipped asset inventory completeness, mirror drift risk, hermetic tests
- stop conditions:
  - mirror cannot be updated without one-off shortcuts, installer requires behavior change, or new asset is not copied by current init/update mechanics
- output required:
  - changed files, install/update test result, provider/mirror comparison evidence, Ledger Note/no-material-decision

#### 具体テストケース一覧
- `tc-s30-001` acceptance: mirror wrapper and provider wrapper are heredoc-free
  - 前提: S20 provider extraction is complete.
  - 操作: run static heredoc check against provider and mirror wrappers.
  - 期待結果: no heredoc markers in either wrapper.
  - 失敗検出: catches provider-only extraction or dogfooding drift.
  - 検証方法: pytest static assertion or `rg` command.
  - 関連 closure id: `tc-006`
- `tc-s30-002` acceptance: new Python asset installs by init and update
  - 前提: temp target repo and provider `pr_review_snapshot.py`.
  - 操作: call `main(["init", target])`, compare installed bytes, delete installed asset, call `main(["update", target])`, compare bytes again.
  - 期待結果: installed `.agents/.../scripts/lib/pr_review_snapshot.py` exists after init/update and equals provider bytes.
  - 失敗検出: catches missing authoritative path or update not restoring the new asset.
  - 検証方法: `tests/unit/infra/test_init_update.py`.
  - 関連 closure id: `tc-007`

#### ステップ完了契約
- close 条件:
  - S30 tests pass; provider/mirror parity evidence is in report; `code-reviewer` pass; step commit closed.

### 実装ステップ S90 — Docs / scaffold / mirror impact resolution
- 振る舞いの目標:
  - extraction により stale docs / skill text / scaffold references が残っていないことを確認する。
- 依存:
  - S30
- unblock:
  - S99
- 対象:
  - docs / skill text only if stale references are found; otherwise no-op report evidence
- 計画済み契約:
  - scope:
    - affected skill/docs paths を search する。
    - 更新が不要なら approved-no-op として report に記録する。
    - 更新が必要なら `doc-writer` に限定委任する。
  - test obligation:
    - closure id: `tc-008`
  - Green 検証:
    - stale reference search
    - `spec-reviewer` docs/spec alignment
  - amendment trigger:
    - docs change requires new behavior promise not in requirement/design.

#### 委任契約
- delegated role:
  - `doc-writer` only if docs/skill text changes are required; otherwise orchestrator no-op evidence plus `spec-reviewer`
- input docs:
  - `requirement.md`, `design.md`, `plan.md`, affected skill/docs paths, S30 evidence
- allowed paths:
  - affected docs/skill text only
- forbidden changes:
  - code, tests, runtime scripts, config, GitHub state
- required verification:
  - `rg -n "heredoc|pr_review_snapshot.py|fetch_pr_review_snapshot" src/spec_dock/assets/install_root/.agents/skills/github-pr-observation .agents/skills/github-pr-observation spec-dock/docs src/spec_dock/assets/spec_dock/docs`
  - `spec-reviewer` docs/spec alignment
- stop conditions:
  - docs update requires design change or stale docs are outside allowed path

#### 具体テストケース一覧
- `tc-s90-001` inspect-only: docs impact is resolved
  - 前提: S30 mirror/scaffold parity is complete.
  - 操作: search affected skill/docs paths for stale heredoc or wrapper/Python extraction references.
  - 期待結果: no stale references remain, or doc-writer updates only stale text.
  - 失敗検出: catches hidden docs drift before final spec review.
  - 検証方法: search output plus spec-reviewer docs/spec alignment.
  - 関連 closure id: `tc-008`

#### ステップ完了契約
- close 条件:
  - docs impact updated or approved-no-op; `spec-reviewer` pass; report evidence complete.

### 実装ステップ S99 — Final quality gate
- 振る舞いの目標:
  - integrated issue がすべての requirement/design/plan obligation を満たすことを確認する。
- 依存:
  - S10/S20/S30/S90
- 対象:
  - success path では report evidence と final checks のみ
- 計画済み契約:
  - scope:
    - final validation、reviewer passes、report closure evidence を確認する。
  - test obligation:
    - closure id: `tc-009`
  - Green 検証:
    - focused pytest and static no-heredoc check
    - `uv run pytest tests/unit/infra/test_init_update.py` if QA requests broader coverage
    - `./spec-dock/scripts/spec-dock validate`
  - amendment trigger:
    - missing closure row、unplanned bug class、test insufficiency、reviewer failure

#### 委任契約
- delegated roles:
  - `qa-reviewer`, issue-wide `code-reviewer`, `spec-reviewer`
- input docs:
  - final `requirement.md`, `design.md`, `plan.md`, `report.md`, implementation diff, test output, S90 evidence
- allowed paths:
  - none for reviewers; follow-up implementation requires new bounded step
- forbidden changes:
  - direct final-gate implementation changes; reviewer waiver as pass; skipped report closure
- required verification:
  - focused pytest/static commands
  - final reviewer outputs
  - clean worktree evidence after final commit
- stop conditions:
  - any reviewer fails, closure evidence missing, heredoc check matches, or tests fail without unrelated-baseline evidence

#### 具体テストケース一覧
- `tc-s99-001` final gate: all locked expectations are closed
  - 前提: S10/S20/S30/S90 are complete and reviewed.
  - 操作: inspect report closure ledgers and run final focused tests plus static heredoc check.
  - 期待結果: every required closure row has pass/approved-no-op evidence; tests pass; heredoc check has no matches.
  - 失敗検出: catches premature completion with missing evidence.
  - 検証方法: report ledger inspection, pytest, `rg`, reviewer passes.
  - 関連 closure id: `tc-009`

#### ステップ完了契約
- close 条件:
  - QA, issue-wide code review, and spec review pass; final report ledger is complete; final commit/delivery evidence is recorded; no unintended staged/unstaged changes remain.

## 推奨検証コマンド
```bash
uv run pytest tests/unit/infra/test_init_update.py -k "issue_197 or issue_187_s410 or issue_75_pr_observation_review_collector_explicit_trigger_body_caps_and_threads or issue_176_s03_review_collector_returns_codex_review_contract or issue_75_pr_observation_snapshot_includes_s04_review_collector_result"
rg -n "python3 - <<'PY'|<<PY|<<'PY'" src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_review_snapshot.sh .agents/skills/github-pr-observation/scripts/lib/fetch_pr_review_snapshot.sh
```

`rg` command は完了時に no matches でなければならない。`-k` selector が rename で対象を拾わない場合、S99 は concrete test names を指定するか `uv run pytest tests/unit/infra/test_init_update.py` へ広げる。

## Final Exit Contract
- canonical `plan.md` is reviewed by fresh `spec-reviewer` with `review_status: pass`.
- S10/S20/S30/S90/S99 closure evidence exists in `report.md`.
- Required tests and static inspections pass.
- Provider and mirror wrappers are heredoc-free.
- Provider and mirror `pr_review_snapshot.py` exist.
- `init` / `update` install the new Python entrypoint.
- No behavior policy changes were introduced.
- Docs impact is resolved.
- Per-step reviewer gates and commit/no-op gates are closed.
- Final `qa-reviewer`, issue-wide `code-reviewer`, and `spec-reviewer` pass.
- PR delivery and merge-preparation gates are handled if this issue proceeds to PR delivery.
- Lifecycle completion uses `./spec-dock/scripts/spec-dock issue finish`, not manual metadata edits.
