---
種別: 実装計画書（Issue）
ID: "iss-00238"
タイトル: "Use Stdout Runbook Handoff Instead Of Generated Workflow Files"
関連GitHub: ["#238"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-24"
依存: ["requirement.md", "design.md"]
親: ["epic-00224", "init-local-00003"]
---

# iss-00238 Use Stdout Runbook Handoff Instead Of Generated Workflow Files — 実装計画（実行契約 / Execution Contract）

## この計画で満たす要件ID

- AC:
  - AC-001: `guidance issue-planning` が planning guidance を stdout に返す。
  - AC-002: `guidance issue-execution` が execution guidance を stdout に返す。
  - AC-003: `current` / `next` を primary command surface に残さない。
  - AC-004: Projection は agent guidance を block しない。
  - AC-005: Projection は ignored human artifact として扱われる。
  - AC-006: Skill が stdout guidance の task checklist 登録を促す。
  - AC-007: Stale projection が guidance 結果に影響しない。
- EC:
  - EC-001: active issue が存在しない。
  - EC-002: unknown target。
  - EC-003: malformed assurance / stale source binding。
  - EC-004: context packet write failure。
- 制約:
  - Provider-side source を authority とする。
  - `workflow next` 互換 alias は追加しない。
  - Context packet の責務は変更しない。
  - User-facing docs は日本語で記述する。

## 依存関係から導く実装順序

- 依存関係の参照元:
  - `design.md` の module dependency と file 変更計画。
- 順序ルール:
  - 先に public CLI contract を test で固定する。
  - 次に use case / projection semantics を変更する。
  - 最後に Skill asset と installer / wrapper tests を更新する。
- step 依存サマリー:
  - S01:
    - 依存: なし。
    - unblock: `guidance <target>` public contract。
    - 対象ファイル: parser / command / presentation / CLI tests。
  - S02:
    - 依存: S01。
    - unblock: projection non-blocking / stale independence。
    - 対象ファイル: application workflow / runbook store / infra tests。
  - S03:
    - 依存: S01, S02。
    - unblock: Skill first-read handoff と installed asset parity。
    - 対象ファイル: provider Skill assets / init-update tests / wrapper tests。
  - S99:
    - 依存: S01-S03。
    - unblock: issue-wide quality gate。

## ステップ一覧

- S01:
  - 観測可能な振る舞い: `guidance issue-planning` / `guidance issue-execution` が stdout guidance を返し、`workflow next` ではなく `guidance` が primary CLI になる。
  - 依存: なし。
  - unblock: S02, S03。
  - 対象ファイル: runtime parser / command / presentation / CLI tests。
  - 閉じる要件: AC-001, AC-002, AC-003, EC-001, EC-002, EC-003。
  - レビューゲート: code-reviewer。
- S02:
  - 観測可能な振る舞い: projection write failure が guidance stdout を block せず、stale projection に依存しない。
  - 依存: S01。
  - unblock: S03, S99。
  - 対象ファイル: application workflow / runbook store / tests。
  - 閉じる要件: AC-004, AC-005, AC-007, EC-004。
  - レビューゲート: code-reviewer。
- S03:
  - 観測可能な振る舞い: Issue Planning / Execution Skill が `guidance <target>` と task checklist 登録を first-read handoff にする。
  - 依存: S01, S02。
  - unblock: S99。
  - 対象ファイル: provider Skill assets / installer tests / wrapper tests。
  - 閉じる要件: AC-003, AC-006。
  - レビューゲート: spec-reviewer。
- S99:
  - 観測可能な振る舞い: issue-wide tests / docs / specs が整合し、実装 ready。
  - 依存: S01-S03。
  - unblock: issue finish / PR。
  - 対象ファイル: issue-wide diff。
  - 閉じる要件: 全 AC / EC。
  - レビューゲート: qa-reviewer、code-reviewer、spec-reviewer。

## 要件 ↔ ステップ対応

- AC-001 -> S01
- AC-002 -> S01
- AC-003 -> S01, S03
- AC-004 -> S02
- AC-005 -> S02
- AC-006 -> S03
- AC-007 -> S02
- EC-001 -> S01
- EC-002 -> S01
- EC-003 -> S01
- EC-004 -> S02

## 仕様固定クロージャ索引（Spec-Locked Closure Index）

| 識別子（ID） | ステップ（step） | スライス（slice） | 種別（type） | 仕様リンク | 固定する期待値 | 観測可能な入力 / 状態 | 防ぐ bug class | 必須 | 証跡レベル（evidence level） | クロージャ証跡（closure evidence） |
|---|---|---|---|---|---|---|---|---|---|---|
| tc-001 | S01 | guidance CLI | 受け入れ | AC-001, AC-002 | `guidance issue-planning` / `issue-execution` が stdout guidance を返す | CLI command | command surface drift | yes | red-required | report step closure |
| tc-002 | S01 | target validation | 否定系 | EC-002 | unknown target を reject し projection を作らない | `guidance unknown-target` | silent invalid target | yes | red-required | report step closure |
| tc-003 | S02 | projection non-blocking | 回帰 | AC-004 | projection write failure でも guidance stdout は成功 | failing RunbookStore fixture | projection failure blocks agent | yes | red-required | report step closure |
| tc-004 | S02 | stale projection independence | 回帰 | AC-007 | stale `current-runbook.*` を読まず現在 state から guidance を生成 | stale projection + active issue | stale handoff | yes | red-required | report step closure |
| tc-005 | S03 | skill handoff | inspect | AC-006 | Skill が `guidance <target>` と checklist 登録を要求する | provider / installed Skill text | skill drift | yes | inspect-only | report step closure |
| tc-006 | S99 | issue-wide regression | 統合 | 全 AC / EC | focused unit / CLI / installer tests が通る | branch diff | integration regression | yes | covered-existing | final quality gate |

## レビュー / QA ゲート方針

- RG1 step review:
  - 実施タイミング: 各 implementation step の commit 前。
  - reviewer:
    - S01 / S02: code-reviewer。
    - S03: spec-reviewer。
  - pass 条件: review_status: pass。
- QG1 final QA:
  - reviewer: qa-reviewer。
  - 範囲: guidance CLI、projection non-blocking、Skill handoff、regression coverage。
- SG1 final spec review:
  - reviewer: spec-reviewer。
  - 範囲: requirement / design / plan / report / implementation / tests / docs 整合。

## 実行ルール（全ステップ共通）

- 各 implementation step は 1 behavior slice / 1 review scope / 1 commit boundary とする。
- `plan.md` は planned contract を記録し、実行結果は `report.md` に記録する。
- `workflow next` 互換 alias は追加しない。
- Provider source を先に更新し、dogfooding mirror は必要に応じて検証する。
- Context packet の write / fail-closed semantics は今回の scope で変更しない。
- Projection は human-facing ignored artifact であり、agent-facing authority ではない。

## 実装ステップ

### 実装ステップ S01 — `guidance <target>` CLI contract を導入する

- 振る舞いの目標（behavior goal）:
  - `./spec-dock/scripts/spec-dock guidance issue-planning --format json`
  - `./spec-dock/scripts/spec-dock guidance issue-execution --format markdown`
  - 上記が既存 Runbook / state guidance を stdout に返す。
- design 参照:
  - `design.md` の "インターフェース契約"、"シーケンス差分"。
- 依存:
  - なし。
- unblock:
  - S02, S03。
- 対象ファイル:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/parser.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/workflow.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/guidance.py`（追加する場合）
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/workflow.py`
  - `tests/cli_runtime/test_workflow.py`
  - `tests/cli_runtime/test_workflow_context_routing.py`
- 計画済み契約（planned contract）:
  - scope:
    - `guidance` command を public entrypoint とする。
    - `issue-planning` / `issue-execution` target を受ける。
    - `--format markdown|json` を維持する。
    - `workflow next` tests を `guidance` contract に置き換える。
  - テスト義務:
    - closure id: tc-001, tc-002
    - coverage rationale:
      - command name / target validation / output shape が今回の主要 contract であるため、CLI runtime test で固定する。
  - Red / 代替証跡の要件:
    - red-required:
      - 実装前に `guidance` command が存在しないため CLI test は失敗する。
  - 実装範囲:
    - allowed paths:
      - 上記 runtime / CLI / presentation / tests。
    - forbidden changes:
      - Assurance classification policy の変更。
      - Context packet semantics の変更。
      - `workflow next` 互換 alias の追加。
  - Green 検証:
    - `uv run pytest tests/cli_runtime/test_workflow.py`
    - `uv run pytest tests/cli_runtime/test_workflow_context_routing.py`
  - Refactor / cleanup ガードレール:
    - 目的: command surface 置換に必要な最小責務移動。
    - 禁止する広がり: workflow state resolver / assurance engine の再設計。
  - closure 証跡要件:
    - Step Contract Closure: `guidance` CLI contract が通る。
    - Test Contract Closure: tc-001 / tc-002 が通る。
    - Closure Coverage: no-active / scaffold requirement / malformed assurance / stale source binding の代表 case が guidance で通る。
  - report 証跡の記録先:
    - `report.md` の S01 Step Contract Closure / Test Contract Closure。
  - amendment trigger:
    - `workflow status` の削除 / rename が必要になる。
    - `WorkflowResult` schema の破壊的変更が必要になる。

#### 委任契約（delegation contract）

- 委任ロール:
  - dev-coder。
- 入力 docs:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - `spec-dock/docs/workflow_issue.md`
  - current target files listed above。
- 許可 paths:
  - S01 対象ファイル。
- 禁止 changes:
  - Assurance / context packet policy。
  - Skill asset 更新（S03 で実施）。
- 受け入れ条件:
  - AC-001, AC-002, AC-003, EC-001, EC-002, EC-003。
- 必須 tests:
  - `uv run pytest tests/cli_runtime/test_workflow.py`
  - `uv run pytest tests/cli_runtime/test_workflow_context_routing.py`
- reviewer focus:
  - code-reviewer: parser / command boundary、payload compatibility、regression risk。
- 必須出力:
  - changed files、verification result、report evidence、unresolved risks。
- 停止条件:
  - parser architecture が `guidance` を追加できない。
  - output schema 変更が downstream tests を広範囲に壊す。

#### 具体テストケース一覧

- `tc-s01-001` acceptance: planning guidance JSON
  - 前提: active issue with scaffold requirement。
  - 操作: `guidance issue-planning --format json`。
  - 期待結果: `state=requirement-capture`、`next_action=requirement-capture-required`。
  - 失敗検出: command missing / wrong state / malformed JSON。
  - 検証方法: CLI runtime test。
  - 関連 closure id: tc-001

- `tc-s01-002` acceptance: execution guidance Markdown
  - 前提: substantive requirement and executable plan。
  - 操作: `guidance issue-execution --format markdown`。
  - 期待結果: `state: ready` と execution-ready guidance。
  - 失敗検出: old `workflow next` only / missing execution content。
  - 検証方法: CLI runtime / context routing tests。
  - 関連 closure id: tc-001

- `tc-s01-003` negative: unknown target
  - 前提: initialized repo。
  - 操作: `guidance unknown-target --format json`。
  - 期待結果: invalid choice / non-zero、projection file を作らない。
  - 検証方法: CLI runtime test。
  - 関連 closure id: tc-002

#### ステップ完了契約

- closure id:
  - tc-001, tc-002
- close 条件:
  - `guidance` CLI tests が pass。
  - `workflow next` を primary とする tests が残っていない。
- 検証 evidence:
  - pytest output。
- report evidence:
  - Step Contract Closure、Test Contract Closure、Closure Coverage、Closure Delta。
- 残リスク:
  - `workflow status` naming の残存が混乱しないかは S99 で inspection。

#### ステップゲート

- step reviewer gate:
  - reviewer: code-reviewer。
  - review 範囲: S01 diff。
  - pass 条件: review_status: pass。
- commit / no-op gate:
  - closure 状態: committed。
  - commit 範囲: S01 files。

### 実装ステップ S02 — projection を human-only / non-blocking にする

- 振る舞いの目標:
  - Guidance stdout は projection write failure によって blocked にならない。
  - Stale projection が存在しても guidance は current state から生成される。
  - Projection は ignored human artifact として残り、Git tracked diff を作らない。
- design 参照:
  - `design.md` の "projection の再整理"、"ドメインモデル差分"。
- 依存:
  - S01。
- unblock:
  - S03, S99。
- 対象ファイル:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/workflow.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/runbook_store.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/workflow.py`
  - `tests/unit/infra/test_runbook_store.py`
  - `tests/cli_runtime/test_workflow.py`
- 計画済み契約:
  - scope:
    - `runbook_store.write_current` は best-effort projection として扱う。
    - Projection result / error は payload metadata として観測可能にしてよい。
    - Projection error は `WorkflowState(kind="blocked", reason_code="runbook-write-failure")` に変換しない。
    - Context packet write failure は既存どおり fail-closed を維持する。
  - テスト義務:
    - closure id: tc-003, tc-004
    - coverage rationale:
      - stale / write failure が本 issue の主要 bug class。
  - Red / 代替証跡の要件:
    - red-required:
      - 現行 `test_workflow_next_returns_blocked_when_projection_write_fails` は新仕様に対して失敗する。
  - 実装範囲:
    - allowed paths:
      - S02 対象ファイル。
    - forbidden changes:
      - Context packet fail-closed 緩和。
      - Git ignore policy の広範囲変更。
  - Green 検証:
    - `uv run pytest tests/unit/infra/test_runbook_store.py`
    - `uv run pytest tests/cli_runtime/test_workflow.py`
  - Refactor / cleanup ガードレール:
    - projection と guidance result の責務分離だけに留める。
  - closure 証跡要件:
    - Projection failure non-blocking。
    - Stale projection independence。
    - Git tracked diff なし。
  - report 証跡の記録先:
    - `report.md` の S02 sections。
  - amendment trigger:
    - Projection error を payload に出せない既存 schema 制約が判明する。
    - Context packet と projection の責務が切り分け不能と判明する。

#### 委任契約

- 委任ロール:
  - dev-coder。
- 許可 paths:
  - S02 対象ファイル。
- 禁止 changes:
  - S01 command surface 以外の public API 拡張。
  - Context packet semantics の変更。
- 受け入れ条件:
  - AC-004, AC-005, AC-007, EC-004。
- 必須 tests:
  - `uv run pytest tests/unit/infra/test_runbook_store.py`
  - `uv run pytest tests/cli_runtime/test_workflow.py`
- reviewer focus:
  - code-reviewer: failure handling、observability、context packet distinction。
- 停止条件:
  - projection write error を握り潰して観測不能にする設計になる。

#### 具体テストケース一覧

- `tc-s02-001` regression: projection write failure non-blocking
  - 前提: failing RunbookStore。
  - 操作: guidance use case を実行。
  - 期待結果: original state / runbook が返り、`runbook-write-failure` blocked state にならない。
  - 検証方法: unit test。
  - 関連 closure id: tc-003

- `tc-s02-002` regression: stale projection ignored
  - 前提: stale `current-runbook.json` が別 issue を指す。
  - 操作: `guidance issue-planning --format json`。
  - 期待結果: stdout payload は current active issue を示す。
  - 検証方法: CLI runtime test。
  - 関連 closure id: tc-004

- `tc-s02-003` acceptance: projection remains ignored human artifact
  - 前提: Git initialized target repo。
  - 操作: `guidance issue-planning`。
  - 期待結果: projection が生成されても `git status --short` は空。
  - 検証方法: CLI runtime test。
  - 関連 closure id: tc-004

#### ステップ完了契約

- closure id:
  - tc-003, tc-004
- close 条件:
  - Projection failure / stale projection tests が pass。
  - Context packet fail-closed tests が維持される。
- 検証 evidence:
  - pytest output。
- report evidence:
  - Step Contract Closure、Test Contract Closure、Closure Coverage。
- 残リスク:
  - Human projection warning の文言は S99 で final inspection。

#### ステップゲート

- step reviewer gate:
  - reviewer: code-reviewer。
  - review 範囲: S02 diff。
  - pass 条件: review_status: pass。
- commit / no-op gate:
  - closure 状態: committed。

### 実装ステップ S03 — Skill first-read handoff を `guidance <target>` に更新する

- 振る舞いの目標:
  - Issue Planning / Execution Skill が `guidance` command を first-read handoff とし、stdout guidance を task checklist に登録するよう促す。
- design 参照:
  - `design.md` の "skill 文面"。
- 依存:
  - S01, S02。
- unblock:
  - S99。
- 対象ファイル:
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md`
  - `tests/unit/infra/test_init_update.py`
  - `tests/cli_runtime/test_wrappers.py`
  - 必要に応じて docs references。
- 計画済み契約:
  - scope:
    - Planning Skill は `guidance issue-planning --format markdown` を実行する。
    - Execution Skill は `guidance issue-execution --format markdown` を実行する。
    - stdout を current dynamic guidance として扱う。
    - `state` / `next_action` / selected step / commands / stop conditions / verification / reviewer gate を task checklist へ登録する。
    - Projection は human-only ignored artifact であり、agent handoff として読まない。
  - テスト義務:
    - closure id: tc-005
    - coverage rationale:
      - Skill wording drift は agent behavior に直結する。
  - Red / 代替証跡の要件:
    - inspect-only:
      - Skill text assertion で固定する。
  - 実装範囲:
    - allowed paths:
      - S03 対象ファイル。
    - forbidden changes:
      - Skill に full workflow procedure を埋め込むこと。
      - Projection path を handoff authority として説明すること。
  - Green 検証:
    - `uv run pytest tests/unit/infra/test_init_update.py -k "issue_skills or workflow_next or guidance"`
    - `uv run pytest tests/cli_runtime/test_wrappers.py`
  - Refactor / cleanup ガードレール:
    - Skill kernel は concise に保ち、state-specific generated text を入れない。
  - closure 証跡要件:
    - Provider asset / installed asset の両方で wording が一致。
  - report 証跡の記録先:
    - `report.md` の S03 sections。
  - amendment trigger:
    - Existing tests が skill wording を大量 snapshot として固定しており、局所更新できない。

#### 委任契約

- 委任ロール:
  - doc-writer。
- 許可 paths:
  - S03 対象ファイル。
- 禁止 changes:
  - Runtime behavior の変更。
  - Canonical workflow docs の広範囲 rewrite。
- 受け入れ条件:
  - AC-003, AC-006。
- 必須 tests または docs-only verification:
  - focused pytest。
  - `rg -n "workflow next|guidance issue-" src/spec_dock/assets/install_root/.agents/skills tests/unit/infra/test_init_update.py tests/cli_runtime/test_wrappers.py`
- reviewer focus:
  - spec-reviewer: skill wording、authority boundary、task checklist 登録。
- 停止条件:
  - Skill が dynamic guidance を読まず static docs primary に戻る。

#### 具体テストケース一覧

- `tc-s03-001` inspect: planning skill handoff
  - 前提: provider Skill asset。
  - 操作: text を読む。
  - 期待結果: `guidance issue-planning --format markdown` と task checklist 登録要求がある。
  - 検証方法: unit/infra assertion。
  - 関連 closure id: tc-005

- `tc-s03-002` inspect: execution skill handoff
  - 前提: provider Skill asset。
  - 操作: text を読む。
  - 期待結果: `guidance issue-execution --format markdown` と projection non-handoff warning がある。
  - 検証方法: unit/infra assertion。
  - 関連 closure id: tc-005

#### ステップ完了契約

- closure id:
  - tc-005
- close 条件:
  - Provider / installed Skill tests が pass。
- 検証 evidence:
  - focused pytest / rg inspection。
- report evidence:
  - Step Contract Closure、Test Contract Closure、Closure Coverage。
- 残リスク:
  - Other Epic / Initiative Skills への `guidance` 展開は follow-up。今回の required scope は Issue Planning / Execution。

#### ステップゲート

- step reviewer gate:
  - reviewer: spec-reviewer。
  - review 範囲: S03 diff。
  - pass 条件: review_status: pass。
- commit / no-op gate:
  - closure 状態: committed。

### ドキュメント影響の解消ステップ S90（docs impact resolution / docs refresh）

- 対象:
  - `spec-dock/active/issue/requirement.md`
  - `spec-dock/active/issue/design.md`
  - `spec-dock/active/issue/plan.md`
  - 必要に応じて provider docs / workflow docs。
- 対応:
  - S01-S03 の実装中に、runtime command rename により docs の `workflow next` 記述が stale になる場合は、agent-facing な箇所を `guidance <target>` に更新する。
  - Epic docs の大規模 rewrite はこの Issue の実装範囲に含めず、必要な場合は follow-up として report に記録する。
- doc update owner:
  - doc-writer。
- spec/doc review:
  - reviewer: spec-reviewer。
  - pass 条件: docs が requirement / design / plan と整合し、未解決の必須 docs 影響が残っていない。

### 最終品質ゲートステップ S99（final quality gate）

- branch diff 範囲:
  - S01-S03 の統合 diff。
- 必須 validation:
  - `uv run pytest tests/cli_runtime/test_workflow.py`
  - `uv run pytest tests/cli_runtime/test_workflow_context_routing.py`
  - `uv run pytest tests/unit/infra/test_runbook_store.py`
  - `uv run pytest tests/cli_runtime/test_wrappers.py`
  - `uv run pytest tests/unit/infra/test_init_update.py -k "issue_skills or guidance or workflow_next"`
  - 必要に応じて `uv run pytest tests/unit tests/cli_runtime`
- final QA gate:
  - reviewer: qa-reviewer。
  - 範囲: Issue 全体の obligation coverage と integration test 要否。
  - pass 条件: reviewer pass。
- final code review gate:
  - reviewer: code-reviewer。
  - 範囲: issue-wide integrated diff、runtime / tests / projection handling。
  - pass 条件: review_status: pass。
- final spec review gate:
  - reviewer: spec-reviewer。
  - 範囲: requirement / design / plan / report / implementation / tests / docs 整合。
  - pass 条件: reviewer pass。
- final commit gate:
  - commit 範囲: S99 cleanup / report evidence。
  - final report ledger: all AC / EC closure。
  - post-commit external evidence destination: `report.md`。

## 未確定事項

- なし。

## 最終完了条件

- AC/EC 達成:
  - AC-001〜AC-007、EC-001〜EC-004 が report evidence で閉じている。
- docs 影響解決:
  - Skill / docs の agent-facing handoff が `guidance <target>` に整合している。
- 全 implementation step 完了:
  - S01, S02, S03, S90, S99 が committed / approved-no-op。
- final quality gate pass:
  - qa-reviewer: pass。
  - issue-wide code-reviewer: pass。
  - spec-reviewer: pass。
- final commit 完了:
  - 実装・docs・report が commit 済み。
- 必須 closure id 完了:
  - tc-001〜tc-006。
- final clean state:
  - no unintended staged / unstaged changes。
