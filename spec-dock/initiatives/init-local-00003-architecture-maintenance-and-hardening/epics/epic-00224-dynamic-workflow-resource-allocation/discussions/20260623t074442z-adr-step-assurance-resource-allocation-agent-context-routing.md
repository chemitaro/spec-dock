---
種別: ADR（Architecture Decision Record）
ID: "20260623t074442z-adr"
タイトル: "Step Assurance Resource Allocation And Agent Context Routing"
状態: "accepted"
作成者: "iwasawayuuta"
最終更新: "2026-06-23"
親: ["epic-00224"]
authority: "accepted"
amended_by:
  - "20260629t003131z-adr"
derived_from:
  - "20260623t074452z-disc-adr-decision-synthesis-after-issue-226-closure.md"
  - "20260623t024533z-research-agent-context-routing-supplemental-draft.md"
reflected_to:
  - "../requirement.md"
  - "../design.md"
  - "../plan.md"
  - "../report.md"
---

# 20260623t074442z-adr Step Assurance Resource Allocation And Agent Context Routing

## 変更履歴（Supersession / Amendment）

- 2026-06-29: `20260629t003131z-adr Plan Centric Issue Execution Preflight` により、default issue execution path で runtime が step assurance / context packet / worker / reviewer / verification を選ぶ方針は変更済み。
- 維持: reviewer / consultant independence、clean-room boundary、bounded return contract は current policy として有効である。
- 変更済み: step-level worker / reviewer / verification / context obligations は runtime inference ではなく、`plan.md` の explicit step contract として planning 時に固定する。

## ADR 化基準
- hard to reverse: yes
- surprising without context: yes
- real tradeoff: yes
- ADR として残す理由:
  - Agent context を継承するほど効率は上がるが、reviewer / consultant の独立性は下がる。どの agent に何を渡すかは複数 workflow にまたがる durable policy である。

## 結論（Decision）
- Step Assurance は Assurance Profile、Complexity Tier、Context Policy の 3 軸で resource allocation を決める。
- Assurance Profile は verification / review / human gate の深さを制御する。
- Complexity Tier は reasoning effort / specialist depth / delegation expectation を制御する。
- Context Policy は `inherit` / `recent_fork` / `bounded_packet` / `clean_room` を制御する。
- Worker / implementation-oriented agent は `recent_fork` または `bounded_packet` を使える。Reviewer / QA / spec-reviewer / deep-consultant は原則 `clean_room` とし、author narrative や unreviewed conclusion への anchor を避ける。
- Hard safety rule は profile / tier / context を強められるが、model confidence、token pressure、速度優先は reviewer / consultant clean-room boundary を弱める理由にならない。
- Sub-agent return contract は outcome、changed files、evidence refs、risk / uncertainty、open blockers に圧縮する。raw transcript、private reasoning、unbounded context dump を canonical evidence にしない。

## 背景（Context）
- 全 sub-agent を fresh start すると、同じ context を何度も読み直す cost が高い。
- 反対に、reviewer が author と同じ narrative を継承すると、見落としや自己追認が起きる。
- ユーザーから追加共有された draft では、agent context routing の作り込みが不足していたため、この Epic で明示 policy 化する必要がある。

## 選択肢（Options considered）
- Option A: 全 agent を常に fresh / clean-room にする。
  - Pros: 独立性が高い。
  - Cons: 実装 worker でも context rebuild cost が大きい。
  - 棄却理由: 軽量 task の waste 削減に反する。
- Option B: 全 agent に full thread context を渡す。
  - Pros: worker は早く動ける。
  - Cons: reviewer independence が壊れ、評価が author narrative に寄る。
  - 棄却理由: review / consultant の価値を損なう。
- Option C: Agent role ごとに context mode を tracked policy で決める。
  - Pros: worker 効率と reviewer independence を両立できる。
  - Cons: context packet compiler / source binding / exclusion tests が必要。
  - 採用理由: resource allocation の目的に最も合う。

## 判断理由（Rationale）
- Resource allocation は profile だけで決めると粗すぎる。軽量 task でも reviewer independence が必要な場面があり、重量 task でも worker context inheritance は有効な場面がある。
- Context Policy を tracked / source-bound にすることで、agent の都度判断で clean-room boundary が弱まることを防ぐ。
- MyPy / Ruff baseline は feature scope ではないが、context packet model、return contract、policy enum は typed contract として実装する必要がある。

## 影響（Consequences）
- Positive:
  - Worker は必要 context を得やすくなり、reviewer は独立性を保てる。
  - Returned evidence refs を通じて、親 orchestrator が採用判断を追跡しやすくなる。
- Negative / Debt:
  - Context packet compiler、hash binding、freshness invalidation、clean-room exclusion tests が必要。
  - role / context mode matrix の maintenance が必要。
- 影響範囲:
  - Step assurance model
  - context routing policy
  - sub-agent handoff / return contract
  - spec-reviewer / deep-consultant use policy
- 移行/ロールバック:
  - Policy 欠落時は strict / clean-room safe default に戻す。
  - Context packet compile failure は fail-closed とし、manual bounded summary または fresh review を要求する。
- Follow-ups:
  - `iss-00230` が Step Assurance、Context Policy Resolver、Packet Compiler、return contract を実装する。

## 非目標（Non-goals）
- private reasoning を保存しない。
- raw transcript を canonical evidence にしない。
- reviewer / consultant clean-room boundary を token cost 理由で弱めない。

## 未確定事項（Open Questions）
- fork turn count、packet size、fallback compaction の具体値は `iss-00230` で確定する。ただし bounded / source-bound / clean-room no weakening は固定済み。

## 参考（References）
- `requirement.md`
- `design.md`
- `20260623t024533z-research-agent-context-routing-supplemental-draft.md`
- `20260623t074452z-disc-adr-decision-synthesis-after-issue-226-closure.md`
