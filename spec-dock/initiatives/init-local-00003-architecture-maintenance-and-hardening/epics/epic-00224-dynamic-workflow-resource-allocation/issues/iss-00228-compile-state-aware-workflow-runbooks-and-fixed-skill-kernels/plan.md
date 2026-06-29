---
種別: 実装計画書（Issue）
ID: "iss-00228"
タイトル: "Compile State Aware Workflow Runbooks And Fixed Skill Kernels"
関連GitHub: ["#228"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-23"
依存: ["requirement.md", "design.md"]
親: ["epic-00224", "init-local-00003"]
---

# iss-00228 Compile State Aware Workflow Runbooks And Fixed Skill Kernels — 実装計画（実行契約 / Execution Contract）

## この計画で満たす要件ID
- AC:
  - AC-001 no-active guidance
  - AC-002 requirement-capture state
  - AC-003 classification-required state
  - AC-004 authorized profile authority
  - AC-005 fixed Skill / clean Git
  - AC-006 Runbook minimality
- EC:
  - EC-001 malformed assurance
  - EC-002 generated store write failure
  - EC-003 unknown command target
- 制約:
  - Fixed Skill kernel / compiled Runbook authority
  - `authorized_profile` authority only
  - generated projection is not canonical
  - provider source / dogfooding mirror parity
  - MyPy / Ruff clean

## 依存関係から導く実装順序
- 依存関係の参照元:
  - `design.md` の module dependency diagram、interface contract、file change plan。
- 順序ルール:
  - public CLI behavior の red test を先に固定し、domain/application を vertical tracer bullet として通す。
  - generated store と fixed Skill は runtime contract が固定されてから変更する。
  - dogfooding mirror は provider 実装後に同期し、tracked diff / parity を検証する。
- step 依存サマリー:
  - S01:
    - 依存: `iss-00227` Assurance runtime。
    - unblock: state/runbook public contract。
    - 対象ファイル: runtime domain/application/commands/presentation/tests。
  - S02:
    - 依存: S01 の Runbook model。
    - unblock: ignored projection / clean Git evidence。
    - 対象ファイル: infra store / CLI integration / tests。
  - S03:
    - 依存: S01/S02 の `workflow next` contract。
    - unblock: fixed planning/execution skill kernels。
    - 対象ファイル: install_root skills / installer tests。
  - S90:
    - 依存: S01-S03。
    - unblock: provider/mirror parity。
  - S99:
    - 依存: S01-S90。
    - unblock: issue finish readiness。

## ステップ一覧
- S01:
  - 観測可能な振る舞い: `workflow status` / `workflow next` が state-aware Runbook を stdout に返す。
  - 依存: `iss-00227` assurance contract。
  - unblock: runtime public interface。
  - 対象ファイル: runtime domain/application/commands/presentation/tests。
  - 閉じる要件: AC-001, AC-002, AC-003, AC-004, AC-006, EC-001, EC-003。
  - レビューゲート: code-reviewer。
- S02:
  - 観測可能な振る舞い: Runbook projection が ignored generated path に atomic write され、write failure は blocked state として扱われる。
  - 依存: S01。
  - unblock: generated state clean Git evidence。
  - 対象ファイル: infra runbook store / CLI integration / tests。
  - 閉じる要件: AC-005, EC-002。
  - レビューゲート: code-reviewer。
- S03:
  - 観測可能な振る舞い: Planning / Execution Skill が fixed kernel として `workflow next` を参照し、state-specific generated text を tracked Skill に持たない。
  - 依存: S01/S02。
  - unblock: Skill diff stability。
  - 対象ファイル: provider install_root skills / tests。
  - 閉じる要件: AC-005, AC-006。
  - レビューゲート: spec-reviewer。
- S90:
  - 観測可能な振る舞い: provider asset から dogfooding mirror へ同期され、runtime / skill parity と generated ignored paths が確認される。
  - 依存: S01-S03。
  - unblock: issue-wide verification。
  - 対象ファイル: dogfooding mirror under `spec-dock/`。
  - 閉じる要件: provider/mirror parity constraint。
  - レビューゲート: spec-reviewer。
- S99:
  - 観測可能な振る舞い: issue-wide tests / lint / reviewers が pass し、report が closure evidence を持つ。
  - 依存: S01-S90。
  - unblock: issue finish / epic continuation。
  - 対象ファイル: report / final validation evidence。
  - 閉じる要件: all。
  - レビューゲート: qa-reviewer, code-reviewer, spec-reviewer。

## 要件 ↔ ステップ対応
- AC-001 -> S01
- AC-002 -> S01
- AC-003 -> S01
- AC-004 -> S01
- AC-005 -> S02, S03, S90
- AC-006 -> S01, S03
- EC-001 -> S01
- EC-002 -> S02
- EC-003 -> S01

## 仕様固定クロージャ索引（Spec-Locked Closure Index）

| 識別子（ID） | ステップ（step） | スライス（slice） | 種別（type） | 仕様リンク | 固定する期待値 | 観測可能な入力 / 状態 | 防ぐ bug class | 必須 | 証跡レベル（evidence level） | クロージャ証跡（closure evidence） |
|---|---|---|---|---|---|---|---|---|---|---|
| tc-001 | S01 | workflow-state-runbook | acceptance | AC-001/AC-002/AC-003 | state に応じて一つの next action を返す | no-active / scaffold requirement / missing assurance | wrong phase execution | yes | red-required | report S01 closure |
| tc-002 | S01 | profile-authority | invariant | AC-004/AC-006 | `lite_candidate` では obligation を減らさず未選択 profile 手順を含めない | valid assurance with non-Lite authorized profile and Lite candidate | unsafe Lite reduction | yes | red-required | report S01 closure |
| tc-003 | S01 | malformed-input | negative | EC-001/EC-003 | malformed assurance / unknown target は fail-closed または validation error | invalid `assurance.json` / unknown target | silent unsafe fallback | yes | red-required | report S01 closure |
| tc-004 | S02 | generated-projection | acceptance | AC-005/EC-002 | ignored projection を atomic write し、write failure を blocked / doctor guidance にする | workflow next with writable/unwritable projection path | tracked generated artifact / partial write / unsafe continuation | yes | red-required | report S02 closure |
| tc-005 | S03 | fixed-skill-kernel | inspect | AC-005/AC-006 | Skill は `workflow next` kernel を持ち、state-specific full profile text を持たない | installed skill assets | tracked skill mutation / token waste | yes | inspect-only | report S03 closure |
| tc-006 | S90 | provider-mirror-parity | integration | provider/mirror constraint | provider runtime / skill assets が mirror と一致する | `spec-dock update .` after provider changes | dogfooding drift | yes | inspect-only | report S90 closure |
| tc-007 | S99 | issue-final-quality | final | all | unit/CLI/lint/reviewer gates pass | full issue diff | integrated regression | yes | manual-required | report S99 closure |

## レビュー / QA ゲート方針
- RG1 step review:
  - 実施タイミング: 各 implementation step の commit 前。
  - reviewer: code-reviewer for runtime/tests/scaffold behavior; spec-reviewer for skill/docs-only changes。
  - pass 条件: `review_status: pass`。
- QG1 final QA:
  - reviewer: qa-reviewer。
  - 範囲: Issue 全体の obligation coverage、missing high-value tests、manual / integration test 要否。
- SG1 final spec review:
  - reviewer: spec-reviewer。
  - 範囲: requirement / design / plan / report / implementation / tests / docs 整合。

## 実行ルール（全ステップ共通）
- 各 implementation step は 1 behavior slice / 1 review scope / 1 commit boundary とする。
- `plan.md` には planned requirements、evidence destination、closure 条件だけを書く。observed result は `report.md` に書く。
- docs-only / inspect-only step は code test 前提にせず、代替 evidence path と rationale を implementation 前に固定する。
- implementation 中に新しい仕様、external contract risk、未計画の closure が見つかった場合は、report 記録だけで足りるか、plan amendment と re-review が必要かを判断する。

## 実装ステップ

### 実装ステップ S01 — workflow status / next の state-aware Runbook stdout
- 振る舞いの目標（behavior goal）:
  - `workflow status` / `workflow next` が active state、artifact readiness、Assurance authority から no-active / requirement-capture / classification-required / ready を解決し、JSON / Markdown Runbook を返す。
- design 参照:
  - `design.md` の Interface contract、Domain Model Delta、Sequence Delta。
- 依存:
  - `iss-00227` Assurance runtime。
- unblock:
  - S02 projection store、S03 fixed skill kernel。
- 対象ファイル:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/{cli,commands,application,domain,presentation}/`
  - `tests/cli_runtime/test_workflow.py`
  - `tests/unit/domain/test_workflow_state.py`
- 計画済み契約（planned contract）:
  - scope:
    - `workflow status` / `workflow next` parser、command、use case、state resolver、runbook compiler、rendering を実装する。
  - テスト義務（test obligation）:
    - closure id: tc-001, tc-002, tc-003。
    - coverage rationale: wrong phase execution、unsafe Lite reduction、malformed authority の regression risk が高いため red-required。
  - Red / 代替証跡の要件:
    - `tests/cli_runtime/test_workflow.py` と `tests/unit/domain/test_workflow_state.py` に public behavior first の failing tests を置く。
  - 実装範囲（implementation scope）:
    - allowed paths:
      - runtime CLI/domain/application/presentation。
      - workflow-related tests。
    - forbidden changes:
      - Skill assets、Runbook projection store、PR review、profile-aware artifact composer。
  - Green 検証:
    - `uv run pytest tests/unit/domain/test_workflow_state.py tests/cli_runtime/test_workflow.py`
  - Refactor / cleanup ガードレール:
    - 既存 assurance command の責務を崩さず、必要な read-only reuse に限定する。
  - closure 証跡要件:
    - Step Contract Closure、Test Contract Closure、Closure Coverage を report に記録する。
  - report 証跡の記録先:
    - `report.md` の S01 セッションログ、TDD / Red / Green / Refactor Evidence、Step Contract Closure。
  - amendment trigger:
    - state kind の追加、authority model の変更、Runbook schema の backward-incompatible 変更が必要になった場合。

#### 委任契約（delegation contract）
- 委任ロール（delegated role）:
  - dev-coder。
- 入力 docs:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - `spec-dock/docs/workflow_issue.md`
  - existing assurance runtime files。
- 許可 paths:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/`
  - `tests/cli_runtime/test_workflow.py`
  - `tests/unit/domain/test_workflow_state.py`
- 禁止 changes:
  - `.agents/skills/**`
  - GitHub / PR review tooling
  - profile-aware artifact composition
- 受け入れ条件:
  - tc-001, tc-002, tc-003 が pass する。
- 必須 tests:
  - `uv run pytest tests/unit/domain/test_workflow_state.py tests/cli_runtime/test_workflow.py`
- reviewer focus:
  - code-reviewer: architecture layering、authority invariant、CLI behavior、tests。
- 必須出力（output required）:
  - changed files、verification result、unresolved risks、Ledger Note または no material decision statement。
- 停止条件（stop conditions）:
  - approved docs と矛盾する state model が必要、assurance contract の破壊的変更が必要、targeted tests が実行不能。

#### 具体テストケース一覧

- `tc-s01-001` acceptance: no-active は issue start guidance だけを返す
  - 前提: temp SpecDock repo に active issue がない。
  - 操作: `spec-dock workflow next issue-execution --format json` を実行する。
  - 期待結果: `state=no-active`、`next_action=issue-start-required` となり、commands は `issue start <issue-id>` guidance のみに限定される。
  - 失敗検出: active なしで requirement / implementation / review 手順へ進む回帰を検出する。
  - 検証方法: CLI runtime test。
  - 関連 closure id: tc-001

- `tc-s01-002` acceptance: scaffold requirement は requirement-capture へ戻す
  - 前提: active Issue があり、`requirement.md` が template placeholder のまま。
  - 操作: `spec-dock workflow status --format json` と `spec-dock workflow next issue-planning --format json` を実行する。
  - 期待結果: 両方で `state=requirement-capture` と reason code が返り、`workflow next` の next action は requirement authoring / review gate に限定される。
  - 失敗検出: template-only specs を execution-ready と誤判定する回帰、または status と next が state 不一致になる回帰を検出する。
  - 検証方法: CLI runtime test。
  - 関連 closure id: tc-001

- `tc-s01-003` acceptance: missing assurance は classification-required にする
  - 前提: active Issue があり、要件は実質入力済みだが `assurance.json` がない。
  - 操作: `spec-dock workflow next issue-execution --format markdown` を実行する。
  - 期待結果: Runbook は `assurance classify` / `assurance verify` を先に要求し、実装開始を許可しない。
  - 失敗検出: assurance なしで execution を許可する回帰を検出する。
  - 検証方法: CLI runtime test。
  - 関連 closure id: tc-001

- `tc-s01-004` invariant: lite_candidate は obligation を減らさない
  - 前提: Assurance summary に `lite_candidate=true` と non-Lite `authorized_profile` がある。
  - 操作: Runbook compiler を実行する。
  - 期待結果: `obligation_source=authorized_profile` となり、Lite 向け削減手順は含まれない。
  - 失敗検出: candidate と authorized を混同する回帰を検出する。
  - 検証方法: domain unit test。
  - 関連 closure id: tc-002

- `tc-s01-005` negative: malformed assurance は fail-closed
  - 前提: active Issue の `assurance.json` が malformed。
  - 操作: `spec-dock workflow next issue-execution --format json` を実行する。
  - 期待結果: fail-closed state / reason code を返し、obligation を減らさない。
  - 失敗検出: parse failure を無視して ready 扱いする回帰を検出する。
  - 検証方法: CLI runtime test。
  - 関連 closure id: tc-003

- `tc-s01-006` negative: unknown target は projection なしで reject
  - 前提: temp repo。
  - 操作: `spec-dock workflow next unknown-target --format json` を実行する。
  - 期待結果: command は validation error で失敗し、Runbook は生成されない。
  - 失敗検出: unknown target を silently fallback する回帰を検出する。
  - 検証方法: CLI runtime test。
  - 関連 closure id: tc-003

#### ステップ完了契約（step closure contract）
- closure id:
  - tc-001, tc-002, tc-003
- close 条件:
  - planned tests が pass し、workflow stdout contract が実装される。
- 検証 evidence:
  - targeted pytest command。
- report evidence:
  - Step Contract Closure、Test Contract Closure、Closure Coverage、Closure Delta。
- 残リスク:
  - downstream profile-specific Runbook は S01 scope 外。

#### ステップゲート（step gate）
- step reviewer gate:
  - reviewer: code-reviewer
  - review 範囲: S01 diff。
  - pass 条件: `review_status: pass`
  - re-review rule: 指摘を修正し pass まで再実行。
- commit / no-op gate:
  - closure 状態: committed
  - commit 範囲: S01 runtime/tests/report evidence。

### 実装ステップ S02 — ignored generated Runbook projection store
- 振る舞いの目標（behavior goal）:
  - `workflow next` が current Runbook を ignored generated path へ atomic write し、projection result を stdout に含める。
- design 参照:
  - `design.md` の Generated projection path、RunbookStore。
- 依存:
  - S01。
- unblock:
  - S03 fixed skill kernel、S90 parity。
- 対象ファイル:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/runbook_store.py`
  - workflow application / command integration
  - `tests/unit/infra/test_runbook_store.py`
  - `tests/cli_runtime/test_workflow.py`
- 計画済み契約:
  - scope:
    - projection JSON / Markdown atomic write、blocked error propagation、ignored path check。
  - テスト義務:
    - closure id: tc-004。
    - coverage rationale: generated artifact の tracked diff / partial write は workflow 信頼性を壊すため red-required。
  - Red / 代替証跡:
    - store unit test と CLI runtime clean Git test。
  - 実装範囲:
    - allowed paths: infra runbook store、workflow use case integration、tests。
    - forbidden changes: `.gitignore` の unrelated rewrite、skill text。
  - Green 検証:
    - `uv run pytest tests/unit/infra/test_runbook_store.py tests/cli_runtime/test_workflow.py`
  - Refactor / cleanup ガードレール:
    - atomic write helper が既存 infra にあれば reuse し、広い filesystem abstraction は追加しない。
  - report 証跡の記録先:
    - `report.md` S02 ledger。
  - amendment trigger:
    - generated path を requirement/design と変える必要がある場合。

#### 委任契約（delegation contract）
- 委任ロール:
  - dev-coder。
- 入力 docs:
  - `requirement.md`, `design.md`, `plan.md`, existing infra patterns。
- 許可 paths:
  - runtime infra/application/commands/presentation workflow files。
  - `tests/unit/infra/test_runbook_store.py`
  - `tests/cli_runtime/test_workflow.py`
- 禁止 changes:
  - Skill assets、profile composer、PR tooling。
- 受け入れ条件:
  - tc-004 pass。
- 必須 tests:
  - `uv run pytest tests/unit/infra/test_runbook_store.py tests/cli_runtime/test_workflow.py`
- reviewer focus:
  - code-reviewer。
- 必須出力:
  - changed files、verification result、projection path behavior、Ledger Note。
- 停止条件:
  - ignored generated path を保証できない、atomic write が host policy で検証不能。

#### 具体テストケース一覧

- `tc-s02-001` acceptance: current-runbook projection を ignored path に書く
  - 前提: temp git repo に SpecDock scaffold があり、`.agent/` と `active/` が ignored。
  - 操作: `spec-dock workflow next issue-planning --format json` を実行する。
  - 期待結果: `.agent/runbooks/current-runbook.{json,md}` と `active/current-runbook.{json,md}` が作成され、`git status --short` は tracked diff を示さない。
  - 失敗検出: generated output が tracked diff になる回帰を検出する。
  - 検証方法: CLI runtime test。
  - 関連 closure id: tc-004

- `tc-s02-002` negative: projection write failure は blocked として返す
  - 前提: projection 書き込み先を作成できない store fixture。
  - 操作: RunbookStore write を実行する。
  - 期待結果: canonical docs / tracked skill は変更されず、`state=blocked` / `reason_code=runbook-write-failure` と temp cleanup / doctor guidance が result に残る。
  - 失敗検出: write failure で partial file / silent success / unsafe continuation になる回帰を検出する。
  - 検証方法: infra unit test。
  - 関連 closure id: tc-004

#### ステップ完了契約（step closure contract）
- closure id:
  - tc-004
- close 条件:
  - projection tests pass、tracked diff safety が確認される。
- 検証 evidence:
  - targeted pytest command、`git status --short` fixture assertion。
- report evidence:
  - S02 Step Contract Closure。
- 残リスク:
  - projection の telemetry 集計は I07 scope。

#### ステップゲート（step gate）
- step reviewer gate:
  - reviewer: code-reviewer
  - review 範囲: S02 diff。
  - pass 条件: `review_status: pass`
- commit / no-op gate:
  - closure 状態: committed
  - commit 範囲: S02 implementation/tests/report evidence。

### 実装ステップ S03 — Planning / Execution Skill fixed kernel
- 振る舞いの目標（behavior goal）:
  - shipped Planning / Execution Skill が `workflow next` を first-read handoff とする fixed kernel になり、state-specific generated procedure を tracked Skill に持たない。
- design 参照:
  - `design.md` の fixed Skill kernel 方針。
- 依存:
  - S01, S02。
- unblock:
  - Issue switch / classification clean skill diff。
- 対象ファイル:
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md`
  - relevant installer/scaffold tests。
- 計画済み契約:
  - scope:
    - Skill を固定 kernel へ更新し、runtime `workflow next <target>` の取得、freshness / authority stop、canonical docs fallback を明示する。
  - テスト義務:
    - closure id: tc-005。
    - coverage rationale: skill text は code behavior ではないが workflow authority の入口なので inspect-only と scaffold assertion で閉じる。
  - Red / 代替証跡:
    - installer/scaffold test または text assertion で `workflow next` handoff と state-specific profile procedure absence を確認する。
  - 実装範囲:
    - allowed paths: provider skill assets、asset tests。
    - forbidden changes: runtime logic、unrelated skills、generated dogfooding mirror direct edits。
  - Green 検証:
    - `uv run pytest tests/unit/infra/test_init_update.py`
    - direct inspection of skill text。
  - Refactor / cleanup ガードレール:
    - Skill は短縮しすぎず、stop conditions と canonical docs fallback は残す。
  - report 証跡の記録先:
    - `report.md` S03 ledger。
  - amendment trigger:
    - runtime `workflow next` command contract を変更する必要が出た場合。

#### 委任契約（delegation contract）
- 委任ロール:
  - doc-writer。
- 入力 docs:
  - `requirement.md`, `design.md`, `plan.md`, existing skill files, ADR fixed kernel。
- 許可 paths:
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md`
  - tests that assert installed skill content。
- 禁止 changes:
  - runtime implementation、other skills、workflow docs unrelated to fixed kernel。
- 受け入れ条件:
  - tc-005 pass。
- 必須 tests または docs-only verification:
  - `uv run pytest tests/unit/infra/test_init_update.py`
  - skill text inspection。
- reviewer focus:
  - spec-reviewer: ADR / requirement / design alignment、unselected profile text absence。
- 必須出力:
  - changed files、verification result、unresolved risks、Ledger Note。
- 停止条件:
  - Skill kernel だけでは safety stop を表現できない、runtime command contract と矛盾。

#### 具体テストケース一覧

- `tc-s03-001` inspect-only: planning skill is fixed kernel
  - 前提: provider planning skill asset。
  - 操作: skill text を検査する。
  - 期待結果: `workflow next issue-planning` への handoff、freshness stop、canonical docs fallback があり、state-specific full profile procedure はない。
  - 失敗検出: tracked skill が state-specific procedure を持つ回帰を検出する。
  - 検証方法: scaffold/unit assertion と direct inspection。
  - 関連 closure id: tc-005

- `tc-s03-002` inspect-only: execution skill is fixed kernel
  - 前提: provider execution skill asset。
  - 操作: skill text を検査する。
  - 期待結果: `workflow next issue-execution` への handoff、authority stop、canonical docs fallback があり、Lite candidate で obligation を減らす記述はない。
  - 失敗検出: execution skill が profile authority を誤表現する回帰を検出する。
  - 検証方法: scaffold/unit assertion と direct inspection。
  - 関連 closure id: tc-005

#### ステップ完了契約（step closure contract）
- closure id:
  - tc-005
- close 条件:
  - provider skill asset が fixed kernel になり、tests / inspection が pass。
- 検証 evidence:
  - targeted pytest、direct inspection。
- report evidence:
  - S03 Step Contract Closure。
- 残リスク:
  - Full rollout observability は I07 scope。

#### ステップゲート（step gate）
- step reviewer gate:
  - reviewer: spec-reviewer
  - review 範囲: skill asset diff。
  - pass 条件: `review_status: pass`
- commit / no-op gate:
  - closure 状態: committed
  - commit 範囲: S03 skill/tests/report evidence。

### ドキュメント影響の解消ステップ S90（docs impact resolution / docs refresh）
- 対象:
  - dogfooding mirror runtime / skills。
  - generated projection ignored path verification。
- 対応:
  - `uv run python -m spec_dock.cli update .` で provider asset を local dogfooding workspace へ同期する。
  - provider runtime と mirror runtime の parity を確認する。
  - provider install_root skills と mirror `.agents/skills` の relevant skill parity を確認する。
- doc update owner:
  - doc-writer if additional shipped docs changes are required; otherwise orchestrator verification step。
- spec/doc review:
  - reviewer: spec-reviewer
  - pass 条件: docs / skills / mirror が requirement / design / plan と整合し、未解決の必須 docs 影響がない。
- 具体テストケース:
  - `tc-s90-001` inspect-only: provider/mirror parity
    - 前提: provider asset 変更後。
    - 操作: `uv run python -m spec_dock.cli update .` と parity diff を実行する。
    - 期待結果: runtime / relevant skill assets が mirror と一致し、意図しない tracked generated artifact がない。
    - 失敗検出: dogfooding mirror drift を検出する。
    - 検証方法: command inspection。
    - 関連 closure id: tc-006

### 最終品質ゲートステップ S99（final quality gate）
- branch diff 範囲:
  - `iss-00228` の全差分。
- 必須 validation:
  - `uv run pytest tests/unit`
  - `uv run pytest tests/cli_runtime`
  - `make lint`
  - `./spec-dock/scripts/spec-dock validate`
  - provider/mirror runtime parity diff。
- final QA gate:
  - reviewer: qa-reviewer
  - 範囲: Issue 全体の obligation coverage と integration test 要否。
  - pass 条件: `review_status: pass`
- final code review ゲート:
  - reviewer: code-reviewer
  - 範囲: issue-wide integrated diff、構造、責務境界、回帰リスク、保守性。
  - pass 条件: `review_status: pass`
- final spec review ゲート:
  - reviewer: spec-reviewer
  - 範囲: requirement / design / plan / report / implementation / tests / docs 整合。
  - pass 条件: `review_status: pass`
- final commit gate:
  - commit 範囲: final report / reviewer-fix if any。
  - final report ledger: S99 closure evidence。
  - post-commit external evidence destination: `report.md` and git log。

## 未確定事項
- なし。

## 最終完了条件
- AC/EC 達成:
  - AC-001〜AC-006、EC-001〜EC-003 が report closure evidence を持つ。
- docs 影響解決:
  - fixed Skill kernel と dogfooding mirror parity が確認される。
- 全 implementation step 完了:
  - S01/S02/S03/S90/S99 が committed または approved-no-op。
- final quality gate pass:
  - qa-reviewer: pass
  - code-reviewer: pass
  - spec-reviewer: pass
  - required validation commands: pass
