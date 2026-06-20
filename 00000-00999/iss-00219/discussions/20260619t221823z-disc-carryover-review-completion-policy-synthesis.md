---
種別: disc
ID: "20260619t221823z-disc"
タイトル: "Carryover review completion policy synthesis"
状態: "draft | proposed | archived"
作成者: "iwasawayuuta"
最終更新: "2026-06-19"
親: ["iss-00219"]
関連: []
authority: "synthesized"
derived_from:
  - "20260619t164615z-research-carryover-observation-source-analysis.md"
  - "20260619t164616z-interview-carryover-incomplete-stop-policy.md"
  - "deep-consultant internal-logic report 019ee1ef-a0a9-7311-917e-bb139a7bf3ff"
  - "deep-consultant ui-cli report 019ee1ef-be1d-7250-a18c-f946db56906f"
reflected_to:
  - "requirement.md"
  - "design.md"
---

# 20260619t221823z-disc Carryover review completion policy synthesis

## 位置づけ
- 用途: 集まった質問回答や調査をもとに、意思決定前の synthesis、選択肢、tradeoff、reflection proposal、ADR candidate triage、推奨反映先を整理する。
- authority default: `proposed`。通常は doc type から推定し、例外時だけ front matter の `authority` で override する。
- この artifact は synthesis / reflection proposal / adoption target / ADR triage の evidence surface であり、main orchestrator が canonical docs / accepted ADR / `report.md` Evidence Adoption Ledger へ採用するまでは canonical authority ではない。
- 人間から回答を引き出し、回答欄や未回答事項を管理する場合は `interview` を使う。
- 生ログや未整理の思考は `scratch`、事実確認や外部根拠は `research`、長期判断の固定は `adr` に分ける。
- この doc は proposal / synthesis であり、issue `report.md` の observed evidence ledger ではない。採否の最終証跡は canonical docs / ADR / `report.md` Evidence Adoption Ledger に昇格する。
- doc が大きくなりすぎたら、質問回答は `interview`、事実調査は `research`、raw capture は `scratch`、長期決定は `adr` へ分割する。

## 対象論点 (必須)
- 今回整理する論点:
  - Carryover unresolved review threads が存在するが、current `@codex review` の trusted completion signal がまだない状態を、PR observation がどう表現し、いつ wait loop を止めるべきか。
- この synthesis が必要な理由:
  - GitHub issue `#219` は内部 state machine、Codex review lifecycle、GitHub UI の unresolved/outdated/resolved thread semantics、CLI progress/final JSON、downstream agent action をまたぐ contract 問題である。
  - 初期 interview の Option A/B/C は正解候補とは限らないため、2名の deep-consultant に独立 read-only 分析を依頼した。

## derived question sheets / research (必須)
- `interview`:
  - `20260619t164616z-interview-carryover-incomplete-stop-policy.md`
- `research`:
  - `20260619t164615z-research-carryover-observation-source-analysis.md`
- その他の根拠:
  - GitHub issue `#219`
  - `.agents/skills/github-pr-observation/SKILL.md`
  - `.agents/skills/github-pr-observation/scripts/lib/pr_review_snapshot.py`
  - `.agents/skills/github-pr-observation/scripts/lib/pr_observation_snapshot.py`
  - `.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py`
  - `tests/unit/infra/test_init_update.py`
  - Deep-consultant reports:
    - `019ee1ef-a0a9-7311-917e-bb139a7bf3ff`
    - `019ee1ef-be1d-7250-a18c-f946db56906f`

## synthesis (必須)
- 合意済みのこと:
  - Carryover unresolved thread は無視してよい audit noise ではない。GitHub 上で `isResolved=false` かつ `isOutdated=false` と観測できる限り、latest-head actionable inventory として final JSON に残す。
  - ただし carryover unresolved thread は current `@codex review` の trusted completion signal ではない。
  - Current selected unresolved feedback / current selected changes requested は従来通り immediate terminal `human_gate` / `address_review_feedback` にしてよい。
  - Carryover-only + `completion_signal="none"` + latency guard 未満は terminal `address_review_feedback` にしてはいけない。`observation_complete=false` で wait/resume 継続が正しい。
  - `current review lifecycle` と `actionable review inventory` を別軸として requirement/design に固定する。
- 未合意 / 未確定のこと:
  - Latency guard 満了後の exact `status_reason` 名:
    - 既存 `review_completion_unknown` を定義拡張する案。
    - 新規 `current_review_completion_unknown_with_carryover_unresolved` を使う案。
  - Progress line の carryover count field 名:
    - `carryover_unresolved` が明確。
    - line budget を重視するなら短縮名も候補。
- source-grounded に解決できたこと:
  - `#218` の `fallback_issue_comment` 昇格問題は Issue219 の範囲外。
  - Carryover を non-actionable に落とす案は、既存 skill contract と `iss-00187` の安全性に反する。
  - `selected_unresolved_count == 0` を no review work / pass / merge-ready の根拠にしてはならない。

## 選択肢 / tradeoff (必須)
- Option A:
  - 内容:
    - Carryover-only + current completion missing + latency guard 未満では wait/resume を継続する。Carryover は actionable inventory として counts/ids に残す。
  - Pros:
    - Current review completion を観測し切る。
    - False pass と premature stop の両方を避ける。
    - 2名の deep-consultant が一致して推奨。
  - Cons:
    - Carryover feedback が既にある場合でも、current review completion / unknown まで待つため時間が伸びる。
