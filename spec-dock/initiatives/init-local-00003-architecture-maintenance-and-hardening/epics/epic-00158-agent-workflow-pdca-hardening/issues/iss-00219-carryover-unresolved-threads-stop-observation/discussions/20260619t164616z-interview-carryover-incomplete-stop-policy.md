---
種別: interview
ID: "20260619t164616z-interview"
タイトル: "Carryover incomplete stop policy"
状態: "draft | answered | archived"
作成者: "iwasawayuuta"
最終更新: "2026-06-19"
親: ["iss-00219"]
関連: []
scope: "<initiative | epic | issue | local-topic>"
scope_id: "iss-00219"
created_at: "2026-06-19THH:MM:SSZ"
created_by: "iwasawayuuta"
status: "answered"
authority: "proposed | user-approved | synthesized"
adoption_status: "adopted"
derived_from: []
reflected_to:
  - "requirement.md"
  - "design.md"
---

# 20260619t164616z-interview Carryover incomplete stop policy

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
    - carryover-only unresolved threads を latency guard 未満でどう扱うかが、必須スコープと受け入れ条件を左右する。
  - `design.md`:
    - `classify_snapshot(...)` / `classify(...)` の terminal 判定、`observation_complete`、`recommended_next_action` の設計が変わる。
  - `plan.md`:
    - red test の期待値と step boundary が変わる。
  - `ADR`:
    - 現時点では不要。長期の review completion policy 変更へ広がる場合のみ ADR 候補。
- chat 上の軽微な一問では足りない理由:
  - これは単なる命名ではなく、wait loop がいつ止まるか、下流 agent が resume すべきか review feedback を扱うべきかを決める operator-facing contract であるため。

## 質問の目的 (必須)
- 対象者:
  - SpecDock maintainer / workflow owner
- 何を明確にする質問か:
  - carryover-only unresolved thread があるが current Codex review completion をまだ観測できていない状態を、latency guard 未満で terminal human gate にしてよいか。
- 回答が後続判断へ与える影響:
  - Requirement の AC、Design の state classification、Plan の regression tests、Skill docs の resume guidance が変わる。

## 質問 (必須)
- pressure-test question:
  - CI passed / head matched / current selected unresolved 0 / `completion_signal="none"` / carryover unresolved > 0 / latency guard 未満の状態を、wait loop はどう扱うべきか。
- 質問:
  - Issue219 では、carryover-only unresolved threads がある場合でも current-boundary Codex review completion が未観測なら、latency guard を満たすまで原則 wait/resume を続ける方針でよいですか？
- 回答してほしいこと:
  - A/B/C のどれを採用するか、または別方針があるか。

## source-grounded context (必須)
- 確認済みの docs / code / tests / ADR / discussions / primary source:
  - GitHub issue `#219`
  - `.agents/skills/github-pr-observation/SKILL.md`
  - `.agents/skills/github-pr-observation/scripts/lib/pr_review_snapshot.py`
  - `.agents/skills/github-pr-observation/scripts/lib/pr_observation_snapshot.py`
  - `.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py`
  - `tests/unit/infra/test_init_update.py`
  - `iss-00187` / `iss-00214` requirement docs
  - `discussions/20260619t164615z-research-carryover-observation-source-analysis.md`
- local context で解決できたこと:
  - `#218` は scope 外。
  - current selected unresolved feedback は即 `address_review_feedback` のままでよい。
  - carryover unresolved thread 自体は actionable inventory として可視化する。
- まだ人間判断が必要な理由:
  - GitHub issue body は「観測を続ける」方針を強く示す一方で、「早期停止するなら partial/current-review-incomplete human gate として明示し resume guidance を出す」余地も残している。どちらを canonical contract とするかは運用判断である。

## 回答案 (必須)
- Option A:
  - 推奨。carryover-only + completion signal none + latency guard 未満では terminal にせず、`wait_or_resume` の incomplete state として観測を継続する。current selected feedback または trusted completion signal または latency guard 後の unknown/carryover gate まで進める。
