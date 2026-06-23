---
種別: disc
ID: "20260623t074452z-disc"
タイトル: "ADR Decision Synthesis After Issue 226 Closure"
状態: "adopted"
作成者: "iwasawayuuta"
最終更新: "2026-06-23"
親: ["epic-00224"]
関連:
  - "iss-00226"
  - "#226"
authority: "proposed"
derived_from:
  - "deep-consultant architecture decision authority analysis"
  - "deep-consultant workflow dependency and handoff analysis"
  - "deep-consultant semantic completeness analysis"
reflected_to:
  - "20260623t074441z-adr-fixed-skill-kernel-compiled-runbook-authority.md"
  - "20260623t074443z-adr-adaptive-assurance-lite-authorization-monotonic-escalation.md"
  - "20260623t074442z-adr-step-assurance-resource-allocation-agent-context-routing.md"
  - "20260623t074444z-adr-trusted-base-sha-github-review-policy.md"
  - "20260623t074447z-adr-blocker-centric-pr-risk-closure-rereview.md"
  - "../design.md"
  - "../plan.md"
  - "../report.md"
---

# 20260623t074452z-disc ADR Decision Synthesis After Issue 226 Closure

## 対象論点
- `iss-00226 / #226` を「ADR 作成 Issue」として残すべきか、それとも ADR-level decision を現 Epic planning/design で確定すべきか。
- Downstream Issue が実装開始前に依存する durable architecture decisions をどこに置くべきか。
- `iss-00226` を閉じた後に、Epic design / plan / report / issue draft handoff をどう補正するか。

## derived question sheets / research
- `interview`: なし。3 本の deep-consultant は、blocking な人間確認は不要と判断した。
- `research` / consultant evidence:
  - Architecture decision authority analysis:
    - ADR は Epic-scope `discussions/` に accepted artifact として作る。
    - `iss-00226` は復活させない。
  - Workflow dependency and handoff analysis:
    - T0 は Issue slice から削除し、非 Issue の `G0 Epic Decision Baseline` に置き換える。
    - `iss-00227 -> iss-00226` dependency は削除する。
  - Semantic completeness analysis:
    - ADR は 5 件維持。
    - Lite authorization と Step Assurance resource allocation が名前から見えるように改名する。

## synthesis
- 合意済み:
  - Decision-only Issue を execution-ready prerequisite として扱うのは誤り。
  - `iss-00226 / #226` は closed / superseded historical evidence とし、downstream readiness graph から外す。
  - ADR-level decisions はこの Epic で accepted ADR として固定する。
  - Downstream implementation は `iss-00227` から開始する。
  - Automatic Lite default は初期 scope 外。将来採用には別 accepted ADR、policy version bump、rollout Issue が必要。
- 未合意 / 未確定:
  - なし。現時点で人間確認が必要な blocking decision はない。
- source-grounded に解決できたこと:
  - `decision-routing.md` は decision-only Issue を bad pattern としている。
  - `workflow_epic.md` は cross-issue design backbone を Epic が所有すると定義している。
  - `workflow_clarification.md` は重要判断を canonical docs / ADR / report へ採用することを要求している。

## 選択肢 / tradeoff
- Option A: `iss-00226` を closed dependency として残す。
  - Pros:
    - Graph 上は satisfied になり、既存 plan diff が少ない。
  - Cons:
    - Future reader が `#226` を正しい architecture gate と誤読する。
    - decision-only Issue を execution prerequisite にする bad pattern を残す。
  - Decision:
    - 棄却。
- Option B: `iss-00226` を削除する。
  - Pros:
    - 誤った scaffold を完全に消せる。
  - Cons:
    - GitHub issue closure / historical evidence との対応が追いにくくなる。
  - Decision:
    - 棄却。削除ではなく closed / superseded evidence として残す。
- Option C: `iss-00226` を closed / superseded とし、ADR authority を Epic-scope accepted ADR に移す。
  - Pros:
    - workflow docs と一致し、履歴も残る。
    - downstream readiness graph が正しい実装 Issue だけを表す。
  - Cons:
    - Epic design / plan / report / draft handoff の修正が必要。
  - Decision:
    - 採用。

## ADR triage
- ADR candidate か:
  - yes, 5 件。
- hard to reverse:
  - yes。
- surprising without context:
  - yes。
- real tradeoff:
  - yes。
- ADR 化しない判断:
  - `iss-00226` routing correction 自体は Epic design / plan / report に反映する。これはこの Epic の handoff correction であり、独立 ADR にしない。

## 推奨案
- 5 件の accepted ADR を Epic `discussions/` 直下に作成する。
- `plan.md` の T0 Issue slice を削除し、`G0 Epic Decision Baseline` に置換する。
- `design.md` の Issue Realization Map から T0 を外し、accepted ADR index を置く。
- `report.md` で `iss-00226` を superseded / closed evidence として記録する。
- `iss-00227` draft requirement の Upstream を accepted Epic ADR / Epic design baseline に置き換える。

## 推奨反映先
- `requirement.md`:
  - 原則大きな要件追加は不要。必要なら ADR acceptance を implementation readiness の前提として追記する。
- `design.md`:
  - Accepted ADR index / decision summary / Issue map correction。
- `plan.md`:
  - T0 removal / G0 gate / dependency command correction / final exit correction。
- `ADR`:
  - 5 件を accepted。
- `report.md` Evidence Adoption Ledger:
  - deep-consultant synthesis adoption、`iss-00226` closure/supersession、fresh reviewer result を記録する。

## 未採用 / deferred 理由
- `iss-00226` を satisfied dependency として残す:
  - 誤った decision-only Issue を正当な architecture gate と誤読させるため未採用。
- Automatic Lite default:
  - 初期 scope では安全性と telemetry が不足するため deferred。将来採用には別 accepted ADR、policy version bump、rollout Issue が必要。

## 次アクション
- `deps remove --from iss-00227 --to iss-00226` を実行する。
- 5 件の ADR を accepted として作成する。
- Epic `design.md` / `plan.md` / `report.md` と `iss-00227` draft requirement、integration review discussion を更新する。
- `validate` / `sync` / `deps check` を実行する。
- fresh `spec-reviewer` に通す。