- Option B:
  - 内容:
    - Carryover-only で早期 partial human gate にするが、`observation_complete=false` と `wait_or_resume` を明示する。
  - Pros:
    - 早く caller に返せる。
  - Cons:
    - Stop を completion と誤読されやすく、Issue219 の premature stop risk を残す。
    - Deep-consultant は通常 wait flow では非推奨。
- Option C:
  - 内容:
    - 現状に近く、carryover-only を即 terminal `address_review_feedback` にする。
  - Pros:
    - 既存実装に近い。
  - Cons:
    - Current review completion 未観測のまま terminal 化するため、Issue219 の主問題を解消しない。
- Option D:
  - 内容:
    - Carryover を non-actionable/audit-only に落とす。
  - Pros:
    - Current completion unknown の扱いは単純になる。
  - Cons:
    - GitHub UI/GraphQL 上の non-outdated unresolved thread を見落とし、`selected_unresolved_count == 0` を no work と誤解させる退行になる。

## reflection proposal (必須)
- canonical docs / workflow / template / skill guidance へ反映すべき候補:
  - Requirement:
    - Carryover-only は merge-ready/pass を阻止するが、current review completion の代替ではない。
    - Latency guard 未満では `pending` / `wait_or_resume` / `observation_complete=false` を固定する。
    - Current selected feedback は immediate `address_review_feedback` を維持する。
  - Design:
    - `current review lifecycle` と `actionable review inventory` を別軸として分類する。
    - `actionable_unresolved_reason(...)` を terminal 判定に直接使わず、current selected blocker と carryover-only blocker を分ける。
    - Progress line では current review 未完了なら `review=pending_signal` を維持しつつ、carryover count を別 field で表示する。
  - Plan:
    - Red tests for carryover-only + missing completion + latency guard未満。
    - Red tests for current selected unresolved immediate terminal。
    - Guard満了後の chosen reason 名を固定する test。
- まだ proposal に留める理由:
  - Exact `status_reason` 名と progress field 名は canonical design authoring で最終固定する必要がある。

## adoption target / 採用先候補 (必須)
- `requirement.md`:
  - 採用済み。
- `design.md`:
  - 採用済み。
- `plan.md`:
  - 採用する。
- `ADR`:
  - 現時点では不要。PR observation skill 内の contract refinement として Issue-local docs に固定する。
- `report.md` Evidence Adoption Ledger:
  - Deep-consultant reports とこの synthesis を採用 evidence として記録する。

## ADR triage / ADR candidate triage (必須)
- ADR candidate か:
  - no
- hard to reverse:
  - no
- surprising without context:
  - yes
- real tradeoff:
  - yes
- ADR 化しない場合の反映先:
  - `disc`, `requirement.md`, `design.md`, `plan.md`, `report.md`

## 推奨案 (必須)
- 採用案:
  - Carryover unresolved thread は actionable inventory として保持する。
  - Current review lifecycle とは別軸に扱う。
  - Latency guard 未満で current `@codex review` completion signal がない場合は、carryover-only で terminal `address_review_feedback` にしない。
  - Authoritative JSON は `pending` / `wait_or_resume` / `observation_complete=false` / `status_reason="missing_current_completion_signal"` を維持し、carryover counts/ids を残す。
  - Current review completion 後に carryover が残る場合は `human_gate` / `address_review_feedback` / `carryover_non_outdated_unresolved_thread` とする。
  - Latency guard 満了後も completion がない場合は non-pass human gate とし、fresh audit requirement を明示する。
- 理由:
  - 2名の deep-consultant が、内部 logic と UI/CLI/operator contract の別観点から同じ二軸モデルを推奨した。
  - GitHub UI/GraphQL の unresolved/outdated/resolved thread semantics と、SpecDock skill の current-boundary final readiness semantics の両方を満たす。

## 推奨反映先 (必須)
- `requirement.md`:
  - 目的、スコープ、受け入れ条件、例外ケース、用語へ反映済み。
- `design.md`:
  - State classification table、module/function impact、JSON contract、progress line contract、test strategy へ反映済み。
- `plan.md`:
  - Red/green step と closure index へ反映する。
- `ADR`:
  - なし。
- `report.md` Evidence Adoption Ledger:
  - この `disc`、research、interview、2件の deep-consultant report を採用 evidence として記録する。

## 未採用 / deferred 理由 (必須)
- 未採用:
  - Carryover-only immediate terminal `address_review_feedback`:
    - Current review completion 未観測のまま stop するため不採用。
  - Carryover audit-only:
    - GitHub 上の non-outdated unresolved thread を隠すため不採用。
  - `selected_unresolved_count == 0` を no review work とみなす案:
    - Existing skill contract と `iss-00187` の安全性に反するため不採用。
- deferred:
  - Latency guard 満了後の exact `status_reason` 名。
  - Progress field exact spelling。

## 次アクション (必須)
- `requirement.md` / `design.md` / `plan.md` / `adr` へ反映する内容:
  - Requirement authoring:
    - carryover inventory と current review lifecycle の二軸 contract を固定する。
  - Design authoring:
    - `pr_observation_snapshot.py` / `pr_observation_wait.py` の terminal 判定差分を設計する。
  - Plan authoring:
    - red tests と implementation steps を設計する。
- 追加で作る discussion docs:
  - 現時点では不要。Exact reason 名の決定で迷う場合のみ追加 `interview` または `disc` を作る。
