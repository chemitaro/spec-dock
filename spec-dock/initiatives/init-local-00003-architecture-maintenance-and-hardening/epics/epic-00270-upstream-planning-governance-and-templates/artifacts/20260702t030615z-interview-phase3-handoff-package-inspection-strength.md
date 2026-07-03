---
種別: interview
ID: "20260702t030615z-interview"
タイトル: "Phase 3 Handoff Package Inspection Strength"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
親: ["epic-00270"]
関連:
  - "20260702t025127z-adr"
  - "20260702t025127z-01-research"
scope: "epic"
scope_id: "epic-00270"
created_at: "2026-07-02T03:06:15Z"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved evidence"
adoption_status: "adopted"
derived_from:
  - "artifacts/20260702t025127z-adr-complete-understanding-before-canonical-authoring.md"
  - "artifacts/20260702t025127z-01-research-grill-with-docs-research.md"
  - "spec-dock/docs/workflow_clarification.md"
  - ".agents/skills/spec-dock-epic-execution/SKILL.md"
  - ".agents/skills/spec-dock-issue-planning/SKILL.md"
  - ".agents/skills/spec-dock-issue-execution/SKILL.md"
  - "spec-dock/docs/phase_plan_epic.md"
  - "spec-dock/docs/phase_plan_issue.md"
  - "spec-dock/docs/authoring/issue-plan.md"
reflected_to:
  - "report.md"
---

# 20260702t030615z-interview Phase 3 Handoff Package Inspection Strength

## 正式質問として扱う理由
- 影響する artifact:
  - `requirement.md`:
    - Epic / Issue handoff が満たすべき user-visible reliability expectation に影響する。
  - `design.md`:
    - Epic execution entrypoint が handoff package をどの深さで検査し、どこで issue planning / clarification へ戻すかに影響する。
  - `plan.md`:
    - Issue 03-05 付近の実装 slice、acceptance criteria、reviewer fail conditions、smoke tests の強さに影響する。
  - `ADR`:
    - 既存 workflow の fail-closed 方針と整合するが、現時点では ADR ではなく design / plan 反映で足りる可能性が高い。
- chat 上の軽微な一問では足りない理由:
  - Handoff package の厳しさは、実装開始を止めるかどうかに直結する。過剰に厳しいと運用が重くなり、緩すぎると incomplete spec のまま実装に流れる。

## 質問の目的
- 対象者:
  - product maintainer / Epic owner
- 何を明確にする質問か:
  - Epic execution skill / runtime / reviewer が、Epic -> Issue execution handoff package をどの強さで検査するべきか。
- 回答が後続判断へ与える影響:
  - `spec-dock-epic-execution` の入口ルール、Epic plan template の Issue readiness contract、Issue plan executable contract、reviewer fail/smoke の設計が変わる。

## 質問
- pressure-test question:
  - Handoff package が不完全なまま実装へ進む事故を防ぎつつ、毎回 heavyweight な gate で詰まらないようにするには、どこを blocking fail にし、どこを reviewer finding / warning に留めますか。
- 質問:
  - Epic execution が Issue を開始・実行へ流す前の handoff package 検査は、どの強さにしますか。
- 回答してほしいこと:
  - A / B / C のどれに近いか、または混合案があれば教えてください。

## source-grounded context
- 確認済みの docs / code / tests / ADR / artifacts / primary source:
  - `spec-dock-epic-execution` は、Epic planning handoff が missing / stale / unreviewed / non-executable の場合、Epic planning / Issue planning へ戻す。
  - `spec-dock-issue-planning` は、fresh `spec-reviewer` pass、delegated draft adoption、Issue grade、template-only/unresolved docs を stop condition とする。
  - `spec-dock-issue-execution` は、requirement/design/plan の approved / reviewer-pass / executable readiness がない場合、execution を開始しない。
  - `phase_plan_epic.md` は Issue readiness contract を Epic plan に置く責務を持つ。
  - `phase_plan_issue.md` / `authoring/issue-plan.md` は、delegation contract、target files、required verification、reviewer focus、stop conditions が欠けると fail とする。
  - `workflow_clarification.md` は、implementation start 前に requirement/design/plan gate と Spec Authoring Gate evidence を確認し、handoff readiness evidence を `report.md` に残すとしている。
  - Grill With Docs research は、設計判断を失わず handoff artifact へ残すことを重視している。
