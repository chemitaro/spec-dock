---
種別: research
ID: "research-20260528t004419z"
タイトル: "Matt Pocock skills source capture for iss-00134"
状態: "completed"
作成者: "Codex"
最終更新: "2026-05-28"
親: ["iss-00134"]
関連: ["https://github.com/mattpocock/skills", "https://github.com/mattpocock/skills/commit/0288510dd61ff6ef7c2003834082ab8f2387e80e"]
authority: "synthesized"
derived_from:
  - "discussions/mattpocock-skills-source/"
reflected_to: []
---

# research-20260528t004419z Matt Pocock skills source capture for iss-00134

## 調査目的
- `mattpocock/skills` を毎回 Web 参照せず、issue-local の安定した evidence base として扱えるようにする。
- ChatGPT 5.5 Pro への分析依頼で、上流 repo URL だけに依存せず、取り込み済み原文を参照できる状態を作る。

## 調査方法
- GitHub repo `mattpocock/skills` の HEAD tarball を取得した。
- HEAD commit は `0288510dd61ff6ef7c2003834082ab8f2387e80e`、commit date は `2026-05-27T12:36:22Z`。
- `README.md`、`LICENSE`、`CONTEXT.md`、各 `SKILL.md`、skill-local の関連 Markdown、`.claude-plugin/plugin.json` を `discussions/mattpocock-skills-source/` に元 tree に近い構造で取り込んだ。
- 実行 helper script は今回の capture から除外した。理由は、現時点の分析対象が skill 文書・設計思想・運用パターンであり、script behavior は採用設計の次段で必要性を判断するため。

## 調査結果
- 取り込み済みファイル数は 68、サイズは約 340KB。
- 主要な分析対象は次の通り。
  - `skills/productivity/grill-me/SKILL.md`: 計画・設計を一問ずつ詰める interview loop。
  - `skills/engineering/grill-with-docs/SKILL.md`: `grill-me` に domain glossary / ADR 更新を足した docs-aware interview loop。
  - `skills/engineering/to-prd/SKILL.md`: 既存 conversation/codebase context を PRD 化する synthesis skill。
  - `skills/engineering/to-issues/SKILL.md`: plan / PRD を vertical slice issue に分割する skill。
  - `skills/engineering/tdd/SKILL.md`: vertical tracer bullet と behavior-first testing を重視する TDD skill。
  - `skills/engineering/improve-codebase-architecture/SKILL.md`: domain language / ADR を踏まえ、deep module 化の候補を可視化する architecture review skill。
  - `skills/engineering/setup-matt-pocock-skills/SKILL.md`: issue tracker、triage labels、domain docs layout を repo-local に設定する setup skill。
- `README.md` 上の中心思想は、重い process ownership よりも小さく composable な skills を重視し、misalignment、曖昧な domain language、弱い feedback loop、codebase entropy を主要 failure mode として扱うこと。

## 推測 / 未検証事項
- 推測:
  - spec-dock への活用では、`grill-with-docs` をそのまま移植するより、spec-dock の `requirement.md` / `design.md` / `plan.md` / `discussions/` / ADR workflow に合わせた派生 skill または workflow phase として吸収する方が自然そうである。
  - `CONTEXT.md` の役割は、spec-dock では既存の active docs、domain glossary section、discussion research、ADR docs に分散している可能性があり、そのまま root `CONTEXT.md` を正本にするかは要検討。
- 未検証:
  - 上流 repo の script 類が setup や guardrail の採用判断に影響するか。
  - `grill-with-docs` の inline docs update を spec-dock の phase authority / lifecycle approval と矛盾なく扱う最小設計。
  - Matt Pocock skills の license / attribution を spec-dock shipped assets に取り込む場合の配布要件。

## 判断への含意
- ChatGPT への次プロンプトでは、Web で上流 repo を毎回読む前提ではなく、`discussions/mattpocock-skills-source/` を primary evidence として指定する。
- 初回の設計分析では、少なくとも次を比較軸にする。
  - `grill-me` 的な一問ずつの要件壁打ちを、spec-dock の `interview` discussion artifact として扱う案。
  - `grill-with-docs` 的な glossary / ADR 更新を、spec-dock の active docs / ADR / discussion reflection workflow に統合する案。
  - `to-prd` / `to-issues` 的な synthesis / slicing を、Issue requirement/design/plan authoring や follow-up issue generation として扱う案。
  - `tdd` の tracer bullet / behavior-first testing を、plan の Spec-Locked Closure Index と step closure contract に反映する案。

## リスク/制約
- 原文 capture は evidence であり、spec-dock に採用済みの要件・設計ではない。
- 上流 repo は今後更新されるため、この capture は commit `0288510dd61ff6ef7c2003834082ab8f2387e80e` 時点の snapshot として扱う。
- 原文を shipped asset として配布する場合は、license / attribution / scope を別途検討する。

## 反映先
- reflected_to:
  - 未反映。次の ChatGPT 分析と議論整理を経て `requirement.md` / `design.md` / `plan.md` へ反映する。

## 参考（References）
- `discussions/mattpocock-skills-source/source-metadata.md`
- `discussions/mattpocock-skills-source/README.md`
- `discussions/mattpocock-skills-source/skills/productivity/grill-me/SKILL.md`
- `discussions/mattpocock-skills-source/skills/engineering/grill-with-docs/SKILL.md`
- `discussions/mattpocock-skills-source/skills/engineering/to-prd/SKILL.md`
- `discussions/mattpocock-skills-source/skills/engineering/to-issues/SKILL.md`
- `discussions/mattpocock-skills-source/skills/engineering/tdd/SKILL.md`
- `discussions/mattpocock-skills-source/skills/engineering/improve-codebase-architecture/SKILL.md`
