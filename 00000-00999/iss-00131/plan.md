---
種別: 実装計画書（Issue）
ID: "iss-00131"
タイトル: "Restore guarded workspace-write authoring roles"
関連GitHub: ["#131"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-05-27"
依存: ["requirement.md", "design.md"]
親: ["epic-00112", "init-local-00003"]
---

# iss-00131 Restore guarded workspace-write authoring roles — 実装計画（実行契約）

## この計画で満たす要件ID
- AC:
  - AC-001: custom Permission Profile が完全に削除される
  - AC-002: 両 static role が guarded workspace-write contract を持つ
  - AC-003: fresh spawn が unavailable で拒否されない
  - AC-004: scope-local discussion authoring が可能である
  - AC-005: forbidden path edits は採用されない
  - AC-006: docs / skills / tests が guarded workspace-write 方針を一貫して説明する
  - AC-007: provider authority と dogfooding mirror が同期している
  - AC-008: final validation が通る
  - AC-009: 親 Epic との scope gap が明示される
- EC:
  - EC-001: parent permission profile override により child が write できない
  - EC-002: child が forbidden path を編集できてしまう
  - EC-003: network disabled により notify / helper command が失敗する
  - EC-004: role remains unavailable after Permission Profile removal
  - EC-005: historical docs に old Permission Profile / scoped-context wording が残る
- 制約:
  - `default_permissions` / `[permissions.*]` は復活させない。
  - `delegated-authoring scoped-context` は復活させない。
  - `system-architect` / `implementation-planner` は this issue の canonical spec authoring delegate として使わない。
  - actual `design.md` / `plan.md` delegated canonical draft authoring は this issue の完了条件に含めない。

## 依存関係から導く実装順序
- 依存関係の正本:
  - `design.md` の依存関係分析、インターフェース契約、ファイル変更計画。
- 順序ルール:
  - role TOML contract の tests を先に固定する。
  - provider assets を先に更新し、dogfooding mirror は provider 後に同期する。
  - manual smoke は role TOML / mirror / docs 更新後に実施する。
- step 依存サマリー:
  - S01:
    - 依存: requirement AC-001/AC-002、design Static role TOML contract。
    - unblock: broken custom Permission Profile を tests で検出できる。
    - 対象ファイル: `tests/test_init_update.py`、provider role TOML。
  - S02:
    - 依存: S01 の role contract。
    - unblock: skills/docs が guarded workspace-write operation を説明できる。
    - 対象ファイル: provider `.codex/AGENTS.md`、role skills、workflow docs、docs tests。
  - S03:
    - 依存: S01/S02 provider changes。
    - unblock: dogfooding mirror と parity tests。
    - 対象ファイル: `.codex` / `.agents` / `spec-dock/docs` mirror。
  - S04:
    - 依存: S01-S03。
    - unblock: live host fresh spawn と discussion write evidence。
    - 対象: manual smoke、`report.md`。
  - S90:
    - 依存: S02/S03。
    - unblock: stale docs wording と parent Epic gap follow-up の最終整理。
  - S99:
    - 依存: S01-S04/S90。
    - unblock: final quality gates。

## ステップ一覧
- S01:
  - 観測可能な振る舞い: provider role TOML が custom Permission Profile を持たず、workspace-write / network disabled contract を満たす。
  - 依存: pass 済み requirement/design。
  - unblock: role config の core failure を解く。
  - 対象ファイル: `tests/test_init_update.py`, `src/spec_dock/assets/install_root/.codex/agents/system-architect.toml`, `src/spec_dock/assets/install_root/.codex/agents/implementation-planner.toml`
  - 閉じる要件: AC-001, AC-002, EC-004 の一部
  - レビューゲート: code-reviewer
- S02:
  - 観測可能な振る舞い: provider skills/docs/tests が guarded workspace-write discussion authoring を説明し、read-only final path / Permission Profile / scoped-context を current success path にしない。
  - 依存: S01
  - unblock: mirror sync と docs impact closure。
  - 対象ファイル: provider `.codex/AGENTS.md`, provider role skills, provider workflow/phase docs, `tests/test_init_update.py`
  - 閉じる要件: AC-005, AC-006, AC-009, EC-002, EC-005
  - レビューゲート: spec-reviewer
- S03:
  - 観測可能な振る舞い: dogfooding mirror が provider role/docs contract と一致する。
  - 依存: S01/S02
  - unblock: manual smoke が dogfooding role config で実行できる。
  - 対象ファイル: `.codex`, `.agents`, `spec-dock/docs`, parity tests if needed
  - 閉じる要件: AC-007
  - レビューゲート: code-reviewer or spec-reviewer
- S04:
  - 観測可能な振る舞い: fresh spawn と new discussion Markdown write probe の pass/fail/unavailable を report に記録する。
  - 依存: S01-S03
  - unblock: AC-003/AC-004 の live evidence。
  - 対象ファイル: `report.md`、manual smoke による新規 discussion draft evidence file if pass
  - 閉じる要件: AC-003, AC-004, AC-005, EC-001, EC-002, EC-003, EC-004
  - レビューゲート: spec-reviewer for evidence completeness
- S90:
  - 観測可能な振る舞い: docs impact と parent Epic gap が report に整理され、blocking stale wording がない。
  - 依存: S02/S03
  - 閉じる要件: AC-006, AC-009, EC-005
  - レビューゲート: spec-reviewer
- S99:
  - 観測可能な振る舞い: targeted tests、validate、diff check、final reviewers が pass する。
  - 依存: S01-S04/S90
  - 閉じる要件: AC-008
  - レビューゲート: qa-reviewer, code-reviewer, spec-reviewer

## 要件 ↔ ステップ対応
- AC-001 -> S01
- AC-002 -> S01
- AC-003 -> S04
- AC-004 -> S04
- AC-005 -> S02, S04
- AC-006 -> S02, S90
- AC-007 -> S03
- AC-008 -> S99
- AC-009 -> S02, S90
- EC-001 -> S04
- EC-002 -> S02, S04
- EC-003 -> S04
- EC-004 -> S01, S04
- EC-005 -> S02, S90

## 仕様固定クロージャ索引

| 識別子（ID） | ステップ（step） | スライス（slice） | 種別（type） | 仕様リンク | 固定する期待値 | 観測可能な入力 / 状態 | 防ぐ bug class | 必須 | 証跡レベル（evidence level） | クロージャ証跡（closure evidence） |
|---|---|---|---|---|---|---|---|---|---|---|
| tc-001 | S01 | role TOML no profile | acceptance | AC-001 | 対象 provider TOML に `default_permissions`、`permissions`、unsupported `write` glob がない | provider role TOML parse/text | custom Permission Profile compile failure regression | yes | red-required | asset test output |
| tc-002 | S01 | workspace-write contract | acceptance | AC-002 | 対象 provider TOML は `sandbox_mode = "workspace-write"`、`approval_policy = "never"`、`web_search = "disabled"`、`network_access = false` を持つ | provider role TOML parse/text | accidental read-only fallback or network-enabled write role | yes | red-required | asset test output |
| tc-003 | S02 | provider guidance | acceptance | AC-006 | provider skills/docs は guarded workspace-write discussion authoring、新規 discussion draft only、diff guard mandatory を説明する | provider docs/assets | stale read-only / Permission Profile / scoped-context guidance | yes | inspect-only | rg inspection + spec-reviewer |
| tc-004 | S02 | forbidden paths / parent gap | acceptance | AC-005/AC-009 | docs explain forbidden path diff adoption-ineligible and parent Epic canonical draft authoring remains follow-up | provider docs/report | scope creep into canonical draft authoring | yes | inspect-only | docs inspection |
| tc-005 | S03 | mirror parity | acceptance | AC-007 | dogfooding `.codex`, `.agents`, `spec-dock/docs` mirror provider contract | provider/mirror files | provider-only or mirror-only drift | yes | covered-existing | parity tests |
| tc-006 | S03 | scoped-context absent | regression | AC-006 | `delegated-authoring scoped-context` remains unregistered | CLI/runtime tests | accidental scoped-context revival | yes | covered-existing | runtime test output |
| tc-007 | S04 | fresh spawn | acceptance | AC-003 | both roles fresh spawn without `agent type is currently not available` | multi-agent smoke | TOML parse success without role callability | yes | manual-required | report smoke evidence |
| tc-008 | S04 | discussion write probe | acceptance | AC-004/AC-005 | each role can create one new allowed discussion Markdown and no forbidden diff is adopted | git status/diff after smoke | workspace-write out-of-scope adoption | yes | manual-required | report diff guard evidence |
| tc-009 | S99 | final validation | acceptance | AC-008 | targeted tests, validate, diff check, final reviewers pass | final worktree | integration drift | yes | covered-existing | final report ledger |

## レビュー / QA ゲート方針
- RG1 step review:
  - S01: code-reviewer for TOML/test contract.
  - S02: spec-reviewer for docs/skills/workflow wording.
  - S03: code-reviewer or spec-reviewer for provider/mirror parity.
  - S04: spec-reviewer for manual smoke evidence completeness.
- QG1 final QA:
  - reviewer: qa-reviewer
  - 範囲: issue-wide obligation coverage、manual smoke residual risk、missing high-value tests。
- SG1 final spec review:
  - reviewer: spec-reviewer
  - 範囲: requirement / design / plan / report / docs / implementation evidence alignment。

## 実行ルール（全ステップ共通）
- `plan.md` は planned contract、`report.md` は observed evidence を所有する。
- repair target である `system-architect` / `implementation-planner` をこの issue の canonical spec authoring delegate として使わない。
- implementation 中に parent Epic canonical draft authoring へ踏み込みたくなった場合は、plan amendment ではなく follow-up issue / Epic amendment として扱う。
- manual smoke で created discussion draft が残る場合、report に provenance と adoption-ineligible / adopted status を記録する。
- forbidden path write を実際に試す negative probe は行わない。forbidden path は diff guard と adoption-ineligible rule で閉じる。

## 実装ステップ

### 実装ステップ S01 — Role TOML contract and asset tests
- 振る舞いの目標:
  - provider role TOML が custom Permission Profile を持たず、guarded workspace-write static role contract を満たす。
- design 参照:
  - `design.md` Static role TOML contract。
- 依存:
  - requirement/design reviewer pass。
- unblock:
  - S02 docs wording and S03 mirror sync。
- 対象ファイル:
  - `tests/test_init_update.py`
  - `src/spec_dock/assets/install_root/.codex/agents/system-architect.toml`
  - `src/spec_dock/assets/install_root/.codex/agents/implementation-planner.toml`
- 計画済み契約:
  - scope:
    - `_assert_codex_delegated_author_adapter_contract` and taxonomy tests を workspace-write no-profile contract に更新する。
    - provider TOMLs から `default_permissions` と `[permissions.*]` を削除する。
    - provider TOMLs に `[sandbox_workspace_write] network_access = false` を追加する。
  - テスト義務:
    - closure id: tc-001, tc-002
    - coverage rationale: role config compile failure と accidental permission broadening / network enable を検出する。
  - Red / 代替証跡の要件:
    - red-required:
      - 更新した tests は現行 TOML の `default_permissions` / `permissions` に対して fail する。
  - 実装範囲:
    - allowed paths:
      - S01 target files only.
    - forbidden changes:
      - docs / skills / mirror changes; runtime command changes; `scoped-context` revival.
  - Green 検証:
    - `python -m unittest tests.test_init_update.TestInitUpdate.test_issue_117_codex_delegated_author_adapters_are_thin_skill_wrappers tests.test_init_update.TestInitUpdate.test_s04_codex_agent_permission_taxonomy_contract -v`
  - Refactor / cleanup ガードレール:
    - test helper を必要最小限で更新し、unrelated agent taxonomy を変えない。
  - report 証跡の記録先:
    - Session Log、TDD Evidence、Step Contract Closure、Test Contract Closure、Reviewer Gate Status。
  - amendment trigger:
    - `sandbox_mode = "workspace-write"` が role TOML で accepted config にならない場合。

#### 委任契約
- 委任ロール:
  - dev-coder or main orchestrator if delegation is unavailable.
- 入力 docs:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - `tests/test_init_update.py`
- 許可 paths:
  - S01 target files.
- 禁止 changes:
  - runtime delegated-authoring command surface.
  - global/user `~/.codex/config.toml`.
  - dogfooding mirror files.
- 受け入れ条件:
  - tc-001 / tc-002 pass.
- 必須 tests:
  - S01 targeted unittest command.
- reviewer focus:
  - TOML parseability, custom profile removal, network disabled, no scoped-context.
- 必須出力:
  - changed files, test output, unresolved risks, report evidence.
- 停止条件:
  - tests require `default_permissions` / `[permissions.*]` to pass.

#### 具体テストケース一覧
- `tc-s01-001` acceptance: custom Permission Profile is removed
  - 前提: provider role TOML exists.
  - 操作: parse TOML in adapter contract test.
  - 期待結果: no `default_permissions`, no `permissions`, no unsupported `write` glob.
  - 失敗検出: old custom Permission Profile remains.
  - 検証方法: unittest.
  - 関連 closure id: tc-001
- `tc-s01-002` acceptance: guarded workspace-write fields are fixed
  - 前提: provider role TOML exists.
  - 操作: parse TOML in adapter/taxonomy tests.
  - 期待結果: `sandbox_mode == "workspace-write"`, `approval_policy == "never"`, `web_search == "disabled"`, `sandbox_workspace_write.network_access is False`.
  - 失敗検出: read-only fallback, danger-full-access, missing network setting, network true.
  - 検証方法: unittest.
  - 関連 closure id: tc-002

#### ステップ完了契約
- closure id:
  - tc-001, tc-002
- close 条件:
  - S01 tests pass.
  - report records Red/Green evidence.
- 検証 evidence:
  - targeted unittest output.
- report evidence:
  - Step Contract Closure / Test Contract Closure / Closure Coverage.
- 残リスク:
  - live host callability remains unproven until S04.

#### ステップゲート
- step reviewer gate:
  - reviewer: code-reviewer
  - review 範囲: S01 TOML/test changes
  - pass 条件: review_status: pass
  - re-review rule: 指摘を修正し pass まで再実行
- commit / no-op gate:
  - closure 状態: committed or batched with report evidence
  - commit 範囲: S01 target files + report evidence

### 実装ステップ S02 — Provider guidance and shipped docs
- 振る舞いの目標:
  - provider guidance が guarded workspace-write discussion authoring contract を一貫して説明する。
- design 参照:
  - `design.md` Docs / skill wording contract。
- 依存:
  - S01 role TOML contract。
- unblock:
  - S03 mirror parity and S90 docs impact.
- 対象ファイル:
  - `src/spec_dock/assets/install_root/.codex/AGENTS.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-system-architect/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-implementation-planner/SKILL.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
  - `src/spec_dock/assets/spec_dock/docs/phase_design.md`
  - `src/spec_dock/assets/spec_dock/docs/phase_plan.md`
  - `src/spec_dock/assets/spec_dock/docs/phase_plan_epic.md`
  - `src/spec_dock/assets/spec_dock/docs/phase_plan_issue.md`
  - `src/spec_dock/assets/spec_dock/docs/authoring/issue-plan.md`
  - `tests/test_init_update.py`
- 計画済み契約:
  - scope:
    - role guidance は new discussion Markdown creation only for this issue's two roles とする。
    - broader workflow の existing discussion update exception は general rule として残してよいが、this issue role guidance / smoke path では禁止する。
    - docs は parent Epic canonical draft authoring gap を follow-up として扱う。
  - テスト義務:
    - closure id: tc-003, tc-004
  - Red / 代替証跡の要件:
    - inspect-only:
      - stale wording inventory を `rg` で記録する。
  - 実装範囲:
    - allowed paths: S02 target files.
    - forbidden changes: role TOML already handled in S01; mirror in S03; runtime command changes.
  - Green 検証:
    - `python -m unittest tests.test_init_update.TestInitUpdate.test_issue_116_delegated_authoring_phase_gate_contract_assets tests.test_init_update.TestInitUpdate.test_issue_127_removed_scoped_context_contract_stays_removed -v`
    - `rg -n "default_permissions|\\[permissions\\.|scoped-context|discussion-file|read-only advisory|Permission Profile" src/spec_dock/assets/install_root src/spec_dock/assets/spec_dock/docs tests`
    - 判定基準:
      - `default_permissions` / `[permissions.` matches in current provider target-role guidance are blocking.
      - `scoped-context` / `discussion-file` matches are allowed only in tests asserting absence or historical/explanatory issue docs outside shipped guidance.
      - `read-only advisory` matches are blocking if they describe target roles' normal success path.
      - `Permission Profile` matches are allowed only when explaining removed/unsupported path or future follow-up, not as current success path.
  - Refactor / cleanup ガードレール:
    - docs wording only; do not redesign canonical draft authoring.
  - report 証跡の記録先:
    - Session Log, docs inspection, Step Contract Closure.
  - amendment trigger:
    - docs cannot be coherent without changing requirement scope.

#### 委任契約
- 委任ロール:
  - doc-writer or main orchestrator.
- 入力 docs:
  - `requirement.md`, `design.md`, `plan.md`
  - provider docs/skills target files
- 許可 paths:
  - S02 target files.
- 禁止 changes:
  - runtime command surface.
  - dogfooding mirror until S03 unless explicitly batching with report evidence.
- 受け入れ条件:
  - tc-003 / tc-004 pass.
- 必須 verification:
  - rg inspection and targeted asset/docs tests.
- reviewer focus:
  - stale Permission Profile/scoped-context/read-only final wording, new draft only contract, parent Epic gap.
- 必須出力:
  - changed files, inspection output, unresolved accepted matches.
- 停止条件:
  - shipped docs still advertise unsupported current success path.

#### 具体テストケース一覧
- `tc-s02-001` inspect-only: provider guidance describes guarded workspace-write
  - 前提: provider docs/skills updated.
  - 操作: run S02 Green verification commands.
  - 期待結果: current guidance says workspace-write discussion authoring, new draft only for these roles, diff guard mandatory.
  - 失敗検出: read-only final path, Permission Profile hard allow-list, scoped-context workaround.
  - 検証方法: exact unittest command + rg inspection + spec-reviewer.
  - 関連 closure id: tc-003
- `tc-s02-002` inspect-only: parent Epic gap remains explicit
  - 前提: docs/report updated.
  - 操作: inspect issue docs and shipped guidance.
  - 期待結果: actual canonical draft authoring is follow-up and not this issue completion.
  - 失敗検出: issue claims to satisfy parent Epic canonical draft authoring.
  - 検証方法: docs inspection/spec-reviewer.
  - 関連 closure id: tc-004

#### ステップ完了契約
- closure id:
  - tc-003, tc-004
- close 条件:
  - No blocking stale shipped guidance remains.
  - report records accepted historical/explanatory matches.
- 検証 evidence:
  - rg output / targeted tests.
- report evidence:
  - Step Contract Closure / docs impact ledger.
- 残リスク:
  - manual smoke remains S04.

#### ステップゲート
- step reviewer gate:
  - reviewer: spec-reviewer
  - review 範囲: provider docs/skills/tests wording
  - pass 条件: review_status: pass
- commit / no-op gate:
  - closure 状態: committed or batched
  - commit 範囲: S02 target files + report evidence

### 実装ステップ S03 — Dogfooding mirror and parity
- 振る舞いの目標:
  - checked-in dogfooding mirror has same guarded workspace-write contract as provider.
- design 参照:
  - `design.md` provider-first and mirror parity.
- 依存:
  - S01/S02 provider changes.
- unblock:
  - S04 manual smoke uses updated dogfooding roles.
- 対象ファイル:
  - `.codex/AGENTS.md`
  - `.codex/agents/system-architect.toml`
  - `.codex/agents/implementation-planner.toml`
  - `.agents/skills/spec-dock-system-architect/SKILL.md`
  - `.agents/skills/spec-dock-implementation-planner/SKILL.md`
  - `spec-dock/docs/**` mirrored docs listed in S02
  - `tests/test_init_update.py` if parity mapping changes
- 計画済み契約:
  - scope:
    - mirror provider changes exactly or through update/sync mechanism.
    - keep historical issue docs unchanged.
  - テスト義務:
    - closure id: tc-005, tc-006
  - Green 検証:
    - `python -m unittest tests.test_init_update.TestInitUpdate.test_issue_71_checked_in_dogfooding_agent_tooling_parity_matches_install_root_assets tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_mirror_docs_match_provider_assets -v`
    - `python -m unittest tests.cli_runtime.test_delegated_authoring.TestDelegatedAuthoringCli.test_scoped_context_subcommand_is_not_registered -v`
  - report 証跡の記録先:
    - parity evidence, scoped-context absence evidence.
  - amendment trigger:
    - provider/mirror cannot match without installer mapping changes outside design.

#### 委任契約
- 委任ロール:
  - dev-coder / doc-writer or main orchestrator.
- 入力 docs:
  - S01/S02 changes, parity tests.
- 許可 paths:
  - S03 target files.
- 禁止 changes:
  - runtime command revival.
  - historical issue artifacts.
- 受け入れ条件:
  - tc-005 / tc-006 pass.
- 必須 verification:
  - parity tests and scoped-context absent test.
- reviewer focus:
  - provider/mirror drift and accidental runtime command revival.
- 必須出力:
  - mirror changed files, test output, unresolved non-parity rationale.
- 停止条件:
  - mirror sync requires broader installer behavior not covered by design.

#### 具体テストケース一覧
- `tc-s03-001` acceptance: mirror matches provider
  - 前提: provider and mirror files updated.
  - 操作: run parity tests.
  - 期待結果: affected `.codex`, `.agents`, `spec-dock/docs` match provider authority.
  - 失敗検出: provider-only or mirror-only contract drift.
  - 検証方法: unittest.
  - 関連 closure id: tc-005
- `tc-s03-002` regression: scoped-context remains absent
  - 前提: runtime unchanged.
  - 操作: run scoped-context unregistered test.
  - 期待結果: `delegated-authoring scoped-context` remains invalid.
  - 失敗検出: accidental parser/command revival.
  - 検証方法: unittest.
  - 関連 closure id: tc-006

#### ステップ完了契約
- closure id:
  - tc-005, tc-006
- close 条件:
  - parity tests and scoped-context absent test pass.
- 検証 evidence:
  - test outputs.
- report evidence:
  - Step Contract Closure and Test Contract Closure.
- 残リスク:
  - live host smoke pending.

#### ステップゲート
- step reviewer gate:
  - reviewer: code-reviewer or spec-reviewer
  - pass 条件: review_status: pass
- commit / no-op gate:
  - closure 状態: committed or batched
  - commit 範囲: S03 target files + report evidence

### 実装ステップ S04 — Manual fresh spawn and discussion write smoke
- 振る舞いの目標:
  - live host confirms whether updated roles can fresh spawn and create one new allowed discussion Markdown.
- design 参照:
  - `design.md` シーケンス差分 and manual test strategy.
- 依存:
  - S01-S03 completed in working tree.
- unblock:
  - AC-003 / AC-004 / EC classification.
- 対象ファイル:
  - `report.md`
  - allowed new discussion draft files created by smoke, if any
- 計画済み契約:
  - scope:
    - spawn `system-architect` with `fork_context=false`.
    - spawn `implementation-planner` with `fork_context=false`.
    - each role gets explicit task-local consent with:
      - target node: `iss-00131`
      - delegated role name
      - allowed discussion path rule: active issue `discussions/` direct child only
      - exact target path
      - filename rule: `<ts>-<kind>-<slug>.md` or `<ts>-<nn>-<kind>-<slug>.md`
      - forbidden paths/actions
      - stop/invalidation conditions
      - report ledger destinations
    - each role gets explicit target path for one new discussion Markdown under active issue `discussions/`.
    - existing discussion draft updates are forbidden during smoke.
    - run before/after `git status --short`.
  - テスト義務:
    - closure id: tc-007, tc-008
  - manual-required:
    - Record tool result or unavailable error.
    - Record Workflow Delegation Consent for each smoke run.
    - Record Delegated Draft Evidence for each produced draft, including `created_by_role`, `scope_id`, `source_paths`, `intended_targets`, `adoption_status: unreviewed`, `reflected_to: []`, `diff_guard_result`, fallback decision, report evidence destination, and adoption ledger note.
    - Record changed files and classify pass/adoption-ineligible/blocked.
    - Record Evidence Adoption Ledger entry for each draft using the workflow schema values `adopted` / `partially_adopted` / `rejected` / `deferred` / `stale` / `blocked`.
    - Record `adoption-ineligible` as promotion eligibility / failure classification / rationale, not as the EAL `adoption_status` value.
    - Do not run destructive or forbidden-path write probe.
  - expected:
    - no `agent type is currently not available`.
    - exactly one allowed new discussion Markdown per successful delegated role smoke.
    - filename matches the discussion naming rule.
    - no existing discussion file is modified.
    - no forbidden path is changed.
  - report 証跡の記録先:
    - Manual Smoke Evidence, Delegated Draft Evidence, Evidence Adoption Ledger, Step Contract Closure.
  - amendment trigger:
    - roles remain unavailable after profile removal due repo config error.

#### 委任契約
- 委任ロール:
  - N/A for execution. Main orchestrator performs host smoke; the target roles are the system under test.
- 入力 docs:
  - requirement/design/plan
  - updated dogfooding role TOMLs and skills
- 許可 paths:
  - `report.md`
  - new files directly under active issue `discussions/` created by smoke and matching `<ts>-<kind>-<slug>.md` or `<ts>-<nn>-<kind>-<slug>.md`
- 禁止 changes:
  - source/test/config/docs changes during smoke, except report evidence.
  - existing discussion draft updates.
  - discussion files whose name does not match the naming rule.
  - forbidden path write probes.
- 受け入れ条件:
  - tc-007 / tc-008 pass or blocked with explicit non-pass evidence.
- 必須 verification:
  - before/after status.
  - multi-agent result.
  - diff guard.
  - filename rule inspection.
  - Workflow Delegation Consent / Delegated Draft Evidence / Evidence Adoption Ledger entries.
- reviewer focus:
  - no success claim when host/tool unavailable; no forbidden diff adoption.
- 必須出力:
  - smoke result summary, changed files, AC/EC classification, unresolved host limitation.
- 停止条件:
  - role remains unavailable and no repo-config fix remains in scope.

#### 具体テストケース一覧
- `tc-s04-001` manual-required: fresh spawn system-architect
  - 前提: updated dogfooding `.codex/agents/system-architect.toml`.
  - 操作: spawn `system-architect`, `fork_context=false`, with task-local consent and exact new target path matching `<ts>-kind-slug.md`.
  - 期待結果: no unavailable error; exactly one new allowed discussion Markdown; no existing draft update; Workflow Delegation Consent and Delegated Draft Evidence recorded.
  - 失敗検出: unavailable, host/tool error, forbidden diff, filename mismatch, missing consent/provenance, existing draft update.
  - 検証方法: multi-agent result + git status/diff + filename/provenance/report ledger inspection.
  - 関連 closure id: tc-007, tc-008
- `tc-s04-002` manual-required: fresh spawn implementation-planner
  - 前提: updated dogfooding `.codex/agents/implementation-planner.toml`.
  - 操作: spawn `implementation-planner`, `fork_context=false`, with task-local consent and exact new target path matching `<ts>-kind-slug.md`.
  - 期待結果: no unavailable error; exactly one new allowed discussion Markdown; no existing draft update; Workflow Delegation Consent and Delegated Draft Evidence recorded.
  - 失敗検出: unavailable, host/tool error, forbidden diff, filename mismatch, missing consent/provenance, existing draft update.
  - 検証方法: multi-agent result + git status/diff + filename/provenance/report ledger inspection.
  - 関連 closure id: tc-007, tc-008
- `tc-s04-003` manual-required: diff guard classification
  - 前提: after each smoke run.
  - 操作: inspect changed files and report ledger entries.
  - 期待結果: allowed new discussion Markdown only; otherwise adoption-ineligible / blocked / rejected is recorded with fallback decision.
  - 失敗検出: canonical/source/test/config/mirror/non-Markdown/existing draft update, missing Evidence Adoption Ledger, missing diff_guard_result, missing fallback decision.
  - 検証方法: git diff/status, filename check, Workflow Delegation Consent, Delegated Draft Evidence, Evidence Adoption Ledger.
  - 関連 closure id: tc-008

#### ステップ完了契約
- closure id:
  - tc-007, tc-008
- close 条件:
  - manual smoke evidence recorded.
  - AC-003/AC-004 pass only if both roles spawn and allowed discussion write path succeeds.
  - blocked/unavailable is explicit non-pass evidence.
  - created draft filenames match discussion naming rule.
  - no existing discussion draft is modified.
  - Workflow Delegation Consent, Delegated Draft Evidence, Evidence Adoption Ledger, and fallback/adoption-ineligible classification are complete for each smoke attempt.
- 検証 evidence:
  - multi-agent results and diff guard output.
- report evidence:
  - Manual Smoke Evidence / Delegated Draft Evidence / Step Contract Closure.
- 残リスク:
  - parent permission override may require follow-up.

#### ステップゲート
- step reviewer gate:
  - reviewer: spec-reviewer
  - review 範囲: S04 report evidence
  - pass 条件: review_status: pass
- commit / no-op gate:
  - closure 状態: report-evidence committed or batched
  - commit 範囲: report and smoke discussion files if accepted as evidence

### ドキュメント影響の解消ステップ S90
- 対象:
  - provider docs, dogfooding docs, role skills, `.codex/AGENTS.md`, report follow-up.
- 対応:
  - run stale wording inspection:
    - `rg -n "default_permissions|\\[permissions\\.|scoped-context|discussion-file|read-only advisory|Permission Profile|actual design.md|actual plan.md" src/spec_dock/assets/install_root src/spec_dock/assets/spec_dock/docs .codex .agents spec-dock/docs tests`
  - classify remaining matches:
    - acceptable: historical issue docs, this issue explanatory text, tests asserting absence, parent Epic gap note.
    - unacceptable: current shipped guidance advertising old Permission Profile / scoped-context / read-only final path for target roles.
- doc update owner:
  - doc-writer or main orchestrator.
- spec/doc review:
  - reviewer: spec-reviewer
  - pass 条件: no blocking stale wording remains.

### 最終品質ゲートステップ S99
- branch diff 範囲:
  - provider assets, dogfooding mirror assets, tests, issue docs/report, smoke discussion evidence if any.
- 必須 validation:
  - S01 targeted unittest command.
  - S03 parity tests.
  - `python -m unittest tests.cli_runtime.test_delegated_authoring.TestDelegatedAuthoringCli.test_scoped_context_subcommand_is_not_registered -v`
  - `./spec-dock/scripts/spec-dock validate`
  - `git diff --check`
- final QA gate:
  - reviewer: qa-reviewer
  - 範囲: obligation coverage, manual smoke residual risk, missing tests.
  - pass 条件: review_status: pass
- final code review ゲート:
  - reviewer: code-reviewer
  - 範囲: TOML/tests/mirror changes, no accidental permission profile, no scoped-context.
  - pass 条件: review_status: pass
- final spec review ゲート:
  - reviewer: spec-reviewer
  - 範囲: requirement / design / plan / report / implementation / tests / docs alignment.
  - pass 条件: review_status: pass
- final commit gate:
  - commit 範囲:
    - all accepted implementation changes and report evidence.
  - final report ledger:
    - all decision entries resolved/superseded; no blocking open entries.

### PR review follow-up 2 ステップ S99-PR-REVIEW-2
- trigger:
  - GitHub Codex review on PR #132 raised additional P2 findings after the first follow-up.
- 観測可能な振る舞い:
  - `delegated-authoring diff-guard` accepts only exactly one new discussion draft for the guarded scope.
  - `baseline-status` without `# head` in an unborn repository does not force `git_head_failed`; `HEAD` comparison is required only when the baseline records a head.
  - New discussion frontmatter must have `scope_id` equal to `--scope`.
  - `created_by_role` must match the authorized `--role` passed to `delegated-authoring diff-guard`.
  - `source_paths` and `intended_targets` must be non-empty YAML block lists; inline scalar values and `[]` are not sufficient adoption provenance.
  - Ignored file / directory side effects are blocked when created after baseline.
  - `.env*` read denial remains instruction-forbidden soft control under the explicit no-Permission-Profile requirement; diff guard pass does not prove no `.env*` read occurred.
- 依存:
  - S99-PR-REVIEW first follow-up and PR #132 Codex review feedback.
- 対象ファイル:
  - provider and dogfooding delegated-authoring runtime.
  - delegated-authoring domain/CLI tests.
  - provider and dogfooding role skills.
  - provider and dogfooding `workflow_spec_authoring.md`.
  - this `plan.md` and `report.md`.
- 閉じる要件:
  - AC-004, AC-005, AC-008.
- validation:
  - `python -m unittest tests.domain_runtime.test_delegated_authoring tests.cli_runtime.test_delegated_authoring -v`
  - `python -m unittest tests.test_init_update -v`
  - `python -m unittest discover -v`
  - `git diff --check`
  - `./spec-dock/scripts/spec-dock validate`
- reviewer gates:
  - code-reviewer, qa-reviewer, spec-reviewer fresh pass after follow-up 2 fixes.
- report evidence:
  - EAL entry for adopted Codex PR review follow-up 2.
  - reviewer gate status row for follow-up 2.
  - final validation rows for targeted tests, full suite, diff check, validate, and PR checks after push.

### PR review follow-up 3 ステップ S99-PR-REVIEW-3
- trigger:
  - Final reviewer passes after follow-up 2 required cleanup for S04 adoption-state wording, decision-ledger closure, QA coverage gaps, and empty ignored-directory handling.
- 観測可能な振る舞い:
  - S04 smoke rows remain deferred when full-worktree diff guard blocks adoption.
  - No-HEAD baseline and modified preexisting ignored-file scenarios are covered by CLI regressions.
  - Empty ignored directories under guarded ignored surfaces are either detected or explicitly documented as residual risk.
- 依存:
  - S99-PR-REVIEW-2 implementation and reviewer feedback.
- 対象ファイル:
  - delegated-authoring runtime and tests.
  - this `plan.md` and `report.md`.
- 閉じる要件:
  - AC-004, AC-005, AC-008.
- validation:
  - delegated-authoring targeted domain/CLI tests.
  - `git diff --check`
  - `./spec-dock/scripts/spec-dock validate`
- reviewer gates:
  - code-reviewer, qa-reviewer, spec-reviewer fresh pass after follow-up 3 cleanup.
- report evidence:
  - S99-PR-REVIEW-3 rows in the reviewer gate status table.
  - final validation rows for follow-up 2 cleanup and final report/parity validation.

### PR review follow-up 4 ステップ S99-PR-REVIEW-4
- trigger:
  - Additional bounded ignored-scan review found P2 risks around ignored symlink retargets and unbounded ignored directory fingerprinting.
- 観測可能な振る舞い:
  - The diff guard records symlink target state and blocks ignored symlink retargeting on guarded surfaces.
  - Ignored side-effect scanning is bounded to `.env*`, `manual-tests/**`, and forbidden roots instead of recursively fingerprinting arbitrary ignored caches.
  - Preexisting ignored guarded directories still block modified child side effects where the scan is intentionally in scope.
  - Temporary-directory cleanup races in delegated-authoring CLI tests do not mask assertion outcomes.
- 依存:
  - S99-PR-REVIEW-3 cleanup and bounded ignored-scan reviewer feedback.
- 対象ファイル:
  - delegated-authoring runtime and CLI/domain tests.
  - this `report.md`.
- 閉じる要件:
  - AC-004, AC-005, AC-008.
- validation:
  - `python -m unittest tests.domain_runtime.test_delegated_authoring tests.cli_runtime.test_delegated_authoring -v`
  - `python -m unittest tests.cli_runtime.test_delegated_authoring -v`
  - focused CLI regression for baseline status.
  - `python -m unittest discover -v`
  - `git diff --check`
  - `./spec-dock/scripts/spec-dock validate`
- reviewer gates:
  - code-reviewer and qa-reviewer fresh pass.
  - spec-reviewer records closure-state feedback; report must show pending remote rerun honestly until PR checks complete.
- report evidence:
  - EAL-020.
  - S99-PR-REVIEW-4 rows in the reviewer gate status table.
  - final validation rows for bounded ignored-scan follow-up.

### PR review follow-up 5 ステップ S99-PR-REVIEW-5
- trigger:
  - PR #132 checks completed after the tolerant teardown fix and report ledger needed to move from pending remote rerun to checked pass.
- 観測可能な振る舞い:
  - PR #132 latest checked head records `validate` pass x2 and `provider-tests` pass x2.
  - S99-PR-REVIEW status is `pass` only after local validation, reviewer gates, commit/push, and remote checks align for the latest pushed head.
  - Final diff-guard hardening passes the authorized role through the CLI so a `system-architect` run cannot claim `spec-dock-implementation-planner` provenance, and vice versa.
  - Final duplicate provenance hardening rejects ambiguous frontmatter where a required evidence key appears more than once.
  - Final CLI parser coverage rejects `delegated-authoring diff-guard` calls that omit `--role`.
  - Final CLI parser coverage rejects `delegated-authoring diff-guard` calls that omit `--baseline-status`, so adoption checks always have a pre-run snapshot.
  - Frontmatter scalar parsing accepts quoted `created_by_role` / `scope_id` values while preserving exact authorized role and scope matching.
  - `issue finish` remains blocked only by lifecycle authority (`active_synthetic_approval_not_lifecycle_approval`), not implementation readiness.
- 依存:
  - S99-PR-REVIEW-4 cleanup and pushed PR head.
- 対象ファイル:
  - this `plan.md` and `report.md`.
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/delegated_authoring.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/delegated_authoring.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/delegated_authoring.py`
  - `spec-dock/scripts/spec_dock_runtime/domain/delegated_authoring.py`
  - `spec-dock/scripts/spec_dock_runtime/application/delegated_authoring.py`
  - `spec-dock/scripts/spec_dock_runtime/commands/delegated_authoring.py`
  - `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`
  - `spec-dock/docs/workflow_spec_authoring.md`
  - `tests/domain_runtime/test_delegated_authoring.py`
  - `tests/cli_runtime/test_delegated_authoring.py`
- 閉じる要件:
  - AC-008 and final report traceability.
- validation:
  - `gh pr checks 132 --watch --interval 60`
  - `python -m unittest tests.domain_runtime.test_delegated_authoring tests.cli_runtime.test_delegated_authoring -v`
  - `python -m unittest discover -v`
  - provider/dogfooding runtime parity targeted tests.
  - provider/dogfooding runtime `cmp -s` for changed runtime files.
  - `git diff --check`
  - `./spec-dock/scripts/spec-dock validate`
- reviewer gates:
  - spec-reviewer final pass after report/test-diff ledger refresh; non-blocking P2 traceability cleanup is handled by this append-only plan amendment.
  - code-reviewer / qa-reviewer pass after duplicate provenance and required-role parser follow-up.
  - spec-reviewer re-review after the latest pending remote rerun state is recorded.
- report evidence:
  - PR #132 checks after bounded ignored-scan follow-up row records latest checked head and all passing checks.
  - S99-PR-REVIEW-5 reviewer gate status row records final spec pass.
  - EAL-022 records duplicate provenance and required-role parser follow-up.
  - Final validation rows record the 69-test targeted suite, whitespace/spec validation, runtime parity, and post-push PR checks.
  - EAL-023 records required baseline-status and quoted scalar hardening.

## 未確定事項
- Q-001:
  - 質問: current host で role-level workspace-write が effective か。
  - 推奨案: S04 で確認し、pass/fail/blocked を report に記録する。
  - 影響範囲: AC-003/AC-004 completion。
- Q-002:
  - 質問: parent Epic canonical draft authoring の follow-up をどう切るか。
  - 推奨案: this issue completion 後に separate issue / Epic amendment candidate として起票する。
  - 影響範囲: epic roadmap。

## 最終完了条件
- AC/EC 達成:
  - AC-001 through AC-009 have report evidence.
  - EC-001/EC-004 are pass or explicit non-pass/blocker; no silent success.
- docs 影響解決:
  - shipped and dogfooding docs do not advertise old target-role success path.
- 全 implementation step 完了:
  - S01-S04, S90, S99 completed or explicitly blocked with workflow-compliant evidence.
- final quality gate pass:
  - qa-reviewer: pass
  - issue-wide code-reviewer: pass
  - spec-reviewer: pass
- final commit 完了:
  - required before PR / issue finish unless user explicitly requests no commit.
- 必須 closure id 完了:
  - tc-001 through tc-009
- final clean state:
  - no unintended staged / unstaged changes.