- Option B:
  - 早期停止は許すが、`observation_complete=false`、`recommended_next_action=wait_or_resume`、carryover-specific `status_reason` を返し、review feedback 対応ではなく resume-oriented incomplete status とする。
- Option C:
  - 現状に近く、carryover-only unresolved があれば即 `address_review_feedback` の terminal human gate とする。ただし Issue219 の観測問題は解消しにくい。

## Codex の分析 (必須)
- 判断軸:
  - false pass 回避、current review completion 観測の完全性、operator / downstream agent の次アクション明確性、既存 `iss-00187` contract との整合。
- tradeoff:
  - Option A は最も completion 観測に忠実だが、carryover feedback が既に存在する場合にも待つため、結果確定まで時間が伸びる。
  - Option B は早く返せるが、downstream が resume すべき partial state と review feedback handling state を誤読しないよう JSON contract を厳密にする必要がある。
  - Option C は既存コードに近いが、current review 未完了のまま停止する問題を残す。
- リスク:
  - carryover を non-actionable に落とすと、`selected_unresolved_count == 0` を no review work と誤解する退行が起きる。
  - carryover を terminal actionable にし続けると、Issue219 の premature stop が残る。
- 具体シナリオ / edge case:
  - PR に古い unresolved thread が8件あり、新しい `@codex review` に対する completion signal はまだない。CI passed 直後で latency guard 未満。この時点で `address_review_feedback` と出ると、agent は current review が完了したかのように次へ進み得る。

## Codex の推奨案 (必須)
- 推奨:
  - Option A。
- 理由:
  - Issue219 の主眼である「current review completion を観測し切る」を最も直接満たす。carryover feedback は JSON に残して可視化しつつ、latency guard 未満では review completion unknown へも feedback対応へも早期確定しないのが安全。
- 未回答時の影響:
  - Option A 前提で requirement/design/plan を書けるが、もし maintainer が早期停止型を望む場合に AC と tests を書き直す必要が出る。

## ユーザー回答 (回答後に必須)
- answer capture:
  - ユーザーは、内部ロジック、Codex review、GitHub UI、CLI interface に関わる問題として、deep-consultant に精密な調査分析を依頼し、その結果から適切な回答を選択するよう指示した。
  - Deep-consultant 2名は独立に、carryover を actionable inventory として残しつつ current review lifecycle とは別軸にする contract を推奨した。
- 回答:
  - Latency guard 未満で current review completion signal がない場合、carryover-only unresolved thread だけで terminal `address_review_feedback` にしてはいけない。
  - `pending` / `wait_or_resume` / `observation_complete=false` / `missing_current_completion_signal` を維持し、carryover counts/ids は actionable inventory として残す。
  - Current review completion 後に carryover が残る場合は `human_gate` / `address_review_feedback` として扱う。
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
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - `report.md` Evidence Adoption Ledger
- 採用 / 棄却 / deferred の理由:
  - Deep-consultant 2名の独立分析が一致し、GitHub UI/GraphQL の unresolved/outdated/resolved semantics と SpecDock skill の current-boundary final readiness semantics の両方を満たすため採用する。
- `report.md` Evidence Adoption Ledger への反映要否:
  - yes

## requirement / design / plan / ADR への含意 (回答後に必須)
- `requirement.md`:
  - Carryover-only + missing current completion + latency guard 未満を wait/resume 継続として AC に固定する。
- `design.md`:
  - Current review lifecycle と actionable review inventory を別軸として classification table と module impact に固定する。
- `plan.md`:
  - Red tests と closure ids に、carryover-only wait継続、current selected immediate terminal、latency guard後の non-pass gate を含める。
- `ADR`:
  - 不要。
- reflected_to 更新方針:
  - `requirement.md` / `design.md` へ反映済み。Plan / report authoring 時に追加更新する。
- adoption reflection:
  - `20260619t221823z-disc-carryover-review-completion-policy-synthesis.md` に synthesis を記録済み。

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
