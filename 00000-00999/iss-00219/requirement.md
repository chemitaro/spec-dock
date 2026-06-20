---
種別: 要件定義書（Issue）
ID: "iss-00219"
タイトル: "Carryover Unresolved Threads Stop Observation"
関連GitHub: ["#219"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-20"
親: ["epic-00158", "init-local-00003"]
---

# iss-00219 Carryover Unresolved Threads Stop Observation — 要件定義（何を、なぜ行うか）

## 目的
- `github-pr-observation` の wait / snapshot 判定で、過去レビューから残った carryover unresolved thread だけを理由に、現在の `@codex review` 境界の観測を早期終了しないようにする。
- Carryover unresolved thread は actionable inventory として可視化しつつ、current review completion lifecycle とは別軸で扱う。
- Downstream agent / CLI 利用者が、現在レビューを待つべき状態、現在レビューのフィードバックに対応すべき状態、completion unknown として人間監査すべき状態を誤読しない JSON / progress contract にする。

## 背景・現状
- GitHub issue `#219` の観測例では、CI は passed、head は matched、`current_selected_unresolved_count=0`、`completion_signal="none"`、`carryover_unresolved_count=8`、`review_completion_unknown_latency_satisfied=false` であるにもかかわらず、`status_reason="carryover_non_outdated_unresolved_thread"` により `human_gate` / `address_review_feedback` で停止していた。
- `.agents/skills/github-pr-observation/SKILL.md` は、final readiness を current `@codex review` trigger/resume boundary に scope し、carryover unresolved review threads を decision-facing actionable inventory に含めると説明している。
- 現行実装では、`actionable_unresolved_reason(...)` が current selected unresolved thread と carryover unresolved thread を同じ terminal 判定入力として扱い、wait / snapshot classification が carryover-only の状態でも `address_review_feedback` へ早期停止し得る。
- Issue `#218` は `fallback_issue_comment` の completion signal 取り扱いであり、本 Issue の carryover-only premature stop とは別問題である。

## 対象ユーザー / 利用シナリオ
- 主な利用者:
  - PR observation 結果を読んで次 action を決める coding agent / maintainer。
  - `github-pr-merge-preparer` など、PR review observation の JSON contract に依存する downstream workflow。
- 代表シナリオ:
  - PR に過去レビュー由来の non-outdated unresolved thread が残っている。
  - 新しい `@codex review` を投稿した後、CI は passed したが current Codex review の trusted completion signal はまだ観測されていない。
  - Agent は carryover feedback の存在を失わずに、現在レビューの completion / current feedback / latency-guarded unknown のいずれかまで観測を続ける。

## スコープ
- 必須:
  - `wait_pr_observation.sh` / `fetch_pr_observation_snapshot.sh` の final JSON 判定で、current review lifecycle と actionable review inventory を分離する。
  - Carryover-only unresolved threads があり、current completion signal がなく、latency guard 未満の場合は terminal `address_review_feedback` にしない。
  - Latency guard 満了後も current completion signal がない場合は、`review_completion_unknown` として non-pass human gate にし、fresh audit requirement を残す。
  - Current selected unresolved thread / current selected changes requested は、従来通り immediate `human_gate` / `address_review_feedback` とする。
  - Trusted current completion signal があり、carryover unresolved threads が残る場合は、`human_gate` / `address_review_feedback` / `carryover_non_outdated_unresolved_thread` とする。
  - Carryover unresolved counts / ids は guard 未満、guard 満了後、trusted completion 後のいずれでも decision-facing inventory として保持する。
  - Skill docs の `review_completion_unknown` 説明を、actionable inventory 全体が空である前提ではなく、current-boundary selected actionable feedback がない前提へ修正する。
- 禁止:
  - Carryover unresolved thread を audit-only / non-actionable に落とすこと。
  - `selected_unresolved_count == 0` を no review work / merge-ready / pass の根拠にすること。
  - Current review completion signal がない guard 未満状態を `observation_complete=true` として扱うこと。
  - `#218` の fallback issue comment completion policy を本 Issue で変更すること。
- 対象外:
  - GitHub GraphQL の thread 収集範囲や authentication policy の再設計。
  - PR merge preparation 全体の policy 変更。
  - New no-findings artifact contract の定義。
  - Runtime 以外の product feature expansion。

## 境界
- 常に行う:
  - `decision` / `decision_fingerprint` を current trigger/resume boundary の authoritative contract として扱う。
  - Carryover unresolved thread を actionable inventory として JSON に残す。
  - Current review lifecycle の状態と actionable inventory の状態を別々に読めるようにする。
- 判断が必要:
  - 実装時に `decision.actionable_inventory_reason` のような補助 field を追加するか、既存 counts / ids だけで十分に表現するか。
  - Progress line の field spelling は既存 line budget と readable contract の範囲で最小追加にする。
- 行わない:
  - Issue-local な status reason 命名判断を ADR 化しない。
  - Carryover feedback があるだけで current review completion を観測済みとみなさない。
  - Current feedback と carryover feedback を同じ terminal reason に畳み込まない。

## 非交渉制約
- Provider-side installed skill assets が実装の source of truth であり、dogfooding mirror は検証対象として扱う。
- Fresh current review completion が不明な結果を `passed`、merge-ready、no-review-work として扱ってはならない。
- `review_completion_unknown` は non-pass human gate であり、post-unknown fresh audit が必要である。
- Outdated unresolved threads または outdated state unavailable/null の threads は、既存 contract 通り actionable inventory へ昇格しない。

## 前提
- GitHub issue `#219`、source analysis、2件の interview、policy synthesis、3名の deep-consultant 分析から、以下を採用済みとする。
  - Carryover unresolved thread は actionable inventory だが、current `@codex review` completion signal ではない。
  - Latency guard 未満の carryover-only missing-completion 状態は wait/resume 継続にする。
  - Latency guard 満了後の missing-completion 状態は `review_completion_unknown` を再利用し、carryover の存在は structured fields で表す。

## 受け入れ条件
- AC-001: Guard 未満の carryover-only missing-completion は観測継続になる。
  - アクター: PR observation wait caller
  - 前提: CI passed、head matched、current selected unresolved 0、selected changes requested なし、`completion_signal="none"`、`carryover_unresolved_count > 0`、`review_completion_unknown_latency_satisfied=false`。
  - 操作: `wait_pr_observation.sh` または同等の classification を実行する。
  - 期待結果: top-level status は non-terminal wait/resume 系になり、`recommended_next_action="wait_or_resume"`、`observation_complete=false`、`decision.status_reason="missing_current_completion_signal"` を維持する。
  - 観測点: final stdout JSON の top-level fields、`decision`、`wait.review_completion_unknown_latency_satisfied`、carryover count/id fields。
- AC-002: Current selected unresolved feedback は即 feedback 対応になる。
  - アクター: PR observation wait / snapshot caller
  - 前提: CI passed、head matched、current selected unresolved thread または current selected changes requested が存在する。
  - 操作: wait / snapshot classification を実行する。
  - 期待結果: `human_gate` / `address_review_feedback` となり、理由は current selected feedback を示す。
  - 観測点: `decision.status_reason`、top-level `recommended_next_action`、selected thread/comment ids。
- AC-003: Guard 満了後の carryover-only missing-completion は `review_completion_unknown` になる。
  - アクター: PR observation wait caller
  - 前提: AC-001 と同じだが、trigger age と CI-passed age の latency guard を満たしている。
  - 操作: wait classification を実行する。
  - 期待結果: `human_gate` / `human_gate`、`observation_complete=true`、`decision.status="unknown"`、`decision.status_reason="review_completion_unknown"`、`decision.completion_signal="none"`、`wait.post_unknown_fresh_audit_required=true` となる。
  - 観測点: final stdout JSON の top-level fields、`decision`、`wait` metadata、carryover count/id fields。
- AC-004: Trusted completion 後に carryover unresolved が残る場合は feedback 対応になる。
  - アクター: PR observation caller
  - 前提: Current `@codex review` の trusted submitted PR review completion signal が観測され、current selected unresolved はないが carryover unresolved thread が残っている。
  - 操作: wait / snapshot classification を実行する。
  - 期待結果: `human_gate` / `address_review_feedback` / `carryover_non_outdated_unresolved_thread` となり、carryover count/id fields が残る。
  - 観測点: `decision.completion_signal`、`decision.status_reason`、carryover count/id fields。
- AC-005: Snapshot と wait の status contract が矛盾しない。
  - アクター: CLI / downstream agent
  - 前提: AC-001 から AC-004 の各状態。
  - 操作: snapshot script と wait script の classification result を比較する。
  - 期待結果: 同じ意味の状態に対して、one-shot snapshot と wait final JSON が同じ next action family と status reason を返す。
  - 観測点: `fetch_pr_observation_snapshot.sh` equivalent result、`wait_pr_observation.sh` stdout JSON。
- AC-006: Skill docs が二軸モデルを説明する。
  - アクター: future coding agent
  - 前提: `.agents/skills/github-pr-observation/SKILL.md` を読む。
  - 操作: `review_completion_unknown`、carryover unresolved threads、`selected_unresolved_count == 0` の意味を確認する。
  - 期待結果: Current review lifecycle と actionable inventory が別軸であり、carryover-only は current completion signal の代替ではないことが読める。
  - 観測点: Skill docs diff と spec review。

## 例外・エッジケース
- EC-001: Fallback issue comment がある。
  - 条件: `completion_signal="fallback_issue_comment"` または fallback low-confidence signal がある。
  - 期待: `#218` の範囲として扱い、本 Issue では trusted completion へ昇格しない。
  - 観測点: fallback-related status reason / next action が既存 contract から不用意に変わらないこと。
- EC-002: Carryover thread が outdated または outdated state unavailable/null。
  - 条件: GitHub thread data が outdated、または outdated state を信頼できない。
  - 期待: 既存 contract 通り audit/limitation context に留め、actionable inventory へ昇格しない。
  - 観測点: actionable unresolved counts/ids に含まれないこと。
- EC-003: CI が pending/running/failed/stale head。
  - 条件: CI または head state が review lifecycle 判定以前に blocking である。
  - 期待: CI/head state が既存通り優先され、本 Issue の carryover policy が CI/head 判定を上書きしない。
  - 観測点: top-level status reason / next action。
- EC-004: No carryover、no current selected feedback、completion signal none、guard 満了。
  - 条件: actionable inventory が空で current completion signal がない。
  - 期待: 既存の `review_completion_unknown` path を維持する。
  - 観測点: `decision.status_reason="review_completion_unknown"`、fresh audit requirement。

## 入力→出力例
- EX-001: Guard 未満 carryover-only
  - 入力:
    - `ci.status="passed"`, `head_matches_expected=true`, `decision.current_selected_unresolved_count=0`, `decision.completion_signal="none"`, `decision.carryover_unresolved_count=8`, `wait.review_completion_unknown_latency_satisfied=false`
  - 出力:
    - `normalized_status="pending"`, `recommended_next_action="wait_or_resume"`, `observation_complete=false`, `decision.status_reason="missing_current_completion_signal"`
- EX-002: Guard 満了 carryover-only
  - 入力:
    - EX-001 に加えて `wait.review_completion_unknown_latency_satisfied=true`
  - 出力:
    - `normalized_status="human_gate"`, `recommended_next_action="human_gate"`, `observation_complete=true`, `decision.status_reason="review_completion_unknown"`, `wait.post_unknown_fresh_audit_required=true`
- EX-003: Trusted completion + carryover
  - 入力:
    - `decision.completion_signal="submitted_pull_request_review"`, `decision.current_selected_unresolved_count=0`, `decision.carryover_unresolved_count=8`
  - 出力:
    - `normalized_status="human_gate"`, `recommended_next_action="address_review_feedback"`, `decision.status_reason="carryover_non_outdated_unresolved_thread"`

## 用語（ドメイン語彙）
- Current review lifecycle:
  - Current `@codex review` trigger/resume boundary に対する Codex review の pending / completed / fallback / unknown / missing-completion 状態。
- Actionable review inventory:
  - Current selected unresolved feedback と、GitHub thread data 上で `isResolved=false` かつ `isOutdated=false` と観測された carryover unresolved review threads の集合。
- Current selected feedback:
  - Current trigger boundary の selected reviews / comments / threads から得られる unresolved thread または changes requested evidence。
- Carryover unresolved thread:
  - Current selected feedback ではないが、latest-head 側で non-outdated unresolved と観測できる review thread。
- `review_completion_unknown`:
  - CI passed、head matched、current-boundary selected blocker がなく、trusted current completion signal が latency guard 後も見つからない non-pass human gate。Carryover inventory の有無は structured fields で別途表す。

## 未確定事項
- Blocking question:
  - なし。
- Non-blocking implementation choice:
  - `decision.actionable_inventory_reason` を追加するかは design/implementation で最小互換性を確認して決める。追加しない場合でも counts/ids と status reason の組み合わせで AC を満たす必要がある。