- local context で解決できたこと:
  - SpecDock は既に、execution handoff を fail-closed に寄せる方針を持つ。
  - Missing / stale / template-only / reviewer-pass missing / non-executable plan は実装開始 blocker である。
  - Raw artifact や delegated draft は、fresh reviewer pass や canonical adoption の代替ではない。
- まだ人間判断が必要な理由:
  - 今回の Epic では upstream planning UX を扱うため、どこまでを machine-blocking にし、どこからを reviewer finding / warning にするかの運用バランスは product decision になる。

## 回答案
- Option A:
  - 軽め。Epic execution は既存の reviewer-pass / executable plan / dependency readiness だけを見る。詳細な handoff completeness は spec-reviewer findings に委ねる。
- Option B:
  - 中程度。Blocking fail は machine-checkable な構造欠落に限定する。例: missing canonical docs、fresh reviewer pass なし、Issue readiness contract なし、Issue plan の executable step / delegation contract / required verification / reviewer focus 欠落、unresolved Spec Authoring Gate。解釈が必要な品質問題は reviewer finding にする。
- Option C:
  - 強め。Epic execution entrypoint が handoff package の意味的十分性まで積極的に検査し、target files の妥当性、acceptance criteria の網羅性、test strategy の十分性、ADR/reference adoption の不足も blocking fail にする。

## Codex の分析
- 判断軸:
  - 不完全な spec が実装へ流れる事故の防止。
  - Lightweight CLI tool としての運用負荷。
  - Machine-check と reviewer judgment の責務分離。
  - 後続エージェントが止まるべき条件を明確に理解できるか。
- tradeoff:
  - Option A は軽いが、実装直前に spec gap が露見しやすい。
  - Option B は既存 fail-closed 方針と整合し、構造欠落を止めつつ、意味的判断は reviewer に残せる。
  - Option C は安全だが、Epic execution skill / runtime が semantic reviewer 化しやすく、SpecDock の layer/skill boundary が重くなる。
- リスク:
  - Blocking 条件が曖昧だと、後続 agent が self-claim で実装に進む。
  - Blocking 条件が広すぎると、reviewer が担うべき判断を runtime / entry skill が抱えすぎる。
- 具体シナリオ / edge case:
  - Issue plan に steps はあるが required verification が空: machine-checkable missing field として block しやすい。
  - Acceptance criteria が弱いが形式上は存在する: reviewer finding として扱う方が自然。
  - Artifact adoption はあるが report EAL がない: authority leak 防止のため blocking に寄せる。

## Codex の推奨案
- 推奨:
  - Option B。
- 理由:
  - 既存 SpecDock docs / skills の fail-closed posture と合う。
  - Machine-checkable structure は実行前に止め、semantic sufficiency は fresh reviewer gate に委ねられる。
  - Epic execution skill が coordinator であり、semantic reviewer にならない。
- 未回答時の影響:
  - Epic plan の Issue readiness contract と execution entrypoint acceptance criteria が固定できない。

## ユーザー回答
- answer capture:
  - Option B を採用する。
- 回答:
  - Handoff package 検査は中程度の強さにする。Machine-checkable な構造欠落は blocking fail とし、意味的な品質・十分性は reviewer finding として扱う。
- 回答日時:
  - 2026-07-02

## 追加確認の要否
- 追加確認が必要か:
  - no
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - なし

## 採用判断
- adoption_status:
  - adopted
- adoption target:
  - `design.md` / `plan.md` / `report.md` Evidence Adoption Ledger
- 採用 / 棄却 / deferred の理由:
  - ユーザーが Option B を明示採用した。既存 SpecDock workflow の fail-closed posture と coordinator / reviewer の責務分離に合う。
- `report.md` Evidence Adoption Ledger への反映要否:
  - yes

## requirement / design / plan / ADR への含意
- `requirement.md`:
  - Execution handoff の信頼性要求。
- `design.md`:
  - Epic execution entrypoint / reviewer / runtime の責務分離。
- `plan.md`:
  - Issue readiness contract、smoke tests、reviewer fail/warning split。
- `ADR`:
  - 現時点では不要。既存 fail-closed / complete understanding ADR に従う設計詳細として扱える。
- reflected_to 更新方針:
  - `report.md` EAL へ反映し、canonical docs 作成時に `design.md` / `plan.md` へ採用する。
- adoption reflection:
  - `report.md` EAL-012 へ反映する。
