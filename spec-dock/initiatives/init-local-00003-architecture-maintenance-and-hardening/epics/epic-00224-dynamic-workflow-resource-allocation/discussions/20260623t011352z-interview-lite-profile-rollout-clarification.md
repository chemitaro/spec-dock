---
種別: interview
ID: "20260623t011352z-interview"
タイトル: "Lite Profile Rollout Clarification"
状態: "answered-by-analysis"
作成者: "Codex"
最終更新: "2026-06-23"
親: ["epic-00224"]
関連:
  - "20260623t011349z-research"
  - "20260623t011746z-research"
  - "20260623t012043z-research"
authority: "evidence"
derived_from:
  - "source-grounded clarification before epic authoring"
reflected_to: []
---

# 20260623t011352z-interview Lite Profile Rollout Clarification

## 質問

軽量タスクの過剰ゲート削減について、初期 rollout の正式仕様はどちらに寄せますか。

## 選択肢

- Option A: Conservative rollout
  - Draft package の方針どおり、初期は Standard default とし、Lite は all-positive eligibility が揃った場合だけ opt-in / evidence-gated で有効化する。
  - 利点:
    - Safety regression が小さい。
    - 既存の重い workflow から段階移行しやすい。
    - Lite 誤判定による review / verification 不足を避けやすい。
  - 欠点:
    - ユーザーが感じている token / time waste は初期段階ではあまり減らない可能性がある。

- Option B: Aggressive Lite automation
  - 新規 Issue では、routine / low-risk と判定できる場合に Lite を自動適用し、Standard 以上へ escalation する条件を runtime が監視する。
  - 利点:
    - 軽量タスクの token / wall-clock 削減効果が早く出る。
    - この Epic の主目的である dynamic workflow switching を体感しやすい。
  - 欠点:
    - Lite 誤判定時の safety net、telemetry、escalation、rollback 条件をより厳密に設計する必要がある。

- Option C: Hybrid acceptance gate
  - 実装 rollout は Option A で始めるが、Epic の success criteria には「Lite 自動適用が安全に可能な判定条件と telemetry gate を定義する」ことを含める。
  - 利点:
    - 初期 safety を保ちつつ、最終的に Lite 自動化へ進む道筋を requirement / plan に明記できる。
  - 欠点:
    - Epic 内の完了条件がやや広がり、I07 の rollout / telemetry gate が重くなる。

## 推奨案

- 推奨は Option C。
- 理由:
  - Draft package は安全側の Standard default を置いている一方、ユーザーの問題意識は軽量タスクの過剰コスト削減にある。
  - 初期実装でいきなり Lite 自動適用を default にすると、classification の false negative / false positive の設計負荷が高い。
  - ただし Epic の formal acceptance criteria に Lite 自動化への gate を入れないと、最も解きたい軽量タスク問題が後続に薄まりやすい。

## 回答欄

- user answer:
  - ユーザーから、この論点はユーザー体験の好みではなく、SpecDock scripts と SpecDock を操作する agent workflow 側の system-design / best-practice 判断であると補正があった。
  - そのため、ユーザーへの選好質問ではなく deep-consultant analysis へ reroute した。
- adoption decision:
  - `20260623t012043z-research-deep-consultant-lite-rollout-report.md` の結論を採用候補とする。
  - 採用候補は Option C の強化版。
  - 初期実行は Standard default / Lite explicit opt-in + evidence-gated とし、この Epic 内では automatic Lite default を有効化しない。
  - Epic success criteria には、将来の automatic Lite default に必要な safe predicates、shadow classification、telemetry gate、promotion 条件を含める。
- reflected_to:
  - `requirement.md`: Lite / Standard default / success criteria
  - `design.md`: classification policy, escalation, telemetry, rollback
  - `plan.md`: rollout tranche, I07 completion gate
  - `report.md`: Evidence Adoption Ledger / Spec Authoring Gate
