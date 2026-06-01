---
種別: 実装計画書（Issue）
ID: "iss-00149"
タイトル: "Issue finish synthetic approval closeout bug"
関連GitHub: ["#149"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-01"
依存: ["requirement.md", "design.md"]
親: ["epic-00080", "init-00079"]
---

# iss-00149 Issue finish synthetic approval closeout bug — 実装計画（Execution Contract）

## この計画で満たす要件ID
- AC: AC-001, AC-002, AC-003, AC-004
- EC: EC-001, EC-002, EC-003, EC-004
- 制約:
  - `runtime_active_selection` は lifecycle approval ではない。
  - `issue_finish_lifecycle_transition` は `issue_finish` 限定。
  - provider runtime と dogfooding mirror を一致させる。
  - `issue finish` を PR delivery / review / test / merge readiness の代替にしない。

## 依存関係から導く実装順序
- S01 Domain Authority Contract:
  - 依存: approved requirement / design。
  - unblock: S02 application flow。
  - 対象ファイル: provider `domain/authority.py`, `tests/domain_runtime/test_authority.py`。
- S02 Application Issue Finish Transition Flow:
  - 依存: S01 の token / grants / gate contract。
  - unblock: S03 mirror parity, S90 docs impact。
  - 対象ファイル: provider `application/issue_lifecycle.py`, 必要最小の active helper, `tests/cli_runtime/test_issue_lifecycle.py`。
- S03 Provider / Dogfooding Mirror Parity:
  - 依存: S01 / S02 runtime diff。
  - unblock: S90 / S99。
  - 対象ファイル: `spec-dock/scripts/spec_dock_runtime/...` mirror。
- S90 Docs Impact Resolution:
  - 依存: S02 / S03 の確定挙動。
  - unblock: S99 final spec review。
  - 対象ファイル: provider `src/spec_dock/assets/spec_dock/docs/workflow_issue.md` and dogfooding mirror `spec-dock/docs/workflow_issue.md`。
- S99 Final Quality Gate:
  - 依存: S01-S03 / S90 完了または approved no-op。
  - 対象: issue-wide diff, report closure, final reviewer gates。

## ステップ一覧
- S01:
  - 観測可能な振る舞い: domain authority が synthetic rejection と finish-only transition token を同時に保証する。
  - 閉じる要件: AC-003, EC-002, constraints。
  - レビューゲート: code-reviewer。
- S02:
  - 観測可能な振る舞い: synthetic active issue から `issue finish` が local gates 後に transition を永続化し、close / clear / post-sync へ進む。
  - 閉じる要件: AC-001, AC-002, EC-001, EC-002, EC-003, EC-004。
  - レビューゲート: code-reviewer。
- S03:
  - 観測可能な振る舞い: provider runtime と dogfooding mirror / runtime guidance が一致する。
  - 閉じる要件: AC-004。
  - レビューゲート: code-reviewer。
- S90:
  - 観測可能な振る舞い: workflow docs が finish-only internal transition と lifecycle-only boundary を正しく説明する。
  - 閉じる要件: AC-004。
  - レビューゲート: spec-reviewer。
- S99:
  - 観測可能な振る舞い: closure ledger、validation、QA/code/spec final gates が issue-wide に pass する。
  - 閉じる要件: 全 AC / EC / constraints。
  - レビューゲート: qa-reviewer, code-reviewer, spec-reviewer。

## 要件 ↔ ステップ対応
- AC-001 -> S02, S03, S99
- AC-002 -> S02, S99
- AC-003 -> S01, S02, S99
- AC-004 -> S03, S90, S99
- EC-001 -> S02
- EC-002 -> S01, S02
- EC-003 -> S02
- EC-004 -> S02

## 仕様固定クロージャ索引（Spec-Locked Closure Index）

| ID | Step | Slice | Type | Spec link | Locked expectation | Observable input / state | Bug class guarded | Required | Evidence level | Closure evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| tc-001 | S01 | synthetic invariant | constraint | AC-003 | `runtime_active_selection` fails for downstream lifecycle grants | `evaluate_authority_gate()` with runtime promotion record | unsafe synthetic lifecycle approval | yes | red-required | domain test closure |
| tc-002 | S01 | finish transition helper | acceptance / constraint | AC-001, AC-003 | helper builds `issue_finish_lifecycle_transition` bound to `active:<issue-id>` with input grants plus `issue_finish` only | helper output | broad grants after transition | yes | red-required | domain helper tests |
| tc-003 | S01 | finish-only token gate | constraint | AC-003 | finish token passes only `required_grant=issue_finish` | gate call with finish token | token accepted too broadly | yes | red-required | domain authority tests |
| tc-004 | S01/S02 | active binding | edge / negative | EC-002 | stale revision/hash/different active id fail closed | mismatched active entry and promotion record | closing wrong issue | yes | red-required | domain and lifecycle tests |
| tc-005 | S02 | normal closeout | acceptance | AC-001 | synthetic active issue closes OPEN GitHub issue, clears active, post-syncs | temp repo after `issue start` / `active set` | original closeout block | yes | red-required | CLI runtime test |
| tc-006 | S02 | already closed closeout | edge | EC-001 | already CLOSED issue uses same transition and clears active | GitHub issue state `CLOSED` | already-closed active stuck | yes | red-required | CLI runtime test |
| tc-007 | S02 | EAL precondition failure | negative | AC-002, EC-003 | blocked / stale EAL prevents transition persistence and close | report ledger with blocking EAL | auto-promoting blocked evidence | yes | red-required | lifecycle tests |
| tc-007b | S02 | delegated artifact precondition failure | negative | AC-002, EC-004 | proposed / missing delegated metadata prevents transition persistence and close | delegated design/plan artifact with proposed/missing metadata | auto-promoting unapproved delegated artifact | yes | red-required | lifecycle tests |
| tc-008 | S02 | stale synthetic record | negative | EC-002 | stale synthetic record fails before transition and close | active id differs from promotion record | stale active close | yes | red-required | lifecycle test |
| tc-009 | S02 | transition persistence failure | negative | design retry semantics | active store failure restores previous state and avoids GitHub mutation | failing active store | partial local write plus external mutation | yes | red-required | application test |
| tc-010 | S02 | close failure retry | negative / retry | AC-002 | close failure after transition leaves finish-ready active state and retry guidance | failing gh stub after transition | retry trap | yes | red-required | CLI runtime test |
| tc-011 | S02 | clear failure recovery | regression | existing finish contract | close succeeds, clear failure skips post-sync and reports recovery | clear failure fake | false success / stale derived artifacts | yes | covered-existing | existing test update if needed |
| tc-012 | S02 | post-sync ownership | regression | AC-001 | `close_node(run_post_sync=False)`, lifecycle post-sync runs once after clear | finish success path | double sync | yes | covered-existing | existing tests |
| tc-013 | S03/S90 | provider / mirror / guidance parity | acceptance / docs | AC-004 | every S01/S02-changed provider runtime file matches its dogfooding mirror; CLI/context-pack guidance and workflow docs agree | dynamic `cmp` list, docs diff, stderr/context-pack inspection | shipped / dogfooding divergence | yes | inspect-only | parity and spec-review evidence |
| tc-014 | S99 | issue-wide closure | final gate | workflow_issue | all required closure ids and reviewer gates are recorded and pass | final diff and report ledger | local pass with issue-wide gap | yes | manual-required | final gate evidence |
| tc-015 | S99 | PR delivery and merge preparation | lifecycle delivery gate | workflow_issue PR Delivery Gate / Merge Preparation Gate | PR URL/base/head/linkage and merge-prepared monitoring evidence are recorded before `issue finish` | PR snapshot, checks/reviews/merge blocker status, report gate entries | issue reported complete without mandatory PR lifecycle evidence | yes | manual-required | PR Delivery Gate and Merge Preparation Gate report evidence |

## レビュー / QA ゲート方針
- Step review:
  - S01-S03: code-reviewer pass。
  - S90: spec-reviewer pass when docs changed; no-op の場合も S99 final spec-reviewer で確認。
- Final QA:
  - qa-reviewer が obligation coverage、missing high-value tests、manual / integration test 要否を確認する。
- Final code review:
  - code-reviewer が issue-wide integrated diff、layering、retry / rollback / failure order、mirror parity を確認する。
- Final spec review:
  - spec-reviewer が requirement / design / plan / report / implementation / tests / docs alignment を確認する。

## report 証跡 destination 共通表

| Step | Red / 代替証跡 destination | Green / 検証 destination | Refactor / cleanup destination | Closure destination | Reviewer / commit destination |
|---|---|---|---|---|---|
| S01 | `report.md` TDD Evidence: S01 Red / alternative | `report.md` TDD Evidence: S01 Green | `report.md` TDD Evidence: S01 Refactor | Step Contract Closure, Test Contract Closure, Closure Coverage | Implementation Delegation Gate, Delegated Worker Evidence, Reviewer Gate Status, Step Commit Gate |
| S02 | `report.md` TDD Evidence: S02 Red / alternative | `report.md` TDD Evidence: S02 Green | `report.md` TDD Evidence: S02 Refactor | Step Contract Closure, Test Contract Closure, Closure Coverage, Closure Delta when aliases/added cases occur | Implementation Delegation Gate, Delegated Worker Evidence, Reviewer Gate Status, Step Commit Gate |
| S03 | `report.md` TDD Evidence: S03 inspect-only / alternative | `report.md` TDD Evidence: S03 Green / parity inspection | `report.md` TDD Evidence: S03 Refactor / approved-no-op | Step Contract Closure, Test Contract Closure, Closure Coverage | Implementation Delegation Gate, Delegated Worker Evidence, Reviewer Gate Status, Step Commit Gate |
| S90 | `report.md` Docs Impact Resolution and TDD Evidence: S90 inspect-only | `report.md` Docs Impact Resolution and Reviewer Gate Status | `report.md` Docs Impact Resolution approved-no-op / docs diff guard | Step Contract Closure, Test Contract Closure, Closure Coverage | Reviewer Gate Status, Step Commit Gate |
| S99 | `report.md` Final QA Gate / Final Code Review Gate / Final Spec Review Gate | `report.md` final validation command log and closure ledgers | Closure Delta if final review adds or aliases closure rows | Final Quality Gate, Closure Coverage, Closure Delta | Final QA Gate, Final Code Review Gate, Final Spec Review Gate, Step Commit Gate |

## 実装ステップ

### 実装ステップ S01 — Domain Authority Contract
- 振る舞いの目標:
  - `issue_finish_lifecycle_transition` の finish-only domain contract を追加し、synthetic approval rejection を維持する。
- design 参照:
  - `design.md` の「インターフェース契約」「ドメインモデル差分」「テスト戦略」。
- 対象ファイル:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authority.py`
  - `tests/domain_runtime/test_authority.py`
- 計画済み契約:
  - scope:
    - finish transition promotion record helper / grants helper を追加する。
    - `evaluate_authority_gate()` に finish token restriction を追加する。
  - テスト義務:
    - closure id: tc-001, tc-002, tc-003, tc-004。
    - coverage rationale: domain invariant と stale binding は application flow の前提であり、ここが緩むと安全境界全体が崩れる。
  - Red / 代替証跡:
    - red-required: 新 token / grants helper と finish-only gate tests。
    - covered-existing: 既存 stale hash / revision tests は維持し、finish token case を追加する。
  - Green 検証:
    - `python -m unittest tests.domain_runtime.test_authority -v`
  - Refactor / cleanup ガードレール:
    - 目的: token 判定を読みやすく保つ。
    - 禁止: authority model 全体の列挙再設計、public schema 追加、wildcard grant 導入。
  - report 証跡の記録先:
    - TDD evidence, Step Contract Closure, Test Contract Closure, Closure Coverage, Reviewer Gate Status, Step Commit Gate。
  - amendment trigger:
    - token が `issue_finish` 以外を authorize する必要が出た場合。
    - `runtime_active_selection` の lifecycle rejection を維持できない場合。

#### 委任契約（delegation contract）
- 委任ロール: dev-coder
- 入力 docs:
  - `requirement.md`, `design.md`, `plan.md`, `workflow_issue.md`, provider `authority.py`, `tests/domain_runtime/test_authority.py`
- 許可 paths:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authority.py`
  - `tests/domain_runtime/test_authority.py`
- 禁止 changes:
  - `issue_lifecycle.py`、CLI parser、docs、mirror copy、active state、unrelated refactor。
- 受け入れ条件:
  - tc-001 から tc-004 が pass。
- 必須 tests:
  - `python -m unittest tests.domain_runtime.test_authority -v`
- reviewer focus:
  - synthetic rejection、exact grants、finish-only token、stale record behavior。
- 必須出力:
  - changed files、test result、closed closure ids、unresolved risks、Ledger Note。
- 停止条件:
  - approved requirement/design を変える必要、new command 必要、synthetic approval relaxation 必要。

#### 具体テストケース一覧
- `tc-s01-001` negative: synthetic approval remains non-lifecycle
  - 前提: `approved_runtime_promotion_record(node_id="iss-00101")` は `promotion_decision=runtime_active_selection`。
  - 操作: `evaluate_authority_gate()` を `implementation_start`, `issue_ready`, `issue_finish`, `phase_completion` で呼ぶ。
  - 期待結果: すべて `ok=False`, reason `active_synthetic_approval_not_lifecycle_approval`。
  - 失敗検出: synthetic active selection が lifecycle approval になる回帰を検出する。
  - 検証方法: `tests/domain_runtime/test_authority.py` の red-first / regression test。
  - 関連 closure id: tc-001
- `tc-s01-002` acceptance: finish transition helper output is restricted and bound
  - 前提: helper を `node_id="iss-00101"` で呼ぶ。
  - 操作: promotion record と grants を検査する。
  - 期待結果: decision は `issue_finish_lifecycle_transition`; revision/hash は `active:iss-00101`; grants は `review_input`, `planning_input`, `design_baseline`, `issue_finish` のみ。
  - 失敗検出: unrelated lifecycle を authorize できる helper output を検出する。
  - 検証方法: new domain helper test。
  - 関連 closure id: tc-002
- `tc-s01-003` acceptance / negative: finish transition token is finish-only
  - 前提: approved authority、finish transition grants、finish transition promotion record。
  - 操作: `required_grant=issue_finish` と他 lifecycle grants を評価する。
  - 期待結果: `issue_finish` は pass、他 lifecycle grants は explicit restriction または missing grant で fail。
  - 失敗検出: token が `main_orchestrator_promotion` 相当になる回帰を検出する。
  - 検証方法: subTest loop in domain tests。
  - 関連 closure id: tc-003
- `tc-s01-004` negative: stale binding remains fail-closed with finish token
  - 前提: finish token record は `active:iss-00101`、expected revision は `active:iss-00999`。
  - 操作: expected_revision 付きで `issue_finish` gate を評価する。
  - 期待結果: `promotion_record_not_bound_to_active_entry` または `promotion_hash_not_bound_to_active_entry`。
  - 失敗検出: stale active issue を閉じる回帰を検出する。
  - 検証方法: expected-revision domain test extension。
  - 関連 closure id: tc-004

#### ステップ完了契約
- close 条件:
  - S01 tests pass、既存 domain authority tests pass、code-reviewer pass。
- commit / no-op gate:
  - S01 allowed paths のみ commit。no-op は同契約が既に満たされる場合だけ。

### 実装ステップ S02 — Application Issue Finish Transition Flow
- 振る舞いの目標:
  - `issue_finish()` が local preconditions 後、GitHub close 前に finish transition を永続化し、既存 `issue_finish` gate を再利用する。
- 対象ファイル:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_lifecycle.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/set_active.py` only if helper reuse/extraction is necessary
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/active_store.py` only if existing API is insufficient
  - `tests/cli_runtime/test_issue_lifecycle.py`
- 計画済み契約:
  - scope:
    - bound synthetic active issue を検出する。
    - delegated artifact / EAL preconditions を transition persistence 前に評価する。
    - issue entry だけを finish transition record / grants へ差し替える。
    - active store snapshot / rollback path で永続化する。
    - persistence 後に既存 authority gate、close、clear、post-sync の順に進む。
  - テスト義務:
    - closure id: tc-005 から tc-012（tc-007b を含む）。
  - Green 検証:
    - `python -m unittest tests.cli_runtime.test_issue_lifecycle -v`
    - `python -m unittest tests.domain_runtime.test_authority tests.cli_runtime.test_issue_lifecycle -v`
  - Red / 代替証跡:
    - red-required: tc-s02-001, tc-s02-001b, tc-s02-002, tc-s02-003a, tc-s02-003b, tc-s02-004, tc-s02-005, tc-s02-006。
    - covered-existing: tc-s02-007 and tc-s02-008 may remain covered-existing only if existing tests still assert clear failure and single post-sync after the transition path is introduced.
  - Refactor / cleanup ガードレール:
    - 目的: transition flow を readable helper へ閉じ、existing close / clear / post-sync flow の責務境界を保つ。
    - 禁止: broad lifecycle refactor、GitHub gateway rewrite、active store schema migration、S01 token semantics の再設計。
  - report 証跡の記録先:
    - `report.md` TDD Evidence、Step Contract Closure、Test Contract Closure、Closure Coverage、Closure Delta、Implementation Delegation Gate、Delegated Worker Evidence、Reviewer Gate Status、Step Commit Gate。
  - amendment trigger:
    - transition が local gates 前に必要になる。
    - existing active store で rollback-safe persistence が作れない。
    - `issue finish` が delivery completion を判定する必要が出る。

#### 委任契約（delegation contract）
- 委任ロール: dev-coder
- 入力 docs:
  - approved requirement/design/plan、S01 diff、`workflow_issue.md`、provider lifecycle / active store files、`tests/cli_runtime/test_issue_lifecycle.py`
- 許可 paths:
  - S02 対象ファイル。
- 禁止 changes:
  - domain token semantics の再変更、docs、CLI command shape、GitHub gateway broad changes、unrelated lifecycle commands。
- 受け入れ条件:
  - tc-005 から tc-012 が tests または covered-existing evidence で閉じる。
- 必須 tests:
  - targeted CLI/application lifecycle tests。
- reviewer focus:
  - call ordering、rollback semantics、retry behavior、no external mutation before local preconditions、no double post-sync。
- 必須出力:
  - changed files、test result、helper reuse/extraction decision、closed closure ids、Ledger Note。
- 停止条件:
  - public CLI contract 変更、finish-only を超える authority change、precondition ordering conflict。

#### 具体テストケース一覧
- `tc-s02-001` acceptance: `issue start` then `issue finish` closes OPEN issue
  - 前提: temp repo の linked issue #101 は `OPEN`。`issue start --id iss-00101` 後、active issue は synthetic。
  - 操作: `spec-dock issue finish`。
  - 期待結果: success、`active_cleared=true`、`already_closed=false`、gh close called、active issue cleared、post-sync updates issue status to done。
  - 失敗検出: original closeout block、active clear / sync missing。
  - 検証方法: CLI runtime test から manual `_promote_active_issue_lifecycle()` を除去して assertion 追加。
  - 関連 closure id: tc-005
- `tc-s02-001b` acceptance: `active set` then `issue finish` uses the same synthetic transition
  - 前提: temp repo の linked issue #101 は `OPEN`。`active set --id iss-00101 --force` 後、active issue は synthetic `runtime_active_selection`。
  - 操作: `spec-dock issue finish`。
  - 期待結果: `issue start` path と同じく internal transition 後に close / active clear / post-sync が成功する。active set と issue start が同じ active manifest builder を使う場合も、この観測点で shared path を証明する。
  - 失敗検出: `issue start` だけが special-case され、通常の `active set` synthetic selection が closeout できない回帰を検出する。
  - 検証方法: separate CLI runtime test or parameterized test with explicit `active set` setup。
  - 関連 closure id: tc-005
- `tc-s02-002` acceptance: already CLOSED issue clears active from synthetic state
  - 前提: synthetic active issue、gh stub issue #101 is `CLOSED`。
  - 操作: `spec-dock issue finish`。
  - 期待結果: `already_closed=true`、active cleared、issue pointer is active-none、post-sync runs once。
  - 失敗検出: already-closed state が synthetic approval で止まる回帰。
  - 検証方法: existing already-closed CLI test update。
  - 関連 closure id: tc-006
- `tc-s02-003a` negative: blocked or stale EAL prevents transition and close
  - 前提: synthetic active issue is bound; report has a blocking or stale Evidence Adoption Ledger entry。
  - 操作: `issue_finish()` with a report Evidence Adoption Ledger entry whose status is `blocked` or `stale`。
  - 期待結果: EAL guidance で fail、promotion decision remains `runtime_active_selection`、transition persistence / gh close / clear / post-sync not called。
  - 失敗検出: blocked local evidence を auto-promote する回帰。
  - 検証方法: existing EAL tests に store write / close / clear / post-sync call assertions を追加。
  - 関連 closure id: tc-007
- `tc-s02-003b` negative: proposed or missing delegated artifact metadata prevents transition and close
  - 前提: synthetic active issue is bound; delegated `design.md` または `plan.md` は proposed / missing approval metadata。
  - 操作: `issue_finish()`。
  - 期待結果: delegated artifact guidance で fail、promotion decision remains `runtime_active_selection`、transition persistence / gh close / clear / post-sync not called。
  - 失敗検出: unapproved delegated artifact を finish-ready state に昇格する回帰。
  - 検証方法: existing delegated artifact tests に store write / close / clear / post-sync call assertions を追加。
  - 関連 closure id: tc-007b
- `tc-s02-004` negative: stale active record is not transitioned
  - 前提: active issue id と synthetic promotion record の `active:<id>` が異なる。
  - 操作: `spec-dock issue finish`。
  - 期待結果: stale/binding reason で transition / close 前に fail、active unchanged。
  - 失敗検出: stale record を transition helper が上書きする回帰。
  - 検証方法: stale active case extension。
  - 関連 closure id: tc-008
- `tc-s02-005` negative: transition persistence failure rolls back
  - 前提: local gates pass; fake active store raises during write/pointer update after snapshot。
  - 操作: `issue_finish()` with fake close/clear/sync recorders。
  - 期待結果: previous active restored、close/clear/post-sync not called、error mentions active-state write/transition failure。
  - 失敗検出: partial local write plus external GitHub mutation。
  - 検証方法: application-level failing active store test。
  - 関連 closure id: tc-009
- `tc-s02-006` negative / retry: GitHub close failure leaves finish-ready active state
  - 前提: synthetic active passes local gates; transition persistence succeeds; gh view/close fails。
  - 操作: `spec-dock issue finish`。
  - 期待結果: command fails; active issue remains with `promotion_decision=issue_finish_lifecycle_transition`; active clear/post-sync not called; guidance says `active show` and retry `issue finish`, not manual `active.json` edit。
  - 失敗検出: close failure retry trap。
  - 検証方法: close failure CLI test extension。
  - 関連 closure id: tc-010
- `tc-s02-007` regression: clear failure recovery remains correct
  - 前提: close/already-closed succeeds; `clear_active` raises。
  - 操作: `issue_finish()` with fake clear failure。
  - 期待結果: close called once、post-sync not called、active-clear recovery guidance remains。
  - 失敗検出: false success or stale derived artifacts。
  - 検証方法: existing clear failure test。
  - 関連 closure id: tc-011
- `tc-s02-008` regression: lifecycle-owned post-sync runs once
  - 前提: close and clear succeed after transition。
  - 操作: `issue_finish()` with recorders。
  - 期待結果: `close_node` receives `run_post_sync=False`; post-sync called exactly once after clear。
  - 失敗検出: double sync or internal close sync leak。
  - 検証方法: existing post-sync test updated if needed。
  - 関連 closure id: tc-012

#### ステップ完了契約
- close 条件:
  - success / failure ordering が design sequence と一致、S02 tests pass、code-reviewer pass。
- commit / no-op gate:
  - S02 allowed paths のみ commit。no-op は all closure already satisfied の場合だけ。

### 実装ステップ S03 — Provider / Dogfooding Mirror Parity and Runtime Guidance
- 振る舞いの目標:
  - shipped provider runtime と dogfooding runtime mirror / runtime-facing guidance を一致させる。
- 対象ファイル:
  - dogfooding mirror for every provider runtime file changed by S01/S02 under `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/...`
  - expected current mirror candidates include `spec-dock/scripts/spec_dock_runtime/domain/authority.py`, `spec-dock/scripts/spec_dock_runtime/application/issue_lifecycle.py`, and, if touched by S02, `spec-dock/scripts/spec_dock_runtime/application/set_active.py` / `spec-dock/scripts/spec_dock_runtime/infra/active_store.py`
  - `spec-dock/docs/workflow_issue.md` inspection only if runtime mirror update exposes docs drift; S90 owns docs edits
  - runtime presentation files only if S02 error text requires it
  - `tests/cli_runtime/test_issue_lifecycle.py` only for output assertions tightly coupled to guidance
- 計画済み契約:
  - scope:
    - provider changes を mirror へ反映する。
    - changed runtime files の byte parity または approved intentional difference を確認する。
    - error guidance が direct `active.json` editing を標準 path にしないことを確認する。
  - Green 検証:
    - For every runtime provider file changed in S01/S02, run `cmp -s <provider-file> <dogfooding-mirror-file>` and record the pair. If an optional provider file was considered but not changed, record approved no-diff evidence for that file.
    - `python -m unittest tests.domain_runtime.test_authority tests.cli_runtime.test_issue_lifecycle -v`
  - Red / 代替証跡:
    - inspect-only: provider/mirror runtime file parity before and after mirror update, and output/guidance assertion inspection.
  - Refactor / cleanup ガードレール:
    - 目的: provider runtime changes を dogfooding mirror へ同一内容で反映する。
    - 禁止: docs parity check を S03 completion 条件にしない。workflow docs parity は S90 / S99 が所有する。
  - report 証跡の記録先:
    - `report.md` TDD Evidence inspect-only rows、Step Contract Closure、Test Contract Closure、Closure Coverage、Implementation Delegation Gate、Delegated Worker Evidence、Reviewer Gate Status、Step Commit Gate、Docs Impact Resolution handoff note。
  - amendment trigger:
    - provider/mirror が一致できない。
    - docs/guidance が approved design を超える workflow semantic change を要求する。

#### 委任契約（delegation contract）
- 委任ロール: dev-coder
- 入力 docs:
  - approved requirement/design/plan、S01/S02 diffs、provider and mirror runtime files。
- 許可 paths:
  - S03 対象ファイル。
- 禁止 changes:
  - canonical issue docs、workflow docs、unrelated generated assets、active state direct edits。
- 受け入れ条件:
  - tc-013 parity and guidance inspection pass。
- 必須 tests / inspection:
  - `cmp` parity checks、targeted tests、runtime guidance assertions/inspection。
- reviewer focus:
  - mirror parity、shipped asset behavior、no accidental divergence。
- 必須出力:
  - changed files、parity results、tests run、docs impact handoff、Ledger Note。
- 停止条件:
  - intentional divergence が design にない、または docs update が必要だが S90 に渡せない。

#### 具体テストケース一覧
- `tc-s03-001` inspect-only: provider and dogfooding runtime parity for every changed runtime file
  - 前提: S01/S02 changed provider runtime。
  - 操作: each changed provider runtime file under `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/...` と対応する mirror under `spec-dock/scripts/spec_dock_runtime/...` を compare。S02 optional files `set_active.py` / `active_store.py` が provider 側で変更された場合も必ず含める。
  - 期待結果: every changed pair is byte-identical or has approved intentional difference with report evidence。optional file が未変更なら approved no-diff evidence を残す。
  - 失敗検出: shipped / dogfooding behavior divergence。
  - 検証方法: dynamic `cmp -s` command list recorded in report。
  - 関連 closure id: tc-013
- `tc-s03-002` inspect-only / regression: operator guidance points to official retry path
  - 前提: S02 failure paths produce stderr guidance。
  - 操作: failing test assertions and runtime guidance text を inspect。
  - 期待結果: direct `active.json` editing を標準化しない。close failure after transition は `active show` and retry `issue finish`。
  - 失敗検出: guidance-only workaround への逆戻り。
  - 検証方法: CLI runtime assertions plus code inspection。
  - 関連 closure id: tc-013
- `tc-s03-003` inspect-only / regression: context-pack and active display do not imply full lifecycle approval
  - 前提: S02 transition and S03 mirror update may affect runtime guidance or generated context-pack output。
  - 操作: `spec-dock/active/context-pack.md` generation path or CLI assertions for context-pack / active display wording are inspected, and tests are added if S02 changes the output.
  - 期待結果: issue finish readiness may be shown for the transitioned issue, but ancestor synthetic downstream blocks or non-finish lifecycle purposes are not presented as full lifecycle approval。
  - 失敗検出: context-pack wording regression that makes synthetic ancestors appear lifecycle-approved。
  - 検証方法: output assertion when changed, otherwise inspect-only evidence recorded in report。
  - 関連 closure id: tc-013

#### ステップ完了契約
- close 条件:
  - provider/mirror parity verified、runtime guidance consistent、docs impact handed to S90。
- commit / no-op gate:
  - mirror/runtime guidance changes は S03 scope で commit。no-op は parity evidence 必須。

### ドキュメント影響の解消ステップ S90（Docs Impact Resolution）
- 振る舞いの目標:
  - workflow docs が finish-only internal transition と lifecycle-only boundary を正しく説明する。
- 対象:
  - provider source of truth: `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
  - dogfooding mirror: `spec-dock/docs/workflow_issue.md`
- 計画済み契約:
  - scope:
    - provider source of truth を先に更新し、dogfooding mirror へ同内容を反映または established scaffold refresh path で同期する。
    - `issue finish` が local gates 後に `issue_finish_lifecycle_transition` を内部永続化し得ることを説明する。
    - `issue finish` は PR delivery / tests / review / merge readiness を保証しないことを維持する。
    - fail-closed conditions と official recovery path を書く。
  - Green 検証:
    - docs diff inspection
    - `cmp -s src/spec_dock/assets/spec_dock/docs/workflow_issue.md spec-dock/docs/workflow_issue.md`
    - `./spec-dock/scripts/spec-dock validate`
    - spec-reviewer docs/spec alignment pass
  - Red / 代替証跡:
    - inspect-only: provider and mirror workflow docs are inspected before edit to identify stale guidance; no code test is required because S90 is docs-only.
  - Refactor / cleanup ガードレール:
    - 目的: minimum docs wording needed for runtime behavior and recovery path alignment。
    - 禁止: broad workflow rewrite、new command semantics、delivery-completion semantics の追加。
  - report 証跡の記録先:
    - `report.md` Docs Impact Resolution、TDD Evidence inspect-only row、Step Contract Closure、Test Contract Closure、Closure Coverage、Reviewer Gate Status、Step Commit Gate。
  - amendment trigger:
    - new command / new lifecycle phase が必要。
    - docs が approved requirement/design と矛盾する。

#### 委任契約（delegation contract）
- 委任ロール: doc-writer
- 入力 docs:
  - approved requirement/design/plan、S01-S03 observed behavior、provider and mirror `workflow_issue.md`。
- 許可 paths:
  - `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
  - `spec-dock/docs/workflow_issue.md`
- 禁止 changes:
  - runtime、tests、canonical issue docs、broad documentation restructuring。
- 受け入れ条件:
  - provider and mirror docs が primary `issue start` -> `issue finish` path、finish-only transition、fail-closed local gates、lifecycle-only boundary と一致する。
- 必須 verification:
  - docs diff inspection、`validate`、spec-reviewer pass。
- reviewer focus:
  - docs が requirement/design/plan と一致し、新 behavior を追加しない。
- 必須出力:
  - changed docs、validation result、reviewer result、Ledger Note。
- 停止条件:
  - docs change が behavior change になる。

#### 具体テストケース一覧
- `tc-s90-001` inspect-only: workflow primary path matches runtime transition
  - 前提: S02 implements finish-only internal transition。
  - 操作: provider `src/spec_dock/assets/spec_dock/docs/workflow_issue.md` と mirror `spec-dock/docs/workflow_issue.md` の lifecycle bullets around `issue start`, `issue finish`, authority gates, recovery, lifecycle-only boundary を inspect。
  - 期待結果: local gates precede transition、transition precedes close/clear、`issue finish` remains lifecycle-only。
  - 失敗検出: docs/runtime mismatch or delivery-completion claim。
  - 検証方法: docs diff inspection、provider/mirror `cmp -s`、spec-reviewer docs/spec alignment。
  - 関連 closure id: tc-013

#### ステップ完了契約
- close 条件:
  - docs impact resolved or approved no-op、spec-reviewer pass。
- commit / no-op gate:
  - docs-only changes commit。no-op は docs already match の report evidence 必須。

### 最終品質ゲートステップ S99（Final Quality Gate）
- 振る舞いの目標:
  - issue-wide obligation coverage、integration safety、docs consistency、report evidence を確定する。
- 計画済み契約:
  - scope:
    - required closure ids tc-001 through tc-015 を report closure ledgers で閉じる。
    - final validation bundle を実行する。
    - qa-reviewer、issue-wide code-reviewer、final spec-reviewer を pass まで回す。
    - PR Delivery Gate と Merge Preparation Gate を `issue finish` 前に通し、`report.md` に evidence を記録する。
  - Green 検証:
    - `python -m unittest tests.domain_runtime.test_authority tests.cli_runtime.test_issue_lifecycle -v`
    - `python -m unittest discover -v`
    - `./spec-dock/scripts/spec-dock validate`
    - `./spec-dock/scripts/spec-dock sync`
    - `git diff --check`
    - S03 provider/mirror parity checks。
    - S90 provider/mirror workflow docs parity check。
    - PR Delivery Gate evidence and Merge Preparation Gate evidence recorded in `report.md` before `issue finish`。
  - amendment trigger:
    - final reviewer が missing high-value tests / architecture regression / spec mismatch を指摘する。
    - validation が product change 起因で fail する。

#### 委任契約（delegation contract）
- 委任ロール:
  - qa-reviewer, code-reviewer, spec-reviewer。修正が必要な場合のみ bounded dev-coder / doc-writer。
- 入力 docs:
  - final requirement/design/plan/report、branch diff、S01-S90 evidence、workflow docs、tests。
- 許可 paths:
  - reviewers are read-only。fixes は bounded follow-up steps の allowed paths に限る。
- 禁止 changes:
  - reviewer の直接実装、phase promotion self-claim、broad refactor。
- 受け入れ条件:
  - reviewer triad pass、validation commands pass、report closure ledgers complete、PR Delivery Gate pass、Merge Preparation Gate pass。
- reviewer focus:
  - qa-reviewer: test sufficiency and missing integration cases。
  - code-reviewer: integrated diff, layering, rollback/retry/failure order, mirror parity。
  - spec-reviewer: requirement/design/plan/report/docs alignment。
- 必須出力:
  - reviewer verdicts、validation results、PR Delivery Gate evidence、Merge Preparation Gate evidence、final risks、report ledger updates。
- 停止条件:
  - required validation / reviewer gate が fail, unavailable, denied, waived without explicit risk acceptance, provisional のまま。

#### 具体テストケース一覧
- `tc-s99-001` manual-required: closure ledger completeness
  - 前提: S01-S90 are complete or approved no-op。
  - 操作: `report.md` closure ledgers / reviewer gate / commit gate を inspect。
  - 期待結果: tc-001 through tc-015 が pass または justified approved-no-op。unresolved blocking EAL なし。
  - 失敗検出: implementation success without issue-level evidence closure。
  - 検証方法: manual report inspection plus final spec-reviewer。
  - 関連 closure id: tc-014
- `tc-s99-002` command: final validation bundle
  - 前提: final branch diff is ready。
  - 操作: targeted tests, full unittest, validate, sync, diff check, parity checks。
  - 期待結果: all pass or failure classified/fixed/re-run。
  - 失敗検出: cross-module regression missed by targeted tests。
  - 検証方法: commands recorded in report。
  - 関連 closure id: tc-014
- `tc-s99-003` manual-required: final reviewer triad
  - 前提: final diff, report evidence, docs ready。
  - 操作: qa-reviewer, code-reviewer, spec-reviewer。
  - 期待結果: all fresh pass; findings fixed through bounded follow-up and re-reviewed。
  - 失敗検出: treating worker output or earlier reviewer pass as final gate。
  - 検証方法: reviewer evidence in final gate sections。
  - 関連 closure id: tc-014
- `tc-s99-004` manual-required: PR Delivery Gate and Merge Preparation Gate evidence exists before issue finish
  - 前提: final branch diff is ready and PR creation/reuse has been handled through `github-pr-merge-preparer` workflow。
  - 操作: inspect `report.md` for PR URL, selected base, base-resolution source/conflict handling, draft/ready decision, head branch/SHA, issue linkage, PR reuse/new-PR decision, PR open state, monitor status, latest monitored head SHA, checks/reviews/merge blocker status, unresolved blockers, and final merge-prepared decision。
  - 期待結果: PR Delivery Gate and Merge Preparation Gate are pass before `issue finish` is attempted。
  - 失敗検出: issue reported complete or `issue finish` attempted without mandatory PR lifecycle evidence。
  - 検証方法: manual report inspection plus final spec-reviewer。
  - 関連 closure id: tc-015

#### ステップ完了契約
- close 条件:
  - final validation, reviewer triad, PR Delivery Gate, and Merge Preparation Gate pass; report ledger complete; remaining risks none or non-blocking with evidence。
- commit / no-op gate:
  - final commit / external evidence は workflow に従って report に記録する。

## Rollback / Compatibility
- Persistent schema migration は行わない。既存 `promotion_record` と `grants` fields を使う。
- rollback は runtime / tests / docs changes の通常 revert。
- 既に `issue_finish_lifecycle_transition` が永続化された active entry は新 runtime で finish-ready。revert 前の旧 runtime では token interpretation が異なる可能性があるため、rollback note を `report.md` に残し、標準 workflow として manual `active.json` edit を案内しない。
- Failure recovery:
  - local gate failure: synthetic active state unchanged。
  - transition persistence failure: previous active state restored; no GitHub mutation。
  - GitHub close failure after transition: finish-ready active state remains for retry。
  - active clear failure: existing recovery guidance and no post-sync。

## Docs Impact
- Required:
  - provider source of truth `src/spec_dock/assets/spec_dock/docs/workflow_issue.md` を更新し、dogfooding mirror `spec-dock/docs/workflow_issue.md` と一致させる。
  - finish-only internal transition、fail-closed local gates、official recovery path、lifecycle-only boundary を反映する。
- Runtime guidance:
  - direct `active.json` editing を標準 recovery としない。
- Context-pack / active display:
  - ancestor synthetic downstream blocks が残り得ることを full lifecycle approval と誤読させない。

## 未確定事項
- なし:
  - `commit_active_state()` を直接使うか小 helper を作るかは S02 の implementation-local decision。active-store snapshot / rollback path を使う契約は固定済み。

## 最終完了条件
- AC-001 through AC-004 and EC-001 through EC-004 are closed by tc-001 through tc-015。
- Synthetic approval rejection remains intact。
- `issue finish` can close/clear from supported synthetic active state through internal finish-only transition。
- Fail-closed cases mutate neither GitHub nor active state unless transition has already been safely persisted for retry。
- Provider and dogfooding mirror behavior match。
- Workflow docs and CLI guidance match runtime behavior。
- `report.md` closure ledgers, reviewer gates, validation commands, and commit/no-op gates are complete。
- PR Delivery Gate and Merge Preparation Gate evidence are recorded before `issue finish`。
- qa-reviewer, issue-wide code-reviewer, and final spec-reviewer return fresh pass。
