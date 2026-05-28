---
種別: research
ID: "research-20260528t013700z"
タイトル: "requirement grill discussion template design from ChatGPT follow-up"
状態: "completed"
作成者: "Codex"
最終更新: "2026-05-28"
親: ["iss-00134"]
関連: ["research-20260528t011700z", "scratch-20260528t013400z"]
authority: "synthesized"
derived_from:
  - "discussions/20260528t012300z-scratch-chatgpt-template-design-followup-prompt.md"
  - "discussions/20260528t013400z-scratch-chatgpt-template-design-response.md"
reflected_to:
  - "requirement.md"
---

# research-20260528t013700z requirement grill discussion template design from ChatGPT follow-up

## 調査目的
- `spec-dock-requirement-grill` が使う discussion templates の placement、template contract、canonical reflection rules、implementation slice boundary を具体化する。

## 調査方法
- 前回と同じ ChatGPT thread に follow-up prompt を送り、discussion template 設計を依頼した。
- ChatGPT thread:
  - `https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a1790e9-2be8-83a4-aa7c-3350ef063f6f`
- Prompt では、agent-tooling `install_root` と scaffold template authority の境界を明示し、`src/spec_dock/assets/spec_dock/templates/discussions/` を provider-side authority として検討させた。

## 調査結果
- ChatGPT の placement recommendation:
  - Option A: new specialized templates を provider scaffold に追加する。
  - ただし nested path は増やさず、現行 flat layout を維持する。
- 推奨 provider-side paths:
  - `src/spec_dock/assets/spec_dock/templates/discussions/research-source-grounding.md`
  - `src/spec_dock/assets/spec_dock/templates/discussions/interview-grill-session.md`
  - `src/spec_dock/assets/spec_dock/templates/discussions/disc-decision-tree.md`
  - `src/spec_dock/assets/spec_dock/templates/discussions/disc-adr-triage.md`
- 推奨 installed scaffold paths:
  - `spec-dock/templates/discussions/research-source-grounding.md`
  - `spec-dock/templates/discussions/interview-grill-session.md`
  - `spec-dock/templates/discussions/disc-decision-tree.md`
  - `spec-dock/templates/discussions/disc-adr-triage.md`
- Option assessment:
  - Existing generic templates を拡張する案は、generic template が重くなるため非推奨。
  - Skill 内 guidance のみに留める案は初期回避策としては可だが、artifact shape が揺れやすいため本採用では非推奨。
- Template contracts:
  - `research-source-grounding.md`: local source inspection の facts / inferences / unverified / implications / source-resolved questions / remaining human questions を分ける。
  - `interview-grill-session.md`: one-question-at-a-time interview を記録し、各 question に why it matters、source-grounded context、affected artifacts、answer、resolution status を持たせる。
  - `disc-decision-tree.md`: options、tradeoffs、recommendation、open questions、adoption target、proposed canonical wording を分ける。
  - `disc-adr-triage.md`: final ADR ではなく ADR candidate triage に限定し、hard-to-reverse / surprising / real tradeoff / long-term impact / cross-issue consequence などを評価する。
- Implementation slice recommendation:
  - Template addition は same issue に含めてよいが、first skill slice とは分けて Slice 2 とする。
  - Slice 2 は scaffold template authority 側の docs-only / template-only asset addition とする。
  - CLI/template discovery integration は、必要が分かった場合だけ別 slice または follow-up issue に切り出す。

## 推測 / 未検証事項
- 推測:
  - `src/spec_dock/assets/spec_dock/templates/discussions/*` が installed `spec-dock/templates/discussions/*` にそのまま同期される。
  - Flat template 追加だけなら `validate` で最低限の structural check は通せる可能性が高い。
- 未検証:
  - spec-dock runtime の `new doc` / template discovery が arbitrary template filename を扱えるか。
  - Existing generic templates の文体・section convention に完全に合っているか。
  - Discussion artifact instance の date/file naming convention。
  - Sync が scaffold template asset changes の dogfooding mirror に必要か。

## 判断への含意
- `design.md` では `spec-dock-requirement-grill` skill asset と discussion template additions を別 slice として扱うのがよい。
- Slice 1:
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-requirement-grill/SKILL.md`
- Slice 2:
  - `src/spec_dock/assets/spec_dock/templates/discussions/research-source-grounding.md`
  - `src/spec_dock/assets/spec_dock/templates/discussions/interview-grill-session.md`
  - `src/spec_dock/assets/spec_dock/templates/discussions/disc-decision-tree.md`
  - `src/spec_dock/assets/spec_dock/templates/discussions/disc-adr-triage.md`
- `install_root/spec-dock/templates/...` は今回の template authority として使わない。

## リスク/制約
- New flat templates が runtime command から直接使えない可能性がある。初期 slice は asset addition として扱い、CLI integration は別途確認する。
- Specialized templates が generic templates と重複する。generic は汎用、specialized は requirement grill workflow 用と明記する。
- `disc-adr-triage.md` が final ADR と誤読される恐れがある。本文と filename で discussion-level triage であることを明示する。
- Discussion recommendations が shadow source-of-truth 化しないよう、全 template に canonical status / reflection target を持たせる。

## 反映先
- reflected_to:
  - 未反映。`requirement.md` / `design.md` / `plan.md` の slice definition に反映候補。

## 参考（References）
- `discussions/20260528t012300z-scratch-chatgpt-template-design-followup-prompt.md`
- `discussions/20260528t013400z-scratch-chatgpt-template-design-response.md`
