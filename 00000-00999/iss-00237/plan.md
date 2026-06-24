---
種別: 実装計画書（Issue）
ID: "iss-00237"
タイトル: "Analyze Manual Test Routing Failures"
関連GitHub: ["#237"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-24"
依存: ["requirement.md", "design.md"]
親: ["epic-00224", "init-local-00003"]
---

# iss-00237 Analyze Manual Test Routing Failures — 実装計画

## この計画で満たす要件ID
- AC:
  - AC-001: runtime evidence と `docs-only verification` phrase が同居しても runtime routing になる。
  - AC-002: 否定文だけでは `security-sensitive` / `xhigh` に昇格しない。
  - AC-003: 肯定的な authentication / authorization / permissions / security evidence は引き続き `security-sensitive` / `xhigh` になる。
  - AC-004: explicit docs-only は既存 docs-only routing を維持する。
  - AC-005: migration / rollback の肯定的 evidence は既存 migration routing を維持する。
  - AC-006: targeted pytest が成功する。
- EC:
  - EC-001: runtime evidence は docs-only weak phrase より優先する。
  - EC-002: forbidden / stop condition / negated high-risk word だけでは security-sensitive にしない。
  - EC-003: affirmative security evidence は runtime evidence より優先する。
- 制約:
  - routing policy matrix、assurance classification policy、PR observation、`workflow_state.py`、explicit task field schema は変更しない。

## 依存関係から導く実装順序
- S01:
  - 依存: `requirement.md` / `design.md`
  - unblock: classifier 実装修正の Red evidence
  - 対象ファイル: `tests/cli_runtime/test_workflow_context_routing.py`
- S02:
  - 依存: S01
  - unblock: AC-001〜AC-005 の Green evidence
  - 対象ファイル: `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/context_packets.py`
- S90:
  - 依存: S02
  - unblock: docs impact の有無確認
  - 対象ファイル: 原則なし
- S99:
  - 依存: S01 / S02 / S90
  - unblock: Issue 完了判断
  - 対象ファイル: `report.md`

## ステップ一覧
- S01:
  - 観測可能な振る舞い: 現行 classifier が MT-009 / MT-024 の failure を再現する。
  - 依存: なし
  - unblock: S02
  - 対象ファイル: `tests/cli_runtime/test_workflow_context_routing.py`
  - 閉じる要件: AC-001〜AC-002 の Red fixture と AC-003〜AC-005 の covered-existing guards
  - レビューゲート: code-reviewer
- S02:
  - 観測可能な振る舞い: evidence-based classifier により routing regression tests が Green になる。
  - 依存: S01
  - unblock: S90 / S99
  - 対象ファイル: `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/context_packets.py`
  - 閉じる要件: AC-001〜AC-006、EC-001〜EC-003
  - レビューゲート: code-reviewer
- S90:
  - 観測可能な振る舞い: この修正に必要な docs update がないこと、または follow-up に切り出すことが明確になっている。
  - 依存: S02
  - unblock: S99
  - 対象ファイル: 原則なし。必要が出た場合のみ plan amendment。
  - 閉じる要件: scope constraint
  - レビューゲート: spec-reviewer
- S99:
  - 観測可能な振る舞い: Issue の実装証跡、検証結果、残リスクが `report.md` に記録される。
  - 依存: S01 / S02 / S90
  - unblock: Issue finish
  - 対象ファイル: `report.md`
  - 閉じる要件: AC-006、final evidence
  - レビューゲート: qa-reviewer / spec-reviewer

## 要件 ↔ ステップ対応
- AC-001 -> S01 / S02
- AC-002 -> S01 / S02
- AC-003 -> S01 / S02
- AC-004 -> S01 / S02
- AC-005 -> S01 / S02
- AC-006 -> S02 / S99
- EC-001 -> S01 / S02
- EC-002 -> S01 / S02
- EC-003 -> S01 / S02

## 仕様固定クロージャ索引（Spec-Locked Closure Index）
| 識別子（ID） | ステップ（step） | スライス（slice） | 種別（type） | 仕様リンク | 固定する期待値 | 観測可能な入力 / 状態 | 防ぐ bug class | 必須 | 証跡レベル（evidence level） | クロージャ証跡（closure evidence） |
|---|---|---|---|---|---|---|---|---|---|---|
| tc-237-001 | S01/S02 | runtime-over-docs-only-phrase | 受け入れ | AC-001, EC-001 | runtime step は `dev-coder` / `medium` / `unit_tests` / `code-reviewer` | runtime paths、`unit_tests`、`dev-coder`、`code-reviewer`、`docs-only verification` が同居する plan step | docs-only over-match による過小分類 | yes | red-required | `report.md` Step/Test Contract Closure |
| tc-237-002 | S01/S02 | negated-security | 否定系 | AC-002, EC-002 | 否定文だけでは `security-sensitive` / `xhigh` にしない | `security/privacy-sensitive として過剰に分類しない` を含み、肯定的 security evidence はない plan step | negated high-risk word の過剰分類 | yes | red-required | `report.md` Step/Test Contract Closure |
| tc-237-003 | S01/S02 | affirmative-security | 回帰防止 | AC-003, EC-003 | 肯定的 security evidence は `security-sensitive` / `xhigh` | authentication / authorization / permissions / `security_review` / `privacy_review` を含む plan step | security false negative | yes | covered-existing | `report.md` Step/Test Contract Closure |
| tc-237-004 | S01/S02 | explicit-docs-only | 回帰防止 | AC-004 | explicit docs-only は `doc-writer` / `low` / `docs_inspection` / `spec-reviewer` | `Task marker: docs-only` を含む plan step | docs-only true positive の破壊 | yes | covered-existing | `report.md` Step/Test Contract Closure |
| tc-237-005 | S01/S02 | affirmative-migration | 回帰防止 | AC-005 | migration / rollback evidence は `migration` routing を維持し、`rollback_plan` を要求する | `Task marker: migration rollback` を含む plan step | migration true positive の破壊 | yes | covered-existing | `report.md` Step/Test Contract Closure |
| tc-237-006 | S99 | targeted-routing-suite | 受け入れ | AC-006 | targeted pytest が成功する | routing CLI test suite | 実装と既存投影 contract の不整合 | yes | covered-existing | `report.md` Final Verification |

## レビュー / QA ゲート方針
- RG1 step review:
  - 実施タイミング: S01 / S02 の implementation step 完了後。
  - reviewer: code-reviewer。
  - pass 条件: classifier precedence、false positive / false negative、test sensitivity に blocking 指摘がないこと。
- QG1 final QA:
  - reviewer: qa-reviewer。
  - 範囲: AC/EC coverage、追加すべき high-value test の有無、manual test failure 再発リスク。
- SG1 final spec review:
  - reviewer: spec-reviewer。
  - 範囲: requirement / design / plan / report の整合、scope 外項目の切り分け。

## 実行ルール（全ステップ共通）
- 各 implementation step は 1 behavior slice / 1 review scope / 1 commit boundary とする。
- `plan.md` には planned contract を置き、観測結果は `report.md` に記録する。
- routing policy matrix に手を入れる必要が出た場合は、実装を止めて plan amendment と再レビューを行う。
- explicit `task_kind` / `risk_tags` field が必要と判明した場合は、この issue では実装せず follow-up 化する。

## 実装ステップ

### 実装ステップ S01 — routing classifier regression を赤で固定する
- 振る舞いの目標:
  - MT-009 / MT-024 の routing failure を CLI runtime test で再現できるようにする。
- design 参照:
  - `design.md` の「分類 precedence」「テスト戦略」。
- 依存:
  - なし。
- unblock:
  - S02。
- 対象ファイル:
  - `tests/cli_runtime/test_workflow_context_routing.py`
- 計画済み契約:
  - scope:
    - CLI runtime fixture を追加し、`workflow next issue-execution --format json` の public output を assert する。
  - テスト義務:
    - closure id:
      - tc-237-001
      - tc-237-002
      - tc-237-003
      - tc-237-004
      - tc-237-005
    - coverage rationale:
      - 手動テスト failure の再発を、private helper ではなく public CLI surface で検出する。
  - Red / 代替証跡の要件:
    - red-required:
      - S02 実装前に少なくとも tc-237-001 または tc-237-002 が失敗することを確認する。
      - tc-237-003 / tc-237-004 / tc-237-005 は existing true positive を守る covered-existing evidence として固定する。
  - 実装範囲:
    - allowed paths:
      - `tests/cli_runtime/test_workflow_context_routing.py`
    - forbidden changes:
      - production code。
      - routing policy matrix。
  - Green 検証:
    - S01 単独では failure が期待される。結果は `report.md` に Red evidence として記録する。
  - closure 証跡要件:
    - Step Contract Closure: tests added。
    - Test Contract Closure: Red evidence recorded。
    - Closure Coverage: tc-237-001〜tc-237-005 linked。
  - amendment trigger:
    - CLI fixture では再現できず private function test が必要になる場合。

#### 委任契約（S01）
- 委任ロール:
  - dev-coder
- 入力 docs:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - `spec-dock/active/issue/discussions/20260624t062220z-disc-routing-repair-design-options.md`
- 許可 paths:
  - `tests/cli_runtime/test_workflow_context_routing.py`
- 禁止 changes:
  - `src/spec_dock/**`
  - `spec-dock/**` の canonical docs 以外
- 受け入れ条件:
  - tc-237-001〜tc-237-005 の test fixture が存在する。
  - S02 前に Red evidence を観測できる。
- 必須 tests:
  - `uv run pytest tests/cli_runtime/test_workflow_context_routing.py`
- reviewer focus:
  - tests が current implementation details に過剰結合せず、public CLI output を見ていること。
- 停止条件:
  - fixture で active issue / plan step selection を安定再現できない。

#### 具体テストケース一覧（S01）
- `tc-s01-001` acceptance: runtime paths override docs-only verification phrase
  - 前提: plan step に runtime paths、`unit_tests`、`dev-coder`、`code-reviewer`、`docs-only verification` が同居する。
  - 操作: `workflow next issue-execution --format json`
  - 期待結果: `task_kind=runtime`、`worker=dev-coder`、`reasoning_effort=medium`、`verification=["unit_tests"]`、`reviewers=["code-reviewer"]`
  - 失敗検出: `doc-writer` / `low` / `docs_inspection` になる。
  - 関連 closure id: tc-237-001
- `tc-s01-002` negative: negated security phrase does not escalate
  - 前提: plan step に `security/privacy-sensitive として過剰に分類しない` があるが、肯定的 security evidence はない。
  - 操作: `workflow next issue-execution --format json`
  - 期待結果: `task_kind` は `security-sensitive` ではなく、`reasoning_effort` は `xhigh` ではない。
  - 失敗検出: `security-sensitive` / `xhigh` になる。
  - 関連 closure id: tc-237-002
- `tc-s01-003` regression: affirmative authz terms still escalate
  - 前提: plan step に authentication / authorization / permissions / `security_review` / `privacy_review` がある。
  - 操作: `workflow next issue-execution --format json`
  - 期待結果: `task_kind=security-sensitive`、`reasoning_effort=xhigh`、verification に `security_review` と `privacy_review` が含まれる。
  - 失敗検出: runtime / medium に落ちる。
  - 関連 closure id: tc-237-003
- `tc-s01-004` regression: explicit docs-only still routes to doc-writer
  - 前提: plan step に explicit `Task marker: docs-only` がある。
  - 操作: `workflow next issue-execution --format json`
  - 期待結果: `worker=doc-writer`、`reasoning_effort=low`、`verification=["docs_inspection"]`、`reviewers=["spec-reviewer"]`
  - 失敗検出: runtime / dev-coder になる。
  - 関連 closure id: tc-237-004
- `tc-s01-005` regression: affirmative migration still routes to migration obligations
  - 前提: plan step に explicit `Task marker: migration rollback` がある。
  - 操作: `workflow next issue-execution --format json`
  - 期待結果: `task_kind=migration`、`worker=dev-coder`、`reasoning_effort=high`、verification に `rollback_plan` が含まれる。
  - 失敗検出: runtime / medium または docs-only に落ちる。
  - 関連 closure id: tc-237-005

### 実装ステップ S02 — evidence-based classifier を実装する
- 振る舞いの目標:
  - S01 の Red tests を Green にし、既存 routing tests を維持する。
- design 参照:
  - `design.md` の「採用方針」「分類 precedence」「インターフェース契約」。
- 依存:
  - S01。
- unblock:
  - S90 / S99。
- 対象ファイル:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/context_packets.py`
  - `tests/cli_runtime/test_workflow_context_routing.py`（reviewer-directed regression の追加のみ）
- 計画済み契約:
  - scope:
    - `_classify_task_kind` を evidence-based precedence に変更する。
    - 必要な private helper を同ファイルに追加する。
  - テスト義務:
    - closure id:
      - tc-237-001
      - tc-237-002
      - tc-237-003
      - tc-237-004
      - tc-237-005
      - tc-237-006
  - 実装範囲:
    - allowed paths:
      - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/context_packets.py`
      - `tests/cli_runtime/test_workflow_context_routing.py`（S02 reviewer finding を閉じる regression のみ）
    - forbidden changes:
      - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/context_routing.py`
      - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/workflow_state.py`
      - PR observation scripts
      - docs/templates/system-wide schema changes
  - Green 検証:
    - `uv run pytest tests/cli_runtime/test_workflow_context_routing.py`
  - Refactor / cleanup ガードレール:
    - 目的: classifier の evidence 判定を読みやすく保つ。
    - 禁止する広がり: selection algorithm、completion detection、packet writing、policy matrix への拡大。
  - closure 証跡要件:
    - Step Contract Closure: classifier changed and tests Green。
    - Test Contract Closure: tc-237-001〜tc-237-006 observed。
    - Closure Coverage: AC/EC 全対応。
  - amendment trigger:
    - true positive を守るために policy matrix 変更が必要と判明した場合。
    - explicit schema field なしでは誤分類を安全に解消できないと判明した場合。

#### 委任契約（S02）
- 委任ロール:
  - dev-coder
- 入力 docs:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - `tests/cli_runtime/test_workflow_context_routing.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/context_packets.py`
- 許可 paths:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/context_packets.py`
  - `tests/cli_runtime/test_workflow_context_routing.py`（S02 reviewer-directed regression のみ）
- 禁止 changes:
  - S02 allowed paths 以外。
- 受け入れ条件:
  - S01 tests と既存 routing tests が成功する。
- 必須 tests:
  - `uv run pytest tests/cli_runtime/test_workflow_context_routing.py`
- reviewer focus:
  - precedence が AC/EC と一致していること。
  - negation handling が broad すぎないこと。
  - runtime fallback が docs-only true positive を壊していないこと。
- 停止条件:
  - security true positive が壊れる。
  - policy matrix 変更なしでは実装できない。

### ドキュメント影響の解消ステップ S90
- 対象:
  - docs / templates / README / workflow / skill / migration notes / none
- 対応:
  - 今回の修正は private classifier の bug fix であり、operator-visible contract は変えない想定。
  - docs update が必要な場合は、変更前に plan amendment を行う。
  - MT-003、MT-004、MT-015 はこの issue の実装修正対象外であり、必要なら follow-up issue に残す。
- spec/doc review:
  - spec-reviewer が scope 外項目の切り分けを確認する。

### 最終確認ステップ S99
- 対象:
  - `report.md`
  - routing regression suite
- 対応:
  - Red / Green / closure evidence を `report.md` に記録する。
  - targeted pytest の結果を記録する。
  - 未解決リスクと follow-up 候補を記録する。
- 最終検証:
  - `uv run pytest tests/cli_runtime/test_workflow_context_routing.py`
- final gates:
  - qa-reviewer:
    - AC/EC coverage と追加 test gap を確認する。
  - spec-reviewer:
    - `requirement.md` / `design.md` / `plan.md` / `report.md` の整合を確認する。

## フォローアップ候補
- Issue plan step schema への explicit `task_kind` / `risk_tags` field 導入 ADR / issue。
- `--github-issue` docs cleanup。
- symlink abuse fresh trial retest。
- `validate` / `doctor` の empty workspace semantics docs 明記。
