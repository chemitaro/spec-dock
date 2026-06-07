---
種別: 実装計画書（Issue）
ID: "iss-00171"
タイトル: "Improve Issue Planning Actor Workflow"
関連GitHub: ["#171"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-07"
依存: ["requirement.md", "design.md"]
親: ["epic-00158", "init-local-00003"]
---

# iss-00171 Improve Issue Planning Actor Workflow — 実装計画

## この計画で満たす要件ID

- AC:
  - AC-001: Actor-based workflow spine。
  - AC-002: Design phase の `system-architect` request。
  - AC-003: Plan phase の `implementation-planner` request。
  - AC-004: Draft adoption / report evidence。
  - AC-005: Role unavailable / fallback。
  - AC-006: Provider / mirror verification。
  - AC-007: 周辺補正。
  - AC-008: `system-architect` agent instruction encapsulation。
  - AC-009: `implementation-planner` agent instruction encapsulation。
  - AC-010: role skill directories deletion and reference cleanup。
  - AC-011: runtime delegated authoring provenance role names。
  - AC-012: test contract update for deleted role skills and agent role provenance。
- EC:
  - EC-001: `system-architect` unavailable。
  - EC-002: stale / insufficient design evidence。
  - EC-003: forbidden write / diff guard failure。
  - EC-004: discussion kind policy conflict。
  - EC-005: stale role-skill references。
  - EC-006: delegated authoring provenance compatibility。
  - EC-007: installer/update tests still expecting deleted role skills。
- 制約:
  - Canonical docs は main orchestrator authority。
  - Draft は reviewer pass ではない。
  - Skill は first-read spine、docs は detail semantics。
  - `system-architect` / `implementation-planner` は skill ではなく agent role。
  - Role behavior は `.codex/agents/*.toml` に閉じ、`.agents/skills/spec-dock-system-architect/` と `.agents/skills/spec-dock-implementation-planner/` は削除する。

## 依存関係から導く実装順序

- 依存関係の参照元:
  - `design.md` の依存関係分析、module dependency diagram、file change plan。
- 順序ルール:
  - Provider-side source を先に更新する。
  - Mirror は provider source の後に同期する。
  - 周辺補正は central skill rewrite の後に contradiction を確認してから行う。
  - Validation / sync / manual smoke はすべての text surface 更新後に行う。
- step 依存サマリー:
  - S01:
    - 依存: requirement/design/ChatGPT research。
    - unblock: mirror sync と surrounding inspection。
    - 対象ファイル: provider-side `spec-dock-issue-planning/SKILL.md`。
  - S02:
    - 依存: S01。
    - unblock: verification。
    - 対象ファイル: `.agents/skills/spec-dock-issue-planning/SKILL.md`。
  - S03:
    - 依存: S01/S02。
    - unblock: final validation。
    - 対象ファイル: provider-side と dogfooding mirror の `.codex/agents/system-architect.toml` / `implementation-planner.toml`、および削除対象 role skill directories。
  - S04:
    - 依存: S01-S03。
    - unblock: final validation。
    - 対象ファイル: hub skill / runtime delegated authoring checks / affected tests / provider-side workflow docs の必要最小補正。Dogfooding docs は mirror / validation target として扱う。
  - S90:
    - 依存: S01-S04。
    - unblock: S99。
    - 対象ファイル: docs impact evidence。
  - S99:
    - 依存: S01-S90。
    - unblock: execution completion decision。
    - 対象ファイル: all changed files / report.

## ステップ一覧

- S01:
  - 観測可能な振る舞い: Provider-side issue planning skill が actor-based workflow spine として読める。
  - 依存: ChatGPT research / issue requirement / issue design。
  - unblock: dogfooding mirror sync。
  - 対象ファイル:
    - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md`
  - 閉じる要件: AC-001, AC-002, AC-003, AC-004, AC-005, EC-001, EC-002, EC-003, EC-004。
  - レビューゲート: spec-reviewer docs/spec alignment。
- S02:
  - 観測可能な振る舞い: Dogfooding mirror の issue planning skill が provider-side source と一致する。
  - 依存: S01。
  - unblock: provider/mirror verification。
  - 対象ファイル:
    - `.agents/skills/spec-dock-issue-planning/SKILL.md`
  - 閉じる要件: AC-006。
  - レビューゲート: spec-reviewer docs/spec alignment。
- S03:
  - 観測可能な振る舞い: `system-architect` / `implementation-planner` が skill ではなく self-contained agent role として成立する。
  - 依存: S01/S02。
  - unblock: surrounding reference cleanup。
  - 対象ファイル:
    - `src/spec_dock/assets/install_root/.codex/agents/system-architect.toml`
    - `src/spec_dock/assets/install_root/.codex/agents/implementation-planner.toml`
    - `.codex/agents/system-architect.toml`
    - `.codex/agents/implementation-planner.toml`
    - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-system-architect/`
    - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-implementation-planner/`
    - `.agents/skills/spec-dock-system-architect/`
    - `.agents/skills/spec-dock-implementation-planner/`
  - 閉じる要件: AC-008, AC-009, AC-010, EC-005。
  - レビューゲート: spec-reviewer docs/spec alignment。
- S04:
  - 観測可能な振る舞い: Surrounding surfaces が actor workflow rewrite と agent-only role model に矛盾しない。
  - 依存: S01-S03。
  - unblock: final validation。
  - 対象ファイル:
    - `src/spec_dock/assets/install_root/.agents/skills/spec-driven-tdd-workflow/SKILL.md`
    - `.agents/skills/spec-driven-tdd-workflow/SKILL.md`
    - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/delegated_authoring.py`
    - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/delegated_authoring.py`
    - `tests/unit/infra/test_init_update.py`
    - `tests/unit/domain/test_delegated_authoring.py`
    - `tests/cli_runtime/test_delegated_authoring.py`
    - `tests/cli_runtime/harness.py`
    - `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`
    - `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
    - `src/spec_dock/assets/spec_dock/docs/phase_design.md`
    - `src/spec_dock/assets/spec_dock/docs/phase_plan_issue.md`
    - `spec-dock/docs/workflow_spec_authoring.md`
    - `spec-dock/docs/workflow_issue.md`
    - `spec-dock/docs/phase_design.md`
    - `spec-dock/docs/phase_plan_issue.md`
  - 閉じる要件: AC-007, AC-011, AC-012, EC-004, EC-005, EC-006, EC-007。
  - レビューゲート: spec-reviewer docs/spec alignment。
- S90:
  - 観測可能な振る舞い: docs impact が解決または不要根拠付きで閉じている。
  - 依存: S01-S04。
  - unblock: S99。
  - 対象ファイル: report evidence / docs impact inspection。
  - 閉じる要件: AC-006, AC-007。
  - レビューゲート: spec-reviewer。
- S99:
  - 観測可能な振る舞い: issue 全体の planned checks と final review gates が pass できる状態になる。
  - 依存: S01-S90。
  - unblock: implementation completion。
  - 対象ファイル: all changed files。
  - 閉じる要件: all AC/EC。
  - レビューゲート: qa-reviewer / issue-wide code-reviewer / final spec-reviewer。

## 要件 ↔ ステップ対応

- AC-001 -> S01
- AC-002 -> S01
- AC-003 -> S01
- AC-004 -> S01
- AC-005 -> S01
- AC-006 -> S02, S99
- AC-007 -> S04, S90
- AC-008 -> S03
- AC-009 -> S03
- AC-010 -> S03, S04
- AC-011 -> S04
- AC-012 -> S04
- EC-001 -> S01
- EC-002 -> S01
- EC-003 -> S01
- EC-004 -> S01, S04
- EC-005 -> S03, S04
- EC-006 -> S04
- EC-007 -> S04

## 仕様固定クロージャ索引（Spec-Locked Closure Index）

| ID | Step | Slice | Type | 仕様リンク | 固定する期待値 | 観測可能な入力 / 状態 | 防ぐ bug class | 必須 | Evidence level | Closure evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| tc-001 | S01 | actor-workflow-spine | acceptance | AC-001 | Skill 本体が actor-based workflow として読める | Provider-side skill text | phase order だけに戻る regression | yes | inspect-only | `rg` / reviewer evidence |
| tc-002 | S01 | design-draft-route | acceptance | AC-002 | Design phase に `system-architect` draft request / adoption route がある | Provider-side skill text | design draft 作成漏れ | yes | inspect-only | `rg` / manual smoke |
| tc-003 | S01 | plan-draft-route | acceptance | AC-003 | Plan phase に `implementation-planner` draft request / adoption route がある | Provider-side skill text | plan draft 作成漏れ | yes | inspect-only | `rg` / manual smoke |
| tc-004 | S01 | adoption-boundary | acceptance | AC-004 | Draft は diff guard / EAL / canonical integration 後も reviewer pass ではない | Provider-side skill text | evidence laundering | yes | inspect-only | `rg` / reviewer evidence |
| tc-005 | S01 | fallback-boundary | edge | AC-005, EC-001 | unavailable / denied / consent missing / manual fallback は記録付きで扱い reviewer gate を緩めない | Provider-side skill text | role unavailable を degraded success にする regression | yes | inspect-only | `rg` / manual smoke |
| tc-006 | S02 | mirror-sync | acceptance | AC-006 | Provider-side source と dogfooding mirror が一致する | `diff -u` result | shipped source / mirror drift | yes | inspect-only | command evidence |
| tc-007 | S03 | agent-role-encapsulation | acceptance | AC-008, AC-009 | `system-architect` / `implementation-planner` role contract が `.codex/agents/*.toml` に閉じている | Provider-side and dogfooding agent TOML | role behavior remains split into skills | yes | inspect-only | `rg` / reviewer evidence |
| tc-008 | S03 | role-skill-removal | acceptance | AC-010, EC-005 | role skill directories が provider-side と dogfooding mirror から削除されている | filesystem state | stale skill remains discoverable | yes | inspect-only | `test ! -e` / `find` |
| tc-009 | S04 | surrounding-surface-consistency | compatibility | AC-007, EC-004, EC-005 | 周辺 surface が rewrite と agent-only model に矛盾しない、または follow-up として分類される | targeted inspection result | stale skill reference / docs contradiction | yes | inspect-only | report decision ledger |
| tc-010 | S04 | runtime-provenance-role-names | compatibility | AC-011, EC-006 | Delegated authoring runtime の fresh `created_by_role` は agent role names を使う | `delegated_authoring.py` and tests | deleted skill names remain runtime contract | yes | focused test / inspect | pytest / targeted rg |
| tc-011 | S04 | test-contract-update | compatibility | AC-012, EC-007 | Tests no longer expect deleted role skills and do expect agent role provenance | affected pytest files | stale tests preserve old contract | yes | focused pytest | pytest output |
| tc-012 | S99 | specdock-validation | acceptance | AC-006 | SpecDock validate/sync が成功または failure が今回差分由来でないと判断できる | `validate` / `sync` result | dogfooding projection drift | yes | inspect-only | command evidence |

## レビュー / QA ゲート方針

- Step review:
  - Skill-text-only / docs-only 変更なので、各 implementation step の primary reviewer は `spec-reviewer` docs/spec alignment。
  - Code / runtime / tests が変更された場合だけ `code-reviewer` を追加する。
- Final QA:
  - `qa-reviewer` は issue 全体の obligation coverage と manual smoke の十分性を確認する。
- Final spec review:
  - `spec-reviewer` は requirement / design / plan / report / changed skill/docs/mirror の整合を確認する。
- Final issue-wide code review:
  - `workflow_issue.md` の S99 contract に従い、docs-only / skill-text-only であっても issue-wide `code-reviewer` gate を実行する。
  - Reviewer focus は runtime correctness ではなく、統合 diff の構造、source-of-truth boundary、reviewability、unintended shipped-asset drift とする。

## 実装ステップ

### 実装ステップ S01 — Provider-side issue planning skill を actor-based workflow spine へ書き換える

- 振る舞いの目標:
  - Agent が provider-side `spec-dock-issue-planning/SKILL.md` だけを最初に読んでも、requirement / design / plan の各 phase で誰が何をするかを判断できる。
- design 参照:
  - `design.md` の `採用方針 / トレードオフ`、`依存関係分析`、`ディレクトリ / ファイル変更計画`。
- 依存:
  - ChatGPT research。
- unblock:
  - S02 mirror sync。
- 対象ファイル:
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md`
- 計画済み契約:
  - scope:
    - description を operational workflow spine として補正する。
    - `Mandatory Issue Authoring Workflow` を actor-based sequence に置換または増補する。
    - `Authority And Routing` を draft invocation / adoption / fallback と接続する。
    - 必要なら `Discussion Draft Path Compatibility` を追加する。
  - test obligation:
    - closure id: tc-001, tc-002, tc-003, tc-004, tc-005。
    - coverage rationale: 今回の failure mode は text surface の欠落なので、inspection と reviewer evidence で閉じる。
  - Red / 代替証跡:
    - inspect-only:
      - 変更前 skill では workflow 本体に `system-architect` / `implementation-planner` の draft request sequence がないことを確認済み。
      - 変更後は targeted `rg` と manual smoke で確認する。
  - Green 検証:
    - `rg -n "system-architect|implementation-planner|diff guard|Evidence Adoption Ledger|fresh spec-reviewer|unavailable|manual fallback" src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md`
  - Refactor / cleanup ガードレール:
    - docs の詳細 schema を skill にコピーしすぎない。
    - `workflow_spec_authoring.md` / `workflow_issue.md` の authority を上書きしない。
  - report 証跡の記録先:
    - Evidence Adoption Ledger
    - Step Contract Closure
    - Test Contract Closure
    - Reviewer Gate Status
  - amendment trigger:
    - Runtime API / validation implementation 変更が必要になった場合。
    - Canonical docs の policy 変更が必要になった場合。

#### 委任契約

- 委任ロール:
  - doc-writer preferred for skill-text-only implementation.
  - Parent implementation exception is acceptable only if role unavailable is recorded and user instruction permits direct authoring.
- 入力 docs:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - `discussions/20260607t074107z-research-chatgpt-actor-workflow-analysis.md`
  - `spec-dock/docs/workflow_spec_authoring.md`
  - `spec-dock/docs/workflow_issue.md`
  - `spec-dock/docs/phase_design.md`
  - `spec-dock/docs/phase_plan_issue.md`
- 許可 paths:
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md`
- 禁止 changes:
  - Runtime CLI / tests / unrelated docs / unrelated skills。
  - Canonical issue docs outside planned report updates。
- 受け入れ条件:
  - tc-001 through tc-005。
- 必須 verification:
  - targeted `rg`
  - spec-reviewer docs/spec alignment。
- reviewer focus:
  - spec-reviewer: actor sequence, authority boundary, no over-copy, gap routing。
- 必須出力:
  - changed files
  - verification result
  - unresolved risks
  - `Ledger Note` or no material decisions。
- 停止条件:
  - Skill rewrite requires runtime behavior change.
  - Allowed path insufficient.
  - Draft kind policy conflict cannot be resolved without broad docs rewrite.

#### 具体テストケース一覧

- `tc-s01-001` inspect-only: actor-based workflow spine が存在する
  - 前提: provider-side issue planning skill を開く。
  - 操作: `Mandatory Actor-Based Issue Authoring Workflow` または同等 section を読む。
  - 期待結果: main orchestrator、system-architect、implementation-planner、spec-reviewer の役割と順序が分かる。
  - 失敗検出: phase order だけがあり、actor が workflow 本体に出ない回帰を検出する。
  - 検証方法: `rg` と manual inspection。
  - 関連 closure id: tc-001
- `tc-s01-002` inspect-only: design draft route が明示される
  - 前提: requirement が fresh reviewer pass 済みの design phase。
  - 操作: design phase subsection を読む。
  - 期待結果: `system-architect` request、source requirement revision、diff guard、handoff review、adoption、canonical integration、fresh reviewer pass が順に読める。
  - 失敗検出: design draft 作成が任意 evidence 扱いに戻る回帰を検出する。
  - 検証方法: `rg -n "system-architect|handoff review|diff guard|canonical design|fresh spec-reviewer"`
  - 関連 closure id: tc-002
- `tc-s01-003` inspect-only: plan draft route が明示される
  - 前提: requirement/design が fresh reviewer pass 済みの plan phase。
  - 操作: plan phase subsection を読む。
  - 期待結果: `implementation-planner` request、source revisions、design gap blocker、adoption、canonical integration、fresh reviewer pass が順に読める。
  - 失敗検出: plan draft 作成が省略される回帰を検出する。
  - 検証方法: `rg -n "implementation-planner|design evidence|canonical plan|fresh spec-reviewer"`
  - 関連 closure id: tc-003
- `tc-s01-004` inspect-only: draft adoption は reviewer pass ではない
  - 前提: delegated draft が存在する。
  - 操作: Authority / Draft Adoption wording を読む。
  - 期待結果: draft existence / handoff review / adoption が reviewer pass ではないことが明示される。
  - 失敗検出: delegated draft を phase promotion に laundering する regression を検出する。
  - 検証方法: `rg -n "not.*reviewer pass|does not replace|fresh spec-reviewer"`
  - 関連 closure id: tc-004
- `tc-s01-005` inspect-only: unavailable fallback が reviewer gate を緩めない
  - 前提: role unavailable / consent missing。
  - 操作: fallback / stop condition wording を読む。
  - 期待結果: skip/blocker is recorded, manual fallback may proceed only with full canonical reviewer gates preserved。
  - 失敗検出: unavailable を degraded success にする regression を検出する。
  - 検証方法: `rg -n "unavailable|manual fallback|skip_reason|does not weaken"`
  - 関連 closure id: tc-005

#### ステップ完了契約

- closure id:
  - tc-001, tc-002, tc-003, tc-004, tc-005
- close 条件:
  - Provider-side skill が actor-based workflow spine として読める。
- 検証 evidence:
  - targeted `rg`
  - manual inspection
  - reviewer pass
- report evidence:
  - Step Contract Closure
  - Test Contract Closure
  - Closure Coverage
- 残リスク:
  - Actual agent behavior は manual dogfooding smoke で補完する。

#### ステップゲート

- step reviewer gate:
  - reviewer: spec-reviewer
  - review 範囲: provider-side issue planning skill text
  - pass 条件: review_status: pass
- commit / no-op gate:
  - closure 状態: committed
  - commit 範囲: S01 related files

### 実装ステップ S02 — Dogfooding mirror を同期する

- 振る舞いの目標:
  - `.agents/skills/spec-dock-issue-planning/SKILL.md` が provider-side source と同じ actor workflow を提供する。
- 対象ファイル:
  - `.agents/skills/spec-dock-issue-planning/SKILL.md`
- 計画済み契約:
  - scope:
    - S01 の provider-side change を mirror に反映する。
  - test obligation:
    - closure id: tc-006。
  - Red / 代替証跡:
    - inspect-only: provider/mirror diff がないことを確認する。
  - Green 検証:
    - `diff -u src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md .agents/skills/spec-dock-issue-planning/SKILL.md`
  - report 証跡の記録先:
    - Test Contract Closure
    - Closure Coverage

#### 委任契約

- 委任ロール:
  - doc-writer preferred; parent direct sync acceptable if recorded.
- 入力 docs:
  - S01 provider-side file.
- 許可 paths:
  - `.agents/skills/spec-dock-issue-planning/SKILL.md`
- 禁止 changes:
  - Other mirror skills unless S03 decides they are needed.
- 必須 verification:
  - `diff -u`
- reviewer focus:
  - spec-reviewer: provider/mirror identity.
- 必須出力:
  - changed files
  - diff result
  - unresolved risks
- 停止条件:
  - Mirror is generated and should not be manually edited; if so, use repo-local update path instead.

#### 具体テストケース一覧

- `tc-s02-001` inspect-only: provider/mirror identity
  - 前提: S01 provider-side skill rewrite is complete。
  - 操作: provider-side file と mirror file を比較する。
  - 期待結果: 差分なし、または意図した generated difference の根拠が report に残る。
  - 失敗検出: provider source と dogfooding mirror が drift する regression を検出する。
  - 検証方法: `diff -u src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md .agents/skills/spec-dock-issue-planning/SKILL.md`
  - 関連 closure id: tc-006

#### ステップ完了契約

- closure id:
  - tc-006
- close 条件:
  - provider/mirror comparison が pass。
- 検証 evidence:
  - `diff -u`
- report evidence:
  - Test Contract Closure
  - Closure Coverage

#### ステップゲート

- step reviewer gate:
  - reviewer: spec-reviewer
  - pass 条件: review_status: pass
- commit / no-op gate:
  - closure 状態: committed

### 実装ステップ S03 — system-architect / implementation-planner を agent instruction に完全カプセル化する

- 振る舞いの目標:
  - `system-architect` / `implementation-planner` が skill を読まず、agent TOML の `developer_instructions` だけで delegated draft role として実行できる。
  - Provider-side と dogfooding mirror の role skill directories が削除され、skill discovery surface から消える。
- 対象ファイル:
  - 変更:
    - `src/spec_dock/assets/install_root/.codex/agents/system-architect.toml`
    - `src/spec_dock/assets/install_root/.codex/agents/implementation-planner.toml`
    - `.codex/agents/system-architect.toml`
    - `.codex/agents/implementation-planner.toml`
  - 削除:
    - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-system-architect/`
    - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-implementation-planner/`
    - `.agents/skills/spec-dock-system-architect/`
    - `.agents/skills/spec-dock-implementation-planner/`
- 計画済み契約:
  - scope:
    - agent TOML から skill 正本参照を削除する。
    - 既存 role skill の essential contract を agent TOML に移す。
    - 移す内容は role behavior、allowed path、forbidden changes、output sections、stop conditions、diff guard 前提に限定する。
    - `spec-dock-issue-planning` skill には role details をコピーせず、agent invocation / adoption / fallback 契約だけを残す。
  - test obligation:
    - closure id: tc-007, tc-008。
  - Red / 代替証跡:
    - inspect-only:
      - 現行 agent TOML は role skill path を canonical role contract として書き、skill 参照に依存している。
      - 現行 role skill directories が provider-side と dogfooding mirror に存在する。
  - Green 検証:
    - `rg -n "spec-dock-system-architect/SKILL.md|spec-dock-implementation-planner/SKILL.md|canonical role contract is|read and follow that skill" src/spec_dock/assets/install_root/.codex/agents/system-architect.toml src/spec_dock/assets/install_root/.codex/agents/implementation-planner.toml .codex/agents/system-architect.toml .codex/agents/implementation-planner.toml`
    - `test ! -e src/spec_dock/assets/install_root/.agents/skills/spec-dock-system-architect`
    - `test ! -e src/spec_dock/assets/install_root/.agents/skills/spec-dock-implementation-planner`
    - `test ! -e .agents/skills/spec-dock-system-architect`
    - `test ! -e .agents/skills/spec-dock-implementation-planner`
    - `diff -u src/spec_dock/assets/install_root/.codex/agents/system-architect.toml .codex/agents/system-architect.toml`
    - `diff -u src/spec_dock/assets/install_root/.codex/agents/implementation-planner.toml .codex/agents/implementation-planner.toml`
  - report 証跡の記録先:
    - Decision Ledger
    - Test Contract Closure
    - Closure Coverage
    - Deleted Files / Source-of-truth note
  - amendment trigger:
    - Agent TOML alone cannot express the role contract.
    - Installer/update tooling requires explicit manifest changes for deleted skill directories.

#### 委任契約

- 委任ロール:
  - doc-writer preferred for TOML instruction migration.
  - Parent direct authoring acceptable when keeping wording exactly aligned across provider/mirror.
- 入力 docs:
  - current role skill files before deletion
  - current provider/mirror agent TOML
  - requirement/design/plan
  - ChatGPT research and user追加要件
- 許可 paths:
  - S03 target files/directories only.
- 禁止 changes:
  - unrelated skills
  - runtime behavior except stale skill-reference cleanup explicitly discovered in S04
  - canonical issue docs outside planned report updates
- 必須 verification:
  - targeted `rg`
  - `test ! -e`
  - provider/mirror `diff -u`
- reviewer focus:
  - spec-reviewer: role knowledge is agent-only, skill directories are gone, issue-planning does not absorb role details.
- 停止条件:
  - Skill deletion breaks generated skill registry / installer tests in a way that requires runtime redesign.

#### 具体テストケース一覧

- `tc-s03-001` inspect-only: system-architect agent instruction is self-contained
  - 前提: S03 TOML migration is complete。
  - 操作: `system-architect.toml` を読む。
  - 期待結果: role mission、allowed output path、forbidden changes、output sections、stop conditions、diff guard 前提が skill 参照なしで分かる。
  - 失敗検出: `Before producing any answer, read and follow that skill` などの skill dependency が残る。
  - 検証方法: targeted `rg` and manual inspection。
  - 関連 closure id: tc-007
- `tc-s03-002` inspect-only: implementation-planner agent instruction is self-contained
  - 前提: S03 TOML migration is complete。
  - 操作: `implementation-planner.toml` を読む。
  - 期待結果: plan draft role contract、design gap routing、allowed output path、forbidden changes、output sections、stop conditions が skill 参照なしで分かる。
  - 失敗検出: role behavior が削除済み skill に残る。
  - 検証方法: targeted `rg` and manual inspection。
  - 関連 closure id: tc-007
- `tc-s03-003` inspect-only: role skill directories are removed
  - 前提: S03 deletion is complete。
  - 操作: provider-side and dogfooding mirror paths を確認する。
  - 期待結果: four role skill directories do not exist。
  - 失敗検出: deleted role remains discoverable as a skill。
  - 検証方法: `test ! -e` / `find`。
  - 関連 closure id: tc-008

#### ステップ完了契約

- closure id:
  - tc-007, tc-008
- close 条件:
  - role agent TOML self-contained, role skill directories deleted, provider/mirror TOML synchronized.
- 検証 evidence:
  - targeted `rg`
  - `test ! -e`
  - provider/mirror `diff -u`
- report evidence:
  - Decision Ledger
  - Test Contract Closure
  - Closure Coverage

#### ステップゲート

- step reviewer gate:
  - reviewer: spec-reviewer
  - pass 条件: review_status: pass
- commit / no-op gate:
  - closure 状態: committed

### 実装ステップ S04 — 周辺 surface の stale skill 参照と矛盾を必要最小限で補正する

- 振る舞いの目標:
  - `spec-dock-issue-planning` rewrite と agent-only role model が hub skill / docs / runtime reference checks と矛盾しない。
- 対象ファイル:
  - 必要時のみ:
    - `src/spec_dock/assets/install_root/.agents/skills/spec-driven-tdd-workflow/SKILL.md`
    - `.agents/skills/spec-driven-tdd-workflow/SKILL.md`
    - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/delegated_authoring.py`
    - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/delegated_authoring.py`
    - `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`
    - `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
    - `src/spec_dock/assets/spec_dock/docs/phase_design.md`
    - `src/spec_dock/assets/spec_dock/docs/phase_plan_issue.md`
    - `spec-dock/docs/workflow_spec_authoring.md`
    - `spec-dock/docs/workflow_issue.md`
    - `spec-dock/docs/phase_design.md`
    - `spec-dock/docs/phase_plan_issue.md`
- 計画済み契約:
  - scope:
    - Hub routing description が deleted role skills を案内しないこと。
    - Runtime delegated authoring checks は agent role names `system-architect` / `implementation-planner` を fresh `created_by_role` provenance の正値にすること。
    - Deleted skill names `spec-dock-system-architect` / `spec-dock-implementation-planner` を runtime contract として残さないこと。
    - Existing fixture / historical artifact compatibility が必要な場合は、legacy acceptance を明示し、fresh generated output が agent role name になる focused test を追加すること。
    - Installer/update tests が deleted role skill files を期待しないこと。
    - Delegated authoring unit / CLI runtime tests が agent role name provenance を期待すること。
    - Docs が hidden mandatory workflow や deleted skill reference を残さないこと。
    - Docs 補正が必要な場合は provider-side `src/spec_dock/assets/spec_dock/docs/` を変更し、`spec-dock/docs/` は dogfooding mirror / validation target として確認すること。
  - test obligation:
    - closure id: tc-009, tc-010, tc-011。
  - Green 検証:
    - targeted `rg -n "spec-dock-system-architect|spec-dock-implementation-planner|system-architect.toml|implementation-planner.toml|delegated_authoring"`
    - targeted `rg -n "AUTHORIZED_ROLE_FRONTMATTER|created_by_role|spec-dock-system-architect|spec-dock-implementation-planner|system-architect|implementation-planner" src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/delegated_authoring.py tests`
    - `uv run pytest tests/unit/infra/test_init_update.py tests/unit/domain/test_delegated_authoring.py tests/cli_runtime/test_delegated_authoring.py`
    - if changed, provider/mirror comparison for changed installed assets。
  - report 証跡の記録先:
    - Decision Ledger
    - Closure Delta
    - Test Contract Closure
  - amendment trigger:
    - Broad docs rewrite, runtime redesign, or generator manifest redesign is required。

#### 委任契約

- 委任ロール:
  - doc-writer preferred for text alignment; dev-coder only if runtime reference cleanup is required.
- 入力 docs:
  - S01 changed skill
  - S03 changed agent TOML / deleted role skill paths
  - requirement/design/plan
  - ChatGPT research and user追加要件
- 許可 paths:
  - listed target files only when stale reference or contradiction is confirmed.
- 禁止 changes:
  - Broad cleanup unrelated to iss-00171.
  - Runtime behavior changes beyond removing stale skill-path dependency and migrating delegated authoring provenance values.
- 必須 verification:
  - targeted `rg`
  - focused pytest:
    - `uv run pytest tests/unit/infra/test_init_update.py tests/unit/domain/test_delegated_authoring.py tests/cli_runtime/test_delegated_authoring.py`
  - provider/mirror diff for any changed installed asset.
- reviewer focus:
  - spec-reviewer: no stale skill dependency, no scope creep, docs detail preserved.
- 停止条件:
  - Correction requires new issue / broad ADR.

#### 具体テストケース一覧

- `tc-s04-001` inspect-only: hub routing consistency
  - 前提: issue planning skill and agent TOML are rewritten。
  - 操作: hub skill routing wording is inspected。
  - 期待結果: hub skill routes issue planning and delegated roles as agent roles, not removed role skills。
  - 失敗検出: router wording reintroduces deleted skill dependency。
  - 検証方法: targeted inspection。
  - 関連 closure id: tc-009
- `tc-s04-002` inspect-only: stale role skill references are classified
  - 前提: role skill directories are deleted。
  - 操作: repo-local relevant surfaces are searched for `spec-dock-system-architect` / `spec-dock-implementation-planner`。
  - 期待結果: remaining matches are either removed, role-name-only allowed references, or explicitly recorded as historical/follow-up。
  - 失敗検出: installed docs or runtime still instruct agents to read deleted skills。
  - 検証方法: targeted `rg`。
  - 関連 closure id: tc-009
- `tc-s04-003` focused runtime: delegated authoring provenance uses agent role names
  - 前提: delegated authoring runtime is inspected or changed。
  - 操作: runtime front matter validation / authorized role mapping is checked。
  - 期待結果: fresh `created_by_role` values are `system-architect` and `implementation-planner`; deleted skill names are not the primary runtime contract。
  - 失敗検出: `AUTHORIZED_ROLE_FRONTMATTER` maps role names to `spec-dock-*` skill names without an explicit compatibility rationale。
  - 検証方法: targeted `rg`; if code changes, focused pytest for delegated authoring domain/runtime tests。
  - 関連 closure id: tc-010
- `tc-s04-004` focused tests: asset and provenance tests encode the new contract
  - 前提: S03/S04 implementation changes delete role skill files and update delegated authoring provenance。
  - 操作: affected installer/update and delegated authoring tests are updated and run。
  - 期待結果: tests assert removed role skill paths are absent, agent TOML files are installed, and `created_by_role` uses `system-architect` / `implementation-planner`。
  - 失敗検出: tests still expect `.agents/skills/spec-dock-system-architect/SKILL.md`, `.agents/skills/spec-dock-implementation-planner/SKILL.md`, or `created_by_role: spec-dock-*` as the fresh contract。
  - 検証方法: `uv run pytest tests/unit/infra/test_init_update.py tests/unit/domain/test_delegated_authoring.py tests/cli_runtime/test_delegated_authoring.py`
  - 関連 closure id: tc-011

#### ステップ完了契約

- closure id:
  - tc-009, tc-010, tc-011
- close 条件:
  - contradictions corrected or explicitly deferred with non-blocking rationale; runtime provenance value and affected test contract are not ambiguous.
- 検証 evidence:
  - targeted `rg`
  - focused pytest
  - diff inspection
- report evidence:
  - Decision Ledger
  - Closure Coverage
  - Closure Delta

#### ステップゲート

- step reviewer gate:
  - reviewer: spec-reviewer
  - pass 条件: review_status: pass
- commit / no-op gate:
  - closure 状態: committed / approved-no-op

### ドキュメント影響の解消ステップ S90

- 対象:
  - Skills:
    - `spec-dock-issue-planning`
    - `spec-driven-tdd-workflow` if routing wording mentions removed role skills
  - Agent instructions:
    - `system-architect`
    - `implementation-planner`
  - Deleted skill directories:
    - `spec-dock-system-architect`
    - `spec-dock-implementation-planner`
  - Docs:
    - provider-side workflow / phase docs only if contradiction is confirmed.
    - dogfooding workflow / phase docs as mirror / validation targets.
  - Templates:
    - none expected.
- 対応:
  - Changed surfaces and no-op rationale are recorded in `report.md`。
  - If docs are unchanged, record why existing detail semantics remain valid。
- doc update owner:
  - doc-writer if docs change.
- spec/doc review:
  - reviewer: spec-reviewer
  - pass 条件: docs/skills remain aligned with requirement/design/plan and ChatGPT research adoption.

### 最終品質ゲートステップ S99

- branch diff 範囲:
  - issue docs/research
  - provider-side skill changes
  - provider-side agent TOML changes
  - deleted role skill directories
  - runtime delegated authoring provenance changes
  - affected tests for installed asset inventory and delegated authoring provenance
  - dogfooding mirror changes
  - necessary surrounding text corrections
- 必須 validation:
  - targeted `rg`
  - provider/mirror `diff -u`
  - `test ! -e` for deleted role skill directories
  - `uv run pytest tests/unit/infra/test_init_update.py tests/unit/domain/test_delegated_authoring.py tests/cli_runtime/test_delegated_authoring.py`
  - `./spec-dock/scripts/spec-dock validate`
  - `./spec-dock/scripts/spec-dock sync`
  - `git diff --check`
- final QA gate:
  - reviewer: qa-reviewer
  - 範囲: closure coverage、manual smoke 十分性、missing high-value scenarios。
  - pass 条件: reviewer pass。
- final code review gate:
  - reviewer: code-reviewer
  - 範囲: issue-wide integrated diff。docs-only / skill-text-only の場合も、source-of-truth boundary、reviewability、unintended shipped-asset drift、workflow regression risk を確認する。
  - pass 条件: review_status: pass.
- final spec review gate:
  - reviewer: spec-reviewer
  - 範囲: requirement / design / plan / report / skill changes / agent instruction changes / deleted role skill directories / runtime provenance changes / tests / mirror sync。
  - pass 条件: reviewer pass。
- final commit gate:
  - commit 範囲:
    - each implementation step or approved aggregation if docs-only review scope remains coherent.
  - final report ledger:
    - all closure ids pass / approved-no-op.
  - post-commit external evidence destination:
    - final response / PR body / issue comment.

## 未確定事項

- Blocking question:
  - なし。
- Non-blocking:
  - S04 で broad surrounding contradiction が見つかった場合は follow-up issue 化する。

## 最終完了条件

- AC/EC 達成:
  - AC-001 through AC-012 and EC-001 through EC-007 have closure evidence.
- docs 影響解決:
  - S90 complete.
- 全 implementation step 完了:
  - S01-S04 committed / approved-no-op.
- final quality gate pass:
  - qa-reviewer pass.
  - issue-wide code-reviewer pass.
  - final spec-reviewer pass.
  - validation/sync/git diff checks recorded.
