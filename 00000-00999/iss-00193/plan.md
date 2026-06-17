---
種別: 実装計画書（Issue）
ID: "iss-00193"
タイトル: "Node Level Dependency Mutation"
関連GitHub: ["#193"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-17"
依存: ["requirement.md", "design.md"]
親: ["epic-00059", "init-local-00003"]
---

# iss-00193 Node Level Dependency Mutation — 実装計画（実行契約 / Execution Contract）

## この計画で満たす要件ID
- AC:
  - AC-001, AC-002, AC-003, AC-004, AC-005, AC-006, AC-007, AC-008, AC-009
- EC:
  - EC-001, EC-002, EC-003, EC-004, EC-005, EC-006
- 制約:
  - `.meta.json.depends_on` single SoT。
  - No legacy `deps.json` dual-read / fallback / auto-migration。
  - Preflight-first / fail-closed / atomic write。
  - Raw node-level self / ancestor-container / descendant / cycle と compiled issue-level self-edge の保存前拒否。
  - Existing issue->issue behavior preservation。

## 依存関係から導く実装順序
- 依存関係の参照元:
  - `design.md` の「依存関係分析」「モジュール依存図」「ディレクトリ / ファイル変更計画」。
- 順序ルール:
  - Raw node validation helper は unit test で単独に閉じられる foundation step として先に固定する。
  - Public CLI behavior は validation helper がある状態で vertical integration step として Green まで閉じる。
  - Regression consolidation は integration 後に行う。
  - Docs/help は runtime contract が実装済みになってから更新する。
- step 依存サマリー:
  - S01:
    - 依存: reviewed requirement/design。
    - unblock: S02。
    - 対象ファイル: `domain/deps.py`, `tests/unit/domain/test_deps.py`。
  - S02:
    - 依存: S01 raw validation foundation。
    - unblock: S03。
    - 対象ファイル: `infra/deps_reader.py`, `application/mutate_deps.py`, `infra/fs_repo.py`, `cli/bootstrap.py`, `application/ports.py`, `tests/cli_runtime/test_deps.py`。
  - S03:
    - 依存: S02 public integration。
    - unblock: S04, S90。
    - 対象ファイル: `tests/cli_runtime/test_deps.py`, 必要時 S02 touched runtime files。
  - S04:
    - 依存: S03 integration。
    - unblock: S90。
    - 対象ファイル: `tests/cli_runtime/test_deps.py`, 必要時 S03 touched runtime files。
  - S90:
    - 依存: S03/S04 runtime contract。
    - unblock: S99。
    - 対象ファイル: `commands/deps.py`, provider docs, dogfooding docs mirror / snapshot tests as required。
  - S99:
    - 依存: S01..S04/S90 closed。
    - unblock: implementation closeout。
    - 対象ファイル: report evidence only by default。

## ステップ一覧
- S01:
  - 観測可能な振る舞い:
    - Raw node-level graph と candidate add の invalid state を unit-level helper で検出できる。
  - 依存:
    - Requirement / design reviewer pass。
  - unblock:
    - S02。
  - 対象ファイル:
    - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/deps.py`
    - `tests/unit/domain/test_deps.py`
  - 閉じる要件:
    - AC-006, AC-007, EC-001, EC-002, EC-003, EC-004
  - レビューゲート:
    - `code-reviewer`
- S02:
  - 観測可能な振る舞い:
    - `deps add/remove` が valid node-level direct dependency を source `.meta.json.depends_on` に add/remove し、S01 validation を mutation path で使う。
  - 依存:
    - S01。
  - unblock:
    - S03。
  - 対象ファイル:
    - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/deps_reader.py`
    - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/mutate_deps.py`
    - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/fs_repo.py`
    - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/bootstrap.py`
    - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/ports.py`（必要時のみ）
    - `tests/cli_runtime/test_deps.py`
  - 閉じる要件:
    - AC-001, AC-002, AC-005, AC-006, AC-007, EC-001, EC-002, EC-003, EC-004
  - レビューゲート:
    - `code-reviewer`
- S03:
  - 観測可能な振る舞い:
    - Duplicate add、inherited-only remove、raw shorthand matching、existing issue->issue behavior を direct-edge semantics として固定する。
  - 依存:
    - S02。
  - unblock:
    - S04, S90。
  - 対象ファイル:
    - `tests/cli_runtime/test_deps.py`
    - 必要時 S02 touched runtime files の minimal repair。
  - 閉じる要件:
    - AC-003, AC-004, AC-008, EC-005
  - レビューゲート:
    - `code-reviewer`
- S04:
  - 観測可能な振る舞い:
    - Existing issue->issue behavior、preflight-first、no-write、post-sync update/skip を regression として固定する。
  - 依存:
    - S03。
  - unblock:
    - S90。
  - 対象ファイル:
    - `tests/cli_runtime/test_deps.py`
    - 必要時 S03 touched runtime files の minimal repair。
  - 閉じる要件:
    - AC-008, EC-006
  - レビューゲート:
    - `code-reviewer`
- S90:
  - 観測可能な振る舞い:
    - CLI help / provider docs / workflow docs が node-level mutation と direct-edge semantics を説明する。
  - 依存:
    - S03, S04。
  - unblock:
    - S99。
  - 対象ファイル:
    - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/deps.py`
    - `src/spec_dock/assets/spec_dock/docs/reference_deps.md`
    - `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
    - `spec-dock/docs/reference_deps.md`
    - `spec-dock/docs/workflow_issue.md`
    - 必要な snapshot / scaffold tests。
  - 閉じる要件:
    - AC-009
  - レビューゲート:
    - `spec-reviewer`; help parser/test code が非自明なら `code-reviewer` も追加。
- S99:
  - 観測可能な振る舞い:
    - Issue-wide closure coverage、final QA、final code review、final spec review が pass する。
  - 依存:
    - S01..S04, S90。
  - unblock:
    - issue execution closeout。
  - 対象ファイル:
    - 原則なし。findings は bounded step へ戻す。
  - 閉じる要件:
    - all SLCI rows。
  - レビューゲート:
    - `qa-reviewer`, issue-wide `code-reviewer`, final `spec-reviewer`。

## 要件 ↔ ステップ対応
- AC-001 -> S02
- AC-002 -> S02
- AC-003 -> S03
- AC-004 -> S03
- AC-005 -> S02
- AC-006 -> S01, S02
- AC-007 -> S01, S02
- AC-008 -> S03, S04
- AC-009 -> S90
- EC-001 -> S01, S02
- EC-002 -> S01, S02
- EC-003 -> S01, S02
- EC-004 -> S01, S02
- EC-005 -> S03
- EC-006 -> S04

## 仕様固定クロージャ索引（Spec-Locked Closure Index）

| 識別子（ID） | ステップ（step） | スライス（slice） | 種別（type） | 仕様リンク | 固定する期待値 | 観測可能な入力 / 状態 | 防ぐ bug class | 必須 | 証跡レベル（evidence level） | クロージャ証跡（closure evidence） |
|---|---|---|---|---|---|---|---|---|---|---|
| slci-ac-001 | S02 | node-add | acceptance | AC-001 | Valid node-level add stores target node id in source `.meta.json.depends_on` and returns `result=updated` | `deps add --from <initiative|epic|issue> --to <initiative|epic|issue>` | issue-only mutation drift | yes | red-required | report Step/Test Closure |
| slci-ac-002 | S02 | node-remove | acceptance | AC-002 | Node-level remove deletes matching direct ref and returns `result=updated` | source direct ref exists | remove path remains issue-only | yes | red-required | report Step/Test Closure |
| slci-ac-003 | S03 | duplicate-add | acceptance | AC-003 | Duplicate direct add on healthy graph returns `result=unchanged`, skips post-sync, and does not duplicate storage | same direct edge already resolves | duplicate storage / compiled edge confusion | yes | red-required | report Test Closure |
| slci-ac-004 | S03 | inherited-remove | negative | AC-004 | Inherited-only edge is not direct and remove returns `edge_not_found` with no-write | compiled edge exists but source direct ref absent | direct-vs-inherited confusion | yes | red-required | report Test Closure |
| slci-ac-005 | S02 | empty-container | acceptance | AC-005 | Empty epic/initiative valid raw dependency is stored; empty issue expansion is not a write failure | source or target has no child issues | compiled-empty false negative | yes | red-required | report Test Closure |
| slci-ac-006 | S01/S02 | raw-cycle | negative | AC-006 | Candidate raw cycle is rejected before write regardless of child issue presence | reverse edge between empty/non-empty parent nodes | raw cycle saved | yes | red-required | report Test Closure |
| slci-ac-007 | S01/S02 | invalid-container-edge | negative | AC-007 | Self, ancestor/container, descendant, and compiled self-edge candidates are rejected before write | invalid candidate direct edges | future invalid state saved | yes | red-required | report Test Closure |
| slci-ac-008 | S03/S04 | issue-regression | regression | AC-008 | Existing issue->issue add/remove contracts do not regress | existing issue-level scenarios | compatibility regression | yes | covered-existing | report Closure Coverage |
| slci-ac-009 | S90 | docs-help | docs | AC-009 | CLI help and docs describe node-level endpoints, validation, duplicate, empty-container, and direct-edge semantics | `deps add/remove --help`, provider docs, dogfooding mirror | issue-only docs drift | yes | inspect-only | docs/spec review evidence |
| slci-ec-001 | S01/S02 | empty-raw-cycle | negative | EC-001 | `epic-a -> epic-b` plus `epic-b -> epic-a` is rejected as raw cycle, even empty | two epics, reverse add | compiled-only validation | yes | red-required | report Test Closure |
| slci-ec-002 | S01/S02 | issue-to-parent | negative | EC-002 | `issue-x -> parent epic-a` or compiled self-edge candidate is rejected before write | child issue to parent/container | self-edge persistence | yes | red-required | report Test Closure |
| slci-ec-003 | S01/S02 | parent-to-child | negative | EC-003 | `epic-a -> child issue-x` descendant dependency is rejected before write | parent to descendant | descendant invalid edge | yes | red-required | report Test Closure |
| slci-ec-004 | S01/S02 | child-scope-to-ancestor | negative | EC-004 | `epic-a -> parent initiative-a` ancestor/container dependency is rejected before write, even empty | child scope to ancestor | ancestor invalid edge | yes | red-required | report Test Closure |
| slci-ec-005 | S03 | raw-ref-matching | acceptance | EC-005 | Direct resolution matching handles numeric/scoped/URL refs for duplicate add and remove | raw ref is `123`, `"123"`, `owner/repo#123`, URL | raw ref mismatch | yes | red-required | report Test Closure |
| slci-ec-006 | S04 | preflight-first | negative | EC-006 | Broken current graph fails preflight before duplicate/no-op, remove not-found, or node-kind semantics | existing invalid graph | semantic checks before preflight | yes | red-required | report Test Closure |

## レビュー / QA ゲート方針
- RG1 step review:
  - 実施タイミング: 各 implementation step の report evidence 記録後、commit 前。
  - reviewer:
    - S01/S02/S03/S04: `code-reviewer`
    - S90: `spec-reviewer` docs/spec alignment。help parser/test changes が非自明なら `code-reviewer` も追加。
  - pass 条件: `review_status: pass`
- QG1 final QA:
  - reviewer: `qa-reviewer`
  - 範囲: SLCI coverage、missing high-value tests、manual/integration test 要否。
- CG1 final code review:
  - reviewer: issue-wide `code-reviewer`
  - 範囲: final diff、layering、regression risk、test coverage。
- SG1 final spec review:
  - reviewer: final `spec-reviewer`
  - 範囲: requirement / design / plan / report / docs / implementation evidence alignment。

## 実行ルール（全ステップ共通）
- 1 implementation step = 1 observable behavior slice = 1 review scope = 1 commit boundary。
- 実装は `dev-coder`、docs は `doc-writer` に委任する。親エージェントは canonical issue docs / report evidence の統合のみ担当する。
- `plan.md` は planned contract、`report.md` は observed evidence ledger とする。
- Public error code name を新規に固定する必要が出た場合は、実装前に report decision と plan/design amendment 要否を判断する。
- S99 で実装修正をまとめない。findings は bounded step へ戻す。

## 実装ステップ

### 実装ステップ S01 — raw node validation foundation
- 振る舞いの目標（behavior goal）:
  - Raw node-level graph の self / ancestor-container / descendant / cycle を unit-level helper で検出し、empty container でも検証できる foundation を作る。
- design 参照:
  - `design.md`「インターフェース契約」「ドメインモデル差分」。
- 依存:
  - Requirement/design reviewer pass。
- unblock:
  - S02。
- 対象ファイル:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/deps.py`
  - `tests/unit/domain/test_deps.py`
- 計画済み契約（planned contract）:
  - scope:
    - Raw node graph validation helper and unit tests only。
  - テスト義務（test obligation）:
    - closure id:
      - slci-ac-006, slci-ac-007, slci-ec-001, slci-ec-002, slci-ec-003, slci-ec-004
    - coverage rationale:
      - Raw invalid state can be invisible in compiled issue graph when containers are empty, so helper-level tests must close before CLI integration.
  - Red / 代替証跡の要件:
    - red-required:
      - New unit tests fail before the helper rejects raw cycle / ancestor / descendant / self edge.
  - 実装範囲（implementation scope）:
    - allowed paths:
      - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/deps.py`
      - `tests/unit/domain/test_deps.py`
    - forbidden changes:
      - CLI orchestration, infra reader, writer, docs/help, canonical specs/report, GitHub state.
  - Green 検証:
    - `uv run pytest tests/unit/domain/test_deps.py`
  - Refactor / cleanup ガードレール:
    - Keep existing issue-level dependency functions stable; add small helper(s) only for raw node graph validation.
  - report 証跡の記録先:
    - TDD Evidence, Test Contract Closure, Closure Coverage, Delegated Worker Evidence, Reviewer Gate Status.
  - amendment trigger:
    - Helper requires public raw graph projection, new storage schema, or changed requirement semantics.

#### 委任契約（delegation contract）
- 委任ロール（delegated role）:
  - `dev-coder`
- 入力 docs:
  - `requirement.md`, `design.md`, `plan.md`, `workflow_issue.md`, `phase_plan_issue.md`, `authoring/issue-plan.md`, `domain/deps.py`, `tests/unit/domain/test_deps.py`
- 許可 paths:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/deps.py`
  - `tests/unit/domain/test_deps.py`
- 禁止 changes:
  - CLI/application/infra writer changes, docs, canonical specs/report, GitHub state.
- 受け入れ条件:
  - Raw graph validation rejects self, ancestor/container, descendant, and cycle, including empty-container graph cases.
- 必須 tests または docs-only verification:
  - `uv run pytest tests/unit/domain/test_deps.py`
- reviewer focus:
  - Domain helper correctness, graph traversal safety, no issue-level readiness regression.
- 必須出力（output required）:
  - changed files, red/green evidence, verification result, unresolved risks, ledger note.
- 停止条件（stop conditions）:
  - CLI integration is needed to prove the behavior, or validation requires broader topology rewrite.

#### 具体テストケース一覧
- `tc-s01-001` negative: raw cycle between empty epics is rejected
  - 前提: unit test builds a graph with two empty epics and raw map `epic-a -> epic-b`, `epic-b -> epic-a`。
  - 操作: call raw node validation helper。
  - 期待結果: validation raises cycle error。
  - 失敗検出: helper only validates compiled issue graph and misses empty-container cycle。
  - 検証方法: `tests/unit/domain/test_deps.py`。
  - 関連 closure id: `slci-ac-006`, `slci-ec-001`
- `tc-s01-002` negative: source cannot depend on ancestor/container
  - 前提: unit graph has `issue-x` under `epic-a` under `init-a`。
  - 操作: validate `issue-x -> epic-a` and `epic-a -> init-a` candidate raw edges。
  - 期待結果: validation rejects before any write path is involved。
  - 失敗検出: ancestor/container edge is accepted because it has no current compiled issue edge。
  - 検証方法: `tests/unit/domain/test_deps.py`。
  - 関連 closure id: `slci-ac-007`, `slci-ec-002`, `slci-ec-004`
- `tc-s01-003` negative: source cannot depend on descendant
  - 前提: unit graph has `epic-a` with child `issue-x`。
  - 操作: validate `epic-a -> issue-x`。
  - 期待結果: validation rejects descendant dependency。
  - 失敗検出: candidate add bypasses stored-state descendant validation。
  - 検証方法: `tests/unit/domain/test_deps.py`。
  - 関連 closure id: `slci-ac-007`, `slci-ec-003`
- `tc-s01-004` negative: source cannot depend on itself
  - 前提: unit graph has any dependency-capable node。
  - 操作: validate `node -> same node`。
  - 期待結果: validation rejects self dependency。
  - 失敗検出: self edge reaches writer or compiled validation only。
  - 検証方法: `tests/unit/domain/test_deps.py`。
  - 関連 closure id: `slci-ac-007`

#### ステップ完了契約（step closure contract）
- closure id:
  - slci-ac-006, slci-ac-007, slci-ec-001, slci-ec-002, slci-ec-003, slci-ec-004
- close 条件:
  - Unit tests fail before helper implementation and pass with raw validation helper.
- 検証 evidence:
  - `uv run pytest tests/unit/domain/test_deps.py`
- report evidence:
  - Step Contract Closure, Test Contract Closure, Closure Coverage, Closure Delta.
- 残リスク:
  - CLI integration remains S02 responsibility.

#### ステップゲート（step gate）
- step reviewer gate:
  - reviewer: `code-reviewer`
  - review 範囲: domain helper tests and validation correctness.
  - pass 条件: `review_status: pass`
- commit / no-op gate:
  - closure 状態: committed
  - commit 範囲: S01 domain helper and unit tests.

### 実装ステップ S02 — public node-level add/remove integration
- 振る舞いの目標（behavior goal）:
  - `deps add/remove` が initiative / epic / issue node を受け、S01 validation を mutation path に組み込み、valid direct dependency を atomic に add/remove する。
- design 参照:
  - `design.md`「シーケンス差分」「インターフェース契約」。
- 依存:
  - S01。
- unblock:
  - S03。
- 対象ファイル:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/deps_reader.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/mutate_deps.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/fs_repo.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/bootstrap.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/ports.py`（必要時のみ）
  - `tests/cli_runtime/test_deps.py`
- 計画済み契約（planned contract）:
  - scope:
    - Runtime mutation orchestration, all-node direct resolution, writer wrapper compatibility, and public CLI tests.
  - テスト義務（test obligation）:
    - closure id:
      - slci-ac-001, slci-ac-002, slci-ac-005, slci-ac-006, slci-ac-007, slci-ec-001, slci-ec-002, slci-ec-003, slci-ec-004
    - coverage rationale:
      - This is the first public vertical slice that proves node-level mutation and no-write invalid candidates end to end.
  - Red / 代替証跡の要件:
    - red-required:
      - Public CLI tests fail under old issue-only guard and pass after integration.
  - 実装範囲（implementation scope）:
    - allowed paths:
      - S02 target files listed above.
    - forbidden changes:
      - Raw visualization, docs/help wording, delete/sync/active redesign, legacy fallback.
  - Green 検証:
    - `uv run pytest tests/cli_runtime/test_deps.py -k "deps_add or deps_remove"`
    - `uv run pytest tests/unit/domain/test_deps.py`
  - Refactor / cleanup ガードレール:
    - Keep `DepsTopologyLoadResult(issue_depends_on_map, warnings)` stable and preserve existing success text.
  - report 証跡の記録先:
    - TDD Evidence, Step Contract Closure, Test Contract Closure, Closure Delta, Delegated Worker Evidence.
  - amendment trigger:
    - Direct removal requires storage grammar/output contract change, or invalid candidates need new requirement semantics.

#### 委任契約（delegation contract）
- 委任ロール（delegated role）:
  - `dev-coder`
- 入力 docs:
  - `requirement.md`, `design.md`, `plan.md`, S01 evidence, `deps_reader.py`, `mutate_deps.py`, `fs_repo.py`, `cli/bootstrap.py`, `ports.py`, `tests/cli_runtime/test_deps.py`
- 許可 paths:
  - S02 target files.
- 禁止 changes:
  - Docs/help wording, raw visualization, `deps.json` fallback, unrelated downstream commands.
- 受け入れ条件:
  - Valid node-level add/remove works; S01 invalid candidates reject before write; empty valid container dependency is stored.
- 必須 tests または docs-only verification:
  - `uv run pytest tests/cli_runtime/test_deps.py -k "deps_add or deps_remove"`
  - `uv run pytest tests/unit/domain/test_deps.py`
- reviewer focus:
  - Orchestration order, direct metadata writes, S01 validation use, empty container behavior, public output compatibility.
- 必須出力（output required）:
  - changed files, tests run, worker summary, unresolved risks, ledger note for public error-code decisions.
- 停止条件（stop conditions）:
  - Preflight order conflicts with parent epic; new storage field needed; post-sync semantics cannot remain compatible.

#### 具体テストケース一覧
- `tc-s02-001` acceptance: `epic -> epic` add writes source epic direct ref
  - 前提: temp repo has two epics with child issues。
  - 操作: `deps add --from epic-a --to epic-b`。
  - 期待結果: stdout has `result=updated`; source epic `.meta.json.depends_on` contains `epic-b`。
  - 失敗検出: non-issue endpoints still return `unsupported_node_kind`。
  - 検証方法: `tests/cli_runtime/test_deps.py`。
  - 関連 closure id: `slci-ac-001`
- `tc-s02-002` acceptance: node-level remove deletes matching direct raw ref
  - 前提: source initiative or epic `.meta.json.depends_on` directly contains target node id。
  - 操作: `deps remove --from <node> --to <node>`。
  - 期待結果: stdout has `result=updated`; matching direct ref is removed。
  - 失敗検出: remove path remains issue-only。
  - 検証方法: `tests/cli_runtime/test_deps.py`。
  - 関連 closure id: `slci-ac-002`
- `tc-s02-003` acceptance: empty container dependency is stored when raw graph is valid
  - 前提: source or target epic/initiative has no child issue。
  - 操作: valid `deps add`。
  - 期待結果: source `.meta.json.depends_on` stores target node id; empty expansion is not a write failure。
  - 失敗検出: implementation rejects empty source/target because compiled issue expansion is empty。
  - 検証方法: CLI runtime test。
  - 関連 closure id: `slci-ac-005`
- `tc-s02-004` negative: invalid candidate rejects before write through CLI
  - 前提: fixtures cover self, ancestor/container, descendant, and raw cycle candidates。
  - 操作: run `deps add` for each invalid edge。
  - 期待結果: command fails before write; `.meta.json` remains unchanged。
  - 失敗検出: S01 helper is not used by mutation path。
  - 検証方法: CLI runtime tests。
  - 関連 closure id: `slci-ac-006`, `slci-ac-007`, `slci-ec-001`, `slci-ec-002`, `slci-ec-003`, `slci-ec-004`

#### ステップ完了契約（step closure contract）
- closure id:
  - slci-ac-001, slci-ac-002, slci-ac-005, slci-ac-006, slci-ac-007, slci-ec-001, slci-ec-002, slci-ec-003, slci-ec-004
- close 条件:
  - Node-level add/remove and invalid candidate no-write behavior pass through public CLI tests.
- 検証 evidence:
  - Focused CLI pytest and S01 unit pytest.
- report evidence:
  - Step Contract Closure, Test Contract Closure, Closure Coverage.
- 残リスク:
  - Duplicate/direct matching regressions remain S03 responsibility.

#### ステップゲート（step gate）
- step reviewer gate:
  - reviewer: `code-reviewer`
  - review 範囲: node-level mutation orchestration and S01 validation integration.
  - pass 条件: `review_status: pass`
- commit / no-op gate:
  - closure 状態: committed
  - commit 範囲: S02 public integration.

### 実装ステップ S03 — direct-edge semantics and issue regression
- 振る舞いの目標（behavior goal）:
  - Duplicate add、inherited-only remove、raw shorthand matching、existing issue->issue add/remove を direct-edge semantics として固定する。
- design 参照:
  - `design.md`「シーケンス差分」「テスト戦略」。
- 依存:
  - S02。
- unblock:
  - S04, S90。
- 対象ファイル:
  - `tests/cli_runtime/test_deps.py`
  - 必要時 S02 touched runtime files の minimal repair。
- 計画済み契約（planned contract）:
  - scope:
    - Direct matching, duplicate/no-op, inherited-only remove, shorthand raw ref matching, issue->issue regression.
  - テスト義務（test obligation）:
    - closure id:
      - slci-ac-003, slci-ac-004, slci-ac-008, slci-ec-005
    - coverage rationale:
      - These cases prevent compiled/inherited edges from being confused with source direct metadata.
  - Red / 代替証跡の要件:
    - red-required:
      - Existing or new CLI tests fail if direct matching semantics are wrong.
  - 実装範囲（implementation scope）:
    - allowed paths:
      - S03 target files.
    - forbidden changes:
      - Docs/help, unrelated delete/sync redesign, public output shape changes not required by AC.
  - Green 検証:
    - `uv run pytest tests/cli_runtime/test_deps.py -k "deps_add or deps_remove"`
  - Refactor / cleanup ガードレール:
    - No broad fixture rewrite; keep issue-named wrappers as compatibility aliases if existing code still calls them.
  - report 証跡の記録先:
    - Delegated Worker Evidence, TDD Evidence, Reviewer Gate Status, Step Commit Gate.
  - amendment trigger:
    - Direct removal requires storage grammar or output contract change.

#### 委任契約（delegation contract）
- 委任ロール（delegated role）:
  - `dev-coder`
- 入力 docs:
  - `requirement.md`, `design.md`, `plan.md`, S01/S02 evidence, `tests/cli_runtime/test_deps.py`, S02 touched runtime files.
- 許可 paths:
  - S03 target files.
- 禁止 changes:
  - Docs/help, canonical specs/report, unrelated commands, GitHub state.
- 受け入れ条件:
  - Duplicate direct add, inherited-only remove, raw shorthand matching, and issue->issue regressions pass.
- 必須 tests または docs-only verification:
  - Focused CLI runtime command.
- reviewer focus:
  - Direct-vs-inherited semantics, raw ref matching, no duplicated storage, issue->issue compatibility.
- 必須出力（output required）:
  - changed files, tests run, worker summary, unresolved risks, ledger note for public error-code decisions.
- 停止条件（stop conditions）:
  - Public output format or storage grammar change is needed.

#### 具体テストケース一覧
- `tc-s03-001` acceptance: duplicate node-level add is unchanged without duplicate storage
  - 前提: source epic direct ref already resolves to target epic through node id or shorthand。
  - 操作: add the same edge by node id。
  - 期待結果: `result=unchanged`; post-sync skipped; storage still has one logical direct ref。
  - 失敗検出: duplicate append or compiled/inherited edge treated as direct。
  - 検証方法: CLI runtime test。
  - 関連 closure id: `slci-ac-003`, `slci-ec-005`
- `tc-s03-002` acceptance: inherited-only remove remains `edge_not_found`
  - 前提: parent-level dependency compiles to an issue edge, but source node has no direct ref。
  - 操作: remove the compiled/inherited edge from the child source。
  - 期待結果: stderr has `code=edge_not_found`; no-write。
  - 失敗検出: compiled edge is mistaken for direct metadata。
  - 検証方法: CLI runtime test。
  - 関連 closure id: `slci-ac-004`
- `tc-s03-003` acceptance: shorthand direct ref remove resolves to node target
  - 前提: source node direct ref is `123`, `"123"`, `owner/repo#123`, or canonical URL。
  - 操作: remove by node id。
  - 期待結果: matching raw ref is removed。
  - 失敗検出: remove only compares stringified target id。
  - 検証方法: CLI runtime parameterized test。
  - 関連 closure id: `slci-ec-005`
- `tc-s03-004` regression: existing issue->issue direct dependency behavior stays compatible
  - 前提: existing issue->issue add/remove fixtures and tests exist in `tests/cli_runtime/test_deps.py`。
  - 操作: run the existing issue->issue add, duplicate add, remove, and remove not-found scenarios。
  - 期待結果: existing `result=updated|unchanged`, skipped post-sync on unchanged, and `edge_not_found` semantics are preserved。
  - 失敗検出: node-level generalization changes issue-level output or direct matching。
  - 検証方法: focused CLI runtime tests, with concrete existing test names recorded in `report.md` during execution。
  - 関連 closure id: `slci-ac-008`

#### ステップ完了契約（step closure contract）
- closure id:
  - slci-ac-003, slci-ac-004, slci-ac-008, slci-ec-005
- close 条件:
  - Direct-edge semantics and issue->issue regressions pass under focused CLI runtime tests.
- 検証 evidence:
  - Focused pytest command.
- report evidence:
  - Step Contract Closure, Test Contract Closure, Closure Coverage.
- 残リスク:
  - Full deps lane remains S04 responsibility.

#### ステップゲート（step gate）
- step reviewer gate:
  - reviewer: `code-reviewer`
  - review 範囲: direct matching and issue regression.
  - pass 条件: `review_status: pass`
- commit / no-op gate:
  - closure 状態: committed
  - commit 範囲: S03 behavior slice.

### 実装ステップ S04 — regression consolidation and no-write/post-sync guardrails
- 振る舞いの目標（behavior goal）:
  - Existing issue->issue behavior、preflight-first、write failure no-write、post-sync update/skip を issue-wide regression として固定する。
- design 参照:
  - `design.md`「テスト戦略」。
- 依存:
  - S03。
- unblock:
  - S90。
- 対象ファイル:
  - `tests/cli_runtime/test_deps.py`
  - 必要時 S03 touched runtime files の minimal repair。
- 計画済み契約（planned contract）:
  - scope:
    - Regression tests and minimal repair only.
  - テスト義務（test obligation）:
    - closure id:
      - slci-ac-008, slci-ec-006
    - coverage rationale:
      - Node-level generalization must not weaken existing issue-level contracts.
  - Red / 代替証跡の要件:
    - covered-existing:
      - Existing issue->issue add/remove, write failure, preflight-first, post-sync tests.
    - red-required:
      - Add regression rows only for gaps discovered after S03.
  - 実装範囲（implementation scope）:
    - allowed paths:
      - Target files above.
    - forbidden changes:
      - Docs/help, unrelated command suites, GitHub state.
  - Green 検証:
    - `uv run pytest tests/cli_runtime/test_deps.py`
  - Refactor / cleanup ガードレール:
    - No broad fixture rewrite.
  - report 証跡の記録先:
    - Test Contract Closure, Closure Coverage, Step Commit Gate.
  - amendment trigger:
    - Regression repair requires public CLI response or requirement/design change.

#### 委任契約（delegation contract）
- 委任ロール（delegated role）:
  - `dev-coder`
- 入力 docs:
  - requirement/design/plan, S03 diff/evidence, current test failures.
- 許可 paths:
  - `tests/cli_runtime/test_deps.py` and already-touched runtime mutation files for minimal repair.
- 禁止 changes:
  - Docs/help, canonical specs/report, unrelated command suites, GitHub state.
- 受け入れ条件:
  - AC-008 and EC-006 remain locked; all add/remove failure paths are no-write.
- 必須 tests または docs-only verification:
  - `uv run pytest tests/cli_runtime/test_deps.py`
- reviewer focus:
  - Regression completeness, no-write assertions, no behavior drift.
- 必須出力（output required）:
  - test summary, repair summary if any, unresolved risks, no material decision note.
- 停止条件（stop conditions）:
  - Broad failures outside deps suite; public output format change needed; flaky external GitHub dependency appears.

#### 具体テストケース一覧
- `tc-s04-001` regression: existing issue->issue add/remove output stays unchanged
  - 前提: existing two-issue fixture。
  - 操作: add, duplicate add, remove, remove not-found。
  - 期待結果: existing `result=updated|unchanged`, skipped post-sync on unchanged, `edge_not_found` on not-found。
  - 失敗検出: node-level generalization changes issue output or post-sync。
  - 検証方法: existing and adjusted CLI tests。
  - 関連 closure id: `slci-ac-008`
- `tc-s04-002` no-write: write failure preserves before content
  - 前提: source meta path or directory is made unwritable as existing POSIX test does。
  - 操作: remove or add direct edge。
  - 期待結果: `code=write_failed`; `.meta.json` content unchanged。
  - 失敗検出: partial write or permission handling regression。
  - 検証方法: existing POSIX write failure test extended only if needed。
  - 関連 closure id: `slci-ac-008`
- `tc-s04-003` preflight-first: broken current graph blocks semantic outcomes
  - 前提: current dependency graph is already invalid before the requested add/remove。
  - 操作: run duplicate add, remove missing edge, or another semantic branch that would otherwise return unchanged/not-found。
  - 期待結果: command returns `preflight_validate_failed`; duplicate/no-op and `edge_not_found` are not reached。
  - 失敗検出: mutation checks requested edge semantics before validating current graph。
  - 検証方法: existing `test_deps.py` preflight-before-duplicate/not-found tests or added focused regression。
  - 関連 closure id: `slci-ec-006`
- `tc-s04-004` post-sync guardrail: updated and unchanged mutation keep existing sync behavior
  - 前提: existing auto-sync fixture covers updated and unchanged dependency mutation outcomes。
  - 操作: run successful add/remove and duplicate add。
  - 期待結果: updated mutation runs post-sync; unchanged duplicate add reports skipped post-sync reason `unchanged`。
  - 失敗検出: node-level changes accidentally skip required sync or run sync for unchanged no-op。
  - 検証方法: existing or adjusted CLI runtime post-sync assertions。
  - 関連 closure id: `slci-ac-008`

#### ステップ完了契約（step closure contract）
- closure id:
  - slci-ac-008, slci-ec-006
- close 条件:
  - Full deps CLI runtime lane passes or unrelated failures are classified with evidence.
- 検証 evidence:
  - `uv run pytest tests/cli_runtime/test_deps.py`
- report evidence:
  - Test Contract Closure, Closure Coverage, Step Commit Gate.
- 残リスク:
  - Docs/help alignment remains S90.

#### ステップゲート（step gate）
- step reviewer gate:
  - reviewer: `code-reviewer`
  - review 範囲: regression coverage and no-write behavior.
  - pass 条件: `review_status: pass`
- commit / no-op gate:
  - closure 状態: committed / approved-no-op if all existing coverage already suffices.
  - commit 範囲: S04 tests/minimal repair.

### ドキュメント影響の解消ステップ S90（docs impact resolution / docs refresh）
- 対象:
  - CLI help, provider docs, workflow docs, dogfooding mirror inspection/refresh, necessary snapshot tests.
- 対応:
  - `deps add/remove --from/--to` wording を issue-only から node-level に更新する。
  - Direct-edge remove、duplicate unchanged、empty-container behavior、raw validation boundary を docs に反映する。
- doc update owner:
  - `doc-writer`
- spec/doc review:
  - reviewer: `spec-reviewer`
  - pass 条件: docs/help が requirement / design / runtime behavior と整合する。
- 対象ファイル:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/deps.py`
  - `src/spec_dock/assets/spec_dock/docs/reference_deps.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
  - `spec-dock/docs/reference_deps.md`
  - `spec-dock/docs/workflow_issue.md`
  - Required snapshot/scaffold tests if changed text is asserted.
- delegation contract:
  - delegated role: `doc-writer`
  - input docs: requirement/design/plan, accepted runtime evidence, provider docs, workflow docs, `commands/deps.py`
  - allowed paths: files listed above and necessary snapshot tests
  - forbidden changes: runtime behavior beyond help text, canonical specs/report, agent instructions, GitHub state, unrelated docs
  - acceptance criteria: AC-009 covered
  - required verification: docs diff inspection, CLI help output or relevant tests, dogfooding mirror handling evidence
  - reviewer focus: docs/spec alignment; code-reviewer only for nontrivial parser/test changes
  - stop conditions: docs reveal runtime/spec mismatch, mirror refresh would overwrite unrelated dogfooding data, snapshot change exceeds docs scope
  - output required: docs changed, inspection commands, mirror handling, unresolved risks
- 具体テストケース一覧:
  - `tc-s90-001` docs: `workflow_issue.md` no longer documents issue-only add/remove
    - 前提: provider-side workflow docs contain dependency command examples。
    - 操作: inspect updated text。
    - 期待結果: examples use `<node-id>` or explicitly mention initiative / epic / issue。
    - 失敗検出: docs still instruct issue-only mutation。
    - 検証方法: docs diff inspection。
    - 関連 closure id: `slci-ac-009`
  - `tc-s90-002` help: add/remove help says node id
    - 前提: CLI help text is rendered from `commands/deps.py`。
    - 操作: inspect `deps add --help` / `deps remove --help` or targeted parser/help test。
    - 期待結果: `--from` and `--to` help mention initiative / epic / issue node ids。
    - 失敗検出: user-facing CLI still says issue-only。
    - 検証方法: command output or test assertion。
    - 関連 closure id: `slci-ac-009`
- step closure contract:
  - closure id: `slci-ac-009`
  - close 条件: docs/help and provider/dogfooding mirror handling are recorded, with spec-reviewer docs/spec alignment pass.
  - report evidence: Docs impact, Reviewer Gate Status, Step Commit Gate.

### 最終品質ゲートステップ S99（final quality gate）
- branch diff 範囲:
  - S01..S04, S90 committed / approved-no-op changes.
- 必須 validation:
  - `uv run pytest tests/cli_runtime/test_deps.py`
  - If helper/protocol changes affect unit surfaces, run targeted unit tests or `uv run pytest tests/unit`.
  - `./spec-dock/scripts/spec-dock validate`
- final QA gate:
  - reviewer: `qa-reviewer`
  - 範囲: SLCI coverage, missing high-value tests, manual/integration test necessity
  - pass 条件: `review_status: pass`
- final code review ゲート:
  - reviewer: issue-wide `code-reviewer`
  - 範囲: integrated diff, layering, regression risk, maintainability
  - pass 条件: `review_status: pass`
- final spec review ゲート:
  - reviewer: final `spec-reviewer`
  - 範囲: requirement / design / plan / report / docs / implementation evidence alignment
  - pass 条件: `review_status: pass`
- final commit gate:
  - commit 範囲: S99 report evidence / final adjustments only
  - final report ledger:
    - all closure rows have evidence
  - post-commit external evidence destination:
    - `report.md`
- 具体検証ケース:
  - `tc-s99-001` final test lane
    - 前提: all step commits complete。
    - 操作: run `uv run pytest tests/cli_runtime/test_deps.py`。
    - 期待結果: pass, or unrelated failure classified with evidence and accepted handling。
    - 失敗検出: integration regression not caught by step-local tests。
    - 検証方法: command output in `report.md`。
  - `tc-s99-002` closure coverage review
    - 前提: report has Step Contract Closure, Test Contract Closure, Closure Coverage, reviewer gate status。
    - 操作: compare every SLCI row to evidence。
    - 期待結果: no required closure is missing; any closure delta has re-review evidence。
    - 失敗検出: AC/EC marked done without test/report evidence。
    - 検証方法: QA/spec review。
- step closure contract:
  - closure id: all SLCI rows
  - close 条件: final QA/code/spec reviewer gates pass after S90; no unresolved blockers
  - report evidence: Final QA Gate, Final Code Review Gate, Final Spec Review Gate, Closure Coverage, Final Commit evidence

## 未確定事項
- なし。
- 実装中に public error code names を新規固定する必要が出た場合は、report decision と plan/design amendment 要否を判断する。

## 最終完了条件
- AC/EC 達成:
  - SLCI rows all pass / approved-no-op with evidence.
- docs 影響解決:
  - S90 complete and spec-reviewed.
- 全 implementation step 完了:
  - S01..S04, S90 committed / approved-no-op.
- final quality gate pass:
  - qa-reviewer: pass
  - issue-wide code-reviewer: pass
  - spec-reviewer: pass
- final commit 完了:
  - Step commit gate evidence recorded in `report.md`.
- 必須 closure id 完了:
  - Step Contract Closure, Test Contract Closure, Closure Coverage complete.
- final clean state:
  - no unintended staged / unstaged changes.

## 委任ドラフト採用
- 採用元:
  - `discussions/20260617t-plan-node-level-dependency-mutation.md`
- 採用内容:
  - S01/S02/S03/S04/S90/S99 step boundaries。
  - Spec-Locked Closure Index。
  - Per-step delegation contracts and concrete test seeds。
  - Docs impact and final quality gate。
- 採用しなかった内容:
  - Draft の narrative は canonical plan では実行契約へ圧縮した。
  - Helper-level unit tests は mandatory ではなく、実装形状に応じた conditional verification として残した。
