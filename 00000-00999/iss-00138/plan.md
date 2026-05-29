---
種別: 実装計画書（Issue）
ID: "iss-00138"
タイトル: "Split Issue Planning and Execution Skills"
関連GitHub: ["#138"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-05-29"
依存: ["requirement.md", "design.md"]
親: ["epic-00112", "init-local-00003"]
---

# iss-00138 Split Issue Planning and Execution Skills — 実装計画（実行契約 / Execution Contract）

この計画は、Issue planning と Issue execution の skill routing を分離するための実行契約である。Provider-side asset を正本として変更し、dogfooding workspace は provider から反映・検査する parity surface として扱う。実行結果、逸脱、reviewer verdict、commit/no-op evidence は `report.md` に記録する。

## この計画で満たす要件ID
- AC:
  - AC-001: Issue planning skill が追加される
  - AC-002: Planning skill は既存 authority boundary を保つ
  - AC-003: Execution skill は implementation boundary を明確にする
  - AC-004: Hub skill が Issue planning / execution を正しく route する
  - AC-005: Shipped docs と tests が新しい skill split を検出する
  - AC-006: Existing workflow semantics は維持される
- EC:
  - EC-001: `$spec-dock-issue-execution` だけが指定され、Issue docs が template または gap あり
  - EC-002: `$spec-dock-issue-planning` と `$spec-dock-issue-execution` が同時指定される
  - EC-003: `system-architect` / `implementation-planner` draft が作られる
  - EC-004: 新規 skill asset が provider-side にだけ存在する
- 制約:
  - Canonical docs は main orchestrator single-writer authority。
  - `workflow_spec_authoring.md` の fresh `spec-reviewer` gate を維持する。
  - `authoring/issue-plan.md` を Issue plan field semantics / executable step schema の正本として扱う。
  - Dogfooding `.agents/skills` / `spec-dock/docs` は primary source ではなく parity output。

## 依存関係から導く実装順序
- 依存関係の正本:
  - `design.md` の `依存関係分析`、`Module Dependency Diagram`、`ディレクトリ / ファイル変更計画`
- 順序ルール:
  - Provider-side skill asset を先に固定し、その後に hub/docs/tests/dogfooding parity を追随させる。
  - Execution boundary は planning skill / hub route と矛盾しないよう順に閉じる。
  - Tests は最終 wording と file inventory が決まってから更新する。
  - Dogfooding parity は provider-side source が固定された後に検証する。
- step 依存サマリー:
  - S01:
    - 依存: reviewer-pass requirement/design
    - unblock: S02, S04, S05, S06
    - 対象ファイル: provider-side new planning skill
  - S02:
    - 依存: S01
    - unblock: S05, S06
    - 対象ファイル: provider-side hub skill
  - S03:
    - 依存: S01/S02 の boundary
    - unblock: S05, S06
    - 対象ファイル: provider-side execution skill
  - S04:
    - 依存: S01-S03
    - unblock: S05, S06, S90
    - 対象ファイル: provider-side shipped docs
  - S05:
    - 依存: S01-S04
    - unblock: S99
    - 対象ファイル: tests
  - S06:
    - 依存: S01-S05
    - unblock: S90, S99
    - 対象ファイル: dogfooding parity outputs only

## ステップ一覧
- S01: Provider-side `spec-dock-issue-planning` skill を追加する
  - 観測可能な振る舞い: installed assets が Issue planning leaf skill を含む
  - 依存: requirement/design reviewer pass
  - unblock: hub routing、docs、tests、parity
  - 対象ファイル: `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md`
  - 閉じる要件: AC-001, AC-002, EC-003
  - レビューゲート: `spec-reviewer`
- S02: Hub skill の Issue planning / execution route を分割する
  - 観測可能な振る舞い: Issue planning は planning skill、Issue execution は execution skill に route される
  - 依存: S01
  - unblock: docs/tests/parity
  - 対象ファイル: `src/spec_dock/assets/install_root/.agents/skills/spec-driven-tdd-workflow/SKILL.md`
  - 閉じる要件: AC-002, AC-004, AC-006, EC-002, EC-003
  - レビューゲート: `spec-reviewer`
- S03: Issue execution skill の境界を実装専用に締める
  - 観測可能な振る舞い: execution skill が approved/reviewer-pass planning artifacts を前提にし、gap を planning / clarification に戻す
  - 依存: S01/S02
  - unblock: docs/tests/parity
  - 対象ファイル: `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md`
  - 閉じる要件: AC-003, AC-006, EC-001
  - レビューゲート: `spec-reviewer`
- S04: Provider-side shipped docs を skill split に合わせる
  - 観測可能な振る舞い: README / workflow_issue が planning / execution を別 leaf skill として案内する
  - 依存: S01-S03
  - unblock: tests/parity/docs impact
  - 対象ファイル: `src/spec_dock/assets/spec_dock/docs/README.md`, `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
  - 閉じる要件: AC-005, AC-006, EC-001, EC-002
  - レビューゲート: `spec-reviewer`
- S05: Tests と managed asset expectations を更新する
  - 観測可能な振る舞い: new skill / routing / docs / wrapper / parity drift を tests が検出する
  - 依存: S01-S04
  - unblock: S06/S99
  - 対象ファイル: `tests/test_init_update.py`, `tests/cli_runtime/harness.py`, `tests/cli_runtime/test_wrappers.py`
  - 閉じる要件: AC-001, AC-004, AC-005, AC-006, EC-004
  - レビューゲート: `code-reviewer`
- S06: Dogfooding parity を refresh / inspection で解決する
  - 観測可能な振る舞い: checked-in dogfooding `.agents/skills` / `spec-dock/docs` が provider source と一致する、または drift detection evidence により checked-in parity update 不要が証明される
  - 依存: S01-S05
  - unblock: S90/S99
  - 対象ファイル: dogfooding parity output files only
  - 閉じる要件: AC-005, EC-004
  - レビューゲート: `spec-reviewer`; scaffold behavior が変わる場合は `code-reviewer`
- S90: Docs impact resolution
- S99: Final quality gate

## 要件 ↔ ステップ対応
- AC-001 -> S01, S05, S06
- AC-002 -> S01, S02, S99
- AC-003 -> S03, S05, S99
- AC-004 -> S02, S05, S99
- AC-005 -> S04, S05, S06, S90, S99
- AC-006 -> S01-S06, S90, S99
- EC-001 -> S03, S04, S05
- EC-002 -> S02, S04, S05
- EC-003 -> S01, S02, S99
- EC-004 -> S05, S06

## 仕様固定クロージャ索引（Spec-Locked Closure Index）

| 識別子（ID） | ステップ | スライス | 種別 | 仕様リンク | 固定する期待値 | 観測可能な入力 / 状態 | 防ぐ bug class | 必須 | 証跡レベル | クロージャ証跡 |
|---|---|---|---|---|---|---|---|---|---|---|
| tc-001 | S01 | planning skill asset | acceptance | AC-001, AC-002, EC-003 | Provider-side `spec-dock-issue-planning/SKILL.md` が存在し、spec authoring / clarification / issue lifecycle / phase plan / `authoring/issue-plan.md` を正本へ route する | provider skill asset text | Issue planning が execution skill に埋もれる回帰 | yes | inspect-only | Step/Test closure in `report.md` |
| tc-002 | S02 | hub routing | acceptance | AC-004, EC-002 | Hub が Issue planning と execution を別 route にし、planning + execution 同時指定時も gate sequencing を飛ばさない | hub skill text | reviewer gate bypass の誤誘導 | yes | inspect-only | Step/Test closure in `report.md` |
| tc-003 | S03 | execution boundary | acceptance | AC-003, EC-001 | Execution skill が approved/reviewer-pass requirement/design/plan と executable `plan.md` を前提にし、gap を planning / clarification に戻す | execution skill text | 実装中の未承認仕様仮定 | yes | inspect-only | Step/Test closure in `report.md` |
| tc-004 | S04 | shipped docs split | acceptance | AC-005, AC-006 | Shipped docs が planning / execution split を案内し、completion / PR / finish policy を再設計しない | provider README / workflow_issue docs | docs が古い Issue entrypoint を固定する回帰 | yes | inspect-only | Step/Test closure in `report.md` |
| tc-005 | S05 | managed asset tests | regression | AC-001, AC-005, EC-004 | Tests が new skill の managed asset、installed output、routing text、docs list を検出する | focused unittest commands | provider-only 追加や init/update drift の見逃し | yes | red-required | Failing-first or equivalent test sensitivity + Green command in `report.md` |
| tc-006 | S05 | authority text tests | regression | AC-002, AC-006, EC-003 | Tests / assertions が direct canonical authority、reviewer pass 代替、full automation を許さない wording を検出する | text assertions | delegated draft と canonical authority の混同 | yes | red-required | Test closure in `report.md` |
| tc-007 | S06 | dogfooding parity | acceptance | AC-005, EC-004 | Dogfooding `.agents/skills` / `spec-dock/docs` が provider source と一致する、または drift detection evidence により checked-in parity update 不要が証明される | parity diff / tests / update output | checked-in dogfooding drift | yes | manual-required | Parity evidence in `report.md` |
| tc-008 | S90 | docs impact | acceptance | AC-005, AC-006 | docs/templates/README/workflow/skill impacts が解消され、docs/spec alignment が reviewer pass する | S90 evidence | docs impact の閉じ忘れ | yes | manual-required | S90 table in `report.md` |
| tc-009 | S99 | final quality | acceptance | all AC/EC | Focused tests、validate/sync、final QA/code/spec review が pass する | commands + reviewers | partial implementation readiness claim | yes | manual-required | Final Quality Gate in `report.md` |

## レビュー / QA ゲート方針
- RG1 step review:
  - docs-only / skill-text-only step: `spec-reviewer`
  - tests / scaffold behavior step: `code-reviewer`
  - mixed step: split first。分けられない場合は `code-reviewer` と `spec-reviewer` の両方を必須にする。
- QG1 final QA:
  - reviewer: `qa-reviewer`
  - 範囲: Issue 全体の obligation coverage、missing high-value tests、manual / integration test 要否
- CG1 final code review:
  - reviewer: `code-reviewer`
  - 範囲: issue-wide integrated diff、provider/dogfooding parity、tests、scaffold behavior
- SG1 final spec review:
  - reviewer: `spec-reviewer`
  - 範囲: requirement / design / plan / report / implementation / tests / docs 整合

## 実行ルール（全ステップ共通）
- `plan.md` は planned contract、`report.md` は observed evidence ledger。
- 各 step は原則 `1 implementation step = 1 review scope = 1 commit`。
- Implementation 中に plan 外の仕様差分、bug class、外部 contract risk が出た場合は、`report.md` に記録し、必要なら plan amendment と re-review を先に行う。
- Provider-side source of truth を先に編集する。Dogfooding output を直接編集する場合は、provider parity refresh として scope / evidence / rationale を `report.md` に残す。

## 実装ステップ

### 実装ステップ S01 — Issue planning leaf skill を追加する
- 振る舞いの目標:
  - Provider-side installed skill assets に `spec-dock-issue-planning` が追加され、Issue requirement/design/plan authoring の入口を提供する。
- design 参照:
  - `インターフェース契約`, `ディレクトリ / ファイル変更計画`, AC-001/AC-002 mapping
- 依存:
  - Requirement/design reviewer pass
- unblock:
  - S02, S04, S05, S06
- 対象ファイル:
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md`
- 計画済み契約:
  - scope:
    - Initiative / Epic planning skill と同じ concise reminder 形式で Issue planning skill を追加する。
  - テスト義務:
    - closure id: tc-001
    - coverage rationale: new managed asset と authority boundary は workflow regression risk が高いため、inspection と later test assertion の両方で閉じる。
  - Red / 代替証跡の要件:
    - inspect-only:
      - code test は S05 で固定する。S01 では skill text の存在、frontmatter、source-of-truth references、authority boundary を inspection する。
  - 実装範囲:
    - allowed paths:
      - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md`
    - forbidden changes:
      - canonical docs、tests、runtime code、dogfooding output、Permission Profile、direct canonical authoring authority
  - Green 検証:
    - skill file inspection
  - Refactor / cleanup ガードレール:
    - Initiative / Epic planning skill の concise style を踏襲し、workflow policy を skill に複製しすぎない。
  - report 証跡の記録先:
    - Implementation Delegation Gate, Delegated Worker Evidence or Parent Implementation Exception, Step Contract Closure, Test Contract Closure, Closure Coverage, Reviewer Gate Status
  - amendment trigger:
    - `authoring/issue-plan.md` への routing を削る必要が出た場合、design amendment と re-review が必要。

#### 委任契約（delegation contract）
- 委任ロール: `doc-writer`
- scope: S01 provider-side planning skill asset only
- source of truth: `requirement.md`, `design.md`, `workflow_spec_authoring.md`, `workflow_clarification.md`, `workflow_issue.md`, `phase_plan_issue.md`, `authoring/issue-plan.md`
- 入力 docs: `requirement.md`, `design.md`, `workflow_spec_authoring.md`, `workflow_clarification.md`, `workflow_issue.md`, `phase_plan_issue.md`, `authoring/issue-plan.md`
- 許可 paths: S01 allowed paths のみ
- 禁止 changes: implementation files、tests、canonical specs、dogfooding output
- 受け入れ条件: tc-001
- 必須 verification: docs-only inspection
- reviewer focus: `spec-reviewer`
- 必須出力: changed files、inspection result、unresolved risks、`Ledger Note` または `No material implementation decisions beyond the approved plan.`
- 停止条件: source docs conflict、allowed path 外変更が必要、authority wording が曖昧

#### 具体テストケース一覧
- `tc-s01-001` acceptance: planning skill asset が存在する
  - 前提: provider install_root skills に Issue planning skill がない。
  - 操作: `spec-dock-issue-planning/SKILL.md` を追加する。
  - 期待結果: file が存在し、frontmatter name が `spec-dock-issue-planning` である。
  - 失敗検出: new skill が provider-side managed assets に存在しない回帰を検出する。
  - 検証方法: S01 inspection、S05 unittest assertion。
  - 関連 closure id: tc-001
- `tc-s01-002` inspect-only: authority boundary が明記される
  - テスト不要理由: S01 は docs-only skill text 追加であり、structural assertion は S05 で実装する。
  - 代替検証方法: text inspection で main orchestrator ownership、delegated draft evidence、fresh reviewer gate、`authoring/issue-plan.md` routing を確認する。
  - 期待結果: direct canonical authoring authority や reviewer-pass 代替を主張しない。
  - 記録先: `report.md`
  - 関連 closure id: tc-001

#### ステップ完了契約
- closure id: tc-001
- close 条件: skill file exists, required source refs present, no authority expansion
- 検証 evidence: inspection + `spec-reviewer` pass
- report evidence: Step Contract Closure, Test Contract Closure, Closure Coverage
- 残リスク: wording regression は S05/S99 で再確認する。

#### ステップゲート
- step reviewer gate:
  - reviewer: `spec-reviewer`
  - review 範囲: skill text vs requirement/design/workflow docs
  - pass 条件: `review_status: pass`
  - re-review rule: 指摘を修正し pass まで再実行
- commit / no-op gate:
  - closure 状態: committed / approved-no-op
  - commit 範囲: S01 file only

### 実装ステップ S02 — Hub routing を Issue planning / execution に分割する
- 振る舞いの目標:
  - Hub skill が Issue planning と Issue execution を別 route として示し、planning + execution 同時指定でも gate sequencing を守る。
- design 参照:
  - `シーケンス差分`, `インターフェース契約`
- 依存: S01
- unblock: S04, S05, S06
- 対象ファイル:
  - `src/spec_dock/assets/install_root/.agents/skills/spec-driven-tdd-workflow/SKILL.md`
- 計画済み契約:
  - scope:
    - Route list / quick reminders / direct references を必要最小限更新する。
  - テスト義務:
    - closure id: tc-002
    - coverage rationale: hub wording は workflow entrypoint であり、gate bypass 誘導を防ぐ必要がある。
  - Red / 代替証跡:
    - inspect-only in S02; red-required assertion is S05.
  - 実装範囲:
    - allowed paths: target file only
    - forbidden changes: workflow policy の詳細再定義、runtime commands の過剰追加
  - Green 検証: text inspection
  - Refactor guardrail: route wording だけに限定する。
  - report 証跡の記録先: Implementation Delegation Gate, Delegated Worker Evidence or Parent Implementation Exception, Step/Test/Closure ledgers
  - amendment trigger: Issue execution を planning entrypoint として残す必要が出た場合

#### 委任契約（delegation contract）
- 委任ロール: `doc-writer`
- scope: S02 hub routing text only
- source of truth: `requirement.md`, `design.md`, `workflow_spec_authoring.md`, `workflow_clarification.md`, `workflow_issue.md`
- 入力 docs: `requirement.md`, `design.md`, `spec-driven-tdd-workflow/SKILL.md`, workflow docs
- 許可 paths: S02 target file
- 禁止 changes: S01/S03/S04/S05/S06 対象
- 受け入れ条件: tc-002
- 必須 verification: docs-only inspection
- reviewer focus: `spec-reviewer`
- 必須出力: changed files、routing evidence、unresolved risks、`Ledger Note` または `No material implementation decisions beyond the approved plan.`
- 停止条件: route wording が execution bypass を示唆する

#### 具体テストケース一覧
- `tc-s02-001` acceptance: Issue planning route が追加される
  - 前提: hub skill に Issue execution route だけがある。
  - 操作: route list に `spec-dock-issue-planning` を追加する。
  - 期待結果: Issue planning は planning skill、Issue execution は execution skill に route される。
  - 失敗検出: Issue planning が execution skill に送られる古い routing を検出する。
  - 検証方法: S02 inspection、S05 text assertion。
  - 関連 closure id: tc-002
- `tc-s02-002` inspect-only: simultaneous request sequencing
  - テスト不要理由: skill text contract のため inspection と S05 text assertion で足りる。
  - 代替検証方法: planning + execution 同時指定時に reviewer gate / handoff readiness を飛ばさない wording を確認する。
  - 期待結果: implementation readiness の self-claim を許さない。
  - 記録先: `report.md`
  - 関連 closure id: tc-002

#### ステップ完了契約
- closure id: tc-002
- close 条件: hub route / sequencing / clarification companion が正しく記載される
- 検証 evidence: inspection + `spec-reviewer` pass
- report evidence: Step/Test/Closure ledgers
- 残リスク: S05/S99 で test assertion と final spec review を行う。

#### ステップゲート
- reviewer: `spec-reviewer`
- commit / no-op gate: S02 file only

### 実装ステップ S03 — Issue execution skill の implementation boundary を明確化する
- 振る舞いの目標:
  - `spec-dock-issue-execution` が approved/reviewer-pass planning artifacts と executable `plan.md` を前提にし、gap を planning / clarification に戻す。
- design 参照:
  - `インターフェース契約`, `シーケンス差分`
- 依存: S01, S02
- unblock: S04, S05, S06
- 対象ファイル:
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md`
- 計画済み契約:
  - scope:
    - Existing execution reminders は保ちつつ、planning artifact readiness と gap stop condition を明確化する。
  - テスト義務:
    - closure id: tc-003
    - coverage rationale: execution は実装開始 gate のため、未解決 spec gap の吸収を防ぐ。
  - Red / 代替証跡:
    - inspect-only in S03; S05 で assertion。
  - 実装範囲:
    - allowed paths: target file only
    - forbidden changes: completion policy / PR delivery policy の再設計
  - Green 検証: text inspection
  - Refactor guardrail: runtime command reminders の既存構造を壊さない。
  - report 証跡の記録先: Implementation Delegation Gate, Delegated Worker Evidence or Parent Implementation Exception, Step/Test/Closure ledgers
  - amendment trigger: execution skill に planning authoring を再統合する必要が出た場合

#### 委任契約（delegation contract）
- 委任ロール: `doc-writer`
- scope: S03 issue execution skill boundary wording only
- source of truth: `requirement.md`, `design.md`, `workflow_issue.md`, `authoring/issue-plan.md`
- 入力 docs: `requirement.md`, `design.md`, existing execution skill, `workflow_issue.md`, `authoring/issue-plan.md`
- 許可 paths: S03 target file
- 禁止 changes: runtime code/tests/provider docs/dogfooding output
- 受け入れ条件: tc-003
- 必須 verification: docs-only inspection
- reviewer focus: `spec-reviewer`
- 必須出力: changed files、boundary evidence、unresolved risks、`Ledger Note` または `No material implementation decisions beyond the approved plan.`
- 停止条件: approved/reviewer-pass prerequisite を表現できない

#### 具体テストケース一覧
- `tc-s03-001` acceptance: execution prerequisite が明記される
  - 前提: execution skill は active issue execution reminder である。
  - 操作: approved/reviewer-pass requirement/design/plan と executable `plan.md` prerequisite を明記する。
  - 期待結果: incomplete specs のまま implementation を開始しない wording になる。
  - 失敗検出: planning gap を実装仮定で吸収する回帰を検出する。
  - 検証方法: S03 inspection、S05 assertion。
  - 関連 closure id: tc-003
- `tc-s03-002` inspect-only: gap stop condition
  - テスト不要理由: docs-only skill text の境界確認。
  - 代替検証方法: unresolved requirement/design/plan gap は `workflow_clarification.md` または authoring phase に戻す wording を確認する。
  - 期待結果: execution skill が requirement/design/plan 作成そのものを主責務にしない。
  - 記録先: `report.md`
  - 関連 closure id: tc-003

#### ステップ完了契約
- closure id: tc-003
- close 条件: prerequisite / gap stop condition / execution-only boundary が記載される
- 検証 evidence: inspection + `spec-reviewer` pass
- report evidence: Step/Test/Closure ledgers
- 残リスク: S05/S99 で assertions と final spec review。

#### ステップゲート
- reviewer: `spec-reviewer`
- commit / no-op gate: S03 file only

### 実装ステップ S04 — Provider-side shipped docs を更新する
- 振る舞いの目標:
  - Shipped README / `workflow_issue.md` が Issue planning / execution split を示し、既存 authoring/execution policy を再定義しない。
- design 参照:
  - `ディレクトリ / ファイル変更計画`, `要件 → 設計マッピング`
- 依存: S01-S03
- unblock: S05, S06, S90
- 対象ファイル:
  - `src/spec_dock/assets/spec_dock/docs/README.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
- 計画済み契約:
  - scope:
    - Skill list、corresponding leaf skills、authoring/execution boundary references を更新する。
  - テスト義務:
    - closure id: tc-004
    - coverage rationale: shipped docs are installed guidance, so stale entrypoint wording must be detected.
  - Red / 代替証跡:
    - inspect-only in S04; S05 tests assert docs text.
  - 実装範囲:
    - allowed paths: target files only
    - forbidden changes: `workflow_spec_authoring.md`, `workflow_clarification.md`, `phase_plan_issue.md`, `authoring/issue-plan.md` unless implementation reveals actual docs drift requiring amendment
  - Green 検証: docs inspection
  - Refactor guardrail: completion / PR / issue finish policy を広く書き換えない。
  - report 証跡の記録先: Implementation Delegation Gate, Delegated Worker Evidence or Parent Implementation Exception, Step/Test/Closure ledgers, S90
  - amendment trigger: workflow policy docs の source-of-truth split 自体を変える必要が出た場合

#### 委任契約（delegation contract）
- 委任ロール: `doc-writer`
- scope: S04 provider-side shipped docs split wording only
- source of truth: `requirement.md`, `design.md`, provider README/workflow_issue, workflow source docs
- 入力 docs: `requirement.md`, `design.md`, provider README/workflow_issue, workflow source docs
- 許可 paths: S04 target files
- 禁止 changes: tests/runtime/dogfooding output
- 受け入れ条件: tc-004
- 必須 verification: docs inspection
- reviewer focus: `spec-reviewer`
- 必須出力: changed files、docs diff summary、unresolved risks、`Ledger Note` または `No material implementation decisions beyond the approved plan.`
- 停止条件: docs update requires policy rewrite outside design scope

#### 具体テストケース一覧
- `tc-s04-001` acceptance: README skill list が split を示す
  - 前提: README は Issue leaf skill を execution のみとして案内している。
  - 操作: `spec-dock-issue-planning` と `spec-dock-issue-execution` の役割を分けて記載する。
  - 期待結果: planning は spec authoring / clarification、execution は issue execution workflow へ route される。
  - 失敗検出: Issue entrypoint が execution-only として固定される回帰を検出する。
  - 検証方法: S04 inspection、S05 docs assertion。
  - 関連 closure id: tc-004
- `tc-s04-002` inspect-only: workflow_issue policy を広げない
  - テスト不要理由: policy wording の境界確認。
  - 代替検証方法: `workflow_issue.md` の completion / PR / finish policy に不要な再設計がないことを diff inspection する。
  - 期待結果: corresponding leaf skills と authoring/execution boundary だけが更新される。
  - 記録先: `report.md`
  - 関連 closure id: tc-004

#### ステップ完了契約
- closure id: tc-004
- close 条件: provider docs are updated and remain source-of-truth aligned
- 検証 evidence: docs inspection + `spec-reviewer` pass
- report evidence: Step/Test/Closure ledgers, S90
- 残リスク: S05/S99 で docs assertions / final spec review。

#### ステップゲート
- reviewer: `spec-reviewer`
- commit / no-op gate: S04 docs only

### 実装ステップ S05 — Tests / managed asset expectations を更新する
- 振る舞いの目標:
  - Tests が `spec-dock-issue-planning` の存在、routing、docs、installed output、dogfooding parity drift を検出する。
- design 参照:
  - `テスト戦略`, `要件 / 例外 -> 検証マッピング`
- 依存: S01-S04
- unblock: S06, S99
- 対象ファイル:
  - `tests/test_init_update.py`
  - `tests/cli_runtime/harness.py`
  - `tests/cli_runtime/test_wrappers.py`
- 計画済み契約:
  - scope:
    - Managed asset names/maps、authoritative relative paths、classification prefixes、wrapper installed skill checks、bundled routing/docs assertions を更新する。
  - テスト義務:
    - closure id: tc-005, tc-006
    - coverage rationale: asset inventory and routing contract are regression-prone; assertions must fail without the new skill/split.
  - Red / 代替証跡:
    - red-required:
      - Before implementation or by diff inspection, identify existing focused tests that fail without S01-S04 changes; if impossible due same-turn implementation, record equivalent sensitivity evidence by showing new assertions target newly added paths/text.
  - 実装範囲:
    - allowed paths: S05 target files only
    - forbidden changes: production/runtime code、provider docs、dogfooding output
  - Green 検証:
    - Focused unittest commands covering changed assertions.
  - Refactor guardrail:
    - Do not reorganize large test modules beyond adding the necessary expectations/assertions.
  - report 証跡の記録先:
    - Implementation Delegation Gate, Delegated Worker Evidence or Parent Implementation Exception, TDD evidence, Step/Test/Closure ledgers, Reviewer Gate Status
  - amendment trigger:
    - If installer/scaffold behavior must change beyond asset addition, return to design/plan amendment.

#### 委任契約（delegation contract）
- 委任ロール: `dev-coder`
- scope: S05 tests and managed asset expectations only
- source of truth: `requirement.md`, `design.md`, `plan.md`, provider assets/docs after S01-S04, target tests
- 入力 docs: `requirement.md`, `design.md`, `plan.md`, provider assets/docs after S01-S04, target tests
- 許可 paths: S05 target files
- 禁止 changes: provider assets/docs/dogfooding output/runtime behavior unless amendment approved
- 受け入れ条件: tc-005, tc-006
- 必須 tests:
  - run focused unittest(s) that cover managed skill names/install plan/routing/docs/wrapper expectations
- reviewer focus: `code-reviewer`
- 必須出力: changed files、commands/results、test sensitivity evidence、unresolved risks、`Ledger Note` または `No material implementation decisions beyond the approved plan.`
- 停止条件: tests require changing runtime installer behavior or broad fixture rewrite

#### 具体テストケース一覧
- `tc-s05-001` regression: managed skill inventory includes planning skill
  - 前提: `_EXPECTED_MANAGED_SKILL_NAMES` / managed maps do not include `spec-dock-issue-planning`.
  - 操作: test expectations に new skill path を追加する。
  - 期待結果: managed install plan and installed target include `.agents/skills/spec-dock-issue-planning/SKILL.md`.
  - 失敗検出: provider-only or installed-output-missing regression を検出する。
  - 検証方法: focused `python -m unittest ...` for managed asset/install assertions。
  - 関連 closure id: tc-005
- `tc-s05-002` regression: hub/docs text assertions detect split
  - 前提: bundled routing contract は Issue execution route のみを期待している。
  - 操作: assertions に planning route、execution route、sequencing、docs list を追加する。
  - 期待結果: hub/docs が new split を示さない場合に test が失敗する。
  - 失敗検出: stale docs / stale hub route regression。
  - 検証方法: focused `python -m unittest tests.test_init_update.TestInitUpdate.test_bundled_skill_routing_contract` または実在する該当 test。
  - 関連 closure id: tc-005
- `tc-s05-003` regression: authority boundary assertions
  - 前提: planning skill が direct canonical authority や reviewer-pass 代替を主張しても検出されない。
  - 操作: planning skill text assertions を追加する。
  - 期待結果: main orchestrator ownership、delegated draft evidence、fresh reviewer gate、`authoring/issue-plan.md` routing が固定される。
  - 失敗検出: delegated draft / canonical authority 混同。
  - 検証方法: focused unittest for bundled skill routing / policy contract。
  - 関連 closure id: tc-006

#### ステップ完了契約
- closure id: tc-005, tc-006
- close 条件: tests fail-sensitive assertions added and focused tests pass
- 検証 evidence: focused unittest output
- report evidence: TDD table, Test Contract Closure, Closure Coverage
- 残リスク: full suite risk is closed in S99 or explicitly scoped.

#### ステップゲート
- reviewer: `code-reviewer`
- pass 条件: `review_status: pass`
- commit / no-op gate: S05 test changes only

### 実装ステップ S06 — Dogfooding parity を refresh / inspection で閉じる
- 振る舞いの目標:
  - Dogfooding workspace が provider-side skill/docs split を反映している、または drift detection evidence により checked-in parity update 不要が証明される。
- design 参照:
  - `Dogfooding Rules`, `テスト戦略`, AC-005/EC-004 mapping
- 依存: S01-S05
- unblock: S90, S99
- 対象ファイル:
  - `.agents/skills/spec-dock-issue-planning/SKILL.md`
  - `.agents/skills/spec-dock-issue-execution/SKILL.md`
  - `.agents/skills/spec-driven-tdd-workflow/SKILL.md`
  - `spec-dock/docs/README.md`
  - `spec-dock/docs/workflow_issue.md`
  - Only if parity refresh is intentionally applied
- 計画済み契約:
  - scope:
    - Run or inspect provider-to-dogfooding parity. Direct edits are allowed only as parity refresh outputs, not implementation source.
  - テスト義務:
    - closure id: tc-007
    - coverage rationale: checked-in dogfooding drift is a primary acceptance observation point.
  - Red / 代替証跡:
    - manual-required:
      - inspect provider vs dogfooding files before/after, or run repo-local update command if chosen.
  - 実装範囲:
    - allowed paths: target parity outputs only
    - forbidden changes: provider source, tests, canonical issue docs
  - Green 検証:
    - provider-to-dogfooding parity diff inspection and focused drift detection evidence; `./spec-dock/scripts/spec-dock validate`
  - Refactor guardrail:
    - Stop if refresh causes broad generated churn outside listed parity outputs.
  - report 証跡の記録先:
    - Implementation Delegation Gate, Delegated Worker Evidence or Parent Implementation Exception, Step/Test/Closure ledgers, Docs Impact S90, Final Quality Gate
  - amendment trigger:
    - if parity cannot be established or drift detection cannot prove checked-in parity update is unnecessary

#### 委任契約（delegation contract）
- 委任ロール: `doc-writer` for parity docs/skills; orchestrator records command evidence
- scope: S06 dogfooding parity outputs only
- source of truth: provider files after S01-S04, tests after S05, dogfooding targets
- 入力 docs: provider files after S01-S04, tests after S05, dogfooding targets
- 許可 paths: S06 target files only
- 禁止 changes: implementation source outside parity outputs
- 受け入れ条件: tc-007
- 必須 verification: provider-to-dogfooding parity inspection, validate, relevant drift-detection tests/evidence
- reviewer focus: `spec-reviewer`; `code-reviewer` if scaffold/update behavior changes
- 必須出力: parity action, changed files, verification result, unresolved risks, `Ledger Note` または `No material implementation decisions beyond the approved plan.`
- 停止条件: broad generated churn, dirty provider conflict, update command failure that requires design change, or parity cannot be established/proven unnecessary

#### 具体テストケース一覧
- `tc-s06-001` manual-required: dogfooding skill parity
  - 前提: provider skill files changed.
  - 操作: dogfooding `.agents/skills` corresponding files を refresh / inspect する。
  - 期待結果: dogfooding files reflect provider split, or drift detection evidence proves no checked-in parity update is required.
  - 失敗検出: provider-only skill addition drift。
  - 検証方法: diff inspection / existing parity tests / update command evidence。
  - 関連 closure id: tc-007
- `tc-s06-002` manual-required: dogfooding docs parity
  - 前提: provider README / workflow_issue changed.
  - 操作: dogfooding `spec-dock/docs` corresponding files を refresh / inspect する。
  - 期待結果: docs parity is resolved without treating dogfooding as source of truth.
  - 失敗検出: checked-in docs drift。
  - 検証方法: diff inspection / validate。
  - 関連 closure id: tc-007

#### ステップ完了契約
- closure id: tc-007
- close 条件: provider-to-dogfooding parity is established, or drift detection evidence proves checked-in parity update is unnecessary. A rationale-only non-refresh is incomplete/blocked.
- 検証 evidence: inspection/test/validate output
- report evidence: Step/Test/Closure ledgers, S90
- 残リスク: full issue-wide check in S99.

#### ステップゲート
- reviewer: `spec-reviewer` unless scaffold behavior changed
- commit / no-op gate: parity output files only

### ドキュメント影響の解消ステップ S90（docs impact resolution / docs refresh）
- 対象:
  - provider skill docs, provider README, provider `workflow_issue.md`, dogfooding parity docs/skills
- 対応:
  - S01-S04/S06 の docs impact を `report.md` に集約し、追加 docs/template/migration note が不要か確認する。
- doc update owner:
  - `doc-writer` when updates are required
- spec/doc review:
  - reviewer: `spec-reviewer`
  - pass 条件: docs が requirement / design / plan と整合し、未解決の必須 docs 影響が残っていない
- closure id:
  - tc-008
- 具体テストケース:
  - `tc-s90-001` manual-required: docs impact closure
    - 前提: S01-S06 が完了している。
    - 操作: docs/templates/README/workflow/skill/migration notes impact を確認する。
    - 期待結果: required docs updates are complete; no hidden docs impact remains.
    - 失敗検出: docs impact の閉じ忘れ。
    - 検証方法: `spec-reviewer` docs/spec alignment。
    - 関連 closure id: tc-008
- report evidence:
  - Final Quality Gate / Docs Impact Resolution table

### 最終品質ゲートステップ S99（final quality gate）
- branch diff 範囲:
  - provider skills/docs, tests, dogfooding parity outputs, issue docs/report
- 必須 validation:
  - focused unittest commands selected in S05
  - `./spec-dock/scripts/spec-dock validate`
  - `./spec-dock/scripts/spec-dock sync` or recorded `--no-github` rationale if live GitHub sync is intentionally skipped
  - `git diff --check`
- final QA gate:
  - reviewer: `qa-reviewer`
  - 範囲: Issue 全体の obligation coverage と integration test 要否
  - pass 条件: `review_status: pass`
- final code review gate:
  - reviewer: `code-reviewer`
  - 範囲: issue-wide integrated diff、構造、責務境界、回帰リスク、保守性
  - pass 条件: `review_status: pass`
- final spec review gate:
  - reviewer: `spec-reviewer`
  - 範囲: requirement / design / plan / report / implementation / tests / docs 整合
  - pass 条件: `review_status: pass`
- final commit gate:
  - commit 範囲: all accepted implementation/docs/test/parity changes and report evidence
  - final report ledger: no `Status=open`; unresolved blocked/stale adoption entries absent
  - post-commit external evidence destination: final response, PR body, or issue comment. Final commit hash and clean check are not required inside the committed `report.md`.
- PR Delivery Gate:
  - required evidence: PR URL, selected base, base-resolution source, base-resolution conflict / handling, draft/ready decision, head branch, head SHA, issue linkage, existing PR reuse / new PR creation decision
  - report evidence destination: `report.md` PR Delivery Gate before issue completion
- Merge Preparation Gate:
  - required evidence: PR open state, monitor status, latest monitored head SHA, fix loop count / history, required check status, non-required check status and waiver evidence, blocking review status, merge conflict / visible merge blocker status, unresolved review-thread limitation status, unresolved blockers, final merge-prepared decision
  - report evidence destination: `report.md` Merge Preparation Gate before issue completion
- closure id:
  - tc-009
- 具体テストケース:
  - `tc-s99-001` manual-required: final issue readiness
    - 前提: S01-S06/S90 are complete.
    - 操作: focused tests, validate/sync, final reviewers, clean diff checks を実行する。
    - 期待結果: all required gates pass and report ledger has closure evidence.
    - 失敗検出: partial readiness / missing review / missing closure evidence。
    - 検証方法: commands + reviewer outputs recorded in `report.md`。
    - 関連 closure id: tc-009

## 未確定事項
- none

## 最終完了条件
- AC/EC 達成:
  - tc-001 through tc-009 are closed in `report.md`.
- docs 影響解決:
  - S90 completed with `spec-reviewer` pass.
- 全 implementation step 完了:
  - S01-S06 committed / approved-no-op with report evidence.
  - Each S01-S06 step has Implementation Delegation Gate evidence and either Delegated Worker Evidence or Parent Implementation Exception evidence as applicable.
- final quality gate pass:
  - qa-reviewer: pass
  - issue-wide code-reviewer: pass
  - spec-reviewer: pass
- final commit 完了:
  - `report.md` records final report ledger, final commit scope, and post-commit external evidence destination. The final commit hash and clean worktree check are recorded after commit as external delivery evidence.
- PR delivery / merge preparation 完了:
  - `report.md` records the full PR Delivery Gate evidence set: PR URL, selected base, base-resolution source, base-resolution conflict / handling, draft/ready decision, head branch, head SHA, issue linkage, and existing PR reuse / new PR creation decision.
  - `report.md` records the full Merge Preparation Gate evidence set: PR open state, monitor status, latest monitored head SHA, fix loop count / history, required check status, non-required check status and waiver evidence, blocking review status, merge conflict / visible merge blocker status, unresolved review-thread limitation status, unresolved blockers, and final merge-prepared decision.
- 必須 closure id 完了:
  - Step Contract Closure, Test Contract Closure, Closure Coverage all complete.
- final clean state:
  - no unintended staged / unstaged changes before PR delivery.
