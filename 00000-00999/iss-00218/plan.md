---
種別: 実装計画書（Issue）
ID: "iss-00218"
タイトル: "Codex Review Fallback Signal Semantics"
関連GitHub: ["#218"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-20"
依存: ["requirement.md", "design.md"]
親: ["epic-00158", "init-local-00003"]
---

# iss-00218 Codex Review Fallback Signal Semantics — 実装計画（実行契約 / Execution Contract）

## この計画で満たす要件ID
- AC:
  - AC-001 strict no-findings issue comment promotion
  - AC-002 generic fallback non-promotion
  - AC-003 blocker precedence
  - AC-004 boundary rejection
  - AC-005 documentation clarity
- EC:
  - EC-001 observed Codex Review wording
  - EC-002 existing no-major-issues wording
  - EC-003 generic progress comment
  - EC-004 blockers coexist
  - EC-005 CI non-pass
  - EC-006 collection limitation
- 制約:
  - `fallback_issue_comment` remains low-confidence / non-promoting.
  - `--head-sha` missing / expected head unknown does not promote.
  - Collector does not own top-level `merge_prepared`; snapshot / wait owns it after CI / metadata integration.
  - `no_findings_completion_candidate` is mandatory for the new signal.

## 依存関係から導く実装順序
- 依存関係の参照元:
  - `design.md` の Completion Signal Taxonomy、Blocker Precedence、Interface Contract、Module Dependency Diagram。
- 順序ルール:
  - Upstream collector taxonomy を先に固定し、snapshot / wait がその decision を受け取る。
  - Docs は behavior が固定された後に更新する。
  - Final gate は provider tests、SpecDock validate、reviewer gate の順に閉じる。
- step 依存サマリー:
  - S01 collector taxonomy:
    - 依存: reviewed requirement / design。
    - unblock: S02, S03, S90。
    - 対象ファイル: `pr_review_snapshot.py`, `tests/unit/infra/test_init_update.py`。
  - S02 snapshot propagation:
    - 依存: S01。
    - unblock: S03。
    - 対象ファイル: `pr_observation_snapshot.py`, `tests/unit/infra/test_init_update.py`。
  - S03 wait propagation:
    - 依存: S01, S02。
    - unblock: S90, S99。
    - 対象ファイル: `pr_observation_wait.py`, `tests/unit/infra/test_init_update.py`。
  - S90 docs impact:
    - 依存: S01-S03。
    - unblock: S99。
    - 対象ファイル: `github-pr-observation/SKILL.md`、必要な dogfooding mirror inspection。
  - S99 final quality gate:
    - 依存: S01-S90。

## ステップ一覧
- S01:
  - 観測可能な振る舞い: Collector が strict no-findings issue comment を `codex_no_findings_issue_comment` review-level completion として分類し、generic fallback と分ける。
  - 依存: requirement / design pass。
  - unblock: snapshot / wait propagation。
  - 対象ファイル: `pr_review_snapshot.py`, `tests/unit/infra/test_init_update.py`。
  - 閉じる要件: AC-001, AC-002, AC-004, EC-001, EC-002, EC-003。
  - レビューゲート: code-reviewer。
- S02:
  - 観測可能な振る舞い: Snapshot が collector の review-level completion と CI / PR metadata / head match を統合し、top-level pass または blocker action を返す。
  - 依存: S01。
  - unblock: wait propagation。
  - 対象ファイル: `pr_observation_snapshot.py`, `tests/unit/infra/test_init_update.py`。
  - 閉じる要件: AC-001, AC-003, AC-004, EC-004, EC-005, EC-006。
  - レビューゲート: code-reviewer。
- S03:
  - 観測可能な振る舞い: Wait loop が new signal を terminal pass として扱い、generic fallback は non-retryable human action として扱う。
  - 依存: S01, S02。
  - unblock: docs / final gate。
  - 対象ファイル: `pr_observation_wait.py`, `tests/unit/infra/test_init_update.py`。
  - 閉じる要件: AC-001, AC-002, AC-003。
  - レビューゲート: code-reviewer。
- S90:
  - 観測可能な振る舞い: Operator-facing docs が new signal / generic fallback / retryability を正しく説明する。
  - 依存: S01-S03。
  - unblock: S99。
  - 対象ファイル: `github-pr-observation/SKILL.md`。
  - 閉じる要件: AC-005。
  - レビューゲート: spec-reviewer。
- S99:
  - 観測可能な振る舞い: Issue-wide diff が requirement / design / plan と整合し、実行へ渡せる。
  - 依存: S01-S90。
  - レビューゲート: qa-reviewer, code-reviewer, spec-reviewer。

## 要件 ↔ ステップ対応
- AC-001 -> S01, S02, S03
- AC-002 -> S01, S03
- AC-003 -> S02, S03
- AC-004 -> S01, S02
- AC-005 -> S90
- EC-001 -> S01
- EC-002 -> S01
- EC-003 -> S01
- EC-004 -> S02
- EC-005 -> S02
- EC-006 -> S02

## 仕様固定クロージャ索引（Spec-Locked Closure Index）

| 識別子（ID） | ステップ（step） | スライス（slice） | 種別（type） | 仕様リンク | 固定する期待値 | 観測可能な入力 / 状態 | 防ぐ bug class | 必須 | 証跡レベル（evidence level） | クロージャ証跡（closure evidence） |
|---|---|---|---|---|---|---|---|---|---|---|
| tc-001 | S01 | collector no-findings signal | acceptance | AC-001, EC-001, EC-002 | Strict no-findings comment becomes `codex_no_findings_issue_comment` with `confidence=medium` and mandatory `no_findings_completion_candidate` | fake `gh` issue comments with current trigger, expected head, no PR review | transport mismatch false block | yes | red-required | report Step/Test Contract Closure |
| tc-002 | S01 | generic fallback | negative | AC-002, EC-003 | Generic Codex issue comment remains `fallback_issue_comment`, low confidence, non-promoting | fake `gh` issue comments with ambiguous body | generic issue comment false pass | yes | red-required | report Step/Test Contract Closure |
| tc-003 | S01 | head boundary | negative | AC-004 | Missing `--head-sha` or boundary mismatch does not promote to new signal | collector call without expected head or with old trigger window | stale / unproven head false pass | yes | red-required | report Step/Test Contract Closure |
| tc-004 | S02 | snapshot top-level promotion | acceptance | AC-001 | Snapshot returns top-level `passed` / `merge_prepared` only after CI passed, open non-draft PR, head match, no blockers | collector new signal + green CI + clean metadata | collector-only merge authority confusion | yes | red-required | report Step/Test Contract Closure |
| tc-005 | S02 | blocker precedence | negative | AC-003, EC-004, EC-005, EC-006 | CI / PR metadata / review blockers / limitations override no-findings signal | fake snapshot with new signal plus blocker | no-findings overrides blocker | yes | red-required | report Step/Test Contract Closure |
| tc-006 | S03 | wait propagation | acceptance | AC-001, AC-002 | Wait returns `passed` / `merge_prepared` for new signal, but generic fallback returns `human_gate` / `manual_review_required_non_retryable` | wait helper payloads for new signal and fallback | retryable/non-retryable action confusion | yes | red-required | report Step/Test Contract Closure |
| tc-007 | S90 | docs semantics | acceptance | AC-005 | Skill doc explains submitted review, no-findings issue comment, generic fallback, missing completion, retryability | provider-side `SKILL.md` inspection | operator misinterprets actions | yes | inspect-only | report Docs Impact Resolution |

## レビュー / QA ゲート方針
- RG1 step review:
  - 実施タイミング: 各 implementation step の report update 前後、commit 前。
  - reviewer: S01-S03 は code-reviewer、S90 は spec-reviewer。
  - pass 条件: `review_status: pass`。
- QG1 final QA:
  - reviewer: qa-reviewer。
  - 範囲: closure coverage、missing high-value tests、manual / integration test 要否。
- SG1 final spec review:
  - reviewer: spec-reviewer。
  - 範囲: requirement / design / plan / report / docs / implementation の整合。

## 実行ルール（全ステップ共通）
- 各 implementation step は 1 behavior slice / 1 review scope / 1 commit boundary とする。
- Provider-side source が実装 authority。Dogfooding mirror は必要な inspection / validate 対象。
- Parent agent は原則 orchestration / integration / reviewer gate を担い、file mutation step は plan の delegated role に従う。
- Observed evidence は `report.md` に記録し、`plan.md` へ実行結果を書き戻さない。
- Plan 外の behavior / test obligation が見つかった場合は、report に発見を残し、必要なら plan amendment / re-review へ戻す。

## 実装ステップ

### 実装ステップ S01 — Collector no-findings signal taxonomy
- 振る舞いの目標:
  - `pr_review_snapshot.py` が strict no-findings issue comment を generic fallback と分け、review-level completion signal と mandatory evidence を返す。
- design 参照:
  - Completion Signal Taxonomy、昇格条件、Interface Contract。
- 依存:
  - requirement review pass、design review pass。
- unblock:
  - S02, S03, S90。
- 対象ファイル:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_review_snapshot.py`
  - `tests/unit/infra/test_init_update.py`
- 計画済み契約:
  - scope:
    - `codex_no_findings_issue_comment` signal、strict allow-list、mandatory `no_findings_completion_candidate`、generic fallback non-promotion、head/boundary rejection を実装・検証する。
  - テスト義務:
    - closure id: tc-001, tc-002, tc-003。
    - coverage rationale: review-level signal taxonomy が downstream 全体の起点であり、false pass / false block 両方の regression risk が高い。
  - Red / 代替証跡:
    - red-required: existing collector tests に failing expectations を追加する。
  - 実装範囲:
    - allowed paths:
      - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_review_snapshot.py`
      - `tests/unit/infra/test_init_update.py`
    - forbidden changes:
      - snapshot / wait logic の実装変更。
      - `fallback_issue_comment` を success へ意味変更すること。
      - arbitrary GitHub endpoint / raw `gh` args の追加。
  - Green 検証:
    - `uv run pytest tests/unit/infra/test_init_update.py -k "review_collector or no_findings or fallback_issue_comment"`
  - Refactor / cleanup ガードレール:
    - Allow-list helper の最小変更に留め、collector 全体の構造 refactor はしない。
  - report 証跡の記録先:
    - Session Log、TDD Evidence、Step Contract Closure、Test Contract Closure、Closure Coverage。
  - amendment trigger:
    - Expected head なしで promotion が必要になる場合。
    - Body matcher を allow-list ではなく substring / regex broad match に広げる必要が出た場合。

#### 委任契約（delegation contract）
- 委任ロール:
  - dev-coder。
- 入力 docs:
  - `spec-dock/active/issue/requirement.md`
  - `spec-dock/active/issue/design.md`
  - `spec-dock/active/issue/plan.md`
  - `workflow_issue.md`
  - 対象 source / tests。
- 許可 paths:
  - S01 対象ファイルのみ。
- 禁止 changes:
  - S02/S03/S90 の対象 file。
  - canonical issue docs の変更。
  - GitHub state / secrets / config の変更。
- 受け入れ条件:
  - tc-001, tc-002, tc-003 が pass し、existing collector fallback tests が意図通り更新される。
- 必須 tests:
  - S01 Green 検証コマンド。
- reviewer focus:
  - code-reviewer: signal taxonomy、head/boundary safety、candidate evidence、backward compatibility。
- 必須出力:
  - changed files、tests run、result、unresolved risks、Ledger Note。
- 停止条件:
  - `--head-sha` なし promotion が必要。
  - allow-list 外の broad matcher が必要。
  - allowed paths 外変更が必要。

#### 具体テストケース一覧
- `tc-s01-001` acceptance: observed Codex Review wording promotes at collector review level
  - 前提: fake `gh` returns current trigger `@codex review`, no PR review object, and Codex issue comment body `Codex Review: Didn't find any major issues. Breezy!`; `--head-sha` matches PR head.
  - 操作: `fetch_pr_review_snapshot.sh` を実行する。
  - 期待結果: `decision.completion_signal == "codex_no_findings_issue_comment"`、`decision.recommended_next_action == "review_completion_observed"`、`decision.no_findings_completion_candidate.source_ids == [100]`。
  - 失敗検出: 実観測文言が generic fallback のまま残る回帰を検出する。
  - 検証方法: `tests/unit/infra/test_init_update.py` の collector fixture。
  - 関連 closure id: tc-001
- `tc-s01-002` negative: generic Codex issue comment remains non-promoting fallback
  - 前提: fake `gh` returns current-boundary Codex issue comment `I am still reviewing this PR.`。
  - 操作: `fetch_pr_review_snapshot.sh` を実行する。
  - 期待結果: `completion_signal == "fallback_issue_comment"`、`confidence == "low"`、`recommended_next_action == "manual_review_required_non_retryable"`、`fallback_pass_candidate.promotes_top_level_status is False`。
  - 失敗検出: generic issue comment が new signal または merge-prepared に昇格する回帰を検出する。
  - 検証方法: existing fallback collector test を更新または追加。
  - 関連 closure id: tc-002
- `tc-s01-003` negative: missing expected head does not promote
  - 前提: strict no-findings issue comment はあるが `--head-sha` を渡さない。
  - 操作: `fetch_pr_review_snapshot.sh` を実行する。
  - 期待結果: `completion_signal != "codex_no_findings_issue_comment"`、`decision.status != "passed"`。
  - 失敗検出: head 未確認の no-findings comment を信頼してしまう回帰を検出する。
  - 検証方法: collector fixture の head-sha 省略ケース。
  - 関連 closure id: tc-003
- `tc-s01-004` negative: no-findings comment outside trigger boundary does not promote
  - 前提: strict no-findings issue comment はあるが、`created_at` が current `--trigger-created-at` より前である。
  - 操作: `fetch_pr_review_snapshot.sh --trigger-comment-id 99 --trigger-created-at 2026-06-08T01:00:00Z` を実行する。
  - 期待結果: old no-findings comment は current selected signal にならず、`completion_signal != "codex_no_findings_issue_comment"`。
  - 失敗検出: 古い no-findings comment を current review completion と誤認する回帰を検出する。
  - 検証方法: collector fixture の old trigger window case。
  - 関連 closure id: tc-003
- `tc-s01-005` negative: expected head mismatch does not promote
  - 前提: strict no-findings issue comment はあるが、comment / PR review context が expected `--head-sha` と一致しない stale head として扱われる。
  - 操作: `fetch_pr_review_snapshot.sh --head-sha <new-head>` を実行し、fake PR review/comment data は old head の signal を返す。
  - 期待結果: `codex_no_findings_issue_comment` に昇格せず、decision は pass しない。
  - 失敗検出: 古い head の no-findings signal を current head の completion と誤認する回帰を検出する。
  - 検証方法: collector fixture の expected head mismatch case。
  - 関連 closure id: tc-003

#### ステップ完了契約（step closure contract）
- closure id:
  - tc-001, tc-002, tc-003
- close 条件:
  - Collector decision が design の signal taxonomy に一致する。
- 検証 evidence:
  - Targeted pytest command result。
- report evidence:
  - Step Contract Closure / Test Contract Closure / Closure Coverage。
- 残リスク:
  - 外部 Codex wording の将来変更は別 follow-up。

#### ステップゲート（step gate）
- report update gate:
  - 実行タイミング: step reviewer gate の前に、S01 の Red / Green / Refactor evidence、Step Contract Closure、Test Contract Closure、Closure Coverage を `report.md` に記録する。
  - pass 条件: report に tc-001, tc-002, tc-003 の observed evidence と未解決リスクが記録済み。
- step reviewer gate:
  - reviewer: code-reviewer。
  - review 範囲: S01 changed files。
  - pass 条件: `review_status: pass`。
- commit / no-op gate:
  - closure 状態: committed。
  - commit 範囲: S01 changed files and report evidence。

### 実装ステップ S02 — Snapshot top-level promotion and blocker precedence
- 振る舞いの目標:
  - Snapshot が collector review-level completion を CI / PR metadata / head match と統合し、top-level `merge_prepared` を安全条件付きで返す。
- design 参照:
  - Blocker Precedence、Collector / snapshot / wait responsibility boundary。
- 依存:
  - S01。
- unblock:
  - S03, S90, S99。
- 対象ファイル:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_snapshot.py`
  - `tests/unit/infra/test_init_update.py`
- 計画済み契約:
  - scope:
    - New signal を top-level pass に伝搬し、CI / metadata / blocker / limitation がある場合は既存 blocker action を優先する。
  - テスト義務:
    - closure id: tc-004, tc-005。
    - coverage rationale: collector-only pass と merge-prepared authority の混同を防ぐ。
  - Red / 代替証跡:
    - red-required: snapshot helper fixture に new signal と blocker variants を追加する。
  - 実装範囲:
    - allowed paths:
      - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_snapshot.py`
      - `tests/unit/infra/test_init_update.py`
    - forbidden changes:
      - Collector matcher / wait loop / docs の変更。
  - Green 検証:
    - `uv run pytest tests/unit/infra/test_init_update.py -k "snapshot and (no_findings or fallback_issue_comment or blocker)"`
  - report 証跡の記録先:
    - Session Log、TDD Evidence、Step Contract Closure、Test Contract Closure、Closure Coverage。
  - amendment trigger:
    - Snapshot が collector decision を再分類せずに安全条件を満たせない場合。

#### 委任契約（delegation contract）
- 委任ロール:
  - dev-coder。
- 入力 docs:
  - requirement / design / plan、S01 result、target source / tests。
- 許可 paths:
  - S02 対象ファイルのみ。
- 禁止 changes:
  - S01 collector implementation、S03 wait implementation、docs。
- 受け入れ条件:
  - tc-004, tc-005 が pass。
- 必須 tests:
  - S02 Green 検証コマンド。
- reviewer focus:
  - code-reviewer: top-level authority, blocker precedence, expected head handling。
- 必須出力:
  - changed files、tests run、result、unresolved risks、Ledger Note。
- 停止条件:
  - CI / metadata 条件を collector へ戻す必要が出た場合。

#### 具体テストケース一覧
- `tc-s02-001` acceptance: snapshot promotes new signal only after green integration
  - 前提: review collector payload has `completion_signal="codex_no_findings_issue_comment"` and `recommended_next_action="review_completion_observed"`; CI passed; PR open non-draft; head matches.
  - 操作: `fetch_pr_observation_snapshot.sh` を fixture collector で実行する。
  - 期待結果: top-level `normalized_status == "passed"`、`recommended_next_action == "merge_prepared"`、`observation_complete is True`。
  - 失敗検出: collector-only signal が top-level に伝搬しない false block を検出する。
  - 検証方法: snapshot helper fixture。
  - 関連 closure id: tc-004
- `tc-s02-002` negative: CI failed overrides no-findings signal
  - 前提: new signal はあるが CI status は `failed`。
  - 操作: `fetch_pr_observation_snapshot.sh` を実行する。
  - 期待結果: top-level `normalized_status == "failed"`、`recommended_next_action == "fix_ci"`、`merge_prepared` にならない。
  - 失敗検出: no-findings comment が failed CI を上書きする回帰を検出する。
  - 検証方法: snapshot fixture の CI failed case。
  - 関連 closure id: tc-005
- `tc-s02-003` negative: CI pending/running/none does not promote
  - 前提: new signal はあるが CI status は `pending`、`running`、または `none`。
  - 操作: `fetch_pr_observation_snapshot.sh` を各 CI status fixture で実行する。
  - 期待結果: top-level status は CI status に対応する wait / non-pass で、`recommended_next_action` は `wait` または既存 CI action、`merge_prepared` にならない。
  - 失敗検出: no-findings comment が non-terminal CI を pass にする回帰を検出する。
  - 検証方法: snapshot fixture の CI non-pass parameterized cases。
  - 関連 closure id: tc-005
- `tc-s02-004` negative: draft and non-open PR do not promote
  - 前提: new signal と green CI はあるが metadata は `isDraft=true`、または `state` が `OPEN` 以外。
  - 操作: `fetch_pr_observation_snapshot.sh` を draft / non-open fixture で実行する。
  - 期待結果: draft は `mark_pr_ready_for_review`、non-open は `reopen_or_use_open_pr` を返し、`merge_prepared` にならない。
  - 失敗検出: no-findings comment が PR lifecycle blocker を上書きする回帰を検出する。
  - 検証方法: snapshot fixture の metadata blocker cases。
  - 関連 closure id: tc-005
- `tc-s02-005` negative: stale head does not promote
  - 前提: new signal と green CI はあるが `head_matches_expected is False` または normalized status が `stale_head`。
  - 操作: `fetch_pr_observation_snapshot.sh --head-sha <old-or-new-mismatch>` を実行する。
  - 期待結果: top-level `normalized_status == "stale_head"`、`recommended_next_action == "rerun_for_current_head"`。
  - 失敗検出: stale head の no-findings signal を current merge-prepared にする回帰を検出する。
  - 検証方法: snapshot fixture の stale head case。
  - 関連 closure id: tc-005
- `tc-s02-006` negative: review blockers and limitations override no-findings signal
  - 前提: new signal と green CI はあるが current unresolved thread、current changes requested、または blocking collection limitation がある。
  - 操作: `fetch_pr_observation_snapshot.sh` を review blocker / limitation fixture で実行する。
  - 期待結果: review blockers は `address_review_feedback`、blocking limitation は `human_gate` または permission action を返し、`merge_prepared` にならない。
  - 失敗検出: no-findings comment が review blocker / collection limitation を上書きする回帰を検出する。
  - 検証方法: snapshot fixture の review blocker / limitation cases。
  - 関連 closure id: tc-005

#### ステップ完了契約（step closure contract）
- closure id:
  - tc-004, tc-005
- close 条件:
  - Snapshot top-level status が design の blocker precedence に一致する。
- 検証 evidence:
  - Targeted pytest command result。
- report evidence:
  - Step Contract Closure / Test Contract Closure / Closure Coverage。
- 残リスク:
  - GitHub API schema drift は既存 limitation path に従う。

#### ステップゲート（step gate）
- report update gate:
  - 実行タイミング: step reviewer gate の前に、S02 の Red / Green / Refactor evidence、Step Contract Closure、Test Contract Closure、Closure Coverage を `report.md` に記録する。
  - pass 条件: report に tc-004, tc-005 の observed evidence と blocker case coverage が記録済み。
- step reviewer gate:
  - reviewer: code-reviewer。
  - review 範囲: S02 changed files。
  - pass 条件: `review_status: pass`。
- commit / no-op gate:
  - closure 状態: committed。
  - commit 範囲: S02 changed files and report evidence。

### 実装ステップ S03 — Wait propagation and non-retryable fallback action
- 振る舞いの目標:
  - Wait loop が new signal を terminal pass として扱い、generic fallback を `manual_review_required_non_retryable` にする。
- design 参照:
  - Completion Signal Taxonomy、Interface Contract。
- 依存:
  - S01, S02。
- unblock:
  - S90, S99。
- 対象ファイル:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py`
  - `tests/unit/infra/test_init_update.py`
- 計画済み契約:
  - scope:
    - wait classification の new signal propagation と generic fallback action の変更。
  - テスト義務:
    - closure id: tc-006。
    - coverage rationale: operator が retryable pending と non-retryable fallback を混同しないことが Issue の主要目的。
  - Red / 代替証跡:
    - red-required: wait classification helper / script fixture に new signal と fallback cases を追加する。
  - 実装範囲:
    - allowed paths:
      - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py`
      - `tests/unit/infra/test_init_update.py`
    - forbidden changes:
      - Collector / snapshot / docs の変更。
  - Green 検証:
    - `uv run pytest tests/unit/infra/test_init_update.py -k "wait and (no_findings or fallback_issue_comment or manual_review_required_non_retryable)"`
  - report 証跡の記録先:
    - Session Log、TDD Evidence、Step Contract Closure、Test Contract Closure、Closure Coverage。
  - amendment trigger:
    - `manual_review_required_non_retryable` が existing consumers と互換しないことが判明した場合。

#### 委任契約（delegation contract）
- 委任ロール:
  - dev-coder。
- 入力 docs:
  - requirement / design / plan、S01/S02 result、target source / tests。
- 許可 paths:
  - S03 対象ファイルのみ。
- 禁止 changes:
  - S01/S02/S90 の対象 file。
- 受け入れ条件:
  - tc-006 が pass。
- 必須 tests:
  - S03 Green 検証コマンド。
- reviewer focus:
  - code-reviewer: wait terminal classification、retryability semantics、existing pending behavior regression。
- 必須出力:
  - changed files、tests run、result、unresolved risks、Ledger Note。
- 停止条件:
  - new action が downstream schema と矛盾する場合。

#### 具体テストケース一覧
- `tc-s03-001` acceptance: wait treats no-findings issue comment as terminal after safe snapshot
  - 前提: wait classification receives snapshot/decision with new signal, CI passed, no blockers.
  - 操作: wait helper または `wait_pr_observation.sh` fixture を実行する。
  - 期待結果: `overall_status == "passed"`、`recommended_next_action == "merge_prepared"`、`observation_complete is True`。
  - 失敗検出: wait が new signal を pending / human_gate に戻す回帰を検出する。
  - 検証方法: wait fixture test。
  - 関連 closure id: tc-006
- `tc-s03-002` negative: generic fallback is non-retryable human gate
  - 前提: wait classification receives generic `fallback_issue_comment` with no no-findings completion.
  - 操作: wait helper または `wait_pr_observation.sh` fixture を実行する。
  - 期待結果: `overall_status == "human_gate"`、`recommended_next_action == "manual_review_required_non_retryable"`、`observation_complete is False`。
  - 失敗検出: repeated resume を促す `wait_or_resume` が generic fallback に残る回帰を検出する。
  - 検証方法: wait fixture test。
  - 関連 closure id: tc-006

#### ステップ完了契約（step closure contract）
- closure id:
  - tc-006
- close 条件:
  - Wait terminal result が design taxonomy に一致する。
- 検証 evidence:
  - Targeted pytest command result。
- report evidence:
  - Step Contract Closure / Test Contract Closure / Closure Coverage。
- 残リスク:
  - Downstream consumers が unknown action を持つ場合は report に compatibility note を残す。

#### ステップゲート（step gate）
- report update gate:
  - 実行タイミング: step reviewer gate の前に、S03 の Red / Green / Refactor evidence、Step Contract Closure、Test Contract Closure、Closure Coverage を `report.md` に記録する。
  - pass 条件: report に tc-006 の observed evidence と downstream compatibility risk が記録済み。
- step reviewer gate:
  - reviewer: code-reviewer。
  - review 範囲: S03 changed files。
  - pass 条件: `review_status: pass`。
- commit / no-op gate:
  - closure 状態: committed。
  - commit 範囲: S03 changed files and report evidence。

### ドキュメント影響の解消ステップ S90（docs impact resolution / docs refresh）
- 対象:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md`
  - Dogfooding mirror `.agents/skills/github-pr-observation/SKILL.md` は provider update / inspection 対象。
- 対応:
  - Completion signal taxonomy、strict no-findings issue comment、generic fallback non-promotion、retryable/non-retryable action を記載する。
  - Operator に `fallback_issue_comment` と `codex_no_findings_issue_comment` の違いが読めるようにする。
- doc update owner:
  - doc-writer。
- spec/doc review:
  - reviewer: spec-reviewer。
  - pass 条件: docs が requirement / design / plan と整合し、未解決の必須 docs 影響が残っていない。

#### 委任契約（delegation contract）
- 委任ロール:
  - doc-writer。
- 入力 docs:
  - requirement / design / plan、S01-S03 result、target SKILL.md。
- 許可 paths:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md`
  - 必要な dogfooding mirror inspection / report evidence。
- 禁止 changes:
  - Python implementation / tests。
  - canonical docs の仕様変更。
- 受け入れ条件:
  - tc-007 が pass。
- 必須 tests または docs-only verification:
  - docs inspection。
  - 必要なら `rg -n "codex_no_findings_issue_comment|manual_review_required_non_retryable|fallback_issue_comment" <target SKILL.md>`。
- reviewer focus:
  - spec-reviewer: docs/spec alignment。
- 必須出力:
  - changed files、inspection result、unresolved risks、Ledger Note。
- 停止条件:
  - Docs update が design の signal taxonomy と矛盾する場合。

#### 具体テストケース一覧
- `tc-s90-001` inspect-only: skill doc explains new taxonomy and actions
  - 前提: S01-S03 の behavior が実装済みで、provider-side `github-pr-observation/SKILL.md` が更新対象。
  - 操作: `SKILL.md` を inspection し、必要なら `rg -n "codex_no_findings_issue_comment|manual_review_required_non_retryable|fallback_issue_comment|review_completion_observed|merge_prepared"` を実行する。
  - 期待結果: docs は submitted PR review、`codex_no_findings_issue_comment`、generic `fallback_issue_comment`、missing completion、retryable pending、non-retryable fallback を区別して説明する。Collector-only output が top-level `merge_prepared` authority だとは主張しない。
  - 失敗検出: Operator-facing docs が generic fallback を pass と誤読させる、または collector-only `merge_prepared` を許す回帰を検出する。
  - 検証方法: docs inspection / `rg` result を report Docs Impact Resolution に記録する。
  - 関連 closure id: tc-007

#### ステップ完了契約（step closure contract）
- closure id:
  - tc-007
- close 条件:
  - Skill doc が AC-005 と設計 taxonomy に一致する。
- 検証 evidence:
  - docs inspection / `rg` result。
- report evidence:
  - Docs Impact Resolution。
- 残リスク:
  - Dogfooding mirror update が別 step になる場合は report に扱いを記録する。

#### ステップゲート（step gate）
- report update gate:
  - 実行タイミング: step reviewer gate の前に、S90 の docs inspection、Docs Impact Resolution、Closure Coverage を `report.md` に記録する。
  - pass 条件: report に tc-007 の docs-only verification と未解決 docs 影響の有無が記録済み。
- step reviewer gate:
  - reviewer: spec-reviewer。
  - review 範囲: S90 docs diff。
  - pass 条件: `review_status: pass`。
- commit / no-op gate:
  - closure 状態: committed。
  - commit 範囲: S90 changed files and report evidence。

### 最終品質ゲートステップ S99（final quality gate）
- branch diff 範囲:
  - S01-S90 の全変更。
- 必須 validation:
  - `uv run pytest tests/unit/infra/test_init_update.py -k "github_pr_observation or pr_observation or fallback_issue_comment or no_findings"`
  - `./spec-dock/scripts/spec-dock validate`
  - `git diff --check`
- final QA gate:
  - reviewer: qa-reviewer。
  - 範囲: Issue 全体の obligation coverage と integration test 要否。
  - pass 条件: reviewer pass。
- final code review ゲート:
  - reviewer: code-reviewer。
  - 範囲: issue-wide integrated diff、責務境界、回帰リスク。
  - pass 条件: `review_status: pass`。
- final spec review ゲート:
  - reviewer: spec-reviewer。
  - 範囲: requirement / design / plan / report / implementation / tests / docs 整合。
  - pass 条件: reviewer pass。
- final commit gate:
  - commit 範囲: final report ledger and any final fixes。
  - final report ledger: Final Quality Gate、Closure Coverage、commit evidence。
  - post-commit external evidence destination: PR observation / merge-preparer flow if PR is created later。

## 未確定事項
- Blocking question:
  - なし。
- Non-blocking risk:
  - Future Codex wording changes may need a follow-up allow-list update.

## 最終完了条件
- AC/EC 達成:
  - tc-001 through tc-007 closed with evidence.
- docs 影響解決:
  - S90 complete and reviewed.
- 全 implementation step 完了:
  - S01-S03, S90 committed or approved-no-op with evidence.
- final quality gate pass:
  - qa-reviewer: pass
  - code-reviewer: pass
  - spec-reviewer: pass
  - validation commands pass or documented blocker / waiver with explicit user risk acceptance.
