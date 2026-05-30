---
種別: 実装計画書（Issue）
ID: "iss-00142"
タイトル: "Matt Pocock Skill Adoption Analysis"
関連GitHub: ["#142"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-05-30"
依存: ["requirement.md", "design.md"]
親: ["epic-00067", "init-local-00003"]
---

# iss-00142 Matt Pocock Skill Adoption Analysis — 実装計画

## この計画で満たす要件ID
- AC:
  - AC-001, AC-002, AC-003, AC-004, AC-005, AC-006, AC-007, AC-008
- EC:
  - EC-001, EC-002, EC-003, EC-004, EC-005
- 制約:
  - Direct import 禁止
  - runtime / CLI / GitHub label / new skill / `CONTEXT.md` authority / prototype lifecycle 変更禁止
  - Provider-side source of truth first
  - Fresh reviewer gates and report evidence required

## 依存関係から導く実装順序
- 依存関係の正本:
  - `design.md` の依存関係分析、Module Dependency Diagram、ディレクトリ / ファイル変更計画。
- 順序ルール:
  - Plan semantics を持つ docs を先に固定する。
  - Workflow execution policy を次に固定する。
  - Installed skill reminder は docs wording に route する。
  - Tests / dogfooding validation は wording が安定してから行う。
- step 依存サマリー:
  - S01:
    - 依存: approved requirement / design
    - unblock: S03, S05
    - 対象ファイル: `src/spec_dock/assets/spec_dock/docs/phase_plan_issue.md`, `src/spec_dock/assets/spec_dock/docs/authoring/issue-plan.md`
  - S02:
    - 依存: approved requirement / design
    - unblock: S03, S05
    - 対象ファイル: `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
  - S03:
    - 依存: S01, S02
    - unblock: S05
    - 対象ファイル: `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md`
  - S04:
    - 依存: approved design
    - unblock: S05
    - 対象ファイル: `src/spec_dock/assets/install_root/.agents/skills/spec-dock-system-architect/SKILL.md`
  - S05:
    - 依存: S01, S02, S03, S04
    - unblock: S90, S99
    - 対象ファイル: `tests/test_init_update.py`
  - S90:
    - 依存: S01..S05
    - unblock: S99
    - 対象ファイル: dogfooding `spec-dock/docs/...` and `.agents/skills/...` as needed
  - S99:
    - 依存: S90
    - unblock: final delivery
    - 対象ファイル: integrated diff / report evidence

## ステップ一覧
- S01: Issue plan / TDD / slicing discipline docs を更新する
  - 観測可能な振る舞い: Issue planning docs が vertical behavior slice、dependency order、integration checkpoint、HITL/AFK annotation、public interface / observable behavior、vertical tracer bullet、no horizontal batching を説明する。
  - レビューゲート: spec-reviewer
- S02: Issue workflow / diagnosis discipline docs を更新する
  - 観測可能な振る舞い: Issue execution workflow が feedback loop、reproduction、ranked hypotheses、targeted instrumentation、instrumentation cleanup、regression evidence、report ledger を説明する。
  - レビューゲート: spec-reviewer
- S03: Issue execution skill reminder を更新する
  - 観測可能な振る舞い: Execution skill が approved plan 前提を維持したまま、diagnosis と behavior-first TDD を workflow docs へ route する。
  - レビューゲート: spec-reviewer
- S04: System architect skill guidance を更新する
  - 観測可能な振る舞い: System architect skill が deep module、interface as test surface、deletion test、locality / leverage を source-grounded heuristic として扱い、`CONTEXT.md` authority を作らない。
  - レビューゲート: spec-reviewer
- S05: Content / scaffold assertions を更新する
  - 観測可能な振る舞い: Shipped docs / installed skill guidance の essential markers が regression で検出される。
  - レビューゲート: code-reviewer
- S90: Docs impact / dogfooding parity を解消する
  - 観測可能な振る舞い: Provider-side changes が dogfooding workspace に反映済み、または provider-only とする根拠が report に残る。
  - レビューゲート: spec-reviewer
- S99: Final quality gate を通す
  - 観測可能な振る舞い: qa-reviewer / code-reviewer / spec-reviewer が integrated diff を pass する。

## 要件 ↔ ステップ対応
- AC-001 -> S90, S99
- AC-002 -> S01, S02, S03, S04
- AC-003 -> S01, S05
- AC-004 -> S01, S03, S05
- AC-005 -> S02, S03, S05
- AC-006 -> S04, S05
- AC-007 -> S90, S99
- AC-008 -> S01..S99
- EC-001 -> S01..S04, S99
- EC-002 -> S01, S05, S99
- EC-003 -> S01, S05
- EC-004 -> S02, S03, S05
- EC-005 -> S90, S99

## 仕様固定クロージャ索引（Spec-Locked Closure Index）

| 識別子（ID） | ステップ（step） | スライス（slice） | 種別（type） | 仕様リンク | 固定する期待値 | 観測可能な入力 / 状態 | 防ぐ bug class | 必須 | 証跡レベル（evidence level） | クロージャ証跡（closure evidence） |
|---|---|---|---|---|---|---|---|---|---|---|
| tc-001 | S01 | issue slicing guidance | 受け入れ | AC-003, EC-002, EC-003 | `phase_plan_issue.md` が vertical behavior slice、dependency order、integration checkpoint、HITL/AFK annotation、horizontal batching 禁止を説明する | provider docs diff / marker inspection | 水平分割、readiness label 誤用、integration checkpoint 欠落 | yes | inspect-only | Step Contract Closure + Test Contract Closure |
| tc-002 | S01 | TDD plan guidance | 受け入れ | AC-004 | `phase_plan_issue.md` と `authoring/issue-plan.md` が public interface / observable behavior、vertical tracer bullet、one test -> minimal implementation、step-local concrete seeds を説明する | provider docs diff / marker inspection | private method 固定、全テスト inventory 化、後付けテスト | yes | inspect-only | Step Contract Closure + Test Contract Closure |
| tc-003 | S02 | diagnosis workflow guidance | 受け入れ | AC-005, EC-004 | `workflow_issue.md` が feedback loop、reproduction、ranked hypotheses、targeted instrumentation、instrumentation cleanup、regression evidence、report ledger を説明する | provider docs diff / marker inspection | 再現なし仮説実装、証跡なし修正 | yes | inspect-only | Step Contract Closure + Test Contract Closure |
| tc-004 | S03 | execution skill reminder | 受け入れ | AC-004, AC-005 | `spec-dock-issue-execution` が approved executable plan 前提を維持し、diagnosis / behavior-first TDD を workflow docs に route する | installed skill diff / marker inspection | skill guidance による readiness bypass | yes | inspect-only | Step Contract Closure + Test Contract Closure |
| tc-005 | S04 | architecture heuristic guidance | 受け入れ | AC-006 | `spec-dock-system-architect` が deep module、interface as test surface、deletion test、locality / leverage を扱い、`CONTEXT.md` authority を作らない | installed skill diff / marker inspection | 外部 authority 作成、architecture workflow 分裂 | yes | inspect-only | Step Contract Closure + Test Contract Closure |
| tc-006 | S05 | regression assertions | 回帰 | AC-003, AC-004, AC-005, AC-006 | Essential markers が unittest または structural inspection で検出される | targeted unittest / inspection command | shipped asset drift、将来の guidance 削除 | yes | covered-existing | Step Contract Closure + Test Contract Closure |
| tc-007 | S90 | dogfooding parity | 受け入れ | AC-008 | provider docs / skills と dogfooding workspace の反映状態が確認される | `spec-dock update .` or parity inspection / report evidence | provider-only drift、consumer workspace stale | yes | inspect-only | Step Contract Closure + Test Contract Closure |
| tc-008 | S99 | scope control | 否定系 | EC-001..EC-005 | runtime / CLI / new skill / GitHub label / `CONTEXT.md` / prototype lifecycle 変更が diff に含まれない | `git diff --name-only` / reviewer gates | scope creep | yes | inspect-only | Final gate evidence |
| tc-009 | S90 | ADR reflection | 受け入れ | AC-001 | accepted ADR が requirement / design / plan / report に反映され、decision と reflected_to が追跡できる | ADR front matter / canonical docs / report evidence | ADR 作成だけで反映証跡が欠ける | yes | inspect-only | Step Contract Closure + Test Contract Closure |
| tc-010 | S90 | follow-up ledger | 受け入れ | AC-007, EC-005 | `triage`、`prototype`、first-class diagnosis、CLI slicing support が follow-up として report に記録され、この Issue の implementation scope から除外される | report evidence / scope inspection | follow-up 消失、prototype lifecycle scope creep | yes | inspect-only | Step Contract Closure + Test Contract Closure |

## レビュー / QA ゲート方針
- Step review:
  - S01, S02, S03, S04, S90: `spec-reviewer`
  - S05: `code-reviewer`
- Final gates:
  - `qa-reviewer`: obligation coverage と integration test 要否を確認する。
  - issue-wide `code-reviewer`: integrated diff、tests、scope creep を確認する。
  - final `spec-reviewer`: requirement / design / plan / report / docs / implementation alignment を確認する。
- Re-review rule:
  - reviewer が `fail` の場合、該当 step を修正して fresh reviewer pass まで繰り返す。

## 実行ルール（全ステップ共通）
- この Issue の implementation は docs-only / skill-text-only / test assertion に限定する。
- Observed evidence は `report.md` に記録し、`plan.md` へ実行結果を追記しない。
- Runtime / CLI / GitHub integration / new skill directory / prototype lifecycle が必要になった場合は stop し、plan amendment と re-review を先に行う。
- Delegated worker output は final authority ではない。main orchestrator が diff と evidence を確認して `report.md` へ統合する。

## 実装ステップ

### 実装ステップ S01 — Issue plan / TDD / slicing discipline docs
- 振る舞いの目標:
  - Issue plan guidance が `to-issues` と `tdd` の有効要素を spec-dock-native な plan discipline として説明する。
- design 参照:
  - `採用分類`, `ディレクトリ / ファイル変更計画`, `要件 → 設計マッピング`
- 依存:
  - approved requirement / design
- unblock:
  - S03, S05
- 対象ファイル:
  - `src/spec_dock/assets/spec_dock/docs/phase_plan_issue.md`
  - `src/spec_dock/assets/spec_dock/docs/authoring/issue-plan.md`
- 計画済み契約:
  - scope:
    - Epic -> Issue slicing guidance と Issue plan TDD guidance を docs に追加 / 補強する。
  - テスト義務:
    - closure id: `tc-001`, `tc-002`
    - coverage rationale: AC-003 / AC-004 / EC-002 / EC-003 は docs wording が source of truth なので inspect-only で閉じる。
  - Red / 代替証跡の要件:
    - docs-only / inspect-only:
      - code test を先に書かない理由: policy text の追加であり runtime behavior ではないため。
      - 代替 evidence path: docs diff と marker inspection。
  - 実装範囲:
    - allowed paths:
      - `src/spec_dock/assets/spec_dock/docs/phase_plan_issue.md`
      - `src/spec_dock/assets/spec_dock/docs/authoring/issue-plan.md`
    - forbidden changes:
      - runtime / CLI / test / installed skill / dogfooding copies の変更。
  - Green 検証:
    - `rg "vertical behavior slice|dependency order|integration checkpoint|HITL|AFK|public interface / observable behavior|vertical tracer bullet|horizontal batching" src/spec_dock/assets/spec_dock/docs/phase_plan_issue.md src/spec_dock/assets/spec_dock/docs/authoring/issue-plan.md`
  - Refactor / cleanup ガードレール:
    - 既存 heading / lifecycle policy を大きく組み替えない。
  - closure 証跡要件:
    - Step Contract Closure: `tc-001`, `tc-002`
    - Test Contract Closure: inspect-only evidence
    - Closure Coverage: AC-003 / AC-004 mapped
  - report 証跡の記録先:
    - `Step Contract Closure`, `Test Contract Closure`, `Closure Coverage`, `Reviewer Gate Status`
  - amendment trigger:
    - New CLI enforcement, new template schema, new issue slicing command が必要になった場合。

#### 委任契約（delegation contract）
- 委任ロール:
  - `doc-writer`
- 入力 docs:
  - `requirement.md`, `design.md`, `plan.md`, `workflow_issue.md`, `phase_plan_issue.md`, `authoring/issue-plan.md`
- 許可 paths:
  - S01 target files only
- 禁止 changes:
  - S01 target files 以外の変更、direct import、新規 skill、runtime / CLI 変更。
- 受け入れ条件:
  - `tc-001`, `tc-002` が close できる。
- 必須 tests または docs-only verification:
  - S01 Green 検証の `rg` marker inspection。
- reviewer focus:
  - spec-reviewer docs/spec alignment
- 必須出力:
  - changed files, verification result, unresolved risks, `Ledger Note` or no material decision statement
- 停止条件:
  - docs だけでは AC-003 / AC-004 を満たせず runtime/template enforcement が必要になった場合。

#### 具体テストケース一覧

- `tc-s01-001` inspect-only: Issue slicing guidance が AC-003 を閉じる
  - 前提: `phase_plan_issue.md` が Issue plan philosophy を所有している。
  - 操作: vertical behavior slice、dependency order、integration checkpoint、HITL/AFK annotation、horizontal batching 禁止の guidance を追加する。
  - 期待結果: HITL/AFK は readiness label ではなく annotation として読め、Issue boundary は vertical slice と dependency order で説明される。
  - 失敗検出: dependency order / integration checkpoint / HITL-AFK-as-annotation のいずれかが docs から欠ける回帰を検出する。
  - 検証方法: `rg` marker inspection と spec-reviewer。
  - 関連 closure id: `tc-001`

- `tc-s01-002` inspect-only: TDD guidance が AC-004 を閉じる
  - 前提: `phase_plan_issue.md` と `authoring/issue-plan.md` が plan semantics を所有している。
  - 操作: public interface / observable behavior、vertical tracer bullet、one test -> minimal implementation、step-local concrete seeds を追加 / 補強する。
  - 期待結果: 実装者が private method や水平 batch ではなく、観測可能な behavior test から開始できる。
  - 失敗検出: plan guidance が full test inventory や implementation-detail test 固定に戻る回帰を検出する。
  - 検証方法: `rg` marker inspection と spec-reviewer。
  - 関連 closure id: `tc-002`

#### ステップ完了契約
- closure id:
  - `tc-001`, `tc-002`
- close 条件:
  - S01 marker inspection が通り、spec-reviewer が pass する。
- 検証 evidence:
  - `rg` marker inspection
- report evidence:
  - Step Contract Closure / Test Contract Closure / Closure Coverage
- 残リスク:
  - Guidance-only で enforcement は弱い。

#### ステップゲート
- step reviewer gate:
  - reviewer: spec-reviewer
  - pass 条件: `review_status: pass`
- commit / no-op gate:
  - closure 状態: committed
  - commit 範囲: S01 target files

### 実装ステップ S02 — Issue workflow / diagnosis discipline docs
- 振る舞いの目標:
  - Issue execution workflow が bug / performance / unknown failure に対する feedback-loop-first discipline を説明する。
- design 参照:
  - AC-005 mapping
- 依存:
  - approved requirement / design
- unblock:
  - S03, S05
- 対象ファイル:
  - `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
- 計画済み契約:
  - scope:
    - diagnosis loop を approved docs / executable plan / report evidence の中に位置付ける。
  - テスト義務:
    - closure id: `tc-003`
    - coverage rationale: workflow policy text が AC-005 の source of truth になるため inspect-only。
  - Red / 代替証跡の要件:
    - docs-only / inspect-only:
      - code test を置かない理由: runtime behavior ではなく workflow text の変更。
      - 代替 evidence path: docs diff / marker inspection。
  - 実装範囲:
    - allowed paths:
      - `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
    - forbidden changes:
      - lifecycle command / completion policy の意味変更、runtime / CLI 変更。
  - Green 検証:
    - `rg "feedback loop|reproduction|hypotheses|instrumentation cleanup|regression evidence|report.md" src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
  - Refactor / cleanup ガードレール:
    - 既存 issue workflow の completion policy を再構成しない。
  - closure 証跡要件:
    - Step Contract Closure: `tc-003`
    - Test Contract Closure: inspect-only evidence
  - report 証跡の記録先:
    - `Step Contract Closure`, `Test Contract Closure`, `Reviewer Gate Status`
  - amendment trigger:
    - diagnosis を first-class skill / new workflow にする必要が出た場合。

#### 委任契約（delegation contract）
- 委任ロール:
  - `doc-writer`
- 入力 docs:
  - `requirement.md`, `design.md`, `plan.md`, `workflow_issue.md`
- 許可 paths:
  - S02 target file only
- 禁止 changes:
  - runtime / CLI / new skill / GitHub label / prototype lifecycle
- 受け入れ条件:
  - `tc-003` が close できる。
- 必須 tests または docs-only verification:
  - S02 Green 検証の `rg` marker inspection。
- reviewer focus:
  - spec-reviewer docs/spec alignment
- 必須出力:
  - changed files, verification result, unresolved risks, `Ledger Note` or no material decision statement
- 停止条件:
  - approved plan 前に diagnosis 実装を開始するように読める変更が必要になった場合。

#### 具体テストケース一覧

- `tc-s02-001` inspect-only: Diagnosis workflow が AC-005 を閉じる
  - 前提: `workflow_issue.md` が Issue execution policy と report evidence を所有している。
  - 操作: feedback loop、reproduction、ranked hypotheses、targeted instrumentation、instrumentation cleanup、regression evidence を report evidence として追加する。
  - 期待結果: bug / performance Issue で再現や仮説なしに修正へ進むことを避けられる。
  - 失敗検出: diagnosis guidance が approved plan を迂回する、または report evidence を要求しない回帰を検出する。
  - 検証方法: `rg` marker inspection と spec-reviewer。
  - 関連 closure id: `tc-003`

#### ステップ完了契約
- closure id:
  - `tc-003`
- close 条件:
  - S02 marker inspection が通り、spec-reviewer が pass する。
- 検証 evidence:
  - `rg` marker inspection
- report evidence:
  - Step Contract Closure / Test Contract Closure
- 残リスク:
  - Future first-class diagnosis skill は別 Issue。

#### ステップゲート
- step reviewer gate:
  - reviewer: spec-reviewer
  - pass 条件: `review_status: pass`
- commit / no-op gate:
  - closure 状態: committed
  - commit 範囲: S02 target file

### 実装ステップ S03 — Issue execution skill reminder
- 振る舞いの目標:
  - Execution skill が concise reminder として diagnosis / behavior-first TDD を workflow docs に route する。
- design 参照:
  - AC-004, AC-005 mapping
- 依存:
  - S01, S02
- unblock:
  - S05
- 対象ファイル:
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md`
- 計画済み契約:
  - scope:
    - skill reminder に短い guidance を追加する。
  - テスト義務:
    - closure id: `tc-004`
    - coverage rationale: installed skill text is user-facing agent guidance.
  - Red / 代替証跡の要件:
    - docs-only / inspect-only:
      - code test を置かない理由: skill text change。
      - 代替 evidence path: skill diff / marker inspection。
  - 実装範囲:
    - allowed paths:
      - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md`
    - forbidden changes:
      - workflow policy の full copy、new skill、runtime / CLI。
  - Green 検証:
    - `rg "feedback loop|public interface / observable behavior|approved|plan.md" src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md`
  - Refactor / cleanup ガードレール:
    - Skill は concise reminder のままにする。
  - closure 証跡要件:
    - Step Contract Closure: `tc-004`
  - report 証跡の記録先:
    - `Step Contract Closure`, `Test Contract Closure`, `Reviewer Gate Status`
  - amendment trigger:
    - skill が workflow docs の policy を重複定義し始める場合。

#### 委任契約（delegation contract）
- 委任ロール:
  - `doc-writer`
- 入力 docs:
  - `workflow_issue.md`, `phase_plan_issue.md`, `authoring/issue-plan.md`, S03 target file
- 許可 paths:
  - S03 target file only
- 禁止 changes:
  - new skill / runtime / CLI / canonical issue docs
- 受け入れ条件:
  - `tc-004` が close できる。
- 必須 tests または docs-only verification:
  - S03 Green 検証の `rg` marker inspection。
- reviewer focus:
  - spec-reviewer docs/spec alignment
- 必須出力:
  - changed files, verification result, unresolved risks, `Ledger Note` or no material decision statement
- 停止条件:
  - Execution skill だけで policy を完結させる必要が出た場合。

#### 具体テストケース一覧

- `tc-s03-001` inspect-only: Execution skill reminder が approved plan 前提を維持する
  - 前提: `spec-dock-issue-execution/SKILL.md` は workflow docs への reminder である。
  - 操作: feedback loop と public interface / observable behavior TDD を approved `plan.md` 前提の guidance として追加する。
  - 期待結果: skill 単体が readiness bypass にならず、詳細は workflow docs に route される。
  - 失敗検出: skill が approved artifacts なしの実装開始を許す回帰を検出する。
  - 検証方法: `rg` marker inspection と spec-reviewer。
  - 関連 closure id: `tc-004`

#### ステップ完了契約
- closure id:
  - `tc-004`
- close 条件:
  - S03 marker inspection が通り、spec-reviewer が pass する。
- 検証 evidence:
  - `rg` marker inspection
- report evidence:
  - Step Contract Closure / Test Contract Closure
- 残リスク:
  - Skill reminder が長くなりすぎる場合は docs 側へ戻す。

#### ステップゲート
- step reviewer gate:
  - reviewer: spec-reviewer
  - pass 条件: `review_status: pass`
- commit / no-op gate:
  - closure 状態: committed
  - commit 範囲: S03 target file

### 実装ステップ S04 — System architect skill guidance
- 振る舞いの目標:
  - Architecture analysis heuristic を system-architect skill に追加する。
- design 参照:
  - AC-006 mapping
- 依存:
  - approved design
- unblock:
  - S05
- 対象ファイル:
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-system-architect/SKILL.md`
- 計画済み契約:
  - scope:
    - deep module、interface as test surface、deletion test、locality / leverage を source-grounded design heuristic として追加する。
  - テスト義務:
    - closure id: `tc-005`
    - coverage rationale: architecture guidance が AC-006 の source of truth になる。
  - Red / 代替証跡の要件:
    - docs-only / inspect-only:
      - code test を置かない理由: skill text change。
      - 代替 evidence path: skill diff / marker inspection。
  - 実装範囲:
    - allowed paths:
      - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-system-architect/SKILL.md`
    - forbidden changes:
      - `CONTEXT.md` authority、external architecture source of truth、新規 skill。
  - Green 検証:
    - `rg "deep module|interface as test surface|deletion test|locality|leverage|CONTEXT.md" src/spec_dock/assets/install_root/.agents/skills/spec-dock-system-architect/SKILL.md`
  - Refactor / cleanup ガードレール:
    - Existing source-of-truth and operating boundary sectionsを壊さない。
  - closure 証跡要件:
    - Step Contract Closure: `tc-005`
  - report 証跡の記録先:
    - `Step Contract Closure`, `Test Contract Closure`, `Reviewer Gate Status`
  - amendment trigger:
    - External architecture authority を追加する必要が出た場合。

#### 委任契約（delegation contract）
- 委任ロール:
  - `doc-writer`
- 入力 docs:
  - `design.md`, ADR, S04 target file
- 許可 paths:
  - S04 target file only
- 禁止 changes:
  - `CONTEXT.md` creation / docs authority変更 / new skill / runtime
- 受け入れ条件:
  - `tc-005` が close できる。
- 必須 tests または docs-only verification:
  - S04 Green 検証の `rg` marker inspection。
- reviewer focus:
  - spec-reviewer docs/spec alignment
- 必須出力:
  - changed files, verification result, unresolved risks, `Ledger Note` or no material decision statement
- 停止条件:
  - skill の operating boundary と矛盾する authority 追加が必要になった場合。

#### 具体テストケース一覧

- `tc-s04-001` inspect-only: Architecture heuristic が AC-006 を閉じる
  - 前提: `spec-dock-system-architect/SKILL.md` は source-grounded design proposal の operating boundary を所有する。
  - 操作: deep module、interface as test surface、deletion test、locality / leverage を heuristic として追加し、`CONTEXT.md` authority を作らないことを明記する。
  - 期待結果: architecture review 語彙は増えるが、正本は active docs / ADR / discussions / source / tests に保たれる。
  - 失敗検出: system architect が `CONTEXT.md` や別 authority を作る回帰を検出する。
  - 検証方法: `rg` marker inspection と spec-reviewer。
  - 関連 closure id: `tc-005`

#### ステップ完了契約
- closure id:
  - `tc-005`
- close 条件:
  - S04 marker inspection が通り、spec-reviewer が pass する。
- 検証 evidence:
  - `rg` marker inspection
- report evidence:
  - Step Contract Closure / Test Contract Closure
- 残リスク:
  - Vocabulary だけでは architecture quality を強制できない。

#### ステップゲート
- step reviewer gate:
  - reviewer: spec-reviewer
  - pass 条件: `review_status: pass`
- commit / no-op gate:
  - closure 状態: committed
  - commit 範囲: S04 target file

### 実装ステップ S05 — Content / scaffold assertions
- 振る舞いの目標:
  - Essential guidance markers が shipped asset regression で落ちないようにする。
- design 参照:
  - Test strategy
- 依存:
  - S01, S02, S03, S04
- unblock:
  - S90, S99
- 対象ファイル:
  - `tests/test_init_update.py`
- 計画済み契約:
  - scope:
    - Existing unittest style に合わせ、主要 marker の presence assertion を最小追加する。
  - テスト義務:
    - closure id: `tc-006`
    - coverage rationale: docs / skill guidance は runtime behavior ではないが、shipped asset drift は regression risk。
  - Red / 代替証跡の要件:
    - covered-existing:
      - 既存 scaffold / install_root asset tests に content assertion を追加または既存 test sensitivity を示す。
  - 実装範囲:
    - allowed paths:
      - `tests/test_init_update.py`
    - forbidden changes:
      - production docs / skills / runtime / CLI
  - Green 検証:
    - `python -m unittest tests.test_init_update.TestInitUpdate.test_issue_142_matt_pocock_phase_discipline_contract_assets`
  - Refactor / cleanup ガードレール:
    - Test helper の大規模 refactor はしない。
  - closure 証跡要件:
    - Step Contract Closure: `tc-006`
  - report 証跡の記録先:
    - `Step Contract Closure`, `Test Contract Closure`, `Reviewer Gate Status`
  - amendment trigger:
    - Existing tests が scaffold content を扱っておらず、新しい test harness が必要になる場合。

#### 委任契約（delegation contract）
- 委任ロール:
  - `dev-coder`
- 入力 docs:
  - `requirement.md`, `design.md`, `plan.md`, changed provider docs / skills, existing tests
- 許可 paths:
  - `tests/test_init_update.py`
- 禁止 changes:
  - production docs / skills / runtime / CLI
- 受け入れ条件:
  - `tc-006` が close できる。
- 必須 tests または docs-only verification:
  - `python -m unittest tests.test_init_update.TestInitUpdate.test_issue_142_matt_pocock_phase_discipline_contract_assets`
- reviewer focus:
  - code-reviewer for test quality / maintainability / scope.
- 必須出力:
  - changed files, command result, unresolved risks, `Ledger Note` or no material decision statement
- 停止条件:
  - test addition requires production behavior change.

#### 具体テストケース一覧

- `tc-s05-001` covered-existing: Essential guidance markers are asserted
  - 前提: S01..S04 の provider docs / installed skills が更新済みである。
  - 操作: Existing scaffold / asset assertion tests に marker checks を追加する。
  - 期待結果: AC-003 の dependency order / integration checkpoint / HITL/AFK annotation を含む essential markers が regression で検出される。
  - 失敗検出: guidance text が削除されたとき targeted unittest が fail する。
  - 検証方法: `python -m unittest tests.test_init_update.TestInitUpdate.test_issue_142_matt_pocock_phase_discipline_contract_assets`
  - 関連 closure id: `tc-006`

#### ステップ完了契約
- closure id:
  - `tc-006`
- close 条件:
  - targeted unittest が成功し、code-reviewer が pass する。
- 検証 evidence:
  - `python -m unittest tests.test_init_update.TestInitUpdate.test_issue_142_matt_pocock_phase_discipline_contract_assets`
- report evidence:
  - Step Contract Closure / Test Contract Closure
- 残リスク:
  - Phrase-level assertion は wording change に弱いため、marker は最小限にする。

#### ステップゲート
- step reviewer gate:
  - reviewer: code-reviewer
  - pass 条件: `review_status: pass`
- commit / no-op gate:
  - closure 状態: committed
  - commit 範囲: `tests/test_init_update.py`

### ドキュメント影響の解消ステップ S90（docs impact resolution / docs refresh）
- 対象:
  - Provider docs / provider installed skills / dogfooding workspace copies / canonical issue report
- 計画済み契約:
  - scope:
    - Provider-side source of truth の変更を dogfooding workspace に反映する。
    - Accepted ADR の反映証跡と follow-up candidates を `report.md` に記録する。
  - Red / 代替証跡の要件:
    - inspect-only:
      - docs / skill / report evidence step であり、runtime code test は置かない。
      - 代替 evidence path: update command、diff inspection、ADR / report inspection。
  - 実装範囲:
    - allowed paths:
      - `spec-dock/docs/phase_plan_issue.md`
      - `spec-dock/docs/authoring/issue-plan.md`
      - `spec-dock/docs/workflow_issue.md`
      - `.agents/skills/spec-dock-issue-execution/SKILL.md`
      - `.agents/skills/spec-dock-system-architect/SKILL.md`
      - `spec-dock/active/issue/report.md`
    - forbidden changes:
      - provider docs / skills / tests / runtime / CLI / new skill directory / GitHub label configuration / `CONTEXT.md`。
  - Green 検証:
    - `./spec-dock/scripts/spec-dock update .`
    - `git diff --name-only -- spec-dock/docs .agents/skills spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00067-installed-layout-aligned-asset-source-structure-for-agent-tooling/issues/iss-00142-matt-pocock-skill-adoption-analysis/report.md`
    - `rg "matt-pocock-skills-as-spec-dock-phase-discipline|triage|prototype|first-class.*diagnosis|CLI slicing" spec-dock/active/issue/report.md spec-dock/active/issue/discussions/20260530t094323z-adr-matt-pocock-skills-as-spec-dock-phase-discipline.md`
  - no-op path:
    - If `spec-dock update .` produces no dogfooding diff, record the command result, provider/dogfooding parity rationale, and accepted no-op evidence in `report.md`.
  - closure 証跡要件:
    - Step Contract Closure: `tc-007`, `tc-009`, `tc-010`
    - Test Contract Closure: inspect-only evidence
    - Closure Coverage: AC-001 / AC-007 / AC-008 mapped
  - report 証跡の記録先:
    - Evidence Adoption Ledger, Step Contract Closure, Test Contract Closure, Closure Coverage, Reviewer Gate Status
  - amendment trigger:
    - Dogfooding refresh requires runtime / CLI / installer behavior changes, or follow-up candidates require implementation in this Issue.
- doc update owner:
  - `doc-writer` when dogfooding docs / skill refresh requires manual doc updates.
- spec/doc review:
  - reviewer: spec-reviewer
  - pass 条件: docs が requirement / design / plan と整合し、未解決の必須 docs 影響が残っていない。
- 具体テストケース:
  - `tc-s90-001` inspect-only: dogfooding parity が確認される
    - 前提: S01..S05 が完了している。
    - 操作: `./spec-dock/scripts/spec-dock update .` を実行し、provider docs / installed skills と dogfooding copies の反映状態を確認する。
    - 期待結果: 必要な dogfooding updates が反映済み、または provider-only とする根拠が report に残る。
    - 失敗検出: provider asset と consumer workspace の意図しない drift を検出する。
    - 検証方法: `./spec-dock/scripts/spec-dock update .`, diff inspection, spec-reviewer。
    - 関連 closure id: `tc-007`
  - `tc-s90-002` inspect-only: ADR reflection が AC-001 を閉じる
    - 前提: accepted ADR が存在し、requirement / design / plan がその decision を参照している。
    - 操作: `report.md` の Evidence Adoption Ledger / Spec Authoring Gate に ADR と reviewer pass を記録する。
    - 期待結果: ADR の decision、derived_from、reflected_to、report evidence が追跡できる。
    - 失敗検出: ADR は存在するが canonical docs / report への反映証跡がない回帰を検出する。
    - 検証方法: `rg "20260530t094323z-adr|Spec Authoring Gate|review_status: pass" spec-dock/active/issue/report.md spec-dock/active/issue/*.md`
    - 関連 closure id: `tc-009`
  - `tc-s90-003` inspect-only: follow-up candidates が AC-007 を閉じる
    - 前提: この Issue では `triage`、`prototype`、first-class diagnosis、CLI slicing support を実装しない。
    - 操作: follow-up candidates と scope 外理由を `report.md` に記録する。
    - 期待結果: follow-up は失われず、この Issue の diff には prototype lifecycle / triage label model が混入しない。
    - 失敗検出: follow-up が report に残らない、または implementation scope に混入する回帰を検出する。
    - 検証方法: `rg "triage|prototype|first-class.*diagnosis|CLI slicing" spec-dock/active/issue/report.md`
    - 関連 closure id: `tc-010`
  - step gate:
    - reviewer: spec-reviewer
    - pass 条件: `review_status: pass`
  - commit / no-op gate:
    - closure 状態: committed または approved-no-op
    - no-op 条件: dogfooding files に差分がなく、report evidence が S90 closure を満たす。

### 最終品質ゲートステップ S99（final quality gate）
- branch diff 範囲:
  - ADR / canonical issue docs / provider docs / installed skill guidance / tests / dogfooding updates / report evidence。
- 必須 validation:
  - `git diff --check`
  - `./spec-dock/scripts/spec-dock validate`
  - `python -m unittest tests.test_init_update.TestInitUpdate.test_issue_142_matt_pocock_phase_discipline_contract_assets`
  - `git diff --name-only` scope inspection for no runtime / CLI / new skill / GitHub label / `CONTEXT.md` / prototype lifecycle changes
- final QA gate:
  - reviewer: qa-reviewer
  - 範囲: Issue 全体の obligation coverage と integration test 要否
  - pass 条件: reviewer pass
- final code review ゲート:
  - reviewer: code-reviewer
  - 範囲: issue-wide integrated diff、test assertions、scope creep、保守性
  - pass 条件: `review_status: pass`
- final spec review ゲート:
  - reviewer: spec-reviewer
  - 範囲: requirement / design / plan / report / implementation / tests / docs 整合
  - pass 条件: reviewer pass
- final commit gate:
  - commit 範囲:
    - all completed implementation steps and report evidence
  - final report ledger:
    - Step Contract Closure, Test Contract Closure, Closure Coverage, Reviewer Gate Status, Final QA / Code / Spec Review Gate, PR Delivery Gate, Merge Preparation Gate
  - post-commit external evidence destination:
    - final response / PR body / GitHub issue comment
- PR Delivery Gate:
  - 実施タイミング: final commit gates 後、`issue finish` 前。
  - required evidence:
    - PR URL
    - selected base
    - base-resolution source
    - base-resolution conflict / handling
    - draft / ready decision
    - head branch
    - head SHA
    - issue linkage
    - existing PR reuse / new PR creation decision
  - report 記録先: `PR Delivery Gate`
- Merge Preparation Gate:
  - 実施タイミング: PR Delivery Gate 後、`issue finish` 前。
  - required evidence:
    - PR open state
    - monitor status
    - latest monitored head SHA
    - fix loop count / history
    - required check status
    - non-required check status and waiver evidence
    - blocking review status
    - merge conflict / visible merge blocker status
    - unresolved review-thread limitation status
    - unresolved blockers
    - final merge-prepared decision
  - report 記録先: `Merge Preparation Gate`
- lifecycle boundary:
  - S99 は PR Delivery Gate と Merge Preparation Gate の evidence を report に残すところまでを final completion gate とする。
  - `issue finish` は、workflow completion evidence と PR / merge-preparation evidence が揃った後にだけ実行できる。
- 具体テストケース:
  - `tc-s99-001` inspect-only: scope creep がない
    - 前提: S01..S90 が完了している。
    - 操作: integrated diff を確認する。
    - 期待結果: runtime / CLI / new skill / GitHub label / `CONTEXT.md` / prototype lifecycle の変更が含まれない。
    - 失敗検出: forbidden scope が diff に混入する回帰を検出する。
    - 検証方法: `git diff --name-only`, qa-reviewer, code-reviewer, spec-reviewer。
    - 関連 closure id: `tc-008`

## 最終完了条件
- AC/EC 達成:
  - `tc-001`..`tc-010` が report evidence で閉じている。
- docs 影響解決:
  - S90 が pass している。
- 全 implementation step 完了:
  - S01..S05 committed / approved-no-op。
- final quality gate pass:
  - qa-reviewer: pass
  - issue-wide code-reviewer: pass
  - final spec-reviewer: pass
- validation:
  - `git diff --check` pass
  - `./spec-dock/scripts/spec-dock validate` pass
  - `python -m unittest tests.test_init_update.TestInitUpdate.test_issue_142_matt_pocock_phase_discipline_contract_assets` pass
- delivery:
  - PR Delivery Gate pass evidence が `report.md` にある。
  - Merge Preparation Gate pass evidence が `report.md` にある。
  - `issue finish` 前 evidence が揃っている。
