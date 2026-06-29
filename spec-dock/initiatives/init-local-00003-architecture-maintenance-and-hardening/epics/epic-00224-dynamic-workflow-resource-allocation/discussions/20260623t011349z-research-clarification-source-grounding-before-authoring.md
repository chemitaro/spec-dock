---
種別: research
ID: "20260623t011349z-research"
タイトル: "Clarification Source Grounding Before Authoring"
状態: "draft"
作成者: "Codex"
最終更新: "2026-06-23"
親: ["epic-00224"]
関連:
  - "epic-00158"
  - "20260623t010733z-draft-requirement"
  - "20260623t010737z-draft-design"
  - "20260623t010749z-draft-plan"
  - "20260623t010846z-disc"
authority: "evidence"
derived_from:
  - "spec-dock-clarification skill"
  - "workflow_clarification.md"
  - "active epic scaffold"
  - "epic-00158 requirement/design"
  - "user-provided draft package"
  - "repo source search"
reflected_to: []
---

# 20260623t011349z-research Clarification Source Grounding Before Authoring

## 読んだ source

- `.agents/skills/spec-dock-clarification/SKILL.md`
  - Source-grounded grill loop、one-question discipline、artifact capture before asking を確認した。
- `spec-dock/docs/workflow_clarification.md`
  - `research` / `interview` / `disc` / ADR / `report.md` の使い分け、formal question trigger、adoption evidence を確認した。
- `spec-dock/active/epic/{requirement,design,plan}.md`
  - `epic-00224` の canonical docs は scaffold のままであり、まだ formal authoring 前であることを確認した。
- `epic-00224` discussions:
  - draft requirement / design / plan、Issue slice seeds、selection decision、README、GPT full log、synthesis を保存済み evidence として確認した。
- `epic-00158-agent-workflow-pdca-hardening` requirement / design:
  - Skills / docs / templates の context surface ownership、fresh reviewer gate、evidence adoption boundary、runtime gate 後続化の前提を確認した。
- Repo source:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/{cli,commands,application,domain,infra,presentation}` の layered runtime structure を確認した。
  - `workflow next` / `workflow status` / `assurance classify` / `assurance compile` / `AssuranceContract` / `Runbook` に相当する command / domain model は現時点では見当たらない。
  - 現行 `spec-dock-issue-planning` skill は actor sequence と reviewer gates を skill 内に直接持つ。
  - 現行 `spec-dock-issue-execution` skill は one-step-at-a-time、delegation、reviewer gate、commit gate などの固定的な execution spine を持つ。

## Source-grounded に解決できたこと

- この Epic は `init-local-00003 Architecture Maintenance and Hardening` 配下が適切。
- 既存 `epic-00158` へ直接追加せず、新規 Epic として扱う判断は draft decision と親 Epic の境界から妥当。
- 変更対象は単なる docs cleanup ではなく、runtime command、generated state、skill kernel、review trigger / observation、PR repair semantics を横断する。
- `.agents/skills/**` を Issue 状態ごとに差し替える方式は採らず、固定 Skill kernel から runtime compiled Runbook を取得する方式が draft package の中心判断。
- Current implementation はまだ `workflow next` / `assurance` surface を持たないため、I01/I02 は新しい runtime contract の導入になる。
- Provider source / dogfooding mirror の扱いは既存 repo guideline と `epic-00158` の設計に従い、provider side を authority、dogfooding mirror を検証面として扱う。

## Draft package から formal docs へ採用できそうな核

- `Assurance Profile`: `lite / standard / strict / critical`
- `Complexity Tier`: `routine / normal / complex / deep`
- `Assurance Contract`: tracked machine-readable issue-local contract with source binding and obligations.
- `Runbook`: current state / phase / profile / step から runtime が生成する Markdown / JSON projection.
- `Fixed Skill kernel`: Skill は `workflow next` 呼び出しと stdout Runbook 遵守、blocked / human gate 停止だけを first-read に持つ。
- `Blocker-centric PR repair`: comment zero ではなく verified blocker zero を merge-prepared の終了条件にする。
- `Trusted review policy`: PR head ではなく PR base SHA の fixed path から policy を取得し、deterministic trigger body を runtime が合成する。

## まだ user intent が必要な高影響 gap

- 軽量タスクの過剰ゲート削減が主目的である一方、draft package は Standard default と Lite all-positive eligibility / manual-evidence-gated activation をかなり保守的に置いている。
- Formal requirement / design / plan では、Lite を初期 rollout でどこまで自動適用するかを明確にしないと、次が変わる。
  - Lite の acceptance criteria
  - classification hard trigger / unknown fact handling
  - artifact composition の最小 section
  - reviewer / re-review obligation
  - rollout plan and default switch gate
  - telemetry success metric

## 質問候補と分類

- Q: Epic title を scaffold の `Dynamic Workflow Resource Allocation` から draft 推奨の `Adaptive Assurance And Compiled Agent Workflow` へ変えるか。
  - 分類: low-impact naming / authoring polish。
  - local assumption: formal docs では draft package の用語に寄せ、metadata title 変更は後で別途判断可能。
- Q: `workflow next` の初期 scope を issue planning / execution に限定するか、PR delivery まで含めるか。
  - 分類: plan / slicing に影響。
  - local answer: draft plan I01-I07 では PR delivery policy まで含むが、I05/I06 として後段分割されているため、すぐ user に聞かず plan で tranche 化できる。
- Q: Lite profile をいつ自動適用するか。
  - 分類: requirement / design / plan / rollout / acceptance criteria に影響する user-intent blocker。
  - 推奨: これを最初の formal interview question にする。

## 次アクション

- `20260623t011352z-interview-lite-profile-rollout-clarification.md` に unanswered question と選択肢を保存し、ユーザーへ一問だけ確認する。
- 回答後、同じ interview artifact に user answer、adoption target、canonical docs への反映方針を追記する。
