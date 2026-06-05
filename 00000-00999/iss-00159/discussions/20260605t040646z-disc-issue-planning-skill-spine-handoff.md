---
種別: disc
ID: "20260605t040646z-disc"
タイトル: "Issue Planning Skill Spine Handoff"
状態: "draft | proposed | archived"
作成者: "iwasawayuuta"
最終更新: "2026-06-05"
親: ["iss-00159"]
関連: []
authority: "proposed"
derived_from:
  - "spec-dock/active/epic/discussions/20260605t040338z-disc-skill-docs-workflow-spine-synthesis.md"
  - "spec-dock/active/epic/discussions/20260605t035200z-research-chatgpt-skill-docs-information-architecture-report.md"
  - "spec-dock/active/epic/discussions/20260605t040000z-research-chatgpt-skill-rewrite-targets-report.md"
  - "spec-dock/active/epic/discussions/20260605t035201z-research-chatgpt-empirical-skill-compliance-tests-report.md"
reflected_to: []
---

# 20260605t040646z-disc Issue Planning Skill Spine Handoff

## 位置づけ
- この doc は、`epic-00158` の ChatGPT `じっくり思考 Pro` 調査結果を `iss-00159` の最初の authoring 入力へ渡すための proposal / synthesis である。
- この doc 自体は canonical requirement / design / plan ではない。
- 後続の issue planning では、この handoff と epic synthesis を根拠に `requirement.md` を作成し、fresh `spec-reviewer` pass まで進める。

## 対象論点 (必須)
- 今回整理する論点:
  - `spec-dock-issue-planning` skill に、agent が読み飛ばしてはいけない authoring workflow spine を明示する。
- この synthesis が必要な理由:
  - 現状の skill は主に docs への導線であり、モデルが linked docs を読まない場合、要件定義 -> review -> 設計 -> review -> 計画 -> review -> 実行 handoff の順序や stop conditions を十分に認識できない可能性がある。

## derived question sheets / research (必須)
- `interview`:
  - なし。
- `research`:
  - `spec-dock/active/epic/discussions/20260605t035200z-research-chatgpt-skill-docs-information-architecture-report.md`
  - `spec-dock/active/epic/discussions/20260605t040000z-research-chatgpt-skill-rewrite-targets-report.md`
  - `spec-dock/active/epic/discussions/20260605t035201z-research-chatgpt-empirical-skill-compliance-tests-report.md`
- その他の根拠:
  - `spec-dock/active/epic/discussions/20260605t040338z-disc-skill-docs-workflow-spine-synthesis.md`

## synthesis (必須)
- 合意済みのこと:
  - docs は詳細 authority として維持する。
  - skill には、agent が最初に守るべき最小の operational workflow を置く。
  - 最初の改修対象は `spec-dock-issue-planning` が適切である。
- 未合意 / 未確定のこと:
  - 実際の文言と section 順序は issue authoring 中に詰める。
  - `.agents/skills/` root mirror と `src/spec_dock/assets/install_root/.agents/skills/` の同期方針は実装前に確認する。
- source-grounded に解決できたこと:
  - `spec-dock-issue-planning` は重要な docs への link と reviewer gate の短い reminder を持つが、step-by-step の runbook にはなっていない。
  - `workflow_spec_authoring.md` と `workflow_issue.md` には詳細 workflow があるため、skill は schema を複製せず、必須手順と stop conditions だけを明示すればよい。

## 選択肢 / tradeoff (必須)
- Option A: skill に最小 workflow spine を追加する。
  - Pros:
    - agent が linked docs を開く前に、phase order / stop conditions / evidence obligations を把握できる。
    - 小さい差分で PDCA を開始できる。
  - Cons:
    - docs と skill の二重記述が少し増えるため、詳細 schema は複製しない境界が必要。
- Option B: runtime gate から先に実装する。
  - Pros:
    - 一部の違反を fail-closed に検出できる。
  - Cons:
    - agent が正しい順序を理解する前の行動改善には直結しにくい。
    - 今回のユーザー仮説と比べて初手としては重い。

## reflection proposal (必須)
- canonical docs / workflow / template / skill guidance へ反映すべき候補:
  - `spec-dock-issue-planning` skill に以下の section を追加する:
    - `Source-of-truth boundary`
    - `Must read before acting`
    - `Must-follow issue planning checklist`
    - `Artifact gates`
    - `Stop and return conditions`
    - `Evidence to record in report.md`
    - `Exit / handoff criteria`
- まだ proposal に留める理由:
  - issue requirement / design / plan と reviewer pass がまだないため。

## ADR candidate triage (必須)
- ADR candidate か:
  - no
- hard to reverse:
  - no
- surprising without context:
  - no
- real tradeoff:
  - yes
- ADR 化しない場合の反映先:
  - `requirement.md`, `design.md`, `plan.md`

## 推奨案 (必須)
- `iss-00159` では、まず `spec-dock-issue-planning` skill だけを operationally sufficient にする。
- 具体的には、docs の詳細 policy を複製せず、agent が守るべき phase order、fresh reviewer gate、non-pass reviewer states、canonical ownership、unresolved gap handling、report evidence、execution handoff criteria を skill 本文に明示する。

## 推奨反映先 (必須)
- `requirement.md`:
  - skill に可視化する mandatory workflow と non-scope を固定する。
- `design.md`:
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md` と必要な mirror の更新方針を決める。
  - docs/source-of-truth boundary と duplication control を決める。
- `plan.md`:
  - doc-writer への bounded handoff、spec-reviewer の docs/spec alignment review、manual compliance smoke probe を step 化する。
- `ADR`:
  - 現時点では不要。
- `report.md` Evidence Adoption Ledger:
  - この handoff と epic synthesis の採用可否を記録する。

## 未採用 / deferred 理由 (必須)
- 未採用:
  - `gate status --json` を初手にする案は未採用。後続候補としては有用だが、今回の主因である skill readability / first-read workflow awareness への直接効果が弱い。
- deferred:
  - hub skill、issue-execution skill、epic/initiative planning skill、manual compliance harness は follow-up に defer する。

## 次アクション (必須)
- `requirement.md` / `design.md` / `plan.md` / `adr` へ反映する内容:
  - `iss-00159` の requirement authoring で、この handoff から scope / non-scope / acceptance criteria を作成する。
- 追加で作る discussion docs:
  - 必要なら manual compliance probe の詳細を別 `disc` または `research` として作る。
