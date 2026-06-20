---
種別: interview
ID: "20260620t010354z-interview"
タイトル: "Carryover unknown status reason naming"
状態: "draft | answered | archived"
作成者: "iwasawayuuta"
最終更新: "2026-06-20"
親: ["iss-00219"]
関連: []
scope: "<initiative | epic | issue | local-topic>"
scope_id: "iss-00219"
created_at: "2026-06-20THH:MM:SSZ"
created_by: "iwasawayuuta"
status: "answered"
authority: "synthesized"
adoption_status: "adopted"
derived_from:
  - "20260619t221823z-disc-carryover-review-completion-policy-synthesis.md"
  - "deep-consultant internal-logic report 019ee1ef-a0a9-7311-917e-bb139a7bf3ff"
  - "deep-consultant ui-cli report 019ee1ef-be1d-7250-a18c-f946db56906f"
  - "deep-consultant reason-taxonomy report 019ee290-7d66-7f50-a4e7-28a3d78a86c6"
reflected_to:
  - "requirement.md"
  - "design.md"
---

# 20260620t010354z-interview Carryover unknown status reason naming

## 位置づけ
- 用途: 重要判断に関わる一つの質問を、回答前の source-grounded 正式質問シートとして作成し、回答後に同じ artifact を完成 record にする。
- authority default: `proposed`。ユーザー回答と採用判断を反映した後は、必要に応じて `user-approved` または `synthesized` に更新する。
- この artifact は answer capture / adoption target / reflection の evidence surface であり、main orchestrator が canonical docs / accepted ADR / `report.md` Evidence Adoption Ledger へ採用するまでは canonical authority ではない。
- 技術的に調べられることは先に docs / code / tests / ADR / discussions / primary source を確認する。
- 一つの `interview` artifact には one essential question / 一つの本質的な質問だけを書く。回答によって新しい高影響な曖昧さが見つかった場合は、追加質問をこの file に増やさず、次の unanswered `interview` を作成する。
- trivial な yes/no は、重要な判断、後続反映、回答証跡が必要なら `interview` を使い、そうでなければ issue comment や `scratch` で足りる。
- 回答から複数質問の synthesis が必要になったら `disc`、追加調査が必要になったら `research`、長期判断が固まったら `adr` を新規作成する。

## 正式質問として扱う理由 (必須)
- 影響する artifact:
  - `requirement.md`:
    - Latency guard 満了後も current review completion signal がない場合の observable status reason を受け入れ条件に固定する。
  - `design.md`:
    - `review_completion_unknown` 既存語彙を拡張するか、carryover-specific reason を追加するかで state classification table と JSON contract が変わる。
  - `plan.md`:
    - Guard 満了後 regression test の期待値が変わる。
  - `ADR`:
    - 現時点では不要。既存 PR observation contract 内の命名判断。
- chat 上の軽微な一問では足りない理由:
  - `status_reason` は downstream agent / CLI consumer が分岐に使う machine-readable contract であり、後から rename しにくい。

## 質問の目的 (必須)
- 対象者:
  - SpecDock maintainer / workflow owner
- 何を明確にする質問か:
  - Carryover-only unresolved threads が存在し、latency guard 満了後も current review completion signal がない場合の exact `decision.status_reason`。
- 回答が後続判断へ与える影響:
  - Requirement AC、Design の JSON contract、Plan の red tests、downstream guidance が変わる。

## 質問 (必須)
- pressure-test question:
  - Carryover unresolved threads が残る状態は、既存 `review_completion_unknown` の一種として扱うべきか、それとも distinct reason として表現すべきか。
- 質問:
  - Latency guard 満了後も current `@codex review` の trusted completion signal がなく、かつ carryover unresolved threads が残っている場合、`decision.status_reason` はどちらにしますか？
- 回答してほしいこと:
  - Option A / B / C のいずれを採用するか。

## source-grounded context (必須)
- 確認済みの docs / code / tests / ADR / discussions / primary source:
  - `20260619t221823z-disc-carryover-review-completion-policy-synthesis.md`
  - `.agents/skills/github-pr-observation/SKILL.md`
  - `.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py`
  - `.agents/skills/github-pr-observation/scripts/lib/pr_observation_snapshot.py`
  - `.agents/skills/github-pr-observation/scripts/lib/pr_review_snapshot.py`
  - Deep-consultant reports
- local context で解決できたこと:
  - Latency guard 未満は `missing_current_completion_signal` / `wait_or_resume` / `observation_complete=false`。
  - Current review completion 後に carryover が残る場合は `carryover_non_outdated_unresolved_thread` / `address_review_feedback`。
- まだ人間判断が必要な理由:
  - Guard 満了後は、current completion unknown と carryover actionable inventory が同時に存在する。既存語彙を拡張するか、新しい reason で区別するかは consumer contract の判断になる。

## 回答案 (必須)
- Option A:
  - 既存 `review_completion_unknown` を使う。ただし docs では「actionable inventory empty」ではなく「current-boundary selected actionable feedback empty」と定義を修正し、carryover counts/ids を併記する。
- Option B:
  - 新規 `current_review_completion_unknown_with_carryover_unresolved` を使う。Current completion unknown と carryover actionable が同時にあることを machine-readable に明示する。
- Option C:
  - 新規 `carryover_review_completion_unknown` のような短い carryover-specific reason を使う。

