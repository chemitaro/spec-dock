---
種別: ADR（Architecture Decision Record）
ID: "20260629t003131z-adr"
タイトル: "Plan Centric Issue Execution Preflight"
状態: "accepted"
作成者: "iwasawayuuta"
最終更新: "2026-06-29"
親: ["epic-00224"]
authority: "accepted"
supersedes:
  - "runtime-selected issue execution step"
  - "default Step Assurance Compiler execution authority"
  - "default Context Packet Compiler execution authority"
amends:
  - "20260623t074441z-adr"
  - "20260623t074442z-adr"
derived_from:
  - "../issues/iss-00244-simplify-issue-execution-guidance-into-plan-centric-preflight-validation/discussions/20260627t130116z-research-plan-centric-execution-guidance-handoff.md"
  - "../issues/iss-00244-simplify-issue-execution-guidance-into-plan-centric-preflight-validation/discussions/20260627t131746z-research-plan-centric-guidance-requirement-preparation.md"
  - "../issues/iss-00244-simplify-issue-execution-guidance-into-plan-centric-preflight-validation/discussions/20260627t132248z-disc-plan-centric-guidance-requirement-scope-synthesis.md"
  - "../issues/iss-00244-simplify-issue-execution-guidance-into-plan-centric-preflight-validation/report.md"
reflected_to:
  - "../requirement.md"
  - "../design.md"
  - "../plan.md"
  - "../report.md"
  - "../issues/iss-00244-simplify-issue-execution-guidance-into-plan-centric-preflight-validation/requirement.md"
  - "../issues/iss-00244-simplify-issue-execution-guidance-into-plan-centric-preflight-validation/design.md"
  - "../issues/iss-00244-simplify-issue-execution-guidance-into-plan-centric-preflight-validation/plan.md"
---

# 20260629t003131z-adr Plan Centric Issue Execution Preflight

## ADR 化基準

- hard to reverse: yes
- surprising without context: yes
- real tradeoff: yes
- ADR として残す理由:
  - Issue execution の authority を runtime-selected step から `plan.md` に移す判断は、skills、runtime guidance、runbook projection、context routing、review obligation、manual dogfooding workflow にまたがる。
  - 旧 Epic ADR は runtime が step / worker / reviewer / verification / context packet を動的に選ぶ前提を含んでいたため、変更済みであることを accepted decision として明示しないと、後続 Issue が古い設計へ戻るリスクがある。

## 結論（Decision）

- Issue execution の実行順、worker allocation、reviewer obligation、verification、step closure evidence は、承認済み `plan.md` に集約する。
- `guidance issue-execution` は、実行時に次 step / worker / reviewer / verification / context packet を選ばない。
- `guidance issue-execution` は、承認済み `plan.md` を実行してよいかを確認する preflight / consistency validator とする。
- Ready guidance は、`plan.md` を execution contract、`report.md` を observed evidence ledger として示し、`may_execute_approved_plan=true` を返す。
- Blocked / planning-required guidance は、non-executable plan、stale source binding、invalid assurance contract、未解決 marker、scaffold artifact、必要な reviewer/verification obligation 不足を fail-closed に示す。
- `selected_step`、`step_assurance`、`context_packets`、runtime 推定の worker / reviewer / reasoning effort / verification / context mode は default output contract から hard cutover で削除する。
- `report.md` は evidence ledger であり、runtime が次 step を選ぶ control plane ではない。
- Generated runbook projection は human/debug-only evidence であり、agent handoff authority ではない。
- Step-level obligation pattern は issue planning / plan authoring の時点で明示する。実装時に runtime が free text から補完しない。

## 背景（Context）

- Epic 初期設計では、Skill を固定 kernel にし、runtime が current Runbook を compile して agent に提示する方針だった。
- さらに Step Assurance / Context Routing では、runtime が step kind、worker、reviewer、context policy、verification を導出する想定があった。
- Dogfooding 中、`report.md` に step closure evidence が残っていても `guidance issue-execution` が同じ step を返し続ける問題が発生した。
- 直接原因は parser / ledger 形式の不整合だったが、追加分析では、作業しながら `report.md` を更新し、その更新を runtime が次 step selection に使う model 自体が不安定だと判断した。
- `plan.md` はすでに planned executable workflow contract として存在し、`report.md` は observed evidence ledger として使える。実行時の判断を `plan.md` に一本化する方が、agent にとって理解しやすく、authority も分散しない。

## 選択肢（Options considered）

- Option A: report parser を修正し、runtime-selected step model を維持する。
  - Pros: 初期設計との差分が小さい。
  - Cons: `plan.md`、skill、runtime guidance、projection、`report.md` parser の複数 authority が残る。実行中に state を更新し続ける必要があり、dogfooding で不安定さが確認済み。
  - 判断: 棄却する。
