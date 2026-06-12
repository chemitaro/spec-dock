---
種別: 実装計画書（Issue）
ID: "iss-00182"
タイトル: "Limit PR observation final status to current trigger boundary"
関連GitHub: ["#182"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-12"
依存: ["requirement.md", "design.md"]
親: ["epic-00067", "init-local-00003"]
---

# iss-00182 Limit PR observation final status to current trigger boundary — 実装計画

## この計画で満たす要件ID

- AC-001: historical thread は final decision に混ざらない
- AC-002: current selected unresolved thread は final decision に反映される
- AC-003: fallback issue comment は top-level pass にしない
- AC-004: fallback no-major-issues comment は準成功信号として観測できる
- AC-005: fingerprint は decision と audit で分離される
- AC-006: output semantics が docs に固定される
- EC-001: trigger が推定である場合
- EC-002: selected ids が空で fallback comment もない場合
- EC-003: current selected review thread と historical thread が同時に存在する場合
- EC-004: existing consumer が legacy `review.threads` を読んでいる場合

## 依存関係から導く実装順序

1. `fetch_pr_review_snapshot.sh`
   - collector が decision/current/audit surfaces、selected ids、fallback candidate、fingerprint split の上流 contract を作る。
2. `fetch_pr_observation_snapshot.sh`
   - collector の decision surface と CI/head/limitations を統合し、one-shot final status/action/reason を決める。
3. `wait_pr_observation.sh`
   - decision fingerprint と decision/current counts を使って wait stability と progress を決める。
4. `SKILL.md`
   - 実装済み output semantics を shipped skill contract として説明する。
5. S90 / S99
   - docs impact、QA、issue-wide code review、final spec review を閉じる。

## ステップ一覧

- S01: collector に decision/current/audit surfaces と fingerprint split を追加する。
- S02: snapshot classification を decision surface ベースに更新する。
- S03: wait stability と progress を decision-scoped に更新する。
- S04: shipped skill docs に output boundary semantics を固定する。
- S90: docs impact resolution を行う。
- S99: final quality gate を通す。

## 要件 ↔ ステップ対応

- AC-001 -> S01, S02, S03
- AC-002 -> S01, S02, S03
- AC-003 -> S02, S03
- AC-004 -> S01, S02, S03
- AC-005 -> S01, S03
- AC-006 -> S04, S90
- EC-001 -> S01, S02
- EC-002 -> S02, S03
- EC-003 -> S01, S02, S03
- EC-004 -> S01, S04

## 仕様固定クロージャ索引（Spec-Locked Closure Index）

| 識別子（ID） | ステップ | スライス | 種別 | 仕様リンク | 固定する期待値 | 観測可能な入力 / 状態 | 防ぐ bug class | 必須 | 証跡レベル | クロージャ証跡 |
|---|---|---|---|---|---|---|---|---|---|---|
| cli-001 | S01, S02, S03 | historical audit separation | acceptance | AC-001, EC-003 | historical unresolved thread は decision blocker にならない | explicit trigger、old unresolved thread、current fallback comment | historical blocker contamination | yes | red-required | report Step/Test Closure |
| cli-002 | S01, S02, S03 | current blocker decision | acceptance | AC-002 | current selected unresolved thread は human gate / feedback action になる | current selected unresolved Codex thread | current review feedback ignored | yes | red-required | report Step/Test Closure |
| cli-010 | S01, S02, S03 | current changes requested decision | acceptance | AC-002 | current selected changes-requested review/comment は `current_selected_changes_requested` reason で human gate / feedback action になる | current selected Codex review or review comment with changes requested | current changes-requested evidence ignored or collapsed into unrelated reason | yes | red-required | report Step/Test Closure |
| cli-003 | S02, S03 | fallback non-promotion | acceptance | AC-003 | `fallback_issue_comment` は top-level pass / complete にならない | CI passed、head matched、selected unresolved 0、fallback comment | low-confidence comment over-promotes readiness | yes | red-required | report Step/Test Closure |
| cli-004 | S01, S02, S03 | fallback candidate signal | acceptance | AC-004 | no-major-issues fallback comment は `fallback_pass_candidate` として観測できる | current boundary Codex issue comment | useful fallback signal hidden | yes | red-required | report Step/Test Closure |
| cli-005 | S01, S03 | fingerprint split | acceptance | AC-005 | historical-only change で `decision_fingerprint` は変わらない | same current decision、changed historical thread | wait reset by audit-only change | yes | red-required | report Step/Test Closure |
| cli-006 | S04, S90 | docs semantics | inspect-only | AC-006 | authoritative / audit-only surfaces が docs に明記される | post-change `SKILL.md` | downstream output misread | yes | inspect-only | report Docs Impact / Spec Review |
| cli-007 | S01, S02 | inferred boundary | negative / compatibility | EC-001 | inferred trigger は confidence / limitation を保持し decision/audit を混ぜない | inferred trigger snapshot | inferred treated as fully explicit | yes | covered-existing + update | report Step/Test Closure |
| cli-008 | S02, S03 | missing completion safe-side | negative | EC-002 | no current completion signal は pass にならない | CI passed、no selected review、no fallback | absence of evidence becomes success | yes | red-required | report Step/Test Closure |
| cli-009 | S01 | legacy compatibility | compatibility | EC-004 | legacy fields は残り all-fetched / non-authoritative scope が分かる | historical context in legacy output | debug consumer breakage / ambiguous legacy fields | yes | red-required | report Step/Test Closure |

## レビュー / QA ゲート方針

- S01, S02, S03:
  - worker: `dev-coder`
  - reviewer: per-step `code-reviewer`
  - standard: each step is one behavior slice / one review scope / one commit.
- S04:
  - worker: `doc-writer`
  - reviewer: `spec-reviewer` docs/spec alignment.
  - If tests are materially changed, add `code-reviewer` for test diff.
- S90:
  - reviewer: `spec-reviewer`
- S99:
  - `qa-reviewer`
  - issue-wide `code-reviewer`
  - final `spec-reviewer`

Fresh pass だけを gate pass とする。

## 実装ステップ S01 — collector emits decision/current/audit surfaces

### 振る舞いの目標

`fetch_pr_review_snapshot.sh` の existing selected/current calculation を、authoritative `decision` と explanatory `review.current`、debug-only `review.audit` として出力する。`decision_fingerprint` と `audit_fingerprint` を分ける。

### design 参照

- `design.md`:
  - インターフェース契約
  - fingerprint 設計
  - 依存関係分析
  - テスト戦略

### 計画済み契約

- scope:
  - 実装・文書化する範囲:
    - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_review_snapshot.sh`
    - `.agents/skills/github-pr-observation/scripts/lib/fetch_pr_review_snapshot.sh`（dogfooding mirror parity）
    - focused tests in `tests/unit/infra/test_init_update.py`
- テスト義務:
  - closure id:
    - `cli-001`, `cli-002`, `cli-004`, `cli-005`, `cli-007`, `cli-009`
  - coverage rationale:
    - collector は downstream snapshot/wait の source-of-truth なので public JSON contract を red-first で固定する。
- Red / 代替証跡の要件:
  - red-required:
    - decision/current/audit surfaces
    - selected unresolved count / ids
    - selected changes-requested review/comment evidence and reason
    - fallback candidate
    - decision/audit fingerprint split
    - legacy all-fetched scope metadata
  - covered-existing:
    - inferred trigger 周辺の既存 test がある場合は sensitivity を確認して不足 assertion を追加する。
- Green 検証:
  - `uv run pytest tests/unit/infra/test_init_update.py -k "review_collector or pr_observation_review_collector or issue_176_s03"`
  - shared helper に影響した場合は `uv run pytest tests/unit/infra/test_init_update.py`
- Refactor / cleanup ガードレール:
  - legacy `review.threads`, `review.signals`, `review.codex_authored` を削除しない。
  - `review.codex_authored` の list shape を壊す必要が出たら sibling metadata 方式を優先する。
- amendment trigger:
  - fallback candidate の本文判定が narrow whitelist を超えて自然言語分類になりそうな場合。
  - legacy field shape の breaking change が必要になった場合。

### 委任契約

- 委任ロール:
  - `dev-coder`
- 入力 docs:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - research / interview / design draft discussions
  - target script and existing tests
- 許可 paths:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_review_snapshot.sh`
  - `.agents/skills/github-pr-observation/scripts/lib/fetch_pr_review_snapshot.sh`（provider asset と同一内容へ同期する dogfooding mirror）
  - `tests/unit/infra/test_init_update.py`
- 禁止 changes:
  - `fetch_pr_observation_snapshot.sh`
  - `wait_pr_observation.sh`
  - `SKILL.md`
  - canonical docs
  - unrelated installer / update behavior
- 受け入れ条件:
  - `decision.scope`, `decision.trigger`, selected ids/counts, `fallback_pass_candidate`, `review.current`, `review.audit`, legacy scope metadata, `decision_fingerprint`, `audit_fingerprint` が design と一致する。
  - current selected changes-requested review/comment が `decision.status_reason == "current_selected_changes_requested"` に必要な decision evidence として表現される。
- 必須 tests:
  - targeted pytest above.
- reviewer focus:
  - `code-reviewer`: output compatibility, shell/Python JSON construction, trigger identity in fingerprint, no body/secret leakage regression.
- 停止条件:
  - selected current thread semantics が design と矛盾する。
  - fallback candidate matching が broad NLP を必要とする。
  - legacy compatibility が breaking になる。
- 必須出力:
  - changed files
  - verification result
  - unresolved risks
  - `Ledger Note` or `No material implementation decisions beyond the approved plan.`

### 具体テストケース一覧

- `tc-s01-001` acceptance: historical thread is audit-only
  - 前提: explicit trigger after an old unresolved Codex thread; no selected current thread.
  - 操作: fake `gh` で `fetch_pr_review_snapshot.sh` を実行する。
  - 期待結果: `decision.selected_unresolved_count == 0`。old thread は `review.audit` または all-fetched legacy field に non-authoritative scope 付きで残り、`review.current.selected_unresolved_thread_ids` には入らない。
  - 失敗検出: old unresolved thread が decision-facing count または decision fingerprint を変える。
  - 検証方法: `tests/unit/infra/test_init_update.py` に collector test を追加 / 更新。
  - 関連 closure id: `cli-001`, `cli-009`

- `tc-s01-002` acceptance: current selected unresolved thread is decision-facing
  - 前提: explicit trigger 後の selected Codex review comment が unresolved thread に紐づく。
  - 操作: fake PR review/comment/thread payload で collector を実行する。
  - 期待結果: `decision.selected_unresolved_thread_ids` と `selected_unresolved_count` に selected thread が入り、`review.current` にも出る。
  - 失敗検出: current selected thread が audit にしか出ない。
  - 検証方法: existing `test_issue_176_s03_review_collector_returns_codex_review_contract` pattern を拡張する。
  - 関連 closure id: `cli-002`

- `tc-s01-003` acceptance: fallback pass candidate is explicit and non-promoting
  - 前提: current boundary の Codex issue comment が no-major-issues 相当本文を持ち、submitted PR review はない。
  - 操作: collector を実行する。
  - 期待結果: `decision.fallback_pass_candidate.present == true`、source id は issue comment、`promotes_top_level_status == false`、lifecycle は `fallback_issue_comment`。
  - 失敗検出: candidate が欠落する、または primary submitted review 扱いになる。
  - 検証方法: existing fallback collector test を更新または sibling test を追加する。
  - 関連 closure id: `cli-004`

- `tc-s01-004` acceptance: decision and audit fingerprints split
  - 前提: current decision artifacts は同一で、historical-only thread だけが異なる二つの payload。
  - 操作: collector を二回実行する、または test helper で二つの fake output を作る。
  - 期待結果: `decision_fingerprint` は同一、`audit_fingerprint` は変化し得る。
  - 失敗検出: historical-only change が decision fingerprint を変える。
  - 検証方法: collector test を追加する。
  - 関連 closure id: `cli-005`

- `tc-s01-005` acceptance: current selected changes-requested evidence is decision-facing
  - 前提: explicit trigger 後の Codex review または review comment が changes requested 相当で selected current artifact になる。
  - 操作: fake review / comment payload で collector を実行する。
  - 期待結果: decision/current surface から selected changes-requested evidence を識別でき、snapshot が `current_selected_changes_requested` を判定できる情報が出る。
  - 失敗検出: changes-requested evidence が audit/legacy にしか出ない、または unresolved thread と区別できない。
  - 検証方法: collector test を追加 / 更新する。
  - 関連 closure id: `cli-010`

### ステップ完了契約

- close 条件:
  - S01 の required closure ids が pass。
  - legacy debug fields が観測可能。
  - per-step `code-reviewer` が pass。
- report evidence:
  - TDD evidence
  - Step Contract Closure
  - Test Contract Closure
  - Closure Coverage
  - Implementation Delegation Gate
  - Reviewer Gate Status
  - Step Commit Gate

### ステップゲート

- step reviewer gate:
  - reviewer: `code-reviewer`
  - pass 条件: `review_status: pass`
- commit / no-op gate:
  - closure state: `committed`
  - commit scope: S01 allowed files only

## 実装ステップ S02 — snapshot classification reads decision surface

### 振る舞いの目標

`fetch_pr_observation_snapshot.sh` が mixed `review.threads` ではなく collector `decision` と CI/head/limitations から final status、recommended action、status reason、observation complete、fingerprint を決める。

### 計画済み契約

- scope:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/fetch_pr_observation_snapshot.sh`
  - `.agents/skills/github-pr-observation/scripts/fetch_pr_observation_snapshot.sh`（dogfooding mirror parity）
  - focused tests in `tests/unit/infra/test_init_update.py`
- テスト義務:
  - closure id:
    - `cli-001`, `cli-002`, `cli-010`, `cli-003`, `cli-004`, `cli-008`
  - coverage rationale:
    - one-shot final JSON は downstream agent が直接読む public contract であり、classification precedence を固定する必要がある。
- Red / 代替証跡の要件:
  - red-required:
    - historical unresolved thread が feedback action にならない。
    - current selected unresolved thread が feedback action になる。
    - current selected changes-requested review/comment が feedback action になる。
    - fallback candidate は top-level pass にしない。
    - missing completion は pass にしない。
- Green 検証:
  - `uv run pytest tests/unit/infra/test_init_update.py -k "pr_observation_snapshot or fetch_pr_observation_snapshot or fallback_issue_comment or review_collector"`
  - shared helper に影響した場合は full file test。
- Refactor / cleanup ガードレール:
  - collector の selection logic を snapshot 側に重複実装しない。
  - status reason は design の taxonomy から増やさない。増やす必要があれば design/plan amendment。
- amendment trigger:
  - status taxonomy では分類できない branch が見つかった場合。
  - top-level fingerprint と decision fingerprint の互換方針が衝突する場合。

### 委任契約

- 委任ロール:
  - `dev-coder`
- 許可 paths:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/fetch_pr_observation_snapshot.sh`
  - `.agents/skills/github-pr-observation/scripts/fetch_pr_observation_snapshot.sh`（provider asset と同一内容へ同期する dogfooding mirror）
  - `tests/unit/infra/test_init_update.py`
- 禁止 changes:
  - S01 の collector contract を無断変更しない。
  - `wait_pr_observation.sh`
  - `SKILL.md`
  - canonical docs
- 受け入れ条件:
  - top-level classification は decision surface と CI/head/limitations に基づく。
  - fallback issue comment は `human_gate` / `wait_or_resume`。
  - current selected changes-requested evidence は `current_selected_changes_requested` reason で `address_review_feedback` になる。
  - `fallback_pass_candidate` は final JSON で観測できる。
- 必須 tests:
  - targeted pytest above.
- reviewer focus:
  - `code-reviewer`: precedence, top-level compatibility, status_reason correctness.
- 停止条件:
  - S01 output が存在しない / stale。
  - decision と legacy fields が矛盾し、どちらを優先するか未定。
- 必須出力:
  - changed files, tests, verification, risks, ledger note.

### 具体テストケース一覧

- `tc-s02-001` acceptance: historical unresolved thread does not drive final action
  - 前提: collector output has `decision.selected_unresolved_count == 0`, audit/legacy unresolved count is 1, CI passed, head matched, fallback issue comment present.
  - 操作: fake collector/checks payload で snapshot script を実行する。
  - 期待結果: `recommended_next_action == "wait_or_resume"` and `status_reason == "fallback_issue_comment_low_confidence"`。`address_review_feedback` ではない。
  - 失敗検出: all-fetched unresolved count が feedback action を決める。
  - 検証方法: snapshot test を追加。
  - 関連 closure id: `cli-001`, `cli-003`

- `tc-s02-002` acceptance: current selected unresolved thread drives review feedback
  - 前提: collector `decision.selected_unresolved_thread_ids` に current selected thread がある。CI passed、head matched。
  - 操作: snapshot を実行する。
  - 期待結果: top-level `human_gate`、`recommended_next_action == "address_review_feedback"`、`decision.status_reason == "current_selected_unresolved_thread"`。
  - 失敗検出: current selected blocker が無視される。
  - 検証方法: snapshot fake collector test。
  - 関連 closure id: `cli-002`

- `tc-s02-005` acceptance: current selected changes-requested drives review feedback
  - 前提: collector decision に current selected changes-requested review/comment evidence があり、CI passed、head matched。
  - 操作: snapshot を実行する。
  - 期待結果: top-level `human_gate`、`recommended_next_action == "address_review_feedback"`、`decision.status_reason == "current_selected_changes_requested"`。
  - 失敗検出: changes-requested evidence が fallback / missing completion / unresolved thread と混同される、または無視される。
  - 検証方法: snapshot fake collector test。
  - 関連 closure id: `cli-010`

- `tc-s02-003` acceptance: fallback pass candidate stays non-promoting
  - 前提: CI passed、head matched、selected unresolved 0、current fallback no-major-issues comment。
  - 操作: snapshot を実行する。
  - 期待結果: top-level remains `human_gate`, `recommended_next_action == "wait_or_resume"`, `observation_complete is false`, `decision.fallback_pass_candidate.present is true`。
  - 失敗検出: fallback comment が `passed` / complete になる。
  - 検証方法: snapshot test。
  - 関連 closure id: `cli-003`, `cli-004`

- `tc-s02-004` negative: missing current completion signal is not pass
  - 前提: CI passed、head matched、limitations empty、selected review なし、fallback comment なし。
  - 操作: snapshot を実行する。
  - 期待結果: safe-side pending / wait / human-gate result になり、top-level pass にならない。
  - 失敗検出: absence of evidence が success になる。
  - 検証方法: snapshot test。
  - 関連 closure id: `cli-008`

### ステップ完了契約

- close 条件:
  - S02 closure ids pass。
  - per-step `code-reviewer` pass。
- report evidence:
  - Step Contract Closure, Test Contract Closure, Closure Coverage, Implementation Delegation Gate, Reviewer Gate Status, Step Commit Gate。

### ステップゲート

- reviewer: `code-reviewer`
- closure state: `committed`
- commit scope: S02 allowed files only

## 実装ステップ S03 — wait stability and progress are decision-scoped

### 振る舞いの目標

`wait_pr_observation.sh` の `semantic_fingerprint()`、same-fingerprint stability、final wait payload fingerprint、progress summary が decision fingerprint と decision/current counts を使うようにする。

### 計画済み契約

- scope:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh`
  - `.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh`（dogfooding mirror parity）
  - focused tests in `tests/unit/infra/test_init_update.py`
- テスト義務:
  - closure id:
    - `cli-001`, `cli-002`, `cli-010`, `cli-003`, `cli-004`, `cli-005`, `cli-008`
- Red / 代替証跡の要件:
  - red-required:
    - historical-only change で same-fingerprint count が reset されない。
    - progress が audit unresolved count を current blocker として表示しない。
    - current selected changes-requested evidence は wait final status/action でも feedback gate になる。
    - fallback candidate は pass / complete にならない。
- Green 検証:
  - `uv run pytest tests/unit/infra/test_init_update.py -k "pr_observation_wait or wait_pr_observation or issue_174"`
  - shared helper に影響した場合は full file test。
- Refactor / cleanup ガードレール:
  - `trigger_codex_review.sh` の write behavior は変更しない。
  - resume / timeout metadata は既存 contract を維持する。
- amendment trigger:
  - progress に audit counts を表示する必要がある場合は、audit-only label と docs alignment を必須にする。

### 委任契約

- 委任ロール:
  - `dev-coder`
- 許可 paths:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh`
  - `.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh`（provider asset と同一内容へ同期する dogfooding mirror）
  - `tests/unit/infra/test_init_update.py`
- 禁止 changes:
  - `trigger_codex_review.sh`
  - GitHub write semantics
  - S01/S02 contract の無断変更
  - `SKILL.md`
  - canonical docs
- 受け入れ条件:
  - wait は `decision_fingerprint` を優先する。
  - historical-only audit change は wait stability を reset しない。
  - progress は decision/current selected counts を使う。
  - current selected changes-requested evidence は terminal human gate / feedback action になる。
  - fallback issue comment remains terminal human gate but not complete/pass.
- 必須 tests:
  - targeted pytest above.
- reviewer focus:
  - `code-reviewer`: terminal/stability semantics, progress non-authority, timeout/resume compatibility.
- 停止条件:
  - S01/S02 の output が不足。
  - timeout/resume contract と decision fingerprint が矛盾する。
- 必須出力:
  - changed files, tests, verification, risks, ledger note.

### 具体テストケース一覧

- `tc-s03-001` acceptance: historical-only changes do not reset wait stability
  - 前提: same decision fingerprint で audit / legacy thread payload だけが異なる fake snapshot sequence。
  - 操作: `--same-fingerprint-count 2` で wait を実行する。
  - 期待結果: audit-only change をまたいで `same_fingerprint_observed` が進み、final fingerprint は decision fingerprint になる。
  - 失敗検出: audit-only change で semantic change 扱いになり reset / timeout する。
  - 検証方法: `_issue_174_run_wait_fake_snapshots` 系 helper を拡張。
  - 関連 closure id: `cli-005`

- `tc-s03-002` acceptance: wait progress uses decision/current counts
  - 前提: audit unresolved count 1、decision selected unresolved count 0、fallback issue comment。
  - 操作: stderr progress 付きで wait を実行する。
  - 期待結果: progress が historical unresolved count を decision blocker として表示しない。final action は `wait_or_resume`。
  - 失敗検出: progress が audit count から current blocker を示唆する。
  - 検証方法: wait progress test。
  - 関連 closure id: `cli-001`, `cli-003`

- `tc-s03-003` acceptance: current selected unresolved thread remains terminal human gate
  - 前提: fake snapshot に decision selected unresolved thread id と CI passed がある。
  - 操作: wait を実行する。
  - 期待結果: final top-level `human_gate`, `recommended_next_action == "address_review_feedback"`。
  - 失敗検出: selected blocker を無視する、または terminal evidence 後に待ち続ける。
  - 検証方法: wait fake snapshot test。
  - 関連 closure id: `cli-002`

- `tc-s03-005` acceptance: current selected changes-requested remains terminal human gate
  - 前提: fake snapshot に `decision.status_reason == "current_selected_changes_requested"` と CI passed がある。
  - 操作: wait を実行する。
  - 期待結果: final top-level `human_gate`, `recommended_next_action == "address_review_feedback"`。
  - 失敗検出: wait が changes-requested evidence を無視する、または fallback/missing signal として扱う。
  - 検証方法: wait fake snapshot test。
  - 関連 closure id: `cli-010`

- `tc-s03-004` acceptance: fallback issue comment stays non-complete in wait
  - 前提: fake snapshot に fallback pass candidate、CI passed、selected unresolved 0。
  - 操作: terminal gate まで wait を実行する。
  - 期待結果: `human_gate`, `wait_or_resume`, `observation_complete is false`, candidate remains visible。
  - 失敗検出: fallback candidate が pass / complete になる。
  - 検証方法: wait fake snapshot test。
  - 関連 closure id: `cli-003`, `cli-004`

### ステップ完了契約

- close 条件:
  - S03 closure ids pass。
  - per-step `code-reviewer` pass。
- report evidence:
  - Step Contract Closure, Test Contract Closure, Closure Coverage, Implementation Delegation Gate, Reviewer Gate Status, Step Commit Gate。

### ステップゲート

- reviewer: `code-reviewer`
- closure state: `committed`
- commit scope: S03 allowed files only

## 実装ステップ S04 — shipped skill output semantics

### 振る舞いの目標

`github-pr-observation/SKILL.md` に、final decision は current boundary scoped、audit context は non-authoritative、fallback issue comment は low-confidence / non-promoting、wait progress は decision-scoped であることを固定する。

### 計画済み契約

- scope:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md`
  - optional focused test in `tests/unit/infra/test_init_update.py` if existing asset content assertions are appropriate.
- テスト義務:
  - closure id:
    - `cli-006`
- Red / 代替証跡の要件:
  - inspect-only:
    - prose change は manual inspection と `spec-reviewer` docs/spec alignment で閉じる。
  - optional:
    - existing asset content test pattern があれば string assertion を追加してよい。
- Green 検証:
  - `uv run pytest tests/unit/infra/test_init_update.py -k "github_pr_observation or install_root or skill"`
  - docs inspection.
- Refactor / cleanup ガードレール:
  - script public entrypoint や permission boundary を docs 以外で変えない。
- amendment trigger:
  - docs が Option C を超えて fallback pass policy を定義しそうな場合。

### 委任契約

- 委任ロール:
  - `doc-writer`
- 許可 paths:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md`
  - optional focused tests in `tests/unit/infra/test_init_update.py`
- 禁止 changes:
  - scripts
  - canonical docs
  - unrelated skills/docs
- 受け入れ条件:
  - `decision`, `review.current`, `review.audit`, `fallback_pass_candidate`, `decision_fingerprint`, `audit_fingerprint` の semantics が明記される。
- 必須 verification:
  - docs inspection
  - optional targeted pytest if tests changed
- reviewer focus:
  - `spec-reviewer` docs/spec alignment
  - tests changed materially の場合のみ `code-reviewer`
- 停止条件:
  - implemented behavior が approved design と異なる。
- 必須出力:
  - changed files, docs summary, verification / inspection result, unresolved risks, ledger note.

### 具体テストケース一覧

- `tc-s04-001` inspect-only: output boundary semantics documented
  - 前提: S01-S03 behavior が実装済み。
  - 操作: `SKILL.md` を inspect する。
  - 期待結果: `decision` が final decision-facing authority として説明され、`review.audit` / all-fetched legacy fields は audit-only と説明される。
  - 失敗検出: docs が mixed `review.threads.unresolved` を final blocker と読めるまま残る。
  - 検証方法: manual docs inspection and spec-reviewer.
  - 関連 closure id: `cli-006`

- `tc-s04-002` inspect-only: fallback and fingerprint semantics documented
  - 前提: S01-S03 behavior が実装済み。
  - 操作: `SKILL.md` を inspect する。
  - 期待結果: `fallback_issue_comment` は top-level human gate / wait、`fallback_pass_candidate` は non-promoting、wait stability は `decision_fingerprint`、`audit_fingerprint` は debug-only と説明される。
  - 失敗検出: docs が fallback candidate を merge-ready と読ませる、または audit fingerprint が wait stability を制御すると読ませる。
  - 検証方法: manual docs inspection and spec-reviewer.
  - 関連 closure id: `cli-006`

### ステップ完了契約

- close 条件:
  - docs semantics が implemented behavior と一致。
  - `spec-reviewer` docs/spec alignment pass。
- report evidence:
  - Docs Impact, Step Contract Closure, Implementation Delegation Gate, Reviewer Gate Status, Step Commit Gate。

### ステップゲート

- reviewer: `spec-reviewer`
- closure state: `committed`
- commit scope: S04 allowed files only

## S90 docs 影響解決 / docs refresh

### 対象

- Required:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md`
- Candidate if implementation reveals references:
  - shipped docs / templates that describe PR observation output semantics.

### 対応

- S04 で `SKILL.md` を更新する。
- S90 では `rg -n "github-pr-observation|fallback_issue_comment|decision_fingerprint|review\\.threads|human_gate" src/spec_dock/assets spec-dock/docs tests` 等で関連 docs references を点検する。
- 追加 docs 更新不要なら approved-no-op とし、根拠を `report.md` に記録する。

### reviewer

- `spec-reviewer`

## S99 final quality gate

### QA gate

- reviewer:
  - `qa-reviewer`
- scope:
  - AC-001 through AC-006 and EC-001 through EC-004 coverage.
- expected commands:
  - `uv run pytest tests/unit/infra/test_init_update.py`
  - `uv run pytest tests/unit`
  - Broaden to `uv run pytest` if shared install/update or runtime behavior beyond planned files is affected.

### issue-wide code review gate

- reviewer:
  - `code-reviewer`
- scope:
  - integrated diff for S01-S03 and any test changes in S04.
- focus:
  - output contract compatibility
  - shell / embedded Python robustness
  - fingerprint semantics
  - false pass prevention

### final spec review gate

- reviewer:
  - `spec-reviewer`
- scope:
  - `requirement.md`, `design.md`, `plan.md`, `report.md`, implementation, tests, docs alignment.

### SpecDock validation

- `./spec-dock/scripts/spec-dock validate`
- `./spec-dock/scripts/spec-dock sync` if execution updates canonical docs/report and projections require refresh.

### PR delivery gate

Before `issue finish`, record PR delivery evidence in `report.md`.

- PR URL
- selected base branch and base-resolution source
- head branch and head SHA
- issue linkage to `#182` / `iss-00182`
- existing PR reuse or new PR creation decision
- draft / ready decision

### Merge preparation gate

Before `issue finish`, record merge-prepared evidence in `report.md`.

- PR open state
- latest monitored head SHA
- required and non-required check status
- blocking review status
- merge conflict / visible merge blocker status
- unresolved review-thread limitation status
- final merge-prepared decision
- any waiver or blocker classification

## Final Exit Contract

Implementation handoff is ready when:

- requirement/design/plan fresh spec-reviewer pass is recorded in `report.md`.
- delegated draft evidence for design and plan is recorded with draft provenance separated from orchestrator adoption.
- every required closure id has a planned verification path.
- every implementation step has delegation contract, concrete test cases, closure contract, reviewer gate, and commit/no-op gate.

Issue execution is complete only after:

- all S01-S04/S90/S99 gates close in `report.md`;
- required tests pass or failures are classified with evidence;
- per-step reviewer gates pass;
- final QA/code/spec reviewers pass;
- PR Delivery Gate is recorded;
- Merge Preparation Gate is recorded as pass or blocked with explicit next action;
- final commit and clean worktree evidence are recorded externally and/or in delivery evidence.

## 計画上の未解決事項

- なし。

## 実装 watchpoints

- `review.codex_authored` の shape を変える必要がある場合は sibling metadata を優先し、compatibility rationale を `report.md` に記録する。
- no-major-issues phrase matching が narrow whitelist を超える場合は、requirement/design clarification に戻す。
- top-level `fingerprint` compatibility と `decision_fingerprint` semantics が衝突する場合は、`decision_fingerprint` を wait stability の authoritative source として使い、alias / transition decision を `report.md` に記録する。