## Codex の分析 (必須)
- 判断軸:
  - Downstream 分岐の明確さ、既存 contract との互換性、operator が状態を誤読しないこと、将来の reason taxonomy。
- tradeoff:
  - Option A は既存語彙を再利用できるが、`review_completion_unknown` の意味を広げるため docs/test の定義修正が必要。
  - Option B は意味が最も明確だが長い。JSON contract としては問題ないが progress line には出しにくい。
  - Option C は短いが、何が unknown なのかやや曖昧。
- リスク:
  - Option A は carryover があるのに unknown とだけ見えて、actionable inventory の存在が軽視される可能性がある。
  - Option B/C は downstream consumer が新 reason を知らない場合、既存 unknown handling に乗らない可能性がある。
- 具体シナリオ / edge case:
  - CI passed、head matched、current selected unresolved 0、completion signal none、carryover unresolved 8、latency guard 満了。この状態は pass ではなく、人間判断/新鮮な監査が必要。

## Codex の推奨案 (必須)
- 推奨:
  - Option A: `review_completion_unknown`
- 理由:
  - 追加 deep-consultant の reason-taxonomy 分析では、`review_completion_unknown` は current `@codex review` の trusted completion signal が latency guards 後も見つからないことを表す主 reason として維持するのが、既存 consumer 互換性と将来拡張性の両面で最も安全とされた。
  - Carryover unresolved threads は GitHub UI / GraphQL 上の実在する actionable inventory だが、current review completion signal ではない。したがって主 `status_reason` に carryover を混ぜず、`carryover_unresolved_count` / `actionable_unresolved_count` / IDs、必要なら `decision.actionable_inventory_reason` で表す。
  - `current_review_completion_unknown_with_carryover_unresolved` は意味は明確だが、reason taxonomy を組み合わせ条件ごとに増やし、既存の `review_completion_unknown` handling から外れるリスクがある。
- 未回答時の影響:
  - Option A 前提で design/plan を進める。既存 docs の「actionable review inventory empty」は「current-boundary selected actionable feedback empty」へ修正する必要がある。

## ユーザー回答 (回答後に必須)
- answer capture:
  - User asked to consult a deep consultant because the judgment depends on GitHub review thread semantics, Codex review lifecycle, CLI/UI behavior, downstream agent branching, and the correct logic rather than the initially listed options.
- 回答:
  - 追加 deep-consultant の分析を採用し、guard 満了後の current review completion unknown + carryover unresolved present は `decision.status_reason="review_completion_unknown"` として扱う。
  - Carryover の存在は `carryover_unresolved_*` / `actionable_unresolved_*` と、必要なら `decision.actionable_inventory_reason="carryover_non_outdated_unresolved_thread"` で表す。
- 回答日時:
  - 2026-06-20

## 追加確認の要否 (回答後に必須)
- 追加確認が必要か:
  - no
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - none

## 採用判断 (回答後に必須)
- adoption_status:
  - adopted
- adoption target:
  - `requirement.md`, `design.md`, `plan.md`
- 採用 / 棄却 / deferred の理由:
  - `status_reason` は current review lifecycle の unknown reason を表し、carryover unresolved threads は別軸の actionable inventory として表す二軸モデルにする。これにより、latency guard 未満の `missing_current_completion_signal`、guard 満了後の `review_completion_unknown`、trusted completion 後の carryover human gate を区別できる。
- `report.md` Evidence Adoption Ledger への反映要否:
  - yes

## requirement / design / plan / ADR への含意 (回答後に必須)
- `requirement.md`:
  - Guard 未満は `pending` / `wait_or_resume` / `observation_complete=false` / `missing_current_completion_signal`。
  - Guard 満了後は `human_gate` / `human_gate` / `observation_complete=true` / `review_completion_unknown` / `post_unknown_fresh_audit_required=true`。
  - Carryover counts/IDs は guard 未満・満了後のどちらでも保持する。
- `design.md`:
  - `actionable_unresolved_reason(...)` を単一 terminal 判定に使わず、current selected blocker と carryover inventory を分離する。
  - `is_review_completion_unknown_candidate` は carryover-only inventory を除外条件にしない。
  - 追加フィールドを許容するなら `decision.actionable_inventory_reason="carryover_non_outdated_unresolved_thread"` を導入候補にする。
- `plan.md`:
  - Guard 未満 carryover-only、guard 満了 carryover-only、current selected unresolved 優先、trusted completion + carryover、empty inventory unknown の regression を固定する。
- `ADR`:
  - 不要。既存 PR observation contract 内の命名判断として扱う。
- reflected_to 更新方針:
  - `requirement.md` / `design.md` へ反映済み。Plan authoring 時に追加更新する。
- adoption reflection:
  - `review_completion_unknown` の説明を「actionable inventory empty」ではなく「current-boundary selected actionable feedback empty」に改め、carryover inventory は structured fields で保持する。

## 条件付き補足 (必要な場合だけ)
- PlantUML 図:
  ```plantuml
  @startuml
  ' TODO: 質問依存、意思決定フロー、before/after、責務境界が必要なら追加する
  @enduml
  ```
- 詳細 tradeoff:
  - ...
- 後続 reflection proposal:
  - ...
- 追加で作る discussion docs:
    - ...
