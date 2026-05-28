---
種別: scratch
ID: "scratch-20260528t012300z"
タイトル: "ChatGPT follow-up prompt for requirement grill discussion templates"
状態: "draft"
作成者: "Codex"
最終更新: "2026-05-28"
親: ["iss-00134"]
関連: ["research-20260528t011700z"]
authority: "raw"
derived_from:
  - "discussions/20260528t011700z-research-spec-dock-requirement-grill-skill-design.md"
  - "discussions/20260528t011400z-scratch-chatgpt-skill-design-response.md"
reflected_to: []
---

# scratch-20260528t012300z ChatGPT follow-up prompt for requirement grill discussion templates

## メモ

前回の `spec-dock-requirement-grill` skill design を前提に、次は Slice 2 の discussion templates を実際に設計してください。

# 前提
- `spec-dock-requirement-grill` の first implementation slice は provider-side shared skill asset だけにする方針。
- その次の slice として、requirement grill workflow が使う issue-local discussion templates を設計したい。
- spec-dock の現行 discussion templates は flat に置かれている:
  - `spec-dock/templates/discussions/research.md`
  - `spec-dock/templates/discussions/disc.md`
  - `spec-dock/templates/discussions/interview.md`
  - `spec-dock/templates/discussions/scratch.md`
  - `spec-dock/templates/discussions/adr.md`
- provider-side shipped scaffold の authority は `src/spec_dock/assets/spec_dock/templates/discussions/` 側です。前回提案にあった `src/spec_dock/assets/install_root/spec-dock/templates/...` は active epic の agent-tooling install_root と scaffold templates の境界を混同している可能性があります。
- この点を踏まえ、templates を追加すべきか、既存 flat template を拡張すべきか、あるいは `spec-dock-requirement-grill` の skill 内 guidance に留めるべきかも評価してください。

# 設計対象
1. `source-grounding` template:
   - local source inspection の facts / inferences / unverified / implications を分ける。
2. `grill-session` template:
   - one-question-at-a-time interview を記録する。
   - 各質問に why it matters / source-grounded context / affected artifacts / answer / resolution status を持たせる。
3. `decision-tree` template:
   - options / tradeoffs / recommendation / open questions / adoption target を分ける。
4. `adr-triage` template:
   - final ADR ではなく candidate 判定に限定する。
   - hard-to-reverse / surprising / real tradeoff / long-term impact / cross-issue consequence を評価する。

# 出力してほしいこと
- まず template placement 方針:
  - Option A: 新規 specialized templates を provider scaffold に追加
  - Option B: 既存 `research.md` / `interview.md` / `disc.md` を拡張
  - Option C: template は増やさず skill 内 guidance として持つ
  - 推奨案と理由
- もし新規 template を追加するなら、provider-side path と installed path を正しく提案してください。
- 各 template の full Markdown draft を出してください。
- requirement/design/plan に直接反映してよい情報と、discussion に留めるべき情報の境界を明記してください。
- この template slice を first skill slice と同じ issue に含めるべきか、follow-up issue に分けるべきかも判断してください。

# 制約
- Matt Pocock skills の原文コピーは避け、spec-dock の用語で書いてください。
- discussion artifact は source of truth ではない。adoption / reflection を経て canonical docs に反映される。
- 現行 spec-dock は flat template layout なので、安易に nested template path を増やす場合は理由が必要。
- docs-only / template-only change として review / validation しやすい設計にしてください。

# 望ましい出力形式
- Placement decision
- Template contract summary
- Full template drafts
- Canonical reflection rules
- Implementation slice recommendation
- Risks / unresolved questions
- Next follow-up prompt