- Option B: dynamic fields を互換 field として残しつつ、plan-centric guidance へ段階移行する。
  - Pros: 旧 consumer の破壊を避けやすい。
  - Cons: agent が旧 field を authority と誤読する。今回の目的である authority simplification が弱まる。
  - 判断: 棄却する。
- Option C: hard cutover で plan-centric preflight に切り替える。
  - Pros: source of truth が `plan.md` に一本化され、runtime は readiness / consistency validation に集中できる。旧 dynamic field への誤追随を止められる。
  - Cons: 旧 output contract を期待する tests / docs / skills を更新する必要がある。
  - 判断: 採用する。

## 判断理由（Rationale）

- 実装作業の実行計画は `plan.md` に記述されるべきであり、実行時 runtime が別の step plan を合成する設計は authority を二重化する。
- Dynamic guidance は「今すべき step」を短く提示できる一方で、その正しさが `report.md` parser、projection freshness、runtime state update、agent の再実行習慣に依存する。
- Agent が最も追随しやすい contract は、承認済み `plan.md` を上から実行し、`report.md` に evidence を残す単純な contract である。
- 品質 gate の強弱は runtime 推定ではなく、plan authoring 時の Step-level Obligation Pattern と Assurance Profile に織り込む方が再現性が高い。
- 旧 dynamic model を互換維持すると、後続 agent が `selected_step` や `step_assurance` を current authority と誤読し続けるため、hard cutover が必要である。

## 影響（Consequences）

- Positive:
  - Issue execution の authority が `plan.md` に集約される。
  - `report.md` を parser control plane として扱う不安定さを排除できる。
  - Skills は lightweight preflight と stop conditions に集中できる。
  - Generated projection は human/debug-only の位置づけに戻る。
- Negative / Debt:
  - 旧 Runbook / Step Assurance / Context Packet output を期待する tests と docs は置換が必要である。
  - 将来 context packet utility を再導入する場合でも、default issue execution authority には戻さない設計が必要である。
  - planning-time template / compose fragments は、step obligation を十分に書ける scaffold を提供する必要がある。
- 影響範囲:
  - `guidance issue-execution`
  - `domain/runbook.py`
  - `presentation/workflow.py`
  - `application/workflow.py`
  - `context_packets.py` / `context_routing.py` の default path
  - `spec-dock-issue-planning` / `spec-dock-issue-execution` skills
  - plan authoring docs / assurance compose templates
- 移行/ロールバック:
  - 互換期間は設けない。
  - 旧 dynamic fields が必要になった場合は、この ADR を supersede する新 ADR が必要である。

## 旧決定との関係（Supersession / Amendment）

- `20260623t074441z-adr Fixed Skill Kernel And Compiled Runbook Authority`:
  - 維持: Skill は固定 kernel とし、generated projection は tracked source of truth ではない。
  - 変更済み: runtime が issue execution の current step / detailed workflow body を compile して agent handoff authority にする部分は、本 ADR により plan-centric preflight へ置換する。
  - 変更済み: `workflow next` / compiled Runbook を execution authority とする語彙は historical wording として扱う。Current command surface は `guidance <target>` であり、issue execution の execution contract は `plan.md` である。
- `20260623t074442z-adr Step Assurance Resource Allocation And Agent Context Routing`:
  - 維持: reviewer / consultant independence、bounded return contract、clean-room review boundary は有効である。
  - 変更済み: default issue execution path で runtime が step assurance / context packet / worker / reviewer / verification を選ぶ部分は、本 ADR により廃止する。
  - 変更済み: step obligations は runtime inference ではなく plan authoring 時の explicit contract として扱う。

## 非目標（Non-goals）

- `plan.md` の品質 gate を弱めない。
- Reviewer / consultant の clean-room boundary を廃止しない。
- 将来の context packet utility を永久に禁止しない。ただし default issue execution authority にはしない。
- PR observation / review trigger の終了条件はこの ADR では扱わない。

## 参考（References）

- `../issues/iss-00244-simplify-issue-execution-guidance-into-plan-centric-preflight-validation/requirement.md`
- `../issues/iss-00244-simplify-issue-execution-guidance-into-plan-centric-preflight-validation/design.md`
- `../issues/iss-00244-simplify-issue-execution-guidance-into-plan-centric-preflight-validation/plan.md`
- `../issues/iss-00244-simplify-issue-execution-guidance-into-plan-centric-preflight-validation/discussions/20260627t130116z-research-plan-centric-execution-guidance-handoff.md`
- `../issues/iss-00244-simplify-issue-execution-guidance-into-plan-centric-preflight-validation/discussions/20260627t131746z-research-plan-centric-guidance-requirement-preparation.md`
- `20260623t074441z-adr-fixed-skill-kernel-compiled-runbook-authority.md`
- `20260623t074442z-adr-step-assurance-resource-allocation-agent-context-routing.md`
