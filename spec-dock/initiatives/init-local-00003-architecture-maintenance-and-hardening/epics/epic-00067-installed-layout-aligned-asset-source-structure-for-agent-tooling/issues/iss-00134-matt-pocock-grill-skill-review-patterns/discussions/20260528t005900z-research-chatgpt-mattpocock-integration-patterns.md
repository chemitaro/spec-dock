---
種別: research
ID: "research-20260528t005900z"
タイトル: "ChatGPT analysis of Matt Pocock skills integration patterns for spec-dock"
状態: "completed"
作成者: "Codex"
最終更新: "2026-05-28"
親: ["iss-00134"]
関連: ["research-20260528t004419z", "scratch-20260528t005600z"]
authority: "synthesized"
derived_from:
  - "discussions/20260528t004419z-research-mattpocock-skills-source-capture.md"
  - "discussions/20260528t004700z-scratch-chatgpt-initial-analysis-prompt.md"
  - "discussions/20260528t005600z-scratch-chatgpt-initial-analysis-response.md"
reflected_to: []
---

# research-20260528t005900z ChatGPT analysis of Matt Pocock skills integration patterns for spec-dock

## 調査目的
- Matt Pocock skills のうち、`grill-me` / `grill-with-docs` を中心とした clarification pattern を spec-dock にどう取り込むべきかを初回分析する。
- 単純移植ではなく、spec-dock の active docs、discussion artifacts、ADR lifecycle、provider-side `install_root` 境界と整合する統合方針を整理する。

## 調査方法
- issue-local source capture と spec-dock active issue context を ChatGPT 5.5 Pro / じっくり思考 Pro に渡して分析させた。
- ChatGPT thread:
  - `https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a1790e9-2be8-83a4-aa7c-3350ef063f6f`
- ChatGPT は追加 Web 確認なしで、提示した source capture summary と file inventory を一次 evidence として回答した。

## 調査結果
- ChatGPT の推奨結論:
  - `grill-me` をそのまま移植するのではなく、`grill-with-docs` を基礎にした spec-dock 版 docs-aware clarification workflow を採用する。
  - skill 名の第一候補は `spec-dock-requirement-grill`。
  - `grill-me` は、one-question-at-a-time interview、decision-tree traversal、shared-understanding stop condition、repo/docs で答えられる質問を人に聞かない、という sub-pattern として使う。
- Matt Pocock pattern と spec-dock surface の対応:
  - small/composable skills -> `.agents/skills` shared layer と host-specific agent layer に合わせて小さく導入する。
  - docs-aware grilling -> root `CONTEXT.md` ではなく、active issue docs、parent epic/initiative docs、discussion artifacts、`.agent` state を context source set とする。
  - `to-prd` -> PRD ではなく `requirement.md` / `design.md` / `plan.md` synthesis に変形する。
  - `to-issues` -> GitHub issue publish 前提ではなく、spec-dock Issue tree と vertical-slice plan に変形する。
  - `tdd` -> 既存 `spec-driven-tdd-workflow` と Spec-Locked Closure Index / step closure contract の補強として扱う。
  - `improve-codebase-architecture` -> HTML report mandatory ではなく、research / disc / diagram / ADR triage に分解する。
- 候補 artifact:
  - `.agents/skills/spec-dock-requirement-grill/SKILL.md`
  - optional `.codex/agents/requirement-grill-facilitator`
  - `spec-dock/templates/discussions/interview/grill-session.md`
  - `spec-dock/templates/discussions/research/source-grounding.md`
  - `spec-dock/templates/discussions/disc/decision-tree.md`
  - ADR triage policy or existing `spec-dock-adr-facilitation` extension

## 推測 / 未検証事項
- 推測:
  - first implementation slice は new shared skill `spec-dock-requirement-grill` が最も自然。
  - new Codex agent は必須ではなく、既存 `consultant` / `deep-consultant` / `spec-manager` に shared skill を読ませるだけでも開始できる。
- 未検証:
  - Matt Pocock skills `LICENSE` の正確な再利用条件。
  - 実際の `SKILL.md` 全文に基づく逐語的差分分析。
  - `issue clarify` を CLI command にするか、skill/prompt workflow に留めるか。
  - discussion artifact の filename convention と template placement。
  - global `CONTEXT.md` を導入しない場合の glossary promotion rule。

## 判断への含意
- 要件定義壁打ちには `grill-with-docs` 系が向いている。ただし spec-dock では `CONTEXT.md` 中心ではなく、active spec tree と discussions 中心に再設計する。
- `grill-me` は primary skill ではなく、question discipline と shared-understanding stop condition を取り込む。
- ChatGPT の次ループは、抽象ビジョンではなく `spec-dock-requirement-grill` の actual `SKILL.md` 契約、context source mapping、`issue clarify` lifecycle phase を具体化する方向がよい。

## リスク/制約
- ChatGPT output は third-party analysis であり、まだ spec-dock の canonical requirement/design/plan には未反映。
- license / attribution を確認するまでは、Matt Pocock skills の instruction text を shipped asset に逐語コピーしない。
- `CONTEXT.md` を spec-dock に安易に追加すると、active docs / parent docs / discussions と二重 authority になる可能性がある。
- new agent 追加は agent sprawl のリスクがあるため、shared skill 先行が無難。

## 反映先
- reflected_to:
  - 未反映。次の discussion / design step で requirement/design/plan へ反映する。

## 参考（References）
- `discussions/20260528t004419z-research-mattpocock-skills-source-capture.md`
- `discussions/20260528t004700z-scratch-chatgpt-initial-analysis-prompt.md`
- `discussions/20260528t005600z-scratch-chatgpt-initial-analysis-response.md`
